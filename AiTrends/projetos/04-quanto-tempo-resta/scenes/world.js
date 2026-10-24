import {actor,library} from './rig.js';
const cache=new Map();
export function world(T,location){
 if(cache.has(location))return cache.get(location);
 const L=library(T),H=T.THREE,scene=new H.Scene(),camera=new H.PerspectiveCamera(43,16/9,.08,180),inside=!['street','park'].includes(location),night=['reading','corridor','foyer'].includes(location);let pool=[];
 scene.background=new H.Color(night?'#253548':inside?'#bdc6c8':'#a9cbd7');scene.fog=new H.Fog(scene.background,45,100);
 const hemi=new H.HemisphereLight(night?'#afc5e2':'#fff1d9',night?'#192938':'#687b86',night?1.1:1.6),sun=new H.DirectionalLight(night?'#ffcf8f':'#ffe9ca',night?1.5:2.0);sun.position.set(-5,10,8);scene.add(hemi,sun);
 const add=x=>(scene.add(x),x),box=(c,p,s)=>{pool.push({shape:'box',c,p,s});},sphere=(c,p,s)=>{pool.push({shape:'sphere',c,p,s});},dynamic=(shape,c,p,s,parent=scene)=>{const m=L.mesh(shape,c,p,s);parent.add(m);return m;};
 function flush(){for(const shape of ['box','sphere']){const items=pool.filter(p=>p.shape===shape);if(!items.length)continue;const m=new H.InstancedMesh(L.geo[shape],new H.MeshLambertMaterial({color:'#ffffff',flatShading:true}),items.length),dummy=new H.Object3D();items.forEach((p,i)=>{dummy.position.set(...p.p);dummy.scale.set(...p.s);dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);m.setColorAt(i,new H.Color(p.c));});m.instanceMatrix.needsUpdate=true;if(m.instanceColor)m.instanceColor.needsUpdate=true;scene.add(m);}pool=[];}
 function textPanel(words,p,w=2,h=.5,bg='#2c5c65',fg='#fff1ce',parent=scene){const tex=T.canvasTex(640,160,(g,W,Q)=>{g.fillStyle=bg;g.fillRect(0,0,W,Q);g.fillStyle=fg;g.font='900 60px Nunito';g.textAlign='center';g.textBaseline='middle';g.fillText(words,W/2,Q/2,W-20);});const m=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tex,side:H.DoubleSide}));m.position.set(...p);parent.add(m);return m;}
 function plant(x,z,scale=1){box('#a56853',[x,.18*scale,z],[.4*scale,.36*scale,.4*scale]);for(let i=0;i<5;i++){const a=i*1.9;sphere(i%2?'#3e766b':'#648f6c',[x+Math.sin(a)*.2*scale,(.5+i*.07)*scale,z+Math.cos(a)*.16*scale],[.16*scale,.3*scale,.09*scale]);}}
 function table(x,z,w=2.3,h=.88){box('#be976e',[x,h,z],[w,.13,1.05]);for(const dx of [-w*.4,w*.4])for(const dz of [-.39,.39])box('#6c5b4b',[x+dx,h/2,z+dz],[.09,h,.09]);box('#a98865',[x,h-.25,z],[w-.15,.1,.07]);}
 function bench(x,z,w=3.6){box('#a37b58',[x,.55,z+.15],[w,.11,.5]);for(let i=0;i<3;i++)box('#937051',[x,.89+i*.15,z],[w,.1,.09]);for(const dx of [-w*.39,w*.39])box('#405560',[x+dx,.55,z],[.09,1.1,.12]);}
 function bookRow(x,y,z,w=2.1,rows=3){const colors=['#478a85','#b96c56','#d2b16c','#7c7aa2','#809764','#7098b1'];for(let r=0;r<rows;r++)for(let j=0;j<14;j++){const ht=.28+.11*(.5+.5*Math.sin(j*7.3+r*2));box(colors[(j+r)%6],[x-w*.45+j*w*.069,y+r*.56+ht/2,z],[w*.06,ht,.23]);box('#e6d7af',[x-w*.45+j*w*.069,y+r*.56+ht*.72,z+.123],[w*.045,.022,.012]);}}
 function shelf(x,z,w=2.2){for(const dx of [-w/2,w/2])box('#765e4d',[x+dx,1.5,z],[.11,3,.45]);for(let i=0;i<5;i++)box('#8e7156',[x,.17+i*.56,z],[w,.09,.5]);bookRow(x,.23,z+.02,w*.95,4);}
 function lamp(x,z){box('#5c636b',[x,.63,z],[.07,1.26,.07]);sphere('#b4a380',[x,.06,z],[.25,.05,.25]);const shade=new H.Mesh(new H.CylinderGeometry(.24,.4,.35,12),L.mat('#e9c993'));shade.position.set(x,1.45,z);add(shade);const glow=new H.Mesh(new H.CircleGeometry(1,32),new H.MeshBasicMaterial({color:'#ffc885',transparent:true,opacity:.1,depthWrite:false}));glow.rotation.x=-Math.PI/2;glow.position.set(x,.012,z);glow.scale.set(1.25,.9,1);add(glow);}
 function floor(){for(let x=-14;x<14;x++)for(let z=-6;z<9;z++){const shift=z%2?.5:0,v=(x*3+z*7)%5;box(['#9e836b','#a58b72','#af967c','#957e69','#b49b80'][(v+5)%5],[x+shift,-.06,z*.8],[.988,.12,.79]);}}
 const A={};for(const id of ['nico','lia','sol','gui','ari','courier']){A[id]=actor(T,id);scene.add(A[id].root);}
 const P={};
 if(inside){const front=new H.Group();add(front);P.front=front;dynamic('box',night?'#4b5963':'#b5a48c',[0,2,6.8],[28,4,.15],front);dynamic('box','#6d675d',[0,.2,6.68],[28,.4,.1],front);for(const x of [-4,1,5]){dynamic('box','#6e5b4c',[x,1.8,6.65],[2.6,2.3,.12],front);dynamic('box','#cebda0',[x,1.8,6.56],[2.35,2.05,.1],front);for(let i=0;i<4;i++)dynamic('box',['#69948d','#ad7f65','#bca875','#8e88a2'][i],[x-.7+i*.48,1.8,6.48],[.35,1.45,.05],front);}const sign=textPanel('ENCONTRO DE LEITURA',[0,3.35,6.43],4,.48,'#3f6a6b','#fff1cf',front);sign.rotation.y=Math.PI;}

 if(inside){
  floor();box(night?'#55646c':'#d5c7ae',[0,2,-4.35],[28,4,.18]);box('#c0ad90',[-7,2,.3],[.16,4,9]);box('#7f7564',[0,.13,-4.18],[28,.26,.12]);box('#e1cfb1',[0,3.7,-4.18],[28,.13,.13]);
  // Window with exterior geometry, panes, mullions and curtains; no image background.
  box(night?'#213a54':'#8fb8c7',[-3.9,2.25,-4.23],[3.6,2.0,.05]);for(let i=0;i<6;i++)box(night?'#34495f':'#7897a5',[-5.3+i*.52,1.7+(.5+.5*Math.sin(i*2))*.3,-4.15],[.43,.8+.2*Math.sin(i),.04]);
  for(const x of [-5.7,-3.9,-2.1])box('#e3d7bd',[x,2.25,-4.05],[.09,2.12,.12]);for(const y of [1.2,2.25,3.3])box('#e3d7bd',[-3.9,y,-4.05],[3.7,.08,.12]);
  for(const x of [-5.95,-1.85])for(let j=0;j<4;j++)box('#9a9985',[x+j*.07,2.2,-3.97],[.075,2.25,.1]);
  for(let i=0;i<5;i++){box('#dbc7a7',[7+i*.48,2.5,-4.04],[.33,.45,.04]);box(['#73978f','#b17e69','#8b8fab'][i%3],[7+i*.48,2.5,-4],[.25,.36,.025]);}
  plant(-5.9,-2.8,1.3);plant(5.6,-2.9,1.3);
 }
 if(['library','reading'].includes(location)){
  shelf(-.2,-3.7,2.2);shelf(4.3,-3.7,2.1);shelf(-5.9,-1.4,1.6);table(-1.5,-.6,2.8);table(4,1.2,2.2);bench(-1.4,-1.65,2.7);lamp(5.9,.8);
  textPanel('BIBLIOTECA DO BAIRRO',[2.1,3.35,-4.1],4,.4);textPanel('NOITE DE HISTÓRIAS',[2.8,2.4,-4.0],1.7,.42,'#b77858');
  for(let i=0;i<9;i++)box(i%2?'#e6d8b6':'#73988e',[-2.5+i*.25,.98,-.6],[.2,.06,.32]);
  // Unsafe shelf pivots around its floor contact. Its contents follow the same transform.
  const g=new H.Group();g.position.set(2.8,0,-2);add(g);P.shelf=g;
  for(const dx of [-.72,.72])dynamic('box','#87664c',[dx,1.35,0],[.10,2.7,.48],g);
  for(let j=0;j<5;j++)dynamic('box','#ac8059',[0,.16+j*.55,0],[1.52,.08,.53],g);
  for(let i=0;i<40;i++){const row=Math.floor(i/10),j=i%10;dynamic('box',['#589b8e','#c77c62','#d0ad69','#8683ac'][i%4],[-.62+j*.135,.38+row*.55,.03],[.105,.34,.3],g);}
 }
 if(['cafe','home'].includes(location)){
  box('#8e9b87',[0,.47,-3.66],[4.0,.94,.85]);box('#d8c9b3',[0,.99,-3.6],[4.15,.12,1.0]);for(let i=0;i<4;i++){box('#5f7066',[-1.5+i,.46,-3.2],[.025,.68,.025]);sphere('#cfb68a',[-1.37+i,.57,-3.17],[.03,.03,.03]);}
  box('#424c50',[.7,1.02,-3.2],[1.0,.035,.6]);box('#cac3ae',[-.8,1.16,-3.5],[.3,.3,.3]);table(-1.3,-.3,2.5);bench(-1.4,-1.38,2.7);lamp(3.8,-2.2);
  textPanel(location==='cafe'?'CAFÉ DA PRAÇA':'HOJE',[2.8,2.6,-4.05],2,.55,'#80675b');
  if(location==='home'){
   box('#4a6671',[3.6,.4,-1.4],[2,.8,1.3]);box('#c4b094',[3.6,.88,-1.4],[2,.16,1.3]);box('#d2c7b7',[3.1,1,-1.6],[.65,.12,.65]);box('#789b9c',[-4.2,1.5,-4],[1.3,1.8,.06]);box('#c7d1c3',[-4.2,1.5,-3.96],[1.1,1.6,.03]);
  }
 }
 if(['corridor','foyer'].includes(location)){
  for(const x of [-4.5,0,4.5]){box('#806a59',[x,1.35,-4.1],[2.1,2.7,.12]);box('#b3936e',[x,2.75,-3.95],[2.3,.15,.18]);for(const dx of [-1.13,1.13])box('#b3936e',[x+dx,1.4,-3.95],[.14,2.8,.18]);sphere('#cda96b',[x+.75,1.25,-3.94],[.05,.05,.04]);}
  bench(-3.2,-2.5,2.5);lamp(-5.8,-2.0);plant(5,-3.1,1.5);textPanel('SAÍDA →',[1.7,3.1,-3.92],1.8,.48,'#27776b');
  // Foreground doorway supplies real occlusion as the cast crosses the corridor.
  for(const z of [-1.6,1.6])box('#8e735a',[5.6,1.5,z],[.18,3,.18]);box('#8e735a',[5.6,3,0],[.18,.18,3.4]);
  const door=new H.Group();door.position.set(5.6,0,-1.5);add(door);dynamic('box','#567a78',[0,1.4,1.4],[.10,2.8,2.8],door);dynamic('sphere','#dbbd77',[-.08,1.25,2.5],[.05,.05,.05],door);P.door=door;
 }
 if(!inside){
  box('#8d9c87',[0,-.1,0],[80,.2,50]);box('#b9b3a1',[0,.015,0],[70,.03,7]);box('#556e7a',[0,-.02,-6],[70,.04,5]);
  for(let x=-30;x<30;x++){box(x%2?'#bfb8a7':'#b4ae9e',[x,.038,1.2],[.97,.018,2.9]);box('#e8d6a0',[x*2,.02,-6],[.75,.025,.07]);}
  for(let i=-4;i<=4;i++){
   const x=i*5.3;box(['#c5b294','#a7b4ac','#b8a49e'][(i+6)%3],[x,1.7,-11],[4.8,3.4,4]);box('#795f52',[x,3.45,-11],[5,.18,4.4]);
   for(const dx of [-1.5,0,1.5]){box('#e4d4b4',[x+dx,2.0,-8.96],[1.0,1.4,.08]);box('#89aab3',[x+dx,2.0,-8.9],[.83,1.2,.06]);box('#dcd2b5',[x+dx,2,-8.83],[.06,1.2,.06]);box('#dcd2b5',[x+dx,2,-8.83],[.83,.06,.06]);}plant(x+2,-8.4,1.3);
  }
  bench(-1,0,4.2);lamp(5.4,-1.3);plant(-5,0,1.6);textPanel('PRAÇA DAS HISTÓRIAS',[0,3,-8.75],3.7,.5,'#456b70');
 }
 // Dynamic hand props.
 function group(){return add(new H.Group());}
 P.book=group();dynamic('box','#b97559',[0,0,0],[.35,.055,.45],P.book);dynamic('box','#f2dfb9',[0,.035,0],[.31,.025,.41],P.book);textPanel('HISTÓRIAS',[0,.06,.001],.29,.18,'#b97559','#fff0cf',P.book).rotation.x=-Math.PI/2;
 P.cup=group();const body=new H.Mesh(new H.CylinderGeometry(.105,.08,.2,12),L.mat('#f2dfb9'));P.cup.add(body);const rim=new H.Mesh(new H.TorusGeometry(.10,.012,6,16),L.mat('#fff0d1'));rim.rotation.x=Math.PI/2;rim.position.y=.1;P.cup.add(rim);const handle=new H.Mesh(new H.TorusGeometry(.055,.015,6,12),L.mat('#f4e6c9'));handle.position.z=.11;handle.rotation.y=Math.PI/2;P.cup.add(handle);
 P.paper=dynamic('box','#f1dfb6',[0,1,0],[.42,.025,.55]);P.phone=group();dynamic('box','#293c50',[0,0,0],[.12,.24,.035],P.phone);dynamic('box','#88bcb1',[0,0,.021],[.095,.18,.009],P.phone);
 P.toy=group();const watch=new H.Mesh(new H.CylinderGeometry(.09,.09,.035,16),L.mat('#e2bc63'));watch.rotation.x=Math.PI/2;P.toy.add(watch);dynamic('box','#cc8f60',[0,0,0],[.08,.37,.025],P.toy);
 P.flashlight=group();const fl=new H.Mesh(new H.CylinderGeometry(.045,.065,.24,10),L.mat('#526b75'));fl.rotation.z=Math.PI/2;P.flashlight.add(fl);dynamic('sphere','#fff0bd',[.13,0,0],[.06,.055,.055],P.flashlight);
 P.cart=group();dynamic('box','#547d7b',[0,.62,0],[1.1,.09,.67],P.cart);for(const y of [.14,.38])dynamic('box','#6e918b',[0,y,0],[1.1,.07,.67],P.cart);for(const x of [-.5,.5])dynamic('box','#425d61',[x,.42,0],[.05,.84,.05],P.cart);
 for(let i=0;i<8;i++)dynamic('box',['#bd7e63','#cdb477','#70958b'][i%3],[-.43+i*.12,.78,0],[.095,.25,.42],P.cart);for(const x of [-.43,.43])for(const z of [-.27,.27])dynamic('sphere','#253f49',[x,.09,z],[.09,.09,.06],P.cart);
 dynamic('box','#354d52',[-.55,.98,0],[.05,.3,.05],P.cart);dynamic('box','#354d52',[-.55,1.12,0],[.05,.05,.60],P.cart);
 P.chair=group();dynamic('box','#a48562',[0,.47,0],[.48,.09,.48],P.chair);for(const x of [-.2,.2])for(const z of [-.2,.2])dynamic('box','#77614c',[x,.23,z],[.055,.46,.055],P.chair);dynamic('box','#a48562',[0,.94,-.23],[.48,.55,.06],P.chair);
 if(location==='home'){const portrait=T.canvasTex(256,400,(g)=>{g.fillStyle='#bac9bd';g.fillRect(0,0,256,400);g.fillStyle='#101625';g.beginPath();g.arc(128,110,65,0,7);g.fill();g.fillStyle='#fff4db';for(const x of [105,151]){g.beginPath();g.ellipse(x,100,9,15,0,0,7);g.fill();}g.strokeStyle='#fff4db';g.lineWidth=6;g.beginPath();g.arc(128,118,26,.2,Math.PI-.2);g.stroke();g.fillStyle='#2ac9b4';g.fillRect(75,180,106,140);g.strokeStyle='#122230';g.lineWidth=13;g.beginPath();g.moveTo(100,320);g.lineTo(90,390);g.moveTo(155,320);g.lineTo(165,390);g.stroke();});const reflection=new H.Mesh(new H.PlaneGeometry(1.0,1.5),new H.MeshBasicMaterial({map:portrait}));reflection.position.set(-4.2,1.5,-3.91);add(reflection);}
 P.box=dynamic('box','#b9976b',[0,.25,0],[.9,.5,.7]);P.loose=[];for(let i=0;i<7;i++)P.loose.push(dynamic('box',['#ad785d','#68958b','#c6b16c'][i%3],[0,.05,0],[.28,.05,.4]));
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMapping=H.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;flush();
 const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){}};const state={stage,scene,camera,A,P,hemi,sun,inside,night,location};cache.set(location,state);return state;
}
