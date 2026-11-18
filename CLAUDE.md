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
- **Barra do Kindle** (alto de todas as páginas, `BARRA_KINDLE_H`): bateria, Wi-Fi, Bluetooth, modo avião e caminho do Tailscale até o atheron (direto/relay). O `loop.sh` lê com `lipc-get-prop` a cada `KSTATUS_EVERY` s e manda como parâmetros `k*` do `/tela.png` (só números e enums); `server/kindle_status.py` guarda o último estado. Esse código rodou sem commit de 16 a 17/11/2026 e foi reconstruído a partir do instalado.
- **Páginas** (barra de 6 botões no rodapé): resumo, serviços, detalhes, ações (id `comandos`) e **Claude** (id `claude`, só leitura): limites de 5 h e semanal e tokens do Claude Code (`m["claude"]`) mais bateria e caminhos de acesso do S10 (`m["s10"]`); sem as chaves na config mostra "Claude/S10 desligado na config". Prévia: `python3 -I tools/preview.py --saida /tmp/c.png --pagina claude`.
- **NAS**: `/srv/nas` é mergerfs (SSD + HD); a tela usa `/srv/nas-hd` (statvfs) e a camada SSD de `/var/lib/cerberus-nas/tier-state.json` (`tier_state` na config), como o painel do Cerberus. GPU com util 0 e VRAM 0 aparece como "desativada".
- **Deploy** (`deploy/`): `config.atheron.json`, `kindle-monitor.service` (`User=nobody`, somente leitura), `instalar-atheron.sh`.

## Acesso e infraestrutura
| O quê | Detalhe |
|---|---|
| atheron | `100.64.0.1` (tailnet), `192.0.2.10` (LAN). Serviço em `/opt/kindle-monitor`, config `/etc/kindle-monitor/config.json`. Firewall (`/etc/nftables.conf`) libera a 8765 só para o Kindle `100.64.0.2` e o nomad `100.64.0.3`. |
| Kindle SSH | `ssh root@kindle-monitor` (Tailscale SSH) ou, na LAN, `ssh -i ~/.ssh/kindle-monitor_ed25519 root@192.0.2.46` (Jobman/dropbear, **só chave**; senha desligada). |
| Kindle jailbreak | KPM, Jobman (bloqueio de OTA ligado), Scriptlets. FBInk em `/mnt/us/libkh/bin/fbink`. KUAL/MRPI/USBNetwork são legado e **não valem**. |
| Tailscale no Kindle | `/mnt/us/tailscale/` (`tailscaled --tun=userspace-networking --socks5-server=localhost:1055`). Não sobe sozinho após reiniciar o Kindle. |

## Comandos
| Ação | Comando |
|---|---|
| Testes do servidor | `cd server && (umask 022; python3 -I -m unittest discover -s tests)` (648 testes, ~4 min; com `umask 0002` os testes do executor falham porque ele recusa arquivo gravável pelo grupo) |
| Rodar local | `python3 -I server/monitor_server.py --bind 127.0.0.1 --porta 8765 --config server/config.exemplo.json` |
| Ver a tela | `curl -s http://127.0.0.1:8765/tela.txt`; PNG: `python3 -I tools/preview.py` |
| Atualizar o atheron | precisa de `sudo` com senha (passo do usuário): `sudo bash -c 'set -euo pipefail; umask 022; S=/root/kindle-monitor-deploy; R=~/development/personal/kindle-monitor; rm -rf "$S"; install -d -m 0700 "$S"; cp -a "$R/server" "$S/server"; cp -a "$R/deploy/." "$S/"; find "$S" -name __pycache__ -prune -exec rm -rf {} +; bash "$S/instalar-atheron.sh"'` |
| Atualizar o Kindle | `ssh root@kindle-monitor 'cat > /tmp/X.novo' < kindle/kindle-monitor/X`, `sh -n`, guardar o anterior (`X.antes-<motivo>`) e copiar para `/mnt/us/kindle-monitor/`; depois "Monitor Desligar" e "Monitor Ligar". O Tailscale SSH do Kindle pede aprovação no navegador (modo check) |
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
- **Parar a interface do Kindle (`stop lab126_gui`) às vezes apaga a tela para branco** depois do 1º desenho (2 de 6 partidas em 17/11/2026). No modo economia (5 min) isso deixava uma tela branca com o toque preso; o `supervisor.sh` redesenha a última imagem logo depois de parar a interface ("redrew after UI stop" no log). Para conferir a tela sem olhar o aparelho: `ssh root@kindle-monitor 'cat /dev/fb0'` (8 bpp, stride 1248, 1236x1648 visíveis).
- **USB num computador mata o que roda de `/mnt/us`** (modo disco). Nada crítico (botão, toque) pode depender de arquivo em `/mnt/us` enquanto roda: fica no supervisor em RAM.
- Com `preventScreenSaver=1` o `powerd` ignora o botão virtual (`powerButton 1`); para testar a saída, injete `KEY_POWER` (116) em `/dev/input/event0`. Isso pode deixar o Kindle em repouso (sem Wi-Fi até alguém apertar o botão).
- O instalador do atheron faz `restart` (o `enable --now` não reinicia) e só deve rodar depois dos testes passarem; não use `| tail` no meio, ele mascara o código de saída.
- Servidor somente leitura, sem segredos, só no IP da tailnet. **Não crie worktrees de outros repositórios dentro de `~/development/personal`** (o exportador do Obsidian trata qualquer pasta com `.git` ali como projeto novo).
- Documentação do projeto no Obsidian: `projects/nomad/notes/Kindle monitor - *.md` (3 notas manuais) e a entrada `kindle-monitor` no `nomad-enhancement/obsidian/sources.toml`. O exportador só lê o que está commitado (o HEAD do checkout).

## Pendências
- Página Claude no ar desde 17/11/2026 (atheron e Kindle), mas com "n/d" até os produtores rodarem no atheron: `claude-uso-painel` (branch `feat/claude-uso-painel` do dotfiles; grava `/var/lib/claude-uso/*.json`) e `cerberus-s10` (projeto `galaxy-s10`; grava `/run/cerberus-s10-publico/resumo.json`).
- Cartão do nomad na tela (rodar o servidor no nomad e listar como par em `config.atheron.json`).
- Início automático após reiniciar o Kindle (hoje: tocar em "Monitor Ligar").
- Confirmar com o botão físico que a saída funciona (testado só por injeção de evento no `event0`).
