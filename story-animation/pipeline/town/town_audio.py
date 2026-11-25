"""IN MY TOWN 'The Game' audio: dialogue (Rico/Maya/Leo + processed game voice), cinematic SFX, TEMPOREX 'Numbers' bed with drops.
Writes town_mix.wav (with music) and town_mix_nomusic.wav."""
import os, sys, json, math, subprocess
_src = open("/home/claude/zara/egg_audio.py").read()
_head = _src[:_src.index("WSFX =")]
_head = _head.replace('os.environ["EGG_NOMAIN"] = "1"', 'os.environ["EGG_NOMAIN"] = "1"; os.environ["TOWN_NOMAIN"] = "1"')
_head = _head.replace("/home/claude/zara/egg_compose.py", "/home/claude/zara/town/town_compose.py")
exec(_head)
import librosa
from scipy.signal import fftconvolve, butter, lfilter
MUS = "/home/claude/zara/egg/music"

def lp(x, fc):
    b, a = butter(2, fc / (SR / 2), "low"); return lfilter(b, a, x)
def hp(x, fc):
    b, a = butter(2, fc / (SR / 2), "high"); return lfilter(b, a, x)
def noise(d): return rng.standard_normal(int(d * SR))
def reverb(x, d=1.6, mix=0.35):
    ir = noise(d) * np.exp(-T(d) * 4.0); ir = lp(ir, 5000); ir /= np.abs(ir).sum() ** 0.5 * 10
    w = fftconvolve(x, ir)[: len(x) + int(d * SR * 0.5)]; out = np.zeros(len(w)); out[: len(x)] += x * (1 - mix); return out + w * mix * 6
def dice_rattle(d=0.6, k=7):
    out = np.zeros(int(d * SR))
    for j in range(k):
        i = int((j / k) ** 1.3 * (d - 0.05) * SR); c = hp(noise(0.03), 1800) * np.exp(-T(0.03) * 120) * (0.9 - j * 0.08)
        out[i:i + len(c)] += c
    return out * 0.7
def shatter(d=1.6):
    out = hp(noise(d), 2500) * np.exp(-T(d) * 3.5) * 0.6
    for j in range(60):
        f_ = rng.uniform(2500, 7000); c = np.sin(2 * np.pi * f_ * T(0.25)) * np.exp(-T(0.25) * rng.uniform(12, 30)) * 0.12
        i = int(rng.uniform(0, d * 0.8) * SR); out[i:i + len(c)] += c[: len(out) - i]
    im = impact(0.8); out[: len(im)] += im[: len(out)] * 0.5
    return out
def roar(d=1.6, low=55):
    x = T(d); f = low + 25 * np.sin(2 * np.pi * 7 * x) + 20 * (1 - x / d)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    g = lp(saw * 0.5 + lp(noise(d), 900) * 1.2, 1400) * np.minimum(1, x / 0.08) * np.exp(-x * 1.2)
    return g * 0.9
def mew(): x = T(0.35); f = 700 + 500 * np.sin(np.pi * x / 0.35); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.35) * 0.25
def creak(d=1.2):
    x = T(d); f = 90 + 40 * np.sin(2 * np.pi * 0.7 * x) + rng.uniform(-10, 10)
    s_ = 2 * ((np.cumsum(f) / SR) % 1) - 1; return lp(s_ * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * x)), 900) * np.sin(np.pi * x / d) * 0.35
def crickets(d):
    out = np.zeros(int(d * SR))
    for j in range(int(d * 9)):
        i = int(rng.uniform(0, d - 0.2) * SR); c = np.sin(2 * np.pi * rng.uniform(4200, 5200) * T(0.12)) * (np.sin(2 * np.pi * 45 * T(0.12)) > 0) * np.exp(-T(0.12) * 10) * 0.05
        out[i:i + len(c)] += c
    return out
def phone_beep(): return np.sin(2 * np.pi * 1600 * T(0.12)) * np.exp(-T(0.12) * 20) * 0.3

# dialogue: game voice gets pitched down + cathedral reverb
for s, a, d in shots:
    src = TL["src"].get(s)
    if not src: continue
    y, sr = sf.read(f"{E}/vo/{s}.wav"); y = y if y.ndim == 1 else y.mean(1)
    if sr != SR: y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
    if src == "game":
        y = librosa.effects.pitch_shift(y.astype(np.float32), sr=SR, n_steps=-4); y = reverb(y, 2.2, 0.45) * 1.1
        add(sfx, lp(noise(len(y) / SR), 120) * 0.25, a + LEADS[s], 1.0)
    add(vo, y, a + LEADS[s], 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(env * 9, 0, 1)
# FX-driven hits
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.25 * rng.random()), a + it[2], 0.3)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.3)
    add(sfx, whoosh(0.3), a - 0.12, 0.2)
A = {s: (a, d) for s, a, d in shots}
def at(s, t=0.0): return A[s][0] + t
add(sfx, dice_rattle(1.2, 9), at("s01", 0.4), 0.6); add(sfx, chime(84, 6), at("s01", 0.2), 0.25)
add(sfx, creak(0.8), at("s02", 0.6), 0.6); add(sfx, chime(79, 4), at("s03", 0.5), 0.45); add(sfx, riser(0.9), at("s03"), 0.3)
add(sfx, dice_rattle(0.8, 8), at("s05", wt("s05", "rolled.")), 0.7)
add(sfx, dice_rattle(1.3, 8), at("s05b"), 0.7); add(sfx, impact(1.0), at("s05b", A["s05b"][1] * 0.72), 0.7); add(sfx, chime(72, 6), at("s05b", A["s05b"][1] * 0.72), 0.4)
add(sfx, shatter(2.0), at("s06", 0.15), 1.0)
add(sfx, impact(1.4), at("s07", 2.95), 1.0); add(sfx, roar(1.2, 60), at("s08", 0.2), 0.9); add(sfx, impact(0.8), at("s08", 0.1), 0.7)
add(sfx, roar(0.8, 70), at("s09", 0.8), 0.5); add(sfx, whoosh(0.4), at("s09", 1.6), 0.5)
add(sfx, phone_beep(), at("s10", 0.05), 0.8); add(sfx, roar(0.7, 65), at("s10", 0.9), 0.4)
add(sfx, riser(A["s11"][1]), at("s11"), 0.35)
for k in range(6): add(sfx, chime(84 + k, 1), at("s11", wt("s11", "six") + k * 0.125), 0.35)
for k in range(int(A["s13"][1] / 0.6)): add(sfx, heartbeat(), at("s13", k * 0.6), 0.6)
add(sfx, dice_rattle(1.0, 8), at("s14", wt("s14", "rolled!")), 0.7); add(sfx, impact(1.2), at("s14", wt("s14", "dice!")), 0.6)
sp = A["s15"][1] * 0.58; add(sfx, riser(sp), at("s15"), 0.7); add(sfx, impact(1.6), at("s15", sp), 0.9)
add(sfx, crickets(A["s16"][1] + A["s17"][1] + A["s18"][1] + A["s19"][1]), at("s16"), 0.9)
tr = A["s17"][1] * 0.3; add(sfx, mew(), at("s17", tr - 0.45), 0.8); add(sfx, roar(2.2, 45), at("s17", tr), 1.1); add(sfx, impact(1.4), at("s17", tr), 0.6)
for k in range(10): add(sfx, creak(1.3), at("s18", wt("s18", "final") + k * 4 / 24), 0.35)
add(sfx, dice_rattle(1.0, 8), at("s19", 0.3), 0.6)
# music bed with drops
mp = f"{MUS}/numbers.wav"
if not os.path.exists(mp): subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{MUS}/numbers_loop.mp3", "-ac", "1", "-ar", str(SR), mp], check=True)
mus, _ = sf.read(mp); mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
def hold(t0, t1, g): gain[int(t0 * SR):int(t1 * SR)] = g
ramp(0, 0.4, 0.4, 1.0)
s6 = at("s06", 0.1); ramp(s6, s6 + 0.1, 1, 0); hold(s6 + 0.1, at("s07", 2.95), 0); ramp(at("s07", 2.95), at("s07", 3.0), 0, 1.1)
s13 = at("s13"); ramp(s13, s13 + 0.2, 1, 0.15); hold(s13 + 0.2, at("s14", wt("s14", "dice!")), 0.15); ramp(at("s14", wt("s14", "dice!")), at("s14", wt("s14", "dice!")) + 0.05, 0.15, 1.15)
s17 = at("s17"); ramp(s17, s17 + 0.3, 1, 0.0); hold(s17 + 0.3, at("s17", tr), 0); ramp(at("s17", tr), at("s17", tr) + 0.05, 0, 1.1)
mus = mus * gain * (1 - 0.6 * talk) * 0.38
def master(with_music):
    mix = vo * 1.1 + sfx * 0.55 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.15) / 1.15
    return mix[: int(TOTAL * SR)]
for name, wm in (("town_mix.wav", True), ("town_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"{E}/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
