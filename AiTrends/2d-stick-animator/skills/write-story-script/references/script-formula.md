# Script formula (measured on the seven references)

`story-prompt.md` (the channel's script prompt) sets the rules for new scripts: When/After/During opener,
short sentences at the word count of the length the user chose (60 s: ~222 words, 18-25 sentences), no names or
dialogue. This file adds what was measured
on the reference videos: pacing, the connector skeleton, the phrase bank and the title style. Where the two
differ (the references are all ~55 s and use fewer, longer sentences), follow story-prompt.md.

| measure | references |
|---|---|
| words | 188-230 (median ~200) |
| duration | 50.8-60.7 s |
| speaking rate | 206-229 wpm |
| first word | at 0.00 s - the hook IS the opening |
| sentences | 8-14, mostly 12-25 words, chained with "and" |
| tense / person | past tense, third person, anonymous roles ("this guy", "these three accused women") |

## Skeleton
1. **Hook (0-5 s, one sentence):** `When this [person] [did/suffered an unusual thing], [what happened next / the
   stakes].` Starts with "When this...", "When these...". Names a concrete, visual situation.
   - When this homeless man ate rat poison and accidentally died, two soldiers found his body and decided to use
     it for something useful.
   - When this guy carried a heavy briefcase up to the roof of a building, he opened it and pulled out several
     bundles of cash...
2. **First action (5-15 s):** "Right away, ..." / "Instantly, ..." / "Immediately, ..." - the protagonist's plan
   or reaction, in physical steps (bathed him, took a photo, dressed him, threw him in the sea).
3. **Complication (~15-25 s):** "The problem was (that) ..." / "Problem was, ..." - the obstacle or the twist of
   circumstance (it was World War II; the guards thought he was already out; the doctors read normal behaviour
   as insanity).
4. **Escalation (25-40 s):** "Because of that, ..." / "Meanwhile, ..." / "At that moment, ..." / "Luckily, ..."
   / "Knowing this, ..." / "Then, ..." - 2-4 sentences where things get bigger (more people, more days, more money).
5. **Turn (40-50 s):** "But when ..." / "That's when ..." / "Unfortunately, ..." / "Thanks to this, ..."
6. **Payoff (last 5 s):** the irony or the number, short and flat: "...all thanks to a dead homeless man." /
   "...he simply replied that he hadn't sent anyone." / "...each of the guards was forced to pay him $2,000." /
   "...the only passenger who survived was the man who had been shouting."

## Phrase bank (connectors the references use)
Right away, | Instantly, | Immediately, | The problem was (that) | Problem was, | But | But when | But since |
Because of that, | Meanwhile, | At that moment, | Right then, | Luckily, | Unfortunately, | Knowing this, |
Then, | Just as | As soon as | After X days, | Thanks to this, | That's because | That's when | So | and even |
just so | making / leaving / turning (participle chains: "...throwing them down onto a street full of people")

## Style rules
- Plain, spoken, slightly informal ("this guy", "crazy", "a huge army"). No academic words, no dates unless
  essential ("100 years later" instead of a year), no names of private people, no jokes that stop the flow.
- Concrete verbs and objects in every clause: picture-able (threw, grabbed, hid a float under her shirt, put
  stones inside her shoes, spat the pills out, slammed on the brakes).
- Escalating numbers: days (3 -> 30 -> 18), counts (40 new people, 40 million), money ($2,000).
- One idea per sentence part; repetition of the key noun is fine ("the virus... the virus").
- The narrator never addresses the viewer, never asks questions, no "did you know", no call to action.
- Hedge legends and theories ("supposedly", "people think") instead of stating them as fact.

## Title
ALL CAPS, 2-5 words, the core image or the irony: MONEY RAIN, THE BRAVE PASSENGER, HE BECAME A HERO.,
FORGOTTEN IN THE BASEMENT, HE SNEAKED INTO AN ASYLUM, HOW WITCHES SURVIVED THE PAST, HIV OUTBREAK THEORY.

## Checklist before approval
- [ ] `story_check.py` passes (words, sentences, opener, no dialogue/questions/viewer address)
- [ ] the first sentence sets up a concrete, visual situation with its stakes
- [ ] a "problem" beat before ~40% of the words; the turn after ~75%
- [ ] every sentence has a drawable person, object and action
- [ ] last line <= 12 words and lands the irony or the number
- [ ] 0-2 `**red**` words, 1-3 `*big*` words (added after approval)
- [ ] facts checked against research.md; hedged where uncertain
