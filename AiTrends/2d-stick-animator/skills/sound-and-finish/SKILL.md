---
name: sound-and-finish
description: Finish a glow stick-figure Short - music bed, sound effects, mix and loudness master, mux with the After Effects (or fallback) render, measure the result against the reference style, look at contact sheets, and deliver the MP4 with title, description credits and a thumbnail frame. Use when the user says "add music", "add sound effects", "mix the audio", "the music is too loud", "export the final video", "QC the video", "check it against the samples", or when the make-story-short pipeline reaches the finishing stage.
---

# Sound and finish

Tools in `<workspace>/_kit/py/`. Targets: house-style `references/sound-style.md`.

## 1. Music
Ask the user once: their own licensed track, ElevenLabs music, or the built-in procedural bed.
- Own track: copy to `audio/music.wav` (ffmpeg converts); it is looped/trimmed automatically.
- ElevenLabs: `python eleven.py music "instrumental storytelling bed, curious and mysterious, plucked strings and
  soft synth pad with a sustained melody, steady 116 bpm, no vocals, no big drops" -o P/audio/music.wav --dur <s>`
  (tense / playful / sad variants by mood).
- Procedural: `python music.py -o P/audio/music.wav --dur <duration> --mood mystery|tension|playful|sad|war`.

## 2. SFX
- `compile_spec.py` already places pops, whooshes (special transitions only), impacts (shakes), cash (money
  rain), glitch and swells; files come from `audio/sfx/` (copied from the kit by new_project.py; regenerate with
  `sfx_kit.py -o P/audio/sfx`).
- The immersive layer is planned with the shots (plan-shots, house-style sound-style.md): an ambience bed under
  every location and a real sound on every on-screen action. Check it is all there and audible: listen to the
  animatic/mix at the start of each scene and on each action (a race start needs a loud pistol crack and the crowd).
  Add missing ones in `spec.audio.sfx` - cues can trim a longer file: `{"t": 3.5, "file": "audio/sfx/src/wind.wav",
  "gain_db": -20, "offset": 0, "dur": 10, "fade_in": 0.3, "fade_out": 0.4}` - or make a specific one:
  `python eleven.py sfx "heavy wooden door slams shut in a stone cellar" -o P/audio/sfx/door.wav --dur 1.2`.
- Keep whooshes rare (2-9 per video). Re-run compile_spec.py after edits.

## 3. Mix and master
Living creatures are heard automatically: compile_spec adds each creature's `sound` when it appears and every ~3 s
while it is on screen (quieter after the first); check they sit under the voice, not over it.
`python mix.py P` -> `audio/mix.wav`: speech normalised, music ~17 dB under the voice with a dip under words
(`--music-db -15..-20`), SFX at their gains, two-pass loudnorm to -14 LUFS, -1.2 dBTP.
Listen-check by numbers: `ffmpeg -i P/audio/mix.wav -af ebur128 -f null -` (I ~ -14), and spot-check moments.

## 4. Final file
`python finish.py P` (uses the newest `exports/ae_render.*`, or `--video exports/preview_full.mp4`) ->
`exports/final.mp4` (H.264 High CRF 16, 1080x1920, 30 fps, AAC 192k, faststart).

## 5. QC (always, before saying it is done)
`python qc_video.py P/exports/final.mp4` -> `qc/report.md` + `qc/sheet_*.jpg`. Stage the sheets and LOOK at them:
every 0.5 s should show a lively, readable frame with a yellow caption; compare with
`house-style/references/look/frames_board.jpg`. Fix anything flagged (format, duration, motion share, caption
presence, loudness, frozen/black frames), rebuild/re-render as needed.

## 6. Deliver
- Send `exports/final.mp4` (SendUserFile) and say where it is in their folder.
- Title (ALL CAPS from the script stage), a 1-2 line description, and the credits needed from
  `assets/manifest.csv` (CC BY etc.), plus 3-5 hashtags. Suggest a thumbnail frame time (the most striking still).
- Update PROJECT_STATE.md (what was made, settings, anything hand-edited in After Effects).
