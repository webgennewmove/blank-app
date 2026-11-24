"""Roblox-style painted faces matching the reference: small black oval eyes with one glint, D-shaped open smile
with a white teeth strip, no blush. Texture covers +/-0.40 head units (1280 px per unit at N=1024)."""
from PIL import Image, ImageDraw
import math, os
OUT = "/home/claude/zara/facetex2"; os.makedirs(OUT, exist_ok=True)
N = 1024; U = N / 0.8
def px(u): return N / 2 + u * U
def py(z): return N / 2 - z * U

def lin2srgb(c):
    return tuple(int(round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055))) for v in c)

BLACK = (20, 16, 22, 255); WHITE = (255, 255, 255, 255); MOUTH = (92, 24, 30, 255); TONGUE = (205, 85, 95, 255); TEAR = (90, 190, 255, 255)
EX, EZ, ERX, ERY = 0.19, 0.08, 0.062, 0.098     # eye centre x offset, height, radii (head units)
MZ = -0.075                                      # mouth top line

def eye(d, x, z, k=1.0, glint=True):
    cx, cy, rx, ry = px(x), py(z), ERX * U * k, ERY * U * k
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=BLACK)
    if glint:
        g = 0.36 * rx; gx, gy = cx + rx * 0.32, cy - ry * 0.42
        d.ellipse([gx - g, gy - g, gx + g, gy + g], fill=WHITE)

def arc(d, cx, cy, w, h, th, up=True, col=BLACK):
    pts = [(cx + (i / 30 * 2 - 1) * w / 2, cy + (h * (1 - (i / 30 * 2 - 1) ** 2)) * (1 if up else -1)) for i in range(31)]
    d.line(pts, fill=col, width=th, joint="curve")
    for x, y in (pts[0], pts[-1]): d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=col)

def dmouth(d, w, h, teeth=True, tongue=False, top=MZ, cx=0.0):
    """D-shaped open smile: flat top edge, rounded bottom (the reference mouth)"""
    x0, x1, y0 = px(cx - w / 2), px(cx + w / 2), py(top); hh = h * U
    d.chord([x0, y0 - hh, x1, y0 + hh], 0, 180, fill=MOUTH)
    if tongue: d.chord([px(cx - w * 0.28), y0 + hh * 0.35, px(cx + w * 0.28), y0 + hh * 1.25], 180, 360, fill=TONGUE)
    if teeth:
        tw, th = w * 0.62 * U / 2, 0.034 * U
        d.rounded_rectangle([px(cx) - tw, y0 - 2, px(cx) + tw, y0 + th], radius=th * 0.35, fill=WHITE)

def brows(d, slope, z=0.235, th=22):
    for s in (-1, 1):
        x = s * EX; k = slope * s
        d.line([(px(x - 0.07), py(z + k * 0.03)), (px(x + 0.07), py(z - k * 0.03))], fill=BLACK, width=th)
        for xx, zz in ((x - 0.07, z + k * 0.03), (x + 0.07, z - k * 0.03)):
            d.ellipse([px(xx) - th / 2, py(zz) - th / 2, px(xx) + th / 2, py(zz) + th / 2], fill=BLACK)

def face(kind, skin_lin):
    skin = lin2srgb(skin_lin) + (255,)
    im = Image.new("RGBA", (N, N), skin); d = ImageDraw.Draw(im, "RGBA")
    if kind in ("happy", "talk", "sad", "scared", "determined"):
        for s in (-1, 1): eye(d, s * EX, EZ)
    if kind == "excited":
        for s in (-1, 1): eye(d, s * EX, EZ + 0.01, 1.15)
    if kind == "shocked":
        for s in (-1, 1): eye(d, s * EX, EZ + 0.02, 1.3)
    if kind in ("laugh", "blink"):
        for s in (-1, 1): arc(d, px(s * EX), py(EZ - 0.01), ERX * 2.4 * U, 0.035 * U, 20, up=(kind == "blink"))
    if kind == "smug":
        for s in (-1, 1):
            eye(d, s * EX, EZ - 0.01)
            d.rectangle([px(s * EX - 0.09), py(EZ + 0.12), px(s * EX + 0.09), py(EZ + 0.005)], fill=skin)
            d.line([(px(s * EX - 0.075), py(EZ + 0.005)), (px(s * EX + 0.075), py(EZ + 0.005))], fill=BLACK, width=20)
    if kind == "determined":
        brows(d, -1.2, z=EZ + 0.13)
    if kind == "scared": brows(d, 1.1)
    if kind == "sad":
        brows(d, 1.3, z=0.225)
        d.ellipse([px(-EX - 0.02), py(EZ - 0.12), px(-EX + 0.02), py(EZ - 0.18)], fill=TEAR)
    # mouths
    if kind in ("happy", "blink"): dmouth(d, 0.3, 0.1)
    elif kind == "excited": dmouth(d, 0.36, 0.14, tongue=True)
    elif kind == "laugh": dmouth(d, 0.38, 0.16, tongue=True)
    elif kind == "talk": dmouth(d, 0.24, 0.12)
    elif kind == "smug": arc(d, px(0.05), py(MZ - 0.02), 0.24 * U, 0.04 * U, 18, up=True)
    elif kind == "sad": arc(d, px(0), py(MZ - 0.06), 0.2 * U, 0.035 * U, 18, up=False)
    elif kind == "shocked":
        d.ellipse([px(-0.06), py(MZ + 0.01), px(0.06), py(MZ - 0.15)], fill=MOUTH)
    elif kind == "scared":
        pts = [(px(-0.12 + i * 0.012), py(MZ - 0.04 + (0.012 if (i // 2) % 2 else -0.012))) for i in range(21)]
        d.line(pts, fill=BLACK, width=18, joint="curve")
    elif kind == "determined":
        dmouth(d, 0.22, 0.05, teeth=True)
    return im.resize((512, 512), Image.LANCZOS)

KINDS = ["happy", "excited", "laugh", "sad", "shocked", "scared", "determined", "blink", "smug", "talk"]
def path(kind, skin): return f"{OUT}/{kind}_{'_'.join(f'{v:.3f}' for v in skin)}.png"
def ensure(kind, skin):
    p = path(kind, skin)
    if not os.path.exists(p): face(kind, skin).convert("RGB").save(p)
    return p

if __name__ == "__main__":
    skin = (0.9, 0.6, 0.38)
    ims = [Image.open(ensure(k, skin)).resize((200, 200)) for k in KINDS]
    W = Image.new("RGB", (200 * 5, 400))
    for i, im in enumerate(ims): W.paste(im, ((i % 5) * 200, (i // 5) * 200))
    W.save("/home/claude/zara/egg/faces_sheet.png")
