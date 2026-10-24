"""Word-level timestamps for the narration, aligned to the approved script.

usage:
  python transcribe.py PROJECT/audio/voice.wav -o PROJECT/timing --script PROJECT/script/script_final.txt [--model small.en]
         [--engine auto|whisper|eleven]

engines: whisper = faster-whisper on this computer (default, free); eleven = ElevenLabs forced alignment of the
approved script to the audio (needs the user's ElevenLabs key and --script; exact words, used when faster-whisper
is not installed or Whisper mishears many words). auto = whisper, else eleven.

writes timing/words.json  [{"w": "When", "s": 0.00, "e": 0.18}, ...]   (script spelling and punctuation)
       timing/words_whisper.json (raw)
       timing/align_report.txt  (words whisper heard differently; check names/numbers)
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ra_common import strip_labels  # noqa: E402


def load_audio(path, sr=16000):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def whisper_words(path, model_name, device="auto"):
    from faster_whisper import WhisperModel
    try:
        model = WhisperModel(model_name, device=device, compute_type="int8")
    except Exception:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
    audio = load_audio(path)
    segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=False, language="en",
                               condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words or []:
            out.append({"w": w.word.strip(), "s": round(float(w.start), 3), "e": round(float(w.end), 3)})
    return out


def eleven_words(path, text):
    """ElevenLabs forced alignment: the script's words with their times in the audio"""
    import requests
    from ra_common import get_key
    key = get_key("elevenlabs")
    with open(path, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/forced-alignment", headers={"xi-api-key": key},
                          files={"file": (os.path.basename(path), f, "audio/wav")}, data={"text": text}, timeout=600)
    if r.status_code != 200:
        sys.exit(f"ElevenLabs forced alignment failed {r.status_code}: {r.text[:300]}")
    out = []
    for w in r.json().get("words", []):
        t = (w.get("text") or "").strip()
        if t:
            out.append({"w": t, "s": round(float(w["start"]), 3), "e": round(float(w["end"]), 3)})
    return out


def pick_engine(want, have_script):
    if want in ("auto", "whisper"):
        try:
            import faster_whisper  # noqa: F401
            return "whisper"
        except ImportError:
            if want == "whisper":
                sys.exit("faster-whisper is not installed: pip install faster-whisper (or use --engine eleven)")
    from ra_common import get_key
    if have_script and get_key("elevenlabs", required=False):
        return "eleven"
    sys.exit("No timing engine: install faster-whisper (setup-studio), or give --script and store an ElevenLabs key "
             "for --engine eleven.")


def norm(w):
    w = w.lower().replace("’", "'")
    w = re.sub(r"[^a-z0-9']", "", w)
    return w


NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
       "8": "eight", "9": "nine", "10": "ten", "11": "eleven", "12": "twelve", "18": "eighteen", "20": "twenty",
       "30": "thirty", "40": "forty", "50": "fifty", "100": "hundred"}


def script_tokens(text):
    text = strip_labels(text)
    text = re.sub(r"\[[^\]]*\]", " ", text)          # stage notes
    text = text.replace("**", "").replace("*", "")    # emphasis markup
    return [t for t in re.split(r"\s+", text.strip()) if t]


def align(script_words, heard):
    a = [norm(w) for w in script_words]
    b = [norm(w["w"]) for w in heard]
    b2 = [NUM.get(x, x) for x in b]
    a2 = [NUM.get(x, x) for x in a]
    sm = difflib.SequenceMatcher(a=a2, b=b2, autojunk=False)
    out, report = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                h = heard[j1 + k]
                out.append({"w": script_words[i1 + k], "s": h["s"], "e": h["e"]})
        elif tag in ("replace", "delete"):
            # spread the script words over the heard span (or squeeze between neighbours)
            if j2 > j1:
                s0, e0 = heard[j1]["s"], heard[j2 - 1]["e"]
            else:
                s0 = out[-1]["e"] if out else 0.0
                e0 = heard[j1]["s"] if j1 < len(heard) else s0 + 0.25 * (i2 - i1)
                e0 = max(e0, s0 + 0.12 * (i2 - i1))
            n = i2 - i1
            lens = [max(1, len(norm(script_words[i]))) for i in range(i1, i2)]
            tot = float(sum(lens))
            t = s0
            for k, i in enumerate(range(i1, i2)):
                d = (e0 - s0) * lens[k] / tot
                out.append({"w": script_words[i], "s": round(t, 3), "e": round(t + d, 3)})
                t += d
            report.append(f"{tag}: script '{' '.join(script_words[i1:i2])}' <- heard '{' '.join(h['w'] for h in heard[j1:j2])}' at {s0:.2f}s")
        elif tag == "insert":
            report.append(f"extra (not in script): '{' '.join(h['w'] for h in heard[j1:j2])}' at {heard[j1]['s']:.2f}s")
    # monotonic clean-up
    for i in range(1, len(out)):
        if out[i]["s"] < out[i - 1]["s"]:
            out[i]["s"] = out[i - 1]["s"]
        if out[i]["e"] < out[i]["s"]:
            out[i]["e"] = out[i]["s"] + 0.05
    return out, report


def remember_pace(audio, wpm, n):
    """store the measured words per minute with the project's voice (and the user's default voice), so the next
    story's word target fits the voice that will read it (story_length.py)"""
    if n < 60 or not (120 <= wpm <= 320):
        return
    P = os.path.dirname(os.path.dirname(os.path.abspath(audio)))
    vf = os.path.join(P, "audio", "voice.json")
    if not os.path.exists(vf):
        return
    try:
        from ra_common import get_setting, read_json, set_setting, write_json
        rec = read_json(vf, {})
        rec["wpm"] = round(wpm, 1)
        write_json(vf, rec)
        d = get_setting("elevenlabs_voice") or {}
        if d.get("voice_id") and d.get("voice_id") == rec.get("voice_id"):
            k = int(d.get("wpm_n", 0))
            d["wpm"] = round((float(d.get("wpm", wpm)) * k + wpm) / (k + 1), 1) if k else round(wpm, 1)
            d["wpm_n"] = min(k + 1, 10)
            set_setting("elevenlabs_voice", d)
        print(f"pace {wpm:.0f} wpm saved with the voice (used for the next story's word target)")
    except Exception as e:  # never block timing over this
        print("pace not saved:", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("-o", "--out", default="timing")
    ap.add_argument("--script")
    ap.add_argument("--model", default="small.en", help="tiny.en/base.en/small.en/medium.en/large-v3")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--engine", choices=["auto", "whisper", "eleven"], default="auto")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    script = open(a.script, encoding="utf-8").read() if a.script and os.path.exists(a.script) else None
    engine = pick_engine(a.engine, bool(script))
    if engine == "whisper":
        heard = whisper_words(a.audio, a.model, a.device)
    else:
        heard = eleven_words(a.audio, " ".join(script_tokens(script)))
    json.dump(heard, open(os.path.join(a.out, f"words_{engine}.json"), "w", encoding="utf-8"), indent=0)
    if script:
        words, report = align(script_tokens(script), heard)
    else:
        words, report = heard, ["no script given: whisper spelling kept"]
    json.dump(words, open(os.path.join(a.out, "words.json"), "w", encoding="utf-8"), indent=0)
    with open(os.path.join(a.out, "align_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    dur = words[-1]["e"] - words[0]["s"] if words else 0
    wpm = len(words) / dur * 60 if dur else 0
    print(f"{len(words)} words, {dur:.1f}s speech, {wpm:.0f} wpm, first word at {words[0]['s'] if words else 0:.2f}s")
    remember_pace(a.audio, wpm, len(words))
    print(f"engine {engine}; alignment notes: {len(report)} (see {os.path.join(a.out, 'align_report.txt')})")
    if engine == "whisper" and script and len(report) > max(4, 0.08 * len(words)):
        print("many words differ from the script: read align_report.txt; if audio is not missing, re-run with "
              "--model medium.en or --engine eleven (exact alignment to the script)")


if __name__ == "__main__":
    main()
