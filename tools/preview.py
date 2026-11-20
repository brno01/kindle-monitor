#!/usr/bin/env python3
"""Gera um PNG de pre-visualizacao da tela do Kindle, para conferir o resultado olhando a imagem.

Uso (so biblioteca padrao):
    python3 -I tools/preview.py --saida /tmp/resumo.png                        # dados que imitam o atheron real
    python3 -I tools/preview.py --saida /tmp/s2.png --pagina servicos --p 2
    python3 -I tools/preview.py --saida /tmp/a.png --pagina servicos --armado svc:ai-agent:reiniciar
    python3 -I tools/preview.py --saida /tmp/cheia.png --cheia                 # 52 servicos, varios em falha, 8 comandos
    python3 -I tools/preview.py --saida /tmp/a.png --estado alertas            # disco 91 %, 2 servicos em falha, bateria 12 %
    python3 -I tools/preview.py --saida /tmp/v.png --estado velho              # inventario e limites do Claude velhos
    python3 -I tools/preview.py --saida /tmp/j.png --pagina jogos              # pagina Jogos (sem aba): Ragnarok + 4 instancias do AMP
    python3 -I tools/preview.py --todas /tmp/prev                               # <pagina>-<estado>.png, 7 paginas x 3 estados
    python3 -I tools/preview.py --saida /tmp/x.png --porta 8765 --pagina servicos --p 2   # baixa de um servidor
"""
import argparse
import json
import os
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "server"))

import alertas  # noqa: E402
import botoes  # noqa: E402
import coletores  # noqa: E402
import render_png  # noqa: E402
import servicos  # noqa: E402

AGORA = 1_794_000_000.0  # fixo: a previa nao depende do relogio

ESTADOS = ("ok", "alertas", "velho")

PARADOS = ("ai-coder", "cloudflare-gateway", "microservices-old", "onion-gw", "ro-client-build")


def catalogo(cheia=False):
    with open(os.path.join(RAIZ, "deploy", "config.atheron.example.json"), encoding="utf-8") as f:
        cat = servicos.validar_catalogo(json.load(f)["servicos_kindle"])
    if cheia:  # 52 servicos: 4 sinteticos a mais
        for n in range(4):
            cat.append({"id": "extra-%d" % n, "rotulo": "Servico extra %d" % n, "grupo": "docker", "tipo": "docker",
                        "alvo": "extra-%d" % n, "verbos": ["reiniciar", "ligar", "parar"], "protegido": False,
                        "opcional": False, "prefixo": False})
    return cat


def inventario(cat, cheia=False, estado="ok"):
    est = {}
    for c in cat:
        e, d = ("parado", "stopped") if c["id"] in PARADOS else ("ativo", "running")
        est[c["id"]] = {"estado": e, "detalhe": d}
    est["dokploy"] = {"estado": "ativo", "detalhe": "2/2"}
    if estado == "alertas":
        est["wud"] = {"estado": "falha", "detalhe": "restarting"}
        est["vaultwarden"] = {"estado": "falha", "detalhe": "failed"}
    else:
        est["wud"] = {"estado": "ativo", "detalhe": "running"}
        est["vaultwarden"] = {"estado": "desconhecido", "detalhe": "nao encontrado"}
    if cheia:
        for k in ("cerberus-ro-brain", "smbd", "ai-webui", "n8n-redis", "rathena-char", "extra-1"):
            est[k] = {"estado": "falha", "detalhe": "failed"}
        for k in ("pihole-link", "cerberus-syncthing"):
            est[k] = {"estado": "parado", "detalhe": "dead"}
    return json.dumps({"gerado": AGORA - (120 if estado == "velho" else 3), "servicos": est})


def kindle_exemplo(estado="ok"):
    """Vista de kindle_status (o que o render recebe em `kindle`); bateria baixa so em `alertas`."""
    bateria, carregando = (12, False) if estado == "alertas" else (86, False)
    return {"bateria": bateria, "carregando": carregando, "temp_c": 29, "autonomia": "2 d 4 h", "wifi": 3,
            "wifi_ok": True, "aviao": False, "bt": False, "bt_conectados": 0, "tailscale": "direto",
            "latencia": "38 ms", "falhas": 0, "relogio": None, "whispersync": None}


def exemplo(cheia=False, estado="ok"):
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
            {"rotulo": "/", "caminho": "/", "total_b": 42 * 10 ** 9, "usado_b": 33 * 10 ** 9, "pct": 78.6},
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
        "servicos_kindle": coletores.montar_servicos_kindle(cat, inventario(cat, cheia, estado), AGORA),
        "pares": [],
        # janela semanal a 62 % e a de 5 h recem-renovada; o S10 com um caminho fora e um desconhecido
        "claude": {"limites": {"cinco_horas": {"pct": 34.0, "volta_em": int(AGORA) + 3 * 3600, "renovado": True},
                               "semanal": {"pct": 62.0, "volta_em": int(AGORA) + 3 * 86400, "renovado": False},
                               "idade_s": 45, "velho": False},
                   "tokens": {"hoje": {"entrada": 410_000, "saida": 160_000, "cache_leitura": 2_300_000,
                                       "cache_escrita": 230_000, "total": 3_100_000, "custo_usd": 4.87},
                              "sete_dias": {"entrada": 2_900_000, "saida": 1_100_000, "cache_leitura": 16_000_000,
                                            "cache_escrita": 1_000_000, "total": 21_000_000, "custo_usd": 31.4},
                              "idade_s": 45, "velho": False}},
        "s10": {"bateria": {"nivel": 87, "status": "charging", "temperatura_c": 36.5, "saude": "good"},
                "caminhos": {"usb": True, "adb_sem_fio": False, "tailscale": True, "ssh_termux": True, "vnc": None},
                "avisos": ["temperatura"], "idade_s": 20, "velho": False},
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
    # painel de jogos: o AMP com 4 instancias (2 rodando, 1 iniciando, 1 parada); em `alertas` a porta MAP do Ragnarok
    # fecha; em `velho` o AMP esta ligado mas sem dados (inventario velho)
    if estado == "velho":
        m["amp"] = {"ativo": True, "inventario": "velho", "idade_s": 300, "erro": None, "instancias": []}
    else:
        m["amp"] = {"ativo": True, "inventario": "ok", "idade_s": 6, "erro": None, "instancias": [
            {"id": "5e1f0a21", "nome": "Minecraft", "modulo": "Minecraft", "estado": "rodando", "jogadores": 2, "max": 20},
            {"id": "b7c3d9e4", "nome": "Terraria", "modulo": "Terraria", "estado": "rodando", "jogadores": 0, "max": 8},
            {"id": "09a8f6c2", "nome": "Palworld", "modulo": "Palworld", "estado": "iniciando", "jogadores": None,
             "max": None},
            {"id": "c4d2e7b1", "nome": "Valheim", "modulo": "Valheim", "estado": "parado", "jogadores": None, "max": None},
        ]}
    if estado == "alertas":
        m["portas"][2]["aberto"] = False
        total = 63 * 1024 ** 3
        m["discos"][0].update({"total_b": total, "usado_b": total - int(5.7 * 1024 ** 3), "pct": 91.0})  # 5,7 GB livres
    elif estado == "velho":
        for k in ("limites", "tokens"):
            m["claude"][k]["idade_s"] = 900
            m["claude"][k]["velho"] = True
    em_alerta, velho = estado == "alertas", estado == "velho"
    m["aparelhos"] = {"inventario": "velho" if velho else "ok", "idade_s": 120 if velho else 4, "itens": [
        {"id": "notebook", "rotulo": "Notebook", "icone": "notebook", "online": True, "offline_min": None,
         "conexao": "direto", "alerta_offline_min": None},
        {"id": "s22", "rotulo": "S22", "icone": "celular", "online": True, "offline_min": None,
         "conexao": "relay", "alerta_offline_min": None},
        {"id": "s10", "rotulo": "S10", "icone": "celular", "online": True, "offline_min": None,
         "conexao": "direto", "alerta_offline_min": None},
        {"id": "iphone", "rotulo": "iPhone", "icone": "celular", "online": True, "offline_min": None,
         "conexao": "relay", "alerta_offline_min": None},
        {"id": "kindle", "rotulo": "Kindle", "icone": "leitor", "online": True, "offline_min": None,
         "conexao": "direto", "alerta_offline_min": None},
        {"id": "gateway", "rotulo": "Gateway", "icone": "rede", "online": not em_alerta,
         "offline_min": 95 if em_alerta else None, "conexao": None if em_alerta else "direto",
         "alerta_offline_min": 10},
        {"id": "games", "rotulo": "Games", "icone": "jogo", "online": False, "offline_min": 95,
         "conexao": None, "alerta_offline_min": None},
    ]}
    ult_cerebro = 112320 if em_alerta else 32400  # 31,2 h (atrasada, max 24 h) ou 9 h
    m["rotinas"] = {"inventario": "velho" if velho else "ok", "idade_s": 120 if velho else 4, "itens": [
        {"id": "backup-senhas", "rotulo": "Backup senhas", "resultado": "ok", "ultima_em": int(AGORA) - 19800,
         "idade_h": 5.5, "max_idade_h": 26, "atrasada": False},
        {"id": "sync-cofre", "rotulo": "Sync cofre", "resultado": "ok", "ultima_em": int(AGORA) - 1440,
         "idade_h": 0.4, "max_idade_h": 2, "atrasada": False},
        {"id": "segundo-cerebro", "rotulo": "Segundo cerebro", "resultado": "ok",
         "ultima_em": int(AGORA) - ult_cerebro, "idade_h": ult_cerebro / 3600, "max_idade_h": 24,
         "atrasada": em_alerta},
        {"id": "tokens-claude", "rotulo": "Tokens Claude", "resultado": "ok", "ultima_em": int(AGORA) - 720,
         "idade_h": 0.2, "max_idade_h": 1, "atrasada": False},
    ], "unidades_falhas": {"n": 1 if em_alerta else 0,
                           "nomes": ["rclone-nas-sync.service"] if em_alerta else []}}
    m["claude"]["sessoes"] = {"itens": [
        {"projeto": "kindle-monitor", "estado": "esperando" if em_alerta else "trabalhando",
         "desde_s": 1500 if em_alerta else 240},
        {"projeto": "dotfiles", "estado": "trabalhando", "desde_s": 60},
        {"projeto": "cerberus", "estado": "aberta", "desde_s": 7200},
    ], "total": 3, "esperando": 1 if em_alerta else 0, "idade_s": 12}
    def pr(repo, n, titulo, ci, revisao="nenhuma", conflito=False, idade=1, atualizado=0, rascunho=False):
        return {"repo": repo, "numero": n, "titulo": titulo, "rascunho": rascunho, "ci": ci, "revisao": revisao,
                "conflito": conflito, "idade_d": idade, "atualizado_d": atualizado}
    m["github"] = {"prs": [
        pr("kindle-monitor", 14, "Painel do ecossistema", "ok", "aprovado", False, 4, 0),
        pr("dotfiles", 7, "Roteamento de modelos", "pendente", rascunho=True, idade=9, atualizado=2),
        pr("cerberus", 31, "Chatter dos bots com banco de frases", "falha" if em_alerta else "ok", "mudancas",
           False, 12, 3),
        pr("dotfiles", 8, "Seleção do ECC por máquina", "ok", "pendente", em_alerta, 2, 1),
        pr("galaxy-s10", 3, "Vigia do S10 sem tela", "ok", "nenhuma", False, 21, 9),
        pr("kindle-monitor", 15, "Painel de jogos e AMP", "ok", "pendente", False, 1, 0),
        pr("vaultwarden", 2, "Backup às 03:10 com verificação", None, "aprovado", False, 45, 30),
    ], "ci": [
        {"repo": "kindle-monitor", "branch": "feat/painel-ecossistema", "estado": "ok"},
        {"repo": "dotfiles", "branch": "main", "estado": "ok"},
        {"repo": "cerberus", "branch": "main", "estado": "falha" if em_alerta else "ok"},
    ], "issues": {"n": 6, "itens": [
        {"repo": "kindle-monitor", "numero": 9, "titulo": "Tela branca depois de parar a interface", "idade_d": 2},
        {"repo": "cerberus", "numero": 22, "titulo": "Bot trava no mapa de Prontera", "idade_d": 11},
        {"repo": "dotfiles", "numero": 5, "titulo": "claude-uso-painel sem timer", "idade_d": 30},
        {"repo": "galaxy-s10", "numero": 1, "titulo": "Tailscale SSH ignora authorized_keys", "idade_d": 120},
    ]}, "repos": [
        {"repo": "kindle-monitor", "push_d": 0}, {"repo": "dotfiles", "push_d": 0}, {"repo": "cerberus", "push_d": 2},
        {"repo": "galaxy-s10", "push_d": 9}, {"repo": "vaultwarden", "push_d": 30},
        {"repo": "obsidian-cofre", "push_d": 61},
    ], "abertos": 7, "ci_falhas": 1 if em_alerta else 0, "idade_s": 30, "velho": False}
    return m, hist


def gerar(m, hist, args, pagina, armado, p, kindle):
    return render_png.render_png(m, hist, args.largura, args.altura, pagina, armado, p, args.modo, kindle)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--saida", default=None, help="arquivo PNG de saida")
    p.add_argument("--estado", default="ok", choices=ESTADOS, help="metricas de exemplo: ok, alertas ou velho")
    p.add_argument("--todas", default=None, metavar="DIR",
                   help="grava <pagina>-<estado>.png de todas as paginas nos tres estados em DIR")
    p.add_argument("--porta", type=int, default=None, help="busca /tela.png do servidor local nessa porta")
    p.add_argument("--cheia", action="store_true", help="52 servicos, varios em falha, 8 comandos recentes")
    p.add_argument("--pagina", default="resumo", choices=botoes.PAGINAS)
    p.add_argument("--p", type=int, default=1, help="pagina da lista (so em servicos)")
    p.add_argument("--modo", default=None, help="perfil de energia ativo (desempenho|balanceado|economia; pagina comandos)")
    p.add_argument("--armado", default=None, help="id do botao armado (acao rapida ou svc:<id>:<verbo>)")
    p.add_argument("--largura", type=int, default=1236)
    p.add_argument("--altura", type=int, default=1648)
    args = p.parse_args(argv)
    if args.todas:
        os.makedirs(args.todas, exist_ok=True)
        for estado in ESTADOS:
            m, hist = exemplo(args.cheia, estado)
            for pagina in botoes.PAGINAS:
                dados = gerar(m, hist, args, pagina, None, 1, kindle_exemplo(estado))
                caminho = os.path.join(args.todas, "%s-%s.png" % (pagina, estado))
                with open(caminho, "wb") as f:
                    f.write(dados)
                print("%s: %d bytes" % (caminho, len(dados)))
        return 0
    if not args.saida:
        p.error("--saida ou --todas e obrigatorio")
    if args.porta:
        url = "http://127.0.0.1:%d/tela.png?pagina=%s&p=%d%s" % (
            args.porta, args.pagina, args.p, "&armado=" + args.armado if args.armado else "")
        if args.modo:
            url += "&modo=" + args.modo
        with urllib.request.urlopen(url, timeout=10) as r:
            dados = r.read()
    else:
        m, hist = exemplo(args.cheia, args.estado)
        dados = gerar(m, hist, args, args.pagina, args.armado, args.p, kindle_exemplo(args.estado))
    with open(args.saida, "wb") as f:
        f.write(dados)
    print("%s: %d bytes" % (args.saida, len(dados)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
