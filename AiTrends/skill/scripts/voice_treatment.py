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
