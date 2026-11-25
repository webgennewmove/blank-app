"""PIRATES 'I'm The Captain Now': reusable sea / ships / arms / fx3d / cast.
exec'd after world.py + eevee_patch.py + rcast.py (needs lib helpers, S, FPS, TEMP, CAM)."""
import bmesh, math, random
import numpy as np
from mathutils import Vector, Quaternion, Matrix, Euler

# ---------------------------------------------------------------- generic helpers (copied from glow_sets)
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
FONTB = bpy.data.fonts.load("/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf")
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
def vis(objs, f, on):
    for o in (objs if isinstance(objs, (list, tuple)) else [objs]):
        o.hide_render = not on; o.keyframe_insert("hide_render", frame=f)
        for ch in o.children_recursive: ch.hide_render = not on; ch.keyframe_insert("hide_render", frame=f)
def stripes(name, c1, c2, scale=2.2, direction="Z"):
    """banded shirt material (object-space wave bands)"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = direction
    wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 0
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].position = 0.5; ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6
    m.diffuse_color = (*c1, 1); return m
def recolor(c, part_prefixes, m):
    """swap the material on a Char's parts (copies mesh data first: never touch cached shared meshes)"""
    for o in c.root.children_recursive:
        if o.type == "MESH" and o.name.split(".")[0] in part_prefixes:
            o.data = o.data.copy(); o.data.materials[0] = m

# ---------------------------------------------------------------- DAY: sky + sun
WBG = S.world.node_tree.nodes["Background"]
SUN = [o for o in S.objects if o.type == "LIGHT" and o.data.type == "SUN"][0]
def day_light():
    WBG.inputs[0].default_value = (0.3, 0.55, 0.95, 1); WBG.inputs[1].default_value = 0.62
    SUN.data.energy = 2.7; SUN.data.color = (1.0, 0.95, 0.86); SUN.data.angle = math.radians(4)
    SUN.rotation_euler = (math.radians(48), 0, math.radians(-30))
day_light()
SKYC = collection("sky")
def clouds_ring():
    cw = mat("cloudw", (1, 1, 1), 0.95); rnd = random.Random(4)
    for i in range(22):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(260, 520)
        c = empty("cloud", coll=SKYC); c.location = (math.cos(a) * r, math.sin(a) * r, rnd.uniform(70, 140))
        for k in range(6):
            sphere("puff", (rnd.uniform(-14, 14), rnd.uniform(-6, 6), rnd.uniform(0, 6)), rnd.uniform(7, 13), cw, coll=SKYC, parent=c, seg=12)
clouds_ring()

# ---------------------------------------------------------------- SEA: displaced grid driven by a frame handler; sea_z() for floating things
WAVES = [(0.75, 64.0, 0.25, 0.16), (0.45, 37.0, 1.35, 0.22), (0.25, 19.0, 2.4, 0.31), (0.12, 9.5, 0.9, 0.45)]   # amp, wavelength, dir, freq Hz
SEA_AMP = [1.0]; SEA_T0 = [0.0]
def sea_z(x, y, t):
    z = 0.0
    for k, (A, L, d, fq) in enumerate(WAVES):
        z += A * math.sin(2 * math.pi / L * (x * math.cos(d) + y * math.sin(d)) - 2 * math.pi * fq * t + k * 1.7)
    return z * SEA_AMP[0]
def _sea_np(x, y, t):
    z = np.zeros_like(x)
    for k, (A, L, d, fq) in enumerate(WAVES):
        z += A * np.sin(2 * np.pi / L * (x * math.cos(d) + y * math.sin(d)) - 2 * np.pi * fq * t + k * 1.7)
    return z * SEA_AMP[0]
def sea_t(f): return (f - 1) / FPS + SEA_T0[0]
def water_mat():
    m = bpy.data.materials.new("water"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = (0.004, 0.09, 0.2, 1); mix.inputs[7].default_value = (0.12, 0.4, 0.62, 1)
    nt.links.new(lw.outputs["Facing"], mix.inputs[0]); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 3
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.18
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.12; m.diffuse_color = (0.05, 0.3, 0.5, 1); return m
WATER = water_mat()
SEAC = collection("sea")
def _grid(name, size, n):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=size / 2)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(WATER); o = bpy.data.objects.new(name, me); SEAC.objects.link(o); return o
SEA = _grid("sea", 520, 230)
_SEA_CO = np.zeros(len(SEA.data.vertices) * 3); SEA.data.vertices.foreach_get("co", _SEA_CO); _SEA_CO = _SEA_CO.reshape(-1, 3)
FAR = box("farsea", (0, 0, -1.6), (9000, 9000, 0.2), WATER, coll=SEAC)
def sea_update(scene, *args):
    if SEAC.hide_render: return
    t = sea_t(scene.frame_current); L = SEA.location
    co = _SEA_CO.copy(); co[:, 2] = _sea_np(co[:, 0] + L.x, co[:, 1] + L.y, t)
    SEA.data.vertices.foreach_set("co", co.ravel()); SEA.data.update()
bpy.app.handlers.frame_change_pre.clear(); bpy.app.handlers.frame_change_pre.append(sea_update)
def sea_center(x, y): SEA.location = (round(x / 2.26) * 2.26, round(y / 2.26) * 2.26, 0)   # keep grid spacing aligned
def float_on(obj, f, x, y, heading, draft=0.0, tilt=1.0, extra_z=0.0, lx=6.0, ly=3.0):
    """sit obj on the sea at frame f: height + pitch/roll from the surface (no clipping)"""
    t = sea_t(f); ch, sh = math.cos(heading), math.sin(heading)
    zc = sea_z(x, y, t)
    zf = sea_z(x + ch * lx, y + sh * lx, t); zb = sea_z(x - ch * lx, y - sh * lx, t)
    zl = sea_z(x - sh * ly, y + ch * ly, t); zr = sea_z(x + sh * ly, y - ch * ly, t)
    pitch = math.atan2(zf - zb, 2 * lx) * tilt; roll = math.atan2(zl - zr, 2 * ly) * tilt
    obj.location = (x, y, zc - draft + extra_z)
    obj.rotation_euler = Euler((roll, -pitch, heading), "XYZ")   # boats are built along +X
    obj.keyframe_insert("location", frame=f); obj.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- CARGO SHIP (built along +X, bow at +X). Deck at DECK_Z.
SHIPC = collection("ship")
DECK_Z = 16.0; SH_L = 240.0; SH_W = 40.0
NAVY = mat("hullnavy", (0.06, 0.1, 0.2), 0.55); HRED = mat("hullred", (0.55, 0.06, 0.05), 0.6); WHITE = mat("white", (1, 1, 1))
DECKM = mat("deckm", (0.42, 0.18, 0.14), 0.8); RAILM = mat("railm", (0.92, 0.92, 0.9), 0.5); BRIDGEM = mat("bridgem", (0.94, 0.94, 0.92), 0.6)
WINM = mat("bwin", (0.08, 0.14, 0.2), 0.15); YEL = mat("yel", (1.0, 0.78, 0.08), 0.5); FUNM = mat("funm", (0.85, 0.3, 0.1), 0.6)
SHIP = empty("shiproot", coll=SHIPC)
def _hull():
    it = []
    it.append(((0, 0, -3.0), (SH_L, SH_W, 10.0), 0, 0))        # red underbody (below waterline + boot top)
    it.append(((0, 0, 8.5), (SH_L, SH_W, 15.0), 1, 0))         # navy topsides up to deck
    it.append(((0, 0, DECK_Z - 0.4), (SH_L - 0.6, SH_W - 0.6, 0.8), 2, 0))   # deck plate
    h = merged_boxes("hull", it, [HRED, NAVY, DECKM], SHIPC); h.parent = SHIP
    # bow wedge (prism helper makes a triangular prism; build a custom tapered bow instead)
    bm = bmesh.new(); hw = SH_W / 2; x0 = SH_L / 2; L = 34
    vs = [bm.verts.new(v) for v in [(x0, -hw, -8), (x0, hw, -8), (x0 + L * 0.55, 0, -8), (x0, -hw, DECK_Z), (x0, hw, DECK_Z), (x0 + L, 0, DECK_Z + 2)]]
    for fa in [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]: bm.faces.new([vs[i] for i in fa])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("bow"); bm.to_mesh(me); bm.free(); me.materials.append(NAVY)
    bo = bpy.data.objects.new("bow", me); SHIPC.objects.link(bo); bo.parent = SHIP
    box("bowred", (x0 + 6, 0, -5.0), (12, SH_W * 0.7, 6), HRED, coll=SHIPC, parent=SHIP)
    box("bowdeck", (x0 + 9, 0, DECK_Z + 0.3), (18, SH_W * 0.55, 0.6), DECKM, coll=SHIPC, parent=SHIP)
    # waterline stripe + name
    for sy in (-1, 1): box("bootstripe", (0, sy * (hw + 0.02), 2.2), (SH_L, 0.1, 0.6), WHITE, coll=SHIPC, parent=SHIP)
    t = text3d("MEGA MAERSKY", (x0 - 20, -hw - 0.15, 11), 3.2, WHITE, coll=SHIPC, extrude=0.05); t.parent = SHIP
    # rails along both sides (posts + top bar), gap for the standoff area kept continuous (characters vault it)
    for sy in (-1, 1):
        box("railtop", (0, sy * (hw - 0.3), DECK_Z + 1.9), (SH_L - 4, 0.25, 0.25), RAILM, coll=SHIPC, parent=SHIP)
        box("railmid", (0, sy * (hw - 0.3), DECK_Z + 1.0), (SH_L - 4, 0.18, 0.18), RAILM, coll=SHIPC, parent=SHIP)
        for x in range(-116, 118, 6): box("post", (x, sy * (hw - 0.3), DECK_Z + 0.95), (0.25, 0.25, 1.9), RAILM, coll=SHIPC, parent=SHIP)
_hull()
# superstructure at the stern
BR_X = -104.0
def _bridge():
    box("house", (BR_X, 0, DECK_Z + 14), (24, 30, 28), BRIDGEM, coll=SHIPC, parent=SHIP, bevel=0.3)
    box("bridgedeck", (BR_X + 2, 0, DECK_Z + 30), (20, 46, 4), BRIDGEM, coll=SHIPC, parent=SHIP, bevel=0.3)
    box("bridgewin", (BR_X + 12.05, 0, DECK_Z + 30.6), (0.2, 44, 1.8), WINM, coll=SHIPC, parent=SHIP)
    for k in range(5): box("winrow", (BR_X + 12.05, 0, DECK_Z + 5 + k * 5), (0.2, 26, 1.4), WINM, coll=SHIPC, parent=SHIP)
    box("funnel", (BR_X - 8, 0, DECK_Z + 36), (8, 10, 12), FUNM, coll=SHIPC, parent=SHIP, bevel=0.5)
    box("funtop", (BR_X - 8, 0, DECK_Z + 42.3), (8.2, 10.2, 1.2), mat("blk", (0.04, 0.04, 0.05)), coll=SHIPC, parent=SHIP)
    box("mast", (BR_X + 2, 0, DECK_Z + 38), (0.8, 0.8, 12), RAILM, coll=SHIPC, parent=SHIP)
    # galley door on the forward face (port side half), with sign
    box("galleydoor", (BR_X + 12.1, -9, DECK_Z + 3.2), (0.3, 4.2, 6.4), mat("doorm", (0.55, 0.58, 0.62), 0.5), coll=SHIPC, parent=SHIP)
    t = text3d("GALLEY", (BR_X + 12.3, -9, DECK_Z + 7.4), 1.0, mat("galleyt", (0.1, 0.1, 0.12)), rot=(math.pi / 2, 0, math.pi / 2), coll=SHIPC); t.parent = SHIP
_bridge()
# bridge wing (starboard, y<0 faces camera side) where the Giant stands: top surface at WING_Z
WING_Z = DECK_Z + 32.0; WING = Vector((BR_X + 4, -21.0, WING_Z))
box("wingrail", (BR_X + 4, -23.6, WING_Z + 1.4), (10, 0.3, 0.3), RAILM, coll=SHIPC, parent=SHIP)
# containers: two aft bays, open standoff deck x in [-88, -10], forward bays
CL, CW, CH = 16.0, 6.6, 7.0
CCOLS = [(0.75, 0.12, 0.1), (0.1, 0.3, 0.6), (0.15, 0.45, 0.25), (0.9, 0.5, 0.08), (0.55, 0.57, 0.6), (0.1, 0.55, 0.6), (0.85, 0.82, 0.78)]
def cont_mat(i):
    nm = f"cont{i}"; m = bpy.data.materials.get(nm)
    if m: return m
    m = bpy.data.materials.new(nm); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; col = CCOLS[i]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 0.55
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 6.0
    wv.bands_direction = "X"; nt.links.new(tc.outputs["Generated"], wv.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = (*col, 1); return m
CMATS = [cont_mat(i) for i in range(len(CCOLS))]
ROWS_Y = [-13.2, -6.6, 0.0, 6.6, 13.2]
STACK_X = [-0.0, 18.0, 36.0, 54.0, 72.0, 90.0]     # forward bays (centres)
WALL_X = 0.0                                       # the bay that topples in the money shot (separate objects)
OPEN_X = (-88.0, -9.0)                             # open deck for the standoff
rnd = random.Random(7)
_items = []
for bx in STACK_X[1:]:
    tiers = 5 if bx in (36.0, 54.0) else 4
    for ry in ROWS_Y:
        for tz in range(tiers):
            _items.append(((bx, ry, DECK_Z + CH / 2 + tz * CH), (CL - 0.3, CW - 0.25, CH - 0.2), rnd.randrange(len(CCOLS)), 0))
CSTACKS = merged_boxes("containers", _items, CMATS, SHIPC); CSTACKS.parent = SHIP
WALL = []   # tallest stack (6 tiers) at WALL_X: kept separate so it can topple
for ry in ROWS_Y:
    for tz in range(6):
        o = box("wallc", (WALL_X, ry, DECK_Z + CH / 2 + tz * CH), (CL - 0.3, CW - 0.25, CH - 0.2), CMATS[rnd.randrange(len(CCOLS))], coll=SHIPC, parent=SHIP)
        o["home"] = list(o.location); WALL.append(o)
# deck crane (port side of the open deck) with a hook on a cable
CR_BASE = Vector((-48.0, 14.0, DECK_Z)); CR_TIP = Vector((-48.0, -2.0, DECK_Z + 30.0))
cyl("cranepost", CR_BASE + Vector((0, 0, 6)), 1.6, 12, YEL, coll=SHIPC, verts=16)
box("cranecab", CR_BASE + Vector((0, 0, 13.5)), (4.5, 4.5, 3.5), YEL, coll=SHIPC, bevel=0.3)
rod("cranejib", CR_BASE + Vector((0, 0, 14)), CR_TIP, 0.7, YEL, coll=SHIPC, verts=8)
HOOK_Z0 = DECK_Z + 12.0
CABLE = rod("cable", CR_TIP, Vector((CR_TIP.x, CR_TIP.y, HOOK_Z0 + 1.2)), 0.08, mat("cablem", (0.1, 0.1, 0.1)), coll=SHIPC, verts=6)
HOOK = empty("hook", (CR_TIP.x, CR_TIP.y, HOOK_Z0), coll=SHIPC)
box("hookblock", (0, 0, 0.6), (1.2, 0.8, 1.2), YEL, parent=HOOK, coll=SHIPC, bevel=0.15)
for k, (yy, zz) in enumerate(((0, -0.4), (0, -1.0))): box("hookc", (0.0, 0.0, zz), (0.35, 0.35, 0.7), mat("hookm", (0.25, 0.25, 0.28), 0.3), parent=HOOK, coll=SHIPC)
box("hookbend", (0.35, 0, -1.35), (0.9, 0.35, 0.35), mat("hookm", (0.25, 0.25, 0.28), 0.3), parent=HOOK, coll=SHIPC)
SHIP_OBJS = [o for o in SHIPC.objects]
def ship_on(on=True):
    SHIPC.hide_render = not on
def wall_reset():
    for o in WALL:
        if o.animation_data: o.animation_data_clear()
        o.location = o["home"]; o.rotation_euler = (0, 0, 0)

# ---------------------------------------------------------------- SKIFF (built along +X), floor top at SKIFF_FLOOR (local)
SKIFF_FLOOR = 1.15
def mk_skiff(coll=None, col=(0.92, 0.92, 0.88), stripe=(0.1, 0.55, 0.75)):
    coll = coll or TEMP; r = empty("skiff", coll=coll); hm = mat(f"skiffm{col}", col, 0.5); sm = mat(f"skiffs{stripe}", stripe, 0.5)
    L, W = 20.0, 6.8
    box("sk_bottom", (0, 0, 0.35), (L, W - 0.6, 1.6), hm, parent=r, coll=coll, bevel=0.3)
    for sy in (-1, 1):
        box("sk_side", (0, sy * (W / 2 - 0.25), 1.6), (L, 0.5, 2.2), hm, parent=r, coll=coll, bevel=0.15)
        box("sk_stripe", (0, sy * (W / 2 + 0.02), 1.9), (L - 0.4, 0.06, 0.45), sm, parent=r, coll=coll)
    box("sk_stern", (-L / 2 + 0.25, 0, 1.6), (0.5, W, 2.2), hm, parent=r, coll=coll)
    bm = bmesh.new(); hw = W / 2; x0 = L / 2
    vs = [bm.verts.new(v) for v in [(x0, -hw, -0.4), (x0, hw, -0.4), (x0 + 3.0, 0, 0.6), (x0, -hw, 2.7), (x0, hw, 2.7), (x0 + 5.0, 0, 2.9)]]
    for fa in [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]: bm.faces.new([vs[i] for i in fa])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("skbow"); bm.to_mesh(me); bm.free(); me.materials.append(hm)
    bo = bpy.data.objects.new("sk_bow", me); coll.objects.link(bo); bo.parent = r
    box("sk_floor", (0, 0, SKIFF_FLOOR - 0.1), (L - 0.8, W - 1.0, 0.2), mat("skfloor", (0.55, 0.38, 0.22), 0.8), parent=r, coll=coll)
    # outboard motor
    box("motor", (-L / 2 - 0.9, 0, 2.6), (1.6, 1.4, 2.4), mat("motorm", (0.12, 0.12, 0.14), 0.4), parent=r, coll=coll, bevel=0.3)
    box("motorleg", (-L / 2 - 1.0, 0, 0.3), (0.5, 0.4, 2.6), mat("motorm", (0.12, 0.12, 0.14), 0.4), parent=r, coll=coll)
    # pennant: black flag with a white hat icon
    box("pole", (-L / 2 + 1.0, 2.6, 5.0), (0.2, 0.2, 7.0), RAILM, parent=r, coll=coll)
    fl = box("pennant", (-L / 2 - 0.6, 2.6, 7.6), (3.0, 0.08, 1.8), mat("flagblk", (0.03, 0.03, 0.04)), parent=r, coll=coll)
    box("flaghat", (-L / 2 - 0.6, 2.54, 7.6), (1.6, 0.05, 0.55), WHITE, parent=r, coll=coll)
    r["L"] = L; return r
def wake(boat, f0, f1, coll=None, length=26, width=10):
    """V of white foam behind a moving boat: parented strips that ride with the hull"""
    coll = coll or TEMP; fm = emat("foam", (0.95, 0.98, 1.0), 0.4)
    out = []
    for sy in (-1, 1):
        o = box("wake", (-boat["L"] / 2 - length / 2, sy * width / 4, 0.15), (length, 1.2, 0.12), fm, rot=(0, 0, -sy * 0.22), parent=boat, coll=coll); out.append(o)
    out.append(box("wakec", (-boat["L"] / 2 - 6, 0, 0.12), (12, 3.2, 0.1), fm, parent=boat, coll=coll))
    return out
def mk_lifeboat(coll=None):
    coll = coll or TEMP; r = empty("lifeboat", coll=coll); om = mat("lbor", (1.0, 0.42, 0.05), 0.5)
    box("lb_hull", (0, 0, 0.6), (16, 6.2, 2.4), om, parent=r, coll=coll, bevel=0.6)
    box("lb_white", (0, 0, 1.6), (15.6, 6.0, 0.4), WHITE, parent=r, coll=coll)
    box("lb_rail", (0, 0, 1.95), (15.0, 5.4, 0.3), om, parent=r, coll=coll, bevel=0.1)
    box("lb_floor", (0, 0, 1.0), (14.4, 4.8, 0.2), mat("lbfloor", (0.7, 0.7, 0.68)), parent=r, coll=coll)
    box("lb_motor", (-8.6, 0, 1.6), (1.4, 1.2, 2.0), mat("motorm", (0.12, 0.12, 0.14), 0.4), parent=r, coll=coll, bevel=0.2)
    r["L"] = 16.0; r["floor"] = 1.1; return r

# ---------------------------------------------------------------- ARMS + KIT (props parented to the Char rig)
GUNM = mat("gunm", (0.12, 0.12, 0.14), 0.35); GUNW = mat("gunw", (0.42, 0.26, 0.12), 0.7); RPGG = mat("rpgg", (0.28, 0.42, 0.18), 0.6)
def rifle(c, hand=1):
    """chunky toy-proportioned rifle along the arm (arm local -Z = pointing direction)"""
    a = c.arms[hand]; g = empty("rifle", (0, 0, 0), parent=a, coll=c.coll)
    box("r_stock", (0, -0.05, -1.25), (0.42, 0.5, 1.2), GUNW, parent=g, coll=c.coll, bevel=0.08)
    box("r_body", (0, -0.15, -2.45), (0.5, 0.7, 1.4), GUNM, parent=g, coll=c.coll, bevel=0.08)
    box("r_mag", (0, 0.55, -2.35), (0.36, 0.7, 0.5), GUNM, parent=g, coll=c.coll)
    box("r_guard", (0, -0.12, -3.5), (0.44, 0.55, 0.9), GUNW, parent=g, coll=c.coll, bevel=0.06)
    cyl("r_barrel", (0, -0.2, -4.4), 0.12, 1.3, GUNM, parent=g, coll=c.coll, verts=10)
    c.gun_tip = Vector((0, -0.2, -5.05)); c.gun = g; return g
def rpg(c, hand=1):
    a = c.arms[hand]; g = empty("rpg", (0, 0, 0), parent=a, coll=c.coll)
    cyl("rpg_tube", (0, -0.95, -1.4), 0.42, 5.2, RPGG, parent=g, coll=c.coll, verts=14)
    cone("rpg_head", (0, -0.95, -4.55), 0.62, 1.3, mat("rpghead", (0.35, 0.36, 0.3), 0.4), verts=12, parent=g, coll=c.coll, rot=(math.pi, 0, 0))
    box("rpg_grip", (0, -0.4, -1.9), (0.3, 0.6, 0.35), GUNM, parent=g, coll=c.coll)
    c.gun_tip = Vector((0, -0.95, -5.4)); c.gun_back = Vector((0, -0.95, 1.2)); c.gun = g; return g
def aim_pose(c, f, lean=0.0, twist=0.0, head=(0, 0, 0)):
    c.pose(f, arms=(1.48, 1.56), arms_side=(-0.42, 0.0), head=head, lean=lean, twist=twist)
def rpg_pose(c, f, up=0.0, head=(0, 0, 0)):
    c.pose(f, arms=(1.5 + up, 1.5 + up), arms_side=(-0.5, 0.0), head=(head[0] - up * 0.5, head[1], head[2]))
def salute_pose(c, f):
    c.pose(f, arms=(0, 2.55), arms_side=(0, 0.95), head=(0.05, 0, 0))
def bandana(c, col, tails=True):
    m = mat(f"band{col}", col, 0.6)
    box("bandana", (0, 0.02, 0.62), (1.36, 1.34, 0.36), m, parent=c.head, coll=c.coll, bevel=0.1)
    if tails:
        for k, (rz, dz) in enumerate(((0.5, -0.1), (-0.4, -0.35))):
            box("btail", (0.18 - k * 0.3, 0.78, 0.45 + dz), (0.24, 0.12, 0.7), m, rot=(0.3, 0, rz), parent=c.head, coll=c.coll)
def eyepatch(c, side=1):
    bk = mat("patchm", (0.02, 0.02, 0.02), 0.6)
    box("patch", (side * 0.24, -0.655, 0.12), (0.36, 0.04, 0.3), bk, parent=c.head, coll=c.coll)
    box("strap", (0, -0.02, 0.32), (1.32, 1.32, 0.07), bk, rot=(0.0, side * 0.35, 0), parent=c.head, coll=c.coll)
def goggles(c):
    gm = mat("gogm", (0.35, 0.22, 0.1), 0.5); lm = mat("goglens", (0.3, 0.7, 0.9), 0.1)
    box("gogstrap", (0, 0.02, 0.5), (1.34, 1.34, 0.16), gm, parent=c.head, coll=c.coll)
    for sx in (-0.28, 0.28): cyl("goglens", (sx, -0.68, 0.52), 0.22, 0.14, lm, rot=(math.pi / 2, 0, 0), parent=c.head, coll=c.coll, verts=14)
def tiny_tricorn(c):
    m = mat("tricm", (0.06, 0.05, 0.05), 0.6)
    box("tric_crown", (0, 0.02, 0.92), (1.0, 1.0, 0.4), m, parent=c.head, coll=c.coll, bevel=0.1)
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        box("tric_brim", (math.cos(a) * 0.45, math.sin(a) * 0.45, 0.76), (1.3, 0.35, 0.12), m, rot=(0, 0, a + math.pi / 2), parent=c.head, coll=c.coll)
def vest(c, col):
    m = mat(f"vest{col}", col, 0.7)
    for sx in (-1, 1): box("vestp", (sx * 0.62, -0.53, 1.05), (0.7, 0.09, 1.9), m, parent=c.hips, coll=c.coll, bevel=0.03)
    box("vestback", (0, 0.53, 1.05), (2.02, 0.09, 1.95), m, parent=c.hips, coll=c.coll)
def long_coat(c, col, trim=(1.0, 0.78, 0.1)):
    m = mat(f"lcoat{col}", col, 0.6); tm = mat(f"lctrim{trim}", trim, 0.3)
    box("lcoat", (0, 0, 0.9), (2.24, 1.2, 2.25), m, parent=c.hips, coll=c.coll, bevel=0.2)
    for sx in (-1, 1): box("lcoattail", (sx * 0.62, 0.15, -0.65), (0.98, 1.06, 1.3), m, rot=(0, sx * 0.08, 0), parent=c.hips, coll=c.coll, bevel=0.1)
    for k in range(3): sphere("btn", (0.32, -0.62, 0.5 + k * 0.5), 0.1, tm, coll=c.coll, parent=c.hips, seg=8)
    for a in c.arms: box("lcsleeve", (0, 0, -0.72), (1.08, 1.08, 1.5), m, parent=a, coll=c.coll, bevel=0.2)
def coveralls(c, col=(1.0, 0.45, 0.06)):
    m = mat(f"cover{col}", col, 0.6); hv = mat("hivis", (0.85, 0.95, 0.85), 0.3)
    recolor(c, ("torso", "sleeve", "leg"), m)
    box("hvstripe", (0, -0.52, 0.6), (2.04, 0.06, 0.22), hv, parent=c.hips, coll=c.coll)
    for a in c.arms: box("hvsl", (0, 0, -0.55), (1.0, 1.0, 0.18), hv, parent=a, coll=c.coll)
def hardhat(c):
    m = mat("hardhat", (0.97, 0.97, 0.95), 0.35)
    box("hh_crown", (0, 0.04, 0.86), (1.42, 1.42, 0.55), m, parent=c.head, coll=c.coll, bevel=0.22)
    box("hh_brim", (0, -0.2, 0.62), (1.6, 1.8, 0.1), m, parent=c.head, coll=c.coll, bevel=0.04)
def toque(c):
    m = mat("toquem", (1, 1, 1), 0.7)
    box("toque_band", (0, 0.03, 0.85), (1.34, 1.34, 0.5), m, parent=c.head, coll=c.coll, bevel=0.1)
    box("toque_top", (0, 0.03, 1.75), (1.6, 1.6, 1.4), m, parent=c.head, coll=c.coll, bevel=0.45)
    c.hat_top = 2.45
def apron(c):
    m = mat("apronm", (0.97, 0.97, 0.97), 0.7)
    box("apron", (0, -0.54, 0.6), (1.6, 0.08, 2.0), m, parent=c.hips, coll=c.coll)
def ladle(c, hand=1):
    m = mat("ladlem", (0.75, 0.76, 0.8), 0.25)
    box("ladle_h", (0, -0.3, -2.4), (0.18, 0.18, 1.6), m, parent=c.arms[hand], coll=c.coll)
    sphere("ladle_cup", (0, -0.3, -3.25), 0.38, m, coll=c.coll, parent=c.arms[hand], seg=10)
def shades(c):
    m = mat("shadesm", (0.02, 0.02, 0.03), 0.05)
    box("shades", (0, -0.66, 0.18), (1.2, 0.05, 0.3), m, parent=c.head, coll=c.coll)
def peaked_cap(c):
    m = mat("pcap", (0.97, 0.97, 0.97), 0.5); n = mat("pcapn", (0.05, 0.08, 0.2), 0.5)
    box("pc_crown", (0, 0.04, 0.84), (1.5, 1.5, 0.42), m, parent=c.head, coll=c.coll, bevel=0.1)
    box("pc_band", (0, 0.04, 0.68), (1.38, 1.38, 0.2), n, parent=c.head, coll=c.coll)
    box("pc_peak", (0, -0.78, 0.6), (1.2, 0.5, 0.08), n, parent=c.head, coll=c.coll)
    c.hat_top = 1.06
def epaulettes(c):
    n = mat("epn", (0.05, 0.08, 0.2), 0.5); g = mat("epg", (1, 0.8, 0.2), 0.3)
    for a in c.arms:
        box("epau", (0, 0, 0.05), (1.05, 1.05, 0.14), n, parent=a, coll=c.coll)
        box("epaug", (0, -0.4, 0.06), (1.0, 0.1, 0.12), g, parent=a, coll=c.coll)
def juicebox(c, hand=1):
    box("juice", (0, -0.3, -2.0), (0.5, 0.35, 0.7), mat("juicem", (0.95, 0.35, 0.6), 0.5), parent=c.arms[hand], coll=c.coll)
    box("straw", (0.1, -0.3, -1.55), (0.06, 0.06, 0.5), mat("strawm", (1, 1, 1)), rot=(0, 0.3, 0), parent=c.arms[hand], coll=c.coll)

# ---------------------------------------------------------------- THE HAT (hero prop): oversized black bicorne, gold trim, red feather
HATC = collection("hat")
HAT = empty("HAT", coll=HATC)
def _build_hat():
    bk = mat("hatblk", (0.025, 0.022, 0.03), 0.5); gd = mat("hatgold", (1.0, 0.74, 0.12), 0.25); rd = mat("hatfeather", (0.9, 0.06, 0.08), 0.7)
    box("hat_crown", (0, 0, 0.22), (1.5, 1.45, 0.44), bk, parent=HAT, coll=HATC, bevel=0.12)
    def crescent(name, R, th, y, zs, m, z0=0.3):
        bm = bmesh.new(); n = 18; top = []; bot = []
        for i in range(n + 1):
            a = math.pi * i / n; x = -math.cos(a) * R; z = z0 + math.sin(a) * R * zs - 0.25 * (1 - math.sin(a))   # tips dip down a bit
            top.append(bm.verts.new((x, y - th / 2, z))); bot.append(bm.verts.new((x, y + th / 2, z)))
        cf = bm.verts.new((0, y - th / 2, z0 - 0.1)); cb = bm.verts.new((0, y + th / 2, z0 - 0.1))
        for i in range(n):
            bm.faces.new((cf, top[i + 1], top[i])); bm.faces.new((cb, bot[i], bot[i + 1])); bm.faces.new((top[i], top[i + 1], bot[i + 1], bot[i]))
        bm.faces.new((cf, top[0], bot[0], cb)); bm.faces.new((cb, bot[n], top[n], cf))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
        o = bpy.data.objects.new(name, me); HATC.objects.link(o); o.parent = HAT; return o
    crescent("hat_wing", 1.75, 0.62, 0.0, 0.78, bk)
    crescent("hat_trim", 1.88, 0.42, 0.0, 0.8, gd)      # gold rim peeks out around the black wing
    sphere("hat_cockade", (0.0, -0.36, 0.75), 1, gd, coll=HATC, parent=HAT, seg=12, scale=(0.3, 0.1, 0.3))
    sphere("hat_feather", (0.35, 0.05, 1.9), 1, rd, coll=HATC, parent=HAT, scale=(0.25, 0.22, 1.1))
_build_hat()
HAT_ON = 0.76   # head-local z of the hair top: hat base sits here
def hat_on_head(c, f, extra=0.0, tilt=0.0):
    """key the hat on c's head at frame f (world-space, follows the rig)"""
    S.frame_set(f); mw = c.head.matrix_world
    top = getattr(c, "hat_top", None); z = (top if top else HAT_ON) + extra
    p = mw @ Vector((0, 0, z)); r = mw.to_euler()
    HAT.location = p; HAT.rotation_euler = (r.x + tilt, r.y, r.z); HAT.scale = (mw.to_scale().x / 1.04,) * 3
    HAT.keyframe_insert("location", frame=f); HAT.keyframe_insert("rotation_euler", frame=f); HAT.keyframe_insert("scale", frame=f)
def hat_follow(c, f0, f1, extra=0.0):
    for f in range(f0, f1 + 1): hat_on_head(c, f, extra)
def hat_key(f, loc, rot=(0, 0, 0), sc=1.0):
    HAT.location = loc; HAT.rotation_euler = rot; HAT.scale = (sc,) * 3
    HAT.keyframe_insert("location", frame=f); HAT.keyframe_insert("rotation_euler", frame=f); HAT.keyframe_insert("scale", frame=f)
def hat_arc(f0, f1, a, b, h=6.0, spins=1.5, sc0=1.0, sc1=1.0, rz0=0.0):
    a, b = Vector(a), Vector(b)
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); p = a.lerp(b, u) + Vector((0, 0, 4 * h * u * (1 - u)))
        hat_key(f, p, (0.4 * math.sin(u * 6), spins * 2 * math.pi * u, rz0 + 1.2 * u), sc0 + (sc1 - sc0) * u)

# ---------------------------------------------------------------- SEAGULL + DOLPHIN
class Gull:
    def __init__(self, coll=None, scale=1.0):
        coll = coll or TEMP; self.root = empty("gull", coll=coll); self.root.scale = (scale,) * 3
        w = mat("gullw", (0.97, 0.97, 0.95), 0.6); g = mat("gullg", (0.55, 0.58, 0.62), 0.6); y = mat("gully", (1.0, 0.72, 0.1), 0.4); k = mat("gullk", (0.02, 0.02, 0.02), 0.3)
        b = self.body = empty("gbody", (0, 0, 1.3), self.root, coll)
        box("g_body", (0, 0.2, 0), (1.3, 2.2, 1.25), w, parent=b, coll=coll, bevel=0.4)
        box("g_tail", (0, 1.5, 0.15), (0.9, 0.8, 0.3), g, rot=(-0.25, 0, 0), parent=b, coll=coll)
        h = self.head = empty("ghead", (0, -0.95, 0.85), b, coll)
        box("g_head", (0, 0, 0), (1.0, 1.0, 0.95), w, parent=h, coll=coll, bevel=0.3)
        box("g_beak", (0, -0.75, -0.1), (0.3, 0.75, 0.26), y, parent=h, coll=coll, bevel=0.06)
        box("g_beakdot", (0, -0.98, -0.18), (0.31, 0.2, 0.1), mat("gullr", (0.85, 0.1, 0.05)), parent=h, coll=coll)
        for sx in (-1, 1):
            box("g_eye", (sx * 0.51, -0.18, 0.12), (0.04, 0.24, 0.13), k, parent=h, coll=coll)     # half-lidded smug slits
            box("g_lid", (sx * 0.515, -0.18, 0.24), (0.04, 0.3, 0.12), g, parent=h, coll=coll)
        self.wings = []
        for sx in (-1, 1):
            wp = empty("gwing", (sx * 0.62, 0.1, 0.3), b, coll)
            box("g_wing", (sx * 1.3, 0.1, 0), (2.6, 1.3, 0.12), g, parent=wp, coll=coll, bevel=0.05)
            box("g_wtip", (sx * 2.5, 0.2, 0), (0.8, 1.1, 0.13), k, parent=wp, coll=coll)
            self.wings.append((wp, sx))
        self.legs = []
        for sx in (-0.3, 0.3):
            box("g_leg", (sx, 0.2, 0.4), (0.12, 0.12, 0.8), y, parent=self.root, coll=coll)
            box("g_foot", (sx, 0.0, 0.05), (0.35, 0.5, 0.08), y, parent=self.root, coll=coll)
        self.hat_z = 2.55   # root-local height of the head top (hat base)
    def fold(self, f, a=0.0):
        """wings folded back along the body sides (a>0 = half open, puffed up)"""
        for wp, sx in self.wings: wp.rotation_euler = (0, -sx * (0.15 + a), sx * (math.pi / 2 - a)); wp.keyframe_insert("rotation_euler", frame=f)
    def flap(self, f0, f1, speed=4.0, amp=0.9, base=0.2):
        for f in range(f0, f1 + 1):
            a = base + amp * math.sin(f / 24 * speed * 2 * math.pi)
            for wp, sx in self.wings: wp.rotation_euler = (0, -sx * a, 0); wp.keyframe_insert("rotation_euler", frame=f)
    def head_key(f, *a): pass
class Dolphin:
    def __init__(self, coll=None, scale=1.0):
        coll = coll or TEMP; self.root = empty("dolphin", coll=coll); self.root.scale = (scale,) * 3
        g = mat("dolg", (0.38, 0.48, 0.58), 0.35); l = mat("doll", (0.82, 0.86, 0.9), 0.4); k = mat("gullk", (0.02, 0.02, 0.02), 0.3)
        b = self.body = self.root
        box("d_body", (0, 0, 0), (1.9, 5.6, 1.9), g, parent=b, coll=coll, bevel=0.75)
        box("d_belly", (0, -0.4, -0.55), (1.5, 4.0, 0.9), l, parent=b, coll=coll, bevel=0.4)
        box("d_snout", (0, -3.3, -0.3), (0.8, 1.6, 0.6), g, parent=b, coll=coll, bevel=0.25)
        box("d_grin", (0, -3.1, -0.48), (0.86, 1.0, 0.07), k, parent=b, coll=coll)
        for sx in (-1, 1):
            box("d_eye", (sx * 0.9, -2.0, 0.25), (0.08, 0.3, 0.3), k, parent=b, coll=coll)
            box("d_flip", (sx * 1.25, -0.8, -0.6), (1.4, 0.8, 0.15), g, rot=(0, sx * 0.4, sx * 0.4), parent=b, coll=coll)
        box("d_fin", (0, 0.4, 1.3), (0.2, 1.5, 1.4), g, rot=(-0.5, 0, 0), parent=b, coll=coll)
        box("d_tail", (0, 3.2, 0), (0.8, 1.4, 0.8), g, parent=b, coll=coll, bevel=0.3)
        box("d_fluke", (0, 4.0, 0), (3.0, 0.8, 0.18), g, parent=b, coll=coll, bevel=0.08)
        self.hat_z = 0.95

# ---------------------------------------------------------------- FX3D: muzzle flash, tracer, boom, splash, water column, smoke trail, knockback
FLASHM = emat("flashm", (1.0, 0.75, 0.25), 25.0); FIREM = emat("firem", (1.0, 0.38, 0.05), 5.0); FIRE2 = emat("fire2", (1.0, 0.75, 0.25), 7.0)
SMOKEM = mat("smokem", (0.33, 0.33, 0.35), 0.95); SMOKEW = mat("smokew", (0.85, 0.85, 0.86), 0.95)
SPRAYM = mat("spraym", (0.92, 0.96, 1.0), 0.3); FOAMM = emat("foamm", (0.95, 0.98, 1.0), 0.35)
TRACEM = emat("tracem", (1.0, 0.9, 0.5), 30.0)
def _scale_keys(o, keys):
    for f, s in keys:
        o.scale = (s,) * 3 if not isinstance(s, (tuple, list)) else s; o.keyframe_insert("scale", frame=f)
def muzzle(loc, f, size=1.0, coll=None, direction=None):
    coll = coll or TEMP; e = empty("muzzle", Vector(loc), coll=coll)
    for k in range(3):
        sphere("mzl", (0, 0, 0), 1, FLASHM if k else FIRE2, coll=coll, parent=e, seg=8, scale=(0.5, 0.5, 0.5))
    _scale_keys(e, [(f - 1, 0.001), (f, size * 1.4), (f + 1, size * 0.8), (f + 2, 0.001)])
    L = light("mzlL", "POINT", Vector(loc), 0, (1, 0.7, 0.35), coll=coll, radius=0.5); L.data.use_shadow = False
    for ff, en in ((f - 1, 0), (f, 4000 * size), (f + 2, 0)): L.data.energy = en; L.data.keyframe_insert("energy", frame=ff)
    return e
def tracer(a, b, f0, frames=3, coll=None):
    coll = coll or TEMP; a, b = Vector(a), Vector(b)
    t = rod("tracer", Vector((0, 0, 0)), Vector((0, 0, 3.0)), 0.09, TRACEM, coll=coll, verts=6)
    d = (b - a).normalized(); q = d.to_track_quat("Z", "Y"); t.rotation_mode = "QUATERNION"; t.rotation_quaternion = q
    for k in range(frames + 1):
        t.location = a.lerp(b, k / frames); t.keyframe_insert("location", frame=f0 + k)
    vis(t, f0 - 1, False); vis(t, f0, True); vis(t, f0 + frames + 1, False)
    return t
def boom(loc, f0, size=1.0, coll=None, smoke=True, light_e=60000):
    """cartoon explosion: fireball spheres pop + grow, swap to grey smoke puffs that rise; flash light"""
    coll = coll or TEMP; loc = Vector(loc); rnd = random.Random(int(f0 * 7 + loc.x))
    fb = []
    for k in range(7):
        off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 1))) * 2.2 * size
        o = sphere("fire", loc + off, 1, FIRE2 if k < 3 else FIREM, coll=coll, seg=12)
        r = rnd.uniform(1.6, 2.8) * size
        _scale_keys(o, [(f0 - 1, 0.001), (f0, r * 0.5), (f0 + 3, r), (f0 + 7, r * 0.8), (f0 + 10, 0.001)]); fb.append(o)
    if smoke:
        for k in range(10):
            off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 1.2))) * 2.6 * size
            o = sphere("smoke", loc + off, 1, SMOKEM if k % 3 else SMOKEW, coll=coll, seg=10)
            r = rnd.uniform(1.8, 3.2) * size
            _scale_keys(o, [(f0 + 4, 0.001), (f0 + 8, r), (f0 + 40, r * 1.3), (f0 + 60, 0.001)])
            o.keyframe_insert("location", frame=f0 + 6); o.location = o.location + Vector((rnd.uniform(-2, 2), rnd.uniform(-2, 2), 9 * size)); o.keyframe_insert("location", frame=f0 + 60)
    L = light("boomL", "POINT", loc + Vector((0, 0, 3 * size)), 0, (1, 0.6, 0.25), coll=coll, radius=3 * size); L.data.use_shadow = False
    for ff, en in ((f0 - 1, 0), (f0, light_e * size), (f0 + 6, light_e * size * 0.4), (f0 + 14, 0)): L.data.energy = en; L.data.keyframe_insert("energy", frame=ff)
    # flat shockwave ring
    ring = cyl("shock", loc + Vector((0, 0, 0.3)), 1.0, 0.15, emat("shockm", (1, 0.9, 0.7), 3.0), coll=coll, verts=32)
    _scale_keys(ring, [(f0, (0.1, 0.1, 1)), (f0 + 6, (9 * size, 9 * size, 1)), (f0 + 7, (0.001, 0.001, 0.001))])
    return fb
def splash(loc, f0, size=1.0, coll=None, n=26, crown=True):
    """water splash: ballistic white droplets + rising crown + foam disc. loc z = sea surface"""
    coll = coll or TEMP; loc = Vector(loc); rnd = random.Random(int(f0 * 13 + loc.x * 3 + loc.y))
    g = 9.8 * 2.2
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(2.5, 7.0) * size; vz = rnd.uniform(6, 13) * math.sqrt(size)
        o = sphere("drop", loc, 1, SPRAYM, coll=coll, seg=6); r = rnd.uniform(0.22, 0.5) * size
        vis(o, f0 - 1, False); vis(o, f0, True)
        T = 2 * vz / g; nf = max(4, int(T * FPS))
        for i in range(nf + 1):
            t = i / FPS; o.location = loc + Vector((math.cos(a) * sp * t, math.sin(a) * sp * t, vz * t - 0.5 * g * t * t)); o.keyframe_insert("location", frame=f0 + i)
            o.scale = (r,) * 3; o.keyframe_insert("scale", frame=f0 + i)
        o.scale = (0.001,) * 3; o.keyframe_insert("scale", frame=f0 + nf + 1)
    if crown:   # ring of stretched spray blobs that shoot up and fall back
        for k in range(12):
            a = k / 12 * 2 * math.pi; o = sphere("crown", loc, 1, SPRAYM, coll=coll, seg=8)
            for f, rr, z, s in ((f0 - 1, 0.5, 0, 0.001), (f0, 1.0, 0.5, 0.5), (f0 + 5, 2.2, 3.2, 0.75), (f0 + 10, 3.0, 3.6, 0.6), (f0 + 16, 3.6, 0.6, 0.35), (f0 + 18, 3.7, 0, 0.001)):
                o.location = loc + Vector((math.cos(a) * rr * size, math.sin(a) * rr * size, z * size)); o.keyframe_insert("location", frame=f)
                o.scale = (s * size, s * size, s * size * 2.2); o.keyframe_insert("scale", frame=f)
def water_column(loc, f0, height=14.0, coll=None):
    """cannon-shell miss: tall white column that rises and collapses + a splash ring"""
    coll = coll or TEMP; loc = Vector(loc)
    rnd = random.Random(int(f0 * 5 + loc.x))
    for k in range(7):
        o = sphere("colm", loc, 1, SPRAYM, coll=coll, seg=10)
        h = height * (0.25 + 0.12 * k); loc = Vector(loc) + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0))
        for f, z, s in ((f0 - 1, 0, 0.001), (f0, 1, 1.4), (f0 + 5, h, 1.8 - 0.25 * k), (f0 + 12, h * 1.05, 1.6 - 0.2 * k), (f0 + 22, 0.5, 0.9), (f0 + 26, 0, 0.001)):
            o.location = loc + Vector((0, 0, z)); o.keyframe_insert("location", frame=f); o.scale = (s, s, s * 1.6); o.keyframe_insert("scale", frame=f)
    splash(loc, f0, 1.2, coll=coll, n=16, crown=False)
def smoke_trail(path_pts, f0, f1, coll=None, every=1, size=0.7):
    """puffs dropped behind a moving point (rocket)"""
    coll = coll or TEMP
    for i, (f, p) in enumerate(path_pts):
        if i % every: continue
        o = sphere("trail", Vector(p), 1, SMOKEW, coll=coll, seg=8)
        _scale_keys(o, [(f - 1, 0.001), (f, size * 0.5), (f + 10, size * 1.6), (f + 30, size * 2.0), (f + 40, 0.001)])
def rocket(coll=None):
    coll = coll or TEMP; r = empty("rocket", coll=coll)
    cyl("rk_body", (0, 0, 0), 0.4, 2.2, RPGG, coll=coll, parent=r, verts=12)
    cone("rk_nose", (0, 0, 1.6), 0.55, 1.1, mat("rpghead", (0.35, 0.36, 0.3), 0.4), verts=12, coll=coll, parent=r)
    fl = sphere("rk_flame", (0, 0, -1.4), 1, FIRE2, coll=coll, parent=r, seg=8, scale=(0.35, 0.35, 0.8))
    r.rotation_mode = "QUATERNION"; return r
def fly_rocket(r, pts, f0, f1, trail=True):
    P = [Vector(p) for p in pts]; out = []
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0)
        if len(P) == 2: p = P[0].lerp(P[1], u); d = P[1] - P[0]
        else:   # quadratic bezier
            p = (1 - u) ** 2 * P[0] + 2 * (1 - u) * u * P[1] + u * u * P[2]; d = 2 * (1 - u) * (P[1] - P[0]) + 2 * u * (P[2] - P[1])
        r.location = p; r.rotation_quaternion = d.normalized().to_track_quat("Z", "Y")
        r.keyframe_insert("location", frame=f); r.keyframe_insert("rotation_quaternion", frame=f); out.append((f, p.copy()))
    if trail: smoke_trail(out[1:], f0, f1, every=1)
    return out
def knockback(c, f0, a, b, h=8.0, frames=18, spin=1.0):
    """ballistic arc a->b with tumble + flailing (no injuries): ends in the water"""
    a, b = Vector(a), Vector(b)
    for i in range(frames + 1):
        u = i / frames; p = a.lerp(b, u) + Vector((0, 0, 4 * h * u * (1 - u)))
        c.root.location = p; c.root.keyframe_insert("location", frame=f0 + i)
        c.root.rotation_euler = (spin * 2.4 * u, 0.6 * math.sin(u * 5), c.root.rotation_euler.z); c.root.keyframe_insert("rotation_euler", frame=f0 + i)
        c.pose(f0 + i, arms=(2.6 + 0.5 * math.sin(i), 2.6 - 0.5 * math.sin(i)), arms_side=(0.8, 0.8), legs=(0.5 * math.sin(i * 1.3), -0.5 * math.sin(i * 1.3)))
    c.set_face("excited", f0)

# ---------------------------------------------------------------- CAST (generic pirate kit, mixed town skin tones)
def combo(*fs):
    def f(c):
        for g in fs: g(c)
    return f
def _shirt(c, m): recolor(c, ("torso", "sleeve"), m)
def mk_bev():
    c = Char("bev", TEMP, (0.62, 0.42, 0.28), (0.7, 0.08, 0.1), (0.15, 0.12, 0.12), hair="short", hair_col=(0.62, 0.62, 0.65), scale=1.08)
    long_coat(c, (0.62, 0.05, 0.08)); return c
def mk_toby():
    c = Char("toby", TEMP, (0.95, 0.78, 0.62), (0.2, 0.7, 0.7), (0.3, 0.22, 0.14), hair="short", hair_col=(0.45, 0.25, 0.1), scale=1.02)
    _shirt(c, stripes("tobystripe", (0.1, 0.62, 0.62), (0.96, 0.96, 0.94), 2.4)); vest(c, (0.4, 0.24, 0.12)); bandana(c, (1.0, 0.8, 0.1)); return c
def mk_dale():
    c = Char("dale", TEMP, (0.35, 0.22, 0.13), (0.4, 0.45, 0.25), (0.25, 0.22, 0.18), hair="fade", hair_col=(0.05, 0.03, 0.02), scale=1.1)
    vest(c, (0.32, 0.38, 0.18)); bandana(c, (1.0, 0.45, 0.08), tails=False); goggles(c); return c
def mk_kevin():
    c = Char("kevin", TEMP, (0.88, 0.68, 0.5), (0.5, 0.2, 0.7), (0.2, 0.2, 0.25), hair="short", hair_col=(0.8, 0.5, 0.15), scale=0.82)
    _shirt(c, stripes("kevstripe", (0.45, 0.15, 0.65), (0.95, 0.95, 0.95), 2.6)); eyepatch(c); tiny_tricorn(c); return c
def mk_crew(i):
    cols = [((0.7, 0.1, 0.1), (0.25, 0.15, 0.1), (0.75, 0.55, 0.4), "spiky", (0.1, 0.05, 0.02)),
            ((0.12, 0.25, 0.7), (0.2, 0.2, 0.25), (0.45, 0.3, 0.2), "afro", (0.05, 0.03, 0.02))][i % 2]
    sc, pa, sk, hr, hc = cols
    c = Char(f"crew{i}", TEMP, sk, sc, pa, hair=hr, hair_col=hc, scale=1.0)
    _shirt(c, stripes(f"crewstripe{i}", sc, (0.95, 0.95, 0.95), 2.4))
    if hr != "afro": bandana(c, (0.15, 0.15, 0.18), tails=False)
    return c
def mk_cook():
    c = Char("cook", TEMP, (0.75, 0.52, 0.36), (0.96, 0.96, 0.96), (0.2, 0.2, 0.24), hair="short", hair_col=(0.1, 0.06, 0.03), scale=1.12)
    apron(c); toque(c); ladle(c); return c
def mk_giant():
    c = Char("giant", TEMP, (0.9, 0.72, 0.58), (0.97, 0.97, 0.97), (0.95, 0.95, 0.95), hair="short", hair_col=(0.35, 0.3, 0.28), scale=2.6)
    epaulettes(c); peaked_cap(c); shades(c); juicebox(c); return c
CARGO_SKIN = [(0.95, 0.78, 0.62), (0.45, 0.27, 0.16), (0.8, 0.6, 0.45), (0.3, 0.18, 0.1), (0.6, 0.4, 0.25)]
def mk_cargo(i):
    c = Char(f"cargo{i}", TEMP, CARGO_SKIN[i % 5], (1.0, 0.45, 0.06), (1.0, 0.45, 0.06), hair="short", hair_col=(0.1, 0.06, 0.03), scale=1.0 + 0.05 * (i % 3))
    coveralls(c); hardhat(c); return c
