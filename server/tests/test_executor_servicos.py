"""Executor: comandos por servico (svc:<id>:<verbo>), inventario e paridade com o validador do web."""
import json
import os
import subprocess
import unittest

import _caminho  # noqa: F401
import servicos
from test_executor import INC, Base, Fake, ex

NS = 10 ** 9
MICRO = ["incus", "exec", "microservices", "--project", "core", "--"]


def it(**k):
    d = {"id": "a", "rotulo": "A", "grupo": "host", "tipo": "systemd", "alvo": "a.service",
         "verbos": ["reiniciar", "ligar", "parar"]}
    d.update(k)
    return d


CAT = [
    it(id="smbd", alvo="smbd.service"),
    it(id="ai-agent", grupo="incus", tipo="incus", alvo="ai-agent"),
    it(id="onion-gw", grupo="incus", tipo="incus", alvo="onion-gw", projeto="onion", verbos=[]),
    it(id="ro-client-build", grupo="incus", tipo="incus", alvo="ro-client-build", projeto="sandbox", verbos=["parar"]),
    it(id="n8n-app", grupo="docker", tipo="docker", alvo="n8n-app"),
    it(id="dokploy", grupo="docker", tipo="docker", alvo="dokploy.", prefixo=True, verbos=[]),
    it(id="rathena-map", grupo="ragnarok", tipo="rathena", alvo="rathena-map.service", protegido=True),
    it(id="tailscaled", alvo="tailscaled.service", verbos=[]),
]


def catalogo():
    return ex.validar_catalogo(CAT)


class ArgvTest(unittest.TestCase):
    def argv(self, sid, verbo):
        item = {i["id"]: i for i in catalogo()}[sid]
        return ex.Executor.argv_servico(item, verbo)

    def test_systemd(self):
        self.assertEqual(self.argv("smbd", "reiniciar"), (["systemctl", "restart", "smbd.service"], 40))
        self.assertEqual(self.argv("smbd", "ligar")[0], ["systemctl", "start", "smbd.service"])
        self.assertEqual(self.argv("smbd", "parar")[0], ["systemctl", "stop", "smbd.service"])

    def test_incus_com_projeto(self):
        self.assertEqual(self.argv("ai-agent", "reiniciar"),
                         (["incus", "restart", "ai-agent", "--project", "core"], 90))
        self.assertEqual(self.argv("ai-agent", "ligar")[0], ["incus", "start", "ai-agent", "--project", "core"])
        self.assertEqual(self.argv("ro-client-build", "parar")[0],
                         ["incus", "stop", "ro-client-build", "--project", "sandbox"])

    def test_docker_e_rathena(self):
        self.assertEqual(self.argv("n8n-app", "parar")[0], MICRO + ["docker", "stop", "n8n-app"])
        self.assertEqual(self.argv("n8n-app", "reiniciar")[0], MICRO + ["docker", "restart", "n8n-app"])
        self.assertEqual(self.argv("rathena-map", "reiniciar")[0], INC + ["systemctl", "restart", "rathena-map.service"])


class SvcFilaTest(Base):
    def setUp(self):
        super().setUp()
        self.cfg["catalogo"] = catalogo()

    def rodar(self, *nomes, fake=None, **kw):
        for n in nomes:
            self.req(n)
        e = self.executor(fake, **kw)
        e.processar_spool()
        return self.resultados()

    def test_executa_e_grava_acao_com_dois_pontos(self):
        r = self.rodar("10-svc--ai-agent--parar.req")
        self.assertEqual(self.fake.chamadas, [["incus", "stop", "ai-agent", "--project", "core"]])
        self.assertEqual(r["10-svc--ai-agent--parar.json"]["acao"], "svc:ai-agent:parar")
        self.assertEqual(r["10-svc--ai-agent--parar.json"]["estado"], "ok")
        self.assertEqual(os.listdir(self.spool), [])

    def test_fora_do_catalogo_ou_verbo_nao_permitido(self):
        r = self.rodar("10-svc--nao-existe--parar.req", "11-svc--tailscaled--reiniciar.req",
                       "12-svc--ro-client-build--reiniciar.req", "13-svc--dokploy--parar.req")
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(r["10-svc--nao-existe--parar.json"]["detalhe"], "servico fora do catalogo")
        for n in ("11-svc--tailscaled--reiniciar", "12-svc--ro-client-build--reiniciar", "13-svc--dokploy--parar"):
            self.assertEqual(r[n + ".json"]["detalhe"], "verbo nao permitido")

    def test_nomes_malformados_sao_descartados_sem_executar(self):
        self.rodar("10-svc--AI--parar.req", "11-svc--ai-agent--apagar.req", "12-svc----parar.req",
                   "13-svc--ai-agent--parar--x.req", "14-svc--a%20b--parar.req")
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(os.listdir(self.spool), [])
        self.assertEqual(self.resultados(), {})

    def test_cooldown_e_dedupe_por_acao(self):
        agora = 1_000_000 * NS
        a, b = "%d-svc--smbd--reiniciar.req" % (agora - NS), "%d-svc--smbd--reiniciar.req" % (agora - 2 * NS)
        c = "%d-svc--ai-agent--reiniciar.req" % (agora - 3 * NS)
        r = self.rodar(a, b, c, agora_ns=lambda: agora)
        det = {k: v["detalhe"] for k, v in r.items() if "detalhe" in v}
        self.assertEqual(len(self.fake.chamadas), 2)  # smbd (uma vez) e ai-agent
        self.assertIn("duplicado", det.values())
        # nova passada 5 s depois: cooldown de 30 s da mesma acao, outra acao livre
        self.req("%d-svc--smbd--reiniciar.req" % (agora + 4 * NS))
        self.req("%d-svc--smbd--parar.req" % (agora + 4 * NS))
        self.executor(agora_ns=lambda: agora + 5 * NS).processar_spool()
        r = self.resultados()
        self.assertEqual(r["%d-svc--smbd--reiniciar.json" % (agora + 4 * NS)]["detalhe"], "cooldown de 30 s")
        self.assertEqual(r["%d-svc--smbd--parar.json" % (agora + 4 * NS)]["estado"], "ok")

    def test_cooldown_persiste_chave_svc(self):
        agora = 1_000_000 * NS
        self.rodar("%d-svc--smbd--reiniciar.req" % (agora - NS), agora_ns=lambda: agora)
        with open(os.path.join(self.estado, ".cooldown.json")) as f:
            self.assertIn("svc:smbd:reiniciar", json.load(f))
        self.req("%d-svc--smbd--reiniciar.req" % (agora + NS))
        e = self.executor(agora_ns=lambda: agora + 2 * NS)
        e.processar_spool()
        self.assertEqual(self.resultados()["%d-svc--smbd--reiniciar.json" % (agora + NS)]["detalhe"], "cooldown de 30 s")

    def test_protegido_recusa_com_autoupdate_e_nao_protegido_nao(self):
        r = self.rodar("10-svc--rathena-map--reiniciar.req", "11-svc--smbd--reiniciar.req", fake=Fake(autoupdate=True))
        self.assertEqual(r["10-svc--rathena-map--reiniciar.json"]["detalhe"], "atualizacao automatica em andamento")
        self.assertEqual(r["11-svc--smbd--reiniciar.json"]["estado"], "ok")
        self.assertNotIn(INC + ["systemctl", "restart", "rathena-map.service"], self.fake.chamadas)

    def test_protegido_executa_sem_autoupdate(self):
        self.rodar("10-svc--rathena-map--reiniciar.req")
        self.assertIn(INC + ["systemctl", "restart", "rathena-map.service"], self.fake.chamadas)

    def test_falha_do_comando(self):
        fake = Fake({("incus", "stop", "ai-agent", "--project", "core"): (1, "", "boom")})
        r = self.rodar("10-svc--ai-agent--parar.req", fake=fake)
        self.assertEqual(r["10-svc--ai-agent--parar.json"]["estado"], "falhou")
        r = self.rodar("20-svc--ai-agent--ligar.req", fake=Fake({
            ("incus", "start", "ai-agent", "--project", "core"): subprocess.TimeoutExpired("incus", 90)}))
        self.assertEqual(r["20-svc--ai-agent--ligar.json"]["detalhe"], "tempo esgotado")

    def test_sem_catalogo_nada_executa(self):
        self.cfg["catalogo"] = []
        r = self.rodar("10-svc--smbd--reiniciar.req")
        self.assertEqual(r["10-svc--smbd--reiniciar.json"]["detalhe"], "servico fora do catalogo")
        self.assertEqual(self.fake.chamadas, [])


class CatalogoParidadeTest(unittest.TestCase):
    CASOS = [
        [], None, "x", [1], [it(id="A")], [it(id="a--b")], [it(id="-a")], [it(id="a" * 41)], [it(), it()],
        [it(rotulo="")], [it(rotulo="x" * 29)], [it(rotulo="aç")], [it(grupo="x")], [it(tipo="x")],
        [it(alvo="-x.service")], [it(alvo="a b.service")], [it(alvo="a$(x).service")], [it(alvo="a")],
        [it(projeto="core")], [it(tipo="incus", alvo="x", projeto="Ruim!")], [it(prefixo=True)],
        [it(tipo="docker", alvo="x.", prefixo=True, verbos=["reiniciar"])], [it(verbos=["apagar"])],
        [it(verbos="reiniciar")], [it(verbos=["parar", "parar"])], [it(protegido="sim")], [it(opcional=1)],
        [it(extra=1)], [it(id=5)], CAT, [it(tipo="docker", alvo="x", grupo="docker")],
        [it(tipo="rathena", alvo="x.service", grupo="ragnarok", protegido=True, opcional=True)],
    ]

    def decide(self, f, caso):
        try:
            return f(caso)
        except ValueError:
            return "erro"

    def test_mesmas_decisoes_e_mesma_normalizacao(self):
        for caso in self.CASOS:
            self.assertEqual(self.decide(ex.validar_catalogo, caso), self.decide(servicos.validar_catalogo, caso),
                             str(caso)[:80])

    def test_config_real(self):
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(raiz, "deploy", "config.atheron.json")) as f:
            lista = json.load(f)["servicos_kindle"]
        self.assertEqual(ex.validar_catalogo(lista), servicos.validar_catalogo(lista))

    def test_codec_do_nome(self):
        for acao in ("svc:ai-agent:reiniciar", "svc:a:ligar", "gpu-descarregar", "bots-pausar"):
            self.assertEqual(ex.nome_para_acao(servicos.acao_para_nome(acao)), acao)
        for tk in ("svc--A--ligar", "svc--a--apagar", "svc----ligar", "ab", "a/b", "svc--a--ligar--x"):
            self.assertEqual(ex.nome_para_acao(tk), servicos.nome_para_acao(tk), tk)
            self.assertIsNone(ex.nome_para_acao(tk))

    def test_regex_do_spool_aceita_svc(self):
        self.assertTrue(ex.RE_REQ.match("12-svc--ai-agent--parar.req"))
        self.assertTrue(ex.RE_JSON.match("12-svc--ai-agent--parar.json"))
        self.assertIsNone(ex.RE_JSON.match("servicos.json"))


class ConfigRuimTest(Base):
    def test_main_catalogo_invalido_sai_0_com_log(self):
        import tempfile
        logs = []
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"servicos_kindle": [{"id": "x"}]}, f)
            self.assertEqual(ex.main(["--config", cam], log=logs.append), 0)
            self.assertEqual(ex.main(["--config", cam, "--inventario"], log=logs.append), 0)
        self.assertEqual(len(logs), 2)
        self.assertIn("config invalida", logs[0])

    def test_main_config_valida_carrega_catalogo(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"servicos_kindle": CAT, "comandos": {"spool": self.spool, "estado": self.estado}}, f)
            cfg = ex.carregar_cfg(cam)
        self.assertEqual([i["id"] for i in cfg["catalogo"]], [i["id"] for i in CAT])


# ------------------------------------------------------------------ inventario

SYSTEMD = """Id=smbd.service
ActiveState=active
SubState=running

Id=tailscaled.service
ActiveState=failed
SubState=failed
"""
INCUS = "ai-agent,RUNNING,core\nonion-gw,STOPPED,onion\nro-client-build,RUNNING,sandbox\nai-agent,STOPPED,outro\n"
DOCKER = ("n8n-app running\ndokploy.1.abc123 running\ndokploy.2.def456 exited\ndokploy-postgres.1.zzz running\n"
          "wud restarting\n")
RATHENA = "Id=rathena-map.service\nActiveState=inactive\nSubState=dead\n"


def saidas():
    base = {
        ("systemctl", "show", "-p", "Id,ActiveState,SubState", "smbd.service", "tailscaled.service"): (0, SYSTEMD, ""),
        ("incus", "list", "--all-projects", "--format", "csv", "-c", "n,s,e"): (0, INCUS, ""),
        tuple(MICRO + ["docker", "ps", "-a", "--format", "{{.Names}} {{.State}}"]): (0, DOCKER, ""),
        tuple(INC + ["systemctl", "show", "-p", "Id,ActiveState,SubState", "rathena-map.service"]): (0, RATHENA, ""),
    }
    return base


class FakeInv:
    def __init__(self, respostas):
        self.respostas = respostas
        self.chamadas = []

    def __call__(self, argv, timeout):
        self.chamadas.append((list(argv), timeout))
        r = self.respostas.get(tuple(argv), (1, "", "?"))
        if isinstance(r, BaseException):
            raise r
        return r


class ParseInventarioTest(unittest.TestCase):
    def test_systemctl_show(self):
        self.assertEqual(ex.parse_systemctl_show(SYSTEMD),
                         {"smbd.service": ("active", "running"), "tailscaled.service": ("failed", "failed")})
        self.assertEqual(ex.parse_systemctl_show(""), {})
        self.assertEqual(ex.parse_systemctl_show("lixo\nsem igual\n\nActiveState=active\n"), {})

    def test_incus_csv(self):
        r = ex.parse_incus_csv(INCUS + "linha ruim\n,,\n")
        self.assertEqual(r[("ai-agent", "core")], "RUNNING")
        self.assertEqual(r[("onion-gw", "onion")], "STOPPED")
        self.assertEqual(r[("ai-agent", "outro")], "STOPPED")

    def test_docker_ps(self):
        self.assertEqual(ex.parse_docker_ps(DOCKER)[:2], [("n8n-app", "running"), ("dokploy.1.abc123", "running")])
        self.assertEqual(ex.parse_docker_ps("so-nome\n\n"), [])

    def test_estados(self):
        self.assertEqual(ex.estado_systemd("active", "running"), ("ativo", "running"))
        self.assertEqual(ex.estado_systemd("activating", "start")[0], "ativo")
        self.assertEqual(ex.estado_systemd("inactive", "dead"), ("parado", "dead"))
        self.assertEqual(ex.estado_systemd("failed", "failed")[0], "falha")
        self.assertEqual(ex.estado_systemd("", "")[0], "desconhecido")
        self.assertEqual(ex.estado_incus("RUNNING")[0], "ativo")
        self.assertEqual(ex.estado_incus("STOPPED")[0], "parado")
        self.assertEqual(ex.estado_incus("ERROR")[0], "falha")
        self.assertEqual(ex.estado_incus("???")[0], "desconhecido")
        self.assertEqual([ex.estado_docker(s)[0] for s in ("running", "exited", "created", "paused", "restarting", "dead", "x")],
                         ["ativo", "parado", "parado", "parado", "falha", "falha", "desconhecido"])


class ColetarInventarioTest(unittest.TestCase):
    def coletar(self, subs=None):
        f = FakeInv(saidas() | (subs or {}))
        return ex.coletar_inventario(catalogo(), f), f

    def est(self, r):
        return {k: v["estado"] for k, v in r.items()}

    def test_estados_completos(self):
        r, f = self.coletar()
        self.assertEqual(self.est(r), {
            "smbd": "ativo", "tailscaled": "falha", "ai-agent": "ativo", "onion-gw": "parado",
            "ro-client-build": "ativo", "n8n-app": "ativo", "dokploy": "falha", "rathena-map": "parado"})
        self.assertEqual(r["dokploy"]["detalhe"], "1/2")  # prefixo "dokploy." nao casa dokploy-postgres
        self.assertEqual(r["smbd"]["detalhe"], "running")

    def test_projetos_distintos_nao_se_misturam(self):
        r, _ = self.coletar()
        self.assertEqual(r["ai-agent"]["estado"], "ativo")  # core RUNNING, apesar de outro projeto STOPPED

    def test_chamadas_em_lote_sem_shell_e_timeout_10(self):
        _, f = self.coletar()
        self.assertEqual(len(f.chamadas), 4)
        self.assertTrue(all(t == 10 for _, t in f.chamadas))
        self.assertTrue(all(isinstance(a, list) for a, _ in f.chamadas))
        self.assertEqual(f.chamadas[0][0][:5], ["systemctl", "show", "-p", "Id,ActiveState,SubState", "smbd.service"])

    def test_falha_de_chamada_deixa_so_seus_itens_desconhecidos(self):
        r, _ = self.coletar({("incus", "list", "--all-projects", "--format", "csv", "-c", "n,s,e"):
                               subprocess.TimeoutExpired("incus", 10)})
        e = self.est(r)
        self.assertEqual((e["ai-agent"], e["onion-gw"], e["ro-client-build"]), ("desconhecido",) * 3)
        self.assertEqual(r["ai-agent"]["detalhe"], "tempo esgotado")
        self.assertEqual(e["smbd"], "ativo")

    def test_docker_indisponivel_e_rathena_indisponivel(self):
        r, _ = self.coletar({tuple(MICRO + ["docker", "ps", "-a", "--format", "{{.Names}} {{.State}}"]): (125, "", "x"),
                               tuple(INC + ["systemctl", "show", "-p", "Id,ActiveState,SubState", "rathena-map.service"]): FileNotFoundError()})
        self.assertEqual(r["n8n-app"], {"estado": "desconhecido", "detalhe": "codigo 125"})
        self.assertEqual(r["dokploy"]["estado"], "desconhecido")
        self.assertEqual(r["rathena-map"]["detalhe"], "comando indisponivel")

    def test_ausentes(self):
        r, _ = self.coletar({("incus", "list", "--all-projects", "--format", "csv", "-c", "n,s,e"): (0, "", ""),
                               tuple(MICRO + ["docker", "ps", "-a", "--format", "{{.Names}} {{.State}}"]): (0, "", "")})
        self.assertEqual(r["ai-agent"], {"estado": "desconhecido", "detalhe": "nao encontrado"})
        self.assertEqual(r["n8n-app"]["detalhe"], "nao encontrado")
        self.assertEqual(r["dokploy"], {"estado": "parado", "detalhe": "sem tarefas"})

    def test_catalogo_sem_tipo_nao_chama(self):
        f = FakeInv({})
        self.assertEqual(ex.coletar_inventario([], f), {})
        self.assertEqual(f.chamadas, [])

    def test_swarm_todas_rodando(self):
        r, _ = self.coletar({tuple(MICRO + ["docker", "ps", "-a", "--format", "{{.Names}} {{.State}}"]):
                               (0, "dokploy.1.a running\ndokploy.2.b running\n", "")})
        self.assertEqual(r["dokploy"], {"estado": "ativo", "detalhe": "2/2"})

    def test_detalhe_curto_e_ascii(self):
        r, _ = self.coletar({("systemctl", "show", "-p", "Id,ActiveState,SubState", "smbd.service", "tailscaled.service"):
                               (0, "Id=smbd.service\nActiveState=active\nSubState=" + "çx" * 40 + "\n", "")})
        d = r["smbd"]["detalhe"]
        self.assertLessEqual(len(d), 24)
        self.assertTrue(d.isascii())


class GravarInventarioTest(Base):
    def setUp(self):
        super().setUp()
        self.cfg["catalogo"] = catalogo()

    def inv(self, **kw):
        self.fake = FakeInv(saidas())
        e = ex.Executor(self.cfg, executar=self.fake, dono=self.dono, log=self.logs.append, **kw)
        e.agora_inv = lambda: 1_700_000_000
        return e

    def test_grava_json_completo(self):
        self.assertEqual(self.inv().inventariar(), 1)
        cam = os.path.join(self.estado, "servicos.json")
        with open(cam) as f:
            d = json.load(f)
        self.assertEqual(d["gerado"], 1_700_000_000)
        self.assertEqual(set(d["servicos"]), {i["id"] for i in CAT})
        self.assertEqual(d["servicos"]["smbd"]["estado"], "ativo")
        self.assertEqual(oct(os.stat(cam).st_mode & 0o777), "0o644")
        self.assertEqual([n for n in os.listdir(self.estado) if n.startswith(".")], [])

    def test_nao_toca_no_spool(self):
        self.req("10-monitor-reiniciar.req")
        self.inv().inventariar()
        self.assertEqual(os.listdir(self.spool), ["10-monitor-reiniciar.req"])
        self.assertTrue(all(c[0][0] != "systemctl" or c[0][1] == "show" for c in self.fake.chamadas))

    def test_sobrescreve_atomicamente_e_ignora_tmp_symlink(self):
        alvo = os.path.join(self._tmp.name, "alvo-externo")
        with open(alvo, "w") as f:
            f.write("intocado")
        os.symlink(alvo, os.path.join(self.estado, ".servicos.json.tmp"))
        self.inv().inventariar()
        self.inv().inventariar()
        with open(alvo) as f:
            self.assertEqual(f.read(), "intocado")
        with open(os.path.join(self.estado, "servicos.json")) as f:
            self.assertEqual(json.load(f)["gerado"], 1_700_000_000)

    def test_diretorios_ausentes_nao_cria(self):
        self.cfg["spool"] = os.path.join(self._tmp.name, "x", "spool")
        self.cfg["estado"] = os.path.join(self._tmp.name, "x", "status")
        self.assertEqual(self.inv().inventariar(), 0)
        self.assertFalse(os.path.exists(os.path.join(self._tmp.name, "x")))

    def test_status_com_symlink_e_recusado(self):
        os.rmdir(self.estado)
        os.makedirs(os.path.join(self._tmp.name, "outro"))
        os.symlink(os.path.join(self._tmp.name, "outro"), self.estado)
        with self.assertRaises(ex.Recusa):
            self.inv().inventariar()
        self.assertEqual(os.listdir(os.path.join(self._tmp.name, "outro")), [])

    def test_servicos_json_sobrevive_a_limpeza_de_resultados(self):
        self.inv().inventariar()
        for i in range(30):
            with open(os.path.join(self.estado, "%d-monitor-reiniciar.json" % (i + 1)), "w") as f:
                f.write("{}")
        self.req("99-bots-retomar.req")
        self.executor().processar_spool()
        self.assertTrue(os.path.exists(os.path.join(self.estado, "servicos.json")))


if __name__ == "__main__":
    unittest.main()
