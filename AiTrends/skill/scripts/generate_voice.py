"""Optional authorized Puck generation. Secrets only from environment, never files/Git."""
from pathlib import Path
import json,os,urllib.request,urllib.error,base64,time,argparse,hashlib,wave
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--project',type=Path,required=True);p.add_argument('--model',default='gemini-3.8-flash-tts');p.add_argument('--parts',help='Comma-separated one-based parts; default all');p.add_argument('--api',choices=['interactions','generateContent'],default='interactions');a=p.parse_args();
 global ROOT
 ROOT=a.project.resolve();a.work.mkdir(parents=True,exist_ok=True)
 key=os.environ.get('GEMINI_API_KEY')
 if not key:raise SystemExit('GEMINI_API_KEY missing from environment; secret not logged.')
 beats=json.loads((ROOT/'story/beats.json').read_text());groups=[beats[i:i+4]for i in range(0,len(beats),4)]
 manifest=[]
 for i,group in enumerate(groups):
  if a.parts and i+1 not in [int(n)for n in a.parts.split(',')]:continue
  text='\n\n'.join(b['text']for b in group);sha=hashlib.sha256(text.encode()).hexdigest();out=a.work/f'parte-{i+1:02}.wav';meta=out.with_suffix('.json')
  record={'part':i+1,'beats':[b['id']for b in group],'text_sha256':sha,'text':text,'model':a.model,'voice':'Puck'}
  if out.exists()and meta.exists()and json.loads(meta.read_text()).get('text_sha256')==sha and json.loads(meta.read_text()).get('model')==a.model:print('Cached part',i+1,flush=True);manifest.append(record);continue
  body={'model':a.model,'input':[{'type':'user_input','content':[{'type':'text','text':text,'annotations':[{'type':'speech_metadata','style':'Brazilian Portuguese. Cheerful, curious, warm narrative presenter, brisk conversational pace around 165 words per minute. Keep one stable medium volume, avoid sudden loud or whispered passages. Brief natural pauses. Serious beats stay empathetic, not theatrical. Read only the supplied narration exactly, no introductions, no stage directions, no added phrases.'}]}]}],'response_format':{'type':'audio'},'generation_config':{'speech_config':[{'voice':'Puck'}]}}
  endpoint='https://generativelanguage.googleapis.com/v1beta/interactions'
  if a.api=='generateContent':
   endpoint=f'https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent'
   body={'contents':[{'parts':[{'text':text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':'Puck'}}}}}
  req=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
  for attempt in range(4):
   try:
    with urllib.request.urlopen(req,timeout=240)as r:data=json.load(r)
    break
   except urllib.error.HTTPError as e:
    if e.code in [429,500,502,503,504] and attempt<3:
     raw=e.read().decode(errors='replace').replace(key,'[REDACTED]');(a.work/'provider-error-private.txt').write_text(raw)
     if 'per day' in raw.lower():raise SystemExit('Daily free-tier quota exhausted; no billing change attempted.')
     print('Temporary TTS HTTP',e.code,'retry in 55s',attempt+1,flush=True);time.sleep(55)
    else:raise SystemExit(f'Gemini HTTP {e.code}; stopped without logging provider body or credential.')from None
  if a.api=='generateContent':
   audio=[p['inlineData']for c in data.get('candidates',[])for p in c.get('content',{}).get('parts',[])if 'inlineData'in p]
  else:audio=[p for st in data.get('steps',[])if st.get('type')=='model_output'for p in st.get('content',[])if p.get('type')=='audio']
  if not audio:
   safe={'candidate_finish_reasons':[c.get('finishReason')for c in data.get('candidates',[])],'promptFeedback':data.get('promptFeedback'),'candidate_count':len(data.get('candidates',[]))}
   (a.work/'empty-response.json').write_text(json.dumps(safe,indent=2));raise SystemExit(f'No audio for part {i+1}; diagnostic recorded privately')
  raw=base64.b64decode(audio[-1]['data'])
  if raw[:4]==b'RIFF':out.write_bytes(raw)
  else:
   with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(raw)
  record['api']=a.api;meta.write_text(json.dumps(record,ensure_ascii=False,indent=2));manifest.append(record)
  print('Generated Puck part',i+1,'of',len(groups),flush=True)
  if i<len(groups)-1:time.sleep(35)
 (a.work/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print('VOICE_GENERATION_COMPLETE',flush=True)
if __name__=='__main__':main()
