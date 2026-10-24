# plan/spec.json - schema

All times are **global seconds** (the same clock as the narration). Positions are in **scene pixels** of the
1080x1920 frame at camera zoom 1 (x right, y down). Paths are relative to the project folder.

```jsonc
{
  "version": 1,
  "meta": {"title": "MONEY RAIN", "slug": "money-rain", "fps": 30, "width": 1080, "height": 1920, "duration": 51.2},
  "audio": {
    "voice": "audio/voice.wav", "music": "audio/music.wav", "music_db": -17,
    "auto_sfx": true,                       // compile_spec adds pops/whooshes/impacts/cash/glitch/swell
    "sfx": [{"t": 12.3, "file": "audio/sfx/impact.wav", "gain_db": -6}]
  },
  "captions": [{"text": "When", "t": 0.0, "end": 0.18, "color": "yellow|red|white|#hex", "scale": 1.0}],
  "caption_style": {"size": 100, "y": 0.758, "fonts": ["Anton-Regular", "Impact"]},   // optional overrides
  "look": {"vignette": 0.42, "grain": 0.025, "end": "none|fade_black"},
  "cast": {
    "hobo": {
      "color": "#F2C489",          // body colour (unique per character)
      "glow": 0.0,                 // 0-1 coloured outer glow
      "build": 1.0, "limb": 1.0, "head": 1.0,   // torso width / limb width / head size multipliers
      "idle": 1,                   // idle breathing + arm sway
      "parts": ["hair_messy", "beard", "tunic"],   // vector costume kit (parts.json)
      "c1": "#5B3A22", "c2": "#4A2E1A",           // costume colours used by parts
      "outline": "#5A3F14",        // optional ink colour (default: the body colour x 0.42, as in the samples)
      // no "sleeve"/"pants"/"shoes": one colour per character (compile_spec drops them; "house": {"limb_colours": true} opts out)
      "accessories": [             // image costume pieces (PNG with alpha) - written by assets.py / costume.py
        {"file": "assets/cast/hobo_head.png", "slot": "head|torso", "w": 1.28, "dx": 0.006, "dy": 0.02,
         "rot": 0, "behind": false, "flip": false, "from": 0, "to": 7.02,   // from/to: costume window (s)
         "over_face": false, "follow_gaze": false}   // glasses: over_face + follow_gaze (ride the eyes)
      ]                            // head slot: w/dx/dy in head diameters from the head centre (+dy down)
    }                              // torso slot: units of torso length from the hip (up is negative dy)
  },
  "shots": [{
    "id": "S01", "t": 0.0, "end": 1.4,
    "transition": "cut|flash|light_leak|red_wipe|glitch|bw_fade|whip|zoom_blur",   // INTO this shot
    "bg": {"file": "assets/bg/alley.jpg", "kind": "image|video|color", "color": "#222",
           "world": [3200, 1920],                          // optional: a wider/taller location (scene px) - see Notes
           "grade": "none|moody|dark|night|warm|cold|sepia|bw|green|red", "blur": 3,
           "scale": 1.06, "offset": [0, 0], "pan": [0, 0], "flip": false,
           "start": 0.0, "speed": 1.0},                    // video backgrounds (live inserts)
    "camera": "auto",                                       // measured house camera (default) - or keys:
    "camera_keys_example": [                                // a list here replaces the auto plan for this shot
      {"t": 0.0, "zoom": 1.32, "focus": [540, 1150]},
      {"t": 0.55, "zoom": 1.02, "focus": [540, 960], "ease": "out"},     // ease of the move INTO this key
      {"t": 1.4, "zoom": 1.05, "focus": [540, 960], "ease": "linear"}    // inout | out | linear | cut
    ],
    "shake": [{"t": 0.9, "dur": 0.4, "amp": 18}],
    "actors": [{
      "cast": "hobo", "x": 540, "y": 1760, "h": 1100,       // foot point and standing height in px
      "face": 1,                                             // 1 faces right, -1 faces left
      "z": 0, "crop": false, "shadow": true, "rot": 0,
      "keys": [                                              // pose + face keys
        {"t": 0.0, "pose": "sit_floor", "eyes": "determined", "mouth": "none"},
        {"t": 0.9, "pose": "eat", "dur": 0.2, "eyes": "happy", "mouth": "grin", "gaze": 0.11, "gaze_y": 0.05,
         "set": {"aN": [92, 150], "head": 6, "turn": 0}},   // per-key overrides of pose fields
        {"t": 1.2, "eyes": "worried", "mouth": "frown"}   // no "face_color": the head keeps the body colour (house rule)
      ],
      "act": [{"t": 1.0, "end": 1.4, "kind": "nod", "eyes": "happy", "then": "stand"},   // actions
              {"t": 10.1, "end": 11.5, "kind": "brush", "to": "hobo", "at": "cheek"},          // done TO someone
              {"t": 1.3, "end": 1.4, "kind": "topple", "rot": -24, "dur": 0.5, "pose": "slump_sit", "eyes": "closed"}],
      "move": [{"t": 0.0, "x": 300, "y": 1760}, {"t": 1.4, "x": 640, "y": 1760, "ease": "linear", "step": true}],
      "walk": [{"t": 0.0, "mode": "walk|run|none", "speed": 1.6, "arms": true}],   // speed < 0 walks backwards
      "talk": [[0.2, 1.1]],
      "hold": [{"t": 0.9, "end": 1.4, "file": "assets/props/bread.png", "hand": "N|F", "w": 180,
                "offset": [0, -20], "rot": 0, "front": true, "covers": ["food"],
                "grip": [0.33, 0.84], "tip": [0.72, 0.09], "style": "tool|upright"}],   // grip/tip/style: from the prop's
                                                     // <image>.grip.json (props.py) unless given here
      "enter": {"from": "left|right|bottom|top|pop", "t": 0.0, "dur": 0.35},
      "exit": {"to": "left|right|bottom|top|pop", "t": 1.1, "dur": 0.3},
      "flip": [[0.8, -1]],                                   // [time, face] turns
      "attach": [{"to": "sol1", "hand": "N|F", "grip": "neck|shoulder|hip|head|feet|hand_N|hand_F",
                  "t": 5.85, "end": 7.0, "snap": false, "blend": 0.2, "offset": [0, 0]}],   // carried / dragged by another actor
      "state": "color|gray|silhouette|red|sick|ghost",       // whole shot
      "states": [{"t": 1.0, "end": 1.4, "state": "gray", "fade": 0.2}]
    }],
    "props": [{"file": "assets/props/box.png", "x": 540, "y": 1500, "w": 700, "t": 0.0, "end": 1.4,
               "z": "back|front", "pop": true, "pop_out": false, "rot": 0, "flip": false, "screen": false,
               "anim": "none|float|bob|spin|shake|fall|slide|grow|drift", "amp": 10, "dx": -400, "dur": 0.35,
               "shadow": true, "outline": false, "blend": "normal|screen|add", "opacity": 100}],
    "creatures": [{"id": "hens", "animal": "chicken", "file": "assets/creatures/hen.png", "x": 520, "y": 1800,
                   "h": 260, "count": 4, "spread": [600, 70], "behave": "idle|peck|wander|walk|flee|hop|fly|swim|sleep",
                   "range": 240, "to": [1300, 1820], "speed": 1.0, "px_s": 210, "dir": 1, "faces": "right|left",
                   "t": 0.0, "end": 2.4, "z": "back|front", "pop": true, "sound": "audio/sfx/hens.wav",
                   "sound_every": 3.2, "gain_db": -15, "covers": ["chickens", "hens"], "shadow": true}],
    "icons": [{"kind": "emoji|thought|speech|badge", "file": "assets/icons/skull_and_crossbones.png",
               "x": 760, "y": 560, "size": 220, "t": 0.6, "end": 1.4, "no": false, "text": "3D",
               "text_color": "#E8202A", "text_size": 120, "text_pos": [0, 30], "tail": [-0.5, 0.9],
               "ring": "#3D3638", "face": "#6B5C61", "anim": "float|spin|none", "screen": false, "pop_out": true}],
    "fx": [{"kind": "money_rain|image_rain|embers|dust|snow|rain|smoke|tint|glitch|flash|video|fire|overlay",
            "t": 0.5, "end": 1.4, "file": "assets/icons/banknote_with_dollar_sign.png", "count": 30,
            "pile": true, "min_w": 90, "max_w": 170, "speed": 520, "area": [-80, 1160],
            "color": "#3AA64A", "opacity": 40, "blend": "overlay|multiply|color|screen|add", "fade": 0.25,
            "x": 540, "y": 960, "w": 900, "screen": false, "dark": false}],
    "state": [{"kind": "bw|gray|dark|tint", "t": 1.0, "end": 1.4, "fade": 0.3, "color": "#C8202A", "amount": 60}]
  }]
// creatures: living animals. x/y = the feet of the first one (scene or world px), h = its height in px (true to
// the characters: creatures.py list gives each animal's share of a person's height), count/spread = a flock
// scattered around it (each one moves on its own), behave = what they do the whole time they are on screen
// (range = how far they roam; walk/flee go to "to"), faces = the way the picture faces (filled from the image's
// sidecar), sound = their sound, repeated every ~sound_every s while on screen (compile_spec adds the cues).
}
```

## Notes
- `say`, `w`, `ideas`, `camera_kind`, `notes` are planning fields (auto_plan writes them); compile_spec drops them.
- Camera: leave `"camera": "auto"` (what auto_plan writes) - compile_spec plans the measured jolt rhythm from the
  shot's words, pops, pose keys and actions (see house-style `editing-grammar.md`). Write keys (in `camera`, not
  `camera_keys_example`) only for a special move. In keys, `focus` is the scene point in the frame centre; zoom 1 =
  full frame. A key's `ease` shapes the move that arrives at it: `out` = snap (fast then settle), `inout` = smooth,
  `linear` = drift, `cut` = hold the previous key then jump (punch-in).
- Pose keys: the move to a key's pose starts at `t` and lasts `dur` (default 0.22 s). The first key of each
  shot snaps. Eyes/mouth/gaze change instantly at `t`. `set` overrides fields of the pose (`lean`, `head`,
  `hip` [dx,dy], `aF`/`aN`/`lF`/`lN` [upper, bend], `turn` 0 three-quarter view - 1 front view, `fFront` 1 = in a
  front view the far arm is drawn in front of the body - for arms that cross in front of the chest). Prefer a
  pose that already does the gesture over `set` arm angles: the library's hands are placed on the chin, ear,
  brow, chest and object.
- Arms always start at the outer top corners of the body: compile_spec measures each character's torso garment
  (cast "shoulder"/"shoulder_dn" are filled in; leave them out) so the arms come out of a jacket's armholes or the
  bare body's top corners - never from the chest.
- Front vs three-quarter: standing, talking and reacting poses are front views (`turn: 1`, shoulders apart, both
  arms visible) like the samples; poses that act on something (walk, run, point, hold, eat, drink, phone, read,
  clap, pray, think, fight, sit, lie) are three-quarter views - the body and its clothes turn a little towards
  `face`, the camera-side arm `aF` is in front of the chest and `aN` comes from behind it. The eyes always look
  towards the facing side (`gaze` 0.11 default, up to 0.17; `gaze_y` + looks down, - looks up).
- House rules (v2.3, user feedback): one colour per character - `sleeve`/`pants`/`shoes` and `face_color` are dropped
  by compile_spec (`"house": {"limb_colours": true, "face_colours": true}` at the top level opts out). Torso
  costume pieces are sleeveless.
- `vehicles` (a shot list): people riding in a car, cart, carriage, wagon or boat -
  `{"file": "assets/props/car.png", "x": 900, "y": 1573, "w": 1050, "t": 13.1, "end": 14.6, "dx": 700, "dy": 0,
  "flip": false, "covers": ["car", "drove"], "riders": [{"cast": "driver", "seat": -1, "h": 590, "role": "driver",
  "keys": [{"t": 13.1, "eyes": "determined"}]}, {"cast": "org", "seat": 0, "h": 590, "keys": [...],
  "wave": [[13.8, 14.4]]}]}`. compile_spec (vehicles.py) adds the seat layer (behind everyone), the door layer (in
  front) and the riders seated on their cushions (sit pose, thighs along the cushion, knees bent, hands on the
  thighs or the wheel), all travelling `dx`/`dy` over the window. `seat` indexes the seats found in the picture
  (0 = rearmost, -1 = front); `"hip": [dx_frac, dy_frac]` overrides a seat anchor. Run `vehicles.py layers <image>`
  once and LOOK at `<name>_layers.png`.
- Creature `gait`: a list of frame files (or the frames recorded in the image's sidecar by `creatures.py gait`):
  compile_spec replaces the creature with frame-flipping props along its behaviour path (`gait_fps`, default 9,
  12 for flee/fly); `"gait": false` keeps the still picture.
- Props: `"exact": true` shows the prop exactly from `t` (no early start) - for back-to-back frames.
- `audio.sfx` cues may play part of a file: `"offset"` (s into the file), `"dur"` (s), `"fade_in"`, `"fade_out"` (s) -
  ambience beds and long effects without pre-cut files.
- Hand-made camera keys are clamped inside the picture by compile_spec (a focus too close to an edge would show a
  black band): at zoom z the focus stays at least 540/z from the sides and 960/z from the top and bottom.
- `bg.world` [W, H]: the location is bigger than the frame - a long street, a corridor, a battlefield, a beach
  (wide, e.g. [3200, 1920]) or a staircase, a cliff, a tall building (tall/big, e.g. [1620, 2880]). x/y of actors,
  props, icons and camera focus are then world coordinates (0..W, 0..H); the background is made at that size
  (asset_list `world`) and covers it; the auto camera follows whoever travels and never shows past its edges. Use it
  whenever characters travel, chase, drag or carry someone, or the story moves along a place - real distance (half a
  frame to several frames per shot) is what makes movement read. Without `world` the scene is the frame.
- Steps: whenever `move` carries a standing character across the ground and no `walk`/`run` is keyed for that
  stretch, compile_spec adds a walk cycle with a cadence from the speed (backwards when it moves against its
  facing, no arm swing while its hands hold something or someone). Nobody slides. `"step": false` on a move key
  opts out (vehicles, ice, floating); keyed `walk`/`run` entries always win; `"arms": false` stops the arm swing.
- Holding: the hand is at the prop's grip; a `tool` continues the forearm (its tip points where the arm points),
  an `upright` prop stays upright. Grips come from `<image>.grip.json` next to the image (compile_spec estimates
  and writes it if missing; `python props.py grip <image>` + LOOK at `<image>.grip.png` to check or fix it).
- Actions done to someone (`"to": cast id`, `"at": face|cheek|head|mouth|chest|arm|hand` or [dx, dy] in head
  widths): the doer's arm reaches so the held tool's tip (or the hand) lands on that spot and strokes around it;
  the tool points at the spot for the whole action. Stand the doer beside the person, not behind their head.
- `covers` (on props, icons, holds, fx, keys, acts, costume pieces): the narration words this element shows, for
  coverage.py when its file name does not already say it ("covers": ["makeup"] on a brush). Actors draw in list
  order, higher `z` in front: put whoever holds the important prop in front of the person it is used on.
- `attach`: this actor is held by another actor's hand from `t` to `end` (dragged, carried, lifted, led by the
  hand). compile_spec bakes it into `move` keys every 2 frames from the carrier's solved hand, so the body follows
  every step, crouch and walk cycle in both After Effects and the preview. Default (`snap: false`): the body stays
  where it is when the hand takes it and then moves with the hand - stage the carrier's hand on the body first
  (`bend_grab`). `snap: true` pulls the `grip` joint onto the hand over `blend` s. The carrier needs its own
  `move` (and a pulling/carrying pose); the attached actor keeps its own pose (`dead`, `lie_back`, `sit`...).
- `topple` tips the whole body around the feet (negative `rot` falls backwards for a right-facing actor). Stage it
  so the head stays in frame - validate_spec warns when a head leaves the frame.
- Actors of the same cast id share one character comp (global timeline); a cast id can only appear once per
  shot - use extras (`extra1`, `extra2`...) for crowds and twins.
- Icons/props popping at the very start of a shot do not pop (they are already there); give them `t` later
  than the shot start to pop on a word.
- Video backgrounds (`.mp4/.mov`) play from `start` at `speed`, loop if short, and take the B&W look with
  `grade: "bw"` or a `state` of kind `bw`.
