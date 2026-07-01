# Plan de Desarrollo del Proyecto

Este documento describe el plan formal para construir el proyecto desde cero. Esta pensado para una persona que aun no tiene el repositorio descargado y necesita conocer el orden de implementacion, los entregables esperados y los criterios de aceptacion de cada fase.

El documento no funciona como bitacora de avance. Los resultados concretos de corridas, decisiones experimentales y hashes de artefactos se registran en `EXPERIMENTOS.md` y `data/processed/MANIFEST.json`.

## 1. Proposito del proyecto

El proyecto implementa un sistema inteligente de moderacion automatica de discurso de odio en espanol. Su nucleo experimental consiste en ajustar BETO sobre un corpus enriquecido con modismos latinoamericanos, compararlo contra modelos de referencia y exponer el modelo final mediante una API REST y una extension de navegador.

Hipotesis de investigacion:

| ID | Hipotesis |
|----|-----------|
| H1 | BETO ajustado mejora frente a BETO base sin ajuste fino en la misma tarea. |
| H2 | BETO ajustado iguala o supera a modelos multilingues de referencia como mBERT y XLM-R. |
| H3 | BETO ajustado obtiene mejor desempeno relativo en textos con modismos latinoamericanos que en textos sin ellos. |

## 2. Stack tecnico

| Componente | Tecnologia |
|------------|------------|
| Lenguaje principal | Python 3.10+ |
| Procesamiento de datos | pandas, numpy, scikit-learn |
| Modelos NLP | Hugging Face Transformers |
| Modelo principal | `dccuchile/bert-base-spanish-wwm-cased` |
| Baselines | BETO base, mBERT, XLM-R |
| Evaluacion | scikit-learn, bootstrap, McNemar |
| XAI | SHAP |
| Backend | FastAPI, Uvicorn, Pydantic |
| Extension | Chrome Extension Manifest V3 |
| Entorno GPU | Google Colab o equivalente |

## 3. Estructura objetivo del repositorio

```text
Tesis_Proyecto/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── lexicons/
│   └── reports_qc/
├── documentos_extras/
├── extension/
├── models/
├── notebooks/
├── reports/
│   ├── figures/
│   ├── predictions/
│   └── tables/
├── scripts/
├── src/
│   ├── api/
│   ├── data/
│   └── xai/
├── tests/
├── EXPERIMENTOS.md
├── README.md
├── requirements.txt
└── Makefile
```

## 4. Fase 0: Preparacion inicial

### Objetivo

Crear el entorno minimo de trabajo y dejar el repositorio listo para ejecutar pipelines de datos, entrenamiento, evaluacion y servicio.

### Actividades

1. Clonar o inicializar el repositorio.
2. Crear entorno virtual.
3. Instalar dependencias.
4. Verificar acceso a Python, Git y Jupyter.
5. Crear carpetas principales si no existen.

### Comandos base

```powershell
python --version
git --version

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Entregables

| Entregable | Criterio de aceptacion |
|------------|------------------------|
| Entorno virtual | Dependencias instaladas sin error. |
| Estructura de carpetas | Carpetas principales disponibles. |
| `requirements.txt` | Dependencias necesarias declaradas. |
| `Makefile` | Comandos frecuentes documentados. |

## 5. Fase 1: Gestion y preparacion de datos

### Objetivo

Construir un corpus unificado, limpio, enriquecido y particionado para la deteccion binaria de discurso de odio.

### Fuentes previstas

| Fuente | Uso |
|--------|-----|
| Spanish Hate Speech Superset, Tonneau et al. 2024 | Base principal del corpus. |
| DETOXIS, IberLEF 2021 | Fuente adicional para comentarios en espanol. |

### 5.1 Verificacion de fuentes

Actividades:

1. Confirmar existencia de archivos en `data/raw/`.
2. Inspeccionar columnas, nulos, tamanos y distribucion de etiquetas.
3. Registrar procedencia y condiciones de uso.

Scripts previstos:

```text
data/raw/analisis_dataset/verificar_corpus.py
data/raw/analisis_dataset/verificar_datasets_detoxis.py
```

### 5.2 Exploracion inicial

Crear un script reproducible para generar metricas y figuras preliminares.

Archivo previsto:

```text
scripts/exploracion_inicial.py
```

Salidas:

| Archivo | Contenido |
|---------|-----------|
| `data/reports_qc/exploracion_inicial.md` | Reporte de exploracion. |
| `data/reports_qc/exploracion_inicial.json` | Metricas estructuradas. |
| `data/reports_qc/figuras/*.png` | Figuras de distribucion y longitud. |

### 5.3 Limpieza y normalizacion

Implementar funciones de limpieza en:

```text
src/data/clean.py
```

Requisitos:

- Reparar problemas de encoding cuando corresponda.
- Decodificar entidades HTML.
- Normalizar URLs y menciones.
- Preservar informacion util para el modelo.
- Mantener mayusculas cuando el modelo sea cased.
- Aplicar normalizacion solo a las fuentes que lo requieran.

### 5.4 Unificacion

Implementar:

```text
src/data/unify.py
```

Esquema canonico minimo:

| Columna | Descripcion |
|---------|-------------|
| `id` | Identificador unico de instancia. |
| `texto` | Texto normalizado o preprocesado. |
| `etiqueta` | Etiqueta binaria: 0 no hate, 1 hate. |
| `dataset` | Dataset de origen. |
| `source` | Plataforma o fuente textual. |
| `pais` | Pais o valor `unknown`. |

Salida:

```text
data/interim/corpus_combinado.parquet
```

### 5.5 Lexicon LATAM

Construir un lexicon de modismos latinoamericanos para marcar la variable observacional `tiene_modismo`.

Archivos:

```text
data/lexicons/modismos_latam_v1.csv
src/data/lexicon.py
```

Reglas metodologicas:

- El lexicon no se usa como feature de entrenamiento.
- Su funcion es segmentar el corpus para analisis de H3.
- Cada termino debe tener fuente, pais o region, tipo y notas cuando corresponda.

### 5.6 Enriquecimiento

Implementar:

```text
src/data/enrich.py
```

Columnas derivadas:

| Columna | Uso |
|---------|-----|
| `tiene_modismo` | Segmentacion para H3. |
| `n_tokens_aprox` | Analisis de longitud y control de calidad. |

Salida:

```text
data/processed/corpus_v1_enriquecido.parquet
```

### 5.7 Control de calidad

Implementar:

```text
src/data/qc.py
scripts/generar_reporte_qc_final.py
```

Validaciones:

- IDs unicos.
- Textos no nulos.
- Etiquetas en `{0, 1}`.
- Proporcion de clases documentada.
- Cobertura de `tiene_modismo`.
- Duplicados exactos y normalizados.
- Longitudes de texto.

### 5.8 Particionado

Implementar:

```text
src/data/split.py
```

Requisitos:

- Eliminar duplicados antes del split final.
- Usar particion 70/15/15.
- Estratificar por etiqueta.
- Verificar ausencia de leakage entre train, validation y test.
- Fijar semilla reproducible.

Salidas:

```text
data/processed/train.parquet
data/processed/val.parquet
data/processed/test.parquet
```

### 5.9 Manifiesto

Implementar:

```text
scripts/crear_manifest.py
```

El manifiesto debe incluir:

- Version del corpus.
- Hash SHA-256 de artefactos principales.
- Fuentes usadas.
- Version del lexicon.
- Fecha de generacion.
- Commit del repositorio cuando este disponible.

Salida:

```text
data/processed/MANIFEST.json
```

## 6. Fase 2: Entrenamiento de modelos

### Objetivo

Entrenar BETO ajustado y modelos de referencia bajo un protocolo comparable.

### Modelos

| Modelo | Identificador |
|--------|---------------|
| BETO ajustado | `dccuchile/bert-base-spanish-wwm-cased` |
| BETO base | Mismo modelo sin fine-tuning para baseline de H1. |
| mBERT | `bert-base-multilingual-cased` |
| XLM-R | `xlm-roberta-base` |

### Protocolo

- Usar los mismos splits para todos los modelos.
- Entrenar con semillas fijas, por ejemplo `42`, `123` y `2024`.
- Guardar logs, metricas y checkpoints.
- Seleccionar el mejor BETO por desempeno en validacion.
- Copiar el modelo seleccionado a `models/beto_finetuned_final/`.

### Scripts y notebooks

```text
scripts/train_model.py
notebooks/colab_entrenamiento_evaluacion_xai.ipynb
```

El notebook de Colab debe incluir y ejecutar 3 celdas adicionales para la Hipotesis 1. Estas celdas evaluan BETO base sin fine-tuning y generan la comparacion directa contra BETO ajustado. Sin esos artefactos, H1 queda incompleta metodologicamente.

### Entregables

| Entregable | Criterio de aceptacion |
|------------|------------------------|
| Modelos por semilla | Carpetas en `models/` con pesos y tokenizador. |
| Modelo final | `models/beto_finetuned_final/`. |
| Artefactos de H1 | Predicciones y metricas de BETO base frente a BETO ajustado. |
| Logs de entrenamiento | Hiperparametros, semilla y metrica de validacion. |
| Model card | Descripcion del modelo final y limitaciones. |

## 7. Fase 3: Evaluacion experimental

### Objetivo

Comparar BETO ajustado contra sus baselines usando el test set congelado.

### Actividades

1. Cargar modelos entrenados.
2. Generar predicciones sobre test.
3. Calcular Precision, Recall, F1, Accuracy y ROC-AUC.
4. Generar matrices de confusion.
5. Calcular intervalos de confianza por bootstrap.
6. Aplicar McNemar para comparaciones pareadas.

### Archivos previstos

```text
scripts/evaluate_model.py
reports/predictions/
reports/tables/
reports/figures/
```

### Entregables

| Archivo | Proposito |
|---------|-----------|
| `reports/tables/comparativa_global.csv` | Comparacion principal de modelos. |
| `reports/tables/bootstrap_ic.csv` | Intervalos de confianza. |
| `reports/tables/mcnemar_results.csv` | Pruebas pareadas. |
| `reports/predictions/*.csv` | Predicciones por modelo. |

## 8. Fase 4: Analisis de modismos

### Objetivo

Evaluar la H3 mediante comparacion del desempeno en subconjuntos con y sin modismos latinoamericanos.

### Actividades

1. Dividir test por `tiene_modismo`.
2. Calcular metricas para cada subconjunto.
3. Medir diferencia de desempeno.
4. Aplicar prueba estadistica o bootstrap segun corresponda.
5. Interpretar resultados con cautela metodologica.

### Entregables

```text
reports/tables/h3_idiom_analysis/
```

El analisis debe distinguir entre evidencia favorable, evidencia parcial y ausencia de soporte para H3.

## 9. Fase 5: Inteligencia Artificial Explicable

### Objetivo

Incorporar explicabilidad sobre el modelo final para apoyar el analisis cualitativo y el endpoint `/explain`.

### Actividades

1. Seleccionar instancias correctas e incorrectas.
2. Generar explicaciones SHAP.
3. Analizar tokens con mayor contribucion positiva y negativa.
4. Relacionar explicaciones con modismos, errores y limites del modelo.
5. Implementar un modulo local reutilizable por la API.

### Archivos

```text
src/xai/shap_explainer.py
reports/tables/xai_analysis/
notebooks/colab_entrenamiento_evaluacion_xai.ipynb
```

## 10. Fase 6: Backend FastAPI

### Objetivo

Exponer el modelo final mediante un servicio local con endpoints de salud, metadatos, prediccion y explicacion.

### Estructura

```text
src/api/
├── config.py
├── schemas.py
└── main.py
```

### Endpoints

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/health` | GET | Estado del servicio y carga del modelo. |
| `/metadata` | GET | Informacion del modelo y configuracion. |
| `/predict` | POST | Prediccion binaria con probabilidad. |
| `/explain` | POST | Prediccion y explicacion por tokens. |

### Requisitos

- Cargar el modelo final desde `models/beto_finetuned_final/`.
- Permitir modo degradado si el modelo no esta disponible.
- Validar entradas con Pydantic.
- Configurar CORS para extension local.
- Mantener umbral configurable.
- Cargar SHAP de manera diferida para no ralentizar el arranque.

Comando recomendado para levantar la API en Windows:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

El plan puede conservar `make` para otras tareas auxiliares, pero la documentacion operativa de la API debe priorizar el comando directo anterior porque resuelve correctamente el interprete del entorno virtual.

## 11. Fase 7: Extension de navegador

### Objetivo

Implementar una extension Manifest V3 que detecte contenido potencialmente ofensivo en paginas web y consuma el backend local.

### Componentes

| Archivo | Funcion |
|---------|---------|
| `extension/manifest.json` | Configuracion Manifest V3. |
| `extension/background.js` | Service worker y comunicacion con API. |
| `extension/content.js` | Escaneo del DOM y marcado visual. |
| `extension/api.js` | Cliente HTTP hacia FastAPI. |
| `extension/lexicon.js` | Lexicon local de respaldo. |
| `extension/styles.css` | Estilos de resaltado y censura. |
| `extension/popup/` | Interfaz rapida de usuario. |
| `extension/options/` | Configuracion avanzada y lexicon personal. |

### Requisitos funcionales

- Activar o desactivar deteccion.
- Enviar fragmentos visibles al backend local cuando la API este habilitada.
- Aplicar deteccion por BETO como mecanismo principal.
- Usar lexicon local como respaldo.
- Soportar modos de censura: resaltar, difuminar, asteriscos y ocultar.
- Permitir lexicon personal persistido en `chrome.storage.local`.
- Mostrar estado de conexion con la API.
- Solicitar explicaciones cuando el usuario lo requiera.

## 12. Fase 8: Cierre cientifico y reproducibilidad

### Objetivo

Consolidar evidencias, artefactos y documentacion para que el proyecto sea defendible y reproducible.

### Actividades

1. Completar `EXPERIMENTOS.md`.
2. Actualizar `data/processed/MANIFEST.json`.
3. Crear o actualizar `models/beto_finetuned_final/model_card.md`.
4. Revisar tablas y figuras finales.
5. Ejecutar tests de Python y validaciones estaticas de JavaScript.
6. Verificar `git diff --check`.
7. Preparar commit y tag de version final.

### Verificaciones sugeridas

```powershell
.\venv\Scripts\python.exe -m pytest

node --check extension/content.js
node --check extension/background.js
node --check extension/api.js
node --check extension/popup/popup.js
node --check extension/options/options.js

git diff --check
```

## 13. Cronograma de referencia

| Fase | Duracion estimada | Entregable principal |
|------|-------------------|----------------------|
| 0 | 1 dia | Entorno y estructura inicial. |
| 1 | 1 a 2 semanas | Corpus procesado y validado. |
| 2 | 2 semanas | Modelos entrenados. |
| 3 | 1 semana | Evaluacion comparativa. |
| 4 | 3 a 5 dias | Analisis H3. |
| 5 | 3 a 5 dias | XAI y analisis cualitativo. |
| 6 | 1 semana | Backend funcional. |
| 7 | 1 semana | Extension funcional. |
| 8 | 1 semana | Cierre, documentacion y version final. |

## 14. Criterios generales de aceptacion

| Area | Criterio |
|------|----------|
| Datos | Corpus unificado, enriquecido, validado y sin leakage entre splits. |
| Modelos | BETO, mBERT y XLM-R entrenados bajo protocolo comparable. |
| Evaluacion | Metricas, bootstrap y McNemar generados sobre test congelado. |
| H3 | Segmentacion por modismos documentada y evaluada. |
| XAI | Explicaciones disponibles para analisis y API. |
| Backend | API local con `/health`, `/metadata`, `/predict` y `/explain`. |
| Extension | Manifest V3 instalable y conectada al backend local. |
| Reproducibilidad | `EXPERIMENTOS.md`, `MANIFEST.json`, reportes y pruebas actualizados. |

## 15. Documentos relacionados

| Documento | Funcion |
|-----------|---------|
| `INSTRUCCIONES_PROYECTO.md` | Documento maestro tecnico y metodologico. |
| `GUIA_REPRODUCCION.md` | Procedimiento para comprobar el proyecto ya implementado. |
| `../README.md` | Arranque rapido del repositorio. |
| `../EXPERIMENTOS.md` | Bitacora cientifica de ejecuciones y decisiones. |
| `../data/processed/MANIFEST.json` | Trazabilidad de artefactos. |
