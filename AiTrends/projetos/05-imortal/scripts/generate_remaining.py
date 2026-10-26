from pathlib import Path
import os,json,urllib.request,urllib.error,base64,wave,hashlib,time
P=Path(__file__).resolve().parents[1];parser=__import__('argparse').ArgumentParser();parser.add_argument('--work',type=Path,required=True);W=parser.parse_args().work;assert json.loads((P/'qa/voice-sample.json').read_text())['approval']=='approved_with_discreet_mix','Evaluate a sample first.';beats=json.loads((P/'story/beats.json').read_text());sample=json.loads((W/'sample-original.json').read_text());key=os.environ['GEMINI_API_KEY'];model=sample['model'];direction=sample['direction'];manifest=[{'file':'sample-original.wav','beats':[1],'text':sample['text'],'model':model,'voice':'Puck','approved':True}]
assert sample['text']==beats[0]['text'],'Approved sample must exactly match opening.'
for i,start in enumerate(range(1,len(beats),4),1):
 group=beats[start:start+4];text='\n\n'.join(b['text']for b in group);out=W/f'block-{i:02}.wav';record={'file':out.name,'beats':[b['id']for b in group],'text':text,'direction':direction,'model':model,'voice':'Puck'};sha=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();record['request_sha256']=sha
 if out.exists() and out.with_suffix('.json').exists() and json.loads(out.with_suffix('.json').read_text()).get('request_sha256')==sha:print('CACHED',i,flush=True)
 else:
  if out.exists():raise SystemExit('Unmatched cache; no overwrite.')
  payload={'contents':[{'parts':[{'text':direction+'\n\nNARRAÇÃO:\n'+text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':'Puck'}}}}}
  req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
  try:
   with urllib.request.urlopen(req,timeout=210)as r:data=json.load(r)
  except urllib.error.HTTPError as e:raise SystemExit(f'TTS HTTP {e.code}; stopped without retry or model fallback.')from None
  audio=[p['inlineData']for c in data.get('candidates',[])for p in c.get('content',{}).get('parts',[])if'inlineData'in p]
  if not audio:raise SystemExit('Empty audio; stopped.')
  raw=base64.b64decode(audio[0]['data'])
  if raw[:4]==b'RIFF':out.write_bytes(raw)
  else:
   with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(raw)
  out.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
  with wave.open(str(out))as f:print('GENERATED',i,'seconds',round(f.getnframes()/f.getframerate(),2),flush=True)
  if start+4<len(beats):time.sleep(35)
 manifest.append(record);(W/'episode-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('EPISODE_VOICE_COMPLETE',flush=True)
