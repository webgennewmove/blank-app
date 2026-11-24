"""NUMBER TOWN ep1 — 'whatever number you say, that many of you appear'."""
import sys, os, json, math, random
REAL_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = [sys.argv[0], "--", "none"]
os_env = __import__('os').environ; os_env['HOOD'] = '1'
exec(open("/home/claude/zara/world.py").read())          # builds town, bedroom, helpers, chars
import bmesh
from mathutils import Vector, Matrix
ONLY = set(REAL_ARGV[0].split(",")) if REAL_ARGV and REAL_ARGV[0] != "all" else None
STILL = len(REAL_ARGV) > 1 and REAL_ARGV[1] == "still"
OUT = "/home/claude/zara/nframes"
S.render.resolution_x, S.render.resolution_y = 720, 1280
random.seed(3)
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")

def text3d(body, loc, size, m, rot=(math.pi / 2, 0, 0), coll=None, extrude=0.05, align="CENTER"):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.font = FONTB; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m); return o

exec(open("/home/claude/zara/hood.py").read())

# ---------------------------------------------------------------- hood cast
def hoodie(col):
    def f(c):
        m = mat(f"hood{col}", col)
        box("hoodback", (0, 0.55, 1.95), (1.5, 0.45, 0.8), m, parent=c.hips, coll=c.coll, bevel=0.15)
        box("pocket", (0, -0.52, 0.55), (1.3, 0.06, 0.6), mat(f"hoodpk{col}", tuple(v * 0.8 for v in col)), parent=c.hips, coll=c.coll)
        for sx in (-0.25, 0.25): cyl("string", (sx, -0.53, 1.55), 0.035, 0.6, mat("white", (1, 1, 1)), parent=c.hips, coll=c.coll, verts=6)
    return f
def puffer(col):
    def f(c):
        m = mat(f"puff{col}", col)
        for k in range(3): box("pband", (0, 0, 0.45 + k * 0.62), (2.16, 1.16, 0.5), m, parent=c.hips, coll=c.coll, bevel=0.22)
        box("collar", (0, 0.05, 2.0), (1.5, 1.1, 0.35), m, parent=c.hips, coll=c.coll, bevel=0.12)
    return f
def chain(c):
    for k in range(9):
        a_ = -1.1 + k * 0.275
        sphere("chain", (math.sin(a_) * 0.62, -0.52 + (1 - math.cos(a_)) * 0.05, 1.9 - math.cos(a_) * 0.0 - (1 - abs(a_) / 1.1) * 0.45), 0.07, mat("gold", (1, 0.8, 0.1)), coll=c.coll, parent=c.hips, seg=6)
def combo(*fs):
    def f(c):
        for g in fs: g(c)
    return f
def ray_extra(c):
    m = mat("raycap", (0.1, 0.1, 0.12))
    box("capcrown", (0, 0.05, 0.72), (1.36, 1.36, 0.36), m, parent=c.head, coll=c.coll, bevel=0.12)
    box("capbrim", (0, -0.85, 0.58), (1.2, 0.7, 0.1), m, parent=c.head, coll=c.coll)
    box("beard", (0, -0.5, -0.5), (1.24, 0.3, 0.35), mat("beardg", (0.55, 0.55, 0.55)), parent=c.head, coll=c.coll, bevel=0.1)
    box("apron", (0, -0.52, 0.6), (1.7, 0.06, 2.0), mat("apron", (0.97, 0.97, 0.95)), parent=c.hips, coll=c.coll)
SK = [(0.36, 0.2, 0.11), (0.28, 0.15, 0.08), (0.45, 0.27, 0.16), (0.5, 0.3, 0.18), (0.22, 0.12, 0.07), (0.75, 0.5, 0.35)]
def mk_zara(hat=False):
    return Char("zara", TEMP, SK[2], (0.55, 0.25, 0.85), (0.12, 0.12, 0.16), hair="puffs", hair_col=(0.06, 0.04, 0.03),
                shoes=(1, 0.35, 0.6), scale=0.92, extra=combo(puffer((0.55, 0.25, 0.85)), party_hat) if hat else puffer((0.55, 0.25, 0.85)))
def mk_milo():
    return Char("milo", TEMP, SK[0], (0.92, 0.15, 0.15), (0.55, 0.55, 0.6), hair="fade", hair_col=(0.05, 0.04, 0.03),
                shoes=(1, 1, 1), scale=0.95, extra=hoodie((0.92, 0.15, 0.15)))
KIDS = [(SK[1], (1, 0.8, 0.1), (0.2, 0.3, 0.7), "afro", None), (SK[3], (0.15, 0.45, 0.95), (0.95, 0.95, 0.95), "cornrows", chain),
        (SK[4], (0.2, 0.7, 0.35), (0.12, 0.12, 0.16), "locs", None), (SK[5], (0.97, 0.97, 0.97), (0.3, 0.35, 0.6), "ponytail", None),
        (SK[2], (1, 0.5, 0.1), (0.15, 0.15, 0.2), "fade", None)]
def mk_kid(i):
    s_, sh_, p_, h_, ex = KIDS[i % len(KIDS)]
    return Char(f"kid{i}", TEMP, s_, sh_, p_, hair=h_, hair_col=(0.05, 0.04, 0.03), scale=0.9,
                extra=combo(hoodie(sh_), ex) if (i % 2 == 0 and ex) else (hoodie(sh_) if i % 2 == 0 else ex))
def mk_teacher():
    return Char("teacher", TEMP, SK[2], (0.95, 0.7, 0.15), (0.3, 0.2, 0.45), hair="afro", hair_col=(0.08, 0.05, 0.04),
                shoes=(0.5, 0.15, 0.3), extra=glasses, scale=1.15)
def mk_ray():
    return Char("ray", TEMP, SK[1], (0.75, 0.15, 0.15), (0.15, 0.15, 0.2), hair="short", hair_col=(0.3, 0.3, 0.3),
                shoes=(0.1, 0.1, 0.1), extra=ray_extra, scale=1.18)
def mk_baby():
    b = Char("baby", TEMP, SK[2], (1, 0.85, 0.2), (1, 0.85, 0.2), hair="short", hair_col=(0.05, 0.04, 0.03), shoes=(1, 1, 1), scale=0.5)
    b.head.scale = (1.5, 1.5, 1.5); return b

# ---------------------------------------------------------------- merged crowd Milo (one mesh per pose)
def bake_char(c, name):
    bm = bmesh.new(); mats = []
    S.frame_set(1); bpy.context.view_layer.update()
    for o in list(TEMP.objects):
        if o.type != "MESH" or o.hide_render: continue
        me = o.data; mw = o.matrix_world
        tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(mw)
        m = me.materials[0]
        if m not in mats: mats.append(m)
        mi = mats.index(m)
        for f in tmp.faces: f.material_index = mi
        tmp_me = bpy.data.meshes.new("t"); tmp.to_mesh(tmp_me); tmp.free()
        bm.from_mesh(tmp_me) if False else None
        # append geometry
        offs = len(bm.verts); vmap = []
        for v in tmp_me.vertices: vmap.append(bm.verts.new(v.co))
        bm.verts.ensure_lookup_table()
        for p in tmp_me.polygons:
            try:
                f = bm.faces.new([vmap[i] for i in p.vertices]); f.material_index = mi; f.smooth = False
            except ValueError: pass
        bpy.data.meshes.remove(tmp_me)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    return me

CROWD_SRC = collection("crowdsrc"); CROWD_SRC.hide_render = True
POSES = {}
def make_milo_poses():
    specs = {"cheer": dict(arms=(2.8, 2.8), arms_side=(0.5, 0.5), face="excited"),
             "wave": dict(arms=(0.2, 2.9), arms_side=(0.1, 0.3), face="laugh"),
             "dab": dict(arms=(1.5, 1.2), arms_side=(1.2, -0.6), face="smug", head=(0.3, 0, 0.5)),
             "stand": dict(arms=(0.1, -0.1), arms_side=(0.1, 0.1), face="happy"),
             "shock": dict(arms=(1.9, 1.9), arms_side=(0.2, 0.2), face="shocked")}
    for k, sp in specs.items():
        clear_temp(); m = mk_milo(); m.root.location = (0, 0, 0)
        m.pose(1, arms=sp["arms"], arms_side=sp["arms_side"], head=sp.get("head", (0, 0, 0))); m.set_face(sp["face"], 1)
        POSES[k] = bake_char(m, f"milo_{k}")
    clear_temp()
make_milo_poses()
POSES_HI = dict(POSES)
import lib as _lib
_orig_box = _lib.box
def _flat_box(name, loc, size, m, rot=(0, 0, 0), parent=None, bevel=0.0, coll=None):
    return _orig_box(name, loc, size, m, rot=rot, parent=parent, bevel=0.0, coll=coll)
_lib.box = _flat_box; globals()["box"] = _flat_box
_saved = dict(POSES); make_milo_poses(); POSES_LO = dict(POSES); POSES.clear(); POSES.update(_saved)
_lib.box = _orig_box; globals()["box"] = _orig_box
print("LOD verts", len(POSES_HI["stand"].vertices), "->", len(POSES_LO["stand"].vertices), flush=True)

def get_fc(o, path, idx):
    ad = o.animation_data; act = ad.action
    if hasattr(act, "fcurves"):
        try: return act.fcurves.find(path, index=idx)
        except Exception: pass
    for layer in act.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot)
            if cb:
                fc = cb.fcurves.find(path, index=idx)
                if fc: return fc

def crowd_merged(coll, positions, seed=0, scale=1.0, poses=None):
    rnd = random.Random(seed); bm = bmesh.new(); mats = []
    poses = poses or list(POSES)
    for p in positions:
        me = POSES_LO[rnd.choice(poses)]
        for m in me.materials:
            if m not in mats: mats.append(m)
        remap = [mats.index(m) for m in me.materials]
        sc = scale * rnd.uniform(0.9, 1.05)
        mtx = Matrix.Translation(Vector(p)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z") @ Matrix.Scale(sc, 4)
        vs = [bm.verts.new(mtx @ v.co) for v in me.vertices]
        for poly in me.polygons:
            try:
                f = bm.faces.new([vs[i] for i in poly.vertices]); f.material_index = remap[poly.material_index]
            except ValueError: pass
    me2 = bpy.data.meshes.new("crowdmerged"); bm.to_mesh(me2); bm.free()
    for m in mats: me2.materials.append(m)
    o = bpy.data.objects.new("crowdmerged", me2); coll.objects.link(o); return o

def crowd(coll, positions, f_pop=None, pop_len=5, bob=True, scale=0.95, seed=0, poses=None, face_cam=None):
    rnd = random.Random(seed); out = []
    poses = poses or list(POSES)
    for i, p in enumerate(positions):
        o = bpy.data.objects.new("mc", POSES[rnd.choice(poses)]); coll.objects.link(o)
        o.location = p
        if face_cam is not None:
            d = Vector(face_cam) - Vector(p); o.rotation_euler = (0, 0, math.atan2(d.y, d.x) + math.pi / 2 + rnd.uniform(-0.5, 0.5))
        else: o.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
        s = scale * rnd.uniform(0.9, 1.05)
        if f_pop is not None:
            f0 = f_pop[i] if isinstance(f_pop, (list, tuple)) else f_pop
            for f, k in [(f0 - 1, 0.0), (f0, 0.01), (f0 + pop_len * 0.6, 1.25), (f0 + pop_len, 1.0)]:
                o.scale = (s * k,) * 3; o.keyframe_insert("scale", frame=int(f))
        else: o.scale = (s,) * 3
        if bob:
            o.keyframe_insert("location", index=2, frame=1)
            fc = get_fc(o, "location", 2)
            mod = fc.modifiers.new("NOISE"); mod.scale = rnd.uniform(4, 8); mod.strength = 0.9; mod.phase = rnd.uniform(0, 100)
        out.append(o)
    return out

# ---------------------------------------------------------------- classroom (x=-600)
CLASS = collection("class")
C0 = Vector((-600, 0, 0))
def Q(x, y, z): return (C0.x + x, C0.y + y, C0.z + z)
box("cfloor", Q(0, 0, -0.1), (30, 30, 0.2), mat("cfloor", (0.85, 0.72, 0.5)), coll=CLASS)
for k in range(-14, 15, 2): box("plank", Q(k, 0, 0.01), (0.05, 30, 0.01), mat("plankline", (0.75, 0.6, 0.42)), coll=CLASS)
cwall = mat("cwall", (1.0, 0.88, 0.55))
box("cwallb", Q(0, 12, 6), (30, 0.4, 12), cwall, coll=CLASS)
box("cwalll", Q(-13, 0, 6), (0.4, 30, 12), cwall, coll=CLASS)
box("cwallr", Q(13, 0, 6), (0.4, 30, 12), mat("cwall2", (0.6, 0.85, 0.95)), coll=CLASS)
box("cdado", Q(0, 11.75, 1.0), (30, 0.2, 2.0), mat("dado", (0.45, 0.7, 0.85)), coll=CLASS)
box("board", Q(0, 11.7, 6), (14, 0.2, 5.5), mat("board", (1, 1, 1)), coll=CLASS)
box("boardframe", Q(0, 11.78, 6), (14.6, 0.15, 6.1), mat("bframe", (0.5, 0.5, 0.55)), coll=CLASS)
text3d("1 + 1 = 3??", Q(-2.5, 11.55, 7.2), 1.3, mat("marker", (0.15, 0.3, 0.9)), coll=CLASS, extrude=0.02)
text3d("MAYBE 7?", Q(2.5, 11.55, 5.0), 1.5, mat("marker2", (0.95, 0.2, 0.4)), coll=CLASS, extrude=0.02)
for k in range(5): sphere("vstar", Q(5.5 + k * 0.4, 11.55, 6.4 + (k % 2) * 0.6), 0.18, mat("star", (1, 0.8, 0.1)), coll=CLASS, seg=6)
for k, (x, txt, col) in enumerate([(-9.5, "NO\nNUMBERS!", (1, 0.3, 0.3)), (9.5, "BE\nKIND", (0.3, 0.7, 1))]):
    box("cposter", Q(x, 11.7, 6.5), (3.6, 0.1, 3.4), mat(f"cposter{k}", col), coll=CLASS)
    text3d(txt, Q(x, 11.6, 6.5), 0.7, mat("white", (1, 1, 1)), coll=CLASS, extrude=0.02)
for k, y in enumerate((-4, 4)):
    box("cwin", Q(12.75, y, 6.5), (0.2, 5, 4.5), mat("skyglass", (0.6, 0.85, 1.0)), coll=CLASS)
    box("cwinf", Q(12.7, y, 6.5), (0.15, 5.4, 4.9), M["trim"], coll=CLASS)
# blank clock on wall
cyl("wclock", Q(-8, 11.6, 10), 1.1, 0.2, mat("clockface", (1, 1, 1)), rot=(math.pi / 2, 0, 0), coll=CLASS, verts=24)
cyl("wclockrim", Q(-8, 11.7, 10), 1.25, 0.2, mat("clockrim", (0.9, 0.2, 0.2)), rot=(math.pi / 2, 0, 0), coll=CLASS, verts=24)
text3d("?", Q(-8, 11.45, 10), 1.0, mat("qmark", (0.1, 0.1, 0.1)), coll=CLASS, extrude=0.02)
DESKS = []
for i, x in enumerate((-6.5, 0, 6.5)):
    for j, y in enumerate((-4, 1.5)):
        box("desk", Q(x, y, 2.0), (3.6, 2.4, 0.25), mat("desktop", (0.95, 0.85, 0.65)), coll=CLASS)
        for sx in (-1.6, 1.6):
            for sy in (-1, 1): box("dleg", Q(x + sx, y + sy, 1.0), (0.15, 0.15, 2.0), mat("metal", (0.45, 0.5, 0.6)), coll=CLASS)
        box("chair", Q(x, y - 2.3, 1.2), (1.8, 1.6, 0.2), mat("chair", [(0.2, 0.55, 0.95), (1, 0.45, 0.2), (0.3, 0.8, 0.4)][i]), coll=CLASS)
        box("chairback", Q(x, y - 3.05, 2.2), (1.8, 0.15, 2.0), mat("chair", [(0.2, 0.55, 0.95), (1, 0.45, 0.2), (0.3, 0.8, 0.4)][i]), coll=CLASS)
        DESKS.append((x, y))
box("tdesk", Q(-5, 8.5, 1.6), (5, 2.5, 3.2), mat("tdesk", (0.55, 0.35, 0.2)), coll=CLASS)
sphere("apple", Q(-4, 8.5, 3.45), 0.3, mat("applered", (0.9, 0.1, 0.1)), coll=CLASS)

# ---------------------------------------------------------------- kitchen (x=-600, y=200)
KIT = collection("kitchen")
K0 = Vector((-600, 200, 0))
def K(x, y, z): return (K0.x + x, K0.y + y, K0.z + z)
box("kfloor", K(0, 0, -0.1), (24, 24, 0.2), mat("tile", (0.95, 0.95, 0.92)), coll=KIT)
for x in range(-11, 12, 2):
    for y in range(-11, 12, 2):
        if (x + y) % 4 == 0: box("ktile", K(x, y, 0.01), (2, 2, 0.01), mat("tile2", (0.7, 0.85, 0.95)), coll=KIT)
box("kwallb", K(0, 9, 6), (24, 0.4, 12), mat("kwall", (1, 0.95, 0.6)), coll=KIT)
box("kwalll", K(-10, 0, 6), (0.4, 24, 12), mat("kwall", (1, 0.95, 0.6)), coll=KIT)
box("counter", K(-4, 7.8, 1.8), (10, 2.2, 3.6), mat("counter", (0.3, 0.6, 0.55)), coll=KIT)
box("countertop", K(-4, 7.8, 3.7), (10.2, 2.4, 0.25), mat("ctop", (0.95, 0.95, 0.95)), coll=KIT)
box("fridge", K(5.5, 7.6, 4), (3.2, 2.6, 8), mat("fridge", (0.85, 0.9, 0.95)), coll=KIT, bevel=0.2)
box("kwin", K(-4, 8.75, 7.2), (5, 0.2, 3.2), mat("skyglass", (0.6, 0.85, 1.0)), coll=KIT)
box("kwinf", K(-4, 8.7, 7.2), (5.4, 0.15, 3.6), M["trim"], coll=KIT)
# high chair
hc = mat("hchair", (1, 0.4, 0.55))
for sx in (-0.9, 0.9):
    for sy in (-0.9, 0.9): box("hcleg", K(1 + sx, 1 + sy, 1.6), (0.2, 0.2, 3.2), hc, coll=KIT)
box("hcseat", K(1, 1, 3.2), (2.2, 2.2, 0.3), hc, coll=KIT)
box("hctray", K(1, -0.3, 4.4), (2.6, 1.0, 0.2), mat("tray", (1, 1, 1)), coll=KIT)
box("hcback", K(1, 2.0, 4.6), (2.2, 0.2, 2.8), hc, coll=KIT)

# ---------------------------------------------------------------- characters
def _old_teacher():
    return Char("teacher", TEMP, (0.98, 0.82, 0.7), (0.25, 0.7, 0.45), (0.3, 0.3, 0.45), hair="bun", hair_col=(0.45, 0.25, 0.12),
                shoes=(0.4, 0.2, 0.1), extra=glasses, scale=1.15)
def mayor_extra(c):
    blk = mat("tophat", (0.08, 0.08, 0.1))
    cyl("hatbrim", (0, 0, 0.66), 0.95, 0.08, blk, parent=c.head, coll=c.coll, verts=20)
    cyl("hattop", (0, 0, 1.25), 0.62, 1.15, blk, parent=c.head, coll=c.coll, verts=20)
    cyl("hatband", (0, 0, 0.82), 0.64, 0.18, mat("hatband", (0.85, 0.1, 0.15)), parent=c.head, coll=c.coll, verts=20)
    box("stache", (0, -0.64, -0.12), (0.7, 0.05, 0.16), mat("stache", (0.35, 0.2, 0.1)), parent=c.head, coll=c.coll, bevel=0.03)
    box("sash", (0.2, -0.52, 1.0), (0.4, 0.06, 2.3), mat("sash", (0.85, 0.1, 0.15)), rot=(0, 0.6, 0), parent=c.hips, coll=c.coll)
    sphere("medal", (-0.4, -0.55, 1.5), 0.2, mat("gold", (1, 0.8, 0.1)), coll=c.coll, parent=c.hips)
def mk_mayor():
    return Char("mayor", TEMP, (0.98, 0.8, 0.68), (0.12, 0.18, 0.4), (0.12, 0.18, 0.4), hair="short", hair_col=(0.55, 0.55, 0.55),
                shoes=(0.05, 0.05, 0.05), extra=mayor_extra, scale=1.2)
def _old_baby():
    b = Char("baby", TEMP, (0.45, 0.27, 0.16), (0.7, 0.85, 1.0), (0.7, 0.85, 1.0), hair="short", hair_col=(0.1, 0.06, 0.04),
             shoes=(1, 1, 1), scale=0.5)
    b.head.scale = (1.5, 1.5, 1.5); return b

def seat(c, f0, f1, x, y, rotz=0.0, energy=0.6, face="happy", talk=False):
    c.place((x, y - 2.3, 0.0), rotz, f0)
    for f in range(f0, f1 + 1):
        t = f / 24
        c.pose(f, arms=(1.2, 1.2), arms_side=(0.1, 0.1), legs=(1.5, 1.5), hips_z=1.35 + 0.03 * math.sin(t * 3),
               head=(0.05 * math.sin(t * 2) * energy + (0.06 * math.sin(t * 10) if talk else 0), 0.1 * math.sin(t * 1.3) * energy, 0))

# ---------------------------------------------------------------- shots
TLN = "/home/claude/zara/ntimeline.json"
NDUR = {"n07b": 3.2, "n01": 5.5, "n02": 2.6, "n03": 1.9, "n04": 2.0, "n05": 2.8, "n06": 2.4, "n07": 2.0, "n08": 3.6, "n09": 1.6, "n10": 1.6,
        "n11": 3.0, "n12": 2.6, "n13": 1.4, "n14a": 1.8, "n14b": 1.6, "n14c": 1.6, "n14d": 1.5, "n15": 4.2, "n16": 3.2, "n17": 4.6}
if os.path.exists(TLN): NDUR.update(json.load(open(TLN))["dur"])

def show_set(town=False, room=False, cls=False, kit=False):
    WORLD.hide_render = not town; ROOM.hide_render = not room; CLASS.hide_render = not cls; KIT.hide_render = not kit

def n01(n):
    show_set(town=True)
    k = mk_kid(0); k.place((1.5, -6, 0), 0.2); k.idle(1, n, 1.0, talk=True); k.set_face("happy", 1)
    f = int(n * 0.55); k.set_face("excited", f - 6)
    k2 = crowd(TEMP, [(-1.8, -5.4, 0)], f_pop=f, bob=False)  # baked Milo? use kid clone instead
    for o in k2: bpy.data.objects.remove(o, do_unlink=True)
    c2 = mk_kid(0); c2.place((-1.8, -5.6, 0), -0.25); c2.idle(1, n, 1.2); c2.set_face("shocked", 1)
    for ff, s in [(f - 1, 0.0), (f, 0.01), (f + 3, 1.25), (f + 6, 1.0)]:
        c2.root.scale = (0.9 * s,) * 3; c2.root.keyframe_insert("scale", frame=ff)
    k.set_face("shocked", f + 4)
    cam_path(n, (0, -19, 4.2), (0, -5.5, 3.8), (0, -16.5, 4.1), (0, -5.5, 4.0), 28, 32)
def n02(n):
    show_set(town=True)
    for i, (x, y, r) in enumerate([(-2.5, -6, 0.3), (0.5, -7, 0), (3.2, -5.5, -0.3), (-5, -3, 0.5), (5.5, -3, -0.4)]):
        c = mk_kid(i) if i % 2 else (mk_gran() if i == 2 else mk_kid(i + 1)); c.place((x, y, 0), r)
        c.set_face("scared", 1)
        for f in range(1, n + 1):
            t = f / 24; c.pose(f, arms=(2.25, 2.25), arms_side=(-0.55, -0.55), head=(0.1, 0.1 * math.sin(t * 6 + i), 0.05 * math.sin(t * 9 + i)), hips_z=2.0 + 0.04 * math.sin(t * 8 + i))
    sign = box("signpost", (0, 2, 3), (0.3, 0.3, 6), mat("lpost", (0.15, 0.15, 0.18)), coll=TEMP)
    box("signboard", (0, 1.85, 6.6), (7, 0.25, 2.6), mat("signred", (0.9, 0.15, 0.15)), coll=TEMP, bevel=0.1)
    text3d("NO NUMBERS!", (0, 1.65, 6.6), 0.9, mat("white", (1, 1, 1)), coll=TEMP)
    cam_path(n, (0, -19, 4.5), (0, -3, 4.5), (0, -16, 4.2), (0, -3, 5), 28, 30)
def n03(n):
    show_set(town=True)
    r = mk_ray(); r.place((6.6, -4, 0.2), -0.64); r.set_face("smug", 1)
    sg = empty("sign", coll=TEMP); sg.parent = r.hips; sg.location = (0, -1.3, 1.4)
    box("lilsum", (0, 0, 0), (2.6, 0.1, 1.5), mat("cardboard", (0.85, 0.7, 0.45)), parent=sg, coll=TEMP)
    t = text3d("A LIL SUM", (0, -0.08, 0.15), 0.42, mat("marker", (0.1, 0.1, 0.1)), coll=TEMP, extrude=0.01); t.parent = sg
    t2 = text3d("$ ???", (0, -0.08, -0.4), 0.38, mat("marker2", (0.9, 0.1, 0.2)), coll=TEMP, extrude=0.01); t2.parent = sg
    for f in range(1, n + 1):
        tt = f / 24; sh_ = max(0, math.sin(tt * 3.2))
        r.pose(f, arms=(1.3, 1.3), arms_side=(0.25 + 0.3 * sh_, 0.25 + 0.3 * sh_), head=(-0.1 * sh_, 0, 0.25 * math.sin(tt * 2)), hips_z=2.0 + 0.15 * sh_)
    r.set_face("blink", int(n * 0.5)); r.set_face("smug", int(n * 0.5) + 3)
    cam_path(n, (0.5, -13, 4.8), (6.6, -4, 4.6), (1.5, -11.5, 4.6), (6.6, -4, 4.7), 32, 36)
def n04(n):
    show_set(room=True)
    ck = empty("cake", R(5, -4, 1.65), coll=TEMP)
    pink = mat("cake", (1, 0.75, 0.85))
    cyl("tier1", (0, 0, 0.6), 1.4, 1.2, pink, parent=ck, coll=TEMP, verts=24)
    cyl("tier2", (0, 0, 1.6), 1.0, 0.9, mat("cake2", (0.98, 0.98, 0.95)), parent=ck, coll=TEMP, verts=24)
    for k in range(10):
        a = k / 10 * 6.28; sphere("drip", (math.cos(a) * 1.4, math.sin(a) * 1.4, 1.05), 0.2, mat("icing", (0.95, 0.3, 0.6)), coll=TEMP, parent=ck, seg=8)
    q = text3d("?", (0, 0, 2.8), 1.2, mat("qcandle", (0.3, 0.7, 1)), coll=TEMP, extrude=0.15); q.parent = ck
    sphere("flame", (0.05, 0, 3.7), 0.15, mat("flame", (1, 0.8, 0.2)), coll=TEMP, parent=ck)
    for f in range(1, n + 1, 2):
        ck.rotation_euler = (0, 0, -0.4 + 0.5 * f / n); ck.keyframe_insert("rotation_euler", frame=f)
    cam_path(n, R(5, -12, 5.2), R(5, -4, 3.9), R(5, -10.5, 5.0), R(5, -4, 4.0), 36, 40)
def class_kids(n, zara_face="happy", milo_face="happy", groove=False):
    out = {}
    roster = [("zara", mk_zara, DESKS[1]), ("milo", mk_milo, DESKS[3]), ("k0", lambda: mk_kid(0), DESKS[0]),
              ("k1", lambda: mk_kid(1), DESKS[2]), ("k2", lambda: mk_kid(2), DESKS[4]), ("ivy", mk_ivy, DESKS[5])]
    for name, fn, (x, y) in roster:
        c = fn(); seat(c, 1, n, C0.x + x, y, 0.0)
        if groove:
            for f in range(1, n + 1):
                t = f / 24; s = math.sin(t * 2 * math.pi * 1.8 + hash(name) % 7)
                c.pose(f, arms=(1.3 + 0.5 * s, 1.3 - 0.5 * s), arms_side=(0.3, 0.3), legs=(1.5, 1.5), hips_z=1.35 + 0.08 * abs(s), head=(0.15 * s, 0.25 * s, 0.2 * s), twist=0.2 * s)
        c.set_face({"zara": zara_face, "milo": milo_face}.get(name, "happy"), 1)
        out[name] = c
    return out
def n05(n):
    show_set(cls=True)
    class_kids(n, "laugh", "excited", groove=True)
    t = mk_teacher(); t.place(Q(1.5, 9.5, 0), 0.0); t.set_face("happy", 1)
    for f in range(1, n + 1):
        tt = f / 24; s = math.sin(tt * 2 * math.pi * 1.8)
        t.pose(f, arms=(2.6 + 0.3 * s, 0.6), arms_side=(0.4, 0.2), hips_x=0.3 * s, twist=0.2 * s, head=(0, 0.2 * s, 0.2 * s), hips_z=2.0 + 0.1 * abs(s))
    cam_path(n, Q(0, -12, 7.5), Q(0, 4, 4.5), Q(0, -10, 7), Q(0, 4, 5), 26, 28)
def n06(n):
    show_set(cls=True)
    class_kids(n, "scared", "happy")
    t = mk_teacher(); t.place(Q(-3, 8.0, 0), 0.0); t.idle(1, n, 0.4, base_face="happy")
    cam_path(n, Q(-1.5, -9, 6.5), Q(-3, 8, 5.5), Q(-2.5, 1, 6.2), Q(-3, 8, 5.8), 30, 40)
def n07(n):
    show_set(cls=True)
    t = mk_teacher(); t.place(Q(-3, 8.0, 0), 0.0); t.idle(1, n, 0.8, base_face="happy", talk=True)
    for f in range(1, n + 1): t.arms[1].rotation_euler = (-1.5, 0.2, 0); t.arms[1].keyframe_insert("rotation_euler", frame=f)
    cam_path(n, Q(-2.6, 1.5, 6.6), Q(-3, 8, 6.4), Q(-2.7, 2.6, 6.6), Q(-3, 8, 6.5), 45, 52)
def n07b(n):
    show_set(cls=True)
    m = mk_milo(); x, y = DESKS[3]; seat(m, 1, n, C0.x + x, y, 0.0)
    seq = ["scared", "determined", "scared", "shocked", "determined"]
    for k, fc in enumerate(seq): m.set_face(fc, 1 + int(k * n / len(seq)))
    for f in range(1, n + 1):
        t = f / 24; m.neck.rotation_euler = (0.05 * math.sin(t * 5), 0.35 * math.sin(t * 2.2), 0.06 * math.sin(t * 13)); m.neck.keyframe_insert("rotation_euler", frame=f)
    cam_path(n, Q(x + 0.2, y - 9.5, 4.3), Q(x, y - 2.3, 4.15), Q(x + 0.1, y - 6.8, 4.25), Q(x, y - 2.3, 4.2), 45, 60)
CLONE_SPOTS = [(-9, -8), (-3.5, -7.5), (3.5, -7.5), (9, -8), (-10, 3), (10, 4), (-3, 6.5), (3.5, 7), (8, 9)]
def milo_main(n, face="happy"):
    m = mk_milo(); x, y = DESKS[3]; seat(m, 1, n, C0.x + x, y, 0.0); m.set_face(face, 1); return m
def n08(n):
    show_set(cls=True)
    m = milo_main(n, "blink")
    m.set_face("happy", 4)
    talk_end = int(n * 0.45)
    for f in range(1, talk_end):
        m.neck.rotation_euler = (0.05 * math.sin(f / 2), 0.25, 0.2); m.neck.keyframe_insert("rotation_euler", frame=f)
    pops = [talk_end + 3 + k * 3 for k in range(9)]
    crowd(TEMP, [Q(x, y, 0) for x, y in CLONE_SPOTS], f_pop=pops, pop_len=5, face_cam=Q(0, -14, 0), seed=8)
    m.set_face("excited", pops[0])
    for k in range(1, 4): k_ = mk_kid(k - 1)
    cam_path(n, Q(6.5, -5, 4.8), Q(6.5, 1.5, 4.0), Q(3, -14, 8.5), Q(0, 1, 3), 34, 22)
def n09(n):
    show_set(cls=True)
    milo_main(n, "excited")
    crowd(TEMP, [Q(x, y, 0) for x, y in CLONE_SPOTS], face_cam=Q(0, -14, 0), seed=9)
    cam_path(n, Q(0, -15, 9), Q(0, 1, 3), Q(2, -14, 8), Q(0, 1, 3), 22, 24)
def _unused_n10(n):
    show_set(cls=True)
    t = mk_teacher(); t.place(Q(-3, 8.0, 0), 0.0); t.set_face("shocked", 1)
    for f in range(1, n + 1):
        t.pose(f, arms=(2.0, 2.0), arms_side=(-0.35, -0.35), head=(-0.1, 0, 0.04 * math.sin(f * 2)), hips_z=2.0 - 0.1 * min(1, f / 8))
    crowd(TEMP, [Q(x, y, 0) for x, y in CLONE_SPOTS[5:]], seed=10)
    cam_path(n, Q(-2.8, 2.0, 6.6), Q(-3, 8, 6.4), Q(-2.9, 3.6, 6.6), Q(-3, 8, 6.5), 45, 55)
def n11(n):
    show_set(cls=True)
    # silly montage: two Milos bonk heads, one spins, one falls over, one dances on desk
    a = mk_milo(); b = mk_milo(); a.set_face("happy", 1); b.set_face("happy", 1)
    hit = int(n * 0.35)
    a.walk(1, hit, Q(-6, -2, 0), Q(-1.3, -2, 0)); b.walk(1, hit, Q(4, -2, 0), Q(-0.1, -2, 0))
    for c, d in ((a, -1), (b, 1)):
        c.set_face("shocked", hit)
        for f in range(hit, n + 1):
            u = min(1, (f - hit) / 10)
            c.move(f, Vector(c.root.location) + Vector((d * 0.15, 0, 0)) if f == hit else c.root.location)
            c.pose(f, arms=(0.6, 0.6), arms_side=(0.8, 0.8), lean=-0.5 * u, head=(-0.4 * u, 0, 0.3 * math.sin(f)), hips_z=2.0 - 0.6 * u)
    s1 = mk_milo(); s1.place(Q(6.5, 1.5, 2.15), 0); s1.dance(1, n, 0); s1.set_face("laugh", 1)
    s2 = mk_milo(); s2.place(Q(-7, 4, 0), 0); s2.set_face("excited", 1)
    for f in range(1, n + 1):
        s2.move(f, Q(-7, 4, 0), f * 0.5); s2.pose(f, arms=(1.6, 1.6), arms_side=(1.2, 1.2), hips_z=2.0)
    cam_path(n, Q(0, -13, 6), Q(0, 1, 3.5), Q(-1, -11, 5.5), Q(-0.5, 0, 3.5), 26, 28)
def n12(n):
    show_set(cls=True)
    m = mk_milo(); m.place(Q(0, 1.5, 2.15), 0.0); m.set_face("excited", 1)
    for f in range(1, n + 1):
        t = f / 24; s = math.sin(t * 9)
        m.pose(f, arms=(0.3, 0.3), arms_side=(2.4 + 0.2 * s, 2.4 + 0.2 * s), hips_z=2.0 + 0.1 * abs(s), head=(-0.2 + 0.05 * s, 0, 0.1 * s))
    crowd(TEMP, [Q(x, y, 0) for x, y in CLONE_SPOTS], face_cam=Q(0, 1.5, 0), seed=12)
    cam_path(n, Q(0.5, -7, 3.5), Q(0, 1.5, 6.0), Q(0.4, -5.5, 3.2), Q(0, 1.5, 6.4), 34, 40)
def n13(n):
    show_set(cls=True)
    z = mk_zara(); x, y = DESKS[1]; seat(z, 1, n, C0.x + x, y, 0.0); z.set_face("smug", 1)
    for f in range(1, n + 1): z.pose(f, arms=(1.35, 1.35), arms_side=(-0.75, -0.75), legs=(1.5, 1.5), hips_z=1.35, head=(0.05, 0, 0.12))
    z.set_face("blink", int(n * 0.45)); z.set_face("smug", int(n * 0.45) + 4)
    crowd(TEMP, [Q(x + dx, y + dy, 0) for dx, dy in [(-4, 3), (4, 3), (-3, -6), (3.5, -6.5)]], seed=13, face_cam=Q(x, y - 12, 0))
    cam_path(n, Q(x + 0.1, y - 7.5, 4.3), Q(x, y - 2.3, 4.1), Q(x + 0.1, y - 6.5, 4.2), Q(x, y - 2.3, 4.15), 42, 48)
def n14a(n):
    show_set(cls=True)
    pts = [Q(x + random.uniform(-0.4, 0.4), y + random.uniform(-0.4, 0.4), 0) for x in range(-11, 12, 2) for y in range(-10, 11, 2)]
    random.shuffle(pts)
    pops = [1 + int(i / len(pts) * n * 0.8) for i in range(len(pts))]
    crowd(TEMP, pts, f_pop=pops, pop_len=4, seed=14, face_cam=Q(0, -14, 0))
    cam_path(n, Q(0, -13, 10), Q(0, 2, 2), Q(0, -12, 13), Q(0, 3, 1), 22, 20)
STREET_PTS = None
def n14b(n):
    show_set(town=True)
    pts = []
    for (cx, cy, z, w, D) in HOOD_ROOFS:
        if abs(cy) > 80: continue
        for k in range(8): pts.append((cx + random.uniform(-D / 2 + 1, D / 2 - 1), cy + random.uniform(-w / 2 + 0.6, w / 2 - 0.6), z))
    for x in range(-7, 8, 2):
        for y in range(-80, 80, 2): pts.append((x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5), 0.2))
    crowd_merged(TEMP, pts, seed=16, scale=1.0)
    cam_path(n, (14, -58, 38), (0, -5, 3), (20, -40, 52), (0, 8, 2), 26, 24)
def n14c(n):
    show_set(town=True)
    pts = []
    for yy in range(-40, 40, 7):
        sy = yy + 3.5 - 7 * 0.24
        for s_ in range(4):
            for k in (-0.5, 0.5):
                pts.append((-10 + 0.5 + s_ * 0.45, sy + k * 0.8, 0.5 + (3 - s_) * 0.5))
    pts += [(x + random.uniform(-0.4, 0.4), y + random.uniform(-0.4, 0.4), 0.2) for x in (-8.4, -7.2, -6.0) for y in range(-40, 40, 1)]
    pops = [1 + int(max(0, (p[1] + 40) / 80) * n * 0.6) for p in pts]
    crowd(TEMP, pts, f_pop=pops, pop_len=4, seed=17, face_cam=(2, -20, 0), scale=0.8)
    cam_path(n, (2.5, -22, 3.5), (-8, -2, 2.5), (3, -18, 4), (-8, 6, 2.5), 26, 26)
def n14d(n):
    show_set(town=True)
    pts = [(9.2 - k * 0.9, -7.2 + dy, 0.2) for k in range(8) for dy in (-0.7, 0.7)]
    pops = [3 + k * 2 for k in range(len(pts))]
    crowd(TEMP, pts, f_pop=pops, pop_len=4, seed=18, face_cam=(-4, -18, 0), poses=["shock", "cheer", "wave"])
    pts2 = [(x + random.uniform(-0.4, 0.4), y + random.uniform(-0.4, 0.4), 0.2) for x in range(-4, 7, 2) for y in range(-2, 20, 2)]
    crowd(TEMP, pts2, seed=19)
    cam_path(n, (-2.5, -19, 4.5), (7, -5, 4.5), (-1.5, -16.5, 4.8), (7, -5, 4.8), 28, 32)
def n15(n):
    show_set(town=True)
    r = mk_ray(); r.place((6.4, -7.0, 0.2), -0.5); r.set_face("scared", 1)
    for f in range(1, n + 1):
        t = f / 24; s_ = math.sin(t * 14)
        r.pose(f, arms=(0.3, 0.3), arms_side=(2.1 + 0.5 * s_, 2.1 - 0.5 * math.sin(t * 11)), head=(-0.1, 0.12 * s_, 0.1 * s_), hips_z=2.0 + 0.06 * abs(s_))
    r.set_face("shocked", int(n * 0.55))
    pts = [(x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5), 0.2) for x in range(-7, 5, 2) for y in range(-4, 40, 2)]
    near = [p for p in pts if p[1] < 8]; far = [p for p in pts if p[1] >= 8]
    crowd(TEMP, near, seed=20)
    roofs = []
    for (cx, cy, z, w, D) in HOOD_ROOFS:
        if -10 < cy < 60: roofs += [(cx + random.uniform(-4, 4), cy + random.uniform(-2.5, 2.5), z) for _ in range(6)]
    crowd_merged(TEMP, far + roofs, seed=21)
    cam_path(n, (2.2, -16.5, 5.0), (6.4, -7, 5.2), (3.0, -14.8, 5.0), (6.4, -7, 5.3), 34, 40)
def _old_n15(n):
    show_set(town=True)
    my = mk_mayor(); my.place((0, -4, 0), 0.0); my.set_face("scared", 1)
    for f in range(1, n + 1):
        t = f / 24; s = math.sin(t * 14)
        my.pose(f, arms=(0.3, 0.3), arms_side=(2.1 + 0.5 * s, 2.1 - 0.5 * math.sin(t * 11)), head=(-0.1, 0.12 * s, 0.1 * s), hips_z=2.0 + 0.05 * abs(s))
    my.set_face("shocked", int(n * 0.5))
    box("podium", (0, -5.4, 1.7), (3.2, 1.6, 3.4), mat("podium", (0.6, 0.35, 0.2)), coll=TEMP, bevel=0.1)
    box("pplate", (0, -6.25, 2.4), (1.6, 0.1, 0.8), mat("gold", (1, 0.8, 0.1)), coll=TEMP)
    cyl("mic", (0, -5.6, 4.0), 0.06, 1.2, mat("metal", (0.45, 0.5, 0.6)), rot=(0.4, 0, 0), coll=TEMP)
    sphere("mich", (0, -5.85, 4.55), 0.18, mat("pupil", (0.05, 0.05, 0.05)), coll=TEMP)
    pts = [(x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5), 0.2) for x in range(-14, 15, 2) for y in range(2, 40, 2)]
    crowd(TEMP, pts, seed=18)
    for (side, y), (hx, hy) in HOUSES.items():
        if -10 < hy < 60:
            crowd(TEMP, [(hx + random.uniform(-4, 4), hy + random.uniform(-5, 5), 13.5) for _ in range(10)], seed=int(hy))
    cam_path(n, (0, -14.5, 5.2), (0, -4, 5.4), (0, -12.8, 5.2), (0, -4, 5.5), 34, 40)
def n16(n):
    show_set(kit=True)
    b = mk_baby(); b.place(K(1, 1.0, 3.35), 0.0); b.set_face("happy", 1)
    for f in range(1, n + 1):
        t = f / 24; b.pose(f, arms=(1.4 + 0.6 * math.sin(t * 6), 1.4 + 0.6 * math.sin(t * 6 + 2)), arms_side=(0.3, 0.3), legs=(1.5, 1.5), hips_z=2.0, head=(0.1 * math.sin(t * 3), 0.2 * math.sin(t * 2), 0))
    z = mk_zara(); z.place(K(4.2, -0.5, 0), 0.9); z.set_face("scared", 1); z.idle(1, n, 0.5, base_face="scared", blink=False)
    crowd(TEMP, [K(-5.5 + k * 1.1, 10.5, 4.2 + (k % 2) * 0.4) for k in range(6)], seed=19, poses=["wave", "cheer"], face_cam=K(-4, -10, 0))
    cam_path(n, K(1.5, -7.5, 5.2), K(2.2, 0, 4.4), K(1.6, -6.2, 5.1), K(2.2, 0, 4.5), 32, 36)
def n17(n):
    show_set(kit=True)
    b = mk_baby(); b.place(K(1, 1.0, 3.35), 0.0)
    a = int(n * 0.25)
    b.set_face("happy", 1); b.set_face("determined", a); b.set_face("excited", a + 10)
    for f in range(1, n + 1):
        t = f / 24; b.pose(f, arms=(1.0, 1.0), arms_side=(0.3, 0.3), legs=(1.5, 1.5), hips_z=2.0, head=(-0.15 * min(1, f / a), 0, 0))
    cam_path(n, K(1.05, -4.0, 5.6), K(1, 1, 5.4), K(1.05, -2.6, 5.55), K(1, 1, 5.45), 45, 60)

SHOTS = {k: v for k, v in globals().items() if k.startswith("n") and len(k) >= 3 and k[1:3].isdigit() and callable(v)}
os.makedirs(OUT, exist_ok=True)
for name in sorted(SHOTS):
    if ONLY and name not in ONLY: continue
    n = max(10, int(round(NDUR[name] * FPS)))
    clear_temp(); S.frame_set(1)
    SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    if STILL:
        S.frame_set(int(n * 0.8)); S.render.filepath = f"{OUT}/preview_{name}.png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
