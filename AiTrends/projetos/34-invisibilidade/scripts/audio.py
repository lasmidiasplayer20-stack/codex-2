from pathlib import Path
import argparse,json,re,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work;cfg=json.loads((P/'config.json').read_text());theme=cfg['theme'];fs,raw=wavfile.read(W/'voice/block-01.wav');x=raw.astype(float)/32768
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice/block-01.wav'),'-af','silencedetect=noise=-36dB:d=0.22','-f','null','-'],capture_output=True,text=True,check=True);starts=[float(v)for v in re.findall('silence_start: ([0-9.]+)',r.stderr)];ends=[float(v)for v in re.findall('silence_end: ([0-9.]+)',r.stderr)];parts=[];last=0;trimmed=[]
# Preserve ordinary sentence pauses; remove only excess above .45s.
for b,e in zip(starts,ends):
 keep=min(e-b,.45)if b>.01 else .08
 parts.extend([x[last:round(b*fs)],x[round(b*fs):round((b+keep)*fs)]]);last=round(e*fs);trimmed.append({'start':b,'end':e,'kept':keep})
parts.append(x[last:]);x=np.concatenate(parts);assert len(x)/fs<29.1,'Voice too long: revise timing without speeding up';x=sosfilt(butter(2,55,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,10500,fs=fs,output='sos'),x);x-=.06*sosfilt(butter(2,[1800,4300],fs=fs,btype='bandpass',output='sos'),x)
wavfile.write(W/'voice-eq.wav',fs,(x*32767).astype(np.int16));r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice-eq.wav'),'-af','loudnorm=I=-20.5:TP=-3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-20.5-float(m['input_i']),-3.5-20*np.log10(max(abs(x))));x*=10**(gain/20);N=30*fs;voice=np.zeros(N);offset=.22;j=round(offset*fs);voice[j:j+len(x)]=x;fx=np.zeros(N);rng=np.random.default_rng(29+theme);events=[]
def add(at,dur,kind,amp=.014,freq=400,noise=True,low=2300):
 n=round(dur*fs);u=np.arange(n)/fs;env=np.sin(np.linspace(0,np.pi,n))**2
 v=sosfilt(butter(2,low,fs=fs,output='sos'),rng.normal(0,1,n))if noise else np.sin(2*np.pi*(freq*u-freq*.4*u*u/max(.01,dur)))
 if any(word in kind for word in ['wood','crate','book','bench']):v=.35*sosfilt(butter(2,700,fs=fs,output='sos'),rng.normal(0,1,n))+(.5*np.sin(2*np.pi*155*u)+.2*np.sin(2*np.pi*310*u))*np.exp(-u*18)
 if any(word in kind for word in ['basketball','ball']):v=np.sin(2*np.pi*(150*u-80*u*u))*np.exp(-u*28)+.12*rng.normal(0,1,n)*np.exp(-u*40)
 if 'electric' in kind:v=sosfilt(butter(2,1800,fs=fs,btype='highpass',output='sos'),rng.normal(0,1,n))*(.2+.8*np.sin(2*np.pi*19*u)**16)
 if any(word in kind for word in ['shimmer','chime','counter','rewind']):v=(np.sin(2*np.pi*640*u)+.45*np.sin(2*np.pi*960*u)+.25*np.sin(2*np.pi*1280*u))*np.exp(-u*4)
 k=round(at*fs);fx[k:k+n]+=amp*v*env;events.append({'seconds':at,'duration':dur,'kind':kind,'amplitude':amp})
shots=json.loads((P/'story/shots.json').read_text())['shots'];at=lambda i,p=.5:shots[i]['start']+(shots[i]['end']-shots[i]['start'])*p
patterns={0:[(0,'fall air',.6),(0,'landing thud',.1),(2,'tree creak',.8),(3,'run step',.1),(4,'wood strain',.7),(5,'wood on stone',.15),(6,'rescue steps',.2)],1:[(0,'electric magic spark',.15),(1,'lamp switch',.13),(3,'electric crackle',.8),(4,'retreat step',.1),(5,'discharge fades',.5),(6,'small light',.15)],2:[(0,'basketball bounce',.13),(1,'copy shimmer',.4),(2,'basketball net',.25),(3,'stack wooden block',.15),(5,'puzzled breath cloth',.2),(6,'soft footstep',.1)],3:[(0,'counter discovery',.25),(2,'urgent footstep',.1),(3,'bridge wood crack',.5),(4,'running gravel',.3),(5,'counter resolves',.25),(6,'clothing embrace',.2)],4:[(0,'trip shoe scrape',.2),(2,'uneven footsteps',.3),(3,'stop shoe',.1),(6,'bandage cloth',.5),(7,'bench wood',.2)],5:[(0,'invisibility shimmer',.5),(2,'unseen footsteps',.3),(3,'crate strain',.4),(4,'floating crate creak',.3),(5,'reappear air',.4),(6,'two pairs footsteps',.4)],6:[(0,'basketball net',.2),(1,'basketball bounce',.15),(2,'departing steps',.25),(3,'impossible basket',.25),(5,'ball set down',.2),(6,'celebration hands',.15)],7:[(0,'alarm clock',.25),(1,'caught ball',.15),(2,'crate falls',.2),(3,'time rewind',.6),(4,'clock tick',.1),(5,'crate caught',.15),(6,'new day chime',.4)],8:[(0,'soil planting',.3),(1,'construction wood',.3),(2,'tree wind',.7),(3,'bench creak',.3),(5,'new visitor step',.1),(6,'soil planting',.5),(7,'leaves breeze',.7)]}
for i,kind,d in patterns[theme]:add(at(i,.65 if 'landing'in kind else .45),d,kind,amp=.012 if 'electric'not in kind else .007,noise=not any(x in kind for x in ['chime','shimmer','alarm','counter']),freq=510)
for i in [3,6]:
 for q in [.25,.5,.75]:add(at(i,q),.075,'foot contact / cloth',.004,low=1200)
for time in [12.2,25.2]:add(time,.08,'CTA click',.002,noise=False,freq=650)
t=np.arange(N)/fs;music=np.zeros(N)
for f in [174.61,220,261.63]:music+=.0012*np.sin(2*np.pi*f*t)
# Gentle original marimba phrase; lift the bed only after speech ends.
voice_end=offset+len(x)/fs
lift=.23+.77*np.clip((t-voice_end+.5)/1.4,0,1)
notes=[261.63,329.63,392,440,392,329.63,293.66,261.63]
for i,onset in enumerate(np.arange(.5,29.3,.75)):
 k=round(onset*fs);n=min(round(.65*fs),N-k);u=np.arange(n)/fs;f=notes[(i+theme)%len(notes)];tone=(np.sin(2*np.pi*f*u)+.20*np.sin(2*np.pi*2*f*u))*np.exp(-u*7)*np.minimum(1,u/.012);music[k:k+n]+=.018*tone*lift[k:k+n]
fade=np.minimum(1,np.minimum(t/.5,(30-t)/.6));music*=fade;mix=np.stack([voice+fx+music,voice+.96*fx+music],axis=1);headroom=min(1,.72/max(abs(mix.flatten())));mix*=headroom
for name,v in [('narracao',voice*headroom),('sfx',fx*headroom),('musica',music*headroom),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(v*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'seconds':30,'raw_voice_seconds':len(raw)/fs,'treated_voice_seconds':len(x)/fs,'voice_offset_seconds':offset,'gain_db':gain,'speed_change':False,'pitch_change':False,'extra_compression':False,'same_voice':'Puck/gemini-2.5-flash-preview-tts','successful_generations':1,'silences_shortened':trimmed,'mix_peak_dbfs':float(20*np.log10(max(abs(mix.flatten())))),'human_full_listening':False,'asr_report':'qa/narration-check.json'},indent=2));print('AUDIO30_READY',len(x)/fs,flush=True)
