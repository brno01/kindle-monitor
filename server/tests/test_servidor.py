import contextlib
import http.client
import io
import json
import os
import struct
import tempfile
import threading
import time
import unittest

import _caminho  # noqa: F401
import coletores
import monitor_server as ms


def coletor_fake():
    arquivos = {
        "/proc/stat": "cpu  100 0 50 800 50 0 0 0 0 0\n",
        "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
        "/proc/meminfo": "MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n",
        "/proc/uptime": "100.0 50.0\n",
    }

    def leitor(p):
        if p in arquivos:
            return arquivos[p]
        raise FileNotFoundError(p)

    def sem_exec(a):
        raise FileNotFoundError(a[0])

    cfg = {"host": "teste", "discos": [], "servicos": [], "balanceador": None, "pares": []}
    return coletores.Coletor(
        cfg, leitor_arquivo=leitor, executar=sem_exec, buscar=lambda u: {},
        dormir=lambda s: None, raiz_sys="/nao/existe",
    )


class _Con:
    def close(self):
        pass


class ServidorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ms.criar_servidor("127.0.0.1", 0, coletor_fake(), colunas=38, log=False)
        cls.porta = cls.srv.server_address[1]
        cls.t = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.t.start()

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

    def test_tela_txt(self):
        st, h, corpo = self.req("GET", "/tela.txt")
        self.assertEqual(st, 200)
        self.assertTrue(h["Content-Type"].startswith("text/plain"))
        self.assertIn("utf-8", h["Content-Type"].lower())
        self.assertEqual(h["Cache-Control"], "no-store")
        texto = corpo.decode("ascii")
        linhas = texto.splitlines()
        self.assertLessEqual(len(linhas), 26)
        self.assertTrue(all(len(l) <= 38 for l in linhas))
        self.assertIn("teste", linhas[0])

    def test_tela_png(self):
        st, h, corpo = self.req("GET", "/tela.png")
        self.assertEqual(st, 200)
        self.assertEqual(h["Content-Type"], "image/png")
        self.assertEqual(h["Cache-Control"], "no-store")
        self.assertEqual(corpo[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", corpo[16:24]), (1236, 1648))
        self.assertEqual(int(h["Content-Length"]), len(corpo))

    def test_tela_png_responde_em_menos_de_1_5s(self):
        t0 = time.monotonic()
        st, _, _ = self.req("GET", "/tela.png")
        self.assertEqual(st, 200)
        self.assertLess(time.monotonic() - t0, 1.5)

    def test_tela_png_com_dimensoes_do_servidor(self):
        srv = ms.criar_servidor("127.0.0.1", 0, coletor_fake(), colunas=38, log=False, largura=900, altura=1400)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            con = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
            con.request("GET", "/tela.png")
            corpo = con.getresponse().read()
            con.close()
            self.assertEqual(struct.unpack(">II", corpo[16:24]), (900, 1400))
        finally:
            srv.shutdown()
            srv.server_close()

    def test_historico_json(self):
        st, h, corpo = self.req("GET", "/historico.json")
        self.assertEqual(st, 200)
        self.assertTrue(h["Content-Type"].startswith("application/json"))
        self.assertEqual(h["Cache-Control"], "no-store")
        dados = json.loads(corpo)
        for chave in ("intervalo_s", "t", "cpu", "ram"):
            self.assertIn(chave, dados)

    def test_metricas_json(self):
        st, h, corpo = self.req("GET", "/metricas.json")
        self.assertEqual(st, 200)
        self.assertTrue(h["Content-Type"].startswith("application/json"))
        self.assertEqual(h["Cache-Control"], "no-store")
        dados = json.loads(corpo)
        self.assertEqual(dados["host"], "teste")
        self.assertIn("gerado_em", dados)

    def test_metricas_com_query_pares_0(self):
        st, _, corpo = self.req("GET", "/metricas.json?pares=0")
        self.assertEqual(st, 200)
        self.assertNotIn("pares", json.loads(corpo))

    def test_saude(self):
        st, h, corpo = self.req("GET", "/saude")
        self.assertEqual((st, corpo), (200, b"ok"))
        self.assertEqual(h["Cache-Control"], "no-store")

    def test_404(self):
        for caminho in ("/", "/nada", "/tela.txt/extra", "/../etc/passwd"):
            st, h, _ = self.req("GET", caminho)
            self.assertEqual(st, 404, caminho)
            self.assertEqual(h["Cache-Control"], "no-store")

    def test_metodos_nao_get_405(self):
        for metodo in ("POST", "PUT", "DELETE", "PATCH", "HEAD"):
            st, h, _ = self.req(metodo, "/tela.txt")
            self.assertEqual(st, 405, metodo)
            self.assertEqual(h["Allow"], "GET")

    def test_tela_txt_mostra_portas(self):
        co = coletor_fake()
        co.config["portas"] = [{"rotulo": "LOGIN", "host": "10.0.0.1", "porta": 6900},
                               {"rotulo": "MAP", "host": "10.0.0.1", "porta": 5121}]
        co._conectar = lambda e, timeout: (_ for _ in ()).throw(OSError()) if e[1] == 5121 else _Con()
        srv = ms.criar_servidor("127.0.0.1", 0, co, colunas=38, log=False)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            con = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
            con.request("GET", "/tela.txt")
            texto = con.getresponse().read().decode("ascii")
            con.close()
            self.assertIn("Portas: LOGIN ok MAP FALHA", texto.splitlines())
        finally:
            srv.shutdown()
            srv.server_close()

    def test_erro_interno_nao_vaza(self):
        class Quebrado:
            def coletar(self, com_pares=True):
                raise RuntimeError("segredo")
        srv = ms.criar_servidor("127.0.0.1", 0, Quebrado(), colunas=38, log=False)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            con = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
            con.request("GET", "/tela.txt")
            r = con.getresponse()
            corpo = r.read()
            self.assertEqual(r.status, 500)
            self.assertNotIn(b"segredo", corpo)
            con.close()
        finally:
            srv.shutdown()
            srv.server_close()


class ConfigTest(unittest.TestCase):
    def test_padroes(self):
        cfg = ms.carregar_config(None)
        self.assertEqual(cfg["balanceador"], "/var/lib/cerberus/memory-balancer.json")
        self.assertEqual(cfg["discos"], [])
        self.assertEqual(cfg["pares"], [])
        self.assertEqual(cfg["intervalo_cpu_s"], 0.5)
        self.assertTrue(cfg["host"])

    def test_arquivo_ignora_comentarios(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as f:
                json.dump({"_comentario": "x", "host": "atheron", "servicos": ["a"], "balanceador": None}, f)
            cfg = ms.carregar_config(p)
        self.assertEqual(cfg["host"], "atheron")
        self.assertEqual(cfg["servicos"], ["a"])
        self.assertIsNone(cfg["balanceador"])
        self.assertNotIn("_comentario", cfg)

    def test_tipo_invalido_levanta(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as f:
                json.dump({"discos": "nao-e-lista"}, f)
            with self.assertRaises(ValueError):
                ms.carregar_config(p)

    def test_padroes_novos(self):
        cfg = ms.carregar_config(None)
        self.assertEqual(cfg["portas"], [])
        self.assertEqual(cfg["intervalo_historico_s"], 15)

    def test_portas_invalidas_rejeitadas(self):
        for portas in ("x", [{"rotulo": "A", "host": "10.0.0.1", "porta": 70000}],
                       [{"rotulo": "A", "host": "a b", "porta": 80}], [1]):
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "c.json")
                with open(p, "w") as f:
                    json.dump({"portas": portas}, f)
                with self.assertRaises(ValueError, msg=repr(portas)):
                    ms.carregar_config(p)

    def test_intervalo_historico_invalido(self):
        for v in (0, -1, "15", True, 100000):
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "c.json")
                with open(p, "w") as f:
                    json.dump({"intervalo_historico_s": v}, f)
                with self.assertRaises(ValueError, msg=repr(v)):
                    ms.carregar_config(p)

    def test_exemplo_valido(self):
        exemplo = os.path.join(_caminho.RAIZ, "config.exemplo.json")
        cfg = ms.carregar_config(exemplo)
        self.assertTrue(cfg["discos"])
        self.assertTrue(cfg["servicos"])
        self.assertTrue(cfg["portas"])
        self.assertIn("intervalo_historico_s", cfg)


class CliTest(unittest.TestCase):
    def test_padroes_nunca_0_0_0_0(self):
        args = ms.parse_args([])
        self.assertEqual(args.bind, "127.0.0.1")
        self.assertEqual(args.porta, 8765)
        self.assertEqual(args.colunas, 38)
        self.assertIsNone(args.config)
        self.assertEqual((args.largura, args.altura), (1236, 1648))

    def test_opcoes(self):
        args = ms.parse_args(["--bind", "100.1.2.3", "--porta", "9000", "--colunas", "40", "--config", "a.json"])
        self.assertEqual((args.bind, args.porta, args.colunas, args.config), ("100.1.2.3", 9000, 40, "a.json"))

    def test_largura_altura(self):
        args = ms.parse_args(["--largura", "1072", "--altura", "1448"])
        self.assertEqual((args.largura, args.altura), (1072, 1448))
        for ruim in (["--largura", "10"], ["--altura", "99999"], ["--largura", "x"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                ms.parse_args(ruim)

    def test_recusa_0_0_0_0(self):
        for end in ("0.0.0.0", "::", ""):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                ms.parse_args(["--bind", end])

    def test_colunas_invalidas(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            ms.parse_args(["--colunas", "5"])


class ConfigTierStateTest(unittest.TestCase):
    def _carregar(self, discos):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as f:
                json.dump({"discos": discos}, f)
            return ms.carregar_config(p)

    def test_tier_state_aceito(self):
        cfg = self._carregar([{"rotulo": "NAS SSD", "tier_state": "/var/lib/cerberus-nas/tier-state.json"},
                              {"rotulo": "/", "caminho": "/"}])
        self.assertEqual(len(cfg["discos"]), 2)

    def test_rejeitados(self):
        for discos in ([{"rotulo": "x"}], [{"rotulo": "x", "tier_state": 3}], [{"tier_state": ""}],
                       [{"rotulo": "x", "caminho": "/", "tier_state": "/t"}], [{"rotulo": "x", "caminho": 4}]):
            with self.assertRaises(ValueError, msg=repr(discos)):
                self._carregar(discos)

    def test_config_atheron_valida(self):
        caminho = os.path.join(_caminho.RAIZ, "..", "deploy", "config.atheron.example.json")
        if not os.path.exists(caminho):  # deploy copy on the server has no repo layout
            self.skipTest("deploy/config.atheron.example.json fora do layout do repositório")
        cfg = ms.carregar_config(caminho)
        rotulos = [d["rotulo"] for d in cfg["discos"]]
        self.assertEqual(rotulos, ["/", "NAS HD", "NAS SSD", "SSD"])
        self.assertTrue(any("tier_state" in d for d in cfg["discos"]))


if __name__ == "__main__":
    unittest.main()
