"""Aplicación principal FastAPI — Backend de detección de discurso de odio en español."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from .config import settings
from .schemas import (
    ExplainResponse,
    HealthResponse,
    MetadataResponse,
    PredictRequest,
    PredictResponse,
)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# ── Estado global del proceso ─────────────────────────────────────────────────
# Se llena en startup y se vacía en shutdown. Nunca usar variables de módulo
# globales; así el test puede mockearlo sin efectos secundarios.
state: dict = {}

# Mapeado de labels del modelo → etiqueta del dominio
LABEL_MAP = {"LABEL_0": "no_hate", "LABEL_1": "hate"}


# ── Ciclo de vida ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo al arrancar y lo libera al apagar."""
    model_path = Path(settings.model_dir)

    if not model_path.exists():
        logger.warning(
            "Directorio del modelo no encontrado: %s  — iniciando en modo DEGRADADO (sin modelo).",
            model_path,
        )
        state["model_loaded"] = False
        yield
        state.clear()
        return

    logger.info("Cargando tokenizador desde %s …", model_path)
    state["tokenizer"] = AutoTokenizer.from_pretrained(str(model_path))

    logger.info("Cargando modelo desde %s …", model_path)
    state["model"] = AutoModelForSequenceClassification.from_pretrained(str(model_path))
    state["model"].eval()

    device = 0 if torch.cuda.is_available() else -1
    logger.info("Dispositivo: %s", "CUDA" if device == 0 else "CPU")

    state["pipe"] = pipeline(
        "text-classification",
        model=state["model"],
        tokenizer=state["tokenizer"],
        device=device,
    )
    state["model_loaded"] = True
    logger.info("✓ Modelo cargado correctamente.")

    yield  # La app sirve peticiones aquí

    # Shutdown: liberar recursos
    state.clear()
    logger.info("Modelo descargado. Backend cerrado.")


# ── Aplicación ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Hate Speech ES API",
    description=(
        "Backend REST para detección automática de discurso de odio en español. "
        "Modelo: BETO fine-tuned (dccuchile/bert-base-spanish-wwm-cased). "
        "Proyecto de tesis — Universidad Nacional Mayor de San Marcos."
    ),
    version=settings.model_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _require_model() -> None:
    """Lanza HTTP 503 si el modelo no está cargado."""
    if not state.get("model_loaded"):
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible. Verifique que 'models/beto_finetuned_final/' existe.",
        )


def _run_pipeline(texto: str) -> tuple[str, float]:
    """
    Ejecuta el pipeline de clasificación y devuelve (etiqueta, probabilidad_hate).

    - Si el pipeline devuelve LABEL_1 (hate), la probabilidad ya corresponde a hate.
    - Si devuelve LABEL_0 (no_hate), la prob del pipeline es la de no_hate; la de
      hate es 1 - score.
    """
    output = state["pipe"](
        texto[:settings.max_input_chars],
        truncation=True,
        max_length=128,
    )[0]

    raw_label: str = output["label"]   # "LABEL_0" o "LABEL_1"
    score: float = output["score"]

    etiqueta = LABEL_MAP.get(raw_label, raw_label)

    if raw_label == "LABEL_1":
        prob_hate = score
    else:
        prob_hate = 1.0 - score

    # Aplicar umbral de decisión
    if prob_hate >= settings.threshold:
        etiqueta = "hate"
    else:
        etiqueta = "no_hate"

    return etiqueta, prob_hate


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health() -> HealthResponse:
    """Liveness check. Devuelve si el modelo está cargado en memoria."""
    return HealthResponse(
        status="ok",
        model_loaded=bool(state.get("model_loaded")),
        model_version=settings.model_version,
    )


@app.get("/metadata", response_model=MetadataResponse, tags=["Sistema"])
def metadata() -> MetadataResponse:
    """Información sobre el modelo activo y la configuración del backend."""
    return MetadataResponse(
        model_name="beto_finetuned",
        model_version=settings.model_version,
        model_dir=settings.model_dir,
        threshold=settings.threshold,
        max_input_chars=settings.max_input_chars,
    )


@app.post("/predict", response_model=PredictResponse, tags=["Inferencia"])
def predict(req: PredictRequest) -> PredictResponse:
    """
    Clasificación binaria de un texto en español.

    Devuelve la etiqueta (`hate` / `no_hate`) y la probabilidad de que sea discurso de odio.
    """
    _require_model()

    etiqueta, prob_hate = _run_pipeline(req.texto)

    logger.info("predict | etiqueta=%s | prob=%.4f | len=%d", etiqueta, prob_hate, len(req.texto))

    return PredictResponse(
        etiqueta=etiqueta,
        probabilidad=round(prob_hate, 4),
        modelo="beto_finetuned",
        version=settings.model_version,
    )


@app.post("/explain", response_model=ExplainResponse, tags=["Inferencia"])
def explain(req: PredictRequest) -> ExplainResponse:
    """
    Clasificación + explicabilidad con pesos SHAP por token.

    Devuelve la misma información que `/predict` más los tokens y sus pesos SHAP.
    Los pesos positivos empujan la predicción hacia `hate`; los negativos, hacia `no_hate`.

    Nota: si el módulo SHAP no está disponible en el entorno, devuelve pesos neutros (0.0).
    """
    _require_model()

    etiqueta, prob_hate = _run_pipeline(req.texto)

    # Intentar usar ShapExplainer; si falla (sin GPU, sin shap instalado), degradar.
    tokens: list[str] = []
    pesos: list[float] = []

    try:
        from src.xai import ShapExplainer  # importación lazy para no bloquear startup

        if "shap_explainer" not in state:
            logger.info("Inicializando ShapExplainer (primera petición a /explain)…")
            state["shap_explainer"] = ShapExplainer(settings.model_dir)

        result = state["shap_explainer"].explain(req.texto)
        tokens = result["tokens"]
        pesos = result["pesos"]

    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("ShapExplainer no disponible: %s — devolviendo tokens simples.", exc)
        tokens = req.texto.split()[:20]
        pesos = [0.0] * len(tokens)

    logger.info("explain | etiqueta=%s | prob=%.4f | tokens=%d", etiqueta, prob_hate, len(tokens))

    return ExplainResponse(
        etiqueta=etiqueta,
        probabilidad=round(prob_hate, 4),
        modelo="beto_finetuned",
        version=settings.model_version,
        tokens=tokens,
        pesos=pesos,
    )
