import json
import os
import unittest

import _caminho  # noqa: F401
import servicos

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def item(**k):
    d = {"id": "a", "rotulo": "A", "grupo": "host", "tipo": "systemd", "alvo": "a.service", "verbos": ["reiniciar"]}
    d.update(k)
    return d


def carregar(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return json.load(f)["servicos_kindle"]


class CatalogoTest(unittest.TestCase):
    def test_catalogos_reais_sao_validos(self):
        for rel in ("deploy/config.atheron.example.json", "server/config.exemplo.json"):
            cat = servicos.validar_catalogo(carregar(rel))
            self.assertEqual(len(cat), 48)
            self.assertEqual(len({c["id"] for c in cat}), 48)

    def test_catalogo_atheron_conteudo(self):
        cat = {c["id"]: c for c in servicos.validar_catalogo(carregar("deploy/config.atheron.example.json"))}
        self.assertEqual(cat["cerberus-updater"]["protegido"], True)
        self.assertEqual(cat["onion-gw"]["projeto"], "onion")
        self.assertEqual(cat["ro-client-build"]["projeto"], "sandbox")
        self.assertEqual(cat["ai-agent"]["projeto"], "core")
        self.assertTrue(cat["dokploy"]["prefixo"])
        self.assertEqual(cat["dokploy"]["alvo"], "dokploy.")
        self.assertEqual(cat["pihole-ftl"]["alvo"], "pihole-FTL.service")
        self.assertEqual(cat["vaultwarden"]["verbos"], ["reiniciar"])
        self.assertFalse(cat["vaultwarden"]["opcional"])
        for i in ("ai-coder", "cloudflare-gateway", "microservices-old", "onion-gw", "ro-client-build",
                  "cerberus-optimizer", "cerberus-tailnet-sync", "nftables"):
            self.assertTrue(cat[i]["opcional"], i)
        self.assertEqual([c["id"] for c in cat.values() if c["grupo"] == "ragnarok"],
                         ["rathena-login", "rathena-char", "rathena-map", "rathena-web"])
        self.assertTrue(all(c["protegido"] for c in cat.values() if c["grupo"] == "ragnarok"))
        self.assertEqual(cat["tailscaled"]["verbos"], [])

    def test_invalidos(self):
        ruins = [
            "x", [1], [item(id="A")], [item(id="a--b")], [item(id="-a")], [item(id="a" * 41)], [item(id="")],
            [item(), item()], [item(rotulo="")], [item(rotulo="x" * 29)], [item(rotulo="aç")],
            [item(grupo="x")], [item(tipo="x")], [item(alvo="-x.service")], [item(alvo="a b.service")],
            [item(alvo="a$(x).service")], [item(alvo="a" * 65)], [item(alvo="a")],
            [item(projeto="core")], [item(tipo="incus", alvo="x", projeto="Ruim!")],
            [item(prefixo=True)], [item(tipo="docker", alvo="x.", prefixo=True, verbos=["reiniciar"])],
            [item(verbos=["apagar"])], [item(verbos="reiniciar")], [item(verbos=["parar", "parar"])],
            [item(protegido="sim")], [item(opcional=1)], [item(extra=1)], [item(id=5)],
        ]
        for r in ruins:
            with self.assertRaises(ValueError, msg=str(r)):
                servicos.validar_catalogo(r)

    def test_vazio(self):
        self.assertEqual(servicos.validar_catalogo([]), [])
        self.assertEqual(servicos.validar_catalogo(None), [])


class NomeSpoolTest(unittest.TestCase):
    def test_ida_e_volta(self):
        for acao in ("svc:ai-agent:reiniciar", "svc:a:ligar", "svc:x1-y2:parar", "svc:" + "a" * 40 + ":parar",
                     "gpu-descarregar", "bots-pausar"):
            nome = servicos.acao_para_nome(acao)
            self.assertNotIn(":", nome)
            self.assertEqual(servicos.nome_para_acao(nome), acao)

    def test_invalidos(self):
        for ruim in ("svc:A:ligar", "svc:a:apagar", "svc::ligar", "svc:a:ligar:x", "svc--a--ligar", "ab", "x" * 33, "Gpu",
                     "svc:" + "a" * 41 + ":ligar"):
            with self.assertRaises(ValueError, msg=ruim):
                servicos.acao_para_nome(ruim)
        for ruim in ("svc--a--apagar", "svc--A--ligar", "svc--ligar", "svc----ligar", "a", "a/b"):
            self.assertIsNone(servicos.nome_para_acao(ruim), ruim)

    def test_rotulo_acao(self):
        self.assertEqual(servicos.rotulo_acao("svc:ai-coder:reiniciar"), "Reiniciar ai-coder")
        self.assertEqual(servicos.rotulo_acao("bots-pausar"), "bots-pausar")


class ItensTest(unittest.TestCase):
    def itens(self):
        return [item(id="a", estado="ativo"), item(id="b", estado="falha"),
                item(id="c", estado="parado"), item(id="d", estado="parado", opcional=True),
                item(id="e", estado="desconhecido")]

    def test_resumo(self):
        r = servicos.resumo(self.itens())
        self.assertEqual((r["total"], r["ok"], r["parados"], r["falhas"], r["desconhecidos"]), (5, 1, 2, 1, 1))
        self.assertEqual([i["id"] for i in r["atencao"]], ["b", "c"])
        self.assertEqual(servicos.texto_resumo(self.itens()), "5 servicos · 1 ok · 2 parados · 1 falhas · 1 ?")

    def test_verbos_visiveis(self):
        v = ["reiniciar", "ligar", "parar"]
        f = lambda e, vs: servicos.verbos_visiveis({"estado": e, "verbos": vs})
        self.assertEqual(f("ativo", v), ["reiniciar", "parar"])
        self.assertEqual(f("parado", v), ["ligar"])
        self.assertEqual(f("falha", v), ["reiniciar"])
        self.assertEqual(f("desconhecido", v), [])
        self.assertEqual(f("ativo", ["ligar", "parar"]), ["parar"])
        self.assertEqual(f("parado", ["reiniciar"]), ["reiniciar"])
        self.assertEqual(f("ativo", []), [])

    def test_legado(self):
        m = {"servicos": [{"nome": "a.service", "ativo": True}, {"nome": "b.service", "ativo": False},
                          {"nome": "c", "erro": "n/d"}, "x"]}
        r = servicos.itens_de(m)
        self.assertEqual([(i["rotulo"], i["estado"]) for i in r],
                         [("a", "ativo"), ("b", "falha"), ("c", "desconhecido")])
        self.assertEqual(servicos.itens_de({}), [])

    def test_paginar(self):
        its = [item(id="h%d" % i, estado="ativo") for i in range(10)] + \
              [item(id="i%d" % i, grupo="incus", estado="ativo") for i in range(3)]
        pgs = servicos.paginar(its, 520)
        todos = [e for p in pgs for e in p if e[0] == "svc"]
        self.assertEqual([i for _, i in todos], list(range(13)))
        for p in pgs:
            h = sum(servicos.CAB_H if e[0] == "cab" else servicos.altura_linha(its[e[1]]) for e in p)
            self.assertLessEqual(h, 520)
            self.assertEqual(p[0][0], "cab")
            self.assertNotEqual(p[-1][0], "cab")
        self.assertEqual(servicos.paginar([], 500), [[]])

    def test_pagina_valida(self):
        for v, esperado in (("2", 2), ("0", 1), ("-3", 1), ("x", 1), (None, 1), ("99", 4), ("", 1)):
            self.assertEqual(servicos.pagina_valida(v, 4), esperado)


if __name__ == "__main__":
    unittest.main()
