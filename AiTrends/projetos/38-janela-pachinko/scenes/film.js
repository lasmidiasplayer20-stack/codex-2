import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {library,actor} from './rig.js';
const story=await(await fetch('/project/story/shots.json')).json();
const E=x=>ease.inOut(clamp(x)),mix=(a,b,q)=>a+(b-a)*q;
let cache;export let current=null;
function init(T){if(cache)return cache;const H=T.THREE,L=library(T),scene=new H.Scene(),camera=new H.PerspectiveCamera(43,9/16,.04,130);
 scene.background=new H.Color('#15223d');scene.fog=new H.Fog('#15223d',19,42);
 const hemi=new H.HemisphereLight('#d5efff','#4e2852',1.65);scene.add(hemi);const sun=new H.DirectionalLight('#ffedcf',2.0);sun.position.set(3,7,6);scene.add(sun);
 const neon=new H.PointLight('#f768ca',5,13,2);neon.position.set(-3,3,3);scene.add(neon);const blue=new H.PointLight('#46c8ed',4,12,2);blue.position.set(3,2,1);scene.add(blue);
 const sets={};for(const k of ['hall','counter','street','window','cycle']){sets[k]=new H.Group();scene.add(sets[k]);}
 const box=(p,c,xyz,sz,b=false)=>{const m=L.mesh('box',c,xyz,sz,b);p.add(m);return m;},ball=(p,c,xyz,r,b=false)=>{const m=L.mesh('sphere',c,xyz,Array.isArray(r)?r:[r,r,r],b);p.add(m);return m;};
 function panel(p,w,h,xyz,lines,cols=[],base='#152640'){const cv=document.createElement('canvas');cv.width=1024;cv.height=Math.round(1024*h/w);const cx=cv.getContext('2d');cx.fillStyle=base;cx.fillRect(0,0,cv.width,cv.height);cx.strokeStyle=cols[0]||'#61e7e9';cx.lineWidth=15;cx.strokeRect(9,9,1006,cv.height-18);cx.textAlign='center';cx.textBaseline='middle';lines.forEach((x,i)=>{cx.fillStyle=cols[i]||'#fff3ce';cx.font=`900 ${Math.min(195,cv.height/lines.length*.63)}px sans-serif`;cx.fillText(x,512,(i+.5)*cv.height/lines.length,970);});const tx=new H.CanvasTexture(cv);tx.colorSpace=H.SRGBColorSpace;const m=new H.Mesh(new H.PlaneGeometry(w,h),new H.MeshBasicMaterial({map:tx}));m.position.set(...xyz);p.add(m);return m;}
 function strip(p,c,xyz,sz){return box(p,c,xyz,sz,true);}
 function plant(p,x,z){box(p,'#d37a58',[x,.18,z],[.40,.36,.40]);for(let i=0;i<4;i++)ball(p,i%2?'#60bd91':'#89d688',[x+.12*Math.sin(i*2),.57+i*.08,z+.12*Math.cos(i*2)],[.17,.32,.17]);}
 function room(p,floor,wall){box(p,floor,[0,-.10,-1],[13,.20,13]);box(p,wall,[0,2.0,-3.7],[11,4,.14]);for(const x of [-4,4])box(p,'#34324f',[x,2,-.6],[.14,4,6]);for(let x=-4;x<=4;x++)strip(p,'#3c4762',[x,.008,-.6],[.012,.016,7]);}
 const hall=sets.hall;room(hall,'#533761','#292b48');for(const x of [-3.9,3.9]){strip(hall,x<0?'#ff83ca':'#5de3e1',[x,3.2,-.5],[.065,.065,6.2]);}
 panel(hall,3,.53,[0,3.05,-3.57],['PACHINKO'],['#ffe179']);
 const movingBalls=[],rotors=[];function machine(x,z){const m=new H.Group();m.position.set(x,0,z);hall.add(m);box(m,'#dd819b',[0,1.25,0],[.95,2.5,.45]);box(m,'#17263b',[0,1.56,.24],[.78,1.55,.08]);const ring=new H.Mesh(new H.TorusGeometry(.32,.027,8,36),L.mat('#ffd573',true));ring.position.set(0,1.75,.31);m.add(ring);for(let i=0;i<15;i++){const a=i*2.4;ball(m,'#e7f4ff',[.26*Math.sin(a),1.75+.28*Math.cos(a),.34],.018,true);}for(let i=0;i<5;i++)box(m,['#56dce1','#c0a0ff','#ffd96c'][i%3],[-.3+i*.15,.91,.31],[.10,.13,.04],true);box(m,'#574466',[0,.53,.26],[.80,.19,.41]);box(m,'#383e55',[0,.68,.49],[.74,.08,.14]);ball(m,'#ffe8b5',[.33,.83,.39],.065);panel(m,.52,.20,[0,2.13,.30],['7 • 7'],['#ffe888']);
 for(let i=0;i<6;i++){const q=ball(m,'#cee4eb',[0,1,.36],.026);movingBalls.push({q,offset:i/6,root:m});}const rotor=box(m,'#f4ba59',[0,1.75,.36],[.14,.14,.025]);rotors.push(rotor);
 const stool=new H.Group();stool.position.set(0,0,1);m.add(stool);const seat=L.mesh('limb','#5abeb8',[0,.51,0],[.28,.12,.28]);stool.add(seat);box(stool,'#b3bac5',[0,.24,0],[.08,.48,.08]);const foot=L.mesh('limb','#a4adb9',[0,.035,0],[.25,.05,.25]);stool.add(foot);return m;}
 for(const z of [-2.8,-.8,1.2]){machine(-2,z).rotation.y=Math.PI/2;machine(2,z).rotation.y=-Math.PI/2;}const heroMachine=machine(0,-2.6);plant(hall,-3,2.5);plant(hall,3,2.5);
 const counter=sets.counter;room(counter,'#644b77','#464560');box(counter,'#a46692',[0,.49,-.43],[3.7,.98,.40]);box(counter,'#f7c98b',[0,1.10,-.43],[3.9,.10,.46]);strip(counter,'#65ead7',[0,.86,-.03],[3.6,.055,.03]);panel(counter,2.4,.50,[0,2.8,-3.59],['BALCÃO DE PRÊMIOS'],['#ffe190']);panel(counter,1.6,.62,[1.6,1.85,-1.5],['PRÊMIOS','SEM DINHEIRO'],['#8aefdc','#ffe2ab']);for(const y of [.6,1.45,2.25]){box(counter,'#d8a36b',[0,y,-3.2],[3.6,.08,.6]);for(let j=0;j<7;j++){const x=-1.45+j*.48;box(counter,['#75bcd1','#e9a769','#d597c7','#a1c975'][j%4],[x,y+.22,-3.18],[.28,.37,.22]);if(j%2===0)strip(counter,'#fff1cf',[x,y+.22,-3.05],[.035,.34,.01]);}}plant(counter,-2.5,-.2);
 const special=new H.Group();scene.add(special);box(special,'#dab552',[0,0,0],[.25,.12,.16]);box(special,'#fcf2c5',[0,.065,0],[.21,.015,.12]);strip(special,'#df639b',[0,.077,0],[.04,.01,.15]);
 const cash=new H.Group();scene.add(cash);for(let i=0;i<3;i++){box(cash,'#b9d7a6',[i*.005,i*.012,0],[.25,.012,.13]);strip(cash,'#e6f2d0',[0,i*.012+.007,0],[.04,.002,.13]);}
 const tray=new H.Group();scene.add(tray);box(tray,'#eac85e',[0,0,0],[.37,.09,.29]);for(const x of [-.19,.19])box(tray,'#b99f4d',[x,.065,0],[.025,.15,.31]);for(const z of [-.15,.15])box(tray,'#b99f4d',[0,.065,z],[.40,.15,.025]);for(let i=0;i<28;i++)ball(tray,'#c7dbe8',[(i%6-2.5)*.055,.10+Math.floor(i/18)*.047,(Math.floor(i/6)%3-1)*.065],.031);
 const street=sets.street;box(street,'#6e8e9a',[0,-.1,0],[24,.20,14]);box(street,'#32475e',[0,.016,2.7],[24,.03,1.8]);for(let i=-4;i<=4;i++){const x=i*2.7,h=3.4+(i+4)%3*.6;box(street,['#b075a8','#5b9fa8','#bc8b73','#8879b8'][(i+4)%4],[x,h/2,-1.9],[2.5,h,1.8]);box(street,'#33435b',[x,1.1,-.94],[.85,2.2,.08]);for(const dx of [-.7,.6]){box(street,'#ffd691',[x+dx,2.8,-.94],[.48,.65,.045],true);}panel(street,1.8,.34,[x,2.08,-.86],[i===0?'SALÃO A':i===1?'LOJA B':'LOJA'],[i%2?'#f7b4e9':'#79efdb']);for(let j=0;j<5;j++)box(street,j%2?'#f6cfa3':'#b85d83',[x-1+j*.5,1.85,-.50],[.5,.09,.68]);}
 for(const x of [-4,4]){box(street,'#253f58',[x,1.5,.8],[.065,3,.065]);ball(street,'#ffecaa',[x,3.04,.8],.15,true);plant(street,x-1,.9);}
 // The exchange booth has an actual opening: no wall or plane covering the handoff.
 const win=sets.window;box(win,'#7b8491',[0,-.10,0],[10,.2,9]);box(win,'#bd9b78',[-2.1,1.75,-.62],[2.7,3.5,.16]);box(win,'#bd9b78',[2.1,1.75,-.62],[2.7,3.5,.16]);box(win,'#bd9b78',[0,2.82,-.62],[1.5,1.36,.16]);box(win,'#bd9b78',[0,.37,-.62],[1.5,.74,.16]);box(win,'#dab888',[0,1.055,-.48],[1.64,.10,.60]);for(const x of [-.79,.79])box(win,'#354257',[x,1.48,-.58],[.10,1.12,.22]);box(win,'#354257',[0,2.08,-.58],[1.68,.10,.22]);box(win,'#354257',[0,.94,-.58],[1.68,.10,.22]);box(win,'#947459',[0,1.7,-2.4],[3.0,3.4,.12]);panel(win,1.45,.33,[0,2.36,-.50],['COMPRA DE PRÊMIOS'],['#ffdd8a']);panel(win,.65,.27,[.98,1.13,-.50],['LOJA B'],['#8fe3e8']);for(let i=0;i<5;i++)box(win,'#dac189',[-.65+i*.30,.97,-1.9],[.16,.15,.18]);box(win,'#ddb18c',[0,.84,-1.8],[2,.08,.40]);plant(win,-2.25,.4);for(let i=0;i<4;i++)strip(win,'#e0b77e',[.88+i*.29,.012,1.5],[.17,.01,.7]);
 const cyc=sets.cycle;box(cyc,'#223858',[0,-.1,0],[15,.2,12]);const nodes=[[-1.45,0],[1.45,0],[0,-2.5]],colors=['#c96a9d','#5697b3','#be9657'];
 const nodeSigns=[];for(let i=0;i<3;i++){const[x,z]=nodes[i];box(cyc,colors[i],[x,.42,z],[1.5,.84,1.1]);box(cyc,'#fff0c2',[x,.87,z],[1.56,.10,1.2]);const q=panel(cyc,1.38,.46,[x,1.30,z+.59],[["SALÃO A","LOJA B","ATACADISTA C"][i]],[['#f9cae4','#a3f5ed','#ffdf8d'][i]]);nodeSigns.push(q);}
 const route=[];for(let n=0;n<3;n++){const a=nodes[n],b=nodes[(n+1)%3];for(let i=0;i<10;i++){const u=(i+.5)/10;const q=box(cyc,'#64dece',[mix(a[0],b[0],u),.055,mix(a[1],b[1],u)],[.12,.025,.18],true);q.rotation.y=Math.atan2(b[0]-a[0],b[1]-a[1]);route.push(q);}}
 const routePrize=new H.Group();cyc.add(routePrize);box(routePrize,'#ffdd71',[0,0,0],[.25,.16,.20]);strip(routePrize,'#ee7aa4',[0,.085,0],[.035,.014,.23]);
 const van=new H.Group();cyc.add(van);box(van,'#a47bc9',[0,.34,0],[.6,.4,.33]);box(van,'#bee2ec',[.24,.43,0],[.18,.20,.35]);for(const x of [-.2,.2])for(const z of [-.19,.19])ball(van,'#18243b',[x,.15,z],.09);panel(cyc,3,.42,[0,2.35,-3.5],['TRÊS ESTABELECIMENTOS'],['#ffe39c']);
 const actors={nico:actor(T,'nico'),lia:actor(T,'lia'),sol:actor(T,'sol'),courier:actor(T,'courier'),ari:actor(T,'ari')};for(const a of Object.values(actors))scene.add(a.root);
 const stage={render(){T.getRenderer().render(scene,camera);},dispose(){}};
 return cache={H,L,scene,camera,stage,sets,actors,hemi,sun,neon,blue,tray,special,cash,movingBalls,rotors,route,routePrize,van,nodes,box,ball,panel};
}
function draw(s,t,info){current=s;const H=s.H,g=info.globalT,act=info.act,cam=info.cam,sh=story.shots.find(x=>g>=x.start&&g<x.end)||story.shots.at(-1),u=clamp((g-sh.start)/(sh.end-sh.start)),v=E(u);
 for(const set of Object.values(s.sets))set.visible=false;for(const a of Object.values(s.actors))a.root.visible=false;for(const p of [s.special,s.cash,s.tray])p.visible=false;
 const range=a=>{const x=story.shots.filter(q=>q.params.act===a);return [x[0].start,x.at(-1).end];},progress=a=>{const[b,e]=range(a);return clamp((g-b)/(e-b));};
 let set='hall',pos=[3,2.65,6],target=[0,1.25,0],fov=43;
 const n={time:g,x:0,y:.02,z:.8,yaw:-Math.PI/2,headYaw:0,moving:false,expr:'smile'},l={...n,x:.4,z:-1.3,yaw:-Math.PI/2},b={...n,x:-1.7,z:1.1};let showL=false,showB=false,holding=false,holder='nico',specialOnTray=false,cashMode=0;
 if(act==='hall'){
  set='hall';const q=progress('hall');n.z=mix(1.75,-.25,E(q));n.yaw=Math.PI/2;n.headYaw=q<.8?-.50:-.2;n.moving=q<.96;n.distance=2*E(q);n.expr='surprised';showL=showB=true;l.x=1.0;l.z=-.8;l.yaw=0;l.sit=true;b.x=-1.0;b.z=1.2;b.yaw=Math.PI;b.sit=true;
  pos=cam==='crane'?[1.8-1.3*v,4.8-1.8*v,7.3-1.2*v]:[.8+v*.35,2.45,n.z+5.5];target=[0,1.35,n.z-.5];
 }
 if(act==='machine'){
  n.z=-1.56;n.yaw=Math.PI/2;n.sit=true;n.headYaw=-.35;n.hand=[.34,.83,.12];n.handB=[.28,.68,-.18];n.expr='joy';s.tray.visible=true;s.tray.position.set(0,.72,-1.96);s.tray.rotation.set(0,0,0);
  if(cam==='over'){pos=[.85,2.1,.40];target=[0,1.5,-2.2];fov=49;}else{pos=[.50,1.63,-1.45];target=[0,1.60,-2.35];fov=54;}
 }
 if(act==='counter'||act==='prize'){
  set='counter';showL=true;n.x=-.10;n.z=.06;n.yaw=Math.PI/2;n.headYaw=-.55;l.x=.26;l.z=-.92;l.yaw=-Math.PI/2;l.headYaw=.35;n.expr='surprised';l.expr='smile';
  s.tray.visible=true;s.tray.position.set(-.65,1.20,-.4);s.tray.rotation.set(0,0,0);
  if(act==='counter'){n.gesture='think';n.gestureWeight=.65;l.gesture='point';l.gestureWeight=.6;pos=cam==='reverse'?[1.85,2.15,-2.65]:[1.65-v*.5,2.3,4.55-v*.45];target=[0,1.25,-.4];}
  else{
   const q=progress('prize');const extend=E(q/.40),take=E((q-.50)/.24),recover=E((q-.78)/.2);
   // Reachable palms meet the counter surface; prize follows seller, then table, then buyer.
   l.hand=[mix(.13,.49,extend*(1-recover)),mix(1.22,1.14,extend),.18];n.hand=[mix(.15,.49,take),mix(1.22,1.14,take),.18];n.expr=q>.7?'smile':'surprised';s.special.visible=true;
   if(q<.43){holder='lia';holding=true;}else if(q<.74){specialOnTray=true;}else{holder='nico';holding=true;}
   pos=cam==='macro'?[.85,1.75,1.2]:[-1.5,2.35,3.65];target=cam==='macro'?[.06,1.08,-.36]:[0,1.25,-.25];fov=cam==='macro'?45:43;
  }
 }
 if(act==='walk'){
  set='street';const q=progress('walk');n.x=mix(-1.6,1.1,E(q));n.z=.28;n.yaw=0;n.headYaw=-.6;n.moving=q<.96;n.distance=2.7*E(q);n.hand=[.28,1.15,.18];holding=true;showB=true;b.x=mix(-2.7,-1.1,E(q));b.z=1.0;b.yaw=0;b.moving=true;b.distance=1.6*E(q);b.headYaw=-.6;
  pos=cam==='track'?[n.x+2.6,2.4,4.7]:[n.x+2.8,1.05,4.1];target=[n.x,1.15,.30];
 }
 if(act==='window'||act==='exchange'){
  set='window';showL=true;n.x=-.10;n.z=.06;n.yaw=Math.PI/2;n.headYaw=-.6;l.x=.26;l.z=-.92;l.yaw=-Math.PI/2;l.headYaw=.4;n.hand=[.28,1.12,.18];holding=true;
  // Hook starts with prize in palm at the same booth that will explain it later.
  if(act==='window'){n.expr='surprised';l.gesture='think';l.gestureWeight=.45;pos=cam==='detail'?[.73,1.63,1.3]:[1.85-v*.25,2.30,4.55-v*.5];target=cam==='detail'?[.02,1.16,-.29]:[0,1.4,-.35];}
  if(act==='exchange'){
   const q=progress('exchange'),reach=E(q/.30),withdraw=E((q-.45)/.17),pay=E((q-.57)/.23);n.hand=[mix(mix(.28,.49,reach),.25,E((q-.86)/.12)),mix(1.08,1.20,E((q-.86)/.12)),.18];l.hand=[mix(.15,.49,Math.max(E((q-.32)/.10),pay)),1.08,.18];
   holding=q<.31;specialOnTray=q>=.31&&q<.45;s.special.visible=q<.62;if(q>=.45&&q<.62){holding=true;holder='lia';}s.cash.visible=q>=.60;cashMode=q<.82?1:2;n.expr=q>.8?'joy':'smile';
   pos=cam==='detail'?[.95,1.8,1.45]:[-1.65,2.4,3.85];target=[0,1.22,-.43];
  }
 }
 if(act==='cycle'){
  set='cycle';n.x=-1.45;n.z=.9;n.yaw=-Math.PI/2;n.gesture='point';n.gestureWeight=.45;showL=showB=true;l.x=1.45;l.z=.85;l.yaw=-Math.PI/2;b.x=.0;b.z=-1.6;b.yaw=-Math.PI/2;
  const q=progress('cycle'),phase=q*3,idx=Math.min(2,Math.floor(phase)),p=E(phase-idx),a=s.nodes[idx],bnode=s.nodes[(idx+1)%3];s.routePrize.position.set(mix(a[0],bnode[0],p),1.05+Math.sin(p*Math.PI)*.35,mix(a[1],bnode[1],p));s.routePrize.rotation.y=g*.5;
  s.van.visible=q>.28;s.van.position.set(mix(1.7,-.7,E((q-.3)/.7)),.03,-2.9);s.van.rotation.y=Math.PI;s.route.forEach((m,i)=>m.material=s.L.mat(Math.floor(i/10)===idx?'#ffe480':'#64dece',true));
  pos=cam==='top'?[.02,8.2,4.1]:cam==='shop'?[2.8-v*.3,2.5,3.6]:cam==='wholesaler'?[1.8,3.0,2.8-v*.3]:cam==='van'?[2.9-v*.6,2.4,.8]:[Math.sin(.25+v*.35)*5.7,5.2,6.0];target=cam==='shop'?[.8,.8,-.4]:cam==='wholesaler'?[0,.9,-2.0]:cam==='van'?[.2,.6,-2.5]:[0,.55,-.8];fov=48;
 }
 if(act==='end'){
  set='street';n.x=.1;n.z=.15;n.yaw=-Math.PI/2;n.expr='smile';n.gesture='point';n.gestureWeight=.30+.08*Math.sin(g*2);showL=true;l.x=-1.0;l.z=-.25;l.yaw=-Math.PI/2;l.expr='smile';
  pos=cam==='close'?[.95-v*.2,1.95,3.65-v*.25]:cam==='side'?[3.0+v*.4,2.7,5.4]:[1.2,2.5,5.3-v*.4];target=cam==='side'?[.9,1.45,-.4]:[.0,1.25,.05];
 }
 s.sets[set].visible=true;s.actors.nico.update(n);s.actors.nico.root.visible=true;s.actors.lia.update(l);s.actors.lia.root.visible=showL;s.actors.courier.update(b);s.actors.courier.root.visible=showB;
 if(holding){s.special.visible=true;const h=s.actors[holder].point();s.special.position.copy(h);s.special.position.y+=.065;s.special.rotation.set(0,s.actors[holder].root.rotation.y,0);}
 if(specialOnTray){s.special.visible=true;s.special.position.set(.08,act==='prize'?1.225:1.165,-.43);s.special.rotation.set(0,.2,0);}
 if(s.cash.visible){const a=s.actors.lia.point(),b=s.actors.nico.point(),q=progress('exchange');s.cash.position.copy(a).lerp(b,E((q-.76)/.10));s.cash.position.y+=.07;s.cash.rotation.y=Math.PI/2;}
 // Moving steel balls have deterministic gravity, never reverse upwards in the channel.
 for(const {q,offset}of s.movingBalls){const p=(g*.65+offset)%1;q.position.set(.18*Math.sin(p*11),2.0-1.08*p,.365);}s.rotors.forEach((r,i)=>r.rotation.z=g*1.6+i);
 if(set!=='cycle')s.van.visible=false;
 s.camera.position.set(...pos);s.camera.lookAt(...target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
 s.state={time:g,act,cam,set,prize_holder:holding?holder:specialOnTray?'counter':'none',cash_visible:s.cash.visible,characters:['nico',...(showL?['lia']:[]),...(showB?['courier']:[])]};
}
function overlay(g,t,info){const labels={window:['POR QUE DUAS PORTAS?','O caminho do prêmio'],hall:['PACHINKO','Bolinhas de aço → mercadorias'],machine:['DA MÁQUINA AO BALCÃO','Ilustração do funcionamento'],counter:['O SALÃO ENTREGA PRÊMIOS','Não paga dinheiro no balcão'],prize:['UM PRÊMIO ESPECIAL','É um objeto, não uma cédula'],walk:['A TROCA MUDA DE ENDEREÇO','Outro estabelecimento'],exchange:['A LOJA COMPRA O OBJETO','Operações separadas'],cycle:['O CIRCUITO DO PRÊMIO','Salão → loja → atacadista'],end:['A DIFERENÇA ESTÁ NA OPERAÇÃO','Não é autorização para qualquer aposta']};const a=labels[info.act];g.fillStyle='#12233eec';rr(g,55,130,970,150,22);g.fill();text(g,a[0],540,177,{size:35,color:'#ffe088',align:'center'});text(g,a[1],540,235,{size:32,color:'#e7fffa',align:'center'});text(g,'ENTÃO • EXPLICAÇÃO ILUSTRADA',540,1795,{size:23,color:'#fff0d7',align:'center'});}
for(const sh of story.shots)registerShot(sh.id,{kind:'3d',init,draw,overlay});
