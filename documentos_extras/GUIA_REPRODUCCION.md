# Guia de Reproduccion del Proyecto

Este documento describe como reproducir el proyecto completo desde un entorno limpio. Su audiencia principal es un evaluador externo, por ejemplo un docente o jurado, que desea comprobar que los datos, scripts, notebooks, modelos, reportes, API y extension funcionan de acuerdo con los objetivos del repositorio.

Para la especificacion metodologica completa, consultar `INSTRUCCIONES_PROYECTO.md`. Para el plan de construccion desde cero, consultar `PLAN_DESARROLLO.md`.

## 1. Requisitos

- Python 3.10 o superior.
- Git.
- PowerShell en Windows.
- Espacio suficiente para datasets, modelos y reportes.
- Acceso a GPU para reproducir el entrenamiento completo de modelos Transformer. Se recomienda Google Colab con GPU T4.
- Navegador Chrome o Edge para probar la extension.

## 2. Preparacion del entorno local

Clonar el repositorio:

```powershell
git clone <URL-del-repositorio>
cd Tesis_Proyecto
```

Crear entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Verificar estructura minima:

```powershell
dir data\raw
dir src\data
dir src\api
dir extension
```

## 3. Fuentes de datos

El corpus se construye a partir de dos fuentes principales:

| Fuente | Ruta esperada |
|--------|---------------|
| Spanish Hate Speech Superset, Tonneau et al. 2024 | `data/raw/spanish-hate-speech-superset/es_hf_102024.csv` |
| DETOXIS, IberLEF 2021 | `data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv` |

Verificar disponibilidad e integridad basica:

```powershell
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_corpus.py
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_datasets_detoxis.py
```

## 4. Exploracion inicial

Ejecutar el analisis exploratorio reproducible:

```powershell
.\venv\Scripts\python.exe scripts\exploracion_inicial.py
```

Salidas esperadas:

| Archivo | Descripcion |
|---------|-------------|
| `data/reports_qc/exploracion_inicial.md` | Reporte ejecutivo de exploracion. |
| `data/reports_qc/exploracion_inicial.json` | Metricas en formato estructurado. |
| `data/reports_qc/figuras/distribucion_clases.png` | Distribucion de clases por fuente. |
| `data/reports_qc/figuras/volumen_datasets.png` | Volumen por dataset. |
| `data/reports_qc/figuras/longitud_tokens.png` | Longitud de textos. |
| `data/reports_qc/figuras/seeds_latam.png` | Cobertura preliminar de semillas LATAM. |

## 5. Construccion del corpus

### 5.1 Limpieza

Verificar el modulo de normalizacion:

```powershell
.\venv\Scripts\python.exe src\data\clean.py
```

La normalizacion se aplica a DETOXIS. El superset conserva su preprocesamiento original.

### 5.2 Unificacion

Construir el corpus combinado con esquema canonico:

```powershell
.\venv\Scripts\python.exe src\data\unify.py
```

Salida esperada:

```text
data/interim/corpus_combinado.parquet
```

### 5.3 Lexicon LATAM

Verificar el lexicon de modismos latinoamericanos:

```powershell
.\venv\Scripts\python.exe src\data\lexicon.py
```

Artefactos principales:

| Archivo | Descripcion |
|---------|-------------|
| `data/lexicons/modismos_latam_v1.csv` | Lexicon documentado de modismos LATAM. |
| `src/data/lexicon.py` | Clase `LexiconLatam` y funcion de deteccion. |

### 5.4 Enriquecimiento

Agregar variables derivadas al corpus:

```powershell
.\venv\Scripts\python.exe src\data\enrich.py
```

Salida esperada:

```text
data/processed/corpus_v1_enriquecido.parquet
```

### 5.5 Control de calidad

Ejecutar validaciones del corpus:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe src\data\qc.py
```

Salida esperada:

```text
data/reports_qc/qc_corpus_v1.md
```

### 5.6 Particionado

Generar splits estratificados train, validation y test:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe src\data\split.py
```

Salidas esperadas:

| Archivo | Uso |
|---------|-----|
| `data/processed/train.parquet` | Entrenamiento. |
| `data/processed/val.parquet` | Validacion y seleccion de modelo. |
| `data/processed/test.parquet` | Evaluacion final. |

### 5.7 Manifiesto y reporte final

Generar manifiesto de artefactos:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe scripts\crear_manifest.py
```

Generar reporte QC final:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe scripts\generar_reporte_qc_final.py
```

Salidas esperadas:

| Archivo | Descripcion |
|---------|-------------|
| `data/processed/MANIFEST.json` | Hashes, versiones y trazabilidad del corpus. |
| `data/reports_qc/qc_corpus_v1_final.md` | Reporte final del corpus y splits. |
| `data/reports_qc/figuras/qc_corpus_v1_4paneles.png` | Figura resumen del corpus. |

## 6. Entrenamiento, evaluacion y XAI en Colab

El entrenamiento completo de BETO, mBERT y XLM-R se reproduce mediante:

```text
notebooks/colab_entrenamiento_evaluacion_xai.ipynb
```

### 6.1 Preparar Google Drive

Subir a Drive la carpeta de trabajo con esta estructura:

```text
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

### 6.2 Ejecutar notebook

1. Abrir Google Colab.
2. Cargar `notebooks/colab_entrenamiento_evaluacion_xai.ipynb`.
3. Seleccionar GPU T4.
4. Ejecutar las celdas en orden.
5. Ejecutar las 3 celdas extra de la Hipotesis 1.
6. Descargar los artefactos generados hacia el repositorio local.

Las 3 celdas extra de H1 son obligatorias para la reproduccion academica del proyecto. Generan la comparacion entre BETO ajustado y BETO base sin fine-tuning, y producen los artefactos necesarios para sustentar la Hipotesis 1 en el informe de tesis.

### 6.3 Artefactos esperados

Modelos:

```text
models/
├── beto_finetuned_42/
├── beto_finetuned_123/
├── beto_finetuned_2024/
├── beto_finetuned_final/
├── mbert_finetuned_42/
├── mbert_finetuned_123/
├── mbert_finetuned_2024/
├── xlmr_finetuned_42/
├── xlmr_finetuned_123/
└── xlmr_finetuned_2024/
```

Reportes:

```text
reports/
├── tables/
│   ├── metrics_all_models.csv
│   ├── metrics_all_models.json
│   ├── comparativa_global.csv
│   ├── bootstrap_ic.csv
│   ├── mcnemar_results.csv
│   ├── h3_idiom_analysis/
│   └── xai_analysis/
└── predictions/
```

## 7. Modulo XAI local

Verificar que el explicador usado por la API carga correctamente:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe src\xai\shap_explainer.py
```

Este paso requiere que exista:

```text
models/beto_finetuned_final/
```

## 8. Backend FastAPI

Verificar imports y rutas:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe -c "from src.api.main import app; print('OK'); print([r.path for r in app.routes])"
```

Levantar el servidor:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Este es el comando recomendado para Windows. No usar `make api` como instruccion principal de reproduccion, porque puede fallar si `make`, `uvicorn` o el entorno virtual no quedan resueltos correctamente en el `PATH`.

Endpoints:

| Endpoint | Metodo | Proposito |
|----------|--------|-----------|
| `/health` | GET | Estado del servicio y carga del modelo. |
| `/metadata` | GET | Version, umbral y configuracion activa. |
| `/predict` | POST | Clasificacion binaria y probabilidad. |
| `/explain` | POST | Prediccion con explicacion por tokens. |

Prueba de inferencia:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict `
  -Method POST `
  -ContentType 'application/json' `
  -Body '{"texto": "Ese pinche tipo me cae muy mal"}'
```

## 9. Extension de navegador

### 9.1 Instalacion

1. Abrir Chrome o Edge.
2. Ir a `chrome://extensions/` o `edge://extensions/`.
3. Activar modo de desarrollador.
4. Seleccionar **Cargar extension sin empaquetar**.
5. Elegir la carpeta `extension/`.

### 9.2 Configuracion

En la pagina de opciones de la extension:

- Activar la API local.
- Verificar que la URL sea `http://127.0.0.1:8000`.
- Ajustar el umbral de deteccion si corresponde.

### 9.3 Prueba end-to-end

Con el backend activo:

```text
extension/test/demo.html
```

Verificar:

- Deteccion por modelo BETO.
- Deteccion por lexicon local de respaldo.
- Aplicacion de modos de censura.
- Explicacion por tokens cuando se solicita.

## 10. Pruebas automatizadas

Ejecutar suite general:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Verificar JavaScript de la extension:

```powershell
node --check extension/content.js
node --check extension/background.js
node --check extension/api.js
node --check extension/popup/popup.js
node --check extension/options/options.js
```

Verificar formato de cambios:

```powershell
git diff --check
```

## 11. Criterios de reproduccion satisfactoria

La reproduccion se considera satisfactoria cuando:

- Los datasets se cargan desde `data/raw/`.
- El corpus combinado, enriquecido y particionado se regenera.
- `MANIFEST.json` contiene hashes de los artefactos procesados.
- Los reportes de QC se generan sin errores criticos.
- Los modelos y predicciones se obtienen desde el notebook de Colab.
- Las tablas de evaluacion, bootstrap, McNemar, H3 y XAI existen en `reports/`.
- La API responde en `http://127.0.0.1:8000`.
- La extension se instala y consume el backend local.
- La suite de pruebas automatizadas pasa en el entorno local.
