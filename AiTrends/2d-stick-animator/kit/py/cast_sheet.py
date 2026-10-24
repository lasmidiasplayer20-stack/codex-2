"""Render the cast for approval: every character in a few poses and faces, with costumes and accessories.

  python cast_sheet.py PROJECT [--spec plan/spec.json] [--poses stand,point_fwd,cheer,sit] [-o qc/cast_sheet.png]

Use it after designing spec.cast (colours, parts, accessories): check that image accessories (hair, hats, beards)
sit on the head (tune w, dx, dy, rot in units of the head diameter), that every character has its own colour and
silhouette, and that faces read at phone size. Show the sheet to the user before building the video.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw

import ra_rig as R


def straight(arr):
    a = np.clip(arr, 0, 1)
    al = a[..., 3:4]
    rgb = np.where(al > 0, a[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray((np.concatenate([rgb, al], -1) * 255).astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec.json")
    ap.add_argument("--poses", default="stand,point_fwd,cheer,hands_hips")
    ap.add_argument("--faces", default="normal/none,angry/open,wide/scream,happy/grin")
    ap.add_argument("-o", "--out", default="qc/cast_sheet.png")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.project, a.spec), encoding="utf-8"))
    cast = spec.get("cast", {})
    poses = a.poses.split(",")
    faces = [f.split("/") for f in a.faces.split(",")]
    cw, ch = 300, 420
    sheet = Image.new("RGB", (cw * len(poses), ch * max(1, len(cast))), (64, 68, 74))
    d = ImageDraw.Draw(sheet)
    for r, (cid, c) in enumerate(cast.items()):
        for i, p in enumerate(poses):
            e, m = faces[i % len(faces)]
            arr, (ox, oy) = R.render_character(c, R.pose_params(p), 0.2, {"eyes": e, "mouth": m}, 0.32, a.project)
            im = straight(arr)
            sheet.paste(im, (i * cw + cw // 2 - int(ox), r * ch + ch - 30 - int(oy)), im)
            d.text((i * cw + 6, r * ch + 4), f"{cid}: {p} {e}/{m}", fill=(255, 240, 0))
    out = os.path.join(a.project, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print("cast sheet ->", out)


if __name__ == "__main__":
    main()
