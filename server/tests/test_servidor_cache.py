import http.client
import threading
import unittest
from unittest import mock

import _caminho  # noqa: F401
import monitor_server as ms
import render_png
from test_servidor import coletor_fake


class CacheServidorTest(unittest.TestCase):
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
            self.chamadas.append(a[5:])  # pagina, armado, p
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

    def test_sem_snapshot_nao_usa_cache(self):
        self.get("/tela.png")
        self.get("/tela.png")
        self.assertEqual(len(self.chamadas), 2)

    def test_mesmo_snapshot_renderiza_uma_vez(self):
        self.coletor.atualizar_snapshot()
        a = self.get("/tela.png?pagina=resumo")
        b = self.get("/tela.png?pagina=resumo")
        self.assertEqual(a, b)
        self.assertEqual(a[0], 200)
        self.assertEqual(len(self.chamadas), 1)
        self.assertEqual(len(self.srv.cache), 1)

    def test_snapshot_novo_invalida(self):
        self.coletor.atualizar_snapshot()
        self.get("/tela.png")
        self.coletor.atualizar_snapshot()
        self.get("/tela.png")
        self.assertEqual(len(self.chamadas), 2)

    def test_pagina_p_e_armado_separam_entradas(self):
        self.coletor.atualizar_snapshot()
        for q in ("pagina=resumo", "pagina=detalhes", "pagina=servicos&p=1", "pagina=servicos&p=2",
                  "pagina=comandos", "pagina=comandos&armado=bots-pausar"):
            self.get("/tela.png?" + q)
        self.assertEqual(len(self.chamadas), 6)
        for q in ("pagina=resumo", "pagina=comandos&armado=bots-pausar"):
            self.get("/tela.png?" + q)
        self.assertEqual(len(self.chamadas), 6)

    def test_comandos_novos_invalidam_a_pagina_comandos(self):
        self.coletor.atualizar_snapshot()
        self.get("/tela.png?pagina=comandos")
        itens = [{"acao": "bots-pausar", "estado": "ok", "quando": "x", "detalhe": ""}]
        with mock.patch.object(self.srv.comandos, "ultimos", lambda *a, **k: itens):
            self.get("/tela.png?pagina=comandos")
        self.assertEqual(len(self.chamadas), 2)

    def test_botoes_e_metricas_nao_renderizam_e_nao_vazam_comandos(self):
        self.coletor.atualizar_snapshot()
        self.assertEqual(self.get("/botoes.txt")[0], 200)
        self.get("/metricas.json")
        self.assertEqual(self.chamadas, [])
        self.assertNotIn("comandos", self.coletor.snapshot().metricas)

    def test_preaquecer_renderiza_a_ultima_vista(self):
        self.coletor.atualizar_snapshot()
        self.get("/tela.png?pagina=detalhes")
        novo = self.coletor.atualizar_snapshot()
        n = len(self.chamadas)
        self.srv.preaquecer(novo)
        self.assertEqual(len(self.chamadas), n + 1)
        self.get("/tela.png?pagina=detalhes")  # hit
        self.assertEqual(len(self.chamadas), n + 1)

    def test_preaquecer_sem_pedido_recente_nao_faz_nada(self):
        novo = self.coletor.atualizar_snapshot()
        self.srv.preaquecer(novo)
        self.assertEqual(self.chamadas, [])
        self.get("/tela.png")
        self.srv._relogio = lambda: 1e9
        self.srv.preaquecer(self.coletor.atualizar_snapshot())
        self.assertEqual(len(self.chamadas), 1)


class ConfigColetaTest(unittest.TestCase):
    def test_padroes(self):
        cfg = ms.carregar_config(None)
        self.assertEqual(cfg["intervalo_coleta_s"], 1.0)
        self.assertEqual(cfg["intervalo_lento_s"], 5.0)

    def test_valores_invalidos(self):
        import json
        import os
        import tempfile
        for chave, v in (("intervalo_coleta_s", 0), ("intervalo_coleta_s", "x"), ("intervalo_coleta_s", 100),
                         ("intervalo_lento_s", True), ("intervalo_lento_s", 0.1)):
            with tempfile.TemporaryDirectory() as d:
                f = os.path.join(d, "c.json")
                with open(f, "w") as fh:
                    json.dump({chave: v}, fh)
                with self.assertRaises(ValueError, msg=(chave, v)):
                    ms.carregar_config(f)


if __name__ == "__main__":
    unittest.main()
