"""Final soundtrack: narration + ducked music bed + timed SFX, mastered for Shorts.

  python mix.py PROJECT [--spec plan/spec.json] [--music-db -17] [--lufs -14] [-o audio/mix.wav]

Reads spec.audio: {"voice": "audio/voice.wav", "music": "audio/music.wav", "music_db": -17,
                   "sfx": [{"t": 1.2, "file": "audio/sfx/whoosh.wav", "gain_db": -8},
                           {"t": 3.5, "file": "audio/sfx/day_breeze.wav", "gain_db": -20, "offset": 0, "dur": 10,
                            "fade_in": 0.3, "fade_out": 0.4}, ...]}          # trimmed/faded beds and long effects
House levels (measured): music sits ~15-20 dB under the voice and dips a little more while words are spoken;
SFX are short and sit 4-12 dB under the voice (whooshes -10, pops -12, impacts -6); integrated loudness of the
samples is -14 to -18 LUFS, peaks just under -1 dBTP. Output: 48 kHz stereo WAV, loudness-normalised.
"""
import argparse
import json
import os
import subprocess
import tempfile

import numpy as np

SR = 48000


def load(path, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def db(x):
    return 10 ** (x / 20.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec_compiled.json", help="compiled spec (falls back to plan/spec.json)")
    ap.add_argument("--music-db", type=float)
    ap.add_argument("--duck-db", type=float, default=4.0, help="extra music dip under speech")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("-o", "--out", default="audio/mix.wav")
    a = ap.parse_args()
    P = a.project
    sp = os.path.join(P, a.spec)
    if not os.path.exists(sp):
        sp = os.path.join(P, "plan", "spec.json")
    spec = json.load(open(sp, encoding="utf-8"))
    if "_compiled" not in spec:
        from compile_spec import compile_spec
        spec = compile_spec(spec, P)
    A = spec.get("audio", {})
    dur = float(spec["meta"]["duration"])
    n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    voice = None
    if A.get("voice") and os.path.exists(os.path.join(P, A["voice"])):
        voice = load(os.path.join(P, A["voice"]))
        # normalise speech so its active RMS is -16 dBFS (music/SFX levels are relative to this)
        mono0 = voice.mean(1)
        hop0 = int(SR * 0.02)
        m0 = max(1, len(mono0) // hop0)
        r0 = np.sqrt((mono0[: m0 * hop0].reshape(m0, hop0) ** 2).mean(1))
        act0 = r0[20 * np.log10(r0 + 1e-9) > -45]
        if len(act0):
            voice = voice * (db(-16) / (np.sqrt((act0 ** 2).mean()) + 1e-9))
        off = int(float(A.get("voice_offset", 0)) * SR)
        v = voice[: max(0, n - off)]
        out[off:off + len(v)] += v
    # speech envelope for ducking (20 ms RMS, smoothed)
    env = np.zeros(n)
    if voice is not None:
        mono = out.mean(1)
        hop = int(SR * 0.02)
        m = len(mono) // hop
        r = np.sqrt((mono[: m * hop].reshape(m, hop) ** 2).mean(1))
        act = (20 * np.log10(r + 1e-9) > -40).astype(float)
        k = np.ones(15) / 15
        act = np.convolve(act, k, mode="same")
        env = np.repeat(act, hop)
        env = np.pad(env, (0, max(0, n - len(env))))[:n]
    if A.get("music") and os.path.exists(os.path.join(P, A["music"])):
        mu = load(os.path.join(P, A["music"]))
        if len(mu) < n:  # loop the bed with a short crossfade
            reps = int(np.ceil(n / len(mu))) + 1
            mu = np.concatenate([mu] * reps)
        mu = mu[:n]
        level = a.music_db if a.music_db is not None else float(A.get("music_db", -17))
        # bed RMS -> -16 dBFS (same as the speech), then sit it `level` dB under the voice and dip under words
        rms = np.sqrt((mu ** 2).mean()) + 1e-9
        mu = mu / rms * db(-16)
        gain = db(level) * (1 - (1 - db(-a.duck_db)) * env)
        out += mu * gain[:, None]
    for s in A.get("sfx", []):
        f = os.path.join(P, s["file"])
        if not os.path.exists(f):
            print("missing sfx", f)
            continue
        x = load(f)
        # a cue can play part of a file: "offset" (s into the file), "dur" (s), with "fade_in"/"fade_out" (s) -
        # ambience beds and long effects are trimmed here instead of in separate files
        o = int(float(s.get("offset", 0)) * SR)
        x = x[o:o + int(float(s["dur"]) * SR)] if s.get("dur") else x[o:]
        fi, fo = int(float(s.get("fade_in", 0)) * SR), int(float(s.get("fade_out", 0)) * SR)
        if fi > 0 and len(x):
            x[:fi] *= np.linspace(0, 1, min(fi, len(x)))[:, None]
        if fo > 0 and len(x):
            x[-fo:] *= np.linspace(1, 0, min(fo, len(x)))[:, None]
        x = x * db(float(s.get("gain_db", -8)))
        i = int(float(s["t"]) * SR)
        if i >= n:
            continue
        j = min(n, i + len(x))
        out[i:j] += x[: j - i]
    tmp = os.path.join(tempfile.gettempdir(), f"ra_premix_{os.getpid()}.wav")   # outside the project: some shells cannot delete there
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                          "-c:a", "pcm_f32le", tmp], stdin=subprocess.PIPE)
    p.communicate(out.astype(np.float32).tobytes())
    # two-pass loudnorm
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", f"loudnorm=I={a.lufs}:TP=-1.2:LRA=9:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(m[m.rfind("{"): m.rfind("}") + 1])
    flt = (f"loudnorm=I={a.lufs}:TP=-1.2:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
           f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    dst = os.path.join(P, a.out)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", flt, "-ar", str(SR), "-c:a", "pcm_s16le", dst], check=True)
    try:
        os.remove(tmp)
    except OSError:
        pass
    print(f"mix -> {dst} ({dur:.1f}s, target {a.lufs} LUFS, {len(A.get('sfx', []))} sfx)")


if __name__ == "__main__":
    main()
