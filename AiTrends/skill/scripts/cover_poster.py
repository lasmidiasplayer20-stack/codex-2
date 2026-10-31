"""Typography for original code-rendered covers. Native frame + own branding, no image API."""
from pathlib import Path
import argparse
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
A=argparse.ArgumentParser();A.add_argument('--source',type=Path,required=True);A.add_argument('--out',type=Path,required=True);A.add_argument('--text',required=True);A.add_argument('--theme',type=int,required=True);a=A.parse_args();im=Image.open(a.source).convert('RGB');assert im.size==(1080,1920)
im=ImageEnhance.Color(im).enhance(1.08);im=ImageEnhance.Contrast(im).enhance(1.06);shade=Image.new('RGBA',im.size);d=ImageDraw.Draw(shade)
for y in range(540):d.line((0,y,1080,y),fill=(3,7,24,int(150*max(0,1-y/540))))
im=Image.alpha_composite(im.convert('RGBA'),shade);d=ImageDraw.Draw(im);root=Path(__file__).resolve().parents[2];fontpath=root/'2d-stick-animator/kit/fonts/Anton-Regular.ttf';mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf';small='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';size=154;font=ImageFont.truetype(str(fontpath),size);lines=[];line=''
for word in a.text.split():
 trial=(line+' '+word).strip()
 if d.textlength(trial,font=font)>970 and line:lines.append(line);line=word
 else:line=trial
lines.append(line)
if len(lines)>2:
 size=106;font=ImageFont.truetype(str(fontpath),size)
y=90 if len(lines)>1 else 120
for i,line in enumerate(lines):
 if len(lines)==1 and ' 'in line:
  white,yellow=line.rsplit(' ',1);white+=' ';w1=d.textlength(white,font=font);w2=d.textlength(yellow,font=font);x=(1080-w1-w2)/2;d.text((x,y),white,font=font,fill='white',stroke_width=11,stroke_fill='#02030b',anchor='lt');d.text((x+w1,y),yellow,font=font,fill='#ffed32',stroke_width=11,stroke_fill='#02030b',anchor='lt')
 else:
  width=d.textlength(line,font=font);d.text(((1080-width)/2,y+i*(size+20)),line,font=font,fill='white'if i==0 else'#ffed32',stroke_width=11,stroke_fill='#02030b',anchor='lt')
if a.theme in [3,8]:
 accent='#ff426f'if a.theme==3 else'#4be7ff';box=(700,375,1045,488);glow=Image.new('RGBA',im.size);g=ImageDraw.Draw(glow);g.rounded_rectangle(box,15,outline=accent,width=13);glow=glow.filter(ImageFilter.GaussianBlur(16));im=Image.alpha_composite(im,glow);d=ImageDraw.Draw(im);d.rounded_rectangle(box,15,fill='#091024',outline=accent,width=6)
 if a.theme==3:d.text((873,430),'00:00:03',font=ImageFont.truetype(mono,51),fill='white',anchor='mm',stroke_width=2,stroke_fill=accent)
 else:d.text((873,428),'∞',font=ImageFont.truetype(small,110),fill='#ffed32',anchor='mm',stroke_width=3,stroke_fill='#060916')
d.text((65,1820),'Então',font=ImageFont.truetype(small,43),fill='#fff4da',stroke_width=4,stroke_fill='#030919');a.out.parent.mkdir(parents=True,exist_ok=True);im.convert('RGB').save(a.out,quality=93);assert a.out.stat().st_size<2*1024*1024;print('COVER_READY',a.out)
