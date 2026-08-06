# Resultados y Validación de Hipótesis

Resumen ejecutivo de los resultados finales del proyecto, pensado para consulta rápida (por ejemplo, antes de la sustentación). La bitácora experimental completa, con hashes de trazabilidad y metadatos del entorno, está en `EXPERIMENTOS.md`.

## Las 3 hipótesis de investigación

| ID | Hipótesis | Estado |
|---|---|---|
| H1 | BETO ajustado mejora frente a BETO base sin ajuste fino. | ✅ Soportada |
| H2 | BETO ajustado iguala o supera a modelos multilingües de referencia (mBERT, XLM-R). | ⚠️ Parcialmente soportada |
| H3 | BETO ajustado obtiene mejor desempeño relativo en textos con modismos latinoamericanos que en textos sin ellos. | ✅ Soportada |

## H1 — BETO ajustado vs. BETO base

BETO base es el mismo modelo preentrenado pero **sin fine-tuning** en la tarea, usado como referencia de "punto de partida".

| Métrica | BETO base | BETO ajustado (semilla 123) | Diferencia |
|---|---:|---:|---:|
| F1 (hate) | 0.0682 | 0.6858 | +0.6176 |

- Test de McNemar: p = 1.7095e-62 (diferencia estadísticamente muy significativa).
- **Lectura:** el fine-tuning es indispensable. El modelo preentrenado sin ajustar prácticamente no distingue la clase `hate` (recall de solo 4%); el ajuste fino le permite pasar a un F1 de 0.68.

## H2 — BETO ajustado vs. mBERT y XLM-R

| Comparación | Resultado | p-valor (McNemar) | Significativo (α=0.05) |
|---|---|---:|---|
| BETO vs. mBERT | BETO gana (F1: 0.6810 vs 0.6474) | 1.7806e-11 | Sí |
| BETO vs. XLM-R | BETO gana en promedio (F1: 0.6810 vs 0.6681), pero no de forma concluyente | 0.1174 | No |

- **Lectura:** BETO ajustado supera claramente a mBERT. Frente a XLM-R, BETO tiene mejor F1 promedio pero la diferencia no alcanza significancia estadística en la semilla evaluada — por eso H2 se reporta como "parcialmente soportada": BETO es competitivo con XLM-R, no estrictamente superior con evidencia estadística.
- Este matiz es importante mencionarlo así ante el jurado: es una conclusión honesta, no una debilidad oculta. Un modelo monolingüe especializado (BETO) igualando a un modelo multilingüe mucho más grande y general (XLM-R) ya es un resultado relevante.

## H3 — Desempeño en textos con modismos latinoamericanos

El lexicón LATAM (383 términos canónicos, 886 tokens con variantes) se usa para marcar qué textos del test set contienen modismos regionales, sin influir en el modelo.

| Subconjunto del test set | Total | % hate real | F1 de BETO |
|---|---:|---:|---:|
| Con modismos | 2,686 | 31.57% | **0.7347** |
| Sin modismos | 2,263 | 12.42% | 0.5055 |

- Delta F1: +0.2292 (intervalo de confianza bootstrap: [0.1738, 0.2889]).
- p-valor (test de permutación): 0.000999 (significativo).
- **Lectura:** BETO ajustado detecta discurso de odio notablemente mejor en textos con modismos latinoamericanos que sin ellos. Una hipótesis posible es que los textos con modismos suelen ser más explícitos/coloquiales en su agresividad, lo cual favorece la señal que el modelo aprendió.

## Explicabilidad (XAI)

- Método: SHAP sobre `models/beto_finetuned_final`.
- Artefactos: `reports/tables/xai_analysis/` (pesos por token, casos mal clasificados, análisis específico de tokens que son modismos).
- Uso: inspección cualitativa, no un criterio de validación estadística por sí solo.
- Hallazgo relevante: se observan falsos positivos en textos con insultos o marcadores políticos usados en tono irónico o no dirigido a una persona — una limitación esperable de cualquier clasificador que no tiene contexto conversacional completo.

## Resumen para la defensa (una frase por hipótesis)

- **H1:** El ajuste fino es indispensable; sin él, BETO no distingue el discurso de odio (F1 de 0.07 vs. 0.68).
- **H2:** BETO ajustado supera a mBERT con significancia estadística, e iguala competitivamente a XLM-R.
- **H3:** El modismo LATAM no se usó para entrenar, pero sí sirve para explicar dónde el modelo funciona mejor: en textos con modismos regionales el F1 sube de 0.51 a 0.73.

## Fuentes de estos datos

- `EXPERIMENTOS.md` — bitácora completa con hashes SHA-256, metadata del entorno y comandos de verificación.
- `reports/tables/comparativa_global.csv` — métricas agregadas de los 3 modelos.
- `reports/tables/mcnemar_results.csv` — pruebas de significancia pareada.
- `reports/tables/h3_idiom_analysis/` — segmentación por modismos.
- `reports/tables/xai_analysis/` — resultados de SHAP.
