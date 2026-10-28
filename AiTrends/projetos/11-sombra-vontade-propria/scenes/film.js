import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {library,actor} from './rig.js';
const story=await(await fetch('/project/story/shots.json')).json(),S=x=>ease.inOut(clamp(x)),lerp=(a,b,p)=>a+(b-a)*p;
const shot=n=>story.shots.find(x=>x.params.cam===n),at=n=>shot(n).start,end=n=>shot(n).end,phase=(g,n)=>S((g-at(n))/(end(n)-at(n)));
let cached;export let current=null;
function make(T){if(cached)return cached;const L=library(T),H=T.THREE,scene=new H.Scene(),camera=new H.PerspectiveCamera(45,9/16,.05,100);scene.background=new H.Color('#83c9ec');scene.add(new H.HemisphereLight('#e2edfa','#7e8271',1.7));const key=new H.DirectionalLight('#ffe3af',2);key.position.set(-4,8,6);scene.add(key);
 const box=(c,p,s,parent=scene)=>{const m=L.mesh('box',c,p,s);parent.add(m);return m;};box('#d9b988',[0,-.14,0],[24,.28,20]);box('#f2dfaf',[0,.005,0],[6,.035,8]);box('#607c8e',[0,.01,-5],[24,.05,2.5]);for(let i=0;i<9;i++)box('#e3d3ae',[-12+i*3,.05,-5],[1.4,.01,.10]);
 // Keep pavement quiet so the independent silhouette is the visual subject.
 for(const x of [-4.3,5.4]){box('#8d785f',[x,.85,-3.3],[.17,1.7,.17]);const m=L.mesh('sphere','#7ca184',[x,2.05,-3.3],[1.0,1.1,1.0]);scene.add(m);}
 for(let i=0;i<6;i++){const h=3+i%3;box(['#70bec3','#ee9b91','#b39bd7','#e5c66d','#8bc2a3','#e9ac72'][i%3],[-11+i*4,h/2,-8],[3.2,h,2]);for(let j=0;j<3;j++)box('#edd5ad',[-12+i*4+j*.85,1.6,-6.97],[.35,.55,.03]);}

 // Colorful original street dressing. Keep the central shadow-reading area clear.
 const street=new H.Group();scene.add(street);
 for(let i=0;i<5;i++){
  const x=-7+i*2.6,z=-4.0,h=2.1+(i%2)*.35,col=['#ed967c','#80c4c8','#bca1df','#f1ce76','#8ac9a6'][i];
  box(col,[x,h/2,z],[2.25,h,1.6],street);box('#eee2c7',[x,h+.08,z],[2.4,.16,1.75],street);
  box('#406a7b',[x,h*.52,z+.82],[.72,1.25,.04],street);box('#ffe1a1',[x-.65,h*.58,z+.84],[.38,.55,.05],street);
  for(let k=0;k<6;k++)box(k%2?'#fff1cc':['#d86565','#4b9eaa','#8d73b6','#da9b4d','#5e9d72'][i],[x-.94+k*.38,h*.83,z+1.03],[.38,.09,.52],street);
  for(const dx of [-.76,.76]){box('#b87954',[x+dx,.25,z+.92],[.36,.38,.34],street);for(let f=0;f<3;f++){const stem=L.mesh('limb','#578d66',[x+dx+(f-1)*.08,.60,z+.95],[.012,.34,.012]);street.add(stem);street.add(L.mesh('sphere',['#ef6b83','#f7ce63','#b68ed5'][f],[x+dx+(f-1)*.08,.79+(f%2)*.06,z+.95],[.07,.07,.07]));}}
 }
 // Planters, cafe furniture and a bicycle are outside the actors' routes.
 for(const x of [-3.0,4.7]){box('#c27d60',[x,.28,2.7],[.65,.48,.55],street);for(let k=0;k<5;k++)street.add(L.mesh('sphere',['#76af79','#91c481','#5e9f7b'][k%3],[x+Math.sin(k*2)*.18,.72+(k%2)*.15,2.7+Math.cos(k*2)*.15],[.19,.26,.19]));}
 for(const z of [-2.1,-.9]){box('#cb8d60',[-3.2,.48,z],[1.25,.12,.52],street);for(const x of [-3.65,-2.75])box('#667c7e',[x,.23,z],[.06,.46,.40],street);}
 const bike=new H.Group();street.add(bike);bike.position.set(-3.6,0,-2.7);for(const x of [-.40,.40]){const wheel=new H.Mesh(new H.TorusGeometry(.30,.027,7,32),L.mat('#384b5d',true));wheel.position.set(x,.32,0);bike.add(wheel);}for(const [a,b]of [[[-.4,.32,0],[0,.70,0]],[[0,.70,0],[.4,.32,0]],[[-.4,.32,0],[.17,.32,0]],[[.17,.32,0],[0,.70,0]]])L.bone(bike,'#e67376',.027).set(a,b);
 // A few slow clouds provide depth without distracting flicker.
 const butterflies=[];for(let i=0;i<2;i++){const b=new H.Group();scene.add(b);const wings=[];for(const side of [-1,1]){const w=L.mesh('sphere',i?'#ee85ab':'#f0bc55',[side*.08,0,0],[.09,.025,.11],true);b.add(w);wings.push(w);}butterflies.push({root:b,wings});}
 const clouds=new H.Group();scene.add(clouds);for(let i=0;i<3;i++)for(let k=0;k<3;k++)clouds.add(L.mesh('sphere','#e6f4f5',[-9+i*8+k*.65,7.5+(i%2),-14],[.85,.35,.4],true));
 const facade=new H.Group();scene.add(facade);box('#efb078',[3.15,2.25,-.7],[.25,4.5,6.0],facade);box('#304a5f',[2.995,3.38,.8],[.035,1.1,1.25],facade);for(const z of [.18,1.42])box('#eee0bd',[2.96,3.38,z],[.07,1.2,.055],facade);for(const y of [2.82,3.94])box('#eee0bd',[2.96,y,.8],[.07,.055,1.3],facade);box('#aa8e72',[1.98,2.96,.8],[2.0,.16,1.4],facade);box('#8d7762',[2.2,2.55,.8],[.10,.7,.12],facade);
 const vase=new H.Group();scene.add(vase);const clay=L.mat('#bc795f');const pot=new H.Mesh(new H.CylinderGeometry(.23,.16,.40,18),clay);pot.position.y=.20;vase.add(pot);const rim=new H.Mesh(new H.TorusGeometry(.23,.035,6,24),clay);rim.rotation.x=Math.PI/2;rim.position.y=.38;vase.add(rim);for(let i=0;i<5;i++){const a=i*2.4,m=L.mesh('sphere',['#57896c','#71a879'][i%2],[Math.sin(a)*.13,.54+(i%2)*.06,Math.cos(a)*.13],[.08,.2,.065]);m.rotation.z=Math.sin(a)*.6;vase.add(m);}
 const shards=[];for(let i=0;i<10;i++){const m=new H.Mesh(new H.TetrahedronGeometry(.13),clay);scene.add(m);m.scale.set(1,.4,1);shards.push(m);}
 const actors={nico:actor(T,'nico'),lia:actor(T,'lia')};Object.values(actors).forEach(a=>scene.add(a.root));actors.nico.shadow.visible=false;
 const shade=actor(T,'nico'),shadowParent=new H.Group();scene.add(shadowParent);shadowParent.add(shade.root);const black=new H.MeshBasicMaterial({color:'#263346',side:H.DoubleSide});shade.root.traverse(m=>{if(m.isMesh){if(m.material?.map)m.visible=false;else m.material=black;}});shade.shadow.visible=false;shadowParent.matrixAutoUpdate=false;
 const guide=new H.Group();scene.add(guide);for(let i=0;i<3;i++)box('#263346',[0,.045,-i*.12],[.07,.018,.10],guide);guide.visible=false;
 const renderer=T.getRenderer();renderer.shadowMap.enabled=false;const stage={render(){renderer.render(scene,camera);},dispose(){}};return cached={H,L,scene,camera,stage,clouds,butterflies,actors,shade,shadowParent,facade,vase,shards,guide};}
function draw(s,t,info){current=s;const g=info.globalT,c=info.cam,H=s.H;s.clouds.position.x=.25*Math.sin(g*.04);s.butterflies.forEach((b,i)=>{b.root.position.set(-2.3+i*.5+.25*Math.sin(g*.5+i),1.3+.18*Math.sin(g*.7+i),-2.7+.2*Math.cos(g*.5+i));b.wings.forEach((w,k)=>w.rotation.z=(k?1:-1)*(.3+.45*Math.sin(g*6+i)));});let nx=lerp(-.2,-1.25,phase(g,'left')),nz=.8;const go=S((g-at('stamp'))/(end('escape')-at('stamp')));if(g>=at('stamp'))nx=lerp(-1.25,-.35,go);if(c==='stamp')nx=lerp(-1.25,.8,S(info.p/.55));if(c==='escape')nx=.8;if(g>=at('alert'))nx=lerp(.8,.75,S((g-at('alert'))/(end('look')-at('alert'))));
 const jump=phase(g,'jump');if(g>=at('jump'))nx=lerp(.75,-.95,jump);if(g>=at('lead'))nx=lerp(-.95,-2.1,phase(g,'end'));
 const n={x:nx,z:nz,y:0,yaw:0,time:g,headYaw:-.6,moving:['left','stamp','escape','alert','point','look','end'].includes(c),distance:phase(g,'left')*1.05+(g>=at('stamp')?2.05*S((g-at('stamp'))/((end('stamp')-at('stamp'))*.55)):0)+(g>=at('end')?phase(g,'end')*1.15:0),gaitWeight:1,expr:['jump','crash'].includes(c)?'surprised':'smile'},l={x:2.05,z:1.75,y:0,yaw:-Math.PI/2,time:g,moving:false,headYaw:.2,expr:c==='lia'?'joy':'smile',gesture:'think',gestureWeight:.6};
 if(['wave','cross'].includes(c)){n.moving=false;n.hand=[.12,1.92,.19];n.handB=[.1,1.1,-.19];n.expr='surprised';}if(c==='stamp'){n.moving=info.p<.55;if(info.p>=.55)n.stamp=(info.p-.55)/.45;n.expr='determined';}if(['point','look','insist','window','slide'].includes(c)){n.moving=false;n.nod=c==='look'?.12:.38;n.headYaw=c==='look'?-1.15:0;}
 if(c==='jump'){n.y=.42*Math.sin(Math.PI*info.p);n.floatFeet=info.p>.03&&info.p<.97;n.floatPhase=.3;n.moving=false;n.gesture='surprise';n.gestureWeight=.9;}if(['crash','thanks'].includes(c)){n.moving=false;n.gesture=c==='thanks'?'point':'think';n.gestureWeight=.8;}
 if(['lead','end'].includes(c)){n.yaw=Math.PI;n.headYaw=.6;n.gesture='think';n.gestureWeight=.5;}s.actors.nico.update(n);s.actors.lia.update(l);s.actors.nico.shadow.visible=false;
 let sx=lerp(-.1,1.2,S((g-at('left'))/(end('right')-at('left')))),sz=.8;const sh={x:0,z:0,y:0,yaw:-Math.PI/2,time:g,moving:false,headYaw:0,expr:'smile'};
 if(['wave','cross','argument','stamp'].includes(c)){sh.allowCross=true;sh.hand=[.18,1.35,-.20];sh.handB=[.18,1.35,.20];}if(c==='stamp')sx=lerp(1.2,1.9,S((info.p-.7)/.3));if(c==='escape'){sx=lerp(1.9,2.3,info.p);sh.moving=true;sh.distance=info.p*.7;}
 if(g>=at('alert')){sx=.55;sz=.9;sh.yaw=0;sh.gesture='point';sh.gestureWeight=1;}
 if(c==='knock'){sh.gesture=undefined;sh.hand=[.48,1.15+.13*Math.cos(info.p*6*Math.PI),.19];}
 if(g>=at('jump')){sx=lerp(.55,-.85,jump);sh.gesture='point';}if(g>=at('lead')){sx=lerp(-.85,-2.7,phase(g,'end'));sz=.6;sh.yaw=Math.PI;sh.gesture='point';sh.moving=true;sh.distance=phase(g,'end')*1.85;}
 s.shade.update(sh);s.shade.shadow.visible=false;
 // Project the full articulated cast into a stable ground silhouette, no image assets.
 s.shadowParent.matrix.set(1,.22,0,sx, 0,.012,0,.045, 0,-1.12,.38,sz, 0,0,0,1);s.shadowParent.matrixWorldNeedsUpdate=true;
 const fallStart=at('crash')-.72,fallT=Math.max(0,g-fallStart),fallY=Math.max(.03,3.045-4.9*fallT*fallT),impact=fallT>=Math.sqrt((3.045-.03)/4.9);s.vase.position.set(lerp(1.10,.75,phase(g,'slide')),fallY,.80);s.vase.rotation.z=-.18*phase(g,'slide')-.9*Math.min(fallT,1);s.vase.visible=!impact;
 for(let i=0;i<s.shards.length;i++){const m=s.shards[i],a=i*2.4,u=S((fallT-.785)/.5);m.visible=impact;m.position.set(.75+Math.sin(a)*(.12+.40*u),.07+Math.sin(Math.PI*u)*.18,.80+Math.cos(a)*(.12+.38*u));m.rotation.set(i*.5,.4*i,.6*i);}
 let target=new H.Vector3(.25,.85,-.1),pos=new H.Vector3(.4,6.8,10.8),fov=46;
 const head=s.actors.nico.head.getWorldPosition(new H.Vector3());
 switch(c){case'hook':target.set(.2,.7,-.2);pos.set(.7,6.5,12-info.p*.5);fov=48;break;case'left':case'right':target.set((nx+sx)/2,.5,-.1);pos.set(.8,7.8,9);fov=47;break;case'argument':case'wave':target.set((nx+sx)/2,.7,-.1);pos.set(.3+.5*info.p,6.5,10);fov=47;break;case'cross':case'alert':case'point':case'knock':case'insist':target.set(sx+.15,.05,-.3);pos.set(sx+.3,6.2,3.5);fov=43;break;case'stamp':target.set(nx+.4,.2,.25);pos.set(nx+1.0,2.0,3.7);break;case'escape':target.set((nx+sx)/2,.25,.2);pos.set(1.2,5.5,7);break;case'lia':target.copy(s.actors.lia.head.getWorldPosition(new H.Vector3()));pos.copy(target).add(new H.Vector3(.6,.18,1.9));fov=40;break;case'look':target.copy(head);pos.copy(target).add(new H.Vector3(1.7,.25,2));fov=41;break;case'window':case'slide':target.copy(s.vase.position).add(new H.Vector3(.5,.4,0));pos.copy(target).add(new H.Vector3(-3.1,1.0,4.2));fov=43;break;case'jump':target.set(.3,1.4,.8);pos.set(-2.1,2.5,7);fov=48;break;case'crash':target.set(.75,.25,.8);pos.set(-.7,2.0,4.3);fov=42;break;case'thanks':target.set(-.5,.7,-.1);pos.set(.7,5,8);break;case'lead':case'end':target.set((nx+sx)/2,.5,-.1);pos.set(nx+2.5,6,9);fov=47;break;}
 s.camera.position.copy(pos);s.camera.lookAt(target);s.camera.fov=fov;s.camera.updateProjectionMatrix();
 for(const [id,a]of Object.entries(s.actors))a.root.visible=!['cross','alert','point','knock','insist','window','slide','crash'].includes(c);s.shadowParent.visible=!['lia','look','window','slide','crash'].includes(c);
 // Exterior facade stays beyond the camera side; no foreground canopy on reaction inserts.
 s.facade.visible=!['lia','look','cross','alert','point','knock','insist','stamp'].includes(c);s.vase.visible=s.vase.visible&&s.facade.visible;if(['look','left','right','wave','argument','stamp','escape','jump','thanks','lead','end'].includes(c))s.actors.lia.root.visible=false;
 s.state={nx,sx,sz,fallY,impact,fallT,foot:s.actors.nico.point('foot').toArray()};
}
const labels={hook:['E SE SUA SOMBRA','TIVESSE VONTADE?'],left:['NICO VAI','À ESQUERDA'],right:['ELA VAI','À DIREITA'],wave:['ELE ACENA…','ELA NÃO!'],cross:['A SOMBRA','CRUZA OS BRAÇOS'],argument:['VIROU','UMA DISCUSSÃO!'],stamp:['TENTOU','PISAR NELA'],escape:['ELA','ESCAPOU!'],lia:['LIA ACHA','GRAÇA'],alert:['MAS ALGO','MUDOU'],point:['OLHA','LÁ EM CIMA!'],look:['NICO NÃO','VIU NADA'],knock:['TOC! TOC! TOC!','PRESTA ATENÇÃO'],insist:['ELA INSISTE','NA JANELA'],window:['UM VASO','NA BEIRADA'],slide:['ESTÁ','ESCORREGANDO!'],jump:['SAI','DAÍ!'],crash:['ERA ONDE','ELE ESTAVA'],thanks:['OBRIGADO,','MINHA SOMBRA'],lead:['FIZERAM','AS PAZES?'],end:['AGORA ELA','ESCOLHE O CAMINHO']};
function overlay(g,t,info){const[a,b]=labels[info.cam];g.fillStyle='#173147ef';rr(g,58,145,964,180,28);g.fill();text(g,a,540,200,{size:43,color:'#f5fff7',align:'center'});text(g,b,540,265,{size:46,color:'#ffe183',align:'center'});text(g,'EXPERIMENTO IMAGINÁRIO',540,1750,{size:27,color:'#3d5365',align:'center'});}
for(const x of story.shots)registerShot(x.id,{kind:'3d',init:make,draw,overlay});
