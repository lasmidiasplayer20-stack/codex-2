"""Mux native render, make preview and validate full decode. Offline."""
from pathlib import Path
import argparse,subprocess,json,hashlib,re
from PIL import Image,ImageDraw
def run(args):subprocess.run([str(x)for x in args],check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def check(p,seconds,fps):
 data=probe(p);v=next(s for s in data['streams']if s['codec_type']=='video');assert (v['width'],v['height'])==(1920,1080);assert v['avg_frame_rate']==f'{fps}/1';assert int(v['nb_frames'])==round(seconds*fps);assert abs(float(data['format']['duration'])-seconds)<.08
 result=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-progress','pipe:1','-nostats','-f','null','-'],check=True,text=True,capture_output=True);frames=[int(x)for x in re.findall(r'^frame=(\d+)$',result.stdout,re.M)];assert frames[-1]==round(seconds*fps);print('DECODE_VALIDATED',p.name,frames[-1],flush=True);return data
def main():
 p=argparse.ArgumentParser();p.add_argument('--patches',type=Path,help='JSON list of native frame-range replacements');p.add_argument('--project',type=Path,required=True);p.add_argument('--silent',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();root=a.project.resolve();cfg=json.loads((root/'config.json').read_text());seconds=cfg['duration'];fps=cfg['fps'];a.work.mkdir(parents=True,exist_ok=True);out=root/'exports';out.mkdir(exist_ok=True);qa=root/'qa';qa.mkdir(exist_ok=True)
 log=(a.work/'full-render.log').read_text();assert 'Done: '+str(a.silent)in log and not any(x in log for x in ['SHOT ERROR','RENDER FAILED','[pageerror]','IMPORT ERROR','shots have no scene file']),'Require a successful render log.'
 dest=out/(cfg['title']+'.mp4');preview=out/(cfg['title']+' - Preview 1min.mp4');common=['ffmpeg','-v','error','-y','-i',a.silent,'-i',root/'audio/mix.mp3','-map','0:v:0','-map','1:a:0'];audio=['-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',str(seconds),'-movflags','+faststart']
 patches=json.loads(a.patches.read_text())if a.patches else []
 if patches:
  inputs=['ffmpeg','-v','error','-y','-i',a.silent,'-i',root/'audio/mix.mp3'];chains=[];labels=[];cursor=0
  for i,patch in enumerate(patches):
   start,end=patch['start_frame'],patch['end_frame'];assert cursor<=start<end<=round(seconds*fps);pv=next(x for x in probe(patch['path'])['streams']if x['codec_type']=='video');assert (pv['width'],pv['height'])==(1920,1080)and int(pv['nb_frames'])==end-start
   patchlog=(a.work/('patch-'+patch['action']+'.log')).read_text();assert 'Done: '+patch['path']in patchlog and not any(x in patchlog for x in ['SHOT ERROR','RENDER FAILED','[pageerror]','IMPORT ERROR'])
   if cursor<start:
    label=f'b{i}';chains.append(f'[0:v]trim=start_frame={cursor}:end_frame={start},setpts=PTS-STARTPTS[{label}]');labels.append(f'[{label}]')
   inputs+=['-i',patch['path']];label=f'p{i}';chains.append(f'[{i+2}:v]trim=end_frame={end-start},setpts=PTS-STARTPTS[{label}]');labels.append(f'[{label}]');cursor=end
  if cursor<round(seconds*fps):
   chains.append(f'[0:v]trim=start_frame={cursor}:end_frame={round(seconds*fps)},setpts=PTS-STARTPTS[tail]');labels.append('[tail]')
  chains.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=0[v]');common=inputs+['-filter_complex_threads','1','-filter_complex',';'.join(chains),'-map','[v]','-map','1:a:0']
 else:run(common+['-c:v','copy']+audio+[dest])
 recompressed=False
 if patches or dest.stat().st_size>98_000_000:
  recompressed=True;kbps=int((94_000_000*8/seconds-192000)/1000);prefix=a.work/'size-pass'
  for turn in [1,2]:
   cmd=common+['-c:v','libx264','-preset','fast','-threads','2','-pix_fmt','yuv420p','-r',str(fps),'-frames:v',str(round(seconds*fps)),'-b:v',f'{kbps}k','-pass',str(turn),'-passlogfile',prefix]
   run(cmd+(['-an','-t',str(seconds),'-f','null','/dev/null']if turn==1 else audio+[dest]))
 assert dest.stat().st_size<98_000_000
 data=check(dest,seconds,fps)
 run(['ffmpeg','-v','error','-y','-i',dest,'-t','60','-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',preview]);prev=check(preview,60,fps)
 times=cfg.get('qaTimes',[2,22,46,69,100,135,170,205,250,290,325,365,400,440,475,500]);sheet=Image.new('RGB',(1980,1220),'#121c29');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  path=a.work/f'qa-{t}.jpg';run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',dest,'-vf','scale=480:-1','-frames:v','1',path]);x=12+i%4*492;y=12+i//4*302;sheet.paste(Image.open(path),(x,y));draw.text((x+4,y+275),f'{t//60:02}:{t%60:02}',fill='white')
 sheet.save(qa/'filme-completo.jpg',quality=93)
 for label,t in cfg.get('qaStills',[('cta-45s',46),('cta-intermediario',250),('cta-final',500),('contato',2),('apoio-banco',330)]):run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',dest,'-frames:v','1',qa/(label+'.jpg')])
 run(['ffmpeg','-v','error','-y','-i',root/'audio/narracao.wav','-c:a','libmp3lame','-b:a','192k',root/'audio/narracao.mp3'])
 sources=[root/'config.json',root/'runtime-style.json',*sorted((root/'scenes').glob('*.js')),root/'story/beats.json',root/'story/shots.json'];report={'seconds':seconds,'width':1920,'height':1080,'fps':fps,'frames':round(seconds*fps),'native_render':True,'upscaled':False,'size_limited_two_pass':recompressed,'video_bitrate_target_kbps':kbps if recompressed else None,'full_decode_passed':True,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(b''.join(x.read_bytes()for x in sources)).hexdigest(),'preview':{'seconds':60,'frames':round(60*fps),'bytes':preview.stat().st_size},'audio':'Puck pt-BR + original procedural music and SFX; AAC stereo 192 kb/s 48kHz','speech_review':'Exact TTS input/cache checks and signal metrics. No claim of full independent ASR or human listening.','cta_seconds':cfg.get('ctaSeconds',[[43,51],[247,255],[495,509.3]]),'renderer_errors':[],'native_replacements':patches}
 for name,obj in [('export-validation.json',report),('ffprobe-final.json',data),('ffprobe-preview.json',prev)]: (qa/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print('FINAL_EXPORT_COMPLETE',json.dumps(report),flush=True)
if __name__=='__main__':main()
