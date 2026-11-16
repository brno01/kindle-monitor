#!/usr/bin/python3 -I
"""Prepara o token da API de comandos (rodado pelo instalador, como root). Nunca imprime o token.

- <dir>/token.raw    : token cru (64 hex), root:root 0600, para o dono copiar ao Kindle.
- <dir>/token.sha256 : hex do sha256 do token cru, root:nogroup 0640; e o unico que o web le.

O token cru so e gerado se nao houver um valido. Existente invalido = erro claro (exit 1), nada e
sobrescrito. Um /etc/kindle-monitor/token antigo (cru, legivel pelo web) e migrado para token.raw.
Biblioteca padrao apenas.
"""
import grp
import hashlib
import os
import re
import secrets
import sys

RE_TOKEN = re.compile(r"^[0-9a-f]{64}$")


def _ler(caminho):
    with open(caminho, "r", encoding="ascii") as f:
        return f.readline().strip()


def _escrever(caminho, texto, modo, gid):
    tmp = caminho + ".tmp"
    try:
        os.unlink(tmp)
    except FileNotFoundError:
        pass
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, modo)
    with os.fdopen(fd, "w", encoding="ascii") as f:
        os.fchmod(f.fileno(), modo)
        if os.geteuid() == 0:
            os.fchown(f.fileno(), 0, gid)
        f.write(texto + "\n")
    os.rename(tmp, caminho)


def preparar(dir_, gid):
    """Devolve a lista de acoes tomadas (texto sem segredo). SystemExit(1) se o token existente for invalido."""
    raw = os.path.join(dir_, "token.raw")
    antigo = os.path.join(dir_, "token")
    feito = []
    if not os.path.lexists(raw) and os.path.lexists(antigo):
        try:
            valor = _ler(antigo)
        except (OSError, ValueError):
            valor = ""
        if not RE_TOKEN.match(valor):
            raise SystemExit("erro: %s existe mas nao tem 64 caracteres hex; corrija ou apague" % antigo)
        os.rename(antigo, raw)
        feito.append("token antigo migrado para token.raw")
    if os.path.lexists(raw):
        if os.path.islink(raw):
            raise SystemExit("erro: %s e um symlink" % raw)
        try:
            token = _ler(raw)
        except (OSError, ValueError):
            token = ""
        if not RE_TOKEN.match(token):
            raise SystemExit("erro: %s existe mas nao tem 64 caracteres hex; apague-o para gerar outro" % raw)
    else:
        token = secrets.token_hex(32)
        feito.append("token gerado")
    # cru: sempre root:root 0600
    _escrever(raw, token, 0o600, 0)
    _escrever(os.path.join(dir_, "token.sha256"), hashlib.sha256(token.encode("ascii")).hexdigest(), 0o640, gid)
    feito.append("token.sha256 gravado")
    return feito


def main(argv):
    if len(argv) != 2:
        raise SystemExit("uso: preparar-token.py <diretorio>")
    try:
        gid = grp.getgrnam("nogroup").gr_gid
    except KeyError:
        gid = os.getgid() if os.geteuid() != 0 else grp.getgrnam("nobody").gr_gid
    for linha in preparar(argv[1], gid):
        print(linha)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
