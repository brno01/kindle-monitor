"""Painel de jogos, lado web: montar_amp (jogos.json do executor), integracao com o Coletor e regras de alerta."""
import json
import unittest

import _caminho  # noqa: F401
import alertas
import coletores
import ecossistema as eco

AGORA = 1_700_000_000.0
CAM = "/run/kindle-monitor/status/jogos.json"
AMP_CFG = {"url": "http://10.0.0.60:8080", "credenciais": "/etc/kindle-monitor/amp.cred"}


def inst(i="a1b2c3d4", nome="Minecraft", modulo="Minecraft", estado="rodando", jogadores=2, maximo=20, **extra):
    d = {"id": i, "nome": nome, "modulo": modulo, "estado": estado, "jogadores": jogadores, "max": maximo}
    d.update(extra)
    return d


def doc(gerado=AGORA - 5, ativo=True, erro=None, instancias=None, **extra):
    d = {"versao": 1, "gerado": gerado, "ativo": ativo, "erro": erro,
         "instancias": [inst()] if instancias is None else instancias}
    d.update(extra)
    return json.dumps(d)


class MontarAmpTest(unittest.TestCase):
    def test_ok(self):
        r = eco.montar_amp(doc(), AGORA)
        self.assertEqual((r["ativo"], r["inventario"], r["idade_s"], r["erro"]), (True, "ok", 5, None))
        self.assertEqual(r["instancias"], [inst()])

    def test_ausente_e_ilegivel(self):
        for texto in (None, "", "{", "[]", "3", "null", '"x"'):
            with self.subTest(texto=texto):
                r = eco.montar_amp(texto, AGORA)
                self.assertEqual((r["ativo"], r["inventario"], r["idade_s"], r["instancias"]), (None, "ausente", None, []))

    def test_versao_e_tipos_dos_campos_de_topo(self):
        base = json.loads(doc())
        for k, v in (("versao", 2), ("versao", "1"), ("versao", None), ("versao", True), ("gerado", "x"), ("gerado", None),
                     ("gerado", True), ("gerado", float("nan")), ("ativo", "sim"), ("ativo", 1), ("ativo", None),
                     ("instancias", {}), ("instancias", None), ("instancias", "x"), ("erro", 5), ("erro", [])):
            d = dict(base)
            d[k] = v
            with self.subTest(campo=k, valor=v):
                r = eco.montar_amp(json.dumps(d), AGORA)
                self.assertEqual((r["inventario"], r["ativo"], r["instancias"]), ("ausente", None, []))

    def test_campo_ausente(self):
        for k in ("versao", "gerado", "ativo", "erro", "instancias"):
            d = json.loads(doc())
            del d[k]
            with self.subTest(campo=k):
                self.assertEqual(eco.montar_amp(json.dumps(d), AGORA)["inventario"], "ausente")

    def test_idade_limites(self):
        self.assertEqual(eco.montar_amp(doc(gerado=AGORA - 60), AGORA)["inventario"], "ok")
        r = eco.montar_amp(doc(gerado=AGORA - 61), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"], r["instancias"]), ("velho", 61, []))
        self.assertTrue(r["ativo"])  # o `ativo` do arquivo velho continua valendo (quem decide o alerta)
        self.assertEqual(eco.montar_amp(doc(gerado=AGORA + 3), AGORA)["inventario"], "ok")

    def test_relogio_adiantado(self):
        r = eco.montar_amp(doc(gerado=AGORA + 300), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"], r.get("relogio_adiantado")), ("velho", 300, True))
        self.assertNotIn("relogio_adiantado", eco.montar_amp(doc(gerado=AGORA - 120), AGORA))

    def test_erro_nao_vazio_ignora_as_instancias(self):
        r = eco.montar_amp(doc(erro="amp sem resposta"), AGORA)
        self.assertEqual((r["inventario"], r["erro"], r["instancias"]), ("ok", "amp sem resposta", []))
        for vazio in (None, "", "   "):
            self.assertIsNone(eco.montar_amp(doc(erro=vazio), AGORA)["erro"])
            self.assertEqual(len(eco.montar_amp(doc(erro=vazio), AGORA)["instancias"]), 1)

    def test_erro_e_saneado(self):
        r = eco.montar_amp(doc(erro="amp é \x1b[31m" + "x" * 100), AGORA)
        self.assertTrue(r["erro"].isascii() and r["erro"].isprintable())
        self.assertLessEqual(len(r["erro"]), 40)

    def test_desligado(self):
        r = eco.montar_amp(doc(ativo=False, instancias=[]), AGORA)
        self.assertEqual((r["ativo"], r["inventario"], r["erro"], r["instancias"]), (False, "ok", None, []))

    def test_texto_das_instancias_e_saneado(self):
        r = eco.montar_amp(doc(instancias=[inst(nome="Zé \x1b[31m☃ " + "n" * 40, modulo="Módulo " + "m" * 30)]),
                             AGORA)
        i = r["instancias"][0]
        self.assertTrue(i["nome"].isascii() and i["nome"].isprintable() and len(i["nome"]) <= 24)
        self.assertTrue(i["modulo"].isascii() and i["modulo"].isprintable() and len(i["modulo"]) <= 16)
        self.assertTrue(i["nome"].startswith("Ze"))

    def test_nome_vazio_vira_interrogacao(self):
        self.assertEqual(eco.montar_amp(doc(instancias=[inst(nome="☃")]), AGORA)["instancias"][0]["nome"], "?")
        self.assertEqual(eco.montar_amp(doc(instancias=[inst(nome=5)]), AGORA)["instancias"][0]["nome"], "?")

    def test_estado_desconhecido_vira_outro(self):
        for e in ("RUNNING", 5, None, "", "rodando "):
            self.assertEqual(eco.montar_amp(doc(instancias=[inst(estado=e, jogadores=None, maximo=None)]),
                                            AGORA)["instancias"][0]["estado"], "outro")
        for e in ("rodando", "parado", "iniciando", "falha", "outro"):
            self.assertEqual(eco.montar_amp(doc(instancias=[inst(estado=e)]), AGORA)["instancias"][0]["estado"], e)

    def test_contagens(self):
        casos = [((3, 20), (3, 20)), ((0, 0), (0, 0)), ((3, None), (3, None)), ((None, 20), (None, None)),
                 ((True, 20), (None, None)), (("3", "20"), (None, None)), ((-1, 20), (None, None)),
                 ((3, -5), (3, None)), ((10 ** 6, 5), (None, None)), ((3, 10 ** 6), (3, None)),
                 ((3.0, 20.0), (3, 20)), ((3.5, 20), (None, None)), ((float("nan"), 1), (None, None))]
        for (j, m), (ej, em) in casos:
            with self.subTest(j=j, m=m):  # json.dumps escreve NaN e o loads le de volta
                i = eco.montar_amp(doc(instancias=[inst(jogadores=j, maximo=m)]), AGORA)["instancias"][0]
                self.assertEqual((i["jogadores"], i["max"]), (ej, em))

    def test_so_rodando_tem_contagem(self):
        i = eco.montar_amp(doc(instancias=[inst(estado="parado", jogadores=4, maximo=20)]), AGORA)["instancias"][0]
        self.assertEqual((i["jogadores"], i["max"]), (None, None))

    def test_id_invalido_ou_repetido_e_descartado(self):
        r = eco.montar_amp(doc(instancias=[inst(i="a1b2c3d4"), inst(i="a1b2c3d4", nome="Copia"), inst(i="XYZ"),
                                          inst(i="a1b2c3d4e"), inst(i=5), inst(i=""), inst(i="B1B2C3D4"),
                                          inst(i="a1b2c3d4\n"), inst(i="00000001", nome="Valheim")]), AGORA)
        self.assertEqual([i["id"] for i in r["instancias"]], ["a1b2c3d4", "00000001"])

    def test_itens_que_nao_sao_objetos_somem(self):
        r = eco.montar_amp(doc(instancias=["x", 3, None, [], inst()]), AGORA)
        self.assertEqual(len(r["instancias"]), 1)

    def test_maximo_16(self):
        r = eco.montar_amp(doc(instancias=[inst(i="%08x" % n, nome="S%02d" % n) for n in range(20)]), AGORA)
        self.assertEqual(len(r["instancias"]), 16)

    def test_ligadas_primeiro_depois_por_nome(self):
        r = eco.montar_amp(doc(instancias=[inst(i="00000001", nome="Zeta", estado="parado", jogadores=None, maximo=None),
                                          inst(i="00000002", nome="beta"), inst(i="00000003", nome="Alfa"),
                                          inst(i="00000004", nome="Gama", estado="iniciando", jogadores=None,
                                               maximo=None)]), AGORA)
        self.assertEqual([i["nome"] for i in r["instancias"]], ["Alfa", "beta", "Gama", "Zeta"])

    def test_chave_extra_na_instancia_nao_vaza(self):
        r = eco.montar_amp(doc(instancias=[inst(senha="x", ip="1.2.3.4")]), AGORA)
        self.assertEqual(set(r["instancias"][0]), {"id", "nome", "modulo", "estado", "jogadores", "max"})

    def test_aninhamento_profundo_nao_levanta(self):
        r = eco.montar_amp("[" * 5000, AGORA)
        self.assertEqual(r["inventario"], "ausente")
        r = eco.montar_amp(doc(instancias=[inst(nome=[[[[]]]])]), AGORA)
        self.assertEqual(r["instancias"][0]["nome"], "?")

    def test_agora_ruim_nao_levanta(self):
        self.assertEqual(eco.montar_amp(doc(), None)["inventario"], "ausente")
        self.assertEqual(eco.montar_amp(doc(), "x")["inventario"], "ausente")


class ColetorAmpTest(unittest.TestCase):
    def coletor(self, cfg, arquivos):
        def ler(caminho):
            if caminho in arquivos:
                return arquivos[caminho]
            raise OSError("nao existe")
        cfg = dict({"host": "t", "comandos": {"estado": "/run/kindle-monitor/status"}}, **cfg)
        return coletores.Coletor(cfg, leitor_arquivo=ler, executar=lambda *a, **k: "", agora=lambda: AGORA,
                                 buscar=lambda *a, **k: "")

    def test_sem_a_chave_amp_nada_aparece_mesmo_com_o_arquivo(self):
        for cfg in ({}, {"amp": None}, {"amp": {"url": "http://127.0.0.1:1", "credenciais": "/etc/passwd"}},
                    {"amp": "x"}, {"amp": []}):
            with self.subTest(cfg=cfg):
                m = self.coletor(cfg, {CAM: doc()}).coletar()
                self.assertNotIn("amp", m)

    def test_le_o_caminho_padrao(self):
        m = self.coletor({"amp": AMP_CFG}, {CAM: doc()}).coletar()
        self.assertEqual((m["amp"]["inventario"], m["amp"]["ativo"], len(m["amp"]["instancias"])), ("ok", True, 1))

    def test_diretorio_de_estado_da_config(self):
        c = self.coletor({"amp": AMP_CFG, "comandos": {"estado": "/x"}}, {"/x/jogos.json": doc()})
        self.assertEqual(c.coletar()["amp"]["inventario"], "ok")

    def test_arquivo_ausente_e_leitor_que_levanta(self):
        m = self.coletor({"amp": AMP_CFG}, {}).coletar()
        self.assertEqual((m["amp"]["inventario"], m["amp"]["ativo"]), ("ausente", None))

    def test_metricas_json_nao_leva_credencial_nem_url(self):
        m = self.coletor({"amp": AMP_CFG}, {CAM: doc()}).coletar()
        txt = json.dumps(m)
        self.assertNotIn("amp.cred", txt)
        self.assertNotIn("10.0.0.60", txt)


def alertas_amp(amp, **extra):
    m = {"amp": amp}
    m.update(extra)
    return [(a["nivel"], a["texto"], a["sistema"], a["pagina"]) for a in alertas.avaliar(m)]


def bloco(texto, agora=AGORA):
    return eco.montar_amp(texto, agora)


class AlertasAmpTest(unittest.TestCase):
    def test_instancia_parada_ou_falha_nao_alerta(self):
        b = bloco(doc(instancias=[inst(estado="parado", jogadores=None, maximo=None),
                                  inst(i="00000002", estado="falha", jogadores=None, maximo=None)]))
        self.assertEqual(alertas_amp(b), [])

    def test_erro_com_feature_ativa_e_alerta_leve(self):
        self.assertEqual(alertas_amp(bloco(doc(erro="amp login falhou"))),
                         [("leve", "AMP sem dados", "amp", "jogos")])

    def test_feature_desligada_nao_alerta(self):
        self.assertEqual(alertas_amp(bloco(doc(ativo=False, instancias=[]))), [])
        self.assertEqual(alertas_amp(bloco(doc(ativo=False, instancias=[], erro="x"))), [])

    def test_arquivo_ausente_nao_alerta(self):
        self.assertEqual(alertas_amp(bloco(None)), [])

    def test_velho_com_feature_ativa_avisa_uma_vez(self):
        b = bloco(doc(gerado=AGORA - 300))
        self.assertEqual(alertas_amp(b), [("aviso", "AMP sem atualizar ha 5 min", "amp", "jogos")])

    def test_velho_com_feature_desligada_nao_alerta(self):
        self.assertEqual(alertas_amp(bloco(doc(gerado=AGORA - 300, ativo=False, instancias=[]))), [])

    def test_relogio_adiantado(self):
        r = alertas_amp(bloco(doc(gerado=AGORA + 300)))
        self.assertEqual(r, [("aviso", "AMP sem atualizar com relogio adiantado", "amp", "jogos")])

    def test_velho_junto_de_outro_inventario_vira_aviso_unico(self):
        sk = {"inventario": "velho", "idade_s": 120, "itens": []}
        r = alertas_amp(bloco(doc(gerado=AGORA - 300)), servicos_kindle=sk)
        self.assertEqual([x for x in r if "sem atualizar" in x[1]], [("aviso", "Inventario root sem atualizar ha 5 min",
                                                                     "servicos", "servicos")])
        self.assertFalse([x for x in r if "AMP" in x[1]])

    def test_amp_velho_desligado_nao_conta_para_o_aviso_unico(self):
        sk = {"inventario": "velho", "idade_s": 120, "itens": []}
        r = alertas_amp(bloco(doc(gerado=AGORA - 300, ativo=False, instancias=[])), servicos_kindle=sk)
        self.assertEqual(r, [("aviso", "Inventario de servicos velho", "servicos", "servicos")])

    def test_erro_nao_duplica_com_inventario_velho(self):
        # velho = a causa e o executor parado; o texto de erro de um arquivo velho nao vira "AMP sem dados"
        r = alertas_amp(bloco(doc(gerado=AGORA - 300, erro="amp sem resposta")))
        self.assertEqual([x[1] for x in r], ["AMP sem atualizar ha 5 min"])

    def test_porta_do_ragnarok_fechada_continua_aviso_agora_na_pagina_jogos(self):
        r = alertas.avaliar({"portas": [{"rotulo": "MAP", "aberto": False}]})
        self.assertEqual([(a["nivel"], a["texto"], a["sistema"], a["pagina"]) for a in r],
                         [("aviso", "Porta MAP fechada", "jogos", "jogos")])


if __name__ == "__main__":
    unittest.main()
