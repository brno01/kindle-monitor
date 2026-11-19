"""Motor de alertas do painel: transforma as metricas (`m`) em uma lista curta de alertas por gravidade.

Funcao pura: `avaliar(m, lim, kv)` nunca levanta (entrada malformada vira "sem alerta" naquela regra) e nao faz E/S.
Cada alerta e `{"nivel": "critico"|"aviso"|"leve", "texto": ASCII ate 48, "pagina": id de pagina, "sistema": ...}`.
Ordem: critico, aviso, leve; dentro do nivel, a ordem das regras abaixo (estavel).

`limiares(cfg)` valida a secao `limiares` da config (o coletor a publica em `m["limiares"]`). A bateria do Kindle
chega a cada pedido, por isso entra como `kv` (a vista de `kindle_status`).
"""
import math
import unicodedata

import servicos

PADRAO = {"disco_aviso": 85, "disco_critico": 93, "ram": 90, "swap": 50, "temp_cpu_c": 85, "kindle_bateria": 15,
          "s10_bateria": 20, "claude_limite": 90, "sessao_esperando_min": 10}

_FAIXAS = {k: (1, 100) for k in PADRAO}
_FAIXAS["temp_cpu_c"] = (40, 120)
_FAIXAS["sessao_esperando_min"] = (1, 1440)

TEXTO_MAX = 48
NIVEIS = ("critico", "aviso", "leve")
GIB = 2 ** 30

# pagina aberta ao tocar na linha de cada sistema (E3 do plano; o Kindle nao tem linha, vai para Sistema). `jogos` (portas
# do Ragnarok) e `amp` (servidores do AMP) abrem a pagina Jogos, que nao e aba; so `jogos` conta para a forma da linha
# JOGOS da tela inicial (o aviso "AMP sem dados" vira o "?" da linha, ver render_png._l_jogos)
_PAGINA = {"atheron": "detalhes", "nas": "detalhes", "rotinas": "detalhes", "kindle": "detalhes",
           "aparelhos": "aparelhos", "servicos": "servicos", "jogos": "jogos", "amp": "jogos",
           "claude": "claude", "github": "claude"}


# ------------------------------------------------------------------ utilidades

def _num(v):
    """int/float finito (nunca bool) ou None."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    try:
        return v if math.isfinite(v) else None
    except (OverflowError, ValueError):
        return None


def _dict(v):
    return v if isinstance(v, dict) else {}


def _lista(v):
    return v if isinstance(v, list) else []


def _ascii(valor):
    """Texto so com ASCII imprimivel, espacos colapsados."""
    try:
        s = unicodedata.normalize("NFKD", str(valor))
    except Exception:
        return ""
    s = "".join(ch for ch in s if ch.isascii() and ch.isprintable() or ch in "\t\n ")
    return " ".join(s.split())


_SEM_ROTULO = object()


def _texto(antes, rotulo=_SEM_ROTULO, depois=""):
    """`antes` + rotulo + `depois`, com o rotulo cortado para o total caber em TEXTO_MAX.

    Sem argumento de rotulo, nao ha rotulo; rotulo `None`, ausente ou vazio vira "?"."""
    if rotulo is _SEM_ROTULO:
        return (antes + depois)[:TEXTO_MAX]
    rot = _ascii(rotulo) if rotulo is not None else ""
    rot = rot or "?"
    sobra = max(1, TEXTO_MAX - len(antes) - len(depois))
    return (antes + rot[:sobra] + depois)[:TEXTO_MAX].rstrip()


def _pct(v):
    """Inteiro arredondado para o texto, limitado para nao gerar numeros enormes."""
    return "%d" % round(min(max(v, -999999), 999999))


def _alerta(nivel, texto, sistema):
    return {"nivel": nivel, "texto": texto, "pagina": _PAGINA[sistema], "sistema": sistema}


def limiares(cfg):
    """PADRAO com as chaves validas de `cfg` aplicadas. Chave desconhecida e ignorada; valor que nao e numero
    (bool inclusive), nao finito ou fora da faixa da chave volta ao padrao daquela chave."""
    r = dict(PADRAO)
    if not isinstance(cfg, dict):
        return r
    for k, (lo, hi) in _FAIXAS.items():
        v = _num(cfg.get(k))
        if v is not None and lo <= v <= hi:
            r[k] = v
    if r["disco_critico"] < r["disco_aviso"]:
        r["disco_aviso"], r["disco_critico"] = PADRAO["disco_aviso"], PADRAO["disco_critico"]
    return r


# ----------------------------------------------------------------------- regras
# Cada regra recebe o contexto (m, lim, kv) e devolve uma lista de alertas; falha de uma nao afeta as outras.

def _r_discos(m, lim, kv):
    out = []
    for d in _lista(m.get("discos")):
        d = _dict(d)
        pct = _num(d.get("pct"))
        if pct is None or pct < lim["disco_aviso"]:
            continue
        nivel = "critico" if pct >= lim["disco_critico"] else "aviso"
        sistema = "atheron" if d.get("caminho") == "/" else "nas"
        livre = ""
        total, usado = _num(d.get("total_b")), _num(d.get("usado_b"))
        if total is not None and usado is not None and 0 <= usado <= total:
            livre = " - %.1f GB livres" % ((total - usado) / GIB)
        out.append(_alerta(nivel, _texto("Disco ", d.get("rotulo"), " %s%%%s" % (_pct(pct), livre)), sistema))
    return out


def _r_ram(m, lim, kv):
    pct = _num(_dict(m.get("ram")).get("pct"))
    if pct is not None and pct >= lim["ram"]:
        return [_alerta("aviso", _texto("RAM em %s%%" % _pct(pct)), "atheron")]
    return []


def _r_swap(m, lim, kv):
    s = _dict(m.get("swap"))
    pct, total = _num(s.get("pct")), _num(s.get("total_kb"))
    if pct is not None and total is not None and total > 0 and pct >= lim["swap"]:
        return [_alerta("aviso", _texto("Swap em %s%%" % _pct(pct)), "atheron")]
    return []


def _r_temp(m, lim, kv):
    c = _num(_dict(m.get("temp_cpu")).get("c"))
    if c is not None and c >= lim["temp_cpu_c"]:
        return [_alerta("aviso", _texto("CPU a %s C" % _pct(c)), "atheron")]
    return []


def _itens_servicos(m):
    return [i for i in servicos.itens_de(m) if isinstance(i, dict)]


def _r_servicos_falha(m, lim, kv):
    return [_alerta("critico", _texto("", i.get("rotulo"), " em falha"), "servicos")
            for i in _itens_servicos(m) if i.get("estado") == "falha"]


def _r_rotinas_falha(m, lim, kv):
    return [_alerta("critico", _texto("", i.get("rotulo"), " falhou"), "rotinas")
            for i in _lista(_dict(m.get("rotinas")).get("itens"))
            if isinstance(i, dict) and i.get("resultado") == "falha"]


def _alvos_em_falha(m):
    """Unidades `alvo` das rotinas `timer` em falha: ja alertadas pela propria rotina."""
    return {_ascii(i.get("alvo")) for i in _lista(_dict(m.get("rotinas")).get("itens"))
            if isinstance(i, dict) and i.get("resultado") == "falha" and i.get("tipo") == "timer"
            and isinstance(i.get("alvo"), str)}


def _r_unidades_falhas(m, lim, kv):
    u = _dict(_dict(m.get("rotinas")).get("unidades_falhas"))
    n = _num(u.get("n"))
    if n is None or n < 1:
        return []
    nomes = [_ascii(x) for x in _lista(u.get("nomes")) if isinstance(x, str)]
    nomes = [x for x in nomes if x]
    cobertos = _alvos_em_falha(m)
    if cobertos:
        # a unidade da rotina em falha ja tem o alerta da rotina: sai da contagem e da lista
        restam = [x for x in nomes if x not in cobertos]
        n -= len(nomes) - len(restam)
        nomes = restam
        if n < 1:
            return []
    nomes = nomes[:2]
    antes = "%s %s em falha" % (_pct(n), "unidade" if round(n) == 1 else "unidades")
    if not nomes:
        return [_alerta("critico", _texto(antes), "rotinas")]
    lista = ", ".join(nomes)
    sobra = TEXTO_MAX - len(antes) - 2
    if len(lista) > sobra:  # nao cabe: corta a lista (nao o texto final) e avisa com reticencias
        lista = lista[:max(1, sobra - 3)].rstrip(", ") + "..."
    return [_alerta("critico", _texto(antes + ": " + lista), "rotinas")]


def _r_aparelhos_offline(m, lim, kv):
    out = []
    for i in _lista(_dict(m.get("aparelhos")).get("itens")):
        i = _dict(i)
        alvo, off = _num(i.get("alerta_offline_min")), _num(i.get("offline_min"))
        if alvo is not None and alvo > 0 and off is not None and off >= alvo:
            out.append(_alerta("critico", _texto("", i.get("rotulo"), " offline ha %s min" % _pct(off)),
                               "aparelhos"))
    return out


def _r_servicos_parados(m, lim, kv):
    return [_alerta("aviso", _texto("", i.get("rotulo"), " parado"), "servicos")
            for i in _itens_servicos(m) if i.get("estado") == "parado" and not i.get("opcional")]


def _inventarios_parados(m):
    """Blocos de inventario root parados: servicos (velho ou ausente), aparelhos e rotinas (velho). Com 2 ou mais a
    causa e a mesma (o executor root parou) e `_r_inventario_servicos` emite um aviso so."""
    out = []
    sk = _dict(m.get("servicos_kindle"))
    if sk.get("inventario") in ("velho", "ausente"):
        out.append(sk)
    for nome in ("aparelhos", "rotinas"):
        b = _dict(m.get(nome))
        if b.get("inventario") == "velho":
            out.append(b)
    amp = _dict(m.get("amp"))
    if amp.get("inventario") == "velho" and amp.get("ativo") is True:  # sem credencial, o AMP nem esta ligado
        out.append(amp)
    return out


def _r_inventario_servicos(m, lim, kv):
    parados = _inventarios_parados(m)
    if len(parados) >= 2:
        if any(b.get("relogio_adiantado") is True for b in parados):
            return [_alerta("aviso", "Inventario root com relogio adiantado", "servicos")]
        idades = [v for v in (_num(b.get("idade_s")) for b in parados) if v is not None and v >= 0]
        texto = ("Inventario root sem atualizar ha %s min" % _pct(max(idades) // 60) if idades
                 else "Inventario root sem atualizar")
        return [_alerta("aviso", _texto(texto), "servicos")]
    inv = _dict(m.get("servicos_kindle")).get("inventario")
    if inv in ("velho", "ausente"):
        return [_alerta("aviso", "Inventario de servicos %s" % inv, "servicos")]
    return []


# o arquivo `senhas-arq` e o resultado do mesmo backup que a timer `senhas`: atrasadas juntas, so a timer alerta
_ARQUIVO_DO_MESMO_BACKUP = {"senhas-arq": "senhas"}


def _r_rotinas_atrasadas(m, lim, kv):
    its = [i for i in _lista(_dict(m.get("rotinas")).get("itens"))
           if isinstance(i, dict) and i.get("atrasada") is True and i.get("resultado") != "falha"]
    ids = {i.get("id") for i in its}
    return [_alerta("aviso", _texto("", i.get("rotulo"), " atrasada"), "rotinas") for i in its
            if _ARQUIVO_DO_MESMO_BACKUP.get(i.get("id"), object()) not in ids]


def _r_rotinas_sem_dados(m, lim, kv):
    """Rotina `desconhecido` nunca falha nem atrasa, entao o painel parecia verde sem dado nenhum. Todas as
    rotinas do catalogo desconhecidas (inventario ok, ex.: o systemctl falhou) = um aviso so; uma isolada = alerta
    leve, mas so para `timer` (um `arquivo` desconhecido pode ainda nao existir de proposito)."""
    r = _dict(m.get("rotinas"))
    if r.get("inventario") != "ok":
        return []
    its = [i for i in _lista(r.get("itens")) if isinstance(i, dict)]
    if not its:
        return []
    desconhecidas = [i for i in its if i.get("resultado") == "desconhecido"]
    if len(desconhecidas) == len(its):
        return [_alerta("aviso", "Rotinas sem dados", "rotinas")]
    return [_alerta("leve", _texto("Rotina ", i.get("rotulo"), " sem dado"), "rotinas")
            for i in desconhecidas if i.get("tipo") == "timer"]


def _r_claude_limites(m, lim, kv):
    out = []
    limites = _dict(_dict(m.get("claude")).get("limites"))
    for chave, nome in (("cinco_horas", "5h"), ("semanal", "semanal")):
        j = _dict(limites.get(chave))
        pct = _num(j.get("pct"))
        if pct is not None and j.get("renovado") is not True and pct >= lim["claude_limite"]:
            out.append(_alerta("aviso", _texto("Limite Claude %s em %s%%" % (nome, _pct(pct))), "claude"))
    return out


def _r_ci(m, lim, kv):
    return [_alerta("aviso", _texto("CI falhou em ", c.get("repo", "?")), "github")
            for c in _lista(_dict(m.get("github")).get("ci"))
            if isinstance(c, dict) and c.get("estado") == "falha"]


def _r_portas(m, lim, kv):
    return [_alerta("aviso", _texto("Porta ", p.get("rotulo"), " fechada"), "jogos")
            for p in _lista(m.get("portas")) if isinstance(p, dict) and p.get("aberto") is False]


def _r_bateria_kindle(m, lim, kv):
    b = _num(kv.get("bateria"))
    if b is not None and not kv.get("carregando") and b <= lim["kindle_bateria"]:
        return [_alerta("aviso", _texto("Bateria do Kindle %s%%" % _pct(b)), "kindle")]
    return []


def _r_bateria_s10(m, lim, kv):
    bat = _dict(_dict(m.get("s10")).get("bateria"))
    n = _num(bat.get("nivel"))
    if n is not None and n <= lim["s10_bateria"] and bat.get("status") in ("discharging", "not_charging"):
        return [_alerta("aviso", _texto("Bateria do S10 %s%%" % _pct(n)), "aparelhos")]
    return []


_NOME_FONTE = {"limites": "Limites do Claude", "tokens": "Tokens do Claude", "s10": "S10", "github": "GitHub",
               "aparelhos": "Aparelhos", "rotinas": "Rotinas", "amp": "AMP"}


def _fonte_velha(nome, sistema, bloco):
    legivel = _NOME_FONTE.get(nome) or _ascii(nome).capitalize()
    idade = _num(_dict(bloco).get("idade_s"))
    if _dict(bloco).get("relogio_adiantado") is True:
        texto = _texto("%s sem atualizar com relogio adiantado" % legivel)
    elif idade is not None and idade >= 0:
        texto = _texto("%s sem atualizar ha %s min" % (legivel, _pct(idade // 60)))
    else:
        texto = _texto("%s sem atualizar" % legivel)
    return _alerta("aviso", texto, sistema)


def _r_fontes_velhas(m, lim, kv):
    out = []
    claude = _dict(m.get("claude"))
    for nome, sistema, bloco in (("limites", "claude", claude.get("limites")),
                                 ("tokens", "claude", claude.get("tokens")),
                                 ("s10", "aparelhos", m.get("s10")),
                                 ("github", "github", m.get("github"))):
        if _dict(bloco).get("velho") is True:
            out.append(_fonte_velha(nome, sistema, bloco))
    if len(_inventarios_parados(m)) < 2:  # com 2 ou mais, `_r_inventario_servicos` ja deu o aviso unico
        for nome, bloco in (("aparelhos", m.get("aparelhos")), ("rotinas", m.get("rotinas")), ("amp", m.get("amp"))):
            if _dict(bloco).get("inventario") == "velho" and (nome != "amp" or _dict(bloco).get("ativo") is True):
                out.append(_fonte_velha(nome, nome, bloco))
    return out


def _r_amp_sem_dados(m, lim, kv):
    """AMP ligado (o executor tem a credencial) mas a coleta falhou: sem numero nenhum nao se pode dizer que esta tudo
    bem. Leve, porque o aviso do proprio jogo (porta fechada) e outro. Inventario velho tem aviso proprio. Instancia
    parada ou em falha NAO alerta: desligar um servidor e normal."""
    b = _dict(m.get("amp"))
    if b.get("ativo") is True and b.get("inventario") == "ok" and isinstance(b.get("erro"), str) and b["erro"].strip():
        return [_alerta("leve", "AMP sem dados", "amp")]
    return []


def _r_sessoes(m, lim, kv):
    out = []
    minimo = lim["sessao_esperando_min"] * 60
    for s in _lista(_dict(_dict(m.get("claude")).get("sessoes")).get("itens")):
        s = _dict(s)
        desde = _num(s.get("desde_s"))
        if s.get("estado") == "esperando" and desde is not None and desde >= minimo:
            out.append(_alerta("leve", _texto("Sessao ", s.get("projeto", "?"), " esperando ha %s min"
                                              % _pct(desde // 60)), "claude"))
    return out


# na ordem de E6: critico, aviso (recursos, servicos, rotinas, claude, ci/portas, baterias, fontes), leve
_REGRAS = (_r_discos, _r_servicos_falha, _r_rotinas_falha, _r_unidades_falhas, _r_aparelhos_offline,
           _r_ram, _r_swap, _r_temp,
           _r_servicos_parados, _r_inventario_servicos,
           _r_rotinas_atrasadas, _r_rotinas_sem_dados, _r_claude_limites, _r_ci, _r_portas,
           _r_bateria_kindle, _r_bateria_s10, _r_fontes_velhas,
           _r_sessoes, _r_amp_sem_dados)


def avaliar(m, lim=None, kv=None):
    """Lista de alertas de `m` (metricas), ordenada critico, aviso, leve. Nunca levanta.

    `lim`: limiares (passam por `limiares()`); sem `lim`, vale `m["limiares"]` se houver, senao PADRAO.
    `kv`: estado do Kindle (`kindle_status.vista`), de onde saem `bateria` e `carregando`.
    """
    if not isinstance(m, dict):
        return []
    try:
        lim = limiares(lim if lim is not None else m.get("limiares"))
        kv = kv if isinstance(kv, dict) else {}
    except Exception:
        lim, kv = dict(PADRAO), {}
    alertas = []
    for regra in _REGRAS:
        try:
            alertas.extend(regra(m, lim, kv))
        except Exception:
            continue
    alertas.sort(key=lambda a: NIVEIS.index(a["nivel"]))  # estavel
    return alertas
