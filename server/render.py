"""Renderizador de texto puro (ASCII) da tela do Kindle. Funcoes puras, sem I/O."""
import unicodedata
from datetime import datetime

import botoes
import coletores
import formato

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

        servicos = m.get("servicos")
        if isinstance(servicos, list):
            def estado(s):
                if "erro" in s:
                    return "n/d"
                return "ok" if s.get("ativo") else "FALHA"
            try:
                itens = sorted(((str(s.get("nome", "?")), estado(s)) for s in servicos),
                               key=lambda t: t[1] == "ok")  # falhas primeiro (estavel)
                larg = max(1, cols - 6)
                for nome, est in itens:
                    linhas.append("%s %5s" % (nome[:larg].ljust(larg), est))
            except Exception:
                linhas.append("Servicos n/d")
        elif servicos is not None:
            linhas.append("Servicos n/d")
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
    linhas = ["COMANDOS (toque na imagem)", ""]
    for grupo in ("leves", "servicos"):
        linhas.append(botoes.TITULOS[grupo])
        linhas += ["  [%s]" % rotulo for _, rotulo, g in botoes.COMANDOS if g == grupo]
    linhas += ["", "ULTIMOS COMANDOS"]
    lista = m.get("comandos")
    itens = [i for i in lista if isinstance(i, dict)][:5] if isinstance(lista, list) else []
    if not itens:
        linhas.append("  nenhum comando ainda")
    for it in itens:
        linhas.append("  %s %s %s" % (it.get("quando", ""), it.get("estado", "?"), it.get("acao", "?")))
    return linhas


def render_texto(metricas, colunas, pagina="resumo"):
    """Monta a tela: lista de linhas ASCII, cada uma com no maximo `colunas` caracteres.

    `pagina`: "resumo" e "detalhes" mostram a tela completa (o texto ja e um resumo denso); "comandos" so lista os rotulos.
    """
    cols = max(1, int(colunas))
    m = metricas if isinstance(metricas, dict) else {}
    linhas = [_cabecalho(m, cols), "-" * cols]
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
