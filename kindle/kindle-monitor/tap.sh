#!/bin/sh
# kindle-monitor tap handler. The supervisor's touch reader calls it with the screen
# coordinates of one tap: tap.sh X Y. It looks the tap up in the button layout the
# server sent (/tmp/kindle-monitor-botoes.txt, one "id tipo x y w h" per line),
# updates the page / armed state and wakes the loop so the screen follows at once.
# Commands need two taps: the first arms the button, the second (within ARM_SECONDS)
# sends it to the server with the token.
x=$1
y=$2
D=/mnt/us/kindle-monitor
STF=/tmp/kindle-monitor.state
BTN=/tmp/kindle-monitor-botoes.txt
PIDF=/tmp/kindle-monitor.pid
LOG=/tmp/kindle-monitor.log
log() { echo "$(date '+%d/%m %H:%M:%S') tap: $*" >> "$LOG"; }

case "$x$y" in ''|*[!0-9]*) exit 0 ;; esac
[ -f "$BTN" ] || exit 0

# debounce: ignore a second contact within 0.4 s (finger bounce)
now_cs=$(awk '{printf "%d", $1 * 100}' /proc/uptime)
last_cs=$(cat /tmp/kindle-monitor.lasttap 2>/dev/null || echo 0)
echo "$now_cs" > /tmp/kindle-monitor.lasttap
[ $((now_cs - last_cs)) -lt 40 ] && exit 0

hit=$(awk -v x="$x" -v y="$y" 'NF == 6 && $3 <= x && x < $3 + $5 && $4 <= y && y < $4 + $6 { print $1, $2; exit }' "$BTN")
[ -n "$hit" ] || exit 0
id=${hit% *}
tipo=${hit#* }
case "$id" in ''|*[!a-z:-]*) exit 0 ;; esac

ARM_SECONDS=6
[ -f "$D/config.sh" ] && . "$D/config.sh"
PAGINA=resumo
ARMADO=
ARMADO_ATE=0
[ -f "$STF" ] && . "$STF"
now=$(date +%s)

send() {
  tok=$(head -n 1 "$D/token" 2>/dev/null)
  case "$tok" in ''|*[!0-9a-f]*) log "no valid token, $1 not sent"; return 1 ;; esac
  code=$(curl -s -m 15 --socks5-hostname localhost:1055 -o /dev/null -w '%{http_code}' \
    -H 'Content-Type: application/json' -H "X-Kindle-Token: $tok" \
    -d "{\"acao\":\"$1\"}" "http://$SERVER/comando")
  log "sent $1 -> HTTP $code"
}

case "$id" in
  atualizar) log "refresh" ;;
  pagina:resumo | pagina:detalhes | pagina:comandos)
    PAGINA=${id#pagina:}; ARMADO=; ARMADO_ATE=0; log "page $PAGINA" ;;
  *)
    if [ "$tipo" = comando ]; then
      if [ "$ARMADO" = "$id" ] && [ "$ARMADO_ATE" -ge "$now" ] 2>/dev/null; then
        ARMADO=; ARMADO_ATE=0
        send "$id"
      else
        ARMADO=$id; ARMADO_ATE=$((now + ARM_SECONDS)); log "armed $id"
      fi
    fi ;;
esac

printf 'PAGINA=%s\nARMADO=%s\nARMADO_ATE=%s\n' "$PAGINA" "$ARMADO" "$ARMADO_ATE" > "$STF.new" && mv -f "$STF.new" "$STF"
[ -f "$PIDF" ] && kill -USR1 "$(cat "$PIDF")" 2>/dev/null
exit 0
