"""Split a cached block at reviewed silent boundaries, then validate each part by ASR."""
from pathlib import Path
import argparse,json,hashlib,wave
import numpy as np
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--parts',type=int,nargs='+',required=True);a.add_argument('--cuts',type=float,nargs='+',required=True);a.add_argument('--work',type=Path,required=True);o=a.parse_args();assert len(o.cuts)+1==len(o.parts);profile=json.loads((P/'audio/voice-profile.json').read_text());records=json.loads((P/'roteiro/partes.json').read_text());parent=json.loads(o.source.with_suffix('.json').read_text())
with wave.open(str(o.source))as f:assert f.getnchannels()==1 and f.getsampwidth()==2;fs=f.getframerate();data=f.readframes(f.getnframes())
x=np.frombuffer(data,dtype=np.int16);bounds=[0,*[round(t*fs)for t in o.cuts],len(x)];assert bounds==sorted(bounds)
for pos in bounds[1:-1]:assert np.max(np.abs(x[pos-int(.02*fs):pos+int(.02*fs)].astype(float)))<655,'Boundary not quiet'
for n,begin,end in zip(o.parts,bounds,bounds[1:]):
 part=next(p for p in records if p['part']==n);record={'part':n,'text':part.get('tts_source_text',part['text']),'voice':profile['voice'],'model':profile['model'],'direction':profile['direction']};record['request_sha256']=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();record.update(generation_type='shared_block',provider_request_sha256=parent['request_sha256'],source_block=o.source.name,source_sample_range=[begin,end],source_seconds_range=[begin/fs,end/fs],raw_seconds=(end-begin)/fs,credential_slot=parent['credential_slot']);out=o.work/f'{n:02}-raw.wav';assert not out.exists(),'Refuse to overwrite split source without explicit editorial handling'
 with wave.open(str(out),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(fs);f.writeframes(x[begin:end].tobytes())
 out.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('SPLIT_READY',n,record['raw_seconds'],flush=True)
