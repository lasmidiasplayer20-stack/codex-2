import assert from'node:assert/strict';import{open}from'./browser.mjs';import{writeFile,mkdir}from'node:fs/promises';
const b=await open();try{
 const checks=await b.page.evaluate(()=>{const out=[];for(let t=0;t<480;t+=13){const x=film.draw(t);out.push(x);}for(const c of film.timings){out.push(film.draw(c.start));out.push(film.draw(Math.min(479.99,c.end-.001)));}return{samples:out.length,finite:out.every(x=>Number.isFinite(x.time)&&x.chapter>=1&&x.chapter<=9),chapters:[...new Set(out.map(x=>x.chapter))],metrics:film.metrics};});assert(checks.finite);assert.equal(checks.chapters.length,9);assert.equal(checks.metrics.externalImages,0);
 await b.page.locator('#seek').fill('135');await b.page.locator('#seek').dispatchEvent('input');assert((await b.page.locator('#time').textContent()).startsWith('2:15'));
 await b.page.locator('#play').click();await b.page.waitForTimeout(350);await b.page.locator('#play').click();assert.equal(await b.page.locator('#play').textContent(),'Reproduzir');assert.equal(b.errors.length,0);
 await mkdir('qa',{recursive:true});await writeFile('qa/runtime.json',JSON.stringify({...checks,playPauseSeek:true,pageErrors:b.errors},null,2));console.log('PASS: all nine chapters, boundary coverage, finite timeline, procedural assets, play/pause/seek.');
}finally{await b.close();}
