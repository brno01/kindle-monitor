#!/bin/sh
# kindle-monitor supervisor. monitor-ligar.sh copies it to /var/tmp (RAM) and runs it from there,
# because USB drive mode unmounts /mnt/us and kills anything running from it (loop.sh, tailscaled).
# - starts loop.sh, and starts it again after it dies once /mnt/us is back;
# - the power button (powerd's screensaver event or the raw power key) stops everything;
# - whenever the loop is not running the touch screen is on, so the Kindle is never left without touch.
cd / || exit 1
D=/mnt/us/kindle-monitor
LOCK_TOUCH=1
# shellcheck disable=SC1091
[ -f "$D/config.sh" ] && . "$D/config.sh"
SUPF=/tmp/kindle-monitor-sup.pid
PIDF=/tmp/kindle-monitor.pid
STOPF=/tmp/kindle-monitor.stop
LOG=/tmp/kindle-monitor.log
IMG=/tmp/kindle-monitor.png        # last image the loop drew
FBINK=/mnt/us/libkh/bin/fbink

log() {
  [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 20000 ] && : > "$LOG"
  echo "$(date '+%d/%m %H:%M:%S') sup: $*" >> "$LOG"
}

if [ -f "$SUPF" ] && kill -0 "$(cat "$SUPF")" 2>/dev/null; then exit 0; fi
echo $$ > "$SUPF"
rm -f "$STOPF"
trap '' HUP

loop_pid() { [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null && cat "$PIDF"; }
touch_on() { lipc-set-prop com.lab126.deviced enable_touch 1 2>/dev/null; }

P1=""
P2=""
G1=""
G2=""
FIFO=/tmp/kindle-monitor-touch.fifo

# touch reader (LOCK_TOUCH=buttons): evtest grabs the panel so the Kindle UI gets nothing;
# `script` gives it a pty so it prints line by line; read_taps turns each lift into "x y" for tap.sh
# one line per evtest event; a finger lift (tracking id -1) after a contact is one tap.
# The kernel drops a position event whose value did not change, so a tap on the same
# pixel as the previous one carries no X/Y: keep the last known position, never reset it.
read_taps() {
  cr=$(printf '\r')
  down=0; tx=""; ty=""
  while IFS= read -r line; do
    v=${line##* }; v=${v%"$cr"}
    case "$line" in
      *"code 57 "*)
        if [ "$v" -ge 0 ] 2>/dev/null; then down=1
        elif [ "$down" = 1 ]; then
          [ -n "$tx" ] && [ -n "$ty" ] && sh /var/tmp/kindle-monitor/tap.sh "$tx" "$ty"
          down=0
        fi ;;
      *"code 53 "*) tx=$v ;;
      *"code 54 "*) ty=$v ;;
    esac
  done
}
grab_alive() { pgrep -f 'evtest --grab /dev/input/event1' >/dev/null 2>&1; }
grab_start() {
  grab_alive && return 0
  grab_stop
  rm -f "$FIFO"; mkfifo "$FIFO" || return 1
  lipc-set-prop com.lab126.deviced enable_touch 1 2>/dev/null
  # `script` quits when its stdin ends, so feed it a pipe that never ends (a long sleep)
  ( sleep 2000000000 | script -q -f -c 'evtest --grab /dev/input/event1' /dev/null > "$FIFO" 2>/dev/null ) &
  G1=$!
  # parse in plain sh: busybox awk buffers a continuous stream, sh `read` does not
  read_taps < "$FIFO" &
  G2=$!
  log "touch reader started"
}
grab_stop() {
  kill $G1 $G2 2>/dev/null
  pkill -f 'evtest --grab /dev/input/event1' 2>/dev/null
  pkill -f 'sleep 2000000000' 2>/dev/null
  G1=""; G2=""; rm -f "$FIFO"
}

GUI_STOPPED=0
# the Kindle UI keeps repainting (clock, status bar) over the monitor even with the touch grabbed:
# stop it while the loop runs, bring it back whenever the loop is not running and on exit
gui_stop() {
  [ "${STOP_GUI:-0}" = 1 ] && [ "$GUI_STOPPED" = 0 ] || return 0
  stop lab126_gui >/dev/null 2>&1 || return 0
  GUI_STOPPED=1
  log "kindle UI stopped"
  # stopping the UI can wipe the screen to white after the loop's first draw; with a long interval
  # (economia: 5 min) the loop would not draw again for minutes, leaving a blank screen with the
  # touch panel grabbed. Redraw the last image now (needs /mnt/us, like the loop that drew it).
  [ -x "$FBINK" ] && [ -f "$IMG" ] && "$FBINK" -q -f -g file="$IMG" >/dev/null 2>&1 && log "redrew after UI stop"
}
gui_start() {
  [ "$GUI_STOPPED" = 1 ] || return 0
  start lab126_gui >/dev/null 2>&1; GUI_STOPPED=0; log "kindle UI started"
}

finish() {
  kill $P1 $P2 2>/dev/null
  grab_stop
  lp=$(loop_pid)
  [ -n "$lp" ] && kill "$lp" 2>/dev/null
  sleep 1
  gui_start
  touch_on
  lipc-set-prop com.lab126.powerd preventScreenSaver 0 2>/dev/null
  rm -f "$SUPF"
  log "stopped: $1"
  if [ "$1" = "power button" ]; then
    sleep 2
    # if powerd did not go to the screensaver, bring the library back so the screen matches the UI
    [ "$(lipc-get-prop com.lab126.powerd state 2>/dev/null)" = "active" ] && \
      lipc-set-prop com.lab126.appmgrd start app://com.lab126.booklet.home 2>/dev/null
  fi
  exit 0
}
trap 'finish TERM' TERM
trap 'finish INT' INT

# two independent detectors; both only use system binaries, never /mnt/us
lipc-wait-event com.lab126.powerd goingToScreenSaver >/dev/null 2>&1 &
P1=$!
dd if=/dev/input/event0 of=/dev/null bs=16 count=1 2>/dev/null &
P2=$!
log "started pid=$$ (button detectors $P1 $P2)"

starts=0
while :; do
  [ -f "$STOPF" ] && finish "stop requested"
  if ! kill -0 "$P1" 2>/dev/null || ! kill -0 "$P2" 2>/dev/null; then
    finish "power button"
  fi
  if [ -z "$(loop_pid)" ]; then
    grab_stop
    gui_start
    touch_on
    if [ -f "$D/loop.sh" ]; then
      [ "$starts" -gt 0 ] && log "loop not running (USB drive mode or crash?), starting it again"
      setsid sh "$D/loop.sh" >/dev/null 2>&1 < /dev/null &
      starts=$((starts + 1))
      # back off if it keeps dying
      if [ "$starts" -gt 5 ]; then sleep 30; else sleep 5; fi
    fi
  fi
  [ "$LOCK_TOUCH" = buttons ] && [ -n "$(loop_pid)" ] && grab_start
  # after the loop's first draw (FIRST_DELAY), the screen belongs to the monitor
  [ -n "$(loop_pid)" ] && [ -f /tmp/kindle-monitor.png ] && gui_stop
  sleep 2
done
