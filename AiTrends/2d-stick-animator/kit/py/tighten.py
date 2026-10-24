"""Remove the long pauses from a narration so it runs as tight as the samples (gaps <= ~0.18 s).

usage: python tighten.py PROJECT/audio/voice_raw.wav -o PROJECT/audio/voice.wav [--max-pause 0.18] [--keep 0.09]
       [--threshold -38] [--lead 0.0]

Keeps the original file untouched. Silences longer than --max-pause are shortened to --keep seconds with 10 ms
fades so no clicks are introduced. --lead trims leading silence down to that many seconds (the samples start
speaking on frame 1). Prints the before/after duration and the number of pauses shortened.
"""
import argparse
import subprocess

import numpy as np


def read(path, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy(), sr


def write(path, y, sr):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                          "-c:a", "pcm_s16le", path], stdin=subprocess.PIPE)
    p.communicate(y.astype(np.float32).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--max-pause", type=float, default=0.18)
    ap.add_argument("--keep", type=float, default=0.09)
    ap.add_argument("--threshold", type=float, default=-38.0, help="dBFS below which a 10 ms frame is silence")
    ap.add_argument("--lead", type=float, default=0.0)
    ap.add_argument("--tail", type=float, default=0.25)
    a = ap.parse_args()
    y, sr = read(a.inp)
    hop = int(sr * 0.01)
    n = len(y) // hop
    frames = y[: n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(1)) + 1e-9)
    peak = db.max()
    sil = db < max(a.threshold, peak - 45)
    keep = np.ones(n, bool)
    i = 0
    cut = 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            length = (j - i) * 0.01
            if i == 0:
                drop = max(0, (j - i) - int(a.lead / 0.01))
                keep[i:i + drop] = False
            elif j >= n:
                drop = max(0, (j - i) - int(a.tail / 0.01))
                keep[j - drop:j] = False
            elif length > a.max_pause:
                k = int(a.keep / 0.01)
                left = k // 2
                keep[i + left:j - (k - left)] = False
                cut += 1
            i = j
        else:
            i += 1
    out = []
    fade = int(sr * 0.01)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)
    i = 0
    while i < n:
        if keep[i]:
            j = i
            while j < n and keep[j]:
                j += 1
            seg = y[i * hop: j * hop].copy()
            if len(seg) > 2 * fade:
                seg[:fade] *= ramp
                seg[-fade:] *= ramp[::-1]
            out.append(seg)
            i = j
        else:
            i += 1
    res = np.concatenate(out) if out else y
    write(a.out, res, sr)
    print(f"{len(y) / sr:.2f}s -> {len(res) / sr:.2f}s, {cut} long pauses shortened (max {a.max_pause}s, kept {a.keep}s)")


if __name__ == "__main__":
    main()
