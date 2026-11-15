# kindle-monitor: servidor

Servidor HTTP em Python 3 (somente biblioteca padrao) que coleta metricas do host e serve uma "tela" pronta para o Kindle: texto ASCII (`/tela.txt`) ou uma imagem PNG estilizada em tons de cinza (`/tela.png`, 1236x1648, para o FBInk). Somente GET, somente leitura, sem autenticacao, nao escreve em disco.

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
| `/tela.txt` | texto puro ASCII, uma linha por linha da tela (ate `--colunas` colunas e 26 linhas), barras como `[#####-----]  50%`; inclui a linha `Portas: LOGIN ok CHAR ok MAP FALHA` |
| `/tela.png` | imagem PNG 8-bit em tons de cinza (`image/png`), `--largura` x `--altura` (padrao 1236x1648, Kindle Paperwhite 5), gerada so com a biblioteca padrao |
| `/historico.json` | anel em memoria das ultimas 60 amostras: `intervalo_s`, `max`, `t` (epoch), `cpu`, `ram` e `gpu` (so se houver GPU), em %, da mais antiga para a mais nova (`null` = leitura falhou) |
| `/metricas.json` | metricas brutas em JSON (`host`, `gerado_em` ISO, cpu, ram, gpu, discos, servicos, ragnarok, portas, historico, pares). `?pares=0` nao consulta os pares |
| `/saude` | `ok` |

Outro caminho: 404. Metodo diferente de GET: 405. Todas as respostas levam `Cache-Control: no-store`.

## Config (`config.exemplo.json`)
Copie para `config.json` e ajuste. Chaves que comecam com `_` sao comentarios e sao ignoradas.
- `host`: nome exibido (padrao: hostname).
- `discos`: lista de entradas de dois tipos. `{rotulo, caminho}` mede o ponto de montagem com `statvfs`. `{rotulo, tier_state}` le o JSON do Cerberus (`ssd_used_gib` / `cap_gib`, em GiB; usado para o "NAS SSD", porque o `/srv/nas` e uma uniao mergerfs que soma discos inteiros). Se o arquivo faltar ou os numeros forem invalidos (negativos, tipo errado, `cap_gib` <= 0) a linha mostra `n/d`; se `when` faltar ou tiver mais de 3 h a linha mostra o valor com o aviso `parado`. Cada entrada tem `caminho` ou `tier_state`, nunca os dois.
- `servicos`: unidades systemd checadas com `systemctl is-active` (mostra `ok` ou `FALHA`).
- `balanceador`: JSON do balanceador do Ragnarok (padrao `/var/lib/cerberus/memory-balancer.json`; `null` desliga). `players_by.ragnarok` ausente conta como 0 jogadores; `updated` com mais de 120 s marca o dado como `PARADO`.
- `pares`: lista de `{nome, url}` de outros servidores iguais a este; busca `<url>/metricas.json?pares=0` com timeout de 2 s. Se falhar, a tela mostra `nome: sem resposta`.
- `portas`: lista de `{rotulo, host, porta}` testadas com conexao TCP (timeout de 0,6 s, em paralelo, resultado em cache por ~5 s). `rotulo` tem ate 12 caracteres (letras, digitos, `_`, `.`, `-`), `host` e IP literal ou nome simples e `porta` vai de 1 a 65535; valor invalido faz o servidor recusar a config. Aparece como `portas: [{rotulo, aberto}]` no JSON, como linha `Portas:` no texto e como "pilulas" na imagem (preenchida = aberta, so contorno com X = fechada). Os valores do exemplo (`10.0.0.60`, 6900/6121/5121) sao os padroes do rAthena: ajuste para o seu.
- `intervalo_historico_s`: segundos entre as amostras do historico (padrao `15`; entre 0 e 3600). Uma thread de fundo (daemon) guarda CPU %, RAM % e GPU % das ultimas 60 amostras (15 min no padrao); alimenta o grafico da imagem e o `/historico.json`. So memoria: nada e escrito em disco, e o historico recomeca vazio ao reiniciar.
- `intervalo_cpu_s`: intervalo entre as duas leituras de `/proc/stat` (CPU % fica em cache por ~5 s).

Cada coletor falha isolado: o que der erro aparece como `n/d` na tela e nunca derruba a requisicao. Sem GPU NVIDIA ou sem sensor de temperatura, a linha simplesmente nao aparece.

## Testes
```
cd server && python3 -I -m unittest discover -s tests
```
Os testes usam fixtures e fakes: nao precisam de rede, `nvidia-smi`, `systemctl` nem `/var/lib/cerberus`.

## Imagem (`/tela.png`)
Retrato, faixa de cabecalho preta com o host e a hora, uma linha por metrica (CPU, RAM, GPU, VRAM, SWAP e discos) com numero grande e barra grossa, grafico do historico ao lado de CPU/RAM/GPU (na RAM o `usado / total GB` fica em x=228 e o grafico comeca depois do texto; `/tela.txt` mostra `7.4/19.4G` na linha da RAM e da SWAP, ou logo abaixo se nao couber), GPU "desativada" (util 0 % e memoria usada 0 MiB: uma linha so com `desativada · 39°C`, sem barra nem VRAM; `/tela.txt`: `GPU   desativada 39C`; `metricas.gpu.estado` e `desativada` ou `ativa`), temperaturas/carga/uptime, bloco Ragnarok (jogadores, pilulas LOGIN/CHAR/MAP e aviso `PARADO`), servicos (falhas primeiro) e cartoes compactos dos pares. Campos ausentes nao ocupam espaco; se nao couber, o layout reduz numeros e espacamentos e, no limite, omite itens (`+N servicos`), sem cortar texto nem desenhar fora da imagem. Textos sem acento (a fonte embutida e ASCII mais `°` e `·`).

Em producao so entram `png.py` (encoder PNG com `struct` + `zlib`), `canvas.py` (desenho) e `render_png.py` (layout). As fontes DejaVu vem **pre-rasterizadas** em `fonte_dados.py` (arquivo gerado, ~300 KB; licenca DejaVu/Bitstream Vera no topo do arquivo). Para regerar (ferramenta de desenvolvimento, usa Pillow so via `uv`, nada global):
```
uv run --with pillow python tools/gerar_fonte.py        # reescreve server/fonte_dados.py
```
Para ver o resultado sem subir o servidor: `python3 -I tools/preview.py --saida /tmp/tela.png [--cheia]` (dados de exemplo; `--cheia` usa 8 servicos e 3 discos) ou `--porta 8765` para baixar de um servidor local.
