from pathlib import Path
import subprocess,concurrent.futures,time,json
ROOT=Path(__file__).resolve().parent.parent;OUT=Path('/workspace/rain-renders-r2');OUT.mkdir(exist_ok=True)
def render(i):
 path=OUT/f'part-{i+1:02d}.mp4';log=OUT/f'part-{i+1:02d}.log'
 if path.exists() and path.with_suffix('.mp4.json').exists():return i
 with log.open('w') as f:
  p=subprocess.run(['node','scripts/render.mjs','--start',str(i*60),'--duration','60','--output',str(path)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError('Render failed, inspect '+str(log))
 print('Completed minute',i+1,flush=True);return i
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,range(8)))
print('All 8 minutes rendered',flush=True)
