#!/usr/bin/env python3
"""Servidor HTTP do kindle-monitor: GET de leitura e um POST /comando autenticado por token.

Endpoints: /tela.txt e /tela.png (parametros ?pagina=resumo|detalhes|comandos e, no PNG, &armado=<id>),
/botoes.json e /botoes.txt (layout dos botoes), /metricas.json, /historico.json, /saude e /comando/estado.
POST /comando so registra um pedido (ver comandos.py); quem executa e o executor root.
NUNCA escute em 0.0.0.0: passe --bind com o IP da LAN/tailnet.
"""
import argparse
import json
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

# Com `python3 -I` o diretorio do script nao entra no sys.path: adiciona so o do proprio programa.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import botoes  # noqa: E402
import coletores  # noqa: E402
import comandos  # noqa: E402
import render  # noqa: E402
import render_png  # noqa: E402
import servicos  # noqa: E402

PORTA_PADRAO = 8765
COLUNAS_PADRAO = 38
COLUNAS_MIN, COLUNAS_MAX = 20, 120
LARGURA_PADRAO, ALTURA_PADRAO = 1236, 1648  # Kindle Paperwhite 5
LARGURA_MIN, LARGURA_MAX = 800, 3000
ALTURA_MIN, ALTURA_MAX = 1300, 4000
ENDERECOS_PROIBIDOS = ("0.0.0.0", "::", "")


# ------------------------------------------------------------------------ config

def carregar_config(caminho):
    """Config padrao + arquivo JSON opcional. Chaves iniciadas por '_' sao comentarios."""
    cfg = {
        "host": socket.gethostname(),
        "discos": [],
        "servicos": [],
        "servicos_kindle": [],
        "balanceador": coletores.BALANCEADOR_PADRAO,
        "pares": [],
        "intervalo_cpu_s": 0.5,
        "cache_cpu_s": coletores.CACHE_CPU_PADRAO,
        "io": {"discos": [], "redes": []},
        "intervalo_io_s": coletores.INTERVALO_IO_PADRAO,
        "portas": [],
        "intervalo_historico_s": coletores.INTERVALO_HISTORICO_PADRAO,
        "comandos": {},
    }
    if caminho:
        with open(caminho, "r", encoding="utf-8") as f:
            lido = json.load(f)
        if not isinstance(lido, dict):
            raise ValueError("config: a raiz deve ser um objeto JSON")
        cfg.update({k: v for k, v in lido.items() if not str(k).startswith("_")})
    _validar(cfg)
    return cfg


def _validar(cfg):
    if not isinstance(cfg["host"], str) or not cfg["host"]:
        raise ValueError("config: host deve ser texto")
    if not isinstance(cfg["discos"], list) or not all(
        isinstance(d, dict) and (isinstance(d.get("caminho"), str) and d["caminho"]) != (
            isinstance(d.get("tier_state"), str) and bool(d["tier_state"]))
        and ("caminho" not in d or isinstance(d["caminho"], str))
        and ("tier_state" not in d or isinstance(d["tier_state"], str))
        and ("tier_state" not in d or "caminho" not in d)
        for d in cfg["discos"]
    ):
        raise ValueError("config: discos deve ser lista de {rotulo, caminho} ou {rotulo, tier_state}")
    if not isinstance(cfg["servicos"], list) or not all(isinstance(s, str) for s in cfg["servicos"]):
        raise ValueError("config: servicos deve ser lista de nomes")
    if cfg["balanceador"] is not None and not isinstance(cfg["balanceador"], str):
        raise ValueError("config: balanceador deve ser caminho ou null")
    if not isinstance(cfg["pares"], list) or not all(
        isinstance(p, dict) and isinstance(p.get("nome"), str) and isinstance(p.get("url"), str)
        for p in cfg["pares"]
    ):
        raise ValueError("config: pares deve ser lista de {nome, url}")
    i = cfg["intervalo_cpu_s"]
    if isinstance(i, bool) or not isinstance(i, (int, float)) or not 0 < i <= 5:
        raise ValueError("config: intervalo_cpu_s deve estar entre 0 e 5")
    c = cfg["cache_cpu_s"]
    if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 60:
        raise ValueError("config: cache_cpu_s deve estar entre 0 e 60")
    i = cfg["intervalo_io_s"]
    if isinstance(i, bool) or not isinstance(i, (int, float)) or not 0 < i <= 5:
        raise ValueError("config: intervalo_io_s deve estar entre 0 e 5")
    cfg["io"] = coletores.validar_io(cfg["io"])  # ValueError com a causa
    if not isinstance(cfg["portas"], list):
        raise ValueError("config: portas deve ser lista de {rotulo, host, porta}")
    for p in cfg["portas"]:
        coletores.validar_porta(p)  # ValueError com a causa
    h = cfg["intervalo_historico_s"]
    if isinstance(h, bool) or not isinstance(h, (int, float)) or not 0 < h <= 3600:
        raise ValueError("config: intervalo_historico_s deve estar entre 0 e 3600")
    cfg["comandos"] = comandos.validar_config(cfg["comandos"])  # ValueError com a causa
    cfg["servicos_kindle"] = servicos.validar_catalogo(cfg["servicos_kindle"])  # ValueError com a causa


# ---------------------------------------------------------------------- servidor

def _parametros(query):
    """(pagina, armado) da query string; valor invalido (ou ausente) vira o padrao, nunca excecao."""
    try:
        q = parse_qs(query, keep_blank_values=True, errors="replace")
    except Exception:
        q = {}
    pagina = botoes.pagina_valida(q.get("pagina", [""])[0])
    armado = botoes.armado_valido(q.get("armado", [""])[0]) if pagina == "comandos" else None
    return pagina, armado


class Handler(BaseHTTPRequestHandler):
    server_version = "kindle-monitor"
    protocol_version = "HTTP/1.0"
    timeout = 10  # segundos: cliente lento nao prende a thread (leitura de cabecalho e corpo)

    def _responder(self, status, corpo, tipo="text/plain; charset=utf-8", extra=None):
        dados = corpo if isinstance(corpo, bytes) else corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(dados)

    def do_GET(self):
        url = urlsplit(self.path)
        try:
            if url.path == "/saude":
                self._responder(200, "ok")
            elif url.path == "/tela.txt":
                m = self.server.coletor.coletar(com_pares=True)
                pagina, _ = _parametros(url.query)
                linhas = render.render_texto(m, self.server.colunas, pagina)
                self._responder(200, "\n".join(linhas) + "\n")
            elif url.path == "/tela.png":
                m = self.server.coletor.coletar(com_pares=True)
                pagina, armado = _parametros(url.query)
                if pagina == "comandos":
                    m = dict(m, comandos=self.server.comandos.ultimos())
                png = render_png.render_png(m, m.get("historico"), self.server.largura, self.server.altura,
                                            pagina, armado)
                self._responder(200, png, "image/png")
            elif url.path == "/botoes.json":
                pagina, armado = _parametros(url.query)
                corpo = {"largura": self.server.largura, "altura": self.server.altura, "pagina": pagina,
                         "botoes": botoes.layout(pagina, armado, self.server.largura, self.server.altura)}
                self._responder(200, json.dumps(corpo, ensure_ascii=True), "application/json; charset=utf-8")
            elif url.path == "/botoes.txt":
                # same layout as /botoes.json, one "id tipo x y w h" per line, for the Kindle's busybox awk
                pagina, armado = _parametros(url.query)
                linhas = ["%s %s %d %d %d %d" % (b["id"], b["tipo"], b["x"], b["y"], b["w"], b["h"])
                          for b in botoes.layout(pagina, armado, self.server.largura, self.server.altura)]
                self._responder(200, "\n".join(linhas) + "\n")
            elif url.path == "/historico.json":
                h = self.server.coletor.historico()
                self._responder(200, json.dumps(h, ensure_ascii=True), "application/json; charset=utf-8")
            elif url.path == "/metricas.json":
                com_pares = parse_qs(url.query).get("pares", ["1"])[0] != "0"
                m = self.server.coletor.coletar(com_pares=com_pares)
                m["comandos"] = self.server.comandos.ultimos()
                self._responder(200, json.dumps(m, ensure_ascii=True), "application/json; charset=utf-8")
            elif url.path == "/comando/estado":
                self._responder(200, json.dumps(self.server.comandos.ultimos()), "application/json; charset=utf-8")
            else:
                self._responder(404, "nao encontrado\n")
        except Exception:
            # Nunca vaza detalhes da excecao para o cliente.
            self._responder(500, "erro interno\n")

    def _nao_permitido(self):
        self._responder(405, "metodo nao permitido\n", extra={"Allow": "GET"})

    def do_POST(self):
        if urlsplit(self.path).path != "/comando":
            return self._nao_permitido()
        try:
            tam = int(self.headers.get("Content-Length", ""))
        except ValueError:
            tam = None
        status, corpo, extra = self.server.comandos.processar(
            self.client_address[0], self.headers.get("X-Kindle-Token"),
            self.headers.get("Content-Type"), tam, self.rfile)
        self._responder(status, json.dumps(corpo), "application/json; charset=utf-8", extra)

    do_PUT = do_DELETE = do_PATCH = do_HEAD = do_OPTIONS = _nao_permitido

    def log_message(self, formato, *args):
        if self.server.log:
            super().log_message(formato, *args)


class Servidor(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco, coletor, colunas, log, largura=LARGURA_PADRAO, altura=ALTURA_PADRAO,
                 comandos_obj=None):
        if ":" in endereco[0]:
            self.address_family = socket.AF_INET6
        self.coletor = coletor
        self.colunas = colunas
        self.largura = largura
        self.altura = altura
        self.log = log
        self.comandos = comandos_obj or comandos.Comandos(comandos.validar_config({}))
        super().__init__(endereco, Handler)


def criar_servidor(bind, porta, coletor, colunas=COLUNAS_PADRAO, log=True,
                   largura=LARGURA_PADRAO, altura=ALTURA_PADRAO, comandos=None):
    return Servidor((bind, porta), coletor, colunas, log, largura, altura, comandos)


# --------------------------------------------------------------------------- CLI

def _colunas(valor):
    n = int(valor)
    if not COLUNAS_MIN <= n <= COLUNAS_MAX:
        raise argparse.ArgumentTypeError("deve estar entre %d e %d" % (COLUNAS_MIN, COLUNAS_MAX))
    return n


def _intervalo(minimo, maximo):
    def conv(valor):
        n = int(valor)
        if not minimo <= n <= maximo:
            raise argparse.ArgumentTypeError("deve estar entre %d e %d" % (minimo, maximo))
        return n
    return conv


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Servidor de metricas para o Kindle (somente leitura).")
    p.add_argument("--bind", default="127.0.0.1",
                   help="endereco onde escutar (padrao 127.0.0.1; use o IP da LAN/tailnet, nunca 0.0.0.0)")
    p.add_argument("--porta", type=int, default=PORTA_PADRAO)
    p.add_argument("--config", default=None, help="caminho do config.json (ver config.exemplo.json)")
    p.add_argument("--colunas", type=_colunas, default=COLUNAS_PADRAO)
    p.add_argument("--largura", type=_intervalo(LARGURA_MIN, LARGURA_MAX), default=LARGURA_PADRAO,
                   help="largura do /tela.png em px (padrao 1236, Kindle Paperwhite 5)")
    p.add_argument("--altura", type=_intervalo(ALTURA_MIN, ALTURA_MAX), default=ALTURA_PADRAO,
                   help="altura do /tela.png em px (padrao 1648)")
    args = p.parse_args(argv)
    if args.bind.strip() in ENDERECOS_PROIBIDOS:
        p.error("nao escute em 0.0.0.0/::: passe o IP da LAN/tailnet em --bind")
    if not 0 <= args.porta <= 65535:
        p.error("--porta fora de 0..65535")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        cfg = carregar_config(args.config)
    except (OSError, ValueError) as e:
        print("erro na config: %s" % e, file=sys.stderr)
        return 2
    coletor = coletores.Coletor(cfg)
    coletor.iniciar_historico()
    srv = criar_servidor(args.bind, args.porta, coletor, args.colunas, largura=args.largura, altura=args.altura,
                         comandos=comandos.Comandos(cfg["comandos"], catalogo=cfg["servicos_kindle"]))
    print("kindle-monitor em http://%s:%d (host %s)" % (args.bind, srv.server_address[1], cfg["host"]),
          file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        coletor.parar()
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
