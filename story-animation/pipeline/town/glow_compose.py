"""IN MY TOWN 'Glows' compositor: cinematic grade (teal/amber), bloom, vignette, grain, word captions, light feedback FX,
Rico's phone UI, emerald vortex + rays. No outro: the last frame cuts back to the first (loop)."""
import os, sys, json, math, random, re, subprocess
os.environ["EGG_NOMAIN"] = "1"; _argv = sys.argv[:]; sys.argv = ["x"]
exec(open("/home/claude/zara/egg_compose.py").read())
sys.argv = _argv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
E = "/home/claude/zara/town/glow/ep"; FR = f"{E}/frames"
TL = json.load(open(f"{E}/timeline.json")); ORDER = TL["shots"]; DUR = TL["dur"]; LEADS = TL["lead"]; VOD = TL["vo"]; WORDS = TL["words"]
HOT = {"glows", "steve", "steve.", "four", "found", "disco", "blink", "me", "glow", "bell", "whiskers", "jingle", "dead", "bulb", "flashlight",
       "three", "two", "one", "unzipped", "seconds", "flashlight", "tree", "lights", "star", "staring", "light", "fwoom", "giant", "moths", "porch", "pants", "homework", "thrilled", "hood", "glowing", "coats",
       "hey", "followed", "rock", "top", "concert", "street", "leo", "laughs", "dark", "gap", "swarm", "over", "here", "moth", "no"}
GREEN = (90, 255, 150); GOLD = (255, 205, 60); RED = (255, 80, 70); PINK = (255, 120, 200)
def wt(s, word, k=0):
    word = word.lower().strip(".,!?-")
    hits = [a for w, a, b in WORDS[s] if w.lower().strip(".,!?-\u2026") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
def build_fx(s, d):
    fx = FX(s, d); X = W / 2
    if s == "s01":
        for i, c in enumerate(((255, 220, 90), (90, 255, 140), (255, 90, 80))): fx.punch((1 + i * 7) / 24, 0.05)
        fx.word("GLOWS", 0.0, X, 300, 190, GOLD, d + 0.02, -5)
    elif s == "s04": fx.word("STEVE", wt(s, "steve"), X, 300, 150, GOLD, 1.2, -6); fx.pop("☕", wt(s, "steve") + 0.3, 600, 420, 0.9)
    elif s == "s05": fx.word("4 SECONDS", wt(s, "four"), X, 290, 110, GOLD, 1.3, 5)
    elif s in ("s06", "s07", "s07b"): fx.word("FOUND YOU!", 0.05, X, 300, 120, (255, 255, 255), 0.7, -6 if s != "s07" else 6); fx.punch(0.05, 0.1)
    elif s == "s09":
        for k, w_ in enumerate(("BLINK!", "BLINK!", "BLINK!")):
            fx.word(w_, wt(s, "blink", k), [200, 520, 360][k], [300, 420, 540][k], 96, [(255, 80, 80), (90, 255, 140), (90, 160, 255)][k], 0.6, [-10, 8, -4][k])
    elif s == "s10": fx.pop("🕸️", 0.3, 130, 380, 1.0)
    elif s == "s11": fx.sparkle(0.2, d, X, H * 0.45, 380, (255, 240, 180), 26); fx.word("WE ARE THEM", wt(s, "are"), X, 290, 110, GOLD, 1.2, -4)
    elif s == "s13": fx.pop("👍", 0.25, 560, 420, 1.0)
    elif s == "s14": fx.pop("🔔", wt(s, "bell") + 0.1, 560, 400, 1.0)
    elif s == "s17": fx.word("JINGLE", wt(s, "jingle"), 230, 330, 100, GOLD, 0.6, -8); fx.word("JINGLE", wt(s, "jingle", 1), 490, 430, 100, GOLD, 0.6, 8)
    elif s == "s20": fx.word("DEAD BULB", wt(s, "dead"), X, 300, 130, (190, 190, 200), 1.0, -5); fx.punch(wt(s, "dead"), 0.12)
    elif s == "s21": fx.pop("🔦", wt(s, "flashlight"), 560, 420, 1.0)
    elif s == "s24":
        for k, w_ in enumerate(("3", "2", "1")): fx.word(w_, wt(s, ["three", "two", "one"][k]), X, 330, 240, GOLD, 0.45, 0); fx.punch(wt(s, ["three", "two", "one"][k]), 0.06)
    elif s == "s25": fx.word("UNZIP!", wt(s, "unzipped"), X, 300, 130, (255, 255, 255), 0.8, -6)
    elif s == "s26": fx.flash(0.0, (255, 245, 200), 0.35, 0.8); fx.shake(0, 0.5, 10); fx.word("FWOOM!", 0.05, X, 300, 170, GOLD, 0.7, -6); fx.sparkle(0, d, X, H * 0.45, 420, (255, 230, 160), 30)
    elif s == "s27": fx.word("BZZZZ!", 0.1, X, 300, 140, (230, 200, 150), 1.2, -6); fx.shake(0, d, 4)
    elif s == "s29": fx.pop("😍", d * 0.38, 560, 380, 1.0)
    elif s == "s30": fx.word("CHOMP!", d * 0.42, X, 330, 150, (255, 255, 255), 0.8, 7); fx.punch(d * 0.42, 0.12)
    elif s == "s31": fx.word("RIIIP!", d * 0.45, X, 320, 140, (255, 255, 255), 0.8, -7)
    elif s == "s32": fx.pop("🎉", 0.2, 560, 380, 1.0)
    elif s == "s33": fx.shake(0, d, 5)
    elif s == "s35": fx.shake(0, d, 7)
    elif s == "s38": fx.sparkle(0, d, X, H * 0.5, 200, (255, 230, 120), 10)
    elif s == "s40": fx.word("COATS ON!", 0.42, X, 330, 190, GOLD, d - 0.42 + 0.02, -6); fx.punch(0.42, 0.12); fx.shake(0.42, 0.3, 6)
    elif s == "s41": fx.word("ZZZIP!", 0.0, X, 300, 150, (220, 230, 255), d, 6)
    elif s == "s42": fx.word("CLICK!", 0.15, X, 300, 140, (255, 250, 210), 0.5, -6); fx.flash(0.2, (255, 250, 220), 0.2, 0.6)
    elif s == "s44": fx.pop("👀", 0.3, 560, 380, 1.0)
    elif s == "s45": fx.speed(d * 0.3, d, 22, True)
    elif s == "s46": fx.speed(0, d, 26, False)
    elif s == "s49": fx.hearts(0.1, d, X, H * 0.4, 6)
    elif s == "s51": t_ = wt(s, "top"); fx.word("STAR", t_, X, 300, 190, GOLD, d - t_ + 0.02, -5); fx.punch(t_, 0.12); fx.sparkle(t_, d, X, H * 0.35, 220, (255, 230, 140), 16)
    elif s == "s53": fx.pop("🏄", d * 0.45, X + 150, H * 0.4, 1.0); t_ = wt(s, "concert."); fx.word("CONCERT!", t_, X, 320, 190, GOLD, d - t_ + 0.02, -5); fx.punch(t_, 0.14); fx.shake(t_, 0.35, 8); fx.sparkle(t_, d, X, H * 0.3, 260, (255, 230, 160), 18)
    for i, it in enumerate(fx.items):
        if it[0] == "text":
            k, txt, t0, x, y, sz, fill, life, rot = it
            fx.items[i] = (k, txt, t0, x, y, fit(txt, sz, 0.82), fill, life, rot)
    return fx

def cine_grade(img, s):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    lum = a.mean(axis=2, keepdims=True)
    blackshot = s in ("s01", "s12", "s37")
    if not blackshot:
        a = np.clip(a, 0, 1) ** 0.88                 # lift midtones ~10% (blacks stay black)
        a = a + (np.array([-0.02, 0.025, 0.035]) * (1 - lum) * np.clip(lum * 8, 0, 1)) + (np.array([0.05, 0.02, -0.03]) * lum)   # teal shadows (not in pure black), amber highlights
    a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(1.18)
    # bloom
    br = out.point(lambda v: max(0, v - 200) * 2)
    bl = br.filter(ImageFilter.GaussianBlur(22))
    out = ImageChops.add(out, bl.point(lambda v: int(v * 0.45)))   # (was scale=2.2, which halved the whole frame)
    return out.convert("RGBA")
_VIG = None
def vignette(img):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        al = np.clip((r - 0.75) / 0.6, 0, 1) ** 1.6 * 120
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
    if s in ("s11", "s18", "s26", "s51"): glow(img, W / 2, H * 0.42, 360 + 25 * math.sin(t * 5), (255, 220, 140), 0.22)
    if s in ("s52", "s53"): glow(img, W / 2, H * 0.25, 300, (255, 240, 200), 0.18)
    if s == "s53" and t > T - 0.17: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * min(1, (t - (T - 0.17)) / 0.13)))))
    z, dx, dy = fx.cam(t)
    if z != 1.0 or dx or dy:
        zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
        x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
    vignette(img); grain(img, f)
    fx.draw(img, t); fx.overlay(img, t)
    caption(img, s, t, fx)
    return img

STOP = {"a", "an", "the", "of", "and", "to", "in", "on", "at", "is", "it", "it's", "was", "were", "my", "me", "i", "he", "she", "they", "we", "you",
        "his", "her", "their", "our", "your", "that", "this", "so", "but", "like", "just", "then", "with", "for", "up", "out", "all", "every", "there", "are", "be", "had", "has", "have", "even", "not", "no", "still"}
def _cl(w): return re.sub(r"[^\w']", "", w).lower()
def phrases(s):
    """split a shot's words into phrases (punctuation / pauses / max 5 words); each shows ONE keyword held for the whole phrase"""
    ws = WORDS[s]; out = []; cur = []
    for i, (w, a, b) in enumerate(ws):
        cur.append((w, a, b)); nxt = ws[i + 1][1] if i + 1 < len(ws) else None
        if re.search(r"[.,!?\u2026]$", w) or nxt is None or nxt - b > 0.28 or len(cur) >= 5: out.append(cur); cur = []
    res = []
    for ph in out:
        hot = [k for k, (w, a, b) in enumerate(ph) if _cl(w) in HOT]
        if hot:   # longest run of consecutive hot words starting at the first hot word
            k0 = hot[0]; k1 = k0
            while k1 + 1 < len(ph) and _cl(ph[k1 + 1][0]) in HOT: k1 += 1
            txt = " ".join(re.sub(r"[.,\u2026\-]+$", "", w) for w, _, _ in ph[k0:k1 + 1]); is_hot = True
        else:
            cand = [w for w, _, _ in ph if _cl(w) not in STOP] or [w for w, _, _ in ph]
            txt = re.sub(r"[.,\u2026\-]+$", "", max(cand, key=lambda w: len(_cl(w)))); is_hot = False
        res.append((txt.upper(), ph[0][1], ph[-1][2], is_hot))
    for k, (txt, hot) in CAPO.get(s, {}).items():
        if k < len(res): res[k] = (txt, res[k][1], res[k][2], hot)
    return res
CAPO = {"s10": {1: ("DON'T BUY", True)}, "s23": {1: ("TREE LIGHTING", True)}, "s24": {0: ("THE MAYOR", False)},
        "s35": {0: ("NO", True), 1: ("NO NO", True), 2: ("NO NO NO!", True)}, "s36": {0: ("CAN'T HIDE", True)},
        "s39": {0: ("SNUCK", True)}, "s46": {0: ("LED THEM", False), 1: ("OUT OF TOWN", True)}, "s50": {0: ("THEY PUT…", False)}}
_PH = {}
def caption(img, s, t, fx=None):
    if fx is not None and any(it[0] == "text" and it[2] <= t < it[2] + it[7] for it in fx.items): return   # a slam is on screen: no duplicate caption
    if s not in _PH: _PH[s] = phrases(s)
    ps = _PH[s]
    for i, (txt, a, b, hot) in enumerate(ps):
        end = ps[i + 1][1] if i + 1 < len(ps) else b + 0.4
        if max(0, a - 0.02) <= t < end:
            u = (t - a) / 0.16; sc = 1.0 + (0.22 if hot else 0.1) * max(0, 1 - u)
            paste_center(img, text_img(txt, fit(txt, 104 if hot else 90, 0.8, 11), GOLD if hot else (255, 255, 255), 11), W / 2, H * 0.74, sc)
            return

if __name__ == "__main__" and not os.environ.get("GLOW_NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{E}/glow_noaudio.mp4", set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
