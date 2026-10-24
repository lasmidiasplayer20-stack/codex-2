import {E,S,registerShot,clamp,lerp,ease,text,seg,circle,alpha,rr,glow} from '/engine/core.js';
import {world} from './world.js';
const beats=await(await fetch('/project/story/beats.json')).json(),plan=await(await fetch('/project/story/shots.json')).json();
const curves=new Map();const CUTS=[0,.23,.43,.60,.78,1];
const ROUTES={sprint:[[-12,0],[4,0],[28,0]],test:[[-10,0],[22,0],[26,3],[12,4],[3,2]],commute:[[-18,0],[3,0],[24,0]],steps:[[-10,0],[0,0],[12,0]],brake:[[-13,0],[7,0],[19,0]],turn:[[-13,0],[0,0],[12,1],[15,6],[8,8],[-2,5],[2,2]],train:[[-3,.8],[0,.8],[3,1.2],[1,1.8]],challenge:[[-10,0],[2,.7],[5,.7],[8,-.7],[12,.7],[18,0]],finish:[[8,-.7],[11,.8],[12.5,.6],[17,0]],race:[[-10,0],[8,0],[12,3],[0,3],[-6,1]],serve:[[-3,.9],[0,.9],[2,.9]],help:[[-8,1],[-1,1],[4,1],[9,1]]};
function route(T,key,u){
 if(!curves.has(key))curves.set(key,new T.THREE.CatmullRomCurve3(ROUTES[key].map(([x,z])=>new T.THREE.Vector3(x,0,z)),false,'centripetal'));
 const c=curves.get(key),v=c.getPointAt(clamp(u)),d=c.getTangentAt(clamp(u));return {x:v.x,z:v.z,yaw:Math.atan2(-d.z,d.x),distance:c.getLength()*clamp(u)};
}
function pos(ob,x,y,z){ob.position.set(x,y,z);ob.visible=true;}
function reset(s){for(const a of Object.values(s.A))a.root.visible=false;for(const k of ['cup','extraCup','thirdCup','ball','toast','tray','bus'])if(s.props[k])s.props[k].visible=false;for(const a of s.props.paper)a.visible=false;for(const a of s.props.birds)a.root.visible=false;for(const a of s.props.cones)a.visible=false;}
function setup(T,s,b,bt,dur){
 reset(s);const u=clamp(bt/dur),p=ease.inOut(u),H=T.THREE;let n={x:0,z:.7,yaw:0,distance:0,moving:false,run:false,expr:'smile',time:bt},l={x:3,z:1.4,yaw:Math.PI,distance:0,moving:false,expr:'smile',headYaw:.85,time:bt+.7};
 s.A.nico.root.visible=true;
 if(ROUTES[b.action]){const q=b.action==='race'?Math.min(1,u*1.2):p;Object.assign(n,route(T,b.action,q),{moving:u>.035&&u<.965,run:true,expr:'determined'});}
 if(['test','brake','challenge','finish','race','ball','friend','question','sunset'].includes(b.action))s.A.lia.root.visible=true;
 if(b.action==='test'){l.x=-10+p*3;l.z=2;l.moving=u<.8;l.distance=p*3;l.expr=u>.35?'surprised':'smile';}
 if(b.action==='race'){l.x=-10+p*4;l.z=1.4;l.moving=true;l.distance=p*4;if(u>.8){n.x=l.x-.7;n.z=l.z-.9;n.yaw=0;n.run=false;n.distance=l.distance;}}
 if(b.action==='brake'){l.x=4;l.z=2;if(u>.55){n.run=false;n.gesture='surprise';n.expr='surprised';}}
 if(b.action==='catch'){
  n.x=-.9;n.z=.7;n.hand=[.45,1.13,.19];n.expr=u<.18?'surprised':'joy';s.A.lia.root.visible=true;l.x=1.7;l.z=.8;l.expr=u<.32?'smile':'surprised';
 }
 if(b.action==='morning'){n.x=-.8;n.z=.8;n.hand=[.44,1.2,.19];n.expr='joy';}
 if(b.action==='serve'){n.hand=[.55,1.17,.19];s.A.sol.root.visible=true;s.A.sol.update({x:1.5,z:-1.1,yaw:-.9,moving:false,expr:'surprised',time:bt});}
 if(b.action==='birds'){n.x=-4+10*p;n.z=1;n.distance=10*p;n.moving=true;}
 if(['ball','ballroad','intercept','replay'].includes(b.action)){
  if(b.action==='ball'){n.x=-1;n.z=1;n.hand=[.45,1.25,.19];l.x=3;l.z=1.5;l.gesture='point';}
  else{n.x=lerp(-6,.7,ease.inOut(clamp((u-.08)/.52)));n.z=.5;n.distance=n.x+6;n.moving=u>.08&&u<.6;n.run=true;n.expr='determined';l.x=3.6;l.z=1.5;l.gesture=u>.4?'point':null;s.A.lia.root.visible=true;s.A.gui.root.visible=true;s.A.gui.update({x:3,z:lerp(1.5,.5,Math.min(p,.7)),yaw:Math.PI/2,moving:u<.55,distance:p,expr:'surprised',time:bt});}
 }
 if(b.action==='wind'){n.x=-1+3*p;n.z=.8;n.distance=3*p;n.moving=true;n.gesture='surprise';n.expr='surprised';}
 if(b.action==='heat'){n.x=-1;n.z=.8;n.expr='tired';n.nod=.08*Math.sin(bt);n.gesture='think';}
 if(b.action==='hungry'){n.x=-2.2;n.z=.7;n.hand=[.42,1.25,.19];n.expr='joy';s.A.sol.root.visible=true;s.A.sol.update({x:1,z:-1.5,yaw:-1,moving:false,gesture:'point',time:bt});}
 if(b.action==='friend'){n.x=2.1;n.z=2.8;n.sit=true;n.yaw=-Math.PI/2;l.yaw=-Math.PI/2;l.headYaw=-.65;n.expr=u<.4?'joy':'sad';l.x=3.7;l.z=2.8;l.sit=true;l.expr=u<.3?'smile':'sad';}
 if(['challenge','finish'].includes(b.action)){n.hand=[.47,1.18,.19];for(const x of s.props.cones)x.visible=true;l.x=18;l.z=2;l.expr='joy';}
 if(['sunset','question'].includes(b.action)){n.x=-1;n.z=1.3;n.sit=true;n.yaw=-Math.PI/2;l.yaw=-Math.PI/2;l.headYaw=-.65;n.expr='smile';l.x=1;l.z=1.3;l.sit=true;l.expr='smile';}
 s.A.nico.update(n);if(s.A.lia.root.visible)s.A.lia.update(l);
 const hand=s.A.nico.point(),foot=s.A.nico.point('foot');
 if(['catch','morning','serve','challenge','finish','hungry','sunset','question'].includes(b.action)){
  const cup=s.props.cup;cup.visible=true;
  if(b.action==='catch'){const k=ease.inOut(clamp(u/.23));cup.position.set(lerp(-.45,hand.x,k),lerp(1.65,hand.y+.13,k),lerp(.89,hand.z,k));cup.rotation.z=(1-k)*.35;}
  else if(b.action==='morning'){s.props.toast.visible=true;s.props.toast.position.set(hand.x,hand.y+.1+Math.sin(Math.PI*clamp(u/.3))*.6,hand.z);cup.visible=false;}
  else if(b.action==='serve'){
   pos(s.props.tray,hand.x,hand.y+.02,hand.z);s.props.tray.rotation.y=n.yaw;for(const [i,c]of [s.props.cup,s.props.extraCup,s.props.thirdCup].entries()){const dx=(i-1)*.235;pos(c,hand.x+dx*Math.cos(n.yaw),hand.y+.145,hand.z-dx*Math.sin(n.yaw));}
  }else{cup.position.set(hand.x,hand.y+.13,hand.z);cup.rotation.z=['challenge','finish'].includes(b.action)?Math.sin(bt*4)*.04:0;}
 }
 if(['ball','ballroad','intercept','replay'].includes(b.action)){
  const ob=s.props.ball;ob.visible=true;
  if(b.action==='ball'){const k=clamp(u/.55),v=new H.Vector3(lerp(3,hand.x,k),lerp(1.4,hand.y+.15,k)+Math.sin(Math.PI*k)*1.1,lerp(1.5,hand.z,k));ob.position.copy(v);}
  else{const stop=u>.6;ob.position.set(stop?foot.x+.24:lerp(3,foot.x+.24,ease.inOut(clamp(u/.6))),.17,stop?foot.z:lerp(1.4,foot.z,ease.inOut(clamp(u/.6))));if(s.props.bus){pos(s.props.bus,lerp(-45,35,p),0,-4.5);}}
  ob.rotation.z=-bt*4;
 }
 if(['birds','wind','help'].includes(b.action)){
  for(let i=0;i<s.props.paper.length;i++){const ob=s.props.paper[i],slow=b.action==='birds'?.08:1;pos(ob,n.x-2+(i*.73+bt*slow)%5,.4+(i%4)*.38-Math.sin(bt*slow+i)*.2,.5+(i%3)*.35);ob.rotation.set(bt*.3+i,.4*i,Math.sin(bt+i)*.5);}
 }
 if(b.action==='birds')for(const [i,a]of s.props.birds.entries()){pos(a.root,-1+i*.6,1.1+i*.13,1.2+(i%2)*.8);a.wingL.rotation.x=Math.sin(bt*.9+i)*.4;a.wingR.rotation.x=-a.wingL.rotation.x;}
 // Store real actor world state for all camera cuts; moving props never reset at a cut.
 s.motion={n,l,u,bt,hand,foot};return s.motion;
}
function cam(s,info,T){
 const b=beats[info.beat],m=s.motion,H=T.THREE,local=clamp((info.globalT-b.start)/(b.end-b.start)),q=ease.inOut(info.p),hero=new H.Vector3(m.n.x,.95,m.n.z),c=s.camera;
 let target=hero.clone(),offset=new H.Vector3(5.8,2.8,7.8),fov=43;
 const n=info.cam;
 if(n==='wide'){offset.set(5.5,3.3,7.5);target.y=.7;}
 if(n==='track'){offset.set(2.4+q,1.9,6.9);target.y=1.0;}
 if(n==='front'){offset.set(6,1.2,3.1);target.y=1.25;fov=39;}
 if(n==='feet'){target.copy(m.foot);target.y=.14;offset.set(1.8,.55,2.2);fov=39;}
 if(n==='close'){target.copy(s.A.nico.head.getWorldPosition(new H.Vector3()));offset.set(1.35,.18,1.65);fov=35;}
 if(n==='detail'){target.copy(['ballroad','intercept','replay'].includes(b.action)?s.props.ball.position:m.hand);offset.set(1.4,.65,1.65);fov=38;}
 if(n==='aerial'){offset.set(.6,15.0,.8);target.y=0;fov=46;}
 if(n==='orbit'||n==='slow'){const a=lerp(-.55,.65,q);offset.set(7*Math.sin(a)+2.3,2.4,7*Math.cos(a));target.y=1.05;}
 if(['friend','sunset','question'].includes(b.action)&&['wide','orbit'].includes(n)){target.set((m.n.x+m.l.x)/2,1.1,m.n.z);offset.set(3.8,2.1,5.5);}
 if(b.action==='race'&&n==='close')offset.z=-1.65;
 if(n==='detail'&&['catch','hungry','question','sunset'].includes(b.action)){target.y+=.22;offset.set(1.7,.6,2.2);}
 if(['front','close','feet','detail'].includes(n))offset.applyAxisAngle(new H.Vector3(0,1,0),m.n.yaw||0);
 const drift=new H.Vector3(.1*Math.sin(info.globalT*.6),.035*Math.sin(info.globalT*.8),.06*Math.cos(info.globalT*.7));c.position.copy(target).add(offset).add(drift);c.fov=fov;c.updateProjectionMatrix();c.lookAt(target);
}
function projected(p,s){const v=p.clone().project(s.camera);return [(v.x*.5+.5)*E.W,(-v.y*.5+.5)*E.H];}
function label(g,txt,x,y,color='#ffe3a1',size=45){text(g,txt,x,y,{size,color,stroke:5,strokeColor:'#263446',glow:6,glowColor:'#415366'});}
function overlay(g,t,info,s){
 const b=beats[info.beat],m=s.motion,fast=['sprint','test','commute','steps','brake','turn','wind','challenge','finish','race','intercept'].includes(b.action),slow=info.cam==='slow';
 if(fast&&m.u>.05&&m.u<.92){for(let i=0;i<20;i++){const y=110+(i*83)%850,x=((i*251-info.globalT*900)%2400+2400)%2400-240;seg(g,[[x,y],[x+70+(i%4)*35,y]],1.5+i%2,alpha(i%3?'#fff9e9':'#258f86',.24));}}
 if(fast&&curves.has(b.action)&&m.u>.08&&m.u<.85){const c=curves.get(b.action),V=m.hand.constructor;for(let i=4;i>=1;i--){const v=c.getPointAt(ease.inOut(clamp(m.u-i*.012)));const h=projected(v.clone().add(new V(0,1.7,0)),s),hip=projected(v.clone().add(new V(0,.94,0)),s),f=projected(v.clone().add(new V(0,.07,0)),s);g.strokeStyle=alpha('#36bdb0',.14-i*.02);g.lineWidth=5;g.beginPath();g.arc(h[0],h[1],12,0,Math.PI*2);g.stroke();seg(g,[h,hip,f],5,alpha('#36bdb0',.14-i*.02));}}
 if(['feet','track'].includes(info.cam)&&fast){const [x,y]=projected(m.foot,s);for(let i=0;i<5;i++){const age=(t*3+i*.2)%1;circle(g,x-age*110,y-age*15,3+age*9,alpha('#e7dbbc',(1-age)*.14));}}
 if(b.action==='heat'){const [x,y]=projected(m.foot,s);glow(g,x,y,85,'#f2b56b',.3);for(let i=0;i<5;i++){const xx=x-60+i*25;seg(g,[[xx,y-15],[xx+Math.sin(info.globalT*3+i)*10,y-70]],3,alpha('#ffdd96',.45));}label(g,'ENERGIA → CALOR',960,130);}
 if(slow)label(g,'UM INSTANTE, POR DENTRO',960,120,'#e0f9ed',36);
 if(b.action==='sprint'&&info.part===0){label(g,'E SE VOCÊ FOSSE',960,125,'#fff5d8',46);label(g,'10× MAIS RÁPIDO?',960,195,'#67e5d0',72);}
 if(b.action==='test')label(g,'MESMA DISTÂNCIA • OUTRO RITMO',960,110,'#fff0d1',37);
 if(b.action==='brake')label(g,'CHEGAR É UMA COISA. PARAR É OUTRA.',960,115,'#ffdda5',39);
 if(b.action==='train'||b.action==='challenge')label(g,'CONTROLE > PRESSA',960,118,'#fff0d1',40);
 if(b.action==='replay')label(g,'ESCOLHER ANTES DE CORRER',960,120,'#fff0d1',41);
 if(info.cam==='aerial'){g.save();g.setLineDash([13,10]);
  const c=curves.get(b.action);if(c){const pts=[];for(let i=0;i<=32;i++)pts.push(projected(c.getPointAt(i/32).add(new (c.getPointAt(0).constructor)(0,.03,0)),s));seg(g,pts,5,alpha('#efb96d',.75));}
  else if(['ballroad','intercept','replay'].includes(b.action)){for(const [pts,col]of [[[[ -6,.03,.5],[.7,.03,.5]],'#5cdac2'],[[[3,.03,1.4],[1,.03,.5]],'#f1c37b'],[[[-8,.03,-4.5],[8,.03,-4.5]],'#97c9eb']])seg(g,pts.map(p=>projected(new (s.motion.hand.constructor)(...p),s)),5,col);}
  g.setLineDash([]);const a=projected(s.A.nico.root.position.clone(),s);g.strokeStyle='#fff6d8';g.lineWidth=3;g.beginPath();g.arc(a[0],a[1],14+Math.sin(t*3)*3,0,Math.PI*2);g.stroke();label(g,'VISÃO DE CIMA',960,160,'#fff0d1',40);g.restore();}
 drawCTA(g,info.globalT);
}
function drawCTA(g,t){
 const ranges=[[43,51],[247,255],[495,509.3]],r=ranges.find(([a,z])=>t>=a&&t<z);if(!r)return;const k=t-r[0],dur=r[1]-r[0],a=ease.out(clamp(k/.5))*(1-ease.in(clamp((k-dur+.5)/.5))),x=420,y=926+(1-a)*175;
 g.save();g.globalAlpha=a;rr(g,x,y,1080,124,25);g.fillStyle='#172a39ed';g.fill();circle(g,x+68,y+62,38,'#5edac3');text(g,'E',x+68,y+62,{size:47,color:'#173347'});text(g,'Então',x+130,y+43,{size:41,color:'#fff0d9',align:'left'});text(g,k<2.8?'Curtiu essa hipótese?':'Tem mais no Então',x+130,y+86,{size:24,color:'#cfdee7',align:'left'});
 rr(g,x+580,y+29,330,66,15);g.fillStyle=k>2.8?'#32635f':'#da765f';g.fill();text(g,k>2.8?'✓ INSCRITO':'INSCREVA-SE',x+745,y+62,{size:31,color:'#fff5e9'});
 const bx=x+995,by=y+60;g.strokeStyle=k>4?'#f2d591':'#e6efef';g.lineWidth=4;g.beginPath();g.arc(bx,by-5,17,Math.PI,0);g.lineTo(bx+19,by+15);g.lineTo(bx-19,by+15);g.closePath();g.stroke();circle(g,bx,by+22,3,'#e5eceb');if(k>4){for(const z of [-1,1])seg(g,[[bx+z*28,by-17],[bx+z*33,by],[bx+z*28,by+15]],3,'#f2d591');}
 if(k>1.4&&k<4.7){const px=lerp(x+820,x+755,ease.out(clamp((k-1.4)/1.3)));g.beginPath();g.moveTo(px,y+65);g.lineTo(px,y+104);g.lineTo(px+13,y+91);g.lineTo(px+23,y+111);g.lineTo(px+30,y+105);g.lineTo(px+18,y+86);g.lineTo(px+35,y+85);g.closePath();g.fillStyle='#fff';g.fill();}g.restore();
}
function diagram(g,t,info){
 const b=beats[info.beat],bt=info.globalT-b.start,u=clamp(bt/(b.end-b.start)),part=info.part;
 g.fillStyle='#142b42';g.fillRect(0,0,E.W,E.H);for(let x=0;x<1920;x+=70)seg(g,[[x,0],[x,1080]],1,'#1d3a54');for(let y=0;y<1080;y+=70)seg(g,[[0,y],[1920,y]],1,'#1d3a54');
 const titles={ratio:'DEZ VEZES É UMA PROPORÇÃO',body:'UM PACOTE IMPOSSÍVEL',energy:'VELOCIDADE 10× • ENERGIA 100×',stop:'A PARADA COMEÇA ANTES DO FREIO',radius:'CURVAS TAMBÉM TÊM LIMITES',drag:'O AR NÃO ESTÁ VAZIO',recap:'VELOCIDADE NÃO É TUDO'};label(g,titles[b.action],960,140,'#fff0cf',56);
 function runner(x,y,scale=1,col='#71e0c9'){circle(g,x,y-95*scale,19*scale,col);seg(g,[[x,y-75*scale],[x-8*scale,y-28*scale]],6*scale,col);const q=Math.sin(bt*7)*16*scale;seg(g,[[x-8*scale,y-28*scale],[x+q,y]],6*scale,col);seg(g,[[x-8*scale,y-28*scale],[x-q,y]],6*scale,col);seg(g,[[x-2*scale,y-64*scale],[x+27*scale,y-50*scale]],6*scale,col);}
 const point=(x,y,c='#f4c782')=>circle(g,x,y,11,c);
 if(b.action==='ratio'){
  for(let i=0;i<2;i++){const yy=420+i*280;seg(g,[[260,yy],[1670,yy]],4,'#799baa');const progress=clamp((bt%7)/7)*(i?1:.1),xx=300+progress*1280;runner(xx,yy,1.1,i?'#71e0c9':'#d6e4eb');label(g,i?'50 m/s = 180 km/h':'5 m/s',360,yy-150,i?'#71e0c9':'#e5eff3',48);}
  label(g,'MESMA DISTÂNCIA • EXEMPLO ILUSTRATIVO',960,870,'#d4e5ed',37);
 }else if(b.action==='energy'){
  runner(330,700,2,'#c5e0e4');runner(1030,700,2,'#71e0c9');
  const count=Math.round(ease.inOut(clamp((bt-.6)/4))*100);for(let i=0;i<100;i++){const x=1300+(i%10)*25,y=310+Math.floor(i/10)*25;rr(g,x,y,18,18,3);g.fillStyle=i<count?'#f0c179':'#254258';g.fill();}
  rr(g,580,550,38,38,5);g.fillStyle='#f0c179';g.fill();label(g,'1×',600,640,'#f1d49e',47);label(g,'100×',1420,640,'#f1d49e',56);label(g,'E = ½ m v²',960,815,'#d4e5ed',55);
 }else if(b.action==='body'){
  const xs=[410,960,1510],names=['PERCEBER','PENSAR','COORDENAR'];
  for(let i=0;i<3;i++){circle(g,xs[i],470,92,'#22465d');label(g,names[i],xs[i],650,'#71e0c9',42);if(i<2){seg(g,[[xs[i]+110,470],[xs[i+1]-110,470]],7,'#7dafbb');point(lerp(xs[i]+110,xs[i+1]-110,(bt*.65)%1),470);}}
  circle(g,410,470,35,'#d8eced');circle(g,410,470,12,'#142b42');for(let j=0;j<4;j++){g.strokeStyle='#e9d7a8';g.lineWidth=5;g.beginPath();g.arc(950+j*8,470,30+j*4,-1.6,1.5);g.stroke();}runner(1510,540,1.3,'#d8eced');label(g,'NA FANTASIA, TUDO ACOMPANHA',960,840,'#d4e5ed',39);
 }else if(b.action==='stop'){
  const names=['PERCEBER','FREAR'];for(let i=0;i<2;i++){let y=385+i*260;label(g,names[i],300,y-80,'#d8e6eb',42);seg(g,[[300,y],[1640,y]],5,'#607f92');const len=i?1140:500;const x=300+len*ease.out(clamp((bt-i*.7)/5));point(x,y,i?'#e8a37b':'#71e0c9');runner(x,y-10,.8);}
  label(g,'10× NA REAÇÃO • ATÉ 100× NA FRENAGEM',960,855,'#f0d5a6',42);label(g,'MESMA DESACELERAÇÃO • MODELO IDEALIZADO',960,920,'#bfd9e3',29);
 }else if(b.action==='radius'){
  for(const [x,r,c]of [[430,115,'#dae8ee'],[1260,280,'#71e0c9']]){g.strokeStyle=c;g.lineWidth=7;g.beginPath();g.arc(x,620,r,Math.PI,Math.PI*2);g.stroke();const angle=Math.PI+Math.PI*((bt*.11)%1);point(x+Math.cos(angle)*r,620+Math.sin(angle)*r,c);seg(g,[[x,620],[x+r,620]],2,c);}
  label(g,'MENOR',430,735,'#d5e7ed',37);label(g,'MAIOR',1260,735,'#71e0c9',43);label(g,'RAIO ∝ v² • MESMA ACELERAÇÃO LATERAL',960,860,'#e9d5ac',38);label(g,'DIAGRAMA FORA DE ESCALA',960,920,'#bfd9e3',29);
 }else if(b.action==='drag'){
  runner(960,675,2.4,'#71e0c9');for(let i=0;i<18;i++){const x=180+((i*179-bt*320)%1600+1600)%1600,y=300+(i%8)*60;seg(g,[[x,y],[x+80+part*12,y]],3,'#8bb8c8');}
  label(g,'ARRASTO ≈ v²',440,795,'#e9d5ac',45);label(g,'POTÊNCIA ≈ v³',1430,795,'#e9d5ac',45);label(g,'MESMA FORMA E CONDIÇÕES • MODELO SIMPLIFICADO',960,920,'#bfd9e3',30);
 }else{
  const names=['PERCEPÇÃO','CONTROLE','CONVIVÊNCIA'];for(let i=0;i<3;i++){const x=390+i*570;rr(g,x-220,330,440,340,20);g.fillStyle=part===i+1?'#31556a':'#223f55';g.fill();label(g,names[i],x,730,'#71e0c9',38);if(i===0){circle(g,x,480,44,'#d4e9ed');point(x+Math.sin(bt)*18,480,'#142b42');}if(i===1){seg(g,[[x-100,530],[x-30,410],[x+110,500]],7,'#e9d3a7');point(x-100+((bt*.4)%1)*210,490);}if(i===2){runner(x-55,560,1.1);runner(x+70,560,1.1,'#bc9fe2');}}
  label(g,'A ESCOLHA AINDA É SUA',960,870,'#e9d5ac',43);
 }
 drawCTA(g,info.globalT);
}
for(const shot of plan.shots){const b=beats[shot.params.beat];if(b.set==='diagram'){registerShot(shot.id,{draw:diagram});continue;}
 registerShot(shot.id,{kind:'3d',init(T){return world(T,b.set);},draw(s,t,info,T){const beat=beats[info.beat];setup(T,s,beat,info.globalT-beat.start,beat.end-beat.start);cam(s,info,T);},overlay});}
