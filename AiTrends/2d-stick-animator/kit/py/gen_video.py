"""Generate short live-action-style insert clips (1-3 s are used) with Kie.ai video models.

  python gen_video.py "1940s black and white newsreel: soldiers running across a muddy trench, film grain" \
         -o PROJECT/assets/video/ww2.mp4 [--model kling-3.0/video] [--dur 5] [--image first_frame_url]

The samples cut to 0-3 real-looking clips per video (archival B&W war footage, a woman running down a prison
corridor, an angry man on the phone, aerial traffic). Prefer real public-domain footage first (fetch_assets.py
archive / pexels / pixabay); generate only what does not exist. Prompts: describe STYLE (film stock, colour/B&W,
grain), SCENE, CAMERA (handheld, slow push) and MOTION in one line; vertical 9:16; no text.
Costs credits: confirm with the user first.
"""
import argparse
import json
import os
import sys
import time

import requests

from ra_common import get_key

KIE = "https://api.kie.ai/api/v1"


def call(method, path, key, payload=None):
    for i in range(5):
        r = requests.request(method, KIE + path, json=payload, timeout=60,
                             headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        if r.status_code in (429, 500, 502, 503):
            time.sleep(5 + 5 * i)
            continue
        if r.status_code == 401:
            sys.exit("Kie.ai rejected the key")
        return r.json()
    raise RuntimeError("no answer")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--model", default="kling-3.0/video", help="kling-3.0/video | bytedance/seedance-2 | grok-imagine/image-to-video")
    ap.add_argument("--dur", type=int, default=5)
    ap.add_argument("--image", help="first-frame image URL (image-to-video)")
    a = ap.parse_args()
    key = get_key("kie")
    if a.model.startswith("kling"):
        inp = {"prompt": a.prompt, "sound": False, "duration": str(a.dur), "aspect_ratio": "9:16", "mode": "std"}
        if a.image:
            inp["image_urls"] = [a.image]
    elif a.model.startswith("bytedance/seedance"):
        inp = {"prompt": a.prompt, "generate_audio": False, "resolution": "720p", "aspect_ratio": "9:16", "duration": a.dur}
        if a.image:
            inp["first_frame_url"] = a.image
    else:
        inp = {"prompt": a.prompt, "mode": "normal", "duration": str(a.dur), "resolution": "720p", "aspect_ratio": "9:16"}
        if a.image:
            inp["image_urls"] = [a.image]
    r = call("POST", "/jobs/createTask", key, {"model": a.model, "input": inp})
    if r.get("code") != 200:
        sys.exit(f"createTask failed: {r.get('msg')}")
    task = r["data"]["taskId"]
    print("task", task)
    t0, delay = time.time(), 10
    while time.time() - t0 < 1800:
        time.sleep(delay)
        delay = min(20, delay + 3)
        d = call("GET", "/jobs/recordInfo?taskId=" + task, key).get("data") or {}
        if d.get("state") == "success":
            res = json.loads(d.get("resultJson") or "{}")
            url = (res.get("resultUrls") or [None])[0]
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            open(a.out, "wb").write(requests.get(url, timeout=300).content)
            sys.path.insert(0, os.path.dirname(__file__))
            from fetch_assets import manifest_add
            manifest_add(os.path.dirname(a.out), {"file": a.out, "kind": "video", "source": f"Kie.ai {a.model}", "url": url,
                                                  "licence": "generated for this project", "query": a.prompt[:200]})
            print("ok  ", a.out)
            return
        if d.get("state") == "fail":
            sys.exit(f"failed: {d.get('failCode')} {d.get('failMsg')}")
        print("  ...", d.get("state"))
    sys.exit("timed out")


if __name__ == "__main__":
    main()
