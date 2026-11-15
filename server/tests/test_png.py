import struct
import unittest
import zlib

import _caminho  # noqa: F401
import png

ASSINATURA = b"\x89PNG\r\n\x1a\n"


def chunks(dados):
    assert dados[:8] == ASSINATURA
    pos, saida = 8, []
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8:pos + 8 + n]
        crc = struct.unpack(">I", dados[pos + 8 + n:pos + 12 + n])[0]
        saida.append((tipo, corpo, crc))
        pos += 12 + n
    return saida


class PngTest(unittest.TestCase):
    def test_assinatura_ihdr_e_fim(self):
        dados = png.gerar_png(7, 5, bytearray(range(35)))
        self.assertEqual(dados[:8], ASSINATURA)
        cs = chunks(dados)
        self.assertEqual([c[0] for c in cs][0], b"IHDR")
        self.assertEqual(cs[-1][0], b"IEND")
        larg, alt, prof, cor, comp, filt, ent = struct.unpack(">IIBBBBB", cs[0][1])
        self.assertEqual((larg, alt, prof, cor, comp, filt, ent), (7, 5, 8, 0, 0, 0, 0))

    def test_crc_de_todos_os_chunks(self):
        for tipo, corpo, crc in chunks(png.gerar_png(10, 10, bytearray(100))):
            self.assertEqual(crc, zlib.crc32(tipo + corpo) & 0xFFFFFFFF, tipo)

    def test_idat_descomprime_com_tamanho_esperado(self):
        larg, alt = 13, 9
        pix = bytearray((i * 7) % 256 for i in range(larg * alt))
        idat = b"".join(c[1] for c in chunks(png.gerar_png(larg, alt, pix)) if c[0] == b"IDAT")
        bruto = zlib.decompress(idat)
        self.assertEqual(len(bruto), alt * (larg + 1))

    def test_roundtrip_dos_pixels(self):
        larg, alt = 13, 9
        pix = bytearray((i * 7) % 256 for i in range(larg * alt))
        idat = b"".join(c[1] for c in chunks(png.gerar_png(larg, alt, pix)) if c[0] == b"IDAT")
        bruto = zlib.decompress(idat)
        recon = bytearray()
        for y in range(alt):
            linha = bruto[y * (larg + 1):(y + 1) * (larg + 1)]
            filtro, resto = linha[0], linha[1:]
            self.assertIn(filtro, (0, 1))
            if filtro == 1:
                resto = bytearray(resto)
                for i in range(1, larg):
                    resto[i] = (resto[i] + resto[i - 1]) & 255
            recon += resto
        self.assertEqual(bytes(recon), bytes(pix))

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            png.gerar_png(4, 4, bytearray(15))
        with self.assertRaises(ValueError):
            png.gerar_png(0, 4, bytearray(0))

    def test_area_chapada_comprime_bem(self):
        dados = png.gerar_png(1236, 1648, bytearray(b"\xff" * (1236 * 1648)))
        self.assertLess(len(dados), 20000)


if __name__ == "__main__":
    unittest.main()
