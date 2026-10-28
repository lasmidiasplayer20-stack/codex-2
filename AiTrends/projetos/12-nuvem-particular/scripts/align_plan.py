from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];ins=json.loads((P/'audio/quality.json').read_text())['pause_insertions'];mp=lambda t:t+.25+sum(i['insert_seconds']for i in ins if i['raw_time']<t)
raw=[0,3.18,6.512,7.79,11.127,13.224,15.495,17.29,18.756,20.5,22.48,25.414,27,30.805,35.31,37.029,38.884,43.19,47.42,49.3,51.291]
bounds=[0]+[round(mp(t)*24)/24 for t in raw[1:-1]]+[60];old=json.loads((P/'story/shots.json').read_text())
for i,sh in enumerate(old['shots']):sh['start']=bounds[i];sh['end']=bounds[i+1]
(P/'story/shots.json').write_text(json.dumps(old,ensure_ascii=False,indent=2));(P/'story/timing.json').write_text(json.dumps({'method':'Estimated phrase boundaries from sustained waveform gaps, no ASR claim','pause_insertions':ins},indent=2));print([(s['params']['cam'],round(s['start'],2),round(s['end'],2))for s in old['shots']])
