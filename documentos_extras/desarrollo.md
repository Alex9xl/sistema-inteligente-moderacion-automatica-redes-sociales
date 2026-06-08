# Guía Ejecutable: Pasos para Llevar a Cabo el Proyecto Completo

Este documento es un **itinerario práctico paso a paso** para implementar todo el proyecto. Está basado en `guia.md` y complementa sus especificaciones técnicas.

**Tiempo total estimado:** 8-10 semanas (ver cronograma en guia.md sección 16)

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

### Paso 1.1 - Descargar datasets

Descarga **manualmente** (o con scripts curl/wget) los siguientes **cuatro** datasets públicos a `data/raw/`:

| Dataset         | URL                                                                                        | Guardar en                  |
| --------------- | ------------------------------------------------------------------------------------------ | --------------------------- |
| HatEval 2019    | https://huggingface.co/datasets/valeriobasile/HatEval                                      | `data/raw/hateval/`         |
| DETOXIS         | https://github.com/alvaro-mazcu-herreros/DETOXIS_2021                                      | `data/raw/detoxis/`         |
| HaterNet        | https://zenodo.org/records/2592149                                                         | `data/raw/haternet/`        |
| Chilean Dataset | https://github.com/aymeam/Datasets-for-Hate-Speech-Detection/tree/master/Chilean%20dataset | `data/raw/chilean_dataset/` |

**Documentar en `EXPERIMENTOS.md`:** URLs exactas, checksums descargados, fechas.

### Paso 1.2 - Verificar contenido de datasets

```bash
cd data/raw
# Verificar que cada carpeta tenga archivos .csv o .tsv
ls -lah hateval/
ls -lah mexa3t/
ls -lah detoxis/
```

Abrir cada archivo con un editor/pandas para entender su estructura:

```python
import pandas as pd

df_hateval = pd.read_csv("data/raw/hateval/train.csv")
print(df_hateval.head())
print(df_hateval.columns)
print(df_hateval.dtypes)
print(df_hateval.shape)
```

---

### ✅ REALIZADO - Paso 1.2

**Se hizo:**

- Se definieron las fuentes de datos (4 datasets públicos en Hugging Face, GitHub y Zenodo).
- Se documentaron en `EXPERIMENTOS.md` las URLs exactas y referencias.
- Se verificó la estructura teórica de cada dataset y sus columnas esperadas.

**Nota para continuar:**

- Los datasets aún **no están descargados** en `data/raw/`. Cuando retome el proyecto, debe descargar manualmente los 4 datasets desde las URLs en Paso 1.1.
- Una vez descargados, puede proceder directamente al **Paso 1.3** (notebook de exploración).

---

### Paso 1.3 - Ejecutar notebook de exploración

Crear y ejecutar `notebooks/01_exploracion.ipynb`:

```python
import pandas as pd
import numpy as np

# Cargar cada dataset
df_hateval = pd.read_csv("../data/raw/hateval/train.csv")
df_mexa3t = pd.read_csv("../data/raw/mexa3t/train.csv")
df_detoxis = pd.read_csv("../data/raw/detoxis/train.csv")

# Explorar
print("HatEval shape:", df_hateval.shape)
print("MEX-A3T shape:", df_mexa3t.shape)
print("DETOXIS shape:", df_detoxis.shape)

# Columnas
print("\nHatEval columns:", df_hateval.columns.tolist())
print("MEX-A3T columns:", df_mexa3t.columns.tolist())
print("DETOXIS columns:", df_detoxis.columns.tolist())

# Distribución de etiquetas
print("\nHatEval etiquetas:", df_hateval['HS'].value_counts())
print("MEX-A3T etiquetas:", df_mexa3t['aggressive'].value_counts())
print("DETOXIS etiquetas:", df_detoxis['toxicity_level'].value_counts())
```

**Guardar análisis en `data/reports_qc/exploracion_inicial.md`.**

---

### ✅ REALIZADO - Paso 1.3

**Se hizo:**

- Se construyó un pipeline reproducible de exploración que carga los **4 datasets reales** (no los 3 de placeholder de la guía: HatEval, **DETOXIS**, **HaterNet** y **Chilean** — no MEX-A3T).
- HatEval se filtró a `language == "es"` (queda en 6,599 ejemplos).
- HaterNet se parseó desde su formato `id=...;||;texto;||;label`.
- Se calcularon, por cada dataset: shape, columnas, dtypes, nulos, duplicados, distribuciones de etiquetas, longitudes (chars/tokens) y proporción de "seeds" LATAM como aproximación previa al lexicón completo del Paso 1.6.
- Se generaron 4 figuras (PNG) y un reporte Markdown + JSON.
- **Total combinado tras carga inicial:** 37,026 filas (HatEval ES 6,599 + DETOXIS 3,463 + HaterNet 6,000 + Chilean 20,964).

**Archivos agregados / modificados:**

| Archivo                                           | Qué hace                                                                                                                                                         |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/exploracion_inicial.py`                  | Script ejecutable con toda la lógica (cargadores por dataset, métricas, figuras, render del MD/JSON). Reproducible: `python scripts/exploracion_inicial.py`.     |
| `notebooks/01_exploracion.ipynb`                  | Notebook que importa las funciones del script y las invoca paso a paso, con `display(Image(...))` para ver las figuras inline. Útil para inspección interactiva. |
| `data/reports_qc/exploracion_inicial.md`          | **Salida automática.** Reporte ejecutivo con tabla resumen, figuras, hallazgos y propuesta de mapeo binario para el Paso 1.5.                                    |
| `data/reports_qc/exploracion_inicial.json`        | **Salida automática.** Métricas crudas en JSON (machine-readable).                                                                                               |
| `data/reports_qc/figuras/volumen_datasets.png`    | Figura: filas por dataset.                                                                                                                                       |
| `data/reports_qc/figuras/distribucion_clases.png` | Figura: barras 0/1 por dataset (etiqueta de hate principal).                                                                                                     |
| `data/reports_qc/figuras/longitud_tokens.png`     | Figura: mediana/P95/máx de tokens por dataset.                                                                                                                   |
| `data/reports_qc/figuras/seeds_latam.png`         | Figura: % de textos con al menos un seed LATAM.                                                                                                                  |

**Hallazgos clave (datos reales):**

| Dataset  |  Filas |                  % odio | % seeds LATAM | Longitud P95 (tokens) |
| -------- | -----: | ----------------------: | ------------: | --------------------: |
| HatEval  |  6,599 |              41.5% (HS) |          2.4% |                    46 |
| DETOXIS  |  3,463 |        33.1% (toxicity) |          0.1% |                   112 |
| HaterNet |  6,000 |           26.1% (label) |          1.1% |                    30 |
| Chilean  | 20,964 | 6.4% (hate/estereotipo) |          9.6% |                    49 |

- **Chilean** tiene >11k duplicados de texto que habrá que tratar en el Paso 1.5.
- **DETOXIS** tiene los textos más largos (P95=112 tokens, máx=556) → en BETO podría requerir `max_length=256` en lugar de 128 si se quiere preservar contexto.
- **Chilean** confirma su rol crítico para H3: 9.6% de textos con seeds LATAM, frente a <2.5% de los demás.

**Cómo reproducir:**

```powershell
.\venv\Scripts\python.exe scripts\exploracion_inicial.py
# o desde Jupyter
jupyter notebook notebooks\01_exploracion.ipynb
```

---

### Paso 1.4 - Crear scripts de limpieza y normalización

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
    """Normalizar texto preservando mayúsculas (para BETO cased)."""
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

# Probar con muestras
muestras = [
    "Hola @usuario https://example.com #test",
    "¡¡¡Hola!!!",
    "Me encanta 😂😂😂"
]
for m in muestras:
    print(f"Original: {m}")
    print(f"Limpio: {normalizar(m)}")
    print()
```

**Ejecutar en notebook `02_unificacion.ipynb`** (paso siguiente).

### Paso 1.5 - Limpiar y mapear etiquetas

**Notebook:** `notebooks/02_unificacion.ipynb`

```python
import pandas as pd
from src.data.clean import normalizar

# Cargar y limpiar HatEval
df_hateval = pd.read_csv("../data/raw/hateval/train.csv")
df_hateval["texto"] = df_hateval["text"].apply(normalizar)
df_hateval["etiqueta"] = df_hateval["HS"]  # 0 o 1 ya está bien
df_hateval["dataset"] = "hateval"
df_hateval_limpio = df_hateval[["texto", "etiqueta", "dataset"]].copy()

# Cargar y limpiar MEX-A3T
df_mexa3t = pd.read_csv("../data/raw/mexa3t/train.csv")
df_mexa3t["texto"] = df_mexa3t["text"].apply(normalizar)
df_mexa3t["etiqueta"] = (df_mexa3t["aggressive"] == "yes").astype(int)  # yes→1, no→0
df_mexa3t["dataset"] = "mexa3t"
df_mexa3t_limpio = df_mexa3t[["texto", "etiqueta", "dataset"]].copy()

# Cargar y limpiar DETOXIS
df_detoxis = pd.read_csv("../data/raw/detoxis/train.csv")
df_detoxis["texto"] = df_detoxis["text"].apply(normalizar)
df_detoxis["etiqueta"] = (df_detoxis["toxicity_level"] >= 2).astype(int)  # >=2→1
df_detoxis["dataset"] = "detoxis"
df_detoxis_limpio = df_detoxis[["texto", "etiqueta", "dataset"]].copy()

# Concatenar
corpus = pd.concat([df_hateval_limpio, df_mexa3t_limpio, df_detoxis_limpio],
                     ignore_index=True)

# Agregar ID único
corpus["id"] = corpus["dataset"] + "_" + corpus.reset_index().index.astype(str)

# Reordenar columnas
corpus = corpus[["id", "texto", "etiqueta", "dataset"]]

print("Corpus combinado shape:", corpus.shape)
print("Distribución de clases:")
print(corpus["etiqueta"].value_counts())
print("\nDistribución por dataset:")
print(corpus["dataset"].value_counts())

# Guardar versión interim
corpus.to_parquet("../data/interim/corpus_combinado.parquet")
```

**Output:** `data/interim/corpus_combinado.parquet`

### Paso 1.6 - Construir lexicón LATAM

**Archivo:** `data/lexicons/modismos_latam_v1.csv`

Crear manualmente un CSV con estructura:

```csv
termino,variantes,pais,tipo,fuente,notas,version_introduccion
weón,wei;weon;weón,CL,coloquial,ASALE,Puede ser amistoso o insulto.,1
pinche,pinche,MX,intensificador,ASALE,Marcador frecuente de ofensa.,1
parce,parce;parcero,CO,coloquial,ASALE,Neutro.,1
chamo,chamo;chama,VE,curado_manual,Término coloquial.,1
naco,naco;naca,MX,despectivo,ASALE,Clasista.,1
```

**Meta:** ≥ 500 términos, con referencias citables.

### Paso 1.7 - Enriquecer corpus con `tiene_modismo`

**Crear:** `src/data/lexicon.py`

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
                self.terminos.add(var.strip().lower())

    def tiene_modismo(self, texto: str) -> bool:
        """Detectar si el texto contiene algún modismo LATAM."""
        tokens = re.findall(r"\w+", texto.lower())
        return any(t in self.terminos for t in tokens)

# En el notebook 02_unificacion.ipynb:
from src.data.lexicon import LexiconLatam

lexicon = LexiconLatam("../data/lexicons/modismos_latam_v1.csv")
corpus["tiene_modismo"] = corpus["texto"].apply(lexicon.tiene_modismo)

print("Proporción con modismos:", corpus["tiene_modismo"].mean())
```

**Output:** Corpus actualizado en `data/interim/corpus_enriquecido.parquet`

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
    "datasets_origen": ["hateval-2019", "mexa3t-2020", "detoxis-2021"],
    "lexicon_version": "modismos_latam_v1.csv",
    "n_total": 38421,
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

## FASE 2: FINE-TUNING DE BETO (Semanas 3–5)

### Paso 2.1 - Configurar entorno de GPU (opcional)

Si usas **Colab** o **Kaggle**, ejecuta en la primera celda:

```python
# En Colab
!pip install --upgrade torch transformers datasets

# Verificar GPU
import torch
print("GPU disponible:", torch.cuda.is_available())
print("Dispositivo:", torch.device("cuda" if torch.cuda.is_available() else "cpu"))
```

Si usas **PC local con GPU**:

```bash
# Verificar CUDA
nvidia-smi

# Instalar PyTorch con CUDA (reemplaza 12.1 con tu versión)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Paso 2.2 - Crear script de entrenamiento

**Archivo:** `scripts/train_model.py`

```python
#!/usr/bin/env python
"""
Script de entrenamiento reproducible para BETO, mBERT y XLM-R.

Uso:
  python scripts/train_model.py --model beto --seed 42
  python scripts/train_model.py --model mbert --seed 123
  python scripts/train_model.py --model xlmr --seed 2024
"""

import argparse
import numpy as np
import torch
import pandas as pd
from pathlib import Path
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding,
    EarlyStoppingCallback,
)
from datasets import Dataset
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

# Configuración
MODELS = {
    "beto": "dccuchile/bert-base-spanish-wwm-cased",
    "mbert": "bert-base-multilingual-cased",
    "xlmr": "xlm-roberta-base",
}

LR_MAP = {
    "beto": 2e-5,
    "mbert": 2e-5,
    "xlmr": 1e-5,  # XLM-R suele ir mejor con LR más baja
}

def print_banner(model_name, seed, device):
    print("=" * 60)
    print(" INICIO ENTRENAMIENTO")
    print("=" * 60)
    print(f"Modelo: {model_name}")
    print(f"Semilla: {seed}")
    print(f"Dispositivo: {device}")
    print(f"PyTorch: {torch.__version__}")
    print(f"Transformers: {__import__('transformers').__version__}")
    print("=" * 60)

def set_seeds(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(-1)
    p, r, f, _ = precision_recall_fscore_support(
        labels, preds, average="binary", pos_label=1, zero_division=0
    )
    return {
        "precision": p, "recall": r, "f1": f,
        "accuracy": accuracy_score(labels, preds),
    }

class WeightedTrainer(Trainer):
    def __init__(self, class_weights_t, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights_t = class_weights_t

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=self.class_weights_t.to(logits.device)
        )
        loss = loss_fct(logits.view(-1, 2), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["beto", "mbert", "xlmr"], default="beto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--max_length", type=int, default=128)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print_banner(args.model, args.seed, device)
    set_seeds(args.seed)

    # Cargar datos
    print("Cargando corpus...")
    train_df = pd.read_parquet("data/processed/train.parquet")
    val_df = pd.read_parquet("data/processed/val.parquet")

    # Calcular class weights
    class_weights = compute_class_weight(
        "balanced", classes=np.array([0, 1]), y=train_df["etiqueta"].values
    )
    class_weights_t = torch.tensor(class_weights, dtype=torch.float)
    print(f"Class weights: {class_weights}")

    # Tokenizar
    print("Tokenizando...")
    model_name = MODELS[args.model]
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize(batch):
        return tokenizer(
            batch["texto"],
            truncation=True,
            max_length=args.max_length,
            padding=False,
        )

    train_ds = Dataset.from_pandas(train_df[["texto", "etiqueta"]])
    val_ds = Dataset.from_pandas(val_df[["texto", "etiqueta"]])
    train_ds = train_ds.rename_column("etiqueta", "labels")
    val_ds = val_ds.rename_column("etiqueta", "labels")
    train_ds = train_ds.map(tokenize, batched=True, batch_size=100)
    val_ds = val_ds.map(tokenize, batched=True, batch_size=100)

    # Modelo
    print("Cargando modelo...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # Configuración de entrenamiento
    output_dir = f"models/{args.model}_finetuned_{args.seed}"
    args_train = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=32,
        learning_rate=LR_MAP[args.model],
        weight_decay=0.01,
        warmup_ratio=0.1,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=torch.cuda.is_available(),
        seed=args.seed,
        report_to="none",
        save_total_limit=2,
        logging_steps=50,
    )

    # Trainer
    trainer = WeightedTrainer(
        class_weights_t=class_weights_t,
        model=model,
        args=args_train,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    # Entrenar
    print("Iniciando entrenamiento...")
    trainer.train()

    # Guardar
    print(f"Guardando en {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("¡Entrenamiento completado!")

if __name__ == "__main__":
    main()
```

**Hacer ejecutable:**

```bash
chmod +x scripts/train_model.py
```

### Paso 2.3 - Entrenar BETO con 3 semillas

```bash
python scripts/train_model.py --model beto --seed 42
python scripts/train_model.py --model beto --seed 123
python scripts/train_model.py --model beto --seed 2024
```

Esto genera:

- `models/beto_finetuned_42/`
- `models/beto_finetuned_123/`
- `models/beto_finetuned_2024/`

**Registrar en `EXPERIMENTOS.md`** las métricas de validación de cada corrida.

### Paso 2.4 - Entrenar mBERT y XLM-R

```bash
# mBERT
python scripts/train_model.py --model mbert --seed 42
python scripts/train_model.py --model mbert --seed 123
python scripts/train_model.py --model mbert --seed 2024

# XLM-R
python scripts/train_model.py --model xlmr --seed 42
python scripts/train_model.py --model xlmr --seed 123
python scripts/train_model.py --model xlmr --seed 2024
```

**Tiempo esperado:** 2-3 horas por modelo en T4/P100; 6-12 horas en CPU.

### Paso 2.5 - Seleccionar mejor semilla y crear modelo final

```python
# Leer métricas de los 3 entrenamientos
import json

f1_scores = {}
for seed in [42, 123, 2024]:
    # Leer del último checkpoint
    with open(f"models/beto_finetuned_{seed}/trainer_state.json") as f:
        state = json.load(f)
    best_f1 = state["best_metric"]
    f1_scores[seed] = best_f1
    print(f"Semilla {seed}: F1={best_f1:.4f}")

# Mejor semilla
best_seed = max(f1_scores, key=f1_scores.get)
print(f"\nMejor semilla: {best_seed} (F1={f1_scores[best_seed]:.4f})")

# Copiar a modelo final
import shutil
shutil.copytree(
    f"models/beto_finetuned_{best_seed}",
    "models/beto_finetuned_final",
    dirs_exist_ok=True
)
```

---

## FASE 3: EVALUACIÓN EN TEST SET (Semana 5–6)

### Paso 3.1 - Crear script de evaluación

**Archivo:** `scripts/evaluate_model.py`

```python
#!/usr/bin/env python
"""
Script de evaluación en test set.

Uso:
  python scripts/evaluate_model.py --model beto --seed 42
  python scripts/evaluate_model.py --all  # Todos los modelos
"""

import argparse
import numpy as np
import torch
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.metrics import (
    precision_recall_fscore_support, accuracy_score, confusion_matrix,
    roc_auc_score, classification_report
)
import json

MODELS_TO_EVAL = [
    ("beto", 42), ("beto", 123), ("beto", 2024),
    ("mbert", 42), ("mbert", 123), ("mbert", 2024),
    ("xlmr", 42), ("xlmr", 123), ("xlmr", 2024),
]

def evaluate_one(model_name, seed):
    print(f"\nEvaluando {model_name} (semilla {seed})...")

    # Cargar modelo y tokenizer
    model_path = f"models/{model_name}_finetuned_{seed}"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Pipeline para facilitar inferencia
    pipe = pipeline("text-classification", model=model, tokenizer=tokenizer,
                    device=0 if torch.cuda.is_available() else -1)

    # Cargar test set
    test_df = pd.read_parquet("data/processed/test.parquet")

    # Predicciones
    preds_list = []
    probs_list = []
    for text in test_df["texto"]:
        output = pipe(text, top_k=2, truncation=True, max_length=128)
        # output = [{"label": "LABEL_0", "score": ...}, ...]
        # Extraer predicción y probabilidad
        label_to_id = {"LABEL_0": 0, "LABEL_1": 1}
        scores_dict = {o["label"]: o["score"] for o in output}
        pred = int(label_to_id[max(output, key=lambda x: x["score"])["label"]])
        prob_1 = scores_dict.get("LABEL_1", 0.0)
        preds_list.append(pred)
        probs_list.append(prob_1)

    y_true = test_df["etiqueta"].values
    y_pred = np.array(preds_list)
    y_proba = np.array(probs_list)

    # Métricas
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    pm, rm, fm, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    acc = accuracy_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)

    print(f"  Precision (hate): {p:.4f}")
    print(f"  Recall (hate): {r:.4f}")
    print(f"  F1 (hate): {f:.4f}")
    print(f"  F1 macro: {fm:.4f}")
    print(f"  Accuracy: {acc:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")

    # Guardar resultado
    result = {
        "model": model_name,
        "seed": seed,
        "precision_hate": float(p),
        "recall_hate": float(r),
        "f1_hate": float(f),
        "f1_macro": float(fm),
        "accuracy": float(acc),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm.tolist(),
    }

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    results = []

    if args.all:
        for model, seed in MODELS_TO_EVAL:
            result = evaluate_one(model, seed)
            results.append(result)
    elif args.model and args.seed is not None:
        result = evaluate_one(args.model, args.seed)
        results.append(result)
    else:
        print("Especifica --model y --seed, o --all")
        return

    # Guardar resultados
    df_results = pd.DataFrame(results)
    df_results.to_csv("reports/tables/metrics_all_models.csv", index=False)

    # Resumen por modelo (media ± std)
    summary = df_results.groupby("model").agg({
        "precision_hate": ["mean", "std"],
        "recall_hate": ["mean", "std"],
        "f1_hate": ["mean", "std"],
        "f1_macro": ["mean", "std"],
        "accuracy": ["mean", "std"],
        "roc_auc": ["mean", "std"],
    })
    print("\n" + "="*60)
    print("RESUMEN POR MODELO")
    print("="*60)
    print(summary)
    summary.to_csv("reports/tables/comparativa_global.csv")

if __name__ == "__main__":
    main()
```

### Paso 3.2 - Ejecutar evaluación

```bash
python scripts/evaluate_model.py --all
```

Esto genera:

- `reports/tables/metrics_all_models.csv`
- `reports/tables/comparativa_global.csv`

### Paso 3.3 - Bootstrap e intervalos de confianza

**Crear notebook:** `notebooks/06_evaluacion_comparada.ipynb`

```python
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score

def bootstrap_ic(y_true, y_pred, B=1000, alpha=0.05, seed=42):
    """Intervalos de confianza por bootstrap."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    vals = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        vals[b] = f1_score(y_true[idx], y_pred[idx], average="binary", pos_label=1)
    lo = np.percentile(vals, 100 * alpha / 2)
    hi = np.percentile(vals, 100 * (1 - alpha / 2))
    return vals.mean(), lo, hi

# Cargar predicciones y calcular IC
test_df = pd.read_parquet("../data/processed/test.parquet")
y_true = test_df["etiqueta"].values

# Para cada modelo, calcular IC
for model_name in ["beto", "mbert", "xlmr"]:
    f1_vals = []
    for seed in [42, 123, 2024]:
        # Cargar predicciones (de evaluate_model.py)
        # Aquí simplificado
        f1_mean, f1_lo, f1_hi = bootstrap_ic(y_true, y_pred)
        print(f"{model_name} (semilla {seed}): F1 = {f1_mean:.4f} [{f1_lo:.4f}, {f1_hi:.4f}]")
```

### Paso 3.4 - Test de McNemar

```python
from statsmodels.stats.contingency_tables import mcnemar

# Cargar predicciones de dos modelos
y_pred_beto = np.array([...])  # Predicciones de BETO
y_pred_mbert = np.array([...]) # Predicciones de mBERT

# Tabla 2x2
aciertos_beto = (y_pred_beto == y_true).astype(int)
aciertos_mbert = (y_pred_mbert == y_true).astype(int)

n00 = ((aciertos_beto == 1) & (aciertos_mbert == 1)).sum()  # Ambos acierto
n01 = ((aciertos_beto == 1) & (aciertos_mbert == 0)).sum()  # Solo BETO acierto
n10 = ((aciertos_beto == 0) & (aciertos_mbert == 1)).sum()  # Solo mBERT acierto
n11 = ((aciertos_beto == 0) & (aciertos_mbert == 0)).sum()  # Ambos error

tabla = [[n00, n01], [n10, n11]]
res = mcnemar(tabla, exact=False, correction=True)

print(f"McNemar BETO vs mBERT:")
print(f"  p-valor: {res.pvalue:.6f}")
print(f"  Significativo: {res.pvalue < 0.05}")
```

---

## FASE 4: ANÁLISIS DE MODISMOS (Semana 6)

### Paso 4.1 - Segmentar test set

```python
test_df = pd.read_parquet("data/processed/test.parquet")

test_mod = test_df[test_df["tiene_modismo"] == True]
test_no_mod = test_df[test_df["tiene_modismo"] == False]

print(f"Test con modismos: {len(test_mod)} ({len(test_mod)/len(test_df):.1%})")
print(f"Test sin modismos: {len(test_no_mod)} ({len(test_no_mod)/len(test_df):.1%})")

print("\nDistribución de clases en test_mod:")
print(test_mod["etiqueta"].value_counts())
print("\nDistribución de clases en test_no_mod:")
print(test_no_mod["etiqueta"].value_counts())
```

### Paso 4.2 - Evaluar en subconjuntos

```python
# Cargar modelo BETO ajustado
from transformers import pipeline

pipe = pipeline("text-classification", model="models/beto_finetuned_final")

# Evaluar en test_mod y test_no_mod
for subset_name, subset_df in [("con_modismos", test_mod), ("sin_modismos", test_no_mod)]:
    y_true = subset_df["etiqueta"].values
    y_pred = []
    for text in subset_df["texto"]:
        output = pipe(text, truncation=True, max_length=128)
        label = 1 if output[0]["label"] == "LABEL_1" else 0
        y_pred.append(label)
    y_pred = np.array(y_pred)

    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="binary")
    print(f"{subset_name}: Precision={p:.4f}, Recall={r:.4f}, F1={f:.4f}")
```

### Paso 4.3 - Prueba estadística de H3

```python
# Bootstrap de la diferencia
f1_con = 0.82  # Placeholder
f1_sin = 0.77  # Placeholder
delta = f1_con - f1_sin

print(f"H3: F1(con_modismos) - F1(sin_modismos) = {delta:.4f}")
print(f"Conclusión: {'Hipótesis soportada' if delta > 0 else 'Hipótesis rechazada'}")
```

---

## FASE 5: XAI - SHAP (Semana 7)

### Paso 5.1 - Generar explicaciones

**Notebook:** `notebooks/08_xai.ipynb`

```python
import shap
import torch
from transformers import pipeline

# Cargar modelo
model_path = "models/beto_finetuned_final"
pipe = pipeline("text-classification", model=model_path, device=0 if torch.cuda.is_available() else -1)

# SHAP explainer
masker = shap.maskers.Text(tokenizer)
explainer = shap.Explainer(pipe, masker)

# Ejemplos a explicar
ejemplos = test_df["texto"].sample(10, random_state=42).tolist()

# Generar explicaciones (esto puede tardar 1-2 min por ejemplo en CPU)
for i, texto in enumerate(ejemplos):
    print(f"Explicando ejemplo {i+1}/10...")
    shap_values = explainer([texto])
    # Visualizar (en notebook)
    shap.plots.text(shap_values)
```

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

### Paso 6.2 - Ejecutar API

```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Acceder a http://127.0.0.1:8000/docs para Swagger UI.

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

## FASE 8: VALIDACIÓN FINAL (Semana 10)

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
    "datasets": ["hateval-2019", "mexa3t-2020", "detoxis-2021"],
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

## 📋 ESTADO DE PROGRESO — Última actualización: 2026-06-06

### Avance actual: **Paso 1.3 (Fase 1) + Extensión completa (Fase 7)**

#### Lo que se completó:

1. **Paso 0 — Preparación inicial:** ✅
   - Entorno configurado (Python 3.10+, venv, dependencias en `requirements.txt`).
   - Estructura de carpetas verificada.

2. **Paso 1.1–1.2 — Identificación y verificación de datasets:** ✅
   - 4 datasets descargados en `data/raw/`: HatEval, DETOXIS, HaterNet, Chilean.
   - Scripts de verificación ejecutados (`data/raw/analisis_dataset/`).
   - Documentación detallada en `data/raw/analisis_dataset/dataset_resumen.md`.

3. **Paso 1.3 — Exploración inicial:** ✅
   - Pipeline reproducible (`scripts/exploracion_inicial.py` + `notebooks/01_exploracion.ipynb`).
   - Reporte automático en `data/reports_qc/exploracion_inicial.md` con 4 figuras.
   - Total combinado: 37,026 filas tras carga inicial (HatEval filtrado a ES).
   - Confirmado el rol crítico de Chilean para H3 (9.6% de textos con seeds LATAM).

4. **Fase 7 — Extensión Chrome (COMPLETA):** ✅
   - Prototipo beta funcional (v0.9.0) desarrollado y probado.
   - Detección 100% local por lexicón (sin BETO, funciona ya).
   - Frontend limpio, moderno, tema claro (violeta suave).

---

### Archivos nuevos y modificados para la exploración (Paso 1.3):

| Archivo                                    | Descripción                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `scripts/exploracion_inicial.py`           | Script reproducible. Carga los 4 datasets reales, calcula métricas, genera 4 figuras y escribe el reporte MD/JSON. Ejecutar con `python scripts/exploracion_inicial.py`. |
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

1. **Inmediato (Fase 1):**
   - ✅ Datasets ya descargados en `data/raw/`.
   - ✅ Exploración inicial completa (Paso 1.3): ver `data/reports_qc/exploracion_inicial.md`.
   - **Siguiente: Paso 1.4** — implementar `src/data/clean.py` con `normalizar()` (regex URLs/menciones/hashtags/emojis) y tests con muestras.
   - **Paso 1.5** — `notebooks/02_unificacion.ipynb`: aplicar `normalizar()` y mapear cada dataset al esquema binario unificado (HatEval `HS==1`, DETOXIS `toxicity_level>=2`, HaterNet `label==1`, Chilean `hate speech/estereotipo==1`).
   - **Pasos 1.6–1.10** — lexicón LATAM (`data/lexicons/modismos_latam_v1.csv`), enriquecimiento (`tiene_modismo`), QC, particionado 70/15/15.

2. **Cuando BETO esté entrenado (Fase 3 → Fase 6):**
   - Usar `documentos_extras/guia-extension.md`, **Sección 11.1** como mapa exacto.
   - Tabla con 8 archivos a modificar (paso a paso, qué línea cambiar).
   - Modificar `content.js`, `background.js`, `styles.css`.
   - Activar API desde la Options Page (`apiHabilitada=true`).
   - Testar end-to-end con backend en `localhost:8000`.

3. **Para entender la arquitectura:**
   - Leer `documentos_extras/guia.md` Sección 15 (Extensión).
   - Leer `documentos_extras/modelo-de-analisis.md` (flujos de datos).
   - Leer `ARQUITECTURA_CREADA.md` para visión general.

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
