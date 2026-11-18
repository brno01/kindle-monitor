# Painel do ecossistema no Kindle — plano de tarefas

> Para quem executa: uma tarefa por vez, na ordem das dependências; cada uma traz `Agente:`. Commit local por tarefa na branch de feature (mensagem em inglês). Push e PR só quando o dono pedir.

## Contexto

- **Objetivo:** o Kindle vira painel do ecossistema. A tela inicial mostra só exceções: cartão ATENÇÃO alimentado por um motor de alertas único (hoje o disco `/` a 91% sai como "Tudo em ordem") e uma linha por sistema.
- **Fonte da verdade:** plano aprovado `~/.claude/plans/floofy-cuddling-nova.md`, Parte B (a Parte A já foi feita). Desenho: `docs/superpowers/specs/2026-11-18-painel-ecossistema-design.md`. Não reabrir decisões.
- **Worktrees:** kindle-monitor em `~/development/worktrees/kindle-monitor-ecossistema` (`feat/painel-ecossistema`); dotfiles em `~/development/worktrees/dotfiles-bypass-sessoes` (`feat/bypass-e-painel-dev`).
- **Testes:** kindle-monitor, um módulo: `cd server && (umask 022; python3 -I -m unittest tests.<modulo> -v)`. Suíte inteira (643+ testes, ~4 min): mesmo comando com `discover -s tests`, em segundo plano, log em `<scratchpad>/km-*.log`. dotfiles: `uv run --no-project --with pytest pytest tests`. Scripts do Kindle: `busybox sh -n` e `shellcheck`.
- **Restrições:** servidor só com stdlib, roda como `nobody` e só lê; fonte ASCII (sem acento na tela); texto de fora vira ASCII com tamanho máximo em quem grava e em quem lê; nada da empresa-x (a tailnet tem um peer `empresa-x-*`); o root só roda comandos de leitura com argv fixo, `shell=False` e timeout.
- **Gargalo:** `server/render_png.py`. As tarefas 4–9 e 22–23 mexem nele e são estritamente sequenciais.

## Escolhas deste plano (o desenho deixou em aberto)

- **E1. Ordem das entregas.** As listas genéricas de página do Kindle vão para a Entrega 1 (tarefa 4). `TapShTest` (`server/tests/test_botoes.py` ~l.223) exige que os `case` de `tap.sh`/`loop.sh` sejam iguais a `botoes.PAGINAS`; sem isso, a aba nova `aparelhos` quebra a suíte e fica sem efeito no Kindle.
- **E2. Geometria fixa da tela inicial.** O `/botoes.txt` é montado sem as métricas (`botoes.layout` só recebe os itens de serviço). Por isso:
  - as 8 linhas ficam em posições fixas, ancoradas embaixo: 112 px cada, 12 px entre elas, primeira em y=532 (1236x1648); cada linha é um botão `pagina:<destino>`;
  - o ATENÇÃO ocupa de `TOPO` até a primeira linha: cabem 7 linhas de item (6 alertas mais "+N");
  - as segundas linhas nunca somem; linha sem fonte mostra "sem dados" em cinza, com a forma "?", e nenhuma linha some.
- **E3. Destinos ao tocar nas linhas:** ATHERON, NAS e ROTINAS → `detalhes`; APARELHOS → `aparelhos`; SERVICOS e RAGNAROK → `servicos`; CLAUDE e GITHUB → `claude`.
- **E4. Botões invisíveis.** Um botão de layout pode ter `"visivel": False`: entra no `/botoes.txt`, mas `_desenhar_botoes` não o desenha. Vale para as linhas da tela inicial e para `atualizar`, que vira o relógio do cabeçalho (`x = largura-MARGEM-200`, `y = BARRA_KINDLE_H`, `w = 200`, `h = 70`, em todas as páginas).
- **E5. Abas.** `PAGINAS = ("resumo","servicos","aparelhos","detalhes","claude","comandos")`. NAV, na ordem (rótulo/ícone): Inicio/`inicio`, Servicos/`servicos`, Aparelhos/`aparelhos`, Sistema/`sistema`, Dev/`dev`, Acoes/`acoes`. Ícone de 30 px em cima; rótulo sempre em negrito 26.
- **E6. Motor de alertas (`server/alertas.py`).** O render não recebe a config, então o coletor publica `m["limiares"]`. A bateria do Kindle chega a cada pedido, então entra como `kv`.

  ```python
  PADRAO = {"disco_aviso": 85, "disco_critico": 93, "ram": 90, "swap": 50, "temp_cpu_c": 85, "kindle_bateria": 15,
            "s10_bateria": 20, "claude_limite": 90, "sessao_esperando_min": 10}
  def limiares(cfg) -> dict  # None/não-dict -> PADRAO; chave desconhecida ignorada; bool, não número ou fora da faixa
                             # (pct 1..100, temp 40..120, minutos 1..1440) -> padrão daquela chave
  def avaliar(m, lim=None, kv=None) -> list[dict]  # pura, nunca levanta; m não-dict -> []
  # alerta = {"nivel": "critico"|"aviso"|"leve", "texto": ASCII <= 48, "pagina": id de botoes.PAGINAS,
  #           "sistema": "atheron"|"nas"|"aparelhos"|"servicos"|"rotinas"|"claude"|"github"|"ragnarok"|"kindle"}
  # ordem: critico, aviso, leve; dentro do nível, a ordem das regras (estável)
  ```

  Regras (o disco `/` conta para `atheron`; os outros, para `nas`):
  - **Crítico:** disco ≥ `disco_critico`; serviço em falha; rotina com `resultado == "falha"`; `unidades_falhas.n > 0` (um alerta, com até 2 nomes); aparelho com `alerta_offline_min` e `offline_min` maior ou igual a ele.
  - **Aviso:**
    - recursos: disco ≥ `disco_aviso`; RAM ≥ `ram`; swap ≥ `swap` (com `total_kb > 0`); `temp_cpu.c` ≥ `temp_cpu_c`;
    - serviços: parado não opcional; `servicos_kindle.inventario` em `velho`/`ausente`;
    - rotina `atrasada`;
    - limite do Claude (5h ou semanal, não `renovado`) ≥ `claude_limite`;
    - CI da branch padrão em `falha`; porta do Ragnarok com `aberto` falso;
    - baterias: Kindle ≤ `kindle_bateria` sem carregar; S10 com nível ≤ `s10_bateria` e `status` `discharging`/`not_charging`;
    - fonte velha: "dados de <fonte> sem atualizar ha N min". Conta como velha `velho is True` em `claude.limites`, `claude.tokens`, `s10` e `github`, e `inventario == "velho"` em `aparelhos` e `rotinas`.
  - **Leve:** sessão `esperando` com `desde_s` ≥ `sessao_esperando_min*60`.

  A Entrega 1 já implementa todas as regras. As chaves da Entrega 2 têm formato fechado abaixo e entram nos testes com fixtures.
- **E7. JSON novos.** Todos 0644, com gravação atômica (temporário no mesmo diretório + rename). Nenhum leva IP, chave, e-mail ou OS.
  - `/run/kindle-monitor/status/aparelhos.json` (root): `{"versao":1,"gerado":int,"erro":null|str<=40,"aparelhos":{"<id>":{"online":bool|null,"visto_em":int|null,"conexao":"direto"|"relay"|null}}}`.
    - Só ids do catálogo; peer fora do catálogo nunca é gravado.
    - `conexao`: `CurAddr` não vazio → direto; senão `Relay` → relay. `visto_em` vem de `LastSeen`. Peer ausente → `online: null`.
  - `/run/kindle-monitor/status/rotinas.json` (root): `{"versao":1,"gerado":int,"rotinas":{"<id>":{"resultado":"ok"|"falha"|"desconhecido","ultima_em":int|null,"detalhe":str<=24}},"unidades_falhas":{"n":int,"nomes":[str<=40] (máx. 5)}}`.
  - `/var/lib/claude-uso/sessoes/<id>.json` (usuário `claude`): `{"versao":1,"id":str,"projeto":str<=40,"estado":"aberta"|"trabalhando"|"esperando","desde":int,"atualizado_em":int}`. O `id` casa com `^[0-9a-f-]{8,64}$`; `projeto` é o basename do `cwd` com `[A-Za-z0-9._-]`.
  - `/var/lib/claude-uso/github.json` (usuário `claude`): `{"versao":1,"gerado_em":int,"dono":"brno01","prs":[{"repo":str<=40,"numero":int,"titulo":str<=80,"rascunho":bool,"ci":"ok"|"falha"|"pendente"|null}] (máx. 20),"ci":[{"repo":str,"branch":str<=40,"estado":"ok"|"falha"|"pendente"}] (máx. 30)}`.
- **E8. Chaves novas da config** (`deploy/config.atheron.json`, `server/config.exemplo.json`):

  ```json
  "limiares": {"disco_aviso": 85, "disco_critico": 93, "ram": 90, "swap": 50, "temp_cpu_c": 85, "kindle_bateria": 15,
               "s10_bateria": 20, "claude_limite": 90, "sessao_esperando_min": 10},
  "aparelhos": [{"id": "gw", "nome": "cerberus-gw", "rotulo": "Gateway", "icone": "rede", "alerta_offline_min": 10}],
  "rotinas": [{"id": "senhas", "rotulo": "Backup senhas", "tipo": "timer", "alvo": "cerberus-vault-backup.service", "max_idade_h": 26},
              {"id": "painel", "rotulo": "Tokens Claude", "tipo": "arquivo", "alvo": "/var/lib/claude-uso/tokens.json", "max_idade_h": 1}],
  "claude": {"limites": "...", "tokens": "...", "sessoes": "/var/lib/claude-uso/sessoes"},
  "github": {"resumo": "/var/lib/claude-uso/github.json"}
  ```

  Validação (igual no executor e no servidor; um teste confere a paridade):
  - `aparelhos` (máx. 16): `id` `^[a-z0-9-]{1,24}$`; `nome` `^[a-z0-9-]{1,63}$` e sem `empresa-x`; `rotulo` ASCII de 1 a 16; `icone` em `icones_dados.ICONES`; `alerta_offline_min` opcional, inteiro de 1 a 10080.
  - `rotinas` (máx. 16): `rotulo` de 1 a 20; `timer` → `alvo` `^[A-Za-z0-9_.@-]{1,64}\.service$`; `arquivo` → `alvo` absoluto, com `normpath(alvo) == alvo`, sob `/srv/`, `/var/lib/` ou `/var/backups/`; `max_idade_h` de 0.1 a 720.
  - Config inválida não derruba nada: o servidor descarta a lista; o executor registra uma linha e não grava aquele arquivo.
- **E9. Ícones** em `tools/icones/<nome>.svg`, gerados em 30, 40 e 56 px.
  - Material Symbols (Apache-2.0, `@material-symbols/svg-400` via jsDelivr com versão fixada, `outlined`, variante `-fill` quando existir). Nome no painel=símbolo: `inicio`=home, `servidor`=dns, `nas`=hard_drive, `aparelhos`=devices, `notebook`=laptop, `celular`=smartphone, `leitor`=menu_book, `servicos`=apps, `conteiner`=deployed_code, `rotinas`=schedule, `backup`=backup, `jogo`=sports_esports, `alerta`=warning, `ok`=check_circle, `rede`=lan, `temperatura`=thermostat, `acoes`=bolt, `sistema`=memory, `dev`=terminal. `sistema` e `dev` não estavam no desenho; entram por causa das abas.
  - Simple Icons (CC0, `simple-icons@16.38.0`): `claude` (sai de `tools/claude.svg`), `github`, `docker`, `tailscale`. Total: 23.
- **E10. Sessões.**
  - Eventos: `UserPromptSubmit` → `trabalhando`; `Stop` e `Notification` → `esperando`; `SessionEnd` apaga o arquivo.
  - Batimento da statusline: cria como `aberta` se faltar; senão só renova `atualizado_em`, no máximo a cada 30 s. `desde` só muda quando o estado muda.
  - Leitor e gravador: o leitor ignora `atualizado_em` com mais de 12 h (o hook não tem sinal confiável de que o processo continua vivo); o gravador apaga arquivos com mais de 24 h.
  - Só grava na conta pessoal (`CLAUDE_CONFIG_DIR` vazio ou `~/.claude`) e com `cwd` fora de caminhos com `/empresa-x`.
- **E11. Rotinas de usuário.** `claude-uso-painel` e `second-brain` são timers de usuário do `claude`; o `systemctl` do root não os vê. Entram como `arquivo`, pela idade do que produzem.

## Roadmap

| Entrega | Conteúdo | Pronto quando |
|---|---|---|
| 1 | Motor de alertas, ícones, tela inicial e navegação novas, Sistema/Dev/Ações reorganizadas, aba Aparelhos com Kindle e S10, listas genéricas no Kindle. Só dados existentes; tailnet, ROTINAS, GITHUB e sessões mostram "sem dados" | Suíte verde, prévias aprovadas, instalado, toque em cada aba e linha funcionando |
| 2 | Inventário root (aparelhos e rotinas), publicadores do dotfiles (sessões e GitHub), páginas Aparelhos e Dev completas | Suítes dos dois repos verdes, prévias aprovadas, fontes novas conferidas no ar |

## Tarefas

### 0. Linha de base
- Agente: executor (haiku) · Depende de: — · Paralelo com: —
- Fazer: `git status` nos dois worktrees; suíte do kindle-monitor (`umask 022`) em segundo plano em `<scratchpad>/km-base.log`; suíte do dotfiles.
- Pronto quando: total e falhas de cada repo anotados em "Verificação final".

## Entrega 1

### 1. Motor de alertas
- Agente: implementador (sonnet) · Depende de: 0 · Paralelo com: 2, 4
- Arquivos: `server/alertas.py` (novo), `server/tests/test_alertas.py` (novo)
- Fazer: TDD de E6, começando pelos testes:
  - um teste por regra, no limiar e um ponto abaixo; ordenação;
  - `test_disco_91_gera_aviso`: `/` a 91% com 5.7 GB livres vira `aviso` com "91%" no texto;
  - `limiares` com `"85"`, `True`, `-1`, `500`, `None` e lista; tipos errados em cada chave de `m`, sem nunca levantar;
  - texto só ASCII com até 48 caracteres (rótulo de 300 caracteres com acento); `pagina` sempre em `botoes.PAGINAS`.

  `kindle_status.BATERIA_BAIXA` continua existindo para o ícone da barra.
- Pronto quando: `(umask 022; python3 -I -m unittest tests.test_alertas -v)` passa.

### 2. Gerador de ícones para uma pasta
- Agente: implementador (sonnet) · Depende de: 0 · Paralelo com: 1, 4
- Arquivos: `tools/gerar_icones.py`, `tools/icones/claude.svg` (`git mv` de `tools/claude.svg`), `tools/tests/test_gerar_icones.py` (novo)
- Fazer:
  - Ler `tools/icones/*.svg`, ainda só `d` (todos os `<path>`), `fill-rule` e `viewBox`, por regex. Nome do ícone = nome do arquivo (`^[a-z]{2,16}$`); os outros arquivos são ignorados.
  - Escalar pela `viewBox` (tamanho óptico igual); sem ela, pela caixa do path. `TAMANHOS = (56, 40, 30)`.
  - Nonzero por soma de enrolamento no lugar da heurística: cada subpath soma ±1 pelo sinal da área; o pixel é cheio se a soma ≠ 0.
  - O cabeçalho gerado lista origem, versão e licença de cada ícone, lidas do `<!-- Source: ... -->` de cada SVG.
- Pronto quando: `uv run --no-project --with pillow --with svgelements --with pytest pytest tools/tests` passa (anel com o interno anti-horário tem furo; dois quadrados sobrepostos no mesmo sentido ficam cheios; nome inválido é ignorado) e, regerando só com `claude.svg`, `tests.test_canvas` continua verde.

### 3. Conjunto de ícones
- Agente: mecanico (haiku) · Depende de: 2 · Paralelo com: 1, 4, 5
- Arquivos: `tools/icones/*.svg` (22 novos), `server/icones_dados.py` (gerado), `server/tests/test_canvas.py`
- Fazer:
  - Baixar os SVGs de E9 com `curl` (URLs com versão fixada) para um diretório novo e vazio; copiar cada um para `tools/icones/<nome>.svg` com `<!-- Source: <url> (<pacote> <versao>). <licenca>. -->` na primeira linha, como em `claude.svg`.
  - Regerar `server/icones_dados.py`.
  - Teste: os nomes de `ICONES` são exatamente os 23 de E9, cada um em 30/40/56 px, com `len(bitmap) == w*h` e com pixels escuros.
- Pronto quando: `tests.test_canvas` passa.

### 4. Abas, botões invisíveis e Kindle genérico
- Agente: implementador (sonnet) · Depende de: 0 · Paralelo com: 1, 2, 3
- Arquivos: `server/botoes.py`, `server/render_png.py` (só `_desenhar_botoes` e o despacho de `desenhar`), `kindle/kindle-monitor/tap.sh`, `kindle/kindle-monitor/loop.sh`, `tools/preview.py` (`choices=botoes.PAGINAS`), `server/tests/test_botoes.py`, `server/tests/test_paginas_png.py`
- Fazer: E1, E2, E4 e E5.
  - Botões: `botoes.geometria_resumo(largura, altura) -> {"atencao": {x,y,w,h}, "linhas": [{"id","destino","x","y","w","h"}]}`, linhas na ordem atheron, nas, aparelhos, servicos, rotinas, claude, github, ragnarok. `layout("resumo")` as acrescenta como `pagina:<destino>` com `visivel: False`. Toda página ganha o `atualizar` invisível; os outros botões recebem `visivel: True`.
  - Render: `_desenhar_botoes` pula os invisíveis; `aparelhos` cai num `_desenhar_aparelhos` provisório, que só mostra "Aparelhos".
  - Kindle: `tap.sh` ganha um ramo `pagina:*)`, que só aceita `${id#pagina:}` com `[a-z]`, de 1 a 16 letras. O `read_state` dos dois scripts passa a usar `PAGINA) case "$v" in ''|*[!a-z]*) ;; *) [ ${#v} -le 16 ] && PAGINA=$v ;; esac ;;`.
  - `TapShTest`: todo id de `PAGINAS` casa com `^[a-z]{1,16}$`; os dois `case` são o padrão genérico; um trecho rodado com `busybox sh` aceita `aparelhos` e recusa `Aparelhos`, `a1`, `../x` e 17 letras.
  - `test_paginas_png`: pular os invisíveis nas checagens de coordenadas e de inversão; NAV com 6 abas, sem `atualizar`.
- Pronto quando: `tests.test_botoes`, `tests.test_paginas_png` e `tests.test_botoes_txt` passam, e `busybox sh -n` e `shellcheck` nos dois scripts não trazem achado novo.

### 5. Alertas na tela, no texto e na config
- Agente: implementador (sonnet) · Depende de: 1, 4 · Paralelo com: 3, 10
- Arquivos: `server/render_png.py` (`_atencao`, `_card_atencao`), `server/render.py` (`_linhas_catalogo`), `server/coletores.py` (`Coletor.coletar`: `m["limiares"] = alertas.limiares(cfg.get("limiares"))`), `server/config.exemplo.json` e `deploy/config.atheron.json` (bloco `limiares` de E8), testes `test_render_png`, `test_render`, `test_coletores`
- Fazer:
  - `_atencao(m, kv)` passa a ser `alertas.avaliar(m, m.get("limiares"), kv)`. O `/tela.txt` usa a mesma lista.
  - Formas: crítico ✕ (`falha`); aviso `!` (forma nova `_forma(..., "aviso")`, triângulo com "!"); leve ○ (`parado`).
  - Título `ATENCAO (n)`, invertido quando há crítico; no máximo 6 itens mais "+N".
- Pronto quando: os três módulos passam, e um teste confirma (espiando `c.texto`) que o disco `/` a 91% mostra o alerta e não "Tudo em ordem".

### 6. Tela inicial
- Agente: implementador (sonnet) · Depende de: 3, 5 · Paralelo com: 10
- Arquivos: `server/render_png.py` (`_desenhar_resumo`, `_cabecalho`, novos `_linhas_resumo` e `_linha_sistema`), `server/tests/test_render_png.py`
- Fazer:
  - `_linhas_resumo(m, itens, kv, alertas) -> [{"id","icone","titulo","valor","detalhe","estado"}]` é pura. `estado` é o pior nível dos alertas daquele `sistema`, ou `"sem_dados"`.
  - Conteúdo, como no mock do desenho:
    - ATHERON: CPU, RAM, °C e `/`; NAS: os discos que não são `/`.
    - APARELHOS: "sem dados" na tailnet, com a bateria do Kindle e do S10 no detalhe.
    - SERVICOS: "N de M ok", com o detalhe por grupo.
    - ROTINAS e GITHUB: "sem dados"; CLAUDE: 5h e semanal; RAGNAROK: jogadores, com as portas no detalhe.
  - `_linha_sistema`, nas caixas de `geometria_resumo`: ícone de 40 px, forma, título em negrito 26, valor em negrito 34, detalhe regular 26. Cabeçalho: host, `_icone_sync` e HH:MM.
  - Saem da tela inicial os tiles, os chips, os grupos e `_linha_claude_s10`. Ajustar os testes que espiam essas funções (`test_render_png.py` ~l.192).
- Pronto quando: `tests.test_render_png` e `tests.test_paginas_png` passam; `_linhas_resumo` é testada com `m` vazio, completo e com tipos errados; nada sai das caixas (canvas estrito); com 12 alertas aparecem 6 mais "+6".

### 7. Navegação com ícones e escala fixa
- Agente: implementador (sonnet) · Depende de: 6 · Paralelo com: 10
- Arquivos: `server/render_png.py` (`_botao`, `_desenhar_botoes`), `server/botoes.py` (campo `icone` na NAV), `server/tests/test_paginas_png.py`
- Fazer: na NAV, ícone de 30 px centrado em cima e rótulo sempre em negrito 26, sem cair para outro tamanho; a aba atual fica invertida. Botões de linha e de ação seguem a regra atual.
- Pronto quando: um teste espia `c.texto` e confirma todos os rótulos da NAV em 26; outro confirma pixels de ícone na metade de cima de cada aba.

### 8. Sistema e Ações sem repetição
- Agente: implementador (sonnet) · Depende de: 7 · Paralelo com: 10
- Arquivos: `server/render_png.py` (`_blocos_detalhes`, `_desenhar_comandos`; remover `_card_chips`, `_card_grupos`, `_tiles`, `_tile` e `_linha_claude_s10`, se ficarem sem uso), `server/tests/test_render_png.py`, `server/tests/test_render_v5.py`
- Fazer:
  - Sistema: mantém discos, memória, temperaturas, carga, uptime, I/O e histórico; ganha o cartão ROTINAS ("sem dados" enquanto não houver `m["rotinas"]`); saem Kindle, grupos, Ragnarok e pares.
  - Ações: ficam ações rápidas, ajustes e últimos comandos; saem ATENÇÃO e a grade.
- Pronto quando: as duas páginas passam nos testes com `caso_cheio()` e com `{}`, e "TODOS OS SERVICOS" e "SERVICOS POR GRUPO" não aparecem em página nenhuma.

### 9. Aparelhos (E1), Dev (E1) e texto
- Agente: implementador (sonnet) · Depende de: 8 · Paralelo com: 10
- Arquivos: `server/render_png.py` (`_desenhar_aparelhos`, `_desenhar_claude`), `server/render.py` (ramo `aparelhos` em `render_texto`), `server/tests/test_render_png.py`, `server/tests/test_render.py`
- Fazer:
  - Aparelhos: cartão TAILNET ("sem dados"), `_card_kindle`, `_card_s10` e `_card_par`.
  - Dev: `_card_claude` mais os cartões SESSOES e GITHUB ("sem dados"); sem `claude`, "Claude desligado na config".
  - Texto: ramo `aparelhos` com Kindle e S10.
- Pronto quando: as 6 páginas passam em todos os casos de `PaginasEstritasTest` e `render_texto(..., pagina="aparelhos")` sai só em ASCII.

### 10. Prévias com estados
- Agente: implementador (sonnet) · Depende de: 4 · Paralelo com: 5–9
- Arquivos: `tools/preview.py`
- Fazer: `--estado ok|alertas|velho` (`ok`: tudo dentro dos limiares; `alertas`: disco a 91%, 2 serviços em falha, Kindle a 12%; `velho`: inventário de 120 s e limites do Claude com `velho`). `--todas DIR` grava `<pagina>-<estado>.png` de todas as páginas.
- Pronto quando: `python3 -I tools/preview.py --todas <scratchpad>/prev1` gera 18 PNGs sem exceção.

### 11. Docs da Entrega 1
- Agente: escriba (haiku) · Depende de: 9 · Paralelo com: 12
- Arquivos: `CLAUDE.md`, `server/README.md`
- Fazer: documentar abas, toque no relógio, linhas da tela inicial como botões, motor e `limiares` (tabela E6), como regerar os ícones, Kindle com página genérica e comando de instalação apontando para o worktree.
- Pronto quando: `grep -n "alertas.py\|limiares\|aparelhos" CLAUDE.md server/README.md` acha as três coisas.

### 12. Revisão da Entrega 1
- Agente: revisor (sonnet) e python-reviewer, em paralelo · Depende de: 9, 10 · Paralelo com: 11
- Fazer: revisar `git diff origin/master...HEAD` contra este plano. Foco: regras e limiares; nada fora da caixa; invisíveis fora do desenho mas presentes no `/botoes.txt`; `case` do Kindle sem brecha (`../`, maiúscula, 17 letras). Os achados voltam ao `implementador`, um commit por correção.
- Pronto quando: nenhum achado bloqueante em aberto.

### 13. Suíte e conferência 1 com o dono
- Agente: executor (haiku) para a suíte; eu para as prévias · Depende de: 11, 12
- Fazer: suíte em segundo plano (`<scratchpad>/km-e1.log`), comparada com a linha de base; `tools/preview.py --todas <scratchpad>/prev-e1` e `--cheia`; mostrar ao dono Início (3 estados), Aparelhos, Sistema, Dev e Ações.
- Pronto quando: suíte verde e prévias aprovadas. Pedido de ajuste volta para as tarefas 6–9.

### 14. Instalação da Entrega 1
- Agente: dono (root) e eu · Depende de: 13
- Fazer: Runbook R1–R3.
- Pronto quando: as 6 páginas respondem por `curl`; `/botoes.txt?pagina=resumo` tem 8 linhas `pagina:` e um `atualizar`; toques em abas e linhas aparecem no `/tmp/kindle-monitor.log` do Kindle; o alerta de disco está na tela.

## Entrega 2

### 15. Executor: aparelhos da tailnet
- Agente: implementador (sonnet) · Depende de: 14 · Paralelo com: 17, 18, 19
- Arquivos: `deploy/kindle-monitor-executor.py`, `deploy/kindle-monitor-inventario.service`, `server/tests/test_executor_aparelhos.py` (novo), `server/tests/test_deploy_units.py`
- Fazer:
  - `validar_aparelhos(lista)` (E8), e `carregar_cfg` passa a ler `aparelhos`.
  - `parse_tailscale(texto, catalogo) -> dict` (E7), casando o 1º rótulo do `DNSName` com `nome`.
  - `inventariar` chama `["tailscale","status","--json"]` (timeout 10 s) só se houver catálogo e grava `aparelhos.json` com `_gravar_arquivo`. Se o comando falhar, grava `erro` e todos com `online: null`; `servicos.json` continua sendo gravado.
  - Unit: `ReadWritePaths=-/run/tailscale/tailscaled.sock`, a validar no host. Ajustar o teste "mesmo endurecimento do executor" para aceitar essa linha só no inventário.
- Pronto quando: os testes passam, cobrindo:
  - JSON real anonimizado, com um peer `empresa-x-x` fora do catálogo que não aparece no arquivo; catálogo com `nome` contendo `empresa-x`, que é recusado;
  - JSON truncado; timeout; tipos errados; saída sem `@` e sem endereço IP.

### 16. Executor: rotinas
- Agente: implementador (sonnet) · Depende de: 15 · Paralelo com: 17, 18, 19
- Arquivos: `deploy/kindle-monitor-executor.py`, `server/tests/test_executor_rotinas.py` (novo)
- Fazer: `validar_rotinas` (E8) e `coletar_rotinas(catalogo, executar, stat=os.stat, listar=os.scandir, agora)`, que grava `rotinas.json`:
  - timers: uma chamada `systemctl show -p Id,Result,ExecMainExitTimestamp --timestamp=unix <svc...>`; `Result=success` → `ok`, outro → `falha`; `ultima_em` vem do `@epoch`;
  - arquivos: `mtime` do arquivo, ou o maior `mtime` das entradas diretas do diretório, sem seguir symlink e sem ler conteúdo;
  - unidades em falha: `systemctl list-units --failed --plain --no-legend --no-pager`, 1ª coluna, saneada.
- Pronto quando: os testes passam com saída fake do `systemctl`, diretório temporário datado, alvo inexistente (`desconhecido`), symlink (ignorado) e mais de 5 unidades em falha (corta em 5, com `n` correto).

### 17. Servidor: aparelhos e rotinas
- Agente: implementador (sonnet) · Depende de: 14 · Paralelo com: 15, 16, 18, 19
- Arquivos: `server/ecossistema.py` (novo), `server/coletores.py` (`Coletor.__init__` e `coletar`), `server/tests/test_ecossistema.py` (novo)
- Fazer:
  - `validar_aparelhos` e `validar_rotinas`: cópia de E8.
  - `montar_aparelhos(catalogo, texto, agora)` → `{"inventario": "ok"|"velho"|"ausente", "itens": [{"id","rotulo","icone","online","offline_min","conexao","alerta_offline_min"}]}`.
  - `montar_rotinas(catalogo, texto, agora)` → `{"inventario", "itens": [{"id","rotulo","resultado","ultima_em","idade_h","max_idade_h","atrasada"}], "unidades_falhas": {"n","nomes"}}`.
  - Validade de 60 s, como `montar_servicos_kindle`; nunca levanta. `m["aparelhos"]` e `m["rotinas"]` só existem com catálogo.
- Pronto quando: `tests.test_ecossistema` passa com arquivo ausente, velho, do futuro, JSON inválido, id fora do catálogo (ignorado) e rótulo com acento ou controle (sai ASCII).

### 18. dotfiles: estado das sessões
- Agente: implementador (sonnet) · Depende de: 0 · Paralelo com: 15, 16, 17, 19
- Arquivos: `bin/claude-sessao` (novo, stdlib, `#!/usr/bin/env -S python3 -I`), `claude/settings.json`, `claude/statusline.sh`, `tests/test_claude_sessao.py` (novo), `tests/test_statusline.py`
- Fazer:
  - `claude-sessao evento|batimento [--dir D] [--agora N]`: `evento` lê o JSON do hook no stdin (`session_id`, `cwd`, `hook_event_name`); `batimento` lê o da statusline.
  - Regras de E10. Gravação atômica 0644 em `D/sessoes/` (cria o diretório 0755 com `chmod` explícito, porque o umask do `claude` é 002). Sai 0 em silêncio em qualquer erro.
  - `settings.json`: acrescentar, sem substituir, `claude-sessao evento` (timeout 5) em `UserPromptSubmit`, `Stop` e `SessionEnd`, e uma entrada nova `Notification`.
  - `statusline.sh`: no mesmo `if` do `claude-limites`, chamar `claude-sessao batimento` em segundo plano.
- Pronto quando: `uv run --no-project --with pytest pytest tests/test_claude_sessao.py tests/test_statusline.py` passa, cobrindo:
  - cada evento, e `SessionEnd` apagando o arquivo; batimento sem mudar `estado`/`desde`; poda de 24 h;
  - `id` `../x` e `a/b` recusados; `cwd` com `/empresa-x/` e `CLAUDE_CONFIG_DIR=~/.claude-<conta-de-trabalho>` sem gravar;
  - diretório ausente em silêncio; entradas antigas do `settings.json` preservadas.

### 19. dotfiles: `claude-github` e timer
- Agente: implementador (sonnet) · Depende de: 0 · Paralelo com: 15, 16, 17, 18
- Arquivos: `bin/claude-github` (novo), `claude/painel/systemd/claude-github.service` e `.timer` (novos), `tests/test_claude_github.py` (novo), `tests/test_timers_usuario.py` (acrescentar o timer)
- Fazer:
  - Uma chamada `gh api graphql`, com argv em lista: `repositoryOwner(login:"brno01")`, repos `ownerAffiliations: OWNER` por `PUSHED_AT`, até 30 (conferir os nomes dos campos no schema antes). Por repo: PRs `OPEN` (`number`, `title`, `isDraft`, `statusCheckRollup.state` do último commit) e `defaultBranchRef { name target { ... on Commit { statusCheckRollup { state } } } }`. Descartar `isArchived` e todo `owner.login` diferente de `brno01`.
  - `normalize(resposta) -> dict` (E7), pura. Títulos: NFKD, sem combinantes nem controles, ASCII, até 80 caracteres. Estado: `SUCCESS` → `ok`; `FAILURE`/`ERROR` → `falha`; `PENDING`/`EXPECTED` → `pendente`.
  - Se o `gh` falhar, não grava e sai 1.
  - Units: service `oneshot` com `ExecCondition=/usr/bin/test -w /var/lib/claude-uso`; timer com `OnStartupSec=1min` e `OnUnitActiveSec=5min`.
- Pronto quando: `uv run --no-project --with pytest pytest tests/test_claude_github.py tests/test_timers_usuario.py` passa, com:
  - fixture GraphQL com repo de outro dono, arquivado, título com emoji, ANSI e 500 caracteres, e mais de 20 PRs;
  - um `gh` falso falhando, que mantém o arquivo antigo;
  - `systemd-analyze --user verify` das duas units sem erro.

### 20. dotfiles: links e docs
- Agente: mecanico (haiku) · Depende de: 18, 19
- Arquivos: `bin/claude-mirror` (`install_links`, linha ~24: `claude-sessao` e `claude-github`), `README.md` (linha do painel do Kindle, ~150), `claude/CLAUDE.md` se citar o painel
- Pronto quando: a suíte inteira do dotfiles passa e `grep -n "claude-sessao\|claude-github" bin/claude-mirror README.md` acha os dois.

### 21. Servidor: sessões e GitHub
- Agente: implementador (sonnet) · Depende de: 17 · Paralelo com: 15, 16, 18, 19, 22, 25
- Arquivos: `server/dev_fontes.py` (novo), `server/coletores.py` (`Coletor` ganha `listar_dir=os.scandir`; `coletar`), `server/tests/test_dev_fontes.py` (novo)
- Fazer:
  - `coletar_sessoes(dir, listar, ler, agora)`: lê até 50 arquivos regulares (`is_file(follow_symlinks=False)`, nome `<id>.json`, até 4 KB) e devolve `{"itens": [{"projeto","estado","desde_s"}] (12 mais recentes), "total", "esperando"}` ou ND.
  - `coletar_github(caminho, ler, agora)`: devolve `{"prs","ci","abertos","ci_falhas","idade_s","velho"}`, com `velho` acima de 1200 s e títulos saneados de novo, cortados em 60.
  - `m["claude"]["sessoes"]` só existe com `claude.sessoes`; `m["github"]`, só com `github`.
- Pronto quando: `tests.test_dev_fontes` passa com symlink, arquivo grande, JSON ruim, estado desconhecido, sessão com mais de 12 h, título hostil e diretório ausente.

### 22. Página Aparelhos e rotinas em Sistema
- Agente: implementador (sonnet) · Depende de: 17 · Paralelo com: 21, 25
- Arquivos: `server/render_png.py` (`_desenhar_aparelhos`, cartão ROTINAS, linhas APARELHOS e ROTINAS de `_linhas_resumo`), `server/render.py`, `server/tests/test_render_png.py`, `server/tests/test_render.py`
- Fazer:
  - TAILNET: uma linha por aparelho, com ícone de 40 px, rótulo, forma (● online, ○ offline, ? sem dado) e "direto/relay" ou "visto ha N h". Linha APARELHOS: "N de M online", com rótulos e as baterias do Kindle e do S10 no detalhe.
  - ROTINAS: forma, rótulo, "ha N h"/"falhou"/"atrasada", e uma linha "N unidades em falha". Linha da tela inicial: "N de M ok" e a mais recente.
- Pronto quando: os testes passam com 16 aparelhos (cabem ou cortam com "+N"), rótulo hostil, inventário velho e catálogo vazio.

### 23. Página Dev e linhas CLAUDE/GITHUB
- Agente: implementador (sonnet) · Depende de: 21, 22
- Arquivos: `server/render_png.py`, `server/render.py`, `server/tests/test_render_png.py`, `server/tests/test_render.py`
- Fazer: cartão SESSOES (projeto, estado, "ha N min"); cartão GITHUB (PRs como `repo#n titulo`; CI por repo, primeiro os que não estão ok, depois "N ok"); na tela inicial, CLAUDE com "N sessoes, M esperando" e GITHUB com "N PRs abertos  CI ok/falha".
- Pronto quando: os testes passam com 20 PRs, título de 80 caracteres, 12 sessões e as duas fontes ausentes.

### 24. Config de produção
- Agente: mecanico (haiku) · Depende de: 17, 21
- Arquivos: `deploy/config.atheron.json`, `server/config.exemplo.json` (com `_comentario_*`)
- Fazer: E8 completo.
  - `aparelhos` (peers conferidos em 18/11; rótulo/ícone): nomad/notebook; S22/celular (`galaxy-s22`); S10/celular (`galaxy-s10`); iPhone/celular (`iphone-12`); Kindle/leitor (`kindle-monitor`); Gateway/rede (`cerberus-gw`, `alerta_offline_min: 10`); games/jogo.
  - `rotinas`: `cerberus-vault-backup.service` (26 h); arquivo `/srv/nas/backups/vaultwarden` (26 h); arquivo `/var/lib/claude-uso/tokens.json` (1 h). Syncthing do cofre e segundo cérebro: alvo a confirmar em R5 (`/srv/nas/vault` é do grupo `cofre`, 0770, e o `claude` não lista).
  - Chaves `claude.sessoes` e `github.resumo`.
- Pronto quando: um teste carrega `config.atheron.json` com os validadores do servidor e do executor, sem erro e sem `nome` contendo `empresa-x`.

### 25. Prévias da Entrega 2
- Agente: mecanico (haiku) · Depende de: 10, 17, 21 · Paralelo com: 22, 23
- Arquivos: `tools/preview.py`
- Fazer: acrescentar ao `exemplo()`: `aparelhos` (7, um offline), `rotinas` (4, uma atrasada em `alertas`), `claude.sessoes` (3, uma esperando há 25 min) e `github` (2 PRs, com CI falhando em `alertas`).
- Pronto quando: `--todas <scratchpad>/prev2` gera 18 PNGs sem exceção.

### 26. Casos de borda e paridade
- Agente: testador (sonnet) · Depende de: 16, 17, 21
- Arquivos: `server/tests/test_paridade_catalogos.py` (novo), `server/tests/test_ecossistema.py`, `server/tests/test_dev_fontes.py`
- Fazer:
  - Paridade: executor e servidor aceitam e recusam a mesma tabela de catálogos (≥ 20 casos).
  - Ponta a ponta: `aparelhos.json` do executor fake → `montar_aparelhos` → `alertas.avaliar` dispara o alerta do gateway offline.
  - Nenhum texto que chega à tela passa de 48/60 caracteres ou foge do ASCII.
- Pronto quando: os módulos passam e os casos novos falham se a sanitização for removida (conferir revertendo localmente).

### 27. Docs da Entrega 2
- Agente: escriba (haiku) · Depende de: 23, 24 · Paralelo com: 28
- Arquivos: `server/README.md` (inventário, formatos E7, chaves E8), `CLAUDE.md` (páginas, fontes, pendências)
- Pronto quando: os 4 formatos de JSON e as 5 chaves de config estão documentados.

### 28. Revisão da Entrega 2
- Agente: revisor, python-reviewer e security-reviewer, em paralelo · Depende de: 20, 23, 24, 25, 26
- Fazer:
  - security-reviewer: diff do executor e da unit, `claude-sessao`, `claude-github` e a sanitização no servidor. Foco: argv fixo e sem shell; path traversal no id da sessão; symlink; prefixos de `arquivo`; peer da empresa-x; nada de IP ou e-mail nos JSON; `nobody` só lendo.
  - revisor: diff dos dois repos contra este plano.
  - Os achados voltam ao `implementador`.
- Pronto quando: nenhum achado bloqueante em aberto.

### 29. Suítes e conferência 2 com o dono
- Agente: executor (haiku) para as suítes; eu para as prévias · Depende de: 27, 28
- Fazer: suíte do kindle-monitor em segundo plano, suíte do dotfiles e prévias `--todas` para o dono.
- Pronto quando: as duas suítes estão verdes e as prévias aprovadas.

### 30. Instalação da Entrega 2
- Agente: dono (root) e eu · Depende de: 29
- Fazer: Runbook R4–R7.
- Pronto quando: `aparelhos.json` e `rotinas.json` se renovam a cada 15 s; o S22 aparece offline com o Wi-Fi desligado; abrir e fechar uma sessão do Claude muda a contagem; `github.json` bate com `gh pr list`.

## Paralelismo

| Pode rodar junto | Sequencial (motivo) |
|---|---|
| 1 ∥ 2 ∥ 4; 3 ∥ 5; 10 ∥ 5–9; 11 ∥ 12 | 4 → 5 → 6 → 7 → 8 → 9 (`render_png.py`) |
| 15 ∥ 17 ∥ 18 ∥ 19 (repos e arquivos distintos) | 15 → 16 (mesmo executor) |
| 21 ∥ 22 (módulos distintos); 25 ∥ 22, 23 | 17 → 21 (`coletores.py`); 22 → 23 (`render_png.py`) |

## Runbook

Antes de cada instalação, a suíte passa e o dono aprovou as prévias. O comando "Atualizar o atheron" do `CLAUDE.md` aponta para `personal/kindle-monitor`; aqui ele usa o worktree.

- **R1. Backup (dono, root).** `sudo bash -c 'D=/root/backup/kindle-monitor-antes-ecossistema-$(date +%F-%H%M); install -d -m 0700 "$D"; cp -a /opt/kindle-monitor /etc/kindle-monitor /etc/systemd/system/kindle-monitor* /etc/tmpfiles.d/kindle-monitor*.conf "$D"/; ls -la "$D"'`.
  - Verificar: a listagem mostra os quatro itens.
  - Desfazer qualquer etapa: copiar de volta `"$D"/kindle-monitor` para `/opt/`, a config para `/etc/kindle-monitor/` e as units; depois `systemctl daemon-reload && systemctl restart kindle-monitor.service kindle-monitor-inventario.timer`.
- **R2. Instalar o servidor (dono, root).** Comando "Atualizar o atheron" do `CLAUDE.md`, com `R=~/development/worktrees/kindle-monitor-ecossistema`.
  - Verificar (eu): `systemctl is-active kindle-monitor`; `curl -s "http://100.64.0.1:8765/botoes.txt?pagina=resumo"`; `curl -so <scratchpad>/<p>.png ".../tela.png?pagina=<p>"` das 6 páginas, lendo as imagens; `journalctl -u kindle-monitor -n 20`.
  - Desfazer: R1.
- **R3. Kindle (eu, do nomad, onde existe o apelido `kindle-lan`).**
  - Para cada X entre `loop.sh` e `tap.sh`: `ssh kindle-lan 'cat > /tmp/X.novo' < kindle/kindle-monitor/X`, depois `ssh kindle-lan 'sh -n /tmp/X.novo && cp /mnt/us/kindle-monitor/X /mnt/us/kindle-monitor/X.antes-ecossistema && cp /tmp/X.novo /mnt/us/kindle-monitor/X'`. Em seguida, `monitor-desligar.sh` e `monitor-ligar.sh`.
  - Verificar: `ssh kindle-lan 'tail -20 /tmp/kindle-monitor.log'` mostra `page aparelhos` depois do toque; o dono toca cada aba e cada linha.
  - Desfazer: copiar `X.antes-ecossistema` de volta e religar.
- **R4. Backup da Entrega 2 (dono).** Igual a R1, em um diretório novo.
- **R5. Confirmar caminhos (dono, root, só leitura).** `sudo ls -lt /srv/nas/vault | head` e `sudo systemctl status cerberus-syncthing --no-pager`. O dono escolhe os alvos `arquivo` do Syncthing e do segundo cérebro; a tarefa 24 recebe um commit de ajuste.
- **R6. Instalar o servidor (dono).** Igual a R2; a unit do inventário passa a acessar o socket do Tailscale.
  - Verificar: `sudo cat /run/kindle-monitor/status/{aparelhos,rotinas}.json`; `journalctl -u kindle-monitor-inventario -n 20` sem erro. Se o hardening bloquear o socket, seguir a ordem de afrouxamento do `server/README.md`.
  - Desfazer: R4.
- **R7. Publicadores do dotfiles (eu, usuário `claude`).**
  - Pré-requisito: a branch `feat/bypass-e-painel-dev` precisa estar no checkout `~/development/dotfiles`. **Decisão do dono:** merge local ou PR.
  - Depois: (1) `claude-mirror install`; (2) `ln -sfn "$PWD/claude/painel/systemd/claude-github."{service,timer} ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable --now claude-github.timer`; (3) abrir uma sessão nova.
  - Verificar: `ls /var/lib/claude-uso/sessoes`; `jq '.prs|length' /var/lib/claude-uso/github.json` contra `gh pr list`.
  - Desfazer: `systemctl --user disable --now claude-github.timer`; reverter o commit dos hooks; `rm -r /var/lib/claude-uso/sessoes`.

## Verificação final

- kindle-monitor: `cd server && (umask 022; python3 -I -m unittest discover -s tests)` em segundo plano com log. O total é maior que a linha de base, sem falhas.
- dotfiles: `uv run --no-project --with pytest pytest tests` sem falhas. Kindle: `busybox sh -n` e `shellcheck` nos dois scripts.
- No ar: as 6 páginas por `curl`; toque em cada aba e em cada linha; alerta de disco visível; S22 offline; contagem de sessões; GitHub contra `gh`.
- Linha de base (tarefa 0): kindle-monitor ___ testes / ___ falhas; dotfiles ___ / ___.
