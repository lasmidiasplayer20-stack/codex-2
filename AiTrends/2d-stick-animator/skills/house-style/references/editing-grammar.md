# Editing grammar (measured)

## Rhythm
| measure | value (7 references, 245 shots) |
|---|---|
| shots per video | 27-47 (median ~33 visual cuts; more if punch-ins are counted) |
| shot length | p10 0.71 s, p25 0.87 s, **median 1.3 s**, p75 1.97 s, p90 2.95 s, max ~4.8 s |
| words per shot | ~6 |
| cut placement | on a word onset (median 0.07 s from it); only 29% right after a comma/period |
| static shots | almost none: 97% of shots have camera motion |

Cut on the word that changes the picture - the noun that introduces a new thing, the verb of a new action, the
first word of a new clause ("and threw him", "| two soldiers found", "| The problem was"). Never cut so a shot
ends on "the", "a", "of", "to". A long sentence becomes 2-4 shots; a short punchline can be one shot.
`auto_plan.py` proposes cuts with these rules; adjust them so every shot has one clear visual idea.

## Camera (measured frame by frame; `"camera": "auto"` builds exactly this)
- **It never rests.** A new move every 0.45-1.25 s, landing on a word onset or an event (an icon/prop pop, a pose
  change, an action). 97% of shots move.
- **Every move is a jolt:** a fast ease-out snap (0.2-0.3 s, fast start, soft landing) to a new framing, then a slow
  linear drift (push-ins keep creeping in 5-10%, pull-outs keep easing out 2-4%) until the next jolt.
- **In and out alternate:** push in to 1.26-1.46x on whoever is acting (or halfway between the face and the object
  that just popped), then pull out to 1.02-1.1x on the whole group, and so on.
- **Shots open tight:** 1.36-1.5x on the main character's face; the first move is usually the pull-out.
- **Groups stay together:** characters acting together (talking, walking side by side, carrying something) are framed
  together; a single-face close-up only when one character reacts alone.
- **Walkers are tracked:** the focus slides with a character crossing the frame - and across a wider/taller
  location (`bg.world`) the camera travels with them, so a walk, chase or drag covers real ground.
- **Aim at the face where it really is:** seated, crouching, lying or toppling characters are framed on their head
  (auto camera solves the pose and the tilt), never on the empty spot where a standing head would be.
- Hand-made keys are still right for special moves: a punch-in (ease `cut`) on the key word, a pan across a crowd,
  a slow push on a sad ending. `camera` as a list of keys replaces the automatic plan for that shot.
- **Shake** on impacts, crashes, explosions, slams (amp 12-24 px, 0.3-0.6 s). **Roll** a few degrees for
  turbulence or falling.
- Zoom range 1.0-1.5 with `bg.scale` 1.06; for zoom < 1 set `bg.scale` >= 1.15.

## Transitions (into a shot)
- **Cut** for ~85-90% of shots.
- **Flash** (2 frames up to white, 5 down) for a jolt: "Problem was", a gunshot, a reveal.
- **Light leak** (orange/yellow blob sweeping) and **red wipe** (soft red bar sweeping) for chapter changes and
  time jumps - the war story stacked B&W archival insert -> white flash -> yellow/red leak -> red wipe -> B&W
  battlefield over two seconds on "Problem was, World War II was happening".
- **Glitch** (block dissolve) for digital/microscopic multiplication or a shocking twist.
- **B&W fade** out of a shot that ends badly.
- **Whip** (fast slide + blur) and **zoom blur** for speed and travel.
- **Fade to black** at the very end (2/7 references).
Special transitions: 2-6 per video. Whooshes only on these, never on plain cuts.

## Beat patterns
- **Sentence anatomy:** establish (who/where, pull-out) -> action (pose change, prop pops) -> consequence
  (reaction face, punch-in, icon, state change).
- **Literal pop-ins:** every concrete noun gets its picture on its word (rat, poison, bread, ID card, medals, life
  jacket, document, calendar, crown, rifles, briefcase, crate, cash, hot dogs, ambulance).
- **Reaction shots:** a close-up (h 1500-2300, crop:true) with a new face on the emotional word.
- **Escalation by multiplication:** the same prop pops 2-3 times in a row; crowds grow; bills keep falling.
- **Flashback/negative:** B&W or grey characters, then back to colour.
- **Location rotation:** cut between 2-3 places of the same scene (cell / door / corridor) to keep it moving.
- **Real insert for scale:** one real-looking clip when the story leaves the room (war, city, traffic, rescue).
- **Callback ending:** the final shot repeats the opening framing so the loop is seamless.

## Timing details
- Pose keys and icon pops land on the word onset (or 0-3 frames before). Pops last 9 frames.
- Captions change on every word; shot cuts align with caption changes.
- The first word is at 0.00 s; the last shot ends 0.2-0.4 s after the last word (or fades out).
