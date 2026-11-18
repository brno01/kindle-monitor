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

# aba aberta ao tocar na linha de cada sistema (E3 do plano; o Kindle nao tem linha, vai para Sistema)
_PAGINA = {"atheron": "detalhes", "nas": "detalhes", "rotinas": "detalhes", "kindle": "detalhes",
           "aparelhos": "aparelhos", "servicos": "servicos", "ragnarok": "servicos",
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


def _texto(antes, rotulo=None, depois=""):
    """`antes` + rotulo + `depois`, com o rotulo cortado para o total caber em TEXTO_MAX."""
    if rotulo is None:
        return (antes + depois)[:TEXTO_MAX]
    rot = _ascii(rotulo) or "?"
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
        out.append(_alerta(nivel, _texto("Disco ", d.get("rotulo", "?"), " %s%%%s" % (_pct(pct), livre)), sistema))
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
    return [_alerta("critico", _texto("", i.get("rotulo", "?"), " em falha"), "servicos")
            for i in _itens_servicos(m) if i.get("estado") == "falha"]


def _r_rotinas_falha(m, lim, kv):
    return [_alerta("critico", _texto("", i.get("rotulo", "?"), " falhou"), "rotinas")
            for i in _lista(_dict(m.get("rotinas")).get("itens"))
            if isinstance(i, dict) and i.get("resultado") == "falha"]


def _r_unidades_falhas(m, lim, kv):
    u = _dict(_dict(m.get("rotinas")).get("unidades_falhas"))
    n = _num(u.get("n"))
    if n is None or n <= 0:
        return []
    nomes = [_ascii(x) for x in _lista(u.get("nomes")) if isinstance(x, str)]
    nomes = [x for x in nomes if x][:2]
    depois = ": " + ", ".join(x[:16] for x in nomes) if nomes else ""
    return [_alerta("critico", _texto("%s unidades em falha" % _pct(n), None, depois), "rotinas")]


def _r_aparelhos_offline(m, lim, kv):
    out = []
    for i in _lista(_dict(m.get("aparelhos")).get("itens")):
        i = _dict(i)
        alvo, off = _num(i.get("alerta_offline_min")), _num(i.get("offline_min"))
        if alvo is not None and alvo > 0 and off is not None and off >= alvo:
            out.append(_alerta("critico", _texto("", i.get("rotulo", "?"), " offline ha %s min" % _pct(off)),
                               "aparelhos"))
    return out


def _r_servicos_parados(m, lim, kv):
    return [_alerta("aviso", _texto("", i.get("rotulo", "?"), " parado"), "servicos")
            for i in _itens_servicos(m) if i.get("estado") == "parado" and not i.get("opcional")]


def _r_inventario_servicos(m, lim, kv):
    inv = _dict(m.get("servicos_kindle")).get("inventario")
    if inv in ("velho", "ausente"):
        return [_alerta("aviso", "Inventario de servicos %s" % inv, "servicos")]
    return []


def _r_rotinas_atrasadas(m, lim, kv):
    return [_alerta("aviso", _texto("", i.get("rotulo", "?"), " atrasada"), "rotinas")
            for i in _lista(_dict(m.get("rotinas")).get("itens"))
            if isinstance(i, dict) and i.get("atrasada") is True and i.get("resultado") != "falha"]


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
    return [_alerta("aviso", _texto("Porta ", p.get("rotulo", "?"), " fechada"), "ragnarok")
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


def _fonte_velha(nome, sistema, bloco):
    idade = _num(_dict(bloco).get("idade_s"))
    if idade is not None and idade >= 0:
        texto = _texto("dados de %s sem atualizar ha %s min" % (_ascii(nome), _pct(idade // 60)))
    else:
        texto = _texto("dados de %s desatualizados" % _ascii(nome))
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
    for nome, bloco in (("aparelhos", m.get("aparelhos")), ("rotinas", m.get("rotinas"))):
        if _dict(bloco).get("inventario") == "velho":
            out.append(_fonte_velha(nome, nome, bloco))
    return out


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
           _r_rotinas_atrasadas, _r_claude_limites, _r_ci, _r_portas,
           _r_bateria_kindle, _r_bateria_s10, _r_fontes_velhas,
           _r_sessoes)


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
