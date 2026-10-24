---
name: write-story-script
description: Start every glow stick-figure Short with its story - present 10 story concepts (or take the user's own pasted story), write the full script for the chosen concept with the channel's story prompt (When/After/During opener, short cause-and-effect sentences, no names or dialogue, ironic twist) at the length the user chooses - the word and sentence targets follow from the chosen duration and the voice's pace - let the user edit it, and save the approved script and title. Use when the user wants story ideas or concepts, a script written, rewritten, shortened, checked or approved, a batch of scripts, a different length ("make it 90 seconds", "a 30 second version", "make it 2 minutes"), or says "here is my story/script", "find me a story", "write the script about...", or when the make-story-short pipeline reaches the story stage.
---

# Write the story script

Outputs in `P/script/` (P = `projects/<slug>`, created once the story is chosen): `concepts.md` (if generated), `research.md`, `script_final.txt` (the
approved script, the only file the voice stage reads) and `title.txt`.
The story rules are in `references/story-prompt.md` (the channel's script prompt, refined): read it before
writing concepts or a script and follow it exactly. `references/script-formula.md` adds the measured connectors,
phrase bank and title style of the reference videos. Check every script with `python _kit/py/story_check.py`;
`python _kit/py/story_length.py` turns the chosen length into the word, sentence and beat targets.

## 0. Ask where the story comes from and how long it should be
Unless the user already said (the pipeline's first questions usually cover both), ask with AskUserQuestion -
one question for the source and, unless they paste their own story, one for the length.
Source:
- **Show me story concepts (Recommended)** - 10 concepts to choose from (path A).
- **Concepts on a theme** - same, limited to the theme they type (war, prisons, medicine, survival...).
- **I'll paste my own story** - path B: their text is used as written.
- **Write it from my topic or article** - path A from step A3 with their topic.
Length: **60 seconds (Recommended, like the samples)** / **30-45 seconds** / **90 seconds** / **2-3 minutes**; they
can type any length in Other ("75 seconds", "1:40"). Ask for the exact figure if they pick a range. Then print the
targets: `python _kit/py/story_length.py --seconds <length>` (words, sentences, beats, shots, locations) and tell
the user the word target in one line ("60 s -> about 222 words"). Over 3 minutes is no longer a YouTube Short -
say so. A pasted story needs no length question: its length comes from its words.

## Path A - concepts, script, the user's changes
**A1. Concepts.** Pick stories that carry the chosen length (a long video needs a documented chain of many
events; a 30 s one a single sharp reversal). List the titles already made (`projects/*/script/title.txt`) so nothing repeats. Search the web
for strong candidates (several searches in parallel, different categories and eras), keep only stories that pass
the topic, truth and safety rules, and write 10 concepts in the prompt's mode-A format (TITLE, HOOK, TWIST, TYPE
with source, cast, places), strongest first. Save them to `stories/concepts_<YYYY-MM-DD>.md` in the workspace (no project exists yet).

**A2. The user picks.** Send the numbered list (SendUserMessage), then ask with AskUserQuestion: the 3 strongest as
options plus "10 new concepts"; they can type any number, combine two, or give their own angle in Other.

**A3. Make the project and research the chosen story.** `python _kit/py/new_project.py "<TITLE + tags>"` (the
slug ignores the tags and the title is written to `script/title.txt`; skip if the project already exists), copy
the concepts file to `P/script/concepts.md`, then research: 2-6 sources (WebSearch/WebFetch). Write `P/script/research.md`: what happened step
by step, numbers (days, money, counts), places, what people, clothes, buildings and objects looked like in that
era (the asset stage draws from this), what is disputed, and the links. Record the length:
`python _kit/py/story_length.py P --seconds <length>` (writes `P/script/length.json`, which story_check, the voice
stage and the edit read).

**A4. Write the script** in the prompt's mode-B format at the chosen length: one paragraph, the target words
and sentence range from `story_length.py` (60 s: ~222 words, 18-25 sentences), first word When/After/During,
cause-and-effect chain with the beats in place (problem before 40%, turn after 75%), no names or dialogue, twist
in the last 12 words or fewer, every sentence a picture. Then:
`python _kit/py/story_check.py P/script/draft.txt --title "<TITLE>"` (it reads the project's length) and fix every error and every warning that is
real (a sentence the library does not recognise may still be a clear picture - judge it). Re-check until PASS.
Check every fact in the script against `research.md`; hedge anything disputed.

**A5. Show it and let the user change it.** Show the TOPIC/TITLE, the script, and one stats line (words,
sentences, ~seconds against the chosen length, TYPE + sources). Ask with AskUserQuestion:
- **Approve** - go to step 1 of the save.
- **I'll make changes** - they paste their edited script or describe the changes. A pasted edit is used word for
  word: run `story_check.py --info`, tell them anything that would break production (dialogue in quotes, a question)
  and how far its length now is from the chosen one, and only change it if they agree. Described changes: apply them, re-check, show again.
- **Rewrite it** (another angle, more tension, a different twist) - rewrite, re-check, show again.
- **Change the length** - record the new length (`story_length.py P --seconds <new>`), then lengthen it (more
  cause-and-effect steps, failed attempts, consequences) or shorten it (keep the essential chain), re-check, show
  again.
- **Pick another concept** - back to A2.
Repeat until they approve. Never voice a script the user has not approved.

## Path B - the user's own story
- Make the project with their title (or a working title): `python _kit/py/new_project.py "<TITLE>"`.
- Save their text exactly as written to `P/script/script_user.txt` and `P/script/script_final.txt` (only lift out a
  "TOPIC/TITLE:" line into `title.txt` and drop a "SCRIPT:" label). Do not rewrite it, tighten it or "improve"
  the style, and skip the edit round - it is already theirs.
- Record its length from its words: `python _kit/py/story_length.py P --from-script`. If they also named a length
  and the story is far from it, say so and ask whether to keep their text as it is (the default) or adjust it.
- Run `python _kit/py/story_check.py P/script/script_user.txt --info` and tell them only the words, the estimated
  length, and anything that breaks production (dialogue the single narrator would have to voice, symbols a voice
  misreads, over 3 minutes = not a Short). Ask before changing anything.
- No title given: write one in the house style (ALL CAPS, 2-6 words + tags) and show it; they can change it.
- Research only what the pictures need (era, uniforms, places, objects) into `research.md`; never change their
  text because of it.

## Save (both paths)
1. Caption markup: mark 0-2 emotional peak words `**word**` (red captions) and 1-3 key nouns `*word*` (big
   captions) in `script_final.txt`. The words do not change; the voice tool strips the marks.
2. `script/title.txt` = the TOPIC/TITLE line (headline + tags).
3. Note the source path (A or B), the chosen length, word count and estimated length in `PROJECT_STATE.md`, then continue with
   voice-and-timing.

## Batch mode (only when asked)
"Write 10 scripts", "give me a batch": ask the length once (all 10 share it), write 10 TOPIC/TITLE + SCRIPT pairs
in mode C, check them all with `story_check.py stories/batch_<date>.md --batch --seconds <length>`, fix until every one passes, and save the file in the workspace's
`stories/` folder. When the user picks one to produce, it becomes a project's `script_final.txt` after their
approval (path A from A5).
