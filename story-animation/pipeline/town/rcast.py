"""IN MY TOWN (cinematic) cast in the approved Roblox look: R6 Char rig + painted faces (lib.py / faces.py),
dressed after the character sheet. Needs lib's helpers in scope (exec world.py first)."""
import math, random
from mathutils import Vector

def combo(*fs):
    def f(c):
        for g in fs: g(c)
    return f
def long_sleeves(col, skin):
    def f(c):
        cuff = mat(f"cuff{col}", tuple(v * 0.62 for v in col)); sh = mat(f"shirt_{col}", col, 0.6); sk = mat(f"skin_{skin}", skin, 0.5)
        for p in c.arms:
            for ch in list(p.children): bpy.data.objects.remove(ch, do_unlink=True)
            box("sleeve", (0, 0, -0.78), (0.98, 0.98, 1.72), sh, parent=p, bevel=0.2, coll=c.coll)
            box("cuff", (0, 0, -1.56), (1.01, 1.01, 0.2), cuff, parent=p, bevel=0.05, coll=c.coll)
            box("hand", (0, 0, -1.84), (0.88, 0.88, 0.44), sk, parent=p, bevel=0.16, coll=c.coll)
    return f
def hoodie(col, strings=True):
    def f(c):
        m = mat(f"hood{col}", col); pk = mat(f"hoodpk{col}", tuple(v * 0.8 for v in col))
        box("hoodback", (0, 0.55, 1.95), (1.5, 0.45, 0.8), m, parent=c.hips, coll=c.coll, bevel=0.15)
        box("pocket", (0, -0.52, 0.5), (1.25, 0.08, 0.55), pk, parent=c.hips, coll=c.coll, bevel=0.03)
        if strings:
            for sx in (-0.25, 0.25): box("string", (sx, -0.54, 1.55), (0.07, 0.04, 0.6), mat("white", (1, 1, 1)), parent=c.hips, coll=c.coll)
    return f
def jacket(col, inner):
    """open jacket over a hoodie: two front panels + collar, inner colour shows down the middle"""
    def f(c):
        m = mat(f"jkt{col}", col, 0.55); im = mat(f"jin{inner}", inner, 0.7)
        box("jinner", (0, -0.51, 1.0), (0.7, 0.06, 1.9), im, parent=c.hips, coll=c.coll)
        for sx in (-1, 1): box("jpanel", (sx * 0.66, -0.53, 1.0), (0.66, 0.08, 2.0), m, parent=c.hips, coll=c.coll, bevel=0.03)
        box("jcollar", (0, 0.05, 2.02), (2.05, 1.08, 0.22), m, parent=c.hips, coll=c.coll, bevel=0.08)
        box("hoodup", (0, 0.58, 1.95), (1.4, 0.4, 0.75), im, parent=c.hips, coll=c.coll, bevel=0.15)
    return f
def puffer(col, hood_col):
    def f(c):
        m = mat(f"puff{col}", col, 0.3)
        for k in range(4): box("pband", (0, 0, 0.3 + k * 0.48), (2.18, 1.18, 0.46), m, parent=c.hips, coll=c.coll, bevel=0.2)
        box("pcollar", (0, 0.06, 2.04), (1.6, 1.12, 0.3), m, parent=c.hips, coll=c.coll, bevel=0.12)
        box("zip", (0, -0.6, 1.0), (0.06, 0.04, 2.0), mat("zip", (0.5, 0.5, 0.52), 0.3), parent=c.hips, coll=c.coll)
        hm = mat(f"hood{hood_col}", hood_col)
        box("hoodup", (0, 0.6, 1.98), (1.4, 0.42, 0.75), hm, parent=c.hips, coll=c.coll, bevel=0.15)
        for p in c.arms:
            for ch in list(p.children):
                if ch.name.startswith("sleeve"): ch.data = ch.data.copy(); ch.data.materials.clear(); ch.data.materials.append(m)
    return f
def cargo(col):
    def f(c):
        m = mat(f"cargo{col}", tuple(v * 0.8 for v in col))
        for l in c.legs: box("cpocket", (0.5 * (1 if l.location.x > 0 else -1), 0, -0.95), (0.12, 0.6, 0.55), m, parent=l, coll=c.coll, bevel=0.04)
    return f
def curly_top(col, seed=1, n=34, r=0.2, height=0.75):
    def f(c):
        m = mat(f"curl{col}", col, 0.8); rnd = random.Random(seed); h = c.head
        box("hcap", (0, 0.05, 0.56), (1.3, 1.28, 0.24), m, parent=h, bevel=0.08, coll=c.coll)
        for sx in (-0.62, 0.62): box("fadeside", (sx, 0.12, 0.28), (0.06, 1.0, 0.48), mat(f"fade{col}", tuple(v * 0.8 for v in col)), parent=h, coll=c.coll)
        box("fadeback", (0, 0.62, 0.25), (1.26, 0.06, 0.6), m, parent=h, coll=c.coll)
        for k in range(n):
            x, y = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.48, 0.45)
            sphere("curl", (x, y, height + rnd.uniform(-0.05, 0.12)), 1, m, coll=c.coll, parent=h, scale=(r, r, r * 0.9), seg=10)
    return f
def long_curls(col, seed=4):
    def f(c):
        m = mat(f"lcurl{col}", col, 0.7); rnd = random.Random(seed); h = c.head
        box("hair", (0, 0.06, 0.58), (1.34, 1.32, 0.3), m, parent=h, coll=c.coll, bevel=0.1)
        box("fringe", (0, -0.6, 0.5), (1.3, 0.14, 0.24), m, parent=h, coll=c.coll, bevel=0.06)
        box("hairback", (0, 0.66, -0.5), (1.45, 0.32, 2.0), m, parent=h, coll=c.coll, bevel=0.14)
        for sx in (-1, 1): box("hairside", (sx * 0.78, 0.15, -0.75), (0.34, 0.85, 2.3), m, parent=h, coll=c.coll, bevel=0.14)
        for k in range(70):
            side = rnd.choice((-1, 1)); x = side * rnd.uniform(0.7, 0.98) if k % 3 else rnd.uniform(-0.7, 0.7)
            y = rnd.uniform(-0.25, 0.6) if k % 3 else rnd.uniform(0.6, 0.85)
            sphere("lcurl", (x, y, rnd.uniform(-1.85, 0.6)), 1, m, coll=c.coll, parent=h, scale=(0.19, 0.19, 0.22), seg=10)
        sphere("pony", (0, 0.45, 0.9), 1, m, coll=c.coll, parent=h, scale=(0.26, 0.24, 0.22))
        cyl("scrunchie", (0, 0.45, 0.74), 0.2, 0.1, mat("scrunch", (0.95, 0.25, 0.6)), parent=h, coll=c.coll, verts=12)
        gold = mat("gold", (1, 0.75, 0.08), 0.25)
        for sx in (-1, 1):
            for k in range(10):
                a = k / 10 * 6.283
                sphere("hoop", (sx * 0.66, 0.0 + math.cos(a) * 0.16, -0.42 + math.sin(a) * 0.16), 1, gold, coll=c.coll, parent=h, scale=(0.035, 0.035, 0.035), seg=6)
    return f
def swoop(col, seed=2):
    def f(c):
        m = mat(f"swoop{col}", col, 0.75); dk = mat(f"swoopd{col}", tuple(v * 0.75 for v in col), 0.75); rnd = random.Random(seed); h = c.head
        box("hcap", (0, 0.08, 0.58), (1.32, 1.26, 0.28), m, parent=h, bevel=0.1, coll=c.coll)
        box("hback", (0, 0.6, 0.22), (1.3, 0.16, 0.8), m, parent=h, bevel=0.05, coll=c.coll)
        for sx in (-0.63, 0.63): box("side", (sx, 0.15, 0.3), (0.08, 0.9, 0.5), m, parent=h, coll=c.coll)
        for k in range(7):
            x = -0.5 + k * 0.17
            box("tuft", (x, -0.32 + rnd.uniform(-0.05, 0.08), 0.82 + 0.06 * (k % 2)), (0.3, 0.6, 0.36), m if k % 2 else dk,
                rot=(0.5, rnd.uniform(-0.25, 0.25), 0.1 * (k - 3)), parent=h, bevel=0.12, coll=c.coll)
    return f
def back_cap(col):
    def f(c):
        m = mat(f"bcap{col}", col, 0.5); h = c.head
        box("capcrown", (0, 0.03, 0.7), (1.38, 1.38, 0.42), m, parent=h, coll=c.coll, bevel=0.16)
        box("capbrim", (0, 0.88, 0.6), (1.2, 0.72, 0.1), m, parent=h, coll=c.coll, bevel=0.04)
        box("capgap", (0, 0.7, 0.62), (0.4, 0.04, 0.22), mat("capstrap", (0.35, 0.35, 0.38)), parent=h, coll=c.coll)
        box("hairfr", (0, -0.6, 0.48), (1.2, 0.1, 0.16), mat("ricohair", (0.04, 0.03, 0.02)), parent=h, coll=c.coll)
    return f
def specs(c):
    fm = mat("specs", (0.05, 0.05, 0.06), 0.3)
    for sx in (-0.24, 0.24):
        for dz, w, hh in ((0.24, 0.42, 0.05), (-0.02, 0.42, 0.05)): box("spec", (sx, -0.66, dz), (w, 0.05, hh), fm, parent=c.head, coll=c.coll)
        for dx in (-0.2, 0.2): box("specv", (sx + dx, -0.66, 0.11), (0.05, 0.05, 0.3), fm, parent=c.head, coll=c.coll)
    box("bridge", (0, -0.66, 0.16), (0.1, 0.05, 0.04), fm, parent=c.head, coll=c.coll)
    for sx in (-0.63, 0.63): box("specarm", (sx, -0.3, 0.15), (0.04, 0.7, 0.04), fm, parent=c.head, coll=c.coll)
def crop_top(skin):
    def f(c):
        box("midriff", (0, 0, 0.45), (1.98, 0.98, 0.4), mat(f"skin_{skin}", skin, 0.5), parent=c.hips, coll=c.coll, bevel=0.15)
    return f
def kicks(col, sole=(0.97, 0.97, 0.97), swoosh=None):
    def f(c):
        so = mat(f"sole{sole}", sole, 0.5); up = mat(f"kick{col}", col, 0.45)
        for l in c.legs:
            for ch in list(l.children):
                if ch.name.startswith("shoe"): bpy.data.objects.remove(ch, do_unlink=True)
            box("kick", (0, -0.1, -1.82), (1.04, 1.25, 0.38), up, parent=l, bevel=0.14, coll=c.coll)
            box("ksole", (0, -0.1, -1.98), (1.08, 1.3, 0.12), so, parent=l, bevel=0.05, coll=c.coll)
            if swoosh:
                sx = 0.53 * (1 if l.location.x > 0 else -1)
                box("kswoosh", (sx, -0.15, -1.82), (0.03, 0.7, 0.14), mat(f"sw{swoosh}", swoosh, 0.4), rot=(0.25, 0, 0), parent=l, coll=c.coll)
    return f

SKJ, SKM, SKL, SKT, SKR = (0.33, 0.18, 0.1), (0.62, 0.38, 0.24), (0.92, 0.66, 0.5), (0.22, 0.12, 0.065), (0.8, 0.55, 0.38)
BLK = (0.035, 0.035, 0.045)
def mk_jayden(coll):
    return Char("jayden", coll, SKJ, BLK, (0.05, 0.05, 0.06), hair="none", scale=0.95,
                extra=combo(long_sleeves(BLK, SKJ), puffer(BLK, (0.45, 0.45, 0.48)), cargo((0.07, 0.07, 0.08)), curly_top((0.03, 0.02, 0.015), 3),
                            kicks((0.97, 0.97, 0.97), swoosh=(0.03, 0.03, 0.03))))
def mk_maya(coll):
    pink = (0.85, 0.13, 0.45)
    return Char("maya", coll, SKM, pink, (0.2, 0.32, 0.6), hair="none", scale=0.92,
                extra=combo(long_sleeves(pink, SKM), hoodie(pink), crop_top(SKM), cargo((0.2, 0.32, 0.6)), long_curls((0.2, 0.09, 0.04)),
                            kicks((0.97, 0.97, 0.97), sole=(0.95, 0.3, 0.6), swoosh=(0.9, 0.2, 0.55))))
def mk_leo(coll):
    den = (0.12, 0.2, 0.42); grey = (0.6, 0.6, 0.63)
    return Char("leo", coll, SKL, den, (0.16, 0.16, 0.17), hair="none", scale=0.9,
                extra=combo(long_sleeves(den, SKL), jacket(den, grey), cargo((0.16, 0.16, 0.17)), swoop((0.32, 0.14, 0.05)),
                            kicks((0.04, 0.04, 0.04), swoosh=(0.97, 0.97, 0.97))))
def mk_tyrone(coll):
    grn = (0.05, 0.32, 0.12)
    c = Char("tyrone", coll, SKT, grn, (0.04, 0.04, 0.05), hair="none", scale=1.12,
             extra=combo(long_sleeves(grn, SKT), hoodie(grn), cargo((0.05, 0.05, 0.06)), curly_top((0.025, 0.018, 0.012), 7, n=26, r=0.17, height=0.7), specs,
                         kicks((0.45, 0.72, 0.5), swoosh=(0.06, 0.3, 0.12))))
    c.torso.scale = (1.15, 1.12, 1.0); return c
def mk_rico(coll):
    return Char("rico", coll, SKR, BLK, (0.05, 0.05, 0.06), hair="none", scale=0.93,
                extra=combo(long_sleeves(BLK, SKR), jacket(BLK, (0.09, 0.09, 0.1)), cargo((0.06, 0.06, 0.07)), back_cap(BLK),
                            kicks((0.97, 0.97, 0.97), swoosh=(0.03, 0.03, 0.03))))

class Cat:
    """blocky Roblox-style tabby"""
    def __init__(self, coll, scale=1.0, crown=False):
        fur = mat("tabby", (0.45, 0.3, 0.18), 0.85); wht = mat("catw", (0.95, 0.93, 0.88), 0.85); dk = mat("tabbyd", (0.12, 0.08, 0.05), 0.85)
        self.root = empty("whiskers", coll=coll); self.root.scale = (scale,) * 3; self.coll = coll
        self.body = empty("cbody", (0, 0, 0.85), self.root, coll)
        box("cb", (0, 0.35, 0), (1.0, 1.7, 0.95), fur, parent=self.body, coll=coll, bevel=0.25)
        box("cchest", (0, -0.42, -0.05), (0.8, 0.2, 0.8), wht, parent=self.body, coll=coll, bevel=0.15)
        for k in range(3): box("cstripe", (0, 0.2 + k * 0.4, 0.46), (0.9, 0.14, 0.08), dk, parent=self.body, coll=coll)
        self.legs = []
        for sx in (-0.3, 0.3):
            for sy in (-0.3, 0.95):
                l = empty("cleg", (sx, sy, -0.35), self.body, coll); box("cl", (0, 0, -0.3), (0.3, 0.3, 0.6), fur, parent=l, coll=coll, bevel=0.1)
                box("cpaw", (0, -0.04, -0.6), (0.32, 0.36, 0.14), wht, parent=l, coll=coll, bevel=0.06); self.legs.append(l)
        self.tail = empty("ctail", (0, 1.2, 0.2), self.body, coll)
        for k in range(5): box("tseg", (0, 0.12 + k * 0.05, 0.15 + k * 0.2), (0.18, 0.18, 0.24), dk if k % 2 else fur, rot=(-0.3 + k * 0.1, 0, 0), parent=self.tail, coll=coll, bevel=0.06)
        self.neck = empty("cneck", (0, -0.45, 0.45), self.body, coll)
        self.head = empty("chead", (0, -0.1, 0.35), self.neck, coll); h = self.head
        box("chd", (0, 0, 0), (1.05, 0.9, 0.85), fur, parent=h, coll=coll, bevel=0.25)
        box("cmuz", (0, -0.42, -0.18), (0.5, 0.2, 0.32), wht, parent=h, coll=coll, bevel=0.1)
        box("cnose", (0, -0.53, -0.08), (0.14, 0.05, 0.08), mat("catnose", (0.8, 0.35, 0.4)), parent=h, coll=coll, bevel=0.02)
        for sx in (-1, 1):
            cone("cear", (sx * 0.33, 0.0, 0.52), 0.22, 0.42, fur, verts=4, parent=h, coll=coll, rot=(0, 0, 0.78))
            sphere("ceye", (sx * 0.24, -0.43, 0.08), 1, mat("cateye", (0.85, 0.75, 0.1), 0.15), coll=coll, parent=h, scale=(0.15, 0.06, 0.16))
            sphere("cpup", (sx * 0.24, -0.47, 0.08), 1, mat("pupil", (0.01, 0.01, 0.01), 0.2), coll=coll, parent=h, scale=(0.05, 0.04, 0.13))
            sphere("cgl", (sx * 0.24 + 0.05, -0.49, 0.15), 1, mat("white", (1, 1, 1)), coll=coll, parent=h, scale=(0.035, 0.02, 0.035))
            for k in range(2): box("whisk", (sx * 0.45, -0.45, -0.15 + k * 0.08), (0.45, 0.015, 0.015), mat("white", (1, 1, 1)), rot=(0, sx * (0.15 - k * 0.3), 0), parent=h, coll=coll)
        box("collar", (0, -0.05, -0.42), (1.0, 0.85, 0.14), mat("collarb", (0.1, 0.25, 0.75)), parent=h, coll=coll, bevel=0.05)
        sphere("bell", (0, -0.48, -0.55), 1, mat("gold", (1, 0.75, 0.08), 0.25), coll=coll, parent=h, scale=(0.09, 0.09, 0.09))
        self.crown = None
        if crown:
            g = mat("gold", (1, 0.75, 0.08), 0.25); gem = mat("gem", (0.1, 0.9, 0.4), 0.1)
            self.crown = empty("crown", (0, 0.05, 0.5), h, coll)
            box("crband", (0, 0, 0.08), (0.75, 0.7, 0.18), g, parent=self.crown, coll=coll, bevel=0.03)
            for k, (x, y) in enumerate([(-0.3, -0.28), (0, -0.3), (0.3, -0.28), (-0.3, 0.28), (0.3, 0.28)]):
                cone("crspike", (x, y, 0.27), 0.09, 0.22, g, verts=4, parent=self.crown, coll=coll)
                sphere("crgem", (x, y - 0.04 * (1 if y < 0 else -1), 0.1), 1, gem, coll=coll, parent=self.crown, scale=(0.05, 0.03, 0.05))
    def sit(self, f):
        self.body.rotation_euler = (-0.5, 0, 0); self.body.keyframe_insert("rotation_euler", frame=f)
        self.neck.rotation_euler = (0.45, 0, 0); self.neck.keyframe_insert("rotation_euler", frame=f)
        for i, l in enumerate(self.legs):
            l.rotation_euler = (0.5 if i % 2 == 0 else -1.1, 0, 0); l.keyframe_insert("rotation_euler", frame=f)
    def tailwag(self, f0, f1, amp=0.4, speed=1.5):
        for f in range(f0, f1 + 1, 2):
            self.tail.rotation_euler = (0, amp * math.sin(f / 24 * speed * 6.28), 0); self.tail.keyframe_insert("rotation_euler", frame=f)
