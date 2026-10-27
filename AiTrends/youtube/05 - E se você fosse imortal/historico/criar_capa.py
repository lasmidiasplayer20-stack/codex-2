"""Original thumbnail, drawn entirely with Pillow; no external image or API."""
from pathlib import Path
import math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent;S=2;W,H=1280,720
im=Image.new('RGB',(W*S,H*S));pix=im.load()
for y in range(H*S):
 for x in range(W*S):
  u=x/(W*S);v=y/(H*S);warm=max(0,1-math.hypot(u-.79,v-.52)*1.8);pix[x,y]=(int(8+warm*25),int(18+warm*40),int(40+warm*34))
g=ImageDraw.Draw(im)
def xy(points):return [(int(x*S),int(y*S))for x,y in points]
def line(points,fill,width):
 g.line(xy(points),fill=fill,width=int(width*S),joint='curve')
 for x,y in [points[0],points[-1]]:g.ellipse(((x-width/2)*S,(y-width/2)*S,(x+width/2)*S,(y+width/2)*S),fill=fill)
def ellipse(box,fill,outline=None,width=1):g.ellipse(tuple(int(v*S)for v in box),fill=fill,outline=outline,width=width*S)
def rect(box,fill,r=0,outline=None,width=1):g.rounded_rectangle(tuple(int(v*S)for v in box),r*S,fill=fill,outline=outline,width=width*S)
def poly(points,fill):g.polygon(xy(points),fill=fill)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(s,x,y,size,color='#fff3dc',stroke=5):
 font=ImageFont.truetype(fontpath,size*S);g.text((x*S,y*S),s,font=font,fill=color,stroke_width=stroke*S,stroke_fill='#07111d')
rng=random.Random(51)
for i in range(100):
 x,y=rng.randrange(1280),rng.randrange(650);r=rng.choice([.8,1,1.5]);ellipse((x-r,y-r,x+r,y+r),'#647c98')
# Stable cosmic clock motif and changing skyline.
ellipse((670,3,1260,593),None,'#456c79',3);ellipse((693,26,1237,570),None,'#284c60',2)
for i in range(12):
 a=i*math.pi/6;line([(965+263*math.sin(a),298-263*math.cos(a)),(965+278*math.sin(a),298-278*math.cos(a))],'#a6b4a5',4)
for i in range(15):
 x=i*95;ht=40+rng.randrange(95);rect((x,720-ht,x+78,720),'#122a3c',4)
# Main original Nico, mint zip jacket, intentional reach toward old photograph.
ink='#0b1321';mint='#2ac9b4';rim='#f0d5a6'
ellipse((837,663,1188,717),'#091523')
for pts in [[(958,552),(944,627),(918,684)],[(1014,552),(1053,628),(1072,684)]]:
 line(pts,rim,29);line(pts,ink,23)
line([(899,687),(936,687)],'#e4fff5',25);line([(1065,687),(1101,687)],'#e4fff5',25)
poly([(943,329),(1028,329),(1060,553),(928,553)],ink)
poly([(950,337),(1022,337),(1048,544),(939,544)],mint)
line([(981,351),(993,532)],'#d7fff3',4);line([(964,497),(1017,497)],'#169d93',5)
line([(949,356),(871,396),(812,442)],ink,39);line([(949,356),(871,396),(812,442)],mint,29)
line([(1028,356),(1103,433),(1065,522)],ink,39);line([(1028,356),(1103,433),(1065,522)],mint,29)
ellipse((1048,503,1087,542),ink)
ellipse((876,103,1082,309),rim);ellipse((883,110,1075,302),ink)
# Curious/concerned face looking toward the photograph.
ellipse((918,190,946,224),'#fff6e8');ellipse((984,190,1012,224),'#fff6e8')
ellipse((920,205,931,218),ink);ellipse((985,205,996,218),ink)
line([(915,174),(945,163)],'#fff6e8',6);line([(981,163),(1012,174)],'#fff6e8',6)
g.arc((942*S,237*S,994*S,270*S),10,155,fill='#fff6e8',width=5*S)
# Photo: two original silhouettes and a chair, not an imported frame.
rect((745,374,834,485),'#f4e4bd',5,ink,3);rect((752,381,827,464),'#88aba7',1)
for x,c in [(773,mint),(805,'#ac76e2')]:
 line([(x,418),(x,451)],c,12);ellipse((x-9,398,x+9,416),ink)
line([(780,442),(799,442),(799,453)],'#775438',4)
ellipse((797,429,830,460),ink)
# Text remains uncluttered and readable at small thumbnail size.
label('VIVER',48,46,106,'#fff4dc',7);label('PRA SEMPRE?',45,169,82,'#ffe054',6)
rect((53,551,531,633),'#092332',16,'#75cbbb',3);label('ANO 2326',78,564,52,'#d5fff0',2)
label('Então',59,669,26,'#b8d5d5',2)
im.resize((W,H),Image.Resampling.LANCZOS).save(ROOT/'capa.jpg',quality=94,optimize=True)
print(ROOT/'capa.jpg')
