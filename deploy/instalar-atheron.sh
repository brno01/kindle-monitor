#!/bin/bash
# Run on atheron as root, after the files were copied to /root/kindle-monitor-deploy/.
set -euo pipefail
S=/root/kindle-monitor-deploy
command -v /usr/bin/python3 >/dev/null
# The real config is local and not versioned (the repo only has config.atheron.example.json). Without it, stop.
CFG="$S/config.atheron.local.json"
[ -f "$CFG" ] || { echo "erro: falta $CFG (copie deploy/config.atheron.example.json para deploy/config.atheron.local.json e preencha os valores reais)" >&2; exit 1; }
# IP where the web service listens (key "bind"): a single IPv4, never 0.0.0.0 (the service is tailnet-only).
BIND=$(/usr/bin/python3 -I -c 'import ipaddress, json, sys
b = ipaddress.IPv4Address(json.load(open(sys.argv[1]))["bind"])
if b.is_unspecified or b.is_multicast:
    sys.exit("bind invalido")
print(b)' "$CFG")
install -d -m 0755 /opt/kindle-monitor /etc/kindle-monitor
rm -rf /opt/kindle-monitor/server && cp -a "$S/server" /opt/kindle-monitor/server
chown -R root:root /opt/kindle-monitor && chmod -R go-w /opt/kindle-monitor
install -d -m 0755 /opt/kindle-monitor/deploy
install -m 0755 "$S/kindle-monitor-executor.py" /opt/kindle-monitor/deploy/kindle-monitor-executor.py
# Command token. The raw token stays in token.raw (root 0600; copy it to the Kindle with
# `sudo head -1 /etc/kindle-monitor/token.raw`); the web service reads only token.sha256 (root:nogroup 0640).
# Generated only when there is no valid one; an invalid existing token aborts the install. Never printed.
/usr/bin/python3 -I "$S/preparar-token.py" /etc/kindle-monitor
install -m 0644 "$CFG" /etc/kindle-monitor/config.json
# /run/kindle-monitor is owned by root (the web service must not own it): create it BEFORE (re)starting anything.
install -m 0644 "$S/kindle-monitor.tmpfiles" /etc/tmpfiles.d/kindle-monitor.conf
systemd-tmpfiles --create /etc/tmpfiles.d/kindle-monitor.conf
# /var/lib/claude-uso for the Claude card: only when the `claude` user exists (otherwise the card shows n/d).
if getent passwd claude >/dev/null; then
    install -m 0644 "$S/kindle-monitor-claude.tmpfiles" /etc/tmpfiles.d/kindle-monitor-claude.conf
    systemd-tmpfiles --create /etc/tmpfiles.d/kindle-monitor-claude.conf
else
    echo "aviso: usuario claude nao existe; /var/lib/claude-uso nao foi criado (cartao Claude fica n/d)" >&2
fi
sed "s|@BIND@|$BIND|" "$S/kindle-monitor.service" > /etc/systemd/system/kindle-monitor.service
chmod 0644 /etc/systemd/system/kindle-monitor.service
install -m 0644 "$S/kindle-monitor-executor.service" /etc/systemd/system/kindle-monitor-executor.service
install -m 0644 "$S/kindle-monitor-executor.path" /etc/systemd/system/kindle-monitor-executor.path
install -m 0644 "$S/kindle-monitor-inventario.service" /etc/systemd/system/kindle-monitor-inventario.service
install -m 0644 "$S/kindle-monitor-inventario.timer" /etc/systemd/system/kindle-monitor-inventario.timer
systemctl daemon-reload
systemctl enable kindle-monitor.service
systemctl enable --now kindle-monitor-executor.path
systemctl enable --now kindle-monitor-inventario.timer   # service inventory for the Services page (root, every 15 s)
systemctl restart kindle-monitor.service   # enable --now does not restart a running service
sleep 4
systemctl is-active kindle-monitor.service
