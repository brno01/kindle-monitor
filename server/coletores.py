"""Coletores de metricas do kindle-monitor.

Somente leitura, somente biblioteca padrao. As funcoes `parse_*` sao puras (recebem
texto bruto); as `coletar_*` recebem callables injetaveis (executar, buscar, statvfs)
para os testes nao dependerem de nvidia-smi, systemctl, rede nem /var/lib/cerberus.

Convencao de falha: cada coletor falha isolado. Na classe `Coletor`, qualquer excecao
vira `{"erro": "n/d"}` naquela metrica; coletor "ausente" (sem GPU, sem sensor) omite a chave.
"""
import glob
import ipaddress
import json
import os
import re
import socket
import subprocess
import threading
import time
import urllib.request
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlsplit

ND = {"erro": "n/d"}
CACHE_S = 5.0
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
    """Duas leituras de /proc/stat com intervalo curto; resultado em cache por ~5 s."""

    def __init__(self, leitor, dormir=time.sleep, relogio=time.monotonic, intervalo_s=0.5, cache_s=CACHE_S):
        self._leitor = leitor
        self._dormir = dormir
        self._relogio = relogio
        self._intervalo = intervalo_s
        self._cache_s = cache_s
        self._lock = threading.Lock()
        self._t = None
        self._valor = None

    def medir(self):
        with self._lock:
            agora = self._relogio()
            if self._t is not None and agora - self._t < self._cache_s:
                return self._valor
            a = parse_cpu_stat(self._leitor())
            self._dormir(self._intervalo)
            b = parse_cpu_stat(self._leitor())
            self._valor = calcular_cpu(a, b)
            self._t = self._relogio()
            return self._valor


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
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0


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


def ler_arquivo_padrao(caminho):
    with open(caminho, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _isolado(fn):
    try:
        return fn()
    except Exception:
        return dict(ND)


class Coletor:
    def __init__(self, config, leitor_arquivo=ler_arquivo_padrao, executar=executar_padrao,
                 buscar=buscar_http, statvfs=os.statvfs, relogio=time.monotonic, agora=time.time,
                 dormir=time.sleep, raiz_sys="/sys", conectar=CONECTAR_PADRAO):
        self.config = config
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
        )
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
        if self._thread_historico is not None:
            self._thread_historico.join(timeout=2)

    def coletar(self, com_pares=True):
        cfg = self.config
        m = {
            "host": cfg.get("host", "?"),
            "gerado_em": datetime.fromtimestamp(self._agora()).astimezone().isoformat(timespec="seconds"),
        }
        m["cpu"] = _isolado(lambda: {"pct": self._cpu.medir()})
        m["carga"] = _isolado(lambda: parse_loadavg(self._ler("/proc/loadavg")))
        mem = _isolado(lambda: parse_meminfo(self._ler("/proc/meminfo")))
        m["ram"] = mem if "erro" in mem else mem["ram"]
        m["swap"] = mem if "erro" in mem else mem["swap"]
        m["uptime"] = _isolado(lambda: parse_uptime(self._ler("/proc/uptime")))

        for chave, fn in (
            ("temp_cpu", lambda: coletar_temperatura(self._raiz_sys)),
            ("gpu", lambda: coletar_gpu(self._executar)),
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
                m["servicos"] = coletar_servicos(cfg["servicos"], self._executar)
            except Exception:
                m["servicos"] = dict(ND)
        if cfg.get("portas"):
            try:
                m["portas"] = self._portas()
            except Exception:
                m["portas"] = dict(ND)
        if cfg.get("balanceador"):
            m["ragnarok"] = _isolado(
                lambda: parse_ragnarok(self._ler(cfg["balanceador"]), self._agora())
            )
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
