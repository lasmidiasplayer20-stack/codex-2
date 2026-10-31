# Usage: python3 verify_narration.py ABS_PROJECT PRIVATE_WORK; GEMINI_API_KEY from environment.
from pathlib import Path
import subprocess,os,sys,json,base64,urllib.request,urllib.error,difflib,re
model=os.environ.get('ASR_MODEL','gemini-3-flash-preview');p=Path(sys.argv[1]);w=Path(sys.argv[2]);out=p/'qa/narration-check.json'
if out.exists():raise SystemExit(0)
key=os.environ.get('GEMINI_API_KEY')
if not key:raise SystemExit('Missing environment key; no request made.')
encoded=w/'voice-check.mp3';subprocess.run(['ffmpeg','-v','error','-y','-i',str(w/'voice/block-01.wav'),'-c:a','libmp3lame','-b:a','64k',str(encoded)],check=True)
body={'contents':[{'parts':[{'text':'Transcreva literalmente o áudio em português, preservando repetições reais. Segmente por frase, com tempos aproximados de início e fim em segundos. Retorne JSON {"segments":[{"start":0,"end":1,"text":"..."}],"repeated_phrases":[]}. Não invente palavras em silêncios.'},{'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(encoded.read_bytes()).decode()}}]}],'generationConfig':{'temperature':0,'responseMimeType':'application/json'}}
req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
try:
 with urllib.request.urlopen(req,timeout=180)as f:data=json.load(f)
 raw=''.join(part.get('text','')for c in data.get('candidates',[])for part in c.get('content',{}).get('parts',[]));q=json.loads(raw)
except urllib.error.HTTPError as e:
 (w/'asr-error-private.json').write_text(e.read().decode().replace(key,'[REDACTED]'));raise SystemExit(f'ASR HTTP {e.code}; stopped')from None
expected=(p/'input/narracao.txt').read_text();actual=' '.join(s['text']for s in q['segments']);norm=lambda x:re.sub(r'[^\w]+',' ',x.lower()).split();ratio=difflib.SequenceMatcher(None,norm(expected),norm(actual)).ratio();q.update({'model':model,'expected':expected,'word_similarity':ratio,'human_full_listening':False,'timing':'approximate automatic transcription','passed':ratio>.9 and not q.get('repeated_phrases')});out.write_text(json.dumps(q,ensure_ascii=False,indent=2));print('ASR',ratio,'PASS',q['passed'],flush=True)
if not q['passed']:raise SystemExit('Review transcript before proceeding')
