# Guía de Arquitectura

Cómo está organizado el sistema, qué responsabilidad tiene cada pieza y por qué se diseñó así. Para el detalle metodológico exhaustivo, ver `documentos_extras/INSTRUCCIONES_PROYECTO.md` (sección 3).

## Visión general: 3 capas con fronteras estrictas

El sistema se divide en 3 capas. Cada capa solo conoce el contrato (formato de entrada/salida) de la capa vecina, nunca su implementación interna. Esto permite construir, probar y hasta reemplazar cada capa por separado.

```text
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1: DATOS Y EXPERIMENTACIÓN (offline, no se ejecuta     │
│  en producción; corre una vez para producir el modelo)      │
│                                                               │
│  Datasets crudos → limpieza → unificación → enriquecimiento │
│  con lexicón LATAM → splits → entrenamiento (BETO, mBERT,    │
│  XLM-R) → evaluación estadística → modelo final empaquetado  │
└───────────────────────────┬───────────────────────────────────┘
                            ▼  (modelo final + tokenizer)
┌───────────────────────────┴───────────────────────────────────┐
│  CAPA 2: SERVICIO (online, siempre corriendo)                │
│                                                               │
│  Backend FastAPI: carga el modelo una sola vez y expone      │
│  /health, /predict, /explain, /metadata                       │
└───────────────────────────┬───────────────────────────────────┘
                            ▼  (HTTP/JSON, CORS restringido)
┌───────────────────────────┴───────────────────────────────────┐
│  CAPA 3: CLIENTE (online, en el navegador del usuario)        │
│                                                               │
│  Extensión Manifest V3: escanea el DOM, consulta la API,     │
│  aplica lexicón personal como respaldo, censura/resalta       │
└─────────────────────────────────────────────────────────────┘
```

Para el diagrama ASCII detallado con los 4 sub-bloques de datos, ver `documentos_extras/INSTRUCCIONES_PROYECTO.md` sección 3.2. Para el flujo paso a paso con nombres exactos de scripts y archivos, ver `docs/flujo_completo.md`.

## Componentes y responsabilidades

| Módulo | Ubicación | Responsabilidad |
|---|---|---|
| Datos | `src/data/` | Limpiar, unificar, enriquecer, validar y particionar el corpus. |
| Lexicón LATAM | `src/data/lexicon.py`, `data/lexicons/` | Detectar modismos regionales en un texto; exportar versión y hash para trazabilidad. |
| Modelado | `scripts/train_model.py`, notebook de Colab | Tokenizar, entrenar con `Trainer`, seleccionar el mejor checkpoint por F1, guardar el modelo. |
| Evaluación | `scripts/evaluate_model.py`, notebook de Colab | Calcular métricas, bootstrap, test de McNemar, análisis segmentado por modismos (H3). |
| XAI | `src/xai/shap_explainer.py` | Explicar predicciones individuales con SHAP (qué tokens influyeron y cuánto). |
| API | `src/api/` | Cargar el modelo final una sola vez, exponer endpoints REST, validar entradas, aplicar el umbral interno. |
| Extensión | `extension/` | Escanear el DOM, consumir la API, aplicar el lexicón personal como respaldo, censurar/resaltar según configuración del usuario. |

## Dependencias entre módulos

El grafo de dependencias es **acíclico**: ningún módulo depende de uno que esté "más arriba" en el flujo. Esto es lo que permite probar cada módulo de forma aislada.

```text
Lexicón LATAM ──► Módulo de Datos ──► Módulo de Modelado ──► Módulo de Evaluación / XAI ──► Backend API ──► Extensión
```

- El **Lexicón LATAM** no depende de nada; es un recurso fundacional.
- El **Módulo de Datos** depende del lexicón para poder marcar la columna `tiene_modismo`.
- El **Módulo de Modelado** consume el corpus ya particionado (train/val/test).
- **Evaluación** y **XAI** dependen del modelo entrenado.
- El **Backend** carga el modelo final y expone la explicabilidad de XAI.
- La **Extensión** solo conoce el contrato HTTP/JSON del backend; nunca accede directamente al modelo ni al corpus.

## Decisiones de diseño clave

Estas son las decisiones que más impactan la arquitectura y por qué se tomaron. Ver `documentos_extras/INSTRUCCIONES_PROYECTO.md` sección 3.6 para la tabla ampliada con alternativas descartadas.

### Backend desacoplado (FastAPI) en vez de correr el modelo en el navegador

BETO pesa cerca de 440 MB, lo cual es inviable de ejecutar directamente en el navegador (vía ONNX o TensorFlow.js) sin degradar fuertemente la experiencia. Separar el modelo en un backend permite mantenerlo completo, tipado con Pydantic, documentado automáticamente con OpenAPI/Swagger, y actualizable sin tocar la extensión.

### BETO `cased` en vez de `uncased`

El discurso de odio explota patrones de mayúsculas (gritos, énfasis, agresividad). La variante `uncased` normaliza todo a minúsculas y destruiría esa señal antes de que el modelo pueda aprenderla.

### Etiquetado binario (`hate` / `no_hate`) en vez de multiclase

Los dos datasets de origen (Spanish Hate Speech Superset y DETOXIS) usan esquemas de etiquetado distintos y no directamente comparables en granularidad. Unificar en binario permite combinarlos de forma consistente. Un análisis más fino por tipo de discurso de odio podría hacerse después, sobre el mismo corpus, sin rehacer el pipeline.

### Lexicón LATAM como variable observacional, no como input del modelo

El lexicón de modismos solo se usa para calcular la columna `tiene_modismo` y así poder segmentar la evaluación (Hipótesis 3: ¿el modelo rinde distinto en textos con modismos vs. sin ellos?). Deliberadamente **no** se concatena ni se inyecta como feature al modelo. Esto mantiene al modelo como una "caja negra" evaluable de forma justa: si el lexicón influyera directamente en la predicción, ya no se podría medir con honestidad si el modelo "aprendió" a reconocer modismos por sí mismo o si solo está copiando una regla explícita.

### Tres semillas de entrenamiento (42, 123, 2024) en vez de una sola

El fine-tuning de modelos Transformer tiene varianza intrínseca entre corridas (Mosbach et al., 2021): la misma configuración puede dar resultados algo distintos según la inicialización aleatoria. Entrenar 3 veces y reportar media ± desviación estándar da una medición más honesta que confiar en una única corrida que podría haber sido inusualmente buena o mala.

### Test de McNemar en vez de comparar solo el promedio de métricas

Comparar F1 promedio entre dos modelos no dice si la diferencia es estadísticamente significativa o producto del azar. McNemar es el test estándar para comparar dos clasificadores evaluados sobre el mismo conjunto de prueba, porque compara directamente los casos donde un modelo acierta y el otro falla.

### Manifest V3 "vanilla" (sin framework) en la extensión

Se evitó usar React/Vue para no introducir un paso de build adicional, reducir el peso de la extensión y facilitar que el jurado o cualquier evaluador externo pueda auditar el código fuente directamente, sin herramientas extra.

### Detección automática opt-in, no activada por defecto

Por privacidad: ningún texto de la página sale del navegador hacia la API sin que el usuario haya activado explícitamente la extensión.

## Riesgos y cómo se mitigan

| Riesgo | Mitigación |
|---|---|
| El backend se cae mientras la extensión está activa | La extensión detecta la falla y cae en modo degradado, usando solo el lexicón personal local. |
| Desfase entre la versión del modelo y lo que espera la extensión | El endpoint `/metadata` expone la versión activa para que el cliente pueda validarla. |
| Latencia alta del modelo corriendo en CPU | Cola de peticiones con concurrencia limitada y truncamiento de texto a 512 caracteres. |
| Cambios futuros en las políticas de Manifest V3 | Toda la lógica de red está centralizada en un único módulo (`extension/api.js`), fácil de ajustar. |
| Confundir el lexicón LATAM (científico) con el lexicón personal (producto) | Carpetas y nombres distintos; el lexicón personal vive solo en `chrome.storage.local`, nunca en `data/`. Ver `docs/glosario.md`. |
