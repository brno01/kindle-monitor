import base64
import os
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import gerar_icones as g  # noqa: E402


def _svg(pasta, nome, paths, viewbox="0 0 10 10", fonte="https://x/y.svg (pkg 1). MIT."):
    vb = ' viewBox="%s"' % viewbox if viewbox else ""
    corpo = "".join('<path d="%s"%s/>' % (d, (' fill-rule="%s"' % r) if r else "") for d, r in paths)
    with open(os.path.join(pasta, nome), "w", encoding="utf-8") as f:
        f.write("<!-- Source: %s -->\n<svg%s>%s</svg>" % (fonte, vb, corpo))


def _bitmap(pasta, nome, tam=10):
    ic = g.carregar(pasta)
    (_, svg, paths), = [i for i in ic if i[0] == nome]
    return g.rasterizar(paths, svg["viewbox"], tam)


def _px(bmp, x, y, tam=10):
    return bmp[y * tam + x]


def test_ring_with_counterclockwise_inner_has_hole(tmp_path):
    # externo horario (area > 0 em y para baixo), interno anti-horario
    d = "M0 0H10V10H0Z M3 3V7H7V3Z"
    _svg(str(tmp_path), "anel.svg", [(d, None)])
    b = _bitmap(str(tmp_path), "anel")
    assert _px(b, 1, 1) == 255
    assert _px(b, 5, 5) == 0


def test_overlapping_squares_same_direction_are_filled(tmp_path):
    d = "M0 0H6V6H0Z M4 4H10V10H4Z"
    _svg(str(tmp_path), "dois.svg", [(d, None)])
    b = _bitmap(str(tmp_path), "dois")
    assert _px(b, 5, 5) == 255  # sobreposicao nao vira furo
    assert _px(b, 1, 1) == 255 and _px(b, 8, 8) == 255
    assert _px(b, 8, 1) == 0


def test_evenodd_makes_hole_for_same_direction(tmp_path):
    d = "M0 0H10V10H0Z M3 3H7V7H3Z"
    _svg(str(tmp_path), "par.svg", [(d, "evenodd")])
    b = _bitmap(str(tmp_path), "par")
    assert _px(b, 5, 5) == 0 and _px(b, 1, 1) == 255


def test_all_path_elements_are_read(tmp_path):
    _svg(str(tmp_path), "dois.svg", [("M0 0H4V4H0Z", None), ("M6 6H10V10H6Z", None)])
    b = _bitmap(str(tmp_path), "dois")
    assert _px(b, 1, 1) == 255 and _px(b, 8, 8) == 255 and _px(b, 8, 1) == 0


def test_viewbox_scales_independent_of_path_bbox(tmp_path):
    # quadrado 0..5 numa viewBox 10: ocupa so a metade (a caixa do path nao estica o desenho)
    _svg(str(tmp_path), "meio.svg", [("M0 0H5V5H0Z", None)])
    b = _bitmap(str(tmp_path), "meio")
    assert _px(b, 2, 2) == 255 and _px(b, 7, 7) == 0


def test_without_viewbox_falls_back_to_path_box(tmp_path):
    _svg(str(tmp_path), "meio.svg", [("M0 0H5V5H0Z", None)], viewbox=None)
    b = _bitmap(str(tmp_path), "meio")
    assert _px(b, 5, 5) == 255  # caixa do path ocupa o bitmap todo (com folga)


def test_invalid_names_are_ignored(tmp_path):
    p = str(tmp_path)
    for nome in ("ok.svg", "Maiuscula.svg", "a.svg", "com-hifen.svg", "nome1.svg", "muitolongonomedeicone.svg", "x.png", "bom.txt"):
        _svg(p, nome, [("M0 0H10V10H0Z", None)])
    assert g.listar_icones(p) == ["ok"]


def test_generated_module_has_all_sizes_and_sources(tmp_path):
    p = str(tmp_path)
    _svg(p, "quadro.svg", [("M0 0H10V10H0Z", None)], fonte="https://x/quadro.svg (pkg 2.0). Apache-2.0.")
    _svg(p, "outro.svg", [("M2 2H8V8H2Z", None)])
    ns = {}
    exec(g.gerar(p), ns)  # saida do proprio gerador, sobre SVGs de teste
    assert sorted(ns["ICONES"]) == ["outro", "quadro"]
    assert tuple(ns["ICONES"]["quadro"]) == g.TAMANHOS == (56, 40, 30)
    for tam, ic in ns["ICONES"]["quadro"].items():
        assert ic["w"] == ic["h"] == tam
        blob = zlib.decompress(base64.b64decode("".join(ic["dados"])))
        assert len(blob) == tam * tam and max(blob) == 255
    assert "quadro: https://x/quadro.svg (pkg 2.0). Apache-2.0." in g.gerar(p)


def test_source_comment_spanning_lines_is_collapsed(tmp_path):
    p = str(tmp_path)
    with open(os.path.join(p, "multi.svg"), "w", encoding="utf-8") as f:
        f.write('<!-- Source: https://x (pkg 1).\n     CC0. -->\n<svg viewBox="0 0 4 4"><path d="M0 0H4V4H0Z"/></svg>')
    assert g.ler_svg(os.path.join(p, "multi.svg"))["fonte"] == "https://x (pkg 1). CC0."


def test_real_claude_icon_in_all_sizes():
    ic = {n: (s, p) for n, s, p in g.carregar(g.PASTA)}
    assert "claude" in ic
    s, p = ic["claude"]
    assert "simple-icons" in s["fonte"] and s["viewbox"] == (0.0, 0.0, 24.0, 24.0)
    for tam in (56, 40, 30):
        b = g.rasterizar(p, s["viewbox"], tam)
        assert len(b) == tam * tam and max(b) > 200


# ---- SVG e dado nao confiavel: tempo linear, limites e docstring seguro

import time  # noqa: E402

import pytest  # noqa: E402


def _escrever(pasta, nome, txt):
    caminho = os.path.join(str(pasta), nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(txt)
    return caminho


@pytest.mark.parametrize("trecho", ["<svg ", "<path ", "<!-- Source: "])
def test_entradas_patologicas_terminam_rapido(tmp_path, trecho):
    # N=20000 cabe em 256 KB e exercita a busca; o limite de tamanho nao pode ser a unica defesa
    txt = trecho * 20000
    assert len(txt) <= g.TAM_MAX_SVG
    c = _escrever(tmp_path, "x.svg", txt)
    t0 = time.time()
    try:
        g.ler_svg(c)
    except SystemExit:
        pass
    assert time.time() - t0 < 1.0


def test_arquivo_grande_demais_e_recusado_antes_de_ler(tmp_path):
    c = _escrever(tmp_path, "grande.svg", "<svg " * 60000)
    assert os.path.getsize(c) > g.TAM_MAX_SVG
    with pytest.raises(SystemExit) as e:
        g.ler_svg(c)
    assert "grande" in str(e.value)


def test_d_somado_acima_do_limite_e_recusado(tmp_path):
    d = "M0 0H1 " * (g.D_MAX // 7 + 100)
    c = _escrever(tmp_path, "d.svg", '<svg viewBox="0 0 10 10"><path d="%s"/></svg>' % d)
    assert os.path.getsize(c) <= g.TAM_MAX_SVG
    with pytest.raises(SystemExit) as e:
        g.ler_svg(c)
    assert "64 KB" in str(e.value)


def test_svg_normal_continua_lido(tmp_path):
    c = _escrever(tmp_path, "a.svg", '<!-- Source: x -->\n<svg a="1" viewBox="0 0 8 9"><path d="M0 0H1V1Z" '
                  'fill-rule="evenodd"/><path d="M1 1H2V2Z"/></svg>')
    r = g.ler_svg(c)
    assert r["viewbox"] == (0.0, 0.0, 8.0, 9.0)
    assert r["paths"] == [("M0 0H1V1Z", "evenodd"), ("M1 1H2V2Z", "nonzero")]
    assert r["fonte"] == "x"


def test_viewbox_no_segundo_svg_ainda_e_achada(tmp_path):
    c = _escrever(tmp_path, "b.svg", '<svg a="1"><svg viewBox="0 0 4 4"><path d="M0 0H1V1Z"/></svg></svg>')
    assert g.ler_svg(c)["viewbox"] == (0.0, 0.0, 4.0, 4.0)


def test_fonte_hostil_gera_modulo_que_compila(tmp_path):
    fonte = 'bad \x00 """ quebra \\ barra \\"""x é \x07'
    _svg(str(tmp_path), "ok.svg", [("M0 0H10V10H0Z", None)], fonte=fonte)
    texto = g.gerar(str(tmp_path))
    compile(texto, "icones_dados.py", "exec")
    ns = {}
    exec(compile(texto, "icones_dados.py", "exec"), ns)
    assert "ok" in ns["ICONES"]
    assert "\x00" not in texto
