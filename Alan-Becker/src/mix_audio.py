"""Mix ElevenLabs effects and an original procedural electronic score."""
import numpy as np,subprocess,wave,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1];SR=44100;DUR=120
mix=np.zeros((SR*DUR,2),dtype=np.float32)
def add(a,at,gain=1,pan=0):
 a=np.asarray(a);a=np.column_stack((a,a)) if a.ndim==1 else a
 i=int(at*SR);n=min(len(a),len(mix)-i)
 if n>0:mix[i:i+n]+=a[:n]*gain*np.array([min(1,1-pan),min(1,1+pan)])
def note(freq,dur,at,gain=.06):
 t=np.arange(int(SR*dur))/SR;env=np.minimum(1,t/.015)*np.exp(-t*4/dur);a=(np.sin(2*np.pi*freq*t)+.2*np.sin(4*np.pi*freq*t))*env;add(a,at,gain,np.sin(at)*.25)
# Original restrained 96 BPM ostinato, opens up in the final restoration.
for beat in range(192):
 at=beat*.625;chord=[48,45,53,55][(beat//16)%4];midi=chord+[0,7,12,7][beat%4]
 note(440*2**((midi-69)/12),.5,at,.035 if at<20 else .048)
 if 20<at<100 and beat%2==0:
  t=np.arange(int(.15*SR))/SR;add(np.sin(2*np.pi*(75*t-120*t*t))*np.exp(-t*35),at,.06)
 if at>100:note(440*2**((midi+24-69)/12),1.4,at,.025)
EVENTS={'click':[7.9,10.2,30.8,34,40.5,41.5,42.5,43.5,44.5,64,66,67,100.8], 'whoosh':[20.2,22,24,26,28,33,35,37,47,51,53,55,77,79,81,83,85,87,89], 'impact':[29,49,56.2,57,90,94], 'erase':[13,23,45.5,54,91,95], 'spring':[72.5,76.2,81.2,84,87], 'restore':[101,106,112]}
for name,times in EVENTS.items():
 p=R/'audio'/f'{name}.mp3'
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','2','-ar',str(SR),'-'])
 a=np.frombuffer(raw,np.float32).reshape(-1,2)
 for at in times:add(a,at,.35 if name in ['erase','restore'] else .48,np.sin(at)*.35)
# Discreet run contacts, deterministic soft ticks.
for start,end in [(2,7),(20,28),(80,89)]:
 for at in np.arange(start,end,.28):
  t=np.arange(int(.05*SR))/SR;add(np.sin(2*np.pi*180*t)*np.exp(-t*95),at,.05)
peak=float(np.max(np.abs(mix)));mix*=.88/max(.88,peak)
mix[:SR]*=np.linspace(0,1,SR)[:,None];mix[-SR*3:]*=np.linspace(1,0,SR*3)[:,None]
with wave.open(str(R/'audio'/'mix.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('<i2').tobytes())
(R/'audio'/'cue-sheet.json').write_text(json.dumps({'source':'ElevenLabs Sound Effects API','effects':EVENTS,'score':'Original procedural synthesis, 96 BPM','duration':120,'peak_before_normalization':peak},indent=2))
print('Mix complete',peak)
