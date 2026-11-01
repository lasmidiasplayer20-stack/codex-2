from pathlib import Path
import argparse,subprocess,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1];a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);W=a.parse_args().work;W.mkdir(exist_ok=True,parents=True);out=R/'youtube/38 - A janela do pachinko/capa.jpg';native=W/'cover-native.png'
subprocess.run(['node',str(R/'skill/scripts/render-original-cover.mjs'),'--project',str(P),'--at','63','--scale','1','--out',str(native)],check=True)
subprocess.run([str(R/'.venv/bin/python'),str(R/'skill/scripts/cover_poster.py'),'--source',str(native),'--out',str(out),'--text','POR QUE OUTRA JANELA?','--theme','38'],check=True)
(P/'qa/cover-validation.json').write_text(json.dumps({'width':1080,'height':1920,'source':'Dedicated procedural cover composition, original rounded cast','title':'POR QUE OUTRA JANELA?','font':'Anton OFL bundled','image_api_used':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size},indent=2))
