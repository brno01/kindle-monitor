#!/bin/sh
# kindle-monitor loop: keeps Tailscale up, fetches the status PNG and draws it with FBInk.
# Started by supervisor.sh (see monitor-ligar.sh). While it runs the touch screen is off;
# the power button stops it (handled by the supervisor), and so does monitor-desligar.sh.
D=/mnt/us/kindle-monitor
. "$D/config.sh"
F=/mnt/us/libkh/bin/fbink
TS=/mnt/us/tailscale
PIDF=/tmp/kindle-monitor.pid
LOG=/tmp/kindle-monitor.log
IMG=/tmp/kindle-monitor.png

if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then exit 0; fi
echo $$ > "$PIDF"
cleanup() {
  lipc-set-prop com.lab126.deviced enable_touch 1 2>/dev/null
  lipc-set-prop com.lab126.powerd preventScreenSaver 0 2>/dev/null
  rm -f "$PIDF"
}
trap '' HUP
trap 'log "got INT"; cleanup; exit 0' INT
trap 'log "got TERM"; cleanup; exit 0' TERM
trap 'log "exit"; cleanup' EXIT

log() {
  [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 20000 ] && : > "$LOG"
  echo "$(date '+%d/%m %H:%M:%S') $*" >> "$LOG"
}

ensure_ts() {
  pgrep tailscaled >/dev/null 2>&1 && return 0
  log "starting tailscaled"
  ( cd "$TS" && nohup ./tailscaled --tun=userspace-networking \
      --statedir="$TS/state" --state="$TS/state/tailscaled.state" \
      --socket=/tmp/tailscaled.sock --socks5-server=localhost:1055 \
      > "$TS/tailscaled.log" 2>&1 < /dev/null & )
  sleep 10
}

fetch() {
  rm -f "$IMG.new"
  curl -s -f -m 25 --socks5-hostname localhost:1055 -o "$IMG.new" "http://$SERVER/tela.png" || return 1
  [ "$(head -c 4 "$IMG.new" | od -An -tx1 | tr -d ' \n')" = "89504e47" ]
}

lipc-set-prop com.lab126.powerd preventScreenSaver 1 2>/dev/null
log "loop started pid=$$ server=$SERVER interval=${INTERVAL}s"
n=0
fails=0
# let the launcher app exit and the library repaint before the first draw (interruptible)
sleep "$FIRST_DELAY" &
wait $!
# from here on the screen belongs to the monitor: touch off, power button is the way out
# (supervisor.sh, running from RAM, watches the power button and turns touch back on)
if [ "${LOCK_TOUCH:-1}" = 1 ]; then
  lipc-set-prop com.lab126.deviced enable_touch 0 2>/dev/null && log "touch disabled"
fi
while :; do
  T0=$(date +%s)
  ensure_ts
  if fetch; then
    mv -f "$IMG.new" "$IMG"
    fails=0
    if [ $((n % FULL_EVERY)) -eq 0 ]; then
      "$F" -q -f -g file="$IMG" >/dev/null 2>&1
    else
      "$F" -q -g file="$IMG" >/dev/null 2>&1
    fi
    n=$((n + 1))
  else
    fails=$((fails + 1))
    log "fetch failed ($fails)"
    [ "$fails" -eq "$FAIL_NOTICE_AFTER" ] && "$F" -q -y -1 -x 0 "sem dados desde $(date +%H:%M)" >/dev/null 2>&1
  fi
  # interruptible sleep: a signal is handled right away instead of after the sleep ends
  # sleep only what is left of the interval, so the period stays close to INTERVAL
  left=$((INTERVAL - ($(date +%s) - T0)))
  [ "$left" -lt 0 ] && left=0
  sleep "$left" &
  wait $!
done
