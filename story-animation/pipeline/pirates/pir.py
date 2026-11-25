"""PIRATES: 'I'm The Captain Now (For 3 Seconds)'. EEVEE, Roblox-style cast.
usage: EEVEE=1 python pir.py -- all|p01,p05 [still]"""
import sys, os, json, math, random
REAL_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = [sys.argv[0], "--", "none"]
os.environ["HOOD"] = "1"
exec(open("/home/claude/zara/world.py").read())
import bmesh
from mathutils import Vector, Quaternion, Matrix, Euler
ONLY = set(REAL_ARGV[0].split(",")) if REAL_ARGV and REAL_ARGV[0] != "all" else None
exec(open("/home/claude/zara/eevee_patch.py").read())
exec(open("/home/claude/zara/town/rcast.py").read())
STILL = len(REAL_ARGV) > 1 and REAL_ARGV[1] == "still"
E = "/home/claude/zara/pirates/ep"; OUT = f"{E}/frames"
S.render.resolution_x, S.render.resolution_y = 576, 1024
try: S.eevee.shadow_resolution_scale = 0.5
except Exception: pass
S.render.film_transparent = False
TL = json.load(open(f"{E}/timeline.json")); DUR = TL["dur"]; WORDS = TL["words"]; T0 = TL["t0"]
WORLD.hide_render = True; ROOM.hide_render = True
for o in BALLOONS: o.hide_render = True
def ease(u): return u * u * (3 - 2 * u)
def wt(shot, word, k=0):
    word = word.lower().strip(".,!?-…\"")
    hits = [a for w, a, b in WORDS[shot] if w.lower().strip(".,!?-…\"") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
def F(t): return max(1, int(round(t * FPS)) + 1)
exec(open("/home/claude/zara/pirates/pir_sets.py").read())
ship_on(False)
FIXED_HAT = 1.15

# ---------------------------------------------------------------- camera + pose helpers
def cam2(f, loc, at, lens=30, roll=0.0):
    CAM.location = loc; CAM.data.lens = lens
    q = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y") @ Quaternion((0, 0, 1), roll)
    CAM.rotation_euler = q.to_euler()
    CAM.keyframe_insert("location", frame=f); CAM.keyframe_insert("rotation_euler", frame=f); CAM.data.keyframe_insert("lens", frame=f)
def cpath(n, a_loc, a_at, b_loc, b_at, la=30, lb=None, ra=0.0, rb=None, f0=1, f1=None, smooth=True, shake=0.0):
    f1 = f1 or n
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); u = ease(u) if smooth else u
        j = Vector((math.sin(f * 1.9), math.cos(f * 1.3), math.sin(f * 2.7))) * shake
        cam2(f, Vector(a_loc).lerp(Vector(b_loc), u) + j, Vector(a_at).lerp(Vector(b_at), u), la + ((lb or la) - la) * u,
             ra + ((rb if rb is not None else ra) - ra) * u)
def look_rot(src, dst):
    d = Vector(dst) - Vector(src); return math.atan2(d.y, d.x) + math.pi / 2
def hold(c, f0, f1, face=None, **kw):
    for f in range(f0, f1 + 1, 2):
        t = f / 24; kw2 = dict(kw); kw2.setdefault("hips_z", 2.0); kw2["hips_z"] += 0.03 * math.sin(t * 2.6 + hash(c.name) % 7)
        hd = kw2.get("head", (0, 0, 0)); kw2["head"] = (hd[0] + 0.04 * math.sin(t * 1.9), hd[1], hd[2] + 0.05 * math.sin(t * 1.2))
        c.pose(f, **kw2)
    if face: c.set_face(face, f0)
def blinks(c, f0, f1, face, seed=0):
    rnd = random.Random(seed + len(c.name)); f = f0 + rnd.randint(6, 20)
    while f < f1 - 4: c.set_face("blink", f); c.set_face(face, f + 3); f += rnd.randint(30, 60)
def aim_hold(c, f0, f1, face="determined", lean=0.0, twist=0.0):
    for f in range(f0, f1 + 1, 2):
        t = f / 24; aim_pose(c, f, lean=lean, twist=twist, head=(0.03 * math.sin(t * 2 + len(c.name)), 0, 0.04 * math.sin(t * 1.3)))
    c.set_face(face, f0)
def salute_hold(c, f0, f1, face="determined"):
    for f in range(f0, f1 + 1, 2): salute_pose(c, f)
    c.set_face(face, f0)
def sea_shot(name):
    SEA_T0[0] = T0[name]; SEA_AMP[0] = 1.0
def W2L(obj, p):
    return obj.matrix_world @ Vector(p)

# ---------------------------------------------------------------- layout (ship at origin, along +X; starboard (y<0) faces the camera side)
OURS = [(-62.0, -12.0), (-56.5, -13.0), (-51.0, -12.0), (-45.5, -13.0), (-40.0, -12.0), (-34.5, -13.0)]   # bev toby dale kevin crew0 crew1
CARGO = [(-59.0, 6.0), (-52.5, 7.0), (-46.0, 6.0), (-39.5, 7.0)]
COOKP = (-84.0, -4.0)
GIANTP = Vector((BR_X + 6, -20.5, WING_Z))
OPEN = Vector((-620.0, -320.0, 0))       # open sea for the opening (ship far away + hidden)
SKLOC = {"bev": (6.0, -1.6), "toby": (6.0, 1.6), "dale": (1.5, -1.6), "kevin": (1.5, 1.6), "crew0": (-3.0, -1.6), "crew1": (-3.0, 1.6)}
MK = {"bev": mk_bev, "toby": mk_toby, "dale": mk_dale, "kevin": mk_kevin, "crew0": lambda: mk_crew(0), "crew1": lambda: mk_crew(1)}
NAMES = ["bev", "toby", "dale", "kevin", "crew0", "crew1"]
def our_crew(names=NAMES, weapons=True):
    cs = {}
    for k in names:
        c = MK[k]()
        if k == "toby": c.hat_top = 0.84
        if weapons: rpg(c) if k == "dale" else rifle(c)
        cs[k] = c
    return cs
def cargo_crew(n=4, weapons=True):
    out = []
    for i in range(n):
        c = mk_cargo(i)
        if weapons: rifle(c)
        out.append(c)
    return out
def skiff_scene(n, at=OPEN, heading=0.0, speed=0.0, names=NAMES, weapons=True, gull=False, draft=0.2):
    """skiff floating at 'at' with the crew aboard (parented, standing on the floor, facing the bow)"""
    sea_center(at.x, at.y); sk = mk_skiff(); wake(sk, 1, n) if speed > 4 else None
    for f in range(1, n + 1):
        d = speed * (f - 1) / FPS; float_on(sk, f, at.x + math.cos(heading) * d, at.y + math.sin(heading) * d, heading, draft=draft, tilt=0.8)
    cs = our_crew(names, weapons)
    for k, c in cs.items():
        lx, ly = SKLOC[k]; c.root.parent = sk; c.place((lx, ly, SKIFF_FLOOR), math.pi / 2)
    g = None
    if gull:
        g = Gull(); g.root.parent = sk; g.root.location = (12.0, 0, 2.78); g.root.rotation_euler = (0, 0, -math.pi / 2); g.fold(1)
    return sk, cs, g
def boat_pt(sk, f, local):
    S.frame_set(f); return sk.matrix_world @ Vector(local)
def hat_on_obj(obj, f, z, sc=FIXED_HAT, tilt=0.0, off=(0, 0)):
    S.frame_set(f); mw = obj.matrix_world
    p = mw @ Vector((off[0], off[1], z)); r = mw.to_euler()
    hat_key(f, p, (r.x + tilt, r.y, r.z), sc)
def hat_on(c, f0, f1, extra=0.0, sc=FIXED_HAT, step=1):
    z = (getattr(c, "hat_top", None) or HAT_ON) + extra
    for f in range(f0, f1 + 1, step): hat_on_obj(c.head, f, z, sc)
def hat_off(f): hat_key(f, (0, 0, -500), (0, 0, 0), 0.01)
def head_world(c, f, z=0.0):
    S.frame_set(f); return c.head.matrix_world @ Vector((0, 0, z))
def hat_fly(f0, f1, a, b, h=5.0, spins=1.5, sc=FIXED_HAT):
    a, b = Vector(a), Vector(b)
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); p = a.lerp(b, u) + Vector((0, 0, 4 * h * u * (1 - u)))
        hat_key(f, p, (0.35 * math.sin(u * 7), 0.25 * math.sin(u * 5), spins * 2 * math.pi * u), sc)
def ping(loc, f):
    muzzle(loc, f, 0.45)
def sneeze(c, f, n_after=8):
    """Kevin's sneeze: head snaps back then forward, rifle jerks straight up and fires at the sky"""
    c.set_face("shocked", f - 6); aim_pose(c, f - 6)
    c.pose(f - 3, arms=(1.6, 1.7), head=(-0.45, 0, 0), lean=-0.15)
    c.pose(f, arms=(2.9, 3.0), arms_side=(-0.2, 0.0), head=(0.35, 0, 0), lean=0.2); c.set_face("blink", f)
    c.pose(f + n_after, arms=(2.6, 2.7), head=(0.0, 0, 0), lean=0.0); c.set_face("shocked", f + 3)
    S.frame_set(f); tip = c.gun.matrix_world @ c.gun_tip
    muzzle(tip, f, 0.9); tracer(tip, tip + Vector((0, 0, 60)), f, 3)
def thumbs(c, f0, f1, face="smug"):
    for f in range(f0, f1 + 1, 2): c.pose(f, arms=(0, 1.5), arms_side=(0, 0.25), head=(0.04 * math.sin(f / 5), 0, 0))
    c.set_face(face, f0)
def rail_climb_pose(c, f, k=0.0):
    c.pose(f, arms=(2.9, 2.6 + 0.3 * math.sin(k)), arms_side=(0.2, 0.2), legs=(0.6 * math.sin(k), -0.6 * math.sin(k)))
def look_at_cam(c, f0, f1): pass

# ---------------------------------------------------------------- shots
def p01(n):   # tight CU: smug gull on the skiff bow wearing the hat (frame 1 = loop target)
    sea_shot("p01"); sk, cs, g = skiff_scene(n, names=["bev", "toby"], gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    g.fold(1); g.fold(n, 0.1)
    for k, c in cs.items(): salute_hold(c, 1, n)
    def gp(f, off): return boat_pt(sk, f, (12.0 + off[0], off[1], 2.78 + off[2]))
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); tgt = gp(f, (0, 0, 3.3))
        cam2(f, gp(f, (-5.2 + 1.2 * u, -6.4 + 1.5 * u, 1.9)), gp(f, (0, 0, 2.7)), 33)
def p02(n):   # the whole crew snaps to attention and salutes the gull (gull POV, low)
    sea_shot("p02"); sk, cs, g = skiff_scene(n, gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    for i, (k, c) in enumerate(cs.items()):
        hold(c, 1, 4 + i, face="happy"); c.pose(6 + i, arms=(0, 2.0), arms_side=(0, 0.6)); salute_hold(c, 8 + i, n)
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1))
        cam2(f, boat_pt(sk, f, (16.0, -2.0 + 2.5 * u, 6.6)), boat_pt(sk, f, (0.0, 0.4 * u, 4.6)), 22)
def p03(n):   # hatless Bev holds the salute, deadpan, eyes slide to the gull
    sea_shot("p03"); sk, cs, g = skiff_scene(n, names=["bev"], weapons=False, gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    for k, c in cs.items(): salute_hold(c, 1, n, face="determined")
    b = cs["bev"]; b.set_face("smug", 1)
    for f in range(1, n + 1, 2): b.pose(f, arms=(0, 2.55), arms_side=(0, 0.95), head=(0.05, 0, -0.35 * ease(min(1, f / (n * 0.6)))))
    hp = lambda f: boat_pt(sk, f, (6.0, -1.6, SKIFF_FLOOR + 4.7 * 1.08))
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); h = hp(f)
        cam2(f, boat_pt(sk, f, (6.0 + 6.5 - 1.2 * u, -1.6 + 4.2, SKIFF_FLOOR + 5.2)), h, 42)
def fries_basket(parent=None, loc=(0, 0, 0), coll=None):
    coll = coll or TEMP; b = empty("basket", loc, parent=parent, coll=coll)
    box("bsk", (0, 0, 0.3), (1.2, 0.9, 0.6), mat("bskm", (0.85, 0.15, 0.1), 0.6), parent=b, coll=coll, bevel=0.06)
    fr = []
    for k in range(9):
        fr.append(box("fry", (-0.4 + (k % 3) * 0.4, -0.25 + (k // 3) * 0.25, 0.75), (0.12, 0.12, 0.7), mat("frym", (1.0, 0.8, 0.25), 0.6),
                      rot=(0.2 * math.sin(k), 0.2 * math.cos(k), 0), parent=b, coll=coll))
    return b, fr
def p04(n):   # gull squawks an order and points a wing at the fry basket
    sea_shot("p04"); sk, cs, g = skiff_scene(n, names=["bev", "kevin"], gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    fb, fr = fries_basket(sk, (9.2, 1.6, SKIFF_FLOOR))
    g.fold(1)
    for f in range(4, n + 1):
        a = 0.9 + 0.15 * math.sin(f * 0.9)
        g.wings[0][0].rotation_euler = (0, a * 0.6, math.pi / 2 - a); g.wings[0][0].keyframe_insert("rotation_euler", frame=f)   # one wing points
    for f, hx in ((1, 0), (5, -0.35), (8, 0.15), (11, -0.3), (14, 0.1), (n, 0)):
        g.head.rotation_euler = (hx, 0, 0.3 if f > 4 else 0); g.head.keyframe_insert("rotation_euler", frame=f)
    for k, c in cs.items(): salute_hold(c, 1, n)
    gp = lambda f, o: boat_pt(sk, f, (12.0 + o[0], o[1], 2.78 + o[2]))
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); z = 1.0 + 0.25 * min(1, f / 5)
        cam2(f, gp(f, (-6.0 + 1.0 * u, -4.5, 2.2)), gp(f, (-1.5, 0.6, 1.6)), 30 + 8 * min(1, f / 5))
def p05(n):   # Kevin, sad, tips the whole basket in front of the gull; it gulps them
    sea_shot("p05"); sk, cs, g = skiff_scene(n, names=["kevin", "bev"], weapons=False, gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    k = cs["kevin"]; k.root.location = (8.55, 0.0, SKIFF_FLOOR); k.place((8.55, 0.0, SKIFF_FLOOR), math.pi / 2)
    fb, fr = fries_basket(k.arms[1], (0, -0.6, -2.3))
    fb.rotation_euler = (0, 0, 0)
    for f in range(1, n + 1, 2):
        u = min(1, f / (n * 0.5)); k.pose(f, arms=(1.3, 1.45), arms_side=(-0.35, 0), head=(0.15, 0, 0), lean=0.1)
        fb.rotation_euler = (-1.4 * ease(u), 0, 0); fb.keyframe_insert("rotation_euler", frame=f)
    k.set_face("sad", 1)
    for i, o in enumerate(fr): vis(o, int(n * 0.45) + i // 2, False)
    for f in range(1, n + 1, 3):
        g.head.rotation_euler = (0.35 + 0.25 * math.sin(f), 0, 0); g.head.keyframe_insert("rotation_euler", frame=f)
    hold(cs["bev"], 1, n, face="sad")
    gp = lambda f, o: boat_pt(sk, f, (12.0 + o[0], o[1], 2.78 + o[2]))
    cpath(n, gp(1, (-2.5, -9.0, 3.5)), gp(1, (-1.5, 0, 1.8)), gp(1, (-2.5, -8.2, 3.0)), gp(1, (-1.5, 0, 1.4)), 30, 32)
def p06(n):   # Toby to lens, deadpan thumbs-up; gull gulping behind him
    sea_shot("p06"); sk, cs, g = skiff_scene(n, names=["toby"], weapons=False, gull=True)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    t = cs["toby"]; t.place((7.0, -1.0, SKIFF_FLOOR), 0.15)
    thumbs(t, 1, n, "smug")
    for f in range(1, n + 1, 3): g.head.rotation_euler = (0.3 + 0.3 * math.sin(f * 1.3), 0, 0); g.head.keyframe_insert("rotation_euler", frame=f)
    hp = lambda f: head_world(t, f)
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); h = hp(f)
        cam2(f, boat_pt(sk, f, (9.5 + 0.4 * math.sin(f / 6), -8.5, SKIFF_FLOOR + 4.6)), h + Vector((0, 0, -0.6)), 34)
def p07(n):   # Bev snatches the hat and slaps it on; the gull flaps off, offended
    sea_shot("p07"); sk, cs, g = skiff_scene(n, names=["bev", "toby"], gull=True)
    b = cs["bev"]; b.place((9.5, -0.8, SKIFF_FLOOR), math.pi / 2)
    grab = int(n * 0.35)
    for f in range(1, grab + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    S.frame_set(grab); a = HAT.location.copy(); hb = head_world(b, n, HAT_ON)
    hat_fly(grab, grab + 6, a, hb + Vector((0, 0, 0.2)), h=1.5, spins=0.25)
    hat_on(b, grab + 7, n)
    b.pose(1, arms=(0.3, 0.2)); b.pose(grab - 2, arms=(0.3, 2.8), arms_side=(0, 0.2)); b.pose(grab + 6, arms=(0.3, 2.9), arms_side=(0, 0.6)); b.pose(n, arms=(0.2, 2.6), arms_side=(0, 0.7))
    b.set_face("determined", 1); b.set_face("smug", grab + 6)
    g.root.parent = None; g0 = boat_pt(sk, 1, (12.0, 0, 2.78))
    for f in range(1, n + 1):
        if f <= grab: S.frame_set(f); g.root.location = boat_pt(sk, f, (12.0, 0, 2.78)); g.root.rotation_euler = (0, 0, -math.pi / 2)
        else:
            u = (f - grab) / (n - grab); g.root.location = boat_pt(sk, f, (12.0 + 7 * u, 3 * u, 2.78 + 7 * u * u)); g.root.rotation_euler = (0.2, 0, -math.pi / 2 + math.pi * u)
        g.root.keyframe_insert("location", frame=f); g.root.keyframe_insert("rotation_euler", frame=f)
    g.flap(grab, n, speed=5, amp=1.0)
    hold(cs["toby"], 1, n, face="excited")
    cpath(n, boat_pt(sk, 1, (8.0, -9.0, 6.0)), boat_pt(sk, 1, (11.0, 0, 5.0)), boat_pt(sk, 1, (8.5, -8.5, 6.5)), boat_pt(sk, 1, (10.0, 0, 5.6)), 28, 30)
SHIP_ON_SHOTS = set()
def ship_shot(name):
    ship_on(True); SHIP_ON_SHOTS.add(name)
def p08(n):   # skiff at full speed, wake, aimed at the red hull corner (bow only, top cropped)
    sea_shot("p08"); ship_shot("p08")
    at = Vector((60.0, -115.0, 0)); hd = math.radians(70)
    sk, cs, g = skiff_scene(n, at=at, heading=hd, speed=22, names=["bev", "toby", "dale", "kevin"])
    hat_on(cs["bev"], 1, n, step=1)
    for k, c in cs.items():
        hold(c, 1, n, face="excited", arms=(0.6, 0.6), lean=0.15)
    for f in range(1, n + 1):
        p = boat_pt(sk, f, (2.0, -9.5, 0)); p.z = 2.2
        cam2(f, p, boat_pt(sk, f, (14.0, 2.0, 3.5)), 24)
def p09(n):   # Dale shoulders the RPG, squints, FWOOSH: rocket straight UP
    sea_shot("p09"); sk, cs, g = skiff_scene(n, names=["dale", "kevin", "bev"])
    hat_on(cs["bev"], 1, n, step=1)
    d = cs["dale"]; fire = int(n * 0.45)
    for f in range(1, n + 1, 2): rpg_pose(d, f, up=min(1.25, 1.25 * f / (fire - 2)) if f < fire else 1.25)
    d.set_face("determined", 1); d.set_face("blink", fire - 6); d.set_face("excited", fire + 2)
    S.frame_set(fire); tip = d.gun.matrix_world @ d.gun_tip
    r = rocket(); fly_rocket(r, [tip, tip + Vector((0, 0, 140))], fire, n + 6)
    muzzle(tip, fire, 1.0)
    S.frame_set(fire); back = d.gun.matrix_world @ d.gun_back
    for k in range(4): smoke_trail([(fire + k, back + Vector((0, 0, 0.3 * k)))], fire, fire + 4, size=0.9)
    hold(cs["kevin"], 1, n, face="excited"); hold(cs["bev"], 1, n, face="determined")
    h = lambda f: head_world(d, f)
    for f in range(1, n + 1):
        u = ease(max(0, (f - fire)) / max(1, n - fire)); hh = h(f)
        cam2(f, boat_pt(sk, f, (5.5, -7.5, SKIFF_FLOOR + 4.0)), hh + Vector((0, 0, 30 * u)), 30)
def p10(n):   # the whole crew tilts their heads up at a tiny dot in the sky; Dale shrugs
    sea_shot("p10"); sk, cs, g = skiff_scene(n)
    hat_on(cs["bev"], 1, n, step=1)
    for k, c in cs.items():
        for f in range(1, n + 1, 2): c.pose(f, head=(-0.55 - 0.05 * math.sin(f / 4), 0, 0), arms=(0.2, 0.3)) if k != "dale" else None
        c.set_face("shocked", 1)
    d = cs["dale"]
    for f in range(1, n + 1, 2):
        s_ = max(0, min(1, (f - n * 0.5) / 6))
        d.pose(f, arms=(1.2 * s_ + 0.2, 1.2 * s_ + 0.2), arms_side=(0.9 * s_, 0.9 * s_), head=(-0.3 + 0.3 * s_, 0, 0.25 * s_))
    d.set_face("happy", int(n * 0.5))
    dot = sphere("dot", boat_pt(sk, 1, (4, 0, 120)), 1.0, mat("dotm", (0.2, 0.2, 0.2)), coll=TEMP)
    cpath(n, boat_pt(sk, 1, (16.5, -0.5, 2.4)), boat_pt(sk, 1, (2.0, 0.2, 6.5)), boat_pt(sk, 1, (16.2, -1.2, 2.3)), boat_pt(sk, 1, (2.0, 0.6, 7.0)), 20, 20)
def p11(n):   # the rocket vanishes into a cloud with a twinkle
    sea_shot("p11"); sea_center(OPEN.x, OPEN.y)
    cl = empty("bigcloud", OPEN + Vector((30, 160, 150)), coll=TEMP); cw = mat("cloudw", (1, 1, 1), 0.95); rnd = random.Random(3)
    for k in range(9): sphere("puff", (rnd.uniform(-16, 16), rnd.uniform(-5, 5), rnd.uniform(-4, 6)), rnd.uniform(8, 14), cw, coll=TEMP, parent=cl, seg=14)
    r = rocket(); a = OPEN + Vector((10, 120, 60)); b = cl.location + Vector((0, 0, 2))
    fly_rocket(r, [a, b], 1, int(n * 0.6)); vis(r, int(n * 0.6) + 1, False)
    cpath(n, OPEN + Vector((0, 0, 8)), cl.location + Vector((0, 0, -20)), OPEN + Vector((2, 4, 8)), cl.location + Vector((-3, 0, -14)), 32, 34)
def rope_rod(a, b, name="rope"):
    return rod(name, Vector(a), Vector(b), 0.12, mat("ropem", (0.72, 0.58, 0.35), 0.9), coll=TEMP, verts=6)
def hook_prop(loc):
    e = empty("ghook", loc, coll=TEMP); m = mat("hookm2", (0.2, 0.2, 0.22), 0.3)
    box("gh1", (0, 0.35, 0.2), (0.25, 0.9, 0.25), m, parent=e, coll=TEMP); box("gh2", (0, 0.75, -0.25), (0.25, 0.25, 0.8), m, parent=e, coll=TEMP)
    box("gh3", (0, -0.1, -0.2), (0.25, 0.25, 0.7), m, parent=e, coll=TEMP)
    return e
HULLY = -SH_W / 2; RAILZ = DECK_Z + 1.9
def climbers(names, x0, f0, n, y=HULLY - 1.3, z0=4.0, z1=13.0):
    cs = our_crew(names, weapons=False); out = {}
    for i, k in enumerate(names):
        c = cs[k]; x = x0 + i * 4.5
        for f in range(1, n + 1, 2):
            u = (f - 1) / max(1, n - 1); z = z0 + (z1 - z0) * u - i * 1.2
            c.move(f, (x, y, z), 0.0 + math.pi); rail_climb_pose(c, f, f * 0.6 + i)
        c.root.rotation_euler = (0, 0, math.pi); c.set_face("determined", 1); out[k] = c
    return out
def p12(n):   # CLANK CLANK: hooks bite the rail, the crew climbs the red hull
    sea_shot("p12"); ship_shot("p12"); sea_center(-50, -60)
    for i, x in enumerate((-58.0, -50.0)):
        hk = hook_prop(Vector((x, HULLY - 0.2, RAILZ + 0.1))); hk.rotation_euler = (0, 0, math.pi)
        o = Vector((x, -40, 2)); b = hk.location
        for f in range(1, n + 1):
            u = min(1, f / (3 + i * 3)); hk.location = o.lerp(b, ease(u)) + Vector((0, 0, 6 * u * (1 - u))); hk.keyframe_insert("location", frame=f)
        rope_rod(Vector((x, HULLY - 0.6, RAILZ)), Vector((x, HULLY - 1.4, 0.5)))
    climbers(["toby", "bev", "dale"], -60.0, 1, n, z0=3.0, z1=7.0)
    cpath(n, (-46, -36, 1.5), (-54, HULLY, 14), (-47, -35, 1.8), (-54, HULLY, 16), 22, 22)
def p14(n):   # Kevin dangles at the end of a short rope, legs kicking above the waves
    sea_shot("p14"); ship_shot("p14"); sea_center(-50, -60)
    x = -45.0; top = Vector((x, HULLY - 0.6, RAILZ)); end = Vector((x, HULLY - 1.2, 10.0))
    hook_prop(Vector((x, HULLY - 0.2, RAILZ + 0.1))).rotation_euler = (0, 0, math.pi)
    rope_rod(top, end)
    k = our_crew(["kevin"], weapons=False)["kevin"]
    for f in range(1, n + 1):
        sw = 0.08 * math.sin(f / 5); k.root.location = end + Vector((0, -0.3, -4.6 * 0.82 - 0.2)); k.root.rotation_euler = (sw, 0, math.pi)
        k.root.keyframe_insert("location", frame=f); k.root.keyframe_insert("rotation_euler", frame=f)
        k.pose(f, arms=(3.05, 3.05), arms_side=(0.05, 0.05), legs=(0.7 * math.sin(f * 0.8), -0.7 * math.sin(f * 0.8)))
    k.set_face("scared", 1)
    cpath(n, (x + 3, HULLY - 15, 6), (x, HULLY, 8.5), (x + 3.6, HULLY - 14, 6.4), (x, HULLY, 8.0), 30, 32)
def p15(n):   # Thanks, Kevin: the crew climbs over him, boot on his head
    sea_shot("p15"); ship_shot("p15"); sea_center(-50, -60)
    x = -45.0; end = Vector((x, HULLY - 1.2, 10.0))
    rope_rod(Vector((x, HULLY - 0.6, RAILZ)), end)
    k = our_crew(["kevin"], weapons=False)["kevin"]; kroot = end + Vector((0, -0.3, -4.6 * 0.82 - 0.2))
    k.place(kroot, math.pi)
    for f in range(1, n + 1, 2): k.pose(f, arms=(3.05, 3.05), arms_side=(0.05, 0.05), head=(0.25, 0, 0), legs=(0.3 * math.sin(f), -0.3 * math.sin(f)))
    k.set_face("sad", 1)
    S.frame_set(1); ktop = k.head.matrix_world @ Vector((0, 0, 0.62))
    t = our_crew(["toby"], weapons=False)["toby"]
    for f in range(1, n + 1, 2):
        u = min(1, f / (n * 0.55)); z = ktop.z + 0.3 + 4.0 * max(0, (f - n * 0.6) / (n * 0.4))
        t.move(f, (ktop.x - 0.3, ktop.y + 0.25, max(ktop.z + 0.3, z) if f > n * 0.55 else ktop.z + 1.0 - 0.7 * u), math.pi)
        rail_climb_pose(t, f, f * 0.7)
    t.set_face("smug", 1)
    cpath(n, (x + 2.5, HULLY - 12, 10.5), (x, HULLY - 1, 10.8), (x + 2.8, HULLY - 11, 10.5), (x, HULLY - 1, 10.5), 32, 34)
def deck_shot(name, cx=-50.0, cy=-40.0):
    sea_shot(name); ship_shot(name); sea_center(cx, cy)
def place_ours(cs, f=1, face="determined"):
    for k, (x, y) in zip(NAMES, OURS):
        if k in cs: cs[k].place((x, y, DECK_Z), math.pi)
def place_cargo(cg, f=1):
    for c, (x, y) in zip(cg, CARGO): c.place((x, y, DECK_Z), 0.0)
def p16(n):   # our crew pops over the rail; the cargo crew spins round, everyone raises rifles
    deck_shot("p16"); cs = our_crew(); cg = cargo_crew()
    for i, (k, (x, y)) in enumerate(zip(NAMES, OURS)):
        c = cs[k]; f_in = 2 + i * 2
        c.move(1, (x, HULLY - 1.5, DECK_Z - 4.5), math.pi); c.move(f_in, (x, HULLY - 1.5, DECK_Z - 4.5), math.pi)
        c.move(f_in + 6, (x, HULLY + 1.5, DECK_Z + 3.0), math.pi); c.move(f_in + 10, (x, y, DECK_Z), math.pi)
        c.pose(1, arms=(2.9, 2.9)); c.pose(f_in + 6, arms=(2.6, 2.6), legs=(0.9, -0.3)); aim_hold(c, f_in + 12, n)
        if k == "bev": hat_on(c, 1, n)
    for i, (c, (x, y)) in enumerate(zip(cg, CARGO)):
        fs = int(n * 0.35) + i * 2
        c.move(1, (x, y, DECK_Z), math.pi); c.move(fs, (x, y, DECK_Z), math.pi); c.move(fs + 5, (x, y, DECK_Z), 0.0)
        hold(c, 1, fs, face="happy", arms=(0.1, 0.1)); aim_hold(c, fs + 4, n, face="shocked")
    cpath(n, (-49, -34, DECK_Z + 6), (-49, 0, DECK_Z + 4), (-49, -27, DECK_Z + 5.5), (-49, 0, DECK_Z + 4), 22, 24)
def standoff(n, faces=True):
    cs = our_crew(); cg = cargo_crew(); place_ours(cs); place_cargo(cg)
    for k, c in cs.items():
        if k == "dale":
            for f in range(1, n + 1, 2): rpg_pose(c, f)
            c.set_face("determined", 1)
        else: aim_hold(c, 1, n)
    for c in cg: aim_hold(c, 1, n)
    return cs, cg
def p17(n):   # ten guns, ten guys: slow orbit; two are aiming at their own teammates
    deck_shot("p17"); cs, cg = standoff(n); hat_on(cs["bev"], 1, n)
    cs["crew1"].place((OURS[5][0], OURS[5][1], DECK_Z), math.pi + 1.4); cg[3].place((CARGO[3][0], CARGO[3][1], DECK_Z), -1.3)
    C = Vector((-48, -3, DECK_Z))
    for f in range(1, n + 1):
        a = math.radians(-70 + 50 * ease((f - 1) / (n - 1))); cam2(f, C + Vector((math.cos(a) * 34, math.sin(a) * 34, 14)), C + Vector((0, 0, 3)), 24)
def p18(n):   # ZERO plan: Kevin and a cargo crewman aim at each other, then both shrug
    deck_shot("p18"); ks = our_crew(["kevin"]); k = ks["kevin"]; c = cargo_crew(1)[0]
    k.place((-48, -7, DECK_Z), math.pi); c.place((-48, 5, DECK_Z), 0.0)
    sh = int(n * 0.45)
    for ch, fc in ((k, "determined"), (c, "determined")):
        aim_hold(ch, 1, sh - 2, face=fc)
        for f in range(sh, n + 1, 2): ch.pose(f, arms=(1.0, 0.9), arms_side=(0.9, 0.9), head=(0, 0.2 * math.sin(f / 4), 0.15))
        ch.set_face("smug", sh)
    cpath(n, (-24, -1.0, DECK_Z + 5), (-48, -1.0, DECK_Z + 4.0), (-25.5, -1.0, DECK_Z + 5), (-48, -1.0, DECK_Z + 4.0), 24, 25)
def p19(n):   # Kevin sneezes: head snaps, rifle jerks straight up, muzzle flash at the sky
    deck_shot("p19"); cs, cg = standoff(n); hat_on(cs["bev"], 1, n)
    k = cs["kevin"]; sz = int(wt("p19", "sneezed") * FPS) + 6
    aim_hold(k, 1, sz - 6); sneeze(k, sz)
    S.frame_set(1); h = k.head.matrix_world.translation
    cpath(n, h + Vector((3.5, 9.0, 0.6)), h + Vector((0, 0, 0.2)), h + Vector((3.0, 7.8, 0.8)), h + Vector((0, 0, 0.6)), 32, 34)
def p20(n):   # PING: the hat spins up off Bev's head and arcs onto the Giant up on the bridge wing
    deck_shot("p20"); cs, cg = standoff(n); gi = mk_giant(); gi.place(GIANTP, -0.25)
    hold(gi, 1, n, face="smug", arms=(0.25, 1.3), arms_side=(0, 0.1))
    b = cs["bev"]; up = 8
    hat_on(b, 1, up); S.frame_set(up); a = HAT.location.copy()
    S.frame_set(up); ping(a + Vector((0.8, -0.4, 0.8)), up)
    land = int(n * 0.72); dst = head_world(gi, land, gi.hat_top)
    hat_fly(up, land, a, dst, h=12, spins=2.5)
    for f in range(land, n + 1): hat_on_obj(gi.head, f, gi.hat_top)
    b.set_face("shocked", up + 2)
    for f in range(1, n + 1):
        S.frame_set(f); hp = HAT.matrix_world.translation.copy() if f <= land else dst
        u = ease((f - 1) / (n - 1)); base = Vector((-58, -38, DECK_Z + 8)).lerp(Vector((-86, -50, DECK_Z + 26)), u)
        cam2(f, base, hp, 26 + 10 * u)
def p21(n):   # the Giant sips his juice box and lazily points at the sea
    deck_shot("p21"); gi = mk_giant(); gi.place(GIANTP, -0.25); hat_on(gi, 1, n)
    pt = int(n * 0.45)
    for f in range(1, n + 1, 2):
        u = max(0, min(1, (f - pt) / 8))
        gi.pose(f, arms=(0.25 + 1.2 * u, 2.4 - 1.1 * u), arms_side=(0.6 * u, 0.2), head=(0.15 - 0.2 * u, 0, -0.1))
    gi.set_face("smug", 1)
    S.frame_set(1); h = gi.head.matrix_world.translation
    cpath(n, h + Vector((3, -24, -7)), h + Vector((0, 0, -1)), h + Vector((2.5, -20, -6.5)), h + Vector((0, 0, -0.5)), 26, 28)
def p22(n):   # our crew salutes, then all vault the rail in sync
    deck_shot("p22"); cs = our_crew(); jump = int(n * 0.45)
    for i, (k, (x, y)) in enumerate(zip(NAMES, OURS)):
        c = cs[k]; y0 = HULLY + 2.5
        c.place((x, y0, DECK_Z), 0.0); salute_hold(c, 1, jump - 2)
        for f in range(jump, n + 1):
            u = (f - jump) / max(1, n - jump); c.move(f, (x, y0 - 6.5 * u, DECK_Z + 5.5 * math.sin(math.pi * min(1, u * 1.3)) - 4 * max(0, u - 0.6)), 0.0)
            c.pose(f, arms=(2.9, 2.9), arms_side=(0.3, 0.3), legs=(0.9, 0.9))
        c.set_face("excited", jump)
    cpath(n, (-30, -38, DECK_Z + 3), (-48, HULLY, DECK_Z + 3), (-32, -37, DECK_Z + 3.4), (-48, HULLY, DECK_Z + 3.6), 22, 23)
def p23(n):   # high angle straight down the hull: six bodies tumble into the water, a row of splashes
    deck_shot("p23", -48, -45); cs = our_crew(weapons=False)
    for i, (k, (x, y)) in enumerate(zip(NAMES, OURS)):
        c = cs[k]; f0 = 1 + i * 2; land = min(n - 2, f0 + 14)
        a = Vector((x, HULLY - 3, DECK_Z - 2)); b = Vector((x + 1, HULLY - 9, -1.5))
        knockback(c, f0, a, b, h=2.0, frames=land - f0, spin=0.6)
        vis(c.root, land + 2, False)
        splash(Vector((x + 1, HULLY - 9, 0.2)), land, 1.3)
    cpath(n, (-40, HULLY + 3, DECK_Z + 7), (-48, HULLY - 9, 0), (-40.5, HULLY + 2.5, DECK_Z + 6.5), (-48, HULLY - 9, 0), 20, 20)
def p24(n):   # soaked crew climbs back over the rail; Kevin sneezes AGAIN at the end
    deck_shot("p24"); cs = our_crew(["bev", "toby", "kevin", "crew0"])
    sz = int(wt("p24", "sneezed") * FPS) + 5
    for i, k in enumerate(["bev", "toby", "kevin", "crew0"]):
        c = cs[k]; x = -56 + i * 5.5
        c.move(1, (x, HULLY - 1.5, DECK_Z - 3.5), math.pi); c.move(8 + i, (x, HULLY + 1.0, DECK_Z + 1.5), math.pi); c.move(14 + i, (x, HULLY + 3.5, DECK_Z), math.pi)
        c.pose(1, arms=(2.8, 2.8)); c.pose(10 + i, arms=(2.0, 2.4), legs=(0.8, -0.2)); hold(c, 16 + i, n, face="sad", arms=(0.2, 0.2))
        c.set_face("sad", 1)
    k = cs["kevin"]; rifle(k); aim_hold(k, 18, sz - 7, face="sad"); sneeze(k, min(n - 6, sz))
    cpath(n, (-44, -38, DECK_Z + 6), (-48, HULLY + 3, DECK_Z + 3), (-45, -35, DECK_Z + 6), (-48, HULLY + 3, DECK_Z + 3.5), 26, 28)
def p25(n):   # PING: a stray shot pings the hat off the Giant's cap
    deck_shot("p25"); gi = mk_giant(); gi.place(GIANTP, -0.25)
    hold(gi, 1, n, face="smug", arms=(0.25, 1.3)); off = int(n * 0.4)
    hat_on(gi, 1, off); S.frame_set(off); a = HAT.location.copy(); ping(a + Vector((0.6, -0.5, 1.0)), off)
    hat_fly(off, n, a, a + Vector((14, 10, -10)), h=7, spins=1.5)
    gi.set_face("shocked", off + 3)
    S.frame_set(1); h = gi.head.matrix_world.translation
    cpath(n, h + Vector((5, -15, 0)), h + Vector((0, 0, 1.5)), h + Vector((5.5, -14, 0.5)), h + Vector((2, 2, 1.5)), 34, 30)
def p26(n):   # the hat lands on the Cook's toque; ladle up: LUNCH BREAK. Cargo crew salutes in the background
    deck_shot("p26"); ck = mk_cook(); ck.place((*COOKP, DECK_Z), -0.6)
    cg = cargo_crew(4)
    for i, c in enumerate(cg): c.place((COOKP[0] + 9 + i * 4.0, COOKP[1] + 9 + (i % 2), DECK_Z), 2.6); salute_hold(c, 8 + i * 2, n, face="happy"); hold(c, 1, 7 + i * 2)
    land = 7; S.frame_set(land); top = ck.head.matrix_world @ Vector((0, 0, ck.hat_top))
    hat_fly(1, land, top + Vector((-6, 4, 6)), top, h=2, spins=0.4)
    hat_on(ck, land, n)
    for f in range(1, n + 1, 2):
        u = min(1, max(0, (f - land) / 6)); ck.pose(f, arms=(0.2, 0.3 + 2.6 * u), arms_side=(0, 0.2), head=(-0.1 * u, 0, 0))
    ck.set_face("happy", 1); ck.set_face("excited", land + 2)
    S.frame_set(1); h = ck.head.matrix_world.translation
    cpath(n, h + Vector((6, -11, -2)), h + Vector((2, 2, 1.0)), h + Vector((5.5, -10, -2.2)), h + Vector((2, 2, 1.4)), 26, 28)
def sandwich(c, hand=0):
    e = empty("sandwich", (0, -0.4, -2.1), parent=c.arms[hand], coll=c.coll)
    box("bread1", (0, 0, 0.22), (0.9, 0.8, 0.18), mat("breadm", (0.92, 0.72, 0.42), 0.8), parent=e, coll=c.coll, bevel=0.05)
    box("lettuce", (0, 0, 0.08), (1.0, 0.9, 0.08), mat("lettm", (0.3, 0.8, 0.2), 0.7), parent=e, coll=c.coll)
    box("ham", (0, 0, -0.02), (0.92, 0.84, 0.1), mat("hamm", (0.95, 0.45, 0.45), 0.7), parent=e, coll=c.coll)
    box("bread2", (0, 0, -0.16), (0.9, 0.8, 0.18), mat("breadm", (0.92, 0.72, 0.42), 0.8), parent=e, coll=c.coll, bevel=0.05)
    return e
def p27(n):   # standoff... with sandwiches: rifle in one hand, sandwich in the other, chewing hard
    deck_shot("p27"); cs = our_crew(); cg = cargo_crew(); place_ours(cs); place_cargo(cg)
    for k, c in list(cs.items()) + [(c.name, c) for c in cg]:
        sandwich(c)
        for f in range(1, n + 1, 2):
            ch = math.sin(f * 1.1 + len(c.name))
            c.pose(f, arms=(1.2 + 0.5 * max(0, ch), 1.5), arms_side=(-0.25, 0), head=(0.06 * ch, 0, 0))
        c.set_face("determined", 1)
        for f in range(3, n, 6): c.set_face("talk", f); c.set_face("determined", f + 3)
    ck = mk_cook(); ck.place((-70, -2, DECK_Z), -1.2); hat_on(ck, 1, n); hold(ck, 1, n, face="happy", arms=(0.2, 2.6))
    C = Vector((-48, -3, DECK_Z))
    for f in range(1, n + 1):
        a = math.radians(-20 - 45 * ease((f - 1) / (n - 1))); cam2(f, C + Vector((math.cos(a) * 30, math.sin(a) * 30, 12)), C + Vector((0, 0, 3)), 24)
def p28(n):   # KEVIN.: he sneezes again, the hat pings off the toque; the Cook's face drops
    deck_shot("p28"); ks = our_crew(["kevin"]); k = ks["kevin"]; k.place((-60, -9, DECK_Z), math.pi - 0.6)
    ck = mk_cook(); ck.place((-72, 2, DECK_Z), -2.2); hold(ck, 1, n, face="happy", arms=(0.2, 2.4))
    sz = 6; aim_hold(k, 1, 2); sneeze(k, sz)
    off = sz + 3; hat_on(ck, 1, off); S.frame_set(off); a = HAT.location.copy(); ping(a + Vector((0, 0, 1.5)), off)
    hat_fly(off, n, a, a + Vector((10, 8, 6)), h=4, spins=1.2); ck.set_face("sad", off + 3)
    S.frame_set(1); hk = k.head.matrix_world.translation.copy(); fw = Vector((0.56, 0.83, 0))
    cpath(n, hk + fw * 9 + Vector((1.5, 0, 0.6)), hk + Vector((0, 0, 0.6)), hk + fw * 8 + Vector((1.3, 0, 0.8)), hk + Vector((0, 0, 1.2)), 28, 30)
def hook_swing(n, amp=0.12):
    for f in range(1, n + 1):
        a = amp * math.sin(f / 9); HOOK.rotation_euler = (a, 0, 0); HOOK.keyframe_insert("rotation_euler", frame=f)
def p29(n):   # the hat lands on the swinging crane hook
    deck_shot("p29"); hook_swing(n)
    land = int(n * 0.35)
    S.frame_set(land); top = HOOK.matrix_world @ Vector((0, 0, 1.2))
    hat_fly(1, land, top + Vector((-8, 6, 5)), top, h=2, spins=0.5)
    for f in range(land, n + 1): hat_on_obj(HOOK, f, 1.2)
    cpath(n, (-42, -14, DECK_Z + 4), HOOK.location + Vector((0, 0, 0)), (-43, -13, DECK_Z + 4), HOOK.location + Vector((0, 0, 1)), 24, 26)
def p30(n):   # both crews salute the dangling hook. Nothing happens. The smug gull lands on the hook
    deck_shot("p30"); hook_swing(n, 0.08); cs = our_crew(); cg = cargo_crew(); place_ours(cs); place_cargo(cg)
    for c in list(cs.values()) + cg:
        S.frame_set(1); c.root.rotation_euler = (0, 0, look_rot(c.root.location, HOOK.location)); c.root.keyframe_insert("rotation_euler", frame=1)
        salute_hold(c, 1, n, face="determined")
    for f in range(1, n + 1): hat_on_obj(HOOK, f, 1.2)
    g = Gull(); land = int(n * 0.6)
    for f in range(1, n + 1):
        S.frame_set(f); hp = HOOK.matrix_world @ Vector((0.0, 0.0, -1.55))
        if f < land:
            u = f / land; p = hp + Vector((14 * (1 - u), -6 * (1 - u), 6 * (1 - u) ** 2 + 0.2))
        else: p = hp
        g.root.location = p; g.root.rotation_euler = (0, 0, -0.6); g.root.keyframe_insert("location", frame=f); g.root.keyframe_insert("rotation_euler", frame=f)
    g.root.location = HOOK.location; g.flap(1, land, speed=4, amp=0.9); g.fold(land + 1)
    cpath(n, (-49, -46, DECK_Z + 8), (-48, -1, DECK_Z + 8), (-49, -44, DECK_Z + 8.5), (-48, -1, DECK_Z + 9), 22, 22)
def p31(n):   # a gust lifts the hat off the hook and sails it over the rail
    deck_shot("p31"); hook_swing(n, 0.2)
    S.frame_set(1); a = HOOK.matrix_world @ Vector((0, 0, 1.2)); b = Vector((-30, -60, 6))
    for f in range(1, 4): hat_on_obj(HOOK, f, 1.2)
    hat_fly(4, n, a, b, h=6, spins=2.0)
    for f in range(1, n + 1):
        S.frame_set(f); hp = HAT.matrix_world.translation.copy()
        cam2(f, hp + Vector((-6, 12, 3)), hp, 28)
def p32(n):   # our soggy crew back in the skiff, racing
    sea_shot("p32"); ship_shot("p32")
    at = Vector((60.0, -120.0, 0)); sk, cs, g = skiff_scene(n, at=at, heading=0.0, speed=26, names=["bev", "toby", "dale", "kevin"])
    for k, c in cs.items(): hold(c, 1, n, face="determined", arms=(0.8, 0.8), lean=0.2)
    for f in range(1, n + 1):
        p = boat_pt(sk, f, (-4.0, -10.0, 0)); p.z = 2.0; cam2(f, p, boat_pt(sk, f, (8.0, 0.0, 3.0)), 22)
def p33(n):   # the orange lifeboat packed with hard hats, racing
    sea_shot("p33"); ship_shot("p33"); at = Vector((60.0, -100.0, 0)); sea_center(at.x + 30, at.y)
    lb = mk_lifeboat(); wake(lb, 1, n)
    for f in range(1, n + 1): float_on(lb, f, at.x + 25 * (f - 1) / FPS, at.y, 0.0, draft=0.3, tilt=0.8)
    cg = cargo_crew(4, weapons=False)
    for i, c in enumerate(cg):
        c.root.parent = lb; c.place((3.5 - i * 2.8, 1.2 if i % 2 else -1.2, lb["floor"]), math.pi / 2); hold(c, 1, n, face="determined", arms=(0.9, 0.9), lean=0.2)
    for f in range(1, n + 1):
        p = boat_pt(lb, f, (-3.0, 10.0, 0)); p.z = 2.0; cam2(f, p, boat_pt(lb, f, (8.0, 0, 3.0)), 22)
HATSEA = Vector((175.0, -75.0, 0))
def bob_hat(f0, f1, at=HATSEA):
    for f in range(f0, f1 + 1):
        t = sea_t(f); z = sea_z(at.x, at.y, t)
        hat_key(f, Vector((at.x, at.y, z + 0.15)), (0.15 * math.sin(f / 6), 0.12 * math.cos(f / 7), f * 0.02), FIXED_HAT)
def hose_jet(a, b, f0, f1, h=10.0, k=14):
    """fire-hose water arc a->b: droplet blobs streaming along a parabola"""
    a, b = Vector(a), Vector(b)
    for i in range(k):
        o = sphere("jet", a, 1, SPRAYM, coll=TEMP, seg=8)
        for f in range(f0, f1 + 1, 2):
            u = ((f - f0) / 10.0 + i / k) % 1.0; p = a.lerp(b, u) + Vector((0, 0, 4 * h * u * (1 - u)))
            o.location = p; o.keyframe_insert("location", frame=f); s = 0.45 + 0.35 * u; o.scale = (s, s, s); o.keyframe_insert("scale", frame=f)
def p34(n):   # the hat bobs on a wave; skiff + lifeboat flank it; the cargo bow looms (cropped); fire-hose jets
    sea_shot("p34"); ship_shot("p34"); sea_center(HATSEA.x, HATSEA.y)
    bob_hat(1, n)
    sk = mk_skiff(); lb = mk_lifeboat()
    for f in range(1, n + 1):
        float_on(sk, f, HATSEA.x + 22 - 6 * f / n, HATSEA.y - 11, math.pi - 0.3, draft=0.2, tilt=0.8)
        float_on(lb, f, HATSEA.x + 24 - 5 * f / n, HATSEA.y + 11, math.pi + 0.3, draft=0.3, tilt=0.8)
    cs = our_crew(["bev", "toby", "dale"])
    for k, c in cs.items(): c.root.parent = sk; lx, ly = SKLOC[k]; c.place((lx, ly, SKIFF_FLOOR), math.pi / 2); hold(c, 1, n, face="excited", arms=(1.3, 1.3))
    cg = cargo_crew(2, weapons=False)
    for i, c in enumerate(cg): c.root.parent = lb; c.place((3 - i * 3, 0.6 * (1 if i else -1), lb["floor"]), math.pi / 2); hold(c, 1, n, face="excited", arms=(1.3, 1.3))
    for j, (ox, oy) in enumerate(((-4, 3), (5, -2.5), (-1, -5))):
        hose_jet(Vector((140 + j * 6, HULLY - 0.5, RAILZ)), HATSEA + Vector((ox, oy, 0)), 1, n, h=8)
        splash(HATSEA + Vector((ox, oy, 0.2)), 1 + j * 5, 0.8, n=10, crown=False)
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); z = sea_z(HATSEA.x - 9, HATSEA.y, sea_t(f)) + 2.2
        cam2(f, HATSEA + Vector((-10 + 1.5 * u, -1.5, z)), HATSEA + Vector((0, 1.0, 1.6 + 0.4 * u)), 26)
def p35(n):   # a dolphin leaps and the hat lands on its head mid-arc (slow-mo, side tracking)
    sea_shot("p35"); sea_center(HATSEA.x, HATSEA.y)
    d = Dolphin(scale=1.2); land = int(n * 0.45)
    a = HATSEA + Vector((-12, 0, -3)); b = HATSEA + Vector((12, 0, -3))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); p = a.lerp(b, u) + Vector((0, 0, 4 * 9 * u * (1 - u)))
        d.root.location = p; ang = math.atan2(36 * (1 - 2 * u), 24)
        d.root.rotation_euler = (ang, 0, math.pi / 2); d.root.keyframe_insert("location", frame=f); d.root.keyframe_insert("rotation_euler", frame=f)
    bob_hat(1, land - 4); S.frame_set(land - 4); a2 = HAT.location.copy()
    S.frame_set(land); hd = d.root.matrix_world @ Vector((0, -2.0, 0.95))
    hat_fly(land - 4, land, a2, hd, h=2.5, spins=0.6)
    for f in range(land, n + 1): hat_on_obj(d.root, f, 0.95, off=(0, -2.0))
    splash(a + Vector((0, 0, 3.2)), 1, 1.2); splash(b + Vector((0, 0, 3.2)), n - 2, 1.0)
    for f in range(1, n + 1):
        S.frame_set(f); dp = d.root.matrix_world.translation.copy()
        cam2(f, Vector((dp.x - 2, dp.y - 26, 4.5)), Vector((dp.x, dp.y, dp.z * 0.7 + 1.5)), 26)
def p36(n):   # every boat salutes the dolphin, which nods gravely
    sea_shot("p36"); sea_center(HATSEA.x, HATSEA.y)
    d = Dolphin(scale=1.2); dp = HATSEA + Vector((0, 0, 0))
    for f in range(1, n + 1):
        z = sea_z(dp.x, dp.y, sea_t(f)) + 0.4; d.root.location = (dp.x, dp.y, z); d.root.rotation_euler = (-0.55 + 0.15 * math.sin(f / 3), 0, -0.6)
        d.root.keyframe_insert("location", frame=f); d.root.keyframe_insert("rotation_euler", frame=f)
        hat_on_obj(d.root, f, 0.95, off=(0, -2.0))
    sk = mk_skiff()
    for f in range(1, n + 1): float_on(sk, f, dp.x - 6, dp.y + 18, -0.2, draft=0.2, tilt=0.8)
    cs = our_crew(["bev", "toby", "dale", "kevin"])
    for k, c in cs.items(): c.root.parent = sk; lx, ly = SKLOC[k]; c.place((lx, ly, SKIFF_FLOOR), math.pi); salute_hold(c, 1, n)
    S.frame_set(1); hp = d.root.matrix_world @ Vector((0, -2, 0.5))
    cpath(n, hp + Vector((5, -14, 2.5)), hp + Vector((-2, 6, 1.5)), hp + Vector((4.5, -12.5, 2.6)), hp + Vector((-2, 6, 1.6)), 26, 28)
def p37(n):   # Dale lines up the shot of his life: one eye shut, tongue out (slow push)
    sea_shot("p37"); sk, cs, g = skiff_scene(n, at=Vector((120.0, -110.0, 0)), heading=0.5, names=["dale", "toby"])
    d = cs["dale"]
    for f in range(1, n + 1, 2): rpg_pose(d, f, up=0.08, head=(0.02 * math.sin(f / 3), 0, 0))
    d.set_face("smug", 1); hold(cs["toby"], 1, n, face="scared", arms=(0.4, 0.4))
    S.frame_set(1); h = d.head.matrix_world.translation
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); hh = head_world(d, f)
        cam2(f, boat_pt(sk, f, (6.8 - 1.4 * u, -5.5 + 1.0 * u, SKIFF_FLOOR + 4.6 * 1.1)), hh + Vector((0, 0, -0.1)), 32 + 10 * u)
def p38(n):   # Toby lunges, panicked: FWOOSH (whip-pan with the rocket)
    sea_shot("p38"); sk, cs, g = skiff_scene(n, at=Vector((120.0, -110.0, 0)), heading=0.5, names=["dale", "toby"])
    d = cs["dale"]; t = cs["toby"]; fire = int(n * 0.35)
    for f in range(1, n + 1, 2): rpg_pose(d, f, up=0.08)
    d.set_face("smug", 1); d.set_face("excited", fire)
    for f in range(1, n + 1, 2):
        u = min(1, f / fire); t.pose(f, arms=(1.6 * u + 0.3, 1.8 * u + 0.3), lean=0.35 * u, legs=(0.6 * u, -0.3 * u))
    t.set_face("scared", 1)
    S.frame_set(fire); tip = d.gun.matrix_world @ d.gun_tip; muzzle(tip, fire, 1.2)
    tgt = Vector((WALL_X, HULLY - 0.5, DECK_Z + 3))
    r = rocket(); fly_rocket(r, [tip, (tip + tgt) / 2 + Vector((0, 0, 6)), tgt], fire, fire + 40)
    for f in range(1, n + 1):
        S.frame_set(f); u = ease(max(0, f - fire) / max(1, n - fire))
        rp = r.matrix_world.translation.copy() if f >= fire else tip
        hd = head_world(t, f)
        cam2(f, boat_pt(sk, f, (2.0, -9.0, SKIFF_FLOOR + 5.0)), hd.lerp(rp, u), 26)
def p39(n):   # KA-BOOOOM: rocket slams the base of the tallest stack (CU on the base only)
    sea_shot("p39"); ship_shot("p39"); sea_center(WALL_X, -60)
    base = Vector((WALL_X, HULLY - 0.3, DECK_Z + 3.0)); hit = 4
    r = rocket(); fly_rocket(r, [base + Vector((-30, -40, 2)), base], 1, hit); vis(r, hit + 1, False)
    boom(base + Vector((0, -1.5, 0)), hit, 1.5)
    for o in WALL:
        h = Vector(o["home"])
        for f in range(1, n + 1):
            j = 0.25 * math.sin(f * 2.3 + h.z) if f >= hit else 0
            o.location = h + Vector((0, j * 0.3, 0)); o.keyframe_insert("location", frame=f)
    cpath(n, base + Vector((12, -42, 5)), base + Vector((0, 0, 6)), base + Vector((11, -40, 4.5)), base + Vector((0, 0, 6.5)), 26, 26, shake=0.0)
def p40(n):   # Dale lowers the smoking RPG: stunned, then proud
    sea_shot("p40"); sk, cs, g = skiff_scene(n, at=Vector((120.0, -110.0, 0)), heading=0.5, names=["dale"])
    d = cs["dale"]
    for f in range(1, n + 1, 2):
        u = min(1, f / (n * 0.5)); rpg_pose(d, f, up=-0.5 * u)
    d.set_face("shocked", 1); d.set_face("excited", int(n * 0.55))
    S.frame_set(1); tip = d.gun.matrix_world @ d.gun_tip
    smoke_trail([(f, tip + Vector((0.2 * math.sin(f), 0, 0.15 * f))) for f in range(1, n, 2)], 1, n, size=0.45)
    for f in range(1, n + 1):
        hh = head_world(d, f); cam2(f, boat_pt(sk, f, (7.5, -5.2, SKIFF_FLOOR + 5.0)), hh + Vector((0, 0, -0.4)), 34)
def wall_topple(f0, n, step=2, sea_y=HULLY - 12):
    """the container wall dominoes off the starboard side into the sea (top tiers first)"""
    order = sorted(WALL, key=lambda o: (-o["home"][2], o["home"][1]))
    out = []
    for i, o in enumerate(order):
        h = Vector(o["home"]); fs = f0 + (i // 5) * step + (i % 5) // 2
        land_y = sea_y - (h.z - DECK_Z) * 0.35 - (h.y + 13.2) * 0.3; dur = 14 + int((h.z - DECK_Z) / 7)
        for f in range(1, n + 1):
            if f < fs: o.location = h; o.rotation_euler = (0, 0, 0)
            else:
                u = min(1, (f - fs) / dur); uu = u * u
                o.location = Vector((h.x + 2 * math.sin(i), h.y + (land_y - h.y) * u, h.z + (-0.5 - h.z) * uu))
                o.rotation_euler = (-1.6 * u * (1 + 0.3 * math.sin(i)), 0.2 * math.sin(i) * u, 0.15 * math.cos(i) * u)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
        out.append((fs + dur, Vector((h.x + 2 * math.sin(i), land_y, 0.2))))
    return out
def p41(n):   # FIRST FULL REVEAL: the whole mega ship; the container wall starts to lean (extreme wide crane pull-back)
    sea_shot("p41"); ship_shot("p41"); sea_center(-20, -120)
    for o in WALL:
        h = Vector(o["home"])
        for f in range(1, n + 1):
            u = ease((f - 1) / (n - 1)); lean = 0.06 * u * (h.z - DECK_Z) / 40
            o.location = h + Vector((0, -(h.z - DECK_Z) * lean, 0)); o.rotation_euler = (-lean, 0, 0)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
    sk = mk_skiff()
    for f in range(1, n + 1): float_on(sk, f, 40, -110, 2.2, draft=0.2)
    cpath(n, (30, -70, 30), (WALL_X, HULLY, DECK_Z + 25), (-40, -260, 70), (-10, 0, 20), 24, 22)
def p42(n):   # containers domino into the ocean in a chain of giant splashes; the hat spins skyward through the spray
    sea_shot("p42"); ship_shot("p42"); sea_center(WALL_X, -70)
    lands = wall_topple(1, n + 30, step=1)
    for fl, p in lands:
        if fl <= n + 2: splash(p, fl, 2.2, n=14)
    a = Vector((WALL_X + 20, -80, 1)); b = Vector((WALL_X + 6, -60, 60))
    hat_fly(1, n, a, b, h=10, spins=3)
    cpath(n, (WALL_X + 30, -150, 18), (WALL_X, -35, 22), (WALL_X + 36, -146, 20), (WALL_X, -35, 20), 26, 26)
SWELLM = None
def swell_obj(loc):
    global SWELLM
    o = sphere("swell", loc, 1, WATER, coll=TEMP, seg=24)
    return o
def p43(n):   # a giant swell rises under the skiff; the crew screams with delight
    sea_shot("p43"); ship_shot("p43"); SEA_AMP[0] = 0.6
    at = Vector((WALL_X - 30, -70, 0)); sk, cs, g = skiff_scene(n, at=at, heading=math.pi / 2 + 0.25, names=["bev", "toby", "dale", "kevin"])
    sw = swell_obj(at + Vector((0, -6, -12)))
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); h = 14 * u
        sw.scale = (26, 30, 12 + h); sw.location = at + Vector((0, -6 + 10 * u, -12)); sw.keyframe_insert("scale", frame=f); sw.keyframe_insert("location", frame=f)
        sk.location = at + Vector((0, 10 * u, h + 0.3)); sk.rotation_euler = (0.25 * u, 0, math.pi / 2 + 0.25); sk.keyframe_insert("location", frame=f); sk.keyframe_insert("rotation_euler", frame=f)
    for k, c in cs.items(): hold(c, 1, n, face="excited", arms=(2.7, 2.7), arms_side=(0.4, 0.4))
    rnd = random.Random(5)
    for k in range(6): splash(at + Vector((rnd.uniform(-10, 10), rnd.uniform(-4, 10), 12)), 1 + k * 3, 1.0, n=10, crown=False)
    for f in range(1, n + 1):
        S.frame_set(f); p = sk.matrix_world.translation.copy()
        cam2(f, p + Vector((-30, -8, -3 + 3 * f / n)), p + Vector((0, 0, 1)), 22)
SKD = Vector((-62.0, -3.0, DECK_Z)); LBD = Vector((-34.0, 4.0, DECK_Z))
def p44(n):   # skiff AND lifeboat surf over the rail and skid to a stop on the deck; both crews tumble out still aiming
    deck_shot("p44", -48, -50); wall_reset()
    for o in WALL: vis(o, 1, False)
    sk = mk_skiff(); lb = mk_lifeboat(); stop = int(n * 0.55)
    for boat, dst, y0, hd in ((sk, SKD, -48.0, 0.15), (lb, LBD, -52.0, -0.1)):
        a = Vector((dst.x - 8, y0, 10)); top = Vector((dst.x - 4, HULLY, RAILZ + 7))
        for f in range(1, n + 1):
            if f <= stop:
                u = f / stop
                p = a.lerp(dst, u) + Vector((0, 0, 4 * 10 * u * (1 - u))) if u < 1 else dst
                boat.location = p; boat.rotation_euler = (0.25 * (1 - u), 0.1 * math.sin(u * 3), hd * (1 - u))
            else:
                boat.location = dst; boat.rotation_euler = (0, 0, 0)
            boat.keyframe_insert("location", frame=f); boat.keyframe_insert("rotation_euler", frame=f)
    splash(Vector((-48, HULLY - 4, 1.0)), 2, 2.4)
    cs = our_crew(["bev", "toby", "dale", "kevin"]); cg = cargo_crew(3)
    for i, (k, c) in enumerate(cs.items()):
        c.root.parent = sk; c.place(((4 - i * 3.5), 1.4 if i % 2 else -1.4, SKIFF_FLOOR), math.pi / 2)
        hold(c, 1, stop, face="excited", arms=(2.6, 2.6)); aim_hold(c, stop + 3, n, face="excited")
    for i, c in enumerate(cg):
        c.root.parent = lb; c.place((3 - i * 3, 1.2 if i % 2 else -1.2, lb["floor"]), -math.pi / 2)
        hold(c, 1, stop, face="scared", arms=(2.6, 2.6)); aim_hold(c, stop + 3, n, face="shocked")
    cpath(n, (-48, -60, DECK_Z + 4), (-48, -20, DECK_Z + 6), (-48, -40, DECK_Z + 9), (-48, 0, DECK_Z + 3), 22, 24)
def end_state(n, names=NAMES, cargo=4, face="determined", aim=True):
    """deck after the surf: skiff + lifeboat on deck, our crew by the skiff, cargo crew by the lifeboat, facing off"""
    for o in WALL: vis(o, 1, False)
    sk = mk_skiff(); sk.location = SKD; lb = mk_lifeboat(); lb.location = LBD; lb.rotation_euler = (0, 0, 0)
    cs = our_crew(names); cg = cargo_crew(cargo)
    pos = [(-60, -10.5), (-54.5, -11), (-49, -10.5), (-66, -11), (-43.5, -11), (-70.5, -10)]
    for (k, c), (x, y) in zip(cs.items(), pos):
        c.place((x, y, DECK_Z), math.pi - 0.15)
        if aim: (aim_hold(c, 1, n, face=face) if k != "dale" else [rpg_pose(c, f) for f in range(1, n + 1, 2)])
    for c, (x, y) in zip(cg, [(-50, 10.5), (-44, 11), (-38, 10.5), (-32, 11)]):
        c.place((x, y, DECK_Z), 0.15)
        if aim: aim_hold(c, 1, n, face=face)
    return sk, lb, cs, cg
def p45(n):   # the hat drifts down from the sky in a slow spin
    deck_shot("p45"); sk, lb, cs, cg = end_state(n, names=["toby", "bev"], cargo=0)
    t = cs["toby"]; S.frame_set(n); dst = head_world(t, n, t.hat_top) + Vector((0, 0, 3))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); p = dst + Vector((2.0 * math.sin(u * 5), 1.2 * math.cos(u * 4), 18 * (1 - u)))
        hat_key(f, p, (0.25 * math.sin(u * 8), 0.2 * math.cos(u * 6), u * 3), FIXED_HAT)
    for f in range(1, n + 1):
        S.frame_set(f); hp = HAT.matrix_world.translation.copy()
        cam2(f, Vector((dst.x + 3, dst.y - 14, DECK_Z + 4)), hp, 30)
def p46(n):   # onto ME: it lands on Toby's head; he looks up at the brim
    deck_shot("p46"); sk, lb, cs, cg = end_state(n, names=["toby", "bev", "kevin"], cargo=2)
    t = cs["toby"]; land = int(wt("p46", "me.") * FPS) + 2
    S.frame_set(land); dst = head_world(t, land, t.hat_top)
    for f in range(1, land + 1):
        u = f / land; hat_key(f, dst + Vector((0.4 * math.sin(u * 4), 0, 3 * (1 - u))), (0.1 * math.sin(u * 6), 0, 3 + u * 0.4), FIXED_HAT)
    hat_on(t, land, n)
    for f in range(land, n + 1, 2): t.pose(f, arms=(1.48, 1.56), arms_side=(-0.42, 0), head=(-0.35, 0, 0))
    t.set_face("shocked", land)
    S.frame_set(1); h = t.head.matrix_world.translation
    cpath(n, h + Vector((2.5, 9, 0.5)), h + Vector((0, 0, 0.8)), h + Vector((2.2, 8.2, 0.4)), h + Vector((0, 0, 0.8)), 32, 34)
def p47(n):   # Look at me. I'm the captain now. Deadpan into the lens, slow push-in to CU
    deck_shot("p47"); sk, lb, cs, cg = end_state(n, names=["toby", "bev", "dale"], cargo=2)
    t = cs["toby"]
    hold(t, 1, n, face="smug", arms=(0.15, 0.15)); hat_on(t, 1, n)
    S.frame_set(1); h = t.head.matrix_world.translation
    cpath(n, h + Vector((0, 9, 0.2)), h + Vector((0, 0, 0.3)), h + Vector((0, 4.8, 0.15)), h + Vector((0, 0, 0.35)), 34, 36)
def p48(n):   # First order: Everyone... stop shooting. Wide on both crews, still aiming
    deck_shot("p48"); sk, lb, cs, cg = end_state(n)
    t = cs["toby"]
    for f in range(1, n + 1, 2): t.pose(f, arms=(0.2, 1.6), arms_side=(0, 0.6), head=(0, 0, 0))
    t.set_face("talk", 1); t.set_face("determined", int(n * 0.7)); hat_on(t, 1, n)
    cpath(n, (-30, -40, DECK_Z + 14), (-50, 0, DECK_Z + 3), (-32, -36, DECK_Z + 13), (-50, 0, DECK_Z + 3), 22, 22)
def p49(n):   # It worked: every gun lowers at once; the Cook starts handing out sandwiches
    deck_shot("p49"); sk, lb, cs, cg = end_state(n, aim=False)
    lw = 4
    for c in list(cs.values()) + cg:
        aim_pose(c, 1); c.pose(lw, arms=(1.3, 1.4), arms_side=(-0.3, 0)); hold(c, lw + 3, n, face="happy", arms=(0.25, 0.3))
        c.set_face("determined", 1); c.set_face("happy", lw + 2)
    hat_on(cs["toby"], 1, n)
    ck = mk_cook(); ck.place((-47, -1, DECK_Z), 0.0); sandwich(ck, 1)
    for f in range(1, n + 1, 2): ck.pose(f, arms=(0.3, 1.4 + 0.3 * math.sin(f / 3)), head=(0, 0, 0.3 * math.sin(f / 5)))
    ck.set_face("excited", 1)
    cpath(n, (-49, -30, DECK_Z + 7), (-49, 0, DECK_Z + 3), (-49, -27, DECK_Z + 7), (-49, 0, DECK_Z + 3), 24, 24)
def p50(n):   # a gust lifts the hat off Toby, who grabs at air
    deck_shot("p50"); sk, lb, cs, cg = end_state(n, names=["toby"], cargo=0, aim=False)
    t = cs["toby"]; off = int(n * 0.3)
    hat_on(t, 1, off); S.frame_set(off); a = HAT.location.copy()
    hat_fly(off, n, a, a + Vector((6, 8, 9)), h=3, spins=1.2)
    for f in range(1, n + 1, 2):
        u = max(0, min(1, (f - off) / 6)); t.pose(f, arms=(0.2 + 2.6 * u, 0.2 + 2.8 * u), arms_side=(0, 0.2 * u), head=(-0.5 * u, 0, 0), legs=(0.3 * u, 0))
    t.set_face("smug", 1); t.set_face("shocked", off + 1)
    S.frame_set(1); h = t.head.matrix_world.translation
    cpath(n, h + Vector((1.5, 8.5, 0.3)), h + Vector((0, 0, 0.8)), h + Vector((1.5, 8, 0.8)), h + Vector((0, 0, 2.5)), 32, 30)
def p51(n):   # the gull snatches the hat mid-air, lands on the skiff's bow and puffs up; everyone salutes. Same framing as p01
    deck_shot("p51"); sk, lb, cs, cg = end_state(n, names=["toby", "bev"], cargo=0, aim=False)
    for c in cs.values(): c.place((c.root.location.x, c.root.location.y, DECK_Z), -math.pi / 2 + 0.2); salute_hold(c, 6, n)
    g = Gull(); perch = SKD + Vector((12.0, 0, 2.78)); land = int(n * 0.35)
    for f in range(1, n + 1):
        if f < land:
            u = f / land; p = perch + Vector((-8 * (1 - u), -6 * (1 - u), 7 * (1 - u) ** 2))
        else: p = perch
        g.root.location = p; g.root.rotation_euler = (0, 0, -math.pi / 2); g.root.keyframe_insert("location", frame=f); g.root.keyframe_insert("rotation_euler", frame=f)
    g.flap(1, land, speed=5, amp=1.0); g.fold(land + 1, 0.0); g.fold(n, 0.35)
    for f in range(1, n + 1): hat_on_obj(g.head, f, 0.52, sc=0.78)
    gp = lambda off: perch + Vector(off)
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); u2 = max(0, (f - land) / (n - land))
        cam2(f, gp((-7.5 + 2.0 * ease(u2), -2.6 + 0.8 * ease(u2), 1.4)), gp((0, 0, 3.3)), 40)

# ---------------------------------------------------------------- render loop
def track_json(n): return [None] * n
SHOTS = {k: v for k, v in list(globals().items()) if k.startswith("p") and k[1:3].isdigit() and callable(v)}
os.makedirs(OUT, exist_ok=True); os.makedirs(f"{E}/preview", exist_ok=True)
def reset_world():
    for o in [HAT, HOOK] + WALL:
        if o.animation_data: o.animation_data_clear()
    wall_reset(); HOOK.rotation_euler = (0, 0, 0)
    for o in WALL: o.hide_render = False
    hat_off(1); ship_on(False); SEA_AMP[0] = 1.0
for name in TL["shots"]:
    if ONLY and name not in ONLY: continue
    n = max(6, int(round(DUR[name] * FPS)))
    clear_temp(); reset_world(); S.frame_set(1)
    SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    if STILL:
        SF = float(os.environ.get("STILLF", "0.6")); S.frame_set(max(1, int(n * SF))); S.render.filepath = f"{E}/preview/{name}" + ("" if SF == 0.6 else f"_{int(SF*100)}") + ".png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d):
            if f.endswith(".png"): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
