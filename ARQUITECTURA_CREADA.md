# DOCUMENTO ARQUITECTURA CREADO

**Fecha:** 3 de Junio de 2026  
**Ubicación:** `documentos_extras/arquitectura.md`  
**Estado:** ✓ COMPLETADO Y LISTO PARA INCORPORAR EN TESIS

---

## Contenido del Documento

He creado un documento completo de **Diseño del Sistema** con todas las secciones solicitadas:

### 1. Diseño Arquitectónico ✓
- Visión general de 3 capas desacopladas
- Modelo arquitectónico (Capas + Microservicios)
- Diagrama ASCII profesional

### 2. Diagramas UML ✓

**2.1 Diagrama de Casos de Uso**
- Usuario final (Activar detección, Ajustar umbral, Gestionar lexicón)
- Investigador (Descargar datasets, Limpiar corpus, Entrenar modelos, Evaluar)

**2.2 Diagrama de Clases**
- Documento (Corpus): documento_id, texto, etiqueta, tiene_modismo, etc.
- Dataset (Metadatos): dataset_id, nombre, url_fuente, n_ejemplos, etc.
- Modismo LATAM: modismo_id, termino, variantes, pais, tipo, etc.
- Modelo Entrenado: modelo_id, base_model, seed, f1_test, etc.
- Predicción (Inferencia): prediccion_id, modelo_id, etiqueta_predicha, probabilidad
- Explicación (XAI): explicacion_id, tokens, pesos_shap

**2.3 Diagrama de Secuencia - Flujo de Predicción**
- Usuario activa detección
- Extensión escanea DOM y segmenta texto
- Backend procesa: POST /predict → Tokenizar → Forward Pass → Softmax
- Respuesta: {etiqueta, probabilidad}
- XAI: POST /explain → SHAP Extract → {tokens, pesos}

**2.4 Diagrama de Secuencia - Flujo de Entrenamiento**
- Descarga de datasets
- Limpieza y unificación de corpus
- Entrenamiento con 3 semillas
- Selección de mejor modelo
- Evaluación y comparativa

**2.5 Diagrama de Secuencia - Flujo de Inicialización**
- Carga del modelo en memoria del backend
- Inicialización de extensión
- Carga de lexicón personal

### 3. Diagrama Entidad-Relación (DER) ✓

**3.1 Esquema Conceptual**
- Relaciones entre Documentos, Datasets, Modismos
- Relaciones entre Modelos, Predicciones, Explicaciones
- Entidad Usuario (local en chrome.storage)

**3.2 Esquema SQL**
- DDL completo: CREATE TABLE para todas las entidades
- Constraints: PK, FK, CHECK
- Índices implícitos sobre claves primarias

**Tablas incluidas:**
- datasets
- documentos
- modismos_latam
- documento_modismos (Tabla asociativa M:N)
- modelos_entrenados
- predicciones
- explicaciones

### 4. Diagramas de Actividades ✓

**4.1 Fase 1: Gestión de Datos**
- Pasos 1.1-1.11
- Bifurcaciones de decisión (¿Verificación exitosa?, ¿QC Exitoso?)
- Salida: Corpus Listo

**4.2 Fase 2: Entrenamiento**
- Configuración de GPU
- Creación de script
- Entrenamiento BETO, mBERT, XLM-R
- Selección de mejor semilla
- Salida: Modelos Listos

**4.3 Fase 3: Evaluación**
- Evaluación en test set
- Bootstrap e intervalos de confianza
- Test de McNemar
- Análisis de modismos (H3)
- Generación de reportes

---

## Secciones Adicionales del Documento

### 5. Componentes del Sistema ✓
- **Módulo de Datos** (`src/data/`)
- **Módulo de Modelado** (`src/modeling/`)
- **Módulo de Evaluación** (`src/evaluation/`)
- **Módulo de XAI** (`src/xai/`)
- **Backend API** (`src/api/`)
- **Extensión de Navegador** (`extension/`)

Cada módulo incluye:
- Responsabilidades
- Interfaces (Entrada/Proceso/Salida)

### 6. Patrones de Diseño ✓
- **MVC**: Backend + Extensión
- **Pipeline**: src/data/
- **Factory**: src/modeling/
- **Strategy**: src/evaluation/
- **Observer**: Extension (Service Worker)
- **Singleton**: Backend (carga única del modelo)
- **Repository**: src/data/ + SQL
- **Adapter**: Extension + Backend

### 7. Flujo de Despliegue ✓
```
Desarrollo Local
  ├─ Fase 1: Preparación de Datos
  ├─ Fase 2: Entrenamiento
  ├─ Fase 3: Evaluación
  ├─ Fase 5: XAI
  └─ Backend API (uvicorn)
     └─ Extensión (chrome.extensions)
        └─ Usuario Final
```

### 8. Matriz de Trazabilidad ✓
**Requisitos → Arquitectura → Módulos → Fases**

| RF | Módulo | Endpoint | Componente | Fase |
|---|---|---|---|---|
| RF1: Corpus unificado | src/data/ | — | Pipeline de datos | 1 |
| RF2: Lexicón LATAM | src/data/lexicon.py | — | Módulo de Lexicón | 1 |
| RF3: Fine-tuning BETO | src/modeling/ | — | Trainer | 2 |
| RF7: Backend REST | src/api/ | /health, /predict, /explain | FastAPI | 6 |
| RF9: Detección automática | extension/content.js | — | Content Script | 7 |
| ... y más |

### 9. Decisiones Arquitectónicas Clave ✓
- **¿Por qué 3 capas?** → Separación de concerns, escalabilidad, testabilidad
- **¿Por qué FastAPI vs. Flask?** → Type hints, OpenAPI, performance, async
- **¿Por qué Manifest V3 vanilla (no React)?** → Peso, reproducibilidad, privacidad
- **¿Por qué etiquetado binario (no multiclase)?** → Unificación, simplicidad, generalización
- **¿Por qué 3 semillas (no 1)?** → Varianza, confiabilidad, replicabilidad

---

## Estadísticas del Documento

- **Total de líneas:** 1000+
- **Secciones principales:** 9
- **Diagramas UML/DER/ASCII:** 15+
- **Tablas comparativas:** 5+
- **Código SQL:** Completo (DDL)
- **Patrón arquitectónico:** Arquitectura en Capas + Microservicios

---

## Características del Documento

✓ **Profesional**: Formato académico listo para tesis  
✓ **Completo**: Cubre todas las secciones solicitadas  
✓ **Visual**: 15+ diagramas en ASCII (fáciles de convertir a imágenes en Word)  
✓ **Técnico**: SQL, patrones de diseño, trazabilidad de requisitos  
✓ **Modular**: Cada sección es independiente, facilita reorganización en Word  
✓ **Citable**: Referencias a módulos específicos y números de fase

---

## Cómo Usar en tu Word

1. **Copiar secciones completas** desde Markdown a Word
2. **Convertir diagramas ASCII** a:
   - Imágenes PNG (captura de pantalla + crop)
   - Shapes/Diagramas nativos en Word (Draw + Connector tools)
   - SmartArt de Word
3. **Reorganizar según estructura de tesis**:
   - Renombrar secciones
   - Ajustar nivel de títulos
   - Añadir numeración de figuras
4. **Referenciar desde otras secciones** (Estado del Arte, Marco Teórico, etc.)

---

## Próximos Pasos Opcionales

El documento está completo según lo solicitado. Opcionalmente puedes:

- ✗ Añadir Prototipos/Mockups (dijiste que todavía no son necesarios)
- ✓ Incluir Componentes del Sistema (YA INCLUIDO)
- ✓ Incluir Patrones de Diseño (YA INCLUIDO)
- ✓ Incluir Matriz de Trazabilidad (YA INCLUIDO)

---

## Validación

El documento cumple con TODAS las secciones solicitadas:

- [x] **Diseño del Sistema**
- [x] **Arquitectura del software** (Capas + Microservicios)
- [x] **Diagramas UML**
  - [x] Casos de uso
  - [x] Clases
  - [x] Secuencia
  - [x] Actividades
- [x] **Diseño de base de datos (DER)**
- [x] **Prototipos**: NO (según indicaste)

---

**ESTADO: ✓ LISTO PARA INCORPORAR EN TESIS**

Ubicación: `documentos_extras/arquitectura.md`
