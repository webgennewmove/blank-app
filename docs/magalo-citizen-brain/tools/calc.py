# Scratch calculator for the design doc: one set of formulas -> every number quoted.
import math

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

C = {  # traits: conf, caut, soc, cur, awr ; archetype: urgency, mobility, walk, run, phoneHabit
 "Priya": dict(conf=.55, caut=.35, soc=.30, cur=.25, awr=.20, urg=.9, mob=1.0, walk=10, run=18, habit=.8),
 "Des":   dict(conf=.85, caut=.20, soc=.75, cur=.65, awr=.55, urg=.3, mob=.9,  walk=8,  run=16, habit=.4),
 "Edith": dict(conf=.20, caut=.85, soc=.60, cur=.35, awr=.70, urg=.4, mob=.4,  walk=6,  run=9,  habit=.2),
}
def derived(t):
    return dict(
        vision=40+30*t["awr"], fov=110+40*t["awr"], attn=0.7+0.6*t["awr"],
        react=0.6-0.4*t["awr"], fearGain=1.4-0.8*t["conf"],
        panicIn=0.5+0.25*t["conf"], panicOut=0.25+0.25*t["conf"],
        fearHL=6+18*t["caut"], alertHL=4+6*t["caut"], space=3+3*t["caut"],
        standoff=22-10*t["cur"], loseTrack=6+4*t["awr"],
        shakenDur=120+180*t["caut"])
def prox_f(d): return 1/(1+(d/12)**2)
def prox_a(d): return 1/(1+(d/20)**2)
def raise_fear(f, threat, gain): return f+(1-f)*(1-math.exp(-threat*gain))
def raise_alert(a, sal): return a+(1-a)*(1-math.exp(-sal))
def decay(x, base, hl, dt): return base+(x-base)*0.5**(dt/hl)

print("== Derived parameters")
for n,t in C.items():
    d=derived(t); print(n, {k: round(v,2) for k,v in d.items()})

print("\n== Noticing an approaching player (walks 16 studs/s straight at them, from vision radius)")
def notice(t, activity, speed=16, sal=1.3, thresh=0.35):
    d=derived(t); att=d["attn"]*activity; dist=d["vision"]; a=0; dt=0.005
    while dist>0:
        a+=1.0*att*(1/(1+(dist/15)**2))*sal*dt; dist-=speed*dt
        if a>=thresh: return dist
    return 0
for n,t,act,lab in [("Priya",C["Priya"],0.4,"on phone"),("Des",C["Des"],1.0,"walking"),("Edith",C["Edith"],1.0,"walking"),("Edith",C["Edith"],0.7,"browsing")]:
    print(n,lab,"notices at %.1f studs"%notice(t,act))

print("\n== Scenario 3: theft 14 studs away (Priya hears it on phone; Des & Edith see it)")
d0=14
for n,t in C.items():
    dv=derived(t); seen = n!="Priya"; vis=1.0 if seen else 0.6
    threat=0.6*prox_f(d0)*vis; f=raise_fear(0.05,threat,dv["fearGain"]); a=raise_alert(0.05,1.2*vis*prox_a(d0))
    close=prox_f(d0); cert=1.0 if seen else 0.7
    S={}
    S["Ignore"]=(0.3+0.7*t["urg"])*(1-t["cur"])*(1-0.5*a)*(1-f)
    S["Observe"]=(0.3+0.9*t["cur"])*a*(1-f)**1.5
    S["Film"]=1.6*t["cur"]*(1-t["caut"])*a*(1-f)**2
    S["Call999"]=(0.4+0.4*t["caut"]+0.2*t["soc"])*0.6*cert*(1-0.5*f)
    S["Shout"]=(1.8*t["conf"]**2*(1-t["caut"])*a*(1-f)**2) if seen else 0.0
    S["MoveAway"]=(0.3+0.7*t["caut"])*(0.4+0.6*math.sqrt(f))*(0.5+0.5*close)
    print(n,"threat=%.3f fear=%.3f alert=%.3f"%(threat,f,a),"reactDelay=%.2fs"%(dv["react"]*(1.5 if n=="Priya" else 1)))
    for k,v in sorted(S.items(), key=lambda kv:-kv[1]): print("   %-9s %.3f"%(k,v))

print("\n== Des, 1.5 s later (Shout on cooldown), thief now 18 studs away vs. if thief ran past at 7 studs")
t=C["Des"]; dv=derived(t)
f=raise_fear(0.05,0.6*prox_f(14),dv["fearGain"]); f=decay(f,0.05,dv["fearHL"],1.5)
a=raise_alert(0.05,1.2*prox_a(14)); a=decay(a,0.05,dv["alertHL"],1.5)
for dthief in (18,7):
    chase=1.5*t["conf"]**2*(1-t["caut"])*clamp(1-dthief/25)*(1-0.6*f)
    obs=(0.3+0.9*t["cur"])*a*(1-f)**1.5; call=(0.4+0.4*t["caut"]+0.2*t["soc"])*0.6*(1-0.5*f); film=1.6*t["cur"]*(1-t["caut"])*a*(1-f)**2
    print(" thief %d: fear=%.3f alert=%.3f Chase=%.3f Observe=%.3f Call999=%.3f Film=%.3f"%(dthief,f,a,chase,obs,call,film))

print("\n== Scenario 4: robbed directly (thief 2 studs, directed x1.5); then choice after Shock")
for n,t in C.items():
    dv=derived(t); threat=1.0*prox_f(2)*1.0*1.5; f=raise_fear(0.05,threat,dv["fearGain"])
    thiefNear=clamp(1-4/25); helpNear=0.6
    S={"Freeze":1.2*(1-t["conf"])*f,
       "Chase":1.5*t["conf"]**2*(1-t["caut"])*thiefNear*(1-0.6*f),
       "GetAway":t["mob"]*(0.4+0.6*t["caut"])*f,
       "SeekHelp":(0.3+0.5*t["soc"])*f*helpNear}
    sh=1.0*(1-0.5*t["conf"])
    print(n,"threat=%.3f fear=%.3f shaken=%.3f"%(threat,f,sh))
    for k,v in sorted(S.items(), key=lambda kv:-kv[1]): print("   %-9s %.3f"%(k,v))

print("\n== Scenario 4 aftermath -> Recover (threat gone).")
def recover(t, f, shaken, officer, citizenNear, involve, episode):
    S={"CatchBreath":(0.5+0.5*t["caut"])*f,
       "TellSomeone":t["soc"]*episode*citizenNear,
       "GiveStatement":(0.5+0.3*t["soc"]+0.2*t["conf"])*(1-0.5*f)*officer*involve,
       "ResumeTrip":(0.4+0.6*t["urg"])*(1-shaken)*(1-f),
       "GoHome":(0.4+0.6*t["caut"])*shaken*(0.5+0.5*f)}
    return S
for n,t,dt,cn in [("Priya",C["Priya"],3.0,0),("Des",C["Des"],7.0,1),("Edith",C["Edith"],3.0,0)]:
    dv=derived(t); f0=raise_fear(0.05,prox_f(2)*1.5,dv["fearGain"]); f=decay(f0,0.05,dv["fearHL"],dt); sh=1-0.5*t["conf"]
    S=recover(t,f,sh,0,cn,1.3,1.0)
    print(n,"t+%.0fs fear=%.3f shaken=%.3f (no officer, citizenNear=%d)"%(dt,f,sh,cn), ", ".join("%s %.3f"%(k,v) for k,v in sorted(S.items(), key=lambda kv:-kv[1])))
    S2=recover(t,f,sh,1,cn,1.3,1.0)
    print("   ...if an officer is within 25 studs:", ", ".join("%s %.3f"%(k,v) for k,v in sorted(S2.items(), key=lambda kv:-kv[1])))

print("\n== Scenario 2: player lingers 3.5 studs away, facing them, for 2 s (alertness from lingering)")
for n,t in C.items():
    dv=derived(t); dd=3.5; a=raise_alert(0.05,0.25*2)
    intr=math.sqrt(clamp((dv["space"]-dd)/dv["space"])); ling=1.0
    keep=(0.4+0.6*t["caut"])*intr*ling
    face=t["conf"]*(1-t["caut"])*ling*clamp((6-dd)/6)*1.0
    cont=0.35*1.15
    phoneAway=(0.3+0.7*t["caut"])*intr*(0.5+0.5*a)
    ack=t["soc"]*t["conf"]*1.0*(1-a)
    print(n,"space=%.2f intrusion=%.3f alert=%.3f | Continue(with momentum)=%.3f switch-bar=%.3f KeepDistance=%.3f FaceAndHold=%.3f | overlay: PhoneAway=%.3f Acknowledge=%.3f"%(dv["space"],intr,a,cont,cont*1.2,keep,face,phoneAway,ack))

print("\n== Section 4 deep dive: Edith")
t=C["Edith"]; dv=derived(t)
f=raise_fear(0.05,0.6*prox_f(14),dv["fearGain"]); a=raise_alert(0.05,1.2*prox_a(14))
print("t=0.32 fear=%.3f alert=%.3f"%(f,a))
# MoveAway completes at t=3.5 (reached ~19 studs). Re-score at t=3.5
f35=decay(f,0.05,dv["fearHL"],3.18); a35=decay(a,0.05,dv["alertHL"],3.18); d35=19.0
S={"Call999":(0.4+0.4*t["caut"]+0.2*t["soc"])*0.6*(1-0.5*f35),
   "Observe":(0.3+0.9*t["cur"])*a35*(1-f35)**1.5,
   "Ignore":(0.3+0.7*t["urg"])*(1-t["cur"])*(1-0.5*a35)*(1-f35),
   "Film":1.6*t["cur"]*(1-t["caut"])*a35*(1-f35)**2,
   "MoveAway(done)":0.0}
print("t=3.5 fear=%.3f alert=%.3f"%(f35,a35), ", ".join("%s %.3f"%(k,v) for k,v in sorted(S.items(), key=lambda kv:-kv[1])))
# Escalation at t=5.2: suspect sprints past at 6 studs, approaching
f52=decay(f35,0.05,dv["fearHL"],1.7); thr=0.6*prox_f(6)*1.0*1.5
f52b=raise_fear(f52,thr,dv["fearGain"])
mob=t["mob"]; shelterD=5; threatD=6
P={"Shelter":(0.5+0.5*t["caut"])*f52b*(1/(1+(shelterD/15)**2)),
   "Flee":(0.5+0.5*mob)*f52b*(1/(1+(threatD/15)**2))*0.7,
   "Freeze":1.2*(1-t["conf"])*f52b**2*(1/(1+(threatD/8)**2))}
print("t=5.2 pre=%.3f threat=%.3f fear=%.3f (panicIn %.2f)"%(f52,thr,f52b,dv["panicIn"]), ", ".join("%s %.3f"%(k,v) for k,v in sorted(P.items(), key=lambda kv:-kv[1])))
# police at t=20 -> half-life halves
f20=decay(f52b,0.05,dv["fearHL"],20-5.2)
need=dv["panicOut"]; hl=dv["fearHL"]/2
dt=hl*math.log((f20-0.05)/(need-0.05))/math.log(2)
tr=20+dt
print("t=20 fear=%.3f ; fear < panicOut(%.2f) at t=%.1f"%(f20,need,tr))
fr=need-0.001; sh=0.8*(1-0.5*t["conf"])
R=recover(t,fr,sh,1,0,1.0,0.8)
print("t=%.1f Recover:"%tr, ", ".join("%s %.3f"%(k,v) for k,v in sorted(R.items(), key=lambda kv:-kv[1])))
# walk to officer 18 studs at 6 studs/s = 3 s, statement 5 s
tdone=tr+3+5; fd=decay(fr,0.05,hl,8)
R2=recover(t,fd,sh,0,0,1.0,0.8); R2.pop("GiveStatement")
print("t=%.1f after statement fear=%.3f:"%(tdone,fd), ", ".join("%s %.3f"%(k,v) for k,v in sorted(R2.items(), key=lambda kv:-kv[1])))
print("loseTrack window %.1fs -> live track purged at t=%.1f (last seen t=7.0)"%(dv["loseTrack"],7.0+dv["loseTrack"]))
