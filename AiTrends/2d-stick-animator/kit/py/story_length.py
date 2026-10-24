"""The length the user chose for a story, and the word count that fills it.

  python story_length.py --seconds 90                # targets for a 90 s video (before a project exists)
  python story_length.py P --seconds 90              # record the chosen length -> P/script/length.json
  python story_length.py P --seconds 2:30            # minutes:seconds works too
  python story_length.py P --from-script             # the user's own story: its length comes from its words
  python story_length.py P                           # show the project's length and targets
  python story_length.py P --check-voice             # after the voiceover: real length vs chosen, what to change

Words = seconds x words-per-minute / 60. The rate is the channel's narration pace (222 wpm; the references run
206-229 after pause tightening) unless the user's voice was measured on an earlier project (transcribe.py stores the
measured rate with the voice), so the target fits the voice that will read it.
  target words +-8%       -> the script lands within ~5 s of the chosen length (story_check warns outside it)
  target words +-20%      -> hard limits (story_check fails outside them)
  sentences               -> one per 9-12 words (18-25 at 60 s), at least 6
  beats                   -> hook = sentence 1, problem before 40% of the words, turn after 75%, payoff = last line
  the edit                -> ~0.75 shots per second (median shot 1.3 s), one location per ~7 s (3-25)
A YouTube Short can be at most 3 minutes; longer lengths are allowed but flagged.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_common import get_setting, read_json, strip_labels, write_json  # noqa: E402

HOUSE_WPM = 222
DEFAULT_SECONDS = 60
MIN_SECONDS, SHORTS_MAX = 15, 180
TOL_WARN, TOL_FAIL = 0.08, 0.20


def parse_seconds(v):
    v = str(v).strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d+):(\d{1,2})", v)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(m|min|mins|minutes?)", v)
    if m:
        return round(float(m.group(1)) * 60)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(s|sec|secs|seconds?)?", v)
    if m:
        return round(float(m.group(1)))
    sys.exit(f"cannot read a length from '{v}' (use 60, 90s, 1.5min or 2:30)")


def voice_wpm(P=None):
    """measured words per minute of the voice that will read it: project voice, else the user's default voice"""
    if P:
        vf = os.path.join(P, "audio", "voice.json")
        if os.path.exists(vf):
            w = read_json(vf, {}).get("wpm")
            if w:
                return float(w), "this project's voice (measured)"
    d = get_setting("elevenlabs_voice") or {}
    if d.get("wpm"):
        return float(d["wpm"]), f"your voice {d.get('name') or d.get('voice_id')} (measured on earlier videos)"
    return float(HOUSE_WPM), "the channel's narration pace"


def targets(seconds, wpm=None, P=None):
    seconds = max(1, int(round(seconds)))
    src = "given"
    if wpm is None:
        wpm, src = voice_wpm(P)
    tw = round(seconds * wpm / 60)
    s_lo = max(6, round(tw / 12.3))
    s_hi = max(s_lo + 2, round(tw / 8.9))
    notes = []
    if seconds < MIN_SECONDS:
        notes.append(f"{seconds} s is very short: the story needs at least a hook, one problem and a twist")
    if seconds > SHORTS_MAX:
        notes.append(f"{seconds} s is longer than 3 minutes: it will not count as a YouTube Short")
    return {
        "seconds": seconds,
        "wpm": round(wpm, 1),
        "wpm_source": src,
        "target_words": tw,
        "words": [round(tw * (1 - TOL_WARN)), round(tw * (1 + TOL_WARN))],
        "words_limit": [round(tw * (1 - TOL_FAIL)), round(tw * (1 + TOL_FAIL))],
        "sentences": [s_lo, s_hi],
        "problem_by_word": round(tw * 0.40),
        "turn_after_word": round(tw * 0.75),
        "escalation_sentences": max(1, round((s_lo + s_hi) / 2 * 0.35)),
        "shots": [round(seconds * 0.55), round(seconds * 0.82)],
        "locations": [max(3, round(seconds / 9)), min(25, max(4, round(seconds / 5)))],
        "notes": notes,
    }


def length_file(P):
    return os.path.join(P, "script", "length.json")


def load(P):
    """the project's targets (recomputed with the current voice rate), or None"""
    f = length_file(P) if P else None
    if not f or not os.path.exists(f):
        return None
    d = read_json(f, {})
    if not d.get("seconds"):
        return None
    t = targets(d["seconds"], P=P)
    t["chosen_by"] = d.get("chosen_by", "user")
    return t


def save(P, t, chosen_by="user"):
    rec = dict(t)
    rec["chosen_by"] = chosen_by
    write_json(length_file(P), rec)
    return length_file(P)


def word_count(text):
    text = strip_labels(text)
    text = re.sub(r"\[[^\]]*\]", " ", text).replace("**", "").replace("*", "")
    return len([w for w in text.split() if re.search(r"[A-Za-z0-9]", w)])


def describe(t):
    lines = [f"length    {t['seconds']} s ({t['seconds'] // 60}:{t['seconds'] % 60:02d})",
             f"pace      {t['wpm']:.0f} words/min ({t['wpm_source']})",
             f"words     target {t['target_words']}  (aim {t['words'][0]}-{t['words'][1]}; limits {t['words_limit'][0]}-{t['words_limit'][1]})",
             f"sentences {t['sentences'][0]}-{t['sentences'][1]} (one per 9-12 words)",
             f"beats     problem before word ~{t['problem_by_word']}, turn after word ~{t['turn_after_word']}, "
             f"~{t['escalation_sentences']} escalation sentences, twist in the last line",
             f"the edit  ~{t['shots'][0]}-{t['shots'][1]} shots, {t['locations'][0]}-{t['locations'][1]} locations"]
    lines += [f"NOTE      {n}" for n in t["notes"]]
    return "\n".join(lines)


def check_voice(P):
    t = load(P)
    wf = os.path.join(P, "timing", "words.json")
    if not os.path.exists(wf):
        sys.exit("no timing/words.json yet - run transcribe.py first")
    words = read_json(wf)
    real = words[-1]["e"] if words else 0.0
    vf = os.path.join(P, "audio", "voice.json")
    speed = (read_json(vf, {}).get("settings") or {}).get("speed", 1.1) if os.path.exists(vf) else None
    print(f"voiceover {real:.1f} s, {len(words)} words, {len(words) / max(real, 0.1) * 60:.0f} wpm")
    if not t:
        print("no chosen length recorded (story_length.py P --seconds N)")
        return 0
    diff = (real - t["seconds"]) / t["seconds"]
    print(f"chosen    {t['seconds']} s -> {diff * 100:+.0f}%")
    if abs(diff) <= 0.08:
        print("OK: within 8% of the chosen length")
        return 0
    if speed:
        need = round(speed * real / t["seconds"], 2)
        if 0.9 <= need <= 1.2:
            print(f"FIX: regenerate with --speed {need} (now {speed}), then tighten and time again")
            return 1
    words_needed = round(len(words) * t["seconds"] / max(real, 0.1))
    print(f"FIX: the voice speed cannot cover {diff * 100:+.0f}% - the script needs about {words_needed} words "
          f"({words_needed - len(words):+d}); ask the user before changing the approved script, or accept the length")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--seconds", help="the chosen length: 60, 90s, 1.5min or 2:30")
    ap.add_argument("--wpm", type=float, help="override the narration pace")
    ap.add_argument("--from-script", action="store_true", help="length from P/script/script_final.txt (the user's own story)")
    ap.add_argument("--check-voice", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    P = a.project
    if a.check_voice:
        sys.exit(check_voice(P))
    if a.from_script:
        f = os.path.join(P, "script", "script_final.txt")
        n = word_count(open(f, encoding="utf-8").read())
        wpm = a.wpm or voice_wpm(P)[0]
        t = targets(n / wpm * 60, a.wpm, P)
        print("saved", save(P, t, "the user's own story"))
    elif a.seconds:
        t = targets(parse_seconds(a.seconds), a.wpm, P)
        if P:
            print("saved", save(P, t))
    else:
        t = load(P) if P else None
        if not t:
            t = targets(DEFAULT_SECONDS, a.wpm, P)
            t["notes"].append("no length chosen yet - showing the 60 s default")
    print(json.dumps(t, indent=1) if a.json else describe(t))


if __name__ == "__main__":
    main()
