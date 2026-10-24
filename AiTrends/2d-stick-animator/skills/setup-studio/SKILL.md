---
name: setup-studio
description: Install, check or repair the 2D Stick Animator studio on the user's computer - copy the kit (After Effects engine and bridge, Python tools, rig data, 373 3D-emoji icons, the 54-piece costume library for free mode, SFX kit, caption font) into the video workspace, install the Python packages (numpy, Pillow, requests, skia-python, faster-whisper), install the caption font, enable After Effects scripting, start the bridge and run the self-test. Use when the user says "install the studio", "set up the plugin", "check my setup", "the bridge doesn't work", "update the kit", or before the first video on a computer.
---

# Set up the studio

The kit lives in this plugin at `<plugin root>/kit` (two folders above this skill's folder). Every project
works from a copy in the user's **workspace**: a folder on the computer that has After Effects (for example the
folder the user connected to this session). Layout after setup:
```
<workspace>/_kit/      engine (ae/), tools (py/), data/, assets/icons, assets/costumes, assets/sfx, fonts/, templates/, dev/
<workspace>/_ae_jobs/  job queue for the After Effects bridge
<workspace>/projects/<slug>/   one folder per video
```

## 1. Choose the workspace
Use the folder the user connected/named. If none is connected and the session is linked to a computer, ask for
one (device_request_folder_access). Without a linked computer: work in the cloud workspace and use the fallback
renderer (no After Effects).

## 2. Copy the kit into the workspace
- Same machine (local Claude Code): `cp -r <plugin root>/kit <workspace>/_kit` (overwrite to update; keep
  `_kit/assets/icons`, `_kit/assets/costumes` and `_kit/assets/sfx` if present).
- Cloud session linked to the user's computer: in the container `cd <plugin root> && tar czf
  /mnt/user-data/outputs/ra_kit_<n>.tgz kit` (a NEW file name for every transfer: a re-used staged name can deliver
  the old copy), `device_commit_files` it to `<workspace>/_tmp/ra_kit_<n>.tgz`, then in device_bash:
  `cd "$HOME/mnt/<folder>" && mkdir -p _kit _tmp/k<n> && tar xzf _tmp/ra_kit_<n>.tgz -C _tmp/k<n> && cp -r
  _tmp/k<n>/kit/. _kit/`. (Connected folders usually forbid deleting, so `tar` cannot overwrite files in place:
  unpack beside and copy over. Kit tools write temporary files outside the project for the same reason.)
- Check: `_kit/ae/ra_engine.jsx`, `_kit/py/install_kit.py`, `_kit/data/rig.json` exist.

## 3. Python packages, icons, SFX
In the workspace shell: `cd _kit/py && python3 install_kit.py --whisper` (pip installs what is missing, converts
the icon library and the costume library to PNG, renders the SFX kit, pre-downloads the Whisper model). `python3 install_kit.py --check`
is the doctor. A linked computer's Linux shell may be reset between sessions: run the check at the start of each
session and reinstall if needed. If skia-python is installed but cannot load (missing libEGL/libGL, no root),
install_kit.py fetches those libraries without root into `_kit/.libs`, and the kit preloads them. ffmpeg must exist (`apt-get install -y ffmpeg` / `winget install ffmpeg`).

## 4. After Effects side (once per computer)
Prefer the plugin's `ae-desktop` tools (local MCP server; ToolSearch "ae_find"): `ae_find` (is AE installed?),
with AE closed `ae_enable_scripting` and `install_font <workspace>\_kit\fonts\Anton-Regular.ttf` (skip the font if
the user has Burbank Big Condensed), then `ae_launch` and `ae_run_jsx <workspace>\_kit\ae\ra_bridge.jsx`.
Without those tools, do the same by computer use: double-click the font > Install; AE Preferences > Scripting &
Expressions > "Allow Scripts to Write Files and Access Network"; File > Scripts > Run Script File... > the bridge.
Check `python3 make_job.py status` -> ALIVE. Details and dialogs: after-effects-build `references/ae-guide.md`.
API keys: `python3 keys.py set <service> <key> --workspace` on a linked computer whose Linux shell may be reset
(stored in `<workspace>/.ra_secrets/keys.json`, outside projects); `python3 keys.py set ...` elsewhere.

## 5. Self-test
`python3 selftest.py` (builds `projects/_selftest` with procedural art, compiles, preview stills), then
`python3 make_job.py build projects/_selftest --wait` and `python3 make_job.py stills projects/_selftest --times
<printed times> --wait`. Compare `ae/stills` with `qc/stills` (stage and look). Report: AE version, font found,
errors/warnings, render speed if tested. Keys (ElevenLabs, Kie.ai, Pexels, Pixabay, OpenAI) are set later with
`python3 keys.py set <service> <key>` only when needed and only with the user's own key - never write keys into
project files or the plugin. Kie.ai is only needed for projects in kie asset mode (make-assets).

## Updating
A newer plugin version: copy the kit over again (step 2), restart the bridge (run `ra_bridge.jsx` again - the old
one stops itself), `install_kit.py --check`. Projects keep working; re-run `compile_spec.py` before rebuilding.
