from pathlib import Path
import argparse,json,re,subprocess,math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);W=p.parse_args().work
fs,raw=wavfile.read(W/'voice/block-01.wav');x=raw.astype(float)/32768
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice/block-01.wav'),'-af','silencedetect=noise=-36dB:d=0.22','-f','null','-'],capture_output=True,text=True,check=True)
starts=[float(v)for v in re.findall('silence_start: ([0-9.]+)',r.stderr)];ends=[float(v)for v in re.findall('silence_end: ([0-9.]+)',r.stderr)];parts=[];last=0;cuts=[]
for b,e in zip(starts,ends):
 keep=min(e-b,.45)if b>.01 else .08
 parts.extend([x[last:round(b*fs)],x[round(b*fs):round((b+keep)*fs)]]);last=round(e*fs);cuts.append({'start':b,'end':e,'kept':keep})
parts.append(x[last:]);x=np.concatenate(parts)
x=sosfilt(butter(2,55,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,10500,fs=fs,output='sos'),x);x-=.06*sosfilt(butter(2,[1800,4300],fs=fs,btype='bandpass',output='sos'),x)
wavfile.write(W/'voice-eq.wav',fs,(x*32767).astype(np.int16));r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice-eq.wav'),'-af','loudnorm=I=-20.5:TP=-3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-20.5-float(m['input_i']),-3.5-20*np.log10(max(abs(x))));x*=10**(gain/20)
offset=.18;D=math.ceil(offset+len(x)/fs+.5);N=D*fs;voice=np.zeros(N);j=round(offset*fs);voice[j:j+len(x)]=x;fx=np.zeros((N,2));rng=np.random.default_rng(3801);events=[]
def mapT(t):return offset+t-sum(max(0,min(t,c['end'])-c['start']-c['kept'])for c in cuts if t>c['start'])
q=json.loads((P/'qa/narration-check.json').read_text());segments=q['segments'];text=' '.join(s['text']for s in segments)
def wordtime(phrase,default):
 for s in segments:
  a=s['text'].lower().find(phrase.lower())
  if a>=0:return mapT(s['start']+(s['end']-s['start'])*a/max(1,len(s['text'])))
 return default
# Approximate ASR phrase times, adjusted exactly for the removed excess silence.
anchors=[0,wordtime('No Japão',7.5),wordtime('O detalhe',17),wordtime('Entre as opções',25),wordtime('Nico sai',34),wordtime('Na loja',37),wordtime('E falta',43),wordtime('Esse arranjo',51),wordtime('Isso não significa',59),D]
assert all(a<b for a,b in zip(anchors,anchors[1:])),anchors
# Acts never restart on a reverse angle; all motions use their global act interval.
groups=[('window',['wide','detail'],anchors[0],anchors[1]),('hall',['crane','track'],anchors[1],anchors[1]+(anchors[2]-anchors[1])*.55),('machine',['over','macro'],anchors[1]+(anchors[2]-anchors[1])*.55,anchors[2]),('counter',['wide','reverse'],anchors[2],anchors[3]),('prize',['over','macro'],anchors[3],anchors[4]),('walk',['track','low'],anchors[4],anchors[5]),('exchange',['over','detail'],anchors[5],anchors[6]),('cycle',['top','shop','wholesaler','van','orbit'],anchors[6],anchors[8]),('end',['wide','side','close'],anchors[8],D)]
shots=[]
for act,cams,b,e in groups:
 for i,cam in enumerate(cams):
  shots.append({'id':f's{len(shots)+1:02}','start':round(b+(e-b)*i/len(cams),5),'end':round(b+(e-b)*(i+1)/len(cams),5),'scene':'pachinko','bars':'none','in':{'type':'cut','dur':0},'params':{'act':act,'cam':cam,'label':''}})
(P/'story/shots.json').write_text(json.dumps({'duration':D,'shots':shots},ensure_ascii=False,indent=2));cfg=json.loads((P/'config.json').read_text());cfg.update(duration=D,qaTimes=[round((s['start']+s['end'])/2,4)for s in shots]);(P/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
(P/'story/timing.json').write_text(json.dumps({'seconds':D,'voice_offset':offset,'raw_to_treated_silence_map':cuts,'phrase_anchors':anchors,'timing':'Approximate Gemini ASR; piecewise removal map; no forced phoneme alignment'},indent=2))
def add(at,dur,kind,amp=.014,pan=0):
 n=min(round(dur*fs),N-round(at*fs));u=np.arange(n)/fs
 noise=rng.normal(0,1,n);env=np.exp(-u*18)*np.minimum(1,u/.003)
 if kind=='steel ball':v=(np.sin(2*np.pi*2800*u)+.42*np.sin(2*np.pi*4350*u))*env+.12*noise*np.exp(-u*85)
 elif kind=='footstep':v=sosfilt(butter(2,950,fs=fs,output='sos'),noise)*np.exp(-u*45)+.18*np.sin(2*np.pi*135*u)*np.exp(-u*36)
 elif kind in ['prize tap','tray set']:v=(np.sin(2*np.pi*480*u)+.6*np.sin(2*np.pi*730*u))*env+.15*sosfilt(butter(2,1500,fs=fs,output='sos'),noise)*np.exp(-u*35)
 elif kind=='paper cash':v=sosfilt(butter(2,[1100,5500],fs=fs,btype='bandpass',output='sos'),noise)*np.sin(np.linspace(0,np.pi,n))**2*.35
 elif kind=='cloth':v=sosfilt(butter(2,1800,fs=fs,output='sos'),noise)*np.sin(np.linspace(0,np.pi,n))**2*.3
 else:v=(np.sin(2*np.pi*620*u)+.4*np.sin(2*np.pi*930*u))*np.exp(-u*6)*np.minimum(1,u/.01)
 k=round(at*fs);fx[k:k+n,0]+=amp*v*np.sqrt((1-pan)/2);fx[k:k+n,1]+=amp*v*np.sqrt((1+pan)/2);events.append({'seconds':at,'duration':dur,'kind':kind,'amplitude':amp,'pan':pan})
for act,cams,b,e in groups:
 if act=='machine':
  for t in np.arange(b+.08,e,.19):add(float(t),.11,'steel ball',.008,float(rng.uniform(-.4,.4)))
 if act in ['hall','walk']:
  # At the same distance-driven stance entry as the rig, not on arbitrary beat pulses.
  distance=2.0 if act=='hall'else 2.7;stride=.31;steps=int(distance/(stride/.6)*2)
  for i in range(1,steps+1):
   target=(i/2)*(stride/.6)/distance;lo,hi=0,1
   for _ in range(24):
    mid=(lo+hi)/2
    if mid*mid*(3-2*mid)<target:lo=mid
    else:hi=mid
   when=b+(e-b)*(lo+hi)/2
   if when<e-.05:add(when,.09,'footstep',.011,-.12 if i%2 else .12)
 if act=='prize':add(b+.43*(e-b),.12,'prize tap',.022);add(b+.74*(e-b),.16,'cloth',.014)
 if act=='exchange':add(b+.31*(e-b),.12,'prize tap',.022);add(b+.62*(e-b),.30,'paper cash',.025);add(b+.82*(e-b),.22,'paper cash',.021)
 if act=='counter':add(b+.3,.15,'tray set',.015)
 if act=='cycle':
  for qv in [.08,.4,.73]:add(b+qv*(e-b),.38,'gentle chime',.005)
for at in [15.1,D-8.0]:add(at,.10,'gentle chime',.002)
t=np.arange(N)/fs;music=np.zeros(N)
for onset in np.arange(.4,D-.4,.65):
 k=round(onset*fs);n=min(round(.60*fs),N-k);u=np.arange(n)/fs;freq=[261.63,329.63,392,440,392,329.63,293.66,329.63][int(onset/.65)%8];music[k:k+n]+=.0045*(np.sin(2*np.pi*freq*u)+.18*np.sin(2*np.pi*freq*2*u))*np.exp(-u*7)*np.minimum(1,u/.015)
for freq in [130.81,164.81,196]:music+=.0006*np.sin(2*np.pi*freq*t)
music*=np.minimum(1,np.minimum(t/.5,(D-t)/.5));mix=np.stack([voice+music,voice+music],axis=1)+fx;headroom=min(1,.72/max(abs(mix.flatten())));mix*=headroom
for name,v in [('narracao',voice*headroom),('sfx',fx*headroom),('musica',music*headroom),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(v*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'seconds':D,'raw_voice_seconds':len(raw)/fs,'treated_voice_seconds':len(x)/fs,'voice_offset_seconds':offset,'gain_db':gain,'speed_change':False,'pitch_change':False,'extra_compression':False,'same_voice':'Puck/gemini-2.5-flash-preview-tts','successful_generations':1,'silences_shortened':cuts,'mix_peak_dbfs':float(20*np.log10(max(abs(mix.flatten())))),'human_full_listening':False,'asr_report':'qa/narration-check.json'},indent=2));print('AUDIO_READY',D,len(x)/fs,'anchors',anchors,flush=True)
