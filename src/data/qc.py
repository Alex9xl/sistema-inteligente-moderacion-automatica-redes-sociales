"""
Paso 1.8 - Validación de calidad del corpus (Quality Control).

Funciones:
  - validar_corpus(df)        : aserciones estrictas; lanza AssertionError si falla.
  - detectar_duplicados(df)   : informe de duplicados exactos y normalizados.
  - generar_reporte_qc(df, n) : escribe data/reports_qc/qc_corpus_v{n}.md
  - ejecutar_qc_completo()    : carga el corpus enriquecido y ejecuta todo lo anterior.

Uso directo:
    python src/data/qc.py
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections import Counter
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rutas por defecto
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "data" / "processed" / "corpus_v1_enriquecido.parquet"
REPORTS_DIR = ROOT / "data" / "reports_qc"

# ---------------------------------------------------------------------------
# 1. Validaciones estrictas (INSTRUCCIONES_PROYECTO.md §6.4)
# ---------------------------------------------------------------------------


def validar_corpus(df: pd.DataFrame) -> None:
    """
    Aserciones de calidad del corpus enriquecido.

    Lanza AssertionError con mensaje descriptivo si alguna validación falla.
    Imprime un resumen de las comprobaciones realizadas.

    Parameters
    ----------
    df : pd.DataFrame
        Corpus a validar (salida del Paso 1.7 o similar).
    """
    errores: list[str] = []

    # 1. IDs únicos
    n_dup_ids = df["id"].duplicated().sum()
    if n_dup_ids > 0:
        errores.append(f"IDs duplicados: {n_dup_ids}")

    # 2. Textos no nulos
    n_nulos = df["texto"].isna().sum()
    if n_nulos > 0:
        errores.append(f"Textos nulos: {n_nulos}")

    # 3. Longitud mínima (≥3 tokens) — warning, no error bloqueante
    longitudes = df["texto"].dropna().str.split().str.len()
    n_cortos = (longitudes < 3).sum()
    if n_cortos > 0:
        pct_cortos = n_cortos / len(df)
        if pct_cortos > 0.05:
            # Solo es error si supera el 5% del corpus
            errores.append(f"Textos con < 3 tokens: {n_cortos} ({pct_cortos:.1%}) — supera umbral 5%")
        else:
            print(f"  [ADVERTENCIA] {n_cortos} textos con < 3 tokens ({pct_cortos:.1%}) -- dentro del umbral aceptable.")

    # 4. Etiquetas en {0, 1}
    etiquetas_unicas = set(df["etiqueta"].unique())
    if not etiquetas_unicas <= {0, 1}:
        errores.append(f"Etiquetas fuera de {{0,1}}: {etiquetas_unicas - {0,1}}")

    # 5. tiene_modismo es bool
    if df["tiene_modismo"].dtype != bool:
        errores.append(
            f"tiene_modismo dtype incorrecto: {df['tiene_modismo'].dtype} (esperado: bool)"
        )

    # 6. Proporción de hate dentro de rango esperado [5%, 60%]
    prop_hate = float(df["etiqueta"].mean())
    if not (0.05 <= prop_hate <= 0.60):
        errores.append(f"Proporción hate fuera de rango [5%-60%]: {prop_hate:.2%}")

    # 7. n_tokens_aprox no tiene negativos
    if "n_tokens_aprox" in df.columns:
        n_neg = (df["n_tokens_aprox"] < 0).sum()
        if n_neg > 0:
            errores.append(f"n_tokens_aprox con valores negativos: {n_neg}")

    # 8. tiene_modismo no tiene nulos
    n_nulos_mod = df["tiene_modismo"].isna().sum()
    if n_nulos_mod > 0:
        errores.append(f"tiene_modismo tiene nulos: {n_nulos_mod}")

    # ---- Resultado ----
    if errores:
        msg = "\n  ".join(errores)
        raise AssertionError(f"Validación del corpus FALLIDA:\n  {msg}")

    print("[OK] Corpus validado correctamente -- todas las aserciones pasaron.")


# ---------------------------------------------------------------------------
# 2. Análisis de duplicados (INSTRUCCIONES_PROYECTO.md §6.5)
# ---------------------------------------------------------------------------

_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)


def _normalizar_para_dup(texto: str) -> str:
    """Normalización ligera para detección de duplicados nivel 2."""
    texto = texto.lower().strip()
    texto = _EMOJI_RE.sub("", texto)
    texto = _PUNCT_RE.sub("", texto)
    return re.sub(r"\s+", " ", texto).strip()


def detectar_duplicados(df: pd.DataFrame) -> dict:
    """
    Detecta duplicados exactos y duplicados normalizados (nivel 2).

    Parameters
    ----------
    df : pd.DataFrame
        Corpus a analizar.

    Returns
    -------
    dict
        Informe con conteos de duplicados en ambos niveles.
    """
    # Nivel 1: duplicados exactos en texto
    n_exactos = df.duplicated(subset=["texto"]).sum()

    # Nivel 2: duplicados normalizados
    texto_norm = df["texto"].apply(_normalizar_para_dup)
    n_normalizados = texto_norm.duplicated().sum()

    informe = {
        "n_total": len(df),
        "n_duplicados_exactos": int(n_exactos),
        "n_duplicados_normalizados": int(n_normalizados),
        "n_unicos_exactos": int(len(df) - n_exactos),
        "n_unicos_normalizados": int(len(df) - n_normalizados),
    }

    print(f"  Duplicados exactos      : {n_exactos:,}")
    print(f"  Duplicados normalizados : {n_normalizados:,}")

    return informe


# ---------------------------------------------------------------------------
# 3. Estadísticas de longitud
# ---------------------------------------------------------------------------


def stats_longitud(df: pd.DataFrame) -> dict:
    """Estadísticas de longitud en tokens y caracteres."""
    tokens = df["texto"].str.split().str.len()
    chars = df["texto"].str.len()

    return {
        "tokens_mediana": float(tokens.median()),
        "tokens_p95": float(tokens.quantile(0.95)),
        "tokens_max": int(tokens.max()),
        "tokens_min": int(tokens.min()),
        "chars_mediana": float(chars.median()),
        "chars_p95": float(chars.quantile(0.95)),
        "chars_max": int(chars.max()),
    }


# ---------------------------------------------------------------------------
# 4. Top N-gramas por clase
# ---------------------------------------------------------------------------


def _tokenize_simple(texto: str) -> list[str]:
    """Tokenización simple para n-gramas (lowercase, solo alfanuméricos)."""
    return re.findall(r"\b[a-záéíóúüñ]{3,}\b", texto.lower())


def top_ngramas(df: pd.DataFrame, n: int = 1, top_k: int = 30) -> dict:
    """
    Top K unigramas o bigramas por clase (0=no_hate, 1=hate).

    Parameters
    ----------
    n : int
        1 = unigramas, 2 = bigramas.
    top_k : int
        Número de items a devolver por clase.
    """
    resultado: dict = {}

    for etiqueta in [0, 1]:
        label = "hate" if etiqueta == 1 else "no_hate"
        textos = df[df["etiqueta"] == etiqueta]["texto"].fillna("")
        tokens_todos: list[str] = []
        for t in textos:
            tok = _tokenize_simple(t)
            if n == 1:
                tokens_todos.extend(tok)
            else:
                tokens_todos.extend(
                    [f"{tok[i]} {tok[i+1]}" for i in range(len(tok) - 1)]
                )
        resultado[label] = Counter(tokens_todos).most_common(top_k)

    return resultado


# ---------------------------------------------------------------------------
# 5. Generador del reporte QC en Markdown
# ---------------------------------------------------------------------------


def _sha256_archivo(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def generar_reporte_qc(
    df: pd.DataFrame,
    version: int = 1,
    corpus_path: Path | None = None,
    output_dir: Path = REPORTS_DIR,
) -> Path:
    """
    Genera el reporte de calidad del corpus en formato Markdown.

    Sigue la especificación de INSTRUCCIONES_PROYECTO.md §6.4:
      - Tamaño total
      - Distribución de clases (global y por dataset)
      - Distribución de tiene_modismo (global y por clase)
      - Longitudes (mediana, p95) en tokens y caracteres
      - Top 50 unigramas y bigramas por clase
      - Conteo de duplicados
      - Conteo de filas con longitud < 3 tokens

    Parameters
    ----------
    df : pd.DataFrame
        Corpus ya validado con validar_corpus().
    version : int
        Versión del corpus (se usa en el nombre del archivo).
    corpus_path : Path | None
        Ruta del archivo Parquet fuente (para calcular SHA-256 y tamaño).
    output_dir : Path
        Directorio donde se escribe el reporte.

    Returns
    -------
    Path
        Ruta al archivo .md generado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"qc_corpus_v{version}.md"

    # ---- Estadísticas básicas ----
    n_total = len(df)
    n_hate = int((df["etiqueta"] == 1).sum())
    n_no_hate = int((df["etiqueta"] == 0).sum())
    prop_hate = n_hate / n_total

    n_con_mod = int(df["tiene_modismo"].sum())
    n_sin_mod = n_total - n_con_mod

    long_stats = stats_longitud(df)
    dup_info = detectar_duplicados(df)

    n_cortos = int((df["texto"].str.split().str.len() < 3).sum())

    # ---- N-gramas (unigramas, solo top 30 por velocidad) ----
    unigrams = top_ngramas(df, n=1, top_k=30)
    bigrams = top_ngramas(df, n=2, top_k=30)

    # ---- SHA-256 del archivo fuente ----
    sha_str = "N/A"
    tamano_str = "N/A"
    if corpus_path and corpus_path.exists():
        sha_str = _sha256_archivo(corpus_path)
        tamano_kb = corpus_path.stat().st_size / 1024
        tamano_str = f"{tamano_kb:,.1f} KB"

    # ---- Distribución por dataset ----
    dist_dataset = df.groupby("dataset")["etiqueta"].agg(
        total="count", hate=lambda x: (x == 1).sum()
    )
    dist_dataset["no_hate"] = dist_dataset["total"] - dist_dataset["hate"]
    dist_dataset["pct_hate"] = (dist_dataset["hate"] / dist_dataset["total"]).map(
        "{:.1%}".format
    )

    # ---- Distribución de modismos por clase ----
    ct = pd.crosstab(
        df["etiqueta"].map({0: "no_hate", 1: "hate"}),
        df["tiene_modismo"].map({True: "con_modismo", False: "sin_modismo"}),
        margins=True,
    )

    # ---- Escritura del reporte ----
    lineas: list[str] = []

    def w(s: str = "") -> None:
        lineas.append(s)

    w("# Reporte QC — Corpus v1 Enriquecido")
    w()
    w(f"**Generado automáticamente por `src/data/qc.py`**")
    w()
    w("---")
    w()

    # Sección 1: Tamaño
    w("## 1. Tamaño del corpus")
    w()
    w(f"| Métrica | Valor |")
    w(f"|---------|-------|")
    w(f"| Total filas | **{n_total:,}** |")
    w(f"| Hate (1) | {n_hate:,} ({prop_hate:.1%}) |")
    w(f"| No hate (0) | {n_no_hate:,} ({1-prop_hate:.1%}) |")
    w(f"| Archivo fuente | `corpus_v{version}_enriquecido.parquet` |")
    w(f"| Tamaño en disco | {tamano_str} |")
    w(f"| SHA-256 | `{sha_str}` |")
    w()

    # Sección 2: Distribución de clases por dataset
    w("## 2. Distribución de clases por dataset")
    w()
    w("| Dataset | Total | Hate | No hate | % Hate |")
    w("|---------|-------|------|---------|--------|")
    for ds, row in dist_dataset.iterrows():
        w(f"| {ds} | {row['total']:,} | {row['hate']:,} | {row['no_hate']:,} | {row['pct_hate']} |")
    w()

    # Sección 3: Modismos
    w("## 3. Distribución de `tiene_modismo`")
    w()
    w("### 3.1 Global")
    w()
    w("| | Valor | % |")
    w("|---|---|---|")
    w(f"| Con modismo | {n_con_mod:,} | {n_con_mod/n_total:.1%} |")
    w(f"| Sin modismo | {n_sin_mod:,} | {n_sin_mod/n_total:.1%} |")
    w()
    w("### 3.2 Cruzada (etiqueta × tiene_modismo)")
    w()
    w("```")
    w(ct.to_string())
    w("```")
    w()
    # Añadir observación sobre porcentajes por clase
    if n_hate > 0 and n_no_hate > 0:
        pct_hate_con = ct.loc["hate", "con_modismo"] / n_hate if "hate" in ct.index and "con_modismo" in ct.columns else 0
        pct_nohate_con = ct.loc["no_hate", "con_modismo"] / n_no_hate if "no_hate" in ct.index and "con_modismo" in ct.columns else 0
        w(f"> **Observación:** El {pct_hate_con:.1%} de las instancias *hate* contienen modismos LATAM")
        w(f"> vs {pct_nohate_con:.1%} de las *no_hate*. Diferencia relevante para H3.")
    w()

    # Sección 4: Longitudes
    w("## 4. Longitud de texto")
    w()
    w("| Métrica | Tokens | Caracteres |")
    w("|---------|--------|------------|")
    w(f"| Mediana | {long_stats['tokens_mediana']:.0f} | {long_stats['chars_mediana']:.0f} |")
    w(f"| P95 | {long_stats['tokens_p95']:.0f} | {long_stats['chars_p95']:.0f} |")
    w(f"| Máximo | {long_stats['tokens_max']} | {long_stats['chars_max']} |")
    w(f"| Mínimo (tokens) | {long_stats['tokens_min']} | — |")
    w()
    w(f"> Textos con < 3 tokens (descartables): **{n_cortos}**")
    if long_stats["tokens_p95"] <= 128:
        w(f"> P95 ≤ 128 tokens → `max_length=128` es suficiente para tokenización BERT.")
    elif long_stats["tokens_p95"] <= 256:
        w(f"> P95 ≤ 256 tokens → considerar `max_length=256` para tokenización BERT.")
    else:
        w(f"> ⚠ P95 > 256 tokens → `max_length=512` recomendado; revisar truncamiento.")
    w()

    # Sección 5: Duplicados
    w("## 5. Duplicados")
    w()
    w("| Nivel | Duplicados encontrados |")
    w("|-------|------------------------|")
    w(f"| Exactos (texto idéntico) | {dup_info['n_duplicados_exactos']:,} |")
    w(f"| Normalizados (sin puntuación/emojis, lowercase) | {dup_info['n_duplicados_normalizados']:,} |")
    w()
    if dup_info["n_duplicados_exactos"] == 0 and dup_info["n_duplicados_normalizados"] == 0:
        w("> ✓ Sin duplicados detectados.")
    else:
        w("> ⚠ Existen duplicados — considerar eliminación antes del entrenamiento.")
    w()

    # Sección 6: Top N-gramas
    w("## 6. Top 30 unigramas por clase (sanity check)")
    w()
    w("### Clase: hate")
    w()
    w("| Posición | Unigrama | Frecuencia |")
    w("|----------|----------|------------|")
    for i, (term, cnt) in enumerate(unigrams.get("hate", []), start=1):
        w(f"| {i} | {term} | {cnt:,} |")
    w()
    w("### Clase: no_hate")
    w()
    w("| Posición | Unigrama | Frecuencia |")
    w("|----------|----------|------------|")
    for i, (term, cnt) in enumerate(unigrams.get("no_hate", []), start=1):
        w(f"| {i} | {term} | {cnt:,} |")
    w()
    w("## 7. Top 30 bigramas por clase")
    w()
    w("### Clase: hate")
    w()
    w("| Posición | Bigrama | Frecuencia |")
    w("|----------|---------|------------|")
    for i, (term, cnt) in enumerate(bigrams.get("hate", []), start=1):
        w(f"| {i} | {term} | {cnt:,} |")
    w()
    w("### Clase: no_hate")
    w()
    w("| Posición | Bigrama | Frecuencia |")
    w("|----------|---------|------------|")
    for i, (term, cnt) in enumerate(bigrams.get("no_hate", []), start=1):
        w(f"| {i} | {term} | {cnt:,} |")
    w()

    # Sección 7: Checklist de aserciones
    w("## 8. Resumen de aserciones de calidad")
    w()
    w("| Aserción | Resultado |")
    w("|----------|-----------|")
    n_ids_dup = int(df["id"].duplicated().sum())
    w(f"| IDs únicos | {'[OK]' if n_ids_dup == 0 else f'[WARN] ({n_ids_dup} dup.)'} |")
    w(f"| Textos no nulos | {'✓' if df['texto'].notna().all() else '✗'} |")
    w(f"| Textos ≥ 3 tokens | {'✓' if n_cortos == 0 else f'⚠ ({n_cortos} casos)'} |")
    w(f"| Etiquetas ∈ {{0,1}} | {'✓' if set(df['etiqueta'].unique()) <= {0,1} else '✗'} |")
    w(f"| tiene_modismo dtype==bool | {'✓' if df['tiene_modismo'].dtype == bool else '✗'} |")
    w(f"| Proporción hate ∈ [5%,60%] | {'✓' if 0.05 <= prop_hate <= 0.60 else '✗'} ({prop_hate:.1%}) |")
    w(f"| Cobertura modismos ≥ 15% | {'✓' if (n_con_mod/n_total) >= 0.15 else '✗'} ({n_con_mod/n_total:.1%}) |")
    w()
    w("---")
    w()
    w("*Reporte generado por `src/data/qc.py` — Paso 1.8 del pipeline de datos.*")

    # ---- Escribir archivo ----
    output_path.write_text("\n".join(lineas), encoding="utf-8")
    print(f"  Reporte QC guardado en: {output_path.relative_to(ROOT)}")
    return output_path


# ---------------------------------------------------------------------------
# 6. Función orquestadora
# ---------------------------------------------------------------------------


def ejecutar_qc_completo(
    corpus_path: Path = CORPUS_PATH,
    version: int = 1,
    output_dir: Path = REPORTS_DIR,
) -> pd.DataFrame:
    """
    Carga el corpus enriquecido, ejecuta todas las validaciones y genera el reporte.

    Parameters
    ----------
    corpus_path : Path
        Ruta al corpus_v{n}_enriquecido.parquet.
    version : int
        Versión del corpus.
    output_dir : Path
        Directorio para el reporte .md.

    Returns
    -------
    pd.DataFrame
        El corpus cargado (para uso posterior).
    """
    print(f"Cargando corpus desde {corpus_path.relative_to(ROOT)}...")
    df = pd.read_parquet(corpus_path)
    print(f"  {len(df):,} filas, {len(df.columns)} columnas")
    print(f"  Columnas: {df.columns.tolist()}")

    print("\n--- Validaciones de integridad ---")
    validar_corpus(df)

    print("\n--- Detección de duplicados ---")
    detectar_duplicados(df)

    print("\n--- Generando reporte QC ---")
    generar_reporte_qc(
        df,
        version=version,
        corpus_path=corpus_path,
        output_dir=output_dir,
    )

    return df


# ---------------------------------------------------------------------------
# Ejecución directa: python src/data/qc.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # Asegurar que la raíz del proyecto está en sys.path
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("=" * 60)
    print("  PASO 1.8 - Validación de calidad del corpus")
    print("=" * 60)

    corpus = ejecutar_qc_completo(
        corpus_path=CORPUS_PATH,
        version=1,
        output_dir=REPORTS_DIR,
    )

    print("\n" + "=" * 60)
    print("Paso 1.8 completado exitosamente.")
    print("  Reporte: data/reports_qc/qc_corpus_v1.md")
    print("=" * 60)
