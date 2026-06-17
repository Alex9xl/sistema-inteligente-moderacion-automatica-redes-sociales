import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

parquet_path = Path("data/interim/corpus_combinado.parquet")
df = pd.read_parquet(parquet_path)

print("=== VERIFICACION FINAL — corpus_combinado.parquet ===")
print(f"Filas       : {len(df):,}")
print(f"Tamaño      : {parquet_path.stat().st_size / 1024:.1f} KB")
print(f"IDs únicos  : {df['id'].nunique() == len(df)}")
print(f"Textos nulos: {df['texto'].isna().sum()}")
print(f"Etiquetas   : {sorted(df['etiqueta'].unique().tolist())} → válidas: {set(df['etiqueta'].unique()) <= {0, 1}}")
print(f"Hate   (1)  : {(df['etiqueta']==1).sum():,} ({(df['etiqueta']==1).mean():.1%})")
print(f"No hate(0)  : {(df['etiqueta']==0).sum():,} ({(df['etiqueta']==0).mean():.1%})")
print(f"Datasets    : {df['dataset'].unique().tolist()}")
print(f"Columnas    : {df.columns.tolist()}")
print("\n✓ Verificación completada.")
