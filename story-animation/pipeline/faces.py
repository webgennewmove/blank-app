"""Smooth Roblox-style face textures, painted on the character's skin colour (opaque, sRGB)."""
from PIL import Image, ImageDraw, ImageFilter
import math, os
OUT = "/home/claude/zara/facetex"; os.makedirs(OUT, exist_ok=True)
N = 1024  # draw at 1024, store 512

def lin2srgb(c):
    return tuple(int(round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055))) for v in c)

BLACK = (22, 18, 24, 255); WHITE = (255, 255, 255, 255); MOUTH = (110, 20, 35, 255); TONGUE = (240, 110, 130, 255)
BLUSH = (255, 120, 140, 110); TEAR = (90, 190, 255, 255)

def thick_arc(d, cx, cy, w, h, th, up=True, col=BLACK):
    """smooth curve: parabola y = cy + h*(x/w*2)^2 (up=smile)"""
    pts = []
    for i in range(41):
        u = i / 40 * 2 - 1; x = cx + u * w / 2; y = cy + (h * (1 - u * u) if up else -h * (1 - u * u))
        pts.append((x, y))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]): d.line([(x0, y0), (x1, y1)], fill=col, width=th)
    for x, y in (pts[0], pts[-1]): d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=col)

def eye(d, cx, cy, rx, ry, glint=True):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=BLACK)
    if glint:
        d.ellipse([cx + rx * 0.05, cy - ry * 0.62, cx + rx * 0.62, cy - ry * 0.05], fill=WHITE)
        d.ellipse([cx - rx * 0.5, cy + ry * 0.25, cx - rx * 0.2, cy + ry * 0.55], fill=WHITE)

def face(kind, skin_lin):
    skin = lin2srgb(skin_lin) + (255,)
    im = Image.new("RGBA", (N, N), skin); d = ImageDraw.Draw(im, "RGBA")
    L, R = N * 0.33, N * 0.67; EY = N * 0.44
    blush = kind in ("happy", "excited", "laugh", "smug", "blink")
    if blush:
        bl = Image.new("RGBA", (N, N)); bd = ImageDraw.Draw(bl)
        for x in (N * 0.2, N * 0.8): bd.ellipse([x - 95, N * 0.6 - 45, x + 95, N * 0.6 + 45], fill=BLUSH)
        im.alpha_composite(bl.filter(ImageFilter.GaussianBlur(18)))
    if kind in ("happy", "excited", "sad", "determined", "smug", "talk"):
        big = 1.15 if kind == "excited" else 1.0
        eye(d, L, EY, 62 * big, 92 * big); eye(d, R, EY, 62 * big, 92 * big)
    if kind in ("shocked", "scared"):
        for x in (L, R):
            d.ellipse([x - 92, EY - 110, x + 92, EY + 110], fill=WHITE, outline=BLACK, width=14)
            d.ellipse([x - 34, EY - 40, x + 34, EY + 40], fill=BLACK)
            d.ellipse([x - 8, EY - 30, x + 16, EY - 8], fill=WHITE)
    if kind == "laugh":
        for x in (L, R): thick_arc(d, x, EY + 30, 150, 70, 30, up=False)
    if kind == "blink":
        for x in (L, R): thick_arc(d, x, EY + 10, 140, 30, 26, up=True)
    if kind == "sad":
        for x, s in ((L, -1), (R, 1)): d.line([(x - 70, EY - 150 - s * 30), (x + 70, EY - 150 + s * 30)], fill=BLACK, width=26)
        d.ellipse([L - 30, EY + 105, L + 10, EY + 175], fill=TEAR)
        d.polygon([(L - 30, EY + 140), (L - 10, EY + 80), (L + 10, EY + 140)], fill=TEAR)
    if kind in ("determined", "scared"):
        for x, s in ((L, 1), (R, -1)):
            k = s if kind == "determined" else -s
            d.line([(x - 75, EY - 140 - k * 30), (x + 75, EY - 140 + k * 30)], fill=BLACK, width=28)
    if kind == "smug":
        d.rectangle([L - 75, EY - 105, L + 75, EY - 40], fill=skin); d.rectangle([R - 75, EY - 105, R + 75, EY - 40], fill=skin)
        for x in (L, R): d.line([(x - 70, EY - 40), (x + 70, EY - 40)], fill=BLACK, width=22)
    MY = N * 0.72
    if kind in ("happy", "blink"):
        thick_arc(d, N / 2, MY - 40, 330, 90, 30, up=True)
    elif kind in ("excited", "laugh"):
        h = 170 if kind == "laugh" else 150
        d.chord([N / 2 - 190, MY - h - 40, N / 2 + 190, MY + h - 40], 0, 180, fill=MOUTH)
        d.chord([N / 2 - 120, MY + 20, N / 2 + 120, MY + h - 50], 180, 360, fill=TONGUE)
        d.rectangle([N / 2 - 160, MY - 40, N / 2 + 160, MY - 10], fill=WHITE)
    elif kind == "sad":
        thick_arc(d, N / 2, MY + 20, 260, 70, 28, up=False)
    elif kind == "shocked":
        d.ellipse([N / 2 - 85, MY - 120, N / 2 + 85, MY + 90], fill=MOUTH)
        d.ellipse([N / 2 - 50, MY + 10, N / 2 + 50, MY + 75], fill=TONGUE)
    elif kind == "scared":
        pts = [(N / 2 - 150 + i * 15, MY - 20 + (18 if (i // 2) % 2 else -18)) for i in range(21)]
        d.line(pts, fill=BLACK, width=22, joint="curve")
    elif kind == "determined":
        d.line([(N / 2 - 120, MY - 20), (N / 2 + 120, MY - 30)], fill=BLACK, width=28)
    elif kind == "smug":
        thick_arc(d, N / 2 + 40, MY - 40, 260, 60, 28, up=True)
        d.rectangle([N / 2 - 140, MY - 80, N / 2 - 40, MY + 10], fill=skin)
    elif kind == "talk":
        d.ellipse([N / 2 - 110, MY - 90, N / 2 + 110, MY + 40], fill=MOUTH)
    return im.resize((512, 512), Image.LANCZOS)

KINDS = ["happy", "excited", "laugh", "sad", "shocked", "scared", "determined", "blink", "smug", "talk"]
def path(kind, skin): return f"{OUT}/{kind}_{'_'.join(f'{v:.3f}' for v in skin)}.png"
def ensure(kind, skin):
    p = path(kind, skin)
    if not os.path.exists(p): face(kind, skin).convert("RGB").save(p)
    return p

if __name__ == "__main__":
    skin = (0.45, 0.27, 0.16)
    ims = [Image.open(ensure(k, skin)).resize((160, 160)) for k in KINDS]
    W = Image.new("RGB", (160 * 5, 320))
    for i, im in enumerate(ims): W.paste(im, ((i % 5) * 160, (i // 5) * 160))
    W.save("/tmp/faces.jpg")
