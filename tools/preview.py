#!/usr/bin/env python3
"""Gera um PNG de pre-visualizacao da tela do Kindle, para conferir o resultado olhando a imagem.

Uso (so biblioteca padrao):
    python3 -I tools/preview.py --saida /tmp/preview.png                   # dados de exemplo
    python3 -I tools/preview.py --saida /tmp/preview.png --cheia           # 8 servicos e 3 discos
    python3 -I tools/preview.py --saida /tmp/preview.png --porta 8765      # baixa de http://127.0.0.1:8765/tela.png
"""
import argparse
import os
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "server"))

import render_png  # noqa: E402


def exemplo(cheia=False):
    discos = [
        {"rotulo": "/", "caminho": "/", "total_b": 500 * 10**9, "usado_b": 212 * 10**9, "pct": 42.4},
        {"rotulo": "NAS", "caminho": "/mnt/nas", "total_b": 14 * 10**12, "usado_b": 11 * 10**12, "pct": 78.6},
    ]
    servicos = [
        {"nome": "ragnarok.service", "ativo": True},
        {"nome": "cerberus-balancer.service", "ativo": True},
    ]
    if cheia:
        discos += [{"rotulo": "BACKUP", "caminho": "/mnt/bkp", "total_b": 8 * 10**12, "usado_b": 7 * 10**12,
                    "pct": 91.0}]
        servicos = [{"nome": n, "ativo": a} for n, a in (
            ("ragnarok.service", True), ("cerberus-balancer.service", False), ("cerberus-ro-account.service", True),
            ("tailscaled.service", True), ("smbd.service", True), ("docker.service", True),
            ("nvidia-persistenced.service", None), ("kindle-monitor.service", True))]
        for s in servicos:
            if s["ativo"] is None:
                del s["ativo"]
                s["erro"] = "n/d"
    m = {
        "host": "atheron",
        "gerado_em": "2026-11-15T14:32:10-03:00",
        "cpu": {"pct": 56.0},
        "carga": {"1m": 0.52, "5m": 0.48, "15m": 0.4},
        "ram": {"total_kb": 32_000_000, "usado_kb": 18_400_000, "pct": 57.5},
        "swap": {"total_kb": 8_000_000, "usado_kb": 1_000_000, "pct": 12.5},
        "uptime": {"segundos": 90061},
        "temp_cpu": {"c": 55.0},
        "gpu": {"util_pct": 12, "mem_usada_mb": 5300, "mem_total_mb": 8192, "temp_c": 47},
        "discos": discos,
        "servicos": servicos,
        "ragnarok": {"jogadores": 7, "parado": False, "idade_s": 4},
        "portas": [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True},
                   {"rotulo": "MAP", "aberto": False}],
        "pares": [{"nome": "nomad", "ok": True, "metricas": {
            "host": "nomad", "cpu": {"pct": 23.0}, "ram": {"pct": 64.0}, "gpu": {"util_pct": 4},
            "uptime": {"segundos": 4 * 3600 + 1200}, "temp_cpu": {"c": 49.0}}}],
    }
    n = 60
    hist = {
        "cpu": [min(100, max(3, 45 + 35 * ((i * 37) % 17 - 8) / 8.0 + (i % 7) * 2)) for i in range(n)],
        "ram": [52 + i * 0.09 + (i % 5) for i in range(n)],
        "gpu": [max(0, (i * 13) % 40 - 5) for i in range(n)],
    }
    return m, hist


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--saida", required=True, help="arquivo PNG de saida")
    p.add_argument("--porta", type=int, default=None, help="busca /tela.png do servidor local nessa porta")
    p.add_argument("--cheia", action="store_true", help="dados de exemplo com 8 servicos e 3 discos")
    p.add_argument("--largura", type=int, default=1236)
    p.add_argument("--altura", type=int, default=1648)
    args = p.parse_args(argv)
    if args.porta:
        with urllib.request.urlopen("http://127.0.0.1:%d/tela.png" % args.porta, timeout=10) as r:
            dados = r.read()
    else:
        m, hist = exemplo(args.cheia)
        dados = render_png.render_png(m, hist, args.largura, args.altura)
    with open(args.saida, "wb") as f:
        f.write(dados)
    print("%s: %d bytes" % (args.saida, len(dados)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
