"""
Paso 1.10 - Crear MANIFEST.json
Calcula SHA-256 de los archivos del corpus procesado y genera
data/processed/MANIFEST.json con metadatos completos de versión.
"""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def calcular_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def main():
    print("=" * 60)
    print("  PASO 1.10 - Crear MANIFEST.json")
    print("=" * 60)

    processed_dir = ROOT / "data" / "processed"

    archivos = {
        "corpus_v1_enriquecido": processed_dir / "corpus_v1_enriquecido.parquet",
        "train":                 processed_dir / "train.parquet",
        "val":                   processed_dir / "val.parquet",
        "test":                  processed_dir / "test.parquet",
    }

    # Verificar existencia
    for nombre, ruta in archivos.items():
        if not ruta.exists():
            raise FileNotFoundError(f"No encontrado: {ruta}")

    # Calcular SHA-256
    print("\nCalculando SHA-256...")
    sha_corpus = calcular_sha256(archivos["corpus_v1_enriquecido"])
    sha_train  = calcular_sha256(archivos["train"])
    sha_val    = calcular_sha256(archivos["val"])
    sha_test   = calcular_sha256(archivos["test"])

    print(f"  corpus_v1_enriquecido : {sha_corpus[:32]}...")
    print(f"  train                 : {sha_train[:32]}...")
    print(f"  val                   : {sha_val[:32]}...")
    print(f"  test                  : {sha_test[:32]}...")

    git_commit = get_git_commit()
    print(f"\nCommit git            : {git_commit[:12]}...")

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "corpus": {
            "version": 1,
            "file": "corpus_v1_enriquecido.parquet",
            "sha256": sha_corpus,
            "git_commit": git_commit,
            "created_at": created_at,
            "datasets_origen": [
                "spanish-hate-speech-superset-v2024",
                "detoxis-2021"
            ],
            "lexicon_version": "modismos_latam_v1.csv",
            "n_total": 33318,
            "n_hate": 7603,
            "n_no_hate": 25715,
            "nota": (
                "33,318 filas antes de deduplicación. "
                "Tras eliminar 331 duplicados quedan 32,987 filas "
                "distribuidas en los splits train/val/test."
            )
        },
        "splits": {
            "deduplication": {
                "duplicados_exactos_eliminados": 217,
                "duplicados_normalizados_eliminados": 114,
                "total_eliminados": 331,
                "corpus_limpio": 32987
            },
            "train": {
                "file": "train.parquet",
                "sha256": sha_train,
                "n_filas": 23090,
                "proporcion": "70%",
                "pct_hate": "22.8%"
            },
            "val": {
                "file": "val.parquet",
                "sha256": sha_val,
                "n_filas": 4948,
                "proporcion": "15%",
                "pct_hate": "22.8%"
            },
            "test": {
                "file": "test.parquet",
                "sha256": sha_test,
                "n_filas": 4949,
                "proporcion": "15%",
                "pct_hate": "22.8%"
            }
        },
        "leakage_check": {
            "train_val":  0,
            "train_test": 0,
            "val_test":   0
        },
        "pipeline": {
            "clean_py":   "src/data/clean.py",
            "unify_py":   "src/data/unify.py",
            "enrich_py":  "src/data/enrich.py",
            "qc_py":      "src/data/qc.py",
            "split_py":   "src/data/split.py"
        }
    }

    output_path = processed_dir / "MANIFEST.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] MANIFEST.json guardado en: {output_path}")
    print("\nContenido generado:")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("Paso 1.10 completado exitosamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()
