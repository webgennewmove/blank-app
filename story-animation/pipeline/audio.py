"""Soundtrack: VO + mood-following kid-friendly score + SFX synced to every visual pop."""
import json, math, os, sys, subprocess
import numpy as np, soundfile as sf
sys.argv = ["x"]
src = open("/home/claude/zara/compose.py").read().replace('if __name__ == "__main__":', "if False:")
exec(src)

SR = 48000
shots = []
t = 0.0
for s in ORDER:
    info = f"{Z}/frames/{s}/info.json"
    n = json.load(open(info))["n"] if os.path.exists(info) else int(round(DUR[s] * FPS))
    shots.append((s, t, n / FPS)); t += n / FPS
TOTAL = t; N = int((TOTAL + 1.0) * SR)
ST = {s: (a, d) for s, a, d in shots}
mus = np.zeros(N); sfx = np.zeros(N); vo = np.zeros(N)
rng = np.random.default_rng(5)
def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR); i0 = max(0, i); e = min(len(buf), i + len(sig))
    if e > i0: buf[i0:e] += g * sig[i0 - i:e - i]
def T(n_sec): return np.arange(int(n_sec * SR)) / SR
def env_ad(n_sec, a=0.005, dec=8.0):
    tt = T(n_sec); return np.minimum(1, tt / a) * np.exp(-tt * dec)
def note(f): return 440 * 2 ** ((f - 69) / 12)

# ---------------- instruments
def pluck(m, dur=0.35, bright=1.0):
    tt = T(dur); f = note(m)
    return (np.sin(2 * np.pi * f * tt) + 0.4 * bright * np.sin(4 * np.pi * f * tt) + 0.15 * np.sin(6 * np.pi * f * tt)) * env_ad(dur, 0.003, 9)
def marimba(m, dur=0.4):
    tt = T(dur); f = note(m)
    return (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 30)) * env_ad(dur, 0.002, 7)
def bass(m, dur=0.25):
    tt = T(dur); f = note(m)
    return (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env_ad(dur, 0.005, 6)
def kick():
    tt = T(0.35); f = 45 + 110 * np.exp(-tt * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def clap():
    n = rng.standard_normal(int(0.18 * SR)); tt = T(0.18)
    e = np.exp(-tt * 25) + 0.6 * np.exp(-np.maximum(0, tt - 0.012) * 30) * (tt > 0.012)
    return np.convolve(n, [1, -0.9], "same") * e * 0.5
def hat():
    n = rng.standard_normal(int(0.05 * SR)); return np.diff(n, prepend=0) * np.exp(-T(0.05) * 70) * 0.25
def pad(ms, dur, vol=0.15, trem=0.0):
    tt = T(dur); s = sum(np.sin(2 * np.pi * note(m) * tt + k) + 0.5 * np.sin(2 * np.pi * note(m) * 1.003 * tt) for k, m in enumerate(ms))
    e = np.minimum(1, tt / 0.6) * np.minimum(1, (dur - tt) / 0.6)
    return s / len(ms) * e * vol * (1 + trem * np.sin(2 * np.pi * 5 * tt))

# ---------------- score sections
BPM = 120; B = 60 / BPM
CHORDS_HAPPY = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]   # C G Am F
MEL = [72, 76, 79, 76, 74, 72, 74, 76, 79, 81, 79, 76, 74, 76, 72, 67]
def happy(t0, t1, big=False):
    b = 0; tt = t0
    while tt < t1 - 0.05:
        bar = int(b // 4) % 4; ch = CHORDS_HAPPY[bar]
        add(mus, kick(), tt, 0.55 if b % 2 == 0 else 0.0)
        if b % 2 == 1: add(mus, clap(), tt, 0.5)
        add(mus, hat(), tt + B / 2, 0.6); add(mus, hat(), tt, 0.3)
        add(mus, bass(ch[0] - 24, B * 0.9), tt, 0.5); add(mus, bass(ch[0] - 12, B * 0.4), tt + B / 2, 0.25)
        m = MEL[b % 16]
        add(mus, marimba(m, 0.4), tt, 0.28); add(mus, marimba(ch[(b) % 3] + 12, 0.3), tt + B / 2, 0.14)
        if big: add(mus, pluck(m + 12, 0.4), tt, 0.12); add(mus, pad(ch, B, 0.08), tt)
        tt += B; b += 1
def sad(t0, t1):
    chs = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]; tt = t0; k = 0
    while tt < t1 - 0.1:
        dur = min(2 * B * 2, t1 - tt); add(mus, pad(chs[k % 4], dur, 0.16), tt)
        for j, m in enumerate(chs[k % 4]): add(mus, pluck(m + 12, 1.0, 0.4), tt + j * 0.35, 0.12)
        tt += 4 * B; k += 1
def tension(t0, t1):
    tt = t0
    while tt < t1:
        add(mus, bass(40, 0.2), tt, 0.6); add(mus, bass(40, 0.2), tt + 0.25, 0.4); tt += 0.5
    dur = t1 - t0; x = T(dur); f = 200 + 900 * (x / dur) ** 2
    add(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / dur) ** 2 * 0.12, t0)
def freeze(t0, t1):
    dur = t1 - t0; add(mus, pad((84, 88, 91, 95), dur, 0.07, trem=0.3), t0)
    tt = t0
    while tt < t1:
        tk = rng.standard_normal(int(0.02 * SR)) * np.exp(-T(0.02) * 300) * 0.5
        add(mus, np.convolve(tk, [1, -0.95], "same"), tt, 0.7); tt += 0.5
def mystery(t0, t1):
    dur = t1 - t0; add(mus, pad((45, 52, 57), dur, 0.15), t0)
    box = [69, 72, 76, 75, 72, 69, 68, 71]; tt = t0; k = 0
    while tt < t1 - 0.2:
        add(mus, marimba(box[k % 8] + 12, 0.8), tt, 0.13)
        tk = rng.standard_normal(int(0.02 * SR)) * np.exp(-T(0.02) * 300) * 0.3
        add(mus, np.convolve(tk, [1, -0.95], "same"), tt, 0.5); tt += 0.5; k += 1

def at(s, frac=0.0): a, d = ST[s]; return a + d * frac
happy(0, at("s09")); sad(at("s09") + 0.1, at("s13")); tension(at("s13"), at("s15") + ST["s15"][1] * 0.62)
freeze(at("s16"), at("s18")); happy(at("s18"), at("s20"), big=True); mystery(at("s20"), TOTAL + 0.5)

# ---------------- sfx library
def pop_s(): x = T(0.12); f = 900 * np.exp(-x * 25) + 300; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30) * 0.6
def boing():
    x = T(0.6); f = 180 + 500 * x / 0.6 + 60 * np.sin(2 * np.pi * 14 * x); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 3) * 0.5
def whoosh(d=0.5, up=True):
    n = rng.standard_normal(int(d * SR)); n = np.convolve(n, np.ones(30) / 30, "same") * 3
    e = np.sin(np.pi * T(d) / d) ** 2; return n * e * 0.6
def popper():
    n = rng.standard_normal(int(0.4 * SR)) * np.exp(-T(0.4) * 12)
    cr = np.zeros(int(0.8 * SR));
    for k in range(40): i = rng.integers(0, len(cr) - 200); cr[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 30) * 0.4
    out = np.zeros(int(0.8 * SR)); out[:len(n)] += n * 0.8; return out + cr * 0.6
def chime(base=84, k=4):
    out = np.zeros(int(1.2 * SR))
    for j in range(k):
        s = np.sin(2 * np.pi * note(base + [0, 4, 7, 12, 16, 19][j % 6]) * T(0.8)) * np.exp(-T(0.8) * 5) * 0.25
        i = int(j * 0.06 * SR); out[i:i + len(s)] += s
    return out
def honk():
    x = T(0.7); s = np.sign(np.sin(2 * np.pi * 311 * x)) * 0.3 + np.sign(np.sin(2 * np.pi * 392 * x)) * 0.3
    s = np.convolve(s, np.ones(12) / 12, "same"); return s * np.minimum(1, x / 0.02) * np.minimum(1, (0.7 - x) / 0.05) * 0.5
def impact():
    x = T(1.6); f = 35 + 90 * np.exp(-x * 12); b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.5)
    n = rng.standard_normal(len(x)) * np.exp(-x * 9) * 0.4; return (b + n) * 0.9
def scratch():
    x = T(0.5); f = 600 * np.abs(np.sin(2 * np.pi * 3 * x)) + 100
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + rng.standard_normal(len(x)) * 0.15 * np.exp(-x * 4)
def reverse_cym(d=1.0):
    n = rng.standard_normal(int(d * SR)); n = np.diff(n, prepend=0); return n * (T(d) / d) ** 3 * 0.35
def ding(): return chime(88, 2)
def laughsfx():
    out = np.zeros(int(1.2 * SR))
    for j in range(5):
        x = T(0.12); s = np.sin(2 * np.pi * (500 - j * 30) * x) * np.sin(np.pi * x / 0.12) * 0.25; i = int(j * 0.17 * SR); out[i:i + len(s)] += s
    return out

EMOJI_SFX = {"❤": ding, "💖": ding, "💕": ding, "✨": lambda: chime(91, 4), "⭐": lambda: chime(88, 3), "⚠": honk}
WORD_SFX = {"BOING!": boing, "ZOOM!": lambda: whoosh(0.7), "HONK!": honk, "STOP!": impact, "WOW!": lambda: chime(84, 6),
            "HAHA": laughsfx, "TIME STOPPED": lambda: chime(96, 3), "boing?": lambda: boing() * 0.4, "flap flap": lambda: whoosh(0.3) * 0.6, "10!": lambda: chime(84, 5)}
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, EMOJI_SFX.get(it[1], pop_s)(), a + it[2], 0.55)
        elif k == "text": add(sfx, WORD_SFX.get(it[1], pop_s)(), a + it[2], 0.8)
        elif k == "confetti": add(sfx, popper(), a + it[1], 0.7)
        elif k == "ring": add(sfx, whoosh(0.4), a + it[1], 0.5)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.4)
        elif k == "flash": add(sfx, reverse_cym(0.5), a + it[1] - 0.5, 0.6)
# story-specific
add(sfx, scratch(), at("s09") + 0.05, 0.9)
add(sfx, reverse_cym(1.2), at("s16") - 1.0, 0.7)
add(sfx, chime(72, 6), at("s16") + 0.05, 0.5)
add(sfx, whoosh(0.8), at("s19", 0.55), 0.8)
for k in range(4): add(sfx, kick() * 0.8, at("s02") + ST["s02"][1] * 0.72 + k * 0.001, 0.3)
add(sfx, impact() * 0.7, at("s22") + LEAD + VOD["s22"] + 0.45, 0.9)
add(sfx, chime(76, 6), at("s22") + LEAD + VOD["s22"] + 0.5, 0.5)
# dog bark-ish yip on puppy pops
# VO
for s, a, d in shots:
    p = f"{Z}/vo/{s}.wav"
    if os.path.exists(p):
        y, sr = sf.read(p); add(vo, y if y.ndim == 1 else y.mean(1), a + LEAD, 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); duck = 1 - 0.6 * np.clip(env * 9, 0, 1)
mix = vo * 1.0 + mus * 0.6 * duck + sfx * 0.55 * (1 - 0.35 * np.clip(env * 9, 0, 1))
mix = np.tanh(mix * 1.2) / 1.2
mix = mix[: int(TOTAL * SR)]
sf.write(f"{Z}/soundtrack.wav", np.stack([mix, mix], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
