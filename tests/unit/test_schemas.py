"""Tests unitarios para esquemas Pydantic de la API."""

import pytest
from pydantic import ValidationError

from src.api.schemas import PredictRequest, PredictResponse


def test_predict_request_strips_whitespace() -> None:
    req = PredictRequest(texto="  texto de prueba  ")

    assert req.texto == "texto de prueba"


def test_predict_request_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        PredictRequest(texto="   ")


def test_predict_response_rejects_unknown_label() -> None:
    with pytest.raises(ValidationError):
        PredictResponse(
            etiqueta="toxic",
            probabilidad=0.8,
            modelo="beto_finetuned",
            version="1.0",
        )


def test_predict_response_rejects_probability_out_of_range() -> None:
    with pytest.raises(ValidationError):
        PredictResponse(
            etiqueta="hate",
            probabilidad=1.5,
            modelo="beto_finetuned",
            version="1.0",
        )
