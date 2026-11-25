"""IN MY TOWN 'Glows' audio: Rico VO (one continuous take) + SFX + TEMPOREX 'Numbers' bed with drops.
Writes glow_mix.wav (with music) and glow_mix_nomusic.wav."""
import os, sys, json, math, subprocess
_src = open("/home/claude/zara/egg_audio.py").read()
_head = _src[:_src.index("WSFX =")]
_head = _head.replace('os.environ["EGG_NOMAIN"] = "1"', 'os.environ["EGG_NOMAIN"] = "1"; os.environ["GLOW_NOMAIN"] = "1"')
_head = _head.replace("/home/claude/zara/egg_compose.py", "/home/claude/zara/town/glow_compose.py")
exec(_head)
from scipy.signal import butter, lfilter
MUS = "/home/claude/zara/egg/music"
def lp(x, fc): b, a = butter(2, fc / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, fc): b, a = butter(2, fc / (SR / 2), "high"); return lfilter(b, a, x)
def noise(d): return rng.standard_normal(int(d * SR))
def fwoom(d=0.7):
    x = T(d); f = 60 + 500 * (x / d); return (lp(noise(d), 1500) * 1.4 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5) * np.sin(np.pi * x / d) ** 1.5 * 0.8
def jingle(n=3):
    out = np.zeros(int(0.7 * SR))
    for k in range(n):
        for h in (2200, 3300, 4400):
            s_ = np.sin(2 * np.pi * (h + rng.uniform(-60, 60)) * T(0.4)) * np.exp(-T(0.4) * 12) * 0.12; i = int(k * 0.09 * SR); out[i:i + len(s_)] += s_
    return out
def buzz(d, f0=110):
    x = T(d); f = f0 + 8 * np.sin(2 * np.pi * 9 * x); s_ = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return lp(s_ * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * x)), 1800) * 0.25
def zipper(d=0.45):
    out = np.zeros(int(d * SR)); k = 0; tt = 0.0
    while tt < d - 0.01:
        i = int(tt * SR); c = hp(noise(0.006), 2500) * 0.5; out[i:i + len(c)] += c[: len(out) - i]; tt += 0.009 + 0.004 * rng.random()
    return out * np.linspace(0.6, 1.0, len(out))
def click(): return hp(noise(0.02), 3000) * np.exp(-T(0.02) * 300) * 0.9
def chomp(): return (lp(noise(0.12), 900) * np.exp(-T(0.12) * 30) * 1.2)
def rip(d=0.4): return hp(noise(d), 1200) * np.exp(-T(d) * 5) * (0.6 + 0.4 * np.sin(2 * np.pi * 45 * T(d))) * 0.6
def gasp(d=0.8): return lp(noise(d), 2500) * np.sin(np.pi * T(d) / d) ** 2 * 0.35
def snore(d):
    x = T(d); return lp(noise(d), 400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * x)) ** 2 * 0.4
def beep(f=880, d=0.12): return np.sin(2 * np.pi * f * T(d)) * np.exp(-T(d) * 8) * 0.25
A = {s: (a, d) for s, a, d in shots}
def at(s, t=0.0): return A[s][0] + t
# VO: one continuous take, placed at 0 (shots are cut on its word times)
y, sr = sf.read("/home/claude/zara/town/glow/voice/rico.wav"); y = y if y.ndim == 1 else y.mean(1)
if sr != SR: y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
add(vo, y, 0.0, 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(env * 9, 0, 1)
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.25 * rng.random()), a + it[2], 0.35)
        elif k == "text": add(sfx, bubble(), a + it[2], 0.4)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.3)
    add(sfx, whoosh(0.28), a - 0.12, 0.18)
for i in range(3): add(sfx, fwoom(0.45), at("s01", (1 + i * 7) / 24 - 0.05), 0.55)
add(sfx, thud(), at("s04", A["s04"][1] * 0.62), 0.6); add(sfx, buzz(0.6, 180), at("s04", 0.1), 0.25)
for k in range(4): add(sfx, beep(1200 - k * 100, 0.08), at("s05", wt("s05", "four") + k * 0.25), 0.25)
add(sfx, thud(), at("s08", A["s08"][1] * 0.55), 0.8)
a9, d9 = A["s09"]; tt = a9
while tt < a9 + d9: add(sfx, pop_s(1.6 + 0.4 * rng.random()), tt, 0.12); tt += 0.125
add(sfx, snore(A["s10"][1]), at("s10"), 0.6)
add(sfx, sparkle_s(A["s11"][1]), at("s11"), 0.5)
add(sfx, jingle(2), at("s14", A["s14"][1] * 0.5 + 0.3), 0.8)
add(sfx, jingle(2), at("s17", wt("s17", "jingle")), 0.9); add(sfx, jingle(2), at("s17", wt("s17", "jingle", 1)), 0.9)
add(sfx, slam(), at("s20", A["s20"][1] * 0.45), 0.5)
add(sfx, click(), at("s22", 3 / 24), 0.8)
for w_ in ("three", "two", "one"): add(sfx, beep(660 if w_ != "one" else 990, 0.18), at("s24", wt("s24", w_)), 0.4)
add(sfx, zipper(0.5), at("s25", A["s25"][1] * 0.35), 0.8)
add(sfx, fwoom(1.0), at("s26", -0.1), 1.0); add(sfx, gasp(1.0), at("s26", 0.1), 0.8); add(sfx, chime(84, 6), at("s26", 0.05), 0.35)
mb0 = at("s27"); mb1 = at("s44")
add(sfx, buzz(mb1 - mb0, 105) * np.minimum(1, np.linspace(0, 6, int((mb1 - mb0) * SR))), mb0, 0.55)
add(sfx, buzz(A["s45"][1] + A["s46"][1], 125), at("s45"), 0.6)
add(sfx, chime(91, 3), at("s29", A["s29"][1] * 0.35), 0.4)
add(sfx, chomp(), at("s30", A["s30"][1] * 0.42), 0.9); add(sfx, rip(0.5), at("s31", A["s31"][1] * 0.45), 0.8)
add(sfx, jingle(2), at("s38", wt("s38", "jingle")), 0.8); add(sfx, jingle(2), at("s38", wt("s38", "jingle", 1)), 0.8)
for k in range(3): add(sfx, jingle(1), at("s39", 0.3 + k * 0.6), 0.5)
add(sfx, zipper(0.45), at("s41", 0.05), 1.0); add(sfx, click(), at("s42", 0.2), 1.0)
add(sfx, whoosh(0.4), at("s44", A["s44"][1] * 0.35), 0.5)
for k in range(3): add(sfx, jingle(1), at("s48", 0.1 + k * 0.33), 0.5)
add(sfx, sparkle_s(A["s51"][1]), at("s51"), 0.6); add(sfx, chime(84, 5), at("s51", wt("s51", "top")), 0.45); add(sfx, slam(), at("s51", wt("s51", "top")), 0.5)
add(sfx, slam(), at("s53", wt("s53", "concert.")), 0.7); add(sfx, chime(88, 6), at("s53", wt("s53", "concert.")), 0.4); add(sfx, slam(), at("s40", 0.42), 0.6)
add(sfx, buzz(A["s52"][1] + A["s53"][1], 95) * 0.5, at("s52"), 0.4)
# music bed with drops
mp = f"{MUS}/numbers.wav"
mus, _ = sf.read(mp); mus = mus if mus.ndim == 1 else mus.mean(1); mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
def hold_(t0, t1, g): gain[int(t0 * SR):int(t1 * SR)] = g
ramp(0, 0.3, 0.5, 1.0)
d1 = at("s12"); ramp(d1, d1 + 0.08, 1, 0); hold_(d1 + 0.08, at("s13", 0.05), 0); ramp(at("s13", 0.05), at("s13", 0.1), 0, 1.05)
d2 = at("s23"); ramp(d2, d2 + 0.3, 1, 0.5); hold_(d2 + 0.3, at("s26"), 0.5); ramp(at("s26"), at("s26", 0.05), 0.5, 1.2)
d3 = at("s37"); ramp(d3, d3 + 0.1, 1, 0); hold_(d3 + 0.1, at("s38"), 0.0); ramp(at("s38"), at("s38", 0.3), 0.0, 0.3); hold_(at("s38", 0.3), at("s42", 0.2), 0.3); ramp(at("s42", 0.2), at("s42", 0.25), 0.3, 1.15)
d4 = at("s52"); ramp(d4, d4 + 0.4, 1, 0.45)
mus = mus * gain * (1 - 0.6 * talk) * 0.36
def master(with_music):
    mix = vo * 1.1 + sfx * 0.55 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.15) / 1.15
    return mix[: int(TOTAL * SR)]
for name, wm in (("glow_mix.wav", True), ("glow_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"{E}/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
