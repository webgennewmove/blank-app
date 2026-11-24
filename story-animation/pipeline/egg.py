"""IN MY TOWN Ep1: 'Everyone steals eggs' (Steal An Egg parody). Builds on world.py's suburb + bedroom.
usage: python egg.py -- all|e01,e05 [still]"""
import sys, os, json, math, random
REAL_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = [sys.argv[0], "--", "none"]
exec(open("/home/claude/zara/world.py").read())
from mathutils import Vector, Quaternion
ONLY = set(REAL_ARGV[0].split(",")) if REAL_ARGV and REAL_ARGV[0] != "all" else None
exec(open("/home/claude/zara/eevee_patch.py").read())
STILL = len(REAL_ARGV) > 1 and REAL_ARGV[1] == "still"
E = "/home/claude/zara/egg"; OUT = f"{E}/frames"
S.render.resolution_x, S.render.resolution_y = 720, 1280
TL = json.load(open(f"{E}/timeline.json")); DUR = TL["dur"]; LEADS = TL["lead"]; WORDS = TL["words"]
random.seed(7)
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")

def text3d(body, loc, size, m, rot=(math.pi / 2, 0, 0), coll=None, extrude=0.05):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.font = FONTB; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m); return o

def F(t): return max(1, int(round(t * FPS)) + 1)
def wt(shot, word, k=0):
    """time (s) of the k-th occurrence of a word in a shot's VO"""
    hits = [a for w, a, b in WORDS[shot] if w.lower().strip(".,!?") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0

# ---------------------------------------------------------------- camera with roll (dutch angles)
def cam2(f, loc, at, lens=30, roll=0.0):
    CAM.location = loc; CAM.data.lens = lens
    q = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y")
    q = q @ Quaternion((0, 0, 1), roll)
    CAM.rotation_euler = q.to_euler()
    CAM.keyframe_insert("location", frame=f); CAM.keyframe_insert("rotation_euler", frame=f); CAM.data.keyframe_insert("lens", frame=f)
def cpath(n, a_loc, a_at, b_loc, b_at, la=30, lb=None, ra=0.0, rb=None, ease=True):
    for f in range(1, n + 1):
        u = (f - 1) / max(1, n - 1)
        if ease: u = u * u * (3 - 2 * u)
        cam2(f, Vector(a_loc).lerp(Vector(b_loc), u), Vector(a_at).lerp(Vector(b_at), u), la + ((lb or la) - la) * u, ra + ((rb if rb is not None else ra) - ra) * u)
def ctrack(n, obj, offset, look=(0, 0, 3.5), lens=24, roll=0.0):
    for f in range(1, n + 1):
        S.frame_set(f); p = obj.matrix_world.translation.copy()
        cam2(f, p + Vector(offset), p + Vector(look), lens, roll)

# ---------------------------------------------------------------- the reference look: Toby
TSKIN = (0.9, 0.6, 0.38); THAIR = (0.2, 0.085, 0.03); TGREEN = (0.13, 0.72, 0.09); TNAVY = (0.03, 0.05, 0.22)
def long_sleeves(col, skin):
    def f(c):
        cuff = mat(f"cuff{col}", tuple(v * 0.62 for v in col)); sh = mat(f"shirt_{col}", col, 0.6); sk = mat(f"skin_{skin}", skin, 0.5)
        for p in c.arms:
            for ch in list(p.children): bpy.data.objects.remove(ch, do_unlink=True)
            box("sleeve", (0, 0, -0.78), (0.98, 0.98, 1.72), sh, parent=p, bevel=0.2, coll=c.coll)
            box("cuff", (0, 0, -1.56), (1.01, 1.01, 0.2), cuff, parent=p, bevel=0.05, coll=c.coll)
            box("hand", (0, 0, -1.84), (0.88, 0.88, 0.44), sk, parent=p, bevel=0.16, coll=c.coll)
    return f
def hoodie(col):
    def f(c):
        m = mat(f"hood{col}", col); pk = mat(f"hoodpk{col}", tuple(v * 0.8 for v in col))
        box("hoodback", (0, 0.55, 1.95), (1.5, 0.45, 0.8), m, parent=c.hips, coll=c.coll, bevel=0.15)
        box("pocket", (0, -0.52, 0.5), (1.25, 0.08, 0.55), pk, parent=c.hips, coll=c.coll, bevel=0.03)
        for sx in (-0.25, 0.25): box("string", (sx, -0.54, 1.55), (0.07, 0.04, 0.6), mat("white", (1, 1, 1)), parent=c.hips, coll=c.coll)
    return f
def chunky_hair(col):
    def f(c):
        m = mat(f"hair_{col}", col, 0.8); dk = mat(f"hairdk_{col}", tuple(v * 0.7 for v in col), 0.8); h = c.head
        box("hcap", (0, 0.08, 0.6), (1.3, 1.24, 0.22), m, parent=h, bevel=0.08, coll=c.coll)
        box("hback", (0, 0.6, 0.25), (1.28, 0.14, 0.75), m, parent=h, bevel=0.05, coll=c.coll)
        for k, x in enumerate((-0.46, -0.15, 0.16, 0.46)):
            box("chunk", (x, -0.3 + 0.04 * (k % 2), 0.8 + 0.05 * (k % 2)), (0.36, 0.62, 0.42), m if k % 2 else dk,
                rot=(0.35, 0.12 * (k - 1.5), 0), parent=h, bevel=0.13, coll=c.coll)
        for k, x in enumerate((-0.32, 0.0, 0.32)):
            box("chunk2", (x, 0.28, 0.82), (0.4, 0.55, 0.36), dk if k % 2 else m, rot=(-0.2, 0, 0), parent=h, bevel=0.1, coll=c.coll)
        for sx in (-0.62, 0.62): box("side", (sx, 0.18, 0.3), (0.07, 0.85, 0.45), m, parent=h, coll=c.coll)
    return f
def combo(*fs):
    def f(c):
        for g in fs: g(c)
    return f
def mk_toby():
    return Char("toby", TEMP, TSKIN, TGREEN, TNAVY, hair="none", shoes=(0.95, 0.95, 0.95), scale=0.95,
                extra=combo(long_sleeves(TGREEN, TSKIN), hoodie(TGREEN), chunky_hair(THAIR)))
def mk_mom():
    return Char("mom", TEMP, TSKIN, (0.92, 0.22, 0.42), (0.12, 0.22, 0.55), hair="ponytail", hair_col=THAIR, scale=1.08,
                extra=long_sleeves((0.92, 0.22, 0.42), TSKIN))
def mk_teacher():
    return Char("teacher", TEMP, (0.42, 0.25, 0.14), (0.5, 0.18, 0.72), (0.2, 0.2, 0.26), hair="bun", hair_col=(0.06, 0.04, 0.03),
                shoes=(0.35, 0.12, 0.2), extra=glasses, scale=1.12)
def cop_extra(c):
    cap((0.02, 0.03, 0.12))(c)
    sphere("badge", (0.55, -0.55, 1.45), 1, mat("gold", (1, 0.75, 0.08), 0.3), coll=c.coll, parent=c.hips, scale=(0.2, 0.05, 0.24))
    box("belt", (0, 0, 0.12), (2.04, 1.04, 0.25), mat("belt", (0.02, 0.02, 0.02)), parent=c.hips, coll=c.coll)
    box("capbadge", (0, -0.69, 0.8), (0.25, 0.04, 0.25), mat("gold", (1, 0.75, 0.08), 0.3), parent=c.head, coll=c.coll)
def mk_cop(i=0):
    return Char(f"cop{i}", TEMP, [(0.36, 0.2, 0.11), (0.9, 0.62, 0.45)][i % 2], (0.05, 0.12, 0.42), (0.03, 0.05, 0.16), hair="short",
                hair_col=(0.05, 0.04, 0.03), shoes=(0.03, 0.03, 0.03), extra=cop_extra, scale=1.12)
def mayor_extra(c):
    blk = mat("tophat", (0.04, 0.04, 0.05))
    cyl("hatbrim", (0, 0, 0.66), 0.95, 0.08, blk, parent=c.head, coll=c.coll, verts=20)
    cyl("hattop", (0, 0, 1.25), 0.62, 1.15, blk, parent=c.head, coll=c.coll, verts=20)
    cyl("hatband", (0, 0, 0.82), 0.64, 0.18, mat("gold", (1, 0.75, 0.08), 0.3), parent=c.head, coll=c.coll, verts=20)
    box("stache", (0, -0.64, -0.12), (0.7, 0.05, 0.16), mat("stache", (0.6, 0.6, 0.62)), parent=c.head, coll=c.coll, bevel=0.03)
    box("sash", (0.2, -0.53, 1.0), (0.4, 0.06, 2.3), mat("sash", (0.85, 0.1, 0.15)), rot=(0, 0.6, 0), parent=c.hips, coll=c.coll)
def mk_mayor():
    return Char("mayor", TEMP, (0.95, 0.72, 0.55), (0.06, 0.06, 0.1), (0.06, 0.06, 0.1), hair="short", hair_col=(0.6, 0.6, 0.62),
                shoes=(0.02, 0.02, 0.02), extra=mayor_extra, scale=1.25)
CROWD = [((0.36, 0.2, 0.11), (1, 0.6, 0.05), (0.2, 0.3, 0.7), "afro"), ((0.9, 0.62, 0.45), (0.15, 0.5, 0.95), (0.9, 0.9, 0.9), "spiky"),
         ((0.55, 0.33, 0.18), (0.95, 0.85, 0.2), (0.15, 0.15, 0.2), "ponytail"), ((0.25, 0.14, 0.08), (0.6, 0.25, 0.9), (0.2, 0.2, 0.25), "fade"),
         ((0.95, 0.75, 0.6), (0.95, 0.35, 0.1), (0.25, 0.35, 0.3), "short")]
def mk_extra(i):
    s_, sh_, p_, h_ = CROWD[i % len(CROWD)]
    return Char(f"x{i}", TEMP, s_, sh_, p_, hair=h_, hair_col=[(0.05, 0.04, 0.03), (0.6, 0.35, 0.1)][i % 2], scale=random.Random(i).uniform(0.88, 1.1))

# ---------------------------------------------------------------- eggs
EGGCOLS = [(1, 0.55, 0.7), (0.45, 0.75, 1), (0.5, 0.92, 0.45), (0.75, 0.5, 1), (1, 0.62, 0.2), (0.98, 0.96, 0.9), (1, 0.9, 0.3)]
def mk_egg(coll, loc=(0, 0, 0), r=0.7, col=None, spots=True, parent=None, gold=False, seed=0):
    rnd = random.Random(seed); col = col or rnd.choice(EGGCOLS)
    root = empty("egg", loc, parent=parent, coll=coll)
    m = mat("goldegg", (1, 0.68, 0.04), 0.15) if gold else mat(f"egg{col}", col, 0.35)
    sphere("shell", (0, 0, r * 1.05), 1, m, coll=coll, parent=root, scale=(r * 0.82, r * 0.82, r * 1.05), seg=24)
    if spots and not gold:
        sm = mat(f"eggspot{col}", tuple(min(1, v * 0.6 + 0.35) for v in col), 0.4)
        for k in range(6):
            a = k / 6 * 6.28 + rnd.uniform(-0.3, 0.3); zz = rnd.uniform(0.6, 1.5) * r
            rr = r * 0.82 * math.sqrt(max(0.05, 1 - ((zz - r * 1.05) / (r * 1.05)) ** 2))
            sphere("spot", (math.cos(a) * rr, math.sin(a) * rr, zz), 1, sm, coll=coll, parent=root, scale=(r * 0.16, r * 0.16, r * 0.16), seg=8)
    if gold:
        sphere("glint", (-r * 0.3, -r * 0.62, r * 1.45), 1, mat("white", (1, 1, 1)), coll=coll, parent=root, scale=(r * 0.12, r * 0.06, r * 0.2), seg=8)
        sphere("band", (0, 0, r * 1.05), 1, mat("goldband", (0.85, 0.3, 0.02), 0.2), coll=coll, parent=root, scale=(r * 0.835, r * 0.835, r * 0.12), seg=24)
    return root
def cracks(egg, r, coll, front=-1, n=7, reveal=None):
    """zigzag crack across the egg's front; returns crack objects (optionally hidden until frame reveal)"""
    out = []; m = mat("crack", (0.04, 0.03, 0.03)); x, z = -r * 0.55, r * 1.15
    for k in range(n):
        x2 = x + r * 1.1 / n; z2 = r * 1.15 + (0.16 * r if k % 2 else -0.16 * r)
        ln = math.hypot(x2 - x, z2 - z); ang = math.atan2(z2 - z, x2 - x)
        o = box("crack", ((x + x2) / 2, front * r * 0.81, (z + z2) / 2), (ln + 0.02, 0.03, 0.045 * r + 0.01), m, rot=(0, -ang, 0), parent=egg, coll=coll)
        out.append(o); x, z = x2, z2
    if reveal:
        for o in out:
            o.hide_render = True; o.keyframe_insert("hide_render", frame=1); o.hide_render = False; o.keyframe_insert("hide_render", frame=reveal)
    return out
def wobble(obj, f0, f1, amp=0.15, speed=18, grow=False):
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); a = amp * ((0.3 + u) if grow else 1)
        obj.rotation_euler = (a * 0.4 * math.sin(f * speed / 24 * 1.3), a * math.sin(f * speed / 24), 0); obj.keyframe_insert("rotation_euler", frame=f)

def hold(c, f0, f1, mode="hug"):
    for f in range(f0, f1 + 1):
        for i, a in enumerate(c.arms):
            sd = 1 if i == 0 else -1
            a.rotation_euler = (-1.2, -0.22 * sd, 0) if mode == "hug" else (-2.95, 0.12 * sd, 0)
            a.keyframe_insert("rotation_euler", frame=f)
def carry(c, mode="hug", r=0.7, gold=False, seed=0):
    loc = (0, -1.45, 0.45) if mode == "hug" else (0, 0.1, 3.55)
    return mk_egg(TEMP, loc, r, parent=c.hips, gold=gold, seed=seed)
def talk(c, shot, base="happy", t0=0, t1=99):
    for w, a, b in WORDS[shot]:
        if t0 <= a < t1:
            c.set_face("talk", F(a)); c.set_face(base, F(a) + max(2, int((b - a) * FPS * 0.7)))

# ---------------------------------------------------------------- set dressing: egg "bases" on every lawn, mansion, egg mountain
DRESS = collection("eggdress", WORLD)
for (side, y), (hx, hy) in HOUSES.items():
    if abs(hy) > 150: continue
    fx_ = hx - side * 6.4
    for k in range(random.randint(3, 7)):
        sphere("lawnegg", (fx_ + random.uniform(-0.5, 0.5), hy - 5 + random.uniform(-1.2, 1.2) + (k % 3) * 0.9, 0.55), 1, mat(f"egg{EGGCOLS[k % 7]}", EGGCOLS[k % 7], 0.35),
               coll=DRESS, scale=(0.42, 0.42, 0.55), seg=12)
TOBY_HOME = HOUSES[(1, 0)]   # (15.5, 4) front faces -x
PED = (9.0, -2.3, 0)
box("pedestal", (PED[0], PED[1], 0.45), (1.3, 1.3, 0.9), mat("ped", (0.96, 0.96, 0.96)), coll=DRESS, bevel=0.08)
box("pedtop", (PED[0], PED[1], 0.93), (1.45, 1.45, 0.1), mat("pedtrim", (0.2, 0.75, 0.25)), coll=DRESS, bevel=0.03)
TINY = mk_egg(DRESS, (PED[0], PED[1], 0.98), 0.28, col=(0.92, 0.88, 0.78), seed=3)
cracks(TINY, 0.28, DRESS, front=-1, n=5)
TINY.rotation_euler = (0, 0.25, 0)

MAN = Vector((0, 236, 0)); MCOL = collection("mansion", WORLD)
def MP(x, y, z): return (MAN.x + x, MAN.y + y, MAN.z + z)
mw = mat("manwall", (0.98, 0.95, 0.88)); gold_m = mat("gold", (1, 0.75, 0.08), 0.3); mtrim = mat("mantrim", (0.75, 0.15, 0.2))
box("plaza", MP(0, -16, 0.06), (44, 30, 0.12), mat("plaza", (0.85, 0.82, 0.76)), coll=MCOL)
box("mbody", MP(0, 0, 6.5), (30, 14, 13), mw, coll=MCOL)
box("mroof", MP(0, 0, 13.2), (31.5, 15.5, 0.6), mtrim, coll=MCOL, bevel=0.1)
for x in (-15.2, 15.2):
    box("parapet", MP(x, 0, 14.0), (0.6, 15.5, 1.2), mw, coll=MCOL)
box("parapetf", MP(0, -7.5, 14.0), (31, 0.6, 1.2), mw, coll=MCOL)
box("roofped", MP(0, -1, 14.1), (3.2, 3.2, 1.4), gold_m, coll=MCOL, bevel=0.15)
GOLDEN = mk_egg(MCOL, MP(0, -1, 14.8), 1.5, gold=True)
for k, x in enumerate((-10, -6, -2, 2, 6, 10)):
    cyl("column", MP(x, -8.2, 5.5), 0.7, 11, mw, coll=MCOL, verts=14)
    box("colcap", MP(x, -8.2, 11.2), (1.9, 1.9, 0.5), mw, coll=MCOL)
box("portico", MP(0, -8.3, 11.8), (24, 2.6, 1.0), mw, coll=MCOL)
box("mdoor", MP(0, -7.05, 2.6), (3.6, 0.2, 5.2), mtrim, coll=MCOL, bevel=0.05)
sphere("knob", MP(1.2, -7.2, 2.6), 0.18, gold_m, coll=MCOL)
for x in (-12, -6.5, 6.5, 12):
    for z in (3.5, 9):
        box("mwin", MP(x, -7.05, z), (2.6, 0.15, 3.0), mat("glass", (0.55, 0.8, 0.98)), coll=MCOL)
        box("mwinf", MP(x, -7.0, z), (3.0, 0.1, 3.4), gold_m, coll=MCOL)
for k in range(3): box("mstep", MP(0, -9.8 - k * 0.8, 0.2 + (2 - k) * 0.3), (10, 1.0, 0.4 + (2 - k) * 0.6), mw, coll=MCOL)
box("msign", MP(0, -9.65, 12.0), (9, 0.2, 1.4), gold_m, coll=MCOL)
text3d("THE MAYOR", MP(0, -9.8, 12.0), 0.95, mat("signtxt", (0.6, 0.05, 0.1)), coll=MCOL, extrude=0.03)
MOUNT_C = Vector(MP(0, -21, 0))
MOUNT = collection("mountain", WORLD); _ec = [mat(f"egg{c}", c, 0.35) for c in EGGCOLS]
for i in range(420):
    a = random.uniform(0, 6.28); rr = 7.5 * math.sqrt(random.random()); h = 6.5 * (1 - rr / 7.5) ** 1.1
    sphere("pile", MOUNT_C + Vector((math.cos(a) * rr, math.sin(a) * rr, random.uniform(0, h) + 0.5)), 1, random.choice(_ec), coll=MOUNT,
           scale=(0.55, 0.55, 0.7), seg=12)
MOUNT_TOP = MOUNT_C + Vector((0, 0, 6.9))

# bedroom: strip the birthday props, add a door
for o in ROOM.objects:
    if o.name.split(".")[0] in ("balloon", "bstring", "cake", "candle", "flame", "flag", "desk"): o.hide_render = True
box("rdoor", R(-7.75, -3.5, 3.0), (0.25, 3.0, 6.0), mat("rdoor", (0.6, 0.32, 0.15)), coll=ROOM, bevel=0.05)
box("rdoorf", R(-7.8, -3.5, 3.1), (0.18, 3.5, 6.4), M["trim"], coll=ROOM)
sphere("rknob", R(-7.55, -2.3, 3.0), 0.16, gold_m, coll=ROOM)

def show_set(town=True, room=False, mansion=True, mount=True):
    WORLD.hide_render = not town; ROOM.hide_render = not room
    MCOL.hide_render = not mansion; MOUNT.hide_render = not mount

# ---------------------------------------------------------------- shots
def e01(n):   # hook: low angle, Toby sprints at camera hugging an egg; town steals eggs behind him
    show_set()
    t = mk_toby(); t.set_face("excited", 1); t.walk(1, n, (0.5, 16, 0), (0.5, -1, 0), run=True); hold(t, 1, n); carry(t, seed=1)
    ev = F(wt("e01", "everyone!")); t.set_face("laugh", ev)
    m = mk_mom(); m.walk(1, n, (-9, 10, 0.2), (4, 22, 0.2), run=True); hold(m, 1, n, "up"); carry(m, "up", seed=4); m.set_face("excited", 1)
    k = mk_extra(0); k.walk(1, n, (8, 26, 0), (-6, 18, 0), run=True); hold(k, 1, n); carry(k, seed=5); k.set_face("laugh", 1)
    k2 = mk_extra(1); k2.walk(1, n, (-7, 34, 0.2), (7, 30, 0.2), run=True); hold(k2, 1, n, "up"); carry(k2, "up", seed=6); k2.set_face("excited", 1)
    ctrack(n, t.root, (1.5, -7.8, 2.6), (-0.3, 0, 3.9), 23, -0.08)
def e02(n):   # mom sneaks off a neighbour's lawn with an egg, glances at camera
    show_set()
    m = mk_mom(); m.set_face("smug", 1)
    a, b = Vector((-8.8, 0.5, 0.2)), Vector((-7.6, -5.0, 0.2))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); s = math.sin(f / 24 * 2 * math.pi * 1.4)
        m.move(f, a.lerp(b, u), math.atan2(b.y - a.y, b.x - a.x) + math.pi / 2)
        m.pose(f, arms=(1.2, 1.2), arms_side=(-0.22, -0.22), legs=(0.45 * s, -0.45 * s), hips_z=1.75 + 0.06 * abs(s), lean=0.3,
               head=(-0.1, 0, 0.45 * min(1, u * 2.5)))
    carry(m, seed=8); m.set_face("blink", int(n * 0.55)); m.set_face("smug", int(n * 0.55) + 3)
    cpath(n, (-1.0, -10.5, 4.6), (-8.6, -4.0, 4.1), (-0.8, -8.0, 4.4), (-8.2, -1.5, 4.0), 24, 26, 0.06, 0.1)
def e03(n):   # teacher wobbles down the sidewalk with a tower of eggs
    show_set()
    t = mk_teacher(); t.walk(1, n, (6.5, -1, 0.2), (6.5, -8, 0.2), bounce=0.6); hold(t, 1, n); t.set_face("smug", 1)
    tower = empty("tower", (0, -1.35, 0.7), parent=t.hips, coll=TEMP)
    for k in range(5): mk_egg(TEMP, (0.05 * math.sin(k * 2), 0, k * 1.0), 0.52, parent=tower, seed=20 + k)
    wobble(tower, 1, n, 0.12, 9)
    t.set_face("blink", int(n * 0.6)); t.set_face("smug", int(n * 0.6) + 3)
    cpath(n, (3.2, -16, 3.8), (6.5, -4, 5.2), (3.8, -15, 4.2), (6.5, -6, 5.6), 30, 30, 0.0, -0.06)
def e04(n):   # cops sprint past with stolen eggs
    show_set()
    for i, (x, dl) in enumerate([(0, 0), (-3.2, 0.45)]):
        c = mk_cop(i); c.walk(1, n, (-12 - dl * 6, -6 + x, 0), (14 - dl * 6, -6 + x, 0), run=True); c.set_face("laugh" if i == 0 else "excited", 1)
        hold(c, 1, n, "hug" if i == 0 else "up"); carry(c, "hug" if i == 0 else "up", seed=30 + i)
    cpath(n, (-3, -21, 2.6), (-3, -6, 5.6), (5, -21, 2.6), (5, -6, 5.6), 24, 24, 0.12, 0.12, ease=False)
def e05(n):   # the mayor on a mountain of eggs; an endless spiral of eggs rains onto it (hypnotic), camera orbits up
    show_set(); GOLDEN.hide_render = True; GOLDEN.keyframe_insert("hide_render", frame=1)
    for ch in GOLDEN.children: ch.hide_render = True
    my = mk_mayor(); my.place(MOUNT_TOP - Vector((0, 0, 1.4)), 0.0); my.set_face("smug", 1); my.dance(1, n, 1, speed=0.8)
    my.root["hz"] = 4.0; TRACK.append(my.root)
    for k in range(3):
        e = mk_extra(k + 2); e.place(MOUNT_C + Vector((-8 + k * 8, -9.5, 0.12)), math.pi); e.set_face("shocked", 1); e.idle(1, n, 0.5, base_face="shocked", blink=False)
    NR, CYC = 72, 1.6 * FPS
    for k in range(NR):
        o = sphere("rain", (0, 0, 0), 1, _ec[k % len(_ec)], coll=TEMP, scale=(0.5, 0.5, 0.65), seg=12)
        for f in range(1, n + 1):
            u = (k / NR + f / CYC) % 1.0; r = 1.2 + 8.5 * (1 - u); a = k * 2.399 + u * 6.28 * 1.25
            o.location = MOUNT_C + Vector((math.cos(a) * r, math.sin(a) * r, 7.0 + 20 * (1 - u) ** 1.3))
            o.rotation_euler = (u * 9 + k, u * 6, 0)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); u = u * u * (3 - 2 * u); a = -1.95 + 0.95 * u; rr = 17 + 7 * u
        cam2(f, MOUNT_C + Vector((math.cos(a) * rr, math.sin(a) * rr, 2.0 + 12 * u)), MOUNT_C + Vector((0, 0, 6.5 + 2.5 * u)), 22, -0.05 * u)
def e06a(n):  # "And me? I had one." Toby beside his pedestal
    show_set()
    t = mk_toby(); t.place((PED[0] - 0.2, PED[1] - 2.4, 0.2), -1.0); t.idle(1, n, 0.8, base_face="happy", talk=True)
    for f in range(int(n * 0.45), n + 1):
        t.arms[1].rotation_euler = (-1.3, -0.5, 0); t.arms[1].keyframe_insert("rotation_euler", frame=f)
    talk(t, "e06a", "happy"); t.set_face("sad", F(wt("e06a", "one.")) + 4)
    cpath(n, (3.0, -12, 3.4), (8.3, -3.6, 2.8), (4.0, -10.5, 3.0), (8.5, -3.4, 2.6), 30, 34)
def e06b(n):  # macro push on the tiny cracked egg
    show_set()
    t = mk_toby(); t.place((PED[0] + 0.6, PED[1] + 2.4, 0.2), -2.2); t.set_face("sad", 1); t.idle(1, n, 0.3, base_face="sad", blink=False)
    wobble(TINY, 1, n, 0.08, 6)
    cpath(n, (PED[0] - 3.2, PED[1] - 2.6, 1.8), (PED[0], PED[1], 1.25), (PED[0] - 1.7, PED[1] - 1.3, 1.45), (PED[0], PED[1], 1.25), 40, 50)
def e07(n):   # night. Over Toby's shoulder: the mansion at the end of the street
    show_set()
    t = mk_toby(); t.place((1.0, 150, 0), math.pi); t.idle(1, n, 0.3, base_face="determined", blink=False); t.set_face("determined", 1)
    cpath(n, (2.6, 141, 4.6), (0.5, MAN.y, 12), (2.2, 144, 4.8), (0.2, MAN.y, 13), 30, 36)
def e08(n):   # the golden egg on the mayor's roof, crane up and push in
    show_set(mount=False)
    wobble(GOLDEN, 1, n, 0.05, 5); GOLDEN["hz"] = 1.6; TRACK.append(GOLDEN)
    g = F(wt("e08", "golden"))
    for f in range(1, n + 1):
        GOLDEN.rotation_euler.z = 0.6 * math.sin(f / 30); GOLDEN.keyframe_insert("rotation_euler", index=2, frame=f)
    cpath(n, (6, MAN.y - 32, 6), (0, MAN.y - 1, 15.8), (2.5, MAN.y - 12.5, 18.8), (0, MAN.y - 1, 16.4), 28, 40, 0.05, -0.04)
def e09(n):   # rule number one, whispered. tight close-up, nervous glances
    show_set()
    t = mk_toby(); t.place((1.0, 150, 0), 0.0); t.set_face("scared", 1)
    for f in range(1, n + 1):
        tt = f / 24
        t.pose(f, arms=(0.2, 0.2), arms_side=(0.05, 0.05), head=(0.05, 0, 0.45 * math.sin(tt * 2.6) * (1 if tt < 2.3 else 0.15)), hips_z=2.0 + 0.02 * math.sin(tt * 3))
    talk(t, "e09", "scared"); t.set_face("determined", F(wt("e09", "never")))
    talk(t, "e09", "determined", wt("e09", "never"))
    cpath(n, (1.2, 142.8, 4.8), (1.0, 150, 4.7), (1.1, 144.8, 4.75), (1.0, 150, 4.7), 40, 52, 0.0, 0.07)
def e10(n):   # on the roof: smug look to camera, then he touches it
    show_set(mount=False)
    t = mk_toby(); x0 = MAN.x + 3.2; y0 = MAN.y - 2.0; t.place((x0, y0, 13.5), 0.9); t.set_face("smug", 1)
    tt = F(wt("e10", "touched"))
    t.idle(1, tt - 4, 0.6, base_face="smug", talk=False)
    talk(t, "e10", "smug", 0, wt("e10", "touched"))
    for f in range(tt - 3, n + 1):
        u = min(1, (f - tt + 3) / 4)
        t.pose(f, arms=(0.1, 1.5 * u), arms_side=(0.1, 0.25), head=(0.15, 0, 0.7 * u), hips_z=2.0, lean=0.1 * u, twist=0.5 * u)
    t.set_face("excited", tt); wobble(GOLDEN, tt, n, 0.12, 22); GOLDEN["hz"] = 1.6; TRACK.append(GOLDEN)
    cpath(n, (MAN.x + 1.0, MAN.y - 13.5, 17.6), (MAN.x + 1.8, MAN.y - 1.5, 17.2), (MAN.x + 1.3, MAN.y - 12.0, 17.4), (MAN.x + 1.8, MAN.y - 1.5, 17.2), 28, 31, 0.04, 0.04)
def e11(n):   # RUN!! he leaps off the roof with the golden egg, worm's-eye
    show_set(mount=False)
    GOLDEN.hide_render = True
    for ch in GOLDEN.children: ch.hide_render = True
    t = mk_toby(); t.set_face("excited", 1)
    t.jump(1, n, height=2.5, start=MP(2, -7.0, 13.5), end=MP(3, -16, 0.2), cheer=True)
    carry(t, "up", r=1.1, gold=True)
    cpath(n, MP(6, -24, 0.8), MP(2, -9, 10), MP(6.5, -26, 1.0), MP(3, -14, 5), 18, 20, -0.15, -0.2)
def chaser(c, n, a, b, face="determined", grab=True):
    c.walk(1, n, a, b, run=True); c.set_face(face, 1)
    if grab:
        for f in range(1, n + 1):
            s = math.sin(f / 24 * 2 * math.pi * 2.6)
            for i, arm in enumerate(c.arms):
                arm.rotation_euler = (-1.55 - 0.25 * s * (1 if i else -1), 0.1 * (1 if i == 0 else -1), 0); arm.keyframe_insert("rotation_euler", frame=f)
def e12a(n):
    show_set(); m = mk_mom(); chaser(m, n, (0.5, 40, 0), (0.5, 22, 0))
    for k in range(3): chaser(mk_extra(k), n, (-3 + k * 3.5, 52 + k * 3, 0), (-3 + k * 3.5, 34 + k * 3, 0), "excited")
    ctrack(n, m.root, (1.5, -8.5, 1.4), (0, 0, 4.4), 24, -0.1)
def e12b(n):
    show_set(); t = mk_teacher(); chaser(t, n, (-1.5, 70, 0), (-1.5, 52, 0))
    for k in range(3): chaser(mk_extra(k + 3), n, (1.5 + k * 2.6, 80 + k * 2, 0), (1.5 + k * 2.6, 62 + k * 2, 0), "excited")
    ctrack(n, t.root, (-1.8, -8.5, 1.3), (0, 0, 4.6), 24, 0.1)
def e12c(n):  # side tracking: Toby with the golden egg, the whole town behind him
    show_set()
    t = mk_toby(); t.walk(1, n, (0.5, 100, 0), (0.5, 80, 0), run=True); hold(t, 1, n, "up"); carry(t, "up", r=1.1, gold=True); t.set_face("excited", 1)
    t.set_face("scared", F(wt("e12c", "definitely")))
    lineup = [mk_cop(0), mk_cop(1), mk_mom(), mk_teacher(), mk_mayor()]
    for i, c in enumerate(lineup):
        dx = [-1.5, 2.2, -3.5, 3.6, 0.3][i]; dy = 4.5 + i * 1.7
        chaser(c, n, (0.5 + dx, 100 + dy, 0), (0.5 + dx, 80 + dy, 0))
    # hypnotic: endless marching columns of townsfolk pouring down the street behind them
    for k in range(30):
        col, row = k % 3, k // 3
        x0 = 0.5 + (col - 1) * 3.2; y0 = 100 + 14 + row * 3.1 + (col % 2) * 1.5
        chaser(mk_extra(k), n, (x0, y0, 0), (x0, y0 - 20, 0), "excited" if k % 2 else "determined")
    ctrack(n, t.root, (1.8, -10.5, 7.0), (-0.3, 9, 2.2), 24, 0.04)
def e13(n):   # home: back against the door, then the egg on the rug starts to crack
    show_set(town=False, room=True, mansion=False, mount=False)
    t = mk_toby(); t.place(R(-6.6, -3.5, 0), math.pi / 2); t.set_face("scared", 1)
    sl = F(wt("e13", "slammed"))
    for f in range(1, n + 1):
        tt = f / 24; pant = math.sin(tt * 14) * 0.04
        t.pose(f, arms=(0.1, 0.1), arms_side=(1.0, 1.0), head=(-0.2 + pant, 0, 0), hips_z=2.0 + pant, lean=-0.12)
    t.set_face("shocked", F(wt("e13", "crack.")))
    egg = mk_egg(TEMP, R(1.0, -1.5, 0.05), 1.1, gold=True)
    egg["hz"] = 1.15; TRACK.append(egg)
    cr = F(wt("e13", "crack.")); cracks(egg, 1.1, TEMP, front=-1, n=7, reveal=cr); wobble(egg, cr - 6, n, 0.12, 24, grow=True)
    p = F(wt("e13", "put"))
    for f in range(1, n + 1):
        u = 0 if f < p else min(1, (f - p) / 12); u = u * u * (3 - 2 * u)
        cam2(f, Vector(R(-1.5, -12, 4.5)).lerp(Vector(R(1.3, -7.5, 2.6)), u), Vector(R(-6.4, -3.5, 4.2)).lerp(Vector(R(1.0, -1.5, 1.2)), u), 26 + 10 * u)
def e14(n):   # the whole town frozen in perfect rings around Toby's house; slow spiral up to overhead (hypnotic)
    show_set()
    hx, hy = TOBY_HOME; C = Vector((hx - 6.6, hy, 0))
    named = [mk_mayor, lambda: mk_cop(0), lambda: mk_cop(1), mk_mom, mk_teacher]; i = 0
    for ring, r in enumerate((5.0, 8.0, 11.0, 14.0)):
        cnt = int(r * math.pi / 2.4)
        for j in range(cnt):
            a = math.pi / 2 + math.pi * (j + 0.5) / cnt
            p = C + Vector((math.cos(a) * r, math.sin(a) * r, 0.0))
            c = named[i]() if i < len(named) else mk_extra(i)
            d = C - p; c.place(p, math.atan2(d.y, d.x) + math.pi / 2); c.set_face("shocked", 1)
            c.pose(1, arms=(0.25, 0.25), arms_side=(0.12, 0.12), head=(-0.05, 0, 0)); i += 1
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); u = u * u * (3 - 2 * u); a = -2.5 + 1.1 * u; rr = 21 * (1 - u) + 3.5
        cam2(f, C + Vector((math.cos(a) * rr, math.sin(a) * rr, 9 + 27 * u)), C + Vector((-4.5 * (1 - u), 0, 2)), 26, 0.9 * u)
def e15(n):   # the hatch: low behind the shaking egg, Toby's face lit by it
    show_set(town=False, room=True, mansion=False, mount=False)
    t = mk_toby(); t.place(R(1.0, 2.2, 0), 0.0); t.set_face("scared", 1)
    for f in range(1, n + 1):
        tt = f / 24; tr = 0.03 * math.sin(tt * 30)
        t.pose(f, arms=(0.9, 0.9), arms_side=(0.5, 0.5), legs=(1.2, 1.2), hips_z=1.25 + tr, lean=-0.05, head=(-0.12 + tr, 0, 0))
    nt = F(wt("e15", "not")); t.set_face("shocked", nt)
    egg = mk_egg(TEMP, R(1.0, -1.0, 0.05), 1.1, gold=True); cracks(egg, 1.1, TEMP, front=1, n=7); cracks(egg, 1.1, TEMP, front=-1, n=7)
    wobble(egg, 1, nt, 0.18, 26, grow=True); egg["hz"] = 1.15; TRACK.append(egg)
    cpath(n, R(2.0, -6.8, 2.7), R(1.0, 1.6, 3.3), R(1.6, -5.6, 2.9), R(1.0, 1.8, 3.5), 26, 32, 0.06, 0.0)

TRACK = []
def track_json(n):
    from bpy_extras.object_utils import world_to_camera_view
    out = []
    for f in range(1, n + 1):
        S.frame_set(f)
        if not TRACK: out.append(None); continue
        o = TRACK[0]; p = o.matrix_world @ Vector((0, 0, o.get("hz", 1.0)))
        v = world_to_camera_view(S, CAM, p); out.append((round(v.x, 4), round(1 - v.y, 4), round(v.z, 2)))
    return out

SHOTS = {k: v for k, v in list(globals().items()) if k.startswith("e") and k[1:3].isdigit() and callable(v)}
os.makedirs(OUT, exist_ok=True)
for name in TL["shots"]:
    if ONLY and name not in ONLY: continue
    n = max(10, int(round(DUR[name] * FPS)))
    clear_temp(); S.frame_set(1)
    for o in [GOLDEN] + list(GOLDEN.children) + [TINY]:
        if o.animation_data: o.animation_data_clear()
        o.hide_render = False
    GOLDEN.rotation_euler = (0, 0, 0); TINY.rotation_euler = (0, 0.25, 0)
    TRACK.clear(); SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    json.dump(track_json(n), open(f"{d}/track.json", "w"))
    if STILL:
        S.frame_set(int(n * 0.6)); S.render.filepath = f"{E}/preview/{name}.png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
