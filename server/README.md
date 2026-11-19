# kindle-monitor: servidor

Servidor HTTP em Python 3 (somente biblioteca padrao) que coleta metricas do host e serve uma "tela" pronta para o Kindle: texto ASCII (`/tela.txt`) ou uma imagem PNG estilizada em tons de cinza (`/tela.png`, 1236x1648, para o FBInk). Leitura por GET sem autenticacao; o unico POST e `/comando` (ver "Comandos"), que so registra um pedido. O processo web nao escreve em disco, exceto o pedido no spool.

## Como rodar
```
python3 -I server/monitor_server.py --porta 8765                      # so local (127.0.0.1)
python3 -I server/monitor_server.py --bind 100.64.0.5 --config server/config.json   # IP da tailnet/LAN
curl -s http://127.0.0.1:8765/tela.txt
curl -s -o tela.png http://127.0.0.1:8765/tela.png
```
Opcoes: `--bind` (padrao `127.0.0.1`), `--porta` (padrao `8765`), `--config` (arquivo JSON), `--colunas` (padrao `38`, entre 20 e 120), `--largura` (padrao `1236`, entre 800 e 3000) e `--altura` (padrao `1648`, entre 1300 e 4000) do `/tela.png`.

**Nao escute em `0.0.0.0`.** O endpoint nao tem autenticacao; o programa recusa `0.0.0.0` e `::`. Para o Kindle alcancar o servidor, passe `--bind` com o IP da interface da LAN ou da tailnet (por exemplo o `100.x.y.z` do Tailscale) e nunca exponha a porta na internet.

## Endpoints
| Caminho | Resposta |
|---|---|
| `/tela.txt` | texto puro ASCII, uma linha por linha da tela (ate `--colunas` colunas e 26 linhas; linhas `IO`/`NET` quando ha `io` na config), barras como `[#####-----]  50%`; inclui a linha `Portas: LOGIN ok CHAR ok MAP FALHA`, o bloco de alertas do motor (ver "Motor de alertas") linhas da Entrega 2 (`Rotinas: N de M ok` no resumo; TAILNET, Kindle e S10 na aba `aparelhos`; SESSOES e GITHUB na aba `claude`) |
| `/tela.png` | imagem PNG 8-bit em tons de cinza (`image/png`), `--largura` x `--altura` (padrao 1236x1648, Kindle Paperwhite 5), gerada so com a biblioteca padrao |
| `/historico.json` | anel em memoria das ultimas 60 amostras: `intervalo_s`, `max`, `t` (epoch), `cpu`, `ram` e `gpu` (so se houver GPU), em %, da mais antiga para a mais nova (`null` = leitura falhou) |
| `/metricas.json` | metricas brutas em JSON (`host`, `gerado_em` ISO, cpu, ram, gpu, discos, io, servicos, ragnarok, portas, historico, pares, e os blocos da Entrega 2: `aparelhos`, `rotinas`, `github`, `claude.sessoes` e `limiares`; ver "Aparelhos, rotinas, sessoes e GitHub"). `?pares=0` nao consulta os pares |
| `/botoes.json` | `{"largura","altura","pagina","p","paginas","botoes":[{id,rotulo,x,y,w,h,tipo,armado,visivel}]}`: fonte unica do layout dos botoes (pixels do PNG, origem no canto superior esquerdo); o render desenha exatamente estes retangulos (`botoes.py`), exceto os invisiveis (`visivel: false`); `p` e `paginas` valem na pagina servicos. `/botoes.txt` traz o mesmo layout como `id tipo x y w h` por linha (para o awk do Kindle), com os invisiveis |
| `/saude` | `ok` |
| `/comando/estado` | lista JSON dos ultimos comandos (mesma de `metricas.comandos`) |
| `POST /comando` | registra um pedido de comando (ver "Comandos"); exige token |

Parametros (GET): `/tela.png`, `/tela.txt`, `/botoes.json` e `/botoes.txt` aceitam `?pagina=resumo|servicos|aparelhos|detalhes|claude|comandos` (padrao `resumo`) e, na pagina `servicos`, `&p=<n>` (1 a N; invalido = 1, acima do maximo = a ultima). `/tela.png`, `/botoes.json` e `/botoes.txt` aceitam `&armado=<id>`: acao rapida (`gpu-descarregar`, `bots-pausar`, `bots-retomar`, `monitor-reiniciar`; so na pagina comandos) ou `svc:<id>:<verbo>` de um botao da pagina servicos (o id e o verbo tem de estar no catalogo); o botao armado aparece invertido ("Confirmar?" nas linhas de servico, "Toque de novo para confirmar" nas acoes rapidas). Os quatro tambem aceitam `&modo=desempenho|balanceado|economia` (perfil de energia ativo; invalido ou ausente = `desempenho`; so muda a pagina comandos, onde o bloco AJUSTES destaca o perfil ativo e descreve o ritmo). Valor invalido e ignorado (usa o padrao), nunca 500. Os botoes de comando chamam `POST /comando` (ver "Comandos"). A pagina comandos mostra ate 8 itens de `metricas["comandos"]` (`{acao, estado, quando, detalhe}`) se existirem. Os ids dos botoes usam so `[a-z0-9:-]`.

**Contrato com o Kindle (v5)**: a barra de navegacao tem 6 abas locais (`pagina:resumo`, `pagina:servicos`, `pagina:aparelhos`, `pagina:detalhes`, `pagina:claude`, `pagina:comandos`); `atualizar` e o relogio do cabecalho (invisivel, em todas as paginas); na pagina resumo, as 8 linhas sao botoes `pagina:<destino>` invisiveis (ATHERON, NAS e ROTINAS -> detalhes; APARELHOS -> aparelhos; SERVICOS e RAGNAROK -> servicos; CLAUDE e GITHUB -> claude); na pagina servicos ha tambem `servicos:anterior` e `servicos:proxima` (tipo `local`, so quando existem), que o Kindle trata trocando o `p` da proxima requisicao. Os botoes de linha `svc:<id>:<verbo>` (tipo `comando`) usam o mesmo fluxo de dois toques das acoes rapidas e fazem `POST /comando {"acao":"svc:<id>:<verbo>"}`. O Kindle deve repassar `p` (e `modo`) ao pedir `/tela.png` e `/botoes.txt`.

**Perfis de energia (Ajustes)**: a pagina comandos (Acoes) tem o bloco AJUSTES com tres botoes `local` `modo:desempenho`, `modo:balanceado` e `modo:economia`, um toque so. O Kindle guarda o escolhido em `/var/local/kindle-monitor/modo` (ext3, so o nome, 0644; sem arquivo = `desempenho`), le o arquivo a cada ciclo e passa `&modo=<nome>` nos dois pedidos. A tabela abaixo vive em `perfis.py` (rotulos e descricoes) e, em numeros, em `kindle/kindle-monitor/config.sh` (`PERFIL_<nome>="<intervalo_s> <ciclos_ate_o_flash>"`); `tests/test_modos.py` confere que as duas concordam. Trocar de perfil zera o contador do flash e acorda o loop (USR1), entao o efeito e imediato mesmo vindo de `economia`.

| Perfil | Intervalo | Flash completo |
|---|---|---|
| `desempenho` (padrao) | 1 s | a cada 600 ciclos (~10 min) |
| `balanceado` | 60 s | a cada 15 ciclos (~15 min) |
| `economia` | 300 s | a cada 6 ciclos (~30 min) |

Com intervalos longos o loop dorme de forma interrompivel: qualquer toque (ou troca de perfil, mesmo se cair durante a busca) acorda o loop na hora, e com um botao de comando armado ele acorda de novo apos `ARM_SECONDS` para a tela deixar de mostrar "confirmar". O aviso "sem dados" conta ciclos (`FAIL_NOTICE_AFTER`), entao em `economia` aparece apos ~15 min de falhas.

Outro caminho: 404. Metodo diferente de GET: 405 (menos `POST /comando`). Todas as respostas levam `Cache-Control: no-store`.

## Config (`config.exemplo.json`)
Copie para `config.json` e ajuste. Chaves que comecam com `_` sao comentarios e sao ignoradas.
- `host`: nome exibido (padrao: hostname).
- `servicos_kindle`: catalogo da pagina Servicos e dos comandos por servico (ver "Catalogo de servicos" em Comandos). O estado vem do inventario root; a lista antiga `servicos` (`systemctl is-active` no proprio web) continua valendo para quem nao usa o catalogo e aparece na pagina Servicos como grupo host sem botoes. No atheron ela fica `[]`.
- `discos`: lista de entradas de dois tipos. `{rotulo, caminho}` mede o ponto de montagem com `statvfs`. `{rotulo, tier_state}` le o JSON do Cerberus (`ssd_used_gib` / `cap_gib`, em GiB; usado para o "NAS SSD", porque o `/srv/nas` e uma uniao mergerfs que soma discos inteiros). Se o arquivo faltar ou os numeros forem invalidos (negativos, tipo errado, `cap_gib` <= 0) a linha mostra `n/d`; se `when` faltar ou tiver mais de 3 h a linha mostra o valor com o aviso `parado`. Cada entrada tem `caminho` ou `tier_state`, nunca os dois.
- `servicos`: unidades systemd checadas com `systemctl is-active` (mostra `ok` ou `FALHA`).
- `balanceador`: JSON do balanceador do Ragnarok (padrao `/var/lib/cerberus/memory-balancer.json`; `null` desliga). `players_by.ragnarok` ausente conta como 0 jogadores; `updated` com mais de 120 s marca o dado como `PARADO`.
- `pares`: lista de `{nome, url}` de outros servidores iguais a este; busca `<url>/metricas.json?pares=0` com timeout de 2 s. Se falhar, a tela mostra `nome: sem resposta`.
- `portas`: lista de `{rotulo, host, porta}` testadas com conexao TCP (timeout de 0,6 s, em paralelo, resultado em cache por ~5 s). `rotulo` tem ate 12 caracteres (letras, digitos, `_`, `.`, `-`), `host` e IP literal ou nome simples e `porta` vai de 1 a 65535; valor invalido faz o servidor recusar a config. Aparece como `portas: [{rotulo, aberto}]` no JSON, como linha `Portas:` no texto e como "pilulas" na imagem (preenchida = aberta, so contorno com X = fechada). Os valores do exemplo (`10.0.0.60`, 6900/6121/5121) sao os padroes do rAthena: ajuste para o seu.
- `intervalo_historico_s`: segundos entre as amostras do historico (padrao `15`; entre 0 e 3600). Uma thread de fundo (daemon) guarda CPU %, RAM % e GPU % das ultimas 60 amostras (15 min no padrao); alimenta o grafico da imagem e o `/historico.json`. So memoria: nada e escrito em disco, e o historico recomeca vazio ao reiniciar.
- `intervalo_cpu_s`: intervalo entre as duas leituras de `/proc/stat` (padrao `0.5`, entre 0 e 5). So vale na primeira leitura ou quando a amostra anterior tem mais de 30 s; nas demais requisicoes o CPU % vem da diferenca entre a leitura atual e a anterior, sem dormir.
- `intervalo_coleta_s`: segundos entre os snapshots da thread de coleta (padrao `1`; entre 0,1 e 60). A thread (daemon) coleta todas as metricas e troca o snapshot imutavel; `/tela.png`, `/tela.txt`, `/metricas.json` e `/botoes.*` so leem o ultimo snapshot e nunca coletam na requisicao (so nos primeiros instantes, antes do 1o snapshot). Metrica que falha numa rodada mantem o valor da anterior. O CPU % vem da diferenca entre snapshots (sem dormir).
- `intervalo_lento_s`: cadencia das coletas caras dentro da thread, `nvidia-smi` e `systemctl is-active` (padrao `5`; entre 0,5 e 600). Portas e pares ja tinham cache de ~5 s e agora tambem rodam so na thread.
- `cache_cpu_s`: segundos em que o CPU % calculado fica em cache (padrao `1.5`, entre 0 e 60). Com o Kindle pedindo a tela a cada ~2 s, o numero muda a cada requisicao. Requisicao a menos de 0,5 s da amostra anterior reutiliza o ultimo valor.
- `io`: `{"discos": [{"rotulo", "dev"}], "redes": [{"rotulo", "if"}]}`. `dev` e o nome do dispositivo em `/proc/diskstats` (ex.: `nvme0n1`, `sda`; setores lidos = coluna 6, escritos = coluna 10, setor de 512 bytes) e `if` o da interface em `/proc/net/dev` (`rx_bytes` e `tx_bytes`). `dev` e `if` aceitam so letras, digitos, `.`, `_` e `-` (ate 32); `rotulo` tem de 1 a 16 caracteres ASCII simples; valor invalido faz o servidor recusar a config. Padrao: nada (`{"discos": [], "redes": []}`, sem bloco na tela).
- `intervalo_io_s`: intervalo (padrao `0.3`, entre 0 e 5) entre as duas leituras feitas na primeira requisicao de I/O ou quando a amostra anterior tem mais de 30 s.
- `limiares`: limiares do motor de alertas (`alertas.py`, ver "Motor de alertas"). Todas as chaves sao opcionais; valor que nao e numero (bool inclui), nao e finito ou esta fora da faixa volta ao padrao daquela chave, sem erro. Chave desconhecida e ignorada. `config.exemplo.json` e `deploy/config.atheron.json` trazem os mesmos valores:

  | Chave | Padrao | Faixa |
  |---|---|---|
  | `disco_aviso` | 85 | 1 a 100 (% usado) |
  | `disco_critico` | 93 | 1 a 100 (% usado) |
  | `ram` | 90 | 1 a 100 (%) |
  | `swap` | 50 | 1 a 100 (%) |
  | `temp_cpu_c` | 85 | 40 a 120 (°C) |
  | `kindle_bateria` | 15 | 1 a 100 (%) |
  | `s10_bateria` | 20 | 1 a 100 (%) |
  | `claude_limite` | 90 | 1 a 100 (% do limite de 5 h ou semanal) |
  | `sessao_esperando_min` | 10 | 1 a 1440 (minutos) |

- `aparelhos` (lista, opcional, ate 16; catalogo da aba Aparelhos e do alerta de aparelho offline): cada item tem `id` (`^[a-z0-9-]{1,24}$`), `nome` (nome do peer no Tailscale, `^[a-z0-9-]{1,63}$`; com `empresa-x` e recusado), `rotulo` (ASCII imprimivel, 1 a 16), `icone` (nome de `icones_dados.ICONES`; o executor so confere o formato `^[a-z]{2,16}$`, ver o paragrafo de paridade abaixo) e `alerta_offline_min` (opcional, inteiro de 1 a 10080; `null` e recusado). `id` e `nome` nao podem repetir, e chave desconhecida recusa a lista. Lista invalida e descartada inteira: o servidor recebe lista vazia (sem `m.aparelhos`, o cartao TAILNET fica sem dados) e o executor registra uma linha e nao grava `aparelhos.json` (o `servicos.json` continua). Producao (`deploy/config.atheron.json`): nomad, s22, s10, iphone, kindle, gw (`alerta_offline_min` 10) e games.
- `rotinas` (lista, opcional, ate 16): `id` (`^[a-z0-9-]{1,24}$`, unico), `rotulo` (ASCII imprimivel, 1 a 20), `tipo` e `alvo`. `timer`: `alvo` e a unit `.service` (`^[A-Za-z0-9_.@-]{1,64}\.service$`). `arquivo`: `alvo` e caminho absoluto normalizado sob `/srv/`, `/var/lib/` ou `/var/backups/`, menos `/var/lib/claude-uso` (fonte do painel, nao e alvo de rotina; servidor e executor recusam) (vale o mtime, sem ler conteudo). `max_idade_h` de 0.1 a 720 (idade acima dele = atrasada). Mesma regra de lista inteira de `aparelhos`. Producao: `senhas` (timer `cerberus-vault-backup.service`, 26 h) e `senhas-arq` (arquivo `/srv/nas/backups/vaultwarden`, 26 h). O `tokens.json` nao e rotina: o aviso de dados velhos dele ja sai de `claude.tokens`. Os alvos do Syncthing e do segundo cerebro ainda nao entraram (ver "Pendencias desta entrega").
- `claude.sessoes` (diretorio, opcional): caminho absoluto normalizado sob `/var/lib/` ou `/run/`; fora disso, `m.claude.sessoes` vira `{"erro": "n/d"}`. Producao: `/var/lib/claude-uso/sessoes`.
- `github.resumo` (arquivo, opcional): mesma regra de caminho; fora disso, `m.github` vira `{"erro": "n/d"}`. Producao: `/var/lib/claude-uso/github.json`.

Sem essas chaves, `m.aparelhos`, `m.rotinas`, `m.claude.sessoes` e `m.github` nao existem. No `config.exemplo.json` os quatro blocos estao comentados (chaves `_exemplo_*`, com `_comentario_*` ao lado). Servidor e executor validam pela mesma tabela (`tests/test_paridade_catalogos.py`); a unica diferenca e o icone, de proposito: o executor so confere o formato, porque nao importa nada de `server/`.

### I/O: como as taxas sao calculadas
As taxas (bytes/s) saem da diferenca entre a amostra atual e a anterior, guardada em memoria, dividida pelo tempo (relogio monotonico) entre elas. Na primeira requisicao, ou se a amostra anterior tiver mais de 30 s, o servidor le duas vezes com `intervalo_io_s` entre as leituras. Se a ultima amostra tem menos de 0,5 s, a ultima taxa e reutilizada (nada e lido). Contador que voltou para tras (reboot, overflow) da `null` (`n/d` na tela) naquela amostra, nunca taxa negativa. Dispositivo ou interface que nao existe em `/proc` some da tela e do JSON; se o proprio arquivo de `/proc` nao puder ser lido, as linhas aparecem com `n/d`.

`metricas.io`: `{"discos": [{"rotulo", "dev", "leitura_bps", "escrita_bps"}], "redes": [{"rotulo", "if", "rx_bps", "tx_bps"}]}`, em bytes/s (numero ou `null`). A chave so existe se a config tiver algum dispositivo/interface; se a leitura falhar, vale `{"erro": "n/d"}`.

Unidades na tela: **base 1024** (1 KB/s = 1024 B/s, 1 MB/s = 1024 KB/s, igual aos GiB da RAM), uma casa decimal: `512 B/s`, `40.0 KB/s`, `12.3 MB/s`. No `/tela.txt` a forma curta: `IO NVMe r 12.3M w 1.2M` e `NET LAN rx 3.4M tx 0.2M` (`B`, `K`, `M`, `G`; o rotulo e encurtado se a linha passar de `--colunas`).

**Cache de imagem:** o PNG renderizado fica num LRU de 8 entradas, chave (id do snapshot, pagina, p, armado, modo, tamanho; na pagina comandos tambem o conteudo de `comandos.ultimos`). A thread de coleta ja renderiza a ultima tela pedida nos ultimos 30 s a cada snapshot novo, entao o pedido seguinte do Kindle costuma ser um acerto de cache. O encoder usa zlib nivel 1 e o canvas mistura texto/cantos por tabela (pixels identicos aos de antes).

Cada coletor falha isolado: o que der erro aparece como `n/d` na tela e nunca derruba a requisicao. Sem GPU NVIDIA ou sem sensor de temperatura, a linha simplesmente nao aparece.

## Motor de alertas (`alertas.py`)
`avaliar(m, lim, kv)` e pura e nunca levanta: devolve a lista de alertas `{"nivel", "texto", "pagina", "sistema"}`, ordenada por nivel (`critico`, `aviso`, `leve`) e, dentro do nivel, pela ordem das regras. `texto` e ASCII de ate 48 caracteres; `pagina` e um id de `botoes.PAGINAS`. Ela substitui a antiga regra de atencao do render: o cartao ATENCAO da imagem e a linha de atencao do `/tela.txt` usam a mesma lista. O coletor publica os limiares em `m["limiares"]` (`alertas.limiares(cfg["limiares"])`); a bateria do Kindle chega a cada pedido e entra como `kv` (a vista de `kindle_status`).

Regras, com os limiares da tabela de `limiares` (`disco_critico` e `disco_aviso` valem para discos; `/` conta para `atheron`, os outros para `nas`):
- **Critico:** disco >= `disco_critico`; servico em falha; rotina com resultado `falha`; unidades do systemd em falha; aparelho offline ha pelo menos `alerta_offline_min` (quando o aparelho define esse campo).
- **Aviso:** disco >= `disco_aviso`; RAM >= `ram`; swap >= `swap` (com swap configurada); temperatura da CPU >= `temp_cpu_c`; servico parado que nao e `opcional`; inventario de servicos velho ou ausente; rotina atrasada; todas as rotinas do catalogo `desconhecido` com inventario ok ("Rotinas sem dados", um aviso so); inventario root parado em duas ou mais fontes (servicos, aparelhos, rotinas: um aviso so, "Inventario root sem atualizar ha N min"); limite de 5 h ou semanal do Claude >= `claude_limite` (sem `renovado`); CI da branch padrao em falha; porta do Ragnarok fechada; bateria do Kindle <= `kindle_bateria` e sem carregar; bateria do S10 <= `s10_bateria` e descarregando; fonte velha ("<fonte> sem atualizar ha N min").
- **Leve:** sessao do Claude `esperando` ha pelo menos `sessao_esperando_min`.

As regras de aparelhos, rotinas, sessoes e GitHub leem `m["aparelhos"]`, `m["rotinas"]`, `m["claude"]["sessoes"]` e `m["github"]` (formatos na secao "Aparelhos, rotinas, sessoes e GitHub"). Sem inventario (`ausente`) ou com `erro` (o `aparelhos.json` do executor com `"erro"` nao vazio conta como `ausente`), nao ha alerta: a linha mostra "sem dados". Dedupe: a unidade em falha que e o `alvo` de uma rotina `timer` em falha ja tem o alerta da rotina e sai da regra de unidades (so sobra o resto); `senhas-arq` atrasada junto com `senhas` nao gera um segundo aviso. Rotina `desconhecido` isolada: alerta leve "Rotina X sem dado" so para `timer` (um `arquivo` pode ainda nao existir de proposito). Relogio do executor adiantado alem de 5 s: `inventario: velho`, `idade_s` com a diferenca absoluta, `relogio_adiantado: true` e o aviso diz "... com relogio adiantado". Com inventario `velho` ou fonte velha, aparece o aviso "<fonte> sem atualizar ha N min". A regra das sessoes: so conta como aberta a sessao com batimento nos ultimos 10 min (`SESSAO_IDADE_MAX_S = 600` em `dev_fontes.py`); a mais velha sai da lista, do total e dos alertas. Os testes das regras estao em `tests/test_alertas.py`, com limiares e valores logo abaixo deles.

## Comandos (POST /comando)
O servidor continua sem privilegio (`User=nobody`, `ProtectSystem=strict`). Para mudar o atheron a partir do Kindle (com confirmacao em dois toques na tela), o processo web so **registra um pedido**; quem executa e um **executor root separado**, com uma tabela fixa de acoes. Nunca ha shell nem comando montado a partir do pedido.

```
Kindle --POST /comando {"acao":"..."} + X-Kindle-Token--> kindle-monitor.service (nobody)
   grava /run/kindle-monitor/spool/<epoch_ns>-<acao>.req (vazio, tmp + rename)
   (servico: <epoch_ns>-svc--<id>--<verbo>.req; no JSON e na API a acao e "svc:<id>:<verbo>")
kindle-monitor-executor.path (DirectoryNotEmpty) --> kindle-monitor-executor.service (root, oneshot)
   apaga o .req ANTES de executar, roda a acao da tabela, grava /run/kindle-monitor/status/<epoch_ns>-<acao>.json
GET /comando/estado e metricas.comandos leem esses JSON (e os .req ainda no spool, como "executando")
```

**Acoes** (ids fixos, contrato com a tela):
| id | O que faz |
|---|---|
| `gpu-descarregar` | `GET http://10.0.0.1:11435/api/ps` e, para cada modelo carregado, `POST /api/generate {"model": nome, "keep_alive": 0}` |
| `bots-pausar` | para o `ro-bot-scheduler.timer` no container `games` (projeto `core`) e depois `ro-bot stop <bot>` para cada linha do `ro-bot list` com ESTADO `active` |
| `bots-retomar` | inicia o `ro-bot-scheduler.timer` |
| `monitor-reiniciar` | `systemctl restart kindle-monitor.service` |
| `svc:<id>:<verbo>` | comando por servico do catalogo `servicos_kindle` (ver abaixo); verbo `reiniciar`, `ligar` ou `parar` |

`ragnarok-reiniciar` e `ollama-reiniciar` (v4) foram removidos: agora sao `svc:rathena-*` e `svc:ollama-gpu:reiniciar`. Uma config antiga que ainda os liste em `comandos.acoes` e recusada.

### Catalogo de servicos (`servicos_kindle`)
Lista no `config.json` (validada no web e no executor, que e root e le o mesmo arquivo em `/etc`; id repetido ou item invalido = o web nao sobe e o executor loga e sai 0). Cada item: `id` (`[a-z0-9-]`, ate 40, sem `--`, nao comeca nem termina com `-`), `rotulo` (ASCII ate 28), `grupo` (`host`|`incus`|`docker`|`ragnarok`), `tipo` (`systemd`|`incus`|`docker`|`rathena`), `alvo` (`^[A-Za-z0-9_.@-]{1,64}$`, nunca comeca com `-`; systemd/rathena terminam em `.service`), `projeto` (so incus, padrao `core`), `prefixo` (so docker; casa contenedores cujo nome comeca com `alvo`, ex.: tarefas do swarm `dokploy.1.xxxx`; exige `verbos: []`), `verbos` (subconjunto de `reiniciar`, `ligar`, `parar`; `[]` = so mostra o estado), `protegido` (recusado enquanto `cerberus-autoupdate.service` estiver ativo: "falhou: atualizacao automatica em andamento") e `opcional` (extra da v5: pode ficar parado sem entrar em "Atencao"). O catalogo do atheron real (48 itens: 17 host, 10 incus, 16 docker, 4 ragnarok) esta em `deploy/config.atheron.json`. Politica: itens de infraestrutura (`docker-socket-proxy`, `dokploy-traefik`, `dokploy`, `dokploy-postgres`, `n8n-postgres`, `n8n-redis`, `incus`, `tailscaled`, `nftables`, `pihole-ftl`, `smbd`) nunca tem `ligar`/`parar`, no maximo `reiniciar`.

Argv montado pelo executor (fixo por tipo; so entram o `alvo` e o `projeto` do catalogo, nunca o pedido): `systemd` -> `systemctl restart|start|stop <alvo>` (40 s); `incus` -> `incus restart|start|stop <alvo> --project <projeto>` (90 s); `docker` -> `incus exec microservices --project core -- docker restart|start|stop <alvo>` (60 s); `rathena` -> `incus exec games --project core -- systemctl restart|start|stop <alvo>` (60 s). O web so aceita `svc:<id>:<verbo>` se o id existe e o verbo esta em `verbos`; o executor repete a checagem. Cooldown (30 s) e dedupe sao por acao (`svc:<id>:<verbo>`).

### Inventario de estados (root)
`kindle-monitor-inventario.timer` (OnBootSec=20s, OnUnitInactiveSec=15s, AccuracySec=1s) dispara `kindle-monitor-inventario.service` (oneshot, root, mesmo endurecimento do executor) que roda `kindle-monitor-executor.py --inventario`. Servicos: 4 chamadas em lote, 10 s de timeout cada, nunca shell (aparelhos e rotinas tem as suas, na secao "Aparelhos, rotinas, sessoes e GitHub"): `systemctl show -p Id,ActiveState,SubState <units...>`; `incus list --all-projects --format csv -c n,s,e`; `incus exec microservices --project core -- docker ps -a --format '{{.Names}} {{.State}}'`; `incus exec games --project core -- systemctl show -p Id,ActiveState,SubState <units...>`. Grava `status/servicos.json` (`{"gerado": epoch, "servicos": {id: {"estado": "ativo|parado|falha|desconhecido", "detalhe": curto}}}`; tmp `O_EXCL|O_NOFOLLOW` + rename via `dir_fd`, dirs conferidos como root; modo 0644 para o `nobody` ler). Chamada que falha deixa so os seus itens `desconhecido`. O web (`coletores.montar_servicos_kindle`) le o arquivo: com mais de 60 s, do futuro, ausente ou corrompido, todos viram `desconhecido`, nao ha botoes de comando e a tela avisa ("estados desatualizados" / "sem inventario de servicos"). Swarm (`prefixo`): todas as tarefas `running` = ativo (`N/N`), alguma nao = falha, nenhuma = parado.

**Requisicao**: `POST /comando`, `Content-Type: application/json`, cabecalho `X-Kindle-Token: <64 hex>`, corpo `{"acao": "<id>"}` (ate 1 KB). Respostas: `202 {"estado":"aceito","acao","id"}`; `400` acao invalida/desligada ou JSON ruim; `401` token ausente/errado (sem detalhe); `403` IP de origem fora de `permitidos_de`; `413` corpo > 1 KB; `415` content-type; `429` mais de 1 pedido a cada 5 s no total (com `Retry-After`); `408` corpo nao chegou em 10 s; `503` comandos desligados (hash do token ou spool ausente; so e revelado a IPs permitidos, o IP e checado antes). O web guarda so o sha256 do token e compara `hmac.compare_digest(sha256(enviado).hexdigest(), hash)`; o corpo e lido com timeout de 10 s. Cada pedido, aceito ou recusado, vai para o journal (stderr) com hora, IP, acao e motivo, nunca o token.

**Estado**: cada resultado e `{"acao","estado":"executando"|"ok"|"falhou","quando":"HH:MM:SS","detalhe":<=80 chars}`; `ultimos(5)` junta os JSON de `comandos.estado` com os pedidos ainda no spool (`executando`), do mais novo ao mais antigo. O executor guarda so os 20 resultados mais novos. O `detalhe` sai em ASCII (a fonte da tela nao tem acentos).

**Config** (secao `comandos`, todas opcionais): `token_hash_arquivo` (padrao `/etc/kindle-monitor/token.sha256`, primeira linha com o sha256 em 64 hex do token cru), `permitidos_de` (padrao `["100.64.0.2","100.64.0.3"]`), `acoes` (ids das acoes rapidas ligadas; padrao as 4; o executor tambem respeita; os `svc:*` dependem so do catalogo), `spool` (padrao `/run/kindle-monitor/spool`; o web nao cria nem muda modo: se faltar, 503), `estado` (padrao `/run/kindle-monitor/status`).

**Instalacao no atheron**: `deploy/instalar-atheron.sh` copia o executor para `/opt/kindle-monitor/deploy/`, instala `kindle-monitor.tmpfiles` em `/etc/tmpfiles.d/kindle-monitor.conf` e roda `systemd-tmpfiles --create` **antes** de reiniciar os servicos, prepara o token (abaixo) **sem imprimi-lo**, instala e habilita `kindle-monitor-executor.path` e reinicia o monitor.

**Diretorios (achado 1)**: `/run/kindle-monitor` (root 0755), `spool/` (`1730 root:nogroup`: o `nobody` so cria arquivos, sticky impede mexer nos alheios; nao consegue listar) e `status/` (root 0755) sao criados pelo tmpfiles.d, **nao** pelo `RuntimeDirectory` (que dava a posse ao `nobody` e permitia trocar spool/status por symlink). O web tem so `ReadWritePaths=/run/kindle-monitor/spool`. O executor (root) abre pai, spool e status com `O_DIRECTORY|O_NOFOLLOW`, confere com `fstat` (dono uid 0, nao gravavel por outros; spool `root:nogroup` com sticky) e dai em diante usa so `dir_fd`; se algo nao bater, recusa tudo e sai 1 com a causa no journal. Sem os diretorios, o web responde 503 e o executor sai 0 com uma linha de log (nada e criado). Como o `nobody` nao lista o spool, os pedidos ainda nao consumidos nao aparecem como "executando" na tela; o resultado aparece quando o executor grava o status.

**Executor**: a `.path` usa `PathExistsGlob=/run/kindle-monitor/spool/*.req` (um `.tmp` ou subdiretorio nao a dispara em laco) e o servico tem `StartLimitIntervalSec=0`. Por passada: ate 10 pedidos; pedido com mais de 60 s (pelo `epoch_ns` do nome) vira `falhou: pedido expirado`; cada acao roda no maximo uma vez (repetida: `falhou: duplicado`); cooldown de 30 s por acao em `status/.cooldown.json` (root); temporarios `.*` com mais de 60 s sao apagados; SIGTERM grava `falhou: interrompido` no item em execucao. Config invalida (tipos, acoes desconhecidas, caminhos nao absolutos) = uma linha no journal e saida 0. **Gate do autoupdate (fail-closed)**: servicos `protegido` consultam `systemctl show -p ActiveState --value cerberus-autoupdate.service` (timeout 10 s) e so rodam com rc 0 e valor exatamente `inactive` ou `failed`; `active`, `activating` (o servico e oneshot sem RemainAfterExit: e assim que ele aparece enquanto roda), `reloading`, `deactivating`, saida vazia, timeout, erro ou rc diferente de 0 bloqueiam. Diretorio chamado `*.req` no spool (religaria a `.path` para sempre) e renomeado para `.lixo-<epoch>-<n>` e removido se vazio. Cooldown: `.cooldown.json` lido ate 64 KiB e podado ao gravar (so o que tem ate 60 s); se estiver ilegivel, corrompido ou grande demais, loga, reescreve vazio e recusa tudo nessa passada (`falhou: cooldown indisponivel`). Orcamento por passada: depois de 400 s nao pega pedido novo (o resto fica no spool e a `.path` dispara de novo), para nunca passar do `TimeoutStartSec=600`. Os subprocessos rodam com `HOME=/root` (o cliente do incus le `/root/.config/incus`; `ProtectHome=read-only` permite a leitura). Cada pedido gera uma linha no journal: `acao=<id> id=<epoch> rc=<n> estado=<ok|falhou> detalhe=<curto>` (sem segredo).

**Token (achado 4) e rotacao**: `deploy/preparar-token.py` (chamado pelo instalador) gera o token cru (`secrets.token_hex(32)`) so se nao houver um valido, em `/etc/kindle-monitor/token.raw` (`root:root 0600`), e grava `/etc/kindle-monitor/token.sha256` (hex do sha256 do token cru, `root:nogroup 0640`), o unico arquivo que o web le. Token existente invalido (nao 64 hex) aborta a instalacao com erro claro; um `/etc/kindle-monitor/token` antigo e valido e migrado para `token.raw`. Para copiar ao Kindle: `sudo head -1 /etc/kindle-monitor/token.raw`. **Rotacao**: `sudo rm /etc/kindle-monitor/token.raw`, rode o instalador de novo (gera outro e atualiza o `.sha256`; o web le o hash a cada pedido, sem reiniciar) e copie o novo token para o Kindle; o antigo para de valer na hora.

**Endurecimento do executor (validar no host)**: `kindle-monitor-executor.service` usa `ProtectSystem=strict`, `ReadWritePaths=/run/kindle-monitor`, `ReadWritePaths=-/var/lib/incus/unix.socket`, `ProtectKernelModules`, `ProtectControlGroups`, `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`, `PrivateTmp`, `NoNewPrivileges`. `kindle-monitor-inventario.service` tem o mesmo endurecimento, mas `ReadWritePaths=/run/kindle-monitor/status` em vez do diretorio todo (so grava `status/*.json`). Isso nao foi testado no atheron: depois de instalar, dispare uma acao de cada tipo (`monitor-reiniciar`, um `svc:` de incus e um de docker) e confira `journalctl -u kindle-monitor-executor` e `journalctl -u kindle-monitor-inventario` (e `cat /run/kindle-monitor/status/servicos.json`) (`systemctl` precisa do D-Bus, `incus` do socket em `/var/lib/incus/unix.socket`). Se falhar, tire primeiro `ProtectSystem=strict` e as linhas `ReadWritePaths`, depois `ProtectKernelModules`/`ProtectControlGroups`; `RestrictAddressFamilies` nunca pode excluir `AF_UNIX`.

## Aparelhos, rotinas, sessoes e GitHub

Quatro fontes do painel do ecossistema (Entrega 2). Quem grava e o executor root (`--inventario`, para `aparelhos.json` e `rotinas.json`) ou o usuario `claude` (hooks e statusline, para as sessoes; timer, para o GitHub). O servidor (`nobody`) so le, valida e corta texto. O coletor le os arquivos na thread de coleta, nunca na requisicao.

| Arquivo | Grava | Onde | Validade no servidor |
|---|---|---|---|
| `aparelhos.json` | executor root | `/run/kindle-monitor/status/` | 60 s (campo `gerado`) |
| `rotinas.json` | executor root | `/run/kindle-monitor/status/` | 60 s |
| `sessoes/<id>.json` | `claude-sessao` (usuario `claude`) | `/var/lib/claude-uso/sessoes/` | batimento ate 10 min |
| `github.json` | `claude-github` (usuario `claude`) | `/var/lib/claude-uso/github.json` | `velho` acima de 20 min |

### aparelhos.json (executor root)

```
{"versao":1,"gerado":<epoch>,"erro":null|"<texto curto>",
 "aparelhos":{"<id>":{"online":true|false|null,"visto_em":<epoch>|null,"conexao":"direto"|"relay"|null}}}
```

- Origem: `tailscale status --json` (argv fixo, sem shell, timeout 10 s, saida ate 4 MiB). Cada peer casa pelo primeiro trecho do `DNSName` (minusculo) com o `nome` do catalogo. Nome repetido: vale o que estiver online.
- `online` vem de `Online` (bool, ou null). `conexao`: `CurAddr` preenchido = `direto`; senao `Relay` = `relay`. `visto_em` vem de `LastSeen` em epoch (antes de 2000 = null).
- Peer fora do catalogo nunca sai no arquivo. Peer do catalogo sem registro no tailnet sai com `online: null`.
- `erro` (ate 40 caracteres): `saida vazia`, `saida grande demais`, `json invalido`, `formato inesperado`, `codigo N`, `tempo esgotado`, `comando indisponivel` ou `falha ao executar`. Com erro, todos saem com `online: null`.

### rotinas.json (executor root)

```
{"versao":1,"gerado":<epoch>,
 "rotinas":{"<id>":{"resultado":"ok"|"falha"|"desconhecido","ultima_em":<epoch>|null,"detalhe":"<ate 24>"}},
 "unidades_falhas":{"n":<int>,"nomes":[<ate 5 nomes>]}}
```

- `timer`: `systemctl show -p Id,Result,LoadState,ExecMainStatus,ExecMainExitTimestamp --timestamp=unix -- <alvos>` (uma chamada). `Result=success` = `ok` com `ultima_em`. Outro resultado = `falha` (detalhe `exit N` ou o proprio resultado). Unidade inexistente = `desconhecido` ("sem unidade"). Nunca rodou = `desconhecido`.
- `arquivo`: mtime do arquivo, ou o maior mtime das entradas diretas do diretorio (ate 2000 entradas; sem ler conteudo; o executor roda como root, entao desce de `/` por descritores com `O_NOFOLLOW` em cada componente, decide o tipo com `fstat` no descritor final e lista pelo proprio descritor: link em qualquer componente = `link ignorado`, e trocar um componente por link no meio da leitura nao desvia nada). Resultado `ok` ou `desconhecido`, nunca `falha`: o atraso sai de `max_idade_h` (aviso).
- `unidades_falhas`: `systemctl list-units --failed --plain --no-legend --no-pager`. `n` conta as linhas; `nomes` guarda as 5 primeiras que casam `^[A-Za-z0-9_.@:-]{1,40}$`. Linha que cita `empresa-x` (qualquer caixa) nao conta nem aparece; o servidor refaz o filtro em `m.rotinas.unidades_falhas` (nome e `n`).
- Se o `systemctl` falhar (saida diferente de 0 ou excecao), todas as rotinas saem `desconhecido` e `unidades_falhas` zerado.

### sessoes/<id>.json (claude-sessao)

```
{"versao":1,"id":"<id>","projeto":"<ate 40>","estado":"aberta"|"trabalhando"|"esperando","desde":<epoch>,"atualizado_em":<epoch>}
```

- `id`: `^[0-9a-f-]{8,64}$`; outro formato e recusado (sem barra, sem `..`). `projeto`: basename do `cwd`, so `[A-Za-z0-9._-]`, ate 40; vazio vira `sessao`.
- Hooks: `UserPromptSubmit` = `trabalhando`; `Stop` e `Notification` = `esperando`; `SessionEnd` apaga o arquivo.
- Statusline (batimento): cria como `aberta` se faltar; senao so renova `atualizado_em`, no maximo a cada 30 s. `desde` so muda quando o estado muda.
- Poda: arquivo com `atualizado_em` de mais de 24 h e apagado na proxima gravacao.
- Gravacao atomica, 0644, sem seguir symlink; cria `sessoes/` (0755) se faltar. So grava na conta pessoal (`CLAUDE_CONFIG_DIR` vazio ou `~/.claude`) e nunca com `cwd` contendo `/empresa-x`.
- Leitor (`dev_fontes.py`): varre ate 500 entradas e le os 50 arquivos regulares de ate 4 KB com nome `<id>.json` de `mtime` mais recente (nao os 50 primeiros por nome: sessoes velhas sem `SessionEnd` nao escondem a viva). **Regra das sessoes: so conta como aberta a sessao com batimento nos ultimos 10 min** (`atualizado_em` com menos de 600 s). Sessao mais velha sai da lista, do total e dos alertas. `atualizado_em` mais de 60 s no futuro, estado fora dos tres valores ou `desde` invalido: sessao descartada. `esperando` ha `sessao_esperando_min` ou mais = alerta leve.

### github.json (claude-github)

```
{"versao":1,"gerado_em":<epoch>,"dono":"<login>",
 "prs":[{"repo","numero","titulo","rascunho","ci"}],     (ate 20)
 "ci":[{"repo","branch","estado"}]}                      (ate 30)
```

- Uma chamada `gh api graphql` (argv em lista, timeout 60 s). Repos com afiliacao `OWNER` do login `brno01` (ate 30, por `PUSHED_AT`); arquivados e de outro dono sao descartados. PRs `OPEN` (ate 10 por repo). O `ci` do PR e o rollup do ultimo commit; o `ci` do repo e o rollup da branch padrao (so esta entra no alerta de CI).
- Estado: `SUCCESS` = `ok`; `FAILURE` e `ERROR` = `falha`; `PENDING` e `EXPECTED` = `pendente`; outro valor = null (no PR) ou entrada omitida (no CI).
- Titulos e nomes: NFKD, so ASCII imprimivel, sem controles, espacos colapsados. O gravador corta em 80 (titulo) e 40 (repo, branch); o leitor corta o titulo em 60.
- Se o `gh` falhar, o gravador nao grava (o arquivo antigo fica) e sai com 1.
- Leitor: ate 64 KB; `velho` acima de 1200 s (20 min). `abertos` conta so os PRs que cabem em `prs` (no maximo 20).

### O que o servidor entrega

- `m["aparelhos"]` (so com o catalogo): `{"inventario": "ok"|"velho"|"ausente", "idade_s", "itens": [{"id","rotulo","icone","online","offline_min","conexao","alerta_offline_min"}]}`. Aparelho com `alerta_offline_min` que esta offline sem `visto_em` conta os minutos desde a primeira vez que o servidor o viu offline (guardado em memoria; zera quando volta a ficar online).
- `m["rotinas"]` (so com o catalogo): `{"inventario", "idade_s", "itens": [{"id","rotulo","resultado","ultima_em","idade_h","max_idade_h","atrasada","tipo","alvo"}], "unidades_falhas": {"n","nomes"}}`; `alvo` so existe para `timer` (o caminho de um `arquivo` nao sai). Em `aparelhos` e `rotinas`, `relogio_adiantado: true` aparece so quando o `gerado` esta no futuro.
- Com inventario `velho` ou `ausente`, os itens saem com `online: null` ou `desconhecido`, e nenhuma unidade em falha e contada.
- `m["claude"]["sessoes"]` (so com `claude.sessoes`): `{"itens": [{"projeto","estado","desde_s"}] (ate 12, da menor `desde_s`), "total", "esperando", "idade_s"}`. `total` conta as sessoes validas lidas (ate 50 arquivos). Ou `{"erro": "n/d"}`.
- `m["github"]` (so com `github.resumo`): `{"prs": [...], "ci": [...], "abertos", "ci_falhas", "idade_s", "velho"}`. Ou `{"erro": "n/d"}`.
- `m["limiares"]`: sempre (tabela na secao "Config").

### Privacidade (Entrega 2)

- empresa-x: `nome` com `empresa-x` recusa a lista de aparelhos (servidor e executor). Peer fora do catalogo nunca vai para `aparelhos.json`. Sessao de `cwd` com `/empresa-x` nao e gravada, e so a conta pessoal grava. GitHub: so repos do dono pessoal (afiliacao `OWNER` e login `brno01`); PRs e CI de organizacao nao entram.
- Leitura das fontes pelo servidor (`nobody`): `coletores.ler_arquivo_padrao` abre com `O_NOFOLLOW|O_NONBLOCK`, confere `S_ISREG` e o tamanho (256 KB) no descritor e le no maximo o limite; FIFO, link, dispositivo, diretorio ou arquivo grande dao o mesmo erro de arquivo ausente (`n/d`). Vale para `limites.json`, `tokens.json`, `sessoes/*.json`, `github.json`, os inventarios e `/proc`.
- Limite conhecido: a checagem de `claude-sessao` e um substring em minusculas (`/empresa-x`), sem ignorar caixa. Um `cwd` com `empresa-x` nao e barrado, e o leitor nao filtra por nome de projeto.
- Nenhum IP, chave ou e-mail nos JSON. `aparelhos.json` nao tem nome, IP, usuario nem SO. As sessoes guardam so o basename do projeto. `rotinas.json` guarda nomes de unidades systemd em falha (ate 5).
- `github.json` guarda o login do dono (`dono`), nomes de repositorio, titulos de PR e estado de CI. Sao dados da conta pessoal, mostrados no Kindle; nao sao IP, chave nem e-mail.

## Testes
```
cd server && (umask 022; python3 -I -m unittest discover -s tests)              # 1074 testes (19/11/2026)
cd server && (umask 022; python3 -I -m unittest discover -s tests -p test_alertas.py -v)   # um modulo
```
Os testes usam fixtures e fakes: nao precisam de rede, `nvidia-smi`, `systemctl` nem `/var/lib/cerberus`. Com `umask 0002` os testes do executor falham (ele recusa arquivo gravavel pelo grupo). Falha conhecida, anterior a esta branch e so neste servidor: `test_executor.FilaTest.test_limpeza_20_mais_novos` (21 != 20).

## Imagem (`/tela.png`)
Retrato 1236x1648, seis abas na barra de navegacao fixa no rodape (96 px; icone de 30 px em cima e rotulo sempre em negrito 26: Inicio, Servicos, Aparelhos, Sistema, Dev, Acoes; a aba atual invertida). Cabecalho fino (~70 px): host, resumo dos servicos ("48 servicos · 41 ok · 5 parados"; ou o aviso de inventario velho) e hora (HH:MM, sem segundos). Visual e-ink: alto contraste, contornos finos, raios pequenos, sem sombras; fontes embutidas 26 e 34 (negrito tambem 48, 72 e 140). Estado de servico por forma antes da cor: cheia = ativo, vazia = parado, X = falha, ? = desconhecido.
- **Inicio** (`resumo`): cartao ATENCAO no alto, so com os alertas do motor (criticos, avisos e leves; "Tudo em ordem" sem alertas), com a altura que ele precisa; faixa de historico (CPU e RAM) no espaco que sobrar. Abaixo, 8 linhas de sistema, cada uma com icone de 56 px, titulo, valor e detalhe: ATHERON (CPU, RAM, temperatura e `/`), NAS (os discos que nao sao `/`), APARELHOS ("N de M online"; offline no detalhe, e bateria do Kindle e do S10), SERVICOS ("N de M ok" e o detalhe por grupo), ROTINAS ("N de M ok", ou "N unidades em falha", ou a rotina em problema), CLAUDE (limites de 5 h e semanal, e "N sessoes, M esperando"), GITHUB ("N PRs abertos", com o CI no detalhe) e RAGNAROK (jogadores e portas no detalhe). Tocar numa linha abre a aba de destino (`pagina:<destino>`, ver "Contrato com o Kindle"). Quando o estado da linha nao e `ok`, uma forma no canto direito mostra o estado: X (critico), ! (aviso), vazia (leve) ou ? (sem dados).
- **servicos**: lista densa agrupada (HOST / CONTEINERES / DOCKER / RAGNAROK, com "N de M ativos"), uma linha por servico: forma do estado, rotulo (34 ou 26), estado e, a direita, botoes contextuais de 190x84 px com 16 px de espaco (ativo: Reiniciar e Parar; parado: Ligar; falha: Reiniciar; desconhecido ou sem verbos: nada; se o catalogo so permite `reiniciar`, ele tambem serve para ligar). Paginada: "Pagina X/N" e `< Anterior` / `Proxima >` no topo, so quando ha mais de uma pagina (o atheron real da 4). A divisao em paginas so depende do catalogo (linha de 100 px, ou 64 px se o item nao tem verbos), nao do estado.
- **Sistema** (`detalhes`): discos completos, memoria (RAM, swap, VRAM), I/O, temperaturas (CPU e GPU), carga, uptime, historico (sparklines de ~15 min) e o cartao ROTINAS (forma, rotulo e "ha N h", "falhou" ou "atrasada" por rotina; linha de unidades em falha). Kindle, grupos de servicos, Ragnarok e pares sairam daqui.
- **Aparelhos** (`aparelhos`): cartao TAILNET (uma linha por aparelho: forma de online, offline ou sem dado; "direto" ou "relay" quando online; "offline ha N min" quando offline), cartao Kindle, cartao S10 (bateria, estado, temperatura, cinco caminhos com forma cheia/X/?, avisos; le `m["s10"]`, so se houver na config) e os pares.
- **Dev** (`claude`, so leitura): cartao Claude (icone, janelas de 5 h e semanal com barra, % e quando volta; >= 90 % em negrito grande e preto; `renovado` mostra 0 %; dados velhos mostram "ha N min/h" em cinza; tokens de hoje e de 7 dias com custo), cartoes SESSOES (uma linha por sessao: projeto, forma do estado e ha quanto tempo) e GITHUB (PRs como "repo#n titulo", CI por repo). Le `m["claude"]`; sem a chave: "Claude desligado na config".
- **Acoes** (`comandos`): grade 2x2 das 4 acoes rapidas, bloco AJUSTES (os tres perfis de energia, com o ativo destacado) e "ULTIMOS COMANDOS" (ate 8; servico aparece como "Reiniciar <id>") no espaco que sobrar. Saiu daqui o ATENCAO, que ficou no Inicio.
Nada e cortado, sobreposto ou desenhado fora da imagem (testado com canvas estrito em 1236x1648, 1072x1448 e 800x1300, inclusive 52 servicos com varios em falha e 8 comandos recentes). Textos sem acento (a fonte embutida e ASCII mais `°` e `·`). Botoes de linha e de acao tem no minimo 150x84 px e 16 px de folga entre si.

Em producao so entram `alertas.py` (motor de alertas), `botoes.py` (layout dos botoes), `ecossistema.py` (aparelhos e rotinas), `dev_fontes.py` (sessoes e GitHub), `icones_dados.py` (icones), `png.py` (encoder PNG com `struct` + `zlib`), `canvas.py` (desenho) e `render_png.py` (layout). As fontes DejaVu vem **pre-rasterizadas** em `fonte_dados.py` (arquivo gerado, ~300 KB; licenca DejaVu/Bitstream Vera no topo do arquivo). Para regerar (ferramenta de desenvolvimento, usa Pillow so via `uv`, nada global):
```
uv run --with pillow python tools/gerar_fonte.py        # reescreve server/fonte_dados.py
```
Para ver o resultado sem subir o servidor (dados que imitam o atheron real):
```
python3 -I tools/preview.py --saida /tmp/tela.png                                   # aba Inicio, estado ok
python3 -I tools/preview.py --saida /tmp/tela.png --pagina servicos --p 2 --armado svc:ai-agent:reiniciar
python3 -I tools/preview.py --saida /tmp/tela.png --pagina comandos --modo economia
python3 -I tools/preview.py --saida /tmp/tela.png --estado alertas                  # disco a 91 %, 2 servicos em falha, bateria do Kindle a 12 %
python3 -I tools/preview.py --saida /tmp/tela.png --estado velho                    # inventario e limites do Claude velhos
python3 -I tools/preview.py --saida /tmp/tela.png --cheia                           # 52 servicos, varios em falha, 8 comandos
python3 -I tools/preview.py --todas /tmp/prev                                       # <pagina>-<estado>.png: 6 abas x 3 estados = 18 PNGs
python3 -I tools/preview.py --saida /tmp/x.png --porta 8765 --pagina servicos --p 2 # baixa de um servidor local
```
`--pagina` aceita as 6 abas (`resumo`, `servicos`, `aparelhos`, `detalhes`, `claude`, `comandos`); `--estado` aceita `ok`, `alertas` e `velho`.

## Ícones
`server/icones_dados.py` e gerado por `tools/gerar_icones.py` (nao editar a mao). Entrada: `tools/icones/<nome>.svg`, com `<nome>` em `^[a-z]{2,16}$` (os outros arquivos sao ignorados); sao 23 icones, em 56, 40 e 30 px. Os SVGs sao tratados como dado nao confiavel: so os atributos `d`, `fill-rule` e `viewBox` sao lidos, por regex, sem parser XML.

Origem e licenca ficam no comentario `<!-- Source: ... -->` no topo de cada SVG, e o cabecalho de `icones_dados.py` as repete:
- Material Symbols (`@material-symbols/svg-400` 0.49.0 via jsDelivr, estilo `outlined`, variante `-fill`), Apache-2.0: inicio, servidor, nas, aparelhos, notebook, celular, leitor, servicos, conteiner, rotinas, backup, jogo, alerta, ok, rede, temperatura, acoes, sistema, dev.
- Simple Icons 16.38.0 (CC0), com nota de marca registrada de uso privado: `claude`, `github`, `docker`, `tailscale`.

Regerar (ferramenta de desenvolvimento; Pillow e svgelements so via `uv`):
```
uv run --no-project --with pillow --with svgelements python tools/gerar_icones.py
```

## Instalacao da Entrega 2

**Estado: pendente.** Nada desta secao foi executado. A Entrega 2 nao esta instalada no atheron.

Root (dono; R4 e R6 do plano `docs/superpowers/plans/2026-11-18-painel-ecossistema.md`):

1. Backup (R4), em diretorio novo: `sudo bash -c 'D=/root/backup/kindle-monitor-antes-entrega2-$(date +%F-%H%M); install -d -m 0700 "$D"; cp -a /opt/kindle-monitor /etc/kindle-monitor /etc/systemd/system/kindle-monitor* /etc/tmpfiles.d/kindle-monitor*.conf "$D"/; ls -la "$D"'`. Verificar: a listagem mostra os quatro itens.
2. Servidor, executor e units: o comando "Atualizar o atheron" do `CLAUDE.md`, com `R=~/development/worktrees/kindle-monitor-ecossistema`. Ele copia `server/` e `deploy/` e roda `instalar-atheron.sh` (daemon-reload e reinicio do monitor). A unit `kindle-monitor-inventario.service` passa a gravar so em `/run/kindle-monitor/status` (`ReadWritePaths=/run/kindle-monitor/status`; o socket do Tailscale nao precisa de entrada, `connect()` funciona em mount somente leitura). A unit do executor nao muda nesta entrega.
3. O instalador grava `deploy/config.atheron.json` sobre `/etc/kindle-monitor/config.json`. Os catalogos `aparelhos` e `rotinas` vao junto por esse arquivo. Ajuste feito so no host se perde na proxima instalacao: edite no repo.
4. Verificar: `sudo cat /run/kindle-monitor/status/{aparelhos,rotinas}.json` (o campo `gerado` deve andar a cada ~15 s); `journalctl -u kindle-monitor-inventario -n 20` sem erro; `systemctl is-active kindle-monitor`.
5. Se o hardening bloquear o socket do Tailscale, afrouxar na ordem da secao "Endurecimento do executor" (`ProtectSystem=strict` e os `ReadWritePaths` primeiro). `RestrictAddressFamilies` nunca pode excluir `AF_UNIX`.
6. Desfazer: restaurar o backup do R4 (`/opt/kindle-monitor`, `/etc/kindle-monitor/config.json`, units e tmpfiles); `systemctl daemon-reload && systemctl restart kindle-monitor.service kindle-monitor-inventario.timer`; e apagar `/run/kindle-monitor/status/{aparelhos,rotinas}.json`.

Usuario `claude` (R7; passos da sessao principal):

1. Pre-requisito: a branch `feat/bypass-e-painel-dev` do dotfiles precisa estar mesclada no master do checkout `~/development/dotfiles`. **Hoje nao esta**: a branch tem 4 commits a frente de `origin/master`. Decisao do dono: merge local ou PR.
2. Depois do merge: `claude-mirror install` (cria os links `~/.local/bin/claude-sessao` e `claude-github`; o statusline chama `claude-sessao` pelo nome). Depois: `ln -sfn "$PWD/claude/painel/systemd/claude-github."{service,timer} ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable --now claude-github.timer`. O timer roda 1 min depois do boot e a cada 5 min. Abrir uma sessao nova do Claude.
3. Verificar: `ls /var/lib/claude-uso/sessoes`; `jq '.prs|length' /var/lib/claude-uso/github.json` contra `gh pr list`.
4. Desfazer: `systemctl --user disable --now claude-github.timer`; reverter o commit dos hooks e do statusline; `rm -r /var/lib/claude-uso/sessoes`.

### Pendencias desta entrega

- R5: alvos `arquivo` do Syncthing do cofre e do segundo cerebro ainda nao estao em `deploy/config.atheron.json`. Confirmar como root: `sudo ls -lt /srv/nas/vault | head` e `sudo systemctl status cerberus-syncthing --no-pager`. `/srv/nas/vault` e do grupo `cofre` (0770), e o `claude` nao lista. Depois, commit de ajuste na config.
- Nao confirmado no host: a unit `cerberus-vault-backup.service` (rotina `senhas`), o caminho `/srv/nas/backups/vaultwarden`, o acesso do executor ao socket do Tailscale e a saida real de `tailscale status --json` nesse ambiente.
- Pior caso do inventario: as quatro chamadas de servicos (10 s cada), mais `tailscale status` (10 s), `systemctl show` das rotinas (10 s) e `systemctl list-units` (10 s), somam ate 70 s; a unit tem `TimeoutStartSec=120` para isso caber com folga.
- Paridade: a unica diferenca de validacao entre executor e servidor e o icone (`tests/test_paridade_catalogos.py`).

## Recuperacao: Kindle com a interface parada
Enquanto o monitor roda, o supervisor para a interface do Kindle (`lab126_gui`) e desliga o toque; o botao de energia o encerra normalmente. Se o supervisor morrer sem limpar (SIGKILL, falta de memoria), o Kindle pode ficar com a tela congelada e sem toque. Recuperar: `ssh root@kindle-monitor 'start lab126_gui; lipc-set-prop com.lab126.deviced enable_touch 1'` (ou, sem rede, segurar o botao de energia por ~40 s para reiniciar o aparelho).
