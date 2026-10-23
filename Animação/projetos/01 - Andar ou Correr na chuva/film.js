/* Procedural geometry, materials, character rig, weather, diagrams and editing.
   No external images, video textures or imported character models. */
import {stage,chapters} from './story.js';
const T=window.THREE;
const timings=await (await fetch('timing.json')).json();
const W=1280,H=720,SCALE=1.5,canvas=document.querySelector('#output'),ctx=canvas.getContext('2d',{alpha:false,willReadFrequently:true});
const renderer=new T.WebGLRenderer({antialias:false,alpha:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
canvas.width=1920;canvas.height=1080;renderer.setSize(1920,1080);renderer.setPixelRatio(1);renderer.outputEncoding=T.sRGBEncoding;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
const scene=new T.Scene();scene.background=new T.Color('#839cae');scene.fog=new T.Fog('#839cae',25,75);
const camera=new T.PerspectiveCamera(38,W/H,.1,130);
scene.add(new T.HemisphereLight(0xe2f6ff,0x6c6c91,.60));const sun=new T.DirectionalLight(0xffe2b1,.80);sun.position.set(-8,16,8);scene.add(sun);
const palette={ink:0x253448,cream:0xffeed4,yellow:0xffca59,orange:0xf79b4c,teal:0x57bdb6,blue:0x5d99c0,skin:0xeeb187};
const mats=new Map();function mat(color){if(!mats.has(color))mats.set(color,new T.MeshToonMaterial({color:new T.Color(color).convertSRGBToLinear()}));return mats.get(color);}
const outlineMat=new T.MeshBasicMaterial({color:palette.ink,side:T.BackSide});
const ballGeo=new T.SphereGeometry(1,8,6),boxGeo=new T.BoxGeometry(1,1,1),cylGeo=new T.CylinderGeometry(1,1,1,10),coneGeo=new T.ConeGeometry(1,1,10);
function mesh(geo,color,parent=scene,pos=[0,0,0],scale=[1,1,1],outline=false){const m=new T.Mesh(geo,mat(color));m.position.set(...pos);m.scale.set(...scale);parent.add(m);if(outline){const edge=new T.Mesh(geo,outlineMat);edge.scale.setScalar(1.045);m.add(edge);}return m;}
const ball=(c,p,xyz,s,ink=false)=>mesh(ballGeo,c,p,xyz,s,ink);
const box=(c,p,xyz,s,ink=false)=>mesh(boxGeo,c,p,xyz,s,ink);
function cylinder(c,p,xyz,s,ink=false){return mesh(cylGeo,c,p,xyz,s,ink);}
let seed=142857;function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}const mix=(a,b,t)=>a+(b-a)*t;const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const world=new T.Group();scene.add(world);
// A toy-town street, assembled from solid geometry.
box(0x8ea49f,world,[0,-.28,-2],[58,.4,32]);box(0x536879,world,[0,-.055,1],[54,.14,8]);
box(0xb9c3bf,world,[0,.04,6],[54,.22,2]);box(0xaab7b7,world,[0,.04,-4],[54,.22,2]);
for(let x=-26;x<27;x+=2.3)box(0xefddad,world,[x,.024,1],[1.05,.012,.10]);
for(let i=0;i<35;i++){const x=-26+random()*52,z=-2.3+random()*6.4;const p=mesh(new T.CircleGeometry(1,18),0x88b3c4,world,[x,.032,z],[.3+random(),.14+random()*.35,1]);p.rotation.x=-Math.PI/2;p.rotation.z=random()*Math.PI;}
const buildings=[];
for(let i=0;i<9;i++){const g=new T.Group();g.position.set(-24+i*6,0,-10);world.add(g);const height=3.2+random()*3.5;const colors=[0xd3a997,0x7ea4b0,0xb5b0c3,0xc8b586,0x8fae9f];box(colors[i%5],g,[0,height/2,0],[4.8,height,3.4],true);box(0x657487,g,[0,height+.13,0],[5.1,.28,3.65],true);
 for(let row=0;row<Math.floor(height/1.25);row++)for(let col=0;col<3;col++){mesh(new T.PlaneGeometry(1,1),0x526879,g,[-1.5+col*1.5,.8+row*1.25,1.73],[.78,.82,1]);mesh(new T.PlaneGeometry(1,1),(row+col+i)%3?0xf1cd83:0x91b9c4,g,[-1.5+col*1.5,.8+row*1.25,1.77],[.59,.65,1]);}
 const awning=box([0x4c908b,0xde8c76,0xe7bc6d][i%3],g,[0,2,2],[4.9,.20,1.05],true);awning.rotation.x=.18;box(0x40556b,g,[0,.75,1.76],[1,.0+1.5,.08]);buildings.push(g);
}
function tree(x,z){const g=new T.Group();g.position.set(x,0,z);world.add(g);cylinder(0x8f7866,g,[0,1,0],[.16,2,.16]);for(let i=0;i<3;i++)ball([0x6d9a8a,0x7eab95,0x8db39a][i],g,[(i-1)*.43,2.2+(i===1?.4:0),0],[.8,.95,.76],true);ball(0x758b88,g,[0,.14,0],[.7,.12,.6]);}
for(const x of [-19,-11,-3,6,15,23])tree(x,-4.2);
function lamp(x,z){const g=new T.Group();g.position.set(x,0,z);world.add(g);cylinder(0x526679,g,[0,1.6,0],[.075,3.2,.075]);ball(0x4a6072,g,[0,.2,0],[.20,.2,.20]);box(0xffdd92,g,[0,3.3,0],[.42,.55,.42],true);mesh(coneGeo,0x526679,g,[0,3.7,0],[.42,.3,.42]);}
for(const x of [-15,-2,11,24])lamp(x,-5.3);
// Shelter is visibly dry, with a welcoming warm roof.
const shelter=new T.Group();shelter.position.set(9,0,0);world.add(shelter);for(const x of [-1.4,1.4])for(const z of [-1.2])cylinder(0x566b78,shelter,[x,1.5,z],[.07,3,.07]);box(0xe7b766,shelter,[0,3.03,0],[3.8,.28,3.4],true);box(0xe8dab8,shelter,[0,3.23,0],[3.5,.15,3.2]);box(0x78938e,shelter,[0,.1,0],[3.5,.2,3.0]);box(0x7c8f95,shelter,[0,.65,-.95],[2,.15,.5]);
// Batch the static toy town into two draw calls, preserving vertex colours and ink outlines.
world.updateMatrixWorld(true);
const batches={toon:[],ink:[]};
world.traverse(m=>{if(m.isMesh){const g=m.geometry.index?m.geometry.toNonIndexed():m.geometry.clone();g.applyMatrix4(m.matrixWorld);const pos=g.getAttribute('position'),norm=g.getAttribute('normal'),color=m.material.color;const colors=new Float32Array(pos.count*3);for(let i=0;i<pos.count;i++){const j=i*3,dot=norm.array[j]*.35+norm.array[j+1]*.85+norm.array[j+2]*.39;const light=m.material===outlineMat?1:dot>.35?1.1:dot>-.15?.76:.49;colors.set([color.r*light,color.g*light,color.b*light],j);}batches[m.material===outlineMat?'ink':'toon'].push({pos:pos.array,norm:norm.array,color:colors});}});
world.clear();for(const [kind,items] of Object.entries(batches)){const geo=new T.BufferGeometry();for(const key of ['pos','norm','color']){let n=0;for(const item of items)n+=item[key].length;const out=new Float32Array(n);let offset=0;for(const item of items){out.set(item[key],offset);offset+=item[key].length;}geo.setAttribute(key==='pos'?'position':key==='norm'?'normal':'color',new T.BufferAttribute(out,3));}const m=new T.Mesh(geo,kind==='ink'?new T.MeshBasicMaterial({vertexColors:true,side:T.BackSide}):new T.MeshBasicMaterial({vertexColors:true}));world.add(m);}

// Low, translucent contact shadows; no baked images or textures.
function shadow(parent,x,z,sx,sz){const m=new T.Mesh(new T.CircleGeometry(1,24),new T.MeshBasicMaterial({color:0x233b54,transparent:true,opacity:.20,depthWrite:false}));m.rotation.x=-Math.PI/2;m.position.set(x,.045,z);m.scale.set(sx,sz,1);parent.add(m);return m;}
function bone(parent,color,radius=.065){const m=cylinder(color,parent,[0,0,0],[radius,1,radius],true);return m;}
const UP=new T.Vector3(0,1,0);function connect(m,a,b,radius){const av=new T.Vector3(...a),bv=new T.Vector3(...b);m.position.copy(av).add(bv).multiplyScalar(.5);m.quaternion.setFromUnitVectors(UP,bv.clone().sub(av).normalize());m.scale.set(radius,av.distanceTo(bv),radius);}
function legKnee(hip,foot){const dy=foot[1]-hip[1],dz=foot[2]-hip[2],length=Math.hypot(dy,dz),d=Math.min(.855,length),half=d/2,h=Math.sqrt(Math.max(0,.43*.43-half*half));return[hip[0],(hip[1]+foot[1])/2+(-dz/(length||1))*h,(hip[2]+foot[2])/2+(dy/(length||1))*-h];}
function batchRig(g){
 g.updateMatrixWorld(true);const lists={body:[],ink:[]};g.traverse(m=>{if(m.isMesh){const geo=m.geometry.index?m.geometry.toNonIndexed():m.geometry;lists[m.material===outlineMat?'ink':'body'].push({m,p:geo.attributes.position.array,n:geo.attributes.normal.array,c:m.material.color});m.visible=false;}});
 const outputs=[];for(const [kind,list] of Object.entries(lists)){const count=list.reduce((n,s)=>n+s.p.length,0),p=new Float32Array(count),c=new Float32Array(count),geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(p,3).setUsage(T.DynamicDrawUsage));geo.setAttribute('color',new T.BufferAttribute(c,3).setUsage(T.DynamicDrawUsage));const m=new T.Mesh(geo,new T.MeshBasicMaterial({vertexColors:true,side:kind==='ink'?T.BackSide:T.FrontSide}));m.frustumCulled=false;scene.add(m);outputs.push({kind,list,p,c,geo,m});}
 return ()=>{g.updateMatrixWorld(true);for(const o of outputs){o.m.visible=g.visible;if(!g.visible)continue;let offset=0;for(const s of o.list){const e=s.m.matrixWorld.elements,nm=new T.Matrix3().getNormalMatrix(s.m.matrixWorld).elements;for(let j=0;j<s.p.length;j+=3){const x=s.p[j],y=s.p[j+1],z=s.p[j+2];o.p[offset+j]=e[0]*x+e[4]*y+e[8]*z+e[12];o.p[offset+j+1]=e[1]*x+e[5]*y+e[9]*z+e[13];o.p[offset+j+2]=e[2]*x+e[6]*y+e[10]*z+e[14];const a=s.n[j],b=s.n[j+1],c=s.n[j+2],nx=nm[0]*a+nm[3]*b+nm[6]*c,ny=nm[1]*a+nm[4]*b+nm[7]*c,nz=nm[2]*a+nm[5]*b+nm[8]*c,len=Math.hypot(nx,ny,nz)||1,dot=(nx*.35+ny*.85+nz*.39)/len,f=o.kind==='ink'?1:dot>.3?1.13:dot>-.2?.78:.50;o.c[offset+j]=s.c.r*f;o.c[offset+j+1]=s.c.g*f;o.c[offset+j+2]=s.c.b*f;}offset+=s.p.length;}o.geo.attributes.position.needsUpdate=true;o.geo.attributes.color.needsUpdate=true;}};
}
// R2 rig: waist/head pivots, reachable arm targets, expressions and distance-driven feet.
function armElbow(a,b,side){const A=new T.Vector3(...a),B=new T.Vector3(...b),v=B.clone().sub(A),d=Math.min(.654,v.length()),dir=v.normalize();const half=(.34*.34-.32*.32+d*d)/(2*Math.max(d,.001)),h=Math.sqrt(Math.max(0,.34*.34-half*half));let bend=new T.Vector3(side*.3,-1,-.25);bend.addScaledVector(dir,-bend.dot(dir)).normalize();return A.addScaledVector(dir,half).addScaledVector(bend,h).toArray();}
function person(color){const g=new T.Group();scene.add(g);const torso=new T.Group(),body=new T.Group();torso.position.y=1;body.position.y=-1;torso.add(body);g.add(torso);
 const coatMat=mat(color),baseColor=coatMat.color.clone();
 ball(color,body,[0,1.25,0],[.30,.43,.24],true);cylinder(color,body,[0,1.02,0],[.30,.23,.25],true);box(0xffeac0,body,[0,1.28,.237],[.018,.58,.025]);for(const x of [-.16,.16])box(0xe1ae52,body,[x,1.12,.22],[.13,.12,.035]);
 const head=new T.Group(),face=new T.Group();head.position.y=1.65;face.position.y=-1.65;head.add(face);body.add(head);
 ball(color,face,[0,1.91,-.035],[.38,.40,.34],true);ball(palette.skin,face,[0,1.9,.15],[.285,.30,.21]);
 for(let i=-1;i<=1;i++)ball(0x51423f,face,[i*.12,2.105,.24],[.105,.09,.085]);ball(palette.skin,face,[0,1.89,.36],[.055,.055,.055]);
 const eyes=[],brows=[];for(const x of [-.105,.105]){ball(0xfffbef,face,[x,1.96,.325],[.073,.087,.035]);eyes.push(ball(0x273a48,face,[x+.015,1.96,.354],[.032,.045,.018]));ball(0xffffff,face,[x+.023,1.979,.37],[.011,.015,.008]);brows.push(box(0x604139,face,[x,2.06,.338],[.10,.019,.021]));ball(0xe89e8c,face,[x*1.8,1.85,.30],[.055,.025,.012]);}
 const mouth=ball(0x774b42,face,[0,1.80,.334],[.064,.024,.012]);const teeth=box(0xfff4dd,face,[0,1.807,.347],[.074,.014,.008]);
 const limbs=[];for(const side of [-1,1]){const thigh=bone(g,0x36546f,.095),shin=bone(g,0x36546f,.082),knee=ball(0x36546f,g,[0,0,0],[.091,.091,.091]),shoe=ball(0xf4eee2,g,[0,0,0],[.12,.09,.22],true),sole=ball(0x34485a,g,[0,0,0],[.125,.035,.23]),upper=bone(g,color,.105),lower=bone(g,color,.085),elbow=ball(color,g,[0,0,0],[.10,.10,.10]),hand=ball(palette.skin,g,[0,0,0],[.09,.105,.08]);limbs.push({side,thigh,shin,knee,shoe,sole,upper,lower,elbow,hand});}
 const sh=shadow(scene,0,0,.50,.34),bake=batchRig(g),overlay=new T.Group();g.add(overlay);
 const volume=new T.Mesh(new T.BoxGeometry(.91,2.32,.83),new T.MeshBasicMaterial({color:0x8cdeef,transparent:true,opacity:.075,depthWrite:false}));volume.position.y=1.17;overlay.add(volume);
 const edges=new T.LineSegments(new T.EdgesGeometry(volume.geometry),new T.LineBasicMaterial({color:0xa6efff,transparent:true,opacity:.85}));edges.position.copy(volume.position);overlay.add(edges);
 const top=new T.Mesh(new T.PlaneGeometry(.93,.85),new T.MeshBasicMaterial({color:0x8cecff,transparent:true,opacity:.36,side:T.DoubleSide,depthWrite:false}));top.rotation.x=-Math.PI/2;top.position.y=2.34;overlay.add(top);
 const front=new T.Mesh(new T.PlaneGeometry(.93,2.32),new T.MeshBasicMaterial({color:0xffb579,transparent:true,opacity:.22,side:T.DoubleSide,depthWrite:false}));front.position.set(0,1.17,.43);overlay.add(front);
 const handWorld={};
 function pose(t,state){const speed=state.speed||0,moving=speed>.02,run=speed>1.15,cycle=(state.distance||0)/(run?1.22:.82),bounce=(moving?Math.sin(cycle*Math.PI*4)*.035:Math.sin(t*2)*.008)-(state.crouch||0)*.16;torso.position.y=1+bounce;torso.rotation.set(state.bend??(run?.13:0),0,state.tilt||0);head.rotation.set((state.headPitch||0)+Math.sin(t*1.6)*.018,(state.look||0)+Math.sin(t*.85)*.045,state.headRoll||0);torso.updateMatrix();body.updateMatrix();g.updateMatrixWorld(true);
  coatMat.color.copy(baseColor).multiplyScalar(1-(state.wet||0)*.24);
  mouth.scale.y=state.expression==='shock'?.060:state.expression==='laugh'?.045:.024;mouth.scale.x=state.expression==='shock'?.040:.064;teeth.scale.y=state.expression==='shock'?.0001:.014;
  brows.forEach((b,j)=>b.rotation.z=(state.expression==='annoyed'?(j?-.2:.2):state.expression==='shock'?(j?.18:-.18):0));
  for(const l of limbs){const p=((cycle+(l.side===1?.5:0))%1+1)%1,stance=run?.43:.60,amplitude=run?.54:.44;let z=0,y=.09;
   if(moving){if(p<stance)z=amplitude*(.5-p/stance);else{const u=(p-stance)/(1-stance);z=mix(-amplitude/2,amplitude/2,smooth(u));y+=Math.sin(u*Math.PI)*(run?.25:.12);}}
   if(state.air){z=l.side*.18;y+=.15+(l.side===1?.08:0);}
   const hip=[l.side*.145,.91+bounce,0],foot=[l.side*.15,y,z],k=legKnee(hip,foot);connect(l.thigh,hip,k,.095);connect(l.shin,k,foot,.082);l.knee.position.set(...k);l.shoe.position.set(foot[0],foot[1]-.005,foot[2]+.06);l.sole.position.set(foot[0],foot[1]-.055,foot[2]+.06);
   const shoulder=new T.Vector3(l.side*.29,1.49,0).applyMatrix4(body.matrix).applyMatrix4(torso.matrix).toArray(),swing=moving?Math.sin(cycle*Math.PI*2+(l.side===1?Math.PI:0))*(run?.38:.22):Math.sin(t*2+l.side)*.018;
   let hand=[shoulder[0]+l.side*.05,shoulder[1]-.58,shoulder[2]+swing];const custom=state.hands?.[l.side===-1?'left':'right'];if(custom){hand=[...custom];hand[1]+=.015*Math.sin(t*2.6+l.side);}
   const target=state.contact?.[l.side===-1?'left':'right'];if(target)hand=g.worldToLocal(new T.Vector3(...target)).toArray();
   const A=new T.Vector3(...shoulder),delta=new T.Vector3(...hand).sub(A);if(delta.length()>.65)hand=A.add(delta.setLength(.65)).toArray();const elbow=armElbow(shoulder,hand,l.side);connect(l.upper,shoulder,elbow,.105);connect(l.lower,elbow,hand,.085);l.elbow.position.set(...elbow);l.hand.position.set(...hand);handWorld[l.side===-1?'left':'right']=g.localToWorld(new T.Vector3(...hand)).toArray();
  }
  const blink=Math.pow(Math.max(0,Math.sin(t*1.8+(color===palette.teal?1:0))),42);for(const [j,e]of eyes.entries()){e.scale.y=.045*(1-blink*.92)*(state.expression==='laugh'?.65:1);e.position.x=(j?.105:-.105)+.015+(state.look||0)*.025;}
  overlay.visible=Boolean(state.overlay);top.visible=state.overlay!=='front';front.visible=state.overlay!=='top';
  sh.position.x=g.position.x;sh.position.z=g.position.z;sh.scale.set(.50*(1-g.position.y*.15),.34*(1-g.position.y*.15),1);sh.visible=g.visible;bake();
 }
 return{g,pose,handWorld,overlay,shadow:sh};}
const walker=person(palette.yellow),runner=person(palette.teal);

// Props are attached to posed hands rather than to fixed screen positions.
const umbrella=new T.Group();scene.add(umbrella);const canopy=new T.Group();canopy.position.y=1.1;umbrella.add(canopy);
const cap=mesh(new T.SphereGeometry(1,16,6,0,Math.PI*2,0,Math.PI/2),palette.orange,canopy,[0,0,0],[1.15,.48,1.15]);cap.material=new T.MeshBasicMaterial({color:palette.orange,side:T.DoubleSide});
cylinder(palette.ink,umbrella,[0,.55,0],[.025,1.15,.025]);ball(palette.ink,umbrella,[0,0,0],[.07,.09,.07]);
for(let j=0;j<8;j++){const a=j*Math.PI/4;const rib=bone(canopy,palette.cream,.012);connect(rib,[0,.45,0],[Math.cos(a)*1.12,0,Math.sin(a)*1.12],.012);}
const clipboard=new T.Group();scene.add(clipboard);box(palette.cream,clipboard,[0,0,0],[.43,.53,.035],true);box(palette.ink,clipboard,[0,.25,.03],[.16,.04,.04]);for(let j=0;j<4;j++)box(0x839cae,clipboard,[-.02,.12-j*.075,.025],[.25,.012,.006]);
const pencil=box(palette.orange,scene,[0,0,0],[.025,.20,.025]);pencil.rotation.z=-.6;
const towel=box(palette.cream,scene,[0,0,0],[.25,.38,.045]);
const buckets=new T.Group();scene.add(buckets);for(let j=0;j<2;j++){const x=(j-.5)*1.3;const g=new T.Group();g.position.set(x,0,0);buckets.add(g);const m=cylinder(j?palette.teal:palette.yellow,g,[0,.25,0],[.30,.5,.30],true);const water=cylinder(0x91d7e8,g,[0,j?.29:.43,0],[.265,.025,.265]);const handle=mesh(new T.TorusGeometry(.26,.018,5,16,Math.PI),palette.ink,g,[0,.54,0],[1,1,1]);}
const clockProp=new T.Group();scene.add(clockProp);const dial=cylinder(palette.cream,clockProp,[0,0,0],[.32,.045,.32],true);dial.rotation.x=Math.PI/2;const needle=box(palette.ink,clockProp,[0,.10,.04],[.018,.2,.02]);for(let j=0;j<12;j++){const a=j*Math.PI/6;box(palette.ink,clockProp,[Math.sin(a)*.25,Math.cos(a)*.25,.04],[.025,.025,.01]);}
const ruler=new T.Group();scene.add(ruler);box(palette.cream,ruler,[0,.075,0],[6,.05,.16]);for(let j=0;j<=12;j++)box(palette.ink,ruler,[-3+j*.5,.11,0],[.025,.018,j%2?.08:.15]);
const track=new T.Group();scene.add(track);for(const x of [-3,3])box(palette.cream,track,[x,.065,.2],[.12,.018,3.1]);
const puddle=mesh(new T.CircleGeometry(1,32),0x84b8ca,scene,[.5,.055,.8],[1.05,.56,1]);puddle.rotation.x=-Math.PI/2;
// Narrow rain streaks and round spray droplets, never falling blocks.
const rainCount=650,rainPositions=new Float32Array(rainCount*6),rainBase=Array.from({length:rainCount},()=>[-18+random()*40,random()*13,-7+random()*16]);const rainGeo=new T.BufferGeometry();rainGeo.setAttribute('position',new T.BufferAttribute(rainPositions,3));const rain=new T.LineSegments(rainGeo,new T.LineBasicMaterial({color:0xcbeaf5,transparent:true,opacity:.36}));scene.add(rain);
const sprayCount=56,spray=new T.InstancedMesh(ballGeo,new T.MeshBasicMaterial({color:0xbce8ee,transparent:true,opacity:.78}),sprayCount);scene.add(spray);const dummy=new T.Object3D();const droplets=Array.from({length:sprayCount},()=>({a:random()*Math.PI*2,v:.4+random()*1.8,up:.6+random()*2,offset:random()*.18}));
const rings=new T.InstancedMesh(new T.RingGeometry(.8,1,12),new T.MeshBasicMaterial({color:0xb8dce3,transparent:true,opacity:.22,side:T.DoubleSide}),32);scene.add(rings);const ringBase=Array.from({length:32},()=>[-8+random()*20,-2+random()*6]);
const demoDrops=new T.InstancedMesh(ballGeo,new T.MeshBasicMaterial({color:0xa9ebf8}),24);scene.add(demoDrops);
const heroDrop=ball(0xc4eff9,scene,[0,0,0],[.045,.09,.045]);
function put(prop,pos){prop.position.set(...pos);}
function draw(t){t=clamp(t,0,479.999);const st=stage(t,timings),{A,B,q}=st;
 for(const [rig,a]of[[walker,A],[runner,B]]){rig.g.position.set(a.x,a.y,a.z);rig.g.rotation.set(0,a.yaw,0);rig.pose(t,a);}
 const midX=(A.x+B.x)/2,midZ=(A.z+B.z)/2;heroDrop.visible=st.action==='drops'&&q<.65;if(heroDrop.visible){const h=walker.handWorld.right;heroDrop.position.set(h[0],h[1]+Math.max(0,2.8-q*5),h[2]);}
 umbrella.visible=!!st.props.umbrella;if(umbrella.visible){const u=st.props.umbrella;if(u.flying)put(umbrella,[u.x,u.y,u.z]);else put(umbrella,(u.holder==='A'?walker:runner).handWorld.right);umbrella.rotation.set(u.flip*.1,0,-u.flip*.25+.03*Math.sin(t*3));canopy.scale.set(.12+.88*u.open,u.flip?-.6:1,.12+.88*u.open);}
 clipboard.visible=!!st.props.clipboard;pencil.visible=clipboard.visible;if(clipboard.visible){const rig=st.props.clipboard==='A'?walker:runner;put(clipboard,rig.handWorld.left);clipboard.rotation.set(-.5,.15,-.1);put(pencil,rig.handWorld.right);pencil.rotation.z=-.6+Math.sin(t*12)*.08;}
 towel.visible=!!st.props.towel;if(towel.visible){const rig=st.action==='dry_friend'?walker:runner;put(towel,rig.handWorld.right);towel.rotation.z=Math.sin(t*5)*.2;}
 buckets.visible=!!st.props.buckets;buckets.position.set(midX,.03,midZ+1.2);
 ruler.visible=!!st.props.ruler;ruler.position.set(midX,0,midZ+1.6);track.visible=!!st.props.track;
 clockProp.visible=!!st.props.clock;clockProp.position.set(midX+1.3,1.3,midZ+.5);needle.rotation.z=-st.local*1.5;
 puddle.visible=!!st.props.puddle;
 let radius=8.1,cy=4.0,ly=1.25,angle=[-.28,.35,-.45,.48,-.16,.3,-.35,.18][st.index]+(q-.5)*.14,fx=midX,fz=midZ;
 if(st.camera==='faces'){radius=5.4;cy=2.7;ly=1.65;}
 if(st.camera.includes('hands')){radius=5.6;cy=3.0;ly=1.2;}
 if(st.camera==='feet'){radius=6.8;cy=1.55;ly=.6;}
 if(st.camera==='splash'){radius=6.5;cy=2.6;ly=1.0;angle=.35;}
 if(st.camera==='profile'){radius=9;cy=3.1;angle=-.8+(q*.12);}
 if(st.camera==='orbit'){angle=-.65+q*1.1;radius=8.3;}
 if(st.camera==='overhead'){radius=6.5;cy=9;ly=.3;}
 if(st.camera==='shelter_wide'){fx=4;radius=17;cy=6;ly=1.2;angle=-.3;}
 if(st.camera==='umbrella'){radius=9.0;cy=4.0;ly=1.7;}
 if(st.camera==='follow')radius=Math.max(8.8,Math.abs(A.x-B.x)*1.6+5);
 if(st.camera.startsWith('shelter_')&&st.camera!=='shelter_wide'){angle=-.45;radius=st.camera==='shelter_hands'?6.3:8.5;cy=3.2;}
 radius*=1-.04*q;camera.position.set(fx+Math.sin(angle)*radius,cy,fz+Math.cos(angle)*radius);camera.lookAt(fx,ly,fz);
 const rainTime=st.props.slow?t*.20:t;for(let j=0;j<rainCount;j++){const b=rainBase[j],y=13-((rainTime*6.5+b[1])%13),x=((b[0]+st.wind*t+180)%40)-18,z=b[2],k=j*6;const dry=x>7.1&&x<10.9&&z>-1.7&&z<1.7&&y<3.35;rainPositions.set([x,dry?-9:y,z,x-st.wind*.035,(dry?-9:y)+.24,z],k);}rainGeo.attributes.position.needsUpdate=true;
 spray.visible=!!st.burst;if(st.burst){const b=st.burst,age=((q-b.start)*st.length)%1.2;for(let j=0;j<sprayCount;j++){const d=droplets[j],a=age-d.offset,visible=a>=0&&a<1.2;dummy.position.set(b.x+Math.cos(d.a)*d.v*a*b.strength,b.y+d.up*a*1.7-2*a*a,b.z+Math.sin(d.a)*d.v*a*b.strength);dummy.scale.setScalar(visible&&dummy.position.y>.05?.025+.008*(j%3):0);dummy.updateMatrix();spray.setMatrixAt(j,dummy.matrix);}spray.instanceMatrix.needsUpdate=true;}
 for(let j=0;j<32;j++){const a=(t*1.2+j*.131)%1;dummy.position.set(ringBase[j][0],.06,ringBase[j][1]);dummy.rotation.set(-Math.PI/2,0,0);dummy.scale.setScalar(.05+a*.25);dummy.updateMatrix();rings.setMatrixAt(j,dummy.matrix);}rings.instanceMatrix.needsUpdate=true;
 demoDrops.visible=Boolean(A.overlay||B.overlay);if(demoDrops.visible){for(let j=0;j<24;j++){const actor=j<12?A:B,rig=j<12?walker:runner,front=actor.overlay==='front'||actor.overlay==='both'&&j%2===0,phase=(t*(st.props.slow?.3:.8)+j*.137)%1;const v=new T.Vector3((j%3-1)*.23,front?.65+(j%5)*.29:3.55-phase*1.1,front?1.8-phase*1.2:(j%4-1.5)*.16);rig.g.localToWorld(v);dummy.position.copy(v);dummy.rotation.set(0,0,0);dummy.scale.set(.025,front?.035:.065,.025);dummy.updateMatrix();demoDrops.setMatrixAt(j,dummy.matrix);}demoDrops.instanceMatrix.needsUpdate=true;}
 renderer.render(scene,camera);ctx.drawImage(renderer.domElement,0,0,1920,1080);ctx.save();ctx.scale(SCALE,SCALE);
 const grad=ctx.createLinearGradient(0,0,0,H);grad.addColorStop(0,'#10263abd');grad.addColorStop(.24,'#10263a00');grad.addColorStop(.78,'#10263a00');grad.addColorStop(1,'#10263abb');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
 text('CIÊNCIA NO CAMINHO',40,36,14,'#d9e9ed');text(chapters[st.chapter].name.toUpperCase(),1240,36,14,'#f5d694','right');text(st.title,40,79,27,'#fff5df');
 const cards={top:'POR CIMA · menos tempo, menos água',front:'PELA FRENTE · distância também conta',sum:'POR CIMA + PELA FRENTE',body:'Uma silhueta para visualizar as áreas',wind:st.wind>0?'VENTO POR TRÁS':'VENTO DE FRENTE',test:'Mesmas condições · repetir e comparar'};
 if(st.diagram){const label=cards[st.diagram]||cards.body;ctx.font='600 16px "DejaVu Sans",sans-serif';const w=ctx.measureText(label).width+32;ctx.fillStyle='#20364be6';ctx.fillRect(1240-w,101,w,35);text(label,1224,125,16,'#e2f4ec','right');}
 ctx.fillStyle='#142d43dd';ctx.fillRect(40,638,1200,43);text(st.title,640,667,22,'#f4f4ed','center');ctx.fillStyle='#ffcf6a';ctx.fillRect(40,701,1200*t/480,3);ctx.restore();
 const left=walker.handWorld.left,right=runner.handWorld.left;return {chapter:st.chapter+1,action:st.action,time:t,camera:st.camera,contact:st.contact,handDistance:Math.hypot(...left.map((v,i)=>v-right[i])),overlays:[walker.overlay.visible,runner.overlay.visible],speeds:[A.speed,B.speed],drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles};
}
function text(s,x,y,size,color,align='left'){ctx.font=`600 ${size}px "DejaVu Sans",sans-serif`;ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(s,x,y);}
window.film={draw,duration:480,timings,chapters,renderer,scene,metrics:{procedural:true,externalImages:0,importedModels:0,fps:24,width:1920,height:1080}};
const audio=document.querySelector('#audio'),seek=document.querySelector('#seek'),play=document.querySelector('#play');let playing=false,time=0;
function clock(t){return `${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;}
function update(){if(playing){time=audio.currentTime;draw(time);seek.value=time;document.querySelector('#time').textContent=clock(time)+' / 8:00';requestAnimationFrame(update);}}
play.onclick=async()=>{if(playing){audio.pause();playing=false;play.textContent='Reproduzir';}else{await audio.play();playing=true;play.textContent='Pausar';update();}};
seek.oninput=()=>{time=+seek.value;audio.currentTime=time;draw(time);document.querySelector('#time').textContent=clock(time)+' / 8:00';};audio.onended=()=>{playing=false;play.textContent='Reproduzir';};draw(0);
