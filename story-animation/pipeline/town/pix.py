"""Stylised feature-animation characters (procedural, EEVEE): big expressive eyes with lids/brows, sculpted-ish
smooth bodies, layered clothes, curly hair from sphere clusters. Rig = empties; expressions = keyframed lids/brows/mouth.
Units: metres. Kid ~1.6 m. Characters face -Y in rest pose."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler

S = bpy.context.scene
_M, _ME = {}, {}

def srgb(c):  # 0-255 sRGB -> linear
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(f(v) for v in c)

def pmat(name, col, rough=0.5, sss=0.0, metal=0.0, emit=None, estr=1.0, sheen=0.0, coat=0.0, alpha=1.0):
    key = (name, tuple(round(c, 4) for c in col), rough, sss, metal, emit, estr)
    if key in _M: return _M[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss; b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.03
    if sheen: b.inputs["Sheen Weight"].default_value = sheen
    if coat: b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    m.diffuse_color = (*col, 1)
    _M[key] = m; return m

def coll_new(name, parent=None):
    c = bpy.data.collections.new(name); (parent or S.collection).children.link(c); return c

def _mesh(key, build):
    if key in _ME: return _ME[key]
    me = bpy.data.meshes.new(str(key)); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    _ME[key] = me; return me

def obj(name, me, m, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, coll=None, sub=0):
    me2 = me.copy() if m is not None else me
    if m is not None:
        me2.materials.clear(); me2.materials.append(m)
    o = bpy.data.objects.new(name, me2); (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    if parent: o.parent = parent
    if sub:
        md = o.modifiers.new("sub", "SUBSURF"); md.levels = 1; md.render_levels = sub
    return o

def empty(name, loc=(0, 0, 0), parent=None, coll=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def ell(name, loc, rad, m, parent=None, coll=None, rot=(0, 0, 0), seg=32):
    me = _mesh(("sph", seg), lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1))
    return obj(name, me, m, loc, rot, rad, parent, coll)
def half(name, loc, rad, m, parent=None, coll=None, rot=(0, 0, 0)):
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.01], context="VERTS")
    return obj(name, _mesh("half", b), m, loc, rot, rad, parent, coll)
def rbox(name, loc, size, m, parent=None, coll=None, rot=(0, 0, 0), bev=0.3, sub=2):
    """pillowy rounded box: bevelled cube + subdivision; bev = fraction of the smallest side"""
    sz = tuple(round(v, 4) for v in size); bv = round(min(sz) * bev, 4)
    def b(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co = Vector((v.co.x * sz[0], v.co.y * sz[1], v.co.z * sz[2]))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bv, segments=3, affect="EDGES", profile=0.5)
    return obj(name, _mesh(("rbox", sz, bv), b), m, loc, rot, (1, 1, 1), parent, coll, sub=sub)
def cylr(name, loc, r, depth, m, parent=None, coll=None, rot=(0, 0, 0), verts=24, r2=None):
    me = _mesh(("cyl", verts, r2), lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=1, radius2=(r2 if r2 is not None else 1), depth=1))
    return obj(name, me, m, loc, rot, (r, r, depth), parent, coll)
def torus(name, loc, R, r, m, parent=None, coll=None, rot=(0, 0, 0), seg=32):
    def b(bm):
        vs = []
        for i in range(seg):
            a = i / seg * 2 * math.pi; ring = []
            for j in range(10):
                c = j / 10 * 2 * math.pi
                ring.append(bm.verts.new((math.cos(a) * (1 + r / R * math.cos(c)), math.sin(a) * (1 + r / R * math.cos(c)), r / R * math.sin(c))))
            vs.append(ring)
        for i in range(seg):
            for j in range(10):
                bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % 10], vs[i][(j + 1) % 10]))
    return obj(name, _mesh(("torus", round(r / R, 3), seg), b), m, loc, rot, (R, R, R), parent, coll)
def limb(name, a, b, r, m, parent=None, coll=None, r2=None):
    """tapered capsule from local point a to b"""
    a, b = Vector(a), Vector(b); d = b - a; L = d.length; r2 = r2 or r
    piv = empty(name + "_p", a, parent, coll); piv.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    cylr(name, (0, 0, L / 2), 1, L, m, parent=piv, coll=coll, verts=20, r2=r2 / r).scale = (r, r, L)
    ell(name + "_e1", (0, 0, 0), (r, r, r), m, parent=piv, coll=coll, seg=20)
    ell(name + "_e2", (0, 0, L), (r2, r2, r2), m, parent=piv, coll=coll, seg=20)
    return piv

def kf(o, path, f, v=None, idx=-1):
    if v is not None: setattr(o, path, v)
    o.keyframe_insert(path, frame=f, index=idx)

def _head_mesh(bm):
    """one smooth head: round cranium, full cheeks, soft narrowing jaw, slight forward chin (no seams)"""
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=1)
    for v in bm.verts:
        x, y, z = v.co
        low = max(0.0, -z); front = max(0.0, -y)
        x *= 1 + 0.10 * math.sin(min(1, low * 1.6) * math.pi) - 0.28 * max(0, low - 0.55) ** 1.2
        y *= 1 - 0.18 * max(0, low - 0.5) * (1 - front) - 0.06 * max(0, y)
        y -= 0.07 * front * math.sin(min(1, low * 1.4) * math.pi)
        z *= 1 + 0.02 * front
        v.co = Vector((x * 0.155, y * 0.15, z * 0.172))

# ---------------------------------------------------------------- the character
EXPR = {  # lid (deg, + = closing), brow (rot, z-lift), mouth (width, open), smile (1 = D smile, 0 = round/flat)
    "neutral": dict(lid=-8, lidl=0, brow=(0.0, 0.0), mouth=(0.8, 0.15), smile=1),
    "happy": dict(lid=-2, lidl=-10, brow=(0.1, 0.006), mouth=(1.25, 0.55), smile=1),
    "grin": dict(lid=4, lidl=-20, brow=(0.15, 0.008), mouth=(1.5, 0.75), smile=1),
    "shock": dict(lid=-35, lidl=0, brow=(0.25, 0.022), mouth=(0.75, 1.15), smile=0),
    "scared": dict(lid=-28, lidl=0, brow=(0.45, 0.015), mouth=(1.1, 0.45), smile=0),
    "worried": dict(lid=-10, lidl=0, brow=(0.5, 0.01), mouth=(0.7, 0.2), smile=0),
    "angry": dict(lid=10, lidl=-12, brow=(-0.45, -0.01), mouth=(1.0, 0.3), smile=0),
    "smirk": dict(lid=12, lidl=-8, brow=(-0.1, 0.0), mouth=(0.9, 0.18), smile=1),
    "blink": dict(lid=88, lidl=-20, brow=(0.0, 0.0), mouth=(0.8, 0.15), smile=1),
    "talk": dict(lid=-8, lidl=0, brow=(0.08, 0.006), mouth=(0.95, 0.8), smile=0),
    "laugh": dict(lid=40, lidl=-30, brow=(0.2, 0.01), mouth=(1.5, 1.0), smile=1),
}

class Kid:
    def __init__(self, name, coll, skin, hair_fn, outfit_fn, height=1.6, build=1.0, iris=(0.12, 0.06, 0.025), extra=None, hair_col=(0.02, 0.012, 0.008)):
        self.name, self.coll = name, coll; self.build = build
        sk = pmat(f"skin{name}", skin, 0.45, sss=0.25); self.skinm = sk
        s = height / 1.6; self.s = s
        self.root = empty(name, coll=coll); self.root.scale = (s, s, s)
        self.hips = empty("hips", (0, 0, 0.84), self.root, coll)
        self.spine = empty("spine", (0, 0, 0.0), self.hips, coll)
        self.chest = empty("chest", (0, 0, 0.22), self.spine, coll)
        self.neck = empty("neck", (0, 0, 0.25), self.chest, coll)
        self.headp = empty("headp", (0, 0, 0.035), self.neck, coll)
        H = self.headp; hc = Vector((0, 0, 0.15)); H.scale = (1.36, 1.36, 1.36)
        # head: soft rounded, fuller cheeks
        self.head = obj("head", _mesh("pixhead", _head_mesh), sk, hc, (0, 0, 0), (1, 1, 1), H, coll, sub=1)
        ell("nose", hc + Vector((0, -0.158, -0.025)), (0.024, 0.024, 0.022), sk, H, coll, seg=24)
        for sx in (-1, 1): ell("ear", hc + Vector((sx * 0.152, 0.01, -0.01)), (0.022, 0.03, 0.042), sk, H, coll, seg=20)
        ell("neckm", (0, 0, 0.0), (0.066, 0.06, 0.08), sk, self.neck, coll, seg=20)
        # eyes
        white = pmat("sclera", (0.92, 0.92, 0.9), 0.15, coat=0.5); irm = pmat(f"iris{iris}", iris, 0.2, coat=1.0); pup = pmat("pupil", (0.005, 0.005, 0.005), 0.1, coat=1.0)
        glint = pmat("glint", (1, 1, 1), 0.1, emit=(1, 1, 1), estr=3.0)
        self.eyes, self.lids, self.lowlids, self.brows = [], [], [], []
        brm = pmat(f"brow{hair_col}", hair_col, 0.8)
        for sx in (-1, 1):
            ec = hc + Vector((sx * 0.062, -0.098, 0.012))
            sock = empty("eyesock", ec, H, coll)
            e = empty("eye", (0, 0, 0), sock, coll); r = 0.047
            ell("sclera", (0, 0, 0), (r, r, r * 1.08), white, e, coll, seg=32)
            ell("iris", (0, -r * 0.82, 0), (r * 0.62, r * 0.32, r * 0.64), irm, e, coll, seg=32)
            ell("pupil", (0, -r * 0.97, 0), (r * 0.33, r * 0.2, r * 0.35), pup, e, coll, seg=24)
            ell("glint", (sx * -r * 0.18 + r * 0.12, -r * 1.06, r * 0.28), (r * 0.13, r * 0.05, r * 0.13), glint, e, coll, seg=12)
            lp = empty("lidp", (0, 0, 0), sock, coll); half("lid", (0, 0, 0), (r * 1.035, r * 1.035, r * 1.12), sk, lp, coll)
            lp2 = empty("lidlp", (0, 0, 0), sock, coll); half("lidl", (0, 0, 0), (r * 1.03, r * 1.03, r * 1.08), sk, lp2, coll, rot=(math.pi, 0, 0))
            self.eyes.append(e); self.lids.append(lp); self.lowlids.append(lp2)
            bp = empty("browp", hc + Vector((sx * 0.064, -0.142, 0.083)), H, coll)
            ell("brow", (0, 0, 0), (0.04, 0.012, 0.014), brm, bp, coll, rot=(0.25, 0, 0), seg=20)
            bp["sx"] = sx; self.brows.append(bp)
        # mouth: D-shaped dark interior + teeth + tongue, in a scalable group
        self.mouth = empty("mouth", hc + Vector((0, -0.137, -0.083)), H, coll); self.mouth.rotation_euler = (0.25, 0, 0); self.mouth.scale = (1.3, 1.0, 1.15)
        inner = pmat("mouthin", (0.16, 0.02, 0.03), 0.6); teeth = pmat("teeth", (0.95, 0.94, 0.9), 0.25); tng = pmat("tongue", (0.75, 0.2, 0.22), 0.5)
        self.m_smile = empty("msmile", (0, 0, 0), self.mouth, coll)
        half("mD", (0, 0.004, 0), (0.045, 0.013, 0.035), inner, self.m_smile, coll, rot=(math.pi, 0, 0))
        rbox("mteeth", (0, -0.012, -0.004), (0.062, 0.012, 0.012), teeth, self.m_smile, coll, bev=0.4, sub=1)
        ell("mtongue", (0, -0.004, -0.026), (0.026, 0.012, 0.01), tng, self.m_smile, coll, seg=16)
        self.m_round = empty("mround", (0, 0, -0.008), self.mouth, coll)
        ell("mO", (0, 0, 0), (0.03, 0.014, 0.034), inner, self.m_round, coll, seg=24)
        # body
        outfit_fn(self); hair_fn(self)
        if extra: extra(self)
        self.set_expr("neutral", 1)

    # arms/legs are built by outfit (sleeve colours) via these helpers
    def make_arms(self, sleeve_m, wide=0.062, hand_m=None, cuff_m=None):
        self.arms, self.fores = [], []
        hm = hand_m or self.skinm
        for sx in (-1, 1):
            sh = empty("shoulder", (sx * 0.19 * self.build, 0, 0.2), self.chest, self.coll)
            limb("uarm", (0, 0, 0), (0, 0, -0.27), wide, sleeve_m, sh, self.coll, r2=wide * 0.92)
            el = empty("elbow", (0, 0, -0.27), sh, self.coll)
            limb("farm", (0, 0, 0), (0, 0, -0.22), wide * 0.92, sleeve_m, el, self.coll, r2=wide * 0.85)
            if cuff_m: cylr("cuff", (0, 0, -0.225), wide * 0.88, 0.035, cuff_m, el, self.coll)
            hd = empty("hand", (0, 0, -0.27), el, self.coll)
            ell("palm", (0, 0, 0.0), (0.056, 0.036, 0.062), hm, hd, self.coll, seg=20)
            ell("thumb", (-sx * 0.045, -0.025, 0.012), (0.02, 0.02, 0.034), hm, hd, self.coll, rot=(0, sx * 0.5, 0), seg=12)
            for k in range(4): ell("finger", (-0.034 + k * 0.0225, 0, -0.062), (0.0125, 0.0135, 0.03), hm, hd, self.coll, seg=10)
            sh.rotation_euler = (0, -sx * 0.12, 0); el.rotation_euler = (-0.15, 0, 0)
            self.arms.append(sh); self.fores.append(el)
    def make_legs(self, pant_m, shoe_m, sole_m, wide=0.075, baggy=1.0, lace_m=None):
        self.legs, self.knees = [], []
        for sx in (-1, 1):
            hp = empty("hipj", (sx * 0.085, 0, -0.02), self.hips, self.coll)
            limb("thigh", (0, 0, 0), (0, 0, -0.4), wide * 1.05 * baggy, pant_m, hp, self.coll, r2=wide * baggy)
            kn = empty("knee", (0, 0, -0.4), hp, self.coll)
            limb("shin", (0, 0, 0), (0, 0, -0.36), wide * baggy, pant_m, kn, self.coll, r2=wide * 1.08 * baggy)
            ft = empty("foot", (0, 0, -0.4), kn, self.coll)
            rbox("shoe", (0, -0.05, 0.015), (0.14, 0.3, 0.12), shoe_m, ft, self.coll, bev=0.45)
            rbox("sole", (0, -0.05, -0.04), (0.15, 0.315, 0.05), sole_m, ft, self.coll, bev=0.4)
            rbox("tongue", (0, 0.02, 0.08), (0.08, 0.1, 0.06), shoe_m, ft, self.coll, bev=0.45)
            if lace_m: rbox("swoosh", (sx * 0.071, -0.04, 0.01), (0.006, 0.15, 0.045), lace_m, ft, self.coll, bev=0.4, sub=1)
            self.legs.append(hp); self.knees.append(kn)

    # ---- animation API
    def place(self, loc, rotz=0.0, f=1):
        self.root.location = loc; self.root.rotation_euler = (0, 0, rotz); kf(self.root, "location", f); kf(self.root, "rotation_euler", f)
    def move(self, f, loc, rotz=None):
        self.root.location = loc; kf(self.root, "location", f)
        if rotz is not None: self.root.rotation_euler = (0, 0, rotz); kf(self.root, "rotation_euler", f)
    def pose(self, f, arms=((0, 0.12, 0), (0, -0.12, 0)), elbows=(0.15, 0.15), legs=(0, 0), knees=(0, 0), hipz=0.84, lean=0.0, twist=0.0,
             head=(0, 0, 0), chest=(0, 0, 0), hipx=0.0):
        """arms: per side (forward-raise, out-raise, twist) radians. elbows: bend. legs: forward swing; knees: bend"""
        for i, a in enumerate(self.arms):
            sx = -1 if i == 0 else 1
            fw, out, tw = arms[i]
            a.rotation_euler = (-fw, -sx * (0.12 + out), tw * sx); kf(a, "rotation_euler", f)
            self.fores[i].rotation_euler = (-elbows[i], 0, 0); kf(self.fores[i], "rotation_euler", f)
        for i, l in enumerate(self.legs):
            l.rotation_euler = (-legs[i], 0, 0); kf(l, "rotation_euler", f)
            self.knees[i].rotation_euler = (knees[i], 0, 0); kf(self.knees[i], "rotation_euler", f)
        self.hips.location = (hipx, 0, hipz); kf(self.hips, "location", f)
        self.spine.rotation_euler = (lean, 0, twist); kf(self.spine, "rotation_euler", f)
        self.chest.rotation_euler = chest; kf(self.chest, "rotation_euler", f)
        self.neck.rotation_euler = head; kf(self.neck, "rotation_euler", f)
    def gaze(self, f, x=0.0, z=0.0):
        for e in self.eyes: e.rotation_euler = (-z, 0, x); kf(e, "rotation_euler", f)
    def set_expr(self, name, f, hold=True):
        p = EXPR[name]
        for i, lp in enumerate(self.lids):
            lp.rotation_euler = (math.radians(-55 + p["lid"] * 1.6), 0, 0); kf(lp, "rotation_euler", f)
            self.lowlids[i].rotation_euler = (math.radians(60 + p["lidl"]), 0, 0); kf(self.lowlids[i], "rotation_euler", f)
        for bp in self.brows:
            sx = bp["sx"]; r, dz = p["brow"]
            bp.rotation_euler = (0, sx * r, 0); bp.location.z = 0.15 + 0.083 + dz; kf(bp, "rotation_euler", f); kf(bp, "location", f, idx=2)
        w, op = p["mouth"]
        if p["smile"]:
            self.m_smile.scale = (w, 1, max(0.08, op)); self.m_round.scale = (0.001, 0.001, 0.001)
        else:
            self.m_smile.scale = (0.001, 0.001, 0.001); self.m_round.scale = (w, 1, max(0.1, op))
        kf(self.m_smile, "scale", f); kf(self.m_round, "scale", f)
        self._last = name
    def blink(self, f, base):
        self.set_expr(base, f - 1); self.set_expr("blink", f + 1); self.set_expr(base, f + 3)
    def talk(self, words, base, fps=24, t0=0, t1=99):
        for w, a, b in words:
            if t0 <= a < t1:
                fa = int(a * fps) + 1; fb = max(fa + 2, int(b * fps))
                self.set_expr("talk", fa); self.set_expr(base, fb)
    def idle(self, f0, f1, energy=1.0, seed=0, arms=None, base_lean=0.0, breathe=1.0):
        rnd = random.Random(seed); ph = rnd.uniform(0, 6)
        for f in range(f0, f1 + 1, 2):
            t = f / 24 + ph
            self.pose(f, arms=arms or ((0.05 * math.sin(t * 1.3) * energy, 0.12, 0), (-0.05 * math.sin(t * 1.3) * energy, 0.12, 0)),
                      hipz=0.84 + 0.006 * math.sin(t * 2.2) * breathe, lean=base_lean + 0.02 * math.sin(t * 0.9) * energy,
                      head=(0.04 * math.sin(t * 1.1) * energy, 0, 0.08 * math.sin(t * 0.7) * energy), chest=(0.015 * math.sin(t * 2.2) * breathe, 0, 0))
    def walk(self, f0, f1, a, b, run=False, stride=None):
        a, b = Vector(a), Vector(b); d = b - a; rotz = math.atan2(d.y, d.x) + math.pi / 2
        cad = 2.6 if run else 1.7; amp = 0.75 if run else 0.42
        for f in range(f0, f1 + 1):
            u = (f - f0) / max(1, f1 - f0); self.move(f, a + d * u, rotz)
            ph = (f - f0) / 24 * cad * 2 * math.pi; s = math.sin(ph)
            self.pose(f, arms=((-s * amp, 0.1, 0), (s * amp, 0.1, 0)), elbows=(0.4 + (0.6 if run else 0.1), 0.4 + (0.6 if run else 0.1)),
                      legs=(s * amp, -s * amp), knees=(max(0, -math.cos(ph)) * 0.6 + 0.1, max(0, math.cos(ph)) * 0.6 + 0.1),
                      hipz=0.84 + abs(math.cos(ph)) * (0.05 if run else 0.02), lean=(0.18 if run else 0.04), head=(-0.05 if run else 0, 0, 0))

# ---------------------------------------------------------------- hair kits
def scalp(name, k, m, front=0.42, low=-0.12, grow=1.04, side=0.0):
    """hair shell that follows the head but stops at a hairline (keeps the face clear)"""
    key = ("scalp", front, low, side)
    def bld(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1)
        dead = [v for v in bm.verts if (v.co.y < -0.15 and v.co.z < front) or v.co.z < low or (abs(v.co.x) > 0.8 and v.co.z < side)]
        bmesh.ops.delete(bm, geom=dead, context="VERTS")
    o = obj(name, _mesh(key, bld), m, (0, 0.006, 0.15 + 0.008), (0, 0, 0), (0.155 * grow, 0.15 * grow, 0.172 * grow), k.headp, k.coll)
    sol = o.modifiers.new("solid", "SOLIDIFY"); sol.thickness = 0.01
    return o
def curls(k, col, top=True, fade=True, volume=1.0, seed=1, r=0.026, extent=1.0):
    m = pmat(f"hair{col}", col, 0.75, sheen=0.4); rnd = random.Random(seed); H = k.headp; hc = Vector((0, 0, 0.15))
    if fade: scalp("fade", k, pmat(f"fade{col}", tuple(c * 0.9 for c in col), 0.9), front=0.5, low=-0.05, grow=1.015, side=0.25)
    n = int(160 * volume * extent)
    for i in range(n):
        u = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(0.0, 1.0) ** 0.8 * 1.05 * extent
        x = math.sin(v) * math.cos(u); y = math.sin(v) * math.sin(u); z = math.cos(v)
        if y < -0.35 and z < 0.75: continue      # keep the forehead clear
        rr = r * rnd.uniform(0.75, 1.25); push = 1.0 + 0.12 * volume
        ell("curl", hc + Vector((x * 0.158 * push, y * 0.152 * push + 0.01, z * 0.175 * push + 0.03 * volume)), (rr, rr, rr), m, H, k.coll, seg=12)
def hair_jayden(k): curls(k, srgb((28, 20, 16)), volume=1.25, seed=3, r=0.03, extent=1.0)
def hair_tyrone(k): curls(k, srgb((22, 16, 12)), volume=0.8, seed=5, r=0.024, extent=0.95)
def hair_maya(k):
    col = srgb((92, 52, 30)); m = pmat("hairmaya", col, 0.7, sheen=0.5); hc = Vector((0, 0, 0.15)); H = k.headp; rnd = random.Random(8)
    scalp("mcap", k, m, front=0.45, low=-0.35, grow=1.06, side=0.0)
    ell("mpart", hc + Vector((0.0, -0.06, 0.13)), (0.12, 0.09, 0.05), m, H, k.coll, rot=(0.3, 0, 0), seg=24)
    ell("mvol", hc + Vector((0, 0.06, -0.12)), (0.19, 0.12, 0.3), m, H, k.coll, seg=32)
    for i in range(420):   # long curly mane over the shoulders
        a = rnd.uniform(-2.0, 2.0); zz = rnd.uniform(-0.45, 0.16); rad = 0.165 + 0.04 * (1 - (zz + 0.45) / 0.61) + rnd.uniform(-0.015, 0.015)
        x = math.sin(a) * rad; y = math.cos(a) * rad * 0.75 + 0.03
        if y < 0.0 and zz > -0.12: continue
        rr = rnd.uniform(0.018, 0.03); ell("mcurl", hc + Vector((x, y, zz)), (rr, rr, rr * 1.3), m, H, k.coll, seg=10)
    ell("bun", hc + Vector((0.0, 0.08, 0.17)), (0.07, 0.065, 0.06), m, H, k.coll, seg=24)
    torus("scrunchie", hc + Vector((0.0, 0.075, 0.13)), 0.045, 0.014, pmat("scrunch", srgb((220, 60, 150)), 0.6), H, k.coll, rot=(0.6, 0, 0))
    gold = pmat("gold", srgb((240, 190, 60)), 0.2, metal=1.0)
    for sx in (-1, 1): torus("hoop", hc + Vector((sx * 0.158, 0.0, -0.075)), 0.034, 0.004, gold, H, k.coll, rot=(0, math.pi / 2, 0))
def hair_leo(k):
    col = srgb((112, 64, 34)); m = pmat("hairleo", col, 0.7, sheen=0.4); hc = Vector((0, 0, 0.15)); H = k.headp; rnd = random.Random(2)
    scalp("lcap", k, m, front=0.5, low=-0.1, grow=1.05, side=0.2)
    for i in range(26):
        a = rnd.uniform(-1.3, 1.3); x = math.sin(a) * 0.11; y = -0.06 + rnd.uniform(-0.03, 0.12)
        ell("tuft", hc + Vector((x, y, 0.16 + rnd.uniform(0, 0.03))), (0.035, 0.07, 0.028), m, H, k.coll, rot=(rnd.uniform(-0.9, -0.4), rnd.uniform(-0.4, 0.4), a * 0.4), seg=16)
def hair_rico(k):
    col = srgb((30, 22, 18)); hc = Vector((0, 0, 0.15)); H = k.headp
    scalp("rcap0", k, pmat("hairrico", col, 0.8), front=0.45, low=-0.1, grow=1.02, side=0.15)
    cap = pmat("capblk", srgb((24, 24, 28)), 0.55)
    half("cap", hc + Vector((0, 0.0, 0.045)), (0.172, 0.17, 0.15), cap, H, k.coll)
    rbox("brim", hc + Vector((0, 0.17, 0.06)), (0.2, 0.15, 0.018), cap, H, k.coll, rot=(-0.25, 0, 0), bev=0.4)
    torus("capstrap", hc + Vector((0, 0.13, 0.05)), 0.035, 0.008, pmat("capstrap", srgb((60, 60, 66)), 0.4), H, k.coll, rot=(math.pi / 2, 0, 0))
    for sx in (-1, 1): ell("sideburn", hc + Vector((sx * 0.15, 0.03, 0.0)), (0.012, 0.05, 0.06), pmat("hairrico", col, 0.8), H, k.coll)

# ---------------------------------------------------------------- outfits
def cargo_pants(k, col, shoe, sole, lace=None, baggy=1.2):
    pm = pmat(f"pants{col}", col, 0.85, sheen=0.2)
    k.make_legs(pm, pmat(f"shoe{shoe}", shoe, 0.45), pmat(f"sole{sole}", sole, 0.5), baggy=baggy, lace_m=pmat(f"lace{lace}", lace, 0.4) if lace else None)
    for i, l in enumerate(k.legs):
        rbox("pocket", ((-1 if i == 0 else 1) * 0.085, 0.0, -0.26), (0.045, 0.1, 0.1), pm, l, k.coll, bev=0.3, sub=1)
    rbox("pelvis", (0, 0, -0.02), (0.27 * k.build, 0.17 * k.build, 0.16), pm, k.hips, k.coll, bev=0.45)
def puffer(k, col, inner, hood_col, tee=None):
    m = pmat(f"puff{col}", col, 0.32, coat=0.3); C = k.chest; b = k.build
    rbox("pcore", (0, 0, 0.0), (0.37 * b, 0.22 * b, 0.44), m, C, k.coll, bev=0.4)
    for j in range(5):
        rbox("pband", (0, 0, -0.19 + j * 0.095), (0.41 * b, 0.26 * b, 0.115), m, C, k.coll, bev=0.48)
    rbox("pcollar", (0, 0.02, 0.24), (0.27, 0.2, 0.08), m, C, k.coll, bev=0.45)
    hm = pmat(f"hood{hood_col}", hood_col, 0.85, sheen=0.3)
    rbox("hoodie_hood", (0, 0.11, 0.25), (0.26, 0.12, 0.13), hm, C, k.coll, bev=0.45)
    rbox("hoodie_front", (0, -0.125 * b, 0.1), (0.1, 0.02, 0.2), hm, C, k.coll, bev=0.3, sub=1)
    rbox("zip", (0, -0.133 * b, -0.02), (0.012, 0.01, 0.4), pmat("zip", srgb((90, 90, 96)), 0.3, metal=0.8), C, k.coll, bev=0.3, sub=0)
    for sx in (-0.025, 0.025): cylr("string", (sx, -0.13 * b, 0.13), 0.006, 0.12, pmat("white", (0.9, 0.9, 0.9), 0.5), C, k.coll, verts=8)
    k.make_arms(m, wide=0.068 * b, cuff_m=pmat(f"puffc{col}", tuple(c * 0.6 for c in col), 0.5))
def hoodie_top(k, col, crop=False, jacket=None, jacket_open=True):
    m = pmat(f"hoodie{col}", col, 0.85, sheen=0.35); C = k.chest; b = k.build
    rbox("torso", (0, 0, 0.0 if not crop else 0.05), (0.36 * b, 0.22 * b, 0.42 if not crop else 0.32), m, C, k.coll, bev=0.42)
    rbox("hood", (0, 0.1 * b, 0.21), (0.26, 0.11, 0.12), m, C, k.coll, bev=0.45)
    rbox("kanga", (0, -0.11 * b, -0.12 if not crop else -0.02), (0.22 * b, 0.02, 0.1), m, C, k.coll, bev=0.3, sub=1)
    for sx in (-0.03, 0.03): cylr("string", (sx, -0.115 * b, 0.12), 0.006, 0.12, pmat("white", (0.9, 0.9, 0.9), 0.5), C, k.coll, verts=8)
    if crop: rbox("midriff", (0, 0, -0.16), (0.31, 0.19, 0.1), k.skinm, C, k.coll, bev=0.45)
    sleeve = m
    if jacket:
        jm = pmat(f"jacket{jacket}", jacket, 0.7, sheen=0.2)
        for sx in (-1, 1):
            rbox("jpanel", (sx * 0.12 * b, -0.01, 0.0), (0.14 * b, 0.235 * b, 0.43), jm, C, k.coll, bev=0.35)
        rbox("jback", (0, 0.04, 0.0), (0.37 * b, 0.16 * b, 0.43), jm, C, k.coll, bev=0.35)
        rbox("jcollar", (0, 0.03, 0.22), (0.3, 0.22, 0.05), jm, C, k.coll, bev=0.45)
        sleeve = jm
    k.make_arms(sleeve, wide=0.058 * b, cuff_m=pmat(f"cuff{col}", tuple(c * 0.7 for c in sleeve.diffuse_color[:3]), 0.7))
def glasses(k):
    fr = pmat("frames", srgb((25, 22, 20)), 0.3); hc = Vector((0, 0, 0.15)); H = k.headp
    for sx in (-1, 1): torus("rim", hc + Vector((sx * 0.062, -0.155, 0.012)), 0.05, 0.006, fr, H, k.coll, rot=(math.pi / 2, 0, 0))
    cylr("bridge", hc + Vector((0, -0.16, 0.022)), 0.005, 0.03, fr, H, k.coll, rot=(0, math.pi / 2, 0), verts=8)
    for sx in (-1, 1): cylr("arm", hc + Vector((sx * 0.13, -0.08, 0.015)), 0.004, 0.16, fr, H, k.coll, rot=(math.pi / 2, 0, 0), verts=6)

# ---------------------------------------------------------------- the cast
def mk_jayden(coll):
    def outfit(k):
        cargo_pants(k, srgb((30, 30, 34)), srgb((245, 245, 245)), srgb((240, 240, 240)), lace=srgb((20, 20, 22)))
        puffer(k, srgb((26, 27, 32)), srgb((235, 235, 235)), srgb((140, 140, 146)), tee=srgb((240, 240, 240)))
    return Kid("jayden", coll, srgb((120, 72, 44)), hair_jayden, outfit, 1.62, 1.0, iris=srgb((70, 40, 20)), hair_col=srgb((25, 18, 14)))
def mk_maya(coll):
    def outfit(k):
        cargo_pants(k, srgb((80, 105, 150)), srgb((245, 245, 245)), srgb((235, 90, 170)), lace=srgb((230, 70, 160)), baggy=1.3)
        hoodie_top(k, srgb((215, 60, 150)), crop=True)
    return Kid("maya", coll, srgb((196, 140, 105)), hair_maya, outfit, 1.58, 0.95, iris=srgb((95, 55, 25)), hair_col=srgb((70, 40, 24)))
def mk_leo(coll):
    def outfit(k):
        cargo_pants(k, srgb((70, 72, 76)), srgb((30, 30, 32)), srgb((240, 240, 240)), lace=srgb((245, 245, 245)))
        hoodie_top(k, srgb((175, 175, 180)), jacket=srgb((60, 85, 140)))
    return Kid("leo", coll, srgb((236, 190, 160)), hair_leo, outfit, 1.55, 0.95, iris=srgb((90, 60, 35)), hair_col=srgb((100, 58, 30)))
def mk_tyrone(coll):
    def outfit(k):
        cargo_pants(k, srgb((28, 28, 30)), srgb((120, 190, 140)), srgb((240, 240, 240)), lace=srgb((40, 120, 70)), baggy=1.35)
        hoodie_top(k, srgb((30, 110, 70)))
    return Kid("tyrone", coll, srgb((88, 52, 32)), hair_tyrone, outfit, 1.7, 1.35, iris=srgb((50, 30, 18)), extra=glasses, hair_col=srgb((22, 16, 12)))
def mk_rico(coll):
    def outfit(k):
        cargo_pants(k, srgb((26, 26, 28)), srgb((30, 30, 32)), srgb((240, 240, 240)), lace=srgb((245, 245, 245)))
        hoodie_top(k, srgb((28, 28, 32)), jacket=srgb((20, 20, 24)))
    return Kid("rico", coll, srgb((214, 160, 120)), hair_rico, outfit, 1.6, 0.98, iris=srgb((80, 50, 30)), hair_col=srgb((30, 22, 18)))

# ---------------------------------------------------------------- Whiskers (tabby, big attitude)
class Cat:
    def __init__(self, coll, scale=1.0, crown=False):
        self.coll = coll
        fur = pmat("tabby", srgb((150, 120, 90)), 0.85, sheen=0.6); white = pmat("catwhite", srgb((240, 236, 228)), 0.85, sheen=0.6)
        dark = pmat("tabbydk", srgb((60, 45, 35)), 0.85, sheen=0.5)
        self.root = empty("whiskers", coll=coll); self.root.scale = (scale,) * 3
        self.body = empty("cbody", (0, 0, 0.16), self.root, coll)
        ell("ctorso", (0, 0.05, 0.02), (0.1, 0.16, 0.1), fur, self.body, coll)
        ell("cchest", (0, -0.07, 0.04), (0.075, 0.06, 0.09), white, self.body, coll)
        for k in range(4): ell("stripe", (0, 0.0 + k * 0.05, 0.1), (0.07, 0.012, 0.03), dark, self.body, coll, rot=(0.2, 0, 0))
        self.legs = []
        for sx in (-1, 1):
            for sy in (-0.05, 0.15):
                l = empty("cleg", (sx * 0.05, sy, -0.02), self.body, coll)
                limb("cl", (0, 0, 0), (0, 0, -0.13), 0.025, fur, l, coll); ell("paw", (0, -0.01, -0.14), (0.03, 0.035, 0.018), white, l, coll)
                self.legs.append(l)
        self.tail = []; prev = empty("tail0", (0, 0.2, 0.05), self.body, coll)
        for k in range(8):
            seg = empty("tseg", (0, 0.035 if k else 0, 0.03 if k else 0), prev, coll); seg.rotation_euler = (-0.18, 0, 0)
            ell("tail", (0, 0, 0), (0.02, 0.02, 0.025), dark if k % 2 else fur, seg, coll); self.tail.append(seg); prev = seg
        self.neck = empty("cneck", (0, -0.1, 0.1), self.body, coll)
        self.head = empty("chead", (0, -0.03, 0.08), self.neck, coll); h = self.head
        ell("chead", (0, 0, 0), (0.095, 0.085, 0.08), fur, h, coll, seg=40)
        ell("cmuzzle", (0, -0.07, -0.025), (0.045, 0.03, 0.03), white, h, coll)
        ell("cnose", (0, -0.098, -0.008), (0.012, 0.008, 0.008), pmat("catnose", srgb((220, 130, 140)), 0.4), h, coll)
        for k in range(3): ell("hstripe", (-0.025 + k * 0.025, -0.03, 0.075), (0.008, 0.03, 0.01), dark, h, coll)
        for sx in (-1, 1):
            e = empty("cear", (sx * 0.055, 0.0, 0.065), h, coll); e.rotation_euler = (0, sx * -0.35, 0)
            cylr("ear", (0, 0, 0.03), 0.035, 0.07, fur, e, coll, verts=12, r2=0.05)
            cylr("earin", (0, -0.008, 0.026), 0.024, 0.05, pmat("earpink", srgb((230, 160, 160)), 0.6), e, coll, verts=12, r2=0.05)
            ec = (sx * 0.04, -0.06, 0.018); r = 0.032
            ell("ceye", ec, (r, r * 0.7, r), pmat("cateye", srgb((210, 190, 60)), 0.1, coat=1.0), h, coll)
            ell("cpupil", (ec[0], ec[1] - r * 0.62, ec[2]), (r * 0.28, r * 0.1, r * 0.75), pmat("pupil", (0.005, 0.005, 0.005), 0.1, coat=1.0), h, coll)
            ell("cglint", (ec[0] + 0.006, ec[1] - r * 0.7, ec[2] + 0.012), (0.006, 0.003, 0.006), pmat("glint", (1, 1, 1), 0.1, emit=(1, 1, 1), estr=3.0), h, coll)
            for k in range(3): cylr("whisker", (sx * 0.06, -0.08, -0.03 + k * 0.01), 0.0015, 0.09, pmat("white", (0.9, 0.9, 0.9), 0.5), h, coll, rot=(0, math.pi / 2 + sx * (0.1 - k * 0.1), 0), verts=4)
        torus("collar", (0, -0.01, -0.03), 0.06, 0.01, pmat("collarblue", srgb((40, 80, 180)), 0.4), self.neck, coll, rot=(0.4, 0, 0))
        ell("bell", (0, -0.06, -0.07), (0.014, 0.014, 0.014), pmat("gold", srgb((240, 190, 60)), 0.2, metal=1.0), self.neck, coll)
        self.crown = None
        if crown: self.crown = mk_crown(coll, h, (0, 0, 0.085), 0.065)
    def sit(self, f):
        self.body.rotation_euler = (-0.55, 0, 0); kf(self.body, "rotation_euler", f)
        self.neck.rotation_euler = (0.5, 0, 0); kf(self.neck, "rotation_euler", f)
        for i, l in enumerate(self.legs):
            l.rotation_euler = (0.55 if i % 2 == 0 else -1.0, 0, 0); kf(l, "rotation_euler", f)
    def tailwag(self, f0, f1, amp=0.25, speed=2.0):
        for f in range(f0, f1 + 1, 2):
            for k, sgm in enumerate(self.tail):
                sgm.rotation_euler = (-0.18, amp * math.sin(f / 24 * speed * 6.28 - k * 0.6), 0); kf(sgm, "rotation_euler", f)
def mk_crown(coll, parent, loc, r):
    gold = pmat("crowngold", srgb((255, 200, 50)), 0.18, metal=1.0); gem = pmat("gem", srgb((30, 220, 120)), 0.05, emit=srgb((30, 255, 140)), estr=4.0)
    c = empty("crown", loc, parent, coll)
    cylr("cband", (0, 0, 0.015), r, 0.03, gold, c, coll, verts=32)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        cylr("cspike", (math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, 0.045), 0.012, 0.04, gold, c, coll, verts=8, r2=0.0)
        ell("cgem", (math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0.016), (0.007, 0.007, 0.007), gem, c, coll)
    return c
