"""
Módulo de gestión del lexicón de modismos latinoamericanos.

Este lexicón cumple un rol OBSERVACIONAL: se usa únicamente para calcular
la columna `tiene_modismo` en el corpus y segmentar la evaluación (H3).
NO se inyecta como feature al modelo.

Fuente: data/lexicons/modismos_latam_v1.csv
"""

import re
import hashlib
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Ruta por defecto relativa a la raíz del proyecto
LEXICON_PATH_DEFAULT = Path("data/lexicons/modismos_latam_v1.csv")


class LexiconLatam:
    """
    Gestión del lexicón de modismos latinoamericanos.

    Carga el CSV canónico, construye un set unificado de términos y variantes
    (en minúsculas), y expone la función pura `tiene_modismo`.

    Parámetros
    ----------
    csv_path : str | Path
        Ruta al archivo CSV del lexicón.
    """

    def __init__(self, csv_path: str | Path = LEXICON_PATH_DEFAULT):
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"Lexicón no encontrado: {self.csv_path}\n"
                "Ejecuta primero el Paso 1.6 para construir el CSV."
            )

        self._df = pd.read_csv(self.csv_path)
        self._validar_esquema()
        self.terminos: set[str] = self._construir_set()
        self._sha256 = self._calcular_hash()

        logger.info(
            "LexiconLatam cargado: %d términos canónicos | %d tokens totales | sha256=%s…",
            len(self._df),
            len(self.terminos),
            self._sha256[:8],
        )

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def tiene_modismo(self, texto: str) -> bool:
        """
        Detecta si el texto contiene algún término del lexicón LATAM.

        La detección se realiza sobre el texto en minúsculas, tokenizado
        por `\\w+`. El texto que alimenta al modelo conserva sus mayúsculas.

        Parámetros
        ----------
        texto : str
            Texto ya normalizado (salida de `clean.normalizar`).

        Retorna
        -------
        bool
            True si al menos un token del texto coincide con el lexicón.
        """
        if not isinstance(texto, str) or not texto.strip():
            return False
        tokens = re.findall(r"\w+", texto.lower())
        return any(t in self.terminos for t in tokens)

    @property
    def version_info(self) -> dict:
        """Información de versión para registrar en EXPERIMENTOS.md."""
        return {
            "archivo": str(self.csv_path),
            "n_terminos_canonicos": len(self._df),
            "n_tokens_totales": len(self.terminos),
            "sha256": self._sha256,
        }

    def cobertura(self, corpus: pd.DataFrame, col_texto: str = "texto") -> dict:
        """
        Calcula la cobertura del lexicón sobre un corpus.

        Retorna un dict con n_con_modismo, n_sin_modismo y porcentaje.
        """
        flags = corpus[col_texto].apply(self.tiene_modismo)
        n_total = len(corpus)
        n_con = flags.sum()
        return {
            "n_total": n_total,
            "n_con_modismo": int(n_con),
            "n_sin_modismo": int(n_total - n_con),
            "pct_con_modismo": round(100 * n_con / n_total, 2) if n_total > 0 else 0.0,
        }

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _validar_esquema(self) -> None:
        """Valida que el CSV tenga las columnas canónicas requeridas."""
        columnas_requeridas = {"termino", "variantes", "pais", "tipo", "fuente"}
        faltantes = columnas_requeridas - set(self._df.columns)
        if faltantes:
            raise ValueError(
                f"El CSV del lexicón no tiene las columnas: {faltantes}"
            )
        assert not self._df["termino"].duplicated().any(), (
            "Hay términos duplicados en el lexicón. Revisar el CSV."
        )
        assert self._df["termino"].notna().all(), (
            "Hay términos nulos en el lexicón."
        )

    def _construir_set(self) -> set[str]:
        """Construye el set unificado de términos + variantes en minúsculas."""
        terminos: set[str] = set()
        for _, row in self._df.iterrows():
            termino = str(row["termino"]).strip().lower()
            if termino:
                terminos.add(termino)
            # Variantes separadas por ";"
            for var in str(row.get("variantes", "")).split(";"):
                v = var.strip().lower()
                if v and v not in ("nan", ""):
                    terminos.add(v)
        return terminos

    def _calcular_hash(self) -> str:
        """Calcula el SHA-256 del archivo CSV para trazabilidad."""
        sha = hashlib.sha256()
        with open(self.csv_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
        return sha.hexdigest()


# ------------------------------------------------------------------
# Ejecución directa: prueba de integridad + cobertura sobre corpus interim
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Resolución de la ruta desde src/data/ hasta la raíz
    ROOT = Path(__file__).resolve().parents[2]
    csv_path = ROOT / "data" / "lexicons" / "modismos_latam_v1.csv"

    print("=" * 60)
    print(" PASO 1.6 - Verificacion del lexicon LATAM")
    print("=" * 60)

    lex = LexiconLatam(csv_path)
    info = lex.version_info
    print(f"\nArchivo   : {info['archivo']}")
    print(f"SHA-256   : {info['sha256']}")
    print(f"Terminos canonicos : {info['n_terminos_canonicos']}")
    print(f"Tokens totales     : {info['n_tokens_totales']}")

    # Pruebas unitarias básicas
    print("\n--- Pruebas de deteccion ---")
    casos = [
        ("Ese pinche tipo no sabe nada", True, "MX: pinche"),
        ("Eso es una weá de mierda", True, "CL: weá"),
        ("Boludo no entendes nada", True, "AR: boludo"),
        ("Gonorrea hijueputa", True, "CO: gonorrea + hijueputa"),
        ("El chamo ese es un chimbo", True, "VE: chamo + chimbo"),
        ("Ese longo creido", True, "EC: longo"),
        ("Este es un texto completamente neutral.", False, "Neutro"),
        ("The cat sat on the mat", False, "Ingles sin LATAM"),
    ]

    errores = 0
    for texto, esperado, descripcion in casos:
        resultado = lex.tiene_modismo(texto)
        icono = "[OK]   " if resultado == esperado else "[ERROR]"
        if resultado != esperado:
            errores += 1
        print(f"  {icono}  [{descripcion}]  ->  {resultado}")

    # Cobertura sobre corpus interim si existe
    corpus_path = ROOT / "data" / "interim" / "corpus_combinado.parquet"
    if corpus_path.exists():
        print("\n--- Cobertura sobre corpus_combinado.parquet ---")
        corpus = pd.read_parquet(corpus_path)
        stats = lex.cobertura(corpus, col_texto="texto")
        print(f"  Total        : {stats['n_total']:,}")
        print(f"  Con modismo  : {stats['n_con_modismo']:,}  ({stats['pct_con_modismo']}%)")
        print(f"  Sin modismo  : {stats['n_sin_modismo']:,}")
        req = stats["pct_con_modismo"] >= 15.0
        estado = "[OK]" if req else "[ADVERTENCIA]"
        print(f"\n  {estado}  Requisito >=15%: {stats['pct_con_modismo']}%")
        if not req:
            print("  La cobertura es menor al minimo requerido.")
            print("  Ampliar el lexicon antes de continuar con el Paso 1.7.")
    else:
        print(
            "\n  (corpus_combinado.parquet no encontrado - ejecuta primero el Paso 1.5)"
        )

    print("\n" + "=" * 60)
    if errores == 0:
        print("Lexicon verificado correctamente.")
    else:
        print(f"{errores} prueba(s) fallaron. Revisar el CSV.")
        sys.exit(1)
