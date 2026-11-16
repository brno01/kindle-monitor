"""Catalogo de servicos do Kindle (puro, sem I/O): validacao, nome do pedido no spool, itens e paginacao.

O executor root (deploy/kindle-monitor-executor.py) e autocontido e repete as regras de `validar_catalogo`
(um teste confere que os dois concordam). Aqui fica o lado web, que nunca executa nada.
"""
import re

GRUPOS = ("host", "incus", "docker", "ragnarok")
TIPOS = ("systemd", "incus", "docker", "rathena")
VERBOS = ("reiniciar", "ligar", "parar")
ESTADOS = ("ativo", "parado", "falha", "desconhecido")
TITULOS_GRUPO = {"host": "HOST", "incus": "CONTEINERES", "docker": "DOCKER", "ragnarok": "RAGNAROK"}
RE_ID = re.compile(r"^[a-z0-9]([a-z0-9-]{0,38}[a-z0-9])?$")
RE_ALVO = re.compile(r"^[A-Za-z0-9_.@-]{1,64}$")
RE_PROJETO = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
ROTULO_MAX = 28
CHAVES = {"id", "rotulo", "grupo", "tipo", "alvo", "projeto", "prefixo", "verbos", "protegido", "opcional"}
RE_SVC_ACAO = re.compile(r"^svc:([a-z0-9-]{1,40}):(reiniciar|ligar|parar)$")
RE_SVC_ARQ = re.compile(r"^svc--([a-z0-9-]{1,40})--(reiniciar|ligar|parar)$")
RE_ACAO_ARQ = re.compile(r"^[a-z-]{3,32}$")
# fragmento de regex para o nome do arquivo no spool (depois de "<epoch>-")
TOKEN_ARQ = r"(?:svc--[a-z0-9-]{1,40}--(?:reiniciar|ligar|parar)|[a-z-]{3,32})"


def validar_catalogo(lista):
    """Normaliza `servicos_kindle`. ValueError com a causa. [] e valido."""
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise ValueError("servicos_kindle deve ser uma lista")
    ids, saida = set(), []
    for i, it in enumerate(lista):
        r = "servicos_kindle[%d]" % i
        if not isinstance(it, dict):
            raise ValueError("%s deve ser um objeto" % r)
        extra = set(it) - CHAVES
        if extra:
            raise ValueError("%s: chave desconhecida %s" % (r, sorted(map(str, extra))[0][:30]))
        sid = it.get("id")
        if not isinstance(sid, str) or not RE_ID.match(sid) or "--" in sid:
            raise ValueError("%s: id invalido" % r)
        if sid in ids:
            raise ValueError("%s: id repetido (%s)" % (r, sid))
        ids.add(sid)
        rot = it.get("rotulo")
        if not isinstance(rot, str) or not 1 <= len(rot) <= ROTULO_MAX or \
                not all(32 <= ord(ch) < 127 for ch in rot):
            raise ValueError("%s: rotulo deve ser ASCII de 1 a %d" % (r, ROTULO_MAX))
        if it.get("grupo") not in GRUPOS:
            raise ValueError("%s: grupo invalido" % r)
        tipo = it.get("tipo")
        if tipo not in TIPOS:
            raise ValueError("%s: tipo invalido" % r)
        alvo = it.get("alvo")
        if not isinstance(alvo, str) or not RE_ALVO.match(alvo) or alvo.startswith("-"):
            raise ValueError("%s: alvo invalido" % r)
        if tipo in ("systemd", "rathena") and not alvo.endswith(".service"):
            raise ValueError("%s: alvo de unit deve terminar em .service" % r)
        projeto = it.get("projeto", "core" if tipo == "incus" else None)
        if "projeto" in it and tipo != "incus":
            raise ValueError("%s: projeto so vale para incus" % r)
        if tipo == "incus" and (not isinstance(projeto, str) or not RE_PROJETO.match(projeto)):
            raise ValueError("%s: projeto invalido" % r)
        prefixo = it.get("prefixo", False)
        if not isinstance(prefixo, bool) or (prefixo and tipo != "docker"):
            raise ValueError("%s: prefixo so vale (booleano) para docker" % r)
        verbos = it.get("verbos")
        if not isinstance(verbos, list) or not all(isinstance(v, str) and v in VERBOS for v in verbos) or \
                len(set(verbos)) != len(verbos):
            raise ValueError("%s: verbos deve ser subconjunto de %s" % (r, ", ".join(VERBOS)))
        if prefixo and verbos:
            raise ValueError("%s: prefixo exige verbos []" % r)
        for k in ("protegido", "opcional"):
            if not isinstance(it.get(k, False), bool):
                raise ValueError("%s: %s deve ser booleano" % (r, k))
        n = {"id": sid, "rotulo": rot, "grupo": it["grupo"], "tipo": tipo, "alvo": alvo, "verbos": list(verbos),
             "protegido": it.get("protegido", False), "opcional": it.get("opcional", False),
             "prefixo": prefixo}
        if tipo == "incus":
            n["projeto"] = projeto
        saida.append(n)
    return saida


# ------------------------------------------------------------- nome no spool

def acao_para_nome(acao):
    """'svc:<id>:<verbo>' -> 'svc--<id>--<verbo>'; acoes rapidas ficam como estao. ValueError se invalida."""
    m = RE_SVC_ACAO.match(acao)
    if m:
        return "svc--%s--%s" % m.groups()
    if RE_ACAO_ARQ.match(acao) and not acao.startswith("svc--"):
        return acao
    raise ValueError("acao invalida")


def nome_para_acao(token):
    """Inverso de `acao_para_nome`; None se o token nao e valido."""
    if token.startswith("svc--"):
        m = RE_SVC_ARQ.match(token)
        return "svc:%s:%s" % m.groups() if m else None
    return token if RE_ACAO_ARQ.match(token) else None


def acao_svc(acao):
    """(id, verbo) de 'svc:<id>:<verbo>' ou None."""
    m = RE_SVC_ACAO.match(acao) if isinstance(acao, str) else None
    return m.groups() if m else None


def rotulo_acao(acao):
    """Texto curto para a lista de comandos recentes: 'Reiniciar ai-coder' para svc, o id nos demais."""
    s = acao_svc(acao)
    return "%s %s" % (s[1].capitalize(), s[0]) if s else str(acao)


# ------------------------------------------------------------------- itens

def itens_de(m):
    """Itens para a tela: `servicos_kindle.itens` (catalogo) ou, sem ele, os `servicos` antigos (grupo host, sem verbos)."""
    sk = m.get("servicos_kindle") if isinstance(m, dict) else None
    if isinstance(sk, dict) and isinstance(sk.get("itens"), list):
        return [i for i in sk["itens"] if isinstance(i, dict)]
    leg = m.get("servicos") if isinstance(m, dict) else None
    saida = []
    for n, s in enumerate(leg if isinstance(leg, list) else []):
        if not isinstance(s, dict):
            continue
        nome = str(s.get("nome", "?"))
        nome = nome[:-8] if nome.endswith(".service") and len(nome) > 8 else nome
        estado = "desconhecido" if "erro" in s else ("ativo" if s.get("ativo") else "falha")
        saida.append({"id": "legado-%d" % n, "rotulo": nome[:ROTULO_MAX], "grupo": "host", "estado": estado,
                      "detalhe": "", "verbos": [], "protegido": False, "opcional": False})
    return saida


def ordenar(itens):
    """Agrupa por grupo na ordem fixa, mantendo a ordem do catalogo dentro de cada um."""
    pos = {g: i for i, g in enumerate(GRUPOS)}
    return sorted(itens, key=lambda i: pos.get(i.get("grupo"), 0))  # estavel


def resumo(itens):
    """{'total','ok','parados','falhas','desconhecidos','atencao': [item]}; atencao = falha, desconhecido ou parado nao opcional."""
    r = {"total": len(itens), "ok": 0, "parados": 0, "falhas": 0, "desconhecidos": 0, "atencao": []}
    for i in itens:
        e = i.get("estado")
        if e == "ativo":
            r["ok"] += 1
        elif e == "parado":
            r["parados"] += 1
            if not i.get("opcional"):
                r["atencao"].append(i)
        elif e == "falha":
            r["falhas"] += 1
            r["atencao"].append(i)
        else:
            r["desconhecidos"] += 1
    # falhas primeiro, depois parados
    r["atencao"].sort(key=lambda i: 0 if i.get("estado") == "falha" else 1)
    return r


def texto_resumo(itens, sep=" \u00b7 "):
    r = resumo(itens)
    partes = ["%d servicos" % r["total"], "%d ok" % r["ok"]]
    if r["parados"]:
        partes.append("%d parados" % r["parados"])
    if r["falhas"]:
        partes.append("%d falhas" % r["falhas"])
    if r["desconhecidos"]:
        partes.append("%d ?" % r["desconhecidos"])
    return sep.join(partes)


def verbos_visiveis(item):
    """Verbos mostrados como botao, conforme o estado (ver README)."""
    v = item.get("verbos") or []
    e = item.get("estado")
    if e == "ativo":
        return [x for x in ("reiniciar", "parar") if x in v]
    if e == "parado":
        if "ligar" in v:
            return ["ligar"]
        return ["reiniciar"] if "reiniciar" in v else []
    if e == "falha":
        if "reiniciar" in v:
            return ["reiniciar"]
        return ["ligar"] if "ligar" in v else []
    return []


# --------------------------------------------------------------- paginacao

ROW_H = 100          # botao 84 + 16 de espaco
ROW_H_SEM_BOTAO = 64
CAB_H = 52


def altura_linha(item):
    return ROW_H if item.get("verbos") else ROW_H_SEM_BOTAO


def paginar(itens, disponivel):
    """Divide os itens ordenados em paginas que cabem em `disponivel` px.

    Cada pagina e uma lista de ("cab", grupo) e ("svc", indice em `itens`). Um cabecalho nunca fica sozinho
    no fim da pagina; o grupo repete o cabecalho se continuar na pagina seguinte. Nao depende do estado.
    """
    paginas, atual, usado, grupo_atual = [], [], 0, None
    for idx, it in enumerate(itens):
        g = it.get("grupo")
        h = altura_linha(it)
        precisa = h + (CAB_H if g != grupo_atual else 0)
        if atual and usado + precisa > disponivel:
            paginas.append(atual)
            atual, usado, grupo_atual = [], 0, None
            precisa = h + CAB_H
        if g != grupo_atual:
            atual.append(("cab", g))
            usado += CAB_H
            grupo_atual = g
        atual.append(("svc", idx))
        usado += h
    if atual:
        paginas.append(atual)
    return paginas or [[]]


def pagina_valida(valor, total):
    """`p` da query: invalido = 1, acima do maximo = ultimo."""
    try:
        n = int(valor)
    except (TypeError, ValueError):
        return 1
    return min(max(n, 1), max(1, total))
