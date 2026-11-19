"""Integracao do painel do ecossistema: executor root -> JSON -> servidor web -> alertas -> imagem e texto.

1. Ponta a ponta: `aparelhos.json` e `rotinas.json` gravados pelo executor (com `executar` falso) viram, no
   Coletor, o alerta critico do gateway offline e o aviso da rotina atrasada, e as paginas desenham sem excecao.
2. Texto hostil: dados maliciosos de todas as fontes novas nunca chegam ao render_png nem ao /tela.txt fora de
   ASCII imprimivel nem acima dos limites. Estes testes olham o dado ja montado (`m`), onde a sanitizacao acontece
   (`ecossistema.sanear`); o render_png ainda limpa de novo na hora de desenhar, o que esconderia a falta dela.
"""
import datetime
import json
import os
import unittest
from unittest import mock

import _caminho  # noqa: F401
import alertas
import canvas
import coletores
import ecossistema as eco
import render
import render_png
import test_dev_fontes as tdf
from test_executor import Base, ex
from test_executor_aparelhos import TS, fixture
from test_executor_rotinas import FALHAS, SHOW, bloco

NS = 1_700_000_000
PAGINAS = ("resumo", "servicos", "detalhes", "claude", "aparelhos", "comandos")
PNG = b"\x89PNG\r\n\x1a\n"


def iso(epoch):
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Gravador:
    """Registra todo texto que o render_png manda desenhar (canvas.Canvas.texto)."""

    def __init__(self):
        self.textos = []

    def __enter__(self):
        original = canvas.Canvas.texto
        textos = self.textos

        def texto(c, x, y, t, *a, **k):
            textos.append(t)
            return original(c, x, y, t, *a, **k)

        self._p = mock.patch.object(canvas.Canvas, "texto", texto)
        self._p.start()
        return self

    def __exit__(self, *exc):
        self._p.stop()


def desenhar(m, pagina, kv=None):
    """(png, textos desenhados) da pagina; levanta se o desenho levantar."""
    with Gravador() as g:
        png = render_png.render_png(m, pagina=pagina, kindle=kv)
    return png, g.textos


# --------------------------------------------------------------------------------------- ponta a ponta

class PontaAPontaTest(Base):
    def setUp(self):
        super().setUp()
        self.cfg["aparelhos"] = ex.validar_aparelhos([
            {"id": "gw", "nome": "cerberus-gw", "rotulo": "Gateway", "icone": "rede", "alerta_offline_min": 10},
            {"id": "kindle", "nome": "kindle-monitor", "rotulo": "Kindle", "icone": "leitor"},
            {"id": "sumido", "nome": "nao-existe", "rotulo": "Sumido", "icone": "celular"}])
        self.cfg["rotinas"] = ex.validar_rotinas([
            {"id": "senhas", "rotulo": "Backup senhas", "tipo": "timer", "alvo": "backup-senhas.service",
             "max_idade_h": 26},
            {"id": "sync", "rotulo": "Sync cofre", "tipo": "timer", "alvo": "sync-cofre.service", "max_idade_h": 26}])
        # gateway offline ha 20 min; o resto como na fixture
        d = json.loads(fixture())
        gw = [p for p in d["Peer"].values() if p.get("HostName") == "cerberus-gw"][0]
        gw["Online"] = False
        gw["LastSeen"] = iso(NS - 20 * 60)
        self.ts = json.dumps(d)
        # backup das senhas rodou ha 30 h (limite 26 h); sync rodou ha 1 h; uma unidade em falha
        self.show = (0, bloco("backup-senhas.service", ts="@%d" % (NS - 30 * 3600)) + "\n"
                     + bloco("sync-cofre.service", ts="@%d" % (NS - 3600)), "")
        self.falhas = (0, "rclone-nas-sync.service loaded failed failed Sync do NAS\n", "")

    def executar(self, argv, timeout):
        if argv == TS:
            return 0, self.ts, ""
        if argv == FALHAS:
            return self.falhas
        if argv[:len(SHOW)] == SHOW:
            return self.show
        return 0, "", ""

    def rodar_executor(self):
        e = ex.Executor(self.cfg, executar=self.executar, dono=self.dono, log=self.logs.append)
        e.agora_inv = lambda: NS
        self.assertEqual(e.inventariar(), 1)

    def coletor(self, agora=NS + 5):
        estado = self.estado

        def ler(caminho):
            if not caminho.startswith(estado + "/"):
                raise OSError("fora do estado")
            with open(caminho, encoding="utf-8") as f:
                return f.read()
        cfg = {"host": "t", "comandos": {"estado": estado},
               "aparelhos": self.cfg["aparelhos"], "rotinas": self.cfg["rotinas"]}
        return coletores.Coletor(cfg, leitor_arquivo=ler, executar=lambda *a, **k: "", agora=lambda: float(agora),
                                 buscar=lambda *a, **k: "")

    def metricas(self, **kw):
        self.rodar_executor()
        return self.coletor(**kw).coletar(com_pares=False)

    def test_executor_grava_os_dois_arquivos(self):
        self.rodar_executor()
        self.assertEqual(oct(os.stat(os.path.join(self.estado, "aparelhos.json")).st_mode & 0o777), "0o644")
        self.assertEqual(oct(os.stat(os.path.join(self.estado, "rotinas.json")).st_mode & 0o777), "0o644")
        self.assertEqual(self.logs, [])

    def test_servidor_le_o_que_o_executor_gravou(self):
        m = self.metricas()
        ap = {i["id"]: i for i in m["aparelhos"]["itens"]}
        self.assertEqual(m["aparelhos"]["inventario"], "ok")
        self.assertIs(ap["gw"]["online"], False)
        self.assertEqual(ap["gw"]["offline_min"], 20)
        self.assertEqual(ap["gw"]["alerta_offline_min"], 10)
        self.assertEqual(ap["kindle"]["conexao"], "direto")
        self.assertIsNone(ap["sumido"]["online"])
        ro = {i["id"]: i for i in m["rotinas"]["itens"]}
        self.assertEqual(m["rotinas"]["inventario"], "ok")
        self.assertIs(ro["senhas"]["atrasada"], True)
        self.assertEqual(ro["senhas"]["idade_h"], 30.0)
        self.assertEqual(ro["senhas"]["resultado"], "ok")
        self.assertIs(ro["sync"]["atrasada"], False)
        self.assertEqual(m["rotinas"]["unidades_falhas"], {"n": 1, "nomes": ["rclone-nas-sync.service"]})

    def test_alertas_gateway_offline_critico_e_rotina_atrasada_aviso(self):
        r = alertas.avaliar(self.metricas())
        por_texto = {a["texto"]: a for a in r}
        gw = por_texto["Gateway offline ha 20 min"]
        self.assertEqual((gw["nivel"], gw["sistema"], gw["pagina"]), ("critico", "aparelhos", "aparelhos"))
        atrasada = por_texto["Backup senhas atrasada"]
        self.assertEqual((atrasada["nivel"], atrasada["sistema"], atrasada["pagina"]), ("aviso", "rotinas", "detalhes"))
        self.assertEqual(por_texto["1 unidade em falha: rclone-nas-sync.service"]["nivel"], "critico")
        self.assertNotIn("Sync cofre atrasada", por_texto)
        self.assertNotIn("Kindle offline", " ".join(por_texto))  # sem alerta_offline_min: nunca alerta
        # criticos antes de avisos
        niveis = [a["nivel"] for a in r]
        self.assertEqual(niveis, sorted(niveis, key=alertas.NIVEIS.index))

    def test_gateway_dentro_do_limite_nao_alerta(self):
        d = json.loads(self.ts)
        [p for p in d["Peer"].values() if p.get("HostName") == "cerberus-gw"][0]["LastSeen"] = iso(NS - 5 * 60)
        self.ts = json.dumps(d)
        self.assertFalse([a for a in alertas.avaliar(self.metricas()) if "Gateway" in a["texto"]])

    def test_inventario_do_executor_parado_vira_fonte_velha(self):
        m = self.metricas(agora=NS + 300)
        self.assertEqual(m["aparelhos"]["inventario"], "velho")
        textos = [a["texto"] for a in alertas.avaliar(m)]
        self.assertIn("Aparelhos sem atualizar ha 5 min", textos)
        self.assertIn("Rotinas sem atualizar ha 5 min", textos)
        self.assertFalse([t for t in textos if "offline" in t or "atrasada" in t])  # velho nunca vira dado

    def test_render_png_desenha_inicio_aparelhos_e_sistema(self):
        m = self.metricas()
        esperado = {"resumo": ("Gateway offline ha 20 min", "Backup senhas atrasada"),
                    "aparelhos": ("Gateway", "Kindle"),
                    "detalhes": ("Backup senhas", "rclone-nas-sync.service")}
        for pagina, trechos in esperado.items():
            with self.subTest(pagina=pagina):
                png, textos = desenhar(m, pagina)
                self.assertTrue(png.startswith(PNG))
                tudo = "\n".join(textos)
                for t in trechos:
                    self.assertIn(t, tudo)

    def test_todas_as_paginas_desenham_e_tela_txt_mostra_o_alerta(self):
        m = self.metricas()
        for pagina in PAGINAS:
            with self.subTest(pagina=pagina):
                self.assertTrue(render_png.render_png(m, pagina=pagina).startswith(PNG))
                linhas = render.render_texto(m, 60, pagina)
                self.assertTrue(all(len(l) <= 60 and l.isascii() and l.isprintable() for l in linhas))
        self.assertIn("Gateway offline ha 20 min", "\n".join(render.render_texto(m, 60, "resumo")))

    def test_catalogo_do_executor_e_do_servidor_e_o_mesmo(self):
        self.assertEqual(eco.validar_aparelhos(self.cfg["aparelhos"]), self.cfg["aparelhos"])
        self.assertEqual(eco.validar_rotinas(self.cfg["rotinas"]), self.cfg["rotinas"])


# ------------------------------------------------------------------------------------- texto hostil

HOSTIS = (
    "Café ção über",
    "emoji \U0001F600\U0001F680 fim",
    "\x1b[31mvermelho\x1b[0m\x1b]0;titulo\x07",
    "nul\x00no\x00meio",
    "A" * 500,
    "<b>&amp; \"aspas\" 'simples'</b>",
    "<script>alert(1)</script>&lt;",
    "中文 ทดสอบ",
    "tab\tquebra\nlinha\r\nfim",
    "‮rtl​zero﻿bom",
    "Z" * 80 + "\x00" + "Y" * 80,
)

LIM = {"rotulo_aparelho": 16, "rotulo_rotina": 20, "nome_unidade": 40, "projeto": 40, "repo": 40, "branch": 40,
       "titulo": 60}


def ascii_imprimivel(s):
    return isinstance(s, str) and s.isascii() and s.isprintable()


def montar_hostil():
    """Metricas com dado hostil em todas as fontes novas.

    Sessoes e GitHub entram pelo Coletor (arquivos de outro usuario). Rotulos de catalogo e nomes de unidades em
    falha entram direto nos `montar_*` (o catalogo hostil seria recusado pela validacao; e a defesa em profundidade
    de `sanear` que se testa aqui)."""
    arquivos = {}
    sessoes = []
    for i, h in enumerate(HOSTIS):
        sessoes.append(tdf.sessao(i + 1, projeto=h, estado="esperando", desde=tdf.AGORA - 3600,
                                  atualizado_em=tdf.AGORA - 5))
    d = tdf.com(*sessoes)
    arquivos[tdf.GH] = json.dumps({
        "versao": 1, "gerado_em": tdf.AGORA - 10, "dono": "brno01",
        "prs": [{"repo": h, "numero": i + 1, "titulo": h, "rascunho": i % 2 == 0, "ci": "falha"}
                for i, h in enumerate(HOSTIS)],
        "ci": [{"repo": h, "branch": h, "estado": "falha"} for h in HOSTIS]})
    cfg = {"host": "t", "claude": {"limites": "/x/l.json", "tokens": "/x/t.json", "sessoes": tdf.DIR},
           "github": {"resumo": tdf.GH}}
    m = tdf.coletor(cfg, arquivos, d).coletar(com_pares=False)
    agora = float(tdf.AGORA)
    cat_a = [{"id": "h%d" % i, "nome": "h%d" % i, "rotulo": h, "icone": "rede", "alerta_offline_min": 1}
             for i, h in enumerate(HOSTIS)]
    cat_r = [{"id": "r%d" % i, "rotulo": h, "tipo": "timer", "alvo": "x.service", "max_idade_h": 1}
             for i, h in enumerate(HOSTIS)]
    doc_a = {"gerado": tdf.AGORA - 1, "aparelhos": {c["id"]: {"online": False, "visto_em": tdf.AGORA - 7200,
                                                              "conexao": None} for c in cat_a}}
    doc_r = {"gerado": tdf.AGORA - 1,
             "rotinas": {c["id"]: {"resultado": "falha", "ultima_em": tdf.AGORA - 7200, "detalhe": h}
                         for c, h in zip(cat_r, HOSTIS)},
             "unidades_falhas": {"n": 3, "nomes": list(HOSTIS)}}
    m["aparelhos"] = eco.montar_aparelhos(cat_a, json.dumps(doc_a), agora)
    m["rotinas"] = eco.montar_rotinas(cat_r, json.dumps(doc_r), agora)
    return m


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


class TextoHostilTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = montar_hostil()

    def test_dado_hostil_chegou_ate_o_motor(self):
        # sem isto os testes abaixo passariam no vazio
        m = self.m
        self.assertEqual(len(m["aparelhos"]["itens"]), len(HOSTIS))
        self.assertEqual(len(m["rotinas"]["itens"]), len(HOSTIS))
        self.assertGreaterEqual(len(m["claude"]["sessoes"]["itens"]), len(HOSTIS) - 1)
        self.assertGreaterEqual(len(m["github"]["prs"]), len(HOSTIS) - 1)
        self.assertGreaterEqual(len(m["github"]["ci"]), len(HOSTIS) - 1)
        self.assertEqual(len(m["rotinas"]["unidades_falhas"]["nomes"]), eco.NOMES_FALHAS_MAX)
        niveis = {(a["nivel"], a["sistema"]) for a in alertas.avaliar(m)}
        for esperado in (("critico", "aparelhos"), ("critico", "rotinas"), ("aviso", "github"),
                         ("leve", "claude")):
            self.assertIn(esperado, niveis)

    def conferir_campo(self, valores, limite, rotulo):
        valores = list(valores)
        self.assertTrue(valores, rotulo)
        for v in valores:
            with self.subTest(campo=rotulo, valor=v[:30]):
                self.assertTrue(ascii_imprimivel(v), repr(v))
                self.assertLessEqual(len(v), limite)

    def test_dados_montados_sao_ascii_imprimivel_e_respeitam_os_limites(self):
        m = self.m
        self.conferir_campo((i["rotulo"] for i in m["aparelhos"]["itens"]), LIM["rotulo_aparelho"], "aparelho.rotulo")
        self.conferir_campo((i["rotulo"] for i in m["rotinas"]["itens"]), LIM["rotulo_rotina"], "rotina.rotulo")
        self.conferir_campo(m["rotinas"]["unidades_falhas"]["nomes"], LIM["nome_unidade"], "unidade")
        self.conferir_campo((i["projeto"] for i in m["claude"]["sessoes"]["itens"]), LIM["projeto"], "sessao.projeto")
        self.conferir_campo((p["repo"] for p in m["github"]["prs"]), LIM["repo"], "pr.repo")
        self.conferir_campo((p["titulo"] for p in m["github"]["prs"]), LIM["titulo"], "pr.titulo")
        self.conferir_campo((c["repo"] for c in m["github"]["ci"]), LIM["repo"], "ci.repo")
        self.conferir_campo((c["branch"] for c in m["github"]["ci"]), LIM["branch"], "ci.branch")

    def test_nenhuma_string_das_fontes_novas_foge_do_ascii(self):
        m = self.m
        for fonte in ("aparelhos", "rotinas", "github"):
            for s in strings(m[fonte]):
                with self.subTest(fonte=fonte, s=s[:30]):
                    self.assertTrue(ascii_imprimivel(s), repr(s))
                    self.assertLessEqual(len(s), 60)
        for s in strings(m["claude"]["sessoes"]):
            with self.subTest(fonte="sessoes", s=s[:30]):
                self.assertTrue(ascii_imprimivel(s), repr(s))
                self.assertLessEqual(len(s), 60)

    def test_texto_dos_alertas_e_ascii_e_ate_48(self):
        r = alertas.avaliar(self.m)
        self.assertGreaterEqual(len(r), 20)
        for a in r:
            with self.subTest(texto=a["texto"]):
                self.assertTrue(ascii_imprimivel(a["texto"]), repr(a["texto"]))
                self.assertLessEqual(len(a["texto"]), alertas.TEXTO_MAX)

    def test_texto_desenhado_so_tem_ascii_imprimivel(self):
        for pagina in PAGINAS:
            png, textos = desenhar(self.m, pagina)
            self.assertTrue(png.startswith(PNG))
            self.assertTrue(textos)
            for t in textos:
                with self.subTest(pagina=pagina, texto=t[:30]):
                    # o render_png so admite ASCII imprimivel, mais grau (0xB0) e ponto medio (0xB7)
                    self.assertTrue(all(32 <= ord(c) < 127 or c in "°·" for c in t), repr(t))
                    self.assertNotIn("A" * 61, t)
                    self.assertNotIn("Z" * 61, t)

    def test_texto_da_tela_txt_e_ascii_e_ate_60_colunas(self):
        for pagina in PAGINAS:
            for colunas in (48, 60):
                linhas = render.render_texto(self.m, colunas, pagina)
                self.assertTrue(linhas)
                for l in linhas:
                    with self.subTest(pagina=pagina, colunas=colunas, linha=l[:30]):
                        self.assertTrue(ascii_imprimivel(l), repr(l))
                        self.assertLessEqual(len(l), colunas)

    def test_tela_txt_nao_leva_controle_nem_sequencia_ansi(self):
        for pagina in PAGINAS:
            tudo = "\n".join(render.render_texto(self.m, 60, pagina))
            for ruim in ("\x1b", "\x00", "\x07", "\r", "\t"):
                self.assertNotIn(ruim, tudo, pagina)
            self.assertNotIn("A" * 61, tudo)

    def test_catalogo_hostil_e_recusado_na_validacao_do_coletor(self):
        for h in HOSTIS:
            cfg = {"host": "t", "aparelhos": [{"id": "h", "nome": "h", "rotulo": h, "icone": "rede"}],
                   "rotinas": [{"id": "h", "rotulo": h, "tipo": "timer", "alvo": "x.service", "max_idade_h": 1}]}
            if ascii_imprimivel(h) and len(h) <= 16:
                continue  # rotulo legitimo (so ASCII curto) passa; os demais precisam ser descartados
            with self.subTest(rotulo=h[:20]):
                m = tdf.coletor(cfg, {}).coletar(com_pares=False)
                self.assertNotIn("aparelhos", m)
                self.assertNotIn("rotinas", m)


if __name__ == "__main__":
    unittest.main()
