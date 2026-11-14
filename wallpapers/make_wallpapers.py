"""Cosy beige wallpapers for iPad Pro 12.9" (2732x2732 square, works in both orientations)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import os, sys
S = int(os.environ.get("SIZE", 2732))
K = S / 2732  # scale factor for drafts
CREAM = (243, 235, 221)
WARM = (230, 216, 194)
SAGE = (168, 181, 154)
SAGE_DARK = (132, 148, 120)
CLAY = (201, 162, 126)
BROWN = (150, 115, 88)
PINK = (228, 178, 172)
BLUSH = (240, 205, 198)
OUT = __file__.rsplit("/", 1)[0]


def gradient(top, bottom):
    t = np.linspace(0, 1, S)[:, None, None]
    arr = np.array(top) * (1 - t) + np.array(bottom) * t
    return Image.fromarray(np.repeat(arr, S, axis=1).astype(np.uint8), "RGB")


def blob(img, box, color, blur, alpha=255):
    box = tuple(int(v * K) for v in box); blur = blur * K
    layer = Image.new("RGBA", (S, S), color + (0,))
    ImageDraw.Draw(layer).ellipse(box, fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def grain(img, amount=6):
    rng = np.random.default_rng(7)
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    arr += rng.integers(-amount, amount + 1, (S, S, 1), dtype=np.int16)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def home():
    img = gradient(CREAM, WARM).convert("RGBA")
    blob(img, (-700, -600, 1300, 1200), SAGE, 220, 200)
    blob(img, (1700, 1800, 3500, 3600), PINK, 240, 190)
    blob(img, (1900, -300, 3100, 800), SAGE_DARK, 260, 90)
    blob(img, (-400, 2000, 900, 3300), BLUSH, 260, 150)
    blob(img, (1100, 900, 1900, 1700), BLUSH, 300, 70)
    out = grain(img)
    if S == 2732: out.save(f"{OUT}/cosy-beige-home.png", optimize=True)
    return out


def lock():
    img = gradient(CREAM, WARM).convert("RGBA")
    # soft sun behind the arch
    blob(img, (S // 2 - 430, 1150, S // 2 + 430, 2010), PINK, 40, 230)
    # arched window shape, bottom centre (clock stays clear at top)
    layer = Image.new("RGBA", (S, S), CREAM + (0,))
    d = ImageDraw.Draw(layer)
    w, top = 1100, 1350
    x0, x1 = S // 2 - w // 2, S // 2 + w // 2
    d.ellipse((x0, top, x1, top + w), fill=SAGE + (255,))
    d.rectangle((x0, top + w // 2, x1, S), fill=SAGE + (255,))
    # inner arch line
    inset = 90
    d.ellipse((x0 + inset, top + inset, x1 - inset, top + w - inset), outline=CREAM + (150,), width=10)
    d.line((x0 + inset, top + w // 2, x0 + inset, S), fill=CREAM + (150,), width=10)
    d.line((x1 - inset, top + w // 2, x1 - inset, S), fill=CREAM + (150,), width=10)
    # stack of books on the sill
    books = [(560, 120, BROWN), (500, 110, PINK), (580, 100, SAGE_DARK)]
    sill = 2300
    d.rectangle((x0 - 60, sill, x1 + 60, sill + 36), fill=BROWN + (255,))
    y = sill
    for bw, bh, col in books:
        y -= bh
        d.rounded_rectangle((S // 2 - bw // 2, y, S // 2 + bw // 2, y + bh - 12), radius=18, fill=col + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(1.5))
    img.alpha_composite(layer)
    blob(img, (-600, -500, 1100, 1000), SAGE, 260, 120)
    blob(img, (1900, 2300, 3400, 3600), BLUSH, 260, 160)
    out = grain(img)
    if S == 2732: out.save(f"{OUT}/cosy-beige-lock.png", optimize=True)
    return out


def sky():
    """C: pink dusk sky over sage hills."""
    img = gradient(BLUSH, CREAM).convert("RGBA")
    blob(img, (900, 700, 1830, 1630), PINK, 30, 230)
    layer = Image.new("RGBA", (S, S), CREAM + (0,))
    d = ImageDraw.Draw(layer)
    for (cx, cy, rx, col) in [(600, 2700, 1700, SAGE), (2300, 2800, 1600, SAGE_DARK), (1300, 3100, 1900, CLAY)]:
        d.ellipse(tuple(int(v * K) for v in (cx - rx, cy - 600, cx + rx, cy + 1400)), fill=col + (255,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2 * K)))
    return grain(img)


def shelf():
    """D: minimal bookshelf along the bottom."""
    img = gradient(CREAM, WARM).convert("RGBA")
    blob(img, (1700, 300, 2500, 1100), PINK, 60, 200)
    layer = Image.new("RGBA", (S, S), CREAM + (0,))
    d = ImageDraw.Draw(layer)
    cols = [SAGE, PINK, BROWN, BLUSH, SAGE_DARK, CLAY, PINK, SAGE, BLUSH, BROWN, CLAY, SAGE_DARK, PINK, SAGE]
    rng = np.random.default_rng(3)
    widths = [int(rng.integers(110, 190)) for _ in cols]
    x, base = (S - sum(widths) - 18 * (len(cols) - 1)) // 2, 2350
    rng = np.random.default_rng(3)
    for i, c in enumerate(cols):
        w = int(rng.integers(110, 190)); h = int(rng.integers(420, 640))
        d.rounded_rectangle(tuple(int(v * K) for v in (x, base - h, x + w, base)), radius=int(14 * K), fill=c + (255,))
        x += w + 18
    d.rectangle(tuple(int(v * K) for v in (240, base, 2492, base + 40)), fill=BROWN + (255,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.2 * K)))
    return grain(img)


if __name__ == "__main__":
    which = sys.argv[1:] or ["home", "lock"]
    for name in which:
        globals()[name]()
