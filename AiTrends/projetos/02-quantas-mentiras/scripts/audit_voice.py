"""Optional Gemini ASR content check on our generated speech; secrets env-only.
This is an automated cross-check, not a claim of human listening.
"""
from pathlib import Path
import os,json,urllib.request,urllib.error,base64,subprocess,re,difflib,argparse,time
ROOT=Path(__file__).resolve().parent.parent
def norm(s):return re.findall(r'\w+',s.lower())
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();key=os.environ.get('GEMINI_API_KEY')
 if not key:raise SystemExit('GEMINI_API_KEY missing')
 report=[]
 for i in range(1,9):
  stem=f'parte-{i:02}';wav=a.work/(stem+'.wav');mp3=a.work/(stem+'-audit.mp3');out=a.work/(stem+'-transcript.txt');meta=json.loads(wav.with_suffix('.json').read_text())
  if not out.exists():
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-ar','16000','-ac','1','-b:a','64k',str(mp3)],check=True)
   body={'contents':[{'parts':[{'text':'Transcreva literalmente toda a fala deste áudio em português brasileiro. Retorne somente as palavras faladas, sem resumo, sem análise e sem introdução. Preserve o nome do canal Então.'},{'inlineData':{'mimeType':'audio/mpeg','data':base64.b64encode(mp3.read_bytes()).decode()}}]}],'generationConfig':{'temperature':0}}
   req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
   for attempt in range(4):
    try:
     with urllib.request.urlopen(req,timeout=240)as r:d=json.load(r)
     break
    except urllib.error.HTTPError as e:
     if e.code in [429,500,502,503,504] and attempt<3:
      print('ASR transient HTTP',e.code,'retry',attempt+1,flush=True);time.sleep(25)
     else:raise SystemExit(f'ASR check HTTP {e.code}; credential/provider body not logged.')from None
    except (TimeoutError,urllib.error.URLError):
     if attempt<3:print('ASR timeout; retry',attempt+1,flush=True);time.sleep(20)
     else:raise SystemExit('ASR unavailable after bounded timeout retries.')from None
   text='\n'.join(p.get('text','')for c in d.get('candidates',[])for p in c.get('content',{}).get('parts',[]));out.write_text(text)
   if not text:raise SystemExit('Empty ASR response')
  text=out.read_text();expected=norm(meta['text']);actual=norm(text);ratio=difflib.SequenceMatcher(None,expected,actual,autojunk=False).ratio()
  unexpected=[w for w in ['programação','programar','código','speech','metadata','prompt','instruções','narration']if w in norm(text)and w not in expected]
  record={'part':i,'word_similarity':ratio,'unexpected_instruction_terms':unexpected,'source_words':len(expected),'transcribed_words':len(actual),'method':'Gemini automated independent audio transcription comparison; not human listening.'}
  report.append(record);print('Speech part',i,'similarity',round(ratio,4),'instruction flags',len(unexpected),flush=True)
 (ROOT/'audio/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if any(r['word_similarity']<.88 or r['unexpected_instruction_terms']for r in report):raise SystemExit('Manual editorial review needed before final export.')
 print('VOICE_CONTENT_AUDIT_PASSED',flush=True)
if __name__=='__main__':main()
