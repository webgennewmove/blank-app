"""Pirates episode: shots start on narration word indices (one continuous VO). Writes pirates/ep/timeline.json."""
import json
V = "/home/claude/zara/pirates/voice"; E = "/home/claude/zara/pirates/ep"
W = json.load(open(f"{V}/words.json"))
FIX = {5: "ONE", 6: "rule:", 12: "IS", 38: "ship!", 42: "RPG…", 61: "standoff.", 62: "Ten", 64: "Ten", 66: "ZERO", 77: "THEIR", 81: "\"Everybody", 82: "overboard.\"",
       91: "AGAIN.", 94: "COOK'S", 97: "\"LUNCH", 98: "BREAK!\"", 107: "KEVIN.", 110: "CRANE'S", 120: "it!", 127: "WHOLE", 132: "hat!", 151: "NO—",
       152: "KA-BOOM!", 177: "ME.", 186: "order:", 187: "\"Everyone…", 189: "shooting.\""}
W2 = [[FIX.get(i, w), a, b] for i, (w, a, b) in enumerate(W)]
STARTS = [("p01", 0), ("p02", 7), ("p03", 15), ("p04", 16), ("p05", 21), ("p06", 27), ("p07", 29), ("p08", 34), ("p09", 39), ("p10", 43),
          ("p11", 48), ("p12", 51), ("p14", 54), ("p15", 56), ("p16", 58), ("p17", 62), ("p18", 66), ("p19", 68), ("p20", 71),
          ("p21", 79), ("p22", 83), ("p23", 86), ("p24", 89), ("p25", 92), ("p26", 95), ("p27", 104), ("p28", 107), ("p29", 108), ("p30", 112),
          ("p31", 116), ("p32", 121), ("p33", 123), ("p34", 125), ("p35", 133), ("p36", 140), ("p37", 142), ("p38", 150), ("p39", 152), ("p40", 153),
          ("p41", 156), ("p42", 160), ("p43", 164), ("p44", 167), ("p45", 172), ("p46", 176), ("p47", 178), ("p48", 185), ("p49", 190), ("p50", 192), ("p51", 198)]
END = W[-1][2] + 0.45
FPS = 24
def first_word(k):
    i = STARTS[k][1]; return i[0] + 1 if isinstance(i, tuple) else i
def bt(k):
    if k == 0: return 0.0
    i = STARTS[k][1]
    if isinstance(i, tuple): return W[i[0]][2] + 0.08          # a [beat] shot: starts just after word i
    prev_end = W[i - 1][2]; a = W[i][1]
    return max(prev_end, a - 0.12)
out = {"shots": [], "dur": {}, "t0": {}, "lead": {}, "vo": {}, "words": {}, "src": {}}
for k, (s, _) in enumerate(STARTS):
    t0 = bt(k); t1 = bt(k + 1) if k + 1 < len(STARTS) else END
    f0, f1 = round(t0 * FPS), round(t1 * FPS); n = f1 - f0
    i0 = first_word(k) if not isinstance(STARTS[k][1], tuple) else STARTS[k][1][0] + 1
    i1 = first_word(k + 1) if k + 1 < len(STARTS) else len(W2)
    if isinstance(STARTS[k][1], tuple): i1 = i0     # beat shot: no words of its own
    out["shots"].append(s); out["dur"][s] = n / FPS; out["t0"][s] = f0 / FPS; out["lead"][s] = 0.0; out["vo"][s] = 0; out["src"][s] = None
    out["words"][s] = [(w, round(a - f0 / FPS, 3), round(b - f0 / FPS, 3)) for w, a, b in W2[i0:i1]]
json.dump(out, open(f"{E}/timeline.json", "w"), indent=1)
print("total %.2f" % sum(out["dur"].values()))
for s in out["shots"]: print(s, "%.2f" % out["dur"][s], " ".join(w for w, _, _ in out["words"][s]))
