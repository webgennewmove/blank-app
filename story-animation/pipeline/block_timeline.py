"""Cut Dre's single take into per-shot lines and write block/timeline.json (durations + word timings)."""
import json, os, numpy as np, soundfile as sf
E = "/home/claude/zara/block"
y, sr = sf.read(f"{E}/vo_full.wav")
words = json.load(open(f"{E}/words.json"))
# shot, clip start, clip end, lead-in, tail hold
SHOTS = [("b01", 0.00, 2.55, 0.25, 0.05), ("b02", 2.62, 3.85, 0.00, 0.35), ("b03", 4.15, 7.15, 0.05, 0.15),
         ("b04", 7.30, 11.55, 0.05, 0.25), ("b05", 11.62, 16.45, 0.05, 0.15), ("b06", 16.52, 19.45, 0.05, 0.30),
         ("b07", 20.30, 23.30, 0.10, 0.20), ("b08", 23.45, 27.30, 0.05, 0.10), ("b09", 27.35, 31.15, 0.05, 0.35),
         ("b10", 31.25, 35.95, 0.05, 0.20), ("b11a", 36.02, 38.10, 0.05, 0.05), ("b11b", 38.12, 42.75, 0.05, 0.30),
         ("b12", 43.10, 45.62, 0.05, 0.05), ("b13", 45.66, 47.78, 0.00, 0.05), ("b14", 47.78, 49.45, 0.00, 0.10),
         ("b15", 49.47, 52.55, 0.05, 0.10), ("b16", 52.57, 54.88, 0.05, 0.00), ("b17", 54.88, 56.24, 0.00, 3.80)]
out = {"shots": [], "dur": {}, "lead": {}, "vo": {}, "words": {}}
os.makedirs(f"{E}/vo", exist_ok=True)
for s, a, b, lead, tail in SHOTS:
    clip = y[int(a * sr):int(b * sr)].copy()
    fade = int(0.012 * sr); clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
    sf.write(f"{E}/vo/{s}.wav", clip, sr)
    out["shots"].append(s); out["dur"][s] = round(lead + (b - a) + tail, 3); out["lead"][s] = lead; out["vo"][s] = round(b - a, 3)
    out["words"][s] = [(w.strip(), round(t0 - a + lead, 3), round(t1 - a + lead, 3)) for w, t0, t1 in words if a - 0.05 <= t0 < b - 0.05]
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.2fs" % sum(out["dur"].values()))
for s in out["shots"]: print(s, out["dur"][s], " ".join(w for w, _, _ in out["words"][s]))
