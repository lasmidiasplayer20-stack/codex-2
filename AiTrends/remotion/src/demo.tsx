import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
// Frame-driven SVG example: no timers or unseeded randomness. It is a 2D demonstration.
const limb=(ax:number,ay:number,bx:number,by:number,color:string,width:number,key:string)=><g key={key}><path d={`M${ax} ${ay}L${bx} ${by}`} stroke="#101a32" strokeWidth={width+12} strokeLinecap="round"/><path d={`M${ax} ${ay}L${bx} ${by}`} stroke={color} strokeWidth={width} strokeLinecap="round"/></g>;
const DemoActor: React.FC<{phase:number}>=({phase})=>{
 const feet=[Math.sin(phase)*45,-Math.sin(phase)*45],knees=feet.map(x=>x*.45+22);
 return <g transform="translate(540 1010)">
  <ellipse cx="0" cy="380" rx="155" ry="25" fill="#0d1e3c" opacity=".45"/>
  {[0,1].map(i=><g key={i}>{limb(i?37:-37,90,knees[i]+(i?30:-30),225,'#17233e',24,`thigh${i}`)}{limb(knees[i]+(i?30:-30),225,feet[i]+(i?35:-35),360,'#17233e',24,`shin${i}`)}<ellipse cx={feet[i]+(i?35:-35)} cy={365-Math.max(0,Math.sin(phase+i*Math.PI))*22} rx="45" ry="18" fill="#e3fff1" stroke="#102239" strokeWidth="7"/></g>)}
  <path d="M-85-110Q0-140 85-110L100 110Q0 155-100 110Z" fill="#2ac9b4" stroke="#11203b" strokeWidth="10"/>
  <path d="M0-90V105M-52 53H52" stroke="#defff0" strokeWidth="8" strokeLinecap="round"/>
  {limb(-75,-95,-130,-10-Math.sin(phase)*14,'#2ac9b4',38,'armL1')}{limb(-130,-10-Math.sin(phase)*14,-120,87,'#2ac9b4',35,'armL2')}
  {limb(75,-95,130,-38,'#2ac9b4',38,'armR1')}{limb(130,-38,175,-115+Math.sin(phase*.5)*8,'#2ac9b4',35,'armR2')}
  <circle cx="-120" cy="87" r="25" fill="#0c172b"/><circle cx="175" cy={-115+Math.sin(phase*.5)*8} r="25" fill="#0c172b"/>
  <circle cy="-265" r="135" fill="#0a1020" stroke="#e8f4bf" strokeWidth="8"/>
  <ellipse cx="-45" cy="-280" rx="20" ry="27" fill="#fff9df"/><ellipse cx="45" cy="-280" rx="20" ry="27" fill="#fff9df"/>
  <path d="M-45-220Q0-183 45-220" fill="none" stroke="#fff9df" strokeWidth="9" strokeLinecap="round"/>
 </g>;
};
export const EntaoDemo: React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps;
 const camera=interpolate(frame,[0,120,239],[1,1.10,1.03],{easing:Easing.inOut(Easing.cubic)}),drift=Math.sin(t*.45)*22;
 const cards=['CÂMERA','MOVIMENTO','ÁUDIO'];
 return <AbsoluteFill style={{background:'#162845'}}>
 <svg viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="sky" x2="0" y2="1"><stop stopColor="#10234c"/><stop offset="1" stopColor="#9d5db5"/></linearGradient><linearGradient id="ground" x2="0" y2="1"><stop stopColor="#395c74"/><stop offset="1" stopColor="#162a46"/></linearGradient></defs>
  <rect width="1080" height="1920" fill="url(#sky)"/>
  <g transform={`translate(${540+drift} 1040) scale(${camera}) translate(-540 -1040)`}>
   {Array.from({length:9},(_,i)=><g key={i} transform={`translate(${i*155-120-drift*.3} ${480+(i%3)*70})`}><rect width="143" height="650" rx="9" fill={['#607dab','#9073ba','#4e929e'][i%3]} stroke="#203551" strokeWidth="7"/>{[0,1,2,3,4].map(j=><rect key={j} x={25+j%2*63} y={60+Math.floor(j/2)*115} width="34" height="57" fill="#ffe4a0"/>)}</g>)}
   <path d="M0 1160H1080V1920H0Z" fill="url(#ground)"/><path d="M0 1560L1080 1430M0 1750L1080 1590" stroke="#588993" strokeWidth="8"/>
   <DemoActor phase={t*3.2}/>
   {Array.from({length:12},(_,i)=><circle key={i} cx={100+(i*83)%900} cy={560+Math.sin(t*.8+i*1.8)*40+(i%3)*140} r={4+i%3*2} fill={i%2?'#ffd871':'#67eee1'} opacity=".65"/>)}
  </g>
  <text x="540" y="220" textAnchor="middle" fontFamily="sans-serif" fontWeight="900" fontSize="80" fill="#fff8e5" stroke="#0d1932" strokeWidth="3">ENTÃO + REMOTION</text>
  <text x="540" y="310" textAnchor="middle" fontFamily="sans-serif" fontWeight="700" fontSize="48" fill="#ffe17f">Animação controlada por código</text>
  {cards.map((word,i)=>{const a=interpolate(frame,[i*24+12,i*24+25],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});return <g key={word} opacity={a} transform={`translate(${90+i*310} ${1640+30*(1-a)})`}><rect width="280" height="100" rx="22" fill="#152b4c" stroke="#73dfd3" strokeWidth="5"/><text x="140" y="63" textAnchor="middle" fill="#fff1bc" fontSize="33" fontFamily="sans-serif" fontWeight="800">{word}</text></g>;})}
  <text x="540" y="1840" textAnchor="middle" fontSize="25" fontFamily="sans-serif" fill="#d7f9ed">DEMONSTRAÇÃO DO MOTOR • NÃO É O NOVO EPISÓDIO</text>
 </svg>
 </AbsoluteFill>;
};
