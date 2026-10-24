# Shot recipes (narration beat -> what the references put on screen)

Icons named here exist in `_kit/assets/icons/` (373 Fluent 3D emoji; `ls` it or read `_index`), copy the ones
you use into `assets/icons/`. Times: `w` = onset of the trigger word.

| beat | picture (spec) |
|---|---|
| **Opening hook** | protagonist large (h 1100-1450) mid-action in the first location, in full costume (hair/hat + beard/clothes pieces); `camera: "auto"` opens tight on the face and jolts out; first prop/icon pops on the first noun. |
| **Someone dies / is poisoned** | icon(s) pop on the cause word (skull_and_crossbones, rat, pill); `state` gray/bw from the word; the victim acts it (eyes `worried`/`sleepy`, mouth `frown`, `shiver`; never a head-colour flush); on "died" a close-up `act: topple` (rot -20..-30 when seated with `pose: slump_sit`, -70..-80 standing; stage it so the head stays in frame), eyes `closed`/`dead`; next shot `dead`/`lie_back` pose, eyes `dead`. |
| **A plan / idea / belief** | `thought` icon above the thinker's head with the idea's icon (swap arrows, crown, money...); face `determined`; push-in. |
| **An order / statement / report** | `speech` icon with the subject's icon; speaker `point_fwd` or `talk_gesture` + `talk` range; listener `wide`/`o`. |
| **A duration / countdown** | `badge` with alarm_clock (or no icon) and red `text` "3D", "18D", "100Y"; for a change ("up to 30 days") re-key a second badge with the new text at the word. |
| **Without X / no one / never** | the X icon with `no: true` (red prohibited sign), or a badge with an icon + `no`. "no one heard/showed up" -> B&W or grey crowd. |
| **Animals (farm, pets, wildlife, pests, a flock)** | `creatures` - the whole animal alive in the scene, never a head icon: chickens/hens `peck` (count 3-6, spread ~500x60) around the farmer's feet, dogs `wander` or `walk` beside their owner, a cat `sleep`s or `wander`s, birds `fly` above, fish `swim`, rabbits `hop`, rats scurry (`wander`, speed 1.5); a scared animal or flock `flee`s on the scary word; each with its `sound` (clucking, barking) and sized to the characters (`creatures.py list`); every animal that moves has its gait cycle (`"gait"` in the asset list / `creatures.py gait`) so its legs really move. The characters react to them (look at them with `gaze`, `bend_grab` to pick one up). |
| **Money / greed** | money icons (banknote_with_dollar_sign, money_bag, money_with_wings), `fx money_rain` (+ `pile`), `cheer`/`cheer_bounce`, eyes `happy`, mouth `grin`; cash SFX is automatic. |
| **Danger / problem / "The problem was"** | the characters react (eyes `worried`, `shocked`, a step back), `transition: flash` or `light_leak`, camera punch; a warning_sign icon only when the danger itself cannot be shown; red tint for violence; whoosh is automatic on the special transition. |
| **Chapter / time jump ("100 years later", "after 18 days")** | `light_leak` or `red_wipe` transition, new location, badge with the number, or a real insert. |
| **Realisation / shock** | close-up (`h` 1600-2300, `crop: true`), eyes `wide`, mouth `o`/`scream`, a pose key on the word (`shocked`, `hands_head`) so the auto camera jolts in on it - or a hand-made punch-in (`ease: cut`); optional `act: double_take`. |
| **Reactions: refuse, agree, believe, trust, doubt, surprise, love, sleep** | acted, not iconned: refuse = `arms_crossed_front` + head shake (`act nod` with a stern face) or a raised hand `point_fwd`; agree/believe = nod + eyes `happy`, mouth `smile`; trust = a handshake (two `reach` poses meeting) or a hand on the shoulder; doubt = `chin_think`, eyes `suspicious`; surprise = `shocked` + eyes `wide`; love = a hug pose + eyes `happy`; sleep = `sleep_lie`/`slump_sit` + eyes `sleepy`. No emoji faces, thumbs, hearts, 100s or zzz. |
| **Anger / shouting** | eyes `angry`, mouth `scream`/`teeth` on the peak, `act: shake_fist` or pose `fists_up`, `talk` range, red caption on the peak word, a shout/boo sound. |
| **Smell / sickness / cold** | `fx tint` green (#3AA64A, 30-45%) over the scene, slumped `slump`/`hug_self`, eyes `sleepy`/`worried`, `shiver`; flies/droplets/snowflake icons; a cough/groan sound. Never a green head on a different-coloured body. |
| **Riding in a vehicle (car, cart, carriage, boat)** | a shot `vehicles` entry: seat layer behind, doors in front, riders on the cushions (thighs along the seat, knees bent, shins behind the door), driver's hands on the wheel, passengers' on their thighs, the vehicle drifting `dx`; an engine/hooves sound under it; a wave = the rider's `"wave"` window (seated). Climbing in: the actor walks to the rear, crouches, then the shot cuts to them seated (or a short move onto the seat). Full-size stills to the user before the animatic. |
| **Race start / gunshot / a starting signal** | the starter raises the pistol (pointing UP, `hold` with `style: upright` + `rot`), `act: shoot_once` on the word, `fx flash` + `shake`, a LOUD pistol crack cue (-1..-3 dB) and the crowd reacting; runners burst off with footsteps under them. |
| **Crowd reacts** | 4-12 extras (separate cast ids, pastel colours or team colour), two rows, mixed poses (`cheer`, `shocked`, `point_fwd`, `walk`), some `talk`; pan across. |
| **Army / soldiers** | team colour with glow (0.6-0.7) + a detailed helmet piece (costume `hat_army_helmet` or generated) + held rifle prop (`hold` with `follow: true`), marching in side view (`walk` + `move`), auto camera tracks them; officers get `army_uniform`/`army_jacket_medals`; the other side in another colour (red vs cyan). |
| **Travel / walking / chasing** | a wide `bg.world` (e.g. [3200, 1920]) with a matching wide background; `move` the characters a long way across it (1000-2500 px in a 1.5-3 s shot) - legs step automatically, `run` for chases; the auto camera tracks them; `whip` transition for speed. |
| **Arrest / police** | blue/lavender officer with `hat_police_cap` + `police_uniform` pieces, pose `point_fwd` / `grab`; target `hands_head`/`scared`, eyes `worried`. |
| **Fight** | two actors facing (`face` 1/-1), `act: punch_once` / `punch`, `guard`, `shake` on hits, impact SFX. |
| **Height (climbing, falling from a building, an elevator, stairs)** | a tall `bg.world` (e.g. [1620, 2880]) with a tall background; `move` the character up or down it; the auto camera follows vertically. |
| **Fall / faint / drown** | `act: fall_down` / `faint`; underwater background with `swim`/`sink`/`float`, `act: flail` or `swim_stroke`; rising bubbles via `fx image_rain` with the droplet icon and a negative `speed` (e.g. -300), `min_w` 30, `max_w` 70. |
| **Hiding / sneaking** | `sneak` + slow walk, eyes `determined`, darker grade (`dark`), push-in. |
| **Flashback / remembering** | `state: bw` (or actors `states: gray`) on a re-used earlier location and framing. |
| **Inside the body / microscopic** | abstract bg (red macro of blood cells, generated), virus/microbe/drop_of_blood icons floating, `fx glitch` for multiplication, characters absent. |
| **A document / ID / letter / photo** | paper prop in hand (`hold` page_facing_up / scroll / identification_card), icon pop on the noun, push-in to the paper. |
| **Escalation ("even stronger", "more and more")** | the same prop pops 2-3 times in a row 0.2-0.3 s apart at shifted x; or more icons/crowd members each beat. |
| **Explosion / crash / fire** | `fx flash` + `fx video/fire` (screen-blended real fire on black) or fire icon, `shake` 0.5 s amp 22, boom/impact SFX (automatic for flash/shake). |
| **Real-world scale** | one live insert (`bg.kind: video`, 1-2.5 s, real or generated), often `grade: bw`, between cartoon shots. |
| **Twist / punchline** | close-up of the key character with a new face (smirk: eyes `determined` + mouth `smile`), slow push-in, or B&W crowd; keep it simple and readable. |
| **Moving someone (drag a body, carry, lift, lead)** | the movers walk up, `bend_grab` on the word that starts it (heads go down to the body), then `drag_low` (crouched pull) or `drag`/`lift_body` while their `move` keys pull them back or away a real distance (at least half a frame; use a wide `bg.world` so there is room) - their legs step backwards automatically; the moved actor gets `attach` to the main mover's hand (`grip` neck for a body dragged by the shoulders, hip for a lift, `hand_N` for leading by the hand) so it travels with them; a second mover just mirrors the poses. Show it on screen - never cut away while the body lies still. |
| **Grooming / makeup / shaving / washing someone** | the helper stands BESIDE the person (not behind their head), in front (`z` higher), holding the tool (`hold` with `follow: true`: makeup brush, comb, razor, sponge) - shows it on the word (`show` pose), then `act: brush` (or `scrub`) with `"to": "<person>", "at": "cheek"` so the tool tip lands on the face; foam/sparkle props on the face. |
| **Tools and everyday actions** | eat (`eat` + food held, `act eat_bites`), drink (`drink` + cup), phone (`phone_call` + phone, `act phone_talk`), write/sign (`write` + paper), read (`read` + book), type (`type` + computer), shoot (`aim` + gun, `act shoot_once`, flash + shake), dig/bury (`dig` + shovel), cook/stir (`act stir` + pot), knock (`act knock` at a door), pray, salute, clap, sleep (`lie_back`, closed eyes, zzz). The tool is always in the hand. |
| **Looking at something** | the looker faces it (`face`), `gaze` 0.14-0.17 and `gaze_y` (+0.07 looks down at a body or a box on the ground, -0.06 looks up at a sign or a tall man). |
| **Talking to the viewer / explaining** | front pose (`explain`, `present`, `point_viewer`, `wave`), `gaze` 0 (looks straight out), `talk` range. |
| **Ending loop** | last shot = same bg, cast, pose and framing as the opening; or `look.end: fade_black`. |

## Typical shot snippets
```jsonc
// realisation punch-in inside one shot
"camera": [{"t": 12.0, "zoom": 1.0, "focus": [540, 960]},
           {"t": 12.6, "zoom": 1.03, "focus": [540, 960], "ease": "linear"},
           {"t": 12.633, "zoom": 1.32, "focus": [600, 820], "ease": "cut"},
           {"t": 13.4, "zoom": 1.36, "focus": [600, 820], "ease": "linear"}]
// duration badge that counts up
"icons": [{"kind": "badge", "file": "assets/icons/alarm_clock.png", "x": 760, "y": 520, "size": 220, "t": 22.4, "end": 30.9, "text": "3D", "text_pos": [0, 30]},
          {"kind": "badge", "file": "assets/icons/alarm_clock.png", "x": 760, "y": 520, "size": 220, "t": 30.9, "text": "30D", "text_pos": [0, 30], "pop": false}]
// smell: green wash that grows
"fx": [{"kind": "tint", "color": "#3AA64A", "opacity": 42, "t": 44.6, "end": 50.4, "fade": 0.8}]
```
