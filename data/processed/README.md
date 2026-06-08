# Datasets Procesados (Final)

Este directorio contiene el corpus unificado y las particiones train/val/test.

## Estructura

```
data/processed/
├── corpus_v1.parquet                  # Corpus unificado sin enriquecimiento
├── corpus_v1_enriquecido.parquet      # Corpus con tiene_modismo
├── train.parquet                      # 70% estratificado
├── val.parquet                        # 15% estratificado
├── test.parquet                       # 15% estratificado
├── MANIFEST.json                      # Hashes y metadatos
├── CHANGELOG.md                       # Historial de versiones
└── README.md
```

## Archivos principales

- **corpus_v1_enriquecido.parquet**: Insumo del entrenamiento (NUNCA MODIFICAR TRAS USARSE)
- **train.parquet**: Usado para entrenamiento
- **val.parquet**: Usado para validación durante entrenamiento
- **test.parquet**: Usado SOLO al final para evaluación final

## MANIFEST.json

Contiene metadatos de reproducibilidad:

```json
{
  "corpus": {
    "version": 1,
    "file": "corpus_v1_enriquecido.parquet",
    "sha256": "...",
    "git_commit": "...",
    "n_total": 38421,
    "n_hate": 11250,
    "n_no_hate": 27171
  }
}
```

## Importante

- **Test set congelado**: Una vez creado, no se modifica.
- **No versionar en git**: Archivos .parquet son binarios y muy grandes.
- **Backup**: Guardar en Drive / S3 con MANIFEST.json.

## Generación

```bash
python scripts/prepare_data.py --version 1
```
