"""Fonte unica de verdade do layout dos botoes da tela (PNG) e do toque no Kindle.

`layout` e puro: o render desenha exatamente estes retangulos e o Kindle mapeia o toque para eles
(`/botoes.json`, `/botoes.txt`). Coordenadas em pixels do PNG, origem no canto superior esquerdo.

Pagina comandos tambem tem o bloco AJUSTES (botoes locais `modo:<perfil>`, ver perfis.py).
Paginas: resumo, servicos (paginada, parametro `p`), detalhes, comandos (rotulo "Acoes") e claude (limites e tokens
do Claude Code + estado do S10; so leitura, sem botoes proprios).
Os botoes da pagina servicos dependem do estado dos itens (ativo: Reiniciar e Parar; parado: Ligar...);
a divisao em paginas so depende do catalogo.
"""
import perfis
import servicos

PAGINAS = ("resumo", "servicos", "detalhes", "comandos", "claude")
PAGINA_PADRAO = "resumo"

# (id, rotulo); sem acento (a fonte embutida e ASCII mais o grau e o ponto medio).
COMANDOS = (
    ("gpu-descarregar", "Descarregar modelo GPU"),
    ("bots-pausar", "Pausar bots"),
    ("bots-retomar", "Retomar bots"),
    ("monitor-reiniciar", "Reiniciar monitor"),
)
IDS_COMANDOS = tuple(c[0] for c in COMANDOS)
ROTULO_ARMADO = "Toque de novo para confirmar"
ROTULO_ARMADO_CURTO = "Confirmar?"
ROTULOS_VERBO = {"reiniciar": "Reiniciar", "ligar": "Ligar", "parar": "Parar"}

NAV = (
    ("atualizar", "Atualizar"),
    ("pagina:resumo", "Resumo"),
    ("pagina:servicos", "Servicos"),
    ("pagina:detalhes", "Detalhes"),
    ("pagina:comandos", "Acoes"),
    ("pagina:claude", "Claude"),
)

MARGEM = 48
GAP = 16
NAV_H = 96
NAV_BASE = 24          # distancia da barra de navegacao ate a borda de baixo
CAB_PX = 70            # cabecalho fino
TOPO = 84              # onde o conteudo comeca (abaixo do cabecalho)
BOTAO_H = 84           # altura dos botoes de linha e de paginacao
PAG_W = 220            # largura dos botoes de paginacao
ULTIMOS_MAX = 8
ULTIMOS_TITULO_H = 44


def pagina_valida(valor):
    return valor if valor in PAGINAS else PAGINA_PADRAO


def armado_valido(valor, itens=()):
    """Id de acao rapida, ou 'svc:<id>:<verbo>' com o id nos `itens` e o verbo no catalogo dele."""
    if valor in IDS_COMANDOS:
        return valor
    s = servicos.acao_svc(valor)
    if s:
        for i in itens:
            if i.get("id") == s[0] and s[1] in (i.get("verbos") or []):
                return valor
    return None


def nav_topo(altura=1648):
    return altura - NAV_BASE - NAV_H


def limite(altura=1648):
    """Y maximo (exclusivo) do conteudo: acima da barra de navegacao, com folga."""
    return nav_topo(altura) - GAP


# ------------------------------------------------------------------ servicos

def medidas_linha(largura):
    """(largura do botao, largura da coluna de estado) conforme a largura da tela."""
    return (190, 190) if largura >= 1100 else (170, 110)


def geometria_servicos(itens, largura=1236, altura=1648, p=1):
    """Posicao de tudo na pagina servicos.

    {"p", "paginas", "barra": {"y","h"} | None, "entradas": [{"tipo": "cab", "grupo", "y", "h"} |
     {"tipo": "svc", "item", "y", "h", "botoes": [verbo]}]}.  `itens` ja ordenados (servicos.ordenar).
    """
    util = limite(altura) - TOPO
    paginas = servicos.paginar(itens, util)
    barra = len(paginas) > 1
    if barra:
        util -= BOTAO_H + GAP
        paginas = servicos.paginar(itens, util)
    n = len(paginas)
    p = servicos.pagina_valida(p, n)
    y = TOPO + (BOTAO_H + GAP if barra else 0)
    entradas = []
    for tipo, v in paginas[p - 1]:
        if tipo == "cab":
            entradas.append({"tipo": "cab", "grupo": v, "y": y, "h": servicos.CAB_H})
            y += servicos.CAB_H
        else:
            it = itens[v]
            h = servicos.altura_linha(it)
            entradas.append({"tipo": "svc", "item": it, "y": y, "h": h, "botoes": servicos.verbos_visiveis(it)})
            y += h
    return {"p": p, "paginas": n, "barra": {"y": TOPO, "h": BOTAO_H} if barra else None, "entradas": entradas,
            "fim": y}


def _botoes_servicos(itens, armado, largura, altura, p):
    geo = geometria_servicos(itens, largura, altura, p)
    saida = []
    bw, _ = medidas_linha(largura)
    if geo["barra"]:
        x = largura - MARGEM - PAG_W
        if geo["p"] < geo["paginas"]:
            saida.append({"id": "servicos:proxima", "rotulo": "Proxima >", "x": x, "y": TOPO, "w": PAG_W, "h": BOTAO_H,
                          "tipo": "local", "armado": False})
            x -= PAG_W + GAP
        if geo["p"] > 1:
            saida.append({"id": "servicos:anterior", "rotulo": "< Anterior", "x": x, "y": TOPO, "w": PAG_W,
                          "h": BOTAO_H, "tipo": "local", "armado": False})
    for e in geo["entradas"]:
        if e["tipo"] != "svc":
            continue
        n = len(e["botoes"])
        for k, verbo in enumerate(e["botoes"]):
            bid = "svc:%s:%s" % (e["item"]["id"], verbo)
            arm = bid == armado
            saida.append({"id": bid, "rotulo": ROTULO_ARMADO_CURTO if arm else ROTULOS_VERBO[verbo],
                          "x": largura - MARGEM - (n - k) * bw - (n - k - 1) * GAP, "y": e["y"], "w": bw,
                          "h": BOTAO_H, "tipo": "comando", "armado": arm})
    return saida


# ------------------------------------------------------------------- acoes

def geometria_comandos(largura=1236, altura=1648):
    """Grade 2x2 das acoes rapidas; abaixo dela a pagina empilha Atencao, resumo por grupo e ULTIMOS COMANDOS."""
    w = (largura - 2 * MARGEM - GAP) // 2
    bh = 140 if altura >= 1600 else 110
    botoes_y = TOPO + 44
    # bloco AJUSTES logo abaixo da grade: titulo, uma linha de 3 botoes e a descricao do perfil ativo
    aj_titulo = botoes_y + 2 * bh + GAP + 8
    aj_y = aj_titulo + 44
    aj_desc = aj_y + BOTAO_H + 8
    return {"w_botao": w, "h_botao": bh, "rapidas_titulo_y": TOPO, "botoes_y": botoes_y,
            "linha_h": 64 if altura >= 1600 else 56, "ajustes_titulo_y": aj_titulo, "ajustes_y": aj_y,
            "ajustes_desc_y": aj_desc, "ajustes_desc_h": 44, "fim_botoes": aj_desc + 44}


def layout(pagina, armado=None, largura=1236, altura=1648, p=1, itens=None, modo=None):
    """Botoes visiveis da pagina: [{id, rotulo, x, y, w, h, tipo, armado}]. Valores invalidos = padrao."""
    pagina = pagina_valida(pagina)
    itens = itens or []
    armado = armado_valido(armado, itens)
    saida = []
    if pagina == "comandos":
        geo = geometria_comandos(largura, altura)
        w = geo["w_botao"]
        for i, (cid, rotulo) in enumerate(COMANDOS):
            saida.append({
                "id": cid, "rotulo": ROTULO_ARMADO if cid == armado else rotulo,
                "x": MARGEM + (i % 2) * (w + GAP), "y": geo["botoes_y"] + (i // 2) * (geo["h_botao"] + GAP),
                "w": w, "h": geo["h_botao"], "tipo": "comando", "armado": cid == armado})
        nw = (largura - 2 * MARGEM - 2 * GAP) // 3
        for i, nome in enumerate(perfis.NOMES):  # o perfil ativo e destacado pelo render (id == "modo:" + modo)
            saida.append({"id": "modo:" + nome, "rotulo": perfis.PERFIS[nome]["rotulo"],
                          "x": MARGEM + i * (nw + GAP), "y": geo["ajustes_y"], "w": nw, "h": BOTAO_H,
                          "tipo": "local", "armado": False})
    elif pagina == "servicos":
        saida += _botoes_servicos(itens, armado, largura, altura, p)
    nw = (largura - 2 * MARGEM - (len(NAV) - 1) * GAP) // len(NAV)
    for i, (bid, rotulo) in enumerate(NAV):
        saida.append({"id": bid, "rotulo": rotulo, "x": MARGEM + i * (nw + GAP), "y": nav_topo(altura),
                      "w": nw, "h": NAV_H, "tipo": "local", "armado": False})
    return saida
