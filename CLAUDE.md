# kindle-monitor

## Visão geral
- Área: personal
- O que é: um Kindle Paperwhite 5 (G001 PX11, firmware 5.18.3) com jailbreak moderno funciona como **monitor de recursos em e-ink do atheron**: CPU, RAM, swap, GPU/VRAM, temperaturas, discos, jogadores e portas do Ragnarok, serviços.
- Estado (15/11/2026): **no ar**. Servidor instalado no atheron, Kindle desenhando a cada 15 s (flash completo a cada 40 ciclos = 10 min), **toque desligado com o monitor ligado e saída só pelo botão de energia**. Código na `master` e no GitHub **privado** `brno01/kindle-monitor` (15/11/2026). Commit e push só quando o usuário pedir; mudanças novas em branch de feature.
- O dono do Kindle só fez o jailbreak e não conhece o aparelho por dentro: toda instrução a ele é passo a passo, dizendo o que deve aparecer na tela. Nada é gravado no Kindle sem a autorização dele.

## Arquitetura
```
atheron: kindle-monitor.service (Python stdlib, só lê)  --PNG 1236x1648, HTTP, tailnet:8765-->
Kindle: Tailscale userspace (SOCKS5 localhost:1055) + /mnt/us/kindle-monitor/loop.sh (curl + FBInk)
```
- **Servidor** (`server/`): `monitor_server.py` (CLI; recusa `--bind 0.0.0.0`), `coletores.py` (/proc, nvidia-smi, `systemctl is-active`, balanceador, portas TCP, pares), `render.py` (texto), `render_png.py` + `canvas.py` + `png.py` (imagem só com a stdlib), `fonte_dados.py` (DejaVu pré-rasterizada, gerada por `tools/gerar_fonte.py` com Pillow via `uv run --with pillow`). Endpoints: `/tela.png`, `/tela.txt`, `/metricas.json`, `/historico.json`, `/saude`.
- **Kindle** (`kindle/`): `kindle-monitor/loop.sh`, `supervisor.sh` e `config.sh` vão para `/mnt/us/kindle-monitor/`; `documents/monitor-ligar.sh` e `monitor-desligar.sh` viram "livros" (scriptlets) que o usuário toca. O "Ligar" copia o `supervisor.sh` para `/var/tmp` (RAM) e o inicia: ele lança o `loop.sh`, vigia o botão de energia (`dd` em `/dev/input/event0` + `lipc-wait-event ... goingToScreenSaver`), religa o toque (`lipc-set-prop com.lab126.deviced enable_touch 1`) sempre que o laço não roda e relança o laço depois do modo disco USB.
- **NAS**: `/srv/nas` é mergerfs (SSD + HD); a tela usa `/srv/nas-hd` (statvfs) e a camada SSD de `/var/lib/cerberus-nas/tier-state.json` (`tier_state` na config), como o painel do Cerberus. GPU com util 0 e VRAM 0 aparece como "desativada".
- **Deploy** (`deploy/`): `config.atheron.json`, `kindle-monitor.service` (`User=nobody`, somente leitura), `instalar-atheron.sh`.

## Acesso e infraestrutura
| O quê | Detalhe |
|---|---|
| atheron | `100.64.0.1` (tailnet), `192.0.2.10` (LAN). Serviço em `/opt/kindle-monitor`, config `/etc/kindle-monitor/config.json`. Firewall (`/etc/nftables.conf`) libera a 8765 só para o Kindle `100.64.0.2` e o nomad `100.64.0.3`. |
| Kindle SSH | `ssh kindle-lan` (do nomad, sem login do navegador): dropbear do Jobman na LAN 192.0.2.46, **só chave**, saltando por `root@atheron`; apelido em `dotfiles/ssh/tailnet.conf`. A 22 do `wlan0` só aceita o atheron (192.0.2.10). Reserva: `ssh root@kindle-monitor` (Tailscale SSH, pede o check do navegador). |
| Kindle jailbreak | KPM, Jobman (bloqueio de OTA ligado), Scriptlets. FBInk em `/mnt/us/libkh/bin/fbink`. KUAL/MRPI/USBNetwork são legado e **não valem**. |
| Tailscale no Kindle | `/mnt/us/tailscale/` (`tailscaled --tun=userspace-networking --socks5-server=localhost:1055`, SSH do Tailscale ligado). |
| Autostart (boot) | `/etc/upstart/kmc.conf` (do jailbreak) roda `/mnt/us/emergency.sh` em todo boot; ele copia `kindle-monitor/autostart.sh` para `/var/tmp` e sai. O laço espera o Wi-Fi e mantém o `tailscaled`, o dropbear do Jobman (de `/var/tmp`, `-s -g -j -k`) e a regra `iptables` da 22 para o atheron, conferindo a cada 60 s. Log: `/var/tmp/kindle-autostart.log`. Instalar/desfazer do nomad: `deploy/instalar-autostart-kindle.sh [--check\|--desfazer]`. Trava: `/mnt/us/kindle-monitor/SEM_AUTOSTART`. O monitor (laço da tela) continua manual. |

## Comandos
| Ação | Comando |
|---|---|
| Testes do servidor | `cd server && python3 -I -m unittest discover -s tests` (165 testes) |
| Rodar local | `python3 -I server/monitor_server.py --bind 127.0.0.1 --porta 8765 --config server/config.exemplo.json` |
| Ver a tela | `curl -s http://127.0.0.1:8765/tela.txt`; PNG: `python3 -I tools/preview.py` |
| Atualizar o atheron | copiar `server/` + `deploy/` para `/root/kindle-monitor-deploy/` e rodar `deploy/instalar-atheron.sh` |
| Parar / ligar o monitor | `ssh root@kindle-monitor 'sh /mnt/us/documents/monitor-desligar.sh'` / `'sh -l /mnt/us/documents/monitor-ligar.sh'` |

## Convenções
- Branch padrão `master`. Sem commit nem push sem o usuário pedir. Código e commits em inglês; falas ao usuário em português.
- Servidor só com a biblioteca padrão do Python 3 (o atheron não tem Pillow nem `uv`).

## Cuidados
- **Risco de brick do Kindle:** nada de `;kpm install/uninstall`, `freset`, `;shpm`, "atualizar ambiente" ou recovery do Jobman. O bloqueio de OTA do Jobman tem que ficar ligado; nunca atualizar o firmware.
- **Firewall do atheron:** gerar o candidato em arquivo temporário, `nft -c -f`, mostrar o `diff` e aplicar a regra viva com `nft insert rule`. Nunca `sed` com número de linha vindo de `grep` (já corrompeu o arquivo uma vez; havia cópia `.antes-kindle`).
- `DynamicUser=yes` quebra o `systemctl is-active` (D-Bus): usar `User=nobody`.
- Confirme pelo lado do servidor (`journalctl -u kindle-monitor` no atheron) e pelo `/tmp/kindle-monitor.log` do Kindle: o e-ink mantém a última imagem e engana.
- O lançador de scriptlets roda `sh -l script | fbink` e volta à biblioteca; o laço usa duplo fork + `setsid`, ignora SIGHUP e espera `FIRST_DELAY` (12 s) antes do 1º desenho.
- **Rootfs do Kindle é só leitura e está 96% cheio:** nada de mexer em `/etc/upstart` nem `/usr/local`. O `/etc/upstart/sshd.conf` aponta para um `/usr/local/sbin/dropbear` que não existe (falha calado; deixe assim). Boot só pelo gancho `emergency.sh` do `kmc.conf`.
- **Firewall do Kindle é `INPUT DROP`:** porta nova no `wlan0` precisa de regra `iptables` (o Jobman faz o mesmo quando sobe o SSH dele). Não rode o binário `/mnt/us/jobman/jobman` para "ver a ajuda": ele é o menu/recovery.
- **USB num computador mata o que roda de `/mnt/us`** (modo disco). Nada crítico (botão, toque) pode depender de arquivo em `/mnt/us` enquanto roda: fica no supervisor em RAM.
- Com `preventScreenSaver=1` o `powerd` ignora o botão virtual (`powerButton 1`); para testar a saída, injete `KEY_POWER` (116) em `/dev/input/event0`. Isso pode deixar o Kindle em repouso (sem Wi-Fi até alguém apertar o botão).
- O instalador do atheron faz `restart` (o `enable --now` não reinicia) e só deve rodar depois dos testes passarem; não use `| tail` no meio, ele mascara o código de saída.
- Servidor somente leitura, sem segredos, só no IP da tailnet. **Não crie worktrees de outros repositórios dentro de `~/development/personal`** (o exportador do Obsidian trata qualquer pasta com `.git` ali como projeto novo).
- Documentação do projeto no Obsidian: `projects/nomad/notes/Kindle monitor - *.md` (3 notas manuais) e a entrada `kindle-monitor` no `nomad-enhancement/obsidian/sources.toml`. O exportador só lê o que está commitado (o HEAD do checkout).

## Pendências
- Cartão do nomad na tela (rodar o servidor no nomad e listar como par em `config.atheron.json`).
- Início automático do monitor (laço da tela) após reiniciar o Kindle (hoje: tocar em "Monitor Ligar"). Tailscale e SSH já sobem sozinhos (autostart, 18/11/2026).
- Confirmar com o botão físico que a saída funciona (testado só por injeção de evento no `event0`).
