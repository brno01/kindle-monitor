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

    def test_maximo_invalido(self):
        with self.assertRaises(ValueError):
            cache_render.CacheLru(0)


if __name__ == "__main__":
    unittest.main()
