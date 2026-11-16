#!/bin/bash
# Run on atheron as root, after the files were copied to /root/kindle-monitor-deploy/.
set -euo pipefail
S=/root/kindle-monitor-deploy
command -v /usr/bin/python3 >/dev/null
install -d -m 0755 /opt/kindle-monitor /etc/kindle-monitor
rm -rf /opt/kindle-monitor/server && cp -a "$S/server" /opt/kindle-monitor/server
chown -R root:root /opt/kindle-monitor && chmod -R go-w /opt/kindle-monitor
install -d -m 0755 /opt/kindle-monitor/deploy
install -m 0755 "$S/kindle-monitor-executor.py" /opt/kindle-monitor/deploy/kindle-monitor-executor.py
# Command token: created once, never printed (read it with: sudo head -1 /etc/kindle-monitor/token).
if [ ! -s /etc/kindle-monitor/token ]; then
  ( umask 077; /usr/bin/python3 -c 'import secrets; print(secrets.token_hex(32))' > /etc/kindle-monitor/token )
fi
chown root:nogroup /etc/kindle-monitor/token && chmod 0640 /etc/kindle-monitor/token
install -m 0644 "$S/config.atheron.json" /etc/kindle-monitor/config.json
install -m 0644 "$S/kindle-monitor.service" /etc/systemd/system/kindle-monitor.service
install -m 0644 "$S/kindle-monitor-executor.service" /etc/systemd/system/kindle-monitor-executor.service
install -m 0644 "$S/kindle-monitor-executor.path" /etc/systemd/system/kindle-monitor-executor.path
systemctl daemon-reload
systemctl enable kindle-monitor.service
systemctl enable --now kindle-monitor-executor.path
systemctl restart kindle-monitor.service   # enable --now does not restart a running service
sleep 4
systemctl is-active kindle-monitor.service
