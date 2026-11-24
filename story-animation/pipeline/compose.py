"""Composite rendered frames + visual feedback (particles, emoji pops, text pops, speed lines, shockwaves,
flashes, zoom punches, shake, grading) + word-by-word captions. Streams to ffmpeg."""
import json, math, os, random, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops

Z = "/home/claude/zara"; W, H = 576, 1024; FPS = 24
TL = json.load(open(f"{Z}/timeline.json")); DUR = TL["dur"]; LEAD = TL["lead"]
VOD = json.load(open(f"{Z}/vo/durs.json"))
TEXT = dict(s01="In my town, every kid gets a superpower on their tenth birthday!", s02="My best friend Milo got super jumping.",
            s03="My big sister Ivy can float.", s04="Even Grandma got super speed!", s05="And today... is MY tenth birthday!",
            s06="I ran outside to see what I could do.", s07="I tried jumping...", s08="I tried floating...", s09="Nothing happened.",
            s10="Everyone started laughing.", s11="Maybe you're the only kid with NO power!", s12="I walked home, feeling so small.",
            s13="Then I saw a little puppy, stuck in the road.", s14="And a truck was coming!", s15="I shouted... STOP!",
            s16="And everything froze.", s17="The truck. The birds. Even the clouds.", s18="I could stop TIME!",
            s19="I picked up the puppy... and time started again.", s20="Everyone was staring at me.",
            s21="Only one person has ever had that power... and he vanished fifty years ago.", s22="Who was he?")
HOT = {"superpower", "tenth", "milo", "jumping", "ivy", "float", "grandma", "speed", "my", "nothing", "laughing", "no", "power",
       "small", "puppy", "truck", "stop", "froze", "clouds", "time", "staring", "fifty", "vanished", "who"}
ORDER = [f"s{i:02d}" for i in range(1, 23)]
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]
_ec = {}
def emoji(e):
    if e not in _ec:
        im = Image.new("RGBA", (160, 160)); ImageDraw.Draw(im).text((10, 10), e, font=EMO, embedded_color=True)
        _ec[e] = im.crop(im.getbbox())
    return _ec[e]
_tc = {}
def text_img(s, sz, fill, stroke=8, stroke_fill=(0, 0, 0)):
    k = (s, sz, fill, stroke)
    if k not in _tc:
        f = font(sz); bb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), s, font=f, stroke_width=stroke)
        im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20))
        ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        _tc[k] = im
    return _tc[k]

def ease_pop(u):  # 0..1 -> overshoot scale
    if u <= 0: return 0.0
    if u < 0.35: x = u / 0.35; return 1.25 * (1 - (1 - x) ** 3)
    if u < 0.6: x = (u - 0.35) / 0.25; return 1.25 - 0.25 * x
    return 1.0

def paste_center(base, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    w, h = im.size; im2 = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BILINEAR)
    if rot: im2 = im2.rotate(rot, expand=True, resample=Image.BILINEAR)
    if alpha < 1: a = im2.split()[3].point(lambda v: int(v * alpha)); im2.putalpha(a)
    base.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

# ---------------------------------------------------------------- effects (time t in seconds relative to shot)
class FX:
    def __init__(self, shot, d):
        self.s, self.d = shot, d; self.items = []; self.rng = random.Random(hash(shot) % 9999)
    def pop(self, e, t, x, y, size=1.0, life=1.4, rot=0, rise=60):
        self.items.append(("emoji", e, t, x, y, size, life, rot, rise))
    def word(self, s, t, x, y, sz=96, fill=(255, 230, 40), life=1.2, rot=-8):
        self.items.append(("text", s, t, x, y, sz, fill, life, rot))
    def confetti(self, t, x=W / 2, y=H * 0.35, n=70):
        r = self.rng; ps = [(r.uniform(-1, 1) * 9, r.uniform(-14, -4), r.choice([(255, 60, 90), (255, 220, 40), (60, 220, 120), (40, 190, 255), (220, 90, 255)]),
                             r.uniform(0, 360), r.uniform(-12, 12)) for _ in range(n)]
        self.items.append(("confetti", t, x, y, ps))
    def sparkle(self, t0, t1, x, y, spread=120, col=(255, 255, 255), n=10):
        r = self.rng; ps = [(r.uniform(-spread, spread), r.uniform(-spread, spread), r.uniform(0, 1), r.uniform(6, 16)) for _ in range(n)]
        self.items.append(("sparkle", t0, t1, x, y, ps, col))
    def speed(self, t0, t1, n=26, horiz=True):
        r = self.rng; ls = [(r.uniform(0, H), r.uniform(60, 260), r.uniform(2, 6), r.uniform(0, 1)) for _ in range(n)]
        self.items.append(("speed", t0, t1, ls, horiz))
    def ring(self, t, x, y, col=(255, 255, 255), life=0.6, maxr=420):
        self.items.append(("ring", t, x, y, col, life, maxr))
    def burst(self, t0, t1, x, y, col=(255, 255, 255)):
        self.items.append(("burst", t0, t1, x, y, col))
    def flash(self, t, col=(255, 255, 255), life=0.25, a=0.85):
        self.items.append(("flash", t, col, life, a))
    def pulse(self, t0, t1, col=(255, 0, 0), rate=3.0, a=0.35):
        self.items.append(("pulse", t0, t1, col, rate, a))
    def punch(self, t, amt=0.12, life=0.35): self.items.append(("punch", t, amt, life))
    def shake(self, t0, t1, amp=10): self.items.append(("shake", t0, t1, amp))
    def hearts(self, t0, t1, x, y, n=6):
        r = self.rng
        for k in range(n): self.pop(r.choice(["❤", "💖", "💕"]), t0 + (t1 - t0) * k / n, x + r.uniform(-120, 120), y + r.uniform(-40, 60), size=r.uniform(0.4, 0.6), life=1.3, rise=160)

    def cam(self, t):
        """returns (zoom, dx, dy)"""
        z, dx, dy = 1.0, 0.0, 0.0
        for it in self.items:
            if it[0] == "punch":
                _, t0, amt, life = it; u = (t - t0) / life
                if 0 <= u < 1: z += amt * (1 - u) ** 2
            if it[0] == "shake":
                _, t0, t1, amp = it
                if t0 <= t < t1:
                    k = 1 - (t - t0) / (t1 - t0) * 0.6
                    dx += math.sin(t * 77) * amp * k; dy += math.cos(t * 63) * amp * k
        return z, dx, dy

    def draw(self, img, t):
        d = ImageDraw.Draw(img)
        for it in self.items:
            k = it[0]
            if k == "emoji":
                _, e, t0, x, y, size, life, rot, rise = it; u = (t - t0) / life
                if 0 <= u < 1:
                    sc = ease_pop(u * 2.2) * size * 0.85; a = 1 if u < 0.75 else (1 - u) / 0.25
                    paste_center(img, emoji(e), x, y - rise * u, sc, rot + 8 * math.sin(u * 9), a)
            elif k == "text":
                _, s, t0, x, y, sz, fill, life, rot = it; u = (t - t0) / life
                if 0 <= u < 1:
                    a = 1 if u < 0.8 else (1 - u) / 0.2
                    paste_center(img, text_img(s, sz, fill, 9), x, y, ease_pop(u * 2.5), rot + 3 * math.sin(u * 20), a)
            elif k == "confetti":
                _, t0, x, y, ps = it; tt = t - t0
                if 0 <= tt < 2.2:
                    for vx, vy, col, a0, va in ps:
                        px = x + vx * tt * 40; py = y + (vy * tt + 14 * tt * tt) * 40
                        ang = math.radians(a0 + va * tt * 60); w2, h2 = 7, 13
                        pts = [(px + math.cos(ang) * cx - math.sin(ang) * cy, py + math.sin(ang) * cx + math.cos(ang) * cy)
                               for cx, cy in [(-w2, -h2 / 2), (w2, -h2 / 2), (w2, h2 / 2), (-w2, h2 / 2)]]
                        d.polygon(pts, fill=col + (255,))
            elif k == "sparkle":
                _, t0, t1, x, y, ps, col = it
                if t0 <= t < t1:
                    for ox, oy, ph, sz in ps:
                        tw = max(0, math.sin((t * 3 + ph) * math.pi * 2)); s = sz * tw
                        if s < 1: continue
                        cx, cy = x + ox, y + oy
                        d.polygon([(cx, cy - s), (cx + s * 0.25, cy - s * 0.25), (cx + s, cy), (cx + s * 0.25, cy + s * 0.25), (cx, cy + s),
                                   (cx - s * 0.25, cy + s * 0.25), (cx - s, cy), (cx - s * 0.25, cy - s * 0.25)], fill=col + (235,))
            elif k == "speed":
                _, t0, t1, ls, horiz = it
                if t0 <= t < t1:
                    for yy, ln, th, ph in ls:
                        off = ((t * 5 + ph) % 1) * (W + ln * 2) - ln
                        if horiz: d.line([(W - off, yy), (W - off - ln, yy)], fill=(255, 255, 255, 170), width=int(th))
            elif k == "ring":
                _, t0, x, y, col, life, maxr = it; u = (t - t0) / life
                if 0 <= u < 1:
                    r = maxr * (1 - (1 - u) ** 2)
                    d.ellipse([x - r, y - r, x + r, y + r], outline=col + (int(255 * (1 - u)),), width=int(14 * (1 - u)) + 2)
            elif k == "burst":
                _, t0, t1, x, y, col = it
                if t0 <= t < t1:
                    r = random.Random(int(t * 24))
                    for _ in range(36):
                        a = r.uniform(0, 2 * math.pi); r0 = r.uniform(180, 300); r1 = r0 + r.uniform(150, 500)
                        d.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], fill=col + (170,), width=r.randint(2, 6))

    def overlay(self, img, t):
        for it in self.items:
            if it[0] == "flash":
                _, t0, col, life, a = it; u = (t - t0) / life
                if 0 <= u < 1: img.alpha_composite(Image.new("RGBA", img.size, col + (int(255 * a * (1 - u)),)))
            if it[0] == "pulse":
                _, t0, t1, col, rate, a = it
                if t0 <= t < t1:
                    v = (math.sin((t - t0) * rate * 2 * math.pi) * 0.5 + 0.5) * a
                    vig = VIGNETTE.copy(); vig.putalpha(VIGNETTE.split()[3].point(lambda p: int(p * v)))
                    tint = Image.new("RGBA", img.size, col + (0,)); tint.putalpha(vig.split()[3]); img.alpha_composite(tint)

# vignette mask
_v = np.zeros((H, W), np.float32); yy, xx = np.mgrid[0:H, 0:W]
_v = np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.35, 0, 1)
VIGNETTE = Image.new("RGBA", (W, H), (0, 0, 0, 0)); VIGNETTE.putalpha(Image.fromarray((np.clip(_v * 1.6, 0, 1) * 255).astype(np.uint8)))

# ---------------------------------------------------------------- sky background
def sky(top=(52, 140, 240), bot=(175, 220, 255)):
    a = np.linspace(0, 1, H)[:, None]; g = np.array(top)[None, :] * (1 - a) + np.array(bot)[None, :] * a
    im = np.repeat(g[:, None, :], W, axis=1).astype(np.uint8); return Image.fromarray(im).convert("RGBA")
SKY = sky(); SKY_SUNSET = sky((120, 110, 200), (255, 190, 170))

# ---------------------------------------------------------------- per-shot feedback scripting
def build_fx(s, d):
    fx = FX(s, d); v = VOD.get(s, d - 0.6); L = LEAD
    if s == "s01":
        fx.confetti(0.15, W / 2, H * 0.2, 90); fx.punch(0.0, 0.1); fx.pop("⚡", 0.8, 140, 380, 0.9); fx.pop("🦸", 1.9, 440, 330, 0.9); fx.pop("✨", 2.9, 300, 260, 0.8)
        fx.sparkle(0, d, 400, 470, 80, (255, 255, 200))
    elif s == "s02":
        j0 = d * 0.12; fx.word("BOING!", j0 + 0.1, W / 2, 260, 92, (90, 230, 255)); fx.ring(j0 + 0.05, W / 2, 900, (255, 255, 255), 0.5, 260)
        fx.sparkle(j0 + 0.4, d * 0.72, W / 2, 330, 140, (255, 240, 150)); fx.pop("😎", d * 0.74, 430, 360, 0.9); fx.punch(d * 0.72, 0.14); fx.shake(d * 0.72, d * 0.72 + 0.25, 8)
    elif s == "s03":
        fx.sparkle(0, d, W / 2, 430, 170, (255, 200, 255), 16); fx.pop("🎈", 0.6, 120, 300, 0.8); fx.pop("✨", 1.4, 450, 260, 0.8)
    elif s == "s04":
        fx.speed(0, d * 0.56); fx.word("ZOOM!", 0.15, W / 2, 300, 110, (255, 120, 40), 1.1, -10); fx.pop("💨", 0.5, 120, 560, 1.0, rise=0)
        fx.pop("😎", d * 0.62, 400, 330, 0.9); fx.punch(d * 0.56, 0.1)
    elif s == "s05":
        fx.confetti(0.25, W / 2, H * 0.15, 100); fx.confetti(L + v * 0.62, W / 2, H * 0.2, 90); fx.pop("🎂", 0.5, 110, 300, 0.9); fx.pop("🎉", 1.2, 460, 260, 1.0)
        fx.punch(L + v * 0.62, 0.16); fx.word("10!", L + v * 0.7, 140, 520, 120, (255, 90, 180), 1.4, 10)
    elif s == "s06":
        fx.speed(0, d, 14); fx.pop("⭐", 0.4, 460, 330, 0.8); fx.pop("⭐", 1.2, 110, 280, 0.7)
    elif s == "s07":
        fx.word("boing?", d * 0.4, W / 2, 330, 70, (255, 255, 255), 1.0, 5); fx.pop("🤔", d * 0.7, 440, 300, 0.8)
    elif s == "s08":
        fx.word("flap flap", 0.3, W / 2, 300, 66, (255, 255, 255), 1.4, -4); fx.pop("😤", 1.0, 450, 300, 0.8)
    elif s == "s09":
        fx.pop("🌧", 0.25, W / 2, 230, 1.1, life=d, rise=0); fx.punch(0.0, 0.08)
    elif s == "s10":
        for k, (x, y) in enumerate([(110, 330), (460, 300), (300, 220), (150, 520), (470, 520)]): fx.pop("😂", 0.15 + k * 0.35, x, y, 0.75)
        fx.word("HAHA", 0.3, W / 2, 180, 90, (255, 230, 40), 1.5, 8); fx.shake(0, d, 3)
    elif s == "s11":
        fx.pop("😂", 0.3, 460, 280, 0.8); fx.pop("🤭" if False else "😆", 1.6, 110, 300, 0.7)
    elif s == "s12":
        fx.pop("💔", 0.4, 430, 320, 0.8, life=1.8)
    elif s == "s13":
        fx.pop("🐶", L + v * 0.55, 250, 560, 0.7); fx.pop("❗", 0.3, 430, 300, 0.9); fx.punch(L + v * 0.55, 0.12)
    elif s == "s14":
        fx.pulse(0, d, (255, 0, 0), 3.0, 0.55); fx.pop("⚠", 0.1, W / 2, 230, 1.0); fx.word("HONK!", d * 0.45, W / 2, 330, 96, (255, 70, 60), 1.0, 7); fx.shake(d * 0.4, d, 7)
    elif s == "s15":
        t = L + v * 0.62; fx.burst(t, d, W / 2, H * 0.45); fx.flash(t, (255, 255, 255), 0.3); fx.ring(t, W / 2, H * 0.45, (255, 255, 255), 0.7, 650)
        fx.ring(t + 0.15, W / 2, H * 0.45, (120, 220, 255), 0.8, 650); fx.word("STOP!", t, W / 2, 250, 150, (255, 60, 60), 1.6, -6); fx.shake(t, t + 0.6, 16); fx.punch(t, 0.22)
    elif s == "s16":
        fx.sparkle(0, d, W / 2, H * 0.45, 260, (200, 230, 255), 28); fx.pop("⏸", 0.3, W / 2, 200, 0.9, life=d, rise=0); fx.word("TIME STOPPED", 1.0, W / 2, 320, 54, (170, 230, 255), 2.0, 0)
    elif s == "s17":
        fx.sparkle(0, d, W / 2, H * 0.4, 260, (200, 230, 255), 28)
    elif s == "s18":
        fx.sparkle(0, d, W / 2, H * 0.48, 170, (255, 215, 80), 26); fx.burst(d * 0.45, d * 0.45 + 0.7, W / 2, H * 0.45, (255, 220, 90))
        fx.pop("⏰", 0.3, 130, 280, 0.9); fx.pop("✨", d * 0.45, 450, 260, 1.0); fx.word("WOW!", d * 0.45, W / 2, 210, 120, (255, 215, 60), 1.4, 7)
        fx.punch(d * 0.45, 0.18); fx.flash(d * 0.45, (255, 230, 150), 0.3, 0.6)
    elif s == "s19":
        fx.hearts(0.2, d, W / 2, 520, 8); fx.flash(d * 0.55, (255, 255, 255), 0.2, 0.5); fx.pop("🐶", 0.5, 440, 330, 0.8)
    elif s == "s20":
        for k, (x, y) in enumerate([(120, 300), (300, 250), (460, 300)]): fx.pop("😮", 0.2 + 0.3 * k, x, y, 0.8)
    elif s == "s21":
        fx.pop("👀", 0.4, 450, 300, 0.8); fx.pulse(0, d, (60, 0, 120), 0.6, 0.35)
    elif s == "s22":
        fx.pulse(0, d, (40, 0, 90), 0.5, 0.45)
    return fx

GRADE = dict(s09=("desat", 0.6), s12=("blue", 0.5), s16=("freeze", 0), s17=("freeze", 0), s21=("dark", 0.15), s22=("dark", 0.2))

def grade(img, s, t):
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(1.35); rgb = ImageEnhance.Contrast(rgb).enhance(1.08); rgb = ImageEnhance.Brightness(rgb).enhance(1.04)
    g = GRADE.get(s)
    if g:
        kind, amt = g
        if kind == "desat": rgb = ImageEnhance.Color(rgb).enhance(amt)
        if kind == "blue":
            rgb = ImageEnhance.Color(rgb).enhance(0.45); rgb = Image.blend(rgb, Image.new("RGB", rgb.size, (60, 90, 160)), 0.18)
        if kind == "freeze":
            gray = ImageEnhance.Color(rgb).enhance(0.35); rgb = Image.blend(gray, Image.new("RGB", rgb.size, (120, 140, 255)), 0.25)
        if kind == "dark": rgb = ImageEnhance.Brightness(rgb).enhance(1 - amt)
    return rgb.convert("RGBA")

def words(s, dur):
    ws = TEXT[s].replace("...", "… ").split()
    wt = [len(re.sub(r"[^\w']", "", w)) + 2 + (4 if re.search(r"[.,…?!]$", w) else 0) for w in ws]
    tot = sum(wt); t = 0; out = []
    for w, k in zip(ws, wt):
        dd = dur * k / tot; out.append((re.sub(r"[.,…]+$", "", w), t, t + dd)); t += dd
    return out

def caption(img, s, t):
    vo = VOD.get(s)
    if vo is None: return
    for w, a, b in words(s, vo):
        a += LEAD; b += LEAD
        if s == ORDER[-1] and t > b: continue
        if a <= t < b + (0.25 if w == words(s, vo)[-1][0] else 0):
            clean = re.sub(r"[^\w']", "", w).lower()
            hot = clean in HOT
            col = (255, 226, 30) if hot else (255, 255, 255)
            u = (t - a) / 0.18
            sc = 1.0 + (0.18 * (1 - min(1, u)) if hot else 0.08 * (1 - min(1, u)))
            paste_center(img, text_img(w, 66 if not hot else 74, col, 8), W / 2, H * 0.66, sc)
            return

def endcard(img, t0, t):
    u = t - t0
    if u < 0: return
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, int(min(1, u / 0.3) * 150))))
    paste_center(img, text_img("PART 2", 132, (255, 226, 30), 10), W / 2, H * 0.42, ease_pop(u * 1.6), -4)
    paste_center(img, emoji("👉"), W / 2, H * 0.55, ease_pop((u - 0.25) * 1.6) * 0.8)
    paste_center(img, text_img("follow so you don't miss it", 30, (255, 255, 255), 5), W / 2, H * 0.63, ease_pop((u - 0.45) * 1.6))

def frame_path(s, f):
    p = f"{Z}/frames/{s}/{f:04d}.png"
    return p if os.path.exists(p) else None

def main(out):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    total = 0
    for s in ORDER:
        info = f"{Z}/frames/{s}/info.json"
        n = json.load(open(info))["n"] if os.path.exists(info) else int(round(DUR[s] * FPS))
        fx = build_fx(s, n / FPS)
        last = None
        for f in range(1, n + 1):
            t = (f - 1) / FPS
            p = frame_path(s, f) or last
            base = (SKY.copy())
            if p:
                fr = Image.open(p).convert("RGBA"); last = p; base.alpha_composite(fr)
            img = grade(base, s, t)
            z, dx, dy = fx.cam(t)
            if z != 1.0 or dx or dy:
                zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
                x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
                canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255)); canvas.paste(im2, (-x0, -y0)); img = canvas
            fx.draw(img, t); fx.overlay(img, t)
            caption(img, s, t)
            if s == ORDER[-1]: endcard(img, LEAD + VOD["s22"] + 0.45, t)
            ff.stdin.write(img.convert("RGB").tobytes()); total += 1
        print("composed", s, n, flush=True)
    ff.stdin.close(); ff.wait(); print("frames", total)

if __name__ == "__main__" and not __import__("os").environ.get("NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{Z}/video_noaudio.mp4")
