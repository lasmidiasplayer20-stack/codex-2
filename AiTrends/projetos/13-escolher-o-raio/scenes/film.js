import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {library,actor} from './rig.js';
const story=await(await fetch('/project/story/shots.json')).json(),S=x=>ease.inOut(clamp(x)),lerp=(a,b,p)=>a+(b-a)*p;
const shot=n=>story.shots.find(x=>x.params.cam===n),at=n=>shot(n).start,end=n=>shot(n).end,phase=(g,n)=>S((g-at(n))/(end(n)-at(n)));
let cached;export let current=null;
function make(T){if(cached)return cached;const L=library(T),H=T.THREE,scene=new H.Scene(),camera=new H.PerspectiveCamera(45,9/16,.05,100);scene.background=new H.Color('#667fba');scene.add(new H.HemisphereLight('#e2edfa','#7e8271',1.7));const key=new H.DirectionalLight('#ffe3af',2);key.position.set(-4,8,6);scene.add(key);
 const terrain=new H.Group();scene.add(terrain);const box=(c,p,s,parent=scene)=>{const m=L.mesh('box',c,p,s);parent.add(m);return m;};box('#d9b988',[0,-.14,0],[24,.28,20],terrain);box('#f2dfaf',[0,.005,0],[6,.035,8],terrain);box('#607c8e',[0,.01,-5],[24,.05,2.5]);for(let i=0;i<9;i++)box('#e3d3ae',[-12+i*3,.05,-5],[1.4,.01,.10]);
 // Keep pavement quiet so the independent silhouette is the visual subject.
 for(const x of [-4.3,5.4]){box('#8d785f',[x,.85,-3.3],[.17,1.7,.17]);const m=L.mesh('sphere','#7ca184',[x,2.05,-3.3],[1.0,1.1,1.0]);scene.add(m);}
 for(let i=0;i<6;i++){const h=3+i%3;box(['#70bec3','#ee9b91','#b39bd7','#e5c66d','#8bc2a3','#e9ac72'][i%3],[-11+i*4,h/2,-8],[3.2,h,2]);for(let j=0;j<3;j++)box('#edd5ad',[-12+i*4+j*.85,1.6,-6.97],[.35,.55,.03]);}

 // Colorful original street dressing. Keep the central shadow-reading area clear.
 const street=new H.Group();scene.add(street);
 for(let i=0;i<5;i++){
  const x=-7+i*2.6,z=-4.0,h=2.1+(i%2)*.35,col=['#ed967c','#80c4c8','#bca1df','#f1ce76','#8ac9a6'][i];
  box(col,[x,h/2,z],[2.25,h,1.6],street);box('#eee2c7',[x,h+.08,z],[2.4,.16,1.75],street);
  box('#406a7b',[x,h*.52,z+.82],[.72,1.25,.04],street);box('#ffe1a1',[x-.65,h*.58,z+.84],[.38,.55,.05],street);
  for(let k=0;k<6;k++)box(k%2?'#fff1cc':['#d86565','#4b9eaa','#8d73b6','#da9b4d','#5e9d72'][i],[x-.94+k*.38,h*.83,z+1.03],[.38,.09,.52],street);
  for(const dx of [-.76,.76]){box('#b87954',[x+dx,.25,z+.92],[.36,.38,.34],street);for(let f=0;f<3;f++){const stem=L.mesh('limb','#578d66',[x+dx+(f-1)*.08,.60,z+.95],[.012,.34,.012]);street.add(stem);street.add(L.mesh('sphere',['#ef6b83','#f7ce63','#b68ed5'][f],[x+dx+(f-1)*.08,.79+(f%2)*.06,z+.95],[.07,.07,.07]));}}
 }
 // Planters, cafe furniture and a bicycle are outside the actors' routes.
 for(const x of [-3.0,4.7]){box('#c27d60',[x,.28,2.7],[.65,.48,.55],street);for(let k=0;k<5;k++)street.add(L.mesh('sphere',['#76af79','#91c481','#5e9f7b'][k%3],[x+Math.sin(k*2)*.18,.72+(k%2)*.15,2.7+Math.cos(k*2)*.15],[.19,.26,.19]));}
 for(const z of [-2.1,-.9]){box('#cb8d60',[-3.2,.48,z],[1.25,.12,.52],street);for(const x of [-3.65,-2.75])box('#667c7e',[x,.23,z],[.06,.46,.40],street);}
 const bike=new H.Group();street.add(bike);bike.position.set(-3.6,0,-2.7);for(const x of [-.40,.40]){const wheel=new H.Mesh(new H.TorusGeometry(.30,.027,7,32),L.mat('#384b5d',true));wheel.position.set(x,.32,0);bike.add(wheel);}for(const [a,b]of [[[-.4,.32,0],[0,.70,0]],[[0,.70,0],[.4,.32,0]],[[-.4,.32,0],[.17,.32,0]],[[.17,.32,0],[0,.70,0]]])L.bone(bike,'#e67376',.027).set(a,b);
 // A few slow clouds provide depth without distracting flicker.
 const butterflies=[];for(let i=0;i<2;i++){const b=new H.Group();scene.add(b);const wings=[];for(const side of [-1,1]){const w=L.mesh('sphere',i?'#ee85ab':'#f0bc55',[side*.08,0,0],[.09,.025,.11],true);b.add(w);wings.push(w);}butterflies.push({root:b,wings});}
 const clouds=new H.Group();scene.add(clouds);for(let i=0;i<3;i++)for(let k=0;k<3;k++)clouds.add(L.mesh('sphere','#e6f4f5',[-9+i*8+k*.65,7.5+(i%2),-14],[.85,.35,.4],true));

 const room=new H.Group();scene.add(room);room.position.x=10;
 box('#e8d8ad',[0,-.08,0],[4,.14,4],room);box('#d5a6d1',[0,1.5,-1.7],[4,3,.15],room);box('#87b8cf',[.8,1.8,-1.60],[1.1,1.25,.04],room);box('#fff2cf',[.8,1.8,-1.54],[.04,1.3,.04],room);box('#fff2cf',[.8,1.8,-1.53],[1.2,.04,.04],room);box('#647a90',[-1.2,.35,-.8],[.9,.7,.9],room);box('#f1c964',[-1.2,.76,-.8],[.8,.15,.8],room);
 const house=new H.Group();scene.add(house);box('#f0ac78',[0,1.25,-.8],[3.3,2.5,2.8],house);box('#b56873',[0,2.55,-.8],[3.7,.22,3.2],house);box('#497e9d',[-.7,1.2,.63],[.75,1.1,.04],house);box('#ffdf91',[.7,1.35,.63],[.65,.75,.04],house);
 const protection=new H.Group();scene.add(protection);L.bone(protection,'#c8dce4',.035).set([0,2.7,-.8],[0,3.7,-.8]);
 const path=[[0,3.7,-.8],[0,2.72,-.8],[1.8,2.72,-.8],[1.8,2.72,.8],[1.8,-1.45,.8],[.6,-1.45,.8],[-.7,-1.45,.8]];
 for(let i=0;i<path.length-1;i++)L.bone(protection,'#d9a250',.033).set(path[i],path[i+1]);for(const x of [-.7,.6,1.8])L.bone(protection,'#d9a250',.032).set([x,-.7,.8],[x,-1.85,.8]);
 const soil=new H.Group();scene.add(soil);box('#a47662',[.6,-1.1,.2],[4.2,2,.10],soil);for(let i=0;i<12;i++)box(i%2?'#ba9073':'#946956',[-1.3+(i%4)*1.1,-.45-Math.floor(i/4)*.5,.27],[1,.025,.025],soil);
 const packets=[];for(let i=0;i<18;i++){const m=L.mesh('sphere','#fff18d',[0,0,0],[.065,.065,.065],true);scene.add(m);packets.push(m);}
 const groundRings=[];for(let i=0;i<3;i++){const m=new H.Mesh(new H.TorusGeometry(.5,.025,8,64),L.mat('#ffd86a',true));m.rotation.x=-Math.PI/2;m.position.set(.6,-1.45,.8);scene.add(m);groundRings.push(m);}
 const bolt=new H.Group();scene.add(bolt);const boltBones=[];for(let i=0;i<10;i++)boltBones.push(L.bone(bolt,'#fff3a5',.035));
 const tree=L.mesh('sphere','#5eab9d',[-2.5,2,1],[.65,.9,.65]);scene.add(tree);L.bone(scene,'#926d61',.10).set([-2.5,0,1],[-2.5,2,1]);
 const shield=new H.Group();scene.add(shield);box('#3b7088',[0,0,0],[.38,.6,.18],shield);box('#71e4bc',[0,0,.1],[.17,.25,.03],shield);
 const wires=new H.Group();scene.add(wires);L.bone(wires,'#596a7d',.022).set([3,2,1],[.9,2,1]);L.bone(wires,'#596a7d',.022).set([.9,2,1],[.9,1,1]);
 const actors={nico:actor(T,'nico'),lia:actor(T,'lia')};Object.values(actors).forEach(a=>scene.add(a.root));
 const rain=new H.InstancedMesh(new H.CylinderGeometry(.008,.008,.16,5),L.mat('#a6d3e6',true),100);rain.frustumCulled=false;scene.add(rain);const dummy=new H.Object3D();
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;const stage={render(){renderer.render(scene,camera);},dispose(){}};
 return cached={room,terrain,H,L,scene,camera,stage,actors,house,protection,path,soil,packets,groundRings,bolt,boltBones,tree,shield,wires,rain,dummy,clouds,butterflies};}
function along(path,u){let lens=[],total=0;for(let i=0;i<path.length-1;i++){let d=Math.hypot(...path[i].map((v,k)=>v-path[i+1][k]));lens.push(d);total+=d;}let d=clamp(u)*total;for(let i=0;i<lens.length;i++){if(d<=lens[i])return path[i].map((v,k)=>lerp(v,path[i+1][k],d/lens[i]));d-=lens[i];}return path.at(-1);}
function draw(s,t,info){current=s;const H=s.H,g=info.globalT,c=info.cam,p=phase(g,c),idx=story.shots.findIndex(x=>x.params.cam===c),inside=idx>=23;
 s.clouds.position.x=.15*Math.sin(g*.06);s.butterflies.forEach(b=>b.root.visible=false);
 const approach=c==='enter'?phase(g,c):g>=end('enter')?1:0;const sidestep=g<at('power')?0:g<end('power')?phase(g,'power'):g<at('roof')?1:g<end('roof')?1-phase(g,'roof'):0;const nx=lerp(-1.0,-.7,approach)-sidestep*.8,nz=lerp(3.1,.7,approach);const walking=['power','roof','enter'].includes(c);
 const gesture=['tree','roof','rod','route','metal','choice'].includes(c)?'point':['intro','risk'].includes(c)?'surprise':'think';
 s.actors.nico.update({x:nx,z:nz,yaw:c==='power'?Math.PI:c==='roof'?0:-Math.PI/2,time:g,moving:walking,distance:c==='enter'?approach*2.4:sidestep*.8,expr:idx<5?'surprised':idx>22?'smile':'determined',gesture,gestureWeight:.75});
 s.actors.lia.update({x:lerp(1.0,-.7,approach),z:lerp(3.0,.7,approach),yaw:-Math.PI/2,time:g,moving:c==='enter',distance:approach*2.85,expr:'smile',gesture:'point',gestureWeight:.7});
 s.actors.nico.root.visible=s.actors.lia.root.visible=!['rod','cable','earth','spread','route','surge','shield','system','wait'].includes(c);
 const indoor=['safe','lia2','wait','end'].includes(c);s.room.visible=indoor;s.terrain.visible=!['earth','spread','route'].includes(c);s.house.visible=!indoor;s.protection.visible=g>=at('overview')&&!indoor;s.soil.visible=['earth','spread','route'].includes(c);s.shield.visible=['surge','shield','system'].includes(c);s.shield.position.set(.9,1,1.1);s.wires.visible=['surge','shield','system'].includes(c);
 // Single sustained illustrative discharge, no rapid flashes or exposure changes.
 s.bolt.visible=['tree','roof','catch'].includes(c);const endpoint=c==='tree'?[-2.5,2.8,1]:c==='roof'?[.4,2.7,-.8]:[0,3.7,-.8];for(let i=0;i<10;i++){const point=j=>[lerp(endpoint[0]+.8,endpoint[0],j/10)+(j>0&&j<10?(j%2?.16:-.16):0),lerp(7,endpoint[1],j/10),endpoint[2]];s.boltBones[i].set(point(i),point(i+1));}s.bolt.scale.setScalar(Math.max(.001,S(p*4)));
 const currentOn=['catch','cable','earth','spread','route'].includes(c);s.packets.forEach((m,i)=>{m.visible=currentOn;const u=((g*.19+i/18)%1);m.position.set(...along(s.path,u));});
 s.groundRings.forEach((m,i)=>{m.visible=c==='spread';const u=(g*.35+i/3)%1;m.scale.setScalar(.3+u*2.6);});
 const rainy=!indoor;s.rain.visible=rainy;for(let i=0;i<100;i++){const u=1-((g*1.1+i*.618033)%1);s.dummy.position.set(-3.7+(i%10)*.77,.15+u*6,2+Math.floor(i/10)*.27);s.dummy.rotation.set(0,0,-.08);s.dummy.updateMatrix();s.rain.setMatrixAt(i,s.dummy.matrix);}s.rain.instanceMatrix.needsUpdate=true;
 let target=new H.Vector3(0,2,1),pos=new H.Vector3(4,4.4,12),fov=47;
 if(['intro','power','choice','end','safe'].includes(c)){target.set(nx,1.55,nz);pos.set(nx+1.4,2.7,nz+5.5);}
 if(c==='tree'){target.set(-2,2,1);pos.set(-.5,3.1,7);}
 if(['roof','risk','overview','system'].includes(c)){target.set(0,2,-.1);pos.set(7*Math.sin(.65-.65*p),4.8,1+8*Math.cos(.65-.65*p));}
 if(['rod','metal','catch'].includes(c)){target.set(0,3.2,-.8);pos.set(1.9*Math.cos(p),4.1,3.5);fov=40;}
 if(c==='cable'){target.set(1.8,lerp(2.5,.2,p),.8);pos.set(4,target.y+.5,4);fov=42;}
 if(['earth','spread'].includes(c)){target.set(.6,-1,.8);pos.set(3.4,.6,5);s.house.visible=false;fov=44;}
 if(c==='route'){target.set(.6,1.0,.3);pos.set(5,3.7,10);s.house.visible=false;fov=48;}
 if(['surge','shield'].includes(c)){target.set(.9,1.25,1.1);pos.set(2.2,2.1,4);fov=39;}
 if(['lia','myth','stop'].includes(c)){target.set(1,1.65,3);pos.set(1.8,2.2,6);fov=40;}
 if(c==='enter'){target.set(0,1.4,1.9);pos.set(-3+2*p,3.4,8);}
 
 if(indoor){s.actors.nico.update({x:9.3,z:0,yaw:-Math.PI/2,time:g,moving:false,expr:'joy'});s.actors.lia.update({x:10.5,z:.1,yaw:-Math.PI/2,time:g,moving:false,expr:'smile'});target.set(9.9,1.5,0);pos.set(11,3,7);}
 const drift=new H.Vector3(.12*Math.sin(p*Math.PI),.08*p,-.22*p);s.camera.position.copy(pos).add(drift);s.camera.lookAt(target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
 s.state={cam:c,rainDirection:'down',actors:[nx,nz],discharge:s.bolt.visible};}
const labels=Object.fromEntries(story.shots.map(x=>[x.params.cam,x.params.label]));
function overlay(g,t,info){const lines=labels[info.cam];g.fillStyle='#152740ee';rr(g,50,135,980,190,28);g.fill();for(let i=0;i<lines.length;i++)text(g,lines[i],540,200+i*65,{size:i?44:42,color:i?'#ffe17e':'#f6fff8',align:'center'});text(g,info.globalT<12?'PODER FICTÍCIO • FÍSICA REAL':'ENTÃO • CIÊNCIA EM UMA HIPÓTESE',540,1810,{size:24,color:'#fff1d7',align:'center'});if(info.cam==='wait'){g.fillStyle='#152740f0';rr(g,160,790,760,190,35);g.fill();text(g,'30 MINUTOS',540,870,{size:65,color:'#ffe17e',align:'center'});text(g,'APÓS O ÚLTIMO TROVÃO',540,937,{size:30,color:'#ffffff',align:'center'});}}
for(const x of story.shots)registerShot(x.id,{kind:'3d',init:make,draw,overlay});
