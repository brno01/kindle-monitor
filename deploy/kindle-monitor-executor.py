#!/usr/bin/python3 -I
"""Executor root do kindle-monitor: cumpre os pedidos registrados pelo servidor web.

O servidor web (User=nobody) so grava arquivos vazios "<epoch_ns>-<acao>.req" no spool. Este programa
roda como root (kindle-monitor-executor.service, acionado pela .path), valida o NOME do arquivo, apaga o
pedido ANTES de executar (nunca repete), ignora o conteudo e procura o id numa tabela FIXA de acoes.
Nada do pedido entra em comando algum; nunca ha shell. Resultado em JSON no diretorio de estado.

Seguranca dos diretorios: /run/kindle-monitor, o spool e o status sao criados pelo tmpfiles.d (root). Aqui
cada um e aberto com O_DIRECTORY|O_NOFOLLOW e conferido com fstat (dono, permissoes); dai em diante tudo
usa dir_fd, nunca caminho, entao trocar um diretorio por symlink nao leva o root para fora. Se algo nao
bater, recusa tudo (excecao Recusa, saida 1). Se os diretorios nao existem, sai 0 sem criar nada.
Biblioteca padrao apenas.
"""
import argparse
import grp
import json
import os
import re
import signal
import stat
import subprocess
import sys
import time
import urllib.request

ACOES = ("gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar",
         "ragnarok-reiniciar", "ollama-reiniciar")
SPOOL_PADRAO = "/run/kindle-monitor/spool"
ESTADO_PADRAO = "/run/kindle-monitor/status"
OLLAMA_PADRAO = "http://10.0.0.1:11435"
GUARDAR = 20
TIMEOUT_CMD = 40
TIMEOUT_BOT = 20
TIMEOUT_HTTP = 5
DETALHE_MAX = 80
PEDIDOS_MAX = 10          # pedidos por passada
VALIDADE_S = 60           # pedido mais velho que isso e descartado
TEMP_VELHO_S = 60         # temporarios "." mais velhos que isso sao apagados
COOLDOWN_S = 30           # intervalo minimo entre duas execucoes da mesma acao
COOLDOWN_ARQ = ".cooldown.json"
RE_REQ = re.compile(r"^(\d{1,20})-([a-z-]{3,32})\.req$")
RE_JSON = re.compile(r"^(\d{1,20})-[a-z-]{3,32}\.json$")
RE_BOT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")  # nunca comeca com "-" (viraria opcao)
PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

INCUS = ["incus", "exec", "games", "--project", "core", "--"]
TIMER = "ro-bot-scheduler.timer"
AUTOUPDATE = ["systemctl", "is-active", "--quiet", "cerberus-autoupdate.service"]

# Tabela FIXA das acoes que sao so argv. As outras duas (gpu-descarregar, bots-pausar) tem funcao propria.
TABELA_ARGV = {
    "bots-retomar": [INCUS + ["systemctl", "start", TIMER]],
    "monitor-reiniciar": [["systemctl", "restart", "kindle-monitor.service"]],
    "ragnarok-reiniciar": [INCUS + ["systemctl", "restart", "rathena-login", "rathena-char", "rathena-map"]],
    "ollama-reiniciar": [["systemctl", "restart", "ollama-gpu.service"]],
}
# Recusadas enquanto a janela de atualizacao automatica roda.
BLOQUEADAS_NO_AUTOUPDATE = ("ragnarok-reiniciar", "ollama-reiniciar")


class Falha(Exception):
    """Falha esperada; o texto vira o detalhe (ASCII, ate 80 chars). rc e o codigo de saida, se houver."""
    def __init__(self, msg, rc=1):
        super().__init__(msg)
        self.rc = rc


class Recusa(Exception):
    """Diretorio fora do esperado (symlink, dono, permissoes): o executor recusa tudo."""


class Interrompido(BaseException):
    """SIGTERM durante um pedido (BaseException para nao cair nos 'except Exception')."""


def _sigterm(signum, frame):
    raise Interrompido()


def _log_padrao(linha):
    print(linha, file=sys.stderr, flush=True)


def _curto(texto, limite=DETALHE_MAX):
    return re.sub(r"[^A-Za-z0-9 _.,:;()/=+-]", "?", str(texto))[:limite]


def linha_log(acao, pid, rc, estado, detalhe):
    return "acao=%s id=%s rc=%s estado=%s detalhe=%s" % (_curto(acao, 32), _curto(pid, 20), rc, estado,
                                                         _curto(detalhe))


def validar_cfg(c):
    """Valida a secao "comandos" da config. ValueError com a causa."""
    if not isinstance(c, dict):
        raise ValueError("comandos deve ser um objeto")
    r = {"spool": SPOOL_PADRAO, "estado": ESTADO_PADRAO, "acoes": list(ACOES)}
    r.update({k: v for k, v in c.items() if k in r})
    for k in ("spool", "estado"):
        if not isinstance(r[k], str) or not os.path.isabs(r[k]):
            raise ValueError("comandos.%s deve ser um caminho absoluto (texto)" % k)
    if os.path.dirname(r["spool"]) != os.path.dirname(r["estado"]) or \
            os.path.basename(r["spool"]) == os.path.basename(r["estado"]):
        raise ValueError("comandos.spool e comandos.estado devem ser irmaos no mesmo diretorio")
    if not isinstance(r["acoes"], list) or not all(isinstance(a, str) and a in ACOES for a in r["acoes"]):
        raise ValueError("comandos.acoes deve ser lista de ids conhecidos: %s" % ", ".join(ACOES))
    return r


def _gid_nogroup():
    for nome in ("nogroup", "nobody"):
        try:
            return grp.getgrnam(nome).gr_gid
        except KeyError:
            pass
    raise Recusa("grupo nogroup inexistente")


def executar_padrao(argv, timeout):
    """Roda argv (lista, sem shell). Devolve (rc, stdout, stderr); TimeoutExpired sobe."""
    p = subprocess.run(argv, shell=False, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       errors="replace", timeout=timeout, env={"PATH": PATH, "LANG": "C"})
    return p.returncode, p.stdout, p.stderr


def http_padrao(metodo, url, corpo, timeout):
    dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
    req = urllib.request.Request(url, data=dados, method=metodo,
                                 headers={"Content-Type": "application/json"} if dados else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read(1 << 20).decode("utf-8") or "{}")


def bots_ativos(texto):
    """Nomes dos bots com ESTADO 'active' na saida de `ro-bot list` (cabecalho BOT ESTADO ...)."""
    nomes = []
    for linha in texto.splitlines():
        col = linha.split()
        if len(col) < 2 or col[0] == "BOT" or col[1] != "active":
            continue
        if RE_BOT.match(col[0]):
            nomes.append(col[0])
    return nomes


class Executor:
    def __init__(self, cfg, executar=executar_padrao, http=http_padrao, agora_ns=time.time_ns,
                 ollama=OLLAMA_PADRAO, dono=None, log=_log_padrao):
        """`dono` = (uid, gid do spool) esperado; padrao (0, nogroup). Injetavel para testes sem root."""
        cfg = validar_cfg(cfg)
        self.spool = cfg["spool"]
        self.estado = cfg["estado"]
        self.habilitadas = list(cfg["acoes"])
        self.executar = executar
        self.http = http
        self.agora_ns = agora_ns
        self.ollama = ollama.rstrip("/")
        self.dono = dono
        self.log = log
        self.fd_spool = self.fd_estado = None

    # ------------------------------------------------------- diretorios
    @staticmethod
    def _abrir_dir(nome, rotulo, dir_fd=None):
        try:
            return os.open(nome, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
        except FileNotFoundError:
            raise
        except OSError as e:  # ELOOP (symlink), ENOTDIR, EACCES...
            raise Recusa("%s: nao abre como diretorio sem symlink (%s)" % (rotulo, e.strerror))

    def _conferir(self, fd, rotulo, grupo=None):
        uid, gid_spool = self.dono if self.dono else (0, None)
        st = os.fstat(fd)
        if st.st_uid != uid:
            raise Recusa("%s: dono uid=%d, esperado %d" % (rotulo, st.st_uid, uid))
        if grupo:  # spool: root:nogroup, sticky, sem escrita para "outros"
            esperado = gid_spool if gid_spool is not None else _gid_nogroup()
            if st.st_gid != esperado:
                raise Recusa("%s: grupo gid=%d, esperado %d" % (rotulo, st.st_gid, esperado))
            if not st.st_mode & stat.S_ISVTX:
                raise Recusa("%s: sem sticky bit" % rotulo)
            if st.st_mode & stat.S_IWOTH:
                raise Recusa("%s: gravavel por outros" % rotulo)
        elif st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise Recusa("%s: gravavel por grupo/outros" % rotulo)

    def _abrir(self):
        """Abre pai, spool e status (nesta ordem) com verificacao. None se ainda nao existem."""
        pai = os.path.dirname(self.spool)
        abertos = []
        try:
            try:
                fd_pai = self._abrir_dir(pai, "pai")
            except FileNotFoundError:
                return self._ausente()
            abertos.append(fd_pai)
            self._conferir(fd_pai, "pai")
            novos = []
            for nome, rotulo, grupo in ((os.path.basename(self.spool), "spool", True),
                                        (os.path.basename(self.estado), "status", False)):
                try:
                    fd = self._abrir_dir(nome, rotulo, dir_fd=fd_pai)
                except FileNotFoundError:
                    return self._ausente()
                abertos.append(fd)
                novos.append(fd)
                self._conferir(fd, rotulo, grupo)
            self.fd_spool, self.fd_estado = novos
            return True
        except BaseException:
            self._fechar(abertos)
            raise
        finally:
            self._pai_fds = abertos

    def _ausente(self):
        self.log("diretorios do spool/status ainda nao existem (tmpfiles.d); nada a fazer")
        return None

    @staticmethod
    def _fechar(fds):
        for fd in fds:
            try:
                os.close(fd)
            except OSError:
                pass

    # ---------------------------------------------------------------- fila
    def processar_spool(self):
        self._pai_fds = []
        try:
            if self._abrir() is None:
                return 0
            return self._passada()
        finally:
            self._fechar(self._pai_fds)
            self._pai_fds = []
            self.fd_spool = self.fd_estado = None

    def _passada(self):
        agora = self.agora_ns()
        self._varrer(self.fd_spool, agora)
        self._varrer(self.fd_estado, agora)
        try:
            nomes = os.listdir(self.fd_spool)
        except OSError as e:
            self.log("nao consegui listar o spool: %s" % e.strerror)
            return 0
        pedidos = []
        for n in nomes:
            if not n.endswith(".req"):
                continue  # fora do glob da .path: ignorado
            m = RE_REQ.match(n)
            if m:
                pedidos.append((int(m.group(1)), n, m.group(2)))
            else:
                self._descartar(n)
        pedidos.sort()
        vistos = set()
        cooldown = self._ler_cooldown()
        feitos = 0
        for num, nome, acao in pedidos[:PEDIDOS_MAX]:
            if not self._consumir(nome):
                continue
            feitos += 1
            self._executar_pedido(num, nome[:-len(".req")], acao, agora, vistos, cooldown)
        return feitos

    def _varrer(self, fd, agora_ns):
        """Apaga temporarios (nome com '.' inicial) com mais de TEMP_VELHO_S s; nunca segue link nem apaga diretorio."""
        try:
            nomes = os.listdir(fd)
        except OSError:
            return
        for n in nomes:
            if not n.startswith(".") or n == COOLDOWN_ARQ:
                continue
            try:
                st = os.stat(n, dir_fd=fd, follow_symlinks=False)
                if not stat.S_ISDIR(st.st_mode) and agora_ns / 1e9 - st.st_mtime > TEMP_VELHO_S:
                    os.unlink(n, dir_fd=fd)
            except OSError:
                pass

    def _descartar(self, nome):
        try:
            if not stat.S_ISDIR(os.stat(nome, dir_fd=self.fd_spool, follow_symlinks=False).st_mode):
                os.unlink(nome, dir_fd=self.fd_spool)
        except OSError:
            pass

    def _consumir(self, nome):
        """Abre sem seguir symlink, confere que e arquivo comum e apaga. Conteudo nunca e lido."""
        try:
            fd = os.open(nome, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd_spool)
        except OSError:
            self._descartar(nome)  # symlink, diretorio ou sumiu: nao executa
            return False
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                self._descartar(nome)
                return False
            os.unlink(nome, dir_fd=self.fd_spool)
            return True
        except OSError:
            return False
        finally:
            os.close(fd)

    def _executar_pedido(self, num, pid, acao, agora_ns, vistos, cooldown):
        if agora_ns - num > VALIDADE_S * 10 ** 9:
            return self._final(num, pid, acao, "falhou", "pedido expirado")
        if acao not in ACOES:
            return self._final(num, pid, acao, "falhou", "acao desconhecida")
        if acao not in self.habilitadas:
            return self._final(num, pid, acao, "falhou", "acao desligada na config")
        if acao in vistos:
            return self._final(num, pid, acao, "falhou", "duplicado")
        vistos.add(acao)
        agora_s = agora_ns / 1e9
        ultimo = cooldown.get(acao)
        if ultimo is not None and 0 <= agora_s - ultimo < COOLDOWN_S:
            return self._final(num, pid, acao, "falhou", "cooldown de %d s" % COOLDOWN_S)
        cooldown[acao] = agora_s  # registrado ANTES de executar: queda no meio tambem conta
        self._gravar_cooldown(cooldown)
        self._gravar(pid, acao, "executando", "")
        try:
            detalhe = self._rodar(acao)
        except Falha as e:
            return self._final(num, pid, acao, "falhou", str(e), e.rc)
        except Interrompido:
            self._final(num, pid, acao, "falhou", "interrompido")
            raise
        except Exception:
            return self._final(num, pid, acao, "falhou", "erro inesperado")
        self._final(num, pid, acao, "ok", detalhe, 0)

    def _final(self, num, pid, acao, estado, detalhe, rc=1):
        self.log(linha_log(acao, num, rc, estado, detalhe))
        self._gravar(pid, acao, estado, detalhe)

    # ------------------------------------------------------------- estado
    def _gravar_arquivo(self, nome, dados):
        """tmp (O_EXCL, root, no dir_fd do status) + rename. Erros de E/S viram log, nunca derrubam a passada."""
        tmp = ".%s.tmp" % nome.lstrip(".")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK
        try:
            try:
                fd = os.open(tmp, flags, 0o644, dir_fd=self.fd_estado)
            except FileExistsError:  # sobra de uma queda; nao segue: unlink remove o link, nao o alvo
                os.unlink(tmp, dir_fd=self.fd_estado)
                fd = os.open(tmp, flags, 0o644, dir_fd=self.fd_estado)
            with os.fdopen(fd, "wb") as f:
                os.fchmod(f.fileno(), 0o644)
                f.write(dados)
            os.rename(tmp, nome, src_dir_fd=self.fd_estado, dst_dir_fd=self.fd_estado)
        except OSError as e:
            self.log("falha ao gravar %s: %s" % (_curto(nome, 40), e.strerror))
            try:
                os.unlink(tmp, dir_fd=self.fd_estado)
            except OSError:
                pass

    def _gravar(self, pid, acao, estado, detalhe):
        dados = {"acao": acao, "estado": estado, "quando": time.strftime("%H:%M:%S"),
                 "detalhe": detalhe[:DETALHE_MAX]}
        self._gravar_arquivo(pid + ".json", json.dumps(dados).encode("utf-8"))
        if estado != "executando":
            self._limpar()

    def _ler_cooldown(self):
        try:
            fd = os.open(COOLDOWN_ARQ, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd_estado)
        except OSError:
            return {}
        try:
            st = os.fstat(fd)
            uid = self.dono[0] if self.dono else 0
            if not stat.S_ISREG(st.st_mode) or st.st_uid != uid:
                return {}
            dados = json.loads(os.read(fd, 4096).decode("utf-8"))
        except (OSError, ValueError):
            return {}
        finally:
            os.close(fd)
        if not isinstance(dados, dict):
            return {}
        return {k: float(v) for k, v in dados.items()
                if k in ACOES and isinstance(v, (int, float)) and not isinstance(v, bool)}

    def _gravar_cooldown(self, cooldown):
        self._gravar_arquivo(COOLDOWN_ARQ, json.dumps(cooldown).encode("utf-8"))

    def _limpar(self):
        try:
            nomes = os.listdir(self.fd_estado)
        except OSError:
            return
        achados = []
        for n in nomes:
            m = RE_JSON.match(n)
            if m:
                achados.append((int(m.group(1)), n))
        achados.sort(reverse=True)
        for _, n in achados[GUARDAR:]:
            try:
                os.unlink(n, dir_fd=self.fd_estado)
            except OSError:
                pass

    # ------------------------------------------------------------- acoes
    def _cmd(self, argv, timeout=TIMEOUT_CMD):
        try:
            rc, out, _ = self.executar(argv, timeout)
        except subprocess.TimeoutExpired:
            raise Falha("tempo esgotado")
        except OSError:
            raise Falha("comando indisponivel")
        if rc != 0:
            raise Falha("codigo de saida %s" % rc, rc)
        return out

    def _autoupdate_ativo(self):
        try:
            rc, _, _ = self.executar(AUTOUPDATE, TIMEOUT_CMD)
        except (subprocess.TimeoutExpired, OSError):
            return False
        return rc == 0

    def _rodar(self, acao):
        if acao in BLOQUEADAS_NO_AUTOUPDATE and self._autoupdate_ativo():
            raise Falha("atualizacao automatica em andamento")
        if acao == "gpu-descarregar":
            return self._gpu()
        if acao == "bots-pausar":
            return self._bots_pausar()
        for argv in TABELA_ARGV[acao]:
            self._cmd(argv)
        return "concluido"

    def _bots_pausar(self):
        self._cmd(INCUS + ["systemctl", "stop", TIMER])
        nomes = bots_ativos(self._cmd(INCUS + ["ro-bot", "list"]))
        falhos = []
        for nome in nomes:
            try:
                self._cmd(INCUS + ["ro-bot", "stop", nome], TIMEOUT_BOT)
            except Falha:
                falhos.append(nome)
        if falhos:
            raise Falha("nao parou: " + ", ".join(falhos))
        return "timer parado; bots: " + (", ".join(nomes) if nomes else "nenhum ativo")

    def _gpu(self):
        try:
            ps = self.http("GET", self.ollama + "/api/ps", None, TIMEOUT_HTTP)
            modelos = []
            for m in ps.get("models", []) if isinstance(ps, dict) else []:
                nome = m.get("name") if isinstance(m, dict) else None
                if isinstance(nome, str) and 0 < len(nome) <= 128:
                    modelos.append(nome)
            for nome in modelos:
                self.http("POST", self.ollama + "/api/generate", {"model": nome, "keep_alive": 0}, TIMEOUT_HTTP)
        except (OSError, ValueError):
            raise Falha("ollama sem resposta")
        return "descarregado: " + ", ".join(modelos) if modelos else "nenhum modelo carregado"


def carregar_cfg(caminho):
    """Le e valida a secao "comandos". OSError/ValueError com a causa."""
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    if not isinstance(dados, dict):
        raise ValueError("config: raiz deve ser um objeto")
    return validar_cfg(dados.get("comandos", {}))


def main(argv=None, log=_log_padrao):
    p = argparse.ArgumentParser(description="Executor root do kindle-monitor.")
    p.add_argument("--config", required=True)
    args = p.parse_args(argv)
    try:
        cfg = carregar_cfg(args.config)
    except (OSError, ValueError) as e:
        # exit 0: config ruim nao pode virar laco de falhas disparado pela .path
        log("config invalida, nada feito: %s" % _curto(e, 120))
        return 0
    signal.signal(signal.SIGTERM, _sigterm)
    try:
        Executor(cfg, log=log).processar_spool()
    except Recusa as e:
        log("recusado: %s" % _curto(e, 160))
        return 1
    except Interrompido:
        log("interrompido por SIGTERM")
        return 143
    return 0


if __name__ == "__main__":
    sys.exit(main())
