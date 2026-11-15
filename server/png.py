"""Encoder PNG em tons de cinza 8-bit, so com a biblioteca padrao (struct + zlib)."""
import struct
import zlib

ASSINATURA = b"\x89PNG\r\n\x1a\n"


def _chunk(tipo, corpo):
    return (struct.pack(">I", len(corpo)) + tipo + corpo
            + struct.pack(">I", zlib.crc32(tipo + corpo) & 0xFFFFFFFF))


def gerar_png(largura, altura, pixels, nivel=6):
    """PNG 8-bit tons de cinza. `pixels`: largura*altura bytes, linha a linha (0 preto, 255 branco).

    Filtro 0 em todas as linhas: as telas tem areas chapadas, que o zlib comprime muito bem.
    """
    largura, altura = int(largura), int(altura)
    if largura <= 0 or altura <= 0:
        raise ValueError("dimensoes invalidas")
    if len(pixels) != largura * altura:
        raise ValueError("tamanho de pixels incompativel com largura x altura")
    bruto = bytearray()
    for y in range(altura):
        bruto.append(0)
        bruto += pixels[y * largura:(y + 1) * largura]
    return (ASSINATURA
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 0, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(bytes(bruto), nivel))
            + _chunk(b"IEND", b""))
