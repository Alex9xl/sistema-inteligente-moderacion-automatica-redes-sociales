# Especificación Técnica del Modelo

Detalles técnicos, configuración y metadatos del modelo BETO ajustado.

## Modelo base

- **Arquitectura:** BERT-base (12 capas, 12 cabezales, dim 768)
- **Parámetros:** ~110 M
- **Identificador Hugging Face:** `dccuchile/bert-base-spanish-wwm-cased`
- **Preentrenamiento:** Español exclusivamente
- **Variante:** Cased (preserva mayúsculas)

## Fine-tuning

- **Corpus:** corpus_v1_enriquecido.parquet (~38k ejemplos)
- **Particiones:** 70% train / 15% val / 15% test
- **Tamaño de batch:** 16 (train), 32 (eval)
- **Learning rate:** 2e-5
- **Épocas:** 4
- **Early stopping:** patience=2
- **Class weights:** Balanceados por sklearn
- **Max length:** 128 tokens
- **Optimizador:** AdamW (por defecto en Trainer)

## Entrenamiento reproducible

- **Semillas:** 42, 123, 2024
- **Métrica de selección:** F1 (clase hate)
- **Dispositivo:** GPU/CPU (controlado automáticamente)

## Resultados esperados

Ver `EXPERIMENTOS.md` para métricas reales tras entrenamiento.
