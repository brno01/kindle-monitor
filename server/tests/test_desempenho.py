import os
import time
import unittest

import _caminho  # noqa: F401
import monitor_server as ms
import coletores
import render_png

ORCAMENTO_S = 0.060  # esta maquina e ~10x mais rapida que o atheron: alvo de <250 ms la.
CONFIG = os.path.join(_caminho.RAIZ, "config.exemplo.json")


def snapshot_completo():
    cfg = ms.carregar_config(CONFIG)
    cfg["pares"] = []
    cfg["portas"] = []

    def leitor(p):
        if p == "/proc/stat":
            leitor.n += 1
            return "cpu  %d 0 50 %d 50 0 0 0 0 0\n" % (100 + 10 * leitor.n, 800 + 30 * leitor.n)
        arq = {"/proc/loadavg": "0.5 0.4 0.3 1/2 3\n", "/proc/uptime": "100.0 50.0\n",
               "/proc/meminfo": "MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 10 kB\nSwapFree: 5 kB\n"}
        if p in arq:
            return arq[p]
        raise OSError(p)
    leitor.n = 0
    c = coletores.Coletor(cfg, leitor_arquivo=leitor, executar=lambda a: (0, "50, 4000, 8000, 60\n"),
                          buscar=lambda u: {}, dormir=lambda s: None, raiz_sys="/nao/existe")
    for _ in range(5):
        c.amostrar()
    return c.atualizar_snapshot().metricas


class OrcamentoTest(unittest.TestCase):
    def test_render_e_encode_da_pagina_completa_cabem_no_orcamento(self):
        m = snapshot_completo()
        for pagina in ("resumo", "servicos", "detalhes", "comandos"):
            melhor = min(self._medir(m, pagina) for _ in range(3))
            self.assertLess(melhor, ORCAMENTO_S, "%s: %.1f ms" % (pagina, melhor * 1e3))

    def _medir(self, m, pagina):
        t = time.perf_counter()
        png = render_png.render_png(m, m.get("historico"), 1236, 1648, pagina, None, 1)
        d = time.perf_counter() - t
        self.assertTrue(png.startswith(b"\x89PNG"))
        return d


if __name__ == "__main__":
    unittest.main()
