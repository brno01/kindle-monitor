import http.client
import json
import os
import stat
import tempfile
import threading
import unittest

import _caminho  # noqa: F401
import comandos
import monitor_server as ms
from test_servidor import coletor_fake

TOKEN = "ab" * 32


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        d = self._tmp.name
        self.token_arq = os.path.join(d, "token")
        with open(self.token_arq, "w") as f:
            f.write(TOKEN + "\n")
        self.spool = os.path.join(d, "run", "spool")
        self.estado = os.path.join(d, "run", "status")
        self.t = [100.0]
        self.ns = [1_700_000_000_000_000_000]
        self.logs = []

    def cfg(self, **extra):
        c = {"token_arquivo": self.token_arq, "spool": self.spool, "estado": self.estado,
             "permitidos_de": ["127.0.0.1"]}
        c.update(extra)
        return comandos.validar_config(c)

    def novo(self, **extra):
        def agora_ns():
            self.ns[0] += 1
            return self.ns[0]
        return comandos.Comandos(self.cfg(**extra), relogio=lambda: self.t[0], agora_ns=agora_ns,
                                 log=self.logs.append)


class ConfigTest(unittest.TestCase):
    def test_padroes(self):
        c = comandos.validar_config({})
        self.assertEqual(c["token_arquivo"], "/etc/kindle-monitor/token")
        self.assertEqual(c["permitidos_de"], ["100.64.0.2", "100.64.0.3"])
        self.assertEqual(c["spool"], "/run/kindle-monitor/spool")
        self.assertEqual(c["estado"], "/run/kindle-monitor/status")
        self.assertEqual(set(c["acoes"]), set(comandos.ACOES))

    def test_ids_do_contrato(self):
        self.assertEqual(set(comandos.ACOES), {
            "gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar",
            "ragnarok-reiniciar", "ollama-reiniciar"})

    def test_invalidos(self):
        for ruim in ({"acoes": ["rm-rf"]}, {"permitidos_de": ["nao-ip"]}, {"spool": ""},
                     {"acoes": "gpu-descarregar"}, {"token_arquivo": 3}):
            with self.assertRaises(ValueError, msg=str(ruim)):
                comandos.validar_config(ruim)
        with self.assertRaises(ValueError):
            comandos.validar_config([])

    def test_comentarios_ignorados(self):
        c = comandos.validar_config({"_x": 1, "acoes": ["bots-pausar"]})
        self.assertEqual(c["acoes"], ["bots-pausar"])


class ProcessarTest(Base):
    def post(self, c, corpo=b'{"acao": "bots-pausar"}', ip="127.0.0.1", token=TOKEN,
             tipo="application/json", tamanho=None):
        import io
        return c.processar(ip, token, tipo, len(corpo) if tamanho is None else tamanho, io.BytesIO(corpo))

    def test_aceito_grava_req_atomico(self):
        c = self.novo()
        st, corpo, extra = self.post(c)
        self.assertEqual(st, 202)
        self.assertEqual(corpo["estado"], "aceito")
        self.assertEqual(corpo["acao"], "bots-pausar")
        nomes = os.listdir(self.spool)
        self.assertEqual(nomes, [corpo["id"] + ".req"])
        self.assertRegex(nomes[0], r"^\d{1,20}-bots-pausar\.req$")
        self.assertEqual(os.path.getsize(os.path.join(self.spool, nomes[0])), 0)
        self.assertEqual(stat.S_IMODE(os.stat(self.spool).st_mode), 0o700)

    def test_gravacao_usa_rename_sem_tmp_residual(self):
        chamadas = []
        real = os.rename

        def rename(a, b):
            chamadas.append((a, b))
            self.assertFalse(a.endswith(".req"))
            self.assertTrue(b.endswith(".req"))
            self.assertTrue(os.path.exists(a))
            real(a, b)
        c = self.novo()
        orig = comandos.os.rename
        comandos.os.rename = rename
        try:
            self.post(c)
        finally:
            comandos.os.rename = orig
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(len(os.listdir(self.spool)), 1)

    def test_token_errado_ausente_401(self):
        c = self.novo()
        for tk in ("00" * 32, None, "", TOKEN[:-1]):
            st, corpo, _ = self.post(c, token=tk)
            self.assertEqual(st, 401)
            self.assertEqual(corpo, {"erro": "nao autorizado"})
        self.assertFalse(os.path.exists(self.spool) and os.listdir(self.spool))

    def test_token_nao_vai_para_o_log(self):
        c = self.novo()
        self.post(c, token="00" * 32)
        self.post(c)
        texto = "\n".join(self.logs)
        self.assertNotIn(TOKEN, texto)
        self.assertNotIn("00" * 32, texto)

    def test_arquivo_de_token_ausente_503(self):
        c = self.novo(token_arquivo=os.path.join(self._tmp.name, "nao-existe"))
        self.assertEqual(self.post(c)[0], 503)

    def test_arquivo_de_token_invalido_503(self):
        with open(self.token_arq, "w") as f:
            f.write("curto\n")
        self.assertEqual(self.post(self.novo())[0], 503)

    def test_ip_fora_da_lista_403(self):
        c = self.novo()
        self.assertEqual(self.post(c, ip="100.1.2.3")[0], 403)

    def test_acao_invalida_400(self):
        c = self.novo()
        for corpo in (b'{"acao": "rm -rf /"}', b'{"acao": 3}', b'{}', b'[]', b'nao json', b'\xff\xfe'):
            self.assertEqual(self.post(c, corpo=corpo)[0], 400, corpo)
        self.assertFalse(os.path.exists(self.spool) and os.listdir(self.spool))

    def test_acao_desligada_400(self):
        c = self.novo(acoes=["bots-retomar"])
        self.assertEqual(self.post(c)[0], 400)
        self.assertEqual(self.post(c, corpo=b'{"acao": "bots-retomar"}')[0], 202)

    def test_corpo_grande_413(self):
        c = self.novo()
        st, _, _ = self.post(c, corpo=b"x" * 2000)
        self.assertEqual(st, 413)

    def test_content_length_invalido(self):
        c = self.novo()
        self.assertEqual(self.post(c, tamanho=-1)[0], 400)
        self.assertEqual(self.post(c, tamanho=None, corpo=b"")[0], 400)

    def test_content_type_errado_415(self):
        c = self.novo()
        self.assertEqual(self.post(c, tipo="text/plain")[0], 415)
        self.assertEqual(self.post(c, tipo=None)[0], 415)
        self.assertEqual(self.post(c, tipo="application/json; charset=utf-8")[0], 202)

    def test_rate_limit(self):
        c = self.novo()
        self.assertEqual(self.post(c)[0], 202)
        self.t[0] += 2
        st, corpo, extra = self.post(c)
        self.assertEqual(st, 429)
        self.assertEqual(extra["Retry-After"], "3")
        self.t[0] += 3.1
        self.assertEqual(self.post(c)[0], 202)

    def test_recusado_nao_consome_o_limite(self):
        c = self.novo()
        self.post(c, token="00" * 32)
        self.post(c, corpo=b'{"acao": "x"}')
        self.assertEqual(self.post(c)[0], 202)

    def test_auditoria(self):
        c = self.novo()
        self.post(c)
        self.post(c, ip="9.9.9.9")
        self.assertEqual(len(self.logs), 2)
        self.assertIn("ip=127.0.0.1", self.logs[0])
        self.assertIn("acao=bots-pausar", self.logs[0])
        self.assertIn("aceito", self.logs[0])
        self.assertIn("recusado", self.logs[1])
        self.assertIn("ip=9.9.9.9", self.logs[1])

    def test_acao_hostil_sanitizada_no_log(self):
        c = self.novo()
        self.post(c, corpo=json.dumps({"acao": "a\nFALSO linha\x1b[31m" + "z" * 100}).encode())
        self.assertEqual(len(self.logs), 1)
        self.assertNotIn("\n", self.logs[0])
        self.assertNotIn("\x1b", self.logs[0])


class UltimosTest(Base):
    def setUp(self):
        super().setUp()
        os.makedirs(self.spool)
        os.makedirs(self.estado)

    def estado_arq(self, nome, dados):
        with open(os.path.join(self.estado, nome), "w") as f:
            f.write(dados if isinstance(dados, str) else json.dumps(dados))

    def test_vazio_e_diretorios_ausentes(self):
        c = comandos.Comandos(comandos.validar_config(
            {"spool": "/nao/existe/a", "estado": "/nao/existe/b"}))
        self.assertEqual(c.ultimos(), [])
        self.assertEqual(self.novo().ultimos(), [])

    def test_ordem_e_pendentes(self):
        self.estado_arq("100-bots-pausar.json", {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": "x"})
        self.estado_arq("300-gpu-descarregar.json", {"acao": "gpu-descarregar", "estado": "falhou", "quando": "10:02:00", "detalhe": "y"})
        open(os.path.join(self.spool, "400-bots-retomar.req"), "w").close()
        r = self.novo().ultimos()
        self.assertEqual([i["acao"] for i in r], ["bots-retomar", "gpu-descarregar", "bots-pausar"])
        self.assertEqual(r[0]["estado"], "executando")
        self.assertEqual(set(r[0]), {"acao", "estado", "quando", "detalhe"})
        self.assertRegex(r[0]["quando"], r"^\d\d:\d\d:\d\d$")

    def test_limite_n(self):
        for i in range(8):
            self.estado_arq("%d-bots-pausar.json" % (i + 1), {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": ""})
        self.assertEqual(len(self.novo().ultimos()), 5)
        self.assertEqual(len(self.novo().ultimos(2)), 2)

    def test_numero_ordena_numericamente(self):
        self.estado_arq("9-bots-pausar.json", {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": "velho"})
        self.estado_arq("10-bots-pausar.json", {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": "novo"})
        self.assertEqual(self.novo().ultimos()[0]["detalhe"], "novo")

    def test_lixo_ignorado(self):
        ok = {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": ""}
        self.estado_arq("100-bots-pausar.json", ok)
        self.estado_arq("200-bots-pausar.json", "{quebrado")
        self.estado_arq("outro.json", ok)
        self.estado_arq("300-bots-pausar.txt", ok)
        self.estado_arq("400-BOTS.json", ok)
        self.estado_arq("500-bots-pausar.json", {"acao": "bots-pausar", "estado": "weird", "quando": "10:00:00", "detalhe": ""})
        self.estado_arq("600-bots-pausar.json", [1, 2])
        self.estado_arq("700-bots-pausar.json", {"acao": "../x", "estado": "ok", "quando": "10:00:00", "detalhe": ""})
        alvo = os.path.join(self._tmp.name, "alvo.json")
        with open(alvo, "w") as f:
            json.dump(ok, f)
        os.symlink(alvo, os.path.join(self.estado, "800-bots-pausar.json"))
        os.symlink(alvo, os.path.join(self.spool, "900-bots-pausar.req"))
        open(os.path.join(self.spool, "lixo.req"), "w").close()
        r = self.novo().ultimos()
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["quando"], "10:00:00")

    def test_detalhe_truncado(self):
        self.estado_arq("100-bots-pausar.json", {"acao": "bots-pausar", "estado": "ok", "quando": "10:00:00", "detalhe": "d" * 500})
        self.assertEqual(len(self.novo().ultimos()[0]["detalhe"]), 80)


class HttpTest(Base):
    def setUp(self):
        super().setUp()
        self.com = self.novo()
        self.srv = ms.criar_servidor("127.0.0.1", 0, coletor_fake(), colunas=38, log=False, comandos=self.com)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

        def parar():
            self.srv.shutdown()
            self.srv.server_close()
        self.addCleanup(parar)

    def req(self, metodo, caminho, corpo=None, cab=None):
        con = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        try:
            con.request(metodo, caminho, body=corpo, headers=cab or {})
            r = con.getresponse()
            return r.status, r.read(), dict(r.getheaders())
        finally:
            con.close()

    def cab(self, **extra):
        h = {"Content-Type": "application/json", "X-Kindle-Token": TOKEN}
        h.update(extra)
        return h

    def test_post_aceito(self):
        st, dados, _ = self.req("POST", "/comando", json.dumps({"acao": "gpu-descarregar"}), self.cab())
        self.assertEqual(st, 202)
        j = json.loads(dados)
        self.assertEqual(j["estado"], "aceito")
        self.assertEqual(os.listdir(self.spool), [j["id"] + ".req"])

    def test_post_sem_token_401(self):
        h = self.cab()
        del h["X-Kindle-Token"]
        self.assertEqual(self.req("POST", "/comando", '{"acao": "bots-pausar"}', h)[0], 401)

    def test_post_rate_limit_429(self):
        self.req("POST", "/comando", '{"acao": "bots-pausar"}', self.cab())
        st, _, h = self.req("POST", "/comando", '{"acao": "bots-pausar"}', self.cab())
        self.assertEqual(st, 429)
        self.assertIn("Retry-After", h)

    def test_post_corpo_grande_413(self):
        st, _, _ = self.req("POST", "/comando", b"x" * 1500, self.cab())
        self.assertEqual(st, 413)

    def test_post_outro_caminho_405(self):
        self.assertEqual(self.req("POST", "/metricas.json", "{}", self.cab())[0], 405)

    def test_estado_e_metricas(self):
        os.makedirs(self.spool, exist_ok=True)
        open(os.path.join(self.spool, "400-bots-retomar.req"), "w").close()
        st, dados, _ = self.req("GET", "/comando/estado")
        self.assertEqual(st, 200)
        self.assertEqual(json.loads(dados)[0]["acao"], "bots-retomar")
        st, dados, _ = self.req("GET", "/metricas.json")
        self.assertEqual(json.loads(dados)["comandos"][0]["estado"], "executando")


if __name__ == "__main__":
    unittest.main()
