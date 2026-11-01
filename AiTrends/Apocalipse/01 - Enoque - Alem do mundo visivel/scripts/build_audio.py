"""Resume narration with an external credential file and private cache directory."""
from pathlib import Path
import argparse,subprocess,json,sys
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--credentials',type=Path,required=True);a.add_argument('--work',type=Path,required=True);a.add_argument('--from-part',type=int,default=1);a.add_argument('--to-part',type=int,default=25);a.add_argument('--assemble',action='store_true');o=a.parse_args()
for n in range(o.from_part,o.to_part+1):
 for script,args in [('generate_parts.py',['--credentials',str(o.credentials),'--work',str(o.work)]),('finish_parts.py',['--work',str(o.work)]),('check_speech.py',['--credentials',str(o.credentials),'--work',str(o.work/'asr')])]:
  subprocess.run([sys.executable,str(P/'scripts'/script),*args,'--from-part',str(n),'--to-part',str(n)],check=True)
 q=json.loads((P/f'qa/speech-{n:02}.json').read_text())
 accepted=q.get('editorial_review')in ['accepted_asr_spelling_only','accepted_minor_delivery_and_asr_variants']
 if q['spoken_instructions']or(q['word_sequence_similarity']<.97 and not accepted)or q['asr_reported_audio_issues']:
  raise SystemExit(f'Inspect QA for part {n}; successful generations preserved. Do not regenerate blindly.')
if o.assemble:subprocess.run([sys.executable,str(P/'scripts/assemble_master.py'),'--work',str(o.work)],check=True)
