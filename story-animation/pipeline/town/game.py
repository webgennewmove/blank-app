"""IN MY TOWN: 'The Game' (cinematic, Roblox-style cast). Library + crocodile + jungle. EEVEE.
usage: EEVEE=1 python game.py -- all|s01,s05 [still]"""
import sys, os, json, math, random
REAL_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = [sys.argv[0], "--", "none"]
os.environ["HOOD"] = "1"
exec(open("/home/claude/zara/world.py").read())
import bmesh
from mathutils import Vector, Quaternion, Matrix
ONLY = set(REAL_ARGV[0].split(",")) if REAL_ARGV and REAL_ARGV[0] != "all" else None
exec(open("/home/claude/zara/eevee_patch.py").read())
exec(open("/home/claude/zara/town/rcast.py").read())
STILL = len(REAL_ARGV) > 1 and REAL_ARGV[1] == "still"
E = "/home/claude/zara/town/ep"; OUT = f"{E}/frames"
S.render.resolution_x, S.render.resolution_y = 720, 1280
S.render.film_transparent = False
TL = json.load(open(f"{E}/timeline.json")); DUR = TL["dur"]; LEADS = TL["lead"]; WORDS = TL["words"]
WORLD.hide_render = True; ROOM.hide_render = True
random.seed(9)
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")
SUN = [o for o in S.objects if o.type == "LIGHT" and o.data.type == "SUN"][0]
WBG = S.world.node_tree.nodes["Background"]

def F(t): return max(1, int(round(t * FPS)) + 1)
def wt(shot, word, k=0):
    hits = [a for w, a, b in WORDS[shot] if w.lower().strip(".,!?-…") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
def ease(u): return u * u * (3 - 2 * u)

def emat(name, col, strength=4.0, base=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*(base or col), 1); b.inputs["Emission Color"].default_value = (*col, 1)
    b.inputs["Emission Strength"].default_value = strength; m.diffuse_color = (*col, 1); return m
def light(name, typ, loc, energy, col, size=1.0, rot=(0, 0, 0), coll=None, radius=None):
    L = bpy.data.lights.new(name, typ); L.energy = energy; L.color = col
    if typ == "AREA": L.size = size
    if typ in ("POINT", "SPOT") and radius is not None: L.shadow_soft_size = radius
    o = bpy.data.objects.new(name, L); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot; return o
def text3d(body, loc, size, m, rot=(math.pi / 2, 0, 0), coll=None, extrude=0.02, parent=None):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.font = FONTB; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new("txt", cu); (coll or S.collection).objects.link(o); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    o.data.materials.append(m); return o
def merged_boxes(name, items, mats, coll):
    """items: (loc, size, mat_index, rotz) -> one mesh (fast for thousands of books/leaves)"""
    bm = bmesh.new()
    for loc, size, mi, rz in items:
        r = bmesh.ops.create_cube(bm, size=1.0)
        mtx = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(bm, matrix=mtx, verts=r["verts"])
        for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = mi
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

# ---------------------------------------------------------------- camera
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
def cut_constant():
    for o in (CAM, CAM.data):
        ad = o.animation_data
        if not ad or not ad.action: continue
        act = ad.action
        fcs = act.fcurves if hasattr(act, "fcurves") else [fc for l in act.layers for st in l.strips for fc in st.channelbag(ad.action_slot).fcurves]
        for fc in fcs:
            for k in fc.keyframe_points: k.interpolation = "CONSTANT"

# ---------------------------------------------------------------- night-library palette
LIB = collection("library")
wood = mat("wood", (0.16, 0.07, 0.03), 0.55); wood2 = mat("wood2", (0.24, 0.11, 0.045), 0.5); dwood = mat("dwood", (0.07, 0.03, 0.015), 0.6)
stone = mat("stone", (0.2, 0.18, 0.17), 0.9); rug = mat("rug", (0.25, 0.03, 0.04), 0.9); brass = mat("brass", (0.8, 0.55, 0.15), 0.25)
box("lfloor", (0, 0, -0.1), (48, 60, 0.2), wood, coll=LIB)
for k in range(-23, 24, 2): box("plank", (k, 0, 0.005), (0.05, 60, 0.01), dwood, coll=LIB)
box("rug", (0, 0, 0.02), (20, 14, 0.04), rug, coll=LIB, bevel=0.02)
box("rugtrim", (0, 0, 0.015), (21, 15, 0.03), mat("rugtrim", (0.6, 0.42, 0.12), 0.8), coll=LIB)
box("ceil", (0, 0, 24.2), (48, 60, 0.4), dwood, coll=LIB)
for y in range(-26, 28, 6): box("beam", (0, y, 23.4), (48, 0.9, 1.2), wood, coll=LIB)
# walls: wood panelling + stone above
for name, loc, size in [("wb", (0, 28, 12), (48, 0.6, 24)), ("wf", (0, -30, 12), (48, 0.6, 24)), ("wl", (-24, 0, 12), (0.6, 60, 24)), ("wr", (24, 0, 12), (0.6, 60, 24))]:
    box(name, loc, size, stone, coll=LIB)
# bookshelves (back wall + right wall), books merged per wall
BOOKC = [(0.45, 0.05, 0.05), (0.06, 0.2, 0.12), (0.05, 0.1, 0.35), (0.5, 0.32, 0.08), (0.3, 0.06, 0.25), (0.6, 0.55, 0.45), (0.1, 0.1, 0.1)]
bmats = [mat(f"book{i}", c, 0.7) for i, c in enumerate(BOOKC)]
def shelf_wall(x0, x1, y, face, coll, height=17, rows=8, along="x"):
    items = []; rnd = random.Random(int(x0 * 7 + y))
    L = x1 - x0
    for r in range(rows):
        z = 0.6 + r * (height / rows)
        pos = 0.0
        while pos < L - 0.3:
            w = rnd.uniform(0.18, 0.34); h = rnd.uniform(1.1, 1.75); d = rnd.uniform(0.9, 1.2)
            lean = rnd.uniform(-0.04, 0.04) if rnd.random() < 0.1 else 0
            c = x0 + pos + w / 2
            if along == "x": items.append(((c, y - face * 0.1, z + h / 2), (w, d, h), rnd.randrange(len(BOOKC)), lean))
            else: items.append(((y - face * 0.1, c, z + h / 2), (d, w, h), rnd.randrange(len(BOOKC)), lean))
            pos += w + (0.25 if rnd.random() < 0.05 else 0.01)
        if along == "x": box("shelfboard", ((x0 + x1) / 2, y, z - 0.08), (L, 1.6, 0.16), wood2, coll=coll)
        else: box("shelfboard", (y, (x0 + x1) / 2, z - 0.08), (1.6, L, 0.16), wood2, coll=coll)
    merged_boxes("books", items, bmats, coll)
    for k in range(int(L // 4) + 1):
        p = x0 + k * L / max(1, int(L // 4))
        if along == "x": box("upright", (p, y, height / 2 + 0.3), (0.35, 1.7, height + 0.6), wood, coll=coll)
        else: box("upright", (y, p, height / 2 + 0.3), (1.7, 0.35, height + 0.6), wood, coll=coll)
    if along == "x": box("shelfback", ((x0 + x1) / 2, y + face * 0.8, height / 2 + 0.3), (L, 0.2, height + 0.6), dwood, coll=coll)
    else: box("shelfback", (y + face * 0.8, (x0 + x1) / 2, height / 2 + 0.3), (0.2, L, height + 0.6), dwood, coll=coll)
shelf_wall(-23, -14, 26.8, 1, LIB); shelf_wall(-8, 23, 26.8, 1, LIB)
shelf_wall(-28, -12, 22.8, 1, LIB, along="y"); shelf_wall(0, 26, 22.8, 1, LIB, along="y")
# the locked glass cabinet (back wall gap, x -14..-8)
CAB = Vector((-11, 26.2, 0))
box("cabbody", CAB + Vector((0, 0.3, 6)), (5.6, 1.6, 12), wood, coll=LIB, bevel=0.1)
box("cabin", CAB + Vector((0, 0.0, 6)), (5.0, 1.2, 11), mat("cabin", (0.03, 0.02, 0.015), 0.8), coll=LIB)
box("cabcrown", CAB + Vector((0, 0.1, 12.3)), (6.2, 2.0, 0.6), wood2, coll=LIB, bevel=0.1)
for z in (3.2, 6.4, 9.6): box("cabshelf", CAB + Vector((0, 0, z)), (5.0, 1.2, 0.12), wood2, coll=LIB)
GLASS_L = mat("cabglass", (0.6, 0.8, 0.85), 0.05)
for sx in (-1, 1):
    box("cabframe", CAB + Vector((sx * 1.3, -0.62, 6)), (2.5, 0.12, 11.2), wood2, coll=LIB)
box("lock", CAB + Vector((0, -0.72, 6.2)), (0.45, 0.2, 0.55), brass, coll=LIB, bevel=0.05)
light("cablight", "POINT", CAB + Vector((0, -1.6, 6.2)), 450, (0.35, 1.0, 0.55), coll=LIB, radius=0.5)
box("chain", CAB + Vector((0, -0.75, 6.8)), (2.6, 0.08, 0.12), mat("chain", (0.4, 0.4, 0.42), 0.3), coll=LIB)
# windows (left wall), arched, night-glow glass; panes are separate so they can shatter
WIN_YS = (-14, -2, 10)
WGLASS = emat("winglass", (0.1, 0.45, 0.55), 1.2, base=(0.05, 0.12, 0.18))
PANES = []
for y in WIN_YS:
    box("wsill", (-23.4, y, 3.4), (1.2, 7.2, 0.4), stone, coll=LIB)
    for sy in (-1, 1): box("wjamb", (-23.5, y + sy * 3.2, 9.5), (1.0, 0.6, 12.4), stone, coll=LIB)
    cyl("warch", (-23.5, y, 15.7), 3.5, 1.0, stone, rot=(0, math.pi / 2, 0), coll=LIB, verts=24)
    for k in range(3):
        for j in range(5):
            p = box("pane", (-23.55, y - 2.0 + k * 2.0, 4.8 + j * 2.25), (0.15, 1.9, 2.15), WGLASS, coll=LIB); PANES.append(p)
    for k in range(2): box("mullion", (-23.4, y - 1.0 + k * 2.0, 9.5), (0.25, 0.14, 12), dwood, coll=LIB)
    for j in range(4): box("transom", (-23.4, y, 6.0 + j * 2.25), (0.25, 6.0, 0.14), dwood, coll=LIB)
    light(f"moon{y}", "AREA", (-22.8, y, 9.5), 1200, (0.35, 0.75, 0.85), size=6, rot=(0, -math.pi / 2, 0), coll=LIB)
# big double door (right wall) for the crocodile
DOOR = Vector((23.6, -8, 0))
box("doorframe", DOOR + Vector((0.1, 0, 5.4)), (1.2, 8.4, 10.8), stone, coll=LIB)
DOORL = empty("doorL", DOOR + Vector((-0.2, -3.6, 0)), coll=LIB); DOORR = empty("doorR", DOOR + Vector((-0.2, 3.6, 0)), coll=LIB)
for d_, sgn in ((DOORL, 1), (DOORR, -1)):
    box("doorp", (0, sgn * 1.8, 4.8), (0.5, 3.55, 9.6), wood2, parent=d_, coll=LIB, bevel=0.05)
    for z in (2.5, 7.0): box("doorpanel", (-0.28, sgn * 1.8, z), (0.08, 2.6, 3.4), wood, parent=d_, coll=LIB, bevel=0.05)
    sphere("knob", (-0.4, sgn * 3.1, 4.8), 1, brass, coll=LIB, parent=d_, scale=(0.18, 0.18, 0.18))
# reading table + chairs + banker lamps
TT = 2.75
box("tabletop", (0, 0, TT - 0.15), (15, 6.4, 0.3), wood2, coll=LIB, bevel=0.06)
for sx in (-6.8, 6.8):
    for sy in (-2.6, 2.6): box("tleg", (sx, sy, (TT - 0.3) / 2), (0.45, 0.45, TT - 0.3), wood, coll=LIB)
LAMPS = []
for x in (-5.2, 5.2):
    cyl("lbase", (x, 0.5, TT + 0.06), 0.45, 0.12, brass, coll=LIB, verts=16)
    cyl("lpole", (x, 0.5, TT + 0.6), 0.06, 1.1, brass, coll=LIB, verts=8)
    box("lshade", (x, 0.2, TT + 1.15), (1.5, 0.55, 0.36), emat("bankshade", (0.05, 0.6, 0.25), 1.5, base=(0.02, 0.25, 0.1)), coll=LIB, bevel=0.12)
    LAMPS.append(light("lamp", "POINT", (x, 0.1, TT + 0.85), 140, (1.0, 0.72, 0.4), coll=LIB, radius=0.3))
chair_m = mat("chair", (0.2, 0.09, 0.04), 0.55)
CHAIRS = []
for x, y, r in [(-9.5, -4.6, 0.3), (9.8, -4.4, -0.4), (-10.2, 4.4, 2.8)]:
    c = empty("chair", (x, y, 0), coll=LIB, rot=(0, 0, r))
    box("cseat", (0, 0, 1.7), (2.0, 2.0, 0.25), chair_m, parent=c, coll=LIB, bevel=0.05)
    box("cback", (0, 0.9, 3.0), (2.0, 0.25, 2.6), chair_m, parent=c, coll=LIB, bevel=0.05)
    for sx in (-0.85, 0.85):
        for sy in (-0.85, 0.85): box("cleg", (sx, sy, 0.8), (0.22, 0.22, 1.6), chair_m, parent=c, coll=LIB)
    CHAIRS.append(c)
# chandeliers
for y in (-10, 8):
    for k in range(16): box("chring", (math.cos(k / 16 * 6.283) * 3.2, y + math.sin(k / 16 * 6.283) * 3.2, 17), (0.25, 1.3, 0.2), brass, rot=(0, 0, k / 16 * 6.283), coll=LIB)
    cyl("chchain", (0, y, 20.5), 0.06, 7, brass, coll=LIB, verts=6)
    for k in range(10):
        a = k / 10 * 6.283; sphere("bulb", (math.cos(a) * 3.2, y + math.sin(a) * 3.2, 17.4), 1, emat("bulb", (1, 0.7, 0.35), 8), coll=LIB, scale=(0.18, 0.18, 0.22), seg=8)
    light("chand", "POINT", (0, y, 16.5), 4200, (1.0, 0.66, 0.35), coll=LIB, radius=2.5)
light("fillback", "AREA", (0, 20, 14), 1700, (1.0, 0.6, 0.35), size=20, rot=(math.radians(-110), 0, 0), coll=LIB)
light("doorlight", "POINT", DOOR + Vector((-5, 0, 6)), 2500, (0.5, 1.0, 0.6), coll=LIB, radius=1.5)
DUST = []
rnd = random.Random(3)
for k in range(60):
    d = sphere("dust", (rnd.uniform(-12, 12), rnd.uniform(6, 20), rnd.uniform(6, 16)), 1, emat("dust", (1, 0.85, 0.6), 3), coll=LIB, scale=(0.03, 0.03, 0.03), seg=6)
    DUST.append(d)

# ---------------------------------------------------------------- the board game: a map of our town
def make_board_tex(fpath):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    W_, H_ = 2048, 1460; im = Image.new("RGB", (W_, H_), (214, 190, 140)); d = ImageDraw.Draw(im)
    rr = random.Random(5)
    for k in range(9000):
        x, y = rr.randrange(W_), rr.randrange(H_); c = rr.randint(-18, 10)
        d.point((x, y), fill=(214 + c, 190 + c, 140 + c))
    d.rectangle([28, 28, W_ - 28, H_ - 28], outline=(90, 55, 25), width=18); d.rectangle([62, 62, W_ - 62, H_ - 62], outline=(150, 105, 40), width=6)
    # river + park
    d.line([(0, 1050), (500, 980), (900, 1150), (1400, 1020), (2048, 1120)], fill=(70, 120, 150), width=70)
    d.ellipse([1300, 180, 1800, 600], fill=(120, 150, 80), outline=(70, 95, 40), width=6)
    for k in range(14):
        x, y = 1360 + rr.randint(0, 400), 230 + rr.randint(0, 320); d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(70, 110, 55))
    # streets
    for pts in ([(120, 720), (1950, 720)], [(1000, 100), (1000, 1380)], [(300, 200), (700, 1300)], [(1500, 650), (1800, 1300)]):
        d.line(pts, fill=(170, 150, 110), width=46)
    # landmarks (simple drawings)
    def bld(x, y, w, h, col, roof=None):
        d.rectangle([x, y, x + w, y + h], fill=col, outline=(60, 40, 20), width=4)
        if roof: d.polygon([(x - 10, y), (x + w / 2, y - h * 0.45), (x + w + 10, y)], fill=roof, outline=(60, 40, 20))
        for k in range(int(w // 34)):
            for j in range(int(h // 44)):
                d.rectangle([x + 10 + k * 34, y + 12 + j * 44, x + 28 + k * 34, y + 34 + j * 44], fill=(250, 220, 120))
    bld(180, 300, 300, 220, (150, 70, 50), (90, 40, 30))                 # library
    bld(1110, 820, 180, 140, (60, 110, 160), (40, 60, 90))               # corner shop
    d.rectangle([1590, 300, 1650, 480], fill=(110, 90, 60)); d.polygon([(1540, 300), (1620, 230), (1700, 300)], fill=(150, 60, 40))   # bandstand
    bld(760, 160, 120, 380, (170, 150, 120), (90, 60, 40)); d.ellipse([782, 220, 858, 296], fill=(245, 235, 200), outline=(60, 40, 20), width=5)  # clock tower
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf", 44)
    for txt, x, y in (("LIBRARY", 210, 540), ("CORNER SHOP", 1080, 975), ("THE PARK", 1440, 610), ("CLOCK TOWER", 680, 560)):
        d.text((x, y), txt, font=f, fill=(70, 40, 20))
    # the winding path of squares, six special ones
    sq = [(160 + i * 62, 1260 - 60 * math.sin(i * 0.35) - i * 14) for i in range(28)]
    for i, (x, y) in enumerate(sq):
        special = i in (4, 9, 14, 19, 23, 27)
        d.rounded_rectangle([x - 26, y - 26, x + 26, y + 26], 8, fill=(30, 140, 80) if special else (240, 225, 185), outline=(60, 40, 20), width=4)
        if special: d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(160, 255, 190))
    im.save(fpath)
make_board_tex(f"{E}/board.png")
def tex_mat(name, path, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6
    if emit: nt.links.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    return m
def uv_plane(name, w, h, m, coll, parent=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    me.materials.append(m); o = bpy.data.objects.new(name, me); coll.objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o
BOARD_M = tex_mat("boardtex", f"{E}/board.png", emit=0.15)
BOARD = empty("board", (0, -0.4, TT + 0.02), coll=LIB)
BW, BH = 4.6, 3.3
BHALF = []
for sx in (-1, 1):   # two hinged halves (unfold in s03)
    hinge = empty("bhinge", (0, 0, 0.06), BOARD, LIB)
    half_ = empty("bhalf", (0, 0, 0), hinge, LIB)
    box("bback", (sx * BW / 4, 0, -0.03), (BW / 2, BH, 0.06), mat("boardback", (0.25, 0.05, 0.04), 0.5), parent=half_, coll=LIB, bevel=0.02)
    pl = uv_plane("bface", BW / 2, BH, BOARD_M, LIB, parent=half_, loc=(sx * BW / 4, 0, 0.002))
    for i, l in enumerate(pl.data.uv_layers[0].data):
        u, v = [(0, 0), (1, 0), (1, 1), (0, 1)][i]; l.uv = ((u * 0.5 + (0.5 if sx > 0 else 0.0)), v)
    BHALF.append((hinge, sx))
BGLOW = light("boardglow", "POINT", (0, -0.4, TT + 1.2), 0, (0.2, 1.0, 0.45), coll=LIB, radius=1.0)
GEMS = []
for i in range(6):
    g = sphere("sqglow", (-1.8 + i * 0.72, -0.4 - 1.0 + 0.2 * math.sin(i), TT + 0.1), 1, emat(f"sqglow{i}", (0.2, 1.0, 0.45), 0.0), coll=LIB, scale=(0.14, 0.14, 0.05), seg=12)
    GEMS.append(g)
def gem_on(g, f, strength=12):
    m = g.data.materials[0]; b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    b.default_value = 0.0; b.keyframe_insert("default_value", frame=max(1, f - 1)); b.default_value = strength; b.keyframe_insert("default_value", frame=f)
# the box on the cabinet shelf
GBOX = empty("gamebox", CAB + Vector((0, -0.1, 6.6)), coll=LIB)
box("gbx", (0, 0, 0.0), (2.4, 1.2, 0.55), mat("gboxc", (0.3, 0.05, 0.04), 0.5), parent=GBOX, coll=LIB, bevel=0.05)
box("gbxband", (0, 0, 0.0), (2.45, 1.25, 0.18), brass, parent=GBOX, coll=LIB)
sphere("gbxgem", (0, -0.63, 0.0), 1, emat("gboxgem", (0.2, 1.0, 0.45), 6), coll=LIB, parent=GBOX, scale=(0.14, 0.05, 0.14))
# dice
def mk_die(coll, loc, s=0.42):
    d = empty("die", loc, coll=coll); box("dbody", (0, 0, 0), (s, s, s), mat("ivory", (0.92, 0.88, 0.78), 0.3), parent=d, coll=coll, bevel=s * 0.18)
    pm = emat("pip", (0.15, 1.0, 0.5), 5, base=(0.02, 0.2, 0.08)); h = s * 0.51; o = s * 0.25
    faces = {(0, 0, 1): [(0, 0)], (0, 0, -1): [(-o, -o), (-o, 0), (-o, o), (o, -o), (o, 0), (o, o)], (1, 0, 0): [(-o, -o), (o, o)],
             (-1, 0, 0): [(-o, -o), (0, 0), (o, o)], (0, 1, 0): [(-o, -o), (-o, o), (o, -o), (o, o)], (0, -1, 0): [(-o, -o), (-o, o), (0, 0), (o, -o), (o, o)]}
    for n, pts in faces.items():
        for a, b in pts:
            if n[2]: p = (a, b, n[2] * h)
            elif n[0]: p = (n[0] * h, a, b)
            else: p = (a, n[1] * h, b)
            sphere("pipd", p, 1, pm, coll=coll, parent=d, scale=(s * 0.08,) * 3, seg=8)
    return d
DICE = [mk_die(LIB, (0, 0, -50)), mk_die(LIB, (0, 0, -50))]
def dice_hide():
    for d in DICE: d.location = (0, 0, -50)
def tumble(d, f0, f1, a, b, spins=(3, 2, 1), arc=1.2, settle_rot=(math.pi, 0, 0)):
    a, b = Vector(a), Vector(b)
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); p = a.lerp(b, u); p.z += arc * 4 * u * (1 - u)
        d.location = p; d.keyframe_insert("location", frame=f)
        k = 1 - (1 - u) ** 2
        d.rotation_euler = (settle_rot[0] + spins[0] * 6.283 * (k - 1), settle_rot[1] + spins[1] * 6.283 * (k - 1), spins[2] * 6.283 * (k - 1))
        d.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- crocodile (blocky)
class Croc:
    def __init__(self, coll, scale=1.0):
        g = mat("crocg", (0.08, 0.22, 0.06), 0.6); gd = mat("crocgd", (0.04, 0.12, 0.03), 0.6); belly = mat("crocb", (0.55, 0.55, 0.3), 0.7)
        tooth = mat("tooth", (0.97, 0.95, 0.88), 0.3); eye = emat("crocye", (1.0, 0.75, 0.05), 2.0, base=(0.9, 0.6, 0.05))
        self.root = empty("croc", coll=coll); self.root.scale = (scale,) * 3
        self.body = empty("crbody", (0, 0, 1.2), self.root, coll)
        box("crb", (0, 0, 0), (2.6, 6.0, 1.5), g, parent=self.body, coll=coll, bevel=0.35)
        box("crbelly", (0, 0, -0.55), (2.3, 5.6, 0.45), belly, parent=self.body, coll=coll, bevel=0.15)
        for k in range(9):
            for sx in (-0.5, 0.5): box("scute", (sx, -2.6 + k * 0.65, 0.82), (0.35, 0.4, 0.3), gd, parent=self.body, coll=coll, bevel=0.08)
        self.neck = empty("crneck", (0, -3.0, 0.15), self.body, coll)
        self.head = empty("crhead", (0, -0.4, 0), self.neck, coll)
        box("crskull", (0, -0.6, 0.15), (2.2, 1.9, 1.05), g, parent=self.head, coll=coll, bevel=0.3)
        self.upper = empty("crupper", (0, -1.2, 0.05), self.head, coll)
        box("crsnout", (0, -1.7, 0.1), (1.5, 3.4, 0.6), g, parent=self.upper, coll=coll, bevel=0.22)
        for sx in (-0.3, 0.3): box("nostril", (sx, -3.2, 0.42), (0.18, 0.18, 0.12), gd, parent=self.upper, coll=coll)
        for k in range(8):
            for sx in (-0.68, 0.68): cone("tooth", (sx, -0.4 - k * 0.38, -0.3), 0.1, 0.32, tooth, verts=4, parent=self.upper, coll=coll, rot=(math.pi, 0, 0))
        self.jaw = empty("crjaw", (0, -1.0, -0.3), self.head, coll)
        box("crlower", (0, -1.6, -0.15), (1.4, 3.3, 0.45), belly, parent=self.jaw, coll=coll, bevel=0.18)
        box("crlowtop", (0, -1.6, 0.05), (1.45, 3.35, 0.12), mat("crmouth", (0.6, 0.15, 0.15), 0.6), parent=self.jaw, coll=coll)
        for k in range(7):
            for sx in (-0.6, 0.6): cone("ltooth", (sx, -0.5 - k * 0.4, 0.25), 0.09, 0.3, tooth, verts=4, parent=self.jaw, coll=coll)
        for sx in (-0.65, 0.65):
            box("eyebump", (sx, -0.3, 0.75), (0.55, 0.6, 0.45), g, parent=self.head, coll=coll, bevel=0.15)
            sphere("creye", (sx, -0.55, 0.85), 1, eye, coll=coll, parent=self.head, scale=(0.2, 0.12, 0.17))
            box("crpupil", (sx, -0.66, 0.85), (0.05, 0.02, 0.26), mat("pupil", (0.01, 0.01, 0.01), 0.2), parent=self.head, coll=coll)
        self.legs = []
        for sx in (-1, 1):
            for sy in (-2.0, 1.8):
                l = empty("crleg", (sx * 1.35, sy, -0.2), self.body, coll); l.rotation_euler = (0, sx * 0.5, 0)
                box("crl", (sx * 0.2, 0, -0.5), (0.6, 0.7, 1.1), g, parent=l, coll=coll, bevel=0.15)
                box("crfoot", (sx * 0.35, -0.2, -1.0), (0.8, 1.0, 0.25), gd, parent=l, coll=coll, bevel=0.08)
                self.legs.append(l)
        self.tail = []; prev = empty("crtail0", (0, 3.0, 0.0), self.body, coll)
        for k in range(6):
            seg = empty("crtail", (0, 0.0 if k == 0 else 1.05, 0), prev, coll); w = 2.0 * (1 - k / 7)
            box("crt", (0, 0.55, 0), (w, 1.2, 1.2 * (1 - k / 8)), g, parent=seg, coll=coll, bevel=0.2)
            box("crtsc", (0, 0.55, 0.6 * (1 - k / 8)), (0.3, 0.6, 0.35), gd, parent=seg, coll=coll, bevel=0.08)
            self.tail.append(seg); prev = seg
    def place(self, loc, rotz=0.0, f=1):
        self.root.location = loc; self.root.rotation_euler = (0, 0, rotz); self.root.keyframe_insert("location", frame=f); self.root.keyframe_insert("rotation_euler", frame=f)
    def anim(self, f0, f1, speed=1.0, snap=1.0, wiggle=1.0, walk=True):
        for f in range(f0, f1 + 1):
            t = f / 24 * speed; s = math.sin(t * 2 * math.pi * 1.6)
            self.body.rotation_euler = (0, 0, 0.12 * s * wiggle); self.body.keyframe_insert("rotation_euler", frame=f)
            self.neck.rotation_euler = (0, 0, -0.18 * s * wiggle); self.neck.keyframe_insert("rotation_euler", frame=f)
            for k, sg in enumerate(self.tail):
                sg.rotation_euler = (0, 0, 0.22 * math.sin(t * 2 * math.pi * 1.6 - k * 0.7) * wiggle); sg.keyframe_insert("rotation_euler", frame=f)
            if walk:
                for i, l in enumerate(self.legs):
                    l.rotation_euler = (0.5 * math.sin(t * 2 * math.pi * 1.6 + (0 if i in (0, 3) else math.pi)), l.rotation_euler.y, 0); l.keyframe_insert("rotation_euler", frame=f)
            op = max(0, math.sin(t * 2 * math.pi * 1.1)) ** 0.6 * snap
            self.jaw.rotation_euler = (0.75 * op, 0, 0); self.jaw.keyframe_insert("rotation_euler", frame=f)
            self.upper.rotation_euler = (-0.25 * op, 0, 0); self.upper.keyframe_insert("rotation_euler", frame=f)
    def move(self, f0, f1, a, b, rotz=None):
        a, b = Vector(a), Vector(b)
        rz = rotz if rotz is not None else math.atan2((b - a).y, (b - a).x) + math.pi / 2
        for f in range(f0, f1 + 1, 2):
            u = (f - f0) / max(1, f1 - f0); self.root.location = a.lerp(b, u); self.root.rotation_euler = (0, 0, rz)
            self.root.keyframe_insert("location", frame=f); self.root.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- the jungle (far east)
J = Vector((400, 0, 0)); JUN = collection("jungle")
jg = mat("jground", (0.04, 0.12, 0.03), 0.95); dirt = mat("jdirt", (0.12, 0.07, 0.03), 0.95); bark = mat("bark", (0.12, 0.07, 0.035), 0.9)
LEAF = [mat("leaf0", (0.03, 0.22, 0.05), 0.7), mat("leaf1", (0.05, 0.3, 0.07), 0.7), mat("leaf2", (0.02, 0.15, 0.04), 0.7), mat("leaf3", (0.08, 0.35, 0.1), 0.7)]
box("jground", J + Vector((0, 0, -0.1)), (260, 260, 0.2), jg, coll=JUN)
box("jclear", J + Vector((0, 0, 0.0)), (16, 16, 0.05), dirt, coll=JUN, bevel=0.02)
rr = random.Random(11)
def jtree(p, h=22, girth=1.8, canopy=7, coll=JUN, seed=0):
    r_ = random.Random(seed); t = empty("jtree", p, coll=coll)
    box("trunk", (0, 0, h / 2), (girth, girth, h), bark, parent=t, coll=coll, bevel=0.25)
    for k in range(4):
        a = k * 1.57 + r_.uniform(-0.3, 0.3)
        box("root", (math.cos(a) * girth * 0.7, math.sin(a) * girth * 0.7, 0.6), (girth * 0.9, 0.55, 1.4), bark, rot=(0, 0.5, a), parent=t, coll=coll, bevel=0.15)
    items = []
    for k in range(14):
        items.append(((r_.uniform(-canopy, canopy) * 0.6, r_.uniform(-canopy, canopy) * 0.6, h + r_.uniform(-2, 2.5)), (r_.uniform(3, 6), r_.uniform(3, 6), r_.uniform(1.6, 3)), r_.randrange(4), r_.uniform(0, 1.5)))
    cn = merged_boxes("canopy", items, LEAF, coll); cn.parent = t
    for k in range(r_.randint(2, 5)):
        x, y = r_.uniform(-canopy * 0.6, canopy * 0.6), r_.uniform(-canopy * 0.6, canopy * 0.6); L = r_.uniform(5, h * 0.7)
        cyl("vine", (x, y, h - L / 2), 0.08, L, LEAF[2], parent=t, coll=coll, verts=6)
    return t
for k in range(46):
    a = rr.uniform(0, 6.283); r_ = rr.uniform(26, 90)
    jtree(J + Vector((math.cos(a) * r_, math.sin(a) * r_, 0)), rr.uniform(20, 34), rr.uniform(1.6, 3.0), rr.uniform(6, 10), seed=k)
FERN = []
for k in range(160):
    a = rr.uniform(0, 6.283); r_ = rr.uniform(8.5, 40)
    p = J + Vector((math.cos(a) * r_, math.sin(a) * r_, 0))
    f_ = empty("fern", p, coll=JUN, rot=(0, 0, rr.uniform(0, 6.28)))
    for j in range(5):
        box("frond", (0, 0.9, 0.7), (0.8, 2.4, 0.08), LEAF[(k + j) % 4], rot=(0.6, 0, j * 1.256), parent=f_, coll=JUN)
# face-trees: a ring that will turn to face the kids (eyes start on the far side)
FACE_TREES = []
eye_m = emat("treeeye", (0.25, 1.0, 0.5), 10)
for k in range(10):
    a = k / 10 * 6.283 + 0.614; R_ = 13.5
    p = J + Vector((math.cos(a) * R_, math.sin(a) * R_, 0))
    t = jtree(p, rr.uniform(22, 26), 2.4, 6, seed=100 + k)
    face_out = math.atan2(math.sin(a), math.cos(a))          # direction away from centre
    for sx in (-0.55, 0.55):
        box("socket", (math.cos(face_out) * 1.2 - math.sin(face_out) * sx, math.sin(face_out) * 1.2 + math.cos(face_out) * sx, 9.0), (0.5, 0.5, 0.75), mat("socket", (0.01, 0.01, 0.0), 0.9), parent=t, coll=JUN, rot=(0, 0, face_out))
        sphere("teye", (math.cos(face_out) * 1.42 - math.sin(face_out) * sx, math.sin(face_out) * 1.42 + math.cos(face_out) * sx, 9.0), 1, eye_m, coll=JUN, parent=t, scale=(0.2, 0.2, 0.3))
    box("tmouth", (math.cos(face_out) * 1.25, math.sin(face_out) * 1.25, 6.8), (0.4, 1.4, 0.35), mat("socket", (0.01, 0.01, 0.0), 0.9), parent=t, coll=JUN, rot=(0, 0, face_out))
    t["a"] = a; FACE_TREES.append(t)
    t["feat"] = [ch.name for ch in t.children if ch.name.split(".")[0] in ("socket", "teye", "tmouth")]
# the king's tree: big trunk and a branch over the clearing
KT = J + Vector((0, 17, 0))
kt = jtree(KT, 30, 3.6, 10, seed=999)
box("branch", KT + Vector((0, -5.0, 15.2)), (1.4, 10.5, 1.2), bark, coll=JUN, bevel=0.3)
box("branchtip", KT + Vector((0.2, -10.6, 15.5)), (0.8, 1.6, 0.6), bark, coll=JUN, bevel=0.2)
for k in range(4):
    box("blf", KT + Vector((rr.uniform(-1.5, 1.5), -2 - k * 1.0, 16.5 + rr.uniform(0, 1))), (2.2, 2.2, 1.0), LEAF[k % 4], coll=JUN, rot=(0, 0, rr.uniform(0, 1)))
BRANCH_END = KT + Vector((0, -9.6, 15.8))
FIREFLY = []
for k in range(70):
    FIREFLY.append(sphere("firefly", J + Vector((rr.uniform(-18, 18), rr.uniform(-18, 18), rr.uniform(0.8, 9))), 1, emat("ffly", (0.6, 1.0, 0.35), 12), coll=JUN, scale=(0.05, 0.05, 0.05), seg=6))
JLIGHTS = [light("jmoon", "AREA", J + Vector((10, -12, 40)), 9000, (0.35, 0.9, 0.6), size=30, rot=(math.radians(20), math.radians(15), 0), coll=JUN),
           light("jrim", "AREA", J + Vector((0, 25, 18)), 5000, (0.25, 0.85, 0.55), size=20, rot=(math.radians(-60), 0, 0), coll=JUN),
           light("jfill", "AREA", J + Vector((0, -20, 10)), 1500, (0.4, 0.55, 0.9), size=20, rot=(math.radians(70), 0, 0), coll=JUN)]

def show_set(lib=True, jun=False):
    LIB.hide_render = not lib; JUN.hide_render = not jun
    for o in LIB.objects:
        if o.type == "LIGHT": o.hide_render = not lib
    for o in JUN.objects:
        if o.type == "LIGHT": o.hide_render = not jun
    if lib and not jun:
        WBG.inputs[0].default_value = (0.01, 0.012, 0.02, 1); WBG.inputs[1].default_value = 1.0
        SUN.data.energy = 0.25; SUN.data.color = (0.5, 0.8, 0.9)
    else:
        WBG.inputs[0].default_value = (0.008, 0.03, 0.03, 1); WBG.inputs[1].default_value = 1.0
        SUN.data.energy = 0.35; SUN.data.color = (0.4, 0.9, 0.7)

# ---------------------------------------------------------------- cast placement around the table (kids on the far side face the camera)
SPOT = {"jayden": (-2.6, 4.3), "maya": (0.2, 4.5), "leo": (3.0, 4.2), "tyrone": (6.0, 3.9), "rico": (9.6, 0.8)}
MAKERS = {"jayden": mk_jayden, "maya": mk_maya, "leo": mk_leo, "tyrone": mk_tyrone, "rico": mk_rico}
def kid(name, loc=None, rotz=0.0):
    c = MAKERS[name](TEMP); p = loc or (*SPOT[name], 0)
    c.place(p, rotz); return c
def look_rot(src, dst):
    d = Vector(dst) - Vector(src); return math.atan2(d.y, d.x) + math.pi / 2
def talk(c, shot, base, t0=0, t1=99):
    for w, a, b in WORDS[shot]:
        if t0 <= a < t1:
            c.set_face("talk", F(a)); c.set_face(base, F(a) + max(2, int((b - a) * FPS * 0.7)))
def hold_pose(c, f0, f1, **kw):
    for f in range(f0, f1 + 1, 2):
        t = f / 24; kw2 = dict(kw); kw2.setdefault("hips_z", 2.0); kw2["hips_z"] += 0.02 * math.sin(t * 2.4)
        hd = kw2.get("head", (0, 0, 0)); kw2["head"] = (hd[0] + 0.03 * math.sin(t * 1.7), hd[1], hd[2] + 0.04 * math.sin(t * 1.1))
        c.pose(f, **kw2)
def dust(n):
    for k, d in enumerate(DUST):
        p0 = d.location.copy()
        for f in (1, n):
            d.location = p0 + Vector((0.3 * math.sin(k), 0.2 * math.cos(k * 1.3), 0.4 * (f / max(1, n)))); d.keyframe_insert("location", frame=f)

# ---------------------------------------------------------------- shots
def s01(n):   # HOOK: dice tumbling in emerald slow-mo above the board (macro, orbit)
    show_set(); BGLOW.data.energy = 120
    for i in range(6): gem_on(GEMS[i], 1, 6)
    c = Vector((0, -0.4, TT + 0.06))
    tumble(DICE[0], 1, n, c + Vector((-0.6, -0.3, 2.4)), c + Vector((-0.2, 0.2, 0.25)), spins=(1.2, 0.8, 0.5), arc=0.3)
    tumble(DICE[1], 1, n, c + Vector((0.5, 0.2, 2.9)), c + Vector((0.45, -0.1, 0.25)), spins=(0.9, 1.1, 0.4), arc=0.4)
    j = kid("jayden"); j.set_face("excited", 1); hold_pose(j, 1, n, arms=(1.2, 0.3), arms_side=(0.1, 0.1), head=(0.3, 0, 0))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); a = -1.9 + 0.7 * u; r = 4.2 - 1.2 * u
        cam2(f, c + Vector((math.cos(a) * r, math.sin(a) * r, 1.4 + 0.4 * u)), c + Vector((0, 0, 1.4 - 0.4 * u)), 50, 0.08 * math.sin(u * 3))
def s02(n):   # Jayden pulls the box off the locked shelf
    show_set()
    j = kid("jayden", (-11.2, 22.6, 0), look_rot((-11.2, 22.6), (-11, 26))); j.set_face("excited", 1)
    gr = int(n * 0.35)
    for f in range(1, n + 1):
        u = min(1, max(0, (f - gr) / (n - gr)))
        j.pose(f, arms=(1.6 - 0.6 * u, 1.6 - 0.6 * u), arms_side=(0.05, 0.05), lean=0.15 - 0.2 * u, head=(-0.2 + 0.2 * u, 0, 0))
        GBOX.location = CAB + Vector((0, -0.1, 6.6)) + Vector((0, -2.6 * ease(u), -1.6 * ease(u))); GBOX.keyframe_insert("location", frame=f)
    j.set_face("laugh", gr + 4)
    cpath(n, (-11.9, 25.45, 5.7), (-11.2, 22.0, 4.5), (-11.7, 25.45, 5.5), (-11.2, 22.0, 4.6), 22, 24, 0.0, 0.0)
def s03(n):   # the board unfolds: it's a map of our town (top-down push, emerald pulse)
    show_set(); BGLOW.data.energy = 0
    for f in range(1, n + 1):
        u = ease(min(1, (f - 1) / (n * 0.6)))
        for hinge, sx in BHALF: hinge.rotation_euler = (0, 0 if sx < 0 else -math.pi * (1 - u) * 0.98, 0); hinge.keyframe_insert("rotation_euler", frame=f)
        BGLOW.data.energy = 220 * u; BGLOW.data.keyframe_insert("energy", frame=f)
    for i in range(6): gem_on(GEMS[i], int(n * 0.55) + i * 2, 10)
    c = Vector((0, -0.4, TT))
    cpath(n, c + Vector((0, -0.6, 7.5)), c, c + Vector((0, -0.25, 4.6)), c, 32, 34, 0.4, 0.0)
def s04(n):   # Maya grabs his arm: "Jayden, don't!"
    show_set(); BGLOW.data.energy = 140
    j = kid("jayden"); m = kid("maya", (-0.5, 4.6, 0), look_rot((-0.5, 4.6), (-2.6, 4.3)))
    j.set_face("smug", 1); m.set_face("scared", 1); talk(m, "s04", "scared")
    for f in range(1, n + 1):
        u = ease(min(1, f / 8))
        j.pose(f, arms=(0.3, 1.25), arms_side=(0.1, 0.2), head=(0.05, 0, -0.35 * u))
        m.pose(f, arms=(1.5 * u, 0.3), arms_side=(-0.25 * u, 0.1), lean=0.1 * u, head=(0, 0, 0))
    die = DICE[0]; die.parent = j.arms[1]; die.location = (0, -0.3, -2.25); die.rotation_euler = (0.3, 0.2, 0.1)
    cpath(n, (0.8, -7.0, 4.9), (-1.5, 4.4, 4.3), (0.5, -5.6, 4.8), (-1.5, 4.4, 4.4), 30, 34, 0.04, 0.0)
def s05(n):   # "Obviously... he rolled."  smug, then the throw (low angle across the board)
    show_set(); BGLOW.data.energy = 160
    j = kid("jayden"); j.set_face("smug", 1)
    m = kid("maya", (-0.6, 4.6, 0)); m.set_face("scared", 1); hold_pose(m, 1, n, arms=(0.4, 0.4), head=(0, 0, -0.4))
    th = F(wt("s05", "rolled.")) - 3
    for f in range(1, n + 1):
        if f < th - 6: j.pose(f, arms=(0.3, 2.2), arms_side=(0.1, 0.2), head=(0.0, 0, 0.1))
        else:
            u = min(1, (f - th + 6) / 8); j.pose(f, arms=(0.3, 2.2 - 1.6 * ease(u) + 0.8 * math.sin(u * 3.1)), arms_side=(0.1, 0.1), lean=0.25 * u, head=(0.15 * u, 0, 0))
    j.set_face("blink", 6); j.set_face("smug", 9); j.set_face("excited", th)
    c = Vector((0, -0.4, TT + 0.1))
    tumble(DICE[0], th, n, Vector((-2.4, 2.8, 4.4)), c + Vector((0.6, 0.2, 0.6)), spins=(1.5, 1, 0.5), arc=0.6)
    cpath(n, (1.2, -4.8, TT + 0.9), (-1.6, 4.3, 4.2), (0.8, -3.8, TT + 0.8), (-1.6, 4.3, 4.0), 26, 30, -0.06, -0.1)
def s05b(n):  # the dice tumble across the town map in slow-mo, settle on SIX, burst
    show_set(); BGLOW.data.energy = 200
    c = Vector((0, -0.4, TT + 0.27))
    tumble(DICE[0], 1, int(n * 0.75), c + Vector((-1.0, 0.8, 0.9)), c + Vector((0.3, -0.2, 0)), spins=(1.5, 1.0, 0.6), arc=0.5, settle_rot=(math.pi, 0, 0))
    land = int(n * 0.75)
    for f in range(land, n + 1): DICE[0].location = c + Vector((0.3, -0.2, 0)); DICE[0].keyframe_insert("location", frame=f)
    BGLOW.data.energy = 200; BGLOW.data.keyframe_insert("energy", frame=land - 1); BGLOW.data.energy = 1600; BGLOW.data.keyframe_insert("energy", frame=land + 2)
    for i in range(6): gem_on(GEMS[i], land, 14)
    cpath(n, c + Vector((-2.4, -3.4, 1.1)), c + Vector((-0.2, 0.2, 0.0)), c + Vector((-1.2, -2.4, 0.8)), c + Vector((0.3, -0.2, 0.05)), 42, 50, 0.1, 0.0)
SHARDS = []
def make_shards(coll, n=160):
    rnd = random.Random(21); m = emat("shard", (0.3, 0.75, 0.8), 1.5, base=(0.5, 0.8, 0.9)); out = []
    for k in range(n):
        y = rnd.choice(WIN_YS) + rnd.uniform(-2.8, 2.8); z = rnd.uniform(4, 15)
        me = bpy.data.meshes.new("shard"); s = rnd.uniform(0.25, 0.8)
        me.from_pydata([(0, 0, 0), (s, rnd.uniform(-0.2, 0.2), rnd.uniform(-0.3, 0.3)), (rnd.uniform(0, s), rnd.uniform(-0.1, 0.1), s * rnd.uniform(0.6, 1.2))], [], [(0, 1, 2)])
        me.materials.append(m); o = bpy.data.objects.new("shard", me); coll.objects.link(o)
        o["p0"] = (-23.4, y, z); o["v"] = (rnd.uniform(6, 16), rnd.uniform(-4, 4), rnd.uniform(-2, 3)); o["w"] = (rnd.uniform(-3, 3), rnd.uniform(-3, 3), rnd.uniform(-3, 3))
        out.append(o)
    return out
def shatter(shards, f0, n, slow=0.9):
    """burst then decelerate to a near-freeze (bullet-time)"""
    for o in shards:
        p0 = Vector(o["p0"]); v = Vector(o["v"]); w = o["w"]
        for f in range(1, n + 1, 2):
            t = max(0, (f - f0) / 24); tt = (1 - math.exp(-t * 6)) / 6 * (1 - slow) + t * 0.04 * slow if t > 0 else 0
            tt = (1 - math.exp(-t * 7)) / 7 + 0.035 * t
            o.location = p0 + v * tt; o.rotation_euler = (w[0] * tt * 3, w[1] * tt * 3, w[2] * tt * 3)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
def hide_panes(f):
    for p in PANES:
        p.hide_render = False; p.keyframe_insert("hide_render", frame=max(1, f - 1)); p.hide_render = True; p.keyframe_insert("hide_render", frame=f)
def s06(n):   # every window shatters; the glass freezes mid-air; dolly through it
    show_set(); BGLOW.data.energy = 300
    sh = make_shards(TEMP); f0 = 4; hide_panes(f0); shatter(sh, f0, n)
    kids = []
    for nm in ("jayden", "maya", "leo", "tyrone"):
        c = kid(nm, rotz=look_rot(SPOT[nm], (-23, 0))); c.set_face("shocked", 1)
        for f in range(1, n + 1):
            u = min(1, max(0, (f - f0) / 5)); c.pose(f, arms=(2.0 * u, 2.0 * u), arms_side=(-0.3, -0.3), hips_z=2.0 - 0.5 * u, lean=0.3 * u, head=(0.2 * u, 0, 0))
        kids.append(c)
    cpath(n, (-6, -10, 6.5), (-22, -2, 9.0), (-14.5, -6, 8.0), (-23, 2, 9.5), 24, 26, 0.12, 0.05)
def s07(n):   # Leo laughing -> CRASH (door) -> shock
    show_set(); BGLOW.data.energy = 160
    l = kid("leo"); l.set_face("laugh", 1); cr = F(2.95)
    for f in range(1, n + 1):
        t = f / 24
        if f < cr: l.pose(f, arms=(1.5, 0.4), arms_side=(0.05, 0.3), lean=0.12 + 0.05 * math.sin(t * 20), hips_z=2.0 + 0.05 * abs(math.sin(t * 20)), head=(-0.3 + 0.08 * math.sin(t * 20), 0, 0.1))
        else:
            u = min(1, (f - cr) / 4); l.pose(f, arms=(2.2 * u, 2.2 * u), arms_side=(-0.3, -0.3), lean=-0.2 * u, hips_z=2.0 + 0.3 * u, head=(-0.2, 0, 1.0 * u))
    talk(l, "s07", "laugh", 0, 2.6); l.set_face("shocked", cr)
    cpath(n, (2.6, -2.2, 5.2), (3.0, 4.2, 4.9), (2.8, -0.8, 5.0), (3.0, 4.2, 4.9), 34, 42, 0.0, 0.0)
def s08(n):   # the crocodile smashes through the double doors (low angle)
    show_set(); BGLOW.data.energy = 160
    cr = Croc(TEMP, 1.15); cr.place(DOOR + Vector((6, 0, 0)), math.pi / 2)
    for f, (dl, dr) in [(1, (0, 0)), (3, (0, 0)), (6, (-1.9, 1.9)), (9, (-2.3, 2.3))]:
        DOORL.rotation_euler = (0, 0, dl); DOORL.keyframe_insert("rotation_euler", frame=f); DOORR.rotation_euler = (0, 0, dr); DOORR.keyframe_insert("rotation_euler", frame=f)
    cr.move(1, n, DOOR + Vector((8, 0, 0)), DOOR + Vector((-9, 1, 0)), rotz=-math.pi / 2)
    cr.anim(1, n, speed=1.3, snap=1.0)
    splinters = []
    rnd = random.Random(2)
    for k in range(40):
        o = box("splinter", DOOR, (0.15, rnd.uniform(0.3, 1.2), 0.15), wood2, coll=TEMP); p0 = DOOR + Vector((-0.3, rnd.uniform(-3.5, 3.5), rnd.uniform(1, 9)))
        v = Vector((-rnd.uniform(4, 10), rnd.uniform(-4, 4), rnd.uniform(-1, 4)))
        for f in range(1, n + 1, 2):
            t = max(0, (f - 4) / 24); o.location = p0 + v * t + Vector((0, 0, -4.9 * t * t)); o.rotation_euler = (t * 6 + k, t * 4, t * 3)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
    cpath(n, DOOR + Vector((-16, -6, 0.8)), DOOR + Vector((0, 0, 3.0)), DOOR + Vector((-13, -5, 0.6)), DOOR + Vector((-4, 0, 2.2)), 22, 24, -0.12, -0.18)
def s09(n):   # Tyrone vs crocodile with a chair (Whiskers secretly nudges the dice on the table behind)
    show_set(); BGLOW.data.energy = 180
    t = kid("tyrone", (9.0, -6.0, 0), look_rot((9.0, -6.0), (14, -9))); t.set_face("determined", 1)
    ch = CHAIRS[1]; ch0 = ch.location.copy(); ch0r = ch.rotation_euler.copy()
    for f in range(1, n + 1):
        tt = f / 24; s = math.sin(tt * 9)
        t.pose(f, arms=(1.7 + 0.15 * s, 1.7 - 0.15 * s), arms_side=(0.2, 0.2), lean=0.1, hips_z=1.8 + 0.06 * s, legs=(0.3, -0.3), head=(0.1, 0, 0.1 * s))
    ch.parent = t.root; ch.location = (0, -2.6, 3.2); ch.rotation_euler = (math.pi / 2 - 0.2, 0, 0)
    t.set_face("talk", F(wt("s09", "gladiator,"))); t.set_face("determined", F(wt("s09", "gladiator,")) + 6)
    cr = Croc(TEMP, 1.1); cr.place((14.5, -9.5, 0), look_rot((14.5, -9.5), (9, -6))); cr.anim(1, n, speed=1.4, snap=1.2, walk=False)
    cat = Cat(TEMP, 0.8); cat.root.location = (0.9, -1.5, TT); cat.root.rotation_euler = (0, 0, 0.6); cat.sit(1); cat.tailwag(1, n)
    DICE[0].location = (0.4, -1.9, TT + 0.25)
    nud = int(n * 0.55)
    for f in range(1, n + 1):
        u = max(0, min(1, (f - nud) / 6)); cat.legs[0].rotation_euler = (0.5 + 1.2 * math.sin(u * math.pi), 0, 0); cat.legs[0].keyframe_insert("rotation_euler", frame=f)
        DICE[0].location = Vector((0.4, -1.9, TT + 0.25)) + Vector((-0.25, -0.1, 0)) * ease(u); DICE[0].keyframe_insert("location", frame=f)
    cpath(n, (16.8, -5.4, 4.6), (10.2, -6.8, 3.6), (16.0, -5.6, 4.4), (10.2, -6.8, 3.7), 24, 26, 0.04, 0.0)
def s10(n):   # Rico's phone POV: chaos, then selfie swing ("going straight on my story")
    show_set(); BGLOW.data.energy = 200
    r = kid("rico", (9.6, 3.0, 0), 0.0); r.set_face("laugh", 1)
    t = kid("tyrone"); cr = Croc(TEMP, 1.05)
    t.walk(1, n, (4, -6, 0), (-6, -6, 0), run=True); t.set_face("scared", 1)
    cr.move(1, n, (10, -7, 0), (-1, -7.5, 0)); cr.anim(1, n, 1.5, 1.2)
    l = kid("leo"); l.walk(1, n, (-2, 6, 0), (-12, 4, 0), run=True); l.set_face("scared", 1)
    sw = F(wt("s10", "this")) - 4
    hd = Vector((9.6, 2.1, 4.6))
    for f in range(1, n + 1):
        if f < sw:
            cam2(f, hd + Vector((0.1 * math.sin(f * 1.7), -0.2, 0.08 * math.sin(f * 2.3))), Vector((2, -6.5, 1.8)) + Vector((-6 * f / sw, 0, 0)), 24, 0.06 * math.sin(f * 0.9))
        else:
            u = ease(min(1, (f - sw) / 5))
            cam2(f, Vector((9.9, 0.6, 4.7)) + Vector((0.05 * math.sin(f * 1.7), 0, 0.05 * math.sin(f * 2.1))), Vector((-4, -6.5, 2)).lerp(Vector((9.6, 3.0, 4.4)), u), 22, 0.05 * math.sin(f))
    for f in range(1, n + 1):
        r.pose(f, arms=(1.6, 0.2), arms_side=(0.4, 0.1), head=(0, 0, 0.0 if f < sw else -0.5), hips_z=2.0)
    talk(r, "s10", "laugh", wt("s10", "this"))
def s11(n):   # the game speaks: everything freezes, six squares light up, faces lit green from below
    show_set()
    for f, e in [(1, 300), (F(wt("s11", "six")), 2200), (n, 2600)]: BGLOW.data.energy = e; BGLOW.data.keyframe_insert("energy", frame=f)
    for nm in ("jayden", "maya", "leo", "tyrone"):
        c = kid(nm); c.set_face("scared", 1); hold_pose(c, 1, n, arms=(0.5, 0.5), lean=0.25, head=(0.35, 0, 0))
    cr = Croc(TEMP, 1.05); cr.place((-12, -9, 0), look_rot((-12, -9), (0, 0)))
    cr.jaw.rotation_euler = (0.7, 0, 0); cr.jaw.keyframe_insert("rotation_euler", frame=1)
    for i in range(6): gem_on(GEMS[i], F(wt("s11", "six")) + i * 3, 18)
    c = Vector((0, -0.4, TT))
    cpath(n, c + Vector((0, -6.5, 3.4)), c + Vector((0, 3, 1.8)), c + Vector((0, -3.6, 1.6)), c + Vector((0, 2.5, 2.6)), 26, 30, 0.0, 0.0)
def s12(n):   # Maya close-up: "There's only five of us."
    show_set(); BGLOW.data.energy = 2200
    m = kid("maya"); m.set_face("scared", 1); talk(m, "s12", "scared")
    for f in range(1, n + 1):
        t = f / 24; m.pose(f, arms=(0.6, 0.6), lean=0.2, head=(0.25, 0, 0.35 * math.sin(t * 2.6)))
    cpath(n, (0.2, -5.0, 4.6), (0.2, 4.5, 4.4), (0.2, -3.6, 4.6), (0.2, 4.5, 4.5), 32, 36, 0.03, 0.0)
CATSPOT = Vector((1.0, -1.6, TT))
def s13(n):   # everyone slowly turns to the cat (camera behind the cat, low)
    show_set(); BGLOW.data.energy = 1600
    cat = Cat(TEMP, 0.85); cat.root.location = CATSPOT; cat.root.rotation_euler = (0, 0, math.pi); cat.sit(1); cat.tailwag(1, n, 0.3, 1.0)
    for k_, nm in enumerate(("jayden", "maya", "leo", "tyrone", "rico")):
        sp = SPOT[nm] if nm != "rico" else (6.0, -3.2)
        c = kid(nm, (*sp, 0), look_rot(sp, (0, 0)) + (0.6 if k_ % 2 else -0.6))
        tf = 6 + k_ * 7; c.set_face("scared", 1); c.set_face("shocked", tf + 6)
        for f in range(1, n + 1):
            u = ease(min(1, max(0, (f - tf) / 14)))
            c.pose(f, arms=(0.3, 0.3), head=(0.15 * u, 0, -(0.6 if k_ % 2 else -0.6) * u), hips_z=2.0)
    cpath(n, CATSPOT + Vector((0.2, -4.2, 1.2)), CATSPOT + Vector((0, 4, 3.0)), CATSPOT + Vector((0.1, -2.6, 1.1)), CATSPOT + Vector((0, 4, 3.4)), 30, 34, 0.0, 0.0)
def s14(n):   # Whiskers swats the dice (close), they roll, glow burst
    show_set(); BGLOW.data.energy = 1800
    cat = Cat(TEMP, 0.85, crown=False); cat.root.location = CATSPOT; cat.root.rotation_euler = (0, 0, 0.2); cat.sit(1); cat.tailwag(1, n, 0.5, 2.0)
    sw = F(wt("s14", "rolled!")) - 2
    for f in range(1, n + 1):
        u = max(0, min(1, (f - sw + 6) / 6)); cat.legs[0].rotation_euler = (0.5 + 1.6 * math.sin(min(1, u) * math.pi), 0, 0); cat.legs[0].keyframe_insert("rotation_euler", frame=f)
        cat.neck.rotation_euler = (0.45, 0, 0.3 * math.sin(f / 10)); cat.neck.keyframe_insert("rotation_euler", frame=f)
    c = CATSPOT + Vector((0, -1.1, 0.25))
    for f in range(1, sw): DICE[0].location = c; DICE[0].keyframe_insert("location", frame=f)
    tumble(DICE[0], sw, n, c, c + Vector((-1.6, -0.6, 0)), spins=(2, 1, 0.5), arc=0.4)
    for f, e in [(1, 1800), (sw + 6, 1800), (sw + 9, 5000), (n, 3000)]: BGLOW.data.energy = e; BGLOW.data.keyframe_insert("energy", frame=f)
    cpath(n, CATSPOT + Vector((-3.2, -5.2, 1.6)), CATSPOT + Vector((-0.3, -0.4, 0.8)), CATSPOT + Vector((-2.4, -4.0, 1.2)), CATSPOT + Vector((-0.4, -0.8, 0.6)), 34, 38, 0.08, 0.02)
VORTEX_SPLIT = 0.58
def s15(n):   # the library melts into an emerald vortex (books spiral up) -> flash -> jungle reveal
    nsplit = int(n * VORTEX_SPLIT)
    show_set(lib=True, jun=True); BGLOW.data.energy = 4000
    rnd = random.Random(5); bm_ = bmats
    for k in range(140):
        o = box("flybook", (0, 0, 0), (0.3, 1.1, 1.5), bm_[k % len(bm_)], coll=TEMP, bevel=0.03)
        r0 = rnd.uniform(4, 20); a0 = rnd.uniform(0, 6.28); z0 = rnd.uniform(0.5, 14); sp = rnd.uniform(1.5, 3.0)
        for f in range(1, nsplit + 1, 2):
            t = f / 24; r = r0 * max(0.15, 1 - t * 0.35); a = a0 + t * sp; z = z0 + t * 4
            o.location = (math.cos(a) * r, math.sin(a) * r, z); o.rotation_euler = (t * 3 + k, t * 2, a)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
    for nm in ("jayden", "maya", "leo", "tyrone", "rico"):
        c = kid(nm, (*(SPOT[nm] if nm != "rico" else (6.0, -2.0)), 0), look_rot(SPOT[nm] if nm != "rico" else (6, -2), (0, 0))); c.set_face("shocked", 1)
        for f in range(1, nsplit + 1, 2):
            u = f / nsplit; c.pose(f, arms=(2.6, 2.6), arms_side=(0.6, 0.6), hips_z=2.0 + 1.5 * u * u, head=(-0.4, 0, 0))
    # jungle half: kids drop in and land
    for k_, nm in enumerate(("jayden", "maya", "leo", "tyrone", "rico")):
        p = J + Vector((-3.2 + k_ * 1.6, -0.5 + 0.6 * (k_ % 2), 0))
        c = kid(nm, (p.x, p.y, -80), 0.15 * (k_ - 2)); c.set_face("shocked", 1)
        land = nsplit + 5 + k_ * 2
        for f in range(nsplit, n + 1):
            u = min(1, (f - nsplit) / max(1, land - nsplit)); z = 9 * (1 - u) ** 2
            c.move(f, (p.x, p.y, z if f >= nsplit else -80)); c.pose(f, arms=(2.4 * (1 - u) + 0.6, 2.4 * (1 - u) + 0.6), arms_side=(0.5, 0.5), legs=(0.3 * (1 - u), -0.3 * (1 - u)), hips_z=2.0 - (0.5 if f - land in range(0, 4) else 0))
        c.move(nsplit - 1, (p.x, p.y, -80))
    for f in range(1, n + 1):
        if f < nsplit:
            u = f / nsplit; a = u * 2.4; r = 15 - 7 * u
            cam2(f, (math.cos(a) * r, math.sin(a) * r - 2, 6 + 6 * u), (0, 0, 6 + 4 * u), 20, u * 0.7)
        else:
            u = ease((f - nsplit) / max(1, n - nsplit))
            cam2(f, J + Vector((0, -26 + 6 * u, 18 - 12 * u)), J + Vector((0, 0, 3 + 0 * u)), 22, 0.0)
    cut_constant()
JKIDS = [("jayden", (-2.6, -0.4)), ("maya", (-0.9, 0.6)), ("leo", (0.6, -0.6)), ("tyrone", (2.4, 0.5)), ("rico", (3.8, -0.8))]
def jkids(base_face="scared", look_up_at=None, f_up=None, n=1):
    out = {}
    for k_, (nm, (x, y)) in enumerate(JKIDS):
        p = J + Vector((x, y, 0)); c = kid(nm, (p.x, p.y, 0), 0.2 * (k_ - 2)); c.set_face(base_face, 1); out[nm] = c
    return out
def s16(n):   # jungle: "Guys... where's Whiskers?"
    show_set(lib=False, jun=True)
    ks = jkids("scared")
    for k_, (nm, c) in enumerate(ks.items()):
        for f in range(1, n + 1, 2):
            t = f / 24 + k_; c.pose(f, arms=(0.5, 0.5), arms_side=(0.1, 0.1), hips_z=1.95, head=(0.05, 0, 0.6 * math.sin(t * 1.3)))
    talk(ks["leo"], "s16", "scared")
    ff = FIREFLY
    for k, o in enumerate(ff[:40]):
        p0 = o.location.copy()
        for f in (1, n): o.location = p0 + Vector((math.sin(k) * f / n, math.cos(k) * f / n, 0.5 * f / n)); o.keyframe_insert("location", frame=f)
    cpath(n, J + Vector((-5, -11, 4.0)), J + Vector((0.5, 0, 4.0)), J + Vector((3, -10, 4.4)), J + Vector((0.5, 0, 4.2)), 26, 30, 0.0, 0.0)
def s17(n):   # ROAR: they look up -> tilt up the king's tree -> Whiskers on the branch in a golden crown
    show_set(lib=False, jun=True)
    ks = jkids("shocked"); lk = int(n * 0.25)
    for nm, c in ks.items():
        for f in range(1, n + 1, 2):
            u = ease(min(1, max(0, (f - lk) / 8))); c.pose(f, arms=(0.4 + 0.6 * u, 0.4 + 0.6 * u), arms_side=(-0.2 * u, -0.2 * u), hips_z=2.0, head=(-0.55 * u, 0, 0), lean=-0.15 * u)
    cat = Cat(TEMP, 2.3, crown=True); cat.root.location = BRANCH_END; cat.root.rotation_euler = (0, 0, 0); cat.sit(1); cat.tailwag(1, n, 0.4, 1.0)
    for f in range(1, n + 1, 2):
        cat.neck.rotation_euler = (0.45 - 0.2 * ease(min(1, f / n * 2)), 0, 0); cat.neck.keyframe_insert("rotation_euler", frame=f)
    TRACK.append(cat.head)
    tilt = int(n * 0.32)
    for f in range(1, n + 1):
        if f < tilt: cam2(f, J + Vector((0.5, -9.5, 2.6)), J + Vector((0.5, 0, 4.2)), 26)
        else:
            u = ease(min(1, (f - tilt) / (n * 0.45)))
            cam2(f, (J + Vector((0.5, -9.5, 2.6))).lerp(BRANCH_END + Vector((0.5, -15.0, -3.5)), u), (J + Vector((0.5, 0, 4.2))).lerp(BRANCH_END + Vector((0, 0, 1.6)), u), 26 + 8 * u, 0.0)
def s18(n):   # "The final player has been selected." every tree in the ring turns to face them; slow spiral up (hypnotic)
    show_set(lib=False, jun=True)
    ks = jkids("scared")
    for k_, (nm, c) in enumerate(ks.items()):
        for f in range(1, n + 1, 2):
            t = f / 24 + k_; c.pose(f, arms=(0.6, 0.6), arms_side=(0.2, 0.2), hips_z=1.9, head=(0.0, 0, 0.9 * math.sin(t * 0.8 + k_)))
    t0 = F(wt("s18", "final"))
    for k, tr in enumerate(FACE_TREES):
        f_s = t0 + k * 4; f_e = f_s + 18
        for nm_ in tr["feat"]:
            o_ = bpy.data.objects[nm_]; o_.hide_render = True; o_.keyframe_insert("hide_render", frame=1); o_.hide_render = False; o_.keyframe_insert("hide_render", frame=f_s)
        for f in (1, f_s, f_e):
            u = 0 if f < f_e else 1
            tr.rotation_euler = (0, 0, math.pi * u); tr.keyframe_insert("rotation_euler", frame=f)
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); a = -1.7 + 1.6 * u; r = 10 + 6 * u
        cam2(f, J + Vector((math.cos(a) * r, math.sin(a) * r, 4 + 22 * u)), J + Vector((0, 0, 2 + 0 * u)), 22, 0.6 * u)
def s19(n):   # "And that's why..." dice drop into the jungle dirt (mirrors the opening) -> loop
    show_set(lib=False, jun=True)
    c = J + Vector((0.6, -1.4, 0.25))
    light("dicelight", "POINT", c + Vector((0, -0.5, 1.5)), 400, (0.3, 1.0, 0.5), coll=TEMP)
    tumble(DICE[0], 1, int(n * 0.7), c + Vector((-0.6, 0.4, 2.2)), c, spins=(1.2, 0.8, 0.4), arc=0.2)
    tumble(DICE[1], 1, int(n * 0.8), c + Vector((0.6, 0.6, 2.8)), c + Vector((0.6, 0.3, 0)), spins=(0.8, 1.2, 0.5), arc=0.2)
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); a = -1.9 + 0.5 * u; r = 3.8 - 0.8 * u
        cam2(f, c + Vector((math.cos(a) * r, math.sin(a) * r, 1.3)), c + Vector((0, 0, 1.0 - 0.6 * u)), 50, 0.05)

TRACK = []
def track_json(n):
    from bpy_extras.object_utils import world_to_camera_view
    out = []
    for f in range(1, n + 1):
        S.frame_set(f)
        if not TRACK: out.append(None); continue
        p = TRACK[0].matrix_world.translation; v = world_to_camera_view(S, CAM, p); out.append((round(v.x, 4), round(1 - v.y, 4), round(v.z, 2)))
    return out

SHOTS = {k: v for k, v in list(globals().items()) if k.startswith("s") and k[1:3].isdigit() and callable(v)}
os.makedirs(OUT, exist_ok=True); os.makedirs(f"{E}/preview", exist_ok=True)
STATIC = [GBOX, BGLOW.data, DOORL, DOORR, CHAIRS[1]] + DICE + FACE_TREES + PANES + DUST + FIREFLY + [h for h, _ in BHALF]
CH1 = (CHAIRS[1].location.copy(), CHAIRS[1].rotation_euler.copy())
for name in TL["shots"]:
    if ONLY and name not in ONLY: continue
    n = max(10, int(round(DUR[name] * FPS)))
    clear_temp(); S.frame_set(1)
    for o in STATIC:
        if o.animation_data: o.animation_data_clear()
    for g in GEMS:
        nt = g.data.materials[0].node_tree
        if nt.animation_data: nt.animation_data_clear()
        nt.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
    for p in PANES: p.hide_render = False
    for d in DICE: d.parent = None; d.rotation_euler = (0, 0, 0)
    dice_hide(); GBOX.location = CAB + Vector((0, -0.1, 6.6)); DOORL.rotation_euler = (0, 0, 0); DOORR.rotation_euler = (0, 0, 0)
    CHAIRS[1].parent = None; CHAIRS[1].location, CHAIRS[1].rotation_euler = CH1[0].copy(), CH1[1].copy()
    for t in FACE_TREES:
        t.rotation_euler = (0, 0, 0)
        for nm_ in t["feat"]:
            o_ = bpy.data.objects[nm_]
            if o_.animation_data: o_.animation_data_clear()
            o_.hide_render = True
    for h, sx in BHALF: h.rotation_euler = (0, 0, 0)
    BGLOW.data.energy = 0
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
