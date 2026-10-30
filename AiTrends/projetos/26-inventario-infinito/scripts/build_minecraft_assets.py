from pathlib import Path
from PIL import Image,ImageDraw
import random,colorsys,json
roots=[Path(__file__).resolve().parents[1]]
uv={'head':[(8,0,16,8),(16,0,24,8),(0,8,8,16),(8,8,16,16),(16,8,24,16),(24,8,32,16)],'body':[(20,16,28,20),(28,16,36,20),(16,20,20,32),(20,20,28,32),(28,20,32,32),(32,20,40,32)],'armR':[(44,16,48,20),(48,16,52,20),(40,20,44,32),(44,20,48,32),(48,20,52,32),(52,20,56,32)],'armL':[(36,48,40,52),(40,48,44,52),(32,52,36,64),(36,52,40,64),(40,52,44,64),(44,52,48,64)],'legR':[(4,16,8,20),(8,16,12,20),(0,20,4,32),(4,20,8,32),(8,20,12,32),(12,20,16,32)],'legL':[(20,48,24,52),(24,48,28,52),(16,52,20,64),(20,52,24,64),(24,52,28,64),(28,52,32,64)]}
for p in roots:
 (p/'assets/skins').mkdir(exist_ok=True);(p/'assets/textures').mkdir(exist_ok=True)
 for name,color in [('nico',(33,161,151)),('lia',(151,94,191))]:
  rng=random.Random(26);im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
  for part,rects in uv.items():
   for j,rect in enumerate(rects):
    a,b,c,e=rect;base=(16,20,24)if part=='head'else color if part=='body'or part.startswith('arm')else(29,34,44)
    for y in range(b,e):
     for x in range(a,c):
      n=rng.randrange(-9,10);im.putpixel((x,y),tuple(max(0,min(255,v+n))for v in base)+(255,))
    if part.startswith('leg')and j>=2:d.rectangle((a,e-3,c-1,e-1),fill=(219,230,212,255))
    if part.startswith('arm')and j>=2:d.rectangle((a,e-3,c-1,e-1),fill=(18,22,26,255));d.line((a,e-4,c-1,e-4),fill=(224,231,201,255))
    if part=='body'and j==3:
     mid=(a+c)//2;d.line((mid,b,mid,e-1),fill=(231,230,201,255));d.line((a+1,b+9,a+2,b+9),fill=(231,230,201,255));d.line((c-3,b+9,c-2,b+9),fill=(231,230,201,255))
   if part=='head':
    a,b,c,e=rects[3];d.rectangle((a+1,b+2,a+2,b+3),fill=(248,239,214,255));d.rectangle((a+5,b+2,a+6,b+3),fill=(248,239,214,255));d.point((a+2,b+3),fill=(20,24,28,255));d.point((a+5,b+3),fill=(20,24,28,255));d.line((a+3,b+5,a+4,b+5),fill=(248,239,214,255))
  im.save(p/f'assets/skins/{name}.png');im.resize((512,512),Image.Resampling.NEAREST).save(p/f'assets/skins/{name}-preview.png')
 colors={'dirt':(126,87,57),'grass_top':(92,148,56),'grass_side':(126,87,57),'stone':(125,128,125),'cobblestone':(117,119,114),'oak_planks':(168,130,77),'oak_log':(98,76,43),'leaves':(65,120,43),'pink_leaves':(215,155,187),'sand':(215,202,150),'glass':(174,217,222),'water':(63,118,180)}
 for name,col in colors.items():
  im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);rng=random.Random(name)
  for y in range(16):
   for x in range(16):
    n=rng.randrange(-18,19);base=(92,148,56)if name=='grass_side'and y<3+(x%4==0)*2 else col
    alpha=0 if name in ['leaves','pink_leaves']and rng.random()<.10 else 255;im.putpixel((x,y),tuple(max(0,min(255,v+n))for v in base)+(alpha,))
  if name=='oak_planks':
   for y in [3,7,11,15]:d.line((0,y,15,y),fill=(105,78,42,255))
   for x,y in [(4,0),(12,4),(6,8),(13,12)]:d.line((x,y,x,y+3),fill=(117,90,49,255))
  if name=='oak_log':
   for x in [1,5,9,13]:d.line((x,0,x,15),fill=(62,49,29,255))
  if name=='cobblestone':
   for y in [0,5,10,15]:d.line((0,y,15,y),fill=(65,69,65,255))
   for x,y in [(5,0),(12,0),(3,5),(10,5),(7,10),(14,10)]:d.line((x,y,x,y+5),fill=(65,69,65,255))
  if name=='glass':d.rectangle((0,0,15,15),outline=(210,242,246,255));d.line((2,8,7,3),fill=(228,248,249,255));d.line((8,13,13,8),fill=(228,248,249,255))
  im.save(p/f'assets/textures/{name}.png')
 (p/'assets/skins/README.md').write_text('# Skins próprias\n\nPNG 64×64, layout padrão de skin Minecraft Java, braços clássicos de 4 pixels (modelo Steve), com camadas externas transparentes. Nico verde-água e Lia lavanda. Criadas por código neste projeto; não são skins oficiais nem assets extraídos do jogo. `*-preview.png` amplia o atlas por vizinho mais próximo. O filme usa as proporções 8×8×8 cabeça, 8×12×4 tronco, 4×12×4 em cada braço e perna. Texturas do cenário também são originais, 16×16, filtro nearest.\n')
print('skins and original 16px textures ready')
