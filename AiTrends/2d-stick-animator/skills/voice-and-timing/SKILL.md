---
name: voice-and-timing
description: Turn the approved story script into the timed narration of a glow stick-figure Short - the user's ElevenLabs API key and voice ID (stored on their computer, never in the plugin), a voice sample to approve, the full ElevenLabs voiceover, removal of long pauses to the references' one-breath pace, a check that the voiceover matches the length the user chose, Whisper word timestamps aligned to the script (ElevenLabs forced alignment as the fallback), and the one-word pop captions. Use when the user says "make the voiceover", "here is my ElevenLabs key / voice ID", "use my ElevenLabs voice", "change the voice", "here is my audio", "remove the pauses", "timestamp the narration", "make the captions", or when the make-story-short pipeline reaches the voice stage.
---

# Voice and timing

Input: `P/script/script_final.txt` (approved in write-story-script; never voice an unapproved script).
Outputs: `P/audio/voice.json` (voice ID + settings), `P/audio/voice.wav`, `P/timing/words.json`,
`P/timing/captions.json` (+ `.srt`). Tools are in `<workspace>/_kit/py/`; run them where the workspace lives (the
computer's shell, e.g. device_bash on a linked computer). P = `projects/<slug>`.

## 1. ElevenLabs key (the user's own)
- `python keys.py check`. If `elevenlabs` shows `-`, ask the user for their ElevenLabs API key (ElevenLabs ->
  profile -> API keys; a restricted key needs text to speech and voices, plus forced alignment for the fallback in
  step 5). Store it with `python keys.py set elevenlabs
  <key>`: it goes to `~/.2d_stick_animator/keys.json` on their computer. Never write a key into the plugin, a
  project file, a script, a log or a message, and never repeat it back.
- If the user has no ElevenLabs account, offer: their own recording (step 3b) or another TTS they have.

## 2. Voice ID
- Already set? `python eleven.py voice --show --project P` shows the project voice and the user's default. If
  there is a default, ask once: "Use <name> again?" (AskUserQuestion: yes / another voice ID / list my voices).
- Otherwise ask for the voice ID (ElevenLabs -> Voices -> the voice -> copy its ID; a Voice Library voice must be
  added to My Voices first), or list the account's voices with `python eleven.py voices` and suggest a deep,
  clear, energetic male storyteller (the references: ~120 Hz, fast).
- Check and set it: `python eleven.py voice <voice_id> --project P --save` (prints the voice name; `--save` makes it
  the user's default for future projects - in their settings file, not the plugin).

## 3. Narration
a. **Sample first** (2 sentences, few credits): `python eleven.py tts P/script/script_final.txt -o
   P/audio/voice_sample.wav --project P --first 2`. Send it to the user (SendUserFile) and ask: approve / faster /
   calmer / more energy / another voice. Adjust with `--speed` (1.05-1.2), `--stability` (0.3-0.5, lower = more
   expressive) and `--style` (0.2-0.4); a new voice -> step 2. Repeat until approved.
b. **Full voiceover**: `python eleven.py tts P/script/script_final.txt -o P/audio/voice_raw.wav --project P`
   (the approved settings are kept in `P/audio/voice.json`). Caption marks and any TOPIC/TITLE or SCRIPT: label
   lines are stripped before speaking.
   **The user's own file instead**: copy it to `P/audio/voice_raw.wav` (any format; ffmpeg converts).

## 4. Tighten to the house pace
`python tighten.py P/audio/voice_raw.wav -o P/audio/voice.wav --max-pause 0.18 --keep 0.09 --lead 0`
Target 205-230 wpm, first word at 0.00 s. If it is still slow (< 200 wpm), regenerate with speed 1.15 rather
than time-stretching. Tell the user the before/after duration.

## 5. Word timestamps
`python transcribe.py P/audio/voice.wav -o P/timing --script P/script/script_final.txt --model small.en`
- Whisper (faster-whisper) runs on the computer (first run downloads the model); `--model medium.en` for hard
  names. Read `P/timing/align_report.txt`: every difference should be spelling or numbers, not missing audio. If
  words are missing from the audio, regenerate that line.
- `--engine eleven` uses ElevenLabs forced alignment instead (exact script words, uses the user's key): when
  faster-whisper is not installed or Whisper mishears many words. `--engine auto` (default) falls back to it.

## 6. Match the chosen length
`python story_length.py P --check-voice` compares the real voiceover with the length the user chose
(`P/script/length.json`):
- within 8%: done.
- a speed change covers it (0.9-1.2): it prints the speed - regenerate with that `--speed`, tighten and time again
  (no new approval needed; tell the user).
- more than the voice speed can cover: tell the user the real length and how many words the script would need
  (+/-), and ask: keep this length (the default), or adjust the approved script (back to write-story-script A5).
`transcribe.py` stores the measured pace with the voice (`voice.json`, and the user's default voice), so the next
story's word target is computed for the voice that will read it.

## 7. Captions
`python captions.py P/timing/words.json -o P/timing --script P/script/script_final.txt`
(`**word**` -> red, `*word*` -> big; or `--red w1,w2 --big w3`). Check the count of red words (0-2).

## Done when
voice.wav exists at the house pace and the chosen length (or the user accepted the difference), words.json covers every script word with sane times (monotonic, no zero
lengths), captions.json exists; note the voice name, chosen and real duration and wpm in PROJECT_STATE.md, then go straight on
to the edit (plan-shots) - no extra checkpoint unless the user asked for one.
