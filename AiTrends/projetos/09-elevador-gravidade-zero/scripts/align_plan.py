from pathlib import Path
import json
p=Path(__file__).resolve().parents[1];q=json.loads((p/'audio/quality.json').read_text());ins=q['pause_insertions'];mp=lambda t:t+.25+sum(i['insert_seconds']for i in ins if i['raw_time']<t)
raw=[0,3.4,5.65,7.5,9.15,14.1,17.6,19.6,21.2,24.4,27.7,30.2,33,37.3,39.5,41,42.9,44.95,47.9,50.61]
old=json.loads((p/'story/shots.json').read_text());ends=[0]+[round(mp(t)*24)/24 for t in raw[1:-1]]+[60]
for i,s in enumerate(old['shots']):s['start']=ends[i];s['end']=ends[i+1]
(p/'story/shots.json').write_text(json.dumps(old,ensure_ascii=False,indent=2));print([(s['params']['cam'],s['start'],s['end'])for s in old['shots']]);(p/'story/timing.json').write_text(json.dumps({'alignment':'Estimated clause boundaries on waveform pauses, not ASR','raw_to_timeline_insertions':ins},indent=2))
