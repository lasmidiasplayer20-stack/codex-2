"""Offline native render/export after voice and visual pilots. No TTS/API calls."""
from pathlib import Path
import argparse,subprocess,json,datetime,hashlib
P=Path(__file__).resolve().parents[1];REPO=P.parents[2]
def digest():
 files=[P/'config.json',P/'runtime-style.json',*sorted((P/'scenes').glob('*.js')),P/'story/beats.json',P/'story/shots.json'];return hashlib.sha256(b''.join(f.read_bytes()for f in files)).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);a.add_argument('--expected-source',required=True);a.add_argument('--publish',action='store_true');args=a.parse_args();args.work.mkdir(parents=True,exist_ok=True);py=REPO/'AiTrends/.venv/bin/python'
 def state(phase,**extra):
  (args.work/'queue-state.json').write_text(json.dumps({'phase':phase,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra},indent=2)+'\n');print(phase,flush=True)
 def run(cmd,name):
  with (args.work/name).open('w')as log:subprocess.run([str(v)for v in cmd],cwd=REPO,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  assert digest()==args.expected_source,'Source changed since pilot review.';cfg=json.loads((P/'config.json').read_text());q=json.loads((P/'audio/quality.json').read_text());assert cfg['duration']<=600 and q['successful_audio_blocks']==4 and q['models']==['gemini-2.5-flash-preview-tts']and q['clipped_samples']==0;assert(P/'audio/mix.mp3').is_file()
  state('AUDITING_SCENES');run([py,P/'scripts/audit_scene.py','--work',args.work],'scene-audit-final.log');assert digest()==args.expected_source
  state('RENDERING_NATIVE_1080P',source_sha256=args.expected_source);silent=args.work/'full-silent-1080.mp4';run(['node',REPO/'AiTrends/skill/scripts/render.mjs','--project',P,'--scale','1','--workers','2','--format','jpeg','--preset','fast','--crf','20','--out',silent],'full-render.log');assert digest()==args.expected_source,'Source changed during render; export stopped.'
  state('EXPORTING_AND_VALIDATING');run([py,REPO/'AiTrends/skill/scripts/export.py','--project',P,'--silent',silent,'--work',args.work],'export-final.log');report=json.loads((P/'qa/export-validation.json').read_text());assert report['source_sha256']==args.expected_source and report['seconds']<=600
  run([py,P/'scripts/finish_delivery.py'],'finish-delivery.log')
  for name in ['full-render.log','export-final.log']:(P/'qa'/name.replace('.log','.txt')).write_text('\n'.join(x.rstrip()for x in (args.work/name).read_text().splitlines())+'\n')
  if args.publish:
   assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()=='main';paths=['AiTrends/projetos/08-modo-criativo','AiTrends/youtube/08 - E se você tivesse Modo Criativo na vida real'];subprocess.run(['git','add','--',*paths],cwd=REPO,check=True);subprocess.run(['git','diff','--cached','--check','--',*paths],cwd=REPO,check=True);subprocess.run(['git','commit','--only','-m','Complete creative-mode episode in native1080p with same Puck','--',*paths],cwd=REPO,check=True);subprocess.run(['git','push','origin','main'],cwd=REPO,check=True);local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0];assert local==remote;state('COMPLETE_PUBLISHED',commit=local)
  else:state('COMPLETE_LOCAL')
 except Exception as e:state('STOPPED_REQUIRES_REVIEW',error=str(e));raise
if __name__=='__main__':main()
