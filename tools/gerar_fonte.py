#!/usr/bin/env python3
"""Gera server/fonte_dados.py: glifos DejaVu pre-rasterizados para o renderizador PNG.

Ferramenta de DESENVOLVIMENTO (usa Pillow). O servidor em producao nao precisa de Pillow:
so le o arquivo gerado. Uso:

    uv run --with pillow python tools/gerar_fonte.py [--saida server/fonte_dados.py] [--dir PASTA ...]

Procura as fontes DejaVu em --dir, depois em `fc-list`, depois em pastas conhecidas
(/usr/share/fonts/truetype/dejavu, /usr/share/fonts/dejavu e o runtime flatpak freedesktop).
"""
import argparse
import base64
import glob
import os
import subprocess
import sys
import zlib

from PIL import Image, ImageDraw, ImageFont

# nome interno -> (arquivo, tamanhos em px)
FONTES = {
    "sans-bold": ("DejaVuSans-Bold.ttf", (26, 34, 48, 72, 140)),
    "sans": ("DejaVuSans.ttf", (26, 34)),
    "mono": ("DejaVuSansMono.ttf", (26, 34)),
}
CARACTERES = [chr(c) for c in range(32, 127)] + ["°", "·"]  # ASCII + grau + ponto medio ("%" ja esta no ASCII)
PASTAS_CONHECIDAS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/usr/share/fonts/dejavu-sans-fonts",
]
PASTAS_GLOB = ["/var/lib/flatpak/runtime/org.freedesktop.Platform/*/*/*/files/share/fonts/dejavu"]

CABECALHO = '''\
"""Glifos DejaVu pre-rasterizados (GERADO por tools/gerar_fonte.py: nao edite a mao).

Licenca das fontes: DejaVu Fonts (baseadas em Bitstream Vera), https://dejavu-fonts.github.io/License.html
  Fonts are (c) Bitstream (see below). DejaVu changes are in public domain.
  Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. Bitstream Vera is a trademark of Bitstream, Inc.
  Copyright (c) 2006 by Tavmjong Bah. All Rights Reserved.
A licenca permite usar, copiar, embutir e redistribuir as fontes (e derivados como estes bitmaps) sem custo,
desde que o aviso de copyright acima seja mantido. Estes dados sao bitmaps de cobertura 8-bit (0-255)
renderizados com FreeType/Pillow a partir de DejaVu Sans, DejaVu Sans Bold e DejaVu Sans Mono.

Formato: FONTES[nome][tamanho_px] = {
    "ascent": int, "descent": int,          # metricas da fonte (px)
    "glifos": {codigo: (avanco, xoff, yoff, largura, altura, deslocamento)},
        # avanco em px (float); xoff/yoff = canto superior esquerdo do bitmap relativo a origem na linha de base
        # (yoff negativo = acima da base); deslocamento = posicao dos bytes no blob descomprimido.
    "dados": "<base64 de zlib de todos os bitmaps concatenados, linha a linha>",
}
"""
'''


def achar_pastas(extras):
    pastas = list(extras)
    try:
        saida = subprocess.run(["fc-list"], capture_output=True, text=True, check=False).stdout
        for linha in saida.splitlines():
            caminho = linha.split(":")[0]
            if "dejavu" in caminho.lower():
                pastas.append(os.path.dirname(caminho))
    except OSError:
        pass
    pastas += PASTAS_CONHECIDAS
    for padrao in PASTAS_GLOB:
        pastas += sorted(glob.glob(padrao))
    return pastas


def localizar(arquivo, pastas):
    for p in pastas:
        c = os.path.join(p, arquivo)
        if os.path.isfile(c):
            return c
    raise SystemExit("nao achei %s (procurei em %s); use --dir" % (arquivo, ", ".join(dict.fromkeys(pastas))))


def rasterizar(fonte, ch):
    """(avanco, xoff, yoff, largura, altura, bytes) de um glifo, origem na linha de base."""
    avanco = float(fonte.getlength(ch))
    ascent, descent = fonte.getmetrics()
    pad = 8
    larg = int(avanco) + 2 * pad + fonte.size
    alt = ascent + descent + 2 * pad + fonte.size // 2
    img = Image.new("L", (larg, alt), 0)
    ImageDraw.Draw(img).text((pad, pad + ascent), ch, font=fonte, fill=255, anchor="ls")
    caixa = img.getbbox()
    if caixa is None:  # espaco
        return avanco, 0, 0, 0, 0, b""
    rec = img.crop(caixa)
    return avanco, caixa[0] - pad, caixa[1] - (pad + ascent), rec.width, rec.height, rec.tobytes()


def gerar_tamanho(caminho, tam):
    fonte = ImageFont.truetype(caminho, tam)
    ascent, descent = fonte.getmetrics()
    glifos, blob = {}, bytearray()
    for ch in CARACTERES:
        avanco, xoff, yoff, w, h, dados = rasterizar(fonte, ch)
        glifos[ord(ch)] = (round(avanco, 3), xoff, yoff, w, h, len(blob))
        blob += dados
    dados64 = base64.b64encode(zlib.compress(bytes(blob), 9)).decode("ascii")
    return {"ascent": ascent, "descent": descent, "glifos": glifos, "dados": dados64}


def escrever(saida, pastas):
    partes = [CABECALHO, "FONTES = {\n"]
    for nome, (arquivo, tamanhos) in FONTES.items():
        caminho = localizar(arquivo, pastas)
        print("%s <- %s" % (nome, caminho), file=sys.stderr)
        partes.append("    %r: {\n" % nome)
        for tam in tamanhos:
            d = gerar_tamanho(caminho, tam)
            partes.append("        %d: {\n" % tam)
            partes.append("            \"ascent\": %d,\n            \"descent\": %d,\n" % (d["ascent"], d["descent"]))
            partes.append("            \"glifos\": {\n")
            for cod, g in d["glifos"].items():
                partes.append("                %d: %r,\n" % (cod, g))
            partes.append("            },\n")
            partes.append("            \"dados\": (\n")
            texto = d["dados"]
            for i in range(0, len(texto), 100):
                partes.append("                %r\n" % texto[i:i + 100])
            partes.append("            ),\n        },\n")
        partes.append("    },\n")
    partes.append("}\n")
    conteudo = "".join(partes)
    with open(saida, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("%s: %d bytes" % (saida, len(conteudo.encode("utf-8"))), file=sys.stderr)


def main(argv=None):
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--saida", default=os.path.join(raiz, "server", "fonte_dados.py"))
    p.add_argument("--dir", action="append", default=[], help="pasta com as fontes DejaVu (repetivel)")
    args = p.parse_args(argv)
    escrever(args.saida, achar_pastas(args.dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
