"""Esquemas Pydantic para la API de detección de discurso de odio."""

from pydantic import BaseModel, Field
from typing import Annotated
from pydantic import StringConstraints


TextoStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=512)]


class PredictRequest(BaseModel):
    texto: TextoStr = Field(..., description="Texto a clasificar (máx. 512 caracteres).")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"texto": "Ese tipo me cae muy mal, es un idiota."}
            ]
        }
    }


class PredictResponse(BaseModel):
    etiqueta: str = Field(..., pattern=r"^(hate|no_hate)$", description="Etiqueta predicha.")
    probabilidad: float = Field(..., ge=0.0, le=1.0, description="Probabilidad de la clase predicha.")
    modelo: str = Field(..., description="Nombre del modelo usado.")
    version: str = Field(..., description="Versión del modelo.")


class ExplainResponse(PredictResponse):
    tokens: list[str] = Field(..., description="Tokens del texto (subwords del tokenizador).")
    pesos: list[float] = Field(..., description="Peso SHAP de cada token (positivo → hate).")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio.")
    model_loaded: bool = Field(..., description="Indica si el modelo está cargado en memoria.")
    model_version: str = Field(..., description="Versión del modelo activo.")


class MetadataResponse(BaseModel):
    model_name: str
    model_version: str
    model_dir: str
    threshold: float
    max_input_chars: int
