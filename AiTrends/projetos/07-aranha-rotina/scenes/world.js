import {library,actor} from './rig.js';
let cache;
export function world(T){
 if(cache)return cache;const H=T.THREE,L=library(T),scene=new H.Scene(),camera=new H.PerspectiveCamera(43,16/9,.025,80);scene.background=new H.Color('#101b2b');scene.fog=new H.Fog('#101b2b',20,50);
 scene.add(new H.HemisphereLight('#9cc9df','#253144',1.45));const sun=new H.DirectionalLight('#b5deff',1.9);sun.position.set(-5,7,4);scene.add(sun);const warm=new H.PointLight('#ffbf72',12,12,2);warm.position.set(3.9,2.4,-1.8);scene.add(warm);
 const P={},add=(shape,c,pos,scale,parent=scene,basic=false)=>{const m=L.mesh(shape,c,pos,scale,basic);parent.add(m);return m;},group=id=>{const g=new H.Group();P[id]=g;scene.add(g);return g;};
 const box=(c,p,s,parent)=>add('box',c,p,s,parent);
 function line(parent,c,a,b,r=.012){const v=L.bone(parent,c,r);v.set(a,b);return v;}
 function label(words,pos,w,h,parent=scene,bg='#224652'){const tex=T.canvasTex(720,180,(g,W,Q)=>{g.fillStyle=bg;g.fillRect(0,0,W,Q);g.fillStyle='#fff1d0';g.font='900 64px Nunito';g.textAlign='center';g.textBaseline='middle';g.fillText(words,W/2,Q/2,W-35);});const m=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tex,side:H.DoubleSide}));m.position.set(...pos);parent.add(m);return m;}
 box('#394450',[0,-.13,0],[17,.26,12]);for(let i=0;i<13;i++)box(i%2?'#827666':'#8d7e69',[-7.5+i*1.22,.005,0],[1.20,.025,11]);
 box('#3d5367',[0,2,-3.6],[17,4,.18]);box('#5c7281',[-8.2,2,0],[.16,4,7.3]);box('#293e52',[8.2,2,0],[.16,4,7.3]);box('#bba98c',[0,.12,-3.47],[16.5,.24,.10]);
 // Bedroom left, corridor centre and living room right remain in one space.
 box('#243c53',[-5.7,2.3,-3.46],[3.2,2.25,.06]);box('#5f9ac2',[-5.7,2.3,-3.40],[2.9,2.02,.05]);for(const x of [-7.3,-5.7,-4.1])box('#d3c7a8',[x,2.3,-3.3],[.10,2.35,.16]);box('#d3c7a8',[-5.7,2.3,-3.29],[3.3,.08,.16]);box('#bca98c',[-5.7,1.16,-3.08],[3.6,.12,.65]);add('sphere','#d8eaff',[-6.5,2.9,-3.25],[.24,.24,.03],scene,true);
 for(const x of [-7.5,-3.8]){box('#556275',[x,2.25,-3.12],[.44,2.65,.16]);for(let i=0;i<3;i++)box('#627285',[x-.13+i*.13,2.25,-3.01],[.055,2.6,.06]);}
 const bed=group('bed');box('#7e6c56',[0,.33,0],[2.3,.46,1.7],bed);box('#e4d5b4',[0,.67,0],[2.23,.25,1.64],bed);box('#426d80',[.3,.82,0],[1.55,.12,1.66],bed);box('#eadfc8',[-.75,.88,0],[.55,.16,1.20],bed);box('#8a7864',[-1.15,.65,0],[.12,1.3,1.8],bed);bed.position.set(-5.8,0,-.7);
 const door=group('door');box('#273e4b',[0,1.5,0],[1.65,3,.12],door);box('#a28e70',[0,1.5,.09],[1.42,2.85,.09],door);add('sphere','#e0bc73',[.5,1.4,.19],[.065,.065,.055],door);door.position.set(-2.7,0,-3.30);
 box('#435f69',[-.8,.035,-.8],[2.3,.03,3.6]);for(const z of [-2.45,.85])box('#98a59c',[-.8,.056,z],[2.1,.02,.08]);
 // Kitchen in rear right corner, with kettle and broad stable tile shapes.
 box('#365b65',[6.0,.55,-2.8],[3.8,1.1,1]);box('#d5c5a1',[6.0,1.16,-2.8],[4.0,.16,1.12]);for(const x of [4.7,6.0,7.3]){box('#416d73',[x,.6,-2.24],[1.15,.9,.06]);box('#c5b28e',[x,.9,-2.17],[.30,.05,.05]);}
 const kettle=group('kettle');add('sphere','#8ab1b8',[0,0,0],[.2,.26,.2],kettle);add('limb','#263d50',[0,.24,0],[.15,.06,.15],kettle);line(kettle,'#b8d0c7',[.12,.08,0],[.32,.22,0],.05);line(kettle,'#243b47',[-.1,.18,-.2],[.1,.18,-.2],.025);kettle.position.set(5.6,1.48,-2.7);
 const sofa=group('sofa');box('#5e486e',[0,.35,0],[3,.6,1.1],sofa);box('#80628d',[0,.72,-.43],[3,1.05,.22],sofa);for(const x of [-1.4,1.4])box('#8a6b96',[x,.72,0],[.25,.68,1.15],sofa);for(const x of [-.7,.3])box('#96779e',[x,.69,.0],[.85,.16,.82],sofa);sofa.position.set(3.6,0,-.1);
 const cushion=group('cushion');box('#b8a17b',[0,0,0],[.65,.16,.55],cushion);cushion.position.set(4.5,.85,-.1);
 const table=group('table');box('#ad8a60',[0,.77,0],[2.0,.12,1.1],table);for(const x of [-.82,.82])for(const z of [-.4,.4])box('#6d604c',[x,.37,z],[.10,.74,.10],table);table.position.set(2.4,0,2.0);
 const chair=group('chair');box('#b69362',[0,.58,0],[.65,.12,.65],chair);for(const x of [-.25,.25])for(const z of [-.25,.25])box('#655e50',[x,.27,z],[.08,.54,.08],chair);box('#ad885b',[0,1.0,-.29],[.65,.75,.10],chair);chair.position.set(5.4,0,1.0);
 const lamp=group('lamp');add('limb','#baab8c',[0,.05,0],[.25,.1,.25],lamp);add('limb','#b99b69',[0,.64,0],[.025,1.2,.025],lamp);add('limb','#ffd195',[0,1.32,0],[.30,.38,.30],lamp);lamp.position.set(6.4,0,.6);const bulb=add('sphere','#fff0ba',[0,1.32,.27],[.09,.10,.04],lamp,true);P.bulb=bulb;
 const lampLight=new H.PointLight('#ffcc7c',7,8,2);lampLight.position.set(6.4,1.4,1.1);scene.add(lampLight);
 const switchObj=group('switch');box('#a18f70',[0,0,0],[.25,.10,.22],switchObj);box('#eee1bb',[0,.07,0],[.13,.06,.14],switchObj);switchObj.position.set(6.15,.83,.8);const switchTable=box('#896d52',[6.3,.74,.65],[1.1,.1,.8]);box('#62584c',[6.3,.35,.65],[.1,.7,.1]);
 const cable=group('cable');line(cable,'#1a2739',[6.4,.08,.6],[5.4,.06,1.0],.025);line(cable,'#1a2739',[5.4,.06,1.0],[5.1,.06,-2.0],.025);box('#e2d4b7',[5.1,.2,-3.31],[.25,.32,.05]);const plug=group('plug');box('#d5c9ac',[0,0,0],[.15,.1,.16],plug);plug.position.set(5.1,.08,-2.0);
 const plant=group('plant');add('limb','#ad785c',[0,0,0],[.25,.37,.25],plant);for(let i=0;i<5;i++){const a=i*1.25;line(plant,'#699b7d',[0,.12,0],[.3*Math.sin(a),.55,.2*Math.cos(a)],.018);add('sphere','#84b48c',[.3*Math.sin(a),.5,.2*Math.cos(a)],[.22,.06,.12],plant);}plant.position.set(-4.6,1.4,-3.0);
 const cup=group('cup');const cupMat=new H.MeshBasicMaterial({color:'#b0edf0',transparent:true,opacity:.13,depthWrite:false,side:H.DoubleSide});const cm=new H.Mesh(new H.CylinderGeometry(.15,.12,.30,12,1,true),cupMat);cm.position.y=.15;cup.add(cm);for(const [y,r]of [[.30,.15],[.015,.12]]){const rim=new H.Mesh(new H.TorusGeometry(r,.009,6,24),L.mat('#bee9e2',true));rim.rotation.x=Math.PI/2;rim.position.y=y;cup.add(rim);}add('box','#ceeae2',[.10,.15,.08],[.012,.22,.012],cup,true);add('limb','#c8f1e8',[0,.012,0],[.13,.018,.13],cup);cup.position.set(2.0,.85,2);
 const card=group('card');box('#eddab1',[0,0,0],[.52,.025,.35],card);card.position.set(2.5,.85,2);
 const notebook=group('notebook');box('#c4b192',[0,0,0],[.8,.06,.6],notebook);box('#eee0b8',[0,.035,0],[.75,.015,.56],notebook);notebook.position.set(2.6,.86,1.8);
 const map=group('map');box('#eedeb6',[0,0,0],[1.5,.03,1.1],map);for(const x of [-.38,.24])box('#426d76',[x,.025,0],[.025,.015,.9],map);for(const z of [-.28,.2])box('#426d76',[0,.025,z],[1.3,.015,.025],map);for(const p of [[-.55,-.3],[0,.3],[.5,-.2]])add('sphere','#d77d69',[p[0],.055,p[1]],[.055,.025,.055],map);map.position.set(2.2,.86,2);
 const cards=[];for(let i=0;i<3;i++){const c=group('card'+i);box(['#75b2ac','#dcba74','#b28fc5'][i],[0,0,0],[.50,.035,.38],c);label(['PASSO','LUZ','SOFÁ'][i],[0,.025,.20],.46,.13,c);cards.push(c);}P.cards=cards;
 const remote=group('remote');box('#25364b',[0,0,0],[.13,.04,.30],remote);for(let i=0;i<3;i++)add('sphere',i?'#8ba6a8':'#ef977c',[0,.032,-.09+i*.08],[.025,.014,.025],remote);remote.position.set(4.95,1.08,0);
 const torch=group('torch');add('limb','#b4c5bd',[0,0,0],[.06,.28,.06],torch);add('sphere','#fff2ba',[0,.16,0],[.075,.025,.075],torch,true);torch.rotation.z=-Math.PI/2;torch.position.set(1,1,1);
 const phone=group('phone');box('#15293d',[0,0,0],[.36,.62,.045],phone);box('#5e97aa',[0,0,.027],[.30,.53,.012],phone);add('sphere','#b3d3d4',[0,.23,.04],[.025,.025,.01],phone);phone.position.set(2.8,1.13,2.0);
 const books=group('books');for(let i=0;i<3;i++)box(['#4d8b8e','#b78b68','#9a87b3'][i],[0,.05+i*.08,0],[.68,.075,.55],books);books.position.set(2.8,.85,2);
 const sock=group('sock');box('#d5bf8e',[0,0,0],[.25,.05,.35],sock);sock.position.set(3.2,.05,1.1);
 const wire=group('wire');const thread=L.bone(wire,'#c7ddd2',.014);thread.set([0,0,0],[1,0,0]);P.thread=thread;
 const shadow=group('bigShadow');add('sphere','#152032',[0,0,0],[.5,.3,.02],shadow,true);for(let i=0;i<8;i++){const a=Math.PI*2*i/8;line(shadow,'#152032',[.25*Math.cos(a),.2*Math.sin(a),0],[.95*Math.cos(a),.65*Math.sin(a),0],.035);}shadow.position.set(4.4,2.7,-3.35);
 // Eight supported legs, fixed segment lengths, deterministic crawl (not a flapping sprite).
 const spider=group('spider');spider.scale.setScalar(.45);add('sphere','#263446',[0,.105,0],[.14,.10,.11],spider);add('sphere','#455c6c',[.16,.10,0],[.085,.065,.075],spider);for(const z of [-.03,.03])add('sphere','#f7d69b',[.23,.12,z],[.015,.018,.014],spider,true);const legs=[];
 for(let i=0;i<8;i++){legs.push({upper:L.bone(spider,'#263c4b',.016),lower:L.bone(spider,'#304a59',.012),side:i<4?1:-1,index:i%4});}
 function crawl(distance){for(let i=0;i<8;i++){const leg=legs[i],z=leg.side*.08,x=(leg.index-1.5)*.07,phase=(distance/.18+(i%2)*.5)%1,stance=.65,advance=phase<stance?.09-.18*phase/stance:-.09+.18*(phase-stance)/(1-stance),lift=phase<stance?0:.06*Math.sin(Math.PI*(phase-stance)/(1-stance));const a=new H.Vector3(x,.10,z),end=new H.Vector3(x+advance,.014+lift,leg.side*(.24+leg.index*.025)),delta=end.clone().sub(a),len=delta.length(),mid=a.clone().add(end).multiplyScalar(.5),h=Math.sqrt(Math.max(0,.20**2-(len/2)**2));const axis=delta.clone().normalize(),pole=new H.Vector3(0,1,0),bend=pole.sub(axis.clone().multiplyScalar(pole.dot(axis))).normalize();mid.add(bend.multiplyScalar(h));leg.upper.set(a.toArray(),mid.toArray());leg.lower.set(mid.toArray(),end.toArray());}}
 crawl(0);
 const A={nico:actor(T,'nico'),lia:actor(T,'lia')};for(const a of Object.values(A))scene.add(a.root);
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;renderer.toneMappingExposure=.98;const stage={scene,camera,render(){renderer.render(scene,camera);},dispose(){}};cache={H,L,stage,scene,camera,P,A,add,line,crawl,lampLight,warm};return cache;
}
