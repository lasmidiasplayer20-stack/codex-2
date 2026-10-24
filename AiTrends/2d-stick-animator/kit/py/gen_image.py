"""Generate backgrounds, props, costume accessories, icons and FX plates with an image model, in the house look.

  python gen_image.py one "an abandoned asylum ward with iron beds" --kind background -o PROJECT/assets/bg/ward.jpg
  python gen_image.py one "green WWII army helmet" --kind accessory -o PROJECT/assets/cast/soldier_helmet.png
  python gen_image.py jobs PROJECT/plan/assets.json [--yes]        # batch (asks before spending credits)
  python gen_image.py prompts PROJECT/plan/assets.json             # only print the final prompts (manual generation)

Providers (--provider): kie (default; KIE_API_KEY) | openai (OPENAI_API_KEY, gpt-image-1)
  kie models: backgrounds -> nano-banana-pro (9:16, 2K) or seedream/4.5-text-to-image;
              cut-outs (prop/accessory/icon) -> gpt-image-2-5-flare at 1K with a real transparent background.
If the kie-media-gen MCP tools are available in the session (kie_submit / kie_wait / kie_download) you may use them
instead with the SAME prompts (print them with `prompts`), then run cutout.py on the downloads.

assets.json: {"style": "photo|painterly|illustrated|3d", "jobs": [
  {"id": "bg_s01", "kind": "background", "prompt": "a rooftop terrace of an office tower at sunset", "out": "assets/bg/rooftop.jpg"},
  {"id": "acc_hair", "kind": "accessory", "prompt": "messy dark brown hair and a thick beard", "out": "assets/cast/hobo_hair.png"},
  {"id": "prop_case", "kind": "prop", "prompt": "a black leather briefcase stuffed with cash", "out": "assets/props/case.png"}]}
Every result is logged in assets/manifest.csv.
"""
import argparse
import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import time

import requests
from PIL import Image

from ra_common import get_key

KIE = "https://api.kie.ai/api/v1"

BG_STYLE = {
    "photo": "Photorealistic cinematic background plate, real location photography look, natural light, slightly desaturated moody colour grade, gentle depth of field",
    "painterly": "Digital matte painting with soft painterly realism, rich atmosphere and moody light",
    "illustrated": "Clean modern illustrated background, simplified shapes, flat soft shading, vector-like detail",
    "3d": "Stylized 3D-rendered environment, soft global illumination, detailed props, animated-film look",
}
TEMPLATES = {
    "background": ("{style}. Scene: {subject}. Completely EMPTY of people, characters and animals. Eye-level camera at standing height "
                   "looking straight into the space, vertical 9:16 composition, the floor/ground clearly visible in the lower third with open "
                   "space where cartoon characters will stand, background detail in the upper two thirds, no text, no signs with words, "
                   "no logos, no watermark."),
    "prop": ("A single {subject}. Detailed cartoon 3D-illustration style like a premium mobile-game asset or a 3D emoji: smooth "
             "rounded forms, soft studio lighting, subtle specular highlights, gentle dark outline. Centered, the whole object visible "
             "with margin, three-quarter view, isolated on a fully transparent background, no ground shadow, no text."),
    "creature": ("A single {subject}: the WHOLE animal from head to tail and feet, seen exactly from the side in profile, facing "
                 "RIGHT, standing naturally on its own feet unless described otherwise, friendly readable silhouette. Style: "
                 "detailed 2D cartoon illustration like a modern animated YouTube Short - clean thin dark outline, cel shading with "
                 "soft highlights, fine fur / feather / skin texture lines, rich but natural colours (the same style as the "
                 "characters' hats, hair and clothes). Not 3D, not glossy, not an emoji, not a photo. Centered with margin, isolated "
                 "on a fully transparent background, nothing else in the image: no ground, no shadow, no text, no other animals, "
                 "no people."),
    "accessory": ("{subject}, made as a standalone costume piece for a cartoon character whose head is a plain round ball: NO head, "
                  "NO face, NO body, NO mannequin - only the item itself, front view, symmetrical, detailed cartoon illustration with soft "
                  "shading and a thin dark outline, centered with margin, isolated on a fully transparent background, no text."),
    "icon": ("A 3D emoji-style icon of {subject}: glossy rounded 3D forms, soft lighting, vivid colours, centered, isolated on a fully "
             "transparent background, no text."),
    "fx": ("{subject}, isolated on a pure black background (#000000) so it can be screen-blended, realistic VFX element, high "
           "dynamic range, nothing else in frame, no text."),
    "insert": ("Cinematic still photograph: {subject}. Vertical 9:16, realistic, dramatic lighting, film grain, no text, no watermark."),
    "raw": "{subject}",
}
TRANSPARENT = {"prop", "accessory", "icon", "creature"}


def build_prompt(kind, subject, style="photo", world=None):
    t = TEMPLATES.get(kind, "{subject}")
    if kind == "background" and world:
        r = float(world[0]) / float(world[1])
        if r > 0.9:      # a wide location the characters walk across and the camera pans over
            t = t.replace("vertical 9:16 composition", "wide panoramic composition of a long continuous space that characters "
                          "can walk across from one side to the other, the same eye-level ground line all the way along")
        elif max(world) > 2100:   # a big/tall location: room to climb, fall or rise
            t = t.replace("vertical 9:16 composition", "tall vertical composition with a lot of vertical space (stairs, walls, "
                          "height) that characters can climb or fall through")
    return t.format(subject=subject.rstrip("."), style=BG_STYLE.get(style, BG_STYLE["photo"]))


# ----------------------------------------------------------------------------- providers
def kie_call(method, path, key, payload=None):
    for i in range(5):
        try:
            r = requests.request(method, KIE + path, json=payload, timeout=60,
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        except requests.RequestException:
            time.sleep(3 + 3 * i)
            continue
        if r.status_code == 401:
            sys.exit("Kie.ai rejected the key (401)")
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(5 + 5 * i)
            continue
        return r.json()
    raise RuntimeError("Kie.ai: no answer")


def upload_ref(key, path):
    """upload a local picture so image-to-image jobs can use it as a reference ("refs": [url])"""
    body = {"base64Data": "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode(),
            "uploadPath": "2d-stick-animator/refs", "fileName": f"ref_{int(time.time() * 1000)}.png"}
    for i in range(4):
        try:
            r = requests.post("https://kieai.redpandaai.co/api/file-base64-upload", json=body, timeout=120,
                              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            d = r.json()
            if d.get("success"):
                return d["data"]["downloadUrl"]
        except (requests.RequestException, ValueError):
            pass
        time.sleep(4 + 4 * i)
    raise RuntimeError("reference upload failed")


ASPECTS = ["9:16", "2:3", "3:4", "4:5", "1:1", "5:4", "4:3", "3:2", "16:9", "21:9"]


def aspect_for(world):
    """closest image aspect for a scene size [W, H] (a 9:16 frame, or a wider/taller location world)"""
    if not world:
        return "9:16"
    r = float(world[0]) / float(world[1])
    return min(ASPECTS, key=lambda a: abs(__import__("math").log((int(a.split(":")[0]) / int(a.split(":")[1])) / r)))


def bg_size(world):
    """pixel size of a finished background: 1.2x the scene so camera moves stay sharp, long side capped at 5600"""
    W, H = (world or (1080, 1920))
    k = min(1.2, 5600.0 / max(W, H))
    return int(W * k), int(H * k)


def kie_submit(key, kind, prompt, model=None, refs=None, world=None):
    if kind in TRANSPARENT:
        model = model or "gpt-image-2-5-flare"
    else:
        model = model or "nano-banana-pro"
    if model.startswith("gpt-image-2-5"):
        mid = model + ("-image-to-image" if refs else "-text-to-image")
        inp = {"prompt": prompt, "aspect_ratio": "1:1" if kind in TRANSPARENT else "9:16", "resolution": "1K",
               "background": "transparent" if kind in TRANSPARENT else "opaque"}
        if refs:
            inp["input_urls"] = refs[:16]
    elif model.startswith("nano-banana"):
        mid = model
        inp = {"prompt": prompt, "image_input": refs or [], "aspect_ratio": "1:1" if kind in TRANSPARENT else aspect_for(world),
               "resolution": "4K" if (world and kind not in TRANSPARENT and max(world) > 2100) else "2K", "output_format": "png"}
    elif model.startswith("seedream"):
        mid = model
        inp = {"prompt": prompt, "aspect_ratio": "1:1" if kind in TRANSPARENT else aspect_for(world), "quality": "high", "nsfw_checker": False}
    else:
        mid = model
        inp = {"prompt": prompt, "aspect_ratio": "9:16"}
    r = kie_call("POST", "/jobs/createTask", key, {"model": mid, "input": inp})
    if r.get("code") != 200:
        raise RuntimeError(f"Kie createTask failed: {r.get('msg')}")
    return r["data"]["taskId"], mid


def kie_wait(key, task, timeout=900):
    t0, delay = time.time(), 5
    while time.time() - t0 < timeout:
        time.sleep(delay)
        delay = min(15, delay + 2)
        d = kie_call("GET", "/jobs/recordInfo?taskId=" + task, key).get("data") or {}
        st = d.get("state")
        if st == "success":
            raw = d.get("resultJson") or "{}"
            res = json.loads(raw) if isinstance(raw, str) else raw
            return (res.get("resultUrls") or res.get("result_urls") or [None])[0]
        if st == "fail":
            raise RuntimeError(f"Kie task failed: {d.get('failCode')} {d.get('failMsg')}")
    raise RuntimeError("Kie task timed out")


def openai_generate(kind, prompt):
    key = get_key("openai")
    body = {"model": "gpt-image-1", "prompt": prompt, "size": "1024x1024" if kind in TRANSPARENT else "1024x1536",
            "quality": "high", "background": "transparent" if kind in TRANSPARENT else "opaque", "n": 1}
    r = requests.post("https://api.openai.com/v1/images/generations", json=body, timeout=300,
                      headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI images failed {r.status_code}: {r.text[:300]}")
    return base64.b64decode(r.json()["data"][0]["b64_json"])


# ----------------------------------------------------------------------------- post-processing
def finish(img_bytes, kind, out, world=None):
    im = Image.open(io.BytesIO(img_bytes))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if kind in TRANSPARENT:
        im = im.convert("RGBA")
        try:    # some generations paint a checkerboard instead of real transparency
            import numpy as np
            from costume import remove_fake_transparency
            im = Image.fromarray(remove_fake_transparency(np.array(im).astype("float32")).clip(0, 255).astype("uint8"), "RGBA")
        except Exception:
            pass
        a = im.getchannel("A")
        if a.getextrema()[0] > 250:   # no real transparency -> cut it out
            tmp = os.path.join(tempfile.gettempdir(), f"ra_raw_{os.getpid()}_{os.path.basename(out)}")
            im.save(tmp)
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cutout.py"), tmp, "-o", out], check=False)
            try:
                os.remove(tmp)
            except OSError:
                pass
            return out
        bbox = a.getbbox()
        if bbox:
            im = im.crop(bbox)
        pad = int(max(im.size) * 0.04)
        canvas = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad))
        canvas.save(out if out.endswith(".png") else os.path.splitext(out)[0] + ".png")
    else:
        im = im.convert("RGB")
        W, H = bg_size(world)   # 1.2x the frame (or the location's world) so camera moves stay sharp
        k = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
        x0, y0 = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((x0, y0, x0 + W, y0 + H))
        if out.lower().endswith(".png"):
            im.save(out)
        else:
            im.save(out, quality=93)
    return out


def manifest(out, provider, model, prompt):
    sys.path.insert(0, os.path.dirname(__file__))
    from fetch_assets import manifest_add
    manifest_add(os.path.dirname(out), {"file": out, "kind": "generated", "source": f"{provider} {model}", "url": "",
                                        "licence": "generated for this project", "author": "image model", "query": prompt[:200]})


def run_job(j, provider, style, model=None):
    prompt = build_prompt(j.get("kind", "prop"), j["prompt"], j.get("style", style), j.get("world"))
    out = j["out"]
    if provider == "openai":
        data = openai_generate(j.get("kind", "prop"), prompt)
        mid = "gpt-image-1"
    else:
        key = get_key("kie")
        task, mid = kie_submit(key, j.get("kind", "prop"), prompt, j.get("model") or model, j.get("refs"), j.get("world"))
        url = kie_wait(key, task)
        data = requests.get(url, timeout=180).content
    finish(data, j.get("kind", "prop"), out, j.get("world"))
    manifest(out, provider, mid, prompt)
    print("ok  ", out)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    o = sp.add_parser("one"); o.add_argument("prompt"); o.add_argument("-o", "--out", required=True)
    o.add_argument("--kind", default="prop", choices=sorted(TEMPLATES)); o.add_argument("--style", default="photo")
    o.add_argument("--provider", default="kie", choices=["kie", "openai"]); o.add_argument("--model")
    o.add_argument("--world", help="background for a wide/tall location, scene size WxH, e.g. 3400x1920")
    j = sp.add_parser("jobs"); j.add_argument("file"); j.add_argument("--provider", default="kie", choices=["kie", "openai"])
    j.add_argument("--model"); j.add_argument("--yes", action="store_true"); j.add_argument("--only", default="")
    j.add_argument("--workers", type=int, default=6)
    p = sp.add_parser("prompts"); p.add_argument("file")
    a = ap.parse_args()
    if a.cmd == "one":
        wl = [int(v) for v in a.world.lower().split("x")] if a.world else None
        run_job({"kind": a.kind, "prompt": a.prompt, "out": a.out, "world": wl}, a.provider, a.style, a.model)
        return
    d = json.load(open(a.file, encoding="utf-8"))
    base = os.path.dirname(os.path.dirname(os.path.abspath(a.file)))   # PROJECT (file lives in PROJECT/plan)
    style = d.get("style", "photo")
    jobs = d["jobs"]
    if a.cmd == "prompts":
        for x in jobs:
            print(f"[{x['id']}] ({x.get('kind')}) -> {x['out']}\n{build_prompt(x.get('kind', 'prop'), x['prompt'], x.get('style', style))}\n")
        return
    only = set(x for x in a.only.split(",") if x)
    todo = [x for x in jobs if (not only or x["id"] in only) and not os.path.exists(os.path.join(base, x["out"]))]
    print(f"{len(todo)} image job(s) to generate with {a.provider} (existing files are skipped). They cost credits.")
    if not a.yes:
        sys.exit("re-run with --yes after the user agrees to the cost")
    from concurrent.futures import ThreadPoolExecutor

    def one(x):
        x = dict(x)
        x["out"] = os.path.join(base, x["out"])
        try:
            run_job(x, a.provider, style, a.model)
        except Exception as e:
            print("FAIL", x["id"], e)

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        list(ex.map(one, todo))


if __name__ == "__main__":
    main()
