"""Join original visual clips to existing PCM narration; never generate speech."""
from pathlib import Path
import argparse,json,subprocess,wave,hashlib,tempfile,math

def probe(path,count=False):
 args=['ffprobe','-v','error']
 if count:args+=['-count_frames']
 return json.loads(subprocess.check_output(args+['-show_streams','-show_format','-of','json',str(path)]))

def run(args):subprocess.run(args,check=True)

def main():
 a=argparse.ArgumentParser();a.add_argument('--plan',type=Path,required=True);a.add_argument('--out',type=Path);a.add_argument('--work',type=Path);a.add_argument('--check',action='store_true');a.add_argument('--allow-draft-preview',action='store_true');o=a.parse_args();planpath=o.plan.resolve();base=planpath.parent;plan=json.loads(planpath.read_text());fps=int(plan['fps']);width=int(plan['width']);height=int(plan['height']);assert fps>0 and width>0 and height>0
 total_frames=0;ids=set();missing=[];clips=[]
 for s in plan['shots']:
  assert s['id']not in ids,'Repeated shot ID';ids.add(s['id']);duration=float(s['duration_seconds']);frames=round(duration*fps);assert duration>0 and abs(frames/fps-duration)<1e-6,'Duration must fit whole frames'
  assert abs(float(s['start_seconds'])-total_frames/fps)<1e-6,'Timeline gap or overlap';total_frames+=frames;source=(base/s['clip']).resolve();inside=float(s.get('source_in_seconds',0));assert inside>=0
  if not source.exists():missing.append({'id':s['id'],'file':s['clip']})
  else:
   q=probe(source);v=next(x for x in q['streams']if x['codec_type']=='video');seconds=float(v.get('duration',q['format']['duration']));assert seconds-inside+.02>=duration,f"Short clip {s['id']}: generate continuation or revise the cut; never freeze, loop or speed up automatically"
  clips.append((s,source,inside,frames))
 total=total_frames/fps;assert abs(total-float(plan['duration_seconds']))<1e-6
 audio=[];audio_frames=0;params=None
 for f in plan['audio_files']:
  path=(base/f).resolve()
  with wave.open(str(path))as w:
   current=(w.getnchannels(),w.getsampwidth(),w.getframerate());assert current[1]==2,'Use original PCM16 WAV narration';params=params or current;assert current==params;audio_frames+=w.getnframes()
  audio.append(path)
 assert params and abs(audio_frames/params[2]-total)<.001,'Narration and plan must have identical duration'
 summary={'plan':planpath.name,'duration_seconds':total,'frames':total_frames,'resolution':[width,height],'fps':fps,'shots':len(clips),'missing_clips':missing,'audio_seconds':audio_frames/params[2],'timing_status':plan.get('timing_status'),'generates_voice':False,'calls_paid_apis':False}
 if o.check:print(json.dumps(summary,ensure_ascii=False,indent=2));return
 assert not missing,'Missing visual clips; --check lists them. No generation API is called.'
 assert o.out,'--out required';assert plan.get('timing_status')=='ready' or o.allow_draft_preview,'Draft timing: review against narration, or use --allow-draft-preview for a pilot only'
 out=o.out.resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if o.work:work=o.work.resolve();work.mkdir(parents=True,exist_ok=True)
 else:work=Path(tempfile.mkdtemp(prefix='enoch-assembly-'))
 narration=work/'narration.wav'
 with wave.open(str(narration),'wb')as w:
  w.setnchannels(params[0]);w.setsampwidth(params[1]);w.setframerate(params[2])
  for path in audio:
   with wave.open(str(path))as source:w.writeframesraw(source.readframes(source.getnframes()))
 scene_paths=[]
 for i,(s,source,inside,frames)in enumerate(clips):
  target=work/f'shot-{i:04}.mp4';vf=f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps},setsar=1,setpts=PTS-STARTPTS'
  run(['ffmpeg','-v','error','-y','-ss',str(inside),'-i',str(source),'-an','-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','24000',str(target)])
  q=probe(target,True);v=next(x for x in q['streams']if x['codec_type']=='video');assert int(v['nb_read_frames'])==frames,'Insufficient decoded frames';scene_paths.append(target.name)
 listing=work/'clips.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\n"for p in scene_paths));silent=work/'video-silent.mp4'
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(silent)])
 run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(narration),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(total),'-movflags','+faststart',str(out)])
 run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-']);q=probe(out,True);v=next(x for x in q['streams']if x['codec_type']=='video');assert int(v['nb_read_frames'])==total_frames;assert(v['width'],v['height'])==(width,height);assert any(x['codec_type']=='audio'for x in q['streams']);assert abs(float(q['format']['duration'])-total)<.05
 summary.update(full_decode_passed=True,rendered_frames=int(v['nb_read_frames']),output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),narration_pcm_sha256=hashlib.sha256(narration.read_bytes()).hexdigest(),incoming_clip_audio_discarded=True,voice_pitch_or_speed_changed=False,draft_preview=plan.get('timing_status')!='ready');out.with_suffix('.qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
