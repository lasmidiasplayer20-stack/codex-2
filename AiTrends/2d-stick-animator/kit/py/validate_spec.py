"""Check a scene spec against the engine schema and the house style before building.

  python validate_spec.py PROJECT [--spec plan/spec.json] [--report qc/plan_check.md]

FAIL = the build will break or the video will clearly miss the style; WARN = design note; INFO = statistics.
Exit code 1 when any FAIL is found.
"""
import argparse
import json
import os
import re
import statistics as st

import copy

import compile_spec as CS
from compile_spec import CYCLES, ONESHOTS
from ra_common import STYLE, load_data

POSES = load_data("poses.json")
FACES = load_data("faces.json")
PARTS = load_data("parts.json")
RIG = load_data("rig.json")
TRANS = {"cut", "flash", "light_leak", "red_wipe", "glitch", "bw_fade", "whip", "zoom_blur"}
FXK = {"image_rain", "money_rain", "embers", "dust", "snow", "rain", "smoke", "tint", "glitch", "flash", "video", "fire", "overlay"}
ICONK = {"emoji", "thought", "speech", "badge", "no"}
STATES = {"color", "gray", "silhouette", "red", "sick", "ghost"}
GRADES = {"none", "moody", "dark", "night", "warm", "cold", "sepia", "bw", "green", "red"}
# real heights of everyday objects as a share of a standing person (user feedback v2.3: a well half a person tall
# looked "terrible"); a prop whose file name names one is checked against the characters in its shot
REAL_SIZE = {"well": 0.85, "door": 1.15, "doorway": 1.15, "milepost": 0.5, "signpost": 1.0, "chair": 0.5, "table": 0.45,
             "desk": 0.45, "barrel": 0.45, "bench": 0.4, "bed": 0.35, "wardrobe": 1.1, "fridge": 1.0, "stove": 0.5,
             "bathtub": 0.35, "crate": 0.35, "mailbox": 0.6, "lamppost": 1.9, "streetlamp": 1.9}
_OPAQUE = {}


def opaque_height_ratio(path):
    """visible height / full picture width of a prop image (props are drawn at width w, transparent margin included)"""
    if path not in _OPAQUE:
        try:
            from PIL import Image
            im = Image.open(path)
            bb = im.convert("RGBA").getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
            _OPAQUE[path] = (bb[3] - bb[1]) / float(im.width) if bb else None
        except Exception:
            _OPAQUE[path] = None
    return _OPAQUE[path]


class Report:
    def __init__(self):
        self.lines = []
        self.fails = 0
        self.warns = 0

    def fail(self, m):
        self.fails += 1
        self.lines.append("FAIL  " + m)

    def warn(self, m):
        self.warns += 1
        self.lines.append("WARN  " + m)

    def info(self, m):
        self.lines.append("INFO  " + m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec.json")
    ap.add_argument("--report", default="qc/plan_check.md")
    a = ap.parse_args()
    P = a.project
    spec = json.load(open(os.path.join(P, a.spec), encoding="utf-8"))
    R = Report()
    M = spec.get("meta", {})
    dur = float(M.get("duration", 0))
    W, H = M.get("width", 1080), M.get("height", 1920)
    if not dur:
        R.fail("meta.duration missing")
    if (W, H) != (1080, 1920):
        R.warn(f"frame is {W}x{H}; the house format is 1080x1920 (9:16)")
    import story_length as SL
    chosen = SL.load(P)
    if chosen:
        if dur and abs(dur - chosen["seconds"]) > max(5, 0.12 * chosen["seconds"]):
            R.warn(f"duration {dur:.1f}s vs the chosen length {chosen['seconds']}s (story_length.py P --check-voice)")
        elif dur:
            R.info(f"duration {dur:.1f}s for the chosen {chosen['seconds']}s")
    else:
        lo, hi = STYLE["format"]["duration_s"]
        if dur and not (lo - 8 <= dur <= hi + 8):
            R.warn(f"duration {dur:.1f}s (samples: {lo}-{hi}s; no chosen length recorded in script/length.json)")

    def exists(rel):
        return rel and os.path.exists(os.path.join(P, rel))

    A = spec.get("audio", {})
    for k in ("voice", "music"):
        if A.get(k) and not exists(A[k]):
            R.warn(f"audio.{k} file not found: {A[k]}")
    for s in A.get("sfx", []):
        if not exists(s.get("file")):
            R.warn(f"sfx file not found: {s.get('file')}")
    whooshes = [s for s in A.get("sfx", []) if "whoosh" in s.get("file", "")]
    if dur and len(whooshes) > max(6, dur / 7):
        R.warn(f"{len(whooshes)} whooshes: the samples keep them to big transitions (about 2-9 per video)")

    caps = spec.get("captions", [])
    if not caps:
        R.fail("no captions: every sample has one-word yellow captions for the whole narration")
    reds = sum(1 for c in caps if c.get("color") == "red")
    if reds > 2:
        R.warn(f"{reds} red caption words (samples: 0-2 on the emotional peaks)")

    cast = spec.get("cast", {})
    for cid, c in cast.items():
        for p in c.get("parts", []):
            if p not in PARTS["head"] and p not in PARTS["torso"]:
                R.fail(f"cast {cid}: unknown part '{p}'")
        for acc in c.get("accessories", []):
            if not exists(acc.get("file")):
                R.fail(f"cast {cid}: accessory file missing {acc.get('file')}")
    cols = [c.get("color", "").upper() for c in cast.values()]
    if len(cols) != len(set(cols)):
        R.warn("two cast members share a body colour; the samples give each character its own colour")
    house = spec.get("house", {}) or {}
    limb = [cid for cid, c in cast.items() if any(k in c for k in ("sleeve", "pants", "shoes"))]
    if limb and not house.get("limb_colours"):
        R.warn(f"cast {', '.join(limb)}: sleeve/pants/shoes colours break the house rule (one colour per character: head, body, "
               f"arms and legs match; only the torso/head costume pieces differ) - compile_spec drops them; remove them")
    # ---- sound design: the animatic and the final must sound like the place and every action in it
    hand = [s for s in A.get("sfx", []) if not s.get("auto")]
    if dur and len(hand) < max(6, dur * 0.25):
        R.warn(f"only {len(hand)} hand-placed sound cues for {dur:.0f}s: plan the sound layer - an ambience bed under every "
               f"location (crowd, wind, traffic, room tone) and a real sound on every on-screen action (a starting pistol, "
               f"an engine, footsteps, bites, gulps, coughs, barks, cheers) - house-style sound-style.md")

    shots = spec.get("shots", [])
    if not shots:
        R.fail("no shots")
    durs = []
    prev_end = 0.0
    special = 0
    bw = 0
    inserts = 0
    last_bg = None
    same_bg_run = 0
    used_cast = set()
    for i, s in enumerate(shots):
        sid = s.get("id", f"#{i}")
        t0, t1 = float(s.get("t", -1)), float(s.get("end", -1))
        if abs(t0 - prev_end) > 0.02:
            R.fail(f"{sid}: starts at {t0:.2f}s but the previous shot ends at {prev_end:.2f}s (shots must be contiguous)")
        prev_end = t1
        d = t1 - t0
        durs.append(d)
        if d < 0.45:
            R.fail(f"{sid}: {d:.2f}s is too short to read (min ~0.6s)")
        elif d > 5.0:
            R.warn(f"{sid}: {d:.2f}s is long for this style (p90 2.95s): split it or add a punch-in / new action")
        bg = s.get("bg") or {}
        if not bg.get("file") and bg.get("kind") != "color":
            R.fail(f"{sid}: no background file")
        elif bg.get("file") and not exists(bg["file"]):
            R.fail(f"{sid}: background not found {bg['file']}")
        if bg.get("grade") and bg["grade"] not in GRADES:
            R.warn(f"{sid}: unknown grade {bg['grade']}")
        is_video = (bg.get("file", "").lower().endswith((".mp4", ".mov", ".webm", ".m4v")))
        if is_video:
            inserts += 1
        SW, SH = W, H                      # scene size: the frame or the location's world
        wl = bg.get("world")
        if wl is not None:
            if not (isinstance(wl, (list, tuple)) and len(wl) == 2 and wl[0] >= W and wl[1] >= H):
                R.fail(f"{sid}: bg.world must be [W, H] at least the frame ({W}x{H})")
            else:
                SW, SH = float(wl[0]), float(wl[1])
                if max(SW / W, SH / H) > 5:
                    R.warn(f"{sid}: bg.world {wl} is huge (more than 5 frames); split the journey into shots")
                if bg.get("file") and exists(bg["file"]) and not is_video:
                    try:
                        from PIL import Image
                        iw, ih = Image.open(os.path.join(P, bg["file"])).size
                        k = max(SW / iw, SH / ih)
                        if k > 1.35:
                            R.warn(f"{sid}: background {iw}x{ih} is stretched {k:.1f}x to cover the world {wl}: make it at "
                                   f"the world size (asset_list 'world')")
                    except Exception:
                        pass
        if bg.get("file") == last_bg:
            same_bg_run += 1
        else:
            same_bg_run = 0
        last_bg = bg.get("file")
        cam = s.get("camera") or []
        if cam == "auto":
            cam = []                                   # compile_spec plans the beats
            auto_cam = True
        else:
            auto_cam = False
        if auto_cam:
            pass
        elif len(cam) < 2:
            R.warn(f"{sid}: camera has fewer than 2 keys (every sample shot moves)")
        else:
            zs = [k.get("zoom", 1) for k in cam]
            fs = [tuple(k.get("focus", [540, 960])) for k in cam]
            if max(zs) - min(zs) < 0.03 and len(set(fs)) == 1:
                R.warn(f"{sid}: static camera (add a push-in, snap pull-out or pan)")
            for k in cam:
                if not (t0 - 0.01 <= k["t"] <= t1 + 0.01):
                    R.warn(f"{sid}: camera key at {k['t']:.2f}s is outside the shot")
                if k.get("zoom", 1) < 0.98 and not bg.get("scale"):
                    R.warn(f"{sid}: zoom {k.get('zoom')} < 1 may show background edges (set bg.scale >= 1.15)")
        tr = s.get("transition", "cut")
        if tr.endswith("?"):
            R.warn(f"{sid}: transition '{tr}' is a suggestion: decide (cut/flash/light_leak/...) and remove the '?'")
            tr = tr[:-1]
        if tr not in TRANS:
            R.fail(f"{sid}: unknown transition {tr}")
        if tr != "cut":
            special += 1
        for stt in s.get("state", []):
            if stt.get("kind") in ("bw", "gray"):
                bw += 1
        acts = s.get("actors", [])
        if not acts and not is_video and not s.get("props") and not s.get("icons"):
            R.warn(f"{sid}: nothing animated on screen (no actors, props or icons)")
        for ac in acts:
            c = ac.get("cast")
            used_cast.add(c)
            if c not in cast:
                R.fail(f"{sid}: actor cast '{c}' is not in cast{{}}")
            h = ac.get("h", 900)
            y = ac.get("y", 1650)
            if h < 200:
                R.warn(f"{sid}/{c}: h={h}px is tiny (samples: 45-110% of frame height for leads, 25-40% for crowds)")
            if y - h * 1.0 < -0.15 * H and not ac.get("crop"):
                R.warn(f"{sid}/{c}: head is off the top of the frame (y-h={y - h:.0f}); set crop:true if intended")
            keys = ac.get("keys", [])
            if not keys:
                R.warn(f"{sid}/{c}: no pose keys (defaults to stand)")
            for k in keys:
                if k.get("pose") and k["pose"] not in POSES:
                    R.fail(f"{sid}/{c}: unknown pose '{k['pose']}'")
                if k.get("eyes") is not None and isinstance(k["eyes"], str) and k["eyes"] not in FACES["eye_codes"]:
                    R.fail(f"{sid}/{c}: unknown eyes '{k['eyes']}'")
                if k.get("mouth") is not None and isinstance(k["mouth"], str) and k["mouth"] not in FACES["mouth_codes"]:
                    R.fail(f"{sid}/{c}: unknown mouth '{k['mouth']}'")
                if not (t0 - 0.01 <= k.get("t", t0) <= t1 + 0.01):
                    R.warn(f"{sid}/{c}: key at {k.get('t')}s outside the shot")
                fc = k.get("face_color")
                if isinstance(fc, str) and fc not in ("none", "") and not fc.startswith("#") and fc not in RIG.get("face_colors", {}):
                    R.fail(f"{sid}/{c}: unknown face_color '{fc}' (use none, #hex or {', '.join(RIG.get('face_colors', {}))})")
                if fc not in (None, "none", "") and not house.get("face_colours"):
                    R.warn(f"{sid}/{c}: face_color '{fc}' at {k.get('t')}s recolours only the head - viewers read it as a "
                           f"broken character (house rule: one colour per character); act it with eyes, mouth and pose")
            if any(k.get("pose") in ("sit", "sit_relaxed") for k in keys) and any(
                    re.search(r"car|cart|wagon|carriage|coach|boat|bus|truck|tram", os.path.basename(p.get("file", "")))
                    and not re.search(r"_back|_front", p.get("file", "")) for p in s.get("props", [])):
                R.warn(f"{sid}/{c}: seated next to a vehicle prop - use the shot's \"vehicles\" list (vehicles.py) so the "
                       f"rider sits IN it: seat layer behind, doors in front, thighs on the cushion")
            # the head must stay inside the scene (a topple or fall towards the near edge ends off screen)
            if not ac.get("enter") and not ac.get("exit") and not ac.get("crop"):
                try:
                    e = copy.deepcopy(ac)
                    CS.expand_actions(e, s)
                    n = max(2, int((t1 - t0) / 0.1))
                    for i in range(n + 1):
                        tt = t0 + (t1 - t0) * i / n
                        hx, hy = CS._face(e, tt)
                        fx = CS._actor_x(e, tt)[0]
                        if not (0 <= fx <= SW):     # walking in or out: allowed
                            continue
                        if hx < -40 or hx > SW + 40 or hy > SH:
                            R.warn(f"{sid}/{c}: the head leaves the frame at {tt:.2f}s ({hx:.0f}, {hy:.0f}) - move the actor or "
                                   f"flip the fall/topple direction so the face stays on screen")
                            break
                except Exception:
                    pass
            for at in ac.get("attach", []):
                if at.get("to") not in [o.get("cast") for o in acts if o is not ac]:
                    R.fail(f"{sid}/{c}: attach.to '{at.get('to')}' is not another actor in this shot")
                if at.get("grip", "neck") not in CS.GRIPS:
                    R.fail(f"{sid}/{c}: attach.grip must be one of {', '.join(CS.GRIPS)}")
            for act in ac.get("act", []):
                if act.get("to") and act["to"] not in [o.get("cast") for o in acts if o is not ac]:
                    R.fail(f"{sid}/{c}: action '{act.get('kind')}' is done to '{act['to']}', who is not in this shot")
                if act.get("kind") not in CYCLES and act.get("kind") not in ONESHOTS and act.get("kind") != "topple":
                    R.fail(f"{sid}/{c}: unknown action '{act.get('kind')}' (see compile_spec.py)")
            alive = len(keys) > 1 or ac.get("act") or ac.get("walk") or ac.get("talk") or ac.get("move") or ac.get("enter")
            if d > 1.4 and not alive:
                R.warn(f"{sid}/{c}: holds one pose for {d:.1f}s; give it an action on a word (pose change, talk, walk)")
            if ac.get("state", "color") not in STATES:
                R.fail(f"{sid}/{c}: unknown state {ac.get('state')}")
            for hd in ac.get("hold", []):
                if float(hd.get("w", 220)) > 600:
                    R.warn(f"{sid}/{c}: held prop {hd.get('file')} is {hd.get('w')} wide - more than half the character's height; check its size")
                if not exists(hd.get("file")):
                    R.fail(f"{sid}/{c}: held prop missing {hd.get('file')}")
        people = sorted(float(a.get("h", 900)) for a in acts if not a.get("crop"))
        for p in s.get("props", []):
            if not exists(p.get("file")):
                R.fail(f"{sid}: prop missing {p.get('file')}")
                continue
            words = set(re.split(r"[^a-z]+", os.path.splitext(os.path.basename(p["file"]))[0].lower()))
            real = max((REAL_SIZE[w] for w in words if w in REAL_SIZE), default=None)
            k = opaque_height_ratio(os.path.join(P, p["file"])) if real and people and not p.get("screen") else None
            if k:
                person = people[len(people) // 2]
                drawn, want = float(p.get("w", 300)) * k, real * person
                if not 0.6 * want <= drawn <= 1.7 * want:
                    R.warn(f"{sid}: {os.path.basename(p['file'])} is drawn {drawn:.0f}px tall next to {person:.0f}px characters - "
                           f"a real one is ~{real:.2f} x a person ({want:.0f}px): set w ~{float(p.get('w', 300)) * want / drawn:.0f}")
        for v in s.get("vehicles", []):
            if not exists(v.get("file")):
                R.fail(f"{sid}: vehicle picture missing {v.get('file')}")
            for r in v.get("riders", []):
                used_cast.add(r.get("cast"))
                if r.get("cast") not in cast:
                    R.fail(f"{sid}: vehicle rider '{r.get('cast')}' is not in cast{{}}")
        for cr in s.get("creatures", []):
            if cr.get("behave") in ("walk", "flee", "wander", "hop", "peck", "fly") and cr.get("gait") is not False:
                side = {}
                try:
                    side = json.load(open(os.path.join(P, cr.get("file", "")) + ".creature.json", encoding="utf-8"))
                except Exception:
                    pass
                if not (cr.get("gait") or side.get("gait")):
                    R.warn(f"{sid}: creature '{cr.get('id', cr.get('animal'))}' moves ({cr.get('behave')}) as a still picture - "
                           f"it reads as a doll: python creatures.py gait {cr.get('file')} --kind "
                           f"{'run' if cr.get('behave') == 'flee' else 'walk'} --yes (real leg motion)")
        for ic in s.get("icons", []):
            if ic.get("kind", "emoji") not in ICONK:
                R.fail(f"{sid}: unknown icon kind {ic.get('kind')}")
            if ic.get("file") and not exists(ic["file"]):
                R.fail(f"{sid}: icon file missing {ic['file']}")
        for fx in s.get("fx", []):
            if fx.get("kind") not in FXK:
                R.fail(f"{sid}: unknown fx kind {fx.get('kind')}")
            if fx.get("kind") in ("image_rain", "money_rain", "video", "fire", "overlay") and not exists(fx.get("file")):
                R.fail(f"{sid}: fx file missing {fx.get('file')}")
        if same_bg_run >= 3 and not acts:
            R.warn(f"{sid}: 4 shots in a row on the same background with nothing new; vary framing or location")
    # ---- characters too close: arms reach into the other body (keep a gap unless they really touch)
    for s in shots:
        acts_ = [x for x in s.get("actors", []) if x.get("cast") and not x.get("attach")]
        for i in range(len(acts_)):
            for j in range(i + 1, len(acts_)):
                q1, q2 = acts_[i], acts_[j]
                if q1.get("move") or q2.get("move") or abs(float(q1.get("y", 1700)) - float(q2.get("y", 1700))) > 250:
                    continue
                hh = (float(q1.get("h", 1000)) + float(q2.get("h", 1000))) / 2
                dx = abs(float(q1.get("x", 540)) - float(q2.get("x", 540)))
                def acts_on(x, y):
                    return any(z.get("to") == y.get("cast") for z in (x.get("act") or []) + (x.get("attach") or []))
                low = {"lie_back", "lie_front", "dead", "sleep_lie", "sit_floor", "sit_floor_sad", "slump_sit", "crawl", "sit",
                       "sit_relaxed", "kneel", "crouch"}
                lying = any(k.get("pose") in low for k in (q1.get("keys") or []) + (q2.get("keys") or []))
                if dx < 0.45 * hh and not (q1.get("touch") or q2.get("touch") or acts_on(q1, q2) or acts_on(q2, q1) or lying):
                    R.warn(f"{s.get('id')}: {q1.get('cast')} and {q2.get('cast')} stand {dx:.0f}px apart at height ~{hh:.0f}px - "
                           f"arms reach into the other body; keep them at least {0.45 * hh:.0f}px apart (or set \"touch\": true "
                           "for a handshake, hug or push)")
    # ---- icons: concepts only and sparingly (the samples: ~5-8 icon moments a minute); characters act, animals live
    EMO = {"angry_face", "astonished_face", "cold_face", "crying_face", "dizzy_face", "exploding_head", "face_screaming_in_fear",
           "face_vomiting", "face_with_open_mouth", "face_with_rolling_eyes", "face_with_spiral_eyes", "face_with_tears_of_joy",
           "fearful_face", "grimacing_face", "hot_face", "loudly_crying_face", "lying_face", "money_mouth_face", "nauseated_face",
           "pouting_face", "shushing_face", "sleeping_face", "smiling_face_with_horns", "smiling_face_with_sunglasses",
           "thinking_face", "zipper_mouth_face", "heavy_black_heart", "broken_heart", "hundred_points_symbol", "thumbs_up_sign",
           "thumbs_down_sign", "ok_hand", "ok_hand_sign", "clapping_hands_sign", "raised_hand", "waving_hand_sign", "zzz",
           "sweat_droplets", "right_anger_bubble", "flexed_biceps", "fisted_hand_sign", "eyes", "dizzy_symbol", "collision_symbol",
           "double_exclamation_mark", "exclamation_mark", "question_mark", "sparkles", "glowing_star", "party_popper"}
    PEOPLE = {"detective", "man", "woman", "baby", "child", "older_man", "older_woman", "police_officer", "guardsman",
              "construction_worker", "ninja", "princess", "prince", "bride_with_veil", "superhero", "supervillain", "mage",
              "genie", "zombie", "vampire", "bust_in_silhouette", "busts_in_silhouette"}
    import creatures as _CR
    moments, badges = [], 0
    for s in shots:
        sid = s.get("id", "?")
        ics = s.get("icons", [])
        for ic in ics:
            name = os.path.splitext(os.path.basename(ic.get("file", "") or ""))[0].lower()
            t = float(ic.get("t", s["t"]))
            moments.append((t, sid, name))
            if ic.get("kind") == "badge":
                badges += 1
            if name in EMO:
                R.warn(f"{sid}: emotion/gesture icon '{name}' at {t:.2f}s - the character acts it (eyes, mouth, face colour, "
                       "pose); drop the icon")
            elif name in PEOPLE:
                R.warn(f"{sid}: person icon '{name}' at {t:.2f}s - people are characters, not icons")
            elif _CR.animal_of(name.replace("_face", "")) and not ic.get("concept"):
                R.warn(f"{sid}: animal icon '{name}' at {t:.2f}s - living things in the story are creatures (whole animal, "
                       "moving, with its sound); set \"concept\": true only for a figure of speech")
        spans = sorted((float(ic.get("t", s["t"])), float(ic.get("end", s["end"]))) for ic in ics if ic.get("kind") not in ("badge",))
        for b0, _ in spans:
            n_on = sum(1 for a0, a1 in spans if a0 <= b0 + 0.05 < a1)
            if n_on > 2:
                R.warn(f"{sid}: {n_on} icons on screen at once at {b0:.2f}s - at most a pair (rat + skull), usually one")
                break
        for c in s.get("creatures", []):
            if not exists(c.get("file")):
                R.fail(f"{sid}: creature image missing {c.get('file')}")
            if c.get("behave", "idle") not in _CR.BEHAVES:
                R.fail(f"{sid}: creature behave '{c.get('behave')}' unknown ({', '.join(_CR.BEHAVES)})")
            an = _CR.animal_of(c.get("animal") or c.get("id") or "")
            if not c.get("sound") and c.get("sound") is not False and not (an and _CR.ANIMALS[an]["sound"] is None):
                R.warn(f"{sid}: creature {c.get('id')} has no sound - living animals are heard (cluck, bark, moo...); "
                       "add a sound asset or set \"sound\": false")
            elif c.get("sound") and not exists(c["sound"]):
                R.fail(f"{sid}: creature sound missing {c['sound']}")
            if float(c.get("h", 200)) < 50:
                R.warn(f"{sid}: creature {c.get('id')} is tiny (h {c.get('h')}); animals must read on a phone")
    if dur:
        pm = len(moments) / max(dur / 60.0, 0.25)
        R.info(f"icon moments {len(moments)} ({pm:.1f} per minute; samples ~5-8), clock badges {badges}")
        if pm > 9:
            R.warn(f"{len(moments)} icon moments ({pm:.0f}/min) - far more than the samples (~5-8/min): let the characters "
                   "act it (faces, poses, props, creatures) and keep icons for abstract concepts (death, danger, an idea, time)")
        if badges > 3:
            R.warn(f"{badges} clock badges - keep durations/counts to 1-3 per video")
    if shots and dur and abs(prev_end - dur) > 0.05:
        R.fail(f"last shot ends at {prev_end:.2f}s but meta.duration is {dur:.2f}s")
    for cid in cast:
        if cid not in used_cast:
            R.warn(f"cast {cid} is never used")
    if durs:
        q = sorted(durs)
        med = st.median(q)
        p90 = q[int(0.9 * (len(q) - 1))]
        tgt = STYLE["edit"]["shot_len_s"]
        R.info(f"{len(durs)} shots, median {med:.2f}s (target {tgt['median']}), p90 {p90:.2f}s (target {tgt['p90']}), "
               f"min {q[0]:.2f}s, max {q[-1]:.2f}s")
        if med > 2.0:
            R.warn(f"median shot {med:.2f}s is slow for this style (target ~1.3s)")
        if med < 0.9:
            R.warn(f"median shot {med:.2f}s is frantic (target ~1.3s)")
    R.info(f"special transitions {special} (samples 2-6), B&W moments {bw} (samples 1-4), live/video inserts {inserts} (samples 0-3)")
    if special > 9:
        R.warn("too many special transitions; most cuts are hard cuts")
    # story coverage: every object named and every action described is shown on its word
    try:
        import coverage as CV
        wp = os.path.join(P, "timing", "words.json")
        if os.path.exists(wp):
            words = json.load(open(wp, encoding="utf-8"))
            words = words.get("words", words) if isinstance(words, dict) else words
            rows = CV.check(spec, words)
            miss = [r for r in rows if not r["ok"]]
            for r in miss:
                R.warn(f"{r['shot']}: '{r['word']}' at {r['t']:.2f}s is said but not shown ({r['kind']}): {r['how']}")
            R.info(f"story coverage: {len(rows) - len(miss)}/{len(rows)} named objects and actions on screen "
                   f"(python coverage.py P --visible also checks they can be seen)")
    except Exception as e:
        R.warn(f"coverage check failed: {e}")
    os.makedirs(os.path.join(P, os.path.dirname(a.report)), exist_ok=True)
    txt = "# Plan check\n\n" + "\n".join(R.lines) + f"\n\nRESULT: {R.fails} FAIL, {R.warns} WARN\n"
    open(os.path.join(P, a.report), "w", encoding="utf-8").write(txt)
    print(txt)
    raise SystemExit(1 if R.fails else 0)


if __name__ == "__main__":
    main()
