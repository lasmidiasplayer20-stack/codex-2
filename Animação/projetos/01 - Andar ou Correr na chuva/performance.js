// Continue the approved procedural pilot: intentional gestures and explicit gait choices.
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x);};
const runningB=new Set(['run_test','run_through','chase_umbrella','simultaneous_start','repeat_trial']);
const walking=new Set(['walk_test','walk_through','lean_headwind','tailwind_walk','side_by_side','careful_steps','go_together','enter_shelter','spot_slip']);
const held=new Set(['line_up','start_clock','weigh_coats','write_result','agree_result','umbrella_open','umbrella_flip','chase_umbrella','catch_umbrella','wring_coat','wring_hem','drip_compare','wipe_face','wipe_and_laugh','dry_friend']);
export function perform(st,t){if(t<60)return st;
 const {A,B,action,local,length,q}=st;
 for(const [i,a]of[A,B].entries()){
  a.fullLengthOverlay=true;
  if(runningB.has(action))a.gaitRun=i===1;else if(walking.has(action))a.gaitRun=false;
  if(action==='jump_puddle')a.gaitRun=false;
  a.gestureStrength={};
  const attack=.45+i*.12,release=Math.max(attack+.5,length-.65);
  const strength=held.has(action)?1:ease(local/attack)*(1-ease((local-release)/.65));
  for(const side of Object.keys(a.hands||{}))a.gestureStrength[side]=strength;
 }
 if(action==='nod_agree'){const nod=Math.sin(Math.min(1,local/1.8)*Math.PI*2)*.12*(1-ease((local-1.8)/.7));A.headPitch=nod;B.headPitch=nod*.8;}
 if(action==='apologize'){A.headPitch=.15+.16*Math.sin(Math.min(1,local/1.6)*Math.PI);B.expression=q>.45?'laugh':'annoyed';}
 if(action==='splash_friend'){
  A.x=.6;A.y=.09*Math.exp(-local*5)*Math.sin(local*12);A.crouch=.4*Math.exp(-local*3);
  st.burst.start=.05;st.burstOnce=true;B.expression=local<.2?'neutral':'shock';
  for(const side of Object.keys(B.hands||{}))B.gestureStrength[side]=ease(local/.35)*(1-ease((local-length+.8)/.8));
 }
 if(action==='dry_friend'){
  A.yaw=.85;A.look=.65;B.look=-.40;B.armPoles={left:[-1,-.35,-.15]};
  const meet=[8.9,1.64,-.025],reach=ease((q-.12)/.30),release=1-ease((q-.57)/.30);
  A.hands={};B.hands={};A.contact={right:meet.slice()};A.contactStrength=reach*release;
  const wipe=ease((q-.57)/.20),hand=[-.07+.045*Math.sin(q*8),1.91,.34];
  const c=Math.cos(B.yaw),sn=Math.sin(B.yaw),face=[B.x+1.05*(hand[0]*c+hand[2]*sn),1.05*hand[1],B.z+1.05*(-hand[0]*sn+hand[2]*c)];
  B.contact={left:meet.map((v,i)=>v+(face[i]-v)*wipe)};B.contactStrength=reach;
  st.contact=q>=.42&&q<=.57;st.contactSides=['right','left'];st.props.towelHolder=q<.57?'A':'B';st.props.towelHand=q<.57?'right':'left';
  A.expression=B.expression='laugh';st.performer='B';
 }
 if(['walk_test','run_test','simultaneous_start','repeat_trial'].includes(action)){A.gaitRun=false;B.gaitRun=true;}
 return st;
}
