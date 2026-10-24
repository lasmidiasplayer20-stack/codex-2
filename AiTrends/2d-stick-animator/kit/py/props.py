"""How a held prop sits in the hand: its grip point, the end that points away from the hand, and its holding style.

  python props.py grip assets/props/brush.png [--style tool|upright] [--flip]   # estimate, write the sidecar, make a check image
  python props.py show assets/props/brush.png                                   # make the check image from the sidecar

The sidecar <image>.grip.json holds {"grip": [x, y], "tip": [x, y], "style": "tool|upright"} in fractions of the
image (0..1, x right, y down):
  tool     - brushes, knives, swords, pistols, hammers, shovels, torches, pens, spoons, razors, combs: the hand is at
             the grip (the handle) and the prop continues the forearm, so the working end (tip) points where the arm
             points - at the face being brushed, the target being shot.
  upright  - cups, bottles, bread, phones, books, papers, bags, boxes, bouquets: the hand is at the grip and the prop
             stays upright whatever the arm does.
The estimate takes the long axis of the shape: the narrow end is the handle (grip), the wide end is the tip (brush
bristles, hammer head, shovel blade). It is a guess - LOOK at the check image (<image>.grip.png: green = grip/hand,
red = tip) and fix the sidecar or use --flip when the ends are swapped (knife blades and pistols often need it).
compile_spec.py fills in every hold from its sidecar (estimating one if missing), so both renderers hold props
the same way. A hold can still override "grip", "tip", "style" and "rot".
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw


def sidecar(path):
    return path + ".grip.json"


def estimate(path, style=None):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im)[..., 3] > 40
    ys, xs = np.nonzero(a)
    if len(xs) < 20:
        return {"grip": [0.5, 0.6], "tip": [0.5, 0.1], "style": style or "upright", "auto": True}
    pts = np.stack([xs, ys], 1).astype(np.float64)
    c = pts.mean(0)
    cov = np.cov((pts - c).T)
    ev, evec = np.linalg.eigh(cov)
    major = evec[:, 1]
    proj = (pts - c) @ major
    perp = (pts - c) @ evec[:, 0]
    lo, hi = proj.min(), proj.max()
    length = hi - lo
    width = perp.max() - perp.min()
    elong = length / max(1.0, width)
    if style is None:
        style = "tool" if elong > 2.2 else "upright"
    W, H = im.size
    if style == "upright":
        bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
        grip = [(bx0 + bx1) / 2 / W, (by0 + (by1 - by0) * 0.62) / H]
        tip = [(bx0 + bx1) / 2 / W, by0 / H]
        return {"grip": [round(grip[0], 4), round(grip[1], 4)], "tip": [round(tip[0], 4), round(tip[1], 4)], "style": style, "auto": True}

    def end_width(sel):
        q = perp[sel]
        return (q.max() - q.min()) if len(q) else 0.0
    band = 0.22 * length
    w_lo = end_width(proj < lo + band)
    w_hi = end_width(proj > hi - band)
    # the narrow end is the handle
    if w_lo <= w_hi:
        g, t = lo + 0.12 * length, hi - 0.02 * length
    else:
        g, t = hi - 0.12 * length, lo + 0.02 * length

    def on_axis(s):
        sel = np.abs(proj - s) < 0.04 * length
        off = perp[sel].mean() if sel.any() else 0.0
        p = c + major * s + evec[:, 0] * off
        return [round(float(p[0]) / W, 4), round(float(p[1]) / H, 4)]
    return {"grip": on_axis(g), "tip": on_axis(t), "style": style, "auto": True,
            "note": f"estimated: elongation {elong:.1f}, narrow end = handle"}


def load(path, style=None, write=True):
    sc = sidecar(path)
    if os.path.exists(sc):
        try:
            return json.load(open(sc, encoding="utf-8"))
        except Exception:
            pass
    g = estimate(path, style)
    if write:
        try:
            json.dump(g, open(sc, "w", encoding="utf-8"), indent=1)
        except OSError:
            pass
    return g


def check_image(path, g, out=None):
    im = Image.open(path).convert("RGBA")
    W, H = im.size
    bg = Image.new("RGBA", im.size, (70, 74, 80, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    r = max(6, W // 40)
    gx, gy = g["grip"][0] * W, g["grip"][1] * H
    tx, ty = g["tip"][0] * W, g["tip"][1] * H
    d.line([(gx, gy), (tx, ty)], fill=(255, 255, 255, 255), width=max(2, r // 3))
    d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=(40, 220, 60, 255))
    d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=(230, 40, 40, 255))
    d.text((8, 8), f"{g['style']}  green = hand/grip, red = tip", fill=(255, 255, 255, 255))
    out = out or path + ".grip.png"
    bg.convert("RGB").save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("grip"); g.add_argument("image"); g.add_argument("--style", choices=["tool", "upright"]); g.add_argument("--flip", action="store_true")
    s = sp.add_parser("show"); s.add_argument("image")
    a = ap.parse_args()
    if a.cmd == "grip":
        est = estimate(a.image, a.style)
        if a.flip:
            est["grip"], est["tip"] = est["tip"], est["grip"]
            est["note"] = "flipped by hand"
        json.dump(est, open(sidecar(a.image), "w", encoding="utf-8"), indent=1)
        print(json.dumps(est), "->", sidecar(a.image))
        print("check:", check_image(a.image, est))
    else:
        print("check:", check_image(a.image, load(a.image)))


if __name__ == "__main__":
    main()
