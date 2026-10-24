"""Rain, footfalls, splash and greeting, synthesized with NumPy; no samples."""
from pathlib import Path
import wave
import numpy as np
sr=48000;n=sr*60;rng=np.random.default_rng(29)
w=rng.normal(size=n);mix=(w-np.roll(w,1))*.004

def hit(at,duration,gain,kind='step'):
 count=int(duration*sr);t=np.arange(count)/sr
 if kind=='step':v=(np.sin(t*2*np.pi*95)*np.exp(-t*48)+rng.normal(size=count)*np.exp(-t*65)*.45)*gain
 else:v=rng.normal(size=count)*np.exp(-t*12)*gain
 i=int(at*sr);mix[i:i+count]+=v[:min(count,n-i)]
# Heel strikes are quiet under narration; the run has a faster cadence.
for start,end,cadence,gain in [(5.5,11.2,.60,.027),(21.5,29.6,.395,.040),(22,47.2,.775,.026),(50.7,59.5,.355,.038),(50.7,60,.53,.027)]:
 for at in np.arange(start,end,cadence):hit(at,.12,gain)
hit(23.0,.6,.032,'splash');hit(47.5,.12,.025)
with wave.open(str(Path(__file__).with_name('efeitos-v2.wav')),'wb') as f:f.setparams((1,2,sr,n,'NONE','not compressed'));f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
