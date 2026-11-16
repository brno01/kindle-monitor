import hashlib
import importlib.util
import os
import stat
import tempfile
import unittest

import _caminho  # noqa: F401

_CAM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "deploy", "preparar-token.py")
_spec = importlib.util.spec_from_file_location("preparar_token", _CAM)
pt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pt)


class PrepararTokenTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.d = self._tmp.name
        self.raw = os.path.join(self.d, "token.raw")
        self.sha = os.path.join(self.d, "token.sha256")

    def ler(self, p):
        with open(p) as f:
            return f.read().strip()

    def test_gera_cru_e_hash(self):
        feito = pt.preparar(self.d, os.getgid())
        token = self.ler(self.raw)
        self.assertRegex(token, r"^[0-9a-f]{64}$")
        self.assertEqual(self.ler(self.sha), hashlib.sha256(token.encode()).hexdigest())
        self.assertEqual(stat.S_IMODE(os.stat(self.raw).st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(self.sha).st_mode), 0o640)
        self.assertNotIn(token, "\n".join(feito))  # nunca imprime o token

    def test_nao_regera_se_valido(self):
        pt.preparar(self.d, os.getgid())
        token = self.ler(self.raw)
        os.unlink(self.sha)
        pt.preparar(self.d, os.getgid())
        self.assertEqual(self.ler(self.raw), token)
        self.assertEqual(self.ler(self.sha), hashlib.sha256(token.encode()).hexdigest())

    def test_rotacao_apagando_o_cru(self):
        pt.preparar(self.d, os.getgid())
        antigo = self.ler(self.raw)
        os.unlink(self.raw)
        pt.preparar(self.d, os.getgid())
        self.assertNotEqual(self.ler(self.raw), antigo)

    def test_existente_invalido_erro_sem_sobrescrever(self):
        with open(self.raw, "w") as f:
            f.write("curto\n")
        with self.assertRaises(SystemExit) as c:
            pt.preparar(self.d, os.getgid())
        self.assertIn("64", str(c.exception))
        self.assertEqual(self.ler(self.raw), "curto")
        self.assertFalse(os.path.exists(self.sha))

    def test_migra_token_antigo_valido(self):
        antigo = os.path.join(self.d, "token")
        with open(antigo, "w") as f:
            f.write("cd" * 32 + "\n")
        pt.preparar(self.d, os.getgid())
        self.assertFalse(os.path.exists(antigo))
        self.assertEqual(self.ler(self.raw), "cd" * 32)

    def test_token_antigo_invalido_erro(self):
        with open(os.path.join(self.d, "token"), "w") as f:
            f.write("xx\n")
        with self.assertRaises(SystemExit):
            pt.preparar(self.d, os.getgid())
        self.assertFalse(os.path.exists(self.raw))

    def test_symlink_recusado(self):
        alvo = os.path.join(self.d, "alvo")
        with open(alvo, "w") as f:
            f.write("ab" * 32)
        os.symlink(alvo, self.raw)
        with self.assertRaises(SystemExit):
            pt.preparar(self.d, os.getgid())


if __name__ == "__main__":
    unittest.main()
