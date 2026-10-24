"""Set up / check the studio on this computer (run from the workspace copy of the kit: <workspace>/_kit/py).

  python install_kit.py            # install missing Python packages, build icon PNGs + SFX kit, create folders, report
  python install_kit.py --check    # report only (doctor)
  python install_kit.py --whisper  # also install faster-whisper (word timestamps) and pre-download the model

Creates: <workspace>/projects/, <workspace>/_ae_jobs/, _kit/assets/icons/*.png (373 Fluent 3D emoji, MIT),
         _kit/assets/sfx/*.wav (procedural SFX kit), _kit/fonts (Anton caption font, OFL - install it in Windows
         for After Effects: right-click Anton-Regular.ttf > Install for all users).
"""
import argparse
import importlib
import os
import shutil
import subprocess
import sys

KIT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KIT, "py"))
ROOT = os.path.dirname(KIT)
PKGS = [("numpy", "numpy"), ("PIL", "Pillow"), ("requests", "requests"), ("skia", "skia-python")]


def have(mod):
    if mod == "skia":
        return skia_status() == "ok"
    try:
        importlib.import_module(mod)
        return True
    except Exception:
        return False


def skia_status():
    """'ok', 'gl' (installed but the system GL libraries are missing) or 'missing'."""
    r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import ra_skia" % os.path.join(KIT, "py")],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return "ok"
    return "gl" if ("libEGL" in r.stderr or "libGL" in r.stderr) else "missing"


def fetch_gl_libs():
    """Linux without root: apt-get download the GL packages skia-python links, unpack them into _kit/.libs
    (and ~/.cache/2d_stick_animator/libs) where ra_skia.py preloads them."""
    import glob
    import tempfile
    if not sys.platform.startswith("linux") or not shutil.which("apt-get") or not shutil.which("dpkg-deb"):
        return "skia needs libEGL/libGL: install them with the system package manager (libegl1 libgl1)"
    if subprocess.run(["apt-get", "install", "-y", "-q", "libegl1", "libgl1"], capture_output=True).returncode == 0:
        return "installed libegl1 libgl1"
    tmp = tempfile.mkdtemp(prefix="ra_gl_")
    r = subprocess.run(["apt-get", "download", "libegl1", "libglvnd0", "libgl1", "libglx0"], cwd=tmp, capture_output=True, text=True)
    debs = glob.glob(os.path.join(tmp, "*.deb"))
    if not debs:
        return "could not download the GL packages: " + r.stderr[-300:]
    x = os.path.join(tmp, "x")
    for d in debs:
        subprocess.run(["dpkg-deb", "-x", d, x], capture_output=True)
    # same lists as ra_skia.py (importing it here would raise while the libraries are missing)
    GL_LIBS = ("libGLdispatch.so.0", "libGLX.so.0", "libEGL.so.1", "libGL.so.1")
    LIBDIRS = [os.path.join(KIT, ".libs"), os.path.join(os.path.expanduser("~"), ".cache", "2d_stick_animator", "libs")]
    done = []
    for dst in LIBDIRS:
        try:
            os.makedirs(dst, exist_ok=True)
            for name in GL_LIBS:
                hits = glob.glob(os.path.join(x, "usr", "lib", "*", name))
                if hits:
                    shutil.copyfile(os.path.realpath(hits[0]), os.path.join(dst, name))
            done.append(dst)
        except OSError:
            pass
    return "GL libraries unpacked to " + ", ".join(done)


def pip_install(pkgs):
    base = [sys.executable, "-m", "pip", "install", "-q"]
    for extra in ([], ["--user"], ["--break-system-packages"], ["--user", "--break-system-packages"]):
        r = subprocess.run(base + extra + pkgs, capture_output=True, text=True)
        if r.returncode == 0:
            return True
    print(r.stderr[-800:])
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--whisper", action="store_true")
    a = ap.parse_args()
    report = []
    missing = [pip for mod, pip in PKGS if not have(mod)]
    if args_whisper := a.whisper:
        if not have("faster_whisper"):
            missing.append("faster-whisper")
    if missing and not a.check:
        print("installing:", " ".join(missing))
        pip_install(missing)
    if not a.check and skia_status() == "gl":
        report.append(f"{'GL libraries':15s} {fetch_gl_libs()}")
    for mod, pip in PKGS + [("faster_whisper", "faster-whisper")]:
        st = "ok" if have(mod) else ("installed, system GL libraries missing (run without --check)" if mod == "skia" and skia_status() == "gl" else "MISSING")
        report.append(f"{pip:15s} {st}")
    ff = shutil.which("ffmpeg")
    report.append(f"{'ffmpeg':15s} {'ok ' + ff if ff else 'MISSING (apt-get install ffmpeg / winget install ffmpeg)'}")
    if not a.check:
        os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
        os.makedirs(os.path.join(ROOT, "_ae_jobs", "done"), exist_ok=True)
        # icons
        src = os.path.join(KIT, "assets", "icons_webp")
        dst = os.path.join(KIT, "assets", "icons")
        if have("PIL") and os.path.isdir(src):
            from PIL import Image
            os.makedirs(dst, exist_ok=True)
            n = 0
            for f in os.listdir(src):
                if f.endswith(".webp"):
                    out = os.path.join(dst, f[:-5] + ".png")
                    if not os.path.exists(out):
                        Image.open(os.path.join(src, f)).convert("RGBA").save(out)
                        n += 1
            shutil.copy(os.path.join(src, "LICENSE.txt"), os.path.join(dst, "LICENSE.txt"))
            report.append(f"{'icons':15s} {len([x for x in os.listdir(dst) if x.endswith('.png')])} PNG ({n} new) in {dst}")
        # costume library (free mode): WebP -> PNG for After Effects, plus its index
        csrc = os.path.join(KIT, "assets", "costumes_webp")
        cdst = os.path.join(KIT, "assets", "costumes")
        if have("PIL") and os.path.isdir(csrc):
            from PIL import Image
            os.makedirs(cdst, exist_ok=True)
            n = 0
            for f in os.listdir(csrc):
                if f.endswith(".webp"):
                    out = os.path.join(cdst, f[:-5] + ".png")
                    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(os.path.join(csrc, f)):
                        Image.open(os.path.join(csrc, f)).convert("RGBA").save(out)
                        n += 1
            if os.path.exists(os.path.join(csrc, "index.json")):
                shutil.copyfile(os.path.join(csrc, "index.json"), os.path.join(cdst, "index.json"))
            report.append(f"{'costumes':15s} {len([x for x in os.listdir(cdst) if x.endswith('.png')])} PNG ({n} new) in {cdst}")
        # sfx kit
        if have("numpy") and ff:
            sfx = os.path.join(KIT, "assets", "sfx")
            if not os.path.isdir(sfx) or len(os.listdir(sfx)) < 10:
                subprocess.run([sys.executable, os.path.join(KIT, "py", "sfx_kit.py"), "-o", sfx], capture_output=True)
            report.append(f"{'sfx kit':15s} {len(os.listdir(sfx)) if os.path.isdir(sfx) else 0} files in {sfx}")
        if a.whisper and have("faster_whisper"):
            try:
                from faster_whisper import WhisperModel
                WhisperModel("small.en", device="cpu", compute_type="int8")
                report.append(f"{'whisper model':15s} small.en ready")
            except Exception as e:
                report.append(f"{'whisper model':15s} download failed: {e}")
    report.append(f"{'workspace':15s} {ROOT}")
    report.append(f"{'AE bridge':15s} run once per AE session: File > Scripts > Run Script File... > {os.path.join(KIT, 'ae', 'ra_bridge.jsx')}")
    report.append(f"{'caption font':15s} install {os.path.join(KIT, 'fonts', 'Anton-Regular.ttf')} in Windows (or have Burbank Big Condensed / Impact)")
    print("\n".join(report))


if __name__ == "__main__":
    main()
