"""2D Stick Animator - stick-figure rig (Python side).

Shared maths with the After Effects engine (ra_engine.jsx): same rig.json, poses.json,
parts.json and faces.json, same angle conventions, same procedural walk/run/idle/talk/blink.
Used by ra_preview.py (animatic + fallback renderer) and by pose_sheet.py.
"""
import json
import math
import os

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_skia import skia  # noqa: E402
from PIL import Image, ImageFilter

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def _load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


RIG = _load("rig.json")
POSES = _load("poses.json")
PARTS = _load("parts.json")
FACES = _load("faces.json")
LIMBS = ["aF", "aN", "lF", "lN"]
D2R = math.pi / 180.0


def hex2rgb(h, default=(1, 1, 1)):
    if h is None:
        return default
    if isinstance(h, (list, tuple)):
        return tuple(float(x) for x in h[:3])
    h = str(h).lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    except ValueError:
        return default


def shade(rgb, k):
    return tuple(max(0.0, min(1.0, c * k)) for c in rgb)


def skcolor(rgb, a=1.0):
    return skia.Color4f(rgb[0], rgb[1], rgb[2], a)


def dirv(a):
    a *= D2R
    return (math.sin(a), math.cos(a))


def up(lean):
    a = lean * D2R
    return (math.sin(a), -math.cos(a))


# ----------------------------------------------------------------------------- pose state
def pose_params(name, overrides=None):
    base = dict(POSES["stand"])
    p = POSES.get(name)
    if p is None:
        p = POSES["stand"]
    for k, v in p.items():
        base[k] = v
    if overrides:
        for k, v in overrides.items():
            if k in base or k in ("lean", "head", "hip"):
                base[k] = v
    out = {"lean": float(base["lean"]), "head": float(base.get("head", 0)),
           "hipX": float(base["hip"][0]), "hipY": float(base["hip"][1]),
           "turn": float(p.get("turn", 0)),     # never inherited from stand
           "fFront": float(p.get("fFront", 0))}  # far arm drawn in front of the body (never inherited)
    if overrides and "turn" in overrides:
        out["turn"] = float(overrides["turn"])
    if overrides and "fFront" in overrides:
        out["fFront"] = float(overrides["fFront"])
    for L in LIMBS:
        out[L + "u"] = float(base[L][0])
        out[L + "l"] = float(base[L][1])
    return out


def blend(a, b, k):
    return {key: a[key] + (b[key] - a[key]) * k for key in a}


def ease_inout(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def solve(params, t=0.0, walk=0.0, run=0.0, speed=1.6, idle=1.0, phase=0.0, tw=None, arms=1.0, sw=None, sd=None):
    """Joint positions in rig units for one frame (same maths as the AE expressions).
    sw = half distance between the shoulders (cast_shoulder: the garment's shoulder edge), default spread x torso."""
    P = RIG
    pr = P["procedural"]
    ph = 2 * math.pi * speed * t + phase * D2R
    w, r = walk, run
    W, R = pr["walk"], pr["run"]
    s = math.sin(ph)
    c = math.cos(ph)
    sb = math.sin(ph + math.pi)
    cb = math.cos(ph + math.pi)
    idl = idle * math.sin(2 * math.pi * pr["idle"]["freq"] * t + phase * D2R)
    bob = -(w * W["bob"] + r * R["bob"]) * abs(c) + w * W["bob"] * 0.5 + r * R["bob"] * 0.5
    bob += idle * pr["idle"]["breath"] * math.sin(2 * math.pi * 0.35 * t + phase * D2R)
    lean = params["lean"] + w * W["lean"] + r * R["lean"]
    hip = (P["hip"][0] + params["hipX"], P["hip"][1] + params["hipY"] + bob)
    u = up(lean)
    neck = (hip[0] + u[0] * P["torso_len"], hip[1] + u[1] * P["torso_len"])
    sdv = P["shoulder_down"] if sd is None else sd
    sh = (neck[0] - u[0] * sdv, neck[1] - u[1] * sdv)
    head_rot = lean + params["head"]
    hu = up(lean + params["head"] * 0.35)
    headc = (neck[0] + hu[0] * P["head_lift"], neck[1] + hu[1] * P["head_lift"])

    ang = {}
    # legs: near swings with sin, far with the opposite phase
    ang["lNu"] = params["lNu"] + w * W["leg_amp"] * s + r * R["leg_amp"] * s
    ang["lFu"] = params["lFu"] + w * W["leg_amp"] * sb + r * R["leg_amp"] * sb
    ang["lNl"] = params["lNl"] - w * (W["knee"][0] + W["knee"][1] * max(0.0, c)) - r * (R["knee"][0] + R["knee"][1] * max(0.0, c))
    ang["lFl"] = params["lFl"] - w * (W["knee"][0] + W["knee"][1] * max(0.0, cb)) - r * (R["knee"][0] + R["knee"][1] * max(0.0, cb))
    # arms swing against the legs
    # (arms = 0 while the hands hold something heavy or someone: no walking arm swing)
    ang["aNu"] = params["aNu"] - arms * (w * W["arm_amp"] * s + r * R["arm_amp"] * s) + pr["idle"]["arm_amp"] * idl
    ang["aFu"] = params["aFu"] - arms * (w * W["arm_amp"] * sb + r * R["arm_amp"] * sb) - pr["idle"]["arm_amp"] * idl
    ang["aNl"] = params["aNl"] + arms * (w * W["elbow"] * max(0.0, s) + r * R["elbow"] * 0.2 * max(0.0, s))
    ang["aFl"] = params["aFl"] + arms * (w * W["elbow"] * max(0.0, sb) + r * R["elbow"] * 0.2 * max(0.0, sb))

    limbs = {}
    perp = (math.cos(lean * D2R), math.sin(lean * D2R))
    spread = P.get("hip_spread", 0.22) * P["torso_w"]
    base = sw if sw is not None else P.get("shoulder_spread", 0.36) * (tw if tw is not None else P["torso_w"])
    ks = P.get("shoulder_side", 1.0)
    sw = base * (ks + (1.0 - ks) * params.get("turn", 0.0))
    for L in LIMBS:
        if L[0] == "a":
            sg = 1.0 if L == "aN" else -1.0
            root = (sh[0] + perp[0] * sw * sg, sh[1] + perp[1] * sw * sg)
        else:
            sgn = 1.0 if L == "lN" else -1.0
            root = (hip[0] + perp[0] * spread * sgn, hip[1] + perp[1] * spread * sgn)
        lu = P["arm_u"] if L[0] == "a" else P["leg_u"]
        ll = P["arm_l"] if L[0] == "a" else P["leg_l"]
        au = ang[L + "u"]
        al = au + ang[L + "l"]
        d1 = dirv(au)
        p1 = (root[0] + lu * d1[0], root[1] + lu * d1[1])
        d2 = dirv(al)
        p2 = (p1[0] + ll * d2[0], p1[1] + ll * d2[1])
        limbs[L] = (root, p1, p2, al)
    return {"hip": hip, "neck": neck, "shoulder": sh, "head": headc, "head_rot": head_rot,
            "lean": lean, "limbs": limbs, "far_front": params.get("fFront", 0.0) >= 0.5, "turn": params.get("turn", 0.0)}


_SHOULDER_CACHE = {}


def garment_shoulder(acc, root=""):
    """half width (rig units) of a torso garment at its shoulder line, measured from the picture's alpha: the
    widest extent in the band 5-18 % below the garment's top edge (below the collar, above the chest)"""
    path = os.path.join(root, acc["file"]) if root and not os.path.isabs(acc["file"]) else acc["file"]
    key = (path, acc.get("w"))
    if key in _SHOULDER_CACHE:
        return _SHOULDER_CACHE[key]
    val = None
    try:
        from PIL import Image as _Im
        import numpy as _np
        a = _np.asarray(_Im.open(path).convert("RGBA"))[..., 3] > 60
        rows = _np.nonzero(a.any(1))[0]
        if len(rows) > 10:
            top, bot = rows[0], rows[-1]
            hgt = bot - top
            halves = []
            for y in range(int(top + 0.05 * hgt), int(top + 0.18 * hgt) + 1):
                xs = _np.nonzero(a[y])[0]
                if len(xs):
                    halves.append((xs[-1] - xs[0]) / 2.0)
            if halves:
                px = float(_np.percentile(halves, 70))
                val = px / a.shape[1] * float(acc.get("w", 1.1)) * RIG["torso_len"]
    except Exception:
        val = None
    _SHOULDER_CACHE[key] = val
    return val


def garment_top(acc, root, x_rig):
    """top edge of a torso garment (rig units relative to the hip, along the torso; negative = up) at x_rig"""
    path = os.path.join(root, acc["file"]) if root and not os.path.isabs(acc["file"]) else acc["file"]
    key = ("top", path, acc.get("w"), acc.get("dx"), acc.get("dy"), round(x_rig, 1))
    if key in _SHOULDER_CACHE:
        return _SHOULDER_CACHE[key]
    val = None
    try:
        from PIL import Image as _Im
        import numpy as _np
        a = _np.asarray(_Im.open(path).convert("RGBA"))[..., 3] > 60
        H, W = a.shape
        TL = RIG["torso_len"]
        sc = float(acc.get("w", 1.1)) * TL / W
        # the shoulder slope under the arm: the top edge in each column across the arm's width (outer side), and the
        # lower 70 % of them, so thin straps, collars and hoods near the neck do not count as shoulders
        aw = RIG.get("arm_w", RIG["limb_w"])
        tops = []
        for xr in _np.linspace(x_rig - 0.1 * aw, x_rig + 0.45 * aw, 9):
            xi = int(round(W / 2 + (xr - float(acc.get("dx", 0.0)) * TL) / sc))
            if 0 <= xi < W:
                rows = _np.nonzero(a[:, xi])[0]
                if len(rows):
                    tops.append(rows[0])
        if tops:
            val = float(acc.get("dy", -0.45)) * TL + (float(_np.percentile(tops, 70)) - H / 2.0) * sc
    except Exception:
        val = None
    _SHOULDER_CACHE[key] = val
    return val


def cast_arms(cast, root=""):
    """(half distance between the arm roots, shoulder_down) for this cast: the arms come out at the outer top corners
    of the body - just under a torso garment's shoulder line, or at the top corners of a bare torso"""
    if cast.get("shoulder") and cast.get("shoulder_dn") is not None:
        return float(cast["shoulder"]), float(cast["shoulder_dn"])
    P = RIG
    tw = P["torso_w"] * float(cast.get("build", 1.0))
    aw = P.get("arm_w", P["limb_w"]) * float(cast.get("limb", 1.0))
    half = cast_shoulder(cast, root)
    r = tw / 2.0
    sd = -math.sqrt(max(0.0, r * r - min(half, r * 0.98) ** 2)) + aw / 2 + 4      # bare torso: its rounded top corner
    bare_half = P.get("shoulder_spread", 0.36) * tw
    for acc in cast.get("accessories", []):
        if half > bare_half + 1 and acc.get("slot") == "torso" and not acc.get("behind") and acc.get("file") and not acc.get("from"):
            # only garments that are wider than the body's own shoulders (jackets, coats, uniforms) set the shoulder line;
            # aprons, dresses and straps leave the arms at the body's top corners
            top = garment_top(acc, root, half)
            if top is not None:
                sd = min(sd, top + aw / 2 + 6 + P["torso_len"])                  # just under the garment's shoulder
    # never above the top of the body: the arm's top edge stays at or under the torso's top line
    return half, round(max(-(tw / 2.0) + aw / 2.0, min(0.0, sd)), 2)


def cast_shoulder(cast, root=""):
    """half distance between the arm roots for this cast: the precomputed cast["shoulder"] (compile_spec), else the
    torso garment's shoulder edge minus 0.42 arm widths, never narrower than the bare body's shoulders"""
    if cast.get("shoulder"):
        return float(cast["shoulder"])
    P = RIG
    tw = P["torso_w"] * float(cast.get("build", 1.0))
    bare = P.get("shoulder_spread", 0.36) * tw
    aw = P.get("arm_w", P["limb_w"]) * float(cast.get("limb", 1.0))
    best = bare
    for acc in cast.get("accessories", []):
        if acc.get("slot") == "torso" and not acc.get("behind") and acc.get("file"):
            g = garment_shoulder(acc, root)
            if g:
                best = max(best, g - 0.42 * aw)
    return round(min(best, 0.95 * tw), 2)


def far_arm_front(J, ff=0.0):
    """the far arm is drawn in front of the body when the pose asks (fFront) or when it stays on its own side (elbow
    and hand not crossing the body's centre line) - so both shoulders look the same; an arm reaching across the body
    goes behind it (same rule in the AE engine)"""
    if ff >= 0.5:
        return True
    _, p1, p2, _ = J["limbs"]["aF"]
    sh = J["shoulder"]
    a = J["lean"] * D2R
    px, py = math.cos(a), math.sin(a)
    e = (p1[0] - sh[0]) * px + (p1[1] - sh[1]) * py
    h = (p2[0] - sh[0]) * px + (p2[1] - sh[1]) * py
    return e < -8 and h < 10


def limb_path(p0, p1, p2):
    k = RIG["joint_tangent"]
    tx, ty = (p2[0] - p0[0]) * k * 0.5, (p2[1] - p0[1]) * k * 0.5
    path = skia.Path()
    path.moveTo(*p0)
    # cubic from p0 to p1 with tangent at p1 = -(tx,ty); then p1 to p2
    path.cubicTo(p0[0], p0[1], p1[0] - tx, p1[1] - ty, p1[0], p1[1])
    path.cubicTo(p1[0] + tx, p1[1] + ty, p2[0], p2[1], p2[0], p2[1])
    return path


# ----------------------------------------------------------------------------- element drawing
def _resolve(col, cast, body):
    if col is None:
        return None
    if col == "BODY":
        return body
    if col == "INK":
        return hex2rgb(FACES["ink"])
    if col == "C1":
        return hex2rgb(cast.get("c1", "#3A2A20"))
    if col == "C2":
        return hex2rgb(cast.get("c2", "#2A2A2A"))
    return hex2rgb(col)


def smooth_path(pts, closed):
    path = skia.Path()
    n = len(pts)
    if n < 3:
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        if closed:
            path.close()
        return path
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        path.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        path.close()
    return path


def draw_elements(canvas, els, scale, cast, body, only_layer=None):
    """els in local units * scale; canvas already translated/rotated to the element origin."""
    for e in els:
        lay = e.get("layer", "front")
        if only_layer is not None and lay != only_layer:
            continue
        fill = _resolve(e.get("fill"), cast, body)
        stroke = _resolve(e.get("stroke"), cast, body)
        sw = e.get("sw", 0) * scale
        t = e["t"]
        if t == "ellipse":
            cx, cy = e["c"][0] * scale, e["c"][1] * scale
            w, h = e["s"][0] * scale, e["s"][1] * scale
            path = skia.Path()
            path.addOval(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h))
        elif t == "rect":
            cx, cy = e["c"][0] * scale, e["c"][1] * scale
            w, h = e["s"][0] * scale, e["s"][1] * scale
            r = e.get("r", 0) * scale
            path = skia.Path()
            path.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), r, r))
        elif t == "line":
            pts = [(p[0] * scale, p[1] * scale) for p in e["pts"]]
            path = skia.Path()
            path.moveTo(*pts[0])
            for p in pts[1:]:
                path.lineTo(*p)
            fill = None
            if stroke is None:
                stroke = fill or (0, 0, 0)
        else:
            pts = [(p[0] * scale, p[1] * scale) for p in e["pts"]]
            closed = not e.get("open", False)
            path = smooth_path(pts, closed) if e.get("smooth") else _poly(pts, closed)
        if fill is not None and t != "line":
            paint = skia.Paint(AntiAlias=True, Color4f=skcolor(fill))
            canvas.drawPath(path, paint)
        if stroke is not None and sw > 0:
            paint = skia.Paint(AntiAlias=True, Color4f=skcolor(stroke), Style=skia.Paint.kStroke_Style,
                               StrokeWidth=sw, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
            canvas.drawPath(path, paint)


def _poly(pts, closed):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    return path


# ----------------------------------------------------------------------------- character drawing
_IMG_CACHE = {}


def load_image(path):
    if path in _IMG_CACHE:
        return _IMG_CACHE[path]
    img = skia.Image.open(path) if os.path.exists(path) else None
    _IMG_CACHE[path] = img
    return img


BLINKABLE = ("normal", "determined", "angry", "sad", "wide", "sleepy", "happy", "worried", "suspicious")
OVER_FACE_PARTS = ("glasses",)


def limb_style(cast, kind):
    """cast.sleeve / cast.pants / cast.shoes: '#hex' or {'color': '#hex', 'len': fraction of the limb}.
    Returns (rgb, fraction) or None. Sleeves/pants run from the shoulder/hip, shoes cover the end of the leg."""
    v = cast.get(kind)
    if not v:
        return None
    if isinstance(v, str):
        v = {"color": v}
    dflt = {"sleeve": 0.5, "pants": 1.0, "shoes": 0.13}[kind]
    return hex2rgb(v.get("color")), float(v.get("len", dflt))


def path_segment(path, a, b):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    dst = skia.Path()
    pm.getSegment(a * L, b * L, dst, True)
    return dst


def draw_character_art(canvas, J, cast, eyes="normal", mouth="none", gaze=None, blink=False,
                       hold=None, accessories_root="", gaze_y=None, flush=None):
    """Draw the flat-colour art of one character in rig units (canvas is in rig space).
    Order (same as the AE engine): back hair/accessories, far limbs, torso, near leg, clothes, torso accessories,
    near arm, head, hair/hat parts and image accessories, then the FACE on top (eyes/brows/mouth), then
    over-face accessories (glasses)."""
    P = RIG
    body = hex2rgb(cast.get("color", "#58E0F6"))
    build = float(cast.get("build", 1.0))
    lw_leg = P["limb_w"] * float(cast.get("limb", 1.0))
    lw_arm = P.get("arm_w", P["limb_w"]) * float(cast.get("limb", 1.0))
    tw = P["torso_w"] * build
    D = P["head_d"] * float(cast.get("head", 1.0))
    contour = shade(body, 0.62)
    look = P["look"]
    sleeve, pants, shoes = limb_style(cast, "sleeve"), limb_style(cast, "pants"), limb_style(cast, "shoes")

    def stroke_paint(rgb, width, alpha=1.0):
        return skia.Paint(AntiAlias=True, Color4f=skcolor(rgb, alpha), Style=skia.Paint.kStroke_Style,
                          StrokeWidth=width, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)

    SH = look.get("shade") or {}

    def soft_tube(path, width):
        """a body part as a soft tube: the darker edge colour, then a blurred body-colour core clipped to the part,
        so the colour darkens smoothly from the middle right out to the edge (no inner shape, no spill)"""
        if not SH:
            canvas.drawPath(path, stroke_paint(body, width))
            return
        basep = stroke_paint(shade(body, SH["edge"]), width)
        canvas.drawPath(path, basep)
        outline = skia.Path()
        basep.getFillPath(path, outline)
        canvas.save()
        canvas.clipPath(outline, doAntiAlias=True)
        core = stroke_paint(body, width * (1 - 2 * SH["choke"]))
        core.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(0.5, width * SH["sigma"])))
        canvas.drawPath(path, core)
        canvas.restore()

    def limb(L, contour_alpha=0.0):
        p0, p1, p2, _ = J["limbs"][L]
        lw = lw_arm if L[0] == "a" else lw_leg
        path = limb_path(p0, p1, p2)
        if contour_alpha > 0:
            canvas.drawPath(path, stroke_paint(contour, lw + 7, contour_alpha))
        soft_tube(path, lw)
        segs = []
        if L[0] == "a" and sleeve:
            segs.append((sleeve[0], 0.0, min(1.0, sleeve[1]), lw + 1.5))
        if L[0] == "l" and pants:
            segs.append((pants[0], 0.0, min(1.0, pants[1]), lw + 1.5))
        if L[0] == "l" and shoes:
            segs.append((shoes[0], max(0.0, 1.0 - shoes[1]), 1.0, lw * 1.08))
        for rgb, a, b, w in segs:
            canvas.drawPath(path_segment(path, a, b), stroke_paint(rgb, w))

    # a three-quarter turn: the torso and its clothing narrow and lean towards the facing side
    turn = float(J.get("turn", 1.0))
    ts = 1.0 - P.get("torso_turn", 0.0) * (1.0 - turn)
    tshift = P.get("torso_turn_shift", 0.0) * P["torso_w"] * (1.0 - turn)

    def torso_acc(behind):
        for acc in cast.get("accessories", []):
            if acc.get("slot") == "torso" and bool(acc.get("behind")) == behind:
                canvas.save()
                canvas.translate(*J["hip"])
                canvas.rotate(J["lean"])
                canvas.translate(tshift, 0)
                canvas.scale(ts, 1)
                _draw_acc(canvas, acc, P["torso_len"], accessories_root)
                canvas.restore()

    head_parts = [p for p in cast.get("parts", []) if p in PARTS["head"]]
    torso_parts = [p for p in cast.get("parts", []) if p in PARTS["torso"]]
    hc = J["head"]
    hr = J["head_rot"]

    # 1) hair/back parts behind everything
    canvas.save()
    canvas.translate(*hc)
    canvas.rotate(hr)
    for p in head_parts:
        draw_elements(canvas, PARTS["head"][p]["els"], D, cast, body, only_layer="back")
    for acc in cast.get("accessories", []):
        if acc.get("behind") and acc.get("slot", "head") == "head":
            _draw_acc(canvas, acc, D, accessories_root)
    canvas.restore()
    torso_acc(True)   # capes, backpacks

    # 2) far limbs, torso, near leg, clothes, near arm (the far arm comes in front for crossed / meeting arms)
    three_q = turn < 0.5          # three-quarter view: aN behind the chest, aF (camera side) in front of it
    far_front = three_q or far_arm_front(J, 1.0 if J.get("far_front") else 0.0)
    if three_q:
        limb("aN", look["limb_contour"])
    if not far_front:
        limb("aF")
    limb("lF")
    soft_tube(_line(J["hip"], J["neck"]), tw * ts)
    limb("lN", look.get("leg_contour", 0.0))
    canvas.save()
    canvas.translate(*J["hip"])
    canvas.rotate(J["lean"])
    canvas.translate(tshift, 0)
    canvas.scale(ts, 1)
    for p in torso_parts:
        draw_elements(canvas, PARTS["torso"][p]["els"], 1.0, cast, body)
    canvas.restore()
    torso_acc(False)
    front_arms = []
    if far_front:
        limb("aF")
        front_arms.append("aF")
    if hold and hold.get("hand") == "N" and not hold.get("front", True):
        _draw_hold(canvas, J, hold, accessories_root)
    if not three_q:
        limb("aN", look["limb_contour"])
        front_arms.append("aN")
    # armholes: the garment's shoulder is drawn again over the top end of every arm in front of the body, so the arms
    # come out from under the clothes at the shoulder instead of lying on the fabric (v2.3, same in the AE engine)
    cap_r = float(look.get("armhole_cap", 0.55)) * lw_arm
    if cap_r > 0 and front_arms and any(a.get("slot") == "torso" and not a.get("behind") for a in cast.get("accessories", [])):
        clip = skia.Path()
        for L in front_arms:
            p0 = J["limbs"][L][0]
            clip.addCircle(p0[0], p0[1], cap_r)
        canvas.save()
        canvas.clipPath(clip, doAntiAlias=True)
        torso_acc(False)
        canvas.restore()

    # 3) head, hair/hats, then the face on top, then glasses
    canvas.save()
    canvas.translate(*hc)
    canvas.rotate(hr)
    hp = skia.Path()
    hp.addOval(skia.Rect.MakeXYWH(-D / 2, -D / 2, D, D))
    canvas.drawPath(hp, stroke_paint(contour, 8, look["head_contour"]))
    if SH:
        canvas.drawPath(hp, skia.Paint(AntiAlias=True, Color4f=skcolor(shade(body, SH.get("head_edge", SH["edge"])))))
        ci = D * (1 - 2 * SH["head_choke"])
        cp = skia.Paint(AntiAlias=True, Color4f=skcolor(body))
        cp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(0.5, D * SH["head_sigma"])))
        canvas.save()
        canvas.clipPath(hp, doAntiAlias=True)
        canvas.drawOval(skia.Rect.MakeXYWH(-ci / 2, -ci / 2, ci, ci), cp)
        canvas.restore()
    else:
        canvas.drawPath(hp, skia.Paint(AntiAlias=True, Color4f=skcolor(body)))
    if flush and flush[0] > 0.004 and flush[1] is not None:     # face colour (poisoned, angry red, cold...) on the skull only
        canvas.drawPath(hp, skia.Paint(AntiAlias=True, Color4f=skcolor(flush[1], flush[0])))
    for p in head_parts:
        if p not in OVER_FACE_PARTS:
            draw_elements(canvas, PARTS["head"][p]["els"], D, cast, body, only_layer="front")
    for acc in cast.get("accessories", []):
        if not acc.get("behind") and acc.get("slot", "head") == "head" and not acc.get("over_face"):
            _draw_acc(canvas, acc, D, accessories_root)
    F = P["face"]
    fbody = body                         # lids are cut in the skin colour - flushed skin when the face is coloured
    if flush and flush[0] > 0.004 and flush[1] is not None:
        fbody = tuple(body[i] + (flush[1][i] - body[i]) * flush[0] for i in range(3))
    g = (gaze if gaze is not None else F["gaze"]) * D
    gy = (gaze_y if gaze_y is not None else F.get("gaze_y", 0.0)) * D
    canvas.save()
    canvas.translate(g, gy)
    if blink and eyes in BLINKABLE:
        draw_elements(canvas, FACES["eyes"]["closed"], D, cast, fbody)
    else:
        draw_elements(canvas, FACES["eyes"].get(eyes, FACES["eyes"]["normal"]), D, cast, fbody)
    canvas.restore()
    canvas.save()
    canvas.translate(g * F.get("mouth_follow", 0.6), gy * F.get("mouth_follow_y", 0.3))
    draw_elements(canvas, FACES["mouths"].get(mouth, []), D, cast, fbody)
    canvas.restore()
    for p in head_parts:
        if p in OVER_FACE_PARTS:
            draw_elements(canvas, PARTS["head"][p]["els"], D, cast, body, only_layer="front")
    for acc in cast.get("accessories", []):
        if not acc.get("behind") and acc.get("slot", "head") == "head" and acc.get("over_face"):
            canvas.save()
            if acc.get("follow_gaze"):
                canvas.translate(g, gy)            # glasses ride the eyes
            _draw_acc(canvas, acc, D, accessories_root)
            canvas.restore()
    canvas.restore()
    if hold and (hold.get("front", True) or hold.get("hand") != "N"):
        _draw_hold(canvas, J, hold, accessories_root)


def _line(a, b):
    p = skia.Path()
    p.moveTo(*a)
    p.lineTo(*b)
    return p


_ACC_T = [0.0]   # current time for accessories with from/to (set by render_character)


def _draw_acc(canvas, acc, unit, root):
    t = _ACC_T[0]
    if t < float(acc.get("from", -1e9)) or t >= float(acc.get("to", 1e9)):
        return
    img = load_image(os.path.join(root, acc["file"]) if root and not os.path.isabs(acc["file"]) else acc["file"])
    if img is None:
        return
    w = acc.get("w", 1.1) * unit
    h = w * img.height() / img.width()
    cx = acc.get("dx", 0.0) * unit
    cy = acc.get("dy", -0.45) * unit
    canvas.save()
    canvas.translate(cx, cy)
    if acc.get("rot"):
        canvas.rotate(acc["rot"])
    if acc.get("flip"):
        canvas.scale(-1, 1)
    canvas.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    canvas.restore()


def _draw_hold(canvas, J, hold, root):
    L = "a" + hold.get("hand", "N")
    p0, p1, p2, al = J["limbs"][L]
    img = load_image(os.path.join(root, hold["file"]) if root and not os.path.isabs(hold["file"]) else hold["file"])
    if img is None:
        return
    w = hold.get("w", 220)
    h = w * img.height() / img.width()
    canvas.save()
    canvas.translate(*p2)
    ox, oy = hold.get("offset", [0, 0])
    g = hold.get("grip")
    if g:
        # the hand holds the prop at its grip; a tool continues the forearm (its tip points where the arm points),
        # an upright prop stays upright (same maths as the AE engine)
        canvas.translate(ox, oy)
        if hold.get("style", "tool") == "tool":
            tp = hold.get("tip", [g[0], 0.0])
            th = math.degrees(math.atan2((tp[1] - g[1]) * h, (tp[0] - g[0]) * w))
            if hold.get("aim"):       # the tip points at a spot (a cheek being brushed), whatever the forearm does
                am = hold["aim"]
                phi = math.degrees(math.atan2(am[1] - p2[1] - oy, am[0] - p2[0] - ox))
            else:
                phi = math.degrees(math.atan2(math.cos(al * D2R), math.sin(al * D2R)))
            canvas.rotate(phi - th)
        canvas.rotate(hold.get("rot", 0))
        canvas.drawImageRect(img, skia.Rect.MakeXYWH(-g[0] * w, -g[1] * h, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    else:
        if hold.get("follow"):
            canvas.rotate(-al)
        canvas.rotate(hold.get("rot", 0))
        canvas.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2 + ox, -h / 2 + oy, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    canvas.restore()


# ----------------------------------------------------------------------------- finishing (outline, bevel, glow)
def _blur_alpha(a, radius):
    im = Image.fromarray((a * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im).astype(np.float32) / 255.0


def _dilate(a, r):
    """morphological dilation of an alpha mask (skia, separable and fast)"""
    if r <= 0:
        return a
    h, w = a.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    img = skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kPremul_AlphaType)
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Dilate(int(r), int(r))))
    out = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kPremul_AlphaType)
    return out[..., 3].astype(np.float32) / 255.0


def finish_layer(rgba, px_scale, cast, state="color"):
    """rgba: float32 HxWx4 premultiplied art. Returns finished premultiplied RGBA (outline+bevel+glow)."""
    look = RIG["look"]
    a = rgba[..., 3]
    if a.max() <= 0:
        return rgba
    col = rgba[..., :3]
    k = look["bevel"]
    if k > 0:   # legacy emboss (the references have none: soft per-part shading is drawn with the art instead)
        th = max(1.5, look["bevel_thickness"] * px_scale)
        o = max(1, int(round(th * 0.55)))
        b = _blur_alpha(a, th * 0.6)
        b_dr = np.zeros_like(b)
        b_ul = np.zeros_like(b)
        b_dr[o:, o:] = b[:-o, :-o]
        b_ul[:-o, :-o] = b[o:, o:]
        hl = np.clip(a * (1 - b_dr), 0, 1)
        sh = np.clip(a * (1 - b_ul), 0, 1)
        col = col + (a[..., None] - col) * (hl[..., None] * k * 0.55)
        col = col * (1 - sh[..., None] * k * 0.75)
        core = _blur_alpha(a, th * 2.2)
        col = col * (0.9 + 0.12 * core[..., None])
    if state == "gray":
        lum = (col[..., 0] * 0.3 + col[..., 1] * 0.59 + col[..., 2] * 0.11)
        g = np.clip(lum * 0.85 + a * 0.18, 0, 1)
        col = np.stack([g, g, g], -1)
    elif state == "silhouette":
        col = np.zeros_like(col) + a[..., None] * 0.04
    elif state == "red":
        col = np.stack([np.clip(col[..., 0] * 0.6 + a * 0.45, 0, 1), col[..., 1] * 0.35, col[..., 2] * 0.35], -1)
    elif state == "sick":
        col = np.stack([col[..., 0] * 0.65, np.clip(col[..., 1] * 0.8 + a * 0.15, 0, 1), col[..., 2] * 0.55], -1)
    # outline: dilated alpha in dark ink under the art
    r = max(1, int(round(look["outline_px"] * px_scale)))   # rig units -> output px (same rule as the AE engine)
    ol = _dilate(a, r)
    ink = hex2rgb(cast.get("outline")) if cast.get("outline") else shade(hex2rgb(cast.get("color", "#58E0F6")), look.get("outline_shade", 0.42))
    out = np.zeros_like(rgba)
    out[..., 3] = ol
    out[..., :3] = np.array(ink, np.float32) * ol[..., None]
    # glow under everything
    glow = float(cast.get("glow", look["glow_default"]))
    if glow > 0 and state not in ("silhouette",):
        gr = look["glow_radius"] * px_scale * 1.0
        ga = _blur_alpha(a, max(2.0, gr)) * glow
        body = np.array(hex2rgb(cast.get("color", "#58E0F6")), np.float32)
        if state == "gray":
            body = np.array([0.8, 0.8, 0.8], np.float32)
        gl = np.zeros_like(rgba)
        gl[..., 3] = np.clip(ga, 0, 1)
        gl[..., :3] = body * gl[..., 3:4]
        out = gl * (1 - out[..., 3:4]) + out
    # art over outline
    art = np.concatenate([col, a[..., None]], -1)
    out = art + out * (1 - a[..., None])
    return out


def render_character(cast, params, t, ctl, px_per_unit, accessories_root="", state="color", margin=40):
    """Render one finished character to a premultiplied float RGBA array.
    Returns (array, origin_xy_in_array) where origin is the rig (0,0) foot point."""
    _ACC_T[0] = t
    J = solve(params, t, ctl.get("walk", 0), ctl.get("run", 0), ctl.get("speed", 1.6), ctl.get("idle", 1), ctl.get("phase", 0),
              tw=RIG["torso_w"] * float(cast.get("build", 1.0)), arms=ctl.get("arms", 1.0),
              sw=cast_arms(cast, accessories_root)[0], sd=cast_arms(cast, accessories_root)[1])
    W = int(RIG["comp_w"] * px_per_unit) + margin * 2
    H = int(RIG["comp_h"] * px_per_unit) + margin * 2
    ox = RIG["origin"][0] * px_per_unit + margin
    oy = RIG["origin"][1] * px_per_unit + margin
    surface = skia.Surface(W, H)
    c = surface.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.translate(ox, oy)
    c.scale(px_per_unit, px_per_unit)
    draw_character_art(c, J, cast, ctl.get("eyes", "normal"), ctl.get("mouth", "none"), ctl.get("gaze"),
                       ctl.get("blink", False), ctl.get("hold"), accessories_root, ctl.get("gaze_y"), ctl.get("flush"))
    arr = surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType,
                                               alphaType=skia.AlphaType.kPremul_AlphaType)
    rgba = arr.astype(np.float32) / 255.0
    # crop to content to keep effects cheap
    ys, xs = np.where(rgba[..., 3] > 0.003)
    if len(xs) == 0:
        return rgba[:2, :2] * 0, (ox, oy)
    pad = int(max(8, RIG["look"]["glow_radius"] * px_per_unit * 2.5 + 6))
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad)
    rgba = rgba[y0:y1, x0:x1]
    fin = finish_layer(rgba, px_per_unit, cast, state)
    return fin, (ox - x0, oy - y0)
