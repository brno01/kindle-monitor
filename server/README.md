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
| `/tela.txt` | texto puro ASCII, uma linha por linha da tela (ate `--colunas` colunas e 26 linhas; linhas `IO`/`NET` quando ha `io` na config), barras como `[#####-----]  50%`; inclui a linha `Portas: LOGIN ok CHAR ok MAP FALHA` |
| `/tela.png` | imagem PNG 8-bit em tons de cinza (`image/png`), `--largura` x `--altura` (padrao 1236x1648, Kindle Paperwhite 5), gerada so com a biblioteca padrao |
| `/historico.json` | anel em memoria das ultimas 60 amostras: `intervalo_s`, `max`, `t` (epoch), `cpu`, `ram` e `gpu` (so se houver GPU), em %, da mais antiga para a mais nova (`null` = leitura falhou) |
| `/metricas.json` | metricas brutas em JSON (`host`, `gerado_em` ISO, cpu, ram, gpu, discos, io, servicos, ragnarok, portas, historico, pares). `?pares=0` nao consulta os pares |
| `/botoes.json` | `{"largura","altura","pagina","botoes":[{id,rotulo,x,y,w,h,tipo,armado}]}`: fonte unica do layout dos botoes (pixels do PNG, origem no canto superior esquerdo); o render desenha exatamente estes retangulos (`botoes.py`) |
| `/saude` | `ok` |
| `/comando/estado` | lista JSON dos ultimos comandos (mesma de `metricas.comandos`) |
| `POST /comando` | registra um pedido de comando (ver "Comandos"); exige token |

Parametros (GET): `/tela.png`, `/tela.txt` e `/botoes.json` aceitam `?pagina=resumo|detalhes|comandos` (padrao `resumo`); `/tela.png` e `/botoes.json` aceitam `&armado=<id>` (so ids da pagina comandos: `gpu-descarregar`, `bots-pausar`, `bots-retomar`, `monitor-reiniciar`, `ragnarok-reiniciar`, `ollama-reiniciar`; o botao armado aparece invertido com "Toque de novo para confirmar"). Valor invalido e ignorado (usa o padrao), nunca 500. Os botoes de comando chamam `POST /comando` (ver "Comandos"). A pagina comandos mostra ate 5 itens de `metricas["comandos"]` (`{acao, estado, quando, detalhe}`) se existirem.

Outro caminho: 404. Metodo diferente de GET: 405 (menos `POST /comando`). Todas as respostas levam `Cache-Control: no-store`.

## Config (`config.exemplo.json`)
Copie para `config.json` e ajuste. Chaves que comecam com `_` sao comentarios e sao ignoradas.
- `host`: nome exibido (padrao: hostname).
- `discos`: lista de entradas de dois tipos. `{rotulo, caminho}` mede o ponto de montagem com `statvfs`. `{rotulo, tier_state}` le o JSON do Cerberus (`ssd_used_gib` / `cap_gib`, em GiB; usado para o "NAS SSD", porque o `/srv/nas` e uma uniao mergerfs que soma discos inteiros). Se o arquivo faltar ou os numeros forem invalidos (negativos, tipo errado, `cap_gib` <= 0) a linha mostra `n/d`; se `when` faltar ou tiver mais de 3 h a linha mostra o valor com o aviso `parado`. Cada entrada tem `caminho` ou `tier_state`, nunca os dois.
- `servicos`: unidades systemd checadas com `systemctl is-active` (mostra `ok` ou `FALHA`).
- `balanceador`: JSON do balanceador do Ragnarok (padrao `/var/lib/cerberus/memory-balancer.json`; `null` desliga). `players_by.ragnarok` ausente conta como 0 jogadores; `updated` com mais de 120 s marca o dado como `PARADO`.
- `pares`: lista de `{nome, url}` de outros servidores iguais a este; busca `<url>/metricas.json?pares=0` com timeout de 2 s. Se falhar, a tela mostra `nome: sem resposta`.
- `portas`: lista de `{rotulo, host, porta}` testadas com conexao TCP (timeout de 0,6 s, em paralelo, resultado em cache por ~5 s). `rotulo` tem ate 12 caracteres (letras, digitos, `_`, `.`, `-`), `host` e IP literal ou nome simples e `porta` vai de 1 a 65535; valor invalido faz o servidor recusar a config. Aparece como `portas: [{rotulo, aberto}]` no JSON, como linha `Portas:` no texto e como "pilulas" na imagem (preenchida = aberta, so contorno com X = fechada). Os valores do exemplo (`10.0.0.60`, 6900/6121/5121) sao os padroes do rAthena: ajuste para o seu.
- `intervalo_historico_s`: segundos entre as amostras do historico (padrao `15`; entre 0 e 3600). Uma thread de fundo (daemon) guarda CPU %, RAM % e GPU % das ultimas 60 amostras (15 min no padrao); alimenta o grafico da imagem e o `/historico.json`. So memoria: nada e escrito em disco, e o historico recomeca vazio ao reiniciar.
- `intervalo_cpu_s`: intervalo entre as duas leituras de `/proc/stat` (padrao `0.5`, entre 0 e 5). So vale na primeira leitura ou quando a amostra anterior tem mais de 30 s; nas demais requisicoes o CPU % vem da diferenca entre a leitura atual e a anterior, sem dormir.
- `cache_cpu_s`: segundos em que o CPU % calculado fica em cache (padrao `1.5`, entre 0 e 60). Com o Kindle pedindo a tela a cada ~2 s, o numero muda a cada requisicao. Requisicao a menos de 0,5 s da amostra anterior reutiliza o ultimo valor.
- `io`: `{"discos": [{"rotulo", "dev"}], "redes": [{"rotulo", "if"}]}`. `dev` e o nome do dispositivo em `/proc/diskstats` (ex.: `nvme0n1`, `sda`; setores lidos = coluna 6, escritos = coluna 10, setor de 512 bytes) e `if` o da interface em `/proc/net/dev` (`rx_bytes` e `tx_bytes`). `dev` e `if` aceitam so letras, digitos, `.`, `_` e `-` (ate 32); `rotulo` tem de 1 a 16 caracteres ASCII simples; valor invalido faz o servidor recusar a config. Padrao: nada (`{"discos": [], "redes": []}`, sem bloco na tela).
- `intervalo_io_s`: intervalo (padrao `0.3`, entre 0 e 5) entre as duas leituras feitas na primeira requisicao de I/O ou quando a amostra anterior tem mais de 30 s.

### I/O: como as taxas sao calculadas
As taxas (bytes/s) saem da diferenca entre a amostra atual e a anterior, guardada em memoria, dividida pelo tempo (relogio monotonico) entre elas. Na primeira requisicao, ou se a amostra anterior tiver mais de 30 s, o servidor le duas vezes com `intervalo_io_s` entre as leituras. Se a ultima amostra tem menos de 0,5 s, a ultima taxa e reutilizada (nada e lido). Contador que voltou para tras (reboot, overflow) da `null` (`n/d` na tela) naquela amostra, nunca taxa negativa. Dispositivo ou interface que nao existe em `/proc` some da tela e do JSON; se o proprio arquivo de `/proc` nao puder ser lido, as linhas aparecem com `n/d`.

`metricas.io`: `{"discos": [{"rotulo", "dev", "leitura_bps", "escrita_bps"}], "redes": [{"rotulo", "if", "rx_bps", "tx_bps"}]}`, em bytes/s (numero ou `null`). A chave so existe se a config tiver algum dispositivo/interface; se a leitura falhar, vale `{"erro": "n/d"}`.

Unidades na tela: **base 1024** (1 KB/s = 1024 B/s, 1 MB/s = 1024 KB/s, igual aos GiB da RAM), uma casa decimal: `512 B/s`, `40.0 KB/s`, `12.3 MB/s`. No `/tela.txt` a forma curta: `IO NVMe r 12.3M w 1.2M` e `NET LAN rx 3.4M tx 0.2M` (`B`, `K`, `M`, `G`; o rotulo e encurtado se a linha passar de `--colunas`).

Cada coletor falha isolado: o que der erro aparece como `n/d` na tela e nunca derruba a requisicao. Sem GPU NVIDIA ou sem sensor de temperatura, a linha simplesmente nao aparece.

## Comandos (POST /comando)
O servidor continua sem privilegio (`User=nobody`, `ProtectSystem=strict`). Para mudar o atheron a partir do Kindle (com confirmacao em dois toques na tela), o processo web so **registra um pedido**; quem executa e um **executor root separado**, com uma tabela fixa de acoes. Nunca ha shell nem comando montado a partir do pedido.

```
Kindle --POST /comando {"acao":"..."} + X-Kindle-Token--> kindle-monitor.service (nobody)
   grava /run/kindle-monitor/spool/<epoch_ns>-<acao>.req (vazio, tmp + rename)
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
| `ragnarok-reiniciar` | reinicia `rathena-login`, `rathena-char` e `rathena-map` no container `games`; **recusado** durante a janela de atualizacao automatica (`cerberus-autoupdate.service` ativo) |
| `ollama-reiniciar` | `systemctl restart ollama-gpu.service`; tambem recusado durante a atualizacao automatica |

**Requisicao**: `POST /comando`, `Content-Type: application/json`, cabecalho `X-Kindle-Token: <64 hex>`, corpo `{"acao": "<id>"}` (ate 1 KB). Respostas: `202 {"estado":"aceito","acao","id"}`; `400` acao invalida/desligada ou JSON ruim; `401` token ausente/errado (sem detalhe); `403` IP de origem fora de `permitidos_de`; `413` corpo > 1 KB; `415` content-type; `429` mais de 1 pedido a cada 5 s no total (com `Retry-After`); `408` corpo nao chegou em 10 s; `503` comandos desligados (hash do token ou spool ausente; so e revelado a IPs permitidos, o IP e checado antes). O web guarda so o sha256 do token e compara `hmac.compare_digest(sha256(enviado).hexdigest(), hash)`; o corpo e lido com timeout de 10 s. Cada pedido, aceito ou recusado, vai para o journal (stderr) com hora, IP, acao e motivo, nunca o token.

**Estado**: cada resultado e `{"acao","estado":"executando"|"ok"|"falhou","quando":"HH:MM:SS","detalhe":<=80 chars}`; `ultimos(5)` junta os JSON de `comandos.estado` com os pedidos ainda no spool (`executando`), do mais novo ao mais antigo. O executor guarda so os 20 resultados mais novos. O `detalhe` sai em ASCII (a fonte da tela nao tem acentos).

**Config** (secao `comandos`, todas opcionais): `token_hash_arquivo` (padrao `/etc/kindle-monitor/token.sha256`, primeira linha com o sha256 em 64 hex do token cru), `permitidos_de` (padrao `["100.64.0.2","100.64.0.3"]`), `acoes` (ids ligados; padrao todos; o executor tambem respeita), `spool` (padrao `/run/kindle-monitor/spool`; o web nao cria nem muda modo: se faltar, 503), `estado` (padrao `/run/kindle-monitor/status`).

**Instalacao no atheron**: `deploy/instalar-atheron.sh` copia o executor para `/opt/kindle-monitor/deploy/`, instala `kindle-monitor.tmpfiles` em `/etc/tmpfiles.d/kindle-monitor.conf` e roda `systemd-tmpfiles --create` **antes** de reiniciar os servicos, prepara o token (abaixo) **sem imprimi-lo**, instala e habilita `kindle-monitor-executor.path` e reinicia o monitor.

**Diretorios (achado 1)**: `/run/kindle-monitor` (root 0755), `spool/` (`1730 root:nogroup`: o `nobody` so cria arquivos, sticky impede mexer nos alheios; nao consegue listar) e `status/` (root 0755) sao criados pelo tmpfiles.d, **nao** pelo `RuntimeDirectory` (que dava a posse ao `nobody` e permitia trocar spool/status por symlink). O web tem so `ReadWritePaths=/run/kindle-monitor/spool`. O executor (root) abre pai, spool e status com `O_DIRECTORY|O_NOFOLLOW`, confere com `fstat` (dono uid 0, nao gravavel por outros; spool `root:nogroup` com sticky) e dai em diante usa so `dir_fd`; se algo nao bater, recusa tudo e sai 1 com a causa no journal. Sem os diretorios, o web responde 503 e o executor sai 0 com uma linha de log (nada e criado). Como o `nobody` nao lista o spool, os pedidos ainda nao consumidos nao aparecem como "executando" na tela; o resultado aparece quando o executor grava o status.

**Executor**: a `.path` usa `PathExistsGlob=/run/kindle-monitor/spool/*.req` (um `.tmp` ou subdiretorio nao a dispara em laco) e o servico tem `StartLimitIntervalSec=0`. Por passada: ate 10 pedidos; pedido com mais de 60 s (pelo `epoch_ns` do nome) vira `falhou: pedido expirado`; cada acao roda no maximo uma vez (repetida: `falhou: duplicado`); cooldown de 30 s por acao em `status/.cooldown.json` (root); temporarios `.*` com mais de 60 s sao apagados; SIGTERM grava `falhou: interrompido` no item em execucao. Config invalida (tipos, acoes desconhecidas, caminhos nao absolutos) = uma linha no journal e saida 0. Cada pedido gera uma linha no journal: `acao=<id> id=<epoch> rc=<n> estado=<ok|falhou> detalhe=<curto>` (sem segredo).

**Token (achado 4) e rotacao**: `deploy/preparar-token.py` (chamado pelo instalador) gera o token cru (`secrets.token_hex(32)`) so se nao houver um valido, em `/etc/kindle-monitor/token.raw` (`root:root 0600`), e grava `/etc/kindle-monitor/token.sha256` (hex do sha256 do token cru, `root:nogroup 0640`), o unico arquivo que o web le. Token existente invalido (nao 64 hex) aborta a instalacao com erro claro; um `/etc/kindle-monitor/token` antigo e valido e migrado para `token.raw`. Para copiar ao Kindle: `sudo head -1 /etc/kindle-monitor/token.raw`. **Rotacao**: `sudo rm /etc/kindle-monitor/token.raw`, rode o instalador de novo (gera outro e atualiza o `.sha256`; o web le o hash a cada pedido, sem reiniciar) e copie o novo token para o Kindle; o antigo para de valer na hora.

**Endurecimento do executor (validar no host)**: `kindle-monitor-executor.service` usa `ProtectSystem=strict`, `ReadWritePaths=/run/kindle-monitor`, `ReadWritePaths=-/var/lib/incus/unix.socket`, `ProtectKernelModules`, `ProtectControlGroups`, `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`, `PrivateTmp`, `NoNewPrivileges`. Isso nao foi testado no atheron: depois de instalar, dispare uma acao de cada tipo (`monitor-reiniciar` e `ragnarok-reiniciar`) e confira `journalctl -u kindle-monitor-executor` (`systemctl` precisa do D-Bus, `incus` do socket em `/var/lib/incus/unix.socket`). Se falhar, tire primeiro `ProtectSystem=strict` e as linhas `ReadWritePaths`, depois `ProtectKernelModules`/`ProtectControlGroups`; `RestrictAddressFamilies` nunca pode excluir `AF_UNIX`.

## Testes
```
cd server && python3 -I -m unittest discover -s tests
```
Os testes usam fixtures e fakes: nao precisam de rede, `nvidia-smi`, `systemctl` nem `/var/lib/cerberus`.

## Imagem (`/tela.png`)
Retrato 1236x1648, tres paginas e barra de navegacao fixa no rodape (Atualizar, Resumo, Detalhes, Comandos; a pagina atual invertida). Cabecalho compacto (host e hora com segundos, ~90 px, sem faixa preta).
- **resumo**: cartoes com contorno fino para CPU, RAM, GPU e o disco mais cheio (numero de 140 px, barra e sparkline; GPU "desativada" sem barra), cartao do Ragnarok (jogadores + pilulas das portas, aviso `PARADO`) e cartao dos servicos ("6 ok" ou a lista dos que falharam).
- **detalhes**: todos os discos (usado / total), bloco de I/O (DISCO L/E, REDE rx/tx), TEMP/CARGA/UP, lista completa de servicos (falhas primeiro) e cartoes dos pares.
- **comandos**: grade de botoes em "ACOES LEVES" e "SERVICOS (derruba por alguns segundos)" (borda grossa), confirmacao em dois toques (`?armado=`) e "ULTIMOS COMANDOS".
Se nao couber, o layout reduz densidade e, no limite, omite itens (`+N servicos`), sem cortar texto nem desenhar fora da imagem. Textos sem acento (a fonte embutida e ASCII mais `°` e `·`). Os botoes tem no minimo 150x110 px e 16 px de folga entre si.

Em producao so entram `botoes.py` (layout dos botoes), `png.py` (encoder PNG com `struct` + `zlib`), `canvas.py` (desenho) e `render_png.py` (layout). As fontes DejaVu vem **pre-rasterizadas** em `fonte_dados.py` (arquivo gerado, ~300 KB; licenca DejaVu/Bitstream Vera no topo do arquivo). Para regerar (ferramenta de desenvolvimento, usa Pillow so via `uv`, nada global):
```
uv run --with pillow python tools/gerar_fonte.py        # reescreve server/fonte_dados.py
```
Para ver o resultado sem subir o servidor: `python3 -I tools/preview.py --saida /tmp/tela.png [--cheia]` (dados de exemplo; `--cheia` usa 8 servicos e 3 discos; `--pagina` e `--armado` escolhem a pagina) ou `--porta 8765` para baixar de um servidor local.
