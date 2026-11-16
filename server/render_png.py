"""Tela PNG (retrato, tons de cinza) do kindle-monitor. Funcoes puras: metricas -> bytes PNG.

Layout em blocos empilhados na vertical; se nao couber, `desenhar` tenta densidades menores
(numeros e espacamentos menores, servicos em duas colunas) e, no limite, omite itens
("+N servicos") em vez de cortar texto ou desenhar fora da imagem.
"""
import unicodedata
from datetime import datetime

import coletores
import formato
from canvas import BRANCO, CLARO, ESCURO, MEDIO, PRETO, TRILHO, Canvas, altura_capital

NEG, REG, MONO = "sans-bold", "sans", "mono"
MARGEM = 48
ALTURA_CABECALHO = 150
BARRA_RAIO = 8
HIST_MAX = 60

# Densidades, da mais folgada a mais apertada.
DENSIDADES = (
    dict(num=72, pct=34, barra=26, esp_linha=26, esp_secao=34, svc_h=46, svc_cols=1, card_h=150, io_h=44),
    dict(num=72, pct=34, barra=26, esp_linha=16, esp_secao=26, svc_h=42, svc_cols=2, card_h=146, io_h=42),
    dict(num=48, pct=26, barra=24, esp_linha=14, esp_secao=22, svc_h=40, svc_cols=2, card_h=140, io_h=40),
    dict(num=48, pct=26, barra=20, esp_linha=10, esp_secao=16, svc_h=36, svc_cols=2, card_h=134, io_h=36),
)


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
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _pct(fn):
    try:
        v = _num(fn())
        return None if v is None else min(100.0, max(0.0, float(v)))
    except Exception:
        return None


def _tamanho(usado, total, base=1000):
    """'3.1 / 8.0 GB' (mesma unidade para os dois, escolhida pelo total; base 1000 ou 1024)."""
    un = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    t = float(total)
    while t >= base and i < len(un) - 1:
        t /= float(base)
        i += 1
    f = float(base) ** i
    fmt = "%.0f" if t >= 100 else "%.1f"
    return (fmt + " / " + fmt + " %s") % (usado / f, total / f, un[i])


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


# --------------------------------------------------------------- componentes

def _barra(c, x, y, w, h, pct):
    """Trilho cinza claro com contorno e preenchimento preto, cantos levemente arredondados."""
    c.contorno_arredondado(x, y, w, h, BARRA_RAIO, ESCURO, 2, TRILHO)
    if pct is None:
        return
    iw, ih = w - 4, h - 4
    for marca in (25, 50, 75):
        c.retangulo(x + 2 + int(iw * marca / 100.0) - 1, y + 4, 2, ih - 4, CLARO)
    cheio = int(round(iw * pct / 100.0))
    if cheio > 0:
        c.retangulo_arredondado(x + 2, y + 2, max(cheio, 4), ih, max(2, BARRA_RAIO - 2), PRETO)


def _numero(c, x_dir, base, pct, tam, tam_pct, cor=PRETO):
    """Numero grande com o '%' menor, alinhado a direita em x_dir, sobre a linha de base."""
    if pct is None:
        c.texto(x_dir, base, "n/d", NEG, tam, MEDIO, alinhar="dir")
        return
    wp = c.medir("%", NEG, tam_pct)
    c.texto(x_dir, base, "%", NEG, tam_pct, cor, alinhar="dir")
    c.texto(x_dir - wp - 4, base, "%d" % int(round(pct)), NEG, tam, cor, alinhar="dir")


def _sparkline(c, x, y_base, w, h, serie):
    """Area + linha do historico (0..100%), a amostra mais recente na direita."""
    pts = []
    n = len(serie)
    passo = w / float(max(2, n) - 1)  # preenche a largura; compacta ate chegar a 60 amostras
    for i, v in enumerate(serie):
        v = _num(v)
        if v is None:
            continue
        px = x + w - (n - 1 - i) * passo
        py = y_base - 3 - min(100.0, max(0.0, v)) / 100.0 * (h - 6)
        pts.append((px, py))
    c.retangulo(x, y_base - 1, w, 2, CLARO)
    if len(pts) < 2:
        return
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        for cx in range(int(round(xa)), int(round(xb)) + 1):
            t = 0 if xb == xa else (cx - xa) / (xb - xa)
            top = int(ya + (yb - ya) * t)
            c.retangulo(cx, top, 1, int(y_base - 1 - top), TRILHO)
    c.polilinha([(int(round(px)), int(round(py))) for px, py in pts], PRETO, 3)
    c.circulo(int(round(pts[-1][0])), int(round(pts[-1][1])), 5, PRETO)


def _linha_metrica(c, x, y, w, d, rotulo, pct, detalhe=None, serie=None):
    """Rotulo pequeno a esquerda, numero grande a direita, barra grossa embaixo."""
    cap = altura_capital(NEG, d["num"])
    base = y + cap
    num_w = c.medir("100", NEG, d["num"]) + 4 + c.medir("%", NEG, d["pct"])
    rotulo_w = 170
    tam_rot = 34 if c.medir(_limpar(rotulo), NEG, 34) <= rotulo_w - 10 else 26  # "NAS SSD" cabe a 26
    c.texto(x, base, _ajustar(c, rotulo, NEG, tam_rot, rotulo_w - 10), NEG, tam_rot, ESCURO)
    _numero(c, x + w, base, pct, d["num"], d["pct"])
    x0, x1 = x + rotulo_w + 10, x + w - num_w - 30
    if detalhe:
        # valor em x0 (como nas outras linhas); o sparkline, se houver, comeca depois do texto
        txt = _ajustar(c, detalhe, REG, 26, x1 - x0)
        c.texto(x0, base, txt, REG, 26, ESCURO)
        x0 += int(c.medir(txt, REG, 26)) + 28
    if serie is not None and sum(1 for v in serie if _num(v) is not None) >= 4 and x1 - x0 > 100:
        _sparkline(c, x0, base, x1 - x0, cap, serie)
    _barra(c, x, base + 14, w, d["barra"], pct)


def _linha_desativada(c, x, y, w, d, rotulo, temp):
    """GPU sem nada carregado: uma linha so, 'desativada' no lugar do numero grande (sem barra)."""
    base = y + altura_capital(NEG, d["num"])
    c.texto(x, base, rotulo, NEG, 34, ESCURO)
    txt = "desativada"
    if _num(temp) is not None:
        txt += "  \u00b7  %d\u00b0C" % int(round(temp))
    c.texto(x + w, base, txt, NEG, 48, ESCURO, alinhar="dir")


def _pilula(c, x, y, w, h, rotulo, aberto):
    """Aberta: preenchida de preto com texto branco. Fechada: so contorno, com um X."""
    if aberto:
        c.retangulo_arredondado(x, y, w, h, h // 2, PRETO)
        base = y + (h + altura_capital(NEG, 34)) // 2
        c.texto(x + w // 2, base, rotulo, NEG, 34, BRANCO, alinhar="centro")
        return
    c.contorno_arredondado(x, y, w, h, h // 2, PRETO, 3, BRANCO)
    lado = 20
    tw = c.medir(rotulo, NEG, 34)
    ini = x + (w - (lado + 12 + tw)) / 2.0
    base = y + (h + altura_capital(NEG, 34)) // 2
    c.cruz_x(int(ini), y + (h - lado) // 2, lado, PRETO, 4)
    c.texto(int(ini) + lado + 12, base, rotulo, NEG, 34, PRETO)


def _icone_servico(c, x, y, lado, ok):
    if ok:
        c.circulo(x + lado // 2, y + lado // 2, lado // 2 - 1, PRETO)
    else:
        c.contorno(x, y, lado, lado, PRETO, 3)
        c.cruz_x(x + 6, y + 6, lado - 12, PRETO, 3)


# ----------------------------------------------------------------- blocos

def _bloco_metricas(m, hist, d, w):
    linhas = []  # (rotulo, pct, detalhe, serie)
    cpu, ram, swap, gpu = m.get("cpu"), m.get("ram"), m.get("swap"), m.get("gpu")
    linhas.append(("CPU", _pct(lambda: cpu["pct"]), None, hist.get("cpu")))
    det_ram = None
    if _ok(ram) and _num(ram.get("total_kb")):
        det_ram = _tamanho(ram.get("usado_kb", 0) * 1024, ram["total_kb"] * 1024, 1024)  # GiB, como o /tela.txt
    linhas.append(("RAM", _pct(lambda: ram["pct"]), det_ram, hist.get("ram")))
    if gpu is not None and coletores.gpu_desativada(gpu):
        linhas.append(("GPU", "desativada", gpu.get("temp_c"), None))
    elif gpu is not None:
        linhas.append(("GPU", _pct(lambda: gpu["util_pct"]), None, hist.get("gpu")))
        if _ok(gpu) and _num(gpu.get("mem_usada_mb")) is not None and gpu.get("mem_total_mb"):
            linhas.append(("VRAM", _pct(lambda: gpu["mem_usada_mb"] * 100.0 / gpu["mem_total_mb"]),
                           _tamanho(gpu["mem_usada_mb"] * 10**6, gpu["mem_total_mb"] * 10**6), None))
    if swap is not None and not (_ok(swap) and swap.get("total_kb") == 0):
        det = None
        if _ok(swap) and _num(swap.get("total_kb")):
            det = _tamanho(swap.get("usado_kb", 0) * 1024, swap["total_kb"] * 1024, 1024)
        linhas.append(("SWAP", _pct(lambda: swap["pct"]), det, None))
    discos = m.get("discos")
    if isinstance(discos, list):
        for dk in discos:
            if not isinstance(dk, dict):
                continue
            det = None
            if _num(dk.get("total_b")) and _num(dk.get("usado_b")) is not None:
                det = _tamanho(dk["usado_b"], dk["total_b"], 1024 if dk.get("base") == 1024 else 1000)
                if dk.get("parado"):
                    det += "  \u00b7  parado"
            linhas.append((str(dk.get("rotulo", "?")), _pct(lambda: dk["pct"]), det, None))
    cap = altura_capital(NEG, d["num"])
    h_linha = cap + 14 + d["barra"]
    blocos = []
    for i, (rot, pct, det, serie) in enumerate(linhas):
        def desenhar(c, y, x, rot=rot, pct=pct, det=det, serie=serie):
            if pct == "desativada":
                _linha_desativada(c, x, y, w, d, rot, det)
            else:
                _linha_metrica(c, x, y, w, d, rot, pct, det, serie)
        h = cap + 16 if pct == "desativada" else h_linha
        blocos.append((h, desenhar, d["esp_linha"] if i < len(linhas) - 1 else d["esp_secao"], None))
    return blocos


def _bloco_info(m, d, w):
    partes_temp = []
    try:
        if _ok(m.get("temp_cpu")):
            partes_temp.append("CPU %d°C" % int(round(m["temp_cpu"]["c"])))
        g = m.get("gpu")
        if _ok(g) and _num(g.get("temp_c")) is not None:
            partes_temp.append("GPU %d°C" % int(round(g["temp_c"])))
    except Exception:
        partes_temp = []
    up = None
    try:
        up = _uptime(m["uptime"]["segundos"])
    except Exception:
        pass
    carga = None
    try:
        cg = m["carga"]
        carga = "%.2f  %.2f  %.2f" % (cg["1m"], cg["5m"], cg["15m"])
    except Exception:
        pass
    if not (partes_temp or up or carga):
        return []
    temp = "  \u00b7  ".join(partes_temp)
    linha_h = 46
    cap = altura_capital(NEG, 34)

    def itens(c, tam):
        """[(etiqueta, valor)] na ordem TEMP, CARGA, UP, com a largura de cada um."""
        r = []
        for etq, val in (("TEMP", temp), ("CARGA", carga), ("UP", up)):
            if val:
                r.append((etq, val, c.medir(etq, NEG, 26) + 14 + c.medir(val, NEG, tam)))
        return r

    def cabe_numa_linha(c, tam):
        it = itens(c, tam)
        return sum(i[2] for i in it) + 36 * (len(it) - 1) <= w

    def desenhar(c, y, x):
        if cabe_numa_linha(c, 34):
            tam = 34
            it = itens(c, tam)
            livre = w - sum(i[2] for i in it)
            gap = livre / float(max(1, len(it) - 1)) if len(it) > 1 else 0
            base = y + altura_capital(NEG, tam)
            px = float(x)
            for etq, val, largura in it:
                c.texto(int(px), base, etq, NEG, 26, ESCURO)
                c.texto(int(px + c.medir(etq, NEG, 26) + 14), base, val, NEG, tam, PRETO)
                px += largura + gap
            return
        base = y + cap
        px = x
        if partes_temp:
            c.texto(px, base, "TEMP", NEG, 26, ESCURO)
            px += c.medir("TEMP", NEG, 26) + 14
            c.texto(px, base, temp, NEG, 34, PRETO)
        if up:
            c.texto(x + w, base, up, NEG, 34, PRETO, alinhar="dir")
            c.texto(x + w - c.medir(up, NEG, 34) - 14, base, "UP", NEG, 26, ESCURO, alinhar="dir")
        if carga:
            y2 = base + (linha_h if (partes_temp or up) else 0)
            c.texto(x, y2, "CARGA", NEG, 26, ESCURO)
            c.texto(x + c.medir("CARGA", NEG, 26) + 14, y2, carga, NEG, 34, PRETO)

    # height is decided at layout time (no canvas yet): measure with a throwaway one
    medidor = Canvas(8, 8)
    if cabe_numa_linha(medidor, 34):
        h = altura_capital(NEG, 34)
    else:
        h = cap + (linha_h if ((partes_temp or up) and carga) else 0)
    return [(h, desenhar, d["esp_secao"], None)]


def _bloco_io(m, d, w):
    """Taxas de disco (L = leitura, E = escrita) e de rede (rx/tx): uma tabela compacta de 1 ou 2 colunas."""
    io = m.get("io")
    if not _ok(io):
        return []
    grupos = []  # (titulo, [(rotulo, (tag1, val1), (tag2, val2))])
    for chave, titulo, tags, campos in (("discos", "DISCO", ("L", "E"), ("leitura_bps", "escrita_bps")),
                                         ("redes", "REDE", ("rx", "tx"), ("rx_bps", "tx_bps"))):
        lista = io.get(chave)
        linhas = []
        for it in lista if isinstance(lista, list) else []:
            if isinstance(it, dict):
                linhas.append((_limpar(it.get("rotulo", "?")),
                               (tags[0], formato.taxa(it.get(campos[0]))), (tags[1], formato.taxa(it.get(campos[1])))))
        if linhas:
            grupos.append((titulo, linhas))
    if not grupos:
        return []
    h_linha = d["io_h"]
    tam = tam_tag = tam_rot = 26  # embedded fonts only come in 26 and 34 px (above 34: bold only)
    medidor = Canvas(8, 8)
    titulo_w = max(medidor.medir(t, NEG, 26) for t, _ in grupos) + 14
    todas = [l for _, ls in grupos for l in ls]
    rot_w = max(medidor.medir(l[0], NEG, tam_rot) for l in todas) + 14

    def larg_par(par):
        return medidor.medir(par[0], REG, tam_tag) + 8 + medidor.medir(par[1], NEG, tam)
    a_w = max(larg_par(l[1]) for l in todas) + 18
    b_w = max(larg_par(l[2]) for l in todas)
    celula = int(rot_w + a_w + b_w)
    gap_col = 20
    cols = 2 if 2 * celula + gap_col <= w - titulo_w else 1
    cw = (w - titulo_w - gap_col * (cols - 1)) // cols
    n_linhas = sum(-(-len(ls) // cols) for _, ls in grupos)
    h = n_linhas * h_linha

    def desenhar(c, y, x):
        yy = y
        for titulo, ls in grupos:
            n = -(-len(ls) // cols)
            c.texto(x, yy + (h_linha + altura_capital(NEG, 26)) // 2, titulo, NEG, 26, ESCURO)
            for i, (rot, a, b) in enumerate(ls):
                cx = x + titulo_w + (i % cols) * (cw + gap_col)
                base = yy + (i // cols) * h_linha + (h_linha + altura_capital(NEG, tam)) // 2
                c.texto(cx, base, _ajustar(c, rot, NEG, tam_rot, rot_w - 6), NEG, tam_rot, PRETO)
                for k, (tag, val) in enumerate((a, b)):
                    px = cx + rot_w + (0 if k == 0 else a_w)
                    c.texto(px, base, tag, REG, tam_tag, ESCURO)
                    c.texto(px + c.medir(tag, REG, tam_tag) + 8, base, val, NEG, tam, PRETO)
            yy += n * h_linha

    return [(h, desenhar, d["esp_linha"] + 6, None)]


def _bloco_ragnarok(m, d, w):
    rag, portas = m.get("ragnarok"), m.get("portas")
    portas = [p for p in portas if isinstance(p, dict)] if isinstance(portas, list) else []
    if rag is None and not portas:
        return []
    parado = _ok(rag) and bool(rag.get("parado"))
    cap_n = altura_capital(NEG, 140)
    pil_h = 64
    corpo = cap_n
    if parado:
        corpo = max(corpo, pil_h + 14 + 40)
    titulo_h = altura_capital(NEG, 26) + 18
    h = titulo_h + corpo

    def desenhar(c, y, x):
        c.texto(x, y + altura_capital(NEG, 26),
                "RAGNAROK  \u00b7  " + ("jogadores online" if rag is not None else "portas"), NEG, 26, ESCURO)
        yc = y + titulo_h
        pil_y = 4 if parado else max(0, (cap_n - pil_h) // 2)
        pil_w, gap = 200, 16
        px0 = x + w - (len(portas) * pil_w + max(0, len(portas) - 1) * gap)
        if rag is not None:
            if _ok(rag) and _num(rag.get("jogadores")) is not None:
                n, cor = "%d" % int(rag["jogadores"]), (MEDIO if parado else PRETO)
                c.texto(x, yc + cap_n, n, NEG, 140, cor)
            else:
                c.texto(x, yc + cap_n, "n/d", NEG, 72, MEDIO)
        for i, p in enumerate(portas):
            rot = _ajustar(c, p.get("rotulo", "?"), NEG, 34, pil_w - 70)
            _pilula(c, px0 + i * (pil_w + gap), yc + pil_y, pil_w, pil_h, rot, bool(p.get("aberto")))
        if parado:
            idade = rag.get("idade_s")
            txt = "PARADO %d min" % (idade // 60) if isinstance(idade, int) and idade >= 60 else "PARADO"
            bw = int(c.medir(txt, NEG, 26)) + 36
            bx = x + w - bw
            by = yc + pil_y + pil_h + 14
            c.contorno_arredondado(bx, by, bw, 40, 8, PRETO, 3, BRANCO)
            c.texto(bx + bw // 2, by + (40 + altura_capital(NEG, 26)) // 2, txt, NEG, 26, PRETO, alinhar="centro")

    return [(h, desenhar, d["esp_secao"], None)]


def _bloco_servicos(m, d, w, max_itens=None):
    servicos = m.get("servicos")
    if servicos is None:
        return []
    cap = altura_capital(NEG, 26)
    titulo_h = cap + 16
    if not isinstance(servicos, list):
        def desenhar_nd(c, y, x):
            c.texto(x, y + cap, "SERVICOS", NEG, 26, ESCURO)
            c.texto(x + 190, y + cap, "n/d", NEG, 26, MEDIO)
        return [(cap, desenhar_nd, d["esp_secao"], None)]
    itens = []
    for s in servicos:
        if not isinstance(s, dict):
            continue
        estado = "n/d" if "erro" in s else ("ok" if s.get("ativo") else "FALHA")
        nome = str(s.get("nome", "?"))
        if nome.endswith(".service") and len(nome) > 8:
            nome = nome[:-8]  # todo mundo e .service: economiza largura
        itens.append((nome, estado))
    if not itens:
        return []
    itens.sort(key=lambda t: t[1] == "ok")  # falhas primeiro (estavel)
    extra = 0
    if max_itens is not None and len(itens) > max_itens:
        extra = len(itens) - max_itens
        itens = itens[:max_itens]
    cols = d["svc_cols"] if len(itens) + (1 if extra else 0) > 3 else 1
    n_linhas = -(-len(itens) // cols) + (1 if extra else 0)
    h = titulo_h + n_linhas * d["svc_h"]

    def desenhar(c, y, x):
        falhas = sum(1 for _, e in itens if e != "ok")
        c.texto(x, y + cap, "SERVICOS", NEG, 26, ESCURO)
        if falhas:
            c.texto(x + w, y + cap, "%d com problema" % falhas, NEG, 26, PRETO, alinhar="dir")
        gap = 24
        cw = (w - gap * (cols - 1)) // cols
        sh = d["svc_h"]
        y0 = y + titulo_h
        for i, (nome, est) in enumerate(itens):
            cx = x + (i % cols) * (cw + gap)
            cy = y0 + (i // cols) * sh
            ok = est == "ok"
            if not ok:
                c.retangulo_arredondado(cx, cy + 2, cw, sh - 4, 8, TRILHO)
            lado = 24
            _icone_servico(c, cx + 10, cy + (sh - lado) // 2, lado, ok)
            base = cy + (sh + altura_capital(MONO, 26)) // 2
            reservado = 0 if ok else c.medir(est, NEG, 26) + 26
            c.texto(cx + 10 + lado + 14, base, _ajustar(c, nome, MONO, 26, cw - 10 - lado - 14 - 12 - reservado),
                    MONO, 26, PRETO)
            if not ok:
                c.texto(cx + cw - 14, base, est, NEG, 26, PRETO, alinhar="dir")
        if extra:
            yb = y0 + (-(-len(itens) // cols)) * sh
            c.texto(x + 10, yb + (sh + altura_capital(NEG, 26)) // 2, "+%d servicos" % extra, NEG, 26, ESCURO)

    return [(h, desenhar, d["esp_secao"], None)]


def _mini(c, x, y, w, rotulo, pct, tam=48, tam_pct=26):
    """Medidor compacto do cartao de par: rotulo + numero + barra fina."""
    cap = altura_capital(NEG, tam)
    base = y + cap
    c.texto(x, base, rotulo, NEG, 26, ESCURO)
    _numero(c, x + w, base, pct, tam, tam_pct)
    _barra(c, x, base + 12, w, 16, pct)


def _bloco_pares(m, d, w, max_pares=None):
    pares = m.get("pares")
    if not isinstance(pares, list):
        return []
    pares = [p for p in pares if isinstance(p, dict)]
    if max_pares is not None:
        pares = pares[:max_pares]
    blocos = []
    for i, par in enumerate(pares):
        nome = str(par.get("nome", "?"))
        pm = par.get("metricas") if par.get("ok") and isinstance(par.get("metricas"), dict) else None
        ultimo = i == len(pares) - 1
        gap = d["esp_secao"] if ultimo else d["esp_linha"] + 6
        if pm is None:
            def desenhar_fora(c, y, x, nome=nome):
                c.contorno_arredondado(x, y, w, 84, 16, MEDIO, 3, BRANCO)
                c.texto(x + 22, y + 56, _ajustar(c, nome, NEG, 34, w // 2), NEG, 34, ESCURO)
                c.texto(x + w - 22, y + 56, "sem resposta", NEG, 26, MEDIO, alinhar="dir")
            blocos.append((84, desenhar_fora, gap, None))
            continue

        def desenhar_par(c, y, x, nome=nome, pm=pm):
            c.contorno_arredondado(x, y, w, d["card_h"], 16, PRETO, 3, BRANCO)
            pad = 22
            base = y + 18 + altura_capital(NEG, 34)
            info = []
            try:
                if _ok(pm.get("temp_cpu")):
                    info.append("%d°C" % int(round(pm["temp_cpu"]["c"])))
            except Exception:
                pass
            try:
                info.append("UP " + _uptime(pm["uptime"]["segundos"]))
            except Exception:
                pass
            txt_info = "  ·  ".join(info)
            iw = c.medir(txt_info, REG, 26) if txt_info else 0
            c.texto(x + pad, base, _ajustar(c, nome, NEG, 34, w - 2 * pad - iw - 24), NEG, 34, PRETO)
            if txt_info:
                c.texto(x + w - pad, base, txt_info, REG, 26, ESCURO, alinhar="dir")
            itens = [("CPU", _pct(lambda: pm["cpu"]["pct"])), ("RAM", _pct(lambda: pm["ram"]["pct"]))]
            gpu = pm.get("gpu")
            if gpu is not None:
                itens.append(("GPU", _pct(lambda: gpu["util_pct"])))
            else:
                dk = pm.get("discos")
                if isinstance(dk, list) and dk and isinstance(dk[0], dict):
                    itens.append((_ajustar(c, str(dk[0].get("rotulo", "DISCO")), NEG, 26, 90), _pct(lambda: dk[0]["pct"])))
            gap = 30
            cw = (w - 2 * pad - gap * (len(itens) - 1)) // len(itens)
            for k, (rot, pct) in enumerate(itens):
                _mini(c, x + pad + k * (cw + gap), base + 26, cw, rot, pct)

        blocos.append((d["card_h"], desenhar_par, gap, None))
    return blocos


# ------------------------------------------------------------ composicao

def _montar(m, hist, d, w, max_serv=None, max_pares=None):
    blocos = []
    blocos += _bloco_metricas(m, hist, d, w)
    blocos += _bloco_io(m, d, w)
    blocos += _bloco_info(m, d, w)
    blocos += _bloco_ragnarok(m, d, w)
    blocos += _bloco_servicos(m, d, w, max_serv)
    blocos += _bloco_pares(m, d, w, max_pares)
    return blocos


def _cabecalho(c, m):
    c.retangulo(0, 0, c.largura, ALTURA_CABECALHO, PRETO)
    cap = altura_capital(NEG, 72)
    base = (ALTURA_CABECALHO + cap) // 2
    hora = _hora(m, "%H:%M")
    c.texto(c.largura - MARGEM, base, hora, NEG, 72, BRANCO, alinhar="dir")
    maxw = c.largura - 2 * MARGEM - c.medir(hora, NEG, 72) - 40
    c.texto(MARGEM, base, _ajustar(c, m.get("host", "?"), NEG, 72, maxw), NEG, 72, BRANCO)


def _rodape(c, m):
    txt = "atualizado " + _hora(m, "%H:%M:%S")
    c.texto(c.largura // 2, c.altura - 24, txt, REG, 26, MEDIO, alinhar="centro")


def desenhar(c, metricas, historico=None):
    """Desenha a tela inteira no canvas `c` (qualquer tamanho razoavel; o padrao do Kindle e 1236x1648)."""
    m = metricas if isinstance(metricas, dict) else {}
    hist = historico if isinstance(historico, dict) else m.get("historico")
    hist = hist if isinstance(hist, dict) else {}
    largura = c.largura - 2 * MARGEM
    topo = ALTURA_CABECALHO + 36
    limite = c.altura - 64

    n_serv = len([s for s in m.get("servicos") or [] if isinstance(s, dict)]) if isinstance(m.get("servicos"), list) else 0
    n_pares = len(m.get("pares")) if isinstance(m.get("pares"), list) else 0
    tentativas = [(d, None, None) for d in DENSIDADES]
    ultimo = DENSIDADES[-1]
    tentativas += [(ultimo, k, None) for k in range(n_serv - 1, -1, -1)]
    tentativas += [(ultimo, 0, k) for k in range(n_pares - 1, -1, -1)]
    escolhido = None
    for d, ms, mp in tentativas:
        blocos = _montar(m, hist, d, largura, ms, mp)
        total = sum(b[0] for b in blocos) + sum(b[2] for b in blocos[:-1])
        escolhido = (d, blocos, total)
        if topo + total <= limite:
            break
    d, blocos, total = escolhido

    _cabecalho(c, m)
    sobra = max(0, limite - topo - total)
    n_secoes = sum(1 for b in blocos[:-1] if b[2] >= d["esp_secao"])
    extra = min(36, sobra // n_secoes) if n_secoes else 0
    y = topo
    for i, (h, fn, gap, _) in enumerate(blocos):
        fn(c, y, MARGEM)
        y += h
        if i < len(blocos) - 1:
            if gap >= d["esp_secao"]:
                gap += extra
                c.retangulo(MARGEM, y + gap // 2 - 1, largura, 2, CLARO)
            y += gap
    _rodape(c, m)


def render_png(metricas, historico=None, largura=1236, altura=1648):
    """Devolve a tela como PNG 8-bit em tons de cinza."""
    c = Canvas(largura, altura)
    desenhar(c, metricas, historico)
    return c.para_png()
