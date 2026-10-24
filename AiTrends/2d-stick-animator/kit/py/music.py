"""Procedural background score in the house style (fallback when no licensed track / ElevenLabs music).

  python music.py -o PROJECT/audio/music.wav --dur 56 --mood mystery [--bpm 116] [--seed 3]
  moods: mystery (default: curious minor plucks + pad + soft pulse), tension (faster, more drums),
         playful (major pizzicato), sad (slow pad + soft keys), war (low drums + brass-like pad)

The samples run a steady melodic bed under the whole story (sustained melody notes around 600-1600 Hz,
plucked arpeggios, soft pulse) mixed 15-20 dB under the voice, no silence, ending with the story.
Better options when available: the user's own licensed track, or `eleven.py music "<prompt>" --dur N`.
"""
import argparse
import subprocess

import numpy as np

SR = 48000
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def chord(name, octave=4):
    """'Dm' -> midi notes (root, third, fifth)"""
    minor = name.endswith("m") and not name.endswith("maj")
    root = NOTE[name.rstrip("m")]
    base = 12 * (octave + 1) + root
    return [base, base + (3 if minor else 4), base + 7]


MOODS = {
    "mystery": {"bpm": 116, "prog": ["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"], "drums": 0.6, "pluck": 1.0, "lead": 0.8, "pad": 0.8},
    "tension": {"bpm": 128, "prog": ["Em", "C", "Am", "B", "Em", "C", "D", "B"], "drums": 1.0, "pluck": 0.9, "lead": 0.7, "pad": 0.7},
    "playful": {"bpm": 120, "prog": ["C", "Am", "F", "G", "C", "Em", "F", "G"], "drums": 0.7, "pluck": 1.1, "lead": 0.6, "pad": 0.5},
    "sad": {"bpm": 78, "prog": ["Am", "F", "C", "G", "Am", "F", "Dm", "E"], "drums": 0.0, "pluck": 0.6, "lead": 0.9, "pad": 1.0},
    "war": {"bpm": 96, "prog": ["Cm", "Ab", "Eb", "Bb", "Cm", "Ab", "Fm", "G"], "drums": 1.0, "pluck": 0.4, "lead": 0.9, "pad": 1.0},
}


def pluck(f, d, bright=1.0):
    t = np.arange(int(SR * d)) / SR
    x = np.zeros_like(t)
    for k in range(1, 7):
        if f * k > 9000:
            break
        x += np.sin(2 * np.pi * f * k * t) * (bright ** (k - 1)) / k * np.exp(-t * (5 + 4 * k))
    att = np.minimum(1, t / 0.003)
    return x * att


def pad_voice(f, d):
    t = np.arange(int(SR * d)) / SR
    x = np.zeros_like(t)
    for det in (-0.08, 0.0, 0.07):
        ff = f * 2 ** (det / 12)
        for k in range(1, 6):
            x += np.sin(2 * np.pi * ff * k * t + det * 10) / (k ** 1.5)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.5)
    return x * np.clip(e, 0, 1) / 3


def lead(f, d):
    t = np.arange(int(SR * d)) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    e = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.25)
    return x * np.clip(e, 0, 1)


def kick():
    t = np.arange(int(SR * 0.35)) / SR
    f = 45 + 80 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def shaker(rng):
    n = int(SR * 0.06)
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(8) / 8, mode="same")
    return x * np.exp(-np.arange(n) / SR * 60) * 0.5


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


def render(dur, mood="mystery", bpm=None, seed=3):
    M = MOODS[mood]
    rng = np.random.default_rng(seed)
    bpm = bpm or M["bpm"]
    beat = 60.0 / bpm
    bar = beat * 4
    n = int(SR * (dur + 2))
    L = np.zeros(n); Rr = np.zeros(n)
    prog = M["prog"]
    nbars = int(np.ceil(dur / bar)) + 1
    melody_prev = None
    for b in range(nbars):
        t0 = b * bar
        ch = chord(prog[b % len(prog)], 3)
        intro = b < 2
        # pad
        if M["pad"] > 0:
            for m in ch:
                v = pad_voice(hz(m), bar + 0.3) * 0.16 * M["pad"]
                place(L, v, t0); place(Rr, v * 0.9, t0)
        # bass
        bnote = ch[0] - 12
        for q in range(4):
            v = pluck(hz(bnote), beat * 0.95, 0.4) * (0.35 if q % 2 == 0 else 0.22)
            place(L, v, t0 + q * beat); place(Rr, v, t0 + q * beat)
        # plucked arpeggio (8ths), chord tones up an octave, slight pattern variation
        pat = [0, 1, 2, 1, 0, 2, 1, 2] if b % 2 == 0 else [0, 2, 1, 2, 0, 1, 2, 1]
        for e8 in range(8):
            m = ch[pat[e8]] + 12 + (12 if e8 in (3, 7) and rng.random() < 0.4 else 0)
            v = pluck(hz(m), beat * 0.9, 0.55) * 0.13 * M["pluck"] * (0.6 if intro else 1)
            pan = 0.35 + 0.3 * (e8 % 2)
            place(L, v * (1 - pan), t0 + e8 * beat / 2); place(Rr, v * pan, t0 + e8 * beat / 2)
        # sustained lead: two notes per bar on chord tones in the 600-1600 Hz band
        if not intro and M["lead"] > 0:
            for h in range(2):
                choices = [m + 24 for m in ch] + [ch[0] + 36]
                m = choices[rng.integers(0, len(choices))]
                if melody_prev is not None and abs(m - melody_prev) > 7:
                    m = min(choices, key=lambda x: abs(x - melody_prev))
                melody_prev = m
                v = lead(hz(m), bar / 2 * 0.98) * 0.075 * M["lead"]
                place(L, v * 0.8, t0 + h * bar / 2); place(Rr, v, t0 + h * bar / 2)
        # drums
        if M["drums"] > 0 and not intro:
            for q in range(4):
                if q in (0, 2):
                    k = kick() * 0.4 * M["drums"]
                    place(L, k, t0 + q * beat); place(Rr, k, t0 + q * beat)
                for s8 in range(2):
                    sh = shaker(rng) * 0.18 * M["drums"] * (1.0 if s8 else 0.6)
                    place(L, sh * 0.7, t0 + q * beat + s8 * beat / 2); place(Rr, sh, t0 + q * beat + s8 * beat / 2)
    # gentle end: fade the last 1.2 s
    n2 = int(SR * dur)
    L = L[:n2]; Rr = Rr[:n2]
    fade = np.ones(n2)
    fl = int(SR * 1.2)
    fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
    fade[: int(SR * 0.05)] = np.linspace(0, 1, int(SR * 0.05))
    st = np.stack([L * fade, Rr * fade], 1)
    st /= (np.max(np.abs(st)) + 1e-9)
    return st * 0.7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--mood", default="mystery", choices=sorted(MOODS))
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    x = render(a.dur, a.mood, a.bpm, a.seed)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                          "-c:a", "pcm_s16le", a.out], stdin=subprocess.PIPE)
    p.communicate(x.astype(np.float32).tobytes())
    print(f"music ({a.mood}) {a.dur:.1f}s -> {a.out}")


if __name__ == "__main__":
    main()
