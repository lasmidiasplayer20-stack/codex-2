"""Vehicles people ride in (cars, carts, carriages, wagons, boats): riders must SIT on the seat, legs on it, inside.

  python vehicles.py layers P/assets/props/car.png [--seat auto|#b02030] [--hue-tol 0.06] [--faces right|left]
      -> car_back.png   the whole vehicle: the seats and cushions, drawn BEHIND the riders
         car_front.png  the vehicle without its upholstery: doors, body, wheels, steering wheel, drawn IN FRONT
         car.png.vehicle.json   seats found in the picture: hip anchor (back of each cushion) and cushion top
         car_layers.png QA sheet - LOOK at it: red = what sits behind the riders, crosses = seat anchors

A shot's "vehicles" list (compile_spec expands it into the two props and seated, moving riders):
  {"file": "assets/props/car.png", "x": 900, "y": 1573, "w": 1050,           # centre and width, like a prop
   "t": 13.1, "end": 14.6, "dx": 700, "dy": 0,                               # travel over the window (linear)
   "flip": false, "covers": ["car", "drove"],
   "riders": [{"cast": "driver", "seat": -1, "h": 590, "role": "driver", "keys": [...]},   # seat index, -1 = front
              {"cast": "org", "seat": 0, "h": 590, "keys": [...], "wave": [[31.4, 32.1]]}]}
Riders get the sit pose with their thighs along the cushion, knees bent so the shins drop behind the door, hands on
their thighs (the driver's on the wheel) unless their keys set the arms; "wave" raises one arm while they stay seated.
The seats' anchors can be overridden per rider: "hip": [dx_frac, dy_frac] (fractions of the vehicle width from its centre).
"""
import argparse
import colorsys
import json
import os

import numpy as np

SIT_HIP = 0.19          # sit pose: the hips are 0.19 x the character's height above its foot point
SIT_LEGS = {"lF": [84, -112], "lN": [90, -118]}     # thighs along the cushion, shins tucked down behind the door
LAP_ARMS = {"aF": [40, 30], "aN": [35, 35]}
WHEEL_ARMS = {"aF": [72, 12], "aN": [80, 8]}
WAVE_UP, WAVE_MID = [215, 15], [195, 45]


def _paths(img):
    base, ext = os.path.splitext(img)
    return base + "_back.png", base + "_front.png", img + ".vehicle.json", base + "_layers.png"


def _seat_mask(rgba, seat="auto", hue_tol=0.06):
    a = rgba[..., 3] / 255.0
    rgb = rgba[..., :3] / 255.0
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.zeros_like(mx)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    ys, xs = np.where(a > 0.3)
    top, bot = ys.min(), ys.max()
    upper = np.zeros_like(a, bool)
    upper[top: top + int(0.55 * (bot - top)), :] = True
    if seat and seat != "auto":
        h0 = colorsys.rgb_to_hsv(*[int(seat.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])[0]
    else:   # the upholstery: the dominant saturated colour in the upper part of the vehicle
        cand = upper & (a > 0.3) & (sat > 0.35) & (mx > 0.15)
        hist, edges = np.histogram(hue[cand], bins=36, range=(0, 1))
        k = int(hist.argmax())
        h0 = (edges[k] + edges[k + 1]) / 2
    dh = np.minimum(abs(hue - h0), 1 - abs(hue - h0))
    m = (a > 0.3) & (dh < hue_tol) & (((sat > 0.3) & (mx > 0.12)) | ((sat > 0.15) & (mx > 0.5)))
    from PIL import Image, ImageFilter
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    m = np.asarray(im) > 127
    m &= upper           # wheels, running boards and the lower body always stay in front
    return m, (top, bot)


def _components(mask, min_frac=0.02):
    """connected regions of the seat mask (4-neighbour flood fill on a 4x downsampled grid)"""
    small = mask[::4, ::4]
    lab = np.zeros(small.shape, np.int32)
    comps = []
    total = max(1, int(small.sum()))
    for y0, x0 in zip(*np.where(small)):
        if lab[y0, x0]:
            continue
        n = len(comps) + 1
        stack, pts = [(y0, x0)], []
        lab[y0, x0] = n
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < small.shape[0] and 0 <= xx < small.shape[1] and small[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    stack.append((yy, xx))
        if len(pts) >= min_frac * total:
            p = np.array(pts) * 4
            comps.append((p[:, 1].min(), p[:, 1].max(), p[:, 0].min(), p[:, 0].max(), len(pts)))
    return comps


def layers(img, seat="auto", hue_tol=0.06, faces="right"):
    from PIL import Image, ImageDraw
    src = Image.open(img).convert("RGBA")
    rgba = np.asarray(src).astype(np.float32)
    m, _ = _seat_mask(rgba, seat, hue_tol)
    W, H = src.size
    # seats are big regions (a steering-wheel rim or a lamp in the same colour is not a seat): keep only those
    comps = [c for c in _components(m) if (c[1] - c[0]) >= 0.12 * W and (c[3] - c[2]) >= 0.06 * W]
    keep = np.zeros_like(m)
    for x0, x1, y0, y1, n in comps:
        keep[y0:y1 + 4, x0:x1 + 4] = True
    m &= keep
    back, front, side, qa = _paths(img)
    fr = np.asarray(src).copy()
    fr[m, 3] = 0
    Image.fromarray(fr).save(front)
    src.save(back)
    seats = []
    for x0, x1, y0, y1, n in sorted(comps, key=lambda c: c[0]):
        cushion = y1 - 0.35 * (y1 - y0)                       # where a body sits: the lower part of the seat region
        hip_x = x0 + 0.6 * (x1 - x0) if faces == "right" else x1 - 0.6 * (x1 - x0)
        seats.append({"hip": [round((hip_x - W / 2) / W, 4), round((cushion - H / 2) / W, 4)],
                      "box": [int(x0), int(y0), int(x1), int(y1)]})
    if faces == "left":
        seats.reverse()
    json.dump({"faces": faces, "seats": seats, "back": os.path.basename(back), "front": os.path.basename(front)},
              open(side, "w", encoding="utf-8"), indent=1)
    sheet = Image.new("RGBA", (W * 2, H), (60, 64, 70, 255))
    tint = Image.new("RGBA", src.size, (230, 40, 60, 255))
    sheet.paste(src, (0, 0), src)
    sheet.paste(tint, (0, 0), Image.fromarray((m * 160).astype(np.uint8)))
    sheet.paste(Image.fromarray(fr), (W, 0), Image.fromarray(fr))
    d = ImageDraw.Draw(sheet)
    for i, s in enumerate(seats):
        cx, cy = W / 2 + s["hip"][0] * W, H / 2 + s["hip"][1] * W
        d.line((cx - 18, cy, cx + 18, cy), fill=(255, 255, 0, 255), width=4)
        d.line((cx, cy - 18, cx, cy + 18), fill=(255, 255, 0, 255), width=4)
        d.text((cx + 22, cy - 22), f"seat {i}", fill=(255, 255, 0, 255))
    sheet.save(qa)
    print(f"{len(seats)} seat(s) -> {side}\n  back {back}\n  front {front}\n  LOOK at {qa}")
    return json.load(open(side, encoding="utf-8"))


def _side(project, file):
    p = file if os.path.isabs(file) else os.path.join(project or "", file)
    sp = p + ".vehicle.json"
    if not os.path.exists(sp) or not os.path.exists(_paths(p)[1]):
        return layers(p)
    return json.load(open(sp, encoding="utf-8"))


def expand(spec, project=None):
    """compile_spec: every shot's "vehicles" become a back prop, a front prop and the seated, travelling riders"""
    n = 0
    for sh in spec.get("shots", []):
        for v in sh.pop("vehicles", []) or []:
            side = _side(project, v["file"])
            seats = side.get("seats") or [{"hip": [0.0, -0.08]}]
            t0, t1 = float(v.get("t", sh["t"])), float(v.get("end", sh["end"]))
            x, y, w = float(v.get("x", 540)), float(v.get("y", 1500)), float(v.get("w", 900))
            dx, dy = float(v.get("dx", 0)), float(v.get("dy", 0))
            flip = bool(v.get("flip")) != (side.get("faces", "right") == "left")
            d = os.path.dirname(v["file"])
            base = {"x": x, "y": y, "w": w, "t": t0, "end": t1, "pop": False, "flip": flip,
                    "anim": "drift" if (dx or dy) else "none", "dx": dx, "dy": dy,
                    "covers": v.get("covers", ["car", "cars", "drove", "drive", "ride", "rode"])}
            sh.setdefault("props", []).append(dict(base, file=f"{d}/{side['back']}", z="back", shadow=True))
            sh["props"].append(dict(base, file=f"{d}/{side['front']}", z="front", shadow=False, covers=[]))
            face = -1 if flip else 1
            for r in v.get("riders", []):
                si = int(r.get("seat", -1))
                hx, hy = r.get("hip") or seats[si if -len(seats) <= si < len(seats) else -1]["hip"]
                hx = -hx if flip else hx
                h = float(r.get("h", 0.56 * w))
                rx, ry = x + hx * w + face * 0.01 * h, y + hy * w + SIT_HIP * h
                keys = [dict(k) for k in (r.get("keys") or [{"t": t0}])]
                arms = WHEEL_ARMS if r.get("role") == "driver" else LAP_ARMS
                for k in keys:
                    k["pose"] = "sit"
                    st = k.setdefault("set", {})
                    for kk, vv in list(SIT_LEGS.items()) + list(arms.items()):
                        st.setdefault(kk, list(vv))
                for a, b in r.get("wave", []):
                    tt, up = float(a), True
                    while tt < float(b) - 0.05:
                        keys.append({"t": round(tt, 3), "pose": "sit", "dur": 0.14,
                                     "set": dict(SIT_LEGS, aF=WAVE_UP if up else WAVE_MID, aN=arms["aN"]), "covers": ["wave", "waved"]})
                        tt, up = tt + 0.2, not up
                    keys.append({"t": round(float(b), 3), "pose": "sit", "dur": 0.15, "set": dict(SIT_LEGS, **arms)})
                keys.sort(key=lambda k: float(k.get("t", t0)))
                ac = {k: r[k] for k in ("cast", "act", "talk", "state", "states", "hold", "covers") if k in r}
                ac.update({"x": round(rx, 1), "y": round(ry, 1), "h": h, "face": face, "keys": keys, "z": r.get("z", -2),
                           "move": [{"t": t0, "x": round(rx, 1), "y": round(ry, 1)},
                                    {"t": t1, "x": round(rx + dx, 1), "y": round(ry + dy, 1), "ease": "linear", "step": False}]})
                sh.setdefault("actors", []).append(ac)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("layers")
    l.add_argument("image")
    l.add_argument("--seat", default="auto", help="upholstery colour #rrggbb, or auto (the dominant saturated colour up top)")
    l.add_argument("--hue-tol", type=float, default=0.06)
    l.add_argument("--faces", default="right", choices=["right", "left"])
    a = ap.parse_args()
    if a.cmd == "layers":
        layers(a.image, a.seat, a.hue_tol, a.faces)


if __name__ == "__main__":
    main()
