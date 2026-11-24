"""ON MY BLOCK Ep1: 'Everybody got motion... except me'. YN cast on the hood block (hood.py), EEVEE.
usage: EEVEE=1 python block.py -- all|b01,b05 [still]"""
import sys, os, json, math, random
REAL_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = [sys.argv[0], "--", "none"]
os.environ["HOOD"] = "1"
exec(open("/home/claude/zara/world.py").read())
from mathutils import Vector, Quaternion
ONLY = set(REAL_ARGV[0].split(",")) if REAL_ARGV and REAL_ARGV[0] != "all" else None
exec(open("/home/claude/zara/eevee_patch.py").read())
STILL = len(REAL_ARGV) > 1 and REAL_ARGV[1] == "still"
E = "/home/claude/zara/block"; OUT = f"{E}/frames"
S.render.resolution_x, S.render.resolution_y = 720, 1280
TL = json.load(open(f"{E}/timeline.json")); DUR = TL["dur"]; LEADS = TL["lead"]; WORDS = TL["words"]
random.seed(5)
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")

def text3d(body, loc, size, m, rot=(math.pi / 2, 0, 0), coll=None, extrude=0.05, parent=None):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.font = FONTB; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    o.data.materials.append(m); return o

exec(open("/home/claude/zara/hood.py").read())
ROOM.hide_render = True
for o in list(HOODC.objects):
    if o.name.split(".")[0] in ("stt", "stl", "treepit") and o.location.x > 0 and (abs(o.location.y + 3) < 1.5 or abs(o.location.y + 21) < 1.5): bpy.data.objects.remove(o, do_unlink=True)

def F(t): return max(1, int(round(t * FPS)) + 1)
def wt(shot, word, k=0):
    hits = [a for w, a, b in WORDS[shot] if w.lower().strip(".,!?") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0

# ---------------------------------------------------------------- camera (dutch roll capable)
def cam2(f, loc, at, lens=30, roll=0.0):
    CAM.location = loc; CAM.data.lens = lens
    q = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y") @ Quaternion((0, 0, 1), roll)
    CAM.rotation_euler = q.to_euler()
    CAM.keyframe_insert("location", frame=f); CAM.keyframe_insert("rotation_euler", frame=f); CAM.data.keyframe_insert("lens", frame=f)
def ease(u): return u * u * (3 - 2 * u)
def cpath(n, a_loc, a_at, b_loc, b_at, la=30, lb=None, ra=0.0, rb=None, f0=1, f1=None, smooth=True):
    f1 = f1 or n
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); u = ease(u) if smooth else u
        cam2(f, Vector(a_loc).lerp(Vector(b_loc), u), Vector(a_at).lerp(Vector(b_at), u), la + ((lb or la) - la) * u,
             ra + ((rb if rb is not None else ra) - ra) * u)
def ctrack(n, obj, offset, look=(0, 0, 3.5), lens=24, roll=0.0, shake=0.0):
    for f in range(1, n + 1):
        S.frame_set(f); p = obj.matrix_world.translation.copy()
        j = Vector((math.sin(f * 1.7), 0, math.cos(f * 2.3))) * shake
        cam2(f, p + Vector(offset) + j, p + Vector(look), lens, roll + 0.03 * shake * math.sin(f * 1.1) / max(shake, 1e-6) * (shake > 0))

# ---------------------------------------------------------------- wardrobe
GOLD = mat("gold", (1, 0.75, 0.08), 0.25)
def combo(*fs):
    def f(c):
        for g in fs: g(c)
    return f
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
def durag(col):
    def f(c):
        m = mat(f"durag{col}", col, 0.3); h = c.head
        box("durag", (0, 0.03, 0.47), (1.31, 1.31, 0.5), m, parent=h, bevel=0.2, coll=c.coll)
        box("dutail", (0.12, 0.68, -0.35), (0.34, 0.07, 1.3), m, rot=(-0.12, 0, 0.05), parent=h, coll=c.coll, bevel=0.03)
        box("dutail2", (-0.14, 0.7, -0.3), (0.3, 0.07, 1.15), m, rot=(-0.1, 0, -0.08), parent=h, coll=c.coll, bevel=0.03)
        box("duseam", (0, -0.1, 0.72), (0.08, 1.1, 0.05), mat(f"dus{col}", tuple(v * 0.7 for v in col)), parent=h, coll=c.coll)
    return f
def shades(c):
    m = mat("shades", (0.02, 0.02, 0.03), 0.1)
    box("shades", (0, -0.66, 0.1), (1.12, 0.06, 0.3), m, parent=c.head, coll=c.coll, bevel=0.06)
    box("shglint", (-0.3, -0.7, 0.16), (0.22, 0.02, 0.06), mat("white", (1, 1, 1)), parent=c.head, coll=c.coll)
def chain(size=1.0, drop=0.0, pend=0.35):
    def f(c):
        for k in range(11):
            a_ = -1.25 + k * 0.25
            sphere("link", (math.sin(a_) * 0.75, -0.53 - 0.05 * size, 1.95 - (1 - abs(a_) / 1.25) * (0.55 + drop)), 0.075 * size * 1.6, GOLD,
                   coll=c.coll, parent=c.hips, seg=8)
        cyl("pendant", (0, -0.56 - 0.05 * size, 1.95 - 0.6 - drop - pend * size * 0.9), pend * size, 0.1 * size, GOLD, rot=(math.pi / 2, 0, 0),
            parent=c.hips, coll=c.coll, verts=20)
    return f
def kev_chain(c):
    """the chain so heavy he can't stand up straight: fat links + a pendant the size of a pizza"""
    for k in range(13):
        a_ = -1.3 + k * (2.6 / 12)
        sphere("biglink", (math.sin(a_) * 0.85, -0.62, 1.95 - (1 - abs(a_) / 1.3) * 1.25), 0.24, GOLD, coll=c.coll, parent=c.hips, seg=10)
    cyl("bigpend", (0, -0.75, -0.25), 0.95, 0.3, GOLD, rot=(math.pi / 2, 0, 0), parent=c.hips, coll=c.coll, verts=28)
    text3d("K", (0, -0.92, -0.25), 1.0, mat("pendk", (0.75, 0.05, 0.1)), rot=(math.pi / 2, 0, 0), coll=c.coll, extrude=0.06, parent=c.hips)
def ray_extra(c):
    m = mat("raycap", (0.1, 0.1, 0.12))
    box("capcrown", (0, 0.05, 0.72), (1.36, 1.36, 0.36), m, parent=c.head, coll=c.coll, bevel=0.12)
    box("capbrim", (0, -0.85, 0.58), (1.2, 0.7, 0.1), m, parent=c.head, coll=c.coll)
    box("beard", (0, -0.5, -0.52), (1.24, 0.3, 0.32), mat("beardg", (0.55, 0.55, 0.55)), parent=c.head, coll=c.coll, bevel=0.1)
    box("apron", (0, -0.52, 0.6), (1.7, 0.06, 2.0), mat("apron", (0.97, 0.97, 0.95)), parent=c.hips, coll=c.coll)

SK = [(0.36, 0.2, 0.11), (0.28, 0.15, 0.08), (0.45, 0.27, 0.16), (0.5, 0.3, 0.18), (0.22, 0.12, 0.07)]
RED = (0.9, 0.12, 0.12)
def mk_dre():
    return Char("dre", TEMP, SK[0], (0.96, 0.96, 0.96), (0.48, 0.48, 0.52), hair="none", shoes=(0.98, 0.98, 0.98), scale=0.95,
                extra=durag((0.04, 0.06, 0.22)))
def mk_milo(sh=False):
    return Char("milo", TEMP, SK[3], RED, (0.12, 0.12, 0.16), hair="fade", hair_col=(0.05, 0.04, 0.03), shoes=(1, 1, 1), scale=0.9,
                extra=combo(long_sleeves(RED, SK[3]), hoodie(RED), chain(0.8), *( [shades] if sh else [])))
def mk_kev():
    blk = (0.09, 0.09, 0.11)
    return Char("kev", TEMP, SK[4], blk, (0.22, 0.3, 0.5), hair="cornrows", hair_col=(0.03, 0.02, 0.02), shoes=(0.95, 0.2, 0.15), scale=1.32,
                extra=combo(long_sleeves(blk, SK[4]), hoodie(blk), kev_chain))
def mk_ray():
    return Char("ray", TEMP, SK[1], (0.75, 0.15, 0.15), (0.15, 0.15, 0.2), hair="short", hair_col=(0.3, 0.3, 0.3),
                shoes=(0.1, 0.1, 0.1), extra=ray_extra, scale=1.18)
def mk_baby():
    b = Char("baby", TEMP, SK[0], (1, 0.85, 0.2), (1, 0.85, 0.2), hair="short", hair_col=(0.05, 0.04, 0.03), shoes=(1, 1, 1), scale=0.5,
             extra=combo(shades, chain(1.1)))
    b.head.scale = (1.5, 1.5, 1.5); return b
KIDS = [(SK[1], (1, 0.8, 0.1), (0.2, 0.3, 0.7), "afro"), (SK[3], (0.15, 0.45, 0.95), (0.95, 0.95, 0.95), "locs"),
        (SK[2], (0.2, 0.7, 0.35), (0.12, 0.12, 0.16), "fade"), (SK[4], (0.6, 0.25, 0.9), (0.2, 0.2, 0.25), "cornrows")]
def mk_kid(i):
    s_, sh_, p_, h_ = KIDS[i % len(KIDS)]
    return Char(f"kid{i}", TEMP, s_, sh_, p_, hair=h_, hair_col=(0.04, 0.03, 0.02), scale=0.9 + 0.04 * (i % 3),
                extra=combo(long_sleeves(sh_, s_), hoodie(sh_), chain(0.9)))

def talk(c, shot, base="happy", t0=0, t1=99):
    for w, a, b in WORDS[shot]:
        if t0 <= a < t1:
            c.set_face("talk", F(a)); c.set_face(base, F(a) + max(2, int((b - a) * FPS * 0.7)))
def sit(c, f0, f1, loc, rotz, scale=0.95, seat=1.0, energy=0.5, talkk=False, arms=(1.0, 1.0), arms_side=(0.15, 0.15), legs=(1.25, 1.25)):
    c.place((loc[0], loc[1], seat + 0.05 - 1.35 * scale), rotz, f0)
    for f in range(f0, f1 + 1):
        t = f / 24
        c.pose(f, arms=arms, arms_side=arms_side, legs=legs, hips_z=1.35 + 0.02 * math.sin(t * 3),
               head=(0.05 * math.sin(t * 2) * energy + (0.05 * math.sin(t * 10) if talkk else 0), 0.08 * math.sin(t * 1.3) * energy, 0))
def hand(c, i=1):
    """empty at the hand of arm i (1 = character's left/screen-right when facing camera)"""
    return empty("hand", (0, -0.15, -2.0), parent=c.arms[i], coll=TEMP)
def fastrun(c, f0, f1, a, b, cad=5.5, flail=False):
    a, b = Vector(a), Vector(b); d = b - a; rotz = math.atan2(d.y, d.x) + math.pi / 2
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); c.move(f, a + d * u, rotz)
        ph = (f - f0) / 24 * cad * 2 * math.pi; s = math.sin(ph)
        if flail: arms = (2.6 + 0.4 * s, 2.6 - 0.4 * s); side = (0.6, 0.6)
        else: arms = (-s * 1.3, s * 1.3); side = (0.1, 0.1)
        c.pose(f, arms=arms, arms_side=side, legs=(s * 1.1, -s * 1.1), hips_z=2.0 + abs(math.cos(ph)) * 0.3, lean=-0.3, head=(0.1, 0, 0.06 * s))

# ---------------------------------------------------------------- props
def mk_whip(coll, loc=(0, 0, 0)):
    """gold convertible, nose toward -y"""
    r = empty("whip", loc, coll=coll); g = mat("whipgold", (1, 0.72, 0.06), 0.2); blk = mat("tire", (0.04, 0.04, 0.05), 0.6)
    box("wbody", (0, 0, 1.05), (3.6, 7.0, 1.2), g, parent=r, coll=coll, bevel=0.35)
    box("whood", (0, -2.6, 1.55), (3.4, 2.0, 0.25), g, rot=(-0.12, 0, 0), parent=r, coll=coll, bevel=0.1)
    box("wtrunk", (0, 2.7, 1.6), (3.4, 1.6, 0.3), g, parent=r, coll=coll, bevel=0.1)
    box("wwind", (0, -1.25, 2.15), (3.2, 0.1, 0.95), mat("tglass", (0.25, 0.45, 0.7), 0.05), rot=(-0.45, 0, 0), parent=r, coll=coll)
    box("wseat", (0, 0.6, 1.55), (3.0, 2.4, 0.5), mat("seat", (0.06, 0.06, 0.07)), parent=r, coll=coll, bevel=0.1)
    box("wspoil", (0, 3.4, 2.35), (3.6, 0.6, 0.12), blk, parent=r, coll=coll)
    for sx in (-1.3, 1.3): box("wspleg", (sx, 3.3, 2.0), (0.15, 0.3, 0.7), blk, parent=r, coll=coll)
    box("wwheel_s", (-0.75, -0.55, 2.1), (0.1, 0.5, 0.5), blk, rot=(1.0, 0, 0), parent=r, coll=coll)
    for sx in (-1.75, 1.75):
        for sy in (-2.3, 2.3):
            cyl("wtire", (sx, sy, 0.62), 0.62, 0.55, blk, rot=(0, math.pi / 2, 0), parent=r, coll=coll, verts=20)
            cyl("whub", (sx * 1.02, sy, 0.62), 0.34, 0.57, mat("chrome", (0.9, 0.9, 0.95), 0.1), rot=(0, math.pi / 2, 0), parent=r, coll=coll, verts=12)
    for sx in (-1.2, 1.2): sphere("whl", (sx, -3.48, 1.15), 1, mat("hlight", (1, 1, 0.85), 0.1), coll=coll, parent=r, scale=(0.4, 0.06, 0.22))
    return r
BILL = mat("bill", (0.36, 0.72, 0.36), 0.7)
def money_rain(n, center, rx, ry, top, count=60, seed=0, speed=4.0, bottom=0.3):
    rnd = random.Random(seed)
    for k in range(count):
        o = box("bill", (0, 0, 0), (0.55, 0.26, 0.012), BILL, coll=TEMP)
        x0, y0 = center[0] + rnd.uniform(-rx, rx), center[1] + rnd.uniform(-ry, ry); ph = rnd.random(); sp = speed * rnd.uniform(0.7, 1.2)
        H = top - bottom; spin = rnd.uniform(4, 9); wob = rnd.uniform(0.2, 0.6)
        for f in range(1, n + 1, 2):
            u = (ph + f / 24 * sp / H) % 1.0; tt = f / 24
            o.location = (x0 + wob * math.sin(tt * 3 + k), y0 + wob * math.cos(tt * 2.5 + k), top - u * H + center[2])
            o.rotation_euler = (0.6 * math.sin(tt * spin + k), 0.5 * math.cos(tt * spin * 0.8 + k), tt * 2 + k)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
def tumbleweed(n, a, b, r=0.7):
    o = sphere("tumble", (0, 0, 0), r, mat("tumble", (0.6, 0.45, 0.25), 0.9), coll=TEMP, seg=6)
    o2 = sphere("tumble2", (0, 0, 0), r * 0.8, mat("tumble2", (0.48, 0.34, 0.18), 0.9), coll=TEMP, seg=5, parent=o); o2.rotation_euler = (0.5, 0.3, 0.2)
    a, b = Vector(a), Vector(b)
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); p = a.lerp(b, u); p.z += r + abs(math.sin(u * 9)) * 0.6
        o.location = p; o.rotation_euler = (-u * 20, 0, 0); o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
    return o
def croc(parent, loc=(0, -0.2, -2.15), rot=(0, 0, 0)):
    g = mat("croc", (0.35, 0.88, 0.2), 0.5); r = empty("croc", loc, parent=parent, coll=TEMP, rot=rot)
    box("crocbody", (0, 0, 0), (0.75, 1.45, 0.55), g, parent=r, coll=TEMP, bevel=0.25)
    box("crocsole", (0, 0, -0.28), (0.8, 1.5, 0.12), mat("crocsole", (0.95, 0.95, 0.9)), parent=r, coll=TEMP, bevel=0.05)
    box("crocstrap", (0, 0.55, 0.05), (0.85, 0.14, 0.45), g, parent=r, coll=TEMP, bevel=0.05)
    for i in range(3):
        for j in range(2): sphere("crochole", (-0.18 + i * 0.18, -0.45 + j * 0.25, 0.27), 0.06, mat("crochl", (0.12, 0.3, 0.08)), coll=TEMP, parent=r, seg=6)
    return r

# ---------------------------------------------------------------- the block: Dre's stoop (left side, house centre y=6.5) and Kev's (y=13.5)
STOOP = Vector((-8.85, 4.82, 0)); KSTOOP = Vector((-8.85, 11.82, 0))
DELI_FRONT = Vector((8.3, -4.5, 0.2))

# lemonade stand (shown only in b09)
LEM = collection("lemonade", WORLD); LEM.hide_render = True
LS = Vector((-5.9, -11.0, 0.2))
box("lstand", LS + Vector((0, 0, 1.25)), (1.3, 3.6, 2.5), mat("lstand", (0.98, 0.9, 0.55)), coll=LEM, bevel=0.06)
box("ltop", LS + Vector((0, 0, 2.55)), (1.6, 3.9, 0.16), mat("ltop", (0.95, 0.4, 0.15)), coll=LEM, bevel=0.04)
text3d("LEMONADE", LS + Vector((0.68, 0, 1.75)), 0.62, mat("lemtxt", (0.95, 0.2, 0.25)), rot=(math.pi / 2, 0, math.pi / 2), coll=LEM, extrude=0.02)
text3d("25¢", LS + Vector((0.68, 0, 0.9)), 0.6, mat("lemtxt2", (0.15, 0.45, 0.9)), rot=(math.pi / 2, 0, math.pi / 2), coll=LEM, extrude=0.02)
cyl("pitcher", LS + Vector((0, 1.1, 3.2)), 0.38, 1.1, mat("lemon", (1, 0.9, 0.2), 0.1), coll=LEM, verts=16)
cyl("jar", LS + Vector((0, -1.2, 2.95)), 0.3, 0.65, mat("jar", (0.75, 0.9, 0.95), 0.05), coll=LEM, verts=14)
text3d("TIPS", LS + Vector((0.32, -1.2, 2.95)), 0.17, mat("white", (1, 1, 1)), rot=(math.pi / 2, 0, math.pi / 2), coll=LEM, extrude=0.01)

# ---------------------------------------------------------------- Uncle Ray's deli... inside a deli... inside a deli (Droste set, far east)
DL = Vector((250, 0, 0)); DROSTE = collection("droste", WORLD); DROSTE.hide_render = True
SIGNS = ["DELI & GROCERY", "DELI INSIDE", "DELI INSIDE THAT", "BRO??", "STOP"]
STK = 0.25; CHILD_Y = 4.5
def mk_deli(o, s, lvl, coll, nested=True, sign=None):
    wall = mat("dlbrick", (0.42, 0.24, 0.16), 0.85); W, D, H = 12 * s, 10 * s, 8 * s
    objs = []
    objs.append(box("dlfloor", o + Vector((0, D / 2, 0.05 * s)), (W, D, 0.1 * s), mat("dltile", (0.92, 0.9, 0.85)), coll=coll))
    for k in range(4): objs.append(box("dlstripe", o + Vector((0, D * (0.15 + k * 0.22), 0.11 * s)), (W * 0.98, 0.5 * s, 0.01 * s), mat("dltile2", (0.85, 0.3, 0.3)), coll=coll))
    walls = [box("dlback", o + Vector((0, D, H / 2)), (W, 0.4 * s, H), wall, coll=coll),
             box("dlside", o + Vector((-W / 2, D / 2, H / 2)), (0.4 * s, D, H), wall, coll=coll),
             box("dlside", o + Vector((W / 2, D / 2, H / 2)), (0.4 * s, D, H), wall, coll=coll),
             box("dlroof", o + Vector((0, D / 2, H + 0.2 * s)), (W + 0.4 * s, D + 0.4 * s, 0.4 * s), mat("tar", (0.2, 0.2, 0.22)), coll=coll)]
    for w in walls: w.visible_shadow = False
    objs += walls
    objs.append(box("dlsign", o + Vector((0, -0.05 * s, H - 1.1 * s)), (W, 0.4 * s, 2.2 * s), mat("signyellow", (1, 0.82, 0.1)), coll=coll))
    txt = sign or SIGNS[min(lvl, len(SIGNS) - 1)]
    objs.append(text3d(txt, o + Vector((0, -0.3 * s, H - 1.1 * s)), (1.25 if len(txt) < 12 else 0.95) * s, mat("dlsigntxt", (0.85, 0.1, 0.1)), coll=coll, extrude=0.05 * s))
    aw = box("dlawn", o + Vector((0, -1.0 * s, H - 2.6 * s)), (W, 2.0 * s, 0.14 * s), mat("awn", (0.1, 0.55, 0.25)), rot=(0.35, 0, 0), coll=coll); objs.append(aw)
    for k in range(6): objs.append(box("dlaws", o + Vector((-W / 2 + W * (k + 0.5) / 6, -1.0 * s, H - 2.55 * s)), (0.7 * s, 2.0 * s, 0.15 * s), mat("trimw", (0.95, 0.95, 0.93)), rot=(0.35, 0, 0), coll=coll))
    cols = [(0.9, 0.2, 0.2), (0.2, 0.5, 0.95), (1, 0.8, 0.1), (0.3, 0.8, 0.35), (0.95, 0.5, 0.1), (0.7, 0.3, 0.9)]
    for sx in (-1, 1):
        for row in range(4):
            objs.append(box("dlshelf", o + Vector((sx * (W / 2 - 0.9 * s), D * 0.45, 1.0 * s + row * 1.5 * s)), (1.4 * s, D * 0.75, 0.12 * s), mat("shelf", (0.85, 0.85, 0.88)), coll=coll))
            for k in range(7):
                objs.append(box("dlgood", o + Vector((sx * (W / 2 - 0.9 * s), D * 0.15 + k * D * 0.1, 1.35 * s + row * 1.5 * s)), (0.8 * s, 0.6 * s, 0.6 * s),
                                mat(f"good{(k + row) % 6}", cols[(k + row * 2 + (sx > 0)) % 6]), coll=coll))
    objs.append(box("dlcounter", o + Vector((-W * 0.3, D * 0.9, 1.2 * s)), (W * 0.3, 1.2 * s, 2.4 * s), mat("counter", (0.3, 0.6, 0.55)), coll=coll))
    if nested and lvl < 4:
        mk_deli(o + Vector((0, CHILD_Y * s, 0.1 * s)), s * STK, lvl + 1, coll)
    return objs
mk_deli(DL, 1.0, 0, DROSTE)
DELI2 = empty("deli2", DL + Vector((0, 0, 8.4)), coll=DROSTE)
for ob in mk_deli(Vector((0, 0, 0)), 1.0, 0, DROSTE, nested=False, sign="DELI #2"):
    if ob.parent is None: ob.parent = DELI2
def droste_cam(k):
    s = STK ** k; o = DL + Vector((0, CHILD_Y * (1 - STK ** k) / (1 - STK), 0.1 * (1 - STK ** k) / (1 - STK)))
    return o + Vector((0, -13, 4.2)) * s, o + Vector((0, 3, 3.6)) * s

# ---------------------------------------------------------------- OHIO (far west): flat fields, corn, a big green sign
OH = Vector((-250, 0, 0)); OHIO = collection("ohio", WORLD); OHIO.hide_render = True
box("ohroad", OH + Vector((0, 0, 0.03)), (8, 600, 0.1), mat("ohroad", (0.3, 0.3, 0.32)), coll=OHIO)
for y in range(-300, 300, 10): box("ohdash", OH + Vector((0, y, 0.1)), (0.3, 4, 0.02), mat("ohline", (1, 0.85, 0.2)), coll=OHIO)
corn = mat("corn", (0.45, 0.68, 0.18), 0.8); tassel = mat("tassel", (0.95, 0.85, 0.35), 0.8)
for sx in (-1, 1):
    for r_ in range(9):
        x = sx * (7 + r_ * 2.2)
        box("cornrow", OH + Vector((x, 0, 1.4)), (1.2, 600, 2.8), corn, coll=OHIO, bevel=0.3)
        box("tasselrow", OH + Vector((x, 0, 2.9)), (0.6, 600, 0.25), tassel, coll=OHIO)
SIGNY = -60
for sx in (-1.6, 1.6): box("ohpost", OH + Vector((6.2 + sx, SIGNY, 3)), (0.3, 0.3, 6), mat("ohpost", (0.6, 0.6, 0.62)), coll=OHIO)
box("ohsign", OH + Vector((6.2, SIGNY, 6.6)), (6.4, 0.2, 3.6), mat("ohgreen", (0.05, 0.45, 0.2), 0.4), coll=OHIO, bevel=0.1)
box("ohsignb", OH + Vector((6.2, SIGNY + 0.05, 6.6)), (6.7, 0.15, 3.9), mat("white", (1, 1, 1)), coll=OHIO, bevel=0.1)
text3d("WELCOME TO", OH + Vector((6.2, SIGNY - 0.12, 7.6)), 0.6, mat("white", (1, 1, 1)), coll=OHIO, extrude=0.02)
text3d("OHIO", OH + Vector((6.2, SIGNY - 0.12, 6.1)), 1.5, mat("white", (1, 1, 1)), coll=OHIO, extrude=0.02)
box("barn", OH + Vector((-30, 40, 5)), (12, 10, 10), mat("barn", (0.75, 0.12, 0.1)), coll=OHIO)
prism("barnroof", OH + Vector((-30, 40, 12)), (12.6, 10.6, 4), mat("barnroof", (0.25, 0.25, 0.28)), coll=OHIO)
cyl("silo", OH + Vector((-22, 44, 8)), 2.5, 16, mat("silo", (0.75, 0.78, 0.8)), coll=OHIO, verts=16)
cyl("wtower", OH + Vector((28, 90, 22)), 5, 6, mat("wtower", (0.85, 0.88, 0.9)), coll=OHIO, verts=20)
for a_ in range(4): box("wtleg", OH + Vector((28 + 3 * math.cos(a_ * 1.57), 90 + 3 * math.sin(a_ * 1.57), 9.5)), (0.4, 0.4, 19), mat("ohpost", (0.6, 0.6, 0.62)), coll=OHIO)

# ---------------------------------------------------------------- tiny planet (he runs round the world)
PL = Vector((-250, 400, 60)); PLAN = collection("planet"); PLAN.hide_render = True
PLR = 7.0; PLANET = empty("planet", PL, coll=PLAN)
sphere("pground", (0, 0, 0), PLR, mat("grass", (0.36, 0.78, 0.28)), coll=PLAN, parent=PLANET, seg=48)
cyl("pband", (0, 0, 0), PLR + 0.06, 2.6, mat("road", (0.22, 0.23, 0.26)), rot=(0, math.pi / 2, 0), coll=PLAN, parent=PLANET, verts=64)
for k in range(24):
    a_ = k / 24 * 6.283
    box("pdash", (0, math.cos(a_) * (PLR + 0.1), math.sin(a_) * (PLR + 0.1)), (0.15, 0.9, 0.02), mat("line", (0.97, 0.97, 0.9)), rot=(a_ + math.pi / 2, 0, 0), coll=PLAN, parent=PLANET)
rr = random.Random(4)
for k in range(26):
    a_ = rr.uniform(0, 6.283); sx = rr.choice((-1, 1)) * rr.uniform(2.2, 4.5); h_ = math.sqrt(PLR ** 2 - sx ** 2)
    piv = empty("ppiv", (sx, 0, 0), parent=PLANET, coll=PLAN, rot=(a_, 0, 0))
    if k % 3 == 0:
        sphere("ptree", (0, 0, h_ + 1.1), 0.9, M["leaf"], coll=PLAN, parent=piv, seg=10)
        cyl("ptrunk", (0, 0, h_ + 0.3), 0.15, 1.0, M["bark"], coll=PLAN, parent=piv, verts=6)
    else:
        hh = rr.uniform(1.6, 3.2)
        box("phouse", (0, 0, h_ + hh / 2 - 0.2), (1.4, 1.6, hh), mat(f"brick{rr.randint(0,6)}", BRICK[rr.randint(0, 6)], 0.85), coll=PLAN, parent=piv)
        box("proof", (0, 0, h_ + hh - 0.15), (1.5, 1.7, 0.15), mat("tar", (0.2, 0.2, 0.22)), coll=PLAN, parent=piv)

COLLS = {"hood": HOODC, "lem": LEM, "droste": DROSTE, "ohio": OHIO, "planet": PLAN}
def show_set(*on, ground=True):
    for k, c in COLLS.items(): c.hide_render = k not in on
    WORLD.hide_render = not ground

# ---------------------------------------------------------------- shots
def b01(n):   # crane down the block: everybody got motion (whip, chains, dancing, money rain)
    show_set("hood")
    car = mk_whip(TEMP); m = mk_milo(sh=True); m.root.parent = car
    m.place((-0.75, 0.55, 1.8 - 1.35 * 0.9), 0); m.set_face("smug", 1)
    for f in range(1, n + 1):
        m.pose(f, arms=(1.3, 0.6), arms_side=(0.1, -0.5), legs=(1.5, 1.5), hips_z=1.35, head=(0.05, 0.25, 0.2 * math.sin(f / 6)))
        u = (f - 1) / (n - 1); car.location = (-2.3, 26 - 24 * u, 0.1); car.keyframe_insert("location", frame=f)
    k = mk_kev(); k.place((6.4, 3, 0.2), -0.3); k.set_face("determined", 1)
    for f in range(1, n + 1): k.pose(f, arms=(0.4, 0.4), arms_side=(0.1, 0.1), lean=0.45 + 0.03 * math.sin(f / 4), hips_z=1.9, head=(-0.35, 0, 0))
    for i, (x, y, r) in enumerate([(-6.3, 9, 0.6), (6.4, 13, -0.6), (-6.5, 17, 0.4), (6.2, 20, -0.4)]):
        c = mk_kid(i); c.place((x, y, 0.2), r); c.dance(1, n, i % 3, speed=1.1 + 0.1 * i); c.set_face(["laugh", "excited", "smug", "laugh"][i], 1)
    r = mk_ray(); r.place(DELI_FRONT, -math.pi / 2); r.dance(1, n, 2, 0.9); r.set_face("laugh", 1)
    money_rain(n, (0, 8, 0), 8, 14, 16, 120, seed=1, speed=5)
    cpath(n, (-1.0, -30, 21), (0, 10, 1.5), (-0.4, -11.5, 3.6), (0, 6, 3.4), 22, 24, 0.0, -0.04)
def b02(n):   # "except me." Dre on his stoop, deadpan; snap push
    show_set("hood")
    d = mk_dre(); sit(d, 1, n, STOOP, math.pi / 2, arms=(1.1, 1.4), arms_side=(0.15, -0.2)); d.set_face("blink", 1); d.set_face("sad", 4)
    d.set_face("blink", n - 10); d.set_face("sad", n - 7)
    cpath(n, (-1.6, 4.3, 3.4), (-8.6, 4.8, 2.9), (-2.8, 4.5, 3.35), (-8.6, 4.8, 3.0), 30, 34)
def b03(n):   # Milo in the gold whip. "He's twelve."
    show_set("hood")
    car = mk_whip(TEMP); m = mk_milo(sh=True); m.root.parent = car
    m.place((-0.75, 0.55, 1.8 - 1.35 * 0.9), 0); m.set_face("smug", 1)
    tw = F(wt("b03", "he's"))
    for f in range(1, n + 1):
        lean = 0.0 if f < tw else 0.12
        m.pose(f, arms=(1.3, 0.25), arms_side=(0.1, -1.1), legs=(1.5, 1.5), hips_z=1.35, head=(0.05, 0.0, (0.5 if f >= tw else 0.15 * math.sin(f / 8))), lean=lean)
        u = min(1, (f - 1) / (n * 0.55)); u = 1 - (1 - u) ** 2
        car.location = (-2.3, 10 - 9 * u, 0.1); car.keyframe_insert("location", frame=f)
    m.set_face("blink", tw); m.set_face("smug", tw + 3)
    TRACK.append(m.head)
    cpath(n, (3.2, -6.5, 1.3), (-2.8, 2.0, 2.4), (2.2, -4.0, 1.6), (-2.9, 1.5, 3.2), 22, 26, 0.12, 0.08)
def b04(n):   # Big Kev and the chain; he finally face-plants on "straight"
    show_set("hood")
    k = mk_kev(); k.place((6.2, -14, 0.2), 0.0); k.set_face("determined", 1)
    st = F(wt("b04", "straight.")) - 2
    for f in range(1, n + 1):
        t = f / 24
        if f < st:
            tryup = max(0, math.sin(t * 2.2)) * 0.25
            k.pose(f, arms=(0.35, 0.35), arms_side=(0.15, 0.15), lean=0.75 - tryup, hips_z=1.85, head=(-0.55 + tryup, 0, 0.05 * math.sin(t * 7)))
        else:
            u = min(1, (f - st) / 6)
            k.pose(f, arms=(0.35 + 2.4 * u, 0.35 + 2.4 * u), arms_side=(0.3, 0.3), lean=0.75 + 0.8 * u, hips_z=1.85 - 0.5 * u, head=(-0.55 - 0.3 * u, 0, 0))
    k.set_face("scared", int(st * 0.5)); k.set_face("determined", int(st * 0.5) + 14); k.set_face("shocked", st)
    TRACK.append(k.head)
    cpath(n, (4.6, -29, 2.4), (6.2, -14, 2.9), (5.0, -25.5, 2.4), (6.2, -14, 2.7), 26, 28, 0.0, -0.05)
def b05(n):   # Uncle Ray: a store, a second store (stacked!), a store INSIDE the store (Droste zoom)
    show_set("droste")
    CAM.data.clip_start = 0.002
    r = mk_ray(); r.place(DL + Vector((-3.6, -4.2, 0.0)), 0.25); r.set_face("smug", 1)
    sec, ins = F(wt("b05", "second")), F(wt("b05", "inside"))
    for f in range(1, n + 1):
        t = f / 24; up = 1.0 if sec <= f < ins else 0.0
        r.pose(f, arms=(0.3 + 2.4 * up, 0.3 + 1.0 * (f < sec) * max(0, math.sin(t * 3))), arms_side=(0.4, 0.2), head=(-0.25 * up, 0, 0.1 * math.sin(t * 2)), hips_z=2.0 + 0.04 * math.sin(t * 4))
    talk(r, "b05", "smug")
    for f, s in [(1, 0.0), (sec - 1, 0.0), (sec, 0.05), (sec + 4, 1.15), (sec + 7, 1.0)]:
        DELI2.scale = (s,) * 3; DELI2.keyframe_insert("scale", frame=f)
    wide_l, wide_a = DL + Vector((0.5, -27, 7.5)), DL + Vector((0, 2, 7.6))
    k0l, k0a = droste_cam(0)
    for f in range(1, n + 1):
        if f < ins - 3:
            u = ease((f - 1) / max(1, ins - 4)); cam2(f, wide_l.lerp(wide_l + Vector((0, 3, -1)), u), wide_a, 26)
        else:
            u = (f - ins + 3) / max(1, n - ins + 3)
            if u < 0.25:
                v = ease(u / 0.25); cam2(f, (wide_l + Vector((0, 3, -1))).lerp(k0l, v), wide_a.lerp(k0a, v), 26)
            else:
                k_ = 2.55 * ((u - 0.25) / 0.75) ** 1.4; l, a = droste_cam(k_); cam2(f, l, a, 26)
def b06(n):   # lil bro: shades, chain, money raining on the stoop. "He's ONE."
    show_set("hood")
    b = mk_baby(); sit(b, 1, n, STOOP + Vector((0.25, 0, 0)), math.pi / 2, scale=0.5, seat=1.0, arms=(1.6, 2.4), arms_side=(0.3, 0.6), legs=(1.5, 1.5))
    b.set_face("smug", 1)
    one = F(wt("b06", "one."))
    for f in range(1, n + 1):
        t = f / 24; s = math.sin(t * 9)
        b.pose(f, arms=(1.4 + 0.5 * s, 2.6), arms_side=(0.3, 0.7 + 0.2 * s), legs=(1.5, 1.5), hips_z=1.35, head=(0.05 * s, 0.2 * math.sin(t * 2), 0.1 * s))
    b.set_face("laugh", one - 4)
    money_rain(n, STOOP + Vector((0.8, 0, 0)), 2.5, 3.0, 9, 70, seed=6, speed=3.2)
    for k in range(5): box("stack", STOOP + Vector((1.05, -0.9 + k * 0.08, 1.05 + k * 0.13)), (0.6, 0.32, 0.12), BILL, coll=TEMP)
    TRACK.append(b.head)
    cpath(n, (-2.6, 3.6, 2.4), (-8.4, 4.8, 2.0), (-3.6, 4.2, 2.3), (-8.4, 4.8, 2.1), 28, 32, 0.06, 0.02)
def b07(n):   # library card. tumbleweed.
    show_set("hood")
    d = mk_dre(); sit(d, 1, n, STOOP, math.pi / 2)
    c_ = F(wt("b07", "library"))
    for f in range(1, n + 1):
        u = min(1, max(0, (f - c_ + 6) / 5))
        d.pose(f, arms=(1.0, 1.0 + 1.2 * u), arms_side=(0.15, 0.1), legs=(1.25, 1.25), hips_z=1.33, head=(0.15, 0, 0.0))
    card = box("card", (0, -0.25, -2.0), (0.62, 0.05, 0.42), mat("card", (0.2, 0.45, 0.95), 0.3), parent=d.arms[1], coll=TEMP, bevel=0.04)
    box("cardstrip", (0, -0.03, 0.1), (0.62, 0.02, 0.1), mat("white", (1, 1, 1)), parent=card, coll=TEMP)
    d.set_face("sad", 1); d.set_face("blink", n // 2); d.set_face("sad", n // 2 + 3)
    tumbleweed(n, (-4.6, 16, 0.2), (-5.0, -6, 0.2))
    cpath(n, (-1.8, 4.0, 3.3), (-8.6, 4.8, 2.8), (-2.8, 4.4, 3.3), (-8.6, 4.8, 2.9), 30, 34)
def b08(n):   # stands up: "TODAY, I'm getting motion" -- low dutch hero angle
    show_set("hood")
    d = mk_dre(); s0 = Vector((STOOP.x, STOOP.y, 1.05 - 1.35 * 0.95)); s1 = Vector((-7.0, 4.82, 0.2))
    up = F(wt("b08", "today,")) - 4
    for f in range(1, n + 1):
        u = ease(min(1, max(0, (f - up) / 8)))
        d.move(f, s0.lerp(s1, u), math.pi / 2)
        pump = max(0, math.sin((f - up) / 24 * 9)) if f > up + 8 else 0
        d.pose(f, arms=(1.0 * (1 - u) + (2.9 * pump) , 1.0 * (1 - u) + 0.4 * u), arms_side=(0.15, 0.15 + 0.4 * u), legs=(1.25 * (1 - u), 1.25 * (1 - u)),
               hips_z=1.35 + 0.65 * u, head=(-0.1 * u, 0, 0))
    d.set_face("sad", 1); talk(d, "b08", "determined", 0, 99); d.set_face("determined", up)
    TRACK.append(d.head)
    cpath(n, (-2.2, 2.2, 1.0), (-7.6, 4.8, 3.2), (-2.6, 2.8, 0.7), (-7.2, 4.8, 4.6), 26, 24, 0.18, 0.12)
def b09(n):   # lemonade: sold one cup... to himself
    show_set("hood", "lem")
    d = mk_dre(); d.place(LS + Vector((-1.6, 0, 0)), math.pi / 2); d.set_face("excited", 1)
    c1, me = F(wt("b09", "one")), F(wt("b09", "myself."))
    cup = cyl("cup", (0, -0.1, -2.15), 0.2, 0.5, mat("cupw", (1, 1, 1), 0.3), parent=d.arms[1], coll=TEMP, verts=12)
    cup.hide_render = True; cup.keyframe_insert("hide_render", frame=1); cup.hide_render = False; cup.keyframe_insert("hide_render", frame=c1 - 2)
    for f in range(1, n + 1):
        t = f / 24
        if f < c1 - 2: d.pose(f, arms=(1.8 + 0.3 * math.sin(t * 8), 1.8 - 0.3 * math.sin(t * 8)), arms_side=(1.0, 1.0), hips_z=2.0 + 0.05 * abs(math.sin(t * 8)), head=(-0.1, 0, 0.1 * math.sin(t * 4)))
        elif f < me - 2: d.pose(f, arms=(0.2, 1.6), arms_side=(0.1, 0.1), head=(0, 0, 0.15))
        else:
            u = min(1, (f - me + 2) / 5)
            d.pose(f, arms=(0.2, 1.6 + 1.0 * u), arms_side=(0.1, 0.1 + 0.6 * u), head=(-0.35 * u, 0, 0.2 * u))
    d.set_face("happy", c1); d.set_face("smug", me); d.set_face("blink", me + 12); d.set_face("smug", me + 15)
    cpath(n, (1.6, -10.6, 4.0), (-6.8, -11.2, 3.2), (0.6, -10.8, 3.9), (-6.8, -11.2, 3.3), 26, 30, 0.0, 0.05)
def b10(n):   # the "Jordans" ... "bro, them is crocs"
    show_set("hood")
    d = mk_dre(); d.place((-6.6, 8.9, 0.2), math.pi / 2 + 0.25); d.set_face("excited", 1)
    m = mk_milo(); m.place((-6.2, 6.4, 0.2), math.pi / 2 - 0.15); m.set_face("happy", 1)
    croc(d.arms[1], (0, -0.25, -2.25), (0, 0, 0.3))
    ms, cr = F(wt("b10", "milo")), F(wt("b10", "crocs."))
    for f in range(1, n + 1):
        t = f / 24; s = math.sin(t * 6)
        d.pose(f, arms=(0.4, 2.7 + 0.1 * s), arms_side=(0.2, 0.15), hips_z=2.0 + 0.04 * abs(s), head=(-0.15, 0, 0.1 * s if f < cr else 0.0), twist=0.1 * s if f < cr else 0)
        m.pose(f, arms=(0.1, 0.1), arms_side=(-0.5, -0.5), head=(0, 0, (0.7 if f < ms + 6 else -0.15)), hips_z=2.0)
    talk(m, "b10", "blink", wt("b10", "bro,")); m.set_face("smug", cr + 3)
    d.set_face("shocked", cr + 2)
    TRACK.append(d.head)
    cpath(n, (1.4, 7.2, 4.0), (-6.4, 7.7, 3.5), (0.4, 7.4, 3.9), (-6.4, 7.7, 3.6), 26, 30)
def b11a(n):  # Uncle Ray puts him on (arm round the shoulder) outside the deli
    show_set("hood")
    r = mk_ray(); r.place(DELI_FRONT, -math.pi / 2); r.set_face("smug", 1)
    d = mk_dre(); d.place(DELI_FRONT + Vector((-0.2, 2.15, 0)), -math.pi / 2 - 0.25); d.set_face("happy", 1); d.idle(1, n, 0.5)
    for f in range(1, n + 1): r.pose(f, arms=(0.3, 0.2), arms_side=(0.2, 2.3), head=(0.05, 0, -0.35), hips_z=2.0)
    cpath(n, (0.0, -2.4, 4.4), (8.2, -3.4, 4.0), (1.0, -2.8, 4.4), (8.2, -3.4, 4.1), 28, 30)
def b11b(n):  # Ray close-up, wise; snap zoom on MOVE
    show_set("hood")
    r = mk_ray(); r.place(DELI_FRONT, -math.pi / 2); r.set_face("smug", 1)
    mv = F(wt("b11b", "move."))
    for f in range(1, n + 1):
        t = f / 24
        if f < mv - 1: r.pose(f, arms=(0.9 + 0.3 * math.sin(t * 2), 0.3), arms_side=(0.1, 0.2), head=(0.08 * math.sin(t * 3), 0, 0.12 * math.sin(t * 1.4)), hips_z=2.0)
        else: r.pose(f, arms=(2.9, 2.9), arms_side=(0.5, 0.5), head=(-0.2, 0, 0), hips_z=2.1)
    talk(r, "b11b", "smug", 0, wt("b11b", "move.")); r.set_face("excited", mv)
    for f in range(1, n + 1):
        if f < mv: u = ease((f - 1) / max(1, mv - 2)); cam2(f, Vector((-1.5, -3.8, 5.0)).lerp(Vector((0.0, -4.1, 5.2)), u), (8.3, -4.5, 4.9), 28 + 4 * u)
        else: u = min(1, (f - mv) / 3); cam2(f, (0.0, -4.1, 5.2), (8.3, -4.5, 5.55), 32 + 40 * u)
def b12(n):   # so I moved... and kept moving (walk -> run toward camera)
    show_set("hood")
    d = mk_dre(); h = n // 2
    d.walk(1, h, (-6.4, 18, 0.2), (-6.4, 13, 0.2)); d.walk(h, n, (-6.4, 13, 0.2), (-6.4, 1, 0.2), run=True)
    d.set_face("determined", 1); d.set_face("excited", h)
    ctrack(n, d.root, (1.6, -8.5, 2.2), (0, 0, 3.6), 26)
def b13(n):   # past the block, past the city: blur run, side track
    show_set("hood")
    d = mk_dre(); fastrun(d, 1, n, (-6.4, 120, 0.2), (-6.4, -110, 0.2), cad=6.5); d.set_face("laugh", 1)
    ctrack(n, d.root, (6.5, -3.0, 2.6), (0, 0, 3.2), 22, -0.08)
def b14(n):   # OHIO
    show_set("ohio")
    d = mk_dre(); fastrun(d, 1, n, OH + Vector((1.5, -40, 0.1)), OH + Vector((1.5, -100, 0.1)), cad=6.0, flail=True); d.set_face("scared", 1)
    d.set_face("shocked", F(wt("b14", "ohio.")))
    ctrack(n, d.root, (-1.8, -7.5, 1.6), (0.5, 0, 4.0), 22, 0.1)
def b15(n):   # running round a tiny planet (hypnotic spiral)
    show_set("planet", ground=False)
    d = mk_dre(); top = PL + Vector((0, 0, PLR + 0.15)); d.place(top, 0.0); d.set_face("laugh", 1)
    for f in range(1, n + 1):
        ph = f / 24 * 5.5 * 2 * math.pi; s = math.sin(ph)
        d.pose(f, arms=(-s * 1.3, s * 1.3), arms_side=(0.1, 0.1), legs=(s * 1.1, -s * 1.1), hips_z=2.0 + abs(math.cos(ph)) * 0.25, lean=-0.3, head=(0.1, 0, 0))
        PLANET.rotation_euler = (-f / 24 * 1.6, 0, 0); PLANET.keyframe_insert("rotation_euler", frame=f)
    TRACK.append(d.head)
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); a = -1.9 + 2.6 * u; rr_ = 15 + 9 * u
        cam2(f, PL + Vector((math.cos(a) * rr_, math.sin(a) * rr_, 9 + 6 * u)), PL + Vector((0, 0, PLR + 1.5 - 2.5 * u)), 24, 0.25 * math.sin(u * 3))
def b16(n):   # Kev on his stoop: "bro, how you stop?" Dre zips past again and again
    show_set("hood")
    k = mk_kev(); sit(k, 1, n, KSTOOP, math.pi / 2, scale=1.32, seat=1.0, arms=(0.8, 0.8), legs=(1.1, 1.1))
    k.set_face("happy", 1)
    for f in range(1, n + 1): k.pose(f, arms=(0.8, 0.8), arms_side=(0.1, 0.1), legs=(1.1, 1.1), hips_z=1.35, lean=0.35, head=(-0.25, 0, 0.6 * math.sin(f / 3.5)))
    talk(k, "b16", "happy", wt("b16", "bro,")); k.set_face("shocked", n - 6)
    d = mk_dre(); d.set_face("scared", 1)
    passes = [(2, 1), (int(n * 0.4), -1), (int(n * 0.75), 1)]
    d.place((-5.8, 60, 0.2), 0)
    for f0, dirn in passes:
        a, b = Vector((-5.6, 11.8 + 30 * dirn, 0.2)), Vector((-5.6, 11.8 - 30 * dirn, 0.2))
        fastrun(d, f0, f0 + 5, a, b, cad=7, flail=True)
        d.move(f0 - 1, Vector((-5.6, 80, 0.2))); d.move(f0 + 6, Vector((-5.6, 80, 0.2)))
    cpath(n, (-0.4, 11.3, 4.4), (-8.6, 11.8, 3.8), (-1.2, 11.4, 4.4), (-8.6, 11.8, 3.9), 26, 28)
def b17(n):   # "I DON'T KNOW!!!" sprint at camera, shaky handheld; end card plays over it
    show_set("hood")
    d = mk_dre(); fastrun(d, 1, n, (-1.0, 90, 0.2), (-1.0, -60, 0.2), cad=6.0, flail=True); d.set_face("shocked", 1)
    talk(d, "b17", "shocked")
    TRACK.append(d.head)
    ctrack(n, d.root, (0.4, -6.0, 3.0), (0, 0, 4.1), 24, 0.0, shake=0.12)

TRACK = []
def track_json(n):
    from bpy_extras.object_utils import world_to_camera_view
    out = []
    for f in range(1, n + 1):
        S.frame_set(f)
        if not TRACK: out.append(None); continue
        o = TRACK[0]; p = o.matrix_world.translation
        v = world_to_camera_view(S, CAM, p); out.append((round(v.x, 4), round(1 - v.y, 4), round(v.z, 2)))
    return out

SHOTS = {k: v for k, v in list(globals().items()) if k.startswith("b") and k[1:3].isdigit() and callable(v)}
os.makedirs(OUT, exist_ok=True); os.makedirs(f"{E}/preview", exist_ok=True)
for name in TL["shots"]:
    if ONLY and name not in ONLY: continue
    n = max(10, int(round(DUR[name] * FPS)))
    clear_temp(); S.frame_set(1); CAM.data.clip_start = 0.1
    for o in (DELI2, PLANET):
        if o.animation_data: o.animation_data_clear()
    DELI2.scale = (1, 1, 1); PLANET.rotation_euler = (0, 0, 0)
    TRACK.clear(); SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    json.dump(track_json(n), open(f"{d}/track.json", "w"))
    if STILL:
        S.frame_set(int(n * 0.6)); S.render.filepath = f"{E}/preview/{name}.png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d):
            if f.endswith(".png"): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
