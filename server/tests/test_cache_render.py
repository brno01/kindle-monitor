import threading
import unittest

import _caminho  # noqa: F401
import cache_render


class CacheLruTest(unittest.TestCase):
    def test_hit_nao_chama_a_fabrica(self):
        c = cache_render.CacheLru(3)
        n = []
        self.assertEqual(c.obter("a", lambda: n.append(1) or b"A"), b"A")
        self.assertEqual(c.obter("a", lambda: n.append(1) or b"X"), b"A")
        self.assertEqual(len(n), 1)

    def test_lru_descarta_o_menos_recente(self):
        c = cache_render.CacheLru(2)
        c.obter("a", lambda: 1)
        c.obter("b", lambda: 2)
        c.obter("a", lambda: 99)  # a fica recente
        c.obter("c", lambda: 3)   # descarta b
        self.assertEqual(len(c), 2)
        self.assertEqual(c.obter("a", lambda: -1), 1)
        self.assertEqual(c.obter("b", lambda: 20), 20)

    def test_chave_none_nao_guarda(self):
        c = cache_render.CacheLru(2)
        n = []
        c.obter(None, lambda: n.append(1) or 1)
        c.obter(None, lambda: n.append(1) or 1)
        self.assertEqual(len(n), 2)
        self.assertEqual(len(c), 0)

    def test_excecao_da_fabrica_nao_envenena(self):
        c = cache_render.CacheLru(2)
        with self.assertRaises(ValueError):
            c.obter("a", lambda: (_ for _ in ()).throw(ValueError()))
        self.assertEqual(c.obter("a", lambda: 5), 5)

    def test_threads(self):
        c = cache_render.CacheLru(4)
        erros = []

        def uso(i):
            try:
                for k in range(200):
                    self.assertEqual(c.obter(k % 7, lambda k=k: k % 7), k % 7)
            except Exception as e:  # pragma: no cover
                erros.append(e)
        ts = [threading.Thread(target=uso, args=(i,)) for i in range(4)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(erros, [])
        self.assertLessEqual(len(c), 4)

    def test_single_flight_mesma_chave_renderiza_uma_vez(self):
        c = cache_render.CacheLru(4)
        entrou = threading.Event()
        liberar = threading.Event()
        n = []

        def lenta():
            n.append(1)
            entrou.set()
            liberar.wait(5)
            return b"IMG"
        res = []
        t1 = threading.Thread(target=lambda: res.append(c.obter("k", lenta)))
        t1.start()
        self.assertTrue(entrou.wait(5))
        t2 = threading.Thread(target=lambda: res.append(c.obter("k", lambda: n.append(1) or b"OUTRA")))
        t2.start()
        t2.join(0.1)
        self.assertTrue(t2.is_alive())  # esperando a primeira, nao renderizando em paralelo
        liberar.set()
        t1.join(5)
        t2.join(5)
        self.assertEqual(res, [b"IMG", b"IMG"])
        self.assertEqual(len(n), 1)

    def test_chaves_diferentes_nao_se_bloqueiam(self):
        c = cache_render.CacheLru(4)
        liberar = threading.Event()
        entrou = threading.Event()
        t1 = threading.Thread(target=lambda: c.obter("a", lambda: (entrou.set(), liberar.wait(5))[1]))
        t1.start()
        self.assertTrue(entrou.wait(5))
        self.assertEqual(c.obter("b", lambda: 2), 2)
        liberar.set()
        t1.join(5)

    def test_falha_na_primeira_deixa_a_espera_tentar(self):
        c = cache_render.CacheLru(4)
        entrou = threading.Event()
        liberar = threading.Event()

        def falha():
            entrou.set()
            liberar.wait(5)
            raise ValueError("x")

        def primeira():
            with self.assertRaises(ValueError):
                c.obter("k", falha)
        t1 = threading.Thread(target=primeira)
        t1.start()
        self.assertTrue(entrou.wait(5))
        res = []
        t2 = threading.Thread(target=lambda: res.append(c.obter("k", lambda: 7)))
        t2.start()
        liberar.set()
        t1.join(5)
        t2.join(5)
        self.assertEqual(res, [7])

    def test_maximo_invalido(self):
        with self.assertRaises(ValueError):
            cache_render.CacheLru(0)


if __name__ == "__main__":
    unittest.main()
