# Especificación Técnica del Modelo

Detalles técnicos, configuración de entrenamiento y resultados del modelo BETO ajustado, que es el modelo que usa la API en producción (`models/beto_finetuned_final/`).

## Modelo base

- **Arquitectura:** BERT-base (12 capas, 12 cabezales de atención, dimensión oculta 768).
- **Parámetros:** ~110 millones.
- **Identificador Hugging Face:** `dccuchile/bert-base-spanish-wwm-cased`.
- **Preentrenamiento:** exclusivamente en español (Cañete et al., 2020).
- **Variante:** `cased` (preserva mayúsculas), elegida porque el discurso de odio explota patrones de mayúsculas que la variante `uncased` destruiría.

## Configuración de fine-tuning

| Parámetro | Valor |
|---|---|
| Corpus | `data/processed/corpus_v1_enriquecido.parquet` (32,987 ejemplos limpios tras deduplicar) |
| Particiones | 70% train (23,090) / 15% val (4,948) / 15% test (4,949) |
| Tamaño de batch | 16 (entrenamiento), 32 (evaluación) |
| Learning rate | 2e-5 (BETO y mBERT); 1e-5 para XLM-R |
| Épocas | 4, con early stopping (patience=2) |
| Class weights | Balanceados automáticamente vía `sklearn.utils.class_weight` |
| Longitud máxima | 128 tokens |
| Optimizador | AdamW (por defecto en `Trainer` de Hugging Face) |
| Métrica de selección del mejor checkpoint | F1 de la clase `hate` |
| Semillas de entrenamiento | 42, 123, 2024 (se reporta media ± desviación estándar) |

Semilla seleccionada para el modelo final: **123** (mayor F1 hate entre las tres corridas de BETO).

## Resultados finales (test set, fuente: `EXPERIMENTOS.md` y `reports/tables/comparativa_global.csv`)

| Modelo | Precision (hate) | Recall (hate) | F1 (hate) | F1 macro | Accuracy | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| BETO base (sin fine-tuning) | 0.1880 | 0.0416 | 0.0682 | 0.4587 | 0.7404 | 0.5148 |
| **BETO ajustado (final)** | 0.6772 ± 0.0220 | 0.6859 ± 0.0241 | **0.6810 ± 0.0049** | 0.7929 ± 0.0037 | 0.8534 ± 0.0053 | 0.8912 ± 0.0040 |
| mBERT | 0.6090 ± 0.0564 | 0.7018 ± 0.0816 | 0.6474 ± 0.0058 | 0.7657 ± 0.0045 | 0.8259 ± 0.0161 | 0.8703 ± 0.0068 |
| XLM-R | 0.6272 ± 0.0034 | 0.7148 ± 0.0128 | 0.6681 ± 0.0063 | 0.7805 ± 0.0036 | 0.8380 ± 0.0020 | 0.8881 ± 0.0037 |

Significancia (test de McNemar, ver `reports/tables/mcnemar_results.csv`):

- BETO ajustado vs. BETO base: diferencia muy significativa (p = 1.71e-62).
- BETO vs. mBERT: BETO gana con diferencia significativa (p = 1.78e-11).
- BETO vs. XLM-R: sin diferencia estadísticamente significativa (p = 0.1174) — resultados competitivos entre ambos.

Para el detalle completo de hipótesis, análisis de modismos (H3) y XAI, ver `docs/resultados.md`.

## Dispositivo de entrenamiento e inferencia

- **Entrenamiento:** Google Colab con GPU T4 (el fine-tuning completo de Transformers no es práctico en CPU).
- **Inferencia (API en producción):** se ejecuta tanto en CPU como GPU; el dispositivo se detecta automáticamente (`torch.cuda.is_available()`).
