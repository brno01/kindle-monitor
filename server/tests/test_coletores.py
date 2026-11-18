import json
import os
import tempfile
import unittest
from types import SimpleNamespace

import _caminho  # noqa: F401
import coletores as c

STAT_A = "cpu  100 0 50 800 50 0 0 0 0 0\ncpu0 50 0 25 400 25 0 0 0 0 0\nintr 1\n"
STAT_B = "cpu  150 0 100 850 100 0 0 0 0 0\ncpu0 1 1 1 1 1 0 0 0 0 0\n"

MEMINFO = (
    "MemTotal:       16000000 kB\n"
    "MemFree:         2000000 kB\n"
    "MemAvailable:    4000000 kB\n"
    "Buffers:          100000 kB\n"
    "SwapTotal:       2000000 kB\n"
    "SwapFree:        1500000 kB\n"
)


class CpuTest(unittest.TestCase):
    def test_parse_stat(self):
        self.assertEqual(c.parse_cpu_stat(STAT_A), (1000, 850))

    def test_parse_stat_invalido(self):
        with self.assertRaises(ValueError):
            c.parse_cpu_stat("lixo\n")

    def test_calculo(self):
        # delta total 200, delta ocioso 100 -> 50%
        self.assertEqual(c.calcular_cpu(c.parse_cpu_stat(STAT_A), c.parse_cpu_stat(STAT_B)), 50.0)

    def test_contadores_iguais_da_zero(self):
        a = c.parse_cpu_stat(STAT_A)
        self.assertEqual(c.calcular_cpu(a, a), 0.0)

    def test_amostrador_cacheia_e_nao_dorme_depois_da_primeira(self):
        c3 = "cpu  200 0 150 900 150 0 0 0 0 0\n"  # vs STAT_B: total 200, idle 100 -> 50%
        leituras = iter([STAT_A, STAT_B, c3])
        relogio = [100.0]
        dormidas = []
        am = c.CpuAmostrador(
            leitor=lambda: next(leituras),
            dormir=dormidas.append,
            relogio=lambda: relogio[0],
            intervalo_s=0.5,
            cache_s=5.0,
        )
        self.assertEqual(am.medir(), 50.0)
        self.assertEqual(dormidas, [0.5])
        relogio[0] = 103.0
        self.assertEqual(am.medir(), 50.0)  # do cache: nao consome leituras
        relogio[0] = 106.0
        self.assertEqual(am.medir(), 50.0)  # recalculou com a amostra anterior, sem dormir
        self.assertEqual(dormidas, [0.5])


class ProcTest(unittest.TestCase):
    def test_loadavg(self):
        self.assertEqual(c.parse_loadavg("0.52 0.48 0.40 1/200 1234\n"), {"1m": 0.52, "5m": 0.48, "15m": 0.40})

    def test_meminfo(self):
        r = c.parse_meminfo(MEMINFO)
        self.assertEqual(r["ram"]["total_kb"], 16000000)
        self.assertEqual(r["ram"]["usado_kb"], 12000000)
        self.assertEqual(r["ram"]["pct"], 75.0)
        self.assertEqual(r["swap"]["usado_kb"], 500000)
        self.assertEqual(r["swap"]["pct"], 25.0)

    def test_meminfo_sem_swap(self):
        r = c.parse_meminfo("MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n")
        self.assertEqual(r["swap"]["total_kb"], 0)
        self.assertEqual(r["swap"]["pct"], 0.0)

    def test_meminfo_incompleto(self):
        with self.assertRaises(ValueError):
            c.parse_meminfo("MemTotal: 100 kB\n")

    def test_uptime(self):
        self.assertEqual(c.parse_uptime("12345.67 9999.00\n"), {"segundos": 12345})


class TemperaturaTest(unittest.TestCase):
    def _escrever(self, raiz, rel, texto):
        caminho = os.path.join(raiz, rel)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w") as f:
            f.write(texto)

    def test_thermal_prefere_pkg(self):
        with tempfile.TemporaryDirectory() as d:
            self._escrever(d, "class/thermal/thermal_zone0/type", "acpitz\n")
            self._escrever(d, "class/thermal/thermal_zone0/temp", "27000\n")
            self._escrever(d, "class/thermal/thermal_zone1/type", "x86_pkg_temp\n")
            self._escrever(d, "class/thermal/thermal_zone1/temp", "55000\n")
            self.assertEqual(c.coletar_temperatura(d), {"c": 55.0})

    def test_hwmon(self):
        with tempfile.TemporaryDirectory() as d:
            self._escrever(d, "class/hwmon/hwmon3/name", "k10temp\n")
            self._escrever(d, "class/hwmon/hwmon3/temp1_input", "61500\n")
            self.assertEqual(c.coletar_temperatura(d), {"c": 61.5})

    def test_ausente_retorna_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(c.coletar_temperatura(d))
        self.assertIsNone(c.coletar_temperatura("/caminho/que/nao/existe"))


class GpuTest(unittest.TestCase):
    def test_ok(self):
        r = c.coletar_gpu(lambda args: (0, "12, 300, 2048, 45\n"))
        self.assertEqual(r, {"util_pct": 12, "mem_usada_mb": 300, "mem_total_mb": 2048, "temp_c": 45,
                                 "estado": "ativa"})

    def test_comando_correto(self):
        vistos = []
        c.coletar_gpu(lambda args: vistos.append(args) or (0, "1, 1, 1, 1"))
        self.assertEqual(
            vistos[0],
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
        )

    def test_na_vira_none(self):
        r = c.coletar_gpu(lambda args: (0, "7, [N/A], [N/A], 40"))
        self.assertEqual(r["util_pct"], 7)
        self.assertIsNone(r["mem_usada_mb"])

    def test_nvidia_smi_ausente(self):
        def falha(args):
            raise FileNotFoundError("nvidia-smi")
        self.assertIsNone(c.coletar_gpu(falha))

    def test_driver_com_erro_e_ignorado(self):
        self.assertIsNone(c.coletar_gpu(lambda args: (9, "NVIDIA-SMI has failed")))

    def test_saida_lixo_levanta(self):
        with self.assertRaises(ValueError):
            c.coletar_gpu(lambda args: (0, "lixo"))


class DiscoTest(unittest.TestCase):
    def test_statvfs(self):
        fake = SimpleNamespace(f_frsize=4096, f_blocks=1000, f_bfree=400, f_bavail=300)
        r = c.coletar_disco("NAS", "/mnt/nas", statvfs=lambda p: fake)
        self.assertEqual(r["rotulo"], "NAS")
        self.assertEqual(r["total_b"], 1000 * 4096)
        self.assertEqual(r["usado_b"], 600 * 4096)
        self.assertEqual(r["pct"], round(600 * 100 / 900, 1))

    def test_caminho_inexistente_levanta(self):
        with self.assertRaises(OSError):
            c.coletar_disco("x", "/caminho/que/nao/existe/xyz")


class ServicosTest(unittest.TestCase):
    def test_ativo_e_inativo(self):
        def exe(args):
            self.assertEqual(args[:2], ["systemctl", "is-active"])
            return (0, "active\n") if args[-1] == "a.service" else (3, "inactive\n")
        r = c.coletar_servicos(["a.service", "b.service"], exe)
        self.assertEqual(r, [{"nome": "a.service", "ativo": True}, {"nome": "b.service", "ativo": False}])

    def test_systemctl_ausente_vira_erro_por_item(self):
        def exe(args):
            raise FileNotFoundError("systemctl")
        r = c.coletar_servicos(["a"], exe)
        self.assertEqual(r, [{"nome": "a", "erro": "n/d"}])

    def test_nome_suspeito_rejeitado(self):
        chamadas = []
        r = c.coletar_servicos(["--now", "ok; rm"], lambda a: chamadas.append(a) or (0, "active"))
        self.assertEqual(chamadas, [])
        self.assertEqual([x["erro"] for x in r], ["n/d", "n/d"])


class RagnarokTest(unittest.TestCase):
    AGORA = 1_000_000.0

    def test_com_jogadores(self):
        t = json.dumps({"players_by": {"ragnarok": 3}, "updated": self.AGORA - 10})
        self.assertEqual(
            c.parse_ragnarok(t, self.AGORA), {"jogadores": 3, "parado": False, "idade_s": 10}
        )

    def test_chave_ausente_e_zero(self):
        t = json.dumps({"players_by": {}, "updated": self.AGORA - 5})
        self.assertEqual(c.parse_ragnarok(t, self.AGORA)["jogadores"], 0)

    def test_sem_players_by_e_zero(self):
        t = json.dumps({"updated": self.AGORA - 5})
        self.assertEqual(c.parse_ragnarok(t, self.AGORA)["jogadores"], 0)

    def test_updated_antigo_e_parado(self):
        t = json.dumps({"players_by": {"ragnarok": 2}, "updated": self.AGORA - 121})
        r = c.parse_ragnarok(t, self.AGORA)
        self.assertTrue(r["parado"])
        self.assertEqual(r["idade_s"], 121)

    def test_json_invalido_levanta(self):
        with self.assertRaises(ValueError):
            c.parse_ragnarok("{nao json", self.AGORA)


class ParesTest(unittest.TestCase):
    def test_par_ok_e_fora_do_ar(self):
        def buscar(url):
            if "nomad" in url:
                raise OSError("timeout")
            return {"host": "x", "cpu": {"pct": 1.0}}
        r = c.coletar_pares(
            [{"nome": "nomad", "url": "http://nomad:8765"}, {"nome": "outro", "url": "http://outro:8765"}],
            buscar,
        )
        self.assertEqual(r[0], {"nome": "nomad", "ok": False})
        self.assertTrue(r[1]["ok"])
        self.assertEqual(r[1]["metricas"]["host"], "x")

    def test_url_do_par_pede_sem_pares(self):
        vistos = []
        c.coletar_pares([{"nome": "n", "url": "http://n:8765"}], lambda u: vistos.append(u) or {})
        self.assertEqual(vistos, ["http://n:8765/metricas.json?pares=0"])

    def test_esquema_invalido_e_fora_do_ar(self):
        r = c.coletar_pares([{"nome": "n", "url": "file:///etc/passwd"}], lambda u: {"a": 1})
        self.assertEqual(r, [{"nome": "n", "ok": False}])

    def test_buscar_json_rejeita_nao_objeto(self):
        with self.assertRaises(ValueError):
            c.interpretar_resposta_par(b"[1,2]")


class ColetorTest(unittest.TestCase):
    def _coletor(self, config=None, **kw):
        arquivos = {
            "/proc/stat": STAT_A,
            "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
            "/proc/meminfo": MEMINFO,
            "/proc/uptime": "100.0 50.0\n",
        }

        def leitor(caminho):
            if caminho in arquivos:
                return arquivos[caminho]
            raise FileNotFoundError(caminho)

        base = {"host": "teste", "discos": [], "servicos": [], "balanceador": None, "pares": []}
        base.update(config or {})
        padrao = dict(
            leitor_arquivo=leitor,
            executar=lambda a: (_ for _ in ()).throw(FileNotFoundError(a[0])),
            buscar=lambda u: {},
            dormir=lambda s: None,
            raiz_sys="/caminho/que/nao/existe",
        )
        padrao.update(kw)
        return c.Coletor(base, **padrao)

    def test_coleta_basica(self):
        m = self._coletor().coletar()
        self.assertEqual(m["host"], "teste")
        self.assertIn("gerado_em", m)
        self.assertEqual(m["ram"]["pct"], 75.0)
        self.assertEqual(m["uptime"], {"segundos": 100})
        self.assertNotIn("gpu", m)
        self.assertNotIn("temp_cpu", m)
        self.assertNotIn("ragnarok", m)

    def test_coletor_que_falha_vira_nd_sem_derrubar(self):
        co = self._coletor(leitor_arquivo=lambda p: (_ for _ in ()).throw(PermissionError(p)))
        m = co.coletar()
        self.assertEqual(m["ram"], {"erro": "n/d"})
        self.assertEqual(m["cpu"], {"erro": "n/d"})
        self.assertEqual(m["carga"], {"erro": "n/d"})

    def test_balanceador_ausente_vira_nd(self):
        m = self._coletor({"balanceador": "/var/lib/cerberus/x.json"}).coletar()
        self.assertEqual(m["ragnarok"], {"erro": "n/d"})

    def test_com_pares_false_nao_busca(self):
        chamadas = []
        co = self._coletor({"pares": [{"nome": "n", "url": "http://n:1"}]}, buscar=lambda u: chamadas.append(u) or {})
        m = co.coletar(com_pares=False)
        self.assertEqual(chamadas, [])
        self.assertNotIn("pares", m)

    def test_par_fora_do_ar_nao_derruba(self):
        def buscar(u):
            raise OSError("fora")
        m = self._coletor({"pares": [{"nome": "nomad", "url": "http://n:1"}]}, buscar=buscar).coletar()
        self.assertEqual(m["pares"], [{"nome": "nomad", "ok": False}])

    def test_pares_em_cache(self):
        chamadas = []
        relogio = [10.0]
        co = self._coletor(
            {"pares": [{"nome": "n", "url": "http://n:1"}]},
            buscar=lambda u: chamadas.append(u) or {},
            relogio=lambda: relogio[0],
        )
        co.coletar()
        co.coletar()
        self.assertEqual(len(chamadas), 1)
        relogio[0] = 20.0
        co.coletar()
        self.assertEqual(len(chamadas), 2)


class FakeConexao:
    def __init__(self):
        self.fechada = False

    def close(self):
        self.fechada = True


class PortasTest(unittest.TestCase):
    PORTAS = [
        {"rotulo": "LOGIN", "host": "10.0.0.60", "porta": 6900},
        {"rotulo": "CHAR", "host": "10.0.0.60", "porta": 6121},
        {"rotulo": "MAP", "host": "localhost", "porta": 5121},
    ]

    def test_aberta_recusada_e_timeout(self):
        chamadas = []

        def conectar(endereco, timeout):
            chamadas.append((endereco, timeout))
            if endereco[1] == 6121:
                raise ConnectionRefusedError()
            if endereco[1] == 5121:
                raise TimeoutError()
            return FakeConexao()

        r = c.coletar_portas(self.PORTAS, conectar)
        self.assertEqual(r, [{"rotulo": "LOGIN", "aberto": True},
                             {"rotulo": "CHAR", "aberto": False},
                             {"rotulo": "MAP", "aberto": False}])
        self.assertEqual(sorted(e for e, _ in chamadas),
                         [("10.0.0.60", 6121), ("10.0.0.60", 6900), ("localhost", 5121)])
        self.assertTrue(all(t == 0.6 for _, t in chamadas))

    def test_fecha_a_conexao(self):
        con = FakeConexao()
        c.coletar_portas(self.PORTAS[:1], lambda e, timeout: con)
        self.assertTrue(con.fechada)

    def test_qualquer_erro_vira_fechada(self):
        r = c.coletar_portas(self.PORTAS[:1], lambda e, timeout: (_ for _ in ()).throw(RuntimeError("x")))
        self.assertEqual(r, [{"rotulo": "LOGIN", "aberto": False}])

    def test_ordem_preservada_e_em_paralelo(self):
        import time
        def lento(endereco, timeout):
            time.sleep(0.2)
            return FakeConexao()
        t0 = time.monotonic()
        r = c.coletar_portas(self.PORTAS, lento)
        self.assertLess(time.monotonic() - t0, 0.5)
        self.assertEqual([x["rotulo"] for x in r], ["LOGIN", "CHAR", "MAP"])

    def test_validacao_rejeita(self):
        ruins = [
            {"rotulo": "A", "host": "10.0.0.1", "porta": 0},
            {"rotulo": "A", "host": "10.0.0.1", "porta": 65536},
            {"rotulo": "A", "host": "10.0.0.1", "porta": "80"},
            {"rotulo": "A", "host": "10.0.0.1", "porta": True},
            {"rotulo": "", "host": "10.0.0.1", "porta": 80},
            {"rotulo": "ROTULO MUITO LONGO AQUI", "host": "10.0.0.1", "porta": 80},
            {"rotulo": "a b", "host": "10.0.0.1", "porta": 80},
            {"rotulo": "A", "host": "http://x", "porta": 80},
            {"rotulo": "A", "host": "a;rm -rf", "porta": 80},
            {"rotulo": "A", "host": "-x", "porta": 80},
            {"rotulo": "A", "host": "", "porta": 80},
            {"rotulo": "A", "porta": 80},
            "nao-e-dict",
        ]
        for item in ruins:
            with self.assertRaises(ValueError, msg=repr(item)):
                c.validar_porta(item)

    def test_validacao_aceita(self):
        for host in ("10.0.0.60", "::1", "localhost", "atheron", "nas.lan"):
            self.assertEqual(c.validar_porta({"rotulo": "OK-1", "host": host, "porta": 65535})["host"], host)

    def test_item_invalido_na_coleta_nao_conecta(self):
        chamadas = []
        r = c.coletar_portas([{"rotulo": "X", "host": "1.2.3.4", "porta": 0}],
                             lambda e, timeout: chamadas.append(e))
        self.assertEqual(r, [{"rotulo": "X", "aberto": False}])
        self.assertEqual(chamadas, [])

    def test_padrao_usa_create_connection(self):
        import socket
        self.assertIs(c.CONECTAR_PADRAO, socket.create_connection)

    def test_coletor_poe_em_metricas_e_cacheia(self):
        chamadas = []
        relogio = [10.0]
        co = TestColetorBase.criar(
            {"portas": self.PORTAS[:2]},
            conectar=lambda e, timeout: chamadas.append(e) or FakeConexao(),
            relogio=lambda: relogio[0],
        )
        m = co.coletar()
        self.assertEqual(m["portas"], [{"rotulo": "LOGIN", "aberto": True}, {"rotulo": "CHAR", "aberto": True}])
        co.coletar()
        self.assertEqual(len(chamadas), 2)
        relogio[0] = 30.0
        co.coletar()
        self.assertEqual(len(chamadas), 4)

    def test_sem_portas_nao_poe_chave(self):
        self.assertNotIn("portas", TestColetorBase.criar({}).coletar())


class TestColetorBase:
    @staticmethod
    def criar(config=None, **kw):
        arquivos = {
            "/proc/stat": STAT_A,
            "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
            "/proc/meminfo": MEMINFO,
            "/proc/uptime": "100.0 50.0\n",
        }

        def leitor(caminho):
            if caminho in arquivos:
                return arquivos[caminho]
            raise FileNotFoundError(caminho)

        base = {"host": "teste", "discos": [], "servicos": [], "balanceador": None, "pares": []}
        base.update(config or {})
        padrao = dict(
            leitor_arquivo=leitor,
            executar=lambda a: (_ for _ in ()).throw(FileNotFoundError(a[0])),
            buscar=lambda u: {},
            dormir=lambda s: None,
            raiz_sys="/caminho/que/nao/existe",
        )
        padrao.update(kw)
        return c.Coletor(base, **padrao)


class HistoricoTest(unittest.TestCase):
    def test_anel_de_60_mantem_os_ultimos_em_ordem(self):
        tempo = [1000.0]
        co = TestColetorBase.criar({}, agora=lambda: tempo[0])
        for i in range(75):
            tempo[0] = 1000.0 + i
            co.amostrar()
        h = co.historico()
        self.assertEqual(len(h["t"]), 60)
        self.assertEqual(h["t"][0], 1015.0)
        self.assertEqual(h["t"][-1], 1074.0)
        self.assertEqual(h["t"], sorted(h["t"]))
        self.assertEqual(len(h["cpu"]), 60)
        self.assertEqual(len(h["ram"]), 60)
        self.assertEqual(h["ram"][-1], 75.0)
        self.assertNotIn("gpu", h)
        self.assertEqual(h["intervalo_s"], 15)

    def test_gpu_so_quando_ha(self):
        def executar(args):
            return 0, "40, 100, 1000, 50\n"
        co = TestColetorBase.criar({}, executar=executar)
        co.amostrar()
        co.amostrar()
        h = co.historico()
        self.assertEqual(h["gpu"], [40, 40])

    def test_historico_vazio(self):
        h = TestColetorBase.criar({}).historico()
        self.assertEqual(h["t"], [])
        self.assertEqual(h["cpu"], [])

    def test_metricas_incluem_historico(self):
        co = TestColetorBase.criar({})
        co.amostrar()
        m = co.coletar()
        self.assertEqual(len(m["historico"]["cpu"]), 1)
        import json
        json.dumps(m)

    def test_falha_de_leitura_guarda_none(self):
        co = TestColetorBase.criar({}, leitor_arquivo=lambda p: (_ for _ in ()).throw(OSError(p)))
        co.amostrar()
        h = co.historico()
        self.assertEqual((h["cpu"], h["ram"]), ([None], [None]))

    def test_intervalo_configuravel(self):
        co = TestColetorBase.criar({"intervalo_historico_s": 5})
        self.assertEqual(co.historico()["intervalo_s"], 5)

    def test_thread_amostra_e_para(self):
        import time
        co = TestColetorBase.criar({"intervalo_historico_s": 0.01})
        co.iniciar_historico()
        try:
            limite = time.monotonic() + 3
            while len(co.historico()["t"]) < 3 and time.monotonic() < limite:
                time.sleep(0.01)
            self.assertGreaterEqual(len(co.historico()["t"]), 3)
            self.assertTrue(co._thread_historico.daemon)
        finally:
            co.parar()
        self.assertFalse(co._thread_historico.is_alive())
        n = len(co.historico()["t"])
        time.sleep(0.05)
        self.assertEqual(len(co.historico()["t"]), n)

    def test_iniciar_duas_vezes_nao_duplica(self):
        co = TestColetorBase.criar({"intervalo_historico_s": 0.01})
        co.iniciar_historico()
        t = co._thread_historico
        co.iniciar_historico()
        self.assertIs(co._thread_historico, t)
        co.parar()



GIB = 2 ** 30


def _tier(**extra):
    d = {"when": "2026-11-15 02:03:37", "simulate": False, "ssd_used_gib": 199.86, "hd_used_gib": 158.54,
         "cap_gib": 256}
    d.update(extra)
    return json.dumps(d)


# 2026-11-15 02:03:37 no fuso local, como o job escreve
AGORA_TIER = __import__("datetime").datetime(2026, 11, 15, 3, 0, 0).timestamp()


class TierStateTest(unittest.TestCase):
    def _r(self, texto, agora=AGORA_TIER):
        return c.coletar_tier_state("NAS SSD", "/x/tier-state.json", lambda p: texto, agora)

    def test_valido(self):
        r = self._r(_tier())
        self.assertEqual(r["rotulo"], "NAS SSD")
        self.assertEqual(r["total_b"], 256 * GIB)
        self.assertEqual(r["usado_b"], int(round(199.86 * GIB)))
        self.assertEqual(r["pct"], round(199.86 * 100 / 256, 1))
        self.assertEqual(r["base"], 1024)
        self.assertFalse(r["parado"])

    def test_velho_mais_de_3h_fica_parado(self):
        r = self._r(_tier(), agora=AGORA_TIER + 3 * 3600)
        self.assertTrue(r["parado"])
        self.assertEqual(r["total_b"], 256 * GIB)
        self.assertFalse(self._r(_tier(), agora=AGORA_TIER + 2 * 3600)["parado"])

    def test_when_ausente_ou_invalido_fica_parado(self):
        for w in (None, "ontem", 5):
            r = self._r(_tier(when=w))
            self.assertTrue(r["parado"], w)
            self.assertEqual(r["total_b"], 256 * GIB)

    def test_arquivo_ausente_vira_nd(self):
        def falha(p):
            raise FileNotFoundError(p)
        self.assertEqual(c.coletar_tier_state("N", "/x", falha, AGORA_TIER), {"rotulo": "N", "erro": "n/d"})

    def test_invalidos_viram_nd(self):
        for texto in ("lixo", "[]", _tier(cap_gib=0), _tier(cap_gib=-1), _tier(ssd_used_gib=-1),
                      _tier(ssd_used_gib="1"), _tier(cap_gib=True), _tier(ssd_used_gib=None),
                      json.dumps({"when": "2026-11-15 02:03:37"})):
            self.assertEqual(self._r(texto), {"rotulo": "NAS SSD", "erro": "n/d"}, texto)

    def test_coletor_usa_tier_state_e_statvfs(self):
        fake = SimpleNamespace(f_frsize=1, f_blocks=1000, f_bfree=500, f_bavail=500)
        arquivos = {"/proc/meminfo": MEMINFO, "/t.json": _tier()}

        def leitor(p):
            if p in arquivos:
                return arquivos[p]
            raise FileNotFoundError(p)
        cfg = {"host": "t", "balanceador": None, "servicos": [], "pares": [], "discos": [
            {"rotulo": "NAS HD", "caminho": "/srv/nas-hd"}, {"rotulo": "NAS SSD", "tier_state": "/t.json"},
            {"rotulo": "ruim", "tier_state": "/nao.json"}]}
        co = c.Coletor(cfg, leitor_arquivo=leitor, statvfs=lambda p: fake, agora=lambda: AGORA_TIER,
                       executar=lambda a: (_ for _ in ()).throw(FileNotFoundError(a[0])),
                       dormir=lambda s: None, raiz_sys="/nao/existe")
        d = co.coletar()["discos"]
        self.assertEqual(d[0]["total_b"], 1000)
        self.assertEqual(d[1]["total_b"], 256 * GIB)
        self.assertEqual(d[2], {"rotulo": "ruim", "erro": "n/d"})


AGORA_CL = 1_800_000_000


def _lim(**kw):
    d = {"versao": 1, "conta": "pessoal", "atualizado_em": AGORA_CL - 30,
         "cinco_horas": {"pct": 42.5, "volta_em": AGORA_CL + 3600},
         "semanal": {"pct": 10.0, "volta_em": AGORA_CL + 86400}}
    d.update(kw)
    return d


def _tot(n=1):
    return {"entrada": n, "saida": 2 * n, "cache_leitura": 3 * n, "cache_escrita": 4 * n,
            "total": 10 * n, "custo_usd": 1.5 * n}


def _tok(**kw):
    d = {"versao": 1, "conta": "pessoal", "gerado_em": AGORA_CL - 60, "hoje": _tot(1),
         "sete_dias": _tot(7), "por_modelo_7d": []}
    d.update(kw)
    return d


def _ler_de(arqs):
    def ler(p):
        v = arqs[p]
        return v if isinstance(v, str) else json.dumps(v)
    return ler


class ColetarClaudeTest(unittest.TestCase):
    CFG = {"limites": "/l.json", "tokens": "/t.json"}

    def _col(self, lim=None, tok=None, agora=AGORA_CL):
        arqs = {}
        if lim is not None:
            arqs["/l.json"] = lim
        if tok is not None:
            arqs["/t.json"] = tok
        return c.coletar_claude(self.CFG, _ler_de(arqs), agora)

    def test_valido(self):
        r = self._col(_lim(), _tok())
        self.assertEqual(r["limites"], {
            "cinco_horas": {"pct": 42.5, "volta_em": AGORA_CL + 3600, "renovado": False},
            "semanal": {"pct": 10.0, "volta_em": AGORA_CL + 86400, "renovado": False},
            "idade_s": 30, "velho": False})
        self.assertEqual(r["tokens"], {"hoje": _tot(1), "sete_dias": _tot(7), "idade_s": 60, "velho": False})

    def test_ausente(self):
        r = self._col()
        self.assertEqual(r, {"limites": {"erro": "n/d"}, "tokens": {"erro": "n/d"}})

    def test_json_invalido(self):
        r = self._col("{truncado", "[1, 2]")
        self.assertEqual(r, {"limites": {"erro": "n/d"}, "tokens": {"erro": "n/d"}})

    def test_pct_tipo_errado(self):
        for ruim in ("42", True, None, [1]):
            r = self._col(_lim(cinco_horas={"pct": ruim, "volta_em": AGORA_CL + 5}), _tok())
            self.assertEqual(r["limites"], {"erro": "n/d"}, repr(ruim))

    def test_pct_clampa(self):
        r = self._col(_lim(cinco_horas={"pct": -5, "volta_em": AGORA_CL + 5},
                           semanal={"pct": 130.0, "volta_em": AGORA_CL + 5}), _tok())
        self.assertEqual(r["limites"]["cinco_horas"]["pct"], 0.0)
        self.assertEqual(r["limites"]["semanal"]["pct"], 100.0)

    def test_volta_em_invalido(self):
        for ruim in ("x", True, None, -1):
            r = self._col(_lim(cinco_horas={"pct": 5.0, "volta_em": ruim}), _tok())
            self.assertEqual(r["limites"], {"erro": "n/d"}, repr(ruim))

    def test_renovado(self):
        r = self._col(_lim(cinco_horas={"pct": 99.0, "volta_em": AGORA_CL - 1}), _tok())
        self.assertEqual(r["limites"]["cinco_horas"],
                         {"pct": 0.0, "volta_em": AGORA_CL - 1, "renovado": True})
        self.assertFalse(r["limites"]["semanal"]["renovado"])
        r = self._col(_lim(cinco_horas={"pct": 99.0, "volta_em": AGORA_CL}), _tok())
        self.assertTrue(r["limites"]["cinco_horas"]["renovado"])

    def test_velho_limites_900(self):
        self.assertFalse(self._col(_lim(atualizado_em=AGORA_CL - 900), _tok())["limites"]["velho"])
        r = self._col(_lim(atualizado_em=AGORA_CL - 901), _tok())["limites"]
        self.assertEqual((r["idade_s"], r["velho"]), (901, True))

    def test_velho_tokens_1200(self):
        self.assertFalse(self._col(_lim(), _tok(gerado_em=AGORA_CL - 1200))["tokens"]["velho"])
        self.assertTrue(self._col(_lim(), _tok(gerado_em=AGORA_CL - 1201))["tokens"]["velho"])

    def test_idade_nunca_negativa(self):
        self.assertEqual(self._col(_lim(atualizado_em=AGORA_CL + 50), _tok())["limites"]["idade_s"], 0)

    def test_uma_janela_so(self):
        d = _lim()
        del d["semanal"]
        r = self._col(d, _tok())["limites"]
        self.assertIsNone(r["semanal"])
        self.assertEqual(r["cinco_horas"]["pct"], 42.5)

    def test_sem_nenhuma_janela(self):
        d = _lim()
        del d["semanal"], d["cinco_horas"]
        self.assertEqual(self._col(d, _tok())["limites"], {"erro": "n/d"})

    def test_atualizado_em_invalido(self):
        for ruim in ("x", True, None):
            self.assertEqual(self._col(_lim(atualizado_em=ruim), _tok())["limites"], {"erro": "n/d"})

    def test_tokens_totais_invalidos(self):
        for ruim in ({**_tot(), "total": "9"}, {**_tot(), "custo_usd": True}, {**_tot(), "saida": -1}, 5):
            self.assertEqual(self._col(_lim(), _tok(hoje=ruim))["tokens"], {"erro": "n/d"}, repr(ruim))
        d = _tok()
        del d["sete_dias"]
        self.assertEqual(self._col(_lim(), d)["tokens"], {"erro": "n/d"})

    def test_um_arquivo_ruim_nao_derruba_o_outro(self):
        r = self._col("lixo", _tok())
        self.assertEqual(r["limites"], {"erro": "n/d"})
        self.assertIn("hoje", r["tokens"])


class ColetarS10Test(unittest.TestCase):
    def _res(self, **kw):
        d = {"versao": 1, "gerado_em": AGORA_CL - 10,
             "bateria": {"nivel": 80, "status": "carregando", "temperatura_c": 31.5, "saude": "boa"},
             "caminhos": {"usb": True, "adb_sem_fio": False, "tailscale": True, "ssh_termux": True,
                          "vnc": None},
             "avisos": ["temperatura"]}
        d.update(kw)
        return d

    def _s10(self, dados, agora=AGORA_CL):
        return c.coletar_s10("/r.json", _ler_de({"/r.json": dados}), agora)

    def test_valido(self):
        r = self._s10(self._res())
        self.assertEqual(r["bateria"]["nivel"], 80)
        self.assertEqual(r["caminhos"]["vnc"], None)
        self.assertEqual(r["avisos"], ["temperatura"])
        self.assertEqual((r["idade_s"], r["velho"]), (10, False))

    def test_bateria_nula(self):
        self.assertIsNone(self._s10(self._res(bateria=None))["bateria"])

    def test_velho_120(self):
        self.assertFalse(self._s10(self._res(gerado_em=AGORA_CL - 120))["velho"])
        r = self._s10(self._res(gerado_em=AGORA_CL - 121))
        self.assertEqual((r["idade_s"], r["velho"]), (121, True))

    def test_ausente_e_invalido(self):
        def falha(p):
            raise FileNotFoundError(p)
        self.assertEqual(c.coletar_s10("/r.json", falha, AGORA_CL), {"erro": "n/d"})
        for ruim in ("{x", "[]", self._res(gerado_em="x"), self._res(gerado_em=True),
                     self._res(caminhos="x"), self._res(avisos="temperatura"),
                     self._res(bateria="x")):
            self.assertEqual(self._s10(ruim), {"erro": "n/d"}, repr(ruim))

    def test_avisos_filtra_nao_texto(self):
        self.assertEqual(self._s10(self._res(avisos=["a", 3, None, "b"]))["avisos"], ["a", "b"])


class ColetorClaudeS10Test(unittest.TestCase):
    def _co(self, extra):
        arqs = {"/proc/meminfo": MEMINFO, "/l.json": json.dumps(_lim()), "/t.json": json.dumps(_tok()),
                "/r.json": json.dumps({"gerado_em": AGORA_CL, "bateria": None, "caminhos": {}, "avisos": []})}

        def leitor(p):
            if p in arqs:
                return arqs[p]
            raise FileNotFoundError(p)
        cfg = {"host": "t", "balanceador": None, "servicos": [], "pares": [], "discos": [], **extra}
        return c.Coletor(cfg, leitor_arquivo=leitor, agora=lambda: AGORA_CL,
                         executar=lambda a: (_ for _ in ()).throw(FileNotFoundError(a[0])),
                         dormir=lambda s: None, raiz_sys="/nao/existe")

    def test_sem_chaves_nao_cria(self):
        m = self._co({}).coletar()
        self.assertNotIn("claude", m)
        self.assertNotIn("s10", m)

    def test_com_chaves(self):
        m = self._co({"claude": {"limites": "/l.json", "tokens": "/t.json"},
                      "s10": {"resumo": "/r.json"}}).coletar()
        self.assertEqual(m["claude"]["limites"]["idade_s"], 30)
        self.assertEqual(m["s10"]["idade_s"], 0)

    def test_limiares_publicados_com_padrao_e_validacao(self):
        import alertas
        self.assertEqual(self._co({}).coletar()["limiares"], alertas.PADRAO)
        m = self._co({"limiares": {"disco_aviso": 70, "ram": "x", "zzz": 1}}).coletar()
        self.assertEqual(m["limiares"], {**alertas.PADRAO, "disco_aviso": 70})
        self.assertEqual(self._co({"limiares": 5}).coletar()["limiares"], alertas.PADRAO)

    def test_config_malformada_isolada(self):
        m = self._co({"claude": ["x"], "s10": {"resumo": 5}}).coletar()
        self.assertEqual(m["claude"], {"limites": {"erro": "n/d"}, "tokens": {"erro": "n/d"}})
        self.assertEqual(m["s10"], {"erro": "n/d"})


class GpuEstadoTest(unittest.TestCase):
    def _g(self, saida):
        return c.coletar_gpu(lambda a: (0, saida))

    def test_desativada(self):
        self.assertEqual(self._g("0, 0, 2048, 39")["estado"], "desativada")
        self.assertEqual(self._g("0, [N/A], 2048, 39")["estado"], "desativada")

    def test_ativa(self):
        self.assertEqual(self._g("35, 900, 2048, 50")["estado"], "ativa")
        self.assertEqual(self._g("0, 100, 2048, 50")["estado"], "ativa")
        self.assertEqual(self._g("5, 0, 2048, 50")["estado"], "ativa")
        self.assertEqual(self._g("[N/A], 0, 2048, 50")["estado"], "ativa")


class NaoFinitosClaudeTest(unittest.TestCase):
    CFG = {"limites": "/l.json", "tokens": "/t.json"}

    def test_limites_e_tokens_com_infinity_nan_sao_invalidos(self):
        for lit in ("Infinity", "-Infinity", "NaN"):
            lim = json.dumps(_lim()).replace("42.5", lit)
            self.assertIn(lit, lim)
            r = c.coletar_claude(self.CFG, _ler_de({"/l.json": lim, "/t.json": json.dumps(_tok())}), AGORA_CL)
            self.assertEqual(r["limites"], {"erro": "n/d"}, lit)
            self.assertNotEqual(r["tokens"], {"erro": "n/d"})
            tok = json.dumps(_tok()).replace("1.5", lit, 1)
            self.assertIn(lit, tok)
            r = c.coletar_claude(self.CFG, _ler_de({"/l.json": json.dumps(_lim()), "/t.json": tok}), AGORA_CL)
            self.assertEqual(r["tokens"], {"erro": "n/d"}, lit)
            self.assertNotEqual(r["limites"], {"erro": "n/d"})


class InteirosGigantesClaudeTest(unittest.TestCase):
    CFG = {"limites": "/l.json", "tokens": "/t.json"}

    def test_inteiro_gigante_e_invalido_nao_levanta(self):
        for campo in ("total", "entrada", "custo_usd"):
            tok = json.dumps(_tok(hoje={**_tot(), campo: 10 ** 400}))
            r = c.coletar_claude(self.CFG, _ler_de({"/l.json": json.dumps(_lim()), "/t.json": tok}), AGORA_CL)
            self.assertEqual(r["tokens"], {"erro": "n/d"}, campo)
        lim = json.dumps(_lim(cinco_horas={"pct": 10 ** 400, "volta_em": AGORA_CL + 5}))
        r = c.coletar_claude(self.CFG, _ler_de({"/l.json": lim, "/t.json": json.dumps(_tok())}), AGORA_CL)
        self.assertEqual(r["limites"], {"erro": "n/d"})
        lim = json.dumps(_lim(cinco_horas={"pct": 1.0, "volta_em": 2 ** 53}))
        r = c.coletar_claude(self.CFG, _ler_de({"/l.json": lim, "/t.json": json.dumps(_tok())}), AGORA_CL)
        self.assertEqual(r["limites"], {"erro": "n/d"})

    def test_total_2_elevado_53_e_invalido_e_abaixo_vale(self):
        for n, esperado_ok in ((2 ** 53, False), (2 ** 53 - 1, True)):
            r = c.coletar_claude(self.CFG, _ler_de({"/l.json": json.dumps(_lim()),
                                                    "/t.json": json.dumps(_tok(hoje={**_tot(), "total": n}))}),
                                 AGORA_CL)
            self.assertEqual("erro" not in r["tokens"], esperado_ok, n)


if __name__ == "__main__":
    unittest.main()
