# Página "Claude/S10" no Kindle — desenho

Data: 16/11/2026. Repositórios tocados: `kindle-monitor` (principal), `galaxy-s10`, `dotfiles`.

## Intenção

O dono quer ver no monitor e-ink do Kindle, sem abrir nada:

1. **Uso da conta do Claude**: quanto já gastou da janela de 5 horas e do limite semanal do plano, quando cada um volta, e quantos tokens gastou (hoje e nos últimos 7 dias), com o **ícone do Claude**.
2. **Estado do Galaxy S10** (nó do homelab ligado na USB do atheron): bateria e os três caminhos de acesso (USB, adb sem fio, VNC).

O porquê: o limite do plano é o que interrompe o trabalho; ver a porcentagem e a hora de volta de relance evita surpresa. O S10 é a âncora de emergência do homelab; ver que os caminhos estão ✓ e a bateria está saudável dá confiança sem abrir `s10 status`.

## Decisões do dono

- **Onde**: página nova (5º botão de navegação, rótulo "Claude/S10") com os cartões completos **e** uma linha fixa no rodapé do Resumo para ver de relance.
- **Contas**: **só a conta pessoal** (`~/.claude` do usuário `claude` no atheron). As contas de trabalho do nomad ficam de fora; o formato dos arquivos deve permitir acrescentar contas depois sem quebrar. O dono escolheu sabendo que "nada novo no nomad": os limites são da conta inteira, mas só sessões **no atheron** atualizam o retrato (o atheron é o servidor de desenvolvimento onde as sessões do Claude rodam). Sessões da conta pessoal abertas no nomad não publicam nada; o cartão mostra a idade do dado.
- **Hora sem segundos** no cabeçalho de todas as páginas (já feito à parte: `_cabecalho` usa `%H:%M`).

## Objetivos

- Cartão CLAUDE: ícone + título; janela 5 h e semanal, cada uma com barra, porcentagem e "volta HH:MM" (ou "volta qui 02:00" quando não é hoje); linha de tokens: hoje e 7 dias, com o custo equivalente em preço de API.
- Cartão S10: bateria (nível, carregando/cheia/descarregando, temperatura), os caminhos USB, sem fio e VNC com ✓/✗ (Tailscale e ssh do Termux como detalhe menor), e os avisos que o guardião já calcula (temperatura alta, 100 % por horas).
- Linha do Resumo (rodapé, ancorada como a do Ragnarok): ícone, `5h NN%`, `sem NN%`, e `S10 NN%` + estado de carga + três marcas ✓/✗.
- Dados velhos são mostrados com a idade, nunca como se fossem atuais.

## Não objetivos

- Contas de trabalho / nomad (pode vir depois).
- Limite semanal por modelo e saldo de uso extra: **não existem** em fonte documentada; não inventar.
- Ações (botões) na página nova: ela só mostra.

## Anti-objetivos (falha mesmo funcionando)

- Usar o endpoint **não documentado** de uso da Anthropic com o token OAuth: os termos de consumidor proíbem acesso automatizado; a fonte é só o JSON documentado do statusline.
- Dar ao kindle-monitor o grupo `cerberus-s10` para ler o `estado.json`: esse grupo abre o socket do adb, ou seja, shell no celular.
- Qualquer listener de rede novo, segredo no Kindle, ou IP/porta/serial do S10 num arquivo legível por todos.
- O kindle-monitor deixar de ser só leitura ou passar a ler `/home` (`ProtectHome=yes` fica).

## Restrições

- kindle-monitor: Python 3 só stdlib no atheron (sem Pillow nem `uv`); roda como `nobody`, `ProtectHome=yes`, só leitura; testes com `python3 -I -m unittest discover -s tests`. Tela 1236×1648, tons de cinza.
- galaxy-s10: guardião `cerberus-s10` como usuário `cerberus-s10`; `/run/cerberus-s10` é 0750 e assim fica. Convenções do repo: instalador "Passo do USUÁRIO" com `--check`/`--undo`, backup `*.antes-s10`, idempotente, testes antes de instalar.
- dotfiles: `claude/statusline.sh` roda a cada atualização do statusline (no atheron e no nomad); não pode ficar lento nem falhar visivelmente. `bin/claude-uso` é Python stdlib com testes em `tests/test_claude_uso.py`.
- O dado de limite do statusline (`rate_limits.five_hour|seven_day.used_percentage` e `.resets_at`, epoch em segundos) só existe em assinatura claude.ai, só depois da primeira resposta da sessão, cada janela pode faltar, e só se renova enquanto há sessão ativa (doc: code.claude.com/docs/en/statusline).
- Marca: ícone do Claude só neste painel privado (as diretrizes de marca da Anthropic proíbem sugerir endosso); nada público.

## Abordagens consideradas

**Onde mostrar** (escolha do dono: A).
- A. Página nova + linha no Resumo. Detalhe completo sem espremer as páginas cheias, e leitura de relance no Resumo. Custa um 5º botão e um bloco ancorado no Resumo.
- B. Só página nova: menos mudança, mas exige tocar para ver.
- C. Só no Resumo, compacto: sem página nova, mas espreme blocos que já disputam espaço.

**De onde vem o limite do Claude** (escolha do desenho: 1).
1. O statusline grava um retrato. Fonte documentada; dado fresco só com o Claude em uso, o que se resolve mostrando a idade.
2. Endpoint de uso não documentado: dado sempre fresco, mas fora dos termos. Rejeitado.
3. OpenTelemetry do Claude Code: só tem tokens e custo, não tem limite, e exigiria um coletor novo. Rejeitado para limite.

**Tokens** (escolha do desenho): reutilizar o `claude-uso` (já soma os transcripts) com saída JSON, rodado por um timer do usuário `claude` (linger já ligado). OpenTelemetry foi descartado: precisaria de um coletor só para isto.

**Dados do S10** (escolha do desenho: i).
- i. O guardião publica um resumo próprio, sem nada sensível, num diretório legível por todos.
- ii. O kindle-monitor entra no grupo `cerberus-s10`: dá acesso ao adb. Rejeitado.
- iii. O guardião serve HTTP: listener novo. Rejeitado.

## Como funciona

```
statusline.sh (a cada atualização, conta pessoal) ──► /var/lib/claude-uso/limites.json
claude-uso --painel (timer do usuário claude, 5 min) ► /var/lib/claude-uso/tokens.json
cerberus-s10 (a cada ciclo, 30 s) ─────────────────► /run/cerberus-s10-publico/resumo.json
                                                         │
kindle-monitor (nobody) lê os três ──► m["claude"], m["s10"] ──► página "claude" + linha no Resumo
```

### 1. Limites (dotfiles, `claude/statusline.sh`)
- Só quando a conta é a pessoal (`CLAUDE_CONFIG_DIR` vazio ou `~/.claude`) **e** `/var/lib/claude-uso` existe e é gravável; senão não faz nada (assim o nomad e as contas de trabalho seguem iguais).
- Grava só se algum valor mudou ou se o arquivo tem mais de 60 s, de forma atômica (temporário + `mv`), em segundo plano, sem atrasar a linha.
- Sessões simultâneas (escolha do desenho): por janela, `volta_em` maior sempre vence; com o mesmo `volta_em`, a porcentagem nunca recua (uma sessão parada não sobrescreve um valor mais novo com um mais velho); `volta_em` menor que o gravado é ignorado. A comparação é feita ao gravar (ler o arquivo atual antes).
- Formato (`limites.json`, 0644):
  ```json
  {"versao": 1, "conta": "pessoal", "atualizado_em": 1763300000,
   "cinco_horas": {"pct": 34, "volta_em": 1763310000},
   "semanal": {"pct": 61, "volta_em": 1763600000}}
  ```
  Janela ausente no JSON do statusline = chave ausente aqui.

### 2. Tokens (dotfiles, `bin/claude-uso`)
- O `--json` que já existe (`bin/claude-uso:149`, lista de linhas do relatório) **fica igual**. Nova opção `--painel` (com `--conta pessoal`; escolha do desenho): totais de hoje e dos 7 dias (entrada, saída, cache leitura, cache escrita, soma, custo equivalente) e o total por modelo nos 7 dias. "Hoje" é o dia civil no fuso local do atheron (`America/Sao_Paulo`), igual ao filtro por data que o `scan` já faz.
- Formato (`tokens.json`, 0644): `{"versao": 1, "conta": "pessoal", "gerado_em": <epoch>, "hoje": {...}, "sete_dias": {...}, "por_modelo_7d": [{"modelo": "...", "tokens": N, "custo_usd": x}]}`.
- Timer de usuário `claude-uso-painel.timer` (a cada 5 min, `Persistent=true`) instalado pelo `install.sh --servidor`; grava atômico.

### 3. Diretório `/var/lib/claude-uso`
- Criado como root pelo instalador do kindle-monitor (`deploy/instalar-atheron.sh`), dono `claude`, 0755, via um `tmpfiles.d` próprio (o instalador do kindle-monitor não tem `--check`/`--undo`; segue o padrão dele). Se a máquina não tiver o usuário `claude`, o passo é pulado com aviso.

### 4. Resumo público do S10 (galaxy-s10, `atheron/cerberus-s10`)
- A cada ciclo, junto com o `estado.json`, grava `resumo.json` (0644, atômico) em `/run/cerberus-s10-publico/` (diretório 0755 do usuário `cerberus-s10`, criado por `tmpfiles.d` que o `user-step-s10.sh` instala; `--check`/`--undo` cobrem).
- A unit tem `ProtectSystem=strict` e `UMask=0007` (escolha do desenho): acrescentar só `ReadWritePaths=/run/cerberus-s10-publico` e fazer `chmod 0644` explícito no temporário antes do `os.replace`; atualizar o `atheron/tests/test_installer.sh`, que confere as opções da unit. Nenhuma outra proteção da unit muda.
- Reinício do guardião (escolha do desenho): o `resumo.json` antigo fica e envelhece (o Kindle passa a "sem dados" depois de 2 min); o primeiro ciclo o sobrescreve. `--undo` remove o diretório.
- Conteúdo **só por lista de campos permitidos** (nunca copiar o estado inteiro):
  ```json
  {"versao": 1, "gerado_em": 1763300000,
   "bateria": {"nivel": 82, "status": "charging", "temperatura_c": 31.0, "saude": "good"},
   "caminhos": {"usb": true, "adb_sem_fio": true, "tailscale": true, "ssh_termux": true, "vnc": true},
   "avisos": ["S10 temperature 46.0 C >= 45 C"]}
  ```
  Sem IP, porta, serial, nome de rede ou texto de log. `null` quando o caminho é desconhecido (ex.: VNC sem USB).
- Teste obrigatório: o resumo gerado a partir de um estado completo (fixture) não contém nenhuma chave ou valor fora da lista.

### 5. kindle-monitor
- Config: `"claude": {"limites": "/var/lib/claude-uso/limites.json", "tokens": "/var/lib/claude-uso/tokens.json"}` e `"s10": {"resumo": "/run/cerberus-s10-publico/resumo.json"}`; chave ausente = recurso desligado (a linha do Resumo some; o botão da página continua, para a barra não mudar de forma, e a página mostra "Claude/S10 desligado na config"). Vai em `config.exemplo.json` e `deploy/config.atheron.example.json`.
- Coletores puros e testados com fixtures, isolados como os demais (`_isolado`): arquivo ausente/inválido vira `n/d`, nunca exceção.
- Regras de exibição:
  - Limite com `volta_em` no passado: mostra `0%` e "renovado" (a janela reiniciou; a próxima sessão atualiza o valor real).
  - `limites.json` com mais de 15 min: acrescenta "há N min / N h" em cinza.
  - `tokens.json` com mais de 20 min: "tokens: há N min".
  - `resumo.json` do S10 com mais de 2 min: "S10 sem dados há N min" e as marcas viram "?".
  - Barra de limite ≥ 90 %: texto em preto/negrito (alerta), como o resto do painel faz.
- Página nova `claude` em `botoes.PAGINAS` e `botoes.NAV`, nos dois renderizadores (`render_png.py` e o texto de `render.py`), com o cartão CLAUDE em cima e o S10 embaixo. A barra já tem 5 botões (Atualizar + 4 páginas); com 6, cada um fica com ~176 px. Rótulo "Claude/S10" se couber no tamanho da barra, senão "Claude" (escolha do desenho).
- A fonte embutida é ASCII + grau + ponto médio: textos sem acento ("ha 2 h", "volta qui 02:00") e nada de ✓/⚡ como caractere.
- Linha no Resumo: bloco ancorado no rodapé (60 px, como o Ragnarok, acima dele quando os dois existem); o encaixe dinâmico do Resumo já encolhe Atenção/chips.
- Marcas ✓/✗/? com as formas desenhadas que já existem (`_forma_ok`/`_forma`), não com glifos (a fonte pré-rasterizada pode não ter esses caracteres).

### 6. Ícone do Claude
- Fonte: o SVG do ícone "Claude" do Simple Icons (arquivo CC0; a marca é da Anthropic).
- Rasterizado **fora do atheron** (no nomad, `uv run --with pillow ...`, como `tools/gerar_fonte.py`) por um `tools/gerar_icones.py` que gera `server/icones_dados.py` (cobertura em 8 bits, nos tamanhos usados: ~40 px no cartão, ~30 px na linha). O módulo gerado é commitado.
- Desenhado pelo mesmo caminho dos glifos (`canvas._glifo_bitmap`), em preto.

## Testes e verificação

- kindle-monitor: coletores (válido, ausente, inválido, velho, `volta_em` passado), layout da página nova e da linha do Resumo (nada sai da imagem, com e sem dados), botão novo; suíte inteira passa; `tools/preview.py` gera o PNG da página para o dono ver antes de instalar.
- galaxy-s10: resumo por lista permitida (teste de vazamento), escrita atômica, `tmpfiles`/instalador com `--check`/`--undo`; `shellcheck` e as suítes do CLAUDE.md.
- dotfiles: `claude-uso --painel` (formato e totais; `--json` antigo inalterado), gravação do retrato pelo statusline (conta pessoal grava, outra conta não, diretório ausente não grava, sem regravar dentro de 60 s sem mudança).
- No ar: depois dos passos de root do dono, `curl -s http://127.0.0.1:8765/tela.txt?pagina=claude` mostra os números reais, e o journal do kindle-monitor não tem erro.

## Passos do dono (root, no atheron)

(Atualizado após a implementação; a ruling R10 substituiu o `install.sh --servidor`.)

1. galaxy-s10: `bash atheron/user-step-s10.sh`, como o dono, com `sudo` onde o script pedir (diretório público e guardião novo).
2. kindle-monitor: copiar `server/` + `deploy/` para `/root/kindle-monitor-deploy/` e rodar `deploy/instalar-atheron.sh` (cria `/var/lib/claude-uso` quando o usuário `claude` existe, instala a config e reinicia).
3. dotfiles: `claude-mirror install` (põe `claude-limites` no PATH) e depois habilitar o timer manualmente, como no README do dotfiles.
4. Kindle: copiar `tap.sh` E `loop.sh` para `/mnt/us/kindle-monitor/` (com a autorização do dono) e tocar em "Monitor Desligar" e "Monitor Ligar" (o laço em execução mantém o código antigo).

## Fica para quem constrói

Nomes internos de funções, desenho exato dos cartões dentro das regras acima, intervalo de redesenho do timer dentro de 5–10 min, ordem dos commits por repositório.
