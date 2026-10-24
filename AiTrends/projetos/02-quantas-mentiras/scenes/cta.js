// Original vector CTA. No raster assets, stock footage, platform API or remote calls.
import {E,clamp,ease,prog,text,seg,circle,alpha,rr} from '/engine/core.js';
function box(g,x,y,w,h,color,r){rr(g,x,y,w,h,r);g.fillStyle=color;g.fill();}
function bell(g,x,y,t,active){
 g.save();g.translate(x,y);g.rotate(active?Math.sin(t*25)*.16*Math.exp(-t*3):0);g.strokeStyle=active?'#f2cc62':'#e8edf5';g.fillStyle=active?'#f2cc62':'#e8edf5';g.lineWidth=4;g.lineCap='round';
 g.beginPath();g.moveTo(-15,10);g.quadraticCurveTo(-12,5,-12,-7);g.bezierCurveTo(-12,-24,12,-24,12,-7);g.quadraticCurveTo(12,5,15,10);g.closePath();g.stroke();circle(g,0,17,3,g.fillStyle);circle(g,0,-24,3,g.fillStyle);
 if(active){for(const s of [-1,1]){g.beginPath();g.arc(0,-5,25,s<0?2.5:-.65,s<0?3.8:.65);g.stroke();}}g.restore();
}
function cursor(g,x,y,s=1){g.save();g.translate(x,y);g.scale(s,s);g.beginPath();g.moveTo(0,0);g.lineTo(0,38);g.lineTo(10,28);g.lineTo(20,47);g.lineTo(28,43);g.lineTo(18,25);g.lineTo(33,24);g.closePath();g.lineWidth=4;g.strokeStyle='#121b2d';g.stroke();g.fillStyle='#fff';g.fill();g.restore();}
export const WINDOWS=[{start:43,end:51,label:'Curtiu a hipótese?'},{start:246,end:254,label:'Tem mais no Então'},{start:485,end:499.4,label:'Qual seria a sua pergunta?'}];
export function drawCTA(g,globalT){
 const w=WINDOWS.find(x=>globalT>=x.start&&globalT<x.end);if(!w)return;
 const t=globalT-w.start,d=w.end-w.start,enter=ease.out(clamp(t/.6)),exit=ease.in(clamp((t-(d-.5))/.5));
 const x=E.W/2-485,y=E.H-147+(1-enter+exit)*190;
 const clicked=t>2.8,ringT=t-4.1;
 g.save();g.globalAlpha=(1-exit);g.translate(x,y);g.shadowColor='#0008';g.shadowBlur=24;
 box(g,0,0,970,112,'#0d172bef',27);g.shadowBlur=0;g.strokeStyle='#41526d';g.lineWidth=2;g.stroke();
 circle(g,65,56,36,'#f0c34a');text(g,'E',65,56,{size:47,color:'#142037',weight:700});
 text(g,'Então',123,40,{size:40,color:'#f4eddc',align:'left'});text(g,w.label,125,82,{size:23,font:'Nunito',color:'#bdcbe1',align:'left'});
 const pulse=clicked?1-.07*Math.exp(-(t-2.8)*13):1;g.save();g.translate(632,56);g.scale(pulse,pulse);box(g,-162,-32,324,64,clicked?'#253a52':'#d74744',16);text(g,clicked?'✓ INSCRITO':'INSCREVA-SE',0,0,{size:29,color:'#fff',font:'Nunito',weight:900});g.restore();
 bell(g,875,54,Math.max(0,ringT),ringT>0);
 if(t>1.3&&t<5.5){const q=ease.inOut(prog(t,1.3,2.7)),bx=632+(t>3.3?ease.inOut(prog(t,3.3,4.05))*240:0);cursor(g,bx+(1-q)*100,58+(1-q)*100,.85);}
 if(t>2.8&&t<3.35){const q=prog(t,2.8,3.35);g.strokeStyle=alpha('#ffdf8a',1-q);g.lineWidth=4;g.beginPath();g.arc(632,56,30+q*43,0,Math.PI*2);g.stroke();}
 g.restore();
}
