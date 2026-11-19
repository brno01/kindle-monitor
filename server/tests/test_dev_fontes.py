"""Fontes da aba Dev: sessoes do Claude Code e resumo do GitHub (dev_fontes), integracao com Coletor e alertas."""
import json
import os
import tempfile
import threading
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

    def test_leitor_que_recusa_o_arquivo_ignora_a_sessao(self):
        d = com(sessao(1))
        d.extra = [Entrada(sid(2) + ".json", 100)]

        def ler(c):
            if sid(2) in c:
                raise OSError("nao regular")  # symlink, fifo, diretorio: o leitor recusa
            return json.dumps(sessao(1))
        d.ler = ler
        self.assertEqual(coletar(d)["total"], 1)

    def test_fifo_e_symlink_reais_no_diretorio_de_sessoes(self):
        with tempfile.TemporaryDirectory() as raiz:
            with open(os.path.join(raiz, sid(1) + ".json"), "w") as f:
                json.dump(sessao(1), f)
            os.mkfifo(os.path.join(raiz, sid(2) + ".json"))
            os.symlink("/dev/zero", os.path.join(raiz, sid(3) + ".json"))
            saida = []
            t = threading.Thread(target=lambda: saida.append(
                df.coletar_sessoes(raiz, os.scandir, coletores.ler_arquivo_padrao, AGORA)), daemon=True)
            t.start()
            t.join(5)
            self.assertFalse(t.is_alive(), "coleta travou num FIFO")
            self.assertEqual(saida[0]["total"], 1)

    def test_nao_checa_tipo_antes_de_abrir(self):
        # o tipo e conferido por quem le (fstat no descritor aberto), nao por is_file + open
        d = com(sessao(1))
        d.extra = [Entrada(sid(2) + ".json", 100, regular=False)]
        pedidos = []
        d.ler = lambda c: pedidos.append(c) or json.dumps(sessao(1) if sid(1) in c else sessao(2))
        coletar(d)
        self.assertEqual(len(pedidos), 2)

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


def neutro(p):
    """O PR do formato antigo como o leitor o devolve: campos novos ausentes viram valores neutros."""
    return dict(p, revisao="nenhuma", conflito=False, idade_d=None, atualizado_d=None)


def coletar_gh(dados, agora=AGORA):
    texto = dados if isinstance(dados, str) else json.dumps(dados)
    return df.coletar_github(GH, lambda c: texto, agora)


class GithubTest(unittest.TestCase):
    def test_formato(self):
        r = coletar_gh(gh(prs=[pr(1), pr(2, rascunho=True, ci="falha")], ci=[ci(), ci("x", "falha"), ci("y", "pendente")]))
        self.assertEqual(r, {"prs": [neutro(pr(1)), neutro(pr(2, rascunho=True, ci="falha"))],
                             "ci": [ci(), ci("x", "falha"), ci("y", "pendente")],
                             "issues": None, "repos": [],
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
            self.assertLessEqual(len(t), 80)
            self.assertTrue(t.isascii() and t.isprintable(), repr(t))

    def test_titulo_500_cortado_em_80(self):
        self.assertEqual(len(coletar_gh(gh(prs=[pr(titulo="a" * 500)]))["prs"][0]["titulo"]), 80)

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


def pr2(n=1, **kw):
    """PR no formato novo (campos aditivos do claude-github)."""
    d = {"revisao": "pendente", "conflito": False, "idade_d": 3, "atualizado_d": 1}
    d.update(kw)
    return pr(n, **d)


def issue(n=5, **kw):
    d = {"repo": "dotfiles", "numero": n, "titulo": "Algo quebrou", "idade_d": 12}
    d.update(kw)
    return d


def rep(nome="dotfiles", push_d=0):
    return {"repo": nome, "push_d": push_d}


class GithubNovosCamposTest(unittest.TestCase):
    def test_formato_novo_completo(self):
        r = coletar_gh(gh(prs=[pr2(1, ), pr2(2)], issues={"n": 7, "itens": [issue(5), issue(6, idade_d=0)]},
                          repos=[rep("a", 0), rep("b", 4)]))
        self.assertEqual(r["prs"][0], dict(pr(1), revisao="pendente", conflito=False, idade_d=3, atualizado_d=1))
        self.assertEqual(r["issues"], {"n": 7, "itens": [issue(5), issue(6, idade_d=0)]})
        self.assertEqual(r["repos"], [rep("a", 0), rep("b", 4)])

    def test_formato_antigo_e_neutro(self):
        r = coletar_gh(gh())
        self.assertEqual(r["prs"][0]["revisao"], "nenhuma")
        self.assertIs(r["prs"][0]["conflito"], False)
        self.assertIsNone(r["prs"][0]["idade_d"])
        self.assertIsNone(r["prs"][0]["atualizado_d"])
        self.assertIsNone(r["issues"])
        self.assertEqual(r["repos"], [])

    def test_revisao_valores(self):
        for v in ("aprovado", "mudancas", "pendente", "nenhuma"):
            self.assertEqual(coletar_gh(gh(prs=[pr2(1, revisao=v)]))["prs"][0]["revisao"], v)
        for v in ("APROVADO", "x", None, 1, True, ["aprovado"], {}):
            self.assertEqual(coletar_gh(gh(prs=[pr2(1, revisao=v)]))["prs"][0]["revisao"], "nenhuma", repr(v))

    def test_conflito_so_true_estrito(self):
        self.assertIs(coletar_gh(gh(prs=[pr2(1, conflito=True)]))["prs"][0]["conflito"], True)
        for v in (1, "true", "sim", None, [True], 0):
            self.assertIs(coletar_gh(gh(prs=[pr2(1, conflito=v)]))["prs"][0]["conflito"], False, repr(v))

    def test_dias_do_pr_estritos(self):
        for campo in ("idade_d", "atualizado_d"):
            for v, esperado in ((0, 0), (9999, 9999), (10000, None), (-1, None), (True, None), (False, None),
                                (1.0, None), ("3", None), (None, None), ([3], None)):
                p = coletar_gh(gh(prs=[pr2(1, **{campo: v})]))["prs"][0]
                self.assertEqual(p[campo], esperado, (campo, v))

    def test_campo_novo_ruim_nao_derruba_o_pr(self):
        r = coletar_gh(gh(prs=[pr2(1, revisao="x", conflito="x", idade_d="x"), pr2(2)]))
        self.assertEqual([p["numero"] for p in r["prs"]], [1, 2])

    def test_issues_formato_e_limites(self):
        r = coletar_gh(gh(issues={"n": 9999, "itens": [issue(i) for i in range(1, 9)]}))
        self.assertEqual(r["issues"]["n"], 9999)
        self.assertEqual([i["numero"] for i in r["issues"]["itens"]], [1, 2, 3, 4, 5])

    def test_issues_n_zero_e_n_menor_que_a_lista(self):
        self.assertEqual(coletar_gh(gh(issues={"n": 0, "itens": []}))["issues"], {"n": 0, "itens": []})
        # n menor que os itens validos e incoerente: vale o numero de itens
        self.assertEqual(coletar_gh(gh(issues={"n": 1, "itens": [issue(1), issue(2)]}))["issues"]["n"], 2)

    def test_issues_forma_errada_vira_none(self):
        for v in ("x", [], 3, None, {"itens": []}, {"n": "3", "itens": []}, {"n": True, "itens": []},
                  {"n": -1, "itens": []}, {"n": 10000, "itens": []}, {"n": 2.0, "itens": []},
                  {"n": 2, "itens": "x"}, {"n": 2}):
            self.assertIsNone(coletar_gh(gh(issues=v))["issues"], repr(v))

    def test_issues_item_invalido_descartado_sem_derrubar_o_resto(self):
        itens = ["x", None, 3, issue(0, numero=-1), issue(numero=True), issue(numero="4"), issue(numero=None),
                 issue(7, idade_d=10000), issue(8, idade_d=True), issue(9)]
        r = coletar_gh(gh(issues={"n": 10, "itens": itens}))["issues"]
        self.assertEqual([i["numero"] for i in r["itens"]], [7, 8, 9])
        self.assertEqual([i["idade_d"] for i in r["itens"]], [None, None, 12])
        self.assertEqual(r["n"], 10)

    def test_issues_texto_hostil(self):
        r = coletar_gh(gh(issues={"n": 1, "itens": [issue(1, repo="\U0001F600" + "r" * 99, titulo="t\x1b[31m" + "y" * 200)]}))
        i = r["issues"]["itens"][0]
        self.assertLessEqual(len(i["repo"]), 40)
        self.assertLessEqual(len(i["titulo"]), 80)
        self.assertTrue(i["repo"].isascii() and i["repo"].isprintable())
        self.assertTrue(i["titulo"].isascii() and i["titulo"].isprintable())

    def test_repos_formato_limite_e_ordem_recebida(self):
        r = coletar_gh(gh(repos=[rep("r%d" % i, i) for i in range(9)]))["repos"]
        self.assertEqual([x["repo"] for x in r], ["r0", "r1", "r2", "r3", "r4", "r5"])

    def test_repos_item_invalido_descartado(self):
        lista = ["x", None, rep("a", -1), rep("b", True), rep("c", 10000), rep("d", "2"), {"repo": "e"},
                 {"push_d": 3}, {"repo": 5, "push_d": 1}, {"repo": "", "push_d": 1}, rep("ok", 9999)]
        self.assertEqual(coletar_gh(gh(repos=lista))["repos"], [rep("ok", 9999)])

    def test_repos_nao_lista(self):
        for v in ("x", {}, 3, None):
            self.assertEqual(coletar_gh(gh(repos=v))["repos"], [], repr(v))

    def test_novos_campos_ruins_nao_derrubam_o_arquivo(self):
        r = coletar_gh(gh(issues=object.__class__.__name__, repos=5))
        self.assertEqual(r["abertos"], 1)

    def test_empresa-x_nunca_passa_em_nenhum_item(self):
        suja = ["empresa-x-api", "x-empresa-x", "club\u200bpetro", "empresa-x"]
        prs = [pr2(i + 1, repo=s) for i, s in enumerate(suja)] + [pr2(9, titulo="ver empresa-x"), pr2(10)]
        r = coletar_gh(gh(prs=prs, ci=[ci(s) for s in suja] + [ci("ok")],
                          issues={"n": 6, "itens": [issue(i + 1, repo=s) for i, s in enumerate(suja)]
                                  + [issue(8, titulo="falha no empresa-x"), issue(9)]},
                          repos=[rep(s) for s in suja] + [rep("limpo", 1)]))
        self.assertEqual([p["numero"] for p in r["prs"]], [10])
        self.assertEqual([c["repo"] for c in r["ci"]], ["ok"])
        self.assertEqual([i["numero"] for i in r["issues"]["itens"]], [9])
        self.assertEqual([x["repo"] for x in r["repos"]], ["limpo"])
        self.assertNotIn("empresa-x", json.dumps(r).lower())


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


class LeituraRealTest(unittest.TestCase):
    """Arquivos de outro usuario: FIFO ou link em github.json / limites.json / tokens.json nao pode travar a coleta."""

    def com_prazo(self, fn):
        saida = []
        t = threading.Thread(target=lambda: saida.append(fn()), daemon=True)
        t.start()
        t.join(5)
        self.assertFalse(t.is_alive(), "coleta travou")
        return saida[0]

    def test_github_fifo(self):
        with tempfile.TemporaryDirectory() as raiz:
            caminho = os.path.join(raiz, "github.json")
            os.mkfifo(caminho)
            r = self.com_prazo(lambda: df.coletar_github(caminho, coletores.ler_arquivo_padrao, AGORA))
        self.assertEqual(r, {"erro": "n/d"})

    def test_github_symlink(self):
        with tempfile.TemporaryDirectory() as raiz:
            real = os.path.join(raiz, "real.json")
            with open(real, "w") as f:
                json.dump({"versao": 1, "gerado_em": AGORA, "prs": [], "ci": []}, f)
            caminho = os.path.join(raiz, "github.json")
            os.symlink(real, caminho)
            r = df.coletar_github(caminho, coletores.ler_arquivo_padrao, AGORA)
            self.assertEqual(r, {"erro": "n/d"})
            self.assertEqual(df.coletar_github(real, coletores.ler_arquivo_padrao, AGORA)["abertos"], 0)

    def test_github_arquivo_grande(self):
        with tempfile.TemporaryDirectory() as raiz:
            caminho = os.path.join(raiz, "github.json")
            with open(caminho, "wb") as f:
                f.write(b" " * (coletores.LIMITE_ARQUIVO_PADRAO + 10))
            r = df.coletar_github(caminho, coletores.ler_arquivo_padrao, AGORA)
        self.assertEqual(r, {"erro": "n/d"})

    def test_limites_e_tokens_fifo(self):
        with tempfile.TemporaryDirectory() as raiz:
            cfg = {}
            for nome in ("limites", "tokens"):
                cfg[nome] = os.path.join(raiz, nome + ".json")
                os.mkfifo(cfg[nome])
            r = self.com_prazo(lambda: coletores.coletar_claude(cfg, coletores.ler_arquivo_padrao, AGORA))
        self.assertIsInstance(r, dict)
