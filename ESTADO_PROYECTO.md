# ESTADO GENERAL DEL PROYECTO DE TESIS

**Última revisión:** 2026-06-24  
**Progreso actual:** Paso 1.8 completado (Fase 1: Gestión de Datos)

---

## 1. ¿De qué trata la tesis?

**Título:** *Sistema Inteligente de Moderación Automática en Redes Sociales para la Protección del Bienestar Digital del Usuario*

**En una frase:** Crear un sistema que detecte automáticamente discurso de odio en español usando el modelo BETO (BERT en español) ajustado con un corpus enriquecido con modismos latinoamericanos, y demostrar su funcionamiento mediante un backend REST y una extensión de navegador.

**Clasificación:** Binaria → `hate` / `no_hate`

---

## 2. Secuencia paso a paso (resumen rápido)

### FASE 1 — Gestión de Datos (Semanas 1-2)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1.1 | Verificar fuentes de datos (Superset + DETOXIS) | ✅ Completado |
| 1.2 | Verificar contenido de datasets (scripts de análisis) | ✅ Completado |
| 1.3 | Exploración del corpus base (stats, figuras, reporte) | ✅ Completado |
| 1.4 | Crear `normalizar()` en `src/data/clean.py` (solo DETOXIS) | ✅ Completado |
| 1.5 | Unificar superset + DETOXIS al esquema canónico → `corpus_combinado.parquet` | ✅ Completado |
| 1.6 | Construir lexicón de modismos latinoamericanos (`modismos_latam_v1.csv`) | ✅ Completado |
| 1.7 | Enriquecer corpus con `tiene_modismo` → `corpus_v1_enriquecido.parquet` | ✅ Completado |
| **1.8** | **Validación de calidad (`qc.py`) + reporte `qc_corpus_v1.md`** | ✅ **Completado** |
| 1.9 | Particionar en train/val/test (70/15/15 estratificado) | ⬜ Pendiente |
| 1.10 | Crear `MANIFEST.json` con hashes y versiones | ⬜ Pendiente |
| 1.11 | Generar reporte QC final del corpus v1 | ⬜ Pendiente |

### FASE 2 — Fine-tuning de BETO (Semanas 3-5)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 2.1 | Configurar entorno GPU (Colab/Kaggle/local) | ⬜ Pendiente |
| 2.2 | Crear script de entrenamiento (`scripts/train_model.py`) | ⬜ Pendiente |
| 2.3 | Entrenar BETO con 3 semillas (42, 123, 2024) | ⬜ Pendiente |
| 2.4 | Entrenar mBERT y XLM-R (baselines, 3 semillas c/u) | ⬜ Pendiente |
| 2.5 | Seleccionar mejor semilla → `beto_finetuned_final/` | ⬜ Pendiente |

### FASE 3 — Evaluación en Test Set (Semanas 5-6)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 3.1 | Script de evaluación (`evaluate_model.py`) | ⬜ Pendiente |
| 3.2 | Ejecutar evaluación con métricas (Precision, Recall, F1, Accuracy, ROC-AUC) | ⬜ Pendiente |
| 3.3 | Bootstrap para intervalos de confianza (IC 95%) | ⬜ Pendiente |
| 3.4 | Test de McNemar pareado entre modelos | ⬜ Pendiente |

### FASE 4 — Análisis de Modismos / H3 (Semana 6)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 4.1 | Segmentar test set (con_modismos / sin_modismos) | ⬜ Pendiente |
| 4.2 | Evaluar BETO en ambos subconjuntos | ⬜ Pendiente |
| 4.3 | Prueba estadística de H3 (bootstrap + McNemar) | ⬜ Pendiente |

### FASE 5 — XAI con SHAP (Semana 7)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 5.1 | Generar explicaciones SHAP sobre ejemplos del test | ⬜ Pendiente |

### FASE 6 — Backend FastAPI (Semanas 7-8)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 6.1 | Crear archivos API (config, schemas, main) | ⬜ Pendiente |
| 6.2 | Ejecutar API en localhost:8000 | ⬜ Pendiente |

### FASE 7 — Extensión Chrome (Semanas 8-9)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 7.1-7.3 | Extensión completa con lexicón local | ✅ Completado (v0.9.0-beta) |
| — | Integración con BETO vía API | ⬜ Pendiente (cuando Fase 6 esté lista) |

### FASE 8 — Validación Final (Semana 10)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 8.1-8.3 | EXPERIMENTOS.md, MANIFEST.json, tag v1.0 | ⬜ Pendiente |

---

## 3. Hipótesis que se validan

| ID | Hipótesis | Método de validación |
|----|-----------|---------------------|
| **H1** | BETO ajustado (con corpus enriquecido) > BETO base | F1 + McNemar pareado |
| **H2** | BETO ajustado ≥ mBERT y XLM-R | F1 + McNemar pareado |
| **H3** | BETO ajustado rinde mejor en textos CON modismos LATAM que SIN ellos | Bootstrap de ΔF1 + análisis segmentado |

---

## 4. Análisis: ¿Cumple lo que propone?

### ✅ Lo que está bien

1. **Metodología sólida:** El diseño experimental es robusto — 3 semillas, pruebas estadísticas formales (McNemar, bootstrap), variables de control documentadas. Esto es defendible ante un jurado.

2. **Corpus bien fundamentado:** Usar el Spanish Hate Speech Superset (Tonneau et al., 2024, WOAH/ACL) como base es una decisión muy fuerte — tiene respaldo académico de primer nivel. DETOXIS complementa bien con diversidad de plataforma.

3. **Arquitectura desacoplada:** Las 3 capas (datos/servicio/cliente) están correctamente separadas. El grafo de dependencias es acíclico. Esto es buena ingeniería de software.

4. **Extensión ya funcional:** Tener la Fase 7 completa (aunque sin BETO) es estratégicamente inteligente — demuestra la viabilidad del sistema completo.

5. **Lexicón como feature observacional:** Decisión clave — el lexicón NO alimenta al modelo, solo se usa para segmentar la evaluación. Esto evita la crítica de "inflar desempeño artificialmente".

6. **Documentación exhaustiva:** `guia.md` tiene nivel de especificación técnica de producción.

### ⚠️ Observaciones y riesgos

1. **Paso 1.6 faltante** — Ver sección 5 abajo.

2. **Avance lento relativo al cronograma:** Con 10 semanas estimadas, estar en el paso 1.5 de la Fase 1 indica que aún falta ~75% del trabajo técnico pesado (entrenamiento, evaluación, análisis estadístico).

3. **La Fase 7 se hizo antes de la Fase 2-6:** No es un problema per se (la extensión funciona con lexicón local), pero la integración con BETO aún no se ha probado. Riesgo bajo, pero existe.

4. **Lexicón LATAM aún no existe:** El `modismos_latam_v1.csv` aún no se ha construido. Este es un componente **fundacional** — H3 depende enteramente de él. Debe tener ≥500 términos con cobertura ≥15% del corpus.

5. **GPU requerida para entrenamiento:** Las fases 2-5 necesitan GPU. Si solo se tiene CPU, los tiempos se multiplican x10-x20.

6. **Los datos del corpus real (33,318 filas) difieren ligeramente de las cifras del MANIFEST.json propuesto (38,421):** Esto se debe a que el MANIFEST tiene valores placeholder. Asegurarse de actualizar con datos reales.

### ✅ Veredicto general

**El proyecto cumple con lo que propone a nivel de diseño.** Las hipótesis son validables con la metodología planteada, la arquitectura es correcta, y el pipeline de datos es coherente. El riesgo principal es de **tiempo**, no de diseño.

---

## 5. Sobre el Paso 1.6 — ¿Existe?

### Respuesta: **NO, el paso 1.6 no existe en `desarrollo.md`.**

La numeración en el documento salta directamente:

```
Paso 1.5 → Paso 1.7
```

Específicamente:
- **Paso 1.5** (línea 279): *"Integrar superset y DETOXIS al esquema canónico"* — ✅ completado, crea `corpus_combinado.parquet`
- **Paso 1.7** (línea 398): *"Enriquecer corpus con `tiene_modismo`"* — pendiente, crea `corpus_enriquecido.parquet`

### ¿Qué debería ir en el Paso 1.6?

Revisando la guía maestra (`guia.md`), entre la unificación del corpus (sección 7) y el enriquecimiento con modismos (sección 7.6), el paso lógico faltante sería:

> **Paso 1.6 — Construir el lexicón de modismos latinoamericanos**
> 
> Basado en `guia.md` sección 8 (*Lexicón de Modismos Latinoamericanos*):
> - Crear `data/lexicons/modismos_latam_v1.csv` con ≥500 términos
> - Columnas: `termino`, `variantes`, `pais`, `tipo`, `fuente`, `notas`, `version_introduccion`
> - Fuentes: ASALE (Diccionario de Americanismos), literatura científica, curaduría manual documentada
> - Implementar `src/data/lexicon.py` con la clase `LexiconLatam` y función `tiene_modismo()`
> - Cobertura mínima: MX, AR, CL, CO, PE, VE, EC (≥30 términos por país)
> - Validar: sin duplicados, sin vacíos, países válidos ISO
> - Test: `tests/unit/test_lexicon.py`

De hecho, en la línea 1602 de `desarrollo.md` (sección "Cómo continuar"), se menciona vagamente:

> *"**Pasos 1.6-1.10** - lexicon LATAM (data/lexicons/modismos_latam_v1.csv), enriquecimiento (tiene_modismo), QC, particionado 70/15/15."*

Esto confirma que el paso 1.6 **debía existir** (para el lexicón) pero se omitió al redactar el documento en detalle.

### Acción recomendada

Agregar explícitamente el **Paso 1.6 — Construir lexicón LATAM** entre el paso 1.5 y el 1.7 en `desarrollo.md`.

---

## 6. Resumen del estado actual

```
PROGRESO GENERAL
═══════════════════════════════════════════════════════
Fase 1: Datos          ████████████░░░░░░░  ~65%  (1.8 de 1.11)
Fase 2: Entrenamiento  ░░░░░░░░░░░░░░░░░░░   0%
Fase 3: Evaluación     ░░░░░░░░░░░░░░░░░░░   0%
Fase 4: Modismos/H3    ░░░░░░░░░░░░░░░░░░░   0%
Fase 5: XAI            ░░░░░░░░░░░░░░░░░░░   0%
Fase 6: Backend API    ░░░░░░░░░░░░░░░░░░░   0%
Fase 7: Extensión      ███████████████████  100%  (sin BETO)
Fase 8: Validación     ░░░░░░░░░░░░░░░░░░░   0%
═══════════════════════════════════════════════════════
TOTAL ESTIMADO:        ~30% completado
```

### Próximos pasos inmediatos (en orden)

1. **Paso 1.9** — Particionar en train/val/test (70/15/15 estratificado)
2. **Paso 1.10** — Crear `MANIFEST.json` con SHA-256 y versiones
3. **Paso 1.11** — Reporte QC final del corpus v1
4. **Fase 2** — Entrenamiento de modelos (requiere GPU)

---

## 7. Archivos clave del proyecto

| Documento | Ubicación | Propósito |
|-----------|-----------|-----------|
| Guía maestra | `documentos_extras/guia.md` | Especificación técnica completa |
| Desarrollo | `documentos_extras/desarrollo.md` | Itinerario paso a paso + estado |
| Experimentos | `EXPERIMENTOS.md` | Bitácora científica |
| Este archivo | `ESTADO_PROYECTO.md` | Resumen ejecutivo del estado |
| Guía extensión | `documentos_extras/guia-extension.md` | Documentación de la extensión |
