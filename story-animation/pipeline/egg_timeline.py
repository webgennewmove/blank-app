"""Cut the single ElevenLabs take into per-shot lines and write egg/timeline.json (durations + word timings)."""
import json, numpy as np, soundfile as sf
E = "/home/claude/zara/egg"
y, sr = sf.read(f"{E}/vo_full.wav")
words = [w for w in json.load(open(f"{E}/words.json")) if w[1] < 50.45]
# shot, clip start, clip end, lead-in, tail hold
SHOTS = [("e01", 0.00, 3.55, 0.05, 0.20), ("e02", 3.70, 5.52, 0.05, 0.20), ("e03", 5.60, 7.85, 0.05, 0.10),
         ("e04", 7.90, 10.30, 0.05, 0.25), ("e05", 10.45, 13.55, 0.05, 0.45), ("e06a", 13.85, 15.88, 0.10, 0.25),
         ("e06b", 16.25, 19.40, 0.05, 0.85), ("e07", 19.80, 21.30, 0.35, 0.55), ("e08", 21.60, 25.50, 0.05, 0.30),
         ("e09", 25.75, 30.40, 0.10, 0.65), ("e10", 30.60, 33.58, 0.10, 0.15), ("e11", 33.75, 34.58, 0.00, 0.35),
         ("e12a", 34.70, 36.30, 0.00, 0.10), ("e12b", 36.40, 38.22, 0.00, 0.10), ("e12c", 38.30, 40.70, 0.00, 0.35),
         ("e13", 40.82, 45.25, 0.10, 0.70), ("e14", 45.40, 47.24, 0.35, 0.90), ("e15", 47.45, 50.75, 0.60, 4.80)]
out = {"shots": [], "dur": {}, "lead": {}, "vo": {}, "words": {}}
import os; os.makedirs(f"{E}/vo", exist_ok=True)
for s, a, b, lead, tail in SHOTS:
    clip = y[int(a * sr):int(b * sr)].copy()
    fade = int(0.012 * sr); clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
    sf.write(f"{E}/vo/{s}.wav", clip, sr)
    out["shots"].append(s); out["dur"][s] = round(lead + (b - a) + tail, 3); out["lead"][s] = lead; out["vo"][s] = round(b - a, 3)
    out["words"][s] = [(w.strip(), round(t0 - a + lead, 3), round(t1 - a + lead, 3)) for w, t0, t1 in words if a - 0.05 <= t0 < b]
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.2fs" % sum(out["dur"].values()))
for s in out["shots"]: print(s, out["dur"][s], " ".join(w for w, _, _ in out["words"][s]))
