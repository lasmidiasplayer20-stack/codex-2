// Fixed-length two-bone IK. No Blender, assets, images or motion plugins.
const add=(a,b)=>a.map((v,i)=>v+b[i]),sub=(a,b)=>a.map((v,i)=>v-b[i]),mul=(a,s)=>a.map(v=>v*s),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),len=a=>Math.hypot(...a),norm=a=>mul(a,1/(len(a)||1));
export function solveJoint(root,target,l1,l2,pole){
 const delta=sub(target,root),axis=norm(delta),min=Math.sqrt(l1*l1+l2*l2-2*l1*l2*Math.cos(Math.PI*48/180)),max=Math.sqrt(l1*l1+l2*l2-2*l1*l2*Math.cos(Math.PI*165/180)),d=Math.max(min,Math.min(max,len(delta))),end=add(root,mul(axis,d));
 let bend=sub(pole,mul(axis,dot(pole,axis)));if(len(bend)<1e-5)bend=[1,0,0];bend=norm(bend);
 const along=(l1*l1-l2*l2+d*d)/(2*d),height=Math.sqrt(Math.max(0,l1*l1-along*along));return{joint:add(add(root,mul(axis,along)),mul(bend,height)),end,error:Math.abs(len(delta)-d)};
}
export function arcGesture(rest,target,origin,q){
 if(q<=0)return [...rest];if(q>=1)return [...target];const a=sub(rest,origin),b=sub(target,origin),na=norm(a),nb=norm(b),angle=Math.acos(Math.max(-.99999,Math.min(.99999,dot(na,nb)))),sin=Math.sin(angle),dir=angle<.001?norm(add(mul(na,1-q),mul(nb,q))):add(mul(na,Math.sin((1-q)*angle)/sin),mul(nb,Math.sin(q*angle)/sin));return add(origin,mul(dir,len(a)*(1-q)+len(b)*q));
}
