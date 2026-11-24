"""IN MY TOWN Ep1 audio: VO + TEMPOREX 'Numbers' bed (ducked, with dramatic drop-outs) + SFX synced to the visuals.
Writes egg_mix.wav (with music) and egg_mix_nomusic.wav (post this one, add the sound inside TikTok)."""
import os, sys, json, math, subprocess
import numpy as np, soundfile as sf
os.environ["EGG_NOMAIN"] = "1"; sys.argv = ["x"]
exec(open("/home/claude/zara/egg_compose.py").read())
SR = 48000
shots = []; t = 0.0
for s in ORDER:
    info = f"{FR}/{s}/info.json"
    n = json.load(open(info))["n"] if os.path.exists(info) else int(round(DUR[s] * 24))
    shots.append((s, t, n / 24)); t += n / 24
TOTAL = t; N = int((TOTAL + 0.5) * SR); ST = {s: (a, d) for s, a, d in shots}
vo = np.zeros(N); sfx = np.zeros(N); rng = np.random.default_rng(11)
def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR); i0 = max(0, i); e = min(len(buf), i + len(sig))
    if e > i0: buf[i0:e] += g * sig[i0 - i:e - i]
def T(d): return np.arange(int(d * SR)) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
def pop_s(p=1.0):
    x = T(0.13); f = (900 * np.exp(-x * 25) + 320) * p; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 28) * 0.7
def bubble(p=1.0):
    x = T(0.18); f = (300 + 1400 * x / 0.18) * p; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 18) * 0.6
def whoosh(d=0.5):
    n = rng.standard_normal(int(d * SR)); n = np.convolve(n, np.ones(30) / 30, "same") * 3; return n * np.sin(np.pi * T(d) / d) ** 2 * 0.6
def impact(d=1.4):
    x = T(d); f = 35 + 90 * np.exp(-x * 12); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.5) + rng.standard_normal(len(x)) * np.exp(-x * 9) * 0.4) * 0.9
def chime(base=84, k=4):
    out = np.zeros(int(1.3 * SR))
    for j in range(k):
        s_ = np.sin(2 * np.pi * note(base + [0, 4, 7, 12, 16, 19][j % 6]) * T(0.8)) * np.exp(-T(0.8) * 5) * 0.25; i = int(j * 0.06 * SR); out[i:i + len(s_)] += s_
    return out
def siren(d=1.6):
    x = T(d); f = 700 + 250 * np.sin(2 * np.pi * 2.2 * x); return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12 * np.minimum(1, (d - x) / 0.2)
def scratch():
    x = T(0.45); f = 600 * np.abs(np.sin(2 * np.pi * 3 * x)) + 100; return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + rng.standard_normal(len(x)) * 0.15 * np.exp(-x * 4)
def popper():
    cr = np.zeros(int(0.8 * SR))
    for k in range(40):
        i = rng.integers(0, len(cr) - 200); cr[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 30) * 0.4
    cr[:int(0.4 * SR)] += rng.standard_normal(int(0.4 * SR)) * np.exp(-T(0.4) * 12) * 0.8; return cr * 0.6
def crack():
    out = np.zeros(int(0.5 * SR))
    for k in range(7):
        i = int((0.02 + k * 0.045 + rng.random() * 0.02) * SR); out[i:i + 400] += rng.standard_normal(400) * np.exp(-np.arange(400) / 60) * (0.9 - k * 0.08)
    return out
def heartbeat(): x = T(0.25); return np.sin(2 * np.pi * 55 * x) * np.exp(-x * 14) * 0.9
def riser(d):
    x = T(d); f = 180 + 1400 * (x / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + rng.standard_normal(len(x)) * 0.12) * (x / d) ** 2
def slam(): return impact(0.6) * 0.8 + whoosh(0.2)[: int(0.6 * SR)].tolist().__len__() * 0 + np.pad(whoosh(0.2), (0, int(0.4 * SR)))[: int(0.6 * SR)] * 0.5
def thud(): x = T(0.3); return np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 8) + 40) / SR) * np.exp(-x * 12)
def sparkle_s(d=1.0):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 14)):
        s_ = np.sin(2 * np.pi * note(rng.integers(88, 100)) * T(0.25)) * np.exp(-T(0.25) * 18) * 0.12; i = int(rng.random() * (len(out) - len(s_))); out[i:i + len(s_)] += s_
    return out

WSFX = {"RUN!!": impact, "SLAM!": thud, "CRACK!": crack, "GOLDEN EGG": lambda: chime(84, 6), "*touch*": lambda: chime(96, 2), "RULE #1": impact,
        "NOT A PET": lambda: impact(2.0), "WEE-OO!": lambda: siren(0.9), "EVERYONE!": lambda: chime(79, 4), "DEFINITELY": pop_s}
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.25 * rng.random()), a + it[2], 0.45)
        elif k == "text": add(sfx, WSFX.get(it[1], bubble)(), a + it[2], 0.85)
        elif k == "confetti": add(sfx, popper(), a + it[1], 0.6)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.35)
        elif k == "flash": add(sfx, whoosh(0.35), a + it[1] - 0.2, 0.45)
    add(sfx, whoosh(0.3), a - 0.12, 0.25)                                   # every cut gets a swish
# hypnotic beds: egg-rain plinks (rising), counter ticks, heartbeat into the hatch
a5, d5 = ST["e05"]; tt = a5; gap = 0.16
while tt < a5 + d5:
    add(sfx, bubble(0.9 + 0.9 * (tt - a5) / d5 + 0.1 * rng.random()), tt, 0.28); tt += gap; gap = max(0.05, gap * 0.94)
a12, d12 = ST["e12c"]; tt = a12; gap = 0.1
while tt < a12 + d12: add(sfx, pop_s(1.4 + (tt - a12) / d12), tt, 0.18); tt += gap; gap = max(0.04, gap * 0.93)
add(sfx, siren(ST["e04"][1]), ST["e04"][0], 0.45); add(sfx, siren(d12), a12, 0.5); add(sfx, siren(ST["e10"][1] - wt("e10", "touched")), ST["e10"][0] + wt("e10", "touched") + 0.2, 0.5)
add(sfx, scratch(), ST["e07"][0], 0.8); add(sfx, sparkle_s(ST["e08"][1]), ST["e08"][0], 0.6)
for k in range(int(ST["e09"][1] / 0.7)): add(sfx, heartbeat(), ST["e09"][0] + k * 0.7, 0.55)
a15, d15 = ST["e15"]; tn = wt("e15", "not")
for k in range(int(tn / 0.5)): add(sfx, heartbeat(), a15 + k * (0.5 - 0.02 * k), 0.6)
add(sfx, riser(tn), a15, 0.55); add(sfx, chime(72, 6), a15 + vo_end("e15") + 0.45, 0.55)
a13 = ST["e13"][0]; add(sfx, crack(), a13 + wt("e13", "crack.") + 0.3, 0.6)
# VO
for s, a, d in shots:
    y, sr = sf.read(f"{E}/vo/{s}.wav"); y = y if y.ndim == 1 else y.mean(1)
    if sr != SR: y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
    add(vo, y, a + LEADS[s], 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(env * 9, 0, 1)
# music bed: TEMPOREX - Numbers (instrumental). Drops: record scratch at e07 (back at "golden"), silence at e14, back on the end card.
mp = f"{E}/music/numbers.wav"
if not os.path.exists(mp): subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{E}/music/numbers_loop.mp3", "-ac", "1", "-ar", str(SR), mp], check=True)
mus, _ = sf.read(mp); mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
def hold(t0, t1, g): gain[int(t0 * SR):int(t1 * SR)] = g
e7 = ST["e07"][0]; ramp(e7, e7 + 0.12, 1, 0.0); g8 = ST["e08"][0] + wt("e08", "golden"); hold(e7 + 0.12, g8, 0.0); ramp(g8, g8 + 0.15, 0, 1)
e14 = ST["e14"][0]; ramp(e14, e14 + 0.2, 1, 0.0); end = a15 + vo_end("e15") + 0.45; hold(e14 + 0.2, end, 0.0); ramp(end, end + 0.1, 0, 1)
mus = mus * gain * (1 - 0.62 * talk) * 0.4
fade = np.ones(N); fl = int(0.8 * SR); fade[-fl:] = np.linspace(1, 0, fl)
def master(with_music):
    mix = vo * 1.05 + sfx * 0.5 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.2) / 1.2 * fade
    return mix[: int(TOTAL * SR)]
for name, wm in (("egg_mix.wav", True), ("egg_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"{E}/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
