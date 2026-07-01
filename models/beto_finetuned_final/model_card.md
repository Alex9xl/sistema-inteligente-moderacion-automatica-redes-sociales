# BETO fine-tuned final

## Identificacion

- Proyecto: Sistema inteligente de moderacion automatica de discurso de odio en espanol.
- Modelo base: `dccuchile/bert-base-spanish-wwm-cased`.
- Tarea: clasificacion binaria `hate` / `no_hate`.
- Directorio: `models/beto_finetuned_final/`.
- Version de cierre: v1.0.
- Fecha de cierre local: 2026-07-01.

## Datos

- Corpus: `data/processed/corpus_v1_enriquecido.parquet`.
- Fuentes: Spanish Hate Speech Superset v2024 + DETOXIS 2021.
- Total antes de deduplicacion: 33,318 ejemplos.
- Total despues de deduplicacion: 32,987 ejemplos.
- Splits: train 23,090 / val 4,948 / test 4,949.
- Lexicon LATAM: `data/lexicons/modismos_latam_v1.csv`.
- Uso del lexicon LATAM: variable observacional `tiene_modismo`, no feature de entrenamiento.

## Resultados en test

Promedio de tres semillas BETO (`42`, `123`, `2024`):

| Metrica | Media | Std |
| --- | ---: | ---: |
| Precision hate | 0.6772 | 0.0220 |
| Recall hate | 0.6859 | 0.0241 |
| F1 hate | 0.6810 | 0.0049 |
| F1 macro | 0.7929 | 0.0037 |
| Accuracy | 0.8534 | 0.0053 |
| ROC-AUC | 0.8912 | 0.0040 |

Mejor semilla por F1 hate: `123`.

| Semilla | Precision hate | Recall hate | F1 hate | F1 macro | Accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.6524 | 0.7130 | 0.6813 | 0.7907 | 0.8478 | 0.8941 |
| 123 | 0.6942 | 0.6776 | 0.6858 | 0.7972 | 0.8584 | 0.8866 |
| 2024 | 0.6852 | 0.6670 | 0.6759 | 0.7909 | 0.8541 | 0.8930 |

## Analisis H3

Sobre la semilla BETO evaluada para modismos:

| Subconjunto | n | F1 | Accuracy | ROC-AUC |
| --- | ---: | ---: | ---: | ---: |
| Con modismos | 2,686 | 0.7347 | 0.8209 | 0.8968 |
| Sin modismos | 2,263 | 0.5055 | 0.8798 | 0.8523 |

- Delta F1 observado: +0.2292.
- IC bootstrap delta F1: [0.1738, 0.2889].
- p-value permutacion: 0.000999.
- Conclusion: H3 soportada en esta evaluacion.

## Comparacion estadistica pareada

McNemar semilla 42:

| Comparacion | p-value | Significativo alpha=0.05 |
| --- | ---: | --- |
| BETO vs mBERT | 1.7806e-11 | Si |
| BETO vs XLM-R | 0.1174 | No |
| mBERT vs XLM-R | 2.2162e-07 | Si |

## Limitaciones

- El sistema es binario y no clasifica subtipos de odio.
- La extension v1.0 es demostrativa local; no esta pensada como servicio productivo.
- SHAP se carga de forma lazy y puede degradar a pesos neutros si el entorno no soporta la explicacion.
- Los resultados dependen del corpus publico y de sus decisiones de etiquetado.

## Artefactos requeridos

- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`
- `special_tokens_map.json`
- `vocab.txt`
- `training_args.bin`
