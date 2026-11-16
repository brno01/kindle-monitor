import threading
import time
import unittest

import _caminho  # noqa: F401
import coletores


class Relogio:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def fabrica(gpu_saidas=None, falhar=None, chamadas=None):
    """Coletor com leitor de /proc controlavel. `falhar` e um set de caminhos que levantam."""
    falhar = falhar if falhar is not None else set()
    chamadas = chamadas if chamadas is not None else {"gpu": 0}
    estado = {"cpu": [100, 0, 50, 800, 50]}
    relogio = Relogio()

    def leitor(p):
        if p in falhar:
            raise OSError(p)
        if p == "/proc/stat":
            estado["cpu"][0] += 10
            estado["cpu"][3] += 30
            return "cpu  %d 0 %d %d %d 0 0 0 0 0\n" % tuple(estado["cpu"][:1] + [estado["cpu"][2]] + estado["cpu"][3:])
        return {
            "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
            "/proc/meminfo": "MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n",
            "/proc/uptime": "100.0 50.0\n",
        }[p]

    def executar(a):
        chamadas["gpu"] += 1
        return 0, "10, 100, 1000, 40\n"

    cfg = {"host": "t", "discos": [], "servicos": [], "balanceador": None, "pares": [],
           "intervalo_coleta_s": 0.01, "intervalo_lento_s": 5.0}
    c = coletores.Coletor(cfg, leitor_arquivo=leitor, executar=executar, buscar=lambda u: {},
                          dormir=lambda s: None, raiz_sys="/nao/existe", relogio=relogio,
                          agora=lambda: relogio.t)
    return c, relogio, falhar, chamadas


class SnapshotSincronoTest(unittest.TestCase):
    def test_sem_snapshot_obter_cai_no_coletar(self):
        c, *_ = fabrica()
        self.assertIsNone(c.snapshot())
        sid, m = c.obter_metricas()
        self.assertIsNone(sid)
        self.assertIn("cpu", m)

    def test_atualizar_cria_snapshot_com_id_crescente(self):
        c, *_ = fabrica()
        s1 = c.atualizar_snapshot()
        s2 = c.atualizar_snapshot()
        self.assertEqual(s2.id, s1.id + 1)
        self.assertIs(c.snapshot(), s2)

    def test_obter_usa_o_ultimo_snapshot_sem_coletar(self):
        c, rel, _, chamadas = fabrica()
        c.atualizar_snapshot()
        antes = chamadas["gpu"]
        for _ in range(5):
            sid, m = c.obter_metricas()
        self.assertEqual(chamadas["gpu"], antes)
        self.assertEqual(sid, c.snapshot().id)

    def test_copia_rasa_nao_altera_o_snapshot(self):
        c, *_ = fabrica()
        c.atualizar_snapshot()
        _, m = c.obter_metricas()
        m["comandos"] = ["x"]
        m["host"] = "outro"
        _, m2 = c.obter_metricas()
        self.assertNotIn("comandos", m2)
        self.assertEqual(m2["host"], "t")

    def test_pares_zero_omite_pares(self):
        c, *_ = fabrica()
        c.config["pares"] = [{"nome": "x", "url": "http://x"}]
        c.atualizar_snapshot()
        self.assertIn("pares", c.obter_metricas(com_pares=True)[1])
        self.assertNotIn("pares", c.obter_metricas(com_pares=False)[1])

    def test_coletor_lento_roda_em_cadencia_propria(self):
        c, rel, _, chamadas = fabrica()
        c.atualizar_snapshot()
        self.assertEqual(chamadas["gpu"], 1)
        rel.t += 1
        c.atualizar_snapshot()
        c.atualizar_snapshot()
        self.assertEqual(chamadas["gpu"], 1)  # 5 s ainda nao passaram
        rel.t += 5
        c.atualizar_snapshot()
        self.assertEqual(chamadas["gpu"], 2)

    def test_falha_de_um_coletor_mantem_o_valor_anterior(self):
        c, rel, falhar, _ = fabrica()
        s1 = c.atualizar_snapshot()
        ram_antes = s1.metricas["ram"]
        self.assertNotIn("erro", ram_antes)
        falhar.add("/proc/meminfo")
        rel.t += 1
        s2 = c.atualizar_snapshot()
        self.assertEqual(s2.metricas["ram"], ram_antes)
        self.assertEqual(s2.metricas["swap"], s1.metricas["swap"])
        self.assertIn("cpu", s2.metricas)

    def test_falha_sem_valor_anterior_continua_n_d(self):
        c, _, falhar, _ = fabrica()
        falhar.add("/proc/meminfo")
        s = c.atualizar_snapshot()
        self.assertIn("erro", s.metricas["ram"])

    def test_excecao_inteira_mantem_snapshot_anterior(self):
        c, _, _, _ = fabrica()
        s1 = c.atualizar_snapshot()
        original = c.coletar

        def boom(*a, **k):
            raise RuntimeError("x")
        c.coletar = boom
        self.assertIs(c.atualizar_snapshot(), s1)
        c.coletar = original

    def test_cpu_muda_a_cada_snapshot_apesar_do_cache(self):
        c, rel, _, _ = fabrica()
        c._cpu._cache_s = 10.0  # cache longo nao pode congelar o snapshot
        c.atualizar_snapshot()
        rel.t += 1
        s = c.atualizar_snapshot()
        rel.t += 1
        s2 = c.atualizar_snapshot()
        self.assertIsNotNone(s.metricas["cpu"]["pct"])
        self.assertIsNot(s.metricas["cpu"], s2.metricas["cpu"])


class SnapshotThreadTest(unittest.TestCase):
    def esperar(self, cond, limite=3.0):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            if cond():
                return True
            time.sleep(0.005)
        return False

    def test_start_atualiza_e_stop_encerra(self):
        c, *_ = fabrica()
        c.iniciar_coleta()
        try:
            self.assertTrue(self.esperar(lambda: c.snapshot() is not None and c.snapshot().id >= 3))
        finally:
            c.parar()
        id_final = c.snapshot().id
        time.sleep(0.05)
        self.assertEqual(c.snapshot().id, id_final)  # parou
        self.assertFalse([t for t in threading.enumerate() if t.name == "coleta"])

    def test_iniciar_e_idempotente(self):
        c, *_ = fabrica()
        c.iniciar_coleta()
        c.iniciar_coleta()
        try:
            self.assertEqual(len([t for t in threading.enumerate() if t.name == "coleta"]), 1)
        finally:
            c.parar()

    def test_thread_e_daemon(self):
        c, *_ = fabrica()
        c.iniciar_coleta()
        try:
            t = [t for t in threading.enumerate() if t.name == "coleta"][0]
            self.assertTrue(t.daemon)
        finally:
            c.parar()

    def test_requisicao_nao_espera_coletor_lento(self):
        c, *_ = fabrica()
        c.atualizar_snapshot()
        liberar = threading.Event()
        original = c.coletar

        def lento(*a, **k):
            liberar.wait(5)
            return original(*a, **k)
        c.coletar = lento
        c.iniciar_coleta()
        try:
            time.sleep(0.05)
            t = time.perf_counter()
            c.obter_metricas()
            self.assertLess(time.perf_counter() - t, 0.05)
        finally:
            liberar.set()
            c.parar()

    def test_thread_sobrevive_a_excecao(self):
        c, *_ = fabrica()
        n = {"i": 0}
        original = c.coletar

        def instavel(*a, **k):
            n["i"] += 1
            if n["i"] == 1:
                raise RuntimeError("x")
            return original(*a, **k)
        c.coletar = instavel
        c.iniciar_coleta()
        try:
            self.assertTrue(self.esperar(lambda: c.snapshot() is not None))
        finally:
            c.parar()


if __name__ == "__main__":
    unittest.main()
