#!/usr/bin/env python3
"""Run this complete case study: baseline, measured refinement, then validation."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/reference.mp4'
metadata=ROOT/'analysis/reference.json'
if metadata.exists():
 previous=json.loads(metadata.read_text())
 if previous['source_sha256']!=hashlib.sha256(source.read_bytes()).hexdigest():
  raise SystemExit('Source changed. Use a fresh project/workspace; existing caches are not valid.')
if not (ROOT/'analysis/refinement-complete.json').exists():
 for name in ['recreate.py','refine.py']:
  subprocess.run([sys.executable,str(ROOT/'src'/name)],check=True)
subprocess.run([sys.executable,str(ROOT/'src/validate.py')],check=True)
