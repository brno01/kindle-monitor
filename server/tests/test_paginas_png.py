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
                if b["tipo"] != "local" or b["id"].startswith("modo:"):
                    continue
                miolo = px(c, b["x"] + 12, b["y"] + 12)  # canto interno, longe do texto
                esperado_escuro = b["id"] == "pagina:" + pagina
                self.assertEqual(miolo < 50, esperado_escuro, (pagina, b["id"]))

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
        self.assertLessEqual(render_png.ALTURA_CABECALHO, 96)
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


if __name__ == "__main__":
    unittest.main()
