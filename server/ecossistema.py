"""Aparelhos e rotinas (lado web): validacao do catalogo e montagem a partir do JSON do executor root.

Puro, sem I/O. O servico web roda como `nobody` e so le JSON; todo texto que vem do arquivo e dado nao
confiavel (vira ASCII com tamanho maximo). As regras de `validar_aparelhos` e `validar_rotinas` repetem as do
executor (deploy/kindle-monitor-executor.py), que e a referencia (roda como root): chave desconhecida e `id` ou
`nome` repetido tambem descartam a lista; a unica diferenca intencional e o icone (aqui confere `icones_dados.ICONES`).
`tests/test_paridade_catalogos.py` confere a paridade. Nada aqui levanta com entrada ruim.
"""
import json
import os
import re
import unicodedata

import icones_dados

INVENTARIO_VALIDADE_S = 60
FUTURO_TOLERADO_S = 5
APARELHOS_ARQ = "aparelhos.json"
ROTINAS_ARQ = "rotinas.json"

MAX_ITENS = 16
CHAVES_APARELHO = frozenset(("id", "nome", "rotulo", "icone", "alerta_offline_min"))
CHAVES_ROTINA = frozenset(("id", "rotulo", "tipo", "alvo", "max_idade_h"))
RE_ID = re.compile(r"^[a-z0-9-]{1,24}\Z")
RE_NOME = re.compile(r"^[a-z0-9-]{1,63}\Z")
RE_ROTULO_APARELHO = re.compile(r"^[\x20-\x7e]{1,16}\Z")
RE_ROTULO_ROTINA = re.compile(r"^[\x20-\x7e]{1,20}\Z")
RE_ALVO_TIMER = re.compile(r"^[A-Za-z0-9_.@-]{1,64}\.service\Z")
PREFIXOS_ARQUIVO = ("/srv/", "/var/lib/", "/var/backups/")
NEGADOS_ARQUIVO = ("/var/lib/claude-uso",)  # igual ao executor (paridade)
CONEXOES = ("direto", "relay")
RESULTADOS = ("ok", "falha", "desconhecido")
NOMES_FALHAS_MAX = 5
NOME_FALHA_TAM = 40


def _inteiro(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def sanear(v, tam):
    """Texto nao confiavel -> ASCII imprimivel (NFKD, sem combinantes nem controles), ate `tam` caracteres."""
    if not isinstance(v, str):
        return ""
    s = unicodedata.normalize("NFKD", v[:tam * 4])
    s = "".join(c for c in s if not unicodedata.combining(c) and unicodedata.category(c)[0] != "C")
    return s.encode("ascii", "ignore").decode("ascii").strip()[:tam]


# ------------------------------------------------------------------- validacao (E8)

def _aparelho(it):
    if not isinstance(it, dict) or set(it) - CHAVES_APARELHO:
        return None
    i, nome, rotulo, icone = it.get("id"), it.get("nome"), it.get("rotulo"), it.get("icone")
    if not isinstance(i, str) or not RE_ID.match(i):
        return None
    if not isinstance(nome, str) or not RE_NOME.match(nome) or "empresa-x" in nome:
        return None
    if not isinstance(rotulo, str) or not RE_ROTULO_APARELHO.match(rotulo):
        return None
    if not isinstance(icone, str) or icone not in icones_dados.ICONES:
        return None
    r = {"id": i, "nome": nome, "rotulo": rotulo, "icone": icone}
    if "alerta_offline_min" in it:
        a = it["alerta_offline_min"]
        if not _inteiro(a) or not 1 <= a <= 10080:
            return None
        r["alerta_offline_min"] = a
    return r


def validar_aparelhos(lista):
    """Lista de aparelhos normalizada; qualquer erro (ou mais de 16) devolve []. Nunca levanta."""
    try:
        if not isinstance(lista, list) or len(lista) > MAX_ITENS:
            return []
        saida = [_aparelho(it) for it in lista]
        if any(x is None for x in saida):
            return []
        if len({x["id"] for x in saida}) != len(saida) or len({x["nome"] for x in saida}) != len(saida):
            return []  # id ou nome repetido
        return saida
    except Exception:
        return []


def _rotina(it):
    if not isinstance(it, dict) or set(it) - CHAVES_ROTINA:
        return None
    i, rotulo, tipo, alvo, idade = (it.get("id"), it.get("rotulo"), it.get("tipo"), it.get("alvo"),
                                    it.get("max_idade_h"))
    if not isinstance(i, str) or not RE_ID.match(i):
        return None
    if not isinstance(rotulo, str) or not RE_ROTULO_ROTINA.match(rotulo):
        return None
    if tipo == "timer":
        if not isinstance(alvo, str) or not RE_ALVO_TIMER.match(alvo):
            return None
    elif tipo == "arquivo":
        if (not isinstance(alvo, str) or not os.path.isabs(alvo) or os.path.normpath(alvo) != alvo
                or not alvo.startswith(PREFIXOS_ARQUIVO)
                or any(alvo == n or alvo.startswith(n + "/") for n in NEGADOS_ARQUIVO)):
            return None
    else:
        return None
    if not _numero(idade) or not 0.1 <= idade <= 720:
        return None
    return {"id": i, "rotulo": rotulo, "tipo": tipo, "alvo": alvo, "max_idade_h": idade}


def validar_rotinas(lista):
    """Lista de rotinas normalizada; qualquer erro (ou mais de 16) devolve []. Nunca levanta."""
    try:
        if not isinstance(lista, list) or len(lista) > MAX_ITENS:
            return []
        saida = [_rotina(it) for it in lista]
        if any(x is None for x in saida):
            return []
        if len({x["id"] for x in saida}) != len(saida):
            return []  # id repetido
        return saida
    except Exception:
        return []


# ------------------------------------------------------------------------ montagem

def _ler_inventario(texto, chave, agora):
    """(situacao, idade_s, dados, adiantado). `texto` None = ausente; velho/futuro/ruim nunca vira dado.

    `adiantado` e True quando o `gerado` esta no futuro alem da tolerancia (relogio do executor adiantado); a idade
    e entao a diferenca absoluta, nao um "0" que pareceria recente."""
    if texto is None:
        return "ausente", None, {}, False
    try:
        d = json.loads(texto)
        gerado, dados = d["gerado"], d[chave]
        if not _numero(gerado) or not isinstance(dados, dict):
            raise ValueError("formato")
        idade = agora - gerado
        if -FUTURO_TOLERADO_S <= idade <= INVENTARIO_VALIDADE_S:
            return "ok", max(0, int(idade)), d, False
        if idade < 0:
            return "velho", int(-idade), {}, True
        return "velho", max(0, int(idade)), {}, False
    except Exception:
        return "ausente", None, {}, False


def _epoch(v):
    return int(v) if _numero(v) and v >= 0 else None


def _com_erro(d):
    """O executor grava `erro` (texto curto) quando a coleta falhou: o inventario nao vale como dado."""
    e = d.get("erro") if isinstance(d, dict) else None
    return isinstance(e, str) and bool(e.strip())


def montar_aparelhos(catalogo, texto, agora, primeiro_offline=None):
    """Catalogo + aparelhos.json -> {"inventario", "idade_s", "itens"}. Nunca levanta.

    `erro` nao vazio no arquivo (tailscale falhou) conta como inventario "ausente". `primeiro_offline` e um
    dicionario opcional `{id: instante}` do chamador (o Coletor o guarda em memoria): um aparelho offline sem
    `visto_em` e com `alerta_offline_min` conta os minutos desde a primeira vez que foi visto offline aqui. Esse
    dicionario e o unico efeito colateral: ganha o id ao ver o aparelho offline sem `visto_em` e perde ao ve-lo
    online; inventario sem dado nao mexe nele."""
    try:
        situacao, idade, d, adiantado = _ler_inventario(texto, "aparelhos", agora)
        if situacao == "ok" and _com_erro(d):
            situacao, idade, d = "ausente", None, {}
        inv = d.get("aparelhos") if situacao == "ok" else {}
        itens = []
        for c in catalogo:
            e = inv.get(c["id"])
            e = e if isinstance(e, dict) else {}
            online = e.get("online") if isinstance(e.get("online"), bool) else None
            visto = _epoch(e.get("visto_em"))
            offline = max(0, int((agora - visto) // 60)) if online is False and visto is not None else None
            if primeiro_offline is not None:
                if online is True or (online is False and visto is not None):
                    primeiro_offline.pop(c["id"], None)
                elif online is False and c.get("alerta_offline_min") is not None:
                    desde = primeiro_offline.setdefault(c["id"], agora)
                    offline = max(0, int((agora - desde) // 60))
            conexao = e.get("conexao") if e.get("conexao") in CONEXOES else None
            itens.append({"id": c["id"], "rotulo": sanear(c["rotulo"], 16), "icone": c["icone"],
                          "online": online, "offline_min": offline, "conexao": conexao,
                          "alerta_offline_min": c.get("alerta_offline_min")})
        r = {"inventario": situacao, "idade_s": idade, "itens": itens}
        if adiantado:
            r["relogio_adiantado"] = True
        return r
    except Exception:
        return {"inventario": "ausente", "idade_s": None, "itens": []}


def _unidades_falhas(d):
    u = d.get("unidades_falhas")
    if not isinstance(u, dict):
        return {"n": 0, "nomes": []}
    n = u.get("n")
    n = min(max(n, 0), 9999) if _inteiro(n) else 0
    nomes = u.get("nomes")
    nomes = [x for x in nomes if isinstance(x, str)] if isinstance(nomes, list) else []
    # defesa em profundidade: nome da empresa-x nunca vai para a tela e sai da contagem
    # (testa o original e o saneado: controles no meio do nome nao escondem a palavra)
    seguros = [x for x in nomes if "empresa-x" not in x.lower() and "empresa-x" not in sanear(x, 400).lower()]
    n = max(0, n - (len(nomes) - len(seguros)))
    seguros = [sanear(x, NOME_FALHA_TAM) for x in seguros]
    return {"n": n, "nomes": [x for x in seguros if x][:NOMES_FALHAS_MAX]}


def montar_rotinas(catalogo, texto, agora):
    """Catalogo + rotinas.json -> {"inventario", "idade_s", "itens", "unidades_falhas"}. Nunca levanta."""
    try:
        situacao, idade, d, adiantado = _ler_inventario(texto, "rotinas", agora)
        inv = d.get("rotinas") if situacao == "ok" else {}
        itens = []
        for c in catalogo:
            e = inv.get(c["id"])
            e = e if isinstance(e, dict) else {}
            resultado = e.get("resultado") if e.get("resultado") in RESULTADOS else "desconhecido"
            ultima = _epoch(e.get("ultima_em"))
            idade_h = round(max(0.0, (agora - ultima) / 3600), 1) if ultima is not None else None
            itens.append({"id": c["id"], "rotulo": sanear(c["rotulo"], 20), "resultado": resultado,
                          "ultima_em": ultima, "idade_h": idade_h, "max_idade_h": c["max_idade_h"],
                          "atrasada": idade_h is not None and idade_h > c["max_idade_h"],
                          "tipo": c.get("tipo"), "alvo": c.get("alvo") if c.get("tipo") == "timer" else None})
        falhas = _unidades_falhas(d) if situacao == "ok" else {"n": 0, "nomes": []}
        r = {"inventario": situacao, "idade_s": idade, "itens": itens, "unidades_falhas": falhas}
        if adiantado:
            r["relogio_adiantado"] = True
        return r
    except Exception:
        return {"inventario": "ausente", "idade_s": None, "itens": [],
                "unidades_falhas": {"n": 0, "nomes": []}}
