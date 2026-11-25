"""IN MY TOWN: The Game. Cut narration + character lines into shots; write ep/timeline.json (dur, lead, vo, words, src).
Clips are picked by time range, then long pauses inside a clip are squeezed and, if still too long for its slot, the clip is sped up (max 1.3x)."""
import json, os, numpy as np, soundfile as sf, librosa
V = "/home/claude/zara/town/voice"; E = "/home/claude/zara/town/ep"
W = json.load(open(f"{V}/words.json")); AUD = {n: sf.read(f"{V}/{n}.wav") for n in ("rico", "maya", "leo", "game")}
# shot, source, clip start, clip end, lead, total duration (durations are locked to the rendered frames)
SHOTS = [("s01", "rico", 0.00, 3.45, 0.45, 4.9),    # In my town, there's one game you're never allowed to play.
         ("s02", "rico", 3.68, 5.20, 0.15, 2.4),    # Jayden found it in the library.
         ("s03", None, 0, 0, 0, 1.8),
         ("s04", "maya", 0.00, 1.55, 0.10, 1.9),    # Jayden! Don't!
         ("s05", "rico", 7.05, 8.70, 0.10, 2.2),    # Obviously, he rolled.
         ("s05b", None, 0, 0, 0, 1.9),
         ("s06", None, 0, 0, 0, 2.5),
         ("s07", "leo", 0.55, 3.30, 0.05, 3.4),     # ha ha ha Bro, it's just a board ga- CRASH
         ("s08", None, 0, 0, 0, 2.4),
         ("s09", "rico", 10.92, 13.62, 0.10, 3.0),  # Tyrone went full gladiator with a chair.
         ("s10", "rico", 13.85, 17.10, 0.10, 3.8),  # Me? I was filming. This is going straight on my story.
         ("s11", "game", 0.00, 3.10, 0.20, 3.6),    # Six players, six squares
         ("s12", "maya", 2.48, 4.05, 0.10, 2.2),    # There's only five of us!
         ("s13", "rico", 17.38, 23.80, 0.05, 2.9),  # (Then Maya counted the board. Six squares...) So who was the sixth player?
         ("s14", "rico", 24.42, 27.10, 0.05, 3.1),  # Whiskers, the cat, rolled, the dice.
         ("s15", "rico", 27.32, 29.05, 0.40, 4.0),  # We weren't in the library anymore.
         ("s16", "leo", 4.50, 7.45, 0.05, 3.0),     # Guys... where's Whiskers?!
         ("s17", None, 0, 0, 0, 4.0),
         ("s18", "game", 4.78, 7.55, 0.60, 5.4),    # The final player has been selected.
         ("s19", "rico", 29.05, 31.70, 0.05, 1.8)]  # And that's why, in my town... -> loop
SKIP = {"s13": (17.38, 21.90)}  # s13 only keeps "So who was the sixth player?"
def squeeze(y, sr, maxgap=0.18):
    """Return kept (start,end) sample intervals with pauses longer than maxgap shortened to maxgap."""
    iv = librosa.effects.split(y, top_db=35, frame_length=1024, hop_length=256)
    keep = []; pad = int(0.04 * sr)
    for i, (a, b) in enumerate(iv):
        a = max(0, a - pad) if i else 0; b = min(len(y), b + pad) if i < len(iv) - 1 else len(y)
        if keep and a - keep[-1][1] > maxgap * sr: keep.append([a, b])
        elif keep: keep[-1][1] = b
        else: keep.append([a, b])
    # rebuild with gaps of maxgap
    out = []; t = 0
    for k, (a, b) in enumerate(keep):
        if k: gap = min(maxgap * sr, a - keep[k - 1][1]); out.append(("gap", int(gap))); t += int(gap)
        out.append(("seg", a, b)); t += b - a
    return out
out = {"shots": [], "dur": {}, "lead": {}, "vo": {}, "words": {}, "src": {}}
os.makedirs(f"{E}/vo", exist_ok=True)
for s, src, a, b, lead, dur in SHOTS:
    out["shots"].append(s); out["dur"][s] = dur; out["lead"][s] = lead; out["src"][s] = src
    if not src: out["vo"][s] = 0; out["words"][s] = []; continue
    y, sr = AUD[src]; y = y if y.ndim == 1 else y.mean(1)
    a0 = SKIP[s][1] if s in SKIP else a
    seg = y[int(a0 * sr):int(b * sr)]
    parts = squeeze(seg, sr) if s not in ("s07",) else [("seg", 0, len(seg))]
    clip = []; tmap = []  # (orig_time, new_time) anchors
    t = 0
    for p in parts:
        if p[0] == "gap": clip.append(np.zeros(p[1])); t += p[1]
        else:
            _, i0, i1 = p; tmap.append((i0 / sr, t / sr)); clip.append(seg[i0:i1]); t += i1 - i0; tmap.append((i1 / sr, t / sr))
    clip = np.concatenate(clip)
    slot = dur - lead - 0.08
    rate = max(1.0, len(clip) / sr / slot)
    if s == "s07": slot = 2.95 - lead; rate = max(1.0, len(clip) / sr / slot)   # "ga-" must land on the CRASH
    if rate > 1.0:
        rate = min(rate, 1.3); clip = librosa.effects.time_stretch(clip.astype(np.float32), rate=rate)
    fd = int(0.012 * sr); clip[:fd] *= np.linspace(0, 1, fd); clip[-fd:] *= np.linspace(1, 0, fd)
    sf.write(f"{E}/vo/{s}.wav", clip, sr); out["vo"][s] = round(len(clip) / sr, 3)
    ot = np.array([p[0] for p in tmap]); nt = np.array([p[1] for p in tmap])
    m = lambda x: float(np.interp(x - a0, ot, nt)) / rate + lead
    out["words"][s] = [(w.replace("Jaden", "Jayden"), round(m(t0), 3), round(m(t1), 3)) for w, t0, t1 in W[src] if a0 - 0.05 <= t0 < b - 0.05]
    print(s, src, "len %.2f slot %.2f rate %.2f" % (len(clip) / sr, dur - lead, rate))
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.1fs" % sum(out["dur"].values()))
for s in out["shots"]: print(s, out["dur"][s], " ".join(f"{w}@{a:.2f}" for w, a, _ in out["words"][s]))
