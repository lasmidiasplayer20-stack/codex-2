#!/usr/bin/env python3
"""Split oversized generated vector archives into ordinary GitHub-sized files."""
from pathlib import Path
import json,zipfile,zlib

ROOT=Path(__file__).resolve().parents[1]
LIMIT=64*1024*1024

def main():
 for report_path in sorted((ROOT/'analysis').glob('part-*.json')):
  report=json.loads(report_path.read_text())
  names=report.get('vector_archives') or [report['vector_archive']]
  replacement=[]
  for name in names:
   source=ROOT/name
   if source.stat().st_size<=80*1024*1024:
    replacement.append(name);continue
   shards=[];archive=None;estimated=0
   try:
    with zipfile.ZipFile(source) as original:
     expected=original.namelist()
     for entry in expected:
      data=original.read(entry);size=len(zlib.compress(data,6))+len(entry)+128
      if archive is None or estimated+size>LIMIT:
       if archive:archive.close()
       target=source.with_name(f'{source.stem}-chunk-{len(shards)+1:02d}.zip')
       archive=zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)
       shards.append(target);estimated=0
      archive.writestr(entry,data);estimated+=size
   finally:
    if archive:archive.close()
   actual=[]
   for target in shards:
    assert target.stat().st_size<90*1024*1024
    with zipfile.ZipFile(target) as part:
     assert part.testzip() is None;actual.extend(part.namelist())
   assert actual==expected
   replacement.extend(p.relative_to(ROOT).as_posix() for p in shards)
   source.unlink()
  report['vector_archives']=replacement
  if len(replacement)==1:report['vector_archive']=replacement[0]
  else:report.pop('vector_archive',None)
  report_path.write_text(json.dumps(report,separators=(',',':'))+'\n')
 print('Generated vector archives meet the per-file packaging limit.')

if __name__=='__main__':main()
