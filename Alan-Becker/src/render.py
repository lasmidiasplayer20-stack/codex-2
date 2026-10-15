"""Original authored 2D short. Pillow rigs + deterministic timeline; no reference frames."""
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, pathlib, sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
W,H,FPS,DURATION=1280,720,24,120
BG='#101925'; GRID='#1c2a3b'; WHITE='#e9f1f9'; CYAN='#55e2df'; RED='#ff897d'; GOLD='#ffcf75'; MUTED='#8297ad'
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
fonts={n:font(n) for n in [14,18,22,28,40,68]}
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,b,u):return a+(b-a)*ease(u)
def path(keys,t):
 for a,b in zip(keys,keys[1:]):
  if t<=b[0]:return mix(a[1],b[1],(t-a[0])/(b[0]-a[0]))
 return keys[-1][1]
def txt(s,x,y,n=22,c=WHITE,anchor=None):d.text((x,y),s,font=fonts[n],fill=c,anchor=anchor)
def line(points,c,w=6):
 d.line(points,fill=c,width=w,joint='curve')
 for x,y in points:d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=c)
def box(x,y,w,h,c=GRID,outline=None,r=12):d.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=c,outline=outline,width=2)
def limb(a,b,l,c,side=1):
 dx,dy=b[0]-a[0],b[1]-a[1];dist=max(.01,math.hypot(dx,dy));q=math.sqrt(max(0,l*l-(dist/2)**2));m=((a[0]+b[0])/2-dy/dist*q*side,(a[1]+b[1])/2+dx/dist*q*side);line([a,m,b],c,8)
def actor(x,y,c,t,mode='idle',f=1,scale=1,rot=0,hand=None):
 # y is the supporting ground. Fixed lengths; eased joints and planted support.
 phase=t*11;stride=math.sin(phase) if mode=='run' else 0
 bob=abs(math.cos(phase))*5 if mode=='run' else math.sin(t*2)*1.5
 hip=(0,-51-bob);neck=(f*(8 if mode=='run' else 0),-96-bob)
 feet=[(-18-stride*25,0),(18+stride*25,-max(0,stride)*18)]
 hands=[(-25+stride*24,-65),(26-stride*24,-66)]
 if mode=='reach':hands=[(-27,-75),(f*46,-116)]
 if mode=='push':hands=[(f*49,-82),(f*49,-98)]
 if mode=='guard':hands=[(-25,-111),(28,-115)]
 if mode=='jump':feet=[(-30,-28),(31,-22)];hands=[(-36,-118),(38,-120)]
 if mode=='sit':hip=(0,-23);neck=(8,-67);feet=[(-30,0),(40,0)];hands=[(-25,-20),(30,-20)]
 if mode=='wave':hands=[(-24,-65),(35+math.sin(t*9)*8,-137)]
 if hand: hands[1]=hand
 def tr(p):return (x+scale*(p[0]*math.cos(rot)-p[1]*math.sin(rot)),y+scale*(p[0]*math.sin(rot)+p[1]*math.cos(rot)))
 # contact shadow
 d.ellipse((x-34*scale,y-3,x+34*scale,y+7),fill='#0b111b')
 for i,p in enumerate(feet):limb(tr(hip),tr(p),30*scale,c,1 if i==0 else -1)
 line([tr(hip),tr(neck)],c,8)
 for i,p in enumerate(hands):limb(tr(neck),tr(p),27*scale,c,-1 if i==0 else 1)
 hx,hy=tr((neck[0],neck[1]-23));r=18*scale
 d.ellipse((hx-r,hy-r,hx+r,hy+r),fill=BG,outline=c,width=max(2,int(7*scale)))
def tile(x,y,w=160,c=CYAN,label=''):
 box(x,y,w,22,'#243c4b',c,5)
 for z in range(int(x+10),int(x+w-5),20):line([(z,y+7),(z+8,y+7)],c,2)
 if label:txt(label,x+w/2,y+34,14,MUTED,'mt')
def cursor(x,y,c=WHITE,size=1):
 pts=[(x,y),(x+10*size,y+36*size),(x+18*size,y+25*size),(x+30*size,y+22*size)]
 d.polygon(pts,fill=c,outline=BG)
def orb(x,y,t,r=18):
 for i in range(3):d.ellipse((x-r-i*6,y-r-i*6,x+r+i*6,y+r+i*6),outline=['#ffcf75','#735e3f','#3e3940'][i],width=2)
 d.ellipse((x-r/2,y-r/2,x+r/2,y+r/2),fill=GOLD)
def drone(x,y,t,size=1,safe=False):
 c=CYAN if safe else RED
 for sign in [-1,1]:line([(x+sign*34*size,y),(x+sign*58*size,y-18*size)],c,5)
 box(x-40*size,y-23*size,80*size,46*size,'#304051',c,10)
 d.ellipse((x-11*size,y-11*size,x+11*size,y+11*size),fill=c)
 if not safe:
  for i in [-1,0,1]:line([(x-21+i*20,y+33),(x-12+i*20,y+43)],RED,3)
def particles(x,y,t,c=GOLD,count=25,spread=100):
 for i in range(count):
  a=i*2.399;v=(i%7+3)/10;rr=(t%1.5)*spread*v
  xx=x+math.cos(a)*rr;yy=y+math.sin(a)*rr+25*(t%1.5)**2
  d.rectangle((xx,yy,xx+4,yy+4),fill=c)
CHAPTERS=[(0,'01 / UM PIXEL FORA DO LUGAR'),(10,'02 / LIMPEZA AUTOMÁTICA'),(20,'03 / CORRER NÃO RESOLVE'),(30,'04 / O PRIMEIRO ATALHO'),(40,'05 / DUPLICAR O PROBLEMA'),(50,'06 / PESO DEMAIS'),(60,'07 / PENSAR FORA DA JANELA'),(70,'08 / UM PLANO ELÁSTICO'),(80,'09 / CORRIDA CONTRA O VAZIO'),(90,'10 / NÃO APAGUE'),(100,'11 / DESFAZER'),(110,'12 / NINGUÉM FICA PARA TRÁS')]
def frame(t):
 global im,d
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 for x in range(0,W,40):d.line((x,76,x,H-58),fill=GRID)
 for y in range(76,H-58,40):d.line((0,y,W,y),fill=GRID)
 box(24,16,1232,46,'#182535',None,12);txt('FRAME / laboratório de ideias',44,28,18);txt('●  arquivo não salvo',1218,30,14,GOLD,'rt')
 box(24,650,1232,48,'#182535');txt('V   seleção     /     D   duplicar     /     Z   desfazer',44,666,14,MUTED)
 txt(f'{int(t)//60:02}:{int(t)%60:02} / 02:00',1220,666,14,MUTED,'rt')
 d.rectangle((26,696,26+1228*t/120,699),fill=CYAN)
 s=min(11,int(t//10));u=t-s*10
 txt(CHAPTERS[s][1],42,92,14,MUTED)
 # The same golden pixel travels through every scene.
 if s==0:
  tile(130,560,1020);actor(path([(0,220),(3,380),(7,480),(10,480)],u),560,CYAN,t,'run' if u<7 else 'reach')
  actor(820,560,RED,t,'sit' if u<5 else 'idle',-1)
  orb(530,426+math.sin(t*3)*6,t)
  if u<3:txt('UM PIXEL',640,220,68,WHITE,'mt');txt('uma pequena ideia pode mudar tudo',640,308,22,MUTED,'mt')
  if u>7:cursor(mix(1050,560,(u-7)/2),mix(230,430,(u-7)/2));particles(530,430,u-7,count=10,spread=30)
 elif s==1:
  tile(130,560,1020);actor(480,560,CYAN,t,'guard');actor(820,560,RED,t,'reach',-1)
  orb(520,435,t);drone(mix(1100,700,u/5),245,t)
  box(820,150,340,62,'#382b35',RED);txt('LIMPEZA AUTOMÁTICA',990,170,22,RED,'mt')
  if u>3:
   xx=mix(1120,600,(u-3)/7);d.polygon([(700,265),(xx,556),(1150,556)],fill='#392936');tile(130,560,max(20,xx-130))
   for i in range(24):particles(xx+i*20,565,u/2+i,RED,3,30)
 elif s==2:
  x=mix(1000,190,u/9);tile(70,560,1140);drone(x+160,330,t);actor(x,560,CYAN,t,'run',-1);actor(x-120,560,RED,t,'run',-1);orb(x-135,420,t)
  for i in range(7):line([(x+190+i*28,430+i%3*22),(x+215+i*28,430+i%3*22)],RED,2)
  if u>6:d.rectangle((620,559,1210,585),fill=BG);txt('SEM SAÍDA',1050,490,28,RED,'mm')
 elif s==3:
  tile(70,560,330);tile(800,450,370);box(415,160,370,54,'#24394a',CYAN);txt('SELEÇÃO = PLATAFORMA',600,175,22,CYAN,'mt')
  xx=mix(400,700,u/5);yy=mix(560,450,u/5)
  d.rectangle((xx-55,yy,xx+100,yy+24),outline=CYAN,width=2)
  for a,b in [(xx-55,yy),(xx+100,yy),(xx-55,yy+24),(xx+100,yy+24)]:d.rectangle((a-4,b-4,a+4,b+4),fill=WHITE)
  actor(xx,yy,CYAN,t,'push' if u<5 else 'wave');actor(mix(260,850,max(0,u-3)/6),560-110*ease((u-3)/6)-120*max(0,math.sin(math.pi*max(0,min(1,(u-3)/6)))),RED,t,'jump');orb(xx+35,yy-150,t);cursor(xx+99,yy+23)
 elif s==4:
  tile(80,560,1120);actor(340,560,CYAN,t,'reach');actor(510,560,RED,t,'push');orb(520,410,t)
  for i in range(min(5,int(u)+1)):
   tile(590+i*105,520-i*50,95,GOLD,'Ctrl+D' if i==0 else '')
   if u>5:drone(780+i*72,245+i%2*60,t,.7)
  if u>5:txt('...ele também sabe duplicar.',640,160,28,RED,'mt')
 elif s==5:
  tilt=.06*math.sin(u*4);tile(120,560,1040)
  actor(360,560,CYAN,t,'guard');actor(510,560,RED,t,'guard');orb(510,410,t)
  for i in range(6):drone(650+i*80,280+math.sin(t*3+i)*32,t,.7)
  for i in range(6):
   yy=mix(330-i*30,510-i*23,u/7);tile(720-i*20,yy,190,GOLD)
  if u>6:particles(790,540,u-6,RED,50,180);txt('MEMÓRIA: 99%',1040,165,28,RED,'mt')
 elif s==6:
  tile(100,560,1080);actor(360,560,CYAN,t,'sit' if u<3 else 'reach');actor(560,560,RED,t,'idle');orb(570,420,t)
  box(720,200,330,220,'#192c3d',CYAN);txt('PROPRIEDADES',745,222,18,MUTED)
  txt('Rigidez',745,276,22);line([(750,340),(1000,340)],MUTED,4)
  knob=mix(980,775,max(0,u-4)/3);d.ellipse((knob-10,330,knob+10,350),fill=CYAN);cursor(knob,340)
  txt('100% → 0%',745,375,18,GOLD)
  if u>7:txt('E se o chão fosse uma mola?',640,154,28,WHITE,'mt')
 elif s==7:
  tile(100,560,200);tile(980,560,200)
  sag=70*math.sin(math.pi*min(1,u/6))
  pts=[(300+i*680/40,560+sag*math.sin(math.pi*i/40)) for i in range(41)];line(pts,CYAN,5)
  xx=mix(380,640,u/5);actor(250,560,CYAN,t,'push')
  if u<=6:actor(xx,560+sag*math.sin(math.pi*(xx-300)/680),RED,t,'push');orb(xx,410+sag,t)
  if u>6:
   yy=560-360*math.sin(math.pi*(u-6)/5);actor(mix(640,980,(u-6)/4),yy,RED,t,'jump');orb(mix(640,980,(u-6)/4)+30,yy-140,t)
  drone(1000,230,t);txt('ESTICAR. SOLTAR. VOAR.',640,180,28,GOLD,'mt')
 elif s==8:
  for i in range(5):tile(60+i*260,560-i%2*100,150)
  xx=140+u*95;yy=510-105*abs(math.sin(u*math.pi/2.5));actor(xx,yy,RED,t,'run' if u%2.5<.7 else 'jump');orb(xx+25,yy-145,t)
  actor(xx-130,yy+25,CYAN,t,'jump');drone(xx-300,300,t)
  for i in range(30):
   xx2=(i*71+t*210)%1280;line([(xx2,220+i%7*45),(xx2+28,220+i%7*45)],'#304052',2)
  box(1040,145,150,56,'#334435',GOLD);txt('SALVAR',1115,161,22,GOLD,'mt')
 elif s==9:
  tile(80,560,1120);actor(850,560,RED,t,'reach' if u<4 else 'guard');orb(900,417,t)
  actor(mix(520,740,u/5),560,CYAN,t,'run' if u<5 else 'reach')
  dy=mix(210,490,u/8);drone(570,dy,t)
  if u>3:
   for i in range(12):d.rectangle((100+i*95,580,155+i*95,620),fill=RED if i<u else GRID)
   txt('LIMPEZA TOTAL EM '+str(max(0,6-int(u-3))),640,160,28,RED,'mt')
  if u>6:line([(570,dy+25),(570,570)],RED,3);txt('!',755,370,40,GOLD)
 elif s==10:
  tile(80,560,1120);actor(740,560,CYAN,t,'push');actor(850,560,RED,t,'reach')
  box(350,245,250,95,'#263d4e',CYAN);txt('Ctrl + Z',475,268,40,CYAN,'mt');cursor(560,310)
  drone(570,mix(490,300,u/7),t,safe=u>5)
  orb(mix(900,640,u/7),mix(417,260,u/7),t)
  if u>1:
   rad=(u-1)*115;d.ellipse((570-rad,370-rad,570+rad,370+rad),outline=CYAN,width=5)
   for i in range(7):tile(100+i*160,560,145)
   particles(570,370,u,CYAN,50,250)
  txt('Desfazer a ordem. Salvar quem a executava.',640,170,28,WHITE,'mt')
 elif s==11:
  tile(130,560,1020);actor(490,560,CYAN,t,'wave' if u<5 else 'sit');actor(790,560,RED,t,'wave' if u<5 else 'sit');drone(640,400+math.sin(t*3)*10,t,safe=True)
  orb(640,260,t)
  if u>3:
   # The former eraser now draws a tiny garden around the saved pixel.
   for i in range(min(9,int((u-3)*2))):
    x=220+i*100;line([(x,556),(x,525)],CYAN,3);d.ellipse((x-8,513,x+8,529),fill=GOLD if i%2 else RED)
  if u>6:txt('NENHUMA IDEIA É DESCARTÁVEL.',640,180,40,WHITE,'mt');txt('FIM  /  um curta original feito por código',640,610,18,MUTED,'mt')
 return im
if __name__=='__main__':
 if '--stills' in sys.argv:
  for t in [4,16,26,36,46,56,66,76,86,96,106,117]:frame(t).save(ROOT/'previews'/f'{t:03}.jpg')
 else:
  cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(ROOT/'silent.mp4')]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(ROOT/'render.log','w'))
  for i in range(FPS*DURATION):
   p.stdin.write(frame(i/FPS).tobytes())
   if i%(FPS*10)==0:print(f'{i/FPS:.0f}/{DURATION}s',flush=True)
  p.stdin.close();sys.exit(p.wait())
