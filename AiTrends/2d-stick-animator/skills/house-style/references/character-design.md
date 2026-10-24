# Character design

The engine draws every character from the rig (`kit/data/rig.json`), so proportions are fixed; the creative work
is colour, costume, accessories, poses and faces.

## Anatomy (measured from the reference videos; rig units, head top to feet = 1000)
- Head: a circle 240 across (24% of the height) that FLOATS above the body: a clear gap of about 1/8 of the head
  width (30 units) between the bottom of the head and the top of the body - no neck. A thin darker contour on its
  outer edge.
- Torso: one thick rounded tube about 0.63 head widths wide (152), from the top at 73% of the height down to where
  the legs split at about 39%; tilts with `lean`. Wider and shorter than a "realistic" torso - a sturdy bean.
- Arms: tubes 62 wide (a little thinner than the legs) from the top corners of the torso - the joint sits right at
  the top line of the body (or just under a jacket's or uniform's shoulder line, measured per character), never
  lower on the chest and never in the middle of it - upper 140 + lower 131, smooth rubber-hose bend; hanging, the
  hands reach the hips. Hands go where a real hand would be: a hand at the chin or ear reaches the head's edge, a
  pointing or waving arm clears the big head (raised arms make a V, never hug the skull), lying figures keep their
  arms along the body (an arm off the body's axis reads as lifted into the air).
- Legs: tubes 70 wide from two points either side of the hip, 215 + 215; the round ends are the feet.
- Costume pieces hug this body: hats and helmets only slightly wider than the head (brimmed hats more), beards no
  wider than the face, outfits fitted to the torso shape and leaving the head gap empty.
- No hands, no feet, no fingers, no neck, no nose, no ears.
- Finish: a thin outline in a darker shade of the body colour (body x 0.42 - brown on yellow, navy on blue; not
  black), ~3 px at 1080 wide for a full-height character, scaling with the figure. Soft clay shading, NOT an emboss:
  every body part (each arm, leg, the torso and the skull) is a flat body-colour core that rolls off softly to a
  darker edge (about 0.75 of the body colour at the very edge, flat again ~15% of the part's width inside), so an
  arm crossing the body reads by its soft darker rim. No highlight ridge, no bevel, no lighting direction.
  Optional coloured glow (the cyan soldiers glow strongly, the hobo faintly); soft contact shadow at the feet.
- Front and three-quarter views (`turn` 1 front - 0 three-quarter, facing the `face` side). Front: the body and
  costume face the camera, both arms beside the body from the shoulder corners (the far arm in front when it stays
  on its own side, or with `fFront` 1 for crossed arms). Three-quarter: the body and its costume turn a little
  towards the facing side - about 20% narrower, shifted ~9 units that way, the shoulders closer together - and
  the arms gain depth: the camera-side arm (`aF`, from the back shoulder) is in front of the chest and can reach
  across it to the chin, a cup or a phone; the other arm (`aN`) comes from behind the chest's front edge, so a
  forearm reaching forward pokes out in front of the body. Standing, talking and reacting poses are front views;
  acting on something (walking, running, pointing, holding, eating, drinking, fighting, clapping, praying,
  thinking, phoning, reading, sitting, lying) is three-quarter. The head is always a front-on face that looks
  towards the facing side.

## Faces (`kit/data/faces.json`) - measured from the samples
- Eyes: two solid black tall ovals high on the face (x +-0.125, y -0.085 of the head, 0.095 x 0.205), shifted
  towards where the character looks (`gaze` 0.11 by default, 0.17 max; `gaze_y` + down / - up), no whites, no
  pupils. Expressions come from lid cuts in the skin colour and brows, not from changing the eye shapes.
  Codes: normal, determined (flat lid cut - the default focused look), angry (inner brows down), sad, worried,
  wide (bigger, raised brows - shock/realisation), happy and joy (arcs), calm (half lids), sleepy, suspicious
  (one lid lower), closed (blink/sleep/faint), dead (X X).
- Mouths are filled black shapes under the eyes, small and simple: none (most of the time), o (talking,
  surprise), open, scream, teeth, smile, grin, smirk, frown, flat. The mouth follows the gaze a little.
- Face drawing order: skull -> hair/hats/beards -> eyes and mouth (on top, so a bushy beard never hides the mouth)
  -> glasses. Hat brims and fringes must stay above the eye line (y < -0.2 of the head).
- **No head-colour changes** (house rule, user feedback v2.3): the head is always the body colour. A green, purple,
  red or grey head on a cyan body reads as a broken character, not as "sick" or "angry". Act the state with the eyes,
  mouth and pose (sick = sleepy/worried eyes, frown, `hug_self`/`slump`; angry = angry eyes, `teeth`/`scream`,
  `shake_fist`; poisoned = wide eyes, open mouth, `shiver`, a skull icon). `face_color` is dropped by compile_spec.
- Talking flaps the mouth (o/open/none at ~7.5 Hz); blinks every 2.6-4.4 s; idle breathing and arm sway always on.
- Read at phone size: change the face on the emotional word ("crazy", "realized", "horrible", "proudly").

## Colour (one body colour per character, never shared)
**One colour per character** (house rule, user feedback v2.3): the head, body, arms and legs are always the same
body colour. Only the costume pieces (torso garment, head piece) bring other colours. No sleeve, trouser or shoe
colours on the limbs, no face flushes - compile_spec drops them and validate_spec warns.
Palette measured from the references (`style.json > palette`): cyan #58E0F6, ice #9EEFF6, teal #6DCBC6,
sky #91B8F1, blue #7199C8, mint #98D58A, neon green #35DD6D, lime #7BF25C, lemon #ECF053, cream #EADB8B,
peach #F2C489, orange #EDAE48, coral/red #F25857, salmon #E78F8B, pink #F091E6, orchid #CA78C1,
lavender #A99CF0, violet #B07CE8, white #F4F4F4, grey #BFC3C7.
Habits seen: heroes cyan/green/yellow/peach; the opposing side red/coral (enemy soldiers, the killer guard);
officials, doctors and leaders white; police blue/lavender; crowds use many pastels.

## Costumes (what makes a role readable - and what makes it look detailed)
The engine draws body, limbs and face; everything worn is a detailed illustrated image piece made to fit the rig:
- **Head piece** (everyone): hair, hat, helmet, beard, moustache - one picture per character, e.g. "worn beige
  beanie and a bushy brown beard". Strand, knit and fabric detail, a thin dark outline, cel shading.
- **Outfit** (main cast): uniform, apron, life vest, lab coat, prison stripes, suit jacket, dress, hoodie, army
  jacket with medals - drawn on the torso and always **SLEEVELESS** (only the garment body from the shoulders to the
  hips). Drawn sleeves hang still while the rig's real arms move on top of them; costume.py removes sleeve wording
  and adds the sleeveless instruction to every torso prompt. The arms and legs stay the body colour (no `sleeve`,
  `pants`, `shoes`).
- **Arms come out of the shoulders, under the clothes** (user feedback v2.3: "the arm joints seem to originate from
  the chest"): the image model paints fabric over the shoulder corners, so an arm drawn on top of the garment looks
  like it grows out of the chest. Both renderers draw the torso garment again over the top end of every arm in
  front of the body (a disc of `look.armhole_cap` x arm width around the shoulder, rig.json), so straps, lace
  shoulders and vest edges cover the arm's root like a real armhole. Check it on the cast sheet (stand,
  hands_hips, cheer): every arm must start at the shoulder, under the garment's shoulder.
- **Face pieces**: glasses, sunglasses, eye patch (ride the eyes with `follow_gaze`).
- Made by the make-assets skill: Kie.ai GPT Image 2.5 draws the piece on a template of our own head/body and it
  is fitted automatically (kie mode), or the bundled library (54 pieces, recolourable) is used (free mode).
  Never hand-place generated pieces; re-generate a bad one.
- Vector parts (`kit/data/parts.json`: hair_short, hair_messy, beard, helmet, police_cap, tie, apron, vest,
  belt...) are a fallback for extras and quick previews - flat and simple, so not for the lead characters.
- A costume can change mid-story (dressed as an officer, cleaned up after a bath): two pieces with `from`/`to`.

## Acting
- Pose changes on verbs, 0.15-0.3 s transitions; hold poses no longer than ~1.5 s without another beat.
- Use `kit/data/poses.json`. Front views: stand, stand_wide, hands_hips, arms_crossed_front, wave, point_viewer,
  present, explain, talk_gesture, shrug, point_up, arms_up, cheer, fists_up, hand_head, hands_head, facepalm,
  chin_think, proud, sad_stand, slump, scared, shocked, hold_up, hold_side, dance, float, sink.
  Side views: walk, run, sneak, point_fwd, point_down, hold_front, show, reach, reach_down, grab, push, throw,
  throw_back, punch, guard, arms_crossed, hug_self, drink, eat, think, bow, sit, sit_relaxed, sit_floor,
  sit_floor_sad, slump_sit, crouch, cower, kneel, crawl, lie_back, lie_front, dead, fall, jump, swim,
  carry_heavy, lean_wall, bend_grab (crouch down and take hold of something on the floor), drag_low (crouched,
  pulling), drag (upright, leaning back, pulling), lift_body (holding someone up in front), phone_call (hand at the
  ear), salute, pray, aim (both arms forward), read, brush_face (arm up at someone's face), clap, dig, sleep_lie.
- Actions (`act`, `compile_spec.py`): wave, nod, laugh, shiver, scrub, dance, cheer_bounce, shake_fist, pound,
  talk_hands, struggle, flail, swim_stroke, write, type, bounce, brush (makeup, combing, painting), dig, stir, clap,
  pull_rope, knock, eat_bites, phone_talk (cycles); fall_down, faint, jump_once, sit_down,
  stand_up, throw_once, punch_once, double_take, flinch, slump_down, shoot_once, salute_once, fall_asleep (one-shots); topple (the whole body tips over
  stiffly around the feet - "died", fainting against a wall).
- One character moving another (dragging a body, carrying someone, lifting, leading by the hand): the movers act
  it out (`bend_grab` on the body, then `drag_low`/`drag`/`lift_body` while they `move`) and the moved character
  gets `attach` to a mover's hand, so it really travels with them. Never leave a carried body lying still.
- Nobody slides: any character moved across the ground steps (the compiler adds the walk cycle with the right cadence,
  backwards when pulling, arms still while the hands hold something).
- Walkers walk across the frame (move + walk cycle), runners lean forward; swimmers are horizontal; the dead lie
  flat with X eyes; seated characters sit on real chairs in the background art.
- **Riding in a vehicle** (car, cart, carriage, wagon, boat): riders sit ON the seat, inside the vehicle - thighs
  along the cushion, knees bent at its front edge, shins dropping down behind the door, passengers' hands on their
  thighs, the driver's on the wheel; nothing hangs below the floor and no body stands behind the vehicle. Use the
  shot's `vehicles` list (vehicles.py makes a seat layer behind the riders and a door layer in front, finds the
  seats and seats the riders). A wave from a vehicle raises one arm while the rider stays seated (`"wave"` on the
  rider), never `act: wave` (it stands them up).
- Facing: characters face the person they talk to (`face: -1` flips). Eyes look the way they face.

## Crowds and armies
- 4-12 extras as separate cast ids (`extra1`...), mixed pastel colours or one team colour (red army vs cyan army),
  same costume for a group (helmets + rifle props, black hats + canes), smaller (25-45% height), varied poses,
  slight overlaps, some walking, some cheering (`cheer_bounce`), arranged in two rows.

## States
`state`/`states` on an actor: gray (dead, remembered, irrelevant), silhouette (unknown, passed out), red (wound,
blood, rage), sick (illness), ghost (half transparent). States tint the WHOLE character (head, body and limbs stay
one colour); use red/sick rarely - acting carries the emotion.
