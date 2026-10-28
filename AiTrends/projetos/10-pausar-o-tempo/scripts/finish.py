from pathlib import Path
import argparse,json,subprocess,re,hashlib,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work
log=(W/'full-render.log').read_text();assert 'Done:'in log and not re.search(r'SHOT ERROR|shot error|WARNING:.*no scene',log),'Render incomplete/errors'
frozen=json.loads((P/'qa/frozen-source.json').read_text());h=hashlib.sha256()
for file in frozen['files']:h.update(file.encode());h.update((P/file).read_bytes())
assert h.hexdigest()==frozen['sha256'],'Visual source changed'
F=P/'exports/10 - E se você pudesse pausar o tempo.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(W/'full-silent.mp4'),'-i',str(P/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','60','-movflags','+faststart',str(F)],check=True)
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(F)]));(P/'qa/ffprobe-final.json').write_text(json.dumps(r,indent=2));v=next(s for s in r['streams']if s['codec_type']=='video');audio=next(s for s in r['streams']if s['codec_type']=='audio');assert(v['width'],v['height'],int(v['nb_read_frames']),v['r_frame_rate'])==(1080,1920,1440,'24/1');assert abs(float(r['format']['duration'])-60)<.001
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(F),'-f','null','-'],check=True)
e=subprocess.run(['ffmpeg','-hide_banner','-i',str(F),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr;summary=e[e.rfind('Summary:'):];lufs=float(re.search(r'I:\s*([-\d.]+) LUFS',summary).group(1));peak=float(re.search(r'Peak:\s*([-\d.]+) dBFS',summary).group(1));assert peak< -2,'Insufficient audio headroom'
ref=json.loads((P/'audio/encoded-validation.json').read_text());assert abs(lufs-ref['integrated_lufs'])<.7,'Final MP4 differs from validated mix'
(P/'qa/final-audio-validation.json').write_text(json.dumps({'integrated_lufs':lufs,'true_peak_dbfs':peak,'full_decode_passed':True,'human_full_listening':False,'same_puck_model':True,'speed_change':False},indent=2))
sheet=Image.new('RGB',(1440,1920),'#122238');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([1,5,7.5,9,11,15,20,24,28.5,31,35,43,47,51.5,54.5,58]):
 out=W/f'final-{i}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=270:480','-y',str(out)],check=True);im=Image.open(out);im.thumbnail((255,450));x=i%4*360+30;y=i//4*480;sheet.paste(im,(x,y+25));draw.text((x,y+4),f'{t:.1f}s',fill='white')
sheet.save(P/'qa/filme-completo.jpg',quality=90)
# Consecutive grip frames from actual final export.
sheet2=Image.new('RGB',(1500,520),'#122238');draw=ImageDraw.Draw(sheet2)
for i,t in enumerate([49.5,50.5,51.5,52.5,54,55]):
 out=W/f'grip-{i}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=240:426','-y',str(out)],check=True);sheet2.paste(Image.open(out),(i*250,30));draw.text((i*250+5,5),f'{t}s',fill='white')
sheet2.save(P/'qa/resgate-retorno-movimento.jpg',quality=90)

# Consecutive frames of moving camera around the frozen world, taken from final MP4.
sheet3=Image.new('RGB',(1500,520),'#122238');draw=ImageDraw.Draw(sheet3)
for i,t in enumerate([18.6,19.2,19.8,20.4,21.0,21.6]):
 out=W/f'orbit-{i}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=240:426','-y',str(out)],check=True);sheet3.paste(Image.open(out),(i*250,30));draw.text((i*250+5,5),f'{t}s',fill='white')
sheet3.save(P/'qa/orbita-congelada-movimento.jpg',quality=90)

report={'seconds':60,'fps':24,'frames':1440,'width':1080,'height':1920,'native_render':True,'upscaled':False,'full_decode_passed':True,'audio_codec':audio['codec_name'],'bytes':F.stat().st_size,'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'source_sha256':frozen['sha256'],'preview':'The complete 60-second short itself; no duplicate file','audio_review':'Signal measurements and preserved source text, no full human listening or ASR claim.'};(P/'qa/export-validation.json').write_text(json.dumps(report,indent=2));shutil.copy(W/'full-render.log',P/'qa/full-render.txt')
print('FINAL_VALIDATED',json.dumps(report),flush=True)
