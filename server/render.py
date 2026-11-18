"""Renderizador de texto puro (ASCII) da tela do Kindle. Funcoes puras, sem I/O."""
import unicodedata
from datetime import datetime

import alertas
import botoes
import coletores
import formato
import render_png
import servicos

MAX_LINHAS = 26
ETQ = 5  # largura fixa do rotulo das linhas com barra


def barra(pct, largura):
    """[#####-----] com `largura` celulas internas; pct fora de 0..100 e limitado."""
    largura = max(1, int(largura))
    pct = min(100.0, max(0.0, float(pct)))
    cheios = int(round(pct / 100.0 * largura))
    return "[" + "#" * cheios + "-" * (largura - cheios) + "]"


def ascii_seguro(texto):
    """Remove acentos, descarta o que nao e ASCII imprimivel e troca controles por espaco."""
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    return "".join(ch if 32 <= ord(ch) < 127 else " " for ch in s)


def _ok(bloco):
    return isinstance(bloco, dict) and "erro" not in bloco


ETQ_MAX = 8  # largura maxima do rotulo (ex.: "NAS SSD")
BARRA_MIN = 8  # barra minima para um valor ficar na mesma linha


def _etq_largura(rotulos):
    return min(ETQ_MAX, max([ETQ] + [len(ascii_seguro(r)) for r in rotulos]))


def _linha_barra(etq, pct, cols, ew=ETQ, extra=""):
    largura = max(3, cols - ew - 1 - 2 - 1 - 4 - (len(extra) + 1 if extra else 0))
    linha = "%s %s %4s" % (etq.ljust(ew)[:ew], barra(pct, largura), "%d%%" % int(round(pct)))
    return linha + (" " + extra if extra else "")


def _nd(etq, ew=ETQ):
    return "%s n/d" % etq.ljust(ew)[:ew]


def _barra_de(etq, valor_fn, cols, ew=ETQ, extra=""):
    try:
        return _linha_barra(etq, float(valor_fn()), cols, ew, extra)
    except Exception:
        return _nd(etq, ew)


def _gib(kb):
    return kb / 1024.0 / 1024.0


def _valor_kb(bloco):
    """'7.4/19.4G' (GiB, uma casa) ou None se nao houver os numeros."""
    try:
        if _ok(bloco) and bloco["total_kb"] > 0:
            return "%.1f/%.1fG" % (_gib(bloco.get("usado_kb", 0)), _gib(bloco["total_kb"]))
    except Exception:
        pass
    return None


def _barra_e_valor(etq, bloco, cols, ew):
    """Linha com barra e, se couber, o valor; senao o valor vai numa linha logo abaixo."""
    valor = _valor_kb(bloco)
    if valor and cols - ew - 1 - 2 - 1 - 4 - (len(valor) + 1) >= BARRA_MIN:
        return [_barra_de(etq, lambda: bloco["pct"], cols, ew, valor)]
    linhas = [_barra_de(etq, lambda: bloco["pct"], cols, ew)]
    if valor:
        linhas.append(" " * ew + " " + valor)
    return linhas


def _uptime(seg):
    seg = int(seg)
    d, resto = divmod(seg, 86400)
    h, resto = divmod(resto, 3600)
    mi = resto // 60
    return "%dd %02dh %02dm" % (d, h, mi) if d else "%dh %02dm" % (h, mi)


def _temp_txt(v):
    return "%dC" % int(round(float(v)))


def _linhas_io(io, cols):
    """'IO NVMe r 12.3M w 1.2M' e 'NET LAN rx 3.4M tx 0.2M'; rotulo encurtado para caber em `cols`."""
    if not _ok(io):
        return []
    linhas = []
    for chave, pre, campo, a, b, la, lb in (
            ("discos", "IO", "rotulo", "leitura_bps", "escrita_bps", "r", "w"),
            ("redes", "NET", "rotulo", "rx_bps", "tx_bps", "rx", "tx")):
        itens = io.get(chave)
        for it in itens if isinstance(itens, list) else []:
            try:
                resto = " %s %s %s %s" % (la, formato.taxa_curta(it.get(a)), lb, formato.taxa_curta(it.get(b)))
                rot = ascii_seguro(it.get(campo, "?"))[: max(1, cols - len(pre) - 1 - len(resto))]
                linhas.append("%s %s%s" % (pre, rot, resto))
            except Exception:
                linhas.append("%s n/d" % pre)
    return linhas


def _secao(m, cols, compacto, nome=None):
    linhas = ["== %s ==" % (nome or m.get("host", "?"))]
    cpu, ram, swap, gpu = m.get("cpu"), m.get("ram"), m.get("swap"), m.get("gpu")

    discos = m.get("discos")
    rotulos = []
    if not compacto and isinstance(discos, list):
        rotulos = [str(d.get("rotulo", "?")) for d in discos if isinstance(d, dict)]
    ew = _etq_largura(rotulos)

    linhas.append(_barra_de("CPU", lambda: cpu["pct"], cols, ew))
    if compacto:
        linhas.append(_barra_de("RAM", lambda: ram["pct"], cols, ew))
    else:
        linhas += _barra_e_valor("RAM", ram, cols, ew)
        if _ok(swap) and swap.get("total_kb") == 0:
            linhas.append("SWAP  sem swap")
        else:
            linhas += _barra_e_valor("SWAP", swap, cols, ew)
    if gpu is not None:
        if coletores.gpu_desativada(gpu):
            t = gpu.get("temp_c")
            tt = " " + _temp_txt(t) if isinstance(t, (int, float)) and not isinstance(t, bool) else ""
            linhas.append("%s desativada%s" % ("GPU".ljust(ew), tt))
        else:
            linhas.append(_barra_de("GPU", lambda: gpu["util_pct"], cols, ew))
            if not compacto and _ok(gpu) and gpu.get("mem_usada_mb") is not None and gpu.get("mem_total_mb"):
                linhas.append(_barra_de("VRAM", lambda: gpu["mem_usada_mb"] * 100.0 / gpu["mem_total_mb"], cols, ew))

    if not compacto:
        if isinstance(discos, list):
            for d in discos:
                try:
                    rot = str(d.get("rotulo", "?"))
                    extra = "parado" if d.get("parado") else ""
                    linhas.append(_barra_de(rot, lambda: d["pct"], cols, ew, extra))
                except Exception:
                    linhas.append(_nd("Disco", ew))
        elif discos is not None:
            linhas.append(_nd("Disco", ew))
        linhas += _linhas_io(m.get("io"), cols)
        try:
            c = m["carga"]
            linhas.append("Carga %.2f %.2f %.2f" % (c["1m"], c["5m"], c["15m"]))
        except Exception:
            linhas.append("Carga n/d")

    partes = []
    try:
        if _ok(m.get("temp_cpu")):
            partes.append("CPU " + _temp_txt(m["temp_cpu"]["c"]))
        if _ok(gpu) and gpu.get("temp_c") is not None:
            partes.append("GPU " + _temp_txt(gpu["temp_c"]))
    except Exception:
        partes = ["n/d"]
    if partes:
        linhas.append("Temp " + " ".join(partes))

    try:
        linhas.append("Up " + _uptime(m["uptime"]["segundos"]))
    except Exception:
        linhas.append("Up n/d")

    if not compacto:
        rag = m.get("ragnarok")
        if rag is not None:
            try:
                if not _ok(rag):
                    raise ValueError
                txt = "Ragnarok: %d jog" % rag["jogadores"]
                if rag.get("parado"):
                    idade = rag.get("idade_s")
                    txt += " (PARADO %dm)" % (idade // 60) if isinstance(idade, int) else " (PARADO)"
                linhas.append(txt)
            except Exception:
                linhas.append("Ragnarok: n/d")

        portas = m.get("portas")
        if isinstance(portas, list):
            try:
                itens = ["%s %s" % (p["rotulo"], "ok" if p["aberto"] else "FALHA") for p in portas]
                atual = "Portas:"
                for item in itens:  # quebra em varias linhas se nao couber em `cols`
                    if len(atual) + 1 + len(item) > cols and atual.strip() != "Portas:":
                        linhas.append(atual)
                        atual = "       "
                    atual += " " + item
                linhas.append(atual)
            except Exception:
                linhas.append("Portas: n/d")
        elif portas is not None:
            linhas.append("Portas: n/d")

        svcs = m.get("servicos")
        if isinstance(svcs, list):
            def estado(s):
                if "erro" in s:
                    return "n/d"
                return "ok" if s.get("ativo") else "FALHA"
            try:
                itens = sorted(((str(s.get("nome", "?")), estado(s)) for s in svcs),
                               key=lambda t: t[1] == "ok")  # falhas primeiro (estavel)
                larg = max(1, cols - 6)
                for nome, est in itens:
                    linhas.append("%s %5s" % (nome[:larg].ljust(larg), est))
            except Exception:
                linhas.append("Servicos n/d")
        elif svcs is not None:
            linhas.append("Servicos n/d")
        linhas += _linhas_catalogo(m, cols)
        linhas += _linhas_atencao(m, cols)
    return linhas


def _linhas_catalogo(m, cols):
    """Resumo do catalogo de servicos: contagem e o que pede atencao (falha, ou parado nao opcional)."""
    sk = m.get("servicos_kindle")
    if not isinstance(sk, dict) or not isinstance(sk.get("itens"), list):
        return []
    itens = [i for i in sk["itens"] if isinstance(i, dict)]
    linhas = ["Servicos: " + servicos.texto_resumo(itens, " | ")]
    aviso = {"velho": "estados desatualizados", "ausente": "sem inventario"}.get(sk.get("inventario"))
    if aviso:
        linhas.append("! " + aviso)
    return linhas


ATENCAO_MAX = 6
PREFIXO_NIVEL = {"critico": "[X]", "aviso": "[!]", "leve": "[ ]"}


def _linhas_atencao(m, cols):
    """Alertas do motor (os mesmos do cartao ATENCAO da imagem): ate 6 e '+N' com o resto; vazio sem alertas."""
    lista = alertas.avaliar(m, None, None)
    if not lista:
        return []
    linhas = ["ATENCAO (%d)" % len(lista)]
    for a in lista[:ATENCAO_MAX]:
        linhas.append("%s %s" % (PREFIXO_NIVEL.get(a.get("nivel"), "[?]"), a.get("texto", "?")))
    if len(lista) > ATENCAO_MAX:
        linhas.append("+%d" % (len(lista) - ATENCAO_MAX))
    return linhas


FORMA_TXT = {"ativo": "[#]", "parado": "[ ]", "falha": "[X]"}
LINHAS_POR_PAGINA = MAX_LINHAS - 5


def _linhas_servicos(m, cols, p):
    """Pagina servicos em texto: grupos com uma linha por servico; `p` fora da faixa vira 1 / a ultima."""
    itens = servicos.ordenar(servicos.itens_de(m))
    if not itens:
        return ["Servicos: nenhum configurado"]
    entradas = []
    grupo = None
    for i in itens:
        if i.get("grupo") != grupo:
            grupo = i.get("grupo")
            a = sum(1 for x in itens if x.get("grupo") == grupo and x.get("estado") == "ativo")
            n = sum(1 for x in itens if x.get("grupo") == grupo)
            entradas.append(("%s %d/%d" % (servicos.TITULOS_GRUPO.get(grupo, str(grupo).upper()), a, n), False))
        entradas.append((i, True))
    paginas, atual = [], []
    for e in entradas:
        if len(atual) >= LINHAS_POR_PAGINA or (atual and not e[1] and len(atual) >= LINHAS_POR_PAGINA - 1):
            paginas.append(atual)
            atual = []
        atual.append(e)
    paginas.append(atual)
    p = servicos.pagina_valida(p, len(paginas))
    linhas = ["SERVICOS pagina %d/%d" % (p, len(paginas))]
    for e, eh_item in paginas[p - 1]:
        if not eh_item:
            linhas.append(e)
            continue
        est = e.get("estado")
        det = " " + str(e.get("detalhe")) if est == "falha" and e.get("detalhe") else ""
        linhas.append("%s %s%s" % (FORMA_TXT.get(est, "[?]"), e.get("rotulo", "?"), det))
    return linhas


def _cabecalho(m, cols):
    host = str(m.get("host", "?"))
    try:
        hora = datetime.fromisoformat(m["gerado_em"]).strftime("%H:%M")
    except Exception:
        hora = "--:--"
    host, hora = ascii_seguro(host), ascii_seguro(hora)
    if cols >= len(hora) + 2:
        return host[: cols - len(hora) - 1].ljust(cols - len(hora)) + hora
    return (host + " " + hora)[:cols]


def _linhas_comandos(m, cols):
    """Pagina comandos em texto: so lista os rotulos (o toque so existe na imagem) e os comandos recentes."""
    linhas = ["ACOES (toque na imagem)", "ACOES RAPIDAS"]
    linhas += ["  [%s]" % rotulo for _, rotulo in botoes.COMANDOS]
    linhas += ["", "ULTIMOS COMANDOS"]
    lista = m.get("comandos")
    itens = [i for i in lista if isinstance(i, dict)][:botoes.ULTIMOS_MAX] if isinstance(lista, list) else []
    if not itens:
        linhas.append("  nenhum comando ainda")
    for it in itens:
        linhas.append("  %s %s %s" % (it.get("quando", ""), it.get("estado", "?"), servicos.rotulo_acao(str(it.get("acao", "?")))))
    return linhas


def _linhas_claude(m, cols):
    """Pagina claude em texto: limites e tokens do Claude Code e o estado do S10 (so leitura)."""
    tem_c, tem_s = "claude" in m, "s10" in m
    if not (tem_c or tem_s):
        return ["Claude/S10 desligado na config"]
    agora, tz = render_png._agora(m)
    num, ok = render_png._num, render_png._ok
    linhas = []
    if tem_c:
        cl = m["claude"] if isinstance(m["claude"], dict) else {}
        lim, tok = cl.get("limites"), cl.get("tokens")
        linhas.append("CLAUDE")
        if not ok(lim):
            linhas.append("  limites n/d")
        else:
            for chave, nome in (("cinco_horas", "5h"), ("semanal", "Semanal")):
                j = lim.get(chave)
                j = j if isinstance(j, dict) else {}
                pct = num(j.get("pct"))
                if pct is None:
                    linhas.append("  %-7s n/d" % nome)
                    continue
                ren = j.get("renovado") is True
                pct = 0.0 if ren else min(100.0, max(0.0, float(pct)))
                sub = "renovado" if ren else render_png._volta_txt(j.get("volta_em"), agora, tz)
                linhas.append(("  %-7s %3d%% %s" % (nome, round(pct), sub)).rstrip())
            if lim.get("velho") is True:
                linhas.append("  limites %s" % render_png._idade_txt(lim.get("idade_s")))
        if not ok(tok):
            linhas.append("  tokens n/d")
        else:
            for chave, nome in (("hoje", "Hoje"), ("sete_dias", "7 dias")):
                t = tok.get(chave)
                t = t if isinstance(t, dict) else {}
                linhas.append("  %-7s %s tok %s" % (nome, render_png._tokens_txt(t.get("total")),
                                                    render_png._custo_txt(t.get("custo_usd"))))
            if tok.get("velho") is True:
                linhas.append("  tokens %s" % render_png._idade_txt(tok.get("idade_s")))
    if tem_s:
        s = m["s10"] if ok(m["s10"]) else {}
        if linhas:
            linhas.append("")
        if not s:
            linhas += ["S10", "  n/d"]
            return linhas
        velho = s.get("velho") is True
        linhas.append(("S10 sem dados %s" % render_png._idade_txt(s.get("idade_s"))) if velho else "S10")
        bat = s.get("bateria") if isinstance(s.get("bateria"), dict) else None
        if not velho:
            if bat is None:
                linhas.append("  bateria n/d")
            else:
                nivel, temp = num(bat.get("nivel")), num(bat.get("temperatura_c"))
                st = render_png.STATUS_BATERIA.get(bat.get("status")) if isinstance(bat.get("status"), str) else None
                linhas.append("  bateria " + " ".join(
                    [("n/d" if nivel is None else "%d%%" % round(nivel))] + ([st] if st else [])
                    + ["n/d" if temp is None else "%.0fC" % temp]))
        cam = s.get("caminhos") if isinstance(s.get("caminhos"), dict) else {}
        for chave, rotulo in render_png.CAMINHOS_S10:
            v = cam.get(chave)
            forma = "[?]" if velho or not isinstance(v, bool) else "[#]" if v else "[X]"
            linhas.append("  %s %s" % (forma, rotulo))
        for a in render_png._avisos(s):
            linhas.append("  ! %s" % a)
    return [l.rstrip() for l in linhas]


def render_texto(metricas, colunas, pagina="resumo", p=1):
    """Monta a tela: lista de linhas ASCII, cada uma com no maximo `colunas` caracteres.

    `pagina`: "resumo" e "detalhes" mostram a tela completa (o texto ja e um resumo denso); "comandos" so lista os rotulos.
    """
    cols = max(1, int(colunas))
    m = metricas if isinstance(metricas, dict) else {}
    linhas = [_cabecalho(m, cols), "-" * cols]
    if pagina == "servicos":
        linhas += _linhas_servicos(m, cols, p)
        return [ascii_seguro(l)[:cols] for l in linhas][:MAX_LINHAS]
    if pagina == "claude":
        linhas += _linhas_claude(m, cols)
        return [ascii_seguro(l)[:cols] for l in linhas][:MAX_LINHAS]
    if pagina == "comandos":
        linhas += _linhas_comandos(m, cols)
        linhas = [ascii_seguro(l)[:cols] for l in linhas]
        return linhas[:MAX_LINHAS]
    try:
        linhas += _secao(m, cols, compacto=False)
    except Exception:
        linhas.append("n/d")

    pares = m.get("pares")
    for par in pares if isinstance(pares, list) else []:
        try:
            nome = str(par.get("nome", "?"))
            if par.get("ok") and isinstance(par.get("metricas"), dict):
                linhas += _secao(par["metricas"], cols, compacto=True, nome=nome)
            else:
                linhas.append("%s: sem resposta" % nome)
        except Exception:
            linhas.append("par: n/d")

    linhas = [ascii_seguro(l)[:cols] for l in linhas]
    if len(linhas) > MAX_LINHAS:
        linhas = linhas[: MAX_LINHAS - 1] + ["..."[:cols]]
    return linhas
