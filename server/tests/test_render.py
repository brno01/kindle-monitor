import unittest

import _caminho  # noqa: F401
import render


def local(**extra):
    m = {
        "host": "atheron",
        "gerado_em": "2026-11-15T14:32:10-03:00",
        "cpu": {"pct": 50.0},
        "carga": {"1m": 0.52, "5m": 0.48, "15m": 0.4},
        "ram": {"total_kb": 100, "usado_kb": 75, "pct": 75.0},
        "swap": {"total_kb": 100, "usado_kb": 25, "pct": 25.0},
        "uptime": {"segundos": 90061},
        "temp_cpu": {"c": 55.0},
        "gpu": {"util_pct": 12, "mem_usada_mb": 300, "mem_total_mb": 2048, "temp_c": 45},
        "discos": [{"rotulo": "NAS", "caminho": "/mnt/nas", "total_b": 10, "usado_b": 6, "pct": 60.0}],
        "servicos": [{"nome": "ragnarok.service", "ativo": True}, {"nome": "cerberus", "ativo": False}],
        "ragnarok": {"jogadores": 3, "parado": False, "idade_s": 4},
        "pares": [{"nome": "nomad", "ok": False}],
    }
    m.update(extra)
    return m


class RenderTest(unittest.TestCase):
    def test_linha_de_portas(self):
        m = local(portas=[{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True},
                          {"rotulo": "MAP", "aberto": False}])
        self.assertIn("Portas: LOGIN ok CHAR ok MAP FALHA", render.render_texto(m, 38))

    def test_portas_quebram_linha_sem_cortar(self):
        m = local(portas=[{"rotulo": "LOGIN", "aberto": False}, {"rotulo": "CHAR", "aberto": False},
                          {"rotulo": "MAP", "aberto": False}])
        linhas = render.render_texto(m, 38)
        i = [k for k, l in enumerate(linhas) if l.startswith("Portas:")][0]
        junto = " ".join(l.strip() for l in linhas[i:i + 2])
        self.assertIn("Portas: LOGIN FALHA CHAR FALHA MAP FALHA", junto)

    def test_portas_com_erro_e_sem_portas(self):
        self.assertIn("Portas: n/d", render.render_texto(local(portas={"erro": "n/d"}), 38))
        self.assertFalse([l for l in render.render_texto(local(), 38) if l.startswith("Portas")])

    def test_barra(self):
        self.assertEqual(render.barra(50, 10), "[#####-----]")
        self.assertEqual(render.barra(0, 10), "[----------]")
        self.assertEqual(render.barra(100, 10), "[##########]")
        self.assertEqual(render.barra(250, 10), "[##########]")
        self.assertEqual(render.barra(-5, 10), "[----------]")

    def test_cabecalho_com_host_e_hora(self):
        linhas = render.render_texto(local(), 38)
        self.assertIn("atheron", linhas[0])
        self.assertIn("14:32", linhas[0])
        self.assertEqual(len(linhas[0]), 38)

    def test_barra_com_percentual(self):
        linhas = render.render_texto(local(), 38)
        cpu = [l for l in linhas if l.startswith("CPU")][0]
        self.assertIn("50%", cpu)
        self.assertIn("[", cpu)

    def test_alinhamento_fixo_das_barras(self):
        linhas = render.render_texto(local(), 38)
        barras = [l for l in linhas if "[#" in l or "[-" in l]
        self.assertGreaterEqual(len(barras), 4)
        self.assertEqual(len({l.index("[") for l in barras}), 1)
        self.assertEqual(len({len(l) for l in barras}), 1)

    def test_nunca_passa_das_colunas_nem_26_linhas(self):
        m = local(
            host="h" * 80,
            discos=[{"rotulo": "R" * 50, "caminho": "/", "total_b": 1, "usado_b": 1, "pct": 100.0}] * 10,
            servicos=[{"nome": "s" * 100, "ativo": True}] * 30,
        )
        for cols in (20, 30, 38, 60):
            linhas = render.render_texto(m, cols)
            self.assertLessEqual(len(linhas), 26)
            for l in linhas:
                self.assertLessEqual(len(l), cols, l)

    def test_somente_ascii(self):
        m = local(
            host="atheron-ção",
            servicos=[{"nome": "serviço☃\n", "ativo": True}],
            discos=[{"rotulo": "Água", "caminho": "/", "total_b": 1, "usado_b": 1, "pct": 5.0}],
        )
        linhas = render.render_texto(m, 38)
        for l in linhas:
            self.assertTrue(l.isascii(), repr(l))
            self.assertNotIn("\n", l)
            self.assertTrue(l.isprintable(), repr(l))

    def test_erro_vira_nd(self):
        m = local(cpu={"erro": "n/d"}, ram={"erro": "n/d"}, gpu={"erro": "n/d"}, ragnarok={"erro": "n/d"})
        texto = "\n".join(render.render_texto(m, 38))
        self.assertIn("CPU", texto)
        self.assertGreaterEqual(texto.count("n/d"), 4)

    def test_par_sem_resposta(self):
        texto = "\n".join(render.render_texto(local(), 38))
        self.assertIn("nomad: sem resposta", texto)

    def test_par_ok_tem_secao_propria(self):
        par = {"nome": "nomad", "ok": True, "metricas": local(host="nomad", servicos=[], pares=[])}
        linhas = render.render_texto(local(pares=[par]), 38)
        texto = "\n".join(linhas)
        self.assertIn("nomad", texto)
        self.assertLessEqual(len(linhas), 26)

    def test_servicos_ok_e_falha(self):
        texto = "\n".join(render.render_texto(local(), 38))
        self.assertIn("ragnarok.service", texto)
        self.assertIn("FALHA", texto)
        self.assertRegex(texto, r"ragnarok\.service\s+ok")

    def test_ragnarok_parado(self):
        m = local(ragnarok={"jogadores": 2, "parado": True, "idade_s": 300})
        texto = "\n".join(render.render_texto(m, 38))
        self.assertIn("PARADO", texto)

    def test_metricas_vazias_nao_levantam(self):
        linhas = render.render_texto({}, 38)
        self.assertTrue(linhas)
        for l in linhas:
            self.assertLessEqual(len(l), 38)

    def test_sem_gerado_em(self):
        linhas = render.render_texto({"host": "x"}, 38)
        self.assertIn("--:--", linhas[0])

    def test_colunas_minimas(self):
        linhas = render.render_texto(local(), 5)
        for l in linhas:
            self.assertLessEqual(len(l), 5)


class RenderNovoTest(unittest.TestCase):
    RAM = {"total_kb": 20331012, "usado_kb": 7763836, "pct": 38.2}

    def test_ram_com_valor_na_mesma_linha(self):
        linhas = render.render_texto(local(ram=self.RAM), 38)
        ram = [l for l in linhas if l.startswith("RAM")][0]
        self.assertIn("7.4/19.4G", ram)
        self.assertIn("38%", ram)
        self.assertLessEqual(len(ram), 38)

    def test_ram_valor_abaixo_se_nao_couber(self):
        linhas = render.render_texto(local(ram=self.RAM), 24)
        i = [k for k, l in enumerate(linhas) if l.startswith("RAM")][0]
        self.assertNotIn("7.4/19.4G", linhas[i])
        self.assertIn("7.4/19.4G", linhas[i + 1])
        self.assertTrue(all(len(l) <= 24 for l in linhas))

    def test_gpu_desativada(self):
        g = {"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 2048, "temp_c": 39}
        linhas = render.render_texto(local(gpu=g, discos=[]), 38)
        self.assertIn("GPU   desativada 39C", linhas)
        self.assertFalse([l for l in linhas if l.startswith("VRAM")])
        self.assertFalse([l for l in linhas if l.startswith("GPU") and "[" in l])

    def test_gpu_desativada_sem_temp_e_sem_mem(self):
        linhas = render.render_texto(local(gpu={"util_pct": 0, "mem_usada_mb": None, "temp_c": None}), 38)
        self.assertIn("GPU   desativada", linhas)

    def test_gpu_ativa_volta_barra_e_vram(self):
        g = {"util_pct": 35, "mem_usada_mb": 900, "mem_total_mb": 2048, "temp_c": 50}
        linhas = render.render_texto(local(gpu=g), 38)
        self.assertTrue([l for l in linhas if l.startswith("GPU") and "35%" in l])
        self.assertTrue([l for l in linhas if l.startswith("VRAM")])

    def test_rotulo_longo_de_disco_nao_e_cortado_e_alinha(self):
        d = [{"rotulo": "NAS SSD", "total_b": 256 * 2**30, "usado_b": 100 * 2**30, "pct": 39.1, "base": 1024}]
        linhas = render.render_texto(local(discos=d), 38)
        ssd = [l for l in linhas if l.startswith("NAS SSD")]
        self.assertTrue(ssd)
        barras = [l for l in linhas if "[#" in l or "[-" in l]
        self.assertEqual(len({l.index("[") for l in barras}), 1)

    def test_disco_parado(self):
        d = [{"rotulo": "NAS SSD", "total_b": 256 * 2**30, "usado_b": 100 * 2**30, "pct": 39.1, "parado": True}]
        linhas = render.render_texto(local(discos=d), 38)
        self.assertIn("parado", [l for l in linhas if l.startswith("NAS SSD")][0])


class AtencaoTextoTest(unittest.TestCase):
    @staticmethod
    def _m(**extra):
        return local(servicos=[], pares=[], **extra)

    def test_disco_a_91_entra_na_lista_do_motor(self):
        disco = {"rotulo": "/", "caminho": "/", "total_b": 10**12, "usado_b": 91 * 10**10, "pct": 91.0}
        linhas = render.render_texto(self._m(discos=[disco]), 38)
        self.assertIn("ATENCAO (1)", linhas)
        self.assertTrue(any(l.startswith("[!] Disco /") for l in linhas), linhas)

    def test_12_alertas_mostram_6_e_mais_6(self):
        itens = [{"id": "s%d" % i, "rotulo": "S%d" % i, "grupo": "host", "estado": "falha"} for i in range(12)]
        m = self._m(servicos_kindle={"inventario": "ok", "itens": itens})
        linhas = render.render_texto(m, 60)
        self.assertIn("ATENCAO (12)", linhas)
        self.assertEqual(len([l for l in linhas if l.startswith("[X] S")]), 6)
        self.assertIn("+6", linhas)

    def test_usa_limiares_de_m(self):
        disco = {"rotulo": "/", "caminho": "/", "total_b": 10**12, "usado_b": 91 * 10**10, "pct": 91.0}
        m = self._m(discos=[disco], limiares={"disco_aviso": 95, "disco_critico": 99})
        self.assertFalse(any(l.startswith("ATENCAO") for l in render.render_texto(m, 38)))


class AtencaoKindleTextoTest(unittest.TestCase):
    def test_bateria_do_kindle_aparece_no_resumo_texto(self):
        m = {"host": "x", "cpu": {"pct": 1}}
        t = "\n".join(render.render_texto(m, 48, "resumo", 1, kindle={"bateria": 5, "carregando": False}))
        self.assertIn("Bateria do Kindle 5%", t)
        t = "\n".join(render.render_texto(m, 48, "resumo", 1))
        self.assertNotIn("Bateria do Kindle", t)


class PaginaClaudeTextoTest(unittest.TestCase):
    def test_pagina_claude_so_ascii_e_cabe(self):
        m = local() | {
            "claude": {"limites": {"cinco_horas": {"pct": 34.0, "volta_em": 1_794_000_000, "renovado": False},
                                   "semanal": {"pct": 95.0, "volta_em": 1_794_400_000, "renovado": True},
                                   "idade_s": 10, "velho": False},
                       "tokens": {"hoje": {"total": 3_100_000, "custo_usd": 1.5},
                                  "sete_dias": {"total": 950, "custo_usd": 0.1}, "idade_s": 1, "velho": False}},
            "s10": {"bateria": {"nivel": 87, "status": "charging", "temperatura_c": 36.5, "saude": "good"},
                    "caminhos": {"usb": True, "vnc": None}, "avisos": ["temperatura", "carga_cheia"],
                    "idade_s": 5, "velho": False}}
        for cols in (20, 38, 60):
            linhas = render.render_texto(m, cols, pagina="claude")
            self.assertLessEqual(len(linhas), 26)
            for l in linhas:
                self.assertTrue(l.isascii() and l.isprintable(), repr(l))
                self.assertLessEqual(len(l), cols, l)
        t = "\n".join(render.render_texto(m, 60, pagina="claude"))
        self.assertIn("5h", t)
        self.assertIn("SESSOES", t)
        self.assertIn("GITHUB", t)
        self.assertNotIn("S10", t)  # o S10 mora na pagina Aparelhos

    def test_pagina_aparelhos_so_ascii_com_kindle_e_s10(self):
        m = local() | {"s10": {"bateria": {"nivel": 87, "status": "charging", "temperatura_c": 36.5, "saude": "good"},
                               "caminhos": {"usb": True, "vnc": None}, "avisos": ["temperatura", "carga_cheia"],
                               "idade_s": 5, "velho": False}}
        kv = {"bateria": 86, "carregando": False, "temp_c": 29, "autonomia": "2 d 4 h", "wifi": 3, "wifi_ok": True,
              "aviao": False, "bt": False, "bt_conectados": 0, "tailscale": "direto", "latencia": "38 ms",
              "relogio": "ok", "whispersync": None}
        for cols in (20, 38, 60):
            linhas = render.render_texto(m, cols, pagina="aparelhos", kindle=kv)
            self.assertLessEqual(len(linhas), 26)
            for l in linhas:
                self.assertTrue(l.isascii() and l.isprintable(), repr(l))
                self.assertLessEqual(len(l), cols, l)
        t = "\n".join(render.render_texto(m, 60, pagina="aparelhos", kindle=kv))
        for esperado in ("TAILNET", "KINDLE", "bateria 86%", "S10", "87%"):
            self.assertIn(esperado, t)
        sem = "\n".join(render.render_texto(local(), 60, pagina="aparelhos"))
        self.assertIn("sem dados", sem)
        self.assertNotIn("S10", sem)
        for ruim in ({"erro": "n/d"}, "x", 5, None):
            render.render_texto(local() | {"s10": ruim}, 38, pagina="aparelhos", kindle=ruim if ruim != 5 else {})

    def test_pagina_claude_desligada_e_erros(self):
        self.assertIn("Claude desligado na config", "\n".join(render.render_texto(local(), 38, pagina="claude")))
        render.render_texto(local() | {"claude": {"erro": "n/d"}, "s10": {"erro": "n/d"}}, 38, pagina="claude")
        render.render_texto(local() | {"claude": 3, "s10": "x"}, 38, pagina="claude")


def _ap(i, rotulo, online=True, **k):
    d = {"id": i, "rotulo": rotulo, "icone": "celular", "online": online, "offline_min": None,
         "conexao": "direto" if online else None, "alerta_offline_min": None}
    d.update(k)
    return d


def _rot(i, rotulo, resultado="ok", idade_h=5.5, atrasada=False):
    return {"id": i, "rotulo": rotulo, "resultado": resultado, "ultima_em": 1_794_000_000, "idade_h": idade_h,
            "max_idade_h": 26, "atrasada": atrasada}


class TextoEcossistemaTest(unittest.TestCase):
    def _t(self, m, cols=60, **k):
        linhas = render.render_texto(m, cols, **k)
        self.assertLessEqual(len(linhas), 26)
        for l in linhas:
            self.assertTrue(l.isascii() and l.isprintable(), repr(l))
            self.assertLessEqual(len(l), cols, l)
        return "\n".join(linhas)

    def test_aparelhos_resumo_e_so_o_que_pede_atencao(self):
        its = [_ap("a", "Notebook"), _ap("b", "S22", online=False, offline_min=95),
               _ap("c", "Gateway", online=False, offline_min=20, alerta_offline_min=10),
               _ap("d", "Games", online=None), _ap("e", "Kindle")]
        m = local(aparelhos={"inventario": "ok", "idade_s": 3, "itens": its})
        t = self._t(m, pagina="aparelhos")
        for esperado in ("TAILNET 2 de 5 online", "[ ] S22 offline ha 1 h", "[X] Gateway offline ha 20 min",
                         "[?] Games sem dado", "KINDLE"):
            self.assertIn(esperado, t)
        self.assertNotIn("Notebook", t)

    def test_aparelhos_todos_online_uma_linha(self):
        m = local(aparelhos={"inventario": "ok", "idade_s": 3, "itens": [_ap("a", "A"), _ap("b", "B")]})
        self.assertIn("TAILNET 2 de 2 online\n", self._t(m, pagina="aparelhos") + "\n")

    def test_aparelhos_inventario_velho_e_sem_chave(self):
        m = local(aparelhos={"inventario": "velho", "idade_s": 300, "itens": [_ap("a", "A", online=None)]})
        t = self._t(m, pagina="aparelhos")
        self.assertIn("TAILNET", t)
        self.assertIn("sem dados (inventario sem atualizar)", t)
        self.assertIn("sem dados", self._t(local(), pagina="aparelhos"))

    def test_aparelhos_16_com_s10_cabem_e_cortam_com_mais_n(self):
        its = [_ap("i%d" % k, "Aparelho %02d" % k, online=False, offline_min=k) for k in range(16)]
        its[9].update(alerta_offline_min=1)
        m = local(aparelhos={"inventario": "ok", "idade_s": 3, "itens": its},
                  s10={"bateria": {"nivel": 87}, "caminhos": {"usb": True}, "avisos": [], "idade_s": 1, "velho": False})
        for cols in (20, 38, 60):
            t = self._t(m, cols, pagina="aparelhos", kindle={"bateria": 50})
            self.assertIn("+", t)
            self.assertIn("S10", t)
        self.assertIn("[X] Aparelho 09", self._t(m, pagina="aparelhos"))

    def test_aparelhos_rotulo_hostil_e_blocos_ruins(self):
        m = local(aparelhos={"inventario": "ok", "idade_s": 3,
                             "itens": [_ap("a", "\u00e7\u00e3o\x1b[0m" * 3, online=False, offline_min=3)]})
        self._t(m, 20, pagina="aparelhos")
        for ruim in (None, 5, "x", [], {"itens": "x"}, {"inventario": "ok", "itens": [None, 5, {"online": 3}]}):
            self._t(local(aparelhos=ruim), 38, pagina="aparelhos")

    def test_rotinas_na_tela_principal_e_uma_linha_com_o_problema_no_atencao(self):
        its = [_rot("a", "Backup senhas"), _rot("b", "Segundo cerebro", atrasada=True, idade_h=31),
               _rot("c", "Sync cofre", resultado="falha"), _rot("d", "Tokens", resultado="desconhecido", idade_h=None)]
        m = local(rotinas={"inventario": "ok", "idade_s": 3, "itens": its,
                           "unidades_falhas": {"n": 2, "nomes": ["a.service", "b.service"]}})
        linhas = render.render_texto(m, 60)
        self.assertEqual([l for l in linhas if l.startswith("Rotinas")], ["Rotinas: 1 de 4 ok"])
        t = "\n".join(linhas)
        self.assertIn("ATENCAO", t)
        self.assertIn("Sync cofre falhou", t)  # o detalhe vem do motor de alertas
        self.assertTrue(all(l.isascii() and l.isprintable() and len(l) <= 60 for l in linhas))

    def test_rotinas_ok_velho_e_ausente(self):
        ok = local(rotinas={"inventario": "ok", "idade_s": 3, "itens": [_rot("a", "A")],
                            "unidades_falhas": {"n": 0, "nomes": []}})
        self.assertIn("Rotinas: 1 de 1 ok", self._t(ok))
        velho = local(rotinas={"inventario": "velho", "idade_s": 300, "itens": [_rot("a", "A", resultado="desconhecido")],
                               "unidades_falhas": {"n": 0, "nomes": []}})
        self.assertIn("Rotinas: sem dados", self._t(velho))
        self.assertNotIn("Rotinas", self._t(local()))

    def test_rotinas_16_e_blocos_ruins_nao_estouram(self):
        its = [_rot("r%d" % k, "Rotina %02d" % k, resultado="falha") for k in range(16)]
        m = local(rotinas={"inventario": "ok", "idade_s": 3, "itens": its, "unidades_falhas": {"n": 0, "nomes": []}})
        self.assertIn("Rotinas: 0 de 16 ok", self._t(m, 38))
        for ruim in (None, 5, "x", [], {"itens": "x"}, {"inventario": "ok", "itens": [None, 5, {"resultado": 3}]}):
            self._t(local(rotinas=ruim), 38)


if __name__ == "__main__":
    unittest.main()
