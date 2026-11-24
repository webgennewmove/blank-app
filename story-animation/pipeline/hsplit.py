import json, sys, numpy as np, librosa
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
SR = 16000
def split(src, lines, voice):
    gap = np.zeros(int(0.35 * SR)); ref = []; rb = []; t = 0
    for s, txt in lines:
        a, sr = k.create(txt, voice=voice, speed=1.0, lang="en-us")
        a = librosa.resample(np.asarray(a, dtype=np.float32), orig_sr=sr, target_sr=SR); a, _ = librosa.effects.trim(a, top_db=35)
        rb.append(t); ref += [a, gap]; t += len(a) + len(gap)
    ref = np.concatenate(ref); tgt, _ = librosa.load(src, sr=SR)
    def feat(x):
        m = librosa.feature.mfcc(y=x, sr=SR, n_mfcc=20, hop_length=160)[1:]; return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
    D, wp = librosa.sequence.dtw(feat(ref), feat(tgt), metric="cosine"); wp = wp[::-1]
    rms = librosa.feature.rms(y=tgt, frame_length=800, hop_length=160)[0]; db = 20 * np.log10(rms + 1e-9); sil = db < (db.max() - 36)
    segs = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if j - i >= 10: segs.append((i / 100, j / 100))
            i = j
        else: i += 1
    print("pauses:", " ".join(f"{a:.2f}-{b:.2f}" for a, b in segs))
    mids = [((a + b) / 2, b - a) for a, b in segs if a > 0.05 and b < len(tgt) / SR - 0.05]
    bounds = [0.0]
    for i in range(1, len(lines)):
        tb = (rb[i] - len(gap) / 2) / SR; idx = np.searchsorted(wp[:, 0], int(tb * 100)); m = wp[min(idx, len(wp) - 1), 1] / 100
        near = [x for x in mids if abs(x[0] - m) < 0.9 and x[0] > bounds[-1] + 0.25]
        bounds.append(min(near, key=lambda x: abs(x[0] - m) - 0.3 * x[1])[0] if near else m)
    bounds.append(len(tgt) / SR)
    out = {}
    for (s, txt), a, b in zip(lines, bounds, bounds[1:]): out[s] = (a, b); print(s, f"{a:.2f}-{b:.2f} ({b-a:.2f})", txt)
    return out
Z = [("n01", "In my hood, whatever number you say out loud... that's how many of you pull up!"), ("n02", "So nobody round here says numbers. Like, EVER."),
     ("n03", "The corner store don't even have prices!"), ("n04", "Birthday cakes look like this."), ("n05", "And math class? Ms. Johnson just be guessing."),
     ("n06", "Then... she made a mistake."), ("n09", "Ten Milos!"), ("n11", "And not ONE of 'em did the homework."), ("n13", "...Bro."),
     ("n14a", "A million Milos!"), ("n14b", "Every block!"), ("n14c", "Every stoop!"), ("n14d", "Every corner store!"),
     ("n16", "And that's when my baby brother said his first word..."), ("n17", "It was a number.")]
M = [("n07b", "Okay okay okay... just say a number, bro. How bad could it be?"), ("n08", "Uhh... ten?"), ("n12", "Yo! It's like a MILLION of us!")]
cz = split("hel/zara.mp3", Z, "af_heart"); cm = split("hel/milo.mp3", M, "am_puck")
json.dump({"zara": cz, "milo": cm}, open("hel/cuts.json", "w"))
