"""Cut the timed narration into shots with the house editing rhythm and write a spec skeleton.

  python auto_plan.py PROJECT [--title "MONEY RAIN"] [--seed 1] [-o plan/spec.json] [--force]

Input : PROJECT/timing/words.json, PROJECT/timing/captions.json, audio/voice.wav (duration)
Output: plan/spec.json with meta, captions, audio, an empty cast{} and shots[] that already carry:
        t / end on word onsets, the words spoken ("say"), word times ("w"), a camera move in the house
        pattern (snap pull-outs and eased push-ins, occasional punch-ins), a suggested transition and an
        empty visual brief to fill (bg, actors, props, icons, fx, state).
        plan/shotlist.md - a readable table to plan the visuals shot by shot.

Rhythm (measured on the samples): median shot 1.3 s (p25 0.87, p75 1.97, p90 2.95, min ~0.6), ~6 words per
shot, cuts land on a word onset (within 0.07 s) - usually on the noun/verb that changes the picture, only
~29% right after a comma/period; virtually every shot has camera motion (about half are fast eased pull-outs,
40% slower push-ins, 8% pans). Pivot phrases ("The problem was", "But", "Meanwhile", "Luckily",
"Unfortunately", "Because of that", "Thanks to this", "That's when") always start a new shot.
"""
import argparse
import json
import math
import os
import random
import re
import subprocess

from ra_common import STYLE, load_data, read_json, write_json
import coverage as CV  # noqa: E402

ICON_MAP = load_data("icon_map.json")["map"]
import creatures as CR  # noqa: E402
# emotion, gesture and people icons: the characters act these (faces, poses), so the plan never suggests them
NOT_ICONS = {"angry_face", "astonished_face", "cold_face", "crying_face", "dizzy_face", "exploding_head", "face_screaming_in_fear",
             "face_vomiting", "face_with_open_mouth", "face_with_rolling_eyes", "face_with_spiral_eyes", "face_with_tears_of_joy",
             "fearful_face", "grimacing_face", "hot_face", "loudly_crying_face", "lying_face", "money_mouth_face", "nauseated_face",
             "pouting_face", "shushing_face", "sleeping_face", "smiling_face_with_horns", "smiling_face_with_sunglasses",
             "thinking_face", "zipper_mouth_face", "heavy_black_heart", "broken_heart", "hundred_points_symbol", "thumbs_up_sign",
             "thumbs_down_sign", "ok_hand", "ok_hand_sign", "clapping_hands_sign", "raised_hand", "waving_hand_sign", "zzz",
             "sweat_droplets", "right_anger_bubble", "flexed_biceps", "fisted_hand_sign", "eyes", "dizzy_symbol",
             "detective", "man", "woman", "baby", "child", "older_man", "older_woman", "police_officer", "guardsman",
             "construction_worker", "ninja", "princess", "prince", "bride_with_veil", "superhero", "supervillain", "mage",
             "genie", "zombie", "vampire", "bust_in_silhouette", "busts_in_silhouette"}

PIVOTS = ["the problem was", "problem was", "but", "meanwhile", "luckily", "unfortunately", "because of that",
          "thanks to this", "thanks to that", "that's when", "at that moment", "right away", "instantly",
          "immediately", "after", "then", "so", "and as", "when", "finally", "however", "years later",
          "that's because", "knowing this", "in the end", "outside"]
FUNC = set("a an the of to in on at for and or but with by as from into onto than that this these those his her its their our my your he she it they we i was were is are be been had has have did do does would could should will just so up out off".split())


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def duration_of(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout.strip()
        return float(out)
    except Exception:
        return None


def cut_cost(dur):
    """negative log-likelihood-ish of a shot length under the measured distribution (log-normal, median 1.3 s)"""
    if dur < 0.55:
        return 50.0 + (0.55 - dur) * 200
    mu, sigma = math.log(1.3), 0.62
    z = (math.log(dur) - mu) / sigma
    c = 0.5 * z * z
    if dur > 3.2:
        c += (dur - 3.2) * 6
    return c


DETPREP = set("a an the this these those his her their its my your our of to in on at for from by with into onto about over under very too some any every each".split())
CLAUSE = set("and but he she they it we i then so when while because who which that to in on at after before until with as where if".split())


def boundary_bonus(words, i):
    """bonus (negative cost) for starting a shot at word i: cut at clause/phrase starts, never inside a noun phrase"""
    if i == 0:
        return 0.0
    prev_raw = words[i - 1]["w"].rstrip()
    prev = norm(prev_raw)
    w = norm(words[i]["w"])
    b = 0.0
    punct = prev_raw.endswith((".", "!", "?", ",", ";", ":"))
    if prev_raw.endswith((".", "!", "?")):
        b -= 2.6
    elif prev_raw.endswith((",", ";", ":")):
        b -= 1.6
    phrase = " ".join(norm(x["w"]) for x in words[i:i + 3])
    for p in PIVOTS:
        if phrase.startswith(p + " ") or phrase == p:
            b -= 1.0
            break
    if not punct and prev in DETPREP:
        b += 2.5                       # never end a shot on 'the', 'a', 'of', 'to'...
    if not punct and w in CLAUSE and prev not in FUNC:
        b -= 0.7                       # cut where a new clause / phrase begins
    if not punct and w not in FUNC and prev not in FUNC:
        b += 0.6                       # inside a noun phrase ("con | man")
    if words[i]["w"][:1].isdigit():
        b -= 0.2
    return b


def segment(words, total):
    n = len(words)
    starts = [w["s"] for w in words]
    INF = 1e18
    best = [INF] * (n + 1)
    back = [-1] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        tj = starts[j] if j < n else total
        for i in range(max(0, j - 18), j):
            if best[i] == INF:
                continue
            ti = 0.0 if i == 0 else starts[i]
            c = best[i] + cut_cost(tj - ti) + (boundary_bonus(words, j) if j < n else 0)
            if c < best[j]:
                best[j] = c
                back[j] = i
    cuts = []
    j = n
    while j > 0:
        i = back[j]
        cuts.append((i, j))
        j = i
    cuts.reverse()
    return cuts


def camera_for(k, t0, t1, rnd, prev_kind):
    d = t1 - t0
    kinds = ["pull", "push", "pull", "push", "pull", "punch", "push", "pull", "pan"]
    kind = kinds[k % len(kinds)]
    if kind == prev_kind:
        kind = "push" if kind == "pull" else "pull"
    if d < 0.8 and kind in ("punch", "pan"):
        kind = "pull"
    F = [540, 960]
    if kind == "pull":
        z0 = round(rnd.uniform(1.22, 1.4), 2)
        snap = min(0.62, d * 0.55)
        keys = [{"t": t0, "zoom": z0, "focus": F}, {"t": round(t0 + snap, 3), "zoom": 1.02, "focus": F, "ease": "out"},
                {"t": t1, "zoom": round(1.02 + 0.02 * d, 3), "focus": F, "ease": "linear"}]
    elif kind == "push":
        z1 = round(1.0 + min(0.32, rnd.uniform(0.08, 0.14) * d + 0.04), 3)
        keys = [{"t": t0, "zoom": 1.0, "focus": F}, {"t": t1, "zoom": z1, "focus": F, "ease": "inout"}]
    elif kind == "punch":
        tm = round(t0 + d * 0.5, 3)
        keys = [{"t": t0, "zoom": 1.0, "focus": F}, {"t": tm, "zoom": 1.04, "focus": F, "ease": "linear"},
                {"t": round(tm + 1 / 30, 3), "zoom": 1.3, "focus": F, "ease": "cut"},
                {"t": t1, "zoom": 1.36, "focus": F, "ease": "linear"}]
    else:
        keys = [{"t": t0, "zoom": 1.12, "focus": [460, 960]}, {"t": t1, "zoom": 1.14, "focus": [620, 960], "ease": "inout"}]
    return kind, keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--title", default="")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("-o", "--out", default="plan/spec.json")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    P = a.project
    out = os.path.join(P, a.out)
    if os.path.exists(out) and not a.force:
        raise SystemExit(f"{out} exists (it may hold your visual plan). Use --force to overwrite, or -o plan/spec_new.json")
    words = read_json(os.path.join(P, "timing", "words.json"))
    caps = read_json(os.path.join(P, "timing", "captions.json"), default=[])
    voice = os.path.join(P, "audio", "voice.wav")
    total = duration_of(voice) if os.path.exists(voice) else None
    if not total:
        total = words[-1]["e"] + 0.4
    total = round(max(total, words[-1]["e"] + 0.25), 3)
    rnd = random.Random(a.seed)
    cuts = segment(words, total)
    shots = []
    prev_kind = None
    for k, (i, j) in enumerate(cuts):
        t0 = 0.0 if i == 0 else round(words[i]["s"], 3)
        t1 = total if j >= len(words) else round(words[j]["s"], 3)
        kind, cam = camera_for(k, t0, t1, rnd, prev_kind)
        prev_kind = kind
        say = " ".join(w["w"] for w in words[i:j])
        first = norm(words[i]["w"]) + " " + (norm(words[i + 1]["w"]) if i + 1 < len(words) else "")
        tr = "cut"
        if k > 0 and any(first.startswith(p) for p in ("problem", "the problem", "but when", "meanwhile", "years", "thanks")):
            tr = "flash?"
        # icon ideas only for abstract CONCEPTS nobody can act (death, danger, an idea, time, money amounts) - never
        # emotions (faces act them), gestures (poses), people (characters) or animals (living creatures)
        ideas = []
        for w in words[i:j]:
            key = norm(w["w"])
            if key in ICON_MAP and not CR.animal_of(key):
                ics = [x for x in ICON_MAP[key] if x not in NOT_ICONS and not CR.animal_of(x.replace("_face", ""))]
                if ics:
                    ideas.append({"word": w["w"], "t": round(w["s"], 2), "icons": ics})
        # every object and action the narration names here must be shown on its word (coverage.py checks it)
        show = []
        for text, tw, raw in CV.words_with_phrases(words[i:j]):
            for kind, L, proof, how in CV.readings(text):
                if kind != "person":
                    show.append({"word": raw, "t": round(tw, 2), "kind": kind, "how": how})
        shots.append({"id": f"S{k + 1:02d}", "t": t0, "end": t1, "say": say, "ideas": ideas, "show": show,
                      "w": [[w["w"], round(w["s"], 2)] for w in words[i:j]],
                      "camera_kind": "auto", "camera": "auto", "transition": tr,
                      "bg": {"file": "", "grade": "moody"}, "actors": [], "props": [], "icons": [], "fx": [], "state": []})
    spec = {"version": 1,
            "meta": {"title": a.title, "slug": os.path.basename(os.path.abspath(P)), "fps": 30, "width": 1080, "height": 1920,
                     "duration": total},
            "audio": {"voice": "audio/voice.wav", "music": "audio/music.wav", "music_db": -17, "sfx": []},
            "captions": caps,
            "cast": {},
            "look": {"vignette": STYLE["look"]["vignette"], "grain": STYLE["look"]["grain"], "end": "none"},
            "shots": shots}
    write_json(out, spec)
    durs = sorted(s["end"] - s["t"] for s in shots)
    med = durs[len(durs) // 2]
    lines = ["| shot | time | dur | words | MUST SHOW (word@time: how) | optional concept icons (only if nobody can act it; ~5-8 a minute in all) |",
             "|---|---|---|---|---|---|"]
    for s in shots:
        idea = "; ".join(f"{x['word']}@{x['t']}: {'/'.join(x['icons'])}" for x in s["ideas"])
        must = "; ".join(f"**{x['word']}**@{x['t']} ({x['kind']}): {x['how']}" for x in s["show"])
        lines.append(f"| {s['id']} | {s['t']:.2f}-{s['end']:.2f} | {s['end'] - s['t']:.2f} | {s['say']} | {must} | {idea} |")
    with open(os.path.join(P, "plan", "shotlist.md"), "w", encoding="utf-8") as f:
        f.write(f"# Shot list - {a.title}\n\n{len(shots)} shots, median {med:.2f}s, total {total:.2f}s\n\n" + "\n".join(lines) + "\n")
    print(f"{len(shots)} shots (median {med:.2f}s, min {durs[0]:.2f}s, max {durs[-1]:.2f}s) -> {out}")


if __name__ == "__main__":
    main()
