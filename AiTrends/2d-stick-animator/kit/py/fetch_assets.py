"""Find and download free assets from online sources, logging the licence of every file.

  python fetch_assets.py emoji "skull and crossbones" rat "money with wings" -o PROJECT/assets/icons
  python fetch_assets.py commons "Paris street 1925" -o PROJECT/assets/bg --n 6 [--portrait]
  python fetch_assets.py openverse "abandoned asylum corridor" -o PROJECT/assets/bg --n 6
  python fetch_assets.py pexels "traffic jam aerial" --video -o PROJECT/assets/video --n 4      (PEXELS_API_KEY)
  python fetch_assets.py pixabay "fire on black background" --video -o PROJECT/assets/fx --n 4 (PIXABAY_API_KEY)
  python fetch_assets.py archive "world war ii beach landing" -o PROJECT/assets/video --n 3     (public-domain films)
  python fetch_assets.py url https://... -o PROJECT/assets/props --name crate.png --licence "CC0" --source "..."
  python fetch_assets.py sound "chickens clucking" -o PROJECT/audio/sfx/hens.wav --dur 4      (Wikimedia Commons recordings)

Every download is appended to PROJECT/assets/manifest.csv (file, kind, source, url, licence, author, query) so the
credits can go in the video description. Sources and licences:
  * Fluent UI Emoji 3D (Microsoft, MIT) - the 3D-emoji look of the samples' icons (skull, rat, calendar, crown...)
  * Wikimedia Commons / Openverse - check each licence (CC0/PD free; CC BY needs credit; avoid NC for monetised)
  * Pexels / Pixabay - free licences, no attribution required (keys are free)
  * archive.org - public-domain newsreels and films for B&W historical inserts
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys
import urllib.parse

import requests

from ra_common import get_key

UA = {"User-Agent": "2DStickAnimator/2.0 (faceless video production; contact: local user)"}


def http_get(url, **kw):
    """GET with polite retries on 429/5xx (Wikimedia and Openverse rate-limit shared IPs)."""
    import time
    kw.setdefault("headers", UA)
    kw.setdefault("timeout", 60)
    for i in range(5):
        r = requests.get(url, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            wait = int(r.headers.get("Retry-After", "0") or 0) or (4 + 6 * i)
            print(f"  {r.status_code} from {url.split('/')[2]}, retrying in {wait}s")
            time.sleep(min(wait, 40))
            continue
        return r
    return r


def manifest_add(outdir, row):
    proj = outdir
    for _ in range(4):
        if os.path.basename(proj) == "assets":
            break
        proj = os.path.dirname(proj)
    mf = os.path.join(proj if os.path.basename(proj) == "assets" else outdir, "manifest.csv")
    new = not os.path.exists(mf)
    with open(mf, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["file", "kind", "source", "url", "licence", "author", "query", "date"])
        w.writerow([row.get("file"), row.get("kind"), row.get("source"), row.get("url"), row.get("licence"),
                    row.get("author", ""), row.get("query", ""), datetime.date.today().isoformat()])


def download(url, path):
    r = http_get(url, timeout=120, stream=True)
    r.raise_for_status()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1 << 16):
            f.write(chunk)
    return path


def safe(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


# ----------------------------------------------------------------------------- Fluent emoji (MIT)
FLUENT = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"


def cmd_emoji(a):
    os.makedirs(a.out, exist_ok=True)
    for name in a.names:
        folder = name.strip()
        folder = folder[0].upper() + folder[1:]
        snake = safe(name)
        tries = [f"{urllib.parse.quote(folder)}/3D/{snake}_3d.png",
                 f"{urllib.parse.quote(folder)}/Default/3D/{snake}_3d_default.png"]
        ok = False
        for t in tries:
            url = FLUENT + t
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 200 and r.content[:4] == b"\x89PNG":
                dst = os.path.join(a.out, snake + ".png")
                open(dst, "wb").write(r.content)
                manifest_add(a.out, {"file": dst, "kind": "icon", "source": "Fluent UI Emoji 3D (Microsoft)", "url": url,
                                     "licence": "MIT", "author": "Microsoft", "query": name})
                print("ok  ", dst)
                ok = True
                break
        if not ok:
            print(f"miss {name!r}: use the exact Unicode emoji name (e.g. 'Money with wings', 'Face with open mouth'); "
                  "browse https://github.com/microsoft/fluentui-emoji/tree/main/assets")


# ----------------------------------------------------------------------------- Wikimedia Commons
def cmd_commons(a):
    api = "https://commons.wikimedia.org/w/api.php"
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": a.query + " filetype:bitmap",
              "gsrnamespace": 6, "gsrlimit": max(10, a.n * 4), "prop": "imageinfo",
              "iiprop": "url|size|extmetadata|mime", "iiurlwidth": a.width}
    r = http_get(api, params=params)
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    got = 0
    os.makedirs(a.out, exist_ok=True)
    for p in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < a.min_w or ii.get("mime", "").endswith("svg+xml"):
            continue
        if a.portrait and h < w * 0.9:
            continue
        md = ii.get("extmetadata") or {}
        lic = (md.get("LicenseShortName") or {}).get("value", "?")
        if a.no_nc and "NC" in lic.upper():
            continue
        artist = re.sub(r"<[^>]+>", "", (md.get("Artist") or {}).get("value", ""))[:80]
        url = ii.get("thumburl") or ii.get("url")
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
        dst = os.path.join(a.out, f"{safe(a.query)}_{got + 1}{ext}")
        try:
            download(url, dst)
        except Exception as e:
            print("fail", url, e)
            continue
        manifest_add(a.out, {"file": dst, "kind": "image", "source": "Wikimedia Commons", "url": ii.get("descriptionurl", url),
                             "licence": lic, "author": artist, "query": a.query})
        print(f"ok   {dst}  [{w}x{h}] {lic} {artist}")
        got += 1
        if got >= a.n:
            break
    if not got:
        print("nothing suitable; try other words, --min-w lower, or openverse/pexels")


def fluent_emoji(name, dst):
    """download one Fluent 3D emoji by its Unicode name (e.g. 'Rooster', 'Baby chick') -> dst; True when found"""
    folder = name.strip()
    folder = folder[0].upper() + folder[1:]
    snake = safe(name)
    for t in (f"{urllib.parse.quote(folder)}/3D/{snake}_3d.png", f"{urllib.parse.quote(folder)}/Default/3D/{snake}_3d_default.png"):
        r = requests.get(FLUENT + t, headers=UA, timeout=60)
        if r.status_code == 200 and r.content[:4] == b"\x89PNG":
            os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
            open(dst, "wb").write(r.content)
            manifest_add(os.path.dirname(os.path.abspath(dst)), {"file": dst, "kind": "creature", "source": "Fluent UI Emoji 3D (Microsoft)",
                                                                 "url": FLUENT + t, "licence": "MIT", "author": "Microsoft", "query": name})
            return True
    return False


# ----------------------------------------------------------------------------- sounds from Wikimedia Commons
def commons_sound(query, dst, dur=4.0, no_nc=True):
    """find a recording on Wikimedia Commons (animal sounds, crowds, machines...), convert it to a short clean WAV
    (leading silence removed, trimmed, faded, levelled) -> dst. Returns None or an error message."""
    import subprocess
    import tempfile
    api = "https://commons.wikimedia.org/w/api.php"
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": query + " filetype:audio",
              "gsrnamespace": 6, "gsrlimit": 20, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime"}
    r = http_get(api, params=params)
    if r.status_code != 200 or not r.text.startswith("{"):
        return f"Commons search failed ({r.status_code})"
    pages = sorted(((r.json().get("query") or {}).get("pages") or {}).values(), key=lambda x: x.get("index", 0))
    words = [w for w in re.split(r"\W+", query.lower()) if len(w) > 2]
    def score(p):
        title = p.get("title", "").lower()
        return -sum(1 for w in words if w.rstrip("s") in title)
    tried = 0
    for p in sorted(pages, key=score):
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("mime", "").startswith(("audio/", "application/ogg")) or ii.get("size", 0) > 12_000_000:
            continue
        md = ii.get("extmetadata") or {}
        lic = (md.get("LicenseShortName") or {}).get("value", "?")
        if no_nc and ("NC" in lic.upper() or "ND" in lic.upper().replace("AND", "")):
            continue
        tried += 1
        if tried > 4:
            break
        ext = os.path.splitext(urllib.parse.urlparse(ii["url"]).path)[1] or ".ogg"
        tmp = os.path.join(tempfile.gettempdir(), f"ra_snd_{os.getpid()}_{tried}{ext}")
        try:
            download(ii["url"], tmp)
        except Exception:
            continue
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        af = (f"silenceremove=start_periods=1:start_threshold=-42dB,atrim=0:{dur},asetpts=N/SR/TB,"
              f"afade=t=in:d=0.03,afade=t=out:st={max(0.1, dur - 0.35)}:d=0.35,loudnorm=I=-20:TP=-2")
        q = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", "48000", "-ac", "1", dst], capture_output=True)
        try:
            os.remove(tmp)
        except OSError:
            pass
        if q.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 48000 * 2 * 0.8:   # under ~0.8 s: try the next
            continue
        artist = re.sub(r"<[^>]+>", "", (md.get("Artist") or {}).get("value", ""))[:80]
        manifest_add(os.path.dirname(os.path.abspath(dst)), {"file": dst, "kind": "sound", "source": "Wikimedia Commons",
                                                             "url": ii.get("descriptionurl", ii["url"]), "licence": lic,
                                                             "author": artist, "query": query})
        return None
    return f"no usable Commons recording for {query!r}"


def cmd_sound(a):
    err = commons_sound(a.query, a.out, a.dur)
    print(err or f"ok   {a.out}")


# ----------------------------------------------------------------------------- Openverse (CC search, no key)
def cmd_openverse(a):
    r = http_get("https://api.openverse.org/v1/images/", params={"q": a.query, "page_size": max(10, a.n * 3),
                 "license_type": "commercial" if a.no_nc else "all", "aspect_ratio": "tall" if a.portrait else None})
    r.raise_for_status()
    got = 0
    os.makedirs(a.out, exist_ok=True)
    for it in r.json().get("results", []):
        if (it.get("width") or 0) < a.min_w:
            continue
        url = it.get("url")
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
        dst = os.path.join(a.out, f"{safe(a.query)}_ov{got + 1}{ext}")
        try:
            download(url, dst)
        except Exception as e:
            print("fail", url, e)
            continue
        manifest_add(a.out, {"file": dst, "kind": "image", "source": "Openverse/" + str(it.get("source")), "url": it.get("foreign_landing_url", url),
                             "licence": f"{it.get('license')} {it.get('license_version') or ''}".strip(), "author": it.get("creator", ""), "query": a.query})
        print(f"ok   {dst}  {it.get('license')} {it.get('creator')}")
        got += 1
        if got >= a.n:
            break


# ----------------------------------------------------------------------------- Pexels / Pixabay (free keys)
def cmd_pexels(a):
    key = get_key("pexels")
    if a.video:
        r = requests.get("https://api.pexels.com/videos/search", params={"query": a.query, "per_page": a.n * 2, "orientation": "portrait" if a.portrait else None},
                         headers={"Authorization": key}, timeout=60)
        r.raise_for_status()
        got = 0
        for v in r.json().get("videos", []):
            files = sorted([f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and (f.get("height") or 0) >= 720],
                           key=lambda f: abs((f.get("height") or 0) - 1920))
            if not files:
                continue
            dst = os.path.join(a.out, f"{safe(a.query)}_px{got + 1}.mp4")
            download(files[0]["link"], dst)
            manifest_add(a.out, {"file": dst, "kind": "video", "source": "Pexels", "url": v.get("url"), "licence": "Pexels License",
                                 "author": (v.get("user") or {}).get("name", ""), "query": a.query})
            print("ok  ", dst, f"{v.get('duration')}s")
            got += 1
            if got >= a.n:
                break
    else:
        r = requests.get("https://api.pexels.com/v1/search", params={"query": a.query, "per_page": a.n * 2, "orientation": "portrait" if a.portrait else None},
                         headers={"Authorization": key}, timeout=60)
        r.raise_for_status()
        for i, p in enumerate(r.json().get("photos", [])[: a.n]):
            dst = os.path.join(a.out, f"{safe(a.query)}_px{i + 1}.jpg")
            download(p["src"]["large2x"], dst)
            manifest_add(a.out, {"file": dst, "kind": "image", "source": "Pexels", "url": p.get("url"), "licence": "Pexels License",
                                 "author": p.get("photographer", ""), "query": a.query})
            print("ok  ", dst)


def cmd_pixabay(a):
    key = get_key("pixabay")
    if a.video:
        r = requests.get("https://pixabay.com/api/videos/", params={"key": key, "q": a.query, "per_page": max(3, a.n * 2)}, timeout=60)
        r.raise_for_status()
        for i, h in enumerate(r.json().get("hits", [])[: a.n]):
            v = h["videos"].get("large") or h["videos"].get("medium")
            if not v or not v.get("url"):
                continue
            dst = os.path.join(a.out, f"{safe(a.query)}_pb{i + 1}.mp4")
            download(v["url"], dst)
            manifest_add(a.out, {"file": dst, "kind": "video", "source": "Pixabay", "url": h.get("pageURL"), "licence": "Pixabay Content License",
                                 "author": h.get("user", ""), "query": a.query})
            print("ok  ", dst)
    else:
        r = requests.get("https://pixabay.com/api/", params={"key": key, "q": a.query, "per_page": max(3, a.n * 2),
                         "orientation": "vertical" if a.portrait else "all", "image_type": a.image_type}, timeout=60)
        r.raise_for_status()
        for i, h in enumerate(r.json().get("hits", [])[: a.n]):
            dst = os.path.join(a.out, f"{safe(a.query)}_pb{i + 1}" + (".png" if a.image_type == "vector" else ".jpg"))
            download(h.get("largeImageURL") or h.get("webformatURL"), dst)
            manifest_add(a.out, {"file": dst, "kind": "image", "source": "Pixabay", "url": h.get("pageURL"), "licence": "Pixabay Content License",
                                 "author": h.get("user", ""), "query": a.query})
            print("ok  ", dst)


# ----------------------------------------------------------------------------- archive.org (public-domain film)
def cmd_archive(a):
    q = f"({a.query}) AND mediatype:(movies) AND (licenseurl:*publicdomain* OR collection:(prelinger) OR collection:(newsandpublicaffairs))"
    r = requests.get("https://archive.org/advancedsearch.php", params={"q": q, "fl[]": ["identifier", "title", "licenseurl"], "rows": a.n * 3, "output": "json"},
                     headers=UA, timeout=60)
    r.raise_for_status()
    got = 0
    for d in r.json().get("response", {}).get("docs", []):
        ident = d["identifier"]
        md = requests.get(f"https://archive.org/metadata/{ident}", headers=UA, timeout=60).json()
        files = [f for f in md.get("files", []) if f.get("name", "").lower().endswith(".mp4")]
        files.sort(key=lambda f: int(f.get("size", 0) or 0))
        if not files:
            continue
        pick = files[0] if int(files[0].get("size", 0) or 0) > 2_000_000 else files[-1]
        url = f"https://archive.org/download/{ident}/{urllib.parse.quote(pick['name'])}"
        dst = os.path.join(a.out, f"{safe(a.query)}_ia{got + 1}.mp4")
        try:
            download(url, dst)
        except Exception as e:
            print("fail", url, e)
            continue
        manifest_add(a.out, {"file": dst, "kind": "video", "source": "Internet Archive", "url": f"https://archive.org/details/{ident}",
                             "licence": d.get("licenseurl", "public domain (check)"), "author": d.get("title", ""), "query": a.query})
        print("ok  ", dst, "-", d.get("title"))
        got += 1
        if got >= a.n:
            break


def cmd_url(a):
    os.makedirs(a.out, exist_ok=True)
    dst = os.path.join(a.out, a.name or os.path.basename(urllib.parse.urlparse(a.url).path))
    download(a.url, dst)
    manifest_add(a.out, {"file": dst, "kind": a.kind, "source": a.source or urllib.parse.urlparse(a.url).netloc, "url": a.url,
                         "licence": a.licence or "check", "author": a.author or "", "query": ""})
    print("ok  ", dst)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("emoji"); e.add_argument("names", nargs="+"); e.add_argument("-o", "--out", required=True); e.set_defaults(fn=cmd_emoji)
    for name, fn in (("commons", cmd_commons), ("openverse", cmd_openverse), ("pexels", cmd_pexels), ("pixabay", cmd_pixabay), ("archive", cmd_archive)):
        c = sp.add_parser(name)
        c.add_argument("query"); c.add_argument("-o", "--out", required=True); c.add_argument("--n", type=int, default=4)
        c.add_argument("--portrait", action="store_true"); c.add_argument("--video", action="store_true")
        c.add_argument("--min-w", type=int, default=1000); c.add_argument("--width", type=int, default=1600)
        c.add_argument("--no-nc", action="store_true", help="skip NonCommercial licences (monetised channels)")
        c.add_argument("--image-type", default="photo")
        c.set_defaults(fn=fn)
    so = sp.add_parser("sound"); so.add_argument("query"); so.add_argument("-o", "--out", required=True)
    so.add_argument("--dur", type=float, default=4.0); so.set_defaults(fn=cmd_sound)
    u = sp.add_parser("url"); u.add_argument("url"); u.add_argument("-o", "--out", required=True); u.add_argument("--name")
    u.add_argument("--licence"); u.add_argument("--source"); u.add_argument("--author"); u.add_argument("--kind", default="image"); u.set_defaults(fn=cmd_url)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
