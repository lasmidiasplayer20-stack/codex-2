# After Effects guide: computer use, bridge, project map, troubleshooting

## Requirements
- After Effects 2022 or newer (2023+ recommended: native H.264 render templates; JavaScript expression engine).
  The engine sets the project expression engine to JavaScript.
- Preferences > Scripting & Expressions > **Allow Scripts to Write Files and Access Network** = on.
- Caption font installed for the OS: Burbank Big Condensed Black if the user owns it, else **Anton** (bundled in
  `_kit/fonts/Anton-Regular.ttf`: right-click > Install for all users, then restart After Effects), else Impact.
- Built-in effects only (Tint, Brightness & Contrast, Gaussian Blur, Simple Choker, Fill, Bevel Alpha, Glow,
  Drop Shadow, Mosaic, Block Dissolve, Directional Blur, Radial Blur, Noise, Fractal Noise, CC Rainfall). No
  third-party plugins needed.

## Computer use - how to drive After Effects
- Load the computer-use skill first if listed. Request access to "Adobe After Effects <year>"; use the app's
  window, not the desktop. Take a screenshot before and after every important click.
- Open menus by clicking the menu name, then the item (keyboard shortcuts vary by layout). Useful paths:
  File > Scripts > Run Script File... | Edit > Preferences > Scripting & Expressions... (Windows) |
  Composition > Add to Render Queue | Window > Info.
- File dialogs: click into the "File name" box, type the full path (Windows: `C:\...\_kit\ae\ra_bridge.jsx`,
  quotes not needed), press Enter.
- A **modal dialog** (script error, missing font, "file not found", update prompts, crash recovery) blocks the
  bridge and every later job: read it (screenshot, zoom), note the message, click OK/Close, then retry. If a
  build left a half-finished project, just rebuild.
- Do not click inside the timeline or comp panels while a job runs; After Effects is single-threaded and frozen
  during builds and renders. Wait for the job result instead (`make_job.py ... --wait`).
- To show the user the result in After Effects: double-click MAIN in the Project panel (00_MAIN), press Space
  to play (RAM preview), screenshot.

## The bridge
- `ra_bridge.jsx` registers a repeating task (every 1.2 s) that runs `<workspace>/_ae_jobs/*.jsx` one at a time,
  writes `<job>.result.json` (ok/error/line), moves the job to `_ae_jobs/done/` and refreshes
  `_ae_jobs/bridge_heartbeat.json` (time, state, AE version, open project). Re-running it replaces the old task.
- It survives until After Effects quits. Run it again after every restart of After Effects.
- `make_job.py status` reads the heartbeat (ALIVE < 15 s). `make_job.py raw file.jsx` runs any ExtendScript.
- Without the bridge: File > Scripts > Run Script File... on the job file itself works too (one run per job).

## What the build creates (for hand edits)
- A shot with `bg.world` has a background layer (and BG_TINT) sized to the whole location; CAM pans across it in
  world coordinates. Frame-wide FX/state layers stay in screen space.
- Folders: 00_MAIN, 01_SHOTS, 02_CHARACTERS, 03_FOOTAGE, 04_AUDIO, 05_SOLIDS.
- **MAIN** (1080x1920): CAPTIONS (one text layer, Source Text keyed per word; scale pop by expression; Extrude
  drop shadow + Halo glow effects), END_FADE, LOOK_GRAIN, LOOK_VIGNETTE, TR_* transition layers (flash, leak,
  red wipe, B&W fade, zoom blur), shot layers S01..Sn (earlier shots on top), VO, MUSIC, SFX_n.
- **Shot comps S01..** (full video length, trimmed in MAIN): CAM null (effects: zoom, focus, roll, shake - key
  these to re-frame; position/scale are expressions), BG (+ Desat/Grade/Depth effects, BG_TINT), PROPn_*,
  A<i>_SHADOW / A<i>_GLOW / A<i>_OUTLINE / A<i>_<cast> (three copies of the character comp: glow, ink outline via
  Simple Choker + Fill, art with STATE_* tints - no bevel/emboss), ICONn_* (host null + bubble/badge/image/text),
  FXn_*, STATE_n_* adjustment layers.
- **Character comps CHAR_<id>** (1600x1400, rig origin at 800,1250): CTRL null with sliders lean, head, hipX,
  hipY, aFu, aFl, aNu, aNl, lFu, lFl, lNu, lNl, turn (pose; turn 0 side - 1 front), walk, run, wspeed, idle,
  armSw (walking arm swing 0/1), phase, eyes, mouth, talk, gaze, gazeY, blinkOn, flush + colour control flushCol (skin colour) - every pose/face
  key of the whole video lives on these controls; limbs/torso/head are expressions. Re-pose by keying the sliders
  (angles in degrees: 0 = down, 90 = forward, 180 = up; lower values are bends).
  Faces: eyes 0 normal, 1 determined, 2 angry, 3 sad, 4 wide, 5 happy, 6 closed, 7 dead, 8 sleepy, 9 worried,
  10 calm, 11 joy, 12 suspicious; mouth 0 none, 1 o, 2 open, 3 scream, 4 smile, 5 frown, 6 flat, 7 grin, 8 smirk,
  9 teeth (hold keys).
- Layer order inside a character comp (back to front): back accessories, far arm/leg, TORSO, near leg, torso
  costume pieces, near arm, HEAD (SKULL, FLUSH, vector head parts), head costume pieces, FACE (EYES, MOUTH - on
  top of beards), OVER_FACE (glasses). Sleeves/pants/shoes are trimmed stroke groups on the limb layers. Topple
  and tilt keys sit on the actor's root null in the shot comp.
- Soft shading: each body part is a base layer in the darker edge colour plus a *_CORE layer (body colour, Gaussian
  Blur) above it; clothing segments sit on *_CLOTH layers; HEAD_TOP carries the face colour and vector head parts.
- Re-colour a character: CHAR_<id> > TORSO/ARM_*/LEG_*/HEAD fills and strokes (base = edge colour, *_CORE = body) (or change `cast.color` and rebuild).

## v2.3 elements (built from the compiled spec, nothing extra to do)
- Vehicles: a seat layer (PROP, behind every character) and a door layer (PROP, in front) drifting together, with
  the riders' CHAR comps between them; adjust a rider by its CTRL sliders like any character.
- Animal gait cycles: one PROP layer per frame, back to back (`exact` props start exactly on their time, no
  early in-point), each drifting along the path - select them all to retime or nudge the animal.
- Armholes: in each CHAR comp every torso garment `ACC_<i>` has a copy `ACC_<i>_CAP` above the arms, alpha-matted by
  `ACC_<i>_ARMHOLES` (a hidden shape layer with one disc per arm on its shoulder point, shown only while that arm is
  in front of the body). Resize the discs with `look.armhole_cap` in rig.json and rebuild.

## Rendering
- `make_job.py render` picks "H.264 - Match Render Settings - 40/15 Mbps" when present (AE 2023+), else ProRes/
  lossless. Output `exports/ae_render.mp4|.mov|.avi`; then `finish.py` muxes the final mix (the AE audio is not used).
- Speed: roughly 0.3-4 s per frame for a busy 1080x1920 comp; a 55 s Short = 1650 frames. Quitting other heavy apps
  helps. Rendering blocks the bridge until finished. (Measured on AE 2025 with the 40 Mbps H.264 template: the 7.6 s
  self-test in 35 s; an 11.9 s three-character test with costumes, glow and B&W in 2.6-3.4 min.)
- The bridge keeps polling after a render (it re-arms itself with one-shot tasks and a watchdog: a render-queue
  render cancels AE's repeating tasks). If `status` still says the heartbeat is stale a minute after a render,
  run ra_bridge.jsx again.

## Troubleshooting
| symptom | fix |
|---|---|
| `make_job.py status`: no heartbeat | bridge not started (or AE restarted): run ra_bridge.jsx again |
| heartbeat stale while a job is "running" | a modal dialog is open in AE: screenshot, dismiss, check `<job>.result.json` |
| alert "not allowed to write files" | turn on the Scripting & Expressions preference, rerun the bridge |
| build log `font ... could not confirm` | install Anton (or Burbank), restart AE, rebuild; captions otherwise fall back |
| `effect param N on X` warnings | localized or changed effect; set that parameter by hand once, note it, or adjust the index in ra_engine.jsx |
| expression error banners in the comp | open the layer with the red warning; the engine needs the JavaScript expression engine (File > Project Settings > Expressions) |
| characters invisible | the CHAR comp must last the whole video (it does); check `A<i>_<cast>` is inside the shot's in/out |
| outline too thick/thin | `rig.json > look.outline_px` (rig units: px at character height 1000, scales with the figure) and rebuild; or edit Simple Choker on A<i>_OUTLINE |
| costume piece misplaced | pieces from costume.py/assets.py carry measured `w/dx/dy`; if one is off, the generation was bad: `costume.py fit <piece>_raw.png --piece head -o ...` or regenerate (`assets.py get P --only id --force`); hand-tune `w/dx/dy/rot` only for pieces from elsewhere, check with cast_sheet.py, rebuild |
| caption font wrong | `caption_style.fonts` in the spec, or install the font |
| render template missing | AE < 2023: renders lossless .avi/.mov; finish.py encodes H.264 |
| `Object is invalid` after edits to the engine | AE invalidates property references when siblings are added: re-resolve by name (see RH handles) |
| `SyntaxError` in the engine | ExtendScript is ES3 + ASCII: no let/const/arrows/template strings/Array.indexOf; check with `node _kit/dev/check_jsx.js` |
| AE stills missing right after the job | `saveFrameToPng` is asynchronous in AE 2024+; `make_job.py stills --wait` waits for the files, otherwise wait a few seconds |
| poses/walks differ from the animatic | ExtendScript's `Array.sort` is not stable: engine code must sort with `stableSort()`; run the timeline check below |
| blank faces / eyes and mouth missing for a few frames | AE's `random()`/`seedRandom` give different numbers on different properties: per-frame choices shared by several groups (blink, talk flaps) must use the deterministic hash (`hash01` in the engine, same in ra_preview.py) |
| actor enters from the wrong side / wrong value picked | ExtendScript mis-evaluates unparenthesised chained ternaries (`a ? b : c ? d : e`): use lookup objects or full parentheses; `check_jsx.js` flags them |
| `make_job` says OK but nothing was built | old kit: the project path was not relative to the workspace (`projects/<slug>`); current make_job resolves it and the engine fails loudly when the folder is missing or the build logged errors |
| eye lids a different colour from a flushed face | lids are skin-coloured cuts driven by the CTRL `flush`/`flushCol` controls; rebuild with the current engine |
| whole layer vanishes when an effect is faded | never fade a Fill effect's Opacity (0 % hides the layer); fade a Tint's Amount or the effect's Compositing Options |
| red caption words look pink | the caption Glow must keep "Composite Original" = 1 (letters over the halo) |

Engine changes - dry-run before After Effects (needs `npm i acorn` in `_kit/dev` or the workspace):
`node _kit/dev/mock_ae.js projects/<slug> --timeline` (build errors, expression syntax, array maths; the mock sorts
unstably like ExtendScript) then `python _kit/dev/compare_timeline.py projects/<slug>` (every character's control
values must match the preview: 0 mismatches), `python _kit/dev/rig_parity.py projects/<slug>` (every pose's joints,
arm layer order and three-quarter torso/clothing turn against ra_rig.py: 0 problems) and, with animals,
`node _kit/dev/mock_ae.js projects/<slug> --creatures` + `python _kit/dev/creature_parity.py projects/<slug>`.
Then the live self-test.
With many characters `rig_parity.py` can run node out of memory (one sandbox per expression and pose): run it with
`NODE_OPTIONS=--max-old-space-size=8000`, or on a trimmed copy of the plan with the characters you changed.
