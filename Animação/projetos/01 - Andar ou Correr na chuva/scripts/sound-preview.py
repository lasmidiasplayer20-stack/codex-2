"""Procedural 60-second Foley for the original Three.js/Canvas pilot. Python + NumPy."""
from pathlib import Path
import wave,argparse
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'audio'/'efeitos-preview.wav'));a=ap.parse_args()
sr=48000;n=sr*60;rng=np.random.default_rng(31);white=rng.normal(size=n);mix=(white-np.roll(white,1))*.004

def hit(at,duration,gain,splash=False):
 count=int(duration*sr);t=np.arange(count)/sr
 v=rng.normal(size=count)*np.exp(-t*13)*gain if splash else (np.sin(t*2*np.pi*95)*np.exp(-t*48)+rng.normal(size=count)*np.exp(-t*65)*.45)*gain
 i=int(at*sr);mix[i:i+count]+=v[:min(count,n-i)]
for start,end,cadence,gain in [(4.5,9.3,.675,.026),(19.5,28,.372,.040),(20,46.5,.875,.026),(50.8,58.8,.362,.038),(50.8,60,.656,.026)]:
 for at in np.arange(start,end,cadence):hit(at,.12,gain)
hit(20.95,.55,.032,True);hit(47.6,.12,.025)
p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(p),'wb') as f:f.setparams((1,2,sr,n,'NONE','not compressed'));f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
