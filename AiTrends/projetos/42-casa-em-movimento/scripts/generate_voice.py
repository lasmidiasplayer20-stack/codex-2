from pathlib import Path
import os,json,hashlib,wave,base64,urllib.request,urllib.error,time
P=Path(__file__).resolve().parents[1];parser=__import__('argparse').ArgumentParser();parser.add_argument('--work',type=Path,required=True);W=parser.parse_args().work;W.mkdir(parents=True,exist_ok=True)
profile=json.loads((P/'audio/voice-profile.json').read_text());model=profile['model'];direction=profile['direction'];key=os.environ.get('GEMINI_API_KEY')
if not key:raise SystemExit('Missing environment key; no call made.')
assert model=='gemini-2.5-flash-preview-tts'and profile['voice']=='Puck','Same approved voice/model required.'
beats=json.loads((P/'story/beats.json').read_text());manifest=[]
for i,start in enumerate(range(0,len(beats),8),1):
 group=beats[start:start+8];text='\n\n'.join(b['text']for b in group);out=W/f'block-{i:02}.wav';record={'file':out.name,'beats':[b['id']for b in group],'text':text,'direction':direction,'model':model,'voice':'Puck'};sha=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();record['request_sha256']=sha
 if out.exists() and out.with_suffix('.json').exists() and json.loads(out.with_suffix('.json').read_text()).get('request_sha256')==sha:print('CACHED',i,flush=True)
 else:
  if out.exists():raise SystemExit('Unmatched cache; no overwrite.')
  body={'contents':[{'parts':[{'text':direction+'\n\nNARRAÇÃO:\n'+text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':'Puck'}}}}}
  req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
  try:
   with urllib.request.urlopen(req,timeout=300)as r:data=json.load(r)
  except urllib.error.HTTPError as e:
   raw=e.read().decode(errors='replace').replace(key,'[REDACTED]')
   (W/'last-provider-error-private.json').write_text(raw)
   try:
    error=json.loads(raw).get('error',{});safe={'http_status':e.code,'status':error.get('status'),'message':error.get('message','')[:1400]}
   except Exception:safe={'http_status':e.code}
   print('TTS_LIMIT',json.dumps(safe,ensure_ascii=False),flush=True)
   raise SystemExit(f'TTS HTTP {e.code}; stopped without retry or model fallback.')from None
  a=[p['inlineData']for c in data.get('candidates',[])for p in c.get('content',{}).get('parts',[])if'inlineData'in p]
  if not a:
   (W/'empty-response-private.json').write_text(json.dumps(data))
   raise SystemExit('No audio; stopped.')
  raw=base64.b64decode(a[0]['data'])
  if raw[:4]==b'RIFF':out.write_bytes(raw)
  else:
   with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(raw)
  out.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
  with wave.open(str(out))as f:print('GENERATED',i,'seconds',round(f.getnframes()/f.getframerate(),2),flush=True)
  if start+8<len(beats):time.sleep(35)
 manifest.append(record);(W/'episode-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('EPISODE_VOICE_COMPLETE',flush=True)
