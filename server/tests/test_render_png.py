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
        a = render_png.render_png(completo(historico=historico()), None)
        b = render_png.render_png(completo(), None)
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


def _caixas(m):
    """(nome, y, h) dos blocos do resumo, na ordem em que sao desenhados."""
    reg = []

    def espia(nome, pos_y, pos_h):
        orig = getattr(render_png, nome)

        def f(*a, **k):
            reg.append((nome, a[pos_y], a[pos_h]))
            return orig(*a, **k)
        return f

    c = cv.Canvas(1236, 1648, estrito=True)
    trocas = {"_tile": espia("_tile", 2, 4), "_card_io": espia("_card_io", 3, 5),
              "_card_atencao": espia("_card_atencao", 3, 5), "_card_grupos": espia("_card_grupos", 3, 5),
              "_card_chips": espia("_card_chips", 3, 5), "_linha_ragnarok": espia("_linha_ragnarok", 3, 5),
              "_linha_claude_s10": espia("_linha_claude_s10", 3, 5)}
    antigos = {k: getattr(render_png, k) for k in trocas}
    try:
        for k, v in trocas.items():
            setattr(render_png, k, v)
        render_png.desenhar(c, m, historico())
    finally:
        for k, v in antigos.items():
            setattr(render_png, k, v)
    tiles = [r for r in reg if r[0] == "_tile"][:1]  # os tiles dividem a mesma linha
    return tiles + [r for r in reg if r[0] != "_tile"]


class LinhaClaudeS10Test(unittest.TestCase):
    def _linha(self, m):
        return [r for r in _caixas(m) if r[0] == "_linha_claude_s10"]

    def test_fica_acima_do_ragnarok_sem_sobrepor_nem_sair(self):
        import botoes
        for m in (completo(claude=CL, s10=S10), cheio() | {"claude": CL, "s10": S10}):
            caixas = _caixas(m)
            (_, yl, hl), (_, yr, hr) = [r for r in caixas if r[0] == "_linha_claude_s10"][0], \
                [r for r in caixas if r[0] == "_linha_ragnarok"][0]
            self.assertEqual(hl, 60)
            self.assertLess(yl + hl, yr)
            self.assertEqual(yr + hr, botoes.limite(1648))
            ordenadas = sorted(caixas, key=lambda r: r[1])
            for (_, ya, ha), (_, yb, _) in zip(ordenadas, ordenadas[1:]):
                self.assertLessEqual(ya + ha, yb)
            self.assertGreaterEqual(min(r[1] for r in caixas), botoes.TOPO)

    def test_sem_ragnarok_ancora_no_rodape(self):
        import botoes
        m = completo(claude=CL, s10=S10, ragnarok=None, portas=None)
        (_, y, h), = self._linha(m)
        self.assertEqual(y + h, botoes.limite(1648))

    def test_muitos_itens_em_atencao_continua_cabendo(self):
        import botoes
        m = completo(claude=CL, s10=S10, servicos=[{"nome": "s%d.service" % i, "ativo": False} for i in range(40)])
        caixas = _caixas(m)
        ordenadas = sorted(caixas, key=lambda r: r[1])
        for (_, ya, ha), (_, yb, _) in zip(ordenadas, ordenadas[1:]):
            self.assertLessEqual(ya + ha, yb)
        self.assertLessEqual(max(y + h for _, y, h in caixas), botoes.limite(1648))
        self.assertEqual(len(self._linha(m)), 1)

    def test_sem_as_chaves_nao_ha_linha_e_layout_e_o_antigo(self):
        orig = render_png._linha_claude_s10

        def nunca(*a, **k):
            raise AssertionError("linha nao deveria ser desenhada")
        m = completo()
        ref = render_png.render_png(m, historico())
        render_png._linha_claude_s10 = nunca
        try:
            self.assertEqual(render_png.render_png(m, historico()), ref)
        finally:
            render_png._linha_claude_s10 = orig
        self.assertNotEqual(render_png.render_png(completo(claude=CL), historico()), ref)
        self.assertNotEqual(render_png.render_png(completo(s10=S10), historico()), ref)

    def test_so_uma_parte_so_desenha_ela(self):
        so_c = render_png.render_png(completo(claude=CL), historico())
        so_s = render_png.render_png(completo(s10=S10), historico())
        ambos = render_png.render_png(completo(claude=CL, s10=S10), historico())
        self.assertEqual(len({so_c, so_s, ambos}), 3)

    def test_estados_degradados_nao_quebram(self):
        estados = [{"claude": {"limites": {"erro": "n/d"}, "tokens": {"erro": "n/d"}}},
                   {"claude": {"limites": {"cinco_horas": None, "semanal": None, "idade_s": 1, "velho": False}}},
                   {"claude": {"limites": {"cinco_horas": {"pct": 77.0, "renovado": True},
                                           "semanal": {"pct": float("nan")}}}},
                   {"claude": "x"}, {"s10": {"erro": "n/d"}}, {"s10": "x"},
                   {"s10": dict(S10, velho=True)}, {"s10": dict(S10, bateria=None)},
                   {"s10": dict(S10, bateria={"nivel": None, "status": 5}, caminhos={"usb": 1, "vnc": "x"})},
                   {"s10": dict(S10, bateria={"nivel": 250, "status": "full"})}]
        base = render_png.render_png(completo(), historico())
        for e in estados:
            dados = render_png.render_png(completo(**e), historico())
            self.assertEqual(ihdr(dados), (1236, 1648))
            self.assertNotEqual(dados, base)

    def _espiar_linha(self, m):
        textos, formas = [], []
        orig_t, orig_f = cv.Canvas.texto, render_png._forma

        def espia_t(self, x, y, t, *a, **k):
            textos.append((t, a[2] if len(a) > 2 else None))
            return orig_t(self, x, y, t, *a, **k)

        def espia_f(c, x, y, lado, estado):
            formas.append(estado)
            return orig_f(c, x, y, lado, estado)
        cv.Canvas.texto, render_png._forma = espia_t, espia_f
        try:
            c = cv.Canvas(1236, 1648, estrito=True)
            render_png._linha_claude_s10(c, m, 24, 1400, 1188, 60)
        finally:
            cv.Canvas.texto, render_png._forma = orig_t, orig_f
        return textos, formas

    def test_limites_velhos_em_cinza_medio_com_a_idade(self):
        velho = dict(CL, limites=dict(CL["limites"], idade_s=3 * 3600 + 5, velho=True))
        textos, _ = self._espiar_linha({"claude": velho, "s10": S10})
        parte = [(t, cor) for t, cor in textos if "5h 42%" in t]
        self.assertEqual(len(parte), 1)
        self.assertEqual(parte[0][1], render_png.MEDIO)
        self.assertIn("ha 3 h", parte[0][0])
        textos, _ = self._espiar_linha({"claude": CL, "s10": S10})
        parte = [(t, cor) for t, cor in textos if "5h 42%" in t]
        self.assertEqual(parte[0][1], render_png.PRETO)
        self.assertNotIn("ha ", parte[0][0])

    def test_marcas_com_bateria_nula_usb_falso_mostram_falha(self):
        textos, formas = self._espiar_linha({"claude": CL, "s10": dict(
            S10, bateria=None, caminhos={"usb": False, "adb_sem_fio": None, "vnc": "x"})})
        self.assertEqual(formas, [None, None, "falha"])  # VNC, sem fio, USB (ordem de desenho)
        self.assertIn("S10 n/d", "".join(t for t, _ in textos))

    def test_marcas_velho_ou_erro_sao_interrogacao(self):
        for s in (dict(S10, velho=True), {"erro": "n/d"}):
            _, formas = self._espiar_linha({"claude": CL, "s10": s})
            self.assertEqual(formas, [None, None, None], s)

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
            render_png._linha_claude_s10(c, {"claude": CL, "s10": S10}, 24, 1400, 1188, 60)
        finally:
            cv.Canvas.texto = orig
        txt = "".join(textos)
        self.assertIn("5h 42%", txt)
        self.assertIn("sem 18%", txt)
        self.assertIn("S10 87% carreg.", txt)
        self.assertTrue(all(ord(ch) < 128 or ch in "\u00b0\u00b7" for ch in txt))

    def test_renovado_mostra_zero_e_carga_curta(self):
        self.assertEqual(render_png._pct_txt({"pct": 0.0, "renovado": True}), "0%")
        self.assertEqual(render_png._pct_txt({"pct": 77.0, "renovado": True}), "0%")
        self.assertEqual(render_png._pct_txt(None), "n/d")
        self.assertEqual(render_png.CARGA_CURTA, {"charging": "carreg.", "full": "cheia",
                                                  "discharging": "bat.", "not_charging": "bat."})


def _tinta_gpu(dados):
    """Linhas com tinta nos primeiros 120 px do tile da GPU (resumo, 3o tile), entre o rotulo e a barra.

    Numero de 72 px (tile ativo) ocupa ~52 linhas; a palavra "desativada" (34 px) so ~26."""
    larg, alt, linhas = pixels(dados)
    return sum(1 for y in range(118, 200) if min(linhas[y][642:760]) < 100)


class GpuRamPngTest(unittest.TestCase):
    OFF = {"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 2048, "temp_c": 39}
    ON = {"util_pct": 35, "mem_usada_mb": 900, "mem_total_mb": 2048, "temp_c": 50}

    def test_dimensoes_e_menos_barras_quando_desativada(self):
        off = render_png.render_png(completo(gpu=self.OFF), historico())
        on = render_png.render_png(completo(gpu=self.ON), historico())
        self.assertEqual(ihdr(off), (1236, 1648))
        self.assertEqual(ihdr(on), (1236, 1648))
        # v5: o tile ativo tem numero grande, sparkline e barra cheia; o desativado so a palavra e a barra vazia
        self.assertGreater(_tinta_gpu(on), _tinta_gpu(off) + 15)

    def test_gpu_desativada_sem_mem_nula(self):
        g = {"util_pct": 0, "mem_usada_mb": None, "mem_total_mb": None, "temp_c": None}
        self.assertEqual(ihdr(render_png.render_png(completo(gpu=g), historico())), (1236, 1648))

    def test_uso_de_vram_sem_util_volta_layout_ativo(self):
        a = {"util_pct": 0, "mem_usada_mb": 100, "mem_total_mb": 2048, "temp_c": 40}
        on = render_png.render_png(completo(gpu=self.ON), historico())
        so_vram = render_png.render_png(completo(gpu=a), historico())
        off = render_png.render_png(completo(gpu=self.OFF), historico())
        self.assertGreater(_tinta_gpu(so_vram), _tinta_gpu(off) + 15)  # nao cai no layout "desativada"
        self.assertNotEqual(so_vram, off)

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
            render_png.desenhar(c, m, historico())
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

    def test_comandos_tambem_usa_o_motor(self):
        itens = [{"id": "a", "rotulo": "A", "grupo": "host", "estado": "ativo"}]
        m = self._sem_problemas(discos=[{"rotulo": "/", "caminho": "/", "total_b": 10**12, "usado_b": 9 * 10**11,
                                         "pct": 90.0}])
        textos = []
        orig = cv.Canvas.texto

        def espia(self, x, y, t, *a, **k):
            textos.append(t)
            return orig(self, x, y, t, *a, **k)
        cv.Canvas.texto = espia
        try:
            render_png._desenhar_comandos(cv.Canvas(1236, 1648, estrito=True), m, itens)
        finally:
            cv.Canvas.texto = orig
        self.assertIn("ATENCAO (1)", textos)
        self.assertNotIn("Tudo em ordem", textos)


if __name__ == "__main__":
    unittest.main()
