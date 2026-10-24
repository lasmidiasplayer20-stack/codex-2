"""Mux the picture (After Effects render or preview render) with the final mix into the upload file.

  python finish.py PROJECT [--video exports/ae_render.mp4] [--audio audio/mix.wav] [-o exports/final.mp4]

Encodes H.264 High, CRF 16, yuv420p, 30 fps CFR, AAC 192 kbps 48 kHz, +faststart (YouTube Shorts / TikTok / Reels).
If the video is shorter or longer than the audio it is cut to the audio length.
"""
import argparse
import glob
import os
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--video")
    ap.add_argument("--audio", default="audio/mix.wav")
    ap.add_argument("-o", "--out", default="exports/final.mp4")
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()
    P = a.project
    v = a.video
    if not v:
        c = sorted(glob.glob(os.path.join(P, "exports", "ae_render.*")), key=os.path.getmtime)
        c = [x for x in c if not x.endswith(".done")]
        if not c:
            c = [os.path.join(P, "exports", "preview.mp4")]
        v = c[-1]
    else:
        v = os.path.join(P, v) if not os.path.isabs(v) else v
    au = os.path.join(P, a.audio)
    out = os.path.join(P, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", v]
    if os.path.exists(au):
        cmd += ["-i", au, "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    cmd += ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
            "-r", "30", "-fps_mode", "cfr", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]   # -fps_mode: ffmpeg 8+ removed -vsync
    subprocess.run(cmd, check=True)
    print("final ->", out)


if __name__ == "__main__":
    main()
