import {registerShot,clamp,ease,text,rr,seg,circle} from '/engine/core.js';
import {world} from './world.js';
const beats=await(await fetch('/project/story/beats.json')).json(),story=await(await fetch('/project/story/shots.json')).json();
const q=x=>ease.inOut(clamp(x)),lerp=(a,b,t)=>a+(b-a)*t;
const defaults=(x,z,time,more={})=>({x,z,time,yaw:0,headYaw:-.25,moving:false,distance:0,expr:'smile',...more});
function local(o,p){const x=p[0]-o.x,z=p[2]-o.z,c=Math.cos(o.yaw),s=Math.sin(o.yaw);return [x*c-z*s,p[1],x*s+z*c];}
function show(s,id,p){const ob=s.P[id];if(!ob?.isObject3D)return;ob.visible=true;if(p)ob.position.set(...p);if(id==='boxA'&&s.P.lidA)s.P.lidA.visible=true;if(id==='boxB'&&s.P.lidB)s.P.lidB.visible=true;return ob;}
function walk(o,start,end,progress){o.x=lerp(start,end,progress);o.distance=Math.abs(end-start)*progress;o.moving=progress>0&&progress<1;o.gaitWeight=q(progress/.08)*q((1-progress)/.08);}
function drawDiagram(s,act,u){
 const P=s.P,H=s.H;show(s,'diagram',[.5,0,2.6]);for(const ob of [...P.diagramNodes,...P.diagramBars])ob.visible=false;for(const e of P.diagramEdges)e.mesh.visible=false;
 for(let i=0;i<P.diagramNodes.length;i++)P.diagramNodes[i].material=s.L.mat(['#67cbb3','#aa84c4','#d7b16a','#75a4c8'][i%4]);
 const node=(i,p,size=.16)=>{const n=P.diagramNodes[i];n.visible=size>.001;n.position.set(...p);n.scale.setScalar(size);return n;};
 const edge=(i,a,b)=>{P.diagramEdges[i].mesh.visible=true;P.diagramEdges[i].set(a,b);};
 if(act==='numeros'){
  let count=0;for(let row=0;row<3;row++){const n=2**(row+1),y=2.6-row*.85;for(let j=0;j<n;j++){const growth=q((u-row*.22-j*.008)/.2);node(count++,[(j-(n-1)/2)*.52,y,0],.16*growth);}}return;
 }
 if(act==='diversidade'){for(let i=0;i<32;i++){const right=i>=16,j=i%16,n=node(i,[(right?.65:-2.8)+(j%4)*.47,.6+Math.floor(j/4)*.55,0],.15);if(!right)n.material=s.L.mat('#67cbb3');}return;}
 if(act==='risco'){const parents=[[-1,2.7,0],[1,2.7,0]];parents.forEach((v,i)=>node(i,v,.22));for(let i=0;i<4;i++){const end=[-1.8+i*1.2,.95,0];node(i+2,end,.20*q((u-.15)/.25));edge(i*2,parents[0],end);edge(i*2+1,parents[1],end);}return;}
 if(act==='mutacao'){for(let i=0;i<12;i++){const ob=node(i,[-1.8+(i%4)*1.0,2.8-Math.floor(i/4)*.8,0],.18);ob.material=s.L.mat(i===6&&u>.4?'#d99a7f':'#67cbb3');}return;}
 if(act==='limite'){for(let i=0;i<4;i++){const bar=P.diagramBars[i],height=(.65+i*.48)*q((u-.1)/.65);bar.visible=true;bar.position.set(-1.5+i*1.05,.4+height/2,0);bar.scale.set(.46,Math.max(.02,height),.3);}return;}
 if(['gargalo'].includes(act)){
  const selected=act==='diversidade'?16:4;for(let i=0;i<32;i++){const a=[-2.2+(i%8)*.35,.65+Math.floor(i/8)*.5,0],b=[1.1+(i%4)*.45,.8+Math.floor(i/4)*.35,0];let p=q((u-.15)/.6);node(i,i<selected?a.map((v,k)=>lerp(v,b[k],p)):a,.13*(i<selected?1:1-.8*p));}return;
 }
 if(['copias','oculto','parentesco'].includes(act)){
  for(let i=0;i<8;i++){let x=-1.7+Math.floor(i/2)*1.1,y=i%2?1:2.3;node(i,[x,y,0],.21);if(i%2)edge(Math.floor(i/2),[x,1.2,0],[x,2.1,0]);}return;
 }
 if(['quadrado','chance'].includes(act)){
  for(let i=0;i<4;i++){const x=i%2?1.0:-.35,y=i<2?2.05:.9;node(i,[x,y,0],.32*q((u-i*.09)/.2));}return;
 }
 if(act==='acaso'){
  for(let i=0;i<20;i++){let drop=i%3===1?q((u-.25)/.55):0;node(i,[-1.6+(i%5)*.7,2.7-Math.floor(i/5)*.6-drop*2,0],.14*(1-drop));}return;
 }
 for(let i=0;i<12;i++)node(i,[-1.8+(i%4)*1.0,2.8-Math.floor(i/4)*.8,0],.17);
}
function animate(s,b,t,d){
 const u=clamp(t/d),p=q(u),act=b.action,P=s.P,A={};
 for(const actor of Object.values(s.A))actor.root.visible=false;for(const ob of Object.values(P))if(ob?.isObject3D)ob.visible=false;
 if(P.lidA)P.lidA.rotation.x=0;if(P.lidB)P.lidB.rotation.x=0;
 if(s.location==='street'){show(s,'signal');for(let i=0;i<3;i++){P['lamp'+i].visible=true;P['lamp'+i].scale.set(.105,.105,.04);P['lamp'+i].material=s.L.mat(i===(u<.45?0:2)?['#e78a70','#e3c47e','#7ed6a0'][i]:'#35454d',true);} }
 if(s.location==='school')show(s,'board');if(s.location==='supply'){show(s,'pump');show(s,'freezer');}if(s.location==='clinic')show(s,'bench');if(s.location==='harbor')show(s,'plank');
 const z=s.location==='diagram'?2.5:s.location==='harbor'?1.5:1.3;
 const n=A.nico=defaults(-1.5,z,t),add=(id,x,zz,extra={})=>A[id]=defaults(x,zz,t,{yaw:-2.0,...extra});
 let focus='nico',object='radio',held=null;
 switch(act){
 case 'cidade':walk(n,-4.2,-.7,q(u/.72));n.expr=u>.65?'surprised':'smile';n.hand=[.18,1.2,.21];held='radio';if(u>.72)add('lia',2.0,1.4,{expr:'surprised'});object='signal';break;
 case 'encontro':walk(n,-2,-1.1,q(u/.4));const li=add('lia',1.5,1.4,{yaw:Math.PI});walk(li,3.3,1.5,q(u/.45));n.hand=[.40,1.17,.17];held='radio';object='radio';break;
 case 'plano':n.x=-1.8;add('lia',1.7,.4,{gesture:'point',gestureWeight:q(u/.15)});n.gesture='point';n.gestureWeight=q((u-.15)/.25);drawDiagram(s,'numeros',u);P.diagram.position.set(.5,.85,-1.0);P.diagram.scale.setScalar(.55);object='board';break;
 case 'heranca':{n.x=-1.2;n.z=.95;const li=add('lia',1.4,.95);const theta=q((u-.15)/.4);show(s,'boxA',[-.65,.98,.65]);show(s,'boxB',[.6,.98,.65]);P.lidA.rotation.x=-theta;P.lidB.rotation.x=-theta;const rise=1.26+.45*Math.sin(theta),front=.44+.45*Math.cos(theta);n.hand=local(n,[-.9,rise,front]);li.hand=local(li,[.85,rise,front]);object='boxA';break;}
 case 'parentesco':n.x=-2;add('lia',1.7,1.2,{gesture:'point'});n.gesture='think';drawDiagram(s,act,u);P.diagram.scale.setScalar(.6);P.diagram.position.set(.4,.6,-1.0);object='board';break;
 case 'baralho':n.x=-1.1;add('lia',1.3,1.2,{gesture:'point'});n.hand=[.4+.045*Math.sin(u*8*Math.PI),1.13,.18];n.handB=[.32,1.12,-.08];held='cards';show(s,'boxA',[.0,.98,.1]);object='card';break;
 case 'rotina':walk(n,-3.3,-.5,q(u/.6));n.hand=[.15,.94,.23];held='jug';add('lia',2.1,1.3,{crouch:.35*q((u-.4)/.3),hand:[.40,1.10,.18]});object='pump';break;
 case 'cuidado':n.x=-1.5;n.hand=[.4,1.14,.16];held='jug';add('lia',1.1,1.0,{hand:[.36,1.05,.18],expr:'tired'});object='jug';break;
 case 'ambiente':n.x=-1.2;n.crouch=.65*Math.sin(Math.PI*u);n.hand=[.39,1.03-.25*Math.sin(Math.PI*u),.15];held='seed';add('lia',1.2,1.4,{gesture:'point'});object='seed';break;
 case 'tempo':walk(n,-3.0,.2,p);add('lia',n.x+1.3,1.5,{yaw:0,moving:n.moving,distance:n.distance,gaitWeight:n.gaitWeight});object='paper';break;
 case 'banco':n.x=-1.5;add('lia',1.8,1.2,{gesture:'point'});n.gesture='think';object='freezer';break;
 case 'modelos':n.x=-1.6;add('lia',1.6,.9,{gesture:'point'});n.hand=[.41,1.13,.13];held='paper';object='board';break;
 case 'natureza':walk(n,-3.2,-.1,p);add('lia',1.6,1.4,{gesture:'point'});object='seed';show(s,'seed',[.0,.6,-.7]);break;
 case 'radio':n.x=-.95;n.z=.85;n.hand=[.45,1.10,-.15];held='radio';add('lia',1.25,1.1,{hand:[.42,1.12,.13]});show(s,'paper',[.3,1.0,.15]);object='radio';break;
 case 'travessia':{
  n.x=-2.0;n.z=1.45;n.crouch=.3*q((u-.10)/.4);const yy=1.13-.23*q((u-.10)/.4);n.hand=[.4,yy,.16];n.handB=[.4,yy,-.16];add('lia',1.9,1.45,{yaw:Math.PI,crouch:n.crouch,hand:[.4,yy,.16],handB:[.4,yy,-.16]});
  const plank=show(s,'plank');plank.position.set(0,lerp(1.1,.20,q((u-.18)/.6)),1.45);plank.rotation.z=.05*(1-p);object='plank';break;}
 case 'sinal':walk(n,-3.5,2.6,q(u/.75));add('lia',n.x-1.3,1.45,{yaw:0,moving:n.moving,distance:n.distance,gaitWeight:n.gaitWeight});n.gesture='point';n.gestureWeight=q((u-.75)/.15);object='plank';break;
 case 'grupo':walk(n,-3,-.8,q(u/.55));add('lia',.7,1.3,{gesture:'point'});add('ari',2.0,1.0,{gesture:'point'});add('sol',3.0,1.7,{gesture:'point'});n.hand=[.39,1.1,.15];held='tool';object='tool';break;
 case 'memoria':n.x=-1.2;add('lia',1.2,1.1,{hand:[.42,1.17,.15]});n.hand=[.42,1.17,.13];held='paper';object='paper';show(s,'tool',[.5,1.0,.3]);break;
 case 'resposta':n.x=-1.5;add('lia',1.2,1.4,{gesture:'think'});n.gesture='point';object='radio';break;
 case 'volta':walk(n,-3,.2,p);add('lia',1.5,1.4,{gesture:'point'});add('ari',3.2,.9,{moving:true,distance:2*p,yaw:0});add('sol',-3.8+2*p,1.9,{moving:true,distance:2*p,yaw:0});object='radio';break;
 case 'final':n.x=-1.6;add('lia',.7,1.3,{gesture:'point'});add('ari',2.2,1.7,{gesture:'point'});n.gesture='point';object='radio';break;
 default:n.x=-2.6;n.z=2.6;n.gesture=u<.6?'point':'think';drawDiagram(s,act,u);P.diagram.scale.setScalar(1);object='diagram';
 }
 for(const [id,o]of Object.entries(A)){if(s.location==='harbor')o.y=.16+.11*q((1.6-Math.abs(o.x))/.3);s.A[id].root.visible=true;s.A[id].update(o);}
 if(held){const h=s.A.nico.point();show(s,held,[h.x,h.y,h.z]);if(held==='cards')s.P.cards.rotation.z=.14*Math.sin(u*8*Math.PI);}
 // Contact-driven transfers: props use actual reachable hands after IK.
 if(act==='encontro'&&u>.55){const h=s.A.nico.point().lerp(s.A.lia.point(),q((u-.55)/.3));show(s,'radio',[h.x,h.y,h.z]);}
 
 if(act==='memoria'&&u>.45){const h=s.A.nico.point().lerp(s.A.lia.point(),q((u-.45)/.35));show(s,'paper',[h.x,h.y,h.z]);}
 if(act==='travessia'){
  const a=s.A.nico.point(),b=s.A.lia.point(),k=q((u-.60)/.2);P.plank.position.set((a.x+b.x)/2,lerp((a.y+b.y)/2,.20,k),1.45);P.plank.rotation.z=.05*(1-p);
 }
 s.motion={act,u,p,A,object};
}
function camera(s,info){
 const H=s.H,m=s.motion,n=m.A.nico,cam=info.cam,v=q(info.p),head=s.A.nico.head.getWorldPosition(new H.Vector3());let target=new H.Vector3(n.x+.6,1.1,n.z),off=new H.Vector3(3.8,2.0,5.8),fov=43;
 if(cam==='wide'){target.x=n.x+.9;off.set(4.3,2.6,7.0);}
 if(cam==='track'){target.y=1.03;off.set(2.5,1.35,4.4);}
 if(cam==='two'){const other=m.A.lia||m.A.ari;if(other)target.set((n.x+other.x)/2,1.18,(n.z+other.z)/2);off.set(2.1,1.25,4.4);fov=42;}
 if(cam==='close'){target.copy(head);off.set(1.45,.18,2.0);fov=35;}
 if(cam==='reverse'&&m.A.lia){target.copy(s.A.lia.head.getWorldPosition(new H.Vector3()));off.set(-1.4,.2,2.1);fov=36;}
 if(cam==='feet'){target.copy(s.A.nico.point('foot'));target.y=.12;off.set(1.2,.6,2.2);fov=39;}
 if(cam==='detail'){const ob=s.P[m.object];target.copy(ob?.visible?ob.getWorldPosition(new H.Vector3()):s.A.nico.point());if(['board','freezer','pump'].includes(m.object))target.y=1.25;if(m.object==='signal')target.y=2;off.set(1.3,.55,2.25);fov=38;if(m.object==='board'){target.y=1.9;off.set(1.0,.4,3.4);fov=42;}}
 if(cam==='over'){target.set(n.x+.7,.75,n.z-.15);off.set(.5,7.5,2.1);fov=43;}
 if(cam==='orbit'){const a=.1+.55*v;target.x=n.x+.8;off.set(5.7*Math.sin(a),1.9,5.7*Math.cos(a));}
 if(s.location==='diagram'){target.set(.5,1.6,2.6);off.set(.5,1.0,['detail','over'].includes(cam)?4.2:7.6);if(cam==='over')off.set(.3,4.2,4.2);fov=40;}
 off.multiplyScalar(1-.04*v);s.camera.position.copy(target).add(off);s.camera.lookAt(target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
}
function overlay(g,info,s){
 const m=s.motion,act=m.act,labels={cidade:'SÓ DUAS PESSOAS?',numeros:'CRESCER ≠ SER VIÁVEL',gargalo:'GARGALO GENÉTICO',copias:'DUAS CÓPIAS POR PESSOA*',oculto:'VARIANTES PODEM FICAR OCULTAS',quadrado:'UM MODELO RECESSIVO SIMPLES',chance:'PROBABILIDADE NÃO É UMA FILA',risco:'RISCO NÃO É DESTINO',acaso:'DERIVA GENÉTICA',mutacao:'MUTAÇÕES NÃO SÃO ENCOMENDAS',limite:'NÃO HÁ NÚMERO MÁGICO',diversidade:'QUANTIDADE ≠ DIVERSIDADE'};
 if(labels[act]&&!['close','reverse','feet'].includes(info.cam)){g.fillStyle='#153747ed';rr(g,510,70,1260,90,22);g.fill();text(g,labels[act],1140,116,{size:36,color:'#ffe5ae',align:'center'});}
 if(act==='quadrado'||act==='chance'){
  for(const [i,word]of ['AA','Aa','Aa','aa'].entries()){const ob=s.P.diagramNodes[i];if(!ob.visible)continue;const v=ob.getWorldPosition(new s.H.Vector3()).project(s.camera),x=(v.x*.5+.5)*1920,y=(-v.y*.5+.5)*1080;text(g,word,x,y+9,{size:48,color:i===3?'#efaa93':'#e6f3d3',align:'center'});}text(g,'25% neste exemplo, a cada gestação',1060,840,{size:34,color:'#ffe1ad',align:'center'});
 }
 if(act==='copias')text(g,'*maioria dos genes autossômicos',1190,850,{size:28,color:'#cfdfd8',align:'center'});
 for(const [a,b]of [[43,51],[story.duration*.49,story.duration*.49+8],[story.duration-14,story.duration-1]])if(info.globalT>=a&&info.globalT<=b){g.save();g.globalAlpha=q((info.globalT-a)/.5)*q((b-info.globalT)/.5);g.fillStyle='#153f49';rr(g,80,910,660,100,26);g.fill();text(g,'ENTÃO • INSCREVA-SE',410,960,{size:40,color:'#e4fff1',align:'center'});g.restore();}
}
for(const shot of story.shots)registerShot(shot.id,{kind:'3d',init(T){return world(T,beats[shot.params.beat].set);},draw(s,t,info){const b=beats[info.beat];animate(s,b,info.globalT-b.start,b.end-b.start);camera(s,info);},overlay(g,t,info,s){overlay(g,info,s);}});
