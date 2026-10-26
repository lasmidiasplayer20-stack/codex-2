from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1];cfg=json.loads((P/'config.json').read_text());beats=json.loads((P/'story/beats.json').read_text());rate=24000;n=round(cfg['duration']*rate);bed=np.zeros(n,np.float32);rng=np.random.default_rng(505);events=[]
def add(at,y):
 k=round(at*rate);end=min(n,k+len(y));
 if k>=0 and k<n:bed[k:end]+=y[:end-k]
def note(at,f,d=8,amp=.0018):
 t=np.arange(round(d*rate))/rate;add(at,amp*np.sin(2*np.pi*f*t)*(1-np.exp(-t/1.1))*np.exp(-t/4))
# Opening matches approved mix. Rest uses sparse quiet harmonic chords, no percussion loop.
for at,f in [(0,196),(0,246.94),(0,293.66),(8,174.61),(8,220),(8,261.63),(15,196),(15,246.94),(15,293.66)]:note(at,f)
for i,b in enumerate(beats[1:],1):
 if b['action'] in ['despedida','isolado']:continue
 chord=[196,246.94,293.66]if i%2 else[174.61,220,261.63]
 for at in np.arange(b['start']+.2,b['end']-1,10):
  for f in chord:note(at,f,amp=.0016)
# Single events only; voice remains foreground.
for b in beats:
 if b['action'] in ['caixa','cadeira','vizinha','presente','retorno']:
  at=b['start']+(b['end']-b['start'])*.45;d=.07;t=np.arange(round(d*rate))/rate;y=.004*rng.normal(size=len(t))*np.exp(-t*90);add(at,y);events.append({'time':at,'event':'soft_wood_contact'})
for a,z in cfg['ctaSeconds']:
 t=np.arange(round(.18*rate))/rate;add(a+1,.0025*np.sin(2*np.pi*880*t)*np.exp(-t*20));events.append({'time':a+1,'event':'quiet_cta_note'})
# Smooth speech-driven attenuation. Bed is already far below speech.
sr,voice=wavfile.read(P/'audio/narracao.wav');assert sr==rate and len(voice)==n
voice=voice.astype(np.float32)/32768
hop=2400;chunks=int(np.ceil(n/hop));rms=np.array([np.sqrt(np.mean(voice[i*hop:min((i+1)*hop,n)]**2))for i in range(chunks)])
duck=np.interp(np.arange(n),np.arange(chunks)*hop,np.where(rms>.015,.65,1.0));bed*=duck
fade=np.minimum(np.arange(n)/(rate*1),1)*np.minimum((n-1-np.arange(n))/(rate*1.4),1);bed*=fade
mix=voice+bed;assert np.max(np.abs(mix))<.98
wavfile.write(P/'audio/trilha.wav',rate,np.round(bed*32767).astype(np.int16));wavfile.write(P/'audio/mix.wav',rate,np.round(mix*32767).astype(np.int16))
for source in ['trilha','mix']:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'audio'/f'{source}.wav'),'-ar','48000','-ac','2','-c:a','libmp3lame','-b:a','192k',str(P/'audio'/f'{source}.mp3')],check=True)
(P/'audio/sound-design.json').write_text(json.dumps({'method':'Original NumPy harmonies and isolated wooden Foley, no samples or APIs.','approved_reference':'03-voz-com-mix.mp3 approved by user','music_peak_dbfs':float(20*np.log10(max(np.max(np.abs(bed)),1e-12))),'voice_peak_dbfs':float(20*np.log10(np.max(np.abs(voice)))),'mix_peak_dbfs':float(20*np.log10(np.max(np.abs(mix)))),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'events':events,'no_time_stretch':True},ensure_ascii=False,indent=2)+'\n')
print('SOUND_COMPLETE',cfg['duration'],flush=True)
