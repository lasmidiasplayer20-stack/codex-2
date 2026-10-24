---
name: make-assets
description: Source and generate every picture, clip and sound a glow stick-figure Short needs - detailed costume pieces that sit exactly on the rigged characters (hair, beards, hats, helmets, glasses, uniforms, aprons), living animals in the same drawn style (whole body, side view) with their gait cycles and sounds, vehicles split into seat and door layers for riders, sleeveless torso pieces, empty moody 9:16 backgrounds, detailed props, 3D-emoji icons, fire/smoke FX plates and real-looking live inserts - either with Kie.ai (GPT Image 2.5 with a transparent background, Nano Banana Pro) or from free sources only (bundled costume library and Fluent 3D emoji, Openverse, Wikimedia Commons, Pexels, Pixabay, Internet Archive), as the user chooses, with a licence manifest. Use when the user says "make the backgrounds", "generate the props", "make the characters' hair/hats/clothes", "find footage", "get icons", "use free sources only", "use Kie", or when the make-story-short pipeline reaches the asset stage.
---

# Make the assets

The characters' bodies, faces and limbs are drawn by the engine (After Effects or the preview renderer). Everything
that makes them look detailed - hair, beards, hats, helmets, glasses, uniforms, aprons, life vests - and every
background, prop and icon is an image file made or found here. Tools are in `<workspace>/_kit/py/`. Prompt wording
and licences: `references/asset-prompts.md`. Look standards: house-style `visual-style.md` and `character-design.md`.

## 0. Asset mode (ask once per project, before anything is fetched)
Ask the user with AskUserQuestion: **Kie.ai (best detail, costs credits)** or **free sources only (no paid
service)**. Record it: `python assets.py mode P kie` or `python assets.py mode P free`. Never spend credits in a
free project. In kie mode, check the key first (`python keys.py check`; if Kie.ai has none, ask the user for their own
key and store it with `python keys.py set kie <key>` - never write a key into a project file or the plugin).

| | kie | free |
|---|---|---|
| costume pieces | GPT Image 2.5 drawn on our rig template (`costume.py`), ~6 credits each | bundled costume library (54 pieces), recoloured with `tint` |
| backgrounds | Nano Banana Pro 9:16 2K | Pexels (key) + Openverse + Commons photos, cropped to 9:16 |
| props | GPT Image 2.5, real transparent background | Fluent 3D emoji, else Openverse/Commons PNG cut out |
| icons | Fluent 3D emoji first, generated only if none fits | Fluent 3D emoji |
| creatures (animals) | GPT Image 2.5 in the costume style (2D cartoon, thin outline, cel shading), whole body, side view facing right, ~6 credits each; + a 4-frame gait cycle (~24 credits) for every animal that moves on screen | not available as free pictures in this style yet: ask the user to allow Kie.ai for the animals |
| vehicles with riders | GPT Image 2.5 side view with empty, clearly visible seats; `vehicles.py layers` splits seats (behind) and doors (in front) | an Openverse/Commons side-view cut-out, then `vehicles.py layers` |
| sounds (animal sounds, ambiences) | ElevenLabs sound effects with the user's key (`eleven.py sfx`), Commons as fallback | Wikimedia Commons recordings (`fetch_assets.py sound`), licence logged |
| video inserts | Pexels/Pixabay/archive.org (search), `gen_video.py` only if asked | Pexels/Pixabay (keys) or archive.org |

## 1. Write the list - `plan/asset_list.json`
Start from the shot list's MUST SHOW column: every named object needs a file (prop, icon or costume piece) and every
action its tool (makeup brush, shovel, phone, pistol, sponge...). Missing one means the story beat is not shown.
One entry per file the spec references (plan-shots writes paths into the spec; use the same `out` paths):
```json
{"items": [
 {"id": "bg_street", "kind": "background", "describe": "dark old European street at dusk, wet cobbles, closed wooden doors, gloomy", "search": "old street night door", "out": "assets/bg/street.jpg"},
 {"id": "bg_street_wide", "kind": "background", "world": [3200, 1920], "describe": "a long dark old city street at dusk, a row of stone facades, wide pavement along the whole width", "search": "long old street panorama", "out": "assets/bg/street_wide.jpg"},
 {"id": "box", "kind": "prop", "describe": "large open cardboard box seen from the front, flaps open, inside visible", "search": "cardboard box", "out": "assets/props/box.png"},
 {"id": "rat", "kind": "icon", "emoji": "rat", "out": "assets/icons/rat.png"},
 {"id": "hobo_head", "kind": "costume", "cast": "hobo", "piece": "head", "to": 7.02,
  "describe": "worn beige knitted beanie pulled low and a bushy dark-brown beard and moustache",
  "library": ["hat_beanie_worn", "beard_full_brown"], "tint": {"beard_full_brown": "#5A3A22"}, "out": "assets/cast/hobo_head.png"},
 {"id": "sol_helmet", "kind": "costume", "cast": "sol1", "piece": "head", "describe": "olive-green WWII army helmet with a chin strap",
  "library": ["hat_army_helmet"], "out": "assets/cast/sol1_helmet.png"},
 {"id": "war", "kind": "video", "search": "world war two soldiers marching", "out": "assets/video/war.mp4"}]}
```
- `describe` is the generation prompt (kie); `search` the free-source query; write both so either mode works.
- Creatures: `{"id": "hen", "kind": "creature", "animal": "chicken", "describe": "a plump brown farm hen with a red
  comb", "out": "assets/creatures/hen.png"}` - one picture per kind of animal (a flock re-uses it), described with
  its colours and breed for the story; a flying bird or a swimming fish says so ("flying with wings spread").
  The picture is drawn in the same style as the clothing pieces, trimmed to its feet line and its facing is recorded
  (`<image>.creature.json`). Never use an emoji or a head icon for an animal that is in the scene.
  An animal that moves on screen also gets `"gait": "run|walk|hop|fly|two_legs"`: assets.py generates its gait
  cycle (4 frames of the same animal, image-to-image) and records it in the sidecar; compile_spec flips the frames
  while it travels. A sliding still reads as a doll (user feedback v2.3).
- Vehicles people ride in: one `prop` entry (exactly side-on, seats empty and visible, upholstery in one strong
  colour); after it exists run `python vehicles.py layers P/assets/props/<name>.png` and LOOK at `<name>_layers.png`
  (the shot's `vehicles` entry uses it - plan-shots).
- Sounds: `{"id": "hens_sfx", "kind": "sound", "describe": "several hens clucking calmly in a farmyard", "search":
  "chickens clucking", "dur": 4, "out": "audio/sfx/hens.wav"}` - one per creature that makes a sound; the creature's
  `sound` in the spec points to it.
- `world` on a background = the shot's `bg.world`: the picture is made at that size (wide panorama 16:9/21:9 at 4K
  from Kie, landscape photos in free mode) so travelling characters and camera pans have a real place to cross.
- Costumes: `piece` is `head` (hair, beard, hat, helmet, glasses - all one picture), `torso` (shirt, uniform,
  apron, vest, dress, jacket with medals - always SLEEVELESS: describe only the garment body; costume.py strips
  sleeve words and adds the sleeveless instruction) or `face` (glasses, sunglasses, eye patch, mask only). No
  sleeve/trouser/shoe colours on the cast: one colour per character. `library` names the
  free-mode pieces (`python costume.py library [--tags hat,army]` lists them); `tint` recolours one;
  `from`/`to` (seconds) give a costume window - a character who changes clothes gets two entries.
- Every character gets at least one head piece (hair or a hat) and the main cast a torso piece - bare heads look
  unfinished next to the samples. Extras in a crowd share a piece (one helmet for the whole army).

## 2. Fulfil it
- `python assets.py check P` - what exists / is missing.
- kie mode: `python assets.py get P` (without `--yes`) lists the paid images and the rough credit cost (about 6 per
  GPT image, ~20 per background, ~24 for a 4K wide/tall world background); tell the user, get a yes, then `python assets.py get P --yes`.
  Free mode: `python assets.py get P`.
- Re-do single items with `--only id1,id2 --force`. Jobs run in parallel (`--workers 6`).
- Finished costume pieces are added to `spec.cast.<id>.accessories` with their measured placement
  (`w`, `dx`, `dy` in head diameters for head pieces, torso lengths for torso pieces; `over_face` + `follow_gaze`
  for glasses), so they sit on the rig to the pixel. Do not hand-place generated pieces.
- Single pieces outside the list: `python costume.py head "<describe>" -o P/assets/cast/x.png` (or `torso`,
  `face`), then add it with `--spec`; library piece: `python costume.py use P --cast hobo --piece hair_messy_brown
  --tint "#3A2A1A"`. A piece drawn elsewhere on our template: `costume.py templates -o DIR`, then `costume.py fit`.
- Other sources by hand: `fetch_assets.py archive|pexels|pixabay|commons|openverse "<query>" -o P/assets/video`,
  `fetch_assets.py emoji "<Unicode name>"`, `cutout.py in.png -o out.png [--outline 3]`.
- Live inserts that exist nowhere (kie mode, ask first): `gen_video.py "<STYLE, SCENE, CAMERA, MOTION>" -o ...`.
- Fire, smoke, explosions: real elements on black (Pixabay/Pexels video or a generated still), screen-blended.

## 3. Check every file (look, do not assume)
- Torso pieces side by side first: any sleeve drawn on a torso piece is a failure - regenerate it (`--only id --force`).
- `python cast_sheet.py P` and LOOK: one colour per character (head = body = arms = legs); arms come out of the shoulders under the garment (armholes), never from the chest; each costume sits on the head/body (hat edge above the eyes, beard under the
  mouth, no piece covering the eyes except glasses), pieces stay compact (an oversized hat or beard makes the head
  look bigger than the body - regenerate anything `costume.py` flags with `check`), the gap under the head stays empty, the outline matches, no white halo or leftover magenta, no
  stray neck lines or fake checkerboard. Regenerate a failure with a sharper `describe` (`--only id --force`);
  the raw image is kept as `*_raw.png` for `costume.py fit` retries.
- Backgrounds at phone size: empty of people, eye-level, floor in the lower third, no text, darker and less
  saturated than the cast. Props: one object, clean transparent edge, seen from the side or front.
- Creatures: put each one in a shot and LOOK at a frame (`python creatures.py strip P --shot S03`): whole animal, side
  view, the same drawn style as the costumes, standing on the ground (not floating), facing the way it moves, sized
  right next to the characters. Regenerate anything off-style with a sharper `describe`.
- Props that will be held: `python props.py grip <image>` and LOOK at `<image>.grip.png` - green dot on the
  handle, red on the working end (bristles, blade, muzzle, bowl); fix with `--flip` / `--style upright`.
- Free photos: check every result - search hits are often wrong; change `search` and re-run that id.
- `assets/manifest.csv` logs source and licence for every file; put required credits (CC BY) in the video
  description, never on screen. Avoid NonCommercial/NoDerivs material for monetised channels.
