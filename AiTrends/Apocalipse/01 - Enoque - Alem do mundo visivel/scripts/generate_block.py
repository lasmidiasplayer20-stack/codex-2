"""Save requests by generating consecutive parts as one continuous take."""
from pathlib import Path
import argparse,json,re,hashlib,urllib.request,urllib.error,base64,wave
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--credentials',type=Path,required=True);a.add_argument('--work',type=Path,required=True);a.add_argument('--parts',type=int,nargs='+',required=True);a.add_argument('--text-file',type=Path);a.add_argument('--label');o=a.parse_args();profile=json.loads((P/'audio/voice-profile.json').read_text());assert profile['sample_approval']=='approved_original_v1';allparts=json.loads((P/'roteiro/partes.json').read_text());selected=[x for x in allparts if x['part']in o.parts];assert [x['part']for x in selected]==o.parts
text=o.text_file.read_text().strip()if o.text_file else'\n\n'.join(x.get('tts_source_text',x['text'])for x in selected);record={'parts':o.parts,'text':text,'voice':profile['voice'],'model':profile['model'],'direction':profile['direction']};record['request_sha256']=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();label=o.label or'block-'+'-'.join(f'{x:02}'for x in o.parts);out=o.work/(label+'.wav');meta=out.with_suffix('.json');o.work.mkdir(exist_ok=True,parents=True)
if out.exists():
 assert json.loads(meta.read_text())['request_sha256']==record['request_sha256'];print('BLOCK_CACHED',label);raise SystemExit(0)
keys=list(dict.fromkeys(re.findall(r'(?:AIza[\w-]{20,}|AQ\.[A-Za-z0-9_.-]{20,})',o.credentials.read_text())));blocked_path=o.work/'credential-unavailable.json';blocked=set(json.loads(blocked_path.read_text()).get('slots',[]))if blocked_path.exists()else set()
body={'contents':[{'parts':[{'text':profile['direction']+'\n\nNARRAÇÃO:\n'+text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':profile['voice']}}}}}
for idx in [1,0,2]:
 if idx>=len(keys)or idx in blocked:continue
 key=keys[idx];req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/'+profile['model']+':generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key});print('GENERATE_BLOCK',o.parts,'credential',idx+1,flush=True)
 try:
  with urllib.request.urlopen(req,timeout=300)as f:q=json.load(f)
  audio=[p['inlineData']for c in q.get('candidates',[])for p in c.get('content',{}).get('parts',[])if'inlineData'in p];assert audio;data=base64.b64decode(audio[0]['data'])
  if data[:4]==b'RIFF':out.write_bytes(data)
  else:
   with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(data)
  with wave.open(str(out))as f:record['raw_seconds']=f.getnframes()/f.getframerate()
  record['credential_slot']=idx+1;meta.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('BLOCK_READY',record['raw_seconds'],flush=True);break
 except urllib.error.HTTPError as e:
  detail=e.read().decode()
  for secret in keys:detail=detail.replace(secret,'[REDACTED]')
  (o.work/(label+f'-error-{idx+1}-private.txt')).write_text(detail);print('BLOCK_HTTP',idx+1,e.code,flush=True)
  if e.code in [401,403,429]:continue
  raise SystemExit('Block generation paused')from None
else:raise SystemExit('No available credential for block; cache preserved')
