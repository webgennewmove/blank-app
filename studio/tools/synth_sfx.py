import sys
import wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def lowpass(x, cutoff):
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def env(d, attack, decay):
    tt = t(d)
    return np.minimum(1, tt / max(attack, 1e-4)) * np.exp(-tt / decay)


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-9) * peak


def whoosh():
    d = 0.55
    tt = t(d)
    n = rng.standard_normal(len(tt))
    sweep = 300 + 5000 * np.sin(np.pi * tt / d) ** 2
    shape = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 2
    return norm(highpass(lowpass(n, sweep), 150) * shape)


def glitch():
    d = 0.5
    out = np.zeros(int(SR * d))
    pos = 0
    while pos < len(out):
        seg = int(SR * rng.uniform(0.015, 0.05))
        kind = rng.integers(3)
        tt = t(seg / SR)
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * rng.uniform(80, 900) * tt))
        elif kind == 1:
            s = rng.standard_normal(seg)
        else:
            s = np.round(np.sin(2 * np.pi * rng.uniform(200, 2000) * tt) * 3) / 3
        out[pos:pos + seg] = s[: len(out) - pos] * rng.uniform(0.3, 1)
        pos += seg + int(SR * rng.uniform(0, 0.02))
    return norm(out * np.linspace(1, 0.3, len(out)), 0.7)


def click(freq=3000, d=0.03, decay=0.004):
    tt = t(d)
    return (np.sin(2 * np.pi * freq * tt) * 0.6 + rng.standard_normal(len(tt)) * 0.4) * np.exp(-tt / decay)


def place(buf, snd, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(snd))
    if i < len(buf):
        buf[i:j] += snd[: j - i] * gain


def chips():
    out = np.zeros(int(SR * 1.2))
    tm = 0.0
    while tm < 0.9:
        place(out, click(rng.uniform(2500, 5200), 0.05, rng.uniform(0.004, 0.012)), tm, rng.uniform(0.4, 1))
        tm += rng.uniform(0.02, 0.09)
    return norm(highpass(out, 600), 0.8)


def reels():
    out = np.zeros(int(SR * 1.8))
    tm = 0.0
    while tm < 1.75:
        place(out, click(2200, 0.02, 0.003), tm, 0.6)
        tm += 0.045
    return norm(out, 0.6)


def clunk():
    d = 0.25
    tt = t(d)
    tone = np.sin(2 * np.pi * (140 * np.exp(-tt * 12) + 60) * tt) * np.exp(-tt / 0.06)
    return norm(tone + click(1500, d, 0.01) * 0.6, 0.9)


def bell(freq, d=1.2):
    tt = t(d)
    mod = np.sin(2 * np.pi * freq * 3.5 * tt) * 2.2 * np.exp(-tt / 0.3)
    return np.sin(2 * np.pi * freq * tt + mod) * np.exp(-tt / 0.45)


def jackpot():
    out = np.zeros(int(SR * 3.2))
    notes = [523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5, 1318.5, 1567.98]
    for k in range(3):
        for i, f in enumerate(notes):
            place(out, bell(f), k * 0.75 + i * 0.08, 0.5)
    tm = 0.2
    while tm < 3.0:
        place(out, click(rng.uniform(4000, 7000), 0.08, rng.uniform(0.01, 0.03)), tm, rng.uniform(0.2, 0.5))
        tm += rng.uniform(0.02, 0.06)
    tt = t(3.2)
    ring = np.sign(np.sin(2 * np.pi * 22 * tt)) * np.sin(2 * np.pi * 2400 * tt) * 0.12 * np.exp(-tt / 2)
    return norm(out + ring, 0.85)


def scratch():
    d = 0.7
    tt = t(d)
    rate = np.where(tt < 0.25, 1 - tt / 0.25 * 1.8, -0.8 + (tt - 0.25) * 0.3)
    phase = np.cumsum(300 * rate) / SR
    saw = 2 * (phase * 3 % 1) - 1
    n = rng.standard_normal(len(tt)) * 0.4
    sig = lowpass(saw + n, 1500 + 2500 * np.abs(rate))
    return norm(sig * np.exp(-tt / 0.4), 0.8)


def heartbeat():
    d = 0.45
    out = np.zeros(int(SR * d))
    for at, g in [(0, 1.0), (0.16, 0.7)]:
        tt = t(0.18)
        thump = np.sin(2 * np.pi * (70 * np.exp(-tt * 8) + 40) * tt) * np.exp(-tt / 0.05)
        place(out, thump, at, g)
    return norm(out, 0.95)


def tick():
    return norm(highpass(click(3500, 0.05, 0.006), 800), 0.7)


def snap():
    d = 0.5
    tt = t(d)
    crack = rng.standard_normal(len(tt)) * np.exp(-tt / 0.008)
    ring = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.12) for f in (1870, 2930, 4410)) * 0.3
    thud = np.sin(2 * np.pi * (180 * np.exp(-tt * 20) + 70) * tt) * np.exp(-tt / 0.07)
    return norm(crack + ring + thud, 0.95)


def write(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    out = sys.argv[1]
    for name, fn in [('whoosh', whoosh), ('glitch', glitch), ('chips', chips), ('reels', reels), ('clunk', clunk),
                     ('jackpot', jackpot), ('scratch', scratch), ('heartbeat', heartbeat), ('tick', tick), ('snap', snap)]:
        write(f'{out}/{name}.wav', fn())
        print(name)
