from pathlib import Path
import re,json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1];import argparse
a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work;
subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice/block-01.wav'),'-af','silencedetect=noise=-34dB:d=0.13','-f','null','-'],stdout=subprocess.DEVNULL,stderr=(W/'silences.log').open('w'),check=True)
fs,x=wavfile.read(W/'voice/block-01.wav');x=x.astype(np.float64)/32768
# Insert short visual beats only in existing sustained gaps; preserve all speech samples and pitch.
log=(W/'silences.log').read_text();starts=list(map(float,re.findall('silence_start: ([0-9.]+)',log)));ends=list(map(float,re.findall('silence_end: ([0-9.]+)',log)));pairs=[(a,b)for a,b in zip(starts,ends)if .4<a<b<len(x)/fs-.4 and b-a>.35]
extra=58.7-len(x)/fs-.25;per=extra/len(pairs);assert 0<per<.5
out=[];last=0;insert=[]
for a,b in pairs:
 idx=round((a+b)*.5*fs);out.extend([x[last:idx],np.zeros(round(per*fs))]);insert.append({'raw_time':idx/fs,'insert_seconds':per});last=idx
out.append(x[last:]);x=np.concatenate([np.zeros(round(.25*fs)),*out]);x=np.pad(x,(0,60*fs-len(x)))
# Gentle broad EQ and one static gain: no dynamic pumping, no extra compressor.
x=sosfilt(butter(2,65,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,9500,fs=fs,output='sos'),x)
# Broad mid reduction via a band component, preserving speech presence.
mid=sosfilt(butter(2,[1500,4300],fs=fs,btype='bandpass',output='sos'),x);x=x-.14*mid
wavfile.write(W/'eq.wav',fs,(np.clip(x,-1,1)*32767).astype(np.int16))
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'eq.wav'),'-af','loudnorm=I=-19.5:TP=-4.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-19.5-float(m['input_i']),-4.5-20*np.log10(max(abs(x))));x*=10**(gain/20)
N=60*fs;t=np.arange(N)/fs;rng=np.random.default_rng(9);sfx=np.zeros(N);events=[]
def tone(at,dur,f,amp,kind):
 n=round(dur*fs);u=np.arange(n)/fs;env=np.sin(np.pi*np.arange(n)/n)**2;v=amp*np.sin(2*np.pi*(f*u+f*.1*u*u))*env;j=round(at*fs);sfx[j:j+n]+=v[:N-j];events.append({'seconds':at,'kind':kind,'duration':dur})
story=json.loads((P/'story/shots.json').read_text());times={sh['params']['cam']:sh['start']for sh in story['shots']}
for cam,f in [('watch',780),('alarm',880),('release',620)]:tone(times[cam]+.25,.18,f,.013,'watch click / timer / release')
# Python Foley: cloth, soft footfalls, suspended-water sparkle and final splash.
def noise(at,dur,amp,kind,low=3000):
 n=round(dur*fs);u=np.arange(n)/fs;v=rng.normal(0,1,n);v=sosfilt(butter(2,low,fs=fs,output='sos'),v);v*=amp*np.sin(np.pi*np.arange(n)/n)**2;j=round(at*fs);sfx[j:j+n]+=v[:N-j];events.append({'seconds':at,'kind':kind,'duration':dur})
for at in [times['walk']+.4,times['walk']+1.1,times['dodge']+.7,times['rescue']+.4,times['rescue']+1.0]:noise(at,.13,.012,'soft sneaker contact',1200)
noise(times['reach']+.5,.3,.004,'sleeve brushing cup',2000)
noise(times['rescue']+.6,.4,.004,'cloth during rescue',2200)
noise(times['release']+.9,.7,.018,'water splash on Nico',5000)
for i in range(5):tone(times['drops']+.2+i*.28,.45,650+i*90,.002,'suspended droplet sparkle')
# Low ambience fades to silence when the world freezes, returns on release.
amb=rng.normal(0,1,N);amb=sosfilt(butter(2,500,fs=fs,output='sos'),amb)*.001
pause=((t>=times['ball'])&(t<times['release']));amb[pause]=0;sfx+=amb
music=np.zeros(N)
for at in [0,12,26,39,53]:
 for f in [130.81,196,261.63]:
  n=fs*4;u=np.arange(n)/fs;j=round(at*fs);music[j:j+n]+=.0018*np.sin(2*np.pi*f*u)*np.sin(np.pi*np.arange(n)/n)**2
mix=np.stack([x+sfx+music,x+sfx*.9+music],axis=1);assert max(abs(mix.flatten()))<.8
for name,a in [('narracao',x),('sfx',sfx),('musica',music),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(np.clip(a,-1,1)*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'seconds':60,'samples':N,'sample_rate':fs,'voice_gain_db':gain,'voice_peak_dbfs':20*np.log10(max(abs(x))),'mix_peak_dbfs':20*np.log10(max(abs(mix.flatten()))),'speed_change':False,'extra_compression':False,'pause_insertions':insert,'human_listening':False,'note':'Same Puck one call; short added gaps only inside detected silence, no removed speech. Timing approximate, not ASR.'},indent=2))
print('MIX_60_SECONDS_OK',gain)
