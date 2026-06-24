"""
Paso 1.7 - Enriquecimiento del corpus con flags y features.

Carga el corpus combinado (Paso 1.5), aplica el lexicón LATAM (Paso 1.6)
para calcular `tiene_modismo`, agrega `n_tokens_aprox`, y guarda el
corpus enriquecido en data/processed/corpus_v1_enriquecido.parquet.

El campo `tiene_modismo` es OBSERVACIONAL: se usa para segmentar la
evaluación (H3), NO como feature de entrenamiento del modelo.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Rutas por defecto relativas a la raíz del proyecto
CORPUS_INTERIM = Path("data/interim/corpus_combinado.parquet")
LEXICON_CSV = Path("data/lexicons/modismos_latam_v1.csv")
CORPUS_OUTPUT = Path("data/processed/corpus_v1_enriquecido.parquet")


def enriquecer_corpus(
    corpus_path: Path = CORPUS_INTERIM,
    lexicon_path: Path = LEXICON_CSV,
    output_path: Path = CORPUS_OUTPUT,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Enriquece el corpus combinado con la columna `tiene_modismo` y
    `n_tokens_aprox`.

    Parameters
    ----------
    corpus_path : Path
        Ruta al Parquet del corpus combinado (salida del Paso 1.5).
    lexicon_path : Path
        Ruta al CSV del lexicón LATAM (salida del Paso 1.6).
    output_path : Path
        Ruta donde guardar el corpus enriquecido.
    verbose : bool
        Si True, imprime resúmenes por consola.

    Returns
    -------
    pd.DataFrame
        Corpus enriquecido con las columnas adicionales.
    """
    # --- 1. Cargar corpus ---
    if verbose:
        print(f"Cargando corpus desde {corpus_path}...")
    corpus = pd.read_parquet(corpus_path)
    if verbose:
        print(f"  {len(corpus):,} filas cargadas")

    # --- 2. Cargar lexicón (import lazy para permitir ejecución directa) ---
    from src.data.lexicon import LexiconLatam  # noqa: PLC0415

    if verbose:
        print(f"\nCargando lexicon desde {lexicon_path}...")
    lex = LexiconLatam(lexicon_path)
    if verbose:
        info = lex.version_info
        print(f"  {info['n_terminos_canonicos']} terminos canonicos")
        print(f"  {info['n_tokens_totales']} tokens totales (con variantes)")

    # --- 3. Calcular tiene_modismo ---
    if verbose:
        print("\nCalculando tiene_modismo...")
    corpus["tiene_modismo"] = corpus["texto"].apply(lex.tiene_modismo)
    corpus["tiene_modismo"] = corpus["tiene_modismo"].astype(bool)

    n_con = corpus["tiene_modismo"].sum()
    n_sin = len(corpus) - n_con
    pct = 100 * n_con / len(corpus)

    if verbose:
        print(f"  Con modismo  : {n_con:,}  ({pct:.2f}%)")
        print(f"  Sin modismo  : {n_sin:,}  ({100 - pct:.2f}%)")

    # --- 4. Calcular n_tokens_aprox ---
    if verbose:
        print("\nCalculando n_tokens_aprox...")
    corpus["n_tokens_aprox"] = corpus["texto"].str.split().str.len().astype("int16")

    if verbose:
        print(f"  Mediana : {corpus['n_tokens_aprox'].median():.0f} tokens")
        print(f"  P95     : {corpus['n_tokens_aprox'].quantile(0.95):.0f} tokens")
        print(f"  Max     : {corpus['n_tokens_aprox'].max()} tokens")

    # --- 5. Distribución cruzada (clase x modismo) ---
    if verbose:
        print("\n--- Distribucion cruzada: etiqueta x tiene_modismo ---")
        ct = pd.crosstab(
            corpus["etiqueta"].map({0: "no_hate", 1: "hate"}),
            corpus["tiene_modismo"].map({True: "con_modismo", False: "sin_modismo"}),
            margins=True,
        )
        print(ct.to_string())

    # --- 6. Guardar ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    corpus.to_parquet(output_path, index=False, compression="snappy")

    if verbose:
        size_kb = output_path.stat().st_size / 1024
        print(f"\nGuardado en {output_path}")
        print(f"  Tamano  : {size_kb:,.1f} KB")
        print(f"  Filas   : {len(corpus):,}")
        print(f"  Columnas: {corpus.columns.tolist()}")

    return corpus


# ------------------------------------------------------------------
# Ejecución directa
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    # Permitir ejecución directa: python src/data/enrich.py
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    corpus_path = ROOT / CORPUS_INTERIM
    lexicon_path = ROOT / LEXICON_CSV
    output_path = ROOT / CORPUS_OUTPUT

    print("=" * 60)
    print("  PASO 1.7 - Enriquecimiento del corpus")
    print("=" * 60)

    corpus = enriquecer_corpus(
        corpus_path=corpus_path,
        lexicon_path=lexicon_path,
        output_path=output_path,
        verbose=True,
    )

    # Validaciones rápidas
    print("\n--- Validaciones ---")
    assert "tiene_modismo" in corpus.columns, "Falta columna tiene_modismo"
    assert corpus["tiene_modismo"].dtype == bool, "tiene_modismo no es bool"
    assert corpus["tiene_modismo"].notna().all(), "tiene_modismo tiene nulos"
    assert "n_tokens_aprox" in corpus.columns, "Falta columna n_tokens_aprox"
    assert corpus["n_tokens_aprox"].min() >= 0, "n_tokens_aprox con valores negativos"

    pct = 100 * corpus["tiene_modismo"].mean()
    if pct >= 15.0:
        print(f"  [OK]  Cobertura >= 15%: {pct:.2f}%")
    else:
        print(f"  [ADVERTENCIA]  Cobertura < 15%: {pct:.2f}%")

    print(f"  [OK]  tiene_modismo dtype: {corpus['tiene_modismo'].dtype}")
    print(f"  [OK]  n_tokens_aprox dtype: {corpus['n_tokens_aprox'].dtype}")
    print(f"  [OK]  Sin nulos en tiene_modismo")

    print("\n" + "=" * 60)
    print("Paso 1.7 completado.")
