"""Tela PNG (retrato, tons de cinza) do kindle-monitor. Funcoes puras: metricas -> bytes PNG.

Sete paginas (resumo, servicos, aparelhos, detalhes, claude, comandos e jogos, que nao e aba) mais a barra de navegacao fixa
no rodape. Os botoes vem
sempre de `botoes.layout` (a mesma funcao que serve /botoes.json): aqui so se desenha o que ela devolve.
Visual e-ink: alto contraste, contornos finos, raios pequenos, sem sombras; so os tamanhos de fonte embutidos
(26 e 34; negrito tambem 48, 72 e 140). Estado de servico: forma antes da cor (cheia = ativo, vazia = parado,
X = falha, ? = desconhecido).
"""
import math
import sys
import unicodedata
from datetime import datetime

import alertas
import botoes
import coletores
import formato
import icones_dados
import kindle_status
import perfis
import servicos
from canvas import BRANCO, CLARO, ESCURO, MEDIO, PRETO, TRILHO, Canvas, altura_capital

NEG, REG, MONO = "sans-bold", "sans", "mono"
MARGEM = botoes.MARGEM
GAP = botoes.GAP
ALTURA_CABECALHO = botoes.CAB_PX
RAIO = 10
PAD = 16


# ------------------------------------------------------------------ utilidades

def _limpar(texto):
    """Texto seguro para as fontes embutidas: ASCII imprimivel, mais grau e ponto medio."""
    saida = []
    for ch in unicodedata.normalize("NFKD", str(texto)):
        if unicodedata.combining(ch):
            continue
        o = ord(ch)
        saida.append(ch if 32 <= o < 127 or o in (0xB0, 0xB7) else "?" if o > 127 else " ")
    return "".join(saida)


def _ajustar(c, texto, fonte, tam, larg_max):
    """Corta com reticencias (nunca no meio de um glifo) para caber em larg_max."""
    texto = _limpar(texto)
    if c.medir(texto, fonte, tam) <= larg_max:
        return texto
    while texto and c.medir(texto + "...", fonte, tam) > larg_max:
        texto = texto[:-1]
    return (texto + "...") if c.medir(texto + "...", fonte, tam) <= larg_max else ""


_SEPARADORES_ITENS = ("  ", ", ")


def _ajustar_itens(c, texto, fonte, tam, larg_max):
    """Como `_ajustar`, mas corta so em fronteira de item (depois de um dos `separadores`) e termina em "...": a linha
    JOGOS lista nomes de servidores, e "parado: V..." nao diz nada. Sem fronteira que caiba, cai no corte por caractere."""
    texto = _limpar(texto)
    if c.medir(texto, fonte, tam) <= larg_max:
        return texto
    cortes = sorted({i for sep in _SEPARADORES_ITENS for i in range(1, len(texto)) if texto.startswith(sep, i)},
                    reverse=True)
    for i in cortes:
        cand = texto[:i].rstrip(" ,\u00b7") + "..."
        if len(cand) > 3 and c.medir(cand, fonte, tam) <= larg_max:
            return cand
    return _ajustar(c, texto, fonte, tam, larg_max)


def _ok(bloco):
    return isinstance(bloco, dict) and "erro" not in bloco


def _num(v):
    """Numero finito e razoavel; inteiro >= 2**53 (JSON malformado) conta como ausente, nao estoura float()."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if isinstance(v, int):
        return v if abs(v) < 2 ** 53 else None
    return v if math.isfinite(v) else None


def _pct(fn):
    try:
        v = _num(fn())
        return None if v is None else min(100.0, max(0.0, float(v)))
    except Exception:
        return None


def _un(v, base):
    un = ("B", "KB", "MB", "GB", "TB", "PB")
    i, t = 0, float(v)
    while t >= base and i < len(un) - 1:
        t /= float(base)
        i += 1
    return t, i, un


def _tamanho(usado, total, base=1000):
    """'7.4/19.4 GB': mesma unidade para os dois (escolhida pelo total)."""
    t, i, un = _un(total, base)
    f = float(base) ** i
    fmt = "%.0f" if t >= 40 else "%.1f"  # 33/42 GB, 373/932 GB, mas 7.4/19.4 GB
    return (fmt + "/" + fmt + " %s") % (usado / f, total / f, un[i])


def _uptime(seg):
    d, resto = divmod(int(seg), 86400)
    h, resto = divmod(resto, 3600)
    mi = resto // 60
    return "%dd %02dh %02dm" % (d, h, mi) if d else "%dh %02dm" % (h, mi)


def _hora(m, fmt):
    try:
        return datetime.fromisoformat(m["gerado_em"]).strftime(fmt)
    except Exception:
        return "--:--:--" if "%S" in fmt else "--:--"


def _cap(fonte, tam):
    return altura_capital(fonte, tam)


def _texto_c(c, x, y_centro, texto, fonte, tam, cor, alinhar="esq"):
    """Texto com o centro das maiusculas em y_centro."""
    c.texto(x, y_centro + _cap(fonte, tam) // 2, texto, fonte, tam, cor, alinhar)


# --------------------------------------------------------------- componentes

def _card(c, x, y, w, h):
    c.contorno_arredondado(x, y, w, h, RAIO, PRETO, 2, BRANCO)


def _barra(c, x, y, w, h, pct):
    """Trilho claro com contorno fino e preenchimento preto."""
    r = min(6, h // 2)
    c.contorno_arredondado(x, y, w, h, r, ESCURO, 2, TRILHO)
    if pct is None:
        return
    iw, ih = w - 4, h - 4
    cheio = int(round(iw * pct / 100.0))
    if cheio > 0:
        c.retangulo_arredondado(x + 2, y + 2, max(cheio, min(4, iw)), ih, max(1, r - 2), PRETO)


def _sparkline(c, x, y_base, w, h, serie):
    """Area + linha do historico (0..100%), a amostra mais recente na direita."""
    pts = []
    n = len(serie)
    passo = w / float(max(2, n) - 1)
    for i, v in enumerate(serie):
        v = _num(v)
        if v is None:
            continue
        px = x + w - (n - 1 - i) * passo
        py = y_base - 2 - min(100.0, max(0.0, v)) / 100.0 * (h - 5)
        pts.append((px, py))
    c.retangulo(x, y_base - 1, w, 2, CLARO)
    if len(pts) < 2:
        return
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        for cx in range(int(round(xa)), int(round(xb)) + 1):
            t = 0 if xb == xa else (cx - xa) / (xb - xa)
            top = int(ya + (yb - ya) * t)
            c.retangulo(cx, top, 1, max(0, int(y_base - 1 - top)), TRILHO)
    c.polilinha([(int(round(px)), int(round(py))) for px, py in pts], PRETO, 2)
    c.circulo(int(round(pts[-1][0])), int(round(pts[-1][1])), 3, PRETO)


def _forma(c, x, y, lado, estado):
    """Forma do estado dentro do quadrado (x, y, lado, lado): cheia, vazia, X, triangulo com ! (aviso) ou ?."""
    cx, cy, r = x + lado // 2, y + lado // 2, lado // 2 - 1
    if estado == "ativo":
        c.circulo(cx, cy, r, PRETO)
    elif estado == "parado":
        c.circulo(cx, cy, r, PRETO)
        c.circulo(cx, cy, r - 3, BRANCO)
    elif estado == "falha":
        c.contorno(x + 1, y + 1, lado - 2, lado - 2, PRETO, 3)
        c.cruz_x(x + 7, y + 7, lado - 14, PRETO, 3)
    elif estado == "aviso":  # triangulo com "!"
        base, topo = y + lado - 2, y + 1
        c.polilinha([(cx, topo), (x + lado - 1, base), (x + 1, base), (cx, topo)], PRETO, 3)
        c.retangulo(cx - 1, y + lado // 3 + 2, 3, max(3, lado // 4), PRETO)
        c.retangulo(cx - 1, base - max(5, lado // 6) - 1, 3, 3, PRETO)
    else:
        c.contorno(x + 1, y + 1, lado - 2, lado - 2, MEDIO, 2)
        c.texto(cx, cy + _cap(NEG, 26) // 2, "?", NEG, 26, ESCURO, alinhar="centro")


def _forma_ok(c, x, y, lado, ok):
    _forma(c, x, y, lado, "ativo" if ok else "falha")


# ------------------------------------------------------------------ cabecalho

def _cabecalho(c, m, itens):
    """Fino: host a esquerda e hora (HH:MM, sem segundos) a direita; uma linha clara embaixo (abaixo da barra do Kindle).
    O resumo dos servicos saiu (a linha SERVICOS da tela inicial e o ATENCAO ja dizem isso)."""
    base = botoes.BARRA_KINDLE_H + 14 + _cap(NEG, 34)
    hora = _hora(m, "%H:%M")
    c.texto(c.largura - MARGEM, base, hora, NEG, 34, PRETO, alinhar="dir")
    fim = c.largura - MARGEM - c.medir(hora, NEG, 34) - 28
    c.texto(MARGEM, base, _ajustar(c, _limpar(m.get("host", "?")), NEG, 34, max(40, fim - MARGEM)), NEG, 34, PRETO)
    c.retangulo(MARGEM, ALTURA_CABECALHO - 4, c.largura - 2 * MARGEM, 2, CLARO)


# ------------------------------------------------------------ barra do Kindle

def _riscar(c, x, yc, lado):
    """Traco diagonal sobre um icone de `lado` px: 'desligado'."""
    c.linha(x - 2, yc + lado // 2, x + lado + 2, yc - lado // 2, BRANCO, 6)
    c.linha(x - 2, yc + lado // 2, x + lado + 2, yc - lado // 2, PRETO, 2)


def _icone_bateria(c, x, yc, pct, carregando):
    """Corpo 46x24 com ponta a direita; preenchimento proporcional; raio branco por cima quando carrega."""
    w, h = 46, 24
    y = yc - h // 2
    baixa = pct is not None and pct <= kindle_status.BATERIA_BAIXA and not carregando
    c.contorno_arredondado(x, y, w, h, 5, PRETO, 3 if baixa else 2, BRANCO)
    c.retangulo_arredondado(x + w, yc - 5, 5, 10, 2, PRETO)
    if pct is not None:
        iw = w - 8
        cheio = int(round(iw * pct / 100.0))
        if cheio > 0:
            c.retangulo_arredondado(x + 4, y + 4, max(3, cheio), h - 8, 2, PRETO)
    if carregando:
        cx = x + w // 2
        pts = [(cx + 3, y + 2), (cx - 5, yc + 1), (cx + 1, yc + 1), (cx - 3, y + h - 2)]
        c.polilinha(pts, BRANCO, 5)
        c.polilinha(pts, PRETO, 2)
    return w + 5


def _icone_wifi(c, x, yc, barras, ok):
    """Cinco barras crescentes, cheias ate o sinal; sem conexao, todas claras e riscadas."""
    base = yc + 12
    for i in range(5):
        hb = 6 + i * 4 + (1 if i == 4 else 0)
        cor = PRETO if ok and barras is not None and i < barras else CLARO
        c.retangulo_arredondado(x + i * 9, base - hb, 6, hb, 1, cor)
    if not ok:
        _riscar(c, x + 6, yc, 30)
    return 42


def _icone_aviao(c, x, yc, ligado):
    """Aviao visto de cima, nariz para cima (o icone classico do modo aviao); desligado = cinza riscado."""
    cor = PRETO if ligado else MEDIO
    cx = x + 13
    c.linha(cx, yc - 12, cx, yc + 9, cor, 4)                                     # fuselagem
    c.circulo(cx, yc - 12, 2, cor)                                                # nariz
    c.polilinha([(cx - 13, yc + 3), (cx, yc - 5), (cx + 13, yc + 3)], cor, 4)    # asas
    c.polilinha([(cx - 6, yc + 13), (cx, yc + 8), (cx + 6, yc + 13)], cor, 3)    # cauda
    if not ligado:
        _riscar(c, x, yc, 26)
    return 26


def _icone_bt(c, x, yc, ligado, conectados):
    """Runa do Bluetooth; ponto cheio ao lado = aparelho conectado; desligado = cinza riscado."""
    cor = PRETO if ligado else MEDIO
    t, b = yc - 12, yc + 12
    c.linha(x + 8, t, x + 8, b, cor, 2)
    c.polilinha([(x + 1, yc - 6), (x + 15, yc + 6), (x + 8, b)], cor, 2)
    c.polilinha([(x + 1, yc + 6), (x + 15, yc - 6), (x + 8, t)], cor, 2)
    w = 17
    if ligado and conectados:
        c.circulo(x + 22, yc, 4, PRETO)
        w = 28
    if not ligado:
        _riscar(c, x, yc, 17)
    return w


def _icone_sync(c, x, yc, cor):
    """Dois arcos com setas na ponta (sincronizar), 24 px de largura."""
    cx, r = x + 12, 10
    for a0, a1 in ((200, 330), (20, 150)):
        pts = [(cx + r * math.cos(math.radians(a)), yc + r * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 10)]
        c.polilinha([(int(round(px)), int(round(py))) for px, py in pts], cor, 2)
        ex, ey = pts[-1]
        a = math.radians(a1)
        tx, ty = -math.sin(a), math.cos(a)  # sentido do arco (horario na tela)
        for giro in (2.5, -2.5):  # chevron de ~145 graus para tras
            dx = tx * math.cos(giro) - ty * math.sin(giro)
            dy = tx * math.sin(giro) + ty * math.cos(giro)
            c.linha(int(round(ex)), int(round(ey)), int(round(ex + 6 * dx)), int(round(ey + 6 * dy)), cor, 2)
    return 24


def _texto_elo(kv):
    partes = [kv.get("tailscale") or "elo ?"]
    if kv.get("latencia"):
        partes.append(kv["latencia"])
    if kv.get("falhas"):
        partes.append("%d falhas" % kv["falhas"])
    if kv.get("relogio") and kv["relogio"] != "ok":
        partes.append("relogio " + kv["relogio"])
    return " · ".join(partes)


def _barra_kindle(c, kv):
    """Barra de status do proprio Kindle (y 0..BARRA_KINDLE_H): elo com o atheron a esquerda, icones a direita."""
    yc = botoes.BARRA_KINDLE_H // 2 + 2
    x = MARGEM
    _texto_c(c, x, yc, "KINDLE", NEG, 26, ESCURO)
    x += int(c.medir("KINDLE", NEG, 26)) + 18
    if not kv:
        _texto_c(c, x, yc, "sem dados", REG, 26, MEDIO)
        return
    # direita para a esquerda: bateria, %, wifi, aviao, bt
    xd = c.largura - MARGEM
    pct = kv.get("bateria")
    xd -= 51
    _icone_bateria(c, xd, yc, pct, kv.get("carregando"))
    txt = "n/d" if pct is None else "%d%%" % pct
    xd -= 10
    _texto_c(c, xd, yc, txt, NEG, 26, PRETO, "dir")
    xd -= int(c.medir(txt, NEG, 26)) + 26
    xd -= 42
    _icone_wifi(c, xd, yc, kv.get("wifi"), kv.get("wifi_ok"))
    xd -= 24 + 26
    _icone_aviao(c, xd, yc, bool(kv.get("aviao")))
    bt = bool(kv.get("bt"))
    wbt = 28 if bt and kv.get("bt_conectados") else 17
    xd -= 24 + wbt
    _icone_bt(c, xd, yc, bt, kv.get("bt_conectados"))
    # esquerda: icone de sync + elo
    cor = PRETO if kv.get("tailscale") and not kv.get("falhas") else MEDIO
    _icone_sync(c, x, yc, cor)
    x += 24 + 10
    _texto_c(c, x, yc, _ajustar(c, _texto_elo(kv), REG, 26, max(0, xd - 30 - x)), REG, 26, ESCURO)


_FORMA_NIVEL = {"critico": "falha", "aviso": "aviso", "leve": "parado"}


def _atencao(m, kv):
    """Alertas do painel (motor `alertas`): criticos, avisos e leves, nessa ordem. `m["limiares"]` vale se existir."""
    return alertas.avaliar(m, None, kv)


# --------------------------------------------------------------------- botoes

def _quebrar(c, texto, fonte, tam, larg_max):
    """Quebra por palavras em linhas que cabem em larg_max; None se alguma palavra sozinha nao couber."""
    linhas, atual = [], ""
    for p in _limpar(texto).split():
        t = (atual + " " + p) if atual else p
        if c.medir(t, fonte, tam) <= larg_max:
            atual = t
        elif atual and c.medir(p, fonte, tam) <= larg_max:
            linhas.append(atual)
            atual = p
        else:
            return None
    return linhas + [atual] if atual else linhas


def _botao(c, b, invertido, espessura=2):
    """Desenha exatamente o retangulo do layout: contorno (ou preenchido, se invertido) e rotulo centralizado."""
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    if invertido:
        c.retangulo_arredondado(x, y, w, h, RAIO, PRETO)
    else:
        c.contorno_arredondado(x, y, w, h, RAIO, PRETO, espessura, BRANCO)
    cor = BRANCO if invertido else PRETO
    if h < 110:  # botoes baixos (linha, paginacao, navegacao): uma linha so
        for tam in (34, 26):
            if c.medir(_limpar(b["rotulo"]), NEG, tam) <= w - 16:
                break
        txt = _ajustar(c, b["rotulo"], NEG, tam, w - 12)
        c.texto(x + w // 2, y + (h + _cap(NEG, tam)) // 2, txt, NEG, tam, cor, alinhar="centro")
        return
    tam = 34
    linhas = _quebrar(c, b["rotulo"], NEG, 34, w - 36)
    if linhas is None or len(linhas) > 3:
        tam = 26
        linhas = _quebrar(c, b["rotulo"], NEG, 26, w - 12)
    if linhas is None:
        linhas = [_ajustar(c, b["rotulo"], NEG, 26, w - 12)]
    cap = _cap(NEG, tam)
    passo = cap + 18
    corpo = cap + (len(linhas) - 1) * passo
    original = next((r for cid, r in botoes.COMANDOS if cid == b["id"]), None) if b.get("armado") else None
    cap_p = _cap(REG, 26)
    extra = (cap_p + 16) if original else 0  # sem perder de vista QUAL comando esta armado
    topo = y + (h - corpo - extra) // 2
    if original:
        c.texto(x + w // 2, topo + cap_p, _ajustar(c, original, REG, 26, w - 24), REG, 26, cor, alinhar="centro")
    for i, ln in enumerate(linhas):
        c.texto(x + w // 2, topo + extra + cap + i * passo, ln, NEG, tam, cor, alinhar="centro")


NAV_ICONE = 30
NAV_TAM = 26
_ICONE_NAV = {bid: icone for bid, _rotulo, icone in botoes.NAV}


def _botao_nav(c, b, invertido, icone):
    """Aba da navegacao: icone de 30 px centrado na metade de cima e rotulo SEMPRE em negrito 26 embaixo
    (so o respiro lateral encolhe se faltar largura, nunca a fonte). A aba atual vai invertida."""
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    if invertido:
        c.retangulo_arredondado(x, y, w, h, RAIO, PRETO)
    else:
        c.contorno_arredondado(x, y, w, h, RAIO, PRETO, 2, BRANCO)
    cor = BRANCO if invertido else PRETO
    cap = _cap(NEG, NAV_TAM)
    topo = y + (h - (NAV_ICONE + 10 + cap)) // 2  # icone, 10 px de folga e o rotulo, centrados juntos
    if icone:
        c.icone(x + (w - NAV_ICONE) // 2, topo, icone, NAV_ICONE, cor)
    txt = _ajustar(c, b["rotulo"], NEG, NAV_TAM, w - 4)
    c.texto(x + w // 2, topo + NAV_ICONE + 10 + cap, txt, NEG, NAV_TAM, cor, alinhar="centro")


def _desenhar_botoes(c, pagina, armado, p, itens, modo=None):
    modo = perfis.modo_valido(modo)
    for b in botoes.layout(pagina, armado, c.largura, c.altura, p, itens, modo):
        if not b.get("visivel", True):  # so existe para o toque (/botoes.txt)
            continue
        if b["tipo"] == "local" and b["id"].startswith("pagina:"):
            _botao_nav(c, b, b["id"] == "pagina:" + pagina, _ICONE_NAV.get(b["id"]))
        elif b["id"].startswith("modo:"):
            _botao(c, b, b["id"] == "modo:" + modo)
        else:
            _botao(c, b, b["armado"])


# ----------------------------------------------------------- blocos reutilizaveis

def _info_disco(dk):
    """(rotulo, pct, usado, total, base, parado) de uma entrada de disco; None se nao for um dict."""
    if not isinstance(dk, dict):
        return None
    base = 1024 if dk.get("base") == 1024 else 1000
    return (str(dk.get("rotulo", "?")), _pct(lambda: dk["pct"]), _num(dk.get("usado_b")), _num(dk.get("total_b")),
            base, bool(dk.get("parado")))


def _discos(m):
    d = m.get("discos")
    return [i for i in (_info_disco(x) for x in d) if i] if isinstance(d, list) else []


def _linha_barra(c, x, yc, w, rotulo, pct, valor, rot_w, tam=26, barra_h=18):
    """rotulo | barra fina | pct | valor, centrada verticalmente em yc."""
    _texto_c(c, x, yc, _ajustar(c, rotulo, NEG, tam, rot_w - 8), NEG, tam, ESCURO)
    pct_txt = "n/d" if pct is None else "%d%%" % int(round(pct))
    pw = c.medir("100%", NEG, tam)
    vw = int(c.medir(valor, REG, tam)) if valor else 0
    _texto_c(c, x + w - vw - (16 if vw else 0), yc, pct_txt, NEG, tam, PRETO, "dir")
    if valor:
        _texto_c(c, x + w, yc, valor, REG, tam, ESCURO, "dir")
    bx = x + rot_w
    bw = w - rot_w - int(pw) - vw - 16 - (16 if vw else 0) - 8
    if bw > 40:
        _barra(c, bx, yc - barra_h // 2, bw, barra_h, pct)


def _grupos_io(m):
    """[(titulo, [texto])]: 'NVMe L 12.3 MB/s E 1.2 MB/s' e 'LAN rx 3.4 MB/s tx 0.2 MB/s'."""
    io = m.get("io")
    if not _ok(io):
        return []
    saida = []
    for chave, titulo, a, b, ta, tb in (("discos", "DISCO", "leitura_bps", "escrita_bps", "L", "E"),
                                         ("redes", "REDE", "rx_bps", "tx_bps", "rx", "tx")):
        lista = io.get(chave)
        itens = []
        for it in lista if isinstance(lista, list) else []:
            if isinstance(it, dict):
                itens.append("%s %s %s %s %s" % (_limpar(it.get("rotulo", "?")), ta, formato.taxa(it.get(a)),
                                                tb, formato.taxa(it.get(b))))
        if itens:
            saida.append((titulo, itens))
    return saida


def _linhas_io(c, grupos, w_util):
    """Quebra cada grupo em linhas que cabem: [(titulo|None, texto)]."""
    linhas = []
    for titulo, itens in grupos:
        atual = ""
        primeiro = True
        for it in itens:
            t = (atual + "     " + it) if atual else it
            if atual and c.medir(t, REG, 26) > w_util:
                linhas.append((titulo if primeiro else None, atual))
                primeiro = False
                atual = it
            else:
                atual = t
        if atual:
            linhas.append((titulo if primeiro else None, atual))
    return linhas


IO_LINHA = 40


def _h_io(c, m, w):
    g = _grupos_io(m)
    if not g:
        return 0
    return len(_linhas_io(c, g, w - 2 * PAD - 100)) * IO_LINHA + 2 * 12


def _card_io(c, m, x, y, w, h):
    linhas = _linhas_io(c, _grupos_io(m), w - 2 * PAD - 100)
    _card(c, x, y, w, h)
    for i, (titulo, txt) in enumerate(linhas):
        yc = y + 12 + i * IO_LINHA + IO_LINHA // 2
        if titulo:
            _texto_c(c, x + PAD, yc, titulo, NEG, 26, ESCURO)
        _texto_c(c, x + PAD + 100, yc, _ajustar(c, txt, REG, 26, w - 2 * PAD - 100), REG, 26, PRETO)


def _card_discos(c, discos, x, y, w, titulo=None, linha_h=46):
    """Card com uma linha por disco; devolve a altura usada."""
    topo = 44 if titulo else 0
    h = topo + len(discos) * linha_h + 20
    _card(c, x, y, w, h)
    if titulo:
        c.texto(x + PAD, y + 14 + _cap(NEG, 26), titulo, NEG, 26, ESCURO)
    rot_w = max([c.medir(_limpar(d[0]), NEG, 26) for d in discos] + [60]) + 24
    rot_w = int(min(rot_w, w // 4))
    for i, (rot, pct, usado, total, base, parado) in enumerate(discos):
        yc = y + topo + 10 + i * linha_h + linha_h // 2
        valor = _tamanho(usado, total, base) if total and usado is not None else None
        if valor and parado:
            valor += " · parado"
        _linha_barra(c, x + PAD, yc, w - 2 * PAD, rot, pct, valor, rot_w)
    return h


def _h_discos(discos, titulo=None, linha_h=46):
    return (44 if titulo else 0) + len(discos) * linha_h + 20 if discos else 0


# --------------------------------------------------------------------- Atencao

ATENCAO_LINHA = 46
ATENCAO_TITULO = 48


def _estado_txt(it):
    if it.get("texto"):  # itens que nao sao servicos (bateria do Kindle) trazem o texto pronto
        return _limpar(it["texto"])
    e = it.get("estado")
    base = {"ativo": "ativo", "parado": "parado", "falha": "FALHA"}.get(e, "desconhecido")
    det = _limpar(it.get("detalhe", "") or "")
    if det and (e == "falha" or "/" in det):  # parado/ativo ja dizem tudo; falha e swarm (2/2) ganham o detalhe
        base += "  " + det
    return base


ATENCAO_MAX = 6


def _linhas_atencao(n):
    """Linhas do card para `n` alertas: ate ATENCAO_MAX itens, mais a linha '+N' quando sobram."""
    return n if n <= ATENCAO_MAX else ATENCAO_MAX + 1


def _h_atencao(n):
    """Altura do card: titulo + (linhas de itens | 'Tudo em ordem')."""
    corpo = 64 if n == 0 else _linhas_atencao(n) * ATENCAO_LINHA
    return ATENCAO_TITULO + corpo + 14


def _card_atencao(c, atencao, x, y, w, h):
    _card(c, x, y, w, h)
    n = len(atencao)
    critico = any(a.get("nivel") == "critico" for a in atencao)
    ytit = y + 14 + _cap(NEG, 26)
    if critico:  # cabecalho invertido: branco no preto, dentro do contorno do card
        c.retangulo_arredondado(x + 2, y + 2, w - 4, ATENCAO_TITULO - 2, RAIO - 2, PRETO)
        c.retangulo(x + 2, y + ATENCAO_TITULO // 2, w - 4, ATENCAO_TITULO // 2, PRETO)
    c.texto(x + PAD, ytit, "ATENCAO (%d)" % n if n else "ATENCAO", NEG, 26, BRANCO if critico else ESCURO)
    if not atencao:
        yc = y + ATENCAO_TITULO + 32
        _forma_ok(c, x + PAD, yc - 16, 32, True)
        _texto_c(c, x + PAD + 48, yc, "Tudo em ordem", NEG, 34, PRETO)
        return
    cabem = max(1, (h - ATENCAO_TITULO - 14) // ATENCAO_LINHA)
    mostrar = atencao[:ATENCAO_MAX] if n <= min(ATENCAO_MAX, cabem) else atencao[:max(1, min(ATENCAO_MAX, cabem - 1))]
    for i, it in enumerate(mostrar):
        yc = y + ATENCAO_TITULO + i * ATENCAO_LINHA + ATENCAO_LINHA // 2
        _forma(c, x + PAD, yc - 14, 28, _FORMA_NIVEL.get(it.get("nivel"), "desconhecido"))
        _texto_c(c, x + PAD + 44, yc, _ajustar(c, it.get("texto", "?"), NEG, 34, w - 2 * PAD - 44), NEG, 34, PRETO)
    if n > len(mostrar) and len(mostrar) < cabem:  # com uma linha so, o "+N" ja esta no titulo
        yc = y + ATENCAO_TITULO + len(mostrar) * ATENCAO_LINHA + ATENCAO_LINHA // 2
        _texto_c(c, x + PAD + 44, yc, "+%d" % (n - len(mostrar)), NEG, 26, ESCURO)


def _pct_txt(j):
    """"42%" de uma janela de limite; renovado vale 0%; sem numero -> "n/d"."""
    j = j if isinstance(j, dict) else None
    pct = _num(j.get("pct")) if j else None
    if pct is None:
        return "n/d"
    return "0%" if j.get("renovado") is True else "%d%%" % round(min(100.0, max(0.0, float(pct))))


# --------------------------------------------------------------------- resumo

ICONE_LINHA = 56
FORMA_LINHA = 32
RESUMO_PAD = 8
ESTADO_FORMA = {"critico": "falha", "aviso": "aviso", "leve": "parado", "sem_dados": "desconhecido"}
RANK_NIVEL = {"leve": 1, "aviso": 2, "critico": 3}
# (id, icone, titulo, sistemas de alerta que contam para a linha), na ordem de botoes.LINHAS_RESUMO
_LINHAS = (("atheron", "servidor", "ATHERON", ("atheron",)), ("nas", "nas", "NAS", ("nas",)),
           ("aparelhos", "aparelhos", "APARELHOS", ("aparelhos", "kindle")),
           ("servicos", "servicos", "SERVICOS", ("servicos",)), ("rotinas", "rotinas", "ROTINAS", ("rotinas",)),
           ("claude", "claude", "CLAUDE", ("claude",)), ("github", "github", "GITHUB", ("github",)),
           ("jogos", "jogo", "JOGOS", ("jogos",)))
SEM_DADOS = "sem dados"
SEP = "  \u00b7  "
GRUPOS_RESUMO = ("host", "docker", "incus", "ragnarok")


def _pior_nivel(lista, sistemas):
    """Pior nivel (critico > aviso > leve) dos alertas desses sistemas; None se nao houver."""
    pior = None
    for a in lista if isinstance(lista, list) else []:
        if not isinstance(a, dict) or not isinstance(a.get("sistema"), str) or not isinstance(a.get("nivel"), str):
            continue
        if a["sistema"] in sistemas and RANK_NIVEL.get(a["nivel"], 0) > RANK_NIVEL.get(pior, 0):
            pior = a["nivel"]
    return pior


def _d(v):
    return v if isinstance(v, dict) else {}


def _p(v):
    """'42%' de um numero (limitado a 0..100); None se nao for numero."""
    v = _num(v)
    return None if v is None else "%d%%" % round(min(100.0, max(0.0, float(v))))


def _disco_raiz(dk):
    return isinstance(dk, dict) and (dk.get("caminho") == "/" or dk.get("rotulo") == "/")


def _l_atheron(m, kv, itens):
    partes = []
    for rot, v in (("CPU", _d(m.get("cpu")).get("pct")), ("RAM", _d(m.get("ram")).get("pct"))):
        if _p(v):
            partes.append("%s %s" % (rot, _p(v)))
    det = []
    tc = _d(m.get("temp_cpu"))
    if _ok(tc) and _num(tc.get("c")) is not None:
        det.append("%d C" % round(tc["c"]))
    raiz = next((d for d in m.get("discos") if _disco_raiz(d)), None) if isinstance(m.get("discos"), list) else None
    if raiz and _p(raiz.get("pct")):
        det.append("/ " + _p(raiz["pct"]))
    if coletores.gpu_desativada(m.get("gpu")):
        det.append("GPU desativada")
    return "  ".join(partes), SEP.join(det), bool(partes or det)


def _rotulos_nas(infos):
    """Rotulo de cada disco na linha NAS: sem o prefixo "NAS " (o titulo ja diz), salvo se colidir com outro."""
    originais = [_limpar(i[0]) for i in infos]
    cand = [r[4:].strip() if r.startswith("NAS ") and r[4:].strip() else r for r in originais]
    saida = []
    for k, (orig, novo) in enumerate(zip(originais, cand)):
        outros = [o for j, o in enumerate(originais) if j != k] + [n for j, n in enumerate(cand) if j != k]
        saida.append(novo if novo == orig or novo not in outros else orig)
    return saida


def _l_nas(m, kv, itens):
    discos = [d for d in (m.get("discos") if isinstance(m.get("discos"), list) else []) if isinstance(d, dict)
              and not _disco_raiz(d) and "erro" not in d]
    infos = [i for i in (_info_disco(d) for d in discos) if i and i[1] is not None]
    rots = _rotulos_nas(infos)
    valor = "  ".join("%s %s" % (r, _p(i[1])) for r, i in zip(rots, infos))
    det = ""
    if infos:
        k = max(range(len(infos)), key=lambda j: infos[j][1])
        _, _, usado, total, base, _ = infos[k]
        if usado is not None and total:
            det = "%s  %s" % (rots[k], _tamanho(usado, total, base))
    return valor, det, bool(infos)


INVENTARIO_SEM = "inventario sem atualizar"
_ICONE_APARELHO_PADRAO = "aparelhos"


def _fonte_itens(m, chave):
    """(inventario_ok, itens) de m[chave] ("aparelhos" ou "rotinas"); None se a chave falta ou o bloco e invalido.
    Itens que nao sao dict somem. Com inventario velho/ausente o chamador mostra "sem dados"."""
    b = m.get(chave) if isinstance(m, dict) else None
    if not isinstance(b, dict) or not isinstance(b.get("itens"), list):
        return None
    return b.get("inventario") == "ok", [i for i in b["itens"] if isinstance(i, dict)]


def _ha_txt(minutos):
    """"ha 5 min" (< 90 min), "ha 3 h" (< 48 h) ou "ha 2 d"; "" se nao for numero valido (>= 0)."""
    n = _num(minutos)
    if n is None or n < 0 or n > 10 ** 8:
        return ""
    n = int(n)
    if n < 90:
        return "ha %d min" % max(1, n)
    return "ha %d h" % (n // 60) if n < 48 * 60 else "ha %d d" % (n // 1440)


def _estado_aparelho(it):
    """(estado da forma, texto secundario) de um aparelho: online -> direto/relay; offline -> "offline ha N min"
    (falha se passou de `alerta_offline_min`); sem dado -> ?."""
    online = it.get("online")
    if online is True:
        con = it.get("conexao")
        return "ativo", con if con in ("direto", "relay") else "online"
    if online is False:
        off, alvo = _num(it.get("offline_min")), _num(it.get("alerta_offline_min"))
        ha = _ha_txt(off)
        txt = "offline " + ha if ha else "offline"
        if alvo is not None and alvo > 0 and off is not None and off >= alvo:
            return "falha", txt
        return "parado", txt
    return None, "sem dado"


def _estado_rotina(it):
    """(estado da forma, texto secundario) de uma rotina: ok -> "ha N h"; falha; atrasada (aviso); desconhecida (?)."""
    r = it.get("resultado")
    if r == "falha":
        return "falha", "falhou"
    if r != "ok":
        return None, "sem dado"
    if it.get("atrasada") is True:
        return "aviso", "atrasada"
    horas = _num(it.get("idade_h"))
    return "ativo", _ha_txt(None if horas is None else horas * 60)


_GRAVIDADE = {"falha": 3, "aviso": 2, "parado": 2, None: 1, "ativo": 0}


def _cortar(itens, n_max, estado):
    """(visiveis, resto): ate `n_max - 1` itens mais a linha "+N" quando nao cabem todos; no corte os piores primeiro
    (estavel), para o que pede atencao nunca ficar de fora."""
    if len(itens) <= n_max:
        return itens, 0
    ordem = sorted(itens, key=lambda i: -_GRAVIDADE.get(estado(i)[0], 1))
    vis = ordem[:max(0, n_max - 1)]
    return vis, len(itens) - len(vis)


def _rotulo(it, tam=40):
    r = _limpar(it.get("rotulo")) if isinstance(it.get("rotulo"), str) else ""
    return r.strip()[:tam] or "?"


def _l_aparelhos(m, kv, itens):
    baterias = []
    bat = _p(_d(kv).get("bateria"))
    if bat:
        baterias.append("Kindle " + bat)
    s10 = _d(m.get("s10"))
    nivel = _p(_d(s10.get("bateria")).get("nivel")) if _ok(s10) else None
    if nivel:
        baterias.append("S10 " + nivel)
    baterias = "  ".join(baterias)
    fonte = _fonte_itens(m, "aparelhos")
    if fonte is None or (fonte[0] and not fonte[1]):
        return "", baterias, False
    ok, its = fonte
    if not ok:
        return SEM_DADOS, INVENTARIO_SEM, True  # contagem de um inventario parado parece tudo caido
    off = [_rotulo(i) for i in its if i.get("online") is False]
    sem = sum(1 for i in its if i.get("online") not in (True, False))
    if off:
        det = "offline: " + ", ".join(off)
    else:
        det = "  ".join(x for x in (("%d sem dado" % sem) if sem else "", baterias) if x)
    return "%d de %d online" % (sum(1 for i in its if i.get("online") is True), len(its)), det, True


def _l_servicos(m, kv, itens):
    if _d(m.get("servicos_kindle")).get("inventario") in ("velho", "ausente"):
        return SEM_DADOS, "inventario sem atualizar", True  # contagem de um inventario parado parece tudo caido
    itens = [i for i in itens if isinstance(i, dict)] if isinstance(itens, list) else []
    if not itens:
        return "", "", False
    r = servicos.resumo(itens)
    cont = {}
    for i in itens:
        t = cont.setdefault(i.get("grupo"), [0, 0])
        t[1] += 1
        t[0] += 1 if i.get("estado") == "ativo" else 0
    det = "  ".join("%s %d/%d" % (g, cont[g][0], cont[g][1]) for g in GRUPOS_RESUMO if g in cont)
    return "%d de %d ok" % (r["ok"], r["total"]), det, True


def _plural(n, um, varios):
    return "%d %s" % (n, um if n == 1 else varios)


def _sessoes_txt(total, esperando):
    """"3 sessoes, 1 esperando" (singular com 1)."""
    return "%s, %d esperando" % (_plural(total, "sessao", "sessoes"), esperando)


def _sessoes_dados(cl):
    """(itens, total, esperando) de cl["sessoes"] (ate SESSOES_MAX itens, mais recentes primeiro), ou None se a chave
    falta, e "n/d" ou o bloco e invalido."""
    s = _d(cl).get("sessoes")
    if not _ok(s) or not isinstance(s.get("itens"), list):
        return None
    itens = [i for i in s["itens"] if isinstance(i, dict)][:SESSOES_MAX]
    total, esp = _num(s.get("total")), _num(s.get("esperando"))
    total = int(total) if total is not None and total >= len(itens) else len(itens)
    contados = sum(1 for i in itens if i.get("estado") == "esperando")
    esp = int(esp) if esp is not None and 0 <= esp <= total else contados
    return itens, total, esp


def _l_github(m, kv, itens):
    d = _github_dados(m.get("github"), PRS_MAX)
    if d is None:
        return "", "", False
    valor = _plural(d["abertos"], "PR aberto", "PRs abertos")
    falha = next((i for i in d["ci_ruins"] if i.get("estado") == "falha"), None)
    if falha is not None:
        det = "CI falhou: " + _repo(falha)
    elif d["ci_ruins"]:
        det = "CI pendente: " + _repo(d["ci_ruins"][0])
    else:
        det = "CI ok" if d["ci_ok"] else ""
    return valor, det, True


ROTINAS_SEM = "rotinas sem dado"


def _todas_desconhecidas(itens):
    """True se ha rotinas e todas estao `desconhecido` (o systemctl falhou: nada de verde por falta de erro)."""
    return bool(itens) and all(i.get("resultado") not in ("ok", "falha") for i in itens)


def _rotina_ok(it):
    return it.get("resultado") == "ok" and it.get("atrasada") is not True


def _unidades_falhas(m):
    """(n, nomes) das unidades systemd em falha de m["rotinas"]; (0, []) se ausente ou invalido."""
    u = _d(_d(m.get("rotinas")).get("unidades_falhas"))
    n = _num(u.get("n"))
    nomes = u.get("nomes")
    nomes = [_limpar(x).strip() for x in nomes if isinstance(x, str)] if isinstance(nomes, list) else []
    return (int(n) if n is not None and n > 0 else 0), [x for x in nomes if x][:5]


def _l_rotinas(m, kv, itens):
    fonte = _fonte_itens(m, "rotinas")
    if fonte is None or (fonte[0] and not fonte[1]):
        return "", "", False
    ok, its = fonte
    if not ok:
        return SEM_DADOS, INVENTARIO_SEM, True
    if _todas_desconhecidas(its):
        return SEM_DADOS, ROTINAS_SEM, None  # None: "sem dados" mesmo com o aviso do motor (ver _linhas_resumo)
    valor = "%d de %d ok" % (sum(1 for i in its if _rotina_ok(i)), len(its))
    prob = next((i for i in its if not _rotina_ok(i)), None)
    if prob is not None:
        return valor, "%s %s" % (_rotulo(prob), _estado_rotina(prob)[1]), True
    n, _ = _unidades_falhas(m)
    if n:
        return valor, "%d %s em falha" % (n, "unidade" if n == 1 else "unidades"), True
    datadas = [i for i in its if _num(i.get("ultima_em")) is not None]
    rec = max(datadas, key=lambda i: _num(i["ultima_em"]), default=None)
    if rec is None:
        return valor, "", True
    return valor, ("%s %s" % (_rotulo(rec), _estado_rotina(rec)[1])).strip(), True


def _l_claude(m, kv, itens):
    cl = _d(m.get("claude"))
    lim = cl.get("limites")
    if not _ok(lim):
        return "", "", False
    valor = "5h %s  sem %s" % (_pct_txt(lim.get("cinco_horas")), _pct_txt(lim.get("semanal")))
    cinco = _d(lim.get("cinco_horas"))
    det = ""
    ses = _sessoes_dados(cl)
    if ses is not None and ses[1] > 0:
        return valor, _sessoes_txt(ses[1], ses[2]), True
    if cinco.get("renovado") is not True and cinco.get("volta_em") is not None:
        agora, tz = _agora(m)
        det = "5h " + _volta_txt(cinco["volta_em"], agora, tz)
        det = det if det != "5h " else ""
    return valor, det, True


AMP_ESTADOS = ("rodando", "parado", "iniciando", "falha", "outro")
AMP_MAX = 16


def _portas_lista(m):
    p = m.get("portas")
    return [x for x in p if isinstance(x, dict)] if isinstance(p, list) else []


def _item_amp(it):
    """Instancia do bloco `amp` ja normalizada para o desenho (texto limpo, estado conhecido, contagens int)."""
    nome = _limpar(it.get("nome")).strip()[:24] if isinstance(it.get("nome"), str) else ""
    modulo = _limpar(it.get("modulo")).strip()[:16] if isinstance(it.get("modulo"), str) else ""
    estado = it.get("estado") if it.get("estado") in AMP_ESTADOS else "outro"
    jog, mx = _num(it.get("jogadores")), _num(it.get("max"))
    jog = int(jog) if estado == "rodando" and jog is not None and jog >= 0 else None
    mx = int(mx) if jog is not None and mx is not None and mx >= 0 else None
    return {"nome": nome or "?", "modulo": modulo, "estado": estado, "jogadores": jog, "max": mx}


def _amp_dados(m):
    """(situacao, itens, bloco) do AMP em `m`. situacao: None = AMP fora da tela (sem a chave, credencial ausente/
    desligado, arquivo ausente: "simplesmente nao aparece"); "sem_dados" = ligado mas sem coleta valida (erro ou
    inventario velho: nunca verde); "ok". `itens` so existe em "ok": ligadas primeiro, depois por nome."""
    b = m.get("amp") if isinstance(m, dict) else None
    if not isinstance(b, dict) or b.get("ativo") is not True:
        return None, [], b if isinstance(b, dict) else {}
    erro = b.get("erro")
    if b.get("inventario") != "ok" or (isinstance(erro, str) and erro.strip()) or not isinstance(b.get("instancias"), list):
        return "sem_dados", [], b
    itens = [_item_amp(i) for i in b["instancias"] if isinstance(i, dict)][:AMP_MAX]
    itens.sort(key=lambda i: (i["estado"] != "rodando", i["nome"].lower()))
    return "ok", itens, b


def _contagem_amp(it):
    """"2/20", "2" ou "" (sem numero) de uma instancia rodando."""
    if it["jogadores"] is None:
        return ""
    return "%d/%d" % (it["jogadores"], it["max"]) if it["max"] is not None else "%d" % it["jogadores"]


def _l_jogos(m, kv, itens):
    """Linha JOGOS: valor = "Ragnarok 0  Minecraft 2/20" (so o que esta ligado, ligadas primeiro; o desenho corta com
    "..."); detalhe = estado do Ragnarok ("MAP fechada" ou "login ok char ok map ok") seguido do que nao esta ligado
    ("iniciando: ...", "falha: ...", "parado: ..."). O AMP so entra se estiver ligado (credencial); ligado sem dado vira
    "AMP sem dados" e a forma "?", a menos que o Ragnarok tenha porta fechada (a forma e a dele). Instancia parada nao
    muda a forma da linha."""
    rag = m.get("ragnarok")
    partes = []
    if _ok(rag) and _num(rag.get("jogadores")) is not None:
        partes.append("Ragnarok %d%s" % (int(rag["jogadores"]), "  parado" if rag.get("parado") else ""))
    situacao, amp_itens, _ = _amp_dados(m)
    for it in amp_itens:
        if it["estado"] == "rodando":
            partes.append(("%s %s" % (it["nome"], _contagem_amp(it))).strip())
    valor = "  ".join(partes)
    if not valor and situacao == "ok":
        valor = "nenhum ligado"
    portas = _portas_lista(m)
    fechadas = [_limpar(p.get("rotulo", "?")) for p in portas if p.get("aberto") is False]
    det = []
    if fechadas:
        det.append("%s %s" % (", ".join(fechadas), "fechada" if len(fechadas) == 1 else "fechadas"))
    elif any(p.get("aberto") is True for p in portas):
        det.append(" ".join("%s ok" % _limpar(p.get("rotulo", "?")).lower() for p in portas if p.get("aberto") is True))
    if situacao == "sem_dados":
        det.append("AMP sem dados")
    for estado in ("iniciando", "falha", "outro", "parado"):
        nomes = [it["nome"] for it in amp_itens if it["estado"] == estado]
        if nomes:
            det.append("%s: %s" % (estado, ", ".join(nomes)))
    detalhe = SEP.join(det)
    if situacao == "sem_dados" and not fechadas:
        return valor, detalhe, None  # "?": o aviso leve "AMP sem dados" do motor nao troca a forma (so uma porta fechada)
    return valor, detalhe, bool(valor or detalhe)


_CONSTRUTORES = {"atheron": _l_atheron, "nas": _l_nas, "aparelhos": _l_aparelhos, "servicos": _l_servicos,
                 "rotinas": _l_rotinas, "claude": _l_claude, "github": _l_github, "jogos": _l_jogos}


_LINHAS_AVISADAS = set()  # (linha, tipo do erro) ja registrados: a tela redesenha a cada segundo


def _avisar_linha(lid, exc):
    """Registra no stderr (journal) o erro de um construtor de linha, uma vez por linha e tipo de erro."""
    chave = (lid, type(exc).__name__)
    if chave in _LINHAS_AVISADAS:
        return
    _LINHAS_AVISADAS.add(chave)
    print("render_png: linha %s do resumo sem dados (%s: %s)" % (lid, type(exc).__name__, exc), file=sys.stderr)


def _linhas_resumo(m, itens, kv, alertas):
    """As 8 linhas da tela inicial (ordem de botoes.LINHAS_RESUMO): {"id","icone","titulo","valor","detalhe","estado"}.
    Pura e tolerante: `m`, `itens`, `kv` ou `alertas` com tipo errado so deixam a linha em "sem dados".
    `estado` = pior nivel dos alertas da linha, "ok", ou "sem_dados" (sem fonte e sem alerta)."""
    m = m if isinstance(m, dict) else {}
    saida = []
    for lid, icone, titulo, sistemas in _LINHAS:
        try:
            valor, detalhe, tem = _CONSTRUTORES[lid](m, kv, itens)
        except Exception as e:
            _avisar_linha(lid, e)
            valor, detalhe, tem = "", "", False
        pior = _pior_nivel(alertas, sistemas)
        if tem is None and pior != "critico":  # fonte inteira sem dado: o aviso "sem dados" nao muda a forma "?"
            pior = None
        estado = pior or ("ok" if tem else "sem_dados")
        saida.append({"id": lid, "icone": icone, "titulo": titulo, "valor": valor or SEM_DADOS,
                      "detalhe": detalhe, "estado": estado})
    return saida


def _linha_sistema(c, caixa, linha):
    """Uma linha da tela inicial dentro de `caixa` ({x,y,w,h}): icone 56 px, titulo + valor na 1a linha de texto,
    detalhe na 2a e, so se o estado nao for ok, a forma dele na direita."""
    x, y, w, h = caixa["x"], caixa["y"], caixa["w"], caixa["h"]
    estado = linha.get("estado")
    sem = linha.get("valor") == SEM_DADOS
    c.icone(x + RESUMO_PAD, y + (h - ICONE_LINHA) // 2, linha.get("icone", ""), ICONE_LINHA, PRETO)
    xt = x + RESUMO_PAD + ICONE_LINHA + 20
    xv = xt + int(c.medir("APARELHOS", NEG, 26)) + 32  # coluna dos valores: igual em todas as linhas
    fim = x + w - RESUMO_PAD - FORMA_LINHA - 16
    if estado in ESTADO_FORMA and estado != "ok":
        _forma(c, x + w - RESUMO_PAD - FORMA_LINHA, y + (h - FORMA_LINHA) // 2, FORMA_LINHA, ESTADO_FORMA[estado])
    cap_v, cap_d = _cap(NEG, 34), _cap(REG, 26)
    topo = y + (h - (cap_v + 16 + cap_d)) // 2
    base1 = topo + cap_v
    ajustar = _ajustar_itens if linha.get("id") == "jogos" else _ajustar  # JOGOS lista nomes: so corta entre itens
    c.texto(xt, base1, _ajustar(c, linha.get("titulo", ""), NEG, 26, xv - xt - 8), NEG, 26, ESCURO)
    c.texto(xv, base1, ajustar(c, linha.get("valor", ""), NEG, 34, fim - xv), NEG, 34, MEDIO if sem else PRETO)
    det = linha.get("detalhe") or ""
    if det:
        c.texto(xv, base1 + 16 + cap_d, ajustar(c, det, REG, 26, fim - xv), REG, 26, ESCURO)


FAIXA_MIN = 150  # sobra minima (px) entre o fim do ATENCAO e o fim da caixa para desenhar o HISTORICO
FAIXA_MAX = 230


def _faixa_historico(c, hist, caixa, h_atencao):
    """Faixa HISTORICO (CPU e RAM) no vao que sobra abaixo do ATENCAO. Nao e botao e nao mexe na geometria."""
    fim = caixa["y"] + caixa["h"]
    ini = caixa["y"] + h_atencao
    if fim - ini < FAIXA_MIN or not isinstance(hist, dict):
        return
    series = _series_historico(hist, (("CPU", "cpu"), ("RAM", "ram")))
    if not series:
        return
    y = ini + GAP
    h = min(FAIXA_MAX, fim - y - botoes.LINHA_RESUMO_GAP)
    _card_historico(c, hist, series, caixa["x"], y, caixa["w"], h, titulo_h=44)


def _desenhar_resumo(c, m, hist, itens, kv=None):
    """Tela inicial so com excecoes: cartao ATENCAO no alto (so a altura que precisa) e uma linha por sistema."""
    geo = botoes.geometria_resumo(c.largura, c.altura)
    atencao = _atencao(m, kv)
    caixa = geo["atencao"]
    h = min(_h_atencao(len(atencao)), caixa["h"] - botoes.LINHA_RESUMO_GAP)
    if h >= botoes.ATENCAO_MIN_H:  # tela baixa demais (so fora do Kindle): sem espaco para o cartao
        _card_atencao(c, atencao, caixa["x"], caixa["y"], caixa["w"], h)
        _faixa_historico(c, hist, caixa, h)
    linhas = _linhas_resumo(m, itens, kv, atencao)
    ultima = len(linhas) - 1
    for i, (cx, ln) in enumerate(zip(geo["linhas"], linhas)):
        _linha_sistema(c, cx, ln)
        if i != ultima:  # fio fino claro no fim da caixa, no lugar de um contorno em cada linha
            c.retangulo(cx["x"], cx["y"] + cx["h"] - 2, cx["w"], 2, TRILHO)


# ------------------------------------------------------------------- servicos

def _desenhar_servicos(c, m, itens, p):
    geo = botoes.geometria_servicos(itens, c.largura, c.altura, p)
    bw, sw = botoes.medidas_linha(c.largura)
    w = c.largura - 2 * MARGEM
    if geo["barra"]:
        b = geo["barra"]
        _texto_c(c, MARGEM, b["y"] + b["h"] // 2, "Pagina %d/%d" % (geo["p"], geo["paginas"]), NEG, 34, PRETO)
    if not itens:
        _texto_c(c, MARGEM, botoes.TOPO + 40, "nenhum servico configurado", REG, 34, ESCURO)
        return
    por_grupo = {}
    for it in itens:
        g = por_grupo.setdefault(it.get("grupo"), [0, 0])
        g[1] += 1
        g[0] += 1 if it.get("estado") == "ativo" else 0
    for e in geo["entradas"]:
        y = e["y"]
        if e["tipo"] == "cab":
            tit = servicos.TITULOS_GRUPO.get(e["grupo"], str(e["grupo"]).upper())
            base = y + 12 + _cap(NEG, 26)
            c.texto(MARGEM, base, tit, NEG, 26, ESCURO)
            a, t = por_grupo.get(e["grupo"], [0, 0])
            c.texto(MARGEM + w, base, "%d de %d ativos" % (a, t), REG, 26, ESCURO, alinhar="dir")
            c.retangulo(MARGEM, y + e["h"] - 8, w, 2, CLARO)
            continue
        it, h = e["item"], e["h"]
        alt = botoes.BOTAO_H if h >= servicos.ROW_H else h  # altura util da linha (sem o espaco de 16)
        yc = y + alt // 2
        est = it.get("estado")
        if est == "falha":
            c.retangulo_arredondado(MARGEM, y, w, alt, 8, TRILHO)
        _forma(c, MARGEM + 10, yc - 16, 32, est)
        # coluna de estado fixa: alinha entre linhas com 2, 1 ou nenhum botao
        x_estado = MARGEM + w - (bw * 2 + GAP) - GAP - sw
        txt = _estado_txt(it)
        if c.medir(txt, NEG if est == "falha" else REG, 26) > sw - 8:
            txt = {"falha": "FALHA", "desconhecido": "desconhecido"}.get(est, txt.split("  ")[0])
        c.texto(x_estado, yc + _cap(REG, 26) // 2, txt, NEG if est == "falha" else REG, 26,
                PRETO if est != "desconhecido" else MEDIO)
        lx = MARGEM + 10 + 32 + 16
        lw = x_estado - lx - 16
        rot = _limpar(it.get("rotulo", "?"))
        tam = 34 if c.medir(rot, NEG, 34) <= lw else 26
        cor = PRETO if est != "desconhecido" else ESCURO
        c.texto(lx, yc + _cap(NEG, tam) // 2, _ajustar(c, rot, NEG, tam, lw), NEG, tam, cor)
        c.retangulo(MARGEM, y + h - (9 if h >= servicos.ROW_H else 2), w, 2, TRILHO)


# -------------------------------------------------------------------- detalhes

def _kv(c, x, yc, w, chave, valor, tam=34):
    _texto_c(c, x, yc, chave, NEG, 26, ESCURO)
    kw = int(c.medir(chave, NEG, 26)) + 14
    _texto_c(c, x + kw, yc, _ajustar(c, valor, NEG, tam, w - kw), NEG, tam, PRETO)


H_ROTINAS = 44 + 60  # sem dados: titulo + uma linha
ROTINA_LINHA = 46
ROTINA_TOPO = 50  # do alto do cartao ate a 1a linha (o titulo ocupa 44 e sobra um respiro)
ROTINAS_MAX = 8  # linhas de rotina no cartao; acima disso, as piores primeiro e "+N"


def _rotinas_visiveis(rot):
    """(visiveis, resto, unidades_n, nomes) do cartao ROTINAS, ou None se for "sem dados" (sem bloco, lista vazia ou
    inventario velho/ausente)."""
    fonte = _fonte_itens({"rotinas": rot}, "rotinas")
    if fonte is None or not fonte[0] or not fonte[1] or _todas_desconhecidas(fonte[1]):
        return None
    n, nomes = _unidades_falhas({"rotinas": rot})
    vis, resto = _cortar(fonte[1], ROTINAS_MAX - (1 if n else 0), _estado_rotina)
    return vis, resto, n, nomes


def _h_rotinas(rot):
    d = _rotinas_visiveis(rot)
    if d is None:
        return H_ROTINAS
    vis, resto, n, _ = d
    return ROTINA_TOPO + (len(vis) + (1 if resto else 0) + (1 if n else 0)) * ROTINA_LINHA + 20


def _card_rotinas(c, rot, x, y, w, h):
    """Cartao ROTINAS da pagina Sistema: forma, rotulo e "ha N h"/"falhou"/"atrasada" por rotina, mais a linha das
    unidades systemd em falha. Sem dados (ou inventario velho): "sem dados" cinza."""
    _card(c, x, y, w, h)
    c.texto(x + PAD, y + 14 + _cap(NEG, 26), "ROTINAS", NEG, 26, ESCURO)
    d = _rotinas_visiveis(rot)
    if d is None:
        _texto_c(c, x + PAD, y + 44 + 30, SEM_DADOS, NEG, 34, MEDIO)
        fonte = _fonte_itens({"rotinas": rot}, "rotinas")
        if fonte not in (None, (True, [])):
            sem = ROTINAS_SEM if fonte[0] else INVENTARIO_SEM
            _texto_c(c, x + w - PAD, y + 44 + 30, sem, REG, 26, ESCURO, "dir")
        return
    vis, resto, n, nomes = d
    for i, it in enumerate(vis):
        yc = y + ROTINA_TOPO + i * ROTINA_LINHA + ROTINA_LINHA // 2
        forma, txt = _estado_rotina(it)
        if forma in ("falha", "aviso"):
            c.retangulo_arredondado(x + 8, yc - ROTINA_LINHA // 2 + 2, w - 16, ROTINA_LINHA - 4, 8, TRILHO)
        _forma(c, x + PAD, yc - 14, 28, forma)
        sem = forma is None
        _texto_c(c, x + w - PAD, yc, txt, NEG if forma in ("falha", "aviso") else REG, 26, MEDIO if sem else ESCURO, "dir")
        tw = int(c.medir(txt, NEG, 26)) + 24
        _texto_c(c, x + PAD + 44, yc, _ajustar(c, _rotulo(it), NEG, 34, w - 2 * PAD - 44 - tw), NEG, 34,
                 ESCURO if sem else PRETO)
    linha = len(vis)
    if resto:
        _texto_c(c, x + PAD + 44, y + ROTINA_TOPO + linha * ROTINA_LINHA + ROTINA_LINHA // 2, "+%d" % resto, NEG, 26, ESCURO)
        linha += 1
    if n:
        yc = y + ROTINA_TOPO + linha * ROTINA_LINHA + ROTINA_LINHA // 2
        _forma(c, x + PAD, yc - 14, 28, "falha")
        txt = "%d %s em falha" % (n, "unidade" if n == 1 else "unidades") + (": " + ", ".join(nomes) if nomes else "")
        _texto_c(c, x + PAD + 44, yc, _ajustar(c, txt, NEG, 26, w - 2 * PAD - 44), NEG, 26, PRETO)


def _series_historico(hist, pares):
    """[(rotulo, serie)] das chaves de `hist` com pelo menos 4 amostras validas."""
    return [(r, hist.get(k)) for r, k in pares
            if isinstance(hist.get(k), list) and sum(1 for v in hist[k] if _num(v) is not None) >= 4]


def _card_historico(c, hist, series, x, y, w, h, titulo_h=52):
    """Cartao HISTORICO: uma sparkline por serie, com rotulo a esquerda e o valor atual a direita. A altura de cada
    linha sai de `h` (76 px na pagina Sistema)."""
    _card(c, x, y, w, h)
    c.texto(x + PAD, y + 14 + _cap(NEG, 26), "HISTORICO", NEG, 26, ESCURO)
    intervalo = _num(hist.get("intervalo_s"))
    if intervalo is None or intervalo <= 0:
        intervalo = 15
    minutos = int(round(len(series[0][1]) * intervalo / 60.0))
    c.texto(x + w - PAD, y + 14 + _cap(NEG, 26), "ultimos %d min" % minutos if minutos else "", REG, 26,
            ESCURO, alinhar="dir")
    lh = (h - titulo_h - 8) // len(series)
    pad = 8 if lh >= 70 else 4  # linhas baixas (faixa da tela inicial) aproveitam mais a altura
    for i, (rot, serie) in enumerate(series):
        top = y + titulo_h + i * lh
        _texto_c(c, x + PAD, top + (lh - pad) // 2, rot, NEG, 26, ESCURO)
        ultimo = next((v for v in reversed(serie) if _num(v) is not None), None)
        _texto_c(c, x + w - PAD, top + (lh - pad) // 2, "%d%%" % int(round(min(100.0, max(0.0, ultimo)))), NEG, 34, PRETO, "dir")
        _sparkline(c, x + PAD + 90, top + lh - pad, w - 2 * PAD - 90 - 90, lh - 2 * pad, serie)


def _blocos_detalhes(c, m, itens, w, hist):
    """[(altura, desenhar(c, x, y, h))] da pagina detalhes, de cima para baixo."""
    blocos = []
    discos = _discos(m)
    if discos:
        blocos.append((_h_discos(discos, "DISCOS"),
                       lambda c, x, y, h: _card_discos(c, discos, x, y, w, "DISCOS")))
    # memoria
    linhas = []
    ram, swap, gpu = m.get("ram"), m.get("swap"), m.get("gpu")
    if _ok(ram) and _num(ram.get("total_kb")):
        linhas.append(("RAM", _pct(lambda: ram["pct"]), _tamanho(ram.get("usado_kb", 0) * 1024, ram["total_kb"] * 1024, 1024)))
    if _ok(swap):
        if swap.get("total_kb") == 0:
            linhas.append(("SWAP", None, "sem swap"))
        elif _num(swap.get("total_kb")):
            linhas.append(("SWAP", _pct(lambda: swap["pct"]),
                           _tamanho(swap.get("usado_kb", 0) * 1024, swap["total_kb"] * 1024, 1024)))
    if _ok(gpu) and not coletores.gpu_desativada(gpu) and _num(gpu.get("mem_usada_mb")) is not None and gpu.get("mem_total_mb"):
        linhas.append(("VRAM", gpu["mem_usada_mb"] * 100.0 / gpu["mem_total_mb"],
                       _tamanho(gpu["mem_usada_mb"] * 10 ** 6, gpu["mem_total_mb"] * 10 ** 6)))
    elif gpu is not None and coletores.gpu_desativada(gpu):
        linhas.append(("GPU", None, "desativada"))
    if linhas:
        def mem(c, x, y, h):
            _card(c, x, y, w, h)
            c.texto(x + PAD, y + 14 + _cap(NEG, 26), "MEMORIA", NEG, 26, ESCURO)
            for i, (rot, pct, val) in enumerate(linhas):
                _linha_barra(c, x + PAD, y + 44 + 10 + i * 46 + 23, w - 2 * PAD, rot, pct, val, 100)
        blocos.append((44 + len(linhas) * 46 + 20, mem))
    h_io = _h_io(c, m, w)
    if h_io:
        blocos.append((h_io, lambda c, x, y, h: _card_io(c, m, x, y, w, h)))
    # sistema: temperaturas, carga, uptime
    kvs = []
    try:
        if _ok(m.get("temp_cpu")):
            kvs.append(("TEMP CPU", "%d°C" % int(round(m["temp_cpu"]["c"]))))
        if _ok(gpu) and _num(gpu.get("temp_c")) is not None:
            kvs.append(("TEMP GPU", "%d°C" % int(round(gpu["temp_c"]))))
    except Exception:
        pass
    try:
        cg = m["carga"]
        kvs.append(("CARGA", "%.2f  %.2f  %.2f" % (cg["1m"], cg["5m"], cg["15m"])))
    except Exception:
        pass
    try:
        kvs.append(("UP", _uptime(m["uptime"]["segundos"])))
    except Exception:
        pass
    if kvs:
        nl = -(-len(kvs) // 2)

        def sistema(c, x, y, h):
            _card(c, x, y, w, h)
            cw = (w - 2 * PAD) // 2
            for i, (k, v) in enumerate(kvs):
                _kv(c, x + PAD + (i % 2) * cw, y + 12 + (i // 2) * 48 + 24, cw - 12, k, v)
        blocos.append((nl * 48 + 24, sistema))
    # historico (sparklines de ~15 min)
    series = _series_historico(hist, (("CPU", "cpu"), ("RAM", "ram"), ("GPU", "gpu")))
    if series:
        def historico(c, x, y, h):
            _card_historico(c, hist, series, x, y, w, h)
        historico.descartavel = True  # sem espaco, sai primeiro (antes do ROTINAS, que pode trazer falha)
        blocos.append((52 + len(series) * 76 + 8, historico))
    rot = m.get("rotinas")
    blocos.append((_h_rotinas(rot), lambda c, x, y, h: _card_rotinas(c, rot, x, y, w, h)))
    return blocos


H_KINDLE = 64 + 4 * 48 + 12
H_SEM_DADOS = 64 + 60


def _sim_nao(v, sim, nao):
    return "n/d" if v is None else (sim if v else nao)


def _txt(v):
    """Texto do campo da vista do Kindle; so str nao vazia vale, o resto e None."""
    return v if isinstance(v, str) and v else None


def _campos_kindle(kv):
    """(bateria %, detalhe da bateria, [(rotulo, valor)] de radios, elo, relogio e sincronizacao) da vista do Kindle.
    Campo de tipo errado vira "n/d" (ou some do detalhe da bateria), nunca levanta."""
    det = ["carregando" if kv.get("carregando") else "na bateria"]
    if kv.get("temp_c") is not None:
        t = _num(kv["temp_c"])
        det.append("%d°C" % t if t is not None else "n/d")
    if kv.get("autonomia"):
        det.append(_txt(kv["autonomia"]) or "n/d")
    if kv.get("wifi_ok"):
        w = _num(kv.get("wifi"))
        wifi = "%d/5" % w if w is not None else "conectado"
    else:
        wifi = "desconectado"
    if kv.get("bt") is None:
        bt = "n/d"
    elif not kv["bt"]:
        bt = "desligado"
    else:
        n = _num(kv.get("bt_conectados")) or 0
        bt = "ligado" if n < 1 else "%d conectado%s" % (n, "s" if n > 1 else "")
    elo = _txt(kv.get("tailscale")) or "n/d"
    if kv.get("latencia"):
        elo += " · " + (_txt(kv["latencia"]) or "n/d")
    pares = (("WI-FI", wifi), ("BLUETOOTH", bt),
             ("AVIAO", _sim_nao(kv.get("aviao"), "ligado", "desligado")), ("ELO", elo),
             ("RELOGIO", _txt(kv.get("relogio")) or "n/d"), ("WHISPERSYNC", _txt(kv.get("whispersync")) or "n/d"))
    return kv.get("bateria"), " · ".join(det), pares


def _card_sem_dados(c, x, y, w, h, titulo, icone, detalhe=None, idade_s=None):
    """Cartao de titulo com icone e a linha "sem dados" em cinza (fonte ausente ou parada). `detalhe` fica a direita
    e `idade_s` (fonte velha) vira a idade no titulo."""
    _card(c, x, y, w, h)
    yy = _cabecalho_card(c, x, y, w, titulo, idade_s is not None, idade_s, icone=icone)
    _texto_c(c, x + PAD, yy + 30, SEM_DADOS, NEG, 34, MEDIO)
    if detalhe:
        _texto_c(c, x + w - PAD, yy + 30, detalhe, REG, 26, ESCURO, "dir")


def _card_kindle(c, kv, x, y, w, h):
    """Kindle: BATERIA com barra (como MEMORIA) e mais tres linhas em duas colunas: radios, elo e sincronizacao."""
    if not isinstance(kv, dict):
        return _card_sem_dados(c, x, y, w, h, "Kindle", "leitor")
    _card(c, x, y, w, h)
    yy = _cabecalho_card(c, x, y, w, "Kindle", icone="leitor")
    bat, det, pares = _campos_kindle(kv)
    _linha_barra(c, x + PAD, yy + 24, w - 2 * PAD, "BATERIA", bat, det, 160)
    cw = (w - 2 * PAD) // 2
    for i, (k, v) in enumerate(pares):
        _kv(c, x + PAD + (i % 2) * cw, yy + 48 + (i // 2) * 48 + 24, cw - 16, k, v, tam=26 if len(v) > 14 else 34)


def _card_par(c, par, x, y, w, h):
    _card(c, x, y, w, h)
    nome = str(par.get("nome", "?"))
    pm = par.get("metricas") if par.get("ok") and isinstance(par.get("metricas"), dict) else None
    yc = y + h // 2
    if pm is None:
        _texto_c(c, x + PAD, yc, _ajustar(c, nome, NEG, 34, w // 2), NEG, 34, ESCURO)
        _texto_c(c, x + w - PAD, yc, "sem resposta", NEG, 26, MEDIO, "dir")
        return
    partes = []
    for rot, fn in (("CPU", lambda: pm["cpu"]["pct"]), ("RAM", lambda: pm["ram"]["pct"]),
                    ("GPU", lambda: pm["gpu"]["util_pct"])):
        v = _pct(fn)
        if v is not None:
            partes.append("%s %d%%" % (rot, int(round(v))))
    try:
        partes.append("%d°C" % int(round(pm["temp_cpu"]["c"])))
    except Exception:
        pass
    try:
        partes.append("UP " + _uptime(pm["uptime"]["segundos"]))
    except Exception:
        pass
    txt = "   ".join(partes)
    tw = c.medir(txt, REG, 26)
    c.texto(x + w - PAD, yc + _cap(REG, 26) // 2, _ajustar(c, txt, REG, 26, w - 2 * PAD - 120), REG, 26, ESCURO, alinhar="dir")
    _texto_c(c, x + PAD, yc, _ajustar(c, nome, NEG, 34, max(60, w - 2 * PAD - tw - 24)), NEG, 34, PRETO)


def _desenhar_detalhes(c, m, itens, hist):
    w = c.largura - 2 * MARGEM
    topo, limite = botoes.TOPO, botoes.limite(c.altura)
    blocos = _blocos_detalhes(c, m, itens, w, hist)
    # se nao couber, descarta o HISTORICO e depois do fim, em vez de sair da imagem
    while blocos and sum(b[0] for b in blocos) + GAP * (len(blocos) - 1) > limite - topo:
        k = next((i for i, b in enumerate(blocos) if getattr(b[1], "descartavel", False)), len(blocos) - 1)
        blocos.pop(k)
    if not blocos:
        return
    folga = limite - topo - sum(b[0] for b in blocos) - GAP * (len(blocos) - 1)
    extra = min(24, folga // max(1, len(blocos)))
    y = topo
    for h, fn in blocos:
        fn(c, MARGEM, y, h)
        y += h + GAP + extra


# --------------------------------------------------------------------- acoes

def _ultimos(c, m, x, y, w, rh, limite_y):
    """Titulo + ate 8 comandos recentes; devolve o Y logo abaixo."""
    c.texto(x, y + 4 + _cap(NEG, 26), "ULTIMOS COMANDOS", NEG, 26, ESCURO)
    lista = m.get("comandos")
    its = [i for i in lista if isinstance(i, dict)][:botoes.ULTIMOS_MAX] if isinstance(lista, list) else []
    y0 = y + botoes.ULTIMOS_TITULO_H
    its = its[:max(0, (limite_y - y0) // rh)]
    if not its:
        _texto_c(c, x, y0 + rh // 2, "nenhum comando ainda", REG, 34, ESCURO)
        return y0 + rh
    bh = 36
    bw = max([150] + [int(c.medir(_limpar(str(i.get("estado", "?"))).upper()[:10], NEG, 26)) + 28 for i in its])
    for i, it in enumerate(its):
        yy = y0 + i * rh
        estado = str(it.get("estado", "?"))
        rot = _limpar(estado).upper()[:10]
        by = yy + (rh - bh) // 2
        if estado == "falhou":
            c.retangulo_arredondado(x, by, bw, bh, 8, PRETO)
            cor = BRANCO
        else:
            c.contorno_arredondado(x, by, bw, bh, 8, PRETO, 2, TRILHO if estado == "executando" else BRANCO)
            cor = PRETO
        c.texto(x + bw // 2, by + (bh + _cap(NEG, 26)) // 2, rot, NEG, 26, cor, alinhar="centro")
        yc = yy + rh // 2
        quando = _limpar(it.get("quando", ""))
        c.texto(x + w, yc + _cap(REG, 26) // 2, quando, REG, 26, ESCURO, alinhar="dir")
        ax = x + bw + 20
        limite_a = x + w - c.medir(quando, REG, 26) - 24
        acao = _ajustar(c, servicos.rotulo_acao(str(it.get("acao", "?"))), NEG, 34, limite_a - ax)
        c.texto(ax, yc + _cap(NEG, 34) // 2, acao, NEG, 34, PRETO)
        det = _limpar(it.get("detalhe", ""))
        dx = ax + int(c.medir(acao, NEG, 34)) + 24
        if det and limite_a - dx > 60:
            c.texto(dx, yc + _cap(REG, 26) // 2, _ajustar(c, det, REG, 26, limite_a - dx), REG, 26, ESCURO)
        if i < len(its) - 1:
            c.retangulo(x, yy + rh - 1, w, 2, TRILHO)
    return y0 + len(its) * rh


def _desenhar_comandos(c, m, modo=None):
    """Grade das acoes rapidas, ajustes (modo) e, no resto da pagina, os ultimos comandos."""
    geo = botoes.geometria_comandos(c.largura, c.altura)
    w = c.largura - 2 * MARGEM
    c.texto(MARGEM, geo["rapidas_titulo_y"] + 4 + _cap(NEG, 26), "ACOES RAPIDAS", NEG, 26, ESCURO)
    c.texto(MARGEM, geo["ajustes_titulo_y"] + 4 + _cap(NEG, 26), "AJUSTES", NEG, 26, ESCURO)
    desc = _ajustar(c, perfis.descricao(modo), REG, 34, w)
    c.texto(MARGEM, geo["ajustes_desc_y"] + (geo["ajustes_desc_h"] + _cap(REG, 34)) // 2, desc, REG, 34, ESCURO)
    _ultimos(c, m, MARGEM, geo["fim_botoes"] + GAP, w, geo["linha_h"], botoes.limite(c.altura))


# ---------------------------------------------------------------- claude / S10

DIAS_SEMANA = ("seg", "ter", "qua", "qui", "sex", "sab", "dom")
STATUS_BATERIA = {"charging": "carregando", "full": "cheia", "discharging": "descarregando",
                  "not_charging": "descarregando"}
AVISOS_S10 = {"temperatura": "temperatura alta", "carga_cheia": "100% ha horas: proteger bateria"}
CAMINHOS_S10 = (("usb", "USB"), ("adb_sem_fio", "ADB sem fio"), ("tailscale", "Tailscale"),
                ("ssh_termux", "SSH Termux"), ("vnc", "VNC"))
CLAUDE_H = 520


def _tokens_txt(n):
    """950 -> "950"; 12000 -> "12 k"; 3100000 -> "3,1 M"; nao numero -> "n/d"."""
    n = _num(n)
    if n is None:
        return "n/d"
    n = max(0, n)
    if n < 1000:
        return "%d" % round(n)
    if round(n / 1000.0) < 1000:
        return "%d k" % round(n / 1000.0)
    return ("%.1f M" % (n / 1e6)).replace(".", ",")


def _volta_txt(epoch, agora, tz=None):
    """"volta 14:30" se for hoje, "volta qui 02:00" em outro dia; "" se `epoch` nao for um instante valido."""
    try:
        e, a = _num(epoch), _num(agora)
        if e is None or a is None:
            return ""
        d, hoje = datetime.fromtimestamp(e, tz), datetime.fromtimestamp(a, tz)
    except (OverflowError, OSError, ValueError):
        return ""
    if d.date() == hoje.date():
        return "volta %s" % d.strftime("%H:%M")
    return "volta %s %s" % (DIAS_SEMANA[d.weekday()], d.strftime("%H:%M"))


def _idade_txt(seg):
    seg = _num(seg)
    if seg is None:
        return ""
    return "ha %d h" % (seg // 3600) if seg >= 3600 else "ha %d min" % max(1, int(seg // 60))


def _agora(m):
    """(epoch, tzinfo) do instante da coleta (`gerado_em`); sem ele, o relogio local."""
    try:
        d = datetime.fromisoformat(m["gerado_em"])
        return d.timestamp(), d.tzinfo
    except Exception:
        import time
        return time.time(), None


def _custo_txt(v):
    v = _num(v)
    return "n/d" if v is None else ("US$ %.2f" % v).replace(".", ",")


def _cabecalho_card(c, x, y, w, titulo, velho=False, idade_s=None, icone=None, detalhe=None):
    """Linha de titulo de um cartao (64 px): icone opcional (nome em `icones_dados`), titulo, `detalhe` (resumo em
    cinza logo depois do titulo) e, se os dados estao velhos, a idade em cinza a direita."""
    tx = x + PAD
    if icone:
        tx += (c.icone(x + PAD, y + 12, icone, 40, PRETO) or 0) + 12
    _texto_c(c, tx, y + 32, titulo, NEG, 34, PRETO)
    if detalhe:
        xd = tx + int(c.medir(titulo, NEG, 34)) + 18
        livre = x + w - PAD - xd - (150 if velho else 0)
        _texto_c(c, xd, y + 32, _ajustar(c, detalhe, REG, 26, livre), REG, 26, ESCURO)
    if velho and _idade_txt(idade_s):
        _texto_c(c, x + w - PAD, y + 32, _idade_txt(idade_s), REG, 26, MEDIO, "dir")
    c.retangulo(x + PAD, y + 63, w - 2 * PAD, 2, TRILHO)
    return y + 64


def _linha_janela(c, x, y, w, nome, j, agora, tz):
    """Uma janela de limite (100 px): nome, barra, % (>= 90 em negrito grande e preto) e quando volta."""
    yc = y + 50
    _texto_c(c, x + PAD, yc, nome, NEG, 34, PRETO)
    j = j if isinstance(j, dict) else None
    pct = _num(j.get("pct")) if j else None
    if pct is None:
        _texto_c(c, x + PAD + 186, yc, "n/d", REG, 34, ESCURO)
        return
    renovado = j.get("renovado") is True
    pct = 0.0 if renovado else min(100.0, max(0.0, float(pct)))
    bw = min(480, max(60, w - 596))
    _barra(c, x + PAD + 186, yc - 15, bw, 30, pct)
    alto = pct >= 90
    _texto_c(c, x + PAD + 186 + bw + 18, yc, "%d%%" % round(pct), NEG, 48 if alto else 34, PRETO if alto else ESCURO)
    sub = "renovado" if renovado else _volta_txt(j.get("volta_em"), agora, tz)
    if sub:
        _texto_c(c, x + w - PAD, yc, sub, REG, 26, ESCURO, "dir")


def _bloco_tokens(c, x, y, w, titulo, t):
    t = t if isinstance(t, dict) else {}
    c.texto(x, y + _cap(NEG, 26), titulo, NEG, 26, ESCURO)
    _texto_c(c, x, y + 62, "%s tokens" % _tokens_txt(t.get("total")), NEG, 34, PRETO)
    _texto_c(c, x, y + 104, _custo_txt(t.get("custo_usd")), REG, 34, PRETO)
    ent = "ent %s  sai %s" % (_tokens_txt(t.get("entrada")), _tokens_txt(t.get("saida")))
    cache = "cache %s / %s" % (_tokens_txt(t.get("cache_leitura")), _tokens_txt(t.get("cache_escrita")))
    _texto_c(c, x, y + 146, _ajustar(c, ent, REG, 26, w), REG, 26, ESCURO)
    _texto_c(c, x, y + 180, _ajustar(c, cache, REG, 26, w), REG, 26, ESCURO)


def _card_claude(c, cl, x, y, w, h, agora=None):
    """Cartao Claude: janelas de 5 h e semanal, tokens de hoje e dos ultimos 7 dias."""
    _card(c, x, y, w, h)
    cl = cl if isinstance(cl, dict) else {}
    lim, tok = cl.get("limites"), cl.get("tokens")
    lim = lim if _ok(lim) else None
    tok = tok if _ok(tok) else None
    velho = bool(lim and lim.get("velho") is True)
    yy = _cabecalho_card(c, x, y, w, "Claude", velho, lim.get("idade_s") if lim else None, icone="claude")
    agora, tz = agora or _agora({})
    if lim is None:
        _texto_c(c, x + PAD, yy + 50, "limites n/d", REG, 34, ESCURO)
        yy += 100 * 2
    else:
        _linha_janela(c, x, yy, w, "5h", lim.get("cinco_horas"), agora, tz)
        _linha_janela(c, x, yy + 100, w, "Semanal", lim.get("semanal"), agora, tz)
        yy += 200
    c.retangulo(x + PAD, yy + 6, w - 2 * PAD, 2, TRILHO)
    yy += 24
    if tok is None:
        _texto_c(c, x + PAD, yy + 40, "tokens n/d", REG, 34, ESCURO)
        return
    meio = (w - 2 * PAD) // 2
    _bloco_tokens(c, x + PAD, yy, meio - PAD, "HOJE", tok.get("hoje"))
    _bloco_tokens(c, x + PAD + meio, yy, meio - PAD, "7 DIAS", tok.get("sete_dias"))
    if tok.get("velho") is True and _idade_txt(tok.get("idade_s")):
        _texto_c(c, x + w - PAD, y + h - 28, "tokens " + _idade_txt(tok.get("idade_s")), REG, 26, MEDIO, "dir")


def _aviso_txt(codigo):
    return AVISOS_S10.get(codigo, codigo) if isinstance(codigo, str) else None


def _avisos(s):
    av = s.get("avisos")
    return [a for a in (_aviso_txt(x) for x in (av if isinstance(av, list) else [])) if a][:4]


def _h_s10(s):
    s = s if _ok(s) else {}
    return 64 + 90 + 3 * 46 + 20 + (len(_avisos(s)) * 44 + 12 if _avisos(s) else 0)


def _card_s10(c, s, x, y, w, h):
    """Cartao S10: bateria (nivel, estado, temperatura), cinco caminhos de acesso e avisos."""
    _card(c, x, y, w, h)
    if not _ok(s):
        _cabecalho_card(c, x, y, w, "S10", False, icone="celular")
        _texto_c(c, x + PAD, y + 64 + 40, "n/d", REG, 34, ESCURO)
        return
    velho = s.get("velho") is True
    titulo = "S10 sem dados %s" % _idade_txt(s.get("idade_s")) if velho else "S10"
    yy = _cabecalho_card(c, x, y, w, titulo.strip(), False, icone="celular")
    bat = s.get("bateria") if isinstance(s.get("bateria"), dict) else None
    yc = yy + 45
    if velho or bat is None:
        _texto_c(c, x + PAD, yc, "bateria n/d", REG, 34, ESCURO)
    else:
        nivel = _num(bat.get("nivel"))
        bw = min(300, max(60, w - 2 * PAD - 186 - 18 - 70 - 200))
        _texto_c(c, x + PAD, yc, "Bateria", NEG, 34, PRETO)
        if nivel is None:
            _texto_c(c, x + PAD + 186, yc, "n/d", REG, 34, ESCURO)
        else:
            nivel = min(100.0, max(0.0, float(nivel)))
            _barra(c, x + PAD + 186, yc - 15, bw, 30, nivel)
            _texto_c(c, x + PAD + 186 + bw + 18, yc, "%d%%" % round(nivel), NEG, 34, PRETO)
        partes = []
        st = STATUS_BATERIA.get(bat.get("status")) if isinstance(bat.get("status"), str) else None
        if st:
            partes.append(st)
        temp = _num(bat.get("temperatura_c"))
        partes.append("n/d" if temp is None else "%.0f°C" % temp)
        txt = _ajustar(c, "  ".join(partes), REG, 26, w - 2 * PAD - 186 - bw - 18 - 100)
        _texto_c(c, x + w - PAD, yc, txt, REG, 26, ESCURO, "dir")
    yy += 90
    cam = s.get("caminhos") if isinstance(s.get("caminhos"), dict) else {}
    for i, (chave, rotulo) in enumerate(CAMINHOS_S10):
        cx = x + PAD + (i % 2) * ((w - 2 * PAD) // 2)
        cy = yy + (i // 2) * 46 + 23
        v = cam.get(chave)
        if velho or not isinstance(v, bool):
            _forma(c, cx, cy - 14, 28, None)
        else:
            _forma_ok(c, cx, cy - 14, 28, v)
        _texto_c(c, cx + 40, cy, rotulo, NEG, 26, PRETO)
    yy += 3 * 46 + 20
    for a in _avisos(s):
        _forma(c, x + PAD, yy + 6, 28, "falha")
        _texto_c(c, x + PAD + 40, yy + 20, _ajustar(c, a, NEG, 26, w - 2 * PAD - 40), NEG, 26, PRETO)
        yy += 44


def _empilhar(c, blocos):
    """Desenha [(altura, desenhar(c, x, y, h))] de cima para baixo a partir do topo; o que nao cabe acima da
    navegacao fica de fora (o espaco livre fica so no fim)."""
    y, limite = botoes.TOPO, botoes.limite(c.altura)
    for h, fn in blocos:
        if y + h > limite:
            break
        fn(c, MARGEM, y, h)
        y += h + GAP


SESSAO_LINHA = 46
SESSOES_MAX = 12
SESSAO_ABERTA = "aberta"  # "forma" so das sessoes: circulo cinza cheio (o estado e "abriu e nao fez nada")
PR_LINHA = 46
PRS_MAX = 6
CI_LINHA = 42
CI_PROBLEMAS_MAX = 3  # com mais que isso, ficam 2 e "+N"
CARTAO_BASE = 64 + 4  # titulo do cartao e respiro ate a 1a linha
CARTAO_FIM = 8


def _limite_sessao_s(m):
    """Segundos de uma sessao esperando ate virar aviso: o mesmo limiar do motor de alertas."""
    return alertas.limiares(m.get("limiares") if isinstance(m, dict) else None)["sessao_esperando_min"] * 60


def _desde_txt(desde_s):
    """"agora" (< 1 min), "ha 5 min", "ha 3 h"... de um tempo em segundos; "" se nao for numero valido."""
    n = _num(desde_s)
    if n is None or n < 0:
        return ""
    return "agora" if n < 60 else _ha_txt(n // 60)


def _estado_sessao(it, limite_s):
    """(forma, estado) de uma sessao: trabalhando = ativo; esperando = aviso (>= `limite_s`) ou parado; aberta e
    SESSAO_ABERTA; desconhecido = ?."""
    est = it.get("estado")
    if est == "trabalhando":
        return "ativo", "trabalhando"
    if est == "esperando":
        desde = _num(it.get("desde_s"))
        return ("aviso" if desde is not None and desde >= limite_s else "parado"), "esperando"
    if est == "aberta":
        return SESSAO_ABERTA, "aberta"
    return None, "?"


def _sessao_txt(it, limite_s):
    """(forma, "esperando ha 12 min") de uma sessao: o texto que acompanha a forma."""
    forma, est = _estado_sessao(it, limite_s)
    return forma, " ".join(x for x in (est, _desde_txt(it.get("desde_s"))) if x)


def _sessoes_visiveis(cl, max_linhas, limite_s):
    """(visiveis, resto, total, esperando) do cartao SESSOES, com no maximo `max_linhas` linhas ("+N" conta uma), ou
    None se for "sem dados". As piores primeiro quando precisa cortar."""
    d = _sessoes_dados(cl)
    if d is None:
        return None
    itens, total, esp = d
    extra = max(0, total - len(itens))  # sessoes que o coletor nem listou
    vis, resto = _cortar(itens, max(1, max_linhas - (1 if extra else 0)), lambda i: _estado_sessao(i, limite_s))
    return vis, resto + extra, total, esp


def _h_sessoes(cl, max_linhas, limite_s):
    d = _sessoes_visiveis(cl, max_linhas, limite_s)
    if d is None or not d[2]:
        return H_SEM_DADOS
    return CARTAO_BASE + (len(d[0]) + (1 if d[1] else 0)) * SESSAO_LINHA + CARTAO_FIM


def _card_sessoes(c, cl, x, y, w, h, limite_s, max_linhas=SESSOES_MAX):
    """Cartao SESSOES: uma linha por sessao do Claude Code (projeto, forma de estado, estado e ha quanto tempo), as
    mais recentes primeiro; o resumo "N sessoes, M esperando" fica no titulo."""
    d = _sessoes_visiveis(cl, max_linhas, limite_s)
    if d is None:
        return _card_sem_dados(c, x, y, w, h, "Sessoes", "dev")
    vis, resto, total, esp = d
    _card(c, x, y, w, h)
    if not total:
        yy = _cabecalho_card(c, x, y, w, "Sessoes", icone="dev")
        _texto_c(c, x + PAD, yy + 30, "nenhuma sessao aberta", NEG, 34, MEDIO)
        return
    yy = _cabecalho_card(c, x, y, w, "Sessoes", icone="dev", detalhe=_sessoes_txt(total, esp)) + 4
    ultima = len(vis) - 1 + (1 if resto else 0)
    for i, it in enumerate(vis):
        yc = yy + i * SESSAO_LINHA + SESSAO_LINHA // 2
        forma, txt = _sessao_txt(it, limite_s)
        aviso = forma == "aviso"
        if aviso:
            c.retangulo_arredondado(x + 8, yc - SESSAO_LINHA // 2 + 2, w - 16, SESSAO_LINHA - 4, 8, TRILHO)
        xf = x + w - PAD - 28
        if forma == SESSAO_ABERTA:
            c.circulo(xf + 14, yc, 13, MEDIO)
        else:
            _forma(c, xf, yc - 14, 28, forma)
        xr = xf - 16
        _texto_c(c, xr, yc, txt, NEG if aviso else REG, 26, ESCURO, "dir")
        tw = int(c.medir(txt, NEG, 26)) + 24
        proj = _limpar(it.get("projeto")).strip() if isinstance(it.get("projeto"), str) else ""
        _texto_c(c, x + PAD, yc, _ajustar(c, proj or "?", NEG, 26, xr - tw - x - PAD), NEG, 26, PRETO)
        if i != ultima and not aviso:
            c.retangulo(x + PAD, yc + SESSAO_LINHA // 2 - 1, w - 2 * PAD, 2, TRILHO)
    if resto:
        _texto_c(c, x + PAD, yy + len(vis) * SESSAO_LINHA + SESSAO_LINHA // 2, "+%d" % resto, NEG, 26, ESCURO)


def _repo(it):
    return (_limpar(it.get("repo")).strip() if isinstance(it.get("repo"), str) else "")[:40] or "?"


def _pr_ref(pr):
    n = _num(pr.get("numero"))
    return _repo(pr) + ("#%d" % n if n is not None and n >= 0 else "")


def _estado_pr(pr):
    """Forma do CI de um PR: ok = ativo, falha, pendente = parado, sem CI = None (nao desenha forma)."""
    return {"ok": "ativo", "falha": "falha", "pendente": "parado"}.get(pr.get("ci")), ""


def _github_dados(g, max_prs):
    """Resumo de m["github"] para o cartao e as linhas, ou None se a chave falta, e "n/d" ou o bloco e invalido:
    {"prs": ate `max_prs` PRs (os com CI em falha primeiro quando precisa cortar), "resto": PRs que ficaram de fora,
     "abertos", "ci_ruins": entradas de CI com falha e depois pendentes, "ci_ok": quantas ok, "velho", "idade_s"}."""
    if not _ok(g) or not isinstance(g.get("prs"), list):
        return None
    prs = [p for p in g["prs"] if isinstance(p, dict)][:20]
    ci = [i for i in g.get("ci", []) if isinstance(i, dict)][:30] if isinstance(g.get("ci"), list) else []
    abertos = _num(g.get("abertos"))
    abertos = int(abertos) if abertos is not None and abertos >= len(prs) else len(prs)
    if len(prs) > max_prs:
        prs = sorted(prs, key=lambda p: -_GRAVIDADE.get(_estado_pr(p)[0], 1))[:max(0, max_prs)]
    ruins = [i for i in ci if i.get("estado") == "falha"] + [i for i in ci if i.get("estado") == "pendente"]
    return {"prs": prs, "resto": abertos - len(prs), "abertos": abertos, "ci_ruins": ruins,
            "ci_ok": sum(1 for i in ci if i.get("estado") == "ok"), "velho": g.get("velho") is True,
            "idade_s": g.get("idade_s")}


def _ci_linhas(d):
    """(problemas visiveis, "+N" resto, ok): linhas da faixa de CI do cartao GITHUB."""
    ruins = d["ci_ruins"]
    if len(ruins) <= CI_PROBLEMAS_MAX:
        return ruins, 0, d["ci_ok"]
    return ruins[:CI_PROBLEMAS_MAX - 1], len(ruins) - (CI_PROBLEMAS_MAX - 1), d["ci_ok"]


def _ci_txt(it):
    branch = _limpar(it.get("branch")).strip()[:40] if isinstance(it.get("branch"), str) else ""
    return "CI %s: %s%s" % ("falhou" if it.get("estado") == "falha" else "pendente", _repo(it),
                            " (%s)" % branch if branch else "")


def _h_github(g, max_prs):
    d = _github_dados(g, max_prs)
    if d is None:
        return H_SEM_DADOS
    linhas_pr = len(d["prs"]) + (1 if d["resto"] else 0)
    ruins, resto_ci, ok = _ci_linhas(d)
    linhas_ci = len(ruins) + (1 if resto_ci else 0) + (1 if ok else 0)
    return (CARTAO_BASE + max(1, linhas_pr) * PR_LINHA + (14 + linhas_ci * CI_LINHA if linhas_ci else 0)
            + CARTAO_FIM)


def _card_github(c, g, x, y, w, h, max_prs=PRS_MAX):
    """Cartao GITHUB: PRs abertos como "repo#n titulo" (forma do CI a direita, "(rascunho)" quando e o caso) e, abaixo,
    o CI das branches padrao (o que nao esta ok primeiro, depois "N ok"). Os dados velhos mostram a idade no titulo."""
    d = _github_dados(g, max_prs)
    if d is None:
        return _card_sem_dados(c, x, y, w, h, "GitHub", "github")
    _card(c, x, y, w, h)
    abertos = d["abertos"]
    yy = _cabecalho_card(c, x, y, w, "GitHub", d["velho"], d["idade_s"], icone="github",
                         detalhe=_plural(abertos, "PR aberto", "PRs abertos") if abertos else None) + 4
    n_pr = len(d["prs"]) + (1 if d["resto"] else 0)
    if not n_pr:
        _texto_c(c, x + PAD, yy + PR_LINHA // 2, "nenhum PR aberto", NEG, 34, MEDIO)
        n_pr = 1
    xf = x + w - PAD - 28
    for i, pr in enumerate(d["prs"]):
        yc = yy + i * PR_LINHA + PR_LINHA // 2
        forma = _estado_pr(pr)[0]
        falha = forma == "falha"
        if falha:
            c.retangulo_arredondado(x + 8, yc - PR_LINHA // 2 + 2, w - 16, PR_LINHA - 4, 8, TRILHO)
        if forma is not None:
            _forma(c, xf, yc - 14, 28, forma)
        xr = xf - 16
        if pr.get("rascunho") is True:
            _texto_c(c, xr, yc, "(rascunho)", REG, 26, ESCURO, "dir")
            xr -= int(c.medir("(rascunho)", REG, 26)) + 16
        tx = x + PAD
        ref = _ajustar(c, _pr_ref(pr), NEG, 26, max(80, (xr - tx) * 45 // 100))
        _texto_c(c, tx, yc, ref, NEG, 26, PRETO)
        tx += int(c.medir(ref, NEG, 26)) + 14
        titulo = _limpar(pr.get("titulo")).strip() if isinstance(pr.get("titulo"), str) else ""
        titulo = _ajustar(c, titulo, REG, 26, xr - tx - 8) if xr - tx > 60 else ""
        if titulo:
            _texto_c(c, tx, yc, titulo, REG, 26, ESCURO)
        if i != n_pr - 1 and not falha:
            c.retangulo(x + PAD, yc + PR_LINHA // 2 - 1, w - 2 * PAD, 2, TRILHO)
    if d["resto"]:
        _texto_c(c, x + PAD, yy + len(d["prs"]) * PR_LINHA + PR_LINHA // 2, "+%d" % d["resto"], NEG, 26, ESCURO)
    ruins, resto_ci, ok = _ci_linhas(d)
    if not (ruins or resto_ci or ok):
        return
    yc0 = yy + n_pr * PR_LINHA + 14
    c.retangulo(x + PAD, yc0 - 8, w - 2 * PAD, 2, TRILHO)
    for i, it in enumerate(ruins):
        yc = yc0 + i * CI_LINHA + CI_LINHA // 2
        _forma(c, x + PAD, yc - 14, 28, "falha" if it.get("estado") == "falha" else "parado")
        _texto_c(c, x + PAD + 44, yc, _ajustar(c, _ci_txt(it), NEG, 26, w - 2 * PAD - 44), NEG, 26, PRETO)
    linha = len(ruins)
    if resto_ci:
        _texto_c(c, x + PAD + 44, yc0 + linha * CI_LINHA + CI_LINHA // 2, "+%d" % resto_ci, NEG, 26, ESCURO)
        linha += 1
    if ok:
        yc = yc0 + linha * CI_LINHA + CI_LINHA // 2
        _forma(c, x + PAD, yc - 14, 28, "ativo")
        _texto_c(c, x + PAD + 44, yc, "CI", NEG, 26, ESCURO)
        _texto_c(c, x + PAD + 44 + int(c.medir("CI", NEG, 26)) + 12, yc, "%d ok" % ok, REG, 26, ESCURO)


def _desenhar_claude(c, m):
    """Dev: cartao do Claude Code, SESSOES e GITHUB. Sem espaco para tudo, SESSOES e GITHUB dividem o que sobra (cada
    um corta com "+N"); o que ainda nao couber fica de fora, do fim."""
    w = c.largura - 2 * MARGEM
    if "claude" not in m and "github" not in m:
        c.texto(c.largura // 2, (botoes.TOPO + botoes.limite(c.altura)) // 2 + _cap(NEG, 34) // 2,
                "Claude desligado na config", NEG, 34, ESCURO, "centro")
        return
    agora, limite_s, g = _agora(m), _limite_sessao_s(m), m.get("github")
    blocos = []
    disp = botoes.limite(c.altura) - botoes.TOPO
    if "claude" in m:
        cl = m["claude"]
        blocos.append((CLAUDE_H, lambda c, x, y, h: _card_claude(c, cl, x, y, w, h, agora)))
        disp -= CLAUDE_H + GAP
        # SESSOES leva o que o GITHUB nao precisa no minimo (2 PRs); depois o GITHUB leva o que sobrar
        linhas = (disp - GAP - _h_github(g, 2) - CARTAO_BASE - CARTAO_FIM) // SESSAO_LINHA
        max_s = max(2, min(SESSOES_MAX, linhas))
        h_s = _h_sessoes(cl, max_s, limite_s)
        blocos.append((h_s, lambda c, x, y, h: _card_sessoes(c, cl, x, y, w, h, limite_s, max_s)))
        disp -= h_s + GAP
    max_g = next((k for k in range(PRS_MAX, 0, -1) if _h_github(g, k) <= disp), 1)
    blocos.append((_h_github(g, max_g), lambda c, x, y, h: _card_github(c, g, x, y, w, h, max_g)))
    _empilhar(c, blocos)


APARELHO_LINHA = 56
APARELHOS_MAX = 16


def _icone_aparelho(it):
    nome = it.get("icone")
    return nome if isinstance(nome, str) and nome in icones_dados.ICONES else _ICONE_APARELHO_PADRAO


def _tailnet_visiveis(ap, max_linhas=APARELHOS_MAX):
    """(visiveis, resto) do cartao TAILNET, ou None se for "sem dados" (sem bloco, lista vazia, inventario velho)."""
    fonte = _fonte_itens({"aparelhos": ap}, "aparelhos")
    if fonte is None or not fonte[0] or not fonte[1]:
        return None
    return _cortar(fonte[1][:APARELHOS_MAX], max_linhas, _estado_aparelho)


def _h_tailnet(ap, max_linhas=APARELHOS_MAX):
    d = _tailnet_visiveis(ap, max_linhas)
    if d is None:
        return H_SEM_DADOS
    return 64 + 4 + (len(d[0]) + (1 if d[1] else 0)) * APARELHO_LINHA + 8


def _card_tailnet(c, ap, x, y, w, h, max_linhas=APARELHOS_MAX):
    """Cartao TAILNET: uma linha por aparelho (icone de 40 px, rotulo, texto secundario e a forma de estado a direita).
    Sem o bloco, ou com inventario velho/ausente: "sem dados" cinza."""
    d = _tailnet_visiveis(ap, max_linhas)
    if d is None:
        fonte = _fonte_itens({"aparelhos": ap}, "aparelhos")
        velho = fonte is not None and not fonte[0]
        idade = _num(_d(ap).get("idade_s")) if velho and _d(ap).get("inventario") == "velho" else None
        return _card_sem_dados(c, x, y, w, h, "Tailnet", "tailscale", INVENTARIO_SEM if velho else None, idade)
    vis, resto = d
    _card(c, x, y, w, h)
    yy = _cabecalho_card(c, x, y, w, "Tailnet", icone="tailscale") + 4
    ultima = len(vis) - 1 + (1 if resto else 0)
    for i, it in enumerate(vis):
        yc = yy + i * APARELHO_LINHA + APARELHO_LINHA // 2
        forma, txt = _estado_aparelho(it)
        falha = forma == "falha"
        if falha:
            c.retangulo_arredondado(x + 8, yc - APARELHO_LINHA // 2 + 2, w - 16, APARELHO_LINHA - 4, 8, TRILHO)
        c.icone(x + PAD, yc - 20, _icone_aparelho(it), 40, PRETO)
        _forma(c, x + w - PAD - 28, yc - 14, 28, forma)
        xr = x + w - PAD - 28 - 16
        _texto_c(c, xr, yc, txt, NEG if falha else REG, 26, MEDIO if forma is None else ESCURO, "dir")
        tx = x + PAD + 40 + 16
        tw = int(c.medir(txt, NEG, 26)) + 24
        _texto_c(c, tx, yc, _ajustar(c, _rotulo(it), NEG, 26, xr - tw - tx), NEG, 26,
                 ESCURO if forma is None else PRETO)
        if i != ultima and not falha:
            c.retangulo(x + PAD, yc + APARELHO_LINHA // 2 - 1, w - 2 * PAD, 2, TRILHO)
    if resto:
        yc = yy + len(vis) * APARELHO_LINHA + APARELHO_LINHA // 2
        _texto_c(c, x + PAD + 56, yc, "+%d" % resto, NEG, 26, ESCURO)


def _desenhar_aparelhos(c, m, kv=None):
    """Aparelhos: TAILNET (um aparelho por linha), o proprio Kindle, o S10 (se houver na config) e os pares."""
    w = c.largura - 2 * MARGEM
    h_kindle = H_KINDLE if isinstance(kv, dict) else H_SEM_DADOS
    ap = m.get("aparelhos")
    # o cartao TAILNET deixa sempre espaco para o do Kindle logo abaixo; se faltar, corta com "+N"
    disp = botoes.limite(c.altura) - botoes.TOPO - h_kindle - GAP
    max_linhas = max(2, min(APARELHOS_MAX, (disp - 64 - 4 - 8) // APARELHO_LINHA))
    blocos = [(_h_tailnet(ap, max_linhas), lambda c, x, y, h: _card_tailnet(c, ap, x, y, w, h, max_linhas)),
              (h_kindle, lambda c, x, y, h: _card_kindle(c, kv, x, y, w, h))]
    if "s10" in m:
        blocos.append((_h_s10(m["s10"]), lambda c, x, y, h: _card_s10(c, m["s10"], x, y, w, h)))
    pares = m.get("pares")
    for par in [p for p in pares if isinstance(p, dict)] if isinstance(pares, list) else []:
        blocos.append((76, lambda c, x, y, h, par=par: _card_par(c, par, x, y, w, h)))
    _empilhar(c, blocos)


# ----------------------------------------------------------------------- jogos

JOGO_LINHA = 56
# forma de cada estado do AMP: ligado = cheia; parado e iniciando = vazia; falha = X; outro = ? (o texto diz qual)
_FORMA_AMP = {"rodando": "ativo", "parado": "parado", "iniciando": "parado", "falha": "falha", "outro": None}
_TEXTO_AMP = {"parado": "parado", "iniciando": "iniciando", "falha": "FALHA", "outro": "outro"}


def _ragnarok_dados(m):
    """(jogadores|None, parado, portas) do Ragnarok, ou None sem nenhuma fonte (nem contagem nem portas)."""
    rag = m.get("ragnarok")
    n = int(rag["jogadores"]) if _ok(rag) and _num(rag.get("jogadores")) is not None else None
    portas = [p for p in _portas_lista(m) if p.get("aberto") in (True, False)]
    if n is None and not portas:
        return None
    return n, bool(_ok(rag) and rag.get("parado")), portas


def _h_ragnarok(m):
    d = _ragnarok_dados(m)
    if d is None:
        return H_SEM_DADOS
    return 64 + 4 + (1 + min(len(d[2]), 8)) * JOGO_LINHA + 8


def _card_ragnarok(c, m, x, y, w, h):
    """Cartao RAGNAROK: jogadores (e "parado" se o balanceador parou de atualizar) e uma linha por porta com a forma de
    estado (cheia = aberta, X = fechada)."""
    d = _ragnarok_dados(m)
    if d is None:
        return _card_sem_dados(c, x, y, w, h, "RAGNAROK", "jogo")
    n, parado, portas = d
    _card(c, x, y, w, h)
    yy = _cabecalho_card(c, x, y, w, "RAGNAROK", icone="jogo") + 4
    yc = yy + JOGO_LINHA // 2
    _texto_c(c, x + PAD, yc, "JOGADORES", NEG, 26, ESCURO)
    xv = x + PAD + int(c.medir("JOGADORES", NEG, 26)) + 24
    if n is None:
        _texto_c(c, xv, yc, "n/d", NEG, 34, MEDIO)
    else:
        _texto_c(c, xv, yc, "%d" % n, NEG, 34, PRETO)
        if parado:
            _texto_c(c, x + w - PAD, yc, "parado", REG, 26, ESCURO, "dir")
    for i, p in enumerate(portas[:8]):
        yp = yy + (i + 1) * JOGO_LINHA + JOGO_LINHA // 2
        aberta = p.get("aberto") is True
        if not aberta:
            c.retangulo_arredondado(x + 8, yp - JOGO_LINHA // 2 + 2, w - 16, JOGO_LINHA - 4, 8, TRILHO)
        _forma(c, x + PAD, yp - 14, 28, "ativo" if aberta else "falha")
        _texto_c(c, x + PAD + 28 + 16, yp, _ajustar(c, _limpar(p.get("rotulo", "?")), NEG, 34, w // 2), NEG, 34, PRETO)
        _texto_c(c, x + w - PAD, yp, "aberta" if aberta else "FECHADA", REG if aberta else NEG, 26,
                 ESCURO if aberta else PRETO, "dir")


def _amp_visiveis(itens, max_linhas):
    """(visiveis, resto): ate `max_linhas - 1` instancias mais a linha "+N" quando nao cabem todas; a ordem (ligadas
    primeiro, depois por nome) vale tambem para o corte."""
    if len(itens) <= max_linhas:
        return itens, 0
    vis = itens[:max(0, max_linhas - 1)]
    return vis, len(itens) - len(vis)


def _h_amp(m, max_linhas=AMP_MAX):
    situacao, itens, _ = _amp_dados(m)
    if situacao != "ok" or not itens:
        return H_SEM_DADOS if situacao == "sem_dados" else 64 + 4 + JOGO_LINHA + 8
    vis, resto = _amp_visiveis(itens, max_linhas)
    return 64 + 4 + (len(vis) + (1 if resto else 0)) * JOGO_LINHA + 8


def _card_amp(c, m, x, y, w, h, max_linhas=AMP_MAX):
    """Cartao AMP: uma linha por instancia (forma, nome, modulo e, a direita, "N/MAX" jogadores se esta rodando, ou o
    estado). Ligado sem dado: "sem dados" cinza com o motivo curto. Instancia parada nao e problema: nao ganha destaque."""
    situacao, itens, b = _amp_dados(m)
    if situacao != "ok":
        velho = b.get("inventario") == "velho"
        erro = _limpar(b.get("erro")).strip()[:40] if isinstance(b.get("erro"), str) else ""
        return _card_sem_dados(c, x, y, w, h, "AMP", "servidor", INVENTARIO_SEM if velho else (erro or None),
                               _num(b.get("idade_s")) if velho else None)
    _card(c, x, y, w, h)
    yy = _cabecalho_card(c, x, y, w, "AMP", icone="servidor") + 4
    if not itens:
        _texto_c(c, x + PAD, yy + JOGO_LINHA // 2, "nenhum servidor", REG, 26, ESCURO)
        return
    vis, resto = _amp_visiveis(itens, max_linhas)
    ultima = len(vis) - 1 + (1 if resto else 0)
    for i, it in enumerate(vis):
        yc = yy + i * JOGO_LINHA + JOGO_LINHA // 2
        estado = it["estado"]
        if estado == "falha":
            c.retangulo_arredondado(x + 8, yc - JOGO_LINHA // 2 + 2, w - 16, JOGO_LINHA - 4, 8, TRILHO)
        _forma(c, x + PAD, yc - 14, 28, _FORMA_AMP[estado])
        if estado == "rodando":
            dir_txt, dir_fonte, dir_cor = _contagem_amp(it) or "ligado", NEG, PRETO
            dir_tam = 34 if _contagem_amp(it) else 26
        else:
            dir_txt, dir_fonte, dir_cor, dir_tam = _TEXTO_AMP[estado], NEG if estado == "falha" else REG, ESCURO, 26
        _texto_c(c, x + w - PAD, yc, dir_txt, dir_fonte, dir_tam, dir_cor, "dir")
        xr = x + w - PAD - int(c.medir(dir_txt, dir_fonte, dir_tam)) - 24
        tx = x + PAD + 28 + 16
        cor = PRETO if estado == "rodando" or estado == "falha" else ESCURO
        nome = _ajustar(c, it["nome"], NEG, 34, max(60, (xr - tx) * 3 // 5))
        _texto_c(c, tx, yc, nome, NEG, 34, cor)
        xm = tx + int(c.medir(nome, NEG, 34)) + 18
        if it["modulo"] and it["modulo"].lower() != it["nome"].lower() and xr - xm > 80:  # "Minecraft Minecraft" nao diz nada
            _texto_c(c, xm, yc, _ajustar(c, it["modulo"], REG, 26, xr - xm), REG, 26, MEDIO)
        if i != ultima and estado != "falha":
            c.retangulo(x + PAD, yc + JOGO_LINHA // 2 - 1, w - 2 * PAD, 2, TRILHO)
    if resto:
        yc = yy + len(vis) * JOGO_LINHA + JOGO_LINHA // 2
        _texto_c(c, x + PAD + 44, yc, "+%d" % resto, NEG, 26, ESCURO)


def _desenhar_jogos(c, m):
    """Pagina Jogos (sem aba): cartao RAGNAROK e, se o AMP estiver ligado, o cartao AMP com todas as instancias."""
    w = c.largura - 2 * MARGEM
    h_rag = _h_ragnarok(m)
    blocos = [(h_rag, lambda c, x, y, h: _card_ragnarok(c, m, x, y, w, h))]
    if _amp_dados(m)[0] is not None:
        disp = botoes.limite(c.altura) - botoes.TOPO - h_rag - GAP
        max_linhas = max(2, min(AMP_MAX, (disp - 64 - 4 - 8) // JOGO_LINHA))
        blocos.append((_h_amp(m, max_linhas), lambda c, x, y, h: _card_amp(c, m, x, y, w, h, max_linhas)))
    _empilhar(c, blocos)


# --------------------------------------------------------------------- entrada

def desenhar(c, metricas, historico=None, pagina="resumo", armado=None, p=1, modo=None, kindle=None):
    """Desenha a pagina inteira no canvas `c` (padrao do Kindle: 1236x1648). `kindle`: vista de kindle_status."""
    m = metricas if isinstance(metricas, dict) else {}
    hist = historico if isinstance(historico, dict) else m.get("historico")
    hist = hist if isinstance(hist, dict) else {}
    pagina = botoes.pagina_valida(pagina)
    itens = servicos.ordenar(servicos.itens_de(m))
    armado = botoes.armado_valido(armado, itens)
    kv = kindle if isinstance(kindle, dict) else None
    _barra_kindle(c, kv)
    _cabecalho(c, m, itens)
    if pagina == "resumo":
        _desenhar_resumo(c, m, hist, itens, kv)
    elif pagina == "servicos":
        _desenhar_servicos(c, m, itens, p)
    elif pagina == "detalhes":
        _desenhar_detalhes(c, m, itens, hist)
    elif pagina == "claude":
        _desenhar_claude(c, m)
    elif pagina == "aparelhos":
        _desenhar_aparelhos(c, m, kv)
    elif pagina == "jogos":
        _desenhar_jogos(c, m)
    else:
        _desenhar_comandos(c, m, modo)
    _desenhar_botoes(c, pagina, armado, p, itens, modo)


def render_png(metricas, historico=None, largura=1236, altura=1648, pagina="resumo", armado=None, p=1, modo=None,
               kindle=None):
    """Devolve a tela como PNG 8-bit em tons de cinza."""
    c = Canvas(largura, altura)
    desenhar(c, metricas, historico, pagina, armado, p, modo, kindle)
    return c.para_png()
