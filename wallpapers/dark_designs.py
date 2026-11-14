"""Dark feminine wallpaper designs. Coordinates are fractions of S so drafts render fast.
Usage: SIZE=2732 python3 dark_designs.py <design> <palette> <out.jpg>
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = int(os.environ.get("SIZE", 2732))


def H(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


PALETTES = {
    "midnight": dict(bg1=H("#0E0D16"), bg2=H("#231C30"), mid=H("#3A3049"), pink=H("#F4C9D2"), accent=H("#E9D5B5")),
    "black": dict(bg1=H("#0B0A0D"), bg2=H("#1E1A21"), mid=H("#332B36"), pink=H("#FF9EBB"), accent=H("#F6E3E8")),
    "wine": dict(bg1=H("#120A0C"), bg2=H("#2E1219"), mid=H("#5C1A2B"), pink=H("#F2B8C6"), accent=H("#EBCBA4")),
    "charcoal": dict(bg1=H("#0F0E11"), bg2=H("#24252C"), mid=H("#46484F"), pink=H("#E6AE9C"), accent=H("#D9C3A5")),
}


def p(*v):
    return tuple(int(x * S) for x in v)


def gradient(c1, c2):
    t = np.linspace(0, 1, S)[:, None, None]
    arr = np.array(c1) * (1 - t) + np.array(c2) * t
    return Image.fromarray(np.repeat(arr, S, axis=1).astype(np.uint8)).convert("RGBA")


def glow(img, box, color, blur, alpha):
    lay = Image.new("RGBA", (S, S), color + (0,))
    ImageDraw.Draw(lay).ellipse(p(*box), fill=color + (alpha,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur * S)))


def stars(img, color, n=160, ymax=1.0, seed=11, box=None):
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", (S, S), color + (0,))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box or (0, 0, 1, ymax)
    for _ in range(n):
        x, y = rng.uniform(x0, x1) * S, rng.uniform(y0, y1) * S
        r = rng.choice([0.0011, 0.0015, 0.002, 0.0028]) * S
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(rng.integers(90, 230)),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.0005 * S)))


def grain(img, amount=4):
    rng = np.random.default_rng(7)
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    arr += rng.integers(-amount, amount + 1, (S, S, 1), dtype=np.int16)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------- designs ----------

def silk(c):
    """Flowing satin ribbons with a pink sheen."""
    y, x = np.mgrid[0:1:S * 1j, 0:1:S * 1j]
    wave = np.sin(7 * x + 3.2 * np.sin(2.4 * y + 1.3) + 5 * y)
    band = np.exp(-((y - (0.55 + 0.18 * np.sin(3 * x + 0.5))) ** 2) / 0.05)
    sheen = np.clip((wave * 0.5 + 0.5) ** 3 * band, 0, 1)[..., None]
    base = np.array(c["bg1"]) * (1 - y[..., None]) + np.array(c["bg2"]) * y[..., None]
    shade = np.clip(wave * 0.5 + 0.5, 0, 1)[..., None] * band[..., None]
    arr = base * (1 - 0.6 * shade) + np.array(c["mid"]) * 0.6 * shade
    arr = arr * (1 - 0.75 * sheen) + np.array(c["pink"]) * 0.75 * sheen
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA").filter(ImageFilter.GaussianBlur(0.002 * S))
    return grain(img)


def flower(d, cx, cy, r, color, petals, alpha, rot=0.0):
    for i in range(petals):
        a = rot + 2 * math.pi * i / petals
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        d.ellipse((px - r * 0.5, py - r * 0.5, px + r * 0.5, py + r * 0.5), fill=color + (alpha,))


def florals(c):
    """Soft blooms tumbling in from the corners."""
    img = gradient(c["bg1"], c["bg2"])
    for blur, items in [
        (0.006, [(0.08, 0.12, 0.17, c["mid"], 7, 200), (0.95, 0.9, 0.2, c["mid"], 8, 200)]),
        (0.0015, [(0.2, 0.05, 0.11, c["pink"], 6, 210), (0.02, 0.32, 0.08, c["accent"], 5, 170),
                  (0.82, 0.82, 0.12, c["pink"], 7, 210), (0.98, 0.66, 0.07, c["accent"], 5, 170),
                  (0.68, 0.97, 0.08, c["pink"], 6, 150)]),
    ]:
        lay = Image.new("RGBA", (S, S), c["pink"] + (0,))
        d = ImageDraw.Draw(lay)
        for (x, y, r, col, n, a) in items:
            flower(d, x * S, y * S, r * S, col, n, a, rot=x * 3)
            cr = r * S * 0.16
            d.ellipse((x * S - cr, y * S - cr, x * S + cr, y * S + cr), fill=c["bg1"] + (180,))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur * S)))
    stars(img, c["accent"], n=40, seed=4, box=(0.25, 0.2, 0.75, 0.8))
    return grain(img)


def celestial(c):
    """Crescent moon with a constellation."""
    img = gradient(c["bg1"], c["bg2"])
    stars(img, c["accent"], n=180)
    glow(img, (0.36, 0.2, 0.64, 0.48), c["pink"], 0.04, 70)
    lay = Image.new("RGBA", (S, S), c["pink"] + (0,))
    d = ImageDraw.Draw(lay)
    d.ellipse(p(0.4, 0.24, 0.6, 0.44), fill=c["pink"] + (255,))
    d.ellipse(p(0.445, 0.215, 0.645, 0.415), fill=(0, 0, 0, 0))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.0015 * S)))
    pts = [(0.14, 0.62), (0.24, 0.56), (0.33, 0.64), (0.45, 0.6), (0.52, 0.7), (0.66, 0.66), (0.78, 0.74), (0.86, 0.66)]
    lay = Image.new("RGBA", (S, S), c["accent"] + (0,))
    d = ImageDraw.Draw(lay)
    d.line([p(*q) for q in pts], fill=c["accent"] + (110,), width=max(2, int(0.0012 * S)))
    for q in pts:
        x, y = p(*q)
        r = 0.005 * S
        d.ellipse((x - r, y - r, x + r, y + r), fill=c["accent"] + (240,))
    img.alpha_composite(lay)
    return grain(img)


def window(c):
    """Night reading nook: arched window, moon, books on the sill."""
    img = gradient(c["bg1"], c["bg2"])
    x0, x1, top, sill = 0.3, 0.7, 0.3, 0.8
    w = x1 - x0
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse(p(x0, top, x1, top + w), fill=255)
    md.rectangle(p(x0, top + w / 2, x1, sill), fill=255)
    sky = gradient(c["mid"], c["bg1"])
    stars(sky, c["accent"], n=70, seed=2, box=(x0, top, x1, sill))
    glow(sky, (0.52, 0.38, 0.64, 0.5), c["pink"], 0.012, 255)
    img.paste(sky, (0, 0), mask)
    lay = Image.new("RGBA", (S, S), c["bg1"] + (0,))
    d = ImageDraw.Draw(lay)
    fw = max(4, int(0.008 * S))
    d.ellipse(p(x0, top, x1, top + w), outline=c["bg1"] + (255,), width=fw * 2)
    d.line(p(x0, top + w / 2, x0, sill), fill=c["bg1"] + (255,), width=fw * 2)
    d.line(p(x1, top + w / 2, x1, sill), fill=c["bg1"] + (255,), width=fw * 2)
    d.line(p(0.5, top, 0.5, sill), fill=c["bg1"] + (255,), width=fw)
    d.line(p(x0, top + w / 2 + 0.06, x1, top + w / 2 + 0.06), fill=c["bg1"] + (255,), width=fw)
    d.rectangle(p(x0 - 0.04, sill, x1 + 0.04, sill + 0.018), fill=c["mid"] + (255,))
    y = sill
    for bw, bh, col in [(0.13, 0.026, c["pink"]), (0.11, 0.022, c["accent"]), (0.12, 0.02, c["mid"])]:
        y -= bh
        d.rounded_rectangle(p(0.36, y, 0.36 + bw, y + bh - 0.003), radius=int(0.004 * S), fill=col + (255,))
    # little candle
    d.rounded_rectangle(p(0.6, sill - 0.05, 0.625, sill), radius=int(0.003 * S), fill=c["accent"] + (255,))
    img.alpha_composite(lay)
    glow(img, (0.595, sill - 0.08, 0.63, sill - 0.045), c["pink"], 0.004, 230)
    glow(img, (0.5, sill - 0.2, 0.72, sill + 0.05), c["pink"], 0.05, 40)
    return grain(img)


def controller(d, cx, cy, w, body, btn, alpha=255):
    """Generic rounded gamepad silhouette."""
    h = w * 0.55
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 3), radius=int(h * 0.4), fill=body + (alpha,))
    for sx in (-1, 1):
        gx = cx + sx * w * 0.32
        d.ellipse((gx - w * 0.2, cy - h * 0.2, gx + w * 0.2, cy + h * 0.55), fill=body + (alpha,))
    u = w * 0.045
    lx, ly = cx - w * 0.27, cy - h * 0.05
    d.rectangle((lx - u * 2.4, ly - u * 0.8, lx + u * 2.4, ly + u * 0.8), fill=btn + (alpha,))
    d.rectangle((lx - u * 0.8, ly - u * 2.4, lx + u * 0.8, ly + u * 2.4), fill=btn + (alpha,))
    rx, ry = cx + w * 0.27, cy - h * 0.05
    for ox, oy in ((0, -2.2), (0, 2.2), (-2.2, 0), (2.2, 0)):
        bx, by = rx + ox * u, ry + oy * u
        d.ellipse((bx - u, by - u, bx + u, by + u), fill=btn + (alpha,))


def gamer_nook(c):
    """Night window, controller and mug on the sill, lamp glow."""
    img = gradient(c["bg1"], c["bg2"])
    x0, x1, top, sill = 0.27, 0.73, 0.24, 0.74
    w = x1 - x0
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse(p(x0, top, x1, top + w), fill=255)
    md.rectangle(p(x0, top + w / 2, x1, sill), fill=255)
    sky = gradient(c["mid"], c["bg1"])
    stars(sky, c["accent"], n=80, seed=2, box=(x0, top, x1, sill))
    glow(sky, (0.55, 0.32, 0.66, 0.43), c["pink"], 0.012, 255)
    img.paste(sky, (0, 0), mask)
    lay = Image.new("RGBA", (S, S), c["bg1"] + (0,))
    d = ImageDraw.Draw(lay)
    fw = max(4, int(0.008 * S))
    d.ellipse(p(x0, top, x1, top + w), outline=c["bg1"] + (255,), width=fw * 2)
    d.line(p(0.5, top, 0.5, sill), fill=c["bg1"] + (255,), width=fw)
    d.line(p(x0, top + w / 2 + 0.06, x1, top + w / 2 + 0.06), fill=c["bg1"] + (255,), width=fw)
    d.rectangle(p(x0 - 0.05, sill, x1 + 0.05, sill + 0.02), fill=c["mid"] + (255,))
    controller(d, 0.4 * S, (sill - 0.032) * S, 0.15 * S, c["pink"], c["bg2"])
    # mug with heart
    d.rounded_rectangle(p(0.58, sill - 0.075, 0.645, sill), radius=int(0.008 * S), fill=c["accent"] + (255,))
    d.ellipse(p(0.635, sill - 0.06, 0.668, sill - 0.022), outline=c["accent"] + (255,), width=int(0.007 * S))
    hx, hy, hr = 0.6125 * S, (sill - 0.04) * S, 0.009 * S
    d.ellipse((hx - hr * 2, hy - hr, hx, hy + hr), fill=c["pink"] + (255,))
    d.ellipse((hx, hy - hr, hx + hr * 2, hy + hr), fill=c["pink"] + (255,))
    d.polygon([(hx - hr * 2, hy + hr * 0.2), (hx + hr * 2, hy + hr * 0.2), (hx, hy + hr * 2.4)], fill=c["pink"] + (255,))
    img.alpha_composite(lay)
    # steam
    lay = Image.new("RGBA", (S, S), c["accent"] + (0,))
    d = ImageDraw.Draw(lay)
    for k in (0, 1):
        x = 0.598 + k * 0.03
        d.arc(p(x - 0.01, sill - 0.13, x + 0.01, sill - 0.09), 90, 270, fill=c["accent"] + (120,), width=int(0.004 * S))
        d.arc(p(x - 0.01, sill - 0.17, x + 0.01, sill - 0.13), 270, 90, fill=c["accent"] + (120,), width=int(0.004 * S))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.002 * S)))
    glow(img, (0.25, sill - 0.25, 0.75, sill + 0.12), c["pink"], 0.06, 45)
    return grain(img)


def pixel(c, n=None):
    """Soft pixel-art night sky with hearts and stars. Bigger n = smaller pixels, more zoomed out."""
    n = n or int(os.environ.get("PIXEL_N", 96))
    o = (n - 96) // 2  # keep the 96-grid scene centred
    sm = Image.new("RGB", (n, n), c["bg1"])
    d = ImageDraw.Draw(sm)
    sky = lambda yy: tuple(int(a * (1 - yy / n) + b * yy / n) for a, b in zip(c["bg1"], c["bg2"]))
    for yy in range(n):
        d.line((0, yy, n, yy), fill=sky(yy))
    rng = np.random.default_rng(5)
    for _ in range(int(70 * (n / 96) ** 2)):
        d.point((int(rng.integers(0, n)), int(rng.integers(0, n * 0.75))), fill=c["accent"])
    for sx, sy in [(14, 12), (78, 20), (60, 8), (30, 40), (84, 52)]:
        sx, sy = sx + o, sy + o
        d.point([(sx, sy), (sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)], fill=c["pink"])
    d.ellipse((58 + o, 22 + o, 76 + o, 40 + o), fill=c["pink"])
    for yy in range(19 + o, 38 + o):
        for xx in range(63 + o, 82 + o):
            if (xx - 72 - o) ** 2 + (yy - 28 - o) ** 2 <= 81:
                d.point((xx, yy), fill=sky(yy))
    heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    for hx, hy, col in [(18, 62, c["pink"]), (44, 70, c["accent"]), (70, 64, c["pink"])]:
        for j, row in enumerate(heart):
            for i, ch in enumerate(row):
                if ch == "1":
                    d.point((hx + o + i, hy + o + j), fill=col)
    for i in range(n):
        h = int(n - 12 + 3 * math.sin(i / 7) + 2 * math.sin(i / 3))
        d.line((i, h, i, n), fill=c["mid"])
    for i in range(n):
        h = int(n - 6 + 2 * math.sin(i / 5 + 1))
        d.line((i, h, i, n), fill=c["bg1"])
    img = sm.resize((S, S), Image.NEAREST).convert("RGBA")
    return grain(img, 3)


def pattern(c):
    """Scattered soft gaming icons: controllers, hearts, stars."""
    img = gradient(c["bg1"], c["bg2"])
    lay = Image.new("RGBA", (S, S), c["pink"] + (0,))
    d = ImageDraw.Draw(lay)
    step = 0.16
    for r in range(8):
        for q in range(8):
            x = (q + (0.5 if r % 2 else 0)) * step * S
            y = (r * step * 0.9 + 0.05) * S
            k = (r * 3 + q) % 3
            col = [c["pink"], c["accent"], c["mid"]][(r + q) % 3]
            if k == 0:
                controller(d, x, y, 0.06 * S, col, c["bg1"], 150)
            elif k == 1:
                hr = 0.011 * S
                d.ellipse((x - hr * 2, y - hr, x, y + hr), fill=col + (150,))
                d.ellipse((x, y - hr, x + hr * 2, y + hr), fill=col + (150,))
                d.polygon([(x - hr * 2, y + hr * 0.2), (x + hr * 2, y + hr * 0.2), (x, y + hr * 2.4)], fill=col + (150,))
            else:
                rr = 0.016 * S
                pts = [(x + math.cos(math.pi / 2 + i * math.pi / 5) * (rr if i % 2 == 0 else rr * 0.45),
                        y - math.sin(math.pi / 2 + i * math.pi / 5) * (rr if i % 2 == 0 else rr * 0.45)) for i in range(10)]
                d.polygon(pts, fill=col + (150,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.0008 * S)))
    glow(img, (0.2, 0.3, 0.8, 0.8), c["bg1"], 0.08, 150)
    return grain(img)


DESIGNS = dict(silk=silk, florals=florals, celestial=celestial, window=window,
               gamer_nook=gamer_nook, pixel=pixel, pattern=pattern)

if __name__ == "__main__":
    design, pal, out = sys.argv[1:4]
    DESIGNS[design](PALETTES[pal]).save(out, quality=92)
