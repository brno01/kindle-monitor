#!/usr/bin/env python3
"""Gera server/icones_dados.py: icones pre-rasterizados (cobertura 8-bit) para o renderizador PNG.

Ferramenta de DESENVOLVIMENTO (usa Pillow + svgelements). O servidor so le o arquivo gerado. Uso:

    uv run --no-project --with pillow --with svgelements python tools/gerar_icones.py

Entrada: tools/icones/<nome>.svg, com <nome> em ^[a-z]{2,16}$ (os outros arquivos sao ignorados).
Os SVGs sao tratados como dado nao confiavel: so os atributos `d` (de todos os <path>), `fill-rule` e
`viewBox` sao lidos por busca linear (arquivo de ate 256 KB, `d` somado de ate 64 KB); nenhum parser XML e usado e nada e executado.
"""
import base64
import os
import re
import sys
import zlib

from PIL import Image, ImageChops, ImageDraw
from svgelements import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "tools", "icones")
SAIDA = os.path.join(RAIZ, "server", "icones_dados.py")
TAMANHOS = (56, 40, 30)
SUPER = 8
FOLGA = 0.92  # so sem viewBox: desenho ocupa 92% da caixa (a viewBox ja define a margem do icone)
NOME_OK = re.compile(r"^[a-z]{2,16}$")

CABECALHO_TOPO = '''\
"""Icones pre-rasterizados (GERADO por tools/gerar_icones.py: nao edite a mao).

Origem de cada icone (do comentario <!-- Source: ... --> do SVG em tools/icones/):
'''

CABECALHO_BASE = '''\

Formato: ICONES[nome][tamanho_px] = {"w": int, "h": int, "dados": (<base64 de zlib de w*h bytes de cobertura 0-255>)}
"""
'''

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
TAM_MAX_SVG = 256 * 1024  # SVG maior que isso e recusado antes de ler
D_MAX = 64 * 1024         # soma dos atributos d de um icone
# dentro de UMA tag ja delimitada (sem `>`); classes negadas, sem quantificador aninhado
_ATTR_D = re.compile(r'\sd="([^"]+)"')
_ATTR_REGRA = re.compile(r'\sfill-rule="(evenodd|nonzero)"')
_ATTR_VIEWBOX = re.compile(r'\sviewBox="([^"]+)"')


def _fonte(txt):
    """Texto do primeiro comentario `<!-- Source: ... -->`, em ASCII imprimivel e seguro para um docstring.
    Busca linear (str.find), sem regex com backtracking: o SVG e dado nao confiavel."""
    i = txt.find("<!--")
    while i != -1:
        j = i + 4
        while j < len(txt) and txt[j].isspace():
            j += 1
        if txt.startswith("Source:", j):
            fim = txt.find("-->", j + 7)
            if fim == -1:
                return ""
            bruto = txt[j + 7:fim]
            s = "".join(ch if " " <= ch <= "~" else (" " if ch.isspace() else "?") for ch in bruto)
            s = " ".join(s.split())
            return s.replace('"""', "'''").replace("\\", "/")
        i = txt.find("<!--", i + 4)
    return ""


def _tags(txt, nome):
    """Texto de cada tag `<nome ...>` (ate o primeiro `>`), em tempo linear; tag sem `>` encerra a busca."""
    marca = "<" + nome
    i = txt.find(marca)
    while i != -1:
        k = i + len(marca)
        if k < len(txt) and (txt[k].isalnum() or txt[k] == "_"):  # `<pathx`, `<svgs`: outra tag (como \b)
            i = txt.find(marca, k)
            continue
        fim = txt.find(">", k)
        if fim == -1:
            return
        yield txt[i:fim + 1]
        i = txt.find(marca, fim + 1)


def ler_svg(caminho):
    """-> {"paths": [(d, regra)], "viewbox": (x, y, w, h) | None, "fonte": str}. So busca linear, sem parser XML."""
    if os.path.getsize(caminho) > TAM_MAX_SVG:
        sys.exit("%s: arquivo grande demais (maximo %d KB)" % (caminho, TAM_MAX_SVG // 1024))
    with open(caminho, encoding="utf-8", errors="replace") as f:
        txt = f.read(TAM_MAX_SVG + 1)
    paths = []
    total_d = 0
    for t in _tags(txt, "path"):
        d = _ATTR_D.search(t)
        if not d:
            continue
        total_d += len(d.group(1))
        if total_d > D_MAX:
            sys.exit("%s: atributos d somam mais de %d KB" % (caminho, D_MAX // 1024))
        regra = _ATTR_REGRA.search(t)
        paths.append((d.group(1), regra.group(1) if regra else "nonzero"))
    if not paths:
        sys.exit("nenhum <path> com atributo d em %s" % caminho)
    vb = None
    for t in _tags(txt, "svg"):
        m = _ATTR_VIEWBOX.search(t)
        if not m:
            continue
        nums = re.findall(_NUM, m.group(1))
        if len(nums) == 4:
            x, y, w, h = (float(n) for n in nums)
            if w > 0 and h > 0:
                vb = (x, y, w, h)
        break
    return {"paths": paths, "viewbox": vb, "fonte": _fonte(txt)}


def listar_icones(pasta):
    """Nomes validos (arquivo <nome>.svg com nome em ^[a-z]{2,16}$), ordenados."""
    nomes = []
    for arq in os.listdir(pasta):
        nome, ext = os.path.splitext(arq)
        if ext == ".svg" and NOME_OK.match(nome) and os.path.isfile(os.path.join(pasta, arq)):
            nomes.append(nome)
    return sorted(nomes)


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
            if not atual:  # segmento logo apos Close, sem Move: recomeca no inicio dele
                atual = [(seg.start.x, seg.start.y)]
            n = 1 if nome == "Line" else 16
            for i in range(1, n + 1):
                pt = seg.point(i / n)
                atual.append((pt.x, pt.y))
    if len(atual) > 2:
        polis.append(atual)
    return polis


def _area(pol):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pol, pol[1:] + pol[:1])) / 2.0


def preencher(polis, regra, lado):
    """Mascara lado x lado (0/255). `polis` ja esta em pixels da grade `lado`."""
    if regra == "evenodd":
        acc = Image.new("L", (lado, lado), 0)
        for pol in polis:  # XOR de cada subpath = even-odd
            t = Image.new("L", (lado, lado), 0)
            ImageDraw.Draw(t).polygon(pol, fill=255)
            acc = ImageChops.difference(acc, t)
        return acc
    # nonzero por soma de enrolamento: cada subpath soma +1 ou -1 pelo sinal da area; cheio se soma != 0
    pos = Image.new("L", (lado, lado), 0)
    neg = Image.new("L", (lado, lado), 0)
    for pol in polis:
        t = Image.new("L", (lado, lado), 0)
        ImageDraw.Draw(t).polygon(pol, fill=1)
        if _area(pol) > 0:
            pos = ImageChops.add(pos, t)
        else:
            neg = ImageChops.add(neg, t)
    dif = ImageChops.add(ImageChops.subtract(pos, neg), ImageChops.subtract(neg, pos))
    return dif.point(lambda v: 255 if v else 0)


def rasterizar(paths, viewbox, tam):
    """Bitmap tam x tam (bytes de cobertura 0-255). `paths` = [(poligonos, regra)]."""
    lado = tam * SUPER
    if viewbox:
        vx, vy, vw, vh = viewbox
        esc = lado / max(vw, vh)  # mesma escala para todo icone com a mesma viewBox
        ox = (lado - vw * esc) / 2.0 - vx * esc
        oy = (lado - vh * esc) / 2.0 - vy * esc
    else:
        xs = [x for polis, _ in paths for p in polis for x, _ in p]
        ys = [y for polis, _ in paths for p in polis for _, y in p]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        esc = lado * FOLGA / max(x1 - x0, y1 - y0)
        ox = (lado - (x1 - x0) * esc) / 2.0 - x0 * esc
        oy = (lado - (y1 - y0) * esc) / 2.0 - y0 * esc
    total = Image.new("L", (lado, lado), 0)
    for polis, regra in paths:
        pts = [[(x * esc + ox, y * esc + oy) for x, y in pol] for pol in polis]
        if pts:
            total = ImageChops.lighter(total, preencher(pts, regra, lado))
    return total.resize((tam, tam), Image.BOX).tobytes()  # media por caixa = cobertura 0-255


def carregar(pasta):
    """-> [(nome, svg_lido, [(poligonos, regra)])] dos icones validos da pasta."""
    saida = []
    for nome in listar_icones(pasta):
        svg = ler_svg(os.path.join(pasta, nome + ".svg"))
        saida.append((nome, svg, [(poligonos(d), regra) for d, regra in svg["paths"]]))
    return saida


def gerar(pasta):
    """Texto completo de icones_dados.py para os SVGs da pasta."""
    icones = carregar(pasta)
    if not icones:
        sys.exit("nenhum icone valido em %s" % pasta)
    partes = [CABECALHO_TOPO]
    for nome, svg, _ in icones:
        partes.append("- %s: %s\n" % (nome, svg["fonte"] or "(sem origem declarada)"))
    partes.append(CABECALHO_BASE)
    partes.append("ICONES = {\n")
    for nome, svg, paths in icones:
        partes.append("    %r: {\n" % nome)
        for tam in TAMANHOS:
            bmp = rasterizar(paths, svg["viewbox"], tam)
            b64 = base64.b64encode(zlib.compress(bmp, 9)).decode("ascii")
            partes.append("        %d: {\n            \"w\": %d,\n            \"h\": %d,\n            \"dados\": (\n" % (tam, tam, tam))
            for i in range(0, len(b64), 100):
                partes.append("                %r\n" % b64[i:i + 100])
            partes.append("            ),\n        },\n")
        partes.append("    },\n")
    partes.append("}\n")
    return "".join(partes)


def main():
    texto = gerar(PASTA)
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(texto)
    print("%s: %d icones" % (SAIDA, len(listar_icones(PASTA))), file=sys.stderr)


if __name__ == "__main__":
    main()
