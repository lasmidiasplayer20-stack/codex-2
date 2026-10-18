#!/usr/bin/env python3
"""Trace every reference frame into editable vector paths and render at 1080p.

No previous project's character, style, rig, or scene is used. This is an
image-derived 2D vector reconstruction, not a hand-authored rig or exact recovery
of original animation files. Optical flow and camera estimates are observations.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import math
import os
import subprocess
import time
import zipfile

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import cairosvg
import cv2
import numpy as np
from PIL import Image
import vtracer

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'.work'
SOURCE=ROOT/'assets/reference.mp4'
FPS=Fraction(24000,1001)
cv2.setNumThreads(1)
STYLE={'colormode':'color','hierarchical':'stacked','mode':'spline',
       'filter_speckle':1,'color_precision':7,'layer_difference':8,
       'corner_threshold':60,'length_threshold':3.5,'max_iterations':10,
       'splice_threshold':45,'path_precision':2}

def run(args):
    subprocess.run(args,check=True)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def regions(rgb):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    masks={
      'orange':cv2.inRange(hsv,np.array([3,130,100]),np.array([27,255,255])),
      'cyan_blue':cv2.inRange(hsv,np.array([85,100,80]),np.array([120,255,255])),
      'neutral':cv2.inRange(hsv,np.array([0,0,45]),np.array([179,35,205]))}
    result={}
    for name,mask in masks.items():
      count,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8)
      found=[]
      for i in range(1,count):
        x,y,w,h,area=map(int,stats[i])
        if area>=16:found.append({'bbox':[x,y,w,h],'area':area,'centroid':centers[i].round(3).tolist()})
      result[name]=sorted(found,key=lambda x:-x['area'])
    return result

def motion(previous,current):
    # Flow estimated over every image pixel; exported as an 8-pixel control grid.
    flow=cv2.calcOpticalFlowFarneback(previous,current,None,.5,3,15,3,5,1.2,0)
    grid=flow[::8,::8].astype(np.float16)
    points=cv2.goodFeaturesToTrack(previous,maxCorners=160,qualityLevel=.02,minDistance=8)
    camera=None;inlier_count=0
    if points is not None:
      targets,status,_=cv2.calcOpticalFlowPyrLK(previous,current,points,None)
      valid=status[:,0]==1
      if valid.sum()>=6:
        transform,inliers=cv2.estimateAffinePartial2D(points[valid],targets[valid],method=cv2.RANSAC,ransacReprojThreshold=2)
        if transform is not None:
          camera=transform.round(6).tolist();inlier_count=int(inliers.sum())
    delta=float(np.mean(cv2.absdiff(previous,current)))
    histogram_a=cv2.calcHist([previous],[0],None,[32],[0,256])
    histogram_b=cv2.calcHist([current],[0],None,[32],[0,256])
    distance=float(cv2.compareHist(histogram_a,histogram_b,cv2.HISTCMP_BHATTACHARYYA))
    summary={'mean_pixel_delta':round(delta,4),'histogram_distance':round(distance,5),
      'cut_candidate':bool(delta>24 and distance>.18),
      'camera_affine_candidate':camera,'camera_inliers':inlier_count,
      'flow_median_xy':np.median(flow.reshape(-1,2),axis=0).round(4).tolist(),
      'flow_max_magnitude':round(float(np.linalg.norm(flow,axis=2).max()),4)}
    return grid,summary

def render_part(spec):
    part,start,end=spec
    folder=WORK/f'part-{part:02d}';folder.mkdir(parents=True,exist_ok=True)
    output=folder/'video.mp4'
    archive=ROOT/'vectors'/f'part-{part:02d}.zip'
    report_path=ROOT/'analysis'/f'part-{part:02d}.json'
    flow_path=ROOT/'analysis'/f'flow-{part:02d}.npz'
    if report_path.exists() and output.exists() and archive.exists() and flow_path.exists():
      return json.loads(report_path.read_text())
    begin=time.monotonic()
    args=['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate',str(FPS),'-i','pipe:0',
          '-c:v','libx264','-threads','1','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    error_log=(folder/'encoder.log').open('w')
    encoder=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=error_log)
    metrics=[];flows=[]
    previous=None
    if start:
      previous=cv2.imread(str(WORK/'frames'/f'{start-1:06d}.png'),cv2.IMREAD_GRAYSCALE)
    try:
      with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for index in range(start,end):
          source=WORK/'frames'/f'{index:06d}.png'
          rgb=np.array(Image.open(source).convert('RGB'))
          gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
          svg_path=folder/'frame.svg'
          vtracer.convert_image_to_svg_py(str(source),str(svg_path),**STYLE)
          svg=svg_path.read_bytes()
          assert b'<image' not in svg and b'base64' not in svg
          png=cairosvg.svg2png(bytestring=svg,output_width=1920,output_height=1080)
          encoder.stdin.write(png)
          reconstructed=np.array(Image.open(io.BytesIO(png)).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)).astype(np.float32)
          diff=rgb.astype(np.float32)-reconstructed
          mse=float(np.mean(diff**2))
          data={'frame':index,'time_seconds':round(float(index/FPS),6),
            'svg_paths':svg.count(b'<path'),'mae':round(float(np.mean(abs(diff))),5),
            'psnr_db':round(10*math.log10(255**2/max(mse,1e-10)),4),
            'regions':regions(rgb)}
          if previous is not None:
            grid,summary=motion(previous,gray);flows.append(grid);data['motion_from_previous']=summary
          else:flows.append(np.zeros((45,80,2),dtype=np.float16))
          previous=gray
          metrics.append(data)
          bundle.writestr(f'{index:06d}.svg',svg)
      encoder.stdin.close()
      if encoder.wait()!=0:raise RuntimeError((folder/'encoder.log').read_text())
    except BaseException:
      encoder.kill();encoder.wait()
      archive.unlink(missing_ok=True)
      raise
    finally:error_log.close()
    np.savez_compressed(flow_path,flow=np.stack(flows),frame_indices=np.arange(start,end),grid_step=np.array(8),units=np.array('source pixels per frame'))
    report={'part':part,'start_frame':start,'end_frame_exclusive':end,'frames':end-start,
      'start_seconds':float(start/FPS),'end_seconds':float(end/FPS),
      'elapsed_seconds':round(time.monotonic()-begin,3),'vector_archive':str(archive.relative_to(ROOT)),
      'flow_grid':'45x80 vectors sampled from full-resolution optical flow; source pixel coordinates',
      'camera':'RANSAC affine candidates, not authoritative camera reconstruction',
      'region_identity':'Color components are candidates, not persistent character identities or joint labels',
      'mean_mae':round(float(np.mean([x['mae'] for x in metrics])),5),
      'minimum_psnr_db':min(x['psnr_db'] for x in metrics),'frames_mapping':metrics}
    report_path.write_text(json.dumps(report,separators=(',',':'))+'\n')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--part-frames',type=int,default=240)
    args=parser.parse_args()
    if args.workers<1 or args.part_frames<1:parser.error('Positive worker and part-frame counts required')
    for p in [WORK/'frames',ROOT/'analysis',ROOT/'vectors']:p.mkdir(parents=True,exist_ok=True)
    info=probe(SOURCE);v=next(s for s in info['streams'] if s['codec_type']=='video')
    count=int(v['nb_frames']);assert (v['width'],v['height'],Fraction(v['r_frame_rate']))==(640,360,FPS)
    provenance={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'probe':info,
      'method':'Every frame independently reconstructed as filled SVG paths; original AAC retained',
      'output_size':[1920,1080],'source_detail_limit':[640,360],'fps':str(FPS),'frames':count,
      'trace_settings':STYLE,'not_used':['previous 3D visual reference','source raster textures in SVG','hand-authored replacement story'],
      'limits':['Vector contours approximate raster artwork; not pixel-identical.','Original hidden rig and occluded motion cannot be recovered from this file.','Flow and camera transforms are estimates, not exact motion capture.']}
    (ROOT/'analysis/reference.json').write_text(json.dumps(provenance,indent=2)+'\n')
    if len(list((WORK/'frames').glob('*.png')))!=count:
      run(['ffmpeg','-v','error','-i',str(SOURCE),'-map','0:v:0','-fps_mode','passthrough','-start_number','0',str(WORK/'frames/%06d.png')])
    assert len(list((WORK/'frames').glob('*.png')))==count
    specs=[(i+1,start,min(start+args.part_frames,count)) for i,start in enumerate(range(0,count,args.part_frames))]
    (ROOT/'analysis/parts.json').write_text(json.dumps([{'part':p,'start_frame':s,'end_frame_exclusive':e} for p,s,e in specs],indent=2)+'\n')
    reports=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
      futures={pool.submit(render_part,s):s for s in specs}
      for future in as_completed(futures):
        report=future.result();reports.append(report)
        print(json.dumps({'part_complete':report['part'],'completed_parts':len(reports),'total_parts':len(specs),
          'frames_completed':sum(x['frames'] for x in reports),'total_frames':count,'mean_mae':report['mean_mae']}),flush=True)
    reports.sort(key=lambda x:x['part'])
    assert sum(x['frames'] for x in reports)==count
    manifest=WORK/'parts.ffconcat'
    lines=['ffconcat version 1.0']
    for report in reports:
      video=WORK/f"part-{report['part']:02d}/video.mp4"
      lines.extend([f"file '{video}'",f"duration {float(Fraction(report['frames'],1)/FPS):.12f}"])
    manifest.write_text('\n'.join(lines)+'\n')
    output=ROOT.parents[1]/'video/teamwater-recriado-1080p.mp4';output.parent.mkdir(parents=True,exist_ok=True)
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(manifest),'-i',str(SOURCE),
      '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart',str(output)])
    summary={'status':'rendered','frames':count,'mapped_frame_transitions':count-1,'parts':len(reports),
      'output':str(output.relative_to(ROOT.parents[1])),'mean_mae':float(np.mean([r['mean_mae'] for r in reports])),
      'minimum_psnr_db':min(r['minimum_psnr_db'] for r in reports),
      'full_frame_coverage':True,'editable_vector_frames':count,'audio':'Original AAC stream copied once',
      'exact_pixel_match':False,'motion_method':'Frame-aligned vector retracing; optical flow/camera estimates provided for analysis, not used to invent movements'}
    (ROOT/'analysis/reconstruction.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
