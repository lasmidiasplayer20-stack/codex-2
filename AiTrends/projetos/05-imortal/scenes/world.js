// Original procedural workshop for the opening pilot. No reference frames imported.
import {actor,library} from './rig.js';
let cached;
export function world(T){
 if(cached)return cached;const H=T.THREE,L=library(T),scene=new H.Scene();scene.background=new H.Color('#b4c8cb');scene.fog=new H.Fog('#b4c8cb',28,55);
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
 const nico=actor(T,'nico');scene.add(nico.root);const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMappingExposure=.95;const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){}};
 return cached={stage,nico,photo,box,lid,H};
}
