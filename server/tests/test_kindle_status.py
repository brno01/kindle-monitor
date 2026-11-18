import http.client
import os
import re
import threading
import unittest
from unittest import mock

import _caminho  # noqa: F401
import botoes
import kindle_status as ks
import monitor_server as ms
import render_png
from test_render_png import completo, historico, pixels
from test_servidor import coletor_fake

T0 = 1_794_000_000
Q = "kb=33&kc=0&ktemp=87&kw=5&kwc=1&ka=0&kbt=1&kbc=0&kts=d&klat=48&kf=0&kt=%d&kws=%d" % (T0, T0 - 260)
LOOP_SH = os.path.join(_caminho.RAIZ, "..", "kindle", "kindle-monitor", "loop.sh")


def estado(q=Q, t=T0):
    e = ks.EstadoKindle(relogio=lambda: t)
    e.atualizar(ks.de_query(q), t)
    return e


class DeQueryTest(unittest.TestCase):
    def test_campos_validos(self):
        d = ks.de_query(Q)
        self.assertEqual(d["kb"], 33)
        self.assertEqual(d["kts"], "d")
        self.assertEqual(set(d), set(ks.CHAVES))

    def test_lixo_e_limites_viram_ausentes(self):
        for q in ("kb=101", "kb=-1", "kb=abc", "kb=", "kb=3.5", "kb=1e2", "kb=%C2%B2", "kw=6", "ka=2",
                  "kts=z", "kt=12", "kb=" + "9" * 20, "kb= 3"):
            self.assertEqual(ks.de_query(q), {}, q)

    def test_temperatura_negativa_aceita(self):
        self.assertEqual(ks.de_query("ktemp=-4")["ktemp"], -4)

    def test_sem_parametros_e_query_estranha(self):
        self.assertEqual(ks.de_query(""), {})
        self.assertEqual(ks.de_query(None), {})
        self.assertEqual(ks.de_query("pagina=resumo&modo=economia"), {})
        self.assertEqual(ks.de_query("%%%&&&=="), {})


class VistaTest(unittest.TestCase):
    def test_sem_estado_e_estado_velho(self):
        self.assertIsNone(ks.EstadoKindle(relogio=lambda: T0).vista(T0))
        e = estado()
        self.assertIsNotNone(e.vista(T0 + ks.VELHO_S))
        self.assertIsNone(e.vista(T0 + ks.VELHO_S + 1))

    def test_pedido_sem_campos_nao_apaga(self):
        e = estado()
        self.assertFalse(e.atualizar({}, T0 + 10))
        self.assertEqual(e.vista(T0 + 10)["bateria"], 33)

    def test_textos(self):
        v = estado().vista(T0)
        self.assertEqual(v["temp_c"], 31)  # 87 F
        self.assertEqual(v["tailscale"], "direto")
        self.assertEqual(v["latencia"], "48 ms")
        self.assertEqual(v["relogio"], "ok")
        self.assertEqual(v["whispersync"], "ha 4 min")
        self.assertFalse(v["aviao"])
        self.assertTrue(v["bt"])

    def test_deriva_do_relogio(self):
        self.assertEqual(estado(Q, T0 + 2).vista(T0 + 2)["relogio"], "ok")
        self.assertEqual(estado(Q, T0 - 30).vista(T0 - 30)["relogio"], "+30 s")
        self.assertEqual(estado(Q, T0 + 75).vista(T0 + 75)["relogio"], "-75 s")

    def test_whispersync_em_degraus(self):
        e = estado()
        self.assertEqual(e.vista(T0 - 240)["whispersync"], "agora")
        self.assertEqual(estado(Q.replace("kws=%d" % (T0 - 260), "kws=%d" % (T0 - 3700))).vista(T0)["whispersync"],
                         "ha 1 h")
        self.assertIsNone(estado(Q.replace("&kws=%d" % (T0 - 260), "")).vista(T0)["whispersync"])

    def test_autonomia(self):
        e = ks.EstadoKindle(relogio=lambda: T0)
        e.atualizar(ks.de_query(Q.replace("kb=33", "kb=41")), T0 - 2400)
        e.atualizar(ks.de_query(Q), T0)
        self.assertEqual(e.vista(T0)["autonomia"], "~3 h")  # 8% em 40 min: 12%/h, 33% = 2.75 h
        # janela curta: sem estimativa
        e2 = ks.EstadoKindle(relogio=lambda: T0)
        e2.atualizar(ks.de_query(Q.replace("kb=33", "kb=34")), T0 - 300)
        e2.atualizar(ks.de_query(Q), T0)
        self.assertIsNone(e2.vista(T0)["autonomia"])
        # carregar zera a medida
        e.atualizar(ks.de_query(Q.replace("kc=0", "kc=1")), T0 + 10)
        self.assertIsNone(e.vista(T0 + 10)["autonomia"])
        e.atualizar(ks.de_query(Q), T0 + 20)
        self.assertIsNone(e.vista(T0 + 20)["autonomia"])

    def test_chave_estavel_e_sensivel(self):
        a, b = estado(), estado()
        self.assertEqual(ks.chave(a.vista(T0)), ks.chave(b.vista(T0)))
        # a hora do pedido muda a cada segundo (kt), mas a vista nao
        a.atualizar(ks.de_query(Q.replace("kt=%d" % T0, "kt=%d" % (T0 + 1))), T0 + 1)
        self.assertEqual(ks.chave(a.vista(T0 + 1)), ks.chave(b.vista(T0 + 1)))
        c = estado(Q.replace("kb=33", "kb=32"))
        self.assertNotEqual(ks.chave(c.vista(T0)), ks.chave(b.vista(T0)))
        self.assertEqual(ks.chave(None), ())

    def test_bateria_baixa(self):
        self.assertFalse(ks.bateria_baixa(estado().vista(T0)))
        self.assertTrue(ks.bateria_baixa(estado(Q.replace("kb=33", "kb=15")).vista(T0)))
        self.assertFalse(ks.bateria_baixa(estado(Q.replace("kb=33", "kb=15").replace("kc=0", "kc=1")).vista(T0)))
        self.assertFalse(ks.bateria_baixa(None))


class RenderTest(unittest.TestCase):
    def test_todas_as_paginas_com_e_sem_kindle(self):
        kv = estado().vista(T0)
        for pagina in botoes.PAGINAS:
            com = render_png.render_png(completo(), historico(), pagina=pagina, kindle=kv)
            sem = render_png.render_png(completo(), historico(), pagina=pagina)
            self.assertNotEqual(com, sem, pagina)

    def test_barra_fica_no_alto_e_nao_invade_as_margens(self):
        larg, alt, linhas = pixels(render_png.render_png(completo(), historico(), kindle=estado().vista(T0)))
        self.assertTrue(any(min(linhas[y][larg - 120:larg - 48]) == 0 for y in range(botoes.BARRA_KINDLE_H)))
        for y in range(alt):
            self.assertEqual(min(linhas[y][:40]), 255, y)
            self.assertEqual(min(linhas[y][larg - 40:]), 255, y)

    def test_vista_parcial_nao_quebra(self):
        for q in ("kb=50", "kw=2&kwc=0", "ka=1", "kbt=0", "kf=9", "kts=x"):
            kv = estado(q).vista(T0)
            for pagina in botoes.PAGINAS:
                render_png.render_png(completo(), historico(), pagina=pagina, kindle=kv)

    def test_bateria_baixa_entra_em_atencao(self):
        kv = estado(Q.replace("kb=33", "kb=9")).vista(T0)
        at = render_png._atencao({}, kv)
        self.assertEqual((at[0]["sistema"], at[0]["nivel"]), ("kindle", "aviso"))
        self.assertIn("9%", at[0]["texto"])
        self.assertEqual(render_png._atencao({}, estado().vista(T0)), [])


class ServidorKindleTest(unittest.TestCase):
    def setUp(self):
        self.coletor = coletor_fake()
        self.srv = ms.criar_servidor("127.0.0.1", 0, self.coletor, colunas=38, log=False)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.vistas = []
        original = render_png.render_png

        def contar(*a, **k):
            self.vistas.append(k.get("kindle"))
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

    def _q(self):
        import time
        agora = int(time.time())
        return Q.replace("kt=%d" % T0, "kt=%d" % agora).replace("kws=%d" % (T0 - 260), "kws=%d" % (agora - 60))

    def test_estado_guardado_vale_para_pedidos_sem_k(self):
        self.coletor.atualizar_snapshot()
        self.assertEqual(self.get("/tela.png?pagina=resumo&" + self._q())[0], 200)
        self.assertIsNone(self.vistas[-1])  # aplicado depois de responder
        self.coletor.atualizar_snapshot()
        self.get("/tela.png?pagina=resumo")  # o nomad: sem k*
        self.assertEqual(self.vistas[-1]["bateria"], 33)

    def test_mesmos_dados_acertam_o_cache(self):
        self.coletor.atualizar_snapshot()
        q = self._q()
        self.get("/tela.png?" + q)
        self.get("/tela.png?" + q)  # estado novo ja aplicado: chave nova, renderiza uma vez
        self.get("/tela.png?" + q)
        self.assertEqual(len(self.vistas), 2)

    def test_preaquecer_usa_o_estado_do_kindle(self):
        self.coletor.atualizar_snapshot()
        self.get("/tela.png?" + self._q())
        self.srv.preaquecer(self.coletor.snapshot())
        n = len(self.vistas)
        self.assertEqual(self.vistas[-1]["bateria"], 33)
        self.get("/tela.png?" + self._q())
        self.assertEqual(len(self.vistas), n)  # o pedido seguinte sai do pre-render

    def test_botoes_e_texto_ignoram_k(self):
        self.assertEqual(self.get("/botoes.txt?" + self._q())[0], 200)
        self.assertEqual(self.get("/tela.txt?" + self._q())[0], 200)
        self.assertIsNone(self.srv.kindle.vista())


class ContratoLoopTest(unittest.TestCase):
    def test_loop_envia_exatamente_as_chaves_aceitas(self):
        with open(LOOP_SH, encoding="utf-8") as f:
            texto = f.read()
        enviadas = set(re.findall(r"[&?](k[a-z]+)=", texto))
        self.assertEqual(enviadas, set(ks.CHAVES))


if __name__ == "__main__":
    unittest.main()
