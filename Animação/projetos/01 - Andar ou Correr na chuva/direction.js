import {opening,openingCamera} from './opening.js';
// R3: motion phrases with preparation, accent and recovery; all coordinates are procedural.
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x);},lerp=(a,b,t)=>a+(b-a)*t;
const running=new Set(['launch','arrive','walk_test','run_test','walk_through','run_through','lean_headwind','chase_umbrella','tailwind_walk','side_by_side','jump_puddle','careful_steps','simultaneous_start','repeat_trial','go_together','enter_shelter']);
export function direct(st,t){const {A,B,q,local,length,action}=st;st.lab=[1,2,3,7].includes(st.chapter);st.split=['walk_test','run_test','equal_distance','simultaneous_start','repeat_trial','compare_buckets','compare_clocks','hands_compare'].includes(action);
 // Keep gestures stable; authored actions supply their preparation and recovery.
 for(const a of [A,B]){a.headRoll=a.headRoll||0;a.headPitch=a.headPitch||0;if(a.speed>.2)a.bend=(a.bend||0)+(a.speed>1.15?.10:.02);}
 // A high five is an approach, a brief contact and a release, not six seconds of joined hands.
 if(action==='high_five'){
  const meet=[8.9,1.7,0],envelope=ease((q-.10)/.26)*(1-ease((q-.64)/.26));st.contact=q>=.36&&q<=.64;
  for(const [a,side]of[[A,-1],[B,1]]){a.contact={left:[meet[0]+side*(1-envelope)*.40,lerp(1.10,meet[1],envelope),0]};a.hands.right=[.35,1.1+.2*envelope,.16];a.expression=q>.34?'laugh':'neutral';a.y=.055*Math.sin(envelope*Math.PI);}
 }
 if(action==='steady_friend'){
  const e=ease(q/.3);A.tilt=-.22*(1-e);A.y=-.06*(1-e);A.headRoll=.10*(1-e);A.expression=q<.25?'shock':'laugh';B.expression=q<.18?'shock':'laugh';
 }
 if(action==='drops'){A.expression=q<.18?'neutral':q<.6?'shock':'laugh';A.headPitch=q<.25?.25:-.20;B.headPitch=-.28*ease(q*2);}
 if(action==='look_up'){A.headPitch=-.35+.14*Math.sin(local*2);B.headPitch=-.30;A.hands.left=[-.30,1.0+.8*ease(q*2),.25];}
 if(action==='challenge'){A.yaw=.42+.15*Math.sin(local*1.6);B.yaw=-.42;A.expression=q>.6?'laugh':'neutral';B.expression=q>.35?'laugh':'shock';}
 if(action==='splash_friend'){B.headRoll=-.13*Math.sin(q*Math.PI);B.tilt=-.12*ease(q*4);B.expression=q<.13?'neutral':'shock';A.expression=q<.25?'laugh':'shock';}
 if(action==='apologize'){A.headPitch=.18+.08*Math.sin(local*3);B.headPitch=-.05+.12*ease(q*2);B.expression=q>.55?'laugh':'annoyed';}
 if(['walk_test','run_test','simultaneous_start','repeat_trial'].includes(action)){
  for(const [i,a]of[A,B].entries()){const duration=i?.5:.95,p=clamp(q/duration),f=ease(p);a.x=-3+6*f;a.z=i?-.8:.8;a.yaw=Math.PI/2;a.distance=6*f;a.speed=p>0&&p<1?36*p*(1-p)/(length*duration):0;a.hands={};a.look=-.25;a.wet=i?Math.min(.45,q*.9):q*.9;}
 }
 st.performer=['run_test','run_through','umbrella_open','umbrella_flip','chase_umbrella','wring_hem','write_result'].includes(action)?'B':'A';
 return opening(st,t);
}
export function cameraPlan(st,t,aspect=16/9,solo=null){
 if(st.pilot)return openingCamera(st,t,aspect);
 const d=st.local,sub=Math.min(2,Math.floor(d/2.15)),u=clamp((d-sub*2.15)/2.15),p=ease(u),A=st.A,B=st.B,hero=st.performer==='B'?B:A,reaction=st.performer==='B'?A:B;
 let focus=solo||((sub===1&&!st.split)?hero:(sub===2&&!st.contact&&!st.split)?reaction:null),fx=focus?focus.x:(A.x+B.x)/2,fz=focus?focus.z:(A.z+B.z)/2,ly=focus?1.4:1.25;
 let radius=focus?5.25:Math.max(8.0,Math.abs(A.x-B.x)*1.25+5.4),cy=focus?2.7:4.2,angle=[-.38,.42,-.50,.26][(st.index+sub)%4],fov=42,roll=0;
 if(sub===0){angle+=.20*p;radius*=1-.10*p;}else if(sub===1){angle+=.32*p;radius*=1-.12*p;cy-=.22*p;}else{angle-=.22*p;radius*=1-.07*p;}
 if(st.camera==='orbit'){focus=null;fx=(A.x+B.x)/2;fz=(A.z+B.z)/2;radius=8.0;angle=-.65+st.q*1.25;cy=3.4;}
 if(st.camera==='feet'&&sub!==2){focus=st.action==='jump_puddle'?A:hero;fx=focus.x;fz=focus.z;ly=.55;cy=1.25;radius=5.3;angle=.35+.2*p;}
 if(hero.speed>.2&&!solo){angle=Math.max(-1,Math.min(1,hero.yaw*.65))+.10*p;}
 if(st.camera==='faces'&&sub!==0){radius=3.7;cy=2.35;ly=1.78;}
 if(st.camera.includes('hands')&&sub===1){radius=4.3;cy=2.7;ly=1.3;}
 if(st.camera==='overhead'&&sub===0){cy=9.5;radius=5.7;ly=.35;angle=-.1+.25*p;}
 if(st.camera==='shelter_wide'&&sub===0){fx=4.5;fz=.5;radius=16.5;cy=6;ly=1.1;angle=-.30+.12*p;}
 if(st.camera==='umbrella'){ly=1.65;cy=3.8;radius=sub===1?6.7:8.3;focus=null;fx=(A.x+B.x)/2;fz=(A.z+B.z)/2;angle=.22+.28*p;}
 if(st.action==='splash_friend'){radius=sub===1?4.8:7.5;cy=2.6;ly=1.1;angle=.28+.18*p;fx=sub===2?B.x:(A.x+B.x)/2;fz=.5;roll=Math.sin(st.q*Math.PI)*.018;}
 if(st.contact){focus=null;fx=(A.x+B.x)/2;fz=(A.z+B.z)/2;radius=7.2-.4*p;cy=2.8;ly=1.4;angle=.1+.25*p;}
 if(st.camera.startsWith('shelter_')&&st.camera!=='shelter_wide'){angle=.12+.18*p;}
 if(solo){fx=solo.x;fz=solo.z;radius=6.0-.35*p;cy=3.0;ly=1.2;angle=Math.max(-1,Math.min(1,solo.yaw*.65))+.08*p;fov=40;}
 if(st.action==='drops'&&d<1.05){const target=[A.x+.25,3.65-.75*d,A.z+.2];return{position:[target[0]+.15,target[1]+.12,target[2]+1.15],target,fov:42,roll:0,sub:0,aspect,mode:'macro-drop'};}
 if(st.action==='splash_friend'){const impact=d-.85;if(impact>0&&impact<.45)roll+=Math.sin(impact*48)*.035*Math.exp(-impact*7);}
 return{position:[fx+Math.sin(angle)*radius,cy,fz+Math.cos(angle)*radius],target:[fx,ly,fz],fov,roll,sub,aspect,mode:solo?'comparison':sub===0?'establish':sub===1?'action':'reaction'};
}
