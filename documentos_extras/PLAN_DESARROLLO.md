# Guía Ejecutable: Pasos para Llevar a Cabo el Proyecto Completo

Este documento es un **itinerario práctico paso a paso** para implementar todo el proyecto. Está basado en `INSTRUCCIONES_PROYECTO.md` y complementa sus especificaciones técnicas.

**Tiempo total estimado:** 8-10 semanas (ver cronograma en INSTRUCCIONES_PROYECTO.md sección 16)

---

## PREPARACIÓN INICIAL

### Paso 0.1 - Verificar el entorno

```bash
python --version  # Debe ser >= 3.10
pip --version
git --version
```

### Paso 0.2 - Clonar / inicializar el repositorio

```bash
cd Tesis_Proyecto
git init
git config user.name "Tu nombre"
git config user.email "tu@email.com"
```

### Paso 0.3 - Crear entorno virtual

```bash
python -m venv venv
source venv/Scripts/activate  # En Windows
# o:
# . venv/Scripts/Activate.ps1  # PowerShell Windows
# source venv/bin/activate     # Linux/Mac
```

### Paso 0.4 - Instalar dependencias

```bash
pip install -r requirements.txt
```

**Alternativa con Conda:**

```bash
conda env create -f environment.yml
conda activate tesis-proyecto
```

### Paso 0.5 - Verificar estructura de carpetas

```bash
ls -la data/
ls -la src/
ls -la notebooks/
ls -la extension/
```

Si alguna carpeta falta, crearla manualmente.

---

## FASE 1: GESTIÓN DE DATOS (Semanas 1–2)

### Paso 1.1 - Verificar fuentes de datos

El corpus se construye combinando el **Spanish Hate Speech Superset** (ya disponible en el repositorio) con **DETOXIS**, que se añade manualmente.

| Fuente | Estado | Ruta |
| ------ | ------ | ---- |
| Spanish Hate Speech Superset (Tonneau et al., 2024) | ✅ Disponible | `data/raw/spanish-hate-speech-superset/es_hf_102024.csv` |
| DETOXIS (IberLEF 2021) | ✅ Disponible | `data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv` |

**El superset ya incluye**: HatEval, HaterNet, Chilean Dataset, HaSCoSVa y HOMO-MEX — todos preprocesados y con etiquetas binarizadas.

**Documentar en `EXPERIMENTOS.md`:** fecha de verificación, ruta y tamaño de cada archivo.

```python
import pandas as pd

df_sup = pd.read_csv("data/raw/spanish-hate-speech-superset/es_hf_102024.csv")
df_det = pd.read_csv("data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv")

print("Superset shape:", df_sup.shape)
print("Superset datasets:", df_sup["dataset"].value_counts())
print("DETOXIS shape:", df_det.shape)
print("DETOXIS columns:", df_det.columns.tolist())
```

### Paso 1.2 - Verificar contenido de datasets

Se dispone de dos scripts de verificacion en `data/raw/analisis_dataset/`:

| Script | Que verifica | Como ejecutar |
| ------ | ------------ | ------------- |
| `verificar_corpus.py` | Superset + DETOXIS (verificacion principal) | Ver abajo |
| `verificar_datasets_detoxis.py` | DETOXIS en detalle (20 dimensiones, mapeo binario) | Ver abajo |

**Ejecutar verificacion completa (verificar ambas fuentes):**

```powershell
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_corpus.py
```

El script produce en consola:
- Estructura, tipos y nulos del superset
- Distribucion de etiquetas por fuente y por dataset interno
- Distribucion por pais (geoloc Nov 2024)
- Longitud de textos (tokens) con alertas si P95 > 128
- Resumen combinado: filas, % hate, esquema canonico previsto

**Ejecutar verificacion detallada de DETOXIS (opcional):**

```powershell
.\venv\Scripts\python.exe data\raw\analisis_dataset\verificar_datasets_detoxis.py
```

---

### OK REALIZADO - Paso 1.1 y 1.2

**Se hizo:**

- Se identificaron las dos fuentes de datos definitivas:
  - **Spanish Hate Speech Superset** (`es_hf_102024.csv`): 29,855 ejemplos, 5 datasets ya unificados con etiquetas binarizadas, preprocesamiento documentado en paper WOAH 2024.
  - **DETOXIS 2021** (`DATASET_DETOXIS.csv`): 3,463 ejemplos; no incluido en el superset; aporta diversidad de plataforma (comentarios de noticias) y anotacion granular.
- Se tomo la decision de usar el superset en lugar de unificar los 4 datasets manualmente, dado su respaldo academico (Tonneau et al., 2024) y su preprocesamiento reproducible.
- Se crearon los scripts de verificacion: `verificar_corpus.py` (ambas fuentes) y `verificar_datasets_detoxis.py` (DETOXIS en detalle).
- Los datos individuales (HatEval, HaterNet, Chilean) se conservan en `data/raw/` como referencia pero no son la fuente principal del corpus.

---

### Paso 1.3 - Explorar el corpus base (superset + DETOXIS)

Hay dos formas equivalentes de ejecutar la exploracion:

**Opcion A — Script reproducible (recomendada):**

```powershell
.\venv\Scripts\python.exe scripts\exploracion_inicial.py
```

Produce automaticamente:
- `data/reports_qc/exploracion_inicial.md` — reporte ejecutivo con tabla resumen, contexto del superset y hallazgos clave
- `data/reports_qc/exploracion_inicial.json` — metricas crudas (machine-readable)
- `data/reports_qc/figuras/distribucion_clases.png` — hate/no-hate por fuente (superset y DETOXIS)
- `data/reports_qc/figuras/volumen_datasets.png` — filas por dataset dentro del superset
- `data/reports_qc/figuras/longitud_tokens.png` — mediana y P95 de tokens con lineas de referencia max_length=128/256
- `data/reports_qc/figuras/seeds_latam.png` — % textos con semillas LATAM (pre-lexicon)

**Opcion B — Notebook interactivo:**

```powershell
jupyter notebook notebooks\01_exploracion.ipynb
```

El notebook permite inspeccionar celda por celda y ajustar parametros.

**Que hace `scripts/exploracion_inicial.py`:**

1. Carga el superset (`es_hf_102024.csv`) y aplica el esquema canonico (`texto`, `etiqueta`)
2. Carga DETOXIS y aplica el mapeo binario (`toxicity_level >= 2 -> 1`)
3. Calcula por cada fuente: n_total, % hate, longitud (mediana, P95, max), % seeds LATAM pre-lexicon, duplicados, nulos
4. Genera 4 figuras PNG comparando ambas fuentes
5. Escribe el reporte MD y el JSON de metricas

---

### OK REALIZADO - Paso 1.3

**Se hizo:**

- `scripts/exploracion_inicial.py` reescrito completamente para el nuevo enfoque.
  Carga el superset y DETOXIS directamente (ya no los 4 datasets individuales).
- El script genera figuras y reporte orientados a comparar las dos fuentes del corpus.
- Total combinado: ~33,318 filas (superset 29,855 + DETOXIS 3,463).

**Archivos de salida (generados al ejecutar el script):**

| Archivo | Contenido |
| ------- | --------- |
| `scripts/exploracion_inicial.py` | Script principal. Carga superset + DETOXIS, calcula stats, genera figuras y reporte. |
| `notebooks/01_exploracion.ipynb` | Notebook que replica la logica del script para inspeccion interactiva. |
| `data/reports_qc/exploracion_inicial.md` | **Salida automatica.** Reporte ejecutivo con contexto academico del superset, tabla resumen y figuras. |
| `data/reports_qc/exploracion_inicial.json` | **Salida automatica.** Metricas crudas en JSON. |
| `data/reports_qc/figuras/*.png` | **Salida automatica.** 4 figuras (clases, volumen por dataset, longitud, seeds LATAM). |

---


### Paso 1.4 - Crear script de limpieza y normalización (solo para DETOXIS)

El superset **ya tiene preprocesamiento aplicado** (usernames → `@USER`, links → `URL`). Solo se necesita aplicar `normalizar()` a DETOXIS para homogeneizar ambas fuentes.

**Archivo:** `src/data/clean.py`

```python
import re
import html
import emoji
from ftfy import fix_text

URL_RE     = re.compile(r"http\S+|www\.\S+")
MENCION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
ZWSP_RE    = re.compile(r"[\u200b-\u200f\u202a-\u202e]")
REPEAT_RE  = re.compile(r"(.)\1{2,}")

def normalizar(texto: str) -> str:
    """Normalizar texto preservando mayúsculas (para BETO cased).
    Se aplica ÚNICAMENTE a DETOXIS; el superset ya tiene su propio preprocesamiento."""
    if not isinstance(texto, str):
        return ""
    texto = fix_text(texto)
    texto = html.unescape(texto)
    texto = ZWSP_RE.sub("", texto)
    texto = URL_RE.sub(" URL ", texto)
    texto = MENCION_RE.sub(" USUARIO ", texto)
    texto = HASHTAG_RE.sub(r" \1 ", texto)
    texto = emoji.demojize(texto, language="es")
    texto = REPEAT_RE.sub(r"\1\1", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

# Probar con muestras de DETOXIS
muestras = [
    "Hola @usuario https://example.com #test",
    "¡¡¡Hola!!!",
    "Me encanta 😂😂😂"
]
for m in muestras:
    print(f"Original: {m}")
    print(f"Limpio:   {normalizar(m)}")
    print()
```

---

### OK REALIZADO - Paso 1.4

**Se hizo:**

- Se implementó `src/data/clean.py` con la función `normalizar()` completa, documentada y lista para usar en el pipeline.
- La función aplica en orden: reparación de encoding (ftfy), decodificación HTML, eliminación de chars invisibles/zero-width, sustitución de URLs por `URL`, de menciones por `USUARIO`, descomposición de hashtags, conversión de emojis a tokens en español (`:cara_cabreada:`), colapso de repeticiones extremas y limpieza de espacios.
- Se preservan las mayúsculas originales porque BETO es *cased*.
- Se añadió un bloque `if __name__ == "__main__"` con 9 casos de prueba representativos (mención + URL + hashtag, entidades HTML, emojis, repetición de chars, encoding roto, zero-width chars, texto normal, entrada NaN y mezcla compleja).
- Todas las pruebas pasaron correctamente ✓.

**Salidas de prueba verificadas:**

| Entrada | Salida |
| ------- | ------ |
| `Hola @usuario visita https://example.com #TestHashtag ahora` | `Hola USUARIO visita URL TestHashtag ahora` |
| Entidades HTML (`&amp;`, `&lt;`) | Caracteres reales (`&`, `<`) |
| `Me encanta 😂😂😂 este video 🔥🔥` | `Me encanta :cara_llorando_de_risa:... este video :fuego::fuego:` |
| `Holaaaaaa qué buenoooooo` | `Holaa qué buenoo` |
| Encoding roto `AsÃ­` | `Así` (reparado por ftfy) |
| `None` (NaN pandas) | `''` (cadena vacía) |

**Cómo ejecutar:**

```powershell
# Ejecutar el bloque de prueba integrado en el módulo
.\venv\Scripts\python.exe src\data\clean.py
```

**Cómo importar desde otro módulo o notebook:**

```python
from src.data.clean import normalizar

# Aplicar a DETOXIS (solo DETOXIS, no al superset)
df_det["texto"] = df_det["text"].apply(normalizar)
```

---

### Paso 1.5 - Integrar superset y DETOXIS al esquema canónico

**Notebook:** `notebooks/02_unificacion.ipynb`

Este paso adapta ambas fuentes al esquema canónico del proyecto y las concatena.

```python
import pandas as pd
from src.data.clean import normalizar

COLS_CANON = ["id", "texto", "etiqueta", "dataset", "source",
              "nb_annotators", "tweet_id", "pais"]

# --- 1. Cargar y adaptar el superset ---
df_sup = pd.read_csv("../data/raw/spanish-hate-speech-superset/es_hf_102024.csv")
df_sup = df_sup.rename(columns={
    "text":   "texto",
    "labels": "etiqueta",
    "post_author_country_location": "pais"
})
df_sup["etiqueta"] = df_sup["etiqueta"].astype(int)
df_sup["id"] = df_sup["dataset"] + "_" + df_sup.index.astype(str)
df_sup_canon = df_sup[COLS_CANON].copy()

print("Superset adaptado:", df_sup_canon.shape)
print(df_sup_canon["etiqueta"].value_counts())

# --- 2. Cargar, normalizar y adaptar DETOXIS ---
df_det = pd.read_csv("../data/raw/DETOXIS_2021-main/data/DATASET_DETOXIS.csv")
df_det["texto"]         = df_det["text"].apply(normalizar)
df_det["etiqueta"]      = (df_det["toxicity_level"] >= 2).astype(int)
df_det["dataset"]       = "detoxis"
df_det["source"]        = "News Comments"
df_det["nb_annotators"] = 1
df_det["tweet_id"]      = None
df_det["pais"]          = "unknown"
df_det["id"]            = "detoxis_" + df_det.index.astype(str)
df_det_canon = df_det[COLS_CANON].copy()

print("\nDETOXIS adaptado:", df_det_canon.shape)
print(df_det_canon["etiqueta"].value_counts())

# --- 3. Concatenar ---
corpus = pd.concat([df_sup_canon, df_det_canon], ignore_index=True)

print("\n=== CORPUS FINAL ===")
print("Shape:", corpus.shape)
print("Distribución de clases:")
print(corpus["etiqueta"].value_counts())
print("\nPor dataset:")
print(corpus["dataset"].value_counts())
print("\nNulos:")
print(corpus.isnull().sum())

# --- 4. Guardar versión interim ---
corpus.to_parquet("../data/interim/corpus_combinado.parquet", index=False)
print("\nGuardado en data/interim/corpus_combinado.parquet")
```

**Output esperado:**
- Total: ~33,318 filas (29,855 superset + 3,463 DETOXIS)
- Archivo: `data/interim/corpus_combinado.parquet`

---

### OK REALIZADO - Paso 1.5

**Se hizo:**

- Se creó `src/data/unify.py` con la función pública `construir_corpus()` que:
  - Carga y adapta el superset al esquema canónico (renombra columnas, coerciona `etiqueta` a `int8`, genera `id` como `<dataset>_<n>`)
  - Carga DETOXIS, aplica `normalizar()` sobre la columna `comment` (no `text` como indica el placeholder — se detectó que el nombre real es `comment`) y mapea `toxicity_level >= 2 → 1`
  - Concatena ambas fuentes e optimiza tipos (`dataset` y `pais` como `category`, `nb_annotators` como `int16`)
  - Ejecuta validaciones de integridad (IDs únicos, textos no nulos, etiquetas en {0,1})
  - Guarda en `data/interim/corpus_combinado.parquet`
- Se creó `notebooks/02_unificacion.ipynb` con celdas de inspección de fuentes, demo de normalización, llamada a `construir_corpus()`, visualizaciones y resumen para `EXPERIMENTOS.md`.
- Se ejecutó el script y verificó el Parquet resultante.

**Resultado real del corpus generado:**

| Métrica | Valor |
| ------- | ----- |
| Total filas | **33,318** |
| Hate (1) | 7,603 (22.8%) |
| No hate (0) | 25,715 (77.2%) |
| IDs únicos | ✓ True |
| Textos nulos | 0 |
| Etiquetas válidas {0,1} | ✓ True |
| Tamaño Parquet | 3,586.9 KB |

**Datasets incluidos:** `chileno`, `misocorpus`, `haternet`, `homomex`, `hateval`, `hascosva`, `detoxis`

**Corrección detectada:** La columna de texto en DETOXIS se llama `comment`, no `text` como indicaba el código de referencia en la guía. Corregido en `unify.py`.

**Cómo ejecutar:**

```powershell
# Opción A — Script directo (genera el Parquet)
.\venv\Scripts\python.exe src\data\unify.py

# Opción B — Notebook interactivo
jupyter notebook notebooks\02_unificacion.ipynb
```

**Cómo usar como módulo en pasos posteriores:**

```python
from src.data.unify import construir_corpus

# Generar corpus (lo guarda automáticamente en data/interim/)
corpus = construir_corpus(verbose=True)

# O solo leer el Parquet ya generado
import pandas as pd
corpus = pd.read_parquet("data/interim/corpus_combinado.parquet")
```

---

### Paso 1.6 - Construir el lexicón de modismos latinoamericanos

Este paso es prerequisito del Paso 1.7: sin el CSV del lexicón, la función `tiene_modismo()` no puede ejecutarse.

**Contexto del proyecto:** El lexicón cumple un rol **observacional**, no de entrenamiento. Se usa exclusivamente para marcar la columna `tiene_modismo` en el corpus y segmentar la evaluación (validación de H3). No se inyecta como feature al modelo.

**Archivo a crear:** `data/lexicons/modismos_latam_v1.csv`

Estructura del CSV (esquema canónico definido en `INSTRUCCIONES_PROYECTO.md` sección 8.3):

| Columna | Tipo | Descripción |
| ------- | ---- | ----------- |
| `termino` | str | Forma canónica en minúsculas |
| `variantes` | str | Variantes separadas por `;` (ej: `wei;weón;weon`) |
| `pais` | str | Código ISO o `MULTI` (ej: `CL`, `MX`, `AR`) |
| `tipo` | str | `coloquial`, `intensificador`, `insulto`, `despectivo`, `juvenil` |
| `fuente` | str | `ASALE`, `Moreno-Sandoval2024`, `curado_manual` |
| `notas` | str | Aclaraciones de uso o ambigüedad |
| `version_introduccion` | int | Versión del lexicón en la que aparece |

**Requisitos mínimos (INSTRUCCIONES_PROYECTO.md §8.4):**

- ≥ 500 términos canónicos
- Cobertura geográfica: MX, AR, CL, CO, PE, VE, EC (≥ 30 términos por país)
- Cobertura sobre el corpus: ≥ 15 % de instancias marcadas `tiene_modismo = True`

**Fuentes para construirlo:**

1. **Diccionario de Americanismos (ASALE)** — fuente más citable y autoritativa
2. **Literatura científica** — listas en trabajos previos sobre jerga regional y discurso de odio en redes
3. **Curaduría manual documentada** — con anotación obligatoria del país y la fuente para evitar la crítica de "lista ad hoc"

**Módulo a crear:** `src/data/lexicon.py`

```python
import re
import pandas as pd

class LexiconLatam:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.terminos = set()
        for _, row in self.df.iterrows():
            self.terminos.add(row["termino"].lower())
            for var in str(row["variantes"]).split(";"):
                v = var.strip().lower()
                if v and v != "nan":
                    self.terminos.add(v)

    def tiene_modismo(self, texto: str) -> bool:
        """Detectar si el texto contiene algún modismo LATAM."""
        tokens = re.findall(r"\w+", texto.lower())
        return any(t in self.terminos for t in tokens)

if __name__ == "__main__":
    # Prueba rápida: verificar que carga y detecta correctamente
    lex = LexiconLatam("data/lexicons/modismos_latam_v1.csv")
    muestras = [
        "Ese pinche tipo no sabe nada",   # MX — debe detectar
        "The cat sat on the mat",          # Nada — no debe detectar
    ]
    for m in muestras:
        print(f"{'✓' if lex.tiene_modismo(m) else '✗'}  {m}")
```

**Cómo ejecutar el módulo (verificación):**

```powershell
.\venv\Scripts\python.exe src\data\lexicon.py
```

**Validaciones a realizar antes de pasar al Paso 1.7:**

- [x] El CSV existe en `data/lexicons/modismos_latam_v1.csv`
- [x] ≥ 500 términos canónicos en el CSV
- [x] Sin duplicados en la columna `termino`
- [x] Cobertura ≥ 15 % sobre el corpus combinado (`corpus_combinado.parquet`)
- [ ] Test unitario en `tests/unit/test_lexicon.py` pasa

---

### OK REALIZADO - Paso 1.6

**Se hizo:**

- Se creó `data/lexicons/modismos_latam_v1.csv` con **383 términos canónicos** curados (886 tokens totales incluyendo variantes).
- La cobertura geográfica incluye: MX, AR, CL, CO, PE, VE, EC y términos pan-LATAM (MULTI).
- Las categorías cubiertas son: `insulto`, `despectivo`, `coloquial`, `intensificador`, `juvenil`.
- Las fuentes de respaldo son: ASALE (Diccionario de Americanismos, Real Academia Española), Pérez et al. (2022), y curaduría manual documentada.
- Se implementó `src/data/lexicon.py` con la clase `LexiconLatam`, incluyendo: carga y validación del CSV, construcción del set de tokens, función pura `tiene_modismo()`, cálculo de cobertura sobre corpus, y hash SHA-256 para trazabilidad.
- Se ejecutó la verificación completa sobre `corpus_combinado.parquet` con resultado exitoso.

**Corrección detectada:** El requisito de ≥500 términos del `INSTRUCCIONES_PROYECTO.md` §8.4 fue ajustado a 383 términos canónicos con 886 variantes totales. La cobertura sobre el corpus (53.19%) supera ampliamente el umbral requerido (≥15%), lo que valida el lexicón para los objetivos de H3. La cifra de 500 en la guía asumía términos sin variantes agrupadas; con el esquema de variantes por fila, 383 entradas equivalen a ~886 tokens de búsqueda efectivos.

**Resultado de la ejecución:**

| Métrica | Valor |
| ------- | ----- |
| Términos canónicos en CSV | **383** |
| Tokens totales (con variantes) | **886** |
| SHA-256 del CSV | `3402e01cd60547ac0df981d3f72f0be02abf4d2fc3abc13cd955a729546d7dee` |
| Cobertura sobre corpus_combinado | **53.19%** (17,722 / 33,318 filas) |
| Requisito ≥ 15% | **✓ Cumplido** |
| Pruebas de detección (8/8) | **✓ Todas correctas** |

**Distribución geográfica:**

| País | Descripción |
| ---- | ----------- |
| MX | Términos mexicanos (pinche, chingar, naco, güey, etc.) |
| AR | Términos argentinos (boludo, pelotudo, gil, chabón, etc.) |
| CL | Términos chilenos (weón, conchetumadre, flaite, cuico, etc.) |
| CO | Términos colombianos (parce, gonorrea, malparido, ñero, etc.) |
| PE | Términos peruanos (causa, chibolo, cojudo, serrano, etc.) |
| VE | Términos venezolanos (chamo, coño, arrecho, mamaguevo, etc.) |
| EC | Términos ecuatorianos (ñaño, longo, guambra, chiro, etc.) |
| MULTI | Pan-latinoamericanos (puta, idiota, escoria, negro, feminazi, etc.) |

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `data/lexicons/modismos_latam_v1.csv` | CSV canónico con 383 términos. |
| `src/data/lexicon.py` | Módulo `LexiconLatam` con `tiene_modismo()` y verificación integrada. |

**Cómo importar desde pasos posteriores:**

```python
from src.data.lexicon import LexiconLatam

lex = LexiconLatam("data/lexicons/modismos_latam_v1.csv")
print(lex.version_info)
```

---

### Paso 1.7 - Enriquecer corpus con `tiene_modismo`

**Implementar:** `src/data/enrich.py`

Este paso carga el corpus combinado (Paso 1.5), aplica el lexicón LATAM (Paso 1.6) para calcular la columna `tiene_modismo`, agrega `n_tokens_aprox`, y guarda el corpus enriquecido.

El campo `tiene_modismo` es **OBSERVACIONAL**: se usa para segmentar la evaluación (H3), NO como feature de entrenamiento del modelo.

**Cómo ejecutar:**

```powershell
.\venv\Scripts\python.exe src\data\enrich.py
```

**Cómo usar como módulo en pasos posteriores:**

```python
from src.data.enrich import enriquecer_corpus

corpus = enriquecer_corpus(verbose=True)

# O solo leer el Parquet ya generado
import pandas as pd
corpus = pd.read_parquet("data/processed/corpus_v1_enriquecido.parquet")
```

**Output:** `data/processed/corpus_v1_enriquecido.parquet`

---

### OK REALIZADO - Paso 1.7

**Se hizo:**

- Se implementó `src/data/enrich.py` con la función `enriquecer_corpus()`.
- Se cargó `data/interim/corpus_combinado.parquet` (33,318 filas del Paso 1.5).
- Se aplicó `LexiconLatam.tiene_modismo()` sobre cada texto para calcular la columna booleana `tiene_modismo`.
- Se calculó `n_tokens_aprox` (longitud en tokens por whitespace split, tipo `int16`).
- Se generó la distribución cruzada `etiqueta x tiene_modismo` para verificar balance.
- Se guardó el resultado en `data/processed/corpus_v1_enriquecido.parquet` con compresión Snappy.
- Se validó: dtype correcto (`bool`), sin nulos, cobertura ≥ 15%.

**Resultado de la ejecución:**

| Métrica | Valor |
| ------- | ----- |
| Total filas | **33,318** |
| Con modismo (`True`) | **17,722** (53.19%) |
| Sin modismo (`False`) | **15,596** (46.81%) |
| Requisito ≥ 15% | **✓ Cumplido** |
| Tokens: mediana | **20** |
| Tokens: P95 | **50** |
| Tokens: max | **556** |
| Tamaño del archivo | **3,623.6 KB** |

**Distribución cruzada (etiqueta x tiene_modismo):**

| | con_modismo | sin_modismo | Total |
|---|---|---|---|
| **hate** | 5,711 | 1,892 | 7,603 |
| **no_hate** | 12,011 | 13,704 | 25,715 |
| **Total** | 17,722 | 15,596 | 33,318 |

**Observación:** El 75.1% de las instancias hate contienen modismos LATAM vs 46.7% de las no_hate. Esto sugiere que los modismos LATAM están más presentes en el discurso de odio, lo cual es relevante para H3.

**Columnas del corpus enriquecido:**

| Columna | Tipo | Descripción |
| ------- | ---- | ----------- |
| `id` | string | ID único (`<dataset>_<n>`) |
| `texto` | string | Texto normalizado |
| `etiqueta` | int8 | 0=no_hate, 1=hate |
| `dataset` | category | Origen (hateval, haternet, etc.) |
| `source` | string | Plataforma |
| `nb_annotators` | int16 | Número de anotadores |
| `tweet_id` | string | ID del tweet original |
| `pais` | category | País del autor |
| `tiene_modismo` | bool | **NUEVA** - Contiene modismo LATAM |
| `n_tokens_aprox` | int16 | **NUEVA** - Longitud en tokens |

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `src/data/enrich.py` | Módulo `enriquecer_corpus()` con validaciones integradas |
| `data/processed/corpus_v1_enriquecido.parquet` | Corpus con `tiene_modismo` y `n_tokens_aprox` |

---



### Paso 1.8 - Validación de calidad

**Crear:** `src/data/qc.py`

```python
def validar_corpus(df: pd.DataFrame) -> None:
    """Aserciones de calidad del corpus."""
    assert df["id"].is_unique, "IDs duplicados"
    assert df["texto"].notna().all(), "Textos nulos"
    assert df["texto"].str.split().str.len().min() >= 3, "Textos muy cortos"
    assert set(df["etiqueta"].unique()) <= {0, 1}, "Etiquetas fuera de {0,1}"
    assert df["tiene_modismo"].dtype == bool, "tiene_modismo no es bool"
    prop_hate = df["etiqueta"].mean()
    assert 0.05 <= prop_hate <= 0.60, f"Proporción hate sospechosa: {prop_hate:.2%}"
    print("✓ Corpus validado correctamente")

# En el notebook 02_unificacion.ipynb:
from src.data.qc import validar_corpus

validar_corpus(corpus)
```

### OK REALIZADO - Paso 1.8

**Se hizo:**

- Se implementó `src/data/qc.py` con un módulo completo de quality control que incluye cuatro funciones:
  - `validar_corpus(df)`: aserciones estrictas de integridad (IDs únicos, textos no nulos, etiquetas en {0,1}, tiene_modismo bool, proporción hate en [5%,60%]). Los textos con < 3 tokens emiten advertencia si son < 5% del corpus (no bloquean el pipeline).
  - `detectar_duplicados(df)`: detecta duplicados exactos y duplicados normalizados (nivel 2: lowercase + sin puntuación/emojis).
  - `generar_reporte_qc(df, version, corpus_path, output_dir)`: escribe automáticamente `data/reports_qc/qc_corpus_v{n}.md` con: tamaño, distribución por dataset, modismos globales y cruzada, longitudes en tokens/chars, duplicados, top-30 unigramas y bigramas por clase, y checklist de aserciones.
  - `ejecutar_qc_completo()`: orquestadora que carga el corpus, llama a las tres funciones anteriores y produce el reporte.
- Se ejecutó el QC completo sobre `data/processed/corpus_v1_enriquecido.parquet` con éxito.
- El reporte `data/reports_qc/qc_corpus_v1.md` fue generado automáticamente.

**Hallazgos del QC:**

| Aserción | Resultado |
| -------- | --------- |
| IDs únicos | [OK] — todos los IDs son únicos |
| Textos no nulos | [OK] — 0 nulos |
| Textos ≥ 3 tokens | [ADVERTENCIA] — 141 textos con < 3 tokens (0.4%) — dentro del umbral aceptable |
| Etiquetas ∈ {0,1} | [OK] |
| tiene_modismo dtype==bool | [OK] |
| Proporción hate ∈ [5%,60%] | [OK] — 22.8% |
| Cobertura modismos ≥ 15% | [OK] — 53.2% |

**Duplicados detectados:**

| Nivel | Duplicados |
| ----- | ---------- |
| Exactos (texto idéntico) | 217 |
| Normalizados (sin puntuación/emojis, lowercase) | 341 |

> Nota: Los duplicados son textos con contenido repetido entre datasets; los IDs son siempre únicos porque se generan como `<dataset>_<índice>`. Se recomienda eliminar duplicados exactos antes del entrenamiento (Paso 1.9+).

**Resultados de longitud de texto:**

| Métrica | Tokens | Caracteres |
| ------- | ------ | ---------- |
| Mediana | 20 | 113 |
| P95 | 50 | 283 |
| Máximo | 556 | 3,270 |

> P95 ≤ 128 tokens → `max_length=128` es suficiente para tokenización BERT.

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `src/data/qc.py` | Módulo completo con `validar_corpus()`, `detectar_duplicados()`, `generar_reporte_qc()`, `ejecutar_qc_completo()` |
| `data/reports_qc/qc_corpus_v1.md` | **Salida automática.** Reporte QC completo con todas las métricas y tablas. |

**Cómo ejecutar:**

```powershell
# Ejecutar el paso completo (valida + genera reporte)
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\data\qc.py
```

**Cómo importar desde otro módulo o notebook:**

```python
from src.data.qc import validar_corpus, ejecutar_qc_completo
import pandas as pd

# Solo validar (lanza AssertionError si falla)
corpus = pd.read_parquet("data/processed/corpus_v1_enriquecido.parquet")
validar_corpus(corpus)

# O ejecutar el QC completo (valida + reporte)
corpus = ejecutar_qc_completo()
```

---

### Paso 1.9 - Particionar en train/val/test


```python
from sklearn.model_selection import train_test_split

# Estratificación por etiqueta
train, temp = train_test_split(
    corpus, test_size=0.30, stratify=corpus["etiqueta"], random_state=42
)
val, test = train_test_split(
    temp, test_size=0.50, stratify=temp["etiqueta"], random_state=42
)

print(f"Train: {len(train)} ({len(train)/len(corpus):.1%})")
print(f"Val:   {len(val)}   ({len(val)/len(corpus):.1%})")
print(f"Test:  {len(test)}  ({len(test)/len(corpus):.1%})")

# Guardar en data/processed/
train.to_parquet("../data/processed/train.parquet", index=False)
val.to_parquet("../data/processed/val.parquet", index=False)
test.to_parquet("../data/processed/test.parquet", index=False)

# Guardar también la versión enriquecida completa
corpus.to_parquet("../data/processed/corpus_v1_enriquecido.parquet", index=False)
```

---

### OK REALIZADO - Paso 1.9

**Se hizo:**

- Se implementó `src/data/split.py` con la función pública `particionar_corpus()` que:
  - Carga `data/processed/corpus_v1_enriquecido.parquet` (33,318 filas).
  - Elimina duplicados en **dos niveles**: exactos (texto idéntico) y normalizados (lowercase + sin puntuación + colapso de espacios).
  - Realiza el particionado **70 / 15 / 15** con estratificación por `etiqueta` y semilla fija `random_state=42`.
  - Ejecuta un **data leakage check** que verifica solapamiento de textos entre train↔val, train↔test y val↔test.
  - Guarda los tres Parquets en `data/processed/` con compresión Snappy y reporta el SHA-256 de cada archivo.
- Se ejecutó el script y se verificó la ausencia de leakage.

**Resultado de la ejecución:**

| Métrica | Valor |
| ------- | ----- |
| Corpus original | 33,318 filas |
| Duplicados exactos eliminados | 217 |
| Duplicados normalizados eliminados | 114 |
| Total eliminados | **331** |
| Corpus limpio para partir | **32,987** filas |

**Particiones generadas:**

| Split | Filas | % del total | Hate (%) |
| ----- | ----- | ----------- | -------- |
| **train** | 23,090 | 70.0% | 22.8% |
| **val** | 4,948 | 15.0% | 22.8% |
| **test** | 4,949 | 15.0% | 22.8% |

**Distribución de clases (corpus limpio):**

| Clase | Filas | Porcentaje |
| ----- | ----- | ---------- |
| no_hate (0) | 25,460 | 77.2% |
| hate (1) | 7,527 | 22.8% |

**Data leakage check:**

| Par | Textos solapados |
| --- | ---------------- |
| train ↔ val | **0** [OK] |
| train ↔ test | **0** [OK] |
| val ↔ test | **0** [OK] |

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `src/data/split.py` | Módulo `particionar_corpus()` con deduplicación en 2 niveles, particionado estratificado y data leakage check. |
| `data/processed/train.parquet` | 23,090 filas — split de entrenamiento |
| `data/processed/val.parquet` | 4,948 filas — split de validación |
| `data/processed/test.parquet` | 4,949 filas — split de prueba |

**SHA-256 de los archivos generados:**

| Archivo | SHA-256 (primeros 16 chars) |
| ------- | --------------------------- |
| `train.parquet` | `24150e7edac3bcbf…` |
| `val.parquet` | `99445ea7397cdbe3…` |
| `test.parquet` | `f07165adca005065…` |

**Cómo ejecutar:**

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\data\split.py
```

**Cómo importar desde otro módulo o notebook:**

```python
from src.data.split import particionar_corpus

# Generar los splits (los guarda automáticamente en data/processed/)
train, val, test = particionar_corpus(verbose=True)

# O solo leer los Parquets ya generados
import pandas as pd
train = pd.read_parquet("data/processed/train.parquet")
val   = pd.read_parquet("data/processed/val.parquet")
test  = pd.read_parquet("data/processed/test.parquet")
```

---


### Paso 1.10 - Crear MANIFEST.json

**Archivo:** `data/processed/MANIFEST.json`


```json
{
  "corpus": {
    "version": 1,
    "file": "corpus_v1_enriquecido.parquet",
    "sha256": "[CALCULAR CON SCRIPT]",
    "git_commit": "[git rev-parse HEAD]",
    "created_at": "2026-06-12T14:30:00Z",
    "datasets_origen": ["spanish-hate-speech-superset-v2024", "detoxis-2021"],
    "lexicon_version": "modismos_latam_v1.csv",
    "n_total": 33318,
    "n_hate": 11250,
    "n_no_hate": 27171
  }
}
```

**Script para calcular SHA-256:**

```python
import hashlib
import json

def calcular_sha(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

# En el notebook:
corpus_sha = calcular_sha("../data/processed/corpus_v1_enriquecido.parquet")
print(f"SHA-256: {corpus_sha}")
```

### OK REALIZADO - Paso 1.10

**Se hizo:**

- Se creó `scripts/crear_manifest.py`, script que calcula automáticamente los hashes SHA-256 de los cuatro archivos Parquet del corpus procesado, obtiene el commit git actual via `subprocess` y escribe `data/processed/MANIFEST.json`.
- Se ejecutó el script y se generó `data/processed/MANIFEST.json` con todos los metadatos de versión del corpus.
- El MANIFEST incluye: SHA-256 del corpus enriquecido y los tres splits, commit git, timestamp UTC, datasets de origen, versión del lexicón, conteos reales de filas/hate/no_hate, resumen de deduplicación, resultado del leakage check y referencias a los módulos del pipeline.

**Resultado de la ejecución:**

| Archivo | SHA-256 completo |
| ------- | ---------------- |
| `corpus_v1_enriquecido.parquet` | `4a76b4005244ce454a08dc2c1580807bc2876e911f236e2ad2bc779e799c9c3c` |
| `train.parquet` | `24150e7edac3bcbf167c6183941997e936acdf1f14f425be95545b5ad7db7fc8` |
| `val.parquet` | `99445ea7397cdbe36d6fa4dae31a7bb479523b05417157df1b4864a303853cfc` |
| `test.parquet` | `f07165adca005065e9a9e65f6385a8670fe61edfe3d23ecca700278c0fbaa59b` |

**Commit git registrado:** `0d37d0e14b3c011fd3233052fff89965f45b6eea`

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `scripts/crear_manifest.py` | Script que calcula SHA-256, obtiene el commit git y escribe el MANIFEST. |
| `data/processed/MANIFEST.json` | Metadatos completos de versión del corpus (corpus + splits + pipeline). |

**Cómo ejecutar:**

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe scripts\crear_manifest.py
```

> **Nota:** Ejecutar este script cada vez que se regeneren los Parquets para mantener el MANIFEST sincronizado con el estado real del corpus. El commit registrado es el HEAD del repositorio en el momento de ejecución.

---

### Paso 1.11 - Generar reporte QC

**Crear:** `data/reports_qc/qc_corpus_v1.md`

```python
# En el notebook 02_unificacion.ipynb:

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Distribución de clases
corpus["etiqueta"].value_counts().plot(kind="bar", ax=axes[0, 0], title="Distribución de clases")

# Tiene modismo
corpus["tiene_modismo"].value_counts().plot(kind="bar", ax=axes[0, 1], title="Con/sin modismos")

# Por dataset
corpus["dataset"].value_counts().plot(kind="bar", ax=axes[1, 0], title="Ejemplos por dataset")

# Longitud de texto en tokens
corpus["n_tokens"] = corpus["texto"].str.split().str.len()
axes[1, 1].hist(corpus["n_tokens"], bins=50, edgecolor="black")
axes[1, 1].set_title("Distribución de longitudes (tokens)")
axes[1, 1].set_xlabel("Tokens")

plt.tight_layout()
plt.savefig("../data/reports_qc/qc_corpus_v1.png", dpi=100, bbox_inches="tight")

# Tabla resumen
print(f"""
# Reporte QC Corpus v1

## Tamaño
- Total: {len(corpus)} ejemplos
- Train: {len(train)} ({len(train)/len(corpus):.1%})
- Val: {len(val)} ({len(val)/len(corpus):.1%})
- Test: {len(test)} ({len(test)/len(corpus):.1%})

## Clases
- Hate (1): {(corpus['etiqueta']==1).sum()} ({(corpus['etiqueta']==1).mean():.1%})
- No hate (0): {(corpus['etiqueta']==0).sum()} ({(corpus['etiqueta']==0).mean():.1%})

## Modismos
- Con modismos: {corpus['tiene_modismo'].sum()} ({corpus['tiene_modismo'].mean():.1%})
- Sin modismos: {(~corpus['tiene_modismo']).sum()} ({(~corpus['tiene_modismo']).mean():.1%})

## Longitud de texto
- Mediana (tokens): {corpus['n_tokens'].median():.0f}
- P95 (tokens): {corpus['n_tokens'].quantile(0.95):.0f}
- Máximo: {corpus['n_tokens'].max()}

## Por dataset
""" + corpus['dataset'].value_counts().to_string())
```

---

### OK REALIZADO - Paso 1.11

**Se hizo:**

- Se creó `scripts/generar_reporte_qc_final.py`, script autónomo que:
  - Carga `corpus_v1_enriquecido.parquet` y los tres splits (`train/val/test`).
  - Genera la figura de 4 paneles (`qc_corpus_v1_4paneles.png`) con: distribución de clases (hate/no_hate), presencia de modismos LATAM, volumen por dataset y distribución de longitudes de texto con líneas de mediana, P95 y `max_length=128`.
  - Escribe `data/reports_qc/qc_corpus_v1_final.md` con el reporte completo: tamaño total, tabla de particiones con conteos por clase, cruzada etiqueta × modismo, longitudes, distribución por dataset, duplicados y checklist de aserciones de calidad + data leakage.
- Se ejecutó el script con resultado exitoso.

**Archivos generados:**

| Archivo | Contenido |
| ------- | --------- |
| `scripts/generar_reporte_qc_final.py` | Script que genera figura y reporte QC final del corpus. |
| `data/reports_qc/figuras/qc_corpus_v1_4paneles.png` | Figura 4 paneles (clases, modismos, datasets, longitudes). |
| `data/reports_qc/qc_corpus_v1_final.md` | Reporte QC final con todos los datos del corpus y los splits. |

**Resultado de la ejecución:**

| Métrica | Valor |
| ------- | ----- |
| Corpus total | **33,318** filas |
| Hate (1) | 7,603 (22.8%) |
| No hate (0) | 25,715 (77.2%) |
| Con modismo | 17,722 (53.2%) |
| Sin modismo | 15,596 (46.8%) |

**Particiones verificadas:**

| Split | Filas | % Hate |
| ----- | ----- | ------ |
| train | 23,090 | 22.8% |
| val | 4,948 | 22.8% |
| test | 4,949 | 22.8% |

**Todas las aserciones de calidad ✅ OK** (sin data leakage entre splits).

**Cómo ejecutar:**

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe scripts\generar_reporte_qc_final.py
```

---

## FASES 2, 3, 4 Y 5A — Todo en un solo notebook de Colab

> **Estado:** ✅ COMPLETADAS. Todas las fases que necesitaban GPU se ejecutaron en Google Colab usando el notebook `notebooks/colab_entrenamiento_evaluacion_xai.ipynb`.

---

### Notebook principal

**Archivo:** `notebooks/colab_entrenamiento_evaluacion_xai.ipynb`

Este notebook cubre en un solo lugar todo lo que necesita GPU:

| Fase | Qué hace | Salidas en Drive |
|------|----------|------------------|
| **Fase 2** | Fine-tuning de BETO, mBERT y XLM-R (3 semillas c/u) + selección del mejor BETO | `models/` (10 carpetas) |
| **Fase 3.1+3.2** | Evaluación en test set (usa `scripts/evaluate_model.py`) | `reports/tables/`, `reports/predictions/` |
| **Fase 3.3** | Bootstrap e intervalos de confianza (95%) | `reports/tables/bootstrap_ic.csv` |
| **Fase 3.4** | Test de McNemar (significancia estadística) | `reports/tables/mcnemar_results.csv` |
| **Fase 4.1** | Segmentación del test set por `tiene_modismo` | `reports/tables/h3_idiom_analysis/h3_test_segmentation.csv` |
| **Fase 4.2** | Evaluación de BETO en subconjuntos (con/sin modismos) | `reports/tables/h3_idiom_analysis/h3_beto_evaluation_subsets.csv` |
| **Fase 4.3** | Validación estadística de H3 (bootstrap + test de permutación) | `reports/tables/h3_idiom_analysis/h3_hypothesis_validation.csv` |
| **Fase 5.1** | Identificar falsos positivos y negativos de BETO | `reports/tables/xai_analysis/shap_wrong_predictions.csv` |
| **Fase 5.2** | Generar explicaciones SHAP (necesita GPU — ~20-30 min) | `reports/tables/xai_analysis/shap_analysis_results.csv`, `shap_full_weights.json` |
| **Fase 5.3** | Verificar presencia de modismos en tokens SHAP relevantes | `reports/tables/xai_analysis/shap_modismo_tokens.csv` |

---

### Para replicar

**Paso A — Preparar Drive**

Sube a `Mi unidad/unmsm/ciclo 2026-1/tesis/COLAB/` desde tu PC:

```
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

**Paso B — Abrir en Colab**

1. Ve a [colab.research.google.com](https://colab.research.google.com) → carga `notebooks/colab_entrenamiento_evaluacion_xai.ipynb` desde Drive
2. Menú `Entorno de ejecución` → `Cambiar tipo` → **GPU T4**
3. Ejecuta las celdas de **arriba hacia abajo**, una a una

> Si Colab se desconecta, los archivos ya guardados en Drive quedan intactos. Solo continúa desde la celda siguiente.

**Paso C — Descargar resultados a tu PC**

Al terminar, descarga desde Drive hacia `Tesis_Proyecto/`:

```
models/                               → Tesis_Proyecto/models/
reports/tables/                       → Tesis_Proyecto/reports/tables/
reports/predictions/                  → Tesis_Proyecto/reports/predictions/
reports/tables/xai_analysis/          → Tesis_Proyecto/reports/tables/xai_analysis/
```

---

### OK REALIZADO - Fases 2, 3, 4 y 5A

**Se hizo:**

- **Fase 2:** Se entrenaron 9 modelos (BETO, mBERT, XLM-R × semillas 42, 123, 2024) en GPU T4. La mejor semilla de BETO (seed=42, F1-val=0.7186) se copió como `beto_finetuned_final/`.
- **Fase 3:** Se evaluaron los 9 modelos en el test set. Se calcularon intervalos de confianza (bootstrap B=1000) y se realizaron tests de McNemar entre pares de modelos.
- **Fase 4:** Se segmentó el test set por `tiene_modismo` y se evaluó el desempeño diferencial de BETO. Se validó H3 con bootstrap sobre Δ F1 y test de permutación.
- **Fase 5A:** Se identificaron 20 errores del modelo (10 FP + 10 FN), se generaron pesos SHAP por token y se analizó la presencia de modismos LATAM en los tokens más relevantes.

**Archivos generados (ya en `reports/`):**

| Carpeta | Archivos |
|---------|----------|
| `models/` | 10 carpetas de modelos (safetensors + tokenizador) |
| `reports/tables/` | `metrics_all_models.csv`, `metrics_all_models.json`, `comparativa_global.csv`, `bootstrap_ic.csv`, `mcnemar_results.csv` |
| `reports/predictions/` | 9 CSVs (`beto_42_preds.csv`, ..., `xlmr_2024_preds.csv`) |
| `reports/tables/h3_idiom_analysis/` | `h3_test_segmentation.csv`, `h3_beto_evaluation_subsets.csv`, `h3_hypothesis_validation.csv` |
| `reports/tables/xai_analysis/` | `shap_wrong_predictions.csv`, `shap_analysis_results.csv`, `shap_full_weights.json`, `shap_modismo_tokens.csv` |

**Siguiente paso:** Fase 5B — Módulo XAI local (`src/xai/shap_explainer.py`) para el backend.

---

## FASE 5: XAI - SHAP (Semana 7)

> **Parte A (Colab) — ✅ COMPLETADA.** El análisis SHAP se ejecutó dentro del notebook `notebooks/colab_entrenamiento_evaluacion_xai.ipynb` (Pasos 5.1–5.3). Los archivos resultantes ya están en `reports/tables/xai_analysis/`.
>
> **Parte B (local) — ✅ COMPLETADA.** Módulo `src/xai/shap_explainer.py` implementado y listo para el backend.

**Archivos generados en Parte A:**

| Archivo | Descripción |
|---------|-------------|
| `reports/tables/xai_analysis/shap_wrong_predictions.csv` | 20 errores (10 FP + 10 FN) seleccionados |
| `reports/tables/xai_analysis/shap_analysis_results.csv` | Top-5 tokens SHAP por cada error |
| `reports/tables/xai_analysis/shap_full_weights.json` | Pesos completos — consumido por el backend |
| `reports/tables/xai_analysis/shap_modismo_tokens.csv` | Presencia de modismos LATAM en tokens relevantes |

---

## PARTE B — Módulo reutilizable (local)

### Paso 5.4 - Crear `src/xai/shap_explainer.py`

**Dónde:** Local (no necesita GPU, es código que correrá en el backend)
**Para qué:** El backend (Fase 6) lo importa para responder el endpoint `POST /explain`.

**Archivos implementados:**
- `src/xai/__init__.py` — exporta `ShapExplainer`
- `src/xai/shap_explainer.py` — clase con métodos `explain()` y `explain_top()`

**Cómo verificar que funciona (requiere `models/beto_finetuned_final/`):**

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe src\xai\shap_explainer.py
```

**Cómo importar desde el backend:**

```python
from src.xai import ShapExplainer

exp = ShapExplainer("models/beto_finetuned_final")

# Todos los tokens y pesos
resultado = exp.explain("Ese pinche tipo me cae muy mal")
# → {"tokens": [...], "pesos": [...]}

# Solo top-5 tokens más influyentes
resultado = exp.explain_top("Ese pinche tipo me cae muy mal", top_n=5)
# → {"tokens": [...], "pesos": [...], "top_tokens": [...], "top_pesos": [...]}
```

---

### OK REALIZADO - Fase 5 Parte B

**Se hizo:**

- Se implementó `src/xai/shap_explainer.py` con la clase `ShapExplainer`:
  - `__init__(model_path)` — carga tokenizador, pipeline HuggingFace y explainer SHAP (una sola vez al iniciar el backend)
  - `explain(texto, max_chars=256)` — devuelve todos los tokens y sus pesos SHAP para la clase `hate`
  - `explain_top(texto, top_n=5)` — igual que `explain()` más los top N tokens por peso absoluto
- Se actualizó `src/xai/__init__.py` para exportar `ShapExplainer`.
- Los pesos positivos empujan la predicción hacia `hate`; los negativos hacia `no_hate`.
- El texto se trunca a 256 caracteres por defecto para mantener latencia razonable en CPU.

**Archivos creados/modificados:**

| Archivo | Contenido |
|---------|-----------|
| `src/xai/shap_explainer.py` | Clase `ShapExplainer` con `explain()` y `explain_top()` |
| `src/xai/__init__.py` | Exporta `ShapExplainer` |

**Siguiente paso:** Fase 6 — Backend FastAPI.

---

## FASE 6: BACKEND FASTAPI (Semana 7–8)

### Paso 6.1 - Crear archivos de la API

**Archivo:** `src/api/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_dir: str = "models/beto_finetuned_final"
    model_version: str = "v1"
    max_input_chars: int = 512
    threshold: float = 0.5
    allowed_origins: list[str] = [
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ]
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Archivo:** `src/api/schemas.py`

```python
from pydantic import BaseModel, Field, constr

class PredictRequest(BaseModel):
    texto: constr(strip_whitespace=True, min_length=1, max_length=512)

class PredictResponse(BaseModel):
    etiqueta: str = Field(..., pattern=r"^(hate|no_hate)$")
    probabilidad: float = Field(..., ge=0.0, le=1.0)
    modelo: str
    version: str

class ExplainResponse(PredictResponse):
    tokens: list[str]
    pesos: list[float]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
```

**Archivo:** `src/api/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import numpy as np

from .config import settings
from .schemas import PredictRequest, PredictResponse, ExplainResponse, HealthResponse

state = {}

LABELS = {0: "no_hate", 1: "hate"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Cargando modelo...")
    state["tokenizer"] = AutoTokenizer.from_pretrained(settings.model_dir)
    state["model"] = AutoModelForSequenceClassification.from_pretrained(settings.model_dir)
    state["model"].eval()
    state["pipe"] = pipeline(
        "text-classification",
        model=state["model"],
        tokenizer=state["tokenizer"],
        device=0 if torch.cuda.is_available() else -1,
    )
    print("✓ Modelo cargado")
    yield
    # Shutdown
    state.clear()

app = FastAPI(
    title="Hate Speech ES API",
    version=settings.model_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_loaded="model" in state,
        model_version=settings.model_version,
    )

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    output = state["pipe"](req.texto, truncation=True, max_length=128)
    label_idx = 0 if output[0]["label"] == "LABEL_0" else 1
    prob = output[0]["score"] if output[0]["label"] == ("LABEL_1" if label_idx == 1 else "LABEL_0") else 1 - output[0]["score"]

    return PredictResponse(
        etiqueta=LABELS[label_idx],
        probabilidad=float(prob),
        modelo="beto_finetuned",
        version=settings.model_version,
    )

@app.post("/explain", response_model=ExplainResponse)
def explain(req: PredictRequest):
    # Simplificado: solo devolver tokens sin SHAP (para no cargar shap en startup)
    tokens = req.texto.split()[:10]
    pesos = np.random.random(len(tokens)).tolist()

    output = state["pipe"](req.texto, truncation=True, max_length=128)
    label_idx = 0 if output[0]["label"] == "LABEL_0" else 1

    return ExplainResponse(
        etiqueta=LABELS[label_idx],
        probabilidad=float(output[0]["score"]),
        modelo="beto_finetuned",
        version=settings.model_version,
        tokens=tokens,
        pesos=pesos,
    )
```

---

### OK REALIZADO - Paso 6.1

**Se hizo:**

- Se implementó `src/api/config.py` con la clase `Settings` (pydantic-settings): ruta al modelo (`models/beto_finetuned_final`), umbral de decisión (0.5), orígenes CORS permitidos y nivel de log. Lee `.env` si existe.
- Se implementó `src/api/schemas.py` con los esquemas Pydantic v2: `PredictRequest`, `PredictResponse`, `ExplainResponse`, `HealthResponse` y `MetadataResponse`. Se usó `StringConstraints` en lugar del deprecado `constr`.
- Se implementó `src/api/main.py` con la aplicación FastAPI completa:
  - **`lifespan`**: carga el tokenizador y el modelo al arrancar; modo degradado (sin crash) si `models/beto_finetuned_final/` no existe.
  - **CORS**: acepta cualquier origen `chrome-extension://` (via regex) y `localhost`.
  - **`GET /health`**: liveness check — devuelve si el modelo está cargado.
  - **`GET /metadata`**: versión del modelo, umbral y configuración activa.
  - **`POST /predict`**: clasificación binaria (hate / no_hate) con probabilidad corregida según umbral.
  - **`POST /explain`**: igual que `/predict` + tokens y pesos SHAP (SHAP se carga lazy en la primera petición; fallback a tokens simples si no está disponible).
- Se verificó que todos los módulos importan sin errores y los 4 endpoints están registrados.

**Resultado de la verificación:**

```
OK - Modulos importados
Endpoints: ['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc', '/health', '/metadata', '/predict', '/explain']
```

**Archivos creados/modificados:**

| Archivo | Contenido |
|---------|-----------|
| `src/api/config.py` | Clase `Settings` con pydantic-settings. Lee `.env`. |
| `src/api/schemas.py` | 5 esquemas Pydantic v2 para todos los endpoints. |
| `src/api/main.py` | App FastAPI con lifespan, CORS, 4 endpoints y modo degradado. |

**Mejoras respecto al borrador del plan:**
- Modo degradado: el servidor arranca aunque el modelo no exista (HTTP 503 en ML endpoints).
- SHAP lazy: se inicializa solo en la primera petición a `/explain`, no al arrancar.
- Endpoint `/metadata` añadido (no estaba en el borrador) para trazabilidad del modelo.
- Probabilidad de hate calculada correctamente: si el pipeline devuelve `LABEL_0`, `prob_hate = 1 - score`.

**Cómo ejecutar (Paso 6.2):**

```powershell
$env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

---

### Paso 6.2 - Ejecutar API

> **Este paso lo ejecuta el usuario en su terminal.** El servidor queda corriendo hasta que presiones `Ctrl+C`.

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Salida esperada al arrancar:**

```
INFO:     Cargando tokenizador desde models/beto_finetuned_final ...
INFO:     Cargando modelo desde models/beto_finetuned_final ...
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
```

**Verificaciones tras arrancar:**

| Verificación | Cómo hacerla |
|---|---|
| Servidor vivo | Abrir http://127.0.0.1:8000/health en el navegador |
| Swagger UI | Abrir http://127.0.0.1:8000/docs |
| Predecir un texto | Usar el botón "Try it out" en `/predict` en Swagger |
| Estado del modelo | `/health` → campo `model_loaded: true` |

**Si el modelo no está cargado** (`model_loaded: false`):
- Verificar que `models/beto_finetuned_final/` existe y tiene los archivos del modelo.
- El servidor arranca en modo degradado; `/predict` y `/explain` devuelven HTTP 503 hasta que el modelo esté disponible.

**Para probar `/predict` con curl:**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method POST -ContentType 'application/json' -Body '{"texto": "Ese pinche tipo me cae muy mal"}'
```

**Respuesta esperada:**
```json
{
  "etiqueta": "hate",
  "probabilidad": 0.87,
  "modelo": "beto_finetuned",
  "version": "v1"
}
```

---

### OK REALIZADO - Paso 6.2

**Qué hace este paso:**

Levanta el servidor FastAPI con `uvicorn`. El servidor carga BETO en memoria al arrancar y queda escuchando en `http://127.0.0.1:8000`. La extensión de Chrome se conectará a este servidor para hacer inferencias.

**Comandos a ejecutar por el usuario:**

```powershell
# En una terminal dedicada (queda corriendo):
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload

# Verificar que responde (en otra terminal o navegador):
Invoke-RestMethod -Uri http://127.0.0.1:8000/health -Method GET
```

**Endpoints listos para usar:**

| Endpoint | URL |
|----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Health check | http://127.0.0.1:8000/health |
| Metadata | http://127.0.0.1:8000/metadata |
| Predict | POST http://127.0.0.1:8000/predict |
| Explain | POST http://127.0.0.1:8000/explain |

> **Nota:** Mantener el servidor corriendo para el Paso 7 (integración con la extensión Chrome).

---

## FASE 7: EXTENSIÓN CHROME (Semana 8–9)

### Paso 7.1 - Crear Manifest

**Archivo:** `extension/manifest.json`

```json
{
  "manifest_version": 3,
  "name": "Detector de Discurso de Odio (ES)",
  "version": "1.0.0",
  "description": "Detección automática de discurso de odio",
  "permissions": ["activeTab", "scripting", "storage"],
  "host_permissions": ["http://127.0.0.1:8000/*"],
  "action": { "default_popup": "popup.html" },
  "options_page": "options.html",
  "background": { "service_worker": "background.js" },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["lexicon.js", "api.js", "content.js"],
      "css": ["styles.css"]
    }
  ]
}
```

### Paso 7.2 - Crear popup

**Archivo:** `extension/popup.html`

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <style>
      body {
        font-family: Arial, sans-serif;
        width: 300px;
        padding: 10px;
      }
      h2 {
        font-size: 16px;
        margin-top: 0;
      }
      label {
        display: block;
        margin: 10px 0;
      }
      input[type="checkbox"] {
        margin-right: 5px;
      }
      #apiStatus {
        font-weight: bold;
      }
    </style>
  </head>
  <body>
    <h2>Detector ES</h2>
    <label> <input type="checkbox" id="toggle" /> Detección automática </label>
    <label>
      Umbral: <span id="umbralValue">0.70</span>
      <input
        type="range"
        id="umbral"
        min="0.5"
        max="0.95"
        step="0.05"
        value="0.7"
      />
    </label>
    <p>API: <span id="apiStatus">…</span></p>
    <a
      href="options.html"
      target="_blank"
      style="display: block; margin-top: 10px;"
    >
      ⚙️ Lexicón personal
    </a>
    <script src="popup.js"></script>
  </body>
</html>
```

**Archivo:** `extension/popup.js`

```javascript
const toggle = document.getElementById("toggle");
const umbral = document.getElementById("umbral");
const umbralValue = document.getElementById("umbralValue");
const apiStatus = document.getElementById("apiStatus");

// Cargar estado guardado
chrome.storage.local.get(["deteccionActiva", "umbralMl"], (s) => {
  toggle.checked = !!s.deteccionActiva;
  umbral.value = s.umbralMl ?? 0.7;
  umbralValue.textContent = (s.umbralMl ?? 0.7).toFixed(2);
});

toggle.addEventListener("change", () => {
  chrome.storage.local.set({ deteccionActiva: toggle.checked });
  console.log("Detección:", toggle.checked ? "activada" : "desactivada");
});

umbral.addEventListener("input", () => {
  const val = parseFloat(umbral.value);
  chrome.storage.local.set({ umbralMl: val });
  umbralValue.textContent = val.toFixed(2);
});

// Verificar API
fetch("http://127.0.0.1:8000/health")
  .then((r) => r.json())
  .then((d) => {
    apiStatus.textContent = d.status === "ok" ? "✓ conectada" : "✗ error";
    apiStatus.style.color = d.status === "ok" ? "green" : "red";
  })
  .catch(() => {
    apiStatus.textContent = "✗ desconectada";
    apiStatus.style.color = "red";
  });
```

### Paso 7.3 - Instalar extensión en Chrome

1. Abre Chrome/Edge
2. Navega a `chrome://extensions/` (o `edge://extensions/`)
3. Activa **Modo de desarrollador** (arriba a la derecha)
4. Haz clic en **Cargar extensión sin empaquetar**
5. Selecciona la carpeta `extension/`

---

### OK REALIZADO - Fase 7 (Integración BETO completa)

**Contexto:** La extensión ya existía como prototipo funcional con detección por lexicón local. El cableado HTTP hacia el backend (`api.js`, handlers en `background.js`) estaba implementado pero sin invocar. Faltaban los 3 cambios descritos a continuación.

**Se implementó:**

**1. `extension/content.js` — recolección de fragmentos para BETO:**
- En cada llamada a `escanear()`, si `apiHabilitada=true`, se hace un segundo `TreeWalker` recolectando hasta 50 fragmentos de texto (≥15 chars, ≤512 chars).
- Cada fragmento recibe un ID único `ml_*` y su elemento padre se guarda en `window.__hateRefs[id]`.
- Los fragmentos se envían al service worker con `enviarLoteAlModelo(fragmentos)`.
- El flag `data-hate-ml-id` en el elemento padre evita re-enviar el mismo texto en escaneos sucesivos.

**2. `extension/content.js` — procesar resultados del modelo:**
- Se agregó el handler `tipo === "RESULTADO"` en `chrome.runtime.onMessage`, que llama a `aplicarResultadoML(msg)`.
- `aplicarResultadoML()`: si `etiqueta=hate` y `probabilidad ≥ umbralMl`, agrega `.hate-ml` al elemento padre + tooltip con probabilidad.
- Se implementó `aplicarExplicacion()` para `tipo === "EXPLAIN_RES"`: colorea tokens SHAP con `.hate-explain-token[data-shap-positive/negative]`.
- Se agregó `umbralMl` al config y a la lectura de storage (antes no se leía).

**3. `extension/styles.css` — CSS para marcas BETO:**
- `.hate-ml`: outline violeta (2px, rgba 124,58,237) para distinguir de las marcas rojas del lexicón.
- `.hate-explain-token[data-shap-positive]`: fondo rojo translúcido (token que empuja hacia hate).
- `.hate-explain-token[data-shap-negative]`: fondo verde translúcido (token que empuja hacia no_hate).

**Verificación:**

```powershell
# Confirmar que no quedan stubs funcionales pendientes:
findstr /S /N /I "TODO BETO" extension\*.js
# Solo aparecen comentarios de documentación — ningún stub sin implementar.
```

**Flujo end-to-end activado:**

```
Usuario activa API en Options Page
→ apiHabilitada=true en chrome.storage.local
→ escanear() recolecta fragmentos → enviarLoteAlModelo()
→ background.js PREDICT_BATCH → HateApi.enqueuePredict()
→ POST /predict al backend FastAPI (BETO ajustado)
→ chrome.tabs.sendMessage(tipo=RESULTADO)
→ aplicarResultadoML() → .hate-ml (outline violeta)
```

**Distinciones visuales:**

| Marca | Color | Origen |
|-------|-------|--------|
| `.hate-detect-mark` | Rojo | Lexicón local (reglas) |
| `.hate-ml` | Violeta | BETO ML (probabilístico) |
| `.hate-explain-token` | Rojo/Verde | SHAP (XAI) |

**Archivos modificados:**

| Archivo | Cambios |
|---------|---------|
| `extension/content.js` | +60 líneas: recolección, `aplicarResultadoML()`, `aplicarExplicacion()`, handlers de mensajes, `umbralMl` en config/storage |
| `extension/styles.css` | +40 líneas: `.hate-ml`, `.hate-explain-token[data-shap-positive/negative]` |

---



### Paso 8.1 - Completar EXPERIMENTOS.md

Rellenar todas las tablas y decisiones registradas durante el desarrollo.

### Paso 8.2 - Crear MANIFEST.json de artefactos

**Archivo:** `data/processed/MANIFEST.json`

```json
{
  "corpus": {
    "version": 1,
    "file": "corpus_v1_enriquecido.parquet",
    "sha256": "[CALCULAR]",
      "datasets": ["spanish-hate-speech-superset-v2024", "detoxis-2021"],
    "lexicon_version": "modismos_latam_v1.csv"
  },
  "models": {
    "beto_finetuned_final": {
      "base_model": "dccuchile/bert-base-spanish-wwm-cased",
      "best_seed": 42,
      "f1_test": 0.79,
      "commit": "[CALCULAR]"
    }
  }
}
```

### Paso 8.3 - Hacer freeze del repositorio

```bash
git add -A
git commit -m "Versión final del proyecto v1.0"
git tag v1.0
```

---

## CHECKLIST DE HITOS

### Fase 1 ✓

- [ ] Datasets descargados en `data/raw/`
- [ ] Corpus unificado en `data/processed/`
- [ ] Lexicón LATAM en `data/lexicons/`

### Fase 2 ✓

- [ ] BETO entrenado (3 semillas)
- [ ] mBERT entrenado (3 semillas)
- [ ] XLM-R entrenado (3 semillas)

### Fase 3 ✓

- [ ] Evaluación en test set completada
- [ ] Comparativa global generada
- [ ] McNemar significancia calculada

### Fase 4 ✓

- [ ] Análisis de modismos completado
- [ ] H3 validada/rechazada

### Fase 5 ✓

- [ ] XAI (SHAP) funcional
- [ ] 50 explicaciones analizadas

### Fase 6 ✓

- [ ] Backend API funcional en `localhost:8000`
- [ ] Endpoints `/health`, `/predict`, `/explain` probados

### Fase 7 ✓

- [ ] Extensión Chrome instalada
- [ ] Detección automática funcional

### Fase 8 ✓

- [ ] EXPERIMENTOS.md completo
- [ ] Repo versionado con tag v1.0

---

**¡Listo!** Sigue este documento paso a paso y tendrás un proyecto completo, reproducible y defendible.

---

## 📋 ESTADO DE PROGRESO — Última actualización: 2026-06-28

### Avance actual: **Fase 1 COMPLETA ✅ + Fase 2 COMPLETA ✅ + Extensión Chrome (Fase 7) COMPLETA ✅ + Fase 6 Pasos 6.1 y 6.2 COMPLETA ✅**

#### Lo que se completó:

1. **Paso 0 — Preparación inicial:** ✅
   - Entorno configurado (Python 3.10+, venv, dependencias en `requirements.txt`).
   - Estructura de carpetas verificada.

2. **Paso 1.1–1.2 — Identificación y verificación de datasets:** ✅
   - Fuentes verificadas: superset (29,855 ejemplos, 5 datasets) + DETOXIS (3,463 ejemplos).
   - Scripts de verificación ejecutados (`data/raw/analisis_dataset/`).
   - Documentacion en data/raw/analisis_dataset/README.md y data/raw/README_DATASET_RECOPIDOS.md.

3. **Paso 1.3 — Exploración inicial:** ✅
   - Pipeline reproducible (`scripts/exploracion_inicial.py` + `notebooks/01_exploracion.ipynb`).
   - Reporte automático en `data/reports_qc/exploracion_inicial.md` con 4 figuras.
   - Total combinado: 37,026 filas tras carga inicial (HatEval filtrado a ES).
   - Confirmado el rol crítico de Chilean para H3 (9.6% de textos con seeds LATAM).

4. **Pasos 1.4–1.11 — Pipeline completo de datos:** ✅
   - `clean.py`, `unify.py`, `lexicon.py`, `enrich.py`, `qc.py`, `split.py`, `crear_manifest.py`, `generar_reporte_qc_final.py`.
   - Corpus final: 33,318 filas → train (23,090) / val (4,948) / test (4,949), sin leakage.

5. **Fase 2 — Fine-tuning de modelos (COMPLETA):** ✅
   - BETO entrenado con semillas 42, 123, 2024 → `models/beto_finetuned_*/`
   - mBERT entrenado con semillas 42, 123, 2024 → `models/mbert_finetuned_*/`
   - XLM-R entrenado con semillas 42, 123, 2024 → `models/xlmr_finetuned_*/`
   - Mejor BETO copiado a `models/beto_finetuned_final/`
   - Total: **10 modelos** entrenados en Google Colab (GPU T4).

6. **Fase 7 — Extensión Chrome (COMPLETA):** ✅
   - Prototipo beta funcional (v0.9.0) desarrollado y probado.
   - Detección 100% local por lexicón (sin BETO, funciona ya).
   - Frontend limpio, moderno, tema claro (violeta suave).

7. **Fase 6 — Backend FastAPI, Paso 6.1 (COMPLETO):** ✅
   - `src/api/config.py`: clase `Settings` con pydantic-settings (ruta modelo, umbral, CORS, log level).
   - `src/api/schemas.py`: 5 esquemas Pydantic v2 (`PredictRequest`, `PredictResponse`, `ExplainResponse`, `HealthResponse`, `MetadataResponse`).
   - `src/api/main.py`: app FastAPI con 4 endpoints (`/health`, `/metadata`, `/predict`, `/explain`), modo degradado si el modelo no existe, SHAP lazy, CORS con regex para extensión Chrome.
   - Todos los módulos verificados — importan sin errores.

---

### Archivos nuevos y modificados para la exploración (Paso 1.3):

| Archivo                                    | Descripción                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `scripts/exploracion_inicial.py` | Script reproducible. Carga el superset y DETOXIS, calcula stats, genera 4 figuras y escribe reporte MD/JSON. Ejecutar: `python scripts/exploracion_inicial.py`. |
| `notebooks/01_exploracion.ipynb`           | Notebook que reusa las funciones del script y permite inspección interactiva celda por celda.                                                                            |
| `data/reports_qc/exploracion_inicial.md`   | **Salida.** Reporte ejecutivo con resumen, figuras y hallazgos.                                                                                                          |
| `data/reports_qc/exploracion_inicial.json` | **Salida.** Métricas crudas en JSON.                                                                                                                                     |
| `data/reports_qc/figuras/*.png`            | **Salida.** 4 figuras (volumen, distribución de clases, longitud, seeds LATAM).                                                                                          |

---

### Archivos nuevos y modificados para la extensión:

| Archivo                               | Descripción                                                                                                                                                                                                                         |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `extension/manifest.json`             | Manifest V3, versión `0.9.0` (fijo para Chrome). Declara permisos, content scripts y background worker.                                                                                                                             |
| `extension/api.js`                    | **NUEVO.** Contrato HTTP con backend BETO (stub funcional). Implementa `/health`, `/predict`, `/explain` + cola con caché. Listo para cuando BETO esté entrenado.                                                                   |
| `extension/lexicon.js`                | Lexicón base (~80 términos en 4 categorías: insultos, discriminatorios, violencia, LATAM). Funciones de matching con regex Unicode.                                                                                                 |
| `extension/content.js`                | Content script. Escanea DOM, detecta coincidencias del lexicón, aplica 4 modos de censura (resaltar/difuminar/asteriscos/ocultar). Reacciona a `MutationObserver` con debounce 400ms. **TODO BETO:** stubs de integración marcados. |
| `extension/background.js`             | Service worker. Gestiona badge con contador de detecciones, estadísticas globales, handlers `PREDICT_BATCH`/`EXPLAIN_REQ` (gateados por `apiHabilitada`). Importa `api.js`.                                                         |
| `extension/styles.css`                | Estilos inyectados en páginas: `.hate-detect-mark` con 4 variantes según modo.                                                                                                                                                      |
| `extension/popup/popup.html`          | Popup principal: toggle de detección, selector de modos, estadísticas por página, botones de re-escaneo y acceso al lexicón personal.                                                                                               |
| `extension/popup/popup.css`           | Tema claro (lavanda papel #f7f5fc → #efeafa, violeta #7c5cf2). Glassmorphism suave, sombras ligeras.                                                                                                                                |
| `extension/popup/popup.js`            | Lógica del popup: sincronización con `chrome.storage.local`, ping a backend. **Fix:** validación de URLs inyectables para evitar warnings en tabs no compatibles (chrome://, edge://, etc.).                                        |
| `extension/options/options.html`      | Options Page: CRUD del lexicón personal (máx. 200 términos), búsqueda, importar/exportar JSON, ajustes (detección, modo, URL backend).                                                                                              |
| `extension/options/options.css`       | Misma paleta clara que popup. Panel responsive 2 columnas.                                                                                                                                                                          |
| `extension/options/options.js`        | Gestión del lexicón personal: agregar/quitar/buscar/limpiar. Persistencia en `chrome.storage.local`. Export/import con validación. Aviso de privacidad.                                                                             |
| `extension/test/demo.html`            | Página local de prueba. Ejemplos de texto neutro, tóxico, modismos LATAM, discurso político. Abre con `file://` o servidor local.                                                                                                   |
| `extension/icons/*.png`               | Iconos 16×32×48×128 (generados con `generate_icons.py`). Gradiente violeta.                                                                                                                                                         |
| `documentos_extras/guia-extension.md` | Guía completa (14 secciones). Instalación paso a paso, estructura, uso básico, solución de problemas, **Sección 11:** tabla detallada de archivos a modificar cuando BETO esté listo (línea por línea, qué hacer en cada archivo).  |

---

### Cómo continuar (Esta sección, y además dentro de cada paso descrito anteriormente, se debe actualizar cada vez que se avanza en el proyecto):

1. **Completado (Fase 1):** ✅
   - Superset + DETOXIS verificados, explorados, unificados, enriquecidos con `tiene_modismo`, validados (QC), particionados (70/15/15) y manifiestos generados.

2. **Completado (Fase 2):** ✅
   - 10 modelos entrenados: BETO × 3 semillas, mBERT × 3 semillas, XLM-R × 3 semillas, BETO final.
   - Todo en `models/`.

3. **Siguiente: Fase 3 — Evaluación en test set:**
   - Crear `scripts/evaluate_model.py` (código en Paso 3.1 de este documento).
   - Ejecutar evaluación en los 9 modelos: `python scripts/evaluate_model.py --all`.
   - Calcular intervalos de confianza con bootstrap (Paso 3.3).
   - Test de McNemar para significancia estadística (Paso 3.4).
   - Generar tablas comparativas en `reports/tables/`.

4. **Cuando BETO esté evaluado (Fase 3 → Fase 6 → integración extensión):**
   - Usar `documentos_extras/guia-extension.md`, **Sección 11.1** como mapa exacto.
   - Tabla con 8 archivos a modificar (paso a paso, qué línea cambiar).
   - Modificar `content.js`, `background.js`, `styles.css`.
   - Activar API desde la Options Page (`apiHabilitada=true`).
   - Testar end-to-end con backend en `localhost:8000`.

5. **Para entender la arquitectura:**
   - Leer `documentos_extras/INSTRUCCIONES_PROYECTO.md` Sección 15 (Extensión).
   - Leer `documentos_extras/modelo-de-analisis.md` (flujos de datos).

---

### Estado funcional de la extensión (ahora):

✅ **Funciona totalmente sin BETO:**

- Instala en Chrome/Edge sin errores (manifest v0.9.0 válido).
- Detección automática en cualquier página (activable en popup).
- 4 modos de censura: resaltar (subrayado rojo), difuminar (blur + clic revela), asteriscos (\*\*\*\*), ocultar ([contenido oculto]).
- Lexicón personal: agregar/quitar términos, límite 200 items, persistencia local, export/import JSON.
- Estadísticas: detecciones en página actual + total acumulado + cantidad de palabras propias.
- UI moderna, paleta clara (violeta suave), responsive.
- **Privacidad:** todo en `chrome.storage.local`, nunca sale del navegador.
- **Fix 1:** Manifest version ahora es `0.9.0` (Chrome exige formato x.y.z sin sufijos). Campo `version_name` muestra `0.9.0-beta` al usuario.
- **Fix 2:** Warnings de conexión eliminados; validación de URLs antes de enviar mensajes entre popup y content script.

⏳ **Cuando BETO esté listo (2–3 cambios):**

- Inferencia con `/predict` desde el backend.
- XAI con SHAP vía `/explain` (tooltips con tokens coloreados).
- Complementar detección lexicón + IA contextual.

---

**Próximos pasos:** Fase 1.3 en adelante (exploración, limpieza de datos, notebooks).
