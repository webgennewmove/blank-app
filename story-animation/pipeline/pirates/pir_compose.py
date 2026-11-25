"""PIRATES compositor: day grade, bloom, keyword captions (one per phrase), slams, CAPTAINS TODAY counter, reticle, loop."""
import os, sys, json, math, random, re, subprocess
os.environ["EGG_NOMAIN"] = "1"; _argv = sys.argv[:]; sys.argv = ["x"]
exec(open("/home/claude/zara/egg_compose.py").read())
sys.argv = _argv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
E = "/home/claude/zara/pirates/ep"; FR = f"{E}/frames"
TL = json.load(open(f"{E}/timeline.json")); ORDER = TL["shots"]; DUR = TL["dur"]; WORDS = TL["words"]; T0 = TL["t0"]
HOT = {"one", "rule", "captain's", "hat", "is", "captain", "captain.", "seagull", "fries", "boss", "cargo", "ship", "rpg", "dale", "anything", "ocean",
       "kevin's", "rope", "short", "kevin", "standoff", "ten", "zero", "sneezed", "their", "overboard", "jumped", "rules", "again", "cook's", "lunch",
       "break", "same", "sandwiches", "crane's", "best", "wind", "boat", "lifeboat", "whole", "hat", "dolphin", "leader", "life", "no", "ka-boom",
       "hit", "something", "container", "wall", "sea", "wave", "surfed", "deck", "me", "now", "order", "stop", "shooting", "worked", "gust"}
STOP = {"a", "an", "the", "of", "and", "to", "in", "on", "at", "it", "was", "my", "i", "he", "we", "him", "our", "their", "that", "so", "then", "all", "his",
        "up", "for", "there's", "whoever", "wears", "has", "never", "including", "too", "onto", "said", "now", "into", "with", "two", "seconds", "first", "look", "i'm"}
GOLD = (255, 205, 60); WHITE = (255, 255, 255); RED = (255, 80, 70); AQUA = (120, 230, 255)
def wt(s, word, k=0):
    word = word.lower().strip(".,!?-…\"")
    hits = [a for w, a, b in WORDS[s] if w.lower().strip(".,!?-…\"") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
# CAPTAINS TODAY counter: value changes at (shot, t)
CHANGES = [("p01", 0.0, 1), ("p07", 0.45, 2), ("p20", 1.9, 3), ("p26", 0.3, 4), ("p29", 0.55, 5), ("p35", 1.0, 6), ("p46", 0.6, 7), ("p51", 0.7, 8)]
CH_T = sorted((T0[s] + t, v) for s, t, v in CHANGES)
def captains(gt):
    v = 0; tc = -9
    for t, val in CH_T:
        if gt >= t: v = val; tc = t
    return v, tc
def build_fx(s, d):
    fx = FX(s, d); X = W / 2
    if s == "p01": fx.word("HAT = CAPTAIN", 0.0, X, 330, 120, GOLD, 1.0, -4); fx.pop("🎩", 0.05, 560, 460, 1.0)
    elif s == "p02": fx.word("IS THE CAPTAIN", wt(s, "is"), X, 330, 120, GOLD, 1.4, 4); fx.punch(wt(s, "is"), 0.08)
    elif s == "p04": fx.pop("🍟", 0.5, 560, 460, 1.0)
    elif s == "p05": fx.word("GULP!", d * 0.55, X, 360, 120, WHITE, 0.6, -6)
    elif s == "p06": fx.pop("👍", 0.25, 560, 440, 1.0)
    elif s == "p07": fx.word("YOINK!", 0.35, X, 330, 130, GOLD, 0.6, 6); fx.punch(0.35, 0.08)
    elif s == "p08": fx.speed(0, d, 22, True)
    elif s == "p09": fx.word("FWOOSH!", d * 0.45, X, 330, 140, (255, 170, 60), 0.8, -6); fx.flash(d * 0.45, (255, 210, 140), 0.15, 0.35); fx.shake(d * 0.45, d * 0.45 + 0.3, 8)
    elif s == "p11": fx.sparkle(d * 0.55, d, X, H * 0.35, 120, (255, 255, 230), 10)
    elif s == "p12": fx.word("CLANK!", 0.0, 250, 360, 92, WHITE, 0.4, -8); fx.word("CLANK!", 0.3, 460, 470, 92, WHITE, 0.4, 8)
    elif s == "p15": fx.pop("👍", 0.3, 560, 440, 1.0)
    elif s == "p18": fx.word("ZERO PLAN", wt(s, "zero"), X, 330, 140, RED, 1.2, -5); fx.punch(wt(s, "zero"), 0.1)
    elif s in ("p19", "p24"): t_ = wt(s, "sneezed"); fx.word("ACHOO!", t_, X, 330, 150, AQUA, 0.7, -7); fx.shake(t_, t_ + 0.3, 9)
    elif s == "p28": fx.word("ACHOO!", 0.2, X, 330, 140, AQUA, 0.45, 7); fx.shake(0.2, 0.5, 9); fx.word("PING!", 0.55, 480, 560, 100, WHITE, 0.45, -10)
    elif s in ("p20", "p25"): fx.word("PING!", 0.33 if s == "p20" else d * 0.4, 500, 440, 110, WHITE, 0.45, -10)
    elif s == "p21": fx.pop("🧃", 0.2, 560, 440, 1.0)
    elif s == "p23": fx.word("SPLASH!", 0.4, X, 330, 150, AQUA, 0.9, -6)
    elif s == "p26": fx.pop("🥪", wt(s, "lunch"), 560, 430, 1.0); fx.word("LUNCH BREAK!", wt(s, "lunch"), X, 330, 120, GOLD, 1.0, -5)
    elif s == "p30": fx.pop("🐦", d * 0.6, 560, 440, 1.0)
    elif s == "p31": fx.word("WHOOSH!", 0.1, X, 330, 130, WHITE, 0.7, 5)
    elif s in ("p32", "p33"): fx.speed(0, d, 24, True)
    elif s == "p34": fx.pop("🎩", 0.4, 560, 430, 1.0)
    elif s == "p35": fx.sparkle(d * 0.4, d, X, H * 0.42, 200, (255, 240, 170), 14)
    elif s == "p38": fx.word("NO—", 0.05, X, 330, 160, RED, 0.6, -6); fx.flash(d * 0.35, (255, 210, 140), 0.12, 0.3)
    elif s == "p39": fx.flash(0.17, (255, 245, 220), 0.2, 0.9); fx.shake(0.17, d, 16); fx.word("KA-BOOM!", 0.17, X, 330, 180, (255, 150, 40), d, -6); fx.punch(0.17, 0.15)
    elif s == "p40": fx.pop("😎", d * 0.6, 560, 440, 1.0)
    elif s == "p42": fx.shake(0, d, 10)
    elif s == "p43": fx.shake(0, d, 6)
    elif s == "p44": fx.pop("🏄", 0.3, 560, 430, 1.0); fx.shake(d * 0.5, d * 0.5 + 0.35, 12); fx.word("THUD!", d * 0.55, X, 360, 140, WHITE, 0.6, 6)
    elif s == "p45": fx.sparkle(0, d, X, H * 0.4, 160, (255, 245, 200), 12)
    elif s == "p47": t_ = wt(s, "i'm"); fx.word("I'M THE", t_, X, 330, fit("CAPTAIN NOW!", 140, 0.82), GOLD, d - t_, -4); fx.word("CAPTAIN NOW!", t_ + 0.2, X, 450, 140, GOLD, d - t_ - 0.2, 4); fx.punch(t_ + 0.2, 0.14); fx.shake(t_ + 0.2, t_ + 0.45, 7)
    elif s == "p49": fx.pop("🥪", 0.4, 560, 440, 1.0)
    elif s == "p51": fx.word("HAT = CAPTAIN", d * 0.5, X, 330, 110, GOLD, d * 0.5 + 0.02, 4)
    for i, it in enumerate(fx.items):
        if it[0] == "text":
            k, txt, t0, x, y, sz, fill, life, rot = it
            fx.items[i] = (k, txt, t0, x, y, fit(txt, sz, 0.82), fill, life, rot)
    return fx

def day_grade(img, s):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    a = np.clip((a - 0.5) * 1.1 + 0.5, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8)); out = ImageEnhance.Color(out).enhance(1.25)
    br = out.point(lambda v: max(0, v - 215) * 3); bl = br.filter(ImageFilter.GaussianBlur(18))
    out = ImageChops.add(out, bl.point(lambda v: int(v * 0.35)))
    return out.convert("RGBA")
_VIG = None
def vignette(img):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        al = np.clip((r - 0.8) / 0.6, 0, 1) ** 1.6 * 90
        _VIG = Image.fromarray(np.dstack([np.zeros((H, W, 3)), al]).astype(np.uint8), "RGBA")
    img.alpha_composite(_VIG)
def reticle(img, t, d):
    """RPG scope: drifts over sky / sea / hat only (upper-left area), never a person"""
    dr = ImageDraw.Draw(img); cx = W * (0.32 + 0.08 * math.sin(t * 1.3)); cy = H * (0.22 + 0.05 * math.cos(t * 1.1)); r = 90
    c = (255, 60, 50, 230)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=6)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): dr.line([(cx + dx * 30, cy + dy * 30), (cx + dx * 120, cy + dy * 120)], fill=c, width=5)
def shot_frame(s, f, n, fx, trk, cache):
    t = (f - 1) / FPS; T = n / FPS; gt = T0[s] + t
    p = f"{FR}/{s}/{f:04d}.png"
    if os.path.exists(p): cache["last"] = p
    base = Image.open(cache["last"]).convert("RGBA") if cache.get("last") else Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if base.size != (W, H): base = base.resize((W, H))
    img = day_grade(base, s)
    if s == "p45": glow(img, W / 2, H * 0.4, 300, (255, 240, 190), 0.25)
    if s == "p41": rays = Image.new("RGBA", (W, H)); sunburst(rays, W / 2, H * 0.2, t * 0.5, (255, 230, 150), None, 20, 0.12); img.alpha_composite(rays)
    z, dx, dy = fx.cam(t)
    if z != 1.0 or dx or dy:
        zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
        x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
    vignette(img)
    if s == "p37": reticle(img, t, T)
    fx.draw(img, t); fx.overlay(img, t)
    v, tc = captains(gt)
    if v: counter(img, "CAPTAINS TODAY:", v, gt - tc, GOLD, y=205, pulse=(gt - tc) < 0.5)
    caption(img, s, t, fx)
    return img
def _cl(w): return re.sub(r"[^\w'-]", "", w).lower()
CAPO = {"p01": {0: ("MY PIRATE CREW", False), 1: ("ONE RULE", True)}, "p05": {0: ("WE GAVE HIM", False), 1: ("ALL OUR FRIES", True)}, "p06": {0: ("TOUGH BOSS", True)},
        "p09": {0: ("DALE FIRED THE RPG", True)}, "p22": {0: ("SO WE JUMPED", True)}, "p23": {0: ("RULES ARE RULES", True)}, "p25": {0: ("NOW THE COOK'S…", True)},
        "p27": {0: ("SANDWICHES", True)}, "p32": {0: ("OUR BOAT", True)}, "p36": {0: ("GREAT LEADER", True)}, "p38": {0: ("DALE,", False)},
        "p42": {0: ("INTO THE SEA", True)}, "p43": {0: ("AND THE WAVE…", True)}, "p45": {0: ("FLOATED DOWN", True)}, "p40": {0: ("HIT SOMETHING", True)}, "p46": {0: ("ONTO ME!", True)},
        "p50": {0: ("GUST!", True), 1: ("TOOK THE HAT", True)}, "p02": {0: ("CAPTAIN'S HAT", True)}, "p03": {0: ("WHOEVER.", False)}, "p04": {0: ("TODAY", False), 1: ("SEAGULL", True)},
        "p08": {0: ("CARGO SHIP!", True)}, "p10": {0: ("NEVER HIT", True)}, "p11": {0: ("OCEAN", True)}, "p16": {0: ("STANDOFF", True)},
        "p17": {0: ("TEN GUNS", True), 1: ("TEN GUYS", True)}, "p20": {0: ("A SHOT", False), 1: ("THEIR CAPTAIN", True)}, "p21": {0: ("HE SAID", False), 1: ("OVERBOARD!", True)},
        "p26": {0: ("COOK'S CAPTAIN", True), 2: ("SAME RULE", True)}, "p29": {0: ("CRANE'S CAPTAIN", True)}, "p30": {0: ("BEST CAPTAIN", True)},
        "p34": {0: ("WHOLE CARGO SHIP", True), 1: ("ONE HAT!", True)}, "p35": {0: ("DOLPHIN CAPTAIN", True), 1: ("FOR TWO SECONDS", False)}, "p37": {0: ("LINED UP", False), 1: ("SHOT OF HIS LIFE", True)},
        "p41": {0: ("CONTAINER WALL", True)}, "p44": {0: ("ONTO THE DECK!", True)}, "p47": {0: ("LOOK AT ME", False), 1: ("I'M THE CAPTAIN NOW", True)},
        "p48": {0: ("FIRST ORDER", False), 1: ("EVERYONE…", False), 2: ("STOP SHOOTING", True)}, "p49": {0: ("IT WORKED", True)}, "p51": {0: ("HE'S THE CAPTAIN NOW", True)}}
def phrases(s):
    ws = WORDS[s]; out = []; cur = []
    for i, (w, a, b) in enumerate(ws):
        cur.append((w, a, b)); nxt = ws[i + 1][1] if i + 1 < len(ws) else None
        if re.search(r"[.,!?:…—\"]$", w) or nxt is None or nxt - b > 0.28 or len(cur) >= 5: out.append(cur); cur = []
    res = []
    for ph in out:
        hot = [k for k, (w, a, b) in enumerate(ph) if _cl(w) in HOT]
        if hot:
            k0 = hot[0]; k1 = k0
            while k1 + 1 < len(ph) and _cl(ph[k1 + 1][0]) in HOT: k1 += 1
            txt = " ".join(re.sub(r"[.,…\"]+$", "", w).strip('"') for w, _, _ in ph[k0:k1 + 1]); is_hot = True
        else:
            cand = [w for w, _, _ in ph if _cl(w) not in STOP] or [w for w, _, _ in ph]
            txt = re.sub(r"[.,…\"]+$", "", max(cand, key=lambda w: len(_cl(w)))).strip('"'); is_hot = False
        res.append((txt.upper(), ph[0][1], ph[-1][2], is_hot))
    for k, (txt, hot) in CAPO.get(s, {}).items():
        if k < len(res): res[k] = (txt, res[k][1], res[k][2], hot)
    return res
_PH = {}
def caption(img, s, t, fx=None):
    if fx is not None and any(it[0] == "text" and it[2] <= t < it[2] + it[7] for it in fx.items): return
    if s not in _PH: _PH[s] = phrases(s)
    ps = _PH[s]
    for i, (txt, a, b, hot) in enumerate(ps):
        end = ps[i + 1][1] if i + 1 < len(ps) else b + 0.4
        if max(0, a - 0.02) <= t < end:
            u = (t - a) / 0.16; sc = 1.0 + (0.22 if hot else 0.1) * max(0, 1 - u)
            base = 104 if hot else 90; sz = fit(txt, base, 0.8, 11); col = GOLD if hot else WHITE; ws_ = txt.split()
            if sz < base * 0.85 and len(ws_) > 1:
                k = min(range(1, len(ws_)), key=lambda k: abs(len(" ".join(ws_[:k])) - len(" ".join(ws_[k:]))))
                l1, l2 = " ".join(ws_[:k]), " ".join(ws_[k:]); sz = min(fit(l1, base, 0.8, 11), fit(l2, base, 0.8, 11))
                paste_center(img, text_img(l1, sz, col, 11), W / 2, H * 0.74 - sz * 0.55, sc); paste_center(img, text_img(l2, sz, col, 11), W / 2, H * 0.74 + sz * 0.55, sc)
            else: paste_center(img, text_img(txt, sz, col, 11), W / 2, H * 0.74, sc)
            return

if __name__ == "__main__" and not os.environ.get("PIR_NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{E}/pir_noaudio.mp4", set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
