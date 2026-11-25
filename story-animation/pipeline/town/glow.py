"""IN MY TOWN: 'My Whole Town Glows... Except Me'. EEVEE, Roblox-style cast.
usage: EEVEE=1 python glow.py -- all|s01,s05 [still]"""
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
E = "/home/claude/zara/town/glow/ep"; OUT = f"{E}/frames"
S.render.resolution_x, S.render.resolution_y = 576, 1024
try: S.eevee.shadow_resolution_scale = 0.5
except Exception: pass
S.render.film_transparent = False
TL = json.load(open(f"{E}/timeline.json")); DUR = TL["dur"]; WORDS = TL["words"]
WORLD.hide_render = True; ROOM.hide_render = True
SUN = [o for o in S.objects if o.type == "LIGHT" and o.data.type == "SUN"][0]
WBG = S.world.node_tree.nodes["Background"]
def F(t): return max(1, int(round(t * FPS)) + 1)
def wt(shot, word, k=0):
    word = word.lower().strip(".,!?-…")
    hits = [a for w, a, b in WORDS[shot] if w.lower().strip(".,!?-…") == word]
    return hits[min(k, len(hits) - 1)] if hits else 0.0
def ease(u): return u * u * (3 - 2 * u)
exec(open("/home/claude/zara/town/glow_sets.py").read())
exec(open("/home/claude/zara/town/glow_props.py").read())

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
def look_rot(src, dst):
    d = Vector(dst) - Vector(src); return math.atan2(d.y, d.x) + math.pi / 2
def hold(c, f0, f1, face=None, **kw):
    """keep a pose alive: gentle breathing + head drift (never fully static)"""
    for f in range(f0, f1 + 1, 2):
        t = f / 24; kw2 = dict(kw); kw2.setdefault("hips_z", 2.0); kw2["hips_z"] += 0.03 * math.sin(t * 2.6 + hash(c.name) % 7)
        hd = kw2.get("head", (0, 0, 0)); kw2["head"] = (hd[0] + 0.04 * math.sin(t * 1.9), hd[1], hd[2] + 0.05 * math.sin(t * 1.2))
        c.pose(f, **kw2)
    if face: c.set_face(face, f0)
def blinks(c, f0, f1, face, seed=0):
    rnd = random.Random(seed + len(c.name)); f = f0 + rnd.randint(6, 20)
    while f < f1 - 4: c.set_face("blink", f); c.set_face(face, f + 3); f += rnd.randint(30, 60)
def faces(c, keys):
    for f, k in keys: c.set_face(k, f)
def rim(target, coll=None, energy=900, col=(0.5, 0.65, 1.0), off=(4, 6, 7)):
    """moonlight rim on Rico so he reads in the dark"""
    L = light("rim", "AREA", Vector(target) + Vector(off), energy, col, size=4, coll=coll or TEMP)
    L.rotation_euler = (Vector(target) - L.location).to_track_quat("-Z", "Y").to_euler(); L.data.use_shadow = False; return L
def fill(target, energy=500, col=(0.55, 0.6, 0.9), off=(-2, -9, 5), size=6):
    L = light("fill", "AREA", Vector(target) + Vector(off), energy, col, size=size, coll=TEMP)
    L.rotation_euler = (Vector(target) - L.location).to_track_quat("-Z", "Y").to_euler(); L.data.use_shadow = False; return L
GZ = 0.0
def rico(loc, rotz=0.0, bell=True, fl=False, rimlight=True):
    c = mk_rico(TEMP); c.place(loc, rotz); eyes_glow(c, 2.5)
    if bell: c.bell = bell_on(c)
    if fl: flashlight(c); flash_on(c, 1, False)
    if rimlight: rim(Vector(loc) + Vector((0, 0, 4)))
    return c
def rico_shade(c, k=0.55):
    """match Rico's skin in bright close-ups to the night wides: darker copies of his skin + face materials"""
    for o in c.root.children_recursive:
        if o.type != "MESH": continue
        for i, m in enumerate(o.data.materials):
            if not m: continue
            if m.name.startswith("skin_"):
                o.data = o.data.copy(); g = m.copy(); g.diffuse_color = tuple(v * k for v in m.diffuse_color[:3]) + (1,); o.data.materials[i] = g
            elif m.use_nodes and any(n.bl_idname == "ShaderNodeTexImage" for n in m.node_tree.nodes) and m.name.startswith("face"):
                o.data = o.data.copy(); g = m.copy(); nt = g.node_tree; b = nt.nodes["Principled BSDF"]
                tex = [n for n in nt.nodes if n.bl_idname == "ShaderNodeTexImage"][0]
                mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
                mul.inputs[7].default_value = (k, k, k, 1); nt.links.new(tex.outputs["Color"], mul.inputs[6]); nt.links.new(mul.outputs[2], b.inputs["Base Color"])
                o.data.materials[i] = g
KCOL = {"jayden": (1.0, 0.16, 0.12), "maya": (0.15, 1.0, 0.35), "leo": (1.0, 0.72, 0.08), "tyrone": (0.2, 0.45, 1.0)}
MK = {"jayden": mk_jayden, "maya": mk_maya, "leo": mk_leo, "tyrone": mk_tyrone}
def kid(name, loc, rotz=0.0, halo=380):
    c = MK[name](TEMP); c.place(loc, rotz); glowify(c, KCOL[name], strength=0.6, halo=int(halo * 0.4)); return c
def glow_key(c, f, k):
    """scale a character's glow (emission + halo) at frame f"""
    for o in c.root.children_recursive:
        if o.type == "MESH":
            for m in o.data.materials:
                if m and m.use_nodes and "base_em" in m:
                    b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; b.default_value = m["base_em"] * k; b.keyframe_insert("default_value", frame=f)
    if getattr(c, "halo", None): c.halo.data.energy = c.halo["base"] * k; c.halo.data.keyframe_insert("energy", frame=f)
def strobe(c, f0, f1, step=3):
    """Leo's disco laugh: cycle the glow colour"""
    cols = [(1, 0.15, 0.1), (0.15, 1, 0.3), (0.2, 0.4, 1), (1, 0.85, 0.1), (1, 0.25, 0.85), (0.2, 1, 1)]
    mats = {m.name: m for o in c.root.children_recursive if o.type == "MESH" for m in o.data.materials if m and m.use_nodes and "base_em" in m}
    for k, f in enumerate(range(f0, f1 + 1, step)):
        col = cols[k % len(cols)]
        for m in mats.values():
            inp = m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]; inp.default_value = (*col, 1); inp.keyframe_insert("default_value", frame=f)
        if getattr(c, "halo", None): c.halo.data.color = col; c.halo.data.keyframe_insert("color", frame=f)
    for m in mats.values():
        ad = m.node_tree.animation_data
        if ad and ad.action:
            for fc in (ad.action.fcurves if hasattr(ad.action, "fcurves") else []):
                for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
def town_glow(f, k, skip=()):
    """scale EVERY glowing material in the scene (coats-on dimming)"""
    for m in bpy.data.materials:
        if m.use_nodes and "base_em" in m and m.name not in skip:
            bs = m.node_tree.nodes["Principled BSDF"]
            b = bs.inputs["Emission Strength"]; b.default_value = m["base_em"] * k; b.keyframe_insert("default_value", frame=f)
            bc = bs.inputs["Base Color"]
            if "base_col" not in m: m["base_col"] = list(bc.default_value)
            kk = min(1.0, 0.25 + k); bc.default_value = [v * kk for v in m["base_col"][:3]] + [1]; bc.keyframe_insert("default_value", frame=f)
def unique_glow(c):
    """give a character its own copies of glow materials (so it can be animated alone)"""
    for o in c.root.children_recursive:
        if o.type == "MESH":
            o.data = o.data.copy()
            for i, m in enumerate(o.data.materials):
                if m and "base_em" in m: o.data.materials[i] = m.copy()

# patch glowify/_glowmat to remember base strengths (for glow_key)
_old_glowmat = _glowmat
def _glowmat(m, col, strength):
    g = _old_glowmat(m, col, strength)
    if "base_em" not in g: g["base_em"] = g.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value
    return g
_old_glowify = glowify
def glowify(c, col, strength=0.55, halo=260):
    _old_glowify(c, col, strength, halo)
    if halo: c.halo["base"] = halo
    else: c.halo = None
    return c

# ---------------------------------------------------------------- crowds
def street_walkers(n, f1, ys=(-30, 30), lanes=(-6.0, 6.6, -1.8, 2.4), seed=1, speed=3.2):
    rnd = random.Random(seed); out = []
    for i in range(n):
        x = lanes[i % len(lanes)]; d = 1 if (i % 2 == 0) else -1
        y0 = ys[0] + (ys[1] - ys[0]) * ((i // len(lanes)) / max(1, n // len(lanes))) + rnd.uniform(-2, 2)
        c = townie(i + seed * 7); z = ground_z(x)
        c.walk(1, f1, (x, y0, z), (x, y0 + d * speed * f1 / 24, z)); out.append(c)
    return out
def tree_people(gap=True, coats=False, skip=(), scale=0.72, faces_=None):
    """everyone standing on the tree ledges as the lights. Returns {spot index: char}"""
    out = {}
    for k, (ti, a, p, rz) in enumerate(SPOTS):
        if (gap and k == GAP) or k in skip: continue
        c = townie(k + 3, scale=scale); c.place(Q + p, rz)
        c.pose(1, arms_side=(1.15, 1.15), arms=(0.15, 0.15))
        if coats: coat(c)
        out[k] = c
    return out
def tree_glow_lights(f, k):
    for L in TREE_LIGHTS:
        if "base" not in L: L["base"] = L.data.energy
        L.data.energy = L["base"] * k; L.data.keyframe_insert("energy", frame=f)
def square_crowd(n=14, r0=27, seed=2, face="happy"):
    out = []
    for i in range(n):
        a = math.radians(-90 + (i - (n - 1) / 2) * (110 / n)); r = r0 + (i % 2) * 4.5
        p = Q + Vector((math.cos(a) * r, math.sin(a) * r, 0))
        if (p - STAGE).length < 7 or (p - MAILBOX).length < 4: continue
        c = townie(40 + i + seed); c.place(p, look_rot(p, Q)); c.set_face(face, 1); out.append(c)
    return out
def moth_swarm(n, center, radius, z0, z1, f1, seed=0, scale=1.0, speed=0.6):
    out = []
    for i in range(n):
        m = Moth(TEMP, scale * (0.8 + 0.4 * ((i * 37) % 10) / 10), seed + i); m.flap(1, f1, speed=5 + (i % 3))
        ph = i / n * 2 * math.pi; z = z0 + (z1 - z0) * ((i * 7) % n) / max(1, n - 1); r = radius + (i % 3) * 2
        pts = [Vector(center) + Vector((math.cos(ph + k * speed) * r, math.sin(ph + k * speed) * r, z + math.sin(k + i))) for k in range(4)]
        m.fly(1, f1, pts, wobble=0.4); out.append(m)
    return out
def snowon(n): snow_anim(n)
def black_world():
    for coll in (MAIN, SQ, EDGE, SHOPI): coll.hide_render = True
    for coll, ls in ((MAIN, MAIN_LIGHTS), (SQ, SQ_LIGHTS + TREE_LIGHTS), (EDGE, EDGE_LIGHTS), (SHOPI, SHOPI_LIGHTS)):
        for L in ls: L.hide_render = True
    WBG.inputs[0].default_value = (0, 0, 0, 1); SUN.data.energy = 0.0
_old_show = show_set
def show_set(which):
    _old_show(which)
    SHOPI.hide_render = which != "shopi"
    for L in SHOPI_LIGHTS: L.hide_render = which != "shopi"
    for L in TREE_LIGHTS: L.hide_render = which != "square"
TRACK = []

# ================================================================ SHOTS
def s01(n):   # black: Leo, Maya, Jayden pop on FWOOM-FWOOM-FWOOM
    black_world()
    L = kid("leo", (-1.7, 0, 0), 0.2); M = kid("maya", (2.0, 4.0, 0), -0.15); J = kid("jayden", (-1.2, 8.0, 0), 0.08)
    for i, c in enumerate((L, M, J)):
        unique_glow(c); fo = 2 + i * 7
        glow_key(c, 1, 0.0); glow_key(c, fo - 1, 0.0); glow_key(c, fo, 1.6); glow_key(c, fo + 5, 1.0)
        c.idle(1, n, energy=1.2, base_face="excited", seed=i)
        c.set_face("excited", 1)
    cpath(n, (0.2, -13.5, 9.5), (0.2, 4.0, 4.4), (0.2, -12.2, 9.2), (0.2, 4.0, 4.4), 36, 38)
def s02(n):   # pull back: snowy street, no lamps, lit by glowing walkers
    show_set("main"); snowon(n)
    street_walkers(10, n, ys=(8, 46))
    cpath(n, (0.5, -4, 4.5), (0, 20, 4.5), (0.5, -20, 10), (0, 30, 3.5), 26, 28)
def s03(n):   # low angle: bulbless lamppost with a snow cap
    show_set("main"); snowon(n)
    street_walkers(4, n, ys=(28, 50), seed=3)
    top = LAMP_STEVE + Vector((-2.0, 0, 8.6))
    fill(top + Vector((0, 0, -1)), 900, col=(0.6, 0.7, 1.0), off=(-5, -3, -4), size=4)
    cpath(n, (5.2, 1.2, 1.2), top + Vector((1.2, 0, -1.5)), (5.6, 2.2, 1.4), top + Vector((1.2, 0, -1.0)), 22, 24)
def s04(n):   # tilt down to Steve: arm raised like a lamp, coffee, bored. A moth bonks his head
    show_set("main"); snowon(n)
    st = mk_steve(); p = LAMP_STEVE + Vector((-1.4, 0, 0)); st.place(p, look_rot(p, (0, p.y, 0))); coffee(st)
    hold(st, 1, n, face="smug", arms=(0, 0), arms_side=(2.9, 0.1))
    m = Moth(TEMP, 0.35, 3); m.flap(1, n, speed=8)
    head = p + Vector((0, 0, 6.75)); fb = int(n * 0.62)
    m.fly(1, fb, [p + Vector((-6, -3, 9)), p + Vector((-2.5, -1.2, 7.8)), head + Vector((-0.4, 0, 0.35))], wobble=0.15)
    m.fly(fb, n, [head + Vector((-0.4, 0, 0.35)), head + Vector((-2.5, -1.5, 1.8))], wobble=0.2)
    st.set_face("shocked", fb); st.set_face("smug", fb + 6)
    cpath(n, (2.0, 3.2, 7.5), LAMP_STEVE + Vector((-2, 0, 8.6)), (1.4, 3.6, 5.4), p + Vector((0, 0, 5.2)), 26, 30)
    TRACK.append(st.head)
def s05(n):   # Jayden at the bus stop, hands over eyes, counting
    show_set("main"); snowon(n)
    p = BUS + Vector((-0.6, 0, 0.2)); J = kid("jayden", p, look_rot(p, (20, p.y, 0)))
    for f in range(1, n + 1, 2):
        t = f / 24; J.pose(f, arms=(2.75, 2.75), arms_side=(-0.12, -0.12), head=(0.35 + 0.05 * math.sin(t * 8), 0, 0), hips_z=2.0 + 0.05 * abs(math.sin(t * 6)), lean=0.12)
    J.set_face("happy", 1)
    street_walkers(4, n, ys=(-44, -28), seed=5)
    cpath(n, p + Vector((-8.5, -6.0, 3.6)), p + Vector((0.5, 0, 3.8)), p + Vector((-7.0, -4.8, 3.8)), p + Vector((0.5, 0, 4.0)), 30, 33)
    TRACK.append(J.head)
def s06(n):   # spin + point: Maya "hidden" behind the trash can, glowing over the top
    show_set("main"); snowon(n); trashcan()
    M = kid("maya", TRASH + Vector((-0.2, 2.0, 0)), look_rot(TRASH + Vector((0, 2, 0)), (2, -10, 0)), halo=900)
    hold(M, 1, n, face="smug"); M.set_face("shocked", int(n * 0.55))
    jp = Vector((-1.0, -9.0, 0.03)); J = kid("jayden", jp, look_rot(jp, M.root.location))
    for f in range(1, n + 1):
        u = min(1, f / (n * 0.4)); J.pose(f, arms=(1.55 * ease(u), 0.1), arms_side=(0, 0.1), twist=0.6 * (1 - ease(u)))
    J.set_face("excited", 1)
    cpath(n, jp + Vector((4.6, -3.0, 5.4)), TRASH + Vector((0.2, 1.4, 3.0)), jp + Vector((4.2, -2.2, 5.3)), TRASH + Vector((0.2, 1.6, 3.3)), 30, 33)
def s07(n):   # whip pan: Tyrone behind a skinny lamppost, glowing on both sides
    show_set("main"); snowon(n)
    lamppost(LAMP_TY, TEMP, h=8, skinny=True)
    p = LAMP_TY + Vector((1.6, 0, 0)); T = kid("tyrone", p, look_rot(p, (0, p.y, 0)), halo=900)
    hold(T, 1, n, face="happy", arms_side=(0.05, 0.05))
    at = p + Vector((0, 0, 4.6))
    for f in range(1, n + 1):
        u = ease(min(1, f / 6)); cam2(f, Vector((0.5, 6.0, 4.8)), Vector((-6, 22, 4)).lerp(at, u), 30)
def s07b(n):  # whip pan: Leo hiding under snow, the glow shining through the mound
    show_set("main"); snowon(n)
    MP = Vector((-8.2, 16.0, 0.2))
    mound = sphere("mound", MP + Vector((0, 0, 0.2)), 1, emat("moundm", (1.0, 0.75, 0.2), 0.9, base=(0.85, 0.82, 0.75)), coll=TEMP, seg=20, scale=(2.2, 1.6, 1.5))
    L = light("moundglow", "POINT", MP + Vector((0, -1.8, 1.4)), 900, (1.0, 0.75, 0.2), coll=TEMP, radius=1.0)
    for f, s_ in ((1, 1.0), (int(n * 0.5), 1.04), (n, 1.0)):
        mound.scale = (2.2 * s_, 1.6 * s_, 1.5 / s_ ** 0.5); mound.keyframe_insert("scale", frame=f)   # giggling
    at = MP + Vector((0, 0, 1.2))
    for f in range(1, n + 1):
        u = ease(min(1, f / 6)); cam2(f, Vector((-1.0, 9.0, 3.6)), Vector((6, 22, 4)).lerp(at, u), 30)
def s08(n):   # Jayden face-plants in the snow, Leo cracks up
    show_set("main"); snowon(n)
    jp = Vector((-1.5, 0.0, 0.03)); J = kid("jayden", jp, look_rot(jp, (-1.5, -10, 0)))
    J.set_face("shocked", 1); fall = int(n * 0.55)
    for f in range(1, n + 1):
        u = ease(min(1, max(0, (f - 3) / (fall - 3))))
        J.root.rotation_euler = (1.48 * u, 0, look_rot(jp, (-1.5, -10, 0))); J.root.keyframe_insert("rotation_euler", frame=f)
        J.root.location = jp + Vector((0, 0, 0.62 * u)); J.root.keyframe_insert("location", frame=f)
        J.pose(f, arms=(2.9 * u, 2.9 * u), arms_side=(0.3, 0.3))
    lp = Vector((3.4, 4.5, 0.03)); L = kid("leo", lp, look_rot(lp, jp), halo=600)
    L.laugh(int(n * 0.45), n); L.set_face("happy", 1); L.set_face("laugh", int(n * 0.45))
    cpath(n, (4.0, -14.5, 4.8), (-0.2, -1.0, 1.8), (3.4, -13.2, 4.5), (-0.2, -1.0, 1.7), 28, 29)
def s09(n):   # Leo strobes like a disco ball; passers-by dance; Jayden still face-down
    show_set("main"); snowon(n)
    lp = Vector((0.0, 3.0, 0.03)); L = kid("leo", lp, look_rot(lp, (0, -10, 0)), halo=600); unique_glow(L)
    L.laugh(1, n); L.set_face("laugh", 1); strobe(L, 1, n, 3)
    for i, p in enumerate([(-5.2, 7.5), (5.0, 8.0), (-1.0, 12.5)]):
        c = townie(20 + i); c.place((*p, 0.03), look_rot((*p, 0.03), lp)); c.dance(1, n, style=i % 3); c.set_face("excited", 1)
    jp = Vector((-4.5, -2.5, 0.65)); J = kid("jayden", jp, 0.0, halo=200)
    J.root.rotation_euler = (1.48, 0, 0.0); J.root.keyframe_insert("rotation_euler", frame=1)
    J.pose(1, arms=(2.9, 2.9), arms_side=(0.3, 0.3))
    for f in (int(n * 0.5), int(n * 0.6)): J.legs[0].rotation_euler = (-0.4 if f == int(n * 0.5) else 0, 0, 0); J.legs[0].keyframe_insert("rotation_euler", frame=f)
    for f in range(1, n + 1):
        a = -0.35 + 0.3 * f / n; R = 13
        cam2(f, lp + Vector((math.sin(a) * R, -math.cos(a) * R, 4.2)), lp + Vector((0, 0, 3.2)), 28)
def s10(n):   # push into the shop window: cobwebbed XMAS LIGHTS box ($0), shopkeeper asleep behind
    show_set("shopi"); WBG.inputs[0].default_value = (0.01, 0.012, 0.03, 1)
    sk = townie(5, glow=True); p = SI + Vector((0, 7.0, 0)); sk.place(p, 0.0)   # behind the counter, facing the window
    for f in range(1, n + 1, 2):
        t = f / 24; sk.pose(f, head=(0.55 + 0.06 * math.sin(t * 2.2), 0.2, 0), hips_z=2.0 + 0.04 * math.sin(t * 2.2), arms_side=(0.05, 0.05))
    sk.set_face("blink", 1)
    zz = [text3d("z", p + Vector((0.8 + k * 0.5, -0.8, 6.6 + k * 0.6)), 0.4 + k * 0.15, emat("zzm", (0.8, 0.9, 1), 1.5), coll=TEMP) for k in range(3)]
    for k, z_ in enumerate(zz):
        for f in range(1, n + 1, 3):
            z_.location.z = p.z + 6.6 + k * 0.6 + 0.4 * ((f / 24 + k * 0.3) % 1.0); z_.keyframe_insert("location", frame=f)
    for f in range(1, n + 1, 2):
        SPIDER_ARM.rotation_euler = (0, 0.9 * math.sin(f / 24 * 14), 0); SPIDER_ARM.keyframe_insert("rotation_euler", frame=f)
    cpath(n, XBOX + Vector((0.6, -14.0, 4.6)), XBOX + Vector((0, 0, 2.2)), XBOX + Vector((0.2, -8.0, 3.9)), XBOX + Vector((0, 0, 1.6)), 32, 36)
def s11(n):   # WIDE: everyone on the tree IS the lights; Steve on a ledge with coffee
    show_set("square"); snowon(n)
    people = tree_people(gap=False, skip=[GAP])
    ti, a, p, rz = SPOTS[GAP]; st = mk_steve(); st.place(Q + p, rz); st.root.scale = (0.72,) * 3; coffee(st); hold(st, 1, n, face="sad", arms_side=(0.1, 0.1), arms=(0, 0.9))
    for k, c in list(people.items())[::3]: c.idle(1, n, energy=0.8, base_face="happy", seed=k)
    square_crowd(10)
    cpath(n, Q + Vector((0, -64, 6)), Q + Vector((0, 0, 16)), Q + Vector((0, -58, 14)), Q + Vector((0, 0, 18)), 30, 30)
def s12(n):   # smash to black: two white eyes blink
    black_world()
    R = rico((0, 0, 0), 0.0, rimlight=False); eyes_glow(R, 3.0)
    hold(R, 1, n, face="happy"); R.set_face("blink", int(n * 0.45)); R.set_face("happy", int(n * 0.45) + 3)
    cpath(n, (0, -6.5, 4.6), (0, 0, 4.5), (0, -6.0, 4.6), (0, 0, 4.5), 75, 80)
def s13(n):   # reveal: Rico among glowing kids, the only dark one, double thumbs-up
    show_set("main"); snowon(n)
    R = rico((0, 0, 0.03), 0.0)
    for f in range(1, n + 1, 2):
        u = min(1, f / 8); R.pose(f, arms=(1.45 * ease(u), 1.45 * ease(u)), arms_side=(0.15, 0.15), hips_z=2.0 + 0.05 * math.sin(f / 3))
    R.set_face("excited", 1)
    for nm, p in (("jayden", (-4.6, 2.2)), ("maya", (4.6, 2.4)), ("leo", (-2.3, 6.5)), ("tyrone", (2.8, 6.8))):
        c = kid(nm, (*p, 0.03), look_rot(p, (0, -12)), halo=500); c.idle(1, n, energy=1.0, base_face="happy", seed=len(nm))
    cpath(n, (0, -14, 4.8), (0, 2, 3.8), (0, -11.5, 4.6), (0, 2, 3.8), 30, 32)
    TRACK.append(R.head)
def s14(n):   # Mom calls into the dark (Rico waving right beside her) -> she ties the bell on him
    show_set("main"); snowon(n)
    mp = Vector((-2.2, 0, 0.03)); rp = Vector((2.2, 0.4, 0.03)); mp2 = Vector((-1.55, 0.2, 0.03)); rp2 = Vector((1.55, 0.2, 0.03))
    mom = mk_mom(); mom.place(mp, look_rot(mp, (-1.6, -10, 0)))
    R = rico(rp, look_rot(rp, (1.6, -10, 0)), bell=True); vis(R.bell, 1, False)
    cut = int(n * 0.5)
    for f in range(1, cut):
        t = f / 24; mom.pose(f, arms=(2.3, 0.2), arms_side=(-0.2, 0.1), head=(0.1, 0, 0.5 * math.sin(t * 5)))
        R.pose(f, arms=(0, 3.0), arms_side=(0.1, 0.25 + 0.25 * math.sin(t * 18)))
    mom.set_face("scared", 1); R.set_face("happy", 1)
    mom.move(cut - 1, mp, look_rot(mp, (-2.2, -10, 0))); R.move(cut - 1, rp, look_rot(rp, (2.2, -10, 0)))
    mom.move(cut, mp2, look_rot(mp2, rp2)); R.move(cut, rp2, look_rot(rp2, mp2))
    for f in range(cut, n + 1):
        u = min(1, (f - cut) / 6); mom.pose(f, arms=(1.35 * ease(u), 1.35 * ease(u)), arms_side=(-0.18, -0.18), head=(0.15 + 0.1 * math.sin(f / 2.5) * (f > cut + 8), 0, 0))
        R.pose(f, arms=(0, 0), arms_side=(0.08, 0.08))
    vis(R.bell, cut + 7, True); mom.set_face("happy", cut); R.set_face("sad", cut)
    cpath(n, (0, -13, 5.8), (0, 0, 3.8), (0, -12, 5.6), (0, 0, 3.8), 28, 29, f1=cut - 1)
    cpath(n, Vector((-0.3, -7.0, 4.3)), rp2 + Vector((-0.6, 0, 3.5)), Vector((-0.2, -6.4, 4.2)), rp2 + Vector((-0.6, 0, 3.5)), 36, 38, f0=cut)
    for fc_obj in (CAM, CAM.data):
        ad = fc_obj.animation_data
        if ad and ad.action:
            for fc in (ad.action.fcurves if hasattr(ad.action, "fcurves") else []):
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - cut) < 1.5 or abs(kp.co.x - (cut - 1)) < 1.5: kp.interpolation = "CONSTANT"
def s16(n):   # CU Whiskers: pitch-dark cat, white eyes, same bell; a glowing dog beside him
    show_set("main"); snowon(n)
    cp = Vector((7.6, -2, 0.2)); cat = dark_cat(1.3); cat.root.location = cp; cat.root.rotation_euler = (0, 0, look_rot(cp, cp + Vector((-7, 1.8, 0)))); cat.sit(1); cat.tailwag(1, n, 0.3)
    droot, dtail, dears = make_dog(TEMP); droot.location = cp + Vector((0, 3.6, 0)); droot.rotation_euler = (0, 0, look_rot(droot.location, cp + Vector((-7, 1.8, 0))))
    droot.scale = (1.3,) * 3; glow_objs(droot, (1.0, 0.8, 0.3), 1.6); wag(dtail, dears, 1, n)
    light("dogglow", "POINT", droot.location + Vector((0, -1.5, 1.8)), 600, (1.0, 0.8, 0.3), coll=TEMP, radius=1).data.use_shadow = False
    rim(cp + Vector((0, 0, 1)), energy=500)
    cpath(n, cp + Vector((-9.5, 1.2, 2.4)), cp + Vector((0, 1.6, 1.4)), cp + Vector((-8.5, 1.4, 2.2)), cp + Vector((0, 1.5, 1.5)), 30, 31)
    TRACK.append(cat.head)
def s17(n):   # Rico + Whiskers side by side, both dark, one deadpan bell shake
    show_set("main"); snowon(n)
    rp = Vector((6.6, -3.0, 0.2)); R = rico(rp, look_rot(rp, (0, -14, 0)))
    cp = rp + Vector((3.2, 0.6, 0)); cat = dark_cat(1.3); cat.root.location = cp; cat.root.rotation_euler = (0, 0, look_rot(cp, (0, -14, 0))); cat.sit(1)
    for f in range(1, n + 1):
        t = f / 24; j = abs(math.sin(t * 2 * math.pi * 1.8)) * (f > 4)
        R.pose(f, hips_z=2.0 + 0.12 * j, arms_side=(0.08, 0.08)); cat.body.location = (0, 0, 0.85 + 0.08 * j); cat.body.keyframe_insert("location", frame=f)
    R.set_face("sad", 1)
    rim(cp + Vector((0, 0, 1)), energy=400)
    cpath(n, rp + Vector((-1.2, -8.6, 3.0)), rp + Vector((1.6, 0, 2.4)), rp + Vector((-1.0, -7.8, 2.9)), rp + Vector((1.6, 0, 2.3)), 34, 36)
def s18(n):   # WIDE: the glowing tree with one dark hole -> push in: it's Rico, awkward smile
    show_set("square"); snowon(n)
    tree_people(gap=True); ti, a, p, rz = SPOTS[GAP]; R = rico(Q + p, rz); R.root.scale = (0.72,) * 3
    hold(R, 1, n, face="happy", arms_side=(1.15, 1.15), arms=(0.15, 0.15)); blinks(R, 1, n, "happy")
    square_crowd(10)
    tgt = Q + p + Vector((0, 0, 2.6))
    cpath(n, Q + Vector((0, -60, 10)), Q + Vector((0, 0, 16)), tgt + Vector((0, -15, 1.0)), tgt, 30, 32, f1=int(n * 0.5))
    cpath(n, tgt + Vector((0, -15, 1.0)), tgt, tgt + Vector((0, -12.5, 0.9)), tgt, 32, 32, f0=int(n * 0.5))
    TRACK.append(R.head)
def tree_close(n, rico_face="sad", neighbours=("leo", "jayden", "maya")):
    """Rico at his gap spot with the main kids on the neighbouring spots"""
    show_set("square"); snowon(n)
    ti, a, p, rz = SPOTS[GAP]
    same = sorted([k for k in range(len(SPOTS)) if SPOTS[k][0] == ti and k != GAP], key=lambda k: abs(SPOTS[k][1] - a))
    below = sorted([k for k in range(len(SPOTS)) if SPOTS[k][0] == ti - 1], key=lambda k: abs(SPOTS[k][1] - a))
    spots = {"leo": same[0], "jayden": same[1], "maya": below[0]}
    people = tree_people(gap=True, skip=[spots[nm] for nm in neighbours])
    R = rico(Q + p, rz); R.root.scale = (0.72,) * 3; hold(R, 1, n, face=rico_face, arms_side=(1.15, 1.15), arms=(0.15, 0.15)); tree_glow_lights(1, 0.3); rico_shade(R, 0.5)
    ks = {}
    for nm in neighbours:
        ti2, a2, p2, rz2 = SPOTS[spots[nm]]; c = kid(nm, Q + p2, rz2, halo=300); c.root.scale = (0.72,) * 3; ks[nm] = c
    return R, ks, p
def s19(n):   # kids on nearby branches point and laugh (Leo blinking with laughter)
    R, ks, p = tree_close(n, "sad")
    for nm, c in ks.items():
        rz = look_rot(c.root.location, R.root.location); c.move(1, c.root.location, rz)
        for f in range(1, n + 1, 2):
            t = f / 24; c.pose(f, arms=(1.5, 0.2), arms_side=(0.1, 0.1), hips_z=2.0 + 0.08 * abs(math.sin(t * 12)), head=(0.15 * math.sin(t * 10), 0, 0))
        c.set_face("laugh", 1)
    unique_glow(ks["leo"]); strobe(ks["leo"], 1, n, 3)
    tgt = Q + p + Vector((0, 0, 2.4))
    cpath(n, tgt + Vector((-3, -13, 2.5)), tgt, tgt + Vector((-2, -11.5, 2.0)), tgt, 30, 32)
def s20(n):   # CU: Jayden slaps a DEAD BULB note on Rico's chest
    R, ks, p = tree_close(n, "sad", neighbours=("jayden",))
    J = ks["jayden"]; pr = R.root.location.copy(); dv = (J.root.location - pr); dv.z = 0; dv.normalize()
    outv = Vector((pr.x - Q.x, pr.y - Q.y, 0)).normalized(); jpos = pr + dv * 2.9
    J.move(1, jpos, look_rot(jpos, pr + outv * 1.3)); hold(R, 1, n, face="sad", arms_side=(0.08, 0.08))
    slap = int(n * 0.45)
    for f in range(1, n + 1):
        u = ease(min(1, f / slap)); J.pose(f, arms=(1.55 * u, 0.1), arms_side=(-0.25 * u, 0.1))
    J.set_face("smug", 1)
    nt, _ = note(R, "DEAD BULB"); vis(nt, 1, False); vis(nt, slap, True); R.set_face("sad", 1); R.set_face("shocked", slap); R.set_face("sad", slap + 4)
    tgt = R.root.location + Vector((0, 0, 2.3))
    cpath(n, tgt + Vector((1.2, -6.2, 0.8)), tgt, tgt + Vector((0.9, -5.6, 0.7)), tgt, 34, 36)
def s21(n):   # bus stop: Rico pulls the flashlight from his jacket, sly look
    show_set("main"); snowon(n)
    p = BUS + Vector((-0.8, 0, 0.2)); R = rico(p, look_rot(p, (0, p.y - 2, 0)), fl=True)
    for f in range(1, n + 1):
        u = ease(min(1, f / (n * 0.5))); R.pose(f, arms=(0, 0.3 + 1.6 * u), arms_side=(0.05, -0.35 * u), head=(0.05, 0, -0.15 * u))
    R.set_face("smug", 1); fill(p + Vector((0, 0, 3.5)), 350)
    tgt = p + Vector((0, 0, 3.6))
    cpath(n, p + Vector((-7.5, -5.0, 3.9)), p + Vector((-1.2, -0.3, 3.1)), p + Vector((-6.6, -4.3, 3.8)), p + Vector((-1.4, -0.3, 3.2)), 30, 32)
    TRACK.append(R.fl["lens"])
def s22(n):   # click: townsfolk stare like it's alien tech, Leo cautiously pokes at it
    show_set("main"); snowon(n)
    p = BUS + Vector((-0.8, 0, 0.2)); R = rico(p, look_rot(p, (0, p.y - 2, 0)), fl=True)
    hold(R, 1, n, face="smug", arms=(0, 1.9), arms_side=(0.05, -0.35)); flash_on(R, 3, True)
    lp = p + Vector((-4.6, -3.8, -0.17)); L = kid("leo", lp, look_rot(lp, p), halo=400)
    for f in range(1, n + 1):
        u = ease(min(1, f / n)); L.pose(f, arms=(0.3 + 1.0 * u, 0), arms_side=(0, 0), lean=-0.15 * u)
    L.set_face("shocked", 1)
    for i, q in enumerate([p + Vector((-5.0, 3.6, -0.17)), p + Vector((-1.6, -6.6, -0.17))]):
        c = townie(30 + i); c.place(q, look_rot(q, p)); c.set_face("shocked", 1); hold(c, 1, n, arms_side=(0.3, 0.3))
    cpath(n, p + Vector((-13.5, -1.0, 6.0)), p + Vector((-2.6, -1.2, 2.6)), p + Vector((-12.5, -0.8, 5.8)), p + Vector((-2.6, -1.2, 2.6)), 24, 25)
def s23(n):   # WIDE: packed square, banner; the tree people wear coats (dim)
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    ti, a, p, rz = SPOTS[GAP]; R = rico(Q + p, rz, rimlight=False); R.root.scale = (0.72,) * 3; R.pose(1, arms_side=(1.15, 1.15))
    crowd = square_crowd(16)
    for i, c in enumerate(crowd): c.idle(1, n, energy=0.7, seed=i)
    may = mk_mayor(); may.place(STAGE + Vector((0, 0.4, STAGE_TOP)), look_rot(STAGE, Q + Vector((0, -40, 0)))); megaphone(may); hold(may, 1, n, face="happy")
    cpath(n, Q + Vector((-8, -66, 24)), Q + Vector((-4, 0, 12)), Q + Vector((-4, -60, 15)), Q + Vector((-2, 0, 14)), 28, 28)
def s24(n):   # the mayor counts down 3-2-1 with his megaphone, beaming
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    mp = STAGE + Vector((0, 0.4, STAGE_TOP)); may = mk_mayor(); may.place(mp, look_rot(STAGE, Q + Vector((-6, -40, 0)))); megaphone(may)
    beats = [wt("s24", "three"), wt("s24", "two"), wt("s24", "one")]
    for f in range(1, n + 1):
        t = (f - 1) / 24; k = sum(1 for b in beats if t >= b - 0.05)
        pump = max(0, 1 - min(abs(t - b) for b in beats) / 0.2)
        may.pose(f, arms=(1.45, 2.6 + 0.3 * pump), arms_side=(0.1, 0.1), head=(-0.1 - 0.08 * pump, 0, 0), hips_z=2.0 + 0.1 * pump)
    may.set_face("excited", 1); fill(mp + Vector((0, 0, 4)), 500, off=(3, -9, 5))
    crowd = square_crowd(16)
    for i, c in enumerate(crowd): c.idle(1, n, energy=0.9, seed=i, base_face="excited")
    tgt = mp + Vector((0, 0, 5.0))
    cpath(n, tgt + Vector((5, -14, -2.6)), tgt, tgt + Vector((3.8, -11.5, -2.2)), tgt, 30, 33)
    TRACK.append(may.head)
def s25(n):   # everybody on the tree unzips at once: coats fly off outward and drop
    show_set("square"); snowon(n)
    people = tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    ti, a, p, rz = SPOTS[GAP]; R = rico(Q + p, rz, rimlight=False); R.root.scale = (0.72,) * 3; R.pose(1, arms_side=(1.15, 1.15))
    f0 = int(n * 0.35)
    for k, c in people.items():
        for part in c.coat:
            loc0 = part.location.copy(); part.keyframe_insert("location", frame=f0)
            part.location = loc0 + Vector((0, -2.2, 0.6)); part.keyframe_insert("location", frame=f0 + 5)
            part.location = loc0 + Vector((0, -4.0, -6.0)); part.keyframe_insert("location", frame=f0 + 12)
            vis(part, f0 + 12, False)
        c.set_face("excited", f0)
    town_glow(f0 + 4, 0.15); town_glow(f0 + 10, 0.8); tree_glow_lights(f0 + 4, 0.12); tree_glow_lights(f0 + 10, 0.6)
    tgt = Q + p + Vector((0, 0, 1.0))
    cpath(n, tgt + Vector((-6, -26, 2)), tgt, tgt + Vector((-5, -23, 1.5)), tgt, 30, 30)
def s26(n):   # FWOOM: the tree explodes with colour, crowd gasps, Rico still the gap
    show_set("square"); snowon(n)
    people = tree_people(gap=True); tree_glow_lights(1, 0.5); tree_glow_lights(4, 1.8); tree_glow_lights(n, 1.3); town_glow(1, 0.8); town_glow(4, 1.6); town_glow(n, 1.15)
    ti, a, p, rz = SPOTS[GAP]; R = rico(Q + p, rz, rimlight=False); R.root.scale = (0.72,) * 3; R.pose(1, arms_side=(1.15, 1.15)); R.set_face("sad", 1)
    crowd = square_crowd(16, face="shocked")
    cpath(n, Q + Vector((0, -50, 3)), Q + Vector((0, 0, 17)), Q + Vector((0, -46, 3.2)), Q + Vector((0, 0, 17.5)), 26, 27, shake=0.12)
def s27(n):   # low angle at the moon: giant moth silhouettes swoop across it
    show_set("square"); snowon(n)
    tree_people(gap=True)
    eye = Q + Vector((-6, -40, 2)); tgt = MOON
    for i in range(5):
        m = Moth(TEMP, 2.2, i); m.flap(1, n, speed=4)
        d = (tgt - eye).normalized(); side = d.cross(Vector((0, 0, 1))).normalized()
        base = eye + d * (60 + i * 12)
        m.fly(1, n, [base - side * (40 + i * 6) + Vector((0, 0, i * 3)), base + side * (20 - i * 4) + Vector((0, 0, -2 + i * 2))], wobble=0.8)
    cpath(n, eye, tgt, eye + Vector((0, 1.0, 0)), tgt + Vector((0, 0, 2)), 48, 52)
def s28(n):   # moth POV: blazing tree, wobbly zoom
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.2)
    for f in range(1, n + 1):
        u = f / n; p = Q + Vector((14 * (1 - u), -70 + 30 * u, 28 - 6 * u)) + Vector((math.sin(f * 0.7) * 1.2, 0, math.sin(f * 0.9) * 1.0))
        cam2(f, p, Q + Vector((0, 0, 16)), 24 + 14 * u, roll=0.12 * math.sin(f * 0.35))
def s29(n):   # CU moth: eyes turn into hearts, it dives
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.2)
    mp = Q + Vector((8, -34, 22)); m = Moth(TEMP, 1.6, 4); m.flap(1, n, speed=4.5, amp=0.5)
    sw = int(n * 0.35); dv = int(n * 0.62)
    m.fly(1, dv, [mp, mp + Vector((0, 0.3, 0.2))], look=Q + Vector((0, 0, 16)), wobble=0.05)
    m.fly(dv, n, [mp + Vector((0, 0.3, 0.2)), Q + Vector((0, -12, 12))], wobble=0.1)
    hearts, eyes = heart_eyes(m); vis(hearts, 1, False); vis(hearts, sw, True); vis(eyes, 1, True); vis(eyes, sw, False)
    light("mothkey", "POINT", mp + Vector((-2, -5, 2)), 500, (1, 0.7, 0.5), coll=TEMP, radius=1).data.use_shadow = False
    d = (Q + Vector((0, 0, 16)) - mp).normalized(); sd = d.cross(Vector((0, 0, 1))).normalized()
    c0 = mp + d * 6.5 + sd * 2.2 + Vector((0, 0, 0.9))
    cpath(n, c0, mp + Vector((0, 0, 0.2)), c0 + d * -0.6, mp + Vector((0, 0, 0.2)), 34, 36, f1=dv)
    cpath(n, c0 + d * -0.6, mp + Vector((0, 0, 0.2)), c0 + Vector((0, 0, 1.5)), Q + Vector((0, -12, 12)), 36, 30, f0=dv)
    TRACK.append(m.head)
def s30(n):   # a moth chomps the mayor's pants clean off: candy-cane boxers
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.2)
    mp = STAGE + Vector((0, 0.4, STAGE_TOP)); may = mk_mayor(); rz = look_rot(STAGE, Q + Vector((-6, -40, 0))); may.place(mp, rz); megaphone(may)
    bx, pants = boxers(may); vis(bx, 1, False)
    ch = int(n * 0.42)
    hold(may, 1, n, face="excited", arms=(0.3, 2.8), arms_side=(1.25, 0.1))
    vis(pants, ch, False); vis(bx, ch, True); may.set_face("shocked", ch + 2)
    fwd = (Q + Vector((-6, -40, 0)) - STAGE); fwd.z = 0; fwd.normalize(); side = Vector((-fwd.y, fwd.x, 0))
    m = Moth(TEMP, 0.9, 5); m.flap(1, n, speed=7, amp=0.3, base=0.5)
    legs = mp + Vector((0, 0, 1.3 * 1.2))
    m.fly(1, ch, [legs + side * -9 + fwd * 4 + Vector((0, 0, 1)), legs + fwd * 2.1 + side * -0.3], look=legs, wobble=0.03)
    m.fly(ch, n, [legs + fwd * 2.1 + side * -0.3, legs + fwd * 5 + side * 7 + Vector((0, 0, 3))], wobble=0.2)
    tgt = mp + Vector((0, 0, 3.4))
    cpath(n, tgt + fwd * 12 + side * -3 + Vector((0, 0, -0.8)), tgt, tgt + fwd * 10.5 + side * -2.5 + Vector((0, 0, -0.8)), tgt, 30, 32)
    TRACK.append(may.head)
def s31(n):   # a moth rips the MATH homework from Jayden's backpack
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.2)
    jp = Q + Vector((8, -26, 0)); J = kid("jayden", jp, look_rot(jp, Q + Vector((8, 0, 0))), halo=400); bp, pap = backpack(J)
    hold(J, 1, n, face="happy"); gr = int(n * 0.45)
    m = Moth(TEMP, 1.0, 6); m.flap(1, n, speed=6)
    S.frame_set(1); top = pap.matrix_world.translation.copy()
    m.fly(1, gr, [top + Vector((-6, -5, 4)), top + Vector((0, -1.0, 0.5))], look=top, wobble=0.05)
    m.fly(gr, n, [top + Vector((0, -1.0, 0.5)), top + Vector((5, -7, 7))], wobble=0.2)
    hw2 = box("hw2", (0, -0.75, -0.65), (0.8, 0.05, 0.9), mat("white", (1, 1, 1)), parent=m.head, coll=TEMP)
    t2 = text3d("MATH", (0, -1.2, 0.2 / 0.9), 0.22, mat("hwred", (0.8, 0.05, 0.05), 0.5), coll=TEMP, parent=hw2); t2.rotation_euler = (math.pi / 2, 0, 0); t2.scale = (1 / 0.8, 1 / 0.9, 1 / 0.05)
    vis(hw2, 1, False); vis(hw2, gr, True); vis(pap, gr, False)
    J.set_face("shocked", gr)
    tgt = jp + Vector((0, 0, 4.2))
    cpath(n, tgt + Vector((-6, -9, 1.5)), tgt + Vector((0, -0.8, 0.5)), tgt + Vector((-5, -7.5, 1.6)), tgt + Vector((0.5, -1.5, 1.5)), 30, 30)
def s32(n):   # Jayden double fist-pumps, ecstatic (the moth flaps off with the homework)
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.2)
    jp = Q + Vector((8, -26, 0)); J = kid("jayden", jp, look_rot(jp, Q + Vector((8, -40, 0))), halo=600)
    for f in range(1, n + 1):
        t = f / 24; a = 2.8 + 0.25 * math.sin(t * 16)
        J.pose(f, arms=(a, 2.8 - 0.25 * math.sin(t * 16)), arms_side=(0.25, 0.25), hips_z=2.0 + 0.6 * abs(math.sin(t * 8)), head=(-0.2, 0, 0))
    J.set_face("excited", 1)
    m = Moth(TEMP, 1.0, 6); m.flap(1, n, speed=6)
    m.fly(1, n, [jp + Vector((4, 4, 9)), jp + Vector((10, 12, 14))], wobble=0.3)
    hw2 = box("hw2", (0, -0.75, -0.65), (0.8, 0.05, 0.9), mat("white", (1, 1, 1)), parent=m.head, coll=TEMP)
    tgt = jp + Vector((0, 0, 4.2))
    cpath(n, tgt + Vector((1.5, -10, -0.5)), tgt, tgt + Vector((1.0, -8.5, -0.3)), tgt + Vector((0, 0, 0.6)), 30, 30)
def s33(n):   # WIDE: moths swarm the whole tree
    show_set("square"); snowon(n)
    people = tree_people(gap=True); tree_glow_lights(1, 1.2)
    for k, c in people.items(): c.set_face("scared", 1)
    moth_swarm(18, Q, 17, 6, 34, n, seed=11, scale=1.4, speed=0.45)
    cpath(n, Q + Vector((-10, -62, 6)), Q + Vector((0, 0, 18)), Q + Vector((-5, -57, 9)), Q + Vector((0, 0, 18)), 28, 29, shake=0.08)
def s34(n):   # CU: dark Whiskers peeking from Tyrone's hood, a moth nibbling the hood edge; glasses askew
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.0)
    tp = Q + Vector((-8, -27, 0)); rz = look_rot(tp, tp + Vector((0, -10, 0))); T = kid("tyrone", tp, rz, halo=700)
    hold(T, 1, n, face="scared", arms_side=(0.2, 0.2))
    for o in T.root.children_recursive:
        if o.name.startswith("specs") or o.name.startswith("lens") or o.name.startswith("glass"): pass
    cat = dark_cat(0.5); cat.root.parent = T.hips; cat.root.location = (0.25, 0.95, 2.37); cat.root.rotation_euler = (0, 0, math.pi / 2); cat.sit(1)
    for f in range(1, n + 1, 2):
        cat.neck.rotation_euler = (0.45, 0, -0.9 + 0.2 * math.sin(f / 4)); cat.neck.keyframe_insert("rotation_euler", frame=f)
    m = Moth(TEMP, 0.4, 2); m.flap(1, n, speed=9, amp=0.3, base=0.15)
    hood = tp + Vector((-0.75 * 1.12, 0.75 * 1.12, (2.0 + 2.0) * 1.12))
    m.fly(1, n, [tp + Vector((0.0, 2.1, 7.1)), tp + Vector((0.15, 1.9, 6.95))], look=tp + Vector((0.3, 1.1, 5.6)), wobble=0.04)
    tgt = tp + Vector((0.2, 1.2, 5.8))
    cpath(n, tgt + Vector((4.2, 5.0, 0.8)), tgt, tgt + Vector((3.6, 4.4, 0.7)), tgt, 32, 34)
    TRACK.append(cat.head)
def s35(n):   # Rico's eyes go wide; he rips off the DEAD BULB note and stuffs it in his pocket
    R, ks, p = tree_close(n, "shocked", neighbours=())
    nt, _ = note(R, "DEAD BULB"); rip = int(n * 0.45)
    nt.keyframe_insert("location", frame=rip); nt.location = (0.9, -0.7, 0.35); nt.keyframe_insert("location", frame=rip + 6); vis(nt, rip + 7, False)
    for f in range(1, n + 1):
        u = ease(min(1, max(0, (f - rip + 3) / 8))); R.pose(f, arms=(0.15 + 1.0 * (1 - abs(2 * u - 1)), 0.15), arms_side=(1.15 - 0.9 * u, 1.15))
    R.set_face("shocked", 1); R.set_face("determined", rip + 6)
    moth_swarm(6, Q, 16, 8, 18, n, seed=21, scale=1.2, speed=0.5)
    tgt = R.root.location + Vector((0, 0, 2.4))
    cpath(n, tgt + Vector((0.6, -6.6, 0.6)), tgt, tgt + Vector((0.4, -5.8, 0.5)), tgt, 34, 36)
def s36(n):   # Maya behind a mailbox, glowing all around it like a halo; moths circle overhead
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.0)
    mp = MAILBOX + Vector((0, 2.0, 0)); M = kid("maya", mp, look_rot(mp, mp + Vector((0, -10, 0))), halo=1400)
    hold(M, 1, n, face="scared", arms_side=(0.05, 0.05)); blinks(M, 1, n, "scared")
    L = light("mayahalo", "POINT", mp + Vector((0, 0.9, 2.8)), 2200, KCOL["maya"], coll=TEMP, radius=2.0); L.data.use_shadow = True
    moth_swarm(5, mp + Vector((0, 0, 0)), 4.5, 8.5, 11, n, seed=31, scale=0.9, speed=0.9)
    tgt = MAILBOX + Vector((0, 0, 3.6))
    cpath(n, tgt + Vector((-2, -13, 1.0)), tgt + Vector((0, 0, 1.5)), tgt + Vector((-1.5, -11.2, 1.2)), tgt + Vector((0, 0, 2.2)), 30, 30)
def s37(n):   # near-black: Rico's white eyes narrow, determined
    black_world()
    R = rico((0, 0, 0), 0.0, rimlight=False); eyes_glow(R, 3.0)
    hold(R, 1, n, face="shocked"); R.set_face("determined", int(n * 0.4))
    for objs in R.faces.values():
        for o in objs:
            o.scale = (1, 1, 1); o.keyframe_insert("scale", frame=int(n * 0.4)); o.scale = (1.15, 1, 0.42); o.keyframe_insert("scale", frame=int(n * 0.4) + 4)
    rim((0, 0, 4), energy=60)
    cpath(n, (0.3, -6.0, 4.6), (0, 0, 4.5), (0.2, -5.6, 4.6), (0, 0, 4.5), 80, 90)
def s38(n):   # Rico hops down the tree ledge by ledge (jingle, jingle); moths whoosh past, never noticing
    show_set("square"); snowon(n)
    ti, a, p, rz = SPOTS[GAP]
    people = tree_people(gap=True, skip=[k for k in range(len(SPOTS)) if SPOTS[k][0] < ti and abs(SPOTS[k][1] - a) < 0.42]); tree_glow_lights(1, 1.0)
    R = rico(Q + p, rz); R.root.scale = (0.72,) * 3
    pts = []
    for t_ in range(ti, -1, -1):
        zb, r = TIERS[t_]; pts.append(Q + Vector((math.cos(a) * (r + 0.9), math.sin(a) * (r + 0.9), zb + LEDGE_TOP)))
    pts.append(Q + Vector((math.cos(a) * (TIERS[0][1] + 4.5), math.sin(a) * (TIERS[0][1] + 4.5), 0)))
    seg = (n - 2) / (len(pts) - 1)
    for f in range(1, n + 1):
        u = min(len(pts) - 1.0001, (f - 1) / seg); i = int(u); t = u - i
        a_, b_ = pts[i], pts[i + 1]; q = a_.lerp(b_, t); q.z = a_.z + (b_.z - a_.z) * t + 1.6 * math.sin(math.pi * t)
        q = q + (Vector((math.cos(a), math.sin(a), 0)) * 0.8 * math.sin(math.pi * t))
        R.move(f, q, rz); R.pose(f, arms=(2.6, 2.6), arms_side=(0.2, 0.2), legs=(1.0, 0.7), hips_z=2.0, lean=0.15)
    R.set_face("determined", 1)
    for i in range(3):
        m = Moth(TEMP, 1.1, 40 + i); m.flap(1, n, speed=6)
        c0 = pts[min(i + 1, len(pts) - 1)] + Vector((0, 0, 2.5))
        side = Vector((-math.sin(a), math.cos(a), 0))
        m.fly(1, n, [c0 + side * 12 + Vector((math.cos(a), math.sin(a), 0)) * 11 + Vector((0, 0, 3)), c0 - side * 12 + Vector((math.cos(a), math.sin(a), 0)) * 11 + Vector((0, 0, 3))], wobble=0.2)
    mid = pts[1] + Vector((0, 0, 2))
    out_ = Vector((math.cos(a), math.sin(a), 0))
    cpath(n, mid + out_ * 16 + Vector((0, 0, 4)), pts[0] + Vector((0, 0, 1.5)), mid + out_ * 15 + Vector((0, 0, -2)), pts[-1] + Vector((0, 0, 2)), 30, 30)
    TRACK.append(R.head)
def s39(n):   # ground level: a moth sits on Rico's head (oblivious) as he tiptoes through the swarm
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.0)
    a0 = Q + Vector((4, -18, 0)); a1 = Q + Vector((-4, -21, 0)); R = rico(a0, look_rot(a0, a1))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); ph = f / 24 * 2 * math.pi * 1.1; s_ = math.sin(ph)
        R.move(f, a0.lerp(a1, u), look_rot(a0, a1))
        R.pose(f, arms=(0.9 + 0.2 * s_, 0.9 - 0.2 * s_), arms_side=(0.5, 0.5), legs=(0.9 * max(0, s_), 0.9 * max(0, -s_)), hips_z=2.0 + 0.15 * abs(s_), lean=0.1)
    R.set_face("determined", 1)
    mh = Moth(TEMP, 0.5, 7); mh.root.parent = R.head; mh.root.location = (0, 0.1, 1.25); mh.root.scale = (0.5 / 0.93,) * 3; mh.flap(1, n, speed=1.2, amp=0.25)
    moth_swarm(6, Q + Vector((0, -15, 0)), 6, 10, 13, n, seed=51, scale=1.0, speed=0.7)
    S.frame_set(1); mid = a0.lerp(a1, 0.5)
    cpath(n, a0 + Vector((-1, -11, 3.2)), a0 + Vector((0, 0, 3.6)), mid + Vector((0, -10.5, 3.2)), a1 + Vector((0, 0, 3.6)), 28, 28)
    TRACK.append(R.head)
RP = Q + Vector((-5.0, -19.0, 0)); RF = (Q - RP); RF.z = 0; RF.normalize(); RS = Vector((-RF.y, RF.x, 0))
def s40(n):   # on the stage, hands cupped: "EVERYBODY, COATS ON!"
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.0)
    mp = RP; R = rico(mp, look_rot(mp, Q)); tree_glow_lights(1, 0.35); rico_shade(R, 0.42)
    for f in range(1, n + 1, 2):
        t = f / 24; R.pose(f, arms=(2.35, 2.35), arms_side=(-0.38, -0.38), head=(-0.3, 0, 0), lean=0.06 * math.sin(t * 9), hips_z=2.0 + 0.04 * math.sin(t * 9))
    R.set_face("shocked", 1)
    moth_swarm(6, Q, 17, 12, 24, n, seed=61, scale=1.2)
    tgt = mp + Vector((0, 0, 3.6))
    cpath(n, tgt + RF * 7 + RS * 3.0 + Vector((0, 0, -1.8)), tgt, tgt + RF * 6.2 + RS * 2.6 + Vector((0, 0, -1.6)), tgt + Vector((0, 0, 0.3)), 28, 30)
def s41(n):   # WIDE: the whole tree zips up at once -> the square goes dim, moths hover confused
    show_set("square"); snowon(n)
    people = tree_people(gap=True, coats=True); zp = int(n * 0.3)
    for k, c in people.items():
        for part in c.coat:
            s0 = part.scale.copy(); part.scale = s0 * 0.01; part.keyframe_insert("scale", frame=zp - 1); part.scale = s0; part.keyframe_insert("scale", frame=zp + 2)
    tree_glow_lights(1, 1.0); tree_glow_lights(zp, 1.0); tree_glow_lights(zp + 3, 0.12); town_glow(1, 1.0); town_glow(zp, 1.0); town_glow(zp + 3, 0.15)
    moth_swarm(12, Q, 17, 8, 30, n, seed=71, scale=1.3, speed=0.15)
    cpath(n, Q + Vector((0, -58, 8)), Q + Vector((0, 0, 17)), Q + Vector((0, -55, 8.5)), Q + Vector((0, 0, 17)), 28, 28)
def s42(n):   # INSERT (dark): click — the flashlight comes on
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    mp = RP; R = rico(mp, look_rot(mp, Q), fl=True)
    hold(R, 1, n, face="determined", arms=(0, 1.6), arms_side=(0.05, -0.2)); flash_on(R, int(n * 0.4), True)
    S.frame_set(1); fl = R.fl["root"].matrix_world.translation.copy()
    cpath(n, fl + RF * 1.2 + RS * 2.6 + Vector((0, 0, 0.6)), fl, fl + RF * 1.0 + RS * 2.3 + Vector((0, 0, 0.5)), fl, 36, 38)
def s43(n):   # the beam is the only light in the square, raised like a sword: "HEY, MOTHS! OVER HERE!"
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    mp = RP; R = rico(mp, look_rot(mp, Q), fl=True); flash_on(R, 1, True)
    for f in range(1, n + 1, 2):
        t = f / 24; u = ease(min(1, f / 8)); R.pose(f, arms=(0.4, 1.6 + 1.3 * u), arms_side=(0.25, -0.1), head=(-0.2, 0, 0), hips_z=2.0 + 0.05 * math.sin(t * 12))
    R.set_face("excited", 1)
    tgt = mp + Vector((0, 0, 4.0))
    cpath(n, tgt + RF * 6 + RS * 5 + Vector((0, 0, -3.2)), tgt + Vector((0, 0, 1.2)), tgt + RF * 5.4 + RS * 4.4 + Vector((0, 0, -3.0)), tgt + Vector((0, 0, 1.8)), 24, 26)
def s44(n):   # every moth's head snaps toward him at once
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    mp = RP; R = rico(mp, look_rot(mp, Q), fl=True); flash_on(R, 1, True)
    hold(R, 1, n, face="excited", arms=(0.4, 3.1), arms_side=(0.25, 0.0)); R.fl["spot"].data.energy = 2500; R.fl["spot"].data.keyframe_insert("energy", frame=1)
    sn = int(n * 0.35)
    for i in range(9):
        m = Moth(TEMP, 1.4, 80 + i); m.flap(1, n, speed=4, amp=0.4)
        p = mp + RF * (6 + (i // 3) * 7.5) + RS * ((i % 3 - 1) * 9.0) + Vector((0, 0, 8 + (i % 2) * 4 + (i // 3) * 2))
        r0 = random.Random(i).uniform(-2, 2)
        m.root.location = p; m.root.rotation_euler = (0.1, 0, r0); m.root.keyframe_insert("location", frame=1); m.root.keyframe_insert("rotation_euler", frame=1)
        m.root.keyframe_insert("rotation_euler", frame=sn); m.root.rotation_euler = (0.1, 0, look_rot(p, mp)); m.root.keyframe_insert("rotation_euler", frame=sn + 2)
    tgt = mp + RF * 12 + Vector((0, 0, 11))
    cpath(n, mp - RF * 4 + RS * 2.5 + Vector((0, 0, 5)), tgt, mp - RF * 3.6 + RS * 2.2 + Vector((0, 0, 5.1)), tgt, 24, 25)
def s45(n):   # Rico gulps, then bolts; a cloud of moths chases the beam
    show_set("square"); snowon(n)
    tree_people(gap=True, coats=True); tree_glow_lights(1, 0.12); town_glow(1, 0.15)
    a0 = STAGE + Vector((3.0, -6.5, 0)); a1 = a0 + Vector((-9, -9, 0)); R = rico(a0, look_rot(a0, a1), fl=True); flash_on(R, 1, True)
    go = int(n * 0.3)
    hold(R, 1, go, face="scared", arms=(0.4, 1.7), arms_side=(0.25, -0.1))
    for f in range(go, n + 1):
        u = (f - go) / (n - go); ph = (f - go) / 24 * 2.8 * 2 * math.pi; s_ = math.sin(ph)
        R.move(f, a0.lerp(a1, u), look_rot(a0, a1)); R.pose(f, arms=(-s_ * 0.8, -2.0), arms_side=(0.1, 0.25), legs=(s_ * 0.95, -s_ * 0.95), hips_z=2.0 + 0.25 * abs(math.cos(ph)), lean=-0.2)
    R.set_face("scared", 1)
    for i in range(9):
        m = Moth(TEMP, 0.9, 90 + i); m.flap(1, n, speed=6)
        off = Vector(((i % 3 - 1) * 6.5, 7 + (i // 3) * 6.0, 5 + (i % 2) * 3.5))
        m.fly(1, n, [a0 + off + Vector((6, 8, 3)), a0.lerp(a1, 0.35) + off, a1 + off], wobble=0.3)
    cpath(n, a0 + Vector((6, -8, 4.5)), a0 + Vector((0, 0, 3.5)), a1 + Vector((9, -7, 5)), a1 + Vector((2, 2, 4)), 26, 26)
def s46(n):   # sprint down the snowy Main Street, beam high, a river of moths behind
    show_set("main"); snowon(n)
    a0 = Vector((0, 22, 0.03)); a1 = Vector((0, -6, 0.03)); R = rico(a0, look_rot(a0, a1), fl=True); flash_on(R, 1, True)
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); ph = f / 24 * 2.8 * 2 * math.pi; s_ = math.sin(ph)
        R.move(f, a0.lerp(a1, u), look_rot(a0, a1)); R.pose(f, arms=(-s_ * 0.8, -2.0), arms_side=(0.1, 0.25), legs=(s_ * 0.95, -s_ * 0.95), hips_z=2.0 + 0.25 * abs(math.cos(ph)), lean=-0.2)
    R.set_face("scared", 1)
    for i in range(12):
        m = Moth(TEMP, 1.0, 100 + i); m.flap(1, n, speed=6)
        off = Vector(((i % 3 - 1) * 4.5, 8 + (i // 3) * 6.5, 5 + (i % 2) * 3.0))
        m.fly(1, n, [a0 + off, a1 + off], wobble=0.3)
    S.frame_set(1)
    for f in range(1, n + 1):
        p = a0.lerp(a1, (f - 1) / (n - 1)); cam2(f, p + Vector((3.5, -13, 4.5)), p + Vector((0, 4, 4.0)), 26)
def s47(n):   # edge of town: Rico props the flashlight on the rock, beam pointing up
    show_set("edge"); snowon(n)
    rp = ROCK + Vector((3.3, -2.6, 0)); R = rico(rp, look_rot(rp, ROCK), fl=True); flash_on(R, 1, True)
    pl = int(n * 0.55)
    for f in range(1, n + 1):
        u = ease(min(1, f / pl)); R.pose(f, arms=(2.9 - 1.6 * u, 0.2), arms_side=(-0.1, 0.1), lean=-0.25 * u)
    R.set_face("determined", 1)
    vis([R.fl["root"]], pl, False); flash_on(R, pl, False)
    fl2 = empty("flrock", ROCK + Vector((0.2, 0.0, 1.95)), coll=TEMP); fl2.rotation_euler = (0.35, 0, 0)
    cyl("flbody2", (0, 0, 0), 0.2, 1.0, mat("flbodym", (0.85, 0.15, 0.1), 0.4), parent=fl2, coll=TEMP, verts=12).rotation_euler = (0, 0, 0)
    cyl("flhead2", (0, 0, 0.6), 0.3, 0.35, METAL, parent=fl2, coll=TEMP, verts=12)
    cyl("fllens2", (0, 0, 0.79), 0.26, 0.04, emat("fllensm2", (1, 0.95, 0.8), 30), parent=fl2, coll=TEMP, verts=12)
    cone("flbeam2", (0, 0, 13.0), 4.0, 24, emat("beamm2", (1, 0.95, 0.75), 0.5, alpha=0.07), verts=20, parent=fl2, coll=TEMP, rot=(math.pi, 0, 0))
    sp = light("flspot2", "SPOT", (0, 0, 0.9), 6000, (1, 0.95, 0.8), coll=TEMP, radius=0.2, parent=fl2); sp.rotation_euler = (math.pi, 0, 0); sp.data.spot_size = math.radians(40)
    vis([fl2], 1, False); vis([fl2], pl, True)
    for i in range(5):
        m = Moth(TEMP, 0.9, 110 + i); m.flap(1, n, speed=5)
        off = Vector(((i - 2) * 6.5, 0, 8 + (i % 2) * 3.5))
        m.fly(1, n, [ROCK + off + Vector((0, -14, 0)), ROCK + off + Vector((0, 4, 0))], wobble=0.3)
    tgt = ROCK + Vector((0.8, 0, 2.6))
    cpath(n, ROCK + Vector((-5.5, -8.5, 3.4)), tgt + Vector((0.6, -0.6, 0)), ROCK + Vector((-4.8, -7.5, 3.0)), tgt + Vector((0.4, -0.6, 0.3)), 30, 30)
def flrock():
    fl2 = empty("flrock", ROCK + Vector((0.2, 0.0, 1.95)), coll=TEMP); fl2.rotation_euler = (0.35, 0, 0)
    cyl("flbody2", (0, 0, 0), 0.2, 1.0, mat("flbodym", (0.85, 0.15, 0.1), 0.4), parent=fl2, coll=TEMP, verts=12)
    cyl("flhead2", (0, 0, 0.6), 0.3, 0.35, METAL, parent=fl2, coll=TEMP, verts=12)
    cyl("fllens2", (0, 0, 0.79), 0.26, 0.04, emat("fllensm2b", (1, 0.95, 0.8), 30), parent=fl2, coll=TEMP, verts=12)
    cone("flbeam2", (0, 0, 13.0), 4.0, 24, emat("beamm2b", (1, 0.95, 0.75), 0.5, alpha=0.07), verts=20, parent=fl2, coll=TEMP, rot=(math.pi, 0, 0))
    sp = light("flspot2", "SPOT", (0, 0, 0.9), 6000, (1, 0.95, 0.8), coll=TEMP, radius=0.2, parent=fl2); sp.rotation_euler = (math.pi, 0, 0); sp.data.spot_size = math.radians(40)
    return fl2
def s48(n):   # Rico tiptoes away, cartoon-exaggerated, bell jingling, glancing back
    show_set("edge"); snowon(n); flrock()
    a0 = ROCK + Vector((2.5, -3.0, 0)); a1 = a0 + Vector((3.5, -6.5, 0)); R = rico(a0, look_rot(a0, a1))
    for f in range(1, n + 1):
        u = (f - 1) / (n - 1); ph = f / 24 * 2 * math.pi * 1.2; s_ = math.sin(ph)
        R.move(f, a0.lerp(a1, u), look_rot(a0, a1))
        R.pose(f, arms=(0.9 + 0.2 * s_, 0.9 - 0.2 * s_), arms_side=(0.55, 0.55), legs=(1.0 * max(0, s_), 1.0 * max(0, -s_)), hips_z=2.0 + 0.18 * abs(s_), head=(0, 0, 2.2 * min(1, u * 2)))
    R.set_face("determined", 1)
    for i in range(10):
        m = Moth(TEMP, 0.8, 120 + i); m.flap(1, n, speed=1.5, amp=0.12, base=1.3); a = i / 10 * 2 * math.pi
        p = ROCK + Vector((math.cos(a) * 4.6, math.sin(a) * 4.6, 0.55)); m.place(p, look_rot(p, ROCK))
    tgt = a0.lerp(a1, 0.5) + Vector((0, 0, 3))
    cpath(n, tgt + Vector((2, -12, 1.5)), tgt, tgt + Vector((1.5, -10.5, 1.3)), tgt, 28, 30)
def s49(n):   # back at the tree: Tyrone beams, Whiskers safe in his arms; his hoodie is now a crop top
    show_set("square"); snowon(n)
    tree_people(gap=True); tree_glow_lights(1, 1.0)
    tp = Q + Vector((-2.6, -26, 0)); rp = Q + Vector((2.4, -26.4, 0))
    T = kid("tyrone", tp, look_rot(tp, Q + Vector((-1, -40, 0))), halo=600); R = rico(rp, look_rot(rp, Q + Vector((1, -40, 0))))
    hold(T, 1, n, face="happy", arms=(0.6, 0.6), arms_side=(-0.05, -0.05))
    belly = box("belly", (0, 0, 0.42), (2.0 * 1.15 + 0.03, 1.0 * 1.12 + 0.03, 0.85), _glowmat(mat(f"skin_{SKT}", SKT, 0.5), KCOL["tyrone"], 0.6), parent=T.hips, coll=TEMP, bevel=0.2)
    cat = dark_cat(0.75); cat.root.parent = T.hips; cat.root.location = (0.2, -1.0, 0.45); cat.root.rotation_euler = (0, 0, math.pi / 2); cat.sit(1); cat.tailwag(1, n)
    cat.neck.rotation_euler = (0.45, 0, -1.1); cat.neck.keyframe_insert("rotation_euler", frame=1)
    for f in range(1, n + 1, 2):
        t = f / 24; R.pose(f, arms=(2.9, 2.9), arms_side=(0.3, 0.3), hips_z=2.0 + 0.35 * abs(math.sin(t * 7)))
    R.set_face("excited", 1)
    tgt = (tp + rp) / 2 + Vector((0, 0, 4.3))
    cpath(n, tgt + Vector((0, -13, 0.6)), tgt, tgt + Vector((0, -11.5, 0.5)), tgt, 30, 31)
def s50(n):   # the crowd on the ledges passes Rico up the glowing tree toward the star spot
    show_set("square"); snowon(n)
    people = tree_people(gap=False, skip=[GAP]); tree_glow_lights(1, 1.0)
    ti, a, p, rz = SPOTS[GAP]; out_ = Vector((math.cos(a), math.sin(a), 0))
    R = rico(Q, 0.0); R.root.scale = (0.72,) * 3
    z0, z1 = TIERS[1][0] + 2, TIERS[5][0] + 4.5
    for f in range(1, n + 1):
        u = ease((f - 1) / (n - 1)); z = z0 + (z1 - z0) * u
        r = max(rr + 1.7 + 0.6 for zb, rr in TIERS if zb <= z + 3.0) + 1.8
        R.move(f, Q + out_ * r + Vector((0, 0, z)), rz)
        R.root.rotation_euler = (-1.2, 0, rz); R.root.keyframe_insert("rotation_euler", frame=f)
        R.pose(f, arms=(2.9, 2.9), arms_side=(0.4, 0.4))
    R.set_face("excited", 1)
    for k, c in people.items():
        if abs(SPOTS[k][1] - a) < 0.5: c.pose(1, arms=(2.6, 2.6), arms_side=(0.3, 0.3)); c.set_face("excited", 1)
    S.frame_set(1)
    cpath(n, Q + out_ * 27 + Vector((0, 0, z0 + 1)), Q + out_ * 10 + Vector((0, 0, z0 + 2)), Q + out_ * 25 + Vector((0, 0, z1)), Q + out_ * 8 + Vector((0, 0, z1 + 1)), 30, 30)
    TRACK.append(R.head)
def s51(n):   # top of the tree: Rico tosses the crumpled DEAD BULB note; Jayden slaps "STAR" on him; Steve toasts; mayor (boxers) salutes
    show_set("square"); snowon(n)
    people = tree_people(gap=False, skip=[GAP]); tree_glow_lights(1, 1.0)
    for o in STAR.children_recursive: o.hide_render = True
    cyl("topper", Q + Vector((0, 0, TREE_H + 0.15)), 1.1, 0.3, GOLD, coll=TEMP, verts=20)
    top = Q + Vector((0, 0, TREE_H + 0.3)); R = rico(top, look_rot(top, top + Vector((0, -10, 0)))); R.root.scale = (1.0,) * 3
    light("starglow", "POINT", top + Vector((0, -2.5, 3.5)), 250, (1, 0.8, 0.35), coll=TEMP, radius=1.5).data.use_shadow = False; rico_shade(R, 0.42)
    hold(R, 1, n, face="happy", arms=(0, 2.9), arms_side=(0.1, 0.35))
    nt, _ = note(R, "STAR", col=(1, 0.85, 0.1)); vis(nt, 1, False); vis(nt, int(n * 0.55), True)
    R.set_face("excited", int(n * 0.55))
    crum = sphere("crumple", top + Vector((1.5, -0.5, 3.5)), 0.22, mat("notem(1.0, 0.92, 0.25)", (1.0, 0.92, 0.25), 0.8), coll=TEMP, seg=6)
    for f in range(1, n + 1):
        u = f / n; crum.location = top + Vector((1.5 + 6 * u, -0.5 - 2 * u, 3.5 + 3 * u - 14 * u * u)); crum.keyframe_insert("location", frame=f)
    st = mk_steve(); sp_ = Q + Vector((-4.5, -17, 0)); st.place(sp_, look_rot(sp_, Q + Vector((0, -40, 0)))); coffee(st)
    hold(st, 1, n, face="happy", arms=(0, 2.7), arms_side=(0.1, 0.2))
    may = mk_mayor(); mp = Q + Vector((4.5, -17, 0)); may.place(mp, look_rot(mp, Q + Vector((0, -40, 0)))); bx, pants = boxers(may); vis(pants, 1, False); vis(bx, 1, True)
    hold(may, 1, n, face="happy", arms=(0, 2.4), arms_side=(0, -0.6))
    tgt = top + Vector((0, 0, 2.6))   # close for the whole shot (STAR lands on the close)
    cpath(n, tgt + Vector((0.8, -8.0, 0.6)), tgt, tgt + Vector((0.9, -7.0, 0.4)), tgt, 30, 32)
def concert(n, sway=False):
    """moths sitting in rows facing the flashlight rock; spacing checked so no wings overlap"""
    light("spill", "POINT", ROCK + Vector((0, -3, 3.5)), 1400, (1, 0.85, 0.6), coll=TEMP, radius=2).data.use_shadow = False
    placed = []; ms = []; k = 0
    for row, (r, cnt) in enumerate(((6.5, 2), (11.0, 4), (15.5, 6))):
        for j in range(cnt):
            span = 116; a = math.radians(-90 - span / 2 + span * (j + 0.5) / cnt)
            p = ROCK + Vector((math.cos(a) * r, math.sin(a) * r, 0.5))
            if any((p - q).length < 5.0 for q in placed): continue
            placed.append(p); m = Moth(TEMP, 0.7, 130 + k); k += 1
            m.place(p, look_rot(p, ROCK)); m.flap(1, n, speed=1.0, amp=0.08, base=0.25); ms.append((m, p))
            for f in range(1, n + 1, 2):
                sw = 0.35 * math.sin(f / 24 * 2 * math.pi * 0.9) if sway else 0.0
                m.root.rotation_euler = (0, sw * 0.35, look_rot(p, ROCK)); m.root.keyframe_insert("rotation_euler", frame=f)
                m.head.rotation_euler = (-0.5, sw, 0); m.head.keyframe_insert("rotation_euler", frame=f)
    return ms
def s52(n):   # edge of town: moths sitting in neat rows around the rock, staring up at the beam
    show_set("edge"); snowon(n); flrock()
    concert(n)
    tgt = ROCK + Vector((0, -2, 4.0))
    cpath(n, ROCK + Vector((-15, -19, 7)), ROCK + Vector((0, -6, 1.5)), ROCK + Vector((-13, -17, 6.5)), ROCK + Vector((0, -5, 2.5)), 26, 27)
def s53(n):   # antennae sway in unison; one crowd-surfs over the others
    show_set("edge"); snowon(n); flrock()
    ms = concert(n, sway=True)
    surf = Moth(TEMP, 0.7, 200); surf.flap(1, n, speed=0.8, amp=0.1, base=0.0)
    light("surfl", "POINT", ROCK + Vector((0, -12, 7)), 700, (1, 0.85, 0.6), coll=TEMP, radius=1).data.use_shadow = False
    a0 = ROCK + Vector((-11, -12.5, 3.6)); a1 = ROCK + Vector((0.6, -12.5, 3.6))   # ends centre-frame: last thing on screen
    for f in range(1, n + 1):
        u = 1 - (1 - min(1, f / (n * 0.8))) ** 2; surf.root.location = a0.lerp(a1, u) + Vector((0, 0, 0.2 * math.sin(f / 3))); surf.root.rotation_euler = (math.pi, 0, 0.4 * math.sin(f / 5))
        surf.root.keyframe_insert("location", frame=f); surf.root.keyframe_insert("rotation_euler", frame=f)
    tgt = ROCK + Vector((0, -7, 2.0))
    cpath(n, tgt + Vector((3, -14, 3.4)), tgt + Vector((0, 2, 0)), tgt + Vector((2.4, -12.5, 3.0)), tgt + Vector((0, 2, 0)), 28, 30)

# ---------------------------------------------------------------- render loop
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
STATIC = [SPIDER_ARM, STAR] + list(STAR.children)
def reset_mats():
    for m in bpy.data.materials:
        nt = m.node_tree if m.use_nodes else None
        if nt and nt.animation_data: nt.animation_data_clear()
        if nt and "base_em" in m: nt.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = m["base_em"]
        if nt and "base_col" in m: nt.nodes["Principled BSDF"].inputs["Base Color"].default_value = list(m["base_col"])
    for L in bpy.data.lights:
        if L.animation_data: L.animation_data_clear()
        if "base" in L: pass
    for L in TREE_LIGHTS:
        if "base" in L: L.data.energy = L["base"]
for name in TL["shots"]:
    if ONLY and name not in ONLY: continue
    n = max(6, int(round(DUR[name] * FPS)))
    clear_temp(); reset_mats(); S.frame_set(1)
    for o in STATIC:
        if o.animation_data: o.animation_data_clear()
        o.hide_render = False
    TRACK.clear(); SHOTS[name](n)
    S.frame_start, S.frame_end = 1, n
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    json.dump(track_json(n), open(f"{d}/track.json", "w"))
    if STILL:
        SF = float(os.environ.get("STILLF", "0.6")); S.frame_set(max(1, int(n * SF))); S.render.filepath = f"{E}/preview/{name}" + ("" if SF == 0.6 else f"_{int(SF*100)}") + ".png"; bpy.ops.render.render(write_still=True)
    else:
        for f in os.listdir(d):
            if f.endswith(".png"): os.remove(os.path.join(d, f))
        S.render.filepath = f"{d}/"; bpy.ops.render.render(animation=True)
        json.dump({"n": n}, open(f"{d}/info.json", "w"))
    print("DONE", name, n, flush=True)
