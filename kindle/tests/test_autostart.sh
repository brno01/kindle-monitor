#!/bin/bash
# Testes do autostart do Kindle (emergency.sh + autostart.sh) com stubs no PATH. Nada toca no Kindle.
# Uso: bash kindle/tests/test_autostart.sh
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd)
FALHAS=0; N=0
ok()   { N=$((N + 1)); echo "ok    $*"; }
falha(){ N=$((N + 1)); FALHAS=$((FALHAS + 1)); echo "FALHA $*"; }
check(){ local d=$1; shift; if "$@"; then ok "$d"; else falha "$d"; fi; }

novo_ambiente() {
  T=$(mktemp -d); mkdir -p "$T/bin" "$T/us/tailscale/state" "$T/us/jobman/bin" "$T/us/jobman/ssh/etc/dropbear" \
    "$T/us/kindle-monitor" "$T/var" "$T/root"
  chmod 777 "$T/root"
  # stubs
  printf '#!/bin/sh\necho "${WIFI:-CONNECTED}"\n' > "$T/bin/lipc-get-prop"
  printf '#!/bin/sh\n[ -f "%s/ts.rodando" ]\n' "$T" > "$T/bin/pgrep"
  printf '#!/bin/sh\n[ -f "%s/db.ouvindo" ] && echo "tcp 0 0 0.0.0.0:22 0.0.0.0:* LISTEN"\necho "tcp 0 0 127.0.0.1:1055 0.0.0.0:* LISTEN"\n' "$T" > "$T/bin/netstat"
  printf '#!/bin/sh\necho "$*" >> "%s/setsid.args"\n"$@"\n' "$T" > "$T/bin/setsid"
  # iptables: -C passa só se a regra já foi posta; -A grava os argumentos e marca a regra
  printf '#!/bin/sh\ncase "$1" in -C) [ -f "%s/fw.ok" ];; -A) echo "$*" >> "%s/iptables.args"; touch "%s/fw.ok";; *) exit 1;; esac\n' "$T" "$T" "$T" > "$T/bin/iptables"
  printf '#!/bin/sh\necho "$*" > "%s/tailscaled.args"\n' "$T" > "$T/us/tailscale/tailscaled"
  printf '#!/bin/sh\necho "$*" > "%s/dropbear.args"\n' "$T" > "$T/us/jobman/bin/dropbearmulti"
  chmod +x "$T"/bin/* "$T/us/tailscale/tailscaled" "$T/us/jobman/bin/dropbearmulti"
  echo "ssh-ed25519 AAAATESTE nomad-kindle-monitor" > "$T/us/jobman/ssh/etc/dropbear/authorized_keys"
  echo "HOSTKEY-FALSA" > "$T/us/jobman/ssh/etc/dropbear/dropbear_ed25519_host_key"
  chmod 777 "$T/us/jobman/ssh/etc/dropbear/authorized_keys"
  export PATH="$T/bin:$PATH" AUTOSTART_TS="$T/us/tailscale" AUTOSTART_JOBMAN="$T/us/jobman" \
    AUTOSTART_STOP="$T/us/kindle-monitor/SEM_AUTOSTART" AUTOSTART_RUNDIR="$T/var/kindle-autostart" \
    AUTOSTART_LOG="$T/var/autostart.log" AUTOSTART_ROOT_HOME="$T/root" AUTOSTART_UMA_VEZ=1 \
    AUTOSTART_ESPERA_WIFI=0 AUTOSTART_SRC="$HERE/kindle-monitor/autostart.sh" AUTOSTART_RUN="$T/var/run.sh"
}
modo() { stat -c %a "$1"; }

# 1. boot limpo: sobe tailscaled e dropbear, prepara as chaves
novo_ambiente
sh "$HERE/kindle-monitor/autostart.sh"; sleep 0.3
check "tailscaled sobe com os parâmetros do loop.sh" grep -q -- '--tun=userspace-networking --statedir=.*/state --state=.*/tailscaled.state --socket=/tmp/tailscaled.sock --socks5-server=localhost:1055' "$T/tailscaled.args"
check "dropbear: só chave, sem encaminhamento, porta 22, chave de host copiada" grep -qx -- "dropbear -r $T/var/kindle-autostart/dropbear_ed25519_host_key -p 22 -s -g -j -k" "$T/dropbear.args"
check "dropbear roda da cópia em /var/tmp (sobrevive ao USB)" test -x "$T/var/kindle-autostart/dropbearmulti"
check "chave de host copiada com 600" test "$(modo "$T/var/kindle-autostart/dropbear_ed25519_host_key")" = 600
check "authorized_keys copiado com 600" test "$(modo "$T/root/.ssh/authorized_keys")" = 600
check ".ssh com 700" test "$(modo "$T/root/.ssh")" = 700
check "home do root sem escrita de grupo/outros" test "$(( 0$(modo "$T/root") & 022 ))" = 0
check "conteúdo das chaves igual ao do Jobman" cmp -s "$T/root/.ssh/authorized_keys" "$T/us/jobman/ssh/etc/dropbear/authorized_keys"
check "pid apagado ao sair (uma rodada)" test ! -f "$T/var/kindle-autostart/autostart.pid"
check "firewall: libera a 22 no wlan0 só para o atheron" grep -qx -- "-A INPUT -i wlan0 -s 192.0.2.10 -p tcp --dport 22 -j ACCEPT" "$T/iptables.args"
sh "$HERE/kindle-monitor/autostart.sh"
check "firewall: segunda rodada não duplica a regra" test "$(wc -l < "$T/iptables.args")" = 1
rm -rf "$T"

# 1b. origem configurável
novo_ambiente; AUTOSTART_SSH_DE=10.9.9.9 sh "$HERE/kindle-monitor/autostart.sh"
check "firewall: AUTOSTART_SSH_DE muda a origem" grep -q -- "-s 10.9.9.9 " "$T/iptables.args"
rm -rf "$T"

# 2. já está tudo de pé: não sobe nada de novo
novo_ambiente; touch "$T/ts.rodando" "$T/db.ouvindo"
sh "$HERE/kindle-monitor/autostart.sh"
check "tailscaled rodando: não sobe outro" test ! -f "$T/tailscaled.args"
check "porta 22 ouvindo: não sobe outro dropbear" test ! -f "$T/dropbear.args"
rm -rf "$T"

# 3. modo disco do USB (/mnt/us fora): registra uma vez e não quebra
novo_ambiente; rm -rf "$T/us/tailscale" "$T/us/jobman"
sh "$HERE/kindle-monitor/autostart.sh"
check "sem /mnt/us: loga tailscaled indisponível" grep -q 'tailscaled: /mnt/us indisponível' "$T/var/autostart.log"
check "sem arquivos do Jobman: loga dropbear não subiu" grep -q 'dropbear: não subiu' "$T/var/autostart.log"
rm -rf "$T"

# 4. trava SEM_AUTOSTART
novo_ambiente; touch "$AUTOSTART_STOP"
sh "$HERE/kindle-monitor/autostart.sh"
check "SEM_AUTOSTART: sai sem subir nada" test ! -f "$T/tailscaled.args" -a ! -f "$T/dropbear.args"
check "SEM_AUTOSTART: registra a saída" grep -q 'SEM_AUTOSTART' "$T/var/autostart.log"
sh "$HERE/emergency.sh"
check "emergency.sh com SEM_AUTOSTART: não copia nem dispara" test ! -f "$AUTOSTART_RUN" -a ! -f "$T/setsid.args"
rm -rf "$T"

# 5. emergency.sh: copia para /var/tmp, dispara em segundo plano e sai na hora
novo_ambiente
inicio=$(date +%s%N); sh "$HERE/emergency.sh"; rc=$?; fim=$(date +%s%N)
check "emergency.sh sai com 0" test "$rc" = 0
check "emergency.sh sai rápido (< 1 s)" test $(( (fim - inicio) / 1000000 )) -lt 1000
check "emergency.sh copia o autostart para /var/tmp" cmp -s "$AUTOSTART_RUN" "$HERE/kindle-monitor/autostart.sh"
sleep 0.5
check "emergency.sh dispara com setsid a cópia" grep -q "sh $AUTOSTART_RUN" "$T/setsid.args"
rm -rf "$T"

# 6. emergency.sh sem o autostart instalado: não faz nada
novo_ambiente; AUTOSTART_SRC="$T/nao-existe" sh "$HERE/emergency.sh"
check "sem autostart.sh: emergency.sh não faz nada" test ! -f "$AUTOSTART_RUN"
rm -rf "$T"

# 7. uma instância só
novo_ambiente; mkdir -p "$AUTOSTART_RUNDIR"; sleep 30 & echo $! > "$AUTOSTART_RUNDIR/autostart.pid"
sh "$HERE/kindle-monitor/autostart.sh"
check "outra instância viva: sai sem fazer nada" test ! -f "$T/tailscaled.args"
kill %1 2>/dev/null; rm -rf "$T"

# sintaxe e lint (sh do busybox: POSIX)
check "sh -n emergency.sh" sh -n "$HERE/emergency.sh"
check "sh -n autostart.sh" sh -n "$HERE/kindle-monitor/autostart.sh"
if command -v shellcheck >/dev/null; then
  check "shellcheck -s sh" shellcheck -s sh "$HERE/emergency.sh" "$HERE/kindle-monitor/autostart.sh"
fi
echo "== $((N - FALHAS))/$N ok, $FALHAS falha(s)"
[ "$FALHAS" = 0 ]
