"""Deterministic rain, wind and wet footsteps: NumPy synthesis, no sound-library assets."""
from pathlib import Path
import numpy as np,wave,subprocess,json
ROOT=Path(__file__).resolve().parent.parent;SR=24000;D=480;N=SR*D;rng=np.random.default_rng(20261023)
mix=np.zeros((N,2),np.float32)
# Spectrally shaped independent noise blocks for diffuse rain.
size=SR*2;freq=np.fft.rfftfreq(size,1/SR);shape=(freq/(freq+500))*np.exp(-freq/7000);shape[0]=0
for start in range(0,N,size):
 n=min(size,N-start)
 for side in range(2):
  noise=rng.normal(0,1,size);rain=np.fft.irfft(np.fft.rfft(noise)*shape).astype(np.float32);rain*=.013/max(.01,float(np.std(rain)));mix[start:start+n,side]+=rain[:n]
# Droplet transients with stereo positions, all synthesized.
for _ in range(3500):
 t=float(rng.uniform(0,D-.08));n=int(.05*SR);tt=np.arange(n)/SR;f=float(rng.uniform(1500,5200));sig=(np.sin(2*np.pi*f*tt)*np.exp(-tt*110)+rng.normal(0,.35,n)*np.exp(-tt*180)).astype(np.float32)*float(rng.uniform(.002,.012));pan=float(rng.uniform(-.8,.8));a=int(t*SR);mix[a:a+n,0]+=sig*(1-pan)*.5;mix[a:a+n,1]+=sig*(1+pan)*.5
chap=json.loads((ROOT/'timing.json').read_text());events=[]
motion=json.loads((ROOT/'qa/motion.json').read_text());last_step={'A':-1,'B':-1}
def transient(t,kind,amp=.07,pan=0):
 n=int(.24*SR);tt=np.arange(n)/SR
 if kind=='clap':sig=rng.normal(0,1,n)*np.exp(-tt*75)
 elif kind=='snap':sig=(rng.normal(0,1,n)*np.exp(-tt*45)+np.sin(2*np.pi*250*tt)*np.exp(-tt*35))
 elif kind=='splash':sig=rng.normal(0,1,n)*np.exp(-tt*18)*(1+.3*np.sin(2*np.pi*800*tt))
 else:sig=(np.sin(2*np.pi*(110*tt+6*tt*tt))*np.exp(-tt*55)+rng.normal(0,.5,n)*np.exp(-tt*36))
 sig=sig.astype(np.float32)*amp;a=int(t*SR);n=min(n,N-a);mix[a:a+n,0]+=sig[:n]*(1-pan)*.6;mix[a:a+n,1]+=sig[:n]*(1+pan)*.6;events.append({'t':round(t,3),'type':kind})
previous=''
for m in motion:
 for who,pan in [('A',-.35),('B',.35)]:
  actor=m[who];speed=actor.get('speed',0);run=actor.get('gaitRun',speed>1.15);stride=(1.24 if run else .90)*1.05;step=int(actor.get('distance',0)/stride*2)
  if speed>.08 and step!=last_step[who] and not actor.get('air'):transient(m['t'],'wet_step',.032,pan)
  last_step[who]=step
 if m['action']!=previous:
  if m['action'] in ['splash_friend','wring_hem','wring_coat']:transient(m['t']+(.35 if m['action']=='splash_friend' else .8),'splash',.065,.2)
  if m['action']=='umbrella_flip':transient(m['t']+1.8,'snap',.055,.3)
  if m['action']=='high_five':
   c=chap[8];beat=(c['end']-c['start'])/8;transient(m['t']+beat*.38,'clap',.04,0)
 previous=m['action']
# Slow wind envelope in the wind chapter. No sampled wind.
a=int(chap[5]['start']*SR);b=int(chap[5]['end']*SR);tt=np.arange(b-a)/SR
wind=rng.normal(0,1,b-a).astype(np.float32);wind=np.convolve(wind,np.ones(45)/45,'same');wind*=.018*(.5+.5*np.sin(tt*.6))
mix[a:b,0]+=wind;mix[a:b,1]+=wind*.85
# Fade edges only; preserve the continuous rain bed.
fade=np.minimum(1,np.arange(N)/SR/.5)*np.minimum(1,(N-np.arange(N))/SR/1.2);mix*=fade[:,None]
raw=ROOT/'audio/effects.wav'
with wave.open(str(raw),'wb') as f:f.setparams((2,2,SR,0,'NONE','not compressed'));f.writeframes((np.clip(mix,-.95,.95)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-c:a','libmp3lame','-b:a','128k',str(ROOT/'audio/efeitos.mp3')],check=True)
# Voice stays in the foreground; sidechain ducking gently lowers the rain during speech.
filters='[0:a]aresample=24000,asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=40:release=250[fx];[v][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.84:level=0:attack=5:release=100,apad=pad_dur=1,atrim=duration=480[out]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'audio/narracao.mp3'),'-i',str(raw),'-filter_complex',filters,'-map','[out]','-ar','48000','-c:a','libmp3lame','-b:a','192k',str(ROOT/'audio/mix.mp3')],check=True)
(ROOT/'qa/sound.json').write_text(json.dumps({'duration':D,'sample_rate':SR,'seed':20261023,'source':'NumPy noise shaping, synthesized sine/noise transients, no samples','wet_steps':len(events),'events':events},indent=2))
raw.unlink();print('Synthesized rain, wind and',len(events),'footsteps; mixed 480-second audio.',flush=True)
