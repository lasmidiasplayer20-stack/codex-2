"""Chuva e passos sintetizados, sem arquivos de áudio externos. Python + NumPy."""
from pathlib import Path
import wave
import numpy as np

def gerar(destino):
 sr=48000; n=60*sr; rng=np.random.default_rng(27)
 white=rng.normal(0,1,n).astype(np.float32)
 # Noise is intentionally quiet beneath the existing narration.
 rain=(white-np.roll(white,1))*.005
 t=np.arange(n)/sr; rain*=.7+.3*np.sin(t*.61)**2
 for start,end,speed,stride,gain in [(6,13,.65,.72,.035),(21,30,1.65,1.05,.05),(21,48,.55,.72,.032),(50,59,2,1.05,.045),(50,60,.9,.72,.03)]:
  for at in np.arange(start,end,stride/speed/2):
   count=int(.11*sr); q=np.arange(count)/sr
   hit=(np.sin(2*np.pi*95*q)*np.exp(-q*45)+rng.normal(size=count)*np.exp(-q*75)*.5)*gain
   i=int(at*sr); rain[i:i+count]+=hit[:min(count,n-i)]
 pcm=(np.clip(rain,-1,1)*32767).astype('<i2')
 with wave.open(str(destino),'wb') as w:w.setparams((1,2,sr,n,'NONE','not compressed'));w.writeframes(pcm.tobytes())
if __name__=='__main__':gerar(Path(__file__).with_name('efeitos-60s.wav'))
