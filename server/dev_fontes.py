"""Fontes da aba Dev publicadas pelo usuario `claude`: sessoes abertas do Claude Code e resumo do GitHub (E7, E10).

O servico web roda como `nobody` e so le. Os arquivos vem de outro usuario: tamanho, tipo e texto sao dados nao
confiaveis (tamanho limitado, so arquivo regular, texto vira ASCII com tamanho maximo). Nada aqui grava.
Falha (diretorio ou arquivo ausente, JSON ruim, formato errado) vira {"erro": "n/d"}, como em `coletar_claude`.
"""
import json
import math
import re

import termos
from ecossistema import sanear

ND = {"erro": "n/d"}

# sessoes
SESSOES_VARRER_MAX = 500          # entradas olhadas no diretorio (o resto e ignorado)
SESSOES_LER_MAX = 50              # arquivos validos lidos
SESSOES_ITENS_MAX = 12            # itens devolvidos (as mais recentes)
SESSAO_BYTES_MAX = 4096
SESSAO_IDADE_MAX_S = 600          # E10 (ajuste do dono): a statusline bate a cada 30 s; mais velha que 10 min = fantasma
SESSAO_FUTURO_TOLERADO_S = 60     # atualizado_em adiantado alem disso e relogio ou arquivo ruim
SESSAO_PROJETO_TAM = 40
RE_SESSAO_ARQ = re.compile(r"^([0-9a-f-]{8,64})\.json\Z")
ESTADOS_SESSAO = ("aberta", "trabalhando", "esperando")

# github
GITHUB_BYTES_MAX = 65536
GITHUB_VELHO_S = 1200
GITHUB_PRS_MAX = 20
GITHUB_CI_MAX = 30
GITHUB_REPO_TAM = 40
GITHUB_BRANCH_TAM = 40
GITHUB_TITULO_TAM = 80
GITHUB_ISSUES_MAX = 5
GITHUB_REPOS_MAX = 6
DIAS_MAX = 9999
ESTADOS_CI = ("ok", "falha", "pendente")
ESTADOS_REVISAO = ("aprovado", "mudancas", "pendente", "nenhuma")

INTEIRO_MAX = 2 ** 53


def _inteiro_nao_neg(v):
    return isinstance(v, int) and not isinstance(v, bool) and 0 <= v < INTEIRO_MAX


def _dias(v):
    """Dias 0..9999 (int estrito, nunca bool) ou None."""
    return v if _inteiro_nao_neg(v) and v <= DIAS_MAX else None


def _proibido(*textos):
    """True se algum texto (depois de sanear) cita um termo bloqueado (`termos`): defesa em profundidade, o publicador ja filtra."""
    return any(termos.cita(sanear(t, 10000)) for t in textos if isinstance(t, str))


def _json_dict(texto, max_bytes):
    if not isinstance(texto, str) or len(texto) > max_bytes:
        raise ValueError("tamanho")
    dados = json.loads(texto)
    if not isinstance(dados, dict):
        raise ValueError("nao e objeto")
    return dados


# ---------------------------------------------------------------------------------------------- sessoes

def _sessao(nome, texto, agora):
    """Item {"projeto","estado","desde_s","_idade"} de um arquivo, ou None se invalido/velho/estado desconhecido."""
    m = RE_SESSAO_ARQ.match(nome)
    if not m:
        return None
    try:
        d = _json_dict(texto, SESSAO_BYTES_MAX)
    except ValueError:
        return None
    if d.get("versao") != 1 or d.get("id") != m.group(1) or d.get("estado") not in ESTADOS_SESSAO:
        return None
    desde, atualizado = d.get("desde"), d.get("atualizado_em")
    if not _inteiro_nao_neg(desde) or not _inteiro_nao_neg(atualizado):
        return None
    if atualizado - agora > SESSAO_FUTURO_TOLERADO_S:
        return None
    idade = max(0, int(agora - atualizado))
    if idade >= SESSAO_IDADE_MAX_S:
        return None
    return {"projeto": sanear(d.get("projeto"), SESSAO_PROJETO_TAM) or "sessao", "estado": d["estado"],
            "desde_s": max(0, int(agora - desde)), "_idade": idade}


def _entradas(listar, diretorio):
    """Ate SESSOES_VARRER_MAX entradas do diretorio; fecha o iterador (os.scandir) se der."""
    it = listar(diretorio)
    try:
        saida = []
        for entrada in it:
            saida.append(entrada)
            if len(saida) >= SESSOES_VARRER_MAX:
                break
        return saida
    finally:
        fechar = getattr(it, "close", None)
        if callable(fechar):
            fechar()


def coletar_sessoes(diretorio, listar, ler, agora):
    """Sessoes abertas do Claude Code (um JSON por sessao em `diretorio`).

    -> {"itens": [{"projeto","estado","desde_s"}] (12 mais recentes), "total", "esperando", "idade_s"}.
    `idade_s` e a do batimento mais novo (None sem sessao). Diretorio ausente ou ilegivel -> {"erro": "n/d"}.
    """
    try:
        entradas = _entradas(listar, diretorio)
    except Exception:
        return dict(ND)
    candidatas = []
    for e in entradas:
        try:
            if not RE_SESSAO_ARQ.match(e.name):
                continue
            # so a ordem e um pre-filtro de tamanho; o tipo (regular, sem link) e conferido por `ler`, ao abrir
            st = e.stat(follow_symlinks=False)
            if st.st_size <= SESSAO_BYTES_MAX:
                candidatas.append((st.st_mtime, e.name))
        except Exception:
            continue
    # as mais recentes primeiro: sessoes velhas (crash sem SessionEnd) nao podem esconder uma viva de nome maior
    candidatas.sort(key=lambda c: (-c[0], c[1]))
    sessoes = []
    for _, nome in candidatas[:SESSOES_LER_MAX]:
        try:
            s = _sessao(nome, ler(diretorio.rstrip("/") + "/" + nome), agora)
        except Exception:
            continue
        if s is not None:
            sessoes.append(s)
    sessoes.sort(key=lambda s: (s["desde_s"], s["projeto"]))
    return {"itens": [{"projeto": s["projeto"], "estado": s["estado"], "desde_s": s["desde_s"]}
                      for s in sessoes[:SESSOES_ITENS_MAX]],
            "total": len(sessoes),
            "esperando": sum(1 for s in sessoes if s["estado"] == "esperando"),
            "idade_s": min((s["_idade"] for s in sessoes), default=None)}


# ----------------------------------------------------------------------------------------------- github

def _pr(p):
    """PR do github.json. Campos novos (revisao, conflito, idade_d, atualizado_d) ausentes ou ruins viram neutros."""
    if not isinstance(p, dict) or not _inteiro_nao_neg(p.get("numero")) or _proibido(p.get("repo"), p.get("titulo")):
        return None
    ci, revisao = p.get("ci"), p.get("revisao")
    return {"repo": sanear(p.get("repo"), GITHUB_REPO_TAM), "numero": p["numero"],
            "titulo": sanear(p.get("titulo"), GITHUB_TITULO_TAM), "rascunho": p.get("rascunho") is True,
            "ci": ci if ci in ESTADOS_CI else None,
            "revisao": revisao if revisao in ESTADOS_REVISAO else "nenhuma",
            "conflito": p.get("conflito") is True,
            "idade_d": _dias(p.get("idade_d")), "atualizado_d": _dias(p.get("atualizado_d"))}


def _ci(c):
    if not isinstance(c, dict) or c.get("estado") not in ESTADOS_CI or _proibido(c.get("repo"), c.get("branch")):
        return None
    return {"repo": sanear(c.get("repo"), GITHUB_REPO_TAM), "branch": sanear(c.get("branch"), GITHUB_BRANCH_TAM),
            "estado": c["estado"]}


def _issue(i):
    if not isinstance(i, dict) or not _inteiro_nao_neg(i.get("numero")) or _proibido(i.get("repo"), i.get("titulo")):
        return None
    return {"repo": sanear(i.get("repo"), GITHUB_REPO_TAM), "numero": i["numero"],
            "titulo": sanear(i.get("titulo"), GITHUB_TITULO_TAM), "idade_d": _dias(i.get("idade_d"))}


def _repo_ativo(r):
    if not isinstance(r, dict) or _dias(r.get("push_d")) is None or _proibido(r.get("repo")):
        return None
    nome = sanear(r.get("repo"), GITHUB_REPO_TAM)
    return {"repo": nome, "push_d": r["push_d"]} if nome else None


def _lista_validada(bruta, conv, maximo):
    if not isinstance(bruta, list):
        raise ValueError("nao e lista")
    saida = []
    for x in bruta:
        v = conv(x)
        if v is not None:
            saida.append(v)
            if len(saida) >= maximo:
                break
    return saida


def _issues(bruto):
    """{"n", "itens"} (ate 5) ou None se ausente ou com forma errada; `n` nunca e menor que os itens validos."""
    if not isinstance(bruto, dict) or _dias(bruto.get("n")) is None:
        return None
    try:
        itens = _lista_validada(bruto.get("itens"), _issue, GITHUB_ISSUES_MAX)
    except ValueError:
        return None
    return {"n": max(bruto["n"], len(itens)), "itens": itens}


def _repos(bruto):
    try:
        return _lista_validada(bruto, _repo_ativo, GITHUB_REPOS_MAX)
    except ValueError:
        return []


def coletar_github(caminho, ler, agora):
    """Resumo do GitHub (github.json do claude-github).

    -> {"prs": [{"repo","numero","titulo","rascunho","ci","revisao","conflito","idade_d","atualizado_d"}] (max 20),
    "ci": [{"repo","branch","estado"}] (max 30), "issues": {"n","itens": [{"repo","numero","titulo","idade_d"}]} (max 5)
    ou None, "repos": [{"repo","push_d"}] (max 6, mais recente primeiro), "abertos", "ci_falhas", "idade_s", "velho"}.
    Os campos aditivos (revisao, conflito, idade_d, atualizado_d, issues, repos) faltam em arquivos antigos: ficam
    neutros ("nenhuma", False, None, None, []). Ausente, invalido ou com forma errada -> {"erro": "n/d"}.
    Item invalido e descartado sem derrubar o resto; item que cita um termo bloqueado tambem.
    """
    try:
        dados = _json_dict(ler(caminho), GITHUB_BYTES_MAX)
        gerado = dados.get("gerado_em")
        if dados.get("versao") != 1 or not _inteiro_nao_neg(gerado):
            return dict(ND)
        if isinstance(agora, float) and not math.isfinite(agora):
            return dict(ND)
        prs = _lista_validada(dados.get("prs"), _pr, GITHUB_PRS_MAX)
        ci = _lista_validada(dados.get("ci"), _ci, GITHUB_CI_MAX)
        idade = max(0, int(agora - gerado))
        return {"prs": prs, "ci": ci, "issues": _issues(dados.get("issues")), "repos": _repos(dados.get("repos")),
                "abertos": len(prs), "ci_falhas": sum(1 for c in ci if c["estado"] == "falha"),
                "idade_s": idade, "velho": idade > GITHUB_VELHO_S}
    except Exception:
        return dict(ND)
