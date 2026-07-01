"""Tests unitarios para limpieza de datos."""

from src.data.clean import normalizar


def test_normalizar_replaces_url_mentions_and_hashtags() -> None:
    text = "Hola @usuario visita https://example.com #TestHashtag ahora"

    result = normalizar(text)

    assert "USUARIO" in result
    assert "URL" in result
    assert "TestHashtag" in result
    assert "@" not in result
    assert "#" not in result
    assert "https://example.com" not in result


def test_normalizar_handles_non_string_inputs() -> None:
    assert normalizar(None) == ""  # type: ignore[arg-type]
    assert normalizar(123) == ""  # type: ignore[arg-type]


def test_normalizar_collapses_extreme_repetitions_and_spaces() -> None:
    result = normalizar("Holaaaaaa     buenoooooo")

    assert result == "Holaa buenoo"
