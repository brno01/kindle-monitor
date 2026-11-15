#!/bin/sh
# Name: Monitor Ligar
# Author: kindle-monitor
L=/tmp/kindle-monitor.log
echo "$(date '+%d/%m %H:%M:%S') scriptlet ligar rodou (pid $$)" >> "$L"
if [ -f /tmp/kindle-monitor-sup.pid ] && kill -0 "$(cat /tmp/kindle-monitor-sup.pid)" 2>/dev/null; then
  echo "Monitor ja esta ligado."
  exit 0
fi
# the supervisor runs from RAM so USB drive mode (which unmounts /mnt/us) cannot kill it
mkdir -p /var/tmp/kindle-monitor && cp /mnt/us/kindle-monitor/supervisor.sh /var/tmp/kindle-monitor/supervisor.sh
( setsid nohup sh /var/tmp/kindle-monitor/supervisor.sh >/dev/null 2>&1 < /dev/null & )
sleep 3
if [ -f /tmp/kindle-monitor-sup.pid ] && kill -0 "$(cat /tmp/kindle-monitor-sup.pid)" 2>/dev/null; then
  echo "Monitor ligado. O toque fica desligado; para sair, aperte o botao de energia."
else
  echo "Falhou ao ligar. Veja /tmp/kindle-monitor.log"
fi
