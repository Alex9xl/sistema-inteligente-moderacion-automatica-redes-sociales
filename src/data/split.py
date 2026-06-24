"""
Paso 1.9 - Particionado estratificado en train/val/test.

Carga corpus_v1_enriquecido.parquet, elimina duplicados exactos de texto,
parte en 70 / 15 / 15 con estratificación por etiqueta y semilla fija,
verifica data leakage, y guarda los tres Parquets en data/processed/.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# ── rutas ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "data" / "processed" / "corpus_v1_enriquecido.parquet"
PROCESSED_DIR = ROOT / "data" / "processed"

RANDOM_STATE = 42
VAL_SIZE = 0.15     # proporción del total
TEST_SIZE = 0.15    # proporción del total

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ── utilidades ─────────────────────────────────────────────────────────────────

def _sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _normalizar_texto(texto: str) -> str:
    """Normalización ligera para detección de duplicados nivel-2."""
    import re
    t = texto.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)   # quitar puntuación
    t = re.sub(r"\s+", " ", t)
    return t


def eliminar_duplicados(df: pd.DataFrame, nivel: int = 1) -> pd.DataFrame:
    """
    Elimina duplicados del corpus antes del particionado.

    nivel=1 → duplicados exactos (texto idéntico).
    nivel=2 → duplicados normalizados (lowercase, sin puntuación, sin emojis).

    Retorna el DataFrame limpio y loguea cuántas filas se eliminaron.
    """
    n_antes = len(df)

    if nivel >= 1:
        df = df.drop_duplicates(subset=["texto"], keep="first")
        log.info("  Duplicados exactos eliminados    : %d", n_antes - len(df))

    if nivel >= 2:
        n_tras_exactos = len(df)
        df = df.copy()
        df["_texto_norm"] = df["texto"].apply(_normalizar_texto)
        df = df.drop_duplicates(subset=["_texto_norm"], keep="first")
        df = df.drop(columns=["_texto_norm"])
        log.info(
            "  Duplicados normalizados eliminados: %d",
            n_tras_exactos - len(df),
        )

    log.info("  Total eliminados                 : %d", n_antes - len(df))
    log.info("  Filas restantes                  : %d", len(df))
    return df.reset_index(drop=True)


def verificar_leakage(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    """Verifica que no haya textos solapados entre splits (data leakage check)."""
    train_textos = set(train["texto"].str.lower())
    val_textos   = set(val["texto"].str.lower())
    test_textos  = set(test["texto"].str.lower())

    leakage_train_val  = len(train_textos & val_textos)
    leakage_train_test = len(train_textos & test_textos)
    leakage_val_test   = len(val_textos   & test_textos)

    if leakage_train_val > 0:
        log.warning("  [ADVERTENCIA] Leakage train↔val : %d textos", leakage_train_val)
    else:
        log.info("  [OK] Sin leakage train↔val")

    if leakage_train_test > 0:
        log.warning("  [ADVERTENCIA] Leakage train↔test: %d textos", leakage_train_test)
    else:
        log.info("  [OK] Sin leakage train↔test")

    if leakage_val_test > 0:
        log.warning("  [ADVERTENCIA] Leakage val↔test  : %d textos", leakage_val_test)
    else:
        log.info("  [OK] Sin leakage val↔test")


# ── función principal ──────────────────────────────────────────────────────────

def particionar_corpus(
    corpus_path: Path = CORPUS_PATH,
    output_dir: Path = PROCESSED_DIR,
    eliminar_dup_nivel: int = 2,
    random_state: int = RANDOM_STATE,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Particiona el corpus enriquecido en train/val/test con estratificación.

    Parámetros
    ----------
    corpus_path       : ruta al Parquet enriquecido.
    output_dir        : directorio de salida para train/val/test.parquet.
    eliminar_dup_nivel: 0=no eliminar, 1=exactos, 2=exactos+normalizados.
    random_state      : semilla fija para reproducibilidad.
    verbose           : imprime resumen detallado.

    Retorna
    -------
    (train, val, test) como DataFrames de pandas.
    """
    if verbose:
        print("=" * 60)
        print("  PASO 1.9 - Particionado train/val/test")
        print("=" * 60)

    # ── 1. Cargar corpus ───────────────────────────────────────────────────────
    log.info("\nCargando corpus desde %s...", corpus_path)
    df = pd.read_parquet(corpus_path)
    log.info("  %d filas, %d columnas", len(df), df.shape[1])
    log.info("  Columnas: %s", df.columns.tolist())

    # ── 2. Eliminar duplicados ─────────────────────────────────────────────────
    if eliminar_dup_nivel > 0:
        log.info("\n--- Eliminando duplicados (nivel %d) ---", eliminar_dup_nivel)
        df = eliminar_duplicados(df, nivel=eliminar_dup_nivel)

    n_total = len(df)

    # ── 3. Distribución de clases antes de partir ──────────────────────────────
    log.info("\n--- Distribución de clases ---")
    dist = df["etiqueta"].value_counts().sort_index()
    for etiqueta, count in dist.items():
        nombre = "hate" if etiqueta == 1 else "no_hate"
        log.info("  %s (%d): %d  (%.1f%%)", nombre, etiqueta, count, 100 * count / n_total)

    # ── 4. Particionar: train 70%, val 15%, test 15% ──────────────────────────
    log.info("\n--- Particionado (70/15/15, seed=%d) ---", random_state)

    # test_size en la primera split = val + test = 30 %
    train, temp = train_test_split(
        df,
        test_size=(VAL_SIZE + TEST_SIZE),
        stratify=df["etiqueta"],
        random_state=random_state,
    )

    # val y test son cada uno 50 % de temp → 15 % del total
    val, test = train_test_split(
        temp,
        test_size=0.50,
        stratify=temp["etiqueta"],
        random_state=random_state,
    )

    # ── 5. Resumen de particiones ──────────────────────────────────────────────
    log.info("")
    for nombre, split in [("Train", train), ("Val  ", val), ("Test ", test)]:
        hate_pct = split["etiqueta"].mean() * 100
        log.info(
            "  %s : %5d filas  (%.1f%% del total)  |  hate: %.1f%%",
            nombre, len(split), 100 * len(split) / n_total, hate_pct,
        )

    # ── 6. Verificar data leakage ──────────────────────────────────────────────
    log.info("\n--- Verificación de data leakage ---")
    verificar_leakage(train, val, test)

    # ── 7. Guardar particiones ─────────────────────────────────────────────────
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info("\n--- Guardando particiones ---")
    for nombre, split in [("train", train), ("val", val), ("test", test)]:
        out_path = output_dir / f"{nombre}.parquet"
        split.to_parquet(out_path, index=False, compression="snappy")
        sha = _sha256(out_path)
        log.info(
            "  %s.parquet guardado  (%d filas)  SHA-256: %s…",
            nombre, len(split), sha[:16],
        )

    if verbose:
        print()
        print("=" * 60)
        print("Paso 1.9 completado exitosamente.")
        print(f"  Train : {len(train):,} filas -> data/processed/train.parquet")
        print(f"  Val   : {len(val):,} filas -> data/processed/val.parquet")
        print(f"  Test  : {len(test):,} filas -> data/processed/test.parquet")
        print("=" * 60)

    return train, val, test


# ── entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    train, val, test = particionar_corpus(verbose=True)
