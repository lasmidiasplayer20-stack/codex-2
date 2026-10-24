#!/usr/bin/env python3
"""ae-desktop: a minimal stdio MCP server that lets Claude drive Adobe After Effects on the user's computer.

Runs on the computer that has After Effects (the Claude desktop app starts plugin MCP servers locally).
Stdlib only. JSON-RPC 2.0 over newline-delimited stdio (Model Context Protocol).

Tools
  ae_find              installed After Effects versions, executables, prefs files, whether it is running
  ae_launch            start After Effects (optionally a given version)
  ae_run_jsx           run a .jsx script in the running After Effects (Windows: AfterFX.com -r; macOS: DoScriptFile)
  ae_enable_scripting  turn on "Allow Scripts to Write Files and Access Network" in the prefs file (AE must be closed)
  ae_kill_stale        end leftover AfterFX.com helper processes that can swallow scripts (Windows)
  install_font         install a .ttf/.otf for the current user (Windows per-user fonts / macOS ~/Library/Fonts)
  open_path            open a file or folder with the default app (e.g. the final video, the project folder)
  read_text            read a small text file (job results, build logs) - up to 200 KB
Safety: only .jsx/.jsxbin files can be run; fonts must be .ttf/.otf; prefs are backed up before editing.
"""
import glob
import json
import os
import platform
import shutil
import subprocess
import sys
import time

SYS = platform.system()


# ----------------------------------------------------------------------------- discovery
def _win_installs():
    out = []
    roots = [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramW6432", r"C:\Program Files")]
    seen = set()
    for r in roots:
        for d in glob.glob(os.path.join(r, "Adobe", "Adobe After Effects*")):
            if d in seen:
                continue
            seen.add(d)
            exe = os.path.join(d, "Support Files", "AfterFX.exe")
            com = os.path.join(d, "Support Files", "AfterFX.com")
            if os.path.exists(exe):
                out.append({"name": os.path.basename(d), "folder": d, "exe": exe, "afterfx_com": com if os.path.exists(com) else None,
                            "year": "".join(ch for ch in os.path.basename(d) if ch.isdigit())})
    out.sort(key=lambda x: x["year"], reverse=True)
    return out


def _mac_installs():
    out = []
    for d in glob.glob("/Applications/Adobe After Effects*"):
        apps = glob.glob(os.path.join(d, "Adobe After Effects*.app"))
        if apps:
            out.append({"name": os.path.basename(d), "folder": d, "app": apps[0],
                        "year": "".join(ch for ch in os.path.basename(d) if ch.isdigit())})
    out.sort(key=lambda x: x["year"], reverse=True)
    return out


def installs():
    if SYS == "Windows":
        return _win_installs()
    if SYS == "Darwin":
        return _mac_installs()
    return []


def running():
    try:
        if SYS == "Windows":
            r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq AfterFX.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=20)
            return "AfterFX.exe" in r.stdout
        if SYS == "Darwin":
            r = subprocess.run(["pgrep", "-f", "Adobe After Effects"], capture_output=True, text=True, timeout=20)
            return bool(r.stdout.strip())
    except Exception:
        return False
    return False


def prefs_files():
    pats = []
    if SYS == "Windows":
        base = os.path.join(os.environ.get("APPDATA", ""), "Adobe", "After Effects")
        pats = glob.glob(os.path.join(base, "*", "Adobe After Effects * Prefs.txt"))
    elif SYS == "Darwin":
        base = os.path.expanduser("~/Library/Preferences/Adobe/After Effects")
        pats = glob.glob(os.path.join(base, "*", "Adobe After Effects * Prefs.txt"))
    return sorted(pats)


def pick(version=None):
    ins = installs()
    if not ins:
        raise RuntimeError("Adobe After Effects is not installed in the standard location on this computer (%s)" % SYS)
    if version:
        for i in ins:
            if str(version) in i["name"]:
                return i
    return ins[0]


# ----------------------------------------------------------------------------- tools
def tool_find(args):
    return {"platform": SYS, "installs": installs(), "running": running(), "prefs_files": prefs_files(),
            "python": sys.executable}


def tool_launch(args):
    i = pick(args.get("version"))
    if running():
        return {"ok": True, "note": "After Effects is already running", "install": i["name"]}
    if SYS == "Windows":
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen([i["exe"]], creationflags=flags, close_fds=True)
    else:
        subprocess.Popen(["open", "-a", i["app"]])
    t0 = time.time()
    wait = float(args.get("wait_seconds", 25))
    while time.time() - t0 < wait:
        if running():
            break
        time.sleep(1)
    return {"ok": True, "install": i["name"], "running": running(),
            "note": "Give After Effects ~20-60 s to finish loading before running scripts; check with a screenshot."}


def tool_kill_stale(args):
    if SYS != "Windows":
        return {"ok": True, "note": "nothing to do on this platform"}
    r = subprocess.run(["taskkill", "/F", "/IM", "AfterFX.com"], capture_output=True, text=True)
    return {"ok": True, "output": (r.stdout + r.stderr).strip()[:500]}


def tool_run_jsx(args):
    path = os.path.abspath(args["path"])
    if not path.lower().endswith((".jsx", ".jsxbin")):
        raise ValueError("only .jsx/.jsxbin files can be run")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if not running():
        raise RuntimeError("After Effects is not running: call ae_launch first and wait until it has loaded")
    i = pick(args.get("version"))
    timeout = float(args.get("timeout_seconds", 20))
    if SYS == "Windows":
        if not i.get("afterfx_com"):
            raise RuntimeError("AfterFX.com not found next to AfterFX.exe")
        tool_kill_stale({})
        p = subprocess.Popen([i["afterfx_com"], "-r", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = p.communicate(timeout=timeout)
            return {"ok": True, "sent": path, "exit": p.returncode, "output": (out or b"").decode(errors="replace")[-800:]}
        except subprocess.TimeoutExpired:
            p.kill()
            return {"ok": True, "sent": path, "note": "AfterFX.com did not return within the timeout (normal for long scripts); "
                                                       "check the script's own result/log files"}
    app = os.path.basename(i["app"]).replace(".app", "")
    script = 'tell application "%s" to DoScriptFile "%s"' % (app, path.replace('"', '\\"'))
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=max(timeout, 30))
    return {"ok": r.returncode == 0, "sent": path, "output": (r.stdout + r.stderr)[-800:]}


def tool_enable_scripting(args):
    if running():
        raise RuntimeError("Quit After Effects first (prefs are rewritten when it quits), then call this again, or tick "
                           "Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network' by hand")
    files = prefs_files()
    if args.get("version"):
        files = [f for f in files if str(args["version"]) in f] or files
    if not files:
        raise RuntimeError("no After Effects prefs file found yet: start After Effects once, quit it, then retry")
    done = []
    for f in files:
        txt = open(f, encoding="utf-8", errors="replace").read()
        shutil.copy(f, f + ".ra_backup")
        key = '"Pref_SCRIPTING_FILE_NETWORK_SECURITY"'
        lines = txt.splitlines()
        out, in_main, set_ok = [], False, False
        for ln in lines:
            s = ln.strip()
            if s.startswith("[") and s.endswith("]"):
                if in_main and not set_ok:
                    out.append('\t%s = 01' % key)
                    set_ok = True
                in_main = (s == '["Main Pref Section v2"]')
            if in_main and s.startswith(key):
                out.append('\t%s = 01' % key)
                set_ok = True
                continue
            out.append(ln)
        if in_main and not set_ok:
            out.append('\t%s = 01' % key)
            set_ok = True
        if not set_ok:
            out.append('["Main Pref Section v2"]')
            out.append('\t%s = 01' % key)
        open(f, "w", encoding="utf-8").write("\n".join(out) + "\n")
        done.append(f)
    return {"ok": True, "updated": done, "note": "backups saved as *.ra_backup"}


def tool_install_font(args):
    src = os.path.abspath(args["path"])
    if not src.lower().endswith((".ttf", ".otf")) or not os.path.exists(src):
        raise ValueError("give an existing .ttf or .otf file")
    name = os.path.basename(src)
    if SYS == "Windows":
        import ctypes
        import winreg
        dst_dir = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, name)
        shutil.copy(src, dst)
        label = os.path.splitext(name)[0].replace("-", " ") + (" (TrueType)" if name.lower().endswith(".ttf") else " (OpenType)")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts", 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, label, 0, winreg.REG_SZ, dst)
        try:
            ctypes.windll.gdi32.AddFontResourceW(dst)
            ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0, 1000, None)
        except Exception:
            pass
        return {"ok": True, "installed": dst, "note": "restart After Effects so it sees the new font"}
    if SYS == "Darwin":
        dst = os.path.join(os.path.expanduser("~/Library/Fonts"), name)
        shutil.copy(src, dst)
        return {"ok": True, "installed": dst, "note": "restart After Effects so it sees the new font"}
    raise RuntimeError("font install is only supported on Windows and macOS")


def tool_open_path(args):
    p = os.path.abspath(args["path"])
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    if SYS == "Windows":
        os.startfile(p)  # noqa
    elif SYS == "Darwin":
        subprocess.Popen(["open", p])
    else:
        subprocess.Popen(["xdg-open", p])
    return {"ok": True, "opened": p}


def tool_read_text(args):
    p = os.path.abspath(args["path"])
    if os.path.getsize(p) > 200_000:
        with open(p, encoding="utf-8", errors="replace") as f:
            f.seek(max(0, os.path.getsize(p) - 200_000))
            return {"path": p, "tail": f.read()}
    return {"path": p, "text": open(p, encoding="utf-8", errors="replace").read()}


TOOLS = [
    {"name": "ae_find", "description": "List installed Adobe After Effects versions on this computer, whether it is running, and its prefs files.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "ae_launch", "description": "Start Adobe After Effects (newest version unless 'version' like '2025' is given). Returns once the process is running; loading takes 20-60 s more.",
     "inputSchema": {"type": "object", "properties": {"version": {"type": "string"}, "wait_seconds": {"type": "number"}}}},
    {"name": "ae_run_jsx", "description": "Run a .jsx ExtendScript file in the running After Effects (e.g. <workspace>/_kit/ae/ra_bridge.jsx to start the job bridge, or a job file in _ae_jobs). Windows uses AfterFX.com -r, macOS DoScriptFile.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "version": {"type": "string"}, "timeout_seconds": {"type": "number"}}, "required": ["path"]}},
    {"name": "ae_enable_scripting", "description": "Turn on 'Allow Scripts to Write Files and Access Network' in the After Effects prefs file. After Effects must be closed; a backup is kept.",
     "inputSchema": {"type": "object", "properties": {"version": {"type": "string"}}}},
    {"name": "ae_kill_stale", "description": "End leftover AfterFX.com helper processes (Windows) that can swallow new scripts.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "install_font", "description": "Install a .ttf/.otf font for the current user (e.g. <workspace>/_kit/fonts/Anton-Regular.ttf for the captions).",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "open_path", "description": "Open a file or folder on this computer with its default app (final video, project folder).",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "read_text", "description": "Read a text file on this computer (job results, build logs, heartbeat).",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
]
HANDLERS = {"ae_find": tool_find, "ae_launch": tool_launch, "ae_run_jsx": tool_run_jsx, "ae_enable_scripting": tool_enable_scripting,
            "ae_kill_stale": tool_kill_stale, "install_font": tool_install_font, "open_path": tool_open_path, "read_text": tool_read_text}


def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion", "2024-11-05")
        send({"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": ver, "capabilities": {"tools": {}},
                                                       "serverInfo": {"name": "ae-desktop", "version": "1.2.0"}}})
    elif method == "notifications/initialized":
        pass
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        p = msg.get("params") or {}
        h = HANDLERS.get(p.get("name"))
        if h is None:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "Unknown tool: %s" % p.get("name")}})
            return
        try:
            res = h(p.get("arguments") or {})
            send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}], "isError": False}})
        except Exception as e:
            send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": "Error: %s" % e}], "isError": True}})
    elif mid is not None:
        send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found: %s" % method}})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            handle(msg)
        except Exception as e:
            print("ae-desktop error: %s" % e, file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
