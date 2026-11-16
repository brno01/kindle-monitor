"""Perfis de energia do Kindle ("Ajustes" na pagina Acoes): so rotulos e descricoes; quem aplica e o Kindle.

O Kindle tem a sua propria tabela numerica em kindle/kindle-monitor/config.sh (PERFIL_<nome>="<intervalo> <ciclos>");
um teste confere que as duas tabelas concordam. `modo` invalido ou ausente vale `PADRAO`.
"""

# nome -> rotulo (sem acento: a fonte embutida e ASCII), intervalo entre atualizacoes (s), ciclos entre flashes completos
PERFIS = {
    "desempenho": {"rotulo": "Desempenho", "intervalo_s": 1, "flash_ciclos": 600},
    "balanceado": {"rotulo": "Balanceado", "intervalo_s": 60, "flash_ciclos": 15},
    "economia": {"rotulo": "Economia", "intervalo_s": 300, "flash_ciclos": 6},
}
NOMES = tuple(PERFIS)
PADRAO = "desempenho"


def modo_valido(valor):
    return valor if isinstance(valor, str) and valor in PERFIS else PADRAO


def _duracao(segundos):
    return "%d s" % segundos if segundos < 60 else "%d min" % (segundos // 60)


def descricao(modo):
    p = PERFIS[modo_valido(modo)]
    return "Atualiza a cada %s · flash a cada %s" % (_duracao(p["intervalo_s"]),
                                                           _duracao(p["intervalo_s"] * p["flash_ciclos"]))
