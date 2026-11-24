"""ON MY BLOCK Ep1 audio: Dre VO + TEMPOREX 'Numbers' bed (ducked, comedic drop-outs) + SFX synced to the FX.
Writes block_mix.wav (with music) and block_mix_nomusic.wav."""
import os, sys, json, math, subprocess
_src = open("/home/claude/zara/egg_audio.py").read()
_head = _src[:_src.index("WSFX =")]
_head = _head.replace('os.environ["EGG_NOMAIN"] = "1"', 'os.environ["EGG_NOMAIN"] = "1"; os.environ["BLOCK_NOMAIN"] = "1"')
_head = _head.replace("/home/claude/zara/egg_compose.py", "/home/claude/zara/block_compose.py")
exec(_head)          # synth helpers + shot table from the block compositor
MUS = "/home/claude/zara/egg/music"

def wind(d):
    n = rng.standard_normal(int(d * SR)); n = np.convolve(n, np.ones(220) / 220, "same") * 9
    x = T(d); return n * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * x)) * np.minimum(1, x / 0.3) * np.minimum(1, (d - x) / 0.3) * 0.5
def cash(): return chime(91, 3) + np.pad(pop_s(1.6), (0, int(1.3 * SR) - int(0.13 * SR)))[: int(1.3 * SR)] * 0.6

WSFX = {"MOTION": lambda: chime(84, 5), "EXCEPT ME.": scratch, "WHIP": lambda: chime(88, 4), "HE'S 12": thud, "BONK!": lambda: impact(0.9),
        "STORE #2": pop_s, "INSIDE?!": lambda: impact(0.8), "HE'S ONE": cash, "LIBRARY CARD": thud, "TODAY": lambda: impact(0.8),
        "TO MYSELF": thud, "JORDANS": lambda: chime(86, 3), "CROCS": scratch, "MOVE.": lambda: impact(2.0), "OHIO?!": lambda: impact(1.2),
        "I DON'T KNOW!!!": lambda: impact(1.4), "EVERYBODY": pop_s, "SO HEAVY": thud, "UNCLE RAY": pop_s, "KEPT MOVING": whoosh}
for s, a, d in shots:
    fx = build_fx(s, d)
    for it in fx.items:
        k = it[0]
        if k == "emoji": add(sfx, pop_s(1.0 + 0.25 * rng.random()), a + it[2], 0.45)
        elif k == "text": add(sfx, WSFX.get(it[1], bubble)(), a + it[2], 0.85)
        elif k == "confetti": add(sfx, popper(), a + it[1], 0.6)
        elif k == "punch": add(sfx, whoosh(0.25), a + it[1] - 0.1, 0.35)
        elif k == "flash": add(sfx, whoosh(0.35), a + it[1] - 0.2, 0.45)
    add(sfx, whoosh(0.3), a - 0.12, 0.25)
# set pieces
a5, d5 = ST["b05"]; ti = wt("b05", "inside"); add(sfx, riser(d5 - ti), a5 + ti, 0.55)
a6, d6 = ST["b06"]; tt = a6; gap = 0.22
while tt < a6 + d6: add(sfx, bubble(1.2 + 0.8 * (tt - a6) / d6), tt, 0.2); tt += gap; gap = max(0.07, gap * 0.92)
a7, d7 = ST["b07"]; add(sfx, wind(d7), a7, 0.7)
a8, d8 = ST["b08"]; add(sfx, riser(wt("b08", "today,")), a8, 0.4)
a13, d13 = ST["b13"]
for k in range(6): add(sfx, whoosh(0.3), a13 + k * d13 / 6, 0.45)
a14, d14 = ST["b14"]
for k in range(4): add(sfx, whoosh(0.3), a14 + k * d14 / 4, 0.4)
a15, d15 = ST["b15"]; tt = a15; gap = 0.18
while tt < a15 + d15: add(sfx, bubble(0.8 + 1.2 * (tt - a15) / d15), tt, 0.22); tt += gap; gap = max(0.06, gap * 0.93)
a16, d16 = ST["b16"]
for k in (2, int(d16 * 24 * 0.4), int(d16 * 24 * 0.75)): add(sfx, whoosh(0.4), a16 + k / 24, 0.7)
a17, d17 = ST["b17"]; add(sfx, chime(72, 6), a17 + vo_end("b17") + 0.35, 0.55)
# VO
for s, a, d in shots:
    y, sr = sf.read(f"{E}/vo/{s}.wav"); y = y if y.ndim == 1 else y.mean(1)
    if sr != SR: y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
    add(vo, y, a + LEADS[s], 1.0)
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); talk = np.clip(env * 9, 0, 1)
# music: TEMPOREX - Numbers. Drops on the jokes: "except me" (scratch), the library card (until TODAY), and the beat before MOVE.
mp = f"{MUS}/numbers.wav"
if not os.path.exists(mp): subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{MUS}/numbers_loop.mp3", "-ac", "1", "-ar", str(SR), mp], check=True)
mus, _ = sf.read(mp); mus = np.tile(mus, int(np.ceil(N / len(mus))) + 1)[:N]
gain = np.ones(N)
def ramp(t0, t1, g0, g1):
    i0, i1 = int(t0 * SR), int(t1 * SR); gain[i0:i1] = np.linspace(g0, g1, max(1, i1 - i0))
def hold(t0, t1, g): gain[int(t0 * SR):int(t1 * SR)] = g
b2 = ST["b02"][0]; ramp(b2, b2 + 0.1, 1, 0); hold(b2 + 0.1, ST["b03"][0], 0); ramp(ST["b03"][0], ST["b03"][0] + 0.1, 0, 1)
td = ST["b08"][0] + wt("b08", "today,"); ramp(a7, a7 + 0.15, 1, 0); hold(a7 + 0.15, td, 0); ramp(td, td + 0.08, 0, 1.15)
b11 = ST["b11b"][0]; ts = b11 + wt("b11b", "you"); tm = b11 + wt("b11b", "move."); ramp(ts - 0.2, ts, 1, 0); hold(ts, tm, 0); ramp(tm, tm + 0.05, 0, 1.15)
mus = mus * gain * (1 - 0.62 * talk) * 0.4
fade = np.ones(N); fl = int(0.8 * SR); fade[-fl:] = np.linspace(1, 0, fl)
def master(with_music):
    mix = vo * 1.05 + sfx * 0.5 * (1 - 0.35 * talk) + (mus if with_music else 0)
    mix = np.tanh(mix * 1.2) / 1.2 * fade
    return mix[: int(TOTAL * SR)]
for name, wm in (("block_mix.wav", True), ("block_mix_nomusic.wav", False)):
    m = master(wm); sf.write(f"{E}/{name}", np.stack([m, m], 1).astype(np.float32), SR)
print("audio", round(TOTAL, 2))
