"""Assemble exact 60 s PCM parts using silence edits only; preserve pitch and speed."""
from pathlib import Path
import argparse,json,subprocess,re
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);a.add_argument('--from-part',type=int,default=1);a.add_argument('--to-part',type=int,default=25);o=a.parse_args();fs_expected=24000

def measure(path):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-19:TP=-3.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 return json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]

def intervals(x,fs):
 hop=int(.01*fs);n=len(x)//hop;y=x[:n*hop].reshape(n,hop);rms=np.sqrt(np.mean(y*y,axis=1));quiet=rms<10**(-43/20);changes=np.diff(np.r_[False,quiet,False].astype(int));return [(int(s*hop),int(e*hop))for s,e in zip(np.where(changes==1)[0],np.where(changes==-1)[0])]

for part in json.loads((P/'roteiro/partes.json').read_text()):
 n=part['part']
 if not o.from_part<=n<=o.to_part:continue
 raw=o.work/f'{n:02}-raw.wav';fs,v=wavfile.read(raw);assert fs==fs_expected and v.ndim==1;x=v.astype(float)/32768;rawlen=len(x)
 edit_path=P/'roteiro/audio-edits.json';plan=json.loads(edit_path.read_text()).get(str(n),{})if edit_path.exists()else{}
 for begin,end_cut in sorted(plan.get('cuts_seconds',[]),reverse=True):
  a=int(round(begin*fs));b=int(round(end_cut*fs));assert 0<=a<b<=len(x)
  assert np.max(np.abs(x[a-int(.02*fs):a+int(.02*fs)]))<.02 and np.max(np.abs(x[b-int(.02*fs):b+int(.02*fs)]))<.02,'Edit endpoints must be quiet'
  x=np.r_[x[:a],x[b:]]
 quiet=intervals(x,fs)
 # Remove only demonstrably quiet edges, leaving breath margins.
 start=0;end=len(x)
 if quiet and quiet[0][0]==0:start=max(0,quiet[0][1]-int(.09*fs))
 if quiet and quiet[-1][1]>=len(x)-int(.02*fs):end=min(len(x),quiet[-1][0]+int(.16*fs))
 x=x[start:end]
 # Shorten sustained voids before allocating the minute; retain 0.65 s pauses.
 initial_pause_cuts=[]
 for s,e in intervals(x,fs):
  if s>0 and e<len(x)-int(.02*fs) and e-s>int(1.1*fs):
   cut=e-s-int(.65*fs);initial_pause_cuts.append((s+(e-s-cut)//2,s+(e-s+cut)//2))
 for s,e in sorted(initial_pause_cuts,reverse=True):x=np.r_[x[:s],x[e:]]
 target=60*fs;edits=[]
 if len(x)>target:
  need=len(x)-target
  for s,e in sorted(intervals(x,fs),key=lambda z:z[1]-z[0],reverse=True):
   if s==0 or e>=len(x)-int(.02*fs) or e-s<int(.30*fs):continue
   cut=min(need,max(0,e-s-int(.26*fs)))
   if cut:edits.append((s+(e-s-cut)//2,s+(e-s+cut)//2,b''));need-=cut
   if need<=0:break
  if need>0:raise SystemExit(f'Part {n}: speech exceeds 60 s; editorial revision required, never accelerate or cut speech. Excess {need/fs:.2f} s')
  for s,e,_ in sorted(edits,reverse=True):x=np.r_[x[:s],x[e:]]
 elif len(x)<target:
  need=target-len(x);gaps=[(s,e)for s,e in intervals(x,fs)if s>int(.08*fs) and e<len(x)-int(.18*fs) and e-s>=int(.16*fs)]
  # Extend existing phrase pauses, capped at 1.15 s; no speech stretching.
  additions=[]
  for s,e in sorted(gaps,key=lambda z:z[1]-z[0],reverse=True):
   capacity=max(0,int(1.15*fs)-(e-s));additions.append([s+(e-s)//2,0,capacity])
  remaining=need-int(.28*fs) if need>int(.28*fs) else 0
  while remaining>0:
   active=[z for z in additions if z[1]<z[2]]
   if not active:break
   share=max(1,remaining//len(active))
   for z in active:
    add=min(share,z[2]-z[1],remaining);z[1]+=add;remaining-=add
  inserted=0
  for pos,count,_ in sorted(additions,reverse=True):
   if count:x=np.r_[x[:pos],np.zeros(count),x[pos:]];inserted+=count
  tail=target-len(x)
  if tail>int(1.25*fs):raise SystemExit(f'Part {n}: too little speech for a natural 60 s part; {tail/fs:.2f} s unfilled')
  x=np.pad(x,(0,tail));edits=[{'silence_added_seconds':inserted/fs,'tail_seconds':tail/fs}]
 assert len(x)==target,(n,len(x))
 # Same gentle treatment as the approved v1, float intermediates prevent overflow.
 x=sosfilt(butter(2,50,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,10500,fs=fs,output='sos'),x);x-=.04*sosfilt(butter(2,[1900,4300],fs=fs,btype='bandpass',output='sos'),x)
 eq=o.work/f'{n:02}-eq.wav';comp=o.work/f'{n:02}-compressed.wav';wavfile.write(eq,fs,x.astype(np.float32))
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(eq),'-af','acompressor=threshold=0.125:ratio=1.4:attack=25:release=350:knee=2:makeup=1','-c:a','pcm_f32le',str(comp)],check=True)
 m=measure(comp);gain=-19.5-float(m['input_i'])
 # Fixed level matching; a peak-only lookahead limiter catches isolated outliers.
 # No moving automatic gain; a rare transient must not make the whole minute quiet.
 limited=o.work/f'{n:02}-limited.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(comp),'-af',f'volume={gain}dB,alimiter=limit=0.668344:attack=5:release=100:level=false:latency=true','-c:a','pcm_f32le',str(limited)],check=True)
 _,x=wavfile.read(limited);x=x.astype(float);assert len(x)==target and np.max(np.abs(x))<.99
 name=f"{n:02} - {part['title']}";folder=P/'audio/partes';folder.mkdir(exist_ok=True);out=folder/(name+'.wav');wavfile.write(out,fs,np.rint(x*32767).astype(np.int16));mp3=out.with_suffix('.mp3');subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-c:a','libmp3lame','-b:a','192k',str(mp3)],check=True)
 final=measure(mp3);assert float(final['input_tp'])< -2.5
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(mp3),'-f','null','-'],check=True)
 silences=intervals(x,fs);long=max((e-s for s,e in silences),default=0)/fs
 report={'part':n,'title':part['title'],'raw_seconds':rawlen/fs,'editorial_audio_cuts_seconds':plan.get('cuts_seconds',[]),'pcm_seconds':len(x)/fs,'sample_rate':fs,'pcm_frames':len(x),'integrated_lufs':float(final['input_i']),'true_peak_dbtp':float(final['input_tp']),'lra_lu':float(final['input_lra']),'static_gain_db':gain,'maximum_quiet_interval_seconds_threshold_minus43db':long,'duration_method':'quiet-edge trimming, bounded phrase-pause edits and short tail only','pitch_shift':False,'speed_change':False,'compression_ratio':1.4,'peak_only_limiter_dbfs':-3.5,'moving_auto_gain':False,'full_decode_passed':True,'human_full_listening':False,'voice':'Algenib','model':'gemini-2.5-flash-preview-tts','approved_profile_revision':1,'wav':str(out.relative_to(P)),'mp3':str(mp3.relative_to(P))}
 (P/f'qa/part-{n:02}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('FINISHED',n,'raw',rawlen/fs,'lufs',report['integrated_lufs'],'peak',report['true_peak_dbtp'],'maxquiet',long,flush=True)
