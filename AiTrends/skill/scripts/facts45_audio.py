"""Exact 45-second editorial assembly, same cached Puck, gentle EQ and Python Foley."""
from pathlib import Path
import argparse,json,re,subprocess,difflib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();P=args.project;W=args.work;cfg=json.loads((P/'config.json').read_text());theme=cfg['theme'];fs,raw=wavfile.read(W/'voice/block-01.wav');x=raw.astype(float)/32768;rawD=len(x)/fs;D=45;offset=.18;edits=json.loads((P/'story/audio-edits.json').read_text())if(P/'story/audio-edits.json').exists()else[]
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice/block-01.wav'),'-af','silencedetect=noise=-36dB:d=0.22','-f','null','-'],capture_output=True,text=True,check=True);starts=[float(v)for v in re.findall('silence_start: ([0-9.]+)',r.stderr)];ends=[float(v)for v in re.findall('silence_end: ([0-9.]+)',r.stderr)];silences=[(b,e)for b,e in zip(starts,ends)];deleted=[]
for b,e in silences:
 keep=min(e-b,.45)if b>.01 else .08
 if e-b>keep:deleted.append((b+keep,e))
for e in edits:deleted.append((e['raw_start'],e['raw_end']))
deleted.sort();merged=[]
for b,e in deleted:
 if merged and b<=merged[-1][1]:merged[-1]=(merged[-1][0],max(e,merged[-1][1]))
 else:merged.append((b,e))
def mapraw(t):return t-sum(max(0,min(t,e)-b)for b,e in merged if t>b)
parts=[];last=0
for b,e in merged:parts.append(x[round(last*fs):round(b*fs)]);last=e
parts.append(x[round(last*fs):]);x=np.concatenate(parts);treatedD=len(x)/fs
assert treatedD<44.2,f'Voice too long ({treatedD:.2f}); edit sentences, do not speed up.'
rawbeats=json.loads((P/'story/beats.json').read_text());asr=json.loads((P/'qa/narration-check.json').read_text());segments=asr['segments'];scale=rawD/max(s['end']for s in segments);norm=lambda s:re.sub(r'[^\w]+',' ',s.lower()).split();actual=[];wordTimes=[]
for s in segments:
 words=norm(s['text']);actual+=words;wordTimes += [(s['start']+(s['end']-s['start'])*i/max(1,len(words)))*scale for i in range(len(words))]
# Beat boundaries are approximate ASR timings rescaled to actual PCM, then snapped to nearby real quiet intervals.
boundaries=[0.0];previous=0
for beat in rawbeats[1:]:
 prefix=norm(beat['text'])[:5];matches=[i for i in range(previous,len(actual)-len(prefix)+1)if actual[i:i+len(prefix)]==prefix]
 if matches:i=matches[0];estimated=wordTimes[i];previous=i
 else:estimated=rawD*sum(len(norm(b['text']))for b in rawbeats[:len(boundaries)])/sum(len(norm(b['text']))for b in rawbeats)
 candidates=[(b,e)for b,e in silences if abs((b+e)/2-estimated)<1.5 and b>boundaries[-1]+.7]
 if candidates:
  b,e=min(candidates,key=lambda q:abs((q[0]+q[1])/2-estimated)-.3*(q[1]-q[0]));t=b+min(.22,(e-b)/2)
 else:t=estimated
 boundaries.append(t)
boundaries.append(rawD);mapped=[mapraw(t)for t in boundaries];assert all(b>a for a,b in zip(mapped,mapped[1:])),mapped
# Keep a short musical resolution. Extra short pauses are placed between ideas, never inside a word.
extra=max(0,43.35-offset-treatedD);per=min(extra/5,.72);pads=[0]+[per]*5+[0];newparts=[];timings=[];cursor=offset
for i,(b,e)in enumerate(zip(mapped,mapped[1:])):
 if i:pad=np.zeros(round(pads[i]*fs));newparts.append(pad);cursor+=len(pad)/fs
 segment=x[round(b*fs):round(e*fs)];timings.append({'beat':i,'start':cursor,'end':cursor+len(segment)/fs,'raw_start':boundaries[i],'raw_end':boundaries[i+1]});newparts.append(segment);cursor+=len(segment)/fs
x=np.concatenate(newparts);voiceEnd=offset+len(x)/fs;assert voiceEnd<44.5
x=sosfilt(butter(2,55,fs=fs,btype='highpass',output='sos'),x);x=sosfilt(butter(2,10500,fs=fs,output='sos'),x);x-=.06*sosfilt(butter(2,[1800,4300],fs=fs,btype='bandpass',output='sos'),x)
wavfile.write(W/'voice-eq.wav',fs,(x*32767).astype(np.int16));r=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'voice-eq.wav'),'-af','loudnorm=I=-20.5:TP=-3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];gain=min(-20.5-float(m['input_i']),-3.7-20*np.log10(max(abs(x))));x*=10**(gain/20);N=D*fs;voice=np.zeros(N);k=round(offset*fs);voice[k:k+len(x)]=x;fx=np.zeros((N,2));rng=np.random.default_rng(theme*29);events=[]
def add(t,d,kind,a=.012,pan=0):
 k=round(t*fs);n=min(round(d*fs),N-k)
 if n<=0:return
 u=np.arange(n)/fs;noise=rng.normal(0,1,n);env=np.sin(np.linspace(0,np.pi,n))**2
 if kind=='footstep':v=sosfilt(butter(2,950,fs=fs,output='sos'),noise)*np.exp(-u*45)+.22*np.sin(2*np.pi*140*u)*np.exp(-u*35)
 elif kind in ['chip tap','wood tap']:v=(np.sin(2*np.pi*(750 if kind=='chip tap'else 175)*u)+.38*np.sin(2*np.pi*(1230 if kind=='chip tap'else 350)*u))*np.exp(-u*30)+.15*noise*np.exp(-u*65)
 elif kind in ['paper','cloth']:v=sosfilt(butter(2,[1000,4800],fs=fs,btype='bandpass',output='sos'),noise)*env*.38
 elif kind=='rain':v=sosfilt(butter(2,[700,5200],fs=fs,btype='bandpass',output='sos'),noise)*(.7+.3*np.sin(u*1.8))*env*.18
 elif kind in ['wind','train','hydraulic','motor']:v=sosfilt(butter(2,900 if kind=='wind'else 450,fs=fs,output='sos'),noise)*env*.5+.13*np.sin(2*np.pi*([55,95,110,150][['wind','train','hydraulic','motor'].index(kind)])*u)*env
 elif kind=='masonry':v=sosfilt(butter(2,1500,fs=fs,output='sos'),noise)*np.exp(-u*16)+.15*np.sin(2*np.pi*220*u)*np.exp(-u*25)
 else:v=(np.sin(2*np.pi*640*u)+.38*np.sin(2*np.pi*960*u))*env*np.exp(-u*5)
 fx[k:k+n,0]+=a*v*np.sqrt((1-pan)/2);fx[k:k+n,1]+=a*v*np.sqrt((1+pan)/2);events.append({'seconds':t,'duration':n/fs,'kind':kind,'amplitude':a,'pan':pan})
scene_bounds=[0]+[t['start']for t in timings[1:]]+[45]
at=lambda i,q=.5:scene_bounds[i]+(scene_bounds[i+1]-scene_bounds[i])*q
# Derived events; below steps use the same stance/distance phase as the original rig.
def footsteps(b,e,distance):
 stride=.31/.6;steps=int(distance/stride*2)
 for i in range(1,steps+1):
  wanted=(i/2)*stride/distance;lo,hi=0,1
  for _ in range(24):
   mid=(lo+hi)/2
   if mid*mid*(3-2*mid)<wanted:lo=mid
   else:hi=mid
  t=b+(e-b)*(lo+hi)/2
  if t<e-.04:add(t,.09,'footstep',.012,-.16 if i%2 else .16)
if theme==39:
 add(.0,44.8,'rain',.035);add(at(3,0),timings[3]['end']-timings[3]['start'],'wind',.008);footsteps(at(0,.6),at(1,.75),3.05);add(at(2,0),.8,'cloth',.015)
if theme==40:
 for t in [at(0,.65),at(2,.25),at(3,.55)]:add(t,.09,'gentle chime',.003)
 add(at(4,0),44.6-at(4,0),'train',.023);footsteps(at(5,0),at(5,1),.70)
if theme==41:
 add(at(0,.65),.22,'paper',.025)
 for t in [at(1,.12),at(1,.30),at(1,.52),at(1,.76),at(2,.15),at(2,.45),at(2,.7)]:add(t,.10,'chip tap',.020,float(rng.uniform(-.3,.3)))
 add(at(4,.20),.16,'chip tap',.014)
if theme==42:
 add(at(1,.35),.32,'paper',.020);add(at(2,0),timings[2]['end']-timings[2]['start'],'hydraulic',.028);add(at(3,0),timings[3]['end']-timings[3]['start'],'motor',.022);footsteps(at(3,0),at(3,1),3.0)
if theme==43:
 add(.0,44.6,'motor',.012)
 for t in np.arange(.7,44,1.8):add(float(t),.10,'wood tap',.004,-.2 if int(t)%2 else .2)
if theme==44:
 add(at(1,.3),.35,'paper',.025)
 for t in np.linspace(at(2,.10),at(2,.90),12):add(float(t),.10,'masonry',.010)
 footsteps(at(5,0),at(5,1),.65);add(at(5,.75),.3,'paper',.016)
for t in [15.2,37.2]:add(t,.10,'gentle chime',.002)
t=np.arange(N)/fs;music=np.zeros(N)
for onset in np.arange(.5,44.7,.75):
 k=round(onset*fs);n=min(round(.65*fs),N-k);u=np.arange(n)/fs;f=[261.63,329.63,392,440,392,329.63,293.66,261.63][(int(onset/.75)+theme)%8];amp=.0045 if onset<voiceEnd else .009;music[k:k+n]+=amp*(np.sin(2*np.pi*f*u)+.15*np.sin(2*np.pi*f*2*u))*np.exp(-u*7)*np.minimum(1,u/.015)
for f in [130.81,164.81,196.0]:music+=.0005*np.sin(2*np.pi*f*t)
music*=np.minimum(1,np.minimum(t/.5,(D-t)/.6));mix=np.stack([voice+music,voice+music],axis=1)+fx;headroom=min(1,.72/max(abs(mix.flatten())));mix*=headroom
for name,data in [('narracao',voice*headroom),('sfx',fx*headroom),('musica',music*headroom),('mix',mix)]:
 wavfile.write(P/f'audio/{name}.wav',fs,(data*32767).astype(np.int16));subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/f'audio/{name}.wav'),'-c:a','libmp3lame','-b:a','192k',str(P/f'audio/{name}.mp3')],check=True)
(P/'story/timing.json').write_text(json.dumps({'duration':45,'voice_offset':offset,'voice_end':voiceEnd,'beats':timings,'boundary_method':'Approximate ASR, rescaled to actual PCM duration, nearest detected quiet interval; not word-perfect forced alignment','asr_duration_scale':scale,'added_inter_beat_pauses_seconds':per,'deleted_raw_intervals':merged,'editorial_edits':edits},indent=2));(P/'audio/sfx-events.json').write_text(json.dumps(events,indent=2));(P/'audio/quality.json').write_text(json.dumps({'raw_voice_seconds':rawD,'treated_speech_before_added_pauses':treatedD,'voice_end_seconds':voiceEnd,'gain_db':gain,'speed_change':False,'pitch_change':False,'extra_compression':False,'voice':'Puck/gemini-2.5-flash-preview-tts','successful_generations':1,'mix_peak_dbfs':float(20*np.log10(max(abs(mix.flatten())))),'human_full_listening':False},indent=2))
print('AUDIO45_READY',theme,'voice_end',round(voiceEnd,3),'raw',round(rawD,3),'gain',round(gain,2),'beats',[(round(x['start'],2),round(x['end'],2))for x in timings],flush=True)
