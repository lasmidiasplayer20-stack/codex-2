"""Optional authorized Puck generation. Secrets only from environment, never files/Git."""
from pathlib import Path
import json,os,urllib.request,urllib.error,base64,time,argparse,hashlib
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 key=os.environ.get('GEMINI_API_KEY')
 if not key:raise SystemExit('GEMINI_API_KEY missing from environment; secret not logged.')
 beats=json.loads((ROOT/'story/beats.json').read_text());groups=[beats[i:i+4]for i in range(0,len(beats),4)]
 manifest=[]
 for i,group in enumerate(groups):
  text='\n\n'.join(b['text']for b in group);sha=hashlib.sha256(text.encode()).hexdigest();out=a.work/f'parte-{i+1:02}.wav';meta=out.with_suffix('.json')
  record={'part':i+1,'beats':[b['id']for b in group],'text_sha256':sha,'text':text,'model':'gemini-3.8-flash-tts','voice':'Puck'}
  if out.exists()and meta.exists()and json.loads(meta.read_text()).get('text_sha256')==sha:print('Cached part',i+1,flush=True);manifest.append(record);continue
  body={'model':'gemini-3.8-flash-tts','input':[{'type':'user_input','content':[{'type':'text','text':text,'annotations':[{'type':'speech_metadata','style':'Brazilian Portuguese. Cheerful, curious, warm narrative presenter, brisk conversational pace around 165 words per minute. Keep one stable medium volume, avoid sudden loud or whispered passages. Brief natural pauses. Serious beats stay empathetic, not theatrical. Read only the supplied narration exactly, no introductions, no stage directions, no added phrases.'}]}]}],'response_format':{'type':'audio'},'generation_config':{'speech_config':[{'voice':'Puck'}]}}
  req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
  try:
   with urllib.request.urlopen(req,timeout=240)as r:data=json.load(r)
  except urllib.error.HTTPError as e:raise SystemExit(f'Gemini HTTP {e.code}; stopped without logging provider body or credential.')from None
  audio=[p for st in data.get('steps',[])if st.get('type')=='model_output'for p in st.get('content',[])if p.get('type')=='audio']
  if not audio:raise SystemExit(f'No audio for part {i+1}')
  out.write_bytes(base64.b64decode(audio[-1]['data']));meta.write_text(json.dumps(record,ensure_ascii=False,indent=2));manifest.append(record)
  print('Generated Puck part',i+1,'of',len(groups),flush=True)
  if i<len(groups)-1:time.sleep(22)
 (a.work/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print('VOICE_GENERATION_COMPLETE',flush=True)
if __name__=='__main__':main()
