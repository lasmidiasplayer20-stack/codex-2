"""Local tonal/level correction after user feedback. No TTS/API or video-render changes."""
from pathlib import Path
import json,subprocess,argparse,shutil,re,os,math,hashlib
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parents[1]
def run(cmd):return subprocess.run([str(x)for x in cmd],check=True,text=True,capture_output=True)
def main():
 a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);args=a.parse_args();W=args.work;B=W/'audio-before-remix';B.mkdir(exist_ok=True);R=W/'remix';R.mkdir(exist_ok=True)
 for name in ['narracao.wav','narracao.mp3','mix.wav','mix.mp3','quality.json','mix-quality.json']:
  if(P/'audio'/name).exists()and not(B/name).exists():shutil.copyfile(P/'audio'/name,B/name)
 report=json.loads((P/'audio/quality.json').read_text());records=[];pieces=[];sr=24000;cuts=[2.5,1.0,2.5,3.5]
 for i in range(4):
  src=W/'voice'/f'light-{i:02}.wav';rate,original=wavfile.read(src);assert rate==sr
  # Gentle broad cuts instead of telephone band-pass or more compression.
  eq=f'equalizer=f=1750:t=q:w=1.1:g=-1.2,equalizer=f=2800:t=q:w=1.1:g=-0.8,highshelf=f=4800:t=q:w=0.7:g=-{cuts[i]},lowpass=f=10000:p=2'
  target=-20.2 if i==3 else -19.5
  result=run(['ffmpeg','-hide_banner','-i',src,'-af',eq+f',loudnorm=I={target}:TP=-4.5:LRA=10:print_format=json','-f','null','-'])
  metric=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',result.stderr,re.S)[-1]);gain=min(target-float(metric['input_i']),-4.5-float(metric['input_tp']));gain=max(-5,min(gain,2))
  dst=R/f'voice-{i:02}.wav';run(['ffmpeg','-v','error','-y','-i',src,'-af',eq+f',volume={gain}dB','-ar',sr,'-ac','1','-c:a','pcm_s16le',dst]);rate,x=wavfile.read(dst);assert rate==sr and len(x)==len(original),'Timing must remain sample-identical.';pieces.append(x.astype(np.float32)/32768)
  if i<3:pieces.append(np.zeros(round(.16*sr),np.float32))
  records.append({'block':i+1,'high_shelf_gain_db':-cuts[i],'high_shelf_hz':4800,'bell_cuts_db':{'1750Hz':-1.2,'2800Hz':-.8},'lowpass_hz':10000,'static_gain_db':round(gain,3),'eq_input_integrated_lufs':float(metric['input_i']),'eq_input_true_peak_dbfs':float(metric['input_tp']),'target_lufs':target,'samples_unchanged':True})
 voice=np.concatenate(pieces);frames=round(report['natural_seconds']*sr);assert len(voice)<=frames;voice=np.pad(voice,(0,frames-len(voice)));wavfile.write(R/'narracao.wav',sr,np.round(voice*32767).astype(np.int16))
 rate,fx=wavfile.read(P/'audio/sfx.wav');rate2,music=wavfile.read(P/'audio/trilha.wav');assert rate==rate2==sr and len(fx)==frames and len(music)==frames;mix=np.column_stack([voice,voice])+.90*(fx.astype(np.float32)+music.astype(np.float32))/32768;assert np.max(np.abs(mix))<.98
 wavfile.write(R/'mix.wav',sr,np.round(mix*32767).astype(np.int16))
 for name in ['narracao','mix']:run(['ffmpeg','-v','error','-y','-i',R/f'{name}.wav','-ar',48000 if name=='mix' else sr,'-c:a','libmp3lame','-b:a','192k',R/f'{name}.mp3']);run(['ffmpeg','-v','error','-xerror','-i',R/f'{name}.mp3','-f','null','-'])
 result={'reason':'User reports loud/harsh/megaphone-like synthetic sound toward end. Exact perceptual cause not confirmed.','method':'Gentle broad mid/high EQ and per-block static gain/true-peak headroom; last block slightly quieter. No added compression, no time/pitch changes, no new voice API.','version':2,'blocks':records,'seconds':len(voice)/sr,'source_clipped_samples':0,'new_voice_peak_dbfs':float(20*np.log10(np.max(np.abs(voice))+1e-15)),'new_mix_peak_dbfs':float(20*np.log10(np.max(np.abs(mix))+1e-15)),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'sfx_gain_relative_to_prior':.90,'new_voice_generation_calls':0,'video_frames_unchanged':True,'human_full_listening':False,'claim_to_remove_all_synthetic_timbre':False}
 # Atomic replacement ensures export never reads a partially-written audio file.
 for name in ['narracao.wav','narracao.mp3','mix.wav','mix.mp3']:os.replace(R/name,P/'audio'/name)
 (P/'audio/remix-quality.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');report['local_remix']=result;report['peak_dbfs']=result['new_voice_peak_dbfs'];(P/'audio/quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');mq=json.loads((P/'audio/mix-quality.json').read_text());mq.update(peak_dbfs=result['new_mix_peak_dbfs'],clipped_samples=result['clipped_samples'],local_remix_version=2);(P/'audio/mix-quality.json').write_text(json.dumps(mq,ensure_ascii=False,indent=2)+'\n');print('LOCAL_REMIX_COMPLETE',json.dumps(result),flush=True)
if __name__=='__main__':main()
