"""Comandos do kindle-monitor, lado web (sem privilegio).

O processo web so REGISTRA o pedido: grava um arquivo vazio "<epoch_ns>-<acao>.req" no spool.
Quem executa e o executor root (deploy/kindle-monitor-executor.py), com uma tabela FIXA de acoes.
Nada aqui monta comando a partir do texto do pedido.
"""
import hashlib
import hmac
import ipaddress
import json
import math
import os
import re
import sys
import threading
import time

import servicos

ACOES = ("gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar")
TOKEN_HASH_PADRAO = "/etc/kindle-monitor/token.sha256"
PERMITIDOS_PADRAO = ()  # ninguem: os IPs (Kindle, notebook) vem de comandos.permitidos_de na config local
SPOOL_PADRAO = "/run/kindle-monitor/spool"
ESTADO_PADRAO = "/run/kindle-monitor/status"
CORPO_MAX = 1024
INTERVALO_S = 5.0
ESTADOS = ("executando", "ok", "falhou")
DETALHE_MAX = 80
RE_ARQ = re.compile(r"^(\d{1,20})-(" + servicos.TOKEN_ARQ + r")\.(req|json)\Z")
RE_HORA = re.compile(r"^\d\d:\d\d:\d\d\Z")
RE_TOKEN = re.compile(r"^[0-9a-fA-F]{64}\Z")
JSON_TIPO = "application/json"


def validar_config(raw):
    """Normaliza a secao "comandos" da config. ValueError com a causa."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("config: comandos deve ser um objeto")
    raw = {k: v for k, v in raw.items() if not str(k).startswith("_")}
    c = {"token_hash_arquivo": TOKEN_HASH_PADRAO, "permitidos_de": list(PERMITIDOS_PADRAO),
         "acoes": list(ACOES), "spool": SPOOL_PADRAO, "estado": ESTADO_PADRAO}
    c.update(raw)
    for k in ("token_hash_arquivo", "spool", "estado"):
        if not isinstance(c[k], str) or not c[k]:
            raise ValueError("config: comandos.%s deve ser um caminho" % k)
    if not isinstance(c["permitidos_de"], list):
        raise ValueError("config: comandos.permitidos_de deve ser lista de IPs")
    for ip in c["permitidos_de"]:
        try:
            ipaddress.ip_address(ip)
        except (ValueError, TypeError):
            raise ValueError("config: comandos.permitidos_de com IP invalido")
    if not isinstance(c["acoes"], list) or not all(a in ACOES for a in c["acoes"]):
        raise ValueError("config: comandos.acoes deve ser lista de ids conhecidos: %s" % ", ".join(ACOES))
    return c


def _seguro(texto, limite=40):
    """Texto de origem externa para o log: so caracteres imprimiveis simples."""
    s = re.sub(r"[^A-Za-z0-9_.-]", "?", str(texto))
    return s[:limite]


def _hora(ns):
    return time.strftime("%H:%M:%S", time.localtime(ns / 1e9))


class Comandos:
    def __init__(self, cfg, relogio=time.monotonic, agora_ns=time.time_ns, log=None, catalogo=None):
        self.cfg = cfg
        self.catalogo = {c["id"]: c for c in servicos.validar_catalogo(catalogo or [])}
        self.relogio = relogio
        self.agora_ns = agora_ns
        self.log = log or (lambda linha: print(linha, file=sys.stderr, flush=True))
        self._lock = threading.Lock()
        self._ultimo = None  # relogio do ultimo pedido aceito

    # ----------------------------------------------------------------- POST
    def _auditar(self, ip, acao, resultado, motivo=""):
        self.log("%s comando ip=%s acao=%s %s%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), _seguro(ip, 45), _seguro(acao) if acao else "-",
            resultado, (" motivo=" + motivo) if motivo else ""))

    def _hash(self):
        """sha256 (64 hex) do token, lido do arquivo. O web nunca ve o token cru."""
        try:
            with open(self.cfg["token_hash_arquivo"], "r", encoding="ascii") as f:
                linha = f.readline().strip()
        except (OSError, ValueError):
            return None
        return linha.lower() if RE_TOKEN.match(linha) else None

    def processar(self, ip, token, tipo, tamanho, corpo):
        """Devolve (status, dict, cabecalhos extras). `corpo` e um arquivo com read()."""
        def recusa(status, msg, motivo, acao="", extra=None):
            self._auditar(ip, acao, "recusado", motivo)
            return status, {"erro": msg}, extra or {}

        if ip not in self.cfg["permitidos_de"]:  # antes de revelar se os comandos estao ligados
            return recusa(403, "origem nao permitida", "ip fora da lista")
        esperado = self._hash()
        if esperado is None:
            return recusa(503, "comandos desligados", "hash do token ausente ou ilegivel")
        enviado = token.encode("utf-8", "replace") if isinstance(token, str) else b""
        if not hmac.compare_digest(hashlib.sha256(enviado).hexdigest(), esperado):
            return recusa(401, "nao autorizado", "token ausente ou errado")
        if (tipo or "").split(";")[0].strip().lower() != JSON_TIPO:
            return recusa(415, "use application/json", "content-type")
        if tamanho is None or tamanho < 0:
            return recusa(400, "corpo invalido", "content-length")
        if tamanho > CORPO_MAX:
            return recusa(413, "corpo grande demais", "corpo > 1 KB")
        try:
            dados = corpo.read(tamanho)
        except OSError:  # inclui TimeoutError: cliente lento
            return recusa(408, "tempo esgotado", "leitura do corpo")
        try:
            pedido = json.loads(dados.decode("utf-8"))
            acao = pedido["acao"]
        except (ValueError, KeyError, TypeError, UnicodeDecodeError):
            return recusa(400, "corpo invalido", "json invalido")
        if not isinstance(acao, str):
            return recusa(400, "acao invalida", "acao nao e texto")
        if not self._acao_valida(acao):
            return recusa(400, "acao invalida", "acao desconhecida ou desligada", acao)
        with self._lock:
            agora = self.relogio()
            if self._ultimo is not None and agora - self._ultimo < INTERVALO_S:
                espera = max(1, math.ceil(INTERVALO_S - (agora - self._ultimo)))
                return recusa(429, "muitos pedidos", "limite de 1 a cada 5 s", acao,
                              {"Retry-After": str(espera)})
            try:
                pid = self._gravar(acao)
            except (FileNotFoundError, NotADirectoryError):
                return recusa(503, "comandos desligados", "spool ausente", acao)
            except OSError:
                return recusa(500, "erro interno", "falha ao gravar o pedido", acao)
            self._ultimo = agora
        self._auditar(ip, acao, "aceito")
        return 202, {"estado": "aceito", "acao": acao, "id": pid}, {}

    def _acao_valida(self, acao):
        """Acao rapida ligada na config, ou svc:<id>:<verbo> com id no catalogo e verbo permitido."""
        s = servicos.acao_svc(acao)
        if s:
            item = self.catalogo.get(s[0])
            return bool(item) and s[1] in item["verbos"]
        return acao in ACOES and acao in self.cfg["acoes"]

    def _gravar(self, acao):
        spool = self.cfg["spool"]
        # O spool e criado pelo tmpfiles.d (root); o web nunca cria nem muda modo.
        pid = "%d-%s" % (self.agora_ns(), servicos.acao_para_nome(acao))
        tmp = os.path.join(spool, ".%s.tmp" % pid)
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        try:
            os.rename(tmp, os.path.join(spool, pid + ".req"))
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return pid

    # --------------------------------------------------------------- estado
    @staticmethod
    def _listar(diretorio, ext):
        try:
            nomes = os.listdir(diretorio)
        except OSError:
            return []
        achados = []
        for n in nomes:
            m = RE_ARQ.match(n)
            if m and m.group(3) == ext:
                achados.append((int(m.group(1)), n, m.group(2)))
        achados.sort(reverse=True)
        return achados

    def ultimos(self, n=5):
        itens = []
        for num, nome, token in self._listar(self.cfg["spool"], "req"):
            acao = servicos.nome_para_acao(token)
            if acao is None:
                continue
            try:
                if not os.path.isfile(os.path.join(self.cfg["spool"], nome)) or \
                        os.path.islink(os.path.join(self.cfg["spool"], nome)):
                    continue
            except OSError:
                continue
            itens.append((num, {"acao": acao, "estado": "executando",
                                "quando": _hora(num), "detalhe": ""}))
        for num, nome, _ in self._listar(self.cfg["estado"], "json"):
            if len(itens) >= n * 2 + 20:
                break
            item = self._ler_resultado(os.path.join(self.cfg["estado"], nome))
            if item:
                itens.append((num, item))
        itens.sort(key=lambda p: p[0], reverse=True)
        return [i for _, i in itens[:n]]

    @staticmethod
    def _ler_resultado(caminho):
        try:
            if os.path.islink(caminho):
                return None
            fd = os.open(caminho, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "r", encoding="utf-8") as f:
                d = json.loads(f.read(4096))
        except (OSError, ValueError):
            return None
        if not isinstance(d, dict):
            return None
        acao, estado, quando, detalhe = (d.get(k) for k in ("acao", "estado", "quando", "detalhe"))
        if not (isinstance(acao, str) and (re.match(r"^[a-z-]{3,32}\Z", acao) or servicos.acao_svc(acao))):
            return None
        if estado not in ESTADOS or not (isinstance(quando, str) and RE_HORA.match(quando)):
            return None
        if not isinstance(detalhe, str):
            detalhe = ""
        return {"acao": acao, "estado": estado, "quando": quando, "detalhe": detalhe[:DETALHE_MAX]}
