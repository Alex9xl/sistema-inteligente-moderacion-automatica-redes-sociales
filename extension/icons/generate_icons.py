"""
Genera los 4 iconos PNG (16/32/48/128) de la extensión.

Uso (desde la carpeta extension/):
    python icons/generate_icons.py

Requiere: Pillow  (pip install pillow)

Estética: gradiente violeta + escudo con una franja censurada, alineado al
popup. La franja (en vez de un check) comunica que la extensión oculta
contenido, no que lo aprueba.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent
SIZES = [16, 32, 48, 128]


def gradient(size: int) -> Image.Image:
    """Crea un fondo cuadrado con gradiente diagonal violeta."""
    img = Image.new("RGB", (size, size), 0)
    top = (109, 74, 230)        # #6d4ae6
    bottom = (167, 139, 250)    # #a78bfa
    for y in range(size):
        t = y / max(size - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(size):
            img.putpixel((x, y), (r, g, b))
    return img


def round_corners(img: Image.Image, radius: int) -> Image.Image:
    """Aplica esquinas redondeadas con máscara alfa."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    out = Image.new("RGBA", (w, h))
    out.paste(img, (0, 0), mask=mask)
    return out


def shield_polygon(big: float, left: float, apex: float, shoulder: float,
                   side: float, bottom: float) -> list[tuple[float, float]]:
    """Puntos del escudo en coordenadas absolutas, a partir de fracciones."""
    right = 1.0 - left
    return [
        (big * 0.5, big * apex),
        (big * right, big * shoulder),
        (big * right, big * side),
        (big * 0.5, big * bottom),
        (big * left, big * side),
        (big * left, big * shoulder),
    ]


def draw_shield(size: int) -> Image.Image:
    """Dibuja el escudo con la franja censurada encima del gradiente.

    Se dibuja a una resolución mayor (supersampling) y se reduce al final,
    porque ImageDraw no aplica antialiasing y a 16 px los trazos quedarían
    dentados. El contorno se consigue restando un escudo interior en vez de
    trazar líneas, para que las uniones (sobre todo el vértice superior)
    queden limpias.
    """
    scale = 8
    big = size * scale

    base = gradient(big).convert("RGBA")
    base = round_corners(base, radius=int(big * 0.22))

    glyph = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(glyph)

    d.polygon(
        shield_polygon(big, left=0.22, apex=0.15, shoulder=0.245, side=0.55, bottom=0.87),
        fill=(255, 255, 255, 255),
    )
    d.polygon(
        shield_polygon(big, left=0.305, apex=0.275, shoulder=0.315, side=0.535, bottom=0.735),
        fill=(0, 0, 0, 0),
    )

    # Franja censurada: comunica que el contenido se oculta.
    bar_h = big * 0.135
    bar_y = big * 0.475 - bar_h / 2
    d.rounded_rectangle(
        (big * 0.35, bar_y, big * 0.65, bar_y + bar_h),
        radius=bar_h / 2,
        fill=(255, 255, 255, 255),
    )

    base.alpha_composite(glyph)
    return base.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for s in SIZES:
        img = draw_shield(s)
        out = OUT_DIR / f"icon{s}.png"
        img.save(out, format="PNG")
        print(f"[OK] {out.relative_to(OUT_DIR.parent)}  ({s}x{s})")


if __name__ == "__main__":
    main()
