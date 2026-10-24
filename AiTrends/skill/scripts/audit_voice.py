"""Optional local Whisper transcription; input text never supplied as a hint."""
from pathlib import Path
import argparse,json,re,difflib

def main():
 p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--model',default='base');a=p.parse_args()
 from faster_whisper import WhisperModel
 model=WhisperModel(a.model,device='cpu',compute_type='int8',cpu_threads=1,num_workers=1,download_root=str(a.work/'models'));reports=[]
 for f in sorted(a.work.glob('parte-??.wav')):
  cache=f.with_suffix('.asr.txt')
  if cache.exists():text=cache.read_text()
  else:
   segments,_=model.transcribe(str(f),language='pt',beam_size=3,vad_filter=True,condition_on_previous_text=False);text=' '.join(s.text.strip()for s in segments);cache.write_text(text)
  expected=json.loads(f.with_suffix('.json').read_text())['text'];norm=lambda t:re.findall(r'\w+',t.lower());want,got=norm(expected),norm(text);ratio=difflib.SequenceMatcher(None,want,got,autojunk=False).ratio();bad=[w for w in ['programação','programar','código','prompt','instruções','metadata']if w in got and w not in want];report={'part':int(f.stem[-2:]),'word_similarity':ratio,'unexpected_instruction_terms':bad,'words_expected':len(want),'words_transcribed':len(got),'method':f'Local faster-whisper {a.model}, independent transcription; no text hint, no human listening'};reports.append(report);print(json.dumps(report),flush=True)
  (a.project/'audio/content-audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
 if any(x['word_similarity']<.8 or x['unexpected_instruction_terms']for x in reports):raise SystemExit('Review transcription mismatches; ASR itself can make errors.')
 print('LOCAL_SPEECH_AUDIT_PASSED',flush=True)
if __name__=='__main__':main()
