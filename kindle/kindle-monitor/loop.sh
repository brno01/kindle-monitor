#!/bin/sh
# kindle-monitor loop: keeps Tailscale up, fetches the status PNG and draws it with FBInk.
# Started by supervisor.sh (see monitor-ligar.sh). Pages and the armed command button come
# from tap.sh; the power button stops everything (handled by the supervisor).
D=/mnt/us/kindle-monitor
[ -f "$D/config.sh" ] || { echo "kindle-monitor: $D/config.sh missing (copy config.example.sh to config.sh and set SERVER)" >&2; exit 1; }
. "$D/config.sh"
F=/mnt/us/libkh/bin/fbink
TS=/mnt/us/tailscale
PIDF=/tmp/kindle-monitor.pid
LOG=/tmp/kindle-monitor.log
IMG=/tmp/kindle-monitor.png
BTN=/tmp/kindle-monitor-botoes.txt
STF=/var/tmp/kindle-monitor/state
MODOF=/var/local/kindle-monitor/modo   # power profile written by tap.sh (ext3); only one of the three names
# config.sh's INTERVAL/FULL_EVERY are the fallbacks when the stored profile is missing or invalid
INTERVAL0=$INTERVAL
# Kindle status sent to the server (k* query params); config.sh may leave these out
KSTATUS_EVERY=${KSTATUS_EVERY:-30}
TS_EVERY=${TS_EVERY:-60}
WSYNC_FILE=${WSYNC_FILE:-}
FULL_EVERY0=$FULL_EVERY

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
# tap.sh sends USR1 after a tap: the interruptible sleep below ends and the next fetch is immediate
trap ':' USR1

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

# state is parsed field by field (never sourced): only known keys and validated values
read_state() {
  PAGINA=resumo; P=1; ARMADO=; ARMADO_ATE=0
  [ -f "$STF" ] || return 0
  while IFS='=' read -r k v; do
    case "$k" in
      PAGINA) case "$v" in ''|*[!a-z]*) ;; *) [ ${#v} -le 16 ] && PAGINA=$v ;; esac ;;
      P) case "$v" in ''|*[!0-9]*) ;; *) [ "$v" -ge 1 ] && [ "$v" -le 99 ] && P=$v ;; esac ;;
      ARMADO) case "$v" in ''|*[!a-z0-9:-]*) ;; *) ARMADO=$v ;; esac ;;
      ARMADO_ATE) case "$v" in ''|*[!0-9]*) ;; *) ARMADO_ATE=$v ;; esac ;;
    esac
  done < "$STF"
}

# power profile: only the three known names are accepted (the file is never sourced); the numbers
# come from config.sh's PERFIL_<name>="<interval> <flash period>", validated as positive integers
read_modo() {
  MODO=desempenho
  m=
  if [ -f "$MODOF" ]; then IFS= read -r m < "$MODOF"; fi
  case "$m" in desempenho|balanceado|economia) MODO=$m ;; esac
  INTERVAL=$INTERVAL0; FULL_EVERY=$FULL_EVERY0
  # shellcheck disable=SC2154  # PERFIL_* come from config.sh, sourced at the top
  case "$MODO" in
    desempenho) v=$PERFIL_desempenho ;;
    balanceado) v=$PERFIL_balanceado ;;
    economia) v=$PERFIL_economia ;;
  esac
  # shellcheck disable=SC2086
  set -- $v
  case "$1$2" in ''|*[!0-9]*) return 0 ;; esac
  [ "$1" -ge 1 ] && [ "$2" -ge 1 ] && { INTERVAL=$1; FULL_EVERY=$2; }
  return 0
}

# ---- the Kindle's own status: battery, Wi-Fi, Bluetooth, airplane mode, Tailscale path, Whispersync.
# Read every KSTATUS_EVERY s (each lipc call costs ~50 ms; at 1 s per cycle it would add up) and kept in
# variables, so the k* params stay identical between collections and the server's image cache keeps hitting.
# Only digits and the d/r/x path letter go into the URL: never SSID, MAC or device names.
KST_T=0; TS_T=0; LAT_RAW=
KB=; KC=; KTEMP=; KW=; KWC=; KA=; KBT=; KBC=; KTS=x; KLAT=; KWS=
digits() { printf '%s' "$1" | tr -dc '0-9-' | cut -c1-12; }
lp() { digits "$(lipc-get-prop "$1" "$2" 2>/dev/null)"; }

ts_path() {
  KTS=x
  l=$("$TS/tailscale" --socket=/tmp/tailscaled.sock status 2>/dev/null | awk -v ip="${SERVER%%:*}" '$1 == ip')
  case "$l" in *direct*) KTS=d ;; *relay*) KTS=r ;; esac
}

kstatus() {
  now=$(date +%s)
  [ $((now - KST_T)) -lt "$KSTATUS_EVERY" ] && return 0
  KST_T=$now
  KB=$(lp com.lab126.powerd battLevel)
  KC=$(lp com.lab126.powerd isCharging)
  KTEMP=$(lp com.lab126.powerd battTemperature)
  s=$(lipc-get-prop com.lab126.wifid signalStrength 2>/dev/null)
  KW=$(digits "${s%%/*}")
  case "$(lipc-get-prop com.lab126.wifid cmState 2>/dev/null)" in CONNECTED*) KWC=1 ;; *) KWC=0 ;; esac
  case "$(lp com.lab126.cmd wirelessEnable)" in 0) KA=1 ;; 1) KA=0 ;; *) KA= ;; esac
  case "$(lp com.lab126.btfd BTstate)" in 0) KBT=0 ;; '') KBT= ;; *) KBT=1 ;; esac
  KBC=$(lipc-hash-prop com.lab126.btfd ListConnected 2>/dev/null | grep -c 'is_connected = (1)')
  # time of the last PNG fetch, in ms (curl -w); sampled here so it changes only once per collection
  KLAT=$(printf '%s' "$LAT_RAW" | awk '/^[0-9.]+$/ { printf "%d", $1 * 1000 }')
  if [ $((now - TS_T)) -ge "$TS_EVERY" ]; then TS_T=$now; ts_path; fi
  KWS=
  if [ -n "$WSYNC_FILE" ] && [ -f "$WSYNC_FILE" ]; then KWS=$(digits "$(stat -c %Y "$WSYNC_FILE" 2>/dev/null)"); fi
  return 0
}

# local notice drawn with FBInk when the server cannot be reached (airplane mode, Wi-Fi off, atheron down):
# the server's image can never say "airplane mode on", so it is said here
offline_notice() {
  KST_T=0
  kstatus
  msg="sem dados desde $(date +%H:%M)"
  if [ "$KA" = 1 ]; then msg="$msg - modo aviao ligado"
  elif [ "$KWC" = 0 ]; then msg="$msg - wi-fi desconectado"
  fi
  [ -n "$KB" ] && msg="$msg - bateria $KB%"
  "$F" -q -y -1 -x 0 "$msg" >/dev/null 2>&1
}

# signature of what taps change (page/armed state and profile): a tap that lands while the
# loop is fetching or drawing sends USR1 when nothing is waiting, so it is detected here instead
sig() { cat "$STF" "$MODOF" 2>/dev/null | cksum; }

# page and armed button written by tap.sh
state() {
  read_state
  [ "$ARMADO_ATE" -ge "$(date +%s)" ] 2>/dev/null || ARMADO=
  Q="pagina=$PAGINA"
  [ "$PAGINA" = servicos ] && Q="$Q&p=$P"
  [ -n "$ARMADO" ] && Q="$Q&armado=$ARMADO"
  Q="$Q&modo=$MODO"
  Q="$Q&kb=$KB&kc=$KC&ktemp=$KTEMP&kw=$KW&kwc=$KWC&ka=$KA&kbt=$KBT&kbc=$KBC&kts=$KTS&klat=$KLAT&kf=$fails"
  Q="$Q&kt=$(date +%s)&kws=$KWS"
}

fetch() {
  state
  rm -f "$IMG.new"
  LAT_RAW=$(curl -s -f -m 25 --socks5-hostname localhost:1055 -o "$IMG.new" -w '%{time_total}' \
    "http://$SERVER/tela.png?$Q") || return 1
  [ "$(head -c 4 "$IMG.new" | od -An -tx1 | tr -d ' \n')" = "89504e47" ] || return 1
  # button layout for the same page, used by tap.sh; keep the old one if this fails
  curl -s -f -m 10 --socks5-hostname localhost:1055 -o "$BTN.new" "http://$SERVER/botoes.txt?$Q" && mv -f "$BTN.new" "$BTN"
  return 0
}

lipc-set-prop com.lab126.powerd preventScreenSaver 1 2>/dev/null
# a stale image would make the supervisor stop the Kindle UI before our first draw
rm -f "$IMG"
read_modo
log "loop started pid=$$ server=$SERVER interval=${INTERVAL}s mode=$MODO"
MODO_LOG=
n=0
fails=0   # also sent as kf (consecutive failures before this fetch)
# let the launcher app exit and the library repaint before the first draw (interruptible)
sleep "$FIRST_DELAY" &
wait $!
# from here on the screen belongs to the monitor: touch off, power button is the way out
# (supervisor.sh, running from RAM, watches the power button and turns touch back on)
# LOCK_TOUCH=1: touch fully off; LOCK_TOUCH=buttons: the supervisor grabs the touch panel and only the buttons answer
if [ "${LOCK_TOUCH:-1}" = 1 ]; then
  lipc-set-prop com.lab126.deviced enable_touch 0 2>/dev/null && log "touch disabled"
fi
while :; do
  T0=$(date +%s)
  SIG0=$(sig)
  read_modo
  if [ "$MODO" != "$MODO_LOG" ]; then
    log "mode $MODO interval=${INTERVAL}s"
    # profile changed: the next full flash comes one new period from now (n=0 flashes at once, only at startup)
    [ -n "$MODO_LOG" ] && n=1
    MODO_LOG=$MODO
  fi
  ensure_ts
  kstatus
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
    [ "$fails" -eq "$FAIL_NOTICE_AFTER" ] && offline_notice
  fi
  # interruptible sleep: a signal is handled right away instead of after the sleep ends
  # sleep only what is left of the interval, so the period stays close to INTERVAL
  # a tap or a profile change since the cycle began, or while it ran: skip the sleep. A profile
  # change from a tap is applied at once (the loop re-reads it at the top of the next cycle).
  read_modo
  state
  left=$((INTERVAL - ($(date +%s) - T0)))
  [ "$left" -lt 0 ] && left=0
  [ "$(sig)" != "$SIG0" ] && left=0
  # an armed command button expires after ARM_SECONDS: wake up then so the screen stops showing "confirm"
  if [ -n "$ARMADO" ]; then
    arm_left=$((ARMADO_ATE - $(date +%s) + 1))
    [ "$arm_left" -lt 0 ] && arm_left=0
    [ "$arm_left" -lt "$left" ] && left=$arm_left
  fi
  if [ "$left" -gt 0 ]; then
    sleep "$left" &
    wait $!
    kill $! 2>/dev/null   # woken by USR1: do not leave the long sleep behind
  fi
done
