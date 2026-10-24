"""Get every asset a video needs - generated with Kie.ai or from free sources only, as the user chose.

  python assets.py mode PROJECT                 # show the project's asset mode
  python assets.py mode PROJECT kie|free        # set it (plan/assets_mode.txt) - ask the user which they want
  python assets.py get PROJECT [--yes] [--only id1,id2] [--workers 6]   # fulfil plan/asset_list.json
  python assets.py check PROJECT                # which listed files exist / are missing

Modes
  kie   backgrounds: Nano Banana Pro (9:16, 2K) | props & icons: GPT Image 2.5 with a real transparent background |
        costumes: GPT Image 2.5 drawn on the rig template (costume.py) | emoji icons still come from the bundled
        3D-emoji library when one fits. Costs Kie.ai credits (KIE_API_KEY, keys.py) - `get` asks for --yes.
  free  icons: bundled Fluent 3D emoji (MIT) | backgrounds: Openverse + Wikimedia Commons (+ Pexels/Pixabay with
        free keys) | props: emoji library, else Openverse PNGs cut out of their background | costumes: the bundled
        costume library (costume.py library), recoloured | video inserts: Pexels/Pixabay keys or archive.org.
        No paid service is ever called.

plan/asset_list.json (written while planning, one entry per file the spec references):
  {"items": [
    {"id": "bg_street", "kind": "background", "describe": "dark old city street at dusk, stone doors", "search": "old street night door", "out": "assets/bg/street.jpg"},
    {"id": "bg_road", "kind": "background", "world": [3400, 1920], "describe": "a long empty country road ...", "out": "assets/bg/road.jpg"},
    {"id": "prop_box", "kind": "prop", "describe": "large open cardboard box seen from the front", "search": "cardboard box", "out": "assets/props/box.png"},
    {"id": "rat", "kind": "icon", "emoji": "rat", "out": "assets/icons/rat.png"},
    {"id": "hobo_head", "kind": "costume", "cast": "hobo", "piece": "head", "describe": "worn beige beanie and bushy brown beard",
     "library": ["hat_beanie_worn", "beard_full_brown"], "tint": {"beard_full_brown": "#5A3A22"}, "out": "assets/cast/hobo_head.png"},
    {"id": "hen", "kind": "creature", "animal": "chicken", "describe": "a plump brown farm hen", "out": "assets/creatures/hen.png"},
    {"id": "dog", "kind": "creature", "animal": "dog", "describe": "a scrappy brown-and-white farm dog running", "gait": "run",
     "out": "assets/creatures/dog.png"},     # "gait": run|walk|hop|fly|two_legs for every animal that moves on screen (kie)
    {"id": "hens_sfx", "kind": "sound", "describe": "several hens clucking calmly in a farmyard", "search": "chickens clucking", "dur": 4, "out": "audio/sfx/hens.wav"},
    {"id": "war", "kind": "video", "search": "world war two soldiers", "out": "assets/video/war.mp4"}]}
Costume entries are added to the cast's accessories in plan/spec.json (kie: the generated piece; free: each
library piece). Every file is logged in assets/manifest.csv with its source and licence.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_common import KIT, get_key  # noqa: E402

ICONS = os.path.join(KIT, "assets", "icons")
ICON_MAP = os.path.join(KIT, "data", "icon_map.json")


def item_done(P, it, mode):
    """a free-mode costume made of library pieces is done when every piece file exists (they are placed separately)"""
    if it.get("kind") == "costume" and mode == "free" and it.get("library"):
        return all(os.path.exists(os.path.join(P, f"assets/cast/{it['cast']}_{pid}.png")) for pid in it["library"])
    return os.path.exists(os.path.join(P, it["out"]))


def mode_file(P):
    return os.path.join(P, "plan", "assets_mode.txt")


def get_mode(P):
    try:
        m = open(mode_file(P), encoding="utf-8").read().strip()
        return m if m in ("kie", "free") else None
    except OSError:
        return None


# ----------------------------------------------------------------------------------------------- icons (both modes)
def find_emoji(name):
    """Bundled Fluent 3D emoji by file name or icon_map keyword."""
    if not name:
        return None
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    p = os.path.join(ICONS, key + ".png")
    if os.path.exists(p):
        return p
    try:
        m = json.load(open(ICON_MAP, encoding="utf-8"))
        for k in (name.lower(), key, key.rstrip("s")):
            if k in m and m[k]:
                q = os.path.join(ICONS, m[k][0] + ".png")
                if os.path.exists(q):
                    return q
    except Exception:
        pass
    cands = [f for f in os.listdir(ICONS) if f.endswith(".png") and key in f] if os.path.isdir(ICONS) else []
    return os.path.join(ICONS, sorted(cands, key=len)[0]) if cands else None


def log(P, out, kind, source, url="", licence="", author="", query=""):
    from fetch_assets import manifest_add
    manifest_add(os.path.join(P, "assets"), {"file": out, "kind": kind, "source": source, "url": url, "licence": licence,
                                             "author": author, "query": query})


# ----------------------------------------------------------------------------------------------- free sources
def openverse(query, n=12, tall=None, ext=None):
    from fetch_assets import http_get
    params = {"q": query, "page_size": n, "license_type": "commercial"}
    if tall is not None:
        params["aspect_ratio"] = "tall" if tall else "wide"
    if ext:
        params["extension"] = ext
    r = http_get("https://api.openverse.org/v1/images/", params=params)
    r.raise_for_status()
    return [{"url": it.get("url"), "w": it.get("width") or 0, "h": it.get("height") or 0, "src": "Openverse/" + str(it.get("source")),
             "page": it.get("foreign_landing_url"), "lic": f"{it.get('license')} {it.get('license_version') or ''}".strip(),
             "author": it.get("creator", "")} for it in r.json().get("results", [])]


def commons(query, n=12):
    import re
    from fetch_assets import http_get
    r = http_get("https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "format": "json", "generator": "search", "gsrsearch": query + " filetype:bitmap", "gsrnamespace": 6,
        "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 2000})
    r.raise_for_status()
    out = []
    for p in ((r.json().get("query") or {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        lic = (md.get("LicenseShortName") or {}).get("value", "?")
        if "NC" in lic.upper() or ii.get("mime", "").endswith("svg+xml"):
            continue
        out.append({"url": ii.get("thumburl") or ii.get("url"), "w": ii.get("width", 0), "h": ii.get("height", 0), "src": "Wikimedia Commons",
                    "page": ii.get("descriptionurl"), "lic": lic, "author": re.sub(r"<[^>]+>", "", (md.get("Artist") or {}).get("value", ""))[:80]})
    return out


def pexels_photos(query, n=10, wide=False):
    import requests
    key = get_key("pexels", required=False)
    if not key:
        return []
    r = requests.get("https://api.pexels.com/v1/search", params={"query": query, "per_page": n, "orientation": "landscape" if wide else "portrait"},
                     headers={"Authorization": key}, timeout=60)
    return [{"url": p["src"]["original"], "w": p["width"], "h": p["height"], "src": "Pexels", "page": p["url"],
             "lic": "Pexels licence", "author": p.get("photographer", "")} for p in r.json().get("photos", [])]


def fetch_best(cands, out, min_w=900, prefer_tall=True):
    from fetch_assets import download
    good = [c for c in cands if c.get("url") and (c["w"] or 0) >= min_w]
    if prefer_tall:
        good.sort(key=lambda c: (-(c["h"] >= c["w"] * 0.9), -(c["w"] * c["h"])))
    else:
        good.sort(key=lambda c: -(c["w"] * c["h"]))
    for c in good[:6]:
        tmp = out + ".dl"
        try:
            download(c["url"], tmp)
            from PIL import Image
            Image.open(tmp).verify()
            return tmp, c
        except Exception:
            continue
    return None, None


def finish_background(src, out, world=None):
    from PIL import Image
    from gen_image import bg_size
    im = Image.open(src).convert("RGB")
    W, H = bg_size(world)
    k = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    im.crop((x0, y0, x0 + W, y0 + H)).save(out, quality=93)


def free_background(P, it, out):
    q = it.get("search") or it.get("describe")
    world = it.get("world")
    wide = bool(world) and float(world[0]) / float(world[1]) > 0.9
    cands = pexels_photos(q, wide=wide) + openverse(q, tall=not wide) + openverse(q) + commons(q)
    tmp, c = fetch_best(cands, out, min_w=1600 if wide else 900, prefer_tall=not wide)
    if not tmp:
        return f"no free image found for {q!r} - try other search words"
    finish_background(tmp, out, world)
    os.remove(tmp) if os.path.exists(tmp) else None
    log(P, out, "background", c["src"], c.get("page") or c["url"], c["lic"], c.get("author", ""), q)
    return None


def free_prop(P, it, out):
    e = find_emoji(it.get("emoji") or it.get("search") or it.get("id"))
    if e and (it.get("emoji") or not it.get("search")):
        shutil.copyfile(e, out)
        log(P, out, "icon", "Fluent UI Emoji 3D (Microsoft)", "https://github.com/microsoft/fluentui-emoji", "MIT", "Microsoft", it.get("emoji", ""))
        return None
    q = it.get("search") or it.get("describe")
    cands = openverse(q + " png", ext="png") + openverse(q + " isolated") + commons(q + " isolated")
    tmp, c = fetch_best(cands, out, min_w=400, prefer_tall=False)
    if not tmp:
        if e:
            shutil.copyfile(e, out)
            log(P, out, "icon", "Fluent UI Emoji 3D (Microsoft)", "https://github.com/microsoft/fluentui-emoji", "MIT", "Microsoft", q)
            return None
        return f"no free image found for {q!r}"
    from PIL import Image
    im = Image.open(tmp).convert("RGBA")
    if im.getchannel("A").getextrema()[0] > 250:       # opaque: cut it out of its background
        subprocess.run([sys.executable, os.path.join(KIT, "py", "cutout.py"), tmp, "-o", out], check=False, capture_output=True)
    else:
        bbox = im.getchannel("A").getbbox()
        (im.crop(bbox) if bbox else im).save(out)
    os.remove(tmp) if os.path.exists(tmp) else None
    log(P, out, "prop", c["src"], c.get("page") or c["url"], c["lic"], c.get("author", ""), q)
    return None


def get_creature(P, it, out, mode):
    """a living animal, whole body in side view: generated (kie: GPT Image 2.5 facing right) or the Fluent 3D full-body
    emoji (free: they face left), else a searched cut-out; trimmed so its bottom edge is the feet line"""
    import creatures as CR
    animal = CR.animal_of(it.get("animal") or it.get("id")) or CR.animal_of((it.get("search") or "").split(" ")[-1])
    if mode == "kie" and not it.get("emoji"):
        import gen_image as G
        G.run_job({"kind": "creature", "prompt": it.get("describe") or animal or it["id"], "out": out, "style": "3d"}, "kie", "3d")
        CR.prep(out, it.get("faces", "right"))
        log(P, out, "creature", "Kie.ai GPT Image 2.5", "", "generated for this project", "", (it.get("describe") or "")[:120])
        if it.get("gait"):          # an animal that moves on screen: its gait cycle (same animal, legs in sequence)
            for f in CR.make_gait(out, it["gait"] if it["gait"] in CR.GAITS else "run", int(it.get("gait_frames", 4))):
                log(P, f, "creature gait", "Kie.ai GPT Image 2.5 (image-to-image)", "", "generated for this project", "", it["gait"])
        return None
    import fetch_assets as FA
    name = it.get("emoji") or (CR.ANIMALS.get(animal) or {}).get("emoji")
    if name and FA.fluent_emoji(name, out):
        CR.prep(out, "left")
        return None
    q = it.get("search") or it.get("describe") or animal or it["id"]
    err = free_prop(P, dict(it, emoji=None, search=q + " side view"), out)
    if err:
        return err
    CR.prep(out, it.get("faces", "right"))
    return "found a searched cut-out - LOOK at it: whole body, side view; set \"faces\" if it looks left"


def get_sound(P, it, out, mode):
    """a sound effect (animal sounds, crowds, machines): ElevenLabs (the user's key) in kie mode, Wikimedia Commons
    recordings in free mode (and as the kie fallback)"""
    import fetch_assets as FA
    src = it.get("source") or ("eleven" if mode == "kie" and get_key("elevenlabs", required=False) else "commons")
    dur = float(it.get("dur", 4.0))
    if src == "eleven":
        r = subprocess.run([sys.executable, os.path.join(KIT, "py", "eleven.py"), "sfx", it.get("describe") or it.get("search"),
                            "-o", out, "--dur", str(dur)], capture_output=True, text=True)
        if r.returncode == 0:
            log(P, out, "sound", "ElevenLabs sound effects", "", "generated for this project", "", (it.get("describe") or "")[:120])
            return None
        if mode != "kie":
            return r.stderr[-300:]
    err = FA.commons_sound(it.get("search") or it.get("describe"), out, dur)
    if err and src != "eleven" and mode == "kie" and get_key("elevenlabs", required=False):
        return get_sound(P, dict(it, source="eleven"), out, mode)
    return err


def free_costume(P, it, out):
    import costume as C
    idx = {p["id"]: p for p in C.library_index()["pieces"]}
    if not idx:
        return "the costume library is not installed (python install_kit.py, or copy the plugin kit again)"
    pieces = it.get("library") or []
    if not pieces:
        return "free mode needs 'library' piece ids for costumes (python costume.py library)"
    spec = os.path.join(P, "plan", "spec.json")
    for pid in pieces:
        if pid not in idx:
            return f"no library piece {pid!r}"
        p = idx[pid]
        rel = f"assets/cast/{it['cast']}_{pid}.png"
        dst = os.path.join(P, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tint = (it.get("tint") or {}).get(pid)
        if tint:
            C.tint_image(os.path.join(C.LIB, p["file"]), dst, tint)
        else:
            shutil.copyfile(os.path.join(C.LIB, p["file"]), dst)
        if os.path.exists(spec):
            C.add_to_spec(spec, it["cast"], rel, p, it)
        log(P, dst, "costume", "2D Stick Animator costume library", "", "bundled with the plugin", "", pid)
    return None


def free_video(P, it, out):
    q = it.get("search") or it.get("describe")
    d = os.path.dirname(out)
    for src in (["pexels", q, "--video", "--portrait"], ["pixabay", q, "--video"], ["archive", q]):
        if src[0] in ("pexels", "pixabay") and not get_key(src[0], required=False):
            continue
        before = set(os.listdir(d)) if os.path.isdir(d) else set()
        subprocess.run([sys.executable, os.path.join(KIT, "py", "fetch_assets.py")] + src + ["-o", d, "--n", "1"], capture_output=True)
        new = sorted(set(os.listdir(d)) - before) if os.path.isdir(d) else []
        vids = [f for f in new if f.lower().endswith((".mp4", ".mov", ".webm"))]
        if vids:
            shutil.move(os.path.join(d, vids[0]), out)
            return None
    return f"no free video found for {q!r}"


# ----------------------------------------------------------------------------------------------- Kie.ai
def kie_item(P, it, out):
    kind = it["kind"]
    if kind == "icon" or (kind == "prop" and it.get("emoji") and not it.get("generate")):
        e = find_emoji(it.get("emoji") or it.get("id"))
        if e:
            shutil.copyfile(e, out)
            log(P, out, "icon", "Fluent UI Emoji 3D (Microsoft)", "https://github.com/microsoft/fluentui-emoji", "MIT", "Microsoft", it.get("emoji", ""))
            return None
    if kind == "costume":
        import costume as C
        acc = C.make_piece(get_key("kie"), it.get("piece", "head"), it["describe"], out, it.get("extra"))
        spec = os.path.join(P, "plan", "spec.json")
        if os.path.exists(spec) and it.get("cast"):
            C.add_to_spec(spec, it["cast"], os.path.relpath(out, P).replace("\\", "/"), acc, it)
        log(P, out, "costume", "Kie.ai GPT Image 2.5 (rig template)", "", "generated for this project", "", it["describe"][:120])
        return None
    if kind == "video":
        return free_video(P, it, out) if not it.get("generate") else "video generation: use gen_video.py"
    if kind == "creature":
        return get_creature(P, it, out, "kie")
    if kind == "sound":
        return get_sound(P, it, out, "kie")
    import gen_image as G
    G.run_job({"kind": "background" if kind == "background" else ("icon" if kind == "icon" else "prop"),
               "prompt": it["describe"], "out": out, "style": it.get("style", "3d"), "model": it.get("model"),
               "world": it.get("world") if kind == "background" else None}, "kie", it.get("style", "3d"))
    return None


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("mode"); m.add_argument("project"); m.add_argument("value", nargs="?", choices=["kie", "free"])
    g = sp.add_parser("get"); g.add_argument("project"); g.add_argument("--yes", action="store_true"); g.add_argument("--only", default="")
    g.add_argument("--workers", type=int, default=6); g.add_argument("--force", action="store_true")
    c = sp.add_parser("check"); c.add_argument("project")
    a = ap.parse_args()
    P = a.project
    if a.cmd == "mode":
        if a.value:
            os.makedirs(os.path.join(P, "plan"), exist_ok=True)
            open(mode_file(P), "w", encoding="utf-8").write(a.value + "\n")
        mo = get_mode(P)
        print(f"asset mode: {mo or 'not set'}" + ("" if mo else "  (ask the user: Kie.ai generation or free sources only)"))
        if mo == "kie":
            print("Kie.ai key:", "yes" if get_key("kie", required=False) else "MISSING - python keys.py set kie <key>")
        return
    lst = json.load(open(os.path.join(P, "plan", "asset_list.json"), encoding="utf-8"))["items"]
    if a.cmd == "check":
        for it in lst:
            print(f"{'ok ' if item_done(P, it, get_mode(P)) else '-- '} {it['kind']:10s} {it['out']}")
        return
    mode = get_mode(P)
    if not mode:
        sys.exit("set the asset mode first: python assets.py mode PROJECT kie|free (ask the user)")
    only = set(x for x in a.only.split(",") if x)
    todo = [it for it in lst if (not only or it["id"] in only) and (a.force or not item_done(P, it, mode))]
    if mode == "kie":
        paid = [it for it in todo if not (it["kind"] == "icon" and find_emoji(it.get("emoji") or it.get("id")))
                and not (it["kind"] == "video" and not it.get("generate"))
                and not (it["kind"] == "creature" and it.get("emoji"))
                and not (it["kind"] == "sound" and (it.get("source") == "commons" or not get_key("elevenlabs", required=False)))]
        if paid and not a.yes:
            gaits = sum(int(it.get("gait_frames", 4)) for it in paid if it["kind"] == "creature" and it.get("gait"))
            print(f"{len(paid)} item(s) will be generated with Kie.ai (about 4-6 credits per image, ~20 per Nano Banana Pro "
                  f"background) or ElevenLabs (sound effects use the user's ElevenLabs credits)"
                  + (f", plus {gaits} gait frame(s) for moving animals (~6 credits each)" if gaits else "")
                  + ". Re-run with --yes after the user agrees.")
            for it in paid:
                print(f"  {it['kind']:10s} {it['out']}: {it.get('describe', '')[:90]}")
            return

    def run(it):
        out = os.path.join(P, it["out"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        try:
            if mode == "kie":
                err = kie_item(P, it, out)
            else:
                if it["kind"] == "creature":
                    err = get_creature(P, it, out, "free")
                elif it["kind"] == "sound":
                    err = get_sound(P, it, out, "free")
                else:
                    err = {"background": free_background, "prop": free_prop, "icon": free_prop, "costume": free_costume,
                           "video": free_video}.get(it["kind"], free_prop)(P, it, out)
        except Exception as e:
            err = str(e)
        return it, err

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        for it, err in ex.map(run, todo):
            print(("FAILED " + it["id"] + ": " + err) if err else ("ok     " + it["out"]))


if __name__ == "__main__":
    main()
