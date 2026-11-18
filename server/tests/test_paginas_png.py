import time
import unittest

import _caminho  # noqa: F401
import botoes
import canvas as cv
import render_png
from test_render_png import IO, MINIMO, GpuRamPngTest, cheio, completo, historico, ihdr, pixels

COMANDOS = [{"acao": "gpu-descarregar", "estado": "ok", "quando": "14:31:02", "detalhe": "modelo descarregado"},
            {"acao": "bots-pausar", "estado": "executando", "quando": "14:30:40", "detalhe": ""},
            {"acao": "ollama-reiniciar", "estado": "falhou", "quando": "14:20:11", "detalhe": "timeout de 20 s"}] * 2


def caso_cheio():
    """8 servicos, 4 discos, 2 I/O, 2 redes, GPU ativa, 1 par, 5 comandos recentes."""
    m = cheio() | {"io": IO, "gpu": GpuRamPngTest.ON, "pares": [completo()["pares"][0]], "comandos": COMANDOS[:5]}
    m["discos"] = [{"rotulo": r, "total_b": 10**12, "usado_b": 10**11 * k, "pct": 10.0 * k}
                   for k, r in ((3, "/"), (4, "NAS HD"), (5, "NAS SSD"), (6, "SSD"))]
    return m


def tela(m, pagina, armado=None, w=1236, h=1648, estrito=True):
    c = cv.Canvas(w, h, estrito=estrito)
    render_png.desenhar(c, m, historico(), pagina, armado)
    return c


def px(c, x, y):
    return c.pixels[y * c.largura + x]


class PaginasEstritasTest(unittest.TestCase):
    def test_todas_as_paginas_em_todos_os_casos(self):
        casos = (caso_cheio(), completo(), MINIMO, {}, {"erro": "x"},
                 completo(gpu={"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 2048, "temp_c": 39}),
                 completo(host="h" * 200, servicos=[{"nome": "s" * 300, "ativo": False}] * 12),
                 caso_cheio() | {"pares": [completo()["pares"][0]] * 5})
        for m in casos:
            for pagina in botoes.PAGINAS:
                for armado in (None, "gpu-descarregar"):
                    tela(m, pagina, armado)

    def test_tamanho_pequeno(self):
        for pagina in botoes.PAGINAS:
            tela(caso_cheio(), pagina, "bots-pausar", 800, 1300)

    def test_comandos_vazios_ou_invalidos(self):
        for lista in (None, [], "x", [1, None, {}], [{"acao": "a" * 300, "estado": "???", "quando": 5, "detalhe": "d" * 400}]):
            tela(completo(comandos=lista), "comandos")

    def test_pagina_ou_armado_invalidos_nao_quebram(self):
        tela(completo(), "zzz", "xpto")
        tela(completo(), None, None)

    def test_tempo_de_cada_pagina(self):
        for pagina in botoes.PAGINAS:
            melhor = float("inf")
            for _ in range(3):
                t0 = time.monotonic()
                render_png.render_png(caso_cheio(), historico(), pagina=pagina)
                melhor = min(melhor, time.monotonic() - t0)
            self.assertLess(melhor, 2.0, pagina)

    def test_render_png_devolve_png_do_tamanho(self):
        for pagina in botoes.PAGINAS:
            self.assertEqual(ihdr(render_png.render_png(completo(), historico(), pagina=pagina)), (1236, 1648))


class BotoesDesenhadosTest(unittest.TestCase):
    def test_botoes_nas_coordenadas_do_layout(self):
        for pagina in botoes.PAGINAS:
            c = tela(caso_cheio(), pagina, "gpu-descarregar")
            for b in botoes.layout(pagina, "gpu-descarregar"):
                if not b["visivel"]:
                    continue
                cx = b["x"] + b["w"] // 2
                self.assertLess(px(c, cx, b["y"] + 1), 100, (pagina, b["id"], "borda de cima"))
                self.assertLess(px(c, cx, b["y"] + b["h"] - 2), 100, (pagina, b["id"], "borda de baixo"))
                self.assertLess(px(c, b["x"] + 1, b["y"] + b["h"] // 2), 100, (pagina, b["id"], "borda esquerda"))
                self.assertLess(px(c, b["x"] + b["w"] - 2, b["y"] + b["h"] // 2), 100, (pagina, b["id"], "direita"))
                # a faixa de 16 px ao redor e vazia (nada encosta no botao)
                self.assertEqual(px(c, cx, b["y"] - 4), 255, (pagina, b["id"], "acima"))
                self.assertEqual(px(c, b["x"] - 4, b["y"] + b["h"] // 2), 255, (pagina, b["id"], "a esquerda"))

    def test_nav_pagina_atual_invertida(self):
        for pagina in botoes.PAGINAS:
            c = tela(completo(), pagina)
            for b in botoes.layout(pagina):
                if not b["visivel"] or b["tipo"] != "local" or b["id"].startswith("modo:"):
                    continue
                miolo = px(c, b["x"] + 12, b["y"] + 12)  # canto interno, longe do texto
                esperado_escuro = b["id"] == "pagina:" + pagina
                self.assertEqual(miolo < 50, esperado_escuro, (pagina, b["id"]))

    def test_barra_com_seis_abas_sem_atualizar(self):
        for pagina in botoes.PAGINAS:
            abas = [b for b in botoes.layout(pagina) if b["visivel"] and b["id"].startswith("pagina:")]
            self.assertEqual(len(abas), 6, pagina)
            self.assertNotIn("atualizar", [b["id"] for b in botoes.layout(pagina) if b["visivel"]])

    def test_invisiveis_nao_sao_desenhados(self):
        c = tela(completo(), "aparelhos")
        for b in botoes.layout("aparelhos"):
            if not b["visivel"]:
                self.assertEqual(px(c, b["x"] + 1, b["y"] + 1), 255, b["id"])

    def test_botao_armado_invertido_e_demais_claros(self):
        c = tela(completo(), "comandos", "gpu-descarregar")
        for b in botoes.layout("comandos", "gpu-descarregar"):
            if b["tipo"] != "comando":
                continue
            miolo = px(c, b["x"] + 14, b["y"] + 14)
            self.assertEqual(miolo < 50, b["armado"], b["id"])
        b = [b for b in botoes.layout("comandos", "gpu-descarregar") if b["armado"]][0]
        # amostra no centro do retangulo: escuro em volta do texto branco
        escuros = sum(1 for dx in range(-200, 200, 4) for dy in (-60, 60) if px(c, b["x"] + b["w"] // 2 + dx, b["y"] + b["h"] // 2 + dy) < 50)
        self.assertGreater(escuros, 80)

    def test_armado_muda_a_imagem(self):
        a = render_png.render_png(completo(), None, pagina="comandos")
        b = render_png.render_png(completo(), None, pagina="comandos", armado="bots-pausar")
        self.assertNotEqual(a, b)

    def test_armado_ignorado_fora_de_comandos(self):
        a = render_png.render_png(completo(), None, pagina="resumo")
        b = render_png.render_png(completo(), None, pagina="resumo", armado="bots-pausar")
        self.assertEqual(a, b)

    def test_paginas_diferentes(self):
        imgs = {p: render_png.render_png(caso_cheio(), historico(), pagina=p) for p in botoes.PAGINAS}
        self.assertEqual(len(set(imgs.values())), len(botoes.PAGINAS))

    def test_ultimos_comandos_mudam_a_imagem(self):
        sem = render_png.render_png(completo(), None, pagina="comandos")
        com = render_png.render_png(completo(comandos=COMANDOS[:3]), None, pagina="comandos")
        self.assertNotEqual(sem, com)
        self.assertEqual(render_png.render_png(completo(comandos=[]), None, pagina="comandos"), sem)


class ResumoTest(unittest.TestCase):
    def test_cabecalho_compacto_sem_faixa_preta(self):
        larg, alt, linhas = pixels(render_png.render_png(completo(), historico()))
        self.assertLessEqual(render_png.ALTURA_CABECALHO - botoes.BARRA_KINDLE_H, 96)  # a barra do Kindle fica acima
        self.assertEqual(linhas[5][5], 255)
        self.assertEqual(linhas[50][larg // 2], 255)

    def test_margens_laterais_vazias(self):
        for pagina in botoes.PAGINAS:
            larg, alt, linhas = pixels(render_png.render_png(caso_cheio(), historico(), pagina=pagina))
            for y in range(alt):
                self.assertEqual(min(linhas[y][:40]), 255, (pagina, y))
                self.assertEqual(min(linhas[y][larg - 40:]), 255, (pagina, y))

    def test_resumo_tem_numeros_grandes(self):
        # o numero do CPU (72 px na v5) ocupa muita altura contigua de tinta
        larg, alt, linhas = pixels(render_png.render_png(completo(cpu={"pct": 56.0}), historico()))
        topo = None
        seq = 0
        for y in range(100, 600):
            if min(linhas[y][70:200]) < 100:
                seq += 1
                topo = max(topo or 0, seq)
            else:
                seq = 0
        self.assertGreater(topo, 48)

    def test_servicos_com_falha_aparecem(self):
        a = render_png.render_png(completo(servicos=[{"nome": "a.service", "ativo": True}]), None)
        b = render_png.render_png(completo(servicos=[{"nome": "a.service", "ativo": False}]), None)
        self.assertNotEqual(a, b)



# ------------------------------------------------------------------ pagina claude

from datetime import datetime  # noqa: E402


def _janela(pct, volta_em=1_794_010_000, renovado=False):
    return {"pct": pct, "volta_em": volta_em, "renovado": renovado}


def _tok(total, custo=1.5):
    return {"entrada": total // 4, "saida": total // 8, "cache_leitura": total // 2, "cache_escrita": total // 8,
            "total": total, "custo_usd": custo}


def dados_claude(**extra):
    m = {"host": "atheron", "gerado_em": "2026-11-16T14:32:10-03:00",
         "claude": {"limites": {"cinco_horas": _janela(34.0), "semanal": _janela(91.0), "idade_s": 30, "velho": False},
                    "tokens": {"hoje": _tok(3_100_000), "sete_dias": _tok(21_000_000, 12.3), "idade_s": 30,
                               "velho": False}},
         "s10": {"bateria": {"nivel": 87, "status": "charging", "temperatura_c": 36.5, "saude": "good"},
                 "caminhos": {"usb": True, "adb_sem_fio": False, "tailscale": True, "ssh_termux": True, "vnc": None},
                 "avisos": [], "idade_s": 20, "velho": False}}
    return m | extra


def textos(m, w=1236, h=1648):
    """Textos desenhados na pagina claude (canvas estrito: nada fora da imagem)."""
    caps = []
    original = cv.Canvas.texto

    def espia(self, x, y, texto, *a, **k):
        caps.append(texto)
        return original(self, x, y, texto, *a, **k)

    cv.Canvas.texto = espia
    try:
        tela(m, "claude", w=w, h=h)
    finally:
        cv.Canvas.texto = original
    return caps


class PaginaClaudeTest(unittest.TestCase):
    def test_dados_completos(self):
        t = " | ".join(textos(dados_claude()))
        for esperado in ("5h", "34%", "volta", "S10", "91%"):
            self.assertIn(esperado, t)

    def test_tamanho_pequeno_e_alternativo(self):
        for w, h in ((800, 1300), (1072, 1448)):
            textos(dados_claude(), w, h)

    def test_renovado(self):
        m = dados_claude()
        m["claude"]["limites"]["cinco_horas"] = _janela(80.0, renovado=True)
        t = " | ".join(textos(m))
        self.assertIn("0%", t)
        self.assertIn("renovado", t)
        self.assertNotIn("80%", t)

    def test_noventa_por_cento_em_negrito_preto(self):
        c = tela(dados_claude(), "claude")
        self.assertTrue(any(v < 40 for v in c.pixels))  # smoke; o texto 91% existe (ver test_dados_completos)

    def test_velho_mostra_idade(self):
        m = dados_claude()
        m["claude"]["limites"] |= {"velho": True, "idade_s": 7200}
        m["s10"] |= {"velho": True, "idade_s": 600}
        t = " | ".join(textos(m))
        self.assertIn("ha 2 h", t)
        self.assertIn("S10 sem dados ha 10 min", t)

    def test_caminho_none_ou_estranho_desenha_interrogacao(self):
        t = textos(dados_claude())
        self.assertIn("?", t)  # vnc None
        m = dados_claude()
        m["s10"]["caminhos"] = {"usb": "sim", "vnc": 3}
        self.assertIn("?", textos(m))

    def test_sem_chaves_desligado(self):
        t = " | ".join(textos({"host": "h", "gerado_em": "2026-11-16T14:32:10-03:00"}))
        self.assertIn("desligado na config", t)

    def test_so_um_cartao(self):
        m = dados_claude()
        del m["s10"]
        t = " | ".join(textos(m))
        self.assertIn("5h", t)
        self.assertNotIn("desligado", t)
        m = dados_claude()
        del m["claude"]
        self.assertIn("S10", " | ".join(textos(m)))

    def test_nd_nos_dois_nao_levanta(self):
        for v in ({"erro": "n/d"}, None, "x", 5, {}, {"limites": 3, "tokens": []}):
            textos({"claude": v, "s10": v})

    def test_valores_estranhos_nao_levantam(self):
        m = dados_claude()
        m["s10"]["bateria"] = {"nivel": "x", "status": 5, "temperatura_c": True, "saude": None}
        m["s10"]["avisos"] = ["temperatura", "carga_cheia", "outro_codigo", 7, None]
        m["s10"]["caminhos"] = {"usb": [], "adb_sem_fio": {}}
        t = " | ".join(textos(m))
        self.assertIn("temperatura alta", t)
        self.assertIn("100% ha horas: proteger bateria", t)
        self.assertIn("outro_codigo", t)
        m["claude"]["limites"]["cinco_horas"] = {"pct": "x", "volta_em": None, "renovado": 1}
        m["claude"]["tokens"]["hoje"] = {"total": "x", "custo_usd": None}
        textos(m)

    def test_status_da_bateria(self):
        for st, txt in (("charging", "carregando"), ("full", "cheia"), ("discharging", "descarregando"),
                        ("not_charging", "descarregando")):
            m = dados_claude()
            m["s10"]["bateria"]["status"] = st
            self.assertIn(txt, " | ".join(textos(m)))
        m = dados_claude()
        m["s10"]["bateria"]["status"] = "unknown"
        t = " | ".join(textos(m))
        for txt in ("carregando", "cheia", "descarregando"):
            self.assertNotIn(txt, t)

    def test_texto_so_ascii(self):
        for t in textos(dados_claude()):
            self.assertTrue(all(ord(ch) < 128 or ch in "°·" for ch in t), t)


class HelpersClaudeTest(unittest.TestCase):
    def test_tokens_txt(self):
        self.assertEqual(render_png._tokens_txt(950), "950")
        self.assertEqual(render_png._tokens_txt(12_000), "12 k")
        self.assertEqual(render_png._tokens_txt(3_100_000), "3,1 M")
        self.assertEqual(render_png._tokens_txt(0), "0")
        self.assertEqual(render_png._tokens_txt(999_999), "1,0 M")
        self.assertEqual(render_png._tokens_txt(None), "n/d")

    def test_volta_txt(self):
        agora = datetime(2026, 11, 16, 12, 0).timestamp()  # segunda
        hoje = datetime(2026, 11, 16, 14, 30).timestamp()
        self.assertEqual(render_png._volta_txt(hoje, agora), "volta 14:30")
        qui = datetime(2026, 11, 19, 2, 0).timestamp()
        self.assertEqual(render_png._volta_txt(qui, agora), "volta qui 02:00")
        dom = datetime(2026, 11, 22, 23, 5).timestamp()
        self.assertEqual(render_png._volta_txt(dom, agora), "volta dom 23:05")
        self.assertEqual(render_png._volta_txt(None, agora), "")


class NavClaudeTest(unittest.TestCase):
    def test_seis_botoes_dentro_da_barra_sem_sobreposicao(self):
        nav = [b for b in botoes.layout("resumo") if b["visivel"] and b["y"] == botoes.nav_topo()]
        self.assertEqual(len(nav), 6)
        self.assertEqual(nav[-1]["id"], "pagina:comandos")
        self.assertIn("pagina:claude", [b["id"] for b in nav])
        for a, b in zip(nav, nav[1:]):
            self.assertLessEqual(a["x"] + a["w"], b["x"])
        self.assertLessEqual(nav[-1]["x"] + nav[-1]["w"], 1236 - botoes.MARGEM)

    def test_rotulo_cabe_no_botao(self):
        for nav in (b for b in botoes.layout("resumo") if b["visivel"] and b["y"] == botoes.nav_topo()):
            self.assertLessEqual(cv.Canvas.medir(nav["rotulo"], "sans-bold", 26), nav["w"] - 16, nav["id"])


class NaoFinitosClaudeTest(unittest.TestCase):
    RUINS = (float("inf"), float("-inf"), float("nan"))

    def test_helpers(self):
        for v in self.RUINS:
            self.assertEqual(render_png._tokens_txt(v), "n/d")
            self.assertEqual(render_png._custo_txt(v), "n/d")
            self.assertEqual(render_png._idade_txt(v), "")
            self.assertEqual(render_png._volta_txt(v, 0), "")

    def test_png_sem_excecao_e_sem_inf_nan(self):
        for v in self.RUINS:
            m = dados_claude()
            m["claude"]["limites"]["cinco_horas"] = {"pct": v, "volta_em": v, "renovado": False}
            m["claude"]["limites"] |= {"velho": True, "idade_s": v}
            m["claude"]["tokens"]["hoje"] = {"entrada": v, "saida": v, "cache_leitura": v, "cache_escrita": v,
                                              "total": v, "custo_usd": v}
            m["s10"]["bateria"] = {"nivel": v, "status": "charging", "temperatura_c": v, "saude": "good"}
            m["s10"] |= {"velho": True, "idade_s": v}
            t = " | ".join(textos(m)).lower()
            self.assertNotIn("inf", t)
            self.assertNotIn("nan", t)
            self.assertIn("n/d", t)
            import render
            for l in render.render_texto(m, 60, pagina="claude"):
                self.assertNotIn("inf", l.lower())
                self.assertNotIn("nan", l.lower())


if __name__ == "__main__":
    unittest.main()
