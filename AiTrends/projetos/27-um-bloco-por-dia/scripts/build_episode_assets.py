from pathlib import Path
from PIL import Image,ImageDraw
import random
p=Path(__file__).resolve().parents[1]/'assets/textures'
base=Image.open(p/'stone.png').convert('RGBA');im=base.copy();d=ImageDraw.Draw(im)
for x,y in [(2,3),(10,2),(7,7),(2,11),(12,11)]:
 d.rectangle((x,y,x+2,y+2),fill='#188d9b');d.rectangle((x,y,x+1,y+1),fill='#61e5ed');d.point((x,y),fill='#c0f9f5')
im.save(p/'diamond_ore.png');im=Image.new('RGBA',(16,16));rng=random.Random(27)
for y in range(16):
 for x in range(16):
  v=rng.randrange(100,165);im.putpixel((x,y),(v,v-4,v-9,255))
d=ImageDraw.Draw(im)
for i in range(20):
 x,y=rng.randrange(16),rng.randrange(16);d.line((x,y,min(15,x+2),y),fill='#505451')
im.save(p/'gravel.png')
