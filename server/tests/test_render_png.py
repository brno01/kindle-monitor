import struct
import time
import unittest
import zlib

import _caminho  # noqa: F401
import canvas as cv
import render_png


def completo(**extra):
    m = {
        "host": "atheron",
        "gerado_em": "2026-11-15T14:32:10-03:00",
        "cpu": {"pct": 56.0},
        "carga": {"1m": 0.52, "5m": 0.48, "15m": 0.4},
        "ram": {"total_kb": 32000000, "usado_kb": 12000000, "pct": 37.5},
        "swap": {"total_kb": 8000000, "usado_kb": 1000000, "pct": 12.5},
        "uptime": {"segundos": 90061},
        "temp_cpu": {"c": 55.0},
        "gpu": {"util_pct": 12, "mem_usada_mb": 3000, "mem_total_mb": 8192, "temp_c": 45},
        "discos": [
            {"rotulo": "/", "caminho": "/", "total_b": 500 * 10**9, "usado_b": 200 * 10**9, "pct": 40.0},
            {"rotulo": "NAS", "caminho": "/mnt/nas", "total_b": 4 * 10**12, "usado_b": 3 * 10**12, "pct": 75.0},
        ],
        "servicos": [{"nome": "ragnarok.service", "ativo": True}, {"nome": "cerberus-balancer.service", "ativo": False},
                     {"nome": "x.service", "erro": "n/d"}],
        "ragnarok": {"jogadores": 3, "parado": False, "idade_s": 4},
        "portas": [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True},
                   {"rotulo": "MAP", "aberto": False}],
        "pares": [{"nome": "nomad", "ok": True, "metricas": {
            "host": "nomad", "cpu": {"pct": 20.0}, "ram": {"pct": 61.0}, "gpu": {"util_pct": 3},
            "uptime": {"segundos": 4000}, "temp_cpu": {"c": 48.0}}},
            {"nome": "fora", "ok": False}],
    }
    m.update(extra)
    return m


def historico(n=60):
    return {"cpu": [(i * 7) % 100 for i in range(n)], "ram": [40 + i % 5 for i in range(n)],
            "gpu": [i % 30 for i in range(n)]}


def cheio():
    return completo(
        discos=[{"rotulo": "disco%d" % i, "caminho": "/", "total_b": 10**12, "usado_b": 5 * 10**11, "pct": 50.0 + i}
                for i in range(3)],
        servicos=[{"nome": "servico-numero-%d.service" % i, "ativo": i % 3 != 0} for i in range(8)],
    )


MINIMO = {"host": "h", "gerado_em": "2026-11-15T09:05:00-03:00", "cpu": {"pct": 1.0}, "ram": {"pct": 2.0},
          "uptime": {"segundos": 60}}


def ihdr(dados):
    assert dados[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", dados[16:24])


def pixels(dados):
    larg, alt = ihdr(dados)
    pos, idat = 8, b""
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        if tipo == b"IDAT":
            idat += dados[pos + 8:pos + 8 + n]
        pos += 12 + n
    bruto = zlib.decompress(idat)
    return larg, alt, [bruto[y * (larg + 1) + 1:(y + 1) * (larg + 1)] for y in range(alt)]


class RenderPngTest(unittest.TestCase):
    def test_dimensoes_padrao(self):
        self.assertEqual(ihdr(render_png.render_png(completo(), historico())), (1236, 1648))

    def test_dimensoes_customizadas(self):
        self.assertEqual(ihdr(render_png.render_png(completo(), historico(), 800, 1100)), (800, 1100))

    def test_dados_minimos(self):
        for m in (MINIMO, {}, {"erro": "x"}):
            self.assertEqual(ihdr(render_png.render_png(m, None)), (1236, 1648))

    def test_tudo_com_erro(self):
        nd = {"erro": "n/d"}
        m = {"host": "h", "cpu": nd, "ram": nd, "swap": nd, "carga": nd, "uptime": nd, "gpu": nd,
             "discos": [nd, {"rotulo": "x", "erro": "n/d"}], "servicos": nd, "ragnarok": nd, "portas": nd,
             "pares": [{"nome": "p", "ok": True, "metricas": {"cpu": nd}}]}
        self.assertEqual(ihdr(render_png.render_png(m, {"cpu": [None, None]})), (1236, 1648))

    def test_cabecalho_compacto_e_botoes_no_rodape(self):
        # v4: sem faixa preta (o cabecalho agora e compacto) e a barra de navegacao fica no rodape
        larg, alt, linhas = pixels(render_png.render_png(completo(), historico()))
        self.assertEqual(linhas[3][5], 255)
        self.assertEqual(linhas[60][larg // 2], 255)
        self.assertEqual(linhas[alt - 2][larg // 2], 255)
        self.assertEqual(linhas[alt - 90][100], 0)  # botao Inicio (selecionado) da barra de navegacao

    def test_cabecalho_tem_texto_escuro(self):
        _, _, linhas = pixels(render_png.render_png(completo(), historico()))
        self.assertTrue(any(min(linhas[y][:400]) < 60 for y in range(20, 90)))

    def test_margens_laterais_vazias_abaixo_do_cabecalho(self):
        larg, alt, linhas = pixels(render_png.render_png(cheio(), historico()))
        for y in range(render_png.ALTURA_CABECALHO + 1, alt):
            self.assertEqual(min(linhas[y][:40]), 255, y)
            self.assertEqual(min(linhas[y][larg - 40:]), 255, y)

    def test_sem_texto_fora_da_imagem(self):
        for m in (completo(), cheio(), MINIMO, completo(host="h" * 200, servicos=[
                {"nome": "s" * 300, "ativo": False}], discos=[{"rotulo": "R" * 80, "pct": 5.0}] * 3)):
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, m, historico())  # (pagina resumo) levanta ForaDosLimites se algo sair

    def test_tela_cheia_cabe_sem_cortar(self):
        c = cv.Canvas(1236, 1648, estrito=True)
        render_png.desenhar(c, cheio(), historico())
        self.assertEqual(c.pixels[-1], 255)

    def test_cheio_com_muitos_pares_ainda_cabe(self):
        par = {"nome": "p", "ok": True, "metricas": {"cpu": {"pct": 1.0}, "ram": {"pct": 2.0}}}
        c = cv.Canvas(1236, 1648, estrito=True)
        render_png.desenhar(c, cheio() | {"pares": [par] * 5}, historico())

    def test_tamanho_pequeno_estrito(self):
        c = cv.Canvas(800, 1300, estrito=True)
        render_png.desenhar(c, cheio(), historico())

    def test_so_usa_poucos_tons_de_chapado(self):
        _, _, linhas = pixels(render_png.render_png(completo(), historico()))
        todos = b"".join(linhas)
        for tom in (0, 255):
            self.assertIn(tom, todos)

    def test_pilulas_diferem_aberta_e_fechada(self):
        a = render_png.render_png(completo(portas=[{"rotulo": "LOGIN", "aberto": True}]), None)
        b = render_png.render_png(completo(portas=[{"rotulo": "LOGIN", "aberto": False}]), None)
        self.assertNotEqual(a, b)

    def test_parado_muda_a_imagem(self):
        a = render_png.render_png(completo(), None)
        b = render_png.render_png(completo(ragnarok={"jogadores": 3, "parado": True, "idade_s": 600}), None)
        self.assertNotEqual(a, b)

    def test_sem_historico_funciona(self):
        self.assertEqual(ihdr(render_png.render_png(completo(), None)), (1236, 1648))
        self.assertEqual(ihdr(render_png.render_png(completo(), {})), (1236, 1648))

    def test_historico_vem_de_metricas_quando_omitido(self):
        a = render_png.render_png(completo(historico=historico()), None, pagina="detalhes")
        b = render_png.render_png(completo(), None, pagina="detalhes")
        self.assertNotEqual(a, b)

    def test_tempo_de_render(self):
        # best of 3 with a loose bound: a busy host (load 16 seen on the atheron) must not flake this
        melhor = float("inf")
        for _ in range(3):
            t0 = time.monotonic()
            render_png.render_png(cheio(), historico())
            melhor = min(melhor, time.monotonic() - t0)
        self.assertLess(melhor, 2.0)

    def test_nao_ascii_nao_quebra(self):
        render_png.render_png(completo(host="café 中文 ☃"), None)


CL = {"limites": {"cinco_horas": {"pct": 42.0, "volta_em": 1_794_000_000, "renovado": False},
                  "semanal": {"pct": 18.0, "volta_em": 1_794_500_000, "renovado": False},
                  "idade_s": 30, "velho": False},
      "tokens": {"erro": "n/d"}}
S10 = {"versao": 1, "gerado_em": "2026-11-15T14:32:10-03:00",
       "bateria": {"nivel": 87, "status": "charging", "temperatura_c": 31.0, "saude": "good"},
       "caminhos": {"usb": True, "adb_sem_fio": False, "tailscale": True, "ssh_termux": True, "vnc": None},
       "avisos": [], "idade_s": 20, "velho": False}


class CartoesClaudeS10Test(unittest.TestCase):
    def test_estados_degradados_nao_quebram(self):
        estados = [{"claude": {"limites": {"erro": "n/d"}, "tokens": {"erro": "n/d"}}},
                   {"claude": {"limites": {"cinco_horas": None, "semanal": None, "idade_s": 1, "velho": False}}},
                   {"claude": {"limites": {"cinco_horas": {"pct": 77.0, "renovado": True},
                                           "semanal": {"pct": float("nan")}}}},
                   {"claude": "x"}, {"s10": {"erro": "n/d"}}, {"s10": "x"},
                   {"s10": dict(S10, velho=True)}, {"s10": dict(S10, bateria=None)},
                   {"s10": dict(S10, bateria={"nivel": None, "status": 5}, caminhos={"usb": 1, "vnc": "x"})},
                   {"s10": dict(S10, bateria={"nivel": 250, "status": "full"})}]
        for e in estados:
            m = completo(**e)
            self.assertEqual(ihdr(render_png.render_png(m, historico())), (1236, 1648))
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._card_claude(c, m.get("claude"), 24, 100, 1188, render_png.CLAUDE_H)
            render_png._card_s10(c, m.get("s10"), 24, 640, 1188, render_png._h_s10(m.get("s10")))

    def test_inteiro_gigante_vira_nd_sem_estourar(self):
        self.assertEqual(render_png._tokens_txt(10 ** 400), "n/d")
        dados = render_png.render_png(completo(claude=CL, s10=dict(S10, bateria={"nivel": 10 ** 400})), historico())
        self.assertEqual(ihdr(dados), (1236, 1648))

    def test_card_com_limites_e_tokens_velhos_mostra_as_duas_idades(self):
        textos = []
        orig = cv.Canvas.texto

        def espia(self, x, y, t, *a, **k):
            textos.append(t)
            return orig(self, x, y, t, *a, **k)
        tok = {"hoje": {"entrada": 1, "saida": 2, "cache_leitura": 3, "cache_escrita": 4, "total": 10, "custo_usd": 1.0},
               "sete_dias": {"entrada": 1, "saida": 2, "cache_leitura": 3, "cache_escrita": 4, "total": 70,
                             "custo_usd": 7.0}, "idade_s": 2 * 86400, "velho": True}
        cl = {"limites": dict(CL["limites"], idade_s=3 * 3600, velho=True), "tokens": tok}
        cv.Canvas.texto = espia
        try:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._card_claude(c, cl, 24, 100, 1188, render_png.CLAUDE_H)
        finally:
            cv.Canvas.texto = orig
        self.assertIn("ha 3 h", textos)
        self.assertIn("tokens ha 48 h", textos)

    def test_texto_so_ascii_grau_e_ponto_medio(self):
        textos = []
        orig = cv.Canvas.texto

        def espia(self, x, y, t, *a, **k):
            textos.append(t)
            return orig(self, x, y, t, *a, **k)
        cv.Canvas.texto = espia
        try:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._card_claude(c, CL, 24, 100, 1188, render_png.CLAUDE_H)
            render_png._card_s10(c, S10, 24, 640, 1188, render_png._h_s10(S10))
        finally:
            cv.Canvas.texto = orig
        txt = "|".join(textos)
        self.assertIn("42%", txt)
        self.assertIn("87%", txt)
        self.assertIn("carregando", txt)
        self.assertTrue(all(ord(ch) < 128 or ch in "\u00b0\u00b7" for ch in txt))

    def test_renovado_mostra_zero(self):
        self.assertEqual(render_png._pct_txt({"pct": 0.0, "renovado": True}), "0%")
        self.assertEqual(render_png._pct_txt({"pct": 77.0, "renovado": True}), "0%")
        self.assertEqual(render_png._pct_txt(None), "n/d")


def _detalhe_atheron(m):
    return render_png._linhas_resumo(m, [], None, [])[0]["detalhe"]


class GpuRamPngTest(unittest.TestCase):
    OFF = {"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 2048, "temp_c": 39}
    ON = {"util_pct": 35, "mem_usada_mb": 900, "mem_total_mb": 2048, "temp_c": 50}

    def test_dimensoes_e_gpu_desativada_so_no_detalhe_do_atheron(self):
        off = render_png.render_png(completo(gpu=self.OFF), historico())
        on = render_png.render_png(completo(gpu=self.ON), historico())
        self.assertEqual(ihdr(off), (1236, 1648))
        self.assertEqual(ihdr(on), (1236, 1648))
        self.assertIn("GPU desativada", _detalhe_atheron(completo(gpu=self.OFF)))
        self.assertNotIn("GPU", _detalhe_atheron(completo(gpu=self.ON)))

    def test_gpu_desativada_sem_mem_nula(self):
        g = {"util_pct": 0, "mem_usada_mb": None, "mem_total_mb": None, "temp_c": None}
        self.assertEqual(ihdr(render_png.render_png(completo(gpu=g), historico())), (1236, 1648))

    def test_uso_de_vram_sem_util_nao_conta_como_desativada(self):
        a = {"util_pct": 0, "mem_usada_mb": 100, "mem_total_mb": 2048, "temp_c": 40}
        self.assertNotIn("GPU", _detalhe_atheron(completo(gpu=a)))
        self.assertIn("GPU desativada", _detalhe_atheron(completo(gpu=self.OFF)))

    def test_ram_com_valor_e_disco_tier_state(self):
        m = completo(ram={"total_kb": 20331012, "usado_kb": 7763836, "pct": 38.2},
                     discos=[{"rotulo": "NAS SSD", "total_b": 256 * 2**30, "usado_b": 200 * 2**30, "pct": 78.1,
                              "base": 1024, "parado": True}])
        self.assertEqual(ihdr(render_png.render_png(m, historico())), (1236, 1648))

    def test_tamanho_binario(self):
        self.assertEqual(render_png._tamanho(7763836 * 1024, 20331012 * 1024, 1024), "7.4/19.4 GB")  # v5: sem espacos ao redor da barra (cabe nos tiles)
        self.assertEqual(render_png._tamanho(33 * 10**9, 42 * 10**9), "33/42 GB")
        self.assertEqual(render_png._tamanho(373 * 10**9, 932 * 10**9), "373/932 GB")


IO = {
    "discos": [{"rotulo": "NVMe", "dev": "nvme0n1", "leitura_bps": 2.1 * 1024 ** 2, "escrita_bps": 0.8 * 1024 ** 2},
               {"rotulo": "HD", "dev": "sda", "leitura_bps": 0.0, "escrita_bps": 0.1 * 1024 ** 2}],
    "redes": [{"rotulo": "LAN", "if": "enp2s0f1", "rx_bps": 1.2 * 1024 ** 2, "tx_bps": 0.3 * 1024 ** 2},
              {"rotulo": "Tailnet", "if": "tailscale0", "rx_bps": 40 * 1024, "tx_bps": 12 * 1024}],
}


class IoPngTest(unittest.TestCase):
    def test_bloco_io_muda_a_imagem_e_mantem_dimensoes(self):
        sem = render_png.render_png(completo(), historico(), pagina="detalhes")
        com = render_png.render_png(completo(io=IO), historico(), pagina="detalhes")
        self.assertEqual(ihdr(com), (1236, 1648))
        self.assertNotEqual(sem, com)

    def test_io_vazio_ou_invalido_nao_desenha_nem_quebra(self):
        base = render_png.render_png(completo(), historico())
        self.assertEqual(render_png.render_png(completo(io={"discos": [], "redes": []}), historico()), base)
        for io in ({"erro": "n/d"}, "x", {"discos": "x", "redes": [1, None]},
                   {"discos": [{"rotulo": "A"}], "redes": [{"rotulo": "B", "rx_bps": None, "tx_bps": -1}]}):
            self.assertEqual(ihdr(render_png.render_png(completo(io=io), historico())), (1236, 1648))

    def test_nada_fora_dos_limites_com_io(self):
        for m in (completo(io=IO), cheio() | {"io": IO},
                  cheio() | {"io": IO, "gpu": GpuRamPngTest.ON, "pares": [completo()["pares"][0]]},
                  completo(io={"discos": [dict(IO["discos"][0], rotulo="R" * 16, leitura_bps=1023.9 * 1024 ** 4)],
                               "redes": IO["redes"]})):
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, m, historico())

    def test_caso_cheio_com_io_cabe_na_pagina_detalhes_sem_omitir_blocos(self):
        # v5: a pagina detalhes empilha blocos de altura fixa; nada pode ser descartado por falta de espaco
        import botoes
        import servicos
        m = cheio() | {"io": IO, "gpu": GpuRamPngTest.ON, "pares": [completo()["pares"][0]]}
        w = 1236 - 2 * render_png.MARGEM
        blocos = render_png._blocos_detalhes(cv.Canvas(8, 8), m, servicos.itens_de(m), w, historico())
        total = sum(b[0] for b in blocos) + render_png.GAP * (len(blocos) - 1)
        self.assertLessEqual(total, botoes.limite(1648) - botoes.TOPO)
        self.assertGreaterEqual(len(blocos), 6)

    def test_margens_laterais_vazias_com_io(self):
        larg, alt, linhas = pixels(render_png.render_png(cheio() | {"io": IO}, historico()))
        for y in range(render_png.ALTURA_CABECALHO + 1, alt):
            self.assertEqual(min(linhas[y][:40]), 255, y)
            self.assertEqual(min(linhas[y][larg - 40:]), 255, y)

    def test_tempo_de_render_com_io(self):
        melhor = float("inf")
        for _ in range(3):
            t0 = time.monotonic()
            render_png.render_png(cheio() | {"io": IO}, historico())
            melhor = min(melhor, time.monotonic() - t0)
        self.assertLess(melhor, 2.0)


class CartaoAtencaoAlertasTest(unittest.TestCase):
    """O cartao ATENCAO usa a lista do motor `alertas` (nao so os servicos)."""

    @staticmethod
    def _sem_problemas(**extra):
        m = completo(servicos=[{"nome": "ragnarok.service", "ativo": True}],
                     portas=[{"rotulo": "MAP", "aberto": True}], pares=[])
        m.update(extra)
        return m

    @staticmethod
    def _desenhar(m, pagina="resumo"):
        textos, cartoes = [], []
        orig_t, orig_c = cv.Canvas.texto, render_png._card_atencao

        def espia_t(self, x, y, t, *a, **k):
            textos.append(t)
            return orig_t(self, x, y, t, *a, **k)

        def espia_c(c, atencao, x, y, w, h):
            cartoes.append((x, y, w, h))
            return orig_c(c, atencao, x, y, w, h)
        cv.Canvas.texto, render_png._card_atencao = espia_t, espia_c
        try:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, m, historico(), pagina=pagina)
        finally:
            cv.Canvas.texto, render_png._card_atencao = orig_t, orig_c
        return c, textos, cartoes

    def test_disco_a_91_aparece_e_nao_diz_tudo_em_ordem(self):
        disco = {"rotulo": "/", "caminho": "/", "total_b": 500 * 10**9, "usado_b": 455 * 10**9, "pct": 91.0}
        _, textos, _ = self._desenhar(self._sem_problemas(discos=[disco]))
        self.assertIn("ATENCAO (1)", textos)
        self.assertTrue(any(t.startswith("Disco / 91%") for t in textos), textos)
        self.assertNotIn("Tudo em ordem", textos)

    def test_sem_alertas_mantem_tudo_em_ordem(self):
        _, textos, _ = self._desenhar(self._sem_problemas())
        self.assertIn("Tudo em ordem", textos)
        self.assertIn("ATENCAO", textos)

    def test_12_alertas_mostram_6_e_mais_6(self):
        discos = [{"rotulo": "d%d" % i, "caminho": "/mnt/d%d" % i, "total_b": 10**12, "usado_b": 95 * 10**10,
                   "pct": 95.0} for i in range(12)]
        m = self._sem_problemas(discos=discos)
        self.assertEqual(len(render_png._atencao(m, None)), 12)
        _, textos, cartoes = self._desenhar(m)
        self.assertIn("ATENCAO (12)", textos)
        self.assertEqual(len([t for t in textos if t.startswith("Disco d")]), 6)
        self.assertIn("+6", textos)
        self.assertEqual(cartoes[0][3], render_png._h_atencao(12))
        self.assertEqual(render_png._h_atencao(12), render_png.ATENCAO_TITULO + 7 * render_png.ATENCAO_LINHA + 14)

    def test_cabecalho_invertido_so_com_item_critico(self):
        def canto(disco_pct):
            disco = {"rotulo": "/", "caminho": "/", "total_b": 10**12, "usado_b": 10**11, "pct": disco_pct}
            c, _, cartoes = self._desenhar(self._sem_problemas(discos=[disco]))
            x, y, _, _ = cartoes[0]
            return c.pixels[(y + 20) * c.largura + x + 400]
        self.assertEqual(canto(95.0), 0)   # critico: faixa preta
        self.assertEqual(canto(91.0), 255)  # aviso: cabecalho normal

    def test_formas_por_nivel_sao_distintas(self):
        hashes = []
        for estado in ("falha", "aviso", "parado"):
            c = cv.Canvas(60, 60)
            render_png._forma(c, 10, 10, 28, estado)
            hashes.append(bytes(c.pixels))
        self.assertEqual(len(set(hashes)), 3)
        self.assertEqual(render_png._FORMA_NIVEL, {"critico": "falha", "aviso": "aviso", "leve": "parado"})

    def test_acoes_nao_repete_o_atencao_nem_a_grade_de_servicos(self):
        itens = [{"id": "a", "rotulo": "A", "grupo": "host", "estado": "falha"}]
        m = self._sem_problemas(discos=[{"rotulo": "/", "caminho": "/", "total_b": 10**12, "usado_b": 9 * 10**11,
                                         "pct": 90.0}], servicos_kindle={"inventario": "ok", "itens": itens})
        _, textos, cartoes = self._desenhar(m, "comandos")
        self.assertEqual(cartoes, [])
        for t in ("ATENCAO", "Tudo em ordem", "TODOS OS SERVICOS", "SERVICOS POR GRUPO"):
            self.assertNotIn(t, textos)
        self.assertIn("ACOES RAPIDAS", textos)


if __name__ == "__main__":
    unittest.main()


# ------------------------------------------------------------- tela inicial (linhas por sistema)

IDS_LINHAS = ["atheron", "nas", "aparelhos", "servicos", "rotinas", "claude", "github", "ragnarok"]
SERV = [{"id": "a", "rotulo": "a", "grupo": "host", "estado": "ativo"},
        {"id": "b", "rotulo": "b", "grupo": "host", "estado": "falha"},
        {"id": "c", "rotulo": "c", "grupo": "docker", "estado": "ativo"}]
TIPOS_ERRADOS = [None, 5, "x", [], [1, None], {"erro": "n/d"}, float("nan"), True, 10 ** 400]


class LinhasResumoTest(unittest.TestCase):
    def test_vazio_devolve_as_8_linhas_sem_dados(self):
        import botoes
        ls = render_png._linhas_resumo({}, [], None, [])
        self.assertEqual([l["id"] for l in ls], IDS_LINHAS)
        self.assertEqual([l["id"] for l in ls], [i for i, _ in botoes.LINHAS_RESUMO])
        for l in ls:
            self.assertEqual(set(l), {"id", "icone", "titulo", "valor", "detalhe", "estado"})
            self.assertEqual((l["valor"], l["estado"]), ("sem dados", "sem_dados"), l["id"])

    def test_completo(self):
        m = completo(claude={"limites": {"cinco_horas": {"pct": 14.0, "volta_em": 1_794_000_000, "renovado": False},
                                         "semanal": {"pct": 2.0}}},
                     s10=S10, gpu={"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 2048, "temp_c": 39})
        kv = {"bateria": 58, "carregando": False}
        l = {x["id"]: x for x in render_png._linhas_resumo(m, SERV, kv, [])}
        self.assertEqual(l["atheron"]["valor"], "CPU 56%  RAM 38%")
        self.assertEqual(l["atheron"]["detalhe"], "55 C  ·  / 40%  ·  GPU desativada")
        self.assertEqual(l["nas"]["valor"], "NAS 75%")
        self.assertTrue(l["nas"]["detalhe"].startswith("NAS  "))
        self.assertEqual((l["aparelhos"]["valor"], l["aparelhos"]["detalhe"]), ("sem dados", "Kindle 58%  S10 87%"))
        self.assertEqual((l["servicos"]["valor"], l["servicos"]["detalhe"]), ("2 de 3 ok", "host 1/2  docker 1/1"))
        self.assertEqual((l["rotinas"]["valor"], l["github"]["valor"]), ("sem dados", "sem dados"))
        self.assertEqual(l["claude"]["valor"], "5h 14%  sem 2%")
        self.assertTrue(l["claude"]["detalhe"].startswith("5h volta "))
        self.assertEqual((l["ragnarok"]["valor"], l["ragnarok"]["detalhe"]), ("3 jogadores", "login ok  char ok  map fechada"))
        for i in ("atheron", "nas", "servicos", "claude", "ragnarok"):
            self.assertEqual(l[i]["estado"], "ok", i)

    def test_inventario_velho_ou_ausente_vira_sem_dados_e_o_estado_vem_do_alerta(self):
        for inv in ("velho", "ausente"):
            m = completo(servicos_kindle={"inventario": inv, "itens": SERV})
            al = [{"nivel": "aviso", "sistema": "servicos"}]
            l = {x["id"]: x for x in render_png._linhas_resumo(m, SERV, None, al)}["servicos"]
            self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "inventario sem atualizar", "aviso"))
        m = completo(servicos_kindle={"inventario": "ok", "itens": SERV})
        l = {x["id"]: x for x in render_png._linhas_resumo(m, SERV, None, [])}["servicos"]
        self.assertEqual(l["valor"], "2 de 3 ok")

    def _nas(self, *rotulos):
        discos = [{"rotulo": r, "caminho": "/x%d" % i, "total_b": 10 ** 12, "usado_b": 10 ** 11 * (i + 1),
                   "pct": 10.0 * (i + 1)} for i, r in enumerate(rotulos)]
        return {x["id"]: x for x in render_png._linhas_resumo(completo(discos=discos), [], None, [])}["nas"]

    def test_nas_tira_o_prefixo_so_sem_colisao(self):
        self.assertEqual(self._nas("NAS HD", "NAS SSD")["valor"], "HD 10%  SSD 20%")
        self.assertEqual(self._nas("NAS HD", "NAS SSD", "SSD")["valor"], "HD 10%  NAS SSD 20%  SSD 30%")
        self.assertEqual(self._nas("NAS")["valor"], "NAS 10%")
        self.assertTrue(self._nas("NAS HD", "NAS SSD")["detalhe"].startswith("SSD  "))

    def test_estado_e_o_pior_nivel_dos_alertas_do_sistema(self):
        al = [{"nivel": "leve", "sistema": "nas"}, {"nivel": "critico", "sistema": "nas"},
              {"nivel": "aviso", "sistema": "nas"}, {"nivel": "aviso", "sistema": "kindle"},
              {"nivel": "leve", "sistema": "servicos"}]
        l = {x["id"]: x["estado"] for x in render_png._linhas_resumo(completo(), SERV, None, al)}
        self.assertEqual((l["nas"], l["aparelhos"], l["servicos"], l["atheron"]), ("critico", "aviso", "leve", "ok"))

    def test_alerta_vale_mesmo_sem_dados(self):
        al = [{"nivel": "critico", "sistema": "rotinas"}]
        l = {x["id"]: x for x in render_png._linhas_resumo({}, [], None, al)}
        self.assertEqual(l["rotinas"]["estado"], "critico")
        self.assertEqual(l["rotinas"]["valor"], "sem dados")

    def test_tipos_errados_nunca_levantam(self):
        for ruim in TIPOS_ERRADOS:
            for m in (ruim, {k: ruim for k in ("cpu", "ram", "temp_cpu", "discos", "gpu", "s10", "claude",
                                                "ragnarok", "portas", "gerado_em")}):
                for itens, kv, al in ((ruim, ruim, ruim), ([ruim], {"bateria": ruim}, [ruim, {"sistema": ruim}]),
                                      (SERV, {"bateria": ruim}, [{"nivel": ruim, "sistema": "nas"}])):
                    ls = render_png._linhas_resumo(m, itens, kv, al)
                    self.assertEqual([x["id"] for x in ls], IDS_LINHAS)
        m = completo(discos=[ruim_ for ruim_ in TIPOS_ERRADOS] + [{"rotulo": 5, "pct": "x"}],
                     portas=TIPOS_ERRADOS, claude={"limites": {"cinco_horas": "x", "semanal": [1]}})
        self.assertEqual(len(render_png._linhas_resumo(m, SERV, None, [])), 8)

    def test_renderiza_com_tipos_errados_sem_sair_do_canvas(self):
        for ruim in TIPOS_ERRADOS:
            m = {k: ruim for k in ("cpu", "ram", "temp_cpu", "discos", "gpu", "s10", "claude", "ragnarok", "portas")}
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, m, None)


class DesenhoResumoTest(unittest.TestCase):
    def _textos(self, m, kv=None):
        textos = []
        orig = cv.Canvas.texto

        def espia(self, x, y, t, *a, **k):
            textos.append(t)
            return orig(self, x, y, t, *a, **k)
        cv.Canvas.texto = espia
        try:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png.desenhar(c, m, historico(), kindle=kv)
        finally:
            cv.Canvas.texto = orig
        return textos

    def _com_faixa(self, m):
        return "HISTORICO" in self._textos(m)

    def test_faixa_de_historico_so_com_vao_suficiente(self):
        self.assertTrue(self._com_faixa(completo(portas=[{"rotulo": "L", "aberto": True}], servicos=[])))  # 0 alertas
        m6 = completo(servicos=[], servicos_kindle={"inventario": "ok", "itens": [
            {"id": "s%d" % i, "rotulo": "svc%d" % i, "grupo": "host", "estado": "falha", "detalhe": "x",
             "verbos": [], "protegido": False, "opcional": False} for i in range(6)]})
        self.assertFalse(self._com_faixa(m6))  # 6 alertas
        self.assertTrue(any(t.startswith("ATENCAO (") for t in self._textos(m6)))

    def test_faixa_de_historico_sem_historico_nao_desenha(self):
        textos = []
        orig = cv.Canvas.texto
        cv.Canvas.texto = lambda self, x, y, t, *a, **k: (textos.append(t), orig(self, x, y, t, *a, **k))[1]
        try:
            render_png.desenhar(cv.Canvas(1236, 1648, estrito=True), completo(servicos=[]), {})
        finally:
            cv.Canvas.texto = orig
        self.assertNotIn("HISTORICO", textos)

    def test_com_12_alertas_aparecem_6_e_mais_6(self):
        m = completo(servicos=[], portas=[{"rotulo": "LOGIN", "aberto": True}], servicos_kindle={"inventario": "ok", "itens": [
            {"id": "s%d" % i, "rotulo": "svc%d" % i, "grupo": "host", "estado": "falha", "detalhe": "x",
             "verbos": [], "protegido": False, "opcional": False} for i in range(12)]})
        tx = self._textos(m)
        self.assertIn("ATENCAO (12)", tx)
        self.assertEqual(len([t for t in tx if t.endswith("em falha")]), 6)
        self.assertIn("+6", tx)

    def test_sem_alertas_mostra_tudo_em_ordem(self):
        m = completo(portas=[{"rotulo": "LOGIN", "aberto": True}], servicos=[])
        self.assertIn("Tudo em ordem", self._textos(m))

    def test_nao_desenha_o_que_saiu_da_tela_inicial(self):
        chamadas = []
        nomes = ("_card_discos", "_card_io", "_card_rotinas", "_card_kindle", "_card_par")
        antigos = {n: getattr(render_png, n) for n in nomes}
        try:
            for n in nomes:
                setattr(render_png, n, lambda *a, _n=n, **k: chamadas.append(_n))
            render_png.render_png(completo(), historico())
        finally:
            for n, f in antigos.items():
                setattr(render_png, n, f)
        self.assertEqual(chamadas, [])

    def test_cabecalho_so_host_e_hora(self):
        tx = self._textos(completo())
        self.assertIn("atheron", tx)
        self.assertIn("14:32", tx)
        self.assertFalse([t for t in tx if "servicos ·" in t])

    def test_linha_sistema_nao_sai_da_caixa(self):
        import botoes
        extremos = [{"id": "nas", "icone": "nas", "titulo": "T" * 60, "valor": "V" * 200, "detalhe": "d" * 300,
                     "estado": e} for e in ("ok", "critico", "aviso", "leve", "sem_dados")]
        extremos.append({"id": "x", "icone": "inexistente", "titulo": "", "valor": "", "detalhe": "", "estado": "?"})
        for cx in botoes.geometria_resumo()["linhas"]:
            for ln in extremos:
                c = cv.Canvas(1236, 1648, estrito=True)
                render_png._linha_sistema(c, cx, ln)
                for y in range(1648):
                    fora = c.pixels[y * 1236:(y + 1) * 1236]
                    if cx["y"] <= y < cx["y"] + cx["h"]:
                        fora = fora[:cx["x"]] + fora[cx["x"] + cx["w"]:]
                    self.assertEqual(min(fora, default=255), 255, (cx["id"], ln["estado"], y))


class CorrecoesRevisaoPngTest(unittest.TestCase):
    @staticmethod
    def _texto_desenhado(fn):
        textos = []
        orig = cv.Canvas.texto

        def espia(self, x, y, t, *a, **k):
            textos.append(t)
            return orig(self, x, y, t, *a, **k)
        cv.Canvas.texto = espia
        try:
            fn()
        finally:
            cv.Canvas.texto = orig
        return textos

    def test_historico_intervalo_invalido_usa_15s(self):
        for ruim in ("x", float("nan"), float("inf"), -3, 0, True, [1]):
            h = historico() | {"intervalo_s": ruim}
            c = cv.Canvas(1236, 1648, estrito=True)
            tx = self._texto_desenhado(lambda: render_png._card_historico(
                c, h, render_png._series_historico(h, (("CPU", "cpu"),)), 48, 100, 1100, 300))
            self.assertIn("ultimos 15 min", tx, ruim)  # 60 amostras x 15 s

    def test_historico_valor_atual_limitado_a_0_100(self):
        h = {"cpu": [150.0] * 6, "ram": [-20.0] * 6}
        c = cv.Canvas(1236, 1648, estrito=True)
        tx = self._texto_desenhado(lambda: render_png._card_historico(
            c, h, render_png._series_historico(h, (("CPU", "cpu"), ("RAM", "ram"))), 48, 100, 1100, 300))
        self.assertIn("100%", tx)
        self.assertIn("0%", tx)
        self.assertNotIn("150%", tx)
        self.assertNotIn("-20%", tx)

    def test_card_atencao_com_uma_linha_mostra_pelo_menos_um_item(self):
        at = [{"nivel": "aviso", "texto": "Primeiro alerta"}, {"nivel": "aviso", "texto": "Segundo"},
              {"nivel": "aviso", "texto": "Terceiro"}]
        h = render_png.ATENCAO_TITULO + render_png.ATENCAO_LINHA + 14
        c = cv.Canvas(1236, 1648, estrito=True)
        tx = self._texto_desenhado(lambda: render_png._card_atencao(c, at, 48, 158, 1140, h))
        self.assertIn("Primeiro alerta", tx)

    def test_erro_de_construtor_e_registrado_uma_vez(self):
        import contextlib
        import io
        orig = render_png._CONSTRUTORES["nas"]

        def quebra(m, kv, itens):
            raise ValueError("falha de teste")
        render_png._CONSTRUTORES["nas"] = quebra
        render_png._LINHAS_AVISADAS.clear()
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf):
                for _ in range(3):
                    ls = render_png._linhas_resumo({}, [], None, [])
        finally:
            render_png._CONSTRUTORES["nas"] = orig
            render_png._LINHAS_AVISADAS.clear()
        self.assertEqual(ls[1]["valor"], "sem dados")
        self.assertEqual(buf.getvalue().count("falha de teste"), 1, buf.getvalue())
        self.assertIn("nas", buf.getvalue())

    def test_campos_kindle_tolera_tipos_errados(self):
        kv = {"bateria": 50, "temp_c": "x", "wifi_ok": True, "wifi": "forte", "bt": True, "bt_conectados": "dois",
              "autonomia": 5, "latencia": ["a"], "tailscale": "direto", "relogio": 7, "whispersync": {}}
        bat, det, pares = render_png._campos_kindle(kv)
        d = dict(pares)
        self.assertEqual((d["RELOGIO"], d["WHISPERSYNC"]), ("n/d", "n/d"))
        self.assertEqual(d["ELO"], "direto · n/d")
        self.assertEqual(d["BLUETOOTH"], "ligado")
        self.assertEqual(d["WI-FI"], "conectado")
        self.assertIn("n/d", det)
        c = cv.Canvas(1236, 1648, estrito=True)
        render_png._card_kindle(c, kv, 48, 100, 1140, 400)

    def test_residuos_removidos(self):
        for nome in ("_aviso_inventario", "_bytes_txt"):
            self.assertFalse(hasattr(render_png, nome), nome)


# ------------------------------------------------- aparelhos e rotinas (Entrega 2, Tarefa 22)

def ap(i, rotulo, online=True, icone="celular", **k):
    d = {"id": i, "rotulo": rotulo, "icone": icone, "online": online, "offline_min": None,
         "conexao": "direto" if online else None, "alerta_offline_min": None}
    d.update(k)
    return d


def aparelhos(itens, inv="ok"):
    return {"inventario": inv, "idade_s": 4 if inv == "ok" else 300, "itens": itens}


APS7 = [ap("notebook", "Notebook", icone="notebook"), ap("s22", "S22", conexao="relay"), ap("s10", "S10"),
        ap("iphone", "iPhone", conexao="relay"), ap("kindle", "Kindle", icone="leitor"),
        ap("gateway", "Gateway", icone="rede"), ap("games", "Games", icone="jogo")]


def rot(i, rotulo, resultado="ok", idade_h=5.5, atrasada=False, ultima_em=None, max_idade_h=26):
    return {"id": i, "rotulo": rotulo, "resultado": resultado,
            "ultima_em": 1_794_000_000 - int(idade_h * 3600) if ultima_em is None and idade_h is not None
            else ultima_em, "idade_h": idade_h, "max_idade_h": max_idade_h, "atrasada": atrasada}


def rotinas(itens, inv="ok", n=0, nomes=()):
    return {"inventario": inv, "idade_s": 4 if inv == "ok" else 300, "itens": itens,
            "unidades_falhas": {"n": n, "nomes": list(nomes)}}


ROTS4 = [rot("backup-senhas", "Backup senhas", idade_h=4.2), rot("sync-cofre", "Sync cofre", idade_h=0.4),
         rot("segundo-cerebro", "Segundo cerebro", idade_h=9), rot("tokens-claude", "Tokens Claude", idade_h=0.2)]


def espiar(m, pagina, kv=None, w=1236, h=1648):
    """(textos, icones) desenhados em `pagina` com canvas estrito."""
    textos, icones = [], []
    orig_t, orig_i = cv.Canvas.texto, cv.Canvas.icone

    def espia_t(self, x, y, t, *a, **k):
        textos.append(t)
        return orig_t(self, x, y, t, *a, **k)

    def espia_i(self, x, y, nome, tam, cor):
        icones.append((nome, tam))
        return orig_i(self, x, y, nome, tam, cor)
    cv.Canvas.texto, cv.Canvas.icone = espia_t, espia_i
    try:
        render_png.desenhar(cv.Canvas(w, h, estrito=True), m, historico(), pagina=pagina, kindle=kv)
    finally:
        cv.Canvas.texto, cv.Canvas.icone = orig_t, orig_i
    return textos, icones


def fora_da_caixa(c, x, y, w, h):
    """Menor pixel fora da caixa (255 = nada desenhado fora)."""
    menor = 255
    for yy in range(c.altura):
        linha = c.pixels[yy * c.largura:(yy + 1) * c.largura]
        if y <= yy < y + h:
            linha = linha[:x] + linha[x + w:]
        menor = min(menor, min(linha, default=255))
    return menor


class VistoTest(unittest.TestCase):
    def test_minutos_horas_dias(self):
        f = render_png._ha_txt
        self.assertEqual([f(5), f(89), f(90), f(125), f(47 * 60 + 59), f(48 * 60), f(3 * 1440 + 5)],
                         ["ha 5 min", "ha 89 min", "ha 1 h", "ha 2 h", "ha 47 h", "ha 2 d", "ha 3 d"])
        self.assertEqual(f(0), "ha 1 min")
        for ruim in (None, "x", True, -3, float("nan"), 10 ** 400):
            self.assertEqual(f(ruim), "", ruim)


class LinhaAparelhosTest(unittest.TestCase):
    def _l(self, m, kv=None, al=()):
        return {x["id"]: x for x in render_png._linhas_resumo(m, [], kv, list(al))}["aparelhos"]

    def test_n_de_m_online_e_rotulos_dos_offline(self):
        its = [dict(i) for i in APS7]
        its[1].update(online=False, offline_min=95, conexao=None)
        its[6].update(online=False, offline_min=5, conexao=None)
        l = self._l({"aparelhos": aparelhos(its)}, {"bateria": 58})
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("5 de 7 online", "offline: S22, Games", "ok"))

    def test_todos_online_mostra_as_baterias(self):
        m = completo(s10=S10, aparelhos=aparelhos(APS7))
        l = self._l(m, {"bateria": 58, "carregando": False})
        self.assertEqual((l["valor"], l["detalhe"]), ("7 de 7 online", "Kindle 58%  S10 87%"))

    def test_online_none_nao_conta_como_online(self):
        its = [ap("a", "A"), ap("b", "B", online=None, conexao=None)]
        l = self._l({"aparelhos": aparelhos(its)})
        self.assertEqual((l["valor"], l["detalhe"]), ("1 de 2 online", "1 sem dado"))

    def test_lista_de_offline_longa_e_cortada_com_reticencias(self):
        its = [ap("i%d" % k, "Aparelho %02d" % k, online=False, conexao=None) for k in range(16)]
        l = self._l({"aparelhos": aparelhos(its)})
        self.assertEqual(l["valor"], "0 de 16 online")
        c = cv.Canvas(1236, 1648, estrito=True)
        import botoes
        render_png._linha_sistema(c, botoes.geometria_resumo()["linhas"][2], l)  # nao estoura a caixa

    def test_inventario_velho_ou_ausente_vira_sem_dados(self):
        for inv in ("velho", "ausente"):
            its = [ap("a", "A", online=None, conexao=None)]
            l = self._l({"aparelhos": aparelhos(its, inv)}, None, [{"nivel": "aviso", "sistema": "aparelhos"}])
            self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "inventario sem atualizar", "aviso"))

    def test_sem_catalogo_continua_como_antes(self):
        l = self._l(completo(s10=S10), {"bateria": 58})
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "Kindle 58%  S10 87%", "sem_dados"))

    def test_estado_vem_dos_alertas_do_sistema_aparelhos(self):
        l = self._l({"aparelhos": aparelhos(APS7)}, None, [{"nivel": "critico", "sistema": "aparelhos"}])
        self.assertEqual(l["estado"], "critico")

    def test_blocos_malformados_nao_levantam(self):
        for ruim in TIPOS_ERRADOS + [{"itens": "x"}, {"itens": [None, 5, {"online": "x", "rotulo": 7}]},
                                     {"inventario": "ok", "itens": []}]:
            self._l({"aparelhos": ruim})


class LinhaRotinasTest(unittest.TestCase):
    def _l(self, m, al=()):
        return {x["id"]: x for x in render_png._linhas_resumo(m, [], None, list(al))}["rotinas"]

    def test_tudo_ok_cita_a_mais_recente(self):
        l = self._l({"rotinas": rotinas(ROTS4)})
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("4 de 4 ok", "Tokens Claude ha 12 min", "ok"))
        its = [rot("a", "Backup senhas", idade_h=4.2), rot("b", "Sync cofre", idade_h=9)]
        self.assertEqual(self._l({"rotinas": rotinas(its)})["detalhe"], "Backup senhas ha 4 h")

    def test_atrasada_nao_conta_como_ok_e_vira_o_detalhe(self):
        its = [rot("a", "Backup senhas"), rot("b", "Segundo cerebro", idade_h=31, atrasada=True)]
        l = self._l({"rotinas": rotinas(its)}, [{"nivel": "aviso", "sistema": "rotinas"}])
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("1 de 2 ok", "Segundo cerebro atrasada", "aviso"))

    def test_falha_e_a_primeira_com_problema(self):
        its = [rot("a", "Backup senhas", resultado="falha", idade_h=2), rot("b", "Sync cofre", atrasada=True)]
        l = self._l({"rotinas": rotinas(its)}, [{"nivel": "critico", "sistema": "rotinas"}])
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("0 de 2 ok", "Backup senhas falhou", "critico"))

    def test_desconhecida_nao_conta_como_ok(self):
        its = [rot("a", "Backup senhas", resultado="desconhecido", idade_h=None), rot("b", "Sync cofre")]
        l = self._l({"rotinas": rotinas(its)})
        self.assertEqual((l["valor"], l["detalhe"]), ("1 de 2 ok", "Backup senhas sem dado"))

    def test_unidades_em_falha_sem_rotina_com_problema(self):
        l = self._l({"rotinas": rotinas(ROTS4, n=2, nomes=["a.service", "b.service"])})
        self.assertEqual((l["valor"], l["detalhe"]), ("4 de 4 ok", "2 unidades em falha"))

    def test_inventario_velho_ou_ausente_ou_sem_chave(self):
        for inv in ("velho", "ausente"):
            l = self._l({"rotinas": rotinas(ROTS4, inv)})
            self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "inventario sem atualizar", "ok"))
        l = self._l({})
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "", "sem_dados"))

    def test_blocos_malformados_nao_levantam(self):
        for ruim in TIPOS_ERRADOS + [{"itens": "x"}, {"itens": [None, 5, {"resultado": 3, "rotulo": []}]}]:
            self._l({"rotinas": ruim})
        for ruim in TIPOS_ERRADOS + [{"n": "x", "nomes": 5}, {"n": 2, "nomes": [None, 3, "a"]}]:
            self._l({"rotinas": {"inventario": "ok", "itens": [rot("a", "A")], "unidades_falhas": ruim}})


class PaginaAparelhosTest(unittest.TestCase):
    def test_sete_aparelhos_com_formas_e_texto_secundario(self):
        its = [dict(i) for i in APS7]
        its[1].update(online=False, offline_min=95, conexao=None)           # offline ha 1 h
        its[5].update(online=False, offline_min=20, conexao=None, alerta_offline_min=10)  # passou do limite
        its[6].update(online=False, offline_min=4000, conexao=None)         # offline ha 2 d
        tx, ic = espiar(completo(aparelhos=aparelhos(its)), "aparelhos")
        for t in ("Tailnet", "Notebook", "S22", "iPhone", "Gateway", "Games", "direto", "relay",
                  "offline ha 1 h", "offline ha 20 min", "offline ha 2 d"):
            self.assertIn(t, tx)
        self.assertEqual(tx.count("direto"), 3)
        self.assertEqual(tx.count("relay"), 1)
        self.assertEqual(ic.count(("notebook", 40)), 1)
        self.assertEqual(ic.count(("celular", 40)), 3)
        self.assertEqual(ic.count(("rede", 40)), 1)
        self.assertNotIn("inventario sem atualizar", tx)

    def test_formas_de_estado(self):
        calls = []
        orig = render_png._forma
        render_png._forma = lambda c, x, y, lado, estado: (calls.append((lado, estado)), orig(c, x, y, lado, estado))[1]
        try:
            its = [ap("a", "A"), ap("b", "B", online=False, offline_min=5, conexao=None),
                   ap("c", "C", online=False, offline_min=50, conexao=None, alerta_offline_min=30),
                   ap("d", "D", online=None, conexao=None)]
            espiar(completo(aparelhos=aparelhos(its)), "aparelhos")
        finally:
            render_png._forma = orig
        self.assertEqual([e for lado, e in calls if lado == 28][:4], ["ativo", "parado", "falha", None])

    def test_dezesseis_aparelhos_cabem(self):
        its = [ap("i%d" % k, "Aparelho %02d" % k, online=k % 3 != 0, offline_min=k * 7,
                  conexao="direto" if k % 3 else None) for k in range(16)]
        tx, _ = espiar(completo(aparelhos=aparelhos(its)), "aparelhos")
        self.assertEqual(len([t for t in tx if t.startswith("Aparelho ")]), 16)
        self.assertFalse([t for t in tx if t.startswith("+")])

    def test_sem_espaco_corta_com_mais_n_e_mantem_os_problemas(self):
        its = [ap("i%d" % k, "Aparelho %02d" % k) for k in range(16)]
        its[14].update(online=False, offline_min=500, conexao=None, alerta_offline_min=10)
        tx, _ = espiar(completo(aparelhos=aparelhos(its)), "aparelhos", None, 1236, 1000)
        mostrados = [t for t in tx if t.startswith("Aparelho ")]
        resto = [t for t in tx if t.startswith("+")]
        self.assertEqual(len(resto), 1)
        self.assertEqual(len(mostrados) + int(resto[0][1:]), 16)
        self.assertIn("Aparelho 14", mostrados)  # o aparelho em falha nao fica no corte

    def test_icone_desconhecido_cai_no_aparelhos(self):
        its = [ap("a", "A", icone="nao-existe"), ap("b", "B", icone=None), ap("c", "C", icone=[1])]
        _, ic = espiar(completo(aparelhos=aparelhos(its)), "aparelhos")
        self.assertEqual(ic.count(("aparelhos", 40)), 3)

    def test_online_none_mostra_sem_dado(self):
        tx, _ = espiar(completo(aparelhos=aparelhos([ap("a", "A", online=None, conexao=None)])), "aparelhos")
        self.assertIn("sem dado", tx)

    def test_inventario_velho_ou_ausente_mostra_sem_dados(self):
        for inv in ("velho", "ausente"):
            tx, _ = espiar(completo(aparelhos=aparelhos(APS7, inv)), "aparelhos")
            self.assertIn("inventario sem atualizar", tx)
            self.assertIn("sem dados", tx)
            self.assertNotIn("Notebook", tx)

    def test_sem_a_chave_continua_sem_dados(self):
        tx, _ = espiar(completo(), "aparelhos")
        self.assertIn("Tailnet", tx)
        self.assertIn("sem dados", tx)
        self.assertNotIn("inventario sem atualizar", tx)

    def test_cartoes_kindle_e_s10_continuam_abaixo(self):
        tx, _ = espiar(completo(s10=S10, aparelhos=aparelhos(APS7)), "aparelhos", PaginasAparelhosDevTest.KV)
        for t in ("Kindle", "BATERIA", "S10", "nomad"):
            self.assertIn(t, tx)

    def test_rotulos_hostis_nao_estouram(self):
        hostis = ["W" * 16, "\u00e7\u00e3\u00f5\u0301\u4e2d\u6587", "\x00\x1b[31m", "M" * 16, "...", ""]
        for conexao in ("direto", None):
            its = [ap("i%d" % k, r, online=k % 2 == 0, offline_min=10 ** 9, conexao=conexao, alerta_offline_min=5)
                   for k, r in enumerate(hostis)]
            for inv in ("ok", "velho"):
                for h in (1648, 900):
                    c = cv.Canvas(1236, h, estrito=True)
                    ap_ = aparelhos(its, inv)
                    render_png._card_tailnet(c, ap_, 48, 200, 1140, 500)
                    self.assertEqual(fora_da_caixa(c, 48, 200, 1140, 500), 255)

    def test_blocos_malformados_nao_levantam(self):
        for ruim in TIPOS_ERRADOS + [{"itens": "x"}, {"inventario": "ok", "itens": [None, 5, {"online": "x", "rotulo": 7}]},
                                     {"inventario": "ok", "itens": []}]:
            espiar(completo(aparelhos=ruim), "aparelhos")


class CartaoRotinasTest(unittest.TestCase):
    def test_uma_linha_por_rotina_com_ha_n_h(self):
        tx, ic = espiar(completo(rotinas=rotinas(ROTS4)), "detalhes")
        for t in ("ROTINAS", "Backup senhas", "Sync cofre", "Segundo cerebro", "Tokens Claude", "ha 4 h", "ha 24 min",
                  "ha 9 h", "ha 12 min"):
            self.assertIn(t, tx)
        self.assertFalse([t for t in tx if "unidades" in t])

    def test_formas_ok_falha_aviso_desconhecida(self):
        calls = []
        orig = render_png._forma
        render_png._forma = lambda c, x, y, lado, estado: (calls.append((lado, estado)), orig(c, x, y, lado, estado))[1]
        try:
            its = [rot("a", "A"), rot("b", "B", resultado="falha"), rot("c", "C", atrasada=True),
                   rot("d", "D", resultado="desconhecido", idade_h=None)]
            tx, _ = espiar(completo(rotinas=rotinas(its)), "detalhes")
        finally:
            render_png._forma = orig
        self.assertEqual([e for lado, e in calls if lado == 28], ["ativo", "falha", "aviso", None])
        for t in ("falhou", "atrasada", "sem dado"):
            self.assertIn(t, tx)

    def test_unidades_em_falha_ultima_linha(self):
        m = completo(rotinas=rotinas(ROTS4, n=2, nomes=["rclone-nas-sync.service", "x.service"]))
        tx, _ = espiar(m, "detalhes")
        self.assertIn("2 unidades em falha: rclone-nas-sync.service, x.service", tx)

    def test_inventario_velho_ou_sem_chave_mostra_sem_dados(self):
        for m in (completo(rotinas=rotinas(ROTS4, "velho")), completo(rotinas=rotinas(ROTS4, "ausente")), completo()):
            tx, _ = espiar(m, "detalhes")
            self.assertIn("ROTINAS", tx)
            self.assertIn("sem dados", tx)
            self.assertNotIn("Backup senhas", tx)

    def test_dezesseis_rotinas_cortam_com_mais_n_e_mantem_problemas(self):
        its = [rot("r%d" % k, "Rotina %02d" % k) for k in range(16)]
        its[13].update(resultado="falha")
        tx, _ = espiar(completo(rotinas=rotinas(its, n=1, nomes=["a.service"])), "detalhes")
        mostradas = [t for t in tx if t.startswith("Rotina ")]
        resto = [t for t in tx if t.startswith("+")]
        self.assertEqual(len(resto), 1)
        self.assertEqual(len(mostradas) + int(resto[0][1:]), 16)
        self.assertIn("Rotina 13", mostradas)
        self.assertIn("1 unidade em falha: a.service", tx)

    def test_sem_espaco_o_historico_sai_antes_do_rotinas(self):
        its = [rot("r%d" % k, "Rotina %02d" % k) for k in range(8)]
        m = cheio() | {"rotinas": rotinas(its, n=1, nomes=["a.service"]),
                       "discos": [{"rotulo": "d%d" % i, "caminho": "/", "total_b": 10**12, "usado_b": 10**11,
                                   "pct": 10.0} for i in range(5)],
                       "io": {"discos": [{"rotulo": "NVMe", "leitura_bps": 1, "escrita_bps": 2}],
                              "redes": [{"rotulo": "LAN", "rx_bps": 1, "tx_bps": 2}]}}
        tx, _ = espiar(m, "detalhes")
        self.assertIn("ROTINAS", tx)
        self.assertEqual(len([t for t in tx if t.startswith("Rotina ")]), 6)  # 8 linhas: 6 rotinas, "+2" e as unidades
        self.assertIn("+2", tx)
        self.assertNotIn("HISTORICO", tx)
        tx, _ = espiar(completo(rotinas=rotinas(ROTS4)), "detalhes")  # com folga, o historico fica
        self.assertIn("HISTORICO", tx)

    def test_rotulos_hostis_e_tipos_errados_nao_estouram(self):
        its = [rot("a", "W" * 20), rot("b", "\u00e7\u00e3\u4e2d", resultado="falha"),
               {"rotulo": 5, "resultado": [], "idade_h": "x", "atrasada": "sim"}, None, 7]
        for inv in ("ok", "velho"):
            c = cv.Canvas(1236, 1648, estrito=True)
            r = rotinas(its, inv, n=3, nomes=["N" * 40] * 5)
            render_png._card_rotinas(c, r, 48, 200, 1140, render_png._h_rotinas(r))
            self.assertEqual(fora_da_caixa(c, 48, 200, 1140, render_png._h_rotinas(r)), 255)
        for ruim in TIPOS_ERRADOS:
            espiar(completo(rotinas=ruim), "detalhes")
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._card_rotinas(c, ruim, 48, 200, 1140, render_png._h_rotinas(ruim))


class PaginasAparelhosDevTest(unittest.TestCase):
    KV = {"bateria": 86, "carregando": False, "temp_c": 29, "autonomia": "2 d 4 h", "wifi": 3, "wifi_ok": True,
          "aviao": False, "bt": False, "bt_conectados": 0, "tailscale": "direto", "latencia": "38 ms",
          "relogio": "ok", "whispersync": None}

    def _ver(self, m, pagina, kv=None):
        textos, icones = [], []
        orig_t, orig_i = cv.Canvas.texto, cv.Canvas.icone

        def espia_t(self, x, y, t, *a, **k):
            textos.append(t)
            return orig_t(self, x, y, t, *a, **k)

        def espia_i(self, x, y, nome, tam, cor):
            icones.append(nome)
            return orig_i(self, x, y, nome, tam, cor)
        cv.Canvas.texto, cv.Canvas.icone = espia_t, espia_i
        try:
            render_png.desenhar(cv.Canvas(1236, 1648, estrito=True), m, historico(), pagina=pagina, kindle=kv)
        finally:
            cv.Canvas.texto, cv.Canvas.icone = orig_t, orig_i
        return textos, icones

    def test_aparelhos_tem_tailnet_kindle_s10_e_pares_com_icones(self):
        tx, ic = self._ver(completo(s10=S10), "aparelhos", self.KV)
        for t in ("Tailnet", "Kindle", "S10", "sem dados", "BATERIA", "nomad"):
            self.assertIn(t, tx)
        for i in ("tailscale", "leitor", "celular"):
            self.assertIn(i, ic)

    def test_aparelhos_sem_s10_e_sem_vista_do_kindle(self):
        tx, _ = self._ver(completo(), "aparelhos")
        self.assertNotIn("S10", tx)
        self.assertEqual(tx.count("sem dados"), 3)  # barra do Kindle, cartao Tailnet e cartao Kindle

    def test_dev_tem_claude_sessoes_e_github(self):
        tx, ic = self._ver(completo(claude=CL), "claude")
        for t in ("Claude", "Sessoes", "GitHub"):
            self.assertIn(t, tx)
        for i in ("claude", "dev", "github"):
            self.assertIn(i, ic)
        self.assertNotIn("S10", tx)

    def test_dev_sem_claude_na_config(self):
        tx, _ = self._ver(completo(s10=S10), "claude")
        self.assertIn("Claude desligado na config", tx)


# ------------------------------------------------- Dev: sessoes e GitHub (Entrega 2, Tarefa 23)

def ses(*itens, total=None, esp=None, idade_s=5):
    esp = sum(1 for i in itens if i["estado"] == "esperando") if esp is None else esp
    return {"itens": list(itens), "total": len(itens) if total is None else total, "esperando": esp, "idade_s": idade_s}


def sx(projeto, estado="trabalhando", desde_s=120):
    return {"projeto": projeto, "estado": estado, "desde_s": desde_s}


def prx(repo, numero, titulo="Titulo", rascunho=False, ci="ok"):
    return {"repo": repo, "numero": numero, "titulo": titulo, "rascunho": rascunho, "ci": ci}


def gh(prs=(), ci=(), abertos=None, velho=False, idade_s=30):
    return {"prs": list(prs), "ci": list(ci), "abertos": len(prs) if abertos is None else abertos,
            "ci_falhas": sum(1 for i in ci if isinstance(i, dict) and i.get("estado") == "falha"), "idade_s": idade_s, "velho": velho}


def cix(repo, estado="ok", branch="main"):
    return {"repo": repo, "branch": branch, "estado": estado}


def dev(sessoes=None, github=None, **extra):
    cl = dict(CL)
    if sessoes is not None:
        cl["sessoes"] = sessoes
    m = completo(claude=cl, **extra)
    if github is not None:
        m["github"] = github
    return m


class CartaoSessoesTest(unittest.TestCase):
    def _formas(self, m):
        calls = []
        orig = render_png._forma
        render_png._forma = lambda c, x, y, lado, estado: (calls.append((lado, estado)), orig(c, x, y, lado, estado))[1]
        try:
            tx, ic = espiar(m, "claude")
        finally:
            render_png._forma = orig
        return tx, ic, [e for lado, e in calls if lado == 28]

    def test_tres_sessoes_com_resumo_estado_e_tempo(self):
        m = dev(ses(sx("kindle-monitor", "esperando", 1500), sx("dotfiles", "trabalhando", 240),
                    sx("cerberus", "aberta", 7200)))
        tx, ic, formas = self._formas(m)
        for t in ("Sessoes", "3 sessoes, 1 esperando", "kindle-monitor", "dotfiles", "cerberus",
                  "esperando ha 25 min", "trabalhando ha 4 min", "aberta ha 2 h"):
            self.assertIn(t, tx)
        self.assertIn(("dev", 40), ic)
        self.assertEqual([f for f in formas if f != "ativo"][:1], ["aviso"])  # esperando ha mais de 10 min
        self.assertEqual(formas.count("ativo"), 1)  # so a que trabalha (a aberta e um circulo cinza proprio)

    def test_esperando_recente_e_parado_e_antiga_e_aviso(self):
        for desde, forma in ((599, "parado"), (600, "aviso"), (60, "parado"), (7200, "aviso")):
            _, _, formas = self._formas(dev(ses(sx("p", "esperando", desde))))
            self.assertEqual([f for f in formas if f in ("parado", "aviso")], [forma], desde)

    def test_limiar_vem_de_m_limiares(self):
        m = dev(ses(sx("p", "esperando", 120)))
        m["limiares"] = {"sessao_esperando_min": 1}
        _, _, formas = self._formas(m)
        self.assertIn("aviso", formas)

    def test_um_singular(self):
        tx, _ = espiar(dev(ses(sx("p"))), "claude")
        self.assertIn("1 sessao, 0 esperando", tx)

    def test_doze_sessoes_cabem_ou_cortam_com_mais_n(self):
        itens = [sx("proj-%d" % i, ("esperando", "trabalhando", "aberta")[i % 3], i * 100) for i in range(12)]
        m = dev(ses(*itens), gh(), )
        tx, _ = espiar(m, "claude")
        proj = [t for t in tx if t.startswith("proj-")]
        resto = [t for t in tx if t.startswith("+")]
        self.assertTrue(proj)
        self.assertEqual(len(proj) + (int(resto[0][1:]) if resto else 0), 12)
        self.assertIn("12 sessoes, 4 esperando", tx)

    def test_doze_sessoes_deixam_o_github_na_tela(self):
        itens = [sx("proj-%d" % i) for i in range(12)]
        prs = [prx("r", i, "t%d" % i) for i in range(20)]
        tx, _ = espiar(dev(ses(*itens), gh(prs, [cix("r")])), "claude")
        self.assertIn("GitHub", tx)
        self.assertIn("20 PRs abertos", tx)
        self.assertTrue([t for t in tx if t.startswith("+")])

    def test_sem_sessao(self):
        tx, _ = espiar(dev(ses(), gh()), "claude")
        self.assertIn("nenhuma sessao aberta", tx)
        self.assertNotIn("0 sessoes, 0 esperando", tx)

    def test_sem_dados_com_nd_ou_chave_ausente(self):
        for sess in ({"erro": "n/d"}, None, 5, "x", {"itens": "x"}):
            tx, _ = espiar(dev(sess, gh()), "claude")
            self.assertIn("Sessoes", tx)
            self.assertIn("sem dados", tx)
            self.assertNotIn("nenhuma sessao aberta", tx)

    def test_idade_s_none_e_blocos_estranhos_nao_levantam(self):
        espiar(dev(ses(sx("p"), idade_s=None)), "claude")
        itens = [None, 5, "x", {}, {"projeto": 7, "estado": 3, "desde_s": "x"}, sx("ok", "esperando", None),
                 sx("neg", "esperando", -5), sx("huge", "aberta", 10 ** 400), sx("b", True, True)]
        espiar(dev({"itens": itens, "total": "x", "esperando": None, "idade_s": None}), "claude")
        for ruim in TIPOS_ERRADOS:
            espiar(dev(ruim), "claude")
        for tot in (-1, 10 ** 400, float("nan"), True, 100):
            espiar(dev({"itens": [sx("a")], "total": tot, "esperando": tot}), "claude")

    def test_projeto_hostil_ou_longo_nao_sai_da_caixa(self):
        hostis = ["W" * 40, "\u00e7\u00e3\u00f5\u0301\u4e2d\u6587" * 6, "\x00\x1b[31mX", "m" * 40, "", "..."]
        for estado in ("esperando", "trabalhando", "aberta"):
            for desde in (30, 100000):
                itens = [sx(h, estado, desde) for h in hostis] * 2
                for h in (1648, 1000, 900):
                    c = cv.Canvas(1236, h, estrito=True)
                    cl = {"sessoes": ses(*itens, total=40)}
                    render_png._card_sessoes(c, cl, 48, 200, 1140, 600, 600)
                    self.assertEqual(fora_da_caixa(c, 48, 200, 1140, 600), 255)

    def test_sem_espaco_mantem_o_que_espera_e_corta_o_resto(self):
        itens = [sx("quieto-%d" % i) for i in range(9)] + [sx("esperando-velho", "esperando", 5000)]
        tx, _ = espiar(dev(ses(*itens)), "claude", None, 1236, 1100)
        self.assertIn("esperando-velho", tx)


class CartaoGithubTest(unittest.TestCase):
    def test_zero_prs(self):
        tx, ic = espiar(dev(ses(), gh()), "claude")
        self.assertIn("GitHub", tx)
        self.assertIn("nenhum PR aberto", tx)
        self.assertIn(("github", 40), ic)
        self.assertFalse([t for t in tx if "PRs abertos" in t])

    def test_seis_prs_sem_mais_n(self):
        prs = [prx("repo", 10 + i, "Titulo %d" % i) for i in range(6)]
        tx, _ = espiar(dev(ses(), gh(prs)), "claude")
        for i in range(6):
            self.assertIn("repo#%d" % (10 + i), tx)
        self.assertIn("6 PRs abertos", tx)
        self.assertFalse([t for t in tx if t.startswith("+")])

    def test_vinte_prs_cortam_em_seis_com_mais_n(self):
        prs = [prx("repo", i, "Titulo %d" % i) for i in range(20)]
        tx, _ = espiar(dev(ses(), gh(prs)), "claude")
        refs = [t for t in tx if t.startswith("repo#")]
        self.assertEqual(len(refs), 6)
        self.assertIn("+14", tx)
        self.assertIn("20 PRs abertos", tx)

    def test_prs_em_falha_nao_ficam_no_corte(self):
        prs = [prx("repo", i) for i in range(20)]
        prs[17]["ci"] = "falha"
        tx, _ = espiar(dev(ses(), gh(prs)), "claude")
        self.assertIn("repo#17", tx)

    def test_abertos_maior_que_a_lista(self):
        tx, _ = espiar(dev(ses(), gh([prx("r", 1)], abertos=35)), "claude")
        self.assertIn("35 PRs abertos", tx)
        self.assertIn("+34", tx)

    def test_titulo_de_60_cortado_pela_largura_e_rascunho(self):
        prs = [prx("repo", 1, "W" * 60), prx("repo", 2, "Titulo curto", rascunho=True)]
        tx, _ = espiar(dev(ses(), gh(prs)), "claude")
        cortado = [t for t in tx if t.startswith("WWW")]
        self.assertEqual(len(cortado), 1)
        self.assertTrue(cortado[0].endswith("..."))
        self.assertIn("Titulo curto", tx)
        self.assertEqual(tx.count("(rascunho)"), 1)

    def test_formas_do_ci_do_pr(self):
        calls = []
        orig = render_png._forma
        render_png._forma = lambda c, x, y, lado, estado: (calls.append((lado, estado)), orig(c, x, y, lado, estado))[1]
        try:
            prs = [prx("a", 1, ci="ok"), prx("b", 2, ci="falha"), prx("c", 3, ci="pendente"), prx("d", 4, ci=None)]
            espiar(dev(ses(), gh(prs)), "claude")
        finally:
            render_png._forma = orig
        # o corte nao age (4 PRs): ordem original; None nao desenha forma
        self.assertEqual([e for lado, e in calls if lado == 28], ["ativo", "falha", "parado"])

    def test_ci_primeiro_o_que_falhou_depois_n_ok(self):
        ci = [cix("a"), cix("cerberus", "falha", "main"), cix("b"), cix("dotfiles", "pendente", "dev")]
        tx, _ = espiar(dev(ses(), gh([prx("r", 1)], ci)), "claude")
        self.assertIn("CI falhou: cerberus (main)", tx)
        self.assertIn("CI pendente: dotfiles (dev)", tx)
        self.assertIn("2 ok", tx)
        self.assertLess(tx.index("CI falhou: cerberus (main)"), tx.index("CI pendente: dotfiles (dev)"))
        self.assertLess(tx.index("CI pendente: dotfiles (dev)"), tx.index("2 ok"))

    def test_muitas_falhas_de_ci_cortam_com_mais_n(self):
        ci = [cix("r%d" % i, "falha") for i in range(8)] + [cix("ok1")]
        tx, _ = espiar(dev(ses(), gh([prx("r", 1)], ci)), "claude")
        self.assertEqual(len([t for t in tx if t.startswith("CI falhou")]), 2)
        self.assertIn("+6", tx)
        self.assertIn("1 ok", tx)

    def test_velho_mostra_a_idade_no_titulo(self):
        tx, _ = espiar(dev(ses(), gh([prx("r", 1)], velho=True, idade_s=2000)), "claude")
        self.assertIn("ha 33 min", tx)
        tx, _ = espiar(dev(ses(), gh([prx("r", 1)], velho=False, idade_s=2000)), "claude")
        self.assertNotIn("ha 33 min", tx)

    def test_nd_e_ausente_viram_sem_dados(self):
        for g in ({"erro": "n/d"}, None, 5, "x", [], {"prs": "x"}):
            tx, _ = espiar(dev(ses(sx("p")), g), "claude")
            self.assertIn("GitHub", tx)
            self.assertIn("sem dados", tx)

    def test_blocos_estranhos_nao_levantam(self):
        ruins = [gh([None, 5, {}, {"repo": 3, "numero": "x", "titulo": None, "ci": 7}], [None, {"estado": 3}]),
                 {"prs": [prx("r", 1)], "ci": "x", "abertos": "x", "velho": "sim"},
                 {"prs": [prx("r", 1)], "abertos": -3, "idade_s": None, "velho": True},
                 {"prs": [prx("r", 1)], "abertos": 10 ** 400}]
        for g in ruins + TIPOS_ERRADOS:
            espiar(dev(ses(), g), "claude")

    def test_texto_hostil_nao_sai_da_caixa(self):
        hostis = ["W" * 80, "\u00e7\u00e3\u00f5\u0301\u4e2d\u6587" * 10, "\x00\x1b[31mX\n\r", "m" * 80, "", "..."]
        prs = [prx(h[:40], 10 ** 9 + i, h, rascunho=i % 2 == 0, ci=(None, "ok", "falha", "pendente")[i % 4])
               for i, h in enumerate(hostis * 4)]
        ci = [cix(h[:40], ("falha", "pendente", "ok")[i % 3], h[:40]) for i, h in enumerate(hostis * 5)]
        for velho in (False, True):
            for h in (1648, 1000, 900):
                for k in (1, 3, 6):
                    c = cv.Canvas(1236, h, estrito=True)
                    render_png._card_github(c, gh(prs, ci, velho=velho), 48, 200, 1140, 700, k)
                    self.assertEqual(fora_da_caixa(c, 48, 200, 1140, 700), 255)

    def test_cartao_nao_desenha_acima_do_proprio_alto(self):
        prs = [prx("repo", i, "t") for i in range(20)]
        ci = [cix("r%d" % i, ("falha", "ok")[i % 2]) for i in range(30)]
        g = gh(prs, ci)
        for k in range(1, 7):
            h = render_png._h_github(g, k)
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._card_github(c, g, 48, 200, 1140, h, k)
            self.assertEqual(fora_da_caixa(c, 48, 200, 1140, h), 255, k)


class PaginaDevCompostaTest(unittest.TestCase):
    def test_ordem_claude_sessoes_github(self):
        tx, _ = espiar(dev(ses(sx("p")), gh([prx("r", 1)])), "claude")
        self.assertLess(tx.index("Claude"), tx.index("Sessoes"))
        self.assertLess(tx.index("Sessoes"), tx.index("GitHub"))

    def test_nada_sai_da_pagina_em_nenhuma_combinacao(self):
        estados = [None, ses(), ses(sx("a")), ses(*[sx("p%d" % i, "esperando", 9999) for i in range(12)], total=12),
                   {"erro": "n/d"}]
        gits = [None, {"erro": "n/d"}, gh(), gh([prx("r", i) for i in range(20)], [cix("a", "falha")] * 30)]
        for sess in estados:
            for g in gits:
                for h in (1648, 1200, 900):
                    m = dev(sess, g)
                    c = cv.Canvas(1236, h, estrito=True)
                    render_png.desenhar(c, m, historico(), pagina="claude")

    def test_so_github_configurado_sem_claude(self):
        m = completo()
        m["github"] = gh([prx("r", 1)])
        tx, _ = espiar(m, "claude")
        self.assertIn("GitHub", tx)
        self.assertNotIn("Claude desligado na config", tx)
        self.assertNotIn("Sessoes", tx)

    def test_png_valido(self):
        png = render_png.render_png(dev(ses(sx("p")), gh([prx("r", 1)])), historico(), pagina="claude")
        self.assertEqual(ihdr(png), (1236, 1648))


class LinhasClaudeGithubTest(unittest.TestCase):
    def _ls(self, m, al=()):
        return {x["id"]: x for x in render_png._linhas_resumo(m, [], None, list(al))}

    def test_claude_com_sessoes(self):
        l = self._ls(dev(ses(sx("a", "esperando", 9999), sx("b"), sx("c", "esperando", 5))))["claude"]
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("5h 42%  sem 18%", "3 sessoes, 2 esperando", "ok"))

    def test_claude_sem_sessoes_ou_sem_dados_de_sessao_volta_ao_horario(self):
        esperado = self._ls(completo(claude=CL))["claude"]["detalhe"]
        self.assertTrue(esperado.startswith("5h volta "), esperado)
        for sess in (ses(), {"erro": "n/d"}, None, 7):
            l = self._ls(dev(sess))["claude"]
            self.assertEqual(l["detalhe"], esperado, sess)
            self.assertEqual(l["valor"], "5h 42%  sem 18%")

    def test_claude_estado_vem_dos_alertas_do_sistema_claude(self):
        m = dev(ses(sx("a", "esperando", 9999)))
        self.assertEqual(self._ls(m, [{"nivel": "leve", "sistema": "claude"}])["claude"]["estado"], "leve")
        self.assertEqual(self._ls(m, [{"nivel": "critico", "sistema": "github"}])["claude"]["estado"], "ok")

    def test_github_com_ci_ok(self):
        l = self._ls(dev(ses(), gh([prx("a", 1), prx("b", 2)], [cix("a"), cix("b")])))["github"]
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("2 PRs abertos", "CI ok", "ok"))

    def test_github_ci_falhou_nomeia_o_primeiro(self):
        ci = [cix("a"), cix("cerberus", "falha"), cix("dotfiles", "falha")]
        l = self._ls(dev(ses(), gh([prx("a", 1)], ci)), [{"nivel": "aviso", "sistema": "github"}])["github"]
        self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("1 PR aberto", "CI falhou: cerberus", "aviso"))

    def test_github_zero_prs_e_pendente(self):
        l = self._ls(dev(ses(), gh([], [cix("a", "pendente")])))["github"]
        self.assertEqual((l["valor"], l["detalhe"]), ("0 PRs abertos", "CI pendente: a"))
        l = self._ls(dev(ses(), gh()))["github"]
        self.assertEqual((l["valor"], l["detalhe"]), ("0 PRs abertos", ""))

    def test_github_velho_usa_o_estado_dos_alertas(self):
        g = gh([prx("a", 1)], [cix("a")], velho=True)
        l = self._ls(dev(ses(), g), [{"nivel": "aviso", "sistema": "github"}])["github"]
        self.assertEqual((l["valor"], l["estado"]), ("1 PR aberto", "aviso"))

    def test_github_sem_dados_cinza(self):
        for g in ({"erro": "n/d"}, None, 5, {"prs": "x"}):
            l = self._ls(dev(ses(), g))["github"]
            self.assertEqual((l["valor"], l["detalhe"], l["estado"]), ("sem dados", "", "sem_dados"), g)

    def test_linha_desenhada_nao_sai_da_caixa(self):
        import botoes
        l = self._ls(dev(ses(sx("a")), gh([prx("a", 1)], [cix("r" * 40, "falha")] * 3)))["github"]
        l["detalhe"] = "CI falhou: " + "W" * 40
        c = cv.Canvas(1236, 1648, estrito=True)
        render_png._linha_sistema(c, botoes.geometria_resumo()["linhas"][6], l)
