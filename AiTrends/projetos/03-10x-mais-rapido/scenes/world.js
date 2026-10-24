import {mood} from '/engine/core.js';
import {actor,library} from './rig.js';
const WORLDS=new Map();
export function world(T,location){
 if(WORLDS.has(location))return WORLDS.get(location);
 const L=library(T),{H,mesh,mat}=L,scene=new H.Scene(),camera=new H.PerspectiveCamera(43,16/9,.05,400);
 const inside=['home','cafe','workshop'].includes(location),sunset=location==='rooftop',M=mood(inside?'interiorWarm':sunset?'dusk':'golden');
 scene.background=new H.Color(inside?'#a5b3ba':sunset?'#d8b1ad':'#b6dbe5');scene.fog=new H.Fog(inside?'#a5b3ba':sunset?'#d8b1ad':'#b6dbe5',60,160);
 scene.add(new H.HemisphereLight('#fff6dd','#778e98',2.0));const sun=new H.DirectionalLight('#fff0cc',2.5);sun.position.set(-9,17,12);scene.add(sun);
 const add=(...x)=>{scene.add(...x);return x[0];};const box=(c,p,s)=>add(mesh('box',c,p,s));
 const ground=box(inside?'#c1afa0':'#8cb77d',[0,-.08,-1],[260,.16,130]);
 const A={nico:actor(T,'nico'),lia:actor(T,'lia'),sol:actor(T,'sol'),gui:actor(T,'gui')};for(const a of Object.values(A))add(a.root);
 const props={};
 function label(word,p,w=2,h=.6,color='#f8eacf',bg='#34495c'){
  const tex=T.canvasTex(512,128,(g,W,Q)=>{g.fillStyle=bg;g.fillRect(0,0,W,Q);g.fillStyle=color;g.font='900 54px Nunito';g.textAlign='center';g.textBaseline='middle';g.fillText(word,W/2,Q/2);});const ob=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tex,side:H.DoubleSide}));ob.position.set(...p);add(ob);return ob;
 }
 function tree(x,z,s=1){box('#765c46',[x,.8*s,z],[.18*s,1.6*s,.18*s]);for(const [dx,dy,dz,r]of [[0,1.9,0,.65],[-.35,1.65,.05,.5],[.35,1.7,-.05,.5]])add(mesh('sphere','#538d62',[x+dx*s,dy*s,z+dz*s],[r*s,r*s,r*s]));}
 function house(x,z,c,i){box(c,[x,1.5,z],[4.1,3,3]);box('#9b6655',[x,3.1,z],[4.5,.23,3.5]);for(const dx of [-1.15,1.15]){box('#e8eadb',[x+dx,1.8,z+1.52],[.94,1.1,.04]);box('#90bbc5',[x+dx,1.8,z+1.55],[.75,.9,.045]);}box('#507b97',[x,.85,z+1.55],[.65,1.7,.06]);box('#d5d2bf',[x,0,z+3],[4.7,.08,3]);if(i%2===0)tree(x+2.5,z+2.8,.9);}
 function bench(x,z,w=2.6){const g=new H.Group();for(let i=0;i<3;i++){const b=mesh('box','#936e58',[0,.88+i*.14,0],[w,.1,.11]);g.add(b);}g.add(mesh('box','#ae8967',[0,.55,.13],[w,.11,.45]));for(const dx of [-w*.38,w*.38])g.add(mesh('box','#415261',[dx,.55,0],[.08,1.1,.08]));g.position.set(x,0,z);add(g);return g;}
 function table(x,z,w=1.65){const g=new H.Group();g.add(mesh('box','#c6a77f',[0,.88,0],[w,.12,.85]));for(const dx of [-w*.38,w*.38])for(const dz of [-.3,.3])g.add(mesh('box','#79654e',[dx,.43,dz],[.07,.86,.07]));g.position.set(x,0,z);add(g);return g;}
 function cup(){const g=new H.Group(),body=new H.Mesh(new H.CylinderGeometry(.105,.08,.2,12),mat('#f3e8d4'));g.add(body);const rim=new H.Mesh(new H.TorusGeometry(.1,.012,6,16),mat('#f5eeda'));rim.rotation.x=Math.PI/2;rim.position.y=.1;g.add(rim);const handle=new H.Mesh(new H.TorusGeometry(.055,.014,6,12),mat('#f5eeda'));handle.position.z=.12;handle.rotation.y=Math.PI/2;g.add(handle);return add(g);}
 function ball(){const b=mesh('sphere','#f3e8bd',[0,.16,0],[.16,.16,.16]);add(b);for(let i=0;i<3;i++){const mark=mesh('sphere','#4e6480',[.13*Math.cos(i*2),.05,.13*Math.sin(i*2)],[.06,.055,.035],true);b.add(mark);mark.position.multiplyScalar(1/.16);mark.scale.multiplyScalar(1/.16);}return b;}
 function car(c){const g=new H.Group();g.add(mesh('box',c,[0,.5,0],[2.3,.7,1.1]),mesh('box',c,[-.1,1.02,0],[1.25,.6,.92]),mesh('box','#9cc5d1',[.08,1.03,.47],[.9,.4,.025]));for(const x of [-.73,.73])for(const z of [-.57,.57])g.add(mesh('sphere','#273343',[x,.28,z],[.29,.29,.13]));return add(g);}
 if(!inside){
  box('#627382',[0,-.005,-4.5],[250,.06,6]);box('#d5cfc3',[0,.015,0],[250,.09,3]);box('#bfc4bb',[0,.1,-1.55],[250,.2,.18]);
  for(let x=-120;x<120;x+=3)box('#ebdfae',[x,.032,-4.5],[1.5,.025,.08]);
  const colors=['#d4b893','#b9c9bb','#c9b3a6','#dbcca9','#b2c4cc'];for(let i=-9;i<10;i++)house(i*6,-11,colors[(i+10)%5],i);
  for(let x=-44;x<50;x+=9)tree(x,-8.5,1.1);
  for(let x=-36;x<42;x+=12){box('#627783',[x,1.8,-1.2],[.06,3.6,.06]);box('#f4edc5',[x+.23,3.5,-1.2],[.55,.13,.25]);}
  props.car=car('#687fa2');props.car.position.set(16,0,-4.5);
 }
 if(location==='track'){
  box('#9d615b',[5,.06,2],[74,.08,10]);for(let z=-2;z<=6;z+=1.7)box('#eee0c3',[5,.11,z],[74,.015,.045]);
  for(let x=-12;x<35;x+=5)label(String((x+12)*2),[x,.14,4],.6,.28,'#fff4d0','#9d615b').rotation.x=-Math.PI/2;
  bench(-3,7,3.5);for(let x=0;x<7;x++)box('#e8e5d3',[24,.13,-1+x*.9],[.3,.02,.6]);
 }
 if(['park','plaza'].includes(location)){box('#d6c8ae',[6,.05,1],[50,.08,8]);bench(3,2.5,3.4);for(const x of [-9,13,20])tree(x,5,1.5);if(location==='plaza'){add(new H.Mesh(new H.CylinderGeometry(1.1,1.2,.4,20),mat('#a8bfc2'))).position.set(-6,.2,4);box('#a8d6dc',[-6,.43,4],[1.7,.03,1.7]);}}
 if(location==='intersection'){
  for(let i=0;i<9;i++)box('#f0e5cf',[1,.041,-7+i*.65],[3,.025,.34]);box('#5c6d74',[5,1.6,-1.4],[.08,3.2,.08]);const sig=box('#384253',[5,2.8,-1.4],[.35,.65,.3]);add(mesh('sphere','#ed6a5d',[5,2.98,-1.22],[.1,.1,.04],true));
  props.bus=new H.Group();props.bus.add(mesh('box','#f1ebd4',[0,1.0,0],[5.3,1.7,1.65]),mesh('box','#348e89',[0,.67,.84],[5.1,.22,.03]));for(let x=-1.8;x<2;x+=.75)props.bus.add(mesh('box','#a2c4cf',[x,1.45,.85],[.57,.55,.035]));for(const x of [-1.65,1.65])for(const z of [-.87,.87])props.bus.add(mesh('sphere','#253545',[x,.33,z],[.34,.34,.15]));add(props.bus);
 }
 if(inside){
  box('#ded1bd',[0,2,-3.3],[14,4,.2]);box('#e3d6c3',[-6.4,2,0],[.2,4,8]);box('#a1bcc7',[3,2.3,-3.16],[2.8,2,.04]);for(const x of [2.55,3.45])box('#f2ead3',[x,2.3,-3.1],[.06,2,.06]);box('#f2ead3',[3,2.3,-3.1],[2.8,.06,.06]);
  props.table=table(-.6,.05,2.6);bench(-3,1.4,2);
  if(location==='cafe'){box('#ad8269',[0,.55,-2],[6.5,1.1,.7]);label('CAFÉ DA PRAÇA',[0,2.8,-3.1],3,.55,'#f8e5bc','#ad8269');for(let i=0;i<5;i++)box('#c8a474',[-2+i,.2,-2],[.2,.2,.2]);}
  if(location==='home'){box('#8c9eab',[-3,.35,-1],[1.6,.7,2.6]);box('#e8d8b5',[-3,.78,-1],[1.65,.16,2.6]);box('#f1e7d4',[-3,.92,-1.9],[1.2,.12,.55]);label('08:03',[-4.3,.95,-1],.6,.3,'#f2b077','#44505e');}
  if(location==='workshop'){label('OFICINA',[0,2.8,-3.1],2,.55,'#fff0d6','#6c858c');for(let i=0;i<6;i++)box('#627781',[-2+i*.6,1.8,-3],[.2,.5,.08]);}
 }
 if(location==='rooftop'){
  box('#9995a0',[0,-.05,0],[32,.1,20]);box('#738895',[0,.6,-3],[28,1.2,.15]);for(let i=-5;i<6;i++)box('#86849c',[i*5,1,-15],[3,2+(i*i%5),3]);bench(0,1,4);
 }
 // Reusable animated props, never external images/models.
 props.cup=cup();props.extraCup=cup();props.thirdCup=cup();props.ball=ball();props.toast=box('#e2b276',[0,1,0],[.22,.06,.24]);props.tray=box('#e9cfac',[0,1,0],[.75,.05,.42]);
 props.paper=[];for(let i=0;i<10;i++)props.paper.push(box('#f5eacb',[0,1,0],[.2,.012,.3]));
 props.birds=[];for(let i=0;i<6;i++){const bird=new H.Group();bird.add(mesh('sphere','#657e91',[0,0,0],[.13,.09,.2]),mesh('sphere','#728aa1',[.12,.08,0],[.07,.07,.08]));const wingL=mesh('box','#8199a9',[0,.04,.16],[.3,.025,.22]),wingR=mesh('box','#8199a9',[0,.04,-.16],[.3,.025,.22]);bird.add(wingL,wingR);add(bird);props.birds.push({root:bird,wingL,wingR});}
 props.cones=[];for(let i=0;i<3;i++){const cone=new H.Mesh(new H.ConeGeometry(.17,.45,10),mat('#e89465'));cone.position.set(4+i*4,.23,0);add(cone);props.cones.push(cone);}
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMapping=H.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){/* Worlds shared across shots; released when Chromium closes. */}};
 const state={stage,scene,camera,A,props,location,label};WORLDS.set(location,state);return state;
}
