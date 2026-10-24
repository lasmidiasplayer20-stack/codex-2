"""Provisional reading subtitles, NOT word-aligned speech transcription."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent.parent
def tc(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
out=[]
for b in json.loads((ROOT/'story/beats.json').read_text()):
 sentences=re.split(r'(?<=[.!?])\s+',b['text']);weights=[len(s.split()) for s in sentences];total=sum(weights);start=b['start']
 for s,w in zip(sentences,weights):
  end=start+(b['end']-b['start'])*w/total
  words=s.split();lines=[];line=''
  for word in words:
   if len(line)+len(word)>49:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
  out.append(f'{len(out)+1}\n{tc(start)} --> {tc(end)}\n'+ '\n'.join(lines)+'\n');start=end
(ROOT/'timeline/legendas-provisorias.srt').write_text('\n'.join(out).rstrip()+'\n')
print(len(out),'legendas de leitura; revisar após a voz real.')
