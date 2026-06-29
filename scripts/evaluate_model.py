#!/usr/bin/env python
"""
Script de evaluación en test set — Fase 3.

Evalúa todos los modelos fine-tuneados (BETO, mBERT, XLM-R × 3 semillas)
sobre el test set y genera:
  - reports/predictions/<modelo>_<semilla>_preds.csv  (predicciones individuales)
  - reports/tables/metrics_all_models.csv             (métricas por modelo+semilla)
  - reports/tables/comparativa_global.csv             (resumen media±std por modelo)

Las predicciones individuales son necesarias para los tests estadísticos
de los pasos 3.3 (bootstrap) y 3.4 (McNemar).

Uso:
  python scripts/evaluate_model.py --model beto --seed 42
  python scripts/evaluate_model.py --all
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

MODELS_TO_EVAL = [
    ("beto",  42),
    ("beto",  123),
    ("beto",  2024),
    ("mbert", 42),
    ("mbert", 123),
    ("mbert", 2024),
    ("xlmr",  42),
    ("xlmr",  123),
    ("xlmr",  2024),
]

MAX_LENGTH  = 128
BATCH_SIZE  = 32   # ajustar según VRAM disponible
TEST_PATH   = Path("data/processed/test.parquet")
PRED_DIR    = Path("reports/predictions")
TABLE_DIR   = Path("reports/tables")


def _ensure_dirs():
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Evaluación de un modelo
# ---------------------------------------------------------------------------

def evaluate_one(model_name: str, seed: int) -> dict:
    """Evalúa un modelo en el test set; devuelve dict con métricas."""

    model_path = Path(f"models/{model_name}_finetuned_{seed}")
    if not model_path.exists():
        print(f"  [SKIP] {model_path} no encontrado.", file=sys.stderr)
        return {}

    print(f"\n{'='*60}")
    print(f"  Evaluando {model_name.upper()} — semilla {seed}")
    print(f"{'='*60}")
    print(f"  Ruta modelo : {model_path}")

    # Cargar test set
    test_df = pd.read_parquet(TEST_PATH)
    y_true  = test_df["etiqueta"].values

    # Tokenizar
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    def tokenize_batch(batch):
        return tokenizer(
            batch["texto"],
            truncation=True,
            max_length=MAX_LENGTH,
            padding=False,
        )

    ds = Dataset.from_pandas(test_df[["texto"]].reset_index(drop=True))
    ds = ds.map(tokenize_batch, batched=True, batch_size=200)

    # Inferencia con Trainer (batched, eficiente)
    model      = AutoModelForSequenceClassification.from_pretrained(model_path)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Dispositivo : {device_str}")

    training_args = TrainingArguments(
        output_dir=str(PRED_DIR / f"tmp_{model_name}_{seed}"),
        per_device_eval_batch_size=BATCH_SIZE,
        report_to="none",
        no_cuda=not torch.cuda.is_available(),
        disable_tqdm=False,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=DataCollatorWithPadding(tokenizer),
    )
    preds_output = trainer.predict(ds)

    logits  = preds_output.predictions            # shape (n, 2)
    proba   = _softmax(logits)                    # shape (n, 2)
    y_pred  = logits.argmax(axis=1).astype(int)
    y_proba = proba[:, 1]                         # P(hate)

    # Guardar predicciones individuales (para bootstrap y McNemar)
    preds_df = pd.DataFrame({
        "y_true":  y_true,
        "y_pred":  y_pred,
        "prob_hate": y_proba,
    })
    pred_path = PRED_DIR / f"{model_name}_{seed}_preds.csv"
    preds_df.to_csv(pred_path, index=False)
    print(f"  Predicciones guardadas → {pred_path}")

    # Métricas
    p,  r,  f,  _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    pm, rm, fm, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    acc     = accuracy_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_proba)
    cm      = confusion_matrix(y_true, y_pred)

    print(f"\n  Métricas en test set:")
    print(f"    Precision (hate): {p:.4f}")
    print(f"    Recall    (hate): {r:.4f}")
    print(f"    F1        (hate): {f:.4f}")
    print(f"    F1 macro        : {fm:.4f}")
    print(f"    Accuracy        : {acc:.4f}")
    print(f"    ROC-AUC         : {roc_auc:.4f}")
    print(f"\n  Matriz de confusión:\n{cm}")
    print(f"\n  Reporte de clasificación:")
    print(classification_report(y_true, y_pred,
                                target_names=["no_hate", "hate"], zero_division=0))

    # Limpiar directorio temporal de Trainer
    import shutil
    tmp = PRED_DIR / f"tmp_{model_name}_{seed}"
    if tmp.exists():
        shutil.rmtree(tmp)

    return {
        "model":          model_name,
        "seed":           seed,
        "precision_hate": float(p),
        "recall_hate":    float(r),
        "f1_hate":        float(f),
        "precision_macro": float(pm),
        "recall_macro":   float(rm),
        "f1_macro":       float(fm),
        "accuracy":       float(acc),
        "roc_auc":        float(roc_auc),
        "tn":             int(cm[0, 0]),
        "fp":             int(cm[0, 1]),
        "fn":             int(cm[1, 0]),
        "tp":             int(cm[1, 1]),
    }


def _softmax(logits: np.ndarray) -> np.ndarray:
    exp = np.exp(logits - logits.max(axis=1, keepdims=True))
    return exp / exp.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------------------
# Guardar resultados
# ---------------------------------------------------------------------------

def save_results(results: list[dict]):
    df = pd.DataFrame(results)
    df = df.sort_values(["model", "seed"])

    # Por modelo + semilla
    all_path = TABLE_DIR / "metrics_all_models.csv"
    df.to_csv(all_path, index=False)
    print(f"\n  [OK] Métricas individuales → {all_path}")

    # Resumen media ± std por modelo
    metric_cols = ["precision_hate", "recall_hate", "f1_hate",
                   "f1_macro", "accuracy", "roc_auc"]
    summary = df.groupby("model")[metric_cols].agg(["mean", "std"]).round(4)
    comp_path = TABLE_DIR / "comparativa_global.csv"
    summary.to_csv(comp_path)
    print(f"  [OK] Comparativa global → {comp_path}")

    # Mostrar resumen en consola
    print(f"\n{'='*60}")
    print("  RESUMEN POR MODELO (media ± std, 3 semillas)")
    print(f"{'='*60}")
    for model_name in ["beto", "mbert", "xlmr"]:
        sub = df[df["model"] == model_name]
        if sub.empty:
            continue
        f1_mean = sub["f1_hate"].mean()
        f1_std  = sub["f1_hate"].std()
        roc_mean = sub["roc_auc"].mean()
        roc_std  = sub["roc_auc"].std()
        print(f"  {model_name.upper():6s}  F1={f1_mean:.4f}±{f1_std:.4f}"
              f"  ROC-AUC={roc_mean:.4f}±{roc_std:.4f}")

    # Guardar también en JSON para facilitar el uso en notebooks
    json_path = TABLE_DIR / "metrics_all_models.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"  [OK] JSON de métricas → {json_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evaluación en test set — Fase 3")
    parser.add_argument("--model", choices=["beto", "mbert", "xlmr"],
                        default=None, help="Modelo a evaluar")
    parser.add_argument("--seed",  type=int, default=None,
                        help="Semilla del modelo")
    parser.add_argument("--all",   action="store_true",
                        help="Evaluar todos los modelos")
    args = parser.parse_args()

    _ensure_dirs()

    if not args.all and (args.model is None or args.seed is None):
        parser.error("Especifica --model y --seed, o usa --all")

    to_eval = MODELS_TO_EVAL if args.all else [(args.model, args.seed)]

    results = []
    for model_name, seed in to_eval:
        result = evaluate_one(model_name, seed)
        if result:
            results.append(result)

    if results:
        save_results(results)
        print(f"\n¡Evaluación completada! {len(results)}/{len(to_eval)} modelos procesados.")
    else:
        print("\nNo se generaron resultados. Verifica que los modelos existen en models/")


if __name__ == "__main__":
    main()
