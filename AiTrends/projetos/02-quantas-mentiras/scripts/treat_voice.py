"""Repeatable pause trimming, level riding and final pacing for new Gemini narration.
Inspect speech content for repeats/omissions before running; no credentials are used here.
"""
from pathlib import Path
import numpy as np,wave,json,subprocess,re
PROJECT=Path(__file__).resolve().parent.parent
ROOT=PROJECT/'audio'/'raw-local'
def read(path):
 with wave.open(str(path)) as f:
  sr=f.getframerate();assert f.getsampwidth()==2 and f.getnchannels()==1
  x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
 return sr,x
def write(path,sr,x):
 with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((np.clip(x,-.999,.999)*32767).astype('<i2').tobytes())
def metrics(sr,x):
 n=round(sr*.02);z=x[:len(x)//n*n].reshape(-1,n);r=np.sqrt(np.mean(z*z,axis=1));db=20*np.log10(r+1e-9);active=db[db>-40]
 # Longest low-energy run, with 20ms resolution.
 q=db<-42;edges=np.diff(np.r_[False,q,False].astype(int));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1);gaps=(ends-starts)*.02
 n1=sr;v=x[:len(x)//n1*n1].reshape(-1,n1);levels=20*np.log10(np.sqrt(np.mean(v*v,axis=1))+1e-9);levels=levels[levels>-35]
 return {'one_second_level_p90_minus_p10_db':float(np.percentile(levels,90)-np.percentile(levels,10)),'duration_seconds':len(x)/sr,'peak_dbfs':float(20*np.log10(np.max(np.abs(x))+1e-9)),'active_frame_p90_minus_p10_db':float(np.percentile(active,90)-np.percentile(active,10)),'max_low_energy_gap_seconds':float(max(gaps,default=0)),'gaps_over_0_8_seconds':int(sum(gaps>.8)),'clipped_samples':int(np.sum(np.abs(x)>=.9999))}
def clean(src,dst):
 sr,x=read(src);before=metrics(sr,x);n=round(sr*.01);z=x[:len(x)//n*n].reshape(-1,n);r=np.sqrt(np.mean(z*z,axis=1));quiet=r<10**(-42/20)
 edges=np.diff(np.r_[False,quiet,False].astype(int));starts=np.flatnonzero(edges==1)*n;ends=np.flatnonzero(edges==-1)*n
 keep=np.ones(len(x),dtype=bool);cuts=[]
 for a,b in zip(starts,ends):
  gap=(b-a)/sr
  if a==0:
   end=max(a,b-round(.06*sr));keep[a:end]=False
  elif b>=len(x)-n:
   start=min(b,a+round(.12*sr));keep[start:]=False
  elif gap>.65:
   left=a+round(.18*sr);right=b-round(.18*sr);keep[left:right]=False;cuts.append({'start':a/sr,'original_seconds':gap,'remaining_seconds':.36})
 y=x[keep]
 # Ride level on approximately one-second speech energy, rather than on individual syllables.
 hop=round(sr*.1);count=(len(y)+hop-1)//hop
 padded=np.pad(y,(0,count*hop-len(y)));power=np.mean(padded.reshape(count,hop)**2,axis=1)
 energy=np.sqrt(np.convolve(power,np.ones(11)/11,mode='same')+1e-10)
 gain_db=np.clip(20*np.log10(.11/np.maximum(energy,.012)),-9,9)
 gain_db=np.convolve(np.pad(gain_db,(3,3),mode='edge'),np.ones(7)/7,mode='valid')
 times=(np.arange(count)+.5)*hop
 gain=np.interp(np.arange(len(y)),times,10**(gain_db/20))
 y=y*gain
 raw=dst.with_name(dst.stem+'-trim.wav');write(raw,sr,y)
 # Slow gain riding followed by moderate compression. Preserve pauses and breathing.
 filters='highpass=f=65,acompressor=threshold=0.09:ratio=2.5:attack=15:release=180:makeup=1.25,loudnorm=I=-16:TP=-1.5:LRA=6'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',filters,'-ar','24000','-c:a','pcm_s16le',str(dst)],check=True)
 s,y=read(dst);return {'before':before,'after':metrics(s,y),'shortened_pauses':cuts}


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--target',type=float,default=500);a=p.parse_args()
 beats=json.loads((PROJECT/'story/beats.json').read_text());story=json.loads((PROJECT/'story/shots.json').read_text())
 parts=sorted(a.work.glob('parte-??.wav'))
 if len(parts)!=8:raise SystemExit('Expected eight completed voice segments.')
 report={};ys=[];part_times=[];elapsed=0
 for i,src in enumerate(parts):
  dst=a.work/(src.stem+'-treated.wav');r=clean(src,dst);report[src.name]=r;sr,x=read(dst)
  part_times.append({'id':i+1,'start':elapsed,'end':elapsed+len(x)/sr})
  elapsed+=len(x)/sr+.2;ys.extend([x,np.zeros(round(.2*sr),np.float32)])
 natural=np.concatenate(ys[:-1]);factor=(len(natural)/sr)/a.target
 if not .83<=factor<=1.2:raise SystemExit(f'Pacing {factor:.3f} needs editorial review before export.')
 write(a.work/'natural-treated.wav',sr,natural)
 dest=PROJECT/'audio/narracao.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(a.work/'natural-treated.wav'),'-af',f'atempo={factor:.9f},loudnorm=I=-16:TP=-1.8:LRA=6,apad,atrim=duration={a.target}','-ar','48000','-c:a','pcm_s16le',str(dest)],check=True)
 # Paragraph timings use the nearest energy valley to text-proportional predictions,
 # within each known real generated part. They are reviewed timing, not ASR word timestamps.
 for pi,part in enumerate(part_times):
  group=beats[pi*4:pi*4+4];end=(part_times[pi+1]['start'] if pi<7 else len(natural)/sr)
  weights=[len(b['text'].split()) for b in group];total=sum(weights)
  aa=part['start'];bounds=[aa];cum=0
  for j,w in enumerate(weights[:-1]):
   cum+=w;expected=part['start']+(part['end']-part['start'])*cum/total
   lo=max(aa+2,expected-1.2);hi=min(part['end']-2,expected+1.2)
   positions=np.arange(round(lo*sr),round(hi*sr),round(.02*sr));half=round(.09*sr)
   power=np.array([np.mean(natural[max(0,k-half):min(len(natural),k+half)]**2) for k in positions])
   if len(power):candidate=positions[np.argmin(power)]/sr
   else:candidate=expected
   bounds.append(candidate);aa=candidate
  bounds.append(end)
  for j,b in enumerate(group):b['start']=round(bounds[j]/factor,4);b['end']=round(bounds[j+1]/factor,4)
 for shot in story['shots']:
  b=beats[shot['params']['beat']];j=shot['params']['part'];shot['start']=round(b['start']+(b['end']-b['start'])*j/4,4);shot['end']=round(b['start']+(b['end']-b['start'])*(j+1)/4,4)
 story['shots'][-1]['end']=a.target;story['duration']=a.target;beats[-1]['end']=a.target
 (PROJECT/'story/shots.json').write_text(json.dumps(story,ensure_ascii=False,indent=2))
 (PROJECT/'story/beats.json').write_text(json.dumps(beats,ensure_ascii=False,indent=2))
 cfg=json.loads((PROJECT/'config.json').read_text());cfg['duration']=a.target;(PROJECT/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
 report['final']={'natural_duration':len(natural)/sr,'atempo':factor,'target_duration':a.target,'timing_method':'Generated-part boundaries plus text proportions adjusted to nearby audio energy valleys; not ASR word alignment.','metrics':metrics(*read(dest))}
 (PROJECT/'audio/quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('Narration treated; timing updated.',report['final'],flush=True)
