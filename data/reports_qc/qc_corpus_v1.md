# Reporte QC — Corpus v1 Enriquecido

**Generado automáticamente por `src/data/qc.py`**

---

## 1. Tamaño del corpus

| Métrica | Valor |
|---------|-------|
| Total filas | **33,318** |
| Hate (1) | 7,603 (22.8%) |
| No hate (0) | 25,715 (77.2%) |
| Archivo fuente | `corpus_v1_enriquecido.parquet` |
| Tamaño en disco | 3,623.6 KB |
| SHA-256 | `4a76b4005244ce454a08dc2c1580807bc2876e911f236e2ad2bc779e799c9c3c` |

## 2. Distribución de clases por dataset

| Dataset | Total | Hate | No hate | % Hate |
|---------|-------|------|---------|--------|
| chileno | 9,500 | 599 | 8,901 | 6.3% |
| detoxis | 3,463 | 338 | 3,125 | 9.8% |
| hascosva | 3,994 | 554 | 3,440 | 13.9% |
| haternet | 5,999 | 1,567 | 4,432 | 26.1% |
| hateval | 6,595 | 2,735 | 3,860 | 41.5% |
| homomex | 304 | 304 | 0 | 100.0% |
| misocorpus | 3,463 | 1,506 | 1,957 | 43.5% |

## 3. Distribución de `tiene_modismo`

### 3.1 Global

| | Valor | % |
|---|---|---|
| Con modismo | 17,722 | 53.2% |
| Sin modismo | 15,596 | 46.8% |

### 3.2 Cruzada (etiqueta × tiene_modismo)

```
tiene_modismo  con_modismo  sin_modismo    All
etiqueta                                      
hate                  5711         1892   7603
no_hate              12011        13704  25715
All                  17722        15596  33318
```

> **Observación:** El 75.1% de las instancias *hate* contienen modismos LATAM
> vs 46.7% de las *no_hate*. Diferencia relevante para H3.

## 4. Longitud de texto

| Métrica | Tokens | Caracteres |
|---------|--------|------------|
| Mediana | 20 | 113 |
| P95 | 50 | 283 |
| Máximo | 556 | 3270 |
| Mínimo (tokens) | 1 | — |

> Textos con < 3 tokens (descartables): **141**
> P95 ≤ 128 tokens → `max_length=128` es suficiente para tokenización BERT.

## 5. Duplicados

| Nivel | Duplicados encontrados |
|-------|------------------------|
| Exactos (texto idéntico) | 217 |
| Normalizados (sin puntuación/emojis, lowercase) | 341 |

> ⚠ Existen duplicados — considerar eliminación antes del entrenamiento.

## 6. Top 30 unigramas por clase (sanity check)

### Clase: hate

| Posición | Unigrama | Frecuencia |
|----------|----------|------------|
| 1 | user | 7,032 |
| 2 | que | 6,085 |
| 3 | los | 2,739 |
| 4 | link | 1,740 |
| 5 | por | 1,530 |
| 6 | una | 1,399 |
| 7 | con | 1,375 |
| 8 | las | 1,350 |
| 9 | puta | 1,187 |
| 10 | para | 1,034 |
| 11 | como | 863 |
| 12 | eres | 800 |
| 13 | del | 782 |
| 14 | son | 739 |
| 15 | pero | 725 |
| 16 | más | 683 |
| 17 | perra | 500 |
| 18 | feminazis | 474 |
| 19 | ser | 462 |
| 20 | porque | 435 |
| 21 | mierda | 432 |
| 22 | subnormal | 396 |
| 23 | hay | 394 |
| 24 | eso | 388 |
| 25 | callate | 377 |
| 26 | feminazi | 373 |
| 27 | todos | 367 |
| 28 | cállate | 353 |
| 29 | todo | 351 |
| 30 | les | 351 |

### Clase: no_hate

| Posición | Unigrama | Frecuencia |
|----------|----------|------------|
| 1 | que | 22,264 |
| 2 | user | 20,019 |
| 3 | los | 10,148 |
| 4 | link | 8,240 |
| 5 | por | 6,310 |
| 6 | con | 5,246 |
| 7 | las | 4,524 |
| 8 | una | 4,487 |
| 9 | para | 4,126 |
| 10 | del | 3,832 |
| 11 | como | 3,095 |
| 12 | pero | 2,884 |
| 13 | más | 2,626 |
| 14 | son | 2,555 |
| 15 | puta | 1,881 |
| 16 | hay | 1,623 |
| 17 | ser | 1,525 |
| 18 | porque | 1,359 |
| 19 | eso | 1,332 |
| 20 | todo | 1,301 |
| 21 | este | 1,257 |
| 22 | cuando | 1,147 |
| 23 | todos | 1,129 |
| 24 | sin | 1,096 |
| 25 | esta | 1,079 |
| 26 | qué | 1,078 |
| 27 | les | 1,078 |
| 28 | sus | 1,071 |
| 29 | mujeres | 1,017 |
| 30 | gente | 1,002 |

## 7. Top 30 bigramas por clase

### Clase: hate

| Posición | Bigrama | Frecuencia |
|----------|---------|------------|
| 1 | user user | 2,558 |
| 2 | las feminazis | 235 |
| 3 | user cállate | 223 |
| 4 | user callate | 223 |
| 5 | user eres | 198 |
| 6 | user que | 194 |
| 7 | que los | 186 |
| 8 | todos los | 162 |
| 9 | eres una | 143 |
| 10 | para que | 142 |
| 11 | los que | 140 |
| 12 | que eres | 133 |
| 13 | una puta | 125 |
| 14 | callate puta | 112 |
| 15 | hay que | 111 |
| 16 | los inmigrantes | 107 |
| 17 | hija puta | 107 |
| 18 | las mujeres | 105 |
| 19 | una mujer | 104 |
| 20 | cállate puta | 92 |
| 21 | valla ceuta | 92 |
| 22 | cállate perra | 84 |
| 23 | user los | 80 |
| 24 | los comunistas | 79 |
| 25 | que son | 74 |
| 26 | con los | 74 |
| 27 | por qué | 74 |
| 28 | que les | 71 |
| 29 | user pero | 71 |
| 30 | por que | 69 |

### Clase: no_hate

| Posición | Bigrama | Frecuencia |
|----------|---------|------------|
| 1 | user user | 7,911 |
| 2 | link link | 778 |
| 3 | que los | 733 |
| 4 | los que | 566 |
| 5 | todos los | 496 |
| 6 | user que | 479 |
| 7 | hay que | 434 |
| 8 | las mujeres | 433 |
| 9 | user link | 427 |
| 10 | para que | 409 |
| 11 | greta thunberg | 367 |
| 12 | hijo puta | 338 |
| 13 | creo que | 325 |
| 14 | con los | 324 |
| 15 | los chilenos | 324 |
| 16 | que son | 299 |
| 17 | son los | 297 |
| 18 | vía user | 291 |
| 19 | una mujer | 287 |
| 20 | que hay | 284 |
| 21 | puta madre | 274 |
| 22 | link vía | 265 |
| 23 | por que | 264 |
| 24 | los comunistas | 258 |
| 25 | por qué | 247 |
| 26 | user los | 237 |
| 27 | que les | 233 |
| 28 | que las | 226 |
| 29 | user pero | 212 |
| 30 | que nos | 205 |

## 8. Resumen de aserciones de calidad

| Aserción | Resultado |
|----------|-----------|
| IDs únicos | [OK] |
| Textos no nulos | ✓ |
| Textos ≥ 3 tokens | ⚠ (141 casos) |
| Etiquetas ∈ {0,1} | ✓ |
| tiene_modismo dtype==bool | ✓ |
| Proporción hate ∈ [5%,60%] | ✓ (22.8%) |
| Cobertura modismos ≥ 15% | ✓ (53.2%) |

---

*Reporte generado por `src/data/qc.py` — Paso 1.8 del pipeline de datos.*