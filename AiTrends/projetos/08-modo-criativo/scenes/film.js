import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {world,setCurrent} from './world.js';
const beats=await(await fetch('/project/story/beats.json')).json(),story=await(await fetch('/project/story/shots.json')).json(),q=x=>ease.inOut(clamp(x)),lerp=(a,b,p)=>a+(b-a)*p;
function local(o,p){const x=p[0]-o.x,z=p[2]-o.z,c=Math.cos(o.yaw),s=Math.sin(o.yaw);return[x*c-z*s,p[1]-(o.y||0),x*s+z*c];}
function animate(s,b,t,d){const u=clamp(t/d),p=q(u),act=b.action,P=s.P,A={};for(const ob of s.hidden||[])ob.visible=true;s.hidden=[];for(const ob of Object.values(P))if(ob?.isObject3D)ob.visible=false;for(const m of P.cups)m.visible=false;P.ground.visible=true;for(const a of Object.values(s.A)){a.root.visible=false;a.root.rotation.z=0;}
 const show=(id,pos)=>{P[id].visible=true;if(pos)P[id].position.set(...pos);return P[id];};
 const n=A.nico={x:-1.6,z:1.1,y:0,yaw:-.65,time:t,headYaw:0,moving:false,distance:0,expr:'smile'},l=A.lia={x:1.5,z:1.2,y:0,yaw:-2.2,time:t,headYaw:0,moving:false,distance:0,expr:'smile'};
 let object='menu',held='',holder='nico',pitch=0,mode=true;
 const hand=(id,pos)=>A[id].hand=local(A[id],pos),hold=(id,prop)=>{held=prop;holder=id;A[id].hand=[.40,1.14,.15];object=prop;};
 function walk(id,start,end,seconds=3.4){const o=A[id],w=q(t/seconds),dx=end[0]-start[0],dz=end[1]-start[1];o.x=lerp(start[0],end[0],w);o.z=lerp(start[1],end[1],w);o.yaw=Math.atan2(-dz,dx);o.distance=Math.hypot(dx,dz)*w;o.moving=t<seconds;o.gaitWeight=q(t/.3)*q((seconds-t)/.3);}
 function build(parts,start=.12,window=.6){for(let i=0;i<parts.length;i++){const grow=q((u-start-window*i/parts.length)/.14);parts[i].visible=grow>.001;parts[i].scale.y=Math.max(.001,grow);}}
 function fly(start,end,height=4){const w=q(t/Math.min(8,d*.75));n.x=lerp(start,end,w);n.y=height*(.15+.85*q(t/3));n.z=-.1-.45*Math.sin(w*Math.PI);n.yaw=-.18;n.hand=[.10,1.98,.25];n.handB=[.10,1.98,-.25];pitch=-Math.PI/2*.7*q(t/2);n.nod=-pitch;n.moving=false;}
 switch(act){
 case 'menu':n.gesture='point';n.gestureWeight=q(t/1.0);l.expr='surprised';hold('nico','menu');show('ring',[n.x,.04,n.z]).scale.setScalar(.4+.8*q(t/2));break;
 case 'cadeira':n.x=-1.2;l.x=1.3;l.gesture='point';show('chair',[.1,lerp(.65,0,q((u-.35)/.3)),1]);P.chair.scale.setScalar(Math.max(.02,q(u/.2)));hand('nico',[-.5,1.1,1.1]);object='chair';break;
 case 'copia':n.x=-1.5;n.z=2.2;l.x=1.5;l.z=2.2;show('table',[0,0,1]);hold('nico','cup');for(let i=0;i<10;i++){const c=P.cups[i];c.visible=u>.12+i*.055;c.position.set(-.75+(i%5)*.36,.94,1+(i<5?-.23:.23));c.scale.setScalar(.95);}object='cup';l.gesture='think';break;
 case 'voo':delete A.lia;n.x=-1.2;n.y=6*q(t/5);n.z=1;n.gesture='surprise';n.gestureWeight=q(t/2)*q((d-t)/2);n.expr=t<2?'surprised':'joy';show('ring',[-1.2,.1,1]).scale.setScalar(1+.7*q(t/4));object='ring';break;
 case 'rua':delete A.lia;fly(-6,7,6);object='menu';break;
 case 'limites':n.gesture='think';l.gesture='point';show('table',[.3,0,.2]);show('notebook',[.3,.95,.2]);show('chair',[-.5,0,1.9]);object='notebook';break;
 case 'abrigo':n.x=-2.5;l.x=2.5;show('shelter',[0,0,-.4]);build(P.shelterParts);show('grid',[0,.04,-.4]);n.gesture='point';l.hand=[.43,1.1,.14];object='shelter';break;
 case 'ponte':n.x=-2.7;n.z=1.5;l.x=2.8;l.z=1.5;show('bridge',[0,0,.4]);build(P.bridgeBoards,.15,.55);n.gesture='point';l.gesture='point';object='bridge';break;
 case 'teste':show('bridge',[0,0,.4]);walk('nico',[-3.2,.5],[3.2,.5],6);walk('lia',[-4.3,.8],[2.1,.8],6);n.y=.06+.20*q((1.9-Math.abs(n.x))/.35);l.y=.06+.20*q((1.9-Math.abs(l.x))/.35);object='bridge';break;
 case 'jardim':n.x=-1.7;l.x=1.8;l.gesture='point';show('creationTree',[.2,0,-.6]);const a=lerp(1,2,q(u/.3)),z=lerp(a,.85,q((u-.45)/.3));P.creationTree.scale.setScalar(z);n.gesture='point';object='creationTree';break;
 case 'ferramentas':n.x=-.65;l.x=.65;n.z=l.z=1.6;n.yaw=0;l.yaw=Math.PI;A.sol={...l,x:2.2,z:1.9,yaw:-2.2};show('table',[0,0,.0]);hold('nico','tool');n.hand=[.54,1.20,.15];l.hand=[.54,1.20,.15];object='tool';break;
 case 'ouro':show('table',[0,0,.0]);show('gold',[0,.94,0]);for(let i=0;i<P.golds.length;i++)P.golds[i].visible=u>i*.025;n.hand=[.4,1.17,.16];l.expr='surprised';object='gold';break;
 case 'valor':show('gold',[0,.15,-.3]);for(const m of P.golds)m.visible=true;l.gesture='think';n.gesture='point';object='gold';break;
 case 'comida':show('food',[.2,0,-.2]);for(let i=0;i<P.foods.length;i++)P.foods[i].visible=u>i*.035;n.x=-2;l.x=2;l.gesture='point';n.gesture='point';object='food';break;
 case 'multidao':n.x=-.7;l.x=1.6;A.ari={...l,x:-2.3,z:2.1,yaw:-.4,gesture:'point'};A.sol={...l,x:3,z:1.8,gesture:'think'};hold('nico','menu');n.expr='tired';l.gesture='point';object='menu';break;
 case 'alto':delete A.lia;n.x=-1.7;n.y=1.5+4*p;show('tower',[1.5,0,-1]);build(P.floors,.04,.65);n.gesture='point';object='tower';break;
 case 'sombra':n.x=-2;l.x=1.4;l.gesture='point';show('tower',[1.7+1.8*q((u-.3)/.4),0,-1.3]);for(const f of P.floors){f.visible=true;f.scale.y=1;}show('towerShadow',[P.tower.position.x-.5,.09,1.4]);show('creationTree',[-.1,0,-.5]).scale.setScalar(.65);object='tower';n.gesture='think';break;
 case 'desfazer':n.x=-1.5;l.gesture='think';hold('nico','menu');show('loose',[.5,0,-.2]);for(let i=0;i<P.blocks.length;i++){const m=P.blocks[i];m.visible=i<4&&u<.18+i*.13;m.position.set((i%3)*.8-.8,1.0+Math.floor(i/3)*.6,0);}object='menu';break;
 case 'protegido':delete A.lia;n.x=-1.3;n.y=4*Math.sin(Math.PI*q(t/Math.min(7,d*.8)));n.gesture='surprise';n.gestureWeight=q(t/.7)*q((Math.min(7,d*.8)-t)/.7);show('ring',[n.x,n.y+.04,n.z]).scale.setScalar(.8);object='ring';break;
 case 'blocos':n.x=-2;l.x=2.4;show('loose',[.3,0,-.5]);for(let i=0;i<9;i++){const m=P.blocks[i],fall=q((u-.1-i*.015)/.22),catchUp=q((u-.48)/.25);m.visible=true;m.position.set((i%3)*.8-.8,3+Math.floor(i/3)*.6-fall*2+catchUp*.6,0);m.rotation.z=.12*(i-4)*fall;}n.hand=[.36,1.65,.24];n.handB=[.30,1.65,-.24];n.expr='determined';l.gesture='point';object='loose';break;
 case 'consertar':n.x=-1.7;l.x=1.7;show('loose',[0,0,0]);for(let i=0;i<9;i++){const m=P.blocks[i],w=q((u-i*.055)/.30);m.position.set((i%3)*.8-.8,2-w*1.7,0);m.rotation.z=.12*(i-4)*(1-w);m.visible=w<.98;}hold('nico','menu');l.gesture='point';object='loose';break;
 case 'fuga':delete A.lia;fly(-2,1.5,5);object='house';break;
 case 'ilha':delete A.lia;n.x=-1.8;n.z=1.5;show('house',[.7,0,-1]);P.house.scale.setScalar(Math.max(.01,q(u/.4)));show('chair',[-.5,0,1]);n.gesture='think';n.expr='sad';object='house';break;
 case 'sentido':delete A.lia;show('house',[.7,0,-1]);P.house.scale.setScalar(1);show('chair',[-.2,0,1.0]);n.x=-.2;n.z=1.08;n.yaw=-Math.PI/2;n.sit=true;n.expr='sad';object='chair';break;
 case 'volta':n.x=-.9;n.yaw=0;l.yaw=Math.PI;n.y=3.0*(1-q(t/3.2));n.z=1.6;l.x=.9;l.z=1.6;show('table',[0,0,.1]);hold('nico','plank');l.hand=[.4,1.12,.14];object='plank';break;
 case 'regras':show('table',[.2,0,.2]);show('notebook',[.2,.95,.2]);n.x=-1.6;l.x=1.8;n.gesture='think';l.gesture='point';object='notebook';break;
 case 'maquete':n.x=-2.3;l.x=2.4;show('mini',[0,1.1,-.2]);P.mini.rotation.y=.5*p;for(let i=0;i<P.miniBuildings.length;i++){const m=P.miniBuildings[i];m.position.x=(i%3)*.7-.7+(i===4?.38*q((u-.2)/.4):0);m.scale.y=1-(i===7?.45*q((u-.4)/.4):0);}show('grid',[0,.08,-.2]);n.gesture='point';l.gesture='point';object='mini';break;
 case 'mutirao':n.x=-1;n.z=1.6;n.yaw=0;l.x=1;l.z=1.6;l.yaw=Math.PI;show('table',[0,0,.2]);hold('nico','plank');l.hand=[.40,1.16,.12];A.ari={...l,x:2.7,z:1.9,yaw:-2.1,gesture:'point'};A.sol={...n,x:-2.8,z:2,yaw:-.4,gesture:'think'};show('shelter',[0,0,-1.8]);for(const f of P.shelterParts){f.visible=true;f.scale.y=1;}object='plank';break;
 case 'cidade':delete A.lia;fly(-5,5,4.5);show('shelter',[0,0,-.3]);for(const f of P.shelterParts){f.visible=true;f.scale.y=1;}show('creationTree',[-3,0,1.2]).scale.setScalar(.9);object='shelter';break;
 case 'escolha':hold('nico','menu');l.gesture='point';n.expr='determined';object='menu';break;
 case 'cadeirafinal':show('chair',[1.2,0,1.1]);l.x=1.2;l.z=1.16;l.yaw=-Math.PI/2;l.sit=true;n.x=-1.4;n.gesture='think';mode=false;object='chair';break;
 case 'final':n.x=-1.5;l.x=1.2;n.gesture='point';l.gesture='think';show('chair',[.1,0,-.6]);mode=false;object='chair';break;
 }
 for(const [id,o]of Object.entries(A)){if(o.gesture&&o.gestureWeight===undefined)o.gestureWeight=q(t/.55)*(.88+.12*Math.cos(t*.7));if(!pitch)o.headYaw=(o.headYaw||0)+.10*Math.sin(t*.65);s.A[id].root.visible=true;s.A[id].update(o);if(s.A[id].shadow){s.A[id].shadow.material.opacity=.18*clamp(1-(o.y||0)/.8);s.A[id].shadow.visible=(o.y||0)<.8;}if(id==='nico'&&pitch){s.A[id].root.rotation.z=pitch;s.A[id].root.updateMatrixWorld(true);}}
 if(held){const h=s.A[holder].point();show(held,[h.x,h.y,h.z]);if(held==='cup')P.cup.position.y-=.13;if(held==='menu'){P.menu.rotation.y=-.2;P.menu.position.y+=.12;}}
 // Two-person object transfer uses reachable hand endpoints, not guessed screen coordinates.
 if(act==='ferramentas'&&u>.35){const h=s.A.nico.point().lerp(s.A.lia.point(),q((u-.35)/.35));const prop=P[held];prop.position.copy(h);}
 if(['volta','mutirao'].includes(act)&&u>.35){const a=s.A.nico.point(),b=s.A.lia.point(),w=q((u-.35)/.2);P.plank.position.copy(a.clone().lerp(a.clone().add(b).multiplyScalar(.5),w));P.plank.rotation.y=-Math.atan2(b.z-a.z,b.x-a.x)*w;}
 if(act==='sentido'){const head=s.A.nico.head.getWorldPosition(new s.H.Vector3());if(head.y<1.1)throw Error('Seated head height invalid');}
 s.motion={act,u,p,A,object,mode,held};
}
function camera(s,info){const H=s.H,m=s.motion,cam=info.cam,n=m.A.nico,p=q(info.p),a=s.A.nico,head=a.head.getWorldPosition(new H.Vector3());let target=new H.Vector3(n.x+.4,(n.y||0)+1.1,n.z),off=new H.Vector3(2.5,1.6,4.2),fov=43;const ob=s.P[m.object],object=ob?.visible?ob.getWorldPosition(new H.Vector3()):a.point();if(ob?.visible)object.y+=({chair:.65,cup:.13,table:.85,shelter:1.35,bridge:.50,creationTree:1.1,gold:.35,food:.35,tower:3.2,loose:1.8,house:.9,mini:.25}[m.object]||0);
 switch(cam){
 case 'wide':target.set(m.A.lia?(n.x+m.A.lia.x)/2:n.x+.5,(n.y||0)+1.2,n.z-.6);off.set(3,3.2,7);break;
 case 'two':if(m.A.lia)target.set((n.x+m.A.lia.x)/2,(n.y||0)*.5+1.1,(n.z+m.A.lia.z)/2);off.set(1.5,1.05,4.2);break;
 case 'close':target.copy(head);off.copy(new H.Vector3(1,0,0).applyQuaternion(a.head.getWorldQuaternion(new H.Quaternion()))).multiplyScalar(1.85);off.y+=.15;fov=37;break;
 case 'reverse':{const li=s.A.lia;if(m.A.lia){target.copy(li.head.getWorldPosition(new H.Vector3()));off.copy(new H.Vector3(1,0,0).applyQuaternion(li.head.getWorldQuaternion(new H.Quaternion()))).multiplyScalar(1.85);off.y+=.15;}fov=37;break;}
 case 'hand':target.copy(object);off.set(.65,.48,1.2);fov=38;break;
 case 'detail':target.copy(object);if(['tower','shelter','house','creationTree'].includes(m.object))target.y+=1.15;off.set(1.5,.65,2.6);fov=40;break;
 case 'menu':target.copy(a.point());off.set(.7,.5,1.2);fov=39;break;
 case 'feet':target.copy(a.point('foot'));off.set(1.05,.40,1.6);fov=39;break;
 case 'low':target.set(n.x+.3,(n.y||0)+1.0,n.z);off.set(1,-.78,3.8);fov=47;break;
 case 'ground':target.set(-1,1.05,1.6);off.set(1.8,-.75,4.6);fov=46;break;
 case 'track':off.set(.8,1,4);break;
 case 'fly':target.copy(head);off.set(2.3,1.1,4.2);fov=49;break;
 case 'rise':target.set(n.x+.5,(n.y||0)+1.4,n.z);off.set(3,1.0+3*p,5.8);fov=46;break;
 case 'street':target.copy(head);off.set(-3,-1.0,6);fov=49;break;
 case 'orbit':{const angle=.25+.85*p;target.set(s.location==='space'?0:n.x+.6,(n.y||0)+1.2,n.z-.5);off.set(6.3*Math.sin(angle),2.8,6.3*Math.cos(angle));break;}
 case 'over':target.copy(object);off.set(.2,5.8,1.2);fov=44;break;
 case 'build':target.copy(object);target.y+=m.object==='tower'?2.2:1.0;off.set(3.4,2.0,5.2);fov=43;break;
 case 'reveal':target.copy(head);off.set(lerp(1,4,p),lerp(.2,3.2,p),lerp(2,7,p));fov=43;break;
 }
 if(m.object==='loose'&&['hand','detail'].includes(cam)){off.set(2.1,1.0,3.4);fov=44;}if(['wide','two','track'].includes(cam))off.applyAxisAngle(new H.Vector3(0,1,0),.13*(p-.5));off.multiplyScalar(1-.04*p);s.camera.position.copy(target).add(off);s.camera.lookAt(target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
 if(['detail','menu','hand','build','over'].includes(cam)){for(const [id,actor]of Object.entries(s.A)){if(cam==='hand'&&m.held&&id==='nico')continue;actor.root.visible=false;}}
 if(cam==='close')for(const [id,actor]of Object.entries(s.A))if(id!=='nico')actor.root.visible=false;if(cam==='reverse')for(const [id,actor]of Object.entries(s.A))if(id!=='lia')actor.root.visible=false;
 // Foreground geometry cutaway only on close inserts; restores deterministically next frame.
 if(['close','reverse','hand','menu','detail'].includes(cam)){const subject=cam==='close'?s.A.nico.root:cam==='reverse'?s.A.lia.root:ob;const belongs=(v,o)=>{for(let a=v;a;a=a.parent)if(a===o)return true;return false;};s.scene.updateMatrixWorld(true);const ray=new H.Raycaster(s.camera.position,target.clone().sub(s.camera.position).normalize(),.04,Math.max(.1,s.camera.position.distanceTo(target)-.18));for(let i=0;i<8;i++){const hits=ray.intersectObjects(s.scene.children,true).filter(h=>h.object.visible&&!belongs(h.object,subject)&&!Object.values(s.A).some(a=>belongs(h.object,a.root)));if(!hits.length)break;hits[0].object.visible=false;s.hidden.push(hits[0].object);}}
}
function overlay(g,t,info,s){const m=s.motion;const labels={menu:'E SE VOCÊ PUDESSE CRIAR TUDO?',limites:'PODER NÃO É PERMISSÃO',valor:'CRIAR ≠ DISTRIBUIR',alto:'QUEM FICA LÁ EMBAIXO?',desfazer:'DESFAZER NÃO APAGA TUDO',protegido:'PROTEÇÃO NÃO É RESPONSABILIDADE',sentido:'E AGORA?',regras:'OUVIR • TESTAR • COMBINAR',escolha:'DISPONÍVEL ≠ OBRIGATÓRIO'};
 if(labels[m.act]&&['wide','over','build'].includes(info.cam)){g.fillStyle='#193748ed';rr(g,300,65,1320,92,22);g.fill();text(g,labels[m.act],960,111,{size:40,color:'#ffe6a2',align:'center'});}
 if(m.mode&&['menu','wide'].includes(info.cam)&&!['limites','sentido'].includes(m.act)){g.fillStyle='#172d40e8';rr(g,1480,120,340,245,20);g.fill();text(g,'MODO CRIATIVO',1650,157,{size:28,color:'#a5edce',align:'center'});for(const [i,v]of ['CRIAR','VOAR','DESFAZER'].entries())text(g,v,1650,208+i*55,{size:29,color:i===1&&['voo','rua','cidade'].includes(m.act)?'#ffdb85':'#e2e8dd',align:'center'});}
 for(const [a,b]of [[43,51],[story.duration*.49,story.duration*.49+8],[story.duration-14,story.duration-1]])if(info.globalT>=a&&info.globalT<=b){g.save();g.globalAlpha=q((info.globalT-a)/.5)*q((b-info.globalT)/.5);g.fillStyle='#153f49';rr(g,80,910,660,100,26);g.fill();text(g,'ENTÃO • INSCREVA-SE',410,960,{size:40,color:'#e4fff1',align:'center'});g.restore();}
}
for(const sh of story.shots)registerShot(sh.id,{kind:'3d',init(T){return world(T,beats[sh.params.beat].set);},draw(s,t,info){setCurrent(s);const b=beats[info.beat];animate(s,b,info.globalT-b.start,b.end-b.start);camera(s,info);},overlay(g,t,info,s){overlay(g,t,info,s);}});
