import json, os, subprocess, re, math, random
import numpy as np, soundfile as sf

EP = "/home/claude/ep1"
W, H, FPS = 720, 1280, 30
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
meta = {m["shot"]: m for m in json.load(open(f"{EP}/vo/meta.json"))}
order = [f"s{i:02d}" for i in range(1, 32)]

GAP = 0.3
EXTRA = dict(s01=0.4, s06=1.6, s07=0.4, s11=0.6, s16=0.6, s18=0.8, s19=1.0, s21=0.6, s22=1.0, s28=0.8, s31=2.6)
LEAD = 0.12  # vo starts this long into the shot
# motion: (zoom_start, zoom_end, pan_x, pan_y)  pan in fraction of slack
MOTION = dict(
    s01=(1.0, 1.15, 0, -0.3), s02=(1.0, 1.12, 0, 0), s03=(1.05, 1.15, 0.2, 0), s04=(1.12, 1.0, -0.2, 0),
    s05=(1.0, 1.1, 0, 0.3), s06=("punch",), s07=(1.12, 1.0, 0, 0), s08=(1.0, 1.1, 0.2, 0), s09=(1.05, 1.2, 0, 0),
    s10=(1.0, 1.08, 0, 0), s12=(1.0, 1.1, 0, -0.2), s13=("punch",), s14=(1.0, 1.15, 0, 0), s15=(1.0, 1.15, 0, 0),
    s16=(1.0, 1.18, 0, 0), s17=(1.0, 1.25, 0, -0.2), s18=(1.0, 1.15, 0, 0.3), s19=(1.0, 1.2, 0, -0.2),
    s20=(1.0, 1.12, 0, 0), s21=(1.0, 1.15, 0, 0), s22=(1.05, 1.3, 0, 0), s23=("punch",), s24=(1.0, 1.2, 0, 0),
    s25=(1.0, 1.12, -0.2, 0), s26=(1.0, 1.1, 0, 0), s27=(1.08, 1.0, 0.3, 0), s28=(1.0, 1.15, 0, -0.3),
    s29=(1.0, 1.15, 0, 0), s30=(1.0, 1.12, -0.3, 0), s31=("punch",),
)

def word_times(text, dur):
    words = text.replace("...", "… ").split()
    weights = [len(re.sub(r"[^\w']", "", w)) + 2 + (4 if re.search(r"[.,…?!]$", w) else 0) for w in words]
    tot = sum(weights); t = 0; out = []
    for w, wt in zip(words, weights):
        d = dur * wt / tot; out.append((w.strip(".,…").upper() if False else re.sub(r"[.,…]+$", "", w), t, t + d)); t += d
    return out

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")

timeline = []; t0 = 0.0
for s in order:
    vo = meta[s]["dur"]
    d = max(1.6, LEAD + vo + GAP + EXTRA.get(s, 0))
    timeline.append(dict(shot=s, start=t0, dur=d, vo=vo, text=meta[s]["text"])); t0 += d
TOTAL = t0
print("TOTAL", round(TOTAL, 2))

os.makedirs(f"{EP}/clips", exist_ok=True)
def render_clip(c):
    s, d = c["shot"], c["dur"]; n = int(round(d * FPS))
    still = f"{EP}/stills/{s}.png"
    m = MOTION.get(s, (1.0, 1.1, 0, 0))
    base = f"scale={int(W*1.0)}:{int(H*1.0)}"
    if s == "s11" or not os.path.exists(still):
        src = ["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={d:.3f}"]
        vf = "null"
    else:
        src = ["-framerate", str(FPS), "-loop", "1", "-t", f"{d:.3f}", "-i", still]
        if m[0] == "punch":
            # fast punch-in over 0.25s then slow creep
            z = f"if(lt(on,8),1+0.18*on/8,1.18+0.06*(on-8)/{max(n-8,1)})"
            vf = f"scale=1800:3200,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}"
        else:
            z0, z1, px, py = m
            z = f"{z0}+({z1}-{z0})*on/{n}"
            x = f"iw/2-(iw/zoom/2)+{px}*(iw-iw/zoom)/2*on/{n}"
            y = f"ih/2-(ih/zoom/2)+{py}*(ih-ih/zoom)/2*on/{n}"
            vf = f"scale=1800:3200,zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"
    # shake for impact shots
    if s in ("s06", "s26"):
        vf += ",crop=iw-24:ih-24:12+8*sin(n*1.7):12+8*cos(n*2.3),scale=%d:%d" % (W, H)
    # drum flashes for s06 (3 booms)
    if s == "s06":
        for k in range(3):
            a = LEAD + 0.15 + k * 0.75
            vf += f",eq=brightness=0.25:enable='between(t,{a:.2f},{a+0.08:.2f})'"
    # captions
    for w, a, b in word_times(c["text"], c["vo"]):
        a += LEAD; b += LEAD
        vf += (f",drawtext=fontfile={FONT}:text='{esc(w)}':fontsize=82:fontcolor=0xFFE81A:borderw=7:bordercolor=black"
               f":x=(w-text_w)/2:y=h*0.64-text_h/2:enable='between(t,{a:.3f},{b:.3f})'")
    if s == "s01":
        vf += (f",drawtext=fontfile={FONT}:text='NIGHT RULES':fontsize=58:fontcolor=white:borderw=5:bordercolor=black"
               f":x=(w-text_w)/2:y=110:enable='lt(t,2.8)'"
               f",drawtext=fontfile={FONT}:text='EPISODE 1':fontsize=34:fontcolor=0xFFE81A:borderw=4:bordercolor=black"
               f":x=(w-text_w)/2:y=185:enable='lt(t,2.8)'")
    if s == "s31":
        a = LEAD + c["vo"] + 0.3
        vf += (f",eq=saturation=0.6:contrast=1.15:enable='gte(t,{a:.2f})'"
               f",drawbox=x=0:y=ih*0.42:w=iw:h=210:color=black@0.75:t=fill:enable='gte(t,{a:.2f})'"
               f",drawtext=fontfile={FONT}:text='PART 2 >>':fontsize=110:fontcolor=0xFFE81A:borderw=8:bordercolor=black"
               f":x=(w-text_w)/2:y=h*0.42+22:enable='gte(t,{a:.2f})'"
               f",drawtext=fontfile={FONT}:text='follow so you don’t miss it':fontsize=34:fontcolor=white"
               f":x=(w-text_w)/2:y=h*0.42+150:enable='gte(t,{a+0.4:.2f})'")
    vf += ",format=yuv420p"
    tmp = f"{EP}/clips/{s}.tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *src, "-vf", vf, "-frames:v", str(n), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-an", tmp]
    subprocess.run(cmd, check=True); os.replace(tmp, f"{EP}/clips/{s}.mp4")

import sys
only = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else None
for c in timeline:
    if only and c["shot"] not in only: continue
    render_clip(c); print("clip", c["shot"], round(c["dur"], 2), flush=True)
if only: sys.exit()

with open(f"{EP}/clips/list.txt", "w") as f:
    for c in timeline: f.write(f"file '{EP}/clips/{c['shot']}.mp4'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{EP}/clips/list.txt", "-c", "copy", f"{EP}/video_noaudio.mp4"], check=True)

# ---------------- soundtrack ----------------
SR = 48000; N = int((TOTAL + 0.5) * SR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
music = np.zeros(N); sfx = np.zeros(N); vo = np.zeros(N)
st = {c["shot"]: c["start"] for c in timeline}
def at(s, off=0.0): return int((st[s] + off) * SR)
def add(buf, sig, i, g=1.0):
    i = max(0, i); e = min(len(buf), i + len(sig)); buf[i:e] += g * sig[: e - i]
def env(n, a, r):
    e = np.ones(n); na = int(a * SR); nr = int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[n - nr:] = np.linspace(1, 0, nr) if nr else 1; return e

# VO
for c in timeline:
    a, sr = sf.read(f"{EP}/vo/{c['shot']}.wav"); add(vo, a, at(c["shot"], LEAD))

# night pad: A minor drone, whole video except the day section
def pad(n, freqs, amp):
    tt = np.arange(n) / SR; sig = np.zeros(n)
    for f in freqs:
        for det in (-0.6, 0.6):
            sig += np.sin(2 * np.pi * (f + det) * tt + rng.uniform(0, 6))
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * tt)
    return amp * sig / (len(freqs) * 2) * lfo
night_a = at("s05"); end = N
p = pad(end - night_a, [55, 110, 130.81, 164.81, 220], 0.35) * env(end - night_a, 2.5, 1.5)
add(music, p, night_a)
p = pad(night_a, [110, 164.81, 220], 0.22) * env(night_a, 0.5, 1.5)  # softer intro bed
add(music, p, 0)

# day kalimba plucks (s03-s04)
notes = [440, 523.25, 587.33, 659.25, 783.99, 880]
def pluck(f, dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 7)
beat = 60 / 112 / 2; tpos = st["s03"]
while tpos < st["s05"] - 0.2:
    add(music, pluck(rng.choice(notes)), int(tpos * SR), 0.22); tpos += beat * rng.choice([1, 1, 2])
# hand-drum loop in day section
def drum(f0=120, f1=45, dur=0.8, click=0.3):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 18); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt * 5.5)
    s[: int(0.01 * SR)] += click * rng.standard_normal(int(0.01 * SR))
    return s
tpos = st["s03"]
while tpos < st["s05"] - 0.2:
    add(music, drum(220, 110, 0.25, 0.2), int(tpos * SR), 0.25); tpos += beat * 2

# three big booms at s06, fourth at s13, echo at s14
for k in range(3): add(sfx, drum(), at("s06", LEAD + 0.15 + k * 0.75), 0.9)
add(sfx, drum(), at("s13", LEAD + 1.0), 0.9)
add(sfx, drum(100, 40, 1.2), at("s14", 0.2), 0.5)
# doors slam (s07): noise bursts
for k in range(4):
    n = int(0.12 * SR); add(sfx, rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 40), at("s07", 0.1 + k * 0.22), 0.35)

def whoosh(dur=1.2, up=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    # crude band shaping via moving average
    k = 40; x = np.convolve(x, np.ones(k) / k, mode="same") * 4
    e = np.linspace(0, 1, n) ** 2 if up else np.linspace(1, 0, n) ** 2
    return x * e
for s_ in ("s16", "s18", "s21", "s28"):
    add(sfx, whoosh(1.0), at(s_, -0.9), 0.35); add(sfx, drum(80, 35, 1.5, 0.1), at(s_, 0.05), 0.7)
# heartbeat s18 -> s24
tpos = st["s18"]
while tpos < st["s25"]:
    add(sfx, drum(70, 40, 0.3, 0.05), int(tpos * SR), 0.45); add(sfx, drum(70, 40, 0.3, 0.05), int((tpos + 0.22) * SR), 0.3); tpos += 0.85
# riser into s25 and big hit on "who are you"
n = int(1.4 * SR); tt = np.arange(n) / SR
add(sfx, np.sin(2 * np.pi * (200 + 600 * tt / 1.4) * tt) * (tt / 1.4) ** 2 * 0.25, at("s26", -1.4))
add(sfx, drum(90, 35, 2.0, 0.4), at("s26", 0.0), 1.0)
# silence trick on s27: duck music
i0, i1 = at("s27"), at("s28"); music[i0:i1] *= 0.25
# ending stinger: dissonant cluster + boom on s31 card
n = int(3.0 * SR); tt = np.arange(n) / SR
clu = sum(np.sin(2 * np.pi * f * tt) for f in (440, 466.16, 622.25, 659.25)) / 4 * np.exp(-tt * 0.8)
c31 = [c for c in timeline if c["shot"] == "s31"][0]
add(sfx, clu, at("s31", LEAD + c31["vo"] + 0.3), 0.35); add(sfx, drum(90, 30, 2.5, 0.5), at("s31", LEAD + c31["vo"] + 0.3), 1.0)

# duck music under VO
voenv = np.convolve(np.abs(vo), np.ones(4800) / 4800, mode="same"); duck = 1 - 0.55 * np.clip(voenv * 8, 0, 1)
MUS = 0.0 if os.environ.get("NOMUSIC") else 0.55
mix = vo * 1.0 + music * MUS * duck + sfx * 0.6
mix = np.tanh(mix * 1.1) / 1.1
sf.write(f"{EP}/soundtrack.wav", np.stack([mix, mix], 1).astype(np.float32), SR)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{EP}/video_noaudio.mp4", "-i", f"{EP}/soundtrack.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-14:TP=-1.0", "-shortest", f"{EP}/NIGHT_RULES_EP1" + ("_NO_MUSIC" if os.environ.get("NOMUSIC") else "") + ".mp4"], check=True)
print("DONE")
