#!/usr/bin/env python3
"""Refine visible actors and presentation text in every frame, retaining timing.

Wait for the baseline reconstruction to finish before replacing its archives.
Use the same input and output parameters as the case-study reconstruction.
"""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import io,json,math,subprocess,time,zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import cv2,cairosvg,vtracer
from recreate import ROOT,WORK,SOURCE,FPS,STYLE,probe,run

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
FINE={**STYLE,'filter_speckle':0,'color_precision':8,'layer_difference':4,'corner_threshold':80,'path_precision':3}

def focus_regions(rgb):
 hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
 masks=[cv2.inRange(hsv,np.array([0,150,100]),np.array([19,255,255])),
        cv2.inRange(hsv,np.array([90,210,150]),np.array([108,255,255])),
        cv2.inRange(hsv,np.array([0,0,245]),np.array([179,25,255]))]
 found=[]
 for kind,mask in enumerate(masks):
  if kind!=2:mask=cv2.dilate(mask,np.ones((3,3),np.uint8))
  count,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8)
  candidates=[]
  for i in range(1,count):
   x,y,w,h,area=map(int,stats[i])
   if kind==2:
    valid=area>800 and w>=60 and h>=30 and w*h<640*360*.7
   else:
    valid=area>=30 and w<640*.6 and h<360*.95 and w*h<640*360*.35
    if kind==1:valid=valid and w*h<10000 and area/(w*h)<.65
   if valid:candidates.append((area,x,y,w,h))
  for area,x,y,w,h in sorted(candidates,reverse=True)[:5]:
   x0=max(0,x-4);y0=max(0,y-4);x1=min(640,x+w+4);y1=min(360,y+h+4)
   found.append([x0,y0,x1,y1])
 # Merge overlapping regions to avoid repeated tracing and conflicting overlays.
 changed=True
 while changed:
  changed=False;merged=[]
  for box in found:
   for i,other in enumerate(merged):
    if box[0]<=other[2] and box[2]>=other[0] and box[1]<=other[3] and box[3]>=other[1]:
     merged[i]=[min(box[0],other[0]),min(box[1],other[1]),max(box[2],other[2]),max(box[3],other[3])]
     changed=True;break
   else:merged.append(box)
  found=merged
 return found

def refine_part(spec):
 part,start,end=spec
 baseline_report=ROOT/'analysis'/f'part-{part:02d}.json'
 baseline_archive=ROOT/'vectors'/f'part-{part:02d}.zip'
 while not baseline_report.exists():time.sleep(5)
 folder=WORK/'refined'/f'part-{part:02d}';folder.mkdir(parents=True,exist_ok=True)
 result_path=folder/'report.json'
 if result_path.exists():return json.loads(result_path.read_text())
 report=json.loads(baseline_report.read_text());metrics=report['frames_mapping']
 output=folder/'video.mp4';archive=folder/'vectors.zip'
 encoder_log=(folder/'encoder.log').open('w')
 encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate',str(FPS),'-i','pipe:0','-c:v','libx264','-threads','1','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE,stderr=encoder_log)
 improved=0;begin=time.monotonic();baseline_mse=[];refined_mse=[]
 try:
  with zipfile.ZipFile(baseline_archive) as original,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
   for local,index in enumerate(range(start,end)):
    rgb=np.array(Image.open(WORK/'frames'/f'{index:06d}.png').convert('RGB'))
    svg=original.read(f'{index:06d}.svg')
    baseline_png=cairosvg.svg2png(bytestring=svg,output_width=1920,output_height=1080)
    base=np.array(Image.open(io.BytesIO(baseline_png)).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)).astype(float)
    old_mse=float(np.mean((rgb.astype(float)-base)**2));baseline_mse.append(old_mse)
    root=ET.fromstring(svg);regions=focus_regions(rgb)
    for number,(x0,y0,x1,y1) in enumerate(regions):
     crop=folder/'crop.png';vector=folder/'crop.svg'
     Image.fromarray(rgb[y0:y1,x0:x1]).save(crop)
     vtracer.convert_image_to_svg_py(str(crop),str(vector),**FINE)
     nested=ET.fromstring(vector.read_bytes())
     nested.set('x',str(x0));nested.set('y',str(y0));nested.set('width',str(x1-x0));nested.set('height',str(y1-y0));nested.set('viewBox',f'0 0 {x1-x0} {y1-y0}')
     root.append(nested)
    candidate=ET.tostring(root,encoding='utf-8')
    png=cairosvg.svg2png(bytestring=candidate,output_width=1920,output_height=1080)
    image=np.array(Image.open(io.BytesIO(png)).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)).astype(float)
    mse=float(np.mean((rgb.astype(float)-image)**2))
    applied=bool(regions and mse<old_mse*.995)
    if applied:
     svg=candidate;improved+=1
    else:
     png=baseline_png;image=base;mse=old_mse
    encoder.stdin.write(png);bundle.writestr(f'{index:06d}.svg',svg)
    metrics[local]['baseline_psnr_db']=metrics[local]['psnr_db']
    metrics[local]['baseline_mae']=metrics[local]['mae']
    metrics[local]['refinement']={'applied':applied,'candidate_regions':regions,'acceptance':'MSE improves by at least 0.5%; remaining frame retains baseline'}
    metrics[local]['mae']=round(float(np.mean(abs(rgb.astype(float)-image))),5)
    metrics[local]['psnr_db']=round(10*math.log10(255**2/max(mse,1e-10)),4)
    metrics[local]['svg_paths']=svg.count(b'<path')
    refined_mse.append(mse)
  encoder.stdin.close()
  if encoder.wait()!=0:raise RuntimeError((folder/'encoder.log').read_text())
 except BaseException:
  encoder.kill();encoder.wait();archive.unlink(missing_ok=True);raise
 finally:encoder_log.close()
 report['mean_mae']=round(float(np.mean([x['mae'] for x in metrics])),5)
 report['minimum_psnr_db']=min(x['psnr_db'] for x in metrics)
 report['refinement']={'method':'Source-derived foreground/text regions retraced at higher precision; accepted only with measured error reduction',
  'fine_settings':FINE,'improved_frames':improved,'baseline_mean_mse':float(np.mean(baseline_mse)),
  'refined_mean_mse':float(np.mean(refined_mse)),'elapsed_seconds':time.monotonic()-begin,
  'limits':'Color regions are heuristic, not semantic identities; no claim of exact pixel matching.'}
 result_path.write_text(json.dumps(report,separators=(',',':'))+'\n')
 return {'part':part,'frames':end-start,'improved_frames':improved,'baseline_mse':float(np.mean(baseline_mse)),'refined_mse':float(np.mean(refined_mse))}

def main():
 specs=[(i+1,start,min(start+240,4078)) for i,start in enumerate(range(0,4078,240))]
 results=[]
 with ProcessPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(refine_part,s) for s in specs]
  for future in as_completed(futures):
   result=future.result();results.append(result);print(json.dumps({'refined_part':result,'completed_parts':len(results),'total_parts':len(specs)}),flush=True)
 # Baseline rendering may still be finishing; do not replace files under its assembler.
 while not (ROOT/'analysis/reconstruction.json').exists():time.sleep(5)
 baseline=WORK/'baseline';baseline.mkdir(exist_ok=True)
 summary=[]
 for part,start,end in specs:
  folder=WORK/'refined'/f'part-{part:02d}'
  archive=ROOT/'vectors'/f'part-{part:02d}.zip'
  archive.replace(baseline/f'vectors-{part:02d}.zip')
  (folder/'vectors.zip').replace(archive)
  target=WORK/f'part-{part:02d}/video.mp4'
  target.replace(baseline/f'video-{part:02d}.mp4')
  (folder/'video.mp4').replace(target)
  report=json.loads((folder/'report.json').read_text())
  (ROOT/'analysis'/f'part-{part:02d}.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
  summary.append(report)
 output=ROOT.parents[1]/'video/teamwater-recriado-1080p.mp4'
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(WORK/'parts.ffconcat'),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart',str(output)])
 reconstruction=json.loads((ROOT/'analysis/reconstruction.json').read_text())
 reconstruction['refinement']={'applied':True,'method':'Higher-precision foreground/text vector reconstruction in every source frame, retained where measured error decreases',
  'improved_frames':sum(r['refinement']['improved_frames'] for r in summary),
  'baseline_mean_mse':float(np.mean([r['refinement']['baseline_mean_mse'] for r in summary])),
  'refined_mean_mse':float(np.mean([r['refinement']['refined_mean_mse'] for r in summary]))}
 reconstruction['mean_mae']=float(np.mean([r['mean_mae'] for r in summary]));reconstruction['minimum_psnr_db']=min(r['minimum_psnr_db'] for r in summary)
 (ROOT/'analysis/reconstruction.json').write_text(json.dumps(reconstruction,indent=2)+'\n')
 (ROOT/'analysis/refinement-complete.json').write_text(json.dumps(reconstruction['refinement'],indent=2)+'\n')
 print(json.dumps({'refinement_complete':reconstruction['refinement']}),flush=True)

if __name__=='__main__':main()
