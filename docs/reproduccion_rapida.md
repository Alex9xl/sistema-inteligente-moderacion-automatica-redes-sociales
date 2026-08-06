# Reproducción Rápida

Resumen operativo de los comandos para volver a ejecutar todo el proyecto, **asumiendo que ya tienes `data/raw/`** con los datasets crudos descargados. Para la guía extendida con explicaciones, salidas esperadas y criterios de validación, ver `documentos_extras/GUIA_REPRODUCCION.md`.

## 0. Entorno

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 1. Verificar datos crudos (opcional)

```powershell
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_corpus.py
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_datasets_detoxis.py
```

## 2. Exploración inicial

```powershell
.\venv\Scripts\python.exe scripts\exploracion_inicial.py
```

## 3. Construcción del corpus (pipeline principal, en orden)

```powershell
$env:PYTHONIOENCODING='utf-8'

.\venv\Scripts\python.exe src\data\clean.py       # limpieza (normaliza DETOXIS)
.\venv\Scripts\python.exe src\data\unify.py       # unificación en esquema binario
.\venv\Scripts\python.exe src\data\lexicon.py     # verifica lexicón LATAM
.\venv\Scripts\python.exe src\data\enrich.py      # agrega columna tiene_modismo
.\venv\Scripts\python.exe src\data\qc.py          # control de calidad
.\venv\Scripts\python.exe src\data\split.py       # particionado train/val/test
```

> **Importante:** no usar `make data`. Ese objetivo apunta a `scripts/prepare_data.py`, que está vacío (placeholder sin implementar). El pipeline real y funcional es la secuencia de `src/data/` de arriba.

## 4. Manifiesto y reporte final de QC

```powershell
.\venv\Scripts\python.exe scripts\crear_manifest.py
.\venv\Scripts\python.exe scripts\generar_reporte_qc_final.py
```

Al terminar los pasos 3 y 4 deberían existir: `data/interim/corpus_combinado.parquet`, `data/processed/corpus_v1_enriquecido.parquet`, `data/processed/{train,val,test}.parquet`, `data/processed/MANIFEST.json` y los reportes en `data/reports_qc/`.

## 5. Entrenamiento (requiere GPU → Google Colab)

1. Sube a Google Drive:
   ```text
   COLAB/
   ├── data/processed/{train,val,test,corpus_v1_enriquecido}.parquet
   └── scripts/{train_model.py, evaluate_model.py}
   ```
2. Abre `notebooks/colab_entrenamiento_evaluacion_xai.ipynb` con GPU T4.
3. Ejecuta las celdas en orden **+ las 3 celdas extra de H1** (comparación BETO ajustado vs. BETO base, obligatorias para esa hipótesis).
4. Descarga los artefactos de vuelta: modelos a `models/`, tablas a `reports/tables/` y `reports/predictions/`.

Alternativa si se entrena manualmente (esto es lo que hace `make train`):

```powershell
python scripts\train_model.py --model beto  --seed 42
python scripts\train_model.py --model beto  --seed 123
python scripts\train_model.py --model beto  --seed 2024
python scripts\train_model.py --model mbert --seed 42
python scripts\train_model.py --model mbert --seed 123
python scripts\train_model.py --model mbert --seed 2024
python scripts\train_model.py --model xlmr  --seed 42
python scripts\train_model.py --model xlmr  --seed 123
python scripts\train_model.py --model xlmr  --seed 2024
```

Luego copiar manualmente el mejor checkpoint de BETO (mayor F1 hate) a `models/beto_finetuned_final/`.

## 6. Verificar módulo XAI

Requiere que ya exista `models/beto_finetuned_final/`.

```powershell
.\venv\Scripts\python.exe src\xai\shap_explainer.py
```

## 7. Levantar la API

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

No usar `make api` en Windows: puede fallar según cómo estén resueltos `make`, `PATH` o el entorno virtual.

Prueba rápida:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict `
  -Method POST -ContentType 'application/json' `
  -Body '{"texto": "Ese pinche tipo me cae muy mal"}'
```

## 8. Cargar la extensión

`chrome://extensions/` (o `edge://extensions/`) → activar "Modo de desarrollador" → "Cargar extensión sin empaquetar" → seleccionar la carpeta `extension/`.

## 9. Pruebas automatizadas

```powershell
.\venv\Scripts\python.exe -m pytest

node --check extension\content.js
node --check extension\background.js
node --check extension\api.js
node --check extension\popup\popup.js
node --check extension\options\options.js
```

## Resumen en una tabla

| Paso | Comando(s) | Dónde corre |
|---|---|---|
| 1. Verificar datos | `verificar_corpus.py`, `verificar_datasets_detoxis.py` | Local |
| 2. Exploración | `scripts/exploracion_inicial.py` | Local |
| 3. Corpus (6 sub-pasos) | `src/data/clean.py → unify.py → lexicon.py → enrich.py → qc.py → split.py` | Local |
| 4. Manifiesto/QC final | `crear_manifest.py`, `generar_reporte_qc_final.py` | Local |
| 5. Entrenamiento | Notebook `colab_entrenamiento_evaluacion_xai.ipynb` (o `train_model.py` × 9 combinaciones) | **Colab (GPU)** |
| 6. XAI | `src/xai/shap_explainer.py` | Local |
| 7. API | `uvicorn src.api.main:app ...` | Local |
| 8. Extensión | Carga manual en Chrome/Edge | Local (navegador) |
| 9. Tests | `pytest`, `node --check ...` | Local |

## Referencia

Guía extendida con explicaciones detalladas, salidas esperadas de cada paso y criterios de reproducción satisfactoria: `documentos_extras/GUIA_REPRODUCCION.md`.
