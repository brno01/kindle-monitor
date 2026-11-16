import http.server
import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import threading
import unittest

import _caminho  # noqa: F401

_CAM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "deploy", "kindle-monitor-executor.py")
_spec = importlib.util.spec_from_file_location("executor", _CAM)
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

INC = ["incus", "exec", "games", "--project", "core", "--"]
LISTA = (
    "BOT          ESTADO     PERSONAGEM   CLASSE       NV MAPA               PERFIL      RSS\n"
    "beto         inactive   Beto         Espadachim   63 prt_fild08 (off)   hunt          -\n"
    "ana          active     Ana          Mago         70 prt_fild08         hunt      120M\n"
    "ze_2-x       active     Ze           Arqueiro     12 geffen             farm       80M\n"
)


class Fake:
    """Executar injetavel: grava o que seria rodado, nunca roda nada."""
    def __init__(self, respostas=None, autoupdate=False):
        self.chamadas = []
        self.respostas = respostas or {}
        self.autoupdate = autoupdate

    def __call__(self, argv, timeout):
        self.chamadas.append(list(argv))
        if argv[:3] == ["systemctl", "is-active", "--quiet"]:
            return (0 if self.autoupdate else 3), "", ""
        r = self.respostas.get(tuple(argv))
        if isinstance(r, BaseException):
            raise r
        return r if r is not None else (0, "", "")


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        d = self._tmp.name
        self.spool = os.path.join(d, "spool")
        self.estado = os.path.join(d, "status")
        os.makedirs(self.spool)
        self.cfg = {"spool": self.spool, "estado": self.estado, "acoes": list(ex.TABELA_ARGV) + ["bots-pausar", "gpu-descarregar"]}

    def req(self, nome, conteudo=b""):
        with open(os.path.join(self.spool, nome), "wb") as f:
            f.write(conteudo)

    def executor(self, fake=None, **kw):
        self.fake = fake or Fake()
        return ex.Executor(self.cfg, executar=self.fake, agora_ns=lambda: 5, **kw)

    def resultados(self):
        out = {}
        for n in sorted(os.listdir(self.estado)):
            with open(os.path.join(self.estado, n)) as f:
                out[n] = json.load(f)
        return out


class TabelaTest(unittest.TestCase):
    def test_argv_fixos(self):
        t = ex.TABELA_ARGV
        self.assertEqual(t["monitor-reiniciar"], [["systemctl", "restart", "kindle-monitor.service"]])
        self.assertEqual(t["ollama-reiniciar"], [["systemctl", "restart", "ollama-gpu.service"]])
        self.assertEqual(t["bots-retomar"], [INC + ["systemctl", "start", "ro-bot-scheduler.timer"]])
        self.assertEqual(t["ragnarok-reiniciar"], [INC + ["systemctl", "restart", "rathena-login", "rathena-char", "rathena-map"]])

    def test_ids(self):
        self.assertEqual(set(ex.ACOES), {"gpu-descarregar", "bots-pausar", "bots-retomar",
                                         "monitor-reiniciar", "ragnarok-reiniciar", "ollama-reiniciar"})

    def test_acoes_do_web_batem_com_o_executor(self):
        import comandos
        self.assertEqual(set(ex.ACOES), set(comandos.ACOES))


class ParseTest(unittest.TestCase):
    def test_ro_bot_list(self):
        self.assertEqual(ex.bots_ativos(LISTA), ["ana", "ze_2-x"])

    def test_vazio_e_lixo(self):
        self.assertEqual(ex.bots_ativos(""), [])
        self.assertEqual(ex.bots_ativos("BOT ESTADO\n; rm -rf /   active  x\nBad Name active\n"), [])

    def test_nome_invalido_ignorado(self):
        self.assertEqual(ex.bots_ativos("BOT ESTADO\n" + "a" * 33 + " active\nok active\n"), ["ok"])


class FilaTest(Base):
    def test_nome_invalido_e_symlink_ignorados(self):
        alvo = os.path.join(self._tmp.name, "alvo")
        open(alvo, "w").close()
        os.symlink(alvo, os.path.join(self.spool, "1-bots-retomar.req"))
        self.req("lixo.req")
        self.req("2-BOTS.req")
        self.req("3-bots-retomar.req.x")
        self.req("4-ab.req")
        e = self.executor()
        self.assertEqual(e.processar_spool(), 0)
        self.assertEqual(self.fake.chamadas, [])
        # o link e descartado (para a .path nao disparar em laco) mas o alvo nao e tocado
        self.assertEqual(os.listdir(self.spool), [])
        self.assertTrue(os.path.exists(alvo))

    def test_temporario_do_web_preservado(self):
        self.req(".10-bots-retomar.tmp")
        self.executor().processar_spool()
        self.assertEqual(os.listdir(self.spool), [".10-bots-retomar.tmp"])

    def test_id_desconhecido_nao_executa(self):
        self.req("10-formatar-disco.req")
        e = self.executor()
        e.processar_spool()
        self.assertEqual(self.fake.chamadas, [])
        self.assertFalse(os.listdir(self.spool))
        r = self.resultados()["10-formatar-disco.json"]
        self.assertEqual(r["estado"], "falhou")

    def test_acao_desligada_na_config(self):
        self.cfg["acoes"] = ["bots-pausar"]
        self.req("10-monitor-reiniciar.req")
        e = self.executor()
        e.processar_spool()
        self.assertEqual(self.fake.chamadas, [])

    def test_pedido_apagado_antes_de_executar(self):
        self.req("10-monitor-reiniciar.req")
        visto = []
        fake = Fake()

        def executar(argv, timeout):
            visto.append(os.listdir(self.spool))
            return fake(argv, timeout)
        e = ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5)
        e.processar_spool()
        self.assertEqual(visto, [[]])

    def test_conteudo_ignorado(self):
        self.req("10-monitor-reiniciar.req", b"; rm -rf / --no-preserve-root\n")
        e = self.executor()
        e.processar_spool()
        self.assertEqual(self.fake.chamadas, [["systemctl", "restart", "kindle-monitor.service"]])

    def test_ordem_numerica(self):
        self.req("9-bots-retomar.req")
        self.req("10-monitor-reiniciar.req")
        e = self.executor()
        self.assertEqual(e.processar_spool(), 2)
        self.assertEqual(self.fake.chamadas[0][-1], "ro-bot-scheduler.timer")

    def test_resultado_ok_e_modo(self):
        self.req("10-monitor-reiniciar.req")
        self.executor().processar_spool()
        caminho = os.path.join(self.estado, "10-monitor-reiniciar.json")
        self.assertEqual(stat.S_IMODE(os.stat(caminho).st_mode), 0o644)
        r = self.resultados()["10-monitor-reiniciar.json"]
        self.assertEqual(r["estado"], "ok")
        self.assertEqual(r["acao"], "monitor-reiniciar")
        self.assertRegex(r["quando"], r"^\d\d:\d\d:\d\d$")
        self.assertLessEqual(len(r["detalhe"]), 80)

    def test_falha_de_comando(self):
        self.req("10-monitor-reiniciar.req")
        fake = Fake({("systemctl", "restart", "kindle-monitor.service"): (1, "", "boom")})
        self.executor(fake).processar_spool()
        r = self.resultados()["10-monitor-reiniciar.json"]
        self.assertEqual(r["estado"], "falhou")
        self.assertIn("1", r["detalhe"])

    def test_timeout(self):
        self.req("10-monitor-reiniciar.req")
        fake = Fake({("systemctl", "restart", "kindle-monitor.service"):
                     subprocess.TimeoutExpired("x", 1)})
        self.executor(fake).processar_spool()
        r = self.resultados()["10-monitor-reiniciar.json"]
        self.assertEqual(r["estado"], "falhou")
        self.assertIn("tempo", r["detalhe"])

    def test_executar_padrao_timeout_real(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            ex.executar_padrao(["sleep", "5"], 0.2)

    def test_executar_padrao_sem_shell(self):
        rc, out, _ = ex.executar_padrao(["echo", "a; echo b"], 5)
        self.assertEqual((rc, out.strip()), (0, "a; echo b"))

    def test_autoupdate_recusa_servicos(self):
        for acao in ("ragnarok-reiniciar", "ollama-reiniciar"):
            self.req("10-%s.req" % acao)
            e = self.executor(Fake(autoupdate=True))
            e.processar_spool()
            r = self.resultados()["10-%s.json" % acao]
            self.assertEqual(r["estado"], "falhou")
            self.assertIn("atualizacao automatica em andamento", r["detalhe"])
            self.assertEqual(self.fake.chamadas,
                             [["systemctl", "is-active", "--quiet", "cerberus-autoupdate.service"]])
            os.unlink(os.path.join(self.estado, "10-%s.json" % acao))

    def test_autoupdate_nao_bloqueia_leves(self):
        self.req("10-bots-retomar.req")
        self.executor(Fake(autoupdate=True)).processar_spool()
        self.assertEqual(self.resultados()["10-bots-retomar.json"]["estado"], "ok")

    def test_autoupdate_inativo_executa(self):
        self.req("10-ollama-reiniciar.req")
        self.executor(Fake(autoupdate=False)).processar_spool()
        self.assertIn(["systemctl", "restart", "ollama-gpu.service"], self.fake.chamadas)

    def test_executando_antes_do_resultado(self):
        self.req("10-monitor-reiniciar.req")
        vistos = []
        fake = Fake()

        def executar(argv, timeout):
            vistos.append(self.resultados().get("10-monitor-reiniciar.json", {}).get("estado"))
            return fake(argv, timeout)
        ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5).processar_spool()
        self.assertEqual(vistos, ["executando"])

    def test_limpeza_20_mais_novos(self):
        os.makedirs(self.estado)
        for i in range(1, 31):
            with open(os.path.join(self.estado, "%d-bots-retomar.json" % i), "w") as f:
                f.write("{}")
        open(os.path.join(self.estado, "outro.txt"), "w").close()
        self.req("100-bots-retomar.req")
        self.executor().processar_spool()
        nomes = sorted(n for n in os.listdir(self.estado) if n.endswith(".json"))
        self.assertEqual(len(nomes), 20)
        self.assertIn("100-bots-retomar.json", nomes)
        self.assertIn("12-bots-retomar.json", nomes)
        self.assertNotIn("11-bots-retomar.json", nomes)
        self.assertIn("outro.txt", os.listdir(self.estado))


class BotsTest(Base):
    def test_pausar(self):
        self.req("10-bots-pausar.req")
        fake = Fake({tuple(INC + ["ro-bot", "list"]): (0, LISTA, "")})
        self.executor(fake).processar_spool()
        self.assertEqual(self.fake.chamadas, [
            INC + ["systemctl", "stop", "ro-bot-scheduler.timer"],
            INC + ["ro-bot", "list"],
            INC + ["ro-bot", "stop", "ana"],
            INC + ["ro-bot", "stop", "ze_2-x"],
        ])
        r = self.resultados()["10-bots-pausar.json"]
        self.assertEqual(r["estado"], "ok")
        self.assertIn("ana", r["detalhe"])

    def test_pausar_falha_do_timer_nao_segue(self):
        self.req("10-bots-pausar.req")
        fake = Fake({tuple(INC + ["systemctl", "stop", "ro-bot-scheduler.timer"]): (5, "", "")})
        self.executor(fake).processar_spool()
        self.assertEqual(len(self.fake.chamadas), 1)
        self.assertEqual(self.resultados()["10-bots-pausar.json"]["estado"], "falhou")

    def test_pausar_falha_ao_parar_um_bot(self):
        self.req("10-bots-pausar.req")
        fake = Fake({tuple(INC + ["ro-bot", "list"]): (0, LISTA, ""),
                     tuple(INC + ["ro-bot", "stop", "ana"]): (1, "", "")})
        self.executor(fake).processar_spool()
        self.assertEqual(self.resultados()["10-bots-pausar.json"]["estado"], "falhou")
        self.assertIn(INC + ["ro-bot", "stop", "ze_2-x"], self.fake.chamadas)

    def test_pausar_sem_bots_ativos(self):
        self.req("10-bots-pausar.req")
        fake = Fake({tuple(INC + ["ro-bot", "list"]): (0, "BOT ESTADO\nbeto inactive\n", "")})
        self.executor(fake).processar_spool()
        self.assertEqual(self.resultados()["10-bots-pausar.json"]["estado"], "ok")


class _Ollama(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.server.log.append(("GET", self.path, None))
        corpo = json.dumps({"models": [{"name": m} for m in self.server.modelos]}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_POST(self):
        n = int(self.headers["Content-Length"])
        self.server.log.append(("POST", self.path, json.loads(self.rfile.read(n))))
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")


class GpuTest(Base):
    def servidor(self, modelos):
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Ollama)
        srv.modelos, srv.log = modelos, []
        threading.Thread(target=srv.serve_forever, daemon=True).start()

        def parar():
            srv.shutdown()
            srv.server_close()
        self.addCleanup(parar)
        return srv, "http://127.0.0.1:%d" % srv.server_address[1]

    def test_descarrega_cada_modelo(self):
        srv, url = self.servidor(["qwen3:8b", "llama3:latest"])
        self.req("10-gpu-descarregar.req")
        self.executor(ollama=url).processar_spool()
        self.assertEqual(srv.log[0][:2], ("GET", "/api/ps"))
        self.assertEqual(srv.log[1:], [
            ("POST", "/api/generate", {"model": "qwen3:8b", "keep_alive": 0}),
            ("POST", "/api/generate", {"model": "llama3:latest", "keep_alive": 0})])
        r = self.resultados()["10-gpu-descarregar.json"]
        self.assertEqual(r["estado"], "ok")
        self.assertEqual(r["detalhe"], "descarregado: qwen3:8b, llama3:latest")

    def test_nenhum_modelo(self):
        srv, url = self.servidor([])
        self.req("10-gpu-descarregar.req")
        self.executor(ollama=url).processar_spool()
        self.assertEqual(len(srv.log), 1)
        self.assertEqual(self.resultados()["10-gpu-descarregar.json"]["detalhe"], "nenhum modelo carregado")

    def test_servidor_fora_do_ar(self):
        self.req("10-gpu-descarregar.req")
        self.executor(ollama="http://127.0.0.1:1").processar_spool()
        self.assertEqual(self.resultados()["10-gpu-descarregar.json"]["estado"], "falhou")

    def test_url_padrao(self):
        self.assertEqual(ex.OLLAMA_PADRAO, "http://10.0.0.1:11435")


if __name__ == "__main__":
    unittest.main()
