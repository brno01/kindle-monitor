"""Cache LRU pequeno e thread-safe para as imagens renderizadas (chave: snapshot, pagina, p, armado, tamanho)."""
import threading
from collections import OrderedDict


class CacheLru:
    def __init__(self, maximo=8):
        if int(maximo) < 1:
            raise ValueError("maximo deve ser >= 1")
        self._max = int(maximo)
        self._d = OrderedDict()
        self._voando = {}  # chave -> Event da geracao em andamento
        self._lock = threading.Lock()

    def __len__(self):
        with self._lock:
            return len(self._d)

    def obter(self, chave, fabrica):
        """Valor em cache para `chave` ou `fabrica()` (guardado). `chave` None = nao guarda.

        Single-flight por chave: se outra thread ja esta gerando a mesma chave, espera por ela
        em vez de renderizar de novo (se ela falhar, tenta a fabrica propria). Chaves diferentes
        nao se bloqueiam: a fabrica roda fora do lock."""
        if chave is None:
            return fabrica()
        while True:
            with self._lock:
                if chave in self._d:
                    self._d.move_to_end(chave)
                    return self._d[chave]
                espera = self._voando.get(chave)
                if espera is None:
                    self._voando[chave] = espera = threading.Event()
                    dono = True
                else:
                    dono = False
            if not dono:
                espera.wait()
                continue
            try:
                valor = fabrica()
                with self._lock:
                    self._d[chave] = valor
                    self._d.move_to_end(chave)
                    while len(self._d) > self._max:
                        self._d.popitem(last=False)
                return valor
            finally:
                with self._lock:
                    self._voando.pop(chave, None)
                espera.set()
