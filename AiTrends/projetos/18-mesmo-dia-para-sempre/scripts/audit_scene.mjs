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
const KIT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../aitrends-2d-studio/skills/make-2d-video/kit');
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











const browser=await chromium.launch(LAUNCH),page=await openPlayer(browser),story=JSON.parse(fs.readFileSync(path.join(PROJECT,'story/shots.json'))),records=[];
for(const sh of story.shots)for(const frac of [.1,.35,.65,.9]){
 const sec=sh.start+(sh.end-sh.start)*frac;await page.evaluate(f=>window.renderFrame(f),Math.floor(sec*24));records.push(await page.evaluate(async({sec,cam})=>{const s=(await import('/project/scenes/film.js')).current,H=s.H;let all=[];s.scene.updateMatrixWorld(true);s.scene.traverse(o=>all.push(...o.matrixWorld.elements));const heads=Object.entries(s.actors).filter(([id,a])=>a.root.visible).map(([id,a])=>{const p=a.head.getWorldPosition(new H.Vector3()).project(s.camera);return{id,x:p.x,y:p.y,z:p.z};});const piano=cam==='piano'?['hand','handB'].map(k=>{const a=s.actors.nico.point(k);return Math.min(...s.keys.map(m=>{const p=m.getWorldPosition(new H.Vector3());p.y+=.0375;return Math.hypot(Math.max(0,Math.abs(a.x-p.x)-.054),a.y-p.y,Math.max(0,Math.abs(a.z-p.z)-.20));}));}):[];return {seconds:sec,cam,errors:window.ERRORS,finite:all.every(Number.isFinite),cup_contact:s.state.propContact,piano_key_distances:piano,pan_contact:cam==='cooking'?s.actors.nico.point().distanceTo(s.panHandle.getWorldPosition(new H.Vector3())):0,heads,nico:s.state.nico};},{sec,cam:sh.params.cam}));}
const errors=records.flatMap(x=>x.errors||[]),nonfinite=records.filter(x=>!x.finite).length,badCup=records.filter(r=>r.cup_contact>.001),badPan=records.filter(r=>r.pan_contact>.035),badKeys=records.filter(r=>r.piano_key_distances.some(x=>x>.095));
const result={sampled_frames:records.length,errors:[...new Set(errors)],nonfinite,cup_contact_failures:badCup.length,pan_contact_failures:badPan.length,key_reach_failures:badKeys.length,records,limits:'Sampled rendered integration/contacts, not complete collision/biomechanics simulation or perceptual review.'};fs.writeFileSync(path.join(PROJECT,'qa/scene-numeric-audit.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({samples:records.length,errors:errors.length,nonfinite,cup:badCup.length,pan:badPan.length,keys:badKeys.length}));await browser.close();server.close();if(errors.length||nonfinite||badCup.length||badPan.length||badKeys.length)process.exitCode=1;
