"""Executor: aparelhos da tailnet (validar_aparelhos, parse_tailscale, inventariar -> aparelhos.json)."""
import json
import os
import re
import subprocess
import tempfile
import unittest

import _caminho  # noqa: F401
from test_executor import Base, ex

TS = ["tailscale", "status", "--json"]
AQUI = os.path.dirname(os.path.abspath(__file__))
NS = 1_700_000_000


def ap(**k):
    d = {"id": "gw", "nome": "cerberus-gw", "rotulo": "Gateway", "icone": "rede"}
    d.update(k)
    return d


def fixture():
    with open(os.path.join(AQUI, "fixtures_tailscale_status.json"), encoding="utf-8") as f:
        return f.read()


def catalogo():
    return ex.validar_aparelhos([
        ap(),
        ap(id="s10", nome="galaxy-s10", rotulo="Galaxy S10", icone="celular", alerta_offline_min=30),
        ap(id="kindle", nome="kindle-monitor", rotulo="Kindle", icone="leitor"),
        ap(id="fone", nome="phone-a", rotulo="Fone A", icone="celular"),
        ap(id="sumido", nome="nao-existe", rotulo="Sumido", icone="celular"),
    ])


def sem_ip_nem_segredo(teste, texto):
    """Nenhuma string do arquivo tem '@', pedaco de IP ou '100.'."""
    def strings(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for k, v in o.items():
                yield from strings(k)
                yield from strings(v)
        elif isinstance(o, list):
            for v in o:
                yield from strings(v)
    for s in strings(json.loads(texto)):
        teste.assertNotIn("@", s)
        teste.assertNotIn("100.", s)
        teste.assertIsNone(re.search(r"\.\d", s), s)
        teste.assertIsNone(re.search(r"\d+\.\d+\.\d+\.\d+", s), s)
        teste.assertNotIn(":", s)


class ValidarTest(unittest.TestCase):
    def ruim(self, lista, trecho=None):
        with self.assertRaises(ValueError) as c:
            ex.validar_aparelhos(lista)
        if trecho:
            self.assertIn(trecho, str(c.exception))

    def test_valido(self):
        self.assertEqual(ex.validar_aparelhos([ap(alerta_offline_min=10)]), [ap(alerta_offline_min=10)])
        self.assertEqual(ex.validar_aparelhos(None), [])
        self.assertEqual(ex.validar_aparelhos([]), [])

    def test_nao_e_lista_ou_item_nao_e_objeto(self):
        self.ruim({"id": "x"})
        self.ruim("gw")
        self.ruim(["gw"])

    def test_maximo_16(self):
        ok = [ap(id="a%d" % i, nome="n%d" % i) for i in range(16)]
        self.assertEqual(len(ex.validar_aparelhos(ok)), 16)
        self.ruim(ok + [ap(id="z", nome="z")])

    def test_id(self):
        for v in ("", "A", "a_b", "a" * 25, "a b", "a\n", None, 1):
            self.ruim([ap(id=v)])
        self.assertEqual(ex.validar_aparelhos([ap(id="a" * 24)])[0]["id"], "a" * 24)

    def test_nome(self):
        for v in ("", "Gw", "a_b", "a" * 64, "a.b", "a\n", None, 1):
            self.ruim([ap(nome=v)])

    def test_nome_com_empresa-x_recusado(self):
        for v in ("empresa-x-x", "meu-empresa-x", "empresa-x", "empresa-x"):
            self.ruim([ap(nome=v)])

    def test_rotulo(self):
        for v in ("", "a" * 17, "café", "a\nb", "a\x00", None, 1):
            self.ruim([ap(rotulo=v)])
        self.assertEqual(ex.validar_aparelhos([ap(rotulo="a" * 16)])[0]["rotulo"], "a" * 16)

    def test_icone_formato(self):
        for v in (None, "", "a", "A", "a" * 17, "a1", "a-b", 1):
            self.ruim([ap(icone=v)])
        self.ruim([{"id": "gw", "nome": "gw", "rotulo": "G"}])  # obrigatorio

    def test_alerta_offline_min(self):
        for v in (1, 10080):
            self.assertEqual(ex.validar_aparelhos([ap(alerta_offline_min=v)])[0]["alerta_offline_min"], v)
        for v in (0, 10081, -1, 1.5, "10", True, False, None):
            self.ruim([ap(alerta_offline_min=v)])

    def test_id_e_nome_repetidos(self):
        self.ruim([ap(), ap(nome="outro")])
        self.ruim([ap(), ap(id="outro")])

    def test_chave_desconhecida(self):
        self.ruim([ap(extra=1)])

    def test_nao_aliasa_a_entrada(self):
        orig = [ap()]
        r = ex.validar_aparelhos(orig)
        r[0]["id"] = "mudou"
        self.assertEqual(orig[0]["id"], "gw")


class ParseTest(unittest.TestCase):
    def parse(self, texto, cat=None, agora=NS):
        return ex.parse_tailscale(texto, catalogo() if cat is None else cat, agora=lambda: agora)

    def test_fixture_realista(self):
        d = self.parse(fixture())
        self.assertEqual(d["versao"], 1)
        self.assertEqual(d["gerado"], NS)
        self.assertIsNone(d["erro"])
        self.assertEqual(set(d), {"versao", "gerado", "erro", "aparelhos"})
        self.assertEqual(set(d["aparelhos"]), {"gw", "s10", "kindle", "fone", "sumido"})
        for v in d["aparelhos"].values():
            self.assertEqual(set(v), {"online", "visto_em", "conexao"})
        ap_ = d["aparelhos"]
        self.assertEqual(ap_["gw"], {"online": True, "visto_em": None, "conexao": "relay"})
        self.assertEqual(ap_["s10"], {"online": True, "visto_em": None, "conexao": "direto"})
        self.assertEqual(ap_["kindle"]["conexao"], "direto")
        self.assertIsInstance(ap_["kindle"]["visto_em"], int)
        self.assertEqual(ap_["kindle"]["visto_em"], 1795047049)  # 2026-11-19T00:10:49Z
        self.assertIs(ap_["fone"]["online"], False)
        self.assertEqual(ap_["fone"]["visto_em"], 1794972612)  # 2026-11-18T03:30:12Z
        self.assertEqual(ap_["sumido"], {"online": None, "visto_em": None, "conexao": None})

    def test_peer_fora_do_catalogo_nunca_aparece(self):
        txt = fixture()
        self.assertIn("empresa-x-x", txt)
        d = self.parse(txt)
        self.assertNotIn("empresa-x-x", json.dumps(d))
        self.assertNotIn("empresa-x", json.dumps(d))
        self.assertNotIn("nomad", d["aparelhos"])
        self.assertNotIn("games", json.dumps(d))

    def test_nada_vaza_no_json_gerado(self):
        txt = json.dumps(self.parse(fixture()))
        sem_ip_nem_segredo(self, txt)
        for proibido in ("example", "ts.net", "nodekey", "linux", "user-a", "tag:", "198.51", "203.0", "atheron"):
            self.assertNotIn(proibido, txt)

    def test_catalogo_vazio(self):
        d = self.parse(fixture(), cat=[])
        self.assertEqual(d["aparelhos"], {})
        self.assertIsNone(d["erro"])

    def test_casa_so_o_primeiro_rotulo(self):
        txt = json.dumps({"Peer": {
            "k1": {"DNSName": "cerberus-gw-2.t.ts.net.", "Online": True},
            "k2": {"DNSName": "x.cerberus-gw.ts.net.", "Online": True},
            "k3": {"DNSName": "CERBERUS-GW.t.ts.net.", "Online": True}}})
        self.assertEqual(self.parse(txt, cat=ex.validar_aparelhos([ap()]))["aparelhos"]["gw"]["online"], True)  # k3
        txt = json.dumps({"Peer": {"k1": {"DNSName": "cerberus-gw-2.t.ts.net.", "Online": True},
                                   "k2": {"DNSName": "x.cerberus-gw.ts.net.", "Online": True}}})
        self.assertIsNone(self.parse(txt, cat=ex.validar_aparelhos([ap()]))["aparelhos"]["gw"]["online"])

    def test_duplicado_prefere_online(self):
        txt = json.dumps({"Peer": {"a": {"DNSName": "cerberus-gw.t.", "Online": False},
                                   "b": {"DNSName": "cerberus-gw.t.", "Online": True}}})
        self.assertIs(self.parse(txt, cat=ex.validar_aparelhos([ap()]))["aparelhos"]["gw"]["online"], True)

    def peer(self, **campos):
        base = {"DNSName": "cerberus-gw.t.ts.net."}
        base.update(campos)
        txt = json.dumps({"Peer": {"k": base}})
        return self.parse(txt, cat=ex.validar_aparelhos([ap()]))["aparelhos"]["gw"]

    def test_online_so_aceita_bool(self):
        for v in ("true", 1, 0, None, [], {}):
            self.assertIsNone(self.peer(Online=v)["online"])
        self.assertIs(self.peer(Online=True)["online"], True)
        self.assertIs(self.peer(Online=False)["online"], False)
        self.assertIsNone(self.peer()["online"])

    def test_visto_em(self):
        self.assertEqual(self.peer(LastSeen="2026-11-18T03:30:12Z")["visto_em"], 1794972612)
        self.assertEqual(self.peer(LastSeen="2026-11-18T03:30:12.123456789Z")["visto_em"], 1794972612)
        self.assertEqual(self.peer(LastSeen="2026-11-18T03:30:12.1Z")["visto_em"], 1794972612)
        self.assertEqual(self.peer(LastSeen="2026-11-18T00:30:12-03:00")["visto_em"], 1794972612)
        self.assertEqual(self.peer(LastSeen="2026-11-18T03:30:12")["visto_em"], 1794972612)  # sem fuso = UTC
        for v in ("", "0001-01-01T00:00:00Z", "1970-01-01T00:00:00Z", "lixo", "2026-13-45T00:00:00Z", 12345,
                  None, [], "9999-12-31T23:59:59Z" + "9" * 50, "\x00", "0000-00-00T00:00:00Z"):
            self.assertIsNone(self.peer(LastSeen=v)["visto_em"], v)

    def test_conexao(self):
        self.assertEqual(self.peer(CurAddr="203.0.113.5:41641", Relay="sao")["conexao"], "direto")
        self.assertEqual(self.peer(CurAddr="", Relay="sao")["conexao"], "relay")
        self.assertIsNone(self.peer(CurAddr="", Relay="")["conexao"])
        self.assertIsNone(self.peer()["conexao"])
        self.assertIsNone(self.peer(CurAddr=5, Relay=["x"])["conexao"])
        # o valor do endereco nunca e copiado
        self.assertNotIn("203", json.dumps(self.peer(CurAddr="203.0.113.5:41641")))

    def assert_erro(self, d, cat=None):
        self.assertIsInstance(d["erro"], str)
        self.assertTrue(0 < len(d["erro"]) <= 40)
        self.assertTrue(d["erro"].isascii())
        self.assertEqual(d["versao"], 1)
        self.assertEqual(d["gerado"], NS)
        self.assertEqual(set(d["aparelhos"]), {i["id"] for i in (catalogo() if cat is None else cat)})
        for v in d["aparelhos"].values():
            self.assertEqual(v, {"online": None, "visto_em": None, "conexao": None})

    def test_saida_vazia(self):
        for t in ("", "   \n", None, b"{}"):
            self.assert_erro(self.parse(t))

    def test_json_truncado_e_lixo(self):
        txt = fixture()
        for t in (txt[:len(txt) // 2], txt[:-5], "{", "nao e json", "\x00\xff", '{"Peer": {"a": '):
            self.assert_erro(self.parse(t))

    def test_tipos_errados(self):
        for t in ("[]", "null", '"x"', "12", "true", '{"Peer": null}', '{"Peer": []}', '{"Peer": "x"}',
                  '{"Peer": 5}', '{"Peer": [1,2]}', "{}", '{"Other": {}}'):
            self.assert_erro(self.parse(t))

    def test_peers_com_itens_ruins_sao_ignorados(self):
        txt = json.dumps({"Peer": {"a": 5, "b": None, "c": [], "d": {"DNSName": 7, "Online": True},
                                   "e": {"DNSName": None}, "f": {"Online": True},
                                   "g": {"DNSName": "cerberus-gw.t.", "Online": True}}})
        d = self.parse(txt, cat=ex.validar_aparelhos([ap()]))
        self.assertIsNone(d["erro"])
        self.assertIs(d["aparelhos"]["gw"]["online"], True)

    def test_peer_vazio_e_valido_sem_erro(self):
        d = self.parse('{"Peer": {}}')
        self.assertIsNone(d["erro"])
        self.assertTrue(all(v["online"] is None for v in d["aparelhos"].values()))

    def test_aninhamento_profundo_nao_levanta(self):
        self.assert_erro(self.parse("[" * 100000))
        self.assert_erro(self.parse('{"a":' * 50000))

    def test_saida_enorme_vira_erro(self):
        self.assert_erro(self.parse('{"Peer": {}, "x": "' + "a" * (5 << 20) + '"}'))

    def test_erro_nunca_contem_trecho_da_entrada(self):
        d = self.parse("segredo@exemplo.com 100.1.2.3 {")
        self.assert_erro(d)
        self.assertNotIn("segredo", json.dumps(d))


class FakeTS:
    def __init__(self, resposta):
        self.resposta = resposta
        self.chamadas = []

    def __call__(self, argv, timeout):
        self.chamadas.append((list(argv), timeout))
        if argv != TS:
            return 0, "", ""
        if isinstance(self.resposta, BaseException):
            raise self.resposta
        return self.resposta


class InventarioTest(Base):
    def setUp(self):
        super().setUp()
        self.cfg["aparelhos"] = catalogo()

    def inv(self, resposta, cfg=None):
        self.fake = FakeTS(resposta)
        e = ex.Executor(cfg or self.cfg, executar=self.fake, dono=self.dono, log=self.logs.append)
        e.agora_inv = lambda: NS
        return e

    def ler(self, nome):
        with open(os.path.join(self.estado, nome), encoding="utf-8") as f:
            return f.read()

    def test_chama_tailscale_com_argv_fixo_e_timeout_10(self):
        self.inv((0, fixture(), "")).inventariar()
        self.assertEqual(self.fake.chamadas, [(TS, 10)])
        self.assertEqual(ex.TIMEOUT_TAILSCALE, 10)

    def test_grava_aparelhos_json_atomico_0644(self):
        self.assertEqual(self.inv((0, fixture(), "")).inventariar(), 1)
        cam = os.path.join(self.estado, "aparelhos.json")
        self.assertEqual(oct(os.stat(cam).st_mode & 0o777), "0o644")
        d = json.loads(self.ler("aparelhos.json"))
        self.assertEqual(d["gerado"], NS)
        self.assertIsNone(d["erro"])
        self.assertIs(d["aparelhos"]["gw"]["online"], True)
        self.assertEqual([n for n in os.listdir(self.estado) if n.startswith(".")], [])
        self.assertIn("servicos.json", os.listdir(self.estado))

    def test_arquivo_gravado_sem_empresa-x_nem_ip(self):
        self.inv((0, fixture(), "")).inventariar()
        txt = self.ler("aparelhos.json")
        self.assertNotIn("empresa-x", txt)
        sem_ip_nem_segredo(self, txt)

    def test_sem_catalogo_nao_chama_tailscale_nem_grava(self):
        self.cfg["aparelhos"] = []
        self.inv((0, fixture(), "")).inventariar()
        self.assertEqual(self.fake.chamadas, [])
        self.assertEqual(os.listdir(self.estado), ["servicos.json"])

    def test_chave_ausente_da_cfg_e_lista_vazia(self):
        del self.cfg["aparelhos"]
        self.inv((0, fixture(), "")).inventariar()
        self.assertEqual(self.fake.chamadas, [])

    def todos_nulos(self, erro_esperado=None):
        d = json.loads(self.ler("aparelhos.json"))
        self.assertIsInstance(d["erro"], str)
        self.assertLessEqual(len(d["erro"]), 40)
        if erro_esperado:
            self.assertEqual(d["erro"], erro_esperado)
        self.assertEqual(set(d["aparelhos"]), set(i["id"] for i in self.cfg["aparelhos"]))
        for v in d["aparelhos"].values():
            self.assertEqual(v, {"online": None, "visto_em": None, "conexao": None})
        self.assertIn("servicos.json", os.listdir(self.estado))  # nao derruba os servicos

    def test_timeout(self):
        self.inv(subprocess.TimeoutExpired(TS, 10)).inventariar()
        self.todos_nulos("tempo esgotado")

    def test_binario_ausente(self):
        self.inv(FileNotFoundError()).inventariar()
        self.todos_nulos("comando indisponivel")

    def test_codigo_de_saida(self):
        self.inv((1, "", "daemon parado: user@x 100.1.2.3")).inventariar()
        self.todos_nulos()
        self.assertNotIn("daemon", self.ler("aparelhos.json"))  # stderr nunca entra
        self.assertNotIn("@", self.ler("aparelhos.json"))

    def test_saida_vazia_truncada_e_tipos_errados(self):
        for saida in ("", fixture()[:300], "[1,2]", '{"Peer": 3}'):
            self.inv((0, saida, "")).inventariar()
            self.todos_nulos()

    def test_excecao_inesperada_do_executor_nao_derruba(self):
        self.inv(ValueError("x")).inventariar()
        self.todos_nulos()

    def test_servicos_gravado_mesmo_com_aparelhos_falhando(self):
        self.inv(subprocess.TimeoutExpired(TS, 10)).inventariar()
        with open(os.path.join(self.estado, "servicos.json")) as f:
            self.assertEqual(json.load(f)["gerado"], NS)

    def test_tmp_symlink_nao_e_seguido(self):
        alvo = os.path.join(self._tmp.name, "alvo-externo")
        with open(alvo, "w") as f:
            f.write("intocado")
        os.symlink(alvo, os.path.join(self.estado, ".aparelhos.json.tmp"))
        self.inv((0, fixture(), "")).inventariar()
        with open(alvo) as f:
            self.assertEqual(f.read(), "intocado")
        self.assertIsNone(json.loads(self.ler("aparelhos.json"))["erro"])

    def test_aparelhos_json_sobrevive_a_limpeza_de_resultados(self):
        self.inv((0, fixture(), "")).inventariar()
        for i in range(30):
            with open(os.path.join(self.estado, "%d-monitor-reiniciar.json" % (i + 1)), "w") as f:
                f.write("{}")
        self.req("99-bots-retomar.req")
        self.executor().processar_spool()
        self.assertTrue(os.path.exists(os.path.join(self.estado, "aparelhos.json")))


class CfgTest(unittest.TestCase):
    def cfg(self, dados):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(dados, f)
            return ex.carregar_cfg(cam)

    def test_ausente_e_lista_vazia(self):
        self.assertEqual(self.cfg({})["aparelhos"], [])

    def test_le_aparelhos(self):
        c = self.cfg({"aparelhos": [ap()]})
        self.assertEqual(c["aparelhos"], [ap()])
        self.assertNotIn("aparelhos_erro", c)

    def test_invalida_vira_lista_vazia_com_motivo_e_nao_derruba_servicos(self):
        c = self.cfg({"aparelhos": [ap(nome="empresa-x-x")], "servicos_kindle": []})
        self.assertEqual(c["aparelhos"], [])
        self.assertIn("aparelhos", c["aparelhos_erro"])

    def test_main_loga_aviso_no_inventario(self):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"aparelhos": [ap(nome="empresa-x-x")]}, f)
            logs, vistos = [], []

            class Falso:
                def __init__(self, cfg, log=None):
                    vistos.append(cfg["aparelhos"])

                def inventariar(self):
                    vistos.append("inventariou")

            real, ex.Executor = ex.Executor, Falso
            try:
                self.assertEqual(ex.main(["--config", cam, "--inventario"], log=logs.append), 0)
            finally:
                ex.Executor = real
        self.assertEqual(vistos, [[], "inventariou"])  # lista vazia: o inventario segue, sem aparelhos
        self.assertEqual(len(logs), 1)
        self.assertIn("aparelhos", logs[0])
        self.assertTrue(logs[0].isascii())


class ParidadeTest(unittest.TestCase):
    def test_arquivos_de_config_do_repo_passam(self):
        raiz = os.path.dirname(AQUI)
        for rel in (("..", "deploy", "config.atheron.json"), ("config.exemplo.json",)):
            with open(os.path.join(raiz, *rel), encoding="utf-8") as f:
                dados = json.load(f)
            if "aparelhos" in dados:
                ex.validar_aparelhos(dados["aparelhos"])


if __name__ == "__main__":
    unittest.main()
