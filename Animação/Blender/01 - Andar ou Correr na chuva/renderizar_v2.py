"""Native 1080p/24 fps render. Run inside Blender with --python."""
from pathlib import Path
import sys,time,argparse
import bpy

def configurar(s):
 s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='FXAA'
 s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24
 sh=s.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_specular_highlight=False;sh.show_object_outline=False;sh.background_type='WORLD'
 s.render.use_sequencer=False

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=1);ap.add_argument('--end',type=int,default=1440);ap.add_argument('--out',default=str(Path(__file__).parent/'renders-v2'));a=ap.parse_args(args)
 s=bpy.context.scene;configurar(s);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
 start=time.time()
 for f in range(a.start,a.end+1):
  s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.jpg');bpy.ops.render.render(write_still=True)
  if (f-a.start)%24==0:print('PROGRESS',f,round(time.time()-start,2),flush=True)
 print('DONE',a.start,a.end,round(time.time()-start,2),flush=True)
