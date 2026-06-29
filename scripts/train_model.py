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
    "xlmr": 1e-5,
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

    print("Cargando corpus...")
    train_df = pd.read_parquet("data/processed/train.parquet")
    val_df = pd.read_parquet("data/processed/val.parquet")

    class_weights = compute_class_weight(
        "balanced", classes=np.array([0, 1]), y=train_df["etiqueta"].values
    )
    class_weights_t = torch.tensor(class_weights, dtype=torch.float)
    print(f"Class weights: {class_weights}")

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

    print("Cargando modelo...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

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

    print("Iniciando entrenamiento...")
    trainer.train()

    print(f"Guardando en {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("¡Entrenamiento completado!")

if __name__ == "__main__":
    main()
