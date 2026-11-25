"""PIRATES audio: Toby VO (one take) + SFX + TEMPOREX 'Numbers' bed (continuous, ducked) with drops.
Writes pir_mix.wav (with music) and pir_mix_nomusic.wav."""
import os, sys, json, math, subprocess
_src = open("/home/claude/zara/egg_audio.py").read()
_head = _src[:_src.index("WSFX =")]
_head = _head.replace('os.environ["EGG_NOMAIN"] = "1"', 'os.environ["EGG_NOMAIN"] = "1"; os.environ["PIR_NOMAIN"] = "1"')
_head = _head.replace("/home/claude/zara/egg_compose.py", "/home/claude/zara/pirates/pir_compose.py")
exec(_head)
from scipy.signal import butter, lfilter
MUS = "/home/claude/zara/egg/music"
def lp(x, fc): b, a = butter(2, fc / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, fc): b, a = butter(2, fc / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def noise(d): return rng.standard_normal(int(d * SR))
def env(d, a=0.01, r=6.0): x = T(d); return np.minimum(1, x / a) * np.exp(-x * r)
def squawk(d=0.45):
    x = T(d); f = 1400 - 600 * x / d + 180 * np.sin(2 * np.pi * 28 * x)
    s_ = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + bp(noise(d), 900, 3500) * 0.4
    return lp(s_, 4000) * env(d, 0.02, 4) * 0.5
def fwoosh(d=0.9): return (bp(noise(d), 300, 3000) * np.linspace(1, 0.2, int(d * SR)) + lp(noise(d), 200) * 0.8) * env(d, 0.01, 2.5) * 0.9
def clank():
    x = T(0.5); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * k) for f, k in ((820, 9), (1370, 12), (2210, 16), (3100, 20))) * 0.22
def ping():
    x = T(0.5); f = 3200 - 900 * x; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9) * 0.35
def sneeze():
    a = bp(noise(0.25), 600, 2500) * np.linspace(0.2, 1, int(0.25 * SR)) * 0.25
    b = bp(noise(0.3), 1200, 5000) * env(0.3, 0.005, 9) * 0.9
    return np.concatenate([a, b])
def splash_s(d=0.9): return (lp(noise(d), 2500) * 0.8 + hp(noise(d), 3000) * 0.3) * env(d, 0.005, 4.5)
def boom_s(d=2.4):
    x = T(d); sub = np.sin(2 * np.pi * (55 - 20 * x / d) * x) * np.exp(-x * 2.2)
    return (lp(noise(d), 600) * np.exp(-x * 2.6) * 1.4 + sub * 0.9 + hp(noise(d), 2000) * np.exp(-x * 9) * 0.4)
def motor(d, f0=70, a=0.3):
    x = T(d); f = f0 + 6 * np.sin(2 * np.pi * 3 * x); s_ = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return lp(s_ + 0.3 * noise(d), 900) * a
def wind(d): return bp(noise(d), 300, 1800) * np.sin(np.pi * T(d) / d) ** 1.5 * 0.6
def chirp():
    out = np.zeros(int(0.5 * SR))
    for k in range(3):
        x = T(0.1); f = 3000 + 2500 * x / 0.1; c_ = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.1) * 0.3; i = int(k * 0.13 * SR); out[i:i + len(c_)] += c_
    return out
def gulp(): x = T(0.18); return np.sin(2 * np.pi * (300 - 900 * x) * x) * np.sin(np.pi * x / 0.18) * 0.6
def munch(d):
    out = np.zeros(int(d * SR)); t_ = 0.0
    while t_ < d - 0.1: c_ = lp(noise(0.06), 1500) * env(0.06, 0.003, 30) * 0.5; i = int(t_ * SR); out[i:i + len(c_)] += c_[: len(out) - i]; t_ += 0.16 + 0.05 * rng.random()
    return out
def cock(): return hp(noise(0.05), 2000) * env(0.05, 0.002, 60) * 0.6 + hp(noise(0.05), 1500) * 0.0
def dinner_bell(): x = T(1.2); return sum(np.sin(2 * np.pi * f * x) for f in (1180, 2950, 4100)) * np.exp(-x * 3) * 0.12
def groan(d=1.8): x = T(d); return lp(np.sign(np.sin(2 * np.pi * (45 + 10 * np.sin(2 * np.pi * 0.7 * x)) * x)) * 0.4 + noise(d) * 0.2, 400) * np.sin(np.pi * x / d)
def scrape(d=0.8): return bp(noise(d), 800, 4000) * np.linspace(1, 0, int(d * SR)) * 0.5
A = {s: (a, d) for s, a, d in shots}
def at(s, t=0.0): return A[s][0] + t
# VO
y, sr = sf.read("/home/claude/zara/pirates/voice/toby.wav"); y = y if y.ndim == 1 else y.mean(1)
if sr != SR: y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
add(vo, y, 0.0, 1.0)
envv = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(envv * 9, 0, 1)
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.25 * rng.random()), a + it[2], 0.3)
        elif k == "text": add(sfx, bubble(), a + it[2], 0.3)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.25)
    add(sfx, whoosh(0.22), a - 0.1, 0.14)
# sea ambience under every sea shot + gulls
amb = lp(noise(TOTAL + 0.5), 500) * 0.08; add(sfx, amb, 0.0, 1.0)
add(sfx, squawk(), at("p01", 0.3), 0.6); add(sfx, squawk(0.6), at("p04", 0.3), 0.8); add(sfx, gulp(), at("p05", A["p05"][1] * 0.55), 0.7)
for k in range(6): add(sfx, cock(), at("p02", 0.25 + k * 0.08), 0.5)
add(sfx, gulp(), at("p06", 0.4), 0.5); add(sfx, squawk(0.5), at("p07", 0.45), 0.7)
add(sfx, motor(A["p08"][1] + 0.2, 75, 0.35), at("p08"), 0.8)
add(sfx, fwoosh(), at("p09", A["p09"][1] * 0.45), 1.0); add(sfx, riser(1.2) * 0.3 if callable(globals().get("riser")) else np.zeros(1), at("p10"), 0.4)
add(sfx, ping() * 0.5, at("p11", A["p11"][1] * 0.6), 0.6)
add(sfx, clank(), at("p12", 0.0), 0.9); add(sfx, clank(), at("p12", 0.3), 0.9)
for k in range(10): add(sfx, cock(), at("p16", 0.6 + k * 0.09), 0.5)
add(sfx, scratch(), at("p18", wt("p18", "zero")), 0.5) if callable(globals().get("scratch")) else None
for s_ in ("p19", "p24"): add(sfx, sneeze(), at(s_, wt(s_, "sneezed") - 0.05), 0.9); add(sfx, ping(), at(s_, wt(s_, "sneezed") + 0.25), 0.4)
add(sfx, sneeze(), at("p28", 0.0), 0.9); add(sfx, ping(), at("p28", 0.5), 0.6)
add(sfx, ping(), at("p20", 0.33), 0.7); add(sfx, ping(), at("p25", A["p25"][1] * 0.4), 0.7)
add(sfx, whoosh(0.6), at("p20", 0.4), 0.4); add(sfx, thud(), at("p20", A["p20"][1] * 0.72), 0.3)
for k in range(6): add(sfx, splash_s(), at("p23", 0.55 + k * 0.08), 0.6)
add(sfx, dinner_bell(), at("p26", wt("p26", "lunch") - 0.1), 0.9); add(sfx, munch(A["p27"][1]), at("p27"), 0.6)
add(sfx, squawk(0.4), at("p30", A["p30"][1] * 0.6), 0.6); add(sfx, wind(1.4), at("p31", 0.0), 0.8)
add(sfx, motor(A["p32"][1] + 0.1, 80, 0.4), at("p32"), 0.8); add(sfx, motor(A["p33"][1] + 0.1, 95, 0.35), at("p33"), 0.8)
for k in range(3): add(sfx, splash_s(0.6), at("p34", 0.2 + k * 0.7), 0.5)
add(sfx, chirp(), at("p35", 0.6), 0.6); add(sfx, chirp(), at("p36", 0.1), 0.6); add(sfx, splash_s(), at("p35", 0.05), 0.5)
for k in range(int(A["p37"][1] / 0.55)): add(sfx, heartbeat(), at("p37", 0.1 + k * 0.55), 0.7)
add(sfx, fwoosh(1.0), at("p38", A["p38"][1] * 0.35), 1.0)
add(sfx, boom_s(), at("p39", 0.15), 1.5)
add(sfx, groan(1.9), at("p41", 0.1), 0.9)
for k in range(8): add(sfx, splash_s(1.0), at("p42", 0.15 + k * 0.11), 0.6)
add(sfx, splash_s(1.6) * 1.2, at("p43", 0.0), 0.8); add(sfx, scrape(), at("p44", A["p44"][1] * 0.45), 0.8); add(sfx, thud(), at("p44", A["p44"][1] * 0.55), 0.8)
add(sfx, chime(84, 4), at("p45", 0.1), 0.35); add(sfx, pop_s(0.8), at("p46", wt("p46", "me.") + 0.08), 0.5)
for k in range(10): add(sfx, cock() * 0.7, at("p49", 0.15 + k * 0.03), 0.5)
add(sfx, wind(1.2), at("p50", 0.3), 0.7); add(sfx, squawk(), at("p51", 0.6), 0.7)
# music: Numbers bed, continuous, ducked under VO; drops: silence on KA-BOOM, breathe on "captain now"
mp = f"{MUS}/numbers.wav"
mus, _ = sf.read(mp); mus = mus if mus.ndim == 1 else mus.mean(1); mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
def hold_(t0, t1, g): gain[int(t0 * SR):int(t1 * SR)] = g
ramp(0, 0.2, 0.6, 1.0)
d1 = at("p37"); ramp(d1, d1 + 0.4, 1, 0.35); hold_(d1 + 0.4, at("p39", 0.15), 0.35); hold_(at("p39", 0.15), at("p40", 0.5), 0.0); ramp(at("p40", 0.5), at("p41"), 0, 1.1)
d2 = at("p47"); ramp(d2, d2 + 0.2, 1, 0.15); hold_(d2 + 0.2, at("p48"), 0.15); ramp(at("p48"), at("p48", 0.2), 0.15, 1.0)
mus = mus * gain * (1 - 0.55 * talk) * 0.34
def master(with_music):
    mix = vo * 1.1 + sfx * 0.55 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.15) / 1.15
    return mix[: int(TOTAL * SR)]
for name, wm in (("pir_mix.wav", True), ("pir_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"{E}/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
