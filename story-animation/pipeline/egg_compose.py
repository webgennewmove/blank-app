"""IN MY TOWN Ep1 compositor: sky (day/night), grade, hypnotic layers (rotating sunbursts, tunnel rings, racing counters,
egg glow), FX pops, word captions, end card -> ffmpeg 1080x1920."""
import os, sys, json, math, random, re, subprocess
os.environ["NOMAIN"] = "1"
_src = open("/home/claude/zara/compose.py").read()
_src = _src.replace('W, H = 576, 1024', 'W, H = 720, 1280')
_src = _src.replace('TL = json.load(open(f"{Z}/timeline.json")); DUR = TL["dur"]; LEAD = TL["lead"]', 'TL = {}; DUR = {}; LEAD = 0')
_src = _src.replace('VOD = json.load(open(f"{Z}/vo/durs.json"))', 'VOD = {}')
exec(_src)
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

E = "/home/claude/zara/egg"; FR = f"{E}/frames"
TL = json.load(open(f"{E}/timeline.json")); ORDER = TL["shots"]; DUR = TL["dur"]; LEADS = TL["lead"]; VOD = TL["vo"]; WORDS = TL["words"]
NIGHT = {"e07", "e08", "e09", "e10", "e11", "e12a", "e12b", "e12c", "e13", "e14", "e15"}
HOT = {"everyone", "everyone!", "mom", "teacher", "cops", "most", "whole", "town", "one", "tiny", "cracked", "sad", "night", "golden", "mayor's",
       "never", "touch", "touched", "obviously", "run", "chasing", "definitely", "slammed", "crack", "silent", "not", "pet", "egg", "eggs"}

def wt(s, word, k=0):
    hits = [a for w, a, b in WORDS[s] if w.lower().strip(".,!?") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
def vo_end(s): return LEADS[s] + VOD[s]

# ---------------------------------------------------------------- skies
def night_sky():
    a = np.linspace(0, 1, H)[:, None]; top, bot = np.array((6, 10, 36)), np.array((44, 48, 112))
    g = top[None, :] * (1 - a) + bot[None, :] * a
    return Image.fromarray(np.repeat(g[:, None, :], W, axis=1).astype(np.uint8)).convert("RGBA")
SKY_DAY = sky((40, 130, 245), (170, 218, 255)); SKY_NIGHT = night_sky()
_r = random.Random(4); STARS = [(_r.uniform(0, W), _r.uniform(0, H * 0.6), _r.uniform(1, 3.2), _r.uniform(0, 6)) for _ in range(110)]
def stars(img, t):
    d = ImageDraw.Draw(img)
    for x, y, s, ph in STARS:
        a = int(255 * (0.55 + 0.45 * math.sin(t * 3 + ph))); d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 230, a))

# ---------------------------------------------------------------- hypnotic layers
def sunburst(base, cx, cy, ang, c1, c2, n=18, alpha=1.0, r=2600):
    lay = Image.new("RGBA", (W, H), c2 + (int(255 * alpha),) if c2 else (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(n):
        a0 = ang + k * 2 * math.pi / n; a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + math.cos(a0) * r, cy + math.sin(a0) * r), (cx + math.cos(a1) * r, cy + math.sin(a1) * r)], fill=c1 + (int(255 * alpha),))
    base.alpha_composite(lay)
def tunnel(img, cx, cy, t, period=0.45, K=7, maxr=1400, col=(255, 220, 90), width=18, a=0.8, power=1.6):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for k in range(K):
        u = ((t / period + k / K) % 1.0); r = maxr * u ** power
        al = int(255 * a * (1 - u) * min(1, u * 6)); w = max(2, int(width * (0.4 + u)))
        d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], outline=col + (al,), width=w)
    img.alpha_composite(lay)
def glow(img, cx, cy, rad, col=(255, 200, 60), a=0.7):
    g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
    for k in range(12, 0, -1):
        rr = rad * k / 12; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (int(255 * a * (1 - k / 12) ** 1.5 * 0.35),))
    img.alpha_composite(g)
def counter(img, label, v, t, col=(255, 226, 30), y=150, pulse=True):
    sc = 1.0 + (0.07 * abs(math.sin(t * 14)) if pulse else 0)
    txt = f"{label} {v:,}"; paste_center(img, text_img(txt, fit(txt, 50, 0.84, 8), col, 8), W / 2, y, sc)

def track(s):
    p = f"{FR}/{s}/track.json"
    return json.load(open(p)) if os.path.exists(p) else None

# ---------------------------------------------------------------- per-shot feedback
def build_fx(s, d):
    fx = FX(s, d); X = W / 2
    if s == "e01":
        fx.speed(0, d, 30); fx.punch(0.0, 0.12)
        for k, (x, y) in enumerate([(120, 330), (600, 300), (170, 560), (560, 600)]): fx.pop("🥚", 0.25 + k * 0.33, x, y, 0.9)
        te = wt(s, "everyone!"); fx.word("EVERYONE!", te, X, 300, 118, (255, 226, 30), 1.3, -7); fx.punch(te, 0.18); fx.shake(te, te + 0.35, 10)
    elif s == "e02":
        fx.pop("🤫", 0.2, 590, 330, 1.0); fx.word("MOM?!", wt(s, "mom"), 170, 300, 100, (255, 120, 180), 1.1, 8); fx.pop("🥚", wt(s, "eggs."), 130, 560, 0.8)
    elif s == "e03":
        fx.word("A+ THIEF", wt(s, "steals"), X, 290, 96, (120, 230, 120), 1.2, -6); fx.pop("📚", 0.2, 600, 330, 0.9); fx.pop("🤓", 1.2, 130, 380, 0.9)
    elif s == "e04":
        fx.speed(0, d, 26); fx.word("WEE-OO!", 0.15, X, 270, 104, (90, 200, 255), 1.0, 6); fx.pulse(0, d, (255, 0, 0), 2.0, 0.45)
        fx.pop("🚓", 0.6, 140, 360, 1.0); fx.word("COPS?!", wt(s, "cops"), X, 420, 110, (255, 226, 30), 1.1, -8); fx.punch(wt(s, "cops"), 0.14)
    elif s == "e05":
        fx.pop("👑", 0.3, 590, 330, 1.0); fx.pop("🤑", 1.4, 130, 360, 0.9); tw = wt(s, "whole"); fx.confetti(tw, X, 240, 90); fx.punch(tw, 0.14)
        fx.sparkle(0, d, X, 520, 300, (255, 240, 150), 24)
    elif s == "e06a":
        fx.pop("🙂", 0.25, 590, 330, 0.8); fx.pop("😐", wt(s, "one.") + 0.2, 590, 330, 0.9)
    elif s == "e06b":
        for w, x, y, c in (("tiny", 170, 320, (180, 220, 255)), ("cracked,", 540, 380, (200, 200, 200)), ("sad", 200, 470, (120, 170, 255))):
            fx.word(w.strip(",").upper(), wt(s, w.strip(",")), x, y, 86, c, 1.2, random.Random(x).uniform(-10, 10))
        fx.pop("🌧", 0.2, X, 230, 1.0, life=d, rise=0)
    elif s == "e07":
        fx.flash(0.0, (255, 255, 255), 0.2, 0.5); fx.pop("🌙", 0.4, 590, 300, 1.0, life=2.0, rise=20)
    elif s == "e08":
        tg = wt(s, "golden"); fx.word("GOLDEN EGG", tg, X, 260, 104, (255, 210, 40), 1.6, -5); fx.flash(tg, (255, 230, 140), 0.35, 0.7); fx.punch(tg, 0.16)
        fx.pop("🤩", 0.3, 130, 360, 1.0); fx.sparkle(0, d, X, 500, 330, (255, 235, 140), 30); fx.pop("🏛", wt(s, "mayor's"), 600, 380, 0.9)
    elif s == "e09":
        fx.word("RULE #1", wt(s, "rule"), X, 260, 118, (255, 70, 70), 1.6, -5); fx.pulse(0, d, (255, 0, 0), 1.2, 0.5); fx.pop("⚠", 0.3, 600, 400, 0.9)
        for w, y in (("never", 330), ("touch", 330)): fx.word(w.upper(), wt(s, w), X, y + 120, 92, (255, 255, 255), 0.75, 0)
    elif s == "e10":
        fx.pop("😏", 0.3, 130, 330, 1.0); tt = wt(s, "touched")
        fx.flash(tt, (255, 255, 255), 0.25, 0.8); fx.word("*touch*", tt, X, 300, 92, (255, 226, 30), 1.0, -8); fx.punch(tt, 0.18); fx.shake(tt, tt + 0.4, 10)
        fx.pulse(tt + 0.2, d, (255, 0, 0), 4.0, 0.6); fx.pop("🚨", tt + 0.15, 120, 300, 1.0); fx.pop("🚨", tt + 0.3, 600, 300, 1.0)
    elif s == "e11":
        fx.word("RUN!!", 0.0, X, 380, 190, (255, 60, 60), 1.15, -6); fx.punch(0.0, 0.22); fx.shake(0.0, d, 14); fx.speed(0, d, 34); fx.flash(0.0, (255, 40, 40), 0.3, 0.6)
    elif s == "e12a":
        fx.speed(0, d, 28); fx.pop("😡", 0.2, 590, 330, 1.0); fx.shake(0, d, 4)
    elif s == "e12b":
        fx.speed(0, d, 28); fx.pop("📏", 0.2, 130, 330, 1.0); fx.pop("😤", 0.6, 590, 330, 1.0); fx.shake(0, d, 4)
    elif s == "e12c":
        fx.speed(0, d, 22); fx.pulse(0, d, (255, 0, 0), 3.0, 0.4); td = wt(s, "definitely")
        fx.word("DEFINITELY", td, X, 300, 96, (90, 200, 255), 1.3, -5); fx.punch(td, 0.14); fx.pop("🚔", 0.3, 600, 400, 1.0)
    elif s == "e13":
        ts = wt(s, "slammed"); fx.word("SLAM!", ts, X, 300, 140, (255, 140, 40), 1.0, 8); fx.shake(ts, ts + 0.35, 14); fx.punch(ts, 0.16)
        tc = wt(s, "crack."); fx.word("CRACK!", tc, X, 300, 140, (255, 226, 30), 1.4, -6); fx.shake(tc, d, 6); fx.pop("😰", tc + 0.3, 600, 400, 1.0)
        fx.pop("😮‍💨", 0.3, 600, 300, 0.9)
    elif s == "e14":
        fx.pop("🤫", 0.4, X, 250, 1.1, life=2.2, rise=20)
    elif s == "e15":
        tn = wt(s, "not"); fx.flash(tn, (255, 255, 255), 0.9, 1.0); fx.shake(tn, tn + 0.8, 18); fx.punch(tn, 0.28)
        fx.burst(tn, tn + 1.2, X, H * 0.55, (255, 240, 170)); fx.word("NOT A PET", tn + 0.25, X, 330, 118, (255, 60, 60), 1.5, -5)
        fx.pulse(0, tn, (255, 160, 0), 1.6, 0.4)
    for i, it in enumerate(fx.items):   # keep every slam inside the frame at its overshoot peak
        if it[0] == "text":
            k, txt, t0, x, y, sz, fill, life, rot = it
            fx.items[i] = (k, txt, t0, x, y, fit(txt, sz, 0.78), fill, life, rot)
    return fx

def fit(txt, sz, frac=0.86, stroke=9):
    w = text_img(txt, sz, (255, 255, 255), stroke).width
    return sz if w <= W * frac else max(30, int(sz * W * frac / w))

GR = {"e06b": "desat", "e14": "freeze"}
def grade2(img, s):
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(1.3); rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    g = GR.get(s)
    if s in NIGHT:
        rgb = ImageEnhance.Brightness(rgb).enhance(0.6); rgb = Image.blend(rgb, Image.new("RGB", rgb.size, (40, 60, 150)), 0.2)
    if g == "desat": rgb = Image.blend(ImageEnhance.Color(rgb).enhance(0.35), Image.new("RGB", rgb.size, (90, 110, 160)), 0.15)
    if g == "freeze": rgb = Image.blend(ImageEnhance.Color(rgb).enhance(0.4), Image.new("RGB", rgb.size, (110, 130, 230)), 0.18)
    return rgb.convert("RGBA")

def caption(img, s, t, hide_after=None):
    if hide_after is not None and t > hide_after: return
    ws = WORDS[s]
    for i, (w, a, b) in enumerate(ws):
        nxt = ws[i + 1][1] if i + 1 < len(ws) else b + 0.3
        if a <= t < min(nxt, b + 0.35):
            clean = re.sub(r"[^\w']", "", w).lower(); hot = clean in HOT or w.lower() in HOT
            u = (t - a) / 0.16; sc = 1.0 + (0.22 if hot else 0.08) * max(0, 1 - u)
            txt = re.sub(r"[.,]+$", "", w).upper()
            paste_center(img, text_img(txt, fit(txt, 96 if hot else 84, 0.78, 11), (255, 226, 30) if hot else (255, 255, 255), 11), W / 2, H * 0.73, sc)
            return

def endcard(img, t0, t):
    u = t - t0
    if u < 0: return
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, int(min(1, u / 0.25) * 165))))
    tunnel(img, W / 2, H * 0.42, u, 0.6, 6, 1100, (255, 210, 80), 12, 0.35)
    paste_center(img, text_img("WHAT HATCHED?", fit("WHAT HATCHED?", 82, 0.8, 10), (255, 226, 30), 10), W / 2, H * 0.27, ease_pop(u * 1.8), -3)
    paste_center(img, emoji("🥚"), W / 2, H * 0.40, ease_pop((u - 0.2) * 1.8) * (1.3 + 0.08 * math.sin(u * 6)), 10 * math.sin(u * 5))
    paste_center(img, text_img("wrong answers only", 50, (255, 255, 255), 7), W / 2, H * 0.52, ease_pop((u - 0.4) * 1.8))
    paste_center(img, emoji("👇"), W / 2, H * 0.60, ease_pop((u - 0.55) * 1.8) * 0.7)
    paste_center(img, text_img("PART 2", 128, (90, 230, 255), 11), W / 2, H * 0.74, ease_pop((u - 0.8) * 1.6), -4)

def shot_frame(s, f, n, fx, trk, cache):
    t = (f - 1) / FPS
    p = f"{FR}/{s}/{f:04d}.png"
    if os.path.exists(p): cache["last"] = p
    base = (SKY_NIGHT if s in NIGHT else SKY_DAY).copy()
    if s in NIGHT: stars(base, t)
    ex, ey = (trk[f - 1][0] * W, trk[f - 1][1] * H) if trk and trk[f - 1] else (W / 2, H * 0.4)
    # sunburst layers sit in the sky, behind the 3D render
    if s == "e05": sunburst(base, W / 2, H * 0.3, t * 0.5, (255, 214, 90), None, 20, 0.35)
    if s in ("e08", "e10"): sunburst(base, ex, ey, t * 0.8, (255, 200, 60), None, 22, 0.42)
    if s == "e11": sunburst(base, W / 2, H * 0.3, -t * 2.2, (255, 70, 70), (255, 230, 230), 16, 0.9)
    if cache.get("last"): base.alpha_composite(Image.open(cache["last"]).convert("RGBA"))
    img = grade2(base, s)
    if s in ("e08", "e10", "e13", "e15") and trk:
        tn = wt("e15", "not") if s == "e15" else 99
        k = min(1, t / tn) if s == "e15" else 1.0
        glow(img, ex, ey, 230 + 160 * k + 25 * math.sin(t * 9), (255, 205, 70), 0.55 + 0.4 * k)
    if s == "e08": tunnel(img, ex, ey, t, 0.5, 7, 900, (255, 225, 110), 14, 0.55)
    if s == "e13" and t > wt("e13", "crack."): tunnel(img, ex, ey, t, 0.4, 6, 700, (255, 225, 110), 12, 0.6)
    if s == "e14": tunnel(img, W / 2, H * 0.45, t, 0.9, 6, 1300, (200, 220, 255), 10, 0.3, 1.2)
    if s == "e15":
        tn = wt("e15", "not")
        if t < tn + 0.2:
            k = min(1, t / tn)
            rays = Image.new("RGBA", (W, H)); sunburst(rays, ex, ey, t * (0.6 + 2.4 * k), (255, 215, 90), None, 24, 0.06 + 0.2 * k)
            img.alpha_composite(rays); tunnel(img, ex, ey, t, 0.55 - 0.3 * k, 8, 1300, (255, 230, 120), 14, 0.3 + 0.4 * k)
        else:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(255 * max(0, 0.75 - (t - tn - 0.2) * 0.25)))))
            sunburst(img, ex, ey, t * 3.2, (255, 235, 150), None, 24, 0.35)
    z, dx, dy = fx.cam(t)
    if z != 1.0 or dx or dy:
        zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
        x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
    fx.draw(img, t); fx.overlay(img, t)
    # racing counters (hypnotic)
    if s == "e05": counter(img, "MAYOR'S EGGS:", int(10 ** (3 + 4 * min(1, t / (n / FPS)) ** 0.7)), t)
    if s == "e06a": counter(img, "MY EGGS:", 1, t, (220, 220, 220), pulse=False)
    if s == "e12c": counter(img, "CHASERS:", int(5 * 200 ** min(1, t / (n / FPS))), t, (255, 90, 90))
    end_t = vo_end("e15") + 0.45 if s == "e15" else None
    caption(img, s, t, end_t)
    if s == "e15": endcard(img, end_t, t)
    return img

def main(out, only=None):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                           "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for s in ORDER:
        if only and s not in only: continue
        info = f"{FR}/{s}/info.json"
        n = json.load(open(info))["n"] if os.path.exists(info) else int(round(DUR[s] * FPS))
        fx = build_fx(s, n / FPS); trk = track(s); cache = {}
        for f in range(1, n + 1):
            ff.stdin.write(shot_frame(s, f, n, fx, trk, cache).convert("RGB").tobytes())
        print("composed", s, n, flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == "__main__" and not os.environ.get("EGG_NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{E}/egg_noaudio.mp4", set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
