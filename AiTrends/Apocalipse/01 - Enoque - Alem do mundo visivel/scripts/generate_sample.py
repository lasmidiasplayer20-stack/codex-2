from pathlib import Path
import argparse,os,json,hashlib,urllib.request,urllib.error,base64,wave
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work;W.mkdir(parents=True,exist_ok=True);profile=json.loads((P/'audio/voice-profile.json').read_text());text=(P/'roteiro/amostra-de-voz.txt').read_text().strip();model=profile['model'];voice=profile['voice'];assert voice=='Algenib'and model=='gemini-2.5-flash-preview-tts';record={'model':model,'voice':voice,'text':text,'direction':profile['direction']};sha=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();record['request_sha256']=sha;out=W/'sample-raw.wav'
if out.exists():
 assert json.loads(out.with_suffix('.json').read_text())['request_sha256']==sha,'Mismatched cache, no overwrite';print('SAMPLE_CACHED');raise SystemExit(0)
key=os.environ.get('GEMINI_API_KEY');assert key,'Environment key missing; no call made.'
body={'contents':[{'parts':[{'text':profile['direction']+'\n\nNARRAÇÃO:\n'+text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':voice}}}}}
try:
 req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
 with urllib.request.urlopen(req,timeout=240)as f:q=json.load(f)
except urllib.error.HTTPError as e:
 raw=e.read().decode().replace(key,'[REDACTED]');(W/'sample-error-private.txt').write_text(raw);print('SAMPLE_HTTP',e.code);raise SystemExit(1)from None
parts=[p['inlineData']for c in q.get('candidates',[])for p in c.get('content',{}).get('parts',[])if'inlineData'in p];assert parts,'No voice returned';data=base64.b64decode(parts[0]['data'])
if data[:4]==b'RIFF':out.write_bytes(data)
else:
 with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(data)
out.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
with wave.open(str(out))as f:print('ALGENIB_SAMPLE_READY',f.getnframes()/f.getframerate(),flush=True)
