---
name: make-story-short
description: Make a complete faceless glow stick-figure story Short (9:16, at the length the user chooses - 60 s by default, up to 3 minutes) in the style of the reference videos, end to end - story concepts or the user's own story, the script written with the channel's story prompt and edited by the user, ElevenLabs voiceover with the user's key and voice ID, Whisper word timing, shot plan with the reference editing rhythm, rigged characters, backgrounds, props, icons, FX, captions, After Effects build through computer use, render, sound and QC. Use when the user says "make a video like the samples", "make a stick figure story short", "make a Short about this story", "do the whole video", "/make-story-short", or asks for a new video in this style (with Kie.ai generation or free sources only).
---

# Make a glow stick-figure story Short (pipeline)

Run the stages in order with the user's checkpoints. Each stage has its own skill with the details - load it when
you reach it. Keep `projects/<slug>/PROJECT_STATE.md` up to date and use a task list (one task per stage, last
task = QC). Always load the `house-style` skill before planning or judging pictures.

| # | stage | skill | output | checkpoint |
|---|---|---|---|---|
| 0 | studio ready | setup-studio | `_kit/`, bridge alive | first run on a computer: self-test passes |
| 1 | story + length | write-story-script | the chosen length (`script/length.json`: words, sentences, beats), 10 concepts (`stories/concepts_<date>.md`) or the user's pasted story; project created | **user picks the length and a concept** (or pastes a story) |
| 2 | script | write-story-script | `script/script_final.txt`, `title.txt`, `research.md` | generated: **user edits / approves the script**; pasted: used as written |
| 3 | voice + timing | voice-and-timing | ElevenLabs key + voice ID, `audio/voice.json`, `audio/voice.wav` at the chosen length, `timing/words.json`, `captions.json` | **user approves the voice sample** |
| 4 | shot plan (the edit starts) | plan-shots | `plan/spec.json`, `plan/shotlist.md`, `plan/asset_list.json` | - |
| 5 | cast + assets | make-assets | costume pieces, backgrounds, props, icons in `assets/`, `qc/cast_sheet.png` | kie mode: **credit spend approved**; **user approves cast sheet** |
| 6 | animatic | plan-shots (step 4) | `exports/preview.mp4` (with the immersive sound layer), `qc/preview_sheet.jpg` | vehicle/animal close-ups checked; **user approves the animatic** |
| 7 | After Effects build | after-effects-build | `ae/<slug>.aep`, `ae/stills/` | stills checked (by you) |
| 8 | render | after-effects-build | `exports/ae_render.*` | - |
| 9 | sound + final + QC | sound-and-finish | `audio/mix.wav`, `exports/final.mp4`, `qc/report.md` | deliver |

## Start
1. `python3 _kit/py/install_kit.py --check` (setup-studio if anything is missing; on a linked computer run the
   tools through device_bash in `$HOME/mnt/<folder>`).
2. Ask only what changes the work, in one AskUserQuestion with up to four questions:
   - **Story**: show me story concepts (Recommended) / concepts on a theme (they type it) / I'll paste my own story /
     write it from my topic or article.
   - **Length**: 60 seconds (Recommended, like the samples) / 30-45 seconds / 90 seconds / 2-3 minutes - any exact
     length in Other ("75 s", "1:40"). Not needed for a pasted story (its words set its length).
   - **Voice**: ElevenLabs with my API key and voice ID (Recommended) / my own recording.
   - **Assets**: Kie.ai (generated, most detailed, costs credits) / free sources only (bundled costume library, 3D
     emoji, free photo/video libraries; nothing paid).
   Music is asked at the sound stage (sound-and-finish). Defaults if they say "you decide": concepts, 60 s,
   ElevenLabs, free sources. Show the length's targets right away (`python3 _kit/py/story_length.py --seconds
   <length>`: words, sentences, shots, locations) and, in kie mode, that a longer video needs more backgrounds and
   props (more credits) and renders longer.
3. Stage 1-2 (write-story-script): concepts that fit the length -> the user picks -> `python3 _kit/py/new_project.py
   "<TITLE + tags>"` -> `story_length.py P --seconds <length>` -> script at the target word count -> the user's
   changes -> approved. A pasted story makes the project with its title and is used as
   written. Record the asset choice as soon as the project exists: `python3 _kit/py/assets.py mode
   projects/<slug> kie|free` (kie: check `keys.py check`; if there is no Kie.ai key, ask the user for theirs and
   store it with `keys.py set kie <key>`).
4. Stage 3 (voice-and-timing): ElevenLabs key check (ask for the user's own key if missing, store it with
   `keys.py set elevenlabs <key>`), voice ID (`eleven.py voice <id> --project P --save`), a 2-sentence sample to
   approve, the full voiceover, pause tightening, Whisper timestamps, the length check against the chosen length
   (`story_length.py P --check-voice`), captions. Then go straight on to the edit
   (stage 4 onward). Keys live only on the user's computer (`~/.2d_stick_animator/`) - never in the project,
   the plugin, a log or a message.

## Quality bar (the samples' level of detail)
- About 0.55-0.8 shots per second (30-45 at 60 s; `story_length.py P` prints the range for the chosen length),
  median ~1.3 s, every shot moving, a visual change on every key word.
- 3-8 named characters with distinct colours, each in a detailed costume (illustrated hair/hat/beard piece for
  everyone, an outfit for the main cast), front-on faces with the samples' solid black eyes looking where the
  character looks, every one acting (front poses when talking/reacting, poses on verbs, faces on emotions,
  walking/talking). **One colour per character**: head, body, arms and legs match - no sleeve/trouser/shoe colours,
  no head-colour flushes; torso garments are sleeveless pieces (user feedback v2.3).
- The measured camera on every shot (`"camera": "auto"`): a jolt every 0.45-1.25 s, in and out, aimed at faces.
- Characters act every reaction (faces, poses); icons only for abstract concepts, ~5-8 a minute at most.
- Every animal in the story is a living creature in the drawn costume style - whole body, moving (pecking,
  wandering, hopping, flying...) with a real gait cycle (legs in sequence, never a sliding still) and heard - never
  a head icon.
- People in a vehicle sit IN it: seat layer behind them, doors in front, thighs on the cushion, knees bent, nothing
  below the floor (shot `vehicles`, vehicles.py). Send full-size close-ups of vehicle shots to the user first.
- Props at their real size next to the characters (a well ~0.85 x a person, a mile post ~0.5), standing on the floor.
- Every object the narration names and every action it describes is on screen and visible on its word
  (`coverage.py P --visible` reports 0 missing).
- A fresh, detailed background for each location (one per ~5-9 s: 7-12 at 60 s, 13-24 at 2 min), props and icons for every concrete noun,
  2-6 special transitions, 1-4 B&W/grey moments, FX where the story has fire/smoke/money/smell/water, 0-3
  real-looking inserts, a loop or fade ending.
- Captions for every word; sound never stops and is immersive: an ambience bed under every location and a real
  sound on every on-screen action (the starting pistol on "began", engines, footsteps, bites, crowds); the
  animatic is always sent WITH this sound layer (ra_preview mixes it); -14 LUFS.
Measure with validate_spec.py (plan), the animatic sheet (look), qc_video.py (final). Do not deliver a video that
fails these; fix and re-render.

## Time and cost notes for the user
Generation costs credits (Kie.ai/OpenAI/ElevenLabs): show counts before spending. A full After Effects build takes
under a minute for a short test and a few minutes for a full video; rendering runs about 3 min per 12 s of
video on the test machine (roughly 15-30 min for a 60 s Short, 30-60 min at 2 min, 45-90 min at 3 min; more on
slower computers); the fallback renderer takes 20-40 min per minute of video at full resolution. Asset credits in
kie mode grow with the number of locations and props, so roughly with the length.

## If something is unavailable
- No After Effects / computer offline: fallback renderer (`ra_preview.py --full`) and say the AE build is pending.
- No ElevenLabs: the user's recording or another TTS they have; timing works on any WAV.
- No faster-whisper on the computer: `transcribe.py --engine eleven` (ElevenLabs forced alignment) or install it
  with setup-studio.
- No Kie.ai key or the user chose free: free mode - the bundled costume library (recoloured), kit 3D emoji,
  Openverse/Commons/Pexels/Pixabay/archive.org; say backgrounds and props will be less story-specific.
