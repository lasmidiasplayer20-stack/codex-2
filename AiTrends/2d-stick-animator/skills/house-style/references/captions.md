# Captions

Measured from all seven references; implemented by `captions.py` + the engines (settings in `style.json > captions`).

- **One word at a time**, centred, about **75.8% down the frame** (measured 74.1-78.5%; y ~1455 px of 1920).
- A very short word (< 0.16 s, a function word like a, to, on, he, it, at, the) merges with the next when the
  pair is <= 12 characters and no comma/period sits between them: "a bath", "to be", "on him", "had an",
  "no one", "At that". Most captions are single words.
- Each caption stays until the next one starts (no flicker while the voice runs); blank after pauses > 0.35 s.
- **Font:** a heavy condensed sans in the Burbank Big Condensed Black family. Use Burbank if installed, else
  **Anton** (bundled, OFL - install it in Windows for After Effects), else Impact.
- **Size:** glyph band ~85-95 px tall at 1080x1920 (font size ~100). Long words still fit ("extinguishers").
- **Colour:** yellow #FFF40A. **Red #F2283A on 0-2 emotional peak words per video** ("screamed", "completely",
  "others"). Occasionally one word is bigger (x1.12) for emphasis ("bribe", "30").
- **Finish:** dark olive-black stroke (~5 px, behind the fill), a hard extruded drop shadow down-right
  (~6 px, no blur), and a soft yellow glow halo.
- **Animation:** pop on every change - scale 122% -> 100% within ~4 frames with a tiny settle (no fade, no slide).
- **Stays yellow in B&W moments** (captions sit above all grades) and on white flash frames.
- Script markup feeding it: `**word**` = red, `*word*` = big (stripped before text-to-speech).
