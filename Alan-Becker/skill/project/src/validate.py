#!/usr/bin/env python3
"""Validate complete vector coverage, native export, and retained source audio."""
from array import array
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import subprocess
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT.parents[1]/'video/teamwater-recriado-1080p.mp4'
SOURCE=ROOT/'assets/reference.mp4'

def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))

def audio(p,t):
 raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-t','2','-vn','-ac','1','-ar','16000','-f','s16le','pipe:1'])
 return np.frombuffer(raw,dtype='<i2').astype(float)

source=probe(SOURCE);out=probe(VIDEO)
s=next(x for x in source['streams'] if x['codec_type']=='video')
v=next(x for x in out['streams'] if x['codec_type']=='video')
a=next(x for x in out['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'])==(1920,1080)
assert Fraction(v['avg_frame_rate'])==Fraction(s['avg_frame_rate'])==Fraction(24000,1001)
assert int(v['nb_read_frames'])==int(s['nb_read_frames'])==4078
assert abs(float(out['format']['duration'])-float(source['format']['duration']))<.05
assert a['codec_name']=='aac'
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(VIDEO),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
frames=[];flow_frames=[];motion_count=0;archives=[]
for p in sorted((ROOT/'analysis').glob('part-*.json')):
 data=json.loads(p.read_text())
 frames.extend(x['frame'] for x in data['frames_mapping'])
 motion_count+=sum('motion_from_previous' in x for x in data['frames_mapping'])
 expected=[f'{i:06d}.svg' for i in range(data['start_frame'],data['end_frame_exclusive'])]
 actual=[]
 for name in data.get('vector_archives') or [data['vector_archive']]:
  with zipfile.ZipFile(ROOT/name) as bundle:
   assert bundle.testzip() is None
   actual.extend(bundle.namelist())
   for entry in bundle.namelist():
    svg=bundle.read(entry);assert b'<image' not in svg and b'base64' not in svg
   archives.append({'file':name,'frames':len(bundle.namelist()),'bytes':(ROOT/name).stat().st_size})
 assert actual==expected
 flow=np.load(ROOT/'analysis'/f"flow-{data['part']:02d}.npz")
 assert flow['flow'].shape==(data['frames'],45,80,2)
 assert np.isfinite(flow['flow']).all()
 flow_frames.extend(map(int,flow['frame_indices']))
assert frames==list(range(4078)) and flow_frames==frames
assert motion_count==4077
checks=[]
for t in [0,20,50,80,110,140,165]:
 x,y=audio(SOURCE,t),audio(VIDEO,t);n=min(len(x),len(y));assert n>10000
 norm=math.sqrt(float((x[:n]**2).sum()*(y[:n]**2).sum()))
 correlation=float(np.dot(x[:n],y[:n])/norm)
 assert correlation>.999,(t,correlation)
 checks.append({'time_seconds':t,'correlation':correlation})
report={'status':'passed','video':str(VIDEO.relative_to(ROOT.parents[1])),'sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
 'bytes':VIDEO.stat().st_size,'width':1920,'height':1080,'fps':v['avg_frame_rate'],'frames':4078,
 'duration_seconds':float(out['format']['duration']),'full_video_audio_decode':'passed',
 'mapped_frames':len(frames),'mapped_transitions':motion_count,'vector_archives':archives,
 'flow_grids':'All present, finite, and aligned to source frame indices','audio_alignment':checks,
 'pixel_identical':False,'limits':'Vector approximation of compressed 640x360 source; not a recovered original rig or hidden motion. Optical flow/camera candidates are estimates.'}
(ROOT/'analysis/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
