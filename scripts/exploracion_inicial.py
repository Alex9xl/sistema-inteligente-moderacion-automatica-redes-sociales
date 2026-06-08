#!/usr/bin/env python
"""
scripts/exploracion_inicial.py
==============================
Paso 1.3 del proyecto (ver `documentos_extras/desarrollo.md`).

Exploración inicial de los 4 datasets crudos en español:
  1. HatEval 2019 (filtrado a `language == "es"`)
  2. DETOXIS 2021
  3. HaterNet
  4. Chilean Dataset

Produce:
  * `data/reports_qc/exploracion_inicial.md`  -> reporte ejecutivo
  * `data/reports_qc/figuras/*.png`           -> 4 figuras
  * `data/reports_qc/exploracion_inicial.json` -> métricas crudas (machine-readable)

Uso:
    python scripts/exploracion_inicial.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # backend no interactivo (CI / scripts)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Configuración de rutas (todas relativas a la raíz del repo)
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "data" / "reports_qc"
FIGS = REPORTS / "figuras"
REPORTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

# Subconjunto reducido de modismos/seeds LATAM para identificación preliminar.
# El lexicón completo se construirá en el Paso 1.6 en `data/lexicons/`.
SEEDS_LATAM = {
    "weón", "weon", "wn", "culiao", "culiá", "flaite", "fome", "mapuchento",
    "boludo", "pelotudo", "forro", "sorete", "chamo", "chama",
    "pinche", "naco", "naca", "no mames", "vete a la verga", "chinga tu madre",
    "parce", "parcero", "marica", "gonorrea", "pirobo", "hijueputa",
    "concha de tu madre", "conchatumadre", "ctmre", "qliao",
}


# ----------------------------------------------------------------------
# Cargadores (uno por dataset)
# ----------------------------------------------------------------------
def cargar_hateval() -> pd.DataFrame:
    """Carga HatEval (train+dev+test) y se queda con español únicamente."""
    base = RAW / "HatEval" / "data"
    archivos = {
        "train": base / "train-00000-of-00001.csv",
        "dev":   base / "dev-00000-of-00001.csv",
        "test":  base / "test-00000-of-00001.csv",
    }
    partes = []
    for split, ruta in archivos.items():
        if not ruta.exists():
            print(f"  [HatEval] ! falta {ruta.name}, se omite", file=sys.stderr)
            continue
        df = pd.read_csv(ruta)
        df["split"] = split
        partes.append(df)
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes, ignore_index=True)
    if "language" in df.columns:
        df = df[df["language"].astype(str).str.lower() == "es"].copy()
    return df


def cargar_detoxis() -> pd.DataFrame:
    """Carga DETOXIS (sólo el train, que es el que tiene etiquetas)."""
    ruta = RAW / "DETOXIS_2021-main" / "data" / "DATASET_DETOXIS.csv"
    if not ruta.exists():
        print(f"  [DETOXIS] ! falta {ruta.name}", file=sys.stderr)
        return pd.DataFrame()
    return pd.read_csv(ruta)


def cargar_haternet() -> pd.DataFrame:
    """
    Parsea HaterNet (`labeled_corpus_6K.txt`).
    Formato: `id=...;||;texto;||;etiqueta`.
    """
    ruta = RAW / "HaterNet-data" / "labeled_corpus_6K.txt"
    if not ruta.exists():
        print(f"  [HaterNet] ! falta {ruta.name}", file=sys.stderr)
        return pd.DataFrame()
    filas: list[dict] = []
    with ruta.open("r", encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(";||;")
            if len(partes) != 3:
                continue
            id_raw, texto, etiqueta = partes
            id_ = id_raw.replace("id=", "").strip()
            try:
                lab = int(etiqueta.strip())
            except ValueError:
                continue
            filas.append({"id": id_, "text": texto, "label": lab})
    return pd.DataFrame(filas)


def cargar_chilean() -> pd.DataFrame:
    """Carga el dataset chileno completo."""
    ruta = RAW / "Chilean dataset" / "dataset_chileno_lenguaje_ofensivo.csv"
    if not ruta.exists():
        print(f"  [Chilean] ! falta {ruta.name}", file=sys.stderr)
        return pd.DataFrame()
    return pd.read_csv(ruta, low_memory=False)


# ----------------------------------------------------------------------
# Métricas comunes
# ----------------------------------------------------------------------
def _safe_str(s: Any) -> str:
    return "" if s is None else str(s)


def estadisticas_longitud(textos: pd.Series) -> dict[str, float]:
    """Devuelve estadísticas básicas de longitud (en caracteres y palabras)."""
    textos = textos.dropna().astype(str)
    if textos.empty:
        return {}
    chars = textos.str.len()
    words = textos.str.split().apply(len)
    return {
        "n_textos": int(textos.shape[0]),
        "chars_media": float(chars.mean()),
        "chars_mediana": float(chars.median()),
        "chars_p95": float(chars.quantile(0.95)),
        "chars_max": int(chars.max()),
        "chars_min": int(chars.min()),
        "tokens_media": float(words.mean()),
        "tokens_mediana": float(words.median()),
        "tokens_p95": float(words.quantile(0.95)),
        "tokens_max": int(words.max()),
    }


def distribucion_binaria(serie: pd.Series) -> dict[int, int]:
    """Cuenta valores 0/1 en una serie (después de coerción int donde sea posible)."""
    s = pd.to_numeric(serie, errors="coerce").dropna().astype(int)
    counts = s.value_counts().to_dict()
    return {int(k): int(v) for k, v in counts.items()}


def proporcion_seeds_latam(textos: pd.Series, seeds: set[str]) -> float:
    """Proporción de textos que contienen al menos un seed LATAM (case-insensitive)."""
    if textos.empty:
        return 0.0
    seeds_lc = {s.lower() for s in seeds}
    palabras_re = "|".join(map(_re_escape, seeds_lc))
    if not palabras_re:
        return 0.0
    import re as _re
    pat = _re.compile(rf"(?<![\wáéíóúñ])({palabras_re})(?![\wáéíóúñ])", _re.IGNORECASE)
    presencia = textos.dropna().astype(str).apply(lambda t: bool(pat.search(t)))
    return float(presencia.mean())


def _re_escape(s: str) -> str:
    import re as _re
    return _re.escape(s)


# ----------------------------------------------------------------------
# Reporte por dataset
# ----------------------------------------------------------------------
def explorar_dataset(
    nombre: str,
    df: pd.DataFrame,
    columna_texto: str,
    columnas_etiqueta: list[str],
) -> dict[str, Any]:
    """Devuelve un diccionario con todos los hallazgos del dataset."""
    if df.empty:
        return {"nombre": nombre, "vacio": True}

    resumen: dict[str, Any] = {
        "nombre": nombre,
        "vacio": False,
        "shape": list(df.shape),
        "columnas": df.columns.tolist(),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "nulos_por_columna": {c: int(df[c].isna().sum()) for c in df.columns},
        "duplicados_texto": (
            int(df[columna_texto].astype(str).duplicated().sum())
            if columna_texto in df.columns
            else None
        ),
    }

    if columna_texto in df.columns:
        resumen["longitud"] = estadisticas_longitud(df[columna_texto])
        resumen["seeds_latam_prop"] = round(
            proporcion_seeds_latam(df[columna_texto], SEEDS_LATAM), 4
        )

    resumen["distribucion_etiquetas"] = {}
    for col in columnas_etiqueta:
        if col in df.columns:
            resumen["distribucion_etiquetas"][col] = distribucion_binaria(df[col])

    if columna_texto in df.columns:
        muestras = df[columna_texto].dropna().astype(str).head(3).tolist()
        resumen["muestras"] = [m[:200] for m in muestras]

    return resumen


# ----------------------------------------------------------------------
# Figuras
# ----------------------------------------------------------------------
def figura_distribucion_clases(resumenes: dict[str, dict[str, Any]]) -> Path:
    """Barras 0/1 por dataset."""
    nombres, n0, n1 = [], [], []
    mapping = [
        ("HatEval", "HS"),
        ("DETOXIS", "toxicity"),
        ("HaterNet", "label"),
        ("Chilean", "hate speech/estereotipo"),
    ]
    for ds, col in mapping:
        d = resumenes.get(ds, {})
        if not d or d.get("vacio"):
            continue
        dist = d.get("distribucion_etiquetas", {}).get(col, {})
        if not dist:
            continue
        nombres.append(ds)
        n0.append(int(dist.get(0, 0)))
        n1.append(int(dist.get(1, 0)))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(nombres))
    w = 0.4
    ax.bar(x - w / 2, n0, w, label="No odio (0)", color="#a78bfa")
    ax.bar(x + w / 2, n1, w, label="Odio (1)", color="#7c3aed")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_ylabel("# ejemplos")
    ax.set_title("Distribución de clases por dataset (etiqueta de hate principal)")
    ax.legend()
    for i, (a, b) in enumerate(zip(n0, n1)):
        if a + b > 0:
            ax.text(i - w / 2, a, str(a), ha="center", va="bottom", fontsize=9)
            ax.text(i + w / 2, b, str(b), ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    out = FIGS / "distribucion_clases.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def figura_longitud_texto(resumenes: dict[str, dict[str, Any]]) -> Path:
    """Boxplot de longitud (en tokens) por dataset."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    nombres, datos = [], []
    for nombre, d in resumenes.items():
        if d.get("vacio") or "longitud" not in d:
            continue
        nombres.append(nombre)
        long_ = d["longitud"]
        # Reconstruimos un resumen 5-num desde estadísticos
        datos.append([
            max(1, long_["tokens_media"] - long_["tokens_p95"] / 2),
            long_["tokens_mediana"],
            long_["tokens_p95"],
            long_["tokens_max"],
        ])
    if not nombres:
        plt.close(fig)
        return FIGS / "longitud_tokens.png"
    valores_p95 = [d[2] for d in datos]
    valores_med = [d[1] for d in datos]
    valores_max = [d[3] for d in datos]
    x = np.arange(len(nombres))
    ax.bar(x - 0.2, valores_med, 0.2, label="Mediana", color="#7c3aed")
    ax.bar(x,        valores_p95, 0.2, label="P95",      color="#a78bfa")
    ax.bar(x + 0.2,  valores_max, 0.2, label="Máx",      color="#c4b5fd")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_ylabel("# tokens")
    ax.set_title("Longitud de texto por dataset (en tokens, escala lineal)")
    ax.legend()
    fig.tight_layout()
    out = FIGS / "longitud_tokens.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def figura_seeds_latam(resumenes: dict[str, dict[str, Any]]) -> Path:
    """Barras: proporción con al menos un seed LATAM por dataset."""
    nombres, props = [], []
    for nombre, d in resumenes.items():
        if d.get("vacio"):
            continue
        if "seeds_latam_prop" in d:
            nombres.append(nombre)
            props.append(d["seeds_latam_prop"] * 100)
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(nombres, props, color="#7c3aed")
    ax.set_ylabel("% de textos con ≥1 seed LATAM")
    ax.set_title("Presencia de modismos LATAM (subconjunto pre-lexicón Paso 1.6)")
    for b, p in zip(bars, props):
        ax.text(
            b.get_x() + b.get_width() / 2, p, f"{p:.1f}%",
            ha="center", va="bottom", fontsize=10,
        )
    fig.tight_layout()
    out = FIGS / "seeds_latam.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def figura_volumen(resumenes: dict[str, dict[str, Any]]) -> Path:
    """Volumen total por dataset (después de filtros aplicados)."""
    nombres, volumen = [], []
    for nombre, d in resumenes.items():
        if d.get("vacio"):
            continue
        nombres.append(nombre)
        volumen.append(int(d["shape"][0]))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bars = ax.bar(nombres, volumen, color="#a78bfa")
    ax.set_ylabel("# filas tras carga inicial")
    ax.set_title("Volumen por dataset después de carga (HatEval filtrado a ES)")
    for b, v in zip(bars, volumen):
        ax.text(
            b.get_x() + b.get_width() / 2, v, f"{v:,}",
            ha="center", va="bottom", fontsize=10,
        )
    fig.tight_layout()
    out = FIGS / "volumen_datasets.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------
# Reporte Markdown
# ----------------------------------------------------------------------
def render_md(resumenes: dict[str, dict[str, Any]], rutas_figuras: dict[str, Path]) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = sum(int(d.get("shape", [0])[0]) for d in resumenes.values() if not d.get("vacio"))

    lineas = [
        "# Reporte de Exploración Inicial (Paso 1.3)",
        "",
        f"**Generado:** {fecha}  ",
        f"**Datasets:** {len([d for d in resumenes.values() if not d.get('vacio')])} de 4 cargados.  ",
        f"**Total de filas tras carga inicial:** {total:,}.",
        "",
        "Este documento es la salida automática del script "
        "`scripts/exploracion_inicial.py` y del notebook "
        "`notebooks/01_exploracion.ipynb`. Resume el estado de los datos crudos "
        "antes de la limpieza/normalización (Paso 1.4) y el mapeo a esquema "
        "binario (Paso 1.5).",
        "",
        "## Resumen ejecutivo",
        "",
        "| Dataset | Filas | Idioma | Plataforma | Etiqueta principal | % seeds LATAM |",
        "|---------|------:|--------|------------|--------------------|---------------:|",
    ]

    info_meta = {
        "HatEval":  ("ES (filtrado)", "Twitter",            "HS"),
        "DETOXIS":  ("ES",            "Comentarios noticias", "toxicity"),
        "HaterNet": ("ES",            "Twitter",            "label"),
        "Chilean":  ("ES (CL)",       "Twitter",            "hate speech/estereotipo"),
    }
    for nombre, (idioma, plataforma, etq) in info_meta.items():
        d = resumenes.get(nombre, {"vacio": True})
        if d.get("vacio"):
            lineas.append(f"| {nombre} | — | {idioma} | {plataforma} | {etq} | — |")
            continue
        n_filas = int(d["shape"][0])
        seeds_pct = d.get("seeds_latam_prop", 0) * 100
        lineas.append(
            f"| {nombre} | {n_filas:,} | {idioma} | {plataforma} | `{etq}` | {seeds_pct:.1f}% |"
        )
    lineas.append("")

    lineas += [
        "## Figuras",
        "",
        f"![Volumen por dataset]({rutas_figuras['volumen'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Distribución de clases]({rutas_figuras['clases'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Longitud de texto]({rutas_figuras['longitud'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Seeds LATAM]({rutas_figuras['seeds'].relative_to(REPORTS).as_posix()})",
        "",
    ]

    # Detalle por dataset
    for nombre in ["HatEval", "DETOXIS", "HaterNet", "Chilean"]:
        d = resumenes.get(nombre, {"vacio": True})
        lineas += [f"## {nombre}", ""]
        if d.get("vacio"):
            lineas += ["⚠️ Dataset no encontrado o vacío.", ""]
            continue
        lineas += [
            f"- **Forma:** {d['shape'][0]:,} filas × {d['shape'][1]} columnas",
            f"- **Columnas:** {', '.join(d['columnas'][:14])}"
            + (" …" if len(d["columnas"]) > 14 else ""),
            f"- **Duplicados de texto:** {d.get('duplicados_texto', 'n/a')}",
        ]
        long_ = d.get("longitud", {})
        if long_:
            lineas += [
                f"- **Longitud (chars):** mediana={long_['chars_mediana']:.0f}, "
                f"P95={long_['chars_p95']:.0f}, máx={long_['chars_max']}",
                f"- **Longitud (tokens):** mediana={long_['tokens_mediana']:.0f}, "
                f"P95={long_['tokens_p95']:.0f}, máx={long_['tokens_max']}",
            ]
        lineas.append(f"- **Seeds LATAM presentes:** {d.get('seeds_latam_prop', 0)*100:.2f}% de textos")

        dist = d.get("distribucion_etiquetas", {})
        if dist:
            lineas += ["", "**Distribución de etiquetas:**", ""]
            for col, mapa in dist.items():
                total_col = sum(mapa.values())
                pct = {k: (v / total_col * 100 if total_col else 0) for k, v in mapa.items()}
                pares = ", ".join(f"`{k}`={v:,} ({pct[k]:.1f}%)" for k, v in mapa.items())
                lineas.append(f"- `{col}`: {pares}")

        muestras = d.get("muestras", [])
        if muestras:
            lineas += ["", "**Muestras de texto:**", ""]
            for i, m in enumerate(muestras, 1):
                lineas.append(f"{i}. `{m}`")

        lineas.append("")

    lineas += [
        "## Hallazgos clave (preliminar)",
        "",
        "1. **Volumen consolidado:** los 4 datasets aportan suficientes ejemplos "
        "para particionar 70/15/15 con tamaño razonable.",
        "2. **Heterogeneidad de etiquetas:** cada dataset usa convenciones distintas "
        "(`HS`, `toxicity_level`, `label`, `hate speech/estereotipo`). El Paso 1.5 "
        "las unifica al esquema binario `etiqueta ∈ {0, 1}`.",
        "3. **Cobertura LATAM:** Chilean concentra la mayor proporción de seeds "
        "regionales. Es el dataset crítico para validar H3 (Paso 4).",
        "4. **Calidad textual:** los nulos detectados deben revisarse en limpieza "
        "(Paso 1.4) y los duplicados marcarse antes de unificar (Paso 1.5).",
        "",
        "## Próximo paso",
        "",
        "→ **Paso 1.4** Implementar `src/data/clean.py` con la función `normalizar()` "
        "y aplicarla en el notebook `02_unificacion.ipynb`.",
        "",
    ]
    return "\n".join(lineas)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main() -> int:
    print("=" * 60)
    print(" PASO 1.3 · Exploración inicial de datasets")
    print("=" * 60)

    print("\n[1/4] Cargando datasets...")
    df_hateval = cargar_hateval()
    print(f"  HatEval (ES) :  {df_hateval.shape}")
    df_detoxis = cargar_detoxis()
    print(f"  DETOXIS      :  {df_detoxis.shape}")
    df_haternet = cargar_haternet()
    print(f"  HaterNet     :  {df_haternet.shape}")
    df_chilean = cargar_chilean()
    print(f"  Chilean      :  {df_chilean.shape}")

    print("\n[2/4] Calculando estadísticas por dataset...")
    resumenes = {
        "HatEval": explorar_dataset(
            "HatEval", df_hateval, "text",
            ["HS", "TR", "AG"]
        ),
        "DETOXIS": explorar_dataset(
            "DETOXIS", df_detoxis, "comment",
            ["toxicity", "aggressiveness", "insult", "stereotype",
             "target_person", "target_group"]
        ),
        "HaterNet": explorar_dataset(
            "HaterNet", df_haternet, "text",
            ["label"]
        ),
        "Chilean": explorar_dataset(
            "Chilean", df_chilean, "tweet a etiquetar",
            ["hate speech/estereotipo", "insulto/sobrenombre",
             "grosería c/int.", "sarcasmo/ironía/burla", "mención migración"]
        ),
    }

    print("\n[3/4] Generando figuras...")
    rutas_figuras = {
        "volumen":  figura_volumen(resumenes),
        "clases":   figura_distribucion_clases(resumenes),
        "longitud": figura_longitud_texto(resumenes),
        "seeds":    figura_seeds_latam(resumenes),
    }
    for k, v in rutas_figuras.items():
        print(f"  - {k:9s} -> {v.relative_to(ROOT).as_posix()}")

    print("\n[4/4] Escribiendo reporte Markdown + JSON...")
    md = render_md(resumenes, rutas_figuras)
    md_path = REPORTS / "exploracion_inicial.md"
    md_path.write_text(md, encoding="utf-8")
    json_path = REPORTS / "exploracion_inicial.json"
    json_path.write_text(
        json.dumps(resumenes, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )
    print(f"  Reporte MD   -> {md_path.relative_to(ROOT).as_posix()}")
    print(f"  Reporte JSON -> {json_path.relative_to(ROOT).as_posix()}")

    print("\n[OK] Paso 1.3 completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
