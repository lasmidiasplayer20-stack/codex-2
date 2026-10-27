from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1];parser=__import__('argparse').ArgumentParser();parser.add_argument('--work',type=Path,required=True);W=parser.parse_args().work;beats=json.loads((P/'story/beats.json').read_text());story=json.loads((P/'story/shots.json').read_text());old=[(b['start'],b['end'])for b in beats];manifest=json.loads((W/'episode-manifest.json').read_text());sr=24000;offset=0;pieces=[];report=[]
assert len(manifest)==2
for i,part in enumerate(manifest):
 rate,x=wavfile.read(W/part['file']);assert rate==sr;x=x.astype(float)/32768;n=len(x)//240;silent=np.sqrt(np.mean(x[:n*240].reshape(n,240)**2,axis=1))<.006;e=np.diff(np.r_[False,silent,False].astype(int));starts=np.where(e==1)[0]*240;ends=np.where(e==-1)[0]*240
 gaps=[(a,b)for a,b in zip(starts,ends)if b-a>1.2*sr and a>.1*sr and b<len(x)-.1*sr];cursor=0;removed=0;bounds=[];chunks=[]
 for a,b in gaps:
  ca=a+round(.25*sr);cb=b-round(.4*sr);chunks.append(x[cursor:ca]);bounds.append((ca-removed+.325*sr)/sr);cursor=cb;removed+=cb-ca
 chunks.append(x[cursor:]);x=np.concatenate(chunks);src=W/f'clean-preview-{i}.wav';dst=W/f'light-preview-{i}.wav';wavfile.write(src,sr,(x*32767).astype(np.int16))
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-af','highpass=f=65,acompressor=threshold=0.125:ratio=1.6:attack=25:release=250:makeup=1,loudnorm=I=-18:TP=-3:LRA=8','-ar',str(sr),'-ac','1',str(dst)],check=True)
 _,y=wavfile.read(dst);y=y.astype(np.float32)/32768;d=len(y)/sr;group=[beats[j-1]for j in part['beats']];assert part['text']=='\n\n'.join(b['text']for b in group)
 weights=[len(b['text'].split())for b in group];bb=[0];cum=0
 for w in weights[:-1]:
  cum+=w;target=d*cum/sum(weights);candidates=[v for v in bounds if v>bb[-1]+2 and v<d-2];nearest=min(candidates,key=lambda c:abs(c-target))if candidates else target;bb.append(nearest if abs(nearest-target)<5 else target)
 bb.append(d)
 for j,b in enumerate(group):b['start']=round(offset+bb[j],5);b['end']=round(offset+bb[j+1],5)
 pieces.append(y);offset+=d
 if i<len(manifest)-1:pieces.append(np.zeros(round(.16*sr),np.float32));offset+=.16;group[-1]['end']=round(offset,5)
 report.append({'file':part['file'],'raw_seconds':len(wavfile.read(W/part['file'])[1])/sr,'treated_seconds':d,'long_gaps_shortened':len(gaps),'speed_change':False})
last_id=manifest[-1]['beats'][-1];old_boundary=old[last_id][0];total=story['duration'];remaining=total-offset
for i in range(last_id,len(beats)):
 a,b=old[i];beats[i]['start']=round(offset+remaining*(a-old_boundary)/(total-old_boundary),5);beats[i]['end']=round(offset+remaining*(b-old_boundary)/(total-old_boundary),5)
for shot in story['shots']:
 i=shot['params']['beat'];a,b=old[i];fa=(shot['start']-a)/(b-a);fb=(shot['end']-a)/(b-a);shot['start']=round(beats[i]['start']+fa*(beats[i]['end']-beats[i]['start']),5);shot['end']=round(beats[i]['start']+fb*(beats[i]['end']-beats[i]['start']),5)
for i in range(1,len(story['shots'])):story['shots'][i]['start']=story['shots'][i-1]['end']
for name,obj in [('story/beats.json',beats),('story/shots.json',story)]:(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
x=np.concatenate(pieces);wavfile.write(P/'audio/voz-inicial-parcial.wav',sr,(x*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio/voz-inicial-parcial.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/'audio/voz-inicial-parcial.mp3')],check=True)
(P/'audio/partial-voice.json').write_text(json.dumps({'complete_narration':False,'generated_beats':list(range(1,last_id+1)),'seconds':len(x)/sr,'voice':'Puck','model':'gemini-2.5-flash-preview-tts','parts':report,'timing':'Generated block boundaries and paragraph gaps; approximate sentence timing, no ASR','remaining_timing':'provisional, not a completed final audio/video'},indent=2)+'\n');print('PARTIAL_VOICE_READY',len(x)/sr)
