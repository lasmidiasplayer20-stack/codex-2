"""Create a new video project in the workspace with the standard layout.

  python new_project.py "MONEY RAIN"            -> <workspace>/projects/money-rain/
  python new_project.py "MONEY RAIN" --slug money-rain-v2
  python new_project.py "HE SNEAKED INTO AN ASYLUM! #shorts #animation #curiosities"   -> projects/he-sneaked-into-an-asylum/

Layout: script/ audio/ (sfx kit copied into audio/sfx) timing/ plan/ assets/{bg,cast,props,icons,video,fx}
        ae/ (After Effects project, logs, stills) exports/ qc/ and PROJECT_STATE.md (where the pipeline is).
"""
import argparse
import os
import re
import shutil

from ra_common import KIT, project_dirs, slugify

ROOT = os.path.dirname(KIT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title")
    ap.add_argument("--slug")
    a = ap.parse_args()
    headline = re.split(r"\s#", a.title)[0].strip() or a.title
    slug = a.slug or slugify(headline)
    P = os.path.join(ROOT, "projects", slug)
    project_dirs(P)
    tf = os.path.join(P, "script", "title.txt")
    if not os.path.exists(tf):
        os.makedirs(os.path.dirname(tf), exist_ok=True)
        open(tf, "w", encoding="utf-8").write(a.title.strip() + "\n")
    sfx = os.path.join(KIT, "assets", "sfx")
    if os.path.isdir(sfx):
        for f in os.listdir(sfx):
            d = os.path.join(P, "audio", "sfx", f)
            if not os.path.exists(d):
                shutil.copy(os.path.join(sfx, f), d)
    st = os.path.join(P, "PROJECT_STATE.md")
    if not os.path.exists(st):
        open(st, "w", encoding="utf-8").write(
            f"# {headline}\n\nslug: {slug}\n\n## Pipeline\n- [ ] story source: concept picked / own story pasted (script/concepts.md, research.md)\n"
            "- [ ] script approved after the user's changes (script/script_final.txt, title.txt)\n"
            "- [ ] ElevenLabs key + voice ID set, voice sample approved (audio/voice.json)\n"
            "- [ ] voiceover (audio/voice.wav) + timing (timing/words.json, captions.json)\n- [ ] shot plan (plan/spec.json) + plan check\n"
            "- [ ] cast + assets (assets/, manifest.csv) + cast sheet approved\n- [ ] animatic (exports/preview.mp4) approved\n"
            "- [ ] After Effects build (ae/<slug>.aep) + stills checked\n- [ ] render + mix + final (exports/final.mp4)\n- [ ] QC report (qc/report.md)\n\n## Notes\n")
    print(P)


if __name__ == "__main__":
    main()
