"""Original Python Foley. Contact fractions match film.js; no external audio assets/API."""
from pathlib import Path
import json,subprocess,argparse
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1]
def inverse(x):return (x/4)**(1/3) if x<.5 else 1-((1-x)/4)**(1/3)
def main():
 a=argparse.ArgumentParser();a.add_argument('--voice',default='narracao.wav');args=a.parse_args();cfg=json.loads((P/'config.json').read_text());beats=json.loads((P/'story/beats.json').read_text());sr=24000;n=round(cfg['duration']*sr);fx=np.zeros((n,2),np.float32);music=np.zeros_like(fx);rng=np.random.default_rng(808);events=[]
 def noise(d):return rng.normal(size=round(d*sr)).astype(np.float32)
 def tone(f,d,decay=6):t=np.arange(round(d*sr))/sr;return np.sin(2*np.pi*f*t)*np.minimum(t/.008,1)*np.exp(-t*decay/d)
 def sound(k):
  if k=='foot_wood':
   d=.16;t=np.arange(round(d*sr))/sr;return (.4*np.convolve(noise(d),np.ones(7)/7,'same')+.25*np.sin(2*np.pi*110*t))*np.exp(-t*32)
  if k=='spawn':return .22*tone(523.25,.6)+.12*tone(783.99,.6)+.08*tone(1046.5,.6)
  if k=='undo':return .20*tone(392,.45)+.14*tone(261.63,.45)
  if k=='assemble' or k=='wood':
   d=.19;t=np.arange(round(d*sr))/sr;return (.35*np.convolve(noise(d),np.ones(7)/7,'same')+.2*tone(180,d))*np.exp(-t*24)
  if k=='air':
   d=2.5;t=np.arange(round(d*sr))/sr;return np.convolve(noise(d),np.ones(40)/40,'same')*.4*np.sin(np.pi*t/d)**2
  if k=='tool':return .2*tone(1050,.15)+.12*tone(1670,.15)
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
 walks={'teste':(6.4,6)}
 contacts={'menu':[(.20,'spawn')],'cadeira':[(.2,'spawn'),(.65,'chair')],'copia':[(.15,'glass'),(.35,'glass'),(.65,'glass')],'limites':[(.25,'paper')],'ferramentas':[(.2,'tool'),(.7,'tool')],'ouro':[(.10,'spawn'),(.4,'spawn')],'valor':[(.35,'paper')],'comida':[(.20,'assemble'),(.55,'assemble')],'multidao':[(.35,'phone')],'desfazer':[(.35,'undo')],'blocos':[(.35,'air'),(.60,'assemble')],'consertar':[(.2,'assemble'),(.5,'assemble'),(.8,'undo')],'ilha':[(.25,'spawn')],'volta':[(.7,'wood')],'regras':[(.25,'paper'),(.6,'paper')],'maquete':[(.3,'spawn')],'mutirao':[(.2,'tool'),(.7,'wood')],'escolha':[(.4,'switch')],'cadeirafinal':[(.4,'chair')]}
 for idx,b in enumerate(beats):
  act=b['action'];d=b['end']-b['start']
  if act in walks:
   dist,seconds=walks[act];win=min(1,seconds/d)
   for k,x in enumerate(np.arange(.31/.6/2,dist-.03,.31/.6/2)):cue(b,win*inverse(float(x/dist)),'foot_wood',.06,(-1 if k%2 else 1)*.17)
  if act in ['abrigo','ponte','alto']:
   count={'abrigo':5,'ponte':14,'alto':9}[act]
   for i in range(count):cue(b,.12+.58*i/count,'assemble',.055,(i%3-1)*.22)
  if act in ['voo','rua','protegido','fuga','cidade']:
   cue(b,min(.12,1/d),'air',.035)
  for frac,kind in contacts.get(act,[]):cue(b,frac,kind,.045 if kind in ['phone','switch'] else .08)
  # Quiet interior room tone; no fictional amplified skitter on every spider step.
  ambient=np.convolve(noise(d),np.ones(300)/300,'same')*.005;place(b['start'],ambient,1,0,fx)
  if act not in ['sombra','blocos']:
   chord=[174.61,220,261.63] if idx<16 or idx>24 else [146.83,174.61,220]
   for at in np.arange(b['start']+.2,b['end']-1,12):
    dd=min(8,b['end']-at);t=np.arange(round(dd*sr))/sr
    for f in chord:place(at,np.sin(2*np.pi*f*t)*(1-np.exp(-t/1.4))*np.exp(-t/4),.0017,0,music)
 for at in [44,cfg['duration']*.49+1,cfg['duration']-12]:place(at,sound('cta'),.025,.1,fx)
 for stem,name in [(fx,'sfx'),(music,'trilha')]:
  assert np.max(np.abs(stem))<.7;wavfile.write(P/'audio'/f'{name}.wav',sr,np.round(stem*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-c:a','libmp3lame','-b:a','160k',str(P/'audio'/f'{name}.mp3')],check=True)
 (P/'audio/sfx-events.json').write_text(json.dumps(dict(method='Python NumPy procedural Foley; same action fractions and cubic travel easing as film.js',events=events,provisional_after_beat=None),ensure_ascii=False,indent=2)+'\n')
 rate,y=wavfile.read(P/'audio'/args.voice);assert rate==sr;y=y.astype(np.float32)/32768;mix=np.column_stack([y,y])+(fx+music)[:len(y)];assert np.max(np.abs(mix))<.98;name='mix-inicial-parcial' if 'parcial' in args.voice else 'mix';wavfile.write(P/'audio'/f'{name}.wav',sr,np.round(mix*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{name}.wav'),'-ar','48000','-c:a','libmp3lame','-b:a','192k',str(P/'audio'/f'{name}.mp3')],check=True)
 (P/'audio/mix-quality.json').write_text(json.dumps({'peak_dbfs':float(20*np.log10(max(np.max(np.abs(mix)),1e-12))),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'sfx_events':len(events),'voice_seconds':len(y)/sr,'voice_model':'gemini-2.5-flash-preview-tts','human_full_listening':False},indent=2)+'\n');print('PYTHON_FOLEY_COMPLETE',len(events),flush=True)
if __name__=='__main__':main()
