import sys, os, math, random
sys.argv = [sys.argv[0], "--", "none"]; os.environ["HOOD"] = "1"
exec(open("/home/claude/zara/world.py").read())
exec(open("/home/claude/zara/eevee_patch.py").read())
exec(open("/home/claude/zara/town/rcast.py").read())
from mathutils import Vector
WORLD.hide_render = True; ROOM.hide_render = True
SUN = [o for o in S.objects if o.type == "LIGHT" and o.data.type == "SUN"][0]; WBG = S.world.node_tree.nodes["Background"]
def ease(u): return u * u * (3 - 2 * u)
exec(open("/home/claude/zara/town/glow_sets.py").read())
S.render.resolution_x, S.render.resolution_y = 432, 768; S.render.film_transparent = False
def cam2(loc, at, lens=30):
    CAM.location = loc; CAM.data.lens = lens; CAM.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
O = "/home/claude/zara/town/glow/test"
# main street
show_set("main")
st = mk_steve(); st.place((7.8, 2, 0.2), math.pi / 2 * 0); st.idle(1, 2)
r = mk_rico(TEMP); bell_on(r); flashlight(r); r.place((4.5, -1, 0)); r.set_face("smug", 1)
for i in range(4): t = townie(i); t.place((-3 + i * 2.5, 6 + i, 0)); t.set_face("happy", 1)
m = Moth(TEMP, 1.4, 1); m.place((2, 2, 9), 0.3)
cam2((1, -18, 5), (2, 6, 4.5), 30); S.frame_set(1); S.render.filepath = f"{O}/main.png"; bpy.ops.render.render(write_still=True)
# square
show_set("square")
for k in range(44):
    if k == 22: continue
    p, rz = tree_spot(k); t = townie(k + 10, scale=0.75); t.place(Q + p, rz); t.pose(1, arms=(0,0), arms_side=(1.2, 1.2))
cam2(Q + Vector((0, -62, 12)), Q + Vector((0, 0, 18)), 32); S.render.filepath = f"{O}/square.png"; bpy.ops.render.render(write_still=True)
# edge
show_set("edge"); r.place(G + Vector((2, 2, 0)), 0.4); flash_on(r, 1, True); S.frame_set(1)
cam2(G + Vector((0, -18, 4)), G + Vector((4, 4, 3)), 28); S.render.filepath = f"{O}/edge.png"; bpy.ops.render.render(write_still=True)
print("TESTDONE")
