import json
import os
import tempfile
import threading
import http.client
import unittest

import _caminho  # noqa: F401
import coletores as c
import formato
import monitor_server as ms
import render

DISKSTATS = (
    "   8       0 sda 100 0 2000 50 200 0 4000 80 0 100 130 0 0 0 0\n"
    "   8       1 sda1 1 0 8 1 1 0 8 1 0 1 2 0 0 0 0\n"
    " 259       0 nvme0n1 500 0 10000 90 600 0 20000 70 0 100 160 0 0 0 0\n"
    "garbage line\n"
)
NETDEV = (
    "Inter-|   Receive                                                |  Transmit\n"
    " face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n"
    "    lo: 1000 10 0 0 0 0 0 0 1000 10 0 0 0 0 0 0\n"
    "enp2s0f1: 5000 50 0 0 0 0 0 0 7000 70 0 0 0 0 0 0\n"
    "tailscale0:  300 3 0 0 0 0 0 0 400 4 0 0 0 0 0 0\n"
)
IO_CFG = {
    "discos": [{"rotulo": "NVMe", "dev": "nvme0n1"}, {"rotulo": "HD", "dev": "sda"}],
    "redes": [{"rotulo": "LAN", "if": "enp2s0f1"}, {"rotulo": "Tailnet", "if": "tailscale0"}],
}


def diskstats(sda_r=2000, sda_w=4000, nv_r=10000, nv_w=20000):
    return (
        "   8       0 sda 100 0 %d 50 200 0 %d 80 0 100 130 0 0 0 0\n"
        " 259       0 nvme0n1 500 0 %d 90 600 0 %d 70 0 100 160 0 0 0 0\n" % (sda_r, sda_w, nv_r, nv_w)
    )


def netdev(lan_rx=5000, lan_tx=7000, ts_rx=300, ts_tx=400):
    return (
        "Inter-|   Receive\n face |bytes packets\n"
        "enp2s0f1: %d 50 0 0 0 0 0 0 %d 70 0 0 0 0 0 0\n"
        "tailscale0: %d 3 0 0 0 0 0 0 %d 4 0 0 0 0 0 0\n" % (lan_rx, lan_tx, ts_rx, ts_tx)
    )


class Cenario:
    """Relogio, sleep e arquivos /proc controlados pelo teste."""

    def __init__(self, io=IO_CFG, intervalo_s=0.3):
        self.t = 1000.0
        self.dormidas = []
        self.arquivos = {"/proc/diskstats": diskstats(), "/proc/net/dev": netdev()}
        self.leituras = 0
        self.ao_dormir = None
        self.am = c.IoAmostrador(self.ler, io, dormir=self.dormir, relogio=lambda: self.t, intervalo_s=intervalo_s)

    def ler(self, caminho):
        self.leituras += 1
        v = self.arquivos[caminho]
        if isinstance(v, Exception):
            raise v
        return v

    def dormir(self, s):
        self.dormidas.append(s)
        self.t += s
        if self.ao_dormir:
            self.ao_dormir()


class ParseTest(unittest.TestCase):
    def test_diskstats_setores_em_bytes(self):
        d = c.parse_diskstats(DISKSTATS)
        self.assertEqual(d["sda"], (2000 * 512, 4000 * 512))
        self.assertEqual(d["nvme0n1"], (10000 * 512, 20000 * 512))
        self.assertIn("sda1", d)
        self.assertNotIn("garbage", d)

    def test_net_dev(self):
        n = c.parse_net_dev(NETDEV)
        self.assertEqual(n["enp2s0f1"], (5000, 7000))
        self.assertEqual(n["tailscale0"], (300, 400))
        self.assertEqual(n["lo"], (1000, 1000))

    def test_net_dev_sem_espaco_apos_dois_pontos(self):
        n = c.parse_net_dev("h1\nh2\neth0:123 1 0 0 0 0 0 0 456 1 0 0 0 0 0 0\n")
        self.assertEqual(n["eth0"], (123, 456))


class IoAmostradorTest(unittest.TestCase):
    def test_primeira_leitura_faz_amostra_dupla(self):
        s = Cenario()

        def mexer():  # between the two reads the counters move
            s.arquivos["/proc/diskstats"] = diskstats(sda_r=2000 + 600, sda_w=4000, nv_r=10000 + 6000, nv_w=20000 + 1200)
            s.arquivos["/proc/net/dev"] = netdev(lan_rx=5000 + 300, lan_tx=7000 + 60, ts_rx=300 + 30, ts_tx=400 + 3)
        s.ao_dormir = mexer
        r = s.am.medir()
        self.assertEqual(s.dormidas, [0.3])
        nv, hd = r["discos"]
        self.assertEqual((nv["rotulo"], nv["dev"]), ("NVMe", "nvme0n1"))
        self.assertAlmostEqual(nv["leitura_bps"], 6000 * 512 / 0.3, delta=1)
        self.assertAlmostEqual(nv["escrita_bps"], 1200 * 512 / 0.3, delta=1)
        self.assertAlmostEqual(hd["leitura_bps"], 600 * 512 / 0.3, delta=1)
        self.assertEqual(hd["escrita_bps"], 0.0)
        lan, ts = r["redes"]
        self.assertEqual((lan["rotulo"], lan["if"]), ("LAN", "enp2s0f1"))
        self.assertAlmostEqual(lan["rx_bps"], 300 / 0.3, delta=0.5)
        self.assertAlmostEqual(lan["tx_bps"], 60 / 0.3, delta=0.5)
        self.assertAlmostEqual(ts["rx_bps"], 100.0, delta=0.5)

    def test_requisicao_seguinte_usa_amostra_anterior_sem_dormir(self):
        s = Cenario()
        s.am.medir()
        self.assertEqual(s.dormidas, [0.3])
        s.t += 2.0
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=5000 + 2000, lan_tx=7000 + 400)
        r = s.am.medir()
        self.assertEqual(s.dormidas, [0.3])  # no new sleep
        lan = r["redes"][0]
        self.assertAlmostEqual(lan["rx_bps"], 1000.0, delta=0.5)
        self.assertAlmostEqual(lan["tx_bps"], 200.0, delta=0.5)

    def test_intervalo_menor_que_0_5s_reutiliza_ultima_taxa(self):
        s = Cenario()
        s.am.medir()
        s.t += 2.0
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=7000)
        a = s.am.medir()
        leituras = s.leituras
        s.t += 0.2
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=9999999)
        b = s.am.medir()
        self.assertEqual(a, b)
        self.assertEqual(s.leituras, leituras)  # did not even read the files

    def test_apos_reuso_a_taxa_usa_a_ultima_amostra_real(self):
        s = Cenario()
        s.am.medir()
        s.t += 2.0
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=7000)  # 1000 B/s
        s.am.medir()
        s.t += 0.2
        s.am.medir()  # reused
        s.t += 1.8  # 2.0 s after the last real sample
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=7000 + 4000)
        r = s.am.medir()
        self.assertAlmostEqual(r["redes"][0]["rx_bps"], 2000.0, delta=0.5)

    def test_amostra_velha_refaz_amostra_dupla(self):
        s = Cenario()
        s.am.medir()
        s.t += 31.0
        s.am.medir()
        self.assertEqual(s.dormidas, [0.3, 0.3])

    def test_amostra_de_30s_exatos_ainda_serve(self):
        s = Cenario()
        s.am.medir()
        s.t += 30.0
        s.am.medir()
        self.assertEqual(s.dormidas, [0.3])

    def test_intervalo_da_amostra_dupla_configuravel(self):
        s = Cenario(intervalo_s=0.1)
        s.am.medir()
        self.assertEqual(s.dormidas, [0.1])

    def test_contador_que_voltou_da_nd_nunca_negativo(self):
        s = Cenario()
        s.am.medir()
        s.t += 2.0
        s.arquivos["/proc/diskstats"] = diskstats(sda_r=10, sda_w=4000 + 200, nv_r=10000 + 1000, nv_w=1)
        s.arquivos["/proc/net/dev"] = netdev(lan_rx=1, lan_tx=7000 + 100)
        r = s.am.medir()
        nv, hd = r["discos"]
        self.assertIsNone(hd["leitura_bps"])  # went backwards
        self.assertAlmostEqual(hd["escrita_bps"], 200 * 512 / 2.0, delta=0.5)
        self.assertAlmostEqual(nv["leitura_bps"], 1000 * 512 / 2.0, delta=0.5)
        self.assertIsNone(nv["escrita_bps"])
        lan = r["redes"][0]
        self.assertIsNone(lan["rx_bps"])
        self.assertAlmostEqual(lan["tx_bps"], 50.0, delta=0.5)

    def test_dispositivo_ausente_omite_a_linha(self):
        s = Cenario()
        s.arquivos["/proc/diskstats"] = "   8 0 sda 1 0 10 1 1 0 10 1 0 1 1 0 0 0 0\n"
        s.arquivos["/proc/net/dev"] = "h\nh\ntailscale0: 1 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0\n"
        r = s.am.medir()
        self.assertEqual([d["dev"] for d in r["discos"]], ["sda"])
        self.assertEqual([n["if"] for n in r["redes"]], ["tailscale0"])

    def test_dispositivo_que_some_entre_amostras_vira_nd(self):
        s = Cenario()
        s.am.medir()
        s.t += 2.0
        s.arquivos["/proc/diskstats"] = "   8 0 sda 1 0 10 1 1 0 10 1 0 1 1 0 0 0 0\n"
        r = s.am.medir()
        self.assertEqual([d["dev"] for d in r["discos"]], ["sda"])

    def test_arquivo_ilegivel_da_nd_sem_levantar(self):
        s = Cenario()
        s.arquivos["/proc/diskstats"] = OSError("sem /proc")
        r = s.am.medir()
        self.assertEqual([d["leitura_bps"] for d in r["discos"]], [None, None])
        self.assertEqual([d["escrita_bps"] for d in r["discos"]], [None, None])
        self.assertIsNotNone(r["redes"][0]["rx_bps"])

    def test_sem_config_nao_le_nada(self):
        s = Cenario(io={"discos": [], "redes": []})
        self.assertEqual(s.am.medir(), {"discos": [], "redes": []})
        self.assertEqual(s.leituras, 0)
        self.assertEqual(s.dormidas, [])


class ValidarIoTest(unittest.TestCase):
    def test_valida(self):
        v = c.validar_io(IO_CFG)
        self.assertEqual(v["discos"][0], {"rotulo": "NVMe", "dev": "nvme0n1"})
        self.assertEqual(v["redes"][1], {"rotulo": "Tailnet", "if": "tailscale0"})

    def test_parcial_e_vazio(self):
        self.assertEqual(c.validar_io({}), {"discos": [], "redes": []})
        self.assertEqual(c.validar_io({"redes": [{"rotulo": "L", "if": "eth0"}]})["discos"], [])

    def test_invalidos(self):
        ruins = [
            "x", [], {"discos": "x"}, {"discos": [1]}, {"discos": [{"rotulo": "a"}]},
            {"discos": [{"rotulo": "a", "dev": ""}]},
            {"discos": [{"rotulo": "a", "dev": "../etc/passwd"}]},
            {"discos": [{"rotulo": "a", "dev": "sd a"}]},
            {"discos": [{"rotulo": "a", "dev": "nvme0n1;rm"}]},
            {"discos": [{"rotulo": "a", "dev": 3}]},
            {"discos": [{"dev": "sda"}]},
            {"discos": [{"rotulo": "", "dev": "sda"}]},
            {"discos": [{"rotulo": "x" * 40, "dev": "sda"}]},
            {"redes": [{"rotulo": "a", "if": "eth/0"}]},
            {"redes": [{"rotulo": "a", "dev": "eth0"}]},
            {"redes": [{"rotulo": "a", "if": "é0"}]},
            {"redes": [{"rotulo": "a", "if": "x" * 80}]},
            {"redes": "x"},
        ]
        for r in ruins:
            with self.assertRaises(ValueError, msg=repr(r)):
                c.validar_io(r)

    def test_config_do_servidor(self):
        def carregar(dados):
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "c.json")
                with open(p, "w") as f:
                    json.dump(dados, f)
                return ms.carregar_config(p)
        self.assertEqual(carregar({"io": IO_CFG})["io"]["discos"][0]["dev"], "nvme0n1")
        with self.assertRaises(ValueError):
            carregar({"io": {"discos": [{"rotulo": "a", "dev": "../x"}]}})
        with self.assertRaises(ValueError):
            carregar({"io": "x"})
        for v in (0, -1, "0.3", True, 99):
            with self.assertRaises(ValueError, msg=repr(v)):
                carregar({"intervalo_io_s": v})

    def test_padroes_novos(self):
        cfg = ms.carregar_config(None)
        self.assertEqual(cfg["io"], {"discos": [], "redes": []})
        self.assertEqual(cfg["cache_cpu_s"], 1.5)
        self.assertEqual(cfg["intervalo_io_s"], 0.3)

    def test_cache_cpu_s_invalido(self):
        for v in (-1, "1", True, 1000):
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "c.json")
                with open(p, "w") as f:
                    json.dump({"cache_cpu_s": v}, f)
                with self.assertRaises(ValueError, msg=repr(v)):
                    ms.carregar_config(p)

    def test_exemplo_e_atheron_tem_io(self):
        exemplo = os.path.join(_caminho.RAIZ, "config.exemplo.json")
        self.assertTrue(ms.carregar_config(exemplo)["io"]["discos"])
        atheron = os.path.join(_caminho.RAIZ, "..", "deploy", "config.atheron.example.json")
        if os.path.exists(atheron):
            cfg = ms.carregar_config(atheron)
            self.assertEqual([d["dev"] for d in cfg["io"]["discos"]], ["nvme0n1", "sda"])
            self.assertEqual([d["if"] for d in cfg["io"]["redes"]], ["enp2s0f1", "tailscale0"])


class FormatoTest(unittest.TestCase):
    def test_taxa_base_1024(self):
        f = formato.taxa
        self.assertEqual(f(0), "0 B/s")
        self.assertEqual(f(512), "512 B/s")
        self.assertEqual(f(1024), "1.0 KB/s")
        self.assertEqual(f(40 * 1024), "40.0 KB/s")
        self.assertEqual(f(12.3 * 1024 ** 2), "12.3 MB/s")
        self.assertEqual(f(1.5 * 1024 ** 3), "1.5 GB/s")
        self.assertEqual(f(1023.99 * 1024), "1.0 MB/s")  # rounds up into the next unit
        self.assertEqual(f(None), "n/d")

    def test_taxa_curta(self):
        f = formato.taxa_curta
        self.assertEqual(f(0), "0B")
        self.assertEqual(f(512), "512B")
        self.assertEqual(f(12.3 * 1024 ** 2), "12.3M")
        self.assertEqual(f(40 * 1024), "40.0K")
        self.assertEqual(f(None), "n/d")

    def test_nunca_negativa(self):
        self.assertEqual(formato.taxa(-5), "n/d")


class IoNoColetorTest(unittest.TestCase):
    def _coletor(self, io=IO_CFG, **cfg):
        arquivos = {
            "/proc/stat": "cpu  100 0 50 800 50 0 0 0 0 0\n",
            "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
            "/proc/meminfo": "MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n",
            "/proc/uptime": "100.0 50.0\n",
            "/proc/diskstats": DISKSTATS,
            "/proc/net/dev": NETDEV,
        }

        def leitor(p):
            if p in arquivos:
                return arquivos[p]
            raise FileNotFoundError(p)

        base = {"host": "teste", "discos": [], "servicos": [], "balanceador": None, "pares": [], "io": io}
        base.update(cfg)
        return c.Coletor(base, leitor_arquivo=leitor,
                         executar=lambda a: (_ for _ in ()).throw(FileNotFoundError(a[0])),
                         buscar=lambda u: {}, dormir=lambda s: None, raiz_sys="/nao/existe")

    def test_metricas_io(self):
        m = self._coletor().coletar()
        self.assertEqual([d["dev"] for d in m["io"]["discos"]], ["nvme0n1", "sda"])
        self.assertEqual([n["if"] for n in m["io"]["redes"]], ["enp2s0f1", "tailscale0"])
        json.dumps(m)  # serializable (None -> null)

    def test_sem_io_na_config_nao_ha_chave(self):
        m = self._coletor(io={"discos": [], "redes": []}).coletar()
        self.assertNotIn("io", m)

    def test_falha_do_io_nao_derruba(self):
        co = self._coletor()
        co._io.medir = lambda: (_ for _ in ()).throw(RuntimeError("x"))
        m = co.coletar()
        self.assertEqual(m["io"], {"erro": "n/d"})
        self.assertIn("cpu", m)


class CpuRapidaTest(unittest.TestCase):
    A = "cpu  100 0 50 800 50 0 0 0 0 0\n"
    B = "cpu  150 0 100 850 100 0 0 0 0 0\n"      # delta total 200, idle 100 -> 50%
    C = "cpu  250 0 100 900 100 0 0 0 0 0\n"      # vs B: total 150, idle 50 -> 66.7%

    def _am(self, textos, **kw):
        it = iter(textos)
        s = {"t": 100.0, "dormidas": []}
        am = c.CpuAmostrador(lambda: next(it), dormir=s["dormidas"].append, relogio=lambda: s["t"],
                             intervalo_s=0.5, **kw)
        return am, s

    def test_requisicoes_seguidas_nao_dormem(self):
        am, s = self._am([self.A, self.B, self.C])
        self.assertEqual(am.medir(), 50.0)
        self.assertEqual(s["dormidas"], [0.5])  # first reading only
        s["t"] = 102.0
        self.assertEqual(am.medir(), 66.7)
        self.assertEqual(s["dormidas"], [0.5])
        s["t"] = 104.0

    def test_cache_padrao_e_1_5s(self):
        am, s = self._am([self.A, self.B, self.C])
        am.medir()
        s["t"] = 101.4
        self.assertEqual(am.medir(), 50.0)  # cached: C is not consumed
        s["t"] = 101.6
        self.assertEqual(am.medir(), 66.7)

    def test_cache_configuravel(self):
        am, s = self._am([self.A, self.B, self.C], cache_s=5.0)
        am.medir()
        s["t"] = 103.0
        self.assertEqual(am.medir(), 50.0)
        s["t"] = 105.5
        self.assertEqual(am.medir(), 66.7)

    def test_intervalo_menor_que_0_5s_reutiliza(self):
        am, s = self._am([self.A, self.B, self.C], cache_s=0.0)
        am.medir()
        s["t"] = 100.2
        self.assertEqual(am.medir(), 50.0)
        self.assertEqual(s["dormidas"], [0.5])

    def test_amostra_velha_dorme_de_novo(self):
        am, s = self._am([self.A, self.B, self.A, self.B])
        am.medir()
        s["t"] = 140.0
        am.medir()
        self.assertEqual(s["dormidas"], [0.5, 0.5])

    def test_coletor_repassa_cache_cpu_s(self):
        co = IoNoColetorTest()._coletor(cache_cpu_s=7.0, intervalo_cpu_s=0.25)
        self.assertEqual(co._cpu._cache_s, 7.0)
        self.assertEqual(co._cpu._intervalo, 0.25)
        self.assertEqual(IoNoColetorTest()._coletor()._cpu._cache_s, 1.5)


# --------------------------------------------------------------- render (texto)

def io_metricas(**extra):
    m = {
        "host": "atheron", "gerado_em": "2026-11-15T14:32:10-03:00",
        "cpu": {"pct": 50.0}, "ram": {"total_kb": 100, "usado_kb": 75, "pct": 75.0},
        "uptime": {"segundos": 90061},
        "io": {
            "discos": [{"rotulo": "NVMe", "dev": "nvme0n1", "leitura_bps": 12.3 * 1024 ** 2, "escrita_bps": 1.2 * 1024 ** 2},
                       {"rotulo": "HD", "dev": "sda", "leitura_bps": 0.0, "escrita_bps": None}],
            "redes": [{"rotulo": "LAN", "if": "enp2s0f1", "rx_bps": 3.4 * 1024 ** 2, "tx_bps": 0.2 * 1024 ** 2},
                      {"rotulo": "Tailnet", "if": "tailscale0", "rx_bps": 40 * 1024, "tx_bps": 12 * 1024}],
        },
    }
    m.update(extra)
    return m


class RenderIoTexto(unittest.TestCase):
    def test_linhas_io_e_net(self):
        linhas = render.render_texto(io_metricas(), 38)
        self.assertIn("IO NVMe r 12.3M w 1.2M", linhas)
        self.assertIn("IO HD r 0B w n/d", linhas)
        self.assertIn("NET LAN rx 3.4M tx 204.8K", linhas)
        self.assertIn("NET Tailnet rx 40.0K tx 12.0K", linhas)

    def test_respeita_colunas(self):
        for cols in (20, 24, 30, 38, 60):
            linhas = render.render_texto(io_metricas(), cols)
            self.assertTrue(all(len(l) <= cols for l in linhas), cols)
            self.assertTrue(any(l.startswith("IO ") for l in linhas), cols)

    def test_io_com_erro_ou_ausente(self):
        for io in ({"erro": "n/d"}, "x", {"discos": "x", "redes": None}):
            linhas = render.render_texto(io_metricas(io=io), 38)
            self.assertTrue(linhas)
        self.assertFalse(any(l.startswith(("IO ", "NET ")) for l in render.render_texto(io_metricas(io=None), 38)))

    def test_rotulo_comprido_nao_estoura(self):
        m = io_metricas()
        m["io"]["discos"][0]["rotulo"] = "R" * 50
        linhas = render.render_texto(m, 38)
        self.assertTrue(all(len(l) <= 38 for l in linhas))
        self.assertTrue(any("w 1.2M" in l for l in linhas))


class ServidorIoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        co = IoNoColetorTest()._coletor()
        cls.srv = ms.criar_servidor("127.0.0.1", 0, co, colunas=38, log=False)
        cls.porta = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def get(self, caminho):
        con = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        try:
            con.request("GET", caminho)
            return con.getresponse().read()
        finally:
            con.close()

    def test_metricas_json_tem_io(self):
        m = json.loads(self.get("/metricas.json"))
        self.assertEqual([d["dev"] for d in m["io"]["discos"]], ["nvme0n1", "sda"])
        self.assertIn("leitura_bps", m["io"]["discos"][0])
        self.assertIn("rx_bps", m["io"]["redes"][0])

    def test_tela_txt_tem_linhas_io(self):
        linhas = self.get("/tela.txt").decode("ascii").splitlines()
        self.assertTrue(any(l.startswith("IO NVMe r ") for l in linhas), linhas)
        self.assertTrue(any(l.startswith("NET LAN rx ") for l in linhas), linhas)
        self.assertTrue(all(len(l) <= 38 for l in linhas))


if __name__ == "__main__":
    unittest.main()
