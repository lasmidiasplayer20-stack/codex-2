---
name: house-style
description: The complete look-and-feel bible for glow stick-figure story Shorts, measured from the reference videos - characters, backgrounds, props and icons, camera, cut rhythm, transitions, captions, colour, sound and script voice. Load it whenever designing, planning, judging or fixing any part of such a video ("make it look like the samples", "is this on style", "what would the samples do here", "check the editing"), and before writing a shot plan.
---

# House style - glow stick-figure story Shorts

The plugin no longer has the seven reference videos, so this skill *is* the reference. Read this page fully before
planning; open the references for numbers and examples, and look at the image boards in `references/look/`
(they are real frames from the references) whenever judging a frame.

## The look in one paragraph
Vertical 9:16 Shorts, about 55 s, 30 fps. Flat-coloured rubber-hose stick people - a big round head floating just above a sturdy
bean-shaped body (a small gap, no neck), chunky tube limbs with round ends, no hands or feet, front-on faces (two solid black tall ovals looking where the character
looks, lid cuts and brows for emotion, a small black mouth), dressed in detailed illustrated costume pieces (messy
hair, knitted beanies, bushy beards, army helmets, uniforms), a thin outline in a darker shade of the body colour
and soft clay shading (each part rolls off to a darker edge - no emboss), some with a coloured glow - act out a true or legendary story on top of
detailed, moody, empty AI/photo backgrounds that are darker and softer than the characters. Detailed 3D-emoji
props and icons pop in on the exact word that names them. A fat yellow one-word caption pops in the lower third
for every spoken word. The camera never rests: every 0.45-1.25 s it jolts - a fast eased snap in on the face or
group that acts, or out on the scene - then drifts until the next word or event. A fast, energetic male narrator tells it in one breath over a steady, curious music bed with
pops, whooshes and hits. Black-and-white moments mark death, flashbacks and bad outcomes; one to three real or
real-looking clips add scale; the ending loops back to the opening image or fades to black.

## Non-negotiables (check every shot)
1. **Something changes on every key word.** Cut, punch-in, pose change, prop/icon pop, expression change. Median
   shot 1.3 s; nothing static longer than ~2 s.
2. **Show what the narration names, on the word.** "a secret military document" -> a paper in a hand at
   "document"; "chickens" -> real chickens pecking around the farmer, clucking. Literal, instantly readable. The
   characters act reactions and emotions themselves; icons are rare and only for abstract concepts ("rat poison"
   -> rat + skull pop at "rat" because the poison is the idea, not a living rat).
3. **Characters are big and acting.** Leads fill 45-110% of the frame height (often cropped at the knees or
   waist); poses change on verbs; faces change on emotions; walkers walk, talkers talk.
4. **Camera always moving** - jolts in and out on words and events, aimed at faces, tracking walkers, framing
   groups together, shake on impacts (`"camera": "auto"` does this). See `references/editing-grammar.md`.
5. **Backgrounds are real places, empty, moody, eye-level, darker than the cast** (desaturate, darken, slight
   blur, strong vignette). Never a flat colour unless it is a deliberate abstract (inside the body, a void).
6. **Captions:** one word (sometimes two short ones), yellow, dark stroke, hard drop shadow, soft yellow glow,
   pop scale, ~76% down the frame, 0-2 red words per video.
7. **Every character has its own body colour** from the palette and a detailed costume (illustrated hair, beard,
   helmet, hat, uniform, apron, vest pieces fitted to the rig) so roles read instantly and the frame looks rich.
   Flat vector costume parts are for extras only. **One colour per character**: head, body, arms and legs share it -
   no sleeve/trouser/shoe colours, no head-colour flushes; torso garments are sleeveless pieces.
8. **Sound never stops and is immersive:** voice from frame 1, an ambience bed under every location (crowd, a soft
   daytime breeze - never night insects by day -, traffic), a real sound on every on-screen action (the starting pistol on "began", engines,
   footsteps, bites, gulps, coughs, barks, cheers, boos), music underneath, a pop on every pop-in, whooshes only on
   big transitions, hits on impacts. The animatic is always heard with this layer (ra_preview mixes it).
9. **Real things behave like real things:** people in a vehicle sit on its seat inside it (seat layer behind them,
   doors in front, thighs on the cushion); animals that move run their gait cycle (legs in sequence, never a sliding
   still); props have their real size next to the characters (a well about as tall as a person, a mile post at hip
   height, a car about twice a person's length).

## References
- `references/visual-style.md` - backgrounds, colour, lighting, props, icons, FX, grades, live inserts, endings.
- `references/character-design.md` - anatomy, proportions, faces, costumes, palette, acting, crowds, states.
- `references/editing-grammar.md` - measured rhythm, camera maths, cut placement, transitions, patterns.
- `references/captions.md` - exact caption spec and timing rules.
- `references/sound-style.md` - narration, music, SFX and loudness targets.
- `references/sample-breakdowns.md` - shot-by-shot breakdowns of all seven references (what was on screen when).
- `references/look/*.jpg` - frames from the references: `frames_board`, `characters_board`, `icons_board`,
  `transitions_board`, `captions_board`. Look at them before approving a cast sheet or stills.
- Numbers used by the tools live in the kit: `kit/data/style.json` (targets), `rig.json`, `poses.json`,
  `parts.json`, `faces.json`.
