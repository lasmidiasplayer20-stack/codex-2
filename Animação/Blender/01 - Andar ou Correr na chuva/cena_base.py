import bpy, math, random, os, json, sys
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('RAIN_RENDER_DIR',str(BASE/'verificacao-v2'))); OUT.mkdir(parents=True,exist_ok=True)
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
M={n:mat(n,c) for n,c in {'ink':(.035,.025,.065),'skin':(.91,.57,.34),'blue':(.10,.43,.69),'coral':(.92,.29,.19),'pants':(.10,.15,.23),'shoe':(.97,.87,.65),'road':(.36,.46,.52),'sidewalk':(.55,.62,.65),'teal':(.18,.44,.43),'cream':(.95,.84,.64),'roof':(.16,.25,.32),'water':(.20,.64,.78),'white':(.94,.94,.85),'yellow':(1,.73,.19)}.items()}
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
 for y in [1.7]:rod('Coluna',(x-1.5,y,.12),(x-1.5,y,3.4),.09,'roof')
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
