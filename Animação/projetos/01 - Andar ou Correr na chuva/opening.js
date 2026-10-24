// R4 pilot: original Three.js/Canvas pipeline and original toy-town aesthetics.
const clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
export const env=(t,a,b,c,d)=>smooth((t-a)/(b-a))*(1-smooth((t-c)/(d-c)));
function travel(t,start,D,v,r=.65){const u=t-start,duration=D/v+r;if(u<=0)return[0,0];if(u>=duration)return[D,0];if(u<r){const q=u/r;return[v*r*(q**3-.5*q**4),v*smooth(q)];}if(u>duration-r){const q=(duration-u)/r;return[D-v*r*(q**3-.5*q**4),v*smooth(q)];}return[v*(u-r/2),v];}
export function path(t,i){if(t<19){const[d,v]=travel(t,4,3.3,.7);return[-8.5+d,v,d];}if(t<50){const[d,v]=travel(t,i?19:19.5,i?14.6:14.25,i?1.75:.54);return[-5.2+d,v,3.3+d];}const[d,v]=travel(t,50.3,14,i?1.8:.72);return[-5+d,v,d];}
const cuts=[0,3,6,10,13,17,19,21,23.5,28,31,37,43,47,50,55,60];
const labels=['A primeira gota','A chuva apertou','O abrigo está adiante','E agora?','Ali tem abrigo','Vamos tentar?','Correr ou andar?','Opa, o respingo!','Um chega mais depressa','Fora da chuva','O caminho continua o mesmo','Cada passo conta','Quase lá','Chegar e encontrar o amigo','Mesmo ponto de partida','Mesma distância, velocidades diferentes'];
export function opening(st,t){if(t>=60)return st;st.pilot=true;st.lab=false;st.split=false;st.props={puddle:true};st.diagram=t>=50?'body':null;st.burst=null;st.contact=false;st.wind=0;const shot=cuts.findIndex((a,j)=>t>=a&&t<cuts[j+1]);st.pilotShot=shot;st.title=labels[shot];st.performer=t>=19&&t<31?'B':'A';
 for(const[i,a]of[st.A,st.B].entries()){const[x,v,d]=path(t,i);Object.assign(a,{gaitRun:i===1&&t>=19,x,z:i?-.65:.65,y:0,yaw:Math.PI/2,speed:v,distance:d,hands:{},contact:null,bend:i&&v>1?.10:0,headPitch:0,headRoll:0,look:0,tilt:0,wet:t<19?t*.008:i?.2:.2+(t-19)*.018,expression:'neutral'});a.look=(i?-.65:.65)*env(t,10,10.6,12.4,13.0);if(t<4)a.headPitch=-.18*env(t,1.7,2.2,2.8,3.6);}
 const A=st.A,B=st.B;
 if(t>=28.5&&t<50){B.yaw=Math.PI/2-Math.PI*smooth((t-28.5)/1.4);B.turnPivot=env(t,28.5,28.7,29.6,29.9);}
 if(t>=47&&t<50){A.look=B.look=.65*env(t,46.8,47.3,48.7,49.6);}
 function gesture(a,side,target,strength){if(strength<=0)return;a.hands[side]=target;a.gestureStrength={...(a.gestureStrength||{}),[side]:strength};}
 gesture(A,'left',[-.32,1.46,.45],env(t,.6,1.3,2.3,3.3));
 gesture(B,'left',[-.30,1.55,.54],env(t,13,13.7,15.8,16.8));
 B.bend+=.12*env(t,17,17.8,18.4,19.3);A.expression=t>10&&t<13?'shock':'neutral';
 gesture(A,'left',[-.14,1.85,.24],env(t,21.0,21.3,21.9,22.8));if(t>21&&t<23){A.expression='shock';B.look=.6*env(t,21,21.3,21.8,22.5);}
 if(t>=20.6&&t<22.0){st.burst={x:-2.4,y:.12,z:-.65,start:0,strength:1.3};st.pilotBurstAge=t-20.6;st.props.puddle=true;}
 if(t>=47&&t<49.8){const q=env(t,47,47.5,48.0,49.2);st.pilotGreeting=q;A.contact={right:[9.3,1.8,0]};B.contact={right:[9.3,1.8,0]};A.contactStrength=B.contactStrength=q;A.expression=B.expression='laugh';st.contact=q>.9;}
 st.action=t<3?'drops':t<19?'opening_decision':t<28?'opening_run':t<47?'opening_walk':t<50?'opening_greeting':'opening_comparison';return st;
}
export function openingCamera(st,t,aspect){const shot=st.pilotShot,A=st.A,B=st.B,u=(t-cuts[shot])/(cuts[shot+1]-cuts[shot]);let target,pos,fov=42;
 switch(shot){
 case 0:target=[A.x,2.05,.4];pos=[A.x+3.3,3.0,4.7];break;
 case 1:target=[A.x,1.7,0];pos=[A.x+4.1,3.5,7];break;
 case 2:target=[-6,1.35,0];pos=[-2,4.6,10];fov=40;break;
 case 3:target=[A.x,2.0,.25];pos=[A.x+2.6,2.9,5.7];break;
 case 4:target=[5.8,1.5,.2];pos=[A.x-1.5,3.3,4];fov=38;break;
 case 5:target=[B.x,1.35,0];pos=[B.x+3.7,3.6,8.7];break;
 case 6:target=[B.x+.3,1.35,-.45];pos=[B.x+2.6,2.9,7.8];break;
 case 7:target=[A.x,1.65,.5];pos=[A.x+3.3,3,6.7];break;
 case 8:{const angle=-.4+u*.75;target=[B.x+.3,1.4,-.65];pos=[B.x+Math.sin(angle)*8.5,4.1,B.z+Math.cos(angle)*8.5];break;}
 case 9:target=[9.2,1.35,0];pos=[13.5,3.7,8.3];break;
 case 10:target=[2,.4,0];pos=[2,13.5,9.5];fov=42;break;
 case 11:target=[A.x+.3,1.35,.4];pos=[A.x+3.4,3.1,7.7];break;
 case 12:target=[A.x+.3,1.35,.1];pos=[13,4.1,10];break;
 case 13:target=[9.25,1.7,0];pos=[12.7,3.7,7.4];break;
 case 14:target=[(A.x+B.x)/2,1.3,0];pos=[1,6,13.7];break;
 default:target=[1,1.2,0];pos=[3,7,18];fov=42;
 }
 pos=pos.map((v,i)=>v+(target[i]-v)*.035*u);return{position:pos,target,fov,roll:0,sub:shot,aspect,mode:'original-procedural-r4'};
}
