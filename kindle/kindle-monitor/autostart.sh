#!/bin/sh
# kindle-monitor autostart: espera o Wi-Fi e mantém de pé
#   - o tailscaled (mesmos parâmetros do loop.sh; o SSH do Tailscale já está ligado no estado dele), e
#   - o dropbear do Jobman na LAN, porta 22, só chave (sem senha, sem encaminhamento).
# Disparado por /mnt/us/emergency.sh no boot e copiado para /var/tmp antes de rodar. O modo disco do USB
# desmonta /mnt/us e mata o que roda de lá; este laço sobrevive e religa tudo quando /mnt/us volta.
# Desligar: crie /mnt/us/kindle-monitor/SEM_AUTOSTART (o laço sai em até INTERVALO segundos).
trap '' HUP

TS=${AUTOSTART_TS:-/mnt/us/tailscale}
JM=${AUTOSTART_JOBMAN:-/mnt/us/jobman}
STOP=${AUTOSTART_STOP:-/mnt/us/kindle-monitor/SEM_AUTOSTART}
RUNDIR=${AUTOSTART_RUNDIR:-/var/tmp/kindle-autostart}
LOG=${AUTOSTART_LOG:-/var/tmp/kindle-autostart.log}
ROOT_HOME=${AUTOSTART_ROOT_HOME:-/tmp/root}
INTERVALO=${AUTOSTART_INTERVALO:-60}
# o firewall do Kindle é "INPUT DROP": a 22 do wlan0 só abre para o atheron (o kindle-lan sempre salta por ele)
SSH_DE=${AUTOSTART_SSH_DE:-192.0.2.10}
ESPERA_WIFI=${AUTOSTART_ESPERA_WIFI:-60}   # tentativas de 5 s (5 min)
UMA_VEZ=${AUTOSTART_UMA_VEZ:-0}            # 1 = uma rodada só (testes)

DB_SRC=$JM/bin/dropbearmulti
HOSTKEY_SRC=$JM/ssh/etc/dropbear/dropbear_ed25519_host_key
AK_SRC=$JM/ssh/etc/dropbear/authorized_keys
DB=$RUNDIR/dropbearmulti
HOSTKEY=$RUNDIR/dropbear_ed25519_host_key
PIDF=$RUNDIR/autostart.pid

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

mkdir -p "$RUNDIR" && chmod 700 "$RUNDIR"
# uma instância só
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then exit 0; fi
echo $$ > "$PIDF"
# log com teto de ~64 KB
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 65536 ]; then mv -f "$LOG" "$LOG.1"; fi
log "início (pid $$)"

userstore_ok() { [ -x "$TS/tailscaled" ]; }
wifi_ok() { [ "$(lipc-get-prop com.lab126.wifid cmState 2>/dev/null)" = CONNECTED ]; }
dropbear_ouvindo() { netstat -tln 2>/dev/null | grep -qE '[:.]22[[:space:]]'; }

garantir_tailscaled() {
  pgrep tailscaled >/dev/null 2>&1 && return 0
  userstore_ok || return 1
  log "subindo tailscaled"
  ( cd "$TS" && setsid ./tailscaled --tun=userspace-networking \
      --statedir="$TS/state" --state="$TS/state/tailscaled.state" \
      --socket=/tmp/tailscaled.sock --socks5-server=localhost:1055 \
      >> "$TS/tailscaled.log" 2>&1 < /dev/null & )
  return 0
}

# o dropbear roda de cópias em /var/tmp (binário e chave de host) para sobreviver ao modo disco do USB
copiar_dropbear() {
  if [ ! -x "$DB" ]; then
    [ -f "$DB_SRC" ] || return 1
    cp "$DB_SRC" "$DB.novo" && chmod 755 "$DB.novo" && mv -f "$DB.novo" "$DB" || return 1
  fi
  if [ ! -s "$HOSTKEY" ]; then
    [ -s "$HOSTKEY_SRC" ] || return 1
    cp "$HOSTKEY_SRC" "$HOSTKEY.novo" && chmod 600 "$HOSTKEY.novo" && mv -f "$HOSTKEY.novo" "$HOSTKEY" || return 1
  fi
}

# o home do root é /tmp/root (tmpfs, zera no boot). O dropbear recusa authorized_keys se o home, o .ssh
# ou o arquivo aceitarem escrita de grupo/outros; /mnt/us é 777, por isso copiamos.
preparar_chaves() {
  [ -s "$AK_SRC" ] || { [ -s "$ROOT_HOME/.ssh/authorized_keys" ]; return; }
  mkdir -p "$ROOT_HOME/.ssh" || return 1
  chmod go-w "$ROOT_HOME" && chmod 700 "$ROOT_HOME/.ssh" || return 1
  cp "$AK_SRC" "$ROOT_HOME/.ssh/authorized_keys.novo" && chmod 600 "$ROOT_HOME/.ssh/authorized_keys.novo" \
    && mv -f "$ROOT_HOME/.ssh/authorized_keys.novo" "$ROOT_HOME/.ssh/authorized_keys"
}

garantir_dropbear() {
  dropbear_ouvindo && return 0
  copiar_dropbear || return 1
  preparar_chaves || return 1
  log "subindo dropbear (porta 22, só chave)"
  # -s/-g: sem senha (nem para o root); -j/-k: sem encaminhamento de porta. Sem -F: ele mesmo vira daemon.
  "$DB" dropbear -r "$HOSTKEY" -p 22 -s -g -j -k >> "$LOG" 2>&1
}

# mesma regra que o Jobman cria ao subir o SSH dele, mas presa à origem SSH_DE. -C antes de -A: sem duplicar.
# O laço confere a cada rodada, porque o Kindle pode recarregar o firewall (troca de rede, por exemplo).
garantir_firewall() {
  iptables -C INPUT -i wlan0 -s "$SSH_DE" -p tcp --dport 22 -j ACCEPT 2>/dev/null && return 0
  log "liberando a 22 no wlan0 para $SSH_DE"
  iptables -A INPUT -i wlan0 -s "$SSH_DE" -p tcp --dport 22 -j ACCEPT
}

# no boot o Wi-Fi demora: espera até ESPERA_WIFI x 5 s
i=0
while ! wifi_ok && [ "$i" -lt "$ESPERA_WIFI" ]; do sleep 5; i=$((i + 1)); done
wifi_ok || log "Wi-Fi ainda sem conexão; seguindo mesmo assim"

falha_ts=0; falha_db=0; falha_fw=0
while :; do
  if [ -f "$STOP" ]; then log "SEM_AUTOSTART encontrado: saindo"; rm -f "$PIDF"; exit 0; fi
  if garantir_tailscaled; then falha_ts=0
  elif [ "$falha_ts" = 0 ]; then log "tailscaled: /mnt/us indisponível (modo disco do USB?)"; falha_ts=1; fi
  if garantir_dropbear; then falha_db=0
  elif [ "$falha_db" = 0 ]; then log "dropbear: não subiu (arquivos do Jobman ausentes?)"; falha_db=1; fi
  if garantir_firewall; then falha_fw=0
  elif [ "$falha_fw" = 0 ]; then log "firewall: não consegui liberar a 22 para $SSH_DE"; falha_fw=1; fi
  [ "$UMA_VEZ" = 1 ] && { rm -f "$PIDF"; exit 0; }
  sleep "$INTERVALO"
done
