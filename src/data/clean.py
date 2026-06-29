"""
Limpieza y normalización de texto para el pipeline de datos.

IMPORTANTE: La función `normalizar()` se aplica ÚNICAMENTE a DETOXIS.
El Spanish Hate Speech Superset ya tiene su propio preprocesamiento aplicado
(usernames → @USER, links → URL) y no debe ser re-normalizado.

Reglas aplicadas (en orden):
  1. Reparar encoding roto con ftfy (mojibake, caracteres mal codificados)
  2. Decodificar entidades HTML (&amp;, &lt;, <br>, etc.)
  3. Eliminar caracteres invisibles / zero-width (U+200B–U+200F, U+202A–U+202E)
  4. Sustituir URLs por el token " URL "
  5. Sustituir menciones (@usuario) por el token " USUARIO "
  6. Descomponer hashtags (#PalabraCompuesta → " PalabraCompuesta ")
  7. Convertir emojis a tokens textuales en español (:cara_enojada:)
  8. Colapsar repeticiones extremas de caracteres (holaaaaaa → holaa)
  9. Colapsar espacios múltiples y recortar

Referencia de diseño: INSTRUCCIONES_PROYECTO.md §6.6 "Manejo de ruido".
"""

import re
import html

import emoji
from ftfy import fix_text

# ---------------------------------------------------------------------------
# Expresiones regulares compiladas (costo único en import)
# ---------------------------------------------------------------------------

# URLs: http/https/www (sin espacios)
_URL_RE = re.compile(r"http\S+|www\.\S+", re.IGNORECASE)

# Menciones: @nombre_usuario (letras, dígitos, guión bajo)
_MENCION_RE = re.compile(r"@\w+")

# Hashtags: captura la palabra sin el #
_HASHTAG_RE = re.compile(r"#(\w+)")

# Caracteres invisibles / zero-width:
#   U+200B–U+200F (zero-width space, ZWNJ, ZWJ, LRM, RLM)
#   U+202A–U+202E (directional formatting characters)
_ZWSP_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e]")

# Repeticiones de más de 2 caracteres iguales consecutivos
#   holaaaaaa → holaa | jajajajaja no se toca (son chars distintos)
_REPEAT_RE = re.compile(r"(.)\1{2,}")

# Espacios múltiples (incluye tabs y saltos de línea que queden)
_SPACES_RE = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def normalizar(texto: str) -> str:
    """Normaliza un texto de DETOXIS al esquema canónico del proyecto.

    Preserva las mayúsculas originales porque BETO es *cased* (distingue
    entre "Buenas" y "buenas"). No aplica stemming ni lematización.

    Args:
        texto: Texto crudo de DETOXIS (comentario de noticia en español).

    Returns:
        Texto normalizado como cadena limpia. Devuelve cadena vacía si la
        entrada no es string (p. ej. NaN en pandas).
    """
    if not isinstance(texto, str):
        return ""

    # 1. Reparar encoding roto (mojibake, caracteres mal decodificados)
    texto = fix_text(texto)

    # 2. Decodificar entidades HTML (&amp; → &, &lt; → <, <br> ignorado)
    texto = html.unescape(texto)

    # 3. Eliminar caracteres invisibles / zero-width
    texto = _ZWSP_RE.sub("", texto)

    # 4. Sustituir URLs
    texto = _URL_RE.sub(" URL ", texto)

    # 5. Sustituir menciones
    texto = _MENCION_RE.sub(" USUARIO ", texto)

    # 6. Descomponer hashtags (conserva la palabra sin el #)
    texto = _HASHTAG_RE.sub(r" \1 ", texto)

    # 7. Convertir emojis a tokens textuales en español
    #    Ejemplo: 😂 → :cara_llorando_de_risa:
    texto = emoji.demojize(texto, language="es")

    # 8. Colapsar repeticiones extremas (máximo 2 caracteres iguales seguidos)
    texto = _REPEAT_RE.sub(r"\1\1", texto)

    # 9. Colapsar espacios múltiples y recortar bordes
    texto = _SPACES_RE.sub(" ", texto).strip()

    return texto


# ---------------------------------------------------------------------------
# Bloque de prueba (ejecutar directamente: python src/data/clean.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    # Forzar UTF-8 en la salida de consola (necesario en Windows con cp1252)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    muestras = [
        # Caso 1: mención + URL + hashtag
        ("Mención + URL + hashtag",
         "Hola @usuario visita https://example.com #TestHashtag ahora"),

        # Caso 2: entidades HTML
        ("Entidades HTML",
         "Precio &amp; calidad &lt;excelentes&gt; — véalo aquí &nbsp;"),

        # Caso 3: emojis
        ("Emojis a tokens",
         "Me encanta 😂😂😂 este video 🔥🔥"),

        # Caso 4: repetición extrema de caracteres
        ("Repetición de caracteres",
         "¡¡¡Hola!!! Holaaaaaa qué buenoooooo estás"),

        # Caso 5: texto con encoding roto (simulado)
        ("Encoding roto (ftfy)",
         "AsÃ­ es como funciona el espaÃ±ol mal codificado"),

        # Caso 6: caracteres zero-width
        ("Zero-width chars",
         "Texto\u200bcon\u200czero\u200dwidth\u200e aquí"),

        # Caso 7: texto normal (no debe modificarse sustancialmente)
        ("Texto normal",
         "El presidente anunció medidas contra la inflación en Argentina."),

        # Caso 8: entrada no string (NaN)
        ("Entrada no string (NaN)",
         None),

        # Caso 9: mezcla compleja (real de DETOXIS)
        ("Mezcla compleja",
         "Eres un @idiota!!! Visita http://troll.es #HateSpeech 😡😡😡 y muérete yaaaaaaa"),
    ]

    print("=" * 65)
    print("  PRUEBAS — src/data/clean.py — normalizar()")
    print("=" * 65)

    todos_ok = True
    for nombre, texto in muestras:
        resultado = normalizar(texto)
        print(f"\n[{nombre}]")
        print(f"  Entrada : {repr(texto)}")
        print(f"  Salida  : {repr(resultado)}")

        # Validaciones mínimas
        if texto is None:
            assert resultado == "", f"FALLO: NaN debería dar cadena vacía, got {repr(resultado)}"
        else:
            # Solo validar URL si la entrada contenía http/www
            if texto and ("http" in texto.lower() or "www." in texto.lower()):
                assert "URL" in resultado, \
                    f"FALLO: URL no sustituida en '{nombre}'"
            # Solo validar @ si la entrada tenía menciones
            if texto and re.search(r"@\w+", texto):
                assert "@" not in resultado, \
                    f"FALLO: mención @ no sustituida en '{nombre}'"
            # Solo validar # si la entrada tenía hashtags
            if texto and re.search(r"#\w+", texto):
                assert "#" not in resultado, \
                    f"FALLO: hashtag # no eliminado en '{nombre}'"

    print("\n" + "=" * 65)
    print("  ✓ Todas las pruebas pasaron correctamente.")
    print("=" * 65)
