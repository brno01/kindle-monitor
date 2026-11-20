# kindle-monitor

[![ci](https://github.com/brno01/kindle-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/brno01/kindle-monitor/actions/workflows/ci.yml)
[![security](https://github.com/brno01/kindle-monitor/actions/workflows/security.yml/badge.svg)](https://github.com/brno01/kindle-monitor/actions/workflows/security.yml)

Um Kindle Paperwhite 5 com jailbreak como **monitor de recursos em e-ink** do homelab (atheron). A tela mostra CPU, RAM, GPU, temperaturas, discos, jogadores e portas do Ragnarok e os serviços importantes, e atualiza a cada minuto. Uma página extra, "Claude", mostra os limites e o consumo de tokens do Claude Code e o estado do celular S10 (bateria e caminhos de acesso).

```
atheron (servidor Python, só lê)  --PNG por HTTP, tailnet, porta 8765-->  Kindle (Tailscale userspace + FBInk)
```
O Kindle só busca e desenha. Quem calcula é o servidor.

## Como usar
1. No Kindle, na biblioteca, toque em **Monitor Ligar**. Ele volta à biblioteca e, em cerca de 15 s, a tela do monitor aparece.
2. Não encoste na tela depois (o toque vai para a interface por baixo). Para sair, segure o botão de energia por cerca de 7 s (reinicia) ou peça para parar por SSH.
3. **Monitor Desligar** para o laço quando você consegue ver a biblioteca.

## Estrutura
- `server/`: servidor, coletores, render do PNG e testes.
- `kindle/`: o que vai para o Kindle (`kindle-monitor/loop.sh`, `config.sh`, scriptlets em `documents/`; `emergency.sh` + `kindle-monitor/autostart.sh`: Tailscale e SSH no boot; testes em `kindle/tests/`).
- `deploy/`: unit systemd, config e instalador do atheron; `instalar-autostart-kindle.sh` (roda no nomad: `--check`, instalar, `--desfazer`).
- `tools/`: `gerar_fonte.py` (fonte embutida) e `preview.py`.

Detalhes de arquitetura, acessos, cuidados e pendências: `CLAUDE.md`. No Obsidian: `projects/nomad/notes/Kindle monitor - *.md`.

## Testes e CI
```bash
cd server && (umask 022; python3 -I -m unittest discover -s tests)
```
O `umask 022` é necessário: o executor recusa arquivo gravável pelo grupo. O servidor usa só a biblioteca padrão do Python 3.13.

No GitHub, todo PR e todo push na `master` rodam dois workflows:
- `ci`: os testes do servidor e a checagem de sintaxe (`sh -n`) dos scripts do Kindle.
- `security`: segredos, dependências vulneráveis, análise estática, shellcheck e os próprios workflows. Uma falha na `master` abre uma issue `security-scan`.

O `claude` é o revisor sob demanda: comente `@claude` num PR ou numa issue, ou rode o workflow à mão para uma auditoria que abre issues. Só o dono do repositório consegue acioná-lo.

## Releases
Cada tag `v*` cria uma release com o arquivo `kindle-monitor-kindle.zip`: o que vai para `/mnt/us` no Kindle (`emergency.sh`, `documents/` e `kindle-monitor/`), sem os testes.

## Jailbreak e segurança do aparelho
O jailbreak é o **moderno** (KPM, Jobman e Scriptlets). KUAL, MRPI e USBNetwork são legado e não funcionam nele. O Wi-Fi pode atualizar o firmware e apagar o jailbreak, então o bloqueio de atualização do Jobman precisa ficar ligado. Não use `;kpm install/uninstall`, `freset`, `;shpm`, "atualizar ambiente" nem recovery do Jobman. Guia oficial: <https://kindlemodding.org>.

## Estado
No ar desde 15/11/2026. Repositório privado `brno01/kindle-monitor`, branch `master`.

## Licença
Repositório privado, todos os direitos reservados. Veja [LICENSE](LICENSE).
