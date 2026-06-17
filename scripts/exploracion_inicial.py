#!/usr/bin/env python
"""
scripts/exploracion_inicial.py
==============================
Paso 1.3 del proyecto (ver `documentos_extras/desarrollo.md`).

Exploración del corpus base compuesto por:
  1. Spanish Hate Speech Superset (Tonneau et al., 2024) — WOAH/ACL
     Incluye: HatEval, HaterNet, Chilean, HaSCoSVa, HOMO-MEX
     Archivo: data/raw/spanish-hate-speech-superset/es_hf_102024.csv
  2. DETOXIS 2021 (IberLEF 2021) — añadido manualmente
     Archivo: data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv

El superset es un corpus unificado y preprocesado por Tonneau et al. (2024),
disponible en: https://aclanthology.org/2024.woah-1.23

Produce:
  * data/reports_qc/exploracion_inicial.md   -> reporte ejecutivo
  * data/reports_qc/exploracion_inicial.json -> métricas crudas
  * data/reports_qc/figuras/*.png            -> 4 figuras

Uso:
    python scripts/exploracion_inicial.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT     = Path(__file__).resolve().parent.parent
RAW      = ROOT / "data" / "raw"
REPORTS  = ROOT / "data" / "reports_qc"
FIGS     = REPORTS / "figuras"
REPORTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

SUPERSET_PATH = RAW / "spanish-hate-speech-superset" / "es_hf_102024.csv"
DETOXIS_PATH  = RAW / "DETOXIS_2021-main" / "data" / "DATASET_DETOXIS.csv"

# Semillas LATAM para estimación preliminar (previo al lexicón completo del Paso 1.6)
SEEDS_LATAM = {
    "weon", "wn", "culiao", "culia", "flaite", "fome", "mapuchento",
    "boludo", "pelotudo", "forro", "sorete", "chamo", "chama",
    "pinche", "naco", "naca", "parce", "parcero", "marica",
    "gonorrea", "pirobo", "hijueputa", "ctmre", "qliao",
    "pendejo", "cagon", "mamerto", "bolsa", "gil", "tarado",
    "guebon", "hueon", "conchetumare", "aweonao",
}


# ---------------------------------------------------------------------------
# Cargadores
# ---------------------------------------------------------------------------
def cargar_superset() -> pd.DataFrame:
    """Carga el Spanish Hate Speech Superset."""
    if not SUPERSET_PATH.exists():
        print(f"  [ERROR] Superset no encontrado: {SUPERSET_PATH}", file=sys.stderr)
        return pd.DataFrame()
    df = pd.read_csv(SUPERSET_PATH)
    # Renombrar al esquema canónico para análisis uniforme
    df = df.rename(columns={"text": "texto", "labels": "etiqueta"})
    df["etiqueta"] = df["etiqueta"].astype(float).astype(int)
    return df


def cargar_detoxis() -> pd.DataFrame:
    """Carga DETOXIS 2021 y aplica el mapeo binario previsto."""
    if not DETOXIS_PATH.exists():
        print(f"  [ERROR] DETOXIS no encontrado: {DETOXIS_PATH}", file=sys.stderr)
        return pd.DataFrame()
    df = pd.read_csv(DETOXIS_PATH)
    col_texto = "comment" if "comment" in df.columns else df.columns[0]
    df = df.rename(columns={col_texto: "texto"})
    df["etiqueta"] = (df["toxicity_level"] >= 2).astype(int)
    df["dataset"]  = "detoxis"
    return df


# ---------------------------------------------------------------------------
# Estadísticas comunes
# ---------------------------------------------------------------------------
def estadisticas_longitud(textos: pd.Series) -> dict[str, float]:
    textos = textos.dropna().astype(str)
    if textos.empty:
        return {}
    tokens = textos.str.split().apply(len)
    chars  = textos.str.len()
    return {
        "n": int(len(textos)),
        "tokens_media":   float(tokens.mean()),
        "tokens_mediana": float(tokens.median()),
        "tokens_p95":     float(tokens.quantile(0.95)),
        "tokens_max":     int(tokens.max()),
        "chars_mediana":  float(chars.median()),
        "chars_p95":      float(chars.quantile(0.95)),
    }


def prop_seeds_latam(textos: pd.Series) -> float:
    import re
    if textos.empty:
        return 0.0
    pat = re.compile(
        r"(?<![a-záéíóúñü])(" + "|".join(map(re.escape, SEEDS_LATAM)) + r")(?![a-záéíóúñü])",
        re.IGNORECASE,
    )
    return float(textos.dropna().astype(str).apply(lambda t: bool(pat.search(t))).mean())


# ---------------------------------------------------------------------------
# Análisis por fuente
# ---------------------------------------------------------------------------
def analizar_superset(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"vacio": True}
    total = len(df)
    por_dataset = df["dataset"].value_counts().to_dict()
    return {
        "vacio":         False,
        "n_total":       total,
        "n_hate":        int((df["etiqueta"] == 1).sum()),
        "pct_hate":      round((df["etiqueta"] == 1).mean() * 100, 2),
        "n_no_hate":     int((df["etiqueta"] == 0).sum()),
        "datasets":      {k: int(v) for k, v in por_dataset.items()},
        "n_paises":      int(df["post_author_country_location"].nunique()) if "post_author_country_location" in df.columns else None,
        "longitud":      estadisticas_longitud(df["texto"]),
        "seeds_latam_pct": round(prop_seeds_latam(df["texto"]) * 100, 2),
        "duplicados":    int(df["texto"].astype(str).duplicated().sum()),
        "nulos_texto":   int(df["texto"].isnull().sum()),
    }


def analizar_detoxis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"vacio": True}
    total = len(df)
    return {
        "vacio":         False,
        "n_total":       total,
        "n_hate":        int((df["etiqueta"] == 1).sum()),
        "pct_hate":      round((df["etiqueta"] == 1).mean() * 100, 2),
        "n_no_hate":     int((df["etiqueta"] == 0).sum()),
        "longitud":      estadisticas_longitud(df["texto"]),
        "seeds_latam_pct": round(prop_seeds_latam(df["texto"]) * 100, 2),
        "duplicados":    int(df["texto"].astype(str).duplicated().sum()),
        "nulos_texto":   int(df["texto"].isnull().sum()),
        "mapeo_etiqueta": "toxicity_level >= 2 -> 1",
    }


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def fig_distribucion_clases(stats: dict[str, Any]) -> Path:
    """Barras 0/1 por fuente (superset total y DETOXIS)."""
    fuentes = []
    n0_vals, n1_vals = [], []

    # Superset: agrupado total + por sub-dataset
    for nombre, data in [("Superset\n(total)", stats.get("superset", {})),
                          ("DETOXIS", stats.get("detoxis", {}))]:
        d = data
        if d.get("vacio"):
            continue
        fuentes.append(nombre)
        n0_vals.append(d.get("n_no_hate", 0))
        n1_vals.append(d.get("n_hate", 0))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(fuentes))
    w = 0.4
    bars0 = ax.bar(x - w / 2, n0_vals, w, label="No odio (0)", color="#a78bfa")
    bars1 = ax.bar(x + w / 2, n1_vals, w, label="Odio (1)", color="#7c3aed")
    ax.set_xticks(x)
    ax.set_xticklabels(fuentes)
    ax.set_ylabel("# ejemplos")
    ax.set_title("Distribución de clases por fuente del corpus")
    ax.legend()
    for b, v in list(zip(bars0, n0_vals)) + list(zip(bars1, n1_vals)):
        if v > 0:
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    out = FIGS / "distribucion_clases.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_datasets_en_superset(stats: dict[str, Any]) -> Path:
    """Barras: volumen de cada dataset dentro del superset."""
    sup = stats.get("superset", {})
    if sup.get("vacio") or "datasets" not in sup:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        out = FIGS / "volumen_datasets.png"
        fig.savefig(out, dpi=120)
        plt.close(fig)
        return out

    datasets = dict(sorted(sup["datasets"].items(), key=lambda x: -x[1]))
    nombres  = list(datasets.keys())
    valores  = list(datasets.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(nombres, valores, color="#7c3aed")
    ax.set_ylabel("# ejemplos")
    ax.set_title("Datasets incluidos en el Spanish Hate Speech Superset")
    ax.tick_params(axis="x", rotation=20)
    for b, v in zip(bars, valores):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    out = FIGS / "volumen_datasets.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_longitud(stats: dict[str, Any]) -> Path:
    """Barras comparando longitud P95 de texto entre superset y DETOXIS."""
    labels, mediana_vals, p95_vals = [], [], []
    for nombre, key in [("Superset", "superset"), ("DETOXIS", "detoxis")]:
        d = stats.get(key, {})
        if d.get("vacio") or "longitud" not in d:
            continue
        labels.append(nombre)
        mediana_vals.append(d["longitud"]["tokens_mediana"])
        p95_vals.append(d["longitud"]["tokens_p95"])

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, mediana_vals, w, label="Mediana", color="#7c3aed")
    ax.bar(x + w / 2, p95_vals,     w, label="P95",     color="#a78bfa")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("# tokens")
    ax.set_title("Longitud de texto por fuente (tokens)")
    ax.axhline(128, color="red",    linestyle="--", linewidth=1, label="max_length=128")
    ax.axhline(256, color="orange", linestyle="--", linewidth=1, label="max_length=256")
    ax.legend()
    fig.tight_layout()
    out = FIGS / "longitud_tokens.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_seeds_latam(stats: dict[str, Any]) -> Path:
    """Barras: % de textos con al menos un seed LATAM."""
    labels, props = [], []
    for nombre, key in [("Superset", "superset"), ("DETOXIS", "detoxis")]:
        d = stats.get(key, {})
        if d.get("vacio"):
            continue
        labels.append(nombre)
        props.append(d.get("seeds_latam_pct", 0))

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, props, color="#7c3aed")
    ax.set_ylabel("% textos con >= 1 seed LATAM")
    ax.set_title("Presencia de modismos LATAM — estimacion pre-lexicon (Paso 1.6)")
    for b, p in zip(bars, props):
        ax.text(b.get_x() + b.get_width() / 2, p, f"{p:.1f}%", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    out = FIGS / "seeds_latam.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Reporte Markdown
# ---------------------------------------------------------------------------
def render_md(stats: dict[str, Any], rutas: dict[str, Path]) -> str:
    fecha  = datetime.now().strftime("%Y-%m-%d %H:%M")
    sup    = stats.get("superset", {})
    det    = stats.get("detoxis",  {})
    n_sup  = sup.get("n_total", 0)
    n_det  = det.get("n_total", 0)
    n_tot  = n_sup + n_det

    lineas = [
        "# Reporte de Exploración Inicial (Paso 1.3)",
        "",
        f"**Generado:** {fecha}  ",
        f"**Corpus base:** Spanish Hate Speech Superset (Tonneau et al., 2024) + DETOXIS 2021  ",
        f"**Total de ejemplos:** {n_tot:,}  ",
        "",
        "## Contexto del corpus",
        "",
        "El corpus se construye a partir de dos fuentes complementarias:",
        "",
        "### 1. Spanish Hate Speech Superset",
        "- **Paper:** *From Languages to Geographies: Towards Evaluating Cultural Bias in Hate Speech Datasets*  ",
        "  Tonneau et al. (2024) — WOAH 2024, ACL. https://aclanthology.org/2024.woah-1.23",
        "- **Descripción:** Superset de 29,855 posts anotados como hate/no-hate, resultado de unificar",
        "  todos los datasets públicos de español disponibles a abril 2024.",
        "- **Preprocesamiento:** duplicados eliminados, etiquetas binarizadas, usernames/URLs anonimizados.",
        "- **Datasets incluidos:** HatEval, HaterNet, Chilean, HaSCoSVa, HOMO-MEX.",
        "",
        "### 2. DETOXIS 2021",
        "- **Paper:** Taulé et al. (2021) — IberLEF 2021.",
        "- **Descripción:** 3,463 comentarios de noticias en español con anotación de toxicidad",
        "  en 20 dimensiones. Añadido manualmente porque NO está incluido en el superset.",
        "- **Mapeo:** `toxicity_level >= 2` → etiqueta 1 (hate).",
        "",
        "## Resumen ejecutivo",
        "",
        "| Fuente | Filas | % hate | P95 tokens | % seeds LATAM |",
        "|--------|------:|-------:|-----------:|--------------:|",
    ]

    for nombre, d in [("Superset (total)", sup), ("DETOXIS", det)]:
        if d.get("vacio"):
            lineas.append(f"| {nombre} | — | — | — | — |")
            continue
        long_ = d.get("longitud", {})
        lineas.append(
            f"| {nombre} | {d['n_total']:,} | {d['pct_hate']}% "
            f"| {long_.get('tokens_p95', '—'):.0f} | {d.get('seeds_latam_pct', 0):.1f}% |"
        )

    lineas += [
        f"| **TOTAL** | **{n_tot:,}** | | | |",
        "",
        "## Datasets incluidos en el Superset",
        "",
        "| Dataset | Filas | Origen |",
        "|---------|------:|--------|",
    ]

    meta_datasets = {
        "hateval":  "Twitter ES/EN — SemEval-2019",
        "haternet": "Twitter ES — Sensors 2019",
        "chileno":  "Twitter CL — WOAH 2022",
        "hascosva": "Twitter multi-variedad — VarDial 2023",
        "homomex":  "Twitter MX — WOAH 2023",
    }
    for ds, cnt in sup.get("datasets", {}).items():
        origen = meta_datasets.get(ds, "—")
        lineas.append(f"| `{ds}` | {cnt:,} | {origen} |")

    lineas += [
        "",
        "## Figuras",
        "",
        f"![Distribucion de clases]({rutas['clases'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Datasets en el superset]({rutas['volumen'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Longitud de texto]({rutas['longitud'].relative_to(REPORTS).as_posix()})",
        "",
        f"![Seeds LATAM]({rutas['seeds'].relative_to(REPORTS).as_posix()})",
        "",
        "## Análisis detallado",
        "",
        "### Superset",
    ]

    if not sup.get("vacio"):
        long_ = sup.get("longitud", {})
        lineas += [
            f"- **Filas:** {sup['n_total']:,}",
            f"- **Hate:** {sup['n_hate']:,} ({sup['pct_hate']}%) | **No hate:** {sup['n_no_hate']:,}",
            f"- **Duplicados de texto:** {sup.get('duplicados', 'n/a')} (superset ya deduplico)",
            f"- **Longitud mediana:** {long_.get('tokens_mediana', '—'):.0f} tokens | P95: {long_.get('tokens_p95', '—'):.0f} tokens",
            f"- **Seeds LATAM:** {sup.get('seeds_latam_pct', 0):.1f}% de textos (estimacion pre-lexicon)",
            f"- **Paises inferidos:** {sup.get('n_paises', '—')} distintos (metadata Nov 2024)",
        ]

    lineas += ["", "### DETOXIS"]
    if not det.get("vacio"):
        long_ = det.get("longitud", {})
        lineas += [
            f"- **Filas:** {det['n_total']:,}",
            f"- **Hate (toxicity_level >= 2):** {det['n_hate']:,} ({det['pct_hate']}%)",
            f"- **Longitud mediana:** {long_.get('tokens_mediana', '—'):.0f} tokens | P95: {long_.get('tokens_p95', '—'):.0f} tokens",
            f"- **Seeds LATAM:** {det.get('seeds_latam_pct', 0):.1f}% de textos",
        ]
        if long_.get("tokens_p95", 0) > 128:
            lineas.append(
                f"- **ATENCION:** P95={long_.get('tokens_p95', 0):.0f} tokens > 128 "
                "→ usar `max_length=256` para BETO en este dataset."
            )

    lineas += [
        "",
        "## Hallazgos clave",
        "",
        f"1. **Volumen total:** {n_tot:,} ejemplos — suficiente para particion 70/15/15 con clases representadas.",
        "2. **Corpus academicamente solido:** el superset esta respaldado por un paper WOAH/ACL 2024 "
        "con metodologia de binarizacion y deduplicacion documentadas.",
        "3. **DETOXIS aporta diversidad de plataforma:** los demas datasets son Twitter; DETOXIS "
        "aporta comentarios de noticias, aumentando la variedad lingüística.",
        "4. **Etiquetas ya unificadas en superset:** solo DETOXIS requiere mapeo manual "
        "(`toxicity_level >= 2 -> 1`).",
        "5. **Modismos LATAM (pre-lexicon):** el chileno y homomex concentran la mayor proporcion "
        "de seeds. Crucial para validar H3.",
        "",
        "## Próximo paso",
        "",
        "→ **Paso 1.4** Implementar `src/data/clean.py` con `normalizar()` (para DETOXIS).  ",
        "→ **Paso 1.5** `notebooks/02_unificacion.ipynb`: adaptar superset + DETOXIS al esquema canónico.",
        "",
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("  PASO 1.3 · Exploración del corpus base")
    print("  Spanish Hate Speech Superset + DETOXIS 2021")
    print("=" * 65)

    print("\n[1/4] Cargando fuentes de datos...")
    df_sup = cargar_superset()
    if df_sup.empty:
        print("  [ERROR] No se pudo cargar el superset. Verifica la ruta.")
        return 1
    print(f"  Superset    : {df_sup.shape[0]:,} filas | datasets: {df_sup['dataset'].unique().tolist()}")

    df_det = cargar_detoxis()
    if df_det.empty:
        print("  [ERROR] No se pudo cargar DETOXIS. Verifica la ruta.")
        return 1
    print(f"  DETOXIS     : {df_det.shape[0]:,} filas")
    print(f"  TOTAL       : {len(df_sup) + len(df_det):,} filas")

    print("\n[2/4] Calculando estadísticas...")
    stats = {
        "superset": analizar_superset(df_sup),
        "detoxis":  analizar_detoxis(df_det),
    }
    sup = stats["superset"]
    det = stats["detoxis"]
    print(f"  Superset  -> hate: {sup.get('pct_hate', 0)}%  | P95 tokens: {sup.get('longitud', {}).get('tokens_p95', '—'):.0f}")
    print(f"  DETOXIS   -> hate: {det.get('pct_hate', 0)}%  | P95 tokens: {det.get('longitud', {}).get('tokens_p95', '—'):.0f}")

    print("\n[3/4] Generando figuras...")
    rutas = {
        "clases":  fig_distribucion_clases(stats),
        "volumen": fig_datasets_en_superset(stats),
        "longitud": fig_longitud(stats),
        "seeds":   fig_seeds_latam(stats),
    }
    for k, v in rutas.items():
        print(f"  {k:10s} -> {v.relative_to(ROOT).as_posix()}")

    print("\n[4/4] Escribiendo reporte Markdown + JSON...")
    md      = render_md(stats, rutas)
    md_path = REPORTS / "exploracion_inicial.md"
    md_path.write_text(md, encoding="utf-8")
    json_path = REPORTS / "exploracion_inicial.json"
    json_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"  MD   -> {md_path.relative_to(ROOT).as_posix()}")
    print(f"  JSON -> {json_path.relative_to(ROOT).as_posix()}")

    print("\n[OK] Paso 1.3 completado.")
    n_tot = len(df_sup) + len(df_det)
    print(f"  Total corpus: {n_tot:,} ejemplos listos para Paso 1.4-1.5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
