"""Procedural sound-effect kit (always available, no downloads, no licences).

  python sfx_kit.py -o PROJECT/audio/sfx            # writes the whole kit as 48 kHz WAVs
  python sfx_kit.py -o PROJECT/audio/sfx --only pop,whoosh

Kit: whoosh (big transition), whoosh_short (camera punch), swish (prop slide), pop (icon/prop appear),
pop_high, thud (body falls, door), impact (dramatic hit), boom (explosion), riser (build-up, 1.6 s),
glitch (digital), ding (realisation), shutter (photo), tick (clock), heartbeat, splash (water), crowd_murmur,
fire_crackle, cash (money), siren_short, swell (sad / B&W moment).
For realistic one-offs use eleven.py sfx "<description>" or a licensed library; keep sound designs short.
"""
import argparse
import os
import subprocess

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=0.2, shape=3.0):
    x = np.ones(n)
    na = max(1, int(SR * a))
    x[:na] = np.linspace(0, 1, na)
    tail = np.linspace(1, 0, n - na) ** shape
    x[na:] = tail
    return x


def lp(x, cutoff):
    """one-pole low-pass, cutoff may be an array (Hz)"""
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def hp(x, cutoff):
    return x - lp(x, cutoff)


def norm(x, peak=0.89):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def noise(d):
    return rng.standard_normal(int(SR * d))


def whoosh(d=0.9, lo=300, hi=4200):
    n = noise(d)
    tt = t(d)
    sweep = lo + (hi - lo) * np.sin(np.pi * tt / d) ** 2
    x = lp(n, sweep) - lp(n, sweep * 0.25)
    e = np.sin(np.pi * tt / d) ** 1.6
    return norm(x * e, 0.8)


def pop(f0=900, f1=320, d=0.12):
    tt = t(d)
    f = f1 + (f0 - f1) * np.exp(-tt * 40)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env(len(tt), 0.002, d, 2.5)
    click = noise(0.004) * 0.4
    x[:len(click)] += click
    return norm(x, 0.8)


def thud(d=0.35):
    tt = t(d)
    f = 45 + 90 * np.exp(-tt * 25)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, d, 3)
    x += lp(noise(d), 600) * env(len(tt), 0.001, 0.08, 4) * 0.5
    return norm(x, 0.9)


def impact(d=1.4):
    tt = t(d)
    f = 38 + 120 * np.exp(-tt * 14)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, d, 2.2)
    crack = hp(noise(d), 1500) * env(len(tt), 0.001, 0.25, 5) * 0.6
    body = lp(noise(d), 900) * env(len(tt), 0.002, 0.6, 3) * 0.5
    return norm(sub + crack + body, 0.95)


def boom(d=2.2):
    tt = t(d)
    rumble = lp(noise(d), 220 + 600 * np.exp(-tt * 3)) * env(len(tt), 0.004, d, 1.6) * 2.2
    sub = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-tt * 8)) / SR) * env(len(tt), 0.003, d, 2)
    crack = hp(noise(d), 2500) * env(len(tt), 0.001, 0.12, 4) * 0.5
    return norm(rumble + sub + crack, 0.95)


def riser(d=1.6):
    tt = t(d)
    f = 200 * (2 ** (tt / d * 3))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    nz = lp(noise(d), 300 + 6000 * (tt / d) ** 2) * 0.9
    e = (tt / d) ** 2.2
    e[-int(SR * 0.03):] *= np.linspace(1, 0, int(SR * 0.03))
    return norm((tone + nz) * e, 0.85)


def glitch(d=0.4):
    x = np.zeros(int(SR * d))
    pos = 0
    while pos < len(x):
        seg = int(SR * rng.uniform(0.01, 0.05))
        kind = rng.integers(0, 3)
        tt = np.arange(seg) / SR
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2000) * tt))
        elif kind == 1:
            s = np.round(noise(seg / SR) * 3) / 3
        else:
            s = np.zeros(seg)
        x[pos:pos + seg] = s[:len(x) - pos] * rng.uniform(0.3, 1)
        pos += seg
    return norm(lp(x, 7000), 0.6)


def ding(f=1320, d=1.6):
    tt = t(d)
    x = sum(np.sin(2 * np.pi * f * k * tt) / (k * k) for k in (1, 2.76, 5.4)) * np.exp(-tt * 3)
    return norm(x, 0.7)


def shutter():
    a = hp(noise(0.03), 2000) * env(int(SR * 0.03), 0.001, 0.03, 3)
    b = hp(noise(0.05), 1200) * env(int(SR * 0.05), 0.001, 0.05, 3)
    x = np.concatenate([a, np.zeros(int(SR * 0.06)), b])
    return norm(x, 0.7)


def tick():
    x = hp(noise(0.02), 3000) * env(int(SR * 0.02), 0.0005, 0.02, 6)
    return norm(np.concatenate([x, np.zeros(int(SR * 0.08))]), 0.6)


def heartbeat():
    one = thud(0.18) * 0.9
    gap = np.zeros(int(SR * 0.12))
    x = np.concatenate([one, gap, one * 0.7, np.zeros(int(SR * 0.5))])
    return norm(lp(x, 400), 0.9)


def splash(d=1.2):
    tt = t(d)
    x = lp(noise(d), 2500 + 3000 * np.exp(-tt * 6)) * env(len(tt), 0.003, d, 2.5)
    bub = sum(np.sin(2 * np.pi * rng.uniform(400, 1200) * tt) * np.exp(-((tt - rng.uniform(0.1, 0.9)) ** 2) / 0.0004) for _ in range(12)) * 0.2
    return norm(x + bub, 0.8)


def crowd(d=3.0):
    x = np.zeros(int(SR * d))
    tt = t(d)
    for _ in range(18):
        f0 = rng.uniform(110, 260)
        vib = np.sin(2 * np.pi * rng.uniform(3, 6) * tt) * 8
        amp = np.clip(np.sin(2 * np.pi * rng.uniform(0.3, 1.2) * tt + rng.uniform(0, 6)), 0, 1)
        x += np.sign(np.sin(2 * np.pi * np.cumsum(f0 + vib) / SR)) * amp
    x = lp(x, 900) + lp(noise(d), 1200) * 0.6
    fade = np.minimum(1, np.minimum(tt / 0.3, (d - tt) / 0.5))
    return norm(x * fade, 0.6)


def crackle(d=3.0):
    x = lp(noise(d), 300) * 0.3
    for _ in range(int(d * 40)):
        p = int(rng.uniform(0, len(x) - 400))
        x[p:p + 300] += hp(noise(300 / SR), 2000) * env(300, 0.0002, 300 / SR, 5) * rng.uniform(0.3, 1)
    return norm(x, 0.7)


def cash():
    a = ding(2100, 0.9) * 0.6
    b = hp(noise(0.25), 3000) * env(int(SR * 0.25), 0.001, 0.25, 3) * 0.5
    x = np.zeros(int(SR * 1.0))
    x[:len(b)] += b
    x[int(SR * 0.1):int(SR * 0.1) + len(a)] += a[:len(x) - int(SR * 0.1)]
    return norm(x, 0.75)


def siren(d=1.6):
    tt = t(d)
    f = 700 + 300 * np.sin(2 * np.pi * 1.2 * tt)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5
    return norm(lp(x, 2500) * np.minimum(1, np.minimum(tt / 0.1, (d - tt) / 0.3)), 0.6)


def swell(d=2.4):
    tt = t(d)
    x = sum(np.sin(2 * np.pi * f * tt) for f in (146.8, 174.6, 220.0, 293.7)) / 4
    e = np.sin(np.pi * tt / d) ** 2
    return norm(lp(x, 1200) * e, 0.6)


KIT = {
    "whoosh": lambda: whoosh(0.9),
    "whoosh_short": lambda: whoosh(0.35, 600, 5000),
    "swish": lambda: whoosh(0.22, 1500, 7000),
    "pop": lambda: pop(),
    "pop_high": lambda: pop(1600, 700, 0.09),
    "thud": thud,
    "impact": impact,
    "boom": boom,
    "riser": riser,
    "glitch": glitch,
    "ding": ding,
    "shutter": shutter,
    "tick": tick,
    "heartbeat": heartbeat,
    "splash": splash,
    "crowd_murmur": crowd,
    "fire_crackle": crackle,
    "cash": cash,
    "siren_short": siren,
    "swell": swell,
}


def write_wav(path, x):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                          "-c:a", "pcm_s16le", path], stdin=subprocess.PIPE)
    p.communicate(x.astype(np.float32).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="audio/sfx")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = [n for n in a.only.split(",") if n] or list(KIT)
    for n in names:
        write_wav(os.path.join(a.out, n + ".wav"), KIT[n]())
        print("wrote", os.path.join(a.out, n + ".wav"))


if __name__ == "__main__":
    main()
