from pathlib import Path
import argparse,json,re,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work
fs,raw=wavfile.read(W/'voice/block-01.wav');x=raw.astype(float)/32768
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice/block-01.wav'),'-af','silencedetect=noise=-34dB:d=0.12','-f','null','-'],capture_output=True,text=True,check=True);starts=[float(v)for v in re.findall('silence_start: ([0-9.]+)',r.stderr)];ends=[float(v)for v in re.findall('silence_end: ([0-9.]+)',r.stderr)];parts=[];last=0;trimmed=[]
for b,e in zip(starts,ends):
 if b<.01:keep=.08
 elif e>len(x)/fs-.01:keep=.10
 else:keep=min(e-b,.18)
 parts.append(x[last:round(b*fs)]);parts.append(x[round(b*fs):round((b+keep)*fs)]);last=round(e*fs);trimmed.append({'start':b,'end':e,'kept_seconds':keep})
parts.append(x[last:]);x=np.concatenate(parts);x=sosfilt(butter(2,55,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,10500,fs=fs,output='sos'),x);x-=.08*sosfilt(butter(2,[1500,4300],fs=fs,btype='bandpass',output='sos'),x)
wavfile.write(W/'voice-eq.wav',fs,(x*32767).astype(np.int16));r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice-eq.wav'),'-af','loudnorm=I=-22.2:TP=-4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-22.2-float(m['input_i']),-4-20*np.log10(max(abs(x))));x*=10**(gain/20)
N=15*fs;t=np.arange(N)/fs;voice=np.zeros(N);offset=.25;j=round(offset*fs);assert j+len(x)<N-fs;voice[j:j+len(x)]=x;fx=np.zeros(N);events=[];rng=np.random.default_rng(28)
def add(at,dur,kind,amp=.012,freq=600,noise=False,low=3000):
 n=round(dur*fs);u=np.arange(n)/fs;env=np.sin(np.linspace(0,np.pi,n))**2
 if noise:v=sosfilt(butter(2,low,fs=fs,output='sos'),rng.normal(0,1,n))
 else:v=np.sin(2*np.pi*(freq*u-freq*.45*u*u/max(dur,.01)))+.22*np.sin(2*np.pi*freq*2.1*u)
 v*=amp*env;k=round(at*fs);fx[k:k+n]+=v;events.append({'seconds':at,'duration':dur,'kind':kind})
add(.98,.12,'button click',.012,noise=True,low=1700);add(1.2,.25,'piston wood impact',.022,180);add(1.26,.38,'launch air',.009,noise=True,low=4200);add(3.30,.40,'slime boing',.023,460);add(5.50,.12,'landing on planks',.012,noise=True,low=950);add(5.90,.30,'upper piston mechanism',.018,240);add(7.20,3.25,'water chute',.009,noise=True,low=5400);add(7.45,.30,'water splash',.010,noise=True,low=2600);add(10.50,.20,'splash on exit',.015,noise=True,low=2400)
for at in [7.5,8.05,8.65,9.25,9.85]:add(at,.13,'foot splash / balance on chute',.006,noise=True,low=3600)
# Match the cubic displacement of the return run, approximately one footfall per .55 m.
for d in np.arange(.22,3.7165,.55):
 y=min(.999,d/3.7165);u=(y/4)**(1/3)if y<.5 else 1-((1-y)/4)**(1/3);add(10.5+2.6*u,.09,'shoe on cobblestone',.010,noise=True,low=1200)
for at in [13.35,13.86,14.22]:add(at,.07,'approach step',.006,noise=True,low=1300)
for at,freq in [(5.9,610),(7.7,740),(10.1,980)]:add(at,.09,'quiet CTA click',.0028,freq)
# Integer cycles and phase denominator N-1 make the PCM first and last samples identical.
phase=np.arange(N)/(N-1);music=np.zeros(N)
for f in [220,264,330]:music+=.0013*np.sin(2*np.pi*(f*15)*phase)*(.7+.3*np.cos(2*np.pi*phase))
left=voice+fx+music;right=voice+.95*fx+music;mix=np.stack([left,right],axis=1);headroom=min(1,.68/max(abs(mix.flatten())));mix*=headroom
for name,v in [('narracao',voice*headroom),('sfx',fx*headroom),('musica',music*headroom),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(v*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'seconds':15,'raw_voice_seconds':len(raw)/fs,'treated_voice_seconds':len(x)/fs,'voice_offset_seconds':offset,'gain_db':gain,'headroom_gain':headroom,'speed_change':False,'pitch_change':False,'extra_compression':False,'same_voice':'Puck/gemini-2.5-flash-preview-tts','successful_generations':1,'silences_shortened':trimmed,'pcm_first_last_sample_equal':bool(np.allclose(mix[0],mix[-1],atol=1e-10)),'music_periodic':True,'mix_peak_dbfs':float(20*np.log10(max(abs(mix.flatten())))),'human_full_listening':False,'asr':(P/'qa/narration-check.json').exists(),'asr_report':'qa/narration-check.json','successful_generations_scope':'one replacement generation in revision 2; original superseded'},indent=2));print('AUDIO15_READY',len(x)/fs,flush=True)
