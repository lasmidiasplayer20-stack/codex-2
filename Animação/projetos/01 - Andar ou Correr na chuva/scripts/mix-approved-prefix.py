"""Preserve the approved opening audio while updating the rest of the 480s mix."""
from pathlib import Path
import subprocess,argparse,tempfile,shutil,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--approved',required=True);ap.add_argument('--wav-output');a=ap.parse_args()
with tempfile.TemporaryDirectory(prefix='rain-audio-') as tmp:
 tmp=Path(tmp);wav=Path(a.wav_output) if a.wav_output else tmp/'full.wav';wav.parent.mkdir(parents=True,exist_ok=True)
 filters='[0:a]atrim=end=60,asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[p];[1:a]atrim=start=60:end=480,asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[t];[p][t]concat=n=2:v=0:a=1[a]'
 subprocess.run(['ffmpeg','-v','error','-y','-i',a.approved,'-i',str(ROOT/'audio/mix.mp3'),'-filter_complex',filters,'-map','[a]','-c:a','pcm_s16le',str(wav)],check=True)
 final=tmp/'mix.mp3';subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(final)],check=True)
 ready=ROOT/'audio/mix-ready.mp3';shutil.copy2(final,ready);ready.replace(ROOT/'audio/mix.mp3')
 with wave.open(str(wav),'rb') as f:
  rate=f.getframerate();channels=f.getnchannels();n=f.getnframes();samples=np.frombuffer(f.readframes(n),dtype='<i2').astype(np.float32)/32768
 report={'duration':n/rate,'sample_rate':rate,'channels':channels,'approved_prefix_seconds':60,'narration_regenerated':False,'peak_dbfs':float(20*np.log10(max(1e-12,float(np.max(np.abs(samples)))))),'clipped_samples':int(np.count_nonzero(np.abs(samples)>=1))}
 assert abs(report['duration']-480)<.01 and not report['clipped_samples']
 (ROOT/'qa/audio-full-r4.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
