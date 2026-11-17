#!/usr/bin/env python3
"""Gera server/icones_dados.py: icone do Claude pre-rasterizado (cobertura 8-bit) para o renderizador PNG.

Ferramenta de DESENVOLVIMENTO (usa Pillow + svgelements). O servidor so le o arquivo gerado. Uso:

    uv run --no-project --with pillow --with svgelements python tools/gerar_icones.py

O SVG (tools/claude.svg) e tratado como dado nao confiavel: so o atributo `d` do <path> (e `fill-rule`)
e lido, via regex; nada e executado.
"""
import base64
import os
import re
import sys
import zlib

from PIL import Image, ImageDraw
from svgelements import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(RAIZ, "tools", "claude.svg")
SAIDA = os.path.join(RAIZ, "server", "icones_dados.py")
TAMANHOS = (40, 30)
SUPER = 8
FOLGA = 0.92  # desenho ocupa 92% da caixa (margem para nao encostar na borda)

CABECALHO = '''\
"""Icones pre-rasterizados (GERADO por tools/gerar_icones.py: nao edite a mao).

Origem: Simple Icons 16.38.0, icons/claude.svg (arquivo SVG CC0).
Claude e uma marca da Anthropic: uso privado, em dashboard nao publico.

Formato: ICONES[nome][tamanho_px] = {"w": int, "h": int, "dados": (<base64 de zlib de w*h bytes de cobertura 0-255>)}
"""
'''


def ler_svg(caminho):
    txt = open(caminho, encoding="utf-8").read()
    d = re.search(r'<path\b[^>]*?\sd="([^"]+)"', txt)
    if not d:
        sys.exit("path sem atributo d em %s" % caminho)
    regra = re.search(r'<path\b[^>]*?\sfill-rule="(evenodd|nonzero)"', txt)
    return d.group(1), regra.group(1) if regra else "nonzero"


def poligonos(d):
    """Subpaths do path como listas de pontos (curvas achatadas)."""
    p = Path(d)
    polis, atual = [], []
    for seg in p.segments():
        nome = type(seg).__name__
        if nome == "Move":
            if len(atual) > 2:
                polis.append(atual)
            atual = [(seg.end.x, seg.end.y)]
        elif nome == "Close":
            if len(atual) > 2:
                polis.append(atual)
            atual = []
        else:
            n = 1 if nome == "Line" else 16
            for i in range(1, n + 1):
                pt = seg.point(i / n)
                atual.append((pt.x, pt.y))
    if len(atual) > 2:
        polis.append(atual)
    return polis


def preencher(polis, regra, lado):
    """Mascara lado x lado (0/255) com a regra de preenchimento, desenhada em Pillow."""
    if regra == "evenodd":
        acc = bytearray(lado * lado)
        for pol in polis:  # XOR de cada subpath = even-odd
            t = Image.new("L", (lado, lado), 0)
            ImageDraw.Draw(t).polygon(pol, fill=255)
            acc = bytearray(a ^ b for a, b in zip(acc, t.tobytes()))
        return Image.frombytes("L", (lado, lado), bytes(acc))
    # nonzero: subpaths do Simple Icons nao se sobrepoem com sentido oposto aqui; une todos e
    # remove os de orientacao oposta contida (furos) pelo sinal da area
    m = Image.new("L", (lado, lado), 0)
    dr = ImageDraw.Draw(m)
    # separa externos e furos pelo sinal da area, em relacao ao maior
    def area(pol):
        return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pol, pol[1:] + pol[:1])) / 2.0
    ref = max(polis, key=lambda q: abs(area(q)))
    sinal = area(ref) > 0
    for pol in polis:
        if (area(pol) > 0) == sinal:
            dr.polygon(pol, fill=255)
    for pol in polis:
        if (area(pol) > 0) != sinal:
            dr.polygon(pol, fill=0)
    return m


def rasterizar(polis, regra, tam):
    lado = tam * SUPER
    xs = [x for p in polis for x, _ in p]
    ys = [y for p in polis for _, y in p]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    esc = lado * FOLGA / max(x1 - x0, y1 - y0)
    ox = (lado - (x1 - x0) * esc) / 2.0 - x0 * esc
    oy = (lado - (y1 - y0) * esc) / 2.0 - y0 * esc
    pts = [[(x * esc + ox, y * esc + oy) for x, y in pol] for pol in polis]
    mascara = preencher(pts, regra, lado)
    return mascara.resize((tam, tam), Image.BOX).tobytes()  # media por caixa = cobertura 0-255


def main():
    d, regra = ler_svg(SVG)
    polis = poligonos(d)
    partes = [CABECALHO, "ICONES = {\n    \"claude\": {\n"]
    for tam in TAMANHOS:
        bmp = rasterizar(polis, regra, tam)
        b64 = base64.b64encode(zlib.compress(bmp, 9)).decode("ascii")
        partes.append("        %d: {\n            \"w\": %d,\n            \"h\": %d,\n            \"dados\": (\n" % (tam, tam, tam))
        for i in range(0, len(b64), 100):
            partes.append("                %r\n" % b64[i:i + 100])
        partes.append("            ),\n        },\n")
    partes.append("    },\n}\n")
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("".join(partes))
    print("%s: %d subpaths, regra %s" % (SAIDA, len(polis), regra), file=sys.stderr)


if __name__ == "__main__":
    main()
