#!/bin/sh
# Name: Monitor Desligar
# Author: kindle-monitor
touch /tmp/kindle-monitor.stop
if [ -f /tmp/kindle-monitor-sup.pid ] && kill -0 "$(cat /tmp/kindle-monitor-sup.pid)" 2>/dev/null; then
  kill "$(cat /tmp/kindle-monitor-sup.pid)"
  echo "Monitor desligado."
elif [ -f /tmp/kindle-monitor.pid ] && kill -0 "$(cat /tmp/kindle-monitor.pid)" 2>/dev/null; then
  kill "$(cat /tmp/kindle-monitor.pid)"
  echo "Monitor desligado."
else
  echo "Monitor nao estava ligado."
fi
lipc-set-prop com.lab126.deviced enable_touch 1 2>/dev/null
