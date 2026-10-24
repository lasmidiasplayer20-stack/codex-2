import assert from'node:assert/strict';import{open}from'./browser.mjs';import{mkdir,writeFile}from'node:fs/promises';import{resolve}from'node:path';
const out=process.env.RAIN_QA_DIR||resolve(import.meta.dirname,'../qa/full');await mkdir(out,{recursive:true});const b=await open();try{
 const points=await b.page.evaluate(()=>film.timings.flatMap((c,j)=>film.chapters[j].beats.flatMap((a,k)=>[.12,.48,.84].map(q=>({t:c.start+(c.end-c.start)*(k+q)/8,action:a[0],q}))).filter(p=>p.t>=60)));
 const results=[];let error=0;for(const [i,p]of points.entries()){
  const r=await b.page.evaluate(t=>{const r=film.draw(t);let e=0;for(const rig of[film.walker,film.runner])for(const l of rig.limbs)for(const[n,L]of[['upper',.34],['lower',.32],['thigh',.52],['shin',.52]])e=Math.max(e,Math.abs(l[n].scale.y-L));return{...r,fixedSegmentError:e};},p.t);
  assert(r.cameraPosition.every(Number.isFinite));assert(r.fixedSegmentError<1e-7);if(p.action==='dry_friend'&&p.q===.48)assert(r.contact,'Towel handoff contact missing');if(r.contact)assert(r.handDistance<.025,JSON.stringify(r));error=Math.max(error,r.fixedSegmentError);results.push(r);
  if(p.q===.48){const data=await b.page.evaluate(()=>document.querySelector('#output').toDataURL('image/jpeg',.9).split(',')[1]);await writeFile(resolve(out,`${String(i).padStart(3,'0')}-${p.action}.jpg`),Buffer.from(data,'base64'));}
 }
 assert.equal(b.errors.length,0);await writeFile(resolve(out,'inspection.json'),JSON.stringify({samples:results.length,maximumSegmentError:error,pageErrors:b.errors,results},null,2));console.log('PASS',results.length,'full episode pose/camera/contact samples; fixed segments',error);
}finally{await b.close();}
