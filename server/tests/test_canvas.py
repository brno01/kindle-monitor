import unittest

import _caminho  # noqa: F401
import canvas as cv
import fonte_dados
import icones_dados


def px(c, x, y):
    return c.pixels[y * c.largura + x]


class FonteTest(unittest.TestCase):
    def test_dados_completos(self):
        esperado = {"sans-bold": (26, 34, 48, 72, 140), "sans": (26, 34), "mono": (26, 34)}
        for nome, tams in esperado.items():
            for t in tams:
                f = fonte_dados.FONTES[nome][t]
                for cod in list(range(32, 127)) + [0xB0, 0xB7]:
                    self.assertIn(cod, f["glifos"], (nome, t, cod))

    def test_tamanho_do_arquivo(self):
        import os
        self.assertLess(os.path.getsize(os.path.join(_caminho.RAIZ, "fonte_dados.py")), 400 * 1024)

    def test_bitmaps_decodificam_com_tamanho_certo(self):
        for nome, por_tam in fonte_dados.FONTES.items():
            for t in por_tam:
                f = cv.carregar_fonte(nome, t)
                for cod, g in f["glifos"].items():
                    self.assertEqual(len(g["bitmap"]), g["w"] * g["h"], (nome, t, cod))
                    self.assertGreater(g["avanco"], 0)

    def test_mono_tem_avanco_constante(self):
        f = cv.carregar_fonte("mono", 26)
        self.assertEqual(len({round(g["avanco"], 2) for g in f["glifos"].values()}), 1)


class CanvasTest(unittest.TestCase):
    def test_fundo_e_dimensoes(self):
        c = cv.Canvas(20, 10)
        self.assertEqual(len(c.pixels), 200)
        self.assertEqual(set(c.pixels), {255})
        self.assertEqual(len(cv.Canvas(20, 10, fundo=0).pixels), 200)

    def test_retangulo(self):
        c = cv.Canvas(20, 10)
        c.retangulo(2, 3, 5, 4, 0)
        self.assertEqual(px(c, 2, 3), 0)
        self.assertEqual(px(c, 6, 6), 0)
        self.assertEqual(px(c, 7, 6), 255)
        self.assertEqual(px(c, 1, 3), 255)
        self.assertEqual(px(c, 2, 7), 255)

    def test_contorno(self):
        c = cv.Canvas(20, 20)
        c.contorno(2, 2, 10, 10, 0, espessura=2)
        self.assertEqual(px(c, 2, 2), 0)
        self.assertEqual(px(c, 3, 5), 0)
        self.assertEqual(px(c, 6, 6), 255)
        self.assertEqual(px(c, 11, 11), 0)

    def test_linha_horizontal_e_diagonal(self):
        c = cv.Canvas(20, 20)
        c.linha(2, 5, 15, 5, 0, 1)
        self.assertEqual(px(c, 8, 5), 0)
        c2 = cv.Canvas(20, 20)
        c2.linha(0, 0, 19, 19, 0, 2)
        self.assertLess(px(c2, 10, 10), 128)

    def test_circulo(self):
        c = cv.Canvas(30, 30)
        c.circulo(15, 15, 8, 0)
        self.assertEqual(px(c, 15, 15), 0)
        self.assertEqual(px(c, 15, 9), 0)
        self.assertEqual(px(c, 0, 0), 255)
        self.assertEqual(px(c, 15, 28), 255)

    def test_retangulo_arredondado_corta_o_canto(self):
        c = cv.Canvas(40, 30)
        c.retangulo_arredondado(5, 5, 30, 20, 8, 0)
        self.assertEqual(px(c, 5, 5), 255)  # canto cortado
        self.assertEqual(px(c, 20, 5), 0)
        self.assertEqual(px(c, 5, 15), 0)
        self.assertEqual(px(c, 34, 24), 255)

    def test_polilinha(self):
        c = cv.Canvas(40, 20)
        c.polilinha([(2, 15), (20, 5), (37, 15)], 0, 2)
        self.assertLess(px(c, 20, 5), 128)
        self.assertEqual(px(c, 20, 18), 255)

    def test_texto_desenha_e_mede(self):
        c = cv.Canvas(200, 60)
        w = c.medir("Hello", "sans-bold", 34)
        self.assertGreater(w, 60)
        self.assertLess(w, 130)
        c.texto(10, 40, "Hello", "sans-bold", 34, 0)
        self.assertLess(min(c.pixels), 30)
        self.assertEqual(px(c, 0, 0), 255)

    def test_alinhamento(self):
        for alinhar in ("esq", "dir", "centro"):
            c = cv.Canvas(300, 60)
            c.texto(150, 40, "AB", "sans-bold", 34, 0, alinhar=alinhar)
            xs = [x for x in range(300) if any(px(c, x, y) < 128 for y in range(60))]
            esperado_w = c.medir("AB", "sans-bold", 34)
            if alinhar == "esq":
                self.assertAlmostEqual(min(xs), 150, delta=4)
            elif alinhar == "dir":
                self.assertAlmostEqual(max(xs), 150, delta=4)
            else:
                self.assertAlmostEqual((min(xs) + max(xs)) / 2, 150, delta=4)
            self.assertGreater(esperado_w, 20)

    def test_caractere_desconhecido_vira_interrogacao(self):
        c = cv.Canvas(100, 60)
        self.assertEqual(c.medir("ç", "sans", 26), c.medir("?", "sans", 26))

    def test_cinza_antialias_mistura(self):
        c = cv.Canvas(100, 60)
        c.texto(5, 40, "o", "sans-bold", 34, 0)
        self.assertTrue(any(0 < v < 255 for v in c.pixels))

    def test_altura_capital(self):
        self.assertGreater(cv.altura_capital("sans-bold", 72), cv.altura_capital("sans-bold", 34))

    def test_estrito_detecta_fora_dos_limites(self):
        c = cv.Canvas(50, 50, estrito=True)
        for fn in (
            lambda: c.retangulo(40, 40, 20, 5, 0),
            lambda: c.texto(40, 20, "wwwwww", "sans-bold", 34, 0),
            lambda: c.texto(5, 60, "a", "sans", 26, 0),
            lambda: c.circulo(2, 2, 5, 0),
            lambda: c.linha(-3, 0, 10, 10, 0, 1),
        ):
            with self.assertRaises(cv.ForaDosLimites):
                fn()

    def test_estrito_aceita_dentro(self):
        c = cv.Canvas(100, 60, estrito=True)
        c.retangulo(0, 0, 100, 60, 200)
        c.texto(5, 40, "ok", "sans", 26, 0)
        c.circulo(50, 30, 8, 0)

    def test_nao_estrito_recorta_sem_erro(self):
        c = cv.Canvas(50, 50)
        c.retangulo(40, 40, 30, 30, 0)
        c.texto(40, 20, "wwwwww", "sans-bold", 34, 0)
        self.assertEqual(len(c.pixels), 2500)

    def test_png(self):
        dados = cv.Canvas(30, 20).para_png()
        self.assertEqual(dados[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()


class IconeTest(unittest.TestCase):
    def test_icones_dados_tamanhos(self):
        for tam in (40, 30):
            d = icones_dados.ICONES["claude"][tam]
            blob = cv.carregar_icone("claude", tam)
            self.assertEqual(len(blob["bitmap"]), d["w"] * d["h"])
            self.assertEqual((d["w"], d["h"]), (tam, tam))

    def test_icone_desenha_dentro_da_caixa(self):
        c = cv.Canvas(80, 80)
        self.assertEqual(c.icone(10, 12, "claude", 40, 0), 40)
        escuros = [(i % 80, i // 80) for i, v in enumerate(c.pixels) if v < 128]
        self.assertTrue(escuros)
        for x, y in escuros:
            self.assertTrue(10 <= x < 50 and 12 <= y < 52, (x, y))

    def test_icone_inexistente_nao_desenha(self):
        c = cv.Canvas(60, 60)
        self.assertEqual(c.icone(5, 5, "nao-existe", 40, 0), 0)
        self.assertEqual(c.icone(5, 5, "claude", 41, 0), 0)
        self.assertEqual(set(c.pixels), {255})
