"""IN MY TOWN 'The Game' compositor: cinematic grade (teal/amber), bloom, vignette, grain, word captions, light feedback FX,
Rico's phone UI, emerald vortex + rays. No outro: the last frame cuts back to the first (loop)."""
import os, sys, json, math, random, re, subprocess
os.environ["EGG_NOMAIN"] = "1"; _argv = sys.argv[:]; sys.argv = ["x"]
exec(open("/home/claude/zara/egg_compose.py").read())
sys.argv = _argv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
E = "/home/claude/zara/town/ep"; FR = f"{E}/frames"
TL = json.load(open(f"{E}/timeline.json")); ORDER = TL["shots"]; DUR = TL["dur"]; LEADS = TL["lead"]; VOD = TL["vo"]; WORDS = TL["words"]
HOT = {"never", "game", "jayden", "don't!", "don't", "obviously", "rolled", "rolled.", "rolled!", "chair", "chair.", "filming", "story",
       "six", "five", "sixth", "whiskers", "whiskers!", "cat", "cat!", "dice", "dice!", "anymore", "final", "selected", "gladiator"}
GREEN = (90, 255, 150); GOLD = (255, 205, 60)
def wt(s, word, k=0):
    word = word.lower().strip(".,!?")
    hits = [a for w, a, b in WORDS[s] if w.lower().strip(".,!?…") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0

def build_fx(s, d):
    fx = FX(s, d); X = W / 2
    if s == "s03": fx.flash(0.6, (140, 255, 180), 0.4, 0.35); fx.sparkle(0.5, d, X, H * 0.45, 260, (170, 255, 200), 22)
    elif s == "s04": fx.punch(wt(s, "don't!"), 0.08)
    elif s == "s05": tr = wt(s, "rolled."); fx.punch(tr, 0.1); fx.word("ROLLED.", tr, X, 300, 120, GREEN, 0.9, -5)
    elif s == "s05b": fx.flash(d * 0.72, (150, 255, 190), 0.4, 0.6); fx.shake(d * 0.72, d * 0.72 + 0.3, 8); fx.ring(d * 0.72, X, H * 0.55, (150, 255, 190), 0.7, 600)
    elif s == "s06": fx.flash(0.15, (200, 255, 255), 0.25, 0.7); fx.shake(0.15, 0.6, 14); fx.word("SMASH!", 0.18, X, 330, 150, (200, 240, 255), 0.9, -6)
    elif s == "s07": c = 2.95; fx.word("CRASH!", c, X, 330, 160, (255, 120, 60), 0.9, 7); fx.shake(c, c + 0.45, 18); fx.flash(c, (255, 255, 255), 0.2, 0.6); fx.punch(c, 0.2)
    elif s == "s08": fx.shake(0.1, 0.9, 12); fx.word("RAAAWR!", 0.25, X, 300, 140, (120, 255, 90), 1.0, -6); fx.pop("🐊", 0.4, 600, 380, 1.1)
    elif s == "s09": tc = wt(s, "chair."); fx.word("WITH A CHAIR", tc, X, 290, 100, GOLD, 1.0, -5); fx.pop("🪑", tc + 0.1, 120, 420, 1.0); fx.punch(tc, 0.1)
    elif s == "s10": fx.pop("📱", 0.3, 600, 420, 0.9); ts = wt(s, "story."); fx.pop("🔥", ts, 120, 420, 1.0)
    elif s == "s11": fx.pulse(0, d, (40, 255, 120), 1.2, 0.18); fx.word("SIX PLAYERS", wt(s, "six"), X, 280, 104, GREEN, 1.6, 0); fx.word("SIX SQUARES", wt(s, "six", 1), X, 400, 104, GREEN, 1.4, 0)
    elif s == "s12": tf = wt(s, "five"); fx.word("5", tf, X, 330, 200, (255, 255, 255), 1.4, 0)
    elif s == "s13": fx.pop("👀", 0.4, 600, 380, 1.0)
    elif s == "s14":
        for i, w_ in enumerate(("whiskers!", "cat!", "rolled!", "dice!")):
            t = wt(s, w_); fx.punch(t, 0.08)
        td = wt(s, "dice!"); fx.flash(td, (150, 255, 190), 0.35, 0.7); fx.shake(td, td + 0.4, 10)
    elif s == "s15": fx.flash(d * 0.58, (220, 255, 230), 0.35, 1.0); fx.shake(0, d * 0.58, 6)
    elif s == "s17": tr = d * 0.3; fx.word("ROAR!", tr, X, 330, 170, GOLD, 1.0, -5); fx.shake(tr, tr + 0.6, 14); fx.flash(tr, (255, 240, 180), 0.25, 0.4); fx.pop("👑", d * 0.7, 600, 330, 1.1)
    elif s == "s18": tf = wt(s, "final"); fx.pulse(tf, d, (40, 255, 120), 1.4, 0.22); fx.shake(tf + 1.2, d, 3)
    for i, it in enumerate(fx.items):
        if it[0] == "text":
            k, txt, t0, x, y, sz, fill, life, rot = it
            fx.items[i] = (k, txt, t0, x, y, fit(txt, sz, 0.82), fill, life, rot)
    return fx

def cine_grade(img, s):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    jungle = s in ("s15", "s16", "s17", "s18", "s19")
    lift = 1.35 if jungle else 1.18
    a = np.clip(a * lift, 0, 1)
    a = a + (np.array([-0.02, 0.025, 0.035]) * (1 - lum)) + (np.array([0.05, 0.02, -0.03]) * lum)   # teal shadows, amber highlights
    a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(1.18)
    # bloom
    br = out.point(lambda v: max(0, v - 200) * 2)
    bl = br.filter(ImageFilter.GaussianBlur(22))
    out = ImageChops.add(out, bl, scale=2.2)
    return out.convert("RGBA")
_VIG = None
def vignette(img):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        al = np.clip((r - 0.65) / 0.6, 0, 1) ** 1.6 * 200
        _VIG = Image.fromarray(np.dstack([np.zeros((H, W, 3)), al]).astype(np.uint8), "RGBA")
    img.alpha_composite(_VIG)
_GR = [Image.fromarray((np.random.default_rng(k).normal(128, 18, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)).resize((W, H)) for k in range(4)]
def grain(img, f):
    g = _GR[f % 4].convert("RGBA"); g.putalpha(14); img.alpha_composite(g)

def phone_ui(img, t, selfie=False):
    d = ImageDraw.Draw(img); m = 34; L = 70; c = (255, 255, 255, 230)
    for (x, y, sx, sy) in ((m, 150, 1, 1), (W - m, 150, -1, 1), (m, H - 220, 1, -1), (W - m, H - 220, -1, -1)):
        d.line([(x, y), (x + sx * L, y)], fill=c, width=6); d.line([(x, y), (x, y + sy * L)], fill=c, width=6)
    if int(t * 2) % 2 == 0: d.ellipse([m + 18, 180, m + 44, 206], fill=(255, 40, 40, 255))
    paste_center(img, text_img(f"REC 00:{int(t) + 12:02d}", 34, (255, 255, 255), 5), m + 170, 193, 1.0)
    paste_center(img, text_img("1080p · 60", 26, (255, 255, 255), 4), W - m - 110, 193, 1.0)
    d.rectangle([W - m - 70, 222, W - m - 18, 246], outline=c, width=3); d.rectangle([W - m - 66, 226, W - m - 40, 242], fill=(120, 255, 120, 230))

def shot_frame(s, f, n, fx, trk, cache):
    t = (f - 1) / FPS; T = n / FPS
    p = f"{FR}/{s}/{f:04d}.png"
    if os.path.exists(p): cache["last"] = p
    base = Image.open(cache["last"]).convert("RGBA") if cache.get("last") else Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if base.size != (W, H): base = base.resize((W, H))
    img = cine_grade(base, s)
    ex, ey = (trk[f - 1][0] * W, trk[f - 1][1] * H) if trk and trk[f - 1] else (W / 2, H * 0.4)
    # hypnotic layers
    if s in ("s01", "s19"): glow(img, W / 2, H * 0.5, 320 + 30 * math.sin(t * 4), (90, 255, 150), 0.35)
    if s == "s11": tunnel(img, W / 2, H * 0.62, t, 0.55, 7, 1000, (90, 255, 150), 10, 0.35, 1.5)
    if s == "s14" and t > wt(s, "dice!"): tunnel(img, W / 2, H * 0.6, t, 0.35, 7, 900, (120, 255, 170), 12, 0.5, 1.4)
    if s == "s15":
        sp = T * 0.58
        if t < sp:
            k = t / sp; rays = Image.new("RGBA", (W, H)); sunburst(rays, W / 2, H * 0.42, t * (1.5 + 4 * k), (90, 255, 150), None, 22, 0.08 + 0.35 * k)
            img.alpha_composite(rays); tunnel(img, W / 2, H * 0.42, t, 0.5 - 0.3 * k, 9, 1300, (140, 255, 180), 14, 0.3 + 0.5 * k, 1.3)
        elif t < sp + 0.6:
            img.alpha_composite(Image.new("RGBA", (W, H), (220, 255, 230, int(255 * max(0, 1 - (t - sp) / 0.6)))))
    if s == "s17" and t > T * 0.45:
        k = min(1, (t - T * 0.45) / 0.6); rays = Image.new("RGBA", (W, H)); sunburst(rays, ex, ey, t * 0.8, (255, 215, 90), None, 24, 0.22 * k)
        img.alpha_composite(rays); glow(img, ex, ey, 260, (255, 210, 90), 0.55 * k)
    if s == "s18": tunnel(img, W / 2, H * 0.55, t, 0.9, 6, 1300, (90, 255, 150), 8, 0.22, 1.2)
    z, dx, dy = fx.cam(t)
    if z != 1.0 or dx or dy:
        zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
        x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
    vignette(img); grain(img, f)
    fx.draw(img, t); fx.overlay(img, t)
    if s == "s10": phone_ui(img, t)
    if s == "s11" and t > wt(s, "six"): counter(img, "SQUARES:", min(6, 1 + int((t - wt(s, "six")) * 8)), t, GREEN, y=170, pulse=False)
    caption(img, s, t)
    return img

def caption(img, s, t, hide_after=None):
    ws = WORDS[s]
    for i, (w, a, b) in enumerate(ws):
        nxt = ws[i + 1][1] if i + 1 < len(ws) else b + 0.3
        if a <= t < min(nxt, b + 0.35):
            clean = re.sub(r"[^\w']", "", w).lower(); hot = clean in HOT or w.lower() in HOT
            u = (t - a) / 0.16; sc = 1.0 + (0.22 if hot else 0.08) * max(0, 1 - u)
            txt = re.sub(r"[.,…\-]+$", "", w).upper()
            paste_center(img, text_img(txt, fit(txt, 96 if hot else 84, 0.78, 11), GREEN if hot else (255, 255, 255), 11), W / 2, H * 0.74, sc)
            return

if __name__ == "__main__" and not os.environ.get("TOWN_NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{E}/town_noaudio.mp4", set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
