"""Shared helpers for the 2D Stick Animator tools: paths, keys, JSON, logging, style data."""
import json
import os
import re
import sys

KIT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(KIT, "data")


def load_data(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


STYLE = load_data("style.json")


def read_json(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit(f"missing file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)
    return path


def project_dirs(root):
    """Standard project layout (created on demand)."""
    sub = ["script", "audio", "audio/sfx", "timing", "plan", "assets/bg", "assets/cast", "assets/props",
           "assets/icons", "assets/video", "assets/fx", "ae", "ae/stills", "exports", "qc"]
    for s in sub:
        os.makedirs(os.path.join(root, s), exist_ok=True)
    return root


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.strip().lower()).strip("-")
    return s or "video"


# ----------------------------------------------------------------------------- keys
KEY_NAMES = {
    "elevenlabs": "ELEVENLABS_API_KEY",
    "kie": "KIE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "fal": "FAL_KEY",
    "pexels": "PEXELS_API_KEY",
    "pixabay": "PIXABAY_API_KEY",
    "freesound": "FREESOUND_API_KEY",
}


# per-user folder on the user's computer (keys, settings, caches) - never inside the plugin or a project.
# The plugin was called Relegated Animator before 2.0: files in the old folder are still read and moved over.
USER_DIR = os.path.join(os.path.expanduser("~"), ".2d_stick_animator")
OLD_USER_DIRS = [os.path.join(os.path.expanduser("~"), ".relegated_animator")]


def user_file(name):
    return os.path.join(USER_DIR, name)


def _old_user_files(name):
    return [os.path.join(d, name) for d in OLD_USER_DIRS]


def _read_with_old(name):
    """the new file's content, else the old folder's (so nothing stored before the rename is lost)"""
    for f in [user_file(name)] + _old_user_files(name):
        if os.path.exists(f):
            try:
                with open(f, encoding="utf-8") as fh:
                    return json.load(fh)
            except (OSError, ValueError):
                continue
    return {}


def _key_files(project=None):
    files = [user_file("keys.json")] + _old_user_files("keys.json")
    here = os.path.abspath(project or os.getcwd())
    # walk up to find a workspace-level .ra_secrets/keys.json (kept out of exports and shares)
    for _ in range(5):
        files.append(os.path.join(here, ".ra_secrets", "keys.json"))
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    files.append(os.path.join(os.path.expanduser("~"), ".atlas_studio", "elevenlabs.json"))
    return files


def get_key(service, project=None, required=True):
    env = KEY_NAMES.get(service, service.upper() + "_API_KEY")
    if os.environ.get(env):
        return os.environ[env].strip()
    for f in _key_files(project):
        if os.path.exists(f):
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
                v = d.get(service) or d.get(env) or (d.get("api_key") if f.endswith("elevenlabs.json") and service == "elevenlabs" else None)
                if v:
                    return str(v).strip()
            except (OSError, ValueError):
                continue
    if required:
        sys.exit(f"No {service} key. Set {env} or run: python keys.py set {service} (stored in ~/.2d_stick_animator/keys.json)")
    return None


def set_key(service, value, where=None):
    path = where or user_file("keys.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = {} if where or os.path.exists(path) else _read_with_old("keys.json")   # first write moves the old keys over
    if os.path.exists(path):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except ValueError:
            d = {}
    d[service] = value.strip()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def strip_labels(text):
    """drop a TOPIC/TITLE line and a SCRIPT: label (and stats lines after the paragraph) so only narration remains"""
    lines = []
    for l in text.splitlines():
        if re.match(r"\s*(?:\d+[.)]\s*)?(TOPIC/)?TITLE\s*:", l, re.I):
            continue
        l = re.sub(r"^\s*SCRIPT\s*:\s*", "", l, flags=re.I)
        if re.match(r"\s*(words\s*:|-{3,}|={3,}|\((TRUE|LEGEND|FICTION))", l, re.I):
            break
        lines.append(l)
    return "\n".join(lines).strip()


def settings_path():
    """per-user settings (default voice etc.) - on the user's computer, never inside the plugin"""
    return user_file("settings.json")


def get_setting(name, default=None):
    return _read_with_old("settings.json").get(name, default)


def set_setting(name, value):
    path = settings_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = _read_with_old("settings.json")
    d[name] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path


def hms(t):
    m = int(t // 60)
    return f"{m}:{t - 60 * m:05.2f}"
