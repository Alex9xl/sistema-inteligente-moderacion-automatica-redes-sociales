# Directorio de Modelos

Este directorio contiene los checkpoints del entrenamiento.

## Estructura esperada

```
models/
├── beto_finetuned_42/          # Entrenamiento semilla 42
├── beto_finetuned_123/         # Entrenamiento semilla 123
├── beto_finetuned_2024/        # Entrenamiento semilla 2024
├── mbert_finetuned_42/         # Baselines
├── mbert_finetuned_123/
├── ...
├── beto_finetuned_final/       # Modelo final seleccionado para producción
└── README.md
```

## Convención de nombres

- `<arquitectura>_finetuned_<semilla>/`: Checkpoints de entrenamiento
- `<arquitectura>_finetuned_final/`: Modelo final seleccionado

## Nota importante

Los checkpoints intermedios no se versionan. En cambio,
`beto_finetuned_final/` se versiona íntegramente: su archivo
`model.safetensors` se almacena con Git LFS. Tras clonar el repositorio, ejecuta
`git lfs pull` para descargarlo antes de iniciar la API.

## Verificación

Para verificar que un modelo está presente:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("models/beto_finetuned_final")
model = AutoModelForSequenceClassification.from_pretrained("models/beto_finetuned_final")
print("✓ Modelo cargado correctamente")
```
