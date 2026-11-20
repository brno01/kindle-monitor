"""Executor: gate do autoupdate fail-closed, diretorios *.req, cooldown grande/corrompido, orcamento de tempo, HOME."""
import json
import os
import subprocess
import unittest

import _caminho  # noqa: F401
import servicos
from test_executor import Base, Fake, ex

NS = 10 ** 9
PROT = [{"id": "ollama-gpu", "rotulo": "Ollama", "grupo": "host", "tipo": "systemd", "alvo": "ollama-gpu.service",
         "verbos": ["reiniciar"], "protegido": True},
        {"id": "smbd", "rotulo": "Samba", "grupo": "host", "tipo": "systemd", "alvo": "smbd.service",
         "verbos": ["reiniciar"]}]


class AutoupdateTest(Base):
    def setUp(self):
        super().setUp()
        self.cfg["catalogo"] = ex.validar_catalogo(PROT)

    def roda(self, autoupdate):
        self.req("10-svc--ollama-gpu--reiniciar.req")
        e = self.executor(Fake(autoupdate=autoupdate))
        e.processar_spool()
        return self.resultados()["10-svc--ollama-gpu--reiniciar.json"], self.fake

    def test_comando_do_gate(self):
        self.assertEqual(ex.AUTOUPDATE, ["systemctl", "show", "-p", "ActiveState", "--value",
                                         "cerberus-autoupdate.service"])
        self.assertEqual(ex.TIMEOUT_AUTOUPDATE, 10)

    def test_libera_so_inactive_e_failed(self):
        for valor in ("inactive\n", "inactive", "failed\n"):
            for f in os.listdir(self.estado):
                os.unlink(os.path.join(self.estado, f))
            r, fake = self.roda((0, valor))
            self.assertEqual(r["estado"], "ok", valor)
            self.assertIn(["systemctl", "restart", "ollama-gpu.service"], fake.chamadas)

    def test_bloqueia_todo_o_resto(self):
        casos = [(0, "active\n"), (0, "activating\n"), (0, "reloading\n"), (0, "deactivating\n"), (0, ""), (0, "\n"),
                 (0, "inactive\nactive\n"), (0, "Inactive"), (0, "lixo"), (3, "inactive\n"), (1, ""), (4, "failed\n"),
                 subprocess.TimeoutExpired("systemctl", 10), FileNotFoundError("systemctl"), OSError("x")]
        for caso in casos:
            for f in os.listdir(self.estado):
                os.unlink(os.path.join(self.estado, f))
            r, fake = self.roda(caso)
            self.assertEqual((r["estado"], r["detalhe"]), ("falhou", "atualizacao automatica em andamento"), repr(caso))
            self.assertEqual(fake.chamadas, [ex.AUTOUPDATE], repr(caso))

    def test_timeout_do_gate_e_10s(self):
        _, fake = self.roda(False)
        self.assertEqual(fake.timeout_autoupdate, 10)

    def test_servico_nao_protegido_nem_consulta_o_gate(self):
        self.req("10-svc--smbd--reiniciar.req")
        self.executor(Fake(autoupdate=True)).processar_spool()
        self.assertNotIn(ex.AUTOUPDATE, self.fake.chamadas)

    def test_acoes_rapidas_v4_nao_dependem_do_gate(self):
        # nenhuma acao rapida esta em BLOQUEADAS_NO_AUTOUPDATE; se uma entrar, passa pelo mesmo helper fail-closed
        self.assertEqual(ex.BLOQUEADAS_NO_AUTOUPDATE, ())
        ex.BLOQUEADAS_NO_AUTOUPDATE = ("bots-retomar",)
        try:
            self.req("10-bots-retomar.req")
            self.executor(Fake(autoupdate=(0, ""))).processar_spool()
            self.assertEqual(self.resultados()["10-bots-retomar.json"]["detalhe"], "atualizacao automatica em andamento")
        finally:
            ex.BLOQUEADAS_NO_AUTOUPDATE = ()


class DiretorioReqTest(Base):
    def test_diretorio_req_e_renomeado_e_a_glob_para_de_casar(self):
        os.makedirs(os.path.join(self.spool, "1-monitor-reiniciar.req"))
        os.makedirs(os.path.join(self.spool, "x.req", "dentro"))
        os.makedirs(os.path.join(self.spool, "999-bots-retomar.req"))
        self.executor().processar_spool()
        sobrou = sorted(os.listdir(self.spool))
        self.assertFalse([n for n in sobrou if n.endswith(".req")], sobrou)
        self.assertTrue(all(n.startswith(".lixo-") for n in sobrou), sobrou)
        self.assertEqual(len(sobrou), 1)  # o nao vazio fica (fora da glob); os vazios foram removidos
        self.assertTrue(os.path.isdir(os.path.join(self.spool, sobrou[0], "dentro")))
        self.assertEqual(self.fake.chamadas, [])
        self.assertIn("movido para .lixo-", "\n".join(self.logs))

    def test_nome_do_lixo_usa_epoch_e_contador(self):
        for i in range(3):
            os.makedirs(os.path.join(self.spool, "d%d.req" % i, "f"))
        self.executor(agora_ns=lambda: 1234 * NS).processar_spool()
        self.assertEqual(sorted(os.listdir(self.spool)), [".lixo-1234-1", ".lixo-1234-2", ".lixo-1234-3"])

    def test_temporarios_lixo_nao_sao_apagados_nem_executados(self):
        os.makedirs(os.path.join(self.spool, ".lixo-1-1", "f"))
        self.assertEqual(self.executor().processar_spool(), 0)
        self.assertTrue(os.path.isdir(os.path.join(self.spool, ".lixo-1-1")))

    def test_symlink_req_e_apagado_sem_seguir(self):
        alvo = os.path.join(self._tmp.name, "alvo")
        os.makedirs(alvo)
        os.symlink(alvo, os.path.join(self.spool, "5-bots-retomar.req"))
        self.executor().processar_spool()
        self.assertEqual(os.listdir(self.spool), [])
        self.assertTrue(os.path.isdir(alvo))
        self.assertEqual(self.fake.chamadas, [])


class CooldownGrandeTest(Base):
    def escreve(self, dados):
        with open(os.path.join(self.estado, ".cooldown.json"), "w") as f:
            f.write(dados if isinstance(dados, str) else json.dumps(dados))

    def test_mais_de_81_entradas_e_lido_inteiro(self):
        agora = 1_000_000 * NS
        dados = {"svc:s%03d:reiniciar" % i: agora / 1e9 - 5 for i in range(300)}
        dados["bots-retomar"] = agora / 1e9 - 5
        tam = len(json.dumps(dados))
        self.assertGreater(tam, 4096)
        self.assertLess(tam, ex.COOLDOWN_LER_MAX)
        self.escreve(dados)
        self.req("%d-bots-retomar.req" % (agora - NS))
        self.executor(agora_ns=lambda: agora).processar_spool()
        r = self.resultados()["%d-bots-retomar.json" % (agora - NS)]
        self.assertEqual((r["estado"], r["detalhe"]), ("falhou", "cooldown de 30 s"))
        self.assertEqual(self.fake.chamadas, [])

    def test_gravar_poda_entradas_velhas(self):
        agora = 1_000_000 * NS
        s = agora / 1e9
        dados = {"svc:a:parar": s - 500, "svc:b:parar": s - 61, "svc:c:parar": s - 59, "svc:d:parar": s + 500}
        self.escreve(dados)
        self.req("%d-bots-retomar.req" % (agora - NS))
        self.executor(agora_ns=lambda: agora).processar_spool()
        with open(os.path.join(self.estado, ".cooldown.json")) as f:
            gravado = json.load(f)
        self.assertEqual(set(gravado), {"svc:c:parar", "bots-retomar"})

    def test_arquivo_corrompido_ou_grande_demais_e_fail_safe(self):
        for ruim in ("{quebrado", "[]", '{"a": ' + "1" * 70000 + "}", "\xff"):
            agora = 1_000_000 * NS
            for f in os.listdir(self.estado):
                os.unlink(os.path.join(self.estado, f))
            self.escreve(ruim)
            self.req("%d-bots-retomar.req" % (agora - NS))
            self.executor(agora_ns=lambda: agora).processar_spool()
            r = self.resultados()["%d-bots-retomar.json" % (agora - NS)]
            self.assertEqual((r["estado"], r["detalhe"]), ("falhou", "cooldown indisponivel"), ruim[:20])
            self.assertEqual(self.fake.chamadas, [])
            self.assertIn("cooldown", "\n".join(self.logs))
            with open(os.path.join(self.estado, ".cooldown.json")) as f:  # reescrito: a proxima passada funciona
                self.assertEqual(json.load(f), {})

    def test_ausente_nao_bloqueia(self):
        self.req("10-bots-retomar.req")
        self.executor().processar_spool()
        self.assertEqual(self.resultados()["10-bots-retomar.json"]["estado"], "ok")


class OrcamentoTest(Base):
    def test_para_de_pegar_pedidos_depois_de_400s(self):
        self.cfg["catalogo"] = ex.validar_catalogo([
            {"id": "s%d" % i, "rotulo": "S", "grupo": "host", "tipo": "systemd", "alvo": "s%d.service" % i,
             "verbos": ["reiniciar"]} for i in range(10)])
        relogio = [0.0]
        chamadas = []

        def executar(argv, timeout):
            chamadas.append(list(argv))
            relogio[0] += 150.0  # cada comando "demora" 150 s
            return 0, "", ""
        for i in range(10):
            self.req("%d-svc--s%d--reiniciar.req" % (i + 1, i))
        e = ex.Executor(self.cfg, executar=executar, agora_ns=lambda: 5, dono=self.dono, log=self.logs.append,
                        relogio=lambda: relogio[0])
        feitos = e.processar_spool()
        self.assertEqual(feitos, 3)  # t=0, 150, 300 < 400; depois 450 >= 400
        self.assertEqual(len(chamadas), 3)
        restantes = sorted((n for n in os.listdir(self.spool) if n.endswith(".req")), key=lambda n: int(n.split("-")[0]))
        self.assertEqual(len(restantes), 7)  # ficam para o proximo disparo (mais antigos executam primeiro)
        self.assertEqual(restantes[0], "4-svc--s3--reiniciar.req")
        self.assertIn("orcamento de tempo", "\n".join(self.logs))

    def test_sem_demora_processa_os_10(self):
        for i in range(12):
            self.req("%d-monitor-reiniciar.req" % (i + 1))
        self.assertEqual(self.executor(relogio=lambda: 0.0).processar_spool(), 10)

    def test_orcamento_cabe_no_timeout_do_servico(self):
        self.assertEqual(ex.PASSADA_ORCAMENTO_S, 400)
        # ultimo pedido aceito comeca antes de 400 s e dura no maximo 90 s: < 600 s do TimeoutStartSec
        self.assertLess(ex.PASSADA_ORCAMENTO_S + ex.TIMEOUT_INCUS, 600)


class AmbienteTest(unittest.TestCase):
    def test_home_root_no_subprocess(self):
        rc, out, _ = ex.executar_padrao(["/usr/bin/env"], 5)
        linhas = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
        self.assertEqual(linhas.get("HOME"), "/root")
        self.assertEqual(linhas.get("LANG"), "C")
        self.assertNotIn("USER", linhas)


class RegexFimTest(unittest.TestCase):
    def test_quebra_de_linha_no_fim_e_recusada(self):
        for ruim in ("svc:a:ligar\n", "svc:a\n:ligar"):
            self.assertIsNone(servicos.acao_svc(ruim))
            self.assertIsNone(ex.RE_SVC_ACAO.match(ruim))
        self.assertIsNone(servicos.nome_para_acao("svc--a--ligar\n"))
        self.assertIsNone(ex.nome_para_acao("svc--a--ligar\n"))
        self.assertIsNone(servicos.nome_para_acao("abc\n"))
        self.assertIsNone(ex.nome_para_acao("abc\n"))
        self.assertIsNone(ex.RE_REQ.match("1-abc.req\n"))
        self.assertIsNone(ex.RE_JSON.match("1-abc.json\n"))

    def test_catalogo_recusa_id_e_alvo_com_quebra_de_linha(self):
        base = {"id": "a", "rotulo": "A", "grupo": "host", "tipo": "systemd", "alvo": "a.service", "verbos": []}
        for campo, valor in (("id", "a\n"), ("alvo", "a.service\n"), ("alvo", "-a.service")):
            ruim = dict(base, **{campo: valor})
            for f in (servicos.validar_catalogo, ex.validar_catalogo):
                with self.assertRaises(ValueError, msg=(campo, valor)):
                    f([ruim])
        with self.assertRaises(ValueError):
            servicos.validar_catalogo([dict(base, tipo="incus", alvo="x", projeto="core\n")])
        with self.assertRaises(ValueError):
            ex.validar_catalogo([dict(base, tipo="incus", alvo="x", projeto="core\n")])


class PoliticaCatalogoTest(unittest.TestCase):
    INFRA = ("docker-socket-proxy", "dokploy-traefik", "dokploy", "dokploy-postgres", "n8n-postgres", "n8n-redis",
             "incus", "tailscaled", "nftables", "pihole-ftl", "smbd")

    def test_infraestrutura_sem_ligar_nem_parar(self):
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for rel in ("deploy/config.atheron.example.json", "server/config.exemplo.json"):
            with open(os.path.join(raiz, rel)) as f:
                cat = {c["id"]: c for c in servicos.validar_catalogo(json.load(f)["servicos_kindle"])}
            for i in self.INFRA:
                self.assertTrue(set(cat[i]["verbos"]) <= {"reiniciar"}, (rel, i, cat[i]["verbos"]))
            for i in ("incus", "tailscaled", "nftables", "dokploy", "dokploy-postgres"):
                self.assertEqual(cat[i]["verbos"], [], i)


if __name__ == "__main__":
    unittest.main()
