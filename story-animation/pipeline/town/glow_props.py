"""Glow episode props (exec'd after glow_sets.py)."""
# ---------------------------------------------------------------- Main Street props
def lamppost(p, coll, h=9.0, skinny=False):
    r = 0.12 if skinny else 0.18
    cyl("lpost", p + Vector((0, 0, h / 2)), r, h, METAL, coll=coll, verts=10)
    cyl("lbase", p + Vector((0, 0, 0.3)), r * 2.2, 0.6, METAL, coll=coll, verts=10)
    box("larm", p + Vector((-1.0, 0, h)), (2.2, 0.2, 0.2), METAL, coll=coll)
    box("lhead", p + Vector((-2.0, 0, h - 0.25)), (0.9, 0.7, 0.4), METAL, coll=coll, bevel=0.08)
    sphere("lsocket", p + Vector((-2.0, 0, h - 0.5)), 0.14, mat("socket", (0.06, 0.06, 0.07), 0.3), coll=coll, seg=8)   # no bulb
    box("lsnow", p + Vector((-1.4, 0, h + 0.2)), (2.4, 0.4, 0.2), SNOW, coll=coll, bevel=0.08)
LAMP_STEVE = Vector((8.9, 4.6, 0.2)); LAMP_TY = Vector((7.4, 14.0, 0.2))
for y in (-34, -14, 26, 46): lamppost(Vector((8.9, y, 0.2)), MAIN)
for y in (-24, -4, 16, 36): lamppost(Vector((-8.9, y, 0.2)), MAIN)
lamppost(LAMP_STEVE, MAIN)
TRASH = Vector((-8.4, -2.0, 0.2))
def trashcan():
    cyl("trash", TRASH + Vector((0, 0, 1.6)), 1.1, 3.2, mat("trashm", (0.16, 0.3, 0.2), 0.5), coll=TEMP, verts=18)
    cyl("trashlid", TRASH + Vector((0, 0, 3.3)), 1.2, 0.2, mat("trashlidm", (0.12, 0.24, 0.16), 0.5), coll=TEMP, verts=18)
    cyl("trashsnow", TRASH + Vector((0, 0, 3.47)), 1.15, 0.14, SNOW, coll=TEMP, verts=18)
def ground_z(x):
    ax = abs(x); return 0.2 if 6.4 <= ax <= 10.4 else (0.03 if ax < 6.0 else 0.0)

# ---------------------------------------------------------------- shop interior mini-set (x=-200,y=200): window, XMAS LIGHTS box, cobwebs, spider, sleepy shopkeeper
SHOPI = collection("shopi"); SI = Vector((-200, 200, 0))
box("sifloor", SI + Vector((0, 4, -0.1)), (20, 14, 0.2), mat("sifl", (0.25, 0.15, 0.08), 0.6), coll=SHOPI)
box("siback", SI + Vector((0, 10, 6)), (20, 0.3, 12), mat("siwall", (0.45, 0.3, 0.22), 0.8), coll=SHOPI)
for sx in (-1, 1): box("siside", SI + Vector((sx * 9, 4, 6)), (0.3, 14, 12), mat("siwall", (0.45, 0.3, 0.22), 0.8), coll=SHOPI)
box("sitop", SI + Vector((0, 4, 12)), (20, 14, 0.3), mat("siwall", (0.45, 0.3, 0.22), 0.8), coll=SHOPI)
# window frame (front wall with a big opening)
FRM = mat("frame", (0.5, 0.08, 0.08), 0.5)
box("wfbot", SI + Vector((0, -3, 1.2)), (20, 0.4, 2.4), BRICK[0], coll=SHOPI)
box("wftop", SI + Vector((0, -3, 10.5)), (20, 0.4, 3.0), BRICK[0], coll=SHOPI)
for sx in (-1, 1): box("wfside", SI + Vector((sx * 7.5, -3, 6)), (5, 0.4, 12), BRICK[0], coll=SHOPI)
box("wsill2", SI + Vector((0, -3.3, 2.45)), (10.4, 0.9, 0.2), FRM, coll=SHOPI)
for z in (2.5, 9.0): box("wbar", SI + Vector((0, -3.1, z)), (10, 0.25, 0.25), FRM, coll=SHOPI)
for x in (-5, 5): box("wbarv", SI + Vector((x, -3.1, 5.75)), (0.25, 0.25, 6.75), FRM, coll=SHOPI)
box("wsnow", SI + Vector((0, -3.5, 2.62)), (10.2, 0.7, 0.15), SNOW, coll=SHOPI, bevel=0.05)
# display table + box
box("dtable", SI + Vector((0, -1.0, 2.5)), (6, 3, 0.2), mat("dtab", (0.3, 0.17, 0.08), 0.6), coll=SHOPI)
for x in (-2.6, 2.6):
    for y in (-2.2, 0.2): box("dleg", SI + Vector((x, y, 1.2)), (0.2, 0.2, 2.4), mat("dtab", (0.3, 0.17, 0.08), 0.6), coll=SHOPI)
XBOX = SI + Vector((0, -1.0, 2.6))
box("xbox", XBOX + Vector((0, 0, 1.0)), (3.4, 2.0, 2.0), mat("xboxm", (0.75, 0.62, 0.42), 0.8), coll=SHOPI, bevel=0.04)
text3d("XMAS", XBOX + Vector((0, -1.02, 1.45)), 0.62, mat("xtxt", (0.75, 0.05, 0.05), 0.5), coll=SHOPI)
text3d("LIGHTS", XBOX + Vector((0, -1.02, 0.75)), 0.55, mat("xtxt2", (0.05, 0.4, 0.1), 0.5), coll=SHOPI)
box("pricetag", XBOX + Vector((1.25, -1.03, 1.75)), (0.6, 0.02, 0.35), mat("white", (1, 1, 1)), coll=SHOPI)
text3d("$0", XBOX + Vector((1.25, -1.06, 1.75)), 0.22, mat("f_black", (0.02, 0.02, 0.03), 0.2), coll=SHOPI)
# cobwebs: thin pale strands fanning over the box corners
WEB = emat("web", (0.85, 0.88, 0.95), 0.35, base=(0.8, 0.82, 0.88))
for k in range(14):
    a = k / 13 * math.pi / 2; r_ = 1.6
    for corner, sgn in (((-1.7, -1.04, 2.0), -1), ((1.7, -1.04, 2.0), 1)):
        rod("webfan", XBOX + Vector(corner), XBOX + Vector(corner) + Vector((sgn * math.cos(a) * r_, 0, math.sin(a) * r_)), 0.012, WEB, coll=SHOPI)
    for ring in (0.5, 1.0, 1.5):
        b0 = Vector((-math.cos(a) * ring, 0, math.sin(a) * ring)); a2 = (k + 1) / 13 * math.pi / 2
        b1 = Vector((-math.cos(a2) * ring, 0, math.sin(a2) * ring))
        if k < 13:
            for corner, sgn in (((-1.7, -1.04, 2.0), 1), ((1.7, -1.04, 2.0), -1)):
                bb0 = Vector((b0.x * sgn, 0, b0.z)); bb1 = Vector((b1.x * sgn, 0, b1.z))
                rod("webring", XBOX + Vector(corner) + bb0, XBOX + Vector(corner) + bb1, 0.009, WEB, coll=SHOPI)
SPIDER = empty("spider", XBOX + Vector((-2.6, -1.05, 3.1)), coll=SHOPI)
sphere("spbody", (0, 0, 0), 0.22, mat("f_black", (0.02, 0.02, 0.03), 0.2), coll=SHOPI, parent=SPIDER)
for sx in (-1, 1):
    sphere("speye", (sx * 0.08, -0.2, 0.06), 0.05, mat("white", (1, 1, 1)), coll=SHOPI, parent=SPIDER)
    for k in range(4):
        rod("spleg", SPIDER.location + Vector((sx * 0.15, 0, 0)), SPIDER.location + Vector((sx * 0.5, 0, -0.3 + k * 0.15)), 0.025, mat("f_black", (0.02, 0.02, 0.03), 0.2), coll=SHOPI)
SPIDER_ARM = empty("sparm", (0.15, 0, 0.05), parent=SPIDER, coll=SHOPI)
box("spwave", (0.25, 0, 0.2), (0.05, 0.05, 0.5), mat("f_black", (0.02, 0.02, 0.03), 0.2), parent=SPIDER_ARM, coll=SHOPI)
box("counter", SI + Vector((0, 5.0, 1.6)), (8, 2, 3.2), mat("counterm", (0.35, 0.2, 0.1), 0.6), coll=SHOPI)
SHOPI_LIGHTS = [light("silamp", "POINT", SI + Vector((0, 2, 9)), 900, (1.0, 0.7, 0.4), coll=SHOPI, radius=1.5),
                light("sifront", "AREA", SI + Vector((0, -9, 6)), 600, (0.5, 0.6, 1.0), size=8, rot=(math.radians(80), 0, 0), coll=SHOPI)]

# ---------------------------------------------------------------- square props: stage, banner, mailbox, moon
STAGE = Q + Vector((-17, -21, 0))
box("stage", STAGE + Vector((0, 0, 0.8)), (8, 5, 1.6), mat("stagem", (0.35, 0.08, 0.08), 0.6), coll=SQ, bevel=0.05)
box("stagetop", STAGE + Vector((0, 0, 1.62)), (8.1, 5.1, 0.06), mat("stagetopm", (0.3, 0.17, 0.09), 0.6), coll=SQ)
box("stagesnow", STAGE + Vector((0, 1.8, 1.7)), (7.6, 1.2, 0.1), SNOW, coll=SQ)
for k in range(3): box("step", STAGE + Vector((0, -2.9 - k * 0.5, 0.25 + 0.5 * (2 - k) * 0.5)), (3, 0.5, 0.5 + 0.5 * (2 - k)), mat("stagem", (0.35, 0.08, 0.08), 0.6), coll=SQ)
STAGE_TOP = 1.65
for sx in (-3.7, 3.7): cyl("bpole", STAGE + Vector((sx, 2.2, 5)), 0.15, 10, METAL, coll=SQ, verts=8)
box("banner", STAGE + Vector((0, 2.25, 8.2)), (7.4, 0.08, 2.2), mat("bannerm", (0.75, 0.06, 0.08), 0.6), coll=SQ)
text3d("TREE LIGHTING", STAGE + Vector((0, 2.18, 8.65)), 0.75, emat("bantxt", (1, 0.9, 0.6), 1.5), coll=SQ)
text3d("TONIGHT!", STAGE + Vector((0, 2.18, 7.75)), 0.8, emat("bantxt2", (1, 0.85, 0.2), 2.5), coll=SQ)
MAILBOX = Q + Vector((13, -22, 0))
box("mbox", MAILBOX + Vector((0, 0, 2.0)), (2.2, 1.8, 2.6), mat("mboxm", (0.1, 0.2, 0.55), 0.4), coll=SQ, bevel=0.2)
cyl("mboxtop", MAILBOX + Vector((0, 0, 3.3)), 1.1, 1.8, mat("mboxm", (0.1, 0.2, 0.55), 0.4), rot=(math.pi / 2, 0, 0), coll=SQ, verts=20)
for sx in (-0.7, 0.7): box("mleg", MAILBOX + Vector((sx, 0, 0.35)), (0.3, 1.4, 0.7), mat("mboxm", (0.1, 0.2, 0.55), 0.4), coll=SQ)
text3d("MAIL", MAILBOX + Vector((0, -0.92, 2.2)), 0.45, mat("white", (1, 1, 1)), coll=SQ)
MOON = Q + Vector((-30, 220, 95))
cyl("moon", MOON, 22, 0.5, emat("moonm", (1.0, 0.95, 0.8), 2.2), rot=(math.pi / 2, 0, 0), coll=SQ, verts=48)

# ---------------------------------------------------------------- character extras
SILVER = mat("silver", (0.85, 0.87, 0.9), 0.2)
def note(c, text, col=(1.0, 0.92, 0.25), loc=(0, -0.64, 1.2), name="note"):
    """sticky note on the chest (parented to hips, just in front of the torso)"""
    o = box(name, loc, (1.5, 0.04, 1.05), emat(f"notem{col}", col, 0.35), parent=c.hips, coll=c.coll)
    t = text3d(text.replace(" ", "\n"), (0, -1.6, 0), 0.36, mat("f_black", (0.02, 0.02, 0.03), 0.2), coll=c.coll, parent=o)
    t.rotation_euler = (math.pi / 2, 0, 0); t.scale = (1 / 1.5, 1 / 1.05, 1 / 0.04)
    return o, t
def vis(objs, f, on):
    for o in (objs if isinstance(objs, (list, tuple)) else [objs]):
        o.hide_render = not on; o.keyframe_insert("hide_render", frame=f)
        for ch in o.children_recursive: ch.hide_render = not on; ch.keyframe_insert("hide_render", frame=f)
def coat(c, col=(0.12, 0.13, 0.16)):
    """puffy winter coat over torso + sleeves (dims the glow). Returns the coat parts."""
    m = mat(f"coat{col}", col, 0.7); parts = []
    parts.append(box("coat", (0, 0, 1.0), (2.2, 1.18, 2.15), m, parent=c.hips, coll=c.coll, bevel=0.3))
    parts.append(box("coathood", (0, 0.8, 2.05), (1.6, 0.5, 0.7), m, parent=c.hips, coll=c.coll, bevel=0.2))
    for a in c.arms: parts.append(box("coatsleeve", (0, 0, -0.75), (1.12, 1.12, 1.6), m, parent=a, coll=c.coll, bevel=0.25))
    c.coat = parts; return parts
def coffee(c):
    cup = cyl("coffee", (0, -0.82, -1.75), 0.32, 0.7, mat("cupm", (0.95, 0.95, 0.92), 0.5), parent=c.arms[1], coll=c.coll, verts=14)
    cyl("cuplid", (0, -0.82, -1.36), 0.34, 0.1, mat("lidm", (0.2, 0.1, 0.06), 0.5), parent=c.arms[1], coll=c.coll, verts=14)
    cyl("cupsleeve", (0, -0.82, -1.8), 0.335, 0.3, mat("sleevem", (0.6, 0.35, 0.15), 0.8), parent=c.arms[1], coll=c.coll, verts=14)
    return cup
def megaphone(c):
    m = mat("megam", (0.95, 0.85, 0.2), 0.4)
    cone("mega", (0, 0, -2.6), 0.55, 1.4, m, verts=14, parent=c.arms[0], coll=c.coll)
    return m
def backpack(c):
    bp = box("backpack", (0, 0.82, 1.05), (1.6, 0.6, 1.6), mat("bpm", (0.15, 0.45, 0.8), 0.6), parent=c.hips, coll=c.coll, bevel=0.15)
    pap = box("hw", (0.3, 0.82, 2.05), (0.8, 0.05, 0.9), mat("white", (1, 1, 1)), parent=c.hips, coll=c.coll)
    t = text3d("MATH", (0, -1.2, 0.2 / 0.9), 0.22, mat("hwred", (0.8, 0.05, 0.05), 0.5), coll=c.coll, parent=pap); t.rotation_euler = (math.pi / 2, 0, 0); t.scale = (1 / 0.8, 1 / 0.9, 1 / 0.05)
    return bp, pap
_BOX_TEX = None
def boxers_mat():
    m = bpy.data.materials.get("boxers")
    if m: return m
    m = bpy.data.materials.new("boxers"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "DIAGONAL"
    wv.inputs["Scale"].default_value = 1.4; wv.inputs["Distortion"].default_value = 0
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (0.95, 0.95, 0.95, 1); ramp.color_ramp.elements[1].position = 0.5; ramp.color_ramp.elements[1].color = (0.85, 0.04, 0.06, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"]); nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.6; m.diffuse_color = (0.9, 0.3, 0.3, 1); return m
def boxers(c):
    """candy-cane boxers (upper legs) + bare lower legs, hidden until the moth eats the pants"""
    out = []; sk = mat("legskin", (0.9, 0.72, 0.58), 0.5)
    for l in c.legs:
        out.append(box("boxer", (0, 0, -0.55), (1.02, 1.02, 1.1), boxers_mat(), parent=l, coll=c.coll, bevel=0.2))
        out.append(box("shin", (0, 0, -1.35), (0.9, 0.9, 0.8), sk, parent=l, coll=c.coll, bevel=0.15))
    pants = [ch for l in c.legs for ch in l.children if ch.name.startswith("leg")]
    return out, pants
def dark_cat(scale=1.0):
    cat = Cat(TEMP, scale)
    dk = mat("catdark", (0.03, 0.03, 0.035), 0.8); dk2 = mat("catdark2", (0.06, 0.06, 0.07), 0.8)
    eye = emat("cateyeglow", (1, 1, 0.95), 2.5)
    for o in cat.root.children_recursive:
        if o.type != "MESH": continue
        nm = o.name.split(".")[0]
        if nm in ("ceye",): o.data = o.data.copy(); o.data.materials[0] = eye; o.scale = (o.scale[0] * 1.3, o.scale[1], o.scale[2] * 1.3)
        elif nm in ("cpup", "cgl", "bell", "collar", "whisk", "cnose"): continue
        else: o.data = o.data.copy(); o.data.materials[0] = dk if nm not in ("cmuz", "cchest", "cpaw") else dk2
    return cat
def glow_objs(root, col, strength=1.4):
    for o in root.children_recursive:
        if o.type == "MESH":
            o.data = o.data.copy()
            for i, m in enumerate(o.data.materials):
                if m: o.data.materials[i] = _glowmat(m, col, strength)
def eyes_glow(c, strength=3.0):
    """Rico in the dark: only the whites of his eyes (and teeth) glow"""
    for kind, objs in c.faces.items():
        for o in objs:
            m = o.data.materials[0]; key = ("eyes", m.name)
            if key not in _gcache:
                g = m.copy(); nt = g.node_tree; b = nt.nodes["Principled BSDF"]
                tex = [n for n in nt.nodes if n.bl_idname == "ShaderNodeTexImage"][0]
                ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.8; ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
                ramp.color_ramp.elements[1].position = 0.9; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
                nt.links.new(tex.outputs["Color"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
                b.inputs["Emission Strength"].default_value = strength; _gcache[key] = g
            o.data = o.data.copy(); o.data.materials[0] = _gcache[key]
def heart_eyes(m):
    """swap-in heart eyes for a moth (hidden until used)"""
    hm = emat("heartm", (1, 0.1, 0.25), 3.0); out = []
    for sx in (-1, 1):
        h = empty("heart", (sx * 0.32, -0.38, 0.1), m.head, m.root.users_collection[0]); h.rotation_euler = (math.pi / 2, 0, 0)
        for dx in (-0.09, 0.09): sphere("hlobe", (dx, 0.06, 0), 0.12, hm, coll=m.root.users_collection[0], parent=h)
        box("htip", (0, -0.06, 0), (0.18, 0.18, 0.08), hm, rot=(0, 0, 0.785), parent=h, coll=m.root.users_collection[0])
        out.append(h)
    eyes = [o for o in m.head.children if o.name.startswith("meye")]
    return out, eyes
