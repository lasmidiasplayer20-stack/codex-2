"""Assemble existing native aiTrends render and treated audio; no API calls."""
from pathlib import Path
import argparse,subprocess,json,hashlib,re
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
def run(args):subprocess.run([str(x)for x in args],check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def check(p,seconds):
 data=probe(p);v=next(s for s in data['streams']if s['codec_type']=='video');assert (v['width'],v['height'])==(1920,1080);assert v['avg_frame_rate']=='24/1';assert int(v['nb_frames'])==round(seconds*24);assert abs(float(data['format']['duration'])-seconds)<.08
 result=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-progress','pipe:1','-nostats','-f','null','-'],check=True,text=True,capture_output=True)
 frames=[int(x)for x in re.findall(r'^frame=(\d+)$',result.stdout,re.M)];assert frames and frames[-1]==round(seconds*24)
 print('DECODE_VALIDATED',p.name,frames[-1],flush=True);return data
def main():
 p=argparse.ArgumentParser();p.add_argument('--silent',type=Path,required=True);p.add_argument('--mix',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 cfg=json.loads((ROOT/'config.json').read_text());duration=cfg['duration'];a.work.mkdir(parents=True,exist_ok=True);out=ROOT/'exports';out.mkdir(exist_ok=True)
 audit=json.loads((ROOT/'audio/content-audit.json').read_text())
 checked=[x for x in audit if x.get('word_similarity')is not None]
 if len(audit)!=8 or len(checked)<4 or any(x['word_similarity']<.88 or x['unexpected_instruction_terms']for x in checked):raise SystemExit('Available speech audits must pass and coverage must be documented before assembly.')
 # A failed renderer can leave an output file; require the explicit success marker.
 log=(a.work/'full-render.log').read_text()
 if 'Done: '+str(a.silent)not in log or 'SHOT ERROR'in log or 'RENDER FAILED'in log or '[pageerror]'in log or 'IMPORT ERROR'in log or 'shots have no scene file'in log:raise SystemExit('Renderer success/clean log required.')
 seating=ROOT/'qa/seating-revision.json'
 if seating.exists():
  prior=json.loads(seating.read_text())
  if not(prior['full_decode_passed'] and prior['frames']==round(duration*24) and prior['native_dimensions']==[1920,1080] and prior['after_sha256']==hashlib.sha256(a.silent.read_bytes()).hexdigest()):check(a.silent,duration)
 else:check(a.silent,duration)
 dest=out/'02 - Quantas mentiras.mp4';preview=out/'02 - Quantas mentiras - Preview 1min.mp4'
 run(['ffmpeg','-v','error','-y','-i',a.silent,'-i',a.mix,'-i',ROOT/'timeline/legendas-provisorias.srt','-map','0:v:0','-map','1:a:0','-map','2:s:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-c:s','mov_text','-metadata:s:s:0','language=por','-disposition:s:0','0','-metadata','title=E se você pudesse ver as mentiras?','-metadata','artist=Então','-t',str(duration),'-movflags','+faststart',dest])
 if dest.stat().st_size>98_000_000:raise SystemExit('Delivery exceeds budget; review two-pass compression before publishing.')
 data=check(dest,duration)
 run(['ffmpeg','-v','error','-y','-i',dest,'-t','60','-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',preview]);prev=check(preview,60)
 qa=ROOT/'qa';qa.mkdir(exist_ok=True)
 times=[2,20,34,46,80,108,170,250,293,302,319,365,391,410,466,491]
 sheet=Image.new('RGB',(4*492+12,4*302+12),'#101625');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  thumb=a.work/f'final-qa-{t}.jpg'
  run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',dest,'-vf','scale=480:-1','-frames:v','1',thumb])
  x=12+(i%4)*492;y=12+(i//4)*302;sheet.paste(Image.open(thumb),(x,y));draw.text((x+6,y+276),f'{t//60:02}:{t%60:02}',fill='#e8dcb9')
 sheet.save(qa/'filme-completo.jpg',quality=92,optimize=True)
 for label,t in [('cta-45s',46),('cta-intermediario',250),('cta-final',491),('apoio-banco',466),('apoio-hospital',302)]:
  run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',dest,'-frames:v','1',qa/(label+'.jpg')])
 if (ROOT/'audio/narracao.wav').exists():run(['ffmpeg','-v','error','-y','-i',ROOT/'audio/narracao.wav','-c:a','libmp3lame','-b:a','192k',ROOT/'audio/narracao.mp3'])
 else:assert (ROOT/'audio/narracao.mp3').exists()
 if a.mix.resolve()!=(ROOT/'audio/mix.mp3').resolve():run(['ffmpeg','-v','error','-y','-i',a.mix,'-c:a','libmp3lame','-b:a','192k',ROOT/'audio/mix.mp3'])
 sources=[ROOT/'config.json',*sorted((ROOT/'scenes').glob('*.js')),ROOT/'story/beats.json',ROOT/'story/shots.json'];sourcehash=hashlib.sha256(b''.join(p.read_bytes()for p in sources)).hexdigest()
 report={'duration':duration,'width':1920,'height':1080,'fps':24,'frames':round(duration*24),'audio':'AAC 192 kb/s stereo 48 kHz, Puck pt-BR + procedural music/SFX','bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':sourcehash,'native_render':True,'upscaled':False,'preview':{'seconds':60,'frames':1440,'bytes':preview.stat().st_size},'full_decode_passed':True,'renderer_errors':[],'cta_seconds':[[43,51],[246,254],[485,499.4]],'subtitle_timing':'Phrase-reading estimates, optional track, not ASR word alignment','speech_audit':{'verified_parts':[x['part']for x in checked],'asr_unavailable_parts':[x['part']for x in audit if x.get('word_similarity')is None],'method':'Independent automated Gemini transcription on available parts; no claim of full ASR or human listening. See audio/content-audit.json.'}}
 (qa/'export-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(qa/'ffprobe-final.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(qa/'ffprobe-preview.json').write_text(json.dumps(prev,ensure_ascii=False,indent=2))
 print('FINAL_EXPORT_COMPLETE',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
