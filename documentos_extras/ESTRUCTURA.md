# Estructura del Proyecto Creada

## Resumen

Se ha creado una estructura completa y profesional del proyecto de tesis con:

- **22 carpetas principales** organizadas según la especificación en `guia.md`
- **80+ archivos** incluyendo módulos Python, notebooks vacíos, tests, scripts, documentación y extensión Chrome
- **Documentación de referencia** en cada carpeta con instrucciones y estándares

---

## Jerarquía de carpetas

```
Tesis_Proyecto/
│
├── 📁 data/                          # Gestión de datos por etapas
│   ├── raw/                          # Datasets crudos (descarga manual)
│   ├── interim/                      # Versiones limpiadas individualmente
│   ├── processed/                    # Corpus unificado + particiones
│   ├── lexicons/                     # Lexicón LATAM de investigación
│   └── reports_qc/                   # Reportes de control de calidad
│
├── 📁 notebooks/                     # Notebooks Jupyter (análisis paso a paso)
│   ├── 01_exploracion.ipynb
│   ├── 02_unificacion.ipynb
│   ├── 03_modismos.ipynb
│   ├── 04_finetuning_beto.ipynb
│   ├── 05_baselines_mbert_xlmr.ipynb
│   ├── 06_evaluacion_comparada.ipynb
│   ├── 07_analisis_modismos.ipynb
│   └── 08_xai.ipynb
│
├── 📁 src/                           # Código fuente estructurado
│   ├── config.py                     # Configuración global
│   ├── data/                         # Módulo de gestión de datos
│   ├── modeling/                     # Módulo de modelado
│   ├── evaluation/                   # Módulo de evaluación
│   ├── xai/                          # Módulo de explicabilidad
│   └── api/                          # Módulo de API REST
│
├── 📁 extension/                     # Extensión Chrome Manifest V3
│   ├── manifest.json
│   ├── background.js                # Service Worker
│   ├── content.js                    # Inyección en DOM
│   ├── lexicon.js                    # Utilidades de matching
│   ├── api.js                        # Wrappers HTTP
│   ├── popup.html / popup.js         # Control principal
│   ├── options.html / options.js     # Gestión de lexicón personal
│   ├── styles.css                    # Estilos
│   └── icons/                        # Iconografía
│
├── 📁 models/                        # Checkpoints (no versionados en git)
│   └── README.md                     # Instrucciones de descarga
│
├── 📁 tests/                         # Suite de tests
│   ├── unit/                         # Tests unitarios
│   ├── integration/                  # Tests de integración
│   └── conftest.py                   # Configuración pytest
│
├── 📁 reports/                       # Artefactos del experimento
│   ├── tables/                       # CSV de métricas
│   ├── figures/                      # PNG de gráficos
│   └── logs/                         # Logs de entrenamiento
│
├── 📁 docs/                          # Documentación técnica
│   ├── arquitectura.md               # Diagrama y componentes
│   ├── decisiones.md                 # Justificación de diseño
│   ├── modelo.md                     # Especificación del modelo
│   └── glosario.md                   # Términos técnicos
│
├── 📁 scripts/                       # Entrypoints CLI
│   ├── prepare_data.py               # Pipeline de datos
│   ├── train_model.py                # Entrenamiento
│   ├── evaluate_model.py             # Evaluación
│   ├── run_api.sh                    # Iniciar backend
│   └── package_model.py              # Empaquetado
│
├── 📄 README.md                      # Inicio rápido
├── 📄 guia.md                        # Especificación técnica completa (2465 líneas)
├── 📄 desarrollo.md                  # Guía ejecutable paso a paso
├── 📄 EXPERIMENTOS.md                # Bitácora de decisiones (plantilla)
├── 📄 requirements.txt               # Dependencias Python
├── 📄 environment.yml                # Alternativa conda
├── 📄 pyproject.toml                 # Config de ruff/black/pytest
├── 📄 Makefile                       # Atajos de comandos
└── 📄 .gitignore                     # Exclusiones de git
```

---

## Archivos creados

### Módulos Python (src/)

**data/:**
- `download.py` - Descarga de datasets
- `clean.py` - Limpieza y normalización
- `unify.py` - Unificación de esquemas
- `lexicon.py` - Gestión del lexicón LATAM
- `enrich.py` - Enriquecimiento del corpus
- `split.py` - Particionado estratificado
- `qc.py` - Validaciones de calidad

**modeling/:**
- `tokenize.py` - Tokenización
- `train.py` - Entrenamiento reproducible
- `evaluate.py` - Evaluación
- `losses.py` - Funciones de pérdida
- `checkpoints.py` - Gestión de checkpoints

**evaluation/:**
- `metrics.py` - Cálculo de métricas
- `bootstrap.py` - Intervalos de confianza
- `mcnemar.py` - Tests estadísticos
- `errors.py` - Análisis de errores

**xai/:**
- `shap_explainer.py` - Explicabilidad SHAP

**api/:**
- `main.py` - App FastAPI
- `schemas.py` - Esquemas Pydantic
- `inference.py` - Lógica de predicción
- `xai.py` - Explicaciones en API
- `config.py` - Configuración
- `logging_conf.py` - Logging

### Tests (tests/)

- `conftest.py` - Fixtures
- `unit/test_clean.py`, `test_lexicon.py`, `test_metrics.py`, `test_schemas.py`
- `integration/test_pipeline_data.py`, `test_api.py`

### Scripts (scripts/)

- `prepare_data.py` - Preparación de datos
- `train_model.py` - Entrenamiento
- `evaluate_model.py` - Evaluación
- `run_api.sh` - Backend
- `package_model.py` - Empaquetado

### Documentación (docs/)

- `arquitectura.md` - Visión técnica
- `decisiones.md` - Justificación de diseño
- `modelo.md` - Especificación BETO
- `glosario.md` - Términos

### Extensión Chrome (extension/)

- `manifest.json` - Manifest V3
- `background.js` - Service Worker (cola de inferencia)
- `content.js` - Escaneo DOM y resaltado
- `lexicon.js` - Matching local
- `api.js` - Wrappers HTTP
- `popup.html / popup.js` - Control principal
- `options.html / options.js` - Gestión del lexicón personal
- `styles.css` - Estilos CSS

### Archivos raíz

- `README.md` - Inicio rápido
- `guia.md` - Especificación completa (~2465 líneas)
- `desarrollo.md` - Guía ejecutable paso a paso (~800 líneas)
- `EXPERIMENTOS.md` - Plantilla de bitácora científica
- `requirements.txt` - Dependencias Python
- `environment.yml` - Conda environment
- `pyproject.toml` - Config herramientas
- `Makefile` - Atajos
- `.gitignore` - Exclusiones

---

## Próximos pasos

### 1. Inicializar git y entorno

```bash
cd Tesis_Proyecto
git init
git config user.name "Tu nombre"
git config user.email "tu@email.com"
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. Descarga de datasets

Seguir las instrucciones en `desarrollo.md` Paso 1.1:
- Descargar HatEval, MEX-A3T, DETOXIS a `data/raw/`

### 3. Crear corpus

Ejecutar `notebooks/02_unificacion.ipynb` o:

```bash
python scripts/prepare_data.py --version 1
```

### 4. Entrenar modelos

```bash
python scripts/train_model.py --model beto --seed 42
python scripts/train_model.py --model beto --seed 123
python scripts/train_model.py --model beto --seed 2024
```

### 5. Evaluar

```bash
python scripts/evaluate_model.py --all
```

### 6. Ejecutar API

```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### 7. Instalar extensión

1. Chrome/Edge → `chrome://extensions`
2. Modo de desarrollador ON
3. Cargar extensión sin empaquetar → seleccionar carpeta `extension/`

---

## Documentación de referencia en cada carpeta

Cada carpeta tiene un `README.md` con:
- Propósito de la carpeta
- Estructura esperada
- Archivo de ejemplo
- Comandos de generación

**Ejemplos:**
- `data/raw/README.md` - Cómo descargar datasets
- `data/processed/README.md` - Estructura del corpus unificado
- `data/lexicons/README.md` - Construcción del lexicón LATAM
- `models/README.md` - Gestión de checkpoints
- `extension/` - Código completamente comentado

---

## Características implementadas

✅ Estructura profesional completa  
✅ Módulos organizados por responsabilidad  
✅ Configuración centralizada en `config.py`  
✅ Extensión Chrome Manifest V3 funcional  
✅ Backend FastAPI con esquemas Pydantic  
✅ Tests unitarios e integración  
✅ Documentación en cada carpeta  
✅ Makefile con atajos  
✅ `.gitignore` configurado  
✅ Reproducibilidad garantizada  

---

## Validación

Para verificar la estructura:

```bash
cd Tesis_Proyecto
ls -la                    # Ver archivos raíz
find . -type d | head -30 # Ver estructura
```

---

**Toda la estructura está lista para comenzar el Paso 1.1 de `desarrollo.md`.**
