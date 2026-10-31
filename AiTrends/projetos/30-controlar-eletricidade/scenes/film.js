import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {library,actor} from './rig.js';import {minecraftWorld} from './minecraft-world.js';
const cfg=await(await fetch('/project/config.json')).json(),story=await(await fetch('/project/story/shots.json')).json();
const S=x=>ease.inOut(clamp(x)),M=(a,b,u)=>a+(b-a)*u;let cache;export let current;
function init(T){if(cache)return cache;const H=T.THREE,L=library(T),scene=new H.Scene(),camera=new H.PerspectiveCamera(44,9/16,.05,100);scene.background=new H.Color('#8bd5f1');const hemi=new H.HemisphereLight('#e3f9ff','#807b52',1.6);scene.add(hemi);const sun=new H.DirectionalLight('#ffe4ab',1.25);sun.position.set(-4,8,6);scene.add(sun);const world=minecraftWorld(T,scene,{arena:true,river:cfg.theme===3});
 const props={},make=(name,color,pos,scale,par=scene)=>{const m=L.mesh('box',color,pos,scale);par.add(m);props[name]=m;return m;},group=name=>{const g=new H.Group();scene.add(g);props[name]=g;return g;};
 // Spatially separated props; no coplanar replacement floor.
 const tower=group('tower');for(let i=0;i<6;i++)make('tower'+i,'#bb9864',[-3,i+.5,-1],[1,1,1],tower);
 const log=make('log','#936239',[1,1.5,0],[.35,4.4,.25]);const rock=make('rock','#8a9caa',[.1,.5,.3],[.9,1,.9]);
 const lamp=group('lamp');for(let x of [-3,3]){make('post'+x,'#384c70',[x,1.6,-1],[.14,3.2,.14],lamp);make('lamp'+x,'#ffe25f',[x,3.2,-1],[.65,.5,.65],lamp);}const bulb=make('bulb','#ffffa7',[0,0,0],[.3,.3,.3]);
 const arcs=group('arcs');const electricMat=new H.MeshBasicMaterial({color:'#4bebfa'});for(let i=0;i<16;i++)make('arc'+i,'#69eafa',[0,0,0],[.12,.12,.12],arcs).material=electricMat;
 const court=group('court');const board=make('board','#eeeeec',[2.6,2.7,-.5],[.15,1.2,1.5],court);make('pole','#51627b',[2.8,1.3,-.5],[.12,2.6,.12],court);for(let i=0;i<4;i++)make('hoop'+i,'#ef7653',[2.15+(i<2?0:(i===2?-.28:.28)),2.35,-.5+(i<2?(i===0?-.35:.35):0)],[i<2?.65:.08,.08,i<2?.08:.7],court);const ball=make('ball','#fca340',[0,0,0],[.33,.33,.33]);const blocks=group('blocks');for(let i=0;i<5;i++)make('stack'+i,['#ec9375','#64c8d4','#efcf65','#bd96e1','#9cd997'][i],[0,.2+i*.4,0],[.45,.4,.45],blocks);
 const bench=group('bench');make('seat','#c89d66',[0,.48,-1],[3,.16,.65],bench);make('back','#d2a66c',[0,.95,-1.3],[3,.8,.12],bench);for(let x of [-1.1,1.1])make('leg'+x,'#5e6b6c',[x,.24,-1],[.15,.48,.5],bench);
 const bridge=group('bridge');for(let i=0;i<7;i++)make('bridge'+i,'#d7ad73',[-1.5+i*.5,.12,0],[.48,.22,1],bridge);const water=make('water','#4199d5',[0,-.1,0],[4,.16,2.5]);
 const stone=make('stone','#9ba4af',[-.6,.2,0],[.5,.4,.5]);const bandage=make('bandage','#f1e9cf',[0,.1,0],[.3,.15,.3]);
 const crate=group('crate');make('cratebody','#ba8548',[0,.4,0],[.8,.8,.8],crate);for(let z of [-.407,.407])make('cratebrace'+z,'#efd08c',[0,.4,z],[.6,.13,.03],crate);
 const clock=group('clock');make('clockback','#183c5b',[0,.35,0],[.75,.7,.2],clock);make('clockface','#ffd95d',[0,.37,.115],[.55,.45,.02],clock);
 const tree=group('tree');make('trunk','#9b7148',[0,1,0],[.5,2,.5],tree);for(let x of [-.7,0,.7])make('leaves'+x,'#65b865',[x,2.5+(x===0?.5:0),0],[1.1,1.3,1.3],tree);
 const sapling=group('sapling');make('sapstem','#a07549',[0,.25,0],[.07,.5,.07],sapling);make('sapleaf','#76cc83',[0,.55,0],[.45,.4,.4],sapling);const buildings=group('buildings');for(let i=0;i<4;i++){make('building'+i,['#d3ac91','#8faac8','#ad93b9','#7bafa5'][i],[-5+i*3,2,-7],[1.6,4+i*.5,1.4],buildings);for(let j=0;j<5;j++)make('window'+i+'-'+j,'#ffe5a4',[-5+i*3,.5+j*.65,-6.28],[.8,.22,.03],buildings);}
 const n=actor(T,'nico'),l=actor(T,'lia');scene.add(n.root,l.root);const render=T.getRenderer();render.shadowMap.enabled=false;const stage={render(){render.render(scene,camera);},dispose(){}};return cache={H,scene,camera,stage,world,hemi,sun,props,n,l};}
function draw(s,t,info){current=s;const H=s.H,k=cfg.theme,a=info.act,g=info.globalT,sh=story.shots[a],u=clamp((g-sh.start)/(sh.end-sh.start)),v=S(u),P=s.props;
 Object.values(P).forEach(o=>o.visible=false);const show=(...names)=>names.forEach(n=>{P[n].visible=true;P[n].traverse(x=>x.visible=true);});
 const n={time:g,x:-.8,y:0,z:.7,yaw:-Math.PI/2,headYaw:0,expr:'smile',moving:false,pose:{torso:.025*Math.sin(g*2),armF:.07*Math.sin(g*1.8),armB:-.06*Math.sin(g*1.8)}},l={time:g,x:1.1,y:0,z:.4,yaw:-Math.PI/2,expr:'smile',pose:{armF:.08*Math.sin(g*1.7),armB:-.06*Math.sin(g*1.7)}};let lia=true,attach=null,attachL=null,focus=[0,1,.2],view=a%8,extra={};
 function walk(o,from,to,q,dist){o.x=M(from[0],to[0],q);o.z=M(from[1],to[1],q);o.yaw=Math.atan2(-(to[1]-from[1]),to[0]-from[0]);o.moving=true;o.distance=dist*q;delete o.pose;}
 function lean(o,z=0,arm=0){o.pose={torso:z,armF:arm,armB:arm*.85,legF:.08,legB:-.08,nod:-z*.45};}
 function hold(o,angle=1.25){o.pose={torso:-.1,armF:angle,armB:angle,legF:.12,legB:-.12};}
 if(k===0){
  n.yaw=0;show('tower');lia=a>=2;
  if(a===0){n.x=-1.9;n.z=-1;n.y=M(5.8,0,S(u/.75));n.grounded=false;n.pose={torso:-.4,armF:-1.8,armB:1.5,legF:.7,legB:-.5};focus=[-2,2,0];view=1;}
  if(a===1){n.x=-2;n.z=.2;n.pose={torso:-.12,armF:1.9,armB:1.7};}
  if(a>=2){show('log','rock');P.log.position.set(.9,1.9,.325);P.log.rotation.z=a===2?M(0,-.9,v):-.9;l.x=1.5;l.z=.5;l.expr='surprised';}
  if(a===2){n.expr='surprised';n.pose={torso:.15,armF:1.4,armB:1.5};}
  if(a===3){walk(n,[-2,.7],[.2,.7],v,2.2);n.expr='determined';n.pose={...s.n.poseState(),armF:1.7,armB:1.7,torso:-.2,legF:Math.sin(v*12)*.5,legB:-Math.sin(v*12)*.5};}
  if(a===4||a===5){n.x=.2;n.z=.7;n.expr='determined';hold(n,1.8);P.log.position.set(.6,a===4?1.7: M(1.7,2.05,v),.325);P.log.rotation.z=a===4?-.9:M(-.9,-1.2,v);}
  if(a===6){n.x=.2;hold(n,1.8);P.log.position.set(.6,2.05,.325);P.log.rotation.z=-1.2;walk(l,[1.5,.5],[3,2.3],v,2.34);l.expr='joy';}
  if(a===7){n.x=-.4;n.z=1.8;l.x=1.1;l.z=1.8;P.log.position.set(.6,2.05,.325);P.log.rotation.z=-1.2;n.expr='joy';}
 }
 if(k===1){show('lamp');n.x=-.5;n.z=.8;lia=a>=3;show('bulb');attach='bulb';n.pose={torso:-.07,armF:1.45,armB:.15};l.x=1.4;l.z=.6;const power=a===0?.1:a===5?1-v:a<5?1:a===6?.12:.05;show('arcs');
  if(a===3||a===4){walk(l,[1.4,.6],[2.4,2],v,1.72);l.expr='surprised';n.expr='surprised';n.pose={torso:.18,armF:1.9,armB:-1.1};}
  if(a===5){n.pose={torso:M(.18,0,v),armF:M(1.9,.1,v),armB:M(-1.1,0,v)};P.bulb.visible=false;}
  if(a>=6){P.arcs.visible=false;P['lamp-3'].material.color.set('#715f50');P['lamp3'].material.color.set('#715f50');}
  else{P['lamp-3'].material.color.set(a>=1?'#ffffff':'#715f50');P['lamp3'].material.color.set(a>=1?'#ffffff':'#715f50');}
  extra.power=power;
 }
 if(k===2||k===6){show('court','ball');n.x=-1.5;n.z=.7;l.x=-1.6;l.z=-.9;const thrower=(k===2&&a===0)||(k===6&&a===6)?l:n;const shotBall=(k===2&&[0,2].includes(a))||(k===6&&[0,1,3,6].includes(a));
  if(shotBall){thrower.pose={torso:-.1,armF:1.5+v*.9,armB:1.4+v*.9};extra.ballFlight=v;extra.thrower=thrower===l?'l':'n';}
  else attach='ball';
  if(k===2){if(a===1){n.pose={armF:1.4,armB:.2};extra.copy=true;}if(a===3){P.ball.visible=false;show('blocks');P.blocks.position.set(.2,0,.2);const count=Math.min(5,1+Math.floor(u*5));for(let i=0;i<5;i++)P['stack'+i].visible=i<count;hold(n);n.x=-.5;extra.copy=true;}
   if(a>=4){P.court.visible=false;P.ball.visible=false;show('bench');n.x=-.8;n.z=.5;l.x=.7;l.z=.5;l.expr='sad';n.expr=a===5?'surprised':'smile';if(a>=6){n.headYaw=-.4;n.pose={torso:-.12,armF:.3,armB:.1};l.pose={torso:.08,armF:.7,armB:.1};}}
  }else{
   if(a===1){n.yaw=Math.PI/2;n.headYaw=0;}
   if(a===2){walk(l,[-1.4,-.8],[2.9,-1.3],v,4.32);n.expr='sad';}
   if(a===3){n.yaw=Math.PI*.5;n.expr='surprised';}
   if(a===4){lia=false;n.expr='sad';lean(n,.12,.3);}
   if(a===5){P.ball.visible=false;n.pose={armF:-.2,armB:.2};l.x=-1.6;l.z=-.8;}
   if(a===6){n.x=-.8;n.z=1.2;n.pose={armF:2.2,armB:-1.9};n.expr='joy';l.expr='joy';}
   if(a===7){P.ball.visible=false;n.x=-.8;l.x=.8;l.z=.7;n.pose={armF:1.4,armB:-1.4};l.pose={armF:-1.4,armB:1.4};n.expr=l.expr='joy';}
  }
 }
 if(k===3){show('bridge','water');n.x=-2;n.z=.8;l.x=1;l.y=.24;l.z=0;extra.counter=a<5?Math.max(1,Math.round(8-g*.43)):null;
  if(a<2){n.expr='surprised';n.pose={armF:1.4,armB:.2};}
  if(a===2){n.pose={torso:-.13,armF:1.7,armB:1.2};l.headYaw=-.5;}
  if(a>=3){for(let i=3;i<6;i++){const q=a===3?v:1;P['bridge'+i].position.y=.12-q*(.8+(i-3)*.15);P['bridge'+i].rotation.z=q*(i%2?.5:-.4);}}
  if(a===3){n.x=-1.3;n.z=.3;l.expr='surprised';l.pose={armF:1.8,armB:-1.8,legF:.3,legB:-.2};}
  if(a===4){extra.pull=true;n.yaw=0;l.yaw=Math.PI;n.x=M(-1.3,-2.2,v);n.z=.45;l.x=M(.6,-1.5,v);l.z=.45;n.pose={torso:.2,armF:1.5,armB:.4,legF:.5*Math.sin(v*12),legB:-.5*Math.sin(v*12)};l.pose={torso:-.25,armF:1.4,armB:1.4,legF:.3,legB:-.3};}
  if(a>=5){n.x=-2.8;n.z=2;l.x=-1.8;l.y=0;l.z=2;focus=[-1.8,1,.8];n.expr=l.expr='joy';if(a===6){n.pose={armF:1.4,armB:1.4};l.pose={armF:-1.4,armB:-1.4};l.x=-1.9;} }
 }
 if(k===4){show('stone');n.x=M(-1.8,.7,a<3?v:1);n.z=.7;l.x=1.8;l.z=.4;
  if(a===0){n.x=M(-1.8,.2,v);n.y=.18*Math.sin(Math.PI*u);n.pose={torso:.4*Math.sin(Math.PI*u),armF:-1.2,armB:1.5,legF:.6,legB:-.4};}
  if(a===1){n.x=.3;n.expr='joy';n.pose={armF:1.9,armB:-1.8};}
  if(a===2){walk(n,[.2,.7],[1.3,.7],v,1.1);n.pose={torso:.12,legF:.3*Math.sin(v*9),legB:-.12*Math.sin(v*9),armF:.2,armB:-.2};n.expr='surprised';}
  if(a===3){n.x=.9;n.expr='surprised';l.pose={armF:1.5,armB:.2};}
  if(a===4||a===5){n.x=.4;n.expr='sad';lean(n,.15,.4);focus=[.5,.9,.6];}
  if(a>=6){show('bench','bandage');n.x=-.6;n.z=-.65;n.y=-.29;n.grounded=false;n.pose={torso:.05,legF:1.2,legB:1.15,armF:.3,armB:.3};l.x=.9;l.z=.3;l.pose={torso:.12,armF:1.1,armB:.3};extra.bandage=true;}
 }
 if(k===5){show('crate');l.x=.5;l.z=.1;P.crate.position.set(.7,.75,.7);hold(l);let opacity=a===0?1-S((u-.2)/.65):a<5?0:a===5?S(u/.7):1;extra.opacity=opacity;
  if(a===2){walk(n,[-2,.9],[2,.9],v,4);}
  if(a===3){n.x=1.9;n.z=1.3;l.expr='sad';l.pose={torso:.2,armF:1.1,armB:1.1};}
  if(a===4){n.x=1.6;n.z=.7;hold(n);P.crate.position.set(1.1,1.1+.15*Math.sin(v*Math.PI),.7);l.expr='surprised';l.pose={armF:1.7,armB:-1.5};}
  if(a===5){n.x=1.5;n.z=.8;n.pose={armF:1.4,armB:.3};}
  if(a>=6){walk(n,[1.5,.8],[3.3,2.0],v,2.16);walk(l,[.3,.8],[2.1,2.0],v,2.16);hold(n,1.1);hold(l,1.1);extra.crateHands=true;focus=[M(1,2.7,v),1,1.2];}
 }
 if(k===7){show('clock','ball','crate');P.clock.position.set(-2,.2,.5);P.ball.position.set(.3,a===1?M(3,.2,v):.2,.6);P.crate.position.set(1,.0,.5);l.x=1;l.z=-.3;n.x=-1;n.z=.6;
  if(a===0){n.pose={armF:1.4,armB:.1};extra.clock='07:00';}
  if(a===1){walk(n,[-1,.6],[.25,.6],v,1.25);if(u>.7){attach='ball';n.pose={armF:1.4,armB:1.2};}}
  if(a===2||a===3){P.ball.visible=false;P.crate.position.set(1,M(1,0,v),.5);P.crate.rotation.z=v*.4;l.expr='surprised';l.pose={armF:1.6,armB:-1.6};if(a===3){n.pose={armF:1.9,armB:-1.9};n.expr='joy';}}
  if(a===4){P.ball.visible=false;P.crate.visible=false;n.expr='sad';lean(n,.2,.2);extra.day=300;}
  if(a===5){P.ball.visible=false;walk(n,[-1,.6],[.45,.6],v,1.45);hold(n);P.crate.position.set(.7,1,.5);l.expr='joy';}
  if(a>=6){P.ball.visible=false;P.crate.position.set(1,.0,.5);n.expr=l.expr='joy';n.pose={armF:1.5,armB:-1.5};extra.clock=a===6?'00:01':'UM NOVO DIA';}
 }
 if(k===8){show('bench','tree');n.x=-.7;n.z=.7;l.x=.8;l.z=.7;P.tree.position.set(2.5,0,-2);P.tree.scale.setScalar(a<3?M(.25,1,(a+v)/3):1);extra.year=2026+Math.round((a+v)*50);
  if(a>=1){show('buildings');P.buildings.scale.y=M(.3,1,Math.min(1,(a+v)/4));}
  if(a===0){show('sapling');P.sapling.position.set(.5,.1,.5);n.pose={torso:-.2,armF:1.1,armB:.6};}
  if(a===2){n.headYaw=-.6;n.pose={armF:1.4,armB:.1};}
  if(a===3||a===4){lia=false;n.expr='sad';n.x=-.7;n.z=-.65;n.y=-.29;n.grounded=false;n.pose={torso:.1,legF:1.1,legB:1.1,armF:.2,armB:.2};}
  if(a===5){walk(l,[3,1],[.9,.7],v,2.12);show('sapling');attachL='sapling';l.expr='joy';}
  if(a===6||a===7){show('sapling');P.sapling.position.set(.3,0,1);n.x=-.4;n.z=1.4;l.x=1;l.z=1.4;n.pose={torso:a===6?-.3:-.08,armF:1,armB:.7};l.pose={torso:a===6?.3:.05,armF:-1,armB:-.7};n.expr=l.expr='joy';}
 }
 s.n.update(n);s.l.update(l);s.l.root.visible=lia;if(extra.pull){const delta=s.n.point('hand').sub(s.l.point('hand'));s.l.root.position.add(delta);s.l.root.updateMatrixWorld(true);}
 // Restore opaque materials after invisibility, then vary only in that story.
 s.n.root.traverse(o=>{if(o.isMesh&&o.name){for(const mat of Array.isArray(o.material)?o.material:[o.material]){mat.transparent=extra.opacity!==undefined&&extra.opacity<1;mat.opacity=extra.opacity??1;mat.depthWrite=!(extra.opacity!==undefined&&extra.opacity<.1);}}});s.n.shadow.visible=(extra.opacity??1)>.02;
 if(attach&&P[attach].visible)P[attach].position.copy(s.n.point('hand'));
 if(attachL)P[attachL].position.copy(s.l.point('hand'));
 if(extra.ballFlight!==undefined){const start=(extra.thrower==='l'?s.l:s.n).point('hand'),end=new H.Vector3(2.12,2.38,-.5),q=clamp((extra.ballFlight-.10)/.75);P.ball.position.copy(start).lerp(end,q);P.ball.position.y+=2.0*Math.sin(Math.PI*q);if(extra.ballFlight>.85)P.ball.position.y=M(2.38,.2,S((extra.ballFlight-.85)/.15));P.ball.rotation.set(q*5,0,q*2);}
 if(extra.crateHands){const h1=s.n.point('handB'),h2=s.l.point('hand');P.crate.position.copy(h1).add(h2).multiplyScalar(.5);}
 if(extra.bandage){P.bandage.position.copy(s.n.point('foot'));P.bandage.position.y+=.06;}
 if(extra.power!==undefined){const hand=s.n.point('hand'),end=new H.Vector3(a===0?hand.x+.4:3,a===0?hand.y+.4:3.2,-1);for(let i=0;i<16;i++){const qa=i/16,qb=(i+1)/16,A=hand.clone().lerp(end,qa),B=hand.clone().lerp(end,qb);A.y+=Math.sin(i*1.7+g*2)*.10*extra.power;B.y+=Math.sin((i+1)*1.7+g*2)*.10*extra.power;const line=B.clone().sub(A);P['arc'+i].position.copy(A).add(B).multiplyScalar(.5);P['arc'+i].scale.set(.035*extra.power,line.length(),.035*extra.power);P['arc'+i].quaternion.setFromUnitVectors(new H.Vector3(0,1,0),line.normalize());}}

 const f=new H.Vector3(...focus);if([0,2,4,5,6].includes(view)){f.x=M(f.x,n.x,.55);f.z=M(f.z,n.z,.45);}
 let offset=[[4.5,2.5,7],[7,6,10],[3.6,1.6,5.0],[1.2,8.5,5.3],[4.4,2.8,7],[6.4,1.65,3.4],[4.0,2.1,6.5],[5.0,3,8]][view];let eye=f.clone().add(new H.Vector3(...offset));const angle=(v-.5)*.10;eye.sub(f).applyAxisAngle(new H.Vector3(0,1,0),angle).add(f);if(k===0&&a===0){f.set(-2,2.6,0);eye.set(5,6.5,12);}s.camera.position.copy(eye);s.camera.lookAt(f);s.camera.updateProjectionMatrix();s.scene.updateMatrixWorld(true);s.state={theme:k,act:a,time:g,pose:s.n.poseState(),camera:[...s.camera.position],extra,source:'authored original story'};s.extra=extra;
}
function overlay(g,t,info,s){const a=info.act;g.fillStyle='#09253eea';rr(g,50,130,980,150,20);g.fill();const label=info.label;let size=label.length>24?34:label.length>19?39:46;text(g,label,540,223,{size,color:'#fff2a5',align:'center'});
 const e=s.extra||{};if(e.counter!==undefined&&e.counter!==null){g.fillStyle='#8d2635ed';rr(g,640,370,340,100,12);g.fill();text(g,`00:00:0${e.counter}`,810,436,{size:42,color:'#fff8dd',align:'center'});}if(e.copy){text(g,'COPIADO ✓',540,360,{size:42,color:'#78edec',align:'center'});}if(e.clock){g.fillStyle='#17344be0';rr(g,190,360,700,95,14);g.fill();text(g,e.clock,540,421,{size:44,color:'#b1ffe5',align:'center'});}if(e.day)text(g,`DIA ${e.day}`,540,380,{size:65,color:'#ffe180',align:'center'});if(e.year)text(g,`${e.year}`,540,360,{size:54,color:'#e8fff5',align:'center'});text(g,'Então',85,1815,{size:31,color:'#fff4cf'});
}
for(const sh of story.shots)registerShot(sh.id,{kind:'3d',init,draw,overlay});
