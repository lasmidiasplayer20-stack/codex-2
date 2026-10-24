"""Deterministic original procedural score and action sounds. Offline."""
from pathlib import Path
import argparse,json,wave,subprocess
import numpy as np
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);a=p.parse_args();root=a.project;cfg=json.loads((root/'config.json').read_text());beats=json.loads((root/'story/beats.json').read_text());sr=24000;duration=cfg['duration'];n=round(duration*sr);mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(303);events=[]
 def add(t,y,g=.1,pan=0,kind=None):
  k=round(t*sr);end=min(n,k+len(y))
  if k<0 or k>=n:return
  y=y[:end-k]*g;mix[k:end,0]+=y*np.sqrt((1-pan)/2);mix[k:end,1]+=y*np.sqrt((1+pan)/2)
  if kind:events.append({'time':round(float(t),3),'kind':kind})
 def tone(f,d):
  t=np.arange(round(d*sr))/sr;return (np.sin(2*np.pi*f*t)+.2*np.sin(2*np.pi*f*2.002*t))*np.minimum(t/.012,1)*np.exp(-t*4/d)
 def noise(d):
  t=np.arange(round(d*sr))/sr;return np.convolve(rng.normal(0,1,len(t)),np.ones(13)/13,'same')*np.sin(np.pi*t/d)**2
 chords=[[146.83,220,293.66,369.99],[130.81,196,261.63,329.63],[164.81,246.94,329.63,392],[146.83,220,293.66,440]]
 for b in beats:
  start,end=b['start'],b['end'];action=b['action'];i=b['id'] if isinstance(b['id'],int)else beats.index(b);notes=chords[(beats.index(b)//3)%4];step=.75 if action in ['race','intercept','challenge','train','sprint']else 1.5
  for j,t in enumerate(np.arange(start,end-.3,step)):
   add(t,tone(notes[j%4],min(1.5,end-t)),.016 if step==.75 else .022,(-1 if j%2 else 1)*.3)
   if j%4==0:add(t,tone(notes[0]/2,min(2.5,end-t)),.018)
  if action in ['sprint','test','commute','steps','brake','turn','train','challenge','finish','race','help']:
   for j,t in enumerate(np.arange(start+.15,end-.2,.34)):
    tt=np.arange(round(.085*sr))/sr;add(t,noise(.085)*np.exp(-tt*15)+.22*np.sin(2*np.pi*95*tt)*np.exp(-tt*50),.06,(-1 if j%2 else 1)*.2,'footstep')
   add(start+.3,noise(.7),.06,-.3,'speed_whoosh')
  if action in ['catch','serve','intercept','finish']:
   t=start+(end-start)*({'catch':.23,'serve':.5,'intercept':.6,'finish':.65}[action]);add(t,tone(660,.18)+tone(990,.18)*.4,.06,.1,'contact')
  if action in ['birds','slow','perception']:add(start+1,tone(1760,.3),.025,.5,'slow_detail')
  if action=='brake':add(start+(end-start)*.45,noise(.6),.075,0,'brake')
 for t in [45.8,249.8,497.8]:add(t,noise(.035),.025,.1,'cta_click');add(t+1.3,tone(1046.5,.4)+tone(1568,.4)*.3,.024,.15,'cta_bell')
 fade=np.minimum(np.arange(n)/sr,1)*np.minimum((n-1-np.arange(n))/(sr*2),1);mix*=fade[:,None];peak=float(np.max(np.abs(mix)));assert peak<.9
 out=root/'audio';out.mkdir(exist_ok=True);wav=out/'trilha.wav'
 with wave.open(str(wav),'wb')as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((mix*32767).astype('<i2').tobytes())
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','160k',str(out/'trilha.mp3')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'narracao.wav'),'-i',str(wav),'-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=6[a]','-map','[a]','-ar','48000','-ac','2','-c:a','libmp3lame','-b:a','192k',str(out/'mix.mp3')],check=True)
 (out/'sound-design.json').write_text(json.dumps({'method':'Deterministic NumPy synthesis; no sampled assets or API','seconds':duration,'peak_dbfs':20*np.log10(peak+1e-12),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'events':events},indent=2));print('SOUND_COMPLETE',flush=True)
if __name__=='__main__':main()
