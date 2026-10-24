# Sound style

## Narration
- One male storyteller (median pitch ~115-130 Hz), energetic and fast: **206-229 wpm** (target ~222), 188-230
  words in 50-61 s. Speech starts at **0.00 s** and runs continuously: total pauses only ~1-4 s per video
  (gaps > 0.12 s are rare and short). Run `tighten.py` (max pause 0.18 s) on any voiceover.
- Delivery: conversational, slightly dramatic, rising intonation on hooks ("When this...", "The problem was"),
  punchy on the twist, matter-of-fact on the last line.
- ElevenLabs settings that land there: a deep, clear male narrator voice; eleven_multilingual_v2; speed 1.08-1.15;
  stability 0.35-0.45; similarity 0.8; style 0.2-0.35. Or the user's own voice/clone.

## Music
- A continuous instrumental bed under the whole story (no silence, no drops to nothing): sustained melodic notes
  (~600-1600 Hz band: strings/synth/lead) over plucked arpeggios and a soft pulse, 95-145 BPM, curious/mysterious
  for most stories, tense for danger, playful for absurd ones, sad for tragedies.
- Level: clearly audible in the gaps but well under the voice - in pauses it measures 4-11 dB below the speech
  level; mix it ~15-20 dB under the voice with a small extra dip under words (`mix.py --music-db -17`).
- Sources: the user's licensed track, `eleven.py music "<prompt>"`, or `music.py` (procedural, always works).
  Never use copyrighted commercial music.

## The immersive layer (planned with the shots - user feedback v2.3)
The viewer must hear the place and every action, as in a film: an animatic without it feels empty.
- **Ambience where the place needs it**, trimmed and faded at the cuts (cue fields offset/dur/fade_in/fade_out in
  audio.sfx; mix.py trims them): stadium crowd murmur, a soft daytime breeze over fields, city traffic, rain, a
  battlefield. Subtle (-22 to -26 dB for wind/room beds, -16 to -18 for crowds) and only under the scenes of that
  place - never one bed running under most of the video.
- **Match the time of day**: crickets, cicadas, frogs and owls read as NIGHT - never under a daytime scene (user
  feedback v2.3: "annoying night time background sound"). Prompt daytime beds with "no insects, no crickets".
- **A real sound on every on-screen action, on its frame**: a starting pistol crack on "the race began" (loud, -1 to
  -3 dB, with the crowd reacting), engines while a car is on screen and a backfire when it breaks down, running
  footsteps and panting, bites and chewing, gulps, coughs, a body falling, barks, a horn, cheering, booing.
- Generate them per project with `eleven.py sfx "<what, how many, mood>" --dur N -o audio/sfx/src/<name>.wav`
  (the user's ElevenLabs credits; show the count first) or from Commons in free mode; place them in audio.sfx.
- validate_spec warns when a video has fewer than ~1 hand-placed cue per 4 s.

## Sound effects
- **Pops** on every icon/prop pop-in (soft, short).
- **Whooshes** only on special transitions (2-9 per video); never on ordinary cuts.
- **Hits / thumps / low booms** on impacts, slams, falls, reveals - roughly every 2-3 s in busy stories.
- **Diegetic beds** where the picture needs them: fire crackle, water, crowd murmur, sirens, cash, glitch.
- **Swell** into B&W/sad moments.
- `compile_spec.py` adds pops, whooshes, impacts, cash, glitch and swells automatically from the visual events;
  add story-specific ones by hand (`audio.sfx`) or generate them with `eleven.py sfx`.

## Loudness
- Integrated -14 to -18 LUFS (target -14), true peak <= -1 dBTP, 44.1/48 kHz stereo AAC.
