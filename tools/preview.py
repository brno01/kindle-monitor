#!/usr/bin/env python3
"""Gera um PNG de pre-visualizacao da tela do Kindle, para conferir o resultado olhando a imagem.

Uso (so biblioteca padrao):
    python3 -I tools/preview.py --saida /tmp/resumo.png                        # dados que imitam o atheron real
    python3 -I tools/preview.py --saida /tmp/s2.png --pagina servicos --p 2
    python3 -I tools/preview.py --saida /tmp/a.png --pagina servicos --armado svc:ai-agent:reiniciar
    python3 -I tools/preview.py --saida /tmp/cheia.png --cheia                 # 52 servicos, varios em falha, 8 comandos
    python3 -I tools/preview.py --saida /tmp/x.png --porta 8765 --pagina servicos --p 2   # baixa de um servidor
"""
import argparse
import json
import os
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "server"))

import coletores  # noqa: E402
import render_png  # noqa: E402
import servicos  # noqa: E402

AGORA = 1_794_000_000.0  # fixo: a previa nao depende do relogio

PARADOS = ("ai-coder", "cloudflare-gateway", "microservices-old", "onion-gw", "ro-client-build")


def catalogo(cheia=False):
    with open(os.path.join(RAIZ, "deploy", "config.atheron.json"), encoding="utf-8") as f:
        cat = servicos.validar_catalogo(json.load(f)["servicos_kindle"])
    if cheia:  # 52 servicos: 4 sinteticos a mais
        for n in range(4):
            cat.append({"id": "extra-%d" % n, "rotulo": "Servico extra %d" % n, "grupo": "docker", "tipo": "docker",
                        "alvo": "extra-%d" % n, "verbos": ["reiniciar", "ligar", "parar"], "protegido": False,
                        "opcional": False, "prefixo": False})
    return cat


def inventario(cat, cheia=False):
    est = {}
    for c in cat:
        e, d = ("parado", "stopped") if c["id"] in PARADOS else ("ativo", "running")
        est[c["id"]] = {"estado": e, "detalhe": d}
    est["dokploy"] = {"estado": "ativo", "detalhe": "2/2"}
    est["wud"] = {"estado": "falha", "detalhe": "restarting"}
    est["vaultwarden"] = {"estado": "desconhecido", "detalhe": "nao encontrado"}
    if cheia:
        for k in ("cerberus-ro-brain", "smbd", "ai-webui", "n8n-redis", "rathena-char", "extra-1"):
            est[k] = {"estado": "falha", "detalhe": "failed"}
        for k in ("pihole-link", "cerberus-syncthing"):
            est[k] = {"estado": "parado", "detalhe": "dead"}
    return json.dumps({"gerado": AGORA - 3, "servicos": est})


def exemplo(cheia=False):
    cat = catalogo(cheia)
    gib = 1024 ** 3
    m = {
        "host": "atheron",
        "gerado_em": "2026-11-16T14:32:10-03:00",
        "cpu": {"pct": 14.0},
        "carga": {"1m": 0.52, "5m": 0.48, "15m": 0.4},
        "ram": {"total_kb": int(19.4 * 1024 * 1024), "usado_kb": int(7.4 * 1024 * 1024), "pct": 38.1},
        "swap": {"total_kb": 8 * 1024 * 1024, "usado_kb": 300 * 1024, "pct": 3.7},
        "uptime": {"segundos": 90061},
        "temp_cpu": {"c": 52.0},
        "gpu": {"util_pct": 0, "mem_usada_mb": 0, "mem_total_mb": 8192, "temp_c": 39},
        "discos": [
            {"rotulo": "/", "total_b": 42 * 10 ** 9, "usado_b": 33 * 10 ** 9, "pct": 78.6},
            {"rotulo": "NAS HD", "total_b": 932 * 10 ** 9, "usado_b": 373 * 10 ** 9, "pct": 40.0},
            {"rotulo": "NAS SSD", "total_b": 256 * 10 ** 9, "usado_b": 200 * 10 ** 9, "pct": 78.1},
            {"rotulo": "SSD", "total_b": 914 * 10 ** 9, "usado_b": 507 * 10 ** 9, "pct": 55.5},
        ],
        "ragnarok": {"jogadores": 0, "parado": False, "idade_s": 4},
        "portas": [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True},
                   {"rotulo": "MAP", "aberto": True}],
        "io": {"discos": [{"rotulo": "NVMe", "leitura_bps": 120 * 1024, "escrita_bps": 48 * 1024},
                          {"rotulo": "HD", "leitura_bps": 0, "escrita_bps": 12 * 1024}],
               "redes": [{"rotulo": "LAN", "rx_bps": 22 * 1024, "tx_bps": 8 * 1024},
                         {"rotulo": "Tailnet", "rx_bps": 3 * 1024, "tx_bps": 1024}]},
        "servicos_kindle": coletores.montar_servicos_kindle(cat, inventario(cat, cheia), AGORA),
        "pares": [],
    }
    n = 60
    hist = {
        "cpu": [min(100, max(3, 18 + 14 * ((i * 37) % 17 - 8) / 8.0 + (i % 7))) for i in range(n)],
        "ram": [36 + i * 0.04 + (i % 5) * 0.4 for i in range(n)],
        "gpu": [0 for _ in range(n)],
    }
    cmds = [{"acao": "svc:ai-agent:reiniciar", "estado": "ok", "quando": "14:31:02", "detalhe": "concluido"},
            {"acao": "gpu-descarregar", "estado": "ok", "quando": "14:30:40", "detalhe": "nenhum modelo carregado"},
            {"acao": "svc:glances-link:parar", "estado": "falhou", "quando": "14:20:11", "detalhe": "codigo de saida 1"}]
    if cheia:
        cmds = (cmds + [{"acao": "svc:ollama-gpu:reiniciar", "estado": "falhou", "quando": "14:10:00",
                         "detalhe": "atualizacao automatica em andamento"},
                        {"acao": "bots-pausar", "estado": "executando", "quando": "14:09:00", "detalhe": ""}]) * 2
        cmds = cmds[:8]
        m["pares"] = [{"nome": "nomad", "ok": True, "metricas": {
            "host": "nomad", "cpu": {"pct": 23.0}, "ram": {"pct": 64.0}, "uptime": {"segundos": 4000},
            "temp_cpu": {"c": 49.0}}}]
        m["gpu"] = {"util_pct": 61, "mem_usada_mb": 5300, "mem_total_mb": 8192, "temp_c": 71}
        hist["gpu"] = [(i * 13) % 80 for i in range(n)]
    m["comandos"] = cmds
    return m, hist


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--saida", required=True, help="arquivo PNG de saida")
    p.add_argument("--porta", type=int, default=None, help="busca /tela.png do servidor local nessa porta")
    p.add_argument("--cheia", action="store_true", help="52 servicos, varios em falha, 8 comandos recentes")
    p.add_argument("--pagina", default="resumo", choices=("resumo", "servicos", "detalhes", "comandos"))
    p.add_argument("--p", type=int, default=1, help="pagina da lista (so em servicos)")
    p.add_argument("--armado", default=None, help="id do botao armado (acao rapida ou svc:<id>:<verbo>)")
    p.add_argument("--largura", type=int, default=1236)
    p.add_argument("--altura", type=int, default=1648)
    args = p.parse_args(argv)
    if args.porta:
        url = "http://127.0.0.1:%d/tela.png?pagina=%s&p=%d%s" % (
            args.porta, args.pagina, args.p, "&armado=" + args.armado if args.armado else "")
        with urllib.request.urlopen(url, timeout=10) as r:
            dados = r.read()
    else:
        m, hist = exemplo(args.cheia)
        dados = render_png.render_png(m, hist, args.largura, args.altura, args.pagina, args.armado, args.p)
    with open(args.saida, "wb") as f:
        f.write(dados)
    print("%s: %d bytes" % (args.saida, len(dados)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
