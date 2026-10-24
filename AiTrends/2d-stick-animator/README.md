# 2D Stick Animator

Make faceless **glow stick-figure story Shorts** (9:16, any length you choose - 60 s by default, up to 3 minutes) in the style of the seven reference videos it was
built from (HE BECAME A HERO., FORGOTTEN IN THE BASEMENT, THE BRAVE PASSENGER, HOW WITCHES SURVIVED THE PAST,
HE SNEAKED INTO AN ASYLUM, HIV OUTBREAK THEORY, MONEY RAIN) - from story to final MP4, with the editable
animation built in **Adobe After Effects** on your computer through a script bridge and computer use.

## What's new in 2.3.0 (from user feedback on THE WORST MARATHON EVER)
- **One colour per character**: head, body, arms and legs always share the body colour; only the costume pieces
  differ. compile_spec drops `sleeve`/`pants`/`shoes` and `face_color`; validate_spec warns. Torso costume pieces
  are always sleeveless (costume.py strips sleeve words and adds the instruction).
- **People sit IN vehicles**: `vehicles.py layers <image>` splits a car/cart/carriage/boat into a seat layer (behind
  the riders) and a door layer (in front) and finds the seats; a shot's `vehicles` list seats the riders on the
  cushions (thighs along the seat, knees bent, shins behind the door, hands on thighs or the wheel) and moves them
  with the vehicle; seated waves.
- **Animals move like animals**: `creatures.py gait <image> --kind run|walk|hop|fly|two_legs` (or `"gait"` in the
  asset list) makes a 4-frame gait cycle of the same animal; compile_spec flips the frames along its path.
- **Immersive sound**: the plan carries an ambience bed under every location and a real sound on every on-screen
  action (the starting pistol on "began"...); `audio.sfx` cues can trim/fade a longer file (`offset`, `dur`,
  `fade_in`, `fade_out`); the animatic is always mixed with the full SFX layer (ra_preview runs mix.py).
- Real-size props on the floor line; hand-made camera keys are clamped inside the picture; `exact` props for
  back-to-back frames (both renderers).
- **Arms come out of the shoulders, under the clothes**: both renderers draw the torso garment again over the top of
  each arm in front of the body (armholes, `look.armhole_cap` in rig.json), so straps and shoulders cover the arm's
  root instead of the arm lying on the chest.
- finish.py uses `-fps_mode cfr` (ffmpeg 8+ removed `-vsync`).

## How a video starts
1. **Story and length**: you choose the length (30 s, 60 s, 90 s, 2 min... or any exact length); the word count
   follows from it (seconds x words per minute / 60: ~222 words for 60 s, ~444 for 2 min, measured on your own
   voice once you have made a video with it). Claude presents 10 story concepts that fit that length (true stories, legends, strange experiments...), or you paste your own story.
2. **Script**: for a chosen concept, Claude writes the full script with the channel's story prompt (When/After/During
   opener, short cause-and-effect sentences at the target word count, no names or dialogue, an ironic twist), checks
   it with `story_check.py`, and you change it until you approve it. A pasted story is used exactly as written.
3. **Voice**: ElevenLabs with your own API key and voice ID (stored on your computer, never in the plugin) - a short
   sample to approve, then the full voiceover, tightened to the house pace and checked against the chosen length.
4. **Timing**: Whisper word timestamps aligned to the script (ElevenLabs forced alignment as a fallback), captions.
5. **The edit**: shot plan, cast and assets, animatic, After Effects build, render, sound, QC.

## Asset modes
Each project is either **kie** (costume pieces, backgrounds and props generated with Kie.ai - most detailed,
costs credits, always shown and approved first) or **free** (bundled costume library recoloured per character,
Fluent 3D emoji, Openverse / Wikimedia Commons / Pexels / Pixabay / Internet Archive - nothing paid). The
pipeline asks at the start.

## Skills
| skill | what it does |
|---|---|
| `make-story-short` | the whole pipeline with checkpoints (start here: "make a video like the samples about ...") |
| `house-style` | the measured style bible: look, characters, editing rhythm, captions, sound, shot-by-shot breakdowns, reference frames |
| `write-story-script` | 10 story concepts or your own pasted story, the script from the channel's story prompt (`references/story-prompt.md`), your edits, approval, title; batch mode for 10 scripts |
| `voice-and-timing` | your ElevenLabs key + voice ID (or your recording), voice sample, pause tightening, Whisper word timing, one-word captions |
| `plan-shots` | the edit: cuts, camera, cast, poses, faces, props, icons, FX, transitions -> spec.json, validator, animatic |
| `make-assets` | costume pieces fitted to the rig, backgrounds, props, icons, FX plates, live inserts - **Kie.ai or free sources only, your choice per project** |
| `after-effects-build` | bridge + computer use, build the AE project, stills, render; fallback renderer |
| `sound-and-finish` | music, SFX, mix (-14 LUFS), final MP4, QC report against the reference numbers |
| `setup-studio` | install the kit into your workspace, packages, font, AE scripting preference, bridge, self-test |

## Desktop server (`servers/ae_desktop_server.py`, `.mcp.json`)
A stdlib-only local MCP server the Claude desktop app runs on your computer: `ae_find`, `ae_launch`, `ae_run_jsx`
(starts the bridge or runs any job script in After Effects), `ae_enable_scripting` (prefs flag), `ae_kill_stale`,
`install_font`, `open_path`, `read_text`. Computer use covers the rest (seeing After Effects, dialogs, checks).
Needs `python` on the computer's PATH.

## The kit (`kit/`, copied to `<workspace>/_kit/`)
- `ae/ra_engine.jsx` - After Effects engine (ES3): rigged rubber-hose characters driven by one control layer
  (arms always out of the shoulder corners - a jacket's armholes or the bare body's top corners; front views for
  standing and reacting, three-quarter views for acting - the body and its clothes turn a little towards the facing
  side, the camera-side arm in front of the chest and the other behind it; hands placed on the chin, ear, brow,
  cup or object), living animals (creatures: whole body, pecking, wandering, hopping,
  flying, swimming, fleeing, sleeping, with their sounds; same maths as the preview),
  (body proportions measured from the references - the head floats above a sturdy torso - 79 poses with front and
  three-quarter views, characters that drag, carry and lift each other and
  always step when they move (forwards or backwards), wide/tall locations the camera travels across, walk/run/idle/talk/blink, 13 eye and 10 mouth states that look where
  the character looks, skin colours, topple, sleeves/pants/shoes, fitted costume pieces drawn under the face,
  held props), per-shot comps with the measured jolt camera, backgrounds with grades, pop-in props, 3D-emoji icons, thought/
  speech bubbles, clock badges, money rain, embers, smoke, tints, glitches, B&W states, transitions, captions,
  vignette, grain, audio, stills and render.
- `ae/ra_bridge.jsx` - runs queued jobs inside After Effects (no clicking after it is started).
- `py/` - pipeline tools: vehicles (seat/door layers, seats, riders seated inside), auto_plan (with a MUST SHOW list per shot), coverage (every object and action the narration
  names must be on screen and visible on its word - checked by rendering - plus a detail sheet for a critical
  review), props (how each held prop is gripped: handle in the hand, working end out), validate_spec, compile_spec (auto camera,
  actions, steps, carrying, automatic SFX),
  assets (asset list in kie or free mode), costume (GPT Image 2.5 pieces drawn on the rig template, the bundled
  library), ra_preview (animatic and
  fallback renderer with the same rig maths), creatures (the animals the kit knows, their behaviours and sounds, image prep, frame strips),
  story_length (the chosen length -> word, sentence, beat, shot and location targets; voice length check),
  story_check (script rules: length, sentences, opener, no names or
  dialogue, twist, drawable sentences), transcribe (Whisper or ElevenLabs alignment), captions, tighten, eleven
  (voice ID check and per-project voice, TTS sample and full narration, SFX, music), music, sfx_kit,
  mix, finish, qc_video, cast_sheet, gen_image, gen_video, fetch_assets, cutout, make_job, install_kit,
  new_project, selftest, keys.
- `data/` - style targets, rig, poses, faces, costume parts, story lexicon (what every verb and object needs on screen). `assets/icons_webp/` - 373 Fluent 3D emoji (MIT).
  `assets/costumes_webp/` - 54 costume pieces (13 hair styles, 4 beards, 23 hats and helmets, 3 face pieces,
  11 outfits) with their rig placements, for free mode.
  `fonts/` - Anton (OFL). `dev/` - ES3 checker, a mock After Effects for dry runs, a timeline check that
  compares the After Effects keys of every character with the preview renderer, and rig and creature parity checks
  (every pose's joints, arm layers and body turn; every animal's motion) against the Python maths.

## Requirements
After Effects 2022+ (2023+ recommended; tested live on After Effects 2025 for Windows: bridge, build, stills, render),
Python 3.9+, ffmpeg. Optional keys (each user's own, stored by `keys.py` outside projects, never in the plugin):
ElevenLabs (voice/SFX/music; plus your voice ID, saved in `~/.2d_stick_animator/settings.json`), Kie.ai (kie asset mode: GPT Image 2.5, Nano Banana Pro; ~6 credits per costume or
prop, ~20 per background), Pexels/Pixabay (more stock in free mode). Without After Effects the fallback renderer makes the
video from the same plan.

## Licences
Code: for the plugin owner's use. Icons: Microsoft Fluent Emoji, MIT (`kit/assets/icons_webp/LICENSE.txt`).
Font: Anton, SIL OFL (`kit/fonts/OFL-Anton.txt`). Costume library: generated for this plugin with GPT Image 2.5
on Kie.ai (`kit/assets/costumes_webp/index.json` keeps each piece's prompt). Reference frames in `skills/house-style/references/look/` are
small stills from the user's reference videos, kept as a private style guide.
