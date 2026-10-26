// Opening only. Later shots remain explicitly unimplemented until audio evaluation.
import {registerShot,clamp,ease,text,rr} from '/engine/core.js';
import {world} from './world.js';
const story=await(await fetch('/project/story/shots.json')).json();
const smooth=x=>ease.inOut(clamp(x));
for(const shot of story.shots.filter(s=>s.params.beat===0))registerShot(shot.id,{
 kind:'3d',init(T){return world(T);},
 draw(s,t,info,T){
  const time=info.globalT,u=time/20.16,H=T.THREE,k=smooth(time/3.5),reach=smooth((time-2.8)/1.4),lift=smooth((time-7.6)/3.2);
  const x=-2.7+2.05*k,z=.83;
  // Contact motion uses one global clock across all camera cuts.
  const theta=.9*smooth((time-4.2)/2.5),down=smooth((time-6.7)/.9);
  const grip=[.16,1.3+.48*Math.sin(theta),.145+.48*Math.cos(theta)-z];
  const pickup=[.45,1.27,-.3],hold=[.32,1.28,.10];
  const hand=grip.map((v,i)=>{const resting=[.05,.94,.19][i];const opening=resting+(v-resting)*reach;const picked=opening+(pickup[i]-opening)*down;return picked+(hold[i]-picked)*lift;});
  s.nico.update({x,z,time,yaw:0,headYaw:-.35,moving:time<3.5,distance:2.05*k,hand,handB:[.09,.9,-.19],expr:time>10?'sad':'smile',nod:-.10*lift});
  s.lid.rotation.x=-theta;
  const h=s.nico.point();s.photo.visible=time>=7.6;
  s.photo.position.copy(h);s.photo.position.y+=.08;s.photo.rotation.set(-.1,.25,.06);
  s.box.visible=true;
  const cam=info.cam,v=smooth(info.p),head=s.nico.head.getWorldPosition(new H.Vector3());
  let target=new H.Vector3(x+.45,1.05,z-.2),off=new H.Vector3(3.7,2.1,5.3),fov=42;
  if(cam==='hands'){target.set(-.23,1.16,.45);off.set(1.4,1.25,1.75);fov=37;}
  if(cam==='track'){target.copy(h).lerp(head,.35);off.set(1.3,.6,2.4);fov=37;}
  if(cam==='close'){target.copy(head);off.set(1.5,.18,2.0);fov=34;}
  if(cam==='orbit'){const a=.3+.4*v;off.set(5.3*Math.sin(a),1.8,5.3*Math.cos(a));target.set(-.3,1.16,.5);fov=42;}
  off.multiplyScalar(1-.04*v);s.stage.camera.position.copy(target).add(off);s.stage.camera.lookAt(target);s.stage.camera.fov=fov;s.stage.camera.updateProjectionMatrix();
 },
 overlay(g,t,info){
  const a=smooth((info.globalT-.3)/1)*smooth((19.8-info.globalT)/1);g.save();g.globalAlpha=a;
  g.fillStyle='#18343b';rr(g,1120,78,640,100,22);g.fill();text(g,'300 ANOS DEPOIS',1440,128,{size:43,color:'#ffe6b2',align:'center'});g.restore();
 }
});
