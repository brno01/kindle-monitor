import unittest

import _caminho  # noqa: F401
import botoes


def _sobrepoe(a, b, folga=0):
    return not (a["x"] + a["w"] + folga <= b["x"] or b["x"] + b["w"] + folga <= a["x"]
                or a["y"] + a["h"] + folga <= b["y"] or b["y"] + b["h"] + folga <= a["y"])


class LayoutTest(unittest.TestCase):
    TAMANHOS = ((1236, 1648), (800, 1300), (1072, 1448))

    def todos(self):
        for pagina in botoes.PAGINAS:
            for larg, alt in self.TAMANHOS:
                for armado in (None, "gpu-descarregar", "ollama-reiniciar"):
                    yield pagina, armado, larg, alt, botoes.layout(pagina, armado, larg, alt)

    def test_tamanho_minimo(self):
        for pagina, _, larg, alt, bs in self.todos():
            for b in bs:
                self.assertGreaterEqual(b["w"], 150, (pagina, b["id"]))
                self.assertGreaterEqual(b["h"], 110, (pagina, b["id"]))

    def test_dentro_da_tela_e_separados_por_16px(self):
        for pagina, _, larg, alt, bs in self.todos():
            for b in bs:
                self.assertGreaterEqual(b["x"], 0)
                self.assertGreaterEqual(b["y"], 0)
                self.assertLessEqual(b["x"] + b["w"], larg)
                self.assertLessEqual(b["y"] + b["h"], alt)
            for i, a in enumerate(bs):
                for b in bs[i + 1:]:
                    self.assertFalse(_sobrepoe(a, b, 16), (pagina, a["id"], b["id"]))

    def test_ids_unicos_e_chaves(self):
        for pagina, _, _, _, bs in self.todos():
            ids = [b["id"] for b in bs]
            self.assertEqual(len(ids), len(set(ids)))
            for b in bs:
                self.assertEqual(set(b), {"id", "rotulo", "x", "y", "w", "h", "tipo", "armado"})
                self.assertIn(b["tipo"], ("local", "comando"))

    def test_barra_de_navegacao_em_todas_as_paginas(self):
        esperado = [("atualizar", "Atualizar"), ("pagina:resumo", "Resumo"), ("pagina:detalhes", "Detalhes"),
                    ("pagina:comandos", "Comandos")]
        for pagina in botoes.PAGINAS:
            nav = [b for b in botoes.layout(pagina) if b["tipo"] == "local"]
            self.assertEqual([(b["id"], b["rotulo"]) for b in nav], esperado)
            self.assertEqual(len({b["y"] for b in nav}), 1)
            self.assertFalse(any(b["armado"] for b in nav))

    def test_so_comandos_tem_botoes_de_comando(self):
        self.assertFalse([b for b in botoes.layout("resumo") if b["tipo"] == "comando"])
        self.assertFalse([b for b in botoes.layout("detalhes", "bots-pausar") if b["tipo"] == "comando"])
        ids = [b["id"] for b in botoes.layout("comandos") if b["tipo"] == "comando"]
        self.assertEqual(ids, ["gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar",
                               "ragnarok-reiniciar", "ollama-reiniciar"])

    def test_armado_so_um_e_com_rotulo_de_confirmacao(self):
        bs = botoes.layout("comandos", "bots-pausar")
        armados = [b for b in bs if b["armado"]]
        self.assertEqual([b["id"] for b in armados], ["bots-pausar"])
        self.assertEqual(armados[0]["rotulo"], "Toque de novo para confirmar")
        self.assertEqual({b["rotulo"] for b in bs if b["id"] == "bots-retomar"}, {"Retomar bots"})

    def test_armado_invalido_ou_em_outra_pagina_e_ignorado(self):
        for pagina, armado in (("comandos", "xpto"), ("comandos", "pagina:resumo"), ("resumo", "bots-pausar"),
                               ("comandos", None)):
            self.assertFalse(any(b["armado"] for b in botoes.layout(pagina, armado)))

    def test_pagina_invalida_vira_resumo(self):
        self.assertEqual(botoes.layout("zzz"), botoes.layout("resumo"))

    def test_pura(self):
        self.assertEqual(botoes.layout("comandos", "bots-pausar"), botoes.layout("comandos", "bots-pausar"))

    def test_areas_de_comando_cabem_antes_da_navegacao(self):
        for larg, alt in self.TAMANHOS:
            g = botoes.geometria_comandos(larg, alt)
            u = g["ultimos"]
            self.assertGreaterEqual(u["h"], botoes.ULTIMOS_TITULO_H + 5 * g["linha_h"])
            self.assertLessEqual(u["y"] + u["h"], botoes.nav_topo(alt))


if __name__ == "__main__":
    unittest.main()
