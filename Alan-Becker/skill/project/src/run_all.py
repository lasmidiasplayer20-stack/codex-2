#!/usr/bin/env python3
"""Run this case study: baseline, measured refinement, packaging, validation."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rebuild',action='store_true',help='Regenerate using a fresh workspace; preserve previous caches in .cache/')
args=parser.parse_args()
source=ROOT/'assets/reference.mp4'
metadata=ROOT/'analysis/reference.json'
movie=ROOT.parents[1]/'video/teamwater-recriado-1080p.mp4'
complete=ROOT/'analysis/refinement-complete.json'
checksum=hashlib.sha256(source.read_bytes()).hexdigest()
if metadata.exists():
 previous=json.loads(metadata.read_text())
 if previous['source_sha256']!=checksum and not args.rebuild:
  raise SystemExit('Source changed. Adapt the case-specific parameters, then use --rebuild.')
needs_render=args.rebuild or not complete.exists() or not movie.exists()
if not needs_render:
 saved=ROOT/'analysis/source-code-checksums.json'
 if saved.exists():
  expected=json.loads(saved.read_text())
  changed=[name for name,digest in expected.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
  if changed:raise SystemExit('Source code changed; use --rebuild. Changed: '+', '.join(changed))
if needs_render:
 if args.rebuild or complete.exists():
  cache=ROOT/'.cache';cache.mkdir(exist_ok=True)
  stamp=str(time.time_ns())
  for name in ['.work','vectors']:
   path=ROOT/name
   if path.exists():path.rename(cache/f'{name.lstrip(".")}-{stamp}')
  complete.unlink(missing_ok=True)
 for name in ['recreate.py','refine.py']:
  subprocess.run([sys.executable,str(ROOT/'src'/name)],check=True)
for name in ['package_vectors.py','validate.py']:
 subprocess.run([sys.executable,str(ROOT/'src'/name)],check=True)
checks={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src').glob('*.py')}
(ROOT/'analysis/source-code-checksums.json').write_text(json.dumps(checks,indent=2)+'\n')
