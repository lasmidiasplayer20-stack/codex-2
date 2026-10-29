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
extra=88.7-len(x)/fs-.25;per=extra/len(pairs);assert 0<per<.8
out=[];last=0;insert=[]
for a,b in pairs:
 idx=round((a+b)*.5*fs);out.extend([x[last:idx],np.zeros(round(per*fs))]);insert.append({'raw_time':idx/fs,'insert_seconds':per});last=idx
out.append(x[last:]);x=np.concatenate([np.zeros(round(.25*fs)),*out]);x=np.pad(x,(0,90*fs-len(x)))
# Gentle broad EQ and one static gain: no dynamic pumping, no extra compressor.
x=sosfilt(butter(2,65,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,9500,fs=fs,output='sos'),x)
# Broad mid reduction via a band component, preserving speech presence.
mid=sosfilt(butter(2,[1500,4300],fs=fs,btype='bandpass',output='sos'),x);x=x-.14*mid
# Measure THIS generation; never reuse the previous episode's corrective envelope.
def active_windows(v):
 rows=[]
 for a,b in [(0,18),(18,36),(36,54),(54,72),(72,90)]:
  y=v[round(a*fs):round(b*fs)];n=len(y)//(fs//10);r=np.sqrt(np.mean(y[:n*(fs//10)].reshape(n,-1)**2,axis=1));r=r[r>10**(-40/20)];rows.append(float(20*np.log10(np.median(r))))
 return rows
before=active_windows(x);drift_times=[0,9,27,45,63,81,90];levels=np.array(before);corrections=np.clip(np.median(levels)-levels,-6,6)if np.ptp(levels)>2.5 else np.zeros(5);drift_db=[float(corrections[0]),*map(float,corrections),float(corrections[-1])]
x*=10**(np.interp(np.arange(len(x))/fs,drift_times,drift_db)/20);after=active_windows(x)
wavfile.write(W/'eq.wav',fs,(np.clip(x,-1,1)*32767).astype(np.int16))
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'eq.wav'),'-af','loudnorm=I=-19.5:TP=-4.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-19.5-float(m['input_i']),-4.5-20*np.log10(max(abs(x))));x*=10**(gain/20)
N=90*fs;t=np.arange(N)/fs;rng=np.random.default_rng(9);sfx=np.zeros(N);events=[]
def tone(at,dur,f,amp,kind):
 n=round(dur*fs);u=np.arange(n)/fs;env=np.sin(np.pi*np.arange(n)/n)**2;v=amp*np.sin(2*np.pi*(f*u+f*.1*u*u))*env;j=round(at*fs);sfx[j:j+n]+=v[:N-j];events.append({'seconds':at,'kind':kind,'duration':dur})
def noise(at,dur,amp,kind,low=3000):
 n=round(dur*fs);v=rng.normal(0,1,n);v=sosfilt(butter(2,low,fs=fs,output='sos'),v);v*=amp*np.sin(np.pi*np.arange(n)/n)**2;j=round(at*fs);sfx[j:j+n]+=v[:N-j];events.append({'seconds':at,'kind':kind,'duration':dur})
shots=json.loads((P/'story/shots.json').read_text())['shots'];starts={s['params']['cam']:s['start']for s in shots};ends={s['params']['cam']:s['end']for s in shots}
for cam in ['approach','open','push','close','share']:
 for at in np.arange(starts[cam]+.18,ends[cam],.48):noise(float(at),.09,.007,'sneaker on kitchen floor',1500)
noise(starts['open']+.15,.24,.009,'fridge gasket release',1200);noise(ends['close']-.25,.20,.010,'fridge door seal / latch',1600)
for cam in ['evaporator','condenser','expand']:noise(starts[cam]+.15,.5,.0028,'soft refrigerant flow illustration',3500)
noise(starts['fan']+.3,.11,.007,'fan switch click',2200)
# Gentle fan-air bed and very soft compressor hum; no hard repetitive percussion.
fanenv=np.clip((t-starts['fan'])/1.2,0,1)*np.clip((90-t)/1.0,0,1);air=sosfilt(butter(2,[400,3000],fs=fs,btype='bandpass',output='sos'),rng.normal(0,1,N));sfx+=air*.0018*fanenv
humenv=np.clip((t-starts['open'])/1.5,0,1)*np.clip((starts['rest']-t)/1.5,0,1);sfx+=.0009*np.sin(2*np.pi*83*t)*humenv
events.extend([{'seconds':starts['fan'],'duration':90-starts['fan'],'kind':'quiet fan air generated from filtered noise'},{'seconds':starts['open'],'duration':starts['rest']-starts['open'],'kind':'subtle compressor hum'}])
for base in [15,81]:
 for dt,f in [(1.6,610),(3.1,740),(5.7,980)]:tone(base+dt,.11,f,.005,'CTA click / subscribe / bell')
music=np.zeros(N)
for at in [0,15,31,47,63,79]:
 for f in [130.81,196,261.63]:
  n=fs*4;u=np.arange(n)/fs;j=round(at*fs);music[j:j+n]+=.0018*np.sin(2*np.pi*f*u)*np.sin(np.pi*np.arange(n)/n)**2
mix=np.stack([x+sfx+music,x+sfx*.9+music],axis=1);assert max(abs(mix.flatten()))<.8
for name,a in [('narracao',x),('sfx',sfx),('musica',music),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(np.clip(a,-1,1)*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'seconds':90,'samples':N,'sample_rate':fs,'voice_gain_db':gain,'slow_gain_automation':{'seconds':drift_times,'db':drift_db,'reason':'Measure this episode only; broad fixed gain compensation when spread exceeds2.5dB','before_active_window_dbfs':before,'after_active_window_dbfs':after,'before_spread_db':float(np.ptp(before)),'after_spread_db':float(np.ptp(after))},'voice_peak_dbfs':20*np.log10(max(abs(x))),'mix_peak_dbfs':20*np.log10(max(abs(mix.flatten()))),'speed_change':False,'extra_compression':False,'pause_insertions':insert,'human_listening':False,'note':'Same Puck one call; short added gaps only inside detected silence, no removed speech. Timing approximate, not ASR.'},indent=2))
print('MIX_90_SECONDS_OK',gain)
