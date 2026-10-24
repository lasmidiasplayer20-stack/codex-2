"""Check a story script against the channel's story rules (skills/write-story-script/references/story-prompt.md).

  python story_check.py P/script/script_final.txt [--title "HE SNEAKED INTO AN ASYLUM! #shorts"] [--json]
  python story_check.py draft.txt --seconds 90                # before a project exists: check against a chosen length
  python story_check.py P/script/script_user.txt --info      # the user's own story: report only, nothing fails
  python story_check.py stories/batch.md --batch             # every TOPIC/TITLE + SCRIPT pair in a batch file

The file may hold just the script, or "TOPIC/TITLE: ..." and "SCRIPT:" lines around it. Caption markup
(**red**, *big*) and [notes] are ignored for the counts.
Length: the user's chosen length - P/script/length.json (story_length.py) for a file in a project's script/ folder,
else --seconds (default 60 s). The word target is seconds x words-per-minute / 60 (see story_length.py).
Errors (exit code 1): more than 20% off the target words, fewer sentences than the length needs, not starting with When/After/During, an
introduction opener, dialogue (quotation marks), more than one paragraph, questions, the viewer addressed.
Warnings: more than 8% off the target words (the video would miss the chosen length by more than ~5 s), sentences over 25 words, a last line over 12 words, connectors used more
than 3 times, repeated sentence openings, opinions or morals, spellings a voice misreads, sentences with nothing the
animation library knows how to show, a title that is not a short ALL CAPS headline.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import story_length as SL  # noqa: E402

WPM_RANGE = (206, 229)
MAX_SENT_WORDS = 25
MAX_LAST_WORDS = 12

OPENERS = ("when", "after", "during")
INTRO = re.compile(r"^(there\s+(once\s+)?(was|were|lived)|once\s+upon|a\s+(man|woman|guy|girl|boy)\s+named|did\s+you\s+know|"
                   r"have\s+you\s+ever|imagine|in\s+this\s+video|today|this\s+is\s+the\s+story|meet\b)", re.I)
CONNECTORS = ["right away", "instantly", "immediately", "the problem was", "problem was", "because of that", "so",
              "then", "meanwhile", "at that moment", "right then", "luckily", "unfortunately", "knowing this",
              "but when", "but", "that's when", "thanks to this", "still", "soon", "eventually", "in the end",
              "as soon as", "just as", "a week later", "after", "when"]
MORAL = re.compile(r"\b(lesson|moral|teaches us|we should|we all|never forget|remember that|goes to show|"
                   r"in my opinion|i think|sadly enough)\b", re.I)
FIRST_PERSON = re.compile(r"\b(I|we|our|us)\b")
VIEWER = re.compile(r"\b(you|your|you're|yourself|you'll|you'd)\b", re.I)
QUOTES = re.compile(r"[\"“”„«»]|(?:^|\s)'[A-Z][^']{3,}'")
MISREAD = re.compile(r"(%|&|#|\bDr\.|\bMr\.|\bMrs\.|\bSt\.|\bNo\.\s*\d|\bvs\.?\b|\betc\.?\b|\be\.g\.|\bi\.e\.|\bapprox\.?\b|\bkm\b|\bkg\b|\bmph\b)")
ABBR = ["Dr.", "Mr.", "Mrs.", "Ms.", "St.", "Jr.", "Sr.", "U.S.", "U.K.", "No.", "vs.", "e.g.", "i.e.", "etc.", "approx."]
COMMON_CAPS = {"I", "World", "War", "II", "God", "Christmas", "Easter", "Monday", "Tuesday", "Wednesday", "Thursday",
               "Friday", "Saturday", "Sunday", "January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December", "TV", "CEO", "FBI", "CIA", "KGB", "NASA"}


def strip_markup(text):
    text = re.sub(r"\[[^\]]*\]", " ", text)
    return text.replace("**", "").replace("*", "")


def parse(raw):
    """-> list of (title, script_text)"""
    if "TOPIC/TITLE:" not in raw.upper():
        body = re.sub(r"^\s*SCRIPT:\s*", "", raw.strip(), flags=re.I)
        return [(None, body)]
    out = []
    parts = re.split(r"(?im)^\s*(?:\d+[.)]\s*)?TOPIC/TITLE:\s*", raw)
    for p in parts[1:]:
        lines = p.strip().split("\n", 1)
        title = lines[0].strip()
        rest = lines[1] if len(lines) > 1 else ""
        rest = re.sub(r"(?is)^\s*SCRIPT:\s*", "", rest.strip())
        # drop anything after the paragraph that is clearly not script (a stats block, a separator)
        rest = re.split(r"(?m)^\s*(?:-{3,}|={3,}|words:|\(TRUE|\(LEGEND|\(FICTION)", rest)[0]
        out.append((title, rest.strip()))
    return out


def sentences(text):
    t = " ".join(text.split())
    for a in ABBR:
        t = t.replace(a, a.replace(".", "․"))
    parts = re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"”')]))\s+(?=[\"“'(]?[A-Z0-9$])", t)
    return [p.replace("․", ".").strip() for p in parts if p.strip()]


def words_of(s):
    return [w for w in s.split() if re.search(r"[A-Za-z0-9]", w)]


def showables(sent):
    """what in this sentence the animation library knows how to show: [(kind, lemma, how)]"""
    try:
        import coverage as CV
    except Exception:
        return None
    toks = [{"w": w, "s": 0.0} for w in sent.split()]
    found = []
    for text, _, _ in CV.words_with_phrases(toks):
        for kind, lem, _, how in CV.readings(text):
            found.append((kind, lem, how))
    return found


def check_title(title):
    issues = []
    if not title:
        return issues
    head = re.split(r"\s#", title)[0].strip()
    letters = re.sub(r"[^A-Za-z]", "", head)
    if letters and letters != letters.upper():
        issues.append("title is not ALL CAPS")
    n = len(words_of(head))
    if n < 2 or n > 7:
        issues.append(f"title headline has {n} words (2-6 reads best)")
    if "#shorts" not in title.lower():
        issues.append("title has no tags (#shorts #animation #curiosities)")
    return issues


def check(text, title=None, info=False, t=None):
    t = t or SL.targets(SL.DEFAULT_SECONDS)
    errors, warns, notes = [], [], []
    raw = text.strip()
    clean = strip_markup(raw)
    red = len(re.findall(r"\*\*[^*]+\*\*", raw))
    big = len(re.findall(r"(?<!\*)\*[^*]+\*(?!\*)", raw))
    if re.search(r"\n\s*\n", clean.strip()):
        errors.append("the script is more than one paragraph (write one continuous paragraph)")
    elif len([l for l in clean.strip().splitlines() if l.strip()]) > 1:
        notes.append("line breaks inside the paragraph (they are joined for the voice)")
    sents = sentences(clean)
    nwords = len(words_of(clean))
    secs = nwords / t["wpm"] * 60
    lo, hi = nwords / WPM_RANGE[1] * 60, nwords / WPM_RANGE[0] * 60
    want = f"a {t['seconds']} s story needs ~{t['target_words']} words"

    wl, wh = t["words_limit"]
    if nwords < wl:
        errors.append(f"{nwords} words (~{secs:.0f} s) - {want} (at least {wl}): extend the middle with failed "
                      "attempts, mistakes and consequences")
    elif nwords > wh:
        errors.append(f"{nwords} words (~{secs:.0f} s) - {want} (at most {wh}): cut repeated beats, merge steps")
    elif not t["words"][0] <= nwords <= t["words"][1]:
        warns.append(f"{nwords} words (~{secs:.0f} s) - {want} (aim {t['words'][0]}-{t['words'][1]})")
    s_lo, s_hi = t["sentences"]
    if len(sents) < s_lo:
        errors.append(f"{len(sents)} sentences - a {t['seconds']} s story needs at least {s_lo} (split long sentences, "
                      "add cause-and-effect steps)")
    elif len(sents) > s_hi:
        warns.append(f"{len(sents)} sentences - more than {s_hi} for {t['seconds']} s (sentences are getting very short)")

    first = sents[0] if sents else ""
    fw = re.sub(r"[^a-z]", "", first.split()[0].lower()) if first.split() else ""
    if INTRO.search(first):
        errors.append(f"introduction opener: \"{first[:60]}...\" (drop the viewer into the action)")
    if fw not in OPENERS:
        errors.append(f"first word is \"{first.split()[0] if first.split() else ''}\" - start with When, After or During")
    if QUOTES.search(clean):
        errors.append("dialogue / quotation marks found - use reported speech without quotes")
    if "?" in clean:
        errors.append("a question - the narrator never asks questions")
    m = VIEWER.search(clean)
    if m:
        errors.append(f"the viewer is addressed (\"{m.group(0)}\") - third person only")
    if FIRST_PERSON.search(clean):
        warns.append(f"first person (\"{FIRST_PERSON.search(clean).group(0)}\") - the narrator stays outside the story")
    mm = MORAL.search(clean)
    if mm:
        warns.append(f"opinion or moral (\"{mm.group(0)}\") - just narrate what happened")
    for mm in MISREAD.finditer(clean):
        warns.append(f"\"{mm.group(0).strip()}\" - write it the way it is spoken")

    starts, openings = {}, {}
    for i, s in enumerate(sents, 1):
        n = len(words_of(s))
        if n > MAX_SENT_WORDS:
            warns.append(f"sentence {i} has {n} words (max {MAX_SENT_WORDS}): \"{s[:70]}...\"")
        elif n < 4:
            notes.append(f"sentence {i} is very short ({n} words): \"{s}\"")
        low = s.lower()
        for c in CONNECTORS:
            if re.match(re.escape(c) + r"\b", low):
                starts[c] = starts.get(c, 0) + 1
                break
        op = " ".join(re.sub(r"[^a-z' ]", "", low).split()[:2])
        openings[op] = openings.get(op, 0) + 1
    cap = max(3, round(3 * t["seconds"] / 60))
    for c, k in starts.items():
        if k > cap and c not in ("when", "after"):
            warns.append(f"\"{c.capitalize()}\" opens {k} sentences (max {cap} for {t['seconds']} s) - vary the connectors")
    for op, k in openings.items():
        if k > cap and op:
            warns.append(f"{k} sentences start with \"{op}\" - vary the openings")
    if sents:
        last = sents[-1]
        if len(words_of(last)) > MAX_LAST_WORDS:
            warns.append(f"last sentence has {len(words_of(last))} words - land the twist in {MAX_LAST_WORDS} or fewer")

    caps = []
    for s in sents:
        ws = s.split()
        for w in ws[1:]:
            c = re.sub(r"[^A-Za-z']", "", w)
            if c and c[0].isupper() and c not in COMMON_CAPS and not c.isupper() and c not in caps:
                caps.append(c)
    if caps:
        notes.append("capitalized words (historical people and places are fine, private people's names are not): "
                     + ", ".join(caps))

    shown, blind = [], []
    for i, s in enumerate(sents, 1):
        f = showables(s)
        if f is None:
            break
        if not f:
            blind.append(i)
        for kind, lem, how in f:
            if kind != "person" and not how.startswith("kit icon") and lem not in shown:
                shown.append(lem)
    if blind:
        warns.append("no drawable person/object/action the library knows in sentence(s) "
                     + ", ".join(map(str, blind)) + " - check each one is a picture (who does what to what)")
    if shown:
        notes.append("must be shown on screen (objects and actions): " + ", ".join(shown))
    if red > 2:
        warns.append(f"{red} **red** caption words (0-2)")
    if big > 3:
        warns.append(f"{big} *big* caption words (1-3)")
    for issue in check_title(title):
        warns.append(issue)

    if info:
        notes = [f"(would fail) {e}" for e in errors] + [f"(warning) {w}" for w in warns] + notes
        errors, warns = [], []
    return {"title": title, "length": t, "words": nwords, "sentences": len(sents), "seconds": round(secs, 1),
            "seconds_range": [round(lo, 1), round(hi, 1)], "first": first, "last": sents[-1] if sents else "",
            "red": red, "big": big, "errors": errors, "warnings": warns, "notes": notes,
            "pass": not errors}


def report(r, name):
    out = [f"STORY CHECK  {name}"]
    if r["title"]:
        out.append(f"  title      {r['title']}")
    t = r["length"]
    out.append(f"  length     {t['seconds']} s chosen -> target {t['target_words']} words at {t['wpm']:.0f} wpm "
               f"(aim {t['words'][0]}-{t['words'][1]}, limits {t['words_limit'][0]}-{t['words_limit'][1]})")
    out.append(f"  words      {r['words']}   sentences {r['sentences']} ({t['sentences'][0]}-{t['sentences'][1]})   ~{r['seconds']:.0f} s "
               f"({r['seconds_range'][0]:.0f}-{r['seconds_range'][1]:.0f} s)")
    out.append(f"  last line  {r['last']}")
    for head, key in (("ERRORS", "errors"), ("WARNINGS", "warnings"), ("NOTES", "notes")):
        if r[key]:
            out.append(f"{head} ({len(r[key])})")
            out += [f"  - {x}" for x in r[key]]
    out.append("RESULT: " + ("PASS" if r["pass"] else f"FAIL ({len(r['errors'])} errors)"))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="script file, or - for stdin")
    ap.add_argument("--title")
    ap.add_argument("--info", action="store_true", help="the user's own story: report only, never fail")
    ap.add_argument("--batch", action="store_true", help="check every TOPIC/TITLE + SCRIPT pair in the file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--seconds", help="the chosen length (60, 90s, 2:30); default: the project's length.json, else 60")
    ap.add_argument("--wpm", type=float, help="narration pace override")
    a = ap.parse_args()
    P = None
    if a.file != "-":
        d = os.path.dirname(os.path.abspath(a.file))
        if os.path.basename(d) == "script":
            P = os.path.dirname(d)
    if a.seconds:
        tg = SL.targets(SL.parse_seconds(a.seconds), a.wpm, P)
    else:
        tg = (SL.load(P) if P else None) or SL.targets(SL.DEFAULT_SECONDS, a.wpm, P)
    raw = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    items = parse(raw)
    if not a.batch:
        items = items[:1]
    if a.title and items:
        items[0] = (a.title, items[0][1])
    if not a.title and items and items[0][0] is None and a.file != "-":
        tf = os.path.join(os.path.dirname(os.path.abspath(a.file)), "title.txt")
        if os.path.exists(tf):
            items[0] = (open(tf, encoding="utf-8").read().strip(), items[0][1])
    results = [check(t, title, a.info, tg) for title, t in items]
    if a.json:
        print(json.dumps(results if a.batch else results[0], indent=1))
    else:
        for i, r in enumerate(results, 1):
            print(report(r, a.file if len(results) == 1 else f"{a.file} #{i}"))
            if len(results) > 1:
                print()
    sys.exit(0 if all(r["pass"] for r in results) else 1)


if __name__ == "__main__":
    main()
