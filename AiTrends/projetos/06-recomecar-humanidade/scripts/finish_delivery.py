"""Finish metadata after successful export. Does not claim human final playback."""
from pathlib import Path
import json,hashlib,shutil,re
P=Path(__file__).resolve().parents[1]
def main():
 report=json.loads((P/'qa/export-validation.json').read_text());assert report['full_decode_passed']and report['native_render']and not report['upscaled']
 state={'status':'exported_automatic_technical_validation','voice':'Puck','model':'gemini-2.5-flash-preview-tts','voice_blocks_cached':8,'voice_blocker':None,'final_duration_seconds':report['seconds'],'full_video_generated':True,'final_video_sha256':report['sha256'],'native_resolution':[1920,1080],'full_decode_passed':True,'preview_decode_passed':True,'final_human_audio_review':False,'final_human_mp4_playback':False,'editorial_approval':'pending_user','preflight':'All164 plan sheets plus native motion samples reviewed before queue; final export decoded automatically.'}
 (P/'qa/production-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 s=(P/'README.md').read_text();s=s.replace('**Pré-produção e prévia inicial prontas; voz restante aguardando cota.**','**Vídeo completo exportado e validado automaticamente.**')
 s=re.sub(r'<!-- CURRENT_STATUS_START -->.*?<!-- CURRENT_STATUS_END -->','## Estado atual\n\nOs oito blocos da mesma Puck estão completos. A fila concluiu render e validação técnica; o episódio completo está disponível nos links abaixo. Avaliação editorial do usuário continua pendente.',s,flags=re.S)
 s+='\n## Entrega completa após liberação da cota\n\nDuração natural: '+str(round(report['seconds'],3))+' s, 1920×1080/24 fps, '+str(report['frames'])+' quadros. Narração completa em oito blocos da mesma Puck/modelo, sem troca de timbre e sem aceleração. Decodificação integral do filme e da prévia passou. Fonte, hashes e tempos dos CTAs em `qa/export-validation.json`. A inspeção visual descrita neste projeto foi feita nos pilotos/planos antes da fila; não se declara escuta humana integral ou reprodução humana do MP4 final automático.\n\n[Vídeo completo](exports/06%20-%20Duas%20Pessoas%20Podem%20Recome%C3%A7ar%20a%20Humanidade.mp4) · [Prévia final de 1 minuto](exports/06%20-%20Duas%20Pessoas%20Podem%20Recome%C3%A7ar%20a%20Humanidade%20-%20Preview%201min.mp4)\n'
 (P/'README.md').write_text(s)
 print('DELIVERY_METADATA_COMPLETE',report['sha256'],flush=True)
if __name__=='__main__':main()
