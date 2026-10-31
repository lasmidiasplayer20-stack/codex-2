from pathlib import Path
import sys,json,subprocess
P=Path(__file__).resolve().parents[1];A=P.parents[1];recipe=json.loads((P/'story/cover.json').read_text());target=A/'youtube'/recipe['youtube_folder'];native=P/'build/cover-native.png';native.parent.mkdir(exist_ok=True)
subprocess.run(['node',str(A/'skill/scripts/render-cover.mjs'),'--project',str(P),'--scale','1','--at',str(recipe['requested_seconds']),'--out',str(native)],check=True)
subprocess.run([sys.executable,str(A/'skill/scripts/cover_poster.py'),'--source',str(native),'--out',str(target/'capa.jpg'),'--text',recipe['headline'],'--theme',str(recipe['theme'])],check=True)
