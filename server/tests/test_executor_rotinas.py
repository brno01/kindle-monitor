"""Executor: rotinas (validar_rotinas, coletar_rotinas, inventariar -> rotinas.json)."""
import json
import os
import subprocess
import tempfile
import unittest

import _caminho  # noqa: F401
from test_executor import Base, ex

NS = 1_700_000_000
SHOW = ["systemctl", "show", "-p", "Id", "-p", "Result", "-p", "LoadState", "-p", "ExecMainStatus",
        "-p", "ExecMainExitTimestamp", "--timestamp=unix", "--"]
FALHAS = ["systemctl", "list-units", "--failed", "--plain", "--no-legend", "--no-pager"]


def timer(**k):
    d = {"id": "senhas", "rotulo": "Backup senhas", "tipo": "timer", "alvo": "backup-senhas.service",
         "max_idade_h": 26}
    d.update(k)
    return d


def arq(**k):
    d = {"id": "painel", "rotulo": "Tokens Claude", "tipo": "arquivo", "alvo": "/var/lib/claude-uso/tokens.json",
         "max_idade_h": 1}
    d.update(k)
    return d


def bloco(i, result="success", load="loaded", status="0", ts="@1699990000"):
    # mesma forma da saida real (chaves fora da ordem pedida, bloco separado por linha em branco)
    return "Result=%s\nExecMainExitTimestamp=%s\nExecMainStatus=%s\nId=%s\nLoadState=%s\n" % (
        result, ts, status, i, load)


class FakeSys:
    """Executar injetavel: responde ao `show` e ao `list-units`; grava (argv, timeout)."""
    def __init__(self, show=(0, "", ""), falhas=(0, "", "")):
        self.show, self.falhas, self.chamadas = show, falhas, []

    def __call__(self, argv, timeout):
        self.chamadas.append((list(argv), timeout))
        r = self.falhas if argv == FALHAS else self.show if argv[:len(SHOW)] == SHOW else (0, "", "")
        if isinstance(r, BaseException):
            raise r
        return r


def coletar(catalogo, fake, **kw):
    kw.setdefault("agora", lambda: NS)
    return ex.coletar_rotinas(ex.validar_rotinas(catalogo), fake, **kw)


def so_ascii_sem_controle(teste, texto):
    teste.assertTrue(texto.isascii(), texto)
    teste.assertTrue(all(c >= " " for c in texto), texto)


class ValidarTest(unittest.TestCase):
    def ruim(self, lista, trecho=None):
        with self.assertRaises(ValueError) as c:
            ex.validar_rotinas(lista)
        if trecho:
            self.assertIn(trecho, str(c.exception))

    def test_valido(self):
        self.assertEqual(ex.validar_rotinas([timer(), arq()]), [timer(), arq()])
        self.assertEqual(ex.validar_rotinas(None), [])
        self.assertEqual(ex.validar_rotinas([]), [])

    def test_nao_e_lista_ou_item_nao_e_objeto(self):
        self.ruim({"id": "x"})
        self.ruim("senhas")
        self.ruim(["senhas"])

    def test_maximo_16(self):
        ok = [timer(id="t%d" % i) for i in range(16)]
        self.assertEqual(len(ex.validar_rotinas(ok)), 16)
        self.ruim(ok + [timer(id="z")])

    def test_id(self):
        for ruim in ("", "A", "a b", "a_b", "x" * 25, 3, None, "a\n"):
            self.ruim([timer(id=ruim)], "id")
        self.ruim([timer(id="x")] + [timer(id="x")], "repetido")

    def test_rotulo(self):
        for ruim in ("", "x" * 21, "Coração", "a\nb", "a\x00", 3, None):
            self.ruim([timer(rotulo=ruim)], "rotulo")
        self.assertEqual(len(ex.validar_rotinas([timer(rotulo="x" * 20)])), 1)

    def test_tipo(self):
        for ruim in ("cron", "", None, "Timer"):
            self.ruim([timer(tipo=ruim)], "tipo")

    def test_alvo_timer(self):
        for ok in ("a.service", "cerberus-vault-backup.service", "x@y.service", "A_b.z-1.service"):
            self.assertEqual(len(ex.validar_rotinas([timer(alvo=ok)])), 1)
        for ruim in ("a.timer", "a", ".service", "a b.service", "a;b.service", "a/b.service", "a.service\n",
                     "x" * 65 + ".service", 3, None, "a.service ", "á.service"):
            self.ruim([timer(alvo=ruim)], "alvo")

    def test_alvo_arquivo(self):
        for ok in ("/srv/x", "/var/lib/a/b.json", "/var/backups/pg", "/srv/nas/dir"):
            self.assertEqual(len(ex.validar_rotinas([arq(alvo=ok)])), 1)
        for ruim in ("srv/x", "/srv", "/etc/passwd", "/srv/../etc/passwd", "/srv//x", "/srv/./x", "/srv/x/",
                     "/var/libx/y", "~/x", "/tmp/srv/x", 3, None, ""):
            self.ruim([arq(alvo=ruim)], "alvo")

    def test_max_idade_h(self):
        for ok in (0.1, 1, 26, 720, 720.0, 0.5):
            self.assertEqual(len(ex.validar_rotinas([timer(max_idade_h=ok)])), 1)
        for ruim in (0, 0.09, 721, -1, True, False, "26", None, float("nan"), float("inf")):
            self.ruim([timer(max_idade_h=ruim)], "max_idade_h")
        self.ruim([{k: v for k, v in timer().items() if k != "max_idade_h"}], "max_idade_h")

    def test_chave_desconhecida_ou_ausente(self):
        self.ruim([timer(extra=1)], "chave")
        self.ruim([{k: v for k, v in timer().items() if k != "alvo"}], "alvo")

    def test_devolve_copias(self):
        orig = [timer()]
        saida = ex.validar_rotinas(orig)
        saida[0]["rotulo"] = "mudou"
        self.assertEqual(orig[0]["rotulo"], "Backup senhas")


class ParseShowTest(unittest.TestCase):
    def test_blocos_por_id(self):
        d = ex.parse_show(bloco("a.service") + "\n" + bloco("b.service", result="exit-code", status="1"))
        self.assertEqual(d["a.service"]["Result"], "success")
        self.assertEqual(d["b.service"]["ExecMainStatus"], "1")

    def test_lixo_e_chaves_extras_ignorados(self):
        d = ex.parse_show("Id=a.service\nCoisa=x\nsem igual\n\n\n\nResult=success\n\nId=b.service\nResult=failed\n")
        self.assertEqual(sorted(d), ["a.service", "b.service"])  # bloco sem Id e descartado
        self.assertNotIn("Coisa", d["a.service"])

    def test_nao_texto(self):
        self.assertEqual(ex.parse_show(None), {})
        self.assertEqual(ex.parse_show(b"x"), {})
        self.assertEqual(ex.parse_show(""), {})


class ParseFalhasTest(unittest.TestCase):
    def test_primeira_coluna(self):
        t = ("a.service loaded failed failed Descricao A\n"
             "b@x.service loaded failed failed Descricao B\n"
             "sys-fs.mount loaded failed failed ...\n")
        self.assertEqual(ex.parse_falhas(t), {"n": 3, "nomes": ["a.service", "b@x.service", "sys-fs.mount"]})

    def test_vazio(self):
        self.assertEqual(ex.parse_falhas(""), {"n": 0, "nomes": []})
        self.assertEqual(ex.parse_falhas("\n  \n"), {"n": 0, "nomes": []})
        self.assertEqual(ex.parse_falhas(None), {"n": 0, "nomes": []})

    def test_limite_de_5_nomes_com_n_real(self):
        t = "".join("u%d.service loaded failed failed x\n" % i for i in range(12))
        r = ex.parse_falhas(t)
        self.assertEqual(r["n"], 12)
        self.assertEqual(r["nomes"], ["u%d.service" % i for i in range(5)])

    def test_n_limitado_a_9999(self):
        t = "u.service loaded failed failed x\n" * 10050
        r = ex.parse_falhas(t)
        self.assertEqual(r["n"], 9999)
        self.assertEqual(len(r["nomes"]), 5)

    def test_nome_hostil_descartado(self):
        t = ("ok.service loaded failed failed x\n"
             "a;rm -rf /.service loaded failed failed x\n"
             "$(id).service loaded failed failed x\n"
             "évil.service loaded failed failed x\n"
             + "x" * 41 + ".service loaded failed failed x\n"
             "../../etc/passwd loaded failed failed x\n"
             "\x1b[31mred.service loaded failed failed x\n"
             "bom@a:b.service loaded failed failed x\n")
        r = ex.parse_falhas(t)
        self.assertEqual(r["nomes"], ["ok.service", "bom@a:b.service"])
        self.assertEqual(r["n"], 8)  # a contagem e das linhas reais; so o nome e saneado
        for n in r["nomes"]:
            self.assertRegex(n, r"^[A-Za-z0-9_.@:-]{1,40}$")

    def test_nome_hostil_nao_conta_como_nome_do_limite(self):
        t = "bad;name.service x\n" * 3 + "".join("u%d.service x\n" % i for i in range(6))
        self.assertEqual(ex.parse_falhas(t)["nomes"], ["u%d.service" % i for i in range(5)])


class FakeEntrada:
    def __init__(self, mtime, link=False, erro=False):
        self._m, self._l, self._e = mtime, link, erro

    def is_symlink(self):
        return self._l

    def stat(self, follow_symlinks=True):
        assert follow_symlinks is False
        if self._e:
            raise PermissionError("x")
        return os.stat_result((0o100644, 0, 0, 1, 0, 0, 0, 0, self._m, 0))


class FakeDir:
    def __init__(self, entradas):
        self.entradas = entradas
        self.consumidas = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        for e in self.entradas:
            self.consumidas += 1
            yield e


class ColetarTimersTest(unittest.TestCase):
    def test_argv_fixo_uma_chamada_com_alvos_separados_e_timeout(self):
        f = FakeSys(show=(0, bloco("a.service") + "\n" + bloco("b@x.service"), ""))
        coletar([timer(id="a", alvo="a.service"), timer(id="b", alvo="b@x.service"),
                 timer(id="c", alvo="a.service")], f)
        self.assertEqual(f.chamadas, [(SHOW + ["a.service", "b@x.service"], 10), (FALHAS, 10)])
        for argv, _ in f.chamadas:
            self.assertIsInstance(argv, list)
            self.assertTrue(all(isinstance(x, str) for x in argv))

    def test_alvo_com_hifen_inicial_fica_depois_do_separador(self):
        f = FakeSys()
        coletar([timer(alvo="-x.service")], f)
        argv = f.chamadas[0][0]
        self.assertEqual(argv[-2:], ["--", "-x.service"])

    def test_success_e_ok_com_ultima_em_do_epoch(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", ts="@1699990000"), ""))
        d = coletar([timer()], f)
        self.assertEqual(d["rotinas"]["senhas"], {"resultado": "ok", "ultima_em": 1699990000, "detalhe": "ok"})
        self.assertEqual(d["versao"], 1)
        self.assertEqual(d["gerado"], NS)

    def test_resultado_diferente_de_success_e_falha(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", result="exit-code", status="1"), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual(r, {"resultado": "falha", "ultima_em": 1699990000, "detalhe": "exit 1"})
        for res, det in (("timeout", "timeout"), ("signal", "signal"), ("oom-kill", "oom-kill")):
            f = FakeSys(show=(0, bloco("backup-senhas.service", result=res), ""))
            r = coletar([timer()], f)["rotinas"]["senhas"]
            self.assertEqual((r["resultado"], r["detalhe"]), ("falha", det))

    def test_unit_inexistente(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", load="not-found", ts=""), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual(r, {"resultado": "desconhecido", "ultima_em": None, "detalhe": "sem unidade"})

    def test_unit_ausente_da_saida(self):
        f = FakeSys(show=(0, bloco("outra.service"), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual(r, {"resultado": "desconhecido", "ultima_em": None, "detalhe": "sem unidade"})

    def test_timestamp_vazio_ou_zero(self):
        for ts in ("", "@0", "@", "@-1", "0", "Thu 2026-11-19 02:05:11 UTC", "@99999999999999"):
            f = FakeSys(show=(0, bloco("backup-senhas.service", ts=ts), ""))
            r = coletar([timer()], f)["rotinas"]["senhas"]
            self.assertIsNone(r["ultima_em"], ts)
            self.assertEqual(r["resultado"], "desconhecido", ts)  # success sem execucao nao e "ok"

    def test_falha_sem_timestamp_continua_falha(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", result="resources", ts=""), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual((r["resultado"], r["ultima_em"]), ("falha", None))

    def test_sem_result_e_desconhecido(self):
        f = FakeSys(show=(0, "Id=backup-senhas.service\nLoadState=loaded\nExecMainExitTimestamp=@1699990000\n", ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual((r["resultado"], r["ultima_em"]), ("desconhecido", 1699990000))

    def test_result_hostil_nao_vira_detalhe(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", result="$(rm -rf /)"), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertEqual((r["resultado"], r["detalhe"]), ("desconhecido", "sem resultado"))

    def test_sem_timer_nao_chama_show(self):
        f = FakeSys()
        coletar([arq(alvo="/srv/nao-existe-xyz")], f)
        self.assertEqual([c[0] for c in f.chamadas], [FALHAS])

    def test_falha_de_comando_sobe(self):
        for show in ((1, "", "x"), subprocess.TimeoutExpired("systemctl", 10), OSError("x")):
            with self.assertRaises(Exception):
                coletar([timer()], FakeSys(show=show))
        with self.assertRaises(Exception):
            coletar([timer()], FakeSys(show=(0, bloco("backup-senhas.service"), ""), falhas=(1, "", "")))

    def test_detalhe_sempre_ascii_ate_24(self):
        f = FakeSys(show=(0, bloco("backup-senhas.service", result="x" * 24), ""))
        r = coletar([timer()], f)["rotinas"]["senhas"]
        self.assertLessEqual(len(r["detalhe"]), 24)
        so_ascii_sem_controle(self, r["detalhe"])


class ColetarArquivosTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.d = os.path.realpath(self._tmp.name)

    def f(self, nome, mtime, conteudo="x"):
        cam = os.path.join(self.d, nome)
        with open(cam, "w") as fh:
            fh.write(conteudo)
        os.utime(cam, (mtime, mtime))
        return cam

    def um(self, alvo):
        # validar_rotinas exige /srv, /var/lib ou /var/backups; os testes de disco validam o catalogo a mao
        cat = [dict(arq(alvo=alvo))]
        return ex.coletar_rotinas(cat, FakeSys(), agora=lambda: NS)["rotinas"]["painel"]

    def test_arquivo_usa_mtime(self):
        cam = self.f("tokens.json", 1699990000)
        self.assertEqual(self.um(cam), {"resultado": "ok", "ultima_em": 1699990000, "detalhe": "ok"})

    def test_diretorio_usa_maior_mtime_das_entradas_diretas(self):
        self.f("a", 1699000000)
        self.f("b", 1699990000)
        self.f("c", 1699500000)
        os.mkdir(os.path.join(self.d, "sub"))
        with open(os.path.join(self.d, "sub", "profundo"), "w") as fh:
            fh.write("x")
        os.utime(os.path.join(self.d, "sub", "profundo"), (1699999999, 1699999999))
        os.utime(os.path.join(self.d, "sub"), (1699100000, 1699100000))
        self.assertEqual(self.um(self.d)["ultima_em"], 1699990000)  # sem recursao

    def test_symlink_e_ignorado_nas_entradas(self):
        self.f("velho", 1699000000)
        fora = tempfile.TemporaryDirectory()
        self.addCleanup(fora.cleanup)
        alvo = os.path.join(fora.name, "novo-fora")
        with open(alvo, "w") as fh:
            fh.write("x")
        os.utime(alvo, (1699999999, 1699999999))
        os.symlink(alvo, os.path.join(self.d, "link"))
        sub = os.path.join(self.d, "sub")
        os.mkdir(sub)
        os.utime(sub, (1699100000, 1699100000))
        # o symlink (mtime proprio = agora, ou o do alvo) nao pode valer: sobra o do subdiretorio
        self.assertEqual(self.um(self.d)["ultima_em"], 1699100000)
        # alvo dentro de um diretorio so com link: vazio, desconhecido
        solo = os.path.join(self.d, "solo")
        os.mkdir(solo)
        os.symlink(alvo, os.path.join(solo, "so-link"))
        self.assertEqual(self.um(solo), {"resultado": "desconhecido", "ultima_em": None, "detalhe": "vazio"})

    def test_alvo_que_e_symlink_e_ignorado(self):
        alvo = self.f("real", 1699990000)
        link = os.path.join(self.d, "tokens.json")
        os.symlink(alvo, link)
        self.assertEqual(self.um(link), {"resultado": "desconhecido", "ultima_em": None,
                                         "detalhe": "link ignorado"})

    def test_inexistente(self):
        self.assertEqual(self.um(os.path.join(self.d, "nao-existe")),
                         {"resultado": "desconhecido", "ultima_em": None, "detalhe": "sem arquivo"})

    def test_diretorio_vazio(self):
        self.assertEqual(self.um(self.d)["detalhe"], "vazio")

    def test_nao_le_conteudo(self):
        cam = self.f("seg.json", 1699990000, "segredo")
        os.chmod(cam, 0)  # se abrisse para ler, falharia (usuario nao-root)
        try:
            self.assertEqual(self.um(cam)["ultima_em"], 1699990000)
        finally:
            os.chmod(cam, 0o600)

    def test_stat_sem_seguir_symlink(self):
        vistos = []

        def stat(p, **kw):
            vistos.append(kw)
            return os.stat_result((0o100644, 0, 0, 1, 0, 0, 0, 0, 1699990000, 0))
        r = ex.coletar_rotinas([arq()], FakeSys(), stat=stat, agora=lambda: NS)["rotinas"]["painel"]
        self.assertEqual(vistos, [{"follow_symlinks": False}])
        self.assertEqual(r["ultima_em"], 1699990000)

    def test_erro_de_permissao_ou_de_leitura(self):
        def stat(p, **kw):
            raise PermissionError("x")
        r = ex.coletar_rotinas([arq()], FakeSys(), stat=stat, agora=lambda: NS)["rotinas"]["painel"]
        self.assertEqual((r["resultado"], r["ultima_em"]), ("desconhecido", None))

        def stat_dir(p, **kw):
            return os.stat_result((0o040755, 0, 0, 1, 0, 0, 0, 0, 5, 0))

        def listar(p):
            raise PermissionError("x")
        r = ex.coletar_rotinas([arq()], FakeSys(), stat=stat_dir, listar=listar, agora=lambda: NS)["rotinas"]["painel"]
        self.assertEqual((r["resultado"], r["detalhe"]), ("desconhecido", "erro de leitura"))

    def test_entrada_com_erro_e_pulada_e_limite_de_2000(self):
        def stat_dir(p, **kw):
            return os.stat_result((0o040755, 0, 0, 1, 0, 0, 0, 0, 5, 0))
        entradas = [FakeEntrada(1699000000, erro=True), FakeEntrada(1699500000, link=True),
                    FakeEntrada(1699200000)] + [FakeEntrada(1699100000)] * 3000
        entradas.insert(2500, FakeEntrada(1699999999))  # alem do limite: nem e visto
        fd = FakeDir(entradas)
        r = ex.coletar_rotinas([arq()], FakeSys(), stat=stat_dir, listar=lambda p: fd, agora=lambda: NS)
        self.assertEqual(r["rotinas"]["painel"]["ultima_em"], 1699200000)
        self.assertLessEqual(fd.consumidas, 2001)

    def test_mtime_invalido(self):
        for m in (0, -5, 1e30, float("nan")):
            def stat(p, m=m, **kw):
                return os.stat_result((0o100644, 0, 0, 1, 0, 0, 0, 0, m, 0))
            try:
                r = ex.coletar_rotinas([arq()], FakeSys(), stat=stat, agora=lambda: NS)["rotinas"]["painel"]
            except Exception:
                self.fail("nao pode levantar para mtime %r" % (m,))
            self.assertEqual(r["resultado"], "desconhecido", m)


class ColetarFalhasTest(unittest.TestCase):
    def test_mais_de_5_unidades_corta_em_5_com_n_correto(self):
        t = "".join("u%d.service loaded failed failed Desc %d\n" % (i, i) for i in range(8))
        d = coletar([timer()], FakeSys(falhas=(0, t, "")))
        self.assertEqual(d["unidades_falhas"], {"n": 8, "nomes": ["u%d.service" % i for i in range(5)]})

    def test_nome_hostil(self):
        t = "bom.service x\n; reboot x\n$(x).service x\n"
        d = coletar([timer()], FakeSys(falhas=(0, t, "")))
        self.assertEqual(d["unidades_falhas"], {"n": 3, "nomes": ["bom.service"]})

    def test_nenhuma(self):
        d = coletar([timer()], FakeSys())
        self.assertEqual(d["unidades_falhas"], {"n": 0, "nomes": []})


class InventarioTest(Base):
    def setUp(self):
        super().setUp()
        self.arquivos = os.path.join(self.estado, "..", "dados")
        self.cfg["rotinas"] = [timer(), timer(id="outra", alvo="outra.service", rotulo="Outra"),
                               arq(alvo="/srv/nao-existe-kindle-monitor-teste/x.json")]

    def inv(self, show=None, falhas=(0, "", ""), cfg=None, **kw):
        if show is None:
            show = (0, bloco("backup-senhas.service") + "\n" + bloco("outra.service", result="exit-code",
                                                                      status="2"), "")
        self.fake = FakeSys(show=show, falhas=falhas)
        e = ex.Executor(cfg or self.cfg, executar=self.fake, dono=self.dono, log=self.logs.append, **kw)
        e.agora_inv = lambda: NS
        return e

    def ler(self, nome="rotinas.json"):
        with open(os.path.join(self.estado, nome), encoding="utf-8") as f:
            return f.read()

    def test_grava_rotinas_json_atomico_0644_e_formato(self):
        self.assertEqual(self.inv().inventariar(), 1)
        cam = os.path.join(self.estado, "rotinas.json")
        self.assertEqual(oct(os.stat(cam).st_mode & 0o777), "0o644")
        d = json.loads(self.ler())
        self.assertEqual(set(d), {"versao", "gerado", "rotinas", "unidades_falhas"})
        self.assertEqual(d["versao"], 1)
        self.assertEqual(d["gerado"], NS)
        self.assertEqual(d["rotinas"]["senhas"], {"resultado": "ok", "ultima_em": 1699990000, "detalhe": "ok"})
        self.assertEqual(d["rotinas"]["outra"]["detalhe"], "exit 2")
        self.assertEqual(d["rotinas"]["outra"]["resultado"], "falha")
        self.assertEqual(d["rotinas"]["painel"], {"resultado": "desconhecido", "ultima_em": None,
                                                  "detalhe": "sem arquivo"})
        self.assertEqual(d["unidades_falhas"], {"n": 0, "nomes": []})
        self.assertEqual([n for n in os.listdir(self.estado) if n.startswith(".")], [])

    def test_servicos_json_continua_sendo_gravado(self):
        self.inv().inventariar()
        self.assertIn("servicos.json", os.listdir(self.estado))

    def test_arquivo_gravado_so_com_ascii(self):
        t = "bom.service loaded failed failed Descrição\névil☃.service x\n\x1b[31m.service x\n"
        self.inv(falhas=(0, t, "")).inventariar()
        with open(os.path.join(self.estado, "rotinas.json"), "rb") as f:
            bruto = f.read()
        bruto.decode("ascii")
        self.assertEqual(json.loads(bruto)["unidades_falhas"], {"n": 3, "nomes": ["bom.service"]})

    def test_sem_catalogo_nao_chama_nem_grava(self):
        self.cfg["rotinas"] = []
        self.inv().inventariar()
        self.assertEqual(self.fake.chamadas, [])
        self.assertNotIn("rotinas.json", os.listdir(self.estado))

    def test_chave_ausente_da_cfg_e_lista_vazia(self):
        del self.cfg["rotinas"]
        self.inv().inventariar()
        self.assertEqual(self.fake.chamadas, [])

    def todas_desconhecidas(self):
        d = json.loads(self.ler())
        self.assertEqual(set(d["rotinas"]), {"senhas", "outra", "painel"})
        for v in d["rotinas"].values():
            self.assertEqual(v["resultado"], "desconhecido")
            self.assertIsNone(v["ultima_em"])
            self.assertLessEqual(len(v["detalhe"]), 24)
        self.assertEqual(d["unidades_falhas"], {"n": 0, "nomes": []})
        self.assertIn("servicos.json", os.listdir(self.estado))  # nao derruba os servicos

    def test_timeout(self):
        self.inv(show=subprocess.TimeoutExpired("systemctl", 10)).inventariar()
        self.todas_desconhecidas()
        self.assertEqual(len(self.logs), 1)
        so_ascii_sem_controle(self, self.logs[0])

    def test_timeout_da_lista_de_falhas(self):
        self.inv(falhas=subprocess.TimeoutExpired("systemctl", 10)).inventariar()
        self.todas_desconhecidas()

    def test_codigo_de_saida_e_binario_ausente_e_excecao(self):
        for show in ((1, "", "Failed to connect to bus: user@x"), FileNotFoundError(), ValueError("x"), (0, None, None)):
            self.logs.clear()
            self.inv(show=show).inventariar()
            self.todas_desconhecidas()
            self.assertNotIn("user@x", self.ler())

    def test_timeout_de_cada_comando_e_10(self):
        self.inv().inventariar()
        self.assertEqual(ex.TIMEOUT_ROTINAS, 10)
        for argv, t in self.fake.chamadas:
            if argv[0] == "systemctl" and argv[1] in ("show", "list-units"):
                self.assertEqual(t, 10)

    def test_aparelhos_falhando_nao_quebra_rotinas_e_vice_versa(self):
        self.cfg["aparelhos"] = ex.validar_aparelhos([{"id": "gw", "nome": "cerberus-gw", "rotulo": "GW",
                                                       "icone": "rede"}])
        antes = ex.Executor._inventariar_aparelhos

        def quebra(self_):
            raise RuntimeError("boom")
        ex.Executor._inventariar_aparelhos = quebra
        try:
            self.inv().inventariar()
        finally:
            ex.Executor._inventariar_aparelhos = antes
        self.assertEqual(json.loads(self.ler())["rotinas"]["senhas"]["resultado"], "ok")
        self.assertIn("servicos.json", os.listdir(self.estado))
        # e o contrario
        for n in os.listdir(self.estado):
            os.unlink(os.path.join(self.estado, n))
        antes_r = ex.Executor._inventariar_rotinas
        ex.Executor._inventariar_rotinas = quebra
        try:
            self.inv().inventariar()
        finally:
            ex.Executor._inventariar_rotinas = antes_r
        self.assertIn("aparelhos.json", os.listdir(self.estado))
        self.assertIn("servicos.json", os.listdir(self.estado))

    def test_roda_depois_de_servicos_e_aparelhos(self):
        self.cfg["aparelhos"] = ex.validar_aparelhos([{"id": "gw", "nome": "cerberus-gw", "rotulo": "GW",
                                                       "icone": "rede"}])
        self.inv().inventariar()
        chamadas = [c[0][0] + " " + c[0][1] for c in self.fake.chamadas]
        self.assertLess(chamadas.index("tailscale status"), chamadas.index("systemctl show"))

    def test_tmp_symlink_nao_e_seguido(self):
        alvo = os.path.join(self._tmp.name, "alvo-externo")
        with open(alvo, "w") as f:
            f.write("intocado")
        os.symlink(alvo, os.path.join(self.estado, ".rotinas.json.tmp"))
        self.inv().inventariar()
        with open(alvo) as f:
            self.assertEqual(f.read(), "intocado")
        self.assertEqual(json.loads(self.ler())["rotinas"]["senhas"]["resultado"], "ok")

    def test_rotinas_json_sobrevive_a_limpeza_de_resultados(self):
        self.inv().inventariar()
        for i in range(30):
            with open(os.path.join(self.estado, "%d-monitor-reiniciar.json" % (i + 1)), "w") as f:
                f.write("{}")
        self.req("99-bots-retomar.req")
        self.executor().processar_spool()
        self.assertTrue(os.path.exists(os.path.join(self.estado, "rotinas.json")))


class CfgTest(unittest.TestCase):
    def cfg(self, dados):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(dados, f)
            return ex.carregar_cfg(cam)

    def test_ausente_e_lista_vazia(self):
        c = self.cfg({})
        self.assertEqual(c["rotinas"], [])
        self.assertNotIn("rotinas_erro", c)

    def test_le_rotinas(self):
        c = self.cfg({"rotinas": [timer(), arq()]})
        self.assertEqual(c["rotinas"], [timer(), arq()])
        self.assertNotIn("rotinas_erro", c)

    def test_invalida_vira_lista_vazia_com_motivo_e_nao_derruba_o_resto(self):
        c = self.cfg({"rotinas": [timer(alvo="/etc/x")], "servicos_kindle": [], "aparelhos": []})
        self.assertEqual(c["rotinas"], [])
        self.assertIn("rotinas", c["rotinas_erro"])
        self.assertEqual(c["aparelhos"], [])

    def test_rotinas_ruins_nao_apagam_aparelhos_bons(self):
        ap = {"id": "gw", "nome": "cerberus-gw", "rotulo": "GW", "icone": "rede"}
        c = self.cfg({"rotinas": "x", "aparelhos": [ap]})
        self.assertEqual(c["aparelhos"], [ap])
        self.assertEqual(c["rotinas"], [])

    def test_main_loga_uma_linha_e_nao_grava(self):
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"rotinas": [timer(tipo="cron")]}, f)
            logs, vistos = [], []

            class Falso:
                def __init__(self, cfg, log=None):
                    vistos.append(cfg["rotinas"])

                def inventariar(self):
                    vistos.append("inventariou")

            real, ex.Executor = ex.Executor, Falso
            try:
                self.assertEqual(ex.main(["--config", cam, "--inventario"], log=logs.append), 0)
            finally:
                ex.Executor = real
        self.assertEqual(vistos, [[], "inventariou"])
        self.assertEqual(len(logs), 1)
        self.assertIn("rotinas", logs[0])
        self.assertTrue(logs[0].isascii())

    def test_config_invalida_nao_grava_rotinas_json(self):
        with tempfile.TemporaryDirectory() as d:
            est = os.path.join(d, "status")
            sp = os.path.join(d, "spool")
            os.makedirs(est)
            os.makedirs(sp)
            os.chmod(sp, 0o1730)
            c = ex.carregar_cfg(self._escreve(d, {"comandos": {"spool": sp, "estado": est},
                                                   "rotinas": [timer(id="X")]}))
            self.assertEqual(c["rotinas"], [])
            e = ex.Executor(c, executar=FakeSys(), dono=(os.getuid(), os.getgid()), log=lambda l: None)
            e.inventariar()
            self.assertNotIn("rotinas.json", os.listdir(est))

    def _escreve(self, d, dados):
        cam = os.path.join(d, "c.json")
        with open(cam, "w") as f:
            json.dump(dados, f)
        return cam


class ParidadeTest(unittest.TestCase):
    def test_validacao_igual_a_do_servidor(self):
        import ecossistema
        casos = [
            [timer(), arq()],
            [timer(alvo="a.timer")], [timer(alvo="x" * 65 + ".service")], [timer(rotulo="x" * 21)],
            [timer(rotulo="Coração")], [timer(id="A")], [timer(tipo="cron")],
            [arq(alvo="/srv/../etc/x")], [arq(alvo="/etc/x")], [arq(alvo="/var/backups/x")],
            [timer(max_idade_h=0.05)], [timer(max_idade_h=True)], [timer(max_idade_h=721)],
            [timer(max_idade_h=0.1)], [timer(max_idade_h=720)],
            [timer(id="t%d" % i) for i in range(17)], [timer(id="t%d" % i) for i in range(16)],
            [], "x", [3],
        ]
        for c in casos:
            try:
                local = ex.validar_rotinas(c)
            except ValueError:
                local = []
            web = ecossistema.validar_rotinas(c)
            self.assertEqual(local, web, c)

    def test_executor_recusa_chave_desconhecida_e_id_repetido(self):
        # como validar_aparelhos do executor (decisao da tarefa); o servidor e mais tolerante nesses dois casos
        for c in ([timer(extra=1)], [timer(), timer()]):
            with self.assertRaises(ValueError):
                ex.validar_rotinas(c)

    def test_arquivos_de_config_do_repo_passam(self):
        aqui = os.path.dirname(os.path.abspath(__file__))
        raiz = os.path.dirname(aqui)
        for rel in (("..", "deploy", "config.atheron.json"), ("config.exemplo.json",)):
            with open(os.path.join(raiz, *rel), encoding="utf-8") as f:
                dados = json.load(f)
            if "rotinas" in dados:
                ex.validar_rotinas(dados["rotinas"])


if __name__ == "__main__":
    unittest.main()
