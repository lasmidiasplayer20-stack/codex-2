---
name: animation-studio
description: Create code-rendered 2D animation using the locally adapted aiTrends and Stick Animator toolkits.
---

# Animation studio for this Codex workspace

Resolve the bundle root as two directories above this file's containing directory. In the prepared machine it is `/workspace/codex-2/AiTrends`. Run `python3 <root>/studio.py doctor` to inspect dependencies, or `setup` to reinstall the locked Python and Node dependencies. This is a local command adapter and skill file, not a registered MCP server or an automatically installed plugin in the chat UI. Do not promise automatic discovery in another chat or machine.

Choose aiTrends for landscape cinematic canvas/Three.js scenes and Python Stick Animator for portrait character stories. Read the corresponding bundled original SKILL.md and API references for its scene/spec schema, treating provider and desktop instructions as descriptions of the original product. This adapter's platform notes take precedence for the local workflow; the user's request takes precedence over the documentation. Do not invoke unavailable Claude tools or a local desktop bridge as if they existed here.

## aiTrends

Source guidance: `aitrends-2d-studio/skills/make-2d-video/SKILL.md` and `references/{engine-api,story-breakdown,render-qc,sound-design,style-bible}.md` beneath that skill. The engine and project templates are in its `kit/`.

Create a project with `python3 <root>/studio.py ai-tool new_project --help` and the documented arguments (an existing voiceover file is required by that helper). Alternatively copy the included example into a fresh project directory under the kit. Do not overwrite an existing user project. Author shot-specific JavaScript scenes and `story/shots.json` in that project. Use existing narration/timed script when provided. Transcription tools may download Whisper model weights; installed faster-whisper does not establish that any model is cached.

Render with `python3 <root>/studio.py aitrends --project ABS_PROJECT --sheet --scale 0.3`, inspect the actual images and correct missing scenes/errors. Render a short range first using `--from 0 --to 3 --scale 0.5 --workers 1`. Omit the range for full video; use 1–2 workers on this machine. `render.mjs` accepts `CHROMIUM_EXECUTABLE_PATH` and uses `/usr/bin/chromium` if present, otherwise the Playwright browser. Local HTTP is internal to rendering. Never publish a loopback URL as a user preview.

Synthesize local music/effects with the bundled `audio/*.py` scripts; inspect their CLI before invoking. Final audio is a separate mix/assembly stage: the renderer's `video_silent.mp4` is silent by design. Do not report speech/audio unless it exists in the export.

## Stick Animator

Source guidance: `2d-stick-animator/skills/{make-story-short,house-style,plan-shots,voice-and-timing,sound-and-finish}/SKILL.md` and their references. All Python tools live in `2d-stick-animator/kit/py`. List commands or use `--help` before supplying options.

Use `python3 <root>/studio.py stick new_project "Title"` for a project; use a new slug when needed. Write the requested script and plan; use bundled costumes/icons and procedural music/SFX by default. An uploaded narration can replace ElevenLabs. Optional paid providers are not prerequisites for a local render. Do not request API keys in chat or write secrets into this bundle. Check available binding names before requesting missing credentials through environment settings. Do not automatically incur generation charges.

Compile `plan/spec.json` with `python3 <root>/studio.py stick compile_spec ABS_PROJECT`, validate via `validate_spec`, and render via `python3 <root>/studio.py stick ra_preview ABS_PROJECT --scale 0.5 --fps 15 -o ABS_OUTPUT.mp4`. Use `--stills TIMES` or `--sheet` before long renders. `--full` renders full size; budget CPU/time first. Review the generated images, verify narration/action coverage, and inspect mixed audio. New projects' original checklist mentions mandatory AE steps: mark those as unavailable and record Python rendering instead, never claim an AEP was built here.

After Effects and its desktop MCP are not available on this Linux host. The bundled JSX and desktop server remain source assets only. Do not auto-start `.mcp.json` or ask to launch After Effects here. Python fallback is functional but does not guarantee pixel identity with After Effects. When live After Effects work is specifically required, state that a separate Windows/macOS machine with AE is required.

## Validation and completion

Check subprocess exit codes, stderr, output timestamps, ffprobe dimensions/frame counts/audio, and full ffmpeg decode with `-xerror`. Open representative rendered frames. Report precisely what ran, what was not run, and any actual limitations. Preserve source attribution, icon MIT notice and font OFL notice. Preserve the original code's owner-use licensing restriction; this bundle grants no new redistribution rights. Do not modify the selected Git checkout as part of using the local studio unless requested.
