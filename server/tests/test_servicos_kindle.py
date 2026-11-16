"""Coletor: catalogo + inventario root (arquivo velho, ausente, corrompido)."""
import json
import unittest

import _caminho  # noqa: F401
import coletores
import monitor_server as ms
import servicos
from test_executor_servicos import CAT

AGORA = 1_700_000_000.0


def cat():
    return servicos.validar_catalogo(CAT)


def doc(gerado=AGORA - 5, **estados):
    base = {"smbd": ("ativo", "running"), "ai-agent": ("parado", "stopped")}
    base.update(estados)
    return json.dumps({"gerado": gerado, "servicos": {k: {"estado": e, "detalhe": d} for k, (e, d) in base.items()}})


class MontarTest(unittest.TestCase):
    def estados(self, r):
        return {i["id"]: i["estado"] for i in r["itens"]}

    def test_ok(self):
        r = coletores.montar_servicos_kindle(cat(), doc(), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"]), ("ok", 5))
        e = self.estados(r)
        self.assertEqual((e["smbd"], e["ai-agent"], e["n8n-app"]), ("ativo", "parado", "desconhecido"))
        self.assertEqual(len(r["itens"]), len(CAT))
        item = r["itens"][0]
        self.assertEqual(set(item), {"id", "rotulo", "grupo", "estado", "detalhe", "verbos", "protegido", "opcional"})
        self.assertNotIn("alvo", item)

    def test_velho_ausente_corrompido_viram_desconhecido(self):
        for texto, sit in ((doc(gerado=AGORA - 61), "velho"), (doc(gerado=AGORA + 100), "velho"), (None, "ausente"),
                           ("{", "ausente"), ("[]", "ausente"), ('{"gerado": "x", "servicos": {}}', "ausente"),
                           ('{"gerado": 1, "servicos": []}', "ausente")):
            r = coletores.montar_servicos_kindle(cat(), texto, AGORA)
            self.assertEqual(r["inventario"], sit, str(texto)[:30])
            self.assertEqual(set(self.estados(r).values()), {"desconhecido"})

    def test_limite_de_60s(self):
        self.assertEqual(coletores.montar_servicos_kindle(cat(), doc(gerado=AGORA - 60), AGORA)["inventario"], "ok")
        self.assertEqual(coletores.montar_servicos_kindle(cat(), doc(gerado=AGORA - 60.5), AGORA)["inventario"], "velho")

    def test_entradas_invalidas_viram_desconhecido(self):
        texto = json.dumps({"gerado": AGORA, "servicos": {"smbd": {"estado": "voando", "detalhe": "x" * 99},
                                                           "ai-agent": "lixo", "n8n-app": {"estado": "ativo",
                                                                                           "detalhe": "aç\n" * 20}}})
        r = coletores.montar_servicos_kindle(cat(), texto, AGORA)
        e = self.estados(r)
        self.assertEqual((e["smbd"], e["ai-agent"], e["n8n-app"]), ("desconhecido", "desconhecido", "ativo"))
        d = [i for i in r["itens"] if i["id"] == "n8n-app"][0]["detalhe"]
        self.assertLessEqual(len(d), 24)
        self.assertTrue(d.isascii() and "\n" not in d)


class ColetorTest(unittest.TestCase):
    def coletor(self, arquivos, catalogo=CAT):
        def leitor(p):
            if p in arquivos:
                return arquivos[p]
            raise FileNotFoundError(p)
        cfg = {"host": "t", "discos": [], "servicos": [], "balanceador": None, "pares": [],
               "servicos_kindle": servicos.validar_catalogo(catalogo),
               "comandos": {"estado": "/run/x/status"}}
        return coletores.Coletor(cfg, leitor_arquivo=leitor, executar=lambda a: (_ for _ in ()).throw(FileNotFoundError()),
                                 agora=lambda: AGORA, dormir=lambda s: None, raiz_sys="/nao/existe")

    def test_coletar_inclui_servicos_kindle(self):
        c = self.coletor({"/run/x/status/servicos.json": doc(), "/proc/stat": "cpu 1 0 1 8 0 0 0 0\n"})
        m = c.coletar(com_pares=False)
        self.assertEqual(m["servicos_kindle"]["inventario"], "ok")
        self.assertEqual(servicos.itens_de(m), m["servicos_kindle"]["itens"])

    def test_itens_ordenados_por_grupo(self):
        c = self.coletor({"/run/x/status/servicos.json": doc()})
        grupos = [i["grupo"] for i in c.servicos_itens()]
        self.assertEqual(grupos, sorted(grupos, key=servicos.GRUPOS.index))
        self.assertEqual(len(grupos), len(CAT))

    def test_arquivo_ausente(self):
        c = self.coletor({})
        self.assertEqual(c.servicos_kindle()["inventario"], "ausente")

    def test_sem_catalogo_omite(self):
        c = self.coletor({}, catalogo=[])
        self.assertIsNone(c.servicos_kindle())
        self.assertEqual(c.servicos_itens(), [])
        self.assertNotIn("servicos_kindle", c.coletar(com_pares=False))


class ConfigWebTest(unittest.TestCase):
    def test_config_com_catalogo_invalido_recusa(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"servicos_kindle": [{"id": "A"}]}, f)
            with self.assertRaises(ValueError):
                ms.carregar_config(cam)

    def test_config_atheron_e_exemplo_carregam(self):
        import os
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for rel in ("deploy/config.atheron.json", "server/config.exemplo.json"):
            cfg = ms.carregar_config(os.path.join(raiz, rel))
            self.assertEqual(len(cfg["servicos_kindle"]), 48)


if __name__ == "__main__":
    unittest.main()
