import unittest

import _caminho  # noqa: F401
import botoes
import servicos


def _sobrepoe(a, b, folga=0):
    return not (a["x"] + a["w"] + folga <= b["x"] or b["x"] + b["w"] + folga <= a["x"]
                or a["y"] + a["h"] + folga <= b["y"] or b["y"] + b["h"] + folga <= a["y"])


def mk(i, grupo="host", estado="ativo", verbos=("reiniciar",), **k):
    d = {"id": "s%d" % i, "rotulo": "Servico %d" % i, "grupo": grupo, "estado": estado, "detalhe": "",
         "verbos": list(verbos), "protegido": False, "opcional": False}
    d.update(k)
    return d


def itens_cheios(n=52):
    """52 servicos: 4 grupos, estados e verbos variados (inclui itens sem verbos)."""
    grupos = ("host", "incus", "docker", "ragnarok")
    estados = ("ativo", "parado", "falha", "desconhecido", "ativo", "ativo")
    verbos = (("reiniciar", "ligar", "parar"), ("reiniciar",), (), ("ligar", "parar"))
    return servicos.ordenar([mk(i, grupos[i * 4 // n], estados[i % 6], verbos[i % 4]) for i in range(n)])


class LayoutTest(unittest.TestCase):
    TAMANHOS = ((1236, 1648), (800, 1300), (1072, 1448))

    def todos(self):
        its = itens_cheios()
        for pagina in botoes.PAGINAS:
            for larg, alt in self.TAMANHOS:
                for armado in (None, "gpu-descarregar", "svc:s0:reiniciar"):
                    for p in (1, 2, 99):
                        yield pagina, armado, larg, alt, p, botoes.layout(pagina, armado, larg, alt, p, its)

    def test_tamanho_minimo(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in bs:
                nav = b["tipo"] == "local" and b["id"].startswith("pagina:") or b["id"] == "atualizar"
                self.assertGreaterEqual(b["w"], 120 if nav and larg < 1000 else 150, (pagina, b["id"], larg))
                self.assertGreaterEqual(b["h"], 84, (pagina, b["id"]))

    def test_dentro_da_tela_e_separados_por_16px(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in bs:
                self.assertGreaterEqual(b["x"], 0)
                self.assertGreaterEqual(b["y"], 0)
                self.assertLessEqual(b["x"] + b["w"], larg)
                self.assertLessEqual(b["y"] + b["h"], alt)
            for i, a in enumerate(bs):
                for b in bs[i + 1:]:
                    self.assertFalse(_sobrepoe(a, b, 16), (pagina, p, larg, a["id"], b["id"]))

    def test_conteudo_nunca_invade_a_navegacao(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in bs:
                if b["tipo"] == "comando" or b["id"].startswith("servicos:"):
                    self.assertLessEqual(b["y"] + b["h"], botoes.nav_topo(alt) - 16, (pagina, b["id"]))

    def test_ids_unicos_e_chaves(self):
        for pagina, _, _, _, _, bs in self.todos():
            ids = [b["id"] for b in bs]
            self.assertEqual(len(ids), len(set(ids)))
            for b in bs:
                self.assertEqual(set(b), {"id", "rotulo", "x", "y", "w", "h", "tipo", "armado"})
                self.assertIn(b["tipo"], ("local", "comando"))
                self.assertRegex(b["id"], r"^[a-z0-9:-]+$")  # o que o Kindle aceita

    def test_barra_de_navegacao_em_todas_as_paginas(self):
        esperado = [("atualizar", "Atualizar"), ("pagina:resumo", "Resumo"), ("pagina:servicos", "Servicos"),
                    ("pagina:detalhes", "Detalhes"), ("pagina:comandos", "Acoes")]
        for pagina in botoes.PAGINAS:
            nav = [b for b in botoes.layout(pagina) if b["id"] in dict(esperado)]
            self.assertEqual([(b["id"], b["rotulo"]) for b in nav], esperado)
            self.assertEqual(len({b["y"] for b in nav}), 1)
            self.assertFalse(any(b["armado"] for b in nav))
            self.assertTrue(all(b["tipo"] == "local" and b["h"] == 96 for b in nav))

    def test_nav_mais_baixa_que_antes(self):
        self.assertLess(botoes.NAV_H, 130)
        self.assertEqual(botoes.nav_topo(1648), 1648 - 24 - 96)

    def test_so_comandos_e_servicos_tem_botoes_de_comando(self):
        self.assertFalse([b for b in botoes.layout("resumo", None, 1236, 1648, 1, itens_cheios()) if b["tipo"] == "comando"])
        self.assertFalse([b for b in botoes.layout("detalhes", "bots-pausar") if b["tipo"] == "comando"])
        ids = [b["id"] for b in botoes.layout("comandos") if b["tipo"] == "comando"]
        self.assertEqual(ids, ["gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar"])
        self.assertNotIn("ragnarok-reiniciar", ids)
        self.assertNotIn("ollama-reiniciar", ids)

    def test_armado_so_um_e_com_rotulo_de_confirmacao(self):
        bs = botoes.layout("comandos", "bots-pausar")
        armados = [b for b in bs if b["armado"]]
        self.assertEqual([b["id"] for b in armados], ["bots-pausar"])
        self.assertEqual(armados[0]["rotulo"], "Toque de novo para confirmar")
        self.assertEqual({b["rotulo"] for b in bs if b["id"] == "bots-retomar"}, {"Retomar bots"})

    def test_armado_invalido_ou_em_outra_pagina_e_ignorado(self):
        its = itens_cheios()
        for pagina, armado in (("comandos", "xpto"), ("comandos", "pagina:resumo"), ("resumo", "bots-pausar"),
                               ("comandos", None), ("comandos", "svc:nao-existe:parar"), ("servicos", "svc:s2:ligar"),
                               ("servicos", "svc:s0:apagar"), ("servicos", "gpu-descarregar")):
            self.assertFalse(any(b["armado"] for b in botoes.layout(pagina, armado, 1236, 1648, 1, its)), (pagina, armado))

    def test_pagina_invalida_vira_resumo(self):
        self.assertEqual(botoes.layout("zzz"), botoes.layout("resumo"))

    def test_pura(self):
        its = itens_cheios()
        self.assertEqual(botoes.layout("servicos", "svc:s0:reiniciar", 1236, 1648, 2, its),
                         botoes.layout("servicos", "svc:s0:reiniciar", 1236, 1648, 2, its))

    def test_comandos_cabem_antes_da_navegacao(self):
        for larg, alt in self.TAMANHOS:
            g = botoes.geometria_comandos(larg, alt)
            self.assertLessEqual(g["fim_botoes"], botoes.limite(alt))
            # sobra pelo menos a lista de ultimos comandos (titulo + 3 linhas)
            self.assertGreaterEqual(botoes.limite(alt) - g["fim_botoes"], botoes.ULTIMOS_TITULO_H + 3 * g["linha_h"])


class ServicosLayoutTest(unittest.TestCase):
    def test_botoes_contextuais_por_estado(self):
        its = servicos.ordenar([
            mk(0, estado="ativo", verbos=("reiniciar", "ligar", "parar")),
            mk(1, estado="parado", verbos=("reiniciar", "ligar", "parar")),
            mk(2, estado="falha", verbos=("reiniciar", "ligar", "parar")),
            mk(3, estado="desconhecido", verbos=("reiniciar", "ligar", "parar")),
            mk(4, estado="ativo", verbos=()),
            mk(5, estado="parado", verbos=("reiniciar",)),
            mk(6, estado="ativo", verbos=("ligar", "parar")),
        ])
        ids = [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"]
        self.assertEqual(ids, ["svc:s0:reiniciar", "svc:s0:parar", "svc:s1:ligar", "svc:s2:reiniciar",
                               "svc:s5:reiniciar", "svc:s6:parar"])

    def test_botoes_de_linha_150x84_com_16px_e_alinhados_a_direita(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar"))])
        bs = [b for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"]
        self.assertEqual(len(bs), 2)
        self.assertEqual({(b["w"], b["h"]) for b in bs}, {(190, 84)})
        self.assertEqual(bs[0]["x"] + bs[0]["w"] + 16, bs[1]["x"])
        self.assertEqual(bs[1]["x"] + bs[1]["w"], 1236 - botoes.MARGEM)
        self.assertEqual(bs[0]["y"], bs[1]["y"])

    def test_rotulos_dos_verbos(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar")), mk(1, estado="parado", verbos=("ligar",))])
        r = {b["id"]: b["rotulo"] for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"}
        self.assertEqual(r, {"svc:s0:reiniciar": "Reiniciar", "svc:s0:parar": "Parar", "svc:s1:ligar": "Ligar"})

    def test_armado_invertido_com_confirmar(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar"))])
        bs = botoes.layout("servicos", "svc:s0:parar", 1236, 1648, 1, its)
        arm = [b for b in bs if b["armado"]]
        self.assertEqual([(b["id"], b["rotulo"]) for b in arm], [("svc:s0:parar", "Confirmar?")])
        self.assertEqual([b["rotulo"] for b in bs if b["id"] == "svc:s0:reiniciar"], ["Reiniciar"])

    def test_paginacao_cobre_todos_os_itens_sem_repetir(self):
        its = itens_cheios()
        g1 = botoes.geometria_servicos(its, 1236, 1648, 1)
        n = g1["paginas"]
        self.assertGreater(n, 1)
        vistos = []
        for p in range(1, n + 1):
            g = botoes.geometria_servicos(its, 1236, 1648, p)
            self.assertEqual(g["p"], p)
            vistos += [e["item"]["id"] for e in g["entradas"] if e["tipo"] == "svc"]
            self.assertLessEqual(g["fim"], botoes.limite(1648))
        self.assertEqual(vistos, [i["id"] for i in its])

    def test_p_invalido_e_fora_da_faixa(self):
        its = itens_cheios()
        n = botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"]
        for p, esperado in ((None, 1), ("x", 1), (0, 1), (-4, 1), ("0", 1), (n + 5, n), ("999", n), ("2", 2), (1.0, 1)):
            self.assertEqual(botoes.geometria_servicos(its, 1236, 1648, p)["p"], esperado, p)
        self.assertEqual(botoes.layout("servicos", None, 1236, 1648, 999, its),
                         botoes.layout("servicos", None, 1236, 1648, n, its))

    def test_botoes_de_paginacao(self):
        its = itens_cheios()
        n = botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"]
        ids = lambda p: [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, p, its) if b["id"].startswith("servicos:")]
        self.assertEqual(ids(1), ["servicos:proxima"])
        self.assertEqual(ids(2), ["servicos:proxima", "servicos:anterior"])
        self.assertEqual(ids(n), ["servicos:anterior"])
        rot = {b["id"]: b["rotulo"] for b in botoes.layout("servicos", None, 1236, 1648, 2, its)}
        self.assertEqual((rot["servicos:anterior"], rot["servicos:proxima"]), ("< Anterior", "Proxima >"))
        for b in botoes.layout("servicos", None, 1236, 1648, 2, its):
            if b["id"].startswith("servicos:"):
                self.assertEqual(b["tipo"], "local")

    def test_uma_pagina_so_nao_tem_paginacao(self):
        its = servicos.ordenar([mk(i) for i in range(5)])
        g = botoes.geometria_servicos(its, 1236, 1648, 1)
        self.assertEqual((g["paginas"], g["barra"]), (1, None))
        self.assertFalse([b for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["id"].startswith("servicos:")])

    def test_catalogo_real_cabe_em_4_paginas(self):
        import json
        import os
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(raiz, "deploy", "config.atheron.json")) as f:
            cat = servicos.validar_catalogo(json.load(f)["servicos_kindle"])
        its = servicos.ordenar([dict(c, estado="ativo", detalhe="") for c in cat])
        self.assertEqual(botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"], 4)

    def test_sem_itens(self):
        g = botoes.geometria_servicos([], 1236, 1648, 3)
        self.assertEqual((g["p"], g["paginas"], g["entradas"]), (1, 1, []))

    def test_armado_valido(self):
        its = [mk(0, verbos=("reiniciar",))]
        self.assertEqual(botoes.armado_valido("svc:s0:reiniciar", its), "svc:s0:reiniciar")
        self.assertIsNone(botoes.armado_valido("svc:s0:parar", its))
        self.assertIsNone(botoes.armado_valido("svc:s1:reiniciar", its))
        self.assertIsNone(botoes.armado_valido("svc:s0:reiniciar", ()))
        self.assertEqual(botoes.armado_valido("bots-pausar"), "bots-pausar")
        self.assertIsNone(botoes.armado_valido(None))


if __name__ == "__main__":
    unittest.main()
