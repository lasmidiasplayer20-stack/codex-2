"""2D Stick Animator preview renderer (animatic + fallback final renderer).

Renders plan/spec.json with the same semantics as the After Effects engine: rigged characters (poses, walk/run,
idle, talk, blink, faces, costumes, accessories, held props, outline + bevel + glow, states), backgrounds with
grades, the eased camera (push/pull/punch/pan/shake), props and icons with pop-ins, bubbles and badges, money
rain/embers/rain/smoke/tint/glitch/flash/video overlays, B&W states, transitions, vignette, grain and the
one-word pop captions.

  python ra_preview.py PROJECT                       # half-res 15 fps animatic -> exports/preview.mp4 (+ audio)
  python ra_preview.py PROJECT --full                # 1080x1920 30 fps (fallback final picture) -> exports/preview_full.mp4
  python ra_preview.py PROJECT --stills 0.5,3.2,7    # PNG stills -> qc/stills/
  python ra_preview.py PROJECT --sheet               # contact sheet every 0.5 s -> qc/preview_sheet.jpg
  options: --from 10 --to 20, --scale 0.5, --fps 15, --no-audio, --spec plan/spec.json

It is a check and a fallback: the After Effects build is the master (editable, higher fidelity).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_skia import skia  # noqa: E402
import creatures as CR  # noqa: E402
import ra_rig as RIGM  # noqa: E402
from ra_common import KIT, STYLE  # noqa: E402

RIG = RIGM.RIG
FACES = RIGM.FACES
POSE_KEYS = ["lean", "head", "hipX", "hipY", "turn", "fFront", "aFu", "aFl", "aNu", "aNl", "lFu", "lFl", "lNu", "lNl"]
EYE_NAMES = {v: k for k, v in FACES["eye_codes"].items()}
MOUTH_NAMES = {v: k for k, v in FACES["mouth_codes"].items()}
GRADES = {
    "none": (0, 0, 0, None, 0), "moody": (18, -8, 6, None, 0), "dark": (25, -22, 8, "#0E1A2A", 18),
    "night": (30, -30, 10, "#0A1A3A", 30), "warm": (5, -4, 4, "#FF9A3C", 12), "cold": (15, -6, 6, "#3C8CFF", 14),
    "sepia": (70, -6, 4, "#A8743A", 30), "bw": (100, -6, 10, None, 0), "green": (20, -10, 4, "#3AA64A", 30),
    "red": (20, -10, 8, "#C8202A", 26)}


# ============================================================================ timing curves (AE-style eases)
def bezier_ease(x, o, n):
    """AE temporal ease with zero speeds: cubic bezier (o,0),(1-n,1) in normalised time (o,n in 0..1)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    p1x, p2x = max(1e-4, o), 1 - max(1e-4, n)
    lo, hi = 0.0, 1.0
    for _ in range(30):
        u = (lo + hi) / 2
        bx = 3 * (1 - u) ** 2 * u * p1x + 3 * (1 - u) * u * u * p2x + u ** 3
        if bx < x:
            lo = u
        else:
            hi = u
    u = (lo + hi) / 2
    return 3 * (1 - u) * u * u + u ** 3


def interp(keys, t, influence=(0.6, 0.6)):
    """keys: list of (t, value, (out_inf, in_inf) for the segment that ENDS at this key, hold_out bool)."""
    if not keys:
        return None
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(1, len(keys)):
        if t < keys[i][0]:
            t0, v0 = keys[i - 1][0], keys[i - 1][1]
            t1, v1 = keys[i][0], keys[i][1]
            if len(keys[i - 1]) > 3 and keys[i - 1][3]:
                return v0
            o, n = keys[i][2] if len(keys[i]) > 2 and keys[i][2] else influence
            k = bezier_ease((t - t0) / max(1e-6, t1 - t0), o, n)
            if isinstance(v0, (list, tuple)):
                return [a + (b - a) * k for a, b in zip(v0, v1)]
            return v0 + (v1 - v0) * k
    return keys[-1][1]


def id_hash(cid):
    """a small number from a character id: every character blinks, talks and sways on its own timing (two ids of the
    same length used to blink in sync). Same formula in the AE engine."""
    return sum((i + 1) * ord(ch) for i, ch in enumerate(str(cid))) % 997


def hash01(n):
    """deterministic 0..1 hash, identical to hash01() in ra_engine.jsx and to the expressions it writes"""
    x = math.sin(n * 12.9898) * 43758.5453
    return x - math.floor(x)


def tilt_at(tilt, t):
    """whole-body rotation keys [{t, rot, ease}] ('in' = accelerating fall, like the AE engine's 'in' ease)"""
    if not tilt:
        return 0.0
    ks = sorted(tilt, key=lambda k: k["t"])
    seq = [(k["t"], float(k.get("rot", 0)), (0.75, 0.10) if k.get("ease") == "in" else (0.6, 0.6), False) for k in ks]
    return interp(seq, t)


def face_color_at(entries, t):
    """entries [(t, dur, amount, rgb)] -> (amount, rgb) at time t; amounts fade linearly over dur"""
    amt, col = 0.0, None
    for (t0, d, a, c) in entries:
        if t < t0:
            break
        u = 1.0 if d <= 0 else min(1.0, (t - t0) / d)
        amt = amt + (a - amt) * u
        if c is not None:
            col = c
    return amt, col


def hold(keys, t, default=None):
    v = default
    for kt, kv in keys:
        if kt <= t + 1e-6:
            v = kv
        else:
            break
    return v


EASE = {"inout": (0.6, 0.6), "out": (0.05, 0.92), "in": (0.75, 0.10), "linear": (0.001, 0.001)}


def set_keys_style(times, values, ease):
    if isinstance(ease, (int, float)):
        inf = (ease / 100.0, ease / 100.0)
    elif ease == "hold":
        return [(t, v, None, True) for t, v in zip(times, values)]
    else:
        inf = EASE.get(ease, (0.6, 0.6))
    return [(t, v, inf, False) for t, v in zip(times, values)]


# ============================================================================ image helpers
def hexrgb(h, d=(1, 1, 1)):
    return RIGM.hex2rgb(h, d)


def to_skimage(arr_rgba_premul_float):
    a = (np.clip(arr_rgba_premul_float, 0, 1) * 255).astype(np.uint8)
    return skia.Image.fromarray(np.ascontiguousarray(a), colorType=skia.ColorType.kRGBA_8888_ColorType,
                                alphaType=skia.AlphaType.kPremul_AlphaType)


def pil_to_skia(im):
    im = im.convert("RGBA")
    a = np.asarray(im).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return to_skimage(a)


def grade_image(im, gname, blur=0):
    desat, bright, contrast, tint, top = GRADES.get(gname or "moody", GRADES["moody"])
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    if desat:
        lum = (a * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
        a = a + (lum - a) * (desat / 100.0)
    a = a + bright / 255.0 * 1.0
    a = (a - 0.5) * (1 + contrast / 100.0) + 0.5
    if tint and top:
        c = np.array(hexrgb(tint), np.float32)
        sl = np.where(c < 0.5, a - (1 - 2 * c) * a * (1 - a), a + (2 * c - 1) * (np.sqrt(np.clip(a, 0, 1)) - a))
        a = a + (sl - a) * (top / 100.0)
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGB")
    if blur:
        out = out.filter(ImageFilter.GaussianBlur(blur))
    return out


class VideoReader:
    def __init__(self, path, w, h, fps):
        self.path, self.w, self.h, self.fps = path, w, h, fps
        self.proc = None
        self.idx = -1
        self.frame = None
        self.start_t = None

    def _open(self, t):
        if self.proc:
            self.proc.kill()
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.3f}", "-stream_loop", "-1", "-i", self.path,
                                      "-vf", f"scale={self.w}:{self.h}:force_original_aspect_ratio=increase,crop={self.w}:{self.h},fps={self.fps}",
                                      "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
        self.start_t = t
        self.idx = -1

    def get(self, t):
        want = int(round((t - (self.start_t or 0)) * self.fps)) if self.start_t is not None else None
        if self.proc is None or want is None or want < self.idx or want - self.idx > self.fps * 3:
            self._open(t)
            want = 0
        while self.idx < want:
            raw = self.proc.stdout.read(self.w * self.h * 4)
            if len(raw) < self.w * self.h * 4:
                break
            self.frame = raw
            self.idx += 1
        if self.frame is None:
            return None
        arr = np.frombuffer(self.frame, np.uint8).reshape(self.h, self.w, 4)
        return skia.Image.fromarray(arr.copy(), colorType=skia.ColorType.kRGBA_8888_ColorType)


# ============================================================================ the renderer
class Renderer:
    def __init__(self, project, spec, scale=0.5, fps=15):
        self.P = project
        self.spec = spec
        M = spec["meta"]
        self.W0, self.H0 = M.get("width", 1080), M.get("height", 1920)
        self.k = scale
        self.W, self.H = int(round(self.W0 * scale / 2) * 2), int(round(self.H0 * scale / 2) * 2)
        self.fps = fps
        self.dur = float(M["duration"])
        self.images = {}
        self.videos = {}
        self.bgcache = {}
        self.font = self._font()
        self.timelines = self._timelines()
        self.rng = np.random.default_rng(5)
        self.particles = {}

    # ------------------------------------------------------------------ assets
    def path(self, rel):
        if not rel:
            return None
        return rel if os.path.isabs(rel) else os.path.join(self.P, rel)

    def img(self, rel):
        p = self.path(rel)
        if p in self.images:
            return self.images[p]
        im = None
        if p and os.path.exists(p) and not p.lower().endswith((".mp4", ".mov", ".webm", ".m4v")):
            try:
                im = pil_to_skia(Image.open(p))
            except Exception:
                im = None
        self.images[p] = im
        return im

    def _font(self):
        names = STYLE["captions"]["fonts"]
        cands = [os.path.join(KIT, "fonts", "Anton-Regular.ttf")]
        for n in names:
            tf = skia.Typeface.MakeFromName(n, skia.FontStyle.Bold())
            if tf and tf.getFamilyName().lower().replace(" ", "") in n.lower().replace("-", "").replace(" ", ""):
                return tf
        for c in cands:
            if os.path.exists(c):
                return skia.Typeface.MakeFromFile(c)
        return skia.Typeface.MakeFromName("Impact", skia.FontStyle.Bold()) or skia.Typeface.MakeDefault()

    # ------------------------------------------------------------------ actor timelines (same rules as the AE engine)
    def _timelines(self):
        spec = self.spec
        f = 1.0 / 30
        TL = {}
        for sh in spec["shots"]:
            for ac in sh.get("actors", []):
                cid = ac.get("cast")
                if cid not in spec.get("cast", {}):
                    continue
                tl = TL.setdefault(cid, {"pose": [], "eyes": [], "mouth": [], "gaze": [], "gazeY": [], "walk": [], "run": [], "wspeed": [], "armsw": [], "talk": [], "holds": [], "flush": []})
                keys = sorted(ac.get("keys") or [{"t": sh["t"], "pose": "stand"}], key=lambda x: x["t"])
                if keys[0]["t"] > sh["t"] + 0.001:
                    keys.insert(0, {"t": sh["t"], "pose": keys[0].get("pose", "stand"), "eyes": keys[0].get("eyes"), "mouth": keys[0].get("mouth")})
                for i, k in enumerate(keys):
                    t = max(sh["t"], k["t"])
                    pose = k.get("pose") or (keys[i - 1].get("pose") if i else "stand")
                    v = RIGM.pose_params(pose, k.get("set"))
                    tl["pose"].append((t, (f if i == 0 else k.get("dur", 0.22)), v))
                    if k.get("eyes") is not None:
                        tl["eyes"].append((t, k["eyes"]))
                    elif i == 0:
                        tl["eyes"].append((t, "normal"))
                    if k.get("mouth") is not None:
                        tl["mouth"].append((t, k["mouth"]))
                    elif i == 0:
                        tl["mouth"].append((t, "none"))
                    if k.get("gaze") is not None:
                        tl["gaze"].append((t, k["gaze"]))
                    elif i == 0:
                        tl["gaze"].append((t, RIG["face"]["gaze"]))
                    if k.get("face_color") is not None:
                        fc = k["face_color"]
                        if fc in ("none", "", False):
                            tl["flush"].append((t, float(k.get("dur", 0.35)), 0.0, None))
                        else:
                            hexc = RIG.get("face_colors", {}).get(fc, fc)
                            tl["flush"].append((t, float(k.get("dur", 0.35)), float(k.get("face_amount", RIG.get("face_color_amount", 0.82))),
                                                RIGM.hex2rgb(hexc)))
                    if k.get("gaze_y") is not None:
                        tl["gazeY"].append((t, k["gaze_y"]))
                    elif i == 0:
                        tl["gazeY"].append((t, RIG["face"].get("gaze_y", 0.0)))
                tl["walk"].append((sh["t"], 0)); tl["run"].append((sh["t"], 0)); tl["armsw"].append((sh["t"], 1))
                for lo in ac.get("walk", []):
                    m = lo.get("mode", "walk")
                    tt = max(sh["t"], lo.get("t", sh["t"]))
                    tl["walk"].append((tt, 1 if m == "walk" else 0))
                    tl["run"].append((tt, 1 if m == "run" else 0))
                    tl["wspeed"].append((tt, lo.get("speed", 2.4 if m == "run" else 1.6)))
                    tl["armsw"].append((tt, 0 if lo.get("arms") is False else 1))
                tl["talk"].append((sh["t"], 0))
                for a, b in ac.get("talk", []):
                    tl["talk"].append((max(sh["t"], a), 1))
                    tl["talk"].append((min(sh["end"], b), 0))
                for h in ac.get("hold", []):
                    hh = dict(h)
                    hh["t"] = max(sh["t"], h.get("t", sh["t"]))
                    hh["end"] = min(sh["end"], h.get("end", sh["end"]))
                    tl["holds"].append(hh)
        out = {}
        for cid, tl in TL.items():
            tl["pose"].sort(key=lambda x: x[0])
            pts = []
            cur = tl["pose"][0][2] if tl["pose"] else RIGM.pose_params("stand")   # start IN the first pose
            for (t, d, v) in tl["pose"]:
                last = pts[-1][0] if pts else -1
                t0 = max(t, last + f * 0.5)
                t1 = max(t0 + f * 0.5, t + d)
                pts.append((t0, cur, (0.62, 0.62), False))
                pts.append((t1, v, (0.62, 0.62), False))
                cur = v
            for key in ("eyes", "mouth", "gaze", "gazeY", "walk", "run", "wspeed", "armsw", "talk"):
                tl[key].sort(key=lambda x: x[0])
            tl["pts"] = pts
            out[cid] = tl
        return out

    def actor_state(self, cid, t):
        tl = self.timelines.get(cid)
        if not tl:
            return RIGM.pose_params("stand"), {}
        pts = tl["pts"]
        vals = {}
        for k in POSE_KEYS:
            vals[k] = interp([(p[0], p[1][k], p[2], p[3]) for p in pts], t) if pts else RIGM.pose_params("stand")[k]
        ctl = {"walk": hold(tl["walk"], t, 0), "run": hold(tl["run"], t, 0), "speed": hold(tl["wspeed"], t, 1.6),
               "arms": hold(tl.get("armsw", []), t, 1),
               "eyes": hold(tl["eyes"], t, "normal"), "mouth": hold(tl["mouth"], t, "none"), "gaze": hold(tl["gaze"], t, RIG["face"]["gaze"]), "gaze_y": hold(tl["gazeY"], t, RIG["face"].get("gaze_y", 0.0)),
               "talk": hold(tl["talk"], t, 0)}
        if isinstance(ctl["eyes"], (int, float)):
            ctl["eyes"] = EYE_NAMES.get(int(ctl["eyes"]), "normal")
        if isinstance(ctl["mouth"], (int, float)):
            ctl["mouth"] = MOUTH_NAMES.get(int(ctl["mouth"]), "none")
        if ctl["talk"] > 0.5:
            fidx = int(math.floor(t * RIG["procedural"]["talk_rate"]))
            q = hash01(fidx * 31 + id_hash(cid) * 13)
            m = ctl["mouth"]
            if m in ("smile", "grin"):
                ctl["mouth"] = "grin" if q < 0.5 else "open"
            elif m == "scream":
                ctl["mouth"] = "scream" if q < 0.5 else "open"
            else:
                ctl["mouth"] = "o" if q < 0.35 else ("open" if q < 0.75 else "none")
        # blink
        bseed = id_hash(cid) * 7 + 3    # same deterministic hash as the AE engine's blink expression
        per = RIG["procedural"]["blink_period"][0] + hash01(bseed) * (RIG["procedural"]["blink_period"][1] - RIG["procedural"]["blink_period"][0])
        off = hash01(bseed + 1) * per
        ctl["blink"] = ((t + off) % per) < RIG["procedural"]["blink_frames"] / 30.0
        holds = [h for h in tl["holds"] if h["t"] <= t < h["end"]]
        ctl["hold"] = holds[0] if holds else None
        ctl["phase"] = (id_hash(cid) * 47) % 360
        ctl["flush"] = face_color_at(sorted(tl.get("flush", []), key=lambda x: x[0]), t)
        ctl["idle"] = self.spec["cast"][cid].get("idle", 1)
        return vals, ctl

    # ------------------------------------------------------------------ camera
    def camera(self, sh, t):
        keys = sh.get("camera") or [{"t": sh["t"], "zoom": 1.0}, {"t": sh["end"], "zoom": 1.08}]
        zk, fk, rk = [], [], []
        for i, k in enumerate(keys):
            e = k.get("ease", "inout")
            inf = {"out": (0.05, 0.92), "linear": (0.001, 0.001), "cut": None, "snap": None}.get(e, (0.6, 0.6))
            hold_prev = e in ("cut", "snap")
            if hold_prev and zk:
                zk[-1] = (zk[-1][0], zk[-1][1], zk[-1][2], True)
                fk[-1] = (fk[-1][0], fk[-1][1], fk[-1][2], True)
                rk[-1] = (rk[-1][0], rk[-1][1], rk[-1][2], True)
            zk.append((k["t"], k.get("zoom", 1.0), inf, False))
            fk.append((k["t"], list(k.get("focus", [self.W0 / 2, self.H0 / 2])), inf, False))
            rk.append((k["t"], k.get("roll", 0.0), inf, False))
        z = interp(zk, t)
        fcs = interp(fk, t)
        roll = interp(rk, t)
        sx = sy = 0.0
        for s in sh.get("shake", []):
            if s["t"] <= t < s["t"] + s.get("dur", 0.4):
                amp = s.get("amp", 16) * (1 - (t - s["t"]) / s.get("dur", 0.4))
                sx += amp * math.sin(t * 113.0) * 0.9
                sy += amp * math.cos(t * 97.0) * 0.9
        return z, fcs, roll, (sx, sy)

    def cam_matrix(self, cam):
        z, f, roll, (sx, sy) = cam
        m = skia.Matrix()
        m.setScale(self.k, self.k)
        m.preTranslate(self.W0 / 2 + sx, self.H0 / 2 + sy)
        m.preRotate(roll)
        m.preScale(z, z)
        m.preTranslate(-f[0], -f[1])
        return m

    # ------------------------------------------------------------------ background
    def background(self, canvas, sh, t, cam):
        bg = sh.get("bg") or {}
        f = bg.get("file")
        kind = bg.get("kind") or ("video" if f and f.lower().endswith((".mp4", ".mov", ".webm", ".m4v")) else ("image" if f else "color"))
        wl = bg.get("world")
        Ww, Hw = (float(wl[0]), float(wl[1])) if isinstance(wl, (list, tuple)) and len(wl) == 2 else (self.W0, self.H0)
        canvas.save()
        canvas.concat(self.cam_matrix(cam))
        if kind == "color" or not f or not os.path.exists(self.path(f)):
            c = hexrgb(bg.get("color", "#222428"))
            canvas.drawRect(skia.Rect.MakeXYWH(-Ww * 0.3, -Hw * 0.3, Ww * 1.6, Hw * 1.6), skia.Paint(Color4f=RIGM.skcolor(c)))
        elif kind == "video":
            key = (f, bg.get("grade", "none"))
            vr = self.videos.get(key)
            if vr is None:
                vr = self.videos[key] = VideoReader(self.path(f), self.W0, self.H0, self.fps)
            im = vr.get(bg.get("start", 0) + (t - sh["t"]) * bg.get("speed", 1))
            if im is not None and bg.get("grade") in ("bw", "sepia", "dark", "night"):
                arr = im.toarray()[..., :3].astype(np.float32) / 255.0
                lum = (arr * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
                k = {"bw": 1.0, "sepia": 0.7, "dark": 0.25, "night": 0.3}[bg["grade"]]
                arr = arr + (lum - arr) * k
                arr = arr + GRADES[bg["grade"]][1] / 255.0
                rgba = np.concatenate([np.clip(arr, 0, 1), np.ones_like(arr[..., :1])], -1)
                im = to_skimage(rgba)
            if im is not None:
                sc = bg.get("scale", 1.0)
                w, h = self.W0 * sc, self.H0 * sc
                canvas.drawImageRect(im, skia.Rect.MakeXYWH(self.W0 / 2 - w / 2, self.H0 / 2 - h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
                if bg.get("grade") in ("bw", "sepia"):
                    pass
        else:
            ck = (f, bg.get("grade", "moody"), bg.get("blur", 0))
            im = self.bgcache.get(ck)
            if im is None:
                pil = Image.open(self.path(f)).convert("RGB")
                maxw = int(Ww * self.k * 2.2)
                if pil.width > maxw:
                    pil = pil.resize((maxw, int(pil.height * maxw / pil.width)), Image.LANCZOS)
                pil = grade_image(pil, bg.get("grade", "moody"), bg.get("blur", 0) * self.k * (pil.width / (self.W0 * self.k)))
                im = pil_to_skia(pil)
                self.bgcache[ck] = im
            iw, ih = im.width(), im.height()
            # the picture covers the scene: the frame, or the wider/taller world of this location (bg.world)
            c = max(Ww / iw, Hw / ih) * bg.get("scale", 1.0 if wl else 1.06)
            w, h = iw * c, ih * c
            off = bg.get("offset", [0, 0])
            pan = bg.get("pan", [0, 0])
            u = (t - sh["t"]) / max(1e-3, sh["end"] - sh["t"])
            cx = Ww / 2 + off[0] + pan[0] * u
            cy = Hw / 2 + off[1] + pan[1] * u
            canvas.save()
            canvas.translate(cx, cy)
            if bg.get("flip"):
                canvas.scale(-1, 1)
            canvas.drawImageRect(im, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
            canvas.restore()
        canvas.restore()

    # ------------------------------------------------------------------ props & icons
    def pop_scale(self, t, t0, t1, sh, pop=True, pop_out=False):
        f = 1 / 30.0
        s = 1.0
        if pop and t0 > sh["t"] + 0.02:
            keys = set_keys_style([t0 - f, t0 + 3 * f, t0 + 6 * f, t0 + 9 * f], [0, 1.16, 0.96, 1.0], 55)
            s = interp(keys, t)
        if pop_out and t1 < sh["end"] - 0.02:
            keys = set_keys_style([t1 - 6 * f, t1 - 3 * f, t1], [1, 1.1, 0], 50)
            if t >= t1 - 6 * f:
                s *= interp(keys, t)
        return max(0.0, s)

    def draw_image_centered(self, canvas, im, x, y, w, rot=0, flip=False, alpha=1.0, shadow=True, blend=None):
        h = w * im.height() / im.width()
        canvas.save()
        canvas.translate(x, y)
        if rot:
            canvas.rotate(rot)
        if flip:
            canvas.scale(-1, 1)
        r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        if shadow:
            sp = skia.Paint(ImageFilter=skia.ImageFilters.DropShadowOnly(4, 10, 12, 12, skia.ColorSetARGB(int(140 * alpha * 0.55), 0, 0, 0)))
            canvas.saveLayer(None, sp)
            canvas.drawImageRect(im, r, skia.SamplingOptions(skia.FilterMode.kLinear))
            canvas.restore()
        paint = skia.Paint(AntiAlias=True)
        paint.setAlphaf(alpha)
        if blend:
            paint.setBlendMode(blend)
        canvas.drawImageRect(im, r, skia.SamplingOptions(skia.FilterMode.kLinear), paint)
        canvas.restore()

    def prop(self, canvas, sh, p, t, idx):
        t0, t1 = p.get("t", sh["t"]), p.get("end", sh["end"])
        if not (t0 - (0 if p.get("exact") else 1 / 30) <= t < t1):   # exact: back-to-back frames never overlap
            return
        im = self.img(p.get("file"))
        if im is None:
            return
        s = self.pop_scale(t, t0, t1, sh, p.get("pop", True), p.get("pop_out", False))
        x, y, rot = p.get("x", self.W0 / 2), p.get("y", self.H0 / 2), p.get("rot", 0)
        w = p.get("w", 300) * s
        anim = p.get("anim", "none")
        if anim == "float":
            y += math.sin(t * 2.4 + idx) * p.get("amp", 10)
        elif anim == "bob":
            rot += math.sin(t * 3 + idx) * p.get("amp", 6)
        elif anim == "spin":
            rot += (t - t0) * p.get("speed", 200)
        elif anim == "shake":
            x += math.sin(t * 90) * p.get("amp", 8); y += math.cos(t * 77) * p.get("amp", 8)
        elif anim == "fall":
            k = interp(set_keys_style([t0, t0 + p.get("dur", 0.6)], [0, 1], "in"), t)
            y = p.get("from_y", -200) + (y - p.get("from_y", -200)) * k
        elif anim == "slide":
            k = interp(set_keys_style([t0, t0 + p.get("dur", 0.35)], [0, 1], "out"), t)
            x = x + p.get("dx", -400) * (1 - k)
        elif anim == "grow":
            u = (t - t0) / max(1e-3, t1 - t0)
            w *= 0.85 + 0.23 * u
        elif anim == "drift":
            u = (t - t0) / max(1e-3, t1 - t0)
            x += p.get("dx", 120) * u; y += p.get("dy", 0) * u
        blend = {"screen": skia.BlendMode.kScreen, "add": skia.BlendMode.kPlus}.get(p.get("blend"))
        self.draw_image_centered(canvas, im, x, y, w, rot, p.get("flip", False), p.get("opacity", 100) / 100.0,
                                 p.get("shadow", True) and not blend, blend)

    def creature(self, canvas, sh, c, t):
        """a living creature (flock): every copy alive - same maths as the AE engine (creatures.state)"""
        t0, t1 = c.get("t", sh["t"]), c.get("end", sh["end"])
        if not (t0 - 1 / 30 <= t < t1):
            return
        im = self.img(c.get("file"))
        if im is None:
            return
        pop = self.pop_scale(t, t0, t1, sh, c.get("pop", True), c.get("pop_out", False))
        if pop <= 0.001:
            return
        for i in CR.copies(c):
            x, y, sx, sy, rot = CR.state(c, i, t, sh["t"])
            H = CR.size_of(c, i) * pop
            W = H * im.width() / im.height()
            canvas.save()
            canvas.translate(x, y)
            canvas.rotate(rot)
            canvas.scale(sx, sy)
            r = skia.Rect.MakeXYWH(-W / 2, -H, W, H)
            if c.get("shadow", True):
                sp = skia.Paint(ImageFilter=skia.ImageFilters.DropShadowOnly(4, 10, 12, 12, skia.ColorSetARGB(int(140 * 0.55), 0, 0, 0)))
                canvas.saveLayer(None, sp)
                canvas.drawImageRect(im, r, skia.SamplingOptions(skia.FilterMode.kLinear))
                canvas.restore()
            canvas.drawImageRect(im, r, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(AntiAlias=True))
            canvas.restore()

    def icon(self, canvas, sh, ic, t, idx):
        t0, t1 = ic.get("t", sh["t"]), ic.get("end", sh["end"])
        if not (t0 - 1 / 30 <= t < t1 + 0.05):
            return
        kind = ic.get("kind", "emoji")
        s = self.pop_scale(t, t0, t1, sh, ic.get("pop", True), ic.get("pop_out", True)) * ic.get("scale", 100) / 100.0
        if s <= 0.001:
            return
        x, y = ic.get("x", self.W0 / 2), ic.get("y", self.H0 * 0.35)
        if ic.get("anim") == "float" or (kind != "badge" and ic.get("anim") != "none"):
            y += math.sin(t * 2.6 + idx) * ic.get("amp", 8)
        size = ic.get("size", 220)
        canvas.save()
        canvas.translate(x, y)
        if ic.get("anim") == "spin":
            canvas.rotate(math.sin(t * 5) * 8)
        canvas.scale(s, s)
        ink = skia.Color4f(0.12, 0.12, 0.12, 1)
        white = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 1))
        stroke = skia.Paint(AntiAlias=True, Color4f=ink, Style=skia.Paint.kStroke_Style, StrokeWidth=6)
        if kind in ("thought", "speech"):
            w, h = size * 1.5, size * 1.15
            path = skia.Path()
            if kind == "thought":
                for bx, by, bw, bh in [(0, 0, w, h), (-w * .32, -h * .18, w * .55, h * .6), (w * .3, -h * .2, w * .55, h * .62),
                                       (-w * .28, h * .22, w * .5, h * .5), (w * .3, h * .2, w * .5, h * .52), (0, -h * .34, w * .6, h * .5)]:
                    pth = skia.Path(); pth.addOval(skia.Rect.MakeXYWH(bx - bw / 2, by - bh / 2, bw, bh))
                    path = skia.Op(path, pth, skia.PathOp.kUnion_PathOp) if not path.isEmpty() else pth
                tail = ic.get("tail", [-0.5, 0.9])
                dots = skia.Path()
                dots.addOval(skia.Rect.MakeXYWH(tail[0] * w * .62 - size * .11, tail[1] * h * .62 - size * .09, size * .22, size * .18))
                dots.addOval(skia.Rect.MakeXYWH(tail[0] * w * .9 - size * .065, tail[1] * h * .98 - size * .055, size * .13, size * .11))
                for pth in (path, dots):
                    sh_p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(0, 0, 0, 0.35), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
                    canvas.save(); canvas.translate(4, 8); canvas.drawPath(pth, sh_p); canvas.restore()
                    canvas.drawPath(pth, stroke); canvas.drawPath(pth, white)
            else:
                tl = ic.get("tail", [-0.35, 0.6])
                path.addOval(skia.Rect.MakeXYWH(-w / 2, -h * .46, w, h * .92))
                tri = skia.Path(); tri.moveTo(tl[0] * w * .35 - 30, h * .3); tri.lineTo(tl[0] * w * .35 + 30, h * .3); tri.lineTo(tl[0] * w * .9, tl[1] * h * 1.2); tri.close()
                path = skia.Op(path, tri, skia.PathOp.kUnion_PathOp)
                canvas.drawPath(path, stroke); canvas.drawPath(path, white)
        if kind == "badge":
            ring = hexrgb(ic.get("ring", "#3D3638")); face = hexrgb(ic.get("face", "#6B5C61"))
            p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(0, 0, 0, 0.4), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
            canvas.drawCircle(4, 8, size * .625, p)
            canvas.drawCircle(0, 0, size * .625, skia.Paint(AntiAlias=True, Color4f=RIGM.skcolor(ring)))
            canvas.drawCircle(0, 0, size * .625, stroke)
            canvas.drawCircle(0, 0, size * .49, skia.Paint(AntiAlias=True, Color4f=RIGM.skcolor(face)))
            tp = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(.92, .88, .86, 1), Style=skia.Paint.kStroke_Style, StrokeWidth=5, StrokeCap=skia.Paint.kRound_Cap)
            for i in range(12):
                a = i / 12 * math.pi * 2
                canvas.drawLine(math.sin(a) * size * .53, -math.cos(a) * size * .53, math.sin(a) * size * .58, -math.cos(a) * size * .58, tp)
            hl = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, .18), Style=skia.Paint.kStroke_Style, StrokeWidth=size * .05)
            canvas.drawArc(skia.Rect.MakeXYWH(-size * .58, -size * .58, size * 1.16, size * 1.16), 200, 100, False, hl)
        im = self.img(ic.get("file")) if ic.get("file") else None
        if im is not None:
            isz = size * 0.72 if kind in ("thought", "speech") else (size * 0.7 if kind == "badge" else size)
            k2 = isz / max(im.width(), im.height())
            w2, h2 = im.width() * k2, im.height() * k2
            yo = -size * 0.04 if kind == "thought" else 0
            if kind == "emoji":
                sp = skia.Paint(ImageFilter=skia.ImageFilters.DropShadowOnly(3, 8, 9, 9, skia.ColorSetARGB(110, 0, 0, 0)))
                canvas.saveLayer(None, sp)
                canvas.drawImageRect(im, skia.Rect.MakeXYWH(-w2 / 2, -h2 / 2 + yo, w2, h2), skia.SamplingOptions(skia.FilterMode.kLinear))
                canvas.restore()
            canvas.drawImageRect(im, skia.Rect.MakeXYWH(-w2 / 2, -h2 / 2 + yo, w2, h2), skia.SamplingOptions(skia.FilterMode.kLinear))
        if ic.get("no"):
            r = size * 0.42
            np_ = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(.9, .12, .12, 1), Style=skia.Paint.kStroke_Style, StrokeWidth=size * .09, StrokeCap=skia.Paint.kRound_Cap)
            canvas.drawCircle(0, 0, r, np_)
            canvas.drawLine(-r * .7, -r * .7, r * .7, r * .7, np_)
        if ic.get("text"):
            ts = ic.get("text_size", size * 0.62)
            font = skia.Font(self.font, ts)
            txt = str(ic["text"])
            tw = font.measureText(txt)
            tp = ic.get("text_pos", [0, 0])
            blob = skia.TextBlob.MakeFromString(txt, font)
            bx, by = tp[0] - tw / 2, tp[1] + ts * 0.36
            canvas.drawTextBlob(blob, bx + 5, by + 5, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(0, 0, 0, .8)))
            canvas.drawTextBlob(blob, bx, by, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(.1, .05, .05, 1), Style=skia.Paint.kStroke_Style, StrokeWidth=max(4, size * .04) * 2, StrokeJoin=skia.Paint.kRound_Join))
            canvas.drawTextBlob(blob, bx, by, skia.Paint(AntiAlias=True, Color4f=RIGM.skcolor(hexrgb(ic.get("text_color", "#E8202A")))))
        canvas.restore()

    # ------------------------------------------------------------------ actors
    def actor(self, canvas, sh, ac, t, cam):
        cid = ac["cast"]
        cast = self.spec["cast"].get(cid)
        if cast is None:
            return
        vals, ctl = self.actor_state(cid, t)
        x, y = ac.get("x", self.W0 / 2), ac.get("y", self.H0 * 0.86)
        mv = ac.get("move") or []
        if mv:
            keys = set_keys_style([m["t"] for m in mv], [[m.get("x", x), m.get("y", y)] for m in mv], mv[-1].get("ease", "linear"))
            x, y = interp(keys, t)
        en, ex = ac.get("enter") or {}, ac.get("exit") or {}
        face = -1 if ac.get("face", 1) < 0 else 1
        for ft, fv in ac.get("flip", []):
            if t >= ft:
                face = -1 if fv < 0 else 1
        sc = ac.get("h", 900) / 1000.0
        popk = 1.0
        if en.get("from"):
            tIn, dIn = en.get("t", sh["t"]), en.get("dur", 0.35)
            if en["from"] == "pop":
                popk = interp(set_keys_style([tIn - 1 / 30, tIn + 0.1, tIn + 0.2, tIn + 0.3], [0, 1.16, 0.96, 1], 55), t)
            elif not mv:
                off = {"left": (-self.W0 * .45, 0), "right": (self.W0 * .45, 0), "bottom": (0, self.H0 * .5)}.get(en["from"], (0, -self.H0 * .6))
                k = interp(set_keys_style([tIn, tIn + dIn], [0, 1], "out"), t)
                x += off[0] * (1 - k); y += off[1] * (1 - k)
        if ex.get("to"):
            tOut, dOut = ex.get("t", sh["end"] - 0.3), ex.get("dur", 0.35)
            if ex["to"] == "pop":
                if t > tOut + dOut - 0.2:
                    popk *= interp(set_keys_style([tOut + dOut - 0.2, tOut + dOut - 0.1, tOut + dOut], [1, 1.1, 0], 50), t)
            else:
                off = {"left": (-self.W0 * .6, 0), "right": (self.W0 * .6, 0), "bottom": (0, self.H0 * .5)}.get(ex["to"], (0, -self.H0 * .7))
                k = interp(set_keys_style([tOut, tOut + dOut], [0, 1], "in"), t)
                x += off[0] * k; y += off[1] * k
        if popk <= 0.001:
            return
        z = cam[0]
        px = sc * z * self.k * popk
        state = ac.get("state", "color")
        for stt in ac.get("states", []):
            if stt.get("t", sh["t"]) <= t < stt.get("end", sh["end"]):
                state = stt["state"]
        ghost = state == "ghost"
        if ghost:
            state = "color"
        arr, (ox, oy) = RIGM.render_character(cast, vals, t, ctl, px, self.P, state)
        im = to_skimage(arr * (0.45 if ghost else 1.0))
        m = self.cam_matrix(cam)
        sx, sy = m.mapXY(x, y)
        # contact shadow
        if ac.get("shadow", True):
            sp = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(0, 0, 0, RIG["look"]["shadow_opacity"]),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1, 10 * px)))
            canvas.drawOval(skia.Rect.MakeXYWH(sx - 280 * px, sy - 6 * px - 35 * px, 560 * px, 70 * px), sp)
        canvas.save()
        canvas.translate(sx, sy)
        if cam[2]:
            canvas.rotate(cam[2])
        rot = float(ac.get("rot", 0)) + tilt_at(ac.get("tilt"), t)
        if rot:
            canvas.rotate(rot)
        canvas.scale(face, 1)
        canvas.drawImage(im, -ox, -oy)
        canvas.restore()

    # ------------------------------------------------------------------ fx
    def fx(self, canvas, sh, fx, t, idx, cam):
        kind = fx.get("kind")
        t0, t1 = fx.get("t", sh["t"]), fx.get("end", sh["end"])
        if not (t0 <= t < t1):
            return
        W0, H0 = self.W0, self.H0
        if kind in ("image_rain", "money_rain"):
            im = self.img(fx.get("file"))
            if im is None:
                return
            key = (sh["id"], idx)
            if key not in self.particles:
                r = np.random.default_rng(len(sh["id"]) * 101 + idx)
                n = fx.get("count", 36)
                area = fx.get("area", [-80, W0 + 80])
                self.particles[key] = [dict(w=r.uniform(fx.get("min_w", 90), fx.get("max_w", 170)), x=r.uniform(*area),
                                            sp=r.uniform(.7, 1.3) * fx.get("speed", 520), ph=r.uniform(0, 6.28),
                                            y0=r.uniform(-H0 * .9, H0 * .2), pile=(fx.get("pile") and i < n * .35),
                                            py=r.uniform(H0 * .82, H0 * .97), pr=r.uniform(-40, 40)) for i in range(n)]
            canvas.save()
            if not fx.get("screen"):
                canvas.concat(self.cam_matrix(cam))
            else:
                canvas.scale(self.k, self.k)
            tt = t - t0
            for p in self.particles[key]:
                if p["pile"]:
                    self.draw_image_centered(canvas, im, p["x"], p["py"], p["w"], p["pr"], shadow=False)
                    continue
                y = p["y0"] + tt * p["sp"]
                y = ((y + 300) % (H0 + 600)) - 300   # python modulo is always positive (matches the AE expression)
                x = p["x"] + math.sin(tt * 1.7 + p["ph"]) * 60
                rot = math.sin(tt * 2.3 + p["ph"]) * 35
                kx = 0.35 + 0.65 * abs(math.cos(tt * 3.1 + p["ph"]))
                canvas.save(); canvas.translate(x, y); canvas.rotate(rot); canvas.scale(kx, 1)
                h = p["w"] * im.height() / im.width()
                canvas.drawImageRect(im, skia.Rect.MakeXYWH(-p["w"] / 2, -h / 2, p["w"], h), skia.SamplingOptions(skia.FilterMode.kLinear))
                canvas.restore()
            canvas.restore()
        elif kind in ("embers", "dust", "snow"):
            key = (sh["id"], idx)
            if key not in self.particles:
                r = np.random.default_rng(len(sh["id"]) * 11 + idx)
                n = fx.get("count", 60 if kind == "snow" else 36)
                self.particles[key] = [dict(d=r.uniform(fx.get("min_size", 4), fx.get("max_size", 10)), x=r.uniform(0, W0), y=r.uniform(0, H0),
                                            vy=(r.uniform(60, 140) if kind == "snow" else -r.uniform(80, 220)), ph=r.uniform(0, 6.28)) for _ in range(n)]
            col = hexrgb(fx.get("color", "#FF8C26" if kind == "embers" else "#FFFFFF"))
            canvas.save(); canvas.scale(self.k, self.k)
            for p in self.particles[key]:
                y = (p["y"] + t * p["vy"]) % H0
                x = p["x"] + math.sin(t * 1.3 + p["ph"]) * 40
                a = 0.5 + 0.5 * math.sin(t * 4 + p["ph"])
                paint = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(col[0], col[1], col[2], a))
                if kind == "embers":
                    g = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(col[0], col[1], col[2], a * .5), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7))
                    canvas.drawOval(skia.Rect.MakeXYWH(x - p["d"], y - p["d"] * 1.2, p["d"] * 2, p["d"] * 2.4), g)
                canvas.drawOval(skia.Rect.MakeXYWH(x - p["d"] / 2, y - p["d"] * .8, p["d"], p["d"] * (1.6 if kind == "embers" else 1)), paint)
            canvas.restore()
        elif kind == "rain":
            r = np.random.default_rng(int(t * 30))
            paint = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(.8, .85, .9, fx.get("opacity", 40) / 100 * .6), StrokeWidth=2 * self.k)
            for _ in range(int(fx.get("count", 3000) / 30)):
                x, y = r.uniform(0, self.W), r.uniform(0, self.H)
                canvas.drawLine(x, y, x - 6 * self.k, y + 40 * self.k, paint)
        elif kind == "smoke":
            if (sh["id"], idx) not in self.particles:
                base = np.random.default_rng(idx).random((24, 14)).astype(np.float32)
                img = Image.fromarray((base * 255).astype(np.uint8), "L").resize((self.W, self.H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30 * self.k))
                self.particles[(sh["id"], idx)] = img
            a = np.asarray(self.particles[(sh["id"], idx)]).astype(np.float32) / 255.0
            col = hexrgb(fx.get("color", "#8C8C8C"))
            op = fx.get("opacity", 45) / 100 * min(1, (t - t0) / 0.3)
            sh_y = int((t * 40 * self.k) % self.H)
            a = np.roll(a, -sh_y, 0)
            rgba = np.zeros((self.H, self.W, 4), np.float32)
            rgba[..., 3] = np.clip(a * 1.6 - 0.4, 0, 1) * op
            rgba[..., :3] = np.array(col) * rgba[..., 3:4]
            paint = skia.Paint(); paint.setBlendMode(skia.BlendMode.kMultiply if fx.get("dark") else skia.BlendMode.kScreen)
            canvas.drawImage(to_skimage(rgba), 0, 0, skia.SamplingOptions(), paint)
        elif kind == "tint":
            op = fx.get("opacity", 55) / 100.0
            fi = fx.get("fade", 0.25)
            k = min(1, (t - t0) / fi, (t1 - t) / fi)
            col = hexrgb(fx.get("color", "#33B333"))
            paint = skia.Paint(Color4f=skia.Color4f(col[0], col[1], col[2], op * k))
            paint.setBlendMode({"multiply": skia.BlendMode.kMultiply, "color": skia.BlendMode.kColor}.get(fx.get("blend"), skia.BlendMode.kOverlay))
            canvas.drawRect(skia.Rect.MakeWH(self.W, self.H), paint)
        elif kind == "flash":
            k = interp(set_keys_style([t0, t0 + .04, t0 + .3], [0, fx.get("opacity", 85) / 100, 0], "linear"), t)
            col = hexrgb(fx.get("color", "#FFF2D9"))
            paint = skia.Paint(Color4f=skia.Color4f(col[0], col[1], col[2], k)); paint.setBlendMode(skia.BlendMode.kPlus)
            canvas.drawRect(skia.Rect.MakeWH(self.W, self.H), paint)
        elif kind in ("video", "fire", "overlay"):
            p = self.path(fx.get("file"))
            if not p or not os.path.exists(p):
                return
            if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                im = self.img(fx["file"])
            else:
                vr = self.videos.get(("fx", p))
                if vr is None:
                    vr = self.videos[("fx", p)] = VideoReader(p, int(self.W), int(self.H), self.fps)
                im = vr.get(fx.get("start", 0) + t - t0)
            if im is None:
                return
            paint = skia.Paint()
            paint.setBlendMode({"normal": skia.BlendMode.kSrcOver, "add": skia.BlendMode.kPlus}.get(fx.get("blend"), skia.BlendMode.kScreen))
            paint.setAlphaf(fx.get("opacity", 100) / 100)
            if fx.get("w"):
                canvas.save(); canvas.concat(self.cam_matrix(cam))
                w = fx["w"]; h = w * im.height() / im.width()
                canvas.drawImageRect(im, skia.Rect.MakeXYWH(fx.get("x", self.W0 / 2) - w / 2, fx.get("y", self.H0 / 2) - h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), paint)
                canvas.restore()
            else:
                canvas.drawImageRect(im, skia.Rect.MakeWH(self.W, self.H), skia.SamplingOptions(skia.FilterMode.kLinear), paint)

    # ------------------------------------------------------------------ shot + frame
    def shot_frame(self, sh, t):
        surf = skia.Surface(self.W, self.H)
        c = surf.getCanvas()
        c.clear(skia.ColorBLACK)
        cam = self.camera(sh, t)
        self.background(c, sh, t, cam)
        props = sh.get("props", [])
        for i, p in enumerate(props):
            if p.get("z") == "back":
                c.save(); c.concat(self.cam_matrix(cam)) if not p.get("screen") else c.scale(self.k, self.k); self.prop(c, sh, p, t, i); c.restore()
        for cr in sh.get("creatures", []):
            if cr.get("z", "back") == "back":
                c.save(); c.concat(self.cam_matrix(cam)); self.creature(c, sh, cr, t); c.restore()
        acts = sorted(enumerate(sh.get("actors", [])), key=lambda x: (x[1].get("z", 0), x[1].get("y", 0)))
        for i, ac in acts:
            self.actor(c, sh, ac, t, cam)
        for cr in sh.get("creatures", []):
            if cr.get("z", "back") != "back":
                c.save(); c.concat(self.cam_matrix(cam)); self.creature(c, sh, cr, t); c.restore()
        for i, p in enumerate(props):
            if p.get("z") != "back":
                c.save(); c.concat(self.cam_matrix(cam)) if not p.get("screen") else c.scale(self.k, self.k); self.prop(c, sh, p, t, i); c.restore()
        for i, ic in enumerate(sh.get("icons", [])):
            c.save(); c.concat(self.cam_matrix(cam)) if not ic.get("screen") else c.scale(self.k, self.k); self.icon(c, sh, ic, t, i); c.restore()
        for i, fx in enumerate(sh.get("fx", [])):
            if fx.get("kind") != "glitch":
                self.fx(c, sh, fx, t, i, cam)
        arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).astype(np.float32) / 255.0
        # shot-level states (bw/dark/tint)
        for s in sh.get("state", []):
            t0, t1, fd = s.get("t", sh["t"]), s.get("end", sh["end"] + 1), s.get("fade", 0.25)
            if t0 <= t < t1:
                k = min(1, (t - t0) / max(1e-3, fd))
                rgb = arr[..., :3]
                if s.get("kind") in ("bw", "gray"):
                    lum = (rgb * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
                    g = np.clip((lum + s.get("bright", -10) / 255 - 0.5) * 1.12 + 0.5, 0, 1)
                    arr[..., :3] = rgb + (g - rgb) * k
                elif s.get("kind") == "dark":
                    arr[..., :3] = np.clip(rgb + s.get("bright", -45) / 255 * k, 0, 1)
                else:
                    lum = (rgb * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
                    col = np.array(hexrgb(s.get("color", "#FF4D4D")), np.float32)
                    arr[..., :3] = rgb + (lum * col - rgb) * k * s.get("amount", 60) / 100
        for i, fx in enumerate(sh.get("fx", [])):
            if fx.get("kind") == "glitch" and fx.get("t", sh["t"]) <= t < fx.get("t", sh["t"]) + 0.28:
                arr = self.mosaic(arr, t)
        return arr

    def mosaic(self, arr, t):
        r = np.random.default_rng(int(t * 30))
        bw, bh = int(r.uniform(8, 60)), int(r.uniform(14, 90))
        h, w = arr.shape[:2]
        sx, sy = max(1, w // bw), max(1, h // bh)
        yi = np.minimum((np.arange(h) // sy) * sy + sy // 2, h - 1)
        xi = np.minimum((np.arange(w) // sx) * sx + sx // 2, w - 1)
        return arr[yi][:, xi]

    def frame(self, t):
        shots = self.spec["shots"]
        idx = 0
        for i, s in enumerate(shots):
            if s["t"] <= t < s["end"] or (i == len(shots) - 1 and t >= s["t"]):
                idx = i
                break
        sh = shots[idx]
        arr = self.shot_frame(sh, t)
        # transitions around the cut INTO the next shot and from the previous
        nxt = shots[idx + 1] if idx + 1 < len(shots) else None
        if nxt:
            tr = nxt.get("transition", "cut").rstrip("?")
            b = nxt["t"]
            if tr == "bw_fade" and b - 0.3 <= t < b:
                k = (t - (b - 0.3)) / 0.3
                lum = (arr[..., :3] * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
                arr[..., :3] = arr[..., :3] + (lum - arr[..., :3]) * k
            if tr == "glitch" and b - 0.02 <= t < b:
                arr = self.mosaic(arr, t)
        cur_tr = sh.get("transition", "cut").rstrip("?")
        b = sh["t"]
        if idx > 0:
            if cur_tr == "flash" and t < b + 5 / 30:
                k = 1 - (t - b) / (5 / 30)
                arr[..., :3] = arr[..., :3] + (1 - arr[..., :3]) * max(0, k)
            if cur_tr == "glitch" and t < b + 0.2:
                arr = self.mosaic(arr, t) if (int(t * 30) % 2 == 0) else arr
            if cur_tr in ("light_leak", "red_wipe", "whip", "zoom_blur") and t < b + 0.35:
                arr = self.leak(arr, t - b, cur_tr)
        if nxt and nxt.get("transition", "cut").rstrip("?") in ("light_leak", "red_wipe", "flash") and nxt["t"] - 0.18 <= t < nxt["t"]:
            if nxt.get("transition").rstrip("?") == "flash":
                k = (t - (nxt["t"] - 2 / 30)) / (2 / 30)
                if k > 0:
                    arr[..., :3] = arr[..., :3] + (1 - arr[..., :3]) * k
            else:
                arr = self.leak(arr, t - nxt["t"], nxt["transition"].rstrip("?"))
        return arr

    def leak(self, arr, dt, kind):
        h, w = arr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        if kind == "light_leak":
            u = (dt + 0.18) / 0.5
            cx = -0.6 * w + u * 2.2 * w
            cy = 0.2 * h + u * 0.5 * h
            d = ((xx - cx) / (0.7 * w)) ** 2 + ((yy - cy) / (0.45 * h)) ** 2
            a = np.exp(-d * 1.5)[..., None] * (1 - abs(dt - 0.02) / 0.34)
            col = np.array([1.0, 0.62, 0.12])
            arr[..., :3] = np.clip(arr[..., :3] + a * col + a * 0.6, 0, 1)
        elif kind == "red_wipe":
            u = (dt + 0.12) / 0.48
            cx = 1.3 * w - u * 1.6 * w
            a = np.exp(-((xx - cx) / (0.18 * w)) ** 2)[..., None] * 0.8
            col = np.array([0.95, 0.18, 0.16])
            arr[..., :3] = 1 - (1 - arr[..., :3]) * (1 - a * col)
        elif kind in ("whip", "zoom_blur"):
            k = max(0, 1 - abs(dt) / 0.14)
            if k > 0:
                s = int(30 * k * self.k) + 1
                arr[..., :3] = sum(np.roll(arr[..., :3], j, 1) for j in range(0, s * 4, 4)) / len(range(0, s * 4, 4))
        return arr

    # ------------------------------------------------------------------ main-level look and captions
    def look(self, arr, t):
        L = self.spec.get("look", {})
        h, w = arr.shape[:2]
        vg = L.get("vignette", STYLE["look"]["vignette"])
        if vg > 0:
            if not hasattr(self, "_vig"):
                yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
                d = np.sqrt(((xx - w / 2) / (w * 0.575)) ** 2 + ((yy - h / 2) / (h * 0.525)) ** 2)
                self._vig = np.clip((d - 0.55) / 0.75, 0, 1) ** 1.4
            arr[..., :3] *= (1 - self._vig[..., None] * vg)
        gr = L.get("grain", STYLE["look"]["grain"])
        if gr > 0:
            if not hasattr(self, "_grain"):
                self._grain = [self.rng.standard_normal((h, w, 1)).astype(np.float32) * gr * 0.5 for _ in range(4)]
            arr[..., :3] += self._grain[int(t * 30) % 4]
        if L.get("end") == "fade_black" and t > self.dur - 0.7:
            arr[..., :3] *= max(0, (self.dur - 0.05 - t) / 0.65)
        return np.clip(arr, 0, 1)

    def caption(self, canvas, t):
        caps = self.spec.get("captions", [])
        C = STYLE["captions"]
        cur = None
        for c in caps:
            if c["t"] <= t:
                cur = c
            else:
                break
        if not cur or t > cur.get("end", cur["t"] + 0.4) + 0.08:
            nxt_ok = cur and any(c["t"] > cur["t"] and c["t"] - cur.get("end", 0) <= C["gap_blank"] for c in caps)
            if not cur or not nxt_ok or t > cur.get("end", 0) + C["gap_blank"]:
                return
        d = t - cur["t"]
        pop = 1 + C["pop"] / 100 * math.exp(-d * C["pop_decay"]) * math.cos(d * C["pop_freq"])
        size = C["size"] * cur.get("scale", 1.0) * self.k
        font = skia.Font(self.font, size)
        txt = cur["text"]
        tw = font.measureText(txt)
        col = hexrgb(C["red"] if cur.get("color") == "red" else C["yellow"])
        x0, y0 = self.W / 2, self.H * C["y"]
        canvas.save()
        canvas.translate(x0, y0)
        canvas.scale(pop, pop)
        blob = skia.TextBlob.MakeFromString(txt, font)
        bx, by = -tw / 2, size * 0.36
        glow = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(col[0], col[1], col[2], 0.55),
                          MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, C["glow_radius"] * self.k * 0.45))
        canvas.drawTextBlob(blob, bx, by, glow)
        sd = C["shadow_distance"] * self.k
        shc = hexrgb(C["shadow"])
        for j in range(1, 4):
            canvas.drawTextBlob(blob, bx + sd * j / 3 * 0.57, by + sd * j / 3 * 0.82,
                                skia.Paint(AntiAlias=True, Color4f=skia.Color4f(shc[0], shc[1], shc[2], 1),
                                           Style=skia.Paint.kStrokeAndFill_Style, StrokeWidth=C["stroke_width"] * self.k * 2))
        canvas.drawTextBlob(blob, bx, by, skia.Paint(AntiAlias=True, Color4f=RIGM.skcolor(hexrgb(C["stroke"])),
                                                     Style=skia.Paint.kStroke_Style, StrokeWidth=C["stroke_width"] * self.k * 2, StrokeJoin=skia.Paint.kRound_Join))
        canvas.drawTextBlob(blob, bx, by, skia.Paint(AntiAlias=True, Color4f=RIGM.skcolor(col)))
        canvas.restore()

    def render_frame(self, t):
        arr = self.frame(t)
        arr = self.look(arr, t)
        im = to_skimage(np.concatenate([arr[..., :3], np.ones_like(arr[..., :1])], -1))
        surf = skia.Surface(self.W, self.H)
        c = surf.getCanvas()
        c.drawImage(im, 0, 0)
        self.caption(c, t)
        return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3]


def timeline_evaluator(spec):
    """Pose/face state of every character at any time, without rendering (compile_spec uses it to bake attachments)."""
    r = Renderer.__new__(Renderer)
    r.spec = spec
    r.timelines = r._timelines()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec.json")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scale", type=float)
    ap.add_argument("--fps", type=float)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--stills", default="")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    P = a.project
    spec = json.load(open(os.path.join(P, a.spec), encoding="utf-8"))
    if "_compiled" not in spec:
        from compile_spec import compile_spec
        spec = compile_spec(spec, P)
    scale = a.scale or (1.0 if a.full else 0.5)
    fps = a.fps or (30 if a.full else 15)
    R = Renderer(P, spec, scale, fps)
    os.makedirs(os.path.join(P, "qc"), exist_ok=True)
    if a.stills:
        d = os.path.join(P, "qc", "stills")
        os.makedirs(d, exist_ok=True)
        for s in a.stills.split(","):
            t = float(s)
            Image.fromarray(R.render_frame(t)).save(os.path.join(d, f"preview_{int(t * 1000):06d}.png"))
        print("stills ->", d)
        return
    if a.sheet:
        ts = np.arange(0.25, R.dur, 0.5)
        tiles = [Image.fromarray(R.render_frame(float(t))).resize((180, 320)) for t in ts]
        cols = 10
        rows = int(math.ceil(len(tiles) / cols))
        sheet = Image.new("RGB", (cols * 180, rows * 320), (0, 0, 0))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for i, (tile, t) in enumerate(zip(tiles, ts)):
            sheet.paste(tile, ((i % cols) * 180, (i // cols) * 320))
            dr.text(((i % cols) * 180 + 4, (i // cols) * 320 + 3), f"{t:.2f}", fill=(255, 255, 0))
        out = os.path.join(P, "qc", "preview_sheet.jpg")
        sheet.save(out, quality=85)
        print("sheet ->", out)
        return
    t1 = a.t1 if a.t1 is not None else R.dur
    out = a.out or os.path.join(P, "exports", "preview_full.mp4" if a.full else "preview.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    au = None
    if not a.no_audio:
        # the animatic must be heard with its sound design: (re)mix voice + SFX (+ music once chosen) when the mix is
        # missing or older than the plan - a voice-only animatic hides missing sounds
        mixp, cp = os.path.join(P, "audio", "mix.wav"), os.path.join(P, "plan", "spec_compiled.json")
        if os.path.exists(os.path.join(P, spec.get("audio", {}).get("voice", "") or "-")) and (
                not os.path.exists(mixp) or (os.path.exists(cp) and os.path.getmtime(mixp) < os.path.getmtime(cp))):
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mix.py"), P],
                               capture_output=True, text=True)
            print("mix ->", mixp if r.returncode == 0 else "failed: " + r.stderr[-300:])
        for cand in ("audio/mix.wav", spec.get("audio", {}).get("voice", "")):
            if cand and os.path.exists(os.path.join(P, cand)):
                au = os.path.join(P, cand)
                break
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(fps), "-i", "-"]
    if au:
        cmd += ["-ss", f"{a.t0:.3f}", "-i", au, "-map", "0:v", "-map", "1:a", "-shortest", "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-c:v", "libx264", "-preset", "medium" if a.full else "veryfast", "-crf", "17" if a.full else "23", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int((t1 - a.t0) * fps)
    for i in range(n):
        t = a.t0 + i / fps
        p.stdin.write(np.ascontiguousarray(R.render_frame(t)).tobytes())
        if i % int(fps * 5) == 0:
            print(f"  {t:6.2f}s / {t1:.2f}s", flush=True)
    p.stdin.close()
    code = p.wait()
    if code:
        raise SystemExit(code)
    print("video ->", out)


if __name__ == "__main__":
    main()
