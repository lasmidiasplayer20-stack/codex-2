"""Check that the After Effects creature expressions and creatures.py agree (run mock_ae.js PROJECT --creatures first).

  node kit/dev/mock_ae.js PROJECT --creatures && python kit/dev/creature_parity.py PROJECT
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "py"))
import creatures as CR  # noqa: E402

P = sys.argv[1]
spec = json.load(open(os.path.join(P, "plan", "spec_compiled.json"), encoding="utf-8"))
ae = json.load(open(os.path.join(P, "parity_creatures.json"), encoding="utf-8"))
shots = {s.get("id"): s for s in spec["shots"]}
worst, n = 0.0, 0
for name, d in ae["layers"].items():
    _, sid, idx, copy = name.split(" ")[:4]
    sh = shots[sid]
    c = sh["creatures"][int(idx)]
    for k in range(len(d["pos"])):
        t = k * ae["step"]
        if not (float(c.get("t", sh["t"])) <= t < float(c.get("end", sh["end"]))):
            continue
        x, y, sx, sy, rot = CR.state(c, int(copy), t, sh["t"])
        ax, ay = d["pos"][k]
        asx, asy = d["scale"][k][0] / 100.0, d["scale"][k][1] / 100.0
        ar = d["rot"][k]
        err = max(abs(ax - x), abs(ay - y), 100 * abs(asx - sx), 100 * abs(asy - sy), abs(ar - rot))
        worst = max(worst, err)
        n += 1
        if err > 0.01:
            print(f"MISMATCH {name} t={t:.1f}: ae {ax:.2f},{ay:.2f},{asx:.4f},{asy:.4f},{ar:.2f}  py {x:.2f},{y:.2f},{sx:.4f},{sy:.4f},{rot:.2f}")
print(f"creature parity: {len(ae['layers'])} layers, {n} samples, max difference {worst:.6f}")
sys.exit(1 if worst > 0.01 else 0)
