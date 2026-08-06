# Glosario de Términos

Definiciones de los términos técnicos y académicos usados a lo largo del proyecto y de esta documentación.

## Modelos y NLP

| Término | Definición |
|---|---|
| **BETO** | Modelo BERT preentrenado exclusivamente en español por la Universidad de Chile (Cañete et al., 2020). Es el modelo principal del proyecto, en su variante `cased`. |
| **mBERT** | `bert-base-multilingual-cased`, versión de BERT preentrenada en 104 idiomas simultáneamente. Se usa como modelo de referencia (baseline). |
| **XLM-R** | `xlm-roberta-base`, modelo multilingüe basado en RoBERTa. También usado como baseline. |
| **Fine-tuning (ajuste fino)** | Proceso de continuar entrenando un modelo ya preentrenado sobre una tarea específica (aquí, clasificación binaria de discurso de odio), ajustando sus pesos internos. |
| **Tokenización** | Segmentación de un texto en unidades mínimas (tokens) que el modelo puede procesar numéricamente. |
| **Hate speech (discurso de odio)** | Discurso que ataca, degrada o incita violencia contra una persona o grupo por atributos protegidos (origen, género, orientación, etc.). En este proyecto se trata como clasificación binaria: `hate` / `no_hate`. |

## Modismos y lexicones (dos conceptos que NO deben confundirse)

| Término | Definición |
|---|---|
| **Modismo** | Expresión idiomática propia de una variante regional del idioma (por ejemplo, "pinche" en México o "boludo" en Argentina). |
| **Lexicón LATAM** | Recurso léxico de 383 modismos latinoamericanos usado como **instrumento científico observacional**: marca qué textos del corpus contienen modismos para poder segmentar la evaluación (Hipótesis 3). Nunca se inyecta como input al modelo. |
| **Lexicón personal** | Lista de palabras configurada por el propio usuario dentro de la extensión, usada como mecanismo de respaldo si la API no está disponible. Es parte del **producto**, vive solo en `chrome.storage.local` del navegador y nunca se envía al servidor. |

## Evaluación y estadística

| Término | Definición |
|---|---|
| **F1-score** | Media armónica entre Precision y Recall. Métrica principal de selección de modelo en este proyecto (sobre la clase `hate`). |
| **Precision** | De todo lo que el modelo marcó como `hate`, qué proporción realmente lo era. |
| **Recall** | De todo lo que realmente era `hate`, qué proporción el modelo logró detectar. |
| **Bootstrap** | Técnica de remuestreo con reposición usada para estimar intervalos de confianza de una métrica sin asumir una distribución teórica. |
| **McNemar** | Test estadístico usado para comparar dos clasificadores evaluados sobre el mismo conjunto de prueba, determinando si la diferencia entre ellos es significativa o producto del azar. |
| **SHAP (Shapley Additive exPlanations)** | Método de explicabilidad (XAI) que asigna a cada token de un texto un peso que indica cuánto contribuyó a la predicción final del modelo. |

## Extensión de navegador

| Término | Definición |
|---|---|
| **Manifest V3** | Especificación vigente de Google/Chromium para extensiones de navegador; define permisos, ciclo de vida y arquitectura de scripts. |
| **Service Worker** | Script de fondo de la extensión, sin acceso directo al DOM, que se activa por eventos (por ejemplo, recibir un mensaje o hacer una petición a la API). |
| **Content Script** | Script que se inyecta directamente en el contexto de la página web visitada; es el que puede leer y modificar el DOM. |
| **CORS (Cross-Origin Resource Sharing)** | Política de seguridad del navegador que restringe qué orígenes (dominios) pueden hacer peticiones a un servidor. La API la configura para aceptar únicamente peticiones desde la extensión y `localhost`. |

Para el glosario extendido (incluye referencias bibliográficas de cada término), ver `documentos_extras/INSTRUCCIONES_PROYECTO.md` sección 21.
