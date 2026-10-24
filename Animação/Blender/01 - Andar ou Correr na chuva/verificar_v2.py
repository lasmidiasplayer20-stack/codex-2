"""Checks actual saved keyframes: fixed bones, planted stance, hand contact, packed media."""
import bpy,json,math
from pathlib import Path
s=bpy.context.scene
assert (s.frame_start,s.frame_end,s.render.fps)==(1,1440,24)
assert (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)==(1920,1080,100)
assert len(s.timeline_markers)==17
assert len(bpy.data.sounds)==2 and all(a.packed_file for a in bpy.data.sounds)
assert not [im for im in bpy.data.images if im.source=='FILE' and im.filepath]
max_length_error=0
for f in [150,203,490,550,575,703,960,1145,1283]:
 s.frame_set(f)
 for name in ['Lia','Caio']:
  for side in [-1,1]:
   for limb,length in [('thigh',.61),('shin',.62),('upper',.41),('fore',.39)]:
    o=bpy.data.objects[f'{name} • {side} {limb}'];max_length_error=max(max_length_error,abs(o.scale.z-length))
assert max_length_error<.00001
max_slide=0;planted_pairs=0
for name in ['Lia','Caio']:
 for side in [-1,1]:
  foot=bpy.data.objects[f'{name} • {side} sapato']
  for a,b in [(150,210),(540,565),(920,960),(1260,1320)]:
   prev=None
   for f in range(a,b):
    s.frame_set(f);p=foot.location.copy();flat=abs(p.z-.085)<.0001 and abs(foot.rotation_euler.y)<.0001
    if flat and prev is not None:
     max_slide=max(max_slide,(p-prev).length);planted_pairs+=1
    prev=p if flat else None
assert max_slide<.0001,(max_slide,planted_pairs)
s.frame_set(1145)
contact=(bpy.data.objects['Lia • 1 mão'].location-bpy.data.objects['Caio • -1 mão'].location).length
assert contact<.001
report={'timeline_seconds':60,'resolution':[1920,1080],'fps':24,'shots':17,'packed_audio':2,'imported_images':0,'fixed_segment_max_error_m':max_length_error,'planted_pairs_checked':planted_pairs,'max_planted_foot_slide_m_per_frame':max_slide,'greeting_wrist_distance_m':contact,'validation_scope':'Keyframes salvos e amostras de apoio/contato; a avaliação visual de atuação é separada.'}
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
Path(__file__).with_name('verificacao-v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
