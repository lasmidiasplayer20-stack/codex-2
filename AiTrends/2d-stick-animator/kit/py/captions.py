"""Turn words.json into the one-word pop captions of the house style.

usage: python captions.py PROJECT/timing/words.json -o PROJECT/timing [--script PROJECT/script/script_final.txt]
       [--red "screamed,never"] [--big "homeless,dead"]

Rules (measured on the samples):
  * one word per caption; a very short word (< 0.16 s) merges with the next word when the pair is <= 12 characters
    and there is no sentence break between them ("a bath", "to be", "on him", "had an")
  * a caption stays up until the next one starts (no gaps while the voice speaks); blank after long pauses
  * 0-2 RED words per video on the emotional peak (screamed, completely, dead...)  -> **word** in the script or --red
  * a few BIG words (112%) on key nouns                                        -> *word* in the script or --big
writes timing/captions.json and timing/captions.srt
"""
import argparse
import json
import os
import re

from ra_common import STYLE


FUNC_WORDS = set("a an the of to in on at for and or but with by as from into than that this his her its their he she it they we i was were is are be had has have no so up go him them".split())


def strip_punct(w):
    return re.sub(r"^[\"'(\[]+|[\"')\]]+$", "", w)


def markup_from_script(path):
    red, big = set(), set()
    if path and os.path.exists(path):
        t = open(path, encoding="utf-8").read()
        for m in re.finditer(r"\*\*([^*]+)\*\*", t):
            red.add(m.group(1).strip().lower())
        t2 = re.sub(r"\*\*[^*]+\*\*", " ", t)
        for m in re.finditer(r"\*([^*]+)\*", t2):
            big.add(m.group(1).strip().lower())
    return red, big


def build(words, red=(), big=()):
    C = STYLE["captions"]
    caps = []
    i = 0
    red = {r.lower().strip(" ,.!?") for r in red if r}
    big = {b.lower().strip(" ,.!?") for b in big if b}
    while i < len(words):
        w = words[i]
        text = strip_punct(w["w"])
        s, e = w["s"], w["e"]
        if i + 1 < len(words):
            n = words[i + 1]
            ends_sentence = w["w"].rstrip().endswith((".", "!", "?", ",", ";", ":"))
            pair = text + " " + strip_punct(n["w"])
            if (e - s) < C["merge_if_word_shorter_than_s"] and not ends_sentence and len(pair) <= C["max_chars_two_words"] \
                    and n["s"] - e < 0.08 and (text.lower() in FUNC_WORDS or len(text) <= 2):
                text, e = pair, n["e"]
                i += 1
        key = re.sub(r"[^a-z0-9' ]", "", text.lower())
        color = "red" if key in red or any(k in red for k in key.split()) else "yellow"
        scale = 1.12 if (key in big or any(k in big for k in key.split())) else 1.0
        caps.append({"text": text, "t": round(s, 3), "end": round(e, 3), "color": color, "scale": scale})
        i += 1
    # hold each caption until the next one (unless the gap is long)
    for k in range(len(caps) - 1):
        gap = caps[k + 1]["t"] - caps[k]["end"]
        if gap <= C["gap_blank"]:
            caps[k]["end"] = caps[k + 1]["t"]
    return caps


def srt(caps):
    def ts(t):
        h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    out = []
    for i, c in enumerate(caps, 1):
        out.append(f"{i}\n{ts(c['t'])} --> {ts(c['end'])}\n{c['text']}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("-o", "--out", default="timing")
    ap.add_argument("--script")
    ap.add_argument("--red", default="")
    ap.add_argument("--big", default="")
    a = ap.parse_args()
    words = json.load(open(a.words, encoding="utf-8"))
    r1, b1 = markup_from_script(a.script)
    red = r1 | set(x.strip() for x in a.red.split(",") if x.strip())
    big = b1 | set(x.strip() for x in a.big.split(",") if x.strip())
    caps = build(words, red, big)
    os.makedirs(a.out, exist_ok=True)
    json.dump(caps, open(os.path.join(a.out, "captions.json"), "w", encoding="utf-8"), indent=0)
    open(os.path.join(a.out, "captions.srt"), "w", encoding="utf-8").write(srt(caps))
    nred = sum(1 for c in caps if c["color"] == "red")
    print(f"{len(caps)} captions ({nred} red, {sum(1 for c in caps if c['scale'] > 1)} big) from {len(words)} words")
    if nred > STYLE["edit"]["red_caption_words_per_video"][1]:
        print("note: the samples use at most 2 red words per video")


if __name__ == "__main__":
    main()
