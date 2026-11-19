"""Fontes da aba Dev: sessoes do Claude Code e resumo do GitHub (dev_fontes), integracao com Coletor e alertas."""
import json
import unittest

import _caminho  # noqa: F401
import alertas
import coletores
import dev_fontes as df

AGORA = 1_700_000_000
DIR = "/var/lib/claude-uso/sessoes"
GH = "/var/lib/claude-uso/github.json"


class _St:
    def __init__(self, n, mtime=0):
        self.st_size = n
        self.st_mtime = mtime


class Entrada:
    """Imita os.DirEntry."""

    def __init__(self, nome, tamanho=100, regular=True, mtime=0):
        self.name = nome
        self._n = tamanho
        self._reg = regular
        self._mtime = mtime

    def is_file(self, follow_symlinks=True):
        assert follow_symlinks is False
        return self._reg

    def stat(self, follow_symlinks=True):
        assert follow_symlinks is False
        return _St(self._n, self._mtime)


def sid(n):
    return "%08x-aaaa" % n


def sessao(n=1, **kw):
    d = {"versao": 1, "id": sid(n), "projeto": "kindle-monitor", "estado": "trabalhando",
         "desde": AGORA - 60, "atualizado_em": AGORA - 10}
    d.update(kw)
    return d


class Dir:
    """Diretorio falso: listar(dir) e ler(caminho)."""

    def __init__(self, arquivos, entradas_extra=()):
        self.arquivos = dict(arquivos)  # nome -> texto
        self.extra = list(entradas_extra)

    def listar(self, d):
        if d != DIR:
            raise FileNotFoundError(d)
        return iter([Entrada(n, len(t)) for n, t in self.arquivos.items()] + self.extra)

    def ler(self, caminho):
        return self.arquivos[caminho.rsplit("/", 1)[1]]


def com(*sessoes):
    return Dir({s["id"] + ".json": json.dumps(s) for s in sessoes})


def coletar(d):
    return df.coletar_sessoes(DIR, d.listar, d.ler, AGORA)


class SessoesTest(unittest.TestCase):
    def test_formato(self):
        r = coletar(com(sessao(1, estado="esperando", desde=AGORA - 900)))
        self.assertEqual(r, {"itens": [{"projeto": "kindle-monitor", "estado": "esperando", "desde_s": 900}],
                             "total": 1, "esperando": 1, "idade_s": 10})

    def test_vazio(self):
        self.assertEqual(coletar(Dir({})), {"itens": [], "total": 0, "esperando": 0, "idade_s": None})

    def test_diretorio_ausente(self):
        self.assertEqual(df.coletar_sessoes("/var/lib/nada", Dir({}).listar, Dir({}).ler, AGORA), {"erro": "n/d"})

    def test_symlink_e_nao_regular_ignorados(self):
        d = com(sessao(1))
        d.extra = [Entrada(sid(2) + ".json", 100, regular=False)]  # symlink, fifo, diretorio: nao regular
        d.ler = lambda c: json.dumps(sessao(1) if sid(1) in c else sessao(2))
        r = coletar(d)
        self.assertEqual(r["total"], 1)

    def test_arquivo_grande_ignorado(self):
        grande = json.dumps(sessao(2, projeto="x" * 8000))
        d = com(sessao(1))
        d.arquivos[sid(2) + ".json"] = grande
        self.assertEqual(coletar(d)["total"], 1)

    def test_arquivo_que_cresceu_depois_do_stat_ignorado(self):
        d = com(sessao(1))
        nome = sid(2) + ".json"
        d.arquivos[nome] = json.dumps(sessao(2, projeto="x" * 8000))
        d.extra = []
        original = d.listar
        d.listar = lambda x: iter([e if e.name != nome else Entrada(nome, 10) for e in original(x)])
        self.assertEqual(coletar(d)["total"], 1)

    def test_nome_fora_do_padrao_ignorado(self):
        d = com(sessao(1))
        for nome in ("README.json", "ABCDEF12.json", "%s.txt" % sid(2), ".%s.tmp" % sid(2), "../x.json"):
            d.arquivos[nome] = json.dumps(sessao(2))
        self.assertEqual(coletar(d)["total"], 1)

    def test_id_diferente_do_nome_ignorado(self):
        d = Dir({sid(1) + ".json": json.dumps(sessao(2))})
        self.assertEqual(coletar(d)["total"], 0)

    def test_json_ruim_ignorado(self):
        d = com(sessao(1))
        d.arquivos[sid(2) + ".json"] = "{nao e json"
        d.arquivos[sid(3) + ".json"] = "[1, 2]"
        d.arquivos[sid(4) + ".json"] = ""
        self.assertEqual(coletar(d)["total"], 1)

    def test_tipos_errados_ignorados(self):
        ruins = [sessao(2, versao=2), sessao(3, desde="1"), sessao(4, atualizado_em=True), sessao(5, desde=-1),
                 sessao(6, atualizado_em=None), sessao(7, desde=1.5), sessao(8, estado=["esperando"])]
        self.assertEqual(coletar(com(sessao(1), *ruins))["total"], 1)

    def test_estado_desconhecido_ignorado(self):
        self.assertEqual(coletar(com(sessao(1), sessao(2, estado="dormindo")))["total"], 1)

    def test_mais_de_10_min_ignorada(self):
        r = coletar(com(sessao(1, atualizado_em=AGORA - 599), sessao(2, atualizado_em=AGORA - 600),
                        sessao(3, atualizado_em=AGORA - 3600)))
        self.assertEqual(r["total"], 1)
        self.assertEqual(r["idade_s"], 599)

    def test_desde_no_futuro_vira_zero(self):
        r = coletar(com(sessao(1, desde=AGORA + 5000)))
        self.assertEqual(r["itens"][0]["desde_s"], 0)

    def test_sessoes_velhas_nao_escondem_a_viva_de_nome_maior(self):
        # 60 sessoes que nunca ganharam SessionEnd (crash) e uma viva cujo nome (uuid) ordena depois de todas
        velhas = [sessao(n, atualizado_em=AGORA - 3600) for n in range(1, 61)]
        viva = sessao(0xfffffff0)
        arquivos = {s["id"] + ".json": json.dumps(s) for s in velhas + [viva]}
        mtimes = {s["id"] + ".json": AGORA - 3600 for s in velhas}
        mtimes[viva["id"] + ".json"] = AGORA - 10
        d = Dir(arquivos)
        d.listar = lambda x: iter([Entrada(n, len(t), mtime=mtimes[n]) for n, t in arquivos.items()])
        r = coletar(d)
        self.assertEqual((r["total"], [i["projeto"] for i in r["itens"]]), (1, ["kindle-monitor"]))
        self.assertEqual(r["idade_s"], 10)

    def test_le_as_50_mais_recentes_e_nao_as_50_primeiras_por_nome(self):
        ss = [sessao(n) for n in range(1, 71)]  # todas vivas; so as 50 de mtime mais novo entram
        arquivos = {s["id"] + ".json": json.dumps(s) for s in ss}
        d = Dir(arquivos)
        d.listar = lambda x: iter([Entrada(n, len(t), mtime=AGORA - 100 + int(n[:8], 16))
                                   for n, t in arquivos.items()])  # nome maior = mais recente
        lidos = []
        ler = d.ler
        d.ler = lambda c: (lidos.append(c.rsplit("/", 1)[1]), ler(c))[1]
        r = coletar(d)
        self.assertEqual(r["total"], 50)
        self.assertEqual(sorted(lidos), sorted(s["id"] + ".json" for s in ss[20:]))

    def test_limite_de_500_entradas_varridas_continua(self):
        arquivos = {sid(n) + ".json": json.dumps(sessao(n)) for n in range(1, 601)}
        d = Dir(arquivos)
        vistas = []
        d.listar = lambda x: (vistas.append(n) or Entrada(n, 10, mtime=AGORA - 5) for n in arquivos)
        self.assertEqual(coletar(d)["total"], 50)
        self.assertEqual(len(vistas), 500)

    def test_atualizado_em_adiantado_mais_de_60_s_ignorado(self):
        self.assertEqual(coletar(com(sessao(1, atualizado_em=AGORA + 61)))["total"], 0)
        self.assertEqual(coletar(com(sessao(1, atualizado_em=AGORA + 60)))["total"], 1)

    def test_atualizado_em_muito_no_futuro_ignorado(self):
        self.assertEqual(coletar(com(sessao(1, atualizado_em=AGORA + 3600)))["total"], 0)
        self.assertEqual(coletar(com(sessao(1, atualizado_em=AGORA + 30)))["total"], 1)

    def test_projeto_hostil(self):
        for hostil in ("proj\x1b[31mX", "\U0001F600" * 20 + "ok", "a" * 500, "café", "\x00\x07"):
            r = coletar(com(sessao(1, projeto=hostil)))
            p = r["itens"][0]["projeto"]
            self.assertLessEqual(len(p), 40)
            self.assertTrue(p.isascii() and p.isprintable(), repr(p))
            self.assertTrue(p)  # nunca vazio

    def test_projeto_nao_texto(self):
        r = coletar(com(sessao(1, projeto=123)))
        self.assertEqual(r["itens"][0]["projeto"], "sessao")

    def test_mais_de_12_sessoes(self):
        r = coletar(com(*[sessao(n, desde=AGORA - 100 - n, projeto="p%d" % n) for n in range(1, 31)]))
        self.assertEqual(r["total"], 30)
        self.assertEqual(len(r["itens"]), 12)
        self.assertEqual([i["projeto"] for i in r["itens"]][:2], ["p1", "p2"])  # as mais recentes primeiro
        self.assertEqual(r["itens"], sorted(r["itens"], key=lambda i: i["desde_s"]))

    def test_le_no_maximo_50_arquivos(self):
        d = com(*[sessao(n) for n in range(1, 121)])
        lidos = []
        ler = d.ler
        d.ler = lambda c: (lidos.append(c), ler(c))[1]
        r = df.coletar_sessoes(DIR, d.listar, d.ler, AGORA)
        self.assertEqual(len(lidos), 50)
        self.assertEqual(r["total"], 50)

    def test_varredura_limitada(self):
        n = [0]

        def listar(_d):
            def gera():
                while True:
                    n[0] += 1
                    yield Entrada("lixo%d" % n[0])
            return gera()

        r = df.coletar_sessoes(DIR, listar, lambda c: "", AGORA)
        self.assertEqual(r["total"], 0)
        self.assertEqual(n[0], df.SESSOES_VARRER_MAX)

    def test_fecha_o_iterador(self):
        fechou = []

        class It:
            def __iter__(self):
                return iter([])

            def close(self):
                fechou.append(1)

        df.coletar_sessoes(DIR, lambda d: It(), lambda c: "", AGORA)
        self.assertEqual(fechou, [1])

    def test_ler_que_falha_so_perde_o_arquivo(self):
        d = com(sessao(1), sessao(2))
        ler = d.ler

        def ler_ruim(c):
            if sid(2) in c:
                raise PermissionError(c)
            return ler(c)

        self.assertEqual(df.coletar_sessoes(DIR, d.listar, ler_ruim, AGORA)["total"], 1)

    def test_esperando_contado(self):
        r = coletar(com(sessao(1, estado="esperando"), sessao(2, estado="esperando"), sessao(3), sessao(4, estado="aberta")))
        self.assertEqual((r["total"], r["esperando"]), (4, 2))

    def test_scandir_real(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            ok = os.path.join(t, sid(1) + ".json")
            with open(ok, "w") as f:
                json.dump(sessao(1), f)
            os.symlink(ok, os.path.join(t, sid(2) + ".json"))
            with open(os.path.join(t, sid(3) + ".json"), "w") as f:
                f.write(" " * 5000)

            def ler(c):
                with open(c) as f:
                    return f.read()

            r = df.coletar_sessoes(t, os.scandir, ler, AGORA)
        self.assertEqual(r["total"], 1)


# ------------------------------------------------------------------------------------------------ github

def pr(n=1, **kw):
    d = {"repo": "kindle-monitor", "numero": n, "titulo": "Add painel", "rascunho": False, "ci": "ok"}
    d.update(kw)
    return d


def ci(repo="kindle-monitor", estado="ok", **kw):
    d = {"repo": repo, "branch": "master", "estado": estado}
    d.update(kw)
    return d


def gh(**kw):
    d = {"versao": 1, "gerado_em": AGORA - 120, "dono": "brno01", "prs": [pr()], "ci": [ci()]}
    d.update(kw)
    return d


def coletar_gh(dados, agora=AGORA):
    texto = dados if isinstance(dados, str) else json.dumps(dados)
    return df.coletar_github(GH, lambda c: texto, agora)


class GithubTest(unittest.TestCase):
    def test_formato(self):
        r = coletar_gh(gh(prs=[pr(1), pr(2, rascunho=True, ci="falha")], ci=[ci(), ci("x", "falha"), ci("y", "pendente")]))
        self.assertEqual(r, {"prs": [pr(1), pr(2, rascunho=True, ci="falha")],
                             "ci": [ci(), ci("x", "falha"), ci("y", "pendente")],
                             "abertos": 2, "ci_falhas": 1, "idade_s": 120, "velho": False})

    def test_velho_acima_de_1200(self):
        self.assertFalse(coletar_gh(gh(gerado_em=AGORA - 1200))["velho"])
        r = coletar_gh(gh(gerado_em=AGORA - 1201))
        self.assertTrue(r["velho"])
        self.assertEqual(r["idade_s"], 1201)

    def test_gerado_no_futuro(self):
        r = coletar_gh(gh(gerado_em=AGORA + 999))
        self.assertEqual((r["idade_s"], r["velho"]), (0, False))

    def test_ausente_e_json_ruim(self):
        def falta(c):
            raise FileNotFoundError(c)

        self.assertEqual(df.coletar_github(GH, falta, AGORA), {"erro": "n/d"})
        for ruim in ("", "{x", "[]", "null", "123"):
            self.assertEqual(coletar_gh(ruim), {"erro": "n/d"}, ruim)

    def test_forma_errada(self):
        for dados in (gh(versao=2), gh(gerado_em="1"), gh(gerado_em=None), gh(prs={}), gh(ci="x"), gh(prs=None)):
            self.assertEqual(coletar_gh(dados), {"erro": "n/d"})

    def test_arquivo_enorme(self):
        self.assertEqual(coletar_gh(gh(prs=[pr(titulo="x" * 100000)])), {"erro": "n/d"})

    def test_titulo_hostil(self):
        for hostil in ("\U0001F600 fix \x1b[31mvermelho\x1b[0m", "t" * 500, "café ‮\u0000", "\x1b]0;x\x07"):
            r = coletar_gh(gh(prs=[pr(titulo=hostil)]))
            t = r["prs"][0]["titulo"]
            self.assertLessEqual(len(t), 60)
            self.assertTrue(t.isascii() and t.isprintable(), repr(t))

    def test_titulo_500_cortado_em_60(self):
        self.assertEqual(len(coletar_gh(gh(prs=[pr(titulo="a" * 500)]))["prs"][0]["titulo"]), 60)

    def test_repo_e_branch_saneados(self):
        r = coletar_gh(gh(prs=[pr(repo="\U0001F600" + "r" * 100)], ci=[ci(repo="a\x1bb" * 30, branch="b" * 200)]))
        self.assertLessEqual(len(r["prs"][0]["repo"]), 40)
        self.assertLessEqual(len(r["ci"][0]["repo"]), 40)
        self.assertEqual(len(r["ci"][0]["branch"]), 40)
        for s in (r["prs"][0]["repo"], r["ci"][0]["repo"], r["ci"][0]["branch"]):
            self.assertTrue(s.isascii() and s.isprintable())

    def test_mais_de_20_prs_e_30_ci(self):
        r = coletar_gh(gh(prs=[pr(n) for n in range(1, 60)], ci=[ci("r%d" % n, "falha") for n in range(50)]))
        self.assertEqual((len(r["prs"]), r["abertos"]), (20, 20))
        self.assertEqual((len(r["ci"]), r["ci_falhas"]), (30, 30))

    def test_entradas_ruins_ignoradas(self):
        r = coletar_gh(gh(prs=["x", None, pr(1), pr("2"), pr(True), pr(-3), pr(4, ci="amarelo", rascunho="sim")],
                          ci=[ci(), ci(estado="?"), "x", 3, ci(estado=None)]))
        self.assertEqual([p["numero"] for p in r["prs"]], [1, 4])
        self.assertIsNone(r["prs"][1]["ci"])
        self.assertIs(r["prs"][1]["rascunho"], False)
        self.assertEqual(len(r["ci"]), 1)

    def test_titulo_nao_texto(self):
        self.assertEqual(coletar_gh(gh(prs=[pr(titulo=["a"])]))["prs"][0]["titulo"], "")


# ----------------------------------------------------------------------------- Coletor e alertas

def leitor(arquivos, d):
    def ler(caminho):
        if caminho in arquivos:
            return arquivos[caminho]
        if caminho.startswith(DIR + "/") and caminho.rsplit("/", 1)[1] in d.arquivos:
            return d.ler(caminho)
        raise FileNotFoundError(caminho)
    return ler


def coletor(cfg, arquivos, d=None):
    d = d or Dir({})
    return coletores.Coletor(cfg, leitor_arquivo=leitor(arquivos, d), listar_dir=d.listar, agora=lambda: float(AGORA),
                             executar=lambda *a, **k: "", buscar=lambda *a, **k: None)


CLAUDE = {"limites": "/x/l.json", "tokens": "/x/t.json"}


class ColetorTest(unittest.TestCase):
    def test_sem_config_nao_existem(self):
        m = coletor({"claude": dict(CLAUDE)}, {}).coletar(com_pares=False)
        self.assertNotIn("sessoes", m["claude"])
        self.assertNotIn("github", m)
        m = coletor({}, {}).coletar(com_pares=False)
        self.assertNotIn("claude", m)
        self.assertNotIn("github", m)

    def test_sessoes_com_config(self):
        d = com(sessao(1, estado="esperando", desde=AGORA - 30))
        m = coletor({"claude": dict(CLAUDE, sessoes=DIR)}, {}, d).coletar(com_pares=False)
        self.assertEqual(m["claude"]["sessoes"]["total"], 1)
        self.assertEqual(m["claude"]["limites"], {"erro": "n/d"})  # as outras partes seguem independentes

    def test_sessoes_diretorio_ausente(self):
        m = coletor({"claude": dict(CLAUDE, sessoes="/var/lib/claude-uso/outro")}, {}, Dir({})).coletar(com_pares=False)
        self.assertEqual(m["claude"]["sessoes"], {"erro": "n/d"})

    def test_caminhos_invalidos(self):
        for ruim in ("sessoes", "/etc/sessoes", "/var/lib/../etc", "/var/lib//x", "/var/libx/y", "/var/lib/x/",
                     "/tmp/x", 5, ["/var/lib/x"], "/var/lib/a\x00b"):
            m = coletor({"claude": dict(CLAUDE, sessoes=ruim), "github": {"resumo": ruim}}, {}, Dir({})).coletar(
                com_pares=False)
            if ruim:
                self.assertEqual(m["claude"]["sessoes"], {"erro": "n/d"}, repr(ruim))
                self.assertEqual(m["github"], {"erro": "n/d"}, repr(ruim))

    def test_caminho_run_valido(self):
        self.assertEqual(coletores._caminho_dev("/run/claude/sessoes"), "/run/claude/sessoes")

    def test_github_com_config(self):
        m = coletor({"github": {"resumo": GH}}, {GH: json.dumps(gh())}).coletar(com_pares=False)
        self.assertEqual(m["github"]["abertos"], 1)

    def test_github_arquivo_ausente(self):
        m = coletor({"github": {"resumo": GH}}, {}).coletar(com_pares=False)
        self.assertEqual(m["github"], {"erro": "n/d"})

    def test_github_config_malformada(self):
        for cfg in ({"github": "x"}, {"github": {}}, {"github": {"resumo": ""}}, {"github": []}):
            self.assertNotIn("github", coletor(cfg, {}).coletar(com_pares=False))

    def test_claude_nao_dict_nao_derruba(self):
        m = coletor({"claude": "x"}, {}).coletar(com_pares=False)
        self.assertNotIn("sessoes", m["claude"])

    def test_ponta_a_ponta_com_alertas(self):
        d = com(sessao(1, estado="esperando", desde=AGORA - 15 * 60, projeto="kindle-monitor"),
                sessao(2, estado="trabalhando", desde=AGORA - 3600),
                sessao(3, estado="esperando", desde=AGORA - 60),
                sessao(4, estado="esperando", desde=AGORA - 99999, atualizado_em=AGORA - 3600))  # fantasma
        arquivos = {GH: json.dumps(gh(ci=[ci("kindle-monitor", "falha"), ci("outro", "ok")]))}
        cfg = {"claude": dict(CLAUDE, sessoes=DIR), "github": {"resumo": GH}}
        m = coletor(cfg, arquivos, d).coletar(com_pares=False)
        self.assertEqual(m["claude"]["sessoes"]["total"], 3)
        lista = alertas.avaliar(m)
        leves = [a for a in lista if a["nivel"] == "leve"]
        self.assertEqual(len(leves), 1)
        self.assertIn("kindle-monitor", leves[0]["texto"])
        self.assertIn("15 min", leves[0]["texto"])
        self.assertEqual(leves[0]["sistema"], "claude")
        avisos = [a for a in lista if a["sistema"] == "github"]
        self.assertEqual([(a["nivel"], a["texto"]) for a in avisos], [("aviso", "CI falhou em kindle-monitor")])

    def test_github_velho_vira_aviso_de_fonte(self):
        arquivos = {GH: json.dumps(gh(gerado_em=AGORA - 3000))}
        m = coletor({"github": {"resumo": GH}}, arquivos).coletar(com_pares=False)
        textos = [a["texto"] for a in alertas.avaliar(m) if a["sistema"] == "github"]
        self.assertEqual(textos, ["GitHub sem atualizar ha 50 min"])


if __name__ == "__main__":
    unittest.main()
