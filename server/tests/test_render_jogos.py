"""Painel de jogos na imagem e no texto: linha JOGOS da tela inicial, pagina `jogos` (nao e aba) e /tela.txt."""
import os
import re
import unittest

import _caminho  # noqa: F401
import botoes
import canvas as cv
import render
import render_png
from test_paginas_png import px
from test_render_png import completo, historico

ABERTAS = [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True}, {"rotulo": "MAP", "aberto": True}]
FECHADA = [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True}, {"rotulo": "MAP", "aberto": False}]


def inst(i, nome, estado="rodando", jogadores=None, maximo=None, modulo="Minecraft"):
    return {"id": i, "nome": nome, "modulo": modulo, "estado": estado, "jogadores": jogadores, "max": maximo}


def amp(instancias=None, ativo=True, inventario="ok", erro=None, idade_s=4):
    return {"ativo": ativo, "inventario": inventario, "idade_s": idade_s, "erro": erro,
            "instancias": instancias if instancias is not None else []}


QUATRO = [inst("00000001", "Minecraft", "rodando", 2, 20), inst("00000002", "Terraria", "rodando", 0, 8, "Terraria"),
          inst("00000003", "Palworld", "iniciando", modulo="Palworld"),
          inst("00000004", "Valheim", "parado", modulo="Valheim")]


def m_jogos(rag=True, portas=ABERTAS, blocos=None, **extra):
    m = {"host": "atheron", "gerado_em": "2026-11-15T14:32:10-03:00"}
    if rag:
        m["ragnarok"] = {"jogadores": 0, "parado": False, "idade_s": 4}
    if portas is not None:
        m["portas"] = portas
    if blocos is not None:
        m["amp"] = blocos
    m.update(extra)
    return m


def linha(m, alertas_=(), kv=None):
    ls = {l["id"]: l for l in render_png._linhas_resumo(m, [], kv, list(alertas_))}
    return ls["jogos"]


class LinhaJogosTest(unittest.TestCase):
    def test_a_linha_e_jogos_e_nao_ragnarok(self):
        ls = render_png._linhas_resumo({}, [], None, [])
        self.assertEqual([l["id"] for l in ls][-1], "jogos")
        self.assertNotIn("ragnarok", [l["id"] for l in ls])
        l = ls[-1]
        self.assertEqual((l["titulo"], l["icone"], l["valor"], l["estado"]), ("JOGOS", "jogo", "sem dados", "sem_dados"))

    def test_resumo_ligadas_primeiro_e_detalhe(self):
        l = linha(m_jogos(blocos=amp(QUATRO)))
        self.assertEqual(l["valor"], "Ragnarok 0  Minecraft 2/20  Terraria 0/8")
        self.assertEqual(l["detalhe"], "login ok char ok map ok" + render_png.SEP + "iniciando: Palworld"
                         + render_png.SEP + "parado: Valheim")
        self.assertEqual(l["estado"], "ok")

    def test_parados_listados_em_ordem_do_amp(self):
        itens = [inst("00000001", "Valheim", "parado"), inst("00000002", "Palworld", "parado"),
                 inst("00000003", "Minecraft", "rodando", 1, 20)]
        l = linha(m_jogos(blocos=amp(itens)))
        self.assertEqual(l["valor"], "Ragnarok 0  Minecraft 1/20")
        self.assertTrue(l["detalhe"].endswith("parado: Palworld, Valheim"), l["detalhe"])  # por nome

    def test_porta_fechada_no_detalhe_e_estado_vem_do_alerta(self):
        al = [{"nivel": "aviso", "sistema": "jogos"}]
        l = linha(m_jogos(portas=FECHADA, blocos=amp(QUATRO)), al)
        self.assertTrue(l["detalhe"].startswith("MAP fechada" + render_png.SEP), l["detalhe"])
        self.assertNotIn("login ok", l["detalhe"])
        self.assertEqual(l["estado"], "aviso")

    def test_varias_portas_fechadas(self):
        portas = [{"rotulo": "LOGIN", "aberto": False}, {"rotulo": "CHAR", "aberto": True},
                  {"rotulo": "MAP", "aberto": False}]
        self.assertEqual(linha(m_jogos(portas=portas))["detalhe"], "LOGIN, MAP fechadas")

    def test_instancia_parada_nao_muda_a_forma_da_linha(self):
        parados = [inst("00000001", "Valheim", "parado"), inst("00000002", "Palworld", "parado")]
        self.assertEqual(linha(m_jogos(blocos=amp(parados)))["estado"], "ok")
        # nem o alerta do AMP (sistema "amp") nem a instancia mudam a forma
        self.assertEqual(linha(m_jogos(blocos=amp(parados)), [{"nivel": "leve", "sistema": "amp"}])["estado"], "ok")

    def test_amp_nao_configurado_ou_desligado_e_so_o_ragnarok_sem_erro(self):
        sem = linha(m_jogos())
        self.assertEqual((sem["valor"], sem["detalhe"], sem["estado"]), ("Ragnarok 0", "login ok char ok map ok", "ok"))
        for b in (amp(ativo=False), amp(ativo=None, inventario="ausente"), amp(ativo=False, inventario="velho")):
            with self.subTest(b=b):
                self.assertEqual(linha(m_jogos(blocos=b)), sem)

    def test_amp_ativo_sem_dados_e_interrogacao(self):
        for b in (amp(erro="amp sem resposta"), amp(inventario="velho", idade_s=300)):
            l = linha(m_jogos(blocos=b))
            with self.subTest(b=b):
                self.assertEqual(l["valor"], "Ragnarok 0")
                self.assertTrue(l["detalhe"].endswith("AMP sem dados"), l["detalhe"])
                self.assertEqual(l["estado"], "sem_dados")

    def test_amp_ausente_nao_e_sem_dados(self):
        # arquivo ausente = `ativo` desconhecido: a linha nao inventa um "?" nem um aviso
        self.assertEqual(linha(m_jogos(blocos=amp(ativo=None, inventario="ausente")))["estado"], "ok")

    def test_amp_sem_dados_com_porta_fechada_mostra_a_porta(self):
        al = [{"nivel": "aviso", "sistema": "jogos"}, {"nivel": "leve", "sistema": "amp"}]
        l = linha(m_jogos(portas=FECHADA, blocos=amp(erro="amp login falhou")), al)
        self.assertEqual(l["estado"], "aviso")
        self.assertIn("AMP sem dados", l["detalhe"])

    def test_amp_sem_dados_sem_ragnarok(self):
        l = linha(m_jogos(rag=False, portas=None, blocos=amp(erro="x")))
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "AMP sem dados", "sem_dados"))

    def test_so_amp_tudo_parado(self):
        l = linha(m_jogos(rag=False, portas=None, blocos=amp([inst("00000001", "Valheim", "parado")])))
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("nenhum ligado", "parado: Valheim", "ok"))

    def test_so_amp_sem_instancias(self):
        l = linha(m_jogos(rag=False, portas=None, blocos=amp([])))
        self.assertEqual(l["estado"], "ok")
        self.assertNotEqual(l["valor"], "")

    def test_ragnarok_parado_e_sem_numero(self):
        l = linha(m_jogos(ragnarok={"jogadores": 2, "parado": True, "idade_s": 300}))
        self.assertEqual(l["valor"], "Ragnarok 2  parado")
        l = linha(m_jogos(ragnarok={"erro": "n/d"}))
        self.assertEqual(l["valor"], "sem dados")  # portas ok, mas sem contagem: o detalhe diz o resto
        self.assertEqual(l["detalhe"], "login ok char ok map ok")

    def test_contagens_parciais(self):
        itens = [inst("00000001", "A", "rodando", 3, None), inst("00000002", "B", "rodando", None, None),
                 inst("00000003", "C", "rodando", 1, 20)]
        self.assertEqual(linha(m_jogos(rag=False, portas=None, blocos=amp(itens)))["valor"], "A 3  B  C 1/20")

    def test_outro_e_falha_vao_para_o_detalhe(self):
        itens = [inst("00000001", "A", "falha"), inst("00000002", "B", "outro")]
        d = linha(m_jogos(rag=False, portas=None, blocos=amp(itens)))["detalhe"]
        self.assertEqual(d, "falha: A" + render_png.SEP + "outro: B")

    def test_nada_configurado(self):
        l = linha({})
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "", "sem_dados"))

    def test_tipos_errados_nunca_levantam(self):
        ruins = (None, 5, "x", [], [1, None], {"erro": "n/d"}, float("nan"), True, 10 ** 400)
        for r in ruins:
            for chave in ("amp", "ragnarok", "portas"):
                m = m_jogos(blocos=amp(QUATRO))
                m[chave] = r
                linha(m)
        for it in ruins:
            linha(m_jogos(blocos=amp([it, inst("00000001", "A", "rodando", it, it)])))
        linha(m_jogos(blocos={"ativo": True, "inventario": "ok", "erro": None, "instancias": 5}))

    def test_texto_do_amp_nunca_estoura_a_linha(self):
        # o texto e saneado no web; aqui so garante que o desenho nao quebra com nomes no limite
        itens = [inst("%08x" % n, "N" * 24, "rodando", 99999, 99999) for n in range(16)]
        c = cv.Canvas(1236, 1648, estrito=True)
        render_png.desenhar(c, m_jogos(blocos=amp(itens)), historico(), "resumo")


class CorteEmItensTest(unittest.TestCase):
    def setUp(self):
        self.c = cv.Canvas(1236, 1648)

    def test_cabe_inteiro(self):
        self.assertEqual(render_png._ajustar_itens(self.c, "parado: A, B", "sans", 26, 2000), "parado: A, B")

    def test_corta_so_entre_itens(self):
        texto = "login ok char ok map ok" + render_png.SEP + "parado: Valheim, Palworld, Terraria"
        larg = self.c.medir("login ok char ok map ok" + render_png.SEP + "parado: Valheim, Palw", "sans", 26)
        r = render_png._ajustar_itens(self.c, texto, "sans", 26, larg)
        self.assertTrue(r.endswith("parado: Valheim..."), r)
        self.assertLessEqual(self.c.medir(r, "sans", 26), larg)

    def test_valor_corta_na_fronteira_de_dois_espacos(self):
        texto = "Ragnarok 0  Minecraft 2/20  Terraria 0/8  Valheim 3/10"
        larg = self.c.medir("Ragnarok 0  Minecraft 2/20  Terra", "sans-bold", 34)
        r = render_png._ajustar_itens(self.c, texto, "sans-bold", 34, larg)
        self.assertEqual(r, "Ragnarok 0  Minecraft 2/20...")

    def test_sem_fronteira_cai_no_corte_por_caractere(self):
        r = render_png._ajustar_itens(self.c, "umaPalavraMuitoLongaSemEspacos", "sans", 26, 120)
        self.assertTrue(r.endswith("..."))
        self.assertLessEqual(self.c.medir(r, "sans", 26), 120)

    def test_largura_minima_nunca_levanta(self):
        for larg in (-5, 0, 1, 10):
            render_png._ajustar_itens(self.c, "a, b  c", "sans", 26, larg)


def tela(m, pagina="jogos", w=1236, h=1648):
    c = cv.Canvas(w, h, estrito=True)
    textos = []
    orig = cv.Canvas.texto

    def espia(self, x, y, t, fonte, tam, *a, **k):
        textos.append((t, fonte, tam, y))
        return orig(self, x, y, t, fonte, tam, *a, **k)
    cv.Canvas.texto = espia
    try:
        render_png.desenhar(c, m, historico(), pagina)
    finally:
        cv.Canvas.texto = orig
    return c, textos


class PaginaJogosTest(unittest.TestCase):
    def test_pagina_registrada_mas_nao_e_aba(self):
        self.assertIn("jogos", botoes.PAGINAS)
        self.assertNotIn("pagina:jogos", [b for b, _, _ in botoes.NAV])
        self.assertEqual(botoes.pagina_valida("jogos"), "jogos")
        self.assertEqual(len(botoes.NAV), 6)

    def test_linha_da_tela_inicial_abre_a_pagina(self):
        ls = {l["id"]: l for l in botoes.geometria_resumo()["linhas"]}
        self.assertEqual(ls["jogos"]["destino"], "jogos")
        bs = [b for b in botoes.layout("resumo") if b["id"] == "pagina:jogos"]
        self.assertEqual(len(bs), 1)
        self.assertFalse(bs[0]["visivel"])
        self.assertEqual((bs[0]["x"], bs[0]["y"], bs[0]["w"], bs[0]["h"]),
                         tuple(ls["jogos"][k] for k in ("x", "y", "w", "h")))

    def test_na_pagina_jogos_a_barra_nao_destaca_nenhuma_aba(self):
        c, _ = tela(completo(amp=amp(QUATRO)))
        abas = [b for b in botoes.layout("jogos") if b["visivel"] and b["id"].startswith("pagina:")]
        self.assertEqual(len(abas), 6)
        for b in abas:
            self.assertGreater(px(c, b["x"] + 12, b["y"] + 12), 200, b["id"])  # nenhuma invertida

    def test_a_barra_tem_so_os_botoes_comuns(self):
        ids = [b["id"] for b in botoes.layout("jogos")]
        self.assertEqual(sorted(ids), sorted([b for b, _, _ in botoes.NAV] + ["atualizar"]))

    def test_cartoes_e_conteudo(self):
        _, t = tela(completo(amp=amp(QUATRO)))
        textos = [x[0] for x in t]
        for esperado in ("RAGNAROK", "AMP", "LOGIN", "CHAR", "MAP", "Minecraft", "Terraria", "Palworld", "Valheim",
                         "2/20", "0/8", "parado", "iniciando"):
            self.assertIn(esperado, textos, esperado)
        self.assertIn("fechada", " ".join(textos).lower())  # MAP fechada no `completo`
        self.assertEqual(sum(1 for x in textos if x == "parado"), 1)

    def test_instancias_ligadas_primeiro_depois_por_nome(self):
        _, t = tela(completo(amp=amp(list(reversed(QUATRO)))))
        ys = {x[0]: x[3] for x in t if x[0] in ("Minecraft", "Terraria", "Palworld", "Valheim")}
        self.assertLess(ys["Minecraft"], ys["Terraria"])
        self.assertLess(ys["Terraria"], ys["Palworld"])
        self.assertLess(ys["Palworld"], ys["Valheim"])

    def test_amp_desligado_ou_ausente_nao_aparece(self):
        for b in (None, amp(ativo=False), amp(ativo=None, inventario="ausente")):
            m = completo()
            if b is not None:
                m["amp"] = b
            _, t = tela(m)
            textos = [x[0] for x in t]
            self.assertNotIn("AMP", textos)
            self.assertIn("RAGNAROK", textos)

    def test_amp_ativo_sem_dados(self):
        for b in (amp(erro="amp sem resposta"), amp(inventario="velho", idade_s=300)):
            _, t = tela(completo(amp=b))
            textos = [x[0] for x in t]
            self.assertIn("AMP", textos)
            self.assertIn("sem dados", textos)

    def test_ragnarok_sem_nenhuma_fonte(self):
        _, t = tela({"host": "h", "gerado_em": "2026-11-15T14:32:10-03:00"})
        self.assertIn("sem dados", [x[0] for x in t])

    def test_ragnarok_jogadores_e_portas(self):
        _, t = tela(completo(ragnarok={"jogadores": 7, "parado": False, "idade_s": 3}))
        textos = [x[0] for x in t]
        self.assertIn("7", textos)
        self.assertEqual(textos.count("aberta") + textos.count("FECHADA"), 3)

    def test_ragnarok_parado(self):
        _, t = tela(completo(ragnarok={"jogadores": 2, "parado": True, "idade_s": 600}))
        self.assertTrue([x for x in t if "parado" in x[0].lower()])

    def test_estrito_em_todos_os_casos_e_tamanhos(self):
        muitos = [inst("%08x" % n, "Servidor com nome %d" % n, ("rodando", "parado", "falha", "iniciando", "outro")[n % 5],
                       n, 20, "Modulo %d" % n) for n in range(16)]
        casos = [completo(amp=amp(QUATRO)), completo(amp=amp(muitos)), completo(amp=amp(erro="x")), completo(), {},
                 {"erro": "x"}, completo(amp=amp([])), completo(amp="x"), completo(amp={"ativo": True, "instancias": 3}),
                 completo(amp=amp([inst("1", "N" * 300, "rodando", 10 ** 9, -4, "M" * 200)])),
                 completo(host="h" * 200, amp=amp(muitos), portas=[{"rotulo": "P" * 40, "aberto": False}] * 12)]
        for m in casos:
            for w, h in ((1236, 1648), (800, 1300)):
                tela(m, "jogos", w, h)

    def test_ate_16_instancias_cabem_na_tela_do_kindle(self):
        muitos = [inst("%08x" % n, "Srv %02d" % n, "rodando", n, 20) for n in range(16)]
        _, t = tela(completo(amp=amp(muitos)))
        textos = [x[0] for x in t]
        self.assertTrue(all(("Srv %02d" % n) in textos for n in range(16)))
        for _, _, tam, _ in t:
            self.assertGreaterEqual(tam, 26)  # nada de texto menor que 26 px
        self.assertFalse([x for x in textos if re.fullmatch(r"\+\d+", x)])  # sem a linha "+N": coube tudo

    def test_tela_pequena_corta_com_mais_n_sem_sobrepor_a_barra(self):
        muitos = [inst("%08x" % n, "Srv %02d" % n, "rodando", n, 20) for n in range(16)]
        c, t = tela(completo(amp=amp(muitos)), "jogos", 800, 1100)
        limite = botoes.limite(1100)
        self.assertTrue([x for x in t if re.fullmatch(r"\+\d+", x[0])])
        for texto, _, _, y in t:
            if texto in ("Srv 00", "Srv 15"):
                self.assertLess(y, limite)

    def test_fonte_minima_26(self):
        _, t = tela(completo(amp=amp(QUATRO)))
        self.assertTrue(t)
        for _, _, tam, _ in t:
            self.assertGreaterEqual(tam, 26)

    def test_resumo_usa_a_linha_jogos(self):
        _, t = tela(completo(amp=amp(QUATRO)), "resumo")
        textos = [x[0] for x in t]
        self.assertIn("JOGOS", textos)
        self.assertNotIn("RAGNAROK", textos)

    def test_imagem_do_resumo_muda_com_o_amp(self):
        a = render_png.render_png(completo(amp=amp(QUATRO)), historico(), pagina="resumo")
        b = render_png.render_png(completo(), historico(), pagina="resumo")
        self.assertNotEqual(a, b)
        a = render_png.render_png(completo(amp=amp(QUATRO)), historico(), pagina="jogos")
        b = render_png.render_png(completo(amp=amp(erro="x")), historico(), pagina="jogos")
        self.assertNotEqual(a, b)


class TextoJogosTest(unittest.TestCase):
    def test_linha_jogos_no_resumo(self):
        linhas = render.render_texto(completo(amp=amp(QUATRO)), 60)
        l = [x for x in linhas if x.startswith("Jogos:")]
        self.assertEqual(len(l), 1, linhas)
        self.assertIn("Ragnarok 3", l[0])
        self.assertIn("Minecraft 2/20", l[0])

    def test_sem_amp_a_linha_jogos_so_tem_o_ragnarok(self):
        l = [x for x in render.render_texto(completo(), 60) if x.startswith("Jogos:")]
        self.assertEqual(len(l), 1)
        self.assertNotIn("AMP", l[0])

    def test_linhas_antigas_continuam(self):
        linhas = render.render_texto(completo(), 60)
        self.assertTrue([x for x in linhas if x.startswith("Ragnarok:")])
        self.assertIn("Portas: LOGIN ok CHAR ok MAP FALHA", linhas)

    def test_todo_ascii_e_dentro_das_colunas(self):
        for cols in (20, 38, 80):
            for m in (completo(amp=amp(QUATRO)), completo(amp=amp(erro="x")), completo(), {}):
                for pagina in ("resumo", "jogos"):
                    for l in render.render_texto(m, cols, pagina):
                        self.assertTrue(l.isascii() and l.isprintable(), l)
                        self.assertLessEqual(len(l), cols)

    def test_pagina_jogos_em_texto(self):
        linhas = render.render_texto(completo(amp=amp(QUATRO)), 60, "jogos")
        txt = "\n".join(linhas)
        for esperado in ("RAGNAROK", "LOGIN", "MAP", "AMP", "Minecraft", "2/20", "Valheim", "parado"):
            self.assertIn(esperado, txt, esperado)
        self.assertLess(txt.index("Minecraft"), txt.index("Valheim"))

    def test_pagina_jogos_amp_sem_dados_e_desligado(self):
        txt = "\n".join(render.render_texto(completo(amp=amp(erro="x")), 60, "jogos"))
        self.assertIn("AMP", txt)
        self.assertIn("sem dados", txt)
        txt = "\n".join(render.render_texto(completo(amp=amp(ativo=False)), 60, "jogos"))
        self.assertNotIn("AMP", txt)


class KindleGenericoTest(unittest.TestCase):
    """O Kindle aceita `pagina:<id>` com 1 a 16 letras minusculas: `jogos` entra sem regravar o aparelho."""
    RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def ler(self, nome):
        with open(os.path.join(self.RAIZ, "kindle", "kindle-monitor", nome), encoding="utf-8") as f:
            return f.read()

    def test_id_jogos_casa_com_o_padrao_generico(self):
        for pagina in botoes.PAGINAS:
            self.assertRegex(pagina, r"^[a-z]{1,16}\Z")

    def test_tap_e_loop_usam_o_padrao_generico(self):
        tap, loop = self.ler("tap.sh"), self.ler("loop.sh")
        self.assertIn("''|*[!a-z]*) ;; *) [ ${#v} -le 16 ]", tap)
        self.assertIn("''|*[!a-z]*) ;; *) [ ${#v} -le 16 ]", loop)
        self.assertNotIn("jogos", tap + loop)  # nada de lista fixa de paginas no aparelho


if __name__ == "__main__":
    unittest.main()
