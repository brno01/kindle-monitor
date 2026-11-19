"""Coletores de metricas do kindle-monitor.

Somente leitura, somente biblioteca padrao. As funcoes `parse_*` sao puras (recebem
texto bruto); as `coletar_*` recebem callables injetaveis (executar, buscar, statvfs)
para os testes nao dependerem de nvidia-smi, systemctl, rede nem /var/lib/cerberus.

Convencao de falha: cada coletor falha isolado. Na classe `Coletor`, qualquer excecao
vira `{"erro": "n/d"}` naquela metrica; coletor "ausente" (sem GPU, sem sensor) omite a chave.
"""
import errno
import glob
import ipaddress
import json
import math
import os
import re
import socket
import stat
import subprocess
import threading
import time
import urllib.request
from collections import deque, namedtuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlsplit

import alertas
import dev_fontes
import ecossistema
import servicos

Snapshot = namedtuple("Snapshot", "id t metricas")
ND = {"erro": "n/d"}
CACHE_S = 5.0
CACHE_CPU_PADRAO = 1.5
INTERVALO_COLETA_PADRAO = 1.0   # s entre snapshots da thread de coleta
INTERVALO_LENTO_PADRAO = 5.0    # s entre coletas caras (nvidia-smi, systemctl)
IDADE_AMOSTRA_MAX_S = 30.0  # older than this, a previous sample is useless: sample twice again
INTERVALO_MIN_S = 0.5  # closer requests reuse the last computed rate
INTERVALO_IO_PADRAO = 0.3
SETOR_B = 512
IDADE_PARADO_S = 120
LIMITE_RESPOSTA_PAR = 1_000_000
TIMEOUT_PAR_S = 2.0
BALANCEADOR_PADRAO = "/var/lib/cerberus/memory-balancer.json"
TIMEOUT_PORTA_S = 0.6
CONECTAR_PADRAO = socket.create_connection
HISTORICO_MAX = 60
INTERVALO_HISTORICO_PADRAO = 15
_ROTULO_PORTA = re.compile(r"^[A-Za-z0-9_.-]{1,12}$")
_NOME_HOST = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$")
_NOME_DEV = re.compile(r"^[A-Za-z0-9._-]{1,32}$")
_ROTULO_IO = re.compile(r"^[A-Za-z0-9 _.+/-]{1,16}$")
_NOME_UNIDADE = re.compile(r"^[A-Za-z0-9@:._\\-]+$")


# --------------------------------------------------------------------------- CPU

def parse_cpu_stat(texto):
    """Retorna (total, ocioso) da linha agregada `cpu ` de /proc/stat."""
    for linha in texto.splitlines():
        partes = linha.split()
        if partes and partes[0] == "cpu":
            try:
                valores = [int(x) for x in partes[1:9]]
            except ValueError as e:
                raise ValueError("linha cpu invalida") from e
            if len(valores) < 5:
                raise ValueError("linha cpu curta")
            return sum(valores), valores[3] + valores[4]
    raise ValueError("sem linha cpu em /proc/stat")


def calcular_cpu(antes, depois):
    """Percentual de uso entre duas leituras (total, ocioso). Contadores iguais -> 0.0."""
    dt = depois[0] - antes[0]
    di = depois[1] - antes[1]
    if dt <= 0:
        return 0.0
    return round(min(100.0, max(0.0, (dt - di) * 100.0 / dt)), 1)


class CpuAmostrador:
    """CPU % pela diferenca entre a leitura atual e a anterior de /proc/stat.

    So a primeira leitura (ou uma anterior com mais de 30 s) dorme `intervalo_s` entre duas
    leituras; depois cada chamada faz uma leitura e compara com a anterior. Resultado em cache
    por `cache_s`; chamadas a menos de 0,5 s da amostra anterior reutilizam o ultimo valor.
    """

    def __init__(self, leitor, dormir=time.sleep, relogio=time.monotonic, intervalo_s=0.5, cache_s=CACHE_CPU_PADRAO):
        self._leitor = leitor
        self._dormir = dormir
        self._relogio = relogio
        self._intervalo = intervalo_s
        self._cache_s = cache_s
        self._lock = threading.Lock()
        self._t = None  # when the cached value was computed
        self._valor = None
        self._prev = None  # (total, ocioso)
        self._prev_t = None

    def medir(self, forcar=False):
        """`forcar=True` ignora o cache de `cache_s` (a thread de coleta ja controla a cadencia)."""
        with self._lock:
            agora = self._relogio()
            if not forcar and self._t is not None and agora - self._t < self._cache_s:
                return self._valor
            if self._prev is None or agora - self._prev_t > IDADE_AMOSTRA_MAX_S:
                a = parse_cpu_stat(self._leitor())
                self._dormir(self._intervalo)
                b = parse_cpu_stat(self._leitor())
                self._prev, self._prev_t = b, self._relogio()
                self._valor = calcular_cpu(a, b)
            else:
                if agora - self._prev_t < INTERVALO_MIN_S and self._valor is not None:
                    return self._valor
                b = parse_cpu_stat(self._leitor())
                self._valor = calcular_cpu(self._prev, b)
                self._prev, self._prev_t = b, agora
            self._t = self._relogio()
            return self._valor


# --------------------------------------------------------------------------- I/O

def parse_diskstats(texto):
    """{dispositivo: (bytes_lidos, bytes_escritos)} de /proc/diskstats (setores = coluna 6 e 10, de 512 B)."""
    r = {}
    for linha in texto.splitlines():
        p = linha.split()
        if len(p) < 10:
            continue
        try:
            r[p[2]] = (int(p[5]) * SETOR_B, int(p[9]) * SETOR_B)
        except ValueError:
            continue
    return r


def parse_net_dev(texto):
    """{interface: (rx_bytes, tx_bytes)} de /proc/net/dev (as duas primeiras linhas sao cabecalho)."""
    r = {}
    for linha in texto.splitlines()[2:]:
        nome, sep, resto = linha.partition(":")
        campos = resto.split()
        if not sep or len(campos) < 9:
            continue
        try:
            r[nome.strip()] = (int(campos[0]), int(campos[8]))
        except ValueError:
            continue
    return r


def validar_io(io):
    """Valida {"discos": [{rotulo, dev}], "redes": [{rotulo, if}]}; devolve a forma normalizada."""
    if not isinstance(io, dict):
        raise ValueError("io: deve ser um objeto {discos, redes}")
    saida = {"discos": [], "redes": []}
    for chave, campo in (("discos", "dev"), ("redes", "if")):
        itens = io.get(chave, [])
        if not isinstance(itens, list):
            raise ValueError("io: %s deve ser lista de {rotulo, %s}" % (chave, campo))
        for item in itens:
            if not isinstance(item, dict):
                raise ValueError("io: cada item de %s deve ser {rotulo, %s}" % (chave, campo))
            rotulo, nome = item.get("rotulo"), item.get(campo)
            if not isinstance(rotulo, str) or not _ROTULO_IO.match(rotulo):
                raise ValueError("io: rotulo invalido (1 a 16 caracteres ASCII simples)")
            if not isinstance(nome, str) or not _NOME_DEV.match(nome):
                raise ValueError("io: %s invalido (so letras, digitos, '.', '_' e '-', ate 32)" % campo)
            saida[chave].append({"rotulo": rotulo, campo: nome})
    return saida


def _taxa(antes, depois, dt):
    """Bytes/s entre dois contadores; None se nao ha como calcular (contador voltou, sem dt, sem dado)."""
    if antes is None or depois is None or dt <= 0 or depois < antes:
        return None
    return round((depois - antes) / dt, 1)


class IoAmostrador:
    """Taxas de I/O de disco e rede pela diferenca entre duas amostras de /proc/diskstats e /proc/net/dev.

    Primeira chamada (ou amostra anterior com mais de 30 s): duas leituras com `intervalo_s` entre elas.
    Depois: uma leitura por chamada, comparada com a anterior. Menos de 0,5 s desde a ultima amostra:
    devolve a ultima taxa sem ler nada (a amostra de referencia nao muda, o proximo intervalo fica maior).
    """

    def __init__(self, leitor, io, dormir=time.sleep, relogio=time.monotonic, intervalo_s=INTERVALO_IO_PADRAO):
        self._leitor = leitor
        self._discos = list((io or {}).get("discos") or [])
        self._redes = list((io or {}).get("redes") or [])
        self._dormir = dormir
        self._relogio = relogio
        self._intervalo = intervalo_s
        self._lock = threading.Lock()
        self._prev = None
        self._ultimo = None

    def _ler(self, caminho, parse, itens):
        if not itens:
            return {}
        try:
            return parse(self._leitor(caminho))
        except Exception:
            return None  # unreadable file: every entry becomes n/d

    def _amostra(self):
        return (self._relogio(),
                self._ler("/proc/diskstats", parse_diskstats, self._discos),
                self._ler("/proc/net/dev", parse_net_dev, self._redes))

    def _calcular(self, prev, cur):
        dt = cur[0] - prev[0]
        r = {"discos": [], "redes": []}
        for chave, campo, idx, nomes in (("discos", "dev", 1, ("leitura_bps", "escrita_bps")),
                                         ("redes", "if", 2, ("rx_bps", "tx_bps"))):
            itens = self._discos if chave == "discos" else self._redes
            antes, depois = prev[idx], cur[idx]
            for item in itens:
                nome = item[campo]
                if depois is not None and nome not in depois:
                    continue  # absent device/interface: row omitted
                a = (antes or {}).get(nome)
                d = (depois or {}).get(nome)
                linha = dict(item)
                for k, nome_taxa in enumerate(nomes):
                    linha[nome_taxa] = _taxa(a[k] if a else None, d[k] if d else None, dt)
                r[chave].append(linha)
        return r

    def medir(self):
        with self._lock:
            if not (self._discos or self._redes):
                return {"discos": [], "redes": []}
            agora = self._relogio()
            if self._prev is None or agora - self._prev[0] > IDADE_AMOSTRA_MAX_S:
                self._prev = self._amostra()
                self._dormir(self._intervalo)
            elif agora - self._prev[0] < INTERVALO_MIN_S and self._ultimo is not None:
                return self._ultimo
            cur = self._amostra()
            self._ultimo = self._calcular(self._prev, cur)
            self._prev = cur
            return self._ultimo


# ------------------------------------------------------------------------- /proc

def parse_loadavg(texto):
    p = texto.split()
    if len(p) < 3:
        raise ValueError("loadavg invalido")
    return {"1m": float(p[0]), "5m": float(p[1]), "15m": float(p[2])}


def _kb(texto, chave):
    m = re.search(r"^%s:\s+(\d+)\s*kB" % re.escape(chave), texto, re.MULTILINE)
    if not m:
        raise ValueError("meminfo sem " + chave)
    return int(m.group(1))


def _uso(total, usado):
    pct = round(usado * 100.0 / total, 1) if total > 0 else 0.0
    return {"total_kb": total, "usado_kb": usado, "pct": pct}


def parse_meminfo(texto):
    total = _kb(texto, "MemTotal")
    disponivel = _kb(texto, "MemAvailable")
    stotal = _kb(texto, "SwapTotal")
    slivre = _kb(texto, "SwapFree")
    return {"ram": _uso(total, total - disponivel), "swap": _uso(stotal, stotal - slivre)}


def parse_uptime(texto):
    p = texto.split()
    if not p:
        raise ValueError("uptime vazio")
    return {"segundos": int(float(p[0]))}


# ------------------------------------------------------------------ temperatura

_PREFERIDOS = ("x86_pkg_temp", "coretemp", "k10temp", "zenpower", "cpu_thermal", "cpu-thermal", "cpu")


def _ler_txt(caminho):
    try:
        with open(caminho, "r", encoding="ascii", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return None


def _miligraus(texto):
    try:
        v = int(texto) / 1000.0
    except (TypeError, ValueError):
        return None
    return v if 0 < v < 150 else None


def coletar_temperatura(raiz_sys="/sys"):
    """Temperatura da CPU em /sys (thermal_zone ou hwmon). None se nao houver sensor."""
    preferidos, outros = [], []
    for zona in sorted(glob.glob(os.path.join(raiz_sys, "class/thermal/thermal_zone*"))):
        tipo = (_ler_txt(os.path.join(zona, "type")) or "").lower()
        v = _miligraus(_ler_txt(os.path.join(zona, "temp")))
        if v is not None:
            (preferidos if tipo in _PREFERIDOS else outros).append(v)
    for hw in sorted(glob.glob(os.path.join(raiz_sys, "class/hwmon/hwmon*"))):
        nome = (_ler_txt(os.path.join(hw, "name")) or "").lower()
        v = _miligraus(_ler_txt(os.path.join(hw, "temp1_input")))
        if v is not None and nome in _PREFERIDOS:
            preferidos.append(v)
    escolhida = (preferidos or outros or [None])[0]
    return None if escolhida is None else {"c": round(escolhida, 1)}


# -------------------------------------------------------------------------- GPU

_CMD_GPU = [
    "nvidia-smi",
    "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
    "--format=csv,noheader,nounits",
]


def _int_ou_none(s):
    try:
        return int(float(s.strip()))
    except ValueError:
        return None  # "[N/A]", "[Not Supported]"


def coletar_gpu(executar):
    """None se nvidia-smi nao existe ou falha (driver ausente). ValueError se a saida for lixo."""
    try:
        rc, saida = executar(list(_CMD_GPU))
    except FileNotFoundError:
        return None
    if rc != 0:
        return None
    linhas = [l for l in saida.splitlines() if l.strip()]
    if not linhas:
        raise ValueError("nvidia-smi sem saida")
    campos = linhas[0].split(",")
    if len(campos) != 4:
        raise ValueError("nvidia-smi saida inesperada")
    util, usada, total, temp = (_int_ou_none(x) for x in campos)
    g = {"util_pct": util, "mem_usada_mb": usada, "mem_total_mb": total, "temp_c": temp}
    g["estado"] = "desativada" if gpu_desativada(g) else "ativa"
    return g


def gpu_desativada(gpu):
    """GPU sem nada carregado: util 0 % e memoria usada 0 MiB (ou ausente). Sem util conhecida = ativa."""
    if not isinstance(gpu, dict) or "erro" in gpu:
        return False
    util, mem = gpu.get("util_pct"), gpu.get("mem_usada_mb")
    if isinstance(util, bool) or not isinstance(util, (int, float)) or util != 0:
        return False
    if mem is None:
        return True
    return not isinstance(mem, bool) and isinstance(mem, (int, float)) and mem == 0


# ------------------------------------------------------------------------ disco

def coletar_disco(rotulo, caminho, statvfs=os.statvfs):
    s = statvfs(caminho)
    total = s.f_blocks * s.f_frsize
    usado = (s.f_blocks - s.f_bfree) * s.f_frsize
    util = usado + s.f_bavail * s.f_frsize  # mesma conta do df
    pct = round(usado * 100.0 / util, 1) if util > 0 else 0.0
    return {"rotulo": rotulo, "caminho": caminho, "total_b": total, "usado_b": usado, "pct": pct}


GIB = 2 ** 30
IDADE_TIER_MAX_S = 3 * 3600


def _num_nao_neg(v):
    return _num_finito(v) and v >= 0


def coletar_tier_state(rotulo, caminho, ler, agora):
    """Linha de disco a partir do tier-state.json do Cerberus (ssd_used_gib / cap_gib, em GiB).

    Arquivo ausente ou sem numeros validos -> {"erro": "n/d"}. `when` ausente, invalido ou com
    mais de 3 h -> mesmos numeros com "parado": True.
    """
    nd = {"rotulo": rotulo, "erro": "n/d"}
    try:
        dados = json.loads(ler(caminho))
    except Exception:
        return nd
    if not isinstance(dados, dict):
        return nd
    usado, cap = dados.get("ssd_used_gib"), dados.get("cap_gib")
    if not _num_nao_neg(usado) or not _num_nao_neg(cap) or cap <= 0:
        return nd
    idade = None
    try:
        idade = agora - datetime.strptime(dados["when"], "%Y-%m-%d %H:%M:%S").timestamp()
    except Exception:
        pass
    parado = idade is None or idade > IDADE_TIER_MAX_S
    r = {"rotulo": rotulo, "caminho": caminho, "total_b": int(round(cap * GIB)),
         "usado_b": int(round(usado * GIB)), "pct": round(min(usado, cap) * 100.0 / cap, 1),
         "base": 1024, "parado": parado}
    if idade is not None:
        r["idade_s"] = max(0, int(idade))
    return r


# ------------------------------------------------------------- claude e s10

IDADE_LIMITES_MAX_S = 900
IDADE_TOKENS_MAX_S = 1200
IDADE_S10_MAX_S = 120
_CAMPOS_INT_TOKENS = ("entrada", "saida", "cache_leitura", "cache_escrita", "total")


INTEIRO_MAX = 2 ** 53  # acima disso o JSON e malformado para nos (e float()/isfinite() estouram)


def _int_nao_neg(v):
    return isinstance(v, int) and not isinstance(v, bool) and 0 <= v < INTEIRO_MAX


def _json_dict(ler, caminho):
    dados = json.loads(ler(caminho))
    if not isinstance(dados, dict):
        raise ValueError("nao e objeto")
    return dados


def _janela_limite(j, agora):
    """{"pct", "volta_em"} -> J. Ausente -> None; tipos errados -> ValueError. pct e limitado a 0-100."""
    if j is None:
        return None
    if not isinstance(j, dict) or not _num_finito(j.get("pct")) or not _int_nao_neg(j.get("volta_em")):
        raise ValueError("janela invalida")
    volta_em = j["volta_em"]
    if volta_em <= agora:
        return {"pct": 0.0, "volta_em": volta_em, "renovado": True}
    return {"pct": float(min(100.0, max(0.0, j["pct"]))), "volta_em": volta_em, "renovado": False}


def _num_finito(v):
    if isinstance(v, int) and not isinstance(v, bool):
        return -INTEIRO_MAX < v < INTEIRO_MAX
    return isinstance(v, float) and math.isfinite(v)


def _totais_tokens(t):
    if not isinstance(t, dict) or not _num_nao_neg(t.get("custo_usd")):
        raise ValueError("totais invalidos")
    r = {}
    for k in _CAMPOS_INT_TOKENS:
        if not _int_nao_neg(t.get(k)):
            raise ValueError("totais invalidos")
        r[k] = t[k]
    r["custo_usd"] = float(t["custo_usd"])
    return r


def _idade(ts, agora):
    if not _int_nao_neg(ts):
        raise ValueError("timestamp invalido")
    return max(0, int(agora - ts))


def _limites_claude(caminho, ler, agora):
    dados = _json_dict(ler, caminho)
    idade = _idade(dados.get("atualizado_em"), agora)
    cinco = _janela_limite(dados.get("cinco_horas"), agora)
    semanal = _janela_limite(dados.get("semanal"), agora)
    if cinco is None and semanal is None:
        raise ValueError("sem janelas")
    return {"cinco_horas": cinco, "semanal": semanal, "idade_s": idade,
            "velho": idade > IDADE_LIMITES_MAX_S}


def _tokens_claude(caminho, ler, agora):
    dados = _json_dict(ler, caminho)
    idade = _idade(dados.get("gerado_em"), agora)
    return {"hoje": _totais_tokens(dados.get("hoje")), "sete_dias": _totais_tokens(dados.get("sete_dias")),
            "idade_s": idade, "velho": idade > IDADE_TOKENS_MAX_S}


def coletar_claude(cfg, ler, agora):
    """Limites (limites.json) e tokens (tokens.json) do claude-uso. Cada parte falha sozinha: {"erro": "n/d"}."""
    r = {}
    for chave, fn in (("limites", _limites_claude), ("tokens", _tokens_claude)):
        try:
            r[chave] = fn(cfg[chave], ler, agora)
        except Exception:
            r[chave] = dict(ND)
    return r


PREFIXOS_DEV = ("/var/lib/", "/run/")


def _caminho_dev(v):
    """Caminho de fonte do painel Dev: absoluto, normalizado, sob /var/lib/ ou /run/. Senao ValueError."""
    if not isinstance(v, str) or "\0" in v or os.path.normpath(v) != v or not v.startswith(PREFIXOS_DEV):
        raise ValueError("caminho invalido")
    return v


def coletar_s10(caminho, ler, agora):
    """Resumo publico do S10 (resumo.json). Ausente, invalido ou com tipos errados -> {"erro": "n/d"}."""
    try:
        dados = _json_dict(ler, caminho)
        idade = _idade(dados.get("gerado_em"), agora)
        bateria, caminhos, avisos = dados.get("bateria"), dados.get("caminhos"), dados.get("avisos")
        if bateria is not None and not isinstance(bateria, dict):
            return dict(ND)
        if not isinstance(caminhos, dict) or not isinstance(avisos, list):
            return dict(ND)
        return {"bateria": bateria, "caminhos": caminhos,
                "avisos": [a for a in avisos if isinstance(a, str)],
                "idade_s": idade, "velho": idade > IDADE_S10_MAX_S}
    except Exception:
        return dict(ND)


# --------------------------------------------------------------------- servicos

def coletar_servicos(nomes, executar):
    """`systemctl is-active NOME` por unidade. Inativa -> ativo False; sem systemctl -> n/d."""
    resultado = []
    for nome in nomes:
        nome = str(nome)
        if not _NOME_UNIDADE.match(nome) or nome.startswith("-"):
            resultado.append({"nome": nome, "erro": "n/d"})
            continue
        try:
            _rc, saida = executar(["systemctl", "is-active", nome])
            resultado.append({"nome": nome, "ativo": saida.strip() == "active"})
        except Exception:
            resultado.append({"nome": nome, "erro": "n/d"})
    return resultado


# ------------------------------------------------------------ servicos do Kindle

INVENTARIO_ARQ = "servicos.json"
INVENTARIO_VALIDADE_S = 60
INVENTARIO_ESTADO_PADRAO = "/run/kindle-monitor/status"


def _detalhe_curto(v):
    return re.sub(r"[^A-Za-z0-9 _.,:/()=+-]", "?", v)[:24] if isinstance(v, str) else ""


def montar_servicos_kindle(catalogo, texto, agora):
    """Junta o catalogo com o inventario (JSON do executor root).

    `texto` None = arquivo ausente. Mais de 60 s (ou do futuro), JSON ruim ou ausente: todos "desconhecido" e
    `inventario` diz porque ("velho"/"ausente"). Nunca levanta.
    """
    inv, situacao, idade = {}, "ausente", None
    if texto is not None:
        try:
            d = json.loads(texto)
            gerado, dados = d["gerado"], d["servicos"]
            if isinstance(gerado, bool) or not isinstance(gerado, (int, float)) or not isinstance(dados, dict):
                raise ValueError("formato")
            idade = agora - gerado
            if -5 <= idade <= INVENTARIO_VALIDADE_S:
                inv, situacao = dados, "ok"
                idade = max(0, int(idade))
            else:
                situacao, idade = "velho", max(0, int(idade))
        except (ValueError, KeyError, TypeError):
            situacao, idade = "ausente", None
    itens = []
    for c in catalogo:
        e = inv.get(c["id"]) if situacao == "ok" and isinstance(inv.get(c["id"]), dict) else {}
        estado = e.get("estado") if e.get("estado") in servicos.ESTADOS else "desconhecido"
        itens.append({"id": c["id"], "rotulo": c["rotulo"], "grupo": c["grupo"], "estado": estado,
                      "detalhe": _detalhe_curto(e.get("detalhe")) if e else "",
                      "verbos": list(c["verbos"]), "protegido": c["protegido"], "opcional": c["opcional"]})
    return {"itens": itens, "inventario": situacao, "idade_s": idade}


# --------------------------------------------------------------------- ragnarok

def parse_ragnarok(texto, agora):
    """Le o JSON do balanceador. players_by.ragnarok some quando ha 0 humanos: ausente = 0."""
    dados = json.loads(texto)
    if not isinstance(dados, dict):
        raise ValueError("balanceador nao e um objeto")
    jogadores = 0
    por = dados.get("players_by")
    if isinstance(por, dict):
        v = por.get("ragnarok", 0)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            jogadores = int(v)
    idade = None
    parado = False
    upd = dados.get("updated")
    if isinstance(upd, (int, float)) and not isinstance(upd, bool):
        idade = max(0, int(agora - upd))
        parado = idade > IDADE_PARADO_S
    return {"jogadores": jogadores, "parado": parado, "idade_s": idade}


# ------------------------------------------------------------------------ portas

def validar_porta(item):
    """Valida {rotulo, host, porta}; devolve um dict normalizado ou levanta ValueError.

    host: IP literal ou nome simples (letras, digitos, '-' e '.'); porta: inteiro de 1 a 65535.
    """
    if not isinstance(item, dict):
        raise ValueError("porta: item deve ser um objeto")
    rotulo, host, porta = item.get("rotulo"), item.get("host"), item.get("porta")
    if not isinstance(rotulo, str) or not _ROTULO_PORTA.match(rotulo):
        raise ValueError("porta: rotulo invalido (1 a 12 caracteres: letras, digitos, _ . -)")
    if isinstance(porta, bool) or not isinstance(porta, int) or not 1 <= porta <= 65535:
        raise ValueError("porta: numero deve ser inteiro de 1 a 65535")
    if not isinstance(host, str) or not host:
        raise ValueError("porta: host ausente")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if len(host) > 253 or not _NOME_HOST.match(host):
            raise ValueError("porta: host deve ser IP literal ou nome simples") from None
    return {"rotulo": rotulo, "host": host, "porta": porta}


def coletar_portas(portas, conectar=CONECTAR_PADRAO, timeout=TIMEOUT_PORTA_S):
    """Tenta abrir conexao TCP em cada porta (em paralelo). Qualquer erro vira aberto=False."""
    def uma(item):
        rotulo = str(item.get("rotulo", "?")) if isinstance(item, dict) else "?"
        try:
            v = validar_porta(item)
            con = conectar((v["host"], v["porta"]), timeout)
            try:
                if hasattr(con, "close"):
                    con.close()
            except Exception:
                pass
            return {"rotulo": rotulo, "aberto": True}
        except Exception:
            return {"rotulo": rotulo, "aberto": False}

    portas = list(portas)
    if not portas:
        return []
    with ThreadPoolExecutor(max_workers=min(8, len(portas))) as pool:
        return list(pool.map(uma, portas))


# ------------------------------------------------------------------------ pares

def interpretar_resposta_par(corpo):
    dados = json.loads(corpo.decode("utf-8", errors="replace"))
    if not isinstance(dados, dict):
        raise ValueError("resposta do par nao e um objeto")
    return dados


def buscar_http(url, timeout=TIMEOUT_PAR_S):
    req = urllib.request.Request(url, headers={"User-Agent": "kindle-monitor"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (esquema validado antes)
        corpo = r.read(LIMITE_RESPOSTA_PAR + 1)
    if len(corpo) > LIMITE_RESPOSTA_PAR:
        raise ValueError("resposta do par grande demais")
    return interpretar_resposta_par(corpo)


def coletar_pares(pares, buscar):
    """Busca /metricas.json?pares=0 de cada par (o `pares=0` evita um par chamar o outro em loop)."""
    resultado = []
    for par in pares:
        nome = str(par.get("nome", "?"))
        try:
            base = str(par["url"]).rstrip("/")
            if urlsplit(base).scheme not in ("http", "https"):
                raise ValueError("esquema invalido")
            resultado.append({"nome": nome, "ok": True, "metricas": buscar(base + "/metricas.json?pares=0")})
        except Exception:
            resultado.append({"nome": nome, "ok": False})
    return resultado


# ----------------------------------------------------------------------- Coletor

def executar_padrao(args, timeout=3):
    """Executa comando fixo (sem shell). FileNotFoundError se o binario nao existe."""
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    return p.returncode, p.stdout


LIMITE_ARQUIVO_PADRAO = 256 * 1024
_FLAGS_LEITURA = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_NOCTTY", 0) | getattr(os, "O_CLOEXEC", 0)


def ler_arquivo_padrao(caminho, limite=LIMITE_ARQUIVO_PADRAO):
    """Texto de um arquivo regular de ate `limite` bytes; senao OSError (como arquivo ausente).

    Os arquivos vem de outros usuarios: o ultimo componente nao pode ser link (O_NOFOLLOW), O_NONBLOCK evita
    travar a thread de coleta num FIFO, e tipo e tamanho sao conferidos no descritor ja aberto (sem corrida).
    /proc e /sys declaram tamanho 0, por isso o limite tambem vale para o que foi lido."""
    fd = os.open(caminho, _FLAGS_LEITURA)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise OSError(errno.EINVAL, "nao e arquivo regular")
        if st.st_size > limite:
            raise OSError(errno.EFBIG, "arquivo grande demais")
        partes, total = [], 0
        while total <= limite:
            parte = os.read(fd, limite + 1 - total)
            if not parte:
                break
            partes.append(parte)
            total += len(parte)
        if total > limite:
            raise OSError(errno.EFBIG, "arquivo grande demais")
        return b"".join(partes).decode("utf-8", errors="replace")
    finally:
        os.close(fd)


def _isolado(fn):
    try:
        return fn()
    except Exception:
        return dict(ND)


class Coletor:
    def __init__(self, config, leitor_arquivo=ler_arquivo_padrao, executar=executar_padrao,
                 buscar=buscar_http, statvfs=os.statvfs, relogio=time.monotonic, agora=time.time,
                 dormir=time.sleep, raiz_sys="/sys", conectar=CONECTAR_PADRAO, listar_dir=os.scandir):
        self.config = config
        self._listar_dir = listar_dir
        self._ler = leitor_arquivo
        self._executar = executar
        self._buscar = buscar
        self._statvfs = statvfs
        self._relogio = relogio
        self._agora = agora
        self._raiz_sys = raiz_sys
        self._conectar = conectar
        self._cpu = CpuAmostrador(
            lambda: self._ler("/proc/stat"), dormir=dormir, relogio=relogio,
            intervalo_s=float(config.get("intervalo_cpu_s", 0.5)),
            cache_s=float(config.get("cache_cpu_s", CACHE_CPU_PADRAO)),
        )
        self._io = IoAmostrador(
            lambda caminho: self._ler(caminho), config.get("io"), dormir=dormir, relogio=relogio,
            intervalo_s=float(config.get("intervalo_io_s", INTERVALO_IO_PADRAO)),
        )
        self._catalogo = servicos.validar_catalogo(config.get("servicos_kindle") or [])
        estado = (config.get("comandos") or {}).get("estado") or INVENTARIO_ESTADO_PADRAO
        self._inventario_caminho = os.path.join(estado, INVENTARIO_ARQ)
        self._aparelhos = ecossistema.validar_aparelhos(config.get("aparelhos"))
        self._rotinas = ecossistema.validar_rotinas(config.get("rotinas"))
        self._aparelhos_caminho = os.path.join(estado, ecossistema.APARELHOS_ARQ)
        self._rotinas_caminho = os.path.join(estado, ecossistema.ROTINAS_ARQ)
        self._offline_desde = {}  # {id do aparelho: 1o instante visto offline sem `visto_em`}; ver montar_aparelhos
        self._lock_pares = threading.Lock()
        self._pares_t = None
        self._pares_v = None
        self._lock_portas = threading.Lock()
        self._portas_t = None
        self._portas_v = None
        self._intervalo_hist = float(config.get("intervalo_historico_s", INTERVALO_HISTORICO_PADRAO))
        self._hist = deque(maxlen=HISTORICO_MAX)
        self._lock_hist = threading.Lock()
        self._parar = threading.Event()
        self._thread_historico = None
        self._intervalo_coleta = float(config.get("intervalo_coleta_s", INTERVALO_COLETA_PADRAO))
        self._intervalo_lento = float(config.get("intervalo_lento_s", INTERVALO_LENTO_PADRAO))
        self._snap = None  # Snapshot imutavel; so e trocado (atribuicao atomica), nunca alterado
        self._snap_id = 0
        self._lock_snap = threading.Lock()  # serializa atualizar_snapshot
        self._lento = {}  # chave -> (t, valor) das coletas caras
        self._thread_coleta = None
        self.ao_atualizar = None  # callback(snapshot) chamado pela thread depois de cada snapshot novo
        self._parar_coleta = threading.Event()

    def servicos_kindle(self):
        """Catalogo com o estado do inventario root; None sem catalogo. Leve (le um arquivo pequeno)."""
        if not self._catalogo:
            return None
        try:
            texto = self._ler(self._inventario_caminho)
        except Exception:
            texto = None
        return montar_servicos_kindle(self._catalogo, texto, self._agora())

    def _ler_inventario(self, caminho):
        try:
            return self._ler(caminho)
        except Exception:
            return None

    def aparelhos_inventario(self):
        """Aparelhos do catalogo com o estado do inventario root; None sem catalogo."""
        if not self._aparelhos:
            return None
        return ecossistema.montar_aparelhos(self._aparelhos, self._ler_inventario(self._aparelhos_caminho),
                                            self._agora(), self._offline_desde)

    def rotinas_inventario(self):
        """Rotinas do catalogo com o estado do inventario root; None sem catalogo."""
        if not self._rotinas:
            return None
        return ecossistema.montar_rotinas(self._rotinas, self._ler_inventario(self._rotinas_caminho),
                                          self._agora())

    def servicos_itens(self):
        """Itens da tela Servicos, na ordem de exibicao (mesma lista que o render usa).

        Com a thread de coleta ativa usa o snapshot (nada de ler arquivo por requisicao)."""
        snap = self._snap if self._thread_ativa() else None
        sk = snap.metricas.get("servicos_kindle") if snap else self.servicos_kindle()
        return servicos.ordenar(sk["itens"]) if sk else []

    def _pares(self):
        with self._lock_pares:
            t = self._relogio()
            if self._pares_t is None or t - self._pares_t >= CACHE_S:
                self._pares_v = coletar_pares(self.config.get("pares") or [], self._buscar)
                self._pares_t = self._relogio()
            return self._pares_v

    def _portas(self):
        with self._lock_portas:
            t = self._relogio()
            if self._portas_t is None or t - self._portas_t >= CACHE_S:
                self._portas_v = coletar_portas(self.config.get("portas") or [], self._conectar)
                self._portas_t = self._relogio()
            return self._portas_v

    # ------------------------------------------------------------- historico
    def amostrar(self):
        """Guarda uma amostra (t, cpu%, ram%, gpu%) no anel em memoria. Falha isolada vira None."""
        def valor(fn):
            try:
                return fn()
            except Exception:
                return None

        t = self._agora()
        cpu = valor(self._cpu.medir)
        ram = valor(lambda: parse_meminfo(self._ler("/proc/meminfo"))["ram"]["pct"])
        gpu = valor(lambda: (coletar_gpu(self._executar) or {}).get("util_pct"))
        with self._lock_hist:
            self._hist.append((t, cpu, ram, gpu))

    def historico(self):
        """Series em ordem cronologica (a mais antiga primeiro). `gpu` so existe se alguma amostra teve GPU."""
        with self._lock_hist:
            amostras = list(self._hist)
        h = {
            "intervalo_s": self._intervalo_hist if self._intervalo_hist != int(self._intervalo_hist)
            else int(self._intervalo_hist),
            "max": HISTORICO_MAX,
            "t": [a[0] for a in amostras],
            "cpu": [a[1] for a in amostras],
            "ram": [a[2] for a in amostras],
        }
        if any(a[3] is not None for a in amostras):
            h["gpu"] = [a[3] for a in amostras]
        return h

    def _laco_historico(self):
        while not self._parar.is_set():
            try:
                self.amostrar()
            except Exception:
                pass
            self._parar.wait(self._intervalo_hist)

    def iniciar_historico(self):
        """Inicia a thread (daemon) que amostra a cada `intervalo_historico_s`. Idempotente."""
        if self._thread_historico is not None and self._thread_historico.is_alive():
            return
        self._parar.clear()
        self._thread_historico = threading.Thread(target=self._laco_historico, name="historico", daemon=True)
        self._thread_historico.start()

    def parar(self):
        self._parar.set()
        self._parar_coleta.set()
        for t in (self._thread_historico, self._thread_coleta):
            if t is not None:
                t.join(timeout=2)

    # ------------------------------------------------------------- snapshot
    def _thread_ativa(self):
        t = self._thread_coleta
        return t is not None and t.is_alive() and self._snap is not None

    def snapshot(self):
        """Ultimo Snapshot (id, t, metricas) ou None. Nunca bloqueia."""
        return self._snap

    def obter_metricas(self, com_pares=True):
        """(id_do_snapshot, metricas) sem coletar, se ja ha snapshot; senao coleta na hora (id None).

        As metricas sao copia rasa: o chamador pode trocar chaves de topo sem afetar o snapshot."""
        snap = self._snap
        if snap is None:
            return None, self.coletar(com_pares=com_pares)
        m = dict(snap.metricas)
        if not com_pares:
            m.pop("pares", None)
        return snap.id, m

    def _caro(self, chave, fn):
        """Valor de `fn` reutilizado por `intervalo_lento_s` (so no caminho do snapshot). Excecao propaga."""
        agora = self._relogio()
        hit = self._lento.get(chave)
        if hit is not None and agora - hit[0] < self._intervalo_lento:
            return hit[1]
        v = fn()
        self._lento[chave] = (self._relogio(), v)
        return v

    def atualizar_snapshot(self):
        """Coleta e troca o snapshot. Falha de uma metrica mantem o valor anterior; falha total mantem o snapshot."""
        with self._lock_snap:
            anterior = self._snap
            try:
                m = self.coletar(com_pares=True, _snapshot=True)
            except Exception:
                if anterior is not None:
                    return anterior
                raise
            if anterior is not None:
                for k, v in m.items():
                    if isinstance(v, dict) and "erro" in v:
                        velho = anterior.metricas.get(k)
                        if velho is not None and not (isinstance(velho, dict) and "erro" in velho):
                            m[k] = velho
            self._snap_id += 1
            self._snap = Snapshot(self._snap_id, self._agora(), m)
            return self._snap

    def _laco_coleta(self):
        while not self._parar_coleta.is_set():
            try:
                antes = self._snap
                snap = self.atualizar_snapshot()
                if snap is not antes and self.ao_atualizar is not None:
                    self.ao_atualizar(snap)
            except Exception:
                pass
            self._parar_coleta.wait(self._intervalo_coleta)

    def iniciar_coleta(self):
        """Inicia a thread (daemon) que renova o snapshot a cada `intervalo_coleta_s`. Idempotente."""
        if self._thread_coleta is not None and self._thread_coleta.is_alive():
            return
        self._parar_coleta = threading.Event()
        self._thread_coleta = threading.Thread(target=self._laco_coleta, name="coleta", daemon=True)
        self._thread_coleta.start()

    def coletar(self, com_pares=True, _snapshot=False):
        cfg = self.config
        caro = self._caro if _snapshot else (lambda chave, fn: fn())
        m = {
            "host": cfg.get("host", "?"),
            "gerado_em": datetime.fromtimestamp(self._agora()).astimezone().isoformat(timespec="seconds"),
        }
        m["cpu"] = _isolado(lambda: {"pct": self._cpu.medir(forcar=_snapshot)})
        m["carga"] = _isolado(lambda: parse_loadavg(self._ler("/proc/loadavg")))
        mem = _isolado(lambda: parse_meminfo(self._ler("/proc/meminfo")))
        m["ram"] = mem if "erro" in mem else mem["ram"]
        m["swap"] = mem if "erro" in mem else mem["swap"]
        m["uptime"] = _isolado(lambda: parse_uptime(self._ler("/proc/uptime")))

        for chave, fn in (
            ("temp_cpu", lambda: coletar_temperatura(self._raiz_sys)),
            ("gpu", lambda: caro("gpu", lambda: coletar_gpu(self._executar))),
        ):
            try:
                v = fn()
            except Exception:
                v = dict(ND)
            if v is not None:
                m[chave] = v

        if cfg.get("discos"):
            discos = []
            for d in cfg["discos"]:
                rotulo = str(d.get("rotulo", d.get("caminho", d.get("tier_state", "?"))))
                discos.append(_isolado_disco(rotulo, d, self._statvfs, self._ler, self._agora))
            m["discos"] = discos
        if cfg.get("servicos"):
            try:
                m["servicos"] = caro("servicos", lambda: coletar_servicos(cfg["servicos"], self._executar))
            except Exception:
                m["servicos"] = dict(ND)
        sk = self.servicos_kindle()
        if sk is not None:
            m["servicos_kindle"] = sk
        for chave, valor in (("aparelhos", self.aparelhos_inventario()), ("rotinas", self.rotinas_inventario())):
            if valor is not None:
                m[chave] = valor
        if cfg.get("portas"):
            try:
                m["portas"] = self._portas()
            except Exception:
                m["portas"] = dict(ND)
        if cfg.get("balanceador"):
            m["ragnarok"] = _isolado(
                lambda: parse_ragnarok(self._ler(cfg["balanceador"]), self._agora())
            )
        io = cfg.get("io")
        if isinstance(io, dict) and (io.get("discos") or io.get("redes")):
            m["io"] = _isolado(self._io.medir)
        if cfg.get("claude"):
            m["claude"] = _isolado(lambda: coletar_claude(cfg["claude"], self._ler, self._agora()))
            if isinstance(cfg["claude"], dict) and cfg["claude"].get("sessoes") and "erro" not in m["claude"]:
                m["claude"]["sessoes"] = _isolado(lambda: caro("sessoes", lambda: dev_fontes.coletar_sessoes(
                    _caminho_dev(cfg["claude"]["sessoes"]), self._listar_dir, self._ler, self._agora())))
        if isinstance(cfg.get("github"), dict) and cfg["github"].get("resumo"):
            m["github"] = _isolado(lambda: dev_fontes.coletar_github(
                _caminho_dev(cfg["github"]["resumo"]), self._ler, self._agora()))
        if cfg.get("s10"):
            m["s10"] = _isolado(lambda: coletar_s10(cfg["s10"]["resumo"], self._ler, self._agora()))
        m["limiares"] = alertas.limiares(cfg.get("limiares"))
        m["historico"] = self.historico()
        if com_pares and cfg.get("pares"):
            try:
                m["pares"] = self._pares()
            except Exception:
                m["pares"] = []
        return m


def _isolado_disco(rotulo, d, statvfs, ler, agora):
    try:
        if "tier_state" in d:
            return coletar_tier_state(rotulo, d["tier_state"], ler, agora())
        return coletar_disco(rotulo, d["caminho"], statvfs)
    except Exception:
        return {"rotulo": rotulo, "erro": "n/d"}
