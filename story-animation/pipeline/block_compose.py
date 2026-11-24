"""ON MY BLOCK Ep1 compositor: reuses the egg compositor (sky, FX engine, captions, hypnotic layers) with block-specific beats."""
import os, sys, json, math, random, re, subprocess
os.environ["EGG_NOMAIN"] = "1"; _argv = sys.argv[:]; sys.argv = ["x"]
exec(open("/home/claude/zara/egg_compose.py").read())
sys.argv = _argv
E = "/home/claude/zara/block"; FR = f"{E}/frames"
TL = json.load(open(f"{E}/timeline.json")); ORDER = TL["shots"]; DUR = TL["dur"]; LEADS = TL["lead"]; VOD = TL["vo"]; WORDS = TL["words"]
NIGHT = set()
HOT = {"everybody", "motion", "except", "me", "whip", "12", "heavy", "straight", "second", "inside", "store", "one", "library", "card",
       "today", "lemonade", "myself", "jordans", "crocs", "move", "moved", "moving", "block", "city", "ohio", "lots", "stop", "know"}
GOLDC = (255, 205, 40)

def build_fx(s, d):
    fx = FX(s, d); X = W / 2
    if s == "b01":
        for k, (x, y, e) in enumerate([(120, 330, "💸"), (600, 290, "🔥"), (150, 560, "💰"), (580, 600, "💯")]): fx.pop(e, 0.3 + k * 0.4, x, y, 0.9)
        te = wt(s, "everybody"); fx.word("EVERYBODY", te, X, 280, 110, (255, 255, 255), 0.9, -6); fx.punch(te, 0.12)
        tm = wt(s, "motion."); fx.word("MOTION", tm, X, 380, 140, GOLDC, 1.2, 5); fx.confetti(tm, X, 300, 80); fx.punch(tm, 0.16); fx.shake(tm, tm + 0.3, 8)
    elif s == "b02":
        fx.word("EXCEPT ME.", 0.15, X, 300, 104, (200, 200, 200), 1.4, 0); fx.pop("💀", 0.5, 590, 380, 1.0, life=1.2, rise=10)
    elif s == "b03":
        tw = wt(s, "whip."); fx.word("WHIP", tw, X, 270, 140, GOLDC, 1.0, -7); fx.pop("😎", tw + 0.1, 600, 360, 1.0); fx.sparkle(0, d, X, 650, 260, (255, 235, 150), 18)
        t12 = wt(s, "he's"); fx.word("HE'S 12", t12 + 0.15, X, 330, 118, (255, 90, 90), 1.3, 6); fx.pop("🧒", t12 + 0.3, 130, 420, 1.0); fx.punch(t12 + 0.15, 0.14); fx.shake(t12 + 0.15, t12 + 0.45, 8)
    elif s == "b04":
        fx.pop("🏋️", 0.4, 600, 330, 1.0); th = wt(s, "heavy"); fx.word("SO HEAVY", th, X, 270, 112, GOLDC, 1.1, -5)
        ts = wt(s, "straight."); fx.word("BONK!", ts + 0.1, X, 330, 150, (255, 120, 40), 1.0, 9); fx.shake(ts + 0.1, ts + 0.5, 16); fx.punch(ts + 0.1, 0.2); fx.pop("💥", ts + 0.12, 560, 560, 1.2)
    elif s == "b05":
        fx.pop("🏪", wt(s, "store,"), 130, 330, 1.0); t2 = wt(s, "second"); fx.word("STORE #2", t2, X, 260, 112, GOLDC, 1.1, -6); fx.punch(t2, 0.12)
        ti = wt(s, "inside"); fx.word("INSIDE?!", ti, X, 300, 140, (255, 90, 90), 1.2, 5); fx.pop("🤯", ti + 0.2, 600, 420, 1.1); fx.shake(ti, ti + 0.3, 8)
    elif s == "b06":
        for k in range(4): fx.pop("💸", 0.2 + k * 0.45, [120, 600, 160, 560][k], [330, 300, 560, 600][k], 0.85)
        to = wt(s, "one."); fx.word("HE'S ONE", to, X, 300, 120, (255, 90, 90), 1.2, -6); fx.pop("👶", to + 0.15, 600, 420, 1.1); fx.punch(to, 0.16)
    elif s == "b07":
        fx.pop("😐", 0.2, 590, 330, 0.9); tl = wt(s, "library"); fx.word("LIBRARY CARD", tl, X, 290, 96, (90, 170, 255), 1.6, 0); fx.pop("📚", tl + 0.2, 130, 420, 1.0)
    elif s == "b08":
        tt = wt(s, "today,"); fx.word("TODAY", tt, X, 270, 140, (255, 255, 255), 0.9, -6); fx.flash(tt, (255, 220, 120), 0.25, 0.6); fx.punch(tt, 0.14)
        tm = wt(s, "motion."); fx.word("MOTION", tm, X, 380, 140, GOLDC, 1.2, 6); fx.pop("😤", tm, 600, 430, 1.1); fx.shake(tm, tm + 0.3, 8)
    elif s == "b09":
        fx.pop("🍋", 0.25, 120, 330, 1.0); fx.pop("🤑", 0.7, 600, 330, 0.9)
        tm = wt(s, "myself."); fx.word("TO MYSELF", tm, X, 300, 110, (255, 255, 255), 1.4, -4); fx.pop("💀", tm + 0.25, 600, 430, 1.1); fx.punch(tm, 0.18)
    elif s == "b10":
        tj = wt(s, "jordans."); fx.word("JORDANS", tj, X, 270, 120, (255, 90, 90), 1.1, -6); fx.pop("👟", tj + 0.1, 600, 330, 1.0); fx.sparkle(tj, tj + 1, X, 500, 200, (255, 255, 255), 10)
        tc = wt(s, "crocs."); fx.word("CROCS", tc, X, 300, 150, (120, 230, 90), 1.4, 7); fx.pop("🐊", tc + 0.1, 130, 420, 1.2); fx.shake(tc, tc + 0.4, 12); fx.punch(tc, 0.2)
    elif s == "b11a":
        fx.pop("🙏", 0.3, 600, 330, 1.0); fx.word("UNCLE RAY", wt(s, "uncle"), X, 270, 96, GOLDC, 1.2, -4)
    elif s == "b11b":
        fx.pop("🧠", 0.3, 120, 330, 0.9); tm = wt(s, "move.")
        fx.word("MOVE.", tm, X, 330, 190, (255, 255, 255), 1.4, 0); fx.flash(tm, (255, 255, 255), 0.25, 0.8); fx.shake(tm, tm + 0.4, 14); fx.punch(tm, 0.22)
    elif s == "b12":
        tk = wt(s, "kept"); fx.speed(tk, d, 24); fx.pop("🏃", 0.3, 600, 330, 1.0); fx.word("KEPT MOVING", tk, X, 280, 104, GOLDC, 1.1, -5)
    elif s == "b13":
        fx.speed(0, d, 36); fx.shake(0, d, 4)
        fx.word("PAST THE BLOCK", wt(s, "past"), X, 260, 96, (255, 255, 255), 0.8, -5); fx.word("PAST THE CITY", wt(s, "past", 1), X, 330, 100, GOLDC, 0.9, 5); fx.pop("💨", 0.3, 120, 420, 1.1)
    elif s == "b14":
        fx.speed(0, d, 30); to = wt(s, "ohio."); fx.word("OHIO?!", to, X, 330, 180, (255, 90, 90), 1.3, -6); fx.shake(to, d, 10); fx.punch(to, 0.22)
        fx.pop("🌽", to + 0.1, 120, 420, 1.1); fx.pop("😱", 0.2, 600, 330, 1.0)
    elif s == "b15":
        tl = wt(s, "lots"); fx.word("LOTS OF MOTION", tl, X, 280, 100, GOLDC, 1.6, -4); fx.pop("🌍", 0.3, 600, 330, 1.0); fx.pop("😂", tl, 120, 400, 1.0)
    elif s == "b16":
        fx.pop("🤨", 0.3, 600, 330, 1.0); ts = wt(s, "stop?"); fx.word("HOW YOU STOP?", wt(s, "how"), X, 290, 100, (255, 255, 255), 1.3, -4)
        for k in (2, int(d * 24 * 0.4), int(d * 24 * 0.75)): fx.flash(k / 24 + 0.08, (255, 255, 255), 0.12, 0.25)
    elif s == "b17":
        fx.speed(0, d, 30); fx.word("I DON'T KNOW!!!", 0.05, X, 330, 150, (255, 70, 70), 1.4, -5); fx.shake(0, 1.4, 14); fx.punch(0.05, 0.2)
    for i, it in enumerate(fx.items):
        if it[0] == "text":
            k, txt, t0, x, y, sz, fill, life, rot = it
            fx.items[i] = (k, txt, t0, x, y, fit(txt, sz, 0.8), fill, life, rot)
    return fx

GR = {"b02": "desat", "b07": "desat"}

def endcard(img, t0, t):
    u = t - t0
    if u < 0: return
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, int(min(1, u / 0.25) * 170))))
    tunnel(img, W / 2, H * 0.42, u, 0.6, 6, 1100, (255, 205, 60), 12, 0.35)
    paste_center(img, text_img("HOW DOES HE STOP?", fit("HOW DOES HE STOP?", 84, 0.84, 10), GOLDC, 10), W / 2, H * 0.26, ease_pop(u * 1.8), -3)
    paste_center(img, emoji("🏃"), W / 2, H * 0.40, ease_pop((u - 0.2) * 1.8) * (1.3 + 0.08 * math.sin(u * 9)), 8 * math.sin(u * 7))
    paste_center(img, text_img("wrong answers only", 50, (255, 255, 255), 7), W / 2, H * 0.52, ease_pop((u - 0.4) * 1.8))
    paste_center(img, emoji("👇"), W / 2, H * 0.60, ease_pop((u - 0.55) * 1.8) * 0.7)
    paste_center(img, text_img("PART 2", 128, (90, 230, 255), 11), W / 2, H * 0.74, ease_pop((u - 0.8) * 1.6), -4)

def shot_frame(s, f, n, fx, trk, cache):
    t = (f - 1) / FPS; T = n / FPS
    p = f"{FR}/{s}/{f:04d}.png"
    if os.path.exists(p): cache["last"] = p
    base = SKY_DAY.copy()
    ex, ey = (trk[f - 1][0] * W, trk[f - 1][1] * H) if trk and trk[f - 1] else (W / 2, H * 0.4)
    # hypnotic sky layers (behind the render)
    if s in ("b01", "b03"): sunburst(base, W / 2, H * 0.25, t * 0.6, (255, 214, 90), None, 20, 0.3)
    if s == "b06": sunburst(base, ex, ey, t * 0.9, (120, 230, 120), None, 22, 0.35)
    if s == "b08": sunburst(base, ex, ey, -t * 1.2, (255, 120, 60), (255, 210, 120), 18, 0.75)
    if s == "b15": sunburst(base, W / 2, H * 0.45, t * 1.4, (255, 225, 120), (130, 200, 255), 24, 0.6)
    if s == "b11b" and t >= wt(s, "move."): sunburst(base, W / 2, H * 0.4, t * 3, (255, 70, 70), (255, 230, 230), 16, 0.85)
    if cache.get("last"): base.alpha_composite(Image.open(cache["last"]).convert("RGBA"))
    img = grade2(base, s)
    if s == "b05" and t > wt(s, "inside") + 0.15: tunnel(img, W / 2, H * 0.47, t, 0.35, 8, 1100, (255, 220, 60), 14, 0.55, 1.3)
    if s == "b15": tunnel(img, W / 2, H * 0.55, t, 0.6, 7, 1200, (255, 255, 255), 10, 0.3, 1.4)
    if s == "b03" and trk: glow(img, ex, ey, 260, (255, 210, 80), 0.4)
    z, dx, dy = fx.cam(t)
    if z != 1.0 or dx or dy:
        zw, zh = int(W * z), int(H * z); im2 = img.resize((zw, zh), Image.BILINEAR)
        x0 = int((zw - W) / 2 - dx); y0 = int((zh - H) / 2 - dy)
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.paste(im2, (-x0, -y0)); img = c
    fx.draw(img, t); fx.overlay(img, t)
    # racing counters
    if s == "b05" and t > wt(s, "inside"): counter(img, "STORES:", int(3 * 333 ** min(1, (t - wt(s, "inside")) / max(0.1, T - wt(s, "inside")))), t)
    if s == "b06": counter(img, "LIL BRO NET WORTH: $", int(10 ** (2 + 4 * min(1, t / T) ** 0.8)), t, (140, 255, 140))
    if s == "b09" and t > wt(s, "one"): counter(img, "CUPS SOLD:", 1, t, (255, 240, 120), pulse=False)
    if s == "b07": counter(img, "MY MOTION:", 0, t, (200, 200, 200), pulse=False)
    if s == "b15": counter(img, "MILES RAN:", int(10 ** (1 + 4 * min(1, t / T))), t, GOLDC)
    end_t = vo_end("b17") + 0.35 if s == "b17" else None
    caption(img, s, t, end_t)
    if s == "b17": endcard(img, end_t, t)
    return img

if __name__ == "__main__" and not os.environ.get("BLOCK_NOMAIN"):
    main(sys.argv[1] if len(sys.argv) > 1 else f"{E}/block_noaudio.mp4", set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
