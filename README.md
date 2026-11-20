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
- `kindle/`: o que vai para o Kindle (`kindle-monitor/loop.sh`, `config.example.sh`, scriptlets em `documents/`; `emergency.sh` + `kindle-monitor/autostart.sh`: Tailscale e SSH no boot; testes em `kindle/tests/`).
- `deploy/`: unit systemd, config de exemplo (`config.atheron.example.json`) e instalador do atheron; `instalar-autostart-kindle.sh` (roda no nomad: `--check`, instalar, `--desfazer`).
- `tools/`: `gerar_fonte.py` (fonte embutida) e `preview.py`.

Detalhes de arquitetura, acessos, cuidados e pendências: `CLAUDE.md`. No Obsidian: `projects/nomad/notes/Kindle monitor - *.md`.

## Configuração local
Valores reais (IPs, nomes de rede, termos que nunca podem aparecer na tela) ficam em arquivos **locais, fora do git** (`.gitignore`); o repositório traz só exemplos com valores fictícios:
- `deploy/config.atheron.example.json` -> copie para `deploy/config.atheron.local.json` e preencha (o `instalar-atheron.sh` instala esse arquivo em `/etc/kindle-monitor/config.json`; sem ele o instalador para). Chaves próprias: `bind` (IP onde o serviço escuta), `ollama_url` e `termos_bloqueados` (ver `server/README.md`).
- `kindle/kindle-monitor/config.example.sh` -> copie para `kindle/kindle-monitor/config.local.sh`, ajuste `SERVER` e `SSH_FROM`, e grave no Kindle como `/mnt/us/kindle-monitor/config.sh`. O zip da release leva só o exemplo: renomeie para `config.sh` e edite.
- `server/config.exemplo.json`: exemplo comentado de todas as chaves do servidor.

Ao atualizar o Kindle, grave o `config.sh` **antes** do `autostart.sh` novo: o `autostart.sh` lê o `SSH_FROM` do `config.sh` e, sem ele, a porta 22 do Kindle fica fechada. Os comandos de cópia estão em `CLAUDE.md` ("Atualizar o Kindle").

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
No ar desde 15/11/2026. Repositório `brno01/kindle-monitor`, branch `master`.

## Licença
[MIT](LICENSE)
