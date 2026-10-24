"""Local original music/SFX only. No speech, remote API or sampled recordings."""
from pathlib import Path
import numpy as np,json,wave,subprocess,argparse
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=500);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 sr=24000;n=round(a.seconds*sr);mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(273)
 beats=json.loads((ROOT/'story/beats.json').read_text());events=[]
 def add(t,y,g=.1,pan=0):
  at=round(t*sr)
  if at>=n:return
  end=min(n,at+len(y));y=y[:end-at]*g
  mix[at:end,0]+=y*np.sqrt((1-pan)/2);mix[at:end,1]+=y*np.sqrt((1+pan)/2)
 def tone(freq,dur):
  t=np.arange(round(dur*sr))/sr
  return (np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2.003*t))*np.minimum(t/.015,1)*np.exp(-t*3/dur)
 # Sparse bell/pluck bed. Long breaks leave room for future Puck narration.
 for tick in np.arange(0,a.seconds,2.25):
  region=int(tick//31)%4;notes=[[146.83,220,293.66,349.23],[130.81,196,261.63,329.63],[164.81,246.94,329.63,392],[146.83,220,293.66,440]][region]
  i=int(tick/2.25);freq=notes[(i*3)%4]
  add(tick,tone(freq,2.1),.025,(-1 if i%2 else 1)*.25)
  if i%4==0:add(tick,tone(freq/2,4),.018,0)
 for b in beats:
  t=b['start'];action=b['action']
  if action in ['door','test','self','belief','witness','distance','friend','promise','zero']:
   q=t+3 if action in ['door','test'] else t+(b['end']-t)*.53;add(q,tone(784 if action!='zero'else 1046.5,.32),.11,.1);events.append({'t':q,'type':'contador'})
  if action in ['arrival','reject','follow','reveal']:
   for q in np.arange(t+.5,min(t+5,a.seconds),.6):
    time=np.arange(round(.12*sr))/sr;noise=rng.normal(0,1,len(time)).astype(np.float32);kernel=np.ones(20)/20;noise=np.convolve(noise,kernel,'same');add(q,noise*np.exp(-time*35),.14,-.15);events.append({'t':float(q),'type':'passo'})
  if action in ['phone','distance']:
   q=t+1;time=np.arange(round(.3*sr))/sr;add(q,np.sin(2*np.pi*150*time)*np.exp(-time*13),.035,.25)
  if action in ['questions','release','mother']:
   q=t+1;time=np.arange(round(.3*sr))/sr;noise=rng.normal(0,1,len(time));add(q,noise*np.exp(-time*12)*np.sin(np.pi*time/.3),.008,-.2);events.append({'t':q,'type':'papel'})
 for start in [43,246,485]:
  click=start+2.8;tt=np.arange(round(.04*sr))/sr;noise=rng.normal(0,1,len(tt));add(click,noise*np.exp(-tt*150),.013,.12);events.append({'t':click,'type':'cta_click'})
  bell=start+4.1;add(bell,tone(1046.5,.42)+.35*tone(1568,.42),.025,.18);events.append({'t':bell,'type':'cta_bell'})
 fade=np.minimum(np.arange(n)/(sr*1.2),1)*np.minimum((n-1-np.arange(n))/(sr*2.2),1);mix*=fade[:,None]
 peak=float(np.max(np.abs(mix)));assert peak<.95
 a.output.parent.mkdir(parents=True,exist_ok=True)
 wav=a.output.with_suffix('.wav')
 with wave.open(str(wav),'wb')as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((mix*32767).astype('<i2').tobytes())
 if a.output.suffix!='.wav':subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','160k',str(a.output)],check=True)
 (a.output.with_suffix('.json')).write_text(json.dumps({'seconds':a.seconds,'sr':sr,'peak_dbfs':20*np.log10(peak+1e-12),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'speech':False,'method':'NumPy deterministic local synthesis','events':events},ensure_ascii=False,indent=2))
 print('Trilha procedural sem fala:',a.output,'pico',round(20*np.log10(peak),2),'dBFS')
if __name__=='__main__':main()
