"""Render and validate the 60s pilot using the original Three.js/Canvas pipeline."""
from pathlib import Path
import argparse,subprocess,time,json,hashlib,tempfile,re
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(ROOT/'preview-60s.mp4'));ap.add_argument('--work',default=None);ap.add_argument('--audio',default=str(ROOT/'audio'/'mix.mp3'));a=ap.parse_args()
work=Path(a.work or tempfile.mkdtemp(prefix='rain-preview-'));work.mkdir(parents=True,exist_ok=True);dest=Path(a.output).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
started=time.time();jobs=[]
for k in range(2):
 log=(work/f'part-{k+1:02d}.log').open('w')
 p=work/f'part-{k+1:02d}.mp4'
 jobs.append(subprocess.Popen(['node','scripts/render.mjs','--start',str(k*30),'--duration','30','--output',str(p)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT))
while any(p.poll() is None for p in jobs):
 progress=[]
 for k in range(2):
  lines=(work/f'part-{k+1:02d}.log').read_text().splitlines();r={}
  for line in reversed(lines):
   if line.startswith('{'):
    try:r=json.loads(line);break
    except json.JSONDecodeError:pass
  progress.append(r)
 (work/'status.json').write_text(json.dumps({'elapsed':time.time()-started,'workers':[p.poll() for p in jobs],'parts':progress},indent=2))
 if any(p.poll() not in [None,0] for p in jobs):
  for p in jobs:
   if p.poll() is None:p.terminate()
  raise RuntimeError('Render failed; check part logs')
 time.sleep(2)
assert all(p.returncode==0 for p in jobs)
(work/'parts.txt').write_text("file 'part-01.mp4'\nfile 'part-02.mp4'\n")
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(work/'parts.txt'),'-i',a.audio,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(dest)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)]));v=next(st for st in probe['streams'] if st['codec_type']=='video')
assert (v['width'],v['height'],int(v['nb_frames']))==(1920,1080,1440)
assert abs(float(probe['format']['duration'])-60)<.05
assert dest.stat().st_size<95_000_000
subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-f','null','-'],check=True)
volume=subprocess.run(['ffmpeg','-hide_banner','-i',str(dest),'-af','volumedetect','-vn','-f','null','-'],capture_output=True,text=True,check=True).stderr
peak=re.search(r'max_volume:\s*([-\d.]+) dB',volume);peak=float(peak.group(1)) if peak else None
report={'pipeline':'original-threejs-canvas','duration':float(probe['format']['duration']),'width':1920,'height':1080,'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'bytes':dest.stat().st_size,'full_decode_passed':True,'peak_dbfs':peak,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'elapsed':time.time()-started}
(work/'video-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
