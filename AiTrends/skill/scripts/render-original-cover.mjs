// Original rounded-character variant; same bundled renderer license.
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
    // Dedicated original rounded-cast cover. This hook does not affect the video.
    for(const group of Object.values(s.sets))group.visible=false;
    if(!s.coverRig){s.coverRig=true;s.coverFront=new H.PointLight('#a4f7ff',14,12,2);s.coverRim=new H.PointLight('#ff64c9',18,12,2);s.scene.add(s.coverFront,s.coverRim);
      const g=new H.Group();s.scene.add(g);s.box(g,'#6a4878',[0,1.3,-1.1],[2.5,2.6,.22]);s.box(g,'#18283e',[0,1.45,-.95],[1.8,1.25,.14]);s.box(g,'#edbc74',[0,.87,-.78],[1.95,.13,.6]);s.panel(g,2.2,.42,[0,2.49,-.94],['COMPRA DE PRÊMIOS'],['#ffe572']);s.coverBooth=g;s.box(g,'#142447',[0,-.1,0],[18,.2,12]);for(const x of [-1.2,1.2])s.box(g,x<0?'#5feaff':'#ff67ca',[x,1.4,-.90],[.04,2.4,.035],true);for(let i=0;i<20;i++)s.ball(g,i%2?'#e1af51':'#7658aa',[(i%7-3)*.7,.3+Math.floor(i/7)*.8,-2.2],.035,true);
    }
    s.actors.nico.update({time:1,x:0,y:0,z:.5,yaw:-Math.PI/2,headYaw:.08,moving:false,expr:'surprised',hand:[.25,1.37,.18]});s.actors.nico.root.visible=true;s.actors.lia.root.visible=false;s.actors.courier.root.visible=false;
    s.special.visible=true;s.special.position.copy(s.actors.nico.point());s.special.position.y+=.085;s.special.rotation.y=.2;s.special.scale.setScalar(1.8);
    s.cash.visible=true;s.cash.position.set(.72,1.0,-.3);s.cash.scale.setScalar(2.3);s.cash.rotation.y=.1;
    s.scene.background.set('#101e3b');s.hemi.intensity=.8;s.sun.intensity=.60;
    s.coverFront.position.set(2,3,3);s.coverRim.position.set(-2,2,-1);
    s.camera.position.set(1.35,2.4,4.8);s.camera.lookAt(0,1.38,.18);s.camera.fov=43;
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
