# Bitácora de Decisiones Experimentales

Este archivo registra todas las decisiones metodológicas, hiperparámetros y corridas experimentales del proyecto. Sirve como referencia en la defensa de la tesis.

## Metadata del entorno

**Fecha de inicio:** [COMPLETAR]
**Investigador:** [Nombre del tesista]
**Director:** [Nombre del director]
**Versión de código:** [commit hash]

### Entorno de hardware

- **SO:** Windows 10 / Linux / macOS
- **GPU:** [CUDA version si aplica / CPU]
- **RAM:** [GB]
- **Python:** 3.10
- **PyTorch:** [versión]
- **Transformers:** 4.40+

---

## Decisiones previas al experimento

### Unificación de etiquetas

| Dataset | Etiqueta original | Etiqueta unificada | Notas |
|---------|-------------------|--------------------|-------|
| HatEval | HS=1 | 1 | Hate |
| HatEval | HS=0 | 0 | No hate |
| [Agregar otros] | | | |

### Lexicón LATAM

**Versión:** modismos_latam_v1.csv
**Tamaño:** [N] términos
**Cobertura en corpus:** [%] con `tiene_modismo=True`
**Fecha de construcción:** [FECHA]
**Validación manual:** [Precision/Recall del flag]

### Particiones

**Corpus version:** corpus_v1_enriquecido.parquet
**Tamaño total:** [N] ejemplos
**Train/Val/Test:** 70% / 15% / 15%
**Estratificación:** por `etiqueta`
**Random seed:** 42

---

## Corridas de entrenamiento

### BETO ajustado

#### Semilla 42

```
Fecha: [FECHA-HORA]
GPU: [SI/NO]
Tiempo total: [min]
Hiperparámetros:
  - learning_rate: 2e-5
  - batch_size: 16
  - num_epochs: 4
  - max_length: 128
  - class_weights: balanced
  - early_stopping_patience: 2

Métricas en VAL:
  - F1 (hate): 0.XX
  - Accuracy: 0.XX

Métricas en TEST (nunca mirar antes de final):
  - Precision (hate): 0.XX
  - Recall (hate): 0.XX
  - F1 (hate): 0.XX
  - F1 macro: 0.XX

Checkpoint seleccionado: beto_finetuned_42/checkpoint-XXX
```

#### Semilla 123

[Completar igual]

#### Semilla 2024

[Completar igual]

---

### mBERT baseline

[Igual estructura que BETO]

---

### XLM-R baseline

[Igual estructura que BETO, notar LR diferente si aplica]

---

## Análisis de errores

### BETO ajustado - Falsos positivos (ejemplos representativos)

| Texto | Predicción | Real | Categoría de error | Notas |
|-------|-----------|------|-------------------|-------|
| [Ejemplo] | hate | no_hate | Sarcasmo | Frase aparentemente ofensiva pero es irónica |
| | | | | |

### BETO ajustado - Falsos negativos (ejemplos representativos)

| Texto | Predicción | Real | Categoría de error | Notas |
|-------|-----------|------|-------------------|-------|
| [Ejemplo] | no_hate | hate | Modismo no capturado | Insulto regional poco frecuente |
| | | | | |

---

## Análisis de modismos (H3)

### Subconjuntos

| Métrica | Con modismos | Sin modismos | Diferencia |
|---------|-------------|-------------|-----------|
| F1 (BETO ajustado) | 0.XX | 0.XX | +0.XX |
| F1 (mBERT) | 0.XX | 0.XX | +0.XX |
| F1 (XLM-R) | 0.XX | 0.XX | +0.XX |

**Prueba estadística:** [McNemar p-valor]
**Conclusión H3:** [Aceptada / Rechazada / Parcialmente aceptada]

---

## XAI - Casos representativos

### Ejemplo 1: Predicción correcta con modismos

```
Texto: "[Ejemplo]"
Etiqueta: hate
Probabilidad: 0.93

Tokens principales:
  - "pinche" (peso: +0.42)
  - "USUARIO" (peso: -0.05)
  - "odio" (peso: +0.55)

Observación: Los tokens destacados son lingüísticamente plausibles.
```

### Ejemplo 2: Falso positivo interesante

[Similar]

---

## Comparación final (Tabla de resultados)

| Modelo | Precision | Recall | F1 | F1 macro | Accuracy | ROC-AUC |
|--------|-----------|--------|-----|----------|----------|---------|
| BETO base | 0.XX±Y | 0.XX±Y | 0.XX | 0.XX | 0.XX | 0.XX |
| **BETO ajustado** | **0.XX±Y** | **0.XX±Y** | **0.XX** | **0.XX** | **0.XX** | **0.XX** |
| mBERT | 0.XX±Y | 0.XX±Y | 0.XX | 0.XX | 0.XX | 0.XX |
| XLM-R | 0.XX±Y | 0.XX±Y | 0.XX | 0.XX | 0.XX | 0.XX |

### Tests de significancia (McNemar)

| Comparación | p-valor | Significativo (α=0.05) | Conclusión |
|-------------|---------|------------------------|------------|
| BETO ajustado vs BETO base | 0.XXX | Sí/No | [Texto] |
| BETO ajustado vs mBERT | 0.XXX | Sí/No | [Texto] |
| BETO ajustado vs XLM-R | 0.XXX | Sí/No | [Texto] |

---

## Validación de hipótesis

### H1: BETO ajustado > BETO base

**Métrica:** F1 (hate)
**BETO ajustado:** 0.XX [0.XX, 0.XX] (IC 95% bootstrap)
**BETO base:** 0.XX [0.XX, 0.XX]
**Diferencia:** +0.XX
**p-valor McNemar:** 0.XXX
**Conclusión:** [ACEPTADA / RECHAZADA]

### H2: BETO ajustado ≥ mBERT y XLM-R

[Similar]

### H3: Mejor en con_modismos que sin_modismos

[Similar]

---

## Decisiones durante la investigación

(Registra cambios sobre la marcha: si cambió max_length, si se agregaron términos al lexicón, si se reentrena algo, etc.)

**Decisión 1:** [Fecha] - [Descripción] - [Justificación]

---

## Observaciones y lecciones aprendidas

[Al finalizar, anotar qué funcionó bien, qué no, y qué se haría diferente.]
