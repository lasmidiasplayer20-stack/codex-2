// Local aiTrends -> Remotion finishing bridge. Never invokes a voice API.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia} from '@remotion/renderer';
const here=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args={};const av=process.argv.slice(2);for(let i=0;i<av.length;i++){if(av[i].startsWith('--'))args[av[i].slice(2)]=av[i+1]&&!av[i+1].startsWith('--')?av[++i]:true;}
if(!args.project)throw new Error('Usage: npm run episode -- --project ../projetos/38-janela-pachinko [--video SILENT.mp4] [--from 0 --seconds 3] [--out FILE.mp4]');
const project=path.resolve(args.project),config=JSON.parse(fs.readFileSync(path.join(project,'config.json'),'utf8'));
if(config.aspect!=='9:16'||config.fps!==24)throw new Error('This first composition expects portrait/24 fps; add a different Composition for another format.');
const source=path.resolve(args.video||path.join(project,'exports',config.export_name)),audio=path.join(project,'audio/mix.mp3');for(const f of[source,audio])if(!fs.existsSync(f))throw new Error('Missing local media: '+f);
const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',source],{encoding:'utf8'}));const vid=probe.streams.find(s=>s.codec_type==='video');if(vid.width!==1080||vid.height!==1920||Math.abs(Number(probe.format.duration)-config.duration)>.08)throw new Error('Source dimensions/duration mismatch');
const workspace=path.join(here,'public/work',path.basename(project));fs.mkdirSync(workspace,{recursive:true});fs.copyFileSync(source,path.join(workspace,'source.mp4'));fs.copyFileSync(audio,path.join(workspace,'mix.mp3'));
const prefix='work/'+path.basename(project),inputProps={video:prefix+'/source.mp4',audio:prefix+'/mix.mp3',durationSeconds:config.duration,title:'',ctas:[]};
// Completed MP4 already includes CTAs. Muting its audio prevents double narration.
// With a silent source, author transparent CTA clips in the composition separately.
const serveUrl=await bundle({entryPoint:path.join(here,'src/index.ts'),publicDir:path.join(here,'public')});
const options={serveUrl,id:'EpisodeMontage',inputProps,browserExecutable:'/usr/bin/chromium'};const composition=await selectComposition(options);
const first=Math.round(Number(args.from||0)*24),last=args.seconds?first+Math.round(Number(args.seconds)*24)-1:composition.durationInFrames-1;
if(first<0||last>=composition.durationInFrames||last<first)throw new Error('Invalid frame range');
const output=path.resolve(args.out||path.join(here,'exports',path.basename(project)+'-remotion.mp4'));fs.mkdirSync(path.dirname(output),{recursive:true});
await renderMedia({...options,composition,codec:'h264',crf:20,concurrency:1,outputLocation:output,frameRange:[first,last],overwrite:true});
const qa={project:path.basename(project),composition:'EpisodeMontage',source:path.basename(source),range:[first,last],width:1080,height:1920,fps:24,audio:'Local published mix, no new TTS',output:path.basename(output),remotion:'4.0.539'};fs.writeFileSync(path.join(here,'qa',path.basename(project)+'-bridge.json'),JSON.stringify(qa,null,2));console.log('REMOTION_EPISODE',output);
