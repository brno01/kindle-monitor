#!/bin/bash
# Run on atheron as root, after the files were copied to /root/kindle-monitor-deploy/.
set -euo pipefail
S=/root/kindle-monitor-deploy
command -v /usr/bin/python3 >/dev/null
install -d -m 0755 /opt/kindle-monitor /etc/kindle-monitor
rm -rf /opt/kindle-monitor/server && cp -a "$S/server" /opt/kindle-monitor/server
chown -R root:root /opt/kindle-monitor && chmod -R go-w /opt/kindle-monitor
install -m 0644 "$S/config.atheron.json" /etc/kindle-monitor/config.json
install -m 0644 "$S/kindle-monitor.service" /etc/systemd/system/kindle-monitor.service
systemctl daemon-reload
systemctl enable kindle-monitor.service
systemctl restart kindle-monitor.service   # enable --now does not restart a running service
sleep 4
systemctl is-active kindle-monitor.service
