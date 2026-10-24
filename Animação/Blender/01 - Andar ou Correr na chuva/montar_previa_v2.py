"""Muxes the actual 1440 rendered frames with narration and synthesized Foley."""
from pathlib import Path
import argparse,subprocess,json,hashlib
BASE=Path(__file__).resolve().parent

def montar(frames,destino):
 frames=Path(frames);destino=Path(destino)
 assert all((frames/f'frame-{f:04d}.jpg').exists() for f in range(1,1441))
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(frames/'frame-%04d.jpg'),'-i',str(BASE/'narracao-60s.wav'),'-i',str(BASE/'efeitos-v2.wav'),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]','-map','0:v','-map','[a]','-c:v','libx264','-preset','fast','-crf','22','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t','60','-movflags','+faststart',str(destino)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(destino)]));v=next(st for st in probe['streams'] if st['codec_type']=='video')
 assert (v['width'],v['height'],int(v['nb_frames']))==(1920,1080,1440)
 assert abs(float(probe['format']['duration'])-60)<.05
 assert destino.stat().st_size<95_000_000
 subprocess.run(['ffmpeg','-v','error','-i',str(destino),'-f','null','-'],check=True)
 return {'duration':float(probe['format']['duration']),'frames':int(v['nb_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'bytes':destino.stat().st_size,'sha256':hashlib.sha256(destino.read_bytes()).hexdigest(),'full_decode_passed':True}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--frames',default=str(BASE/'renders-v2'));ap.add_argument('--out',default=str(BASE/'02 - Preview 60s.mp4'));a=ap.parse_args()
 print(json.dumps(montar(a.frames,a.out),indent=2))
