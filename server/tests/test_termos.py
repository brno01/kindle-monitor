"""Termos bloqueados (filtro de privacidade configuravel): validacao no web e no executor, e o efeito nos dois."""
import json
import os
import tempfile
import unittest

import _caminho  # noqa: F401
import dev_fontes
import ecossistema as eco
import monitor_server as ms
import termos
from test_executor import Base, ex
from test_executor_rotinas import FakeSys, NS

T = _caminho.TERMO_BLOQUEADO

VALIDOS = [[], None, ["empresa-x"], ["a1", "b.c_d-e"], ["x" * 40], ["empresa-x", "empresa-x"]]
INVALIDOS = [
    "empresa-x", {"a": 1}, [1], [None], [""], ["a"], ["x" * 41], ["Empresa-X"], ["empresa x"], ["empresa/x"],
    ["-x"], ["_x"], ["empresa-x\n"], ["empresa​-x"], ["café"], ["a" * 2 + "\x00"], [["x"]],
    ["t%d" % i for i in range(17)],
]


class ValidacaoTest(unittest.TestCase):
    def tearDown(self):
        termos.definir(None)

    def test_servidor_e_executor_decidem_igual(self):
        for entrada in VALIDOS + INVALIDOS:
            with self.subTest(entrada=entrada):
                try:
                    r_ex = ex.validar_termos(entrada)
                except ValueError:
                    r_ex = None
                try:
                    r_sv = termos.validar(entrada)
                except ValueError:
                    r_sv = None
                self.assertEqual(r_sv, r_ex)
                self.assertEqual(r_ex is not None, entrada in VALIDOS)

    def test_dedup_e_tupla(self):
        self.assertEqual(termos.validar(["empresa-x", "empresa-x", "b2"]), ("empresa-x", "b2"))
        self.assertEqual(ex.validar_termos(["empresa-x", "empresa-x", "b2"]), ("empresa-x", "b2"))

    def test_mensagem_nao_cita_o_valor(self):
        for fn in (termos.validar, ex.validar_termos):
            with self.assertRaises(ValueError) as c:
                fn(["Segredo-Interno"])
            self.assertNotIn("segredo", str(c.exception).lower())

    def test_padrao_neutro_nao_filtra(self):
        termos.definir(None)
        self.assertEqual(termos.obter(), ())
        self.assertFalse(termos.cita("empresa-x-api"))

    def test_cita_ignora_caixa_e_so_str(self):
        termos.definir([T])
        self.assertTrue(termos.cita("meu-Empresa-X-api"))
        self.assertTrue(termos.cita("ok", "EMPRESA-X"))
        self.assertFalse(termos.cita("ok", None, 3, "outra"))
        self.assertTrue(ex.cita_termo("Srv-EMPRESA-X.mount", (T,)))
        self.assertFalse(ex.cita_termo("Srv-EMPRESA-X.mount", ()))


class ConfigServidorTest(unittest.TestCase):
    def tearDown(self):
        termos.definir(None)

    def carregar(self, dados):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(dados, f)
            return ms.carregar_config(cam)

    def test_sem_a_chave_lista_vazia(self):
        self.assertEqual(self.carregar({})["termos_bloqueados"], [])
        self.assertEqual(termos.obter(), ())

    def test_chave_ativa_o_filtro(self):
        cfg = self.carregar({"termos_bloqueados": [T]})
        self.assertEqual(cfg["termos_bloqueados"], [T])
        self.assertEqual(termos.obter(), (T,))
        self.assertEqual(eco.validar_aparelhos([{"id": "a", "nome": "x-empresa-x", "rotulo": "A", "icone": "rede"}]), [])

    def test_chave_invalida_recusa_a_config(self):
        for ruim in ("empresa-x", ["Empresa-X"], [1]):
            with self.assertRaises(ValueError):
                self.carregar({"termos_bloqueados": ruim})

    def test_filtro_no_leitor_de_github(self):
        self.carregar({"termos_bloqueados": [T]})
        self.assertTrue(dev_fontes._proibido("repo", "ver Empresa-X"))
        self.carregar({})
        self.assertFalse(dev_fontes._proibido("repo", "ver Empresa-X"))

    def test_exemplo_versionado_traz_termo_ficticio(self):
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cfg = self.carregar_arquivo(os.path.join(raiz, "deploy", "config.atheron.example.json"))
        self.assertEqual(cfg["termos_bloqueados"], [T])

    def carregar_arquivo(self, cam):
        return ms.carregar_config(cam)


class ConfigExecutorTest(unittest.TestCase):
    def carregar(self, dados):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(dados, f)
            return ex.carregar_cfg(cam)

    def test_padrao_e_chave(self):
        self.assertEqual(self.carregar({})["termos_bloqueados"], ())
        self.assertEqual(self.carregar({"termos_bloqueados": [T]})["termos_bloqueados"], (T,))

    def test_invalido_recusa_a_config_inteira(self):
        for ruim in ("empresa-x", ["Empresa-X"], [1], ["a"] * 17 + ["b"]):
            with self.assertRaises(ValueError):
                self.carregar({"termos_bloqueados": ruim})

    def test_main_com_termos_invalidos_loga_e_sai_0_sem_fazer_nada(self):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"termos_bloqueados": ["Ruim"]}, f)
            logs = []
            self.assertEqual(ex.main(["--config", cam, "--inventario"], log=logs.append), 0)
        self.assertEqual(len(logs), 1)
        self.assertIn("config invalida", logs[0])
        self.assertNotIn("ruim", logs[0].lower())

    def test_aparelho_com_termo_derruba_so_a_lista_de_aparelhos(self):
        ap = {"id": "a", "nome": "empresa-x-api", "rotulo": "A", "icone": "rede"}
        cfg = self.carregar({"aparelhos": [ap], "termos_bloqueados": [T]})
        self.assertEqual(cfg["aparelhos"], [])
        self.assertIn("aparelhos", cfg["aparelhos_erro"])


class ExecutorUsaOsTermosTest(Base):
    def test_inventario_de_rotinas_descarta_unidade_com_termo(self):
        self.cfg["termos_bloqueados"] = (T,)
        e = self.executor()
        self.assertEqual(e.termos, (T,))
        doc = ex.coletar_rotinas([], FakeSys(falhas=(0, "empresa-x-sync.service loaded failed failed x\n"
                                                       "ok.service loaded failed failed x\n", "")), agora=lambda: NS,
                                 termos=e.termos)
        self.assertEqual(doc["unidades_falhas"], {"n": 1, "nomes": ["ok.service"]})

    def test_sem_termos_o_executor_nao_filtra(self):
        self.assertEqual(self.executor().termos, ())


class OllamaUrlTest(unittest.TestCase):
    def test_validos(self):
        for u, esperado in (("http://127.0.0.1:11434", "http://127.0.0.1:11434"), ("http://10.0.0.1:11435/", "http://10.0.0.1:11435"),
                            ("http://100.64.0.9:1", "http://100.64.0.9:1"), (None, None)):
            self.assertEqual(ex.validar_ollama_url(u), esperado)

    def test_invalidos(self):
        for u in ("https://10.0.0.1:1", "http://8.8.8.8:11434", "http://localhost:11434", "http://10.0.0.1", "http://u:p@10.0.0.1:1",
                  "http://10.0.0.1:1/x", "http://10.0.0.256:1", "http://10.0.0.1:70000", 5, ["x"]):
            with self.assertRaises(ValueError):
                ex.validar_ollama_url(u)

    def test_config_troca_a_url(self):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"ollama_url": "http://10.0.0.1:11435"}, f)
            self.assertEqual(ex.carregar_cfg(cam)["ollama"], "http://10.0.0.1:11435")


if __name__ == "__main__":
    unittest.main()
