"""Aparelhos e rotinas: validacao E8, montagem a partir do inventario root, integracao com Coletor e alertas."""
import json
import unittest

import _caminho  # noqa: F401
import alertas
import coletores
import ecossistema as eco

AGORA = 1_700_000_000.0


def textos_de(lista):
    itens = lista["itens"] if isinstance(lista, dict) else lista
    return [a["texto"] for a in itens]


def aparelho(**kw):
    d = {"id": "gw", "nome": "cerberus-gw", "rotulo": "Gateway", "icone": "rede", "alerta_offline_min": 10}
    d.update(kw)
    return d


def rotina(**kw):
    d = {"id": "senhas", "rotulo": "Backup senhas", "tipo": "timer",
         "alvo": "cerberus-vault-backup.service", "max_idade_h": 26}
    d.update(kw)
    return d


class ValidarAparelhosTest(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(eco.validar_aparelhos([aparelho()]), [aparelho()])

    def test_alerta_opcional(self):
        a = aparelho()
        del a["alerta_offline_min"]
        self.assertEqual(eco.validar_aparelhos([a]), [a])

    def test_invalidos_descartam_a_lista(self):
        ruins = [aparelho(id="Gw"), aparelho(id=""), aparelho(id="a" * 25), aparelho(id=3),
                 aparelho(nome="CERB"), aparelho(nome="empresa-x-x"), aparelho(nome="a" * 64), aparelho(nome=None),
                 aparelho(rotulo=""), aparelho(rotulo="x" * 17), aparelho(rotulo="Gatewayé"), aparelho(rotulo=5),
                 aparelho(icone="nao-existe"), aparelho(icone=None),
                 aparelho(alerta_offline_min=0), aparelho(alerta_offline_min=10081),
                 aparelho(alerta_offline_min=True), aparelho(alerta_offline_min=5.5),
                 aparelho(alerta_offline_min="10"), "texto", None, 3, []]
        for r in ruins:
            with self.subTest(r=r):
                lista = [aparelho(), r] if r != [] else [aparelho(), []]
                self.assertEqual(eco.validar_aparelhos(lista), [])

    def test_tipos_e_tamanho(self):
        for v in (None, "x", {}, 5):
            self.assertEqual(eco.validar_aparelhos(v), [])
        cheio = [aparelho(id="a%d" % i, nome="n%d" % i) for i in range(16)]
        self.assertEqual(len(eco.validar_aparelhos(cheio)), 16)
        self.assertEqual(eco.validar_aparelhos(cheio + [aparelho(id="z", nome="z")]), [])

    def test_chave_desconhecida_descarta_a_lista(self):
        for extra in ({"extra": 1}, {"extra": None}, {"Id": "x"}):
            with self.subTest(extra=extra):
                self.assertEqual(eco.validar_aparelhos([aparelho(**extra)]), [])

    def test_id_ou_nome_repetido_descarta_a_lista(self):
        self.assertEqual(eco.validar_aparelhos([aparelho(), aparelho(nome="outro")]), [])
        self.assertEqual(eco.validar_aparelhos([aparelho(), aparelho(id="outro")]), [])
        distintos = [aparelho(), aparelho(id="outro", nome="outro")]
        self.assertEqual(eco.validar_aparelhos(distintos), distintos)

    def test_alerta_nulo_e_recusado_como_no_executor(self):
        self.assertEqual(eco.validar_aparelhos([aparelho(alerta_offline_min=None)]), [])


class ValidarRotinasTest(unittest.TestCase):
    def test_validos(self):
        arq = rotina(id="painel", tipo="arquivo", alvo="/var/lib/painel/tokens.json", max_idade_h=1)
        self.assertEqual(eco.validar_rotinas([rotina(), arq]), [rotina(), arq])
        for alvo in ("/srv/x", "/var/backups/a/b"):
            self.assertEqual(len(eco.validar_rotinas([rotina(tipo="arquivo", alvo=alvo)])), 1)

    def test_invalidos(self):
        ruins = [rotina(id="X"), rotina(rotulo=""), rotina(rotulo="x" * 21), rotina(rotulo="café"),
                 rotina(tipo="outro"), rotina(tipo=None),
                 rotina(alvo="x.timer"), rotina(alvo="a b.service"), rotina(alvo=None), rotina(alvo=".service"),
                 rotina(tipo="arquivo", alvo="relativo/x"), rotina(tipo="arquivo", alvo="/etc/passwd"),
                 rotina(tipo="arquivo", alvo="/var/lib/../etc/x"), rotina(tipo="arquivo", alvo="/var/lib//x"),
                 rotina(tipo="arquivo", alvo="/var/lib/x/"), rotina(tipo="arquivo", alvo="/var/libx/a"),
                 rotina(tipo="arquivo", alvo="/var/lib/claude-uso"),
                 rotina(tipo="arquivo", alvo="/var/lib/claude-uso/tokens.json"),
                 rotina(max_idade_h=0.05), rotina(max_idade_h=721), rotina(max_idade_h=True),
                 rotina(max_idade_h="26"), rotina(max_idade_h=None), rotina(max_idade_h=float("nan")),
                 "x", None]
        for r in ruins:
            with self.subTest(r=r):
                self.assertEqual(eco.validar_rotinas([rotina(), r]), [])

    def test_limites_de_idade(self):
        for v in (0.1, 720, 1.5):
            self.assertEqual(len(eco.validar_rotinas([rotina(max_idade_h=v)])), 1)

    def test_tipos_e_tamanho(self):
        for v in (None, "x", {}, 5):
            self.assertEqual(eco.validar_rotinas(v), [])
        self.assertEqual(eco.validar_rotinas([rotina(id="a%d" % i) for i in range(17)]), [])

    def test_chave_desconhecida_descarta_a_lista(self):
        for extra in ({"extra": 1}, {"extra": None}, {"nome": "x"}):
            with self.subTest(extra=extra):
                self.assertEqual(eco.validar_rotinas([rotina(**extra)]), [])

    def test_id_repetido_descarta_a_lista(self):
        self.assertEqual(eco.validar_rotinas([rotina(), rotina(alvo="outro.service")]), [])
        distintas = [rotina(), rotina(id="outra")]
        self.assertEqual(eco.validar_rotinas(distintas), distintas)


def ap_doc(gerado=AGORA - 5, aparelhos=None):
    if aparelhos is None:
        aparelhos = {"gw": {"online": False, "visto_em": int(AGORA - 15 * 60), "conexao": None}}
    return json.dumps({"versao": 1, "gerado": gerado, "erro": None, "aparelhos": aparelhos})


def ro_doc(gerado=AGORA - 5, rotinas=None, falhas=None):
    if rotinas is None:
        rotinas = {"senhas": {"resultado": "ok", "ultima_em": int(AGORA - 3600), "detalhe": ""}}
    return json.dumps({"versao": 1, "gerado": gerado, "rotinas": rotinas,
                       "unidades_falhas": falhas if falhas is not None else {"n": 0, "nomes": []}})


CAT_A = eco.validar_aparelhos([aparelho(), {"id": "s10", "nome": "s10", "rotulo": "Galaxy S10", "icone": "celular"}])
CAT_R = eco.validar_rotinas([rotina()])


class MontarAparelhosTest(unittest.TestCase):
    def test_offline_calcula_minutos(self):
        r = eco.montar_aparelhos(CAT_A, ap_doc(), AGORA)
        self.assertEqual(r["inventario"], "ok")
        gw = r["itens"][0]
        self.assertEqual(gw, {"id": "gw", "rotulo": "Gateway", "icone": "rede", "online": False,
                              "offline_min": 15, "conexao": None, "alerta_offline_min": 10})
        self.assertEqual(r["itens"][1]["online"], None)  # s10 ausente do arquivo
        self.assertEqual(r["itens"][1]["alerta_offline_min"], None)

    def test_online(self):
        d = ap_doc(aparelhos={"gw": {"online": True, "visto_em": int(AGORA), "conexao": "relay"}})
        gw = eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]
        self.assertEqual((gw["online"], gw["offline_min"], gw["conexao"]), (True, None, "relay"))

    def test_offline_sem_visto(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": None, "conexao": "direto"}})
        gw = eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]
        self.assertEqual((gw["online"], gw["offline_min"]), (False, None))

    def test_visto_no_futuro_nao_fica_negativo(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": int(AGORA + 600), "conexao": None}})
        self.assertEqual(eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]["offline_min"], 0)

    def test_ausente(self):
        r = eco.montar_aparelhos(CAT_A, None, AGORA)
        self.assertEqual((r["inventario"], len(r["itens"])), ("ausente", 2))
        self.assertTrue(all(i["online"] is None and i["offline_min"] is None for i in r["itens"]))

    def test_velho(self):
        r = eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA - 61), AGORA)
        self.assertEqual(r["inventario"], "velho")
        self.assertEqual(r["idade_s"], 61)
        self.assertIsNone(r["itens"][0]["online"])
        self.assertEqual(eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA - 60), AGORA)["inventario"], "ok")

    def test_futuro(self):
        self.assertEqual(eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA + 3), AGORA)["inventario"], "ok")
        self.assertEqual(eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA + 300), AGORA)["inventario"], "velho")

    def test_erro_do_executor_vira_inventario_ausente(self):
        # o executor grava "erro": "<texto curto>" com todos online null quando o tailscale falha
        doc = json.dumps({"versao": 1, "gerado": AGORA - 5, "erro": "json invalido",
                          "aparelhos": {"gw": {"online": None, "visto_em": None, "conexao": None}}})
        r = eco.montar_aparelhos(CAT_A, doc, AGORA)
        self.assertEqual((r["inventario"], r["idade_s"]), ("ausente", None))
        self.assertEqual(len(r["itens"]), 2)
        self.assertTrue(all(i["online"] is None for i in r["itens"]))

    def test_erro_vazio_ou_nulo_nao_atrapalha(self):
        for erro in (None, "", "   "):
            with self.subTest(erro=erro):
                doc = json.dumps({"versao": 1, "gerado": AGORA - 5, "erro": erro,
                                  "aparelhos": {"gw": {"online": True, "visto_em": int(AGORA), "conexao": "direto"}}})
                r = eco.montar_aparelhos(CAT_A, doc, AGORA)
                self.assertEqual((r["inventario"], r["itens"][0]["online"]), ("ok", True))

    def test_relogio_adiantado_e_sinalizado_e_nao_vira_ha_zero_min(self):
        r = eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA + 300), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"], r.get("relogio_adiantado")), ("velho", 300, True))
        r = eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA - 120), AGORA)  # velho de verdade: sem a marca
        self.assertEqual((r["inventario"], r["idade_s"]), ("velho", 120))
        self.assertNotIn("relogio_adiantado", r)
        r = eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA + 3), AGORA)  # dentro da tolerancia: ok
        self.assertNotIn("relogio_adiantado", r)

    def test_offline_sem_visto_usa_o_primeiro_instante_offline(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": None, "conexao": None}})
        desde = {}
        gw = eco.montar_aparelhos(CAT_A, d, AGORA, desde)["itens"][0]
        self.assertEqual((gw["online"], gw["offline_min"]), (False, 0))  # visto agora pela 1a vez
        self.assertEqual(desde, {"gw": AGORA})
        depois = ap_doc(gerado=AGORA + 15 * 60 - 5, aparelhos={"gw": {"online": False, "visto_em": None,
                                                                      "conexao": None}})
        gw = eco.montar_aparelhos(CAT_A, depois, AGORA + 15 * 60, desde)["itens"][0]
        self.assertEqual(gw["offline_min"], 15)
        self.assertEqual(desde, {"gw": AGORA})  # a referencia nao anda
        # voltou a ficar online: a referencia some
        on = ap_doc(aparelhos={"gw": {"online": True, "visto_em": int(AGORA), "conexao": "direto"}})
        on = ap_doc(gerado=AGORA + 20 * 60 - 5,
                    aparelhos={"gw": {"online": True, "visto_em": int(AGORA + 20 * 60), "conexao": "direto"}})
        eco.montar_aparelhos(CAT_A, on, AGORA + 20 * 60, desde)
        self.assertEqual(desde, {})

    def test_offline_sem_visto_sem_dicionario_continua_sem_minutos(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": None, "conexao": None}})
        self.assertIsNone(eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]["offline_min"])

    def test_primeiro_offline_so_vale_com_alerta_offline_min_e_inventario_ok(self):
        d = ap_doc(aparelhos={"s10": {"online": False, "visto_em": None, "conexao": None}})  # s10 nao tem alerta
        desde = {}
        self.assertIsNone(eco.montar_aparelhos(CAT_A, d, AGORA, desde)["itens"][1]["offline_min"])
        self.assertEqual(desde, {})
        desde = {"gw": AGORA - 3600}  # inventario velho (sem dado): nao apaga nem inventa
        r = eco.montar_aparelhos(CAT_A, ap_doc(gerado=AGORA - 120), AGORA, desde)
        self.assertEqual(desde, {"gw": AGORA - 3600})
        self.assertIsNone(r["itens"][0]["offline_min"])

    def test_visto_conhecido_vence_o_primeiro_instante(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": int(AGORA - 15 * 60), "conexao": None}})
        desde = {"gw": AGORA - 3600}
        self.assertEqual(eco.montar_aparelhos(CAT_A, d, AGORA, desde)["itens"][0]["offline_min"], 15)

    def test_json_invalido(self):
        for t in ("", "{", "[]", "null", "3", '{"gerado": 1}', '{"aparelhos": {}}',
                  '{"gerado": "x", "aparelhos": {}}', '{"gerado": true, "aparelhos": {}}',
                  '{"gerado": %d, "aparelhos": []}' % AGORA, '\x00\xff'):
            with self.subTest(t=t):
                r = eco.montar_aparelhos(CAT_A, t, AGORA)
                self.assertEqual(r["inventario"], "ausente")
                self.assertEqual(len(r["itens"]), 2)

    def test_texto_nao_str(self):
        self.assertEqual(eco.montar_aparelhos(CAT_A, 123, AGORA)["inventario"], "ausente")
        self.assertEqual(eco.montar_aparelhos(CAT_A, b"{}", AGORA)["inventario"], "ausente")

    def test_id_fora_do_catalogo_ignorado(self):
        d = ap_doc(aparelhos={"gw": {"online": True, "visto_em": 1, "conexao": "direto"},
                              "empresa-x-x": {"online": True, "visto_em": 1, "conexao": "direto"}})
        r = eco.montar_aparelhos(CAT_A, d, AGORA)
        self.assertEqual([i["id"] for i in r["itens"]], ["gw", "s10"])

    def test_rotulo_do_catalogo_sai_ascii(self):
        cat = [{"id": "gw", "rotulo": "Gaté\x07way", "icone": "rede"}]
        self.assertEqual(eco.montar_aparelhos(cat, None, AGORA)["itens"][0]["rotulo"], "Gateway")

    def test_tipos_errados_em_cada_campo(self):
        ruins = [{"online": "sim"}, {"online": 1}, {"online": None}, {"visto_em": "x"}, {"visto_em": True},
                 {"visto_em": [1]}, {"conexao": "outra"}, {"conexao": 5}, {"conexao": ["direto"]}]
        for e in ruins:
            for base in ({"online": False, "visto_em": int(AGORA - 600), "conexao": None},):
                with self.subTest(e=e):
                    d = ap_doc(aparelhos={"gw": dict(base, **e)})
                    gw = eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]
                    self.assertIn(gw["online"], (True, False, None))
                    self.assertIn(gw["conexao"], ("direto", "relay", None))
                    self.assertTrue(gw["offline_min"] is None or isinstance(gw["offline_min"], int))
        for v in (None, "x", 5, [], [1]):
            d = ap_doc(aparelhos={"gw": v})
            self.assertIsNone(eco.montar_aparelhos(CAT_A, d, AGORA)["itens"][0]["online"])

    def test_nao_levanta_com_catalogo_estranho(self):
        r = eco.montar_aparelhos([{"id": "x"}], ap_doc(), AGORA)
        self.assertEqual(r["itens"], [])


class MontarRotinasTest(unittest.TestCase):
    def test_ok_e_idade(self):
        r = eco.montar_rotinas(CAT_R, ro_doc(), AGORA)
        self.assertEqual(r["inventario"], "ok")
        self.assertEqual(r["itens"][0], {"id": "senhas", "rotulo": "Backup senhas", "resultado": "ok",
                                         "ultima_em": int(AGORA - 3600), "idade_h": 1.0, "max_idade_h": 26,
                                         "atrasada": False, "tipo": "timer",
                                         "alvo": "cerberus-vault-backup.service"})
        self.assertEqual(r["unidades_falhas"], {"n": 0, "nomes": []})

    def test_item_carrega_tipo_e_so_o_alvo_do_timer(self):
        cat = eco.validar_rotinas([rotina(), rotina(id="arq", tipo="arquivo", alvo="/srv/nas/backups/x")])
        d = ro_doc(rotinas={"senhas": {"resultado": "ok", "ultima_em": int(AGORA), "detalhe": ""},
                            "arq": {"resultado": "ok", "ultima_em": int(AGORA), "detalhe": ""}})
        a, b = eco.montar_rotinas(cat, d, AGORA)["itens"]
        self.assertEqual((a["tipo"], a["alvo"]), ("timer", "cerberus-vault-backup.service"))
        self.assertEqual((b["tipo"], b["alvo"]), ("arquivo", None))  # caminho de arquivo nao sai no JSON

    def test_relogio_adiantado_em_rotinas(self):
        r = eco.montar_rotinas(CAT_R, ro_doc(gerado=AGORA + 999), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"], r.get("relogio_adiantado")), ("velho", 999, True))

    def test_atrasada(self):
        d = ro_doc(rotinas={"senhas": {"resultado": "ok", "ultima_em": int(AGORA - 27 * 3600), "detalhe": ""}})
        i = eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]
        self.assertEqual((i["idade_h"], i["atrasada"]), (27.0, True))

    def test_no_limite_nao_atrasa(self):
        d = ro_doc(rotinas={"senhas": {"resultado": "ok", "ultima_em": int(AGORA - 26 * 3600), "detalhe": ""}})
        self.assertFalse(eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]["atrasada"])

    def test_sem_ultima_nao_atrasa(self):
        d = ro_doc(rotinas={"senhas": {"resultado": "desconhecido", "ultima_em": None, "detalhe": ""}})
        i = eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]
        self.assertEqual((i["idade_h"], i["atrasada"], i["resultado"]), (None, False, "desconhecido"))

    def test_ultima_no_futuro(self):
        d = ro_doc(rotinas={"senhas": {"resultado": "ok", "ultima_em": int(AGORA + 500), "detalhe": ""}})
        i = eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]
        self.assertEqual((i["idade_h"], i["atrasada"]), (0.0, False))

    def test_ausente_velho_futuro(self):
        self.assertEqual(eco.montar_rotinas(CAT_R, None, AGORA)["inventario"], "ausente")
        r = eco.montar_rotinas(CAT_R, ro_doc(gerado=AGORA - 120), AGORA)
        self.assertEqual((r["inventario"], r["idade_s"]), ("velho", 120))
        self.assertEqual(r["itens"][0]["resultado"], "desconhecido")
        self.assertEqual(eco.montar_rotinas(CAT_R, ro_doc(gerado=AGORA + 2), AGORA)["inventario"], "ok")
        self.assertEqual(eco.montar_rotinas(CAT_R, ro_doc(gerado=AGORA + 999), AGORA)["inventario"], "velho")

    def test_json_invalido(self):
        for t in ("", "{", "[]", "null", '{"gerado": 1}', '{"gerado": %d, "rotinas": 5}' % AGORA, "\x00"):
            with self.subTest(t=t):
                r = eco.montar_rotinas(CAT_R, t, AGORA)
                self.assertEqual(r["inventario"], "ausente")
                self.assertEqual(r["unidades_falhas"], {"n": 0, "nomes": []})

    def test_id_fora_do_catalogo_ignorado(self):
        d = ro_doc(rotinas={"intruso": {"resultado": "falha", "ultima_em": 1, "detalhe": ""}})
        r = eco.montar_rotinas(CAT_R, d, AGORA)
        self.assertEqual([i["id"] for i in r["itens"]], ["senhas"])
        self.assertEqual(r["itens"][0]["resultado"], "desconhecido")

    def test_tipos_errados_em_cada_campo(self):
        for e in ({"resultado": "talvez"}, {"resultado": 1}, {"resultado": None}, {"ultima_em": "x"},
                  {"ultima_em": True}, {"ultima_em": -5}, {"ultima_em": [1]}, {"ultima_em": float("nan")}):
            with self.subTest(e=e):
                d = ro_doc(rotinas={"senhas": dict({"resultado": "ok", "ultima_em": int(AGORA)}, **e)})
                i = eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]
                self.assertIn(i["resultado"], eco.RESULTADOS)
                self.assertTrue(i["ultima_em"] is None or isinstance(i["ultima_em"], int))
        for v in (None, "x", 3, []):
            d = ro_doc(rotinas={"senhas": v})
            self.assertEqual(eco.montar_rotinas(CAT_R, d, AGORA)["itens"][0]["resultado"], "desconhecido")

    def test_unidades_falhas_saneadas(self):
        falhas = {"n": 7, "nomes": ["ação.service", "x\x1b[31my", "z" * 80, 5, None, "", "d", "e", "f", "g"]}
        u = eco.montar_rotinas(CAT_R, ro_doc(falhas=falhas), AGORA)["unidades_falhas"]
        self.assertEqual(u["n"], 7)
        self.assertEqual(u["nomes"][:2], ["acao.service", "x[31my"])
        self.assertEqual(len(u["nomes"]), 5)
        self.assertTrue(all(n.isascii() and len(n) <= 40 and n.isprintable() for n in u["nomes"]))
        self.assertEqual(u["nomes"][2], "z" * 40)

    def test_unidades_falhas_sem_empresa-x(self):
        falhas = {"n": 4, "nomes": ["empresa-x-sync.service", "srv-empresa-x-repo.mount", "club\x00petro.service", "rclone-nas-sync.service"]}
        u = eco.montar_rotinas(CAT_R, ro_doc(falhas=falhas), AGORA)["unidades_falhas"]
        self.assertEqual(u, {"n": 1, "nomes": ["rclone-nas-sync.service"]})
        falhas = {"n": 1, "nomes": ["empresa-x-sync.service"]}
        u = eco.montar_rotinas(CAT_R, ro_doc(falhas=falhas), AGORA)["unidades_falhas"]
        self.assertEqual(u, {"n": 0, "nomes": []})

    def test_unidades_falhas_tipos_errados(self):
        for f in (None, "x", 5, [], {"n": "3", "nomes": "x"}, {"n": True, "nomes": [1]}, {"n": -4, "nomes": {}},
                  {"n": 1.5}, {"n": 10 ** 12, "nomes": []}):
            with self.subTest(f=f):
                u = eco.montar_rotinas(CAT_R, ro_doc(falhas=f), AGORA)["unidades_falhas"]
                self.assertIsInstance(u["n"], int)
                self.assertLessEqual(u["n"], 9999)
                self.assertGreaterEqual(u["n"], 0)
                self.assertIsInstance(u["nomes"], list)

    def test_rotulo_do_catalogo_sai_ascii(self):
        cat = [{"id": "r", "rotulo": "Copíe\x00a", "max_idade_h": 1}]
        self.assertEqual(eco.montar_rotinas(cat, None, AGORA)["itens"][0]["rotulo"], "Copiea")


class SanearTest(unittest.TestCase):
    def test_casos(self):
        self.assertEqual(eco.sanear("Café", 10), "Cafe")
        self.assertEqual(eco.sanear("a\x00b\x1bc\n", 10), "abc")
        self.assertEqual(eco.sanear("中文", 10), "")
        self.assertEqual(eco.sanear("abcdef", 3), "abc")
        self.assertEqual(eco.sanear(None, 3), "")
        self.assertEqual(eco.sanear(b"x", 3), "")


class ColetorTest(unittest.TestCase):
    def coletor(self, cfg, arquivos):
        def ler(caminho):
            if caminho in arquivos:
                return arquivos[caminho]
            raise OSError("nao existe")
        cfg = dict({"host": "t", "comandos": {"estado": "/run/kindle-monitor/status"}}, **cfg)
        return coletores.Coletor(cfg, leitor_arquivo=ler, executar=lambda *a, **k: "", agora=lambda: AGORA,
                                 buscar=lambda *a, **k: "")

    def test_sem_catalogo_sem_chaves(self):
        for cfg in ({}, {"aparelhos": [], "rotinas": []}, {"aparelhos": "x", "rotinas": [{"id": "ruim"}]},
                    {"aparelhos": None, "rotinas": None}):
            with self.subTest(cfg=cfg):
                m = self.coletor(cfg, {}).coletar()
                self.assertNotIn("aparelhos", m)
                self.assertNotIn("rotinas", m)

    def test_com_catalogo_le_os_caminhos_padrao(self):
        arq = {"/run/kindle-monitor/status/aparelhos.json": ap_doc(),
               "/run/kindle-monitor/status/rotinas.json": ro_doc()}
        m = self.coletor({"aparelhos": [aparelho()], "rotinas": [rotina()]}, arq).coletar()
        self.assertEqual(m["aparelhos"]["inventario"], "ok")
        self.assertEqual(m["aparelhos"]["itens"][0]["offline_min"], 15)
        self.assertEqual(m["rotinas"]["inventario"], "ok")

    def test_arquivo_ausente_e_leitor_que_levanta(self):
        m = self.coletor({"aparelhos": [aparelho()], "rotinas": [rotina()]}, {}).coletar()
        self.assertEqual(m["aparelhos"]["inventario"], "ausente")
        self.assertEqual(m["rotinas"]["inventario"], "ausente")

    def test_diretorio_de_estado_da_config(self):
        arq = {"/x/aparelhos.json": ap_doc()}
        c = self.coletor({"aparelhos": [aparelho()], "comandos": {"estado": "/x"}}, arq)
        self.assertEqual(c.coletar()["aparelhos"]["inventario"], "ok")

    def test_ponta_a_ponta_alertas(self):
        arq = {"/run/kindle-monitor/status/aparelhos.json": ap_doc(),
               "/run/kindle-monitor/status/rotinas.json": ro_doc(
                   rotinas={"senhas": {"resultado": "ok", "ultima_em": int(AGORA - 30 * 3600), "detalhe": ""}})}
        m = self.coletor({"aparelhos": [aparelho()], "rotinas": [rotina()]}, arq).coletar()
        r = alertas.avaliar(m)
        textos = {(a["nivel"], a["texto"]) for a in r["itens"]} if isinstance(r, dict) else \
            {(a["nivel"], a["texto"]) for a in r}
        self.assertIn(("critico", "Gateway offline ha 15 min"), textos)
        self.assertIn(("aviso", "Backup senhas atrasada"), textos)

    def test_dentro_do_limite_nao_alerta(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": int(AGORA - 5 * 60), "conexao": None}})
        arq = {"/run/kindle-monitor/status/aparelhos.json": d}
        m = self.coletor({"aparelhos": [aparelho()]}, arq).coletar()
        r = alertas.avaliar(m)
        itens = r["itens"] if isinstance(r, dict) else r
        self.assertFalse([a for a in itens if "offline" in a["texto"]])

    def test_offline_sem_visto_alerta_pelo_primeiro_instante_visto_pelo_servidor(self):
        d = ap_doc(aparelhos={"gw": {"online": False, "visto_em": None, "conexao": None}})
        arq = {"/run/kindle-monitor/status/aparelhos.json": d}
        relogio = [AGORA]
        c = self.coletor({"aparelhos": [aparelho()]}, arq)
        c._agora = lambda: relogio[0]
        self.assertEqual(c.aparelhos_inventario()["itens"][0]["offline_min"], 0)
        self.assertFalse([a for a in alertas.avaliar({"aparelhos": c.aparelhos_inventario()}) if "offline" in a["texto"]])
        relogio[0] = AGORA + 11 * 60
        arq["/run/kindle-monitor/status/aparelhos.json"] = ap_doc(
            gerado=relogio[0], aparelhos={"gw": {"online": False, "visto_em": None, "conexao": None}})
        r = c.aparelhos_inventario()
        self.assertEqual(r["itens"][0]["offline_min"], 11)
        self.assertIn("Gateway offline ha 11 min", textos_de(alertas.avaliar({"aparelhos": r})))
        # volta a ficar online e cai de novo: a contagem recomeca
        relogio[0] = AGORA + 12 * 60
        arq["/run/kindle-monitor/status/aparelhos.json"] = ap_doc(
            gerado=relogio[0], aparelhos={"gw": {"online": True, "visto_em": int(relogio[0]), "conexao": "direto"}})
        c.aparelhos_inventario()
        relogio[0] = AGORA + 20 * 60
        arq["/run/kindle-monitor/status/aparelhos.json"] = ap_doc(
            gerado=relogio[0], aparelhos={"gw": {"online": False, "visto_em": None, "conexao": None}})
        self.assertEqual(c.aparelhos_inventario()["itens"][0]["offline_min"], 0)

    def test_inventario_velho_vira_aviso_de_fonte(self):
        arq = {"/run/kindle-monitor/status/aparelhos.json": ap_doc(gerado=AGORA - 300)}
        m = self.coletor({"aparelhos": [aparelho()]}, arq).coletar()
        r = alertas.avaliar(m)
        itens = r["itens"] if isinstance(r, dict) else r
        self.assertTrue([a for a in itens if "sem atualizar ha 5 min" in a["texto"]])


if __name__ == "__main__":
    unittest.main()
