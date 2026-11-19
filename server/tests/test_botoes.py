import os
import re
import shlex
import shutil
import subprocess
import unittest

import _caminho  # noqa: F401
import botoes
import servicos


def _sobrepoe(a, b, folga=0):
    return not (a["x"] + a["w"] + folga <= b["x"] or b["x"] + b["w"] + folga <= a["x"]
                or a["y"] + a["h"] + folga <= b["y"] or b["y"] + b["h"] + folga <= a["y"])


def mk(i, grupo="host", estado="ativo", verbos=("reiniciar",), **k):
    d = {"id": "s%d" % i, "rotulo": "Servico %d" % i, "grupo": grupo, "estado": estado, "detalhe": "",
         "verbos": list(verbos), "protegido": False, "opcional": False}
    d.update(k)
    return d


def itens_cheios(n=52):
    """52 servicos: 4 grupos, estados e verbos variados (inclui itens sem verbos)."""
    grupos = ("host", "incus", "docker", "ragnarok")
    estados = ("ativo", "parado", "falha", "desconhecido", "ativo", "ativo")
    verbos = (("reiniciar", "ligar", "parar"), ("reiniciar",), (), ("ligar", "parar"))
    return servicos.ordenar([mk(i, grupos[i * 4 // n], estados[i % 6], verbos[i % 4]) for i in range(n)])


class LayoutTest(unittest.TestCase):
    TAMANHOS = ((1236, 1648), (800, 1300), (1072, 1448))

    @staticmethod
    def visiveis(bs):
        return [b for b in bs if b["visivel"]]

    def todos(self):
        its = itens_cheios()
        for pagina in botoes.PAGINAS:
            for larg, alt in self.TAMANHOS:
                for armado in (None, "gpu-descarregar", "svc:s0:reiniciar"):
                    for p in (1, 2, 99):
                        yield pagina, armado, larg, alt, p, botoes.layout(pagina, armado, larg, alt, p, its)

    def test_tamanho_minimo(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in self.visiveis(bs):
                nav = b["tipo"] == "local" and b["id"].startswith("pagina:") or b["id"] == "atualizar"
                self.assertGreaterEqual(b["w"], 100 if nav and larg < 1100 else 150, (pagina, b["id"], larg))
                self.assertGreaterEqual(b["h"], 84, (pagina, b["id"]))

    def test_dentro_da_tela_e_separados_por_16px(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in bs:
                self.assertGreaterEqual(b["x"], 0)
                self.assertGreaterEqual(b["y"], 0)
                self.assertLessEqual(b["x"] + b["w"], larg)
                self.assertLessEqual(b["y"] + b["h"], alt)
            vis = self.visiveis(bs)
            for i, a in enumerate(vis):
                for b in vis[i + 1:]:
                    self.assertFalse(_sobrepoe(a, b, 16), (pagina, p, larg, a["id"], b["id"]))

    def test_conteudo_nunca_invade_a_navegacao(self):
        for pagina, _, larg, alt, p, bs in self.todos():
            for b in bs:
                if b["tipo"] == "comando" or b["id"].startswith("servicos:"):
                    self.assertLessEqual(b["y"] + b["h"], botoes.nav_topo(alt) - 16, (pagina, b["id"]))

    def test_ids_unicos_e_chaves(self):
        for pagina, _, _, _, _, bs in self.todos():
            ids = [b["id"] for b in self.visiveis(bs)]  # as linhas invisiveis repetem destinos (3 vao a detalhes)
            self.assertEqual(len(ids), len(set(ids)))
            for b in bs:
                self.assertEqual(set(b), {"id", "rotulo", "x", "y", "w", "h", "tipo", "armado", "visivel"})
                self.assertIn(b["tipo"], ("local", "comando"))
                self.assertRegex(b["id"], r"^[a-z0-9:-]+$")  # o que o Kindle aceita

    def test_barra_de_navegacao_em_todas_as_paginas(self):
        esperado = [("pagina:resumo", "Inicio"), ("pagina:servicos", "Servicos"), ("pagina:aparelhos", "Aparelhos"),
                    ("pagina:detalhes", "Sistema"), ("pagina:claude", "Dev"), ("pagina:comandos", "Acoes")]
        self.assertEqual([(b, r) for b, r, _ in botoes.NAV], esperado)
        self.assertEqual([i for _, _, i in botoes.NAV], ["inicio", "servicos", "aparelhos", "sistema", "dev", "acoes"])
        self.assertNotIn("atualizar", [b for b, _, _ in botoes.NAV])
        for pagina in botoes.PAGINAS:
            nav = [b for b in botoes.layout(pagina) if b["visivel"] and b["id"] in dict(esperado)]
            self.assertEqual([(b["id"], b["rotulo"]) for b in nav], esperado)
            self.assertEqual(len({b["y"] for b in nav}), 1)
            self.assertFalse(any(b["armado"] for b in nav))
            self.assertTrue(all(b["tipo"] == "local" and b["h"] == 96 for b in nav))

    def test_paginas_do_desenho(self):
        self.assertEqual(botoes.PAGINAS, ("resumo", "servicos", "aparelhos", "detalhes", "claude", "comandos"))

    def test_atualizar_invisivel_sobre_o_relogio_em_todas_as_paginas(self):
        for pagina in botoes.PAGINAS:
            for larg, alt in self.TAMANHOS:
                a = [b for b in botoes.layout(pagina, None, larg, alt) if b["id"] == "atualizar"]
                self.assertEqual(len(a), 1, pagina)
                a = a[0]
                self.assertFalse(a["visivel"])
                self.assertEqual((a["x"], a["y"], a["w"], a["h"], a["tipo"]),
                                 (larg - botoes.MARGEM - 200, botoes.BARRA_KINDLE_H, 200, 70, "local"))

    def test_so_o_resumo_tem_linhas_invisiveis_para_pagina(self):
        for pagina in botoes.PAGINAS:
            inv = [b for b in botoes.layout(pagina) if not b["visivel"] and b["id"] != "atualizar"]
            self.assertEqual(len(inv), 8 if pagina == "resumo" else 0, pagina)
            vis = [b for b in botoes.layout(pagina, None, 1236, 1648, 1, itens_cheios()) if b["visivel"]]
            self.assertTrue(all(b["id"] != "atualizar" for b in vis), pagina)


    def test_nav_mais_baixa_que_antes(self):
        self.assertLess(botoes.NAV_H, 130)
        self.assertEqual(botoes.nav_topo(1648), 1648 - 24 - 96)

    def test_so_comandos_e_servicos_tem_botoes_de_comando(self):
        self.assertFalse([b for b in botoes.layout("resumo", None, 1236, 1648, 1, itens_cheios()) if b["tipo"] == "comando"])
        self.assertFalse([b for b in botoes.layout("detalhes", "bots-pausar") if b["tipo"] == "comando"])
        ids = [b["id"] for b in botoes.layout("comandos") if b["tipo"] == "comando"]
        self.assertEqual(ids, ["gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar"])
        self.assertNotIn("ragnarok-reiniciar", ids)
        self.assertNotIn("ollama-reiniciar", ids)

    def test_armado_so_um_e_com_rotulo_de_confirmacao(self):
        bs = botoes.layout("comandos", "bots-pausar")
        armados = [b for b in bs if b["armado"]]
        self.assertEqual([b["id"] for b in armados], ["bots-pausar"])
        self.assertEqual(armados[0]["rotulo"], "Toque de novo para confirmar")
        self.assertEqual({b["rotulo"] for b in bs if b["id"] == "bots-retomar"}, {"Retomar bots"})

    def test_armado_invalido_ou_em_outra_pagina_e_ignorado(self):
        its = itens_cheios()
        for pagina, armado in (("comandos", "xpto"), ("comandos", "pagina:resumo"), ("resumo", "bots-pausar"),
                               ("comandos", None), ("comandos", "svc:nao-existe:parar"), ("servicos", "svc:s2:ligar"),
                               ("servicos", "svc:s0:apagar"), ("servicos", "gpu-descarregar")):
            self.assertFalse(any(b["armado"] for b in botoes.layout(pagina, armado, 1236, 1648, 1, its)), (pagina, armado))

    def test_pagina_invalida_vira_resumo(self):
        self.assertEqual(botoes.layout("zzz"), botoes.layout("resumo"))

    def test_pura(self):
        its = itens_cheios()
        self.assertEqual(botoes.layout("servicos", "svc:s0:reiniciar", 1236, 1648, 2, its),
                         botoes.layout("servicos", "svc:s0:reiniciar", 1236, 1648, 2, its))

    def test_comandos_cabem_antes_da_navegacao(self):
        for larg, alt in self.TAMANHOS:
            g = botoes.geometria_comandos(larg, alt)
            self.assertLessEqual(g["fim_botoes"], botoes.limite(alt))
            # sobra pelo menos a lista de ultimos comandos (titulo + 3 linhas)
            self.assertGreaterEqual(botoes.limite(alt) - g["fim_botoes"], botoes.ULTIMOS_TITULO_H + 3 * g["linha_h"])


class ServicosLayoutTest(unittest.TestCase):
    def test_botoes_contextuais_por_estado(self):
        its = servicos.ordenar([
            mk(0, estado="ativo", verbos=("reiniciar", "ligar", "parar")),
            mk(1, estado="parado", verbos=("reiniciar", "ligar", "parar")),
            mk(2, estado="falha", verbos=("reiniciar", "ligar", "parar")),
            mk(3, estado="desconhecido", verbos=("reiniciar", "ligar", "parar")),
            mk(4, estado="ativo", verbos=()),
            mk(5, estado="parado", verbos=("reiniciar",)),
            mk(6, estado="ativo", verbos=("ligar", "parar")),
        ])
        ids = [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"]
        self.assertEqual(ids, ["svc:s0:reiniciar", "svc:s0:parar", "svc:s1:ligar", "svc:s2:reiniciar",
                               "svc:s5:reiniciar", "svc:s6:parar"])

    def test_botoes_de_linha_150x84_com_16px_e_alinhados_a_direita(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar"))])
        bs = [b for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"]
        self.assertEqual(len(bs), 2)
        self.assertEqual({(b["w"], b["h"]) for b in bs}, {(190, 84)})
        self.assertEqual(bs[0]["x"] + bs[0]["w"] + 16, bs[1]["x"])
        self.assertEqual(bs[1]["x"] + bs[1]["w"], 1236 - botoes.MARGEM)
        self.assertEqual(bs[0]["y"], bs[1]["y"])

    def test_rotulos_dos_verbos(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar")), mk(1, estado="parado", verbos=("ligar",))])
        r = {b["id"]: b["rotulo"] for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["tipo"] == "comando"}
        self.assertEqual(r, {"svc:s0:reiniciar": "Reiniciar", "svc:s0:parar": "Parar", "svc:s1:ligar": "Ligar"})

    def test_armado_invertido_com_confirmar(self):
        its = servicos.ordenar([mk(0, verbos=("reiniciar", "ligar", "parar"))])
        bs = botoes.layout("servicos", "svc:s0:parar", 1236, 1648, 1, its)
        arm = [b for b in bs if b["armado"]]
        self.assertEqual([(b["id"], b["rotulo"]) for b in arm], [("svc:s0:parar", "Confirmar?")])
        self.assertEqual([b["rotulo"] for b in bs if b["id"] == "svc:s0:reiniciar"], ["Reiniciar"])

    def test_paginacao_cobre_todos_os_itens_sem_repetir(self):
        its = itens_cheios()
        g1 = botoes.geometria_servicos(its, 1236, 1648, 1)
        n = g1["paginas"]
        self.assertGreater(n, 1)
        vistos = []
        for p in range(1, n + 1):
            g = botoes.geometria_servicos(its, 1236, 1648, p)
            self.assertEqual(g["p"], p)
            vistos += [e["item"]["id"] for e in g["entradas"] if e["tipo"] == "svc"]
            self.assertLessEqual(g["fim"], botoes.limite(1648))
        self.assertEqual(vistos, [i["id"] for i in its])

    def test_p_invalido_e_fora_da_faixa(self):
        its = itens_cheios()
        n = botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"]
        for p, esperado in ((None, 1), ("x", 1), (0, 1), (-4, 1), ("0", 1), (n + 5, n), ("999", n), ("2", 2), (1.0, 1)):
            self.assertEqual(botoes.geometria_servicos(its, 1236, 1648, p)["p"], esperado, p)
        self.assertEqual(botoes.layout("servicos", None, 1236, 1648, 999, its),
                         botoes.layout("servicos", None, 1236, 1648, n, its))

    def test_botoes_de_paginacao(self):
        its = itens_cheios()
        n = botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"]
        ids = lambda p: [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, p, its) if b["id"].startswith("servicos:")]
        self.assertEqual(ids(1), ["servicos:proxima"])
        self.assertEqual(ids(2), ["servicos:proxima", "servicos:anterior"])
        self.assertEqual(ids(n), ["servicos:anterior"])
        rot = {b["id"]: b["rotulo"] for b in botoes.layout("servicos", None, 1236, 1648, 2, its)}
        self.assertEqual((rot["servicos:anterior"], rot["servicos:proxima"]), ("< Anterior", "Proxima >"))
        for b in botoes.layout("servicos", None, 1236, 1648, 2, its):
            if b["id"].startswith("servicos:"):
                self.assertEqual(b["tipo"], "local")

    def test_uma_pagina_so_nao_tem_paginacao(self):
        its = servicos.ordenar([mk(i) for i in range(5)])
        g = botoes.geometria_servicos(its, 1236, 1648, 1)
        self.assertEqual((g["paginas"], g["barra"]), (1, None))
        self.assertFalse([b for b in botoes.layout("servicos", None, 1236, 1648, 1, its) if b["id"].startswith("servicos:")])

    def test_catalogo_real_cabe_em_4_paginas(self):
        import json
        import os
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(raiz, "deploy", "config.atheron.json")) as f:
            cat = servicos.validar_catalogo(json.load(f)["servicos_kindle"])
        its = servicos.ordenar([dict(c, estado="ativo", detalhe="") for c in cat])
        self.assertEqual(botoes.geometria_servicos(its, 1236, 1648, 1)["paginas"], 4)

    def test_sem_itens(self):
        g = botoes.geometria_servicos([], 1236, 1648, 3)
        self.assertEqual((g["p"], g["paginas"], g["entradas"]), (1, 1, []))

    def test_armado_valido(self):
        its = [mk(0, verbos=("reiniciar",))]
        self.assertEqual(botoes.armado_valido("svc:s0:reiniciar", its), "svc:s0:reiniciar")
        self.assertIsNone(botoes.armado_valido("svc:s0:parar", its))
        self.assertIsNone(botoes.armado_valido("svc:s1:reiniciar", its))
        self.assertIsNone(botoes.armado_valido("svc:s0:reiniciar", ()))
        self.assertEqual(botoes.armado_valido("bots-pausar"), "bots-pausar")
        self.assertIsNone(botoes.armado_valido(None))


class ResumoGeometriaTest(unittest.TestCase):
    def test_oito_linhas_fixas_ancoradas_acima_da_navegacao(self):
        g = botoes.geometria_resumo(1236, 1648)
        self.assertEqual([l["id"] for l in g["linhas"]],
                         ["atheron", "nas", "aparelhos", "servicos", "rotinas", "claude", "github", "ragnarok"])
        self.assertEqual([l["destino"] for l in g["linhas"]],
                         ["detalhes", "detalhes", "aparelhos", "servicos", "detalhes", "claude", "claude", "servicos"])
        self.assertEqual(g["linhas"][0]["y"], 532)
        for a, b in zip(g["linhas"], g["linhas"][1:]):
            self.assertEqual(b["y"] - (a["y"] + a["h"]), 12)
        for l in g["linhas"]:
            self.assertEqual((l["x"], l["w"], l["h"]), (48, 1236 - 96, 112))
        ult = g["linhas"][-1]
        self.assertEqual(ult["y"] + ult["h"], botoes.limite(1648))
        self.assertLessEqual(ult["y"] + ult["h"], botoes.nav_topo(1648) - 16)
        self.assertEqual(g["atencao"], {"x": 48, "y": botoes.TOPO, "w": 1236 - 96, "h": 532 - botoes.TOPO})

    def test_tela_baixa_nao_emite_linhas_com_y_negativo(self):
        for altura in (600, 800, 1000, 1200):
            g = botoes.geometria_resumo(1236, altura)
            self.assertEqual(g["linhas"], [], altura)
            lay = botoes.layout("resumo", None, 1236, altura)
            self.assertEqual([b for b in lay if b["id"].startswith("pagina:") and not b["visivel"]], [], altura)
            for b in lay:
                self.assertGreaterEqual(b["y"], 0, (altura, b["id"]))
            self.assertGreaterEqual(g["atencao"]["h"], 0)
        g = botoes.geometria_resumo(1236, 1648)
        self.assertEqual(len(g["linhas"]), 8)
        self.assertGreaterEqual(g["linhas"][0]["y"] - botoes.TOPO, botoes.ATENCAO_MIN_H)

    def test_independe_das_metricas_e_aparece_no_layout(self):
        g = botoes.geometria_resumo(1236, 1648)
        inv = [b for b in botoes.layout("resumo") if not b["visivel"] and b["id"] != "atualizar"]
        self.assertEqual([(b["id"], b["x"], b["y"], b["w"], b["h"], b["tipo"]) for b in inv],
                         [("pagina:" + l["destino"], l["x"], l["y"], l["w"], l["h"], "local") for l in g["linhas"]])
        self.assertEqual(botoes.layout("resumo", None, 1236, 1648, 1, itens_cheios()), botoes.layout("resumo"))


class TapShTest(unittest.TestCase):
    PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kindle", "kindle-monitor")
    PADRAO_READ = 'PAGINA) case "$v" in \'\'|*[!a-z]*) ;; *) [ ${#v} -le 16 ] && PAGINA=$v ;; esac ;;'

    def ler(self, nome):
        with open(os.path.join(self.PASTA, nome), encoding="utf-8") as f:
            return f.read()

    def test_todo_id_de_pagina_casa_com_o_padrao_generico(self):
        for p in botoes.PAGINAS:
            self.assertRegex(p, r"^[a-z]{1,16}$")
        for bid, _, _ in botoes.NAV:
            self.assertRegex(bid, r"^pagina:[a-z]{1,16}$")
            self.assertIn(bid[len("pagina:"):], botoes.PAGINAS)

    def test_os_dois_case_sao_o_padrao_generico(self):
        for nome in ("tap.sh", "loop.sh"):
            texto = self.ler(nome)
            self.assertEqual(texto.count("PAGINA) case"), 1, nome)
            self.assertIn(self.PADRAO_READ, texto, nome)
            # nenhuma lista fixa de paginas sobrou
            for p in botoes.PAGINAS:
                self.assertNotIn("pagina:%s |" % p, texto, nome)
                self.assertNotIn("%s|" % p, texto.replace("pagina:", ""), nome)
        tap = self.ler("tap.sh")
        self.assertEqual(len(re.findall(r"^\s*pagina:\*\)", tap, re.M)), 1)

    @unittest.skipUnless(shutil.which("busybox"), "sem busybox")
    def test_trecho_do_read_state_rodado_no_busybox(self):
        casos = {"aparelhos": "aparelhos", "resumo": "resumo", "abcdefghijklmnop": "abcdefghijklmnop",
                 "Aparelhos": "resumo", "a1": "resumo", "../x": "resumo", "abcdefghijklmnopq": "resumo", "": "resumo",
                 "a b": "resumo"}
        for v, esperado in casos.items():
            script = 'PAGINA=resumo\nv=%s\ncase "$k" in\n  %s\nesac\nprintf %%s "$PAGINA"\n' % (
                shlex.quote(v), self.PADRAO_READ)
            r = subprocess.run(["busybox", "sh", "-c", 'k=PAGINA; ' + script], capture_output=True, text=True, timeout=10)
            self.assertEqual(r.stdout, esperado, (v, r.stderr))

    @unittest.skipUnless(shutil.which("busybox"), "sem busybox")
    def test_ramo_pagina_do_tap_sh_no_busybox(self):
        tap = self.ler("tap.sh")
        ini = tap.index("  pagina:*)")
        fim = tap.index("  modo:desempenho")
        ramo = tap[ini:fim]
        casos = {"pagina:aparelhos": "aparelhos", "pagina:Aparelhos": "resumo", "pagina:a1": "resumo",
                 "pagina:../x": "resumo", "pagina:abcdefghijklmnopq": "resumo", "pagina:": "resumo"}
        for bid, esperado in casos.items():
            script = 'PAGINA=resumo\nlog() { :; }\nid=%s\ncase "$id" in\n%s  *) ;;\nesac\nprintf %%s "$PAGINA"\n' % (
                shlex.quote(bid), ramo)
            r = subprocess.run(["busybox", "sh", "-c", script], capture_output=True, text=True, timeout=10)
            self.assertEqual(r.stdout, esperado, (bid, r.stderr))


if __name__ == "__main__":
    unittest.main()
