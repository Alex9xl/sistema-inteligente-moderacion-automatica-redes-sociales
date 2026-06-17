# COMENZAR AQUÍ — Guía de Replicación

> Este archivo te lleva de cero a replicar el estado actual del proyecto con comandos concretos.
> Se actualiza con cada paso completado. Estado actual: **Paso 1.6 completado**.

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

## Próximos pasos (aún no implementados)

| Paso | Descripción |
|------|-------------|
| **1.7** | Enriquecer corpus con columna `tiene_modismo` → `corpus_v1_enriquecido.parquet` |
| **1.8** | Validación de calidad (`src/data/qc.py`) |
| **1.9** | Particionar en train/val/test (70/15/15 estratificado) |
| **1.10** | Crear `data/processed/MANIFEST.json` con hashes |
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
