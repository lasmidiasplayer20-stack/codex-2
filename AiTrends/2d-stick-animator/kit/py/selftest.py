"""Build the self-test project that exercises every engine feature (no API keys, no downloads).

  python selftest.py                 # -> <workspace>/projects/_selftest (spec, art, audio, preview stills)
  then in After Effects (bridge running):
  python make_job.py build projects/_selftest --wait
  python make_job.py stills projects/_selftest --times 0.6,2.2,3.6,5.1,6.4,7.6 --wait
Compare <project>/ae/stills/*.png with <project>/qc/stills/preview_*.png: same framing, poses, faces, icons,
captions and grades (After Effects looks a little richer). Fix anything that differs before real videos.
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

from ra_common import KIT, project_dirs

ROOT = os.path.dirname(KIT)
P = os.path.join(ROOT, "projects", "_selftest")


def room(path, wall=(150, 120, 90), floor=(90, 70, 55), window=True):
    W, H = 1296, 2304
    im = Image.new("RGB", (W, H), wall)
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        c = tuple(int(v * (0.75 + 0.4 * k)) for v in wall) if y < H * 0.68 else tuple(int(v * (1.05 - 0.3 * (k - 0.68) / 0.32)) for v in floor)
        d.line([(0, y), (W, y)], fill=c)
    if window:
        d.rectangle([W * 0.55, H * 0.18, W * 0.85, H * 0.45], fill=(215, 225, 230), outline=(70, 55, 40), width=18)
        d.line([(W * 0.70, H * 0.18), (W * 0.70, H * 0.45)], fill=(70, 55, 40), width=12)
        d.line([(W * 0.55, H * 0.315), (W * 0.85, H * 0.315)], fill=(70, 55, 40), width=12)
    d.rectangle([W * 0.08, H * 0.36, W * 0.32, H * 0.68], fill=(60, 45, 35))
    for i in range(0, W, 120):
        d.line([(i, H * 0.68), (i - 300, H)], fill=tuple(int(v * 0.85) for v in floor), width=4)
    im = im.filter(ImageFilter.GaussianBlur(2))
    im.save(path, quality=92)


def street(path):
    W, H = 1296, 2304
    im = Image.new("RGB", (W, H), (120, 130, 145))
    d = ImageDraw.Draw(im)
    for y in range(int(H * 0.7)):
        k = y / (H * 0.7)
        d.line([(0, y), (W, y)], fill=(int(150 - 40 * k), int(165 - 40 * k), int(185 - 40 * k)))
    rnd = random.Random(3)
    x = -50
    while x < W:
        w = rnd.randint(220, 380)
        h = rnd.randint(int(H * 0.35), int(H * 0.6))
        col = rnd.choice([(95, 85, 80), (110, 100, 92), (80, 78, 86), (120, 108, 96)])
        d.rectangle([x, H * 0.72 - h, x + w, H * 0.72], fill=col)
        for wy in range(int(H * 0.72 - h + 40), int(H * 0.72 - 60), 110):
            for wx in range(x + 30, x + w - 50, 80):
                d.rectangle([wx, wy, wx + 40, wy + 60], fill=(200, 190, 150) if rnd.random() < 0.3 else (50, 55, 65))
        x += w + rnd.randint(0, 30)
    d.rectangle([0, H * 0.72, W, H], fill=(70, 70, 74))
    d.rectangle([0, H * 0.72, W, H * 0.76], fill=(150, 150, 150))
    im.filter(ImageFilter.GaussianBlur(2.5)).save(path, quality=92)


def main():
    project_dirs(P)
    room(os.path.join(P, "assets/bg/room.jpg"))
    room(os.path.join(P, "assets/bg/office.jpg"), wall=(90, 110, 120), floor=(60, 60, 66), window=False)
    street(os.path.join(P, "assets/bg/street.jpg"))
    icons = os.path.join(KIT, "assets", "icons")
    need = ["skull_and_crossbones", "money_with_wings", "banknote_with_dollar_sign", "warning_sign", "crown", "briefcase", "alarm_clock",
            "droplet", "fire", "top_hat", "page_facing_up", "thinking_face"]
    for n in need:
        s = os.path.join(icons, n + ".png")
        if os.path.exists(s):
            shutil.copy(s, os.path.join(P, "assets/icons", n + ".png"))
        else:
            src = os.path.join(KIT, "assets", "icons_webp", n + ".webp")
            if os.path.exists(src):
                Image.open(src).convert("RGBA").save(os.path.join(P, "assets/icons", n + ".png"))
    sfx = os.path.join(KIT, "assets", "sfx")
    if not os.path.isdir(sfx):
        subprocess.run([sys.executable, os.path.join(KIT, "py", "sfx_kit.py"), "-o", sfx])
    for f in os.listdir(sfx):
        shutil.copy(os.path.join(sfx, f), os.path.join(P, "audio/sfx", f))
    text = "When this guy found a briefcase full of money, he threw it off the roof. The problem was, the police saw everything."
    words, t = [], 0.0
    for w in text.split():
        d = 0.11 + 0.045 * len(w.strip(",."))
        words.append({"w": w, "s": round(t, 3), "e": round(t + d, 3)})
        t += d + (0.08 if w.endswith((",", ".")) else 0.02)
    json.dump(words, open(os.path.join(P, "timing/words.json"), "w"), indent=0)
    sys.argv = ["captions.py", os.path.join(P, "timing/words.json"), "-o", os.path.join(P, "timing"), "--red", "police"]
    import captions
    captions.main()
    caps = json.load(open(os.path.join(P, "timing/captions.json")))
    dur = round(t + 0.4, 2)
    subprocess.run([sys.executable, os.path.join(KIT, "py", "music.py"), "-o", os.path.join(P, "audio/music.wav"), "--dur", str(dur)], capture_output=True)

    def w_at(word, after=0.0):
        for x in words:
            if x["w"].strip(",.").lower() == word.lower() and x["s"] >= after:
                return x["s"]
        raise SystemExit("selftest: word not found " + word)
    b1 = w_at("he", 1.0)
    b2 = w_at("The", b1) - 0.02
    b3 = w_at("police") - 0.02
    spec = {
        "version": 1,
        "meta": {"title": "SELF TEST", "slug": "_selftest", "fps": 30, "width": 1080, "height": 1920, "duration": dur},
        "audio": {"voice": "", "music": "audio/music.wav", "music_db": -17, "sfx": []},
        "captions": caps,
        "cast": {
            "guy": {"color": "#35DD6D", "glow": 0.45, "parts": ["hair_short", "tie"], "c1": "#2E2E32", "c2": "#1E1E22"},
            "cop": {"color": "#F4F4F4", "parts": ["police_cap", "uniform"], "c1": "#2F4A8A", "c2": "#E8B53A"},
            "lady": {"color": "#F091E6", "parts": ["hair_long", "dress"], "c1": "#5A3420",
                     "accessories": [{"file": "assets/icons/crown.png", "slot": "head", "w": 0.7, "dx": 0.0, "dy": -0.62, "from": 0, "to": 99}]},
        },
        "look": {"vignette": 0.42, "grain": 0.025, "end": "fade_black"},
        "shots": [
            {"id": "S01", "t": 0.0, "end": b1, "transition": "cut",
             "bg": {"file": "assets/bg/room.jpg", "grade": "moody", "blur": 3},
             "camera": [{"t": 0.0, "zoom": 1.32, "focus": [540, 1100]}, {"t": 0.55, "zoom": 1.02, "focus": [540, 960], "ease": "out"}, {"t": b1, "zoom": 1.05, "focus": [540, 960], "ease": "linear"}],
             "actors": [{"cast": "guy", "x": 560, "y": 1760, "h": 1000, "keys": [{"t": 0.0, "pose": "reach_down", "eyes": "wide", "mouth": "o"}, {"t": w_at("briefcase"), "pose": "hold_up", "eyes": "happy", "mouth": "grin"}],
                         "hold": [{"t": w_at("briefcase"), "file": "assets/icons/briefcase.png", "hand": "N", "w": 300, "offset": [0, -40]}]}],
             "icons": [{"kind": "thought", "file": "assets/icons/banknote_with_dollar_sign.png", "x": 330, "y": 560, "size": 220, "t": w_at("money"), "tail": [0.5, 0.9]}]},
            {"id": "S02", "t": b1, "end": b2, "transition": "flash",
             "bg": {"file": "assets/bg/street.jpg", "grade": "moody", "blur": 2},
             "camera": [{"t": b1, "zoom": 1.0, "focus": [540, 960]}, {"t": b2, "zoom": 1.14, "focus": [560, 900], "ease": "inout"}],
             "shake": [{"t": w_at("roof"), "dur": 0.4, "amp": 18}],
             "actors": [{"cast": "guy", "x": 300, "y": 1700, "h": 820, "keys": [{"t": b1, "pose": "throw_back", "eyes": "determined"}], "act": [{"t": w_at("threw"), "kind": "throw_once"}]},
                        {"cast": "lady", "x": 760, "y": 1740, "h": 860, "face": -1, "keys": [{"t": b1, "pose": "stand", "eyes": "normal"}, {"t": w_at("roof"), "pose": "cheer", "eyes": "wide", "mouth": "scream"}],
                         "act": [{"t": w_at("roof") + 0.1, "end": b2, "kind": "cheer_bounce"}]}],
             "fx": [{"kind": "money_rain", "file": "assets/icons/banknote_with_dollar_sign.png", "t": w_at("threw"), "count": 24}]},
            {"id": "S03", "t": b2, "end": b3, "transition": "light_leak",
             "bg": {"file": "assets/bg/office.jpg", "grade": "cold", "blur": 3},
             "camera": [{"t": b2, "zoom": 1.0, "focus": [540, 960]}, {"t": b2 + (b3 - b2) * 0.5, "zoom": 1.03, "focus": [540, 960], "ease": "linear"},
                        {"t": b2 + (b3 - b2) * 0.5 + 0.034, "zoom": 1.3, "focus": [700, 900], "ease": "cut"}, {"t": b3, "zoom": 1.35, "focus": [700, 900], "ease": "linear"}],
             "actors": [{"cast": "cop", "x": 740, "y": 1760, "h": 980, "face": -1, "keys": [{"t": b2, "pose": "arms_crossed", "eyes": "determined"}, {"t": w_at("saw"), "pose": "point_fwd", "eyes": "angry", "mouth": "open"}], "talk": [[w_at("saw"), b3]]},
                        {"cast": "guy", "x": 260, "y": 1800, "h": 900, "walk": [{"t": b2, "mode": "run", "speed": 2.4}], "keys": [{"t": b2, "pose": "run", "eyes": "wide", "mouth": "scream"}],
                         "move": [{"t": b2, "x": 420, "y": 1800}, {"t": b3, "x": 120, "y": 1800}], "face": -1}],
             "icons": [{"kind": "badge", "file": "assets/icons/alarm_clock.png", "x": 600, "y": 600, "size": 210, "t": w_at("police") - 0.6, "text": "3D", "text_pos": [0, 40], "text_size": 120},
                       {"kind": "emoji", "file": "assets/icons/warning_sign.png", "x": 820, "y": 520, "size": 200, "t": w_at("saw")}]},
            {"id": "S04", "t": b3, "end": dur, "transition": "glitch",
             "bg": {"file": "assets/bg/street.jpg", "grade": "dark", "blur": 3},
             "camera": [{"t": b3, "zoom": 1.28, "focus": [540, 1000]}, {"t": b3 + 0.5, "zoom": 1.0, "focus": [540, 960], "ease": "out"}, {"t": dur, "zoom": 1.03, "focus": [540, 960], "ease": "linear"}],
             "actors": [{"cast": "guy", "x": 540, "y": 1780, "h": 1050, "keys": [{"t": b3, "pose": "hands_head", "eyes": "dead", "mouth": "scream"}], "state": "silhouette",
                         "states": [{"t": b3 + 0.6, "end": dur, "state": "gray"}]}],
             "icons": [{"kind": "emoji", "file": "assets/icons/skull_and_crossbones.png", "x": 540, "y": 560, "size": 260, "t": b3 + 0.15, "no": False}],
             "fx": [{"kind": "tint", "color": "#C8202A", "opacity": 30}, {"kind": "embers", "count": 24}],
             "state": [{"kind": "bw", "t": b3 + 0.6, "fade": 0.3}]},
        ],
    }
    json.dump(spec, open(os.path.join(P, "plan/spec.json"), "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(KIT, "py", "compile_spec.py"), P])
    subprocess.run([sys.executable, os.path.join(KIT, "py", "mix.py"), P])
    times = [0.6, round(b1 + 0.5, 2), round(b2 + 0.4, 2), round(b3 - 0.3, 2), round(b3 + 0.3, 2), round(dur - 0.6, 2)]
    subprocess.run([sys.executable, os.path.join(KIT, "py", "ra_preview.py"), P, "--stills", ",".join(str(x) for x in times)])
    print(f"self-test project ready: {P}\n  stills to compare at: {times}\n  next: python make_job.py build projects/_selftest --wait")


if __name__ == "__main__":
    main()
