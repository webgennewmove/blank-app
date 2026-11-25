"""IN MY TOWN: The Game. Cut narration + character lines into shots; write ep/timeline.json (dur, lead, vo, words, src)."""
import json, os, numpy as np, soundfile as sf
V = "/home/claude/zara/town/voice"; E = "/home/claude/zara/town/ep"
W = json.load(open(f"{V}/words.json")); AUD = {n: sf.read(f"{V}/{n}.wav") for n in ("rico", "maya", "leo", "game")}
# shot, source, clip start, clip end, lead, total duration
SHOTS = [("s01", "rico", 0.00, 3.75, 0.45, 4.9),    # dice tumbling in emerald slow-mo (hook)
         ("s02", "rico", 4.22, 5.55, 0.15, 2.4),    # Jayden pulls the box off the locked shelf
         ("s03", None, 0, 0, 0, 1.8),               # the board opens: it's a map of our town
         ("s04", "maya", 0.00, 1.40, 0.10, 1.9),    # Maya grabs his arm: "Jayden, don't!"
         ("s05", "rico", 7.66, 9.35, 0.10, 2.2),    # "Obviously... he rolled."
         ("s05b", None, 0, 0, 0, 1.9),              # dice tumble slow-mo -> six
         ("s06", None, 0, 0, 0, 2.5),               # windows shatter, glass freezes mid-air
         ("s07", "leo", 0.00, 2.95, 0.10, 3.4),     # Leo laughing "bro it's just a board ga-" CRASH
         ("s08", None, 0, 0, 0, 2.4),               # crocodile through the door
         ("s09", "rico", 12.38, 14.85, 0.10, 3.0),  # Tyrone + chair (Whiskers nudges the dice in the background)
         ("s10", "rico", 15.18, 18.50, 0.10, 3.8),  # Rico's phone POV
         ("s11", "game", 0.00, 3.00, 0.20, 3.6),    # the game speaks: six players, six squares
         ("s12", "maya", 2.40, 4.10, 0.10, 2.2),    # "There's only five of us."
         ("s13", "rico", 23.80, 26.10, 0.10, 2.9),  # everyone slowly turns to the cat
         ("s14", "rico", 26.70, 29.45, 0.05, 3.1),  # Whiskers. The cat. Rolled. The dice.
         ("s15", "rico", 29.88, 31.58, 0.40, 4.0),  # library melts -> emerald vortex -> jungle
         ("s16", "leo", 3.70, 6.40, 0.10, 3.0),     # "Guys... where's Whiskers?"
         ("s17", None, 0, 0, 0, 4.0),               # ROAR above: Whiskers on a branch, golden crown
         ("s18", "game", 3.00, 7.10, 0.15, 5.4),    # the final player has been selected; trees turn to face them
         ("s19", "rico", 31.66, 32.85, 0.10, 1.8)]  # "And that's why..." -> loops into "In my town..."
out = {"shots": [], "dur": {}, "lead": {}, "vo": {}, "words": {}, "src": {}}
os.makedirs(f"{E}/vo", exist_ok=True)
for s, src, a, b, lead, dur in SHOTS:
    out["shots"].append(s); out["dur"][s] = dur; out["lead"][s] = lead; out["src"][s] = src
    if src:
        y, sr = AUD[src]; clip = y[int(a * sr):int(b * sr)].copy(); fd = int(0.012 * sr)
        clip[:fd] *= np.linspace(0, 1, fd); clip[-fd:] *= np.linspace(1, 0, fd)
        sf.write(f"{E}/vo/{s}.wav", clip, sr); out["vo"][s] = round(b - a, 3)
        out["words"][s] = [(w.replace("Jaden", "Jayden"), round(t0 - a + lead, 3), round(t1 - a + lead, 3)) for w, t0, t1 in W[src] if a - 0.05 <= t0 < b - 0.05]
    else:
        out["vo"][s] = 0; out["words"][s] = []
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.1fs" % sum(out["dur"].values()))
for s in out["shots"]: print(s, out["dur"][s], " ".join(w for w, _, _ in out["words"][s]))
