# Reporte de Exploración Inicial (Paso 1.3)

**Generado:** 2026-06-06 11:35  
**Datasets:** 4 de 4 cargados.  
**Total de filas tras carga inicial:** 37,026.

Este documento es la salida automática del script `scripts/exploracion_inicial.py` y del notebook `notebooks/01_exploracion.ipynb`. Resume el estado de los datos crudos antes de la limpieza/normalización (Paso 1.4) y el mapeo a esquema binario (Paso 1.5).

## Resumen ejecutivo

| Dataset | Filas | Idioma | Plataforma | Etiqueta principal | % seeds LATAM |
|---------|------:|--------|------------|--------------------|---------------:|
| HatEval | 6,599 | ES (filtrado) | Twitter | `HS` | 2.4% |
| DETOXIS | 3,463 | ES | Comentarios noticias | `toxicity` | 0.1% |
| HaterNet | 6,000 | ES | Twitter | `label` | 1.1% |
| Chilean | 20,964 | ES (CL) | Twitter | `hate speech/estereotipo` | 9.6% |

## Figuras

![Volumen por dataset](figuras/volumen_datasets.png)

![Distribución de clases](figuras/distribucion_clases.png)

![Longitud de texto](figuras/longitud_tokens.png)

![Seeds LATAM](figuras/seeds_latam.png)

## HatEval

- **Forma:** 6,599 filas × 9 columnas
- **Columnas:** id, text, target, language, HS, TR, AG, __index_level_0__, split
- **Duplicados de texto:** 4
- **Longitud (chars):** mediana=116, P95=278, máx=846
- **Longitud (tokens):** mediana=19, P95=46, máx=88
- **Seeds LATAM presentes:** 2.44% de textos

**Distribución de etiquetas:**

- `HS`: `0`=3,860 (58.5%), `1`=2,739 (41.5%)
- `TR`: `0`=4,910 (74.4%), `1`=1,689 (25.6%)
- `AG`: `0`=4,447 (67.4%), `1`=2,152 (32.6%)

**Muestras de texto:**

1. `Easyjet quiere duplicar el número de mujeres piloto' Verás tú para aparcar el avión.. http://t.co/46NuLkm09x`
2. `El gobierno debe crear un control estricto de inmigración en las zonas fronterizas con Colombia por q después del 20-8querrán venir en masa`
3. `Yo veo a mujeres destruidas por acoso laboral y callejero. Otras con depresión debido a violación sexual o maltrato físico. Y conocí a varias que se suicidaron por este tipo de comportamientos machist`

## DETOXIS

- **Forma:** 3,463 filas × 21 columnas
- **Columnas:** topic, thread_id, comment_id, reply_to, comment_level, comment, argumentation, constructiveness, positive_stance, negative_stance, target_person, target_group, stereotype, sarcasm …
- **Duplicados de texto:** 18
- **Longitud (chars):** mediana=127, P95=641, máx=3270
- **Longitud (tokens):** mediana=23, P95=112, máx=556
- **Seeds LATAM presentes:** 0.06% de textos

**Distribución de etiquetas:**

- `toxicity`: `0`=2,316 (66.9%), `1`=1,147 (33.1%)
- `aggressiveness`: `0`=3,349 (96.7%), `1`=114 (3.3%)
- `insult`: `0`=3,215 (92.8%), `1`=248 (7.2%)
- `stereotype`: `0`=3,137 (90.6%), `1`=326 (9.4%)
- `target_person`: `0`=2,965 (85.6%), `1`=498 (14.4%)
- `target_group`: `0`=2,960 (85.5%), `1`=503 (14.5%)

**Muestras de texto:**

1. `Pensó: Zumo para restar.`
2. `Como les gusta el afeitado en seco a esta gente.`
3. `asi me gusta, que se maten entre ellos y en alta mar. Mas inmigrantes asi porfavor`

## HaterNet

- **Forma:** 6,000 filas × 3 columnas
- **Columnas:** id, text, label
- **Duplicados de texto:** 1
- **Longitud (chars):** mediana=116, P95=180, máx=342
- **Longitud (tokens):** mediana=18, P95=30, máx=56
- **Seeds LATAM presentes:** 1.05% de textos

**Distribución de etiquetas:**

- `label`: `0`=4,433 (73.9%), `1`=1,567 (26.1%)

**Muestras de texto:**

1. `Ismael es egocentrico porque se vuelve loca si le dicen que tiene el pelo bonito😂😂😂😂 eso se define con otro objetivo #FirstDates251`
2. `..ya tardaba en salir quien pronunciase nombre catalán sílaba aguda como si fuese plana [es Eduááárd],[Ernééést],[Albééért] no son ingleses`
3. `(Esto no es un discurso político y razonado, obviamente, solo una llamada de atención en plan "JODER, NO CUESTA TANTO SABER COSAS")`

## Chilean

- **Forma:** 20,964 filas × 21 columnas
- **Columnas:** Unnamed: 0, caso, link, tweet a etiquetar, contexto, anónimo, género, mención migración, mención venezuela, mención política nacional, mención grupos marginalizados, mención otros, grosería c/int., grosería s/int. …
- **Duplicados de texto:** 11463
- **Longitud (chars):** mediana=131, P95=297, máx=679
- **Longitud (tokens):** mediana=21, P95=49, máx=77
- **Seeds LATAM presentes:** 9.61% de textos

**Distribución de etiquetas:**

- `hate speech/estereotipo`: `0`=9,201 (93.6%), `1`=633 (6.4%)
- `insulto/sobrenombre`: `0`=5,798 (59.0%), `1`=4,036 (41.0%)
- `grosería c/int.`: `0`=7,166 (72.9%), `1`=2,668 (27.1%)
- `sarcasmo/ironía/burla`: `0`=7,709 (78.4%), `1`=2,125 (21.6%)
- `mención migración`: `0`=9,429 (95.9%), `1`=405 (4.1%)

**Muestras de texto:**

1. `Eran tan pero tan feministas que invisibilizaban constantemente a las trabajadoras sexuales, haciéndole creer al mundo que eran incapaces de decidir y que cada vez que ejercían su derecho a hacerlo es`
2. `@Eneatipo7 @Cooperativa @karina_ol Me carga en lo q se convirtió la 2da vuelta a la gobernación...una flaiterío.`
3. `, ¿Sabrán las femiorcas como @karina_ol y todo el flaiterio mapuchento , que si hay una cultura y sociedad absolutamente hetero patriarcal, de un machismo extremo, es justamente la mapuche?`

## Hallazgos clave (preliminar)

1. **Volumen consolidado:** los 4 datasets aportan suficientes ejemplos para particionar 70/15/15 con tamaño razonable.
2. **Heterogeneidad de etiquetas:** cada dataset usa convenciones distintas (`HS`, `toxicity_level`, `label`, `hate speech/estereotipo`). El Paso 1.5 las unifica al esquema binario `etiqueta ∈ {0, 1}`.
3. **Cobertura LATAM:** Chilean concentra la mayor proporción de seeds regionales. Es el dataset crítico para validar H3 (Paso 4).
4. **Calidad textual:** los nulos detectados deben revisarse en limpieza (Paso 1.4) y los duplicados marcarse antes de unificar (Paso 1.5).

## Próximo paso

→ **Paso 1.4** Implementar `src/data/clean.py` con la función `normalizar()` y aplicarla en el notebook `02_unificacion.ipynb`.
