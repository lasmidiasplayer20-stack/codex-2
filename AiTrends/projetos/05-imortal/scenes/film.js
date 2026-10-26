// Opening only. Later shots remain explicitly unimplemented until audio evaluation.
import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {world} from './world.js';
const story=await(await fetch('/project/story/shots.json')).json();
const beats=await(await fetch('/project/story/beats.json')).json();
const smooth=x=>ease.inOut(clamp(x));
for(const shot of story.shots.filter(s=>s.params.beat===0))registerShot(shot.id,{
 kind:'3d',init(T){return world(T,'workshop');},
 draw(s,t,info,T){
  const time=info.globalT,u=time/20.16,H=T.THREE,k=smooth(time/3.5),reach=smooth((time-2.8)/1.4),lift=smooth((time-7.6)/3.2);
  for(const a of Object.values(s.A))a.root.visible=false;s.nico.root.visible=true;for(const ob of Object.values(s.P))ob.visible=false;
  const x=-2.7+2.05*k,z=.83;
  // Contact motion uses one global clock across all camera cuts.
  const theta=.9*smooth((time-4.2)/2.5),down=smooth((time-6.7)/.9);
  const grip=[.16,1.3+.48*Math.sin(theta),.145+.48*Math.cos(theta)-z];
  const pickup=[.45,1.27,-.3],hold=[.32,1.28,.10];
  const hand=grip.map((v,i)=>{const resting=[.05,.94,.19][i];const opening=resting+(v-resting)*reach;const picked=opening+(pickup[i]-opening)*down;return picked+(hold[i]-picked)*lift;});
  s.nico.update({x,z,time,yaw:0,headYaw:-.35,moving:time<3.5,distance:2.05*k,hand,handB:[.09,.9,-.19],expr:time>10?'sad':'smile',nod:-.10*lift});
  s.lid.visible=true;s.lid.rotation.x=-theta;
  const h=s.nico.point();s.photo.visible=time>=7.6;
  s.photo.position.copy(h);s.photo.position.y+=.08;s.photo.rotation.set(-.1,.25,.06);
  s.box.visible=true;
  const cam=info.cam,v=smooth(info.p),head=s.nico.head.getWorldPosition(new H.Vector3());
  let target=new H.Vector3(x+.45,1.05,z-.2),off=new H.Vector3(3.7,2.1,5.3),fov=42;
  if(cam==='hands'){target.set(-.23,1.16,.45);off.set(1.4,1.25,1.75);fov=37;}
  if(cam==='two'){target.x=o.x+1;off.set(2.2,1.35,4.6);fov=42;}
 if(cam==='feet'){target.copy(s.nico.point('foot'));target.y=.15;off.set(1.2,.65,2.3);fov=39;}
 if(cam==='over'){target.set(o.x+.6,.7,o.z);off.set(.6,7.8,2.3);fov=43;}
 if(cam==='reverse'&&s.motion.A.lia){target.copy(s.A.lia.head.getWorldPosition(new H.Vector3()));off.set(-1.2,.2,2);fov=36;}
 if(cam==='track'){target.copy(h).lerp(head,.35);off.set(1.3,.6,2.4);fov=37;}
  if(cam==='close'){target.copy(head);off.set(1.5,.18,2.0);fov=34;}
  if(cam==='orbit'){const a=.3+.4*v;off.set(5.3*Math.sin(a),1.8,5.3*Math.cos(a));target.set(-.3,1.16,.5);fov=42;}
  off.multiplyScalar(1-.04*v);s.stage.camera.position.copy(target).add(off);s.stage.camera.lookAt(target);s.stage.camera.fov=fov;s.stage.camera.updateProjectionMatrix();
 },
 overlay(g,t,info){
  const a=smooth((info.globalT-.3)/1)*smooth((19.8-info.globalT)/1);g.save();g.globalAlpha=a;
  g.fillStyle='#18343b';rr(g,1120,78,640,100,22);g.fill();text(g,'300 ANOS DEPOIS',1440,128,{size:43,color:'#ffe6b2',align:'center'});g.restore();
 }
});

const mix=(a,b,p)=>a+(b-a)*p;
function state(x,z,time,extra={}){return {x,z,time,yaw:-.25,headYaw:-.2,moving:false,distance:0,expr:'smile',...extra};}
function local(o,v){const dx=v[0]-o.x,dz=v[2]-o.z,c=Math.cos(o.yaw),sn=Math.sin(o.yaw);return [dx*c-dz*sn,v[1],dx*sn+dz*c];}
function show(s,id,p,rot=0){const ob=s.P[id];if(!ob)return;ob.visible=true;if(id==='chair'&&s.P.chairBack){s.P.chairBack.visible=true;s.P.chairBack.rotation.set(0,0,0);}ob.position.set(...p);ob.rotation.set(0,rot,0);return ob;}
function action(s,b,time,dur){
 const u=clamp(time/dur),p=smooth(u),act=b.action,A={},P=s.P;
 for(const a of Object.values(s.A))a.root.visible=false;
 for(const ob of Object.values(P))ob.visible=false;
 if(P.bench)P.bench.visible=true;if(P.tree){P.tree.visible=true;P.tree.scale.setScalar(1);}if(P.plant)P.plant.scale.setScalar(.5);
 let z=s.location==='workshop'?1.4:s.location==='garden'?2.6:3;
 const n=A.nico=state(-1.5,z,time),add=(id,x,zz,extra={})=>A[id]=state(x,zz,time,{yaw:-2.1,...extra});
 let focus='nico',object=null,handProp=null;
 const walk=(o,x0,x1,progress=p)=>{o.x=mix(x0,x1,progress);o.distance=Math.abs(x1-x0)*progress;o.moving=progress>.001&&progress<.999;o.gaitWeight=smooth(progress/.08)*smooth((1-progress)/.08);};
 switch(act){
 case 'volta':n.x=-2;n.gesture='surprise';n.expr=u<.5?'surprised':'determined';object='phone';handProp='phone';n.hand=[.27,1.34,.16];break;
 case 'regra':case 'ciencia':case 'natureza':case 'identidade':{
  n.x=-2.5;n.z=3;n.gesture=u<.5?'point':'think';const d=show(s,'diagram',[.4,.25,3]);d.rotation.y=.14*p;
  const which=act==='ciencia'?'chromosome':act==='natureza'?'jelly':act==='identidade'?'docs':'cell';P[which].visible=true;
  if(which==='cell'){P.cell.scale.x=.8+.2*p;P.cell.position.x=.3*p;}
  if(which==='jelly'){P.jelly.position.y=.12*Math.sin(Math.PI*2*u);P.jelly.scale.setScalar(1-.16*p);}
  object='diagram';break;}
 case 'teste':n.x=-1.1;n.gesture='think';add('lia',1,z,{gesture:'point',expr:'surprised'});show(s,'photo',[.2,1.18,z-.2]);object='photo';break;
 case 'promessa':walk(n,-3,0);add('lia',n.x+1.5,z-.3,{moving:n.moving,distance:n.distance});n.gesture='point';n.gestureWeight=smooth((u-.6)/.15);object='tree';break;
 case 'cadeira':{
  n.x=-.95;n.z=1.1;n.crouch=.45*(1-Math.sin(Math.PI*p)*.3);add('lia',.5,1.0,{crouch:.4});const c=show(s,'chair',[-.25,0,1.3]);c.rotation.z=.07*Math.sin(Math.PI*2*p)*(1-smooth((u-.7)/.25));
  n.hand=local(n,[-.52,.87,1.48]);A.lia.hand=local(A.lia,[.03,.87,1.48]);if(P.chairBack)P.chairBack.rotation.y=Math.PI*(1-smooth((u-.25)/.45));n.expr=u>.8?'joy':'determined';handProp='tool';object='chair';break;}
 case 'adiar':n.x=-1.8;n.hand=[.28,1.3,.16];handProp='phone';n.expr='tired';show(s,'chair',[1,0,1.4]);break;
 case 'encontro':walk(n,-4,-1.2,smooth(u/.55));n.gesture='think';n.gestureWeight=smooth((u-.6)/.15);n.expr='sad';n.hand=u>.6?[.3,1.28,.15]:null;handProp=u>.6?'phone':null;object='bench';break;
 case 'acordo':n.x=-1.6;add('lia',.2,z,{gesture:'point'});n.hand=[.4,1.22,.15];handProp='notebook';object='notebook';break;
 case 'decadas':n.x=-1;n.hand=[.42,1.14,.15];handProp='tool';show(s,'chair',[.2,0,1.3]);add('lia',1.6,1.2,{gesture:'point'});n.expr='determined';object='chair';break;
 case 'amiga':walk(n,-3,.5);add('lia',n.x+1.25,z-.22,{moving:n.moving,distance:n.distance});object='tree';break;
 case 'presente':n.x=-1.4;add('lia',.1,1.4,{hand:[.4,1.25,.15]});n.hand=[.45,1.25,.12];show(s,'chair',[1.9,0,1.5]);object='photo';break;
 case 'despedida':walk(n,-4,-1.6,smooth(u/.6));n.expr='sad';n.gesture='think';n.gestureWeight=smooth((u-.7)/.15);object='bench';break;
 case 'isolado':n.x=-1.4;n.expr='sad';n.gesture='think';show(s,'chair',[1.5,0,1.3]);object='chair';break;
 case 'vizinha':n.x=-1.0;n.crouch=1.15*Math.sin(Math.PI*u);add('sol',1.4,1.4,{gesture:'point'});show(s,'cart',[-.0,0,1.6]);const w=show(s,'wheel',[-.35,.28,1.84]);w.rotation.z=3*Math.PI*p;n.hand=local(n,[-.35,.45,1.84]);n.expr='determined';object='wheel';break;
 case 'reabrir':n.x=-1.3;n.crouch=.45*Math.sin(Math.PI*u);add('sol',1.0,z-.3,{gesture:'point'});n.hand=[.42,mix(1.1,.6,Math.sin(Math.PI*u)),.15];handProp='plant';object='plant';break;
 case 'cem':walk(n,-3,.8);n.gesture='point';n.gestureWeight=smooth((u-.5)/.15);add('ari',2.2,z-.4,{gesture:'point'});if(P.tree)P.tree.scale.setScalar(1.25);object='tree';break;
 case 'memoria':n.x=-1.0;n.gesture='think';n.hand=[.42,1.27,.13];handProp='notebook';show(s,'box',[.5,.98,.2]);P.lid.visible=true;P.lid.rotation.x=-.9;object='notebook';break;
 case 'escola':n.x=-1.6;add('ari',.8,1.4,{gesture:'point'});add('gui',2.0,1.5,{gesture:'point'});n.hand=[.42,1.2,.12];handProp='tool';show(s,'chair',[0,0,1.3]);object='tool';break;
 case 'futuro':walk(n,-3.3,.2);n.gesture='point';add('ari',1.8,z-.2,{gesture:'point'});object='tree';break;
 case 'partida':walk(n,-3,-.6,smooth(u/.55));n.hand=[.26,.92,.15];handProp='suitcase';add('ari',1.8,3,{gesture:'point'});object='suitcase';break;
 case 'nave':{
  n.x=mix(-1.8,.0,p);n.y=.1*Math.sin(Math.PI*u);n.hand=[.42,1.33,.1];n.expr=u<.5?'surprised':'determined';
  add('ari',1.8,3.1,{hand:[.3,1.15,.12],expr:'determined'});show(s,'suitcase',[mix(-.3,1.5,smooth(u/.55)),1.1+.25*Math.sin(Math.PI*u),3]);object='suitcase';break;}
 case 'jardim':n.x=-1.5;n.hand=[.45,1.13,.13];handProp='plant';add('ari',.8,3.2,{gesture:'point'});object='plant';break;
 case 'cosmos':case 'estrela':case 'limite':n.x=-2;n.z=3;n.gesture=act==='limite'?'think':'point';n.expr=act==='limite'?'determined':'surprised';if(P.planet){P.planet.visible=act!=='estrela';P.planet.scale.set(1,1,.3);}if(P.sunDisk){P.sunDisk.visible=act==='estrela';P.sunDisk.scale.setScalar(.7+.6*p);}object=act==='estrela'?'sunDisk':'planet';break;
 case 'retorno':n.x=-1.5;add('ari',.6,1.3,{hand:[.4,1.2,.13]});n.hand=[.4,1.2,.13];show(s,'chair',[2,0,1.2]);object='photo';break;
 case 'escolha':walk(n,-4,-.7);add('ari',1,z-.2,{gesture:'point'});object='bench';break;
 case 'final':n.x=-1.8;add('ari',.8,z,{gesture:'point'});add('gui',2.2,z+.2,{gesture:'point'});n.gesture='point';object='tree';break;
 }
 if(A.lia&&['amiga','presente'].includes(act)){A.lia.age=true;A.lia.nod=-.06;}
 for(const [id,o]of Object.entries(A)){s.A[id].root.visible=true;s.A[id].update(o);}
 if(act==='nave'&&u>.48){const ob=P.suitcase,h=s.A.ari.point();ob.position.lerp(h,smooth((u-.48)/.32));}
 if(handProp){const h=s.A.nico.point();show(s,handProp,[h.x,h.y,h.z]);}
 if(['reabrir','jardim'].includes(act)&&u>.65){const h=s.A.nico.point(),k=smooth((u-.65)/.3);show(s,'plant',[mix(h.x,s.location==='garden'?-.7:2.7,k),mix(h.y,s.location==='garden'?.08:.92,k),mix(h.z,s.location==='garden'?2.4:1,k)]);}
 if(['presente','retorno'].includes(act)){
  const other=act==='presente'?'lia':'ari',a=s.A[other].point(),h=s.A.nico.point();
  const transition=act==='presente'?smooth((u-.25)/.5):1-smooth((u-.25)/.5);a.lerp(h,transition);show(s,'photo',[a.x,a.y+.10,a.z+.04]);
 }
 s.motion={u,p,A,object,act,focus};return s.motion;
}
function camera(s,info){
 const m=s.motion,H=s.H,cam=info.cam,v=smooth(info.p),o=m.A.nico,head=s.nico.head.getWorldPosition(new H.Vector3());
 let target=new H.Vector3(o.x+.65,1.05,o.z),off=new H.Vector3(3.3,2,5.7),fov=43;
 if(cam==='wide'){target.x=o.x+.8;off.set(4.0,2.5,6.7);}
 if(cam==='two'){target.x=o.x+1;off.set(2.2,1.35,4.6);fov=42;}
 if(cam==='feet'){target.copy(s.nico.point('foot'));target.y=.15;off.set(1.2,.65,2.3);fov=39;}
 if(cam==='over'){target.set(o.x+.6,.7,o.z);off.set(.6,7.8,2.3);fov=43;}
 if(cam==='reverse'&&s.motion.A.lia){target.copy(s.A.lia.head.getWorldPosition(new H.Vector3()));off.set(-1.2,.2,2);fov=36;}
 if(cam==='track'){off.set(2.0,1.3,4.4);fov=42;}
 if(cam==='close'){target.copy(head);off.set(1.45,.15,2.0);fov=35;}
 if(cam==='hands'){
  const ob=s.P[m.object];target.copy(ob&&ob.visible?ob.getWorldPosition(new H.Vector3()):s.nico.point());
  if(m.object==='chair')target.y=.9;if(m.object==='tree')target.set(o.x+.5,1.1,o.z);if(m.object==='bench')target.y=.7;
  off.set(1.4,.9,2.5);fov=38;
 }
 if(cam==='orbit'){const a=.1+.46*v;off.set(5.2*Math.sin(a),1.8,5.2*Math.cos(a));target.x=o.x+.6;}
 if(s.location==='diagram'){target.set(info.part===1||info.part===3?.8:-.1,1.55,3);off.set(.5,info.part===1?1:1.5,info.part===1||info.part===3?3.6:6.5);fov=40;}
 off.multiplyScalar(1-.035*v);s.stage.camera.position.copy(target).add(off);s.stage.camera.lookAt(target);s.stage.camera.fov=fov;s.stage.camera.updateProjectionMatrix();
}
function caption(g,s,info){
 const act=s.motion.act,labels={volta:'A PRIMEIRA MANHÃ',regra:'NÃO ENVELHECE ≠ NÃO SENTE',decadas:'OS ANOS PASSAM',amiga:'CADA UM NO SEU RITMO',cem:'100 ANOS DEPOIS',memoria:'MEMÓRIA NÃO É INFINITA',ciencia:'FANTASIA ≠ CIÊNCIA',natureza:'TURRITOPSIS DOHRNII',futuro:'UM FUTURO IMAGINÁRIO',cosmos:'MILÊNIOS',estrela:'ATÉ AS ESTRELAS MUDAM',limite:'HIPÓTESE, NÃO PREVISÃO',retorno:'300 ANOS DEPOIS'};
 if(labels[act]&&['wide','orbit','track'].includes(info.cam)){g.fillStyle='#173c4bea';rr(g,620,72,1100,86,18);g.fill();text(g,labels[act],1170,115,{size:37,color:'#ffe8b9',align:'center'});}
 cta(g,info.globalT);
}
function cta(g,t){
 const duration=story.duration,intervals=[[43,51],[duration*.49,duration*.49+8],[duration-14,duration-1]];
 for(const [a,b]of intervals)if(t>=a&&t<=b){const k=smooth((t-a)/.6)*smooth((b-t)/.6);g.save();g.globalAlpha=k;g.fillStyle='#113942';rr(g,1130,900,650,100,26);g.fill();text(g,'ENTÃO • INSCREVA-SE',1455,950,{size:40,color:'#e1fff1',align:'center'});g.restore();}
}
for(const shot of story.shots.filter(s=>s.params.beat!==0))registerShot(shot.id,{kind:'3d',init(T){return world(T,beats[shot.params.beat].set);},draw(s,t,info){const b=beats[info.beat];action(s,b,info.globalT-b.start,b.end-b.start);camera(s,info);},overlay(g,t,info,s){caption(g,s,info);}});
