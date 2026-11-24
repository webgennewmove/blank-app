import bpy, math, random, sys, os
from mathutils import Vector

OUT = "/home/claude/ep1/stills"
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = set(argv[0].split(",")) if argv and argv[0] != "all" else None
SAMPLES = int(argv[1]) if len(argv) > 1 else 24
RES = (900, 1600)

random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.engine = "CYCLES"
S.cycles.device = "CPU"
S.cycles.samples = SAMPLES
S.cycles.use_denoising = True
S.cycles.max_bounces = 4
S.cycles.diffuse_bounces = 2
S.cycles.glossy_bounces = 1
S.cycles.transmission_bounces = 0
S.render.resolution_x, S.render.resolution_y = RES
S.render.image_settings.file_format = "PNG"
S.view_settings.view_transform = "AgX"
S.view_settings.look = "AgX - Punchy"

# ---------- helpers ----------
_mats = {}
def mat(name, col, rough=0.55, emit=None, strength=0.0):
    key = (name, col, emit, strength)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    _mats[key] = m; return m

import bmesh
_mesh = {}
def _mk(key, builder, m, smooth=False):
    k = (key, m.name)
    if k in _mesh: return _mesh[k]
    me = bpy.data.meshes.new(str(k)); bm = bmesh.new(); builder(bm)
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    _mesh[k] = me; return me

def _obj(name, me, loc, rot, scale, parent, coll):
    o = bpy.data.objects.new(name, me)
    (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    if parent: o.parent = parent
    return o

def box(name, loc, size, m, rot=(0, 0, 0), parent=None, bevel=0.0, coll=None):
    if bevel:
        sz = tuple(round(v, 3) for v in size)
        def b(bm, sz=sz, bevel=bevel):
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts: v.co = Vector((v.co.x * sz[0], v.co.y * sz[1], v.co.z * sz[2]))
            bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=bevel, segments=2, affect="EDGES")
        me = _mk(("bcube", sz, bevel), b, m, smooth=False)
        return _obj(name, me, loc, rot, (1, 1, 1), parent, coll)
    me = _mk("cube", lambda bm: bmesh.ops.create_cube(bm, size=1.0), m)
    return _obj(name, me, loc, rot, size, parent, coll)

def cyl(name, loc, r, depth, m, rot=(0, 0, 0), verts=16, parent=None, coll=None):
    me = _mk(("cyl", verts), lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=1, radius2=1, depth=1), m, smooth=True)
    return _obj(name, me, loc, rot, (r, r, depth), parent, coll)

def sphere(name, loc, r, m, coll=None, seg=24):
    me = _mk(("sph", seg), lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1), m, smooth=True)
    return _obj(name, me, loc, (0, 0, 0), (r, r, r), None, coll)

def light(kind, loc, energy, col, coll=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new("L", kind); ld.energy = energy; ld.color = col
    o = bpy.data.objects.new("L", ld); (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot; return o

def collection(name):
    c = bpy.data.collections.new(name); S.collection.children.link(c); return c

def move(o, c):
    for uc in o.users_collection: uc.objects.unlink(o)
    c.objects.link(o)

def rod(name, a, b, r, m, coll):
    a, b = Vector(a), Vector(b); d = b - a
    o = cyl(name, (a + b) / 2, r, d.length, m, verts=8, coll=coll)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o

# ---------- materials ----------
CLAY = [(0.62, 0.27, 0.16), (0.70, 0.36, 0.20), (0.55, 0.24, 0.15), (0.74, 0.45, 0.28)]
M = dict(
    sand=mat("sand", (0.78, 0.62, 0.42), 0.9),
    street=mat("street", (0.66, 0.50, 0.34), 0.95),
    dark=mat("dark", (0.04, 0.03, 0.03), 0.8),
    wood=mat("wood", (0.30, 0.17, 0.08), 0.7),
    trim=mat("trim", (0.10, 0.55, 0.55), 0.5),
    leaf=mat("leaf", (0.12, 0.40, 0.14), 0.7),
    bark=mat("bark", (0.38, 0.28, 0.20), 0.9),
    ocean=mat("ocean", (0.03, 0.10, 0.22), 0.15),
    moon=mat("moon", (1, 1, 1), 0.5, (0.85, 0.9, 1.0), 6.0),
    lamp=mat("lamp", (1, 0.6, 0.2), 0.5, (1.0, 0.55, 0.15), 12.0),
    gold=mat("goldthread", (1, 0.6, 0.1), 0.3, (1.0, 0.55, 0.05), 7.0),
    goldeye=mat("goldeye", (1, 0.7, 0.1), 0.3, (1.0, 0.6, 0.05), 14.0),
    fire=mat("fire", (1, 0.4, 0.1), 0.5, (1.0, 0.35, 0.05), 25.0),
    white=mat("eyewhite", (0.97, 0.97, 0.97), 0.3),
    black=mat("pupil", (0.01, 0.01, 0.01), 0.3),
    mouth=mat("mouth", (0.35, 0.03, 0.05), 0.5),
    cloth_s=mat("stripe", (0.85, 0.2, 0.15), 0.7),
    cloth_y=mat("stripe2", (0.95, 0.75, 0.2), 0.7),
    drum=mat("drum", (0.45, 0.22, 0.10), 0.6),
    drumskin=mat("skin", (0.85, 0.75, 0.6), 0.8),
    spider=mat("spider", (0.05, 0.035, 0.03), 0.45),
    spgold=mat("spgold", (0.9, 0.6, 0.1), 0.35),
    bed=mat("bed", (0.85, 0.80, 0.70), 0.9),
    wall_in=mat("wallin", (0.60, 0.38, 0.24), 0.9),
    sky_plane=mat("skyplane", (0.1, 0.05, 0.25), 0.5, (0.12, 0.08, 0.35), 1.5),
)
SKIN = [(0.30, 0.17, 0.09), (0.40, 0.24, 0.13), (0.24, 0.13, 0.07), (0.48, 0.30, 0.17)]
SHIRTS = [(0.9, 0.85, 0.7), (0.15, 0.45, 0.75), (0.85, 0.55, 0.1), (0.2, 0.6, 0.35), (0.7, 0.2, 0.3), (0.95, 0.9, 0.3)]

# ---------- world ----------
world = bpy.data.worlds.new("w"); S.world = world; world.use_nodes = True
BG = world.node_tree.nodes["Background"]
def sky(col, strength):
    BG.inputs[0].default_value = (*col, 1); BG.inputs[1].default_value = strength

# ---------- character ----------
def face(head, kind, s=1.0):
    """Build face parts on -Y side of a head cube of edge 1.2 (local)."""
    z0 = 0.05
    eye_r = {"neutral": .14, "shocked": .22, "scared": .18, "angry": .14, "closed": .14, "bored": .14}[kind]
    pup_r = {"neutral": .08, "shocked": .06, "scared": .05, "angry": .08, "closed": 0, "bored": .08}[kind]
    for sx in (-0.26, 0.26):
        if kind == "closed":
            box("lid", (sx, -0.61, z0), (0.28, 0.02, 0.05), M["black"], parent=head)
            continue
        e = cyl("eye", (sx, -0.605, z0 + 0.04), eye_r, 0.02, M["white"], rot=(math.pi / 2, 0, 0), parent=head)
        py = z0 + 0.04 - (0.05 if kind == "bored" else 0)
        cyl("pup", (sx * 0.95, -0.62, py), pup_r, 0.02, M["black"], rot=(math.pi / 2, 0, 0), parent=head)
        if kind in ("scared", "angry"):
            ang = 0.35 if (kind == "scared") == (sx < 0) else -0.35
            box("brow", (sx, -0.61, z0 + 0.3), (0.28, 0.02, 0.05), M["black"], rot=(0, ang, 0), parent=head)
        if kind == "bored":
            box("lid", (sx, -0.615, z0 + 0.1), (0.32, 0.02, 0.09), mat("lidskin", (0.25, 0.14, 0.08)), parent=head)
    if kind == "shocked":
        o = cyl("mouth", (0, -0.605, -0.3), 0.15, 0.02, M["mouth"], rot=(math.pi / 2, 0, 0), parent=head); o.scale = (0.15, 0.21, 0.02)
    elif kind == "scared":
        o = cyl("mouth", (0, -0.605, -0.3), 0.08, 0.02, M["mouth"], rot=(math.pi / 2, 0, 0), parent=head); o.scale = (0.13, 0.065, 0.02)
    elif kind in ("neutral", "closed"):
        box("mouth", (0, -0.61, -0.28), (0.26, 0.02, 0.06), M["mouth"], parent=head)
    elif kind == "bored":
        box("mouth", (0.05, -0.61, -0.28), (0.22, 0.02, 0.05), M["mouth"], rot=(0, 0.15, 0), parent=head)
    else:
        box("mouth", (0, -0.61, -0.28), (0.3, 0.02, 0.05), M["mouth"], parent=head)

def person(name, loc, rotz=0, skin=0, shirt=(0.9, 0.85, 0.7), expr="neutral", scarf=False,
           hair="short", arms=(0, 0), coll=None, scale=1.0, elder=False):
    root = bpy.data.objects.new(name, None); (coll or S.collection).objects.link(root)
    root.location = loc; root.rotation_euler = (0, 0, rotz); root.scale = (scale,) * 3
    sk = mat(f"skin{skin}", SKIN[skin], 0.5)
    sh = mat(f"shirt{shirt}", shirt, 0.7)
    pants = mat("pants", (0.25, 0.2, 0.15) if not elder else (0.5, 0.15, 0.2), 0.7)
    for sx in (-0.5, 0.5):
        box("leg", (sx, 0, 1.0), (0.95, 0.95, 2.0), pants if not elder else sh, parent=root, bevel=0.06, coll=coll)
    box("torso", (0, 0, 3.0), (2.0, 1.0, 2.0), sh, parent=root, bevel=0.08, coll=coll)
    for i, sx in enumerate((-1.5, 1.5)):
        piv = bpy.data.objects.new("armpiv", None); (coll or S.collection).objects.link(piv)
        piv.parent = root; piv.location = (sx, 0, 3.8); piv.rotation_euler = (arms[i], 0, 0)
        box("arm", (0, 0, -0.85), (0.95, 0.95, 2.0), sk, parent=piv, bevel=0.06, coll=coll)
    head = box("head", (0, 0, 4.65), (1.2, 1.2, 1.2), sk, parent=root, bevel=0.1, coll=coll)
    hc = (0.03, 0.02, 0.02) if not elder else (0.85, 0.85, 0.85)
    hm = mat(f"hair{hc}", hc, 0.8)
    if hair == "short":
        box("hair", (0, 0.05, 0.55), (1.26, 1.2, 0.22), hm, parent=head, coll=coll)
    elif hair == "wrap":
        box("wrap", (0, 0.05, 0.62), (1.3, 1.3, 0.45), mat("wrap", (0.8, 0.2, 0.5), 0.7), parent=head, coll=coll)
        box("wrapknot", (0, 0.2, 0.95), (0.6, 0.6, 0.35), mat("wrap", (0.8, 0.2, 0.5), 0.7), parent=head, coll=coll)
    elif hair == "puffs":
        for sx in (-0.45, 0.45):
            box("puff", (sx, 0.1, 0.65), (0.5, 0.5, 0.5), hm, parent=head, bevel=0.15, coll=coll)
        box("hair", (0, 0.05, 0.55), (1.26, 1.2, 0.2), hm, parent=head, coll=coll)
    face(head, expr)
    for o in head.children:
        if coll and coll not in o.users_collection: move(o, coll)
    if scarf:
        orange = mat("scarf", (1.0, 0.42, 0.05), 0.7)
        box("scarf", (0, -0.02, 4.05), (2.1, 1.15, 0.35), orange, parent=root, bevel=0.08, coll=coll)
        box("scarftail", (0.55, -0.55, 3.4), (0.4, 0.12, 1.0), orange, parent=root, coll=coll)
    return root

# ---------- town ----------
TOWN = collection("town")
LAMPS = collection("lamps")
DAYC = collection("day")
NIGHTPPL = collection("nightppl")
WEB = collection("web")
WEBUP = collection("webup")
SPIDER = collection("spider")
ROOM = collection("room")
KOFIWIN = collection("kofiwin")

box("ground", (0, 0, -0.5), (400, 400, 1), M["sand"], coll=TOWN)
box("sea", (0, 190, -0.3), (600, 180, 1), M["ocean"], coll=TOWN)
for x in range(-63, 64, 14):
    box("streety", (x + 7, 0, 0.02), (4.6, 140, 0.05), M["street"], coll=TOWN)
for y in range(-63, 64, 14):
    box("streetx", (0, y + 7, 0.02), (140, 4.6, 0.05), M["street"], coll=TOWN)

ROOFS = []
def house(x, y, w, d, h, c):
    clay = mat(f"clay{c}", CLAY[c], 0.9)
    box("house", (x, y, h / 2), (w, d, h), clay, coll=TOWN, bevel=0.15)
    box("roofrim", (x, y, h + 0.25), (w + 0.3, d + 0.3, 0.5), mat(f"rim{c}", tuple(v * 0.8 for v in CLAY[c]), 0.9), coll=TOWN)
    box("trim", (x, y, h - 0.6), (w + 0.05, d + 0.05, 0.3), M["trim"], coll=TOWN)
    for side in (-1, 1):  # doors+windows on both x faces & y faces
        box("door", (x + side * (w / 2 + 0.01), y, 1.6), (0.08, 1.8, 3.2), M["wood"], coll=TOWN)
        box("win", (x + side * (w / 2 + 0.01), y + d * 0.28, h * 0.62), (0.08, 1.2, 1.2), M["dark"], coll=TOWN)
        box("door", (x, y + side * (d / 2 + 0.01), 1.6), (1.8, 0.08, 3.2), M["wood"], coll=TOWN)
        box("win", (x - w * 0.28, y + side * (d / 2 + 0.01), h * 0.62), (1.2, 0.08, 1.2), M["dark"], coll=TOWN)
    for i in range(random.randint(1, 3)):
        cyl("pot", (x + side * (w / 2 + 0.9), y - d * 0.3 + i * 1.1, 0.5), 0.45, 1.0, mat("pot", (0.55, 0.2, 0.08), 0.8), coll=TOWN)
    ROOFS.append(Vector((x, y, h + 0.5)))

def palm(x, y, h=9):
    for i in range(6):
        cyl("trunk", (x + i * 0.08, y, i * h / 6 + h / 12), 0.35 - i * 0.02, h / 6, M["bark"], coll=TOWN)
    for a in range(7):
        ang = a * 2 * math.pi / 7
        box("frond", (x + math.cos(ang) * 1.8, y + math.sin(ang) * 1.8, h - 0.2), (3.6, 0.9, 0.15), M["leaf"],
            rot=(0, 0.35, ang), coll=TOWN)

for gx in range(-63, 64, 14):
    for gy in range(-63, 64, 14):
        if math.hypot(gx, gy) < 16: continue
        if gx == -7 and gy == -21: continue  # kofi's house special
        house(gx + random.uniform(-0.5, 0.5), gy + random.uniform(-0.5, 0.5),
              random.uniform(8.5, 9.6), random.uniform(8.5, 9.6), random.uniform(5.5, 8.0), random.randint(0, 3))
for _ in range(40):
    x = random.choice(range(-63, 64, 14)) + 7 + random.choice((-2.6, 2.6))
    y = random.uniform(-70, 70)
    if math.hypot(x, y) > 18: palm(x, y, random.uniform(7, 11))

# Kofi's house (front faces -y toward plaza is +y... keep window on -y face)
KH = Vector((0, -16, 0))
KHO = box("khouse", (-7, -21, 3.75), (9, 7, 7.5), mat("clay1", CLAY[1], 0.9), coll=TOWN)
KCUT = box("kcut", (-5, -17.5, 4.6), (2.4, 3.0, 2.2), M["dark"], coll=TOWN); KCUT.hide_render = True; KCUT.hide_viewport = True
md = KHO.modifiers.new("cut", "BOOLEAN"); md.object = KCUT; md.operation = "DIFFERENCE"
light("POINT", (-5, -18.3, 5.2), 40, (1, 0.6, 0.3), KOFIWIN)
box("khrim", (-7, -21, 7.75), (9.3, 7.3, 0.5), mat("rim1", tuple(v * 0.8 for v in CLAY[1]), 0.9), coll=TOWN)
box("khwin_back", (-5, -18.95, 4.6), (2.4, 0.1, 2.2), M["dark"], coll=TOWN)
box("khwin_frame_t", (-5, -17.4, 5.8), (2.8, 0.3, 0.25), M["wood"], coll=TOWN)
box("khwin_frame_b", (-5, -17.4, 3.4), (2.8, 0.3, 0.25), M["wood"], coll=TOWN)
box("khshutter", (-3.3, -17.2, 4.6), (0.15, 1.2, 2.2), M["wood"], rot=(0, 0, 0.9), coll=TOWN)
box("khdoor", (-9.3, -17.45, 1.6), (1.8, 0.1, 3.2), M["wood"], coll=TOWN)
ROOFS.append(Vector((-7, -21, 8)))

# Baobab
cyl("baobab", (0, 0, 6), 3.2, 12, M["bark"], verts=24, coll=TOWN)
cyl("baobab2", (0, 0, 13), 2.4, 3, M["bark"], verts=24, coll=TOWN)
for a in range(8):
    ang = a * math.pi / 4
    end = Vector((math.cos(ang) * 8, math.sin(ang) * 8, 18 + (a % 2) * 2))
    rod("branch", (0, 0, 14), end, 0.6, M["bark"], TOWN)
    box("canopy", end + Vector((0, 0, 1.2)), (5, 5, 2.2), M["leaf"], rot=(0, 0, ang), coll=TOWN, bevel=0.3)
BAOBAB_TOP = Vector((0, 0, 21))

# moon
sphere("moon", (0, 420, 150), 26, M["moon"], coll=TOWN)

# lanterns along streets
for x in range(-56, 57, 14):
    for y in range(-60, 61, 14):
        px, py = x + 2.4, y + 7
        if math.hypot(px, py) < 15: continue
        box("post", (px, py, 2.0), (0.25, 0.25, 4.0), M["wood"], coll=LAMPS)
        box("lantern", (px, py, 4.3), (0.6, 0.6, 0.8), M["lamp"], coll=LAMPS)
        L = light("POINT", (px, py, 4.0), 250, (1, 0.55, 0.2), LAMPS); L.data.shadow_soft_size = 0.5

# market stalls + crowd + drums (day collection)
for i in range(10):
    ang = i * 2 * math.pi / 10 + 0.2
    x, y = math.cos(ang) * 11, math.sin(ang) * 11
    if y < -6 and abs(x) < 6: continue
    box("stall", (x, y, 1.0), (3, 2, 2), M["wood"], rot=(0, 0, ang), coll=DAYC)
    box("awning", (x, y, 3.4), (3.4, 2.4, 0.2), M["cloth_s"] if i % 2 else M["cloth_y"], rot=(0.15, 0, ang), coll=DAYC)
    for j in range(3):
        cyl("fruit", (x + random.uniform(-1, 1), y + random.uniform(-.5, .5), 2.2), 0.3, 0.5,
            mat("fr", (random.choice([(0.9, 0.5, 0.1), (0.8, 0.1, 0.1), (0.4, 0.7, 0.1)])), 0.6), coll=DAYC)
DRUMS = collection("drums")
for i, dx in enumerate((-3.2, 0, 3.2)):
    cyl("drum", (dx, -7, 1.1), 0.9, 2.2, M["drum"], verts=20, coll=DRUMS)
    cyl("drumskin", (dx, -7, 2.22), 0.88, 0.05, M["drumskin"], verts=20, coll=DRUMS)
crowd = []
for i in range(22):
    ang = random.uniform(0, 2 * math.pi); r = random.uniform(5, 15)
    x, y = math.cos(ang) * r, math.sin(ang) * r - 4
    if math.hypot(x, y) < 4.2: continue
    if abs(x - 6) < 2.5 and abs(y + 12) < 3: continue
    person(f"crowd{i}", (x, y, 0), rotz=random.uniform(0, 6.28), skin=random.randint(0, 3),
           shirt=random.choice(SHIRTS), expr="neutral", hair=random.choice(["short", "wrap", "puffs"]),
           arms=(random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6)), coll=DAYC, scale=random.uniform(0.85, 1.05))

# night townspeople in doorways along street x=7 (shocked, silent)
NPPL = []
for i, (x, y, rz) in enumerate([(-3.2, -35, 1.57), (3.2, -33, -1.57), (-3.2, -49, 1.57), (3.2, -47, -1.57),
                                 (-3.2, -62, 1.57), (3.2, -61, -1.57)]):
    NPPL.append(person(f"np{i}", (x, y, 0), rotz=rz, skin=i % 4, shirt=SHIRTS[i % 6], expr="shocked",
                       hair=["short", "wrap", "puffs"][i % 3], arms=(-0.4, 0.3), coll=NIGHTPPL))

# gold web: radial + rings over roofs from baobab top
for a in range(16):
    ang = a * 2 * math.pi / 16
    pts = [BAOBAB_TOP]
    for r in (18, 34, 52, 70):
        pts.append(Vector((math.cos(ang) * r, math.sin(ang) * r, 9 - r * 0.04)))
    for p, q in zip(pts, pts[1:]): rod("web", p, q, 0.12, M["gold"], WEB)
for r in (18, 34, 52, 70):
    for a in range(16):
        a0, a1 = a * 2 * math.pi / 16, (a + 1) * 2 * math.pi / 16
        z = 9 - r * 0.04
        rod("ring", (math.cos(a0) * r, math.sin(a0) * r, z), (math.cos(a1) * r, math.sin(a1) * r, z), 0.1, M["gold"], WEB)
# thread to kofi window
rod("kthread", BAOBAB_TOP, (-5, -17.6, 4.6), 0.14, M["gold"], WEB)
# threads pulling up from roofs (voices)
for p in ROOFS[::2]:
    rod("up", p, p + Vector((random.uniform(-4, 4), random.uniform(-4, 4), 60)), 0.08, M["gold"], WEBUP)
    sphere("orb", p + Vector((random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(8, 30))), 0.5, M["gold"], coll=WEBUP, seg=8)

# Anansi on baobab
sp = bpy.data.objects.new("anansi", None); SPIDER.objects.link(sp); sp.location = (0, -6, 27)
abd = sphere("abdomen", (0, 4.5, 2.5), 4.2, M["spider"], coll=SPIDER); abd.scale = (4.2, 5.25, 3.57); abd.parent = sp
for k in range(4):
    st = box("stripe", (0, 2 + k * 1.7, 5.6 - abs(k - 1.5) * 0.4), (3.2 - abs(k - 1.5) * 0.6, 0.35, 0.3), M["spgold"], coll=SPIDER); st.parent = sp
ceph = box("ceph", (0, -1.2, 2.4), (4.2, 4.0, 3.0), M["spider"], coll=SPIDER, bevel=0.5); ceph.parent = sp
# eyes 4 pairs
for k, (ex, ez, r) in enumerate([(0.7, 3.2, 0.45), (-0.7, 3.2, 0.45), (1.5, 3.0, 0.3), (-1.5, 3.0, 0.3),
                                  (0.45, 3.8, 0.22), (-0.45, 3.8, 0.22), (1.1, 2.4, 0.25), (-1.1, 2.4, 0.25)]):
    e = sphere("speye", (ex, -3.25, ez), r, M["goldeye"], coll=SPIDER, seg=12); e.parent = sp
for k in (-1, 1):
    f = box("fang", (k * 0.5, -3.3, 1.2), (0.35, 0.35, 1.0), M["spgold"], rot=(0.3, 0, 0), coll=SPIDER); f.parent = sp
for i in range(4):
    for sgn in (-1, 1):
        y0 = -2.6 + i * 1.3
        knee = Vector((sgn * (6 + i * 0.3), y0 - 1.5 + i * 0.8, 6.5 + (1 - abs(i - 1.5)) * 1.0))
        foot = Vector((sgn * (11 + i * 0.6), y0 - 3 + i * 2.2, -5))
        base = Vector((sgn * 1.8, y0, 2.4))
        for a, b in ((base, knee), (knee, foot)):
            l = rod("leg", a, b, 0.42, M["spider"], SPIDER); l.parent = sp; l.location = l.location
        bnd = sphere("kneegold", knee, 0.55, M["spgold"], coll=SPIDER, seg=10); bnd.parent = sp
# fix parenting offsets: objects were created in world coords then parented; compensate
for o in SPIDER.objects:
    if o.parent == sp: o.matrix_parent_inverse = sp.matrix_world.inverted() @ sp.matrix_world.inverted().inverted() if False else o.matrix_parent_inverse
sp.location = (0, -6, 27)

# ---------- bedroom interior (far away at x=500) ----------
R0 = Vector((500, 0, 0))
def R(x, y, z): return (R0.x + x, R0.y + y, R0.z + z)
box("floor", R(0, 0, -0.1), (16, 16, 0.2), mat("rug", (0.55, 0.35, 0.2), 0.9), coll=ROOM)
box("rug", R(0, -1, 0.02), (6, 4, 0.05), M["cloth_s"], coll=ROOM)
box("wallback", R(0, 7, 5), (16, 0.4, 10), M["wall_in"], coll=ROOM)
box("wallL", R(-7, 0, 5), (0.4, 16, 10), M["wall_in"], coll=ROOM)
box("wallR", R(7, 0, 5), (0.4, 16, 10), M["wall_in"], coll=ROOM)
box("ceiling", R(0, 0, 10), (16, 16, 0.3), M["wall_in"], coll=ROOM)
for bx in (-4, 0, 4):
    box("beam", R(bx, 0, 9.6), (0.6, 16, 0.6), M["wood"], coll=ROOM)
# window hole in back wall: build back wall as frame around a hole (hole at x=2.2,z=5, 3x3)
bpy.data.objects["wallback"].scale = (16, 0.4, 10)
hole = box("winhole_cut", R(2.2, 7, 5.2), (3, 1, 3), M["dark"], coll=ROOM)
md = bpy.data.objects["wallback"].modifiers.new("cut", "BOOLEAN"); md.object = hole; md.operation = "DIFFERENCE"
hole.hide_render = True
box("winframe", R(2.2, 6.75, 3.6), (3.4, 0.5, 0.25), M["wood"], coll=ROOM)
box("shutterL", R(0.3, 6.2, 5.2), (0.15, 1.4, 3), M["wood"], rot=(0, 0, -0.8), coll=ROOM)
box("skyout", R(2.2, 30, 8), (60, 0.5, 40), M["sky_plane"], coll=ROOM)
sphere("moonout", R(5.5, 29, 12), 2.2, M["moon"], coll=ROOM)
for k in range(6):
    rod("webout", R(-10 + k * 4, 28, 2 + k), R(8 - k * 3, 28, 16 - k), 0.07, M["gold"], ROOM)
box("bed", R(-3, 2, 0.7), (4.2, 7, 1.4), M["wood"], coll=ROOM)
box("mattress", R(-3, 2, 1.6), (4, 6.8, 0.6), M["bed"], coll=ROOM)
box("blanket", R(-3, 0.7, 1.95), (4.05, 4.2, 0.2), mat("blanket", (0.1, 0.5, 0.55), 0.8), coll=ROOM)
box("pillow", R(-3, 4.6, 2.1), (2.6, 1.2, 0.5), M["bed"], coll=ROOM, bevel=0.2)
# fire pit for Nana scene (room corner)
FIRE = collection("fire")
cyl("pit", R(4, -3, 0.25), 1.2, 0.5, mat("stone", (0.3, 0.3, 0.3), 0.9), coll=FIRE)
for k in range(5):
    box("flame", R(4 + random.uniform(-.4, .4), -3 + random.uniform(-.4, .4), 0.9 + k * 0.25), (0.6 - k * 0.1, 0.6 - k * 0.1, 0.6), M["fire"],
        rot=(0, 0, k), coll=FIRE)
F = light("POINT", R(4, -3, 2.0), 1500, (1, 0.45, 0.15), FIRE)
# corner gold eyes (shot 30)
CORNER = collection("cornereyes")
for ex in (-0.6, 0.6):
    sphere("ceye", R(-6.3 + ex, 6.2, 6.5), 0.32, M["goldeye"], coll=CORNER, seg=12)
for ex in (-0.35, 0.35):
    sphere("ceye2", R(-6.3 + ex, 6.2, 7.3), 0.18, M["goldeye"], coll=CORNER, seg=12)

# ---------- lights ----------
LIGHTS = {}
def sun(name, rot, energy, col, angle=0.05):
    o = light("SUN", (0, 0, 50), energy, col, rot=rot); o.data.angle = angle; LIGHTS[name] = o; return o
sun("moonlight", (math.radians(55), 0, math.radians(180)), 2.8, (0.6, 0.62, 1.0))
sun("daylight", (math.radians(40), 0, math.radians(30)), 4.0, (1.0, 0.92, 0.8))
sun("dusk", (math.radians(78), 0, math.radians(160)), 3.0, (1.0, 0.45, 0.4))
W = light("AREA", R(2.2, 8, 5.5), 900, (0.5, 0.55, 1.0), rot=(math.radians(90), 0, 0)); W.data.size = 3; LIGHTS["winlight"] = W
RF = light("POINT", R(0.5, -3, 7.5), 1400, (0.55, 0.6, 1.0)); RF.data.shadow_soft_size = 3; LIGHTS["roomfill"] = RF

# ---------- camera ----------
CAM = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); S.collection.objects.link(CAM); S.camera = CAM
def cam(loc, at, lens=28):
    CAM.location = loc; CAM.data.lens = lens; CAM.data.clip_end = 2000
    d = Vector(at) - Vector(loc)
    CAM.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

ALLC = [TOWN, LAMPS, DAYC, NIGHTPPL, WEB, WEBUP, SPIDER, ROOM, KOFIWIN, DRUMS, FIRE, CORNER]
TEMP = collection("temp")
def scene_mode(mode, show):
    for c in ALLC: c.hide_render = c.name not in show
    for n, l in LIGHTS.items(): l.hide_render = True
    lampE = 250
    if mode == "night":
        sky((0.06, 0.05, 0.2), 1.6); LIGHTS["moonlight"].hide_render = False
    elif mode == "day":
        sky((0.3, 0.58, 1.0), 1.4); LIGHTS["daylight"].hide_render = False
    elif mode == "dusk":
        sky((0.85, 0.42, 0.45), 0.8); LIGHTS["dusk"].hide_render = False
    elif mode == "roomnight":
        sky((0.01, 0.01, 0.03), 0.2); LIGHTS["winlight"].hide_render = False; LIGHTS["roomfill"].hide_render = False
    elif mode == "roomfire":
        sky((0.01, 0.01, 0.02), 0.1)
    elif mode == "black":
        sky((0, 0, 0), 0)
    for o in list(TEMP.objects): bpy.data.objects.remove(o, do_unlink=True)

def tmp_person(*a, **k):
    k["coll"] = TEMP; return person(*a, **k)

def render(name):
    S.render.filepath = f"{OUT}/{name}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name, flush=True)

# ---------- shots ----------
def s01():
    scene_mode("night", {"town", "lamps"}); cam((0, -105, 48), (0, 20, 4), 26)
def s02():
    scene_mode("night", {"town", "lamps"}); cam((0, -70, 1.8), (0, -10, 6), 24)
def s03():
    scene_mode("day", {"town", "day", "drums"})
    scene_mode("day", {"town", "drums"})
    tmp_person("x1", (-3, 12, 0), rotz=2.5, skin=2, shirt=SHIRTS[1], hair="wrap")
    tmp_person("x2", (-13, 10, 0), rotz=-0.4, skin=3, shirt=SHIRTS[2])
    tmp_person("kofi", (-8, 5, 0), rotz=0.2, skin=1, shirt=(0.92, 0.88, 0.75), expr="neutral", scarf=True, arms=(0.2, -0.3))
    cam((-9.4, -2.5, 4.9), (-8, 5, 4.4), 45)
def s04():
    scene_mode("day", {"town", "day", "drums"}); cam((-14.5, -4, 6.0), (6, 6, 2.5), 24)
def s05():
    scene_mode("dusk", {"town", "drums"})
    tmp_person("drummer", (0, -9.6, 0), rotz=0, skin=2, shirt=(0.7, 0.2, 0.3), expr="neutral", hair="short", arms=(-2.6, -2.6), elder=True)
    cam((0.8, -17.5, 2.0), (0, -8, 6.5), 30)
def s06():
    scene_mode("night", {"town", "drums", "lamps"}); cam((0.5, -12.5, 3.2), (0, -7, 1.8), 32)
def s07():
    scene_mode("night", {"town"}); cam((0, -70, 1.8), (0, -10, 6), 24)
def s08():
    scene_mode("roomfire", {"room", "fire"})
    tmp_person("nana", R(1.5, -1, 0), rotz=math.radians(-25), skin=0, shirt=(0.55, 0.15, 0.35), expr="neutral", hair="wrap", elder=True, arms=(-0.4, -0.4))
    cam(R(-2.5, -7.5, 4.6), R(1.5, -1, 4.2), 32)
def s09():
    scene_mode("roomfire", {"room", "fire"})
    tmp_person("nana", R(1.5, -1, 0), rotz=math.radians(-5), skin=0, shirt=(0.55, 0.15, 0.35), expr="angry", hair="wrap", elder=True)
    cam(R(1.45, -5.5, 4.8), R(1.5, -1, 4.75), 70)
def kofi_bed(expr):
    p = tmp_person("kofi", R(-3, 1.0, 1.95), rotz=math.radians(180), skin=1, shirt=(0.92, 0.88, 0.75), expr=expr, scarf=False)
    p.rotation_euler = (math.radians(-90), 0, 0)
    p.location = R(-3, -1.5, 2.6)
    return p
def s10():
    scene_mode("roomnight", {"room"}); kofi_bed("bored"); cam(R(-3, 3.5, 7.5), R(-3, 4.2, 2.6), 30)
def s13():
    scene_mode("roomnight", {"room"}); kofi_bed("shocked"); cam(R(-3, 2.3, 5.0), R(-3, 4.3, 2.6), 40)
def s12():
    scene_mode("night", {"town"}); cam((0, -45, 14), (0, 0, 4), 26)
def s14():
    scene_mode("night", {"town", "drums"}); cam((-1.5, -16, 1.2), (0, -7, 2.0), 30)
def s15():
    scene_mode("roomnight", {"room"})
    tmp_person("kofi", R(1.6, 4.2, 0), rotz=math.radians(180), skin=1, shirt=(0.92, 0.88, 0.75), expr="neutral", scarf=True, arms=(-1.2, 0))
    cam(R(0.2, -1.5, 6.0), R(2.4, 10, 5.5), 28)
def s16():
    scene_mode("night", {"town", "web"}); cam((10, -110, 60), (0, 0, 5), 24)
def s17():
    scene_mode("night", {"town", "web", "lamps"}); cam((0, -42, 10), (0, 0, 14), 30)
def s18():
    scene_mode("night", {"town", "web", "spider"}); cam((0.3, -24, 1.6), (0, -6, 27), 26)
    LIGHTS["moonlight"].rotation_euler = (math.radians(100), 0, math.radians(180))
def s19():
    scene_mode("night", {"town", "web", "spider"}); cam((4, -22, 16), (0, -9, 28), 32)
def s20():
    scene_mode("roomnight", {"room"})
    tmp_person("kofi", R(2.2, 4.2, 0), rotz=math.radians(10), skin=1, shirt=(0.92, 0.88, 0.75), expr="scared", scarf=True, arms=(-2.4, 0.2))
    cam(R(1.6, -2.5, 4.8), R(2.2, 4.2, 4.6), 42)
def s21():
    scene_mode("night", {"town", "web", "spider"}); cam((0, -20, 29), (0, -9, 29), 38)
def s22():
    scene_mode("night", {"town", "web", "spider"}); cam((0.3, -15, 30.5), (0, -9, 30.2), 45)
def s23():
    scene_mode("roomnight", {"room"})
    tmp_person("kofi", R(2.2, 4.2, 0), rotz=math.radians(5), skin=1, shirt=(0.92, 0.88, 0.75), expr="shocked", scarf=True)
    cam(R(2.1, 0.8, 4.75), R(2.2, 4.2, 4.7), 50)
def s24():
    scene_mode("roomnight", {"room"})
    tmp_person("kofi", R(2.2, 4.2, 0), rotz=math.radians(-15), skin=1, shirt=(0.92, 0.88, 0.75), expr="shocked", scarf=True, arms=(-0.3, -0.3))
    cam(R(-0.5, -3.5, 4.0), R(2.2, 4.2, 4.0), 36)
def s25():
    scene_mode("night", {"town", "web", "spider", "lamps", "kofiwin"})
    tmp_person("kofiwin", (-5, -18.2, -0.05), rotz=math.pi, skin=1, shirt=(0.92, 0.88, 0.75), expr="shocked", scarf=True)
    cam((-1.5, -8.5, 2.5), (-5.5, -18, 7.5), 28)
def s26():
    scene_mode("night", {"town", "nightppl", "lamps", "web"}); cam((0, -75, 2.5), (0, -40, 4), 30)
def s27():
    scene_mode("night", {"town", "lamps"})
    for i, (x, y) in enumerate([(-2.2, -36), (2.2, -36.5), (0, -39.5)]):
        tmp_person(f"q{i}", (x, y, 0), rotz=0.1 * (i - 1), skin=i, shirt=SHIRTS[i + 1], expr="shocked", hair=["wrap", "short", "puffs"][i], arms=(-0.3, 0.3))
    cam((0, -48, 4.8), (0, -37, 4.0), 32)
def s28():
    scene_mode("night", {"town", "web", "webup"}); cam((20, -120, 45), (0, 0, 25), 24)
def s29():
    scene_mode("night", {"town", "lamps", "kofiwin"})
    tmp_person("kofiwin", (-5, -18.2, -0.05), rotz=math.pi, skin=1, shirt=(0.92, 0.88, 0.75), expr="scared", scarf=True)
    cam((-5, -9.5, 4.3), (-5, -18, 4.6), 40)
def s30():
    scene_mode("roomnight", {"room", "cornereyes"}); LIGHTS["winlight"].data.energy = 250
    tmp_person("kofi", R(1.0, 1.0, 0), rotz=math.radians(-40), skin=1, shirt=(0.92, 0.88, 0.75), expr="scared", scarf=True)
    cam(R(4.5, -6.5, 5.5), R(-4.5, 5.5, 5.8), 26)
def s31():
    scene_mode("roomnight", {"room"}); LIGHTS["winlight"].data.energy = 900
    tmp_person("kofi", R(2.2, 4.2, 0), rotz=math.radians(-5), skin=1, shirt=(0.92, 0.88, 0.75), expr="shocked", scarf=True)
    cam(R(2.4, 1.6, 4.75), R(2.2, 4.2, 4.7), 55)

SHOTS = {k: v for k, v in globals().items() if k.startswith("s") and k[1:].isdigit()}
for name in sorted(SHOTS):
    if ONLY and name not in ONLY: continue
    LIGHTS["moonlight"].rotation_euler = (math.radians(55), 0, math.radians(180))
    SHOTS[name]()
    render(name)
