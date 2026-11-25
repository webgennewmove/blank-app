"""Glow episode: shots start on narration word indices (one continuous VO track). Writes glow/ep/timeline.json."""
import json
V = "/home/claude/zara/town/glow/voice"; E = "/home/claude/zara/town/glow/ep"
W = json.load(open(f"{V}/words.json"))
FIX = {"bald,": "Bulb.", "Boom,": "FWOOM!", "Jaden's": "Jayden's", "Jaden": "Jayden", "whiskers.": "Whiskers.", "whiskers": "Whiskers",
       "street": "street-", "lights.": "lights.", "Hide": "Hide-and-", "and": "and", "glowing.": "GLOWING!", "lights,": "lights?", "are": "ARE",
       "town": "town.", "until": "Until", "one.": "one!", "Hey,": "HEY,", "over": "OVER", "here.": "HERE!", "Everybody,": "EVERYBODY,",
       "coats": "COATS", "on.": "ON!"}
W2 = []
for i, (w, a, b) in enumerate(W):
    w2 = FIX.get(w, w)
    if i == 17 and w == "and": w2 = "seek"; 
    W2.append([w2, a, b])
# merge "Hide" "and" "seek" -> display as separate words ok; fix the hide-and-seek trio
W2[16][0] = "Hide-"; W2[17][0] = "and-"; W2[18][0] = "seek"
W2[11][0] = "street"; W2[12][0] = "lights."
W2[87][0] = "flashlight"; W2[89][0] = "town."
W2[165][0] = "MOTHS!"; W2[80][0] = "Dead"; W2[195][0] = "Dead"; W2[105][0] = "FWOOM!"; W2[106][0] = "GIANT"; W2[107][0] = "MOTHS!"
# shot -> first word index
STARTS = [("s01", 0), ("s02", 3), ("s03", 8), ("s04", 13), ("s05", 16), ("s06", 22), ("s07", 24), ("s07b", 26), ("s08", 28), ("s09", 31),
          ("s10", 40), ("s11", 47), ("s12", 50), ("s13", 53), ("s14", 56), ("s16", 62), ("s17", 67), ("s18", 69), ("s19", 76),
          ("s20", 80), ("s21", 82), ("s22", 88), ("s23", 90), ("s24", 97), ("s25", 103), ("s26", 105), ("s27", 106), ("s28", 108), ("s29", 113),
          ("s30", 118), ("s31", 123), ("s32", 127), ("s33", 130), ("s34", 135), ("s35", 141), ("s36", 144), ("s37", 150), ("s38", 153), ("s39", 155),
          ("s40", 161), ("s41", 163), ("s42", 164), ("s43", 165), ("s44", 168), ("s45", 171), ("s46", 174), ("s47", 180), ("s48", 186), ("s49", 188),
          ("s50", 192), ("s51", 195), ("s52", 199), ("s53", 207)]
END = W[-1][2] + 1.2
FPS = 24
def bt(k):   # boundary time for shot k (a hair before its first word)
    if k == 0: return 0.0
    i = STARTS[k][1]; prev_end = W[i - 1][2]; a = W[i][1]
    return max(prev_end, a - 0.12)
out = {"shots": [], "dur": {}, "t0": {}, "lead": {}, "vo": {}, "words": {}, "src": {}}
for k, (s, i0) in enumerate(STARTS):
    t0 = bt(k); t1 = bt(k + 1) if k + 1 < len(STARTS) else END
    f0, f1 = round(t0 * FPS), round(t1 * FPS); n = f1 - f0
    i1 = STARTS[k + 1][1] if k + 1 < len(STARTS) else len(W2)
    out["shots"].append(s); out["dur"][s] = n / FPS; out["t0"][s] = f0 / FPS; out["lead"][s] = 0.0; out["vo"][s] = 0; out["src"][s] = None
    out["words"][s] = [(w, round(a - f0 / FPS, 3), round(b - f0 / FPS, 3)) for w, a, b in W2[i0:i1]]
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.2f" % sum(out["dur"].values()))
for s in out["shots"]: print(s, "%.2f" % out["dur"][s], " ".join(w for w, _, _ in out["words"][s]))
