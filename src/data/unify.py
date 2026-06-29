"""
Unificación de esquemas: Spanish Hate Speech Superset + DETOXIS.

Este módulo adapta ambas fuentes al esquema canónico del proyecto y las
concatena en un único DataFrame. La salida se guarda en:

    data/interim/corpus_combinado.parquet

Referencia: INSTRUCCIONES_PROYECTO.md §7.2 "Pipeline completo" y §6.3 "Convenciones de nombres".

Esquema canónico producido:
    id              string   — formato <dataset>_<n>, único
    texto           string   — texto ya normalizado
    etiqueta        int8     — {0, 1} (0=no hate, 1=hate)
    dataset         category — origen (hateval, haternet, chileno, hascovsva,
                               homomex, detoxis)
    source          string   — plataforma (Twitter, News Comments)
    nb_annotators   int16    — número de anotadores (1 si desconocido)
    tweet_id        string   — ID del tweet original o None
    pais            category — país del autor o "unknown"

USO COMO SCRIPT:
    python src/data/unify.py

USO COMO MÓDULO:
    from src.data.unify import construir_corpus
    corpus = construir_corpus()
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Rutas (resolucion relativa a la raiz del proyecto)
# ---------------------------------------------------------------------------

# Al importar como modulo, __file__ ya es la ruta al archivo.
# Al correr como script, Path.cwd() suele ser la raiz del proyecto.
_ROOT = Path(__file__).resolve().parents[2]  # src/data/ -> src/ -> root

RAW_SUPERSET = _ROOT / "data/raw/spanish-hate-speech-superset/es_hf_102024.csv"
RAW_DETOXIS  = _ROOT / "data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv"
OUT_INTERIM  = _ROOT / "data/interim/corpus_combinado.parquet"

# Columnas del esquema canonico (orden final del DataFrame)
COLS_CANON = [
    "id", "texto", "etiqueta", "dataset",
    "source", "nb_annotators", "tweet_id", "pais",
]


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _adaptar_superset(path: Path) -> pd.DataFrame:
    """Carga el superset y lo convierte al esquema canonico.

    El superset ya viene preprocesado (usernames → @USER, links → URL),
    por lo que NO se aplica normalizar(). Solo se renombran columnas,
    se coerciona el tipo de etiqueta y se genera el campo id.
    """
    df = pd.read_csv(path, dtype={"tweet_id": "str"})

    # Renombrar al esquema canonico
    df = df.rename(columns={
        "text":                          "texto",
        "labels":                        "etiqueta",
        "post_author_country_location":  "pais",
    })

    # Etiqueta: float -> int8
    df["etiqueta"] = df["etiqueta"].astype("int8")

    # ID unico: <dataset>_<indice>
    df["id"] = df["dataset"].astype(str) + "_" + df.index.astype(str)

    # Asegurar que tweet_id existe (puede no estar en todas las versiones)
    if "tweet_id" not in df.columns:
        df["tweet_id"] = None

    # Homogeneizar pais: NaN → "unknown"
    df["pais"] = df["pais"].fillna("unknown").astype("category")

    # Seleccionar y devolver solo columnas canonicas
    return df[COLS_CANON].copy()


def _adaptar_detoxis(path: Path) -> pd.DataFrame:
    """Carga DETOXIS, normaliza texto y lo convierte al esquema canonico.

    Mapeo de etiqueta:
        toxicity_level >= 2  →  1 (hate)
        toxicity_level <  2  →  0 (no hate)

    Justificacion: el nivel 0 = sin toxicidad, 1 = levemente ofensivo,
    2+ = claramente toxico. Umbral 2 es el usado en literatura (IberLEF 2021).
    """
    # Importar aqui para evitar dependencia circular si se usa solo _adaptar_superset
    from src.data.clean import normalizar  # noqa: PLC0415

    df = pd.read_csv(path)

    # Columna de texto en DETOXIS se llama "comment" (no "text")
    df["texto"] = df["comment"].apply(normalizar)

    # Mapeo binario de etiqueta
    df["etiqueta"] = (df["toxicity_level"] >= 2).astype("int8")

    # Metadatos fijos
    df["dataset"]       = "detoxis"
    df["source"]        = "News Comments"
    df["nb_annotators"] = 1
    df["tweet_id"]      = None
    df["pais"]          = "unknown"

    # ID unico
    df["id"] = "detoxis_" + df.index.astype(str)

    return df[COLS_CANON].copy()


# ---------------------------------------------------------------------------
# Funcion publica principal
# ---------------------------------------------------------------------------

def construir_corpus(
    path_superset: Path = RAW_SUPERSET,
    path_detoxis:  Path = RAW_DETOXIS,
    salida:        Path = OUT_INTERIM,
    guardar:       bool = True,
    verbose:       bool = True,
) -> pd.DataFrame:
    """Construye el corpus combinado superset + DETOXIS.

    Args:
        path_superset: Ruta al CSV del superset.
        path_detoxis:  Ruta al CSV de DETOXIS.
        salida:        Ruta de salida Parquet (data/interim/).
        guardar:       Si True, escribe el Parquet en disco.
        verbose:       Si True, imprime resumen en stdout.

    Returns:
        DataFrame con el corpus unificado en esquema canonico.

    Raises:
        FileNotFoundError: Si alguno de los archivos de entrada no existe.
    """
    # ------------------------------------------------------------------
    # 0. Validar existencia de fuentes
    # ------------------------------------------------------------------
    for ruta in (path_superset, path_detoxis):
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontro el archivo de datos: {ruta}\n"
                "Asegurate de que los datos esten en data/raw/ segun la "
                "estructura del repositorio."
            )

    # ------------------------------------------------------------------
    # 1. Adaptar superset
    # ------------------------------------------------------------------
    if verbose:
        print("Cargando Spanish Hate Speech Superset...")
    df_sup = _adaptar_superset(path_superset)
    if verbose:
        _resumen_parcial("Superset", df_sup)

    # ------------------------------------------------------------------
    # 2. Adaptar DETOXIS (con normalizacion)
    # ------------------------------------------------------------------
    if verbose:
        print("\nCargando y normalizando DETOXIS...")
    df_det = _adaptar_detoxis(path_detoxis)
    if verbose:
        _resumen_parcial("DETOXIS", df_det)

    # ------------------------------------------------------------------
    # 3. Concatenar
    # ------------------------------------------------------------------
    corpus = pd.concat([df_sup, df_det], ignore_index=True)

    # Optimizar tipos para memoria y Parquet
    corpus["dataset"]       = corpus["dataset"].astype("category")
    corpus["pais"]          = corpus["pais"].astype("category")
    corpus["nb_annotators"] = corpus["nb_annotators"].astype("int16")

    # ------------------------------------------------------------------
    # 4. Validacion basica de integridad
    # ------------------------------------------------------------------
    n_dup = corpus.duplicated(subset=["id"]).sum()
    assert n_dup == 0, f"IDs duplicados detectados: {n_dup}"
    assert corpus["texto"].notna().all(), "Hay textos nulos en el corpus"
    assert set(corpus["etiqueta"].unique()) <= {0, 1}, "Etiquetas fuera de {0,1}"

    # ------------------------------------------------------------------
    # 5. Resumen final
    # ------------------------------------------------------------------
    if verbose:
        _resumen_final(corpus)

    # ------------------------------------------------------------------
    # 6. Guardar
    # ------------------------------------------------------------------
    if guardar:
        salida.parent.mkdir(parents=True, exist_ok=True)
        corpus.to_parquet(salida, index=False)
        if verbose:
            print(f"\n✓ Guardado en: {salida.relative_to(_ROOT)}")

    return corpus


# ---------------------------------------------------------------------------
# Helpers de reporte
# ---------------------------------------------------------------------------

def _resumen_parcial(nombre: str, df: pd.DataFrame) -> None:
    hate     = (df["etiqueta"] == 1).sum()
    no_hate  = (df["etiqueta"] == 0).sum()
    print(f"  {nombre}: {len(df):,} filas  |  hate={hate:,} ({hate/len(df):.1%})  |  no_hate={no_hate:,}")


def _resumen_final(corpus: pd.DataFrame) -> None:
    sep = "=" * 55
    print(f"\n{sep}")
    print("  CORPUS UNIFICADO — RESUMEN")
    print(sep)
    print(f"  Total filas : {len(corpus):,}")
    hate    = (corpus["etiqueta"] == 1).sum()
    no_hate = (corpus["etiqueta"] == 0).sum()
    print(f"  Hate   (1)  : {hate:,}  ({hate/len(corpus):.1%})")
    print(f"  No hate(0)  : {no_hate:,}  ({no_hate/len(corpus):.1%})")
    print(f"\n  Por dataset:")
    for ds, cnt in corpus["dataset"].value_counts().items():
        print(f"    {ds:<20} {cnt:>6,}")
    print(f"\n  Nulos por columna:")
    nulos = corpus.isnull().sum()
    for col, n in nulos.items():
        if n > 0:
            print(f"    {col}: {n}")
    if nulos.sum() == 0:
        print("    (ninguno)")
    print(sep)


# ---------------------------------------------------------------------------
# Punto de entrada como script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Permitir correr desde la raiz del proyecto o desde src/data/
    import os
    # Asegurarse de que src/ este en el PYTHONPATH para importar clean.py
    src_dir = str(_ROOT / "src")
    # Insertar la raiz del proyecto en sys.path para que "from src.data.clean" funcione
    root_str = str(_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    print("=" * 55)
    print("  PASO 1.5 — Unificacion superset + DETOXIS")
    print("=" * 55)

    corpus = construir_corpus(verbose=True)

    print(f"\n  Columnas del corpus: {corpus.dtypes.to_dict()}")
    print("\n  Primeras 3 filas:")
    print(corpus.head(3).to_string())
    print("\n✓ Paso 1.5 completado.")
