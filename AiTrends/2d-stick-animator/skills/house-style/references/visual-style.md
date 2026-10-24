# Visual style

Measured on seven references (720x1280 originals; all numbers converted to the 1080x1920 build size).

## Format
- 9:16, build at 1080x1920, 30 fps CFR, 48-62 s (target ~55 s). No intro, no title card, no end card, no logo,
  no subscribe prompt. The first frame is already the story (mid-action, protagonist big, camera snapping out).

## Backgrounds
- **What:** real-looking locations generated or sourced per beat: alley with cardboard box, tiled bathroom,
  photo studio under stairs, pier with skyline, stormy sea, beach, palace hall, stone prison basement, long cell
  corridor, aeroplane cabin and cockpit, onion field, foggy forest river, underwater, asylum ward, jungle clearing
  with huts and campfire, inside a blood vessel, penthouse, rooftop terrace, office street, traffic.
- **How they look:** eye-level camera at standing height, the floor visible in the lower third (that is where the
  feet stand), detail and depth in the upper two thirds, no people, no readable text. Photoreal or painterly AI
  imagery (one reference used a clean illustrated street). Mood > accuracy.
- **Grade:** darker and less saturated than the characters (mean brightness of the frames 70-140 of 255; the
  characters are the brightest, most saturated things on screen). Slight depth-of-field blur (2-6 px) so the cast
  pops. Strong vignette: corners at 57-80% of the centre brightness (`look.vignette` 0.35-0.5). A warm or cold
  cast per location is fine (sepia asylum, teal underwater, red bloodstream, grey B&W streets).
- **Rhythm of locations:** a new location every 2-4 shots, but locations come back with new framings and new
  actions (the cell, the door, the corridor rotate in the basement story). Close/medium framings dominate.
- **Abstract spaces** are allowed when the story goes somewhere no camera can: inside the body (red macro of
  blood cells), a dark void with a single icon, a white flash frame.
- **Build size:** generate at 1296x2304 (1.2x) or larger so zooms of 1.3-1.4x stay sharp; `bg.scale` 1.06 default.

## Props
- Detailed, shaded, slightly cartoon-realistic objects (3D-render or illustration look, not flat vector): bucket,
  medication cart, money bundles, briefcase, wooden crate, document, ID card, camera on tripod, rifles, fire
  extinguisher, ambulance, aeroplane, car, hot-dog stand, spear, chunk of meat, rope, stones, shoes, knife.
- Scale: true to the characters or a little bigger so they read on a phone - never toy-sized (user feedback v2.3:
  a well half a person tall looked "terrible"). Measure against the character's height h: a well ~0.85 h, a door
  ~1.15 h, a mile post or a chair ~0.5 h, a car ~2 h long, a table ~0.45 h high, a bottle ~0.15 h. Stand objects on
  the ground: the prop's visible bottom on the floor line (props are placed by their centre - account for the
  transparent margin). Held props sit in the hand (the rounded end of the arm) and follow it.
- Entrances: they **pop** on the naming word (scale 0 -> 116% -> 96% -> 100% over 9 frames) or slide/fall in;
  repeated props pop one after another for escalation ("even stronger medication" -> 3 carts pop in a row).

## Living creatures
- Animals in the scene are alive: the whole animal in side view, drawn in the same style as the costume pieces
  (detailed 2D cartoon, thin dark outline, cel shading), standing on the ground at a true size next to the
  characters, moving all the time (pecking, wandering, hopping, flying, swimming, fleeing, sleeping) and heard
  (clucking, barking, mooing). Never a head emoji for an animal that is there in the story.
- **Real gait, not a doll** (user feedback v2.3): an animal that walks, runs, hops or flies on screen runs its gait
  cycle - 4 frames of the same animal with the legs (or wings) in sequence, flipped at 9-12 fps while it travels
  (`creatures.py gait`, compile_spec does the flipping). A still picture that only slides and bounces is not
  acceptable for a moving animal.

## Vehicles with people in them
- Cars, carts, carriages, wagons, boats: the picture is split into a seat layer (the upholstery, behind the riders)
  and a body layer (doors, panels, wheels, steering wheel, in front of them) by vehicles.py; riders sit on the
  cushion - thighs along it, knees bent, shins behind the door - and travel with the vehicle. Generate the vehicle
  exactly side-on with its seats and cushions clearly visible and empty.

## Icons (3D emoji) - sparingly
- The samples use about 5-8 icon moments a minute. Characters act emotions and reactions (faces, poses), animals
  are creatures, objects are props; an icon is for a concept that cannot be acted or held.
- Glossy 3D-emoji icons (Fluent-emoji look; the kit ships 373 of them) for concepts: skull (death/poison), rat,
  document/scroll, calendar ("in a few days"), crown (leader/king), warning triangle (danger/problem), virus/
  microbe, droplet, fire, money, clock, ID card, swap arrows (a switch), crossed rifles (attack).
- Size ~160-300 px (15-28% of the frame width), placed in the top third next to the head they belong to, gently
  floating, popping in on the word and out after ~1 s or at the cut.
- **Thought bubble** (white cloud + two dots towards the head) containing an icon = a plan, an idea, a belief.
  **Speech bubble** containing an icon = an order, a statement, a report.
- **Clock badge** (dark metal dial ring + ticks + big red bold text such as "3D", "30D") = a duration. The same
  badge with a red prohibited sign over an icon = "without water / without food".
- Red prohibited sign over any icon = "no / without / never".

## FX
- Real fire, smoke and explosion elements screen-blended over the scene (aircraft fire, field crash, campfire).
- Embers/sparks/dust particles in fire or tense scenes; money rain with bills fluttering and piling on the ground.
- Colour washes: green for a smell or sickness, red for blood/danger/anger, blue for cold.
- Pixel/block glitch for digital or microscopic multiplication ("the virus multiplied"), 0.2-0.3 s.
- Camera shake on impacts, crashes, explosions (0.3-0.6 s).

## Grades and states (story signals)
- **B&W moment:** the whole shot desaturates over ~0.3 s for death, poison, "no one", flashbacks and bad
  outcomes; captions stay yellow. 1-4 per video, 1-3 s each.
- **Grey characters:** characters that are dead, remembered or irrelevant turn grey while others stay in colour.
- **Silhouette:** a character goes solid black for "he didn't know", "an unknown sickness", "passed out".
- **Red tint on a character** for a wound, a scratch, blood, rage; **sick green** for illness.
- **Ghost** (half transparent) for someone imagined or gone.

## Live-action / real-looking inserts
- 0-3 per video, 1-2.5 s each, often B&W or desaturated: archival war footage, a woman running through a prison
  corridor, prisoners being paid, a falling aeroplane, an aerial traffic jam, an angry man on the phone. They give
  scale or reality to one line, then the cartoon resumes. Source public-domain/stock first, generate second.

## Composition
- Leads large: standing height 45-110% of the frame height, feet often below the frame edge, head in the upper
  third. Two-shots: characters face each other, overlap is fine. Crowds: 4-12 smaller figures, 25-45%.
- Keep the lower 18-28% (caption band) free of faces and icons; bodies/legs may pass behind the caption.
- Faces never cut by the top edge unless it is a deliberate extreme close-up (eyes and brows must stay in).

## Endings
- 3 of 7 loop back to the opening image (same location and character, same framing) so the Short replays
  seamlessly; 2 fade to black on the last word; 2 end on the punchline image.
