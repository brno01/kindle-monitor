#!/bin/sh
# kindle-monitor supervisor. monitor-ligar.sh copies it to /var/tmp (RAM) and runs it from there,
# because USB drive mode unmounts /mnt/us and kills anything running from it (loop.sh, tailscaled).
# - starts loop.sh, and starts it again after it dies once /mnt/us is back;
# - the power button (powerd's screensaver event or the raw power key) stops everything;
# - whenever the loop is not running the touch screen is on, so the Kindle is never left without touch.
cd / || exit 1
D=/mnt/us/kindle-monitor
SUPF=/tmp/kindle-monitor-sup.pid
PIDF=/tmp/kindle-monitor.pid
STOPF=/tmp/kindle-monitor.stop
LOG=/tmp/kindle-monitor.log

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
finish() {
  kill $P1 $P2 2>/dev/null
  lp=$(loop_pid)
  [ -n "$lp" ] && kill "$lp" 2>/dev/null
  sleep 1
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
    touch_on
    if [ -f "$D/loop.sh" ]; then
      [ "$starts" -gt 0 ] && log "loop not running (USB drive mode or crash?), starting it again"
      setsid sh "$D/loop.sh" >/dev/null 2>&1 < /dev/null &
      starts=$((starts + 1))
      # back off if it keeps dying
      if [ "$starts" -gt 5 ]; then sleep 30; else sleep 5; fi
    fi
  fi
  sleep 2
done
