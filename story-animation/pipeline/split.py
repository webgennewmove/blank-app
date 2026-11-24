import json, numpy as np, librosa, soundfile as sf, subprocess
from kokoro_onnx import Kokoro
Z = [("s01","In my town, every kid gets a superpower on their tenth birthday!"),("s02","My best friend Milo got super jumping."),
("s03","My big sister Ivy can float."),("s04","Even Grandma got super speed!"),("s05","And today... is MY tenth birthday!"),
("s06","I ran outside to see what I could do."),("s07","I tried jumping..."),("s08","I tried floating..."),("s09","Nothing happened."),
("s10","Everyone started laughing."),("s12","I walked home, feeling so small."),("s13","Then I saw a little puppy, stuck in the road."),
("s14","And a truck was coming!"),("s15","I shouted... STOP!"),("s16","And everything froze."),("s17","The truck. The birds. Even the clouds."),
("s18","I could stop TIME!"),("s19","I picked up the puppy... and time started again."),("s20","Everyone was staring at me."),("s22","Who was he?")]
k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
SR = 16000; gap = np.zeros(int(0.35 * SR)); ref = []; rb = []; t = 0
for s, txt in Z:
    a, sr = k.create(txt, voice="af_heart", speed=1.0, lang="en-us")
    a = librosa.resample(np.asarray(a, dtype=np.float32), orig_sr=sr, target_sr=SR); a, _ = librosa.effects.trim(a, top_db=35)
    rb.append(t); ref += [a, gap]; t += len(a) + len(gap)
ref = np.concatenate(ref)
tgt, _ = librosa.load("el/zara.mp3", sr=SR)
def feat(x):
    m = librosa.feature.mfcc(y=x, sr=SR, n_mfcc=20, hop_length=160)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
D, wp = librosa.sequence.dtw(feat(ref), feat(tgt), metric="cosine"); wp = wp[::-1]
# silences in target
rms = librosa.feature.rms(y=tgt, frame_length=800, hop_length=160)[0]; db = 20 * np.log10(rms + 1e-9)
sil = db < (db.max() - 38)
segs = []; i = 0
while i < len(sil):
    if sil[i]:
        j = i
        while j < len(sil) and sil[j]: j += 1
        if (j - i) >= 15: segs.append((i / 100, j / 100))
        i = j
    else: i += 1
print("pauses:", " ".join(f"{a:.2f}-{b:.2f}" for a, b in segs))
mids = [((a + b) / 2, b - a) for a, b in segs if a > 0.05 and b < len(tgt) / SR - 0.05]
bounds = [0.0]
for i in range(1, len(Z)):
    tb = (rb[i] - len(gap) / 2) / SR
    idx = np.searchsorted(wp[:, 0], int(tb * 100)); m = wp[min(idx, len(wp) - 1), 1] / 100
    near = [x for x in mids if abs(x[0] - m) < 0.8 and x[0] > bounds[-1] + 0.3]
    bounds.append(min(near, key=lambda x: abs(x[0] - m) - 0.3 * x[1])[0] if near else m)
bounds.append(len(tgt) / SR)
cuts = {}
for (s, txt), a, b in zip(Z, bounds, bounds[1:]):
    cuts[s] = (a, b); print(s, f"{a:.2f}-{b:.2f} ({b-a:.2f})", txt)
json.dump(cuts, open("el/cuts.json", "w"))
