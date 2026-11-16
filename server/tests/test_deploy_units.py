import os
import unittest

import _caminho  # noqa: F401

DEPLOY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "deploy")


def ler(nome):
    with open(os.path.join(DEPLOY, nome), encoding="utf-8") as f:
        return f.read()


def linhas(texto):
    return {l.strip() for l in texto.splitlines() if l.strip() and not l.startswith("#")}


class UnidadesTest(unittest.TestCase):
    def test_timer_do_inventario(self):
        t = linhas(ler("kindle-monitor-inventario.timer"))
        for l in ("OnBootSec=20s", "OnUnitActiveSec=15s", "AccuracySec=1s",
                  "Unit=kindle-monitor-inventario.service", "WantedBy=timers.target"):
            self.assertIn(l, t)

    def test_servico_do_inventario_tem_o_mesmo_endurecimento_do_executor(self):
        inv, exe = linhas(ler("kindle-monitor-inventario.service")), linhas(ler("kindle-monitor-executor.service"))
        for l in ("Type=oneshot", "User=root", "NoNewPrivileges=yes", "ProtectHome=read-only", "PrivateTmp=yes",
                  "ProtectSystem=strict", "ReadWritePaths=/run/kindle-monitor", "ReadWritePaths=-/var/lib/incus/unix.socket",
                  "ProtectKernelModules=yes", "ProtectControlGroups=yes",
                  "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6"):
            self.assertIn(l, inv)
            self.assertIn(l, exe)
        self.assertTrue(any(l.startswith("ExecStart=") and "--inventario" in l and "--config /etc/kindle-monitor/config.json" in l
                            for l in inv))

    def test_instalador_instala_e_habilita_o_timer(self):
        s = ler("instalar-atheron.sh")
        self.assertIn("kindle-monitor-inventario.service", s)
        self.assertIn("kindle-monitor-inventario.timer", s)
        self.assertIn("systemctl enable --now kindle-monitor-inventario.timer", s)
        self.assertLess(s.index("kindle-monitor-inventario.timer /etc"), s.index("daemon-reload"))

    def test_executor_demora_o_bastante_para_10_pedidos_de_90s(self):
        self.assertIn("TimeoutStartSec=600", ler("kindle-monitor-executor.service"))


if __name__ == "__main__":
    unittest.main()
