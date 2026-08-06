# Flujo Completo del Proyecto

Descripción end-to-end del pipeline del proyecto: desde los datos crudos hasta la extensión de navegador en funcionamiento. Este documento es un resumen operativo; la especificación metodológica completa está en `documentos_extras/INSTRUCCIONES_PROYECTO.md` y los pasos de reproducción exactos en `documentos_extras/GUIA_REPRODUCCION.md`.

## Resumen visual

```text
data/raw/ (2 datasets)
      │
      ▼
Exploración inicial ──► data/reports_qc/exploracion_inicial.md
      │
      ▼
clean.py → unify.py ──► data/interim/corpus_combinado.parquet
      │
      ▼
lexicon.py (modismos LATAM, rol observacional)
      │
      ▼
enrich.py ──► data/processed/corpus_v1_enriquecido.parquet
      │
      ▼
qc.py → split.py ──► train/val/test.parquet + MANIFEST.json
      │
      ▼
[Google Colab, GPU] train_model.py ──► modelos entrenados (models/)
      │
      ▼
evaluate_model.py ──► métricas, bootstrap, McNemar, H3, XAI (reports/)
      │
      ▼
models/beto_finetuned_final ──► src/api/main.py (FastAPI)
      │
      ▼
extension/ (Chrome/Edge) ──► consume la API en tiempo real
```

## 1. Datos crudos (`data/raw/`)

El corpus parte de dos fuentes públicas de discurso de odio en español:

| Fuente | Archivo | Filas |
|---|---|---:|
| Spanish Hate Speech Superset (Tonneau et al., 2024) | `spanish-hate-speech-superset/es_hf_102024.csv` | 29,855 |
| DETOXIS 2021 (IberLEF) | `DETOXIS_2021-main/data/DATASET_DETOXIS.csv` | 3,463 |

Cada fuente trae su propio esquema de etiquetas. El primer paso es verificar que existan e íntegras con `data/raw/analisis_dataset/verificar_corpus.py` y `verificar_datasets_detoxis.py`.

## 2. Exploración inicial

`scripts/exploracion_inicial.py` genera un diagnóstico antes de procesar nada: distribución de clases, volumen por dataset, longitud de textos y cobertura preliminar de modismos LATAM.

Salidas: `data/reports_qc/exploracion_inicial.md`, `exploracion_inicial.json` y figuras en `data/reports_qc/figuras/`.

## 3. Construcción del corpus (`src/data/`)

Seis sub-pasos secuenciales:

1. **Limpieza** (`clean.py`) — normaliza texto. Solo se aplica a DETOXIS; el superset conserva su preprocesamiento original.
2. **Unificación** (`unify.py`) — combina ambas fuentes bajo un esquema binario común (`hate` / `no_hate`). Mapeo: en DETOXIS, `toxicity_level >= 2` → `1`. Salida: `data/interim/corpus_combinado.parquet`.
3. **Lexicón LATAM** (`lexicon.py`) — carga los 383 términos canónicos (886 tokens con variantes) de `data/lexicons/modismos_latam_v1.csv`. Rol **observacional**: no se inyecta al modelo como feature, solo permite marcar después qué textos contienen modismos (para la Hipótesis 3).
4. **Enriquecimiento** (`enrich.py`) — agrega la columna `tiene_modismo` al corpus. Salida: `data/processed/corpus_v1_enriquecido.parquet` (~33k ejemplos antes de deduplicar, ~32,987 después).
5. **Control de calidad** (`qc.py`) — valida duplicados, balance de clases y consistencia. Salida: `data/reports_qc/qc_corpus_v1.md`.
6. **Particionado** (`split.py`) — separa en train (70%), val (15%) y test (15%), estratificado por clase, verificando que no haya *leakage* entre splits.

Al final, `scripts/crear_manifest.py` genera `data/processed/MANIFEST.json` con hashes SHA-256 de cada artefacto (trazabilidad), y `scripts/generar_reporte_qc_final.py` genera `data/reports_qc/qc_corpus_v1_final.md`.

## 4. Entrenamiento (Google Colab, GPU)

Este paso no corre localmente porque requiere GPU. Flujo:

1. Subir a Google Drive los `.parquet` procesados junto con `scripts/train_model.py` y `scripts/evaluate_model.py`.
2. Ejecutar `notebooks/colab_entrenamiento_evaluacion_xai.ipynb` con GPU T4.
3. Se entrenan 3 arquitecturas, cada una con 3 semillas (42, 123, 2024) para poder promediar resultados de forma estadísticamente robusta:
   - **BETO** (`dccuchile/bert-base-spanish-wwm-cased`) — modelo principal del proyecto.
   - **mBERT** (`bert-base-multilingual-cased`) — baseline multilingüe.
   - **XLM-R** (`xlm-roberta-base`) — baseline multilingüe.
4. Hiperparámetros de BETO: batch 16 (train) / 32 (eval), learning rate 2e-5 (1e-5 para XLM-R), 4 épocas, early stopping (patience=2), max length 128 tokens, class weights balanceados (`sklearn`), optimizador AdamW.
5. Se entrena también BETO base sin fine-tuning (3 celdas extra del notebook), necesario para sustentar la Hipótesis 1 (comparación BETO ajustado vs. BETO sin ajustar).
6. El mejor BETO ajustado por F1 en validación se guarda como `models/beto_finetuned_final/` — es el modelo que usa la API en producción.

Salidas: los 10 modelos entrenados en `models/`, más tablas en `reports/tables/` (métricas, intervalos de confianza bootstrap, test de McNemar, análisis H3 por modismos, análisis XAI).

## 5. Explicabilidad (XAI)

`src/xai/shap_explainer.py` aplica SHAP sobre `models/beto_finetuned_final` para identificar qué tokens influyeron en cada predicción. Alimenta el endpoint `/explain` de la API.

## 6. Backend (API REST)

`src/api/main.py` (FastAPI) carga el modelo final una sola vez (`lifespan`) y expone:

| Endpoint | Método | Función |
|---|---|---|
| `/health` | GET | Verifica que el modelo está cargado. |
| `/metadata` | GET | Versión, umbral activo y configuración. |
| `/predict` | POST | Clasifica un texto (`hate` / `no_hate` + probabilidad). |
| `/explain` | POST | Clasifica y explica con SHAP (tokens + pesos). |

La API aplica su propio **umbral interno** (`threshold` en `src/api/config.py`, por defecto `0.5`) sobre la probabilidad devuelta por el modelo para decidir la etiqueta.

## 7. Cliente (extensión de navegador)

La extensión (Manifest V3) consume la API mientras el usuario navega:

- El *content script* detecta texto en la página (comentarios, posts, etc.).
- Lo envía a `/predict`; si la API está desactivada o no responde, cae en modo degradado y usa el **lexicón personal local** del usuario como respaldo (nunca sale del navegador).
- Aplica un **umbral configurable por el usuario** desde la página de opciones (rango 0.3–0.95, por defecto 0.7). Este es un segundo filtro, independiente del umbral interno de la API, para que el usuario ajuste su propia sensibilidad de detección.
- Censura o resalta visualmente el contenido detectado según el modo configurado.

No confundir el **Lexicón LATAM** (científico, usado solo para evaluación offline) con el **lexicón personal** (producto, configurado por el usuario en la extensión). Ver `docs/glosario.md`.

## 8. Pruebas

- `pytest` corre los tests unitarios e de integración del pipeline Python (datos, API, XAI).
- `node --check` valida la sintaxis de los archivos `.js` de la extensión (`content.js`, `background.js`, `api.js`, `popup.js`, `options.js`).

## Referencias

- Especificación metodológica completa: `documentos_extras/INSTRUCCIONES_PROYECTO.md`.
- Plan de construcción desde cero: `documentos_extras/PLAN_DESARROLLO.md`.
- Pasos exactos de reproducción: `documentos_extras/GUIA_REPRODUCCION.md`.
- Bitácora de resultados y decisiones experimentales reales: `EXPERIMENTOS.md`.
- Arquitectura y capas del sistema: `docs/arquitectura.md`.
