"""/botoes.txt (layout for the Kindle's awk) and the comandos page getting the latest commands."""
import json
import threading
import unittest
import urllib.request

import _caminho  # noqa: F401
import botoes
import monitor_server as ms


class _Coletor:
    def coletar(self, com_pares=True):
        return {"host": "teste", "gerado_em": "2026-11-16T00:00:00"}

    def historico(self):
        return {}


class _Comandos:
    def __init__(self):
        self.chamadas = 0

    def ultimos(self, n=5):
        self.chamadas += 1
        return [{"acao": "gpu-descarregar", "estado": "ok", "quando": "00:00:01", "detalhe": "nada"}]

    def processar(self, *a, **k):
        return 405, b"", {}


class BotoesTxtTest(unittest.TestCase):
    def setUp(self):
        self.cmd = _Comandos()
        self.srv = ms.criar_servidor("127.0.0.1", 0, _Coletor(), comandos=self.cmd)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def _get(self, caminho):
        with urllib.request.urlopen("http://127.0.0.1:%d%s" % (self.porta, caminho), timeout=5) as r:
            return r.read()

    def test_txt_igual_ao_json(self):
        for q in ("?pagina=resumo", "?pagina=comandos&armado=gpu-descarregar", "?pagina=xx"):
            txt = self._get("/botoes.txt" + q).decode().split("\n")
            js = json.loads(self._get("/botoes.json" + q))["botoes"]
            linhas = [l for l in txt if l]
            self.assertEqual(len(linhas), len(js))
            for linha, b in zip(linhas, js):
                self.assertEqual(linha.split(), [b["id"], b["tipo"], str(b["x"]), str(b["y"]), str(b["w"]), str(b["h"])])

    def test_ids_sem_espaco(self):
        for p in ("resumo", "detalhes", "comandos"):
            for b in botoes.layout(p, None):
                self.assertNotIn(" ", b["id"])
                self.assertNotIn(" ", b["tipo"])

    def test_pagina_comandos_recebe_ultimos(self):
        self._get("/tela.png?pagina=comandos")
        self.assertEqual(self.cmd.chamadas, 1)
        self._get("/tela.png?pagina=resumo")
        self.assertEqual(self.cmd.chamadas, 1)


if __name__ == "__main__":
    unittest.main()
