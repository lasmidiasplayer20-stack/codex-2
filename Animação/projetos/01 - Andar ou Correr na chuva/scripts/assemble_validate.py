"""Assemble eight contiguous minute renders, apply audio once, validate final export."""
from pathlib import Path
import subprocess,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent.parent
PARTS=Path('/workspace/rain-renders-r3')
# Override by editing this output path for another checkout; no Git commands are run here.
REPO=Path('/workspace/codex-2');PROJECT=ROOT;OUT=PARTS/'01 - Andar ou Correr na chuva.mp4'
metadata=[]
for i in range(1,9):
 p=PARTS/f'part-{i:02d}.mp4';m=json.loads(p.with_suffix('.mp4.json').read_text());assert m['start']==(i-1)*60 and m['frames']==1440 and not m['errors'];metadata.append(m)
concat=PARTS/'concat.txt';concat.write_text('\n'.join("file '"+str(PARTS/f'part-{i:02d}.mp4')+"'" for i in range(1,9)))
raw=PARTS/'complete-with-audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(ROOT/'audio/mix.mp3'),'-map','0:v:0','-map','1:a:0','-t','480','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(raw)],check=True)
if raw.stat().st_size<95_000_000:shutil.copy2(raw,OUT);encoding='copied H.264 video; AAC192k'
else:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-c:v','libx264','-threads','3','-preset','fast','-crf','27','-c:a','copy','-movflags','+faststart',str(OUT)],check=True);encoding='H.264 CRF27 fast; AAC192k copied'
assert OUT.stat().st_size<100_000_000,'Export exceeds conservative GitHub file budget'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(OUT)]));v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
assert int(v['nb_frames'])==11520 and v['r_frame_rate']=='24/1' and v['width']==1920 and v['height']==1080
assert a['codec_name']=='aac' and abs(float(d['format']['duration'])-480)<.1
check=subprocess.run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'],capture_output=True,text=True);assert check.returncode==0 and not check.stderr,check.stderr
qa=PROJECT/'qa';report={'file':OUT.name,'duration':float(d['format']['duration']),'frames':int(v['nb_frames']),'fps':24,'resolution':[1920,1080],'audio':{'codec':a['codec_name'],'sample_rate':a['sample_rate'],'channels':a['channels']},'encoding':encoding,'complete_decode':True,'decode_stderr':check.stderr,'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'parts':metadata}
(qa/'export-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:x for k,x in report.items() if k!='parts'},indent=2),flush=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT),'-vf','fps=3/160,scale=426:-1,tile=3x3','-frames:v','1',str(qa/'filme-contato.jpg')],check=True)
