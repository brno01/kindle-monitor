#!/usr/bin/python3 -I
"""Executor root do kindle-monitor: cumpre os pedidos registrados pelo servidor web.

O servidor web (User=nobody) so grava arquivos vazios "<epoch_ns>-<acao>.req" no spool. Este programa
roda como root (kindle-monitor-executor.service, acionado pela .path), valida o NOME do arquivo, apaga o
pedido ANTES de executar (nunca repete), ignora o conteudo e procura o id numa tabela FIXA de acoes.
Nada do pedido entra em comando algum; nunca ha shell. Resultado em JSON no diretorio de estado.
Biblioteca padrao apenas.
"""
import argparse
import json
import os
import re
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
PASSADAS_MAX = 10
RE_REQ = re.compile(r"^(\d{1,20})-([a-z-]{3,32})\.req$")
RE_JSON = re.compile(r"^(\d{1,20})-[a-z-]{3,32}\.json$")
RE_BOT = re.compile(r"^[a-z0-9_-]{1,32}$")
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
    """Falha esperada; o texto vira o detalhe (ASCII, ate 80 chars)."""


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
                 ollama=OLLAMA_PADRAO):
        self.spool = cfg.get("spool", SPOOL_PADRAO)
        self.estado = cfg.get("estado", ESTADO_PADRAO)
        self.habilitadas = [a for a in cfg.get("acoes", ACOES) if a in ACOES]
        self.executar = executar
        self.http = http
        self.agora_ns = agora_ns
        self.ollama = ollama.rstrip("/")

    # ---------------------------------------------------------------- fila
    def _pedidos(self):
        try:
            nomes = os.listdir(self.spool)
        except OSError:
            return []
        achados = []
        for n in nomes:
            m = RE_REQ.match(n)
            if m:
                achados.append((int(m.group(1)), n, m.group(2)))
        achados.sort()
        return achados

    def _varrer_lixo(self):
        """Remove (sem seguir links) o que nao tem nome valido, para a .path nao disparar em laco.
        Nomes com '.' inicial sao os temporarios do servidor web e ficam."""
        try:
            nomes = os.listdir(self.spool)
        except OSError:
            return
        for n in nomes:
            if n.startswith(".") or RE_REQ.match(n):
                continue
            caminho = os.path.join(self.spool, n)
            try:
                if not stat.S_ISDIR(os.lstat(caminho).st_mode):
                    os.unlink(caminho)
            except OSError:
                pass

    def _consumir(self, nome):
        """Abre sem seguir symlink, confere que e arquivo comum e apaga. Conteudo nunca e lido."""
        caminho = os.path.join(self.spool, nome)
        try:
            fd = os.open(caminho, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except OSError:
            self._descartar(caminho)  # symlink ou sumiu: nao executa
            return False
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                self._descartar(caminho)
                return False
            os.unlink(caminho)
            return True
        except OSError:
            return False
        finally:
            os.close(fd)

    @staticmethod
    def _descartar(caminho):
        try:
            if not stat.S_ISDIR(os.lstat(caminho).st_mode):
                os.unlink(caminho)
        except OSError:
            pass

    def processar_spool(self):
        self._varrer_lixo()
        n = 0
        for _, nome, acao in self._pedidos():
            if not self._consumir(nome):
                continue
            pid = nome[:-len(".req")]
            n += 1
            self._executar_pedido(pid, acao)
        return n

    def _executar_pedido(self, pid, acao):
        if acao not in ACOES:
            return self._gravar(pid, acao, "falhou", "acao desconhecida")
        if acao not in self.habilitadas:
            return self._gravar(pid, acao, "falhou", "acao desligada na config")
        self._gravar(pid, acao, "executando", "")
        try:
            detalhe = self._rodar(acao)
            self._gravar(pid, acao, "ok", detalhe)
        except Falha as e:
            self._gravar(pid, acao, "falhou", str(e))
        except Exception:
            self._gravar(pid, acao, "falhou", "erro inesperado")

    # ------------------------------------------------------------- estado
    def _gravar(self, pid, acao, estado, detalhe):
        os.makedirs(self.estado, mode=0o755, exist_ok=True)
        os.chmod(self.estado, 0o755)
        dados = {"acao": acao, "estado": estado, "quando": time.strftime("%H:%M:%S"),
                 "detalhe": detalhe[:DETALHE_MAX]}
        tmp = os.path.join(self.estado, ".%s.tmp" % pid)
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(dados, f)
        os.chmod(tmp, 0o644)
        os.rename(tmp, os.path.join(self.estado, pid + ".json"))
        if estado != "executando":
            self._limpar()

    def _limpar(self):
        achados = []
        for n in os.listdir(self.estado):
            m = RE_JSON.match(n)
            if m:
                achados.append((int(m.group(1)), n))
        achados.sort(reverse=True)
        for _, n in achados[GUARDAR:]:
            try:
                os.unlink(os.path.join(self.estado, n))
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
            raise Falha("codigo de saida %s" % rc)
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
    with open(caminho, "r", encoding="utf-8") as f:
        c = json.load(f).get("comandos", {})
    return c if isinstance(c, dict) else {}


def main(argv=None):
    p = argparse.ArgumentParser(description="Executor root do kindle-monitor.")
    p.add_argument("--config", required=True)
    args = p.parse_args(argv)
    try:
        cfg = carregar_cfg(args.config)
    except (OSError, ValueError) as e:
        print("erro na config: %s" % e, file=sys.stderr)
        return 2
    ex = Executor(cfg)
    for _ in range(PASSADAS_MAX):
        if ex.processar_spool() == 0:
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
