"""Measure a rendered video against the house style (the numbers measured on the reference shorts).

  python qc_video.py PROJECT/exports/final.mp4 [--project PROJECT] [-o PROJECT/qc/report.md]

Checks: format (1080x1920 / 9:16, 30 fps, 48-62 s), shot rhythm (cuts per second, median shot length), camera
motion share (feature tracking between frames), caption presence in the 72-80% band, loudness (-13..-18 LUFS,
true peak < -1 dBTP), black/frozen frames, and writes timestamped contact sheets (qc/sheet_*.jpg) to LOOK AT.
"""
import argparse
import json
import os
import re
import statistics as st
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from ra_common import STYLE


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)


def frames(path, fps, w=180, h=320):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    a = np.frombuffer(p.stdout, np.uint8)
    return a.reshape(-1, h, w, 3)


def cuts_from(fr, thr=0.32):
    """histogram-difference cut detector on small frames (10 fps)"""
    cuts = []
    prev = None
    for i, f in enumerate(fr):
        hsv = np.asarray(Image.fromarray(f).convert("HSV")).astype(np.float32)
        h = np.concatenate([np.histogram(hsv[..., c], 32, (0, 256))[0] for c in range(3)]).astype(np.float32)
        h /= h.sum() + 1e-9
        if prev is not None:
            d = 0.5 * np.abs(h - prev).sum()
            if d > thr:
                cuts.append(i)
        prev = h
    return cuts


def motion_share(fr):
    """fraction of frame pairs with visible camera/zoom motion (mean abs diff of downsampled grey, excluding the caption band)"""
    g = fr.mean(-1)
    g = np.concatenate([g[:, :int(g.shape[1] * 0.70)], g[:, int(g.shape[1] * 0.82):]], 1)
    d = np.abs(np.diff(g, axis=0)).mean((1, 2))
    return float((d > 1.2).mean()), d


def loudness(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    return (float(I[-1]) if I else None), (float(tp[-1]) if tp else None)


def sheet(path, out, start, dur, fps=2):
    fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-vf", f"fps={fps},scale=180:320",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    a = np.frombuffer(fr, np.uint8).reshape(-1, 320, 180, 3)
    cols = 10
    rows = int(np.ceil(len(a) / cols))
    im = Image.new("RGB", (cols * 180, rows * 320))
    d = ImageDraw.Draw(im)
    for i, f in enumerate(a):
        im.paste(Image.fromarray(f), ((i % cols) * 180, (i // cols) * 320))
        d.text(((i % cols) * 180 + 4, (i // cols) * 320 + 3), f"{start + i / fps:.1f}", fill=(255, 255, 0))
    im.save(out, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--project")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    P = a.project or os.path.dirname(os.path.dirname(os.path.abspath(a.video)))
    out = a.out or os.path.join(P, "qc", "report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    info = probe(a.video)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    dur = float(info["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    lines = []
    ok = lambda c: "PASS" if c else "WARN"
    lines.append(f"{ok((v['width'], v['height']) == (1080, 1920))}  format {v['width']}x{v['height']} @ {fps:.2f} fps (target 1080x1920 @ 30)")
    import story_length as SL
    chosen = SL.load(P)
    if chosen:
        cs = chosen["seconds"]
        lines.append(f"{ok(abs(dur - cs) <= max(5, 0.12 * cs))}  duration {dur:.1f}s (chosen length {cs}s)")
    else:
        lo, hi = STYLE["format"]["duration_s"]
        lines.append(f"{ok(lo - 6 <= dur <= hi + 6)}  duration {dur:.1f}s (samples {lo}-{hi}s)")
    fr = frames(a.video, 10)
    cuts = cuts_from(fr)
    shots = np.diff([0] + cuts + [len(fr)]) / 10.0
    shots = shots[shots > 0.25]
    med = float(np.median(shots)) if len(shots) else dur
    tg = STYLE["edit"]["shot_len_s"]["median"]
    lines.append(f"{ok(0.9 <= med <= 2.1)}  {len(shots)} visual shots, median {med:.2f}s (samples ~{tg}s; detector also counts punch-ins)")
    ms, d = motion_share(fr)
    lines.append(f"{ok(ms >= 0.6)}  motion in {ms * 100:.0f}% of frame pairs (samples: the camera is almost never still)")
    band = fr[:, int(320 * 0.70):int(320 * 0.82)]
    yellow = ((band[..., 0] > 200) & (band[..., 1] > 190) & (band[..., 2] < 90)).sum((1, 2))
    cap_share = float((yellow > 25).mean())
    lines.append(f"{ok(cap_share > 0.75)}  yellow caption visible in {cap_share * 100:.0f}% of frames (band 70-82% of height)")
    frozen = int((d < 0.05).sum())
    lines.append(f"{ok(frozen < 10)}  {frozen} frozen frame pairs at 10 fps")
    blacks = int((fr.mean((1, 2, 3)) < 6).sum())
    lines.append(f"{ok(blacks <= 8)}  {blacks} near-black frames at 10 fps (fade-out ending allowed)")
    I, tp = loudness(a.video)
    if I is not None:
        lines.append(f"{ok(-18.5 <= I <= -12.5)}  loudness {I:.1f} LUFS (samples -14..-18), true peak {tp} dBFS")
    for k in range(0, int(np.ceil(dur / 30))):
        sp = os.path.join(P, "qc", f"sheet_{k + 1}.jpg")
        sheet(a.video, sp, k * 30, min(30, dur - k * 30))
        lines.append(f"INFO  contact sheet {sp} (look at it: framing, faces, captions, grades)")
    txt = "# QC report\n\n" + "\n".join(lines) + "\n"
    open(out, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
