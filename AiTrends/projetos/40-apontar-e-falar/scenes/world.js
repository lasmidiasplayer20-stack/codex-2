// Six original educational sets. All geometry, surfaces, rigs and motion are code-generated.
import {library,actor} from './rig.js';
const C=x=>Math.max(0,Math.min(1,x)),E=x=>{x=C(x);return x*x*(3-2*x);},mix=(a,b,p)=>a+(b-a)*p;
export function createFactScene(H,theme){
 const L=library({THREE:H}),root=new H.Group(),sets={},props={},actors={nico:actor({THREE:H},'nico'),lia:actor({THREE:H},'lia')};
 const box=(parent,c,p,s,b=false)=>{const m=L.mesh('box',c,p,s,b);parent.add(m);return m;};
 const ball=(parent,c,p,s,b=false)=>{const m=L.mesh('sphere',c,p,Array.isArray(s)?s:[s,s,s],b);parent.add(m);return m;};
 const cylinder=(parent,c,p,r,h)=>{const m=L.mesh('limb',c,p,[r,h,r]);parent.add(m);return m;};
 const group=(parent,p=[0,0,0])=>{const q=new H.Group();q.position.set(...p);parent.add(q);return q;};
 function panel(parent,w,h,p,lines,colors=[],base='#122b45'){const cv=document.createElement('canvas');cv.width=1024;cv.height=Math.round(1024*h/w);const cx=cv.getContext('2d');cx.fillStyle=base;cx.fillRect(0,0,1024,cv.height);cx.strokeStyle=colors[0]||'#f9d68d';cx.lineWidth=14;cx.strokeRect(8,8,1008,cv.height-16);cx.textAlign='center';cx.textBaseline='middle';lines.forEach((v,i)=>{cx.font=`900 ${Math.min(190,cv.height/lines.length*.62)}px sans-serif`;cx.fillStyle=colors[i]||'#fff0d0';cx.fillText(v,512,cv.height*(i+.5)/lines.length,970);});const tx=new H.CanvasTexture(cv);tx.colorSpace=H.SRGBColorSpace;const mesh=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tx}));mesh.position.set(...p);parent.add(mesh);return mesh;}
 function tree(parent,x,z,scale=1){const q=group(parent,[x,0,z]);q.scale.setScalar(scale);cylinder(q,'#a77c63',[0,.85,0],.11,1.7);for(let i=0;i<3;i++)ball(q,['#70bd87','#83cf94','#65a781'][i],[Math.sin(i*2)*.2,1.8+i*.20,Math.cos(i*2)*.2],[.50,.60,.5]);return q;}
 function ground(c='#c9b18e',w=24,d=16){box(root,c,[0,-.12,0],[w,.24,d]);}
 function line(parent,c,a,b,r=.02){const q=L.bone(parent,c,r);q.set(a,b);return q.mesh;}
 function arrow(parent,c,a,b){const q=group(parent),start=new H.Vector3(...a),end=new H.Vector3(...b),dir=end.clone().sub(start);line(q,c,a,b,.025);const tip=new H.Mesh(new H.ConeGeometry(.095,.22,8),L.mat(c,true));tip.position.copy(end);tip.quaternion.setFromUnitVectors(new H.Vector3(0,1,0),dir.normalize());q.add(tip);return q;}
 const hemi=new H.HemisphereLight('#e8faff','#89718c',1.75);root.add(hemi);const sun=new H.DirectionalLight('#ffe7c2',2.1);sun.position.set(4,8,6);root.add(sun);for(const a of Object.values(actors))root.add(a.root);
 if(theme===39){
  ground('#698e9d');box(root,'#d8d0b0',[0,.02,0],[5.2,.06,3.5]);const building=group(root);for(const x of [-2,2])for(const z of [-1.25,1.25])box(building,'#eed8ad',[x,1.35,z],[.27,2.7,.27]);box(building,'#e5c09d',[0,2.79,0],[5.2,.18,3.5]);
  for(let floor=0;floor<3;floor++){const y=3.55+floor*1.35;box(building,['#e39593','#a997d1','#7fc2c7'][floor],[0,y,-.18],[5.0,1.30,3.0]);for(let j=0;j<4;j++){const x=-1.8+j*1.2;box(building,'#2c6380',[x,y,.1+1.23],[.65,.78,.06]);box(building,'#b1e4e9',[x,y,1.38],[.49,.61,.025]);box(building,'#f5e7bd',[x,y,1.40],[.04,.66,.015]);}}
  box(building,'#ffdda2',[0,7.03,-.18],[5.3,.18,3.4]);panel(root,2.6,.42,[0,2.47,1.48],['TÉRREO ABERTO'],['#fff0b9']);
  const bench=group(root,[.6,0,-.65]);for(const x of [-.65,.65])box(bench,'#405976',[x,.26,0],[.09,.52,.38]);box(bench,'#c49369',[0,.55,0],[1.75,.12,.52]);box(bench,'#d5a778',[0,.94,-.24],[1.75,.60,.08]);for(const x of [-4.8,4.8])tree(root,x,-1.7,1.2);
  const shaft=group(root),umbrella=group(shaft,[0,.85,0]);cylinder(shaft,'#45617c',[0,.48,0],.018,.98);const canopy=new H.Mesh(new H.SphereGeometry(.62,24,8,0,Math.PI*2,0,Math.PI/2),L.mat('#db748e'));canopy.scale.y=.42;umbrella.add(canopy);for(let i=0;i<8;i++){const a=i*Math.PI/4;line(umbrella,'#4e3858',[0,.25,0],[.61*Math.cos(a),0,.61*Math.sin(a)],.008);}
  const rain=new H.InstancedMesh(new H.CylinderGeometry(.007,.007,.16,4),L.mat('#a9d9e9',true),160);root.add(rain);const air=[];for(let i=0;i<4;i++)air.push(arrow(root,'#70dbe0',[-2.7,.65+i*.35,-.25],[2.7,.65+i*.35,-.25]));
  Object.assign(props,{building,bench,shaft,umbrella,canopy,rain,air});
 }
 if(theme===40){
  ground('#b8bac0');box(root,'#e9d6ad',[0,-.015,.4],[16,.10,3]);box(root,'#536777',[0,-.06,-2.1],[22,.12,2.0]);for(const z of [-2.6,-1.6])box(root,'#a6c0cb',[0,.06,z],[22,.08,.055]);for(let i=-10;i<=10;i++)box(root,'#8b7564',[i*.65,.035,-2.1],[.15,.07,1.3]);box(root,'#f6db71',[0,.045,-.92],[16,.02,.12]);for(const x of [-5,5]){box(root,'#718ba6',[x,1.85,-.4],[.12,3.7,.12]);box(root,'#b6d8e4',[x,3.65,0],[2,.16,4.0]);}panel(root,2.5,.50,[0,3.08,-1.0],['CONFERÊNCIA'],['#ffdc8c']);
  const signal=group(root,[1.25,0,-.18]);box(signal,'#40546e',[0,.8,0],[.10,1.6,.10]);box(signal,'#172d42',[0,1.85,0],[.48,.62,.15]);const lamp=ball(signal,'#ed8b7f',[0,1.85,.1],[.15,.15,.025],true);panel(signal,.68,.23,[0,2.30,.08],['SINAL'],['#c6f4e7']);
  const plate=group(root,[.13,1.08,.10]);box(plate,'#627fa0',[0,0,0],[.28,.12,.32]);panel(plate,.24,.16,[0,.12,.05],['OK'],['#e5f3b9']);
  const train=group(root,[-6,0,-2.1]);for(let i=0;i<2;i++){const x=i*3.5;box(train,'#ecdfca',[x,.83,0],[3.3,1.40,.98]);box(train,'#43a2ac',[x,.48,.51],[3.25,.12,.02]);for(let j=0;j<4;j++)box(train,'#4a7e9e',[x-1.12+j*.72,1.1,.51],[.52,.52,.025]);for(const dx of [-1.1,1.1])for(const z of [-.48,.48])cylinder(train,'#30415b',[x+dx,.19,z],.16,.12).rotation.x=Math.PI/2;}
  const pointer=L.bone(root,'#111625',.023);box(root,'#87bdc6',[0,3.42,-.40],[12,.16,2.2]);box(root,'#a39bc5',[0,1.8,-5.0],[18,3.6,.16]);for(let i=-5;i<=5;i++)box(root,'#c0e7e8',[i*1.4,2.1,-4.88],[.65,.86,.035]);
  const checks=[];for(let i=0;i<3;i++)checks.push(panel(root,.86,.30,[-1.2+i*1.2,2.55,-.35],[['OLHAR','APONTAR','CONFIRMAR'][i]],['#a0f0d8']));Object.assign(props,{signal,lamp,train,plate,checks,pointer});
 }
 if(theme===41){
  ground('#5e4b79');box(root,'#78649b',[0,1.8,-2.4],[9,3.6,.15]);for(const x of [-3,3]){box(root,'#be8d74',[x,1.75,-2.25],[.12,3.5,.12]);ball(root,'#ffe3a0',[x,2.8,-2.0],.18,true);}const table=group(root,[0,0,-.4]);box(table,'#95694e',[0,.55,0],[2.9,1.1,.40]);box(table,'#4c9b8d',[0,1.10,0],[3.1,.10,.50]);box(table,'#e8c783',[0,1.15,.25],[3.15,.055,.06]);panel(root,2.5,.45,[0,2.9,-2.25],['FICHAS: VALORES E REGRAS'],['#ffe291']);
  const chips=[];const colors=['#e17b8c','#65bcb3','#799bd0'];for(let i=0;i<24;i++){const q=group(root);cylinder(q,colors[Math.floor(i/8)],[0,0,0],.10,.029);for(let j=0;j<4;j++){const a=j*Math.PI/2;box(q,'#fff1d0',[.095*Math.sin(a),.001,.095*Math.cos(a)],[.025,.033,.025],true);}chips.push(q);}
  const money=group(root);for(let i=0;i<3;i++){box(money,'#b8d69e',[0,i*.012,0],[.26,.012,.13]);box(money,'#e6efc7',[0,i*.012+.007,0],[.04,.003,.13],true);}const macro=group(root);const disc=cylinder(macro,'#d979a4',[0,0,0],.50,.09);const seal=panel(macro,.44,.20,[0,.052,.01],['EXEMPLO'],['#fff1cc']);seal.rotation.x=-Math.PI/2;for(let i=0;i<8;i++){const a=i*Math.PI/4;box(macro,'#f9e6b1',[.46*Math.sin(a),.001,.46*Math.cos(a)],[.08,.095,.055],true);}const security=panel(macro,.35,.17,[0,.053,-.20],['SEGURANÇA'],['#7df2e2']);security.rotation.x=-Math.PI/2;
  const labels=[];for(let i=0;i<3;i++)labels.push(panel(root,.75,.25,[-.9+i*.9,1.50,-1.0],['EXEMPLO '+[1,5,25][i]],['#ffdfb4']));Object.assign(props,{chips,money,macro,labels});
 }
 if(theme===42){
  ground('#99bea0',36,20);box(root,'#718b9a',[0,-.025,1.8],[32,.08,4.3]);for(let i=-8;i<=8;i++)box(root,'#eadca9',[i*2,.023,3.4],[1.0,.014,.10]);for(const x of [-7,7])tree(root,x,-4,1.4);
  const load=group(root,[0,.715,-1.4]);box(load,'#7a8e91',[0,.06,0],[4.1,.12,2.8]);box(load,'#eaa992',[0,1.50,0],[3.9,2.85,2.6]);for(const x of [-1.05,1.05]){box(load,'#6e9eb1',[x,1.8,1.32],[.70,.88,.045]);box(load,'#eff0d6',[x,1.8,1.35],[.055,.88,.025]);}box(load,'#697f91',[0,.95,1.32],[.6,1.82,.07]);const roof=box(load,'#9b6275',[0,3.02,0],[4.3,.20,3.05]);for(const x of [-1.4,1.4])box(load,'#425c75',[x,-.07,0],[.18,.15,3.5]);
  const jacks=[];for(const x of [-1.4,1.4])for(const z of [-3.05,.25]){const q=group(root,[x,0,z]);cylinder(q,'#d6ad55',[0,.15,0],.16,.30);const piston=cylinder(q,'#c6d8df',[0,.38,0],.075,.3);const cap=box(q,'#52677b',[0,.54,0],[.36,.10,.36]);jacks.push({q,piston,cap});}
  const cart=group(root,[0,0,-1.4]);for(const x of [-1.8,1.8])box(cart,'#405a74',[x,.47,0],[.20,.18,3.1]);for(const z of [-.9,.9])box(cart,'#405a74',[0,.47,z],[3.6,.18,.20]);const wheels=[];for(const x of [-1.65,1.65])for(const z of [-1.26,1.26]){const q=group(cart,[x,.26,z]);const tire=cylinder(q,'#203149',[0,0,0],.22,.16);tire.rotation.x=Math.PI/2;wheels.push(q);}
  const wire=line(root,'#3c5c75',[-6,5.2,-1.5],[7,5.2,-1.5],.018);for(const x of [-6,7])box(root,'#7d8278',[x,2.65,-1.5],[.13,5.3,.13]);panel(root,2.4,.40,[-3.2,2.6,-2.8],['ROTA PLANEJADA'],['#ffe1a3']);const clipboard=group(root);box(clipboard,'#b38c5e',[0,0,0],[.29,.40,.035]);panel(clipboard,.24,.32,[0,0,.025],['ESTRUTURA','ROTA','APOIOS'],['#17334a','#17334a','#17334a'],'#f3e6c5');Object.assign(props,{load,jacks,cart,wheels,wire,clipboard});
 }
 if(theme===43){
  for(const x of [-6.05,6.05])box(root,'#a5c0bc',[x,-.12,0],[5.9,.24,12]);box(root,'#a5c0bc',[0,-.12,4],[6.2,.24,4.8]);box(root,'#a5c0bc',[0,-.12,-3.6],[6.2,.24,4.8]);const mechanism=group(root,[0,0,-.5]);box(mechanism,'#7d96ac',[0,3,-.8],[5.8,8.8,.12]);for(const x of [-2.2,2.2])box(mechanism,'#475e79',[x,3.5,0],[.10,10.1,.12]);box(mechanism,'#475e79',[0,3.525,0],[.10,5.45,.12]);for(const y of [0,2.4,4.8]){box(mechanism,'#d9bd95',[0,y-.08,1.33],[6,.16,1.13]);for(const x of [-3,3])box(mechanism,'#718993',[x,y+.6,1.85],[.08,1.2,.08]);}for(const y of [-1.55,8.6])box(mechanism,'#4b6380',[0,y,0],[5.5,.15,1.2]);
  const path=[];for(const x of [-1.35,1.35])line(mechanism,'#d2af6e',[x,.8,-.47],[x,6.25,-.47],.035);for(const cy of [.8,6.25]){const arc=new H.Mesh(new H.TorusGeometry(1.35,.035,6,40,Math.PI),L.mat('#d2af6e'));arc.position.set(0,cy,-.47);if(cy===.8)arc.rotation.z=Math.PI;mechanism.add(arc);}
  const cabins=[];for(let i=0;i<8;i++){const q=group(mechanism);const c=['#ba7cae','#66aaa9','#d0a36d','#819cc8'][i%4];box(q,c,[0,0,-.25],[.89,1.45,.11]);box(q,c,[0,-.70,0],[.95,.10,.82]);for(const x of [-.44,.44])box(q,c,[x,0,0],[.07,1.45,.82]);box(q,'#f8dfb0',[0,.66,0],[.95,.10,.82]);cabins.push(q);}
  panel(root,3,.48,[0,8.05,-.20],['CORTE ESQUEMÁTICO'],['#fff0b7']);panel(root,2.7,.38,[0,-1.9,.20],['CABINES SEMPRE VERTICAIS'],['#a6e9dc']);const arrows=[arrow(root,'#efcf73',[-2.7,1.2,.2],[-2.7,3.0,.2]),arrow(root,'#78dddc',[2.7,3.0,.2],[2.7,1.2,.2])];Object.assign(props,{mechanism,cabins,arrows});
 }
 if(theme===44){
  ground('#cdb79b');box(root,'#8ba4ad',[0,-.025,2.7],[24,.08,2.0]);for(let i=-2;i<=2;i++){const x=i*3.15,c=['#a6b8bd','#d5a189','#be8994','#b1a2c5','#8fb4ad'][i+2];box(root,c,[x,2.35,-.50],[3.05,4.7,.28]);box(root,'#efdec1',[x,4.76,-.50],[3.15,.16,.44]);for(const dx of [-.76,.76]){box(root,'#557486',[x+dx,3.55,-.34],[.55,.90,.035]);box(root,'#e4dbc0',[x+dx,3.55,-.30],[.045,.90,.02]);}}
  const frame=group(root,[0,1.55,-.30]);for(const x of [-.65,.65])box(frame,'#f2d7a8',[x,0,0],[.10,1.6,.15]);for(const y of [-.8,.8])box(frame,'#f2d7a8',[0,y,0],[1.4,.10,.15]);const glass=box(frame,'#527788',[0,0,-.025],[1.17,1.47,.045]);box(frame,'#e8e2c1',[0,0,.015],[.045,1.45,.025]);const bricks=[];for(let row=0;row<8;row++)for(let col=0;col<4;col++){const x=-.43+col*.29+(row%2)*.035;const b=box(frame,['#b97c69','#c68c75','#ac7163'][(row+col)%3],[x,-.66+row*.185,.075],[.265,.16,.075]);bricks.push({b,row,col,x,y:-.66+row*.185});}
  // Two other examples demonstrate that not every blind window has the same cause.
  const altered=group(root,[-3.15,1.55,-.30]);box(altered,'#a4b5bb',[0,0,0],[1.2,1.5,.09]);for(const x of [-.66,.66])box(altered,'#edcfaa',[x,0,.04],[.1,1.65,.1]);for(const y of [-.8,.8])box(altered,'#edcfaa',[0,y,.04],[1.4,.1,.1]);panel(root,1.50,.30,[-3.15,2.65,-.22],['ALTERAÇÃO DE USO'],['#fff0c5']);
  const painted=group(root,[3.15,1.55,-.29]);box(painted,'#5f7c8b',[0,0,0],[1.2,1.5,.012],true);for(const x of [-.66,0,.66])box(painted,'#f0dbb8',[x,0,.015],[.055,1.6,.012],true);for(const y of [-.8,0,.8])box(painted,'#f0dbb8',[0,y,.015],[1.4,.055,.012],true);panel(root,1.50,.30,[3.15,2.65,-.22],['SIMETRIA'],['#fff0c5']);
  const ledger=group(root);box(ledger,'#68577e',[0,0,0],[.45,.40,.04]);panel(ledger,.40,.34,[0,0,.026],['JANELAS','IMPOSTO'],['#21394f','#21394f'],'#f5dfaf');const date=panel(root,2,.40,[0,2.85,-.28],['1696 → 1851'],['#ffe19c']);tree(root,-7,-1.2);tree(root,7,-1.2);Object.assign(props,{frame,glass,bricks,ledger,date,painted,altered});
 }
 return {H,L,root,theme,actors,props,hemi,sun,background:'#9acfe0'};
}
export function updateFactScene(s,camera,time,shots,cover=false){
 const H=s.H,g=time,sh=shots.find(x=>g>=x.start&&g<x.end)||shots.at(-1),act=sh.params.act,view=sh.params.view,u=C((g-sh.start)/(sh.end-sh.start)),v=E(u),theme=s.theme,p=s.props;
 const interval=i=>{const a=shots.filter(x=>x.params.act===i);return [a[0].start,a.at(-1).end];},A=i=>{const[a,b]=interval(i);return C((g-a)/(b-a));},G=(i,q)=>{const[a,b]=interval(i);return a+(b-a)*q;};
 const n={time:g,x:0,y:.02,z:.6,yaw:-Math.PI/2,headYaw:0,moving:false,expr:'smile'},l={...n,time:g+.8,x:1.0};let showL=true,pos=[3,2.6,6.5],target=[0,1.15,0],fov=43,holding=null;
 if(theme===39){
  const walk=E(C((g-G(0,.6))/(G(1,.75)-G(0,.6))));n.x=mix(-3.7,-.65,walk);n.z=.68;n.yaw=walk>.98?-Math.PI/2:0;n.headYaw=walk>.98?.04:-.7;n.moving=walk>.001&&walk<.999;n.distance=3.05*walk;n.hand=[.20,1.24,.18];l.x=.65;l.z=-.43;l.y=.02;l.yaw=-Math.PI/2;l.sit=true;l.expr='joy';
  const fold=E(C((g-G(2,.0))/1.2));p.umbrella.scale.set(mix(1,.20,fold),mix(1,2.4,fold),mix(1,.20,fold));p.shaft.visible=true;holding='umbrella';
  const dummy=new H.Object3D();for(let i=0;i<160;i++){const x=((i*73%199)/199-.5)*15,z=((i*37%173)/173-.5)*9,y=8-((g*4.2+i*.37)%8);const under=Math.abs(x)<2.65&&Math.abs(z)<1.78&&y<7.2;dummy.position.set(x,under?-5:y,z);dummy.rotation.z=-.06;dummy.scale.setScalar(1);dummy.updateMatrix();p.rain.setMatrixAt(i,dummy.matrix);}p.rain.instanceMatrix.needsUpdate=true;
  p.air.forEach((q,i)=>{q.visible=act===3;q.position.x=.11*Math.sin(g*1.2+i);});
  if(act===0){pos=view===0?[6.8-v*.5,5.3,12.2]:[4.5,3.1,8.0];target=[-.3,view===0?3.2:1.6,0];}
  if(act===1){pos=view===0?[4.2,3.1,7.4]:[2.2,1.85,5.9];target=[-.2,1.55,0];}
  if(act===2){pos=view===0?[n.x+2.4,2.2,5.1]:[1.9,1.8,3.7];target=[-.05,1.1,.10];}
  if(act===3){pos=view===0?[4.4,2.8,6.5]:[4.7,1.7,4.5];target=[0,1.2,0];}
  if(act===4){pos=view===0?[6.8,5.5,10]:[3.0,2.5,5.8];target=[0,view===0?3.2:1.3,0];}
  if(act===5){n.hand=undefined;n.gesture='point';n.gestureWeight=.35;p.shaft.visible=false;pos=view===0?[2.4,2.45,6]:[1.0,2.15,4.5];target=[0,1.2,0];}
 }
 if(theme===40){
  n.x=-.55;n.z=.38;n.yaw=0;n.headYaw=-.52;n.expr='determined';l.x=2.35;l.z=.70;l.yaw=Math.PI;l.headYaw=.65;l.expr='smile';
  const point=act===0?E(A(0)/.35)*(1-.7*E((A(0)-.7)/.3)):act===1?.3*(1-E(A(1))):act===2?E((A(2)-.2)/.25)*(1-.5*E((A(2)-.8)/.2)):act===3?.5*(1-E(A(3)/.5)):0;n.gesture='point';n.gestureWeight=point*.92;n.hand=[mix(.045,.50,point),mix(.875,1.60,point),.19];n.nod=.035*Math.sin(g*1.4);p.checks.forEach((q,i)=>q.visible=act>=1&&act<=3&&A(2)>(i*.2));p.lamp.material=s.L.mat(g>G(4,.5)?'#82d8bd':'#edba77',true);
  if(act===0){pos=view===0?[3.4-v*.3,2.5,5.5]:[2.4,1.9,3.8];target=[-.15,1.4,.3];}
  if(act===1){pos=view===0?[2.6,2.6,4.9]:[-.9,2.25,3.7];target=[.2,1.55,.1];}
  if(act===2){pos=view===0?[.5,2.25,3.5]:[2.6,2.3,3.5];target=view===0?[.9,1.8,-.12]:[-.3,1.55,.3];}
  if(act===3){pos=view===0?[1.5,2.7,5.0]:[2.7,2.0,4.1];target=[.0,1.45,.1];}
  if(act===4){n.gestureWeight=.25;const q=E(A(4));p.train.position.x=mix(-7,-.4,q);pos=view===0?[3.9,2.8,6.7]:[1.5,3.6,6.5];target=[.2,1.3,-.7];}
  if(act===5){const q=E(A(5));n.x=mix(-.55,.15,q);n.yaw=q<.98?0:-Math.PI/2;n.headYaw=q<.98?-.6:0;n.moving=q>.001&&q<.999;n.distance=.70*q;n.hand=undefined;n.expr='smile';p.train.position.x=mix(-.4,4.8,q);pos=view===0?[3.3,2.4,5.6]:[1.8,2.1,4.3];target=[.2,1.3,.35];}
  if(act<4)p.train.position.x=-7;
 }
 if(theme===41){
  n.x=-.10;n.z=.14;n.yaw=Math.PI/2;n.headYaw=-.55;l.x=.26;l.z=-.88;l.yaw=-Math.PI/2;l.headYaw=.4;n.hand=[.27,1.14,.18];l.hand=[.2,1.14,.18];
  p.macro.visible=act===3;p.macro.position.set(0,1.25,-.38);p.macro.rotation.set(.35,.15,0);p.labels.forEach(q=>q.visible=act===2);
  p.chips.forEach((q,i)=>{q.visible=act!==3;const col=Math.floor(i/8),j=i%8;q.position.set(-.83+col*.82,1.18+j*.031,-.44);q.rotation.y=.12*col;});
  p.money.visible=act===0;p.money.rotation.y=.15;
  if(act===0){const q=A(0);n.hand=[mix(.25,.49,E(q/.45)),1.14,.18];l.hand=[.49,1.14,.18];pos=view===0?[2.5,2.5,5.2]:[1.3,1.8,2.6];target=[0,1.25,-.25];}
  if(act===1){const q=E(A(1));n.hand=[.49,1.14,.18];l.hand=[.49,1.14,.18];p.chips.slice(0,4).forEach((m,i)=>{m.position.set(mix(-.83,.08,q),1.18+i*.031,-.36);});pos=view===0?[1.5,2.4,3.8]:[-1.4,2.25,-2.7];target=[0,1.2,-.3];}
  if(act===2){n.gesture='point';n.gestureWeight=.65;n.hand=undefined;pos=view===0?[.6,2.8,2.9]:[2.2,2.3,4.0];target=[0,1.4,-.45];}
  if(act===3){showL=false;n.x=-1.8;n.z=.5;n.hand=undefined;pos=view===0?[.45,2.55,1.7]:[.9,2.2,1.65];target=[0,1.3,-.35];fov=46;}
  if(act===4){n.hand=[.30,1.25,.18];p.chips[0].position.copy(s.actors.nico.point());p.chips[0].position.y+=.06;n.expr='smile';pos=view===0?[2.4,2.4,4.5]:[-1.6,2.3,-2.7];target=[0,1.35,-.30];}
  if(act===5){n.hand=undefined;n.gesture='point';n.gestureWeight=.4;n.expr='determined';pos=view===0?[2.3,2.6,5.4]:[1.8,2.1,4.0];target=[0,1.35,-.3];}
 }
 if(theme===42){
  const lift=.36*E(A(2)),transfer=E(A(3)/.25),travel=3.0*E((A(3)-.35)/.65);p.load.position.set(travel,.715+lift-.37*transfer,-1.4);p.cart.position.x=travel;p.cart.position.y=act<3?-.04:.0;p.wheels.forEach(w=>w.rotation.z=-travel/.22);
  for(const j of p.jacks){const capY=.52+lift-.37*transfer-.20*E((A(3)-.25)/.20);j.cap.position.y=capY;j.piston.visible=capY>.36;j.piston.scale.y=Math.max(.01,capY-.35);j.piston.position.y=.30+Math.max(.01,capY-.35)/2;}
  n.x=-3+travel;n.z=1.05;n.yaw=-Math.PI/2;n.headYaw=.1;n.hand=[.23,1.13,.18];n.expr='determined';l.x=4.0;l.z=.8;l.yaw=-Math.PI/2;l.expr='smile';n.moving=act===3&&A(3)>.001&&A(3)<.999;n.yaw=n.moving?0:-Math.PI/2;n.headYaw=n.moving?-.65:0;n.distance=travel;holding='clipboard';
  if(act===0){pos=view===0?[7.8,4.8,12.4]:[5.7,2.8,8.9];target=[0,1.6,-.4];}
  if(act===1){pos=view===0?[2.9,3.0,7.4]:[-3.8,2.0,4.9];target=view===0?[-1.2,1.4,0]:[-2.3,1.35,.7];}
  if(act===2){pos=view===0?[3.5,1.3,4.5]:[5,2.25,6.4];target=[.2,.6,-.8];fov=49;}
  if(act===3){pos=view===0?[travel+5.5,3.8,10.8]:[travel+4.8,1.45,7.4];target=[travel,1.6,-.8];}
  if(act===4){pos=view===0?[8.7,6.6,12.4]:[6.6,4.4,10.2];target=[2.0,2.1,-.7];}
  if(act===5){n.moving=false;n.yaw=-Math.PI/2;n.headYaw=.10;pos=view===0?[7.8,4.4,11.9]:[4.4,2.5,7.4];target=[2.0,1.4,-.2];n.expr='smile';}
 }
 if(theme===43){
  showL=false;n.x=2.45;n.z=2.10;n.yaw=-Math.PI/2;n.headYaw=.1;n.gesture='point';n.gestureWeight=.35+.07*Math.sin(g*1.1);n.expr=act===0?'surprised':'smile';
  // Racetrack path; cabin orientation stays upright even on upper/lower arcs.
  const r=1.35,bottom=.8,top=6.25,h=top-bottom,len=2*h+2*Math.PI*r;
  p.cabins.forEach((q,i)=>{let d=(g*.52+i*len/8)%len,x,y;if(d<h){x=-r;y=bottom+d;}else if((d-=h)<Math.PI*r){const a=Math.PI-d/r;x=r*Math.cos(a);y=top+r*Math.sin(a);}else if((d-=Math.PI*r)<h){x=r;y=top-d;}else{d-=h;const a=-d/r;x=r*Math.cos(a);y=bottom+r*Math.sin(a);}q.position.set(x,y,0);q.rotation.set(0,0,0);});
  if(act===0){pos=view===0?[7.3,4.2,12.0]:[5.2,2.5,8.2];target=[.65,view===0?2.7:1.2,.45];}
  if(act===1){pos=view===0?[7.5,5.8,12.8]:[5.2,4.6,9.6];target=[0,3.0,0];}
  if(act===2){pos=view===0?[5.1,8.7,10.8]:[6.1,3.8,10.4];target=view===0?[0,5.8,0]:[0,2.3,0];}
  if(act===3){pos=view===0?[5.7,4.9,10.1]:[5.8,2.5,8.0];target=[.3,2.5,.6];}
  if(act===4){n.expr='determined';pos=view===0?[6.4,2.4,9.6]:[7.0,4.3,11.5];target=[1.1,1.8,.8];}
  if(act===5){n.gestureWeight=.18;n.expr='smile';pos=view===0?[5.8,3.6,9.6]:[7.0,5.0,12.2];target=[.8,2.7,.5];}
 }
 if(theme===44){
  n.x=-1.25;n.z=.75;n.yaw=0;n.headYaw=-.6;n.gesture='point';n.gestureWeight=.45;n.expr=act===0?'surprised':'smile';l.x=1.2;l.z=.65;l.yaw=-Math.PI/2;l.headYaw=.2;l.hand=[.25,1.17,.18];holding='ledger';p.date.visible=act===1||act===2;
  const bprogress=act<2?1:act===2?E(A(2)):1;p.bricks.forEach(({b,row,col,x,y},i)=>{const show=act!==2||bprogress>(i/32);b.visible=show;b.position.set(x,y,.075);});p.glass.visible=act===2&&A(2)<.12;
  if(act===0){pos=view===0?[3.2,2.9,7.0]:[1.3,2.0,3.8];target=[-.2,1.65,-.1];}
  if(act===1){pos=view===0?[3.0,3.0,6.7]:[2.2,2.0,3.2];target=view===0?[0,1.9,0]:[1.2,1.35,.7];}
  if(act===2){pos=view===0?[.6,2.0,3.1]:[2.3,2.9,5.9];target=[0,1.55,-.2];}
  if(act===3){n.expr='determined';pos=view===0?[-1.2,2.5,5.8]:[-3.0,1.9,3.3];target=[-2.5,1.6,-.2];}
  if(act===4){pos=view===0?[3.3,2.4,4.7]:[5.4,2.7,5.2];target=[3.05,1.55,-.2];}
  if(act===5){n.x=mix(-1.25,-.6,E(A(5)));n.moving=A(5)>.001&&A(5)<.999;n.distance=.65*E(A(5));n.headYaw=-.5;n.gestureWeight=.2;pos=view===0?[3.3,2.8,7.1]:[1.2,2.3,5.2];target=[0,1.4,.2];}
 }
 // Small motivated camera drift, no random shake or pulsing lights.
 pos[0]+=(v-.5)*.13;pos[2]+=(v-.5)*.12;
 s.actors.nico.update(n);s.actors.lia.update(l);s.actors.nico.root.visible=true;s.actors.lia.root.visible=showL;
 if(holding==='umbrella'){p.shaft.position.copy(s.actors.nico.point());p.shaft.rotation.set(0,0,0);}
 if(holding==='clipboard'){p.clipboard.position.copy(s.actors.nico.point());p.clipboard.position.x+=.05;p.clipboard.rotation.y=n.yaw+Math.PI/2;}
 if(holding==='ledger'){p.ledger.position.copy(s.actors.lia.point());p.ledger.position.y+=.04;p.ledger.rotation.set(.05,.05,0);}
 if(theme===40){const h=s.actors.nico.point(),dir=new H.Vector3(1.25,1.85,.1).sub(h).normalize();p.pointer.mesh.visible=act<4&&n.gestureWeight>.32;p.pointer.set(h.toArray(),h.clone().addScaledVector(dir,.12).toArray());}
 if(theme===41&&act===0){const q=A(0),to=new H.Vector3(.08,1.20,-.36);p.money.position.copy(s.actors.nico.point()).lerp(to,E((q-.15)/.5));}
 if(theme===41&&act===4){p.chips[0].position.copy(s.actors.nico.point());p.chips[0].position.y+=.06;}
 if(cover){
  s.actors.nico.update({time:1,x:theme===42?-2.2:theme===43?2.1:0,y:0,z:theme===43?2.1:1.15,yaw:-Math.PI/2,headYaw:.1,moving:false,expr:'surprised',gesture:'point',gestureWeight:.55});s.actors.lia.root.visible=false;
  const center=s.actors.nico.root.position;pos=[center.x+1.55,2.5,center.z+4.5];target=[center.x,1.4,center.z];fov=43;
  if(!s.coverLights){const a=new H.PointLight('#92edff',11,12,2),b=new H.PointLight('#ee65d0',13,12,2);s.root.add(a,b);s.coverLights=[a,b];}s.coverLights[0].position.set(center.x+2,3,center.z+2);s.coverLights[1].position.set(center.x-2,3,center.z-1);s.hemi.intensity=.8;s.sun.intensity=.65;
 }
 camera.position.set(...pos);camera.lookAt(...target);camera.fov=fov;camera.updateProjectionMatrix();s.root.updateMatrixWorld(true);s.state={time:g,act,view,nico:{...n},lia:{...l},theme,cover};return sh;
}
