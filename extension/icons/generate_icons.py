"""
Genera los 4 iconos PNG (16/32/48/128) de la extensión.

Uso (desde la carpeta extension/):
    python icons/generate_icons.py

Requiere: Pillow  (pip install pillow)

Estética: gradiente violeta + escudo con check, alineado al popup.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent
SIZES = [16, 32, 48, 128]


def gradient(size: int) -> Image.Image:
    """Crea un fondo cuadrado con gradiente diagonal violeta."""
    img = Image.new("RGB", (size, size), 0)
    top = (124, 58, 237)        # #7c3aed
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


def draw_shield(size: int) -> Image.Image:
    """Dibuja el escudo + check en blanco encima del gradiente."""
    base = gradient(size).convert("RGBA")
    base = round_corners(base, radius=int(size * 0.22))

    d = ImageDraw.Draw(base)

    # Escudo simplificado
    margin = size * 0.22
    top = size * 0.18
    bot = size * 0.82
    cx = size / 2
    half = (size - margin * 2) / 2

    shield = [
        (cx, top),
        (cx + half, top + size * 0.08),
        (cx + half, size * 0.55),
        (cx, bot),
        (cx - half, size * 0.55),
        (cx - half, top + size * 0.08),
    ]
    line_w = max(1, int(size * 0.07))
    d.line(shield + [shield[0]], fill=(255, 255, 255, 235), width=line_w, joint="curve")

    # Check
    pts = [
        (cx - size * 0.13, cx - size * 0.02),
        (cx - size * 0.03, cx + size * 0.10),
        (cx + size * 0.18, cx - size * 0.16),
    ]
    d.line(pts, fill=(255, 255, 255, 245), width=line_w, joint="curve")

    return base


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for s in SIZES:
        img = draw_shield(s)
        out = OUT_DIR / f"icon{s}.png"
        img.save(out, format="PNG")
        print(f"[OK] {out.relative_to(OUT_DIR.parent)}  ({s}x{s})")


if __name__ == "__main__":
    main()
