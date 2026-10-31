import {registerShot,clamp,ease,text,rr} from '/engine/core.js';import {library,actor} from './rig.js';import {minecraftWorld} from './minecraft-world.js';
const S=x=>ease.inOut(clamp(x)),mix=(a,b,p)=>a+(b-a)*p;const PERIOD=359/24;let cached;export let current;
const A=[-1.3,.30,1.3],B=[-2.2,3.25,-.4],C=[.9,6.05,-.4],D=[1.9,6.05,-.4],E=[1.3,.25,2.4],F=[-2.4,.25,2.75];
function make(T){if(cached)return cached;const H=T.THREE,L=library(T),scene=new H.Scene(),camera=new H.PerspectiveCamera(43,9/16,.04,150);scene.background=new H.Color('#a8dceb');scene.add(new H.HemisphereLight('#e8f6ff','#6f8164',1.7));const sun=new H.DirectionalLight('#ffe4b9',1.9);sun.position.set(-4,10,6);scene.add(sun);const world=minecraftWorld(T,scene,{arena:true});const cube=new H.BoxGeometry(1,1,1);function block(par,mat,p,size){const m=new H.Mesh(cube,typeof mat==='string'?L.mat(mat):mat);m.position.set(...p);m.scale.set(...size);par.add(m);return m;}
const stageGroup=new H.Group();scene.add(stageGroup);for(let x=-4;x<=4;x++)for(let z=-2;z<=3;z++)block(stageGroup,world.mats.cobblestone,[x,0,z],[1,.5,1]);
// Launch pad recessed in the arena; only the piston head moves upward.
block(stageGroup,world.mats.stone,[A[0],-.3,A[2]],[.9,.7,.9]);const floorHead=block(stageGroup,world.mats.oak_planks,[A[0],.22,A[2]],[.95,.16,.95]);const floorRod=block(stageGroup,world.mats.oak_log,[A[0],.05,A[2]],[.24,.3,.24]);
const pedestal=block(stageGroup,world.mats.oak_planks,[-.35,.78,1.675],[.3,1.2,.65]);block(stageGroup,world.mats.oak_planks,[-.5,1.42,1.675],[.6,.08,.65]);const button=block(stageGroup,'#e13b32',[-.59,1.50,1.675],[.36,.08,.36]);
// A genuine rectangular slime pad, and fixed oak supports behind the flight path.
const slimeMat=new H.MeshLambertMaterial({color:'#78d34b',transparent:true,opacity:.85});const slime=block(stageGroup,slimeMat,[B[0],2.75,B[2]],[1,1,1]);for(let y=.75;y<2.25;y+=1)block(stageGroup,world.mats.oak_log,[B[0],y,B[2]],[.75,1,.75]);for(const dx of [-.28,.28])block(slime,'#4b8d36',[dx,-.08,.51],[.16,.14,.018]);block(slime,'#4b8d36',[0,-.29,.51],[.28,.06,.018]);
for(let y=.75;y<5.8;y+=1)block(stageGroup,world.mats.oak_log,[.9,y,-.4],[.75,1,.75]);block(stageGroup,world.mats.oak_planks,[1.4,5.925,-.4],[2.1,.25,1.25]);
const upperBase=block(stageGroup,world.mats.stone,[.275,6.85,-.4],[1,1,1]);const upperHead=block(stageGroup,world.mats.oak_planks,[.7125,6.85,-.4],[.125,1,1]);const upperRod=block(stageGroup,world.mats.oak_log,[.8,6.85,-.4],[.1,.25,.25]);
// Stair-stepped water chute, with low transparent glass rails.
const points=[D,[2.6,4.9,.3],[2.9,3.8,1.0],[2.6,2.65,1.7],[2.1,1.45,2.3],E].map(p=>new H.Vector3(...p)),curve=new H.CatmullRomCurve3(points,false,'centripetal');const glass=world.mats.glass.clone();glass.transparent=true;glass.opacity=.22;glass.depthWrite=false;const water=world.mats.water.clone();water.transparent=true;water.opacity=.78;
for(let i=0;i<=20;i++){const q=i/20,p=curve.getPoint(q),dir=curve.getTangent(q),normal=new H.Vector3(-dir.z,0,dir.x).normalize();block(stageGroup,world.mats.oak_planks,[p.x,p.y-.19,p.z],[.98,.38,.82]);block(stageGroup,water,[p.x,p.y+.012,p.z],[.92,.025,.77]);for(const sign of [-1,1]){const v=p.clone().addScaledVector(normal,sign*.63);block(stageGroup,glass,[v.x,v.y+.16,v.z],[.08,.36,.60]);}}
// Redstone-like original circuit accents; no textures or assets taken from the game.
const lamps=[];for(let i=0;i<13;i++){const x=mix(-1.3,.9,i/12),z=1.15-.12*Math.sin(i);lamps.push(block(stageGroup,'#803d39',[x,.265,z],[.10,.025,.10]));}const lampMat=new H.MeshBasicMaterial({color:'#e4523b'});const litLamps=[];for(let i=0;i<lamps.length;i++){const l=block(stageGroup,lampMat,[lamps[i].position.x,.29,lamps[i].position.z],[.07,.015,.07]);litLamps.push(l);}
const bubbles=[];for(let i=0;i<12;i++)bubbles.push(block(stageGroup,'#c6f3f7',[0,0,0],[.035,.035,.035]));
const nico=actor(T,'nico');scene.add(nico.root);const renderer=T.getRenderer();renderer.shadowMap.enabled=false;camera.position.set(8.0,7.2,13.5);camera.lookAt(.2,4.5,.8);camera.updateProjectionMatrix();const stage={render(){renderer.render(scene,camera);},dispose(){}};return cached={H,scene,camera,stage,world,stageGroup,floorHead,floorRod,button,slime,upperHead,upperRod,lamps,litLamps,bubbles,nico,curve};}
// Independently keyed rigid body parts: classic Minecraft limbs remain unsegmented.
const POSE_FIELDS=['torso','roll','legF','legB','armF','armB','twist','nod'];
const POSE_KEYS=[
[0,0,0,0,0,1.238,0,0,0],[.35,0,0,0,0,1.238,0,0,0],[1.05,0,0,0,0,1.171,0,0,0],[1.20,0,0,0,0,1.171,0,0,0],
[1.45,-.18,.08,.25,-.20,2.55,1.90,.08,-.12],[2.0,.22,-.08,-.45,.40,1.80,2.40,-.10,.08],[2.7,-.12,.08,.30,-.25,2.40,1.70,.10,-.06],
[3.10,.05,0,.20,.10,1.60,1.40,0,.05],[3.30,-.30,0,.55,-.55,.65,.80,0,.15],[3.58,.18,-.10,-.40,.35,2.40,2.0,-.08,-.12],
[4.30,-.12,.12,.35,-.40,1.60,2.50,.14,.08],[5.20,.10,.02,.25,.15,1.50,1.30,0,-.04],[5.50,-.24,0,.50,.35,.45,.60,0,.12],
[5.85,0,0,0,0,.80,.50,0,0],[6.0,-.18,.10,.22,.22,1.40,1.20,.08,-.08],[6.6,-.08,-.10,.25,.20,.70,1.50,-.08,.08],
[7.2,0,0,.55,.35,1.0,1.0,0,.04],[7.5,.37,-.10,.80,.35,.60,1.40,-.12,.12],[8.0,.20,.12,.40,.75,1.50,.65,.12,-.10],
[8.6,.40,-.12,.75,.20,.65,1.45,-.12,.10],[9.2,.25,.12,.35,.75,1.45,.60,.12,-.10],[9.8,.40,-.10,.70,.25,.70,1.40,-.10,.10],
[10.3,.20,0,.40,.55,1.20,.80,0,.02],[10.5,-.30,0,.55,-.55,1.20,.80,0,.12],[10.8,-.05,0,.20,-.20,.40,-.40,0,0],
[13.1,0,0,0,0,0,0,0,0],[13.9,-.04,0,0,0,.55,0,0,.03],[14.5,0,0,0,0,1.13,0,0,0],[PERIOD,0,0,0,0,1.238,0,0,0]
];
function bodyPose(q,phase,distance){let i=0;while(i<POSE_KEYS.length-2&&q>POSE_KEYS[i+1][0])i++;const a=POSE_KEYS[i],b=POSE_KEYS[i+1],u=S((q-a[0])/(b[0]-a[0]));const out={};POSE_FIELDS.forEach((k,j)=>out[k]=mix(a[j+1],b[j+1],u));out.armRollF=phase==='slide'?-.30:phase==='launch'||phase==='bounce'?-.18:0;out.armRollB=-out.armRollF;
if(phase==='return'||phase==='approach'){const start=phase==='return'?10.5:13.1,end=phase==='return'?13.1:PERIOD,t=(q-start)/(end-start),w=S(t/.14)*(1-S((t-.78)/.20)),sw=Math.sin(distance/1.1*Math.PI*2)*.62;out.legF=mix(out.legF,sw,w);out.legB=mix(out.legB,-sw,w);out.armB=mix(out.armB,sw*.8,w);if(phase==='return')out.armF=mix(out.armF,-sw*.8,w);out.torso=mix(out.torso,-.12,w);out.twist=mix(out.twist,sw*.10,w);out.roll+=Math.sin(distance/1.1*Math.PI*4)*.035*w;}
return out;}

function draw(s,t,info){current=s;const H=s.H,k=((Math.round(info.globalT*24)%359)+359)%359,q=k/24;let p=new H.Vector3(...A),yaw=0,headYaw=-.6,expr='smile',moving=false,distance=0,air=false,lean=0,hand=[.58,1.30,.375],handB=undefined;let phase='button',push=0,launch=0;
const press=S((q-.35)/.65);if(q<1.2){hand=[.58,mix(1.30,1.255,press),.375];}
else if(q<3.3){phase='launch';const u=(q-1.2)/2.1,v=S(u);p.set(mix(A[0],B[0],v),mix(A[1],B[1],u)+2*Math.sin(Math.PI*u),mix(A[2],B[2],v));expr='surprised';air=true;hand=[.48,2.10,.375];handB=[.48,2.10,-.375];lean=-.10*Math.sin(Math.PI*u);}
else if(q<5.5){phase='bounce';const u=(q-3.3)/2.2;p.x=mix(B[0],C[0],S(u/.78));p.y=mix(B[1],C[1],u)+1.4*Math.sin(Math.PI*u);p.z=u<.78?mix(B[2],.9,S(u/.5)):mix(.9,C[2],S((u-.78)/.22));expr='surprised';air=true;hand=[.48,2.10,.375];handB=[.48,2.10,-.375];}
else if(q<7.2){phase='push';push=S((q-5.9)/1.3);p.set(mix(C[0],D[0],push),C[1],C[2]);expr='surprised';hand=[.42,1.3,.375];handB=[.42,1.3,-.375];}
else if(q<10.5){phase='slide';const u=(q-7.2)/3.3;p.copy(s.curve.getPoint(u));const d=s.curve.getTangent(u);yaw=Math.atan2(-d.z,d.x);headYaw=0;expr='surprised';hand=[.50,1.4,.375];handB=[.50,1.4,-.375];lean=0;p.y+=.055*(1-Math.cos(2*Math.PI*6*u))*.5;headYaw=.18*Math.sin(2*Math.PI*2*u);}
else if(q<13.1){phase='return';const u=(q-10.5)/2.6,v=S(u);p.set(mix(E[0],F[0],v),mix(E[1],F[1],v),mix(E[2],F[2],v));yaw=Math.atan2(-(F[2]-E[2]),F[0]-E[0]);headYaw=0;moving=true;distance=p.distanceTo(new H.Vector3(...E));expr='surprised';hand=undefined;}
else{phase='approach';const u=(q-13.1)/(PERIOD-13.1),v=S(u);p.set(mix(F[0],A[0],v),mix(F[1],A[1],v),mix(F[2],A[2],v));yaw=mix(.92,0,v);headYaw=mix(-.5,-.6,v);moving=u<.88;distance=p.distanceTo(new H.Vector3(...F));expr=u<.55?'surprised':'smile';hand=[mix(.30,.58,v),mix(.95,1.3,v),.375];}
// Local support compression, all values derived from periodic phase, reset each draw.
const squash=Math.abs(q-3.3)<.22?.15*Math.cos((q-3.3)/.22*Math.PI/2):0;s.slime.scale.set(1,1-squash,1);s.slime.position.y=2.25+(1-squash)/2;if(Math.abs(q-3.3)<.22)p.y-=squash;
if(q>=1.2&&q<1.75)launch=Math.sin((q-1.2)/.55*Math.PI)*.36;s.floorHead.position.y=.22+launch;s.floorRod.position.y=.05+launch/2;s.floorRod.scale.y=.3+launch;
if(q>=7.2&&q<7.85)push=1-S((q-7.2)/.65);else if(q>=7.85)push=0;s.upperHead.position.x=.7125+push;s.upperRod.visible=push>.005;s.upperRod.position.x=.775+push/2;s.upperRod.scale.x=Math.max(.001,push);
s.button.position.y=1.50-(q<1.2?press*.035:q<1.65?.035*(1-S((q-1.2)/.45)):0);s.litLamps.forEach((m,i)=>m.visible=q>1&&q<7.5&&q>1+i*.045);s.bubbles.forEach((m,i)=>{m.visible=phase==='slide';if(m.visible){const z=clamp((q-7.2)/3.3-i*.018);const v=s.curve.getPoint(z);m.position.set(v.x+Math.sin(i*2.4)*.25,v.y+.10+(i%3)*.045,v.z+Math.cos(i*2.4)*.2);}});
const pose=bodyPose(q,phase,distance),grounded=!air||Math.abs(q-3.3)<.14||Math.abs(q-5.5)<.12;s.nico.update({time:q,x:p.x,y:p.y,z:p.z,yaw,headYaw,expr,moving,distance,hand:undefined,handB:undefined,pose,grounded});s.nico.root.rotation.z=lean;s.nico.shadow.visible=!air;const follow=q>6.8&&q<11.2?Math.sin(Math.PI*(q-6.8)/4.4)**2:0;const eye=new H.Vector3(8,7.2,13.5).lerp(p.clone().add(new H.Vector3(4.8,3.6,7.2)),.60*follow),look=new H.Vector3(.2,4.5,.8).lerp(p.clone().add(new H.Vector3(0,1.1,0)),.62*follow);s.camera.position.copy(eye);s.camera.lookAt(look);s.camera.updateProjectionMatrix();s.state={cam:'loop',time:q,phase,frame:k,set:'minecraft contraption',cup_error:0,position:p.toArray(),pose:s.nico.poseState(),follow,button:s.button.position.y,launch,push};}
function overlay(g,t,info){g.fillStyle='#17334be8';rr(g,75,110,930,150,14);g.fill();text(g,'NÃO APERTA',540,171,{size:65,color:'#fff7df',align:'center'});text(g,'DE NOVO!',540,235,{size:57,color:'#ffe44f',align:'center'});text(g,'Então',85,1810,{size:31,color:'#fff5dc',align:'left'});}
registerShot('s01',{kind:'3d',init:make,draw,overlay});
