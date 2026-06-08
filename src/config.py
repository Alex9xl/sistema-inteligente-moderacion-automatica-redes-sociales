"""Configuración global del proyecto."""

from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
LEXICONS_DIR = DATA_DIR / "lexicons"
QC_DIR = DATA_DIR / "reports_qc"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = REPORTS_DIR / "logs"

# Semillas para reproducibilidad
SEEDS = [42, 123, 2024]
RANDOM_SEED = 42

# Modelo y tokenización
BETO_MODEL = "dccuchile/bert-base-spanish-wwm-cased"
MBERT_MODEL = "bert-base-multilingual-cased"
XLMR_MODEL = "xlm-roberta-base"
MAX_LENGTH = 128
BATCH_SIZE = 16

# Parámetros de entrenamiento
NUM_EPOCHS = 4
LEARNING_RATE = 2e-5
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01

# Evaluación
THRESHOLD_PREDICT = 0.5
BOOTSTRAP_ITERATIONS = 1000
MCNEMAR_ALPHA = 0.05
