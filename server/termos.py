"""Termos bloqueados: palavras que nunca podem aparecer na tela nem na contagem (filtro de privacidade).

A lista vem da chave `termos_bloqueados` da config local (nao versionada). Sem a chave a lista e vazia: nada e
filtrado. Termo invalido recusa a config inteira (o filtro nunca fica ligado pela metade). As regras sao as mesmas
do executor root (`deploy/kindle-monitor-executor.py`, `validar_termos`); um teste confere a paridade.
"""
import re

RE_TERMO = re.compile(r"^[a-z0-9][a-z0-9._-]{1,39}\Z")
TERMOS_MAX = 16

_termos = ()


def validar(valor):
    """Valida `termos_bloqueados`. ValueError com a causa (nunca cita o valor); devolve tupla sem repeticao."""
    if valor is None:
        return ()
    if not isinstance(valor, list):
        raise ValueError("config: termos_bloqueados deve ser uma lista")
    if len(valor) > TERMOS_MAX:
        raise ValueError("config: termos_bloqueados: no maximo %d itens" % TERMOS_MAX)
    saida = []
    for i, t in enumerate(valor):
        if not isinstance(t, str) or not RE_TERMO.match(t):
            raise ValueError("config: termos_bloqueados[%d]: termo invalido" % i)
        if t not in saida:
            saida.append(t)
    return tuple(saida)


def definir(valor):
    """Valida e ativa a lista do processo (chamada ao carregar a config)."""
    global _termos
    _termos = validar(valor)


def obter():
    return _termos


def cita(*textos):
    """True se algum texto (str; qualquer caixa) contem um termo bloqueado."""
    if not _termos:
        return False
    return any(t in x.lower() for x in textos if isinstance(x, str) for t in _termos)
