---
name: after-effects-build
description: Build, check, polish and render a glow stick-figure Short inside Adobe After Effects on the user's computer - start After Effects and the script bridge with computer use, build the full editable project from plan/spec_compiled.json (rigged characters, shots, camera, icons, FX, transitions, captions, audio), export stills to check it, fix issues, render MAIN, and hand-polish in the After Effects UI when needed. Use when the user says "build it in After Effects", "open it in AE", "render the video", "use computer use", "fix shot 7 in AE", or when the make-story-short pipeline reaches the build stage. Falls back to the preview renderer when After Effects is not available.
---

# Build in After Effects

Inputs: an approved `plan/spec_compiled.json` (compile_spec.py) and the assets. Output: `ae/<slug>.aep`,
`ae/stills/*.png`, `exports/ae_render.mp4|.mov`. Engine: `_kit/ae/ra_engine.jsx`; bridge: `_kit/ae/ra_bridge.jsx`;
job tool: `_kit/py/make_job.py`. Full procedures, the layer map and troubleshooting: `references/ae-guide.md`.

## 0. Before touching the computer
- If a `computer-use` skill is listed (anthropic-skills:computer-use), read its SKILL.md first.
- Python tools run where the workspace is (device_bash on a linked computer: the workspace is
  `$HOME/mnt/<folder>`). After Effects sees the same folder under its Windows/macOS path.
- Never close or overwrite the user's own open After Effects work without asking: the engine saves an open
  project (or backs up an untitled one to `ae/_unsaved_project_backup.aep`) before it builds.

## 1. Start After Effects and the bridge (once per AE session)
`python make_job.py status` - if the bridge is ALIVE, skip to step 2. Otherwise use the first route that works:

**A. The plugin's `ae-desktop` tools** (this plugin's local MCP server; tool names end in `ae_find`, `ae_launch`,
`ae_run_jsx`, `ae_enable_scripting`, `install_font`, `open_path`, `read_text` - on a linked computer they may be
prefixed like `mcp__remote-devices__plugin_2d-stick-animator_ae-desktop__...`; find them with ToolSearch "ae_find"):
1. `ae_find` - versions installed, running or not, prefs files.
2. First time on this computer, with After Effects closed: `ae_enable_scripting`, and
   `install_font` with `<workspace Windows path>\_kit\fonts\Anton-Regular.ttf`.
3. `ae_launch`, wait ~30-60 s (screenshot with computer use to see the start screen / dismiss update dialogs).
4. `ae_run_jsx` with `<workspace Windows path>\_kit\ae\ra_bridge.jsx`.
5. `python make_job.py status` -> ALIVE.

**B. Computer use only** (verified on After Effects 2025, Windows): resolve and request access to the installed
After Effects app (its name includes the year, e.g. "Adobe After Effects 2025"), open it and close the Home screen
(the x at its top right) so the menus answer. First time: Edit > Preferences > Scripting & Expressions > tick "Allow
Scripts to Write Files and Access Network" > OK (often already on; macOS: After Effects > Settings). Then File >
Scripts > Run Script File... > click the File name box, type the full Windows path of
`<workspace>\_kit\ae\ra_bridge.jsx` > Enter. Nothing visible happens; `make_job.py status` must say ALIVE within a
few seconds. `python make_job.py fonts --wait` then lists which caption fonts After Effects has.

**C. Native shell on the AE computer** (Claude Code on Windows): `"<AE folder>\Support Files\AfterFX.com" -r
"<job.jsx>"` per job, After Effects already open (kill stale AfterFX.com processes first).

If `status` stays dead: screenshot After Effects (a modal dialog blocks scripts), dismiss it, retry once.

## 2. Self-test (first use on a computer, or after engine edits)
`python selftest.py` then `python make_job.py build projects/_selftest --wait` and
`python make_job.py stills projects/_selftest --times <the times selftest printed> --wait`; stage and look at
`projects/_selftest/ae/stills/*.png` next to `qc/stills/preview_*.png` (side by side in one image). They should
match in framing, poses, faces, outline, icons, captions, states and grades; After Effects looks slightly richer
(glow) and money/ember particles land differently. After engine edits, first run the dry-run checks at
the end of `references/ae-guide.md`.

## 3. Build the video
1. `python compile_spec.py P` (always, after any plan edit).
2. `python make_job.py build projects/<slug> --wait --timeout 1800`. Read the log summary it prints
   (`ae/build_log.txt`): resolve every ERROR; WARNINGs about fonts or effect parameters need a look.
3. Stills: `python make_job.py stills projects/<slug> --every 1.5 --wait` (or `--times` at every key moment),
   stage a selection and LOOK at them against the animatic and `house-style/references/look/*.jpg`: characters on
   the floor, held props gripped by the handle with the working end out and touching what they act on, heads
   floating just above the bodies, faces readable and looking the right way, carried or dragged
   characters moving with the hands that hold them, costume pieces seated on head and body, the camera on the
   faces (not on legs or empty floor), icons above heads and clear of captions, captions yellow at
   ~76%, grades and B&W where planned, no empty frames. A screenshot of After Effects (computer use) helps for
   things stills cannot show (timeline, layer stacking, errors).
4. Fix in the spec and rebuild (fast and repeatable). Hand edits in After Effects are for final polish only and
   are lost on rebuild - note them in PROJECT_STATE.md.

## 4. Render
`python make_job.py render projects/<slug> --wait --timeout 3600` renders MAIN with the best H.264 template
(AE 2023+) or a lossless/ProRes master -> `exports/ae_render.*`. After Effects is busy (UI frozen) while it
renders; the job result appears when done. Then go to the sound-and-finish skill (mix + mux + QC).

## When After Effects is not available
Say so plainly, then render the picture with the fallback renderer: `python ra_preview.py P --full`
(1080x1920, 30 fps, same spec, ~1-2.5 s per frame) -> `exports/preview_full.mp4`, and continue with
sound-and-finish using `--video exports/preview_full.mp4`. Hand over the project folder (spec, assets, kit) so it
can be built in After Effects later with step 3.
