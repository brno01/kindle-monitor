# kindle-monitor

Um Kindle Paperwhite 5 com jailbreak como **monitor de recursos em e-ink** do homelab (atheron). A tela mostra CPU, RAM, GPU, temperaturas, discos, jogadores e portas do Ragnarok e os serviços importantes, e atualiza a cada minuto.

```
atheron (servidor Python, só lê)  --PNG por HTTP, tailnet, porta 8765-->  Kindle (Tailscale userspace + FBInk)
```
O Kindle só busca e desenha. Quem calcula é o servidor.

## Como usar
1. No Kindle, na biblioteca, toque em **Monitor Ligar**. Ele volta à biblioteca e, em cerca de 15 s, a tela do monitor aparece.
2. Não encoste na tela depois (o toque vai para a interface por baixo). Para sair, segure o botão de energia por cerca de 7 s (reinicia) ou peça para parar por SSH.
3. **Monitor Desligar** para o laço quando você consegue ver a biblioteca.

## Estrutura
- `server/`: servidor, coletores, render do PNG e testes (142).
- `kindle/`: o que vai para o Kindle (`kindle-monitor/loop.sh`, `config.sh`, scriptlets em `documents/`).
- `deploy/`: unit systemd, config e instalador do atheron.
- `tools/`: `gerar_fonte.py` (fonte embutida) e `preview.py`.

Detalhes de arquitetura, acessos, cuidados e pendências: `CLAUDE.md`. No Obsidian: `projects/nomad/notes/Kindle monitor - *.md`.

## Jailbreak e segurança do aparelho
O jailbreak é o **moderno** (KPM, Jobman e Scriptlets). KUAL, MRPI e USBNetwork são legado e não funcionam nele. O Wi-Fi pode atualizar o firmware e apagar o jailbreak, então o bloqueio de atualização do Jobman precisa ficar ligado. Não use `;kpm install/uninstall`, `freset`, `;shpm`, "atualizar ambiente" nem recovery do Jobman. Guia oficial: <https://kindlemodding.org>.

## Estado
No ar desde 15/11/2026. Código na branch `feat/kindle-monitor` (sem push).
