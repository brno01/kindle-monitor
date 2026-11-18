#!/bin/bash
# Roda no nomad. Instala no Kindle o autostart do Tailscale + SSH da LAN (dropbear do Jobman, só chave).
# Uso: bash deploy/instalar-autostart-kindle.sh [--check|--desfazer]
#   --check     só confere (flags do dropbear do Jobman, o que já existe no Kindle); não grava nada
#   (nada)      grava /mnt/us/kindle-monitor/autostart.sh e /mnt/us/emergency.sh e roda uma vez, sem reiniciar
#   --desfazer  cria SEM_AUTOSTART, apaga /mnt/us/emergency.sh e o autostart.sh (o dropbear em pé só some
#               no próximo reboot)
# Acesso: KINDLE (padrão root@kindle-monitor, Tailscale SSH; pede o login do navegador se o check venceu).
# Nunca mexe em rootfs, /etc/upstart, KPM ou Jobman: só arquivos novos em /mnt/us.
set -euo pipefail
K=${KINDLE:-root@kindle-monitor}
AQUI=$(cd "$(dirname "$0")/.." && pwd)
MODO=${1:-aplicar}
k() { ssh -o ConnectTimeout=20 "$K" "$@"; }

echo "==> Kindle: $K"
case "$MODO" in
  --desfazer)
    # shellcheck disable=SC2016  # expande no Kindle, de propósito
    k 'touch /mnt/us/kindle-monitor/SEM_AUTOSTART; rm -f /mnt/us/emergency.sh /mnt/us/kindle-monitor/autostart.sh
       P=/var/tmp/kindle-autostart/autostart.pid; [ -f $P ] && kill "$(cat $P)" 2>/dev/null; rm -f $P
       pkill -f "/var/tmp/kindle-autostart/dropbearmulti dropbear" 2>/dev/null
       while iptables -D INPUT -i wlan0 -s 192.0.2.10 -p tcp --dport 22 -j ACCEPT 2>/dev/null; do :; done
       echo "desfeito: laço e dropbear parados, regra da 22 removida, arquivos apagados (o tailscaled segue com o monitor)"'
    exit 0 ;;
  --check|aplicar) ;;
  *) echo "uso: $0 [--check|--desfazer]" >&2; exit 2 ;;
esac

echo "==> Flags do dropbear do Jobman (precisa de -r -p -s -g -j -k)"
ajuda=$(k '/mnt/us/jobman/bin/dropbearmulti dropbear -h 2>&1' || true)
falta=""
for f in r p s g j k; do printf '%s\n' "$ajuda" | grep -qE "^[[:space:]]*-${f}[[:space:]]" || falta="$falta -$f"; done
if [ -n "$falta" ]; then echo "  FALTA no dropbear do Jobman:$falta. Nada foi gravado." >&2; exit 1; fi
echo "  ok"

echo "==> Estado atual"
k 'ls -la /mnt/us/emergency.sh /mnt/us/kindle-monitor/autostart.sh /mnt/us/kindle-monitor/SEM_AUTOSTART 2>&1 | sed "s/^/  /"; pgrep tailscaled >/dev/null && echo "  tailscaled rodando" || echo "  tailscaled parado"; netstat -tln | grep -qE "[:.]22[[:space:]]" && echo "  porta 22 ouvindo" || echo "  porta 22 fechada"'
if k 'test -f /mnt/us/emergency.sh' && ! k 'grep -q kindle-monitor /mnt/us/emergency.sh'; then
  echo "  já existe um /mnt/us/emergency.sh que NÃO é deste projeto: nada foi gravado." >&2; exit 1
fi
[ "$MODO" = --check ] && { echo "(--check: nada foi gravado)"; exit 0; }

echo "==> Gravando (só /mnt/us)"
k 'cat > /mnt/us/kindle-monitor/autostart.sh.novo && mv -f /mnt/us/kindle-monitor/autostart.sh.novo /mnt/us/kindle-monitor/autostart.sh' < "$AQUI/kindle/kindle-monitor/autostart.sh"
k 'cat > /mnt/us/emergency.sh.novo && mv -f /mnt/us/emergency.sh.novo /mnt/us/emergency.sh' < "$AQUI/kindle/emergency.sh"
k 'rm -f /mnt/us/kindle-monitor/SEM_AUTOSTART'
echo "  sha256 local:  $(sha256sum "$AQUI/kindle/kindle-monitor/autostart.sh" | cut -c1-16)  $(sha256sum "$AQUI/kindle/emergency.sh" | cut -c1-16)"
echo "  sha256 Kindle: $(k 'sha256sum /mnt/us/kindle-monitor/autostart.sh /mnt/us/emergency.sh' | cut -c1-16 | tr '\n' ' ')"

echo "==> Rodando uma vez agora (sem reiniciar)"
# shellcheck disable=SC2016  # expande no Kindle, de propósito
k 'P=/var/tmp/kindle-autostart/autostart.pid; [ -f $P ] && kill "$(cat $P)" 2>/dev/null; rm -f $P   # para o laço antigo (código velho)
   sh /mnt/us/emergency.sh; sleep 8; iptables -C INPUT -i wlan0 -s 192.0.2.10 -p tcp --dport 22 -j ACCEPT 2>/dev/null && echo "22 liberada no wlan0 para o atheron" || echo "22 NÃO liberada"; echo "-- log:"; tail -5 /var/tmp/kindle-autostart.log; netstat -tln | grep -qE "[:.]22[[:space:]]" && echo "porta 22 ouvindo" || echo "porta 22 FECHADA"'
echo
echo "Agora, no nomad (chave do root no agent): ssh kindle-lan true && echo ok-kindle-lan"
echo "Depois teste o boot: reinicie o Kindle SEM tocar na tela durante 'Jobman Recovery' (10 s) e espere ~3 min."
