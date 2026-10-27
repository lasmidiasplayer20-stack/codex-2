"""Wait for the authorized same-model quota reset, then complete with bounded calls.

No billing changes, model fallback or repeated rate-limit calls. Requires a live workspace.
"""
from pathlib import Path
import argparse,subprocess,json,time,datetime,hashlib,os,sys
P=Path(__file__).resolve().parents[1];REPO=P.parents[2]
def digest():
 files=[P/'config.json',P/'runtime-style.json',*sorted((P/'scenes').glob('*.js')),P/'story/beats.json',P/'story/shots.json']
 return hashlib.sha256(b''.join(p.read_bytes()for p in files)).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);a.add_argument('--not-before',required=True);a.add_argument('--expected-source',required=True);a.add_argument('--publish',action='store_true');args=a.parse_args();args.work.mkdir(parents=True,exist_ok=True)
 deadline=datetime.datetime.fromisoformat(args.not_before.replace('Z','+00:00')).timestamp();status=args.work/'queue-state.json'
 def state(phase,**extra):status.write_text(json.dumps({'phase':phase,'not_before':args.not_before,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra},indent=2)+'\n');print(phase,flush=True)
 def run(cmd,logname):
  with (args.work/logname).open('w')as f:subprocess.run([str(x)for x in cmd],cwd=REPO,stdout=f,stderr=subprocess.STDOUT,check=True)
 try:
  state('WAITING_FOR_AUTHORIZED_DAILY_RESET')
  while time.time()<deadline:
   if digest()!=args.expected_source:raise RuntimeError('Project source changed while waiting; abort to avoid overwriting edits.')
   time.sleep(min(55,max(0,deadline-time.time())))
  if digest()!=args.expected_source:raise RuntimeError('Frozen source changed; stopped.')
  py=REPO/'AiTrends/.venv/bin/python';state('GENERATING_REMAINING_VOICE')
  run([py,P/'scripts/generate_voice.py','--work',args.work/'voice'],'generate-after-reset.log')
  state('TREATING_NATURAL_VOICE');run([py,P/'scripts/treat_natural.py','--work',args.work/'voice'],'treat-after-reset.log')
  state('BUILDING_PYTHON_SFX_AND_MIX');run([py,P/'scripts/sound.py','--voice','narracao.wav'],'sound-final.log')
  run([py,P/'scripts/youtube.py'],'youtube-final.log');frozen=digest();state('RENDERING_NATIVE_1080P',source_sha256=frozen)
  silent=args.work/'full-silent-1080.mp4';run(['node',REPO/'AiTrends/skill/scripts/render.mjs','--project',P,'--scale','1','--workers','2','--format','jpeg','--preset','fast','--crf','20','--out',silent],'full-render.log')
  if digest()!=frozen:raise RuntimeError('Source changed during render; export stopped.')
  state('EXPORTING_AND_VALIDATING');run([py,REPO/'AiTrends/skill/scripts/export.py','--project',P,'--silent',silent,'--work',args.work],'export-final.log')
  report=json.loads((P/'qa/export-validation.json').read_text());assert report['source_sha256']==frozen
  run([py,P/'scripts/finish_delivery.py'],'finish-delivery.log')
  for name in ['full-render.log','export-final.log']:
   text=(args.work/name).read_text();(P/'qa'/name.replace('.log','.txt')).write_text('\n'.join(x.rstrip()for x in text.splitlines())+'\n')
  if args.publish:
   branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
   if branch!='main':raise RuntimeError('Unexpected branch; automatic publish stopped.')
   paths=['AiTrends/projetos/06-recomecar-humanidade','AiTrends/youtube/06 - Duas Pessoas Podem Recomeçar a Humanidade']
   subprocess.run(['git','add','--',*paths],cwd=REPO,check=True);subprocess.run(['git','diff','--cached','--check','--',*paths],cwd=REPO,check=True)
   subprocess.run(['git','commit','--only','-m','Complete episode06 after authorized free-tier voice reset','--',*paths],cwd=REPO,check=True)
   subprocess.run(['git','push','origin','main'],cwd=REPO,check=True)
   local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0];assert local==remote
   state('COMPLETE_PUBLISHED',commit=local)
  else:state('COMPLETE_LOCAL_NOT_PUBLISHED')
 except Exception as e:
  state('STOPPED_REQUIRES_REVIEW',error=str(e));raise
if __name__=='__main__':main()
