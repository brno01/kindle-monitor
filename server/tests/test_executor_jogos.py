"""Executor: coletor do AMP (credencial, cliente HTTP, parse das instancias, inventariar -> jogos.json).

A senha do AMP nunca pode aparecer em jogos.json, no log, em excecao nem em argv: `SENHA` e unica e os testes
procuram por ela em tudo que o executor produz. O servidor HTTP falso (127.0.0.1, porta efemera) so serve aos
testes de `amp_post`: a validacao de producao (`validar_amp`) recusa loopback e nao tem parametro para liberar.
"""
import http.server
import json
import os
import socket
import stat
import subprocess
import threading
import time
import unittest
import urllib.error

import _caminho  # noqa: F401
from test_executor import Base, ex

NS = 1_700_000_000
SENHA = "S3nh@-Sup3r-Secreta-9X"
USUARIO = "painel"
URL = "http://10.0.0.60:8080"
IID_A = "11111111-2222-3333-4444-555555555555"
IID_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SID = "d5c13ef2-1111-4222-8333-444455556666"


def inst(iid=IID_A, nome="Minecraft", modulo="Minecraft", running=True, estado=20, jogadores=2, maximo=20, **extra):
    d = {"InstanceID": iid, "FriendlyName": nome, "Module": modulo, "ModuleDisplayName": modulo,
         "Running": running, "AppState": estado,
         "Metrics": {"Active Users": {"RawValue": jogadores, "MaxValue": maximo, "Percent": 0, "Units": ""}}}
    d.update(extra)
    return d


def ads(*instancias):
    """Resposta de ADSModule/GetInstances: lista de alvos ADS, cada um com AvailableInstances."""
    return [{"InstanceID": "ads", "FriendlyName": "Local", "AvailableInstances": list(instancias)}]


def contem_senha(valor):
    return SENHA in json.dumps(valor, default=str) if not isinstance(valor, str) else SENHA in valor


class PostFalso:
    """`post(url, corpo, timeout)` injetavel: grava as chamadas e devolve/levanta o que for combinado por metodo."""

    def __init__(self, login=None, instancias=None, logout=None):
        self.login = {"success": True, "sessionID": SID} if login is None else login
        self.instancias = ads(inst()) if instancias is None else instancias
        self.logout = {} if logout is None else logout
        self.chamadas = []

    def __call__(self, url, corpo, timeout):
        self.chamadas.append((url, json.loads(json.dumps(corpo)), timeout))
        r = {"/API/Core/Login": self.login, "/API/ADSModule/GetInstances": self.instancias,
             "/API/Core/Logout": self.logout}[url[len(URL):]]
        if isinstance(r, BaseException):
            raise r
        return r

    def metodos(self):
        return [c[0][len(URL):] for c in self.chamadas]


# ------------------------------------------------------------------ credencial

class CredencialTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cam = os.path.join(self._tmp.name, "amp.cred")
        self.uid = os.getuid()

    def grava(self, texto, modo=0o600):
        if os.path.lexists(self.cam):
            os.unlink(self.cam)  # o modo anterior pode ser so leitura
        with open(self.cam, "wb") as f:
            f.write(texto if isinstance(texto, bytes) else texto.encode("utf-8"))
        os.chmod(self.cam, modo)

    def ler(self, uid=None):
        return ex.ler_credencial(self.cam, self.uid if uid is None else uid)

    def test_ausente_e_desligado(self):
        self.assertIsNone(self.ler())

    def test_valida_0600_e_0400(self):
        for modo in (0o600, 0o400):
            self.grava(USUARIO + "\n" + SENHA + "\n", modo)
            self.assertEqual(self.ler(), (USUARIO, SENHA))

    def test_sem_quebra_de_linha_final_e_linha_vazia_no_fim(self):
        self.grava(USUARIO + "\n" + SENHA)
        self.assertEqual(self.ler(), (USUARIO, SENHA))
        self.grava(USUARIO + "\n" + SENHA + "\n\n")
        self.assertEqual(self.ler(), (USUARIO, SENHA))

    def test_crlf(self):
        self.grava(USUARIO + "\r\n" + SENHA + "\r\n")
        self.assertEqual(self.ler(), (USUARIO, SENHA))

    def test_senha_com_espacos_nas_pontas_e_preservada(self):
        self.grava(USUARIO + "\n  com espaco  \n")
        self.assertEqual(self.ler(), (USUARIO, "  com espaco  "))

    def test_modos_com_acesso_de_grupo_ou_outros_recusados(self):
        for modo in (0o640, 0o644, 0o660, 0o604, 0o606, 0o666, 0o700, 0o500, 0o620, 0o610):
            self.grava(USUARIO + "\n" + SENHA + "\n", modo)
            with self.subTest(modo=oct(modo)):
                with self.assertRaises(ex.CredencialInvalida):
                    self.ler()

    def test_dono_diferente_recusado(self):
        self.grava(USUARIO + "\n" + SENHA + "\n")
        with self.assertRaises(ex.CredencialInvalida):
            self.ler(uid=self.uid + 1)

    def test_symlink_recusado(self):
        alvo = os.path.join(self._tmp.name, "alvo")
        with open(alvo, "w") as f:
            f.write(USUARIO + "\n" + SENHA + "\n")
        os.chmod(alvo, 0o600)
        os.symlink(alvo, self.cam)
        with self.assertRaises(ex.CredencialInvalida):
            self.ler()

    def test_diretorio_e_fifo_recusados(self):
        os.mkdir(self.cam)
        with self.assertRaises(ex.CredencialInvalida):
            self.ler()
        os.rmdir(self.cam)
        os.mkfifo(self.cam, 0o600)  # abre sem bloquear (O_NONBLOCK) e e recusado pelo tipo
        with self.assertRaises(ex.CredencialInvalida):
            self.ler()

    def test_formatos_invalidos(self):
        casos = ["", "\n", USUARIO + "\n", "\n" + SENHA + "\n", USUARIO + "\n\n", USUARIO + "\n" + SENHA + "\nextra\n",
                 USUARIO + " " + SENHA, "u\x00x\n" + SENHA, USUARIO + "\n" + SENHA + "\x07\n", b"\xff\xfe\n\xff\n",
                 "u" * 129 + "\n" + SENHA, USUARIO + "\n" + "s" * 257, "a" * 5000]
        for texto in casos:
            self.grava(texto)
            with self.subTest(texto=repr(texto)[:30]):
                with self.assertRaises(ex.CredencialInvalida):
                    self.ler()

    def test_excecao_nunca_cita_caminho_nem_conteudo(self):
        self.grava(USUARIO + "\n" + SENHA + "\nextra\n")
        with self.assertRaises(ex.CredencialInvalida) as c:
            self.ler()
        self.assertNotIn(SENHA, str(c.exception))
        self.assertNotIn(self.cam, str(c.exception))
        self.assertNotIn(USUARIO, str(c.exception))


# ---------------------------------------------------------------------- parse

class ParseInstanciasTest(unittest.TestCase):
    def p(self, *itens):
        return ex.parse_instancias(ads(*itens))

    def test_instancia_rodando(self):
        r = self.p(inst())
        self.assertEqual(len(r), 1)
        i = r[0]
        self.assertEqual(set(i), {"id", "nome", "modulo", "estado", "jogadores", "max"})
        self.assertEqual((i["nome"], i["modulo"], i["estado"], i["jogadores"], i["max"]),
                         ("Minecraft", "Minecraft", "rodando", 2, 20))
        self.assertRegex(i["id"], r"^[0-9a-f]{8}\Z")

    def test_id_e_estavel_e_distinto(self):
        a1, a2 = self.p(inst(IID_A))[0]["id"], self.p(inst(IID_A, nome="Outro"))[0]["id"]
        b = self.p(inst(IID_B))[0]["id"]
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)

    def test_appstate(self):
        esperado = {20: "rodando", 0: "parado", 250: "parado", 200: "falha", 999: "outro", -1: "outro", 3: "outro"}
        for n in (5, 7, 10, 30, 40, 50, 60, 70, 80, 100, 300):
            esperado[n] = "iniciando"
        for estado, quer in esperado.items():
            with self.subTest(appstate=estado):
                self.assertEqual(self.p(inst(estado=estado))[0]["estado"], quer)

    def test_running_falso_e_sempre_parado(self):
        for estado in (20, 10, 200, 999, None):
            with self.subTest(appstate=estado):
                i = self.p(inst(running=False, estado=estado))[0]
                self.assertEqual((i["estado"], i["jogadores"], i["max"]), ("parado", None, None))

    def test_running_so_vale_se_for_true(self):
        for v in (None, 1, "true", "yes", 0):
            self.assertEqual(self.p(inst(running=v))[0]["estado"], "parado")

    def test_suspended_true_e_parado(self):
        self.assertEqual(self.p(inst(Suspended=True))[0]["estado"], "parado")

    def test_appstate_nao_inteiro_e_outro(self):
        for v in ("20", 20.5, True, None, [], {}):
            self.assertEqual(self.p(inst(estado=v))[0]["estado"], "outro", repr(v))

    def test_jogadores_so_para_rodando(self):
        for estado in (10, 200, 999):
            i = self.p(inst(estado=estado))[0]
            self.assertEqual((i["jogadores"], i["max"]), (None, None))

    def test_metrica_ausente_ou_ruim(self):
        for metricas in (None, {}, {"Active Users": None}, {"Active Users": {}}, {"Active Users": {"RawValue": "x"}},
                         {"Active Users": {"RawValue": True, "MaxValue": True}},
                         {"Active Users": {"RawValue": -1, "MaxValue": -5}},
                         {"Active Users": {"RawValue": float("nan")}}, {"Active Users": {"RawValue": 10 ** 9}}):
            d = inst()
            d["Metrics"] = metricas
            i = self.p(d)[0]
            self.assertEqual((i["estado"], i["jogadores"], i["max"]), ("rodando", None, None), repr(metricas))

    def test_max_ausente_mantem_jogadores(self):
        d = inst()
        d["Metrics"] = {"Active Users": {"RawValue": 3}}
        i = self.p(d)[0]
        self.assertEqual((i["jogadores"], i["max"]), (3, None))

    def test_numero_inteiro_em_float(self):
        d = inst()
        d["Metrics"] = {"Active Users": {"RawValue": 3.0, "MaxValue": 20.0}}
        self.assertEqual((self.p(d)[0]["jogadores"], self.p(d)[0]["max"]), (3, 20))

    def test_texto_e_saneado(self):
        d = inst(nome="Zé ☃ \x1b[31mServidor\x00 com nome muito comprido demais",
                 modulo="Módulo ‮ muito comprido demais")
        i = self.p(d)[0]
        self.assertTrue(i["nome"].isascii() and i["nome"].isprintable())
        self.assertLessEqual(len(i["nome"]), 24)
        self.assertLessEqual(len(i["modulo"]), 16)
        self.assertTrue(i["modulo"].isascii() and i["modulo"].isprintable())
        self.assertTrue(i["nome"].startswith("Ze"))
        self.assertNotIn("\x1b", i["nome"])

    def test_nome_vazio_ganha_um_nome(self):
        i = self.p(inst(nome="☃\x00"))[0]
        self.assertTrue(i["nome"])

    def test_modulo_generico_usa_o_nome_de_exibicao(self):
        d = inst(modulo="GenericModule")
        d["ModuleDisplayName"] = "Valheim"
        self.assertEqual(self.p(d)[0]["modulo"], "Valheim")

    def test_modulo_ausente(self):
        d = inst()
        del d["Module"], d["ModuleDisplayName"]
        self.assertEqual(self.p(d)[0]["modulo"], "")

    def test_o_proprio_ads_nao_e_jogo(self):
        r = self.p(inst(IID_A, nome="ADS01", modulo="ADS"), inst(IID_B, nome="Minecraft"))
        self.assertEqual([i["nome"] for i in r], ["Minecraft"])
        self.assertEqual(self.p(inst(modulo="ADSModule")), [])

    def test_id_repetido_fica_so_um(self):
        self.assertEqual(len(self.p(inst(IID_A), inst(IID_A, nome="copia"))), 1)

    def test_varios_alvos_ads(self):
        dados = [{"AvailableInstances": [inst(IID_A)]}, {"AvailableInstances": [inst(IID_B, nome="Valheim")]}]
        self.assertEqual(len(ex.parse_instancias(dados)), 2)

    def test_resposta_embrulhada_em_result(self):
        self.assertEqual(len(ex.parse_instancias({"result": ads(inst())})), 1)

    def test_ordem_ligadas_primeiro_depois_nome_e_maximo_16(self):
        itens = [inst("%032x" % n, nome="Srv %02d" % n, running=n % 2 == 0, estado=20 if n % 2 == 0 else 0)
                 for n in range(20)]
        r = ex.parse_instancias(ads(*itens))
        self.assertEqual(len(r), 16)
        self.assertEqual([i["estado"] for i in r[:10]], ["rodando"] * 10)
        self.assertEqual(r[0]["nome"], "Srv 00")
        self.assertEqual([i["nome"] for i in r[:10]], sorted(i["nome"] for i in r[:10]))

    def test_formato_inesperado_levanta_erro_fixo(self):
        for dados in (None, "x", 3, {}, {"a": 1}, [1, 2], [{"AvailableInstances": 3}], [{}], {"result": "x"}):
            with self.subTest(dados=repr(dados)):
                if dados in ([{}],):
                    self.assertEqual(ex.parse_instancias(dados), [])
                    continue
                with self.assertRaises(ex.AmpErro) as c:
                    ex.parse_instancias(dados)
                self.assertEqual(str(c.exception), "amp formato inesperado")

    def test_itens_ruins_sao_ignorados(self):
        dados = ads(inst(), "lixo", 3, None, {"InstanceID": 5}, {"InstanceID": ""}, {"FriendlyName": "sem id"})
        r = ex.parse_instancias(dados)
        self.assertEqual(len(r), 1)

    def test_aninhamento_profundo_nao_levanta_fora_do_erro_fixo(self):
        fundo = []
        for _ in range(5000):
            fundo = [fundo]
        try:
            r = ex.parse_instancias(fundo)
        except ex.AmpErro:
            return
        self.assertEqual(r, [])


# -------------------------------------------------------------------- cliente

class ColetarAmpTest(unittest.TestCase):
    def col(self, post, usuario=USUARIO, senha=SENHA):
        return ex.coletar_amp(URL, usuario, senha, post)

    def test_sequencia_de_chamadas_e_corpos(self):
        p = PostFalso()
        r = self.col(p)
        self.assertEqual(p.metodos(), ["/API/Core/Login", "/API/ADSModule/GetInstances", "/API/Core/Logout"])
        self.assertEqual(p.chamadas[0][1], {"username": USUARIO, "password": SENHA, "token": "", "rememberMe": False})
        self.assertEqual(p.chamadas[1][1], {"SESSIONID": SID})
        self.assertEqual(p.chamadas[2][1], {"SESSIONID": SID})
        self.assertEqual([c[2] for c in p.chamadas], [ex.AMP_TIMEOUT_S] * 3)
        self.assertEqual(ex.AMP_TIMEOUT_S, 8)
        self.assertEqual(r[0]["nome"], "Minecraft")

    def test_a_senha_so_vai_no_corpo_do_login(self):
        p = PostFalso()
        self.col(p)
        for url, corpo, _ in p.chamadas[1:]:
            self.assertFalse(contem_senha(corpo))
        for url, _, _ in p.chamadas:
            self.assertNotIn(SENHA, url)

    def test_login_com_success_falso(self):
        for login in ({"success": False, "resultReason": "senha " + SENHA}, {"success": "true", "sessionID": SID},
                      {"success": True}, {"success": True, "sessionID": ""}, {"success": True, "sessionID": 5},
                      {"success": True, "sessionID": "x y"}, {"success": True, "sessionID": "a" * 200},
                      [], "x", {"outro": 1}, 3):
            p = PostFalso(login=login)
            with self.subTest(login=repr(login)[:40]):
                with self.assertRaises(ex.AmpErro) as c:
                    self.col(p)
                self.assertEqual(str(c.exception), "amp login falhou")
                self.assertEqual(p.metodos(), ["/API/Core/Login"])  # sem sessao: nada de GetInstances nem logout

    def test_login_com_erro_http_4xx_e_login_falhou(self):
        e = urllib.error.HTTPError(URL, 401, "Unauthorized " + SENHA, {}, None)
        with self.assertRaises(ex.AmpErro) as c:
            self.col(PostFalso(login=e))
        self.assertEqual(str(c.exception), "amp login falhou")

    def test_sem_resposta(self):
        for erro in (OSError("conn " + SENHA), TimeoutError(), ValueError(SENHA), urllib.error.URLError(SENHA),
                     socket.timeout(), ConnectionRefusedError(), json.JSONDecodeError("x", "y", 0)):
            with self.subTest(erro=type(erro).__name__):
                with self.assertRaises(ex.AmpErro) as c:
                    self.col(PostFalso(login=erro))
                self.assertEqual(str(c.exception), "amp sem resposta")
                self.assertNotIn(SENHA, str(c.exception))
                self.assertIsNone(c.exception.__cause__)  # a excecao original (que pode citar a senha) nao fica ligada

    def test_get_instances_falha_mas_faz_logout(self):
        p = PostFalso(instancias=OSError("x"))
        with self.assertRaises(ex.AmpErro) as c:
            self.col(p)
        self.assertEqual(str(c.exception), "amp sem resposta")
        self.assertEqual(p.metodos(), ["/API/Core/Login", "/API/ADSModule/GetInstances", "/API/Core/Logout"])

    def test_formato_inesperado_tambem_faz_logout(self):
        p = PostFalso(instancias="lixo")
        with self.assertRaises(ex.AmpErro) as c:
            self.col(p)
        self.assertEqual(str(c.exception), "amp formato inesperado")
        self.assertEqual(p.metodos()[-1], "/API/Core/Logout")

    def test_logout_que_falha_ou_nao_existe_nao_e_erro(self):
        for logout in (OSError("404"), urllib.error.HTTPError(URL, 404, "nf", {}, None), ValueError("html"),
                       {"success": False}):
            with self.subTest(logout=repr(logout)[:30]):
                r = self.col(PostFalso(logout=logout))
                self.assertEqual(len(r), 1)

    def test_excecao_inesperada_do_post_vira_erro_fixo(self):
        for erro in (RuntimeError(SENHA), KeyError(SENHA), RecursionError()):
            with self.assertRaises(ex.AmpErro):
                self.col(PostFalso(login=erro))

    def test_interrupcao_nao_e_engolida(self):
        with self.assertRaises(ex.Interrompido):
            self.col(PostFalso(login=ex.Interrompido()))
        p = PostFalso(instancias=ex.Interrompido())
        with self.assertRaises(ex.Interrompido):
            self.col(p)
        self.assertEqual(p.metodos()[-1], "/API/Core/Logout")  # tenta sair mesmo assim


# ----------------------------------------------------------- HTTP (servidor falso)

class Servidor:
    """http.server em thread, 127.0.0.1, porta efemera. `rotas`: {caminho: funcao(handler, corpo_bytes)}."""

    def __init__(self, rotas):
        self.pedidos = []
        servidor = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                corpo = self.rfile.read(n)
                servidor.pedidos.append({"caminho": self.path, "cab": dict(self.headers), "corpo": corpo,
                                         "metodo": "POST"})
                fn = rotas.get(self.path)
                if fn is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                fn(self, corpo)

            def do_GET(self):
                servidor.pedidos.append({"caminho": self.path, "metodo": "GET", "cab": dict(self.headers)})
                self.send_response(404)
                self.end_headers()

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.httpd.daemon_threads = True
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        self.t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.t.start()

    def fechar(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.t.join(5)


def json_ok(obj):
    def f(h, corpo):
        dados = json.dumps(obj).encode()
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.send_header("Content-Length", str(len(dados)))
        h.end_headers()
        h.wfile.write(dados)
    return f


class AmpPostTest(unittest.TestCase):
    def sobe(self, rotas):
        s = Servidor(rotas)
        self.addCleanup(s.fechar)
        return s

    def test_post_json_com_cabecalhos(self):
        s = self.sobe({"/API/x": json_ok({"a": 1})})
        r = ex.amp_post(s.url + "/API/x", {"k": "v", "n": 3}, 5)
        self.assertEqual(r, {"a": 1})
        p = s.pedidos[0]
        self.assertEqual(p["metodo"], "POST")
        self.assertEqual(json.loads(p["corpo"]), {"k": "v", "n": 3})
        cab = {k.lower(): v for k, v in p["cab"].items()}
        self.assertEqual(cab["content-type"], "application/json")
        self.assertEqual(cab["accept"], "application/json")

    def test_redirect_e_recusado_e_o_destino_nunca_e_chamado(self):
        alvo = self.sobe({"/API/y": json_ok({"seguiu": True})})

        def redir(h, corpo):
            h.send_response(307)
            h.send_header("Location", alvo.url + "/API/y")
            h.end_headers()
        s = self.sobe({"/API/x": redir})
        for _ in range(2):
            with self.assertRaises(urllib.error.HTTPError) as c:
                ex.amp_post(s.url + "/API/x", {"senha": SENHA}, 5)
            self.assertEqual(c.exception.code, 307)
        self.assertEqual(alvo.pedidos, [])  # a senha nao foi reenviada para outro host

    def test_redirect_303_e_301_tambem(self):
        alvo = self.sobe({})
        for codigo in (301, 302, 303, 308):
            def redir(h, corpo, codigo=codigo):
                h.send_response(codigo)
                h.send_header("Location", alvo.url + "/")
                h.end_headers()
            s = self.sobe({"/API/x": redir})
            with self.assertRaises(urllib.error.HTTPError):
                ex.amp_post(s.url + "/API/x", {}, 5)
        self.assertEqual(alvo.pedidos, [])

    def test_resposta_grande_demais(self):
        def grande(h, corpo):
            h.send_response(200)
            h.send_header("Content-Type", "application/json")
            h.end_headers()
            try:
                h.wfile.write(b'{"x":"' + b"a" * (ex.AMP_MAX_BYTES + 10) + b'"}')
            except OSError:
                pass
        s = self.sobe({"/API/x": grande})
        with self.assertRaises(ex.AmpErro) as c:
            ex.amp_post(s.url + "/API/x", {}, 5)
        self.assertEqual(str(c.exception), "amp resposta grande")

    def test_limite_de_1_mib(self):
        self.assertEqual(ex.AMP_MAX_BYTES, 1 << 20)

    def test_json_invalido(self):
        def lixo(h, corpo):
            h.send_response(200)
            h.end_headers()
            h.wfile.write(b"<html>nao e json</html>")
        s = self.sobe({"/API/x": lixo})
        with self.assertRaises(ValueError):
            ex.amp_post(s.url + "/API/x", {}, 5)

    def test_http_500_e_404(self):
        def erro(h, corpo):
            h.send_response(500)
            h.end_headers()
        s = self.sobe({"/API/x": erro})
        with self.assertRaises(urllib.error.HTTPError):
            ex.amp_post(s.url + "/API/x", {}, 5)
        with self.assertRaises(urllib.error.HTTPError):
            ex.amp_post(s.url + "/API/inexistente", {}, 5)

    def test_timeout_curto(self):
        def lento(h, corpo):
            time.sleep(1.5)
        s = self.sobe({"/API/x": lento})
        t0 = time.monotonic()
        with self.assertRaises(OSError):
            ex.amp_post(s.url + "/API/x", {}, 0.3)
        self.assertLess(time.monotonic() - t0, 1.4)

    def test_resposta_gotejando_nao_passa_do_prazo(self):
        def gotas(h, corpo):
            h.send_response(200)
            h.end_headers()
            try:
                for _ in range(40):
                    h.wfile.write(b" ")
                    h.wfile.flush()
                    time.sleep(0.1)
            except OSError:
                pass
        s = self.sobe({"/API/x": gotas})
        t0 = time.monotonic()
        with self.assertRaises(OSError):
            ex.amp_post(s.url + "/API/x", {}, 0.5)
        self.assertLess(time.monotonic() - t0, 1.5)

    def test_sem_proxy_do_ambiente(self):
        s = self.sobe({"/API/x": json_ok({})})
        antes = os.environ.get("http_proxy")
        os.environ["http_proxy"] = "http://127.0.0.1:9"  # porta fechada: se usasse o proxy, falharia
        try:
            self.assertEqual(ex.amp_post(s.url + "/API/x", {}, 5), {})
        finally:
            if antes is None:
                del os.environ["http_proxy"]
            else:
                os.environ["http_proxy"] = antes

    def test_fluxo_completo_com_o_cliente_real(self):
        rotas = {"/API/Core/Login": json_ok({"success": True, "sessionID": SID}),
                 "/API/ADSModule/GetInstances": json_ok(ads(inst(), inst(IID_B, nome="Valheim", running=False,
                                                                           estado=0)))}
        s = self.sobe(rotas)  # /API/Core/Logout nao existe (404): nao pode ser erro
        r = ex.coletar_amp(s.url, USUARIO, SENHA, ex.amp_post)
        self.assertEqual([(i["nome"], i["estado"]) for i in r], [("Minecraft", "rodando"), ("Valheim", "parado")])
        self.assertEqual([p["caminho"] for p in s.pedidos],
                         ["/API/Core/Login", "/API/ADSModule/GetInstances", "/API/Core/Logout"])


# -------------------------------------------------------------- inventariar

class JogosBase(Base):
    def setUp(self):
        super().setUp()
        self.cam_cred = os.path.join(self._tmp.name, "amp.cred")
        self.cfg["amp"] = None  # a validacao de producao exige /etc/kindle-monitor; o teste ajusta o executor
        self.agora = NS

    def cred(self, texto=None, modo=0o600):
        if os.path.lexists(self.cam_cred):
            os.unlink(self.cam_cred)
        with open(self.cam_cred, "w") as f:
            f.write(USUARIO + "\n" + SENHA + "\n" if texto is None else texto)
        os.chmod(self.cam_cred, modo)

    def inv(self, post=None, ligado=True):
        self.post = post or PostFalso()
        e = ex.Executor(self.cfg, executar=lambda argv, timeout: (0, "", ""), dono=self.dono,
                        log=self.logs.append, amp_post=self.post)
        if ligado:
            e.amp = {"url": URL, "credenciais": self.cam_cred}  # so no teste: a producao nao aceita este caminho
        e.agora_inv = lambda: self.agora
        return e

    def doc(self):
        with open(os.path.join(self.estado, "jogos.json"), encoding="utf-8") as f:
            return json.load(f)

    def texto(self):
        with open(os.path.join(self.estado, "jogos.json"), encoding="utf-8") as f:
            return f.read()

    def existe(self):
        return os.path.exists(os.path.join(self.estado, "jogos.json"))


class InventarioJogosTest(JogosBase):
    def test_grava_jogos_json_0644_com_o_formato_combinado(self):
        self.cred()
        self.assertEqual(self.inv().inventariar(), 1)
        d = self.doc()
        self.assertEqual(set(d), {"versao", "gerado", "ativo", "erro", "instancias"})
        self.assertEqual((d["versao"], d["gerado"], d["ativo"], d["erro"]), (1, NS, True, None))
        self.assertEqual([(i["nome"], i["estado"], i["jogadores"], i["max"]) for i in d["instancias"]],
                         [("Minecraft", "rodando", 2, 20)])
        self.assertEqual(oct(os.stat(os.path.join(self.estado, "jogos.json")).st_mode & 0o777), "0o644")
        self.assertEqual([n for n in os.listdir(self.estado) if n.startswith(".")], [])
        self.assertIn("servicos.json", os.listdir(self.estado))

    def test_sem_amp_na_config_nada_acontece(self):
        self.cred()
        e = self.inv(ligado=False)
        e.inventariar()
        self.assertEqual(self.post.chamadas, [])
        self.assertFalse(self.existe())
        self.assertEqual(os.listdir(self.estado), ["servicos.json"])

    def test_credencial_ausente_e_desligado_sem_erro(self):
        self.inv().inventariar()
        d = self.doc()
        self.assertEqual((d["ativo"], d["erro"], d["instancias"]), (False, None, []))
        self.assertEqual(self.post.chamadas, [])  # sem credencial nem chega a abrir a conexao
        self.assertEqual(self.logs, [])

    def test_credencial_invalida(self):
        self.cred(modo=0o644)
        self.inv().inventariar()
        d = self.doc()
        self.assertEqual((d["ativo"], d["erro"], d["instancias"]), (True, "credencial amp invalida", []))
        self.assertEqual(self.post.chamadas, [])
        self.assertNotIn(self.cam_cred, self.texto())
        self.assertNotIn(SENHA, self.texto())
        self.assertFalse(any(SENHA in l or self.cam_cred in l for l in self.logs))

    def test_erros_curtos_e_fixos(self):
        casos = [(PostFalso(login=OSError("x " + SENHA)), "amp sem resposta"),
                 (PostFalso(login={"success": False, "resultReason": SENHA}), "amp login falhou"),
                 (PostFalso(instancias="lixo"), "amp formato inesperado"),
                 (PostFalso(instancias=ValueError(SENHA)), "amp sem resposta")]
        for post, erro in casos:
            self.cred()
            self.agora += 1000
            self.inv(post).inventariar()
            d = self.doc()
            with self.subTest(erro=erro):
                self.assertEqual((d["ativo"], d["erro"], d["instancias"]), (True, erro, []))
                self.assertLessEqual(len(d["erro"]), 40)

    def test_a_senha_nunca_aparece_em_nada(self):
        casos = [PostFalso(), PostFalso(login=OSError(SENHA)), PostFalso(login={"success": False, "x": SENHA}),
                 PostFalso(instancias=RuntimeError(SENHA)), PostFalso(instancias={"vazio": SENHA}),
                 PostFalso(login=urllib.error.HTTPError(URL, 500, SENHA, {}, None)),
                 PostFalso(logout=RuntimeError(SENHA))]
        for post in casos:
            self.cred()
            self.agora += 1000
            self.logs.clear()
            self.inv(post).inventariar()
            self.assertNotIn(SENHA, self.texto())
            self.assertFalse(any(SENHA in l for l in self.logs), self.logs)
            for nome in os.listdir(self.estado):
                with open(os.path.join(self.estado, nome), encoding="utf-8", errors="replace") as f:
                    self.assertNotIn(SENHA, f.read(), nome)

    def test_a_senha_nunca_vai_para_argv(self):
        argvs = []
        self.cred()
        e = ex.Executor(self.cfg, executar=lambda argv, timeout: argvs.append(list(argv)) or (0, "", ""),
                        dono=self.dono, log=self.logs.append, amp_post=PostFalso())
        e.amp = {"url": URL, "credenciais": self.cam_cred}
        e.agora_inv = lambda: NS
        e.inventariar()
        self.assertFalse(any(SENHA in a or USUARIO in a for argv in argvs for a in argv))

    def test_reuso_dentro_da_janela_nao_consulta_de_novo(self):
        self.cred()
        self.inv().inventariar()
        for atraso in (0, 15, ex.AMP_REUSO_S - 1):
            self.agora = NS + atraso
            e = self.inv()
            e.inventariar()
            self.assertEqual(self.post.chamadas, [], atraso)
        self.assertEqual(self.doc()["gerado"], NS)

    def test_depois_da_janela_consulta_de_novo(self):
        self.cred()
        self.inv().inventariar()
        self.agora = NS + ex.AMP_REUSO_S
        self.inv().inventariar()
        self.assertEqual(len(self.post.chamadas), 3)
        self.assertEqual(self.doc()["gerado"], NS + ex.AMP_REUSO_S)

    def test_a_janela_cabe_na_validade_do_web(self):
        import ecossistema
        # o web chama de velho o arquivo de mais de 60 s: o inventario volta a cada 15 s (+ o tempo da rodada)
        self.assertGreaterEqual(ex.AMP_REUSO_S, 15)
        self.assertLessEqual(ex.AMP_REUSO_S + 15 + 15, ecossistema.INVENTARIO_VALIDADE_S)

    def test_arquivo_com_gerado_no_futuro_nao_trava_o_reuso(self):
        self.cred()
        with open(os.path.join(self.estado, "jogos.json"), "w") as f:
            json.dump({"versao": 1, "gerado": NS + 10 ** 6, "ativo": True, "erro": None, "instancias": []}, f)
        self.inv().inventariar()
        self.assertEqual(len(self.post.chamadas), 3)
        self.assertEqual(self.doc()["gerado"], NS)

    def test_arquivo_anterior_ilegivel_ou_symlink_e_refeito(self):
        self.cred()
        alvo = os.path.join(self._tmp.name, "alvo-externo")
        with open(alvo, "w") as f:
            f.write(json.dumps({"gerado": NS}))
        os.symlink(alvo, os.path.join(self.estado, "jogos.json"))
        self.inv().inventariar()
        self.assertEqual(len(self.post.chamadas), 3)  # nao seguiu o link para decidir
        with open(alvo) as f:
            self.assertEqual(json.load(f), {"gerado": NS})  # e nao escreveu atraves dele
        self.assertFalse(os.path.islink(os.path.join(self.estado, "jogos.json")))

    def test_lixo_no_arquivo_anterior(self):
        self.cred()
        for lixo in ("", "{", "[]", '{"gerado": "x"}', '{"gerado": true}', "\xff", "9" * 100000):
            with open(os.path.join(self.estado, "jogos.json"), "w") as f:
                f.write(lixo)
            e = self.inv()
            e.inventariar()
            self.assertEqual(len(self.post.chamadas), 3, repr(lixo)[:20])

    def test_falha_do_amp_nao_derruba_servicos(self):
        self.cred()
        self.inv(PostFalso(login=OSError())).inventariar()
        self.assertIn("servicos.json", os.listdir(self.estado))
        self.assertEqual(self.doc()["erro"], "amp sem resposta")

    def test_excecao_qualquer_do_post_e_isolada(self):
        self.cred()
        self.inv(PostFalso(login=ex.Falha("x"))).inventariar()  # qualquer Exception e isolada
        self.assertEqual(self.doc()["erro"], "amp sem resposta")

    def test_tmp_symlink_nao_e_seguido(self):
        self.cred()
        alvo = os.path.join(self._tmp.name, "alvo-externo")
        with open(alvo, "w") as f:
            f.write("intocado")
        os.symlink(alvo, os.path.join(self.estado, ".jogos.json.tmp"))
        self.inv().inventariar()
        with open(alvo) as f:
            self.assertEqual(f.read(), "intocado")
        self.assertTrue(self.doc()["ativo"])

    def test_so_grava_dentro_do_status(self):
        self.cred()
        antes = set(os.listdir(self._tmp.name))
        self.inv().inventariar()
        self.assertEqual(set(os.listdir(self._tmp.name)), antes)
        self.assertEqual(sorted(os.listdir(self.estado)), ["jogos.json", "servicos.json"])

    def test_nada_do_amp_vira_nome_de_arquivo(self):
        self.cred()
        self.inv(PostFalso(instancias=ads(inst(nome="../../etc/passwd", iid="../../x")))).inventariar()
        self.assertEqual(sorted(os.listdir(self.estado)), ["jogos.json", "servicos.json"])
        self.assertEqual(sorted(os.listdir(self._tmp.name)), sorted(["spool", "status", "amp.cred"]))

    def test_instancias_do_json_sao_ascii(self):
        self.cred()
        self.inv(PostFalso(instancias=ads(inst(nome="Zé ☃ Servidor")))).inventariar()
        self.assertTrue(self.texto().isascii())

    def test_ordem_e_maximo_16_no_arquivo(self):
        self.cred()
        itens = [inst("%032x" % n, nome="Srv %02d" % n, running=n % 2 == 0, estado=20 if n % 2 == 0 else 0)
                 for n in range(30)]
        self.inv(PostFalso(instancias=ads(*itens))).inventariar()
        self.assertEqual(len(self.doc()["instancias"]), 16)

    def test_sem_diretorios_nao_faz_nada(self):
        import shutil
        shutil.rmtree(self.estado)
        shutil.rmtree(self.spool)
        self.cred()
        self.assertEqual(self.inv().inventariar(), 0)
        self.assertEqual(self.post.chamadas, [])


class IntegracaoHttpRealTest(JogosBase):
    """Executor inteiro contra o servidor HTTP falso, sem injetar `amp_post` (usa o cliente urllib de verdade)."""

    def test_de_ponta_a_ponta(self):
        s = Servidor({"/API/Core/Login": json_ok({"success": True, "sessionID": SID}),
                      "/API/ADSModule/GetInstances": json_ok(ads(inst(), inst(IID_B, nome="Palworld", running=False,
                                                                                estado=0)))})
        self.addCleanup(s.fechar)
        self.cred()
        e = ex.Executor(self.cfg, executar=lambda argv, timeout: (0, "", ""), dono=self.dono, log=self.logs.append)
        e.amp = {"url": s.url, "credenciais": self.cam_cred}
        e.agora_inv = lambda: NS
        e.inventariar()
        d = self.doc()
        self.assertEqual([(i["nome"], i["estado"]) for i in d["instancias"]],
                         [("Minecraft", "rodando"), ("Palworld", "parado")])
        login = json.loads(s.pedidos[0]["corpo"])
        self.assertEqual(login, {"username": USUARIO, "password": SENHA, "token": "", "rememberMe": False})
        self.assertNotIn(SENHA, self.texto())
        self.assertEqual(self.logs, [])


# ------------------------------------------------------------------ config/main

class CfgAmpTest(unittest.TestCase):
    def carrega(self, dados):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump(dados, f)
            return ex.carregar_cfg(cam)

    def test_ausente_e_desligado(self):
        self.assertIsNone(self.carrega({})["amp"])

    def test_valida(self):
        amp = {"url": "http://10.0.0.60:8080", "credenciais": "/etc/kindle-monitor/amp.cred"}
        self.assertEqual(self.carrega({"amp": amp})["amp"], amp)

    def test_invalida_desliga_so_o_amp_e_guarda_o_motivo(self):
        cfg = self.carrega({"amp": {"url": "http://127.0.0.1:8080", "credenciais": "/etc/kindle-monitor/amp.cred"},
                            "servicos_kindle": []})
        self.assertIsNone(cfg["amp"])
        self.assertIn("amp.url", cfg["amp_erro"])
        self.assertNotIn("127.0.0.1", cfg["amp_erro"])

    def test_main_loga_aviso_no_inventario(self):
        import tempfile
        logs = []
        with tempfile.TemporaryDirectory() as d:
            cam = os.path.join(d, "c.json")
            with open(cam, "w") as f:
                json.dump({"amp": {"url": "https://10.0.0.60:8080", "credenciais": "/etc/kindle-monitor/amp.cred"},
                           "comandos": {"spool": os.path.join(d, "x", "spool"), "estado": os.path.join(d, "x", "status")}}, f)
            ex.main(["--config", cam, "--inventario"], log=logs.append)
        self.assertTrue(any("amp invalida" in l for l in logs), logs)

    def test_a_producao_nao_tem_como_liberar_loopback(self):
        # a validacao nao tem parametro nem constante para isso; so o teste ajusta `Executor.amp` depois de validar
        import inspect
        self.assertEqual(list(inspect.signature(ex.validar_amp).parameters), ["valor"])
        with self.assertRaises(ValueError):
            ex.validar_amp({"url": "http://127.0.0.1:8080", "credenciais": "/etc/kindle-monitor/amp.cred"})


class UnidadeTest(unittest.TestCase):
    def test_timeout_da_unit_cobre_o_pior_caso(self):
        """4 chamadas em lote de servicos + tailscale + 2 de rotinas (10 s cada) + AMP (login, instancias e logout,
        8 s cada, mais ate um recebimento de sobra por chamada) tem de caber em TimeoutStartSec."""
        cam = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "deploy", "kindle-monitor-inventario.service")
        with open(cam, encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        t = int(next(l for l in linhas if l.startswith("TimeoutStartSec=")).split("=")[1])
        pior = 4 * ex.TIMEOUT_INVENTARIO + ex.TIMEOUT_TAILSCALE + 2 * ex.TIMEOUT_ROTINAS + 3 * 2 * ex.AMP_TIMEOUT_S
        self.assertEqual(pior, 118)
        self.assertGreaterEqual(t, pior + 30)


if __name__ == "__main__":
    unittest.main()
