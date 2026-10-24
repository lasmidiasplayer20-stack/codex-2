"""Compile the hand-written plan into the file both renderers build from.

  python compile_spec.py PROJECT [--spec plan/spec.json] [-o plan/spec_compiled.json] [--no-auto-sfx]

What it does (the After Effects engine and ra_preview.py both read the compiled file):
  * expands actor actions ("act": [{"t":..,"end":..,"kind":"wave"}]) into pose keys - repeated gestures
    (wave, nod, laugh, shiver, scrub, dance, cheer_bounce, shake_fist, pound, talk_hands, struggle, flail,
    swim_stroke, write, bounce) and one-shot moves (fall_down, faint, jump_once, sit_down, stand_up,
    throw_once, punch_once, double_take, flinch, slump_down)
  * adds the house sound design automatically unless audio.auto_sfx is false: a pop on every icon/prop pop-in,
    whooshes only on flash/light-leak/red-wipe/whip/zoom transitions, a glitch hit on glitch cuts and fx, an
    impact on camera shakes, cash on money rain, a swell into B&W moments (de-duplicated, never two cues
    within 0.18 s); hand-placed cues in audio.sfx are kept
  * fills defaults (cast idle, actor shadow), clamps keys into their shots and drops planning-only fields
  * house rules (v2.3): one colour per character (drops cast sleeve/pants/shoes and key face_color), shot "vehicles"
    become a seat layer + a door layer with the riders seated on the cushions (vehicles.py), creatures with gait
    frames flip them along their path (creatures.py gait), hand-made camera keys are kept inside the picture
"""
import argparse
import copy
import json
import os
import re

from ra_common import KIT

CYCLES = {
    # name: (period_s, [overrides per phase], base pose or None to keep the current pose)
    "wave":        (0.36, [{"aN": [115, 28]}, {"aN": [115, 60]}], "wave"),
    "nod":         (0.40, [{"head": 0}, {"head": 14}], None),
    "laugh":       (0.30, [{"lean": -8, "head": -12}, {"lean": 4, "head": 6}], None),
    "shiver":      (0.12, [{"lean": -2, "aN": [-5.5, -115.1]}, {"lean": 2, "aN": [-0.6, -116.4]}], "hug_self"),
    "scrub":       (0.24, [{"aN": [2.4, 96.8]}, {"aN": [25.3, 81.5]}], "hold_front"),
    "dance":       (0.60, [{"aF": [-130, -40], "aN": [40, 100], "lF": [-20, -10], "lN": [30, -40], "head": 10},
                           {"aF": [-40, -100], "aN": [130, 40], "lF": [-30, -40], "lN": [20, -10], "head": -10}], "dance"),
    "cheer_bounce": (0.42, [{"hip": [0, 6]}, {"hip": [0, -60], "lF": [-10, -40], "lN": [20, -50]}], "cheer"),
    "shake_fist":  (0.24, [{"aN": [42, 118]}, {"aN": [56, 96]}], "fists_up"),
    "pound":       (0.36, [{"aN": [118, 40]}, {"aN": [96, -6]}], "push"),
    "talk_hands":  (0.70, [{"aN": [52, 62]}, {"aN": [38, 92], "aF": [-30, -50]}], "talk_gesture"),
    "struggle":    (0.36, [{"lean": -10}, {"lean": 10}], None),
    "flail":       (0.30, [{"aF": [-150, -30], "aN": [120, 40]}, {"aF": [-110, -60], "aN": [160, 10]}], "fall"),
    "swim_stroke": (0.70, [{"aN": [96, 0], "aF": [40, 20]}, {"aN": [10, 30], "aF": [110, 0]}], "swim"),
    "write":       (0.20, [{"aN": [9.4, 94.3]}, {"aN": [15.8, 83.8]}], "hold_front"),
    "bounce":      (0.50, [{"hip": [0, 6]}, {"hip": [0, 20]}], None),
    "type":        (0.16, [{"aN": [7.4, 96.6], "aF": [41.9, 51.1]}, {"aN": [12.3, 86.5], "aF": [35.2, 59.2]}], "hold_front"),
    # small strokes at face height (makeup, combing, painting, shaving someone; with a held brush/comb/razor)
    "brush":       (0.26, [{"aN": [127.7, 22]}, {"aN": [72.9, 117.1]}], "brush_face"),
    "dig":         (0.55, [{"lean": 34, "aN": [24, 18], "aF": [37.3, 5.2]}, {"lean": 18, "aN": [70, 30], "aF": [76.8, 5.2]}], "dig"),
    "stir":        (0.30, [{"aN": [5.7, 93.3]}, {"aN": [19.2, 84.6]}], "hold_front"),
    "clap":        (0.24, [{"aF": [31.3, 87.9], "aN": [52.8, 116.9]}, {"aF": [38.0, 84.1], "aN": [34.4, 127.9]}], "clap"),
    "pull_rope":   (0.50, [{"lean": -18, "aN": [80, 6], "aF": [88, 5.2]}, {"lean": -8, "aN": [96, 4], "aF": [94.6, 5.1]}], "drag"),
    "knock":       (0.22, [{"aN": [96, 70]}, {"aN": [84, 40]}], "point_fwd"),
    "eat_bites":   (0.40, [{"aF": [67.1, 129.2]}, {"aF": [29.2, 128.9]}], "eat"),
    "phone_talk":  (0.70, [{"head": 6}, {"head": 0}], "phone_call"),
}
ONESHOTS = {
    "fall_down":   [(0.0, "fall", 0.14), (0.22, "lie_back", 0.2)],
    "faint":       [(0.0, "slump", 0.25), (0.35, "lie_back", 0.25)],
    "jump_once":   [(0.0, "crouch", 0.12), (0.14, "jump", 0.14), (0.42, "stand", 0.16)],
    "sit_down":    [(0.0, "sit", 0.3)],
    "stand_up":    [(0.0, "stand", 0.3)],
    "throw_once":  [(0.0, "throw_back", 0.18), (0.22, "throw", 0.1)],
    "punch_once":  [(0.0, "guard", 0.12), (0.14, "punch", 0.08), (0.4, "guard", 0.15)],
    "double_take": [(0.0, "stand", 0.1), (0.18, "shocked", 0.08)],
    "flinch":      [(0.0, "scared", 0.08)],
    "slump_down":  [(0.0, "slump", 0.2), (0.3, "sit_floor_sad", 0.3)],
    "shoot_once":  [(0.0, "aim", 0.12), (0.2, "aim", 0.05)],
    "salute_once": [(0.0, "salute", 0.2)],
    "fall_asleep": [(0.0, "slump", 0.3), (0.45, "lie_back", 0.3)],
}
TRANS_WHOOSH = {"flash": ("whoosh", -10, -0.22), "light_leak": ("whoosh", -10, -0.25), "red_wipe": ("whoosh", -11, -0.18),
                "whip": ("whoosh_short", -9, -0.12), "zoom_blur": ("whoosh_short", -10, -0.12), "glitch": ("glitch", -10, -0.05)}


def expand_actions(ac, sh):
    acts = ac.pop("act", [])
    # actions done TO another character ("to": cast id) are aimed later, once everyone's position is known
    aimed = [a for a in acts if a.get("to")]
    if aimed:
        ac.setdefault("_aimed", []).extend(aimed)
        acts = [a for a in acts if not a.get("to")]
    if not acts:
        return
    keys = list(ac.get("keys") or [])
    for a in acts:
        kind = a.get("kind")
        t0 = max(sh["t"], float(a.get("t", sh["t"])))
        t1 = min(sh["end"], float(a.get("end", sh["end"])))
        eyes, mouth = a.get("eyes"), a.get("mouth")
        if kind in CYCLES:
            per, phases, base = CYCLES[kind]
            per = a.get("period", per)
            half = per / len(phases)
            t = t0
            i = 0
            while t < t1 - 0.02:
                k = {"t": round(t, 3), "pose": a.get("pose") or base or _pose_at(keys, t) or "stand", "set": phases[i % len(phases)],
                     "dur": round(half * 0.8, 3), "auto": True}
                if i == 0 and eyes:
                    k["eyes"] = eyes
                if i == 0 and mouth:
                    k["mouth"] = mouth
                keys.append(k)
                t += half
                i += 1
            if a.get("then"):
                keys.append({"t": round(t1, 3), "pose": a["then"], "dur": 0.2, "auto": True})
        elif kind == "topple":
            # the whole body tips over stiffly around the feet, accelerating like a real fall (reference: "died")
            rot = float(a.get("rot", -78))
            d = float(a.get("dur", 0.42))
            ac.setdefault("tilt", []).extend([{"t": round(t0, 3), "rot": float(a.get("from", 0))},
                                              {"t": round(min(t1, t0 + d), 3), "rot": rot, "ease": "in"}])
            k = {"t": round(t0, 3), "pose": a.get("pose") or _pose_at(keys, t0) or "slump", "dur": 0.2, "auto": True}
            if eyes:
                k["eyes"] = eyes
            if mouth:
                k["mouth"] = mouth
            keys.append(k)
        elif kind in ONESHOTS:
            for j, (dt, pose, d) in enumerate(ONESHOTS[kind]):
                k = {"t": round(min(t1, t0 + dt), 3), "pose": pose, "dur": d, "auto": True}
                if j == 0 and eyes:
                    k["eyes"] = eyes
                if j == 0 and mouth:
                    k["mouth"] = mouth
                keys.append(k)
        else:
            print(f"warning: unknown action {kind!r} in {sh.get('id')}")
    keys.sort(key=lambda k: k["t"])
    ac["keys"] = keys


def _pose_at(keys, t):
    p = None
    for k in sorted(keys, key=lambda k: k["t"]):
        if k["t"] <= t and k.get("pose"):
            p = k["pose"]
    return p


def auto_sfx(spec):
    A = spec.setdefault("audio", {})
    if A.get("auto_sfx") is False:
        return 0
    sfxdir = A.get("sfx_dir", "audio/sfx")
    cues = []
    shots = spec["shots"]
    for i, sh in enumerate(shots):
        tr = (sh.get("transition") or "cut").rstrip("?")
        if i > 0 and tr in TRANS_WHOOSH:
            n, g, dt = TRANS_WHOOSH[tr]
            cues.append((sh["t"] + dt, n, g))
        for ic in sh.get("icons", []):
            if ic.get("pop", True) and ic.get("sfx", True):
                cues.append((float(ic.get("t", sh["t"])), "pop", -13))
        for p in sh.get("props", []):
            if p.get("pop", True) and float(p.get("t", sh["t"])) > sh["t"] + 0.02 and p.get("sfx", True):
                cues.append((float(p.get("t", sh["t"])), "pop_high", -16))
        for s in sh.get("shake", []):
            cues.append((float(s["t"]), "impact", -7))
        for fx in sh.get("fx", []):
            k = fx.get("kind")
            t = float(fx.get("t", sh["t"]))
            if k in ("money_rain",) or (k == "image_rain" and "money" in fx.get("file", "") + fx.get("sfx", "")):
                cues.append((t, "cash", -12))
            elif k == "glitch":
                cues.append((t, "glitch", -10))
            elif k == "flash":
                cues.append((t, "boom", -8))
        for st in sh.get("state", []):
            if st.get("kind") in ("bw", "gray"):
                cues.append((float(st.get("t", sh["t"])), "swell", -16))
    have = [(float(s["t"]), s.get("file", "")) for s in A.get("sfx", [])]
    cues.sort()
    added = 0
    last = -9
    for t, n, g in cues:
        if t - last < 0.18:
            continue
        if any(abs(t - ht) < 0.15 for ht, _ in have):
            continue
        A.setdefault("sfx", []).append({"t": round(max(0, t), 3), "file": f"{sfxdir}/{n}.wav", "gain_db": g, "auto": True})
        last = t
        added += 1
    # living creatures make their sounds: on entry, then every ~3 s while they are on screen
    import creatures as _CR
    for cu in _CR.sound_cues(spec):
        if any(abs(cu["t"] - ht) < 0.12 and hf == cu["file"] for ht, hf in have):
            continue
        A.setdefault("sfx", []).append(cu)
        added += 1
    A.setdefault("sfx", []).sort(key=lambda s: s["t"])
    return added


# ------------------------------------------------------------------------------------------------ auto camera
# Measured on the reference Shorts (frame-to-frame tracking): a new camera move starts every 0.4-1.2 s (on a word,
# a pop or an action). Each move is a jolt - about a quarter of it lands in the first frame, half in the first
# three - that decays into a steady drift in the same direction (~0.6-1.0 % of zoom per frame). Moves alternate:
# push in on whoever acts / whatever just appeared (1.25-1.5x), pull back out to the group (1.0-1.12x). Shots open
# tight and snap out. Walkers are tracked. Targets change between characters, so the camera also pans.
CAM = {"beat_min": 0.45, "beat_max": 1.25, "snap": 0.3, "z_in": (1.26, 1.46), "z_out": (1.02, 1.1),
       "z_open": (1.36, 1.5), "drift_in": (0.05, 0.1), "drift_out": (0.02, 0.04)}


def _actor_x(ac, t):
    mv = ac.get("move") or []
    if not mv:
        return float(ac.get("x", 540)), float(ac.get("y", 1700))
    mv = sorted(mv, key=lambda k: k["t"])
    if t <= mv[0]["t"]:
        return float(mv[0].get("x", ac.get("x", 540))), float(mv[0].get("y", ac.get("y", 1700)))
    for a, b in zip(mv, mv[1:]):
        if t < b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            return (a.get("x", 540) + (b.get("x", 540) - a.get("x", 540)) * u, a.get("y", 1700) + (b.get("y", 1700) - a.get("y", 1700)) * u)
    return float(mv[-1].get("x", 540)), float(mv[-1].get("y", 1700))


def _cam_pose_at(ac, t):
    p = None
    for k in sorted(ac.get("keys") or [], key=lambda k: k["t"]):
        if float(k["t"]) <= t + 0.15:
            p = (k.get("pose") or (p[0] if p else "stand"), k.get("set"))
    return p or ("stand", None)


def _head_offset(ac, t):
    """Head centre relative to the foot point in rig units (+x = facing side), solved from the pose at t."""
    try:
        import ra_rig as R
        pose, ov = _cam_pose_at(ac, t)
        J = R.solve(R.pose_params(pose, ov), 0.0, 0, 0, 1.6, 0, 0)
        return J["head"][0], J["head"][1]
    except Exception:
        return 0.0, -844.0


def _tilt(ac, t):
    import math as _m
    ks = sorted(ac.get("tilt") or [], key=lambda k: k["t"])
    if not ks:
        return float(ac.get("rot", 0))
    if t <= ks[0]["t"]:
        r = ks[0].get("rot", 0)
    elif t >= ks[-1]["t"]:
        r = ks[-1].get("rot", 0)
    else:
        r = 0
        for a, b in zip(ks, ks[1:]):
            if a["t"] <= t < b["t"]:
                u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
                r = a.get("rot", 0) + (b.get("rot", 0) - a.get("rot", 0)) * u
    return float(ac.get("rot", 0)) + float(r)


def _face(ac, t):
    import math as _m
    x, y = _actor_x(ac, t)
    s = float(ac.get("h", 1000)) / 1000.0
    hx, hy = _head_offset(ac, t)
    face = -1 if float(ac.get("face", 1)) < 0 else 1
    dx, dy = hx * s * face, hy * s
    r = _m.radians(_tilt(ac, t))                       # whole-body tilt (topple) turns the head around the feet
    return [x + dx * _m.cos(r) - dy * _m.sin(r), y + dx * _m.sin(r) + dy * _m.cos(r)]


def _active(sh, a, b, acts):
    """actors doing something in [a, b): pose keys, actions, holds starting, entrances, walking"""
    out = []
    for ac in acts:
        ts = [float(k.get("t", 0)) for k in ac.get("keys", []) if not k.get("auto")] + [float(k.get("t", 0)) for k in (ac.get("act", []) or ac.get("_act", []))]
        ts += [float(h.get("t", 0)) for h in ac.get("hold", [])]
        if ac.get("enter"):
            ts.append(float(ac["enter"].get("t", sh["t"])))
        if any(a - 0.05 <= x < b for x in ts) or (ac.get("move") and len(ac["move"]) > 1 and ac["move"][0]["t"] < b and ac["move"][-1]["t"] > a):
            out.append(ac)
    return out


def _fit_zoom(points, pad=260.0):
    """largest zoom that keeps all points (scene px) inside the frame with a margin"""
    if len(points) < 2:
        return 9.0
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    w, h = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    return max(1.0, min(1080.0 / max(w, 1), 1920.0 / max(h, 1)))


def _world(sh):
    """scene size of the shot: bg.world [W, H] for wide/tall locations (characters travel, the camera follows), else the frame"""
    w = (sh.get("bg") or {}).get("world")
    if isinstance(w, (list, tuple)) and len(w) == 2:
        return [max(1080.0, float(w[0])), max(1920.0, float(w[1]))]
    return None


def _clamp_focus(f, z, bgs=1.06, world=None):
    hx, hy = 540.0 / z, 960.0 / z
    if world:
        Ww, Hw = world
        x = min(max(f[0], hx), Ww - hx) if Ww > 2 * hx else Ww / 2
        y = min(max(f[1], hy), Hw - hy) if Hw > 2 * hy else Hw / 2
        return [round(x, 1), round(y, 1)]
    mx, my = 540.0 * (bgs - 1), 960.0 * (bgs - 1)
    return [round(min(max(f[0], hx - mx), 1080 - hx + mx), 1), round(min(max(f[1], hy - my), 1920 - hy + my), 1)]


def auto_camera(sh, spec, seed=0):
    import random
    # deterministic in every run and Python version (hash() of a string changes per process): the animatic the user
    # approves and the After Effects build get the same camera
    sid = str(sh.get("id", ""))
    rnd = random.Random(sum((i + 1) * ord(ch) for i, ch in enumerate(sid)) * 7919 + int(seed) * 104729 + 17)
    t0, t1 = float(sh["t"]), float(sh["end"])
    acts = [a for a in sh.get("actors", []) if a.get("cast")]
    # aim at where the characters really are: work on copies with the actions expanded (topple tilt, sit_down...)
    X = {}
    for a in acts:
        e = copy.deepcopy(a)
        try:
            expand_actions(e, sh)
        except Exception:
            e = a
        X[id(a)] = e

    def F(a, t):
        return _face(X.get(id(a), a), t)

    def AX(a, t):
        return _actor_x(X.get(id(a), a), t)
    # events that deserve a beat: pops, pose keys, actions, word onsets
    events = []
    for ic in sh.get("icons", []) + sh.get("props", []):
        tt = float(ic.get("t", t0))
        if t0 + 0.2 < tt < t1 - 0.25:
            events.append((tt, "pop", [float(ic.get("x", 540)), float(ic.get("y", 900))]))
    for a in acts:
        for k in a.get("keys", []):
            tt = float(k.get("t", t0))
            if t0 + 0.2 < tt < t1 - 0.25 and not k.get("auto"):
                events.append((tt, "act", a))
        for k in a.get("act", []) or a.get("_act", []):
            tt = float(k.get("t", t0))
            if t0 + 0.2 < tt < t1 - 0.25:
                events.append((tt, "act", a))
    # living creatures get beats too: when they appear and on the words that name them (the camera shows them)
    import creatures as _CR
    crs = sh.get("creatures", [])
    def C_at(c, t):
        pts = [_CR.state(c, i, t, t0) for i in _CR.copies(c)]
        hh = float(c.get("h", 200))
        return [sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts) - 0.5 * hh]
    for c in crs:
        ct = float(c.get("t", t0))
        if t0 + 0.2 < ct < t1 - 0.25:
            events.append((ct, "creature", c))
        names = set(w.lower() for w in (c.get("covers") or [])) | {str(c.get("id", "")).lower()}
        for cap in spec.get("captions", []):
            wt = float(cap["t"])
            word = re.sub(r"[^a-z]", "", str(cap.get("text", "")).lower())
            if t0 + 0.2 < wt < t1 - 0.25 and max(ct, t0) <= wt < float(c.get("end", t1)) and word and \
                    (word in names or word.rstrip("s") in names or _CR.animal_of(word) and _CR.animal_of(word) == _CR.animal_of(c.get("animal") or c.get("id"))):
                events.append((wt, "creature", c))
    words = [float(c["t"]) for c in spec.get("captions", []) if t0 + 0.3 < float(c["t"]) < t1 - 0.3]
    cands = sorted(set([round(e[0], 3) for e in events] + [round(w, 3) for w in words]))
    beats, last = [t0], t0
    while True:
        nxt = [c for c in cands if c >= last + CAM["beat_min"]]
        if not nxt or nxt[0] > t1 - 0.3:
            break
        # prefer an event within the window, else the first word after beat_min, never longer than beat_max
        win = [c for c in nxt if c <= last + CAM["beat_max"]]
        ev = [c for c in win if any(abs(c - e[0]) < 0.02 for e in events)]
        pick = ev[0] if ev else (win[0] if win else nxt[0])
        if pick - last > CAM["beat_max"] + 0.4 and win:
            pick = win[-1]
        beats.append(pick)
        last = pick
    beats.append(t1)
    # targets
    def group_target(t):
        """centre of the characters' bodies (between each head and its feet) and of the creatures on screen"""
        pts = []
        for a in acts:
            fx, fy = F(a, t)
            x, y = AX(a, t)
            pts.append(((fx + x) / 2, fy * 0.6 + y * 0.4))
        for c in crs:
            if float(c.get("t", t0)) <= t < float(c.get("end", t1)):
                pts.append(tuple(C_at(c, t)))
        if not pts:
            return [540.0, 900.0]
        return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
    main = max(acts, key=lambda a: float(a.get("h", 1000))) if acts else None
    def travel(a):
        mv = a.get("move") or []
        return sum(abs(float(q.get("x", 0)) - float(p.get("x", 0))) + abs(float(q.get("y", 0)) - float(p.get("y", 0)))
                   for p, q in zip(mv, mv[1:]))
    movers = sorted([a for a in acts if len(a.get("move") or []) > 1 and travel(a) > 60], key=travel, reverse=True)
    walker = movers[0] if movers else None
    keys = []
    z = rnd.uniform(*CAM["z_open"])
    first_target = F(main, t0) if main else [540.0, 900.0]
    WLD = _world(sh)
    keys.append({"t": round(t0, 3), "zoom": round(z, 3), "focus": _clamp_focus(first_target, z, world=WLD)})
    direction = "out"
    last_actor = main
    for i in range(len(beats) - 1):
        a, b = beats[i], beats[i + 1]
        dur = b - a
        snap = min(CAM["snap"], dur * 0.45)
        ev = [e for e in events if a - 0.02 <= e[0] < b - 0.05]
        if direction == "in":
            zt = rnd.uniform(*CAM["z_in"])
            tgt = None
            cr_tgt = False
            for e in ev:
                if e[1] == "act":
                    tgt = F(e[2], a + snap); last_actor = e[2]; break
            for e in ev:
                if e[1] == "creature":         # push in on the animal (with whoever is next to it)
                    cc = C_at(e[2], a + snap)
                    near = [x for x in acts if abs(F(x, a)[0] - cc[0]) < 450]
                    if near:
                        f_ = F(near[0], a + snap)
                        tgt = [(f_[0] + cc[0]) / 2, (f_[1] + cc[1]) / 2]
                        zt = min(zt, _fit_zoom([f_, cc]), 1.3)
                    else:
                        tgt = cc
                        zt = min(zt, 1.38)
                    cr_tgt = True
                    break
            for e in ev:
                if e[1] == "pop":
                    base = F(last_actor, a) if last_actor else [540.0, 900.0]
                    tgt = [(base[0] + e[2][0]) / 2, (base[1] + e[2][1]) / 2] if tgt is None else [(tgt[0] + e[2][0]) / 2, (tgt[1] + e[2][1]) / 2]
                    zt = min(zt, 1.32)
                    break
            vis_crs = [c for c in crs if float(c.get("t", t0)) <= a + snap < float(c.get("end", t1))]
            if tgt is None and vis_crs and (not acts or rnd.random() < 0.4):
                c = vis_crs[int(rnd.random() * len(vis_crs)) % len(vis_crs)]     # an animal on screen gets a close-up too
                cc = C_at(c, a + snap)
                near = [x for x in acts if abs(F(x, a)[0] - cc[0]) < 450]
                if near:
                    f_ = F(near[0], a + snap)
                    tgt = [(f_[0] + cc[0]) / 2, (f_[1] + cc[1]) / 2]
                    zt = min(zt, _fit_zoom([f_, cc]), 1.3)
                else:
                    tgt = cc
                    zt = min(zt, 1.38)
                cr_tgt = True
            if tgt is None:
                cand = [x for x in acts if x is not last_actor] if len(acts) > 1 and rnd.random() < 0.5 else acts
                pick = cand[0] if cand else None
                if pick is not None:
                    last_actor = pick
                tgt = F(pick, a + snap) if pick else [540.0, 900.0]
            # several characters on screen: push in on the group that matters, not one face (the samples keep the
            # characters involved in an action in frame together; single-face close-ups only for one-character beats)
            act = _active(sh, a, b, acts)
            upright = [x for x in acts if F(x, a + snap)[1] < float(x.get("y", 1700)) - 0.35 * float(x.get("h", 1000))]
            group = act[:] if act else []
            if group:
                near = sorted([x for x in upright if x not in group],
                              key=lambda x: abs(F(x, a)[0] - F(group[0], a)[0]))
                if near and abs(F(near[0], a)[0] - F(group[0], a)[0]) < 650:
                    group.append(near[0])
            elif len(upright) > 1:
                group = upright
            if len(group) > 1 and not cr_tgt:
                pts = [F(x, a + snap) for x in group]
                zt = min(zt, _fit_zoom(pts))
                tgt = [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts) + 140]
            zend = zt * (1 + rnd.uniform(*CAM["drift_in"]) * min(1.5, dur / 0.7))
        else:
            zt = rnd.uniform(*CAM["z_out"])
            tgt = group_target(a + snap)
            zend = max(1.0, zt * (1 - rnd.uniform(*CAM["drift_out"]) * min(1.5, dur / 0.7)))
        def body_c(x, t):          # middle of a character: between its feet and its (solved, tilted) head
            fx_, fy_ = F(x, t)
            rx_, ry_ = AX(x, t)
            return (fx_ + rx_) / 2, fy_ * 0.6 + ry_ * 0.4
        moving = walker is not None and abs(AX(walker, b)[0] - AX(walker, a)[0]) + abs(AX(walker, b)[1] - AX(walker, a)[1]) > 40
        if moving:                 # keep a walker in frame while it travels (follow it closely in a wide/tall world)
            wx, wy = body_c(walker, a + snap)
            kw = 0.7 if WLD else 0.5
            tgt = [(1 - kw) * tgt[0] + kw * wx, tgt[1] if not WLD else (1 - kw) * tgt[1] + kw * wy]
        tgt_end = tgt
        if moving:
            wx2, wy2 = body_c(walker, b)
            wx1, wy1 = body_c(walker, a + snap)
            kw = 0.85 if WLD else 0.5
            tgt_end = [tgt[0] + kw * (wx2 - wx1), tgt[1] + (kw * (wy2 - wy1) if WLD else 0)]
        if i == 0 and direction == "out":
            pass
        keys.append({"t": round(a + snap, 3), "zoom": round(zt, 3), "focus": _clamp_focus(tgt, zt, world=WLD), "ease": "out"})
        if b - (a + snap) > 0.06:
            keys.append({"t": round(b, 3), "zoom": round(zend, 3), "focus": _clamp_focus(tgt_end, zend, world=WLD), "ease": "linear"})
        direction = "in" if direction == "out" else "out"
    # de-duplicate equal times (keep the later key)
    out = []
    for k in keys:
        if out and abs(out[-1]["t"] - k["t"]) < 0.02:
            out[-1] = k
        else:
            out.append(k)
    return out


# ----------------------------------------------------------------------------------------------- aimed actions
AIM_POINTS = {"face": (0.28, 0.12), "cheek": (0.32, 0.18), "head": (0.0, -0.25), "mouth": (0.15, 0.25),
              "chest": (0.0, 1.05), "arm": (0.3, 1.1), "hand": (0.6, 1.4)}


def _ik2(root, target, L1, L2, sign=1.0):
    import math as _m
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = max(abs(L1 - L2) + 0.5, min(L1 + L2 - 0.5, _m.hypot(dx, dy)))
    phi = _m.degrees(_m.atan2(dx, dy))
    off = _m.degrees(_m.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))))
    best = None
    for au in (phi + off, phi - off):
        p1 = (root[0] + L1 * _m.sin(_m.radians(au)), root[1] + L1 * _m.cos(_m.radians(au)))
        al = _m.degrees(_m.atan2(target[0] - p1[0], target[1] - p1[1]))
        bend = (al - au + 540) % 360 - 180
        cand = ((au + 540) % 360 - 180, bend)
        if best is None or (bend * sign > 0 and not best[1] * sign > 0):
            best = cand
    return best


def aim_actions(spec, project=None):
    """Actions done to someone ({"kind": "brush", "to": "hobo", "at": "cheek"}): the arm reaches so the held tool's tip
    (or the empty hand) lands on that spot of the other character, then strokes around it. Works for brush (makeup,
    combing, painting), scrub/wipe (washing), touch, inject, feed, stab... Positions come from both characters' real
    poses, so it stays right when the plan moves people around."""
    import math as _m
    jobs = [(sh, ac) for sh in spec["shots"] for ac in sh.get("actors", []) if ac.get("_aimed")]
    if not jobs:
        return 0
    import ra_preview as RP
    import ra_rig as RR
    ev = RP.timeline_evaluator(spec)
    n = 0
    for sh, ac in jobs:
        keys = list(ac.get("keys") or [])
        for a in ac.pop("_aimed"):
            tgt = next((x for x in sh.get("actors", []) if x.get("cast") == a["to"] and x is not ac), None)
            if tgt is None:
                print(f"warning: {sh.get('id')}/{ac.get('cast')}: action target {a['to']!r} is not in the shot")
                continue
            t0 = max(sh["t"], float(a.get("t", sh["t"])))
            t1 = min(sh["end"], float(a.get("end", sh["end"])))
            hand = "aF" if str(a.get("hand", "N")).upper().startswith("F") else "aN"
            # target point in the world: the other character's head + an offset (head diameters, towards the doer)
            hx, hy = _joint_world(ev, spec, tgt, t0, "head")
            D = RR.RIG["head_d"] * float(tgt.get("h", 900)) / 1000.0
            at = a.get("at", "face")
            ox, oy = AIM_POINTS.get(at, (0.28, 0.12)) if isinstance(at, str) else at
            rx, _ = _root_xy(ac, t0)
            side = 1.0 if rx > hx else -1.0          # the doer stands on this side
            tx, ty = hx + side * ox * D, hy + oy * D
            # into the doer's rig space
            x0, y0 = _root_xy(ac, t0)
            s = float(ac.get("h", 900)) / 1000.0
            f = _face_at(ac, t0)
            r = -_m.radians(_tilt_deg(ac, t0))
            dx, dy = tx - x0, ty - y0
            dx, dy = dx * _m.cos(r) - dy * _m.sin(r), dx * _m.sin(r) + dy * _m.cos(r)
            T = (dx / (s * f), dy / s)
            base = a.get("pose") or "brush_face"
            vals = RR.pose_params(base)
            _sw, _sd = RR.cast_arms(spec["cast"].get(ac["cast"], {}), project or "")
            J = RR.solve(vals, t0, 0, 0, 1.6, 0, 0, sw=_sw, sd=_sd)
            root = J["limbs"][hand][0]
            # length of the held tool from the hand to its tip (rig units)
            L = 0.0
            for h in ac.get("hold", []):
                if h.get("grip") and h.get("style", "tool") == "tool" and ("a" + h.get("hand", "N")) == hand \
                        and float(h.get("t", -1e9)) <= t0 + 0.05 and float(h.get("end", 1e9)) >= t0:
                    try:
                        from PIL import Image
                        path = h["file"] if os.path.isabs(h["file"]) or not project else os.path.join(project, h["file"])
                        iw, ih = Image.open(path).size
                        w = float(h.get("w", 220))
                        L = _m.hypot((h["tip"][0] - h["grip"][0]) * w, (h["tip"][1] - h["grip"][1]) * w * ih / iw) * 0.92
                    except Exception:
                        L = 0.0
            L1, L2 = RR.RIG["arm_u"], RR.RIG["arm_l"]
            Rch = L1 + L2

            def hand_for(Tp):
                """where the hand goes so the tool tip (length L) touches Tp: the tool comes from in front of the doer,
                the hand stays in a comfortable reach (not folded behind the shoulder)"""
                if L <= 1:
                    return Tp
                base_a = _m.atan2(Tp[1] - root[1], Tp[0] - root[0])
                best, bs = None, 1e9
                for k in range(-16, 17):
                    ang = base_a + _m.radians(k * 6)
                    ux, uy = _m.cos(ang), _m.sin(ang)
                    H = (Tp[0] - L * ux, Tp[1] - L * uy)
                    d = _m.hypot(H[0] - root[0], H[1] - root[1])
                    pen = abs(k) * 0.4 + (0 if 0.35 * Rch <= d <= 0.92 * Rch else 40 + abs(d - 0.65 * Rch) * 0.2)
                    pen += 0 if H[0] > root[0] + 20 else 60          # in front of the body
                    pen += 0 if uy <= 0.35 else 10                    # tools come in level or from below
                    if pen < bs:
                        best, bs = H, pen
                return best
            strokes = []
            amp = float(a.get("amp", 0.05)) * RR.RIG["head_d"] * (float(tgt.get("h", 900)) / max(1.0, float(ac.get("h", 900))))
            for d in (-amp, amp):
                Tp = (T[0], T[1] + d)
                au, bend = _ik2(root, hand_for(Tp), L1, L2)
                strokes.append((round(au, 1), round(bend, 1)))
            per = float(a.get("period", CYCLES.get(a.get("kind"), (0.26,))[0]))
            half = per / 2
            t, i = t0, 0
            while t < t1 - 0.02:
                au, bend = strokes[i % 2]
                k = {"t": round(t, 3), "pose": base, "set": {hand: [au, bend]},
                     "dur": round(half * 0.8 if i else 0.2, 3), "auto": True}
                if i == 0 and a.get("eyes"):
                    k["eyes"] = a["eyes"]
                if i == 0 and a.get("mouth"):
                    k["mouth"] = a["mouth"]
                keys.append(k)
                t += half if i else 0.2
                i += 1
            # the tool points at the spot for the whole action (its tip stays on the cheek while the hand strokes)
            if L > 1:
                new_holds = []
                for h in ac.get("hold", []):
                    ht0, ht1 = float(h.get("t", sh["t"])), float(h.get("end", sh["end"]))
                    if ("a" + h.get("hand", "N")) != hand or ht1 <= t0 or ht0 >= t1 or h.get("style", "tool") != "tool":
                        new_holds.append(h)
                        continue
                    if ht0 < t0:
                        new_holds.append(dict(h, end=round(t0, 3)))
                    new_holds.append(dict(h, t=round(max(ht0, t0), 3), end=round(min(ht1, t1), 3), aim=[round(T[0], 1), round(T[1], 1)]))
                    if ht1 > t1:
                        new_holds.append(dict(h, t=round(t1, 3)))
                ac["hold"] = new_holds
            if a.get("then"):
                keys.append({"t": round(t1, 3), "pose": a["then"], "dur": 0.2, "auto": True})
            n += 1
        keys.sort(key=lambda k: k["t"])
        ac["keys"] = keys
    return n


# ----------------------------------------------------------------------------------------------- automatic steps
NO_STEP_POSES = {"sit", "sit_relaxed", "sit_floor", "sit_floor_sad", "slump_sit", "lie_back", "lie_front", "dead", "swim",
                 "float", "sink", "crawl", "kneel", "fall", "jump", "cower"}
HOLD_POSES = {"bend_grab", "drag", "drag_low", "lift_body", "carry_heavy", "hold_front", "hold_up", "hold_side", "push", "grab",
              "arms_crossed", "arms_crossed_front", "hands_hips", "hug_self"}     # hands busy: no walking arm swing


def _walk_state(walk, t):
    st = None
    for w in sorted(walk or [], key=lambda x: float(x.get("t", 0))):
        if float(w.get("t", 0)) <= t + 1e-4:
            st = w
    return st


def auto_steps(spec):
    """Characters never slide: wherever an actor's move keys carry it across the ground while no walk/run is keyed,
    add a walk cycle (backwards when it moves against its facing, no arm swing while it holds someone), with a
    cadence from the ground speed. A move key with "step": false (vehicles, ice, being carried) opts out."""
    n = 0
    for sh in spec["shots"]:
        acts = sh.get("actors", [])
        carriers = {}
        for ac in acts:
            for at in ac.get("attach", []) or []:
                carriers.setdefault(at.get("to"), []).append((float(at.get("t", sh["t"])), float(at.get("end", sh["end"]))))
        for ac in acts:
            if ac.get("attach"):
                continue                     # carried: it moves with the hand, its legs stay as posed
            mv = sorted(ac.get("move") or [], key=lambda k: float(k["t"]))
            h = float(ac.get("h", 900))
            walk = list(ac.get("walk") or [])
            added = []
            for a, b in zip(mv, mv[1:]):
                t0, t1 = max(float(a["t"]), sh["t"]), min(float(b["t"]), sh["end"])
                if t1 - t0 < 0.12 or a.get("step") is False or b.get("step") is False:
                    continue
                dx = float(b.get("x", ac.get("x", 540))) - float(a.get("x", ac.get("x", 540)))
                dy = float(b.get("y", ac.get("y", 1700))) - float(a.get("y", ac.get("y", 1700)))
                dist = (dx * dx + dy * dy) ** 0.5
                v = dist / (t1 - t0)
                if v < 0.03 * h:
                    continue
                pose = _pose_at(ac.get("keys", []), (t0 + t1) / 2) or "stand"
                if pose in NO_STEP_POSES:
                    continue
                st = _walk_state(walk, t0 + 0.01)
                if st and st.get("mode", "walk") in ("walk", "run") and not st.get("auto"):
                    continue                 # the planner keyed it
                face = -1 if float(ac.get("face", 1)) < 0 else 1
                for ft, fv in ac.get("flip", []):
                    if ft <= t0 + 0.01:
                        face = -1 if fv < 0 else 1
                back = dx * face < -0.25 * dist
                sp = max(1.1, min(2.6, v / (0.42 * h)))
                holding = any(x0 < t1 and x1 > t0 for x0, x1 in carriers.get(ac.get("cast"), [])) or pose in HOLD_POSES
                e = {"t": round(t0, 3), "mode": "walk", "speed": round(-sp if back else sp, 3), "auto": True}
                if holding:
                    e["arms"] = False
                added.append(e)
                prev = _walk_state(walk, t1 - 0.01) or {"mode": "none"}
                restore = {k: v2 for k, v2 in prev.items() if k != "t"}
                restore["t"] = round(t1, 3)
                restore["auto"] = True
                added.append(restore)
                n += 1
            if added:
                # a segment that starts where the previous one ended replaces its restore entry
                merged = []
                for e in sorted(walk + added, key=lambda x: float(x.get("t", 0))):
                    if merged and abs(float(merged[-1].get("t", 0)) - float(e.get("t", 0))) < 1e-3:
                        merged[-1] = e if e.get("mode") in ("walk", "run") else merged[-1]
                        continue
                    merged.append(e)
                ac["walk"] = merged
                if not any(float(w.get("t", 0)) <= sh["t"] + 1e-3 for w in merged):
                    ac["walk"].insert(0, {"t": sh["t"], "mode": "none", "auto": True})
    return n


# ----------------------------------------------------------------------------------------------- attachments
GRIPS = ("feet", "hip", "neck", "shoulder", "head", "hand_N", "hand_F")


def _root_xy(ac, t):
    """root (foot point) of an actor at t from x/y and move keys (linear, like both renderers)"""
    return _actor_x(ac, t)


def _face_at(ac, t):
    f = -1 if float(ac.get("face", 1)) < 0 else 1
    for ft, fv in ac.get("flip", []):
        if t >= ft:
            f = -1 if fv < 0 else 1
    return f


def _tilt_deg(ac, t):
    import ra_preview as RP
    return float(ac.get("rot", 0)) + RP.tilt_at(ac.get("tilt"), t)


def _joint_world(ev, spec, ac, t, joint):
    """scene position of one joint of an actor at t (pose timeline + walk/idle, scale, facing, tilt)"""
    import math as _m
    import ra_rig as RR
    cid = ac["cast"]
    cast = spec["cast"].get(cid, {})
    vals, ctl = ev.actor_state(cid, t)
    J = RR.solve(vals, t, ctl.get("walk", 0), ctl.get("run", 0), ctl.get("speed", 1.6), ctl.get("idle", 1), ctl.get("phase", 0),
                 tw=RR.RIG["torso_w"] * float(cast.get("build", 1.0)), arms=ctl.get("arms", 1.0),
                 sw=RR.cast_arms(cast)[0], sd=RR.cast_arms(cast)[1])
    if joint == "feet":
        p = (0.0, 0.0)
    elif joint in ("hand_N", "hand_F"):
        p = J["limbs"]["aN" if joint == "hand_N" else "aF"][2]
    else:
        p = J[joint]
    x, y = _root_xy(ac, t)
    s = float(ac.get("h", 900)) / float(RR.RIG.get("H", 1000))
    f = _face_at(ac, t)
    dx, dy = p[0] * s * f, p[1] * s
    r = _m.radians(_tilt_deg(ac, t))
    return (x + dx * _m.cos(r) - dy * _m.sin(r), y + dx * _m.sin(r) + dy * _m.cos(r))


def bake_attachments(spec):
    """'attach' on an actor: it is held by another actor's hand (dragged, carried, lifted, led by the hand).
    Baked into move keys every 2 frames from the carrier's solved hand, so After Effects and the preview agree.
      {"to": "sol1", "hand": "N", "grip": "neck", "t": 5.6, "end": 7.0, "snap": false, "blend": 0.2, "offset": [0, 0]}
    snap false (default): the body keeps its place when the hand takes it and then follows the hand's motion.
    snap true: the grip joint is pulled onto the hand over `blend` seconds."""
    jobs = [(sh, ac) for sh in spec["shots"] for ac in sh.get("actors", []) if ac.get("attach")]
    if not jobs:
        return 0
    import ra_preview as RP
    ev = RP.timeline_evaluator(spec)
    n = 0
    for sh, ac in jobs:
        for at in ac.pop("attach"):
            carrier = next((a for a in sh.get("actors", []) if a.get("cast") == at.get("to") and a is not ac), None)
            if carrier is None:
                print(f"warning: {sh.get('id')}/{ac.get('cast')}: attach target {at.get('to')!r} is not in the shot")
                continue
            t0 = max(float(sh["t"]), float(at.get("t", sh["t"])))
            t1 = min(float(sh["end"]), float(at.get("end", sh["end"])))
            if t1 - t0 < 0.05:
                continue
            hand = "hand_F" if str(at.get("hand", "N")).upper().startswith("F") else "hand_N"
            grip = at.get("grip", "neck")
            if grip not in GRIPS:
                grip = "neck"
            off = at.get("offset", [0, 0])
            step = 1.0 / 15
            ts, t = [], t0
            while t < t1 - 1e-6:
                ts.append(round(t, 3))
                t += step
            ts.append(round(t1, 3))
            orig = [_root_xy(ac, tt) for tt in ts]
            att = []
            for tt, (ox, oy) in zip(ts, orig):
                hx, hy = _joint_world(ev, spec, carrier, tt, hand)
                gx, gy = _joint_world(ev, spec, ac, tt, grip)
                att.append((ox + (hx - gx) + float(off[0]), oy + (hy - gy) + float(off[1])))
            if at.get("snap"):
                bl = max(0.01, float(at.get("blend", 0.2)))
                pos = []
                for tt, o, a in zip(ts, orig, att):
                    u = min(1.0, (tt - t0) / bl)
                    u = u * u * (3 - 2 * u)
                    pos.append((o[0] + (a[0] - o[0]) * u, o[1] + (a[1] - o[1]) * u))
            else:
                d0 = (orig[0][0] - att[0][0], orig[0][1] - att[0][1])
                pos = [(a[0] + d0[0], a[1] + d0[1]) for a in att]
            mv = [dict(k, ease="linear") for k in (ac.get("move") or []) if float(k["t"]) < t0 - 1e-3 or float(k["t"]) > t1 + 1e-3]
            if not any(float(k["t"]) < t0 for k in mv) and abs(t0 - float(sh["t"])) > 1e-3:
                mv.append({"t": round(float(sh["t"]), 3), "x": round(orig[0][0], 1), "y": round(orig[0][1], 1), "ease": "linear"})
            mv += [{"t": tt, "x": round(p[0], 1), "y": round(p[1], 1), "ease": "linear"} for tt, p in zip(ts, pos)]
            ac["move"] = sorted(mv, key=lambda k: float(k["t"]))
            n += 1
    return n


def fill_grips(spec, project=None):
    """every hold gets the prop's grip/tip/style from its sidecar (<image>.grip.json, estimated and written if missing)"""
    import props as PR
    for sh in spec["shots"]:
        for ac in sh.get("actors", []):
            for h in ac.get("hold", []):
                if h.get("grip") or not h.get("file"):
                    continue
                path = h["file"] if os.path.isabs(h["file"]) or not project else os.path.join(project, h["file"])
                if not os.path.exists(path):
                    continue
                try:
                    g = PR.load(path)
                except Exception as e:
                    print(f"warning: grip for {h['file']}: {e}")
                    continue
                h["grip"] = g["grip"]
                h.setdefault("tip", g.get("tip"))
                h.setdefault("style", g.get("style", "upright"))


def house_rules(spec):
    """The channel's character rules (user feedback, v2.3): one colour per character - head, body, arms and legs share
    the body colour, only the torso/head costume pieces differ - so limb clothing colours (sleeve, pants, shoes) and
    head-colour flushes (face_color) are dropped. spec.house = {"limb_colours": true, "face_colours": true} opts out."""
    H = spec.get("house", {}) or {}
    dropped = 0
    if not H.get("limb_colours"):
        for c in spec.get("cast", {}).values():
            for k in ("sleeve", "pants", "shoes"):
                if c.pop(k, None) is not None:
                    dropped += 1
    if not H.get("face_colours"):
        for sh in spec.get("shots", []):
            for ac in sh.get("actors", []):
                for k in ac.get("keys", []):
                    if k.pop("face_color", None) is not None:
                        dropped += 1
    return dropped


def clamp_cameras(spec):
    """hand-made camera keys stay inside the picture (a focus too close to an edge shows black bands)"""
    n = 0
    for sh in spec.get("shots", []):
        cam = sh.get("camera")
        if not isinstance(cam, list):
            continue
        bgs = float((sh.get("bg") or {}).get("scale", 1.06))
        for k in cam:
            if "focus" in k:
                f = _clamp_focus([float(k["focus"][0]), float(k["focus"][1])], max(1.0, float(k.get("zoom", 1.0))), bgs, _world(sh))
                if abs(f[0] - k["focus"][0]) > 0.5 or abs(f[1] - k["focus"][1]) > 0.5:
                    k["focus"] = f
                    n += 1
    return n


def compile_spec(spec, project=None):
    spec = copy.deepcopy(spec)
    import ra_rig as _RR
    import vehicles as _VH
    nh = house_rules(spec)                               # one colour per character
    nv = _VH.expand(spec, project)                       # riders sit IN vehicles: seat layer behind, doors in front
    for cid, c in spec.get("cast", {}).items():
        c.setdefault("idle", 1)
        # arms start at the outer shoulder corners / the garment's armholes (both renderers read this)
        c["shoulder"], c["shoulder_dn"] = _RR.cast_arms(c, project or "")
    auto = []
    for sh in spec["shots"]:
        sh["transition"] = (sh.get("transition") or "cut").rstrip("?")
        for k in ("say", "w", "camera_kind", "notes", "ideas", "show"):
            sh.pop(k, None)
        if not sh.get("camera") or sh.get("camera") == "auto":
            auto.append(sh)
        for ac in sh.get("actors", []):
            ac["_act"] = copy.deepcopy(ac.get("act", []))   # the camera plans its beats on the actions
            expand_actions(ac, sh)
            for k in ac.get("keys", []):
                k["t"] = min(max(float(k["t"]), sh["t"]), sh["end"] - 0.01)
    import creatures as _CR
    _CR.fill_from_sidecars(spec, project)                # creatures face the way their picture faces
    ng = _CR.expand_gaits(spec, project)                 # moving animals flip their gait frames (real leg motion)
    fill_grips(spec, project)                            # props are held by their handle, the right way round
    aim_actions(spec, project)                           # actions done to someone land on them (brush on the cheek)
    ns = auto_steps(spec)                                # nobody slides: moving feet step
    na = bake_attachments(spec)                          # carried / dragged characters follow the hand
    for sh in auto:                                      # then the camera, which sees where everyone really is
        sh["camera"] = auto_camera(sh, spec)
        sh["_camera_auto"] = True
    for sh in spec["shots"]:
        for ac in sh.get("actors", []):
            ac.pop("_act", None)
            ac.pop("_aimed", None)
    nc = clamp_cameras(spec)                             # hand-made camera keys never show past the picture
    n = auto_sfx(spec)
    spec.setdefault("_compiled", {})["auto_sfx"] = n
    for k, v in (("house_rules_dropped", nh), ("vehicles", nv), ("gait_creatures", ng), ("camera_keys_clamped", nc)):
        if v:
            spec["_compiled"][k] = v
    if na:
        spec["_compiled"]["attachments"] = na
    if ns:
        spec["_compiled"]["auto_steps"] = ns
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--spec", default="plan/spec.json")
    ap.add_argument("-o", "--out", default="plan/spec_compiled.json")
    ap.add_argument("--no-auto-sfx", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.project, a.spec), encoding="utf-8"))
    if a.no_auto_sfx:
        spec.setdefault("audio", {})["auto_sfx"] = False
    out = compile_spec(spec, a.project)
    json.dump(out, open(os.path.join(a.project, a.out), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    sfxdir = os.path.join(a.project, out.get("audio", {}).get("sfx_dir", "audio/sfx"))
    missing = sorted({s["file"] for s in out.get("audio", {}).get("sfx", []) if not os.path.exists(os.path.join(a.project, s["file"]))})
    print(f"compiled -> {os.path.join(a.project, a.out)} ({out['_compiled']['auto_sfx']} auto SFX cues)")
    C = out["_compiled"]
    if C.get("house_rules_dropped"):
        print(f"house rule: one colour per character - dropped {C['house_rules_dropped']} sleeve/pants/shoes/face_color settings")
    if C.get("vehicles"):
        print(f"{C['vehicles']} vehicle(s): seat layer behind the riders, doors in front - LOOK at full-size stills of them")
    if C.get("gait_creatures"):
        print(f"{C['gait_creatures']} creature(s) run their gait frames")
    if C.get("camera_keys_clamped"):
        print(f"{C['camera_keys_clamped']} hand-made camera key(s) moved inside the picture (no black edges)")
    if missing:
        print(f"missing SFX files ({len(missing)}): run  python {os.path.join(KIT, 'py', 'sfx_kit.py')} -o {sfxdir}")


if __name__ == "__main__":
    main()
