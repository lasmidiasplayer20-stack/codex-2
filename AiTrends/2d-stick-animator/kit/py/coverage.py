"""Story coverage: is every object the narration names and every action it describes shown on screen, on its word?

  python coverage.py PROJECT [--spec plan/spec.json] [--visible] [--sheet] [-o plan/coverage.md]

Reads timing/words.json and the plan. Every narration word that the story lexicon (data/story_lexicon.json) or the
icon map knows as a showable object or action is checked against what is on screen around the moment it is spoken
(from 0.5 s before to 1.5 s after, inside the same shot):
  objects  - a prop, held prop, icon, fx, background or costume piece whose file name (or "covers" list) has the word
             or one of its synonyms ("makeup" -> makeup / brush / lipstick / powder ...);
  actions  - a pose key or an action (act) of the lexicon's poses/acts for that verb, a prop that proves it
             (a pistol for "shot"), or an element with the verb in its "covers" list;
  people   - "man", "soldiers", "doctor"... are covered when a character is on screen.
Mark anything shown another way with "covers": ["word", ...] on the prop/icon/hold/key/act/fx that shows it.
--visible also renders each covered object at its word with the preview renderer, once with and once without it,
and flags objects that are off camera or hidden behind someone (they exist in the plan but nobody can see them).
Exit code 1 when something is missing (validate_spec.py reports the same as warnings).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_common import KIT  # noqa: E402
import creatures as CR  # noqa: E402

LEX = json.load(open(os.path.join(KIT, "data", "story_lexicon.json"), encoding="utf-8"))
try:
    ICON_MAP = json.load(open(os.path.join(KIT, "data", "icon_map.json"), encoding="utf-8")).get("map", {})
except Exception:
    ICON_MAP = {}
BEFORE, AFTER = 0.5, 1.5


def lemma(w):
    w = w.lower().strip()
    w = re.sub(r"[^a-z0-9'\-]", "", w)
    w = re.sub(r"'s$", "", w).strip("'")
    if not w:
        return ""
    if w in LEX["irregular"]:
        return LEX["irregular"][w]
    if w in LEX["verbs"] or w in LEX["nouns"] or w in ICON_MAP or w in LEX["people"]:
        return w
    for suf, rep in (("ies", "y"), ("ied", "y"), ("ying", "ie"), ("es", ""), ("s", ""), ("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e")):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            b = w[: -len(suf)] + rep
            if b in LEX["verbs"] or b in LEX["nouns"] or b in ICON_MAP or b in LEX["people"]:
                return b
            if suf in ("ed", "ing") and len(b) > 3 and b[-1] == b[-2]:      # stopped -> stop
                if b[:-1] in LEX["verbs"]:
                    return b[:-1]
    return w


def tokens_of(path):
    base = os.path.splitext(os.path.basename(str(path)))[0].lower()
    return set(t for t in re.split(r"[^a-z0-9]+", base) if t)


def readings(word):
    """(kind, lemma, proof words, how) for every way this word can be shown. Animals are living CREATURES (a whole
    moving animal with its sound - never an icon). Words that only the icon map knows (problem, time, happy...) are not
    demanded: the characters act them, an icon is optional (house-style icon rules)."""
    out = []
    L = lemma(word)
    if not L or L in LEX["generic"]:
        return out
    an = CR.animal_of(L) or CR.animal_of(re.sub(r"[^a-z]", "", str(word).lower()))
    if an:
        aka = set(CR.ANIMALS[an]["aka"]) | {an}
        return [("creature", an, aka, "a living creature: the whole animal moving in the scene (shot 'creatures', "
                 "behave peck/wander/walk/hop/fly/swim...) with its sound - never a head icon")]
    if L in LEX["people"]:
        out.append(("person", L, set(), "a character on screen"))
    if L in LEX["verbs"]:
        v = LEX["verbs"][L]
        out.append(("action", L, set(v.get("props", [])) | {L}, v.get("how", "")))
    if L in LEX["nouns"]:
        n = LEX["nouns"][L]
        out.append(("object", L, set(n.get("match", [])) | {L}, n.get("how", "")))
    return out


def words_with_phrases(words):
    """merge two-word phrases (make up -> makeup) and return [(text, t)]"""
    out, i = [], 0
    while i < len(words):
        w = words[i]
        a = re.sub(r"[^a-z\-]", "", w["w"].lower())
        if i + 1 < len(words):
            b = re.sub(r"[^a-z\-]", "", words[i + 1]["w"].lower())
            ph = LEX["phrases"].get(f"{a} {b}")
            if ph:
                out.append((ph, float(w["s"]), w["w"] + " " + words[i + 1]["w"]))
                i += 2
                continue
        if a in LEX["phrases"]:
            out.append((LEX["phrases"][a], float(w["s"]), w["w"]))
        else:
            out.append((w["w"], float(w["s"]), w["w"]))
        i += 1
    return out


def active(el, t0, t1, sh, costume=False):
    if costume:      # costume pieces: from/to window
        a, b = float(el.get("from", -1e9)), float(el.get("to", 1e9))
    else:
        a = float(el.get("t", sh["t"]))
        b = float(el.get("end", sh["end"]))
    return a < t1 and b > t0


def evidence(spec, sh, t):
    """everything on screen around time t in shot sh: words proving objects/actions, poses, acts, actors present"""
    t0, t1 = t - BEFORE, t + AFTER
    proof, poses, acts, covers, actors, creatures = set(), set(), set(), set(), set(), set()
    bg = sh.get("bg") or {}
    if bg.get("file"):
        proof |= tokens_of(bg["file"])
    proof |= set(x.lower() for x in bg.get("covers", []))
    items = []
    for p in sh.get("props", []):
        items.append(("prop", p))
    for ic in sh.get("icons", []):
        items.append(("icon", ic))
    for fx in sh.get("fx", []):
        items.append(("fx", fx))
    for v in sh.get("vehicles", []):              # a vehicle and its seated riders (compile_spec expands them)
        items.append(("prop", dict(v, covers=v.get("covers", ["car", "cars", "drove", "drive", "ride", "rode"]))))
        for r in v.get("riders", []):
            actors.add(r.get("cast"))
            poses.add("sit")
            for k in r.get("keys", []):
                covers |= set(x.lower() for x in k.get("covers", []))
            if r.get("wave"):
                acts.add("wave")
    for ac in sh.get("actors", []):
        cid = ac.get("cast")
        actors.add(cid)
        for h in ac.get("hold", []):
            items.append(("hold", h))
        for acc in (spec.get("cast", {}).get(cid, {}) or {}).get("accessories", []):
            if active(acc, t0, t1, sh, costume=True):
                proof |= tokens_of(acc.get("file", ""))
                covers |= set(x.lower() for x in acc.get("covers", []))
        for k in ac.get("keys", []):
            if t0 - 0.2 <= float(k.get("t", sh["t"])) <= t1:
                if k.get("pose"):
                    poses.add(k["pose"])
                covers |= set(x.lower() for x in k.get("covers", []))
        # the pose held at t counts too (a character already eating while "ate" is spoken)
        held = None
        for k in sorted(ac.get("keys", []), key=lambda k: float(k.get("t", 0))):
            if float(k.get("t", 0)) <= t and k.get("pose"):
                held = k["pose"]
        if held:
            poses.add(held)
        for a in ac.get("act", []):
            if active(a, t0, t1, sh):
                acts.add(a.get("kind"))
                covers |= set(x.lower() for x in a.get("covers", []))
        for at in ac.get("attach", []):
            if active(at, t0, t1, sh):
                acts.add("attach")
    for c in sh.get("creatures", []):
        if active(c, t0, t1, sh):
            for w in tokens_of(c.get("file", "")) | {str(c.get("id", "")).lower(), str(c.get("animal", "")).lower()} | \
                    set(x.lower() for x in c.get("covers", [])):
                an = CR.animal_of(w)
                if an:
                    creatures.add(an)
                creatures.add(w)
    for kind, el in items:
        if not active(el, t0, t1, sh):
            continue
        if el.get("file"):
            proof |= tokens_of(el["file"])
        if el.get("text"):
            proof |= set(re.split(r"[^a-z0-9]+", str(el["text"]).lower()))
        if el.get("kind") in ("money_rain",):
            proof |= {"money", "cash", "dollar"}
        covers |= set(x.lower() for x in el.get("covers", []))
    return {"proof": proof, "poses": poses, "acts": acts, "covers": covers, "actors": actors, "creatures": creatures}


def check(spec, words):
    rows = []
    for text, t, raw in words_with_phrases(words):
        rs = readings(text)
        if not rs:
            continue
        sh = next((s for s in spec["shots"] if s["t"] - 1e-3 <= t < s["end"]), None)
        if sh is None:
            continue
        ev = evidence(spec, sh, t)
        ok, by = False, ""
        for kind, L, proof, how in rs:
            if kind == "creature":
                if L in ev["creatures"] or proof & ev["creatures"]:
                    ok, by = True, "creature on screen"
                elif L in ev["covers"] or proof & ev["covers"]:
                    ok, by = True, "covers"          # a figure of speech ("like a dog"), marked by hand
                continue
            if L in ev["covers"]:
                ok, by = True, "covers"
            elif kind == "person":
                ok, by = (len(ev["actors"]) > 0), "characters on screen"
            elif kind == "object":
                hit = proof & ev["proof"]
                if hit:
                    ok, by = True, "file: " + ", ".join(sorted(hit))
            else:
                v = LEX["verbs"][L]
                hp = set(v.get("poses", [])) & ev["poses"]
                ha = set(v.get("acts", [])) & ev["acts"]
                hpr = proof & ev["proof"]
                if L in ("pull", "drag", "carry", "lift") and "attach" in ev["acts"]:
                    ha.add("attach")
                if hp or ha or hpr:
                    ok, by = True, ", ".join(sorted(hp | ha | hpr))
            if ok:
                break
        kinds = "/".join(sorted(set(r[0] for r in rs)))
        rows.append({"word": raw, "lemma": rs[0][1], "t": round(t, 2), "shot": sh["id"], "kind": kinds, "ok": ok, "by": by,
                     "how": " | ".join(r[3] for r in rs if r[3]), "proof": sorted(set().union(*[r[2] for r in rs]) | {r[1] for r in rs})})
    return rows


def visibility(P, spec, rows):
    """render each covered object's moment with and without the element that proves it; tiny difference = not visible"""
    import copy
    import numpy as np
    import ra_preview as RP
    from compile_spec import compile_spec
    out = {}
    base = compile_spec(copy.deepcopy(spec), P)
    R0 = RP.Renderer(P, base, 0.25, 15)
    for r in rows:
        if not r["ok"] or not ("object" in r["kind"] or "creature" in r["kind"]):
            continue
        if not (r["by"].startswith("file:") or r["by"] in ("covers", "creature on screen")):
            continue
        words = set(r["by"][6:].split(", ")) if r["by"].startswith("file:") else ({r["lemma"]} | set(r.get("proof", [])))

        def proves(e):
            return bool(tokens_of(e.get("file", "")) & words) or bool(set(x.lower() for x in e.get("covers", [])) & words) \
                or str(e.get("id", "")).lower() in words or str(e.get("animal", "")).lower() in words
        t = r["t"] + 0.35
        sid = r["shot"]
        sp2 = copy.deepcopy(spec)
        sh2 = next(s for s in sp2["shots"] if s["id"] == sid)
        removed = 0
        for key in ("props", "icons", "fx", "creatures"):
            keep = [e for e in sh2.get(key, []) if not proves(e)]
            removed += len(sh2.get(key, [])) - len(keep)
            sh2[key] = keep
        for ac in sh2.get("actors", []):
            keep = [h for h in ac.get("hold", []) if not proves(h)]
            removed += len(ac.get("hold", [])) - len(keep)
            ac["hold"] = keep
        if not removed:
            continue          # proven by the background or a costume piece: always visible
        R1 = RP.Renderer(P, compile_spec(sp2, P), 0.25, 15)
        a = R0.render_frame(t).astype(np.float32)
        b = R1.render_frame(t).astype(np.float32)
        diff = (np.abs(a - b).max(-1) > 24).mean()
        out[(r["word"], r["t"])] = float(diff)
    return out


def detail_sheet(P, spec, rows, out):
    """frames at every named object/action and at every held prop, labelled, for the critical detail review"""
    import copy
    from PIL import Image, ImageDraw
    import ra_preview as RP
    from compile_spec import compile_spec
    cs = compile_spec(copy.deepcopy(spec), P)
    R = RP.Renderer(P, cs, 0.4, 15)
    moments = [(r["t"] + 0.35, f"{r['t']:.2f}s '{r['word']}' ({r['kind']})") for r in rows if "person" not in r["kind"]]
    for sh in cs["shots"]:
        for ac in sh.get("actors", []):
            for h in ac.get("hold", []):
                tm = (float(h.get("t", sh["t"])) + float(h.get("end", sh["end"]))) / 2
                moments.append((tm, f"{tm:.2f}s {ac.get('cast')} holds {os.path.basename(h.get('file', ''))}"))
    moments.sort()
    tiles = []
    for t, label in moments:
        im = Image.fromarray(R.render_frame(min(t, cs["meta"]["duration"] - 0.05))).convert("RGB")
        im = im.resize((im.width * 300 // im.height, 300))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, im.width, 16), fill=(0, 0, 0))
        d.text((3, 2), label[:44], fill=(255, 230, 0))
        tiles.append(im)
    if not tiles:
        return None
    cols = 6
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)), (30, 30, 30))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out, quality=88)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec.json")
    ap.add_argument("--visible", action="store_true")
    ap.add_argument("--sheet", action="store_true", help="also write qc/detail_sheet.jpg (every named thing and held prop)")
    ap.add_argument("-o", "--out", default="plan/coverage.md")
    a = ap.parse_args()
    P = a.project
    spec = json.load(open(os.path.join(P, a.spec), encoding="utf-8"))
    words = json.load(open(os.path.join(P, "timing", "words.json"), encoding="utf-8"))
    words = words.get("words", words) if isinstance(words, dict) else words
    rows = check(spec, words)
    vis = visibility(P, spec, rows) if a.visible else {}
    lines = ["# Story coverage", "", "| time | shot | word | kind | on screen | how to show it |", "|---|---|---|---|---|---|"]
    missing = 0
    for r in rows:
        v = vis.get((r["word"], r["t"]))
        state = ("OK " + r["by"]) if r["ok"] else "MISSING"
        if v is not None and v < 0.002:
            state = f"NOT VISIBLE ({r['by']}: off camera or hidden behind someone)"
            r["ok"] = False
        if not r["ok"]:
            missing += 1
        lines.append(f"| {r['t']:.2f} | {r['shot']} | {r['word']} | {r['kind']} | {state} | {r['how'] if not r['ok'] else ''} |")
    lines += ["", f"{len(rows)} showable words, {missing} not shown. Mark other ways of showing a word with \"covers\": [\"word\"]."]
    os.makedirs(os.path.dirname(os.path.join(P, a.out)), exist_ok=True)
    open(os.path.join(P, a.out), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    for r in rows:
        if not r["ok"]:
            print(f"MISSING {r['t']:6.2f}s {r['shot']}  '{r['word']}' ({r['kind']}): {r['how']}")
    print(f"{len(rows)} showable words, {missing} not shown -> {a.out}")
    if a.sheet:
        print("detail sheet ->", detail_sheet(P, spec, rows, os.path.join(P, "qc", "detail_sheet.jpg")),
              "- LOOK at every tile with the detail checklist (plan-shots skill)")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
