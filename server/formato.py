"""Formatacao de taxas de I/O (base 1024: 1 KB/s = 1024 B/s, 1 MB/s = 1024 KB/s, como os GiB da RAM)."""

_UNIDADES = ("B", "K", "M", "G", "T")


def _valor(bps):
    """(numero, indice da unidade) com uma casa decimal; None se a taxa for desconhecida/negativa."""
    if isinstance(bps, bool) or not isinstance(bps, (int, float)) or bps != bps or bps < 0:
        return None
    v, i = float(bps), 0
    while v >= 1023.95 and i < len(_UNIDADES) - 1:  # 1023.96 would print as 1024.0: use the next unit
        v /= 1024.0
        i += 1
    return v, i


def taxa(bps):
    """'512 B/s', '1.0 KB/s', '12.3 MB/s'; 'n/d' se nao ha valor."""
    r = _valor(bps)
    if r is None:
        return "n/d"
    v, i = r
    return "%d B/s" % round(v) if i == 0 else "%.1f %sB/s" % (v, _UNIDADES[i])


def taxa_curta(bps):
    """Versao curta para o texto: '512B', '40.0K', '12.3M'; 'n/d' se nao ha valor."""
    r = _valor(bps)
    if r is None:
        return "n/d"
    v, i = r
    return "%dB" % round(v) if i == 0 else "%.1f%s" % (v, _UNIDADES[i])
