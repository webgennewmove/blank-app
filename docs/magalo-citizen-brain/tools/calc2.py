import math, importlib.util, sys
spec = importlib.util.spec_from_file_location("c", "calc.py")
# reuse helpers without re-running prints
src = open("calc.py").read().split('print("== Derived parameters")')[0]
ns = {}; exec(src, ns)
C, derived, prox_f, prox_a, raise_fear, raise_alert, decay, clamp = (ns[k] for k in ["C","derived","prox_f","prox_a","raise_fear","raise_alert","decay","clamp"])

def recover(t, f, shaken, officer, citizenNear, involve, episode):
    return {"CatchBreath":(0.5+0.5*t["caut"])*f,
            "TellSomeone":t["soc"]*episode*citizenNear,
            "GiveStatement":(0.5+0.3*t["soc"]+0.2*t["conf"])*officer*involve*(0.7+0.3*f),
            "ResumeTrip":(0.4+0.6*t["urg"])*(1-shaken)*(1-f),
            "GoHome":(0.4+0.6*t["caut"])*shaken*(0.5+0.5*f)}
fmt=lambda S: ", ".join("%s %.3f"%(k,v) for k,v in sorted(S.items(), key=lambda kv:-kv[1]))

print("== Victim aftermath (Recover, threat gone)")
for n,dt,cn in [("Priya",3.0,0),("Des",7.0,1),("Edith",3.0,0)]:
    t=C[n]; dv=derived(t); f0=raise_fear(0.05,prox_f(2)*1.5,dv["fearGain"]); f=decay(f0,0.05,dv["fearHL"],dt); sh=1-0.5*t["conf"]
    print(n,"t+%.0fs fear=%.3f shaken=%.3f"%(dt,f,sh)); print("   no officer :",fmt(recover(t,f,sh,0,cn,1.3,1.0))); print("   officer≤25:",fmt(recover(t,f,sh,1,cn,1.3,1.0)))

print("\n== Des victim later: after Chase leash (6 s) + TellSomeone (6 s) -> t+13 s, then officer arrives")
t=C["Des"]; dv=derived(t); f0=raise_fear(0.05,prox_f(2)*1.5,dv["fearGain"]); f=decay(f0,0.05,dv["fearHL"],13); sh=1-0.5*t["conf"]
S=recover(t,f,sh,1,1,1.3,1.0); S.pop("TellSomeone"); print(" fear=%.3f"%f, fmt(S))
f2=decay(f,0.05,dv["fearHL"]/2,8); S=recover(t,f2,sh,0,0,1.3,1.0); S.pop("GiveStatement"); S.pop("TellSomeone"); print(" after statement fear=%.3f"%f2, fmt(S))

print("\n== Edith witness deep dive Recover with new GiveStatement")
t=C["Edith"]; dv=derived(t); sh=0.8*(1-0.5*t["conf"])
print(" shaken(close witness who panicked)=%.3f"%sh)
print(" t=27.3:",fmt(recover(t,0.299,sh,1,0,1.0,0.8)))
print(" t=35.3:",fmt({k:v for k,v in recover(t,0.198,sh,0,0,1.0,0.8).items() if k!="GiveStatement"}))

print("\n== Approach: FaceAndHold = Conf(1-Caut) * sqrt(socialIntrusion) * min(1,linger/4) * (0.5+alert)")
for n in C:
    t=C[n]; dv=derived(t); dd=3.5
    for linger in (2,4):
        a=raise_alert(0.05,0.25*linger)
        intr=math.sqrt(clamp((dv["space"]-dd)/dv["space"]))
        keep=(0.4+0.6*t["caut"])*intr*min(1,linger/1.5)
        face=t["conf"]*(1-t["caut"])*math.sqrt(clamp((6-dd)/6))*min(1,linger/4)*(0.5+a)
        phoneAway=(0.3+0.7*t["caut"])*intr*(0.5+0.5*a); ack=t["soc"]*t["conf"]*(1-a)
        print(" %-5s linger %ds alert=%.3f KeepDistance=%.3f FaceAndHold=%.3f (bar 0.483) | PhoneAway=%.3f (bar .25) Acknowledge=%.3f (bar .30)"%(n,linger,a,keep,face,phoneAway,ack))

print("\n== Shaken durations / fear half-lives with police nearby")
for n in C:
    dv=derived(C[n]); print(" %-5s fearHL %.1fs (police near %.1fs) shakenDur %.0fs loseTrack %.1fs"%(n,dv["fearHL"],dv["fearHL"]/2,dv["shakenDur"],dv["loseTrack"]))

print("\n== Witness (heard-only) Priya: time for alertness to fall below 0.20 (Alert -> Ambient), alertHL")
t=C["Priya"]; dv=derived(t); a=0.414; hl=dv["alertHL"]
dt=hl*math.log((a-0.05)/(0.20-0.05))/math.log(2); print(" %.1f s after the shout, +3 s hold = %.1f s"%(dt,dt+3))
