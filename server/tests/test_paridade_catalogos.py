"""Paridade dos catalogos `aparelhos` e `rotinas` (E8) entre o executor root e o servidor web.

O executor (deploy/kindle-monitor-executor.py, roda como root) e a referencia; o servidor (ecossistema.py, usuario
`nobody`) tem de aceitar e recusar exatamente a mesma tabela. A unica divergencia intencional e o icone: o servidor
confere `icones_dados.ICONES`, o executor so o formato `^[a-z]{2,16}$` (ele nao importa nada de server/).
"""
import importlib.util
import os
import unittest

import _caminho  # noqa: F401
import ecossistema as eco
import icones_dados

_CAM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "deploy", "kindle-monitor-executor.py")
_spec = importlib.util.spec_from_file_location("executor_paridade", _CAM)
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

NAN = float("nan")
INF = float("inf")


def ap(**k):
    d = {"id": "gw", "nome": "cerberus-gw", "rotulo": "Gateway", "icone": "rede"}
    d.update(k)
    return d


def sem(d, *chaves):
    return {k: v for k, v in d.items() if k not in chaves}


def ro(**k):
    d = {"id": "senhas", "rotulo": "Backup senhas", "tipo": "timer", "alvo": "backup-senhas.service",
         "max_idade_h": 26}
    d.update(k)
    return d


def ra(**k):
    return ro(id="painel", tipo="arquivo", alvo="/var/lib/claude-uso/tokens.json", max_idade_h=1, **k)


def cheio(fab, n):
    return [fab(id="i%d" % i, **({"nome": "n%d" % i} if fab is ap else {})) for i in range(n)]


# (descricao, entrada, aceita?)
APARELHOS = [
    ("vazio", [], True),
    ("um valido", [ap()], True),
    ("com alerta", [ap(alerta_offline_min=10)], True),
    ("16 itens", cheio(ap, 16), True),
    ("17 itens", cheio(ap, 17), False),
    ("id 24", [ap(id="a" * 24)], True),
    ("id 25", [ap(id="a" * 25)], False),
    ("id vazio", [ap(id="")], False),
    ("id maiusculo", [ap(id="Gw")], False),
    ("id com underscore", [ap(id="a_b")], False),
    ("id com quebra de linha final", [ap(id="gw\n")], False),
    ("id nao texto", [ap(id=3)], False),
    ("sem id", [sem(ap(), "id")], False),
    ("nome 63", [ap(nome="a" * 63)], True),
    ("nome 64", [ap(nome="a" * 64)], False),
    ("nome maiusculo", [ap(nome="Cerberus")], False),
    ("nome com ponto", [ap(nome="a.b")], False),
    ("nome nulo", [ap(nome=None)], False),
    ("empresa-x minusculo", [ap(nome="empresa-x-x")], False),
    ("empresa-x no meio", [ap(nome="meu-empresa-x-x")], False),
    ("empresa-x maiusculo", [ap(nome="empresa-x")], False),
    ("empresa-x misto", [ap(nome="empresa-x-x")], False),
    ("rotulo 16", [ap(rotulo="a" * 16)], True),
    ("rotulo 17", [ap(rotulo="a" * 17)], False),
    ("rotulo vazio", [ap(rotulo="")], False),
    ("rotulo com acento", [ap(rotulo="Gatewayé")], False),
    ("rotulo com quebra de linha", [ap(rotulo="a\nb")], False),
    ("rotulo com NUL", [ap(rotulo="a\x00")], False),
    ("rotulo com DEL", [ap(rotulo="a\x7f")], False),
    ("rotulo com ESC", [ap(rotulo="\x1b[31mx")], False),
    ("rotulo nao texto", [ap(rotulo=5)], False),
    ("icone ausente", [sem(ap(), "icone")], False),
    ("icone nulo", [ap(icone=None)], False),
    ("icone maiusculo", [ap(icone="Rede")], False),
    ("icone com digito", [ap(icone="r1")], False),
    ("icone com hifen", [ap(icone="a-b")], False),
    ("icone curto (1)", [ap(icone="r")], False),
    ("icone longo (17)", [ap(icone="a" * 17)], False),
    ("alerta 0", [ap(alerta_offline_min=0)], False),
    ("alerta 1", [ap(alerta_offline_min=1)], True),
    ("alerta 10080", [ap(alerta_offline_min=10080)], True),
    ("alerta 10081", [ap(alerta_offline_min=10081)], False),
    ("alerta negativo", [ap(alerta_offline_min=-1)], False),
    ("alerta True", [ap(alerta_offline_min=True)], False),
    ("alerta False", [ap(alerta_offline_min=False)], False),
    ("alerta texto", [ap(alerta_offline_min="10")], False),
    ("alerta float", [ap(alerta_offline_min=5.5)], False),
    ("alerta float inteiro", [ap(alerta_offline_min=10.0)], False),
    ("alerta nulo", [ap(alerta_offline_min=None)], False),
    ("alerta NaN", [ap(alerta_offline_min=NAN)], False),
    ("chave desconhecida", [ap(extra=1)], False),
    ("chave desconhecida nula", [ap(extra=None)], False),
    ("id repetido", [ap(), ap(nome="outro")], False),
    ("nome repetido", [ap(), ap(id="outro")], False),
    ("ids e nomes distintos", [ap(), ap(id="outro", nome="outro")], True),
    ("item nao objeto", [ap(), "gw"], False),
    ("item nulo", [None], False),
    ("lista dentro da lista", [[]], False),
    ("nao e lista (dict)", {"id": "gw"}, False),
    ("nao e lista (texto)", "gw", False),
    ("nao e lista (numero)", 5, False),
    ("nulo", None, True),
]

ROTINAS = [
    ("vazio", [], True),
    ("timer valido", [ro()], True),
    ("arquivo valido", [ra()], True),
    ("16 itens", cheio(ro, 16), True),
    ("17 itens", cheio(ro, 17), False),
    ("id 24", [ro(id="a" * 24)], True),
    ("id 25", [ro(id="a" * 25)], False),
    ("id maiusculo", [ro(id="X")], False),
    ("id vazio", [ro(id="")], False),
    ("id nao texto", [ro(id=None)], False),
    ("rotulo 20", [ro(rotulo="a" * 20)], True),
    ("rotulo 21", [ro(rotulo="a" * 21)], False),
    ("rotulo vazio", [ro(rotulo="")], False),
    ("rotulo com acento", [ro(rotulo="café")], False),
    ("rotulo com quebra de linha", [ro(rotulo="a\nb")], False),
    ("rotulo com NUL", [ro(rotulo="a\x00")], False),
    ("rotulo nao texto", [ro(rotulo=5)], False),
    ("tipo desconhecido", [ro(tipo="outro")], False),
    ("tipo nulo", [ro(tipo=None)], False),
    ("tipo maiusculo", [ro(tipo="Timer")], False),
    ("timer sem .service", [ro(alvo="backup.timer")], False),
    ("timer sem sufixo", [ro(alvo="backup")], False),
    ("timer so o sufixo", [ro(alvo=".service")], False),
    ("timer com espaco", [ro(alvo="a b.service")], False),
    ("timer com quebra de linha final", [ro(alvo="a.service\n")], False),
    ("timer com @ e ponto", [ro(alvo="a@b.c-d_e.service")], True),
    ("timer com nome de 64", [ro(alvo="a" * 64 + ".service")], True),
    ("timer com nome de 65", [ro(alvo="a" * 65 + ".service")], False),
    ("timer alvo nulo", [ro(alvo=None)], False),
    ("arquivo em /srv/", [ra(), ro(id="b", tipo="arquivo", alvo="/srv/x")], True),
    ("arquivo em /var/backups/", [ro(tipo="arquivo", alvo="/var/backups/a/b")], True),
    ("arquivo relativo", [ro(tipo="arquivo", alvo="var/lib/x")], False),
    ("arquivo com ..", [ro(tipo="arquivo", alvo="/var/lib/../etc/x")], False),
    ("arquivo fora dos prefixos", [ro(tipo="arquivo", alvo="/etc/passwd")], False),
    ("arquivo prefixo parcial", [ro(tipo="arquivo", alvo="/var/libx/a")], False),
    ("arquivo so o prefixo sem barra", [ro(tipo="arquivo", alvo="/var/lib")], False),
    ("arquivo com barra dupla", [ro(tipo="arquivo", alvo="/var/lib//x")], False),
    ("arquivo com barra final", [ro(tipo="arquivo", alvo="/var/lib/x/")], False),
    ("arquivo com ponto no meio", [ro(tipo="arquivo", alvo="/var/lib/./x")], False),
    ("arquivo alvo nulo", [ro(tipo="arquivo", alvo=None)], False),
    ("arquivo alvo .service ainda e arquivo", [ro(tipo="arquivo", alvo="/srv/a.service")], True),
    ("idade 0.09", [ro(max_idade_h=0.09)], False),
    ("idade 0.1", [ro(max_idade_h=0.1)], True),
    ("idade 720", [ro(max_idade_h=720)], True),
    ("idade 720.5", [ro(max_idade_h=720.5)], False),
    ("idade 721", [ro(max_idade_h=721)], False),
    ("idade 0", [ro(max_idade_h=0)], False),
    ("idade negativa", [ro(max_idade_h=-1)], False),
    ("idade True", [ro(max_idade_h=True)], False),
    ("idade texto", [ro(max_idade_h="26")], False),
    ("idade nula", [ro(max_idade_h=None)], False),
    ("idade ausente", [sem(ro(), "max_idade_h")], False),
    ("idade NaN", [ro(max_idade_h=NAN)], False),
    ("idade inf", [ro(max_idade_h=INF)], False),
    ("chave desconhecida", [ro(extra=1)], False),
    ("chave de aparelho em rotina", [ro(nome="x")], False),
    ("id repetido", [ro(), ro(alvo="outro.service")], False),
    ("ids distintos", [ro(), ro(id="b")], True),
    ("item nao objeto", [ro(), "x"], False),
    ("item nulo", [None], False),
    ("nao e lista (dict)", {"id": "x"}, False),
    ("nao e lista (texto)", "x", False),
    ("nao e lista (numero)", 5, False),
    ("nulo", None, True),
]


def _executor(fn, entrada):
    """(aceitou, resultado) do executor: ValueError e recusa."""
    try:
        return True, fn(entrada)
    except ValueError:
        return False, None


def _servidor(fn, entrada):
    """(aceitou, resultado) do servidor: lista vazia vinda de entrada nao vazia e recusa (nunca levanta)."""
    r = fn(entrada)
    return (bool(r) or entrada is None or entrada == []), r


class ParidadeBase:
    TABELA = ()
    EXECUTOR = None
    SERVIDOR = None

    def test_tamanho_da_tabela(self):
        self.assertGreaterEqual(len(self.TABELA), 20)

    def test_executor_e_servidor_decidem_igual(self):
        divergentes = []
        for desc, entrada, esperado in self.TABELA:
            with self.subTest(caso=desc):
                ok_ex, saida_ex = _executor(self.EXECUTOR, entrada)
                ok_sv, saida_sv = _servidor(self.SERVIDOR, entrada)
                if ok_ex != ok_sv:
                    divergentes.append(desc)
                self.assertEqual(ok_ex, esperado, "executor (referencia): %s" % desc)
                self.assertEqual(ok_sv, esperado, "servidor: %s" % desc)
                if ok_ex and ok_sv:
                    self.assertEqual(saida_sv, saida_ex, "mesma normalizacao: %s" % desc)
        self.assertEqual(divergentes, [])

    def test_recusa_nunca_levanta_no_servidor(self):
        for desc, entrada, _ in self.TABELA:
            with self.subTest(caso=desc):
                self.assertIsInstance(self.SERVIDOR(entrada), list)

    def test_servidor_recusado_devolve_lista_inteira_vazia(self):
        # um item ruim descarta o catalogo inteiro, igual a recusa do executor
        for desc, entrada, esperado in self.TABELA:
            if not esperado and isinstance(entrada, list):
                with self.subTest(caso=desc):
                    self.assertEqual(self.SERVIDOR(entrada), [])


class ParidadeAparelhosTest(ParidadeBase, unittest.TestCase):
    TABELA = APARELHOS
    EXECUTOR = staticmethod(ex.validar_aparelhos)
    SERVIDOR = staticmethod(eco.validar_aparelhos)

    def test_icone_divergencia_intencional(self):
        """Icone bem formado mas inexistente: o executor aceita (so confere o formato), o servidor recusa."""
        bem_formado = "inexistente"
        self.assertRegex(bem_formado, r"^[a-z]{2,16}$")
        self.assertNotIn(bem_formado, icones_dados.ICONES)
        entrada = [ap(icone=bem_formado)]
        self.assertEqual(ex.validar_aparelhos(entrada), entrada)
        self.assertEqual(eco.validar_aparelhos(entrada), [])

    def test_icone_existente_passa_nos_dois(self):
        for nome in icones_dados.ICONES:
            with self.subTest(icone=nome):
                entrada = [ap(icone=nome)]
                self.assertEqual(ex.validar_aparelhos(entrada), entrada)
                self.assertEqual(eco.validar_aparelhos(entrada), entrada)

    def test_icone_mal_formado_recusado_nos_dois(self):
        for v in ("Rede", "r", "a" * 17, "a1", "a-b", "", None, 3):
            with self.subTest(icone=v):
                self.assertFalse(_executor(ex.validar_aparelhos, [ap(icone=v)])[0])
                self.assertEqual(eco.validar_aparelhos([ap(icone=v)]), [])

    def test_icones_do_servidor_passam_no_formato_do_executor(self):
        # senao um icone valido no servidor seria recusado pelo executor: a lista do servidor e subconjunto
        for nome in icones_dados.ICONES:
            with self.subTest(icone=nome):
                self.assertRegex(nome, r"^[a-z]{2,16}$")


class ParidadeRotinasTest(ParidadeBase, unittest.TestCase):
    TABELA = ROTINAS
    EXECUTOR = staticmethod(ex.validar_rotinas)
    SERVIDOR = staticmethod(eco.validar_rotinas)

    def test_prefixos_e_limites_iguais(self):
        self.assertEqual(tuple(ex.PREFIXOS_ARQUIVO), tuple(eco.PREFIXOS_ARQUIVO))
        self.assertEqual(ex.ROTINAS_MAX, eco.MAX_ITENS)
        self.assertEqual(ex.APARELHOS_MAX, eco.MAX_ITENS)


if __name__ == "__main__":
    unittest.main()
