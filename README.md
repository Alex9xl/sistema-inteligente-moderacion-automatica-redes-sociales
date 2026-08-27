# Sistema Inteligente de Moderacion Automatica en Redes Sociales

Proyecto de tesis para la deteccion automatica de discurso de odio en espanol mediante BETO ajustado, modelos multilingues de referencia y una extension de navegador.

Autores:

- Quiñonez Rivera Esteban
- Palomino Julian Alex Marcelo

Grado academico: Bachiller en Ingenieria de Software.

## Inicio rapido

### 1. Crear el entorno

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Obtener el modelo final con Git LFS

El modelo final usado por la API se versiona en el repositorio mediante Git LFS,
porque `model.safetensors` es un archivo grande. Instala Git LFS una sola vez en
tu equipo y descarga los artefactos al clonar el proyecto:

```powershell
git lfs install
git clone https://github.com/Alex9xl/sistema-inteligente-moderacion-automatica-redes-sociales.git
cd sistema-inteligente-moderacion-automatica-redes-sociales
git lfs pull
```

Si el repositorio ya estaba clonado antes de habilitar LFS, ejecuta solamente:

```powershell
git lfs pull
```

Antes de iniciar la API, la carpeta `models/beto_finetuned_final/` debe contener,
como mínimo, `config.json`, `model.safetensors`, `tokenizer.json`,
`tokenizer_config.json`, `special_tokens_map.json` y `vocab.txt`. No desactives
la descarga de LFS si quieres ejecutar la API localmente.

En CMD, para activar el entorno:

```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 3. Preparar datos

```powershell
make data
```

Si `make` no esta disponible, ejecutar los pasos detallados en `documentos_extras/GUIA_REPRODUCCION.md`.

### 4. Ejecutar pruebas

```powershell
make test
```

### 5. Levantar la API

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

La API queda disponible en:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

> Nota: usar este comando directo para levantar la API en Windows. El objetivo `make api` puede no funcionar segun la configuracion local de `make`, `PATH` o entorno virtual.

Si el arranque muestra un error sobre `config.json`, `model_type` o un modelo no
reconocido, verifica que Git LFS haya descargado el contenido real del modelo con
`git lfs pull` y que no solo exista `model_card.md`.

### 6. Entrenamiento y evaluacion en Colab

El entrenamiento, la evaluacion, H3 y XAI se reproducen con:

```text
notebooks/colab_entrenamiento_evaluacion_xai.ipynb
```

Es importante ejecutar tambien las 3 celdas extra destinadas a la Hipotesis 1. Esas celdas generan la comparacion entre BETO ajustado y BETO base sin fine-tuning, necesaria para sustentar H1 en la tesis.

### 7. Instalar la extension

1. Abrir Chrome o Edge.
2. Entrar a `chrome://extensions/` o `edge://extensions/`.
3. Activar el modo de desarrollador.
4. Seleccionar **Cargar extension sin empaquetar**.
5. Elegir la carpeta `extension/`.

## Estructura principal

| Ruta | Contenido |
|------|-----------|
| `src/data/` | Limpieza, unificacion, enriquecimiento, validacion y particionado del corpus. |
| `src/api/` | Backend FastAPI para inferencia y explicabilidad. |
| `src/xai/` | Modulo de explicabilidad basado en SHAP. |
| `scripts/` | Scripts auxiliares para reportes, manifiestos y ejecucion reproducible. |
| `notebooks/` | Notebooks de exploracion, entrenamiento, evaluacion y XAI. |
| `extension/` | Extension de navegador Manifest V3. |
| `data/processed/` | Corpus procesado, splits y manifiesto de artefactos. |
| `reports/` | Tablas, predicciones, figuras y resultados experimentales. |
| `models/` | Modelos entrenados y modelo final. |

## Documentacion

Para una introduccion rapida al proyecto (arquitectura, flujo completo, resultados de las hipotesis y glosario), empezar por `docs/README.md`.

| Documento | Proposito |
|-----------|-----------|
| `docs/README.md` | Indice de la documentacion corta y autocontenida (arquitectura, flujo, modelo, resultados, glosario). |
| `documentos_extras/INSTRUCCIONES_PROYECTO.md` | Especificacion tecnica y metodologica completa del proyecto. |
| `documentos_extras/PLAN_DESARROLLO.md` | Plan formal para construir el proyecto desde cero. |
| `documentos_extras/GUIA_REPRODUCCION.md` | Guia para reproducir datos, entrenamiento, evaluacion, API y extension. |
| `EXPERIMENTOS.md` | Bitacora cientifica de decisiones, corridas y resultados. |
| `data/processed/MANIFEST.json` | Versiones, hashes y trazabilidad de artefactos. |

## Licencia

El codigo del proyecto se distribuye bajo licencia MIT. Los datasets, modelos base y recursos externos conservan sus licencias academicas u originales respectivas.
