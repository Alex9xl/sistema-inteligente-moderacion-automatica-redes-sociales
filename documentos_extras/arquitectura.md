# Arquitectura del Sistema

## 1. Diseño Arquitectónico

### 1.1 Visión General

El sistema "Moderación Automática de Discurso de Odio" se organiza en **3 capas funcionales desacopladas**:

1. **Capa de Datos y Experimentación (offline)**: Pipelines de preparación, entrenamiento y evaluación
2. **Capa de Servicio (online)**: Backend FastAPI de inferencia
3. **Capa de Cliente (online)**: Extensión de navegador Manifest V3

Cada capa es independiente y se comunica mediante interfaces bien definidas (HTTP/JSON).

### 1.2 Modelo Arquitectónico

**Patrón: Arquitectura en Capas + Microservicios**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  CAPA DATOS Y EXPERIMENTACIÓN (Offline)                │
│                      Machine Learning Pipeline                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Datasets → Limpieza → Unificación → Enriquecimiento → Partición       │
│                            ↓                                            │
│           Entrenamiento (BETO, mBERT, XLM-R)                           │
│                            ↓                                            │
│           Evaluación y Selección de Mejor Modelo                       │
│                            ↓                                            │
│         Modelo Final Empaquetado (BETO Ajustado)                       │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │
                   (Modelo serializado + Tokenizer)
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  CAPA SERVICIO (Online)                                │
│                      Backend REST FastAPI                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐              │
│  │ /health  │  │ /predict │  │ /explain │  │ /metadata  │              │
│  │ Liveness │  │ Inference│  │   XAI    │  │  Versión   │              │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘              │
│         [Carga única de modelo en memoria]                              │
│         [OpenAPI / Swagger Doc]                                         │
│         [CORS restringido a localhost + extensión]                      │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ HTTP/JSON
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  CAPA CLIENTE (Online)                                 │
│              Extensión de Navegador (Manifest V3)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐             │
│  │ Content Script         Service Worker                  │             │
│  │ - DOM scanning         - Cola de inferencia            │             │
│  │ - Text segmentation    - Fetch a /predict             │             │
│  │ - Highlighting         - Cache resultados             │             │
│  └────────────────────────────────────────────────────────┘             │
│  ┌────────────────────────────────────────────────────────┐             │
│  │ Popup UI               Options Page                    │             │
│  │ - Toggle detección     - Gestión lexicón personal     │             │
│  │ - Ajuste umbral        - Importar/exportar palabras    │             │
│  │ - Estado API           - Sincronizar settings         │             │
│  └────────────────────────────────────────────────────────┘             │
│  ┌────────────────────────────────────────────────────────┐             │
│  │ Local Storage (chrome.storage.local)                   │             │
│  │ - Lexicón personal del usuario (NUNCA al servidor)    │             │
│  │ - Configuración (umbral, idioma)                       │             │
│  └────────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagramas UML

### 2.1 Diagrama de Casos de Uso

```
                              ┌──────────────┐
                              │   Usuario    │
                              └──────────────┘
                                     │
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
            │ Activar Detección│ │ Ajustar Umbral   │ │Gestionar Lexicón │
            └──────────┬───────┘ └──────────┬───────┘ └──────────┬───────┘
                       │                    │                    │
                       ▼                    ▼                    ▼
            ┌──────────────────────────────────────────────────────────┐
            │           Extensión de Navegador                        │
            │         (Manifest V3 - Cliente)                         │
            └──────────────────┬─────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌──────────┐
        │Escanear DOM│  │Segmentar   │  │Resaltar  │
        │            │  │Texto       │  │Resultados│
        └────────────┘  └────────────┘  └──────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  Backend FastAPI     │
                    │  (Predicción + XAI)  │
                    └──────────────────────┘


        ┌──────────────────────────────────┐
        │    Científico / Investigador     │
        └──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 ┌─────────────┐ ┌────────────┐ ┌──────────────┐
 │ Descargador │ │ Limpiar    │ │ Entrenar     │
 │ Datasets    │ │ Corpus     │ │ Modelos      │
 └─────────────┘ └────────────┘ └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
            ┌──────────────────────┐
            │ Evaluar Resultados   │
            │ (Métricas + XAI)     │
            └──────────────────────┘
```

### 2.2 Diagrama de Clases (Modelos de Datos)

```
┌────────────────────────────────────────┐
│            Documento (Corpus)          │
├────────────────────────────────────────┤
│ - id: str (PRIMARY KEY)                │
│ - texto: str                           │
│ - etiqueta: int (0 o 1)                │
│ - dataset_origen: str (FK)             │
│ - tiene_modismo: bool                  │
│ - n_tokens: int                        │
│ - timestamp_creacion: datetime         │
├────────────────────────────────────────┤
│ + normalizar_texto()                   │
│ + calcular_estadisticas()              │
│ + detectar_modismo()                   │
└────────────────────────────────────────┘
                     △
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────┴──────┐ ┌──┴──────────┐ ┌┴───────────────┐
│ Documento    │ │ Documento   │ │ Documento      │
│ HatEval      │ │ DETOXIS     │ │ HaterNet       │
├──────────────┤ ├─────────────┤ ├────────────────┤
│ - target     │ │ - toxicity  │ │ - (heredado)   │
│ - ag (aggr.) │ │ - tox_level │ │                │
│ - tr (target)│ │ - 20 annots │ │                │
└──────────────┘ └─────────────┘ └────────────────┘

┌────────────────────────────────────────┐
│          Dataset (Metadatos)           │
├────────────────────────────────────────┤
│ - dataset_id: str (PRIMARY KEY)        │
│ - nombre: str                          │
│ - url_fuente: str                      │
│ - fecha_descarga: date                 │
│ - n_ejemplos: int                      │
│ - proporcion_hate: float               │
│ - idioma: str                          │
│ - plataforma: str                      │
├────────────────────────────────────────┤
│ + validar_integridad()                 │
│ + calcular_estadisticas()              │
└────────────────────────────────────────┘
                     △
                     │ 1:N
┌────────────────────┴────────────────────┐
│         Documento (Corpus) ──────────────┘

┌────────────────────────────────────────┐
│           Modelo Entrenado             │
├────────────────────────────────────────┤
│ - modelo_id: str (PRIMARY KEY)         │
│ - nombre: str                          │
│ - base_model: str (BERT, mBERT, etc)  │
│ - seed: int                            │
│ - f1_validacion: float                 │
│ - f1_test: float                       │
│ - ruta_archivo: str                    │
│ - fecha_entrenamiento: datetime        │
├────────────────────────────────────────┤
│ + cargar()                             │
│ + predecir(texto)                      │
│ + explicar(texto) → XAI                │
│ + evaluar(test_set)                    │
└────────────────────────────────────────┘
                     △
                     │ 1:N
┌────────────────────┴────────────────────┐
│    Documento (Corpus) ──────────────────┘

┌────────────────────────────────────────┐
│          Modismo LATAM                 │
├────────────────────────────────────────┤
│ - modismo_id: str (PRIMARY KEY)        │
│ - termino: str                         │
│ - variantes: str[] (semicolon-sep)    │
│ - pais: str (CL, MX, CO, VE, etc)    │
│ - tipo: str (insulto, coloquial, etc) │
│ - fuente: str                          │
│ - notas: str                           │
│ - fecha_inclusion: date                │
├────────────────────────────────────────┤
│ + buscar_en_texto(texto)               │
│ + validar_fuente()                     │
└────────────────────────────────────────┘
                     △
                     │ M:N
                     │
        ┌────────────┴────────────┐
        │                         │
        │  Documento (Corpus)     │
        └─────────────────────────┘
        (tiene_modismo: bool)

┌────────────────────────────────────────┐
│       Predicción (Inferencia)          │
├────────────────────────────────────────┤
│ - prediccion_id: str (PRIMARY KEY)     │
│ - modelo_id: str (FK)                  │
│ - texto_input: str                     │
│ - etiqueta_predicha: int               │
│ - probabilidad: float                  │
│ - timestamp: datetime                  │
│ - es_correcto: bool (si hay gold)     │
├────────────────────────────────────────┤
│ + validar_umbral(threshold)            │
│ + calcular_confianza()                 │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│          Explicacion (XAI)             │
├────────────────────────────────────────┤
│ - explicacion_id: str (PRIMARY KEY)    │
│ - prediccion_id: str (FK)              │
│ - tokens: str[]                        │
│ - pesos_shap: float[]                  │
│ - timestamp: datetime                  │
├────────────────────────────────────────┤
│ + obtener_top_tokens(k)                │
│ + visualizar_importancia()             │
└────────────────────────────────────────┘
```

### 2.3 Diagrama de Secuencia - Flujo de Predicción

```
Usuario          Extensión          Backend          Modelo
  │                  │                  │                │
  │─ Activar        │                  │                │
  │  Detección ────→│                  │                │
  │                 │                  │                │
  │             (Escanear DOM)         │                │
  │                 │                  │                │
  │                 │─ Segmentar      │                │
  │                 │  Texto           │                │
  │                 │                  │                │
  │                 │─ POST /predict  │                │
  │                 │  {texto}────────→│                │
  │                 │                  │                │
  │                 │                  │─ Tokenizar   │
  │                 │                  │  Texto        │
  │                 │                  │                │
  │                 │                  │─ Forward Pass─→│
  │                 │                  │                │
  │                 │                  │←─ Logits ─────│
  │                 │                  │                │
  │                 │                  │─ Softmax      │
  │                 │                  │- Umbral       │
  │                 │                  │                │
  │                 │  {etiqueta,      │                │
  │                 │   probabilidad}  │                │
  │                 │←─────────────────│                │
  │                 │                  │                │
  │  (Resaltar)    │                  │                │
  │←────────────────│                  │                │
  │                 │                  │                │
  │─ Solicitar     │                  │                │
  │  Explicación ──→│                  │                │
  │                 │─ POST /explain  │                │
  │                 │  {texto}────────→│                │
  │                 │                  │                │
  │                 │                  │─ SHAP Extract─→│
  │                 │                  │                │
  │                 │                  │←─ Pesos ─────│
  │                 │  {tokens,        │                │
  │                 │   pesos}         │                │
  │                 │←─────────────────│                │
  │                 │                  │                │
  │  (Mostrar)     │                  │                │
  │←────────────────│  en tooltip/     │                │
  │                 │  panel lateral   │                │
  │                 │                  │                │
```

### 2.4 Diagrama de Secuencia - Flujo de Entrenamiento

```
Investigador     Pipelines       Datasets        Trainer         Modelo
     │               │               │               │               │
     │─ Ejecutar    │               │               │               │
     │  paso 1.x ──→│               │               │               │
     │              │               │               │               │
     │              │─ Descargar ──→│               │               │
     │              │               │               │               │
     │              │←─ Datos ──────│               │               │
     │              │               │               │               │
     │              │─ Limpiar      │               │               │
     │              │  Corpus       │               │               │
     │              │               │               │               │
     │              │─ Unificar     │               │               │
     │              │  Etiquetas    │               │               │
     │              │               │               │               │
     │              │─ Enriquecer   │               │               │
     │              │  (modismos)   │               │               │
     │              │               │               │               │
     │              │─ Particionar ─│               │               │
     │              │  train/val/   │               │               │
     │              │  test         │               │               │
     │              │               │               │               │
     │              │─ Entrenar ───────────────────→│               │
     │              │  (3 semillas)                 │               │
     │              │                               │               │
     │              │                               │─ Forward ────→│
     │              │                               │  Backward     │
     │              │                               │  Optimize     │
     │              │                               │               │
     │              │                               │  (Epoch N)    │
     │              │                               │               │
     │              │                               │- Early Stop   │
     │              │                               │  si val F1 ↓  │
     │              │                               │               │
     │              │                      Checkpoints             │
     │              │←──────────────────────────────│               │
     │              │ (mejor modelo por semilla)    │               │
     │              │                               │               │
     │              │─ Evaluar en test             │               │
     │              │  (Precision, Recall, F1)     │               │
     │              │                               │               │
     │              │─ Comparar vs baselines       │               │
     │              │  (McNemar test)              │               │
     │              │                               │               │
     │              │─ XAI (SHAP)                 │               │
     │              │                               │               │
     │              │─ Generar reportes            │               │
     │              │                               │               │
     │  Resultados ←│                               │               │
     │←─────────────│                               │               │
     │              │                               │               │
```

### 2.5 Diagrama de Secuencia - Flujo de Inicialización

```
Sistema           Capa Datos      Backend         Extensión      Storage Local
   │                  │              │                │               │
   │ (Paso 1)        │              │                │               │
   │ Descargadores ──│─ Verificar ──→│                │               │
   │ de Datos        │  Datasets     │                │               │
   │                 │              │                │               │
   │ (Paso 2)        │              │                │               │
   │ Entrenar ───────│─ Construir ──→│                │               │
   │ BETO, mBERT,    │  Corpus       │                │               │
   │ XLM-R           │              │                │               │
   │                 │              │                │               │
   │ (Paso 3)        │              │                │               │
   │ Evaluar ────────│─ Comparar ───→│                │               │
   │                 │  Modelos      │                │               │
   │                 │              │                │               │
   │ (Paso 5)        │              │                │               │
   │ Empaquetar ─────│─ Serializar ──│                │               │
   │ Modelo Final    │  Modelo       │                │               │
   │                 │              │                │               │
   │                 │              │─ Cargar ──────→│                │
   │                 │              │ Modelo en      │                │
   │                 │              │ memoria        │                │
   │                 │              │                │                │
   │                 │              │              (Inicialización) │
   │                 │              │              Manifestó        │
   │                 │              │              Permisos          │
   │                 │              │                │                │
   │                 │              │                │─ Cargar ─────→│
   │                 │              │                │ Lexicón        │
   │                 │              │                │ Personal       │
   │                 │              │                │                │
   │ (Ready!)        │              │                │                │
   │←─ Sistema Listo─│─────────────→│─────────────────│                │
   │                 │              │                │                │
```

---

## 3. Diagrama Entidad-Relación (DER)

### 3.1 Esquema Conceptual (sin SQL)

```
                   ┌─────────────┐
                   │   Usuario   │
                   └──────┬──────┘
                          │ 1:N
                          │
                  ┌───────┴─────────┐
                  │                 │
        ┌─────────┴────────┐  ┌────┴──────────────┐
        │                  │  │                   │
┌───────▼──────┐  ┌────────▼──┐  ┌──────────────┬─▼─┐
│Configuración │  │  Búsqueda  │  │ Lexicón      │   │
│  del Usuario │  │   Historial│  │  Personal    │   │
│              │  │            │  │              │   │
│ - umbral     │  │ - texto    │  │ - termino    │   │
│ - idioma     │  │ - resultado│  │ - categoria  │   │
│ - preferencias  │ - timestamp│  │ - activo     │   │
└──────────────┘  └────────────┘  └──────────────┘   │
                                                     │
                    (chrome.storage.local)           │
                                                     │


┌─────────────────────────────────────────────────┐
│              CORPUS (Data Layer)                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────┐          │
│  │  Documento                       │          │
│  ├──────────────────────────────────┤          │
│  │ documento_id (PK)                │          │
│  │ dataset_id (FK)                  │          │
│  │ texto                            │          │
│  │ etiqueta (0 o 1)                 │          │
│  │ tiene_modismo (bool)             │          │
│  │ modismo_ids (array FK)           │          │
│  │ n_tokens                         │          │
│  │ partition (train/val/test)       │          │
│  └──────────────────────────────────┘          │
│         △              △              △         │
│         │              │              │         │
│    1:N  │         1:N  │         1:N  │         │
│         │              │              │         │
│  ┌──────┴──┐  ┌───────┴──┐  ┌────────┴─┐     │
│  │HatEval  │  │ DETOXIS  │  │ HaterNet │     │
│  │         │  │          │  │          │     │
│  │- HS     │  │- toxicity│  │(heredado)│     │
│  │- TR     │  │- tox_lvl │  │          │     │
│  │- AG     │  │- 20 annot│  │          │     │
│  └─────────┘  └──────────┘  └──────────┘     │
│                                               │
│  ┌──────────────────────────────────┐        │
│  │ Dataset (Metadatos)              │        │
│  ├──────────────────────────────────┤        │
│  │ dataset_id (PK)                  │        │
│  │ nombre                           │        │
│  │ url_fuente                       │        │
│  │ n_ejemplos                       │        │
│  │ proporcion_hate                  │        │
│  │ fecha_descarga                   │        │
│  └──────────────────────────────────┘        │
│         △                                     │
│         │ 1:N                                 │
│         └─────────────────────────────────────┘
│              (Documento → Dataset)
│
│  ┌──────────────────────────────────┐        │
│  │ Modismo LATAM                    │        │
│  ├──────────────────────────────────┤        │
│  │ modismo_id (PK)                  │        │
│  │ termino                          │        │
│  │ variantes                        │        │
│  │ pais                             │        │
│  │ tipo                             │        │
│  │ fuente                           │        │
│  │ fecha_inclusion                  │        │
│  └──────────────────────────────────┘        │
│         △                                     │
│         │ M:N                                 │
│         └─────────────────────────────────────┘
│              (Documento ↔ Modismo)
│
└─────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────┐
│          MODELOS Y EVALUACIÓN (ML Layer)        │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────┐          │
│  │ Modelo Entrenado                 │          │
│  ├──────────────────────────────────┤          │
│  │ modelo_id (PK)                   │          │
│  │ nombre                           │          │
│  │ base_model (BETO/mBERT/XLM-R)   │          │
│  │ seed                             │          │
│  │ f1_val, precision, recall        │          │
│  │ ruta_archivo                     │          │
│  │ fecha_entrenamiento              │          │
│  └──────────────────────────────────┘          │
│         △              △              △         │
│         │ 1:N          │ 1:N          │ 1:N     │
│         │              │              │         │
│  ┌──────┴──┐  ┌───────┴──┐  ┌────────┴─┐     │
│  │ BETO    │  │ mBERT    │  │  XLM-R   │     │
│  │ seed=42 │  │seed=42..│  │ seed=42..│     │
│  │seed=123 │  │         │  │          │     │
│  │seed=2024│  │         │  │          │     │
│  └─────────┘  └─────────┘  └──────────┘     │
│                                               │
│  ┌──────────────────────────────────┐        │
│  │ Predicción (Inferencia)          │        │
│  ├──────────────────────────────────┤        │
│  │ prediccion_id (PK)               │        │
│  │ modelo_id (FK)                   │        │
│  │ texto_input                      │        │
│  │ etiqueta_predicha                │        │
│  │ probabilidad                     │        │
│  │ timestamp                        │        │
│  │ es_correcto (si hay gold)        │        │
│  └──────────────────────────────────┘        │
│         △                                     │
│         │ 1:N                                 │
│         └─────────────────────────────────────┘
│              (Modelo → Predicción)
│
│  ┌──────────────────────────────────┐        │
│  │ Explicación (XAI / SHAP)         │        │
│  ├──────────────────────────────────┤        │
│  │ explicacion_id (PK)              │        │
│  │ prediccion_id (FK)               │        │
│  │ tokens                           │        │
│  │ pesos_shap                       │        │
│  │ timestamp                        │        │
│  └──────────────────────────────────┘        │
│         △                                     │
│         │ 1:1                                 │
│         └─────────────────────────────────────┘
│              (Predicción → Explicación)
│
└─────────────────────────────────────────────────┘
```

### 3.2 Esquema SQL (Normalización)

```sql
-- Tabla: Dataset
CREATE TABLE datasets (
    dataset_id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    url_fuente TEXT,
    fecha_descarga DATE,
    n_ejemplos INT,
    proporcion_hate FLOAT,
    idioma VARCHAR(10),
    plataforma VARCHAR(50)
);

-- Tabla: Corpus de Documentos
CREATE TABLE documentos (
    documento_id VARCHAR(100) PRIMARY KEY,
    dataset_id VARCHAR(50) NOT NULL REFERENCES datasets(dataset_id),
    texto TEXT NOT NULL,
    etiqueta INT CHECK (etiqueta IN (0, 1)),
    tiene_modismo BOOLEAN,
    n_tokens INT,
    partition VARCHAR(10) CHECK (partition IN ('train', 'val', 'test')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

-- Tabla: Modismos LATAM
CREATE TABLE modismos_latam (
    modismo_id VARCHAR(100) PRIMARY KEY,
    termino VARCHAR(100) NOT NULL UNIQUE,
    variantes TEXT,
    pais VARCHAR(10),
    tipo VARCHAR(50),
    fuente VARCHAR(200),
    notas TEXT,
    fecha_inclusion DATE
);

-- Tabla Asociativa: Documento ↔ Modismo
CREATE TABLE documento_modismos (
    documento_id VARCHAR(100) NOT NULL REFERENCES documentos(documento_id),
    modismo_id VARCHAR(100) NOT NULL REFERENCES modismos_latam(modismo_id),
    PRIMARY KEY (documento_id, modismo_id)
);

-- Tabla: Modelos Entrenados
CREATE TABLE modelos_entrenados (
    modelo_id VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    base_model VARCHAR(50),
    seed INT,
    f1_validacion FLOAT,
    f1_test FLOAT,
    precision FLOAT,
    recall FLOAT,
    ruta_archivo TEXT,
    fecha_entrenamiento TIMESTAMP,
    n_parametros INT
);

-- Tabla: Predicciones (Inferencia)
CREATE TABLE predicciones (
    prediccion_id VARCHAR(100) PRIMARY KEY,
    modelo_id VARCHAR(100) NOT NULL REFERENCES modelos_entrenados(modelo_id),
    texto_input TEXT,
    etiqueta_predicha INT CHECK (etiqueta_predicha IN (0, 1)),
    probabilidad FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    es_correcto BOOLEAN
);

-- Tabla: Explicaciones (XAI)
CREATE TABLE explicaciones (
    explicacion_id VARCHAR(100) PRIMARY KEY,
    prediccion_id VARCHAR(100) NOT NULL UNIQUE REFERENCES predicciones(prediccion_id),
    tokens TEXT,
    pesos_shap TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Diagrama de Actividades

### 4.1 Flujo de Actividades - Fase de Datos (Paso 1)

```
┌─────────────────┐
│      Inicio     │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│ 1.1 Descargar Datasets Públicos  │
│ (HatEval, DETOXIS, HaterNet,     │
│  Chilean)                        │
└────────────┬─────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Verificación  │
     │ Exitosa?      │
     └─┬──────────┬──┘
       │ NO       │ SI
       │          ▼
       │   ┌─────────────────────────────────┐
       │   │ 1.2 Verificar Contenido         │
       │   │ (estructura, integridad, tipos) │
       │   └─────────┬───────────────────────┘
       │             │
       │             ▼
       │   ┌─────────────────┐
       │   │ QC Exitoso?     │
       │   └─┬───────────┬───┘
       │     │ NO        │ SI
       │     │           ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.3 Exploración Inicial       │
       │     │   │ (estadísticas, distribuciones) │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.4 Limpieza de Textos        │
       │     │   │ (normalización, eliminación    │
       │     │   │  de URLs, emojis, etc)        │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.5 Mapeo de Etiquetas        │
       │     │   │ (unificación a binario)        │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.6 Construcción de Lexicón    │
       │     │   │ LATAM (500+ términos)          │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.7 Enriquecimiento Corpus     │
       │     │   │ (marcado de modismos)          │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.8 Validación de Calidad      │
       │     │   │ (aserciones, distribuciones)   │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.9 Particionado              │
       │     │   │ (train/val/test estratificado) │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.10 MANIFEST.json            │
       │     │   │ (hash, versión, metadatos)     │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            ▼
       │     │   ┌────────────────────────────────┐
       │     │   │ 1.11 Reporte QC Corpus        │
       │     │   │ (gráficos, tablas resumen)     │
       │     │   └────────┬───────────────────────┘
       │     │            │
       │     │            └──────────┬─────────────┐
       │     └─────────────────────────┘           │
       │                                           │
       ▼                                           ▼
┌──────────────┐                         ┌──────────────────┐
│    Error ❌   │                         │  Corpus Listo ✓ │
│ Reintentar   │                         │                  │
│ Paso 1.x     │                         │ Pasar a Fase 2   │
└──────────────┘                         │  (Entrenamiento) │
                                         └──────────────────┘
```

### 4.2 Flujo de Actividades - Fase de Entrenamiento (Paso 2)

```
┌─────────────────────────┐
│ Corpus Listo (Fase 1)   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2.1 Configurar GPU (Colab/Local)    │
│ Verificar CUDA, PyTorch             │
└────────────┬────────────────────────┘
             │
             ▼
     ┌──────────────────┐
     │ GPU Disponible?  │
     └─┬──────────────┬─┘
       │ NO           │ SI
       │              ▼
       │      ┌───────────────────────┐
       │      │ Usar CPU con aviso    │
       │      └───────────┬───────────┘
       │                  │
       └──────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ 2.2 Crear Script de Entrenamiento            │
│ (reproducible, con 3 semillas)               │
└──────────────┬───────────────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
┌──────────────┐ ┌──────────────────────┐
│ BETO         │ │ mBERT y XLM-R        │
│ (seed=42,    │ │ (siguiendo mismos    │
│  123, 2024)  │ │  hiperparámetros)    │
└──────────────┘ └──────────────────────┘
     │                   │
     ▼                   ▼
┌────────────────────────────────────────┐
│ 2.3-2.4 Entrenar Modelos               │
│ (3 semillas × 3 modelos = 9 runs)      │
│ Cada: 2-4 horas (T4/P100)              │
│       12-24 horas (CPU)                │
└──────────────┬───────────────────────────┘
               │
               ▼
     ┌─────────────────┐
     │ Entrenamiento   │
     │ Exitoso?        │
     └─┬────────────┬──┘
       │ NO         │ SI
       │            ▼
       │  ┌──────────────────────────────────┐
       │  │ 2.5 Seleccionar Mejor Semilla    │
       │  │ (máximo F1 en validación)        │
       │  └────────────┬─────────────────────┘
       │               │
       │               ▼
       │  ┌──────────────────────────────────┐
       │  │ 2.5 Copiar a Modelo Final        │
       │  │ (beto_finetuned_final/)          │
       │  └────────────┬─────────────────────┘
       │               │
       │               ▼
       │  ┌──────────────────────────────────┐
       │  │ Documentar en EXPERIMENTOS.md    │
       │  │ (métricas, decisiones, notas)    │
       │  └────────────┬─────────────────────┘
       │               │
       │               └────┬─────────┐
       │                    │         │
       └────────────────────┘         │
                                      ▼
                            ┌──────────────────┐
                            │ Modelos Listos ✓ │
                            │ Pasar a Fase 3   │
                            │ (Evaluación)     │
                            └──────────────────┘
```

### 4.3 Flujo de Actividades - Fase de Evaluación (Paso 3)

```
┌──────────────────────────────────┐
│ Modelos Entrenados (Fase 2)      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ 3.1 Crear Script de Evaluación              │
│ (métricas estándar + estadístico)            │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ 3.2 Ejecutar Evaluación en Test Set         │
│ (Precision, Recall, F1, Accuracy, ROC-AUC) │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ 3.3 Bootstrap e Intervalos de Confianza     │
│ (1000 remuestreos × metrica)                │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ 3.4 Test de McNemar Pareado                 │
│ (BETO vs mBERT, BETO vs XLM-R, etc)         │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│ 4.1 Análisis de Modismos (H3)              │
│ - Segmentar test: con/sin modismos          │
│ - Evaluar en cada subconjunto               │
│ - Verificar diferencia significativa        │
└──────────────┬───────────────────────────────┘
               │
               ▼
         ┌──────────────┐
         │ H3 Válida?   │
         └─┬─────────┬──┘
           │ NO      │ SI
           │         ▼
           │  ┌─────────────────────────┐
           │  │ Documentar Conclusión   │
           │  │ (hipótesis soportada)   │
           │  └─────────┬───────────────┘
           │            │
           └────────────┤
                        ▼
         ┌────────────────────────────────┐
         │ Generar Reportes Finales       │
         │ - Tablas comparativas          │
         │ - Gráficos (confusion matrices)│
         │ - Análisis cualitativo         │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │ Evaluación Completada ✓        │
         │ Pasar a Fase 5 (XAI)           │
         └────────────────────────────────┘
```

---

## 5. Componentes del Sistema

### 5.1 Módulo de Datos (`src/data/`)

**Responsabilidades:**
- Descarga y verificación de datasets públicos
- Limpieza y normalización de textos
- Unificación de etiquetas a esquema binario
- Enriquecimiento con lexicón LATAM
- Generación de particiones train/val/test
- Reportes de calidad (QC)

**Interfaces:**
```
Entrada:  datasets_crudos → data/raw/<dataset>/
Proceso:  Pipelines Python con pandas/scikit-learn
Salida:   corpus_unificado → data/processed/*.parquet
          reporte_qc.md → data/reports_qc/
```

### 5.2 Módulo de Modelado (`src/modeling/`)

**Responsabilidades:**
- Tokenización con AutoTokenizer
- Entrenamiento con Trainer o bucle manual
- Gestión de checkpoints
- Fine-tuning reproducible (semillas fijas)
- Empaquetado del modelo final

**Interfaces:**
```
Entrada:  corpus_unificado → data/processed/*.parquet
Proceso:  transformers.Trainer + torch
Salida:   modelos_entrenados → models/<modelo>_<seed>/
          experimentos_log → EXPERIMENTOS.md
```

### 5.3 Módulo de Evaluación (`src/evaluation/`)

**Responsabilidades:**
- Cálculo de métricas (Precision, Recall, F1, etc.)
- Bootstrap e intervalos de confianza
- Test estadísticos (McNemar)
- Análisis segmentado (modismos sí/no)
- Generación de tablas y figuras

**Interfaces:**
```
Entrada:  modelos_entrenados + test.parquet
Proceso:  sklearn.metrics + scipy.stats
Salida:   metricas.csv, confusion_matrix.png
          comparativa_global.csv
```

### 5.4 Módulo de XAI (`src/xai/`)

**Responsabilidades:**
- Generación de explicaciones SHAP
- Extracción de tokens importantes
- Normalización de salida JSON
- Cálculo de pesos por token

**Interfaces:**
```
Entrada:  modelo_final + fragmentos_texto
Proceso:  shap.Explainer()
Salida:   {tokens: [...], pesos_shap: [...]}
```

### 5.5 Backend API (`src/api/`)

**Responsabilidades:**
- Carga única del modelo al iniciar
- Definición de esquemas Pydantic
- Endpoints REST (/health, /predict, /explain, /metadata)
- CORS restringido
- Logging y manejo de errores
- OpenAPI/Swagger documentation

**Interfaces:**
```
Entrada:  HTTP POST requests (JSON)
Proceso:  FastAPI + transformers + torch
Salida:   HTTP JSON responses
          {etiqueta, probabilidad, modelo, version}
          {tokens, pesos_shap}
```

### 5.6 Extensión de Navegador (`extension/`)

**Responsabilidades:**
- Content script: escaneo de DOM y resaltado
- Service worker: cola de inferencia y fetches
- Popup: control de activación y umbral
- Options page: gestión de lexicón personal
- Storage: persistencia en chrome.storage.local

**Interfaces:**
```
Entrada:  Contenido HTML del navegador (DOM)
Proceso:  JavaScript vanilla (Manifest V3)
Salida:   Resaltado de fragmentos
          Tooltips con explicaciones
          Lexicón personal sincronizado
```

---

## 6. Patrones de Diseño

| Patrón | Ubicación | Propósito |
|--------|-----------|----------|
| **MVC** | Backend + Extensión | Separación de Model, View, Controller |
| **Pipeline** | src/data/ | Encadenamiento de transformaciones |
| **Factory** | src/modeling/ | Creación flexible de modelos (BETO, mBERT, XLM-R) |
| **Strategy** | src/evaluation/ | Intercambio de métricas y tests estadísticos |
| **Observer** | Extension (Service Worker) | Cola de eventos y actualizaciones |
| **Singleton** | Backend | Carga única del modelo en lifespan |
| **Repository** | src/data/ + sql | Acceso a datos mediante interfaz abstracta |
| **Adapter** | Extension + Backend | Normalización de contrato HTTP/JSON |

---

## 7. Flujo de Despliegue

```
Desarrollo Local (Investigador)
    ↓
    ├─ Fase 1: Preparación de Datos (data/raw → data/processed/)
    ├─ Fase 2: Entrenamiento (data/processed → models/)
    ├─ Fase 3: Evaluación (models/ → reports/)
    ├─ Fase 5: XAI (models/ → src/xai/)
    │
    ↓
Despliegue Backend (src/api/)
    ├─ uvicorn src.api.main:app --host 127.0.0.1 --port 8000
    ├─ Endpoints: /health, /predict, /explain, /metadata
    ├─ CORS: localhost + chrome-extension://*
    │
    ↓
Instalación Extensión (extension/)
    ├─ chrome://extensions → Modo de desarrollador
    ├─ Cargar extensión sin empaquetar (extension/)
    ├─ Permisos: activeTab, scripting, storage
    ├─ Host: http://127.0.0.1:8000/*
    │
    ↓
Usuario Final
    ├─ Activa extensión desde popup
    ├─ Detecta hate speech en redes sociales
    ├─ Resalta fragmentos con tooltip
    ├─ Gestiona lexicón personal
    └─ Todos los datos: locales (privacidad)
```

---

## 8. Matriz de Trazabilidad: Requisitos → Arquitectura

| Requisito | Módulo | Endpoint | Componente | Fase |
|-----------|--------|----------|-----------|------|
| RF1: Corpus unificado | src/data/ | — | Pipeline de datos | 1 |
| RF2: Lexicón LATAM | src/data/lexicon.py | — | Módulo de Lexicón | 1 |
| RF3: Fine-tuning BETO | src/modeling/ | — | Trainer | 2 |
| RF4: Baselines (mBERT, XLM-R) | src/modeling/ | — | Trainer | 2 |
| RF5: Evaluación cuantitativa | src/evaluation/ | — | Evaluador | 3 |
| RF6: XAI (SHAP) | src/xai/ | /explain | XAI Module | 5 |
| RF7: Backend REST | src/api/ | /health, /predict, /explain | FastAPI | 6 |
| RF8: Extensión de navegador | extension/ | — | Content + Service Worker | 7 |
| RF9: Detección automática | extension/content.js | — | Content Script | 7 |
| RF10: Lexicón personal | extension/ | — | Options Page + Storage | 7 |
| RF11: Reportes científicos | notebooks/ + data/reports/ | — | Documentación | 1-8 |

---

## 9. Decisiones Arquitectónicas Clave

### 9.1 ¿Por qué 3 capas?

- **Separación de concerns**: Datos ≠ Servicio ≠ Cliente
- **Escalabilidad**: Cada capa puede evolucionar independientemente
- **Testabilidad**: Tests unitarios aislados por capa
- **Reusabilidad**: Modelo de datos reutilizable en diferentes contextos

### 9.2 ¿Por qué FastAPI vs. Flask?

- **Type hints**: Validación automática con Pydantic
- **OpenAPI**: Documentación interactiva (Swagger)
- **Performance**: Async por defecto
- **Familiaridad**: Estándar en ML en 2024

### 9.3 ¿Por qué Manifest V3 vanilla (no React)?

- **Peso**: Evita bundle de React (~42 KB vs. 600 KB)
- **Reproducibilidad**: Código simple auditable para jurado
- **Privacidad**: Ningún framework externo analiza DOM

### 9.4 ¿Por qué etiquetado binario (no multiclase)?

- **Unificación**: Compatibilidad entre 4 datasets heterogéneos
- **Simplicidad**: Hipótesis H1–H3 formuladas en binario
- **Generalización**: Mayor transferencia a nuevos dominios

### 9.5 ¿Por qué 3 semillas (no 1)?

- **Varianza**: Neutraliza randomness intrínseco en Transformers
- **Confiabilidad**: Media ± std es más defensible en defensa
- **Replicabilidad**: Reproductor puede validar con mismas semillas

---

## Resumen

La arquitectura del sistema es **modular, escalable y reproducible**, con clara separación entre:
- **Fase científica offline** (datos + ML)
- **Fase de servicio online** (API)
- **Fase de usuario online** (extensión)

Cada componente tiene responsabilidades bien definidas, interfaces claras y patrones de diseño reconocibles. El sistema prioriza **rigor experimental** sobre adorno UI, permitiendo que el jurado audite cada fase de manera independiente.
