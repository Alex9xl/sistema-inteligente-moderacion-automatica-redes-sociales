# DOCUMENTO MAESTRO DE IMPLEMENTACIÓN

## Sistema Inteligente de Moderación Automática en Redes Sociales para la Protección del Bienestar Digital del Usuario

### Detección automática de discurso de odio en español mediante BETO ajustado, modelos multilingües de referencia y una extensión de navegador

---

**Tipo de documento:** Especificación técnica, guía de implementación y bitácora metodológica.
**Audiencia:** Tesista, director de tesis, jurado evaluador, desarrolladores externos que repliquen el sistema.
**Versión:** 2.0
**Estado:** Documento maestro de referencia.

---

## TABLA DE CONTENIDO

1. Introducción y propósito del documento
2. Marco del proyecto: objetivos, hipótesis, variables y alcance
3. Arquitectura general del sistema
4. Stack tecnológico y entorno
5. Organización del repositorio
6. Gestión de datos: estrategia, almacenamiento, versionado y calidad
7. Construcción del corpus unificado
8. Lexicón de modismos latinoamericanos (lexicón de investigación)
9. Fine-tuning de BETO: guía técnica completa
10. Baselines: BETO base, mBERT y XLM-R
11. Evaluación experimental
12. Análisis de modismos (validación de H3)
13. Inteligencia Artificial Explicable (XAI)
14. Backend: especificación técnica del servicio FastAPI
15. Extensión de navegador (Manifest V3)
16. Cronograma técnico por fases y entregables
17. Riesgos del proyecto y mitigaciones
18. Matriz de trazabilidad de requisitos, objetivos e hipótesis
19. Criterios de éxito y aceptación
20. Recomendaciones finales para la defensa
21. Glosario
22. Referencias y fuentes consultadas

---

# 1. INTRODUCCIÓN Y PROPÓSITO DEL DOCUMENTO

Este documento constituye la **guía operativa, arquitectónica y metodológica completa** del proyecto de tesis “Sistema Inteligente de moderación automática en redes sociales para la protección del bienestar digital del usuario”. Su función es triple:

1. **Especificar técnicamente** el sistema, con un nivel de detalle suficiente para que un equipo de desarrollo externo pueda implementarlo sin necesidad de información adicional.
2. **Documentar metodológicamente** las decisiones de diseño, los pipelines de datos, los protocolos de entrenamiento y los procedimientos de evaluación estadística, de forma que el experimento sea **reproducible** y **defendible** ante un jurado académico.
3. **Trazar la correspondencia** entre los objetivos, las hipótesis, las variables y los entregables de la tesis, de manera que cualquier evaluador pueda verificar, paso a paso, que las afirmaciones del informe final están respaldadas por evidencia.

El proyecto se sitúa en la intersección de tres líneas de trabajo:

- **Procesamiento de Lenguaje Natural (NLP)** con modelos basados en *Transformers*, en concreto BETO (BERT en español) y su comparación frente a modelos multilingües (mBERT y XLM-R).
- **Ingeniería de Software**, materializada en un backend desacoplado (FastAPI), una extensión de navegador (Manifest V3) y un repositorio organizado según buenas prácticas de proyectos de Machine Learning reproducibles.
- **Bienestar digital y moderación de contenido**, como dominio de aplicación que justifica la necesidad de modelos sensibles al contexto cultural del usuario hispanohablante.

El núcleo experimental de la investigación es la validación de tres hipótesis:

- **H1.** El fine-tuning de BETO sobre un corpus enriquecido con modismos latinoamericanos mejora el desempeño frente a BETO base aplicado al mismo problema.
- **H2.** Ese mismo BETO ajustado iguala o supera a modelos multilingües de propósito general (mBERT, XLM-R) en la tarea de detección de discurso de odio en español.
- **H3.** El BETO ajustado obtiene un desempeño relativo superior en los segmentos del corpus que contienen modismos latinoamericanos respecto a los que no los contienen.

Estas hipótesis no se modifican en esta versión del documento. Todo lo que sigue se subordina a su validación con métricas (Precision, Recall, F1, Accuracy, ROC-AUC) y pruebas estadísticas formales (bootstrap e McNemar).

---

# 2. MARCO DEL PROYECTO: OBJETIVOS, HIPÓTESIS, VARIABLES Y ALCANCE

## 2.1 Objetivo general

Diseñar, implementar y evaluar un sistema inteligente de moderación automática de discurso de odio en español, basado en el ajuste fino del modelo BETO con un corpus enriquecido con modismos latinoamericanos, e integrarlo en un backend REST y una extensión de navegador que apoyen la protección del bienestar digital del usuario.

## 2.2 Objetivos específicos

- **OE1.** Construir un corpus unificado de discurso de odio en español, integrando cuatro datasets públicos con un esquema de etiquetado binario consistente.
- **OE2.** Construir un lexicón documentado de modismos latinoamericanos que permita enriquecer el corpus mediante una variable observable (`tiene_modismo`).
- **OE3.** Ajustar el modelo BETO sobre el corpus enriquecido bajo un protocolo de entrenamiento reproducible.
- **OE4.** Entrenar y evaluar bajo un protocolo idéntico los modelos de referencia mBERT y XLM-R.
- **OE5.** Comparar el desempeño de BETO ajustado frente a BETO base, mBERT y XLM-R con métricas estándar y pruebas estadísticas formales.
- **OE6.** Analizar el desempeño diferencial del modelo ajustado en subconjuntos con y sin modismos para validar la H3.
- **OE7.** Integrar explicabilidad (XAI) sobre las predicciones del modelo final.
- **OE8.** Exponer el modelo a través de un backend REST y una extensión de navegador funcional (Manifest V3) para demostrar la viabilidad de aplicación.

## 2.3 Variables de la investigación

| Tipo | Variable | Descripción operativa |
|------|----------|-----------------------|
| Independiente | **Modelo de clasificación** | Categoría discreta: `{BETO_base, BETO_ajustado, mBERT, XLM-R}`. |
| Independiente | **Presencia de modismos LATAM** | Booleana sobre cada instancia del corpus, derivada del lexicón. |
| Dependiente | **Desempeño de clasificación** | Vector de métricas: Precision, Recall, F1 (binario y macro), Accuracy, ROC-AUC. |
| Control | **Partición de datos** | `train/val/test` estratificada y fija. |
| Control | **Semilla aleatoria** | Conjunto fijo `{42, 123, 2024}`. |
| Control | **Hiperparámetros base** | Idénticos entre modelos, salvo desviaciones documentadas (p. ej. learning rate de XLM-R). |
| Control | **Tokenización** | Tokenizador asociado a cada modelo, sin alteraciones manuales. |

## 2.4 Alcance

**Incluido:**
- Construcción y unificación del corpus.
- Construcción del lexicón LATAM.
- Fine-tuning de BETO y entrenamiento de baselines.
- Evaluación cuantitativa con pruebas estadísticas formales.
- XAI sobre el modelo final.
- Backend FastAPI demostrativo (no productivo).
- Extensión de navegador Manifest V3 demostrativa (no productiva).

**Excluido (fuera de alcance explícito):**
- Detección de discurso de odio multimodal (imagen/audio).
- Entrenamiento desde cero (*from scratch*) de modelos.
- Despliegue en producción con alta disponibilidad.
- Moderación en tiempo real a escala industrial.
- Categorización fina del odio (sexismo, racismo, xenofobia, etc.); el sistema es **binario** (hate / no hate).

## 2.5 Restricciones

- **Recursos de cómputo limitados**: GPU gratuita (Colab/Kaggle) o GPU local de ≥ 6 GB de VRAM.
- **Datos públicos**: no se recolectarán datos de usuarios reales; se reutilizan datasets académicos.
- **Idioma único**: español. El sistema no se evalúa en otros idiomas.
- **Tiempo académico**: cronograma de ~10 semanas (sección 16).

---

# 3. ARQUITECTURA GENERAL DEL SISTEMA

## 3.1 Visión arquitectónica

El sistema se organiza en **tres capas funcionales** que se comunican mediante interfaces explícitas:

1. **Capa de Datos y Experimentación (offline)**: pipelines de preparación de corpus, entrenamiento, evaluación y generación de artefactos científicos.
2. **Capa de Servicio (online)**: backend FastAPI que carga el modelo final y expone endpoints REST de inferencia y explicación.
3. **Capa de Cliente (online)**: extensión de navegador Manifest V3 que consume el backend y aplica detección automática y un lexicón personal sobre el contenido del DOM.

La frontera entre capas es estricta: la capa de datos no conoce al backend, el backend no conoce al cliente y el cliente solo conoce la API del backend a través de un contrato HTTP/JSON versionado. Esta separación permite que cada capa evolucione, se pruebe y se sustituya de forma independiente.

## 3.2 Diagrama lógico (descrito en texto)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CAPA DE DATOS Y EXPERIMENTACIÓN (offline)                  │
│                                                                             │
│  ┌────────────┐    ┌─────────────┐    ┌────────────┐    ┌───────────────┐   │
│  │ Datasets   │───▶│ Limpieza y  │───▶│ Unificación│───▶│ Enriquecimien-│   │
│  │ públicos   │    │ normaliza-  │    │ etiquetas  │    │ to (lexicón   │   │
│  │ (RAW)      │    │ ción        │    │ binarias   │    │ LATAM)        │   │
│  └────────────┘    └─────────────┘    └────────────┘    └──────┬────────┘   │
│                                                                │             │
│                          ┌─────────────────────────────────────┘             │
│                          ▼                                                   │
│                  ┌───────────────┐                                           │
│                  │ Corpus final  │── train / val / test (estratificado)      │
│                  └──────┬────────┘                                           │
│                         │                                                    │
│        ┌────────────────┼────────────────┬────────────────────┐              │
│        ▼                ▼                ▼                    ▼              │
│  ┌──────────┐    ┌────────────┐    ┌──────────┐         ┌──────────┐         │
│  │BETO base │    │BETO ajusta-│    │  mBERT   │         │  XLM-R   │         │
│  │(referen.)│    │  do (ours) │    │(baseline)│         │(baseline)│         │
│  └────┬─────┘    └─────┬──────┘    └────┬─────┘         └────┬─────┘         │
│       │                │                │                    │               │
│       └────────────────┴───────┬────────┴────────────────────┘               │
│                                ▼                                             │
│                  ┌──────────────────────────────┐                            │
│                  │  Evaluación cuantitativa     │                            │
│                  │  (métricas + bootstrap +     │                            │
│                  │  McNemar + XAI + análisis    │                            │
│                  │  de modismos)                │                            │
│                  └─────────────┬────────────────┘                            │
│                                ▼                                             │
│                  ┌──────────────────────────────┐                            │
│                  │  Modelo final empaquetado    │                            │
│                  │  (BETO ajustado + tokenizer) │                            │
│                  └─────────────┬────────────────┘                            │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────┴─────────────────────────────────────────────┐
│                          CAPA DE SERVICIO (online)                           │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  Backend FastAPI                                                   │      │
│  │  ─ /health      (liveness)                                         │      │
│  │  ─ /predict     (inferencia binaria + probabilidad)                │      │
│  │  ─ /explain     (XAI: tokens + pesos SHAP)                         │      │
│  │  ─ /metadata    (versión modelo, hash, fecha)                      │      │
│  └─────────────────────────┬──────────────────────────────────────────┘      │
└────────────────────────────┼─────────────────────────────────────────────────┘
                             ▼  (HTTP/JSON, CORS restringido)
┌────────────────────────────┴─────────────────────────────────────────────────┐
│                       CAPA DE CLIENTE (extensión)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Content      │  │ Service      │  │ Popup        │  │ Options Page    │   │
│  │ Script       │◀▶│ Worker       │◀▶│ (toggle,     │  │ (CRUD lexicón   │   │
│  │ (DOM scan,   │  │ (cola, fetch │  │  estado,     │  │ personal)       │   │
│  │ resaltado)   │  │  a API)      │  │  umbral)     │  │                 │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘   │
│         │                                                                    │
│         └──── lexicón usuario (chrome.storage.local, NUNCA al servidor)      │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 3.3 Componentes y responsabilidades

### 3.3.1 Módulo de Datos (`src/data/`)

- Descarga y verifica datasets públicos.
- Aplica el pipeline de limpieza y normalización.
- Genera el esquema canónico unificado y la columna `tiene_modismo`.
- Produce las particiones `train/val/test` estratificadas y reproducibles.
- Emite un reporte de calidad por dataset.

### 3.3.2 Módulo de Lexicón LATAM (`src/data/lexicon.py` + `data/lexicons/`)

- Construye y mantiene el lexicón a partir de fuentes citables.
- Provee una función pura `tiene_modismo(texto) -> bool` usada por el pipeline.
- Exporta su versión y hash para trazabilidad experimental.

### 3.3.3 Módulo de Modelado (`src/modeling/`)

- Tokenización con `AutoTokenizer` específico de cada modelo.
- Entrenamiento con `Trainer` o un bucle equivalente, parametrizable por modelo y semilla.
- Gestión de checkpoints y selección del mejor modelo por F1 en validación.
- Empaquetado del modelo final (`save_pretrained`) y registro de hiperparámetros en `EXPERIMENTOS.md`.

### 3.3.4 Módulo de Evaluación (`src/evaluation/`)

- Cálculo de métricas (Precision, Recall, F1, Accuracy, ROC-AUC).
- Bootstrap de intervalos de confianza.
- Test de McNemar pareado entre modelos.
- Análisis segmentado (modismos sí/no).
- Generación automática de tablas y figuras para el informe.

### 3.3.5 Módulo de XAI (`src/xai/`)

- Wrappers SHAP sobre el modelo final.
- Salida estandarizada `{tokens, pesos}` para consumo del backend.

### 3.3.6 Módulo de API (`src/api/`)

- Carga única del modelo en `lifespan`.
- Definición de esquemas Pydantic.
- Endpoints documentados con OpenAPI (Swagger UI automático).
- Middleware CORS restringido al origen de la extensión y a `localhost`.
- Logging estructurado y manejo de errores tipificados.

### 3.3.7 Módulo de Extensión (`extension/`)

- Content script que recorre el DOM, segmenta texto y resalta resultados.
- Service worker que mantiene la cola de inferencia y la comunicación con la API.
- Popup que controla activación, umbral y muestra estado.
- Options page que gestiona el lexicón personal del usuario.

## 3.4 Flujos de datos

### 3.4.1 Flujo offline (entrenamiento y evaluación)

1. **Ingesta**: descarga manual o scripted a `data/raw/<dataset>/`.
2. **Validación de fuente**: checksum, conteo de filas y columnas mínimas.
3. **Limpieza individual**: cada dataset se procesa en `data/interim/<dataset>.parquet`.
4. **Unificación**: mapeo de etiquetas y concatenación en `data/processed/corpus_v{n}.parquet`.
5. **Enriquecimiento**: cálculo de `tiene_modismo` y guardado de `corpus_v{n}_enriquecido.parquet`.
6. **Particionado**: `train.parquet`, `val.parquet`, `test.parquet` con semilla fija.
7. **Entrenamiento**: por cada modelo y semilla, se generan `models/<modelo>_<semilla>/`.
8. **Evaluación**: se generan `reports/metrics_<modelo>.csv`, `reports/confusion_<modelo>.png` y `reports/comparativa.csv`.
9. **Empaquetado del modelo final**: `models/beto_finetuned_final/` con `pytorch_model.bin`, `config.json`, `tokenizer/`, y `model_card.md`.

### 3.4.2 Flujo online (inferencia)

1. Cliente envía `POST /predict` con `{texto}`.
2. Validación Pydantic.
3. Tokenización en el backend.
4. Forward pass del modelo (con `torch.no_grad()`).
5. Softmax y umbral.
6. Logging anónimo (sin almacenar el texto, salvo modo debug).
7. Respuesta JSON con `{etiqueta, probabilidad, modelo, version}`.

### 3.4.3 Flujo de detección automática en la extensión

1. Usuario activa la detección desde el popup (consentimiento explícito).
2. Content script escanea nodos visibles del DOM.
3. Capa local: lexicón personal del usuario se aplica de inmediato (sin red).
4. Capa ML: fragmentos `≤ 512` caracteres se envían en batches al backend con cola y debounce.
5. Backend responde; el content script resalta los fragmentos `hate` con probabilidad `≥ umbral`.
6. Si el usuario solicita explicación, se invoca `POST /explain` y se subrayan tokens por peso SHAP.

## 3.5 Dependencias entre módulos

| Módulo | Depende de | Justificación |
|--------|------------|---------------|
| Lexicón LATAM | — | Componente fundacional. |
| Módulo de Datos | Lexicón LATAM | Necesita marcar `tiene_modismo`. |
| Módulo de Modelado | Módulo de Datos | Consume el corpus particionado. |
| Módulo de Evaluación | Módulo de Modelado | Necesita predicciones de cada modelo. |
| Módulo de XAI | Módulo de Modelado | Necesita el modelo entrenado final. |
| Backend API | Módulo de Modelado, XAI | Carga el modelo y expone XAI. |
| Extensión | Backend API | Consume contrato HTTP/JSON. |

El grafo es **acíclico**: ningún módulo de capa inferior depende de uno de capa superior. Esto facilita pruebas unitarias y de integración aisladas.

## 3.6 Decisiones de diseño y justificación

| Decisión | Alternativa descartada | Justificación |
|----------|------------------------|---------------|
| **Backend desacoplado (FastAPI)** | Servir el modelo desde la extensión vía ONNX/TF.js | Tamaño del modelo BETO (~440 MB) inviable en navegador; FastAPI ofrece tipado, OpenAPI y simplicidad. |
| **Etiquetado binario** | Etiquetado multiclase fino | Compatibilidad entre datasets heterogéneos; la H1–H3 se formula a nivel binario. |
| **Lexicón como feature observable, no como input al modelo** | Concatenar marcadores al input | Mantiene el modelo como **caja negra evaluable**; el lexicón se usa para **segmentar evaluación** (H3), no para inflar el desempeño artificialmente. |
| **3 semillas con media ± std** | Una sola semilla | Neutraliza la varianza intrínseca del fine-tuning de Transformers (Mosbach et al., 2021). |
| **McNemar pareado** | t-test sobre métricas | McNemar es el test estándar para clasificadores pareados sobre el mismo conjunto de prueba. |
| **Manifest V3 vanilla** | React/Vue en la extensión | Reduce el peso, evita herramientas de build adicionales y simplifica la auditoría del jurado. |
| **Detección automática opt-in** | Always-on | Privacidad por defecto: ningún texto sale del navegador sin consentimiento explícito. |

## 3.7 Riesgos arquitectónicos

| Riesgo | Impacto | Probabilidad | Mitigación arquitectónica |
|--------|---------|--------------|---------------------------|
| El backend cae mientras la extensión está activa | Alta | Media | Health-check periódico; modo degradado (solo lexicón local). |
| Acoplamiento entre versión de modelo y contrato de API | Alta | Baja | Endpoint `/metadata` con `model_version`; cliente valida. |
| Latencia del modelo en CPU > 1.5 s | Media | Media | Cuantización dinámica; cola con concurrencia limitada; truncamiento agresivo. |
| Cambios en políticas de Manifest V3 | Media | Baja | Documentar la versión usada; abstraer fetch en un único módulo. |
| Mezcla involuntaria entre **lexicón LATAM (científico)** y **lexicón personal (usuario)** | Alta para integridad metodológica | Media | Carpetas y nombres distintos; el lexicón personal vive **solo** en `chrome.storage.local`, jamás en `data/`. |

---

# 4. STACK TECNOLÓGICO Y ENTORNO

## 4.1 Lenguajes y runtimes

| Capa | Tecnología | Versión mínima |
|------|------------|----------------|
| ML / Backend | Python | 3.10 |
| Extensión | JavaScript (ES2022) | — |
| Notebook | Jupyter | — |
| Empaquetado | `pip` + `venv` (alternativa `conda`) | — |

## 4.2 Bibliotecas Python clave

| Biblioteca | Uso |
|------------|-----|
| `transformers` (≥ 4.40) | Modelos y tokenizadores (BETO, mBERT, XLM-R). |
| `torch` (≥ 2.2) | Backend de cómputo, CUDA opcional. |
| `datasets` (≥ 2.18) | Carga eficiente y mapeo perezoso. |
| `scikit-learn` (≥ 1.4) | Métricas, particionado estratificado, pesos por clase. |
| `pandas` / `numpy` | Manipulación tabular y numérica. |
| `pyarrow` | Backend para Parquet (formato de almacenamiento). |
| `fastapi`, `uvicorn`, `pydantic` (v2) | Backend REST. |
| `shap` (≥ 0.45) | Explicabilidad. |
| `statsmodels` (≥ 0.14) | Test de McNemar. |
| `matplotlib`, `seaborn` | Gráficos científicos. |
| `emoji`, `unidecode`, `regex` | Normalización textual. |
| `pytest`, `pytest-cov` | Tests del backend y de utilidades. |
| `python-dotenv` | Variables de entorno locales. |
| `ruff`, `black` | Linter y formateo. |
| `pre-commit` | Hooks de calidad. |

## 4.3 `requirements.txt` propuesto

```text
transformers>=4.40,<5.0
torch>=2.2
datasets>=2.18
scikit-learn>=1.4
pandas>=2.1
numpy>=1.26
pyarrow>=15.0
fastapi>=0.110
uvicorn[standard]>=0.27
pydantic>=2.6
shap>=0.45
statsmodels>=0.14
matplotlib>=3.8
seaborn>=0.13
emoji>=2.10
unidecode>=1.3
regex>=2024.0
python-dotenv>=1.0
pytest>=8.0
pytest-cov>=5.0
httpx>=0.27
```

## 4.4 Entornos de ejecución

| Entorno | Uso recomendado | Notas |
|---------|------------------|-------|
| **PC local con GPU** (≥ 6 GB VRAM) | Desarrollo y entrenamientos cortos. | Instalar PyTorch con la rueda CUDA correcta. |
| **Google Colab (T4)** | Entrenamientos completos. | Montar Drive; subir corpus en Parquet para velocidad. |
| **Kaggle Notebooks (P100)** | Repetición con semillas adicionales. | 30 h/sem gratuitas; ideal para variabilidad. |
| **PC local sin GPU** | Solo backend e inferencia. | Usar cuantización dinámica si la latencia molesta. |

## 4.5 Reproducibilidad del entorno

- Fijar versiones exactas con `pip freeze > requirements.lock.txt` después de validar.
- Mantener `environment.yml` (conda) opcional, espejo del `requirements.txt`.
- Registrar la versión de CUDA, de Python y del SO en `EXPERIMENTOS.md`.
- Toda ejecución relevante debe imprimir, al inicio, un *banner* con: versión del código (commit hash), versión del corpus, versión del lexicón, semilla y dispositivo.

---

# 5. ORGANIZACIÓN DEL REPOSITORIO

## 5.1 Estructura propuesta

```
Tesis_Proyecto/
├── README.md                         # visión rápida, comandos básicos
├── EXPERIMENTOS.md                   # bitácora científica obligatoria
├── guia.md                           # este documento maestro
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                    # config de ruff/black/pytest
├── requirements.txt
├── requirements.lock.txt
├── environment.yml                   # alternativa conda
├── Makefile                          # atajos: make data, make train, make api
│
├── data/
│   ├── raw/                          # datasets descargados, NO modificar
│   │   ├── hateval/
│   │   ├── mexa3t/
│   │   └── detoxis/
│   ├── interim/                      # versiones limpiadas individualmente
│   ├── processed/                    # corpus unificado + particiones
│   │   ├── corpus_v1.parquet
│   │   ├── corpus_v1_enriquecido.parquet
│   │   ├── train.parquet
│   │   ├── val.parquet
│   │   └── test.parquet
│   ├── lexicons/
│   │   ├── modismos_latam_v1.csv
│   │   └── README.md                 # fuentes y procedimiento
│   └── reports_qc/                   # reportes de control de calidad
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
│   ├── __init__.py
│   ├── config.py                     # paths, semillas, constantes
│   ├── data/
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── clean.py
│   │   ├── unify.py
│   │   ├── lexicon.py
│   │   ├── enrich.py
│   │   ├── split.py
│   │   └── qc.py                     # quality control
│   ├── modeling/
│   │   ├── __init__.py
│   │   ├── tokenize.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── losses.py                 # weighted CE, focal opcional
│   │   └── checkpoints.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── bootstrap.py
│   │   ├── mcnemar.py
│   │   └── errors.py                 # análisis de errores
│   ├── xai/
│   │   ├── __init__.py
│   │   └── shap_explainer.py
│   └── api/
│       ├── __init__.py
│       ├── main.py
│       ├── schemas.py
│       ├── inference.py
│       ├── xai.py
│       ├── config.py
│       └── logging_conf.py
│
├── extension/
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── lexicon.js
│   ├── api.js
│   ├── popup.html
│   ├── popup.js
│   ├── options.html
│   ├── options.js
│   ├── styles.css
│   └── icons/
│
├── models/                           # checkpoints, NO versionar pesos
│   ├── .gitkeep
│   └── README.md                     # cómo se nombran y dónde se guardan
│
├── tests/
│   ├── unit/
│   │   ├── test_clean.py
│   │   ├── test_lexicon.py
│   │   ├── test_metrics.py
│   │   └── test_schemas.py
│   ├── integration/
│   │   ├── test_pipeline_data.py
│   │   └── test_api.py
│   └── conftest.py
│
├── reports/                          # salidas del experimento
│   ├── tables/
│   ├── figures/
│   └── logs/
│
├── docs/                             # documentación adicional
│   ├── arquitectura.md
│   ├── decisiones.md
│   ├── modelo.md
│   └── glosario.md
│
└── scripts/                          # entrypoints CLI
    ├── prepare_data.py
    ├── train_model.py
    ├── evaluate_model.py
    ├── run_api.sh
    └── package_model.py
```

## 5.2 Convenciones de nombres

- **Archivos de datos**: `corpus_v{n}[_enriquecido].parquet`, `train.parquet`, etc. Nunca se sobreescribe una versión; se incrementa `n`.
- **Modelos**: `{arquitectura}_{variante}_{semilla}/`, p. ej. `beto_finetuned_42/`, `xlm-r_baseline_2024/`.
- **Modelo final empaquetado**: `beto_finetuned_final/` (sin semilla; representa el modelo seleccionado para producción).
- **Reportes**: `metrics_{modelo}_{semilla}.csv`, `confusion_{modelo}_{semilla}.png`.
- **Notebooks**: `NN_proposito.ipynb` con índice de dos dígitos para forzar el orden.
- **Tests**: `test_<modulo>.py`; función `test_<comportamiento>()`.
- **Ramas git** (sugerido): `data/<tarea>`, `model/<tarea>`, `api/<tarea>`, `ext/<tarea>`, `docs/<tarea>`.

## 5.3 `.gitignore` mínimo

```gitignore
__pycache__/
.venv/
.env
.ipynb_checkpoints/
data/raw/
data/interim/
models/*/
!models/.gitkeep
!models/README.md
reports/logs/
*.bin
*.safetensors
*.pt
```

Los **pesos** del modelo nunca se versionan en git. Se publican aparte (Hugging Face Hub, Drive con enlace en `models/README.md`, o release de GitHub).

## 5.4 Makefile sugerido

```makefile
.PHONY: install data train evaluate api test lint

install:
	pip install -r requirements.txt
	pre-commit install

data:
	python scripts/prepare_data.py --version 1

train:
	python scripts/train_model.py --model beto --seed 42
	python scripts/train_model.py --model beto --seed 123
	python scripts/train_model.py --model beto --seed 2024

evaluate:
	python scripts/evaluate_model.py --all

api:
	bash scripts/run_api.sh

test:
	pytest --cov=src --cov-report=term-missing

lint:
	ruff check src tests
	black --check src tests
```

---

# 6. GESTIÓN DE DATOS: ESTRATEGIA, ALMACENAMIENTO, VERSIONADO Y CALIDAD

## 6.1 Estrategia de almacenamiento

Se adopta la convención **medallion** (raw → interim → processed) propia de proyectos de datos reproducibles:

- **`data/raw/`**: datasets tal como se descargaron. **Inmutable**. Cualquier modificación se considera un error de proceso.
- **`data/interim/`**: cada dataset, limpio individualmente, con su esquema canónico, en formato Parquet. Reproducible mediante script.
- **`data/processed/`**: corpus unificado y enriquecido + particiones `train/val/test`. Es el único insumo del entrenamiento.

**Formato preferido**: Parquet (`pyarrow`), no CSV, por:
- Tipado fuerte (booleanos no se convierten en strings).
- 5–10× más rápido de leer.
- Compresión por columnas.
- Soporte de metadatos a nivel de archivo.

## 6.2 Versionado de datasets

Cada artefacto en `processed/` lleva un **sufijo de versión** (`_v1`, `_v2`, …). Las versiones nunca se sobreescriben. Cada versión se asocia a:

- Un **commit hash** del repo (registrado en `data/processed/MANIFEST.json`).
- Un **hash SHA-256** del archivo (verificable).
- Un **changelog** en `data/processed/CHANGELOG.md` explicando qué cambió y por qué.

Ejemplo de `MANIFEST.json`:

```json
{
  "corpus": {
    "version": 1,
    "file": "corpus_v1_enriquecido.parquet",
    "sha256": "a3f1...",
    "git_commit": "9d2b1e7",
    "created_at": "2026-06-12T14:30:00Z",
    "datasets_origen": ["hateval-2019", "mexa3t-2020", "detoxis-2021"],
    "lexicon_version": "modismos_latam_v1.csv",
    "n_total": 38421,
    "n_hate": 11250,
    "n_no_hate": 27171
  }
}
```

Esto permite que en la defensa cualquier resultado pueda referenciarse a una versión exacta de datos.

## 6.3 Convenciones de nombres y tipos

Esquema canónico del corpus:

| Columna | Tipo Parquet | Restricción |
|---------|--------------|-------------|
| `id` | `string` | Único; formato `<dataset>_<n>`. |
| `texto` | `string` | No nulo, longitud ≥ 3 tokens. |
| `etiqueta` | `int8` | `{0, 1}`. |
| `dataset` | `category` | Origen. |
| `tiene_modismo` | `bool` | Calculado, no nulo. |
| `pais` | `category` | Opcional, `{MX, ES, AR, CO, CL, PE, VE, ...}` o `UNK`. |
| `n_tokens_aprox` | `int16` | Útil para análisis. |

## 6.4 Validaciones automáticas (Quality Control)

`src/data/qc.py` define un conjunto de aserciones que se ejecutan al final del pipeline. Si alguna falla, el proceso se interrumpe.

```python
def validar_corpus(df: pd.DataFrame) -> None:
    assert df["id"].is_unique, "IDs duplicados"
    assert df["texto"].notna().all(), "Textos nulos"
    assert df["texto"].str.split().str.len().min() >= 3, "Textos muy cortos"
    assert set(df["etiqueta"].unique()) <= {0, 1}, "Etiquetas fuera de {0,1}"
    assert df["tiene_modismo"].dtype == bool, "tiene_modismo no es bool"
    prop_hate = df["etiqueta"].mean()
    assert 0.05 <= prop_hate <= 0.60, f"Proporción hate fuera de rango: {prop_hate:.2f}"
```

Resultados que **siempre** se reportan a `data/reports_qc/qc_corpus_v{n}.md`:

- Tamaño total.
- Distribución de clases (global y por dataset).
- Distribución de `tiene_modismo` (global y por clase).
- Longitudes (mediana, p95) de texto en tokens y caracteres.
- Top 50 unigramas y bigramas por clase (sanity check de contenido).
- Conteo de duplicados eliminados.
- Conteo de filas descartadas por reglas de longitud.

## 6.5 Detección de duplicados

Estrategia en **tres niveles**, en orden creciente de costo:

1. **Duplicados exactos**: `df.drop_duplicates(subset=["texto"])`.
2. **Duplicados normalizados**: misma cadena tras `lower + strip + colapsar espacios + quitar emojis + quitar puntuación`.
3. **Duplicados aproximados** (opcional): MinHash + LSH (`datasketch`) con umbral Jaccard ≥ 0.9.

El nivel 3 es opcional por costo, pero recomendado para evitar fuga entre `train` y `test` cuando dos datasets comparten tuits con pequeñas variaciones.

Pseudocódigo de fuga (data leakage check):

```
sea T = textos normalizados de train
sea V = textos normalizados de test
asumir |T ∩ V| == 0    # si no, eliminar de test
```

## 6.6 Manejo de ruido

Tipos de ruido identificados y tratamiento:

| Ruido | Tratamiento |
|-------|-------------|
| Encoding roto (`Ã©`, mojibake) | Reparar con `ftfy.fix_text`. |
| HTML embebido (`&amp;`, `<br>`) | `html.unescape` + regex de tags. |
| Espacios múltiples, tabs, saltos | Colapsar con `re.sub(r"\s+", " ", t).strip()`. |
| Caracteres invisibles (zero-width) | Eliminar con regex Unicode (`\u200b–\u200f`). |
| URLs, menciones, hashtags | Normalizar a tokens `URL`, `USUARIO`, descomponer hashtag. |
| Emojis | Convertir a tokens textuales (`:cara_enojada:`) con `emoji.demojize(language="es")`. |
| Repeticiones extremas (`holaaaaaa`) | Colapsar a máximo 2 caracteres repetidos. |

## 6.7 Manejo de clases desbalanceadas

El discurso de odio en corpus reales suele tener entre **10 % y 35 %** de positivos. Estrategias:

1. **Pesos por clase en la pérdida** (recomendado por defecto):

   ```python
   from sklearn.utils.class_weight import compute_class_weight
   w = compute_class_weight("balanced", classes=np.array([0, 1]),
                            y=train["etiqueta"].values)
   ```

   Se inyecta en una `CrossEntropyLoss(weight=torch.tensor(w))` dentro de un `Trainer` con `compute_loss` sobrescrito.

2. **Oversampling controlado** de la clase minoritaria solo en `train` (`RandomOverSampler` o repetición ponderada). Mantener `val` y `test` con distribución natural.

3. **Focal Loss** (opcional, no obligatorio): `(1-p)^γ * CE` con γ=2; útil si el modelo ignora la clase minoritaria.

4. **Métrica de selección**: nunca usar Accuracy como criterio. Siempre **F1 de la clase `hate`** o **F1 macro**. `metric_for_best_model="f1"` en `TrainingArguments`.

5. **Threshold tuning** post-hoc: ajustar el umbral de decisión (no necesariamente 0.5) maximizando F1 sobre `val`, y aplicarlo en `test`.

## 6.8 Control de calidad continuo

- **Pre-commit hook** que ejecuta `pytest -k qc` y `ruff` antes de cada commit.
- **CI opcional** (GitHub Actions): test del pipeline de datos sobre una muestra sintética del repo.
- **Snapshot tests** sobre las primeras 10 filas del corpus tras cada versión, para detectar regresiones silenciosas.

---

# 7. CONSTRUCCIÓN DEL CORPUS UNIFICADO

## 7.1 Selección de datasets

Se utilizan **cuatro** datasets públicos en español de calidad académica, seleccionados por cobertura temática, disponibilidad y dialectos representados:

| Dataset | Origen | Tipo | Características |
|---------|--------|------|-----------------|
| **HatEval 2019** (SemEval-2019 Task 5) | Twitter ES/EN | Hate / no hate (mujeres, inmigrantes) | 6,600 tweets en español; estándar internacional; anotación multiclase. |
| **DETOXIS** (IberLEF 2021) | Comentarios noticias ES | Toxicidad multinivel + 20 dimensiones | 5,249 comentarios; anotación granular; nivel de toxicidad ordinal. |
| **HaterNet** | Twitter ES | Hate / no hate (binario) | 6,000 tweets; dataset clásico 2017; volumen adicional. |
| **Chilean Dataset** | Twitter CL | Hate / estereotipo + 17 dimensiones | 31,609 tweets; modismos chilenos auténticos; contexto sociopolítico. |

**Justificación de la combinación**: Esta selección equilibra:
- **Dialecto español (España):** HatEval, DETOXIS, HaterNet
- **Dialecto latinoamericano (Chile):** Chilean Dataset
- **Plataformas:** Twitter (HatEval, HaterNet, Chilean) + Comentarios de noticias (DETOXIS)
- **Anotación granular:** DETOXIS (20 dims) + Chilean (17 dims) para análisis fino de modismos
- **Volumen:** ~49,000 ejemplos en total antes de limpieza

**Descargas reales:**
- **HatEval 2019:** https://huggingface.co/datasets/valeriobasile/HatEval
- **DETOXIS:** https://github.com/alvaro-mazcu-herreros/DETOXIS_2021
- **HaterNet:** https://zenodo.org/records/2592149
- **Chilean Dataset:** https://github.com/aymeam/Datasets-for-Hate-Speech-Detection/tree/master/Chilean%20dataset

## 7.2 Pipeline completo (visión general)

```
[datasets crudos] → cargar → validar esquema → limpiar → normalizar →
   → mapear etiquetas a binario → concatenar → deduplicar →
   → enriquecer (tiene_modismo) → validar QC → particionar →
   → guardar y registrar versión
```

## 7.3 Pseudocódigo del pipeline

```python
def construir_corpus(version: int) -> Path:
    dfs = []
    for nombre, loader in DATASETS.items():
        df_raw = loader.cargar()
        validar_esquema(df_raw, nombre)
        df = limpiar(df_raw, nombre)
        df = normalizar(df)
        df = mapear_etiquetas(df, nombre)
        df = a_esquema_canonico(df, nombre)
        dfs.append(df)

    corpus = pd.concat(dfs, ignore_index=True)
    corpus = deduplicar(corpus)
    corpus = enriquecer_con_lexicon(corpus, LEXICON_PATH)
    validar_corpus(corpus)

    out = PROCESSED / f"corpus_v{version}_enriquecido.parquet"
    corpus.to_parquet(out, compression="snappy")
    registrar_version(out, version)
    return out
```

## 7.4 Limpieza y normalización

**Principio rector**: limpiar lo necesario para reducir ruido, **sin destruir señal**. BETO `cased` requiere mayúsculas; no se aplica `lower`.

```python
import re, emoji, html
from ftfy import fix_text

URL_RE     = re.compile(r"http\S+|www\.\S+")
MENCION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
ZWSP_RE    = re.compile(r"[\u200b-\u200f\u202a-\u202e]")
REPEAT_RE  = re.compile(r"(.)\1{2,}")

def normalizar(texto: str) -> str:
    texto = fix_text(texto)
    texto = html.unescape(texto)
    texto = ZWSP_RE.sub("", texto)
    texto = URL_RE.sub(" URL ", texto)
    texto = MENCION_RE.sub(" USUARIO ", texto)
    texto = HASHTAG_RE.sub(r" \1 ", texto)
    texto = emoji.demojize(texto, language="es")
    texto = REPEAT_RE.sub(r"\1\1", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto
```

**No se aplica**: stemming, lematización, eliminación de stopwords, `lower`. Cada una de estas operaciones degrada el desempeño de BERT.

## 7.5 Mapeo de etiquetas

Cada dataset trae su propio esquema. La normalización a binario debe **documentarse**:

| Dataset | Etiqueta original | Etiqueta unificada |
|---------|-------------------|--------------------|
| HatEval | `HS = 1` | 1 |
| HatEval | `HS = 0` | 0 |
| MEX-A3T | `aggressive` | 1 |
| MEX-A3T | `non-aggressive` | 0 |
| DETOXIS | `toxicity_level ≥ 2` | 1 |
| DETOXIS | `toxicity_level < 2` | 0 |
| HaterNet | `1` (odio) | 1 |
| HaterNet | `0` | 0 |
| OffendES | `OFP, OFG` | 1 |
| OffendES | `NOE, NO` | 0 |

Estas equivalencias deben quedar reflejadas en `notebooks/02_unificacion.ipynb` y en `docs/decisiones.md`. **Una pregunta inevitable del jurado es: “¿cómo unificó las etiquetas?”**.

## 7.6 Estrategia de enriquecimiento

El enriquecimiento agrega la columna `tiene_modismo` mediante el lexicón LATAM (sección 8). La función es **pura** y determinista:

```python
def tiene_modismo(texto: str, lexicon: set[str]) -> bool:
    tokens = re.findall(r"\w+", texto.lower())
    return any(t in lexicon for t in tokens)
```

**Importante**: el lexicón se aplica sobre el texto **ya normalizado** y en minúsculas, **solo** para detectar la presencia. El corpus que alimenta al modelo conserva el `texto` original (con mayúsculas).

## 7.7 Particionado

División estratificada por `etiqueta`, con porcentajes 70 / 15 / 15:

```python
from sklearn.model_selection import train_test_split

train, temp = train_test_split(
    corpus, test_size=0.30, stratify=corpus["etiqueta"], random_state=42
)
val, test = train_test_split(
    temp, test_size=0.50, stratify=temp["etiqueta"], random_state=42
)
```

**Reglas inviolables**:

- El `test` se **congela** desde el día uno.
- Nunca se mira `test` para ajustar hiperparámetros.
- Si se descubre un problema en `train` o `val`, se corrige, se reentrena y, **solo entonces**, se evalúa una sola vez en `test`.

## 7.8 Validación del corpus

Tras el particionado, generar `data/reports_qc/qc_corpus_v{n}.md` con:

- Tamaños de `train/val/test`.
- Distribución de clases en cada partición.
- Distribución de `tiene_modismo` en cada partición.
- Distribución de `dataset` de origen en cada partición.
- Top tokens por clase.
- Histograma de longitudes.
- Verificación de no-fuga entre `train` y `test` (intersección vacía).

## 7.9 Posibles errores y soluciones

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `KeyError` al leer un dataset | Cambio de cabeceras entre versiones | Pin de versión del archivo + asserts de esquema. |
| `tiene_modismo` siempre `False` | Lexicón vacío o ruta errónea | Test unitario que verifica que ≥ 5 % del corpus marca `True`. |
| Distribución de clases sospechosa | Mapeo de etiquetas mal | Revisar la tabla de mapeo y los conteos por dataset. |
| Fuga train↔test detectada | Datasets con tuits compartidos | Aplicar deduplicación cruzada entre particiones. |

---

# 8. LEXICÓN DE MODISMOS LATINOAMERICANOS (LEXICÓN DE INVESTIGACIÓN)

> **Aviso clave**: este lexicón es de **investigación**, se usa para enriquecer el corpus y validar H3. Es distinto del **lexicón personal del usuario** que vive en la extensión (sección 15). Bajo ningún concepto deben mezclarse.

## 8.1 Objetivo

Disponer de un recurso léxico con cobertura suficiente de modismos, coloquialismos e insultos regionales de uso latinoamericano, que permita marcar de forma reproducible cada instancia del corpus como `con_modismo` o `sin_modismo`.

## 8.2 Estrategia de construcción

Tres fuentes, combinadas:

1. **Diccionario de Americanismos (ASALE)**: términos marcados como propios de uno o más países LATAM. Es la fuente más citable y autoritativa.
2. **Literatura científica**: listas referenciadas en trabajos previos sobre jerga regional y discurso de odio en redes (Moreno-Sandoval et al., 2024; Pérez et al., 2023; otros que se consulten).
3. **Curaduría manual** del tesista: términos coloquiales e insultos no incluidos en las fuentes anteriores, con anotación obligatoria del país y la fuente (medio, foro, observación). Esta curaduría se documenta para evitar la crítica de “lista ad hoc”.

## 8.3 Estructura del archivo

`data/lexicons/modismos_latam_v1.csv`:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `termino` | str | Forma canónica en minúsculas. |
| `variantes` | str | Variantes separadas por `;` (p. ej. `wei;weón;weon`). |
| `pais` | str | Código ISO o `MULTI`. |
| `tipo` | str | `{coloquial, intensificador, insulto, despectivo, juvenil}`. |
| `fuente` | str | `ASALE` / `Moreno-Sandoval2024` / `curado_manual`. |
| `notas` | str | Aclaraciones de uso o ambigüedad. |
| `version_introduccion` | int | Versión del lexicón en la que aparece. |

Ejemplos:

| termino | variantes | pais | tipo | fuente | notas |
|---------|-----------|------|------|--------|-------|
| weón | wei;weon;weón | CL | coloquial | ASALE | Puede ser amistoso o insulto. |
| pinche | pinche | MX | intensificador | ASALE | Marcador frecuente de ofensa. |
| parce | parce;parcero | CO | coloquial | ASALE | Neutro. |
| chamo | chamo;chama | VE | coloquial | curado_manual | Neutro. |
| naco | naco;naca | MX | despectivo | ASALE | Clasista. |
| ñero | ñero | CO | despectivo | ASALE | Clasista. |

## 8.4 Cobertura esperada

- **Tamaño**: ≥ 500 términos canónicos.
- **Cobertura geográfica mínima**: MX, AR, CL, CO, PE, VE, EC (al menos 30 términos por país).
- **Cobertura tipológica**: ≥ 100 términos por categoría `tipo` (excepto categorías inherentemente pequeñas).
- **Cobertura sobre el corpus**: ≥ 15 % de las instancias deben quedar marcadas como `tiene_modismo = True`. Si la cobertura es menor, se amplía el lexicón hasta alcanzarlo (sin contaminar `test`).

## 8.5 Proceso de validación

1. **Validación interna del lexicón**:
   - Sin duplicados de `termino`.
   - Sin entradas vacías en columnas obligatorias.
   - Países válidos según ISO o `MULTI`.
   - Test unitario en `tests/unit/test_lexicon.py`.

2. **Validación de aplicación sobre el corpus**:
   - Tomar 100 textos marcados `True` y 100 marcados `False`.
   - Anotación manual de “¿realmente contiene un modismo LATAM?”.
   - Calcular **Precision** (% de True correctos) y **Recall aproximado** (% de modismos reales detectados) del flag.
   - Reportar la matriz de confusión del flag en `docs/decisiones.md`.

3. **Validación cualitativa**:
   - Confirmar que los términos no son exclusivos del español peninsular (sería una contradicción con la hipótesis).
   - Confirmar que ningún término del lexicón es exclusivo de hate; el lexicón LATAM **no es** un lexicón de odio.

## 8.6 Sesgos posibles

| Sesgo | Riesgo | Mitigación |
|-------|--------|------------|
| Sobre-representación de México | Marca como `con_modismo` mayoritariamente textos MX | Equilibrar manualmente: cuota mínima por país. |
| Términos polisémicos (`weón` puede ser amistoso) | Falsos positivos en `tiene_modismo` | Aceptar el flag como “contiene léxico LATAM”, no como “contiene insulto”. |
| Curaduría sesgada por el tesista | Cuestionamiento metodológico | Citar fuente para cada entrada; validar manualmente una muestra. |
| Variación temporal | Modismos obsoletos o emergentes | Versionar el lexicón; documentar fecha de construcción. |

## 8.7 Mantenimiento futuro

- Cada modificación produce una **nueva versión** del archivo (`_v2`, `_v3`, …); no se sobreescribe.
- Cada versión queda registrada en `data/lexicons/CHANGELOG.md`.
- Si se reentrena el modelo con una nueva versión del lexicón, **se reentrenan también los baselines** sobre el mismo corpus enriquecido para mantener comparabilidad.

---

# 9. FINE-TUNING DE BETO: GUÍA TÉCNICA COMPLETA

## 9.1 Explicación conceptual

BETO es una variante de BERT preentrenada exclusivamente en español por el Departamento de Ciencias de la Computación de la Universidad de Chile (Cañete et al., 2020). Hereda la arquitectura BERT-base (12 capas, 12 cabezales, dimensión 768, ~110 M de parámetros). Existen variantes `cased` y `uncased`; se recomienda **`cased`** porque el discurso de odio explota patrones de mayúsculas (gritos, intensificación) que el `uncased` destruye.

El **fine-tuning** consiste en cargar los pesos preentrenados y añadir una **cabeza de clasificación** lineal sobre el token `[CLS]`. Todos los parámetros se reajustan con una tasa de aprendizaje baja (`2e-5`) durante pocas épocas (3–5). Es un proceso barato computacionalmente comparado con el preentrenamiento.

## 9.2 Descarga del modelo

Identificador en Hugging Face:

```
dccuchile/bert-base-spanish-wwm-cased
```

Descarga explícita y caché controlada:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"
CACHE_DIR  = "models/_hf_cache"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model     = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2, cache_dir=CACHE_DIR
)
```

Documentar la **versión exacta del modelo** (commit hash de Hugging Face) en `EXPERIMENTOS.md`.

## 9.3 Tokenización

```python
def tokenize(batch):
    return tokenizer(
        batch["texto"],
        truncation=True,
        max_length=128,
        padding=False,
    )
```

**Por qué `max_length=128`**: cubre el 95 % de los tuits del corpus (estadística empírica del paso 6.4). Si el corpus contiene textos largos (comentarios de noticias), subir a 256 y reportar el cambio.

**Padding dinámico**: usar `DataCollatorWithPadding(tokenizer)` para no padear al máximo global, lo que ahorra 30–50 % de cómputo.

## 9.4 Preparación de los datasets para `Trainer`

```python
from datasets import Dataset

train_ds = Dataset.from_pandas(train_df[["texto", "etiqueta"]])
val_ds   = Dataset.from_pandas(val_df[["texto", "etiqueta"]])
test_ds  = Dataset.from_pandas(test_df[["texto", "etiqueta"]])

for ds in (train_ds, val_ds, test_ds):
    ds = ds.rename_column("etiqueta", "labels")

train_ds = train_ds.map(tokenize, batched=True)
val_ds   = val_ds.map(tokenize, batched=True)
test_ds  = test_ds.map(tokenize, batched=True)
```

## 9.5 Configuración del entrenamiento

```python
from transformers import (
    TrainingArguments, Trainer, DataCollatorWithPadding,
    EarlyStoppingCallback,
)
import numpy as np, torch
from sklearn.utils.class_weight import compute_class_weight

SEMILLA = 42
torch.manual_seed(SEMILLA); np.random.seed(SEMILLA)

class_weights = compute_class_weight(
    "balanced", classes=np.array([0, 1]), y=train_df["etiqueta"].values
)
class_weights_t = torch.tensor(class_weights, dtype=torch.float)

args = TrainingArguments(
    output_dir=f"models/beto_finetuned_{SEMILLA}",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    fp16=torch.cuda.is_available(),
    seed=SEMILLA,
    report_to="none",
    save_total_limit=2,
    logging_steps=50,
)
```

## 9.6 Class weights vía `Trainer` personalizado

```python
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=class_weights_t.to(logits.device)
        )
        loss = loss_fct(logits.view(-1, 2), labels.view(-1))
        return (loss, outputs) if return_outputs else loss
```

## 9.7 Métrica de validación

```python
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(-1)
    p, r, f, _ = precision_recall_fscore_support(
        labels, preds, average="binary", pos_label=1, zero_division=0
    )
    return {
        "precision": p, "recall": r, "f1": f,
        "accuracy": accuracy_score(labels, preds),
    }
```

## 9.8 Entrenamiento

```python
trainer = WeightedTrainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
)

trainer.train()
trainer.save_model(f"models/beto_finetuned_{SEMILLA}")
tokenizer.save_pretrained(f"models/beto_finetuned_{SEMILLA}")
```

## 9.9 Early stopping

- `EarlyStoppingCallback(patience=2)`: si la métrica F1 en `val` no mejora durante 2 evaluaciones consecutivas, el entrenamiento se detiene.
- Esto evita el sobreajuste y reduce tiempo de cómputo.

## 9.10 Reproducibilidad

- `seed=42` en `TrainingArguments` + `torch.manual_seed`/`np.random.seed`.
- Variables `PYTHONHASHSEED=42`, `CUBLAS_WORKSPACE_CONFIG=:4096:8` para CUDA determinístico.
- `torch.use_deterministic_algorithms(True)` (puede penalizar velocidad).
- Tres semillas: `{42, 123, 2024}`. Reportar media ± desviación estándar (sección 11).
- Banner inicial obligatorio en el log:

  ```
  ======================================
   BETO fine-tuning
   commit: <git rev>
   corpus: corpus_v1_enriquecido.parquet (sha256: <hash>)
   lexicon: modismos_latam_v1.csv (sha256: <hash>)
   semilla: 42
   device: cuda:0 (NVIDIA T4)
   transformers: 4.41.2
  ======================================
  ```

## 9.11 Gestión de checkpoints

- `save_strategy="epoch"` + `save_total_limit=2` mantiene solo los 2 mejores.
- `load_best_model_at_end=True` carga el mejor según `metric_for_best_model`.
- Tras el entrenamiento, `trainer.save_model` produce un directorio con:
  - `config.json`
  - `pytorch_model.bin` (o `model.safetensors`)
  - `tokenizer.json`, `vocab.txt`, `special_tokens_map.json`, `tokenizer_config.json`
- Para el **modelo final**, se elige la mejor semilla (o un ensemble simple por voto mayoritario sobre las 3 semillas) y se copia a `models/beto_finetuned_final/` con un `model_card.md`:

  ```markdown
  # BETO ajustado — Detección de discurso de odio en español

  - Versión de corpus: corpus_v1_enriquecido.parquet
  - Semilla seleccionada: 42
  - F1 (hate) val: 0.81 ± 0.012
  - F1 (hate) test: 0.79 [0.77, 0.81] (bootstrap 95%)
  - Hash SHA-256: ...
  - Licencia del modelo base: MIT (Cañete et al., 2020)
  ```

## 9.12 Posibles errores y soluciones

| Error / síntoma | Causa | Solución |
|------------------|------|----------|
| `CUDA out of memory` | Batch demasiado grande | Reducir `batch_size` a 8; activar `gradient_accumulation_steps=2`. |
| F1 estancado en 0 | Predice siempre la mayoritaria | Confirmar `class_weights`; bajar LR a `1e-5`; reentrenar con más épocas. |
| Loss `nan` | `fp16` con LR alto | Desactivar `fp16` o bajar LR; revisar valores extremos en datos. |
| F1 muy variable entre semillas | Varianza típica de Transformers | Confirmar las 3 semillas; reportar media ± std (es esperable). |
| `Trainer` no usa las clases personalizadas | Versión vieja de `transformers` | Pinning a ≥ 4.40. |
| Tokenización rompe acentos | `unidecode` aplicado por error | Quitar `unidecode` del pipeline; BETO `cased` requiere acentos. |
| Evaluación lenta | `eval_batch_size` muy pequeño | Subir a 64 si VRAM lo permite. |
| Modelo guardado pero no se puede recargar | Falta `tokenizer.save_pretrained` | Guardar siempre tokenizer junto al modelo. |

---

# 10. BASELINES: BETO BASE, mBERT Y XLM-R

## 10.1 BETO base (referencia para H1)

“BETO base” en el contexto de la tesis significa **BETO sin el beneficio del corpus enriquecido**. Dos operacionalizaciones son válidas; debe elegirse **una** y declararla explícitamente:

### Opción A (recomendada): BETO base entrenado sobre un único dataset genérico

- Mismo modelo `dccuchile/bert-base-spanish-wwm-cased`.
- Cabeza de clasificación entrenada **solo** sobre HatEval, sin unificación con MEX-A3T/DETOXIS ni enriquecimiento con lexicón LATAM.
- Mismo protocolo de tokenización, batch, LR, épocas, semillas.
- Evaluación sobre el **mismo `test`** del corpus unificado.

Esta operacionalización aísla el efecto del **corpus enriquecido + unificación**, que es justamente la contribución metodológica de la tesis.

### Opción B (cota inferior): BETO base sin fine-tuning específico (zero-shot)

- Cargar `dccuchile/bert-base-spanish-wwm-cased` y usar un clasificador NLI o un *masked language modeling probe*.
- Suele rendir mal; sirve para demostrar que el fine-tuning aporta valor.

**Decisión recomendada**: usar la Opción A como BETO base y, si se desea, reportar la Opción B en apéndice.

## 10.2 mBERT (`bert-base-multilingual-cased`)

- Modelo multilingüe (104 idiomas) preentrenado por Google.
- Tamaño similar a BETO (~177 M parámetros).
- Suele rendir por debajo de BETO en español monolingüe (Cañete et al., 2020), pero es un baseline obligatorio para H2.

## 10.3 XLM-R (`xlm-roberta-base`)

- Modelo multilingüe robusto preentrenado por Facebook AI.
- ~278 M parámetros.
- En tareas en español, suele igualar o superar a BETO en datasets grandes.
- LR recomendada ligeramente inferior: `1e-5` o `2e-5`.

## 10.4 Variables a mantener constantes entre modelos

Para que la comparación sea válida:

| Variable | Valor común |
|----------|-------------|
| Particiones `train/val/test` | Las mismas archivos en disco. |
| Semillas | `{42, 123, 2024}`. |
| Tamaño de batch | 16 (train), 32 (eval). |
| Épocas | 4 con early stopping `patience=2`. |
| `weight_decay` | 0.01. |
| `warmup_ratio` | 0.1. |
| `max_length` | 128 (o 256, consistente entre todos). |
| Estrategia de class weights | Idéntica. |
| Métrica de selección | F1 (hate). |
| Hardware | El mismo siempre que sea posible; si no, registrar el cambio. |

Variables que **pueden** variar (con justificación documentada):

- Learning rate: BETO/mBERT con `2e-5`, XLM-R con `1e-5` si se observa inestabilidad.
- Tokenizador: cada modelo usa el suyo. No se reemplazan.

## 10.5 Protocolo de comparación

1. Entrenar cada modelo con las 3 semillas.
2. Evaluar en `test` y calcular media ± std.
3. Calcular intervalos de confianza por bootstrap.
4. Aplicar test de McNemar pareado entre BETO ajustado y cada baseline (sección 11.7).
5. Reportar p-valores y tamaño de efecto.

## 10.6 Tabla esperada (esqueleto)

| Modelo | Precision (hate) | Recall (hate) | F1 (hate) | F1 macro | Accuracy | ROC-AUC |
|--------|-----------------:|--------------:|----------:|---------:|---------:|--------:|
| BETO base (Opción A) | x ± y | x ± y | x ± y | x ± y | x ± y | x ± y |
| **BETO ajustado (ours)** | x ± y | x ± y | x ± y | x ± y | x ± y | x ± y |
| mBERT | x ± y | x ± y | x ± y | x ± y | x ± y | x ± y |
| XLM-R | x ± y | x ± y | x ± y | x ± y | x ± y | x ± y |

---

# 11. EVALUACIÓN EXPERIMENTAL

## 11.1 Métricas reportadas

Sobre el `test set` congelado, por modelo y semilla:

- **Precision (hate)**: `TP / (TP + FP)`. Crítica en moderación: minimiza la censura indebida.
- **Recall (hate)**: `TP / (TP + FN)`. Crítica en protección: minimiza el contenido tóxico no detectado.
- **F1 (hate)**: media armónica; métrica principal de comparación.
- **F1 macro**: promedio de F1 por clase, robusto al desbalance.
- **Accuracy**: para contexto, **nunca** como criterio.
- **ROC-AUC**: separabilidad agnóstica al umbral.
- **Matriz de confusión** 2×2.

## 11.2 Cálculo en código

```python
from sklearn.metrics import (
    precision_recall_fscore_support, accuracy_score,
    confusion_matrix, roc_auc_score, classification_report
)

def evaluar(y_true, y_pred, y_proba_pos):
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    pm, rm, fm, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    return {
        "precision_hate": p, "recall_hate": r, "f1_hate": f,
        "precision_macro": pm, "recall_macro": rm, "f1_macro": fm,
        "accuracy": accuracy_score(y_true, y_pred),
        "roc_auc":  roc_auc_score(y_true, y_proba_pos),
        "confusion": confusion_matrix(y_true, y_pred).tolist(),
    }
```

## 11.3 Bootstrap para intervalos de confianza

Se remuestrea el `test set` con reposición B = 1000 veces; para cada muestra se recalcula la métrica. El intervalo de confianza al 95 % es el rango entre los percentiles 2.5 y 97.5.

```python
def bootstrap_ic(y_true, y_pred, metric_fn, B=1000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    vals = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        vals[b] = metric_fn(y_true[idx], y_pred[idx])
    lo = np.percentile(vals, 100 * alpha / 2)
    hi = np.percentile(vals, 100 * (1 - alpha / 2))
    return vals.mean(), lo, hi
```

Reportar como `F1 = 0.79 [0.77, 0.81]`.

## 11.4 Tabla comparativa principal (esperada)

| Modelo | Precision (hate) | Recall (hate) | F1 (hate) IC95% | F1 macro | Accuracy | ROC-AUC |
|--------|:----------------:|:-------------:|:---------------:|:--------:|:--------:|:-------:|
| BETO base | 0.72 ± 0.014 | 0.68 ± 0.018 | 0.70 [0.68, 0.72] | 0.78 ± 0.011 | 0.83 ± 0.009 | 0.86 ± 0.010 |
| **BETO ajustado (ours)** | **0.79 ± 0.012** | **0.77 ± 0.015** | **0.78 [0.76, 0.80]** | **0.84 ± 0.010** | **0.87 ± 0.008** | **0.91 ± 0.008** |
| mBERT | 0.74 ± 0.016 | 0.71 ± 0.017 | 0.72 [0.70, 0.74] | 0.80 ± 0.012 | 0.84 ± 0.010 | 0.88 ± 0.011 |
| XLM-R | 0.77 ± 0.013 | 0.75 ± 0.015 | 0.76 [0.74, 0.78] | 0.82 ± 0.011 | 0.86 ± 0.009 | 0.90 ± 0.009 |

> Los números son ilustrativos; el formato es vinculante.

## 11.5 Matriz de confusión

| | Pred no_hate | Pred hate |
|--:|:--:|:--:|
| **Real no_hate** | TN | FP |
| **Real hate** | FN | TP |

Reportar la matriz numérica y la visualización (heatmap) por modelo en `reports/figures/confusion_{modelo}.png`.

## 11.6 Curvas ROC y Precision-Recall

- **ROC** (`y_proba_pos` vs FPR/TPR): útil cuando el umbral es ajustable.
- **Precision-Recall**: más informativa en problemas desbalanceados; reportarla junto con ROC en `reports/figures/`.

## 11.7 Test de McNemar pareado

Compara dos clasificadores sobre el **mismo** test set. Tabla 2×2:

| | Modelo B acierta | Modelo B falla |
|--:|:--:|:--:|
| **Modelo A acierta** | n₀₀ | n₀₁ |
| **Modelo A falla** | n₁₀ | n₁₁ |

```python
from statsmodels.stats.contingency_tables import mcnemar

tabla = [[n00, n01], [n10, n11]]
res = mcnemar(tabla, exact=False, correction=True)
p_valor = res.pvalue
```

- α = 0.05.
- Si `p < 0.05`, la diferencia es estadísticamente significativa.
- Reportar tamaño de efecto: `|n01 - n10| / N`.

Sin esta prueba **no se puede afirmar “mejora significativamente”**, palabra exacta presente en la hipótesis general.

## 11.8 Tabla de significancia (esperada)

| Comparación | F1 (A) | F1 (B) | n₀₁ | n₁₀ | p-valor McNemar | Significativo (α=0.05) |
|-------------|:------:|:------:|:---:|:---:|:---------------:|:----------------------:|
| BETO ajustado vs BETO base | 0.78 | 0.70 | 412 | 218 | 1.3e-12 | Sí |
| BETO ajustado vs mBERT | 0.78 | 0.72 | 351 | 230 | 2.1e-06 | Sí |
| BETO ajustado vs XLM-R | 0.78 | 0.76 | 287 | 246 | 0.075 | No |

## 11.9 Análisis de errores

Procedimiento:

1. Extraer 50 falsos positivos y 50 falsos negativos del modelo BETO ajustado.
2. Anotación manual por categorías:
   - Sarcasmo / ironía.
   - Cita textual de odio (mención sin endoso).
   - Modismo no incluido en lexicón.
   - Error de etiqueta original.
   - Ambigüedad real.
   - Otro.
3. Reportar distribución de categorías.
4. Cruzar con el flag `tiene_modismo` para detectar si los errores se concentran en algún subconjunto.
5. Para 10 errores representativos, generar explicación SHAP y discutirla en el informe.

## 11.10 Generación automática de artefactos

`src/evaluation/` produce, sin intervención manual:

- `reports/tables/metrics_<modelo>_<semilla>.csv`
- `reports/tables/comparativa_global.csv`
- `reports/tables/mcnemar.csv`
- `reports/figures/confusion_<modelo>.png`
- `reports/figures/roc_<modelo>.png`
- `reports/figures/pr_<modelo>.png`
- `reports/logs/eval_<modelo>_<semilla>.log`

---

# 12. ANÁLISIS DE MODISMOS (VALIDACIÓN DE H3)

## 12.1 Hipótesis específica 3

H3: El BETO ajustado obtiene mejor desempeño en textos con modismos LATAM que en textos sin modismos.

## 12.2 Subconjuntos del test set

```python
test_mod    = test[test["tiene_modismo"] == True]
test_no_mod = test[test["tiene_modismo"] == False]
```

**Pre-condiciones**:

- `|test_mod| ≥ 500` y `|test_no_mod| ≥ 500` (si no, ampliar lexicón antes de evaluar).
- Distribución de clases comparable; si difiere mucho, aplicar muestreo balanceado y reportarlo.

## 12.3 Métricas comparativas

| Modelo | Subconjunto | Precision | Recall | F1 (hate) | IC95% F1 |
|--------|-------------|-----------|--------|-----------|----------|
| BETO ajustado | con_modismos | … | … | … | … |
| BETO ajustado | sin_modismos | … | … | … | … |
| BETO base | con_modismos | … | … | … | … |
| BETO base | sin_modismos | … | … | … | … |
| mBERT | con_modismos | … | … | … | … |
| mBERT | sin_modismos | … | … | … | … |
| XLM-R | con_modismos | … | … | … | … |
| XLM-R | sin_modismos | … | … | … | … |

## 12.4 Pruebas estadísticas

1. **Diferencia intra-modelo (BETO ajustado: con vs sin modismos)**:
   - Bootstrap pareado de la diferencia F1.
   - Test de McNemar **dentro del mismo modelo** sobre los subconjuntos.
2. **Diferencia entre BETO ajustado y baselines en `con_modismos`**:
   - McNemar pareado restringido a `test_mod`.
3. **Efecto cruzado modismo × modelo**:
   - Ajuste de un modelo logístico simple: `acierto ~ modelo + tiene_modismo + modelo:tiene_modismo` para detectar interacción significativa.

## 12.5 Procedimiento experimental paso a paso

```
1. Cargar predicciones de cada modelo sobre el test completo.
2. Particionar predicciones según tiene_modismo.
3. Calcular métricas en cada subconjunto.
4. Bootstrap de la diferencia ΔF1 = F1(con) − F1(sin) para BETO ajustado.
5. Reportar Δ con IC95%; si IC no contiene 0, hay evidencia a favor de H3.
6. Ejecutar McNemar dentro de BETO ajustado sobre {con, sin}.
7. Anexar análisis cualitativo: 10 ejemplos correctamente clasificados y
   10 incorrectamente clasificados que contengan modismos.
8. Para los 20 ejemplos, generar explicaciones SHAP y verificar si los
   tokens del modismo aparecen entre los de mayor peso absoluto.
```

## 12.6 Interpretación esperada

- Si **BETO ajustado** mejora más sobre `con_modismos` que sobre `sin_modismos` frente a los baselines, H3 se sostiene.
- Si **no** hay diferencia, se reporta honestamente y se discute si el lexicón cubre poco, si el corpus ya contenía suficientes modismos para los baselines, o si la representación de Transformers multilingües ya internaliza léxico LATAM.

---

# 13. INTELIGENCIA ARTIFICIAL EXPLICABLE (XAI)

## 13.1 Justificación

La justificación teórica y metodológica del plan de tesis menciona XAI explícitamente. Su materialización es **obligatoria**; en caso contrario, el jurado puede señalar un desalineamiento. XAI cumple dos funciones:

1. **Validación científica**: comprobar que el modelo se apoya en tokens lingüísticamente plausibles (insultos, intensificadores) y no en artefactos espurios.
2. **Bienestar del usuario**: ofrecer al usuario una razón comprensible para cada alerta, contribuyendo al objetivo central de la tesis (bienestar digital).

## 13.2 Técnica seleccionada

- **SHAP** (Lundberg & Lee, 2017) con `shap.Explainer` y `shap.maskers.Text(tokenizer)`.
- Alternativa más liviana: `transformers-interpret` con integrated gradients, útil si SHAP es muy lento en CPU.

## 13.3 Wrapper de explicación

```python
import shap, torch
from transformers import pipeline

def construir_explainer(model, tokenizer):
    pipe = pipeline(
        "text-classification",
        model=model, tokenizer=tokenizer,
        top_k=None, return_all_scores=True,
        device=0 if torch.cuda.is_available() else -1,
    )
    masker = shap.maskers.Text(tokenizer)
    return shap.Explainer(pipe, masker)
```

## 13.4 Salida estandarizada

Contrato JSON consumido por el backend y la extensión:

```json
{
  "etiqueta": "hate",
  "probabilidad": 0.93,
  "modelo": "beto_finetuned",
  "version": "v1",
  "tokens": ["pinche", "USUARIO", "te", "odio"],
  "pesos":   [0.42,    -0.05,    0.10, 0.55]
}
```

- `pesos` están en la **escala de SHAP** (no probabilidades).
- Los `tokens` se devuelven en el orden del texto original.

## 13.5 Casos de uso

1. **Validación científica** (notebook 08): generar 50 explicaciones aleatorias, anotar manualmente si los tokens destacados son lingüísticamente coherentes.
2. **Análisis de modismos** (sección 12.5): verificar si los modismos aparecen entre los tokens de mayor peso en clasificaciones correctas con modismos.
3. **Servicio al usuario** (extensión): al hacer clic en un fragmento marcado, el usuario ve por qué fue marcado.

## 13.6 Visualización

- En notebook: `shap.plots.text(shap_values)` produce una visualización HTML embebible.
- En la extensión: gradiente de subrayado con intensidad proporcional al peso (rojo positivo, azul negativo).

## 13.7 Consideraciones de rendimiento

- SHAP sobre Transformers es costoso (10–60 s por instancia en CPU).
- Mitigación: caché por hash del texto, limitar a fragmentos `≤ 256` caracteres en el endpoint `/explain`, advertir al usuario que la explicación puede tardar.

---

# 14. BACKEND: ESPECIFICACIÓN TÉCNICA DEL SERVICIO FASTAPI

## 14.1 Estructura

```
src/api/
├── __init__.py
├── main.py            # creación de la app, lifespan, routers
├── config.py          # settings vía pydantic-settings
├── schemas.py         # contratos Pydantic
├── inference.py       # carga del modelo y predict
├── xai.py             # explicaciones SHAP
└── logging_conf.py    # logging estructurado
```

## 14.2 Configuración

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_dir: str = "models/beto_finetuned_final"
    model_version: str = "v1"
    max_input_chars: int = 512
    threshold: float = 0.5
    allowed_origins: list[str] = [
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ]
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 14.3 Esquemas Pydantic

```python
from pydantic import BaseModel, Field, constr

class PredictRequest(BaseModel):
    texto: constr(strip_whitespace=True, min_length=1, max_length=512)

class PredictResponse(BaseModel):
    etiqueta: str = Field(..., pattern=r"^(hate|no_hate)$")
    probabilidad: float = Field(..., ge=0.0, le=1.0)
    modelo: str
    version: str

class TokenWeight(BaseModel):
    token: str
    peso: float

class ExplainResponse(PredictResponse):
    tokens: list[str]
    pesos: list[float]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str

class ErrorResponse(BaseModel):
    detail: str
    code: str
```

## 14.4 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/health` | Liveness + metadatos básicos. |
| `GET`  | `/metadata` | Versión modelo, hash, fecha de entrenamiento. |
| `POST` | `/predict` | Inferencia binaria. |
| `POST` | `/explain` | Predicción + tokens y pesos SHAP. |

## 14.5 `main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .inference import cargar_modelo, predecir
from .xai import construir_explainer, explicar
from .schemas import (
    PredictRequest, PredictResponse, ExplainResponse, HealthResponse
)

state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"], state["tokenizer"] = cargar_modelo(settings.model_dir)
    state["explainer"] = construir_explainer(state["model"], state["tokenizer"])
    yield
    state.clear()

app = FastAPI(
    title="Hate Speech ES API",
    version=settings.model_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_loaded="model" in state,
        model_version=settings.model_version,
    )

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    return predecir(state["model"], state["tokenizer"], req.texto)

@app.post("/explain", response_model=ExplainResponse)
def explain(req: PredictRequest):
    return explicar(state["explainer"], state["model"],
                    state["tokenizer"], req.texto)
```

## 14.6 Inferencia

```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

LABELS = {0: "no_hate", 1: "hate"}

def cargar_modelo(path: str):
    tok = AutoTokenizer.from_pretrained(path)
    mdl = AutoModelForSequenceClassification.from_pretrained(path)
    mdl.eval()
    return mdl, tok

@torch.no_grad()
def predecir(model, tokenizer, texto: str) -> dict:
    enc = tokenizer(texto, truncation=True, max_length=128,
                    return_tensors="pt")
    logits = model(**enc).logits
    probs = torch.softmax(logits, dim=-1)[0]
    idx = int(torch.argmax(probs).item())
    return {
        "etiqueta": LABELS[idx],
        "probabilidad": float(probs[idx].item()),
        "modelo": "beto_finetuned",
        "version": "v1",
    }
```

## 14.7 Manejo de errores

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "code": "VALIDATION_ERROR"},
    )

@app.exception_handler(Exception)
async def generic_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno", "code": "INTERNAL"},
    )
```

Códigos HTTP previstos:

| Código | Significado |
|--------|-------------|
| 200 | OK. |
| 422 | Validación Pydantic (texto vacío, demasiado largo). |
| 503 | Modelo no cargado. |
| 500 | Error inesperado. |

## 14.8 Logging

`logging_conf.py` con formato JSON line para facilitar parseo:

```python
import logging, json, sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def setup():
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [h]
    root.setLevel("INFO")
```

**Privacidad**: por defecto **no** se loguea el contenido del texto. Solo longitud, etiqueta resultante, probabilidad y latencia.

## 14.9 Seguridad básica

- **CORS** restringido a la extensión y a `localhost`.
- **Rate limiting** opcional con `slowapi` (p. ej. 60 req/min por IP).
- **Validación estricta** del input vía Pydantic (longitud, no nulos).
- **Sin almacenamiento** de los textos enviados (a menos que se active modo debug explícito).
- **HTTPS** si se expone fuera de `localhost` (con `uvicorn --ssl-keyfile/--ssl-certfile`).
- **No exponer** `/docs` en entornos públicos sin protección.

## 14.10 Pruebas del backend

`tests/integration/test_api.py`:

```python
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_predict_ok():
    r = client.post("/predict", json={"texto": "Hola mundo"})
    assert r.status_code == 200
    body = r.json()
    assert body["etiqueta"] in {"hate", "no_hate"}
    assert 0.0 <= body["probabilidad"] <= 1.0

def test_predict_vacio():
    r = client.post("/predict", json={"texto": ""})
    assert r.status_code == 422

def test_predict_largo():
    r = client.post("/predict", json={"texto": "a" * 1000})
    assert r.status_code == 422
```

## 14.11 Ejecución local

```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`.

---

# 15. EXTENSIÓN DE NAVEGADOR (MANIFEST V3)

## 15.1 Visión general y dos capas de detección

| Capa | Mecanismo | Ventaja | Limitación |
|------|-----------|---------|------------|
| **Local (lexicón personal)** | Match de términos en `chrome.storage.local` | Instantánea, offline, personalizable | Cobertura limitada al léxico del usuario. |
| **ML (BETO vía API)** | Fragmentos enviados a `/predict` | Captura odio no listado, contextual | Requiere backend activo y red local. |

Ambas capas son independientes; el lexicón personal **no** reentrena el modelo. La distinción con el lexicón LATAM (sección 8) es fundamental:

| Lexicón LATAM | Lexicón personal |
|---------------|------------------|
| Vive en `data/lexicons/`. | Vive en `chrome.storage.local`. |
| Es de investigación; trazable, citable, versionado. | Es de producto; lo controla el usuario. |
| Se aplica al corpus para crear `tiene_modismo`. | Se aplica al DOM para alertas inmediatas. |
| Nunca cambia entre experimentos sin reentrenar baselines. | Cambia libremente, no afecta al modelo. |

## 15.2 Estructura

```
extension/
├── manifest.json
├── background.js        # service worker: cola, fetch a API, storage sync
├── content.js           # escaneo DOM, resaltado, MutationObserver
├── lexicon.js           # normalización y matching local
├── api.js               # wrapper fetch (predict, explain, health)
├── popup.html
├── popup.js             # toggle, umbral, estado API
├── options.html
├── options.js           # CRUD lexicón personal
├── styles.css
└── icons/               # 16, 32, 48, 128
```

## 15.3 `manifest.json` (Manifest V3)

```json
{
  "manifest_version": 3,
  "name": "Detector de Discurso de Odio (ES)",
  "version": "1.0.0",
  "description": "Detección automática de discurso de odio con BETO ajustado y lexicón personalizable.",
  "permissions": ["activeTab", "scripting", "storage"],
  "host_permissions": ["http://127.0.0.1:8000/*"],
  "action": { "default_popup": "popup.html" },
  "options_page": "options.html",
  "background": { "service_worker": "background.js" },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["lexicon.js", "api.js", "content.js"],
      "css": ["styles.css"]
    }
  ],
  "icons": {
    "16": "icons/16.png", "32": "icons/32.png",
    "48": "icons/48.png", "128": "icons/128.png"
  }
}
```

## 15.4 Modelo de mensajes

| Mensaje | Origen | Destino | Payload |
|---------|--------|---------|---------|
| `TOGGLE_DETECCION` | popup | background | `{activa: bool}` |
| `SET_UMBRAL` | popup | background | `{umbral: number}` |
| `PREDICT_BATCH` | content | background | `{fragmentos: [{id, texto}]}` |
| `RESULTADO` | background | content | `{id, etiqueta, probabilidad}` |
| `EXPLAIN_REQ` | content | background | `{id, texto}` |
| `EXPLAIN_RES` | background | content | `{id, tokens, pesos}` |
| `API_STATUS` | background | popup | `{ok: bool, ms: number}` |

## 15.5 Content script: escaneo del DOM

Responsabilidades:

1. Recorrer nodos visibles (selectores configurables: `p`, `article`, `[role="article"]`, tuits, comentarios).
2. Ignorar nodos ya procesados (`dataset.hateChecked === "1"`).
3. Extraer `textContent`, normalizar espacios, fragmentar a ≤ 512 caracteres respetando frases.
4. Aplicar **lexicón personal** localmente y envolver coincidencias en `<mark class="hate-lexicon">`.
5. Enviar fragmentos pendientes al service worker como `PREDICT_BATCH`.
6. Re-escaneo con `MutationObserver` y debounce de 500 ms, solo si `deteccionActiva === true`.

Esqueleto:

```js
const SELECTORES = ["p", "article", "[role='article']", ".tweet", ".comment"];
const DEBOUNCE_MS = 500;

let activo = false;
let umbral = 0.7;
let timer = null;

chrome.storage.local.get(["deteccionActiva", "umbralMl"], (s) => {
  activo = !!s.deteccionActiva;
  umbral = s.umbralMl ?? 0.7;
  if (activo) escanear();
});

const observer = new MutationObserver(() => {
  if (!activo) return;
  clearTimeout(timer);
  timer = setTimeout(escanear, DEBOUNCE_MS);
});
observer.observe(document.body, { childList: true, subtree: true });

function escanear() {
  const nodos = document.querySelectorAll(SELECTORES.join(","));
  const fragmentos = [];
  nodos.forEach((nodo) => {
    if (nodo.dataset.hateChecked === "1") return;
    const texto = (nodo.textContent || "").trim();
    if (texto.length < 5) return;
    const partes = fragmentar(texto, 512);
    partes.forEach((t, i) => {
      const id = `frag-${Date.now()}-${Math.random().toString(36).slice(2,8)}`;
      fragmentos.push({ id, texto: t });
      nodo.dataset.hateChecked = "1";
      window.__hateRefs = window.__hateRefs || {};
      window.__hateRefs[id] = { nodo, parteIndex: i };
    });
  });
  aplicarLexiconLocal(nodos);
  if (fragmentos.length) {
    chrome.runtime.sendMessage({ tipo: "PREDICT_BATCH", fragmentos });
  }
}

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.tipo === "RESULTADO") {
    const ref = window.__hateRefs?.[msg.id];
    if (!ref) return;
    if (msg.etiqueta === "hate" && msg.probabilidad >= umbral) {
      resaltarML(ref.nodo, msg.probabilidad);
    }
  }
});
```

## 15.6 Service worker: cola de inferencia

```js
const COLA_MAX = 3;
let enVuelo = 0;
const cola = [];

chrome.runtime.onMessage.addListener((msg, sender, _reply) => {
  if (msg.tipo === "PREDICT_BATCH") {
    msg.fragmentos.forEach((f) =>
      cola.push({ ...f, tabId: sender.tab.id })
    );
    procesarCola();
  }
});

async function procesarCola() {
  while (cola.length && enVuelo < COLA_MAX) {
    const item = cola.shift();
    enVuelo++;
    procesarItem(item).finally(() => {
      enVuelo--;
      procesarCola();
    });
  }
}

async function procesarItem({ id, texto, tabId }) {
  try {
    const r = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const data = await r.json();
    chrome.tabs.sendMessage(tabId, { tipo: "RESULTADO", id, ...data });
  } catch (e) {
    chrome.action.setBadgeText({ text: "!" });
    chrome.action.setBadgeBackgroundColor({ color: "#c00" });
  }
}
```

## 15.7 Popup

`popup.html` mínimo:

```html
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><link rel="stylesheet" href="styles.css"></head>
<body>
  <h1>Detector ES</h1>
  <label><input type="checkbox" id="toggle"> Detección automática</label>
  <label>Umbral: <input type="range" id="umbral" min="0.5" max="0.95" step="0.05"></label>
  <p>API: <span id="apiStatus">…</span></p>
  <a href="options.html" target="_blank">Lexicón personal</a>
  <script src="popup.js"></script>
</body>
</html>
```

`popup.js`:

```js
const toggle = document.getElementById("toggle");
const umbral = document.getElementById("umbral");
const apiStatus = document.getElementById("apiStatus");

chrome.storage.local.get(["deteccionActiva", "umbralMl"], (s) => {
  toggle.checked = !!s.deteccionActiva;
  umbral.value = s.umbralMl ?? 0.7;
});

toggle.addEventListener("change", () => {
  chrome.storage.local.set({ deteccionActiva: toggle.checked });
});
umbral.addEventListener("input", () => {
  chrome.storage.local.set({ umbralMl: parseFloat(umbral.value) });
});

fetch("http://127.0.0.1:8000/health")
  .then((r) => r.json())
  .then((d) => apiStatus.textContent = d.status === "ok" ? "conectada" : "error")
  .catch(() => apiStatus.textContent = "desconectada");
```

## 15.8 Options Page: gestión del lexicón personal

Funcionalidad:

- Lista editable de términos (uno por línea o tabla).
- **Agregar**, **Quitar seleccionados**, **Restaurar lista por defecto**.
- Validación: sin duplicados, `trim`, longitud máx. 64, máx. 200 términos.
- Exportar / importar JSON para respaldo local.
- Aviso explícito: *“Esta lista permanece en su navegador y no se envía al servidor”*.

`options.js` (núcleo):

```js
const lista = document.getElementById("lista");
const nuevo = document.getElementById("nuevo");

function cargar() {
  chrome.storage.local.get(["palabrasUsuario"], ({ palabrasUsuario = [] }) => {
    lista.innerHTML = "";
    palabrasUsuario.forEach((t) => {
      const li = document.createElement("li");
      li.textContent = t;
      const btn = document.createElement("button");
      btn.textContent = "Quitar";
      btn.onclick = () => quitar(t);
      li.appendChild(btn);
      lista.appendChild(li);
    });
  });
}

function agregar() {
  const t = nuevo.value.trim().toLowerCase();
  if (!t || t.length > 64) return;
  chrome.storage.local.get(["palabrasUsuario"], ({ palabrasUsuario = [] }) => {
    if (palabrasUsuario.includes(t) || palabrasUsuario.length >= 200) return;
    palabrasUsuario.push(t);
    chrome.storage.local.set({ palabrasUsuario }, cargar);
  });
}

function quitar(t) {
  chrome.storage.local.get(["palabrasUsuario"], ({ palabrasUsuario = [] }) => {
    const next = palabrasUsuario.filter((x) => x !== t);
    chrome.storage.local.set({ palabrasUsuario: next }, cargar);
  });
}

document.getElementById("agregar").onclick = agregar;
cargar();
```

## 15.9 Comunicación con la API

`api.js` centraliza el contrato HTTP:

```js
const BASE = "http://127.0.0.1:8000";

export async function apiPredict(texto) {
  const r = await fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!r.ok) throw new Error("predict failed: " + r.status);
  return r.json();
}

export async function apiExplain(texto) {
  const r = await fetch(`${BASE}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!r.ok) throw new Error("explain failed: " + r.status);
  return r.json();
}

export async function apiHealth() {
  const r = await fetch(`${BASE}/health`);
  return r.ok ? r.json() : { status: "down" };
}
```

## 15.10 Resaltado de contenido

CSS (`styles.css`):

```css
mark.hate-ml {
  background: rgba(255, 80, 80, 0.35);
  border-bottom: 2px solid #c00;
  cursor: help;
}
mark.hate-lexicon {
  background: rgba(255, 200, 0, 0.35);
  border-bottom: 2px dashed #c80;
}
.hate-explain-token {
  background-color: rgba(255, 80, 80, var(--peso, 0));
}
```

Pasos de resaltado ML:

1. Envolver el texto del nodo en un span con `<mark class="hate-ml" title="p=0.93">`.
2. Adjuntar listener de clic que invoca `EXPLAIN_REQ` y, al recibir `EXPLAIN_RES`, despliega un tooltip con los tokens coloreados por peso.

## 15.11 Consideraciones de rendimiento

- **Debounce** del escaneo: 500 ms tras cambios DOM.
- **Tope de fragmentos por escaneo**: 50 primeros bloques visibles para no saturar CPU/API.
- **Cola con concurrencia limitada**: `COLA_MAX = 3`.
- **Caché en memoria**: `Map<hash(texto), respuesta>` con TTL 5 min para evitar repreguntar el mismo fragmento.
- **Marcado idempotente**: `data-hate-checked="1"` evita reescaneo.
- **Backoff** en fallos: si la API falla 3 veces seguidas, pausar la cola 30 s.

## 15.12 Privacidad y consentimiento

- Detección automática **desactivada por defecto**.
- En el primer activado, mostrar un modal explicativo:
  - Qué se envía al backend (texto visible de la página).
  - Qué **no** se envía (lexicón personal, datos de navegación, cookies).
  - Que el backend corre en `127.0.0.1` (máquina del usuario).
- Lexicón personal permanece **solo** en `chrome.storage.local`.

## 15.13 Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| API caída | Badge rojo, dejar de encolar, intentar `/health` cada 30 s. |
| Texto > 512 caracteres | Truncar o dividir; nunca enviar tal cual. |
| Fragmento vacío | Descartar antes de enviar. |
| Página muy grande | Tope de 50 fragmentos por escaneo. |
| Detección desactivada | Quitar resaltados y limpiar `data-hate-checked`. |
| Permiso denegado por CSP del sitio | Registrar y continuar sin romper. |

---

# 16. CRONOGRAMA TÉCNICO POR FASES Y ENTREGABLES

> Cronograma de referencia, ~10 semanas. Cada fase declara entregables verificables.

## Fase 1 — Datos (semanas 1–2)

**Objetivo**: corpus crudo y limpio, individualmente normalizado.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| Datasets descargados en `data/raw/` | Checksums registrados. |
| `src/data/clean.py` + tests | `pytest tests/unit/test_clean.py` pasa. |
| `data/interim/<dataset>.parquet` por cada dataset | Esquema canónico validado. |
| `data/reports_qc/qc_<dataset>.md` | Distribución de clases y longitudes. |

## Fase 2 — Corpus (semana 2–3)

**Objetivo**: corpus unificado y enriquecido, particionado.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `data/lexicons/modismos_latam_v1.csv` | ≥ 500 términos, validación manual reportada. |
| `data/processed/corpus_v1_enriquecido.parquet` | Pasa `validar_corpus`. |
| `train.parquet / val.parquet / test.parquet` | Estratificados, sin fuga. |
| `data/processed/MANIFEST.json` | Hashes y versiones. |
| `data/reports_qc/qc_corpus_v1.md` | Reporte completo. |

## Fase 3 — BETO ajustado y baselines (semanas 3–5)

**Objetivo**: cuatro modelos entrenados con 3 semillas cada uno.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `models/beto_finetuned_{42,123,2024}/` | Métricas en val ≥ baseline interno. |
| `models/beto_base_{42,123,2024}/` (Opción A) | Reportadas con el mismo protocolo. |
| `models/mbert_{42,123,2024}/` | Idem. |
| `models/xlmr_{42,123,2024}/` | Idem. |
| `models/beto_finetuned_final/` + `model_card.md` | Modelo seleccionado y empaquetado. |
| Banner reproducible en cada log | Commit, corpus, lexicón, semilla. |

## Fase 4 — Evaluación experimental (semana 5–6)

**Objetivo**: tablas y figuras listas para la tesis.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `reports/tables/comparativa_global.csv` | 4 modelos × métricas × IC95%. |
| `reports/tables/mcnemar.csv` | p-valores BETO ajustado vs cada baseline. |
| `reports/figures/confusion_*.png` | Por modelo. |
| `reports/figures/roc_*.png`, `pr_*.png` | Por modelo. |
| Sección de **análisis de errores** | 50 FP + 50 FN categorizados. |

## Fase 5 — Análisis de modismos + XAI (semana 6–7)

**Objetivo**: validar H3 con evidencia cuantitativa y cualitativa.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `reports/tables/modismos.csv` | Métricas por subconjunto. |
| Test estadístico H3 documentado | p-valor + tamaño de efecto. |
| 20 explicaciones SHAP analizadas | En `notebooks/08_xai.ipynb`. |
| Conclusión de H3 con honestidad metodológica | Aceptación o rechazo argumentado. |

## Fase 6 — Backend (semana 7–8)

**Objetivo**: API funcional con cobertura de pruebas.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `src/api/` completo | `pytest tests/integration/test_api.py` pasa. |
| Swagger UI accesible | Documentación auto-generada. |
| Latencia P95 < 1.5 s en CPU local | Medido con script de carga simple. |
| Logging JSON y errores tipificados | Verificado con prueba de fallos. |

## Fase 7 — Extensión y validación end-to-end (semanas 8–9)

**Objetivo**: extensión funcional contra el backend local.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| `extension/` completo, instalable en Chrome/Edge | Manifest V3 válido. |
| Demo grabada en página pública | Resaltado ML + lexicón personal + explicación. |
| Documento de privacidad en popup | Consentimiento explícito. |
| Prueba end-to-end | Página real → fragmento → predict → resaltado → explain. |

## Fase 8 — Validación final y redacción (semana 10)

**Objetivo**: informe consolidado y artefactos congelados.

| Entregable | Criterio de aceptación |
|------------|------------------------|
| Matriz de trazabilidad completa (sección 18) | Cada hipótesis ↔ evidencia. |
| `EXPERIMENTOS.md` completo | Todas las decisiones registradas. |
| Pulido de figuras y tablas para la tesis | Calidad publicable. |
| Repo en estado “congelado” con tag `v1.0` | Reproducible desde cero. |

---

# 17. RIESGOS DEL PROYECTO Y MITIGACIONES

## 17.1 Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| `CUDA out of memory` | Media | Alta | `batch_size` reducido, `gradient_accumulation_steps`, `fp16`. |
| Inestabilidad del fine-tuning (varianza alta) | Alta | Media | 3 semillas, reportar media ± std (Mosbach et al., 2021). |
| Latencia del backend en CPU > 1.5 s | Media | Media | Cuantización dinámica, ONNX Runtime opcional. |
| Cambios de API en `transformers` | Baja | Media | Pinning a versión `>=4.40,<5.0` y `requirements.lock.txt`. |
| Manifest V3 cambia políticas | Baja | Media | Abstraer fetch y storage en wrappers. |
| CORS bloqueando llamadas | Media | Baja | `host_permissions` y `allow_origins` documentados. |

## 17.2 Riesgos metodológicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Mapeo de etiquetas cuestionable | Media | Alta | Tabla pública, justificada por dataset; revisión cruzada. |
| Lexicón LATAM percibido como “ad hoc” | Media | Alta | Citar fuentes (ASALE, literatura); validación manual. |
| Resultados no significativos para H1/H2 | Media | Media | Reportar honestamente; analizar causas; una tesis con hallazgos parciales es defendible. |
| Confusión entre lexicón LATAM y lexicón personal | Media | Alta | Separación física y documental (sección 8 vs 15). |
| Comparación entre modelos con variables no controladas | Media | Alta | Sección 10.4 lista variables a fijar. |
| Test set contaminado por fuga | Baja | Muy alta | Deduplicación cruzada (sección 6.5). |

## 17.3 Riesgos de datos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Datasets con etiquetas inconsistentes internas | Alta | Media | Reportar acuerdo entre datasets; análisis de errores. |
| Desbalance fuerte | Alta | Media | `class_weights`, F1 binaria, threshold tuning. |
| Cobertura LATAM insuficiente del lexicón | Media | Alta | Iterar el lexicón hasta cubrir ≥ 15 %. |
| Datos sensibles en `test` | Baja | Alta | No publicar el contenido completo del test; solo IDs. |
| Licencia de algún dataset restrictiva | Media | Media | Auditar licencias antes de redistribuir. |

## 17.4 Riesgos de hardware y entorno

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Colab/Kaggle agota cuota durante el entrenamiento | Alta | Media | Persistir checkpoints en Drive cada epoch; reanudar. |
| Falla del disco local | Baja | Muy alta | Backups en la nube; `MANIFEST.json` versionado en git. |
| Inestabilidad de drivers CUDA | Baja | Media | Documentar versiones; entorno conda alternativo. |
| Cambios silenciosos de pesos en Hugging Face Hub | Baja | Alta | Fijar `revision=` (commit hash) al descargar modelos. |

## 17.5 Riesgos de tiempo

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Fase 1 más larga de lo previsto | Alta | Media | Empezar con dos datasets; sumar el tercero después. |
| Re-trabajo por cambio de lexicón | Media | Alta | Versionar lexicón y corpus; automatizar pipeline. |
| Extensión consume más tiempo del previsto | Media | Media | Mantener UI mínima; foco en la integración funcional. |
| Redacción de la tesis sin datos finales | Media | Alta | Avanzar capítulos teóricos en paralelo a la implementación. |

## 17.6 Plan de contingencia

- Si **H1** no se confirma: discutir saturación del modelo base, posible insuficiencia del corpus enriquecido, y dejar la línea abierta.
- Si **H2** no se confirma: argumentar que el aporte de la tesis es el corpus + análisis de modismos, no la superioridad numérica.
- Si **H3** no se confirma: rediscutir la definición de “modismo”; validar si el lexicón es suficiente; reportar honestamente.

---

# 18. MATRIZ DE TRAZABILIDAD DE REQUISITOS, OBJETIVOS E HIPÓTESIS

## 18.1 Requisitos funcionales

| ID | Requisito | Criterio de aceptación | Fase |
|----|-----------|------------------------|------|
| RF1 | Recolectar e integrar ≥ 3 datasets en español | Corpus ≥ 30 000 ejemplos. | Fase 1 |
| RF2 | Preprocesar sin destruir información | URLs/menciones/hashtags/emojis normalizados; mayúsculas preservadas. | Fase 1 |
| RF3 | Unificar etiquetas a binario | Tabla de mapeo documentada. | Fase 2 |
| RF4 | Marcar `tiene_modismo` con lexicón | Lexicón con fuente y ≥ 500 términos. | Fase 2 |
| RF5 | Fine-tuning de BETO documentado | Modelo guardado y reproducible. | Fase 3 |
| RF6 | Entrenar mBERT y XLM-R con mismo protocolo | Mismas particiones y semillas. | Fase 3 |
| RF7 | Reportar Precision, Recall, F1, matriz de confusión | Por modelo + IC bootstrap. | Fase 4 |
| RF8 | Significancia estadística | McNemar pareado documentado. | Fase 4 |
| RF9 | Evaluación segmentada por modismos | Tabla comparativa + prueba estadística. | Fase 5 |
| RF10 | API REST con `/health`, `/predict`, `/explain` | OpenAPI accesible. | Fase 6 |
| RF11 | XAI individual | SHAP devuelve tokens y pesos. | Fase 5/6 |
| RF12 | Extensión con detección automática | Manifest V3, escaneo, resaltado. | Fase 7 |
| RF13 | Lexicón personalizable en extensión | CRUD persistido en `chrome.storage.local`. | Fase 7 |
| RF14 | XAI desde la extensión | Tooltip/panel con tokens y pesos. | Fase 7 |

## 18.2 Hipótesis vs evidencia

| Hipótesis | Evidencia | Sección |
|-----------|-----------|---------|
| H1: BETO ajustado > BETO base | ΔF1 con IC95% + McNemar p<0.05 | 11.4, 11.7 |
| H2: BETO ajustado ≥ mBERT/XLM-R | Comparativa global + McNemar por baseline | 11.4, 11.7 |
| H3: Mejor en `con_modismos` | Métricas por subconjunto + bootstrap + análisis SHAP | 12, 13 |

## 18.3 Objetivos específicos vs fases

| OE | Fase | Entregables principales |
|----|------|--------------------------|
| OE1 | 1, 2 | Corpus unificado v1 |
| OE2 | 2 | Lexicón LATAM v1 |
| OE3 | 3 | `beto_finetuned_final/` |
| OE4 | 3 | mBERT y XLM-R con misma metodología |
| OE5 | 4 | Comparativa + McNemar |
| OE6 | 5 | Análisis de modismos |
| OE7 | 5, 6 | XAI integrado en API |
| OE8 | 6, 7 | Backend + extensión |

---

# 19. CRITERIOS DE ÉXITO Y ACEPTACIÓN

## 19.1 Éxito científico

- **C1** F1 (clase `hate`) de BETO ajustado **estrictamente mayor** que el de BETO base, con `p < 0.05` (McNemar).
- **C2** F1 de BETO ajustado **mayor o igual** que el de mBERT y XLM-R; significancia estadística reportada (incluso si no es favorable).
- **C3** Diferencia observable y discutida entre `con_modismos` y `sin_modismos` para BETO ajustado, con su prueba estadística.
- **C4** Análisis de errores con al menos 100 instancias revisadas manualmente.
- **C5** Al menos 50 explicaciones SHAP discutidas, con verificación de plausibilidad lingüística.

## 19.2 Éxito de ingeniería

- **C6** Backend responde `/predict` con P95 < 1.5 s en CPU local.
- **C7** Extensión Manifest V3 instala y opera contra `localhost:8000` sin errores en Chrome y Edge.
- **C8** Cobertura de tests del backend ≥ 70 %.
- **C9** Pipeline de datos ejecutable end-to-end con `make data`.
- **C10** Repositorio congelado en tag `v1.0`, reproducible desde cero en máquina nueva.

## 19.3 Éxito metodológico

- **C11** `EXPERIMENTOS.md` con todas las decisiones registradas.
- **C12** `MANIFEST.json` con hashes y versiones de corpus, lexicón y modelos.
- **C13** Cada figura y tabla del informe trazable a un archivo en `reports/`.

---

# 20. RECOMENDACIONES FINALES PARA LA DEFENSA

1. **Congelar el `test set` el primer día.** Ningún experimento puede tocarlo hasta el final. Es la línea roja metodológica del proyecto.
2. **Versionar todo lo que se pueda.** Datos, lexicones, modelos, código, decisiones. Un evaluador riguroso preguntará por la trazabilidad.
3. **Mantener un `EXPERIMENTOS.md` actualizado** con cada decisión no obvia: mapeo de etiquetas, semillas, hiperparámetros, motivos de descarte. Es la mejor defensa contra la pregunta “¿por qué hizo X?”.
4. **Reportar con honestidad** los resultados negativos o no significativos. Una tesis con `p = 0.07` bien argumentada vale más que una con `p < 0.001` mal sustentada.
5. **Distinguir siempre** el lexicón LATAM (instrumento de investigación) del lexicón personal del usuario (producto). No mezclar archivos ni narrativas.
6. **Priorizar el rigor experimental** sobre el adorno de la UI. La extensión es la “vitrina”, pero los números son el esqueleto.
7. **Anticipar las preguntas del jurado**: unificación de etiquetas, construcción del lexicón, comparación justa entre modelos, control de la varianza, sentido de XAI, privacidad de la extensión.
8. **Preparar una demo reproducible** del flujo completo: una página real, un fragmento detectado, su explicación y el lexicón personal en acción.

---

# 21. GLOSARIO

| Término | Definición |
|---------|------------|
| **BETO** | Modelo BERT preentrenado exclusivamente en español (Cañete et al., 2020). |
| **mBERT** | Versión multilingüe de BERT (104 idiomas), `bert-base-multilingual-cased`. |
| **XLM-R** | RoBERTa multilingüe (XLM-RoBERTa), `xlm-roberta-base`. |
| **Fine-tuning** | Ajuste de los pesos preentrenados sobre una tarea específica. |
| **Hate speech** | Discurso que ataca o degrada a una persona o grupo por atributos protegidos. |
| **Modismo** | Expresión idiomática propia de una variante regional del idioma. |
| **Lexicón LATAM** | Recurso léxico de modismos latinoamericanos usado para enriquecer el corpus (instrumento científico). |
| **Lexicón personal** | Lista de palabras configurada por el usuario en la extensión (producto). |
| **F1** | Media armónica de Precision y Recall. |
| **Bootstrap** | Estimación de la distribución de una métrica por remuestreo con reposición. |
| **McNemar** | Test estadístico para clasificadores pareados sobre el mismo `test set`. |
| **SHAP** | Shapley Additive exPlanations, método de atribución por valores de Shapley. |
| **Manifest V3** | Especificación vigente para extensiones de navegador basadas en Chromium. |
| **Service Worker** | Script de fondo de la extensión sin DOM, con ciclo de vida basado en eventos. |
| **Content Script** | Script inyectado en el contexto de la página visitada. |

---

# 22. REFERENCIAS Y FUENTES CONSULTADAS

> Citas mínimas obligatorias para el informe. Completar con las que el plan de tesis ya incluye.

- Cañete, J., Chaperon, G., Fuentes, R., Ho, J., Kang, H., & Pérez, J. (2020). **Spanish Pre-Trained BERT Model and Evaluation Data**. PML4DC at ICLR 2020.
- Basile, V., Bosco, C., Fersini, E., Nozza, D., Patti, V., Rangel, F., Rosso, P., & Sanguinetti, M. (2019). **SemEval-2019 Task 5: Multilingual Detection of Hate Speech against Immigrants and Women in Twitter (HatEval)**.
- Taulé, M., Ariza, A., Nofre, M., Amigó, E., & Rosso, P. (2021). **DETOXIS: Detection of Toxicity in Comments in Spanish**. IberLEF.
- Aragón, M. E. et al. (2020). **Overview of MEX-A3T at IberLEF 2020: Fake News and Aggressiveness Analysis in Mexican Spanish**.
- Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding**. NAACL.
- Conneau, A. et al. (2020). **Unsupervised Cross-lingual Representation Learning at Scale (XLM-R)**.
- Mosbach, M., Andriushchenko, M., & Klakow, D. (2021). **On the Stability of Fine-tuning BERT: Misconceptions, Explanations, and Strong Baselines**. ICLR.
- Lundberg, S. M., & Lee, S.-I. (2017). **A Unified Approach to Interpreting Model Predictions (SHAP)**. NeurIPS.
- Asociación de Academias de la Lengua Española (ASALE). **Diccionario de Americanismos**.
- Moreno-Sandoval, A., et al. (2024). Trabajos referenciados sobre jerga regional en redes sociales hispanohablantes.
- Pérez, J., et al. (2023). Trabajos referenciados sobre detección de discurso de odio en español latinoamericano.
- Mozilla / Chromium Developers. **Manifest V3 Documentation**.
- FastAPI Project. **FastAPI Official Documentation**.
- Hugging Face. **Transformers Documentation** (versión ≥ 4.40).

---

**Fin del documento maestro.**

Este documento debe acompañarse siempre del archivo `EXPERIMENTOS.md`, donde se registra el detalle ejecutivo de cada corrida experimental, y del `MANIFEST.json`, que garantiza la trazabilidad de los artefactos. La combinación de los tres archivos (guia.md + EXPERIMENTOS.md + MANIFEST.json) constituye la **bitácora científica completa** del proyecto.
