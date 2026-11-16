"""Cache LRU pequeno e thread-safe para as imagens renderizadas (chave: snapshot, pagina, p, armado, tamanho)."""
import threading
from collections import OrderedDict


class CacheLru:
    def __init__(self, maximo=8):
        if int(maximo) < 1:
            raise ValueError("maximo deve ser >= 1")
        self._max = int(maximo)
        self._d = OrderedDict()
        self._lock = threading.Lock()

    def __len__(self):
        with self._lock:
            return len(self._d)

    def obter(self, chave, fabrica):
        """Valor em cache para `chave` ou `fabrica()` (guardado). `chave` None = nao guarda.

        A fabrica roda fora do lock: duas requisicoes simultaneas podem renderizar a mesma chave
        uma vez a mais, mas nunca se bloqueiam nem ficam presas a uma excecao."""
        if chave is None:
            return fabrica()
        with self._lock:
            if chave in self._d:
                self._d.move_to_end(chave)
                return self._d[chave]
        valor = fabrica()
        with self._lock:
            self._d[chave] = valor
            self._d.move_to_end(chave)
            while len(self._d) > self._max:
                self._d.popitem(last=False)
        return valor
