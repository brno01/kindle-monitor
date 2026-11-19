#!/usr/bin/python3 -I
"""Executor root do kindle-monitor: cumpre os pedidos registrados pelo servidor web.

O servidor web (User=nobody) so grava arquivos vazios "<epoch_ns>-<acao>.req" no spool (para servicos,
"<epoch_ns>-svc--<id>--<verbo>.req"; o id e validado contra o catalogo "servicos_kindle" da config root-owned). Este programa
roda como root (kindle-monitor-executor.service, acionado pela .path), valida o NOME do arquivo, apaga o
pedido ANTES de executar (nunca repete), ignora o conteudo e procura o id numa tabela FIXA de acoes.
Nada do pedido entra em comando algum; nunca ha shell. Resultado em JSON no diretorio de estado.

Seguranca dos diretorios: /run/kindle-monitor, o spool e o status sao criados pelo tmpfiles.d (root). Aqui
cada um e aberto com O_DIRECTORY|O_NOFOLLOW e conferido com fstat (dono, permissoes); dai em diante tudo
usa dir_fd, nunca caminho, entao trocar um diretorio por symlink nao leva o root para fora. Se algo nao
bater, recusa tudo (excecao Recusa, saida 1). Se os diretorios nao existem, sai 0 sem criar nada.
Com --inventario, em vez de processar o spool, coleta o estado de todos os servicos do catalogo (em lote, sem
shell) e grava status/servicos.json para o web ler; com o catalogo "aparelhos" tambem le `tailscale status --json`
(saida tratada como dado nao confiavel; so id/online/visto_em/conexao sai) e grava status/aparelhos.json; com o
catalogo "rotinas" le `systemctl show` dos timers, o mtime dos arquivos (sem seguir symlink, sem ler conteudo) e
`systemctl list-units --failed`, e grava status/rotinas.json. Biblioteca padrao apenas.
"""
import argparse
import grp
import ipaddress
import json
import os
import re
import signal
import stat
import subprocess
import sys
import datetime
import hashlib
import time
import unicodedata
import urllib.error
import urllib.request

_stat = stat

ACOES = ("gpu-descarregar", "bots-pausar", "bots-retomar", "monitor-reiniciar")
GRUPOS = ("host", "incus", "docker", "ragnarok")
TIPOS = ("systemd", "incus", "docker", "rathena")
VERBOS = ("reiniciar", "ligar", "parar")
VERBO_CLI = {"reiniciar": "restart", "ligar": "start", "parar": "stop"}
INVENTARIO_ARQ = "servicos.json"
APARELHOS_ARQ = "aparelhos.json"
TIMEOUT_TAILSCALE = 10
TAILSCALE_MAX = 4 << 20   # bytes lidos de `tailscale status --json`; acima disso e erro
APARELHOS_MAX = 16
ROTINAS_ARQ = "rotinas.json"
ROTINAS_MAX = 16
TIMEOUT_ROTINAS = 10      # por comando (systemctl show; systemctl list-units)
ARQUIVO_ENTRADAS_MAX = 2000   # entradas diretas de um diretorio lidas para achar o maior mtime
FALHAS_NOMES_MAX = 5
FALHAS_N_MAX = 9999
SAIDA_ROTINAS_MAX = 1 << 20   # bytes de saida do systemctl considerados; o resto e ignorado
TIMEOUT_INVENTARIO = 10
TIMEOUT_INCUS = 90
TIMEOUT_EXEC = 60
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
TOKEN_ARQ = r"(?:svc--[a-z0-9-]{1,40}--(?:reiniciar|ligar|parar)|[a-z-]{3,32})"
RE_REQ = re.compile(r"^(\d{1,20})-(" + TOKEN_ARQ + r")\.req\Z")
RE_JSON = re.compile(r"^(\d{1,20})-" + TOKEN_ARQ + r"\.json\Z")
RE_SVC_ACAO = re.compile(r"^svc:([a-z0-9-]{1,40}):(reiniciar|ligar|parar)\Z")
RE_SVC_ARQ = re.compile(r"^svc--([a-z0-9-]{1,40})--(reiniciar|ligar|parar)\Z")
RE_ACAO_ARQ = re.compile(r"^[a-z-]{3,32}\Z")
RE_ID = re.compile(r"^[a-z0-9]([a-z0-9-]{0,38}[a-z0-9])?\Z")
RE_ALVO = re.compile(r"^[A-Za-z0-9_.@-]{1,64}\Z")
RE_APARELHO_ID = re.compile(r"^[a-z0-9-]{1,24}\Z")
RE_APARELHO_NOME = re.compile(r"^[a-z0-9-]{1,63}\Z")
RE_APARELHO_ICONE = re.compile(r"^[a-z]{2,16}\Z")
CHAVES_APARELHO = {"id", "nome", "rotulo", "icone", "alerta_offline_min"}
RE_ROTINA_ID = re.compile(r"^[a-z0-9-]{1,24}\Z")
RE_ROTINA_ALVO_TIMER = re.compile(r"^[A-Za-z0-9_.@-]{1,64}\.service\Z")
RE_UNIDADE_FALHA = re.compile(r"^[A-Za-z0-9_.@:-]{1,40}\Z")
RE_RESULTADO_UNIT = re.compile(r"^[a-z-]{1,24}\Z")
PREFIXOS_ARQUIVO = ("/srv/", "/var/lib/", "/var/backups/")
NEGADOS_ARQUIVO = ("/var/lib/claude-uso",)  # fonte do painel, nao e alvo de rotina (o web ja le por outro caminho)
CHAVES_ROTINA = {"id", "rotulo", "tipo", "alvo", "max_idade_h"}
RE_PROJETO = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}\Z")
CHAVES_CATALOGO = {"id", "rotulo", "grupo", "tipo", "alvo", "projeto", "prefixo", "verbos", "protegido", "opcional"}
RE_BOT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}\Z")  # nunca comeca com "-" (viraria opcao)
# Painel de jogos (AMP): chave `amp` da config e arquivo status/jogos.json. A senha do AMP nunca sai do arquivo de
# credenciais para nada que nao seja o corpo do POST de login (log, argv, JSON, excecao e tela nunca a veem).
JOGOS_ARQ = "jogos.json"
JOGOS_MAX = 16
AMP_DIR_CREDENCIAIS = "/etc/kindle-monitor/"
RE_AMP_URL = re.compile(r"^http://([0-9]{1,3}(?:\.[0-9]{1,3}){3}):([1-9][0-9]{0,4})/?\Z")
RE_AMP_CREDENCIAIS = re.compile(r"^/etc/kindle-monitor/[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
CHAVES_AMP = {"url", "credenciais"}
REDES_AMP = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "192.168.0.0/16", "100.64.0.0/10"))
AMP_TIMEOUT_S = 8         # por chamada (login, GetInstanceStatuses, GetInstance, logout)
# Prazo total da parte do AMP (login, lista e os GetInstance), contado desde o inicio do login: um GetInstance so comeca
# antes dele e leva no maximo o que resta (ate AMP_TIMEOUT_S); passou do prazo, as instancias que faltam saem como se o
# GetInstance tivesse falhado. Pior caso do coletor: AMP_PRAZO_S + AMP_TIMEOUT_S ate o logout, mais 2 * AMP_TIMEOUT_S
# dele (cada chamada dura no maximo dois recebimentos); a conta inteira esta na unit do inventario e em UnidadeTest.
AMP_PRAZO_S = 40
AMP_MAX_BYTES = 1 << 20   # resposta maior que isso e erro
# O inventario roda a cada ~15 s, mas o AMP so e consultado de novo quando o jogos.json tem AMP_REUSO_S s ou mais (evita
# um login a cada 15 s). Tem de ficar abaixo de ecossistema.INVENTARIO_VALIDADE_S (60) menos o intervalo do timer e a
# duracao de uma rodada: com 45 o arquivo chegaria a ~60 s e o web o chamaria de velho de tempos em tempos.
AMP_REUSO_S = 30
AMP_CREDENCIAL_MAX = 1024
AMP_USUARIO_MAX = 128
AMP_SENHA_MAX = 256
AMP_VALOR_MAX = 99999     # jogadores e vagas: acima disso o dado e lixo
RE_AMP_SESSAO = re.compile(r"^[A-Za-z0-9_-]{8,128}\Z")
RE_AMP_UUID = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\Z")
# `Running` = a instancia (o daemon) esta ligada; `AppState` = estado da aplicacao do jogo dentro dela. Running diferente
# de true ganha de tudo (parado: a instancia inteira desligada, o AppState -1 que o AMP da nela e ignorado). Com Running
# true: AppState 20 = rodando; 0 = parado (aplicacao parada); 250 = suspenso (conta como parado); 200 = falha; os
# transitorios (pre-inicio, configurando, iniciando, reiniciando, parando, dormindo, esperando, instalando,
# atualizando, aguardando o usuario, 100 e 300) = iniciando; o resto (inclusive -1, que e o do controlador ADS) = outro.
APPSTATE_ESTADO = dict([(20, "rodando"), (0, "parado"), (250, "parado"), (200, "falha")]
                       + [(n, "iniciando") for n in (5, 7, 10, 30, 40, 50, 60, 70, 80, 100, 300)])
AMP_MODULOS_ADS = ("ads", "adsmodule")  # a propria instancia do controlador (ADS) nao e um servidor de jogo
PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# `--` antes dos alvos: nome do catalogo que comece com "-" nunca vira opcao. LoadState distingue unit inexistente
# (o systemd devolve Result=success para ela); ExecMainStatus da o "exit N". --timestamp=unix da "@epoch".
SHOW_ROTINAS = ["systemctl", "show", "-p", "Id", "-p", "Result", "-p", "LoadState", "-p", "ExecMainStatus",
                "-p", "ExecMainExitTimestamp", "--timestamp=unix", "--"]
LISTA_FALHAS = ["systemctl", "list-units", "--failed", "--plain", "--no-legend", "--no-pager"]
TAILSCALE = ["tailscale", "status", "--json"]  # PATH fixo (PATH do executar_padrao), como systemctl/incus
INCUS = ["incus", "exec", "games", "--project", "core", "--"]
TIMER = "ro-bot-scheduler.timer"
# is-active e fail-open (oneshot sem RemainAfterExit fica "activating", rc 3): le o valor e so libera inactive/failed.
AUTOUPDATE = ["systemctl", "show", "-p", "ActiveState", "--value", "cerberus-autoupdate.service"]
AUTOUPDATE_LIVRE = ("inactive", "failed")
TIMEOUT_AUTOUPDATE = 10
PASSADA_ORCAMENTO_S = 400  # depois disso nao pega pedido novo; o resto fica no spool para o proximo disparo
COOLDOWN_LER_MAX = 65536
COOLDOWN_GUARDAR_S = max(COOLDOWN_S, VALIDADE_S)

# Tabela FIXA das acoes que sao so argv. As outras duas (gpu-descarregar, bots-pausar) tem funcao propria.
TABELA_ARGV = {
    "bots-retomar": [INCUS + ["systemctl", "start", TIMER]],
    "monitor-reiniciar": [["systemctl", "restart", "kindle-monitor.service"]],
}
# Recusadas enquanto a janela de atualizacao automatica roda.
BLOQUEADAS_NO_AUTOUPDATE = ()  # as acoes rapidas atuais nao precisam; servicos "protegido" sempre sao
INCUS_MICRO = ["incus", "exec", "microservices", "--project", "core", "--"]


class Falha(Exception):
    """Falha esperada; o texto vira o detalhe (ASCII, ate 80 chars). rc e o codigo de saida, se houver."""
    def __init__(self, msg, rc=1):
        super().__init__(msg)
        self.rc = rc


class AmpErro(Exception):
    """Falha do coletor do AMP. O texto e FIXO e curto (nunca vem do servidor nem da credencial): vai para o jogos.json."""


class CredencialInvalida(Exception):
    """Arquivo de credenciais do AMP existe mas nao serve. Sem detalhe: nao cita caminho, dono nem conteudo."""
    def __init__(self):
        super().__init__("credencial amp invalida")


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


def validar_catalogo(lista):
    """Valida `servicos_kindle` (mesmas regras de server/servicos.py; um teste confere). ValueError com a causa."""
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise ValueError("servicos_kindle deve ser uma lista")
    ids, saida = set(), []
    for i, it in enumerate(lista):
        r = "servicos_kindle[%d]" % i
        if not isinstance(it, dict):
            raise ValueError("%s deve ser um objeto" % r)
        if set(it) - CHAVES_CATALOGO:
            raise ValueError("%s: chave desconhecida" % r)
        sid = it.get("id")
        if not isinstance(sid, str) or not RE_ID.match(sid) or "--" in sid:
            raise ValueError("%s: id invalido" % r)
        if sid in ids:
            raise ValueError("%s: id repetido" % r)
        ids.add(sid)
        rot = it.get("rotulo")
        if not isinstance(rot, str) or not 1 <= len(rot) <= 28 or not all(32 <= ord(ch) < 127 for ch in rot):
            raise ValueError("%s: rotulo invalido" % r)
        if it.get("grupo") not in GRUPOS:
            raise ValueError("%s: grupo invalido" % r)
        tipo = it.get("tipo")
        if tipo not in TIPOS:
            raise ValueError("%s: tipo invalido" % r)
        alvo = it.get("alvo")
        if not isinstance(alvo, str) or not RE_ALVO.match(alvo) or alvo.startswith("-"):
            raise ValueError("%s: alvo invalido" % r)
        if tipo in ("systemd", "rathena") and not alvo.endswith(".service"):
            raise ValueError("%s: alvo de unit deve terminar em .service" % r)
        if "projeto" in it and tipo != "incus":
            raise ValueError("%s: projeto so vale para incus" % r)
        projeto = it.get("projeto", "core")
        if tipo == "incus" and (not isinstance(projeto, str) or not RE_PROJETO.match(projeto)):
            raise ValueError("%s: projeto invalido" % r)
        prefixo = it.get("prefixo", False)
        if not isinstance(prefixo, bool) or (prefixo and tipo != "docker"):
            raise ValueError("%s: prefixo so vale (booleano) para docker" % r)
        verbos = it.get("verbos")
        if not isinstance(verbos, list) or not all(isinstance(v, str) and v in VERBOS for v in verbos) or \
                len(set(verbos)) != len(verbos):
            raise ValueError("%s: verbos invalidos" % r)
        if prefixo and verbos:
            raise ValueError("%s: prefixo exige verbos []" % r)
        for k in ("protegido", "opcional"):
            if not isinstance(it.get(k, False), bool):
                raise ValueError("%s: %s deve ser booleano" % (r, k))
        n = {"id": sid, "rotulo": rot, "grupo": it["grupo"], "tipo": tipo, "alvo": alvo, "verbos": list(verbos),
             "protegido": it.get("protegido", False), "opcional": it.get("opcional", False), "prefixo": prefixo}
        if tipo == "incus":
            n["projeto"] = projeto
        saida.append(n)
    return saida


def validar_aparelhos(lista):
    """Valida `aparelhos` (E8; mesmas regras do web). ValueError com a causa; devolve copias novas.

    `icone` so tem o formato conferido aqui: o executor (-I, root) nao importa nada de server/, e a lista
    de icones vive la; o web descarta o aparelho cujo icone nao existe.
    """
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise ValueError("aparelhos deve ser uma lista")
    if len(lista) > APARELHOS_MAX:
        raise ValueError("aparelhos: no maximo %d itens" % APARELHOS_MAX)
    ids, nomes, saida = set(), set(), []
    for i, it in enumerate(lista):
        r = "aparelhos[%d]" % i
        if not isinstance(it, dict):
            raise ValueError("%s deve ser um objeto" % r)
        if set(it) - CHAVES_APARELHO:
            raise ValueError("%s: chave desconhecida" % r)
        aid, nome, rot, ico = it.get("id"), it.get("nome"), it.get("rotulo"), it.get("icone")
        if not isinstance(aid, str) or not RE_APARELHO_ID.match(aid):
            raise ValueError("%s: id invalido" % r)
        if not isinstance(nome, str) or not RE_APARELHO_NOME.match(nome) or "empresa-x" in nome.lower():
            raise ValueError("%s: nome invalido" % r)
        if not isinstance(rot, str) or not 1 <= len(rot) <= 16 or not rot.isascii() or not rot.isprintable():
            raise ValueError("%s: rotulo invalido" % r)
        if not isinstance(ico, str) or not RE_APARELHO_ICONE.match(ico):
            raise ValueError("%s: icone invalido" % r)
        if aid in ids or nome in nomes:
            raise ValueError("%s: id ou nome repetido" % r)
        ids.add(aid)
        nomes.add(nome)
        item = {"id": aid, "nome": nome, "rotulo": rot, "icone": ico}
        if "alerta_offline_min" in it:
            m = it["alerta_offline_min"]
            if type(m) is not int or not 1 <= m <= 10080:
                raise ValueError("%s: alerta_offline_min invalido" % r)
            item["alerta_offline_min"] = m
        saida.append(item)
    return saida


def validar_rotinas(lista):
    """Valida `rotinas` (E8; mesmas regras do web). ValueError com a causa; devolve copias novas."""
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise ValueError("rotinas deve ser uma lista")
    if len(lista) > ROTINAS_MAX:
        raise ValueError("rotinas: no maximo %d itens" % ROTINAS_MAX)
    ids, saida = set(), []
    for i, it in enumerate(lista):
        r = "rotinas[%d]" % i
        if not isinstance(it, dict):
            raise ValueError("%s deve ser um objeto" % r)
        if set(it) - CHAVES_ROTINA:
            raise ValueError("%s: chave desconhecida" % r)
        rid, rot, tipo, alvo, idade = (it.get("id"), it.get("rotulo"), it.get("tipo"), it.get("alvo"),
                                       it.get("max_idade_h"))
        if not isinstance(rid, str) or not RE_ROTINA_ID.match(rid):
            raise ValueError("%s: id invalido" % r)
        if not isinstance(rot, str) or not 1 <= len(rot) <= 20 or not rot.isascii() or not rot.isprintable():
            raise ValueError("%s: rotulo invalido" % r)
        if tipo == "timer":
            if not isinstance(alvo, str) or not RE_ROTINA_ALVO_TIMER.match(alvo):
                raise ValueError("%s: alvo invalido" % r)
        elif tipo == "arquivo":
            if (not isinstance(alvo, str) or not os.path.isabs(alvo) or os.path.normpath(alvo) != alvo
                    or not alvo.startswith(PREFIXOS_ARQUIVO)
                    or any(alvo == n or alvo.startswith(n + "/") for n in NEGADOS_ARQUIVO)):
                raise ValueError("%s: alvo invalido" % r)
        else:
            raise ValueError("%s: tipo invalido" % r)
        if (isinstance(idade, bool) or not isinstance(idade, (int, float)) or idade != idade
                or not 0.1 <= idade <= 720):
            raise ValueError("%s: max_idade_h invalido" % r)
        if rid in ids:
            raise ValueError("%s: id repetido" % r)
        ids.add(rid)
        saida.append({"id": rid, "rotulo": rot, "tipo": tipo, "alvo": alvo, "max_idade_h": idade})
    return saida


def validar_amp(valor):
    """Valida a chave `amp` da config (mesmas regras do web; um teste confere). None = feature desligada.

    `{"url": "http://<ipv4 privado>:<porta>", "credenciais": "/etc/kindle-monitor/<arquivo>"}`: so http, host IPv4 em
    10.0.0.0/8, 192.168.0.0/16 ou 100.64.0.0/10 (nunca loopback, nome de host nem IP publico), porta 1-65535
    explicita, sem usuario/senha, caminho ou query na URL; o arquivo de credenciais fica direto em
    /etc/kindle-monitor/. ValueError com a causa (que nunca cita o valor). Devolve uma copia com a URL sem a barra final."""
    if valor is None:
        return None
    if not isinstance(valor, dict):
        raise ValueError("amp deve ser um objeto")
    if set(valor) != CHAVES_AMP:
        raise ValueError("amp: chaves devem ser url e credenciais")
    url, cred = valor["url"], valor["credenciais"]
    m = RE_AMP_URL.match(url) if isinstance(url, str) else None
    if not m:
        raise ValueError("amp.url invalida (http://IPv4:porta)")
    try:
        ip = ipaddress.IPv4Address(m.group(1))
    except ValueError:
        raise ValueError("amp.url: IPv4 invalido") from None
    if not any(ip in rede for rede in REDES_AMP):
        raise ValueError("amp.url: o host deve ser IPv4 privado (10/8, 192.168/16 ou 100.64/10)")
    if int(m.group(2)) > 65535:
        raise ValueError("amp.url: porta fora de 1 a 65535")
    if not isinstance(cred, str) or not RE_AMP_CREDENCIAIS.match(cred):
        raise ValueError("amp.credenciais deve ser um arquivo direto em " + AMP_DIR_CREDENCIAIS)
    return {"url": "http://%s:%s" % (m.group(1), m.group(2)), "credenciais": cred}


def acao_valida(acao):
    return acao in ACOES or bool(RE_SVC_ACAO.match(acao))


def nome_para_acao(token):
    """'svc--<id>--<verbo>' -> 'svc:<id>:<verbo>'; acoes rapidas como estao; None se invalido."""
    if token.startswith("svc--"):
        m = RE_SVC_ARQ.match(token)
        return "svc:%s:%s" % m.groups() if m else None
    return token if RE_ACAO_ARQ.match(token) else None


def validar_cfg(c):
    """Valida a secao "comandos" da config. ValueError com a causa."""
    if not isinstance(c, dict):
        raise ValueError("comandos deve ser um objeto")
    r = {"spool": SPOOL_PADRAO, "estado": ESTADO_PADRAO, "acoes": list(ACOES), "catalogo": [], "aparelhos": [], "rotinas": [],
         "amp": None}
    r.update({k: v for k, v in c.items() if k in r})
    r["catalogo"] = validar_catalogo(r["catalogo"])
    r["aparelhos"] = validar_aparelhos(r["aparelhos"])
    r["rotinas"] = validar_rotinas(r["rotinas"])
    r["amp"] = validar_amp(r["amp"])
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
                       errors="replace", timeout=timeout, env={"PATH": PATH, "LANG": "C", "HOME": "/root"})
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
                 ollama=OLLAMA_PADRAO, dono=None, log=_log_padrao, relogio=time.monotonic, amp_post=None):
        """`dono` = (uid, gid do spool) esperado; padrao (0, nogroup). Injetavel para testes sem root."""
        cfg = validar_cfg(cfg)
        self.spool = cfg["spool"]
        self.estado = cfg["estado"]
        self.habilitadas = list(cfg["acoes"])
        self.catalogo = {i["id"]: i for i in cfg["catalogo"]}
        self.aparelhos = list(cfg["aparelhos"])
        self.rotinas = list(cfg["rotinas"])
        self.amp = cfg["amp"]  # None = feature desligada; so `validar_amp` a preenche em producao
        self._amp_post = amp_post  # None = o cliente urllib `amp_post` (definido mais abaixo no modulo)
        self.agora_inv = time.time
        self.executar = executar
        self.http = http
        self.agora_ns = agora_ns
        self.ollama = ollama.rstrip("/")
        self.dono = dono
        self.log = log
        self.relogio = relogio
        self._lixo_n = 0
        self._cooldown_ruim = False
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

    def inventariar(self):
        """Coleta o inventario e grava status/servicos.json. 1 se gravou, 0 se os diretorios ainda nao existem."""
        self._pai_fds = []
        try:
            if self._abrir() is None:
                return 0
            dados = coletar_inventario(list(self.catalogo.values()), self.executar)
            doc = {"gerado": int(self.agora_inv()), "servicos": dados}
            self._gravar_arquivo(INVENTARIO_ARQ, json.dumps(doc, separators=(",", ":")).encode("utf-8"))
            # depois dos servicos; um nao quebra o outro (cada um grava o seu arquivo, e falha vira log)
            if self.aparelhos:
                self._isolado("aparelhos", self._inventariar_aparelhos)
            if self.rotinas:
                self._isolado("rotinas", self._inventariar_rotinas)
            if self.amp:
                self._isolado("jogos", self._inventariar_jogos)
            return 1
        finally:
            self._fechar(self._pai_fds)
            self._pai_fds = []
            self.fd_spool = self.fd_estado = None

    def _isolado(self, nome, fn):
        try:
            fn()
        except Exception as e:  # BaseException (SIGTERM) continua subindo
            self.log("inventario de %s falhou: %s" % (nome, _curto(type(e).__name__, 40)))

    def _inventariar_rotinas(self):
        """Coleta timers, arquivos e unidades em falha e grava status/rotinas.json. Comando que falha, estoura o
        tempo ou qualquer excecao: todas as rotinas `desconhecido` e `unidades_falhas` zerado. Nunca levanta."""
        try:
            doc = coletar_rotinas(self.rotinas, self.executar, agora=self.agora_inv)
        except Exception as e:
            self.log("rotinas: coleta falhou (%s)" % _curto(type(e).__name__, 40))
            doc = rotinas_desconhecidas(self.rotinas, agora=self.agora_inv)
        self._gravar_arquivo(ROTINAS_ARQ, json.dumps(doc, separators=(",", ":")).encode("utf-8"))

    def _jogos_recente(self, agora):
        """True se o jogos.json atual (arquivo regular do dono esperado, aberto sem seguir link) tem `gerado` de menos de
        AMP_REUSO_S s atras: o AMP nao e consultado de novo. Qualquer duvida (ausente, link, lixo, no futuro) = False."""
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC | getattr(os, "O_NOCTTY", 0)
        try:
            fd = os.open(JOGOS_ARQ, flags, dir_fd=self.fd_estado)
        except OSError:
            return False
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_uid != (self.dono[0] if self.dono else 0) \
                    or st.st_size > COOLDOWN_LER_MAX:
                return False
            gerado = json.loads(os.read(fd, COOLDOWN_LER_MAX).decode("utf-8")).get("gerado")
        except (OSError, ValueError, AttributeError, RecursionError):
            return False
        finally:
            os.close(fd)
        return isinstance(gerado, (int, float)) and not isinstance(gerado, bool) and 0 <= agora - gerado < AMP_REUSO_S

    def _inventariar_jogos(self):
        """Consulta o AMP (no maximo a cada AMP_REUSO_S s) e grava status/jogos.json. Sem arquivo de credenciais = AMP
        desligado (`ativo` false, sem erro, sem abrir conexao). Falha = `erro` com texto fixo. Nunca levanta."""
        if self._jogos_recente(_agora_int(self.agora_inv)):
            return
        ativo, erro, itens = False, None, []
        try:
            cred = ler_credencial(self.amp["credenciais"], self.dono[0] if self.dono else 0)
            if cred is not None:
                ativo = True
                itens = coletar_amp(self.amp["url"], cred[0], cred[1], self._amp_post or amp_post)
        except CredencialInvalida as e:
            ativo, erro = True, str(e)
        except AmpErro as e:
            erro = str(e)
        except Exception:
            erro = "amp sem resposta"
        finally:
            cred = None
        if erro is not None:
            self.log("jogos: %s" % erro)
        doc = {"versao": 1, "gerado": _agora_int(self.agora_inv), "ativo": ativo, "erro": erro, "instancias": itens}
        self._gravar_arquivo(JOGOS_ARQ, json.dumps(doc, separators=(",", ":")).encode("utf-8"))

    def _inventariar_aparelhos(self):
        """Roda `tailscale status --json` (argv fixo, sem shell) e grava status/aparelhos.json. Nunca levanta."""
        texto = None
        try:
            rc, out, _ = self.executar(list(TAILSCALE), TIMEOUT_TAILSCALE)
            texto = out if rc == 0 else None
            erro = "codigo %s" % rc if rc != 0 else None
        except subprocess.TimeoutExpired:
            erro = "tempo esgotado"
        except OSError:
            erro = "comando indisponivel"
        except Exception:  # saida do executor e dado nao confiavel; nada daqui derruba o inventario
            erro = "falha ao executar"
        doc = parse_tailscale(texto, self.aparelhos, agora=self.agora_inv)
        if erro is not None:
            doc["erro"] = _curto(erro, 40)
        self._gravar_arquivo(APARELHOS_ARQ, json.dumps(doc, separators=(",", ":")).encode("utf-8"))

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
            acao = nome_para_acao(m.group(2)) if m else None
            if acao:
                pedidos.append((int(m.group(1)), n, acao))
            else:
                self._descartar(n)
        pedidos.sort()
        vistos = set()
        cooldown = self._ler_cooldown()
        feitos = 0
        t0 = self.relogio()
        for num, nome, acao in pedidos[:PEDIDOS_MAX]:
            if self.relogio() - t0 >= PASSADA_ORCAMENTO_S:
                self.log("orcamento de tempo da passada esgotado; o resto fica no spool")
                break
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
        """Arquivo/symlink e apagado. Diretorio (que casaria com a glob e religaria a .path sem parar) e
        renomeado no lugar para ".lixo-<epoch>-<n>" e, se estiver vazio, removido; senao fica la, fora da glob."""
        try:
            if not stat.S_ISDIR(os.stat(nome, dir_fd=self.fd_spool, follow_symlinks=False).st_mode):
                os.unlink(nome, dir_fd=self.fd_spool)
                return
            self._lixo_n += 1
            novo = ".lixo-%d-%d" % (self.agora_ns() // 10 ** 9, self._lixo_n)
            os.rename(nome, novo, src_dir_fd=self.fd_spool, dst_dir_fd=self.fd_spool)
            self.log("diretorio no spool movido para %s" % novo)
            try:
                os.rmdir(novo, dir_fd=self.fd_spool)
            except OSError:
                pass
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
        svc = RE_SVC_ACAO.match(acao)
        if svc:
            item = self.catalogo.get(svc.group(1))
            if item is None:
                return self._final(num, pid, acao, "falhou", "servico fora do catalogo")
            if svc.group(2) not in item["verbos"]:
                return self._final(num, pid, acao, "falhou", "verbo nao permitido")
        elif acao not in ACOES:
            return self._final(num, pid, acao, "falhou", "acao desconhecida")
        elif acao not in self.habilitadas:
            return self._final(num, pid, acao, "falhou", "acao desligada na config")
        if acao in vistos:
            return self._final(num, pid, acao, "falhou", "duplicado")
        vistos.add(acao)
        agora_s = agora_ns / 1e9
        if self._cooldown_ruim:  # arquivo de cooldown ilegivel: fail-safe, nada roda nesta passada
            return self._final(num, pid, acao, "falhou", "cooldown indisponivel")
        ultimo = cooldown.get(acao)
        if ultimo is not None and 0 <= agora_s - ultimo < COOLDOWN_S:
            return self._final(num, pid, acao, "falhou", "cooldown de %d s" % COOLDOWN_S)
        cooldown[acao] = agora_s  # registrado ANTES de executar: queda no meio tambem conta
        self._gravar_cooldown(cooldown, agora_s)
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
        """{acao: epoch}. Ausente = {}. Ilegivel/corrompido/grande demais: loga, marca `_cooldown_ruim` (nada roda
        nesta passada) e reescreve vazio para a proxima funcionar."""
        self._cooldown_ruim = False
        try:
            fd = os.open(COOLDOWN_ARQ, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd_estado)
        except FileNotFoundError:
            return {}
        except OSError:
            return self._cooldown_falhou("nao abre")
        try:
            st = os.fstat(fd)
            uid = self.dono[0] if self.dono else 0
            if not stat.S_ISREG(st.st_mode) or st.st_uid != uid:
                return self._cooldown_falhou("tipo ou dono errado")
            bruto = os.read(fd, COOLDOWN_LER_MAX + 1)
            if len(bruto) > COOLDOWN_LER_MAX:
                return self._cooldown_falhou("grande demais")
            dados = json.loads(bruto.decode("utf-8"))
        except (OSError, ValueError):
            return self._cooldown_falhou("ilegivel")
        finally:
            os.close(fd)
        if not isinstance(dados, dict):
            return self._cooldown_falhou("nao e um objeto")
        return {k: float(v) for k, v in dados.items()
                if acao_valida(k) and isinstance(v, (int, float)) and not isinstance(v, bool)}

    def _cooldown_falhou(self, motivo):
        self.log("cooldown %s: nenhuma acao roda nesta passada" % motivo)
        self._cooldown_ruim = True
        self._gravar_arquivo(COOLDOWN_ARQ, b"{}")
        return {}

    def _gravar_cooldown(self, cooldown, agora_s):
        """Grava so o que ainda importa (ate max(cooldown, validade) de idade): o arquivo nao cresce sem limite."""
        for k in [k for k, v in cooldown.items() if not 0 <= agora_s - v <= COOLDOWN_GUARDAR_S]:
            del cooldown[k]
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
        """True = bloqueia. Fail-closed: so libera com rc 0 e ActiveState exatamente inactive ou failed."""
        try:
            rc, out, _ = self.executar(AUTOUPDATE, TIMEOUT_AUTOUPDATE)
        except (subprocess.TimeoutExpired, OSError):
            return True
        return not (rc == 0 and out.strip() in AUTOUPDATE_LIVRE)

    @staticmethod
    def argv_servico(item, verbo):
        """argv FIXO por tipo; so o alvo (validado, root-owned) e o projeto entram. -> (argv, timeout)"""
        v = VERBO_CLI[verbo]
        tipo = item["tipo"]
        if tipo == "systemd":
            return ["systemctl", v, item["alvo"]], TIMEOUT_CMD
        if tipo == "incus":
            return ["incus", v, item["alvo"], "--project", item.get("projeto", "core")], TIMEOUT_INCUS
        if tipo == "docker":
            return INCUS_MICRO + ["docker", v, item["alvo"]], TIMEOUT_EXEC
        return INCUS + ["systemctl", v, item["alvo"]], TIMEOUT_EXEC

    def _servico(self, acao):
        sid, verbo = RE_SVC_ACAO.match(acao).groups()
        item = self.catalogo[sid]
        if item["protegido"] and self._autoupdate_ativo():
            raise Falha("atualizacao automatica em andamento")
        argv, timeout = self.argv_servico(item, verbo)
        self._cmd(argv, timeout)
        return "concluido"

    def _rodar(self, acao):
        if RE_SVC_ACAO.match(acao):
            return self._servico(acao)
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


# ------------------------------------------------------------------ inventario

def _detalhe(texto):
    return re.sub(r"[^A-Za-z0-9 _.,:/()=+-]", "?", str(texto))[:24]


def parse_systemctl_show(texto):
    """{unit: (ActiveState, SubState)} da saida de `systemctl show -p Id,ActiveState,SubState ...` (blocos separados por linha vazia)."""
    r = {}
    for bloco in texto.split("\n\n"):
        kv = {}
        for linha in bloco.splitlines():
            k, sep, v = linha.partition("=")
            if sep:
                kv[k.strip()] = v.strip()
        if kv.get("Id"):
            r[kv["Id"]] = (kv.get("ActiveState", ""), kv.get("SubState", ""))
    return r


def parse_incus_csv(texto):
    """{(nome, projeto): ESTADO} de `incus list --all-projects --format csv -c n,s,e`."""
    r = {}
    for linha in texto.splitlines():
        col = linha.strip().split(",")
        if len(col) >= 3 and col[0]:
            r[(col[0], col[2])] = col[1].strip().upper()
    return r


def parse_docker_ps(texto):
    """[(nome, estado)] de `docker ps -a --format '{{.Names}} {{.State}}'`."""
    r = []
    for linha in texto.splitlines():
        col = linha.split()
        if len(col) >= 2:
            r.append((col[0], col[1].lower()))
    return r


def estado_systemd(ativo, sub):
    if ativo in ("active", "reloading", "activating"):
        return "ativo", _detalhe(sub or ativo)
    if ativo in ("inactive", "deactivating"):
        return "parado", _detalhe(sub or ativo)
    if ativo == "failed":
        return "falha", _detalhe(sub or ativo)
    return "desconhecido", _detalhe(ativo or "sem dados")


def estado_incus(estado):
    if estado == "RUNNING":
        return "ativo", "rodando"
    if estado in ("STOPPED", "FROZEN"):
        return "parado", _detalhe(estado.lower())
    if estado == "ERROR":
        return "falha", "erro"
    return "desconhecido", _detalhe(estado.lower())


def estado_docker(estado):
    if estado == "running":
        return "ativo", "rodando"
    if estado in ("exited", "created", "paused"):
        return "parado", _detalhe(estado)
    if estado in ("restarting", "dead"):
        return "falha", _detalhe(estado)
    return "desconhecido", _detalhe(estado)


def _estado_docker_prefixo(estados):
    """Tarefas do swarm: todas rodando = ativo (N/N); alguma nao = falha; nenhuma = parado."""
    if not estados:
        return "parado", "sem tarefas"
    n = sum(1 for e in estados if e == "running")
    return ("ativo" if n == len(estados) else "falha"), "%d/%d" % (n, len(estados))


def coletar_inventario(catalogo, executar):
    """{id: {"estado", "detalhe"}} do catalogo (ja validado). `executar(argv, timeout)` -> (rc, stdout, stderr).

    Uma chamada em lote por tipo, timeout de 10 s, nunca shell. Chamada que falha deixa seus itens "desconhecido".
    """
    saida = {}

    def chamar(argv):
        try:
            rc, out, _ = executar(argv, TIMEOUT_INVENTARIO)
        except subprocess.TimeoutExpired:
            return None, "tempo esgotado"
        except OSError:
            return None, "comando indisponivel"
        if rc != 0:
            return None, "codigo %s" % rc
        return out, ""

    def tudo(itens, motivo):
        for i in itens:
            saida[i["id"]] = {"estado": "desconhecido", "detalhe": _detalhe(motivo)}

    def porti(tipo):
        return [i for i in catalogo if i["tipo"] == tipo]

    def systemd(itens, prefixo_argv):
        if not itens:
            return
        out, erro = chamar(prefixo_argv + ["systemctl", "show", "-p", "Id,ActiveState,SubState"] +
                           [i["alvo"] for i in itens])
        if out is None:
            return tudo(itens, erro)
        achados = parse_systemctl_show(out)
        for i in itens:
            if i["alvo"] in achados:
                e, d = estado_systemd(*achados[i["alvo"]])
                saida[i["id"]] = {"estado": e, "detalhe": d}
            else:
                saida[i["id"]] = {"estado": "desconhecido", "detalhe": "nao encontrado"}

    systemd(porti("systemd"), [])
    systemd(porti("rathena"), INCUS)

    itens = porti("incus")
    if itens:
        out, erro = chamar(["incus", "list", "--all-projects", "--format", "csv", "-c", "n,s,e"])
        if out is None:
            tudo(itens, erro)
        else:
            achados = parse_incus_csv(out)
            for i in itens:
                est = achados.get((i["alvo"], i.get("projeto", "core")))
                if est is None:
                    saida[i["id"]] = {"estado": "desconhecido", "detalhe": "nao encontrado"}
                else:
                    e, d = estado_incus(est)
                    saida[i["id"]] = {"estado": e, "detalhe": d}

    itens = porti("docker")
    if itens:
        out, erro = chamar(INCUS_MICRO + ["docker", "ps", "-a", "--format", "{{.Names}} {{.State}}"])
        if out is None:
            tudo(itens, erro)
        else:
            lista = parse_docker_ps(out)
            for i in itens:
                if i.get("prefixo"):
                    e, d = _estado_docker_prefixo([s for n, s in lista if n.startswith(i["alvo"])])
                else:
                    est = [s for n, s in lista if n == i["alvo"]]
                    e, d = estado_docker(est[0]) if est else ("desconhecido", "nao encontrado")
                saida[i["id"]] = {"estado": e, "detalhe": d}
    return saida


_RE_FRACAO = re.compile(r"(\.\d{1,9})(?=Z|[+-]\d{2}:?\d{2}|\Z)")


def _epoch_visto(valor):
    """LastSeen (ISO 8601, sufixo Z, fracao de ate 9 digitos) -> epoch int; None se vazio, zero ou invalido."""
    if not isinstance(valor, str) or not 10 <= len(valor) <= 64 or not valor.isascii():
        return None
    t = valor.strip()
    if t.endswith(("Z", "z")):
        t = t[:-1] + "+00:00"
    t = _RE_FRACAO.sub(lambda m: (m.group(1) + "000000")[:7], t, count=1)  # fromisoformat antigo so aceita 3 ou 6
    try:
        d = datetime.datetime.fromisoformat(t)
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        n = int(d.timestamp())
    except (ValueError, OverflowError, OSError):
        return None
    return n if n > 946684800 else None  # antes de 2000 = "0001-01-01" do Tailscale (nunca visto) ou lixo


def _dns_sem_ponto(v):
    """DNSName em minusculas e sem o ponto final; None se nao for texto."""
    if not isinstance(v, str):
        return None
    v = v.strip().lower()
    return v[:-1] if v.endswith(".") else v


def _sufixo_tailnet(dados):
    """Sufixo MagicDNS da propria tailnet (`<tailnet>.ts.net`) ou None.

    Vem do nome do proprio no (`Self.DNSName` sem o 1o rotulo); sem ele, de `CurrentTailnet.MagicDNSSuffix` ou
    `MagicDNSSuffix`. Um no compartilhado de outra tailnet tem outro sufixo e nao pode valer como aparelho meu."""
    eu = dados.get("Self")
    dns = _dns_sem_ponto(eu.get("DNSName")) if isinstance(eu, dict) else None
    if dns:
        suf = dns.partition(".")[2]
        if suf:
            return suf
    atual = dados.get("CurrentTailnet")
    for v in (atual.get("MagicDNSSuffix") if isinstance(atual, dict) else None, dados.get("MagicDNSSuffix")):
        suf = _dns_sem_ponto(v)
        if suf:
            return suf
    return None


def parse_tailscale(texto, catalogo, agora=None):
    """Saida de `tailscale status --json` -> aparelhos.json (E7). Pura; NUNCA levanta.

    `catalogo` = lista validada por validar_aparelhos. So sai o que o catalogo pede e so id, online, visto_em e
    conexao: nenhum IP, chave, e-mail, usuario, SO ou nome de peer de fora do catalogo. So vale peer cujo DNSName
    e `<nome>.<sufixo MagicDNS da minha tailnet>`; sem como saber o sufixo, e erro. Entrada ruim vira `erro`
    curto (ASCII, <= 40) com todos online null.
    """
    ids = [(a["id"], a["nome"]) for a in catalogo]
    vazio = {i: {"online": None, "visto_em": None, "conexao": None} for i, _ in ids}
    try:
        gerado = int((agora or time.time)())
    except Exception:
        gerado = 0

    def doc(erro, aparelhos):
        return {"versao": 1, "gerado": gerado, "erro": erro, "aparelhos": aparelhos}

    if not isinstance(texto, str) or not texto.strip():
        return doc("saida vazia", vazio)
    if len(texto) > TAILSCALE_MAX:
        return doc("saida grande demais", vazio)
    try:
        dados = json.loads(texto)
    except (ValueError, RecursionError):
        return doc("json invalido", vazio)
    peers = dados.get("Peer") if isinstance(dados, dict) else None
    if not isinstance(peers, dict):
        return doc("formato inesperado", vazio)
    sufixo = _sufixo_tailnet(dados)
    if not sufixo:
        return doc("sem sufixo da tailnet", vazio)  # sem ele nao da para separar meus aparelhos dos alheios
    achados = {}
    for p in peers.values():
        if not isinstance(p, dict) or not isinstance(p.get("DNSName"), str):
            continue
        rotulo, _, resto = _dns_sem_ponto(p["DNSName"]).partition(".")
        if resto != sufixo:
            continue  # no de outra tailnet (compartilhado) com o mesmo 1o rotulo
        online = p.get("Online") if isinstance(p.get("Online"), bool) else None
        if rotulo in achados and not (online is True and achados[rotulo]["online"] is not True):
            continue  # nome repetido: o primeiro vale, a nao ser que o novo esteja online e o antigo nao
        cur, relay = p.get("CurAddr"), p.get("Relay")
        if isinstance(cur, str) and cur:
            conexao = "direto"
        elif isinstance(relay, str) and relay:
            conexao = "relay"
        else:
            conexao = None
        achados[rotulo] = {"online": online, "visto_em": _epoch_visto(p.get("LastSeen")), "conexao": conexao}
    return doc(None, {i: dict(achados.get(nome, vazio[i])) for i, nome in ids})


def _agora_int(agora):
    try:
        return int(agora())
    except Exception:
        return 0


def rotinas_desconhecidas(catalogo, agora=time.time):
    """rotinas.json de quando nada pode ser lido: todas `desconhecido`, sem unidades em falha."""
    return {"versao": 1, "gerado": _agora_int(agora),
            "rotinas": {r["id"]: {"resultado": "desconhecido", "ultima_em": None, "detalhe": "sem dados"}
                        for r in catalogo},
            "unidades_falhas": {"n": 0, "nomes": []}}


_SHOW_CHAVES = ("Id", "Result", "LoadState", "ExecMainStatus", "ExecMainExitTimestamp")


def parse_show(texto):
    """Saida de `systemctl show -p ...` (blocos `Chave=valor` separados por linha em branco) -> {Id: {chave: valor}}.

    Pura; so as chaves pedidas; texto nao confiavel (limitado, nunca levanta)."""
    saida = {}
    if not isinstance(texto, str):
        return saida
    bloco = {}

    def fecha():
        i = bloco.get("Id")
        if i and i not in saida:
            saida[i] = dict(bloco)
        bloco.clear()

    for linha in texto[:SAIDA_ROTINAS_MAX].splitlines():
        if not linha.strip():
            fecha()
            continue
        k, sep, v = linha.partition("=")
        if sep and k in _SHOW_CHAVES:
            bloco[k] = v.strip()[:80]
    fecha()
    return saida


def _epoch_unix(valor):
    """`@1795054082` (--timestamp=unix) -> int; None se vazio, zero, antes de 2000 ou invalido."""
    if not isinstance(valor, str) or not re.match(r"^@\d{1,12}\Z", valor):
        return None
    n = int(valor[1:])
    return n if n > 946684800 else None


def _resultado_timer(info):
    """info do `show` de uma unit (ou None) -> {"resultado", "ultima_em", "detalhe"}."""
    def r(res, ultima, det):
        return {"resultado": res, "ultima_em": ultima, "detalhe": _curto(det, 24)}
    if info is None or info.get("LoadState") == "not-found":
        return r("desconhecido", None, "sem unidade")
    if info.get("LoadState") != "loaded":
        return r("desconhecido", None, "nao carregada")
    ultima = _epoch_unix(info.get("ExecMainExitTimestamp"))
    res = info.get("Result")
    if not isinstance(res, str) or not RE_RESULTADO_UNIT.match(res):
        return r("desconhecido", ultima, "sem resultado")
    if res == "success":
        return r("ok", ultima, "ok") if ultima is not None else r("desconhecido", None, "nunca rodou")
    status = info.get("ExecMainStatus")
    if res == "exit-code" and isinstance(status, str) and re.match(r"^\d{1,3}\Z", status):
        return r("falha", ultima, "exit %s" % status)
    return r("falha", ultima, res)


_O_CAMINHO = getattr(os, "O_PATH", 0)  # Linux: fd so para caminho (sem permissao de leitura, nao bloqueia em FIFO)
_FLAGS_COMPONENTE = _O_CAMINHO | os.O_NOFOLLOW | os.O_CLOEXEC
_FLAGS_LISTAR = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_CLOEXEC | getattr(os, "O_NOCTTY", 0)


class _SemLink(Exception):
    """Componente do alvo e um link simbolico."""


def _abrir_componente(nome, dir_fd):
    """Abre `nome` dentro de `dir_fd` sem seguir link (O_PATH|O_NOFOLLOW); devolve (fd, fstat). Link vira _SemLink."""
    fd = os.open(nome, _FLAGS_COMPONENTE, dir_fd=dir_fd)
    try:
        st = os.fstat(fd)
        if _stat.S_ISLNK(st.st_mode):
            raise _SemLink()
    except BaseException:
        os.close(fd)
        raise
    return fd, st


def _mtime_arquivo(alvo):
    """(ultima_em|None, detalhe). Sem seguir symlink em NENHUM componente, sem ler conteudo, sem recursao.

    Roda como root sobre caminhos que outros usuarios podem alterar: desce de "/" por descritores
    (openat com O_NOFOLLOW em cada componente), decide o tipo com fstat no descritor final e lista o
    diretorio pelo proprio descritor, entao trocar um componente por link entre as etapas nao desvia a leitura."""
    partes = alvo.split("/") if isinstance(alvo, str) and alvo.startswith("/") else []
    partes = partes[1:]
    if not partes or any(p in ("", ".", "..") or "\0" in p for p in partes):
        return None, "erro de leitura"
    abertos = []

    def abre(nome, base):
        fd, st = _abrir_componente(nome, base)
        abertos.append(fd)
        return fd, st

    try:
        atual = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        abertos.append(atual)
        for nome in partes[:-1]:
            atual, st = abre(nome, atual)
            if not _stat.S_ISDIR(st.st_mode):
                return None, "erro de leitura"
        fd, st = abre(partes[-1], atual)
        modo = st.st_mode
        if _stat.S_ISREG(modo):
            return _mtime_valido(st.st_mtime)
        if not _stat.S_ISDIR(modo):
            return None, "tipo inesperado"
        # reabre "." a partir do proprio descritor (mesmo inodo, agora listavel); confere o tipo de novo
        dfd = os.open(".", _FLAGS_LISTAR, dir_fd=fd)
        abertos.append(dfd)
        if not _stat.S_ISDIR(os.fstat(dfd).st_mode):
            return None, "tipo inesperado"
        melhor, vistas = None, 0
        with os.scandir(dfd) as it:
            for e in it:
                vistas += 1
                if vistas > ARQUIVO_ENTRADAS_MAX:
                    break
                try:
                    if e.is_symlink():
                        continue
                    m = e.stat(follow_symlinks=False).st_mtime
                except OSError:
                    continue
                if melhor is None or m > melhor:
                    melhor = m
        if melhor is None:
            return None, "vazio"
        return _mtime_valido(melhor)
    except _SemLink:
        return None, "link ignorado"
    except FileNotFoundError:
        return None, "sem arquivo"
    except (OSError, ValueError):
        return None, "erro de leitura"
    finally:
        for fd in abertos:
            try:
                os.close(fd)
            except OSError:
                pass


def _mtime_valido(m):
    try:
        n = int(m)
    except (TypeError, ValueError, OverflowError):
        return None, "data invalida"
    return (n, "ok") if 946684800 < n < 4102444800 else (None, "data invalida")  # 2000 .. 2100


def parse_falhas(texto):
    """Saida de `systemctl list-units --failed --plain --no-legend` -> {"n", "nomes"}.

    1a coluna de cada linha; `n` conta as linhas (limitado a 9999); `nomes` so tem as que passam em
    ^[A-Za-z0-9_.@:-]{1,40}$ (ate 5). Linha que cita "empresa-x" (qualquer caixa) nao conta nem aparece.
    Pura; nunca levanta."""
    n, nomes = 0, []
    if not isinstance(texto, str):
        return {"n": 0, "nomes": []}
    for linha in texto[:SAIDA_ROTINAS_MAX].splitlines():
        col = linha.split(None, 1)
        if not col or "empresa-x" in linha.lower():  # nada da empresa-x vai para a tela (nem na contagem)
            continue
        n += 1
        if len(nomes) < FALHAS_NOMES_MAX and RE_UNIDADE_FALHA.match(col[0]):
            nomes.append(col[0])
    return {"n": min(n, FALHAS_N_MAX), "nomes": nomes}


def coletar_rotinas(catalogo, executar, agora=time.time):
    """Catalogo validado -> rotinas.json (E7). Dependencias injetadas; so o argv fixo e os alvos ja validados
    (argumentos separados, depois de `--`) chegam ao systemctl. Comando com saida != 0 ou que levanta: a excecao
    sobe e o chamador grava tudo `desconhecido`. Erro em arquivo vira `desconhecido` so naquela rotina."""
    timers = []
    for r in catalogo:
        if r["tipo"] == "timer" and r["alvo"] not in timers:
            timers.append(r["alvo"])
    infos = {}
    if timers:
        rc, out, _ = executar(SHOW_ROTINAS + timers, TIMEOUT_ROTINAS)
        if rc != 0:
            raise RuntimeError("systemctl show rc=%s" % rc)
        infos = parse_show(out)
    rc, out, _ = executar(list(LISTA_FALHAS), TIMEOUT_ROTINAS)
    if rc != 0:
        raise RuntimeError("systemctl list-units rc=%s" % rc)
    falhas = parse_falhas(out)
    rotinas = {}
    for r in catalogo:
        if r["tipo"] == "timer":
            rotinas[r["id"]] = _resultado_timer(infos.get(r["alvo"]))
        else:
            ultima, det = _mtime_arquivo(r["alvo"])
            rotinas[r["id"]] = {"resultado": "ok" if ultima is not None else "desconhecido",
                                "ultima_em": ultima, "detalhe": _curto(det, 24)}
    return {"versao": 1, "gerado": _agora_int(agora), "rotinas": rotinas, "unidades_falhas": falhas}


# ------------------------------------------------------------------------ jogos (AMP)

def _controle(ch):
    o = ord(ch)
    return o < 32 or o == 127 or 0x80 <= o < 0xA0


def ler_credencial(caminho, uid=0):
    """`(usuario, senha)` do arquivo de credenciais do AMP; None se o arquivo nao existe (AMP desligado).

    Duas linhas: usuario e senha. So vale arquivo regular, do dono `uid` (root), modo exatamente 0600 ou 0400, aberto
    sem seguir symlink e sem bloquear em FIFO. Qualquer outra coisa e CredencialInvalida, sem citar o caminho nem o
    conteudo. A senha so existe nesta tupla: nunca vai a log, argv, JSON ou excecao."""
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC | getattr(os, "O_NOCTTY", 0)
    try:
        fd = os.open(caminho, flags)
    except FileNotFoundError:
        return None
    except OSError:
        raise CredencialInvalida() from None
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid != uid or (st.st_mode & 0o7777) not in (0o600, 0o400)
                or st.st_size > AMP_CREDENCIAL_MAX):
            raise CredencialInvalida()
        bruto = os.read(fd, AMP_CREDENCIAL_MAX + 1)
    except OSError:
        raise CredencialInvalida() from None
    finally:
        os.close(fd)
    if len(bruto) > AMP_CREDENCIAL_MAX:
        raise CredencialInvalida()
    try:
        linhas = [l[:-1] if l.endswith("\r") else l for l in bruto.decode("utf-8").split("\n")]
    except UnicodeDecodeError:
        raise CredencialInvalida() from None
    while linhas and not linhas[-1]:
        linhas.pop()
    if len(linhas) != 2:
        raise CredencialInvalida()
    usuario, senha = linhas
    if (not 1 <= len(usuario) <= AMP_USUARIO_MAX or not 1 <= len(senha) <= AMP_SENHA_MAX
            or any(_controle(ch) for ch in usuario + senha)):
        raise CredencialInvalida()
    return usuario, senha


class _SemRedirect(urllib.request.HTTPRedirectHandler):
    """Nunca segue redirect: a senha so vai para o host da config."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def amp_post(url, corpo, timeout):
    """POST JSON em `url` (ja montada a partir da `amp.url` validada) e devolve o JSON da resposta.

    Sem proxy, sem redirect, so os cabecalhos Content-Type e Accept `application/json`. `timeout` vale por operacao
    de rede e tambem como prazo da chamada inteira (uma resposta que goteja nao estica o inventario); a resposta
    passa de AMP_MAX_BYTES = AmpErro. Excecoes de rede/HTTP/JSON sobem como estao (o chamador as troca por texto fixo)."""
    dados = json.dumps(corpo).encode("utf-8")
    req = urllib.request.Request(url, data=dados, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "kindle-monitor"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _SemRedirect)
    prazo = time.monotonic() + timeout
    partes, total = [], 0
    with opener.open(req, timeout=timeout) as r:
        while True:
            if time.monotonic() > prazo:
                raise TimeoutError("prazo da chamada")
            parte = r.read1(65536)  # read1: no maximo uma leitura de socket, para o prazo valer entre as partes
            if not parte:
                break
            total += len(parte)
            if total > AMP_MAX_BYTES:
                raise AmpErro("amp resposta grande")
            partes.append(parte)
    return json.loads(b"".join(partes).decode("utf-8"))


def _ascii_amp(valor, tam):
    """Texto do AMP (dado nao confiavel) -> ASCII imprimivel: NFKD, sem combinantes nem controles, ate `tam`."""
    if not isinstance(valor, str):
        return ""
    s = unicodedata.normalize("NFKD", valor[:tam * 4])
    s = "".join(c for c in s if not unicodedata.combining(c) and unicodedata.category(c)[0] != "C")
    return " ".join(s.encode("ascii", "ignore").decode("ascii").split())[:tam]


def _inteiro_amp(v):
    """Contagem do AMP -> int 0..AMP_VALOR_MAX; None se nao for numero inteiro razoavel."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if isinstance(v, float):
        if v != v or v in (float("inf"), float("-inf")) or v != int(v):
            return None
        v = int(v)
    return v if 0 <= v <= AMP_VALOR_MAX else None


def _estado_amp(running, appstate):
    """(Running, AppState) -> estado do painel; a tabela e o motivo estao em APPSTATE_ESTADO."""
    if running is not True:
        return "parado"
    if type(appstate) is not int:
        return "outro"
    return APPSTATE_ESTADO.get(appstate, "outro")


def _id_amp(iid):
    return hashlib.sha256(iid.encode("utf-8")).hexdigest()[:8]


def _instancia_amp(iid, detalhe, running, numero):
    """Uma instancia -> item de jogos.json, ou None se for o controlador ADS.

    `detalhe` = resposta de ADSModule/GetInstance (dict) ou None se a chamada falhou ou nao rodou (prazo): sai como
    "instancia <numero>", sem modulo nem jogadores, com o estado so de `running` (o `Running` de GetInstanceStatuses):
    parado se nao for true, senao "outro". Com `detalhe`, o `Running` dele manda quando e booleano."""
    if not isinstance(detalhe, dict):
        return {"id": _id_amp(iid), "nome": "instancia %d" % numero, "modulo": "",
                "estado": _estado_amp(running, None), "jogadores": None, "max": None}
    modulo, exibicao = detalhe.get("Module"), detalhe.get("ModuleDisplayName")
    if isinstance(modulo, str) and modulo.strip().lower() in AMP_MODULOS_ADS:
        return None
    mod = _ascii_amp(modulo, 16)
    if not mod or mod.lower() == "genericmodule":
        mod = _ascii_amp(exibicao, 16) or mod
    ligada = detalhe["Running"] if isinstance(detalhe.get("Running"), bool) else running
    estado = _estado_amp(ligada, detalhe.get("AppState"))
    if detalhe.get("Suspended") is True:
        estado = "parado"
    jogadores = maximo = None
    m = detalhe.get("Metrics")
    usuarios = m.get("Active Users") if isinstance(m, dict) else None
    if isinstance(usuarios, dict):
        jogadores = _inteiro_amp(usuarios.get("RawValue"))
        maximo = _inteiro_amp(usuarios.get("MaxValue")) if jogadores is not None else None
    return {"id": _id_amp(iid), "nome": _ascii_amp(detalhe.get("FriendlyName"), 24) or "sem nome", "modulo": mod,
            "estado": estado, "jogadores": jogadores, "max": maximo}


def parse_statuses(dados):
    """Resposta de ADSModule/GetInstanceStatuses -> [(InstanceID, Running)] de ate JOGOS_MAX instancias.

    A resposta e dado nao confiavel: so entram entradas com InstanceID no formato de uuid (e so ele vai para a URL/corpo
    das chamadas seguintes), sem repeticao (sem diferenciar caixa); o resto e descartado. `Running` e True so se for
    exatamente true. Formato que nao e lista (nem {"result": lista}) = AmpErro("amp formato inesperado")."""
    if isinstance(dados, dict):
        dados = dados.get("result")
    if not isinstance(dados, list):
        raise AmpErro("amp formato inesperado")
    vistos = {}
    for it in dados:
        iid = it.get("InstanceID") if isinstance(it, dict) else None
        if not isinstance(iid, str) or not RE_AMP_UUID.match(iid) or iid.lower() in vistos:
            continue
        vistos[iid.lower()] = (iid, it.get("Running") is True)
        if len(vistos) >= JOGOS_MAX:
            break
    return list(vistos.values())


def _ordenar_instancias(itens):
    """Sem repeticao de id; ligadas primeiro, depois por nome; ate JOGOS_MAX."""
    achadas = {}
    for i in itens:
        if i is not None and i["id"] not in achadas:
            achadas[i["id"]] = i
    ordem = sorted(achadas.values(), key=lambda i: (i["estado"] != "rodando", i["nome"].lower(), i["id"]))
    return ordem[:JOGOS_MAX]


def coletar_amp(url, usuario, senha, post, relogio=time.monotonic):
    """Login, lista de instancias, um GetInstance por instancia e logout no AMP; devolve as instancias do jogos.json.

    `post(url, corpo, timeout)` e `relogio` sao injetaveis. O `GetInstances` do AMP so devolve o controlador (ADS), entao
    a lista vem de GetInstanceStatuses (InstanceID e Running) e os dados de cada uma de GetInstance. So metodos de
    leitura (e o logout): nunca Start/Stop/Create/Delete.

    Falha no login ou em GetInstanceStatuses = AmpErro com texto FIXO ("amp sem resposta", "amp login falhou", "amp
    formato inesperado"...): nada do servidor, da senha ou da excecao original entra na mensagem. Falha em UM GetInstance
    nao derruba o resto (aquela instancia sai como `_instancia_amp(..., None)`); passou de AMP_PRAZO_S desde o login, as
    que faltam saem assim sem chamada. O logout e so de cortesia (a API pode nem ter o metodo): falha dele e ignorada.
    A senha so vai no corpo do login."""
    inicio = relogio()
    try:
        r = post(url + "/API/Core/Login",
                 {"username": usuario, "password": senha, "token": "", "rememberMe": False}, AMP_TIMEOUT_S)
    except AmpErro:
        raise
    except urllib.error.HTTPError:
        raise AmpErro("amp login falhou") from None
    except Exception:
        raise AmpErro("amp sem resposta") from None
    sessao = r.get("sessionID") if isinstance(r, dict) and r.get("success") is True else None
    if not isinstance(sessao, str) or not RE_AMP_SESSAO.match(sessao):
        raise AmpErro("amp login falhou")
    try:
        try:
            lista = parse_statuses(post(url + "/API/ADSModule/GetInstanceStatuses", {"SESSIONID": sessao},
                                        AMP_TIMEOUT_S))
        except AmpErro:
            raise
        except Exception:
            raise AmpErro("amp sem resposta") from None
        itens = []
        for numero, (iid, running) in enumerate(lista, 1):
            detalhe = None
            restante = AMP_PRAZO_S - (relogio() - inicio)
            if restante > 0:
                try:
                    detalhe = post(url + "/API/ADSModule/GetInstance", {"SESSIONID": sessao, "InstanceId": iid},
                                   max(1, min(AMP_TIMEOUT_S, restante)))
                except Exception:  # so esta instancia: o resto segue (Interrompido e BaseException e passa)
                    detalhe = None
            itens.append(_instancia_amp(iid, detalhe, running, numero))
        return _ordenar_instancias(itens)
    finally:
        try:
            post(url + "/API/Core/Logout", {"SESSIONID": sessao}, AMP_TIMEOUT_S)
        except Exception:
            pass


def carregar_cfg(caminho):
    """Le e valida a secao "comandos". OSError/ValueError com a causa."""
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    if not isinstance(dados, dict):
        raise ValueError("config: raiz deve ser um objeto")
    cfg = validar_cfg(dict(dados.get("comandos", {})) if isinstance(dados.get("comandos", {}), dict)
                      else dados.get("comandos"))
    cfg["catalogo"] = validar_catalogo(dados.get("servicos_kindle", []))
    # aparelhos invalidos nao derrubam o resto: lista vazia (nada a fazer) e o motivo para o main registrar
    try:
        cfg["aparelhos"] = validar_aparelhos(dados.get("aparelhos", []))
    except ValueError as e:
        cfg["aparelhos"] = []
        cfg["aparelhos_erro"] = str(e)
    try:
        cfg["rotinas"] = validar_rotinas(dados.get("rotinas", []))
    except ValueError as e:
        cfg["rotinas"] = []
        cfg["rotinas_erro"] = str(e)
    # amp invalida desliga so o painel de jogos (None) e deixa o motivo para o main registrar
    try:
        cfg["amp"] = validar_amp(dados.get("amp"))
    except ValueError as e:
        cfg["amp"] = None
        cfg["amp_erro"] = str(e)
    return cfg


def main(argv=None, log=_log_padrao):
    p = argparse.ArgumentParser(description="Executor root do kindle-monitor.")
    p.add_argument("--config", required=True)
    p.add_argument("--inventario", action="store_true",
                   help="coleta o estado dos servicos do catalogo e grava status/servicos.json (sem tocar no spool)")
    args = p.parse_args(argv)
    try:
        cfg = carregar_cfg(args.config)
    except (OSError, ValueError) as e:
        # exit 0: config ruim nao pode virar laco de falhas disparado pela .path
        log("config invalida, nada feito: %s" % _curto(e, 120))
        return 0
    if args.inventario and cfg.get("aparelhos_erro"):
        log("aparelhos invalidos, aparelhos.json nao gravado: %s" % _curto(cfg["aparelhos_erro"], 120))
    if args.inventario and cfg.get("rotinas_erro"):
        log("rotinas invalidas, rotinas.json nao gravado: %s" % _curto(cfg["rotinas_erro"], 120))
    if args.inventario and cfg.get("amp_erro"):
        log("amp invalida, jogos.json nao gravado: %s" % _curto(cfg["amp_erro"], 120))
    signal.signal(signal.SIGTERM, _sigterm)
    try:
        ex = Executor(cfg, log=log)
        if args.inventario:
            ex.inventariar()
        else:
            ex.processar_spool()
    except Recusa as e:
        log("recusado: %s" % _curto(e, 160))
        return 1
    except Interrompido:
        log("interrompido por SIGTERM")
        return 143
    return 0


if __name__ == "__main__":
    sys.exit(main())
