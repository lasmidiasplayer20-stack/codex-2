"""Finalize metadata only after validated native export; never claim human full listening."""
from pathlib import Path
import json,re
from urllib.parse import quote
P=Path(__file__).resolve().parents[1]
def main():
 r=json.loads((P/'qa/export-validation.json').read_text());assert r['full_decode_passed']and r['native_render']and not r['upscaled']and r['seconds']<=600
 m,s=divmod(round(r['seconds']),60);state={'status':'complete_export_technical_checks_passed','voice':'Puck','model':'gemini-2.5-flash-preview-tts','voice_blocks':4,'final_seconds':r['seconds'],'maximum_seconds':600,'full_video_generated':True,'full_decode_passed':True,'final_sha256':r['sha256'],'final_human_listening':False,'independent_full_ASR':False,'user_editorial_approval':False};(P/'qa/production-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 txt=(P/'README.md').read_text();txt=re.sub(r'<!-- CURRENT_STATUS_START -->.*?<!-- CURRENT_STATUS_END -->',f'<!-- CURRENT_STATUS_START -->\n**Completo: {m}min{s:02}s, 1920×1080/24fps, abaixo de10min.** Puck em quatro blocos da mesma sessão/modelo, sem aceleração, Foley Python e prévia final de1min. Decodificação integral validada; não se declara escuta humana integral nem aprovação editorial.\n<!-- CURRENT_STATUS_END -->',txt,flags=re.S);title=json.loads((P/'config.json').read_text())['title'];txt+='\n## Exportação final\n\n[Vídeo completo](exports/'+quote(title+'.mp4')+') · [Prévia final de1min](exports/'+quote(title+' - Preview 1min.mp4')+')\n\nValidações, quadros, codecs, duração, hash e CTAs em `qa/export-validation.json`.\n';(P/'README.md').write_text(txt);print('DELIVERY_METADATA_COMPLETE',r['sha256'],flush=True)
if __name__=='__main__':main()
