import {E,S,mood,registerShot,layer,blurLayer,veil,clamp,lerp,ease,prog,text,seg,circle,rr,alpha,shade} from '/engine/core.js';
import {drawFigure,POSES,posesAt,breathe,bigFace,headPos,walkPose} from '/engine/rig2d.js';
import {drawCTA} from './cta.js';
import {CAIO,JUDGE,MARA,ANDRE,RUI,MOTHER,WITNESS,YOUNG} from './cast.js';
import {set,neon,panel,table,cup,phone,paper,bench,sandwich,atmosphere} from './stage.js';
const beats=await (await fetch('/project/story/beats.json')).json();
const plan=await (await fetch('/project/story/shots.json')).json();
const OUTSIDE=['street','bench'];
const COUNTERS=new Set(['door','test','self','belief','kindness','crowd','witness','questions','release','distance','phone','friend','follow','reveal','mother','talk','listen','promise','zero','ask','share','admit','agreement','lesson','ending','question']);
const seconds=(t)=>`${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;

// Constant-length two-link arms: stable elbow side, bounded reach, no rubber limbs.
function elbow(a,b,L=38,side=1){let dx=b[0]-a[0],dy=b[1]-a[1],d=Math.hypot(dx,dy);d=Math.max(.01,Math.min(d,2*L-.03));let ang=Math.atan2(dy,dx)-side*Math.acos(d/(2*L));return [a[0]+Math.cos(ang)*L,a[1]+Math.sin(ang)*L];}
function fixed(p){p={...p};for(const side of ['F','B']){let h=p['h'+side],a=p.sh;let dx=h[0]-a[0],dy=h[1]-a[1],d=Math.hypot(dx,dy);if(d>75.8)p['h'+side]=h=[a[0]+dx/d*75.8,a[1]+dy/d*75.8];p['e'+side]=elbow(a,h,38,side==='F'?1:-1);}return p;}
function idle(t,action='stand',seed=0){
 const gesture=action==='question'?'shrug':action==='ask'||action==='questions'?'talk':action==='admit'||action==='listen'?'sad':action==='belief'?'think':action==='phone'?'phone':action==='test'?'point':action==='reject'?'crossArms':action==='talk'?'explain':'relaxed';
 const pose=posesAt(t,[[0,'stand'],[.5,gesture],[2.7,gesture],[3.5,'relaxed']],.55);
 return fixed(breathe(pose,t,.3,seed));
}
// Stance-foot world position remains fixed while the body advances linearly.
function groundedWalk(t,speed=68){
 const stride=52,cycle=stride/(speed*.6),phase=(t/cycle)%1,p={...POSES.stand};
 p.hip=[0,-98+Math.sin(phase*Math.PI*4)*1.2];p.sh=[3,p.hip[1]-74];p.head=[7,p.sh[1]-34];
 for(const [side,off] of [['F',0],['B',.5]]){const q=(phase+off)%1;const stance=q<.6;let x,y;if(stance){x=stride/2-q/.6*stride;y=0;}else{const r=(q-.6)/.4;x=-stride/2+stride*ease.inOut(r);y=-13*Math.sin(Math.PI*r);}p['f'+side]=[x,y];const a=p.hip,b=p['f'+side];let dx=b[0]-a[0],dy=b[1]-a[1],d=Math.min(Math.hypot(dx,dy),103.99),ang=Math.atan2(dy,dx)-Math.acos(clamp(d/104,-1,1));p['k'+side]=[a[0]+52*Math.cos(ang),a[1]+52*Math.sin(ang)];p['h'+side]=[5+Math.sin((phase+off)*Math.PI*2)*12,-103];}
 return fixed(p);
}
function configFor(b){
 let other=MARA,expr='neutral',pose='stand';
 if(['reject','zero','ask','share','ending'].includes(b.action)){other=RUI;expr='worried';}
 if(['friend','promise'].includes(b.action))other=ANDRE;
 if(['witness','questions','lesson'].includes(b.action))other=WITNESS;
 if(b.action==='release')other=YOUNG;
 if(b.action==='kindness')other={...MARA,top:'hoodie',head:'bun'};
 if(b.action==='mother')other=MOTHER;
 if(['test','distance','phone','follow','blackout','door'].includes(b.action))expr='nervous';
 if(['self','reveal','mother'].includes(b.action))expr='surprised';
 if(['admit','ending','listen'].includes(b.action))expr='sad';
 return {other,expr,pose};
}
function person(g,o,t,count=null){drawFigure(g,o);if(count!==null){const [x,y]=headPos(o);neon(g,x,y-54*o.s,count,count===0?'#55e1a5':'#ff6574',Math.max(.65,o.s*.48));}}
function character(g,b,t,x,y,s,which=0,opts={}){
 const cfg=configFor(b),outfit=which?cfg.other:(b.set==='court'?JUDGE:CAIO);
 let pose=idle(t,which?(b.action==='talk'?'talk':b.action==='share'?'ask':'stand'):b.action,which*7),expr=which?(['ask','zero','ending','share'].includes(b.action)?'neutral':'worried'):cfg.expr;
 if(opts.walk){pose=groundedWalk(t,Math.abs(opts.walk));x+=opts.walk*t*s;}
 if(opts.sit)pose=fixed(breathe(POSES.sit,t,.22,which*3));
 // Emotional eyelines change before the hands; avoid mirrored, simultaneous gestures.
 if(which&&b.action==='door')expr=t<1.3?'smile':'worried';
 if(opts.pose)pose=fixed(opts.pose);
 const f=opts.facing??(which?-1:1),o={x,y,s,facing:f,outfit,pose,expr:opts.expr||expr,rim:{color:which?'#79b7dc':'#edc56d',dir:[-1,-.6],w:4},blink:(t%(which?3.7:3.2))>3.08,look:opts.look||[which?-.2:.35,COUNTERS.has(b.action)?-.15:0],talk:0};
 let count=opts.count;if(count===undefined&&COUNTERS.has(b.action))count=which?b.count:null;
 if(['self','belief','admit'].includes(b.action)&&!which)count=b.count;
 if(['arrival','reject','rest','question'].includes(b.action))count=null;
 if(b.action==='blackout'&&which&&opts.count===undefined)count=9311;
 if(b.action==='door'&&which&&opts.count===undefined)count=9314;
 if(b.action==='talk'&&which&&opts.count===undefined)count=9314;
 person(g,o,t,count);return o;
}
function foreground(g,t,cam,side=-1){blurLayer(g,9,g=>{circle(g,side<0?160:1760,650,170,'#0a1020');panel(g,side<0?-70:1560,800,430,550,'#0a1020',100);},cam,1.45);}
function backgroundMotion(g,b,local,cam){
 if(!OUTSIDE.includes(b.set))return;
 layer(g,cam,.68,g=>{
  for(let i=0;i<2;i++){const x=((local*56+i*820)%2300)-200;drawFigure(g,{x,y:775,s:.55,facing:i?-1:1,pose:groundedWalk(local+i*2),outfit:{top:'none'},rim:{color:'#638a9f',dir:[-1,-1]},dim:.7});}
  if(b.action==='follow'||b.action==='reveal'){const x=200+ease.inOut(clamp(local/13))*600;panel(g,x,695,300,78,'#283853',20);panel(g,x+65,645,150,65,'#344c63',20);for(const dx of [55,245])circle(g,x+dx,778,27,'#080f1b');}
 });
}
function props(g,b,t){
 if(['home','cafe','office'].includes(b.set)){
  table(g,960,810,520);
  if(['phone','distance','friend','rest','agreement'].includes(b.action))phone(g,1020,750,.7,-.2);
  cup(g,850,755,.7);cup(g,1110,755,.7);
 }
 if(b.set==='court'){table(g,520,785,520);paper(g,550,700,.45);table(g,1370,815,350);}
 if(b.set==='hospital'){bench(g,1150,870,470);paper(g,1100,740,.5);}
 if(b.set==='bench'||['zero','ask','share'].includes(b.action)){bench(g,1060,900,650);if(b.action==='share')sandwich(g,960,770,.8);}
}
function polyLaptop(g){panel(g,550,740,820,35,'#66717d',5);for(let i=0;i<6;i++)seg(g,[[690,410+i*38],[1180,410+i*38]],8,'#8c9aa7');}
function insert(g,b,t,info,cam){
 // Dedicated graphic/prop shots tell the beat, instead of repeating a character tableau.
 if(['door','blackout','test','self','belief','crowd','witness','zero','question'].includes(b.action)){
  const val=b.action==='question'?'?':b.action==='test'?(t>info.dur*.4?9312:9311):b.count;neon(g,960,455,val,val===0?'#55e1a5':'#ff6574',3.1);
  text(g,b.action==='belief'?'CERTEZA NÃO É PROVA':b.action==='zero'?'NENHUMA MENTIRA?':'O QUE ESSE NÚMERO NÃO CONTA?',960,735,{size:44,color:'#e8e0cb'});
 }else if(['phone','distance','friend','follow'].includes(b.action)){
  phone(g,960,500,4.2,-.09+ease.inOut(t/info.dur)*.13);if(b.action==='phone')text(g,'AMANHÃ. MESMO HORÁRIO.',960,470,{size:24,color:'#d9f0ee'});
  // Only the hand/forearm entering toward the phone, not an unattached full arm.
  const q=ease.inOut(clamp(t/1.8));seg(g,[[1320,1200],[1160,980],[1120-65*q,730-20*q]],64,'#131826');seg(g,[[1320,1200],[1160,980]],76,CAIO.color);circle(g,1120-65*q,730-20*q,33,'#131826');
 }else if(['questions','release','lesson','arrival'].includes(b.action)){
  paper(g,960,480,3.4);text(g,'CONFERIR PRIMEIRO',960,385,{size:48,color:'#354758'});for(let i=0;i<3;i++)text(g,['HORÁRIO','DISTÂNCIA','GRAVAÇÃO'][i],970,490+i*72,{size:33,color:'#354758'});
 }else if(['share','ending','ask'].includes(b.action)){
  sandwich(g,860,560,4);sandwich(g,1110,560,3);const q=ease.inOut(t/info.dur);seg(g,[[1700,850],[1350-180*q,640]],100,'#182134');circle(g,1350-180*q,640,56,'#182134');
 }else if(['reveal','mother','talk','listen'].includes(b.action)){
  paper(g,960,490,3.2);text(g,'EXAMES',960,330,{size:65,color:'#354758'});text(g,'O CONTEXTO MUDA TUDO',960,805,{size:47,color:'#f0dcc0'});
 }else if(b.action==='reject'){
  const q=ease.inOut(t/info.dur);panel(g,690,350,380,250,'#57463a');text(g,'AJUDA PARA COMER',960,710,{size:48,color:'#edd8b6'});seg(g,[[1300,1050],[1180,750],[1060+90*q,590]],80,CAIO.color);circle(g,1060+90*q,590,42,'#131829');
 }else if(b.action==='rest'){
  panel(g,600,330,720,410,'#0d182b',18);panel(g,625,350,670,350,'#41516b',9);polyLaptop(g);text(g,'SÓ UM POUCO.',960,240,{size:62,color:'#f0dcc0'});
 }else if(b.action==='promise'){
  text(g,'EU ESTAVA COM MEDO.',960,390,{size:67,color:'#f0dcc0'});neon(g,960,600,6043,'#ff6574',2.1);
 }else{
  const q=ease.inOut(t/info.dur);cup(g,960,650,3);seg(g,[[550,1050],[750+80*q,780],[850+30*q,660]],75,CAIO.color);circle(g,850+30*q,660,38,'#121525');
  if(b.action==='admit')text(g,'EU COMPLETEI AS LACUNAS.',960,290,{size:53,color:'#eadfc8'});
 }
}
function diagram(g,t,info){
 const M=mood('void');g.fillStyle='#101c32';g.fillRect(0,0,E.W,E.H);
 for(let x=0;x<1920;x+=60)seg(g,[[x,0],[x,1080]],1,'#1c3048');for(let y=0;y<1080;y+=60)seg(g,[[0,y],[1920,y]],1,'#1c3048');
 const labels=['UM SINAL','UMA HIPÓTESE','UMA PERGUNTA'];
 if(info.part>0){const k=info.part-1,q=ease.inOut(t/info.dur);panel(g,380-q*30,300,1160+q*60,440,'#1b3046');text(g,labels[k],960,420,{size:78,color:'#edcb6b'});text(g,['NÃO É UMA CERTEZA','NÃO É UMA PROVA','PODE SER CONFERIDA'][k],960,590,{size:56,color:'#bad9e2'});text(g,'O CONTEXTO VEM ANTES DO JULGAMENTO',960,855,{size:42,color:'#93c4d6'});return;}
 for(let i=0;i<3;i++){const q=clamp((t-i*.45)/.5);g.globalAlpha=q;panel(g,200+i*555,360,440,300,'#1b3046');text(g,labels[i],420+i*555,430,{size:35,color:i===2?'#edcb6b':'#93c4d6'});text(g,['≠ CERTEZA','≠ PROVA','→ CONFERIR'][i],420+i*555,570,{size:32,color:'#f0e0c4'});if(i<2)seg(g,[[650+i*555,510],[730+i*555,510]],7,'#e5bd69');}
 g.globalAlpha=1;text(g,'UMA HIPÓTESE DE FICÇÃO',960,190,{size:61,color:'#efe0c4'});text(g,'NENHUM CONTADOR SUBSTITUI O CONTEXTO',960,855,{size:46,color:'#93c4d6'});
}
function scene(g,t,info){
 const b=beats[info.beat],mode=info.mode,p=clamp(t/info.dur),q=ease.inOut(p),bt=info.globalT-b.start;
 if(b.set==='diagram'){diagram(g,t,info);drawCTA(g,info.globalT);return;}
 let cam={z:1.03+.045*q,x:lerp(-22,22,q),y:0,r:0};
 if(mode==='wide')cam={z:1.00+.045*q,x:lerp(-20,15,q),y:-15};
 if(mode==='track')cam={z:1.1,x:lerp(-100,140,q),y:5};
 const {GY,M}=set(g,bt,cam,b.set);backgroundMotion(g,b,bt,cam);
 if(mode==='close'){
  // Larger face reacts to a concrete event; no narration lip-sync.
  veil(g,'#060d1c',.35);const cfg=configFor(b);const isOther=['door','mother','zero','release'].includes(b.action);const outfit=isOther?cfg.other:(b.set==='court'?JUDGE:CAIO);
  const r=235+16*q,cx=1060-35*q,cy=610;
  bigFace(g,cx,cy,r,{outfit,expr:isOther?(['zero','ending'].includes(b.action)?'neutral':'worried'):cfg.expr,rimColor:M.rim,rimSide:-1,blink:bt%3.6>3.48,look:[-.4,-.15],tilt:Math.sin(bt*.4)*.012});
  if(COUNTERS.has(b.action)&&isOther)neon(g,cx,cy-r-98,b.count,b.count===0?'#55e1a5':'#ff6574',1.65);
  if(['self','belief','admit'].includes(b.action))neon(g,cx,cy-r-98,b.count,'#ff6574',1.65);
  foreground(g,bt,{z:1},-1);
 }else if(mode==='insert'){
  veil(g,'#060d1c',.55);layer(g,{z:1+.03*q,x:0,y:0},1,g=>insert(g,b,t,info,cam));
 }else{
  layer(g,cam,1,g=>{
   const s=mode==='wide'?1.65:2.3,dist=mode==='wide'?470:620,center=960;
   const sitting=b.set==='bench'||b.action==='share'||b.action==='ending';
   if(sitting)bench(g,1030,940,700);
   const walking=['arrival','follow','reveal','reject'].includes(b.action)&&mode==='wide';
   const rootX=walking?410:Math.max(400,center-dist/2);
   character(g,b,walking?bt:t,rootX,GY,s,0,{walk:walking?35:0,sit:sitting,count:b.action==='crowd'?14003:undefined});
   if(!['self','belief','admit','arrival','question'].includes(b.action)){
    const os=sitting?1.85:s;const otherX=sitting?1215:center+dist/2;
    character(g,b,t,otherX,GY,os,1,{sit:sitting||b.action==='mother',count:b.action==='crowd'?22310:b.action==='door'?(bt<3?9313:9314):b.action==='test'?(bt<3?9311:9312):b.action==='blackout'?(bt<3?null:9311):undefined});
   }
   if(b.action==='talk'){person(g,{x:1530,y:890,s:1.3,facing:-1,outfit:MOTHER,pose:fixed(POSES.sit),expr:'worried',rim:{color:M.rim,dir:[-1,-1]}},t,6811);}
   props(g,b,bt);
   if(b.action==='blackout'){const darkness=bt<2?0:bt<3?1:0;veil(g,'#000',darkness);}
   if(b.action==='share')sandwich(g,960+Math.sin(q*Math.PI)*60,750,1.1);
  });
  if(mode==='ots')foreground(g,bt,cam,-1);
 }
 atmosphere(g,bt,b.set);
 drawCTA(g,info.globalT);
 // Sparse editorial chapter labels, never full narration paragraphs on the image.
 if(info.part===0&&[0,2,5,7,11,18,23,26,29,31].includes(info.beat)){
  const labels={0:'UMA MENTIRA. QUAL HISTÓRIA?',2:'SETE DIAS ANTES',5:'O PRIMEIRO NÚMERO',7:'O PRÓPRIO REFLEXO',11:'APARÊNCIA NÃO É PROVA',18:'A HISTÓRIA QUE FALTAVA',23:'ZERO',26:'A PARTE QUE ERA DELE',29:'E NA VIDA REAL?',31:'VOCÊ GOSTARIA DESSE PODER?'};
  panel(g,85,72,Math.min(1100,labels[info.beat].length*23+70),70,'#101b2be6');text(g,labels[info.beat],120,107,{size:37,align:'left',color:'#f1d284'});
 }
}

// Real 3D establishing shots: short orbits reveal physical depth and return to 2.5D acting.
const threeBeats=new Set([2,10,17,18,23,28,30]);
function threeDef(bi){return {kind:'3d',init(T){
 const b=beats[bi],M=mood(b.set==='hospital'?'interiorCool':'night'),st=T.stage({mood:b.set==='hospital'?'interiorCool':'night',fov:40,fog:[15,65],keyPos:[-4,8,3],keyIntensity:2.4,ambient:1.1,bloom:0});
 st.bloom.enabled=false;st.sun.shadow.mapSize.set(1024,1024);st.composer.renderTarget1.samples=0;st.composer.renderTarget2.samples=0;
 st.add(T.ground(60,60,M.floor));
 if(b.set==='court'){
  st.add(T.box(20,8,.6,M.wall,0,4,-5));for(let i=0;i<7;i++)st.add(T.cyl(.35,.4,6.5,'#5e6274',-8+i*2.6,3.25,-4));for(let i=0;i<4;i++)st.add(T.box(21,.2,3+i*.5,'#42475f',0,.1+i*.2,-2-i*.4));
 }else{
  for(const x of [-9,-5,5,9]){const build=T.building(3,5+Math.abs(x)*.3,4,{color:M.wall,win:M.practical,lit:.5});build.position.set(x,(5+Math.abs(x)*.3)/2,-6);st.add(build);}
  if(b.set==='hospital'){st.add(T.box(10,5,.4,'#3b5265',0,2.5,-5));st.add(T.box(.35,1.5,.1,'#84c9b9',0,3.8,-4.7),T.box(1.5,.35,.1,'#84c9b9',0,3.8,-4.69));}
 }
 // A bench, two lamps, pavement and outfits tie the locations to the acting shots.
 st.add(T.box(3.2,.1,.6,'#72564b',1,.5,.3),T.box(3.2,.6,.1,'#72564b',1,.9,.55));
 for(const x of [-3,4]){st.add(T.cyl(.04,.05,3.4,M.dark,x,1.7,1));st.add(T.box(.4,.45,.4,M.practical,x,3.5,1));}
 const hero=T.figure3D(b.set==='court'?JUDGE:CAIO,{rim:M.rim,pose:POSES.stand,s:1});hero.position.set(-1.5,0,1);hero.rotation.y=Math.PI*.35;st.add(hero);
 const other=T.figure3D(bi===23||bi===30?RUI:b.set==='court'?WITNESS:MARA,{rim:M.rim,pose:POSES.stand,s:1});other.position.set(1.1,0,1);other.rotation.y=-Math.PI*.55;st.add(other);
 return {stage:st,hero,other};
 },draw(s,t,info,T){const q=ease.inOut(t/info.dur);T.orbit(s.stage.camera,t,{target:[0,1.1,0],radius:[10,8.8],height:[3.7,2.8],from:-.35,to:.24,dur:info.dur});s.hero.setPose(idle(t,'stand'));s.other.setPose(idle(t,'stand',3));},overlay(g,t,info){drawCTA(g,info.globalT);if(bi===2)text(g,'SETE DIAS ANTES',960,130,{size:51,color:'#f1d284'});}};}
for(const shot of plan.shots){const bi=shot.params.beat;registerShot(shot.id,shot.params.part===0&&threeBeats.has(bi)?threeDef(bi):{draw:scene});}
