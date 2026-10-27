// Episode06 original procedural sets. Broad details and stable light for temporal quality.
import {library,actor} from './rig.js';
const cache=new Map();
export function world(T,location){
 if(cache.has(location))return cache.get(location);
 const H=T.THREE,L=library(T),scene=new H.Scene(),camera=new H.PerspectiveCamera(42,16/9,.08,140),inside=['school','supply','clinic'].includes(location),space=location==='diagram';
 scene.background=new H.Color(space?'#10293f':inside?'#9caea9':'#b5ced0');scene.fog=new H.Fog(scene.background,35,90);
 const sun=new H.DirectionalLight('#ffe1ae',2.1);sun.position.set(-5,8,6);scene.add(sun,new H.HemisphereLight('#e4f0e3','#50687c',1.65));
 const add=(shape,color,pos,scale,parent=scene,basic=false)=>{const m=L.mesh(shape,color,pos,scale,basic);parent.add(m);return m;};
 const P={},group=id=>{const g=new H.Group();scene.add(g);P[id]=g;return g;};
 function sign(words,pos,w=2.5,h=.5,bg='#285b63',parent=scene){const tx=T.canvasTex(720,180,(g,W,Q)=>{g.fillStyle=bg;g.fillRect(0,0,W,Q);g.fillStyle='#fff2cf';g.font='900 65px Nunito';g.textAlign='center';g.textBaseline='middle';g.fillText(words,W/2,Q/2,W-30);});const m=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tx,side:H.DoubleSide}));m.position.set(...pos);parent.add(m);return m;}
 function lamp(x,z){add('box','#4d6570',[x,1.5,z],[.09,3,.09]);add('sphere','#f1cf8d',[x,2.9,z],[.2,.2,.2],scene,true);}
 function table(x,z){add('box','#ac8764',[x,.90,z],[2.5,.14,1.1]);for(const a of [-1,1])for(const b of [-.39,.39])add('box','#695f4e',[x+a,.43,z+b],[.10,.86,.10]);}
 function planter(x,z){add('box','#9e7957',[x,.25,z],[.65,.5,.65]);for(let i=0;i<4;i++)add('sphere','#639573',[x+Math.sin(i*2)*.16,.65+i*.07,z],[.16,.35,.13]);}
 if(!space){add('box',inside?'#a89076':location==='garden'?'#779786':'#b0aa94',[0,-.13,0],[90,.26,60]);}
 if(inside){
  add('box','#b4b5a3',[0,2,-3.8],[22,4,.2]);add('box','#6d8d96',[-4.4,2.0,-3.64],[3.5,2.2,.10]);for(const x of [-6.1,-4.4,-2.7])add('box','#d5c9ad',[x,2,-3.5],[.1,2.25,.15]);add('box','#d5c9ad',[-4.4,2,-3.49],[3.5,.1,.15]);
  add('box','#7b7b68',[0,.14,-3.6],[22,.28,.12]);table(-.25,.1);planter(-5.9,-2.5);
  for(const x of [3,6]){for(const y of [.7,1.5,2.3])add('box','#7f735b',[x,y,-3.2],[2.2,.1,.7]);for(let j=0;j<4;j++)add('box',['#4b9294','#b7805b','#bfa465','#7e7b9e'][j],[x-.75+j*.48,1.76,-3.2],[.33,.42,.35]);}
 }
 if(location==='street'){
  add('box','#6f8791',[0,.012,-3],[80,.03,3.5]);add('box','#cfbc95',[0,.018,1.4],[80,.04,3.3]);
  for(let i=0;i<7;i++){const x=-14+i*4.1;add('box',['#a5a9a0','#9a9e9b','#b4a58d'][i%3],[x,3.1,-6],[3.7,6.2,2]);for(const dx of [-1,0,1])for(const y of [2.3,4.2])add('box','#dbd2b1',[x+dx,y,-4.92],[.58,.94,.1]);}
  add('box','#6b8a81',[0,1.35,-4.75],[3.8,2.7,.18]);add('box','#9ab7b6',[0,1.7,-4.60],[3.3,1.5,.1]);sign('CAFÉ DA PRAÇA',[0,3.0,-4.5],3.9,.55);add('box','#c8b28c',[0,2.5,-4.1],[4.0,.12,1.0]);
  for(let i=0;i<8;i++)add('box',i%2?'#e4ca9b':'#b16f5b',[-1.75+i*.5,2.43,-3.75],[.46,.12,.55]);
  table(.1,-2.3);planter(-2.8,-3.0);planter(2.8,-3.0);for(const x of [-6.8,5.6])lamp(x,-2.5);
  const signal=group('signal');add('box','#2f4554',[0,1.9,0],[.38,1.0,.30],signal);for(let i=0;i<3;i++)P['lamp'+i]=add('sphere',['#b66e60','#ceb06b','#70ad8e'][i],[.0,2.2-i*.3,.17],[.105,.105,.04],signal,true);signal.position.set(-4.8,0,-1.4);add('box','#455b63',[-4.8,.95,-1.4],[.07,1.9,.07]);
 }
 if(location==='school'){
  const board=group('board');add('box','#78664e',[0,0,0],[4.5,2.5,.13],board);add('box','#244d49',[0,0,.09],[4.22,2.22,.06],board);for(const x of [-1.5,1.5])add('box','#645d4d',[x,-1.6,0],[.08,1.1,.35],board);board.position.set(.6,1.9,-1.45);sign('DUAS PESSOAS → UMA HUMANIDADE?',[0,3.45,-3.60],5.2,.45);
 }
 if(location==='supply'){
  sign('ÁGUA • FERRAMENTAS • CUIDADO',[.8,3.25,-3.60],5.7,.45);const pump=group('pump');add('box','#527c80',[0,.55,0],[.65,1.1,.6],pump);add('box','#8eaca2',[.2,1.12,.0],[.9,.1,.1],pump);pump.position.set(2.7,0,.6);
  const freezer=group('freezer');add('box','#bbcbc5',[0,.7,0],[1.4,1.4,.9],freezer);add('box','#638c95',[0,.85,.47],[1.2,.9,.06],freezer);sign('ARMAZENAMENTO',[0,1.85,.5],2,.35,'#385b68',freezer);freezer.position.set(3.5,0,-.8);
 }
 if(location==='clinic'){
  const bench=group('bench');add('box','#78999b',[0,.58,0],[2.7,.15,1.0],bench);add('box','#ced5c0',[0,.72,0],[2.65,.16,1.0],bench);for(const x of [-1.1,1.1])add('box','#5e7377',[x,.3,0],[.1,.6,.8],bench);bench.position.set(1.6,0,-.6);sign('CUIDAR TAMBÉM É RECONSTRUIR',[1,3.25,-3.60],5.5,.45);
 }
 if(location==='garden'){
  add('box','#b9b38d',[0,.025,1.6],[70,.05,3.2]);for(const x of [-5,4.5]){add('box','#7e6950',[x,1.3,-1.8],[.25,2.6,.25]);add('sphere','#6e9978',[x,3.2,-1.8],[1.7,1.6,1.5]);}
  for(let i=0;i<5;i++){add('box','#947955',[-1.8+i*.9,.18,-.7],[.65,.35,.85]);add('sphere',['#779b6c','#9aa86b','#5e947e'][i%3],[-1.8+i*.9,.56,-.7],[.28,.35,.3]);}lamp(6,-.4);
 }
 if(location==='harbor'){
  add('box','#608f9e',[0,-.11,-1.5],[70,.04,13],scene,true);for(const x of [-4.3,4.3]){add('box','#927956',[x,.08,1.5],[6,.16,4.0]);for(const z of [-.5,3.5])add('box','#68706a',[x,.62,z],[6,.08,.08]);}
  for(const x of [-7.2,-1.4,1.4,7.2])for(const z of [-.5,3.5])add('box','#6c6656',[x,.45,z],[.1,.9,.1]);
  const plank=group('plank');add('box','#c49d64',[0,0,0],[3.3,.14,.65],plank);plank.position.set(0,.20,1.4);lamp(5,0);
  add('sphere','#dfc187',[5.2,1.5,-3],[.13,.13,.13],scene,true);
 }
 if(space){scene.background=new H.Color('#102c43');}
 const A={};for(const id of ['nico','lia','sol','ari','courier']){A[id]=actor(T,id);scene.add(A[id].root);A[id].root.visible=false;}
 // Portable props shared across sets; not photographs or imported assets.
 const radio=group('radio');add('box','#3b5e68',[0,0,0],[.35,.23,.17],radio);add('box','#a5c4b7',[.05,.02,.095],[.13,.09,.025],radio);add('sphere','#e7c58b',[-.1,-.02,.10],[.04,.04,.02],radio);add('box','#d5dcc9',[-.1,.23,0],[.018,.30,.018],radio);
 const jug=group('jug');add('box','#719fbc',[0,0,0],[.24,.32,.20],jug);add('box','#c4daca',[0,.19,0],[.10,.06,.08],jug);
 const tool=group('tool');add('box','#8aa3aa',[0,0,0],[.055,.26,.04],tool);add('box','#d6b57a',[0,-.17,0],[.085,.12,.065],tool);
 const paper=group('paper');add('box','#e5d9b6',[0,0,0],[.45,.025,.34],paper);for(let i=0;i<3;i++)add('box','#6f9693',[-.13+i*.13,.019,0],[.035,.012,.24],paper);
 for(const [id,color]of [['boxA','#449b99'],['boxB','#9c79b4']]){const ob=group(id);add('box',color,[0,.13,0],[.5,.26,.42],ob);const lid=new H.Group();lid.position.set(0,.28,-.21);ob.add(lid);P[id==='boxA'?'lidA':'lidB']=lid;add('box','#d8c7a3',[0,0,.225],[.52,.04,.45],lid);}
 const card=group('card');add('box','#e9d6aa',[0,0,0],[.24,.32,.035],card);add('sphere','#a17fc0',[0,0,.03],[.065,.065,.02],card,true);
 const cards=group('cards');for(let i=0;i<4;i++){const card=add('box','#e8d5ad',[(i-1.5)*.075,0,i*.025],[.18,.27,.018],cards);card.rotation.z=(i-1.5)*.12;add('sphere',['#66c9b2','#ad83be','#d5b16a','#7da5c5'][i],[(i-1.5)*.075,.02,.025+i*.025],[.04,.04,.015],cards,true);}
 const seed=group('seed');add('sphere','#c4a274',[0,0,0],[.09,.06,.06],seed);
 const pointer=group('pointer');add('box','#c7b48b',[0,0,0],[.8,.025,.025],pointer);
 const diagram=group('diagram'),nodes=[];
 for(let i=0;i<40;i++){const m=add('sphere',['#67cbb3','#aa84c4','#d7b16a','#75a4c8'][i%4],[0,0,0],[.16,.16,.16],diagram);nodes.push(m);}
 const bars=[];for(let i=0;i<12;i++)bars.push(add('box','#67cbb3',[0,0,0],[.16,.5,.16],diagram));
 const edges=[];for(let i=0;i<32;i++){const edge=L.bone(diagram,'#8baaaa',.022);edges.push(edge);}
 P.diagramNodes=nodes;P.diagramBars=bars;P.diagramEdges=edges;
 for(const [id,ob]of Object.entries(P))if(ob?.isObject3D)ob.visible=false;
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMappingExposure=.98;const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){}};
 return cache.set(location,{H,L,stage,scene,camera,A,P,location}).get(location);
}
