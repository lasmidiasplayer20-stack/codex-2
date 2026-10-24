import{open}from'./browser.mjs';import{spawn}from'node:child_process';import{once}from'node:events';import{mkdir,writeFile}from'node:fs/promises';import{resolve,dirname}from'node:path';
const args=Object.fromEntries(process.argv.slice(2).reduce((a,x,i,all)=>x.startsWith('--')?[...a,[x.slice(2),all[i+1]]]:a,[]));
const start=Number(args.start||0),duration=Number(args.duration||60),fps=24,output=resolve(args.output||'renders/part-01.mp4');await mkdir(dirname(output),{recursive:true});
const b=await open();let ff;try{
 const ffargs=['-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','mjpeg','-r',String(fps),'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-r',String(fps),'-movflags','+faststart','-y',output];ff=spawn('ffmpeg',ffargs,{stdio:['pipe','ignore','pipe']});let stderr='';ff.stderr.on('data',x=>stderr+=x);let pipeError;ff.stdin.on('error',e=>pipeError=e);const completion=new Promise(r=>ff.on('close',r));
 const frames=Math.round(duration*fps),started=Date.now();
 for(let i=0;i<frames;i++){
  if(pipeError)throw pipeError;
  const data=await b.page.evaluate(t=>{film.draw(t);return document.querySelector('#output').toDataURL('image/jpeg',.96).split(',')[1];},start+i/fps);
  if(!ff.stdin.write(Buffer.from(data,'base64')))await once(ff.stdin,'drain');
  if(i%96===0)console.log(JSON.stringify({output,frame:i,total:frames,percent:+(i/frames*100).toFixed(1),elapsedSeconds:Math.round((Date.now()-started)/1000),fps:+((i+1)/((Date.now()-started)/1000)).toFixed(2)}));
 }
 ff.stdin.end();const exit=await completion;if(exit!==0)throw Error('ffmpeg '+exit+': '+stderr);if(b.errors.length)throw Error(JSON.stringify(b.errors));
 await writeFile(output+'.json',JSON.stringify({start,duration,fps,width:1920,height:1080,frames,errors:b.errors,renderElapsedSeconds:(Date.now()-started)/1000},null,2));console.log('COMPLETE '+output);
}finally{if(ff&&!ff.killed)ff.kill();await b.close();}
