# COMENZAR AQUÍ — Guía de Replicación

> Este archivo te lleva de cero a replicar el estado actual del proyecto con comandos concretos.
> Se actualiza con cada paso completado. Estado actual: **Paso 1.10 completado**.

---

## ¿De qué trata el proyecto?

Sistema de detección automática de discurso de odio en español. El núcleo es ajustar el modelo **BETO** (BERT en español) con un corpus enriquecido con modismos latinoamericanos, y compararlo contra modelos multilingües (mBERT, XLM-R). El sistema se expone como backend REST y extensión de Chrome.

**Tres hipótesis a validar:**
- **H1** — BETO ajustado supera a BETO sin ajuste fino
- **H2** — BETO ajustado iguala o supera a mBERT y XLM-R en español
- **H3** — BETO ajustado rinde mejor en textos con modismos LATAM que sin ellos

Para más detalle técnico: [`guia.md`](guia.md) | Para el itinerario paso a paso: [`desarrollo.md`](desarrollo.md)

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

## Próximos pasos (aún no implementados)

| Paso | Descripción |
|------|-------------|
| **1.11** | Reporte QC final |
| **Fase 2** | Entrenamiento de BETO, mBERT y XLM-R (requiere GPU) |

---

## Archivos de referencia

| Archivo | Para qué sirve |
|---------|---------------|
| [`guia.md`](guia.md) | Especificación técnica completa (22 secciones) |
| [`desarrollo.md`](desarrollo.md) | Itinerario paso a paso con código y estado de cada paso |
| [`../EXPERIMENTOS.md`](../EXPERIMENTOS.md) | Bitácora científica — registrar decisiones y resultados |
| [`../ESTADO_PROYECTO.md`](../ESTADO_PROYECTO.md) | Resumen ejecutivo del estado actual |
