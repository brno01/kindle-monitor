"""Power profiles ("Ajustes" on the Acoes page): table, layout, render, query param and parity with the Kindle config."""
import http.client
import json
import os
import re
import threading
import unittest
from unittest import mock

import _caminho  # noqa: F401
import botoes
import canvas as cv
import monitor_server as ms
import perfis
import render_png
from test_botoes import _sobrepoe, itens_cheios
from test_paginas_png import completo, px
from test_servidor import coletor_fake

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_SH = os.path.join(RAIZ, "kindle", "kindle-monitor", "config.sh")
TAMANHOS = ((1236, 1648), (800, 1300), (1072, 1448))


class PerfisTest(unittest.TestCase):
    def test_nomes_e_padrao(self):
        self.assertEqual(perfis.NOMES, ("desempenho", "balanceado", "economia"))
        self.assertEqual(perfis.PADRAO, "desempenho")

    def test_valores(self):
        self.assertEqual([(perfis.PERFIS[n]["intervalo_s"], perfis.PERFIS[n]["flash_ciclos"]) for n in perfis.NOMES],
                         [(1, 600), (60, 15), (300, 6)])

    def test_modo_valido(self):
        for n in perfis.NOMES:
            self.assertEqual(perfis.modo_valido(n), n)
        for v in (None, "", "xpto", "Economia", "economia ", 5, ["economia"], "../x"):
            self.assertEqual(perfis.modo_valido(v), "desempenho", v)

    def test_descricao(self):
        self.assertEqual(perfis.descricao("desempenho"), "Atualiza a cada 1 s · flash a cada 10 min")
        self.assertEqual(perfis.descricao("balanceado"), "Atualiza a cada 1 min · flash a cada 15 min")
        self.assertEqual(perfis.descricao("economia"), "Atualiza a cada 5 min · flash a cada 30 min")
        self.assertEqual(perfis.descricao("xpto"), perfis.descricao("desempenho"))

    def test_mesma_tabela_do_kindle(self):
        with open(CONFIG_SH, encoding="utf-8") as f:
            texto = f.read()
        kindle = {m.group(1): tuple(int(x) for x in m.group(2).split())
                  for m in re.finditer(r'^PERFIL_([a-z]+)="(\d+ \d+)"', texto, re.M)}
        servidor = {n: (perfis.PERFIS[n]["intervalo_s"], perfis.PERFIS[n]["flash_ciclos"]) for n in perfis.NOMES}
        self.assertEqual(kindle, servidor)


class LayoutModosTest(unittest.TestCase):
    def ajustes(self, modo=None, larg=1236, alt=1648):
        return [b for b in botoes.layout("comandos", None, larg, alt, 1, itens_cheios(), modo) if b["id"].startswith("modo:")]

    def test_tres_botoes_locais(self):
        bs = self.ajustes()
        self.assertEqual([(b["id"], b["rotulo"], b["tipo"]) for b in bs],
                         [("modo:desempenho", "Desempenho", "local"), ("modo:balanceado", "Balanceado", "local"),
                          ("modo:economia", "Economia", "local")])
        for b in bs:
            self.assertRegex(b["id"], r"^[a-z0-9:-]+$")
            self.assertFalse(b["armado"])

    def test_so_na_pagina_comandos(self):
        for pagina in ("resumo", "servicos", "detalhes"):
            self.assertFalse([b for b in botoes.layout(pagina) if b["id"].startswith("modo:")])

    def test_sem_sobreposicao_e_dentro_do_conteudo(self):
        for larg, alt in TAMANHOS:
            todos = botoes.layout("comandos", None, larg, alt, 1, itens_cheios())
            for i, a in enumerate(todos):
                for b in todos[i + 1:]:
                    self.assertFalse(_sobrepoe(a, b, 16), (larg, a["id"], b["id"]))
            g = botoes.geometria_comandos(larg, alt)
            for b in self.ajustes(None, larg, alt):
                self.assertGreaterEqual(b["y"], g["ajustes_y"])
                self.assertLessEqual(b["y"] + b["h"], g["ajustes_desc_y"])
                self.assertGreaterEqual(b["w"], 150)
            self.assertLessEqual(g["fim_botoes"], botoes.limite(alt))
            # ajustes block starts below the quick-action grid
            self.assertGreaterEqual(g["ajustes_titulo_y"], g["botoes_y"] + 2 * g["h_botao"] + 16)

    def test_demais_botoes_inalterados(self):
        ids = [b["id"] for b in botoes.layout("comandos") if not b["id"].startswith("modo:")]
        self.assertEqual(ids, ["gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar", "atualizar",
                               "pagina:resumo", "pagina:servicos", "pagina:detalhes", "pagina:comandos", "pagina:claude"])


class RenderModosTest(unittest.TestCase):
    def test_estrito_cabe_nos_tres_tamanhos_e_modos(self):
        for larg, alt in TAMANHOS:
            for modo in perfis.NOMES:
                c = cv.Canvas(larg, alt, estrito=True)
                render_png.desenhar(c, completo(), None, "comandos", None, 1, modo)

    def test_ativo_invertido(self):
        for modo in perfis.NOMES:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, completo(), None, "comandos", None, 1, modo)
            for b in botoes.layout("comandos"):
                if b["id"].startswith("modo:"):
                    self.assertEqual(px(c, b["x"] + 14, b["y"] + 14) < 50, b["id"] == "modo:" + modo, (modo, b["id"]))

    def test_modo_muda_a_imagem_e_invalido_e_padrao(self):
        im = {m: render_png.render_png(completo(), None, pagina="comandos", modo=m) for m in perfis.NOMES}
        self.assertEqual(len(set(im.values())), 3)
        self.assertEqual(render_png.render_png(completo(), None, pagina="comandos", modo="xpto"), im["desempenho"])
        self.assertEqual(render_png.render_png(completo(), None, pagina="comandos"), im["desempenho"])

    def test_outras_paginas_ignoram_o_modo(self):
        a = render_png.render_png(completo(), None, pagina="resumo")
        self.assertEqual(a, render_png.render_png(completo(), None, pagina="resumo", modo="economia"))


class ServidorModosTest(unittest.TestCase):
    def setUp(self):
        self.coletor = coletor_fake()
        self.srv = ms.criar_servidor("127.0.0.1", 0, self.coletor, colunas=38, log=False)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.chamadas = []
        original = render_png.render_png

        def contar(*a, **k):
            self.chamadas.append((a[5:], k.get("modo")))
            return original(*a, **k)
        p = mock.patch.object(render_png, "render_png", contar)
        p.start()
        self.addCleanup(p.stop)

    def get(self, caminho):
        con = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        try:
            con.request("GET", caminho)
            r = con.getresponse()
            return r.status, r.read()
        finally:
            con.close()

    def test_modo_separa_o_cache(self):
        self.coletor.atualizar_snapshot()
        imgs = [self.get("/tela.png?pagina=comandos&modo=" + m)[1] for m in perfis.NOMES]
        self.assertEqual(len(set(imgs)), 3)
        self.assertEqual(len(self.chamadas), 3)
        for m in perfis.NOMES:
            self.get("/tela.png?pagina=comandos&modo=" + m)
        self.assertEqual(len(self.chamadas), 3)

    def test_ausente_ou_invalido_e_desempenho(self):
        self.coletor.atualizar_snapshot()
        base = self.get("/tela.png?pagina=comandos&modo=desempenho")[1]
        for q in ("", "&modo=", "&modo=xpto", "&modo=%ff%00", "&modo=" + "a" * 5000, "&modo=economia&modo=x"):
            st, corpo = self.get("/tela.png?pagina=comandos" + q)
            self.assertEqual(st, 200, q)
            if "economia" not in q:
                self.assertEqual(corpo, base, q)
        self.assertEqual(len(self.chamadas), 2)  # desempenho + economia

    def test_outros_endpoints_aceitam_modo(self):
        for caminho in ("/tela.txt", "/botoes.json", "/botoes.txt"):
            for q in ("?pagina=comandos&modo=economia", "?pagina=comandos&modo=xpto", "?modo=%ff"):
                self.assertEqual(self.get(caminho + q)[0], 200, caminho + q)

    def test_botoes_inclui_ajustes_e_igual_ao_txt(self):
        d = json.loads(self.get("/botoes.json?pagina=comandos&modo=economia")[1])
        ids = [b["id"] for b in d["botoes"]]
        self.assertEqual([i for i in ids if i.startswith("modo:")],
                         ["modo:desempenho", "modo:balanceado", "modo:economia"])
        txt = self.get("/botoes.txt?pagina=comandos&modo=economia")[1].decode().split("\n")
        self.assertEqual([l.split()[0] for l in txt if l], ids)

    def test_preaquecer_usa_o_ultimo_modo(self):
        self.coletor.atualizar_snapshot()
        self.get("/tela.png?pagina=comandos&modo=economia")
        novo = self.coletor.atualizar_snapshot()
        n = len(self.chamadas)
        self.srv.preaquecer(novo)
        self.assertEqual(len(self.chamadas), n + 1)
        self.assertEqual(self.chamadas[-1][1], "economia")
        self.get("/tela.png?pagina=comandos&modo=economia")
        self.assertEqual(len(self.chamadas), n + 1)


if __name__ == "__main__":
    unittest.main()
