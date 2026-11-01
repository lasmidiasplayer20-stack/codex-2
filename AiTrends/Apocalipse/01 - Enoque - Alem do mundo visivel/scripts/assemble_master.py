"""Assemble validated PCM parts and export a continuous 25-minute MP3."""
from pathlib import Path
import argparse,json,subprocess,wave,hashlib
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);o=a.parse_args();o.work.mkdir(parents=True,exist_ok=True);parts=json.loads((P/'roteiro/partes.json').read_text());records=[];master=o.work/'master-25-minutos.wav'
with wave.open(str(master),'wb')as out:
 out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000)
 for part in parts:
  n=part['part'];qa=json.loads((P/f'qa/part-{n:02}.json').read_text());speech=json.loads((P/f'qa/speech-{n:02}.json').read_text());assert not speech['spoken_instructions'];assert speech['word_sequence_similarity']>=.97 or speech.get('editorial_review')in ['accepted_asr_spelling_only','accepted_minor_delivery_and_asr_variants']
  with wave.open(str(P/qa['wav']),'rb')as f:
   assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())==(1,2,24000,1440000);data=f.readframes(f.getnframes());out.writeframesraw(data)
  meta=json.loads((o.work/f"{n:02}-raw.json").read_text());records.append({'part':n,'title':part['title'],'start_seconds':(n-1)*60,'end_seconds':n*60,'wav':qa['wav'],'mp3':qa['mp3'],'wav_sha256':hashlib.sha256((P/qa['wav']).read_bytes()).hexdigest(),'text_sha256':hashlib.sha256(part['text'].encode()).hexdigest(),'tts_request_sha256':meta.get('provider_request_sha256',meta['request_sha256']),'generation_type':meta.get('generation_type','individual'),'source_block':meta.get('source_block'),'raw_seconds':meta['raw_seconds'],'editorial_audio_cuts_seconds':qa.get('editorial_audio_cuts_seconds',[]),'editorial_review':speech.get('editorial_review'),'integrated_lufs':qa['integrated_lufs'],'true_peak_dbtp':qa['true_peak_dbtp'],'speech_word_sequence_similarity':speech['word_sequence_similarity']})
assert len(records)==25
out=P/'audio/01 - Enoque - Alem do mundo visivel - Completo.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(master),'-c:a','libmp3lame','-b:a','192k','-metadata','title=Enoque - Além do mundo visível','-metadata','artist=Então','-metadata','album=Apocalipse',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out)]));decoded=o.work/'master-decode.s16';subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-f','s16le','-acodec','pcm_s16le',str(decoded)],check=True);samples=decoded.stat().st_size//2;assert samples==1500*24000,samples
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-af','loudnorm=I=-19:TP=-3.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
level=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];assert float(level['input_tp'])< -2
report={'master_integrated_lufs':float(level['input_i']),'master_true_peak_dbtp':float(level['input_tp']),'master_lra_lu':float(level['input_lra']),'complete':True,'voice':'Algenib','model':'gemini-2.5-flash-preview-tts','approved_sample_revision':1,'approval_user_quote':'volte com a primeira versão e manda ver','parts':records,'pcm_total_seconds':1500,'decoded_mp3_samples':samples,'decoded_mp3_seconds':samples/24000,'mp3_container_seconds':float(probe['format']['duration']),'note':'MP3 container may include encoder padding; decoded audio and WAV parts have exact target length.','full_decode_passed':True,'human_full_listening':False,'video_created':False,'credentials_committed':False,'master_mp3':str(out.relative_to(P)),'master_sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(P/'qa/DELIVERY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('MASTER_READY',out.name,'decoded',samples/24000,'container',probe['format']['duration'],flush=True)
