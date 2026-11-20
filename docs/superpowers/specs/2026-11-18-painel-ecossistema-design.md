# Painel do ecossistema no Kindle — desenho

Data: 18/11/2026. Repositórios tocados: `kindle-monitor` (principal) e `dotfiles` (publicadores de sessões, GitHub e timers).
Fonte: plano aprovado pelo dono em 18/11/2026 (o plano aprovado (arquivo local, fora do repositório), Parte B). A Parte A (configuração do Claude ao abrir) não entra neste documento.

## Intenção

O Kindle deixa de mostrar só o atheron e passa a ser o painel de todo o ecossistema: atheron, NAS, aparelhos da tailnet, backups e rotinas, sessões do Claude e GitHub. A tela inicial mostra só o que pede atenção.

Problemas achados na validação das telas (`/tela.png` do servidor no ar):

- O cartão ATENÇÃO diz "Tudo em ordem" com o disco `/` em 91%. Causa no código: `_atencao` (`server/render_png.py:341`) só olha serviços e a bateria do Kindle; não existe limiar de disco, RAM, temperatura nem de dado velho.
- A grade dos 48 serviços ocupa ~35% da tela inicial e se repete inteira na página Ações.
- Nomad, S22, gateways, backups, rotinas, sessões do Claude e GitHub não aparecem.
- Botões da navegação saem com fontes de tamanhos diferentes (`_botao` tenta 34 e cai para 26 conforme o rótulo); nomes cortados; página Claude meio vazia.

## Objetivos

- Tela inicial só com exceções: uma linha por sistema e a lista do que pede atenção.
- Um motor de alertas único decide o que aparece e em que gravidade.
- Entram no painel: aparelhos da tailnet, backups e rotinas, sessões do Claude e GitHub.
- Refatoração visual com ícones (serviços, NAS, Claude, jogos etc.).
- Seis abas de navegação, cada uma com ícone e rótulo do mesmo tamanho.

## Não objetivos

- Comandos novos pelo Kindle: o conjunto de ações não muda.
- Dado de trabalho (termos bloqueados) e sessões do Claude no nomad.
- Métricas internas do nomad: lá o painel mostra só online/offline.

## Anti-objetivos (falha mesmo funcionando)

- Tela dizer "Tudo em ordem" com problema real.
- Listar tudo em vez de mostrar só as exceções.
- O serviço web ganhar privilégio.
- Dado de trabalho (termos bloqueados) aparecer na tela.
- Exigir nova gravação no Kindle a cada página nova.

## Restrições

- Tela e-ink de 1236×1648 em tons de cinza. Estado se mostra por **forma** (● ok, ○ parado, ✕ falha, ! aviso), não por tom de cinza.
- Fonte embutida ASCII: rótulos da tela sem acento (ex.: "ATENCAO", "Atualizar"). Este documento usa acento; a tela não.
- Servidor só com biblioteca padrão do Python 3 (sem Pillow nem `uv` no atheron).
- Serviço web roda como `nobody` e só lê JSON.
- Inventário root roda a cada 15 s (`deploy/kindle-monitor-executor.py`, timer de 15 s) e é o único coletor com privilégio novo.
- Texto que vem de fora (título de PR, nome de aparelho) é não confiável: vira ASCII com tamanho máximo antes de ir para a tela.
- Sessões e GitHub de trabalho ficam de fora.

## Abordagens consideradas

- **Escolhida: estender o servidor atual.** Novos coletores publicam JSON; o servidor (`nobody`) só lê; um motor de alertas único decide o que aparece. Reaproveita canvas, cache, botões dirigidos pelo servidor e os 648 testes.
- Trocar por um dashboard pronto (Glances/Homepage renderizado em imagem): descartado; exige navegador sem cabeça no atheron e perde o toque e o refresh de 1 s.
- Só corrigir os alertas e compactar a grade: descartado pelo dono (opção "manter a lista completa").

## Decisões do dono

As quatro decisões registradas no plano:

1. Tela inicial **só com exceções**: uma linha por sistema e a lista do que pede atenção. Os 48 serviços ficam só na página Serviços.
2. Entram no painel: **aparelhos da tailnet, backups e rotinas, sessões do Claude, GitHub**.
3. **Refatoração visual com ícones** (serviços, NAS, Claude, jogos etc.).
4. Claude sem pedir permissão: **conta pessoal em todo lugar** (atheron e nomad); as contas de trabalho continuam no modo auto. *Executada na Parte A, fora deste documento.*

Escolhas do autor (ajustáveis, não são decisões do dono):

- Limiares padrão do motor de alertas (lista na seção do motor).
- Nomes das abas: Início, Serviços, Aparelhos, Sistema, Dev, Ações.
- Conjunto de ícones (lista na seção Visual e ícones).
- "Atualizar" como toque no relógio do cabeçalho, sem aba própria.
- Listas de página genéricas no Kindle (padrão `[a-z]` até 16 letras).
- Aparelhos e rotinas iniciais, e a classificação de gateway (alerta de offline sim), nomad e celulares (não).

## O desenho

### Páginas (6 abas, cada uma com ícone e rótulo do mesmo tamanho)

| Aba | id interno | Conteúdo |
|---|---|---|
| Início | `resumo` | ATENÇÃO + uma linha por sistema (abaixo) |
| Serviços | `servicos` | lista paginada atual, com os não-ok primeiro |
| Aparelhos | `aparelhos` (nova) | aparelhos da tailnet, cartão do Kindle e do S10 (saem de Detalhes/Claude) |
| Sistema | `detalhes` | discos, memória, temperatura, I/O de disco e rede, histórico, **rotinas** |
| Dev | `claude` | limites e tokens do Claude, **sessões abertas**, **GitHub** (PRs e CI) |
| Ações | `comandos` | ações rápidas, ajustes, últimos comandos (sem a grade repetida) |

Os ids internos antigos ficam; só os rótulos mudam. "Atualizar" deixa de ser aba e vira toque no relógio do cabeçalho (mesmo id `atualizar`, então o Kindle não muda por isso).

### Tela inicial

```
[barra do Kindle: elo, bluetooth, wifi, bateria]
atheron                                   19:30
+- ATENCAO (2) -------------------------------+
| !! Disco / 91%  (livre 5,7 GB)              |
| !  Backup de senhas atrasado (31 h)         |
+---------------------------------------------+
[srv]  ATHERON    CPU 23%  RAM 46%  46 C  / 91%
[nas]  NAS        HD 42%   SSD 79%  dados 57%
[apar] APARELHOS  6 de 9 online
                  nomad  S10 84%  S22  Kindle 58%
[svc]  SERVICOS   43 de 48 ok
                  host 17/17  docker 15/17  incus 8/10
[rel]  ROTINAS    4 de 4 ok   backup senhas 03:10
[cla]  CLAUDE     5h 14%  sem 2%   3 sessoes, 1 esperando
[git]  GITHUB     2 PRs abertos   CI ok
[jogo] RAGNAROK   0 jogadores   login char map ok
[Inicio][Servicos][Aparelhos][Sistema][Dev][Acoes]
```

Sem alertas, o cartão vira uma linha "Tudo em ordem". Tocar numa linha abre a página de detalhe dela (a linha é registrada como botão `pagina:<id>` no layout do servidor). Com muitos alertas, as segundas linhas somem para dar espaço e o cartão mostra no máximo 6, com "+N".

### Motor de alertas (`server/alertas.py`, novo)

Função pura `(metricas, config) -> lista de {nivel, texto, pagina}`, ordenada por gravidade. Substitui `_atencao` (`server/render_png.py:341`) e a regra duplicada em `server/render.py:228`. Limiares em `config["limiares"]`, com estes padrões (escolha do autor, ajustáveis):

- disco ≥ 85% aviso, ≥ 93% crítico; RAM ≥ 90%; swap ≥ 50%; CPU ≥ 85 °C
- serviço em falha (crítico); parado não opcional (aviso); inventário sem atualizar há > 60 s
- aparelho com `alerta_offline_min` definido e offline além disso (gateways sim; nomad e celulares não)
- rotina que falhou ou passou de `max_idade_h`; unidade do systemd em falha
- limite do Claude ≥ 90%; sessão esperando você há > 10 min (aviso leve)
- CI falhando na branch padrão; porta do Ragnarok fechada
- bateria: Kindle ≤ 15% (regra atual), S10 ≤ 20% descarregando
- qualquer fonte de dados velha: "dados de X sem atualizar há N min"

### Fontes de dados novas

O serviço web continua como `nobody` e só lê JSON. Ninguém ganha privilégio novo.

| Dado | Quem coleta | Onde publica |
|---|---|---|
| Aparelhos da tailnet (`tailscale status --json`: online, visto por último, direto/relay) | inventário root já existente (`deploy/kindle-monitor-executor.py`, timer de 15 s) | `/run/kindle-monitor/status/aparelhos.json` |
| Rotinas: resultado e hora do último disparo de timers, idade do arquivo mais novo de um diretório de backup, `systemctl --failed` | mesmo inventário root | `/run/kindle-monitor/status/rotinas.json` |
| Sessões do Claude no atheron (projeto = nome da pasta, estado, desde quando) | hooks `UserPromptSubmit`/`Stop`/`Notification`/`SessionEnd` + batimento do `statusline.sh`, no padrão do `claude-limites` | `/var/lib/claude-uso/sessoes/<id>.json` |
| GitHub: PRs abertos e CI dos repos pessoais `brno01` (uma consulta `gh api graphql`) | novo `dotfiles/bin/claude-github` + timer de usuário a cada 5 min (`OnStartupSec`) | `/var/lib/claude-uso/github.json` |

Catálogos novos em `/etc/kindle-monitor/config.json` (`deploy/config.atheron.example.json`): `aparelhos` (nome na tailnet, rótulo, ícone, `alerta_offline_min`), `rotinas` (id, rótulo, tipo `timer` ou `arquivo`, alvo, `max_idade_h`) e `limiares`. Rotinas iniciais: backup do Vaultwarden (`cerberus-vault-backup`, `/srv/nas/backups/vaultwarden`), Syncthing do cofre, segundo cérebro, `claude-uso-painel`; os nomes exatos das units são confirmados na implementação.

Texto que vem de fora (título de PR, nome de aparelho) é dado não confiável: vira ASCII, com tamanho máximo, antes de ir para a tela. Sessões e GitHub de trabalho ficam de fora.

### Visual e ícones

- Estender `tools/gerar_icones.py` (hoje só rasteriza `tools/claude.svg`) para uma pasta `tools/icones/*.svg`, gerando `server/icones_dados.py` com todos, nos tamanhos 30, 40 e 56 px. O gerador continua lendo só o atributo `d` dos `<path>`.
- Conjunto: Material Symbols (Apache-2.0, traço cheio em um path) para servidor, NAS, aparelhos, notebook, celular, leitor, serviços, contêiner, relógio/backup, jogo, alerta, ok, rede, temperatura, casa, raio; Simple Icons (CC0) para Claude, GitHub, Docker e Tailscale. Registrar origem e licença no cabeçalho gerado, como já é feito.
- Regras para e-ink: estado por **forma** (● ok, ○ parado, ✕ falha, ! aviso), não por tom de cinza; fonte mínima 26 px; escala fixa (rótulo 26, valor 34/40 em negrito); linhas da tela inicial com altura uniforme; cabeçalho do cartão ATENÇÃO invertido (branco no preto) quando houver item crítico; navegação com ícone em cima e rótulo em tamanho único.

### Lado do Kindle

`kindle/kindle-monitor/loop.sh:58` e `tap.sh:72` têm a lista de páginas fixa. Ela é trocada por um padrão genérico (`[a-z]` até 16 letras; o servidor já devolve a página padrão para valor inválido), para que páginas futuras não exijam nova gravação no aparelho. A gravação no Kindle é feita com backup `*.antes-ecossistema`, por `ssh kindle-lan`. O plano aprovado pelo dono autoriza essa gravação.

## Fica para quem implementa

- Nomes exatos das units das rotinas (o plano cita `cerberus-vault-backup` como candidato; confirmar na implementação).
- Formato exato dos JSON novos: `aparelhos.json`, `rotinas.json`, `github.json`. O plano não os define. O de sessões segue o padrão do `claude-limites`, também sem campos fechados no plano.
- Alturas em pixel das linhas da tela inicial e dos cartões: o plano fixa só tamanhos de fonte (mínima 26 px; rótulo 26; valor 34/40) e de ícone (30, 40, 56 px). A altura é uniforme entre as linhas, mas o valor não está definido.
- Nomes internos de funções e ordem dos commits.

## Verificação

- Testes do kindle-monitor: `cd server && (umask 022; python3 -I -m unittest discover -s tests)` (~4 min, em segundo plano com log). Testes do dotfiles pelo comando do README dele.
- Alertas: casos de teste para cada regra e para o caso real de hoje (disco 91% tem de gerar alerta).
- Visual: prévias em PNG (`tools/preview.py`) de todas as páginas, nos estados "tudo ok", "com alertas" e "dados velhos", conferidas pelo dono antes de instalar e de novo antes da segunda instalação.
- No ar: `curl` de `/tela.png?pagina=<cada uma>` e leitura das imagens; `journalctl -u kindle-monitor` com pedidos chegando; `/tmp/kindle-monitor.log` no Kindle; toque em cada aba e em cada linha da tela inicial.
- Fontes novas: desligar o Wi-Fi do S22 e ver o aparelho ficar offline; abrir e fechar uma sessão do Claude e ver a contagem mudar; conferir `github.json` contra `gh pr list`.

## Fora do escopo

- Métricas internas do nomad (CPU, bateria): o painel mostra só online/offline; o cartão do nomad pede um agente lá e fica para depois.
- Sessões do Claude no nomad e qualquer dado de trabalho (termos bloqueados).
- Comandos novos pelo Kindle (o conjunto de ações não muda).
