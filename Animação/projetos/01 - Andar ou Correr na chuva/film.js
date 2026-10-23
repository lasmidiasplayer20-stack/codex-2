/* Procedural geometry, materials, character rig, weather, diagrams and editing.
   No external images, video textures or imported character models. */
const T=window.THREE;
const timings=await (await fetch('timing.json')).json();
const W=1280,H=720,canvas=document.querySelector('#output'),ctx=canvas.getContext('2d',{alpha:false});
const renderer=new T.WebGLRenderer({antialias:false,alpha:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputEncoding=T.sRGBEncoding;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
const scene=new T.Scene();scene.background=new T.Color('#839cae');scene.fog=new T.Fog('#839cae',25,75);
const camera=new T.PerspectiveCamera(35,W/H,.1,130);
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
for(const x of [-15,-2,11,24])lamp(x,5.3);
// Shelter is visibly dry, with a welcoming warm roof.
const shelter=new T.Group();shelter.position.set(9,0,0);world.add(shelter);for(const x of [-1.4,1.4])for(const z of [-1.2,1.2])cylinder(0x566b78,shelter,[x,1.5,z],[.07,3,.07]);box(0xe7b766,shelter,[0,3.03,0],[3.8,.28,3.4],true);box(0xe8dab8,shelter,[0,3.23,0],[3.5,.15,3.2]);box(0x78938e,shelter,[0,.1,0],[3.5,.2,3.0]);box(0x7c8f95,shelter,[0,.65,-.95],[2,.15,.5]);
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
function person(color){const g=new T.Group();scene.add(g);const torso=new T.Group();g.add(torso);
 const coat=ball(color,torso,[0,1.25,0],[.30,.43,.24],true);cylinder(color,torso,[0,1.02,0],[.30,.23,.25],true);box(0xffeac0,torso,[0,1.28,.237],[.018,.58,.025]);for(const x of [-.16,.16])box(0xe1ae52,torso,[x,1.12,.22],[.13,.12,.035]);
 ball(color,torso,[0,1.91,-.035],[.38,.40,.34],true);ball(palette.skin,torso,[0,1.9,.15],[.285,.30,.21]);
 // Hair fringe, nose and eyebrows make expressions legible in close shots.
 for(let i=-1;i<=1;i++)ball(0x51423f,torso,[i*.12,2.105,.24],[.105,.09,.085]);
 ball(palette.skin,torso,[0,1.89,.36],[.055,.055,.055]);
 const eyes=[];for(const x of [-.105,.105]){ball(0xfffbef,torso,[x,1.96,.325],[.073,.087,.035]);eyes.push(ball(0x273a48,torso,[x+.015,1.96,.354],[.032,.045,.018]));ball(0xffffff,torso,[x+.023,1.979,.37],[.011,.015,.008]);box(0x604139,torso,[x,2.06,.338],[.10,.019,.021]);}
 const mouth=ball(0x774b42,torso,[0,1.80,.334],[.064,.024,.012]);
 const limbs=[];for(const side of [-1,1]){const thigh=bone(g,0x36546f,.095),shin=bone(g,0x36546f,.082);const knee=ball(0x36546f,g,[0,0,0],[.091,.091,.091]);const shoe=ball(0xf4eee2,g,[0,0,0],[.12,.09,.22],true);const sole=ball(0x34485a,g,[0,0,0],[.125,.035,.23]);const upper=bone(g,color,.105),lower=bone(g,color,.085),elbow=ball(color,g,[0,0,0],[.10,.10,.10]),hand=ball(palette.skin,g,[0,0,0],[.09,.105,.08]);limbs.push({side,thigh,shin,knee,shoe,sole,upper,lower,elbow,hand});}
 const sh=shadow(scene,0,0,.50,.34);const bake=batchRig(g);
 function pose(t,speed,phase=0,gesture=0){const moving=speed>.01,cycle=t*(speed>1.0?2.2:1.25)+phase;const bounce=moving?Math.sin(cycle*Math.PI*4)*.025:Math.sin(t*2)*.008;torso.position.y=bounce;torso.rotation.x=moving&&speed>1.0?.08:0;
 for(const l of limbs){const p=((cycle+(l.side===1?.5:0))%1+1)%1;const stance=speed>1.0?.43:.60,amplitude=speed*stance/(speed>1.0?2.2:1.25);let z,y=.09;if(moving){if(p<stance)z=amplitude*(.5-p/stance);else{const u=(p-stance)/(1-stance);z=mix(-amplitude/2,amplitude/2,smooth(u));y+=Math.sin(u*Math.PI)*(speed>1.0?.22:.14);}}else z=l.side*.025;
  const hip=[l.side*.145,.91+bounce,0],foot=[l.side*.15,y,z],k=legKnee(hip,foot);connect(l.thigh,hip,k,.095);connect(l.shin,k,foot,.082);l.knee.position.set(...k);l.shoe.position.set(foot[0],foot[1]-.005,foot[2]+.06);l.sole.position.set(foot[0],foot[1]-.055,foot[2]+.06);
  const shoulder=[l.side*.29,1.49+bounce,0],swing=moving?Math.sin(cycle*Math.PI*2+(l.side===1?Math.PI:0))*(speed>1.0?.40:.24):Math.sin(t*1.3)*.02;
  const elbow=[l.side*.34,1.16+bounce,swing*.5],hand=[l.side*.35,.91+bounce,swing];
  if(gesture&&l.side===-1){elbow[1]=1.40;elbow[2]=.30;hand[1]=1.72+Math.sin(t*2)*.04;hand[2]=.45;}
  connect(l.upper,shoulder,elbow,.105);connect(l.lower,elbow,hand,.085);l.elbow.position.set(...elbow);l.hand.position.set(...hand);
 }
 const blink=Math.pow(Math.max(0,Math.sin(t*1.8)),42);for(const e of eyes)e.scale.y=.045*(1-blink*.92);
 sh.position.x=g.position.x;sh.position.z=g.position.z;sh.visible=g.visible;bake();
 }
 return {g,pose,torso,mouth,shadow:sh};}
const walker=person(palette.yellow),runner=person(palette.teal);
// Rain is a single instanced geometry, not thousands of independent draw calls.
const rainCount=850,rainGeo=new T.BufferGeometry(),positions=new Float32Array(rainCount*6),base=[];
for(let i=0;i<rainCount;i++)base.push([random()*46-23,random()*12,random()*24-10]);
rainGeo.setAttribute('position',new T.BufferAttribute(positions,3));const rain=new T.LineSegments(rainGeo,new T.LineBasicMaterial({color:0xc6e8f2,transparent:true,opacity:.46}));scene.add(rain);
const splashGeo=new T.RingGeometry(.8,1,18),splashMat=new T.MeshBasicMaterial({color:0xb9e7e4,transparent:true,opacity:.4,side:T.DoubleSide,depthWrite:false});const splashes=[];
const splashBatch=new T.InstancedMesh(splashGeo,splashMat,32);scene.add(splashBatch);const splashDummy=new T.Object3D();for(let i=0;i<32;i++)splashes.push([random()*28-14,random()*7-2]);
// Dedicated diagram set, also built in 3D.
const lab=new T.Group();scene.add(lab);lab.position.set(0,0,55);
box(0x8ca9b1,lab,[0,-.2,0],[28,.35,15]);const block=box(0xffcf6a,lab,[0,1.2,0],[1.25,2.4,.85],true);const arrowGroup=new T.Group();lab.add(arrowGroup);
function arrow(parent,x,y,z,dir,color,length=1.2){const direction=new T.Vector3(...dir).normalize();const a=new T.ArrowHelper(direction,new T.Vector3(x,y,z),length,color,.22,.12);parent.add(a);return a;}
for(let i=0;i<7;i++)arrow(arrowGroup,-3+i,4.2,(i%2)*.9-.4,[0,-1,0],0xd6f5fa,1.25);
const frontArrows=new T.Group();lab.add(frontArrows);for(let i=0;i<4;i++)arrow(frontArrows,3,1+i*.45,.2,[-1,0,0],0xffb377,1.5);
const sweepMaterial=new T.MeshBasicMaterial({color:0x68c3ce,transparent:true,opacity:.13,side:T.DoubleSide,depthWrite:false});const swept=new T.Mesh(new T.BoxGeometry(5.0,2.4,.89),sweepMaterial);swept.position.set(-1.8,1.2,0);lab.add(swept);
const topPatch=box(0xffe9ad,lab,[0,2.415,0],[1.28,.025,.88]);const frontPatch=box(0xff9e73,lab,[.64,1.2,0],[.025,2.4,.89]);
const visualTitles=['O abrigo está logo ali.','Vamos controlar a experiência.','Menos tempo, menos água por cima.','Mais gotas por segundo. Menos segundos.','As duas partes da conta.','E quando o vento muda?','O mundo real também respinga.','Como testar sem se enganar.','A resposta cabe no caminho.'];
const chapterNames=['A dúvida','O modelo','Água por cima','Água pela frente','A resposta','Com vento','Na vida real','O experimento','Até o abrigo'];
const subtitles=[['Andar ou correr na chuva?','O mesmo destino. Duas velocidades.','O que importa é a viagem inteira.'],['Sem vento · chuva constante','Mesmo corpo · mesmo caminho','Um modelo simples para começar.'],['A água de cima depende do tempo.','100 metros até o abrigo.','Dobrar a velocidade reduz o tempo pela metade.'],['Você encontra mais gotas a cada segundo.','Mas a viagem também termina antes.','No modelo, a parcela frontal depende da distância.'],['Água de cima: diminui ao correr.','Água frontal: aproximadamente igual.','Correr ajuda. Isso não significa ficar seco.'],['Vento de frente muda a comparação.','Vento por trás muda a velocidade relativa.','Não existe uma resposta universal para qualquer vento.'],['Pés, braços e postura também mudam.','Uma poça pode mudar o resultado.','Água recebida não é igual à água retida.'],['Controle chuva, distância, roupa e percurso.','Defina o que está sendo medido.','A simulação depende das regras programadas.'],['Em chuva quase vertical, chegar antes ajuda.','Olhe também para o chão.','Menos tempo exposto costuma significar menos água.']];
function chapterAt(t){let i=timings.findIndex(x=>t>=x.start&&t<x.end);if(i<0)i=8;return {i,local:t-timings[i].start,duration:timings[i].end-timings[i].start};}
// All typography and overlays are drawn as vector text and paths at render time.
function rr(x,y,w,h,r,fill){ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fillStyle=fill;ctx.fill();}
function text(s,x,y,size=26,color='#fff',weight=600,align='left'){ctx.font=`${weight} ${size}px "DejaVu Sans",sans-serif`;ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(s,x,y);}
function label(s,x,y,color='#ffcf6a'){const width=ctx.measureText(s).width+34;rr(x,y,width,35,12,'#1a3045df');text(s,x+17,y+24,18,color,700);}
function tag(s,worldPoint,color='#ffcf6a'){const v=new T.Vector3(...worldPoint).project(camera);const x=(v.x*.5+.5)*W,y=(-v.y*.5+.5)*H;ctx.font='700 18px "DejaVu Sans"';const w=ctx.measureText(s).width+30;rr(x-w/2,y-29,w,34,10,'#20364be8');text(s,x,y-6,18,color,700,'center');}
function panel(x,y,w,h,title){rr(x,y,w,h,22,'#173149eb');text(title,x+24,y+35,20,'#f7d28a',700);}
function meter(x,y,w,f,color){rr(x,y,w,14,7,'#ffffff20');rr(x,y,Math.max(1,w*clamp(f)),14,7,color);}
function diagram(i,local,duration){const f=clamp(local/duration);const x=826,y=180;panel(x,y,398,330,i===5?'CHUVA + VENTO':'UM TRAJETO DE 100 METROS');
 if(i===2){text('ANDANDO',x+24,y+85,18,'#ffcf6a');text('CORRENDO',x+24,y+165,18,'#79d5c8');const progress=clamp((local%14)/10);meter(x+24,y+105,340,progress*.45,'#ffcf6a');meter(x+24,y+185,340,progress,'#79d5c8');text('Tempo de exposição',x+24,y+240,19,'#e0eaf0');text('↓ ao aumentar a velocidade',x+24,y+278,22,'#fff');}
 else if(i===3){text('POR SEGUNDO',x+24,y+85,18,'#b9d7e5');text('Mais encontros ao correr',x+24,y+119,23);text('DURANTE A VIAGEM',x+24,y+180,18,'#b9d7e5');text('Menos segundos exposto',x+24,y+214,23);text('Mesmo trajeto → mesma parcela frontal*',x+24,y+282,16,'#ffcf6a');}
 else if(i===4){text('Água total recebida',x+24,y+90,26);text('POR CIMA',x+24,y+148,19,'#ffcf6a');meter(x+24,y+165,340,.65-.4*smooth(f),'#ffcf6a');text('PELA FRENTE',x+24,y+220,19,'#79d5c8');meter(x+24,y+237,340,.40,'#79d5c8');text('*Chuva vertical e postura semelhante',x+24,y+290,16,'#c2d5e0');}
 else if(i===5){const mode=Math.floor(local/12)%3;const words=['SEM VENTO','VENTO DE FRENTE','VENTO POR TRÁS'];text(words[mode],x+24,y+95,24);text(['↓','↙','↘'][mode],x+197,y+207,76,'#a9e2ed',700,'center');text('Direção e velocidade importam.',x+24,y+277,20,'#f6d493');}
 else if(i===7){['Mesma distância','Mesma chuva e vento','Mesma roupa inicial','Repetir a comparação'].forEach((s,j)=>{text('✓',x+24,y+90+j*53,24,'#79d5c8');text(s,x+64,y+90+j*53,21);});}
}
function draw(t){t=clamp(t,0,479.999);const {i,local,duration}=chapterAt(t),fraction=clamp(local/duration);world.visible=true;lab.visible=false;walker.g.visible=true;runner.g.visible=true;walker.g.rotation.set(0,Math.PI/2,0);runner.g.rotation.set(0,Math.PI/2,0);let speedW=.7,speedR=1.6;
 let loop=(local%19)/19;walker.g.position.set(-7+loop*13,0,2.8);runner.g.position.set(-7+clamp(loop*1.85)*15,0,.1);
 let cx=2+Math.sin(local*.08)*.55,cy=7.5,cz=17,look=[1,1.2,0];
 if(i===0){const p=clamp(local/15);walker.g.position.x=-5+p*6;runner.g.position.x=-5+clamp(local/8)*13;cx=1;cy=6.4;cz=16;look=[0,1,0];if(local>20){cx=-2+Math.sin(local*.12)*.3;cy=3.8;cz=10;look=[-2,1.2,1];walker.g.position.x=-3;runner.g.position.x=4;speedW=0;speedR=0;}}
 if([1,3,4].includes(i)){lab.visible=true;world.visible=false;walker.g.visible=false;runner.g.visible=false;cx=6.5+Math.sin(local*.08)*.5;cy=5.7;cz=65;look=[0,1.5,55];block.position.x=-.6+Math.sin(local*.35)*.4;frontArrows.visible=i!==1;arrowGroup.visible=i!==3;topPatch.visible=i!==3;frontPatch.visible=i!==1;lab.rotation.y=Math.sin(local*.1)*.08;}
 if(i===2){cx=0;cy=9;cz=18;look=[0,1,0];}
 if(i===5){const mode=Math.floor(local/12)%3;cx=1;cy=6.8;cz=17;look=[0,1.2,0];walker.g.position.x=-4;runner.g.position.x=2;speedW=.7;speedR=1.6;}
 if(i===6){const shot=Math.floor(local/10)%4;if(shot===0){cx=-3;cy=2;cz=7;look=[-3,1,1];walker.g.position.x=-4;runner.g.position.x=-1;}else if(shot===1){cx=0;cy=1.5;cz=6;look=[0,.4,1];walker.g.position.x=-1;runner.g.position.x=2;}else{cx=-1;cy=4;cz=10;look=[-1,1.2,1];walker.g.position.x=-3;runner.g.position.x=1;speedW=0;speedR=0;}}
 if(i===7){cx=1;cy=7;cz=16;look=[0,1,0];walker.g.position.x=-5+loop*12;runner.g.position.x=-5+clamp(loop*1.8)*14;}
 if(i===8){const travel=clamp(local/24);walker.g.position.x=-6+travel*14;runner.g.position.x=-6+clamp(local/13)*15;speedW=travel>=1?0:.7;speedR=local>=13?0:1.6;cx=4;cy=6;cz=16;look=[4,1.2,0];if(local>28){cx=12.3;cy=4;cz=9.4;look=[8.1,1.5,0];walker.g.position.x=8.2;runner.g.position.x=9.8;walker.g.rotation.y=-.25;runner.g.rotation.y=-.4;}}
 arrowGroup.position.y=-((local*.9)%1.0);frontArrows.position.x=-((local*.9)%1.0);swept.visible=i===3||i===4;swept.scale.x=.4+.6*(local%8)/8;
 if([1,3,4].includes(i)&&Math.floor(local/6)%3===0){lab.visible=false;world.visible=true;walker.g.visible=true;runner.g.visible=true;walker.g.position.set(-4,0,2.8);runner.g.position.set(2,0,.1);speedW=i===1?0:.7;speedR=i===1?0:1.6;}
 walker.pose(t,speedW,0,speedW===0);runner.pose(t,speedR,.3,speedR===0);walker.shadow.visible=walker.g.visible;runner.shadow.visible=runner.g.visible;
 // Editorial cuts every six seconds. Within shots: dolly, orbit, low angle and overhead views.
 const shot=Math.floor(local/6)%7,q=(local%6)/6;
 if(lab.visible){const angles=[.40,-.55,.85,-.25,.20,1.10,-.75];const a=angles[shot]+(q-.5)*.12;const radius=shot===2?9:shot===4?11:12;cx=Math.sin(a)*radius-1.6;cz=55+Math.cos(a)*radius;cy=shot===3?9:shot===5?3.7:5.6+q*.3;look=[1.0,1.65,55];}
 else if(!(i===8&&local>30)){
  const mid=(walker.g.position.x+runner.g.position.x)*.5;
  const overlay=[2,5,7].includes(i);
  const focus=overlay?mid+2.5:mid;
  const angles=[.18,.62,-.36,.90,.10,-.65,.38];let a=angles[shot]+(q-.5)*.09;
  let radius=overlay?18:shot===1?12:shot===2?14:17;
  cy=shot===4?13:shot===5?3.1:shot===1?4.0:6.4;
  if(overlay)cy=Math.max(cy,5.5);
  cx=focus+Math.sin(a)*radius;cz=1.1+Math.cos(a)*radius;
  look=[focus,shot===4?.4:1.0,1.0];
  if(i===6&&shot===2){cx=walker.g.position.x+3;cy=1.1;cz=6;look=[walker.g.position.x,.40,2.5];}
 }
 camera.position.set(cx,cy,cz);camera.lookAt(...look);
 // The diagram receives its own rain arrows; street rain is disabled there.
 rain.visible=world.visible;const mode=i===5?Math.floor(local/12)%3:0,wind=mode===1?-2.8:mode===2?2.8:0;
 if(rain.visible){for(let j=0;j<rainCount;j++){const b=base[j];const y=12-((t*7+b[1])%12),x=((b[0]+wind*t+46)%46)-23,z=b[2];const k=j*6;let sheltered=x>7.1&&x<10.9&&z>-1.7&&z<1.7&&y<3.3;positions[k]=x;positions[k+1]=sheltered?-8:y;positions[k+2]=z;positions[k+3]=x-wind*.04;positions[k+4]=(sheltered?-8:y)+.33;positions[k+5]=z;}rainGeo.attributes.position.needsUpdate=true;}
 splashBatch.visible=world.visible;splashes.forEach((p,j)=>{const a=(t*1.2+j*.131)%1;splashDummy.position.set(p[0],.055,p[1]);splashDummy.rotation.x=-Math.PI/2;splashDummy.scale.setScalar(.10+a*.25);splashDummy.updateMatrix();splashBatch.setMatrixAt(j,splashDummy.matrix);});splashBatch.instanceMatrix.needsUpdate=true;
 renderer.render(scene,camera);ctx.drawImage(renderer.domElement,0,0,W,H);
 // Soft vignette and crisp editorial typography, both procedural.
 const grad=ctx.createLinearGradient(0,0,0,H);grad.addColorStop(0,'#10263ac0');grad.addColorStop(.24,'#10263a00');grad.addColorStop(.72,'#10263a00');grad.addColorStop(1,'#10263abd');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
 text('CIÊNCIA NO CAMINHO',56,49,16,'#d9e9ed',700);text(`${String(i+1).padStart(2,'0')} / 09`,1224,49,17,'#f5d694',700,'right');
 text(visualTitles[i],56,100,32,'#fff5df',700);
 if([2,3,4,5,7].includes(i))diagram(i,local,duration);
 if(world.visible&&![6,8].includes(i)){tag('ANDANDO',[walker.g.position.x,2.7,walker.g.position.z],'#ffcf6a');tag('CORRENDO',[runner.g.position.x,2.7,runner.g.position.z],'#83e0cd');}
 if(i===1&&lab.visible){tag('SUPERFÍCIE DE CIMA',[0,3.3,55],'#ffcf6a');text('Corpo simplificado · sem vento · chuva uniforme',640,547,23,'#fff4dc',600,'center');}
 if(i===3)text('Mais por segundo × menos segundos',376,541,24,'#ffdfad',700,'center');
 if(i===6&&Math.floor(local/10)%4===1){label('RESPINGOS TAMBÉM CONTAM',68,166);}
 if(i===8&&local>30){rr(300,430,680,112,24,'#18374be8');text('Chegar antes costuma ajudar.',640,477,30,'#ffdb8e',700,'center');text('Com segurança, e considerando o vento e o chão.',640,514,21,'#e9f1f1',500,'center');}
 const sub=subtitles[i][Math.min(2,Math.floor(fraction*3))];rr(56,593,1168,57,17,'#142d43e8');text(sub,640,630,25,'#f4f4ed',600,'center');
 rr(56,675,1168,4,2,'#d3e7ec35');rr(56,675,Math.max(1,1168*t/480),4,2,'#ffcf6a');text('01 · ANDAR OU CORRER NA CHUVA',56,705,13,'#d3e3e7',600);text(chapterNames[i],1224,705,14,'#d3e3e7',600,'right');
 return {chapter:i+1,time:t,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles};
}
window.film={draw,duration:480,timings,renderer,scene,metrics:{procedural:true,externalImages:0,importedModels:0,fps:24,width:W,height:H}};
const audio=document.querySelector('#audio'),seek=document.querySelector('#seek'),play=document.querySelector('#play');let playing=false,time=0;
function clock(t){return `${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;}
function update(){if(playing){time=audio.currentTime;draw(time);seek.value=time;document.querySelector('#time').textContent=clock(time)+' / 8:00';requestAnimationFrame(update);}}
play.onclick=async()=>{if(playing){audio.pause();playing=false;play.textContent='Reproduzir';}else{await audio.play();playing=true;play.textContent='Pausar';update();}};
seek.oninput=()=>{time=+seek.value;audio.currentTime=time;draw(time);document.querySelector('#time').textContent=clock(time)+' / 8:00';};audio.onended=()=>{playing=false;play.textContent='Reproduzir';};
draw(0);
