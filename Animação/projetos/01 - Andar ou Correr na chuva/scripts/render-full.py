"""Resumable native 1080p full-film export. No publishing or Git commands."""
from pathlib import Path
import subprocess,time,json,hashlib,argparse,shutil
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--work',required=True);ap.add_argument('--output',required=True);ap.add_argument('--audio',default=str(ROOT/'audio/mix.mp3'));a=ap.parse_args()
OUT=Path(a.work).resolve();OUT.mkdir(parents=True,exist_ok=True);DEST=Path(a.output).resolve();DEST.parent.mkdir(parents=True,exist_ok=True)
files=['film.js','direction.js','opening.js','performance.js','kinematics.js','story.js','timing.json']
source=hashlib.sha256(b''.join((ROOT/f).read_bytes() for f in files)).hexdigest()
started=time.time();queue=[];completed=[];active={}
for i in range(8):
 p=OUT/f'part-{i+1:02d}.mp4';meta=p.with_suffix('.mp4.json')
 if p.exists() and meta.exists():
  m=json.loads(meta.read_text())
  if m.get('sourceHash')==source or (i==0 and m.get('approvedPilotReused')):completed.append(i);continue
 queue.append(i)
while queue or active:
 while queue and len(active)<2:
  i=queue.pop(0);log=(OUT/f'part-{i+1:02d}.log').open('w');p=OUT/f'part-{i+1:02d}.mp4'
  proc=subprocess.Popen(['node','scripts/render.mjs','--start',str(i*60),'--duration','60','--crf','24','--output',str(p)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);active[i]=(proc,log)
 progress=[]
 for i,(proc,log) in list(active.items()):
  code=proc.poll()
  if code is not None:
   log.close()
   if code:
    for p,_ in active.values():
     if p.poll() is None:p.terminate()
    raise RuntimeError(f'Minute {i+1} failed; inspect its log')
   meta=OUT/f'part-{i+1:02d}.mp4.json';m=json.loads(meta.read_text());assert m['frames']==1440 and not m['errors'];m['sourceHash']=source;meta.write_text(json.dumps(m,indent=2));completed.append(i);del active[i];print('MINUTE_DONE',i+1,flush=True)
  else:
   r={}
   for line in reversed((OUT/f'part-{i+1:02d}.log').read_text().splitlines()):
    if line.startswith('{'):
     try:r=json.loads(line);break
     except json.JSONDecodeError:pass
   progress.append({'minute':i+1,**r})
 frames=len(completed)*1440+sum(p.get('frame',0) for p in progress)
 (OUT/'status.json').write_text(json.dumps({'stage':'render','sourceHash':source,'completedMinutes':[i+1 for i in completed],'totalFrames':11520,'renderedFrames':frames,'percent':frames/11520*100,'elapsed':time.time()-started,'active':progress},indent=2))
 if queue or active:time.sleep(2)
(OUT/'status.json').write_text(json.dumps({'stage':'assemble','percent':100,'elapsed':time.time()-started}))
(OUT/'concat.txt').write_text(''.join(f"file 'part-{i:02d}.mp4'\n" for i in range(1,9)))
RAW=OUT/'full-native-with-audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-i',a.audio,'-map','0:v','-map','1:a','-t','480','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(RAW)],check=True)
encoding='native H.264 copied; AAC160k'
if RAW.stat().st_size<95_000_000:shutil.copy2(RAW,DEST)
else:
 (OUT/'status.json').write_text(json.dumps({'stage':'encode-two-pass','percent':100,'elapsed':time.time()-started}))
 opts=['-c:v','libx264','-threads','4','-preset','slow','-b:v','1350k','-pix_fmt','yuv420p','-passlogfile',str(OUT/'x264-full')]
 with (OUT/'encode.log').open('w') as log:
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(RAW),*opts,'-pass','1','-an','-f','null','-'],stdout=subprocess.DEVNULL,stderr=log,check=True)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(RAW),*opts,'-pass','2','-c:a','copy','-movflags','+faststart',str(DEST)],stderr=log,check=True)
 encoding='native1080 H.264 two-pass1350k slow; AAC160k copied'
assert DEST.stat().st_size<100_000_000
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(DEST)]));v=next(st for st in probe['streams'] if st['codec_type']=='video');audio=next(st for st in probe['streams'] if st['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_frames']),v['r_frame_rate'])==(1920,1080,11520,'24/1')
assert abs(float(probe['format']['duration'])-480)<.05
result=subprocess.run(['ffmpeg','-v','error','-i',str(DEST),'-f','null','-'],capture_output=True,text=True,check=True);assert not result.stderr,result.stderr
report={'file':DEST.name,'pipeline':'original-threejs-canvas','sourceHash':source,'duration':float(probe['format']['duration']),'resolution':[1920,1080],'fps':24,'frames':11520,'encoding':encoding,'audio':{'codec':audio['codec_name'],'sample_rate':audio['sample_rate'],'channels':audio['channels']},'bytes':DEST.stat().st_size,'fullDecodePassed':True,'approvedPilotReused':True,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'elapsed':time.time()-started}
(OUT/'export-validation.json').write_text(json.dumps(report,indent=2));(OUT/'status.json').write_text(json.dumps({'stage':'complete',**report},indent=2));print('FULL_EXPORT_COMPLETE',json.dumps(report),flush=True)
