#!/usr/bin/env python3
"""Local Codex adapter. Run `python3 studio.py --help`. No paid calls by default."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
AI = ROOT / 'aitrends-2d-studio/skills/make-2d-video/kit'
STICK = ROOT / '2d-stick-animator/kit'
PY = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def run(argv, cwd=ROOT):
    subprocess.run([str(x) for x in argv], cwd=cwd, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['setup', 'doctor', 'aitrends', 'ai-tool', 'stick'])
    p.add_argument('args', nargs=argparse.REMAINDER,
                   help='aitrends: render.mjs flags; ai-tool/stick: tool name then flags')
    a = p.parse_args()
    if a.command == 'setup':
        for tool in ('node', 'npm', 'ffmpeg', 'ffprobe'):
            if not shutil.which(tool):
                p.error(f'Missing prerequisite: {tool}')
        if not PY.exists():
            venv.EnvBuilder(with_pip=True).create(ROOT / '.venv')
        run([PY, '-m', 'pip', '--no-cache-dir', 'install', '-r', ROOT / 'requirements.lock.txt'])
        run(['npm', 'ci', '--ignore-scripts', '--cache', ROOT / '.npm-cache'], AI)
        chromium = os.environ.get('CHROMIUM_EXECUTABLE_PATH') or shutil.which('chromium')
        if not chromium:
            run(['npx', 'playwright', 'install', 'chromium'], AI)
        run([PY, STICK / 'py/install_kit.py'])
        run([PY, '-m', 'pip', '--no-cache-dir', 'check'])
        return
    if not PY.exists():
        p.error('Run setup first')
    if a.command == 'doctor':
        run([PY, '-m', 'pip', '--no-cache-dir', 'check'])
        run([PY, AI / 'tools/doctor.py'], AI)
        run([PY, STICK / 'py/install_kit.py', '--check'])
    elif a.command == 'aitrends':
        if not a.args:
            p.error('Supply --project PATH and render options')
        run(['node', AI / 'render.mjs', *a.args], AI)
    else:
        if not a.args:
            p.error('Supply a tool name and its arguments')
        folder = STICK / 'py' if a.command == 'stick' else AI / 'tools'
        tool = a.args[0].removesuffix('.py')
        if Path(tool).name != tool or not (folder / f'{tool}.py').is_file():
            p.error('Unknown tool; use a basename from the kit')
        run([PY, folder / f'{tool}.py', *a.args[1:]], STICK.parent if a.command == 'stick' else AI)


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
