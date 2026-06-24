# 5.3 Construcción / Implementación

Este capítulo describe la fase de construcción del sistema inteligente de moderación automática de discurso de odio en español. Se documentan las tecnologías seleccionadas, la estructura final del proyecto, el desarrollo de cada módulo de software y la forma en que todos estos componentes se integran para conformar el sistema completo.

---

## 5.3.1 Tecnologías Utilizadas

El sistema se implementa mediante un conjunto de tecnologías cuya selección responde a criterios de reproducibilidad científica, madurez de la librería y compatibilidad con los requisitos de cómputo del proyecto.

### Lenguajes y runtimes

| Capa | Tecnología | Versión mínima | Justificación |
|------|-----------|----------------|---------------|
| ML y backend | Python | 3.10 | Soporte de type hints modernos, compatibilidad con todas las librerías de ML utilizadas. |
| Extensión de navegador | JavaScript (ES2022) | — | Estándar nativo del navegador; evita dependencias externas de compilación. |
| Entornos interactivos | Jupyter Notebook | — | Exploración y validación incremental de datos y modelos. |
| Empaquetado | pip + venv / conda | — | Reproducibilidad del entorno; se ofrece tanto `requirements.txt` como `environment.yml`. |

### Bibliotecas Python principales

| Biblioteca | Versión mínima | Uso en el proyecto |
|-----------|---------------|-------------------|
| `transformers` | ≥ 4.40 | Carga y ajuste fino de BETO, mBERT y XLM-R mediante `AutoTokenizer` y `AutoModelForSequenceClassification`. |
| `torch` | ≥ 2.2 | Backend de cómputo para el entrenamiento (CPU y CUDA opcional). |
| `datasets` | ≥ 2.18 | Conversión de DataFrames a objetos `Dataset` con mapeo perezoso y batching. |
| `scikit-learn` | ≥ 1.4 | Métricas de clasificación, particionado estratificado y cálculo de pesos de clase. |
| `pandas` / `numpy` | — | Manipulación tabular y cálculo numérico en el pipeline de datos. |
| `pyarrow` | ≥ 15.0 | Almacenamiento en formato Parquet: tipado fuerte, compresión columnar y lectura rápida. |
| `fastapi` + `uvicorn` + `pydantic` | ≥ 0.110 / ≥ 0.27 / ≥ 2.6 | Backend REST: definición de endpoints, validación de esquemas y servidor ASGI. |
| `shap` | ≥ 0.45 | Explicabilidad mediante valores SHAP sobre el modelo final. |
| `statsmodels` | ≥ 0.14 | Test de McNemar para comparación estadística pareada entre modelos. |
| `emoji` + `ftfy` + `regex` | — | Normalización textual: conversión de emojis, reparación de encoding y limpieza de caracteres. |
| `matplotlib` + `seaborn` | — | Generación de figuras científicas (matrices de confusión, distribuciones, curvas ROC). |
| `pytest` + `pytest-cov` | ≥ 8.0 | Suite de pruebas unitarias e integración del backend. |

### Tecnologías de la extensión de navegador

La extensión se implementa en **JavaScript vanilla bajo el estándar Manifest V3** de Chrome, sin dependencias de frameworks de UI externos. Esta decisión reduce el peso del artefacto entregable (evita un bundle de React de ~600 KB), simplifica la auditoría del código por parte del jurado y garantiza que ningún framework externo accede al DOM del usuario.

Los mecanismos de la plataforma utilizados son:

- **`chrome.storage.local`**: persistencia del lexicón personal del usuario y de la configuración (umbral, estado de activación).
- **`chrome.scripting`**: inyección programática del content script sobre las pestañas activas.
- **`chrome.runtime`**: comunicación entre el service worker, el content script y la interfaz de usuario (popup y options page) mediante paso de mensajes.
- **`fetch` API**: llamadas HTTP al backend FastAPI desde el service worker.

### Entornos de ejecución

| Entorno | Uso |
|---------|-----|
| PC local con GPU (≥ 6 GB VRAM) | Desarrollo, depuración y entrenamientos cortos. |
| Google Colab (T4) | Entrenamientos completos con el corpus de 33 318 ejemplos. |
| Kaggle Notebooks (P100) | Repetición con semillas adicionales para validar varianza. |
| PC local sin GPU | Ejecución del backend y pruebas de la extensión en modo inferencia. |

---

## 5.3.2 Estructura del Proyecto

El repositorio adopta la convención **medallion** (raw → interim → processed), estándar en proyectos de Machine Learning reproducibles, y organiza el código fuente en módulos desacoplados que reflejan las tres capas de la arquitectura.

```
Tesis_Proyecto/
├── README.md                           # Visión rápida y comandos básicos
├── EXPERIMENTOS.md                     # Bitácora científica con métricas por corrida
├── ESTADO_PROYECTO.md                  # Estado actual del avance por fase
├── Makefile                            # Atajos: make data, make train, make api
├── pyproject.toml                      # Configuración de ruff, black y pytest
├── requirements.txt                    # Dependencias Python del proyecto
├── environment.yml                     # Alternativa conda del entorno
│
├── data/
│   ├── raw/                            # Datasets descargados. Inmutable.
│   │   ├── spanish-hate-speech-superset/   # Corpus base (Tonneau et al., 2024)
│   │   ├── DETOXIS_2021-main/              # Complemento manual (IberLEF 2021)
│   │   └── analisis_dataset/              # Scripts de verificación de fuentes
│   ├── interim/                        # DETOXIS limpio individualmente (Parquet)
│   ├── processed/                      # Corpus unificado y particiones finales
│   │   ├── corpus_v1_enriquecido.parquet
│   │   ├── train.parquet
│   │   ├── val.parquet
│   │   ├── test.parquet
│   │   └── MANIFEST.json              # Hash SHA-256, commit, versión de lexicón
│   ├── lexicons/
│   │   └── modismos_latam_v1.csv      # 383 términos canónicos, 886 tokens efectivos
│   └── reports_qc/                    # Reportes de control de calidad y figuras
│
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_unificacion.ipynb
│   ├── 03_modismos.ipynb
│   ├── 04_finetuning_beto.ipynb
│   ├── 05_baselines_mbert_xlmr.ipynb
│   ├── 06_evaluacion_comparada.ipynb
│   ├── 07_analisis_modismos.ipynb
│   └── 08_xai.ipynb
│
├── src/
│   ├── config.py                       # Rutas, semillas y constantes globales
│   ├── data/
│   │   ├── clean.py                    # Normalización textual (función normalizar())
│   │   ├── unify.py                    # Unificación de fuentes al esquema canónico
│   │   ├── lexicon.py                  # Clase LexiconLatam y función tiene_modismo()
│   │   ├── enrich.py                   # Enriquecimiento del corpus con tiene_modismo
│   │   ├── split.py                    # Particionado estratificado train/val/test
│   │   └── qc.py                       # Validaciones de calidad del corpus
│   ├── modeling/
│   │   ├── tokenize.py                 # Tokenización con AutoTokenizer
│   │   ├── train.py                    # Bucle de entrenamiento y WeightedTrainer
│   │   ├── evaluate.py                 # Métricas en validación durante entrenamiento
│   │   ├── losses.py                   # CrossEntropyLoss ponderada y focal opcional
│   │   └── checkpoints.py              # Selección del mejor checkpoint por F1
│   ├── evaluation/
│   │   ├── metrics.py                  # Precision, Recall, F1, Accuracy, ROC-AUC
│   │   ├── bootstrap.py                # Intervalos de confianza (1 000 remuestreos)
│   │   ├── mcnemar.py                  # Test de McNemar pareado entre modelos
│   │   └── errors.py                   # Análisis de errores por segmento
│   ├── xai/
│   │   └── shap_explainer.py           # Wrapper SHAP y normalización de salida JSON
│   └── api/
│       ├── main.py                     # Aplicación FastAPI con lifespan
│       ├── schemas.py                  # Esquemas Pydantic de entrada y salida
│       ├── inference.py                # Lógica de predicción con el modelo cargado
│       ├── xai.py                      # Endpoint /explain conectado a SHAP
│       ├── config.py                   # Variables de entorno y configuración del API
│       └── logging_conf.py             # Logging estructurado
│
├── extension/
│   ├── manifest.json                   # Manifest V3: permisos, scripts y recursos
│   ├── background.js                   # Service worker: cola de inferencia y fetch
│   ├── content.js                      # Content script: escaneo DOM y resaltado
│   ├── lexicon.js                      # Módulo de lexicón personal del usuario
│   ├── api.js                          # Abstracción de llamadas HTTP al backend
│   ├── popup/                          # UI de control (toggle, umbral, estado)
│   ├── options/                        # CRUD de lexicón personal
│   ├── styles.css                      # Estilos de resaltado y tooltips
│   └── icons/                         # Iconos de la extensión
│
├── models/                             # Checkpoints (no versionados en git)
│   └── README.md                       # Convenciones de nombres y ubicación
│
├── scripts/
│   ├── exploracion_inicial.py          # Exploración del corpus (Fase 1)
│   ├── train_model.py                  # Entrypoint de entrenamiento (CLI)
│   ├── evaluate_model.py               # Evaluación en test set (CLI)
│   ├── package_model.py                # Empaquetado del modelo final
│   └── run_api.sh                      # Lanzamiento del servidor uvicorn
│
└── tests/
    ├── unit/
    │   ├── test_clean.py
    │   ├── test_lexicon.py
    │   ├── test_metrics.py
    │   └── test_schemas.py
    └── integration/
        ├── test_pipeline_data.py
        └── test_api.py
```

---

## 5.3.3 Desarrollo de Módulos

### Módulo de Datos (`src/data/`)

El módulo de datos implementa el pipeline completo de preparación del corpus, siguiendo una secuencia ordenada y reproducible de transformaciones.

#### Limpieza y normalización (`clean.py`)

El corpus se construye a partir de dos fuentes con características de preprocesamiento distintas. El Spanish Hate Speech Superset ya incorpora un preprocesamiento estandarizado (nombres de usuario reemplazados por `@USER`, URLs por `URL`). DETOXIS, en cambio, proviene en su forma original y requiere una normalización explícita.

La función `normalizar()` se implementa únicamente para DETOXIS y aplica, en orden, las siguientes transformaciones:

1. **Reparación de encoding** mediante `ftfy.fix_text()`, que corrige caracteres mojibake como `AsÃ­` → `Así`.
2. **Decodificación de entidades HTML** (`&amp;` → `&`, `&lt;` → `<`).
3. **Eliminación de caracteres invisibles** (zero-width spaces del rango Unicode `U+200B–U+200F`).
4. **Sustitución de URLs** por el token `URL`.
5. **Sustitución de menciones** (`@usuario`) por el token `USUARIO`.
6. **Descomposición de hashtags** (`#TestPalabra` → `TestPalabra`).
7. **Conversión de emojis** a tokens textuales en español (`:cara_llorando_de_risa:`) mediante `emoji.demojize(language="es")`.
8. **Colapso de repeticiones extremas** (`holaaaaaa` → `holaa`) mediante regex.
9. **Normalización de espacios** con `re.sub(r"\s+", " ", texto).strip()`.

Las mayúsculas originales se preservan deliberadamente porque el modelo BETO utilizado es *cased* (sensible a mayúsculas), y su tokenizador fue entrenado con ese rasgo.

#### Unificación al esquema canónico (`unify.py`)

La función pública `construir_corpus()` adapta ambas fuentes al esquema canónico del proyecto:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | `string` | Identificador único con formato `<dataset>_<n>`. |
| `texto` | `string` | Texto del post normalizado. No nulo, longitud ≥ 3 tokens. |
| `etiqueta` | `int8` | Etiqueta binaria: `1` = discurso de odio, `0` = no odio. |
| `dataset` | `category` | Dataset de origen (`hateval`, `haternet`, `chileno`, `homomex`, `hascosva`, `detoxis`). |
| `source` | `string` | Plataforma de origen (Twitter, comentarios de noticias). |
| `nb_annotators` | `int16` | Número de anotadores del ejemplo. |
| `pais` | `category` | País del autor inferido, o `unknown`. |
| `tiene_modismo` | `bool` | Calculado por el lexicón LATAM. No nulo. |

Para el superset, la adaptación consiste en renombrar columnas (`text` → `texto`, `labels` → `etiqueta`, `post_author_country_location` → `pais`) y coercionar la etiqueta a `int8`. Para DETOXIS, se aplica primero la función `normalizar()` sobre la columna `comment` (nombre real del campo de texto en ese dataset), y luego se mapea la escala granular de toxicidad a etiqueta binaria según la regla `toxicity_level ≥ 2 → 1`.

El corpus resultante tras la concatenación comprende **33 318 ejemplos** (29 855 del superset + 3 463 de DETOXIS), con una distribución de clases de 22,8 % de odio (7 603 instancias) y 77,2 % de no-odio (25 715 instancias). Se ejecutan validaciones automáticas de integridad antes de guardar: unicidad de IDs, ausencia de textos nulos, etiquetas dentro del conjunto `{0, 1}` y proporción de odio dentro del rango esperado (5 %–60 %).

El corpus se persiste en `data/interim/corpus_combinado.parquet` y posteriormente en `data/processed/corpus_v1_enriquecido.parquet`.

#### Lexicón de modismos latinoamericanos (`lexicon.py` + `data/lexicons/`)

El lexicón cumple un rol **exclusivamente observacional**: se usa para marcar la columna `tiene_modismo` en el corpus y segmentar la evaluación experimental (validación de H3). No se inyecta como característica al modelo.

El archivo `data/lexicons/modismos_latam_v1.csv` contiene **383 términos canónicos** con sus variantes ortográficas agrupadas, organizados según el siguiente esquema:

| Columna | Descripción |
|---------|-------------|
| `termino` | Forma canónica en minúsculas. |
| `variantes` | Variantes separadas por `;` (ej: `wei;weón;weon`). |
| `pais` | Código ISO o `MULTI` para términos pan-latinoamericanos. |
| `tipo` | `coloquial`, `intensificador`, `insulto`, `despectivo`, `juvenil`. |
| `fuente` | `ASALE`, `Pérez et al. (2022)`, `curado_manual`. |
| `notas` | Aclaraciones de uso o ambigüedad. |

La cobertura geográfica incluye México (MX), Argentina (AR), Chile (CL), Colombia (CO), Perú (PE), Venezuela (VE), Ecuador (EC) y términos pan-latinoamericanos (MULTI). Las fuentes de respaldo son el Diccionario de Americanismos de la Real Academia Española (ASALE), la literatura científica sobre jerga regional y curaduría manual documentada.

La clase `LexiconLatam` carga el CSV, construye un conjunto de búsqueda (*set*) con todos los términos canónicos y variantes expandidos, y expone la función pura `tiene_modismo(texto: str) → bool`, que tokeniza el texto por expresión regular y comprueba intersección con el conjunto. El lexicón alcanza una **cobertura del 53,19 %** sobre el corpus combinado (17 722 de 33 318 instancias), superando ampliamente el umbral mínimo del 15 % definido en los criterios de diseño.

#### Particionado estratificado (`split.py`)

El corpus se divide en tres particiones con semilla fija (`random_state=42`) y estratificación por etiqueta, garantizando que la distribución de clases se preserve en cada subconjunto:

| Partición | Proporción | Instancias (aprox.) |
|-----------|-----------|---------------------|
| `train.parquet` | 70 % | 23 323 |
| `val.parquet` | 15 % | 4 998 |
| `test.parquet` | 15 % | 4 997 |

Las particiones se guardan en `data/processed/` junto con un archivo `MANIFEST.json` que registra el hash SHA-256 del corpus, el commit de git y la versión del lexicón, garantizando la trazabilidad experimental completa.

---

### Módulo de Modelado (`src/modeling/` y `scripts/train_model.py`)

El entrenamiento de los modelos se gestiona mediante el script `scripts/train_model.py`, que expone una interfaz de línea de comandos parametrizable por modelo y semilla.

#### Modelos entrenados

Se entrena un total de **nueve configuraciones** (3 arquitecturas × 3 semillas), todas con el mismo protocolo:

| Arquitectura | Identificador HuggingFace | Tipo |
|-------------|--------------------------|------|
| BETO (ajustado) | `dccuchile/bert-base-spanish-wwm-cased` | Modelo principal |
| mBERT | `bert-base-multilingual-cased` | Baseline multilingüe |
| XLM-R | `xlm-roberta-base` | Baseline multilingüe |

Las semillas utilizadas son `{42, 123, 2024}`. Reportar media ± desviación estándar sobre las tres repeticiones neutraliza la varianza intrínseca del fine-tuning de Transformers.

#### Hiperparámetros de entrenamiento

| Hiperparámetro | BETO / mBERT | XLM-R | Justificación |
|---------------|-------------|-------|---------------|
| Learning rate | 2 × 10⁻⁵ | 1 × 10⁻⁵ | XLM-R converge mejor con LR más conservadora. |
| Batch size | 16 | 16 | Equilibrio entre estabilidad y memoria disponible (T4 16 GB). |
| Épocas máximas | 4 | 4 | Límite superior; early stopping activo. |
| Max. longitud (tokens) | 128 | 128 | Cubre el P95 de longitud del corpus (< 128 tokens). |
| Weight decay | 0,01 | 0,01 | Regularización estándar para fine-tuning BERT. |
| Warmup ratio | 0,10 | 0,10 | 10 % de pasos de warmup lineal. |
| Precision numérica | FP16 si GPU | FP16 si GPU | Acelera el entrenamiento en Colab/Kaggle. |

#### Manejo del desbalance de clases

Dado que el corpus presenta un desbalance de aproximadamente 3:1 (no-odio:odio), se aplica una función de pérdida ponderada. Se implementa una subclase `WeightedTrainer` que sobreescribe el método `compute_loss` e inyecta los pesos de clase calculados por `sklearn.utils.class_weight.compute_class_weight("balanced", ...)`:

```python
loss_fct = torch.nn.CrossEntropyLoss(
    weight=class_weights_t.to(logits.device)
)
```

Esto incrementa la penalización por clasificar erróneamente instancias de odio, que constituyen la clase de interés.

#### Criterio de selección del mejor modelo

El criterio de selección dentro de cada corrida es el **F1 de la clase hate** sobre el conjunto de validación (`metric_for_best_model="f1"`). Se activa `EarlyStoppingCallback` con una paciencia de 2 épocas. Al finalizar el entrenamiento, el checkpoint con mejor F1 en validación se copia automáticamente como modelo final en `models/beto_finetuned_final/` (para la mejor semilla de BETO).

Cada corrida genera:
- Pesos del modelo en `models/<arquitectura>_finetuned_<semilla>/`
- Tokenizador serializado con `save_pretrained()`
- Log de métricas por época en `trainer_state.json`

---

### Módulo de Evaluación (`src/evaluation/`)

La evaluación se ejecuta sobre el conjunto de test (fijo, no visto durante el entrenamiento) para los nueve modelos entrenados mediante `scripts/evaluate_model.py`.

#### Métricas reportadas

| Métrica | Justificación |
|---------|---------------|
| Precision (hate) | Tasa de acierto sobre las instancias clasificadas como odio. |
| Recall (hate) | Cobertura de las instancias reales de odio detectadas. |
| F1 (hate) | Media armónica; métrica principal dado el desbalance de clases. |
| F1 macro | Visión global equilibrada entre ambas clases. |
| Accuracy | Referencia complementaria; interpretada con cautela por el desbalance. |
| ROC-AUC | Desempeño del modelo independiente del umbral de decisión. |

#### Pruebas estadísticas

- **Bootstrap con 1 000 remuestreos**: genera intervalos de confianza al 95 % para cada métrica y cada modelo.
- **Test de McNemar pareado**: evalúa si las diferencias de desempeño entre BETO ajustado y cada baseline (mBERT, XLM-R, BETO base) son estadísticamente significativas. Este test es el estándar para clasificadores comparados sobre el mismo conjunto de prueba.

#### Análisis segmentado para H3

Para la validación de la hipótesis H3, el conjunto de test se segmenta en dos subconjuntos mutuamente excluyentes según la columna `tiene_modismo`:

- **Segmento con modismos** (`tiene_modismo == True`)
- **Segmento sin modismos** (`tiene_modismo == False`)

Se calculan las métricas completas en cada segmento para BETO ajustado y los baselines, comparando si BETO ajustado obtiene un desempeño relativo superior en el segmento con modismos.

---

### Módulo de Explicabilidad – XAI (`src/xai/`)

El módulo de explicabilidad implementa un wrapper de SHAP (*SHapley Additive exPlanations*) sobre el modelo final BETO ajustado. La clase `shap_explainer.py` carga el modelo una vez, define un pipeline de predicción compatible con SHAP y, para un texto de entrada, devuelve una estructura JSON con los pesos de importancia por token:

```json
{
  "tokens": ["Este", "tipo", "es", "un", "imbécil"],
  "pesos_shap": [0.02, 0.01, 0.00, 0.01, 0.87]
}
```

Esta salida es consumida directamente por el endpoint `/explain` del backend, que la retransmite a la extensión de navegador para que el usuario visualice qué palabras influyeron en la decisión del modelo.

---

### Backend REST (`src/api/`)

El backend se implementa con **FastAPI** y se ejecuta mediante `uvicorn`. Al iniciar la aplicación, el modelo y su tokenizador se cargan una única vez en memoria durante el evento `lifespan`, evitando tiempos de espera por carga en cada petición.

#### Endpoints implementados

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Verificación de liveness: retorna `{"status": "ok"}` y la versión del modelo. |
| POST | `/predict` | Recibe `{"texto": "..."}` y retorna `{"etiqueta": 0/1, "probabilidad": float, "modelo": str, "version": str}`. |
| POST | `/explain` | Recibe `{"texto": "..."}` y retorna `{"tokens": [...], "pesos_shap": [...]}`. |
| GET | `/metadata` | Retorna versión del modelo, hash SHA-256 del checkpoint, fecha de entrenamiento y métricas de referencia. |

Los esquemas de entrada y salida se definen con modelos Pydantic v2, lo que provee validación automática, documentación OpenAPI (Swagger UI en `/docs`) y mensajes de error claros ante entradas malformadas.

La política CORS restringe el origen de las peticiones a `localhost` y al esquema `chrome-extension://`, de modo que el backend no acepta peticiones de sitios web arbitrarios.

El flujo interno de inferencia ante una petición `/predict` es el siguiente:

1. Validación del cuerpo JSON por Pydantic.
2. Tokenización del texto con truncamiento a 128 tokens.
3. Forward pass del modelo con `torch.no_grad()` para evitar el cálculo de gradientes.
4. Aplicación de softmax sobre los logits para obtener probabilidades.
5. Comparación con el umbral de decisión (por defecto 0,5).
6. Retorno de la etiqueta predicha y la probabilidad de la clase odio.

---

### Extensión de Navegador (`extension/`)

La extensión implementa la interfaz de usuario del sistema y se distribuye como un paquete Manifest V3 instalable en Chromium. Sus componentes son:

#### `manifest.json`

Declara los permisos necesarios (`activeTab`, `scripting`, `storage`), los scripts de background y content, las páginas de UI y el host permitido (`http://127.0.0.1:8000/*`) para las llamadas al backend local.

#### `background.js` – Service Worker

Actúa como intermediario entre el content script y el backend. Implementa:

- **Cola de inferencia**: los fragmentos de texto enviados desde el content script se encolan y se procesan con concurrencia controlada, evitando saturar al backend con peticiones simultáneas.
- **Debounce**: los nuevos nodos detectados en el DOM se acumulan durante un intervalo breve (300 ms) antes de enviarlos, reduciendo el número de peticiones en páginas con renderizado dinámico.
- **Cache de resultados**: las predicciones sobre textos ya procesados se almacenan en memoria para evitar peticiones redundantes durante la sesión.
- **Health check**: el service worker verifica periódicamente la disponibilidad del backend y actualiza el estado visible en el popup.

#### `content.js` – Content Script

Se inyecta en la pestaña activa cuando el usuario activa la extensión. Sus funciones son:

1. **Escaneo del DOM**: recorre los nodos de texto visibles de la página mediante un `TreeWalker`, extrae fragmentos de hasta 512 caracteres y los envía al service worker.
2. **Aplicación del lexicón personal**: antes de enviar al backend, aplica el lexicón personal del usuario directamente en el navegador, sin tráfico de red, marcando en tiempo real los términos configurados.
3. **Resaltado de resultados**: al recibir una predicción de odio con probabilidad por encima del umbral, envuelve el nodo de texto en un elemento `<mark>` con clase CSS y un tooltip que muestra la probabilidad.

#### `lexicon.js` – Lexicón Personal

Módulo que gestiona el lexicón personal del usuario almacenado en `chrome.storage.local`. Expone funciones para agregar, eliminar y consultar términos, y un método `matchesText(texto)` que verifica si el texto contiene alguno de los términos del lexicón.

El lexicón personal es completamente separado del lexicón científico LATAM: reside exclusivamente en el navegador del usuario, nunca se transmite al servidor y no interfiere con el experimento.

#### `api.js` – Abstracción HTTP

Centraliza todas las llamadas `fetch` al backend FastAPI. Expone funciones `predict(texto)` y `explain(texto)` que gestionan el tiempo de espera, los errores de red y la normalización de la respuesta JSON.

#### Popup y Options Page

El **popup** (`popup/popup.html` + `popup/popup.js`) provee al usuario un control compacto con:
- Toggle de activación/desactivación de la detección automática.
- Selector de umbral de confianza (0,5–0,9) con retroalimentación en tiempo real.
- Indicador de estado del backend (disponible / no disponible).

La **options page** (`options/options.html` + `options/options.js`) permite gestionar el lexicón personal: agregar términos, eliminarlos, importar y exportar en formato JSON, y configurar si los términos del lexicón se resaltan con el mismo estilo que las predicciones del modelo o con un estilo diferenciado.

---

## 5.3.4 Integración del Sistema

Los componentes descritos en la sección anterior se integran siguiendo el flujo definido por la arquitectura de tres capas. A continuación se describe la secuencia de puesta en marcha y el flujo de datos de extremo a extremo.

### Preparación del entorno

```powershell
# 1. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt
```

### Pipeline de datos (Fase offline)

```powershell
# Verificar fuentes de datos
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_corpus.py

# Construir corpus unificado y enriquecido
.\venv\Scripts\python.exe src\data\unify.py

# Verificar integridad y particionar
.\venv\Scripts\python.exe scripts\prepare_data.py --version 1
```

Tras ejecutar el pipeline, los archivos `train.parquet`, `val.parquet` y `test.parquet` quedan disponibles en `data/processed/`.

### Entrenamiento de modelos (Fase offline)

```powershell
# Fine-tuning de BETO con 3 semillas
python scripts\train_model.py --model beto --seed 42
python scripts\train_model.py --model beto --seed 123
python scripts\train_model.py --model beto --seed 2024

# Entrenamiento de baselines
python scripts\train_model.py --model mbert --seed 42
python scripts\train_model.py --model xlmr --seed 42
# (... continúa para el resto de semillas)
```

Los modelos entrenados quedan en `models/<arquitectura>_finetuned_<semilla>/`. La mejor semilla de BETO se copia a `models/beto_finetuned_final/`.

### Evaluación comparada (Fase offline)

```powershell
# Evaluar todos los modelos en test set
python scripts\evaluate_model.py --all
```

Genera archivos CSV con métricas por modelo y semilla en `reports/tables/`, figuras de matrices de confusión en `reports/figures/` y el reporte comparativo global.

### Lanzamiento del backend (Fase online)

```powershell
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

El backend queda disponible en `http://127.0.0.1:8000`. La documentación interactiva se accede en `http://127.0.0.1:8000/docs`.

### Instalación de la extensión (Fase online)

1. Abrir Chrome y navegar a `chrome://extensions`.
2. Activar el **Modo de desarrollador** (esquina superior derecha).
3. Seleccionar **Cargar descomprimida** y apuntar al directorio `extension/`.
4. La extensión aparece en la barra de herramientas del navegador.

### Flujo de detección en tiempo real

Una vez el backend está activo y la extensión instalada, el flujo de detección es el siguiente:

1. El usuario activa la detección desde el **popup** de la extensión (consentimiento explícito).
2. El **content script** escanea los nodos de texto visibles del DOM de la página activa.
3. La capa de **lexicón personal** (local, sin red) marca inmediatamente los términos configurados por el usuario.
4. Los fragmentos de texto de hasta 512 caracteres se envían al **service worker**, que los gestiona en cola con debounce.
5. El **service worker** realiza peticiones `POST /predict` al backend FastAPI.
6. El backend tokeniza el texto, ejecuta el **forward pass** del modelo BETO ajustado y retorna la etiqueta predicha junto con la probabilidad.
7. El content script **resalta** los fragmentos clasificados como odio con probabilidad ≥ umbral, mostrando un tooltip con la probabilidad.
8. Si el usuario hace clic en un fragmento resaltado, se invoca `POST /explain` y se subrayan los tokens de mayor peso SHAP dentro del fragmento.

Esta integración demuestra que el sistema puede operar de forma funcional en condiciones reales de uso, cumpliendo con el objetivo específico OE8 de exponer el modelo mediante una extensión de navegador demostrativa.

### Resumen de la integración

```
[data/processed/*.parquet]
        │
        ▼
[scripts/train_model.py]  ──→  [models/beto_finetuned_final/]
                                        │
                                        ▼
                               [src/api/main.py]  ──→  FastAPI en localhost:8000
                                                              │
                                                              │  HTTP/JSON
                                                              ▼
                                                    [extension/background.js]
                                                              │
                                                    [extension/content.js]
                                                              │
                                                              ▼
                                                    [Resaltado en el navegador]
```

La separación de capas garantiza que cualquier componente pueda sustituirse o evaluarse de forma independiente: el backend puede probarse con `pytest` sin necesidad del navegador, el pipeline de datos puede ejecutarse sin el modelo entrenado, y la extensión puede operar en modo degradado (solo lexicón personal) si el backend no está disponible.
