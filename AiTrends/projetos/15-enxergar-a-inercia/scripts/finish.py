from pathlib import Path
import argparse,json,subprocess,re,hashlib,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work
log=(W/'full-render.log').read_text();assert 'Done:'in log and not re.search(r'SHOT ERROR|shot error|WARNING:.*no scene',log),'Render incomplete/errors'
frozen=json.loads((P/'qa/frozen-source.json').read_text());h=hashlib.sha256()
for file in frozen['files']:h.update(file.encode());h.update((P/file).read_bytes())
assert h.hexdigest()==frozen['sha256'],'Visual source changed'
F=P/'exports/15 - E se você pudesse enxergar a inércia.mp4'
key=r'[2:v]format=rgba,colorkey=0x00ff00:0.35:0.10,despill=type=green,scale=900:-2,setpts=PTS-STARTPTS+15/TB[a];[3:v]format=rgba,colorkey=0x00ff00:0.35:0.10,despill=type=green,scale=900:-2,setpts=PTS-STARTPTS+81/TB[b];[0:v][a]overlay=90:1440:eof_action=pass:enable=between(t\,15\,22)[v1];[v1][b]overlay=90:1440:eof_action=pass:enable=between(t\,81\,88)[out]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(W/'full-silent.mp4'),'-i',str(P/'audio/mix.wav'),'-i',str(P/'assets/cta-a.mp4'),'-i',str(P/'assets/cta-b.mp4'),'-filter_complex_threads','2','-filter_complex',key,'-map','[out]','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','24','-frames:v','2160','-c:a','aac','-b:a','192k','-ar','48000','-t','90','-movflags','+faststart',str(F)],check=True)
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(F)]));(P/'qa/ffprobe-final.json').write_text(json.dumps(r,indent=2));v=next(s for s in r['streams']if s['codec_type']=='video');audio=next(s for s in r['streams']if s['codec_type']=='audio');assert(v['width'],v['height'],int(v['nb_read_frames']),v['r_frame_rate'])==(1080,1920,2160,'24/1');assert abs(float(r['format']['duration'])-90)<.001
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(F),'-f','null','-'],check=True)
e=subprocess.run(['ffmpeg','-hide_banner','-i',str(F),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr;summary=e[e.rfind('Summary:'):];lufs=float(re.search(r'I:\s*([-\d.]+) LUFS',summary).group(1));peak=float(re.search(r'Peak:\s*([-\d.]+) dBFS',summary).group(1));assert peak< -2,'Insufficient audio headroom'
ref=json.loads((P/'audio/encoded-validation.json').read_text());assert abs(lufs-ref['integrated_lufs'])<.7,'Final MP4 differs from validated mix'
(P/'qa/final-audio-validation.json').write_text(json.dumps({'integrated_lufs':lufs,'true_peak_dbfs':peak,'full_decode_passed':True,'human_full_listening':False,'same_puck_model':True,'speed_change':False},indent=2))
def sheet(name,times,columns=4):
 cellw,cellh=300,570;im=Image.new('RGB',(columns*cellw,((len(times)+columns-1)//columns)*cellh),'#122238');dd=ImageDraw.Draw(im)
 for i,t in enumerate(times):
  out=W/f'{name}-{i}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=270:480','-y',str(out)],check=True);x=i%columns*cellw+15;y=i//columns*cellh;im.paste(Image.open(out),(x,y+30));dd.text((x,y+5),f'{t:.3f}s',fill='white')
 im.save(P/f'qa/{name}.jpg',quality=90)
sheet('filme-completo',[1,4.5,8,10.5,13,16.5,19,23,28,31,34,40,46,50,56,60,64,67,71,74,76,77.8,79,82,87])
sheet('cta-final',[16.5,20,82.5,86],2)
sheet('freada-movimento',[11.5,12.5,13.5,14.5,15.5,16.4],3)
sheet('catraca-travamento',[61.8,62.2,62.5,63,64,65],3)
sheet('mochila-movimento',[73.4,74.0,74.6,75.2,77.2,78],3)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(F),'-t','60','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/'exports/preview-60s.mp4')],check=True)
report={'seconds':90,'fps':24,'frames':2160,'width':1080,'height':1920,'native_render':True,'upscaled':False,'full_decode_passed':True,'audio_codec':audio['codec_name'],'bytes':F.stat().st_size,'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'source_sha256':frozen['sha256'],'preview':'exports/preview-60s.mp4','audio_review':'Signal measurements and preserved source text, no full human listening or ASR claim.'};(P/'qa/export-validation.json').write_text(json.dumps(report,indent=2));shutil.copy(W/'full-render.log',P/'qa/full-render.txt')
report['cta']={'assets':['assets/cta-a.mp4','assets/cta-b.mp4'],'different_variants':True,'intervals':[[15,22],[81,88]],'overlay_width':900,'position':[90,1440],'chroma_key':True,'despill':True,'original_asset_audio_mixed':False};(P/'qa/export-validation.json').write_text(json.dumps(report,indent=2))
print('FINAL_VALIDATED',json.dumps(report),flush=True)
