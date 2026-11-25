"""IN MY TOWN: 'My Whole Town Glows... Except Me'. Sets + assets (exec'd by glow.py after world.py/eevee_patch/rcast).
Main Street at night (snow, shops, bus stop), the town square with the giant Christmas tree, edge of town (sign + rock).
Glowing townsfolk, giant moths, Rico's flashlight + mom's bell."""
import bmesh
from mathutils import Vector, Quaternion, Matrix

def emat(name, col, strength=4.0, base=None, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*(base or col), 1); b.inputs["Emission Color"].default_value = (*col, 1)
    b.inputs["Emission Strength"].default_value = strength; m.diffuse_color = (*col, 1)
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = "BLENDED"
        except Exception: m.blend_method = "BLEND"
    return m
def light(name, typ, loc, energy, col, size=1.0, rot=(0, 0, 0), coll=None, radius=None, parent=None):
    L = bpy.data.lights.new(name, typ); L.energy = energy; L.color = col
    if typ == "AREA": L.size = size
    if typ in ("POINT", "SPOT") and radius is not None: L.shadow_soft_size = radius
    o = bpy.data.objects.new(name, L); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o
def text3d(body, loc, size, m, rot=(math.pi / 2, 0, 0), coll=None, extrude=0.02, parent=None):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.font = FONTB; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    o.data.materials.append(m); return o
def merged_boxes(name, items, mats, coll):
    bm = bmesh.new()
    for loc, size, mi, rz in items:
        r = bmesh.ops.create_cube(bm, size=1.0)
        mtx = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(bm, matrix=mtx, verts=r["verts"])
        for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = mi
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

# ---------------------------------------------------------------- shared palette
SNOW = mat("snow", (0.75, 0.8, 0.92), 0.8); ASPH = mat("asph", (0.05, 0.055, 0.07), 0.9); CURB = mat("curb", (0.35, 0.37, 0.42), 0.8)
BRICK = [mat(f"brick{i}", c, 0.85) for i, c in enumerate([(0.32, 0.1, 0.08), (0.18, 0.22, 0.32), (0.3, 0.24, 0.16), (0.14, 0.2, 0.16), (0.36, 0.3, 0.38)])]
TRIM = mat("trim", (0.85, 0.82, 0.75), 0.6); DARKWIN = mat("darkwin", (0.02, 0.025, 0.04), 0.2)
WINWARM = emat("winwarm", (1.0, 0.6, 0.25), 2.2, base=(0.3, 0.2, 0.1))
PINEM = mat("pinem", (0.03, 0.14, 0.07), 0.9); TRUNK = mat("trunkm", (0.16, 0.09, 0.05), 0.9)
GOLD = mat("goldm", (1.0, 0.72, 0.12), 0.25); METAL = mat("metal", (0.3, 0.32, 0.36), 0.35)

# ---------------------------------------------------------------- MAIN STREET (origin), street along Y, shops at x=+-11
MAIN = collection("main")
box("mground", (0, 0, -0.1), (120, 160, 0.2), SNOW, coll=MAIN)
box("road", (0, 0, 0.01), (12, 160, 0.04), ASPH, coll=MAIN)
for sx in (-1, 1):
    box("curb", (sx * 6.2, 0, 0.12), (0.5, 160, 0.24), CURB, coll=MAIN)
    box("walk", (sx * 8.4, 0, 0.1), (4.0, 160, 0.2), mat("walk", (0.55, 0.58, 0.66), 0.85), coll=MAIN)
for y in range(-74, 76, 6): box("lane", (0, y, 0.035), (0.25, 3, 0.01), mat("lanepaint", (0.7, 0.65, 0.4), 0.8), coll=MAIN)
SIGNS = ["BAKERY", "TOYS", "PIZZA", "BOOKS", "DINER", "GIFTS", "CANDY", "HARDWARE", "BARBER", "ARCADE", "FLOWERS", "COCOA"]
SIGNC = [(1, 0.3, 0.3), (0.3, 0.9, 1), (1, 0.8, 0.2), (0.5, 1, 0.5), (1, 0.45, 0.85), (0.6, 0.5, 1)]
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")
def shop(x, y, face, k, coll):
    rnd = random.Random(k * 31 + int(y)); w = rnd.choice((7.5, 8.5, 9.5)); h = rnd.choice((9, 11, 13)); d = 8
    bm_ = BRICK[k % len(BRICK)]; cx = x - face * d / 2
    box("shopbody", (cx, y, h / 2), (d, w, h), bm_, coll=coll)
    box("shopsnowroof", (cx, y, h + 0.25), (d + 0.4, w + 0.3, 0.5), SNOW, coll=coll, bevel=0.15)
    box("cornice", (x + face * 0.15, y, h - 0.4), (0.5, w + 0.2, 0.6), TRIM, coll=coll)
    fx = x + face * 0.05
    box("storefront", (fx, y, 2.4), (0.2, w - 1.4, 3.6), WINWARM if rnd.random() < 0.55 else DARKWIN, coll=coll)
    box("door", (fx + face * 0.02, y + w / 2 - 1.4, 1.7), (0.22, 1.3, 3.2), mat("doorm", (0.12, 0.06, 0.04), 0.6), coll=coll)
    awn = mat(f"awn{k % 4}", [(0.7, 0.08, 0.1), (0.08, 0.35, 0.18), (0.1, 0.2, 0.55), (0.75, 0.55, 0.1)][k % 4], 0.8)
    box("awning", (x + face * 0.9, y, 6.2), (1.8, w - 0.8, 0.25), awn, rot=(0, face * 0.35, 0), coll=coll)
    box("awnsnow", (x + face * 0.9, y, 6.45), (1.6, w - 0.9, 0.18), SNOW, rot=(0, face * 0.35, 0), coll=coll)
    for r in range(1, int((h - 5) // 3) + 1):
        for c in (-1, 1):
            box("uwin", (fx, y + c * w / 4.5, 4.5 + r * 2.9), (0.2, 1.6, 1.9), WINWARM if rnd.random() < 0.4 else DARKWIN, coll=coll)
    sc = SIGNC[k % len(SIGNC)]
    text3d(SIGNS[k % len(SIGNS)], (x + face * 0.35, y, 7.1), 1.0, emat(f"neon{k}", sc, 6.0), rot=(math.pi / 2, 0, face * math.pi / 2), coll=coll)
    # Christmas garland along the cornice: small glowing bulbs
    for j in range(int(w)):
        sphere("bulb", (x + face * 0.4, y - w / 2 + 0.5 + j, h - 0.85 - 0.25 * math.sin(j * 1.2)), 0.12,
               emat(f"bulb{j % 4}", [(1, 0.2, 0.2), (0.2, 1, 0.4), (1, 0.8, 0.2), (0.3, 0.5, 1)][j % 4], 8.0), coll=coll, seg=8)
k_ = 0
for y in range(-72, 76, 10):
    shop(-10.5, y, 1, k_, MAIN); shop(10.5, y + 4, -1, k_ + 5, MAIN); k_ += 1
# bus stop (right side, y = -6)
BUS = Vector((8.6, -6, 0))
for sy in (-2.6, 2.6): box("bpost", BUS + Vector((0.9, sy, 3.2)), (0.18, 0.18, 6.4), METAL, coll=MAIN)
box("broof", BUS + Vector((0.9, 0, 6.5)), (2.4, 5.8, 0.25), METAL, coll=MAIN)
box("broofsnow", BUS + Vector((0.9, 0, 6.72)), (2.3, 5.6, 0.22), SNOW, coll=MAIN, bevel=0.08)
box("bback", BUS + Vector((1.45, 0, 2.6)), (0.08, 5.4, 3.2), mat("bglass", (0.25, 0.32, 0.4), 0.1), coll=MAIN)
box("bbench", BUS + Vector((1.0, 0, 1.0)), (0.9, 4.2, 0.18), mat("bench", (0.3, 0.16, 0.06), 0.6), coll=MAIN)
box("bsign", BUS + Vector((0.9, 2.9, 5.6)), (0.1, 0.9, 0.9), emat("bsignm", (0.2, 0.5, 1.0), 2.0), coll=MAIN)
# no streetlights: empty lamp-post bases where Steve stands (gag)
MAIN_LIGHTS = []
MAIN_LIGHTS.append(light("moonfill", "AREA", (-30, -40, 40), 3500, (0.45, 0.6, 1.0), size=40, rot=(math.radians(45), 0, math.radians(-40)), coll=MAIN))

# ---------------------------------------------------------------- TOWN SQUARE + giant Christmas tree (x = 300)
SQ = collection("square"); Q = Vector((300, 0, 0))
box("qground", Q + Vector((0, 0, -0.1)), (160, 160, 0.2), SNOW, coll=SQ)
cyl("plaza", Q + Vector((0, 0, 0.02)), 22, 0.08, mat("plazam", (0.42, 0.44, 0.5), 0.8), coll=SQ, verts=48)
TREE_H = 34.8
PINEM2 = mat("pinem2", (0.04, 0.24, 0.1), 0.85)
TREE = empty("xtree", Q, coll=SQ)
TIERS = [(1.0, 11.0), (5.8, 9.4), (10.6, 7.8), (15.4, 6.2), (20.2, 4.6), (25.0, 3.2)]   # (ledge base z, cone radius)
for zb, r in TIERS:
    cone("tier", (0, 0, zb + 3.6), r, 7.2, PINEM2, verts=18, coll=SQ, parent=TREE)
    cyl("ledge", (0, 0, zb + 0.1), r + 1.7, 0.4, PINEM, coll=SQ, parent=TREE, verts=40)
    cyl("ledgesnow", (0, 0, zb + 0.36), r + 1.72, 0.12, SNOW, coll=SQ, parent=TREE, verts=40)
cone("tiertop", (0, 0, 29.8 + 2.5), 2.6, 5.0, PINEM2, verts=16, coll=SQ, parent=TREE)
cyl("xtrunk", (0, 0, 0.5), 1.4, 1.0, TRUNK, coll=SQ, parent=TREE)
LEDGE_TOP = 0.42
STAR_OFF = emat("staroff", (0.25, 0.2, 0.08), 0.0, base=(0.35, 0.3, 0.12))
STAR = empty("star", (0, 0, TREE_H + 1.4), parent=TREE, coll=SQ)
for a_ in range(5):
    box("starpt", (0, 0, 0), (0.5, 0.3, 3.0), STAR_OFF, rot=(0, a_ * 2 * math.pi / 5, 0), parent=STAR, coll=SQ, bevel=0.1)
def tree_spots(spacing=4.3, arc=125):
    """people spots on the ledges, front arc (camera side = -Y). -> list of (tier, angle, loc(local), rotz)"""
    out = []
    for ti, (zb, r) in enumerate(TIERS):
        R = r + 0.9; n = max(1, int(2 * math.pi * R * (2 * arc / 360) / spacing))
        for j in range(n):
            a = math.radians(-90 - arc + (2 * arc) * (j + 0.5) / n)
            out.append((ti, a, Vector((math.cos(a) * R, math.sin(a) * R, zb + LEDGE_TOP)), a + math.pi / 2))
    return out
SPOTS = tree_spots()
GAP = min(range(len(SPOTS)), key=lambda k: (SPOTS[k][0] != 2, abs(SPOTS[k][1] + math.pi / 2)))   # Rico: tier 2, dead front
TREE_LIGHTS = []
for i in range(6):
    a = -math.pi / 2 + (i - 2.5) * 0.55; c_ = [(1, 0.2, 0.15), (0.15, 1, 0.3), (1, 0.75, 0.1), (0.2, 0.45, 1), (1, 0.3, 0.8), (0.2, 0.95, 1)][i]
    TREE_LIGHTS.append(light("treeglow", "POINT", Q + Vector((math.cos(a) * 16, math.sin(a) * 16, 4 + (i % 3) * 9)), 2500, c_, coll=SQ, radius=3))
for L in TREE_LIGHTS: L.data.use_shadow = False
# square surroundings: dark town buildings
for i in range(14):
    a = i / 14 * 2 * math.pi; r = 48 + (i % 3) * 4
    if -2.4 < ((a + math.pi) % (2 * math.pi)) - math.pi < -0.7: continue   # keep the camera side (-Y) open
    p = Q + Vector((math.cos(a) * r, math.sin(a) * r, 0)); hh = 10 + (i * 7) % 9
    o = box("qbld", p + Vector((0, 0, hh / 2)), (10, 10, hh), BRICK[i % 5], coll=SQ); o.rotation_euler = (0, 0, a)
    box("qbldsnow", p + Vector((0, 0, hh + 0.2)), (10.4, 10.4, 0.4), SNOW, coll=SQ).rotation_euler = (0, 0, a)
    for z in range(3, int(hh) - 1, 3):
        w_ = box("qwin", p + Vector((-math.cos(a) * 5.05, -math.sin(a) * 5.05, z)), (0.2, 6, 1.4), WINWARM if (i + z) % 3 else DARKWIN, coll=SQ)
        w_.rotation_euler = (0, 0, a)
SQ_LIGHTS = [light("sqmoon", "AREA", Q + Vector((-30, -40, 50)), 4000, (0.45, 0.6, 1.0), size=50, rot=(math.radians(40), 0, math.radians(-35)), coll=SQ)]

# ---------------------------------------------------------------- EDGE OF TOWN (x = -300): sign, rock, pines, dark field
EDGE = collection("edge"); G = Vector((-300, 0, 0))
box("eground", G + Vector((0, 0, -0.1)), (200, 200, 0.2), SNOW, coll=EDGE)
box("eroad", G + Vector((0, 0, 0.01)), (10, 200, 0.04), ASPH, coll=EDGE)
SIGNP = G + Vector((8, 6, 0))
for sx in (-2.6, 2.6): box("spost", SIGNP + Vector((sx, 0, 2.5)), (0.35, 0.35, 5.0), mat("spostm", (0.35, 0.25, 0.15), 0.8), coll=EDGE)
box("sboard", SIGNP + Vector((0, 0, 4.6)), (7.2, 0.3, 3.2), mat("sboardm", (0.1, 0.35, 0.2), 0.6), coll=EDGE, bevel=0.1)
box("sboardsnow", SIGNP + Vector((0, 0, 6.3)), (7.3, 0.4, 0.25), SNOW, coll=EDGE, bevel=0.08)
SIGNTXT = mat("signtxt", (0.95, 0.95, 0.9), 0.5)
text3d("YOU ARE NOW", SIGNP + Vector((0, -0.2, 5.4)), 0.55, SIGNTXT, coll=EDGE)
text3d("LEAVING TOWN", SIGNP + Vector((0, -0.2, 4.5)), 0.75, SIGNTXT, coll=EDGE)
text3d("drive safe :)", SIGNP + Vector((0, -0.2, 3.6)), 0.45, SIGNTXT, coll=EDGE)
ROCK = SIGNP + Vector((-6, -4, 0))
sphere("rock", ROCK + Vector((0, 0, 0.6)), 1, mat("rockm", (0.3, 0.3, 0.33), 0.9), coll=EDGE, seg=10, scale=(1.8, 1.5, 1.1))
sphere("rocksnow", ROCK + Vector((0, 0, 1.45)), 1, SNOW, coll=EDGE, seg=10, scale=(1.4, 1.1, 0.35))
rnd_ = random.Random(5)
for i in range(60):
    x, y = rnd_.uniform(-90, 90), rnd_.uniform(-90, 90)
    if abs(x) < 14: continue
    p = G + Vector((x, y, 0)); h = rnd_.uniform(9, 16)
    cyl("etr", p + Vector((0, 0, 1)), 0.4, 2, TRUNK, coll=EDGE)
    for j in range(3): cone("epine", p + Vector((0, 0, 2 + j * h / 4 + h / 6)), h / 3.2 * (1 - j * 0.25), h / 2.6, PINEM, verts=8, coll=EDGE)
# the town glow behind (far end of the road): big warm emissive haze
box("townglow", G + Vector((0, -95, 8)), (180, 2, 20), emat("tglow", (1.0, 0.75, 0.45), 1.2), coll=EDGE)
EDGE_LIGHTS = [light("emoon", "AREA", G + Vector((-30, -40, 50)), 3000, (0.45, 0.6, 1.0), size=50, rot=(math.radians(40), 0, math.radians(-35)), coll=EDGE)]

# ---------------------------------------------------------------- snow fall (merged quads, per-set, animated by object offset)
def snowfall(coll, center, n=700, spread=(40, 60), height=30, name="snowfx"):
    bm = bmesh.new(); rnd = random.Random(len(name) + n)
    for i in range(n):
        p = Vector((rnd.uniform(-spread[0], spread[0]), rnd.uniform(-spread[1], spread[1]), rnd.uniform(0, height)))
        s = rnd.uniform(0.05, 0.11)
        r = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=s)
        bmesh.ops.translate(bm, vec=p, verts=r["verts"])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(emat("flake", (0.9, 0.95, 1.0), 0.6))
    o = bpy.data.objects.new(name, me); coll.objects.link(o); o.location = center; return o
SNOWFX = {"main": snowfall(MAIN, Vector((0, 0, 0))), "square": snowfall(SQ, Q, spread=(60, 60), height=50), "edge": snowfall(EDGE, G)}
def snow_anim(n):
    for o in SNOWFX.values():
        base = o["base"] if "base" in o else o.location.copy(); o["base"] = base
        if o.animation_data: o.animation_data_clear()
        for f in (1, n):
            o.location = Vector(base) + Vector((0.6 * f / 24, 0, -1.4 * f / 24)); o.keyframe_insert("location", frame=f)
        if o.animation_data and o.animation_data.action:
            for fc in (o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []):
                for k in fc.keyframe_points: k.interpolation = "LINEAR"

# ---------------------------------------------------------------- glow: make any Char glow (emissive copies of its materials + halo light)
_gcache = {}
def _glowmat(m, col, strength):
    key = (m.name, tuple(round(c, 2) for c in col), strength)
    if key in _gcache: return _gcache[key]
    if m.use_nodes and m.node_tree and "Image Texture" in [n.bl_idname.replace("ShaderNodeTexImage", "Image Texture") for n in m.node_tree.nodes]:
        g = m.copy(); nt = g.node_tree; b = nt.nodes["Principled BSDF"]
        tex = [n for n in nt.nodes if n.bl_idname == "ShaderNodeTexImage"][0]
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.55
    else:
        dc = m.diffuse_color[:3]; mix = tuple(0.3 * dc[i] + 0.7 * col[i] for i in range(3))
        g = emat(f"G_{m.name}", mix, strength, base=tuple(0.5 * dc[i] + 0.5 * col[i] for i in range(3)))
    _gcache[key] = g; return g
def glowify(c, col, strength=0.55, halo=260):
    objs = []
    def walk(o):
        for ch in o.children: objs.append(ch); walk(ch)
    walk(c.root)
    for o in objs:
        if o.type != "MESH": continue
        o.data = o.data.copy()   # never edit a cached/shared mesh (it would leak the glow onto other characters)
        for i, m in enumerate(o.data.materials):
            if m: o.data.materials[i] = _glowmat(m, col, strength)
    if halo:
        L = light("halo", "POINT", (0, -1.2, 3.2), halo, col, coll=c.coll, radius=1.2, parent=c.root); L.data.use_shadow = False
        c.halo = L
    c.glow = col; return c
GLOWC = [(1.0, 0.18, 0.15), (0.15, 1.0, 0.3), (1.0, 0.75, 0.1), (0.2, 0.45, 1.0), (1.0, 0.3, 0.8), (0.2, 0.95, 1.0)]

# ---------------------------------------------------------------- townsfolk
TFOLK = [((0.95, 0.78, 0.62), (0.7, 0.2, 0.2), (0.2, 0.2, 0.3), "short", (0.4, 0.25, 0.1)),
         ((0.45, 0.27, 0.16), (0.2, 0.5, 0.8), (0.15, 0.15, 0.2), "fade", (0.05, 0.03, 0.02)),
         ((0.8, 0.6, 0.45), (0.9, 0.7, 0.2), (0.3, 0.2, 0.15), "bun", (0.15, 0.08, 0.04)),
         ((0.3, 0.18, 0.1), (0.3, 0.7, 0.4), (0.2, 0.2, 0.25), "afro", (0.05, 0.03, 0.02)),
         ((0.92, 0.7, 0.55), (0.6, 0.3, 0.7), (0.25, 0.25, 0.3), "ponytail", (0.8, 0.6, 0.2)),
         ((0.6, 0.4, 0.25), (0.9, 0.4, 0.6), (0.2, 0.25, 0.4), "spiky", (0.1, 0.05, 0.02)),
         ((0.96, 0.8, 0.68), (0.4, 0.4, 0.45), (0.15, 0.15, 0.2), "short", (0.9, 0.9, 0.92))]
def townie(i, coll=None, glow=True, scale=None):
    s, sh, p, h, hc = TFOLK[i % len(TFOLK)]
    c = Char(f"town{i}", coll or TEMP, s, sh, p, hair=h, hair_col=hc, scale=scale or (1.0 + 0.08 * ((i * 7) % 3)))
    if glow: glowify(c, GLOWC[i % len(GLOWC)], halo=0)
    return c
def mk_steve(coll=None):
    c = Char("steve", coll or TEMP, (0.95, 0.8, 0.66), (0.95, 0.85, 0.55), (0.3, 0.3, 0.35), hair="short", hair_col=(0.35, 0.22, 0.1), scale=1.25)
    glowify(c, (1.0, 0.8, 0.35), strength=0.35, halo=200); return c
def mk_mom(coll=None):
    c = Char("mom", coll or TEMP, SKR, (0.75, 0.2, 0.3), (0.2, 0.2, 0.3), hair="bun", hair_col=(0.08, 0.05, 0.03), scale=1.12)
    glowify(c, (1.0, 0.45, 0.65), halo=150); return c
def mk_mayor(coll=None):
    c = Char("mayor", coll or TEMP, (0.9, 0.72, 0.58), (0.12, 0.12, 0.2), (0.12, 0.12, 0.2), hair="short", hair_col=(0.85, 0.85, 0.88), scale=1.2)
    box("sash", (0, -0.53, 1.1), (0.4, 0.05, 2.0), mat("sash", (0.8, 0.1, 0.1), 0.6), rot=(0, 0.6, 0), parent=c.hips, coll=c.coll)
    tophat = mat("tophat", (0.04, 0.04, 0.05), 0.4)
    cyl("hatbrim", (0, 0, 0.66), 0.95, 0.08, tophat, parent=c.head, coll=c.coll, verts=20)
    cyl("hattop", (0, 0, 1.25), 0.62, 1.15, tophat, parent=c.head, coll=c.coll, verts=20)
    glowify(c, (1.0, 0.8, 0.3), halo=150); return c
def bell_on(c):
    """mom's bell on Rico's jacket collar"""
    b = sphere("ricobell", (0, -0.76, 1.82), 1, GOLD, coll=c.coll, parent=c.hips, scale=(0.2, 0.2, 0.2))
    box("bellstrap", (0, -0.6, 1.98), (0.9, 0.06, 0.1), mat("strap", (0.8, 0.1, 0.12), 0.6), parent=c.hips, coll=c.coll)
    return b
def flashlight(c):
    """flashlight in Rico's right hand: body + lens + spot + visible beam cone (hidden until switched on)"""
    hand = c.arms[1]
    fl = empty("flash", (0, -0.2, -1.95), parent=hand, coll=c.coll); fl.rotation_euler = (math.pi / 2, 0, 0)
    cyl("flbody", (0, 0, 0), 0.2, 1.0, mat("flbodym", (0.85, 0.15, 0.1), 0.4), parent=fl, coll=c.coll, verts=12)
    cyl("flhead", (0, 0, 0.6), 0.3, 0.35, METAL, parent=fl, coll=c.coll, verts=12)
    lens = cyl("fllens", (0, 0, 0.79), 0.26, 0.04, emat("fllensm", (1, 0.95, 0.8), 0.0), parent=fl, coll=c.coll, verts=12)
    beam = cone("flbeam", (0, 0, 7.8), 2.2, 14, emat("beamm", (1, 0.95, 0.75), 1.4, alpha=0.13), verts=20, parent=fl, coll=c.coll, rot=(math.pi, 0, 0))
    sp = light("flspot", "SPOT", (0, 0, 0.9), 0, (1, 0.95, 0.8), coll=c.coll, radius=0.2, parent=fl); sp.rotation_euler = (math.pi, 0, 0)
    sp.data.spot_size = math.radians(40)
    c.fl = dict(root=fl, lens=lens, beam=beam, spot=sp)
    return c.fl
def flash_on(c, f, on=True):
    d = c.fl; d["beam"].hide_render = not on; d["beam"].keyframe_insert("hide_render", frame=f)
    d["spot"].data.energy = 6000 if on else 0; d["spot"].data.keyframe_insert("energy", frame=f)
    b = d["lens"].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    b.default_value = 30 if on else 0; b.keyframe_insert("default_value", frame=f)

# ---------------------------------------------------------------- giant moths
MOTHF = mat("mothfur", (0.55, 0.45, 0.32), 0.95); MOTHW = mat("mothwing", (0.62, 0.52, 0.38), 0.9)
MOTHD = mat("mothdark", (0.2, 0.14, 0.09), 0.9); MOTHEYE = mat("motheye", (0.02, 0.02, 0.03), 0.1)
MOTHSPOT = mat("mothspot", (0.15, 0.25, 0.5), 0.8)
class Moth:
    def __init__(self, coll, scale=1.0, seed=0):
        self.root = empty("moth", coll=coll); self.root.scale = (scale,) * 3; self.seed = seed
        b = self.body = empty("mbody", (0, 0, 0), self.root, coll)
        box("mthorax", (0, 0, 0), (0.9, 1.1, 0.9), MOTHF, parent=b, coll=coll, bevel=0.35)
        box("mabdomen", (0, 1.1, -0.15), (0.75, 1.5, 0.7), MOTHF, parent=b, coll=coll, bevel=0.3)
        for k in range(3): box("mband", (0, 0.75 + k * 0.45, -0.15), (0.78, 0.1, 0.73), MOTHD, parent=b, coll=coll)
        h = self.head = empty("mhead", (0, -0.7, 0.05), b, coll)
        box("mhd", (0, 0, 0), (0.8, 0.6, 0.7), MOTHF, parent=h, coll=coll, bevel=0.25)
        box("mfluff", (0, 0.1, -0.35), (1.0, 0.6, 0.3), mat("mfluffm", (0.85, 0.8, 0.7), 0.95), parent=h, coll=coll, bevel=0.12)
        for sx in (-1, 1):
            sphere("meye", (sx * 0.32, -0.25, 0.08), 1, MOTHEYE, coll=coll, parent=h, scale=(0.24, 0.2, 0.26))
            sphere("meyeg", (sx * 0.27, -0.42, 0.18), 1, mat("white", (1, 1, 1)), coll=coll, parent=h, scale=(0.06, 0.03, 0.06))
            a = empty("mant", (sx * 0.2, -0.2, 0.32), h, coll); a.rotation_euler = (-0.6, sx * 0.4, 0)
            box("mantstem", (0, 0, 0.55), (0.06, 0.06, 1.1), MOTHD, parent=a, coll=coll)
            box("mantfeather", (0, 0, 0.75), (0.5, 0.04, 0.7), MOTHD, parent=a, coll=coll)
        self.wings = []
        for sx in (-1, 1):
            w = empty("mwing", (sx * 0.4, 0.1, 0.25), b, coll)
            box("mfore", (sx * 1.6, -0.3, 0), (3.0, 1.9, 0.06), MOTHW, rot=(0, 0, sx * 0.25), parent=w, coll=coll, bevel=0.03)
            box("mhind", (sx * 1.2, 1.2, -0.02), (2.2, 1.7, 0.06), MOTHW, rot=(0, 0, -sx * 0.2), parent=w, coll=coll, bevel=0.03)
            box("mwspot", (sx * 2.0, -0.35, 0.04), (0.8, 0.8, 0.04), MOTHSPOT, rot=(0, 0, 0.78), parent=w, coll=coll)
            box("mwedge", (sx * 1.7, -1.15, 0.03), (2.8, 0.2, 0.04), MOTHD, rot=(0, 0, sx * 0.25), parent=w, coll=coll)
            self.wings.append((w, sx))
    def place(self, loc, rotz=0.0, f=1):
        self.root.location = loc; self.root.rotation_euler = (0, 0, rotz)
        self.root.keyframe_insert("location", frame=f); self.root.keyframe_insert("rotation_euler", frame=f)
    def flap(self, f0, f1, speed=5.0, amp=0.7, base=0.0):
        ph = self.seed * 1.7
        for f in range(f0, f1 + 1):
            a = base + amp * math.sin(f / 24 * speed * 2 * math.pi + ph)
            for w, sx in self.wings: w.rotation_euler = (0, -sx * a, 0); w.keyframe_insert("rotation_euler", frame=f)
            self.body.location = (0, 0, 0.15 * math.sin(f / 24 * speed * 2 * math.pi + ph + 1.2)); self.body.keyframe_insert("location", frame=f)
    def fly(self, f0, f1, pts, look=None, wobble=0.6):
        """fly along a Catmull-ish path through pts, facing direction of travel (or 'look' point)"""
        P = [Vector(p) for p in pts]; n = max(1, f1 - f0)
        for f in range(f0, f1 + 1):
            u = (f - f0) / n * (len(P) - 1); i = min(int(u), len(P) - 2); t = u - i
            p = P[i].lerp(P[i + 1], ease(t) if len(P) == 2 else t)
            p = p + Vector((math.sin(f * 0.21 + self.seed), math.cos(f * 0.17 + self.seed), math.sin(f * 0.13 + self.seed * 2))) * wobble
            d = (Vector(look) - p) if look else (P[i + 1] - P[i])
            rz = math.atan2(d.y, d.x) + math.pi / 2
            self.root.location = p; self.root.rotation_euler = (0.15, 0, rz)
            self.root.keyframe_insert("location", frame=f); self.root.keyframe_insert("rotation_euler", frame=f)

def show_set(which):
    for name, coll, lights in (("main", MAIN, MAIN_LIGHTS), ("square", SQ, SQ_LIGHTS), ("edge", EDGE, EDGE_LIGHTS)):
        on = name == which; coll.hide_render = not on
        for o in coll.objects:
            if o.type == "LIGHT": o.hide_render = not on
    WBG.inputs[0].default_value = (0.006, 0.01, 0.03, 1); WBG.inputs[1].default_value = 1.0
    SUN.data.energy = 0.18; SUN.data.color = (0.55, 0.7, 1.0)
