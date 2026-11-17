#!/bin/sh
# kindle-monitor tap handler. The supervisor's touch reader calls it with the screen
# coordinates of one tap: tap.sh X Y. It looks the tap up in the button layout the
# server sent (/tmp/kindle-monitor-botoes.txt, one "id tipo x y w h" per line),
# updates the page / armed state and wakes the loop so the screen follows at once.
# Commands need two taps: the first arms the button, the second (within ARM_SECONDS)
# sends it to the server with the token (kept in /var/local, see TOKEN).
x=$1
y=$2
D=/mnt/us/kindle-monitor
STF=/var/tmp/kindle-monitor/state
TOKEN=/var/local/kindle-monitor/token   # ext3, root 0600; never on the FAT /mnt/us
MODOF=/var/local/kindle-monitor/modo    # power profile, ext3 (survives reboot and USB drive mode); only the name
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

# a tap inside a button wins; otherwise the nearest button within SLOP pixels (e-ink touch lands a little off)
hit=$(awk -v x="$x" -v y="$y" -v slop=24 'NF == 6 {
    dx = 0; if (x < $3) dx = $3 - x; else if (x >= $3 + $5) dx = x - ($3 + $5 - 1)
    dy = 0; if (y < $4) dy = $4 - y; else if (y >= $4 + $6) dy = y - ($4 + $6 - 1)
    d = dx > dy ? dx : dy
    if (d <= slop && (best == "" || d < bestd)) { best = $1 " " $2; bestd = d }
  } END { if (best != "") print best }' "$BTN")
log "touch x=$x y=$y -> ${hit:-nothing}"
[ -n "$hit" ] || exit 0
id=${hit% *}
tipo=${hit#* }
case "$id" in ''|*[!a-z0-9:-]*) exit 0 ;; esac

ARM_SECONDS=6
[ -f "$D/config.sh" ] && . "$D/config.sh"
# state is parsed field by field (never sourced): only known keys and validated values
read_state() {
  PAGINA=resumo; P=1; ARMADO=; ARMADO_ATE=0
  [ -f "$STF" ] || return 0
  while IFS='=' read -r k v; do
    case "$k" in
      PAGINA) case "$v" in resumo|servicos|detalhes|comandos) PAGINA=$v ;; esac ;;
      P) case "$v" in ''|*[!0-9]*) ;; *) [ "$v" -ge 1 ] && [ "$v" -le 99 ] && P=$v ;; esac ;;
      ARMADO) case "$v" in ''|*[!a-z0-9:-]*) ;; *) ARMADO=$v ;; esac ;;
      ARMADO_ATE) case "$v" in ''|*[!0-9]*) ;; *) ARMADO_ATE=$v ;; esac ;;
    esac
  done < "$STF"
}
read_state
now=$(date +%s)

send() {
  tok=$(head -n 1 "$TOKEN" 2>/dev/null)
  case "$tok" in ''|*[!0-9a-f]*) log "no valid token, $1 not sent"; return 1 ;; esac
  [ ${#tok} -eq 64 ] || { log "no valid token, $1 not sent"; return 1; }
  # the token header goes through stdin (-K -), so it never shows up in /proc/*/cmdline
  code=$(printf 'header = "X-Kindle-Token: %s"\n' "$tok" | curl -s -m 15 -K - --socks5-hostname localhost:1055 \
    -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"acao\":\"$1\"}" "http://$SERVER/comando")
  log "sent $1 -> HTTP $code"
}

case "$id" in
  atualizar) log "refresh" ;;
  pagina:resumo | pagina:servicos | pagina:detalhes | pagina:comandos | pagina:claude)
    PAGINA=${id#pagina:}; P=1; ARMADO=; ARMADO_ATE=0; log "page $PAGINA" ;;
  modo:desempenho | modo:balanceado | modo:economia)
    # single tap, local: store the profile atomically; the loop re-reads it on the wake-up below
    nome=${id#modo:}
    mkdir -p /var/local/kindle-monitor
    printf '%s\n' "$nome" > "$MODOF.new" && chmod 0644 "$MODOF.new" && mv -f "$MODOF.new" "$MODOF"
    ARMADO=; ARMADO_ATE=0; log "mode $nome" ;;
  servicos:anterior)
    [ "$P" -gt 1 ] && P=$((P - 1)); ARMADO=; ARMADO_ATE=0; log "services page $P" ;;
  servicos:proxima)
    [ "$P" -lt 99 ] && P=$((P + 1)); ARMADO=; ARMADO_ATE=0; log "services page $P" ;;
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

mkdir -p /var/tmp/kindle-monitor
printf 'PAGINA=%s\nP=%s\nARMADO=%s\nARMADO_ATE=%s\n' "$PAGINA" "$P" "$ARMADO" "$ARMADO_ATE" > "$STF.new" && mv -f "$STF.new" "$STF"
[ -f "$PIDF" ] && kill -USR1 "$(cat "$PIDF")" 2>/dev/null
exit 0
