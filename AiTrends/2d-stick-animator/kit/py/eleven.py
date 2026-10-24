"""ElevenLabs helpers: narration (TTS), sound effects and music for the short.

  python eleven.py voices                                   # list the voices on the user's account (id, name, labels)
  python eleven.py voice <voice_id> --project P [--save]    # check a voice ID, use it for this project (--save: default for this user)
  python eleven.py voice --show [--project P]               # which voice is set
  python eleven.py tts P/script/script_final.txt -o P/audio/voice_sample.wav --project P --first 2   # 2-sentence sample
  python eleven.py tts P/script/script_final.txt -o P/audio/voice_raw.wav --project P [--speed 1.1] [--stability 0.4]
  python eleven.py sfx "deep cinematic whoosh" -o audio/sfx/whoosh.wav --dur 1.2
  python eleven.py music "mysterious playful pizzicato..." -o audio/music.wav --dur 60

Key: the user's own key, ELEVENLABS_API_KEY or `python keys.py set elevenlabs <key>` (stored on their computer in
~/.2d_stick_animator/keys.json, never in a project or the plugin). Voice: --voice <id>, else the project's
audio/voice.json, else ELEVENLABS_VOICE_ID, else the user's saved default (~/.2d_stick_animator/settings.json).
Script markup (*word*, **word**, [notes]) is stripped before speaking. House narration: an energetic, fast male
storyteller (~120 Hz), 210-230 wpm, no long pauses -> speed 1.08-1.15, stability 0.35-0.45, similarity 0.8,
style 0.2-0.35, eleven_multilingual_v2.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

import requests

from ra_common import get_key, get_setting, set_setting, read_json, write_json, strip_labels

API = "https://api.elevenlabs.io"


def headers(key, accept="audio/mpeg"):
    return {"xi-api-key": key, "Content-Type": "application/json", "Accept": accept}


def to_wav(mp3_bytes, out, sr=48000):
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as t:
        t.write(mp3_bytes)
        tmp = t.name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", str(sr), "-ac", "2" if out.endswith("music.wav") else "1", out], check=True)
    try:
        os.unlink(tmp)
    except OSError:
        pass
    return out


def clean_script(text):
    text = strip_labels(text)
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = text.replace("**", "").replace("*", "")
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


HOUSE = {"model": "eleven_multilingual_v2", "speed": 1.1, "stability": 0.4, "similarity": 0.8, "style": 0.28}


def explain(r, what):
    """a readable reason for a failed call (never prints the key)"""
    try:
        d = r.json().get("detail")
    except ValueError:
        d = r.text[:300]
    status = d.get("status") if isinstance(d, dict) else ""
    msg = d.get("message") if isinstance(d, dict) else d
    if r.status_code == 401 and status in ("quota_exceeded", "insufficient_credits"):
        return f"{what}: the ElevenLabs account is out of credits ({msg})"
    if r.status_code == 401:
        return f"{what}: ElevenLabs rejected the key ({msg}) - check it and store it again with keys.py set elevenlabs <key>"
    if r.status_code in (400, 404) and ("voice" in str(msg).lower() or status == "voice_not_found"):
        return (f"{what}: voice not found on this account ({msg}) - a Voice Library voice must be added to "
                "My Voices first; then copy its ID")
    return f"{what} failed {r.status_code}: {msg}"


def voice_file(P):
    return os.path.join(P, "audio", "voice.json") if P else None


def resolve_voice(a):
    """voice id + settings: --voice, project audio/voice.json, ELEVENLABS_VOICE_ID, the user's saved default"""
    vf = voice_file(getattr(a, "project", None))
    proj = read_json(vf, {}) if vf and os.path.exists(vf) else {}
    user = get_setting("elevenlabs_voice") or {}
    vid = a.voice or proj.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID") or user.get("voice_id")
    if not vid:
        sys.exit("No voice ID. Ask the user for their ElevenLabs voice ID (Voices -> the voice -> copy its ID), or list "
                 "the account's voices with `python eleven.py voices`, then run `python eleven.py voice <id> --project P`.")
    st = dict(HOUSE)
    st.update({k: v for k, v in (proj.get("settings") or user.get("settings") or {}).items() if k in HOUSE})
    for k in HOUSE:
        v = getattr(a, k, None)
        if v is not None:
            st[k] = v
    return vid, st


def cmd_voices(a):
    key = get_key("elevenlabs")
    r = requests.get(API + "/v1/voices", headers={"xi-api-key": key}, timeout=60)
    if r.status_code != 200:
        sys.exit(explain(r, "listing voices"))
    for v in r.json().get("voices", []):
        lab = v.get("labels") or {}
        print(f"{v['voice_id']}  {v.get('name')}  [{', '.join(f'{k}={x}' for k, x in lab.items())}]")


def cmd_voice(a):
    if a.show or not a.voice_id:
        vf = voice_file(a.project)
        if vf and os.path.exists(vf):
            print("project voice:", json.dumps(read_json(vf)))
        print("user default :", json.dumps(get_setting("elevenlabs_voice")))
        return
    key = get_key("elevenlabs")
    r = requests.get(f"{API}/v1/voices/{a.voice_id}", headers={"xi-api-key": key}, timeout=60)
    if r.status_code != 200:
        sys.exit(explain(r, f"voice {a.voice_id}"))
    v = r.json()
    lab = v.get("labels") or {}
    rec = {"voice_id": a.voice_id, "name": v.get("name"), "labels": lab, "settings": dict(HOUSE)}
    print(f"voice ok: {v.get('name')}  [{', '.join(f'{k}={x}' for k, x in lab.items())}]  category={v.get('category')}")
    if a.project:
        vf = voice_file(a.project)
        old = read_json(vf, {}) if os.path.exists(vf) else {}
        if old.get("voice_id") == a.voice_id and old.get("settings"):
            rec["settings"] = old["settings"]
        os.makedirs(os.path.dirname(vf), exist_ok=True)
        write_json(vf, rec)
        print("project voice ->", vf)
    if a.save:
        print("user default ->", set_setting("elevenlabs_voice", {"voice_id": a.voice_id, "name": v.get("name"),
                                                                    "settings": rec["settings"]}))


def first_sentences(text, n):
    parts = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(parts[:n])


def cmd_tts(a):
    key = get_key("elevenlabs")
    vid, st = resolve_voice(a)
    text = clean_script(open(a.script, encoding="utf-8").read()) if os.path.exists(a.script) else a.script
    if a.first:
        text = first_sentences(text, a.first)
    body = {"text": text, "model_id": st["model"],
            "voice_settings": {"stability": st["stability"], "similarity_boost": st["similarity"], "style": st["style"],
                               "use_speaker_boost": True, "speed": st["speed"]}}
    url = f"{API}/v1/text-to-speech/{vid}?output_format=mp3_44100_192"
    r = requests.post(url, json=body, headers=headers(key), timeout=300)
    if r.status_code in (400, 422) and "speed" in r.text:
        body["voice_settings"].pop("speed", None)
        r = requests.post(url, json=body, headers=headers(key), timeout=300)
    if r.status_code != 200:
        sys.exit(explain(r, "ElevenLabs TTS"))
    to_wav(r.content, a.out)
    if a.project and not a.first:
        vf = voice_file(a.project)
        rec = read_json(vf, {}) if os.path.exists(vf) else {"voice_id": vid}
        rec["settings"] = st
        os.makedirs(os.path.dirname(vf), exist_ok=True)
        write_json(vf, rec)
    print(f"narration -> {a.out} ({len(text.split())} words, voice {vid}, speed {st['speed']}, stability {st['stability']})")


def cmd_sfx(a):
    key = get_key("elevenlabs")
    body = {"text": a.prompt, "duration_seconds": a.dur, "prompt_influence": a.influence}
    r = requests.post(API + "/v1/sound-generation", json=body, headers=headers(key), timeout=180)
    if r.status_code != 200:
        sys.exit(f"ElevenLabs SFX failed {r.status_code}: {r.text[:300]}")
    to_wav(r.content, a.out)
    print(f"sfx -> {a.out}")


def cmd_music(a):
    key = get_key("elevenlabs")
    body = {"prompt": a.prompt, "music_length_ms": int(a.dur * 1000), "model_id": "music_v1", "force_instrumental": True}
    r = requests.post(API + "/v1/music", json=body, headers=headers(key), timeout=600)
    if r.status_code in (400, 422):
        body.pop("force_instrumental", None)
        body.pop("model_id", None)
        r = requests.post(API + "/v1/music", json=body, headers=headers(key), timeout=600)
    if r.status_code != 200:
        sys.exit(f"ElevenLabs music failed {r.status_code}: {r.text[:300]} -- use music.py (procedural) or the user's own track")
    out = a.out if a.out.endswith(".wav") else a.out + ".wav"
    to_wav(r.content, out)
    print(f"music -> {out}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    v = sp.add_parser("voices"); v.set_defaults(fn=cmd_voices)
    vo = sp.add_parser("voice"); vo.add_argument("voice_id", nargs="?"); vo.add_argument("--project")
    vo.add_argument("--save", action="store_true", help="also make it this user's default voice")
    vo.add_argument("--show", action="store_true"); vo.set_defaults(fn=cmd_voice)
    t = sp.add_parser("tts"); t.add_argument("script"); t.add_argument("-o", "--out", required=True)
    t.add_argument("--project", help="project folder: voice from audio/voice.json, settings saved there")
    t.add_argument("--voice"); t.add_argument("--model")
    t.add_argument("--speed", type=float); t.add_argument("--stability", type=float)
    t.add_argument("--similarity", type=float); t.add_argument("--style", type=float)
    t.add_argument("--first", type=int, default=0, help="only the first N sentences (a voice sample)")
    t.set_defaults(fn=cmd_tts)
    s = sp.add_parser("sfx"); s.add_argument("prompt"); s.add_argument("-o", "--out", required=True)
    s.add_argument("--dur", type=float, default=1.0); s.add_argument("--influence", type=float, default=0.45); s.set_defaults(fn=cmd_sfx)
    m = sp.add_parser("music"); m.add_argument("prompt"); m.add_argument("-o", "--out", required=True)
    m.add_argument("--dur", type=float, default=60); m.set_defaults(fn=cmd_music)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
