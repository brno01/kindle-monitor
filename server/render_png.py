"""Tela PNG (retrato, tons de cinza) do kindle-monitor. Funcoes puras: metricas -> bytes PNG.

Cinco paginas (resumo, servicos, detalhes, comandos, claude) mais a barra de navegacao fixa no rodape. Os botoes vem
sempre de `botoes.layout` (a mesma funcao que serve /botoes.json): aqui so se desenha o que ela devolve.
Visual e-ink: alto contraste, contornos finos, raios pequenos, sem sombras; so os tamanhos de fonte embutidos
(26 e 34; negrito tambem 48, 72 e 140). Estado de servico: forma antes da cor (cheia = ativo, vazia = parado,
X = falha, ? = desconhecido).
"""
import math
import unicodedata
from datetime import datetime

import alertas
import botoes
import coletores
import formato
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


def _bytes_txt(v, base):
    t, i, un = _un(v, base)
    return ("%.0f %s" if t >= 100 else "%.1f %s") % (t, un[i])


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

def _aviso_inventario(m):
    sk = m.get("servicos_kindle")
    if not isinstance(sk, dict):
        return None
    if sk.get("inventario") == "velho":
        return "estados desatualizados"
    if sk.get("inventario") == "ausente":
        return "sem inventario de servicos"
    return None


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


def _desenhar_botoes(c, pagina, armado, p, itens, modo=None):
    modo = perfis.modo_valido(modo)
    for b in botoes.layout(pagina, armado, c.largura, c.altura, p, itens, modo):
        if not b.get("visivel", True):  # so existe para o toque (/botoes.txt)
            continue
        if b["tipo"] == "local" and b["id"].startswith("pagina:"):
            _botao(c, b, b["id"] == "pagina:" + pagina)
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


def _h_atencao(n, linhas=None):
    """Altura do card: titulo + (linhas de itens | 'Tudo em ordem')."""
    corpo = 64 if n == 0 else (linhas if linhas is not None else _linhas_atencao(n)) * ATENCAO_LINHA
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
    mostrar = atencao[:ATENCAO_MAX] if n <= min(ATENCAO_MAX, cabem) else atencao[:min(ATENCAO_MAX, cabem - 1)]
    for i, it in enumerate(mostrar):
        yc = y + ATENCAO_TITULO + i * ATENCAO_LINHA + ATENCAO_LINHA // 2
        _forma(c, x + PAD, yc - 14, 28, _FORMA_NIVEL.get(it.get("nivel"), "desconhecido"))
        _texto_c(c, x + PAD + 44, yc, _ajustar(c, it.get("texto", "?"), NEG, 34, w - 2 * PAD - 44), NEG, 34, PRETO)
    if n > len(mostrar):
        yc = y + ATENCAO_TITULO + len(mostrar) * ATENCAO_LINHA + ATENCAO_LINHA // 2
        _texto_c(c, x + PAD + 44, yc, "+%d" % (n - len(mostrar)), NEG, 26, ESCURO)


# ----------------------------------------------------------------- chips (resumo)

CHIP_H = 40


CHIP_H_COMPACTO = 36


def _chips_h(n, cols, ch=CHIP_H):
    return 52 + -(-n // cols) * ch + 12


def _card_chips(c, itens, x, y, w, h, cols, ch=CHIP_H):
    _card(c, x, y, w, h)
    c.texto(x + PAD, y + 14 + _cap(NEG, 26), "TODOS OS SERVICOS", NEG, 26, ESCURO)
    # legenda com as quatro formas, a direita (so se couber ao lado do titulo)
    xd = x + w - PAD
    legenda = (("desconhecido", "n/d"), ("falha", "falha"), ("parado", "parado"), ("ativo", "ativo"))
    larg_leg = sum(int(c.medir(n, REG, 26)) + 8 + 22 + 22 for _, n in legenda)
    if larg_leg + c.medir("TODOS OS SERVICOS", NEG, 26) + 2 * PAD + 30 > w:
        legenda = ()
    for est, nome in legenda:
        wt = int(c.medir(nome, REG, 26))
        c.texto(xd, y + 14 + _cap(REG, 26), nome, REG, 26, ESCURO, alinhar="dir")
        _forma(c, xd - wt - 8 - 22, y + 14 + _cap(REG, 26) - 20, 22, est)
        xd -= wt + 8 + 22 + 22
    cw = (w - 2 * PAD) // cols
    for i, it in enumerate(itens):
        cx = x + PAD + (i % cols) * cw
        yc = y + 52 + (i // cols) * ch + ch // 2
        e = it.get("estado")
        _forma(c, cx, yc - 11, 22, e)
        fonte = NEG if e == "falha" else REG
        _texto_c(c, cx + 32, yc, _ajustar(c, it.get("rotulo", "?"), fonte, 26, cw - 32 - 12), fonte, 26,
                 PRETO if e != "desconhecido" else MEDIO)


# --------------------------------------------------------------- ragnarok (1 linha)

def _linha_ragnarok(c, m, x, y, w, h):
    rag, portas = m.get("ragnarok"), m.get("portas")
    portas = [p for p in portas if isinstance(p, dict)] if isinstance(portas, list) else []
    _card(c, x, y, w, h)
    yc = y + h // 2
    parado = _ok(rag) and bool(rag.get("parado"))
    partes = ["RAGNAROK"]
    if rag is not None:
        if _ok(rag) and _num(rag.get("jogadores")) is not None:
            n = int(rag["jogadores"])
            partes.append("%d jogador%s" % (n, "" if n == 1 else "es"))
        else:
            partes.append("n/d")
        if parado:
            idade = rag.get("idade_s")
            partes.append("PARADO %d min" % (idade // 60) if isinstance(idade, int) and idade >= 60 else "PARADO")
    txt = "  ·  ".join(partes)
    # portas a direita: "LOGIN ok  CHAR ok  MAP FALHA", cada uma com a forma
    xd = x + w - PAD
    usados = 0
    for p in reversed(portas):
        ok = bool(p.get("aberto"))
        rot = _ajustar(c, p.get("rotulo", "?"), NEG, 26, 140) + (" ok" if ok else " FALHA")
        wt = int(c.medir(rot, NEG, 26))
        c.texto(xd, yc + _cap(NEG, 26) // 2, rot, NEG, 26, PRETO, alinhar="dir")
        _forma_ok(c, xd - wt - 8 - 22, yc - 11, 22, ok)
        xd -= wt + 8 + 22 + 26
        usados += wt + 8 + 22 + 26
    _texto_c(c, x + PAD, yc, _ajustar(c, txt, NEG, 26, w - 2 * PAD - usados - 20), NEG, 26,
             MEDIO if parado else PRETO)


# ----------------------------------------------------- claude / S10 (1 linha)

H_LINHA_CLAUDE_S10 = 60
CARGA_CURTA = {"charging": "carreg.", "full": "cheia", "discharging": "bat.", "not_charging": "bat."}
MARCAS_S10 = (("usb", "USB"), ("adb_sem_fio", "sem fio"), ("vnc", "VNC"))


def _pct_txt(j):
    """"42%" de uma janela de limite; renovado vale 0%; sem numero -> "n/d"."""
    j = j if isinstance(j, dict) else None
    pct = _num(j.get("pct")) if j else None
    if pct is None:
        return "n/d"
    return "0%" if j.get("renovado") is True else "%d%%" % round(min(100.0, max(0.0, float(pct))))


def _linha_claude_s10(c, m, x, y, w, h):
    """Uma linha: icone Claude, 5h e semanal, bateria do S10 com estado de carga e marcas USB/sem fio/VNC.
    Parte ausente em `m` some da linha."""
    _card(c, x, y, w, h)
    yc = y + h // 2
    xe, xd = x + PAD, x + w - PAD
    s = m.get("s10")
    if "s10" in m:
        usavel = _ok(s) and s.get("velho") is not True
        cam = s.get("caminhos") if usavel and isinstance(s.get("caminhos"), dict) else {}
        for chave, rotulo in reversed(MARCAS_S10):
            v = cam.get(chave)
            c.texto(xd, yc + _cap(NEG, 26) // 2, rotulo, NEG, 26, PRETO, alinhar="dir")
            xd -= int(c.medir(rotulo, NEG, 26)) + 8 + 22
            _forma(c, xd, yc - 11, 22, None if not usavel or not isinstance(v, bool) else ("ativo" if v else "falha"))
            xd -= 22
    partes = []  # (texto, cor)
    if "claude" in m:
        cl = m["claude"] if isinstance(m["claude"], dict) else {}
        lim = cl.get("limites")
        lim = lim if _ok(lim) else {}
        txt = "5h %s  ·  sem %s" % (_pct_txt(lim.get("cinco_horas")), _pct_txt(lim.get("semanal")))
        velho = lim.get("velho") is True
        partes.append([txt, MEDIO if velho else PRETO, _idade_txt(lim.get("idade_s")) if velho else ""])
        xe += c.icone(xe, yc - 15, "claude", 30, PRETO)
        if xe > x + PAD:
            xe += 12
    if "s10" in m:
        txt = "S10 n/d"
        bat = s.get("bateria") if _ok(s) and s.get("velho") is not True else None
        if isinstance(bat, dict) and _num(bat.get("nivel")) is not None:
            txt = "S10 %d%%" % round(min(100.0, max(0.0, float(bat["nivel"]))))
            carga = CARGA_CURTA.get(bat.get("status")) if isinstance(bat.get("status"), str) else None
            txt += " " + carga if carga else ""
        partes.append([txt, PRETO, ""])
    disp = max(0, xd - xe - 20)
    sep = "  ·  "
    # a idade dos limites velhos so entra se a linha inteira couber; senao o trecho fica so cinza
    if partes and partes[0][2]:
        com_idade = sep.join(p[0] + ("  " + p[2] if p[2] else "") for p in partes)
        if c.medir(com_idade, NEG, 26) <= disp:
            partes[0][0] += "  " + partes[0][2]
    for i, (txt, cor, _idade) in enumerate(partes):
        if i:
            _texto_c(c, xe, yc, sep, NEG, 26, PRETO)
            xe += int(c.medir(sep, NEG, 26))
        txt = _ajustar(c, txt, NEG, 26, max(0, xd - xe - 20))
        _texto_c(c, xe, yc, txt, NEG, 26, cor)
        xe += int(c.medir(txt, NEG, 26))


# --------------------------------------------------------------------- resumo

TILE_PAD = 14


def _tiles(m, hist, discos):
    """4 tiles: CPU, RAM, GPU e o disco "/" (ou o primeiro)."""
    cpu, ram, gpu = m.get("cpu"), m.get("ram"), m.get("gpu")
    t_cpu = None
    if _ok(m.get("temp_cpu")) and _num(m["temp_cpu"].get("c")) is not None:
        t_cpu = "%d°C" % int(round(m["temp_cpu"]["c"]))
    tiles = [dict(rotulo="CPU", pct=_pct(lambda: cpu["pct"]), detalhe=t_cpu, serie=hist.get("cpu"))]
    det_ram = None
    if _ok(ram) and _num(ram.get("total_kb")):
        det_ram = _tamanho(ram.get("usado_kb", 0) * 1024, ram["total_kb"] * 1024, 1024)
    tiles.append(dict(rotulo="RAM", pct=_pct(lambda: ram["pct"]), detalhe=det_ram, serie=hist.get("ram")))
    if gpu is not None:
        t = _num(gpu.get("temp_c")) if isinstance(gpu, dict) else None
        tt = "%d°C" % int(round(t)) if t is not None else None
        if coletores.gpu_desativada(gpu):
            tiles.append(dict(rotulo="GPU", pct=None, desativada=True, detalhe=tt))
        else:
            vram = None
            if _ok(gpu) and _num(gpu.get("mem_usada_mb")) is not None and gpu.get("mem_total_mb"):
                vram = "VRAM " + _tamanho(gpu["mem_usada_mb"] * 10 ** 6, gpu["mem_total_mb"] * 10 ** 6)
            tiles.append(dict(rotulo="GPU", pct=_pct(lambda: gpu["util_pct"]), detalhe=tt, serie=hist.get("gpu"),
                              extra=vram))
    if discos:
        d = next((x for x in discos if x[0] == "/"), discos[0])
        rot, pct, usado, total, base, _parado = d
        det = _tamanho(usado, total, base) if total and usado is not None else None
        livre = "livre " + _bytes_txt(max(0, total - usado), base) if total and usado is not None else None
        tiles.append(dict(rotulo="DISCO " + rot, pct=pct, detalhe=det, extra=livre))
        tiles[-1]["_disco"] = d
    return tiles


def _h_tile():
    return TILE_PAD + _cap(NEG, 26) + 12 + _cap(NEG, 72) + 12 + 40 + 10 + 14 + TILE_PAD


def _tile(c, x, y, w, h, t):
    _card(c, x, y, w, h)
    ix, iw = x + TILE_PAD, w - 2 * TILE_PAD
    base_l = y + TILE_PAD + _cap(NEG, 26)
    rot = _ajustar(c, t["rotulo"], NEG, 26, iw)
    c.texto(ix, base_l, rot, NEG, 26, ESCURO)
    if t.get("detalhe"):
        det = _ajustar(c, t["detalhe"], REG, 26, iw - c.medir(rot, NEG, 26) - 12)
        c.texto(x + w - TILE_PAD, base_l, det, REG, 26, ESCURO, alinhar="dir")
    nb = base_l + 12 + _cap(NEG, 72)
    barra_y = y + h - TILE_PAD - 14
    if t.get("desativada"):
        c.texto(ix, nb, _ajustar(c, "desativada", NEG, 34, iw), NEG, 34, PRETO)
        topo_s = base_l + 12 + _cap(NEG, 72) + 12
        _texto_c(c, ix, (topo_s + barra_y - 10) // 2, "sem modelo", REG, 26, ESCURO)
        _barra(c, ix, barra_y, iw, 14, None)
        return
    pct = t["pct"]
    tam = 72 if c.medir("100", NEG, 72) + 6 + c.medir("%", NEG, 34) <= iw else 48
    if pct is None:
        c.texto(ix, base_l + 12 + _cap(NEG, tam), "n/d", NEG, tam, MEDIO)
    else:
        nb = base_l + 12 + _cap(NEG, tam)
        wn = c.texto(ix, nb, "%d" % int(round(pct)), NEG, tam, PRETO)
        c.texto(ix + wn + 6, nb, "%", NEG, 34 if tam == 72 else 26, PRETO)
    topo_s = base_l + 12 + _cap(NEG, 72) + 12
    serie = t.get("serie")
    if serie is not None and sum(1 for v in serie if _num(v) is not None) >= 4:
        _sparkline(c, ix, barra_y - 10, iw, barra_y - 10 - topo_s, serie)
    elif t.get("extra"):
        _texto_c(c, ix, (topo_s + barra_y - 10) // 2, _ajustar(c, t["extra"], REG, 26, iw), REG, 26, ESCURO)
    _barra(c, ix, barra_y, iw, 14, pct)


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
           ("ragnarok", "jogo", "RAGNAROK", ("ragnarok",)))
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


def _l_nas(m, kv, itens):
    discos = [d for d in (m.get("discos") if isinstance(m.get("discos"), list) else []) if isinstance(d, dict)
              and not _disco_raiz(d) and "erro" not in d]
    infos = [i for i in (_info_disco(d) for d in discos) if i and i[1] is not None]
    valor = "  ".join("%s %s" % (_limpar(i[0]), _p(i[1])) for i in infos)
    det = ""
    if infos:
        rot, pct, usado, total, base, _ = max(infos, key=lambda i: i[1])
        if usado is not None and total:
            det = "%s  %s" % (_limpar(rot), _tamanho(usado, total, base))
    return valor, det, bool(infos)


def _l_aparelhos(m, kv, itens):
    det = []
    bat = _p(_d(kv).get("bateria"))
    if bat:
        det.append("Kindle " + bat)
    s10 = _d(m.get("s10"))
    nivel = _p(_d(s10.get("bateria")).get("nivel")) if _ok(s10) else None
    if nivel:
        det.append("S10 " + nivel)
    return "", "  ".join(det), False  # a tailnet ainda nao tem dados (Entrega 2)


def _l_servicos(m, kv, itens):
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


def _l_nada(m, kv, itens):  # ROTINAS e GITHUB: o formato em `m` chega nas Tarefas 17 e 23
    return "", "", False


def _l_claude(m, kv, itens):
    cl = _d(m.get("claude"))
    lim = cl.get("limites")
    if not _ok(lim):
        return "", "", False
    valor = "5h %s  sem %s" % (_pct_txt(lim.get("cinco_horas")), _pct_txt(lim.get("semanal")))
    cinco = _d(lim.get("cinco_horas"))
    det = ""
    if cinco.get("renovado") is not True and cinco.get("volta_em") is not None:
        agora, tz = _agora(m)
        det = "5h " + _volta_txt(cinco["volta_em"], agora, tz)
        det = det if det != "5h " else ""
    return valor, det, True


def _l_ragnarok(m, kv, itens):
    rag = m.get("ragnarok")
    portas = m.get("portas")
    portas = [p for p in portas if isinstance(p, dict)] if isinstance(portas, list) else []
    valor = ""
    if _ok(rag) and _num(rag.get("jogadores")) is not None:
        n = int(rag["jogadores"])
        valor = "%d jogador%s" % (n, "" if n == 1 else "es")
        if rag.get("parado"):
            valor += "  parado"
    det = "  ".join("%s %s" % (_limpar(p.get("rotulo", "?")).lower(), "ok" if p.get("aberto") else "fechada")
                    for p in portas)
    return valor, det, bool(valor or det)


_CONSTRUTORES = {"atheron": _l_atheron, "nas": _l_nas, "aparelhos": _l_aparelhos, "servicos": _l_servicos,
                 "rotinas": _l_nada, "claude": _l_claude, "github": _l_nada, "ragnarok": _l_ragnarok}


def _linhas_resumo(m, itens, kv, alertas):
    """As 8 linhas da tela inicial (ordem de botoes.LINHAS_RESUMO): {"id","icone","titulo","valor","detalhe","estado"}.
    Pura e tolerante: `m`, `itens`, `kv` ou `alertas` com tipo errado so deixam a linha em "sem dados".
    `estado` = pior nivel dos alertas da linha, "ok", ou "sem_dados" (sem fonte e sem alerta)."""
    m = m if isinstance(m, dict) else {}
    saida = []
    for lid, icone, titulo, sistemas in _LINHAS:
        try:
            valor, detalhe, tem = _CONSTRUTORES[lid](m, kv, itens)
        except Exception:
            valor, detalhe, tem = "", "", False
        estado = _pior_nivel(alertas, sistemas) or ("ok" if tem else "sem_dados")
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
    c.texto(xt, base1, _ajustar(c, linha.get("titulo", ""), NEG, 26, xv - xt - 8), NEG, 26, ESCURO)
    c.texto(xv, base1, _ajustar(c, linha.get("valor", ""), NEG, 34, fim - xv), NEG, 34, MEDIO if sem else PRETO)
    det = linha.get("detalhe") or ""
    if det:
        c.texto(xv, base1 + 16 + cap_d, _ajustar(c, det, REG, 26, fim - xv), REG, 26, ESCURO)


def _desenhar_resumo(c, m, hist, itens, kv=None):
    """Tela inicial so com excecoes: cartao ATENCAO no alto (so a altura que precisa) e uma linha por sistema."""
    geo = botoes.geometria_resumo(c.largura, c.altura)
    atencao = _atencao(m, kv)
    caixa = geo["atencao"]
    h = min(_h_atencao(len(atencao)), caixa["h"] - botoes.LINHA_RESUMO_GAP)
    if h >= ATENCAO_TITULO + ATENCAO_LINHA + 14:  # tela baixa demais (so fora do Kindle): sem espaco para o cartao
        _card_atencao(c, atencao, caixa["x"], caixa["y"], caixa["w"], h)
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


def _blocos_detalhes(c, m, itens, w, hist, kv=None):
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
    # o proprio Kindle
    if kv:
        blocos.append((H_KINDLE, lambda c, x, y, h: _card_kindle(c, kv, x, y, w, h)))
    # historico (sparklines de ~15 min)
    series = [(r, hist.get(k)) for r, k in (("CPU", "cpu"), ("RAM", "ram"), ("GPU", "gpu"))
              if isinstance(hist.get(k), list) and sum(1 for v in hist[k] if _num(v) is not None) >= 4]
    if series:
        def historico(c, x, y, h):
            _card(c, x, y, w, h)
            c.texto(x + PAD, y + 14 + _cap(NEG, 26), "HISTORICO", NEG, 26, ESCURO)
            minutos = int(round(len(series[0][1]) * (hist.get("intervalo_s") or 15) / 60.0))
            c.texto(x + w - PAD, y + 14 + _cap(NEG, 26), "ultimos %d min" % minutos if minutos else "", REG, 26,
                    ESCURO, alinhar="dir")
            for i, (rot, serie) in enumerate(series):
                top = y + 52 + i * 76
                _texto_c(c, x + PAD, top + 34, rot, NEG, 26, ESCURO)
                ultimo = next((v for v in reversed(serie) if _num(v) is not None), None)
                _texto_c(c, x + w - PAD, top + 34, "%d%%" % int(round(ultimo)), NEG, 34, PRETO, "dir")
                _sparkline(c, x + PAD + 90, top + 68, w - 2 * PAD - 90 - 90, 60, serie)
        blocos.append((52 + len(series) * 76 + 8, historico))
    # servicos por grupo
    if itens:
        blocos.append((H_GRUPOS, lambda c, x, y, h: _card_grupos(c, itens, x, y, w, h)))
    # ragnarok
    if m.get("ragnarok") is not None or m.get("portas"):
        blocos.append((60, lambda c, x, y, h: _linha_ragnarok(c, m, x, y, w, h)))
    # pares
    pares = m.get("pares")
    for par in [p for p in pares if isinstance(p, dict)] if isinstance(pares, list) else []:
        blocos.append((76, lambda c, x, y, h, par=par: _card_par(c, par, x, y, w, h)))
    return blocos


H_KINDLE = 44 + 4 * 48 + 8


def _sim_nao(v, sim, nao):
    return "n/d" if v is None else (sim if v else nao)


def _card_kindle(c, kv, x, y, w, h):
    """BATERIA com barra (como MEMORIA) e mais tres linhas em duas colunas: radios, elo e sincronizacao."""
    _card(c, x, y, w, h)
    c.texto(x + PAD, y + 14 + _cap(NEG, 26), "KINDLE", NEG, 26, ESCURO)
    bat = kv.get("bateria")
    det = ["carregando" if kv.get("carregando") else "na bateria"]
    if kv.get("temp_c") is not None:
        det.append("%d°C" % kv["temp_c"])
    if kv.get("autonomia"):
        det.append(kv["autonomia"])
    _linha_barra(c, x + PAD, y + 44 + 24, w - 2 * PAD, "BATERIA", bat, " · ".join(det), 160)
    if kv.get("wifi_ok"):
        wifi = "%d/5" % kv["wifi"] if kv.get("wifi") is not None else "conectado"
    else:
        wifi = "desconectado"
    if kv.get("bt") is None:
        bt = "n/d"
    elif not kv["bt"]:
        bt = "desligado"
    else:
        n = kv.get("bt_conectados") or 0
        bt = "ligado" if not n else "%d conectado%s" % (n, "s" if n > 1 else "")
    elo = kv.get("tailscale") or "n/d"
    if kv.get("latencia"):
        elo += " · " + kv["latencia"]
    pares = (("WI-FI", wifi), ("BLUETOOTH", bt),
             ("AVIAO", _sim_nao(kv.get("aviao"), "ligado", "desligado")), ("ELO", elo),
             ("RELOGIO", kv.get("relogio") or "n/d"), ("WHISPERSYNC", kv.get("whispersync") or "n/d"))
    cw = (w - 2 * PAD) // 2
    for i, (k, v) in enumerate(pares):
        _kv(c, x + PAD + (i % 2) * cw, y + 44 + 48 + (i // 2) * 48 + 24, cw - 16, k, v, tam=26 if len(v) > 14 else 34)


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


def _desenhar_detalhes(c, m, itens, hist, kv=None):
    w = c.largura - 2 * MARGEM
    topo, limite = botoes.TOPO, botoes.limite(c.altura)
    blocos = _blocos_detalhes(c, m, itens, w, hist, kv)
    # se nao couber, descarta do fim (pares, depois ragnarok...) em vez de sair da imagem
    while blocos and sum(b[0] for b in blocos) + GAP * (len(blocos) - 1) > limite - topo:
        blocos.pop()
    if not blocos:
        return
    folga = limite - topo - sum(b[0] for b in blocos) - GAP * (len(blocos) - 1)
    extra = min(24, folga // max(1, len(blocos)))
    y = topo
    for h, fn in blocos:
        fn(c, MARGEM, y, h)
        y += h + GAP + extra


# --------------------------------------------------------------------- acoes

def _card_grupos(c, itens, x, y, w, h):
    cont = {}
    for it in itens:
        t = cont.setdefault(it.get("grupo"), [0, 0])
        t[1] += 1
        t[0] += 1 if it.get("estado") == "ativo" else 0
    grupos = [g for g in servicos.GRUPOS if g in cont]
    _card(c, x, y, w, h)
    c.texto(x + PAD, y + 14 + _cap(NEG, 26), "SERVICOS POR GRUPO", NEG, 26, ESCURO)
    cw = (w - 2 * PAD) // max(1, len(grupos))
    titulos = {g: servicos.TITULOS_GRUPO[g] for g in grupos}
    if any(c.medir(t, NEG, 26) > cw - 10 for t in titulos.values()):  # tela estreita: nomes curtos
        titulos = {g: g.upper() for g in grupos}
    for i, g in enumerate(grupos):
        gx = x + PAD + i * cw
        a, t = cont[g]
        _texto_c(c, gx, y + 44 + 22, _ajustar(c, titulos[g], NEG, 26, cw - 10), NEG, 26, ESCURO)
        txt = "%d/%d" % (a, t)
        _texto_c(c, gx, y + 44 + 22 + 40, txt, NEG, 34, PRETO)
        if a != t:  # sublinhado: nem todos ativos
            c.retangulo(gx, y + 44 + 22 + 40 + 20, int(c.medir(txt, NEG, 34)), 3, PRETO)


H_GRUPOS = 44 + 22 + 40 + 34


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


def _desenhar_comandos(c, m, itens, modo=None, kv=None):
    """Grade das acoes rapidas; abaixo os ultimos comandos, Atencao e (se couber) a grade de todos os servicos."""
    geo = botoes.geometria_comandos(c.largura, c.altura)
    w = c.largura - 2 * MARGEM
    limite = botoes.limite(c.altura)
    c.texto(MARGEM, geo["rapidas_titulo_y"] + 4 + _cap(NEG, 26), "ACOES RAPIDAS", NEG, 26, ESCURO)
    c.texto(MARGEM, geo["ajustes_titulo_y"] + 4 + _cap(NEG, 26), "AJUSTES", NEG, 26, ESCURO)
    desc = _ajustar(c, perfis.descricao(modo), REG, 34, w)
    c.texto(MARGEM, geo["ajustes_desc_y"] + (geo["ajustes_desc_h"] + _cap(REG, 34)) // 2, desc, REG, 34, ESCURO)
    rh = geo["linha_h"]
    y = geo["fim_botoes"] + GAP
    reserva = (_h_atencao(1) + GAP) if itens else 0  # Atencao sempre ganha ao menos uma linha
    y = _ultimos(c, m, MARGEM, y, w, rh, limite - reserva) + GAP
    if not itens or limite - y < _h_atencao(1):
        return
    atencao = _atencao(m, kv)
    kmax = max(1, (limite - y - ATENCAO_TITULO - 14) // ATENCAO_LINHA)
    ah = _h_atencao(len(atencao), min(_linhas_atencao(len(atencao)), kmax)) if atencao else _h_atencao(0)
    _card_atencao(c, atencao, MARGEM, y, w, ah)
    y += ah + GAP
    for cols in (3, 4):  # todos os servicos, se sobrar espaco; senao so o resumo por grupo
        if limite - y >= _chips_h(len(itens), cols):
            _card_chips(c, itens, MARGEM, y, w, _chips_h(len(itens), cols), cols)
            return
    if limite - y >= H_GRUPOS:
        _card_grupos(c, itens, MARGEM, y, w, H_GRUPOS)


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


def _cabecalho_card(c, x, y, w, titulo, velho=False, idade_s=None, icone=False):
    """Linha de titulo de um cartao (64 px): icone opcional, titulo e, se os dados estao velhos, a idade em cinza."""
    tx = x + PAD
    if icone:
        tx += (c.icone(x + PAD, y + 12, "claude", 40, PRETO) or 0) + 12
    _texto_c(c, tx, y + 32, titulo, NEG, 34, PRETO)
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
    yy = _cabecalho_card(c, x, y, w, "Claude", velho, lim.get("idade_s") if lim else None, icone=True)
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
        _cabecalho_card(c, x, y, w, "S10", False)
        _texto_c(c, x + PAD, y + 64 + 40, "n/d", REG, 34, ESCURO)
        return
    velho = s.get("velho") is True
    titulo = "S10 sem dados %s" % _idade_txt(s.get("idade_s")) if velho else "S10"
    yy = _cabecalho_card(c, x, y, w, titulo.strip(), False)
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


def _desenhar_claude(c, m):
    w = c.largura - 2 * MARGEM
    limite = botoes.limite(c.altura)
    tem_c, tem_s = "claude" in m, "s10" in m
    if not (tem_c or tem_s):
        c.texto(c.largura // 2, (botoes.TOPO + limite) // 2 + _cap(NEG, 34) // 2, "Claude/S10 desligado na config",
                NEG, 34, ESCURO, "centro")
        return
    y = botoes.TOPO
    if tem_c:
        h = min(CLAUDE_H, limite - y)
        _card_claude(c, m["claude"], MARGEM, y, w, h, _agora(m))
        y += h + GAP
    if tem_s:
        h = min(_h_s10(m["s10"]), limite - y)
        if h >= 140:
            _card_s10(c, m["s10"], MARGEM, y, w, h)


def _desenhar_aparelhos(c, m):
    """Provisorio (Tarefa 9 desenha a pagina de verdade)."""
    y = (botoes.TOPO + botoes.limite(c.altura)) // 2 + _cap(NEG, 34) // 2
    c.texto(c.largura // 2, y, "Aparelhos", NEG, 34, ESCURO, "centro")


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
        _desenhar_detalhes(c, m, itens, hist, kv)
    elif pagina == "claude":
        _desenhar_claude(c, m)
    elif pagina == "aparelhos":
        _desenhar_aparelhos(c, m)
    else:
        _desenhar_comandos(c, m, itens, modo, kv)
    _desenhar_botoes(c, pagina, armado, p, itens, modo)


def render_png(metricas, historico=None, largura=1236, altura=1648, pagina="resumo", armado=None, p=1, modo=None,
               kindle=None):
    """Devolve a tela como PNG 8-bit em tons de cinza."""
    c = Canvas(largura, altura)
    desenhar(c, metricas, historico, pagina, armado, p, modo, kindle)
    return c.para_png()
