from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];q=json.loads((P/'audio/quality.json').read_text());ins=q['pause_insertions'];mp=lambda t:t+.25+sum(i['insert_seconds']for i in ins if i['raw_time']<t)
raw=[0,4.13,6.08,7.53,9.33,12.21,17.23,20.93,23.9,26.13,28.13,30.44,32.09,35.09,38.81,42.32,45.77,48.9,50.1,51.7,54.57]
bounds=[0]+[round(mp(t)*24)/24 for t in raw[1:-1]]+[60]
# Final release insert is brief; the gag plays visibly rather than behind a watch close-up.
bounds[-3]=54;bounds[-2]=57
s=json.loads((P/'story/shots.json').read_text())
for i,shot in enumerate(s['shots']):shot['start']=bounds[i];shot['end']=bounds[i+1]
assert all(x['end']>x['start']for x in s['shots']);(P/'story/shots.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));(P/'story/timing.json').write_text(json.dumps({'method':'Clause estimates at sustained waveform gaps, not ASR. Last gag timing directed visually.','pause_insertions':ins},indent=2));print([(x['params']['cam'],round(x['start'],2),round(x['end'],2))for x in s['shots']])
