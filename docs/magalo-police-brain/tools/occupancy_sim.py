# Scratch simulation of the proposed occupancy-map search (not game code).
# Alley "Tanner's Yard": LKP = mouth M, heading north. Nodes ~12 studs apart, dt = 0.5 s,
# suspect sprint ~24 studs/s => mass moves about one node per tick, biased AWAY from the LKP.
from collections import deque
def run(dead_end=False, noise_at=None):
    edges = [("S0","M"),("M","A1"),("A1","A2"),("A2","A3"),("A3","N1"),("N1","N2"),("N2","N3"),
             ("A1","B1"),("A2","B2"),("A3","B3")]
    if not dead_end: edges += [("N3","ON"),("A2","E1"),("E1","E2"),("E2","E3"),("E3","OE")]
    nbr = {}
    for a,b in edges: nbr.setdefault(a,[]).append(b); nbr.setdefault(b,[]).append(a)
    hide = {"B1","B2","B3"}; outer = {n for n in ("ON","OE") if n in nbr}
    hop = {"M":0}; dq = deque(["M"])
    while dq:
        n = dq.popleft()
        for k in nbr[n]:
            if k not in hop: hop[k] = hop[n]+1; dq.append(k)
    heading = {"A1","A2","A3","N1","N2","N3","ON"}
    p = {n:0.0 for n in nbr}; p["M"] = 1.0
    vis = [(0.0, {"S0"}), (2.4, {"M","A1","A2","A3"}), (6.0, {"N1","N2"}), (9.0, {"N3"})]
    if not dead_end: vis += [(7.0, {"E1","E2"}), (11.0, {"E3"})]
    out_rows = []; t = 0.0
    while t <= 30.0 + 1e-9:
        q = {n:0.0 for n in p}
        for n,m in p.items():
            if m == 0: continue
            if n in outer: q[n] += m; continue
            out = 0.02 if n in hide else 0.8
            q[n] += m*(1-out)
            ws = []
            for k in nbr[n]:
                if k in hide: w = 0.6
                elif hop[k] > hop[n]: w = 3.0
                elif hop[k] == hop[n]: w = 1.0
                else: w = 0.3
                if t < 6.0 and k in heading: w *= 2.0
                ws.append((k,w))
            tot = sum(w for _,w in ws)
            for k,w in ws: q[k] += m*out*w/tot
        p = q
        if noise_at and abs(t - noise_at[0]) < 1e-9:      # officer hears a bin lid: evidence x3 on that bin
            p[noise_at[1]] *= 3.0
        visible = set().union(*[s for a,s in vis if a <= t])
        for n in visible: p[n] = 0.0
        tot = sum(p.values()); p = {n: m/tot for n,m in p.items()}
        if abs(t-round(t)) < 1e-9 and int(t) in (3,6,9,12,15,18,24,30):
            left = sum(p[o] for o in outer)
            street = max(((n,v) for n,v in p.items() if n not in outer and n not in hide), key=lambda x:x[1], default=("-",0))
            out_rows.append((int(t), {b: p[b] for b in sorted(hide)}, left, street))
        t = round(t+0.5,1)
    return out_rows
def show(title, rows):
    print(title)
    for t,b,left,st in rows:
        print(f"  t={t:>2}s  " + " ".join(f"{k}={v:.2f}" for k,v in b.items()) + f"  beyond-exits={left:.2f}  top-street={st[0]}:{st[1]:.2f}")
show("TWO EXITS", run(False))
show("DEAD END", run(True))
show("TWO EXITS, officer heard B2 lid at t=2.0", run(False, noise_at=(2.0,"B2")))
