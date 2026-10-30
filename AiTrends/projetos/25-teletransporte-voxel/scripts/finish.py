from pathlib import Path
import argparse,json,subprocess,re,hashlib,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work;C=json.loads((P/'config.json').read_text());F=P/'exports'/C['export_name'];D=25;FPS=24
log=(W/'full-render.log').read_text();assert 'Done:'in log and not re.search(r'SHOT ERROR|shot error|WARNING:.*no scene',log)
frozen=json.loads((P/'qa/frozen-source.json').read_text());h=hashlib.sha256()
for file in frozen['files']:h.update(file.encode());h.update((P/file).read_bytes())
assert h.hexdigest()==frozen['sha256'],'Source changed'
key="[0:v]eq=saturation=1.12:contrast=1.02[base];[2:v]format=rgba,colorkey=0x00ff00:0.35:0.10,despill=type=green,scale=900:-2,setpts=PTS-STARTPTS+18/TB[a];[base][a]overlay=90:1440:eof_action=pass:enable='between(t,18,25)'[out]"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(W/'full-silent.mp4'),'-i',str(P/'audio/mix.wav'),'-i',str(P/'assets/cta-b.mp4'),'-filter_complex_threads','2','-filter_complex',key,'-map','[out]','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','24','-frames:v','600','-c:a','aac','-b:a','192k','-ar','48000','-t','25','-movflags','+faststart',str(F)],check=True)
def validate(file,seconds,frames):
 r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(file)]));v=next(s for s in r['streams']if s['codec_type']=='video');assert(v['width'],v['height'],int(v['nb_read_frames']),v['r_frame_rate'])==(1080,1920,frames,'24/1');assert abs(float(r['format']['duration'])-seconds)<.001;assert any(s['codec_type']=='audio'for s in r['streams']);subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(file),'-f','null','-'],check=True);return r
r=validate(F,25,600);(P/'qa/ffprobe-final.json').write_text(json.dumps(r,indent=2))
e=subprocess.run(['ffmpeg','-hide_banner','-i',str(F),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr;e=e[e.rfind('Summary:'):];lufs=float(re.search(r'I:\s*([-\d.]+) LUFS',e).group(1));peak=float(re.search(r'Peak:\s*([-\d.]+) dBFS',e).group(1));assert peak< -2 and -24<lufs< -16
(P/'qa/final-audio-validation.json').write_text(json.dumps({'integrated_lufs':lufs,'true_peak_dbfs':peak,'full_decode_passed':True,'human_full_listening':False,'speed_change':False,'same_puck_model':True},indent=2))
def sheet(name,times,columns=4):
 cw,ch=300,570;im=Image.new('RGB',(columns*cw,((len(times)+columns-1)//columns)*ch),'#132538');d=ImageDraw.Draw(im)
 for i,t in enumerate(times):
  f=W/f'{name}-{i}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(F),'-frames:v','1','-vf','scale=270:480','-y',str(f)],check=True);x=i%columns*cw+15;y=i//columns*ch;im.paste(Image.open(f),(x,y+30));d.text((x,y+5),f'{t:.3f}s',fill='white')
 im.save(P/f'qa/{name}.jpg',quality=90)
shots=json.loads((P/'story/shots.json').read_text())['shots'];sheet('filme-completo',[(s['start']+s['end'])/2 for s in shots]);sheet('cta-final',[19.5,22,24],2)
critical=C.get('qa_actions',[]);times=[]
for s in shots:
 if s['params']['cam']in critical:times.extend([s['start']+(s['end']-s['start'])*q for q in [.15,.45,.8]])
if times:sheet('acoes-movimento',times)
v=P/'exports/preview-10s.mp4';subprocess.run(['ffmpeg','-v','error','-y','-i',str(F),'-t','10','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',str(v)],check=True);validate(v,10,240)
(P/'qa/preview-validation.json').write_text(json.dumps({'seconds':10,'frames':240,'width':1080,'height':1920,'full_decode_passed':True,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()},indent=2))
report={'seconds':25,'fps':24,'frames':600,'width':1080,'height':1920,'native_render':True,'post_color':{'saturation':1.12,'contrast':1.02},'upscaled':False,'full_decode_passed':True,'bytes':F.stat().st_size,'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'source_sha256':frozen['sha256'],'preview':'exports/preview-10s.mp4','cta':{'count':1,'variant':6,'intervals':[[18,25]],'width':900,'position':[90,1440],'source_audio_mixed':False},'audio_review':'Signal measures only; no full human listening/independent ASR claim.'};(P/'qa/export-validation.json').write_text(json.dumps(report,indent=2));shutil.copy(W/'full-render.log',P/'qa/full-render.txt');print('FINAL_VALIDATED',json.dumps(report),flush=True)
