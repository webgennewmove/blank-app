import bpy, math, random, sys, os, json
sys.path.insert(0, "/home/claude/zara")
bpy.ops.wm.read_factory_settings(use_empty=True)
import lib
from lib import *
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = set(argv[0].split(",")) if argv and argv[0] not in ("all",) else None
STILL = len(argv) > 1 and argv[1] == "still"       # render one mid frame per shot (preview)
OUT = "/home/claude/zara/frames"
FPS = 24
S = bpy.context.scene
S.render.fps = FPS
S.render.engine = "BLENDER_WORKBENCH"
S.render.resolution_x, S.render.resolution_y = 576, 1024
S.render.film_transparent = True
S.render.image_settings.file_format = "PNG"; S.render.image_settings.color_mode = "RGBA"
S.display.render_aa = "8"
sh = S.display.shading
sh.light = "STUDIO"; sh.studio_light = "outdoor.sl"; sh.color_type = "TEXTURE"; sh.show_shadows = os.environ.get("SHADOWS","0")=="1"; sh.shadow_intensity = 0.45
sh.show_cavity = True; sh.cavity_type = "BOTH"; sh.cavity_ridge_factor = 0.6; sh.cavity_valley_factor = 1.0
sh.show_specular_highlight = True
S.display.light_direction = (0.45, -0.35, 0.82)
S.display.shadow_focus = 0.2
S.view_settings.view_transform = "Standard"
random.seed(11)

WORLD = collection("world")
TEMP = collection("temp")

# ---------------------------------------------------------------- palette
C = dict(grass=(0.36, 0.78, 0.28), grass2=(0.3, 0.7, 0.25), road=(0.22, 0.23, 0.26), line=(0.97, 0.97, 0.9),
         walk=(0.78, 0.78, 0.76), curb=(0.88, 0.88, 0.86), roof=(0.2, 0.2, 0.24), roof2=(0.45, 0.22, 0.18),
         trim=(0.98, 0.98, 0.96), glass=(0.55, 0.8, 0.98), door=(0.65, 0.28, 0.12), pine=(0.12, 0.42, 0.22),
         leaf=(0.3, 0.68, 0.22), bark=(0.45, 0.3, 0.18), mount=(0.58, 0.66, 0.78), mount2=(0.68, 0.74, 0.84))
WALLS = [(0.82, 0.58, 0.38), (0.9, 0.82, 0.62), (0.72, 0.42, 0.32), (0.62, 0.78, 0.9), (0.95, 0.9, 0.8), (0.98, 0.78, 0.7)]
M = {k: mat(k, v) for k, v in C.items()}
BULBS = [mat(f"bulb{i}", c, 0.2) for i, c in enumerate([(1, 0.2, 0.3), (1, 0.85, 0.1), (0.2, 0.9, 0.4), (0.1, 0.8, 1.0), (1, 0.4, 0.9)])]

# ---------------------------------------------------------------- terrain + road (street along Y at x=0)
box("ground", (0, 0, -0.5), (600, 900, 1), M["grass"], coll=WORLD)
box("road", (0, 0, 0.02), (9, 900, 0.1), M["road"], coll=WORLD)
for y in range(-400, 400, 8):
    box("dash", (0, y, 0.08), (0.3, 3.2, 0.02), M["line"], coll=WORLD)
for sx in (-1, 1):
    box("curb", (sx * 4.75, 0, 0.12), (0.5, 900, 0.3), M["curb"], coll=WORLD)
    box("walk", (sx * 6.5, 0, 0.1), (3.0, 900, 0.2), M["walk"], coll=WORLD)
    for y in range(-400, 400, 3):
        box("joint", (sx * 6.5, y, 0.21), (3.0, 0.06, 0.01), mat("joint", (0.65, 0.65, 0.63)), coll=WORLD)

def pine(x, y, h=10):
    cyl("ptrunk", (x, y, 1), 0.4, 2, M["bark"], verts=6, coll=WORLD, smooth=False)
    for i in range(3):
        cone("pcone", (x, y, 2.2 + i * h * 0.22 + h * 0.15), h * 0.32 * (1 - i * 0.22), h * 0.42, M["pine"], verts=8, coll=WORLD)

def tree(x, y, h=7):
    cyl("trunk", (x, y, h * 0.35), 0.45, h * 0.7, M["bark"], verts=6, coll=WORLD, smooth=False)
    for dx, dy, dz, r in [(0, 0, h * 0.85, h * 0.32), (0.9, 0.5, h * 0.7, h * 0.24), (-0.8, -0.4, h * 0.72, h * 0.25), (0.2, -0.9, h * 0.95, h * 0.2)]:
        sphere("leafball", (x + dx, y + dy, dz), r, M["leaf"], coll=WORLD, seg=10)

def house(x, y, face, wall, two_storey=True, roofc="roof", number=None, garage=True):
    """face=+1 front faces +x (left side of road), -1 front faces -x (right side)."""
    wm = mat(f"wall{wall}", wall, 0.8)
    H = 8.5 if two_storey else 5
    D, W = 11, 13
    box("hbody", (x, y, H / 2), (D, W, H), wm, coll=WORLD)
    prism("hroof", (x, y, H), (D + 1.2, W + 1.0, 4.2), M[roofc], rot=(0, 0, math.pi / 2), coll=WORLD)
    fx = x + face * (D / 2 + 0.02)
    def window(yy, zz, w=2.4, h=2.2):
        box("wframe", (fx, yy, zz), (0.2, w + 0.35, h + 0.35), M["trim"], coll=WORLD)
        box("wglass", (fx + face * 0.06, yy, zz), (0.2, w, h), M["glass"], coll=WORLD)
        box("wbar", (fx + face * 0.12, yy, zz), (0.12, 0.14, h), M["trim"], coll=WORLD)
        box("wbar", (fx + face * 0.12, yy, zz), (0.12, w, 0.14), M["trim"], coll=WORLD)
        box("sill", (fx + face * 0.25, yy, zz - h / 2 - 0.2), (0.5, w + 0.6, 0.2), M["trim"], coll=WORLD)
    window(y - 3.2, 2.8); window(y + 3.4, 2.8)
    if two_storey:
        window(y - 3.2, 6.6); window(y + 3.4, 6.6)
    box("doorframe", (fx, y + 0.1, 1.7), (0.2, 2.2, 3.6), M["trim"], coll=WORLD)
    box("door", (fx + face * 0.08, y + 0.1, 1.6), (0.2, 1.8, 3.3), mat(f"door{wall}", random.choice([(0.65, 0.28, 0.12), (0.2, 0.45, 0.75), (0.75, 0.15, 0.2), (0.2, 0.55, 0.35)])), coll=WORLD)
    sphere("knob", (fx + face * 0.22, y + 0.7, 1.6), 0.09, mat("brass", (0.95, 0.75, 0.2)), coll=WORLD)
    box("step", (fx + face * 0.8, y + 0.1, 0.15), (1.6, 2.8, 0.3), M["walk"], coll=WORLD)
    box("path", (fx + face * ((abs(x) - 7.8 - D / 2) / 2 + 0.8), y + 0.1, 0.03), (abs(x) - 7.8 - D / 2, 2.0, 0.06), M["walk"], coll=WORLD)
    if number:
        box("numplate", (fx + face * 0.05, y - 1.4, 3.6), (0.1, 0.6, 0.6), mat("numgreen", (0.1, 0.6, 0.3)), coll=WORLD)
    if garage:
        gy = y + face * 0 + (W / 2 + 3.2)
        box("garage", (x, gy, 2.5), (D - 1, 6, 5), wm, coll=WORLD)
        prism("groof", (x, gy, 5), (D, 6.6, 1.6), M[roofc], rot=(0, 0, math.pi / 2), coll=WORLD)
        box("gdoor", (fx - face * 0.48, gy, 1.9), (0.2, 4.6, 3.8), mat("gdoor", (0.92, 0.92, 0.9)), coll=WORLD)
        for k in range(4):
            box("gline", (fx - face * 0.4, gy, 0.6 + k * 0.9), (0.1, 4.6, 0.06), mat("gline", (0.75, 0.75, 0.72)), coll=WORLD)
        box("drive", ((fx + face * 0 + (x / abs(x)) * 7.8) / 2 if False else x + face * (D / 2 + (abs(x) - D / 2 - 7.8) / 2), gy, 0.04), (abs(x) - D / 2 - 7.8, 5.5, 0.06), M["walk"], coll=WORLD)
    # hedge / flowers along front
    for k in range(4):
        yy = y - 5.5 + k * 1.2
        sphere("bush", (fx + face * 1.2, yy, 0.6), 0.75, M["grass2"], coll=WORLD, seg=8)
    for k in range(5):
        sphere("flower", (fx + face * 1.9, y - 5.6 + k * 1.0, 0.6), 0.22, mat(f"fl{k%3}", [(1, 0.3, 0.5), (1, 0.85, 0.2), (0.6, 0.3, 1)][k % 3]), coll=WORLD, seg=6)
    # mailbox
    mx = (8.6) * (1 if x > 0 else -1)
    box("mpost", (mx, y - 2.5, 0.8), (0.2, 0.2, 1.6), mat("mpost", (0.95, 0.95, 0.95)), coll=WORLD)
    box("mbox", (mx, y - 2.5, 1.75), (0.6, 0.9, 0.55), mat("mbox", (0.08, 0.08, 0.1)), coll=WORLD, bevel=0.1)

HOUSES = {}
HOOD = os.environ.get('HOOD') == '1'
for i, y in (enumerate(range(-180, 200, 20)) if not HOOD else []):
    for side in (-1, 1):
        x = side * 15.5
        wall = WALLS[(i * 2 + (side > 0)) % len(WALLS)]
        house(x, y + (4 if side > 0 else 0), -side, wall, two_storey=(i + (side > 0)) % 3 != 2,
              roofc="roof" if (i + side) % 2 else "roof2", number=True, garage=(i % 2 == 0))
        HOUSES[(side, y)] = (x, y + (4 if side > 0 else 0))
        tree(side * 9.5, y + 9, random.uniform(6, 8))
    for side in (-1, 1):
        for k in range(3):
            pine(side * random.uniform(26, 34), y + random.uniform(-8, 8), random.uniform(10, 15))
# far mountains + hills
for k in (range(14) if not HOOD else []):
    for sgn in (-1, 1):
        cone("mount", (random.uniform(-220, 220), sgn * random.uniform(330, 420), 0), random.uniform(60, 110), random.uniform(50, 85),
             M["mount"] if k % 2 else M["mount2"], verts=7, coll=WORLD, rot=(0, 0, random.uniform(0, 3)))
for k in (range(18) if not HOOD else []):
    sgn = random.choice((-1, 1))
    cone("hillside", (sgn * random.uniform(80, 200), random.uniform(-300, 300), 0), random.uniform(40, 70), random.uniform(30, 55),
         M["mount2"], verts=7, coll=WORLD)
# string lights across the street + lamp posts
for y in (range(-160, 170, 24) if not HOOD else []):
    for sx in (-1, 1):
        box("lpost", (sx * 5.6, y, 3.2), (0.25, 0.25, 6.4), mat("lpost", (0.15, 0.15, 0.18)), coll=WORLD)
        box("lhead", (sx * 5.1, y, 6.5), (1.2, 0.5, 0.3), mat("lpost", (0.15, 0.15, 0.18)), coll=WORLD)
    for k in range(13):
        u = k / 12; xx = -5.6 + 11.2 * u; zz = 6.2 - 1.0 * math.sin(u * math.pi)
        sphere("bulb", (xx, y, zz), 0.22, BULBS[k % 5], coll=WORLD, seg=8)
    rod("wire", (-5.6, y, 6.2), (0, y, 5.2), 0.03, mat("wire", (0.1, 0.1, 0.1)), coll=WORLD)
    rod("wire", (0, y, 5.2), (5.6, y, 6.2), 0.03, mat("wire", (0.1, 0.1, 0.1)), coll=WORLD)

# ---------------------------------------------------------------- bedroom (x=600)
ROOM = collection("room")
R0 = Vector((600, 0, 0))
def R(x, y, z): return (R0.x + x, R0.y + y, R0.z + z)
wallc = mat("roomwall", (0.62, 0.82, 1.0), 0.9)
box("rfloor", R(0, 0, -0.1), (18, 18, 0.2), mat("wood", (0.8, 0.6, 0.4), 0.8), coll=ROOM)
box("rug", R(1, -1, 0.02), (7, 5, 0.05), mat("rug", (1.0, 0.55, 0.75)), coll=ROOM, bevel=0.02)
box("rwallb", R(0, 8, 5.5), (18, 0.4, 11), wallc, coll=ROOM)
box("rwalll", R(-8, 0, 5.5), (0.4, 18, 11), wallc, coll=ROOM)
box("rwallr", R(8, 0, 5.5), (0.4, 18, 11), wallc, coll=ROOM)
box("bed", R(-3.5, 3.5, 0.8), (5, 8, 1.6), mat("bedframe", (1, 1, 1)), coll=ROOM, bevel=0.15)
box("mattress", R(-3.5, 3.5, 1.9), (4.8, 7.8, 0.7), mat("sheet", (0.55, 0.4, 0.95)), coll=ROOM, bevel=0.2)
box("pillow", R(-3.5, 6.6, 2.5), (3.2, 1.3, 0.6), mat("pillow", (1, 1, 1)), coll=ROOM, bevel=0.25)
box("rwindow", R(3, 7.75, 6), (4, 0.2, 3.5), mat("skyglass", (0.6, 0.85, 1.0)), coll=ROOM)
box("rwinframe", R(3, 7.7, 6), (4.4, 0.15, 3.9), M["trim"], coll=ROOM)
for k, c in enumerate([(1, 0.3, 0.3), (0.3, 0.6, 1), (1, 0.85, 0.2)]):
    box("poster", R(-6 + k * 2.6, 7.75, 7.5 + (k % 2) * 0.6), (2, 0.1, 2.6), mat(f"poster{k}", c), coll=ROOM)
for k in range(9):  # bunting
    u = k / 8; xx = -7 + 14 * u; zz = 9.4 - 0.8 * math.sin(u * math.pi)
    cone("flag", R(xx, 7.6, zz - 0.4), 0.45, 0.8, BULBS[k % 5], verts=3, coll=ROOM, rot=(math.pi, 0, 0))
BALLOONS = []
for k, (bx, by, c) in enumerate([(5.5, 5, 0), (6.5, 3.5, 1), (5, 2, 4), (-6.5, -1, 3), (-6, 1.5, 2)]):
    b = sphere("balloon", R(bx, by, 7 + k % 2), 0.9, BULBS[c], coll=ROOM, scale=(0.9, 0.9, 1.1))
    rod("bstring", R(bx, by, 6.0 + k % 2), R(bx, by, 1.0), 0.02, mat("wire", (0.1, 0.1, 0.1)), coll=ROOM)
    BALLOONS.append(b)
box("desk", R(5, -4, 1.5), (3, 5, 0.3), mat("desk", (1, 1, 1)), coll=ROOM)
box("cake", R(5, -4, 2.1), (1.4, 1.4, 0.9), mat("cake", (1, 0.75, 0.85)), coll=ROOM, bevel=0.1)
cyl("candle", R(5, -4, 2.9), 0.08, 0.6, mat("candle", (0.3, 0.7, 1)), coll=ROOM)
sphere("flame", R(5, -4, 3.3), 0.12, mat("flame", (1, 0.8, 0.2)), coll=ROOM)

# ---------------------------------------------------------------- characters
def cap(col):
    def f(c):
        m = mat(f"cap{col}", col)
        box("capcrown", (0, 0.05, 0.72), (1.36, 1.36, 0.38), m, parent=c.head, coll=c.coll, bevel=0.12)
        box("capbrim", (0, -0.85, 0.56), (1.2, 0.7, 0.1), m, parent=c.head, coll=c.coll)
    return f
def glasses(c):
    fm = mat("glassframe", (0.3, 0.15, 0.4))
    for sx in (-0.25, 0.25):
        box("gl_t", (sx, -0.66, 0.2), (0.4, 0.04, 0.05), fm, parent=c.head, coll=c.coll)
        box("gl_b", (sx, -0.66, -0.05), (0.4, 0.04, 0.05), fm, parent=c.head, coll=c.coll)
def party_hat(c):
    cone("phat", (0.2, 0, 1.35), 0.45, 1.1, mat("phat", (1, 0.3, 0.6)), verts=12, parent=c.head, coll=c.coll, rot=(0, 0.2, 0))
    sphere("pom", (0.32, 0, 1.9), 0.17, mat("pom", (1, 0.9, 0.2)), coll=c.coll, parent=c.head)

def mk_zara(hat=False):
    return Char("zara", TEMP, (0.45, 0.27, 0.16), (1.0, 0.78, 0.08), (0.22, 0.4, 0.8), hair="puffs", hair_col=(0.1, 0.06, 0.04),
                shoes=(1, 0.35, 0.6), scale=0.92, extra=(party_hat if hat else None))
def mk_milo():
    return Char("milo", TEMP, (0.98, 0.78, 0.62), (0.15, 0.75, 0.35), (0.12, 0.12, 0.16), hair="spiky", hair_col=(0.9, 0.42, 0.08),
                scale=0.95, extra=None)
def mk_ivy():
    return Char("ivy", TEMP, (0.45, 0.27, 0.16), (0.1, 0.78, 0.78), (0.55, 0.3, 0.85), hair="ponytail", hair_col=(0.1, 0.06, 0.04), scale=1.05)
def mk_gran():
    return Char("gran", TEMP, (0.96, 0.8, 0.68), (0.98, 0.5, 0.72), (0.6, 0.5, 0.85), hair="bun", hair_col=(0.93, 0.93, 0.95),
                shoes=(0.6, 0.35, 0.2), extra=glasses)
KIDCOLS = [((0.7, 0.45, 0.3), (0.95, 0.3, 0.25), (0.2, 0.25, 0.6), "short", (0.15, 0.08, 0.03)),
           ((0.98, 0.82, 0.7), (0.4, 0.35, 0.95), (0.25, 0.25, 0.3), "ponytail", (0.95, 0.8, 0.3)),
           ((0.3, 0.18, 0.1), (1, 0.6, 0.1), (0.2, 0.45, 0.3), "spiky", (0.05, 0.05, 0.05))]
def mk_kid(i):
    s, sh_, p, h, hc = KIDCOLS[i % 3]
    return Char(f"kid{i}", TEMP, s, sh_, p, hair=h, hair_col=hc, scale=0.9)

def mk_truck(coll):
    root = empty("truck", coll=coll)
    red = mat("truckred", (0.92, 0.15, 0.12)); white = mat("truckwhite", (0.97, 0.97, 0.97)); blk = mat("tire", (0.05, 0.05, 0.06))
    box("cab", (0, -4.5, 3.0), (5.6, 4, 4.4), red, parent=root, coll=coll, bevel=0.3)
    box("cargo", (0, 2.5, 4.0), (6, 9, 6.6), white, parent=root, coll=coll, bevel=0.2)
    box("stripe", (0, 2.5, 3.0), (6.05, 9, 0.8), mat("truckstripe", (1, 0.75, 0.1)), parent=root, coll=coll)
    box("windshield", (0, -6.52, 3.9), (4.6, 0.1, 1.8), mat("tglass", (0.25, 0.45, 0.7)), parent=root, coll=coll)
    box("grille", (0, -6.55, 2.0), (3.6, 0.1, 1.2), mat("grille", (0.75, 0.75, 0.8)), parent=root, coll=coll)
    for sx in (-2.1, 2.1):
        sphere("headlight", (sx, -6.55, 2.1), 0.42, mat("hlight", (1, 1, 0.8)), coll=coll, parent=root, scale=(0.42, 0.1, 0.42))
        for sy in (-4.2, 4.5):
            cyl("wheel", (sx * 1.25, sy, 1.05), 1.05, 0.8, blk, rot=(0, math.pi / 2, 0), parent=root, coll=coll)
    # truck face (cute)
    return root

def mk_birds(coll, n=7, center=(0, -10, 16)):
    birds = []
    bm = mat("bird", (0.1, 0.1, 0.15))
    for i in range(n):
        b = empty("bird", coll=coll); b.location = Vector(center) + Vector((random.uniform(-8, 8), random.uniform(-4, 4), random.uniform(-2, 3)))
        for s in (-1, 1):
            box("wing", (s * 0.45, 0, 0), (0.9, 0.3, 0.08), bm, rot=(0, s * 0.45, 0), parent=b, coll=coll)
        box("bbody", (0, 0, -0.05), (0.25, 0.6, 0.2), bm, parent=b, coll=coll)
        birds.append(b)
    return birds

def mk_clouds(coll, y0=60):
    cw = mat("cloud", (1, 1, 1), 0.9); out = []
    for i in range(9):
        c = empty("cloud", coll=coll); c.location = (random.uniform(-70, 70), y0 + random.uniform(-20, 80), random.uniform(38, 60))
        for k in range(5):
            sphere("puff", (random.uniform(-5, 5), random.uniform(-2, 2), random.uniform(0, 2)), random.uniform(2.5, 4.5), cw, coll=coll, parent=c, seg=10)
        out.append(c)
    return out

# ---------------------------------------------------------------- camera
CAM = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); S.collection.objects.link(CAM); S.camera = CAM
CAM.data.clip_end = 3000; CAM.data.clip_start = 0.1
def cam(f, loc, at, lens=30):
    CAM.location = loc; CAM.data.lens = lens
    CAM.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM.keyframe_insert("location", frame=f); CAM.keyframe_insert("rotation_euler", frame=f); CAM.data.keyframe_insert("lens", frame=f)
def cam_path(n, a_loc, a_at, b_loc, b_at, lens_a=30, lens_b=None, ease=True):
    for f in range(1, n + 1):
        u = (f - 1) / max(1, n - 1)
        if ease: u = u * u * (3 - 2 * u)
        L = Vector(a_loc).lerp(Vector(b_loc), u); T = Vector(a_at).lerp(Vector(b_at), u)
        cam(f, L, T, lens_a + ((lens_b or lens_a) - lens_a) * u)
def cam_follow(n, obj, offset, look_off=(0, 0, 4), lens=30):
    for f in range(1, n + 1):
        S.frame_set(f); p = obj.matrix_world.translation.copy()
        cam(f, p + Vector(offset), p + Vector(look_off), lens)

def clear_temp():
    for o in list(TEMP.objects): bpy.data.objects.remove(o, do_unlink=True)
    if CAM.animation_data: CAM.animation_data_clear()
    if CAM.data.animation_data: CAM.data.animation_data_clear()
    for b in BALLOONS:
        if b.animation_data: b.animation_data_clear()

def show(world=True, room=False):
    WORLD.hide_render = not world; ROOM.hide_render = not room

# ---------------------------------------------------------------- shots
DUR = {"s01": 4.2, "s02": 2.8, "s03": 2.4, "s04": 2.8, "s05": 3.4, "s06": 2.6, "s07": 1.8, "s08": 1.8, "s09": 1.8, "s10": 2.0,
       "s11": 2.8, "s12": 2.6, "s13": 3.0, "s14": 2.2, "s15": 2.4, "s16": 2.6, "s17": 3.2, "s18": 2.4, "s19": 3.4, "s20": 2.4,
       "s21": 5.6, "s22": 3.4}
if os.path.exists("/home/claude/zara/timeline.json"):
    DUR.update({k: v for k, v in json.load(open("/home/claude/zara/timeline.json"))["dur"].items()})

ZH = (16 - 5.5, 4)   # zara's house front door approx (x,y) on right side, house at x=15.5,y=4

def s01(n):
    show()
    milo = mk_milo(); milo.place((-3, 6, 0), 0.4)
    for k in range(0, n, 28): milo.jump(k + 1, min(n, k + 27), height=5, start=(-3, 6, 0))
    milo.set_face("excited", 1)
    ivy = mk_ivy(); ivy.place((3.5, 12, 0), -0.3); ivy.float_(1, n, base_z=3.5, spin=0.3); ivy.set_face("happy", 1)
    k1 = mk_kid(0); k1.place((-1, 0, 0), 0.2); k1.dance(1, n, 0); k1.set_face("excited", 1)
    k2 = mk_kid(1); k2.place((2.5, 2, 0), -0.4); k2.dance(1, n, 2); k2.set_face("laugh", 1)
    gran = mk_gran(); gran.place((-6.5, 16, 0)); gran.walk(1, n, (-6.5, 30, 0), (-6.5, -10, 0), run=True)
    cam_path(n, (2, -40, 22), (0, 8, 2), (1, -20, 5), (0, 6, 4), 32, 30)
def s02(n):
    show()
    milo = mk_milo(); milo.place((-2, 0, 0), 0.25); milo.set_face("determined", 1)
    j0 = int(n * 0.12); j1 = int(n * 0.72)
    milo.idle(1, j0, 1.5, base_face="determined", blink=False)
    milo.jump(j0, j1, height=12, start=(-2, 0, 0), end=(-2, 0, 0))
    milo.set_face("excited", j0 + 4)
    milo.dance(j1 + 1, n, 1); milo.set_face("laugh", j1 + 1)
    cam_path(n, (3, -14, 1.2), (-2, 0, 5), (4, -18, 2.5), (-2, 0, 9), 26, 24)
def s03(n):
    show()
    ivy = mk_ivy(); ivy.place((-6.5, 22, 0), 0.6)
    ivy.float_(1, n, base_z=0.5, spin=0.0)
    for f in range(1, n + 1):  # rise
        u = f / n; ivy.root.location.z = 0.5 + 5.5 * (u * u * (3 - 2 * u)) + 0.4 * math.sin(f / 24 * 2.4); ivy.root.keyframe_insert("location", frame=f)
    ivy.set_face("happy", 1); ivy.set_face("blink", int(n * 0.5)); ivy.set_face("happy", int(n * 0.5) + 3)
    cam_path(n, (0, 10, 2.5), (-6.5, 22, 4), (1, 9, 2), (-6.5, 22, 8), 30, 32)
def s04(n):
    show()
    gran = mk_gran(); gran.set_face("excited", 1)
    a = int(n * 0.35)
    gran.walk(1, a, (-9, -6, 0), (9, -6, 0), run=True, bounce=1.4)
    gran.walk(a + 1, int(n * 0.55), (9, -6, 0), (0.5, -6, 0), run=True, bounce=1.4)
    b = int(n * 0.55)
    gran.move(b + 1, (0.5, -6, 0), 0.0)
    for f in range(b + 1, n + 1):
        t = (f - b) / 24
        gran.pose(f, arms=(0.2, 2.6), arms_side=(0.1, 0.3), hips_z=2.0 + 0.05 * math.sin(t * 6), head=(-0.1, 0.15, 0.1))
    gran.set_face("smug", b + 1)
    cam_path(n, (0, -22, 3), (0, -6, 3.5), (0, -19, 3.2), (0, -6, 3.8), 26, 30)
def s05(n):
    show(False, True)
    z = mk_zara(hat=True); z.set_face("excited", 1)
    for k in range(0, n, 16): z.jump(k + 1, min(n, k + 15), height=1.3, start=R(-3.5, 3.0, 2.2))
    for i, b in enumerate(BALLOONS):
        base = b.location.copy()
        for f in range(1, n + 1, 3):
            b.location = base + Vector((0, 0, 0.35 * math.sin(f / 10 + i))); b.keyframe_insert("location", frame=f)
    cam_path(n, R(1.5, -10, 6.5), R(-3.5, 3, 6.4), R(0.5, -8, 6.6), R(-3.5, 3, 6.6), 26, 30)
def s06(n):
    show()
    z = mk_zara(); z.set_face("excited", 1)
    z.walk(1, n, (6.5, 10, 0.2), (6.5, -12, 0.2), run=True)
    cam_path(n, (5.0, -8, 3.2), (6.5, 8, 3.5), (5.0, -22, 3.8), (6.5, -8, 3.5), 28, 30)
def s07(n):
    show()
    z = mk_zara(); z.place((3, -14, 0), 0.0); z.set_face("determined", 1)
    a = int(n * 0.3)
    z.idle(1, a, 1.2, base_face="determined", blink=False)
    z.jump(a, int(n * 0.65), height=0.7, start=(3, -14, 0), cheer=False)
    z.idle(int(n * 0.65) + 1, n, 0.6, base_face="shocked", blink=False); z.set_face("shocked", int(n * 0.66))
    for f in range(int(n * 0.66), n + 1):
        z.pose(f, head=(0.45, 0, 0), arms=(0.2, 0.2), arms_side=(0.4, 0.4))
    cam_path(n, (3.5, -21, 1.6), (3, -14, 3.2), (3.4, -20, 1.8), (3, -14, 3.6), 30, 32)
def s08(n):
    show()
    z = mk_zara(); z.place((3, -14, 0), 0.2); z.set_face("determined", 1)
    for f in range(1, n + 1):
        t = f / 24; s = math.sin(t * 2 * math.pi * 4)
        z.pose(f, arms=(0.1, 0.1), arms_side=(1.4 + 0.6 * s, 1.4 + 0.6 * s), legs=(0, 0), hips_z=2.15 + 0.1 * abs(s), head=(-0.25, 0, 0.05 * s))
    cam_path(n, (1.5, -21, 3.5), (3, -14, 4), (1.8, -19, 3.6), (3, -14, 4.2), 30, 34)
def s09(n):
    show()
    z = mk_zara(); z.place((3, -14, 0), 0.15); z.set_face("sad", 1)
    for f in range(1, n + 1):
        u = f / n
        z.pose(f, arms=(0, 0), arms_side=(0.02, 0.02), head=(0.35 * u, 0, 0.05), hips_z=2.0 - 0.15 * u, lean=0.1 * u)
    cam_path(n, (3.6, -19.5, 4.6), (3, -14, 4.3), (3.5, -17.8, 4.4), (3, -14, 4.0), 40, 48)
def s10(n):
    show()
    m = mk_milo(); m.place((-1, -8, 0), 0.15); m.laugh(1, n)
    k1 = mk_kid(0); k1.place((-4, -6.5, 0), -0.4); k1.laugh(1, n, point=False)
    k2 = mk_kid(2); k2.place((2, -6.0, 0), 0.45); k2.laugh(1, n)
    cam_path(n, (-1, -20, 3.5), (-1, -7, 3.5), (-1, -17, 3.3), (-1, -7, 3.8), 28, 32)
def s11(n):
    show()
    m = mk_milo(); m.place((-1, -8, 0), math.pi * 0 + 0.15)
    a = int(n * 0.45)
    m.laugh(1, a); m.idle(a + 1, n, 1.4, base_face="smug", talk=True); m.set_face("smug", a + 1)
    cam_path(n, (-0.6, -14.5, 4.6), (-1, -8, 4.3), (-0.8, -13, 4.5), (-1, -8, 4.4), 38, 44)
def s12(n):
    show()
    z = mk_zara(); z.set_face("sad", 1)
    z.walk(1, n, (6.5, -6, 0.2), (6.5, 6, 0.2), run=False, bounce=0.4)
    for f in range(1, n + 1):
        z.neck.rotation_euler = (0.4, 0, 0); z.neck.keyframe_insert("rotation_euler", frame=f)
    cam_path(n, (-1.5, -9, 3.0), (6.5, -4, 3.2), (-1.5, 5, 3.0), (6.5, 7, 3.2), 30, 30)
def s13(n):
    show()
    dog, tail, ears = make_dog(TEMP); dog.location = (0, -2, 0.1); dog.rotation_euler = (0, 0, -0.6)
    wag(tail, ears, 1, n, perky=False)
    z = mk_zara(); z.place((6.5, -12, 0.2), -1.04); z.set_face("shocked", int(n * 0.35))
    z.idle(1, n, 0.6, base_face="sad", blink=False)
    for f in range(int(n * 0.35), n + 1):
        z.pose(f, arms=(0.5, 0.5), arms_side=(0.3, 0.3), head=(-0.1, 0, 0), hips_z=2.0)
    cam_path(n, (-6, -22, 4.5), (2.5, -6, 2), (-5, -19, 4.2), (2.5, -6, 2.2), 28, 32)
def s14(n):
    show()
    dog, tail, ears = make_dog(TEMP); dog.location = (0, -2, 0.1); dog.rotation_euler = (0, 0, math.pi)
    wag(tail, ears, 1, n, speed=10, perky=False)
    tr = mk_truck(TEMP)
    for f in range(1, n + 1):
        u = f / n; tr.location = (0.5, 66 - 44 * u, 0.1); tr.rotation_euler = (0, 0, 0); tr.keyframe_insert("location", frame=f); tr.keyframe_insert("rotation_euler", frame=f)
    cam_path(n, (1.5, -9, 1.2), (0, 20, 2.5), (1.2, -8, 1.0), (0, 20, 3), 26, 30)
FREEZE_TRUCK_Y = 4.5
def s15(n):
    show()
    z = mk_zara(); z.place((5.0, -6, 0.2), -0.9)
    a = int(n * 0.2)
    z.idle(1, a, 1.5, base_face="scared", blink=False); z.set_face("scared", 1)
    z.set_face("shocked", a)
    for f in range(a, n + 1):
        t = (f - a) / 24; s = math.sin(t * 40) * max(0, 0.3 - t) * 0.5
        z.pose(f, arms=(1.55, 0.2), arms_side=(0.0, 0.3), lean=-0.15, head=(-0.15 + s, 0, 0), legs=(0.4, -0.3), hips_z=1.85)
    # face camera-ish close-up
    cam_path(n, (-1.2, -11.5, 4.4), (5, -6, 4.2), (-0.2, -10.5, 4.3), (5, -6, 4.3), 34, 46)
def freeze_scene(zpose=True):
    dog, tail, ears = make_dog(TEMP); dog.location = (0, -2, 0.1); dog.rotation_euler = (0, 0, math.pi)
    tail.rotation_euler = (0, 0, 0.5); ears[0].rotation_euler = (0.6, -0.9, 0); ears[1].rotation_euler = (0.6, 0.9, 0)
    tr = mk_truck(TEMP); tr.location = (0.5, 7.2, 0.1); tr.rotation_euler = (0, 0, 0)
    birds = mk_birds(TEMP, 9, center=(0, 6, 15))
    clouds = mk_clouds(TEMP, y0=40)
    z = mk_zara(); z.place((5.0, -6, 0.2), -0.9); z.set_face("shocked", 1)
    z.pose(1, arms=(1.55, 0.2), arms_side=(0.0, 0.3), lean=-0.15, head=(-0.15, 0, 0), legs=(0.4, -0.3), hips_z=1.85)
    return dog, tr, birds, z
def s16(n):
    show(); freeze_scene()
    for f in range(1, n + 1):
        u = f / n; ang = -0.9 + 1.6 * (u * u * (3 - 2 * u)); r = 16
        cam(f, (r * math.sin(ang), -2 - r * math.cos(ang), 2.2 + 1.2 * u), (0.5, 1, 2.8), 26)
def s17(n):
    show(); freeze_scene()
    cam_path(n, (2.5, -3, 2.2), (0.5, 6, 2.8), (3, -14, 3), (0, 20, 42), 30, 26)
def s18(n):
    show()
    z = mk_zara(); z.place((5.0, -6, 0.2), -0.4)
    a = int(n * 0.45)
    for f in range(1, a):
        z.pose(f, arms=(1.2, 1.2), arms_side=(-0.25, -0.25), head=(0.5, 0, 0), hips_z=2.0)
    z.set_face("shocked", 1); z.set_face("excited", a)
    z.dance(a, n, 1, speed=1.2)
    cam_path(n, (2.5, -11.5, 4.0), (5, -6, 4.0), (2.2, -13, 4.5), (5, -6, 4.6), 34, 30)
def s19(n):
    show()
    z = mk_zara(); z.place((5.5, -7, 0.2), 0.3); z.set_face("happy", 1)
    dog, tail, ears = make_dog(TEMP); dog.parent = z.hips; dog.location = (0, -1.1, 0.2); dog.rotation_euler = (0, 0, 0.2); dog.scale = (0.9,) * 3
    wag(tail, ears, 1, n, speed=12)
    for f in range(1, n + 1):
        t = f / 24
        z.pose(f, arms=(1.3, 1.3), arms_side=(-0.35, -0.35), head=(0.1 + 0.05 * math.sin(t * 3), 0, 0.15 * math.sin(t * 2)), hips_z=2.0 + 0.05 * math.sin(t * 5), twist=0.2 * math.sin(t * 2.5))
    z.set_face("blink", int(n * 0.5)); z.set_face("laugh", int(n * 0.5) + 3)
    tr = mk_truck(TEMP); s = int(n * 0.55)
    for f in range(1, n + 1):
        y = 7.2 if f < s else 7.2 - (f - s) * 2.2
        tr.location = (0.5, y, 0.1); tr.rotation_euler = (0, 0, 0); tr.keyframe_insert("location", frame=f); tr.keyframe_insert("rotation_euler", frame=f)
    cam_path(n, (7.5, -15, 3.6), (5.5, -7, 3.5), (7.0, -13, 3.6), (5.0, -7, 3.6), 34, 38)
def s20(n):
    show()
    cast = [(mk_milo(), (-3, -14)), (mk_ivy(), (0, -15)), (mk_gran(), (3, -14.5)), (mk_kid(0), (-5.5, -12)), (mk_kid(1), (5.5, -12.5))]
    for i, (c, (x, y)) in enumerate(cast):
        c.place((x, y, 0), math.pi + 0.1 * (i - 2)); c.set_face("shocked", 1)
        c.idle(1, n, 0.4, base_face="shocked", blink=False, seed=i)
        for f in range(1, n + 1): c.arms[0].rotation_euler = (-0.3, 0.2, 0); c.arms[0].keyframe_insert("rotation_euler", frame=f)
    cam_path(n, (0, -2, 4), (0, -14, 4), (0, -6, 4.2), (0, -14, 4.3), 26, 32)
def s21(n):
    show()
    g = mk_gran(); g.place((3, -14.5, 0), math.pi * 0 + 0.1)
    a = int(n * 0.4)
    g.idle(1, n, 0.7, base_face="shocked", talk=True, blink=False); g.set_face("shocked", 1); g.set_face("determined", a)
    cam_path(n, (2.8, -20.5, 4.6), (3, -14.5, 4.4), (2.9, -19.2, 4.5), (3, -14.5, 4.5), 40, 48)
def s22(n):
    show()
    z = mk_zara(); z.place((5.5, -7, 0.2), 0.0)
    z.idle(1, n, 0.4, base_face="scared", blink=True); z.set_face("scared", 1)
    cam_path(n, (5.4, -12.8, 4.3), (5.5, -7, 4.2), (5.45, -11.3, 4.3), (5.5, -7, 4.25), 40, 55)

SHOTS = {k: v for k, v in globals().items() if k.startswith("s") and k[1:].isdigit() and len(k) == 3}
os.makedirs(OUT, exist_ok=True)
for name in sorted(SHOTS):
    if ONLY and name not in ONLY: continue
    n = max(12, int(round(DUR[name] * FPS)))
    clear_temp()
    SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    if STILL:
        S.frame_set(n // 2); S.render.filepath = f"{OUT}/preview_{name}.png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
