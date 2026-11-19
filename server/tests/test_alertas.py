import unittest

import _caminho  # noqa: F401
import alertas

PAGINAS = ("resumo", "servicos", "aparelhos", "detalhes", "claude", "comandos")
SISTEMAS = ("atheron", "nas", "aparelhos", "servicos", "rotinas", "claude", "github", "ragnarok", "kindle")
GIB = 2 ** 30


def disco(pct, rotulo="/", caminho="/", livre_gib=None):
    d = {"rotulo": rotulo, "caminho": caminho, "pct": pct, "total_b": 100 * GIB, "usado_b": int(pct * GIB)}
    if livre_gib is not None:
        d["usado_b"] = int((100 - livre_gib) * GIB)
    return d


def item_svc(**k):
    d = {"id": "a", "rotulo": "ai-coder", "grupo": "host", "estado": "ativo", "detalhe": "", "verbos": [],
         "protegido": False, "opcional": False}
    d.update(k)
    return d


def textos(lista):
    return [a["texto"] for a in lista]


class LimiaresTest(unittest.TestCase):
    def test_none_e_tipos_errados_dao_padrao(self):
        for v in (None, [], "x", 3, True):
            self.assertEqual(alertas.limiares(v), alertas.PADRAO)

    def test_padrao_tem_valores_do_plano(self):
        self.assertEqual(alertas.PADRAO, {
            "disco_aviso": 85, "disco_critico": 93, "ram": 90, "swap": 50, "temp_cpu_c": 85, "kindle_bateria": 15,
            "s10_bateria": 20, "claude_limite": 90, "sessao_esperando_min": 10})

    def test_valor_valido_substitui(self):
        r = alertas.limiares({"ram": 80, "temp_cpu_c": 70, "sessao_esperando_min": 30})
        self.assertEqual((r["ram"], r["temp_cpu_c"], r["sessao_esperando_min"]), (80, 70, 30))
        self.assertEqual(r["swap"], 50)

    def test_valor_invalido_volta_ao_padrao_da_chave(self):
        for ruim in ("85", True, False, -1, 0, 500, None, [], {}, float("nan"), float("inf")):
            r = alertas.limiares({"ram": ruim, "disco_aviso": 70})
            self.assertEqual(r["ram"], 90, repr(ruim))
            self.assertEqual(r["disco_aviso"], 70)

    def test_faixas_proprias(self):
        self.assertEqual(alertas.limiares({"temp_cpu_c": 39})["temp_cpu_c"], 85)
        self.assertEqual(alertas.limiares({"temp_cpu_c": 40})["temp_cpu_c"], 40)
        self.assertEqual(alertas.limiares({"temp_cpu_c": 120})["temp_cpu_c"], 120)
        self.assertEqual(alertas.limiares({"temp_cpu_c": 121})["temp_cpu_c"], 85)
        self.assertEqual(alertas.limiares({"sessao_esperando_min": 1440})["sessao_esperando_min"], 1440)
        self.assertEqual(alertas.limiares({"sessao_esperando_min": 1441})["sessao_esperando_min"], 10)
        self.assertEqual(alertas.limiares({"ram": 1})["ram"], 1)
        self.assertEqual(alertas.limiares({"ram": 100})["ram"], 100)
        self.assertEqual(alertas.limiares({"ram": 101})["ram"], 90)

    def test_chave_desconhecida_ignorada(self):
        self.assertEqual(alertas.limiares({"foo": 1}), alertas.PADRAO)

    def test_nao_altera_padrao(self):
        r = alertas.limiares({"ram": 10})
        r["swap"] = 1
        self.assertEqual(alertas.PADRAO["swap"], 50)


class DiscoTest(unittest.TestCase):
    def test_disco_91_gera_aviso(self):
        a = alertas.avaliar({"discos": [disco(91, livre_gib=5.7)]})
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["nivel"], "aviso")
        self.assertIn("91%", a[0]["texto"])
        self.assertIn("5.7 GB", a[0]["texto"])
        self.assertEqual(a[0]["sistema"], "atheron")

    def test_limite_do_aviso(self):
        self.assertEqual(alertas.avaliar({"discos": [disco(85)]})[0]["nivel"], "aviso")
        self.assertEqual(alertas.avaliar({"discos": [disco(84.9)]}), [])

    def test_limite_do_critico(self):
        a = alertas.avaliar({"discos": [disco(93)]})
        self.assertEqual([x["nivel"] for x in a], ["critico"])
        self.assertEqual(alertas.avaliar({"discos": [disco(92.9)]})[0]["nivel"], "aviso")

    def test_so_a_raiz_conta_para_atheron(self):
        a = alertas.avaliar({"discos": [disco(90, "HD", "/srv/nas-hd"), disco(90, "SSD", "/var/x.json")]})
        self.assertEqual([x["sistema"] for x in a], ["nas", "nas"])

    def test_limiares_customizados(self):
        a = alertas.avaliar({"discos": [disco(60)]}, {"disco_aviso": 50, "disco_critico": 70})
        self.assertEqual(a[0]["nivel"], "aviso")

    def test_disco_com_erro_ou_sem_pct_e_ignorado(self):
        self.assertEqual(alertas.avaliar({"discos": [{"rotulo": "X", "erro": "n/d"}, {"pct": "x"}, 5, None]}), [])


class RecursosTest(unittest.TestCase):
    def test_ram(self):
        self.assertEqual(alertas.avaliar({"ram": {"pct": 89.9}}), [])
        a = alertas.avaliar({"ram": {"pct": 90}})
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "atheron"))
        self.assertIn("90%", a[0]["texto"])

    def test_swap(self):
        self.assertEqual(alertas.avaliar({"swap": {"pct": 49.9, "total_kb": 100}}), [])
        a = alertas.avaliar({"swap": {"pct": 50, "total_kb": 100}})
        self.assertEqual(a[0]["nivel"], "aviso")
        self.assertEqual(alertas.avaliar({"swap": {"pct": 100, "total_kb": 0}}), [])
        self.assertEqual(alertas.avaliar({"swap": {"pct": 100}}), [])

    def test_temperatura(self):
        self.assertEqual(alertas.avaliar({"temp_cpu": {"c": 84.9}}), [])
        a = alertas.avaliar({"temp_cpu": {"c": 85}})
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "atheron"))
        self.assertIn("85", a[0]["texto"])


class ServicosTest(unittest.TestCase):
    def sk(self, *itens, inv="ok"):
        return {"servicos_kindle": {"itens": list(itens), "inventario": inv, "idade_s": 1}}

    def test_falha_e_critico(self):
        a = alertas.avaliar(self.sk(item_svc(estado="falha")))
        self.assertEqual((a[0]["nivel"], a[0]["sistema"], a[0]["pagina"]), ("critico", "servicos", "servicos"))
        self.assertIn("ai-coder", a[0]["texto"])

    def test_parado_nao_opcional_e_aviso(self):
        a = alertas.avaliar(self.sk(item_svc(estado="parado")))
        self.assertEqual(a[0]["nivel"], "aviso")

    def test_parado_opcional_ativo_e_desconhecido_nao_alertam(self):
        self.assertEqual(alertas.avaliar(self.sk(
            item_svc(estado="parado", opcional=True), item_svc(estado="ativo"), item_svc(estado="desconhecido"))), [])

    def test_servicos_legados(self):
        a = alertas.avaliar({"servicos": [{"nome": "x.service", "ativo": False}, {"nome": "y.service", "ativo": True}]})
        self.assertEqual([x["nivel"] for x in a], ["critico"])

    def test_inventario_velho_ou_ausente(self):
        for inv in ("velho", "ausente"):
            a = alertas.avaliar(self.sk(inv=inv))
            self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "servicos"), inv)
        self.assertEqual(alertas.avaliar(self.sk(inv="ok")), [])


class RotinasTest(unittest.TestCase):
    def rot(self, itens=(), falhas=None):
        r = {"inventario": "ok", "itens": list(itens), "unidades_falhas": falhas or {"n": 0, "nomes": []}}
        return {"rotinas": r}

    def test_resultado_falha_e_critico(self):
        a = alertas.avaliar(self.rot([{"id": "s", "rotulo": "Backup senhas", "resultado": "falha"}]))
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("critico", "rotinas"))
        self.assertIn("Backup senhas", a[0]["texto"])

    def test_resultado_ok_e_desconhecido_nao_alertam(self):
        self.assertEqual(alertas.avaliar(self.rot([{"rotulo": "A", "resultado": "ok"},
                                                   {"rotulo": "B", "resultado": "desconhecido"}])), [])

    def test_atrasada_e_aviso(self):
        a = alertas.avaliar(self.rot([{"rotulo": "Tokens", "resultado": "ok", "atrasada": True}]))
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "rotinas"))
        self.assertEqual(alertas.avaliar(self.rot([{"rotulo": "T", "resultado": "ok", "atrasada": False}])), [])

    def test_unidades_falhas_um_alerta_com_ate_2_nomes(self):
        a = alertas.avaliar(self.rot(falhas={"n": 4, "nomes": ["a.service", "b.service", "c.service", "d.service"]}))
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]["nivel"], "critico")
        self.assertIn("a.service", a[0]["texto"])
        self.assertIn("b.service", a[0]["texto"])
        self.assertNotIn("c.service", a[0]["texto"])
        self.assertIn("4", a[0]["texto"])

    def test_unidades_falhas_zero(self):
        self.assertEqual(alertas.avaliar(self.rot(falhas={"n": 0, "nomes": ["x"]})), [])

    def test_unidades_falhas_sem_nomes(self):
        a = alertas.avaliar(self.rot(falhas={"n": 1}))
        self.assertEqual(a[0]["nivel"], "critico")


class AparelhosTest(unittest.TestCase):
    def ap(self, **k):
        d = {"id": "gw", "rotulo": "Gateway", "online": False, "offline_min": 10, "alerta_offline_min": 10}
        d.update(k)
        return {"aparelhos": {"inventario": "ok", "itens": [d]}}

    def test_offline_no_limite_e_critico(self):
        a = alertas.avaliar(self.ap())
        self.assertEqual((a[0]["nivel"], a[0]["sistema"], a[0]["pagina"]), ("critico", "aparelhos", "aparelhos"))
        self.assertIn("Gateway", a[0]["texto"])

    def test_um_abaixo_nao_alerta(self):
        self.assertEqual(alertas.avaliar(self.ap(offline_min=9)), [])

    def test_sem_alerta_offline_min_ou_sem_offline_min(self):
        self.assertEqual(alertas.avaliar(self.ap(alerta_offline_min=None, offline_min=999)), [])
        self.assertEqual(alertas.avaliar(self.ap(offline_min=None)), [])


class ClaudeTest(unittest.TestCase):
    def lim(self, c=10, s=10, renovado=False):
        j = lambda p: {"pct": p, "volta_em": 1, "renovado": renovado}
        return {"claude": {"limites": {"cinco_horas": j(c), "semanal": j(s), "idade_s": 5, "velho": False}}}

    def test_cinco_horas_e_semanal(self):
        a = alertas.avaliar(self.lim(c=90))
        self.assertEqual((a[0]["nivel"], a[0]["sistema"], a[0]["pagina"]), ("aviso", "claude", "claude"))
        self.assertIn("5h", a[0]["texto"])
        b = alertas.avaliar(self.lim(s=95))
        self.assertIn("semanal", b[0]["texto"])
        self.assertEqual(alertas.avaliar(self.lim(c=89.9, s=89.9)), [])

    def test_renovado_nao_alerta(self):
        self.assertEqual(alertas.avaliar(self.lim(c=99, s=99, renovado=True)), [])

    def test_janela_ausente_ou_erro(self):
        self.assertEqual(alertas.avaliar({"claude": {"limites": {"erro": "n/d"}}}), [])
        self.assertEqual(alertas.avaliar({"claude": {"limites": {"cinco_horas": None, "semanal": None}}}), [])

    def sessao(self, estado="esperando", desde_s=600):
        return {"claude": {"sessoes": {"itens": [{"projeto": "kindle-monitor", "estado": estado, "desde_s": desde_s}]}}}

    def test_sessao_esperando_e_leve(self):
        a = alertas.avaliar(self.sessao())
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("leve", "claude"))
        self.assertIn("kindle-monitor", a[0]["texto"])
        self.assertEqual(alertas.avaliar(self.sessao(desde_s=599)), [])
        self.assertEqual(alertas.avaliar(self.sessao(estado="trabalhando", desde_s=9999)), [])
        self.assertEqual(alertas.avaliar(self.sessao(desde_s=599), {"sessao_esperando_min": 5})[0]["nivel"], "leve")


class GithubRagnarokTest(unittest.TestCase):
    def test_ci_falha_e_aviso(self):
        m = {"github": {"prs": [], "ci": [{"repo": "kindle-monitor", "branch": "master", "estado": "falha"},
                                           {"repo": "b", "branch": "master", "estado": "ok"},
                                           {"repo": "c", "branch": "master", "estado": "pendente"}],
                        "velho": False}}
        a = alertas.avaliar(m)
        self.assertEqual(len(a), 1)
        self.assertEqual((a[0]["nivel"], a[0]["sistema"], a[0]["pagina"]), ("aviso", "github", "claude"))
        self.assertIn("kindle-monitor", a[0]["texto"])

    def test_porta_fechada_e_aviso(self):
        m = {"portas": [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "MAP", "aberto": False}]}
        a = alertas.avaliar(m)
        self.assertEqual(len(a), 1)
        self.assertEqual((a[0]["nivel"], a[0]["sistema"], a[0]["pagina"]), ("aviso", "ragnarok", "servicos"))
        self.assertIn("MAP", a[0]["texto"])

    def test_portas_com_erro(self):
        self.assertEqual(alertas.avaliar({"portas": {"erro": "n/d"}}), [])


class BateriasTest(unittest.TestCase):
    def test_kindle(self):
        a = alertas.avaliar({}, kv={"bateria": 15, "carregando": False})
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "kindle"))
        self.assertIn("15%", a[0]["texto"])
        self.assertEqual(alertas.avaliar({}, kv={"bateria": 16, "carregando": False}), [])
        self.assertEqual(alertas.avaliar({}, kv={"bateria": 5, "carregando": True}), [])
        self.assertEqual(alertas.avaliar({}, kv={"bateria": None}), [])
        self.assertEqual(alertas.avaliar({}, kv={}), [])

    def test_kindle_limiar_customizado(self):
        self.assertEqual(len(alertas.avaliar({}, {"kindle_bateria": 30}, {"bateria": 30})), 1)

    def s10(self, nivel, status="discharging"):
        return {"s10": {"bateria": {"nivel": nivel, "status": status}, "caminhos": {}, "avisos": [], "velho": False}}

    def test_s10(self):
        a = alertas.avaliar(self.s10(20))
        self.assertEqual((a[0]["nivel"], a[0]["sistema"]), ("aviso", "aparelhos"))
        self.assertIn("20%", a[0]["texto"])
        self.assertEqual(len(alertas.avaliar(self.s10(10, "not_charging"))), 1)
        self.assertEqual(alertas.avaliar(self.s10(21)), [])
        self.assertEqual(alertas.avaliar(self.s10(5, "charging")), [])
        self.assertEqual(alertas.avaliar(self.s10(5, "full")), [])
        self.assertEqual(alertas.avaliar({"s10": {"bateria": None}}), [])


class FonteVelhaTest(unittest.TestCase):
    def test_claude_limites_tokens_s10_github(self):
        m = {"claude": {"limites": {"velho": True, "idade_s": 1200}, "tokens": {"velho": True, "idade_s": 3600}},
             "s10": {"velho": True, "idade_s": 300}, "github": {"velho": True, "idade_s": 7200}}
        a = alertas.avaliar(m)
        self.assertEqual([x["sistema"] for x in a], ["claude", "claude", "aparelhos", "github"])
        self.assertTrue(all(x["nivel"] == "aviso" for x in a))
        self.assertEqual(a[0]["texto"], "Limites do Claude sem atualizar ha 20 min")
        self.assertEqual(a[1]["texto"], "Tokens do Claude sem atualizar ha 60 min")
        self.assertEqual(a[2]["texto"], "S10 sem atualizar ha 5 min")
        self.assertEqual(a[3]["texto"], "GitHub sem atualizar ha 120 min")

    def test_aparelhos_e_rotinas_inventario_velho(self):
        m = {"aparelhos": {"inventario": "velho", "itens": [], "idade_s": 600},
             "rotinas": {"inventario": "velho", "itens": [], "unidades_falhas": {"n": 0, "nomes": []}}}
        a = alertas.avaliar(m)
        self.assertEqual([x["sistema"] for x in a], ["aparelhos", "rotinas"])
        self.assertEqual(a[0]["texto"], "Aparelhos sem atualizar ha 10 min")
        self.assertEqual(a[1]["texto"], "Rotinas sem atualizar")  # sem idade_s
        self.assertTrue(all(x["texto"].isascii() and len(x["texto"]) <= 48 for x in a))

    def test_ausente_nao_conta_como_velha_e_velho_false_nao_alerta(self):
        m = {"aparelhos": {"inventario": "ausente", "itens": []}, "claude": {"limites": {"velho": False}},
             "github": {"velho": "sim"}}
        self.assertEqual(alertas.avaliar(m), [])

    def test_sem_idade_ainda_gera_alerta(self):
        a = alertas.avaliar({"github": {"velho": True}})
        self.assertEqual(len(a), 1)
        self.assertLessEqual(len(a[0]["texto"]), 48)


class OrdemTest(unittest.TestCase):
    def test_critico_aviso_leve_e_ordem_das_regras(self):
        m = {"discos": [disco(90, "HD", "/srv/hd"), disco(95)],
             "ram": {"pct": 95},
             "servicos_kindle": {"itens": [item_svc(estado="falha")], "inventario": "ok"},
             "claude": {"sessoes": {"itens": [{"projeto": "p", "estado": "esperando", "desde_s": 9999}]}},
             "temp_cpu": {"c": 90}}
        a = alertas.avaliar(m)
        self.assertEqual([x["nivel"] for x in a], ["critico", "critico", "aviso", "aviso", "aviso", "leve"])
        self.assertEqual([x["sistema"] for x in a],
                         ["atheron", "servicos", "nas", "atheron", "atheron", "claude"])
        self.assertIn("RAM", a[3]["texto"])
        self.assertIn("CPU", a[4]["texto"])

    def test_estavel(self):
        m = {"portas": [{"rotulo": "A", "aberto": False}, {"rotulo": "B", "aberto": False}]}
        self.assertEqual(textos(alertas.avaliar(m)), ["Porta A fechada", "Porta B fechada"])


class RobustezTest(unittest.TestCase):
    def test_m_nao_dict(self):
        for v in (None, [], "x", 3, True):
            self.assertEqual(alertas.avaliar(v), [])

    def test_lim_e_kv_malformados(self):
        for lim in (None, [], "x", {"ram": "x"}, 5):
            for kv in (None, [], "x", {"bateria": "x"}, {"bateria": True}, 5):
                self.assertEqual(alertas.avaliar({}, lim, kv), [])

    def test_tipos_errados_em_cada_chave(self):
        chaves = ("discos", "ram", "swap", "temp_cpu", "servicos_kindle", "servicos", "claude", "s10", "portas",
                  "ragnarok", "aparelhos", "rotinas", "github", "limiares")
        lixos = (None, 1, True, "x", [], [1, None, "a"], {}, {"a": 1}, float("nan"), [[]], {"itens": 5},
                 {"itens": [None, 1, "x", []]}, {"pct": "x"}, {"pct": None}, {"c": "x"}, {"c": None},
                 {"limites": 1, "tokens": [], "sessoes": "x"}, {"limites": {"cinco_horas": "x", "semanal": 5}},
                 {"sessoes": {"itens": [1, {"estado": "esperando"}]}}, {"bateria": "x"}, {"bateria": {"nivel": "x"}},
                 {"unidades_falhas": 3, "itens": 4}, {"unidades_falhas": {"n": "x", "nomes": 5}},
                 {"itens": [{"resultado": "falha", "rotulo": 5}, {"online": False, "alerta_offline_min": "x"}]},
                 {"ci": [1, {"estado": "falha"}], "prs": 3})
        for ch in chaves:
            for lixo in lixos:
                r = alertas.avaliar({ch: lixo})
                self.assertIsInstance(r, list, "%s=%r" % (ch, lixo))

    def test_tudo_malformado_junto(self):
        m = {k: "x" for k in ("discos", "ram", "swap", "temp_cpu", "servicos_kindle", "claude", "s10", "portas",
                              "aparelhos", "rotinas", "github")}
        self.assertEqual(alertas.avaliar(m, "x", "y"), [])

    def test_servico_sem_campos(self):
        a = alertas.avaliar({"servicos_kindle": {"itens": [{"estado": "falha"}]}})
        self.assertEqual(a[0]["nivel"], "critico")


class TextoTest(unittest.TestCase):
    def conferir(self, lista):
        for a in lista:
            self.assertEqual(set(a), {"nivel", "texto", "pagina", "sistema"})
            self.assertIn(a["nivel"], ("critico", "aviso", "leve"))
            self.assertTrue(a["texto"].isascii(), a["texto"])
            self.assertTrue(a["texto"].isprintable(), repr(a["texto"]))
            self.assertTrue(0 < len(a["texto"]) <= 48, a["texto"])
            self.assertIn(a["pagina"], PAGINAS)
            self.assertIn(a["sistema"], SISTEMAS)

    def test_rotulo_de_300_caracteres_com_acento(self):
        r = "Ação ú" * 60 + "‮\x00\n"
        m = {"discos": [disco(99, r, "/x")],
             "servicos_kindle": {"itens": [item_svc(rotulo=r, estado="falha"), item_svc(rotulo=r, estado="parado")],
                                 "inventario": "velho"},
             "rotinas": {"inventario": "velho", "itens": [{"rotulo": r, "resultado": "falha"},
                                                          {"rotulo": r, "atrasada": True}],
                         "unidades_falhas": {"n": 3, "nomes": [r, r, r]}},
             "aparelhos": {"itens": [{"rotulo": r, "offline_min": 99999, "alerta_offline_min": 1}]},
             "portas": [{"rotulo": r, "aberto": False}],
             "github": {"ci": [{"repo": r, "estado": "falha"}], "velho": True},
             "claude": {"sessoes": {"itens": [{"projeto": r, "estado": "esperando", "desde_s": 10 ** 9}]},
                        "limites": {"cinco_horas": {"pct": 100}, "velho": True}},
             "s10": {"bateria": {"nivel": 1, "status": "discharging"}, "velho": True},
             "ram": {"pct": 100}, "swap": {"pct": 100, "total_kb": 1}, "temp_cpu": {"c": 119}}
        a = alertas.avaliar(m, kv={"bateria": 1})
        self.assertGreater(len(a), 15)
        self.conferir(a)

    def test_numeros_enormes_ou_nao_finitos(self):
        m = {"discos": [disco(10 ** 300)], "ram": {"pct": float("inf")}, "temp_cpu": {"c": 10 ** 30},
             "aparelhos": {"itens": [{"rotulo": "x", "offline_min": 10 ** 40, "alerta_offline_min": 1}]}}
        self.conferir(alertas.avaliar(m))

    def test_conferir_exemplo_completo(self):
        self.conferir(alertas.avaliar({"discos": [disco(91, livre_gib=5.7)], "ram": {"pct": 91}}))


if __name__ == "__main__":
    unittest.main()
