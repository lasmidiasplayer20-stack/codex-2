from pathlib import Path
import argparse,json,subprocess
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
p=argparse.ArgumentParser(description='Episode12 stationary-shot rain pixel direction audit; adjust ROI/timing for other projects.')
p.add_argument('--video',type=Path,required=True);p.add_argument('--start',type=float,default=5);p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();W=args.work;W.mkdir(parents=True,exist_ok=True)
def measure(video,start,label):
 d=W/label;d.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(video),'-frames:v','6','-vsync','0',str(d/'%02d.png')],check=True)
 arr=np.stack([np.asarray(Image.open(p).convert('RGB'))[650:1500,180:800].astype(np.int16)for p in sorted(d.glob('*.png'))[:6]])
 masks=(arr[:,:,:,1]>140)&(arr[:,:,:,2]>155)&(arr[:,:,:,0]<155)&(arr[:,:,:,2]-arr[:,:,:,0]>30)&(arr[:,:,:,1]-arr[:,:,:,0]>20)
 static=np.sum(masks,axis=0)>=5;masks&=~static
 scores=np.zeros((201,21))
 for a,b in zip(masks[:-1],masks[1:]):
  corr=fftconvolve(b.astype(float),a[::-1,::-1].astype(float),mode='full');cy,cx=np.array(a.shape)-1;scores+=corr[cy-100:cy+101,cx-10:cx+11]
 scores[95:106,:]=0;iy,ix=np.unravel_index(np.argmax(scores),scores.shape);dy=int(iy-100);dx=int(ix-10)
 return {'best_vertical_pixel_shift':dy,'best_horizontal_pixel_shift':dx,'peak_match_score':float(scores[iy,ix]),'downward_best_score':float(scores[106:,:].max()),'upward_best_score':float(scores[:95,:].max()),'dynamic_rain_mask_pixels':int(masks.sum()),'direction':'down'if dy>0 else'up','note':'Pixel y increases down. Cyan rain mask correlation across5 consecutive frame pairs; static background removed.'}

result=measure(args.video,args.start,'frames');result['seconds']=[args.start,args.start+5/24];result['scope']='Episode12 stationary rain shot only; mask/ROI not a general camera-motion detector.';args.out.write_text(json.dumps(result,indent=2));print(json.dumps(result));assert result['best_vertical_pixel_shift']>0 and result['downward_best_score']>result['upward_best_score'],'Rain pixels do not predominantly move down'
