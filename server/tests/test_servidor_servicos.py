"""Servidor: pagina servicos (p, armado svc), /botoes.* e /tela.* com catalogo e inventario."""
import http.client
import json
import struct
import threading
import unittest

import _caminho  # noqa: F401
import botoes
import coletores
import monitor_server as ms
import servicos

AGORA = 1_700_000_000.0


def catalogo(n=48):
    cat = []
    grupos = ("host", "incus", "docker", "ragnarok")
    tipos = ("systemd", "incus", "docker", "rathena")
    for i in range(n):
        g = i * 4 // n
        alvo = "s%d.service" % i if tipos[g] in ("systemd", "rathena") else "s%d" % i
        cat.append({"id": "s%d" % i, "rotulo": "Servico %d" % i, "grupo": grupos[g], "tipo": tipos[g], "alvo": alvo,
                    "verbos": [["reiniciar", "ligar", "parar"], ["reiniciar"], [], ["ligar", "parar"]][i % 4],
                    "opcional": i % 7 == 0})
    return servicos.validar_catalogo(cat)


def coletor(gerado=AGORA - 3, n=48, estados=None):
    cat = catalogo(n)
    est = {c["id"]: {"estado": ("ativo", "parado", "falha")[i % 3], "detalhe": "x"} for i, c in enumerate(cat)}
    est.update(estados or {})
    arquivos = {"/run/x/status/servicos.json": json.dumps({"gerado": gerado, "servicos": est}),
                "/proc/stat": "cpu 1 0 1 8 0 0 0 0\n", "/proc/loadavg": "0.5 0.4 0.3 1/2 3\n",
                "/proc/meminfo": "MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n",
                "/proc/uptime": "100.0 50.0\n"}

    def leitor(p):
        if p in arquivos:
            return arquivos[p]
        raise FileNotFoundError(p)

    def sem_exec(a):
        raise FileNotFoundError(a[0])
    cfg = {"host": "teste", "discos": [], "servicos": [], "balanceador": None, "pares": [],
           "servicos_kindle": cat, "comandos": {"estado": "/run/x/status"}}
    return coletores.Coletor(cfg, leitor_arquivo=leitor, executar=sem_exec, buscar=lambda u: {},
                             dormir=lambda s: None, raiz_sys="/nao/existe", agora=lambda: AGORA)


class _Fixo:
    """gerado_em fixo (o cabecalho tem segundos)."""
    def __init__(self, c):
        self._c = c

    def coletar(self, *a, **k):
        m = self._c.coletar(*a, **k)
        m["gerado_em"] = "2026-11-16T12:00:00"
        return m

    def __getattr__(self, n):
        return getattr(self._c, n)


class Base(unittest.TestCase):
    def sobe(self, col):
        srv = ms.criar_servidor("127.0.0.1", 0, _Fixo(col), colunas=38, log=False)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        self.porta = srv.server_address[1]
        return srv

    def req(self, caminho):
        con = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        try:
            con.request("GET", caminho)
            r = con.getresponse()
            return r.status, r.read()
        finally:
            con.close()


class ServicosHttpTest(Base):
    def setUp(self):
        self.col = coletor()
        self.sobe(self.col)
        self.itens = self.col.servicos_itens()

    def test_botoes_json_servicos_com_p(self):
        st, corpo = self.req("/botoes.json?pagina=servicos&p=2")
        d = json.loads(corpo)
        self.assertEqual((st, d["pagina"], d["p"]), (200, "servicos", 2))
        self.assertGreater(d["paginas"], 1)
        self.assertEqual(d["botoes"], botoes.layout("servicos", None, 1236, 1648, 2, self.itens))
        ids = [b["id"] for b in d["botoes"]]
        self.assertIn("servicos:anterior", ids)
        self.assertTrue(any(i.startswith("svc:") for i in ids))

    def test_p_invalido_e_fora_da_faixa(self):
        n = json.loads(self.req("/botoes.json?pagina=servicos")[1])["paginas"]
        for q, esperado in (("p=x", 1), ("p=0", 1), ("p=-3", 1), ("p=", 1), ("p=99999", n), ("p=%ff", 1)):
            d = json.loads(self.req("/botoes.json?pagina=servicos&" + q)[1])
            self.assertEqual(d["p"], esperado, q)
        # p so vale em servicos
        self.assertEqual(json.loads(self.req("/botoes.json?pagina=resumo&p=3")[1])["p"], 1)

    def test_botoes_txt_igual_ao_json_nas_paginas_de_servicos(self):
        for q in ("?pagina=servicos&p=1", "?pagina=servicos&p=3", "?pagina=servicos&p=2&armado=svc:s0:reiniciar",
                  "?pagina=comandos&armado=bots-pausar"):
            txt = [l for l in self.req("/botoes.txt" + q)[1].decode().split("\n") if l]
            js = json.loads(self.req("/botoes.json" + q)[1])["botoes"]
            self.assertEqual([l.split() for l in txt],
                             [[b["id"], b["tipo"], str(b["x"]), str(b["y"]), str(b["w"]), str(b["h"])] for b in js])

    def test_armado_svc_valido_so_aparece_na_pagina_certa(self):
        pg1 = [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, 1, self.itens) if b["id"].startswith("svc:")]
        alvo = pg1[0]
        d = json.loads(self.req("/botoes.json?pagina=servicos&p=1&armado=" + alvo)[1])
        self.assertEqual([(b["id"], b["rotulo"]) for b in d["botoes"] if b["armado"]], [(alvo, "Confirmar?")])
        d = json.loads(self.req("/botoes.json?pagina=servicos&p=2&armado=" + alvo)[1])
        self.assertFalse(any(b["armado"] for b in d["botoes"]))  # o botao esta em outra pagina
        for ruim in ("svc:nao-existe:parar", "svc:s0:apagar", "svc:s2:reiniciar"):  # s2 tem verbos []
            d = json.loads(self.req("/botoes.json?pagina=servicos&armado=" + ruim)[1])
            self.assertFalse(any(b["armado"] for b in d["botoes"]), ruim)

    def test_tela_png_de_cada_pagina_do_catalogo(self):
        n = json.loads(self.req("/botoes.json?pagina=servicos")[1])["paginas"]
        imgs = set()
        for p in range(1, n + 1):
            st, corpo = self.req("/tela.png?pagina=servicos&p=%d" % p)
            self.assertEqual(st, 200)
            self.assertEqual(struct.unpack(">II", corpo[16:24]), (1236, 1648))
            imgs.add(corpo)
        self.assertEqual(len(imgs), n)
        self.assertEqual(self.req("/tela.png?pagina=servicos&p=999")[1], self.req("/tela.png?pagina=servicos&p=%d" % n)[1])
        self.assertEqual(self.req("/tela.png?pagina=servicos&p=abc")[1], self.req("/tela.png?pagina=servicos&p=1")[1])

    def test_armado_svc_muda_a_imagem(self):
        alvo = [b["id"] for b in botoes.layout("servicos", None, 1236, 1648, 1, self.itens) if b["id"].startswith("svc:")][0]
        a = self.req("/tela.png?pagina=servicos&p=1")[1]
        b = self.req("/tela.png?pagina=servicos&p=1&armado=" + alvo)[1]
        self.assertNotEqual(a, b)

    def test_tela_txt_servicos(self):
        n_txt = None
        for p in (1, 2, 3, 99, "x"):
            st, corpo = self.req("/tela.txt?pagina=servicos&p=%s" % p)
            linhas = corpo.decode("ascii").splitlines()
            self.assertEqual(st, 200)
            self.assertLessEqual(len(linhas), 26)
            self.assertTrue(all(len(l) <= 38 for l in linhas))
            self.assertIn("SERVICOS pagina", corpo.decode())
        txt = self.req("/tela.txt?pagina=servicos&p=1")[1].decode()
        self.assertIn("HOST", txt)
        self.assertRegex(txt, r"\[#\] Servico \d+")

    def test_tela_txt_resumo_mostra_contagem_e_atencao(self):
        txt = self.req("/tela.txt")[1].decode()
        self.assertIn("Servicos: 48 servicos | ", txt)
        self.assertIn("FALHA", txt)

    def test_metricas_json_inclui_catalogo_sem_alvos(self):
        d = json.loads(self.req("/metricas.json")[1])
        sk = d["servicos_kindle"]
        self.assertEqual((sk["inventario"], len(sk["itens"])), ("ok", 48))
        self.assertNotIn("alvo", json.dumps(sk))


class InventarioVelhoTest(Base):
    def test_velho_vira_desconhecido_sem_botoes_e_aviso(self):
        col = coletor(gerado=AGORA - 120)
        self.sobe(col)
        d = json.loads(self.req("/botoes.json?pagina=servicos")[1])
        self.assertFalse([b for b in d["botoes"] if b["id"].startswith("svc:")])
        self.assertTrue(all(i["estado"] == "desconhecido" for i in col.servicos_itens()))
        self.assertIn("estados desatualizados", self.req("/tela.txt")[1].decode())
        self.assertEqual(self.req("/tela.png?pagina=servicos")[1][:4], b"\x89PNG")
        self.assertEqual(self.req("/tela.png?pagina=resumo")[1][:4], b"\x89PNG")

    def test_um_item_em_falha_nao_estrago_a_pagina(self):
        col = coletor(estados={"s1": {"estado": "falha", "detalhe": "x" * 80}})
        self.sobe(col)
        self.assertEqual(self.req("/tela.png?pagina=servicos&p=1")[1][:4], b"\x89PNG")


if __name__ == "__main__":
    unittest.main()
