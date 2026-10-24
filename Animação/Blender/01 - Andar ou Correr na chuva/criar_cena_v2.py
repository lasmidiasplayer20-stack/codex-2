"""Blender 4.3+. All geometry, drawn strokes, articulation and staging by code."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cena_base import *
from collections import defaultdict
from mathutils import Euler
ANIM=defaultdict(lambda:defaultdict(list))
def record(o,f,rotation=True,scale=True):
 paths=['location']+(['rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler'] if rotation else [])+(['scale'] if scale else [])
 for path in paths:ANIM[o][path].append((f,tuple(getattr(o,path))))
def bake():
 for o,paths in ANIM.items():
  action=bpy.data.actions.new(o.name+' • poses');o.animation_data_create();o.animation_data.action=action
  for path,rows in paths.items():
   for idx in range(len(rows[0][1])):
    fc=action.fcurves.new(path,index=idx);fc.keyframe_points.add(len(rows));fc.keyframe_points.foreach_set('co',[v for f,p in rows for v in (f,p[idx])])
    for kp in fc.keyframe_points:kp.interpolation='CONSTANT' if path.startswith('hide_') else 'LINEAR'
    fc.update()
def empty(name):
 o=bpy.data.objects.new(name,None);rig.objects.link(o);return o
def smooth(q):q=max(0,min(1,q));return q*q*(3-2*q)
def envelope(t,a,b,c,d):return smooth((t-a)/(b-a))*(1-smooth((t-c)/(d-c)))
def travel(t,start,D,v,r=.7):
 """Smooth acceleration and braking; travelled distance drives planted feet."""
 dur=D/v+r;u=t-start
 if u<=0:return 0,0
 if u>=dur:return D,0
 if u<r:
  q=u/r;return v*r*(q**3-.5*q**4),v*smooth(q)
 if u>dur-r:
  q=(dur-u)/r;return D-v*r*(q**3-.5*q**4),v*smooth(q)
 return v*(u-r/2),v

def route(t,i):
 if t<20:
  d,v=travel(t,5.0,4.4,.75);return -10+d,v,d,False
 if t<50:
  d,v=travel(t,21 if i==0 else 21.5,14.85,1.8 if i==0 else .58)
  return -5.6+d,v,4.4+d,i==0
 d,v=travel(t,50.2,17.8,2.0 if i==0 else .85)
 return -9+d,v,d,i==0

MET={'max_limb_length_error':0.,'unreachable_targets':0,'min_knee_degrees':180.,'max_knee_degrees':0.,'min_elbow_degrees':180.,'max_elbow_degrees':0.}
def joint(root,target,L1,L2,pole,kind):
 root,target=Vector(root),Vector(target);delta=target-root;dist=delta.length
 if dist>L1+L2-.0001:MET['unreachable_targets']+=1
 d=max(abs(L1-L2)+.0001,min(dist,L1+L2-.0001));axis=delta.normalized()
 end=root+axis*d;pole=Vector(pole);perp=pole-axis*pole.dot(axis)
 if perp.length<.001:perp=Vector((0,1,0))
 perp.normalize();a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));mid=root+axis*a+perp*h
 error=max(abs((mid-root).length-L1),abs((end-mid).length-L2));MET['max_limb_length_error']=max(MET['max_limb_length_error'],error)
 angle=math.degrees(math.acos(max(-1,min(1,(L1*L1+L2*L2-d*d)/(2*L1*L2)))))
 MET['min_'+kind+'_degrees']=min(MET['min_'+kind+'_degrees'],angle);MET['max_'+kind+'_degrees']=max(MET['max_'+kind+'_degrees'],angle)
 return mid,end

def drawn(name,strokes,parent=None,width=.014,color=(.045,.025,.07,1)):
 bpy.ops.object.grease_pencil_add(type='EMPTY');o=bpy.context.object;o.name=name;move_coll(o,fx);o.show_in_front=False;o.data.stroke_depth_order='3D'
 if len(o.data.layers):
  for layer in list(o.data.layers):o.data.layers.remove(layer)
 mat=bpy.data.materials.new(name+' • tinta');bpy.data.materials.create_gpencil_data(mat);mat.grease_pencil.color=color;mat.grease_pencil.show_fill=False
 o.data.materials.clear();o.data.materials.append(mat)
 layer=o.data.layers.new('Traços calculados ponto a ponto',set_active=True);drawing=layer.frames.new(1).drawing;drawing.add_strokes([len(points) for points in strokes])
 for stroke,coords in zip(drawing.strokes,strokes):
  stroke.material_index=0
  for j,(point,co) in enumerate(zip(stroke.points,coords)):
   if 'rosto desenhado' in name:
    _,y,z=co
    if z>.2: x=.235*math.sqrt(max(.01,1-(y/.215)**2-((z-.18)/.13)**2))+.008
    else:x=.235*math.sqrt(max(.01,1-(y/.205)**2-(z/.265)**2))+.008
    co=(x,y,z)
   elif 'costura e hachuras' in name:
    _,y,z=co;co=(.215*math.sqrt(max(.01,1-(y/.175)**2-(z/.52)**2))+.008,y,z)
   point.position=co;point.radius=width*(.8+.18*math.sin(j*1.7));point.opacity=1
 if parent:o.parent=parent
 return o

def child_ball(name,loc,scale,material,parent):
 o=ball(name,loc,scale,material);o.parent=parent;return o
actors=[]
for name,color,lane in [('Lia','coral',-.65),('Caio','blue',.65)]:
 a={'name':name,'lane':lane,'parts':{},'limbs':{},'feet':{},'hands':{},'joints':{},'eyes':[]}
 a['head']=empty(name+' • controle cabeça');a['body']=empty(name+' • controle tronco')
 child_ball(name+' • tronco esguio',(0,0,0),(.215,.175,.52),color,a['body'])
 a['pelvis']=ball(name+' • quadril',(0,0,0),(.205,.17,.14),'pants')
 child_ball(name+' • cabeça',(0,0,0),(.235,.205,.265),'skin',a['head'])
 child_ball(name+' • cabelo',(-.025,0,.18),(.235,.215,.13),'ink',a['head'])
 for side in [-1,1]:
  child_ball(name+' • orelha',(-.015,side*.205,-.01),(.06,.045,.085),'skin',a['head'])
  white=child_ball(name+' • olho branco',(.209,side*.077,.035),(.039,.049,.064),'white',a['head'])
  pupil=child_ball(name+' • pupila',(.247,side*.077,.035),(.015,.024,.033),'ink',a['head']);a['eyes']+= [white,pupil]
 # Actual Grease Pencil eyebrows, smile and hair marks, not textures.
 a['face']=drawn(name+' • rosto desenhado',[
  [(.221,-.132,.125),(.24,-.09,.142),(.232,-.045,.132)],
  [(.232,.045,.132),(.24,.09,.142),(.221,.132,.125)],
  [(.214,-.068,-.095),(.233,-.035,-.115),(.239,0,-.12),(.233,.035,-.115),(.214,.068,-.095)],
  [(.12,-.15,.23),(.16,-.08,.255),(.10,-.02,.267)]],a['head'],.010)
 a['seams']=drawn(name+' • costura e hachuras',[
  [(.217,0,.39),(.225,.007,.15),(.225,.002,-.08),(.214,0,-.36)],
  [(.18,-.10,-.25),(.20,-.07,-.31)],[ (.18,-.1,-.33),(.196,-.065,-.39)],
  [(.18,.1,-.25),(.20,.07,-.31)]],a['body'],.008)
 for side in [-1,1]:
  for n,m,r in [('thigh','pants',.078),('shin','pants',.067),('upper',color,.063),('fore','skin',.051)]:a['limbs'][side,n]=rod(name+f' • {side} {n}',(0,0,0),(0,0,1),r,m)
  for n,m,r in [('knee','pants',.078),('elbow',color,.063)]:a['joints'][side,n]=ball(name+f' • {side} {n}',(0,0,0),(r,r,r),m)
  a['feet'][side]=ball(name+f' • {side} sapato',(0,0,0),(.205,.095,.085),'shoe')
  a['hands'][side]=ball(name+f' • {side} mão',(0,0,0),(.065,.058,.078),'skin')
 actors.append(a)

def footpose(dist,run,side):
 stride=1.42 if run else .90;stance=.44 if run else .62;p=(dist/stride+(0 if side==-1 else .5))%1
 if p<stance:return stride*(stance/2-p),.085,0
 u=(p-stance)/(1-stance)
 return stride*stance*(-.5+smooth(u)),.085+(.34 if run else .19)*math.sin(math.pi*u),-.20*math.sin(math.pi*u)

def gesture(hand,shoulder,target,q):
 a=hand-shoulder;b=Vector(target)-shoulder
 direction=a.normalized().slerp(b.normalized(),q)
 return shoulder+direction*(a.length*(1-q)+b.length*q)

def pose(f):
 t=(f-1)/24
 for i,a in enumerate(actors):
  x,v,dist,running=route(t,i);run=running and v>.2;moving=min(1,v/.3);lane=a['lane']
  # Responsive but bounded body acting. Spine leans as a unit, head turns independently.
  anticipation=envelope(t,19.2,20.2,20.6,21.4) if i==0 else 0
  runmix=min(1,v/1.2) if running else 0
  crouch=anticipation*.13;hipz=1.36-(.025+.03*runmix)*moving-.013*abs(math.sin(dist*math.tau/(1.42 if run else .9)))*moving-crouch
  dz=hipz-1.36;lean=.13*runmix+anticipation*.09
  breathe=.005*math.sin(t*2.5+i)
  body=a['body'];body.location=(x+lean,lane,1.88+dz+breathe);body.rotation_euler=(.015*math.sin(dist*5)*moving,.12*runmix,.045*math.sin(dist*5)*moving);record(body,f)
  head=a['head'];head.location=(x+lean*1.6,lane,2.66+dz+breathe)
  look=envelope(t,13,13.6,16.5,17.2)*( .7 if i==0 else -.65)
  look+=envelope(t,23.1,23.4,23.9,24.5)*(.7 if i==0 else -.6)
  look+=envelope(t,43.8,44.5,47.0,48)*(.6 if i==0 else -.6)
  head.rotation_euler=(.035*math.sin(t*1.1+i),.08*runmix-.18*envelope(t,2.2,2.8,3.2,4),look);record(head,f)
  a['pelvis'].location=(x,lane,hipz);record(a['pelvis'],f,False)
  blink=1-.94*max(envelope(t,7.1+i*.3,7.16+i*.3,7.23+i*.3,7.3+i*.3),envelope(t,16.4,16.46,16.53,16.6),envelope(t,35.1,35.16,35.23,35.3))
  for eye in a['eyes']:
   if 'branco' in eye.name:eye.scale.z=.064*blink
   else:eye.scale.z=.033*blink
   record(eye,f,False)
  for side in [-1,1]:
   ff,fz,pitch=footpose(dist,running,side)
   ff*=moving;fz=.085+(fz-.085)*moving
   foot=a['feet'][side];foot.location=(x+ff+.055,lane+side*.145,fz);foot.rotation_euler=(0,pitch*moving,0);record(foot,f)
   hip=(x,lane+side*.145,hipz);ankle=(x+ff,lane+side*.145,fz+.065)
   kn,end=joint(hip,ankle,.61,.62,(1,0,0),'knee')
   for n,p,q in [('thigh',hip,kn),('shin',kn,end)]:o=a['limbs'][side,n];aim(o,p,q);record(o,f)
   o=a['joints'][side,'knee'];o.location=kn;record(o,f,False)
   shoulder=Vector((x+lean,lane+side*.245,2.18+dz));phase=dist*math.tau/(1.42 if run else .9)+(0 if side==-1 else math.pi)
   walk_hand=Vector((-.14*math.cos(phase)*moving,side*.015,-.76));run_hand=Vector((.20-.22*math.cos(phase),side*.015,-.47))
   hand=shoulder+walk_hand.lerp(run_hand,runmix)
   # Prepared gestures blend to a meaningful target, then recover to the rest pose.
   if i==0 and side==-1:
    q=envelope(t,.7,1.5,2.5,3.4);hand=gesture(hand,shoulder,shoulder+Vector((.42,-.13,-.10)),q)
    q=envelope(t,15.8,16.6,17.6,18.4);hand=gesture(hand,shoulder,shoulder+Vector((.67,-.05,-.10)),q)
   if i==1 and side==-1:
    q=envelope(t,22.9,23.2,23.7,24.5);hand=gesture(hand,shoulder,shoulder+Vector((.25,-.03,.37)),q)
   if (i==0 and side==1) or (i==1 and side==-1):
    q=envelope(t,46.9,47.5,47.9,48.5)
    # A short greeting; both wrists meet the same world-space point.
    hand=gesture(hand,shoulder,Vector((9.48,0,2.02)),q)
   el,end=joint(shoulder,hand,.41,.39,(-1,side*.45,-.15),'elbow')
   for n,p,q in [('upper',shoulder,el),('fore',el,end)]:o=a['limbs'][side,n];aim(o,p,q);record(o,f)
   o=a['joints'][side,'elbow'];o.location=el;record(o,f,False)
   o=a['hands'][side];o.location=end;record(o,f,False)
for f in range(1,1441):pose(f)
print('POSES',json.dumps(MET),flush=True)
assert MET['unreachable_targets']==0, 'Alvo fora do alcance anatômico'
assert MET['max_limb_length_error']<.00001
# Hand-drawn impact fans, ripples and speed accents. These are actual GP strokes.
for k in range(9):
 theta=.3+k*.24
 points=[(0,0,0),(-.45, .2+k*.025,.3+k*.025),(-.95,.45+k*.04,.25),(-1.4,.6+k*.055,0)]
 o=drawn('Respingo • arco %02d'%k,[points],width=.012,color=(.13,.55,.7,1));o.location=(-2.7,-.6,.04)
 for f,sc in [(1,.001),(544,.001),(551,1),(561,1.8),(571,.001),(1440,.001)]:o.scale=(sc,sc,sc);record(o,f,False)
for px,py in [(-3,-.6),(2,.9),(6,-1)]:
 points=[(math.cos(k*math.tau/32),math.sin(k*math.tau/32)*.48,0) for k in range(33)]
 o=drawn('Ondulação desenhada',[points],width=.009,color=(.30,.69,.77,1));o.location=(px,py,.045)
 for f in range(1,1441,4):
  u=((f/24+px*.3)%1.7)/1.7;o.scale=(.15+u*.6,.15+u*.6,1);record(o,f,False)
# Fine rain strands, random phases. No big opaque rain slabs.
for j in range(95):
 x=random.uniform(-8,8);y=random.uniform(-2.7,3);z=random.uniform(.3,6)
 o=rod('Chuva • fio %03d'%j,(x,y,z),(x+.035,y,z+.24),.006,'water',fx)
 # Offset the repeat phase independently for every drop.
 period=random.randint(16,24);phase=random.randint(0,period-1)
 for f,zv in [(1-phase,6.4),(1-phase+period,-.2)]:o.location.z=zv;record(o,f,False)
# Camera grammar borrows subject/reaction/detail cuts, not another film's character designs.
shots=[(0,3.6,'01 • Gota e mão'),(3.6,6,'02 • O colega percebe'),(6,10,'03 • Saída do abrigo'),(10,13,'04 • Pés no caminho'),(13,16,'05 • Troca de olhares'),(16,19,'06 • O destino'),(19,22,'07 • Preparação'),(22,23.2,'08 • Travelling corrida'),(23.2,25.4,'09 • Respingo e reação'),(25.4,30.2,'10 • Corrida por trás'),(30.2,33.5,'11 • Chegada'),(33.5,38,'12 • Mesmo trajeto'),(38,42,'13 • Caminhada avança'),(42,46.8,'14 • Abrigo à vista'),(46.8,50,'15 • Encontro'),(50,55,'16 • Comparação'),(55,60,'17 • Duas velocidades')]
shotcams=[]
for j,(start,end,name) in enumerate(shots):
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name=name;move_coll(cam,rig);cam.data.lens=44;cam.data.clip_end=200;shotcams.append(cam)
 marker=s.timeline_markers.new(name,frame=round(start*24)+1);marker.camera=cam
 if j==0:s.camera=cam
 for f in range(round(start*24)+1,min(1440,round(end*24))+1):
  t=(f-1)/24;x=route(t,0)[0];b=route(t,1)[0];u=(t-start)/(end-start)
  if j==0:pos=(-7.0,-4.3,3.5);target=(-9.8,-.55,2.15);cam.data.lens=42
  elif j==1:pos=(-7.5,-3,3.2);target=(-9.8,.6,2.3);cam.data.lens=55
  elif j==2:pos=(-3,-11,6);target=(-7.8,0,1.5);cam.data.lens=38
  elif j==3:pos=(x+1.3,-2.5,.85);target=(x,0,.55);cam.data.lens=45
  elif j==4:pos=(-2.4,-4,3.4);target=(-5.5,0,2.3);cam.data.lens=50
  elif j==5:pos=(-7,-1.2,2.7);target=(9,0,2);cam.data.lens=28
  elif j==6:pos=(-1.8,-5.2,2.7);target=(-5.3,-.4,1.6);cam.data.lens=40
  elif j==7:pos=(x+3.5,-6,3.0);target=(x+.3,-.45,1.45);cam.data.lens=42
  elif j==8:pos=(b+3,-4.5,3.4);target=(b,.5,1.9);cam.data.lens=45
  elif j==9:
   angle=-2.0+.5*u;pos=(x+5*math.cos(angle),5*math.sin(angle),3.8);target=(x+.5,-.6,1.6);cam.data.lens=38
  elif j==10:pos=(13,-6,3.5);target=(9,-.4,1.6);cam.data.lens=45
  elif j==11:pos=(2,-9,15);target=(2,0,.7);cam.data.lens=34
  elif j==12:pos=(b+3.8,-6.8,3.4);target=(b+.3,.5,1.5);cam.data.lens=46
  elif j==13:pos=(12,-8,4);target=(b+.7,.2,1.55);cam.data.lens=40
  elif j==14:pos=(12.5,-4.6,3.4);target=(9.3,0,2.2);cam.data.lens=42
  elif j==15:pos=(-2,-12,6);target=((x+b)/2,0,1.4);cam.data.lens=35
  else:pos=(4,-17,10);target=(0,0,1.3);cam.data.lens=34
  cam.location=Vector(pos).lerp(Vector(target),.025*u);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();record(cam,f)
# Cull facial/cloth strokes on back views. Workbench GP strokes otherwise show through meshes.
for f in range(1,1441):
 t=(f-1)/24;j=max(j for j,(start,end,_) in enumerate(shots) if round(start*24)+1<=f)
 cam=shotcams[j];camera=Vector(ANIM[cam]['location'][f-(round(shots[j][0]*24)+1)][1])
 for a in actors:
  for obj,ctrl in [(a['face'],a['head']),(a['seams'],a['body'])]:
   angles=ANIM[ctrl]['rotation_euler'][f-1][1];loc=Vector(ANIM[ctrl]['location'][f-1][1])
   normal=Euler(angles).to_matrix()@Vector((1,0,0));visible=normal.dot((camera-loc).normalized())>.15
   ANIM[obj]['hide_render'].append((f,(not visible,)));ANIM[obj]['hide_viewport'].append((f,(not visible,)))

# Contours are derived from the 3D meshes; face and cloth marks above are drawn explicitly.
bpy.ops.object.grease_pencil_add(type='LINEART_SCENE');gp=bpy.context.object;gp.name='Grease Pencil • contornos vivos';move_coll(gp,fx);gp.show_in_front=False;gp.data.stroke_depth_order='3D'
la=gp.modifiers[0];la.source_type='COLLECTION';la.source_collection=geo;la.thickness=12;la.use_crease=False;la.use_intersection=False;la.use_material=False;la.stroke_depth_offset=.025;la.target_material.grease_pencil.color=(.04,.022,.065,1)
noise=gp.modifiers.new('Variação sutil do lápis','GREASE_PENCIL_NOISE');noise.factor=.012;noise.factor_thickness=.12;noise.use_random=False
bpy.ops.object.light_add(type='AREA',location=(0,-4,9));bpy.context.object.data.energy=1700;bpy.context.object.data.size=12
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.5,-.4);bpy.context.object.data.energy=1.3
bake()
for o in fx.objects:
 if o.name.startswith('Chuva •'):
  for fc in o.animation_data.action.fcurves:fc.modifiers.new('CYCLES')
seq=s.sequence_editor_create();seq.sequences.new_sound('Narração • 60s',str(BASE/'narracao-60s.wav'),channel=1,frame_start=1)
seq.sequences.new_sound('Foley procedural • 60s',str(BASE/'efeitos-v2.wav'),channel=2,frame_start=1)
s.render.use_sequencer=False;bpy.ops.file.pack_all();s.frame_set(190)
s['Direção']='Personagens alongados, IK analítica de comprimentos fixos, atuação, traços GP originais, 17 câmeras. Tudo por código.'
from renderizar_v2 import configurar
configurar(s)
s.render.filepath='//renders-v2/frame-'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.shading.show_shadows=True;area.spaces.active.shading.show_object_outline=False
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'02 - Chuva - Atuacao e traco.blend'),compress=True)
(OUT/'articulacoes.json').write_text(json.dumps(MET,indent=2))
(OUT/'planos.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2))
print('BUILD_COMPLETE',flush=True)
