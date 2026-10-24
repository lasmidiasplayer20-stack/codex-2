import {E,registerShot,clamp,lerp,ease,text,seg,circle,rr,alpha,glow} from '/engine/core.js';
import {world} from './world.js';
const beats=await(await fetch('/project/story/beats.json')).json(),story=await(await fetch('/project/story/shots.json')).json();
const q=(x)=>ease.inOut(clamp(x));
function state(x,z,time,more={}){return {x,z,time,yaw:0,headYaw:-.4,moving:false,distance:0,expr:'smile',...more};}
function place(ob,x,y,z){ob.visible=true;ob.position.set(x,y,z);}
function toward(o,p){const dx=p[0]-o.x,dz=p[2]-o.z,c=Math.cos(o.yaw),s=Math.sin(o.yaw);return [dx*c-dz*s,p[1],dx*s+dz*c];}
function update(s,b,bt,dur,T){
 const H=T.THREE,u=clamp(bt/dur),p=q(u),act=b.action;for(const a of Object.values(s.A))a.root.visible=false;for(const [k,v]of Object.entries(s.P)){if(k==='loose'){v.forEach(o=>o.visible=false);continue;}v.visible=false;}
 const P=s.P,actors={nico:state(-1,.8,bt)},n=actors.nico;let focus='nico',object='book',beam=false;
 const add=(id,x,z,opts={})=>(actors[id]=state(x,z,bt+(id==='lia'?.8:0),opts));
 const move=(o,x0,z0,x1,z1,k=p)=>{o.x=lerp(x0,x1,k);o.z=lerp(z0,z1,k);o.distance=Math.hypot(x1-x0,z1-z0)*k;o.moving=u>.025&&u<.965;o.yaw=Math.atan2(-(z1-z0),x1-x0);};
 if(['hook','warning','firsthelp','look','arrival','wrong','creak','support'].includes(act))add('sol',1.0,.5,{yaw:-.7,headYaw:-.1});
 if(['meeting','confide','firsthelp','wrong','map','cart','joke','rain','blackout','lead','stuck','creak','support','turn','relief','question','cleanup','privacy','time','meaning','ending'].includes(act))add('lia',1.1,1.15,{yaw:-.45});
 if(['arrival','joke','rain','blackout','lead','stuck','creak','support','turn','relief','cleanup','ending'].includes(act))add('gui',2.5,1.0,{yaw:-.6});
 switch(act){
 case 'hook':case 'warning':
  n.x=-.35;n.z=.7;n.hand=[.45,1.18,.24];n.expr=u<.38?'smile':'surprised';actors.sol.x=.65;actors.sol.z=1.25;actors.sol.yaw=Math.PI-.3;actors.sol.hand=toward(actors.sol,[.1,1.18,.94]);object='cup';break;
 case 'reveal':move(n,-4,2.1,3.4,2.1);n.expr='surprised';add('sol',1,-.1,{moving:true,distance:bt*.45});add('courier',5-9*p,.8,{yaw:Math.PI,moving:true,distance:p*9,run:true});break;
 case 'mirror':n.x=-4.0;n.z=-2.8;n.yaw=Math.PI/2;n.gesture=u>.35?'surprise':'think';n.expr='surprised';break;
 case 'notes':n.x=-1.8;n.z=-1.08;n.sit=true;n.yaw=-Math.PI/2;n.hand=[.5,.99,.18];n.expr='determined';place(P.paper,-1.3,.97,-.3);object='paper';break;
 case 'oldman':move(n,-4,1.5,-1.8,1.5);add('ari',-.6,.3,{sit:u<.7,yaw:-Math.PI/2,expr:'smile'});add('courier',-5+10*p,2.8,{moving:true,distance:p*10,run:true});break;
 case 'cup':n.x=-.7;n.z=.8;n.hand=[.45,1.2,.19];n.expr=u<.4?'surprised':'joy';add('sol',1.1,.7,{yaw:-.7,expr:'surprised'});object='cup';break;
 case 'meeting':n.x=-1.3;n.z=.7;n.gesture='think';move(actors.lia,4,1.6,.7,1.6);actors.lia.yaw=-.6;actors.lia.hand=u>.55?[.2,1.55,.19]:[.5,.95,.18];place(P.chair,1.0,.0,lerp(.4,1.1,q(u/.4)));P.chair.rotation.y=.4;object='chair';break;
 case 'confide':n.x=-1.2;n.z=.8;n.expr='sad';n.gesture='think';actors.lia.gesture=u>.5?'point':'think';actors.lia.expr=u>.5?'smile':'surprised';break;
 case 'arrival':move(n,-3.5,.9,-1.5,.9);n.hand=[.48,1.12,.18];n.handB=[.48,1.12,-.18];add('sol',1.3,.8,{hand:[.4,1.22,.19],expr:'joy'});break;
 case 'look':n.x=-2.1;n.z=.7;n.gesture='point';n.expr='determined';place(P.box,3.0,2.6,-2);place(P.chair,.3,0,1.2);for(let i=0;i<4;i++)place(P.loose[i],-1+i*.4,.04,.6+(i%2)*.3);break;
 case 'firsthelp':n.x=-1.2+1.4*p;n.z=.8;n.crouch=Math.sin(Math.PI*clamp(u/.55));n.hand=[.45,lerp(.38,1.2,q((u-.2)/.45)),.19];actors.lia.x=1.5;actors.lia.z=1.4;actors.lia.gesture='point';n.expr='determined';object='book';break;
 case 'wrong':n.gesture=u<.4?'surprise':'point';n.expr=u<.4?'surprised':'smile';actors.lia.gesture='think';break;
 case 'map':n.x=-1.5;n.z=.4;n.hand=[.48,1.19,.19];actors.lia.x=.0;actors.lia.z=1.1;actors.lia.gesture='point';place(P.paper,-.8,1.0,.8);object='paper';break;
 case 'cart':{
  const k=u<.4?q(u/.4)*.42:u<.58?.42:lerp(.42,1,q((u-.58)/.42));move(n,-3,.8,1.7,1.3,k);n.yaw=0;n.hand=[.48,1.12,.18];n.handB=[.48,1.12,-.18];actors.lia.x=n.x+2;actors.lia.z=2;actors.lia.gesture='point';n.expr=u>.4&&u<.6?'surprised':'determined';object='cart';break;}
 case 'joke':n.x=-.6;n.z=1;actors.gui.x=.1;actors.gui.z=1.5;actors.gui.yaw=Math.PI-.6;actors.gui.hand=[.4,1.15,.18];n.hand=[.5,lerp(.87,1.17,q((u-.55)/.45)),.19];n.expr='joy';object='toy';break;
 case 'rain':n.x=-2;n.z=1;n.crouch=.65*Math.sin(Math.PI*u);n.hand=[.45,.6+.6*p,.18];actors.lia.x=.0;actors.lia.z=.9;actors.lia.hand=[.45,1.28,.19];actors.gui.x=2;actors.gui.gesture='surprise';beam=true;object='flashlight';break;
 case 'blackout':n.gesture='point';n.expr='surprised';actors.lia.hand=[.4,1.3,.18];actors.gui.x=actors.lia.x+.7;actors.gui.z=1.7;beam=true;object='flashlight';break;
 case 'lead':move(n,-3,.2,3.6,.4);actors.lia.x=n.x+1.0;actors.lia.z=n.z+.35;actors.lia.moving=n.moving;actors.lia.distance=n.distance;actors.lia.hand=[.43,1.25,.18];actors.gui.x=n.x+.1;actors.gui.z=n.z+1;actors.gui.moving=n.moving;actors.gui.distance=n.distance;add('sol',n.x-.7,n.z+.6,{moving:n.moving,distance:n.distance});place(P.chair,-.3+q(u/.4)*2,0,1.5);if(P.door){P.door.visible=true;P.door.rotation.y=-1.4;}beam=true;object='chair';break;
 case 'stuck':n.x=1.8+q((u-.55)/.45)*1.1;n.z=.5;n.hand=[.48,1.12,.18];n.handB=[.48,1.12,-.18];n.expr='determined';actors.lia.x=3.0;actors.lia.z=1.0;actors.lia.crouch=Math.sin(Math.PI*clamp(u/.65));actors.lia.hand=[.4,.4+.8*q((u-.2)/.5),.18];if(P.door){P.door.visible=true;P.door.rotation.y=lerp(-.4,-1.5,p);}object='cart';break;
 case 'creak':n.x=-.7;n.z=.8;n.gesture='surprise';n.expr='surprised';actors.lia.x=.5;actors.lia.z=1.8;actors.lia.gesture='point';actors.gui.x=.8;actors.gui.z=2.5;actors.sol.x=1.5;actors.sol.z=1.2;actors.sol.expr='surprised';object='shelf';break;
 case 'support':n.x=-.7+3.4*p;n.z=.8;n.moving=true;n.distance=3.4*p;n.hand=[.48,1.12,.18];n.handB=[.48,1.12,-.18];actors.lia.x=2+2.2*p;actors.lia.z=1.3;actors.lia.moving=true;actors.lia.distance=2.2*p;actors.lia.gesture='point';actors.sol.x=1.1+2.2*p;actors.sol.z=.6;actors.sol.moving=true;actors.sol.distance=2.2*p;actors.gui.x=actors.lia.x-.3;actors.gui.z=2;add('ari',3,-1.25,{yaw:.7,expr:'determined'});actors.ari.hand=toward(actors.ari,[3.1,1.45,lerp(-1.52,-1.66,p)]);actors.ari.handB=toward(actors.ari,[2.8,1.1,lerp(-1.56,-1.66,p)]);object='shelf';break;
 case 'turn':case 'relief':case 'question':n.x=1.5;n.z=1.0;n.expr=act==='question'?'determined':'surprised';add('sol',-.1,1.1,{expr:'joy',yaw:-.3});actors.lia.x=-1.8;actors.lia.z=.6;actors.lia.hand=[.45,1.2,.18];if(actors.gui){actors.gui.x=-.3;actors.gui.z=2.3;}if(P.door){P.door.visible=true;P.door.rotation.y=-1.5;}if(act==='relief'){n.x=1;n.yaw=Math.PI-.3;n.hand=[.48,1.2,.18];actors.lia.x=lerp(-1.8,0,q(u/.45));actors.lia.z=.6;actors.sol.x=-1;}object=act==='relief'?'cup':'phone';break;
 case 'cleanup':n.x=-.6+1.3*p;n.z=.8;n.moving=true;n.distance=1.3*p;n.hand=[.45,lerp(.85,1.2,q((u-.35)/.35)),.19];actors.lia.x=1.8;actors.lia.z=1.8;actors.lia.hand=[.4,1.1,.18];actors.gui.x=n.x+.8;actors.gui.z=n.z+.35;actors.gui.yaw=Math.PI-.3;actors.gui.hand=[.4,1.1,.18];place(P.box,1.1,.25,1.2);object='book';break;
 case 'privacy':move(n,-2,2.1,2,2.1);actors.lia.x=n.x+1.4;actors.lia.z=1.4;actors.lia.distance=n.distance;actors.lia.moving=n.moving;actors.lia.gesture=u<.5?'point':null;n.hand=[.4,1.0,.18];object='paper';break;
 case 'time':n.x=-2.0;n.z=.3;n.sit=true;n.yaw=-Math.PI/2;add('ari',-.8,.3,{sit:true,yaw:-Math.PI/2,gesture:'point'});actors.lia.x=1.8;actors.lia.z=1.2;break;
 case 'call':n.x=-.8;n.z=.7;n.hand=[.18,1.6,.18];n.expr='smile';object='phone';break;
 case 'fade':n.x=-3.7;n.z=-2.5;n.yaw=.6;n.gesture='think';n.expr='smile';break;
 case 'meaning':n.x=-2;n.z=.3;n.sit=true;n.yaw=-Math.PI/2;actors.lia.x=0;actors.lia.z=.3;actors.lia.sit=true;actors.lia.yaw=-Math.PI/2;break;
 case 'ending':n.x=-1.4;n.z=.3;n.sit=true;n.yaw=-Math.PI/2;n.hand=[.45,.85,.18];actors.lia.x=.4;actors.lia.z=.3;actors.lia.sit=true;actors.lia.yaw=-Math.PI/2;actors.gui.x=-1.7;actors.gui.z=1.07;actors.gui.yaw=Math.PI/2;actors.gui.hand=[.4,1.1,.18];object='toy';break;
 }
 if(P.shelf){P.shelf.visible=true;P.shelf.rotation.x=act==='creak'?lerp(.025,.11,p):act==='support'?lerp(.11,0,p):.025;}
 for(const [id,o]of Object.entries(actors)){s.A[id].root.visible=true;s.A[id].update(o);}
 const hand=(id='nico')=>s.A[id].point(),mhand=hand();
 if(['hook','warning','cup','relief'].includes(act)){
  const who=act==='relief'?(u<.45?'lia':'nico'):['hook','warning'].includes(act)&&u<.32?'sol':'nico';let h=hand(who).clone();if(['hook','warning'].includes(act))h.copy(hand('sol')).lerp(hand('nico'),q((u-.2)/.3));if(act==='relief')h.copy(hand('lia')).lerp(hand('nico'),q((u-.35)/.35));h.z-=.11;
  if(act==='cup'&&u<.35){const k=q(u/.35);h.set(lerp(.45,h.x,k),lerp(1.65,h.y,k)+Math.sin(Math.PI*k)*.15,lerp(.8,h.z,k));}
  place(P.cup,h.x,h.y,h.z);P.cup.rotation.z=act==='cup'?(1-q(u/.35))*.3:0;
 }
 if(['arrival','cart','stuck','support'].includes(act)){place(P.cart,mhand.x+.55,0,actors.nico.z);P.cart.rotation.y=0;}
 if(['firsthelp','cleanup'].includes(act)){const h=act==='cleanup'?hand('gui').clone().lerp(hand('nico'),q((u-.2)/.25)):hand();place(P.book,h.x,h.y+.04,h.z);P.book.rotation.set(0,0,0);}
 if(act==='oldman'){place(P.paper,actors.ari.x+.25,1.0,actors.ari.z+.45);}
 if(act==='privacy'){place(P.paper,mhand.x,mhand.y,mhand.z);P.paper.rotation.z=.15;}
 if(act==='map'){place(P.paper,-.8,1.0,.8);}
 if(['joke','ending'].includes(act)){const h=(act==='joke'?hand('gui').clone().lerp(hand('nico'),q((u-.35)/.3)):hand('nico').clone().lerp(hand('gui'),q((u-.35)/.3)));place(P.toy,h.x,h.y,h.z);P.toy.rotation.z=bt*.2;}
 if(act==='call'){place(P.phone,mhand.x,mhand.y,mhand.z);P.phone.rotation.y=.4;}
 if(act==='stuck'){const h=hand('lia');place(P.book,lerp(2.5,h.x,q(u/.65)),lerp(.08,h.y+.04,q(u/.65)),lerp(.8,h.z,q(u/.65)));}
 if(act==='rain'){for(let i=0;i<3;i++)place(P.loose[i],-1.9+i*.4,.04,-.5);}
 if(act==='meeting'){const h=hand('lia');if(u>.55)place(P.loose[0],h.x,h.y,h.z);}
 if(act==='creak'){for(let i=0;i<4;i++){const k=q(clamp((u-.3-i*.08)/.45));place(P.loose[i],2.2+i*.25,lerp(2.4-i*.22,.07,k),-1.8+k*.75);P.loose[i].rotation.z=k*(i%2?1:-1);}}
 if(beam){const h=hand('lia');place(P.flashlight,h.x,h.y,h.z);P.flashlight.rotation.y=-.35+Math.sin(bt*.7)*.3;}
 const night=act==='blackout'?(u>.25?1:.15):['lead','stuck','creak','support'].includes(act)?.72:['rain','turn','relief','question'].includes(act)?.4:0;s.hemi.intensity=lerp(1.6,.65,night);s.sun.intensity=lerp(2,1.2,night);
 s.motion={actors,u,bt,act,focus,object,beam};return s.motion;
}
function camera(s,info,T){
 const H=T.THREE,b=beats[info.beat],m=s.motion,part=info.part,u=q(info.p),mode=info.cam;let id=(['hook','warning'].includes(b.action)&&mode==='close'&&info.part===1)?'sol':(mode==='reverse'&&m.actors.lia)?'lia':(b.action==='turn'&&['close','detail'].includes(mode))?'sol':'nico';const a=s.A[id],o=m.actors[id]||m.actors.nico,head=a.head.getWorldPosition(new H.Vector3());
 let target=new H.Vector3(o.x,1.05,o.z),off=new H.Vector3(4.0,2.3,6.0),fov=43;
 if(mode==='wide'){target.y=1.15;off.set(5.1,3.0,7.4);}
 if(mode==='two'){const others=Object.entries(m.actors).filter(([k])=>k!=='nico'),b=others.find(([k])=>k==='lia')||others[0];if(b)target.set((m.actors.nico.x+b[1].x)/2,1.12,(m.actors.nico.z+b[1].z)/2);off.set(3.3,1.5,5.3);fov=40;}
 if(mode==='track'){off.set(2.3+u*.4,1.5,5.0);target.y=1.0;fov=42;}
 if(mode==='side'){off.set(1.1,1.0,5.4);fov=40;}
 if(mode==='close'||mode==='reverse'){target.copy(head);target.y+=.1;off.set(1.4,.2,1.9);fov=35;}
 if(mode==='feet'){target.copy(s.A.nico.point('foot'));target.y=.2;off.set(1.8,.65,2.6);fov=38;}
 if(mode==='detail'){
  let ob=s.P[m.object];target.copy(ob&&ob.visible?ob.getWorldPosition(new H.Vector3()):s.A.nico.point());if(m.object==='shelf')target.y=1.7;
  off.set(1.8,.65,2.4);fov=40;
  if(['turn','question'].includes(b.action)){target.copy(s.A.sol.head.getWorldPosition(new H.Vector3()));target.y+=.2;}
  if(m.object==='phone'||m.object==='toy'){off.set(1.1,.3,1.6);fov=37;}if(['joke','ending'].includes(b.action)){off.set(-1.5,.9,-2.2);fov=39;}
 }
 if(mode==='over'){target.set(.2,.15,.0);off.set(.8,10.5,2.0);fov=46;}
 if(mode==='window'){target.set(-3.9,2.0,-3.3);off.set(3.8,.8,4.4);fov=45;}
 if(['time','meaning','ending'].includes(b.action)&&['wide','two'].includes(mode)){target.set(-.9,1.1,.3);off.set(4.2,2.3,6);}
 if(b.action==='mirror'&&mode!=='close'){target.set(-4.0,1.5,-3.2);off.set(2.7,1.1,4);}
 if(['close','reverse'].includes(mode)){for(const [key,ob]of Object.entries(s.A))if(key!==id)ob.root.visible=false;}
 if(mode==='detail'&&m.object!=='shelf'&&!['hook','warning','cup','joke','ending','relief'].includes(b.action)){let nearest=id,best=Infinity;for(const [key,st]of Object.entries(m.actors)){const h=s.A[key].point(),dist=h.distanceTo(target);if(dist<best){best=dist;nearest=key;}}for(const [key,ob]of Object.entries(s.A))if(key!==nearest)ob.root.visible=false;}
 if(['close','reverse'].includes(mode)&&b.action!=='mirror')off.applyAxisAngle(new H.Vector3(0,1,0),o.yaw||0);
 const drift=new H.Vector3(Math.sin(info.globalT*.47)*.09,Math.sin(info.globalT*.59)*.035,Math.cos(info.globalT*.39)*.07);s.camera.position.copy(target).add(off).add(drift);s.camera.fov=fov;s.camera.updateProjectionMatrix();s.camera.lookAt(target);if(s.P.front)s.P.front.visible=s.camera.position.z<target.z-.3;
 // Small head turns preserve readable expressions in oblique views, without rotating the torso or restarting an action.
 for(const [k,st]of Object.entries(m.actors)){const ob=s.A[k],hp=ob.head.getWorldPosition(new H.Vector3()),yaw=Math.atan2(-(s.camera.position.z-hp.z),s.camera.position.x-hp.x)-st.yaw;let turn=Math.atan2(Math.sin(yaw),Math.cos(yaw));ob.head.rotation.y=Math.max(-1.15,Math.min(1.15,turn));ob.root.updateMatrixWorld(true);}
}
function xy(v,s){const a=v.clone().project(s.camera);return [(a.x*.5+.5)*E.W,(-a.y*.5+.5)*E.H,a.z];}
function label(g,txt,x,y,size=36,color='#ffefd0'){text(g,txt,x,y,{size,color,stroke:5,strokeColor:'#20303c'});}
function countdown(s,b){
 const u=s.motion.u,act=b.action;const range={hook:[492,484],warning:[492,480],look:[480,462],firsthelp:[462,469],wrong:[469,451],map:[451,416],cart:[416,391],joke:[391,371],rain:[371,331],blackout:[331,271],lead:[271,216],stuck:[216,126],creak:[126,31],support:[31,2]};
 if(act==='arrival')return u>.7?'00:08:12':null;if(act==='turn'&&u<.4)return '00:00:02';if(['turn','relief','question','cleanup','privacy','time','call','fade','meaning','ending'].includes(act))return '37 ANOS';if(!range[act])return '43 ANOS';const t=Math.max(0,Math.round(lerp(...range[act],u)));return `00:${String(Math.floor(t/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')}`;
}
function clocks(g,s,b){
 if(b.action==='mirror'||b.action==='call'||b.action==='notes'||b.action==='fade')return;const boxes=[],heads=[];for(const [key,st]of Object.entries(s.motion.actors)){if(!s.A[key].root.visible)continue;const hp=s.A[key].head.getWorldPosition(new (s.A[key].root.position.constructor)()),center=xy(hp,s),top=xy(hp.clone().add(new (hp.constructor)(0,.255*(key==='gui'?.73:1),0)),s);heads.push({x:center[0],y:center[1],r:Math.abs(center[1]-top[1])+9});}
 for(const [id,st]of Object.entries(s.motion.actors)){if(id==='nico'||!s.A[id].root.visible)continue;const head=s.A[id].head.getWorldPosition(new (s.A[id].root.position.constructor)());head.y+=.38;let [x,y,z]=xy(head,s);if(z>1||x<60||x>1860||y>1060)continue;let txt=id==='sol'?countdown(s,b):({lia:'47 ANOS',gui:'79 ANOS',ari:'52 ANOS',courier:'18 ANOS'})[id];if(!txt)continue;
  let w=txt.includes(':')?244:206,h=55;x=Math.max(w/2+35,Math.min(1885-w/2,x));y=Math.max(70,Math.min(950,y));const original=[x,y];for(let pass=0;pass<6;pass++){for(const head of heads)if(Math.abs(x-head.x)<w/2+head.r&&Math.abs(y-head.y)<h/2+head.r+8)y=head.y-head.r-h/2-12;for(const box of boxes)if(Math.abs(x-box.x)<(w+box.w)/2+10&&Math.abs(y-box.y)<65)y=box.y-68;}y=Math.max(65,y);boxes.push({x,y,w});
  const danger=txt.includes(':'),blink=danger&&s.motion.act==='support'?.8+.2*Math.sin(s.motion.bt*6):1;g.save();g.globalAlpha=blink;if(Math.abs(y-original[1])>20)seg(g,[[x,y+27],original],2,alpha('#9fc5bc',.65));rr(g,x-w/2,y-h/2,w,h,13);g.fillStyle=danger?'#6d253bef':'#183e3bef';g.fill();g.lineWidth=2;g.strokeStyle=danger?'#ed998b':'#68cda8';g.stroke();text(g,txt,x,y,{size:31,color:danger?'#ffd7b8':'#a8f2cb'});g.restore();
 }
}
function cta(g,t){let start=[43,247,495].find(x=>t>=x&&t<x+(x===495?14.3:8));if(start===undefined)return;const k=t-start,a=Math.min(1,k/.35,(start===495?14.3:8)-k),x=420,y=926;g.save();g.globalAlpha=a;rr(g,x,y,1080,124,24);g.fillStyle='#172b3bea';g.fill();circle(g,x+68,y+62,38,'#5edac3');text(g,'E',x+68,y+62,{size:47,color:'#173347'});text(g,'Então',x+130,y+43,{size:41,color:'#fff0d9',align:'left'});text(g,'Uma pergunta, outra história',x+130,y+86,{size:24,color:'#d6e2df',align:'left'});rr(g,x+580,y+29,330,66,15);g.fillStyle=k>2.8?'#32635f':'#d77963';g.fill();text(g,k>2.8?'✓ INSCRITO':'INSCREVA-SE',x+745,y+62,{size:31,color:'#fff4de'});seg(g,[[x+978,y+41],[x+967,y+78],[x+1006,y+78],[x+996,y+41],[x+986,y+35],[x+978,y+41]],4,k>4.1?'#e7ca87':'#d4dfdc');if(k>2.0&&k<4.1){g.fillStyle='#fff6e5';g.beginPath();g.moveTo(x+750,y+69);g.lineTo(x+750,y+104);g.lineTo(x+760,y+94);g.lineTo(x+773,y+110);g.lineTo(x+780,y+104);g.lineTo(x+767,y+89);g.lineTo(x+781,y+86);g.closePath();g.fill();}g.restore();}
function overlay(g,t,info,s){
 const b=beats[info.beat],m=s.motion;clocks(g,s,b);
 if(m.beam&&s.A.lia.root.visible){const h=s.A.lia.point(),from=xy(h,s),v=h.clone();v.x+=3;v.y-=.6;v.z-=.4;const to=xy(v,s),gradient=g.createLinearGradient(from[0],from[1],to[0],to[1]);gradient.addColorStop(0,'#fff1ba3b');gradient.addColorStop(1,'#fff1ba03');g.fillStyle=gradient;g.beginPath();g.moveTo(...from.slice(0,2));g.lineTo(to[0],to[1]-120);g.lineTo(to[0],to[1]+120);g.closePath();g.fill();}
 if(['rain','blackout','lead','stuck','creak','support'].includes(b.action)){for(let i=0;i<26;i++){const x=((-info.globalT*72+i*79)%1920+1920)%1920,y=(info.globalT*390+i*117)%1080;seg(g,[[x,y],[x-4,y+18]],1.1,alpha('#c9dfeb',.12));}}
 for(let i=0;i<14;i++){const x=(i*151+Math.sin(info.globalT*.3+i)*20)%1920,y=90+(i*67+info.globalT*6)%850;circle(g,x,y,1.8,alpha('#f8e4b4',.12));}
 if(b.action==='reveal'&&info.part===0){label(g,'E SE VOCÊ ENXERGASSE',960,115,47);label(g,'QUANTO TEMPO RESTA?',960,182,63,'#8ce6c9');}
 if(b.action==='notes'&&info.part===2){label(g,'UMA HIPÓTESE DE FICÇÃO',960,125,42);label(g,'OBSERVAÇÃO ≠ CERTEZA',960,900,38);}
 if(b.action==='map'&&['over','detail'].includes(info.cam)){
  g.save();g.globalAlpha=.9;rr(g,570,230,780,500,25);g.fillStyle='#17394ce8';g.fill();const pts=[[700,565],[925,565],[925,390],[1210,390]];g.setLineDash([16,10]);seg(g,pts,8,'#82d8bd');g.setLineDash([]);for(const [i,p]of pts.entries()){circle(g,...p,15,i===3?'#efb77b':'#8ae3c5');}text(g,'SALA',730,620,{size:30,color:'#fff0cf'});text(g,'CORREDOR',1020,455,{size:30,color:'#fff0cf'});text(g,'SAÍDA',1200,325,{size:32,color:'#d7f9d9'});g.restore();
 }
 if(b.action==='blackout'&&m.u>.23&&m.u<.29){g.fillStyle=alpha('#0a1726',.3);g.fillRect(0,0,1920,1080);}
 if(b.action==='turn'&&m.u>.4&&m.u<.6){const p=(m.u-.4)/.2;glow(g,960,240,170,'#74d7bb',(1-p)*.25);}
 if(b.action==='fade'){const a=clamp(1-m.u*1.6);g.save();g.globalAlpha=a;label(g,'00:00',960,180,48,'#8de2c7');g.restore();}
 cta(g,info.globalT);
}
for(const shot of story.shots){registerShot(shot.id,{kind:'3d',init(T){return world(T,beats[shot.params.beat].set);},draw(s,t,info,T){const b=beats[info.beat];update(s,b,info.globalT-b.start,b.end-b.start,T);camera(s,info,T);},overlay(g,t,info,s){overlay(g,t,info,s);}});}
