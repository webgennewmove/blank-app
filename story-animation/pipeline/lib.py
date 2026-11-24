"""Shared helpers: fast mesh creation, materials (Workbench-friendly), blocky characters with
animatable rigs and swappable facial expressions."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler

S = bpy.context.scene
_mats, _mesh = {}, {}

def mat(name, col, rough=0.5):
    key = (name, tuple(round(c, 3) for c in col))
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*col, 1); m.roughness = rough; m.metallic = 0.0
    _mats[key] = m; return m

def _mk(key, builder, m, smooth=False):
    k = (key, m.name)
    if k in _mesh: return _mesh[k]
    me = bpy.data.meshes.new(str(k)); bm = bmesh.new(); builder(bm)
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    for p in me.polygons: p.use_smooth = smooth
    _mesh[k] = me; return me

def collection(name, parent=None):
    c = bpy.data.collections.new(name); (parent or S.collection).children.link(c); return c

def _obj(name, me, loc, rot, scale, parent, coll):
    o = bpy.data.objects.new(name, me)
    (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    if parent: o.parent = parent
    return o

def empty(name, loc=(0, 0, 0), parent=None, coll=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); (coll or S.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def box(name, loc, size, m, rot=(0, 0, 0), parent=None, bevel=0.0, coll=None):
    if bevel:
        sz = tuple(round(v, 3) for v in size)
        def b(bm, sz=sz, bevel=bevel):
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts: v.co = Vector((v.co.x * sz[0], v.co.y * sz[1], v.co.z * sz[2]))
            bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=bevel, segments=2, affect="EDGES")
        return _obj(name, _mk(("bcube", sz, bevel), b, m), loc, rot, (1, 1, 1), parent, coll)
    return _obj(name, _mk("cube", lambda bm: bmesh.ops.create_cube(bm, size=1.0), m), loc, rot, size, parent, coll)

def cyl(name, loc, r, depth, m, rot=(0, 0, 0), verts=16, parent=None, coll=None, smooth=True):
    me = _mk(("cyl", verts, smooth), lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=1, radius2=1, depth=1), m, smooth=smooth)
    return _obj(name, me, loc, rot, (r, r, depth), parent, coll)

def cone(name, loc, r, depth, m, verts=8, parent=None, coll=None, rot=(0, 0, 0)):
    me = _mk(("cone", verts), lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=1, radius2=0, depth=1), m)
    return _obj(name, me, loc, rot, (r, r, depth), parent, coll)

def sphere(name, loc, r, m, coll=None, seg=16, parent=None, scale=None):
    me = _mk(("sph", seg), lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1), m, smooth=True)
    return _obj(name, me, loc, (0, 0, 0), scale or (r, r, r), parent, coll)

def prism(name, loc, size, m, rot=(0, 0, 0), coll=None, parent=None):
    """Gable roof: triangular prism along local Y. size=(width x, length y, height z)."""
    def b(bm):
        vs = [bm.verts.new(v) for v in [(-.5, -.5, 0), (.5, -.5, 0), (0, -.5, 1), (-.5, .5, 0), (.5, .5, 0), (0, .5, 1)]]
        for f in [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]: bm.faces.new([vs[i] for i in f])
    return _obj(name, _mk("prism", b, m), loc, rot, size, parent, coll)

def rod(name, a, b, r, m, coll=None, verts=6):
    a, b = Vector(a), Vector(b); d = b - a
    o = cyl(name, (a + b) / 2, r, d.length, m, verts=verts, coll=coll, smooth=False)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o

# ---------------------------------------------------------------- characters
BLACK = None
def _face_mats():
    return dict(black=mat("f_black", (0.02, 0.02, 0.03), 0.2), white=mat("f_white", (1, 1, 1), 0.2),
                mouth=mat("f_mouth", (0.25, 0.02, 0.05), 0.4), tongue=mat("f_tongue", (0.95, 0.35, 0.45), 0.4),
                tooth=mat("f_tooth", (1, 1, 1), 0.3), tear=mat("f_tear", (0.3, 0.7, 1.0), 0.1),
                blush=mat("f_blush", (1.0, 0.45, 0.5), 0.6))

FACES = ["happy", "excited", "laugh", "sad", "shocked", "scared", "determined", "blink", "smug"]

def _arc(name, cx, cz, w, h, thick, m, parent, coll, up=True, n=5):
    """Smile/frown curve built from n short boxes on face plane (y=-0.61)."""
    out = []
    for i in range(n):
        t = (i / (n - 1)) * 2 - 1
        x = cx + t * w / 2
        z = cz + (h * (t * t) if up else -h * (t * t))
        ang = math.atan2(2 * h * t * (1 if up else -1), w / 2)
        out.append(box(name, (x, -0.615, z), (w / n * 1.25, 0.02, thick), m, rot=(0, -ang, 0), parent=parent, coll=coll))
    return out

import sys as _sys
_sys.path.insert(0, "/home/claude/zara")
import faces as _faces
_facemats = {}
def _face_mat(kind, skin):
    k = (kind, skin)
    if k in _facemats: return _facemats[k]
    p = _faces.ensure(kind, skin)
    m = bpy.data.materials.new(f"face_{kind}"); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(p); tex.interpolation = "Cubic"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); nt.nodes.active = tex
    m.diffuse_color = (*skin, 1); m.roughness = 0.5
    _facemats[k] = m; return m
_faceplane = {}
def _plane_mesh():
    if "p" in _faceplane: return _faceplane["p"]
    me = bpy.data.meshes.new("faceplane"); s = 0.56
    me.from_pydata([(-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    _faceplane["p"] = me; return me

def build_face_tex(head, kind, coll, skin):
    me = _plane_mesh().copy(); me.materials.append(_face_mat(kind, skin))
    o = bpy.data.objects.new("face_" + kind, me); coll.objects.link(o)
    o.parent = head; o.location = (0, -0.618, 0); o.rotation_euler = (0, 0, math.pi)
    o.rotation_euler = (0, 0, 0)
    return [o]

def build_face(head, kind, coll, fm):
    grp = []
    def add(o): grp.append(o); return o
    ez = 0.08
    for sx in (-0.25, 0.25):
        if kind in ("happy", "excited", "sad", "determined", "smug"):
            e = add(sphere("eye", (sx, -0.6, ez), 1, fm["black"], coll=coll, parent=head, scale=(0.1 if kind != "excited" else 0.12, 0.03, 0.16 if kind != "excited" else 0.19)))
            add(sphere("glint", (sx + 0.035, -0.635, ez + 0.06), 1, fm["white"], coll=coll, parent=head, scale=(0.035, 0.01, 0.045)))
        if kind == "shocked" or kind == "scared":
            add(sphere("ewhite", (sx, -0.6, ez + 0.02), 1, fm["white"], coll=coll, parent=head, scale=(0.17, 0.03, 0.2)))
            add(sphere("pupil", (sx, -0.63, ez + 0.02), 1, fm["black"], coll=coll, parent=head, scale=(0.06, 0.01, 0.07)))
        if kind == "laugh":  # ^ ^ eyes
            for sgn in (-1, 1):
                add(box("eyearc", (sx + sgn * 0.06, -0.615, ez + 0.02), (0.15, 0.02, 0.045), fm["black"], rot=(0, sgn * 0.6, 0), parent=head, coll=coll))
        if kind == "blink":
            add(box("lid", (sx, -0.615, ez), (0.2, 0.02, 0.04), fm["black"], parent=head, coll=coll))
        if kind == "sad":
            add(box("brow", (sx, -0.615, ez + 0.27), (0.22, 0.02, 0.045), fm["black"], rot=(0, 0.35 if sx < 0 else -0.35, 0), parent=head, coll=coll))
        if kind in ("determined", "scared"):
            a = -0.4 if (sx < 0) == (kind == "determined") else 0.4
            add(box("brow", (sx, -0.615, ez + 0.27), (0.24, 0.02, 0.05), fm["black"], rot=(0, a, 0), parent=head, coll=coll))
        if kind in ("happy", "excited", "laugh", "smug"):
            add(sphere("blush", (sx * 1.55, -0.61, -0.12), 1, fm["blush"], coll=coll, parent=head, scale=(0.09, 0.01, 0.05)))
    if kind in ("happy", "blink"):
        grp += _arc("smile", 0, -0.27, 0.42, 0.09, 0.05, fm["black"], head, coll, up=True)
    elif kind in ("excited", "laugh"):
        m = add(sphere("mouthopen", (0, -0.6, -0.25), 1, fm["mouth"], coll=coll, parent=head, scale=(0.24, 0.03, 0.15 if kind == "excited" else 0.18)))
        add(box("teeth", (0, -0.625, -0.15), (0.34, 0.02, 0.06), fm["tooth"], parent=head, coll=coll))
        add(sphere("tongue", (0, -0.625, -0.33), 1, fm["tongue"], coll=coll, parent=head, scale=(0.12, 0.01, 0.05)))
    elif kind == "sad":
        grp += _arc("frown", 0, -0.24, 0.34, 0.06, 0.045, fm["black"], head, coll, up=False)
        add(sphere("tear", (-0.27, -0.63, -0.08), 1, fm["tear"], coll=coll, parent=head, scale=(0.045, 0.01, 0.07)))
    elif kind == "shocked":
        add(sphere("omouth", (0, -0.6, -0.28), 1, fm["mouth"], coll=coll, parent=head, scale=(0.11, 0.03, 0.15)))
    elif kind == "scared":
        grp += _arc("wobble", 0, -0.28, 0.36, 0.03, 0.04, fm["black"], head, coll, up=False, n=7)
    elif kind == "determined":
        add(box("line", (0, -0.615, -0.27), (0.3, 0.02, 0.05), fm["black"], parent=head, coll=coll))
    elif kind == "smug":
        add(box("smirk", (0.06, -0.615, -0.26), (0.3, 0.02, 0.05), fm["black"], rot=(0, -0.25, 0), parent=head, coll=coll))
    return grp

class Char:
    """Blocky R6-style character. Pivots: root -> hips(bob/lean) -> torso, neck(head), shoulders(arms), legs."""
    def __init__(self, name, coll, skin, shirt, pants, hair="short", hair_col=(0.05, 0.03, 0.02), extra=None,
                 scale=1.0, shoes=(0.95, 0.95, 0.95), elder=False):
        self.name, self.coll = name, coll
        sk = mat(f"skin_{skin}", skin, 0.5); sh = mat(f"shirt_{shirt}", shirt, 0.6)
        pa = mat(f"pants_{pants}", pants, 0.6); hm = mat(f"hair_{hair_col}", hair_col, 0.7)
        so = mat(f"shoe_{shoes}", shoes, 0.4)
        self.root = empty(name, coll=coll); self.root.scale = (scale,) * 3
        self.hips = empty("hips", (0, 0, 2.0), parent=self.root, coll=coll)
        self.legs = []
        for sx in (-0.5, 0.5):
            p = empty("legpiv", (sx, 0, 0), parent=self.hips, coll=coll)
            box("leg", (0, 0, -1.0), (0.95, 0.95, 2.0), pa, parent=p, bevel=0.13, coll=coll)
            box("shoe", (0, -0.06, -1.85), (0.98, 1.08, 0.32), so, parent=p, bevel=0.06, coll=coll)
            self.legs.append(p)
        self.torso = box("torso", (0, 0, 1.0), (2.0, 1.0, 2.0), sh, parent=self.hips, bevel=0.16, coll=coll)
        self.arms = []
        for sx in (-1.5, 1.5):
            p = empty("armpiv", (sx, 0, 1.8), parent=self.hips, coll=coll)
            box("sleeve", (0, 0, -0.45), (0.97, 0.97, 1.0), sh, parent=p, bevel=0.13, coll=coll)
            box("arm", (0, 0, -1.35), (0.92, 0.92, 0.9), sk, parent=p, bevel=0.13, coll=coll)
            self.arms.append(p)
        self.neck = empty("neck", (0, 0, 2.0), parent=self.hips, coll=coll)
        self.head = box("head", (0, 0, 0.62), (1.22, 1.22, 1.22), sk, parent=self.neck, bevel=0.14, coll=coll)
        h = self.head
        if hair == "short":
            box("hair", (0, 0.06, 0.6), (1.34, 1.3, 0.3), hm, parent=h, bevel=0.08, coll=coll)
            box("hairback", (0, 0.6, 0.15), (1.3, 0.2, 0.9), hm, parent=h, coll=coll)
            box("fringe", (0.25, -0.62, 0.48), (0.7, 0.12, 0.22), hm, rot=(0, 0.25, 0), parent=h, coll=coll)
        elif hair == "spiky":
            box("hair", (0, 0.05, 0.6), (1.34, 1.3, 0.3), hm, parent=h, coll=coll)
            for i, (x, y) in enumerate([(-0.4, -0.3), (0, -0.4), (0.4, -0.3), (-0.3, 0.3), (0.3, 0.3)]):
                cone("spike", (x, y, 0.95), 0.3, 0.6, hm, verts=4, parent=h, coll=coll, rot=(random.uniform(-.3, .3), random.uniform(-.3, .3), 0.78))
        elif hair == "puffs":
            box("hair", (0, 0.06, 0.58), (1.32, 1.3, 0.28), hm, parent=h, coll=coll)
            for sx in (-0.62, 0.62):
                sphere("puff", (sx, 0.1, 0.62), 0.38, hm, coll=coll, parent=h)
        elif hair == "ponytail":
            box("hair", (0, 0.06, 0.6), (1.34, 1.3, 0.3), hm, parent=h, coll=coll)
            box("hairback", (0, 0.62, 0.1), (1.3, 0.2, 1.0), hm, parent=h, coll=coll)
            sphere("tail", (0, 0.85, 0.5), 0.32, hm, coll=coll, parent=h, scale=(0.3, 0.3, 0.55))
        elif hair == "bun":
            box("hair", (0, 0.06, 0.6), (1.34, 1.3, 0.3), hm, parent=h, coll=coll)
            box("hairback", (0, 0.62, 0.15), (1.3, 0.2, 0.9), hm, parent=h, coll=coll)
            sphere("bun", (0, 0.25, 1.0), 0.42, hm, coll=coll, parent=h)
        elif hair == "fade":
            box("hair", (0, 0.04, 0.58), (1.3, 1.28, 0.26), hm, parent=h, bevel=0.1, coll=coll)
            box("hairback", (0, 0.6, 0.25), (1.28, 0.16, 0.7), hm, parent=h, coll=coll)
            for sx in (-0.62, 0.62): box("hairside", (sx, 0.15, 0.32), (0.06, 0.9, 0.42), hm, parent=h, coll=coll)
        elif hair == "afro":
            sphere("afro", (0, 0.12, 0.62), 1, hm, coll=coll, parent=h, scale=(0.92, 0.88, 0.62), seg=20)
        elif hair == "cornrows":
            box("hair", (0, 0.05, 0.6), (1.3, 1.3, 0.16), hm, parent=h, coll=coll)
            for k in range(5): box("row", (-0.48 + k * 0.24, 0.05, 0.7), (0.12, 1.28, 0.1), hm, parent=h, coll=coll, bevel=0.04)
        elif hair == "locs":
            box("hair", (0, 0.05, 0.6), (1.34, 1.3, 0.28), hm, parent=h, coll=coll, bevel=0.08)
            for k in range(9):
                a_ = -1.4 + k * 0.35
                cyl("loc", (math.sin(a_) * 0.66, 0.1 + math.cos(a_) * 0.5, 0.05), 0.1, 1.0, hm, parent=h, coll=coll, verts=6)
        self.extra = []
        if extra: self.extra = extra(self)
        self.skin = tuple(skin)
        self.faces = {k: build_face_tex(h, k, coll, self.skin) for k in FACES + ["talk"]}
        self._face_keys = {}
        self.set_face("happy", 1)
        self.anim = {}

    # ---- keyframing helpers
    def key(self, obj, path, frame, value):
        setattr(obj, path, value) if not isinstance(value, (tuple, list)) else setattr(obj, path, value)
        obj.keyframe_insert(data_path=path, frame=frame)

    def set_face(self, kind, frame):
        for k, objs in self.faces.items():
            hide = k != kind
            for o in objs:
                o.hide_render = hide; o.keyframe_insert("hide_render", frame=frame)
                o.hide_viewport = hide

    def place(self, loc, rotz=0.0, frame=1):
        self.root.location = loc; self.root.rotation_euler = (0, 0, rotz)
        self.root.keyframe_insert("location", frame=frame); self.root.keyframe_insert("rotation_euler", frame=frame)

    def pose(self, f, arms=(0, 0), arms_side=(0, 0), legs=(0, 0), head=(0, 0, 0), hips_z=2.0, lean=0.0, twist=0.0, hips_x=0.0):
        """Write a full pose at frame f. Angles in radians. arms: forward swing (+ = forward/up)."""
        for i, a in enumerate(self.arms):
            side = arms_side[i] * (1 if i == 0 else -1)
            a.rotation_euler = (-arms[i], side, 0); a.keyframe_insert("rotation_euler", frame=f)
        for i, l in enumerate(self.legs):
            l.rotation_euler = (-legs[i], 0, 0); l.keyframe_insert("rotation_euler", frame=f)
        self.neck.rotation_euler = head; self.neck.keyframe_insert("rotation_euler", frame=f)
        self.hips.location = (hips_x, 0, hips_z); self.hips.keyframe_insert("location", frame=f)
        self.hips.rotation_euler = (lean, 0, twist); self.hips.keyframe_insert("rotation_euler", frame=f)

    def move(self, f, loc, rotz=None):
        self.root.location = loc; self.root.keyframe_insert("location", frame=f)
        if rotz is not None:
            self.root.rotation_euler = (0, 0, rotz); self.root.keyframe_insert("rotation_euler", frame=f)

    # ---- procedural actions (write per-frame keys)
    def idle(self, f0, f1, energy=1.0, seed=0, blink=True, base_face="happy", talk=False):
        rnd = random.Random(seed + hash(self.name) % 1000)
        ph = rnd.uniform(0, 6)
        for f in range(f0, f1 + 1):
            t = (f + ph * 10) / 24
            b = math.sin(t * 2 * math.pi * 0.7) * 0.05 * energy
            hx = math.sin(t * 1.3) * 0.12 * energy
            self.pose(f, arms=(0.12 * math.sin(t * 2.2) * energy, -0.12 * math.sin(t * 2.2) * energy), arms_side=(0.08, 0.08),
                      head=(0.08 * math.sin(t * 1.7) * energy + (0.05 * math.sin(t * 9) if talk else 0), 0.1 * math.sin(t * 1.1) * energy, hx),
                      hips_z=2.0 + b, twist=0.05 * math.sin(t * 0.9) * energy)
        if blink:
            f = f0 + rnd.randint(10, 30)
            while f < f1 - 4:
                self.set_face("blink", f); self.set_face(base_face, f + 3); f += rnd.randint(40, 75)

    def walk(self, f0, f1, a, b, run=False, bounce=1.0):
        a, b = Vector(a), Vector(b); d = (b - a)
        rotz = math.atan2(-d.x, d.y) + math.pi if d.length > 0.01 else self.root.rotation_euler.z
        rotz = math.atan2(d.x, -d.y)  # character faces -Y in rest pose
        rotz = math.atan2(-d.x, -d.y) * -1
        rotz = math.atan2(d.y, d.x) + math.pi / 2
        n = max(1, f1 - f0)
        cad = 2.6 if run else 1.6   # strides per second
        amp = 0.95 if run else 0.55
        for f in range(f0, f1 + 1):
            u = (f - f0) / n
            self.move(f, a + d * u, rotz)
            ph = (f - f0) / 24 * cad * 2 * math.pi
            s = math.sin(ph)
            self.pose(f, arms=(-s * amp * 1.1, s * amp * 1.1), legs=(s * amp, -s * amp), arms_side=(0.1, 0.1),
                      hips_z=2.0 + abs(math.cos(ph)) * (0.25 if run else 0.12) * bounce, lean=(-0.18 if run else -0.04),
                      head=(0.05 if run else 0, 0, 0.05 * s))

    def jump(self, f0, f1, height=4.0, start=None, end=None, cheer=True):
        n = f1 - f0; start = Vector(start or self.root.location); end = Vector(end or start)
        crouch = max(2, n // 6)
        for f in range(f0, f1 + 1):
            u = (f - f0) / n
            if f - f0 < crouch:
                k = (f - f0) / crouch
                self.pose(f, arms=(-0.5 * k, -0.5 * k), legs=(0.5 * k, 0.5 * k), hips_z=2.0 - 0.6 * k, lean=-0.2 * k)
                self.move(f, start)
            else:
                v = (f - f0 - crouch) / (n - crouch)
                z = 4 * height * v * (1 - v)
                p = start + (end - start) * v; p.z += z
                self.move(f, p)
                arms = (2.8, 2.8) if cheer else (1.2, 1.2)
                self.pose(f, arms=arms, arms_side=(0.4, 0.4), legs=(-0.3 + 0.6 * v, 0.4 - 0.6 * v), hips_z=2.0, lean=0.1,
                          head=(-0.2, 0, 0))

    def dance(self, f0, f1, style=0, speed=1.0):
        for f in range(f0, f1 + 1):
            t = (f - f0) / 24 * speed
            s = math.sin(t * 2 * math.pi * 1.8); c = math.cos(t * 2 * math.pi * 1.8)
            if style == 0:   # arm pump
                self.pose(f, arms=(1.6 + 1.2 * s, 1.6 - 1.2 * s), arms_side=(0.5, 0.5), legs=(0.3 * s, -0.3 * s),
                          hips_z=2.0 + 0.2 * abs(s), twist=0.3 * s, head=(0.15 * c, 0, 0.2 * s), hips_x=0.25 * s)
            elif style == 1:  # celebrate jumps
                self.pose(f, arms=(2.9, 2.9), arms_side=(0.6 + 0.3 * s, 0.6 + 0.3 * s), legs=(0.2 * s, 0.2 * s),
                          hips_z=2.0 + 0.6 * abs(s), head=(-0.2, 0, 0.15 * c))
            else:            # side step groove
                self.pose(f, arms=(0.8 + 0.5 * c, 0.8 - 0.5 * c), arms_side=(0.3, 0.3), legs=(0.2 * s, -0.2 * s),
                          hips_z=2.0 + 0.1 * abs(c), hips_x=0.5 * s, twist=0.25 * c, head=(0, 0.2 * s, 0.25 * c))

    def laugh(self, f0, f1, point=True):
        for f in range(f0, f1 + 1):
            t = (f - f0) / 24; s = math.sin(t * 2 * math.pi * 4)
            self.pose(f, arms=(1.4 if point else 0.6, 0.6 + 0.15 * s), arms_side=(0.05, 0.3), lean=0.15 + 0.06 * s,
                      hips_z=2.0 + 0.08 * abs(s), head=(-0.35 + 0.08 * s, 0, 0.1 * s))
        self.set_face("laugh", f0)

    def float_(self, f0, f1, base_z=3.0, spin=0.0, at=None):
        at = Vector(at or self.root.location)
        for f in range(f0, f1 + 1):
            t = (f - f0) / 24
            self.move(f, at + Vector((0, 0, base_z + 0.4 * math.sin(t * 2.4))), self.root.rotation_euler.z + spin * t)
            self.pose(f, arms=(0.3, 0.3), arms_side=(1.1 + 0.2 * math.sin(t * 3), 1.1 + 0.2 * math.sin(t * 3)),
                      legs=(0.25 + 0.1 * math.sin(t * 2), -0.1), head=(-0.1, 0.1 * math.sin(t * 1.5), 0), lean=0.05)


def make_dog(coll, col=(0.85, 0.6, 0.3)):
    fur = mat("dogfur", col, 0.7); dark = mat("dogdark", (0.45, 0.28, 0.12), 0.7); fm = _face_mats()
    root = empty("dog", coll=coll)
    body = box("dbody", (0, 0.3, 0.9), (0.9, 1.6, 0.8), fur, parent=root, bevel=0.15, coll=coll)
    head = box("dhead", (0, -0.75, 1.45), (0.95, 0.85, 0.85), fur, parent=root, bevel=0.18, coll=coll)
    box("snout", (0, -1.25, 1.3), (0.5, 0.4, 0.4), mat("snout", (0.95, 0.85, 0.7), 0.6), parent=root, bevel=0.1, coll=coll)
    sphere("nose", (0, -1.47, 1.42), 0.1, fm["black"], coll=coll, parent=root)
    for sx in (-0.22, 0.22):
        sphere("deye", (sx, -1.19, 1.62), 1, fm["black"], coll=coll, parent=root, scale=(0.08, 0.03, 0.1))
        sphere("dglint", (sx + 0.02, -1.22, 1.66), 1, fm["white"], coll=coll, parent=root, scale=(0.025, 0.01, 0.03))
    ears = []
    for sx in (-0.5, 0.5):
        e = empty("earpiv", (sx, -0.7, 1.8), parent=root, coll=coll)
        box("ear", (0, 0, -0.3), (0.2, 0.4, 0.6), dark, parent=e, coll=coll); ears.append(e)
    for sx in (-0.3, 0.3):
        for sy in (-0.3, 0.9):
            box("dleg", (sx, sy, 0.3), (0.28, 0.28, 0.6), fur, parent=root, coll=coll)
    tail = empty("tailpiv", (0, 1.1, 1.1), parent=root, coll=coll)
    box("tail", (0, 0.3, 0.2), (0.15, 0.6, 0.15), fur, rot=(0.6, 0, 0), parent=tail, coll=coll)
    return root, tail, ears

def wag(tail, ears, f0, f1, speed=6.0, perky=True):
    for f in range(f0, f1 + 1):
        t = (f - f0) / 24
        tail.rotation_euler = (0, 0, 0.6 * math.sin(t * speed * 2 * math.pi / 2)); tail.keyframe_insert("rotation_euler", frame=f)
        for i, e in enumerate(ears):
            e.rotation_euler = (0.2 * math.sin(t * 5 + i) if perky else 0.6, (0.3 if perky else 0.9) * (-1 if i == 0 else 1), 0)
            e.keyframe_insert("rotation_euler", frame=f)
