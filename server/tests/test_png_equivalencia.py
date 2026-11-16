import random
import struct
import unittest
import zlib

import _caminho  # noqa: F401
import canvas
import png


def png_antigo(largura, altura, pixels, nivel=6):
    """Copia do encoder original (referencia)."""
    def chunk(tipo, corpo):
        return (struct.pack(">I", len(corpo)) + tipo + corpo + struct.pack(">I", zlib.crc32(tipo + corpo) & 0xFFFFFFFF))
    bruto = bytearray()
    for y in range(altura):
        bruto.append(0)
        bruto += pixels[y * largura:(y + 1) * largura]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(bruto), nivel)) + chunk(b"IEND", b""))


def decodificar(dados):
    pos, idat = 8, b""
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        if tipo == b"IDAT":
            idat += dados[pos + 8:pos + 8 + n]
        if tipo == b"IHDR":
            larg, alt = struct.unpack(">II", dados[pos + 8:pos + 16])
        pos += 12 + n
    return larg, alt, zlib.decompress(idat)


class EncoderTest(unittest.TestCase):
    def test_pixels_decodificados_iguais_ao_encoder_antigo(self):
        rnd = random.Random(1)
        for larg, alt in ((1, 1), (7, 5), (64, 33), (300, 20)):
            pix = bytearray(rnd.choice((0, 70, 255, rnd.randrange(256))) for _ in range(larg * alt))
            novo = decodificar(png.gerar_png(larg, alt, pix))
            velho = decodificar(png_antigo(larg, alt, pix))
            self.assertEqual(novo, velho)

    def test_nivel_padrao_e_rapido(self):
        import inspect
        self.assertLessEqual(inspect.signature(png.gerar_png).parameters["nivel"].default, 3)

    def test_aceita_bytes_e_bytearray(self):
        self.assertEqual(png.gerar_png(4, 4, bytes(16)), png.gerar_png(4, 4, bytearray(16)))


def misturar_ref(o, cor, cob):
    d = (cor - o) * cob
    return o + ((d + 127) // 255 if d >= 0 else -((127 - d) // 255))


class GlifoEquivalenciaTest(unittest.TestCase):
    """O blit de glifos acelerado tem de dar exatamente os mesmos pixels do laco por pixel."""

    def referencia(self, pix, W, gx, gy, g, cor):
        pix = bytearray(pix)
        w, h, bmp = g["w"], g["h"], g["bitmap"]
        for yy in range(h):
            for xx in range(w):
                cob = bmp[yy * w + xx]
                i = (gy + yy) * W + gx + xx
                if cob == 255:
                    pix[i] = cor
                elif cob:
                    pix[i] = misturar_ref(pix[i], cor, cob)
        return pix

    def test_fundo_uniforme_e_irregular(self):
        rnd = random.Random(7)
        nome = next(iter(__import__("fonte_dados").FONTES))
        tam = next(iter(__import__("fonte_dados").FONTES[nome]))
        f = canvas.carregar_fonte(nome, tam)
        for fundo in ("uniforme", "ruido"):
            for cor in (0, 70, 255):
                c = canvas.Canvas(200, 60, fundo=235)
                if fundo == "ruido":
                    for i in range(len(c.pixels)):
                        c.pixels[i] = rnd.randrange(256)
                inicial = bytes(c.pixels)
                esperado = bytearray(inicial)
                x = 5
                for ch in "Hg8%":
                    g = canvas._glifo(f, ch)
                    if g["w"]:
                        gx, gy = int(round(float(x) + g["xoff"])), int(30 + g["yoff"])
                        esperado = self.referencia(esperado, 200, gx, gy, g, cor)
                    x += g["avanco"]
                c.texto(5, 30, "Hg8%", nome, tam, cor)
                self.assertEqual(bytes(c.pixels), bytes(esperado), (fundo, cor))

    def test_recorte_nas_bordas(self):
        nome = next(iter(__import__("fonte_dados").FONTES))
        tam = next(iter(__import__("fonte_dados").FONTES[nome]))
        c = canvas.Canvas(30, 30)
        c.texto(-5, 10, "HHHH", nome, tam, 0)   # sai pela esquerda
        c.texto(20, 40, "HHHH", nome, tam, 0)   # sai por baixo/direita
        self.assertEqual(len(c.pixels), 900)


class CanvasAntigo(canvas.Canvas):
    """Canvas com o retangulo arredondado original (pixel a pixel), como referencia."""

    def retangulo_arredondado(self, x, y, w, h, raio, cor):
        x, y, w, h = int(x), int(y), int(w), int(h)
        r = max(0, min(int(raio), w // 2, h // 2))
        x0, y0, x1, y1 = self._caixa(x, y, x + w, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            ci = yy + 0.5
            cy = y + r if ci < y + r else y + h - r if ci > y + h - r else None
            if cy is None or r == 0:
                self.retangulo(x0, yy, x1 - x0, 1, cor)
                continue
            dy = ci - cy
            esq_fim, dir_ini = x + r, x + w - r
            self.retangulo(max(x0, esq_fim), yy, max(0, min(x1, dir_ini) - max(x0, esq_fim)), 1, cor)
            for xx in list(range(x0, min(x1, esq_fim))) + list(range(max(x0, dir_ini), x1)):
                cx = esq_fim if xx < esq_fim else dir_ini
                cob = canvas._clamp01(r + 0.5 - __import__("math").hypot(xx + 0.5 - cx, dy))
                self._misturar(yy * self.largura + xx, cor, int(cob * 255 + 0.5))


class RetanguloArredondadoTest(unittest.TestCase):
    def test_igual_ao_original_com_recorte_e_fundo_irregular(self):
        rnd = random.Random(3)
        for w, h, r in ((40, 30, 8), (100, 50, 12), (20, 20, 0), (30, 60, 40), (7, 5, 3)):
            for ruido in (False, True):
                novo, velho = canvas.Canvas(160, 120), CanvasAntigo(160, 120)
                if ruido:
                    base = bytes(rnd.randrange(256) for _ in range(160 * 120))
                    novo.pixels[:] = base
                    velho.pixels[:] = base
                for x, y in ((10, 10), (-5, -4), (130, 100), (60, 40)):
                    novo.retangulo_arredondado(x, y, w, h, r, 70)
                    velho.retangulo_arredondado(x, y, w, h, r, 70)
                self.assertEqual(bytes(novo.pixels), bytes(velho.pixels), (w, h, r, ruido))


if __name__ == "__main__":
    unittest.main()
