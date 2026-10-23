import bpy, math, random, os, json, sys
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('RAIN_RENDER_DIR',str(BASE/'verificacao'))); OUT.mkdir(parents=True,exist_ok=True)
random.seed(17)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE_NEXT'; s.eevee.taa_render_samples=16
s.render.resolution_x=1920; s.render.resolution_y=1080; s.render.resolution_percentage=100
s.render.fps=24; s.frame_start=1; s.frame_end=1440
s.world.color=(.26,.32,.40); s.view_settings.view_transform='Standard'
s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.render.threads_mode='FIXED'; s.render.threads=4
geo=bpy.data.collections.new('01 • Geometria com traço'); s.collection.children.link(geo)
fx=bpy.data.collections.new('02 • Chuva e efeitos'); s.collection.children.link(fx)
rig=bpy.data.collections.new('03 • Câmeras e direção'); s.collection.children.link(rig)
def move_coll(o,c):
 for old in list(o.users_collection): old.objects.unlink(o)
 c.objects.link(o)
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=.83
 return m
M={n:mat(n,c) for n,c in {'ink':(.035,.025,.065),'skin':(.91,.57,.34),'blue':(.10,.43,.69),'coral':(.92,.29,.19),'pants':(.10,.15,.23),'shoe':(.97,.87,.65),'road':(.26,.34,.40),'sidewalk':(.55,.62,.65),'teal':(.18,.44,.43),'cream':(.89,.79,.59),'roof':(.16,.25,.32),'water':(.20,.64,.78),'white':(.94,.94,.85),'yellow':(1,.73,.19)}.items()}
def finish(o,n,m,c=geo):
 o.name=n; o.data.materials.append(M[m]); move_coll(o,c); return o
def cube(n,loc,scale,m,bevel=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=finish(bpy.context.object,n,m); o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Cantos arredondados','BEVEL'); mod.width=bevel; mod.segments=2
  o.modifiers.new('Normais','WEIGHTED_NORMAL')
 return o
def ball(n,loc,scale,m,c=geo):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc); o=finish(bpy.context.object,n,m,c); o.scale=scale
 for p in o.data.polygons:p.use_smooth=True
 return o
def rod(n,a,b,r,m,c=geo):
 bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=1); o=finish(bpy.context.object,n,m,c)
 aim(o,a,b,r); return o
def aim(o,a,b,r=None):
 a,b=Vector(a),Vector(b); d=b-a; o.location=(a+b)/2; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.scale.z=d.length

def key(o,f,rot=True):
 o.keyframe_insert('location',frame=f)
 if rot:o.keyframe_insert('rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler',frame=f)
 o.keyframe_insert('scale',frame=f)
# Set: a readable 20m route, warm shelters, cool rainy street.
cube('Rua • percurso real', (0,0,-.16),(27,8,.3),'road',.1)
for y in [-3.5,3.5]:
 cube('Calçada',(0,y,.01),(27,1,.22),'sidewalk')
 for x in range(-12,14,2): cube('Junta calçada',(x,y,.125),(.025,.94,.012),'roof',0)
for x in range(-12,13,3):cube('Faixa central',(x,1.45,.005),(1.3,.10,.018),'cream',.01)
for x in [-10,10]:
 cube('Abrigo • plataforma',(x,0,-.055),(3.3,4,.1),'cream')
 cube('Abrigo • teto',(x,0,3.5),(3.9,4.3,.26),'teal')
 for y in [-1.7,1.7]:rod('Coluna',(x+1.3,y,.12),(x+1.3,y,3.4),.09,'roof')
 cube('Banco',(x,1.5,.65),(2.4,.45,.2),'roof')
for x in [-11,-6,-1,4,9]:
 cube('Fachada',(x,5,2.6),(4.2,2,5.2),'cream' if x%2 else 'teal',.15)
 for xx in [-.9,.9]:
  for z in [1.5,3.4]:cube('Janela',(x+xx,3.97,z),(1.1,.06,1.1),'roof',.03)
for x,y,sc in [(-3,-.6,1),(2,.9,.7),(6,-1,.9)]:ball('Poça',(x,y,.018),(sc,.6,.014),'water',fx)
# Typography is geometry, not an image.
def text(n,body,loc,size=.35):
 bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name=n;o.data.body=body;o.data.align_x='CENTER';o.data.size=size;o.rotation_euler=(math.pi/2,0,0);o.data.extrude=.003;o.data.materials.append(M['white']);move_coll(o,fx);return o
text('Destino','ABRIGO',(10,-2.18,3.45),.36)
text('Origem','MESMO CAMINHO',(-10,-2.18,3.45),.25)
# Object rigs. Joints and limbs are explicitly posed; no uncontrolled hand noise.
actors=[]
for name,color,lane in [('Lia','coral',-.8),('Caio','blue',.8)]:
 a={'name':name,'lane':lane,'parts':{},'limbs':{},'joints':{}}
 for n,sc,m in [('torso',(.27,.20,.39),color),('head',(.255,.24,.29),'skin'),('hair',(.27,.245,.16),'ink'),('eyeL',(.027,.022,.035),'ink'),('eyeR',(.027,.022,.035),'ink')]:a['parts'][n]=ball(name+' • '+n,(0,0,0),sc,m)
 for side in [-1,1]:
  for n,m,r in [('thigh','pants',.10),('shin','pants',.085),('upper',color,.075),('fore','skin',.065)]:a['limbs'][(side,n)]=rod(name+' • '+str(side)+' '+n,(0,0,0),(0,0,1),r,m)
  a['parts'][('foot',side)]=ball(name+' • sapato',(0,0,0),(.23,.115,.10),'shoe')
  a['parts'][('hand',side)]=ball(name+' • mão',(0,0,0),(.08,.075,.09),'skin')
 actors.append(a)
def smooth(q): q=max(0,min(1,q));return q*q*(3-2*q)
def route(t,i):
 # Walk forward, hesitate, then travel the full route. Motion is visible against landmarks.
 if t<6:return -10,0,0
 if t<13:return -10+(t-6)*.65,.65,(t-6)*.65
 if t<21:return -5.45,0,4.55
 speed=1.65 if i==0 else .55
 d=min(14.9,max(0,(t-21)*speed));x=-5.45+d
 if t<50:return x, speed if d<14.9 else 0,4.55+d
 # Final matched start demonstrates equal path, independent of first story.
 d=min(17.8,(t-50)*(2.0 if i==0 else .9));return -9+d,(2.0 if i==0 else .9) if d<17.8 else 0, d

def foot_local(distance,speed,side):
 stride=1.05 if speed>1.2 else .72
 p=(distance/stride+(0 if side==-1 else .5))%1
 stance=.62 if speed<1.2 else .5
 if speed==0:return (0,.10)
 if p<stance:return (stride*(stance/2-p),.10)
 u=(p-stance)/(1-stance);return (stride*stance*(-.5+u),.10+(.16 if speed<1.2 else .26)*math.sin(math.pi*u))
def knee(hip,ankle,L=.46):
 h,a=Vector(hip),Vector(ankle);mid=(h+a)/2;v=a-h;dist=min(v.length,2*L-.001)
 axis=Vector((1,0,0)); perp=axis-v.normalized()*axis.dot(v.normalized());perp.normalize()
 return mid+perp*math.sqrt(max(.001,L*L-dist*dist/4))
checks=[]
for f in range(1,1441):
 t=(f-1)/24
 for i,a in enumerate(actors):
  x,speed,dist=route(t,i);lane=a['lane'];run=speed>1.2
  cycle=dist/(1.05 if run else .72)*math.tau
  bounce=(.035 if run else .016)*(1-math.cos(2*cycle)) if speed else 0
  hipZ=1.06+bounce
  # Character faces +X. Lean is bounded and only occurs in the run.
  lean=.11 if run else .015
  positions={'torso':(x+lean,lane,1.38+bounce),'head':(x+lean*1.7,lane,1.98+bounce),'hair':(x+lean*1.7-.025,lane,2.16+bounce),'eyeL':(x+lean*1.7+.235,lane-.085,2.01+bounce),'eyeR':(x+lean*1.7+.235,lane+.085,2.01+bounce)}
  for n,p in positions.items():o=a['parts'][n];o.location=p;key(o,f,False)
  for side in [-1,1]:
   ff,fz=foot_local(dist,speed,side);ank=(x+ff,lane+side*.16,fz+.06);hip=(x,lane+side*.16,hipZ);kn=knee(hip,ank)
   for n,p,q in [('thigh',hip,kn),('shin',kn,ank)]:o=a['limbs'][(side,n)];aim(o,p,q);key(o,f)
   o=a['parts'][('foot',side)];o.location=(ank[0]+.075,ank[1],fz);key(o,f,False)
   sh=(x+lean,lane+side*.30,1.65+bounce)
   swing=math.sin(cycle+(0 if side==-1 else math.pi)) if speed else 0
   # Relaxed arms in walk, bent elbows in run. Inactive arms hold their pose.
   el=(sh[0]-.10+(.16 if run else .10)*swing,sh[1]+side*.025,sh[2]-(.25 if run else .28))
   hand=(el[0]+(.26 if run else .03)+(.12 if run else .12)*swing,el[1],el[2]-(.04 if run else .28))
   if 2<t<5 and i==0 and side==-1:
    q=smooth((t-2)/.6)*(1-smooth((t-4)/.7));hand=tuple(Vector(hand).lerp(Vector((x+.36,lane-.37,1.7)),q));el=tuple(Vector(el).lerp(Vector((x+.05,lane-.45,1.45)),q))
   for n,p,q in [('upper',sh,el),('fore',el,hand)]:o=a['limbs'][(side,n)];aim(o,p,q);key(o,f)
   o=a['parts'][('hand',side)];o.location=hand;key(o,f,False)
  if f%24==1: checks.append({'frame':f,'actor':a['name'],'x':x,'speed':speed})
# Rain: thin line geometry, repeated linear falling trajectories, no opaque blocks.
for j in range(115):
 x=random.uniform(-8,8);y=random.uniform(-2.7,3);z=random.uniform(.3,6)
 o=rod('Chuva • fio %03d'%j,(x,y,z),(x+.035,y,z+.28),.009,'water',fx)
 o.location.z=6+random.random();o.keyframe_insert('location',frame=1)
 o.location.z=-.25;o.keyframe_insert('location',frame=19+random.randint(0,7))
 for fc in o.animation_data.action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
  fc.modifiers.new('CYCLES')
# Light.
bpy.ops.object.light_add(type='AREA',location=(0,-4,9));o=bpy.context.object;o.name='Luz • céu';o.data.energy=1800;o.data.shape='DISK';o.data.size=12
bpy.ops.object.light_add(type='SUN',location=(0,0,8));o=bpy.context.object;o.rotation_euler=(.4,-.5,-.4);o.data.energy=1.4;o.data.angle=.2
# Shot-specific camera paths with real cuts, not a continuously spinning camera.
shots=[(0,4,'01 • Primeiras gotas'),(4,9,'02 • Apresenta o trajeto'),(9,14,'03 • Travelling caminhada'),(14,18,'04 • A dúvida'),(18,22,'05 • Olhar para o abrigo'),(22,29,'06 • Corrida lateral'),(29,35,'07 • Percurso visto de cima'),(35,41,'08 • Chegada ao abrigo'),(41,46,'09 • Caminhada continua'),(46,50,'10 • Detalhe dos passos'),(50,56,'11 • Mesmo ponto de partida'),(56,60,'12 • Duas velocidades')]
cameras=[]
for j,(start,end,name) in enumerate(shots):
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name=name;move_coll(cam,rig);cam.data.lens=45;cam.data.clip_end=180;cameras.append(cam)
 mark=s.timeline_markers.new(name,frame=round(start*24)+1);mark.camera=cam
 for f in range(round(start*24)+1,min(1440,round(end*24))+1):
  t=(f-1)/24;x0=route(t,0)[0];x1=route(t,1)[0];q=(t-start)/(end-start)
  if j==0:pos=(-7.6,-4,3.0);target=(-9.8,-.6,1.65);cam.data.lens=52
  elif j==1:pos=(1,-18,10);target=(0,0,1);cam.data.lens=32
  elif j==2:pos=(x0+3.5,-6,3.2);target=(x0+.6,0,1.15)
  elif j==3:pos=(-2.2,-3.2,2.5);target=(-5.3,-.5,1.8);cam.data.lens=58
  elif j==4:pos=(-7,-2,2.2);target=(8.8,0,1.6);cam.data.lens=35
  elif j==5:pos=(x0+3,-5.7,2.6);target=(x0+.6,-.6,1.15);cam.data.lens=42
  elif j==6:pos=(2,-5,20);target=(2,0,0);cam.data.lens=35
  elif j==7:pos=(13,-5,3.1);target=(9.2,-.5,1.4)
  elif j==8:pos=(x1+3,-5,2.5);target=(x1,.8,1.1)
  elif j==9:pos=(x1+1.4,-1.6,.65);target=(x1,.8,.45);cam.data.lens=48
  elif j==10:pos=(-5,-10,6);target=((x0+x1)/2,0,1);cam.data.lens=35
  else:pos=(4,-16,11);target=(0,0,1);cam.data.lens=35
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();key(cam,f)
s.camera=cameras[0]
# Actual Grease Pencil v3 Line Art. Contours follow current camera and animated geometry.
bpy.ops.object.grease_pencil_add(type='LINEART_SCENE');gp=bpy.context.object;gp.name='Grease Pencil • contorno desenhado';move_coll(gp,fx)
la=gp.modifiers[0];la.source_type='COLLECTION';la.source_collection=geo;la.thickness=18;la.use_crease=False;la.use_intersection=False;la.use_material=False;la.use_contour=True;la.stroke_depth_offset=.03
la.target_material.grease_pencil.color=(.035,.022,.055,1)
noise=gp.modifiers.new('Irregularidade discreta do lápis','GREASE_PENCIL_NOISE');noise.factor=.018;noise.factor_strength=.10;noise.factor_thickness=.12;noise.noise_scale=.4;noise.use_random=False
# Audio is a packed VSE sound strip, with a relative external backup.
seq=s.sequence_editor_create();strip=seq.sequences.new_sound('Narração • Puck • 60 segundos',str(BASE/'narracao-60s.wav'),channel=1,frame_start=1);strip.volume=1
effects=BASE/'efeitos-60s.wav'
if effects.exists(): seq.sequences.new_sound('Chuva e passos • Python',str(effects),channel=2,frame_start=1)
s.render.use_sequencer=False # render scene; mux audio for MP4 externally
bpy.ops.file.pack_all()
# Linear sampled curves prevent Bezier overshoot at elbows and planted feet.
for action in bpy.data.actions:
 for fc in action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
# Opening viewport is the camera view, not an empty default workspace.
s.frame_set(112)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
s['Leia-me']='Teste procedural 60s. 12 planos. Grease Pencil Line Art + Noise. Narração empacotada no Sequencer. 1920×1080 / 24fps. Script e README acompanham.'
s.render.filepath='//renders/frame-'
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'01 - Chuva - Grease Pencil.blend'),compress=True)
(OUT/'motion-checks.json').write_text(json.dumps(checks,indent=2))
# Quality check renders, full output settings remain 1080p in the saved .blend.
for f in ([] if os.environ.get('RAIN_SKIP_CHECK') else [75,235,570,750,910,1140,1340]):
 s.frame_set(f);s.render.resolution_percentage=50;s.render.filepath=str(OUT/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
print('BUILD_COMPLETE',flush=True)
