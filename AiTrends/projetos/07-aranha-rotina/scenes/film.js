import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {world} from './world.js';
const beats=await(await fetch('/project/story/beats.json')).json(),story=await(await fetch('/project/story/shots.json')).json();
const q=x=>ease.inOut(clamp(x)),lerp=(a,b,t)=>a+(b-a)*t;
const positions={bed:[-5.8,.9,-.7],cup:[2,.85,2],card:[2.5,.85,2],notebook:[2.6,.86,1.8],map:[2.2,.86,2],remote:[4.95,1.08,0],phone:[2.8,1.13,2],sock:[3.2,.05,1.1],chair:[5.4,0,1],plant:[-4.6,1.4,-3],switch:[6.15,.83,.8],plug:[5.1,.08,-2],cushion:[4.5,.85,-.1]};
function local(o,v){const x=v[0]-o.x,z=v[2]-o.z,c=Math.cos(o.yaw),s=Math.sin(o.yaw);return [x*c-z*s,v[1],x*s+z*c];}
function animate(s,b,t,d){const u=clamp(t/d),p=q(u),P=s.P,act=b.action;for(const ob of s.hidden||[])ob.visible=true;s.hidden=[];for(const a of Object.values(s.A))a.root.visible=true;for(const [id,v]of Object.entries(positions)){P[id]?.position.set(...v);}P.cup.rotation.set(0,0,0);P.card.rotation.set(0,0,0);P.phone.rotation.set(0,0,0);P.cushion.rotation.set(0,0,0);P.bigShadow.visible=false;P.wire.visible=false;P.map.visible=false;P.books.visible=false;P.phone.visible=false;P.torch.visible=false;P.notebook.visible=false;P.sock.visible=false;P.card.visible=true;P.spider.visible=true;for(const c of P.cards)c.visible=false;
 s.lampLight.intensity=7;s.warm.intensity=12;P.bulb.visible=true;
 const A={nico:{x:-3.5,z:1,time:t,yaw:-.55,headYaw:0,moving:false,distance:0,expr:'surprised'},lia:{x:-.8,z:1.2,time:t,yaw:-2.4,headYaw:0,moving:false,distance:0,expr:'smile'}};s.A.lia.root.visible=true;let sp=[-5.1,1.4,-3.18],spyaw=0,wall=false,held='',who='nico',object='spider',focus='nico',thread=null;
 function walk(id,a,z,finish=.7){finish=Math.min(finish,3.4/d);const o=A[id],w=q(u/finish),dx=z[0]-a[0],dz=z[1]-a[1];o.x=lerp(a[0],z[0],w);o.z=lerp(a[1],z[1],w);o.yaw=Math.atan2(-dz,dx);o.distance=Math.hypot(dx,dz)*w;o.moving=u<finish;o.gaitWeight=q(u/.08)*q((finish-u)/.08);o.headYaw=-.15;}
 function hand(id,v){A[id].hand=local(A[id],v);}
 function hold(id,prop){held=prop;who=id;object=prop;A[id].hand=[.38,1.1,.20];}
 const n=A.nico,l=A.lia;
 switch(act){
 case 'sumiu':s.A.lia.root.visible=false;walk('nico',[-6,1.5],[-4.7,.6],.6);n.gesture='think';n.gestureWeight=q((u-.6)/.2);wall=true;sp=[-5.5+q((u-.25)/.2)*1.2,1.9,-3.20];P.spider.visible=u<.50;break;
 case 'copo':n.x=1.6;n.z=2.5;hold('nico','cup');s.A.lia.root.visible=false;sp=[-4.6,2.2,-3.20];wall=true;object=u<.55?'cup':'spider';break;
 case 'lia':n.x=-4.6;n.z=.8;n.gesture='think';walk('lia',[-1,1.3],[-3.1,.9],.7);l.gesture='point';l.gestureWeight=q((u-.7)/.2);wall=true;sp=[-4.6,2.2,-3.2];break;
 case 'chaleira':walk('nico',[-1,.8],[4.8,-1.4],.6);n.hand=[.42,1.28,.18];l.x=1.6;l.z=2.7;P.notebook.visible=true;object='kettle';thread=[[.1,1.4,-.5],[.1,1.4,1.2]];sp=[.1,1.4,-.5];wall=true;break;
 case 'atalho':walk('nico',[1.7,1.4],[3.6,1],.65);n.crouch=.35*q((u-.35)/.25);n.expr='surprised';hand('nico',[4.1,1.0,0]);P.cushion.position.y=.85+.55*q((u-.35)/.30);P.cushion.rotation.z=.2*q(u/.6);l.x=1;l.z=1.5;sp=[4.95,1.08,.15];object='cushion';P.sock.visible=true;break;
 case 'hipotese':n.x=2.7;n.z=1.4;l.x=.8;l.z=2.3;l.gesture='point';n.gesture='think';sp=[4.9,1.08,.1];break;
 case 'mapa':n.x=1.5;n.z=2.8;l.x=3.2;l.z=2.8;l.yaw=-3.7;P.map.visible=true;hand('nico',[1.9,1.02,2.15]);hand('lia',[2.6,1.02,2.15]);object='map';sp=[4.9,1.08,.1];break;
 case 'teste':{const go=q(u/.5),back=q((u-.5)/.5);n.x=lerp(-1,1,go)-1.1*back;n.z=.9;n.distance=2*go+1.1*back;n.moving=true;n.yaw=u<.5?0:Math.PI;n.gaitWeight=q(u/.05)*q((1-u)/.05);l.x=-2.6;l.z=1.7;l.gesture='think';sp=[.4+.9*p,.02,-3.1];P.spider.visible=u>.6;object='cable';break;}
 case 'olhos':n.x=.1;n.z=.7;n.gesture='point';l.x=1.5;l.z=1;l.yaw=Math.PI;hold('lia','torch');sp=[1.0+2*p,.02,-3.05];object='cable';break;
 case 'escala':walk('nico',[-2.4,.4],[1,.4],.9);l.x=2;l.z=1;sp=[-.8+1.2*p,.02,-2.8];spyaw=0;object='spider';break;
 case 'vibracao':walk('nico',[-2,.9],[.7,.9],.75);l.x=2.5;l.z=1.5;sp=[.2+2*p,.02,-2.9];thread=[[.2,.12,-3.3],[.2,.12,-.4]];object='spider';break;
 case 'rotina':n.x=1.7;n.z=2.8;l.x=3.4;l.z=2.6;l.yaw=-3.4;l.gesture='point';for(let i=0;i<3;i++){P.cards[i].visible=true;P.cards[i].position.set(1.8+i*.6,.88,2);}sp=[3.5,.02,-2.8];object='card1';break;
 case 'troca':n.x=1.5;n.z=2.7;l.x=3.3;l.z=2.7;l.yaw=-3.4;for(let i=0;i<3;i++){P.cards[i].visible=true;P.cards[i].position.set(1.8+((i+1)%3)*.6,.88,2);}sp=[2,.87,2];P.cup.position.set(2,1.15,2);P.cup.rotation.x=Math.PI;object='cup';n.expr='surprised';break;
 case 'captura':n.x=1.6;n.z=2.65;l.x=2.9;l.z=2.55;l.yaw=-3.4;n.yaw=1.2;hand('nico',[2,1.16+.25*q((u-.6)/.3),2.1]);hand('lia',[2.2,.94,2.1]);P.cup.position.set(2,1.15+.25*q((u-.6)/.3),2);P.cup.rotation.x=Math.PI;P.card.position.set(lerp(2.7,2,q(u/.5)),.84+.25*q((u-.6)/.3),2);sp=[2,.87+.25*q((u-.6)/.3),2];object='cup';break;
 case 'soltura':walk('lia',[-2.7,1],[-4.4,-1.6],.6);n.x=-3.2;n.z=.1;hold('lia','cup');sp=[-4.6+q((u-.6)/.2)*.2,1.98,-3];spyaw=Math.PI;object='plant';break;
 case 'retorno':walk('nico',[1.4,1.4],[4.1,1],.6);l.x=2.3;l.z=1.5;hand('nico',[4.7,1.08,.2]);sp=[4.95,1.08,0];thread=[[4.95,1.08,0],[5.4,1.08,-.6]];object='remote';break;
 case 'duvida':n.x=3.8;n.z=1.1;hold('nico','phone');l.x=2.6;l.z=2.8;P.notebook.visible=true;l.hand=[.43,1.08,.18];sp=[4.95,1.08,0];object='notebook';break;
 case 'camera':n.x=3.2;n.z=2.5;l.x=1.5;l.z=2.6;P.books.visible=true;P.phone.visible=true;P.phone.position.set(2.8,1.40,2);n.hand=[.4,1.25,.15];sp=[2.65+.35*p,1.70,2.06];wall=true;object='phone';break;
 case 'fora':n.x=3.2;n.z=2.8;l.x=1.5;l.z=2.6;P.books.visible=true;P.phone.visible=true;P.phone.position.set(2.8,1.40,2);l.gesture='point';sp=[3.2,1.08,-.2];object='phone';break;
 case 'cadeira':n.x=4.5;n.z=1.7;l.x=5.5;l.z=1.7;l.yaw=-.5;P.chair.position.x=5.4+.45*p;P.chair.position.z=1+.3*p;n.hand=[.41,1.12,.1];hold('lia','torch');sp=[6.25,1.3,.6];object='chair';P.bigShadow.visible=true;break;
 case 'sombra':n.x=4.8;n.z=1.5;n.gesture='think';l.x=3.6;l.z=2;hold('lia','torch');P.bigShadow.visible=u<.45;sp=[6.3,1.32,.55];thread=[[2,.9,2],[3.0,.9,2]];P.cards[2].visible=true;P.cards[2].position.set(2.7-.2*p,.88,2);object=u<.5?'bigShadow':'card2';break;
 case 'plano':n.x=2;n.z=2.8;l.x=3.6;l.z=2.7;l.yaw=-3.5;P.notebook.visible=true;P.torch.visible=true;P.torch.position.set(3,.92,2);n.gesture='think';l.hand=[.4,1.12,.1];sp=[2.5,.02,-3.1];object='notebook';break;
 case 'desvio':{const w=q(u/.8);n.x=-2+3*w;n.z=.9+1.5*Math.sin(Math.PI*w);n.yaw=Math.atan2(-1.5*Math.PI*Math.cos(Math.PI*w),3);n.distance=4.3*w;n.moving=u<.8;n.gaitWeight=q(u/.08)*q((.8-u)/.08);l.x=2.5;l.z=1.6;sp=[-.8+2*p,.02,-2.8];object='spider';break;}
 case 'espera':n.x=.9;n.z=1.7;n.gesture='think';l.x=3.1;l.z=1.2;l.expr='joy';sp=[1.2,.02,-2.8];break;
 case 'pista':n.x=2;n.z=1.5;l.x=3.4;l.z=1.3;sp=[1.2+4.8*p,.02,-2.8+3.0*p];spyaw=-.55;object='lamp';break;
 case 'interruptor':walk('lia',[3,1.6],[5.6,1.5],.7);hold('lia','torch');n.x=4.2;n.z=1.8;sp=[6.05,.83,.8];thread=[[3,.06,-2.8],[6.15,.83,.8]];object='switch';break;
 case 'escolha':n.x=5.5;n.z=1.4;n.yaw=.6;l.x=4.6;l.z=1.9;hold('lia','torch');hand('nico',[5.9-.25*q((u-.5)/.4),1.12,.95]);n.expr='determined';sp=[6.0,.83,.8];thread=[[5.75,.84,.8],[6.25,.84,.8]];object='switch';break;
 case 'apagao':n.x=5.1;n.z=1.7;l.x=4.0;l.z=1.9;hold('lia','torch');n.expr='surprised';l.expr='surprised';const dim=q((u-.10)/.25);s.lampLight.intensity=7*(1-dim);s.warm.intensity=12*(1-dim);P.bulb.visible=dim<.9;sp=[6.0,.83,.8];object='switch';break;
 case 'revela':n.x=4.7;n.z=1.7;l.x=5.7;l.z=1.7;l.yaw=Math.PI;hold('lia','torch');n.crouch=.45*q(u/.4);s.lampLight.intensity=0;s.warm.intensity=0;P.bulb.visible=false;sp=[-4.6,1.98,-3];object='plug';break;
 case 'vaso':walk('nico',[-2,1.2],[-4.4,.6],.75);l.x=-4.1;l.z=-1.5;l.yaw=-1.4;l.hand=[.45,1.4,.19];sp=[-4.6+q(u/.8)*.3,1.98,-3];spyaw=0;s.lampLight.intensity=0;s.warm.intensity=0;P.bulb.visible=false;object='plant';break;
 case 'ultimo':walk('nico',[2.6,2.8],[.1,2.8],.55);l.x=-1.5;l.z=2.6;P.spider.visible=false;P.map.visible=true;P.card.position.set(2.7-.4*q((u-.6)/.35),.9,2.1);thread=[[P.card.position.x,.92,2.1],[4.0,.92,2.1]];object='card';s.lampLight.intensity=0;s.warm.intensity=0;P.bulb.visible=false;break;
 case 'final':n.x=1.4;n.z=2.8;n.yaw=-1.0;l.x=3.2;l.z=2.7;l.yaw=-2;l.gesture='think';n.gesture='point';sp=[2.5,.88,2];object='cup';break;
 }
 for(const [id,o]of Object.entries(A))s.A[id].update(o);
 if(held){const h=s.A[who].point();P[held].visible=true;P[held].position.copy(h);if(held==='cup')P.cup.position.y-=.13;}
 if(act==='captura'&&u>.6){const h=s.A.nico.point();P.cup.position.set(h.x,h.y,h.z-.06);P.card.position.set(h.x,h.y-.31,h.z-.06);sp=[h.x,h.y-.29,h.z-.06];}
 if(act==='soltura'){const h=s.A.lia.point(),r=q((u-.6)/.2);P.cup.position.set(h.x,h.y+.13,h.z);P.cup.rotation.x=Math.PI*(1-.5*r);P.card.visible=true;P.card.position.set(h.x,h.y-.17,h.z);sp=[lerp(h.x,-4.4,r),lerp(h.y,1.98,r),lerp(h.z,-3,r)];}if(thread){P.wire.visible=true;P.thread.set(...thread);}
 P.spider.position.set(...sp);P.spider.rotation.set(0,spyaw,0);if(wall)P.spider.rotation.x=Math.PI/2;const travel={sumiu:1.2*q((u-.25)/.2),olhos:2*p,escala:1.2*p,vibracao:2*p,teste:.9*p,pista:Math.hypot(4.8,3)*p,desvio:2*p,vaso:.3*q(u/.8)};s.crawl((travel[act]||0)/.45);
 s.motion={act,u,A,object,focus};
}
function camera(s,info){const H=s.H,m=s.motion,cam=info.cam,n=m.A[m.focus],p=q(info.p),head=s.A[m.focus].head.getWorldPosition(new H.Vector3());let target=new H.Vector3(n.x,1.05,n.z),off=new H.Vector3(2,1.6,4),fov=43;
 const ob=s.P[m.object],obj=ob?ob.getWorldPosition(new H.Vector3()):target.clone();
 switch(cam){
 case 'wide':target.set((m.A.nico.x+m.A.lia.x)/2,1.15,(m.A.nico.z+m.A.lia.z)/2-.7);off.set(2.5,2.8,6.5);break;
 case 'two':target.set((m.A.nico.x+m.A.lia.x)/2,1.10,(m.A.nico.z+m.A.lia.z)/2);off.set(1.2,1.0,4.3);break;
 case 'close':{target.copy(head);const a=n.yaw+(n.headYaw||0);off.set(Math.cos(a)*1.9,.14,-Math.sin(a)*1.9);fov=38;break;}
 case 'reverse':{target.copy(s.A.lia.head.getWorldPosition(new H.Vector3()));const a=m.A.lia.yaw+(m.A.lia.headYaw||0);off.set(Math.cos(a)*1.9,.14,-Math.sin(a)*1.9);fov=38;break;}
 case 'track':off.set(1.5,1.1,4.0);target.y=1.1;break;
 case 'feet':target.copy(s.A.nico.point('foot'));off.set(1.1,.45,1.8);fov=38;break;
 case 'hand':target.copy(obj);off.set(.7,.65,1.3);fov=39;break;
 case 'detail':target.copy(obj);off.set(1.0,.5,1.7);fov=37;break;
 case 'macro':target.copy(obj);off.set(.48,.36,.85);fov=38;break;
 case 'spider':target.copy(s.P.spider.position);off.set(.24,.15,.40);fov=37;break;
 case 'floor':target.copy(s.P.spider.position);target.y=.10;off.set(.45,.10,.72);fov=49;break;
 case 'travel':target.copy(s.P.spider.position);off.set(.15,.28,1.3);fov=51;break;
 case 'over':target.copy(obj);off.set(.1,4.0,.8);fov=44;break;
 case 'window':target.set(-5.2,1.8,-2.6);off.set(2,.7,3.6);break;
 case 'switch':target.copy(s.P.switch.position);off.set(.7,.4,1.1);fov=37;break;
 case 'reveal':target.copy(obj);off.set(lerp(.65,2,p),lerp(.35,1.2,p),lerp(1.1,4,p));break;
 }
 // Camera stays inside open-front apartment; distant back wall never occludes reverse angles.
 if(['macro','spider','detail','switch'].includes(cam)){for(const a of Object.values(s.A))a.root.visible=false;}if(cam==='hand'){s.A.lia.root.visible=false;if(!['copo','captura','soltura','duvida'].includes(m.act))s.A.nico.root.visible=false;}if(cam==='close')s.A.lia.root.visible=false;if(cam==='reverse')s.A.nico.root.visible=false;if(['wide','track','two'].includes(cam))off.applyAxisAngle(new H.Vector3(0,1,0),.12*(p-.5));off.multiplyScalar(1-.035*p);s.camera.position.copy(target).add(off);s.camera.position.z=Math.max(s.camera.position.z,-3.1);s.camera.lookAt(target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
 // Deterministic cutaway for obstructing foreground geometry in inserts only.
 // Restore on next frame before applying narrative visibility; never hide the subject.
 if(['macro','spider','detail','hand','switch','close','reverse'].includes(cam)){
  const subject=cam==='spider'?s.P.spider:cam==='close'?s.A.nico.root:cam==='reverse'?s.A.lia.root:ob;
  const belongs=(v,parent)=>{for(let a=v;a;a=a.parent)if(a===parent)return true;return false;};
  s.scene.updateMatrixWorld(true);const direction=target.clone().sub(s.camera.position),distance=direction.length(),ray=new H.Raycaster(s.camera.position,direction.normalize(),.03,Math.max(.05,distance-.14));
  for(let pass=0;pass<10;pass++){const hits=ray.intersectObjects(s.scene.children,true).filter(h=>h.object.visible&&!belongs(h.object,subject)&&!Object.values(s.A).some(a=>belongs(h.object,a.root)));if(!hits.length)break;const hit=hits[0].object;hit.visible=false;s.hidden.push(hit);}
 }

}
function overlay(g,t,info,s){const act=s.motion.act;
 if(['hipotese','escala'].includes(act)&&info.cam==='wide'){g.fillStyle='#153444ed';rr(g,90,70,910,94,20);g.fill();text(g,'UMA HIPÓTESE DE FICÇÃO',545,118,{size:41,color:'#ffe4a1',align:'center'});}
 if(act==='mapa'&&info.cam==='over')text(g,'PADRÃO ≠ PROVA',960,160,{size:56,color:'#ffe4a1',align:'center'});
 if(act==='espera'&&info.cam==='wide')text(g,'PREVER NÃO É ADIVINHAR',960,120,{size:48,color:'#ffe4a1',align:'center'});
 const when=[[43,51],[story.duration*.49,story.duration*.49+8],[story.duration-14,story.duration-1]];
 for(const [a,b]of when)if(info.globalT>=a&&info.globalT<=b){g.save();g.globalAlpha=q((info.globalT-a)/.5)*q((b-info.globalT)/.5);g.fillStyle='#153f49';rr(g,80,910,660,100,26);g.fill();text(g,'ENTÃO • INSCREVA-SE',410,960,{size:40,color:'#e4fff1',align:'center'});g.restore();}
}
for(const sh of story.shots)registerShot(sh.id,{kind:'3d',init(T){return world(T);},draw(s,t,info){const b=beats[info.beat];animate(s,b,info.globalT-b.start,b.end-b.start);camera(s,info);},overlay(g,t,info,s){overlay(g,t,info,s);}});
