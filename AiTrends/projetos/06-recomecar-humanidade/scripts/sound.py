"""Original deterministic Python Foley/ambience/music. Uses normalized action contacts."""
from pathlib import Path
import json,subprocess,argparse
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1]
def ease(x):x=np.clip(x,0,1);return np.where(x<.5,4*x**3,1-(-2*x+2)**3/2)
def inverse(x):return (x/4)**(1/3)if x<.5 else 1-((1-x)/4)**(1/3)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--voice',default='voz-inicial-parcial.wav');args=parser.parse_args();cfg=json.loads((P/'config.json').read_text());beats=json.loads((P/'story/beats.json').read_text());sr=24000;n=round(cfg['duration']*sr);fx=np.zeros((n,2),np.float32);music=np.zeros_like(fx);rng=np.random.default_rng(606);events=[]
 def noise(d):return rng.normal(0,1,round(d*sr)).astype(np.float32)
 def tone(f,d,decay=6):t=np.arange(round(d*sr))/sr;return np.sin(2*np.pi*f*t)*np.minimum(t/.008,1)*np.exp(-t*decay/d)
 def sound(kind):
  if kind.startswith('foot'):
   d=.15;t=np.arange(round(d*sr))/sr;y=np.convolve(noise(d),np.ones(5)/5,'same')*np.exp(-t*37);y+=.24*np.sin(2*np.pi*(115 if kind=='foot_wood'else 85)*t)*np.exp(-t*50);return y
  if kind=='paper':d=.30;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(3)/3,'same')*np.sin(np.pi*t/d)**2*.45
  if kind=='lid':d=.45;t=np.arange(round(d*sr))/sr;return (.13*np.sin(2*np.pi*(180*t+18*t*t))+.15*np.convolve(noise(d),np.ones(10)/10,'same'))*np.sin(np.pi*t/d)**2
  if kind=='radio_switch':return noise(.035)*np.exp(-np.arange(round(.035*sr))/sr*130)+.15*tone(450,.035)
  if kind=='radio_hiss':d=.6;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(2)/2,'same')*.16*np.sin(np.pi*t/d)**2
  if kind=='wood_contact':d=.18;t=np.arange(round(d*sr))/sr;return (.6*np.convolve(noise(d),np.ones(6)/6,'same')+tone(170,d)*.20)*np.exp(-t*30)
  if kind=='water':d=.55;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(8)/8,'same')*.25*np.sin(np.pi*t/d)**2
  if kind=='tool':return .3*tone(1200,.13)+.13*tone(2100,.13)
  if kind=='cta':return .20*tone(880,.2)+.05*tone(1320,.2)
  return noise(.08)*.1
 def place(at,y,gain,pan,stem):
  start=round(at*sr);end=min(n,start+len(y));
  if start<0 or start>=n:return
  stem[start:end,0]+=y[:end-start]*gain*np.sqrt((1-pan)/2);stem[start:end,1]+=y[:end-start]*gain*np.sqrt((1+pan)/2)
 def cue(b,u,kind,gain=.055,pan=0):
  at=b['start']+u*(b['end']-b['start']);y=sound(kind);place(at,y,gain,pan,fx);events.append({'beat':b['id'],'action':b['action'],'fraction':round(float(u),7),'time':round(at,5),'kind':kind,'gain_db':round(20*np.log10(gain),2),'pan':pan,'duration':len(y)/sr})
 walks={'cidade':(3.5,.72),'encontro':(.9,.4),'rotina':(2.8,.6),'tempo':(3.2,1),'natureza':(3.1,1),'sinal':(6.1,.75),'grupo':(2.2,.55),'volta':(3.2,1)}
 for i,b in enumerate(beats):
  act=b['action'];d=b['end']-b['start']
  if act in walks:
   distance,window=walks[act];step=(.31/.6)/2
   for k,dist in enumerate(np.arange(step,distance-.03,step)):
    u=window*inverse(float(dist/distance));cue(b,u,'foot_wood'if b['set']in['school','supply','clinic','harbor']else'foot_stone',.045,(-1 if k%2 else 1)*.15)
  if act in ['encontro','radio']:cue(b,.58,'radio_switch',.025);cue(b,.62,'radio_hiss',.035)
  if act=='heranca':cue(b,.20,'lid',.08,-.2);cue(b,.36,'lid',.07,.2)
  if act in ['baralho','modelos','memoria']:
   for u in [.25,.55,.75]:cue(b,u,'paper',.045)
  if act in ['rotina','cuidado']:cue(b,.48,'water',.07,.1)
  if act=='travessia':cue(b,.80,'wood_contact',.13);cue(b,.85,'tool',.045,.2)
  if act=='grupo':cue(b,.55,'tool',.035)
  if b['set']in['street','garden','harbor']:
   length=round(d*sr);ambient=np.convolve(noise(d),np.ones(350)/350,'same')*.012;place(b['start'],ambient,1,0,fx)
  # Same quiet harmonic language as the accepted episode05, no percussion loop.
  if act not in ['cuidado','oculto']:
   for at in np.arange(b['start']+.15,b['end']-1,11):
    dd=min(8,b['end']-at);t=np.arange(round(dd*sr))/sr
    for f in ([196,246.94,293.66]if i%2 else[174.61,220,261.63]):place(at,np.sin(2*np.pi*f*t)*(1-np.exp(-t/1.1))*np.exp(-t/4),.0016,0,music)
 for at in [44,cfg['duration']*.49+1,cfg['duration']-12]:place(at,sound('cta'),.025,.1,fx)
 for stem,name in [(fx,'sfx'),(music,'trilha')]:
  assert np.max(np.abs(stem))<.7;wavfile.write(P/'audio'/f'{name}.wav',sr,(stem*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-c:a','libmp3lame','-b:a','160k',str(P/'audio'/f'{name}.mp3')],check=True)
 (P/'audio/sfx-events.json').write_text(json.dumps({'method':'Deterministic Python NumPy procedural Foley, action fractions match animation','provisional_after_beat':None if args.voice=='narracao.wav'else 8,'events':events},ensure_ascii=False,indent=2)+'\n')
 voice=P/'audio'/args.voice
 if voice.exists():
  rate,y=wavfile.read(voice);assert rate==sr;y=y.astype(np.float32)/32768;mix=np.column_stack([y,y])+(fx+music)[:len(y)];assert np.max(np.abs(mix))<.98;name='mix-inicial-parcial'if 'parcial'in args.voice else'mix';wavfile.write(P/'audio'/f'{name}.wav',sr,(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-ar','48000','-c:a','libmp3lame','-b:a','192k',str(P/'audio'/f'{name}.mp3')],check=True)
 print('PYTHON_FOLEY_COMPLETE',len(events),'events; voice',args.voice,flush=True)
if __name__=='__main__':main()
