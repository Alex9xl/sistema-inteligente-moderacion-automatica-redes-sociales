from transformers import AutoTokenizer, AutoModelForSequenceClassification

modelo = "dccuchile/bert-base-spanish-wwm-cased"

tokenizer = AutoTokenizer.from_pretrained(modelo)

model = AutoModelForSequenceClassification.from_pretrained(
    modelo,
    num_labels=2
)