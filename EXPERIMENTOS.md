# Bitacora de Decisiones Experimentales

Este archivo registra las decisiones metodologicas y los resultados finales del
proyecto. Version de cierre local: v1.0, 2026-07-01.

## Metadata del entorno

- Investigador: pendiente de completar con datos personales del tesista.
- Director: pendiente de completar con datos formales de asesoria.
- Git HEAD al momento de generar el manifiesto: `a73af1b6a958672453f5486eab73d640d420c0db`.
- Entorno local de verificacion: Windows, Python 3.14.1, torch 2.12.0+cpu,
  transformers 4.57.6, pandas 3.0.3.
- Entorno de entrenamiento: modelos entrenados previamente en Google Colab/GPU,
  segun los artefactos guardados en `models/`.

## Decisiones de datos

### Corpus base

Se usa el Spanish Hate Speech Superset (Tonneau et al., 2024) como base principal
del corpus, complementado con DETOXIS 2021.

| Fuente | Archivo | Filas | Uso |
| --- | --- | ---: | --- |
| Spanish Hate Speech Superset v2024 | `data/raw/spanish-hate-speech-superset/es_hf_102024.csv` | 29,855 | Base principal |
| DETOXIS 2021 | `data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv` | 3,463 | Complemento de comentarios de noticias |

Justificacion:

- El superset ya trae binarizacion, deduplicacion y documentacion academica.
- DETOXIS no esta incluido en el superset y aporta diversidad de plataforma.
- El esquema final se mantiene binario: `hate` / `no_hate`.

### Mapeo de etiquetas

| Fuente | Etiqueta original | Etiqueta unificada |
| --- | --- | --- |
| Superset | `labels` binaria | `0/1` |
| DETOXIS | `toxicity_level >= 2` | `1` |
| DETOXIS | `toxicity_level < 2` | `0` |

### Corpus procesado

- Archivo: `data/processed/corpus_v1_enriquecido.parquet`.
- SHA-256: `4a76b4005244ce454a08dc2c1580807bc2876e911f236e2ad2bc779e799c9c3c`.
- Total antes de deduplicacion: 33,318 ejemplos.
- Hate: 7,603 (22.8%).
- No hate: 25,715 (77.2%).
- Duplicados exactos eliminados: 217.
- Duplicados normalizados eliminados: 114.
- Corpus limpio para splits: 32,987 ejemplos.

### Splits

| Split | Archivo | Filas | Proporcion | % hate | SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| Train | `data/processed/train.parquet` | 23,090 | 70% | 22.8% | `24150e7edac3bcbf167c6183941997e936acdf1f14f425be95545b5ad7db7fc8` |
| Val | `data/processed/val.parquet` | 4,948 | 15% | 22.8% | `99445ea7397cdbe36d6fa4dae31a7bb479523b05417157df1b4864a303853cfc` |
| Test | `data/processed/test.parquet` | 4,949 | 15% | 22.8% | `f07165adca005065e9a9e65f6385a8670fe61edfe3d23ecca700278c0fbaa59b` |

Leakage check: train-val 0, train-test 0, val-test 0.

## Lexicon LATAM

- Archivo: `data/lexicons/modismos_latam_v1.csv`.
- SHA-256: `3402e01cd60547ac0df981d3f72f0be02abf4d2fc3abc13cd955a729546d7dee`.
- Terminos canonicos: 383.
- Tokens efectivos incluyendo variantes: 886.
- Rol metodologico: observacional. Se usa para marcar `tiene_modismo` y segmentar
  la evaluacion de H3; no se inyecta como feature al modelo.

Distribucion por pais/categoria geografica:

| Pais | Terminos |
| --- | ---: |
| MULTI | 173 |
| AR | 56 |
| CL | 41 |
| MX | 37 |
| CO | 25 |
| PE | 21 |
| VE | 19 |
| EC | 11 |

Nota metodologica: el requisito inicial de 500 terminos canonicos fue ajustado
porque el esquema agrupa variantes por fila; 383 entradas producen 886 tokens
efectivos y la cobertura supera el umbral operativo del proyecto.

## Entrenamiento

Modelos entrenados con tres semillas:

- BETO: `models/beto_finetuned_42`, `models/beto_finetuned_123`,
  `models/beto_finetuned_2024`.
- mBERT: `models/mbert_finetuned_42`, `models/mbert_finetuned_123`,
  `models/mbert_finetuned_2024`.
- XLM-R: `models/xlmr_finetuned_42`, `models/xlmr_finetuned_123`,
  `models/xlmr_finetuned_2024`.

Modelo final empaquetado:

- Directorio: `models/beto_finetuned_final`.
- Modelo base: `dccuchile/bert-base-spanish-wwm-cased`.
- Semilla seleccionada: 123.
- Criterio: mayor F1 hate entre las semillas BETO.
- Archivo principal: `models/beto_finetuned_final/model.safetensors`.
- SHA-256 modelo: `c9409f7a28183aa4f9fbadd94dc189d0b15ed47b84b08cb9aa83f2c4ce08e168`.
- Model card: `models/beto_finetuned_final/model_card.md`.

## Resultados globales

Fuente: `reports/tables/comparativa_global.csv`.

| Modelo | Precision hate | Recall hate | F1 hate | F1 macro | Accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BETO ajustado | 0.6772 +/- 0.0220 | 0.6859 +/- 0.0241 | 0.6810 +/- 0.0049 | 0.7929 +/- 0.0037 | 0.8534 +/- 0.0053 | 0.8912 +/- 0.0040 |
| mBERT | 0.6090 +/- 0.0564 | 0.7018 +/- 0.0816 | 0.6474 +/- 0.0058 | 0.7657 +/- 0.0045 | 0.8259 +/- 0.0161 | 0.8703 +/- 0.0068 |
| XLM-R | 0.6272 +/- 0.0034 | 0.7148 +/- 0.0128 | 0.6681 +/- 0.0063 | 0.7805 +/- 0.0036 | 0.8380 +/- 0.0020 | 0.8881 +/- 0.0037 |

Resultados por semilla: `reports/tables/metrics_all_models.csv`.
Intervalos bootstrap: `reports/tables/bootstrap_ic.csv`.

### Mejor BETO por semilla

| Semilla | Precision hate | Recall hate | F1 hate | F1 macro | Accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.6524 | 0.7130 | 0.6813 | 0.7907 | 0.8478 | 0.8941 |
| 123 | 0.6942 | 0.6776 | 0.6858 | 0.7972 | 0.8584 | 0.8866 |
| 2024 | 0.6852 | 0.6670 | 0.6759 | 0.7909 | 0.8541 | 0.8930 |

## Significancia estadistica

Fuente: `reports/tables/mcnemar_results.csv`.

| Comparacion | Semilla | p-valor | Significativo alpha=0.05 | Lectura |
| --- | ---: | ---: | --- | --- |
| BETO vs mBERT | 42 | 1.7806e-11 | Si | BETO supera a mBERT con diferencia pareada significativa. |
| BETO vs XLM-R | 42 | 0.1174 | No | BETO no difiere significativamente de XLM-R en esta prueba. |
| mBERT vs XLM-R | 42 | 2.2162e-07 | Si | XLM-R supera a mBERT de forma significativa. |

## Analisis de modismos H3

Fuente: `reports/tables/h3_idiom_analysis/`.

Segmentacion de test:

| Subconjunto | Total | Hate | No hate | % hate |
| --- | ---: | ---: | ---: | ---: |
| Con modismos | 2,686 | 848 | 1,838 | 31.57% |
| Sin modismos | 2,263 | 281 | 1,982 | 12.42% |

Evaluacion BETO:

| Subconjunto | Precision | Recall | F1 | Accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Con modismos | 0.6902 | 0.7854 | 0.7347 | 0.8209 | 0.8968 |
| Sin modismos | 0.5167 | 0.4947 | 0.5055 | 0.8798 | 0.8523 |

Validacion:

- Delta F1 observado: +0.2292.
- Delta F1 bootstrap mean: +0.2300.
- IC bootstrap delta F1: [0.1738, 0.2889].
- p-value permutacion: 0.000999.
- H3 soportada: si.

## XAI

Artefactos:

- `reports/tables/xai_analysis/shap_analysis_results.csv`.
- `reports/tables/xai_analysis/shap_modismo_tokens.csv`.
- `reports/tables/xai_analysis/shap_wrong_predictions.csv`.
- `reports/tables/xai_analysis/shap_full_weights.json`.

Lectura metodologica:

- SHAP se usa para inspeccion cualitativa de tokens relevantes.
- Se observan falsos positivos asociados a insultos o marcadores politicos en
  contextos ironicos/no dirigidos.
- La explicabilidad es soporte interpretativo, no criterio unico de validez.

## Backend y extension

Backend:

- Codigo: `src/api`.
- Endpoints: `/health`, `/metadata`, `/predict`, `/explain`.
- Verificacion local: `from src.api.main import app` devuelve `Hate Speech ES API`.
- El backend opera en modo degradado si no encuentra el directorio del modelo.

Extension:

- Directorio: `extension`.
- Version manifest: `1.0.0`.
- Comportamiento: API BETO local prioritaria; lexicon local como respaldo si API
  esta desactivada, caida o sin modelo cargado.
- Modos de censura: resaltar, difuminar, asteriscos, ocultar.
- Test estatico de extension: `tests/unit/test_extension_static.py`.

## Validacion de hipotesis

### H1: BETO ajustado > BETO base

Estado: evidencia incompleta en los artefactos finales disponibles.

La comparativa final contiene BETO ajustado, mBERT y XLM-R, pero no incluye una
tabla separada de BETO base sin fine-tuning. Por rigor metodologico, H1 no debe
declararse aceptada estadisticamente hasta incorporar ese baseline o justificar
formalmente su ausencia en el informe.

### H2: BETO ajustado >= mBERT y XLM-R

Estado: parcialmente soportada.

- BETO ajustado supera a mBERT en F1 hate promedio y McNemar semilla 42 es
  significativo.
- BETO ajustado supera a XLM-R en F1 hate promedio, pero McNemar semilla 42 no
  muestra diferencia significativa (`p=0.1174`).
- Lectura recomendada: BETO ajustado supera a mBERT e iguala competitivamente a
  XLM-R en el protocolo final.

### H3: BETO ajustado mejora en subconjunto con modismos

Estado: soportada.

- F1 con modismos: 0.7347.
- F1 sin modismos: 0.5055.
- Delta F1: +0.2292.
- p-value permutacion: 0.000999.

## Verificaciones de cierre

Ejecutadas localmente el 2026-07-01:

- `python -m pytest`: 15 passed.
- `node --check extension/content.js`: OK.
- `node --check extension/background.js`: OK.
- `node --check extension/api.js`: OK.
- `node --check extension/popup/popup.js`: OK.
- `node --check extension/options/options.js`: OK.
- `node --check extension/lexicon.js`: OK.
- `git diff --check`: sin errores de whitespace; solo avisos CRLF esperados en Windows.

## Decisiones finales

- Se congela la extension como v1.0 con API BETO prioritaria.
- Se mantiene el lexicon personal/local como respaldo de producto, separado del
  lexicon LATAM de investigacion.
- Se documenta explicitamente la limitacion de H1 por ausencia de baseline BETO
  base en las tablas finales disponibles.
- La parte Git/GitHub queda para ejecucion manual del usuario: commit, tag y push.
