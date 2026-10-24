"""Assemble existing native aiTrends render and treated audio; no API calls."""
from pathlib import Path
import argparse,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
def run(args):subprocess.run([str(x)for x in args],check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def check(p,seconds):
 data=probe(p);v=next(s for s in data['streams']if s['codec_type']=='video');assert (v['width'],v['height'])==(1920,1080);assert v['avg_frame_rate']=='24/1';assert int(v['nb_read_frames'])==round(seconds*24);assert abs(float(data['format']['duration'])-seconds)<.08
 run(['ffmpeg','-v','error','-xerror','-i',p,'-f','null','-']);return data
def main():
 p=argparse.ArgumentParser();p.add_argument('--silent',type=Path,required=True);p.add_argument('--mix',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 cfg=json.loads((ROOT/'config.json').read_text());duration=cfg['duration'];a.work.mkdir(parents=True,exist_ok=True);out=ROOT/'exports';out.mkdir(exist_ok=True)
 audit=json.loads((ROOT/'audio/content-audit.json').read_text())
 if len(audit)!=8 or any(x['word_similarity']<.88 or x['unexpected_instruction_terms']for x in audit):raise SystemExit('Speech audit must pass before final assembly.')
 # A failed renderer can leave an output file; require the explicit success marker.
 log=(a.work/'full-render.log').read_text()
 if 'Done: '+str(a.silent)not in log or 'SHOT ERROR'in log or 'RENDER FAILED'in log:raise SystemExit('Renderer success/clean log required.')
 check(a.silent,duration)
 dest=out/'02 - Quantas mentiras.mp4';preview=out/'02 - Quantas mentiras - Preview 1min.mp4'
 run(['ffmpeg','-v','error','-y','-i',a.silent,'-i',a.mix,'-i',ROOT/'timeline/legendas-provisorias.srt','-map','0:v:0','-map','1:a:0','-map','2:s:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-c:s','mov_text','-metadata:s:s:0','language=por','-disposition:s:0','0','-metadata','title=E se você pudesse ver as mentiras?','-metadata','artist=Então','-t',str(duration),'-movflags','+faststart',dest])
 if dest.stat().st_size>98_000_000:raise SystemExit('Delivery exceeds budget; review two-pass compression before publishing.')
 data=check(dest,duration)
 run(['ffmpeg','-v','error','-y','-i',dest,'-t','60','-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',preview]);prev=check(preview,60)
 qa=ROOT/'qa';qa.mkdir(exist_ok=True)
 times=[2,20,34,46,80,108,170,250,293,315,365,410,450,491]
 expression='+'.join(f'eq(n,{int(t*24)})'for t in times)
 run(['ffmpeg','-v','error','-y','-i',dest,'-vf',f"select='{expression}',scale=480:-1,tile=4x4",'-frames:v','1',qa/'filme-completo.jpg'])
 for label,t in [('cta-45s',46),('cta-intermediario',250),('cta-final',491)]:
  run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',dest,'-frames:v','1',qa/(label+'.jpg')])
 run(['ffmpeg','-v','error','-y','-i',ROOT/'audio/narracao.wav','-c:a','libmp3lame','-b:a','192k',ROOT/'audio/narracao.mp3'])
 run(['ffmpeg','-v','error','-y','-i',a.mix,'-c:a','libmp3lame','-b:a','192k',ROOT/'audio/mix.mp3'])
 sources=[ROOT/'config.json',*sorted((ROOT/'scenes').glob('*.js')),ROOT/'story/beats.json',ROOT/'story/shots.json'];sourcehash=hashlib.sha256(b''.join(p.read_bytes()for p in sources)).hexdigest()
 report={'duration':duration,'width':1920,'height':1080,'fps':24,'frames':round(duration*24),'audio':'AAC 192 kb/s stereo 48 kHz, Puck pt-BR + procedural music/SFX','bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':sourcehash,'native_render':True,'upscaled':False,'preview':{'seconds':60,'frames':1440,'bytes':preview.stat().st_size},'full_decode_passed':True,'renderer_errors':[],'cta_seconds':[[43,51],[246,254],[485,499.4]],'subtitle_timing':'Phrase-reading estimates, optional track, not ASR word alignment','speech_audit':'Independent automated Gemini transcription comparison; not human listening'}
 (qa/'export-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(qa/'ffprobe-final.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(qa/'ffprobe-preview.json').write_text(json.dumps(prev,ensure_ascii=False,indent=2))
 print('FINAL_EXPORT_COMPLETE',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
