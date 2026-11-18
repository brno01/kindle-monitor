"""Estado do proprio Kindle (bateria, Wi-Fi, Bluetooth, modo aviao, elo com o atheron, Whispersync).

O loop.sh do Kindle coleta com `lipc-get-prop` a cada KSTATUS_EVERY segundos e manda os valores como parametros
`k*` na query de /tela.png (so inteiros e enums: nada de SSID, MAC ou nome de aparelho). O servidor guarda o
ultimo estado recebido (um Kindle so) e desenha a partir dele, entao pedidos sem `k*` (o nomad, a previa)
mostram o estado real do Kindle.

`vista(agora)` devolve so o que e desenhado, ja arredondado: e a chave do cache de imagens, entao tem de ficar
igual entre pedidos seguidos com os mesmos dados (latencia amostrada a cada coleta, idades em degraus).
"""
import threading
from collections import deque
from urllib.parse import parse_qs

VELHO_S = 300            # sem noticia do Kindle ha mais que isto: "Kindle sem dados"
AUTONOMIA_JANELA_S = 1200  # minimo de descarga observada para estimar a autonomia
AUTONOMIA_MAX_S = 3 * 3600
BATERIA_BAIXA = 15       # % (sem carregar) que vira item em ATENCAO
DERIVA_OK_S = 2

# chave -> (minimo, maximo) para inteiros; "kts" e enum
_INTEIROS = {
    "kb": (0, 100),          # bateria %
    "kc": (0, 1),            # carregando
    "ktemp": (-40, 200),     # temperatura da bateria em graus F (como o powerd informa)
    "kw": (0, 5),            # sinal do Wi-Fi (barras)
    "kwc": (0, 1),           # Wi-Fi conectado
    "ka": (0, 1),            # modo aviao ligado (wirelessEnable == 0)
    "kbt": (0, 1),           # Bluetooth ligado
    "kbc": (0, 9),           # aparelhos Bluetooth conectados
    "klat": (0, 60000),      # ms da ultima busca do PNG (amostrada na coleta)
    "kf": (0, 99999),        # falhas seguidas da busca
    "kt": (10 ** 9, 5 * 10 ** 9),   # relogio do Kindle (epoch s)
    "kws": (10 ** 9, 5 * 10 ** 9),  # ultimo Whispersync conhecido (epoch s)
}
_TAILSCALE = {"d": "direto", "r": "relay", "x": None}
CHAVES = tuple(_INTEIROS) + ("kts",)


def _inteiro(valor, lo, hi):
    if not isinstance(valor, str) or not valor or len(valor) > 12:
        return None
    s = valor[1:] if valor[0] == "-" else valor
    if not s.isascii() or not s.isdigit():
        return None
    n = int(valor)
    return n if lo <= n <= hi else None


def de_query(query):
    """{chave: valor} so com os campos `k*` validos da query string; {} se nao ha nenhum. Nunca levanta."""
    try:
        q = parse_qs(query or "", keep_blank_values=True, errors="replace")
    except Exception:
        return {}
    out = {}
    for k, (lo, hi) in _INTEIROS.items():
        v = _inteiro(q.get(k, [""])[0], lo, hi)
        if v is not None:
            out[k] = v
    ts = q.get("kts", [""])[0]
    if ts in _TAILSCALE:
        out["kts"] = ts
    return out


def _idade(seg):
    """Idade em degraus que mudam devagar (o texto entra na chave do cache)."""
    seg = max(0, int(seg))
    if seg < 60:
        return "agora"
    if seg < 3600:
        return "ha %d min" % (seg // 60)
    if seg < 48 * 3600:
        return "ha %d h" % (seg // 3600)
    return "ha %d dias" % (seg // 86400)


def _duracao(horas):
    if horas < 1:
        return "~%d min" % max(1, int(round(horas * 60 / 10.0)) * 10)
    return "~%d h" % int(round(horas))


class EstadoKindle:
    """Ultimo estado do Kindle, thread-safe. `relogio` (epoch s) e injetavel nos testes."""

    def __init__(self, relogio=None):
        import time
        self._relogio = relogio or time.time
        self._lock = threading.Lock()
        self._dados = {}
        self._quando = None
        self._deriva = None
        self._amostras = deque()  # (t, %) enquanto descarrega

    def atualizar(self, campos, agora=None):
        """Guarda os campos validos (de `de_query`). Sem campos nao muda nada (pedido do nomad, previa)."""
        if not campos:
            return False
        agora = self._relogio() if agora is None else agora
        with self._lock:
            # cada pedido do Kindle traz o conjunto inteiro: campo ausente = Kindle nao conseguiu ler
            self._dados = dict(campos)
            self._quando = agora
            if "kt" in campos:
                self._deriva = campos["kt"] - agora
            kb, kc = campos.get("kb"), campos.get("kc")
            if kc == 1 or kb is None:
                self._amostras.clear()
            elif not self._amostras or self._amostras[-1][1] != kb:
                if self._amostras and kb > self._amostras[-1][1]:
                    self._amostras.clear()  # subiu sem "carregando": recomeca a medida
                self._amostras.append((agora, kb))
                while self._amostras and agora - self._amostras[0][0] > AUTONOMIA_MAX_S:
                    self._amostras.popleft()
        return True

    def _autonomia(self):
        if len(self._amostras) < 2:
            return None
        (t0, p0), (t1, p1) = self._amostras[0], self._amostras[-1]
        if t1 - t0 < AUTONOMIA_JANELA_S or p0 <= p1:
            return None
        por_hora = (p0 - p1) * 3600.0 / (t1 - t0)
        return _duracao(p1 / por_hora)

    def vista(self, agora=None):
        """Dict so com o que e desenhado (texto e numeros pequenos), ou None se nao ha estado recente."""
        agora = self._relogio() if agora is None else agora
        with self._lock:
            if self._quando is None or agora - self._quando > VELHO_S:
                return None
            d = dict(self._dados)
            deriva = self._deriva
            autonomia = self._autonomia()
        v = {
            "bateria": d.get("kb"),
            "carregando": d.get("kc") == 1,
            "temp_c": None if d.get("ktemp") is None else int(round((d["ktemp"] - 32) * 5 / 9.0)),
            "autonomia": autonomia if d.get("kc") != 1 else None,
            "wifi": d.get("kw"),
            "wifi_ok": d.get("kwc") == 1,
            "aviao": None if d.get("ka") is None else d["ka"] == 1,
            "bt": None if d.get("kbt") is None else d["kbt"] == 1,
            "bt_conectados": d.get("kbc") or 0,
            "tailscale": _TAILSCALE.get(d.get("kts")),
            "latencia": None if d.get("klat") is None else "%d ms" % d["klat"],
            "falhas": d.get("kf") or 0,
            "relogio": None,
            "whispersync": None if d.get("kws") is None else _idade(agora - d["kws"]),
        }
        if deriva is not None:
            r = int(round(deriva))
            v["relogio"] = "ok" if abs(r) <= DERIVA_OK_S else "%+d s" % r
        return v


def chave(vista):
    """Tupla estavel (ordenada) da vista, para a chave do cache; None vira ()."""
    return tuple(sorted(vista.items())) if vista else ()


def bateria_baixa(vista):
    return bool(vista) and vista.get("bateria") is not None and not vista.get("carregando") \
        and vista["bateria"] <= BATERIA_BAIXA
