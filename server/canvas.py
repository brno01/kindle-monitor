"""Canvas minimo em tons de cinza (8-bit) para desenhar a tela PNG. Somente biblioteca padrao.

Cores sao inteiros 0 (preto) a 255 (branco). Paleta recomendada para e-ink: areas chapadas, sem dithering.
Texto vem de `fonte_dados` (glifos pre-rasterizados, cobertura 8-bit), misturados ao fundo por antialias.
Com `estrito=True` qualquer desenho que saia dos limites levanta `ForaDosLimites` (usado nos testes);
sem ele o desenho e recortado em silencio.
"""
import base64
import math
import zlib

import fonte_dados
import png

PRETO, ESCURO, MEDIO, CLARO, TRILHO, BRANCO = 0, 70, 140, 200, 235, 255
DESCONHECIDO = ord("?")


class ForaDosLimites(Exception):
    """Desenho fora da imagem (modo estrito)."""


_cache_fontes = {}


def carregar_fonte(nome, tam):
    """Decodifica (uma vez) os glifos de `fonte_dados.FONTES[nome][tam]`."""
    chave = (nome, tam)
    f = _cache_fontes.get(chave)
    if f is None:
        bruto = fonte_dados.FONTES[nome][tam]
        blob = zlib.decompress(base64.b64decode("".join(bruto["dados"])))
        glifos = {}
        for cod, (avanco, xoff, yoff, w, h, desl) in bruto["glifos"].items():
            glifos[cod] = {"avanco": avanco, "xoff": xoff, "yoff": yoff, "w": w, "h": h,
                           "bitmap": blob[desl:desl + w * h]}
        f = {"ascent": bruto["ascent"], "descent": bruto["descent"], "glifos": glifos}
        _cache_fontes[chave] = f
    return f


def _glifo(fonte, ch):
    g = fonte["glifos"]
    return g.get(ord(ch)) or g[DESCONHECIDO]


def altura_capital(nome, tam):
    """Altura em px de uma letra maiuscula/algarismo (acima da linha de base)."""
    return carregar_fonte(nome, tam)["glifos"][ord("H")]["h"]


def _clamp01(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


class Canvas:
    def __init__(self, largura, altura, fundo=BRANCO, estrito=False):
        self.largura = int(largura)
        self.altura = int(altura)
        self.estrito = estrito
        self.pixels = bytearray([fundo]) * (self.largura * self.altura)

    # ------------------------------------------------------------------ interno
    def _caixa(self, x0, y0, x1, y1):
        """Recorta a caixa [x0,x1) x [y0,y1); em modo estrito, levanta se algo ficar fora."""
        if self.estrito and (x0 < 0 or y0 < 0 or x1 > self.largura or y1 > self.altura):
            raise ForaDosLimites("(%s,%s)-(%s,%s) fora de %dx%d" % (x0, y0, x1, y1, self.largura, self.altura))
        return max(0, x0), max(0, y0), min(self.largura, x1), min(self.altura, y1)

    def _misturar(self, i, cor, cob):
        """Mistura `cor` sobre o pixel i com cobertura cob (0..255)."""
        if cob >= 255:
            self.pixels[i] = cor
        elif cob > 0:
            o = self.pixels[i]
            d = (cor - o) * cob
            self.pixels[i] = o + ((d + 127) // 255 if d >= 0 else -((127 - d) // 255))

    # ---------------------------------------------------------------- primitivas
    def retangulo(self, x, y, w, h, cor):
        x0, y0, x1, y1 = self._caixa(int(x), int(y), int(x + w), int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        fatia = bytes([cor]) * (x1 - x0)
        for yy in range(y0, y1):
            i = yy * self.largura
            self.pixels[i + x0:i + x1] = fatia

    def contorno(self, x, y, w, h, cor, espessura=2):
        e = min(int(espessura), int(w) // 2 or 1, int(h) // 2 or 1)
        self.retangulo(x, y, w, e, cor)
        self.retangulo(x, y + h - e, w, e, cor)
        self.retangulo(x, y + e, e, h - 2 * e, cor)
        self.retangulo(x + w - e, y + e, e, h - 2 * e, cor)

    def _disco(self, cx, cy, r, cor):
        """Disco com antialias; centro e raio em float."""
        x0, y0, x1, y1 = self._caixa(int(math.floor(cx - r - 1)), int(math.floor(cy - r - 1)),
                                     int(math.ceil(cx + r + 1)), int(math.ceil(cy + r + 1)))
        for yy in range(y0, y1):
            dy = yy + 0.5 - cy
            for xx in range(x0, x1):
                dx = xx + 0.5 - cx
                cob = _clamp01(r + 0.5 - math.hypot(dx, dy))
                if cob > 0:
                    self._misturar(yy * self.largura + xx, cor, int(cob * 255 + 0.5))

    def circulo(self, cx, cy, r, cor):
        """Circulo preenchido centrado no ponto (cx, cy) (coordenadas de pixel, borda a borda)."""
        if self.estrito:
            self._caixa(int(cx - r), int(cy - r), int(cx + r + 1), int(cy + r + 1))
            self._disco(cx + 0.5, cy + 0.5, r, cor)
        else:
            self._disco(cx + 0.5, cy + 0.5, r, cor)

    def linha(self, x0, y0, x1, y1, cor, espessura=1):
        e = max(1, int(round(espessura)))
        if y0 == y1:
            xa, xb = min(x0, x1), max(x0, x1)
            self.retangulo(xa, y0 - e // 2, xb - xa + 1, e, cor)
            return
        if x0 == x1:
            ya, yb = min(y0, y1), max(y0, y1)
            self.retangulo(x0 - e // 2, ya, e, yb - ya + 1, cor)
            return
        r = e / 2.0
        if self.estrito:
            self._caixa(int(math.floor(min(x0, x1) - r)), int(math.floor(min(y0, y1) - r)),
                        int(math.ceil(max(x0, x1) + r)) + 1, int(math.ceil(max(y0, y1) + r)) + 1)
        passos = max(1, int(math.hypot(x1 - x0, y1 - y0)))
        for i in range(passos + 1):
            t = i / passos
            self._disco(x0 + (x1 - x0) * t + 0.5, y0 + (y1 - y0) * t + 0.5, r, cor)

    def polilinha(self, pontos, cor, espessura=2):
        for (xa, ya), (xb, yb) in zip(pontos, pontos[1:]):
            self.linha(xa, ya, xb, yb, cor, espessura)

    def cruz_x(self, x, y, lado, cor, espessura=3):
        """X dentro do quadrado (x, y, lado, lado)."""
        self.linha(x, y, x + lado - 1, y + lado - 1, cor, espessura)
        self.linha(x, y + lado - 1, x + lado - 1, y, cor, espessura)

    def retangulo_arredondado(self, x, y, w, h, raio, cor):
        """Retangulo preenchido com cantos arredondados (antialias so nos cantos)."""
        x, y, w, h = int(x), int(y), int(w), int(h)
        r = max(0, min(int(raio), w // 2, h // 2))
        x0, y0, x1, y1 = self._caixa(x, y, x + w, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            ci = yy + 0.5
            if ci < y + r:
                cy = y + r
            elif ci > y + h - r:
                cy = y + h - r
            else:
                cy = None
            if cy is None or r == 0:
                self.retangulo(x0, yy, x1 - x0, 1, cor)
                continue
            dy = ci - cy
            esq_fim, dir_ini = x + r, x + w - r
            self.retangulo(max(x0, esq_fim), yy, max(0, min(x1, dir_ini) - max(x0, esq_fim)), 1, cor)
            for xx in list(range(x0, min(x1, esq_fim))) + list(range(max(x0, dir_ini), x1)):
                cx = esq_fim if xx < esq_fim else dir_ini
                cob = _clamp01(r + 0.5 - math.hypot(xx + 0.5 - cx, dy))
                self._misturar(yy * self.largura + xx, cor, int(cob * 255 + 0.5))

    def contorno_arredondado(self, x, y, w, h, raio, cor_borda, espessura, cor_interna):
        """Borda de `espessura` px e miolo `cor_interna` (pinta o retangulo todo: borda e depois miolo)."""
        self.retangulo_arredondado(x, y, w, h, raio, cor_borda)
        self.retangulo_arredondado(x + espessura, y + espessura, w - 2 * espessura, h - 2 * espessura,
                                   max(0, raio - espessura), cor_interna)

    # --------------------------------------------------------------------- texto
    @staticmethod
    def medir(texto, fonte, tam):
        f = carregar_fonte(fonte, tam)
        return sum(_glifo(f, ch)["avanco"] for ch in texto)

    def texto(self, x, y_base, texto, fonte, tam, cor, alinhar="esq"):
        """Desenha `texto` com a linha de base em y_base. `x` e a borda esquerda, direita ou o centro."""
        f = carregar_fonte(fonte, tam)
        larg = self.medir(texto, fonte, tam)
        pen = x - larg if alinhar == "dir" else x - larg / 2.0 if alinhar == "centro" else float(x)
        pen = float(pen)
        for ch in texto:
            g = _glifo(f, ch)
            if g["w"]:
                gx = int(round(pen + g["xoff"]))
                gy = int(y_base + g["yoff"])
                self._glifo_bitmap(gx, gy, g, cor)
            pen += g["avanco"]
        return larg

    def _glifo_bitmap(self, gx, gy, g, cor):
        w, h, bmp = g["w"], g["h"], g["bitmap"]
        x0, y0, x1, y1 = self._caixa(gx, gy, gx + w, gy + h)
        pix, W = self.pixels, self.largura
        for yy in range(y0, y1):
            linha = bmp[(yy - gy) * w + (x0 - gx):(yy - gy) * w + (x1 - gx)]
            base = yy * W + x0
            for i, cob in enumerate(linha):
                if cob == 255:
                    pix[base + i] = cor
                elif cob:
                    o = pix[base + i]
                    d = (cor - o) * cob
                    pix[base + i] = o + ((d + 127) // 255 if d >= 0 else -((127 - d) // 255))

    def para_png(self):
        return png.gerar_png(self.largura, self.altura, self.pixels)
