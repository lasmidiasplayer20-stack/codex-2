"""Import skia-python, supplying missing system GL libraries when the shell has no root.

skia-python links libEGL.so.1 / libGL.so.1. Minimal Linux shells (for example the Linux VM of a linked
computer) often lack them and cannot apt-get install. install_kit.py then downloads the Ubuntu packages
without root (apt-get download + dpkg-deb -x) into _kit/.libs; this module preloads them so `import skia` works.

Usage in the kit:  from ra_skia import skia
"""
import ctypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LIBDIRS = [os.path.normpath(os.path.join(HERE, "..", ".libs")),
           os.path.join(os.path.expanduser("~"), ".cache", "2d_stick_animator", "libs"),
           os.path.join(os.path.expanduser("~"), ".cache", "relegated_animator", "libs")]   # before the rename
GL_LIBS = ("libGLdispatch.so.0", "libGLX.so.0", "libEGL.so.1", "libGL.so.1")


def preload_gl():
    loaded = []
    for d in LIBDIRS:
        for name in GL_LIBS:
            p = os.path.join(d, name)
            if os.path.exists(p) and name not in loaded:
                try:
                    ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
                    loaded.append(name)
                except OSError:
                    pass
    return loaded


try:
    import skia  # noqa: F401
except ImportError as _e:
    if "libEGL" not in str(_e) and "libGL" not in str(_e):
        raise
    if not preload_gl():
        raise ImportError(f"{_e} - run  python install_kit.py  (it fetches the GL libraries without root)") from _e
    import skia  # noqa: F401,E402
