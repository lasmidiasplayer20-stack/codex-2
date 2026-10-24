"""Cut an object out of its background, trim and pad it (for props, accessories and icons).

  python cutout.py in.png -o out.png [--method auto|rembg|key] [--tol 28] [--outline 0] [--border 0]

auto: use rembg (U2Net) when installed (pip install rembg onnxruntime), otherwise key out the background colour
      sampled at the image border with a flood fill (works for plain/studio backgrounds from image models).
--outline N  adds an N-px dark outline (matches the characters' ink line)   --border N adds a white sticker rim
"""
import argparse
from collections import deque

import numpy as np
from PIL import Image, ImageFilter


def key_out(im, tol):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, 0)
    diff = np.abs(a - bg).max(-1)
    cand = diff <= tol
    mask = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not mask[y, x]:
                mask[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not mask[y, x]:
                mask[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True; q.append((ny, nx))
    alpha = Image.fromarray(((~mask) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--method", default="auto")
    ap.add_argument("--tol", type=int, default=28)
    ap.add_argument("--outline", type=int, default=0)
    ap.add_argument("--border", type=int, default=0)
    a = ap.parse_args()
    im = Image.open(a.inp).convert("RGBA")
    if im.getchannel("A").getextrema()[0] < 250 and a.method == "auto":
        out = im
    elif a.method in ("auto", "rembg"):
        try:
            from rembg import remove
            out = remove(im)
        except Exception:
            if a.method == "rembg":
                raise
            out = key_out(im, a.tol)
    else:
        out = key_out(im, a.tol)
    bbox = out.getchannel("A").getbbox()
    if bbox:
        out = out.crop(bbox)
    pad = max(a.outline, a.border) + int(max(out.size) * 0.04)
    canvas = Image.new("RGBA", (out.width + 2 * pad, out.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(out, (pad, pad), out)
    for width, col in ((a.border, (255, 255, 255, 255)), (a.outline, (18, 18, 18, 255))):
        if width > 0:
            al = canvas.getchannel("A").filter(ImageFilter.MaxFilter(width * 2 + 1))
            rim = Image.new("RGBA", canvas.size, col)
            rim.putalpha(al)
            rim.alpha_composite(canvas)
            canvas = rim
    canvas.save(a.out)
    print("cut out ->", a.out, canvas.size)


if __name__ == "__main__":
    main()
