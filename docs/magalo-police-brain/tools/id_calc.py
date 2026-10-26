# Identification and timing numbers for the scenarios (scratch, not game code).
def prox(d): return 1/(1+(d/25)**2)
def rate(desc, d, beh, onscene=1.0): return 1.6*desc*prox(d)*beh*onscene
B = {"fleeing":2.0, "sprinting":1.4, "walking":0.8, "standing":0.6}
print("ID time (s) to reach 1.0, constant conditions")
for desc,lab in [(1.0,"officer saw it"),(0.7,"victim statement"),(0.6,"witness saw"),(0.1,"heard only")]:
    row=[]
    for d in (15,25,40,60):
        row.append(f"d{d}: walk {1/rate(desc,d,B['walking']):.1f} / flee {1/rate(desc,d,B['fleeing']):.1f}")
    print(f"  {lab:<17} " + " | ".join(row))
# Scenario 1: officer sees P walking at 40 studs for 1.0 s, then P sprints away (fleeing) as officer closes 40->34 studs
prog = rate(0.6,40,B['walking'])*1.0
t=0; d=40.0; dt=0.05
while prog < 1.0:
    prog += rate(0.6,d,B['fleeing'])*dt; t+=dt; d = max(20, d - (22-24)*dt*-1*0)  # distance roughly holds while P flees
print(f"\nScenario 1: after 1 s calm progress={rate(0.6,40,B['walking']):.2f}; fleeing at ~40 studs -> confirmed {t:.2f} s later (total {1+t:.2f} s)")
# on-scene factor for heard-only report: person within report radius, fleeing at 20 studs
print(f"Heard-only, fleeing at 20 studs, on scene x1.5: {1/rate(0.1,20,B['fleeing'],1.5):.1f} s")
# ETA examples (jog 0.7*Sp, sprint 0.92*Sp, Sp=24)
Sp=24; jog=0.7*Sp; spr=0.92*Sp
print(f"\nOfficer jog {jog:.1f} studs/s, sprint {spr:.1f} studs/s (player sprint assumed {Sp})")
for dist in (85,140,180): print(f"  {dist} studs: jog ETA {dist/jog:.1f} s, run ETA {dist/spr:.1f} s")
# Gap growth: player sprint vs officer sprint over 8 s from 10 studs
print(f"Gap after 8 s straight sprint from 10 studs: {10+(Sp-spr)*8:.1f} studs; officer then jogs: gap grows {(Sp-jog):.1f} studs/s")
