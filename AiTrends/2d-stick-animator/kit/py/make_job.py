"""Queue After Effects jobs for the bridge (ra_bridge.jsx) and wait for their results.

  python make_job.py status                                   # is the bridge running? (heartbeat age, AE version)
  python make_job.py build  projects/<slug> [--wait]          # build the AE project from plan/spec_compiled.json
  python make_job.py stills projects/<slug> --times 0.5,3.2,7 [--wait]   # PNG stills from MAIN -> <project>/ae/stills
  python make_job.py stills projects/<slug> --every 2 [--wait]
  python make_job.py render projects/<slug> [--wait --timeout 3600]       # render MAIN -> <project>/exports/ae_render.*
  python make_job.py fonts  --names Anton-Regular,Impact [--wait]
  python make_job.py raw path/to/script.jsx [--wait]          # run any ExtendScript through the bridge

PROJECT paths are relative to the workspace root (the folder that holds _kit/). The job files land in
<workspace>/_ae_jobs/. If the bridge is not running, start it once in After Effects (File > Scripts > Run Script
File... > <workspace>/_kit/ae/ra_bridge.jsx) or run the printed job file the same way. On a Windows shell with
After Effects open you can also run:  "<AE>\\Support Files\\AfterFX.com" -r "<job file>"
"""
import argparse
import json
import os
import shutil
import sys
import time

from ra_common import KIT

ROOT = os.path.dirname(KIT)
JOBS = os.path.join(ROOT, "_ae_jobs")


def heartbeat():
    p = os.path.join(JOBS, "bridge_heartbeat.json")
    if not os.path.exists(p):
        return None, None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except ValueError:
        return None, None
    if "time" not in d:
        return d, None
    age = time.time() - d["time"] / 1000.0
    return d, age


def write_job(kind, payload):
    os.makedirs(JOBS, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    name = f"{stamp}_{kind}"
    path = os.path.join(JOBS, name + ".jsx")
    js = json.dumps(payload)
    body = ("// 2D Stick Animator job (written by make_job.py)\n"
            "if (typeof RA_ROOT === \"undefined\" || !RA_ROOT) { $.global.RA_ROOT = (new File($.fileName)).parent.parent.fsName.replace(/\\\\/g, \"/\"); }\n"
            "if (typeof RA_KIT === \"undefined\" || !RA_KIT) { $.global.RA_KIT = RA_ROOT + \"/_kit\"; }\n"
            "$.evalFile(new File(RA_KIT + \"/ae/ra_engine.jsx\"));\n"
            f"$.global.RA_LAST = RA.run({js});\n")
    open(path, "w", encoding="ascii", errors="backslashreplace").write(body)
    return name, path


def wait(name, timeout, project=None, log_name=None):
    res = os.path.join(JOBS, name + ".result.json")
    t0 = time.time()
    shown = 0
    while time.time() - t0 < timeout:
        if os.path.exists(res):
            time.sleep(0.3)
            try:
                d = json.load(open(res, encoding="utf-8"))
            except ValueError:
                time.sleep(1)
                continue
            print(f"job {name}: {'OK' if d.get('ok') else 'FAILED'} in {(d.get('finished', 0) - d.get('started', 0)) / 1000:.1f}s")
            if not d.get("ok"):
                print("  error:", d.get("error"), "line", d.get("line"))
            if project and log_name:
                lp = os.path.join(ROOT, project, "ae", log_name)
                if os.path.exists(lp):
                    lines = open(lp, encoding="utf-8", errors="replace").read().splitlines()
                    bad = [l for l in lines if "ERROR" in l or "WARNING" in l]
                    print(f"  log {lp}: {len(lines)} lines, {len([b for b in bad if 'ERROR' in b])} errors, {len([b for b in bad if 'WARNING' in b])} warnings")
                    for l in bad[:40]:
                        print("   ", l)
                    if lines:
                        print("   ", lines[-1])
            return d
        hb, age = heartbeat()
        if time.time() - t0 > 8 and (hb is None or age is None or age > 15) and not (hb and str(hb.get("state", "")).startswith("running")):
            if time.time() - t0 > 20 and shown == 0:
                print("  the bridge does not seem to be running (no fresh heartbeat). Start it in After Effects:\n"
                      f"  File > Scripts > Run Script File... > {os.path.join(ROOT, '_kit', 'ae', 'ra_bridge.jsx')}\n"
                      "  (a modal error dialog in After Effects also blocks it: take a screenshot and dismiss it)")
                shown = 1
        time.sleep(1.0)
    print(f"timeout after {timeout}s waiting for {name}")
    return None


def still_times(project, times, every):
    if times:
        return times
    dur = 0
    for sp in ("plan/spec_compiled.json", "plan/spec.json"):
        f = os.path.join(ROOT, project, sp)
        if os.path.exists(f):
            dur = float(json.load(open(f, encoding="utf-8")).get("meta", {}).get("duration", 0))
            break
    out, t = [], 0.5
    while t < dur:
        out.append(t)
        t += every or 2.0
    return out


def wait_stills(project, times, timeout=240):
    """saveFrameToPng renders asynchronously in After Effects 2024+: the job returns before the PNGs exist.
    Wait until every requested still is on disk with a stable size."""
    d = os.path.join(ROOT, project, "ae", "stills")
    names = ["still_" + ("00000" + str(int(round(t * 1000))))[-6:] + ".png" for t in times]
    t0, last = time.time(), {}
    while time.time() - t0 < timeout:
        sizes = {n: (os.path.getsize(os.path.join(d, n)) if os.path.exists(os.path.join(d, n)) else -1) for n in names}
        if all(v > 0 for v in sizes.values()) and sizes == last:
            print(f"  {len(names)} stills ready in {d}")
            return True
        last = sizes
        time.sleep(1.0)
    missing = [n for n in names if not os.path.exists(os.path.join(d, n))]
    print(f"  stills not complete after {timeout}s, missing: {missing}")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["status", "build", "stills", "render", "fonts", "raw"])
    ap.add_argument("project", nargs="?")
    ap.add_argument("--times", default="")
    ap.add_argument("--every", type=float, default=0)
    ap.add_argument("--names", default="")
    ap.add_argument("--spec")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    if a.kind == "status":
        hb, age = heartbeat()
        if hb is None:
            print("no bridge heartbeat yet: start ra_bridge.jsx in After Effects")
        elif age is None:
            print("bridge started but has not polled yet")
        else:
            print(f"bridge {'ALIVE' if age < 15 else 'STALE'} ({age:.0f}s ago) state={hb.get('state')} AE={hb.get('ae')} "
                  f"runs={hb.get('runs')} project={hb.get('project')}")
        pend = [f for f in os.listdir(JOBS) if f.endswith((".jsx", ".running"))] if os.path.isdir(JOBS) else []
        print("pending jobs:", pend or "none")
        return
    payload = {"kind": a.kind}
    log = None
    if a.kind in ("build", "stills", "render"):
        if not a.project:
            sys.exit("give the project path relative to the workspace, e.g. projects/money-rain")
        pr = a.project
        if os.path.isabs(pr) or not os.path.isdir(os.path.join(ROOT, pr)):
            # accept an absolute path or one relative to the current folder: the bridge needs it relative to the workspace
            ab = os.path.abspath(pr)
            if os.path.isdir(ab) and os.path.commonpath([ab, os.path.abspath(ROOT)]) == os.path.abspath(ROOT):
                pr = os.path.relpath(ab, ROOT)
        if not os.path.isfile(os.path.join(ROOT, pr, "plan", "spec_compiled.json")) and a.kind == "build":
            sys.exit(f"no plan/spec_compiled.json in {os.path.join(ROOT, pr)} - run compile_spec.py first "
                     f"(project paths are relative to the workspace, e.g. projects/money-rain)")
        payload["project"] = pr.replace("\\", "/").strip("/")
        log = {"build": "build_log.txt", "stills": "stills_log.txt", "render": "render_log.txt"}[a.kind]
    if a.kind == "build" and a.spec:
        payload["spec"] = a.spec
    if a.kind == "stills":
        if a.times:
            payload["times"] = [float(x) for x in a.times.split(",") if x]
        else:
            payload["every"] = a.every or 2.0
    if a.kind == "fonts":
        payload["names"] = [n for n in a.names.split(",") if n]
        payload["project"] = "_ae_jobs"
        log = None
    if a.kind == "raw":
        src = a.project
        os.makedirs(JOBS, exist_ok=True)
        name = time.strftime("%Y%m%d_%H%M%S") + "_raw"
        shutil.copy(src, os.path.join(JOBS, name + ".jsx"))
        print("queued", os.path.join(JOBS, name + ".jsx"))
        if a.wait:
            wait(name, a.timeout)
        return
    if a.kind == "fonts" and not payload["names"]:
        from ra_common import STYLE
        payload["names"] = list(STYLE.get("captions", {}).get("fonts", []))
    name, path = write_job(a.kind, payload)
    print("queued", path)
    if a.wait:
        d = wait(name, a.timeout, payload.get("project"), log)
        if d and d.get("ok") and a.kind == "stills":
            wait_stills(payload["project"], still_times(payload["project"], payload.get("times"), payload.get("every")), min(a.timeout, 600))
        if d and a.kind == "fonts":
            lp = os.path.join(JOBS, "ae", "fonts_log.txt")
            if os.path.exists(lp):
                for line in open(lp, encoding="utf-8", errors="replace").read().splitlines():
                    if " font " in line:
                        print("  " + line.split("] ", 1)[-1])


if __name__ == "__main__":
    main()
