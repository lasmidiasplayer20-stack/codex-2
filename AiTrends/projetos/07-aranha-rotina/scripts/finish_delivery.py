"""Finalize metadata only after technical native export, without claiming human listening."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[1]
def main():
 r=json.loads((P/'qa/export-validation.json').read_text());assert r['full_decode_passed'] and r['native_render'] and not r['upscaled'];m,s=divmod(round(r['seconds']),60)
 state={'status':'complete_export_technical_checks_passed','voice':'Puck','model':'gemini-2.5-flash-preview-tts','voice_blocks':8,'final_seconds':r['seconds'],'full_video_generated':True,'full_decode_passed':True,'final_sha256':r['sha256'],'final_human_listening':False,'independent_full_ASR':False,'user_editorial_approval':False}
 scope=json.loads((P/'qa/audio-review-scope.json').read_text());scope['remaining_voice_blocks']=0;scope['final_voice_complete']=True;(P/'qa/audio-review-scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n')
 (P/'qa/production-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 txt=(P/'README.md').read_text();txt=re.sub(r'<!-- CURRENT_STATUS_START -->.*?<!-- CURRENT_STATUS_END -->',f'<!-- CURRENT_STATUS_START -->\n**Completo: {m}min{s:02}s, 1920×1080/24fps.** Oito blocos da mesma Puck/modelo, tratamento leve, Foley Python e prévia final de1min. Exportação e decodificação integral validadas. Não se declara escuta humana integral nem aprovação editorial do usuário.\n<!-- CURRENT_STATUS_END -->',txt,flags=re.S)
 title=json.loads((P/'config.json').read_text())['title'];from urllib.parse import quote
 txt+='\n## Exportação final\n\n[Vídeo completo](exports/'+quote(title+'.mp4')+') · [Prévia final](exports/'+quote(title+' - Preview 1min.mp4')+')\n\nConfira hashes, duração, quadros e CTAs em `qa/export-validation.json`.\n';(P/'README.md').write_text(txt);print('DELIVERY_METADATA_COMPLETE',r['sha256'],flush=True)
if __name__=='__main__':main()
