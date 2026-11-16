"""Fonte unica de verdade do layout dos botoes da tela (PNG) e do toque no Kindle.

`layout` e puro: o render desenha exatamente estes retangulos e o Kindle mapeia o toque para eles
(`/botoes.json`). Coordenadas em pixels do PNG, origem no canto superior esquerdo.
"""

PAGINAS = ("resumo", "detalhes", "comandos")
PAGINA_PADRAO = "resumo"

# (id, rotulo, grupo); sem acento (a fonte embutida e ASCII mais "°" e "·").
COMANDOS = (
    ("gpu-descarregar", "Descarregar modelo GPU", "leves"),
    ("bots-pausar", "Pausar bots", "leves"),
    ("bots-retomar", "Retomar bots", "leves"),
    ("monitor-reiniciar", "Reiniciar monitor", "leves"),
    ("ragnarok-reiniciar", "Reiniciar Ragnarok", "servicos"),
    ("ollama-reiniciar", "Reiniciar Ollama", "servicos"),
)
IDS_COMANDOS = tuple(c[0] for c in COMANDOS)
ROTULO_ARMADO = "Toque de novo para confirmar"
TITULOS = {"leves": "ACOES LEVES", "servicos": "SERVICOS (derruba por alguns segundos)"}

NAV = (
    ("atualizar", "Atualizar"),
    ("pagina:resumo", "Resumo"),
    ("pagina:detalhes", "Detalhes"),
    ("pagina:comandos", "Comandos"),
)

MARGEM = 48
GAP = 16
NAV_H = 130
NAV_BASE = 40          # distancia da barra de navegacao ate a borda de baixo
BOTAO_H = 150          # altura minima dos botoes da grade de comandos (200 em telas altas)
TOPO = 112             # onde o conteudo comeca (abaixo do cabecalho compacto)
ULTIMOS_TITULO_H = 48  # titulo + folga da area ULTIMOS COMANDOS
ULTIMOS_LINHA_H = 56   # altura minima de cada comando recente (64 em telas altas)
TITULO_H = 48          # espaco reservado ao titulo de cada secao da grade


def pagina_valida(valor):
    return valor if valor in PAGINAS else PAGINA_PADRAO


def armado_valido(valor):
    return valor if valor in IDS_COMANDOS else None


def nav_topo(altura=1648):
    return altura - NAV_BASE - NAV_H


def geometria_comandos(largura=1236, altura=1648):
    """Posicao dos titulos das secoes e da area 'ULTIMOS COMANDOS' (mesma conta que o layout dos botoes)."""
    w = (largura - 2 * MARGEM - GAP) // 2
    alto = altura >= 1600
    bh = 200 if alto else BOTAO_H
    y = TOPO
    secoes = {}
    for grupo in ("leves", "servicos"):
        n = sum(1 for c in COMANDOS if c[2] == grupo)
        linhas = -(-n // 2)
        secoes[grupo] = {"titulo_y": y, "botoes_y": y + TITULO_H, "linhas": linhas}
        y += TITULO_H + linhas * bh + (linhas - 1) * GAP + 44
    return {"w_botao": w, "h_botao": bh, "linha_h": 64 if alto else ULTIMOS_LINHA_H, "secoes": secoes,
            "ultimos": {"x": MARGEM, "y": y, "w": largura - 2 * MARGEM, "h": nav_topo(altura) - 28 - y}}


def layout(pagina, armado=None, largura=1236, altura=1648):
    """Botoes visiveis da pagina: [{id, rotulo, x, y, w, h, tipo, armado}]. Valores invalidos = padrao."""
    pagina = pagina_valida(pagina)
    saida = []
    if pagina == "comandos":
        armado = armado_valido(armado)
        geo = geometria_comandos(largura, altura)
        w = geo["w_botao"]
        contagem = {"leves": 0, "servicos": 0}
        for cid, rotulo, grupo in COMANDOS:
            i = contagem[grupo]
            contagem[grupo] += 1
            sec = geo["secoes"][grupo]
            saida.append({
                "id": cid, "rotulo": ROTULO_ARMADO if cid == armado else rotulo,
                "x": MARGEM + (i % 2) * (w + GAP), "y": sec["botoes_y"] + (i // 2) * (geo["h_botao"] + GAP),
                "w": w, "h": geo["h_botao"], "tipo": "comando", "armado": cid == armado})
    nw = (largura - 2 * MARGEM - 3 * GAP) // 4
    for i, (bid, rotulo) in enumerate(NAV):
        saida.append({"id": bid, "rotulo": rotulo, "x": MARGEM + i * (nw + GAP), "y": nav_topo(altura),
                      "w": nw, "h": NAV_H, "tipo": "local", "armado": False})
    return saida
