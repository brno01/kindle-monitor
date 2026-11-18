#!/bin/sh
# kindle-monitor: no boot, sobe o Tailscale e o SSH da LAN (dropbear do Jobman, só chave).
# Instalado em /mnt/us/emergency.sh. Quem chama é o /etc/upstart/kmc.conf do jailbreak, em todo boot
# ("start on framework_ready"), com /bin/sh. Este arquivo só dispara o autostart em segundo plano e sai
# na hora: nada aqui pode travar ou atrasar o boot.
# Desligar: crie /mnt/us/kindle-monitor/SEM_AUTOSTART, ou apague este arquivo (pelo USB, se preciso).
SRC=${AUTOSTART_SRC:-/mnt/us/kindle-monitor/autostart.sh}
RUN=${AUTOSTART_RUN:-/var/tmp/kindle-autostart.sh}
STOP=${AUTOSTART_STOP:-/mnt/us/kindle-monitor/SEM_AUTOSTART}

[ -f "$STOP" ] && exit 0
[ -f "$SRC" ] || exit 0
# roda de /var/tmp: o modo disco do USB desmonta /mnt/us e mataria um processo que rodasse de lá
cp "$SRC" "$RUN" 2>/dev/null && chmod 755 "$RUN" 2>/dev/null || exit 0
setsid sh "$RUN" >/dev/null 2>&1 </dev/null &
exit 0
