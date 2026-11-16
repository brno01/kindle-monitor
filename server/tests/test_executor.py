import http.server
import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import signal
import threading
import time
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
        """autoupdate: False = inactive; True = activating (rodando); ou (rc, saida) / excecao para falhas."""
        self.chamadas = []
        self.respostas = respostas or {}
        self.autoupdate = autoupdate

    def __call__(self, argv, timeout):
        self.chamadas.append(list(argv))
        if argv == ex.AUTOUPDATE:
            self.timeout_autoupdate = timeout
            a = self.autoupdate
            if isinstance(a, BaseException):
                raise a
            if isinstance(a, tuple):
                return a[0], a[1], ""
            return 0, ("activating\n" if a else "inactive\n"), ""
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
        os.makedirs(self.estado)
        os.chmod(self.spool, 0o1730)
        self.dono = (os.getuid(), os.getgid())  # no host real: (0, gid de nogroup)
        self.logs = []
        self.cfg = {"spool": self.spool, "estado": self.estado, "acoes": list(ex.TABELA_ARGV) + ["bots-pausar", "gpu-descarregar"]}

    def req(self, nome, conteudo=b""):
        with open(os.path.join(self.spool, nome), "wb") as f:
            f.write(conteudo)

    def executor(self, fake=None, **kw):
        self.fake = fake or Fake()
        kw.setdefault("agora_ns", lambda: 5)
        return ex.Executor(self.cfg, executar=self.fake, dono=self.dono, log=self.logs.append, **kw)

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
        self.assertEqual(t["bots-retomar"], [INC + ["systemctl", "start", "ro-bot-scheduler.timer"]])
        self.assertNotIn("ragnarok-reiniciar", t)
        self.assertNotIn("ollama-reiniciar", t)

    def test_ids(self):
        self.assertEqual(set(ex.ACOES), {"gpu-descarregar", "bots-pausar", "bots-retomar",
                                         "monitor-reiniciar"})

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
        self.assertEqual(os.listdir(self.spool), ["3-bots-retomar.req.x"])  # fora do glob *.req: ignorado
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
        e = ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5, dono=self.dono, log=self.logs.append)
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

    def test_resultado_ok_e_modo(self):  # noqa
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

    def test_autoupdate_recusa_protegidos(self):
        self.cfg["catalogo"] = ex.validar_catalogo([
            {"id": "ollama-gpu", "rotulo": "Ollama", "grupo": "host", "tipo": "systemd",
             "alvo": "ollama-gpu.service", "verbos": ["reiniciar"], "protegido": True}])
        self.req("10-svc--ollama-gpu--reiniciar.req")
        e = self.executor(Fake(autoupdate=True))
        e.processar_spool()
        r = self.resultados()["10-svc--ollama-gpu--reiniciar.json"]
        self.assertEqual(r["estado"], "falhou")
        self.assertIn("atualizacao automatica em andamento", r["detalhe"])
        self.assertEqual(r["acao"], "svc:ollama-gpu:reiniciar")
        self.assertEqual(self.fake.chamadas, [ex.AUTOUPDATE])

    def test_autoupdate_nao_bloqueia_leves(self):
        self.req("10-bots-retomar.req")
        self.executor(Fake(autoupdate=True)).processar_spool()
        self.assertEqual(self.resultados()["10-bots-retomar.json"]["estado"], "ok")

    def test_autoupdate_inativo_executa(self):
        self.cfg["catalogo"] = ex.validar_catalogo([
            {"id": "ollama-gpu", "rotulo": "Ollama", "grupo": "host", "tipo": "systemd",
             "alvo": "ollama-gpu.service", "verbos": ["reiniciar"], "protegido": True}])
        self.req("10-svc--ollama-gpu--reiniciar.req")
        self.executor(Fake(autoupdate=False)).processar_spool()
        self.assertIn(["systemctl", "restart", "ollama-gpu.service"], self.fake.chamadas)

    def test_executando_antes_do_resultado(self):
        self.req("10-monitor-reiniciar.req")
        vistos = []
        fake = Fake()

        def executar(argv, timeout):
            vistos.append(self.resultados().get("10-monitor-reiniciar.json", {}).get("estado"))
            return fake(argv, timeout)
        ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5, dono=self.dono,
                    log=self.logs.append).processar_spool()
        self.assertEqual(vistos, ["executando"])

    def test_limpeza_20_mais_novos(self):
        for i in range(1, 31):
            with open(os.path.join(self.estado, "%d-bots-retomar.json" % i), "w") as f:
                f.write("{}")
        open(os.path.join(self.estado, "outro.txt"), "w").close()
        self.req("100-bots-retomar.req")
        self.executor().processar_spool()
        nomes = sorted(n for n in os.listdir(self.estado) if n.endswith(".json") and not n.startswith("."))
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


NS = 1_000_000_000


class SegurancaDirTest(Base):
    """Os diretorios sao abertos sem seguir symlink e o dono e conferido (injetado para rodar sem root)."""

    def _alvo(self):
        alvo = os.path.join(self._tmp.name, "fora")
        os.makedirs(alvo)
        os.chmod(alvo, 0o1730)
        open(os.path.join(alvo, "1-monitor-reiniciar.req"), "w").close()
        return alvo

    def test_spool_trocado_por_symlink_recusado(self):
        alvo = self._alvo()
        os.rmdir(self.spool)
        os.symlink(alvo, self.spool)
        e = self.executor()
        with self.assertRaises(ex.Recusa):
            e.processar_spool()
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(os.listdir(alvo), ["1-monitor-reiniciar.req"])  # nada seguido para fora

    def test_status_trocado_por_symlink_recusado(self):
        alvo = self._alvo()
        os.rmdir(self.estado)
        os.symlink(alvo, self.estado)
        self.req("10-monitor-reiniciar.req")
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(os.listdir(alvo), ["1-monitor-reiniciar.req"])
        self.assertEqual(os.listdir(self.spool), ["10-monitor-reiniciar.req"])  # nao consumiu

    def test_pai_trocado_por_symlink_recusado(self):
        pai = self._tmp.name
        novo_pai = pai + "-real"
        os.rename(pai, novo_pai)
        self.addCleanup(lambda: os.path.exists(novo_pai) and os.rename(novo_pai, pai))
        os.symlink(novo_pai, pai)
        self.addCleanup(lambda: os.path.islink(pai) and os.unlink(pai))
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()

    def test_dono_errado_recusado(self):
        self.req("10-monitor-reiniciar.req")
        for dono in ((self.dono[0] + 1, self.dono[1]),):
            self.dono = dono
            with self.assertRaises(ex.Recusa):
                self.executor().processar_spool()
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(os.listdir(self.spool), ["10-monitor-reiniciar.req"])

    def test_grupo_do_spool_errado_recusado(self):
        self.dono = (self.dono[0], self.dono[1] + 12345)
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()

    def test_spool_sem_sticky_recusado(self):
        os.chmod(self.spool, 0o730)
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()

    def test_spool_gravavel_por_outros_recusado(self):
        os.chmod(self.spool, 0o1732)
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()

    def test_pai_e_status_gravaveis_por_outros_recusados(self):
        os.chmod(self.estado, 0o777)
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()
        os.chmod(self.estado, 0o755)
        os.chmod(self._tmp.name, 0o775)
        with self.assertRaises(ex.Recusa):
            self.executor().processar_spool()

    def test_diretorios_ausentes_saem_limpo_com_log(self):
        os.rmdir(self.spool)
        self.assertEqual(self.executor().processar_spool(), 0)
        self.assertFalse(os.path.exists(self.spool))  # nao cria nada
        self.assertEqual(len(self.logs), 1)
        os.makedirs(self.spool)
        os.chmod(self.spool, 0o1730)
        os.rmdir(self.estado)
        self.assertEqual(self.executor().processar_spool(), 0)
        self.assertFalse(os.path.exists(self.estado))

    def test_req_symlink_para_fora_nao_e_seguido(self):
        alvo = os.path.join(self._tmp.name, "segredo")
        with open(alvo, "w") as f:
            f.write("x")
        os.symlink(alvo, os.path.join(self.spool, "5-monitor-reiniciar.req"))
        self.executor().processar_spool()
        self.assertEqual(self.fake.chamadas, [])
        self.assertTrue(os.path.exists(alvo))

    def test_status_tmp_preso_por_symlink_nao_segue(self):
        alvo = os.path.join(self._tmp.name, "vitima")
        with open(alvo, "w") as f:
            f.write("intacto")
        os.symlink(alvo, os.path.join(self.estado, ".10-monitor-reiniciar.json.tmp"))
        self.req("10-monitor-reiniciar.req")
        self.executor().processar_spool()
        with open(alvo) as f:
            self.assertEqual(f.read(), "intacto")
        self.assertEqual(self.resultados()["10-monitor-reiniciar.json"]["estado"], "ok")

    def test_usa_dir_fd_nunca_caminho(self):
        """Depois de abertos, o executor nao deve tocar em caminhos: troca de diretorio nao o afeta."""
        self.req("10-monitor-reiniciar.req")
        trocado = []
        fake = Fake()

        def executar(argv, timeout):
            # no meio da execucao, o 'status' e trocado por outro diretorio: o resultado final
            # continua indo para o diretorio original (dir_fd)
            if not trocado:
                os.rename(self.estado, self.estado + "-orig")
                os.makedirs(self.estado)
                trocado.append(1)
            return fake(argv, timeout)
        ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5, dono=self.dono,
                    log=self.logs.append).processar_spool()
        self.assertEqual(os.listdir(self.estado), [])
        self.assertIn("10-monitor-reiniciar.json", os.listdir(self.estado + "-orig"))


class LacoETempTest(Base):
    def test_temporarios_velhos_apagados_e_novos_ficam(self):
        agora = time.time()
        self.req(".velho.tmp")
        self.req(".novo.tmp")
        os.utime(os.path.join(self.spool, ".velho.tmp"), (agora - 120, agora - 120))
        os.makedirs(os.path.join(self.spool, "subdir"))
        self.assertEqual(self.executor(agora_ns=time.time_ns).processar_spool(), 0)
        self.assertEqual(sorted(os.listdir(self.spool)), [".novo.tmp", "subdir"])

    def test_subdiretorio_com_nome_de_req_nao_quebra(self):
        os.makedirs(os.path.join(self.spool, "1-monitor-reiniciar.req"))
        self.req("2-bots-retomar.req")
        self.assertEqual(self.executor().processar_spool(), 1)
        self.assertEqual(os.listdir(self.spool), [])  # o diretorio e renomeado para .lixo-* e removido (vazio)

    def test_nada_a_fazer_zero(self):
        self.assertEqual(self.executor().processar_spool(), 0)

    def test_maximo_10_por_passada(self):
        acoes = ["bots-retomar", "monitor-reiniciar", "bots-retomar", "monitor-reiniciar"]
        for i in range(25):
            self.req("%d-%s.req" % (i + 1, acoes[i % 4]))
        self.assertEqual(self.executor().processar_spool(), 10)
        self.assertEqual(len([n for n in os.listdir(self.spool) if n.endswith(".req")]), 15)


class ExpiraDuplicaCooldownTest(Base):
    def test_expirado(self):
        agora = 1_000_000 * NS
        self.req("%d-monitor-reiniciar.req" % (agora - 61 * NS))
        self.req("%d-bots-retomar.req" % (agora - 30 * NS))
        self.executor(agora_ns=lambda: agora).processar_spool()
        r = self.resultados()
        velho = r["%d-monitor-reiniciar.json" % (agora - 61 * NS)]
        self.assertEqual((velho["estado"], velho["detalhe"]), ("falhou", "pedido expirado"))
        self.assertEqual(r["%d-bots-retomar.json" % (agora - 30 * NS)]["estado"], "ok")
        self.assertEqual(len(self.fake.chamadas), 1)
        self.assertIn("pedido expirado", "\n".join(self.logs))

    def test_duplicado_na_passada(self):
        self.req("10-monitor-reiniciar.req")
        self.req("11-monitor-reiniciar.req")
        self.req("12-bots-retomar.req")
        self.executor().processar_spool()
        self.assertEqual(len(self.fake.chamadas), 2)
        r = self.resultados()
        self.assertEqual(r["10-monitor-reiniciar.json"]["estado"], "ok")
        self.assertEqual((r["11-monitor-reiniciar.json"]["estado"], r["11-monitor-reiniciar.json"]["detalhe"]),
                         ("falhou", "duplicado"))

    def test_cooldown_30s_por_acao(self):
        t = [100 * NS]
        self.req("%d-monitor-reiniciar.req" % t[0])
        e = self.executor(agora_ns=lambda: t[0])
        e.processar_spool()
        self.assertEqual(len(self.fake.chamadas), 1)
        arq = os.path.join(self.estado, ".cooldown.json")
        self.assertEqual(stat.S_IMODE(os.stat(arq).st_mode), 0o644)
        t[0] += 10 * NS
        self.req("%d-monitor-reiniciar.req" % t[0])
        self.req("%d-bots-retomar.req" % t[0])
        e.processar_spool()
        r = self.resultados()
        self.assertEqual(r["%d-monitor-reiniciar.json" % t[0]]["detalhe"], "cooldown de 30 s")
        self.assertEqual(r["%d-bots-retomar.json" % t[0]]["estado"], "ok")
        t[0] += 25 * NS  # 35 s depois do primeiro
        self.req("%d-monitor-reiniciar.req" % t[0])
        e.processar_spool()
        self.assertEqual(self.resultados()["%d-monitor-reiniciar.json" % t[0]]["estado"], "ok")

    def test_cooldown_persiste_entre_execucoes_e_ignora_arquivo_ruim(self):
        t = 100 * NS
        self.req("%d-monitor-reiniciar.req" % t)
        self.executor(agora_ns=lambda: t).processar_spool()
        self.req("%d-monitor-reiniciar.req" % (t + NS))
        self.executor(agora_ns=lambda: t + NS).processar_spool()  # outra instancia = outra passada
        self.assertEqual(self.resultados()["%d-monitor-reiniciar.json" % (t + NS)]["estado"], "falhou")
        with open(os.path.join(self.estado, ".cooldown.json"), "w") as f:
            f.write("{quebrado")
        self.req("%d-monitor-reiniciar.req" % (t + 2 * NS))
        self.executor(agora_ns=lambda: t + 2 * NS).processar_spool()
        # v5 (fail-safe): arquivo ilegivel = nenhuma acao nessa passada; o arquivo e reescrito vazio
        r = self.resultados()["%d-monitor-reiniciar.json" % (t + 2 * NS)]
        self.assertEqual((r["estado"], r["detalhe"]), ("falhou", "cooldown indisponivel"))
        self.req("%d-monitor-reiniciar.req" % (t + 3 * NS))
        self.executor(agora_ns=lambda: t + 3 * NS).processar_spool()
        self.assertEqual(self.resultados()["%d-monitor-reiniciar.json" % (t + 3 * NS)]["estado"], "ok")

    def test_cooldown_symlink_nao_e_seguido(self):
        alvo = os.path.join(self._tmp.name, "alvo.json")
        with open(alvo, "w") as f:
            f.write("{}")
        os.symlink(alvo, os.path.join(self.estado, ".cooldown.json"))
        self.req("10-monitor-reiniciar.req")
        self.executor().processar_spool()
        with open(alvo) as f:
            self.assertEqual(f.read(), "{}")

    def test_sigterm_grava_interrompido(self):
        self.req("10-monitor-reiniciar.req")

        def executar(argv, timeout):
            ex._sigterm(signal.SIGTERM, None)
        e = ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5, dono=self.dono, log=self.logs.append)
        with self.assertRaises(ex.Interrompido):
            e.processar_spool()
        r = self.resultados()["10-monitor-reiniciar.json"]
        self.assertEqual((r["estado"], r["detalhe"]), ("falhou", "interrompido"))


class LogTest(Base):
    def test_uma_linha_por_pedido(self):
        self.req("10-monitor-reiniciar.req")
        self.req("11-bots-retomar.req")
        fake = Fake({("systemctl", "restart", "kindle-monitor.service"): (3, "", "")})
        self.executor(fake).processar_spool()
        pedidos = [l for l in self.logs if l.startswith("acao=")]
        self.assertEqual(pedidos, [
            "acao=monitor-reiniciar id=10 rc=3 estado=falhou detalhe=codigo de saida 3",
            "acao=bots-retomar id=11 rc=0 estado=ok detalhe=concluido"])

    def test_log_sem_caracteres_de_controle(self):
        l = ex.linha_log("x", 1, 0, "ok", "a\nb\x1b[0m")
        self.assertNotIn("\n", l)
        self.assertNotIn("\x1b", l)


class ConfigTest(unittest.TestCase):
    def test_bot_nao_comeca_com_hifen(self):
        self.assertIsNone(ex.RE_BOT.match("-rf"))
        self.assertIsNone(ex.RE_BOT.match("_a"))
        self.assertIsNotNone(ex.RE_BOT.match("a-b_c"))
        self.assertEqual(ex.bots_ativos("BOT ESTADO\n-rf active\nok active\n"), ["ok"])

    def test_invalida_levanta_valueerror(self):
        for ruim in ({"acoes": "x"}, {"acoes": ["rm"]}, {"acoes": [1]}, {"spool": 3},
                     {"spool": "relativo/spool"}, {"estado": ""}, {"estado": "/a/b/status", "spool": "/c/spool"}):
            with self.assertRaises(ValueError, msg=str(ruim)):
                ex.validar_cfg(ruim)
        with self.assertRaises(ValueError):
            ex.validar_cfg([])

    def test_padroes(self):
        c = ex.validar_cfg({})
        self.assertEqual(c["spool"], ex.SPOOL_PADRAO)
        self.assertEqual(c["acoes"], list(ex.ACOES))

    def _main(self, conteudo, nome="c.json"):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, nome)
            if conteudo is not None:
                with open(cam, "w") as f:
                    f.write(conteudo)
            logs = []
            rc = ex.main(["--config", cam], log=logs.append)
            return rc, logs

    def test_main_config_invalida_exit_0_com_log(self):
        for c in ("{quebrado", "[]", json.dumps({"comandos": {"acoes": "x"}}),
                  json.dumps({"comandos": {"spool": 1}}), json.dumps({"comandos": []}), None):
            rc, logs = self._main(c)
            self.assertEqual(rc, 0, c)
            self.assertEqual(len(logs), 1, c)
            self.assertIn("config", logs[0])

    def test_main_diretorios_ausentes_exit_0(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = {"comandos": {"spool": d + "/r/spool", "estado": d + "/r/status"}}
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(cfg, f)
            logs = []
            self.assertEqual(ex.main(["--config", cam], log=logs.append), 0)
            self.assertFalse(os.path.exists(d + "/r"))

    def test_main_recusa_dono_errado_exit_1(self):
        # sem ser root, o dono real (uid 0) nao confere: recusa tudo e sai com erro
        if os.getuid() == 0:
            self.skipTest("rodando como root")
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(d + "/r/spool")
            os.makedirs(d + "/r/status")
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"comandos": {"spool": d + "/r/spool", "estado": d + "/r/status"}}, f)
            logs = []
            self.assertEqual(ex.main(["--config", cam], log=logs.append), 1)
            self.assertTrue(any("recusado" in l for l in logs))


if __name__ == "__main__":
    unittest.main()
