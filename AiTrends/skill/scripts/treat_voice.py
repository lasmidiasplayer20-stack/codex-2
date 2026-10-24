"""Treat cached Puck speech and align arbitrary shot layouts. No network calls."""
from pathlib import Path
import argparse,json,subprocess,re
import numpy as np
from voice_treatment import clean,read,write,metrics
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--target',type=float);a=p.parse_args();root=a.project.resolve();cfg=json.loads((root/'config.json').read_text());target=a.target or cfg['duration'];beats=json.loads((root/'story/beats.json').read_text());story=json.loads((root/'story/shots.json').read_text());before=[(b['start'],b['end'])for b in beats]
 files=sorted(a.work.glob('parte-??.wav'));expected=(len(beats)+3)//4
 if len(files)!=expected:raise SystemExit(f'Expected {expected} complete voice parts; got {len(files)}')
 ys=[];parts=[];elapsed=0;report={}
 for i,src in enumerate(files):
  meta=json.loads(src.with_suffix('.json').read_text());text='\n\n'.join(b['text']for b in beats[i*4:i*4+4]);assert meta['text']==text,'Narration text changed after generation.'
  dst=a.work/(src.stem+'-treated.wav');report[src.name]=clean(src,dst);sr,x=read(dst);parts.append(dict(start=elapsed,end=elapsed+len(x)/sr));elapsed+=len(x)/sr+.2;ys.extend([x,np.zeros(round(.2*sr),np.float32)])
 natural=np.concatenate(ys[:-1]);factor=len(natural)/sr/target
 if not .8<=factor<=1.2:raise SystemExit(f'Voice pacing {factor:.3f} needs script review; no extreme time stretch applied.')
 write(a.work/'treated-natural.wav',sr,natural);(root/'audio').mkdir(exist_ok=True)
 out=root/'audio/narracao.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(a.work/'treated-natural.wav'),'-af',f'atempo={factor:.9f},loudnorm=I=-16:TP=-1.8:LRA=6,apad,atrim=duration={target}','-ar','48000','-c:a','pcm_s16le',str(out)],check=True)
 for i,part in enumerate(parts):
  group=beats[i*4:i*4+4];weights=[len(b['text'].split())for b in group];bounds=[part['start']];cum=0
  for w in weights[:-1]:
   cum+=w;t=part['start']+(part['end']-part['start'])*cum/sum(weights);lo=max(bounds[-1]+1.5,t-1.1);hi=min(part['end']-1.5,t+1.1);positions=np.arange(round(lo*sr),round(hi*sr),round(.02*sr));half=round(.08*sr);power=[np.mean(natural[max(0,k-half):min(len(natural),k+half)]**2)for k in positions];bounds.append(positions[int(np.argmin(power))]/sr if len(power)else t)
  bounds.append(parts[i+1]['start']if i+1<len(parts)else len(natural)/sr)
  for j,b in enumerate(group):b['start']=round(bounds[j]/factor,5);b['end']=round(bounds[j+1]/factor,5)
 for s in story['shots']:
  i=s['params']['beat'];oldA,oldB=before[i];fa=(s['start']-oldA)/(oldB-oldA);fb=(s['end']-oldA)/(oldB-oldA);b=beats[i];s['start']=round(b['start']+(b['end']-b['start'])*fa,5);s['end']=round(b['start']+(b['end']-b['start'])*fb,5)
 for i in range(1,len(story['shots'])):story['shots'][i]['start']=story['shots'][i-1]['end']
 beats[-1]['end']=target;story['shots'][-1]['end']=target;story['duration']=target;cfg['duration']=target
 for name,data in [('story/beats.json',beats),('story/shots.json',story),('config.json',cfg)]: (root/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 report['final']={'target_seconds':target,'natural_seconds':len(natural)/sr,'atempo':factor,'metrics':metrics(*read(out)),'timing':'Generated-part boundaries, text proportions and nearby energy valleys; not ASR word alignment.','human_listening':False,'voice':'Puck','models':sorted({json.loads(f.with_suffix('.json').read_text())['model']for f in files})}
 (root/'audio/quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 (root/'ROTEIRO.md').write_text('# '+cfg['title']+' / Então\n\nNarração própria; Puck em português. Timestamps de sequência aproximados a partir dos trechos de voz tratados.\n\n'+'\n\n'.join(f'## {int(b["start"])//60:02}:{int(b["start"])%60:02} — {b["action"]}\n\n{b["text"]}'for b in beats)+'\n')
 # Optional reading subtitles, never passed back into TTS.
 captions=[]
 def tc(t):ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for b in beats:
  sentences=re.split(r'(?<=[.!?])\s+',b['text']);weights=[len(s.split())for s in sentences];start=b['start']
  for sentence,w in zip(sentences,weights):
   end=start+(b['end']-b['start'])*w/sum(weights);words=sentence.split();lines=[];line=''
   for word in words:
    if len(line)+len(word)>50:lines.append(line);line=word
    else:line=(line+' '+word).strip()
   if line:lines.append(line)
   captions.append(f'{len(captions)+1}\n{tc(start)} --> {tc(end)}\n'+'\n'.join(lines));start=end
 (root/'timeline/legendas.srt').write_text('\n\n'.join(captions)+'\n');print('VOICE_TREATED',report['final'],flush=True)
if __name__=='__main__':main()
