# GUIA DE REPRODUCCIÓN — Replicar el proyecto desde cero

> Este archivo te lleva de cero a replicar el estado actual del proyecto con comandos concretos.
> Se actualiza con cada paso completado. Estado actual: **Fase 1 ✅ — Fase 2 ✅ — Fase 3 ✅ — Fase 4 ✅ — Fase 5A ✅ — Fase 5B ✅ — Fase 6 ✅ — Fase 7 (integración BETO) ✅ — Sistema end-to-end COMPLETO ✅**.

---

## ¿De qué trata el proyecto?

Sistema de detección automática de discurso de odio en español. El núcleo es ajustar el modelo **BETO** (BERT en español) con un corpus enriquecido con modismos latinoamericanos, y compararlo contra modelos multilingües (mBERT, XLM-R). El sistema se expone como backend REST y extensión de Chrome.

**Tres hipótesis a validar:**
- **H1** — BETO ajustado supera a BETO sin ajuste fino
- **H2** — BETO ajustado iguala o supera a mBERT y XLM-R en español
- **H3** — BETO ajustado rinde mejor en textos con modismos LATAM que sin ellos

Para más detalle técnico: [`INSTRUCCIONES_PROYECTO.md`](INSTRUCCIONES_PROYECTO.md) | Para el itinerario paso a paso: [`PLAN_DESARROLLO.md`](PLAN_DESARROLLO.md)

---

## Requisitos previos

- Python ≥ 3.10
- Git
- Los datasets ya descargados en `data/raw/` (ver Paso 1.1)

---

## PASO 0 — Preparar el entorno

### Clonar el repositorio

```powershell
git clone <URL-del-repo>
cd Tesis_Proyecto
```

### Crear entorno virtual e instalar dependencias

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1        # PowerShell
# o: venv\Scripts\activate.bat     # CMD

pip install -r requirements.txt
```

### Verificar estructura de carpetas

```powershell
dir data\raw
dir src\data
dir extension
```

---

## PASO 1 — Gestión de Datos

### 1.1 y 1.2 — Verificar fuentes de datos ✅

Los dos datasets ya están en el repositorio:

| Dataset | Ruta |
|---------|------|
| Spanish Hate Speech Superset (Tonneau et al., 2024) | `data/raw/spanish-hate-speech-superset/es_hf_102024.csv` |
| DETOXIS (IberLEF 2021) | `data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv` |

Para verificar que están íntegros:

```powershell
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_corpus.py
```

---

### 1.3 — Exploración inicial ✅

Genera estadísticas, figuras y reporte sobre los dos datasets.

```powershell
.\venv\Scripts\python.exe scripts\exploracion_inicial.py
```

**Salidas generadas:**
- `data/reports_qc/exploracion_inicial.md` — reporte ejecutivo
- `data/reports_qc/exploracion_inicial.json` — métricas crudas
- `data/reports_qc/figuras/*.png` — 4 figuras comparativas

---

### 1.4 — Módulo de limpieza (`clean.py`) ✅

El módulo `src/data/clean.py` ya está implementado. Aplica normalización **solo a DETOXIS** (el superset ya viene preprocesado).

Para verificar que funciona:

```powershell
.\venv\Scripts\python.exe src\data\clean.py
```

**Qué hace:** repara encoding, decodifica HTML, elimina caracteres invisibles, normaliza URLs → `URL`, menciones → `USUARIO`, convierte emojis a texto, colapsa repeticiones.

---

### 1.5 — Unificación del corpus ✅

Integra el superset y DETOXIS en un único archivo con esquema canónico.

```powershell
.\venv\Scripts\python.exe src\data\unify.py
```

**Salida:** `data/interim/corpus_combinado.parquet`

| Métrica | Valor |
|---------|-------|
| Total filas | 33,318 |
| Hate (1) | 7,603 (22.8%) |
| No hate (0) | 25,715 (77.2%) |
| Datasets incluidos | chileno, misocorpus, haternet, homomex, hateval, hascosva, detoxis |

---

### 1.6 — Lexicón de modismos latinoamericanos ✅

Construye la columna `tiene_modismo` que permite segmentar la evaluación (validación de H3). El lexicón tiene un rol **observacional**: no alimenta al modelo, solo marca las instancias del corpus.

El CSV y el módulo ya están implementados. Para verificar:

```powershell
.\venv\Scripts\python.exe src\data\lexicon.py
```

**Resultado esperado:**

```
Terminos canonicos : 383
Tokens totales     : 886
Con modismo        : 17,722  (53.19%)
Requisito >=15%    : [OK]
```

**Archivos:**
- `data/lexicons/modismos_latam_v1.csv` — 383 términos (MX, AR, CL, CO, PE, VE, EC, MULTI)
- `src/data/lexicon.py` — clase `LexiconLatam` con `tiene_modismo()`

**Cómo importar desde otros módulos:**

```python
from src.data.lexicon import LexiconLatam

lex = LexiconLatam("data/lexicons/modismos_latam_v1.csv")
tiene = lex.tiene_modismo("Ese pinche tipo no sabe nada")  # True
```

---

### 1.7 — Enriquecer corpus con `tiene_modismo` ✅

Aplica el lexicón LATAM sobre el corpus combinado para agregar las columnas `tiene_modismo` (bool) y `n_tokens_aprox` (int16). El resultado es el corpus listo para QC y particionado.

```powershell
.\venv\Scripts\python.exe src\data\enrich.py
```

**Resultado esperado:**

```
Con modismo  : 17,722  (53.19%)
Sin modismo  : 15,596  (46.81%)
Requisito >=15%: [OK]
```

**Salida:** `data/processed/corpus_v1_enriquecido.parquet` (33,318 filas, 10 columnas)

**Cómo importar desde otros módulos:**

```python
from src.data.enrich import enriquecer_corpus

corpus = enriquecer_corpus(verbose=True)

# O solo leer el Parquet ya generado
import pandas as pd
corpus = pd.read_parquet("data/processed/corpus_v1_enriquecido.parquet")
```

---

### 1.8 — Validación de calidad del corpus ✅

Valida la integridad del corpus enriquecido y genera el reporte QC completo.

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\data\qc.py
```

**Resultado esperado:**

```
============================================================
  PASO 1.8 - Validación de calidad del corpus
============================================================
Cargando corpus desde data\processed\corpus_v1_enriquecido.parquet...
  33,318 filas, 10 columnas

--- Validaciones de integridad ---
  [ADVERTENCIA] 141 textos con < 3 tokens (0.4%) -- dentro del umbral aceptable.
[OK] Corpus validado correctamente -- todas las aserciones pasaron.

--- Detección de duplicados ---
  Duplicados exactos      : 217
  Duplicados normalizados : 341

--- Generando reporte QC ---
  Reporte QC guardado en: data\reports_qc\qc_corpus_v1.md

============================================================
Paso 1.8 completado exitosamente.
============================================================
```

**Salidas generadas:**
- `data/reports_qc/qc_corpus_v1.md` — Reporte QC completo con: tamaño, distribución por dataset, modismos cruzada, longitudes, duplicados, top-30 unigramas y bigramas por clase

**Hallazgos del QC:**

| Aserción | Resultado |
|----------|-----------|
| IDs únicos | [OK] — todos únicos |
| Textos no nulos | [OK] — 0 nulos |
| Textos ≥ 3 tokens | [ADVERTENCIA] — 141 casos (0.4%) — aceptable |
| Etiquetas ∈ {0,1} | [OK] |
| tiene_modismo dtype==bool | [OK] |
| Proporción hate ∈ [5%,60%] | [OK] — 22.8% |
| Cobertura modismos ≥ 15% | [OK] — 53.2% |

> **Nota sobre duplicados:** 217 textos exactamente repetidos entre datasets. Los IDs son únicos (generados como `<dataset>_<índice>`). Se recomienda eliminar duplicados antes del entrenamiento en el Paso 1.9.

**Cómo importar desde otros módulos:**

```python
from src.data.qc import validar_corpus, ejecutar_qc_completo
import pandas as pd

# Solo validar (lanza AssertionError si falla)
corpus = pd.read_parquet("data/processed/corpus_v1_enriquecido.parquet")
validar_corpus(corpus)

# O ejecutar el QC completo (valida + genera reporte)
corpus = ejecutar_qc_completo()
```

---

### 1.9 — Particionado train/val/test ✅

Elimina duplicados, parte el corpus en 70/15/15 con estratificación por etiqueta y verifica que no haya data leakage entre splits.

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\data\split.py
```

**Resultado esperado:**

```
============================================================
  PASO 1.9 - Particionado train/val/test
============================================================

--- Eliminando duplicados (nivel 2) ---
  Duplicados exactos eliminados    : 217
  Duplicados normalizados eliminados: 114
  Total eliminados                 : 331
  Filas restantes                  : 32987

--- Distribución de clases ---
  no_hate (0): 25460  (77.2%)
  hate (1): 7527  (22.8%)

--- Particionado (70/15/15, seed=42) ---

  Train : 23090 filas  (70.0% del total)  |  hate: 22.8%
  Val   :  4948 filas  (15.0% del total)  |  hate: 22.8%
  Test  :  4949 filas  (15.0% del total)  |  hate: 22.8%

--- Verificación de data leakage ---
  [OK] Sin leakage train↔val
  [OK] Sin leakage train↔test
  [OK] Sin leakage val↔test

============================================================
Paso 1.9 completado exitosamente.
  Train : 23,090 filas -> data/processed/train.parquet
  Val   : 4,948 filas -> data/processed/val.parquet
  Test  : 4,949 filas -> data/processed/test.parquet
============================================================
```

**Salidas generadas:**
- `data/processed/train.parquet` — 23,090 filas (70%)
- `data/processed/val.parquet` — 4,948 filas (15%)
- `data/processed/test.parquet` — 4,949 filas (15%)

**Detalles de deduplicación:**

| Nivel | Duplicados eliminados |
|-------|----------------------|
| Exactos (texto idéntico) | 217 |
| Normalizados (lowercase + sin puntuación) | 114 |
| **Total** | **331** |

**Data leakage check — todos limpios:** train↔val, train↔test, val↔test = **0 textos solapados**.

**Cómo importar desde otros módulos:**

```python
from src.data.split import particionar_corpus

# Generar los splits (los guarda automáticamente en data/processed/)
train, val, test = particionar_corpus(verbose=True)

# O solo leer los Parquets ya generados
import pandas as pd
train = pd.read_parquet("data/processed/train.parquet")
val   = pd.read_parquet("data/processed/val.parquet")
test  = pd.read_parquet("data/processed/test.parquet")
```

---

### 1.10 — Crear MANIFEST.json ✅

Genera `data/processed/MANIFEST.json` con los hashes SHA-256 de todos los Parquets del corpus y el commit git del momento de creación.

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe scripts\crear_manifest.py
```

**Resultado esperado:**

```
============================================================
  PASO 1.10 - Crear MANIFEST.json
============================================================

Calculando SHA-256...
  corpus_v1_enriquecido : 4a76b4005244ce454a08dc2c1580807b...
  train                 : 24150e7edac3bcbf167c6183941997e9...
  val                   : 99445ea7397cdbe36d6fa4dae31a7bb4...
  test                  : f07165adca005065e9a9e65f6385a867...

Commit git            : 0d37d0e14b3c...

[OK] MANIFEST.json guardado en: ...\data\processed\MANIFEST.json

============================================================
Paso 1.10 completado exitosamente.
============================================================
```

**Salida generada:**
- `data/processed/MANIFEST.json` — metadatos de versión del corpus: SHA-256 de los 4 Parquets, commit git, timestamp UTC, datasets de origen, versión del lexicón, conteos reales y resumen del pipeline.

| Archivo | SHA-256 |
|---------|----------|
| `corpus_v1_enriquecido.parquet` | `4a76b4005244ce454a08dc2c1580807bc2876e911f236e2ad2bc779e799c9c3c` |
| `train.parquet` | `24150e7edac3bcbf167c6183941997e936acdf1f14f425be95545b5ad7db7fc8` |
| `val.parquet` | `99445ea7397cdbe36d6fa4dae31a7bb479523b05417157df1b4864a303853cfc` |
| `test.parquet` | `f07165adca005065e9a9e65f6385a8670fe61edfe3d23ecca700278c0fbaa59b` |

> **Nota:** Volver a ejecutar el script cada vez que se regeneren los Parquets para mantener el MANIFEST sincronizado.

---

### 1.11 — Reporte QC final del corpus v1 ✅

Genera la figura de 4 paneles y el reporte QC completo que integra los datos del corpus enriquecido y los tres splits (train/val/test).

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe scripts\generar_reporte_qc_final.py
```

**Salidas generadas:**
- `data/reports_qc/figuras/qc_corpus_v1_4paneles.png` — 4 paneles: clases, modismos, datasets, longitudes
- `data/reports_qc/qc_corpus_v1_final.md` — Reporte QC final con tabla de splits, cruzada etiqueta×modismo y checklist de aserciones + leakage

| Métrica | Valor |
|---------|-------|
| Corpus total | 33,318 filas |
| Hate (1) | 7,603 (22.8%) |
| No hate (0) | 25,715 (77.2%) |
| Con modismo | 17,722 (53.2%) |
| Data leakage | 0 solapamientos ✅ |
| Todas las aserciones QC | ✅ OK |

> **La Fase 1 está completa.** El siguiente paso es la Fase 2: entrenar los modelos (requiere GPU).

---

## PASOS 2, 3, 4 Y 5A — Fine-tuning, Evaluación, Modismos y XAI ✅

> **Todo en un solo notebook de Colab:** `notebooks/colab_entrenamiento_evaluacion_xai.ipynb`  
> Todas estas fases están completadas. Este paso explica cómo replicarlas.

### Qué cubre el notebook

| Fase | Qué hace | Salidas en Drive |
|------|----------|------------------|
| **Fase 2** | Fine-tuning de BETO, mBERT y XLM-R (3 semillas c/u) + selección del mejor BETO | `models/` (10 carpetas) |
| **Fase 3** | Evaluación en test set, bootstrap (IC 95%), test de McNemar | `reports/tables/`, `reports/predictions/` |
| **Fase 4** | Segmentación por modismos LATAM, validación estadística de H3 | `reports/tables/h3_idiom_analysis/` |
| **Fase 5A** | Análisis SHAP — explicabilidad sobre errores de BETO (necesita GPU) | `reports/tables/xai_analysis/` |

### Paso A — Preparar Google Drive

Sube a `Mi unidad/unmsm/ciclo 2026-1/tesis/COLAB/` desde tu PC local:

```
COLAB/
├── data/processed/
│   ├── train.parquet
│   ├── val.parquet
│   ├── test.parquet
│   └── corpus_v1_enriquecido.parquet
└── scripts/
    ├── train_model.py
    └── evaluate_model.py
```

### Paso B — Ejecutar en Colab

1. Abre [colab.research.google.com](https://colab.research.google.com) → carga `notebooks/colab_entrenamiento_evaluacion_xai.ipynb` desde Drive
2. Menú `Entorno de ejecución` → `Cambiar tipo` → **GPU T4**
3. Ejecuta las celdas de **arriba hacia abajo**, una a una

> Si Colab se desconecta, todos los archivos ya guardados en Drive quedan intactos. Solo continúa desde la celda siguiente.
>
> **Tiempo estimado:** Fase 2 ≈ 9–12 h | Fase 3 ≈ 30 min | Fase 4 ≈ 10 min | Fase 5A ≈ 20–30 min

### Paso C — Descargar resultados a tu PC

Al terminar, descarga desde Drive hacia `Tesis_Proyecto/`:

```powershell
# Verificar estructura local una vez descargados:
dir models\
dir reports\tables\
dir reports\predictions\
dir reports\tables\h3_idiom_analysis\
dir reports\tables\xai_analysis\
```

**Resultado esperado:**

```
models/
├── beto_finetuned_42/         ← model.safetensors + tokenizador
├── beto_finetuned_123/
├── beto_finetuned_2024/
├── beto_finetuned_final/      ← mejor BETO (F1-val=0.7186, seed=42)
├── mbert_finetuned_42/
├── mbert_finetuned_123/
├── mbert_finetuned_2024/
├── xlmr_finetuned_42/         ← incluye sentencepiece.bpe.model
├── xlmr_finetuned_123/
└── xlmr_finetuned_2024/

reports/
├── tables/
│   ├── metrics_all_models.csv
│   ├── metrics_all_models.json
│   ├── comparativa_global.csv
│   ├── bootstrap_ic.csv
│   ├── mcnemar_results.csv
│   ├── h3_idiom_analysis/
│   │   ├── h3_test_segmentation.csv
│   │   ├── h3_beto_evaluation_subsets.csv
│   │   └── h3_hypothesis_validation.csv
│   └── xai_analysis/              ← Fase 5A
│       ├── shap_wrong_predictions.csv
│       ├── shap_analysis_results.csv
│       ├── shap_full_weights.json
│       └── shap_modismo_tokens.csv
└── predictions/
    ├── beto_42_preds.csv  ...  xlmr_2024_preds.csv  (9 archivos)
```

---

## PASO 5B — Módulo XAI local ✅

Crea la clase `ShapExplainer` que el backend usa para el endpoint `/explain`.
No necesita GPU — solo ejecutar en local.

Los archivos ya están implementados. Para verificar que funcionan (requiere `models/beto_finetuned_final/`):

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\xai\shap_explainer.py
```

**Salida esperada:**
```
Cargando ShapExplainer...
  Modelo: models/beto_finetuned_final
  ✅ Explainer cargado

Texto: 'Ese pinche tipo me cae muy mal'
  Tokens (...): ['ese', 'pinche', 'tipo', ...]
  Top-3 tokens: [('pinche', 0.42), ('tipo', 0.10), ...]
```

**Archivos:**
- `src/xai/shap_explainer.py` — clase `ShapExplainer` con `explain()` y `explain_top()`
- `src/xai/__init__.py` — exporta `ShapExplainer`

**Cómo lo usará el backend (Fase 6):**

```python
from src.xai import ShapExplainer

exp = ShapExplainer("models/beto_finetuned_final")
resultado = exp.explain("Ese pinche tipo me cae muy mal")
# → {"tokens": [...], "pesos": [...]}
```

---

## Archivos de referencia

| Archivo | Para qué sirve |
|---------|---------------|
| [`INSTRUCCIONES_PROYECTO.md`](INSTRUCCIONES_PROYECTO.md) | Enunciado oficial y especificación técnica completa (22 secciones) |
| [`PLAN_DESARROLLO.md`](PLAN_DESARROLLO.md) | Itinerario paso a paso con código y estado de cada paso |
| [`../EXPERIMENTOS.md`](../EXPERIMENTOS.md) | Bitácora científica — registrar decisiones y resultados |

---

## PASO 6 — Backend FastAPI

### 6.1 — Crear archivos de la API ✅

Implementa los 3 archivos principales del backend: configuración, esquemas y aplicación.

Los archivos ya están implementados en `src/api/`. Para verificar que importan correctamente:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -c "from src.api.main import app; print('OK'); print([r.path for r in app.routes])"
```

**Resultado esperado:**
```
OK
['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc', '/health', '/metadata', '/predict', '/explain']
```

**Archivos implementados:**

| Archivo | Contenido |
|---------|-----------|
| `src/api/config.py` | Clase `Settings` (pydantic-settings): ruta al modelo, umbral, CORS, log level. Lee `.env` si existe. |
| `src/api/schemas.py` | Esquemas Pydantic v2: `PredictRequest`, `PredictResponse`, `ExplainResponse`, `HealthResponse`, `MetadataResponse`. |
| `src/api/main.py` | App FastAPI con 4 endpoints, modo degradado si el modelo no existe, SHAP con fallback. |

**Endpoints disponibles:**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado del servicio y si el modelo está cargado |
| `/metadata` | GET | Versión del modelo, umbral y configuración activa |
| `/predict` | POST | Clasificación binaria (hate / no_hate) con probabilidad |
| `/explain` | POST | Igual que `/predict` + tokens y pesos SHAP por token |

**Detalles de implementación:**
- **Modo degradado:** si `models/beto_finetuned_final/` no existe, el servidor arranca igual (HTTP 503 en `/predict` y `/explain`).
- **CORS:** acepta cualquier origen `chrome-extension://` y `localhost`.
- **Umbral configurable:** por defecto 0.5; ajustable en `.env` (`THRESHOLD=0.7`).
- **SHAP lazy load:** el `ShapExplainer` se inicializa solo en la primera petición a `/explain`, y hace fallback a tokens simples si SHAP no está disponible.

---

### 6.2 — Ejecutar el servidor ✅

> **Este paso lo ejecutas tú en tu terminal.** El servidor queda corriendo en segundo plano mientras usas la extensión.

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
```

**Verificaciones tras arrancar:**

| URL | Qué verificar |
|-----|---------------|
| http://127.0.0.1:8000/health | `"model_loaded": true` |
| http://127.0.0.1:8000/docs | Swagger UI interactivo |
| http://127.0.0.1:8000/metadata | Versión y configuración activa |

**Probar el endpoint `/predict` desde PowerShell:**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict `
  -Method POST `
  -ContentType 'application/json' `
  -Body '{"texto": "Ese pinche tipo me cae muy mal"}'
```

**Respuesta esperada:**
```json
{
  "etiqueta": "hate",
  "probabilidad": 0.87,
  "modelo": "beto_finetuned",
  "version": "v1"
}
```

> **Nota:** Si `model_loaded` es `false`, verificar que `models/beto_finetuned_final/` existe. El servidor arranca en modo degradado (HTTP 503 en `/predict` y `/explain`) hasta que el modelo esté disponible.

> **Mantener el servidor corriendo** para integrar la extensión Chrome en la siguiente fase.

---

## PASO 7 — Extensión Chrome — Integración con BETO ✅

### 7.1 — Estado de la extensión (prototipo previo)

La extensión (`extension/`) ya existía como prototipo funcional con:
- Detección por **lexicón local** (~94 términos, 4 categorías)
- 4 modos de censura: resaltar, difuminar, asteriscos, ocultar
- Lexicón personal (CRUD + export/import)
- Estadísticas por pestaña
- Cliente HTTP (`api.js`) y cola de inferencia ya implementados

### 7.2 — Integración BETO completada ✅

Se implementaron los 3 cambios que faltaban para conectar la extensión con el backend:

**Cambio 1 — `extension/content.js`:** recolección de fragmentos y envío al modelo

En cada escaneo del DOM, si `apiHabilitada=true`, el content script:
1. Hace un segundo recorrido del árbol de texto
2. Recolecta hasta 50 fragmentos únicos (≤512 chars, ≥15 chars)
3. Les asigna un ID único y guarda la referencia al elemento padre en `window.__hateRefs`
4. Los envía al service worker con `enviarLoteAlModelo(fragmentos)`

**Cambio 2 — `extension/content.js`:** procesar resultados y aplicar marca `.hate-ml`

`aplicarResultadoML(resultado)`: cuando el SW responde con `tipo=RESULTADO`:
- Si `etiqueta=hate` y `probabilidad ≥ umbralMl` → agrega clase `.hate-ml` al elemento
- El tooltip muestra la probabilidad: `BETO: hate (p=0.87)`

`aplicarExplicacion(resultado)`: cuando el SW responde con `tipo=EXPLAIN_RES`:
- Resalta tokens SHAP dentro del elemento con `.hate-explain-token`

**Cambio 3 — `extension/styles.css`:** CSS para marcas BETO

| Clase | Color | Cuándo aparece |
|-------|-------|----------------|
| `.hate-ml` | Violeta (outline) | Texto que BETO clasifica como hate |
| `.hate-explain-token[data-shap-positive]` | Rojo translúcido | Token que empuja hacia hate |
| `.hate-explain-token[data-shap-negative]` | Verde translúcido | Token que empuja hacia no_hate |

> Las marcas del lexicón (`.hate-detect-mark`) son **rojas**. Las de BETO (`.hate-ml`) son **violetas**. Esto permite distinguir visualmente qué detectó qué.

### 7.3 — Smoke test end-to-end ✅

**Requisitos:**
1. El backend corre en `http://127.0.0.1:8000` (con `model_loaded: true`)
2. La extensión está instalada en Chrome/Edge
3. En la **Options Page** → activar **"Habilitar API"** → esto escribe `apiHabilitada=true` en `chrome.storage.local`
4. Recargar la extensión desde `chrome://extensions`

**Verificar:**
```
extension/test/demo.html → activar detección → deben aparecer:
  - Marcas rojas:   lexicón local detectó algo
  - Marcas violeta: BETO (≥ umbralMl=0.7) detectó hate
```

**Sin `TODO BETO` pendientes:**
```powershell
findstr /S /N /I "TODO BETO" extension\*.js
# Solo aparecen comentarios informativos — ningún stub funcional pendiente
```

### 7.4 — Activar la API desde la extensión

En la Options Page (`chrome://extensions` → Opciones), activar el toggle **"Habilitar API"**. Esto escribe en `chrome.storage.local`:
```javascript
{ apiHabilitada: true, apiUrl: "http://127.0.0.1:8000" }
```

El content script lo detecta automáticamente vía `storage.onChanged` y empieza a enviar fragmentos al backend en el próximo escaneo.

---

## Sistema end-to-end — Verificación final ✅

| Capa | Estado |
|------|--------|
| Corpus (train/val/test) | ✅ 32,987 filas, sin leakage |
| Lexicón LATAM | ✅ 383 términos, cobertura 53.2% |
| Modelos entrenados (9 + final) | ✅ BETO F1=0.72, en `models/` |
| Evaluación + bootstrap + McNemar | ✅ `reports/tables/` |
| Análisis H3 (modismos) | ✅ `reports/tables/h3_idiom_analysis/` |
| XAI SHAP (análisis) | ✅ `reports/tables/xai_analysis/` |
| Backend FastAPI (4 endpoints) | ✅ `http://127.0.0.1:8000` |
| Extensión Chrome — lexicón | ✅ 4 modos de censura |
| Extensión Chrome — BETO ML | ✅ Marcas `.hate-ml` (violeta) |
| Extensión Chrome — XAI SHAP | ✅ Tokens `.hate-explain-token` |
