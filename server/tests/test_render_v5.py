"""Render v5: nada cortado, sobreposto ou fora da imagem, em todas as paginas, inclusive o caso cheio."""
import json
import time
import unittest

import _caminho  # noqa: F401
import alertas
import botoes
import canvas as cv
import coletores
import render_png
import servicos
from test_paginas_png import COMANDOS, caso_cheio, historico
from test_render_png import completo, pixels
from test_servidor_servicos import catalogo

AGORA = 1_700_000_000.0
TAMANHOS = ((1236, 1648), (800, 1300), (1072, 1448))


def servicos_kindle(n=52, falhas=6, gerado=AGORA - 2, rotulo_longo=False):
    cat = catalogo(n)
    est = {}
    for i, c in enumerate(cat):
        e = "falha" if i % max(1, n // falhas) == 1 else ("parado" if i % 5 == 2 else "ativo")
        est[c["id"]] = {"estado": e, "detalhe": "restarting" if e == "falha" else "x"}
    if rotulo_longo:
        for c in cat:
            c["rotulo"] = "R" * 28
    return coletores.montar_servicos_kindle(cat, json.dumps({"gerado": gerado, "servicos": est}), AGORA)


def caso52(**extra):
    m = caso_cheio() | {"servicos_kindle": servicos_kindle(), "comandos": (COMANDOS * 2)[:8]}
    m.pop("servicos", None)
    m.update(extra)
    return m


class Gravador(cv.Canvas):
    """Canvas estrito que registra a caixa de cada texto: (x0, x1, y0, y1, texto)."""

    def __init__(self, *a, **k):
        super().__init__(*a, estrito=True, **k)
        self.textos = []

    def texto(self, x, y_base, texto, fonte, tam, cor, alinhar="esq"):
        w = self.medir(texto, fonte, tam)
        x0 = x - w if alinhar == "dir" else x - w / 2.0 if alinhar == "centro" else x
        cap = cv.altura_capital(fonte, tam)
        self.textos.append((x0, x0 + w, y_base - cap, y_base, texto, tam))
        return super().texto(x, y_base, texto, fonte, tam, cor, alinhar)


_CACHE = {}


def desenha(m, pagina, armado=None, p=1, w=1236, h=1648, chave=None):
    """`chave` (nome do caso) liga o cache: os testes de um mesmo caso/pagina reaproveitam o desenho."""
    k = (chave, pagina, armado, p, w, h)
    if chave is not None and k in _CACHE:
        return _CACHE[k]
    c = Gravador(w, h)
    render_png.desenhar(c, m, historico(), pagina, armado, p)
    if chave is not None:
        _CACHE[k] = c
    return c


def paginas_de(m, w=1236, h=1648):
    itens = servicos.ordenar(servicos.itens_de(m))
    return botoes.geometria_servicos(itens, w, h, 1)["paginas"]


def inter(a, b, folga=0):
    return not (a[1] <= b[0] + folga or b[1] <= a[0] + folga or a[3] <= b[2] + folga or b[3] <= a[2] + folga)


class NadaForaNemSobrepostoTest(unittest.TestCase):
    CASOS = {
        "cheio52": caso52,
        "real": lambda: caso52() | {"servicos_kindle": servicos_kindle(48, 1)},
        "sem-falha": lambda: caso52() | {"servicos_kindle": servicos_kindle(52, 1) | {}},
        "rotulos-longos": lambda: caso52() | {"servicos_kindle": servicos_kindle(rotulo_longo=True)},
        "velho": lambda: caso52() | {"servicos_kindle": servicos_kindle(gerado=AGORA - 500)},
        "legado": lambda: completo(),
        "minimo": lambda: {},
        "host-gigante": lambda: caso52(host="h" * 200),
    }

    def todas(self):
        for nome, f in self.CASOS.items():
            for w, h in TAMANHOS:
                m = f()
                for pagina in botoes.PAGINAS:
                    ps = range(1, paginas_de(m, w, h) + 1) if pagina == "servicos" else (1,)
                    for p in ps:
                        yield nome, pagina, p, w, h, m

    def test_estrito_em_todas_as_paginas_e_tamanhos(self):
        for nome, pagina, p, w, h, m in self.todas():
            # levanta ForaDosLimites se algo sair da imagem
            desenha(m, pagina, "gpu-descarregar" if pagina == "comandos" else None, p, w, h)  # sem cache: armado

    def test_texto_dentro_das_margens_laterais(self):
        for nome, pagina, p, w, h, m in self.todas():
            c = desenha(m, pagina, None, p, w, h, nome)
            for x0, x1, y0, y1, t, tam in c.textos:
                self.assertGreaterEqual(x0, botoes.MARGEM - 3, (nome, pagina, p, w, t))
                self.assertLessEqual(x1, w - botoes.MARGEM + 3, (nome, pagina, p, w, t))
                self.assertLessEqual(y1, botoes.nav_topo(h) + botoes.NAV_H, (nome, pagina, t))

    def test_texto_sem_sobreposicao_entre_si(self):
        for nome, pagina, p, w, h, m in self.todas():
            tx = desenha(m, pagina, None, p, w, h, nome).textos
            for i, a in enumerate(tx):
                for b in tx[i + 1:]:
                    self.assertFalse(inter(a, b, 1), (nome, pagina, p, w, h, a[4], b[4]))

    def test_texto_so_toca_botao_se_for_o_rotulo_dele(self):
        for nome, pagina, p, w, h, m in self.todas():
            c = desenha(m, pagina, None, p, w, h, nome)
            bs = botoes.layout(pagina, None, w, h, p, servicos.ordenar(servicos.itens_de(m)))
            for x0, x1, y0, y1, t, tam in c.textos:
                for b in bs:
                    if not b["visivel"]:  # so toque, nada desenhado
                        continue
                    caixa_b = (b["x"], b["x"] + b["w"], b["y"], b["y"] + b["h"])
                    dentro = x0 >= caixa_b[0] and x1 <= caixa_b[1] and y0 >= caixa_b[2] and y1 <= caixa_b[3]
                    self.assertTrue(dentro or not inter((x0, x1, y0, y1), caixa_b), (nome, pagina, p, w, t, b["id"]))

    def test_rotulo_do_botao_cabe_dentro_dele(self):
        for nome, pagina, p, w, h, m in self.todas():
            itens = servicos.ordenar(servicos.itens_de(m))
            c = desenha(m, pagina, None, p, w, h, nome)
            for b in botoes.layout(pagina, None, w, h, p, itens):
                if b["h"] >= 110:
                    continue
                rot = b["rotulo"]
                achou = [t for t in c.textos if t[0] >= b["x"] and t[1] <= b["x"] + b["w"] and t[2] >= b["y"]
                         and t[3] <= b["y"] + b["h"]]
                self.assertTrue(achou, (nome, pagina, w, b["id"], rot))

    def test_confirmar_cabe_no_botao_de_linha(self):
        bw, _ = botoes.medidas_linha(1236)
        self.assertLessEqual(cv.Canvas.medir("Confirmar?", "sans-bold", 26), bw - 12)
        bw, _ = botoes.medidas_linha(800)
        self.assertLessEqual(cv.Canvas.medir("Confirmar?", "sans-bold", 26), bw - 6)


class ConteudoTest(unittest.TestCase):
    def textos(self, m, pagina, p=1, armado=None):
        return [t[4] for t in desenha(m, pagina, armado, p).textos]

    def test_servicos_todos_os_itens_com_rotulo_inteiro(self):
        m = caso52()
        itens = servicos.ordenar(servicos.itens_de(m))
        n = paginas_de(m)
        vistos = []
        for p in range(1, n + 1):
            tx = self.textos(m, "servicos", p)
            geo = botoes.geometria_servicos(itens, 1236, 1648, p)
            for e in geo["entradas"]:
                if e["tipo"] == "svc":
                    self.assertIn(e["item"]["rotulo"], tx, (p, e["item"]["rotulo"]))
                    vistos.append(e["item"]["id"])
            self.assertIn("Pagina %d/%d" % (p, n), tx)
        self.assertEqual(vistos, [i["id"] for i in itens])

    def test_cabecalhos_de_grupo(self):
        m = caso52()
        todos = [t for p in range(1, paginas_de(m) + 1) for t in self.textos(m, "servicos", p)]
        for g in ("HOST", "CONTEINERES", "DOCKER", "RAGNAROK"):
            self.assertIn(g, todos)

    def test_resumo_tem_resumo_no_cabecalho_e_ragnarok_em_uma_linha(self):
        m = caso52()
        tx = self.textos(m, "resumo")
        itens = servicos.itens_de(m)
        self.assertIn(servicos.texto_resumo(itens), tx)
        rag = [t for t in tx if t.startswith("RAGNAROK") and "jogadores" in t]  # o titulo do grupo tambem comeca assim
        self.assertEqual(len(rag), 1)
        self.assertIn("jogadores", rag[0])
        for rot in ("CPU", "RAM", "GPU"):
            self.assertIn(rot, tx)
        self.assertTrue(any(t.startswith("DISCO") for t in tx))
        self.assertTrue(any(t.startswith("ATENCAO (") for t in tx))

    def test_tudo_em_ordem(self):
        todos_ok = servicos_kindle(12, 1)
        for i in todos_ok["itens"]:
            i["estado"] = "ativo"
        portas = [dict(p, aberto=True) for p in caso_cheio()["portas"]]
        m = caso52(servicos_kindle=todos_ok, portas=portas)
        self.assertIn("Tudo em ordem", self.textos(m, "resumo"))

    def test_atencao_lista_falhas_e_nao_opcionais_parados(self):
        m = caso52()
        lista = alertas.avaliar(m)
        self.assertTrue(lista)
        tx = self.textos(m, "resumo")
        self.assertIn("ATENCAO (%d)" % len(lista), tx)
        self.assertIn(lista[0]["texto"], tx)

    def test_aviso_de_inventario_velho(self):
        m = caso52(servicos_kindle=servicos_kindle(gerado=AGORA - 500))
        for pagina in ("resumo", "servicos"):
            self.assertIn("estados desatualizados", self.textos(m, pagina))
        self.assertNotIn("estados desatualizados", self.textos(caso52(), "resumo"))

    def test_acoes_tem_ate_8_comandos_e_rotulo_de_servico(self):
        m = caso52(comandos=[{"acao": "svc:s3:reiniciar", "estado": "ok", "quando": "10:00:0%d" % i, "detalhe": ""}
                             for i in range(8)])
        tx = self.textos(m, "comandos")
        self.assertEqual(tx.count("Reiniciar s3"), 8)
        self.assertEqual(self.textos(caso52(comandos=[]), "comandos").count("nenhum comando ainda"), 1)

    def test_detalhes_tem_discos_io_temperaturas(self):
        tx = self.textos(caso52(), "detalhes")
        for t in ("DISCOS", "MEMORIA", "SERVICOS POR GRUPO", "HISTORICO"):
            self.assertIn(t, tx)
        self.assertTrue(any(t.startswith("DISCO") or t == "DISCO" for t in tx))
        self.assertTrue(any("°C" in t for t in tx))


class PixelsTest(unittest.TestCase):
    def test_botoes_de_servico_nas_coordenadas_do_layout(self):
        m = caso52()
        itens = servicos.ordenar(servicos.itens_de(m))
        for p in (1, 2):
            c = desenha(m, "servicos", None, p)
            for b in botoes.layout("servicos", None, 1236, 1648, p, itens):
                if not b["visivel"]:
                    continue
                px = lambda x, y: c.pixels[y * c.largura + x]
                self.assertLess(px(b["x"] + b["w"] // 2, b["y"] + 1), 100, b["id"])
                self.assertLess(px(b["x"] + 1, b["y"] + b["h"] // 2), 100, b["id"])
                self.assertLess(px(b["x"] + b["w"] // 2, b["y"] + b["h"] - 2), 100, b["id"])

    def test_botao_de_linha_armado_invertido(self):
        m = caso52()
        itens = servicos.ordenar(servicos.itens_de(m))
        alvo = [b for b in botoes.layout("servicos", None, 1236, 1648, 1, itens) if b["id"].startswith("svc:")][0]["id"]
        c = desenha(m, "servicos", alvo, 1)
        for b in botoes.layout("servicos", alvo, 1236, 1648, 1, itens):
            if b["tipo"] != "comando":
                continue
            miolo = c.pixels[(b["y"] + 12) * c.largura + b["x"] + 12]
            self.assertEqual(miolo < 50, b["armado"], b["id"])

    def test_pagina_atual_da_nav_invertida(self):
        for pagina in botoes.PAGINAS:
            c = desenha(caso52(), pagina)
            for b in botoes.layout(pagina):
                if b["id"].startswith("pagina:") and b.get("visivel", True):
                    miolo = c.pixels[(b["y"] + 12) * c.largura + b["x"] + 12]
                    self.assertEqual(miolo < 50, b["id"] == "pagina:" + pagina, (pagina, b["id"]))

    def test_margens_laterais_vazias(self):
        for pagina in botoes.PAGINAS:
            larg, alt, linhas = pixels(render_png.render_png(caso52(), historico(), pagina=pagina))
            for y in range(alt):
                self.assertEqual(min(linhas[y][:40]), 255, (pagina, y))
                self.assertEqual(min(linhas[y][larg - 40:]), 255, (pagina, y))

    def test_sem_grandes_vazios_no_resumo(self):
        # nenhuma faixa em branco com mais de 130 px entre o cabecalho e a navegacao
        larg, alt, linhas = pixels(render_png.render_png(caso52(), historico(), pagina="resumo"))
        corrida = maior = 0
        for y in range(botoes.CAB_PX, botoes.nav_topo(alt)):
            if min(linhas[y]) == 255:
                corrida += 1
                maior = max(maior, corrida)
            else:
                corrida = 0
        self.assertLessEqual(maior, 130)  # o cartao ATENCAO tem teto de 6 itens + "+N": sobra um vao acima do rodape

    def test_formas_de_estado_distintas(self):
        # ativo (cheia), parado (vazia), falha (X) e desconhecido (?) nunca desenham a mesma forma
        formas = []
        for estado in servicos.ESTADOS:
            c = cv.Canvas(60, 60)
            render_png._forma(c, 10, 10, 32, estado)
            formas.append(bytes(c.pixels))
        self.assertEqual(len(set(formas)), 4)
        # em tons de cinza puros (sem depender de cor): a cheia tem mais tinta que a vazia
        tinta = lambda b: sum(1 for v in b if v < 100)
        self.assertGreater(tinta(formas[0]), tinta(formas[1]))


class DesempenhoTest(unittest.TestCase):
    def test_render_menor_que_2s_melhor_de_3(self):
        m = caso52()
        for pagina in botoes.PAGINAS:
            for p in ((1, 2) if pagina == "servicos" else (1,)):
                melhor = float("inf")
                for _ in range(3):
                    t0 = time.monotonic()
                    render_png.render_png(m, historico(), pagina=pagina, p=p)
                    melhor = min(melhor, time.monotonic() - t0)
                self.assertLess(melhor, 2.0, (pagina, p))


class LegadoTest(unittest.TestCase):
    def test_servicos_antigos_aparecem_na_pagina_servicos(self):
        m = completo()
        tx = [t[4] for t in desenha(m, "servicos").textos]
        self.assertIn("ragnarok", tx)
        self.assertIn("cerberus-balancer", tx)

    def test_sem_servicos_nenhum_configurado(self):
        tx = [t[4] for t in desenha({"host": "h", "gerado_em": "2026-11-16T12:00:00"}, "servicos").textos]
        self.assertIn("nenhum servico configurado", tx)


if __name__ == "__main__":
    unittest.main()
