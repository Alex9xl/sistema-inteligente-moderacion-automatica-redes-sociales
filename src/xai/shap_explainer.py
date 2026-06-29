"""
src/xai/shap_explainer.py
Wrapper SHAP sobre el modelo BETO ajustado.

Consumido por src/api/xai.py para responder el endpoint POST /explain.

Salida estandarizada:
  {
    "tokens": ["pinche", "USUARIO", "te", "odio"],
    "pesos":  [0.42,    -0.05,    0.10,  0.55]
  }

Pesos positivos → empujan la predicción hacia "hate".
Pesos negativos → empujan la predicción hacia "no_hate".
"""

import shap
import torch
from transformers import AutoTokenizer, pipeline as hf_pipeline


class ShapExplainer:
    """
    Carga el modelo BETO ajustado y genera explicaciones SHAP por token.

    Uso:
        exp = ShapExplainer("models/beto_finetuned_final")
        resultado = exp.explain("Ese pinche tipo me cae muy mal")
        # → {"tokens": [...], "pesos": [...]}
    """

    def __init__(self, model_path: str):
        """
        Inicializa el tokenizador, el pipeline de clasificación y el explainer SHAP.
        La inicialización es costosa (~5-30 s); hacerla una sola vez al arrancar el backend.

        Args:
            model_path: Ruta al directorio del modelo (ej. "models/beto_finetuned_final").
        """
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        device = 0 if torch.cuda.is_available() else -1
        self.pipe = hf_pipeline(
            "text-classification",
            model=model_path,
            tokenizer=self.tokenizer,
            top_k=None,
            device=device,
        )

        masker = shap.maskers.Text(self.tokenizer)
        self.explainer = shap.Explainer(self.pipe, masker)

    def explain(self, texto: str, max_chars: int = 256) -> dict:
        """
        Devuelve tokens y pesos SHAP para la clase hate (LABEL_1).

        El texto se trunca a max_chars caracteres para mantener latencia razonable.
        En CPU, cada llamada toma ~10-60 s según la longitud del texto.

        Args:
            texto:     Texto de entrada.
            max_chars: Máximo de caracteres a procesar (default 256).

        Returns:
            {
                "tokens": list[str],   # tokens del texto
                "pesos":  list[float], # peso SHAP de cada token (+ = hate, - = no_hate)
            }
        """
        texto_truncado = texto[:max_chars]
        shap_values = self.explainer([texto_truncado])

        tokens = list(shap_values.data[0])
        # columna 1 = clase hate (LABEL_1)
        pesos = shap_values.values[0][:, 1].tolist()

        return {"tokens": tokens, "pesos": pesos}

    def explain_top(self, texto: str, top_n: int = 5, max_chars: int = 256) -> dict:
        """
        Igual que explain(), pero añade los top_n tokens por peso absoluto.
        Útil para mostrar un resumen rápido sin serializar todos los tokens.

        Returns:
            {
                "tokens":      list[str],
                "pesos":       list[float],
                "top_tokens":  list[str],   # top_n tokens más influyentes
                "top_pesos":   list[float], # sus pesos
            }
        """
        resultado = self.explain(texto, max_chars=max_chars)
        pares = sorted(
            zip(resultado["tokens"], resultado["pesos"]),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        top = pares[:top_n]
        resultado["top_tokens"] = [t for t, _ in top]
        resultado["top_pesos"] = [round(p, 4) for _, p in top]
        return resultado


# ── Verificación rápida (ejecutar directamente) ─────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    MODEL_PATH = "models/beto_finetuned_final"

    print("Cargando ShapExplainer...")
    print(f"  Modelo: {MODEL_PATH}")
    exp = ShapExplainer(MODEL_PATH)
    print("  ✅ Explainer cargado\n")

    muestras = [
        "Ese pinche tipo me cae muy mal",
        "Que tengas un buen día amigo",
        "Eres un imbécil y te odio",
    ]

    for texto in muestras:
        print(f"Texto: {texto!r}")
        resultado = exp.explain_top(texto, top_n=3)
        print(f"  Tokens ({len(resultado['tokens'])}): {resultado['tokens']}")
        print(f"  Top-3 tokens: {list(zip(resultado['top_tokens'], resultado['top_pesos']))}")
        print()
