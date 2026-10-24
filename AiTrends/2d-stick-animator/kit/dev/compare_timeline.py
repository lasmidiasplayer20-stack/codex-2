"""Check that the After Effects engine keys every character exactly like the preview renderer (dev tool).

  node kit/dev/mock_ae.js PROJECT --timeline      # dry-run build, dumps qc/mock_timeline.json
  python kit/dev/compare_timeline.py PROJECT      # compares it with ra_preview.py's timelines

Compares the hold controls (walk, run, wspeed, talk, gaze, eyes, mouth) at every on-screen sample and the pose sliders
wherever the pose is at rest (the mock interpolates linearly, the preview with AE-style eases, so moving
samples are skipped). Exit code 1 on any mismatch.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))
import ra_preview as RP  # noqa: E402
from compile_spec import compile_spec  # noqa: E402


def main():
    P = sys.argv[1]
    mock = json.load(open(os.path.join(P, "qc", "mock_timeline.json"), encoding="utf-8"))
    sp = os.path.join(P, "plan", "spec_compiled.json")
    spec = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else compile_spec(json.load(open(os.path.join(P, "plan", "spec.json"), encoding="utf-8")))
    R = RP.Renderer(P, spec, 0.25, 15)
    ec, mc = RP.FACES["eye_codes"], RP.FACES["mouth_codes"]
    bad = 0
    for cid, rec in mock["chars"].items():
        tl = R.timelines.get(cid)
        if not tl:
            print(f"{cid}: no preview timeline")
            bad += 1
            continue
        n = len(rec.get("walk", []))
        spans = [(sh["t"], sh["end"]) for sh in spec["shots"] if any(a.get("cast") == cid for a in sh.get("actors", []))]
        mism = []
        for i in range(n):
            t = round(mock["t0"] + i * mock["step"], 3)
            if not any(a <= t < b for a, b in spans):
                continue   # off screen: values held before the first key do not matter
            exp = {"walk": RP.hold(tl["walk"], t, 0), "run": RP.hold(tl["run"], t, 0), "wspeed": RP.hold(tl["wspeed"], t, 1.6),
                   "talk": RP.hold(tl["talk"], t, 0), "armSw": RP.hold(tl.get("armsw", []), t, 1), "gaze": RP.hold(tl["gaze"], t, RP.RIG["face"]["gaze"]),
                   "gazeY": RP.hold(tl["gazeY"], t, RP.RIG["face"].get("gaze_y", 0.0))}
            e, m = RP.hold(tl["eyes"], t, "normal"), RP.hold(tl["mouth"], t, "none")
            exp["eyes"] = e if isinstance(e, (int, float)) else ec.get(e, 0)
            exp["mouth"] = m if isinstance(m, (int, float)) else mc.get(m, 0)
            if not exp["walk"] and not exp["run"]:
                exp.pop("wspeed")   # speed only matters while walking or running
            for k, v in exp.items():
                if k in rec and abs(float(rec[k][i]) - float(v)) > 1e-3:
                    mism.append(f"t={t:.3f} {k}: AE {rec[k][i]} vs preview {v}")
            pts = tl["pts"]
            if pts:
                for k in RP.POSE_KEYS:
                    seq = [(p[0], p[1][k], p[2], p[3]) for p in pts]
                    a, b, c = RP.interp(seq, t - 0.04), RP.interp(seq, t), RP.interp(seq, t + 0.04)
                    if abs(a - b) < 1e-3 and abs(c - b) < 1e-3 and k in rec and abs(float(rec[k][i]) - b) > 0.5:
                        mism.append(f"t={t:.3f} {k}: AE {rec[k][i]:.2f} vs preview {b:.2f}")
        print(f"{cid}: {n} samples, {len(mism)} mismatches")
        for line in mism[:12]:
            print("   " + line)
        bad += len(mism)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
