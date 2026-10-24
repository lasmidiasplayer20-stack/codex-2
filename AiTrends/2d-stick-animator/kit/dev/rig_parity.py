"""Check that the After Effects rig expressions and the Python rig (ra_rig.py) agree: joints of every pose for every
character, walking / running / idle frames, which arm layers show (far arm behind or in front, near arm behind the
chest in a three-quarter view) and the torso width and clothing transform of the three-quarter turn.

  python kit/dev/rig_parity.py PROJECT [--kit KIT]

It writes PROJECT/parity_sliders.json, runs node kit/dev/mock_ae.js PROJECT --parity and compares. Exit code 1 on a
difference above 0.05 rig units (or any layer showing differently).
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(sys.argv[sys.argv.index("--kit") + 1]) if "--kit" in sys.argv else os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KIT, "py"))
import ra_rig as R  # noqa: E402

P = os.path.abspath(sys.argv[1])
spec = json.load(open(os.path.join(P, "plan", "spec_compiled.json"), encoding="utf-8"))
RIG = R.RIG
names = sorted(n for n, v in R.POSES.items() if isinstance(v, dict))
MOTION = [  # (walk, run, idle, t)
    (1.0, 0.0, 0.0, 0.31), (0.0, 1.0, 0.0, 0.77), (0.0, 0.0, 1.0, 1.13), (0.5, 0.0, 1.0, 2.05)]

cases, expect = [], []
for cid, cast in spec["cast"].items():
    sw, sd = R.cast_arms(cast, P)
    phase = sum(ord(ch) for ch in cid) * 7 % 360        # any value: both sides read the same slider
    for i, pname in enumerate(names):
        params = R.pose_params(pname)
        motions = [(0.0, 0.0, 0.0, 0.0)] + ([MOTION[i % len(MOTION)]] if i % 3 == 0 else [])
        for (w, r, idl, t) in motions:
            s = dict(params)
            s.update({"walk": w, "run": r, "idle": idl, "wspeed": 1.6, "armSw": 1, "phase": phase})
            J = R.solve(params, t, w, r, 1.6, idl, phase, sw=sw, sd=sd)
            cases.append({"comp": "CHAR_" + cid, "s": s, "t": t})
            expect.append((cid, pname, (w, r, idl, t), J))
json.dump({"cases": cases}, open(os.path.join(P, "parity_sliders.json"), "w"))
node = subprocess.run(["node", os.path.join(KIT, "dev", "mock_ae.js"), P, "--kit", KIT, "--parity"],
                      capture_output=True, text=True)
if not os.path.exists(os.path.join(P, "parity_ae.json")) or "parity dump written" not in node.stdout:
    print(node.stdout[-3000:], node.stderr[-3000:])
    sys.exit(1)
ae = json.load(open(os.path.join(P, "parity_ae.json"), encoding="utf-8"))["cases"]

worst, bad, n = 0.0, [], 0
for (cid, pname, mo, J), out in zip(expect, ae):
    turn = J["turn"]
    three_q = turn < 0.5
    ff = three_q or R.far_arm_front(J, 1.0 if J.get("far_front") else 0.0)
    want_op = {"ARM_N_BACK": 100 if three_q else 0, "ARM_N": 0 if three_q else 100,
               "ARM_F": 0 if ff else 100, "ARM_F_FRONT": 100 if ff else 0}
    for ln, v in want_op.items():
        if out["opacity"].get(ln) != v:
            bad.append("%s %s %s: %s opacity AE %s, Python %s" % (cid, pname, mo, ln, out["opacity"].get(ln), v))
    for ln, L in (("ARM_F", "aF"), ("ARM_N", "aN"), ("ARM_N_BACK", "aN"), ("ARM_F_FRONT", "aF"), ("LEG_F", "lF"), ("LEG_N", "lN")):
        pts = out["limbs"].get(ln)
        if pts is None:
            bad.append("%s: no %s layer" % (cid, ln))
            continue
        for a, b in zip(pts, J["limbs"][L][:3]):
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            worst = max(worst, d)
            n += 1
            if d > 0.05:
                bad.append("%s %s %s: %s joint AE %s, Python %s" % (cid, pname, mo, ln, a, b))
    if out["head"] is not None:
        d = math.hypot(out["head"][0] - J["head"][0], out["head"][1] - J["head"][1])
        worst = max(worst, d)
        if d > 0.05:
            bad.append("%s %s: head AE %s, Python %s" % (cid, pname, out["head"], J["head"]))
    ts = 1.0 - RIG.get("torso_turn", 0.0) * (1.0 - turn)
    shift = RIG.get("torso_turn_shift", 0.0) * RIG["torso_w"] * (1.0 - turn)
    tw = RIG["torso_w"] * float(spec["cast"][cid].get("build", 1.0))
    if out["torsoW"] is not None and abs(out["torsoW"] - tw * ts) > 0.05:
        bad.append("%s %s: torso width AE %s, Python %s" % (cid, pname, out["torsoW"], tw * ts))
    if out["clothes"]:
        if abs(out["clothes"]["scale"][0] - 100 * ts) > 0.05 or abs(out["clothes"]["pos"][0] - shift) > 0.05:
            bad.append("%s %s: clothes AE %s, Python scale %s shift %s" % (cid, pname, out["clothes"], 100 * ts, shift))

print("rig parity: %d cases, %d joints, worst joint difference %.4f rig units, %d problems" % (len(cases), n, worst, len(bad)))
for b in bad[:40]:
    print("  " + b)
sys.exit(1 if bad else 0)
