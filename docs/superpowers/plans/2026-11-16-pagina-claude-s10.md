# Página "Claude/S10" no Kindle — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** mostrar no Kindle os limites (5 h e semanal) e os tokens da conta pessoal do Claude, com ícone, e o estado do Galaxy S10, numa página nova e numa linha do Resumo.

**Architecture:** três produtores gravam JSON pequenos e legíveis por todos (statusline + `claude-uso` em `/var/lib/claude-uso/`, guardião do S10 em `/run/cerberus-s10-publico/`); o kindle-monitor (`nobody`, só leitura) os lê com coletores puros e desenha a página `claude` e a linha do Resumo.

**Tech Stack:** Python 3 stdlib (kindle-monitor, cerberus-s10, claude-uso), bash (statusline, instaladores), systemd (timer de usuário, tmpfiles), unittest/pytest.

**Spec:** `docs/superpowers/specs/2026-11-16-pagina-claude-s10-design.md` (neste repositório). Leia junto.

## Global Constraints

- kindle-monitor: só stdlib no servidor; `nobody`, `ProtectHome=yes`, só leitura; fonte embutida só ASCII + grau + ponto médio (sem acento, sem ✓/⚡ como caractere); tela 1236×1648.
- Nada usa o endpoint de uso não documentado da Anthropic; a fonte de limite é só o JSON do statusline (`rate_limits.five_hour|seven_day.used_percentage`, `.resets_at` em epoch s).
- O kindle-monitor não entra no grupo `cerberus-s10`; nenhum listener novo; nenhum IP, porta, serial ou nome de rede em arquivo público.
- Arquivos públicos: 0644, escrita atômica (temporário no mesmo diretório + `os.replace`/`mv`).
- Conta: só a pessoal (`CLAUDE_CONFIG_DIR` vazio ou igual a `~/.claude`).
- Código, identificadores e commits seguem cada repo (kindle-monitor: identificadores em português; galaxy-s10 e `claude-uso`: inglês); mensagens ao usuário e docs em pt-BR.
- Commits só com autorização do dono, sempre em branch de feature (ver "Preparação").

## Review Focus

1. JSON do statusline **sem** `rate_limits` (primeira mensagem, sessão com API key) ou com uma janela só: o gravador não apaga a janela que falta; mantém a anterior.
2. `volta_em` já passou com arquivo velho: mostrar `0%` "renovado", nunca a porcentagem antiga.
3. Arquivo truncado, JSON inválido, tipos errados (`pct` string, negativo, > 100, `bool`): coletor devolve `n/d` ou limita a 0–100; nunca exceção, nunca tela quebrada.
4. Caminho do S10 `null` (VNC desconhecido sem USB): marca "?", não ✗.
5. Config sem as chaves `claude`/`s10`: a linha do Resumo some e a página mostra "desligado na config" (o botão continua, para a barra não mudar de forma).

Cada item tem teste na tarefa dona (marcado **[RF n]**).

---

## Preparação (antes da Tarefa 1)

- **dotfiles**: o checkout principal está em `feat/dev-atheron` com mudanças não commitadas do dono (`install.sh`, `README.md`, `claude/settings.json`). Não tocar nele. Criar worktree: `git -C ~/development/dotfiles worktree add ~/development/worktrees/dotfiles-claude-uso-painel -b feat/claude-uso-painel` (base: HEAD de `feat/dev-atheron`). Testes: `uv run --no-project --with pytest pytest tests`.
- **galaxy-s10**: o repo não tem nenhum commit. Com a autorização do dono: commit inicial do estado atual em `master`, depois `git switch -c feat/resumo-publico`.
- **kindle-monitor**: `git switch -c feat/pagina-claude-s10` (leva a mudança da hora sem segundos e os docs desta spec/plano).
- Constatar a linha de base de cada suíte antes de mudar código. kindle-monitor: rodar sempre com `umask 022` (`(umask 022; python3 -I -m unittest discover -s tests)`); com o `umask 0002` do usuário `claude`, os 64 testes do executor falham de propósito ("gravavel por grupo/outros"). Com 022 a suíte inteira passa (16/11/2026).

---

### Task 1: `claude-uso --painel` (dotfiles)

**Agente:** implementador · **Repo:** worktree `dotfiles-claude-uso-painel`

**Files:**
- Modify: `bin/claude-uso` (argparse em `main`, ~linha 144; nova função)
- Test: `tests/test_claude_uso.py`
- Modify: `README.md` (linha do `claude-uso`, ~87)

**Interfaces:**
- Produces: `painel(home: Path, conta: str, hoje: dt.date) -> dict` e a opção `--painel` (imprime o JSON). Formato (chaves exatas):
  `{"versao": 1, "conta": str, "gerado_em": int, "hoje": T, "sete_dias": T, "por_modelo_7d": [{"modelo": str, "total": int, "custo_usd": float}]}` com `T = {"entrada": int, "saida": int, "cache_leitura": int, "cache_escrita": int, "total": int, "custo_usd": float}`; `por_modelo_7d` ordenado por `total` desc; `custo_usd` com 2 casas.
- `--json` existente inalterado.

- [ ] **Step 1: testes que falham** em `tests/test_claude_uso.py` (fixture `home` já existente):
  - `test_painel_splits_today_and_week`: mensagens de hoje e de 3 dias atrás → `hoje.total` só conta as de hoje, `sete_dias.total` conta ambas; `total == entrada+saida+cache_leitura+cache_escrita`.
  - `test_painel_only_requested_account`: mensagem em `~/.claude-<conta-de-trabalho>` não entra com `conta="pessoal"`.
  - `test_painel_cli_prints_json`: `main(["--painel", "--conta", "pessoal"], home)` imprime JSON com `versao == 1` e as chaves acima.
  - `test_json_flag_unchanged`: `--json` continua devolvendo a lista de linhas do relatório.
- [ ] **Step 2:** `uv run --no-project --with pytest pytest tests/test_claude_uso.py -v` → FAIL nos novos.
- [ ] **Step 3:** implementar `painel()` reutilizando `scan()`/`cost()`; "hoje" = `dt.date.today()` local.
- [ ] **Step 4:** a mesma suíte passa.
- [ ] **Step 5:** README: uma linha sobre `--painel`. Commit `feat(claude-uso): add --painel JSON for the Kindle dashboard`.

### Task 2: retrato dos limites pelo statusline (dotfiles)

**Agente:** implementador · **Repo:** worktree `dotfiles-claude-uso-painel`

**Files:**
- Create: `bin/claude-limites` (Python stdlib, executável, `#!/usr/bin/env -S python3 -I`)
- Modify: `claude/statusline.sh` (chamar em segundo plano)
- Modify: `bin/claude-mirror` (`install_links`: incluir `claude-limites` na lista de `bin`)
- Test: `tests/test_claude_limites.py`

**Interfaces:**
- Produces: `claude-limites [--dir DIR] [--agora EPOCH]` lê o JSON do statusline no stdin e grava `DIR/limites.json` (padrão `DIR=/var/lib/claude-uso`). Formato: `{"versao": 1, "conta": "pessoal", "atualizado_em": int, "cinco_horas": {"pct": float, "volta_em": int}, "semanal": {...}}`, cada janela opcional. Funções testáveis: `extract(statusline: dict) -> dict` (janelas válidas, `pct` limitado a 0–100) e `merge(old: dict | None, new: dict, now: int) -> dict | None` (`None` = não gravar).
- Regras de `merge` (spec §1): por janela, `volta_em` maior vence; mesmo `volta_em` → `pct` = máximo; `volta_em` menor que o gravado → mantém o gravado; janela ausente no novo → mantém a antiga **[RF 1]**; não grava se nada mudou e o arquivo tem < 60 s.
- Sai 0 em silêncio se `DIR` não existe ou não é gravável.

- [ ] **Step 1: testes que falham** (`tests/test_claude_limites.py`, carregando o script como em `test_claude_uso.py`):
  - `test_extract_both_windows`, `test_extract_clamps_and_rejects_bad_types` (`"34"`, `-5`, `150`, `True` → descartado/limitado) **[RF 3]**
  - `test_merge_keeps_missing_window` **[RF 1]**, `test_merge_same_window_never_decreases`, `test_merge_newer_reset_wins`, `test_merge_older_reset_ignored`, `test_merge_skips_unchanged_within_60s`
  - `test_cli_writes_atomically_0644` (arquivo final 0644, sem temporário sobrando), `test_cli_missing_dir_is_silent`
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** implementar.
- [ ] **Step 4:** testes passam.
- [ ] **Step 5:** em `statusline.sh`, depois de calcular `acct`: se `acct = pessoal` e `[ -w /var/lib/claude-uso ]`, `( printf '%s' "$input" | claude-limites >/dev/null 2>&1 & )`. Teste `test_statusline_calls_writer_only_for_personal` (rodar o script com `HOME`/`CLAUDE_CONFIG_DIR` falsos e um `claude-limites` falso no `PATH` que registra a chamada). Commit `feat(statusline): publish plan limits for the Kindle dashboard`.

### Task 3: timer do `claude-uso --painel` (dotfiles)

**Agente:** mecanico · **Repo:** worktree `dotfiles-claude-uso-painel`

**Files:**
- Create: `claude/painel/systemd/claude-uso-painel.service`, `claude/painel/systemd/claude-uso-painel.timer`
- Modify: `install.sh` (bloco do servidor, copiando o padrão do segundo cérebro em ~136-150)

**Interfaces:**
- Consumes: `claude-uso --painel --conta pessoal` (Task 1).
- Service `Type=oneshot`: `sh -c 'claude-uso --painel --conta pessoal > /var/lib/claude-uso/.tokens.tmp && chmod 0644 /var/lib/claude-uso/.tokens.tmp && mv /var/lib/claude-uso/.tokens.tmp /var/lib/claude-uso/tokens.json'` com `ExecCondition=test -w /var/lib/claude-uso`. Timer: `OnBootSec=2min`, `OnUnitActiveSec=5min`, `Persistent=true`.
- `install.sh`: só com `--servidor` e só se `/var/lib/claude-uso` for gravável; senão imprime "  /var/lib/claude-uso ausente: rode o instalador do kindle-monitor (root) e depois este de novo".

- [ ] **Step 1:** criar as units; `systemd-analyze --user verify` nas duas → sem erro.
- [ ] **Step 2:** bloco no `install.sh`; `bash -n install.sh` e `shellcheck install.sh` sem achado novo.
- [ ] **Step 3:** commit `feat(install): schedule claude-uso --painel on the server`.

### Task 4: resumo público do S10 (galaxy-s10)

**Agente:** implementador · **Repo:** `galaxy-s10`, branch `feat/resumo-publico`

**Files:**
- Modify: `atheron/cerberus-s10` (nova função pura; laço principal ~1113-1118)
- Modify: `atheron/cerberus-s10.service` (`ReadWritePaths=/run/cerberus-s10-publico`; `Environment=S10_PUBLIC=/run/cerberus-s10-publico/resumo.json` se o padrão do arquivo for por env)
- Create: `atheron/cerberus-s10-publico.tmpfiles` (`d /run/cerberus-s10-publico 0755 cerberus-s10 cerberus-s10 -`)
- Modify: `atheron/user-step-s10.sh` (instalar o tmpfiles em `/etc/tmpfiles.d/cerberus-s10-publico.conf` + `systemd-tmpfiles --create`; `check()` confere o diretório e o modo do `resumo.json`; `--undo` remove os dois)
- Test: `atheron/tests/test_cerberus_s10.py`, `atheron/tests/test_installer.sh`
- Modify: `README.md` (seção do estado: o resumo público e o que ele contém), `CLAUDE.md` (Estrutura/Cuidados: uma linha)

**Interfaces:**
- Produces: `public_summary(snap: dict, alerts: Alerts, now: float) -> dict` com **lista de campos permitidos**: `{"versao": 1, "gerado_em": int, "bateria": {"nivel", "status", "temperatura_c", "saude"} | None, "caminhos": {"usb", "adb_sem_fio", "tailscale", "ssh_termux", "vnc"}: bool | None, "avisos": [str]}`. `caminhos.X` = `snap["caminhos"][X]["ok"]` (ausente → `None`) **[RF 4]**. `avisos` usa códigos: `"temperatura"` (temperatura ≥ `alerts.temp_max`), `"carga_cheia"` (nível 100 e `now - alerts.full_since >= alerts.full_s`).
- No laço: depois de `write_atomic(path, snap, 0o640)`, `write_atomic(public_path, public_summary(...), 0o644)` dentro de `try` próprio (falha só registra no log; não derruba o `estado.json`). `public_path = env.get("S10_PUBLIC", "/run/cerberus-s10-publico/resumo.json")`.

- [ ] **Step 1: testes que falham**:
  - `test_public_summary_whitelist`: a partir de um `snap` completo (com IP, porta, serial, `estado` e dados de Wi-Fi), o JSON serializado do resumo **não contém** nenhum IP (`re` de IPv4), nenhuma porta conhecida do snap, o serial, nem chaves fora da lista.
  - `test_public_summary_unknown_path_is_null` **[RF 4]**, `test_public_summary_no_battery`, `test_public_summary_alert_codes` (quente → `temperatura`; 100 % além de `full_s` → `carga_cheia`).
  - `test_installer.sh`: `ReadWritePaths=/run/cerberus-s10-publico` na unit; o tmpfiles tem `0755 cerberus-s10`; o `UMask=0007` continua.
- [ ] **Step 2:** `python3 -I atheron/tests/test_cerberus_s10.py` e `bash atheron/tests/test_installer.sh` → FAIL nos novos.
- [ ] **Step 3:** implementar função, laço, unit, tmpfiles e instalador.
- [ ] **Step 4:** as quatro suítes e o lint do `CLAUDE.md` do repo passam.
- [ ] **Step 5:** README/CLAUDE.md; commit `feat(cerberus-s10): publish a whitelisted public summary for dashboards`.

### Task 5: coletores `claude` e `s10` (kindle-monitor)

**Agente:** implementador · **Repo:** `kindle-monitor`, branch `feat/pagina-claude-s10`

**Files:**
- Modify: `server/coletores.py` (funções novas perto de `coletar_tier_state`, ~387; integração em `Coletor.coletar`, ~804-860)
- Modify: `server/config.exemplo.json`, `deploy/config.atheron.json`
- Test: `server/tests/test_coletores.py`

**Interfaces:**
- Consumes: formatos de `limites.json`, `tokens.json` (Tasks 1–3) e `resumo.json` (Task 4).
- Produces:
  - `coletar_claude(cfg: dict, ler, agora: float) -> dict` → `{"limites": L, "tokens": K}`; `L = {"cinco_horas": J | None, "semanal": J | None, "idade_s": int, "velho": bool}` com `J = {"pct": float, "volta_em": int, "renovado": bool}` (`volta_em <= agora` → `pct = 0.0`, `renovado = True` **[RF 2]**; `velho = idade_s > 900`); `K = {"hoje": T, "sete_dias": T, "idade_s": int, "velho": bool}` (`velho = idade_s > 1200`). Arquivo ausente/inválido/tipos errados → `L` ou `K` = `{"erro": "n/d"}` **[RF 3]**.
  - `coletar_s10(caminho: str, ler, agora: float) -> dict` → `{"bateria": ..., "caminhos": ..., "avisos": [...], "idade_s": int, "velho": bool}` (`velho = idade_s > 120`) ou `{"erro": "n/d"}`.
  - `Coletor.coletar`: `m["claude"]` só se `cfg.get("claude")`, `m["s10"]` só se `cfg.get("s10")`, via `_isolado`; sem chave → chave ausente em `m` **[RF 5]**.
  - Config: `"claude": {"limites": "/var/lib/claude-uso/limites.json", "tokens": "/var/lib/claude-uso/tokens.json"}`, `"s10": {"resumo": "/run/cerberus-s10-publico/resumo.json"}` (com `_comentario_*` no exemplo).
- [ ] **Step 1: testes que falham** (`test_coletores.py`): válido; ausente; JSON inválido; `pct` string/negativo/> 100/bool **[RF 3]**; `volta_em` passado → `renovado` **[RF 2]**; idade 901 s → `velho`; uma janela só; S10 válido/velho/ausente; `Coletor.coletar` sem as chaves não cria `m["claude"]`/`m["s10"]` **[RF 5]**.
- [ ] **Step 2:** `cd server && python3 -I -m unittest tests.test_coletores -v` → FAIL nos novos.
- [ ] **Step 3:** implementar.
- [ ] **Step 4:** passa.
- [ ] **Step 5:** commit `feat(coletores): read Claude limits/tokens and the S10 public summary`.

### Task 6: ícone do Claude (kindle-monitor)

**Agente:** implementador · **Repo:** `kindle-monitor`

**Files:**
- Create: `tools/claude.svg` (do Simple Icons, versão fixada; cabeçalho com origem, versão, licença CC0 do arquivo e "marca da Anthropic, uso privado")
- Create: `tools/gerar_icones.py` (roda com `uv run --no-project --with pillow --with svgelements python tools/gerar_icones.py`)
- Create: `server/icones_dados.py` (GERADO; mesmo formato de `fonte_dados.py`: `ICONES = {"claude": {tam: {"w", "h", "dados"}}}`, cobertura 8 bits, base64 + zlib)
- Modify: `server/canvas.py` (método novo)
- Test: `server/tests/test_canvas.py`

**Interfaces:**
- Produces: `Canvas.icone(x: int, y: int, nome: str, tam: int, cor: int) -> int` (desenha com `_glifo_bitmap`, devolve a largura; `nome`/`tam` inexistente → não desenha e devolve 0). Tamanhos gerados: 40 e 30.
- Rasterização: preencher o path com a regra do SVG (`fill-rule` do arquivo; padrão nonzero) a 8× e reduzir por média para cobertura 0–255; caixa quadrada `tam × tam`, desenho centrado.
- [ ] **Step 1: testes que falham**: `test_icone_desenha_dentro_da_caixa` (pixels escuros só dentro de `tam×tam`, e há pixels escuros), `test_icone_inexistente_nao_desenha`, `test_icones_dados_tamanhos` (40 e 30 existem, `len(bitmap) == w*h`).
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** baixar o SVG (jsDelivr, versão exata), escrever o gerador, gerar `icones_dados.py`, implementar `Canvas.icone`.
- [ ] **Step 4:** passa; `python3 -I tools/preview.py` não quebra.
- [ ] **Step 5:** commit `feat(canvas): Claude icon pre-rasterized like the font`.

### Task 7: página `claude` (kindle-monitor)

**Agente:** implementador · **Repo:** `kindle-monitor`

**Files:**
- Modify: `server/botoes.py` (`PAGINAS`, `NAV`)
- Modify: `server/render_png.py` (`desenhar` ~921; cartões novos)
- Modify: `server/render.py` (`render_texto` ~305)
- Modify: `tools/preview.py` (aceitar `--pagina claude` com dados de exemplo)
- Test: `server/tests/test_paginas_png.py`, `server/tests/test_botoes.py`, `server/tests/test_render.py`
- Modify: `CLAUDE.md`, `README.md` (páginas)

**Interfaces:**
- Consumes: `m["claude"]`, `m["s10"]` (Task 5); `Canvas.icone` (Task 6).
- Produces: `botoes.PAGINAS = ("resumo", "servicos", "detalhes", "comandos", "claude")`; `NAV` ganha `("pagina:claude", "Claude/S10")` no fim (6 botões de ~176 px; se o rótulo não couber no tamanho da barra, `"Claude"`). Funções: `_card_claude(c, cl, x, y, w, h)`, `_card_s10(c, s, x, y, w, h)`, `_desenhar_claude(c, m)`; texto: `_linhas_claude(m, cols) -> list[str]`; helpers `_tokens_txt(n) -> str` (`"950"`, `"12 k"`, `"3,1 M"`) e `_volta_txt(epoch, agora) -> str` (`"volta 14:30"` hoje; `"volta qui 02:00"` em outro dia; dias `seg ter qua qui sex sab dom`).
- Regras de exibição (spec §5): ≥ 90 % em negrito preto; `velho` → `"ha N min"`/`"ha N h"` em cinza; S10 `velho` → `"S10 sem dados ha N min"` e marcas "?"; marcas com `_forma_ok`/`_forma`; sem `m["claude"]` e sem `m["s10"]` → texto central `"Claude/S10 desligado na config"` **[RF 5]**.
- [ ] **Step 1: testes que falham**: página com dados completos (nada fora da imagem no canvas estrito; textos esperados presentes: `"5h"`, `"34%"`, `"volta"`, `"S10"`); `renovado` mostra `"0%"` e `"renovado"` **[RF 2]**; caminho `None` desenha "?" **[RF 4]**; sem chaves → `"desligado na config"` **[RF 5]**; `n/d` nos dois → sem exceção; `_tokens_txt`/`_volta_txt` (casos acima); NAV com 6 botões dentro de 1236 px sem sobreposição; `render_texto(..., pagina="claude")` só ASCII.
- [ ] **Step 2:** rodar os três módulos de teste → FAIL.
- [ ] **Step 3:** implementar.
- [ ] **Step 4:** passam; `python3 -I tools/preview.py --saida <scratchpad>/claude.png --pagina claude` gera a imagem (mostrar ao dono).
- [ ] **Step 5:** docs; commit `feat(kindle): Claude/S10 page`.

### Task 8: linha Claude/S10 no Resumo (kindle-monitor)

**Agente:** implementador · **Repo:** `kindle-monitor`

**Files:**
- Modify: `server/render_png.py` (`_desenhar_resumo` ~568)
- Test: `server/tests/test_render_png.py`

**Interfaces:**
- Consumes: Tasks 5–7 (`Canvas.icone`, `_volta_txt` não é usado aqui).
- Produces: `_linha_claude_s10(c, m, x, y, w, h)`, 60 px, ancorada no rodapé do Resumo acima da linha do Ragnarok quando as duas existem; conteúdo: ícone 30, `"5h NN%"`, `"sem NN%"`, `"S10 NN%"` + estado de carga em texto curto (`"carreg."`, `"cheia"`, `"bat."`) + três marcas (USB, sem fio, VNC). Só aparece se `m` tem `claude` ou `s10`; parte ausente some da linha.
- [ ] **Step 1: testes que falham**: com Ragnarok + linha nova nada sai da imagem e nada se sobrepõe (caixas dos blocos); com muitos itens em Atenção o encaixe continua cabendo; sem as chaves a linha não existe e o layout é idêntico ao atual (comparar PNG com/sem a mudança para `m` sem `claude`/`s10`) **[RF 5]**.
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** implementar.
- [ ] **Step 4:** suíte inteira do servidor passa (comparar com a linha de base anotada na Preparação); preview do Resumo para o dono.
- [ ] **Step 5:** commit `feat(kindle): Claude/S10 line on the summary page`.

### Task 9: diretório `/var/lib/claude-uso` no instalador (kindle-monitor)

**Agente:** mecanico · **Repo:** `kindle-monitor`

**Files:**
- Create: `deploy/kindle-monitor-claude.tmpfiles` (`d /var/lib/claude-uso 0755 claude claude -`)
- Modify: `deploy/instalar-atheron.sh` (se `getent passwd claude`: instala em `/etc/tmpfiles.d/kindle-monitor-claude.conf` e roda `systemd-tmpfiles --create` nele; senão imprime aviso e segue)
- Test: `server/tests/test_deploy_units.py`

(O instalador do kindle-monitor não tem `--check`/`--undo`; a spec os citava por engano: segue o padrão do instalador atual.)

- [ ] **Step 1: teste que falha**: o tmpfiles tem exatamente o modo `0755` e o dono `claude`; o instalador só o instala com `getent passwd claude`.
- [ ] **Step 2:** rodar → FAIL. **Step 3:** implementar. **Step 4:** passa; `bash -n` e `shellcheck` no instalador.
- [ ] **Step 5:** commit `feat(deploy): create /var/lib/claude-uso for the Claude card`.

### Task 10: revisão final

**Agente:** revisor (um por repo, em paralelo) e depois `security-reviewer` só no diff do galaxy-s10 (resumo público e unit)

- [ ] Revisar cada branch contra a spec e o Review Focus; corrigir o que voltar.
- [ ] Rodar todas as suítes e lints dos três repos; anotar a saída.
- [ ] Entregar ao dono: os previews (página e Resumo), a lista de passos de root (spec, "Passos do dono") e as branches para ele decidir merge/push.
