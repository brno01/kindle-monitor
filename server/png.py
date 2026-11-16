"""Encoder PNG em tons de cinza 8-bit, so com a biblioteca padrao (struct + zlib)."""
import struct
import zlib

ASSINATURA = b"\x89PNG\r\n\x1a\n"


def _chunk(tipo, corpo):
    return (struct.pack(">I", len(corpo)) + tipo + corpo
            + struct.pack(">I", zlib.crc32(tipo + corpo) & 0xFFFFFFFF))


def gerar_png(largura, altura, pixels, nivel=1):
    """PNG 8-bit tons de cinza. `pixels`: largura*altura bytes, linha a linha (0 preto, 255 branco).

    Filtro 0 em todas as linhas: as telas tem areas chapadas, que o zlib comprime muito bem.
    Nivel 1 do zlib: ~6x mais rapido que o 6 e so ~14 % maior nestas telas (importa em CPU lenta).
    """
    largura, altura = int(largura), int(altura)
    if largura <= 0 or altura <= 0:
        raise ValueError("dimensoes invalidas")
    if len(pixels) != largura * altura:
        raise ValueError("tamanho de pixels incompativel com largura x altura")
    # Linhas com o byte de filtro (0) na frente: atribuicao por fatia, sem copiar linha a linha.
    passo = largura + 1
    bruto = bytearray(passo * altura)
    vista = memoryview(pixels)
    for y in range(altura):
        bruto[y * passo + 1:(y + 1) * passo] = vista[y * largura:(y + 1) * largura]
    return (ASSINATURA
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 0, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(bytes(bruto), nivel))
            + _chunk(b"IEND", b""))
