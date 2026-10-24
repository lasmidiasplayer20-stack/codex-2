"""Detailed costume pieces (hair, beards, hats, glasses, clothes) that sit exactly on the rig.

How it works: the piece is drawn by an image model ON a template of our own character (a flat magenta head, or a
magenta body in the front-view stance, rendered from rig.json), with a transparent background. The magenta is then
keyed out and a circle is fitted to the visible head, so the piece is placed on the rig's head/torso to the pixel
whatever framing the model chose. Result: a transparent PNG plus its placement (w, dx, dy) for cast.accessories.

  python costume.py head  "worn beige knitted beanie and a bushy dark-brown beard" -o P/assets/cast/hobo_head.png
  python costume.py torso "blue cotton apron with white straps" -o P/assets/cast/chef_apron.png
  python costume.py batch P/plan/costumes.json [--yes] [--spec P/plan/spec.json]   # many pieces in parallel
  python costume.py fit image.png --piece head -o out.png     # fit a piece drawn elsewhere on our template
  python costume.py templates -o DIR                          # the template PNGs (to use with any other generator)
  python costume.py library [--tags hat,army]                 # the bundled library (free mode, no API key)
  python costume.py use P --cast hobo --piece hat_beanie_worn [--tint "#7A5230"] [--from 0 --to 7]  # add a library piece

costumes.json: {"jobs": [{"cast": "hobo", "piece": "head", "prompt": "...", "out": "assets/cast/hobo_head.png"},
                         {"cast": "chef", "piece": "torso", "prompt": "...", "out": "assets/cast/chef_apron.png"}]}
With --spec, every finished piece is added to that cast's accessories in the spec (replacing the same file).

Generation uses GPT Image 2.5 on Kie.ai (image-to-image with a transparent background; KIE_API_KEY, see keys.py).
The asset mode of a project (plan/assets_mode.txt: "kie" or "free") decides whether the pipeline may spend credits.
"""
import argparse
import base64
import io
import json
import math
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_common import KIT, get_key, user_file  # noqa: E402

KIE = "https://api.kie.ai/api/v1"
UPLOAD = "https://kieai.redpandaai.co/api/file-base64-upload"
MODEL = "gpt-image-2-5-flare-image-to-image"
LIB = os.path.join(KIT, "assets", "costumes")
RIG = json.load(open(os.path.join(KIT, "data", "rig.json"), encoding="utf-8"))
KEY = (255, 0, 255)

STYLE = ("Style: detailed 2D cartoon illustration like a modern animated YouTube Short - clean thin dark outline, cel "
         "shading with soft highlights, fine strand / fabric / texture lines, rich but natural colours.")
PROMPTS = {
    "head": ("Draw {subject} on this plain magenta ball head. Keep the magenta head, neck and body EXACTLY as they are - "
             "same size, same position, flat magenta, no face, no eyes, no mouth, no ears. Hair and hats sit on and around "
             "the head; beards hang from the lower half of the head; leave the middle of the face uncovered. Keep everything close to "
             "the head like a neat cartoon costume: hats, caps and helmets hug the skull - only slightly wider than the head "
             "(only real wide-brim hats such as cowboy or witch hats stick out further) - and cover just the top third of the "
             "head, their lower edge above where the eyes would be; no chin straps. Hair has modest volume. Beards stay within "
             "the width of the face and end just below the chin. Draw ONLY what is "
             "described - no extra hair, beard, bandana or clothing that was not asked for. Front view. "
             + STYLE + " Transparent background, nothing else in the image, no text."),
    "torso": ("Dress this plain magenta character in {subject}. Keep the magenta head, arms and legs EXACTLY as they are - "
              "same size, same position, flat magenta, no face. The garment covers only the magenta torso shape, fitting it closely from the top of the "
              "torso down to where the legs begin (sleeveless; straps may cross the shoulders); keep the gap between head "
              "and body empty; do not draw on the arms, legs or head. Front view. " + STYLE +
              " Transparent background, nothing else in the image, no text."),
    "face": ("Put {subject} on this plain magenta ball head, sitting where the eyes would be (in the upper middle of the "
             "face). Keep the magenta head EXACTLY as it is, flat magenta, no face, no eyes. Front view. " + STYLE +
             " Transparent background, nothing else in the image, no text."),
}


# ----------------------------------------------------------------------------------------------- templates
def template_geometry(piece):
    """Pixel geometry of the template: head centre/diameter and (torso) hip position, in a 1024x1024 canvas."""
    if piece in ("head", "face"):
        D = 400.0
        return {"size": (1024, 1024), "head": (512.0, 520.0), "D": D}
    D = 230.0
    k = D / RIG["head_d"]
    hc = (512.0, 250.0)
    hip = (hc[0], hc[1] + (RIG["torso_len"] + RIG["head_lift"]) * k)
    return {"size": (1024, 1024), "head": hc, "D": D, "hip": hip, "k": k}


def make_template(piece):
    g = template_geometry(piece)
    W, H = g["size"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hx, hy = g["head"]
    R = g["D"] / 2
    if piece in ("head", "face"):
        k = g["D"] / RIG["head_d"]
        tw = RIG["torso_w"] * k
        # the body starts a small gap below the head, as in the reference style (no neck); long hair and beards
        # fall over it
        body_top = hy + RIG["head_lift"] * k - tw / 2
        d.rounded_rectangle((hx - tw / 2, body_top, hx + tw / 2, H + 40), radius=int(tw / 2), fill=KEY + (255,))
        d.ellipse((hx - R, hy - R, hx + R, hy + R), fill=KEY + (255,))
        return im, g
    k = g["k"]
    tw, lw, aw = RIG["torso_w"] * k, RIG["limb_w"] * k, RIG.get("arm_w", RIG["limb_w"]) * k
    neck = (hx, hy + RIG["head_lift"] * k)
    hip = g["hip"]
    sw = RIG.get("shoulder_spread", 0.36) * RIG["torso_w"] * k
    sh = (neck[0], neck[1] + RIG["shoulder_down"] * k)

    def tube(a, b, w):
        d.line([a, b], fill=KEY + (255,), width=int(w))
        for p in (a, b):
            d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=KEY + (255,))

    for s in (-1, 1):   # arms hanging slightly out, legs apart (front view)
        a0 = (sh[0] + s * sw, sh[1])
        a1 = (a0[0] + s * math.sin(math.radians(12)) * RIG["arm_u"] * k, a0[1] + math.cos(math.radians(12)) * RIG["arm_u"] * k)
        a2 = (a1[0] + s * math.sin(math.radians(6)) * RIG["arm_l"] * k, a1[1] + math.cos(math.radians(6)) * RIG["arm_l"] * k)
        tube(a0, a1, aw); tube(a1, a2, aw)
        l0 = (hip[0] + s * RIG.get("hip_spread", 0.22) * RIG["torso_w"] * k, hip[1])
        l1 = (l0[0] + s * math.sin(math.radians(6)) * (RIG["leg_u"] + RIG["leg_l"]) * k, l0[1] + (RIG["leg_u"] + RIG["leg_l"]) * k)
        tube(l0, (l1[0], min(l1[1], H - lw)), lw)
    tube(hip, neck, tw)
    d.ellipse((hx - R, hy - R, hx + R, hy + R), fill=KEY + (255,))
    return im, g


# ----------------------------------------------------------------------------------------------- keying and fitting
def key_mask(a):
    """0..1 'magenta-ness' of each pixel (flat or shaded magenta, not reds/purples of real costumes)."""
    r, g, b, al = [a[..., i].astype(np.float32) for i in range(4)]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    rb = np.minimum(r, b)
    balance = 1 - np.abs(r - b) / np.maximum(mx, 1)          # magenta has R ~= B
    dom = np.clip((rb - g) / np.maximum(mx, 1), 0, 1)          # both well above green
    k = np.clip((dom - 0.35) / 0.25, 0, 1) * np.clip((balance - 0.55) / 0.25, 0, 1) * np.clip((sat - 0.35) / 0.2, 0, 1)
    k *= np.clip((mx - 60) / 60, 0, 1)
    return k * (al / 255.0)


def fit_circle(mask, R0, rng=None):
    """Circle through the visible left/right edges of the template head (hair, hats and beards hide the rest).
    RANSAC over row extremes above the neck, requiring support on both sides; returns ((cx, cy, r), n) or None."""
    rng = rng or np.random.default_rng(3)
    ys, xs = np.nonzero(mask)
    if len(xs) < 500:
        return None
    rows = {}
    for y in range(ys.min(), ys.max() + 1):
        row = np.nonzero(mask[y])[0]
        if len(row) > 3:
            rows[y] = (row.min(), row.max())
    widths = {y: b - a for y, (a, b) in rows.items()}
    wmax = max(widths.values())
    ymax = max(widths, key=lambda y: widths[y])
    L, Rr = [], []
    for y, (a, b) in rows.items():
        if y > ymax and widths[y] < 0.62 * wmax:      # neck / shoulders below the head
            continue
        if widths[y] < 0.25 * wmax:                   # slivers between hair and beard
            continue
        L.append((a, y)); Rr.append((b, y))
    if len(L) < 10:
        return None
    PL, PR = np.array(L, np.float64), np.array(Rr, np.float64)
    P = np.vstack([PL, PR])
    best, best_s = None, 0
    for _ in range(3000):
        i = rng.choice(len(PL), 2, replace=False if len(PL) > 1 else True)
        j = rng.choice(len(PR), 1)
        (x1, y1), (x2, y2), (x3, y3) = PL[i[0]], PL[i[1]], PR[j[0]]
        if rng.random() < 0.5:
            (x1, y1), (x2, y2), (x3, y3) = PR[j[0]], PL[i[0]], PR[rng.choice(len(PR))]
        dd = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(dd) < 1e-6:
            continue
        ux = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / dd
        uy = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / dd
        r = math.hypot(x1 - ux, y1 - uy)
        if not (0.6 * R0 < r < 1.35 * R0):
            continue
        nl = int((np.abs(np.hypot(PL[:, 0] - ux, PL[:, 1] - uy) - r) < 2.5).sum())
        nr = int((np.abs(np.hypot(PR[:, 0] - ux, PR[:, 1] - uy) - r) < 2.5).sum())
        sc = min(nl, nr) * 2 + max(nl, nr) * 0.5       # both sides must agree
        if sc > best_s:
            best, best_s = (ux, uy, r), sc
    if best is None or best_s < 30:
        return None
    ux, uy, r = best
    inl = P[np.abs(np.hypot(P[:, 0] - ux, P[:, 1] - uy) - r) < 2.5]
    A = np.c_[2 * inl[:, 0], 2 * inl[:, 1], np.ones(len(inl))]
    bb = inl[:, 0] ** 2 + inl[:, 1] ** 2
    sol, *_ = np.linalg.lstsq(A, bb, rcond=None)
    cx, cy = sol[0], sol[1]
    r = math.sqrt(max(1.0, sol[2] + cx ** 2 + cy ** 2))
    return (float(cx), float(cy), float(r)), int(best_s)


def remove_fake_transparency(a):
    """Some generations paint a grey/white checkerboard instead of real transparency. Remove light, colourless
    pixels connected to the image border (the piece's dark outline stops the fill)."""
    al = a[..., 3]
    if (al > 250).mean() < 0.85:
        return a                                   # real transparency already
    rgb = a[..., :3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    light = (mn > 150) & ((mx - mn) < 22)
    try:
        from scipy import ndimage
        lab, n = ndimage.label(light)
        border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
        bg = np.isin(lab, list(border))
    except ImportError:
        bg = light
    bg = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    a[..., 3] = np.where(bg, 0, al)
    return a


def remove_key(im):
    a = np.array(im.convert("RGBA")).astype(np.float32)
    a = remove_fake_transparency(a)
    k = key_mask(a)
    # grow the key slightly into the anti-aliased rim
    kk = np.asarray(Image.fromarray((k * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))).astype(np.float32) / 255
    k = np.maximum(k, kk * 0.85)
    a[..., 3] *= (1 - k)
    # magenta despill on what remains
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.minimum(r, b)
    sp = np.clip(m - g, 0, None) * 0.9
    a[..., 0] = r - sp
    a[..., 2] = b - sp
    a[..., 3] = np.where(a[..., 3] < 8, 0, a[..., 3])
    # soft white glow some generations paint around the template: semi-transparent, colourless and light
    rgb = a[..., :3]
    mxc, mnc = rgb.max(-1), rgb.min(-1)
    halo = (a[..., 3] < 190) & ((mxc - mnc) < 0.14 * np.maximum(mxc, 1)) & (mxc > 175)
    a[..., 3] = np.where(halo, 0, a[..., 3])
    a[..., 3] *= thin_stroke_mask(a[..., 3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), k


def thin_stroke_mask(alpha, r=3):
    """Drop thin strokes left over from the template (the model often outlines the magenta neck/body): a
    morphological opening of the alpha (radius r) plus removal of small islands. Returns a 0..1 multiplier."""
    m = Image.fromarray(((alpha > 40) * 255).astype(np.uint8), "L")
    opened = m.filter(ImageFilter.MinFilter(2 * r + 1)).filter(ImageFilter.MaxFilter(2 * r + 5))
    o = np.asarray(opened) > 0
    try:
        from scipy import ndimage
        # long thin appendages (a body outline or strap redrawn by the model, ~5-15 px wide) are cut off where they
        # leave the solid parts of the piece; short thin details next to solid parts (hair strand tips) stay
        thick = np.asarray(m.filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MaxFilter(15))) > 0
        if thick.any():
            near = ndimage.distance_transform_edt(~thick) <= 28
            o = o & (thick | near)
        lab, n = ndimage.label(o)
        if n > 1:
            sizes = ndimage.sum(o, lab, range(1, n + 1))
            keep = np.isin(lab, [i + 1 for i, sz in enumerate(sizes) if sz >= 0.08 * sizes.max()])
            o = keep
    except ImportError:
        pass
    soft = np.asarray(Image.fromarray((o * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    return np.clip(soft * 1.3, 0, 1)


def fit_piece(img, piece, out, extra=None):
    """Key out the template, register it on the rig, crop, save PNG + placement JSON. Returns the accessory dict."""
    im = img.convert("RGBA")
    if im.size != (1024, 1024):
        im = im.resize((1024, 1024), Image.LANCZOS)
    g = template_geometry(piece)
    a = np.array(im)
    k = key_mask(a.astype(np.float32))
    res = fit_circle(k > 0.5, g["D"] / 2)
    if res:
        (cx, cy, r), n = res
        fitted = True
    else:
        cx, cy = g["head"]; r = g["D"] / 2; fitted = False
    clean, _ = remove_key(im)
    bbox = clean.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bbox:
        raise RuntimeError("nothing left after removing the template - the model drew no costume")
    pad = 6
    bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(1024, bbox[2] + pad), min(1024, bbox[3] + pad))
    crop = clean.crop(bbox)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    crop.save(out)
    D = 2 * r
    icx, icy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    if piece in ("head", "face"):
        acc = {"slot": "head", "w": round((bbox[2] - bbox[0]) / D, 4),
               "dx": round((icx - cx) / D, 4), "dy": round((icy - cy) / D, 4)}
        if piece == "face":
            # glasses & co. ride the eyes: centred on the eye line, scaled to the eye spacing, moved by the gaze
            ex = 0.125
            acc.update({"over_face": True, "follow_gaze": True, "dx": 0.0, "dy": -0.085,
                        "w": round(max(0.72, min(0.95, acc["w"] * 0.8)), 4)})
    else:
        kpx = D / RIG["head_d"]                       # template px per rig unit, from the fitted head
        unit = RIG["torso_len"] * kpx
        hipx = cx
        hipy = cy + (RIG["torso_len"] + RIG["head_lift"]) * kpx
        acc = {"slot": "torso", "w": round((bbox[2] - bbox[0]) / unit, 4),
               "dx": round((icx - hipx) / unit, 4), "dy": round((icy - hipy) / unit, 4)}
    acc["fit"] = {"head_px": [round(cx, 1), round(cy, 1), round(r, 1)], "registered": fitted}
    if extra:
        acc.update(extra)
    json.dump(acc, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
    return acc


# ----------------------------------------------------------------------------------------------- Kie.ai
def kie_headers(key):
    return {"Authorization": "Bearer " + key, "Content-Type": "application/json"}


import threading
_UPLOAD_LOCK = threading.Lock()


def upload_template(key, piece):
    """Upload the template once per piece type (cached URL for 20 h in ~/.2d_stick_animator); one upload at a time."""
    with _UPLOAD_LOCK:
        for attempt in range(4):
            try:
                return _upload_template(key, piece)
            except RuntimeError:
                if attempt == 3:
                    raise
                time.sleep(4 + 4 * attempt)


def _upload_template(key, piece):
    cache = user_file("template_urls.json")
    try:
        c = json.load(open(cache, encoding="utf-8"))
    except Exception:
        c = {}
    ent = c.get(piece)
    if ent and time.time() - ent["t"] < 20 * 3600:
        return ent["url"]
    im, _ = make_template(piece)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    body = {"base64Data": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(),
            "uploadPath": "2d-stick-animator/templates", "fileName": f"template_{piece}_{int(time.time())}.png"}
    r = requests.post(UPLOAD, json=body, headers=kie_headers(key), timeout=120)
    d = r.json()
    if not d.get("success"):
        raise RuntimeError("template upload failed: " + r.text[:200])
    url = d["data"]["downloadUrl"]
    c[piece] = {"url": url, "t": time.time()}
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    json.dump(c, open(cache, "w"))
    return url


SLEEVELESS = ("SLEEVELESS: only the body of the garment from the shoulders down to the hips, absolutely no sleeves and "
              "nothing on the arms (the arms are drawn separately and move on their own)")


def torso_subject(subject):
    """Torso pieces never have sleeves: drawn sleeves hang still while the rig's real arms move on top of them (user
    feedback, v2.3). Sleeve wording is removed and the sleeveless instruction always added."""
    import re
    s = re.sub(r"\b(long|short|half|3/4)[- ]sleeved\b|\bwith (?:[\w-]+ ){0,3}sleeves?(?: rolled up)?\b|"
               r"\b(puffed|puff|rolled[- ]up|rolled|long|short|bell) sleeves?\b|\bsleeves? rolled up\b", "", subject, flags=re.I)
    s = re.sub(r"\s{2,}", " ", re.sub(r"\s+,", ",", s)).strip(" ,.")
    return s if "sleeveless" in s.lower() and "no sleeves" in s.lower() else f"{s}, {SLEEVELESS}"


def kie_generate(key, piece, subject, retries=2):
    url = upload_template(key, piece)
    if piece == "torso":
        subject = torso_subject(subject)
    prompt = PROMPTS[piece].format(subject=subject.rstrip("."))
    last = None
    for attempt in range(retries + 1):
        r = requests.post(KIE + "/jobs/createTask", headers=kie_headers(key), timeout=60,
                          json={"model": MODEL, "input": {"prompt": prompt, "input_urls": [url], "aspect_ratio": "1:1",
                                                          "resolution": "1K", "background": "transparent"}})
        d = r.json()
        if d.get("code") != 200:
            last = d.get("msg")
            time.sleep(5)
            continue
        task = d["data"]["taskId"]
        t0 = time.time()
        while time.time() - t0 < 600:
            time.sleep(6)
            info = requests.get(KIE + "/jobs/recordInfo?taskId=" + task, headers=kie_headers(key), timeout=60).json().get("data") or {}
            st = info.get("state")
            if st == "success":
                res = json.loads(info["resultJson"]) if isinstance(info.get("resultJson"), str) else info.get("resultJson") or {}
                u = (res.get("resultUrls") or [None])[0]
                return Image.open(io.BytesIO(requests.get(u, timeout=180).content)), {"task": task, "url": u, "prompt": prompt}
            if st == "fail":
                last = f"{info.get('failCode')} {info.get('failMsg')}"
                break
        time.sleep(3)
    raise RuntimeError(f"Kie generation failed: {last}")


def make_piece(key, piece, subject, out, extra=None):
    img, meta = kie_generate(key, piece, subject)
    raw = os.path.splitext(out)[0] + "_raw.png"
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    img.save(raw)
    acc = fit_piece(img, piece, out, extra)
    acc["source"] = {"generator": "kie:" + MODEL, "task": meta["task"], "subject": subject}
    warn = size_warning(piece, subject, acc)
    if warn:
        acc["warning"] = warn
        print(f"check {out}: {warn}")
    json.dump(acc, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
    return acc


WIDE_OK = ("cowboy", "sombrero", "witch", "pirate", "tricorn", "viking", "horn", "afro", "long", "wavy", "curly",
           "graduation", "mortarboard", "fedora", "top hat", "bob", "ponytail", "feather", "flower", "wide")


def size_warning(piece, subject, acc):
    """The reference style keeps costume pieces close to the head: flag pieces that came out oversized."""
    if piece != "head":
        return ""
    wide = any(k in subject.lower() for k in WIDE_OK)
    lim = 1.8 if wide else 1.45
    if acc["w"] > lim:
        return (f"piece is {acc['w']:.2f} head widths wide (style: hats/helmets ~1.05-1.3, brimmed or long hair up to "
                f"~1.8) - regenerate with a snugger description")
    return ""


# ----------------------------------------------------------------------------------------------- spec + library
def add_to_spec(spec_path, cast_id, file_rel, acc, when=None):
    """Add (or replace) a piece in spec.cast.<id>.accessories. when: optional {"from": s, "to": s} costume window."""
    spec = json.load(open(spec_path, encoding="utf-8"))
    c = spec.setdefault("cast", {}).setdefault(cast_id, {"color": "#58E0F6"})
    accs = [x for x in c.get("accessories", []) if x.get("file") != file_rel]
    entry = {"file": file_rel, "slot": acc["slot"], "w": acc["w"], "dx": acc["dx"], "dy": acc["dy"]}
    for k in ("over_face", "follow_gaze", "behind"):
        if acc.get(k):
            entry[k] = True
    for k in ("from", "to"):
        if when and when.get(k) is not None:
            entry[k] = when[k]
    accs.append(entry)
    c["accessories"] = accs
    json.dump(spec, open(spec_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def ensure_library():
    """Unpack the bundled WebP library to PNG (what After Effects imports) if setup has not done it yet."""
    src = os.path.join(KIT, "assets", "costumes_webp")
    if not os.path.isdir(src):
        return
    os.makedirs(LIB, exist_ok=True)
    for f in os.listdir(src):
        dst = os.path.join(LIB, f[:-5] + ".png")
        if f.endswith(".webp") and (not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(os.path.join(src, f))):
            Image.open(os.path.join(src, f)).convert("RGBA").save(os.path.join(LIB, f[:-5] + ".png"))
    if os.path.exists(os.path.join(src, "index.json")):
        shutil.copyfile(os.path.join(src, "index.json"), os.path.join(LIB, "index.json"))


def library_index():
    p = os.path.join(LIB, "index.json")
    src = os.path.join(KIT, "assets", "costumes_webp", "index.json")
    if not os.path.exists(p) or (os.path.exists(src) and os.path.getmtime(p) < os.path.getmtime(src)):
        ensure_library()       # first use, or the plugin brought a newer library
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"pieces": []}


def tint_image(src, dst, color, strength=0.85):
    """Recolour a library piece (e.g. hair) while keeping its shading and outline."""
    im = Image.open(src).convert("RGBA")
    a = np.array(im).astype(np.float32) / 255
    lum = a[..., :3] @ np.array([0.3, 0.59, 0.11], np.float32)
    tgt = np.array([int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    tl = float(tgt @ np.array([0.3, 0.59, 0.11], np.float32))
    rel = lum / max(0.05, float(np.median(lum[a[..., 3] > 0.5])) if (a[..., 3] > 0.5).any() else 0.5)
    col = np.clip(tgt[None, None, :] * rel[..., None] * (tl / max(tl, 1e-3)), 0, 1)
    dark = lum < 0.12                                   # keep outlines dark
    out = a[..., :3] * (1 - strength) + col * strength
    out[dark] = a[..., :3][dark]
    a[..., :3] = out
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA").save(dst)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    for nm in ("head", "torso", "face"):
        s = sp.add_parser(nm); s.add_argument("subject"); s.add_argument("-o", "--out", required=True)
        s.add_argument("--spec"); s.add_argument("--cast")
    b = sp.add_parser("batch"); b.add_argument("jobs"); b.add_argument("--spec"); b.add_argument("--yes", action="store_true")
    b.add_argument("--workers", type=int, default=6)
    f = sp.add_parser("fit"); f.add_argument("image"); f.add_argument("--piece", default="head"); f.add_argument("-o", "--out", required=True)
    t = sp.add_parser("templates"); t.add_argument("-o", "--out", default=".")
    lb = sp.add_parser("library"); lb.add_argument("--tags", default="")
    u = sp.add_parser("use"); u.add_argument("project"); u.add_argument("--cast", required=True); u.add_argument("--piece", required=True)
    u.add_argument("--tint"); u.add_argument("--spec", default="plan/spec.json")
    u.add_argument("--from", dest="t_from", type=float); u.add_argument("--to", dest="t_to", type=float)
    a = ap.parse_args()

    if a.cmd == "templates":
        os.makedirs(a.out, exist_ok=True)
        for pc in ("head", "torso"):
            im, g = make_template(pc)
            im.save(os.path.join(a.out, f"template_{pc}.png"))
            print(f"template_{pc}.png", json.dumps(g))
        return
    if a.cmd == "fit":
        print(json.dumps(fit_piece(Image.open(a.image), a.piece, a.out)))
        return
    if a.cmd == "library":
        tags = [x for x in a.tags.split(",") if x]
        for p in library_index()["pieces"]:
            if all(tg in p.get("tags", []) for tg in tags):
                print(f"{p['id']:24s} {p['slot']:6s} {', '.join(p.get('tags', []))}")
        return
    if a.cmd == "use":
        idx = {p["id"]: p for p in library_index()["pieces"]}
        if a.piece not in idx:
            sys.exit(f"no library piece {a.piece!r} (python costume.py library)")
        p = idx[a.piece]
        src = os.path.join(LIB, p["file"])
        rel = f"assets/cast/{a.cast}_{a.piece}.png"
        dst = os.path.join(a.project, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if a.tint:
            tint_image(src, dst, a.tint)
        else:
            shutil.copyfile(src, dst)
        add_to_spec(os.path.join(a.project, a.spec), a.cast, rel, p, {"from": a.t_from, "to": a.t_to})
        print(f"{a.cast}: + {rel} ({p['slot']})")
        return

    key = get_key("kie")
    if a.cmd in ("head", "torso", "face"):
        acc = make_piece(key, a.cmd, a.subject, a.out)
        print(json.dumps(acc))
        if a.spec and a.cast:
            base = os.path.dirname(os.path.dirname(os.path.abspath(a.spec)))
            add_to_spec(a.spec, a.cast, os.path.relpath(os.path.abspath(a.out), base).replace("\\", "/"), acc)
        return
    jobs = json.load(open(a.jobs, encoding="utf-8"))["jobs"]
    base = os.path.dirname(os.path.dirname(os.path.abspath(a.jobs)))
    if not a.yes:
        print(f"{len(jobs)} pieces with GPT Image 2.5 on Kie.ai (about 4-6 credits each). Re-run with --yes to generate.")
        for j in jobs:
            print(f"  {j.get('cast', '-'):10s} {j['piece']:6s} {j['prompt']}")
        return

    def run(j):
        out = os.path.join(base, j["out"]) if not os.path.isabs(j["out"]) else j["out"]
        try:
            acc = make_piece(key, j["piece"], j["prompt"], out, j.get("extra"))
            return j, acc, None
        except Exception as e:  # keep going with the others
            return j, None, str(e)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for j, acc, err in ex.map(run, jobs):
            if err:
                print(f"FAILED {j['out']}: {err}")
                continue
            print(f"ok {j['out']}  w={acc['w']} dx={acc['dx']} dy={acc['dy']} registered={acc['fit']['registered']}")
            if a.spec and j.get("cast"):
                add_to_spec(a.spec, j["cast"], j["out"], acc, j)


if __name__ == "__main__":
    main()
