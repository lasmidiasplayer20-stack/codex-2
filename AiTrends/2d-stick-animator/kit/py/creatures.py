"""Living creatures: full-body animals that move, act and make their sounds (never a head icon).

  python creatures.py list                                 # the animals the kit knows: emoji, behaviour, size, sound
  python creatures.py prep P/assets/creatures/hen.png [--faces left|right]   # trim to the feet line, write the sidecar
  python creatures.py strip P --shot S01 [-o qc/creatures.jpg]               # frames of one shot's creatures over time
  python creatures.py gait P/assets/creatures/dog.png --kind run|walk|hop|fly|two_legs [--frames 4] --yes
      # the gait cycle (same animal, legs in sequence; Kie.ai ~6 credits a frame): every creature that moves on screen
      # needs one - compile_spec then flips the frames along its path (a sliding still reads as a doll)

A shot's "creatures" list puts animals in the scene (spec-schema.md): each is a cut-out image (whole body, side view)
anchored at its feet, alive the whole time it is on screen - breathing, looking around, walking, pecking, hopping,
flying or swimming - with its sound (compile_spec adds the cues). The behaviour maths below is deterministic (a
function of time and the creature's id) and the After Effects engine runs the same maths in expressions, so the
preview and After Effects agree frame for frame.

Behaviours ("behave"):
  idle    stands, breathes, looks around (turns now and then)                 any animal
  peck    short walks between spots, pecks the ground twice at each stop      chickens, hens, birds on the ground, pigeons
  wander  walks between random spots near its place, pauses                    dogs, cats, pigs, sheep, goats, cows, rats
  walk    walks to "to" [x, y] at a steady pace, then idles                    any animal going somewhere
  flee    runs to "to" (or off-screen) fast with a big bounce                  scared animals, a flock scattering
  hop     hops between spots                                                   rabbits, frogs, small birds, kangaroos
  fly     loops through the air with flapping                                  birds, bats, bees, flies, butterflies
  swim    glides back and forth with a tail wiggle                             fish, sharks, ducks on water
  sleep   slow deep breathing, no movement                                     sleeping animals
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BEHAVES = ("idle", "peck", "wander", "walk", "flee", "hop", "fly", "swim", "sleep")

# animal -> Fluent 3D full-body emoji (free mode; they all face LEFT; None = only a face exists, search instead), default behaviour, height as a share of a
# standing character's height (h of the actor), sound search words / ElevenLabs sound prompt (None = silent)
ANIMALS = {
    "chicken": {"emoji": "Rooster", "behave": "peck", "size": 0.24, "sound": "hens clucking", "aka": ["hen", "hens", "chickens", "rooster", "roosters", "poultry", "chick", "chicks"]},
    "duck": {"emoji": "Duck", "behave": "wander", "size": 0.22, "sound": "ducks quacking", "aka": ["ducks"]},
    "turkey": {"emoji": "Turkey", "behave": "peck", "size": 0.3, "sound": "turkey gobbling", "aka": ["turkeys"]},
    "bird": {"emoji": "Bird", "behave": "fly", "size": 0.12, "sound": "small birds chirping", "aka": ["birds", "pigeon", "pigeons", "sparrow", "crow", "crows"]},
    "dog": {"emoji": "Dog", "behave": "wander", "size": 0.34, "sound": "dog barking", "aka": ["dogs", "puppy", "hound"]},
    "cat": {"emoji": "Cat", "behave": "wander", "size": 0.24, "sound": "cat meowing", "aka": ["cats", "kitten"]},
    "cow": {"emoji": "Cow", "behave": "wander", "size": 0.62, "sound": "cow mooing", "aka": ["cows", "cattle", "bull", "ox"]},
    "pig": {"emoji": "Pig", "behave": "wander", "size": 0.36, "sound": "pigs oinking", "aka": ["pigs", "hog", "boar"]},
    "horse": {"emoji": "Horse", "behave": "wander", "size": 0.8, "sound": "horse neighing", "aka": ["horses", "pony"]},
    "sheep": {"emoji": "Ewe", "behave": "wander", "size": 0.36, "sound": "sheep bleating", "aka": ["ewe", "lamb", "lambs"]},
    "goat": {"emoji": "Goat", "behave": "wander", "size": 0.38, "sound": "goat bleating", "aka": ["goats"]},
    "rat": {"emoji": "Rat", "behave": "wander", "size": 0.1, "sound": "rats squeaking", "aka": ["rats"]},
    "mouse": {"emoji": "Mouse", "behave": "wander", "size": 0.08, "sound": "mouse squeaking", "aka": ["mice"]},
    "rabbit": {"emoji": "Rabbit", "behave": "hop", "size": 0.2, "sound": None, "aka": ["rabbits", "bunny", "hare"]},
    "monkey": {"emoji": "Monkey", "behave": "hop", "size": 0.34, "sound": "monkey chattering", "aka": ["monkeys", "chimp", "chimpanzee", "ape"]},
    "camel": {"emoji": "Camel", "behave": "walk", "size": 0.9, "sound": "camel groaning", "aka": ["camels"]},
    "elephant": {"emoji": "Elephant", "behave": "walk", "size": 1.2, "sound": "elephant trumpeting", "aka": ["elephants"]},
    "fish": {"emoji": "Fish", "behave": "swim", "size": 0.14, "sound": None, "aka": ["fishes"]},
    "baby chick": {"emoji": "Baby chick", "behave": "peck", "size": 0.1, "sound": "chicks peeping", "aka": []},
    "lion": {"emoji": None, "behave": "wander", "size": 0.55, "sound": "lion roaring", "aka": ["lions"]},
    "tiger": {"emoji": "Tiger", "behave": "wander", "size": 0.55, "sound": "tiger growling", "aka": ["tigers"]},
    "wolf": {"emoji": None, "behave": "wander", "size": 0.45, "sound": "wolf howling", "aka": ["wolves"]},
    "bear": {"emoji": None, "behave": "wander", "size": 0.8, "sound": "bear growling", "aka": ["bears"]},
    "snake": {"emoji": "Snake", "behave": "wander", "size": 0.12, "sound": "snake hissing", "aka": ["snakes", "cobra", "viper"]},
    "crocodile": {"emoji": "Crocodile", "behave": "wander", "size": 0.25, "sound": "crocodile hissing", "aka": ["crocodiles", "alligator"]},
    "shark": {"emoji": "Shark", "behave": "swim", "size": 0.5, "sound": None, "aka": ["sharks"]},
    "bee": {"emoji": "Honeybee", "behave": "fly", "size": 0.06, "sound": "bees buzzing", "aka": ["bees"]},
    "fly": {"emoji": "Fly", "behave": "fly", "size": 0.04, "sound": "flies buzzing", "aka": ["flies"]},
    "bat": {"emoji": "Bat", "behave": "fly", "size": 0.12, "sound": "bats squeaking", "aka": ["bats"]},
    "spider": {"emoji": "Spider", "behave": "wander", "size": 0.06, "sound": None, "aka": ["spiders"]},
    "frog": {"emoji": None, "behave": "hop", "size": 0.1, "sound": "frog croaking", "aka": ["frogs", "toad"]},
    "parrot": {"emoji": "Parrot", "behave": "idle", "size": 0.18, "sound": "parrot squawking", "aka": ["parrots"]},
    "owl": {"emoji": "Owl", "behave": "idle", "size": 0.18, "sound": "owl hooting", "aka": ["owls"]},
    "penguin": {"emoji": "Penguin", "behave": "wander", "size": 0.36, "sound": "penguins calling", "aka": ["penguins"]},
}


def animal_of(word):
    w = (word or "").lower().strip()
    if w in ANIMALS:
        return w
    for k, v in ANIMALS.items():
        if w in v["aka"]:
            return k
    return None


# ----------------------------------------------------------------------------------------- shared maths
TAU = 2 * math.pi


def h01(n):
    """the same hash in the AE expressions: frac(sin(n * 12.9898 + 78.233) * 43758.5453)"""
    x = math.sin(n * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


def sm(v):
    v = max(0.0, min(1.0, v))
    return v * v * (3 - 2 * v)


def id_hash(cid):
    return sum((i + 1) * ord(ch) for i, ch in enumerate(str(cid))) % 997


def copy_params(c, i):
    """(seed, dx, dy, size factor) of copy i of a flock"""
    seed = id_hash(c.get("id", "creature")) + 101 * i
    sp = c.get("spread") or [0, 0]
    if i == 0:
        return seed, 0.0, 0.0, 1.0
    return (seed, (h01(seed + 1) - 0.5) * float(sp[0]), (h01(seed + 2) - 0.5) * float(sp[1]),
            0.88 + 0.24 * h01(seed + 3))


def copies(c):
    """copy indices in drawing order (further back first)"""
    n = max(1, int(c.get("count", 1)))
    return sorted(range(n), key=lambda i: (copy_params(c, i)[2], i))


def state(c, i, t, shot_t):
    """(x, y, sx, sy, rot) of copy i at time t: feet position in scene px, signed scale factors, rotation (deg)"""
    seed, ox, oy, hk = copy_params(c, i)
    t0 = float(c.get("t", shot_t))
    u = t - t0
    H = float(c.get("h", 200)) * hk
    x0 = float(c.get("x", 540)) + ox
    y0 = float(c.get("y", 1750)) + oy
    sp = float(c.get("speed", 1.0))
    f0 = 1.0 if float(c.get("dir", 1)) >= 0 else -1.0
    art = -1.0 if c.get("faces", "right") == "left" else 1.0
    R = float(c.get("range", min(260.0, 1.6 * H)))
    beh = c.get("behave", "idle")
    ph = h01(seed + 7) * 6.2832
    x, y, fl, rot = x0, y0, f0, 0.0
    if beh == "sleep":
        br = 0.05 * math.sin(TAU * 0.35 * u + ph)
    else:
        br = 0.03 * math.sin(TAU * 1.4 * u + ph)
    sy = 1.0 + br
    sx = 1.0 - 0.5 * br
    if beh in ("wander", "peck", "hop"):
        T = (2.2 + 1.4 * h01(seed + 11)) / sp
        q = (u + h01(seed + 13) * T) / T
        n = math.floor(q)
        v = q - n
        xa = x0 + (h01(seed + 31 + (n - 1) * 17) - 0.5) * 2 * R
        xb = x0 + (h01(seed + 31 + n * 17) - 0.5) * 2 * R
        mf = 0.6 if beh == "hop" else 0.5
        k = sm(v / mf) if v < mf else 1.0
        x = xa + (xb - xa) * k
        fl = 1.0 if xb >= xa else -1.0
        mv = 1.0 if (v < mf and abs(xb - xa) > 6) else 0.0
        if beh == "hop":
            w = (v / mf * 2.0) % 1.0
            y = y0 - mv * 0.35 * H * 4 * w * (1 - w)
            rot = -fl * 9 * (1 - 2 * w) * mv
        else:
            st = 3.6 * sp
            y = y0 - mv * 0.045 * H * abs(math.sin(math.pi * st * u))
            rot = mv * 5 * math.sin(math.pi * st * u)
        if beh == "peck" and mv < 0.5:
            w = (v - mf) / (1 - mf)
            pk = 0.0
            if 0.12 <= w < 0.34:
                pk = math.sin(math.pi * (w - 0.12) / 0.22)
            elif 0.58 <= w < 0.8:
                pk = math.sin(math.pi * (w - 0.58) / 0.22)
            rot = fl * 30 * pk
            x += fl * 0.05 * H * pk
    elif beh in ("walk", "flee"):
        fast = beh == "flee"
        to = c.get("to") or [float(c.get("x", 540)) + f0 * (1100 if fast else 420), float(c.get("y", 1750))]
        dx = float(to[0]) - float(c.get("x", 540))
        dy = float(to[1]) - float(c.get("y", 1750))
        spd = float(c.get("px_s", 680 if fast else 210)) * sp
        dur = max(0.3, math.hypot(dx, dy) / spd)
        k = min(1.0, max(0.0, u) / dur)
        x = x0 + dx * k
        y = y0 + dy * k
        fl = 1.0 if dx >= 0 else -1.0
        mv = 1.0 if k < 1 else 0.0
        st = (5.5 if fast else 3.4) * sp
        y -= mv * (0.07 if fast else 0.045) * H * abs(math.sin(math.pi * st * u))
        rot = mv * ((8 if fast else 5) * math.sin(math.pi * st * u) + fl * (10 if fast else 0))
    elif beh == "fly":
        A = float(c.get("range", 260))
        a1 = TAU * 0.21 * sp * u + ph
        a2 = TAU * 0.33 * sp * u + ph * 1.7
        x = x0 + A * math.sin(a1)
        y = y0 + 0.35 * A * math.sin(a2)
        fl = 1.0 if math.cos(a1) >= 0 else -1.0
        sy *= 1 + 0.16 * math.sin(TAU * 7.5 * u)
        rot = fl * 6 * math.cos(a2)
    elif beh == "swim":
        A = float(c.get("range", 220))
        a1 = TAU * 0.13 * sp * u + ph
        x = x0 + A * math.sin(a1)
        y = y0 + 0.06 * H * math.sin(TAU * 0.6 * u + ph)
        fl = 1.0 if math.cos(a1) >= 0 else -1.0
        rot = 7 * math.sin(TAU * 2.3 * u + ph)
        sx *= 1 + 0.04 * math.sin(TAU * 2.3 * u + ph + 1.2)
    elif beh == "idle":
        P = (2.6 + 2.2 * h01(seed + 5)) / sp
        n = math.floor((u + h01(seed + 6) * P) / P)
        fl = f0 if h01(seed + n * 7 + 1) < 0.65 else -f0
        rot = 2.5 * math.sin(TAU * 0.6 * u + ph)
    return x, y, sx * fl * art, sy, rot


def size_of(c, i):
    return float(c.get("h", 200)) * copy_params(c, i)[3]


# ----------------------------------------------------------------------------------------- assets
def sidecar(path):
    return path + ".creature.json"


def load_side(path):
    try:
        return json.load(open(sidecar(path), encoding="utf-8"))
    except Exception:
        return {}


def prep(path, faces=None):
    """trim the picture to its visible pixels (so the bottom edge is the feet line) and record which way it faces"""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
    if bb:
        im = im.crop(bb)
        pad = max(2, int(0.02 * im.width))
        out = Image.new("RGBA", (im.width + 2 * pad, im.height + pad), (0, 0, 0, 0))
        out.paste(im, (pad, pad))       # transparent margin on the sides and top only: the feet touch the bottom
        out.save(path)
    side = load_side(path)
    if faces:
        side["faces"] = faces
    side.setdefault("faces", "right")
    json.dump(side, open(sidecar(path), "w", encoding="utf-8"))
    return side


def fill_from_sidecars(spec, project):
    """creatures take "faces" from their image's sidecar unless the plan sets it (compile_spec)"""
    for sh in spec.get("shots", []):
        for c in sh.get("creatures", []):
            if "faces" not in c and c.get("file"):
                p = c["file"] if os.path.isabs(c["file"]) else os.path.join(project or "", c["file"])
                f = load_side(p).get("faces")
                if f:
                    c["faces"] = f


def sound_cues(spec):
    """sound cues for every creature with a sound: on its first appearance, then every ~3 s while it is on screen"""
    cues = []
    for sh in spec.get("shots", []):
        for j, c in enumerate(sh.get("creatures", [])):
            snd = c.get("sound")
            if not snd:
                continue
            t0 = max(float(c.get("t", sh["t"])), float(sh["t"]))
            t1 = min(float(c.get("end", sh["end"])), float(sh["end"]))
            every = float(c.get("sound_every", 3.2))
            g = float(c.get("gain_db", -15))
            k, t = 0, t0 + 0.05
            while t < t1 - 0.3:
                cues.append({"t": round(t, 3), "file": snd, "gain_db": g if k == 0 else g - 4, "auto": True,
                             "creature": c.get("id", f"c{j}")})
                k += 1
                t += every * (0.8 + 0.4 * h01(id_hash(c.get("id", "c")) + k))
    return cues


# ----------------------------------------------------------------------------------------- gait cycles
# A still picture that only slides and bounces reads as a doll. Animals that move on screen get a gait cycle: a few
# frames of the SAME animal (image-to-image from its own picture) that flip while it travels - real leg motion.
GAITS = {
    "run": ["Frame 1 of a gallop cycle: body stretched long, both front legs reaching far forward, both back legs stretched far back, all paws off the ground.",
            "Frame 2 of a gallop cycle: front paws landing on the ground under the head, back legs swinging forward under the belly.",
            "Frame 3 of a gallop cycle: all four legs gathered together under the body, back rounded.",
            "Frame 4 of a gallop cycle: back paws planted on the ground pushing off, front legs lifting and reaching forward, chest up."],
    "walk": ["Frame 1 of a walk cycle: left front leg and right back leg stepping forward, the other two legs back.",
             "Frame 2 of a walk cycle: legs passing under the body, all paws close together on the ground.",
             "Frame 3 of a walk cycle: right front leg and left back leg stepping forward, the other two legs back.",
             "Frame 4 of a walk cycle: legs passing under the body again, head slightly lower."],
    "hop": ["Frame 1 of a hop: crouched low, ready to spring.", "Frame 2 of a hop: launching, back legs stretched, body rising.",
            "Frame 3 of a hop: airborne, body stretched out.", "Frame 4 of a hop: landing, front feet touching down."],
    "fly": ["Frame 1 of a wing flap: wings fully raised.", "Frame 2 of a wing flap: wings level, spread wide.",
            "Frame 3 of a wing flap: wings fully down.", "Frame 4 of a wing flap: wings level, rising again."],
    "two_legs": ["Frame 1 of a walk cycle: left leg forward, right leg back.", "Frame 2 of a walk cycle: legs passing under the body.",
                 "Frame 3 of a walk cycle: right leg forward, left leg back.", "Frame 4 of a walk cycle: legs passing under the body."],
}
GAIT_OF = {"walk": "walk", "flee": "run", "wander": "walk", "peck": "two_legs", "hop": "hop", "fly": "fly"}
SAME = ("Exactly the same animal as in the reference image: same colours and markings, same face, same drawing style, line "
        "weight and shading, same proportions. Whole body, exactly side view, facing {faces}. ")


def make_gait(path, kind="run", n=None, workers=4):
    """generate the gait frames of a creature picture (Kie.ai GPT Image 2.5, image-to-image, ~6 credits each) and
    record them in its sidecar: {"gait": ["dog_gait1.png", ...], "gait_kind": "run"}"""
    from concurrent.futures import ThreadPoolExecutor
    import gen_image as G
    from ra_common import get_key
    key = get_key("kie")
    side = load_side(path)
    faces = side.get("faces", "right")
    url = G.upload_ref(key, path)
    lines = GAITS[kind][: n or len(GAITS[kind])]
    base = os.path.splitext(path)[0]
    outs = [f"{base}_gait{i + 1}.png" for i in range(len(lines))]

    def one(i):
        if not os.path.exists(outs[i]):
            G.run_job({"kind": "creature", "prompt": SAME.format(faces=faces) + lines[i], "out": outs[i], "refs": [url],
                       "style": "3d"}, "kie", "3d")
            prep(outs[i], faces)
        return outs[i]

    with ThreadPoolExecutor(max(1, workers)) as ex:
        list(ex.map(one, range(len(lines))))
    side["gait"] = [os.path.basename(o) for o in outs]
    side["gait_kind"] = kind
    json.dump(side, open(sidecar(path), "w", encoding="utf-8"))
    print(f"{len(outs)} gait frames -> {', '.join(os.path.basename(o) for o in outs)}  (LOOK: same animal, legs in sequence)")
    return outs


def expand_gaits(spec, project=None):
    """compile_spec: creatures with gait frames become frame-flipping props along the same path the behaviour maths
    gives (state()), so both renderers show real leg motion; their sounds are kept as cues"""
    from PIL import Image
    n = 0
    A = spec.setdefault("audio", {})
    for sh in spec.get("shots", []):
        keep = []
        for c in sh.get("creatures", []):
            p = c.get("file", "")
            ap = p if os.path.isabs(p) else os.path.join(project or "", p)
            side = load_side(ap) if p else {}
            frames = c.get("gait") or [os.path.join(os.path.dirname(p), f).replace("\\", "/") for f in side.get("gait", [])]
            if not frames or c.get("gait") is False:
                keep.append(c)
                continue
            for cu in sound_cues({"shots": [dict(sh, creatures=[c])]}):
                A.setdefault("sfx", []).append(cu)
            fps = float(c.get("gait_fps", 12 if c.get("behave") in ("flee", "fly") else 9))
            H0 = Image.open(ap).size[1]
            sizes = {f: Image.open(f if os.path.isabs(f) else os.path.join(project or "", f)).size for f in frames}
            t0 = max(float(c.get("t", sh["t"])), float(sh["t"]))
            t1 = min(float(c.get("end", sh["end"])), float(sh["end"]))
            for i in copies(c):
                k = size_of(c, i) / float(H0)
                t, j = t0, 0
                while t < t1 - 1e-4:
                    tb = min(t1, t + 1.0 / fps)
                    xa, ya, sxa, sya, ra = state(c, i, t, sh["t"])
                    xb, yb, _, _, _ = state(c, i, tb, sh["t"])
                    moving = math.hypot(xb - xa, yb - ya) > 1.5
                    f = frames[j % len(frames)] if moving else p
                    W, Hh = sizes.get(f) or Image.open(ap).size
                    sh.setdefault("props", []).append({
                        "file": f, "x": round(xa, 1), "y": round(ya - k * Hh / 2, 1), "w": round(k * W, 1),
                        "t": round(t, 3), "end": round(tb, 3), "z": c.get("z", "back"), "pop": False, "sfx": False, "exact": True,
                        "flip": sxa < 0, "rot": round(ra, 2), "anim": "drift", "dx": round(xb - xa, 1),
                        "dy": round(yb - ya, 1), "shadow": c.get("shadow", True),
                        "covers": list(c.get("covers", [])) + [c.get("animal", ""), c.get("id", "")]})
                    t, j = tb, j + (1 if moving else 0)
            n += 1
        sh["creatures"] = keep
    return n


# ----------------------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list")
    p = sp.add_parser("prep"); p.add_argument("image"); p.add_argument("--faces", choices=["left", "right"])
    s = sp.add_parser("strip"); s.add_argument("project"); s.add_argument("--shot", required=True)
    s.add_argument("--spec", default="plan/spec.json"); s.add_argument("-o", "--out", default="qc/creatures.jpg")
    g = sp.add_parser("gait"); g.add_argument("image"); g.add_argument("--kind", default="run", choices=sorted(GAITS))
    g.add_argument("--frames", type=int, default=4); g.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    if a.cmd == "gait":
        if not a.yes:
            sys.exit(f"{a.frames} Kie.ai image-to-image jobs (~{6 * a.frames} credits): re-run with --yes after the user agrees")
        make_gait(a.image, a.kind, a.frames)
        return
    if a.cmd == "list":
        for k, v in ANIMALS.items():
            print(f"{k:12s} behave {v['behave']:7s} size {v['size']:.2f} x person  emoji '{v['emoji']}'  "
                  f"sound {v['sound'] or '-'}  ({', '.join(v['aka'])})")
    elif a.cmd == "prep":
        print(json.dumps(prep(a.image, a.faces)))
    else:
        import numpy as np
        from PIL import Image
        import ra_preview as RP
        spec = json.load(open(os.path.join(a.project, a.spec), encoding="utf-8"))
        from compile_spec import compile_spec
        spec = compile_spec(spec, a.project)
        sh = [x for x in spec["shots"] if x.get("id") == a.shot][0]
        R = RP.Renderer(a.project, spec, scale=0.3)
        ts = [sh["t"] + (sh["end"] - sh["t"]) * k / 7 for k in range(8)]
        frames = [Image.fromarray((np.clip(R.frame(t), 0, 1) * 255).astype(np.uint8)[..., :3]) for t in ts]
        w, h = frames[0].size
        sheet = Image.new("RGB", (w * 4, h * 2))
        for k, f in enumerate(frames):
            sheet.paste(f, ((k % 4) * w, (k // 4) * h))
        out = os.path.join(a.project, a.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sheet.save(out, quality=88)
        print(out)


if __name__ == "__main__":
    main()
