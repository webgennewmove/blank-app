import sys, os, json, math, re, random, subprocess
sys.argv = ["x"]
_had_nomain = __import__("os").environ.get("NOMAIN")
__import__("os").environ["NOMAIN"] = "1"
exec(open("/home/claude/zara/compose.py").read())
if not _had_nomain: del __import__("os").environ["NOMAIN"]
from PIL import Image, ImageDraw

W, H = 720, 1280
FR = "/home/claude/zara/nframes"
NT = json.load(open("/home/claude/zara/ntimeline.json"))
DUR = NT["dur"]; LEAD = NT["lead"]; VOD = NT["vo"]
TEXT = NT["text"]
ORDER = ["n01", "n02", "n03", "n04", "n05", "n06", "n07", "n07b", "n08", "n09", "n11", "n12", "n13", "n14a", "n14b", "n14c", "n14d", "n15", "n16", "n17"]
HOT = {"hood", "pull", "prices", "guessing", "homework", "bro", "block", "stoop", "store", "calm", "number", "numbers", "ever", "clocks", "cakes", "vibes", "mistake", "old", "ten", "milos", "classroom", "silly", "million", "no",
       "street", "roof", "bathroom", "zero", "calm", "baby", "first", "word", "it"}
SKY = sky(); _v = None
import numpy as np
yy, xx = np.mgrid[0:H, 0:W]
_vv = np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.35, 0, 1)
VIGNETTE = Image.new("RGBA", (W, H), (0, 0, 0, 0)); VIGNETTE.putalpha(Image.fromarray((np.clip(_vv * 1.6, 0, 1) * 255).astype(np.uint8)))
globals()["VIGNETTE"] = VIGNETTE
S = 1.25  # scale factor vs 576 layout

def bubble(img, txt, x, y, t0, t, life=1.6, sz=58, col=(30, 30, 30)):
    u = (t - t0) / life
    if not (0 <= u < 1): return
    ti = text_img(txt, sz, col, 0)
    bw, bh = ti.width + 50, ti.height + 34
    b = Image.new("RGBA", (bw + 10, bh + 40)); d = ImageDraw.Draw(b)
    d.rounded_rectangle([5, 5, bw + 5, bh + 5], 28, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=6)
    d.polygon([(bw * 0.3, bh), (bw * 0.3 + 34, bh), (bw * 0.25, bh + 36)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    d.line([(bw * 0.3 + 3, bh + 2), (bw * 0.3 + 31, bh + 2)], fill=(255, 255, 255, 255), width=8)
    b.alpha_composite(ti, (30, 22))
    a = 1 if u < 0.85 else (1 - u) / 0.15
    paste_center(img, b, x, y, ease_pop(u * 3), 3 * math.sin(u * 12), a)

COUNT = {}   # shot -> function(t) -> count
def build_counts():
    def const(v): return lambda t: v
    COUNT.update({k: const(10) for k in ["n09", "n11", "n12", "n13"]})
    d8 = DUR["n08"]; pops = [ (int(d8 * 24 * 0.45) + 3 + k * 3) / 24 for k in range(9)]
    COUNT["n08"] = lambda t: 1 + sum(1 for p in pops if t >= p)
    # n14 ramp across four shots
    tot = sum(DUR[s] for s in ["n14a", "n14b", "n14c", "n14d"]); acc = 0
    for s in ["n14a", "n14b", "n14c", "n14d"]:
        a0 = acc
        COUNT[s] = (lambda a0: lambda t: int(10 * (100000 ** min(1, ((a0 + t) / tot) ** 0.8))))(a0)
        acc += DUR[s]
    COUNT["n15"] = const(1000000)
build_counts()

def counter(img, s, t):
    if s not in COUNT: return
    v = COUNT[s](t); txt = f"MILOS: {v:,}"
    ti = text_img(txt, 46, (255, 226, 30), 7)
    pulse = 1.0 + 0.06 * abs(math.sin(t * 12)) if s.startswith("n14") or s == "n08" else 1.0
    paste_center(img, ti, W / 2, 120, pulse)

def build_fx(s, d):
    fx = FX(s, d); v = VOD.get(s, d - 0.6); L = LEAD
    X, Y = W / 2, H / 2
    if s == "n01":
        f = d * 0.55; fx.ring(f, X - 120, 700, (255, 255, 255), 0.5, 300); fx.sparkle(f, f + 1.2, X - 120, 640, 120, (255, 255, 180), 14)
        fx.word("POP!", f, X - 130, 420, 100, (90, 230, 255)); fx.punch(f, 0.14); fx.pop("😳", f + 0.3, 560, 420, 0.9)
    elif s == "n02":
        for k, x in enumerate((140, 360, 580)): fx.pop("🤐", 0.2 + 0.3 * k, x, 360, 0.8)
    elif s == "n03":
        fx.pop("💸", 0.2, 130, 330, 0.9); fx.pop("🤷", 0.9, 600, 360, 0.9); fx.word("$ ???", L + v * 0.6, 190, 300, 90, (60, 220, 90), 1.3, -8)
    elif s == "n07b":
        fx.pop("💦", 0.3, 520, 520, 0.6, life=1.2, rise=-60); fx.pop("💦", 1.6, 220, 540, 0.6, life=1.2, rise=-60); fx.pop("😰", 2.6, 600, 820, 0.8)
    elif s == "n04":
        fx.pop("❓", 0.3, 580, 300, 0.9); fx.pop("🎂", 0.7, 140, 360, 0.9)
    elif s == "n05":
        fx.pop("💃", 0.3, 120, 380, 0.8); fx.pop("🕺", 0.7, 600, 400, 0.8); fx.sparkle(0, d, X, 500, 300, (255, 240, 150), 18)
        fx.word("VIBES", L + v * 0.7, X, 300, 120, (255, 90, 180), 1.4, -6)
    elif s == "n06":
        fx.pulse(0, d, (40, 0, 60), 0.8, 0.5); fx.pop("⚠", 0.4, 590, 300, 0.8)
    elif s == "n07":
        fx.pop("🙂", 0.6, 590, 320, 0.7)
    elif s == "n08":
        t0 = d * 0.45
        for k in range(9):
            tp = (int(d * 24 * 0.45) + 3 + k * 3) / 24
            fx.ring(tp, random.Random(k).uniform(120, 600), random.Random(k + 9).uniform(500, 1000), (255, 255, 255), 0.35, 160)
        fx.word("POP POP POP", t0 + 0.2, X, 300, 64, (90, 230, 255), 1.3, -5); fx.shake(t0, d, 6); fx.pop("😵", d - 0.6, 590, 380, 0.9)
        fx.confetti(t0 + 0.6, X, 260, 70)
    elif s == "n09":
        fx.pop("🤯", 0.2, 590, 330, 0.9); fx.word("x10", 0.1, 150, 330, 110, (255, 226, 30), 1.4, 8)
    elif s == "n10":
        fx.pop("😱", 0.1, 580, 330, 1.0); fx.punch(0.0, 0.16); fx.shake(0, 0.4, 8)
    elif s == "n11":
        b = d * 0.35; fx.word("BONK!", b, X, 380, 120, (255, 120, 40), 1.1, 8); fx.ring(b, X, 760, (255, 255, 255), 0.5, 250)
        fx.pop("💫", b + 0.1, X - 40, 560, 0.9); fx.pop("🤪", 0.3, 590, 330, 0.8); fx.shake(b, b + 0.3, 10)
    elif s == "n12":
        fx.punch(L + v * 0.6, 0.15); fx.pop("😎", 0.3, 120, 330, 0.8); fx.burst(L + v * 0.6, d, X, 520, (255, 230, 120))
    elif s == "n13":
        fx.punch(0.0, 0.12); fx.pop("😐", 0.15, 590, 330, 0.9); fx.word("BRO.", L + 0.05, 160, 360, 110, (255, 255, 255), 1.3, -6)
    elif s.startswith("n14"):
        fx.flash(0.0, (255, 255, 255), 0.18, 0.7); fx.shake(0, d, 7); fx.punch(0.0, 0.12)
        for k in range(4):
            fx.word("POP", 0.15 + k * d / 4, random.Random(k + len(s)).uniform(160, 560), random.Random(k * 7 + len(s)).uniform(320, 900), 70, (90, 230, 255), 0.6, random.Random(k).uniform(-15, 15))
        fx.pop({"n14a": "🏫", "n14b": "🛣", "n14c": "🏠", "n14d": "🚽"}[s], 0.15, 590, 330, 0.9)
    elif s == "n15":
        fx.pulse(0, d, (255, 0, 0), 2.5, 0.55); fx.pop("🚨", 0.1, 120, 330, 0.9); fx.pop("🚨", 0.4, 600, 330, 0.9)
        tz = L + v * 0.85; fx.word("ZERO", tz, X, 420, 150, (255, 60, 60), 1.4, -6); fx.shake(tz, tz + 0.6, 14); fx.punch(tz, 0.2); fx.flash(tz, (255, 255, 255), 0.25, 0.6)
    elif s == "n16":
        fx.pop("👶", 0.3, 130, 340, 0.9); fx.pop("😰", 1.2, 590, 360, 0.9); fx.pulse(0, d, (40, 0, 80), 0.6, 0.4)
    elif s == "n17":
        fx.pulse(0, d, (40, 0, 80), 0.5, 0.5); fx.pop("❗", L + v * 0.5, 590, 330, 1.0)
    return fx

BUBBLES = {"n01": ("2!", 0.38, 470, 520), "n08": ("10?", 0.12, 470, 470), "n12": ("A MILLION!", 0.15, 360, 300), "n15": ("DON'T SAY ZERO!", 0.6, 360, 260)}
def thought(img, t, d):
    a = min(1, t / 0.3) * (1 if t < d - 0.2 else max(0, (d - t) / 0.2))
    if a <= 0: return
    layer = Image.new("RGBA", (W, H)); dr = ImageDraw.Draw(layer)
    cx, cy = W / 2 + 40, 330
    for ox, oy, r in [(-170, 0, 110), (-60, -60, 130), (80, -50, 125), (180, 10, 100), (60, 70, 120), (-90, 70, 110)]:
        dr.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(255, 255, 255, 245), outline=(0, 0, 0, 255), width=7)
    for ox, oy, r in [(-60, -60, 123), (80, -50, 118), (60, 70, 113), (-90, 70, 103), (-170, 0, 103), (180, 10, 93)]:
        dr.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(255, 255, 255, 255))
    for k, (x, y, r) in enumerate([(cx - 120, cy + 210, 28), (cx - 160, cy + 270, 18), (cx - 190, cy + 315, 11)]):
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5)
    nums = ["7?", "10?", "1,000?", "11?", "2?", "100?", "69?", "3?"]
    k = int(t * 3.2) % len(nums); nxt = nums[k]
    ti = text_img(nxt, 96, (90, 120, 255), 6); u = (t * 3.2) % 1
    paste_center(layer, ti, cx, cy, 0.8 + 0.25 * ease_pop(u * 2), 8 * math.sin(t * 7))
    for j in range(3):
        ang = t * 2.5 + j * 2.1; sm = text_img(nums[(k + j + 3) % len(nums)], 40, (150, 150, 150), 3)
        paste_center(layer, sm, cx + math.cos(ang) * 175, cy + math.sin(ang) * 85, 0.9)
    if a < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
    img.alpha_composite(layer)
GRADE = dict(n06=("dark", 0.1), n07b=("freeze", 0), n16=("dark", 0.15), n17=("dark", 0.2))

def caption(img, s, t):
    vo = VOD.get(s)
    if vo is None or s not in TEXT: return
    ws = words(s, vo)
    for w, a, b in ws:
        a += LEAD; b += LEAD
        if a <= t < b + (0.25 if w == ws[-1][0] else 0):
            clean = re.sub(r"[^\w']", "", w).lower(); hot = clean in HOT
            u = (t - a) / 0.18; sc = 1.0 + (0.2 if hot else 0.08) * (1 - min(1, u))
            paste_center(img, text_img(w, 92 if hot else 82, (255, 226, 30) if hot else (255, 255, 255), 10), W / 2, H * (0.82 if s in ("n07b", "n13", "n17", "n09", "n12") else 0.68), sc)
            return

def endcard(img, t0, t):
    u = t - t0
    if u < 0: return
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, int(min(1, u / 0.25) * 170))))
    paste_center(img, text_img("What number", 70, (255, 255, 255), 9), W / 2, H * 0.30, ease_pop(u * 1.8))
    paste_center(img, text_img("would YOU say?", 70, (255, 226, 30), 9), W / 2, H * 0.37, ease_pop((u - 0.15) * 1.8))
    paste_center(img, emoji("👇"), W / 2, H * 0.47, ease_pop((u - 0.3) * 1.8) * 0.9)
    paste_center(img, text_img("PART 2", 120, (90, 230, 255), 10), W / 2, H * 0.62, ease_pop((u - 0.5) * 1.6), -4)

def main(out):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                           "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for s in ORDER:
        n = json.load(open(f"{FR}/{s}/info.json"))["n"]
        fx = build_fx(s, n / 24); last = None
        for f in range(1, n + 1):
            t = (f - 1) / 24
            p = f"{FR}/{s}/{f:04d}.png"; p = p if os.path.exists(p) else last
            base = SKY.copy()
            if p: base.alpha_composite(Image.open(p).convert("RGBA")); last = p
            img = grade(base, s, t)
            z, dx, dy = fx.cam(t)
            if z != 1.0 or dx or dy:
                zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
                x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
                c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
            fx.draw(img, t); fx.overlay(img, t)
            if s in BUBBLES:
                txt, fr, bx, by = BUBBLES[s]; bubble(img, txt, bx, by, DUR[s] * fr, t, 1.8)
            counter(img, s, t)
            if s == "n07b": thought(img, t, n / 24)
            caption(img, s, t)
            if s == "n17": endcard(img, LEAD + VOD["n17"] + 0.5, t)
            ff.stdin.write(img.convert("RGB").tobytes())
        print("composed", s, flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == "__main__" and not __import__("os").environ.get("NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/zara/number_noaudio.mp4")
