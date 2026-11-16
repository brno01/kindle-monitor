import http.client
import json
import struct
import threading
import unittest
from urllib.parse import quote

import _caminho  # noqa: F401
import botoes
import monitor_server as ms
from test_servidor import coletor_fake


class _HoraFixa:
    """Pins gerado_em: the header shows HH:MM:SS, so two renders a second apart differ byte for byte."""

    def __init__(self, coletor):
        self._c = coletor

    def coletar(self, *a, **k):
        m = self._c.coletar(*a, **k)
        m["gerado_em"] = "2026-11-16T12:00:00"
        return m

    def __getattr__(self, nome):
        return getattr(self._c, nome)


class PaginasServidorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ms.criar_servidor("127.0.0.1", 0, _HoraFixa(coletor_fake()), colunas=38, log=False)
        cls.porta = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def req(self, metodo, caminho):
        con = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        try:
            con.request(metodo, caminho)
            r = con.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            con.close()

    def test_botoes_json_padrao(self):
        st, h, corpo = self.req("GET", "/botoes.json")
        self.assertEqual(st, 200)
        self.assertTrue(h["Content-Type"].startswith("application/json"))
        self.assertEqual(h["Cache-Control"], "no-store")
        d = json.loads(corpo)
        self.assertEqual((d["largura"], d["altura"], d["pagina"]), (1236, 1648, "resumo"))
        self.assertEqual(d["botoes"], botoes.layout("resumo", None, 1236, 1648))

    def test_botoes_json_comandos_armado(self):
        st, _, corpo = self.req("GET", "/botoes.json?pagina=comandos&armado=bots-pausar")
        d = json.loads(corpo)
        self.assertEqual(st, 200)
        self.assertEqual(d["pagina"], "comandos")
        self.assertEqual([b["id"] for b in d["botoes"] if b["armado"]], ["bots-pausar"])
        self.assertEqual(len([b for b in d["botoes"] if b["tipo"] == "comando"]), 4)

    def test_botoes_json_parametros_invalidos_viram_padrao(self):
        for q in ("pagina=xpto", "pagina=", "pagina=comandos&armado=nao-existe", "pagina=resumo&armado=bots-pausar",
                  "armado=%00%ff", "pagina=comandos&pagina=zzz", "pagina=" + quote("../../etc") + "&armado=" + "a" * 5000):
            st, _, corpo = self.req("GET", "/botoes.json?" + q)
            self.assertEqual(st, 200, q)
            d = json.loads(corpo)
            self.assertFalse(any(b["armado"] for b in d["botoes"]), q)
            self.assertIn(d["pagina"], botoes.PAGINAS)

    def test_botoes_json_usa_o_tamanho_do_servidor(self):
        srv = ms.criar_servidor("127.0.0.1", 0, self.srv.coletor, log=False, largura=900, altura=1400)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            con = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
            con.request("GET", "/botoes.json?pagina=comandos")
            d = json.loads(con.getresponse().read())
            con.close()
            self.assertEqual((d["largura"], d["altura"]), (900, 1400))
            self.assertEqual(d["botoes"], botoes.layout("comandos", None, 900, 1400))
        finally:
            srv.shutdown()
            srv.server_close()

    def test_tela_png_com_pagina_e_armado(self):
        imgs = {}
        for q in ("", "?pagina=resumo", "?pagina=detalhes", "?pagina=servicos", "?pagina=comandos",
                  "?pagina=comandos&armado=bots-pausar"):
            st, h, corpo = self.req("GET", "/tela.png" + q)
            self.assertEqual(st, 200, q)
            self.assertEqual(h["Content-Type"], "image/png")
            self.assertEqual(struct.unpack(">II", corpo[16:24]), (1236, 1648))
            imgs[q] = corpo
        self.assertEqual(imgs[""], imgs["?pagina=resumo"])
        self.assertEqual(len({imgs["?pagina=resumo"], imgs["?pagina=detalhes"], imgs["?pagina=comandos"],
                              imgs["?pagina=comandos&armado=bots-pausar"]}), 4)
        self.assertNotEqual(imgs["?pagina=servicos"], imgs["?pagina=resumo"])

    def test_tela_png_parametros_invalidos_nunca_500(self):
        padrao = self.req("GET", "/tela.png")[2]
        for q in ("?pagina=xpto", "?armado=xpto", "?pagina=comandos&armado=%ff%00", "?pagina=%e4%b8%ad", "?x=1&&=",
                  "?pagina=resumo&armado=bots-pausar"):
            st, _, corpo = self.req("GET", "/tela.png" + q)
            self.assertEqual(st, 200, q)
            self.assertEqual(corpo[:4], b"\x89PNG")
        self.assertEqual(self.req("GET", "/tela.png?pagina=xpto")[2], padrao)

    def test_tela_txt_com_pagina(self):
        for q in ("", "?pagina=resumo", "?pagina=detalhes", "?pagina=servicos", "?pagina=servicos&p=9", "?pagina=xpto"):
            st, _, corpo = self.req("GET", "/tela.txt" + q)
            self.assertEqual(st, 200)
            self.assertIn("teste", corpo.decode("ascii"))
        st, _, corpo = self.req("GET", "/tela.txt?pagina=comandos")
        texto = corpo.decode("ascii")
        self.assertEqual(st, 200)
        self.assertTrue(all(len(l) <= 38 for l in texto.splitlines()))
        for _, rotulo in botoes.COMANDOS:
            self.assertIn(rotulo[:30], texto)

    def test_so_get(self):
        self.assertEqual(self.req("POST", "/botoes.json")[0], 405)

if __name__ == "__main__":
    unittest.main()
