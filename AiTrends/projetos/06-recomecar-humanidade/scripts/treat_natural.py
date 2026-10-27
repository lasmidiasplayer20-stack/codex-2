from pathlib import Path
import json,subprocess,math,re,wave
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1];parser=__import__('argparse').ArgumentParser();parser.add_argument('--work',type=Path,required=True);W=parser.parse_args().work;manifest=json.loads((W/'episode-manifest.json').read_text());assert len(manifest)==8,'Wait for eight complete episode06 blocks; no partial export.'
beats=json.loads((P/'story/beats.json').read_text());story=json.loads((P/'story/shots.json').read_text());old=[(b['start'],b['end'])for b in beats];sr=24000;allx=[];offset=0;records=[]
for idx,part in enumerate(manifest):
 src=W/part['file'];rate,x=wavfile.read(src);assert rate==sr;x=x.astype(np.float64)/32768
 # Detect only sustained silence; short breaths/word gaps stay untouched.
 frame=240;n=len(x)//frame;power=np.sqrt(np.mean(x[:n*frame].reshape(n,frame)**2,axis=1));silent=power<.006
 edges=np.diff(np.r_[False,silent,False].astype(int));starts=np.where(edges==1)[0]*frame;ends=np.where(edges==-1)[0]*frame
 gaps=[(a,min(b,len(x)))for a,b in zip(starts,ends)if (b-a)/sr>1.2]
 cuts=[(a+int(.25*sr),b-int(.40*sr))for a,b in gaps if a>sr*.1 and b<len(x)-sr*.1]
 chunks=[];cursor=0
 for a,b in cuts:chunks.append(x[cursor:a]);cursor=b
 chunks.append(x[cursor:]);clean=np.concatenate(chunks)
 # Short head/tail trims at block boundaries only; no continuous silence cutter.
 energy=np.flatnonzero(np.abs(clean)>.012);head=max(0,energy[0]-round(.10*sr))if len(energy) else 0;tail=min(len(clean),energy[-1]+round(.16*sr))if len(energy)else len(clean)
 if idx:clean=clean[head:tail]
 else:head=0;tail=len(clean)
 wavfile.write(W/f'clean-{idx:02}.wav',sr,np.round(np.clip(clean,-1,1)*32767).astype(np.int16))
 dst=W/f'light-{idx:02}.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(W/f'clean-{idx:02}.wav'),'-af','highpass=f=65,acompressor=threshold=0.125:ratio=1.6:attack=25:release=250:makeup=1,loudnorm=I=-18:TP=-3:LRA=8','-ar',str(sr),'-ac','1','-c:a','pcm_s16le',str(dst)],check=True)
 _,y=wavfile.read(dst);y=y.astype(np.float32)/32768;dur=len(y)/sr
 group=[beats[i-1]for i in part['beats']];weights=[len(b['text'].split())for b in group];assert part['text']=='\n\n'.join(b['text']for b in group)
 # Paragraph gaps from generated audio, near expected text proportions; approximate, not word ASR.
 candidates=[]
 removed=0
 for (a,b),(ca,cb)in zip([g for g in gaps if g[0]>sr*.1 and g[1]<len(x)-sr*.1],cuts):
  midpoint=(ca-removed+.325*sr-head)/sr;candidates.append(midpoint);removed+=cb-ca
 bounds=[0];cum=0
 for j,w in enumerate(weights[:-1]):
  cum+=w;expected=dur*cum/sum(weights);available=[c for c in candidates if c>bounds[-1]+2 and c<dur-2]
  chosen=min(available,key=lambda c:abs(c-expected))if available else expected
  if abs(chosen-expected)>6:chosen=expected
  bounds.append(chosen)
 bounds.append(dur)
 for j,b in enumerate(group):b['start']=round(offset+bounds[j],5);b['end']=round(offset+bounds[j+1],5)
 allx.append(y);offset+=dur
 if idx<len(manifest)-1:allx.append(np.zeros(round(.16*sr),np.float32));offset+=.16;group[-1]['end']=round(offset,5)
 records.append({'source':src.name,'beats':part['beats'],'raw_seconds':len(x)/sr,'treated_seconds':dur,'removed_long_gaps':len(cuts),'seconds_removed':len(x)/sr-dur,'model':part['model'],'voice':'Puck','speed_change':False,'boundaries':'Long paragraph gaps near text proportions; not ASR word alignment.'})
x=np.concatenate(allx);fps=24;duration=math.ceil(len(x)/sr*fps)/fps;target=round(duration*sr);x=np.pad(x,(0,target-len(x)))
beats[-1]['end']=duration
for shot in story['shots']:
 i=shot['params']['beat'];a,b=old[i];fa=(shot['start']-a)/(b-a);fb=(shot['end']-a)/(b-a);nb=beats[i];shot['start']=round(nb['start']+(nb['end']-nb['start'])*fa,5);shot['end']=round(nb['start']+(nb['end']-nb['start'])*fb,5)
for i in range(1,len(story['shots'])):story['shots'][i]['start']=story['shots'][i-1]['end']
story['shots'][-1]['end']=duration;story['duration']=duration;story['timing_status']='generated_block_boundaries_and_paragraph_gaps_not_ASR'
cfg=json.loads((P/'config.json').read_text());cfg['duration']=duration;cfg['ctaSeconds']=[[43,51],[duration*.49,duration*.49+8],[duration-14,duration-1]];cfg['qaTimes']=[int(t)for t in np.linspace(2,duration-5,16)];cfg['qaStills']=[['cta-45s',46],['cta-intermediario',int(duration*.49+4)],['cta-final',int(duration-7)],['contato-caixas',int(beats[5]['start']+(beats[5]['end']-beats[5]['start'])*.5)],['passarela',int(beats[24]['start']+(beats[24]['end']-beats[24]['start'])*.8)]]
for name,obj in [('story/beats.json',beats),('story/shots.json',story),('config.json',cfg)]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
wavfile.write(P/'audio/narracao.wav',sr,np.round(np.clip(x,-.99,.99)*32767).astype(np.int16))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio/narracao.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/'audio/narracao.mp3')],check=True)
report={'method':'Same mild treatment as approved sample; only sustained gaps >1.2 seconds shortened to ~0.65 seconds; no tempo or pitch change.','approved_by':'user','approval':'Voice profile accepted by user after episode05; same voice/model requested for06','natural_seconds':duration,'initial_target_seconds':510,'timing_deviation_reason':'Preserve natural approved reading instead of speeding speech.','parts':records,'successful_audio_blocks':len(manifest),'known_http429_before_daily_reset':2,'same_episode_cached_blocks_reused':2,'new_full_voice_editorial_approval':False,'models':list({p['model']for p in manifest}),'human_listening_full_episode':False,'independent_ASR':False,'peak_dbfs':float(20*np.log10(max(np.max(np.abs(x)),1e-12))),'clipped_samples':int(np.sum(np.abs(x)>=1))}
(P/'audio/quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(P/'ROTEIRO.md').write_text('# Duas pessoas poderiam recomeçar a humanidade? / Então\n\nRoteiro original em português. Tempos aproximados dos blocos gerados e pausas entre parágrafos; não alinhamento palavra a palavra. Voz Puck, sem aceleração.\n\n'+'\n\n'.join(f'## {int(b["start"])//60:02}:{int(b["start"])%60:02} — {b["action"]}\n\n{b["text"]}'for b in beats)+'\n')
print('NATURAL_VOICE_TREATED',duration,records,flush=True)
