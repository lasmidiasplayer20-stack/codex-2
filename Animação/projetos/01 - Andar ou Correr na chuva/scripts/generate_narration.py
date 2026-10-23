"""Optional Gemini regeneration. Reads GEMINI_API_KEY from the environment; never logs it.
New generations can change timing: remeasure and retime the film before export.
"""
from pathlib import Path
import os,json,urllib.request,urllib.error,base64,time
ROOT=Path(__file__).resolve().parent.parent
key=os.environ.get('GEMINI_API_KEY')
if not key:raise SystemExit('Configure GEMINI_API_KEY securely before generating speech.')
out=ROOT/'audio'/'raw-local';out.mkdir(exist_ok=True)
for i,text in enumerate((ROOT/'narracao.txt').read_text().strip().split('\n\n')):
 path=out/f'parte-{i+1:02d}.wav'
 if path.exists():continue
 body={'model':'gemini-3.8-flash-tts','input':[{'type':'user_input','content':[{'type':'text','text':text,'annotations':[{'type':'speech_metadata','style':'Cheerful, friendly Brazilian Portuguese science presenter. Steady medium volume, conversational pace, brief natural pauses.'}]}]}],'response_format':{'type':'audio'},'generation_config':{'speech_config':[{'voice':'Puck'}]}}
 req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
 try:
  with urllib.request.urlopen(req,timeout=240) as r:data=json.load(r)
 except urllib.error.HTTPError as e:
  raise SystemExit('Gemini request failed with HTTP '+str(e.code)+'. Check quota/access in the provider console; credential was not logged.') from None
 audio=[p for s in data.get('steps',[]) if s.get('type')=='model_output' for p in s.get('content',[]) if p.get('type')=='audio']
 if not audio:raise SystemExit('No audio returned for segment '+str(i+1))
 path.write_bytes(base64.b64decode(audio[-1]['data']));print('Generated segment',i+1,flush=True)
 # Free tiers can limit speech calls to three per minute.
 time.sleep(22)
