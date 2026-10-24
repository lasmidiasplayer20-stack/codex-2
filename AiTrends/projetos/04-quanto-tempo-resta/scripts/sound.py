"""Original local score/Foley for episode 04. No samples or remote APIs."""
from pathlib import Path
import argparse,json,wave,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=ROOT);a=p.parse_args();root=a.project;beats=json.loads((root/'story/beats.json').read_text());sr=24000;duration=510;n=sr*duration;mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(404);events=[]
 def add(t,y,g=.1,pan=0,kind=None):
  k=round(t*sr);end=min(n,k+len(y))
  if k<0 or k>=n:return
  y=y[:end-k]*g;mix[k:end,0]+=y*np.sqrt((1-pan)/2);mix[k:end,1]+=y*np.sqrt((1+pan)/2)
  if kind:events.append({'time':round(float(t),3),'kind':kind})
 def tone(f,d):
  t=np.arange(round(d*sr))/sr;return (np.sin(2*np.pi*f*t)+.17*np.sin(2*np.pi*f*2.002*t)+.04*np.sin(2*np.pi*f*3*t))*np.minimum(t/.015,1)*np.exp(-t*4/d)
 def noise(d,window=15):
  t=np.arange(round(d*sr))/sr;return np.convolve(rng.normal(0,1,len(t)),np.ones(window)/window,'same')*np.sin(np.pi*t/d)**2
 tension=['warning','look','wrong','blackout','lead','stuck','creak','support'];hope=['turn','relief','cleanup','time','call','meaning','ending']
 for i,b in enumerate(beats):
  start,end=b['start'],b['end'];act=b['action'];chord=[146.83,174.61,220,293.66]if act not in hope else[174.61,220,261.63,349.23];step=.75 if act in tension else 1.5
  for j,t in enumerate(np.arange(start+.05,end-.3,step)):
   add(t,tone(chord[(j+i)%4],min(2.1,end-t)),.016 if act in tension else .023,(-1 if j%2 else 1)*.32)
   if j%4==0:add(t,tone(chord[0]/2,min(3,end-t)),.017)
   if act in tension and j%2==0:
    tt=np.arange(round(.22*sr))/sr;add(t,np.sin(2*np.pi*64*tt)*np.exp(-tt*24),.018,0,'tension_pulse')
  if act in ['reveal','oldman','arrival','cart','lead','stuck','support','cleanup','privacy']:
   for j,t in enumerate(np.arange(start+.3,end-.2,.56)):
    tt=np.arange(round(.1*sr))/sr;add(t,noise(.1)*np.exp(-tt*20)+.12*np.sin(2*np.pi*105*tt)*np.exp(-tt*40),.065,(-1 if j%2 else 1)*.15,'footstep')
  if act in ['notes','map','firsthelp','cleanup','meeting']:
   for frac in [.3,.65]:add(start+(end-start)*frac,noise(.34,25),.045,.2,'paper_rustle')
  if act in ['hook','warning','cup','relief']:add(start+(end-start)*.44,tone(1450,.12)+.2*tone(2300,.12),.028,.15,'ceramic')
  if act in ['cart','stuck','arrival','support']:
   for t in np.arange(start+1,end-.4,1.4):add(t,noise(.55,40),.045,-.2,'cart_wheel')
  if act in ['rain','blackout','lead','stuck','creak','support']:
   for t in np.arange(start,end-.2,2.0):add(t,noise(min(2.3,end-t),8),.012,-.35,'rain_outside')
  if act=='blackout':add(start+(end-start)*.25,noise(.05,2),.027,0,'light_switch')
  if act=='creak':
   d=1.1;t=np.arange(round(d*sr))/sr;add(start+(end-start)*.3,np.sin(2*np.pi*(190*t+35*t*t))*np.sin(np.pi*t/d)**2,.022,-.3,'wood_creak')
   for f in [.55,.66,.77]:add(start+(end-start)*f,noise(.16,25),.12,.25,'book_drop')
  if act in ['lead','stuck','turn']:add(start+(end-start)*.75,noise(.2,25),.05,.5,'door')
  if act in ['hook','warning']:add(start+1,tone(660,.45),.025,-.15,'counter_reveal')
  if act=='turn':
   for j,f in enumerate([523.25,659.25,783.99]):add(start+(end-start)*.4+j*.16,tone(f,.8),.03,j*.2-.2,'counter_change')
  if act in ['joke','ending']:add(start+(end-start)*.5,tone(880,.2),.023,0,'toy_watch')
  if act=='call':
   for k in [0,.2]:add(start+1+k,tone(523,.15)+tone(659,.15),.018,.15,'phone')
 for t in [45.8,249.8,497.8]:add(t,noise(.035,2),.025,.1,'cta_click');add(t+1.3,tone(1046.5,.4)+.3*tone(1568,.4),.024,.15,'cta_bell')
 fade=np.minimum(np.arange(n)/(sr*1.2),1)*np.minimum((n-1-np.arange(n))/(sr*2),1);mix*=fade[:,None];peak=float(np.max(np.abs(mix)));assert peak<.8
 out=root/'audio';out.mkdir(exist_ok=True);wav=out/'trilha.wav'
 with wave.open(str(wav),'wb')as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((mix*32767).astype('<i2').tobytes())
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','160k',str(out/'trilha.mp3')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'narracao.wav'),'-i',str(wav),'-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=6[a]','-map','[a]','-ar','48000','-ac','2','-c:a','libmp3lame','-b:a','192k',str(out/'mix.mp3')],check=True)
 (out/'sound-design.json').write_text(json.dumps({'method':'Deterministic NumPy synthesis, no sampled assets or remote service','duration':duration,'peak_dbfs':20*np.log10(peak+1e-12),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'events':events},indent=2)+'\n');print('SOUND_COMPLETE',flush=True)
if __name__=='__main__':main()
