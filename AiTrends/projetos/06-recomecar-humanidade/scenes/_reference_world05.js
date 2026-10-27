// Original procedural workshop for the opening pilot. No reference frames imported.
import {actor,library} from './rig.js';
const cache=new Map();
export function world(T,location='workshop'){
 if(cache.has(location))return cache.get(location);const H=T.THREE,L=library(T),scene=new H.Scene();scene.background=new H.Color('#b4c8cb');scene.fog=new H.Fog('#b4c8cb',28,55);
 const camera=new H.PerspectiveCamera(42,16/9,.08,80),sun=new H.DirectionalLight('#ffe0ad',2);sun.position.set(-4,8,6);scene.add(sun,new H.HemisphereLight('#f5e6d2','#62767e',1.6));
 const add=(shape,c,p,s,parent=scene,basic=false)=>{const m=L.mesh(shape,c,p,s,basic);parent.add(m);return m;};
 add('box','#ad9174',[0,-.12,0],[25,.24,18]);add('box','#c4b7a0',[0,2,-3.6],[25,4,.22]);
 // Broad, separated geometry; no near-coplanar striped floor or small repeating marks.
 add('box','#6a7f83',[-3,2,-3.42],[3.9,2.45,.16]);add('box','#98bac2',[-3,2,-3.27],[3.6,2.17,.12]);
 for(const x of [-4.85,-3,-1.15])add('box','#e3cfab',[x,2,-3.12],[.12,2.4,.16]);add('box','#e3cfab',[-3,2,-3.10],[3.9,.12,.18]);
 add('box','#84674d',[.65,.88,0],[2.8,.14,1.1]);for(const x of [-.45,1.75])for(const z of [-.39,.39])add('box','#5e594c',[x,.42,z],[.11,.84,.11]);
 // Shelves intentionally use larger objects with wide silhouette separation.
 for(const y of [.65,1.6,2.55])add('box','#79614d',[3.8,y,-3.05],[3.2,.13,.8]);
 for(let i=0;i<8;i++)add('box',['#4f8e8a','#b77958','#c8a761','#7d789b'][i%4],[2.5+i*.34,1.9,-3.0],[.24,.55,.4]);
 for(const x of [2.3,5.3])add('box','#695b4b',[x,1.5,-3.05],[.14,3,.8]);
 add('box','#677e68',[-5,.25,-1.5],[.65,.5,.65]);for(let i=0;i<4;i++)add('sphere','#5b8a6e',[-5+Math.sin(i*2)*.18,.7+i*.16,-1.5],[.2,.4,.15]);
 const box=new H.Group();box.position.set(-.2,.98,.38);scene.add(box);
 add('box','#785740',[0,.15,0],[.63,.3,.47],box);add('box','#292e33',[0,.31,0],[.51,.025,.36],box);
 const lid=new H.Group();lid.position.set(0,.32,-.235);box.add(lid);add('box','#9c7750',[0,.025,.235],[.66,.07,.5],lid);add('box','#c5a16b',[0,.035,.5],[.12,.08,.025],lid);
 const tex=T.canvasTex(640,480,(g,W,Q)=>{g.fillStyle='#e9dcc0';g.fillRect(0,0,W,Q);g.fillStyle='#648b88';g.fillRect(28,22,W-56,Q-110);for(const [x,c]of [[225,'#2ac9b4'],[410,'#ac76e2']]){g.strokeStyle=c;g.lineWidth=38;g.lineCap='round';g.beginPath();g.moveTo(x,190);g.lineTo(x,310);g.stroke();g.fillStyle='#141b25';g.beginPath();g.arc(x,145,47,0,7);g.fill();}g.fillStyle='#655545';g.font='900 31px Nunito';g.textAlign='center';g.fillText('A CADEIRA FICOU PRONTA',W/2,Q-38);});
 const photo=new H.Group();scene.add(photo);add('box','#f1e3c4',[0,0,0],[.36,.29,.045],photo);const panel=new H.Mesh(new H.PlaneGeometry(.32,.25),new H.MeshBasicMaterial({map:tex,side:H.DoubleSide}));panel.position.z=.03;photo.add(panel);
 if(location!=='workshop')for(const ob of scene.children)if(ob.isMesh)ob.visible=false;
 const A={};for(const id of ['nico','lia','sol','ari','gui']){A[id]=actor(T,id);scene.add(A[id].root);A[id].root.visible=false;}const nico=A.nico;
 const P={box,lid,photo};
 const group=(name)=>{const ob=new H.Group();scene.add(ob);P[name]=ob;return ob;};
 const chair=group('chair');for(const x of [-.25,.25])for(const z of [-.2,.2])add('box','#856447',[x,.28,z],[.06,.56,.06],chair);add('box','#c5975e',[0,.57,0],[.63,.10,.56],chair);const chairBack=new H.Group();chair.add(chairBack);P.chairBack=chairBack;for(const x of [-.26,.26])add('box','#856447',[x,.95,-.22],[.07,.8,.07],chairBack);add('box','#b48a5b',[0,1.15,-.22],[.58,.35,.08],chairBack);
 const tool=group('tool');add('box','#aab5b4',[0,0,0],[.05,.32,.035],tool);add('box','#c8a16b',[0,-.18,0],[.08,.15,.07],tool);
 const notebook=group('notebook');add('box','#f0dcad',[0,0,0],[.38,.04,.45],notebook);add('box','#597f7a',[0,-.026,0],[.4,.02,.47],notebook);
 const phone=group('phone');add('box','#192a38',[0,0,0],[.14,.24,.025],phone);add('box','#7cbaac',[0,0,.016],[.115,.19,.008],phone);
 const wheel=group('wheel');const ring=new H.Mesh(new H.TorusGeometry(.22,.055,10,24),L.mat('#344454'));wheel.add(ring);add('sphere','#a6b6b1',[0,0,0],[.07,.07,.07],wheel);for(let i=0;i<4;i++){const b=add('box','#9cacaa',[0,0,0],[.38,.025,.028],wheel);b.rotation.z=i*Math.PI/4;}
 const cart=group('cart');add('box','#b6a079',[0,.56,0],[.9,.10,.6],cart);for(const x of [-.35,.35])for(const z of [-.22,.22])add('sphere','#3e4e56',[x,.21,z],[.13,.13,.13],cart);for(const x of [-.4,.4])add('box','#49636b',[x,.9,-.22],[.06,.7,.06],cart);add('box','#49636b',[0,1.24,-.22],[.85,.05,.06],cart);
 const plant=group('plant');add('box','#a97952',[0,.15,0],[.36,.3,.36],plant);add('box','#47745b',[0,.5,0],[.035,.5,.035],plant);for(let i=0;i<4;i++){const leaf=add('sphere','#71a67c',[(i%2?-.12:.12),.4+i*.09,0],[.15,.07,.09],plant);leaf.rotation.z=i%2?-.4:.4;}
 const suitcase=group('suitcase');add('box','#bc8e52',[0,0,0],[.55,.40,.26],suitcase);add('box','#dcc69b',[0,.24,0],[.22,.08,.07],suitcase);
 // Broad luminous beads show cell replication without flashing or subpixel strokes.
 const diagram=group('diagram');
 const chromosome=new H.Group();diagram.add(chromosome);P.chromosome=chromosome;
 for(const sign of [-1,1]){const ob=add('box','#70becd',[.7,1.3,0],[.18,1.8,.18],chromosome);ob.rotation.z=sign*.6;for(const end of [-1,1])add('sphere','#e0b76c',[.7+sign*end*.5,1.3+end*.73,0],[.17,.17,.17],chromosome);}
 const cell=new H.Group();diagram.add(cell);P.cell=cell;for(const x of [-.4,.5,1.4]){add('sphere','#58bbaa',[x,1.35,0],[.38,.38,.25],cell);add('sphere','#c6dab1',[x,1.35,.23],[.14,.14,.06],cell);}
 const jelly=new H.Group();diagram.add(jelly);P.jelly=jelly;add('sphere','#d49aba',[.7,1.6,0],[.55,.35,.3],jelly);for(let i=0;i<6;i++){const ob=add('box','#cfb3d0',[.3+i*.16,.99,0],[.045,.7,.045],jelly);ob.rotation.z=(i-2.5)*.06;}
 const docs=new H.Group();diagram.add(docs);P.docs=docs;for(let i=0;i<3;i++){add('box','#b6c9bb',[-.2+i*.75,1.3,0],[.58,.85,.05],docs);add('sphere',['#2ac9b4','#ac76e2','#d69b4d'][i],[-.2+i*.75,1.46,.06],[.13,.13,.04],docs);add('box','#5c7f87',[-.2+i*.75,1.17,.07],[.3,.055,.02],docs);}
 diagram.visible=false;
 for(const ob of Object.values(P))ob.visible=false;
 if(location==='garden'){
  scene.background=new H.Color('#b8d6da');scene.fog.color.copy(scene.background);
  add('box','#85a88d',[0,.01,2.8],[25,.04,12]);add('box','#c5b797',[0,.04,1.5],[25,.04,2.6]);
  // New park is in front of workshop geometry; no furniture in the actors' travel strip.
  for(const x of [-5,4.4]){add('box','#80684e',[x,1.2,-1.7],[.3,2.4,.3]);add('sphere','#719c79',[x,3,-1.7],[1.8,1.7,1.6]);}
  const bench=group('bench');add('box','#ab8054',[0,.55,0],[3.2,.12,.55],bench);add('box','#9a734e',[0,.98,-.35],[3.2,.66,.10],bench);for(const x of [-1.28,1.28])add('box','#465b5b',[x,.3,0],[.10,.6,.55],bench);bench.position.set(.1,0,1.45);bench.visible=true;
  for(let i=0;i<5;i++){add('box',['#8b9e9f','#a7b3aa','#b1b8a8'][i%3],[-8+i*3.7,1.7,-5],[2.8,3.4,.8]);for(const dx of [-.7,.7])add('box','#dce0bd',[-8+i*3.7+dx,2,-4.53],[.65,.85,.1]);}
  const tree=group('tree');add('box','#876548',[0,1.3,0],[.24,2.6,.24],tree);add('sphere','#6d9f77',[0,3.1,0],[1.6,1.6,1.3],tree);tree.position.set(-3.6,0,-.7);tree.visible=true;
 }
 if(location==='station'){
  scene.background=new H.Color('#233e55');add('box','#66838f',[0,.05,2],[26,.1,13]);
  add('box','#34495c',[0,2,-1.3],[20,4,.3]);add('box','#0c192f',[0,2.2,-1.10],[4.8,2.2,.12]);
  const earth=add('sphere','#478caa',[.4,2.2,-.9],[.75,.75,.12],scene,true);add('sphere','#73b594',[.2,2.4,-.75],[.38,.24,.06],scene,true);
  for(const x of [-3,3]){add('box','#bed5cf',[x,1.4,-.65],[.1,2.8,.1]);add('box','#c2b284',[x,.8,-.5],[.14,.09,2.6]);}
  add('box','#8bbaa2',[3,.8,1],[2,.12,1.1]);
 }
 if(location==='space'){
  scene.background=new H.Color('#08172d');scene.fog=new H.Fog('#08172d',35,70);
  add('box','#0a1b30',[0,-.01,2],[45,.08,20]);add('box','#09172b',[0,3,-1],[40,6,.15]);
  for(let i=0;i<65;i++){const xx=Math.sin(i*8.13)*16,yy=.9+(Math.sin(i*3.2)+1)*2;add('sphere',i%3?'#d5dddc':'#80a6c6',[xx,yy,-.75],[.025,.025,.025],scene,true);}
  const planet=add('sphere','#588d9c',[3,2,-.4],[1.0,1.0,.3],scene,true);P.planet=planet;const sunDisk=add('sphere','#e5b570',[2.7,2,-.2],[.7,.7,.3],scene,true);P.sunDisk=sunDisk;
 }
 if(location==='diagram'){
  scene.background=new H.Color('#102c45');add('box','#102c45',[0,2,1],[32,5,.1],scene,true);diagram.position.set(0,0,2);diagram.visible=true;
 }
const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMappingExposure=.95;const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){}};
 const result={stage,nico,photo,box,lid,H,A,P,location};cache.set(location,result);return result;
}
