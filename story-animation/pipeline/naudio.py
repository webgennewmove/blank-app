"""Hood ep audio: VO + Numbers instrumental (ducked) + SFX synced to every visual. Writes two mixes."""
import sys, os, json, math, subprocess
import numpy as np, soundfile as sf, librosa
sys.argv = ["x"]
os.environ["NOMAIN"] = "1"
exec(open("/home/claude/zara/ncompose.py").read())
SR = 48000
shots = []; t = 0.0
for s in ORDER:
    info = f"{FR}/{s}/info.json"
    n = json.load(open(info))["n"] if os.path.exists(info) else int(round(DUR[s] * 24))
    shots.append((s, t, n / 24)); t += n / 24
TOTAL = t; N = int((TOTAL + 0.5) * SR); ST = {s: (a, d) for s, a, d in shots}
vo = np.zeros(N); sfx = np.zeros(N)
rng = np.random.default_rng(7)
def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR); i0 = max(0, i); e = min(len(buf), i + len(sig))
    if e > i0: buf[i0:e] += g * sig[i0 - i:e - i]
def T(d): return np.arange(int(d * SR)) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
def pop_s(pitch=1.0):
    x = T(0.13); f = (900 * np.exp(-x * 25) + 320) * pitch; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 28) * 0.7
def bubble_pop(pitch=1.0):
    x = T(0.18); f = (300 + 1400 * x / 0.18) * pitch; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 18) * 0.6
def whoosh(d=0.5):
    n = rng.standard_normal(int(d * SR)); n = np.convolve(n, np.ones(30) / 30, "same") * 3; return n * np.sin(np.pi * T(d) / d) ** 2 * 0.6
def impact():
    x = T(1.4); f = 35 + 90 * np.exp(-x * 12); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.5) + rng.standard_normal(len(x)) * np.exp(-x * 9) * 0.4) * 0.9
def chime(base=84, k=4):
    out = np.zeros(int(1.2 * SR))
    for j in range(k):
        s = np.sin(2 * np.pi * note(base + [0, 4, 7, 12, 16, 19][j % 6]) * T(0.8)) * np.exp(-T(0.8) * 5) * 0.25; i = int(j * 0.06 * SR); out[i:i + len(s)] += s
    return out
def bonk():
    x = T(0.35); f = 520 * np.exp(-x * 6); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 10) * 0.8 + np.sin(2 * np.pi * 1400 * x) * np.exp(-x * 40) * 0.3
def siren(d=1.6):
    x = T(d); f = 700 + 250 * np.sin(2 * np.pi * 2.2 * x); return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12 * np.minimum(1, (d - x) / 0.2)
def scratch():
    x = T(0.45); f = 600 * np.abs(np.sin(2 * np.pi * 3 * x)) + 100; return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + rng.standard_normal(len(x)) * 0.15 * np.exp(-x * 4)
def popper():
    n = rng.standard_normal(int(0.4 * SR)) * np.exp(-T(0.4) * 12); cr = np.zeros(int(0.8 * SR))
    for k in range(40):
        i = rng.integers(0, len(cr) - 200); cr[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 30) * 0.4
    out = cr * 0.6; out[:len(n)] += n * 0.8; return out
def rec_scratch_stop(): return scratch()
def heartbeat(): x = T(0.25); return np.sin(2 * np.pi * 55 * x) * np.exp(-x * 14) * 0.9
def tick():
    k = rng.standard_normal(int(0.02 * SR)) * np.exp(-T(0.02) * 300); return np.convolve(k, [1, -0.95], "same") * 0.5
WSFX = {"POP!": lambda: bubble_pop(1.0), "POP POP POP": lambda: popper(), "x10": lambda: chime(79, 3), "BONK!": bonk, "POP": lambda: bubble_pop(1.2),
        "ZERO": impact, "VIBES": lambda: chime(84, 5)}
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.2 * rng.random()), a + it[2], 0.45)
        elif k == "text": add(sfx, WSFX.get(it[1], pop_s)(), a + it[2], 0.8)
        elif k == "confetti": add(sfx, popper(), a + it[1], 0.6)
        elif k == "ring": pass
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.35)
        elif k == "flash": add(sfx, whoosh(0.35), a + it[1] - 0.2, 0.5)
    if s in BUBBLES: add(sfx, bubble_pop(0.9), a + d * BUBBLES[s][1], 0.5)
# rising-pitch clone pops in n08 (dopamine ladder)
a8, d8 = ST["n08"]
for k in range(9): add(sfx, bubble_pop(1.0 + k * 0.12), a8 + (int(d8 * 24 * 0.45) + 3 + k * 3) / 24, 0.8)
add(sfx, pop_s(0.8), ST["n01"][0] + ST["n01"][1] * 0.55, 0.9)
# montage: machine-gun pops accelerating
m0 = ST["n14a"][0]; m1 = ST["n14d"][0] + ST["n14d"][1]; tt = m0; gap = 0.12
while tt < m1:
    add(sfx, bubble_pop(1.0 + 0.8 * (tt - m0) / (m1 - m0) + 0.1 * rng.random()), tt, 0.35); tt += gap; gap = max(0.04, gap * 0.95)
add(sfx, siren(ST["n15"][1]), ST["n15"][0], 0.6)
# inner monologue: heartbeat + tick under n07b
for k in range(int(ST["n07b"][1] / 0.6)): add(sfx, heartbeat(), ST["n07b"][0] + k * 0.6, 0.7); add(sfx, tick(), ST["n07b"][0] + k * 0.6 + 0.3, 0.5)
add(sfx, rec_scratch_stop(), ST["n06"][0] + 0.05, 0.8)
add(sfx, chime(72, 6), ST["n17"][0] + LEAD + VOD["n17"] + 0.5, 0.5); add(sfx, impact(), ST["n17"][0] + LEAD + VOD["n17"] + 0.5, 0.8)
# VO
for s, a, d in shots:
    p = f"/home/claude/zara/hvo/{s}.wav"
    if os.path.exists(p):
        y, _ = sf.read(p); add(vo, y if y.ndim == 1 else y.mean(1), a + LEAD, 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(env * 9, 0, 1)
# music: Numbers instrumental; drop out for n06 (record scratch) and the end beat, then back
mus, _ = librosa.load("/home/claude/zara/beat/numbers.wav", sr=SR, mono=True)
mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
s6 = ST["n06"][0]; ramp(s6, s6 + 0.15, 1, 0.0); gain[int((s6 + 0.15) * SR):int(ST["n08"][0] * SR)] = 0.0
ramp(ST["n08"][0], ST["n08"][0] + 0.3, 0.0, 1.0)
e17 = ST["n17"][0]; ramp(e17, e17 + 0.2, 1, 0.15); gain[int((e17 + 0.2) * SR):int((e17 + LEAD + VOD["n17"] + 0.5) * SR)] = 0.15
ramp(e17 + LEAD + VOD["n17"] + 0.5, e17 + LEAD + VOD["n17"] + 0.6, 0.15, 1.0)
mus = mus * gain * (1 - 0.6 * talk) * 0.42
fade = np.ones(N); fl = int(1.0 * SR); fade[-fl:] = np.linspace(1, 0, fl)
def master(with_music):
    mix = vo * 1.0 + sfx * 0.5 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.15) / 1.15 * fade
    return mix[: int(TOTAL * SR)]
for name, wm in (("hood_mix.wav", True), ("hood_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"/home/claude/zara/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
