# Asset prompts and sources

`gen_image.py` wraps the subject in these templates automatically (see TEMPLATES there). Write the SUBJECT well:
place + era + materials + light + mood; never people; give the floor.

## Backgrounds (kind: background)
Subject recipe: `<place>, <era/region>, <key objects that the story needs>, <time of day / light>, <mood>`.
- "a narrow European cobblestone street in the 1910s, wet stones, gas lamps, foggy grey morning, gloomy"
- "a medieval stone prison basement cell with a wooden bench and iron bars, a single dim lamp, damp walls"
- "the interior of a 1980s passenger aeroplane cabin by the lavatory door, beige panels, warm light"
- "a foggy forest river bank with bare trees and a wooden post by the water, cold grey dawn"
- "the inside of a human blood vessel, red blood cells floating, macro, soft red glow" (abstract)
- "a rooftop terrace of an office tower with a glass railing, city haze at sunset"
Styles (`"style"` in asset_list.json): photo (default, most references), painterly (war/forest), illustrated (clean
streets), 3d (cabin/stylised interiors). Keep one style per video.
Reject: people in frame, text/signs, fisheye/top-down views, no visible floor, oversaturated colours.
Wide/tall locations (`world` in asset_list): describe the length or height ("a long row of facades", "a whole beach
from the dunes to the pier", "a tall stone stairwell seen from the side"); the tool asks for a panoramic or tall
composition with one continuous ground line, at 4K.

## Props (kind: prop) - detailed 3D-illustration look
"a black leather briefcase overflowing with bundles of US dollar bills", "a stainless steel hospital medication
cart full of pill bottles", "a wooden shipping crate", "an orange life jacket", "a 1940s military rifle",
"a red fire extinguisher", "a white ambulance van, side view", "a hot-dog cart with a striped umbrella".
Side or three-quarter views; one object per image.

## Costumes (kind: costume) - drawn on our own character
`costume.py` sends GPT Image 2.5 a template of OUR head (head piece) or front-view body (torso piece) in flat
magenta and asks for the piece drawn on it with a transparent background; the magenta is keyed out and the head
circle fitted, so the piece lands on the rig exactly. The `describe` text is the piece only - material, colour,
shape, wear - never the person:
- head: "short messy dark-brown hair with loose strands over the forehead", "worn beige knitted beanie pulled low
  and a bushy dark-brown beard and moustache", "olive-green WWII army helmet with a chin strap and scuffs",
  "navy police cap with a gold badge", "long wavy auburn hair falling past the shoulders", "white chef's hat",
  "grey hair bald on top with a neat grey moustache", "black pointed witch hat with a cream band".
- torso (always SLEEVELESS - the rig's arms move on their own; costume.py strips sleeve words and adds the
  instruction): "blue cotton apron with white straps", "orange life vest with reflective strips and buckles", "the
  body of an olive army jacket with a row of colourful medals and a gold rank badge", "the body of a white doctor's
  lab coat over a blue shirt", "black-and-white striped prison vest", "the body of a grey hoodie with a front
  pocket". Never "long-sleeved", "puffed sleeves", "sleeves rolled up".
- face: "round thin gold glasses", "black sunglasses", "black eye patch".
Keep head pieces to hair + headwear + facial hair; never ask for eyes, mouth or skin (the engine draws the face).
Size words help: "small", "snug", "close-fitting", "short rim", "no chin strap" - in the reference style hats and helmets
are only slightly wider than the head and sit on its top third, beards stay within the face. costume.py prints a
`check` warning when a head piece comes out oversized; regenerate it.
Library equivalents for free mode: `python costume.py library` (54 pieces: 13 hair styles, 4 beards/moustaches,
23 hats, 3 face pieces, 11 torso outfits).

## Icons (kind: icon)
Use the kit first (Fluent 3D emoji). Generate only story-specific symbols ("a 3D emoji-style ID card with a photo",
"a 3D emoji-style chimpanzee head").

## FX plates (kind: fx) and real inserts
Stills: "a large orange fireball explosion", "thick grey smoke cloud", "sparks and embers" on pure black.
Video: search Pixabay/Pexels "fire on black background", "smoke black background", "explosion overlay".
Live inserts (search first): archive.org newsreels ("world war ii beach landing", "1950s traffic"), Pexels/
Pixabay ("aerial traffic jam", "angry man phone", "prison corridor"). Generate (gen_video.py) only when missing:
"Black and white 1940s newsreel footage, soldiers in a muddy trench raise binoculars, handheld, film grain, 9:16".

## Licences
| source | licence | credit |
|---|---|---|
| Fluent UI Emoji 3D (kit icons) | MIT | optional (keep LICENSE.txt in the kit) |
| Pexels / Pixabay | free licences | not required |
| Wikimedia Commons / Openverse | per file (CC0, PD, CC BY, CC BY-SA, NC...) | required for BY/BY-SA; avoid NC/ND for monetised videos |
| Internet Archive | often public domain - check each item | courtesy credit |
| Generated (Kie.ai / OpenAI) | per the provider's terms | not required |

## Creatures (animals in the scene)
Template (gen_image.py kind "creature"): the whole animal from head to tail and feet, exactly side-on facing right,
standing on its feet, "detailed 2D cartoon illustration like a modern animated YouTube Short - clean thin dark
outline, cel shading with soft highlights, fine fur / feather / skin texture lines, rich but natural colours (the
same style as the characters' hats, hair and clothes). Not 3D, not glossy, not an emoji, not a photo", transparent
background, no ground or shadow. Describe the breed and colours the story needs ("a scrawny grey street dog with a
torn ear", "a plump brown farm hen with a red comb", "a black-and-white dairy cow"); for flying or swimming animals
say so ("a pigeon flying with wings spread", "a silver fish swimming"). One picture per kind of animal.
**Gait cycle** for every animal that moves on screen (`"gait": "run|walk|hop|fly|two_legs"` in the asset list, or
`creatures.py gait <image> --kind run --yes`): 4 image-to-image frames of the same animal (extended / landing /
gathered / push-off for a run; diagonal leg pairs for a walk; wings up / level / down for a flap), ~6 credits each.
LOOK at them side by side: the same animal, colours and size, legs in sequence.

## Vehicles people ride in
Generate exactly side-on, facing right, with its seats and cushions clearly visible and EMPTY, the upholstery in
one strong colour that appears nowhere else on the vehicle ("a 1904 open-top automobile seen exactly from the side
facing right, high wooden-spoke wheels, brass lamps, glossy black body with red leather bench seats in front and
behind, no roof, empty seats, no people"). Then `vehicles.py layers <image>` and LOOK at `<name>_layers.png`: red =
the seats that go behind the riders; the doors, body, wheels and steering wheel stay in front; one cross per seat.

## Sounds
ElevenLabs sound effects (`eleven.py sfx "<describe>" --dur 4`): name the source, the number and the mood -
"several hens clucking calmly in a farmyard", "a big dog barking twice, aggressive", "a single cow mooing far away".
The immersive layer of every video (house-style sound-style.md) needs, per project: one ambience bed per kind of
location (8-10 s, looped/trimmed by the cues: "a large outdoor stadium crowd murmuring, 1900s", "a gentle daytime breeze
over open farmland, no insects, no crickets" - insects and crickets read as night) and one effect per kind of on-screen action ("a single loud starter pistol shot fired into
the air at a stadium, short echo", "an antique car engine chugging past", "an antique car backfiring and dying",
"runners' footsteps on a dirt road with panting", "a crunchy apple bite and chewing", "a man gulping a drink",
"a man coughing on dust", "a stadium crowd cheering", "an angry crowd booing"). ~12-16 effects for a 60 s Short.
Free: `fetch_assets.py sound "<animal> <sound>"` searches Wikimedia Commons recordings (check the licence column).
