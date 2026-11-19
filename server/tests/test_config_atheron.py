"""Config de producao deploy/config.atheron.json: chaves E8 validas pelo servidor (e pelo executor, se existir)."""
import importlib.util
import json
import os
import unittest

import _caminho  # noqa: F401
import ecossistema as eco
import icones_dados

RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(RAIZ_REPO, "deploy", "config.atheron.json")
EXECUTOR = os.path.join(RAIZ_REPO, "deploy", "kindle-monitor-executor.py")

CHAVES_ANTIGAS = ["host", "discos", "servicos", "servicos_kindle", "claude", "limiares", "s10", "balanceador",
                  "pares", "portas", "io", "comandos", "intervalo_historico_s", "intervalo_cpu_s", "cache_cpu_s"]


def _carregar_executor():
    spec = importlib.util.spec_from_file_location("executor_config_atheron", EXECUTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ex = _carregar_executor()
TEM_VALIDADORES_EXECUTOR = hasattr(_ex, "validar_aparelhos") and hasattr(_ex, "validar_rotinas")


class ConfigAtheronTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CONFIG, encoding="utf-8") as f:
            cls.cfg = json.load(f)

    def test_json_carrega(self):
        self.assertIsInstance(self.cfg, dict)

    def test_chaves_antigas_presentes(self):
        for chave in CHAVES_ANTIGAS:
            self.assertIn(chave, self.cfg)
        self.assertIn("sessoes", self.cfg["claude"])
        self.assertIn("limites", self.cfg["claude"])
        self.assertIn("tokens", self.cfg["claude"])

    def test_aparelhos_servidor_nao_descarta(self):
        lista = self.cfg["aparelhos"]
        self.assertEqual(len(eco.validar_aparelhos(lista)), len(lista))

    def test_rotinas_servidor_nao_descarta(self):
        lista = self.cfg["rotinas"]
        self.assertEqual(len(eco.validar_rotinas(lista)), len(lista))

    def test_rotinas_de_producao_sao_as_duas_do_backup(self):
        # `tokens` (tokens.json, 1 h) duplicava o aviso de dados velhos de claude.tokens: nao e rotina
        self.assertEqual([(r["id"], r["tipo"]) for r in self.cfg["rotinas"]],
                         [("senhas", "timer"), ("senhas-arq", "arquivo")])
        self.assertFalse([r for r in self.cfg["rotinas"] if r["alvo"].endswith("/tokens.json")])

    def test_nenhum_nome_empresa-x(self):
        for a in self.cfg["aparelhos"]:
            self.assertNotIn("empresa-x", a["nome"].lower())

    def test_icones_existem(self):
        for a in self.cfg["aparelhos"]:
            self.assertIn(a["icone"], icones_dados.ICONES)

    @unittest.skipUnless(TEM_VALIDADORES_EXECUTOR,
                         "executor sem validar_aparelhos/validar_rotinas ainda (E8 do executor pendente)")
    def test_aparelhos_executor_nao_descarta(self):
        lista = self.cfg["aparelhos"]
        self.assertEqual(len(_ex.validar_aparelhos(lista)), len(lista))

    @unittest.skipUnless(TEM_VALIDADORES_EXECUTOR,
                         "executor sem validar_aparelhos/validar_rotinas ainda (E8 do executor pendente)")
    def test_rotinas_executor_nao_descarta(self):
        lista = self.cfg["rotinas"]
        self.assertEqual(len(_ex.validar_rotinas(lista)), len(lista))


if __name__ == "__main__":
    unittest.main()
