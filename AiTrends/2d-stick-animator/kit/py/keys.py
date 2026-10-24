"""Store or check API keys for the studio (never inside a project folder that gets shared).

  python keys.py set elevenlabs sk_...        # writes ~/.2d_stick_animator/keys.json (chmod 600)
  python keys.py set kie <key> --workspace    # writes <workspace>/.ra_secrets/keys.json instead (when ~ is not persistent)
  python keys.py check                        # which services have a key (values are never printed)
Services: elevenlabs, kie, openai, fal, pexels, pixabay, freesound
"""
import argparse
import os

from ra_common import KEY_NAMES, KIT, get_key, set_key


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("set"); s.add_argument("service"); s.add_argument("value"); s.add_argument("--workspace", action="store_true")
    sp.add_parser("check")
    a = ap.parse_args()
    if a.cmd == "set":
        where = None
        if a.workspace:
            where = os.path.join(os.path.dirname(KIT), ".ra_secrets", "keys.json")
        p = set_key(a.service, a.value, where)
        print(f"stored {a.service} key in {p}")
    else:
        for svc in KEY_NAMES:
            print(f"{svc:11s} {'yes' if get_key(svc, required=False) else '-'}")


if __name__ == "__main__":
    main()
