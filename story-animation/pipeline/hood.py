"""American block: rowhouses, deli, court + mural, school bus, hydrants, power lines, skyline. Run inside world exec (HOOD=1)."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HOODC = collection("hood")
rnd = random.Random(21)
BRICK = [(0.55, 0.17, 0.1), (0.42, 0.2, 0.13), (0.62, 0.3, 0.18), (0.82, 0.76, 0.6), (0.5, 0.72, 0.62), (0.55, 0.68, 0.85), (0.75, 0.42, 0.3)]
blk = mat("iron", (0.05, 0.05, 0.06), 0.4); white = mat("trimw", (0.95, 0.95, 0.93)); glass = mat("hglass", (0.25, 0.42, 0.6), 0.1)
stone = mat("stoop", (0.62, 0.6, 0.56))
HOOD_ROOFS = []

def tex_mat(name, path):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); nt.links.new(t.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes.active = t
    return m
def tex_plane(name, loc, w, h, m, rot=(0, 0, 0), coll=None):
    me = bpy.data.meshes.new(name); me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    me.materials.append(m); o = bpy.data.objects.new(name, me); (coll or HOODC).objects.link(o); o.location = loc; o.rotation_euler = rot; return o

def rowhouse(x, y, side, w, h, col, fire=False, tower=False):
    """side=-1 left of street (front faces +x), +1 right (front faces -x)."""
    face = -side; D = 12
    cx = x + side * D / 2
    wm = mat(f"brick{col}", col, 0.85)
    box("rh", (cx, y, h / 2), (D, w, h), wm, coll=HOODC)
    fx = x - side * 0.02
    box("cornice", (x - side * 0.25, y, h + 0.35), (0.7, w + 0.05, 0.7), white if rnd.random() < 0.6 else blk, coll=HOODC)
    box("roofcap", (cx, y, h + 0.1), (D, w, 0.2), mat("tar", (0.2, 0.2, 0.22)), coll=HOODC)
    floors = int(h // 3.6)
    for fl in range(floors):
        z = 2.6 + fl * 3.6 if fl > 0 else None
        for k, yy in enumerate((y - w * 0.24, y + w * 0.24)):
            if fl == 0 and k == 0: continue
            zz = 2.0 + fl * 3.6
            box("wf", (fx, yy, zz), (0.2, 1.7, 2.6), white, coll=HOODC)
            box("wg", (fx - side * 0.05, yy, zz), (0.2, 1.35, 2.25), glass, coll=HOODC)
            box("wbar", (fx - side * 0.12, yy, zz + 0.2), (0.1, 1.35, 0.12), white, coll=HOODC)
            box("lintel", (fx - side * 0.1, yy, zz + 1.45), (0.35, 1.9, 0.3), stone, coll=HOODC)
    # door + stoop + rails
    dy = y - w * 0.24
    box("door", (fx, dy, 2.3), (0.25, 1.4, 2.6), mat(f"door{rnd.randint(0,3)}", rnd.choice([(0.1, 0.1, 0.12), (0.45, 0.12, 0.1), (0.1, 0.3, 0.2), (0.15, 0.25, 0.5)])), coll=HOODC)
    box("doorframe", (fx + side * 0.03, dy, 2.4), (0.2, 1.8, 3.0), white, coll=HOODC)
    for s in range(4):
        box("stoop", (x - side * (0.5 + s * 0.45), dy, 0.25 + (3 - s) * 0.25), (0.9 + s * 0.0, 1.8, 0.5 + (3 - s) * 0.5), stone, coll=HOODC)
    for sy in (-1, 1):
        rod("rail", (x - side * 2.2, dy + sy * 0.95, 1.0), (x - side * 0.1, dy + sy * 0.95, 2.4), 0.05, blk, coll=HOODC)
    if fire and floors >= 3:
        for fl in range(1, floors):
            zz = 1.2 + fl * 3.6
            box("fe", (x - side * 0.9, y + w * 0.24, zz), (1.6, 2.6, 0.12), blk, coll=HOODC)
            for k in range(7):
                rod("fer", (x - side * 1.65, y + w * 0.24 - 1.3 + k * 0.43, zz), (x - side * 1.65, y + w * 0.24 - 1.3 + k * 0.43, zz + 1.0), 0.03, blk, coll=HOODC)
            rod("ladder", (x - side * 1.2, y + w * 0.24 - 0.9, zz), (x - side * 1.2, y + w * 0.24 + 0.9, zz + 3.6), 0.05, blk, coll=HOODC)
    if tower:
        tz = h + 0.2
        for sx in (-1, 1):
            for sy in (-1, 1): box("wtleg", (cx + sx * 1.2, y + sy * 1.2, tz + 1.5), (0.15, 0.15, 3), blk, coll=HOODC)
        cyl("wtank", (cx, y, tz + 4.2), 1.8, 3.2, mat("cedar", (0.55, 0.38, 0.25)), coll=HOODC, verts=12)
        cone("wtroof", (cx, y, tz + 6.3), 1.95, 1.2, mat("wtroofc", (0.3, 0.3, 0.32)), verts=12, coll=HOODC)
    if rnd.random() < 0.5:
        box("ac", (cx + rnd.uniform(-3, 3), y + rnd.uniform(-1.5, 1.5), h + 0.6), (1.4, 1.0, 0.8), mat("acgrey", (0.7, 0.7, 0.72)), coll=HOODC)
    HOOD_ROOFS.append((cx, y, h + 0.25, w, D))

# --- court + mural (left side, y -34..-16)
def make_mural(path):
    W, H = 1600, 600
    im = Image.new("RGB", (W, H), (60, 60, 70)); d = ImageDraw.Draw(im)
    for k in range(40):
        x0_, y0_ = rnd.randint(-100, W), rnd.randint(-100, H); r_ = rnd.randint(40, 260)
        d.ellipse([x0_, y0_, x0_ + r_, y0_ + r_], outline=rnd.choice([(255, 90, 160), (60, 200, 255), (255, 210, 40), (120, 255, 120)]), width=6)
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf", 260)
    txt = "THE BLOCK"; bb = d.textbbox((0, 0), txt, font=f)
    x0 = (W - (bb[2] - bb[0])) // 2; y0 = (H - (bb[3] - bb[1])) // 2 - 40
    d.text((x0 + 14, y0 + 14), txt, font=f, fill=(20, 20, 30))
    d.text((x0, y0), txt, font=f, fill=(255, 220, 40), stroke_width=14, stroke_fill=(255, 60, 140))
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf", 70)
    d.text((W - 520, H - 120), "NO NUMBERS!", font=f2, fill=(60, 220, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    im.save(path)
make_mural("/home/claude/zara/facetex/mural.png")
mural_m = tex_mat("mural", "/home/claude/zara/facetex/mural.png")

y = -130
i = 0
while y < 140:
    for side in (-1, 1):
        x = side * 10.0
        if side == -1 and -36 < y < -14: continue       # court gap
        if side == 1 and -10 < y < 2: continue           # deli placed separately
        w = 7.0; h = rnd.choice([10.8, 10.8, 14.4, 14.4])
        rowhouse(x, y + w / 2, side, w, h, rnd.choice(BRICK), fire=rnd.random() < 0.45, tower=rnd.random() < 0.15)
    y += 7.0; i += 1
# deli (right side, y -10..2)
dx = 10.0; dyc = -4
box("deli", (dx + 6, dyc, 6.0), (12, 12, 12), mat("delibrick", (0.35, 0.22, 0.16)), coll=HOODC)
box("delifront", (dx - 0.05, dyc, 2.4), (0.2, 10, 4.2), mat("deliglass", (0.45, 0.7, 0.85), 0.1), coll=HOODC)
box("delidoor", (dx - 0.1, dyc - 3.2, 2.0), (0.2, 1.8, 3.6), mat("delidoorc", (0.2, 0.2, 0.22)), coll=HOODC)
prism("awning", (dx - 1.3, dyc, 4.6), (2.8, 10.6, 1.2), mat("awn", (0.1, 0.55, 0.25)), rot=(0, -math.pi / 2 + 0.25, 0), coll=HOODC)
for k in range(6): box("awnstripe", (dx - 1.25, dyc - 4.5 + k * 1.8, 5.1), (2.6, 0.5, 0.06), white, rot=(0, -0.42, 0), coll=HOODC)
box("delisign", (dx - 0.2, dyc, 7.2), (0.3, 10.5, 2.0), mat("signyellow", (1, 0.82, 0.1)), coll=HOODC)
SIGN_TXT = []
def deli_text(body, z, size, col):
    o = text3d(body, (dx - 0.4, dyc, z), size, mat(f"t{col}", col), rot=(math.pi / 2, 0, -math.pi / 2), coll=HOODC); SIGN_TXT.append(o)
deli_text("DELI & GROCERY", 7.2, 1.0, (0.85, 0.1, 0.1))
deli_text("OPEN 24/7", 3.6, 0.6, (1, 0.2, 0.6))
HOOD_ROOFS.append((dx + 6, dyc, 12.2, 12, 12))
# court
box("court", (-15, -25, 0.05), (14, 20, 0.1), mat("courtblue", (0.2, 0.45, 0.8)), coll=HOODC)
box("key", (-15, -16.5, 0.07), (5, 3, 0.1), mat("courtorange", (0.95, 0.5, 0.15)), coll=HOODC)
box("backboard", (-15, -15.6, 5), (3.2, 0.15, 2.0), white, coll=HOODC)
box("pole", (-15, -14.8, 2.5), (0.25, 0.25, 5), blk, coll=HOODC)
cyl("rim", (-15, -16.3, 4.4), 0.5, 0.06, mat("rimor", (1, 0.4, 0.1)), coll=HOODC, verts=12)
for k in range(11):
    rod("fence", (-8.2, -35 + k * 2, 0), (-8.2, -35 + k * 2, 4.5), 0.05, mat("fencec", (0.6, 0.62, 0.65)), coll=HOODC)
rod("fencetop", (-8.2, -35, 4.5), (-8.2, -15, 4.5), 0.06, mat("fencec", (0.6, 0.62, 0.65)), coll=HOODC)
box("muralwall", (-22.3, -25, 4), (0.6, 20, 8), mat("cinder", (0.5, 0.5, 0.52)), coll=HOODC)
tex_plane("mural", (-21.95, -25, 4), 19.5, 7.5, mural_m, rot=(0, 0, math.pi / 2))
# school bus
bus = empty("bus", (-3.2, 26, 0), coll=HOODC)
yel = mat("busyellow", (1, 0.72, 0.03))
box("busbody", (0, 0, 2.6), (3.2, 13, 3.6), yel, parent=bus, coll=HOODC, bevel=0.25)
box("busstripe", (0, 0, 2.2), (3.25, 13, 0.18), blk, parent=bus, coll=HOODC)
box("bushood", (0, -7.4, 1.8), (3.0, 2.0, 2.0), yel, parent=bus, coll=HOODC, bevel=0.2)
for k in range(7):
    for sx in (-1, 1): box("buswin", (sx * 1.62, -5 + k * 1.6, 3.3), (0.06, 1.2, 1.0), glass, parent=bus, coll=HOODC)
for sy in (-5.5, 4.5):
    for sx in (-1, 1): cyl("buswheel", (sx * 1.5, sy, 0.75), 0.75, 0.5, blk, rot=(0, math.pi / 2, 0), parent=bus, coll=HOODC)
# hydrants, trees, power lines w/ sneakers
for yy in range(-110, 120, 28):
    for sx in (-1, 1):
        hx = sx * 5.3
        cyl("hyd", (hx, yy, 0.6), 0.28, 1.0, mat("hydred", (0.9, 0.1, 0.1)), coll=HOODC, verts=10)
        sphere("hydtop", (hx, yy, 1.15), 0.3, mat("hydred", (0.9, 0.1, 0.1)), coll=HOODC, seg=10)
for yy in range(-120, 130, 18):
    for sx in (-1, 1):
        tx = sx * 6.8
        if abs(yy - (-4)) < 7 and sx > 0: continue
        box("treepit", (tx, yy + 9, 0.21), (1.4, 1.4, 0.02), mat("dirt", (0.3, 0.2, 0.12)), coll=HOODC)
        cyl("stt", (tx, yy + 9, 1.8), 0.18, 3.6, M["bark"], coll=HOODC, verts=6)
        sphere("stl", (tx, yy + 9, 4.4), 1.5, M["leaf"], coll=HOODC, seg=10)
for yy in range(-120, 130, 40):
    for sx in (-1, 1):
        box("upole", (sx * 7.6, yy, 5), (0.35, 0.35, 10), mat("wood", (0.4, 0.28, 0.18)), coll=HOODC)
        box("uarm", (sx * 7.6, yy, 9.4), (2.4, 0.2, 0.2), mat("wood", (0.4, 0.28, 0.18)), coll=HOODC)
    rod("wire", (-7.6, yy, 9.5), (7.6, yy, 9.5), 0.03, blk, coll=HOODC)
    for s in (-0.25, 0.25):
        rod("lace", (s, yy, 9.5), (s, yy, 8.2), 0.015, white, coll=HOODC)
        box("sneaker", (s, yy, 8.0), (0.3, 0.7, 0.3), mat("sneak", (1, 1, 1)), coll=HOODC, bevel=0.08)
        box("sole", (s, yy, 7.83), (0.32, 0.72, 0.08), mat("sole", (0.9, 0.1, 0.15)), coll=HOODC)
# skyline
for k in range(40):
    sgn = rnd.choice((-1, 1)) if k % 3 else 1
    bx = rnd.uniform(-160, 160); by = rnd.uniform(240, 420) * (1 if k % 4 else -1)
    hh = rnd.uniform(50, 160)
    box("tower", (bx, by, hh / 2), (rnd.uniform(14, 30), rnd.uniform(14, 30), hh), mat(f"sky{k%3}", [(0.55, 0.62, 0.72), (0.62, 0.68, 0.78), (0.5, 0.55, 0.66)][k % 3]), coll=HOODC)
