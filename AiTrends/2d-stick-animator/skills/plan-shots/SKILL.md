---
name: plan-shots
description: Turn the timed narration of a glow stick-figure Short into a complete shot plan (plan/spec.json) - cuts on the right words, a camera move per shot, cast design, poses and faces on the verbs, props on the nouns, living animals as moving creatures with real gait cycles and their sounds, people riding inside vehicles (seat layer behind, doors in front), an immersive sound layer (ambience under every location, a real sound on every action), a few concept icons, B&W moments, FX, transitions and SFX - then validate, compile and preview it as an animatic. Use when the user says "plan the shots", "make the storyboard", "edit it like the samples", "fix the pacing", "add more action", "change shot 12", or when the make-story-short pipeline reaches the planning stage. This is where the editing style lives.
---

# Plan the shots (the edit)

Inputs: `timing/words.json`, `timing/captions.json`, `audio/voice.wav`, the approved script.
Output: `plan/spec.json` (hand-made plan) -> `plan/spec_compiled.json` (what the engines build) + animatic.
Read first: the `house-style` skill (SKILL.md + `references/editing-grammar.md`), then `references/spec-schema.md`
and `references/shot-recipes.md` in this skill. Tools: `<workspace>/_kit/py/`.

## 1. Skeleton
`python auto_plan.py P --title "TITLE"` writes `plan/spec.json` with shots cut on word onsets in the measured
rhythm (median ~1.3 s), each with its words (`say`, `w` word times), `"camera": "auto"` (the measured jolt camera,
planned at compile time from what happens in the shot) and empty visual slots, plus `plan/shotlist.md`; each shot also lists `ideas` - optional concept icons for abstract
words (death, danger, an idea, time) with their word times; most shots need none. Read the shot list. Merge shots that share one picture idea, split shots
longer than ~2.5 s with a punch-in or a cut on the next noun, and move cuts so each shot starts on the word that
changes the picture. Keep shots contiguous (each `t` = previous `end`).

## 2. Visual plan per shot (write it in shotlist.md first, then the spec)
For every shot answer: where are we (background), who is on screen and what are they doing on which word (pose
keys, walk/talk, face), what pops in on which noun (prop/icon), how the camera moves, and whether it needs a
grade/state/FX/transition. Rules:
- Show what the words name, on the word - ALL of it. The shot list's MUST SHOW column lists every object the
  narration names and every action it describes (from `_kit/data/story_lexicon.json`): each one gets its picture at
  its word - the object as a prop, held prop or costume piece, an animal as a living creature, the action as a pose/act with its tool in hand
  ("put makeup on him" = a soldier holding a makeup brush and brushing the face, not just standing there). Words the
  lexicon does not know count too: read the script line by line and show every concrete thing and verb. Use the recipes for recurring beats (death, idea, order, duration,
  money, danger, smell, crowd, realisation, travel, fight, arrest, flashback, inside the body, real insert).
- **Act it first, icons last.** Emotions are faces (eyes, mouth) and poses - never emoji faces, never a head-colour
  flush (house rule: one colour per character);
  refusing, agreeing, trusting, believing, sleeping are poses and faces (head shake/`arms_crossed_front`, nod,
  handshake/hug, `sleep_lie`); people are characters; objects are props in a hand or in the scene. An icon only for
  an abstract concept nobody can act (death/skull, danger, an idea in a thought bubble, a duration badge, an
  amount), at most ~5-8 icon moments a minute in all, one at a time (a pair at most), 1-3 clock badges a video.
  validate_spec.py warns about emotion, gesture, people and animal icons and about too many icons.
- **Living things are alive.** Every animal that is in the story's scene is a `creature` (spec-schema): the whole
  animal, never a head icon, moving the whole time it is on screen (chickens `peck`, dogs/cats/pigs `wander`,
  rabbits `hop`, birds `fly`, fish `swim`, a scared flock `flee`s, a sleeping dog `sleep`s), a flock as `count` +
  `spread`, sized to the characters (`creatures.py list`: chicken ~0.24 of a person's height), on the ground line,
  with its `sound` (clucking, barking...) - compile_spec repeats it while it is on screen and the camera gives the
  animals their own push-ins. Plan where they are and what they do on the words that name them.
  **Every animal that moves on screen runs its gait cycle** (user feedback v2.3: a sliding still "moves like a
  doll"): give it `"gait": "run|walk|hop|fly|two_legs"` in the asset list (or `creatures.py gait <image> --kind ...
  --yes` later); compile_spec flips the frames along its path. Frame the animal and whoever it chases together.
- **People in vehicles sit IN them** (user feedback v2.3): a car, cart, carriage, wagon or boat with people in it is
  a shot `vehicles` entry (spec-schema), never a prop with actors standing behind it. vehicles.py splits the
  picture into a seat layer (behind) and a door layer (in front) and seats each rider: thighs along the cushion,
  knees bent, shins behind the door, hands on the thighs (the driver's on the wheel). Waves from a seat use the
  rider's `"wave": [[t0, t1]]`. Runners passing the vehicle run on the far side (smaller, higher) so they never
  overlap the seats.
- **Real sizes**: props stand on the floor at their real size next to the characters (a well ~0.85 x a person's
  height, a mile post ~0.5, a car ~2 x long) - house-style visual-style.md. Account for the picture's transparent
  margin when placing a prop by its centre (measure its opaque box). validate_spec warns when a well, door, mile post,
  chair, table, barrel... is drawn far from its real size next to the characters in its shot, and suggests a `w`.
- **One colour per character**: no `sleeve`/`pants`/`shoes` on the cast and no `face_color` keys - compile_spec
  drops them, validate_spec warns.
- **Plan the sound with the shots** (house-style sound-style.md, "The immersive layer"): an ambience bed under every
  location and a real sound on every on-screen action, on its frame - the starting pistol on "began", engines,
  footsteps, bites, gulps, coughs, barks, cheers, boos. Write them into `audio.sfx` (cue fields `offset`, `dur`,
  `fade_in`, `fade_out` trim a longer file) and the files into the asset list (`kind: sound`).
- One location carries 2-4 shots with new framings; then move on. Re-use backgrounds deliberately.
- Leads big (h 900-1300; close-ups 1500-2400 with `crop: true`), feet near y 1650-1850; faces never under the
  caption band (y 1380-1560) unless the caption is over the body.
- Two characters side by side stand at least ~0.45 x their height apart, so a gesture or a held prop never pushes an
  arm into the other body; closer only when they really touch (handshake, hug, push, grooming: `"touch": true`).
  Clean silhouettes: pointing, holding and giving reach outward or forward. Use the pose library's gestures (its
  hands sit on the chin, ear, brow, cup and object) rather than `set` arm angles; in front views only
  `arms_crossed`, `arms_crossed_front` and `hug_self` fold the arms across the chest.
- Every actor acts: a pose key on each relevant verb (0.15-0.3 s `dur`), a face change on emotional words,
  `talk` ranges while they speak, `walk`/`move` when they travel, actions (`act`) for repeated gestures. These
  keys are also the camera's beats: a shot with nothing happening gets a lazy camera.
- Faces like the samples: front-view poses when standing, talking or reacting (`stand`, `explain`, `shocked`,
  `hands_hips`...); three-quarter poses (body turned a little to the facing side) when acting on something -
  walking, pointing, holding, eating, phoning, fighting, sitting. Eyes look where the
  character looks (`gaze`, `gaze_y`): at the other character, down at the body on the floor, out at the viewer.
  Strong states are acted (eyes, mouth, pose, `shiver`, `hug_self`), never with a head-colour flush.
- Keep heads in frame: seated/lying characters low in frame need their head above the caption band; a `topple` or
  fall goes towards the open side of the frame.
- Give travel room: when characters walk, run, chase, drag someone or the story moves along a place, make the
  location a wide (or tall) `bg.world` and move them a real distance across it - movement that only shifts a few
  hundred pixels reads as standing still. Legs step automatically whenever a character moves.
- When the story says someone is taken, dragged, carried, lifted or led, show it: movers crouch onto them
  (`bend_grab`), pull or carry while they `move`, and the moved character is `attach`ed to a mover's hand so it
  really travels (recipe "Moving someone").
- Plan 1-4 B&W/grey moments, 2-6 special transitions, 0-3 real-looking inserts, 0-2 red caption words.
- Last shot: callback to the opening framing, or `look.end: fade_black`.

## 3. Cast and asset list
Design `cast` once for the whole video (see house-style `character-design.md`): unique body colours from the
palette, every role readable from a detailed costume - a head piece (hair, hat, helmet, beard) for everyone and an
outfit for the main cast (uniform, apron, life vest, lab coat) - glow for one team or the "special" characters,
extras for crowds. A costume change mid-story is two pieces with `from`/`to`.
While planning, write `plan/asset_list.json` (format in the make-assets skill): every background, prop, icon,
costume piece, creature (+ its sound) and video the spec references, with a `describe` (for Kie.ai) and a `search` / `library` choice
(for free mode). Then run the make-assets skill (it fills the cast accessories with exact placements), run
`python cast_sheet.py P` and LOOK at `qc/cast_sheet.png` (pieces sitting on the head and body? colours
distinct? faces readable?). Show it to the user.

## 4. Check, compile, preview
1. `python validate_spec.py P` - fix every FAIL; treat WARNs as design notes (frozen actor, head leaving the
   frame, slow shots...) - except "said but not shown": fix every one.
   Then `python coverage.py P --visible --sheet` - renders each named object at its word with and without it and
   lists anything MISSING or NOT VISIBLE (off camera, behind a head, under another character). Fix until it reports
   0: move the holder beside the person, put the prop in front (`hold.front`, actor `z`), widen the camera. Use
   `"covers": ["word"]` on the element that shows a word another way.
   **Critical detail review** - LOOK at every tile of `qc/detail_sheet.jpg` (each named thing and each held prop)
   and be picky; the user notices every one of these:
   - Held props are held by the handle/grip with the working end out (brush bristles, knife blade, gun muzzle,
     spoon bowl away from the hand), the right way up, at a believable size (a makeup brush about a head long, a
     cup smaller than a head). New held props: `python props.py grip <image>` then LOOK at `<image>.grip.png`
     (green = hand, red = tip); `--flip` if the ends are swapped, `--style upright` for cups/bottles/phones/books.
   - A tool used ON someone touches them: actions done to a person take `"to": "<cast>", "at": "cheek|face|head|
     mouth|chest|arm|hand"` (brush, scrub, touch, inject, feed...) so the arm reaches and the tip lands there.
   - Characters face whoever they talk to or act on; their eyes look at it (`gaze`, `gaze_y`).
   - Feet on the floor (nobody floating or sinking), nobody slides (legs step), nothing passes through a body or
     a prop that should be in front/behind; objects on the ground have a contact shadow.
   - The named person/object is in frame on its word (give a named character a key on that word so the camera
     goes to them); captions never cover a face or the key object.
   - Continuity: same costume, colour and props from shot to shot unless the story changes them; one colour per
     character (head = body = limbs); left/right positions consistent across a cut.
   - Arms start at the shoulders, coming out from under the garment's shoulder (armholes) - never on the chest.
   - Vehicles: render FULL-SIZE stills of every vehicle shot (`ra_preview.py P --stills t1,t2 --scale 1`) and LOOK:
     riders sit on the cushion, legs visible on the seat, nothing below the floor, no body behind the vehicle, no
     limb poking through a door. Send the close-ups to the user before the full animatic.
   - Animals: a 10 fps strip of every moving animal - one animal per frame, legs changing, never sliding.
   - Camera: hand-made keys stay inside the picture (compile_spec clamps them) - no black band at an edge.
   - Nothing obviously wrong: duplicated or synchronised gestures, a prop popping in after the word, a character
     cut in half by the frame edge at a key moment, B&W/tint on the wrong shot.
2. `python compile_spec.py P` - plans the auto cameras, expands actions, adds the automatic SFX, writes
   `plan/spec_compiled.json`.
3. `python ra_preview.py P --sheet` and LOOK at `qc/preview_sheet.jpg` (a frame every 0.5 s): compare against
   `house-style/references/look/*.jpg`. Then `python ra_preview.py P` for the half-res animatic with sound
   (`exports/preview.mp4`; it mixes voice + every SFX cue into audio/mix.wav first, so the user hears the immersive
   layer - never send a voice-only animatic); view 10 fps strips around pops, entrances and transitions.
4. Show the animatic (or the sheet) to the user; iterate until approved. Only then build in After Effects.

## Editing the plan later
Small changes go straight into `plan/spec.json` (times, poses, positions, icons), then compile + preview the
affected range (`ra_preview.py P --from 12 --to 18`). Re-run `auto_plan.py` only with `-o plan/spec_new.json`
(it refuses to overwrite a filled plan).
