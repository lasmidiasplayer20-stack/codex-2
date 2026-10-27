"""Original Python Foley. Contact fractions match film.js; no external audio assets/API."""
from pathlib import Path
import json,subprocess,argparse
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1]
def inverse(x):return (x/4)**(1/3) if x<.5 else 1-((1-x)/4)**(1/3)
def main():
 a=argparse.ArgumentParser();a.add_argument('--voice',default='voz-inicial-parcial.wav');args=a.parse_args();cfg=json.loads((P/'config.json').read_text());beats=json.loads((P/'story/beats.json').read_text());sr=24000;n=round(cfg['duration']*sr);fx=np.zeros((n,2),np.float32);music=np.zeros_like(fx);rng=np.random.default_rng(707);events=[]
 def noise(d):return rng.normal(size=round(d*sr)).astype(np.float32)
 def tone(f,d,decay=6):t=np.arange(round(d*sr))/sr;return np.sin(2*np.pi*f*t)*np.minimum(t/.008,1)*np.exp(-t*decay/d)
 def sound(k):
  if k=='foot_wood':
   d=.16;t=np.arange(round(d*sr))/sr;return (.4*np.convolve(noise(d),np.ones(7)/7,'same')+.25*np.sin(2*np.pi*110*t))*np.exp(-t*32)
  if k=='glass':return .32*tone(1600,.28)+.17*tone(2530,.28)
  if k=='switch':d=.055;t=np.arange(round(d*sr))/sr;return (.5*noise(d)+tone(430,d)*.2)*np.exp(-t*95)
  if k=='paper':d=.35;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(4)/4,'same')*.4*np.sin(np.pi*t/d)**2
  if k=='fabric':d=.5;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(18)/18,'same')*.45*np.sin(np.pi*t/d)**2
  if k=='chair':d=.55;t=np.arange(round(d*sr))/sr;return (.18*np.sin(2*np.pi*(180*t+15*t*t))+.3*np.convolve(noise(d),np.ones(14)/14,'same'))*np.sin(np.pi*t/d)**2
  if k=='latch':return .35*tone(400,.10)+.18*noise(.10)*np.exp(-np.arange(round(.10*sr))/sr*50)
  if k=='kettle':d=1.2;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(4)/4,'same')*.18*np.sin(np.pi*t/d)**2
  if k=='phone':return .14*tone(920,.11)+.06*tone(1380,.11)
  if k=='cable':d=.35;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(12)/12,'same')*.4*np.sin(np.pi*t/d)**2
  if k=='cta':return .20*tone(880,.18)+.05*tone(1320,.18)
  return tone(95,.4)*.2
 def place(at,y,gain,pan,stem):
  i=round(at*sr);j=min(n,i+len(y))
  if i<0 or i>=n:return
  stem[i:j,0]+=y[:j-i]*gain*np.sqrt((1-pan)/2);stem[i:j,1]+=y[:j-i]*gain*np.sqrt((1+pan)/2)
 def cue(b,u,kind,gain=.06,pan=0):
  at=b['start']+u*(b['end']-b['start']);y=sound(kind);place(at,y,gain,pan,fx);events.append(dict(beat=b['id'],action=b['action'],fraction=u,time=round(at,5),kind=kind,gain_db=round(20*np.log10(gain),2),pan=pan,duration=len(y)/sr))
 walks={'sumiu':(1.58,.6),'lia':(2.14,.7),'chaleira':(6.20,.6),'atalho':(1.94,.65),'escala':(3.4,.9),'vibracao':(2.7,.75),'soltura':(3.11,.6),'retorno':(2.73,.6),'interruptor':(2.60,.7),'vaso':(2.47,.75),'ultimo':(2.5,.55)}
 contacts={'copo':[(.12,'glass'),(.4,'paper')],'chaleira':[(.65,'switch'),(.70,'kettle')],'atalho':[(.43,'fabric'),(.68,'fabric')],'mapa':[(.15,'paper'),(.6,'paper')],'rotina':[(.25,'paper'),(.55,'paper'),(.8,'paper')],'troca':[(.22,'paper'),(.5,'paper'),(.75,'glass')],'captura':[(.12,'glass'),(.45,'paper'),(.65,'glass')],'soltura':[(.62,'glass'),(.84,'latch')],'retorno':[(.65,'switch')],'duvida':[(.45,'phone'),(.7,'paper')],'camera':[(.25,'paper'),(.4,'phone')],'cadeira':[(.3,'chair'),(.7,'switch')],'sombra':[(.62,'paper')],'plano':[(.3,'paper')],'escolha':[(.68,'fabric')],'apagao':[(.3,'switch')],'revela':[(.2,'cable')],'vaso':[(.55,'latch')],'ultimo':[(.68,'paper')]}
 for idx,b in enumerate(beats):
  act=b['action'];d=b['end']-b['start']
  if act in walks:
   dist,win=walks[act];win=min(win,3.4/d)
   for k,x in enumerate(np.arange(.31/.6/2,dist-.03,.31/.6/2)):cue(b,win*inverse(float(x/dist)),'foot_wood',.06,(-1 if k%2 else 1)*.17)
  if act=='teste':
   for start,win,dist in [(0,.5,2),(.5,.5,1.1)]:
    for x in np.arange(.31/.6/2,dist-.03,.31/.6/2):cue(b,start+win*inverse(float(x/dist)),'foot_wood',.06)
  if act=='desvio':
   for x in np.arange(.31/.6/2,4.27,.31/.6/2):cue(b,.8*inverse(float(x/4.3)),'foot_wood',.06)
  for frac,kind in contacts.get(act,[]):cue(b,frac,kind,.045 if kind in ['phone','switch'] else .08)
  # Quiet interior room tone; no fictional amplified skitter on every spider step.
  ambient=np.convolve(noise(d),np.ones(300)/300,'same')*.005;place(b['start'],ambient,1,0,fx)
  if act not in ['apagao','escolha','ultimo']:
   chord=[146.83,174.61,220] if idx<20 else [130.81,164.81,196]
   for at in np.arange(b['start']+.2,b['end']-1,12):
    dd=min(8,b['end']-at);t=np.arange(round(dd*sr))/sr
    for f in chord:place(at,np.sin(2*np.pi*f*t)*(1-np.exp(-t/1.4))*np.exp(-t/4),.0017,0,music)
 for at in [44,cfg['duration']*.49+1,cfg['duration']-12]:place(at,sound('cta'),.025,.1,fx)
 for stem,name in [(fx,'sfx'),(music,'trilha')]:
  assert np.max(np.abs(stem))<.7;wavfile.write(P/'audio'/f'{name}.wav',sr,np.round(stem*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-c:a','libmp3lame','-b:a','160k',str(P/'audio'/f'{name}.mp3')],check=True)
 (P/'audio/sfx-events.json').write_text(json.dumps(dict(method='Python NumPy procedural Foley; same action fractions and cubic travel easing as film.js',events=events,provisional_after_beat=None if args.voice=='narracao.wav' else 20),ensure_ascii=False,indent=2)+'\n')
 rate,y=wavfile.read(P/'audio'/args.voice);assert rate==sr;y=y.astype(np.float32)/32768;mix=np.column_stack([y,y])+(fx+music)[:len(y)];assert np.max(np.abs(mix))<.98;name='mix-inicial-parcial' if 'parcial' in args.voice else 'mix';wavfile.write(P/'audio'/f'{name}.wav',sr,np.round(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-ar','48000','-c:a','libmp3lame','-b:a','192k',str(P/'audio'/f'{name}.mp3')],check=True)
 (P/'audio/mix-quality.json').write_text(json.dumps({'peak_dbfs':float(20*np.log10(max(np.max(np.abs(mix)),1e-12))),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'sfx_events':len(events),'voice_seconds':len(y)/sr,'voice_model':'gemini-2.5-flash-preview-tts','human_full_listening':False},indent=2)+'\n');print('PYTHON_FOLEY_COMPLETE',len(events),flush=True)
if __name__=='__main__':main()
