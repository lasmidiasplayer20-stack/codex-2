// Cover-only camera/light variant of local aiTrends renderer; same source license.
// Derived local adapter of bundled aiTrends render.mjs. Same engine/grade; direct canvas encoding avoids screenshot latency. Original kit licensing applies.
// render.mjs — deterministic frame renderer (headless Chromium -> ffmpeg), parallel workers.
//   node render.mjs --project projects/my-video                      full video  -> build/video_silent.mp4
//   node render.mjs --project P --from 30 --to 45 --scale 0.5         preview a range
//   node render.mjs --project P --sheet                               one still per shot -> build/sheets/*.png
//   node render.mjs --project P --stills 3.5,12,40                    stills at times -> build/stills
//   node render.mjs --project P --styles dusk,midnight,golden,neon --at 3.5,12,40   style comparison grid
// Options: --workers N  --scale K  --style ID  --debug  --format png|jpeg  --crf 18  --gl auto|gpu|swiftshader  --out FILE
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const KIT = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../aitrends-2d-studio/skills/make-2d-video/kit');
const {chromium} = createRequire(path.join(KIT,'package.json'))('playwright');

const ROOT = KIT;
const args = {}; { const a = process.argv.slice(2); for (let i = 0; i < a.length; i++) { if (a[i].startsWith('--')) { const k = a[i].slice(2); const v = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true; args[k] = v; } } }
if (!args.project) { console.error('usage: node render.mjs --project projects/<name> [options]'); process.exit(1); }
const PROJECT = path.resolve(args.project);
const BUILD = path.join(PROJECT, 'build'); fs.mkdirSync(BUILD, { recursive: true });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };

function listScenes(dir, base) { let out = []; if (!fs.existsSync(dir)) return out; for (const f of fs.readdirSync(dir).sort()) { const p = path.join(dir, f); if (fs.statSync(p).isDirectory()) out = out.concat(listScenes(p, `${base}/${f}`)); else if (f.endsWith('.js') && !f.startsWith('_')) out.push(`${base}/${f}`); } return out; }
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/__manifest') { res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }); return res.end(JSON.stringify(listScenes(path.join(PROJECT, 'scenes'), '/project/scenes'))); }
  if(url==='/engine/three-kit.js' && CFG.fast3D){const js=fs.readFileSync(path.join(ROOT,'engine/three-kit.js'),'utf8').replace('antialias: true','antialias: false');res.writeHead(200,{'Content-Type':'text/javascript','Cache-Control':'no-store'});return res.end(js);}
  if(url==='/engine/styles.js' && fs.existsSync(path.join(PROJECT,'runtime-style.json'))){const style=JSON.parse(fs.readFileSync(path.join(PROJECT,'runtime-style.json'),'utf8'));const js=fs.readFileSync(path.join(ROOT,'engine/styles.js'),'utf8')+'\nSTYLES.entaoSpeed={...STYLES.golden,name:"Então Speed",grade:'+JSON.stringify(style)+'};';res.writeHead(200,{'Content-Type':'text/javascript','Cache-Control':'no-store'});return res.end(js);}
  if(args['ff-grade'] && url==='/engine/player.js'){const js=fs.readFileSync(path.join(ROOT,'engine/player.js'),'utf8').replace('applyGrade(W, H);','/* grade applied by native FFmpeg LUT in encoder */').replace('if (grade.grain > 0)','if (false)');res.writeHead(200,{'Content-Type':'text/javascript','Cache-Control':'no-store'});return res.end(js);}
  if(url==='/project/scenes/film.js'){
    let source=fs.readFileSync(path.join(PROJECT,'scenes/film.js'),'utf8');
    const cover=`
    // Cover-only direction: original scene, separate camera/light, no video changes.
    if(!s.coverRig){s.coverRig=true;s.coverInks=[];for(const figure of [s.n,s.l]){const alpha=figure===s.n?(extra.opacity??1):1,ink=new H.MeshBasicMaterial({color:'#030716',side:H.BackSide,transparent:true,opacity:alpha});s.coverInks.push(ink);const meshes=[];figure.root.traverse(o=>{if(o.isMesh&&o.name)meshes.push(o);});for(const m of meshes){const hull=new H.Mesh(m.geometry,ink);hull.scale.setScalar(1.035);m.add(hull);if(m.name==='head'&&figure===s.n){const haloMaterial=new H.MeshBasicMaterial({color:'#39d9f0',side:H.BackSide,transparent:true,opacity:alpha});s.coverHeadInk=haloMaterial;const halo=new H.Mesh(m.geometry,haloMaterial);halo.scale.setScalar(1.075);m.add(halo);}}}
      s.coverFront=new H.PointLight('#d7f9ff',15,12,2);s.coverRim=new H.PointLight('#ff65c6',17,12,2);s.scene.add(s.coverFront,s.coverRim);}
    s.coverInks[0].opacity=extra.opacity??1;if(s.coverHeadInk)s.coverHeadInk.opacity=extra.opacity??1;s.coverInks[0].depthWrite=(extra.opacity??1)>.1;const center=s.n.root.position.clone(),heading=s.n.root.rotation.y+(s.n.head.rotation.y||0)*.5,front=new H.Vector3(Math.cos(heading),0,-Math.sin(heading)),side=new H.Vector3(Math.sin(heading),0,Math.cos(heading));
    const look=center.clone().add(new H.Vector3(0,1.30,0));s.camera.position.copy(look).addScaledVector(front,3.2).addScaledVector(side,1.8).add(new H.Vector3(0,1.3,0));s.camera.lookAt(look);s.camera.fov=43;
    if((cfg.theme===2||cfg.theme===6)&&!s.coverBall){s.coverBall=true;const cv=document.createElement('canvas');cv.width=cv.height=16;const cx=cv.getContext('2d');cx.fillStyle='#f98a30';cx.fillRect(0,0,16,16);cx.fillStyle='#442b29';cx.fillRect(7,0,2,16);cx.fillRect(0,7,16,2);for(let y=0;y<16;y++){const x=Math.round(2+2*Math.sin(y/15*Math.PI));cx.fillRect(x,y,1,1);cx.fillRect(15-x,y,1,1);}const tex=new H.CanvasTexture(cv);tex.colorSpace=H.SRGBColorSpace;tex.magFilter=tex.minFilter=H.NearestFilter;P.ball.material=new H.MeshLambertMaterial({map:tex,emissive:'#421000',emissiveIntensity:.25});}
    if(cfg.theme===6){const goal=center.clone().addScaledVector(front,-1.5).addScaledVector(side,.9);P.court.rotation.y=Math.PI;P.court.position.set(goal.x+2.6,0,goal.z-.5);}
    s.scene.background.set('#102040');s.hemi.color.set('#9cc6ff');s.hemi.groundColor.set('#241337');s.hemi.intensity=.72;s.sun.color.set('#e2efff');s.sun.intensity=.38;
    s.coverFront.position.copy(center).addScaledVector(front,2.1).addScaledVector(side,1.5).add(new H.Vector3(0,2.8,0));s.coverRim.position.copy(center).addScaledVector(front,-2).addScaledVector(side,-2).add(new H.Vector3(0,2.6,0));
    `;
    if(!source.includes('s.camera.updateProjectionMatrix();'))throw new Error('Unsupported scene camera hook');source=source.replace('s.camera.updateProjectionMatrix();',cover+'s.camera.updateProjectionMatrix();').replace('init,draw,overlay});','init,draw,overlay:()=>{}});');res.writeHead(200,{'Content-Type':'text/javascript','Cache-Control':'no-store'});return res.end(source);
  }
  const p = url.startsWith('/project/') ? path.join(PROJECT, url.slice(9)) : path.join(ROOT, url);
  if (!(p.startsWith(ROOT) || p.startsWith(PROJECT)) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); fs.createReadStream(p).pipe(res);
}).listen(0);
const PORT = server.address().port;
const gl = args.gl || (process.platform === 'linux' ? 'swiftshader' : 'auto');
const LAUNCH = { args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage', '--disable-accelerated-2d-canvas', ...(gl === 'swiftshader' ? ['--use-angle=swiftshader'] : []), ...(gl === 'gpu' ? ['--enable-gpu', '--use-angle=default'] : [])] };
const executable = process.env.CHROMIUM_EXECUTABLE_PATH || (fs.existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : null);
if (executable) LAUNCH.executablePath = executable;
const FORMAT = args.format === 'jpeg' ? 'jpeg' : 'png';
const CFG = JSON.parse(fs.readFileSync(path.join(PROJECT, 'config.json'), 'utf8'));
const FPS = CFG.fps || 24;

async function openPlayer(browser, style) {
  const qs = new URLSearchParams(); if (args.scale) qs.set('scale', args.scale); if (style || args.style) qs.set('style', style || args.style); if (args.debug) qs.set('debug', '1');
  const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  page.on('console', m => { const t = m.text(); if (/ERROR|missing/i.test(t)) console.log('[page]', t); });
  await page.goto(`http://localhost:${PORT}/player.html?${qs}`);
  await page.waitForFunction('window.READY === true || !!window.BOOT_ERROR', null, { timeout: 120000 });
  const boot = await page.evaluate('window.BOOT_ERROR'); if (boot) throw new Error('Player failed to boot: ' + boot);
  const [w, h] = await page.evaluate('window.OUT'); await page.setViewportSize({ width: w, height: h });
  return page;
}
const shot = async(page,f) => Buffer.from(await page.evaluate(({f,format}) => {window.renderFrame(f); return document.getElementById('main').toDataURL(format==='jpeg'?'image/jpeg':'image/png',.94).split(',')[1];},{f,format:FORMAT}),'base64');
const fmtT = s => `${Math.floor(s / 60)}m${String(Math.round(s % 60)).padStart(2, '0')}s`;











const browser=await chromium.launch(LAUNCH),page=await openPlayer(browser);const at=Number(args.at||0);const bytes=await shot(page,Math.round(at*FPS));const out=path.resolve(args.out||path.join(PROJECT,'build/cover-native.png'));fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,bytes);const errors=await page.evaluate('window.ERRORS');await browser.close();server.close();if(errors?.length)throw new Error(errors.join('\n'));console.log('COVER_NATIVE',out);
