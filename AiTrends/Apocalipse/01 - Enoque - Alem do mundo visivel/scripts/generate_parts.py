"""Generate/cache original narration. Credentials read from an external private file only."""
from pathlib import Path
import argparse,json,re,urllib.request,urllib.error,hashlib,base64,wave,time,datetime
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--credentials',type=Path,required=True);a.add_argument('--work',type=Path,required=True);a.add_argument('--from-part',type=int,default=1);a.add_argument('--to-part',type=int,default=25);o=a.parse_args();o.work.mkdir(parents=True,exist_ok=True)
keys=list(dict.fromkeys(re.findall(r'(?:AIza[\w-]{20,}|AQ\.[A-Za-z0-9_.-]{20,})',o.credentials.read_text())))
assert keys,'No recognized credentials';profile=json.loads((P/'audio/voice-profile.json').read_text());assert profile['sample_approval']=='approved_original_v1';parts=json.loads((P/'roteiro/partes.json').read_text());blocked_path=o.work/'credential-unavailable.json';today=datetime.date.today().isoformat();old=json.loads(blocked_path.read_text())if blocked_path.exists()else{};blocked=set(old.get('slots',[]))if old.get('date')==today else set()
for part in parts:
 n=part['part']
 if not o.from_part<=n<=o.to_part:continue
 out=o.work/f'{n:02}-raw.wav'; meta=out.with_suffix('.json'); record={'part':n,'text':part.get('tts_source_text',part['text']),'voice':profile['voice'],'model':profile['model'],'direction':profile['direction']}; sha=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();record['request_sha256']=sha
 if out.exists():
  assert json.loads(meta.read_text())['request_sha256']==sha,'Cache mismatch';print('CACHED',n,flush=True);continue
 if (o.work/f'pause-before-{n:02}').exists():raise SystemExit('Planned pause before shared-request generation; existing cache preserved')
 body={'contents':[{'parts':[{'text':profile['direction']+'\n\nNARRAÇÃO:\n'+part.get('tts_source_text',part['text'])}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':profile['voice']}}}}}
 success=False
 for idx in [1,0,2]:
  if idx>=len(keys)or idx in blocked:continue
  key=keys[idx];print('GENERATE',n,'credential',idx+1,flush=True)
  req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/'+profile['model']+':generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
  try:
   with urllib.request.urlopen(req,timeout=240)as f:response=json.load(f)
   aud=[p['inlineData']for c in response.get('candidates',[])for p in c.get('content',{}).get('parts',[])if'inlineData'in p];assert aud,'No audio returned';data=base64.b64decode(aud[0]['data'])
   if data[:4]==b'RIFF':out.write_bytes(data)
   else:
    with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(data)
   with wave.open(str(out))as f:record['raw_seconds']=f.getnframes()/f.getframerate();assert f.getnframes()>24000
   record['credential_slot']=idx+1;meta.write_text(json.dumps(record,ensure_ascii=False,indent=2));print('READY',n,record['raw_seconds'],flush=True);success=True;break
  except urllib.error.HTTPError as e:
   detail=e.read().decode()
   for secret in keys:detail=detail.replace(secret,'[REDACTED]')
   (o.work/f'{n:02}-error-{idx+1}-private.txt').write_text(detail);print('HTTP',n,'credential',idx+1,e.code,flush=True)
   if e.code in [401,403,429]:
    blocked.add(idx);blocked_path.write_text(json.dumps({'date':today,'slots':sorted(blocked)}));continue
   raise SystemExit('Generation paused; see private error')from None
 if not success:raise SystemExit('No available authorized credential; cache preserved')
 time.sleep(1)
