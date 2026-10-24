import {E,mood,S,layer,blurLayer,backdrop,poly,rr,seg,circle,glow,text,alpha,shade,linGrad} from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export function panel(g,x,y,w,h,c,r=8){rr(g,x,y,w,h,r);g.fillStyle=c;g.fill();}
export function neon(g,x,y,value,color='#ff5c68',s=1){
 const label=String(value).replace(/\B(?=(\d{3})+(?!\d))/g,'.'); const w=Math.max(105,label.length*37+35)*s,h=74*s;
 g.save();g.shadowColor=color;g.shadowBlur=18;panel(g,x-w/2,y-h/2,w,h,'#0c1324',8*s);g.lineWidth=3*s;g.strokeStyle=color;g.stroke();
 text(g,label,x,y,{size:48*s,font:'Nunito',weight:900,color,glow:12,glowColor:color});g.restore();
}
function window(g,x,y,w,h,M){panel(g,x-7,y-7,w+14,h+14,shade(M.wall,-.5));g.fillStyle=linGrad(g,x,y,x+w,y+h,[alpha(M.practical,.8),'#333454']);g.fillRect(x,y,w,h);seg(g,[[x+w/2,y],[x+w/2,y+h]],9,M.dark);seg(g,[[x,y+h*.55],[x+w,y+h*.55]],9,M.dark);}
export function table(g,x,y,w=520){panel(g,x-w/2,y,w,38,'#71483d');poly(g,[[x-w/2,y],[x-w/2+40,y-55],[x+w/2-40,y-55],[x+w/2,y]],'#9a6950');seg(g,[[x-w*.38,y+20],[x-w*.36,y+220]],25,'#2b2639');seg(g,[[x+w*.38,y+20],[x+w*.36,y+220]],25,'#2b2639');}
export function cup(g,x,y,s=1){panel(g,x-17*s,y-48*s,34*s,48*s,'#e8dcca',4*s);g.strokeStyle='#e8dcca';g.lineWidth=7*s;g.beginPath();g.arc(x+21*s,y-27*s,13*s,-1.7,1.7);g.stroke();}
export function phone(g,x,y,s=1,angle=0){g.save();g.translate(x,y);g.rotate(angle);panel(g,-27*s,-48*s,54*s,96*s,'#0a1021',8*s);panel(g,-21*s,-38*s,42*s,68*s,'#4f7186',3*s);circle(g,0,39*s,3*s,'#91adb5');g.restore();}
export function paper(g,x,y,s=1,label=''){g.save();g.translate(x,y);g.rotate(-.08);panel(g,-65*s,-80*s,130*s,160*s,'#dbd4c2',3);for(let i=0;i<5;i++)seg(g,[[-44*s,(-45+i*22)*s],[40*s,(-45+i*22)*s]],3*s,'#a5a295');if(label)text(g,label,0,-55*s,{size:18*s,color:'#3b4452'});g.restore();}
export function sandwich(g,x,y,s=1){poly(g,[[x-42*s,y],[x+40*s,y],[x-26*s,y-42*s]],'#eac17e');seg(g,[[x-39*s,y+4*s],[x+38*s,y+4*s]],8*s,'#4b8b61');seg(g,[[x-37*s,y+13*s],[x+35*s,y+13*s]],7*s,'#bc685a');}
export function bench(g,x,y,w=500){for(let i=0;i<3;i++)panel(g,x-w/2,y-175+i*25,w,18,'#5e4141');panel(g,x-w/2-10,y-78,w+20,22,'#84614b');for(const d of [-1,1])seg(g,[[x+d*w*.4,y-175],[x+d*w*.4,y]],15,'#131c31');}

export function set(g,t,cam,loc){
 const outside=['street','bench'].includes(loc),M=mood(outside?'night':loc==='hospital'?'interiorCool':'interiorWarm'); const GY=890;
 backdrop(g,M.sky);
 layer(g,cam,.15,g=>{
  for(let i=-3;i<18;i++){const x=i*175-60,h=180+(i*79%230);panel(g,x,540-h,160,h+350,shade(M.wall,-.52));for(let a=0;a<3;a++)for(let b=0;b<4;b++)if((i+a+b)%3)panel(g,x+23+a*43,560-h+b*57,18,27,alpha(M.practical,.24));}
  glow(g,1480,190,220,M.practical,.12);
 });
 layer(g,cam,.55,g=>{
 if(outside){
  panel(g,-900,670,3800,500,'#18253e');
  for(let i=0;i<7;i++){panel(g,360+i*145,620+i*22,1200-i*60,22,shade(M.wall,-.1-i*.04));}
  for(const x of [440,1550]){seg(g,[[x,320],[x,875]],14,'#0d1428');panel(g,x-32,295,64,70,M.practical);glow(g,x,330,170,M.practical,.2);poly(g,[[x-28,365],[x+28,365],[x+210,890],[x-210,890]],alpha(M.practical,.035));}
 }else{
  panel(g,-1000,-400,4000,1200,shade(M.wall,-.24));
  window(g,1340,130,380,440,M);
  for(let i=-2;i<15;i++)seg(g,[[i*180,0],[i*180,810]],4,alpha(M.key,.07));
  if(loc==='court'){panel(g,160,140,570,350,'#20273c');for(let i=0;i<7;i++)seg(g,[[260+i*63,150],[260+i*63,470]],25,'#4d4953');circle(g,440,280,75,'#696047');seg(g,[[440,225],[440,330]],8,'#c6ac6a');}
  if(loc==='home'){panel(g,180,490,390,270,'#443c59',28);panel(g,145,630,460,80,'#5c4a68',16);panel(g,610,145,220,390,'#151e32');panel(g,628,163,184,355,alpha(M.practical,.35));}
  if(loc==='mirror'){panel(g,420,90,1080,730,'#71624e',22);panel(g,447,116,1026,680,'#213849',14);seg(g,[[490,170],[950,750]],18,'#3a5361');seg(g,[[1040,150],[1430,650]],11,'#3a5361');}
  if(loc==='hospital'){for(let i=0;i<3;i++)panel(g,170+i*245,515,190,115,'#3b6171',14);text(g,'RECEPÇÃO',600,210,{size:38,color:'#8cb9bf'});seg(g,[[1050,260],[1120,260]],18,'#79bdad');seg(g,[[1085,225],[1085,295]],18,'#79bdad');}
  if(loc==='office'){panel(g,200,180,620,330,'#1a2638');for(let i=0;i<5;i++)for(let j=0;j<3;j++)panel(g,220+i*110,200+j*100,65,80,['#4e596f','#645244','#5d505f'][j]);}
  if(loc==='cafe'){panel(g,100,210,850,320,'#272b3e');for(let i=0;i<5;i++){seg(g,[[155+i*145,290],[155+i*145,450]],20,'#5e5064');}text(g,'CAFÉ',600,165,{size:54,color:M.practical});}
 }
 });
 layer(g,cam,.85,g=>{g.fillStyle=linGrad(g,0,760,0,1200,[shade(M.floor,-.04),shade(M.floor,-.5)]);g.fillRect(-1400,760,5000,900);for(let i=-8;i<18;i++)seg(g,[[960+i*90,760],[960+i*440,1500]],2,alpha(M.rim,.07));seg(g,[[-900,795],[2900,795]],4,alpha(M.rim,.14));});
 return {GY,M};
}
export function atmosphere(g,t,loc){
 const M=mood('night');
 for(let i=0;i<24;i++){const x=(i*127.3+t*(4+i%4))%1920,y=120+(i*173.7)%830+Math.sin(t*.4+i)*15;circle(g,x,y,1.1+i%2,alpha(M.rim,.08));}
 if(['street','bench'].includes(loc)){
  // Sparse street motion, never opaque rain slabs.
  for(let i=0;i<16;i++){const x=(i*137.8+t*25)%1920,y=(i*83+t*280)%1080;seg(g,[[x,y],[x-3,y+17]],1,alpha(M.rim,.12));}
 }
}
