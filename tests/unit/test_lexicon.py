"""Tests unitarios para el lexicon LATAM."""

from src.data.lexicon import LexiconLatam


def test_lexicon_loads_canonical_file() -> None:
    lex = LexiconLatam()
    info = lex.version_info

    assert info["n_terminos_canonicos"] == 383
    assert info["n_tokens_totales"] >= 800
    assert info["sha256"] == "3402e01cd60547ac0df981d3f72f0be02abf4d2fc3abc13cd955a729546d7dee"


def test_lexicon_detects_known_latam_terms() -> None:
    lex = LexiconLatam()

    assert lex.tiene_modismo("Ese pinche tipo no sabe nada")
    assert lex.tiene_modismo("Boludo, no entendes nada")
    assert lex.tiene_modismo("Gonorrea hijueputa")


def test_lexicon_ignores_neutral_or_invalid_text() -> None:
    lex = LexiconLatam()

    assert not lex.tiene_modismo("Este es un texto neutral de prueba")
    assert not lex.tiene_modismo("")
    assert not lex.tiene_modismo(None)  # type: ignore[arg-type]
