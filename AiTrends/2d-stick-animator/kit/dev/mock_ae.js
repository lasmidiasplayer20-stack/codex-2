/* Mock After Effects object model for dry-running ra_engine.jsx in Node (no After Effects needed).
   It catches JavaScript errors in the engine, invalid property paths in our own code, expression syntax errors
   (every expression string is parsed), ease-array mistakes, and lets us evaluate the rig expressions to compare
   them with the Python rig.
     node kit/dev/mock_ae.js <project_dir> [--kit <kit_dir>] [--parity]
   Exit code 1 when the build logged ERRORs or an expression fails to parse. It is a mock: effect parameter
   indices and names are accepted permissively, so a real After Effects test is still required. */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
let acorn = null;
try { acorn = require("acorn"); } catch (e) { try { acorn = require(path.join(process.cwd(), "node_modules", "acorn")); } catch (e2) {} }

const args = process.argv.slice(2);
const projectDir = path.resolve(args[0] || ".");
const kitDir = path.resolve(args.indexOf("--kit") >= 0 ? args[args.indexOf("--kit") + 1] : path.join(__dirname, ".."));
const PARITY = args.indexOf("--parity") >= 0;
const EXPR = [];
const STATS = { layers: 0, comps: 0, keys: 0, expressions: 0, effects: 0 };

const KIT_ = { LINEAR: 6612, BEZIER: 6613, HOLD: 6614 };
const SPATIAL = new Set(["ADBE Position", "ADBE Anchor Point", "ADBE Point Control-0001", "ADBE Vector Position", "ADBE Vector Anchor"]);

function imgSize(p) {
  try {
    const b = fs.readFileSync(p);
    if (b[0] === 0x89 && b[1] === 0x50) return [b.readUInt32BE(16), b.readUInt32BE(20)];
    if (b[0] === 0xff && b[1] === 0xd8) {
      let i = 2;
      while (i < b.length) {
        if (b[i] !== 0xff) { i++; continue; }
        const m = b[i + 1], len = b.readUInt16BE(i + 2);
        if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)];
        i += 2 + len;
      }
    }
  } catch (e) {}
  return [1000, 1000];
}

class Prop {
  constructor(name, matchName, value, isGroup, parent, auto) {
    this.name = name; this.matchName = matchName || name; this._v = value === undefined ? 0 : value; this.isGroup = !!isGroup;
    this.parentProperty = parent || null; this._kids = []; this._keys = []; this._expr = ""; this._auto = !!auto;
    this.enabled = true; this.canSetExpression = !isGroup;
  }
  get value() { return this._keys.length ? this.valueAtTime(0) : this._v; }
  get numProperties() { return this._kids.length; }
  get numKeys() { return this._keys.length; }
  get expression() { return this._expr; }
  set expression(s) {
    this._expr = s; STATS.expressions++;
    let r = this; while (r.parentProperty) r = r.parentProperty;
    EXPR.push({ prop: this.path(), matchName: this.matchName, src: s, comp: r._layer ? r._layer.comp.name : "" });
  }
  path() { let p = this, out = []; while (p) { out.unshift(p.name); p = p.parentProperty; } return out.join(" > "); }
  property(x) {
    if (!this.isGroup) throw new Error("property() on non-group " + this.path());
    if (typeof x === "number") {
      if (x >= 1 && x <= this._kids.length) return this._kids[x - 1];
      if (this._auto) { while (this._kids.length < x) this._kids.push(new Prop("param" + (this._kids.length + 1), this.matchName + "-" + String(this._kids.length + 1).padStart(4, "0"), 0, false, this)); return this._kids[x - 1]; }
      throw new Error("no property index " + x + " in " + this.path());
    }
    for (const k of this._kids) if (k.name === x || k.matchName === x) return k;
    if (this._auto) { const k = new Prop(x, x, 0, false, this); this._kids.push(k); return k; }
    return null;
  }
  addProperty(mn) {
    if (!this.isGroup) throw new Error("addProperty on non-group");
    const p = makeProp(mn, this);
    this._kids.push(p);
    if (this.matchName === "ADBE Effect Parade") STATS.effects++;
    return p;
  }
  moveTo(i) { const par = this.parentProperty; const a = par._kids; a.splice(a.indexOf(this), 1); a.splice(i - 1, 0, this); }
  remove() { const a = this.parentProperty._kids; a.splice(a.indexOf(this), 1); }
  setValue(v) { if (v === undefined || (typeof v === "number" && isNaN(v))) throw new Error("setValue undefined/NaN on " + this.path()); checkDims(this, v); this._v = v; }
  setValueAtTime(t, v) { if (isNaN(t)) throw new Error("NaN time"); checkDims(this, v); this._keys = this._keys.filter(k => Math.abs(k.t - t) > 1e-6); this._keys.push({ t, v, it: KIT_.LINEAR, ot: KIT_.LINEAR }); this._keys.sort((a, b) => a.t - b.t); STATS.keys++; }
  setValuesAtTimes(ts, vs) { if (ts.length !== vs.length) throw new Error("times/values length mismatch " + this.path()); for (let i = 0; i < ts.length; i++) this.setValueAtTime(ts[i], vs[i]); }
  nearestKeyIndex(t) { let best = 1, d = 1e9; this._keys.forEach((k, i) => { if (Math.abs(k.t - t) < d) { d = Math.abs(k.t - t); best = i + 1; } }); if (!this._keys.length) throw new Error("no keys on " + this.path()); return best; }
  keyTime(i) { return this._keys[i - 1].t; }
  keyValue(i) { return this._keys[i - 1].v; }
  keyInInterpolationType(i) { this._k(i); return this._keys[i - 1].it; }
  keyOutInterpolationType(i) { this._k(i); return this._keys[i - 1].ot; }
  _k(i) { if (i < 1 || i > this._keys.length) throw new Error("bad key index " + i + " on " + this.path()); }
  setInterpolationTypeAtKey(i, a, b) { this._k(i); this._keys[i - 1].it = a; this._keys[i - 1].ot = b === undefined ? a : b; }
  setTemporalEaseAtKey(i, inE, outE) {
    this._k(i);
    const v = this._keys[i - 1].v, dims = Array.isArray(v) ? v.length : 1;
    const need = (SPATIAL.has(this.matchName) || this.matchName.indexOf("Point") >= 0) ? 1 : dims;
    if (inE.length !== need || outE.length !== need) throw new Error("ease length " + inE.length + " != " + need + " on " + this.path());
    for (const e of inE.concat(outE)) if (e.influence < 0.1 || e.influence > 100) throw new Error("influence out of range " + e.influence);
  }
  valueAtTime(t) {
    const K = this._keys; if (!K.length) return this._v;
    if (t <= K[0].t) return K[0].v;
    for (let i = 1; i < K.length; i++) if (t < K[i].t) {
      if (K[i - 1].ot === KIT_.HOLD || typeof K[i].v === "object" && !Array.isArray(K[i].v)) return K[i - 1].v;
      const u = (t - K[i - 1].t) / (K[i].t - K[i - 1].t), a = K[i - 1].v, b = K[i].v;
      return Array.isArray(a) ? a.map((x, j) => x + (b[j] - x) * u) : a + (b - a) * u;
    }
    return K[K.length - 1].v;
  }
}
function checkDims(p, v) {
  if (p._v && Array.isArray(p._v) && Array.isArray(v) && p.matchName !== "ADBE Vector Shape" && v.length < 2) throw new Error("bad dims on " + p.path());
}
class KeyframeEase { constructor(speed, influence) { this.speed = speed; this.influence = influence; } }
class Shape { constructor() { this.vertices = []; this.inTangents = []; this.outTangents = []; this.closed = true; } }
class TextDocument { constructor(t) { this.text = t; this.font = "ArialMT"; this.fontSize = 36; this.fillColor = [1, 1, 1]; this.applyFill = true; this.applyStroke = false; this.strokeColor = [0, 0, 0]; this.strokeWidth = 1; this.strokeOverFill = false; this.justification = 0; this.tracking = 0; } resetCharStyle() {} }

const GROUPS = new Set(["ADBE Vector Group", "ADBE Vectors Group", "ADBE Root Vectors Group", "ADBE Vector Transform Group", "ADBE Effect Parade", "ADBE Mask Parade", "ADBE Mask Atom", "ADBE Text Animators", "ADBE Text Animator", "ADBE Vector Graphic - Stroke", "ADBE Vector Graphic - Fill", "ADBE Vector Shape - Rect", "ADBE Vector Shape - Group", "ADBE Vector Shape - Ellipse", "ADBE Vector Filter - Merge", "ADBE Vector Filter - Trim"]);
function makeProp(mn, parent) {
  const isEffect = parent && parent.matchName === "ADBE Effect Parade";
  if (isEffect) {
    const names = { "ADBE Slider Control": "Slider Control", "ADBE Point Control": "Point Control", "ADBE Angle Control": "Angle Control" };
    let base = names[mn] || mn.replace("ADBE ", ""), nm = base, n = 1;
    while (parent._kids.some(k => k.name === nm)) { n++; nm = base + " " + n; }
    const fx = new Prop(nm, mn, 0, true, parent, true);
    if (mn === "ADBE Slider Control") fx._kids.push(new Prop("Slider", "ADBE Slider Control-0001", 0, false, fx));
    if (mn === "ADBE Point Control") fx._kids.push(new Prop("Point", "ADBE Point Control-0001", [0, 0], false, fx));
    return fx;
  }
  const g = new Prop(defaultName(mn, parent), mn, 0, GROUPS.has(mn), parent, false);
  if (mn === "ADBE Vector Group") {
    g._kids.push(new Prop("Contents", "ADBE Vectors Group", 0, true, g));
    const tg = new Prop("Transform", "ADBE Vector Transform Group", 0, true, g); g._kids.push(tg);
    for (const [n, m, v] of [["Anchor Point", "ADBE Vector Anchor", [0, 0]], ["Position", "ADBE Vector Position", [0, 0]], ["Scale", "ADBE Vector Scale", [100, 100]], ["Rotation", "ADBE Vector Rotation", 0], ["Opacity", "ADBE Vector Group Opacity", 100]]) tg._kids.push(new Prop(n, m, v, false, tg));
  }
  if (mn === "ADBE Vector Shape - Group") g._kids.push(new Prop("Path", "ADBE Vector Shape", new Shape(), false, g));
  if (mn === "ADBE Vector Shape - Rect") for (const [n, m, v] of [["Size", "ADBE Vector Rect Size", [100, 100]], ["Position", "ADBE Vector Rect Position", [0, 0]], ["Roundness", "ADBE Vector Rect Roundness", 0]]) g._kids.push(new Prop(n, m, v, false, g));
  if (mn === "ADBE Vector Shape - Ellipse") for (const [n, m, v] of [["Size", "ADBE Vector Ellipse Size", [100, 100]], ["Position", "ADBE Vector Ellipse Position", [0, 0]]]) g._kids.push(new Prop(n, m, v, false, g));
  if (mn === "ADBE Vector Graphic - Fill") for (const [n, m, v] of [["Color", "ADBE Vector Fill Color", [1, 1, 1, 1]], ["Opacity", "ADBE Vector Fill Opacity", 100]]) g._kids.push(new Prop(n, m, v, false, g));
  if (mn === "ADBE Vector Graphic - Stroke") for (const [n, m, v] of [["Color", "ADBE Vector Stroke Color", [1, 1, 1, 1]], ["Opacity", "ADBE Vector Stroke Opacity", 100], ["Stroke Width", "ADBE Vector Stroke Width", 2], ["Line Cap", "ADBE Vector Stroke Line Cap", 1], ["Line Join", "ADBE Vector Stroke Line Join", 1]]) g._kids.push(new Prop(n, m, v, false, g));
  if (mn === "ADBE Mask Atom") { g.inverted = false; for (const [n, m, v] of [["Mask Path", "ADBE Mask Shape", new Shape()], ["Mask Feather", "ADBE Mask Feather", [0, 0]], ["Mask Opacity", "ADBE Mask Opacity", 100]]) g._kids.push(new Prop(n, m, v, false, g)); }
  return g;
}
function defaultName(mn, parent) {
  const base = { "ADBE Vector Group": "Group", "ADBE Vector Shape - Group": "Path", "ADBE Vector Graphic - Fill": "Fill", "ADBE Vector Graphic - Stroke": "Stroke", "ADBE Vector Shape - Rect": "Rectangle Path", "ADBE Vector Shape - Ellipse": "Ellipse Path", "ADBE Vector Filter - Merge": "Merge Paths", "ADBE Mask Atom": "Mask" }[mn] || mn;
  let n = 1, nm = base + " " + n;
  while (parent && parent._kids.some(k => k.name === nm)) { n++; nm = base + " " + n; }
  return nm;
}

class Item { constructor(name) { this.name = name; this.parentFolder = null; this.id = ++Item.n; } }
Item.n = 0;
class FolderItem extends Item {}
class FootageItem extends Item {
  constructor(file) {
    super(path.basename(file)); this.file = file;
    const ext = path.extname(file).toLowerCase();
    if ([".png", ".jpg", ".jpeg", ".webp"].includes(ext)) { const s = imgSize(file); this.width = s[0]; this.height = s[1]; this.duration = 0; }
    else { this.width = 1080; this.height = 1920; this.duration = 8; }
  }
}
class Layer {
  constructor(comp, name, source, kind) {
    this.comp = comp; this.name = name; this.source = source || null; this.kind = kind; this.parent = null; this.enabled = true;
    this.inPoint = 0; this.outPoint = comp.duration; this.startTime = 0; this.blendingMode = 0; this.adjustmentLayer = false;
    this.timeRemapEnabled = false; this.audioEnabled = true; this.stretch = 100; this.motionBlur = false; STATS.layers++;
    this.root = new Prop(name, "ADBE Layer", 0, true, null); this.root._layer = this;
    const tr = new Prop("Transform", "ADBE Transform Group", 0, true, this.root); this.root._kids.push(tr);
    for (const [n, m, v] of [["Anchor Point", "ADBE Anchor Point", [0, 0, 0]], ["Position", "ADBE Position", [comp.width / 2, comp.height / 2, 0]], ["Scale", "ADBE Scale", [100, 100, 100]], ["Rotation", "ADBE Rotate Z", 0], ["Opacity", "ADBE Opacity", 100]]) tr._kids.push(new Prop(n, m, v, false, tr));
    this.root._kids.push(new Prop("Effects", "ADBE Effect Parade", 0, true, this.root));
    this.root._kids.push(new Prop("Masks", "ADBE Mask Parade", 0, true, this.root));
    if (kind === "shape") this.root._kids.push(new Prop("Contents", "ADBE Root Vectors Group", 0, true, this.root));
    if (kind === "text") {
      const tp = new Prop("Text", "ADBE Text Properties", 0, true, this.root); this.root._kids.push(tp);
      tp._kids.push(new Prop("Source Text", "ADBE Text Document", new TextDocument(" "), false, tp));
      tp._kids.push(new Prop("Animators", "ADBE Text Animators", 0, true, tp));
    }
    const au = new Prop("Audio", "ADBE Audio Group", 0, true, this.root); this.root._kids.push(au);
    au._kids.push(new Prop("Audio Levels", "ADBE Audio Levels", [0, 0], false, au));
    this.root._kids.push(new Prop("Time Remap", "ADBE Time Remapping", 0, false, this.root));
  }
  get name() { return this._name; }
  set name(n) { this._name = n; if (this.root) this.root.name = n; }
  property(x) { const p = this.root.property(x); if (!p) throw new Error("layer " + this.name + " has no property " + x); return p; }
  setParentWithJump(p) { if (p && p.comp !== this.comp) throw new Error("parent in another comp"); this.parent = p; }
  moveBefore(l) { this.comp._move(this, l, 0); }
  moveAfter(l) { this.comp._move(this, l, 1); }
  moveToBeginning() { const a = this.comp._layers; a.splice(a.indexOf(this), 1); a.unshift(this); }
  remove() { const a = this.comp._layers; a.splice(a.indexOf(this), 1); }
  duplicate() { const d = new Layer(this.comp, this.name + " 2", this.source, this.kind); this.comp._layers.unshift(d); return d; }
  setTrackMatte() {}
  get index() { return this.comp._layers.indexOf(this) + 1; }
}
class CompItem extends Item {
  constructor(name, w, h, par, dur, fps) {
    super(name);
    if (w !== Math.round(w) || h !== Math.round(h)) throw new Error("comp size must be integers: " + w + "x" + h);
    this.width = w; this.height = h; this.duration = dur; this.frameRate = fps; this.pixelAspect = par; this._layers = []; STATS.comps++;
    const self = this;
    this.layers = {
      addShape() { const l = new Layer(self, "Shape Layer", null, "shape"); self._layers.unshift(l); return l; },
      addNull(d) { const l = new Layer(self, "Null", { name: "Null" }, "null"); self._layers.unshift(l); return l; },
      addSolid(c, n, w, h, par, d) { if (w !== Math.round(w) || h !== Math.round(h)) throw new Error("addSolid size not integer"); if (!Array.isArray(c) || c.length < 3) throw new Error("solid colour"); const l = new Layer(self, n, { name: n, parentFolder: null }, "solid"); self._layers.unshift(l); return l; },
      addText(t) { const l = new Layer(self, String(t), null, "text"); l.property("ADBE Text Properties").property("ADBE Text Document")._v = new TextDocument(t); self._layers.unshift(l); return l; },
      add(item) { if (!item) throw new Error("layers.add(null)"); const l = new Layer(self, item.name, item, item instanceof CompItem ? "precomp" : "footage"); self._layers.unshift(l); return l; },
    };
  }
  get numLayers() { return this._layers.length; }
  layer(x) { if (typeof x === "number") return this._layers[x - 1]; const l = this._layers.find(l => l.name === x); if (!l) throw new Error("no layer " + x + " in " + this.name); return l; }
  _move(a, b, after) { const L = this._layers; L.splice(L.indexOf(a), 1); L.splice(L.indexOf(b) + after, 0, a); }
  openInViewer() {}
  saveFrameToPng(t, f) { fs.writeFileSync(f.fsName, ""); }
}
class MFile {
  constructor(p) { this.fsName = String(p && p.fsName ? p.fsName : p).replace(/\\/g, "/"); this.encoding = "UTF-8"; this._mode = null; this._buf = ""; }
  get name() { return path.basename(this.fsName); }
  get exists() { return fs.existsSync(this.fsName); }
  get parent() { return new MFolder(path.dirname(this.fsName)); }
  get modified() { return fs.existsSync(this.fsName) ? fs.statSync(this.fsName).mtime : new Date(0); }
  open(m) { this._mode = m; this._buf = m === "a" && this.exists ? "" : ""; if (m === "r" && !this.exists) return false; return true; }
  read() { return fs.readFileSync(this.fsName, "utf8"); }
  write(s) { if (this._mode === "a") fs.appendFileSync(this.fsName, s); else fs.writeFileSync(this.fsName, (this._wrote ? fs.readFileSync(this.fsName, "utf8") : "") + s); this._wrote = true; }
  writeln(s) { this.write(s + "\n"); }
  close() { this._wrote = false; }
  remove() { try { fs.unlinkSync(this.fsName); } catch (e) {} return true; }
  copy(t) { fs.copyFileSync(this.fsName, String(t)); return true; }
  rename(n) { const np = path.join(path.dirname(this.fsName), n); fs.renameSync(this.fsName, np); this.fsName = np; return true; }
}
class MFolder {
  constructor(p) { this.fsName = String(p && p.fsName ? p.fsName : p).replace(/\\/g, "/"); }
  get exists() { return fs.existsSync(this.fsName); }
  get parent() { return new MFolder(path.dirname(this.fsName)); }
  get name() { return path.basename(this.fsName); }
  create() { fs.mkdirSync(this.fsName, { recursive: true }); return true; }
  getFiles(mask) {
    if (!this.exists) return [];
    const re = mask ? new RegExp("^" + mask.replace(/\./g, "\\.").replace(/\*/g, ".*") + "$", "i") : null;
    return fs.readdirSync(this.fsName).filter(n => !re || re.test(n)).map(n => { const p = path.join(this.fsName, n); return fs.statSync(p).isDirectory() ? new MFolder(p) : new MFile(p); });
  }
}
function makeProject() {
  const items = [];
  const proj = {
    file: null, expressionEngine: "extendscript", bitsPerChannel: 8,
    items: {
      addFolder(n) { const f = new FolderItem(n); items.push(f); return f; },
      addComp(n, w, h, par, d, fps) { const c = new CompItem(n, w, h, par, d, fps); items.push(c); return c; },
    },
    get numItems() { return items.length; },
    item(i) { return items[i - 1]; },
    importFile(io) { if (!fs.existsSync(io.file.fsName)) throw new Error("import missing " + io.file.fsName); const it = new FootageItem(io.file.fsName); items.push(it); return it; },
    save(f) { if (f) { this.file = f; fs.writeFileSync(f.fsName, "mock aep"); } },
    close() {},
    renderQueue: { _items: [], get numItems() { return this._items.length; }, item(i) { return this._items[i - 1]; },
      items: { add(c) { const om = { templates: ["Best Settings", "H.264 - Match Render Settings - 15 Mbps", "Lossless"], applyTemplate(t) { this.t = t; }, file: null };
        const it = { applyTemplate() {}, outputModule() { return om; }, remove() {} }; proj.renderQueue._items.push(it); return it; } },
      render() { for (const it of this._items) { const f = it.outputModule(1).file; if (f) fs.writeFileSync(f.fsName, "mock render"); } } },
  };
  return proj;
}
const app = {
  version: "25.0x(mock)", project: makeProject(),
  newProject() { this.project = makeProject(); return this.project; },
  open(f) { this.project = makeProject(); this.project.file = f; },
  beginUndoGroup() {}, endUndoGroup() {}, beginSuppressDialogs() {}, endSuppressDialogs() {},
  scheduleTask() { return 1; }, cancelTask() {},
  fonts: { getFontsByPostScriptName(n) { return ["Anton-Regular", "Impact", "ArialMT", "Arial-BoldMT"].includes(n) ? [{ isSubstitute: false }] : []; } },
};
const ctx = {
  app, File: MFile, Folder: MFolder, ImportOptions: class { constructor(f) { this.file = f; } }, Shape, KeyframeEase, TextDocument,
  KeyframeInterpolationType: KIT_, BlendingMode: { NORMAL: 1, ADD: 2, SCREEN: 3, MULTIPLY: 4, OVERLAY: 5, SOFT_LIGHT: 6, COLOR: 7 },
  ParagraphJustification: { CENTER_JUSTIFY: 7413 }, CloseOptions: { DO_NOT_SAVE_CHANGES: 1 }, TrackMatteType: { ALPHA: 1, ALPHA_INVERTED: 2 },
  CompItem, alert: m => console.log("ALERT", m), writeLn: () => {}, clearOutput: () => {}, console,
  RA_KIT: kitDir, RA_ROOT: path.dirname(projectDir),
};
ctx.$ = { fileName: path.join(kitDir, "ae", "ra_engine.jsx"), global: ctx, evalFile(f) { vm.runInContext(fs.readFileSync(f.fsName || f, "utf8"), ctx); } };
vm.createContext(ctx);
/* ExtendScript's Array.sort is not stable. Emulate the worst case inside the engine's realm (ties come out
   reversed) so engine code that relies on tie order fails here instead of only in After Effects. */
vm.runInContext(`(function () {
  var _sort = Array.prototype.sort;
  Array.prototype.sort = function (cmp) {
    _sort.call(this, cmp);
    if (typeof cmp !== "function") { return this; }
    var i = 0, j, k, run;
    while (i < this.length) {
      j = i + 1;
      while (j < this.length && cmp(this[i], this[j]) === 0) { j += 1; }
      if (j - i > 1) { run = this.slice(i, j).reverse(); for (k = 0; k < run.length; k += 1) { this[i + k] = run[k]; } }
      i = j;
    }
    return this;
  };
}());`, ctx);
const JOB = args.indexOf("--job") >= 0 ? path.resolve(args[args.indexOf("--job") + 1]) : null;
const t0 = Date.now();
let errs;
if (JOB) {   // run a queued job file exactly as the bridge would (RA_ROOT/RA_KIT preset like ra_bridge.jsx)
  ctx.RA_ROOT = path.dirname(path.dirname(JOB)).replace(/\\/g, "/");
  ctx.RA_KIT = ctx.RA_ROOT + "/_kit";
  ctx.$.fileName = JOB;
  vm.runInContext(fs.readFileSync(JOB, "utf8"), ctx, { filename: path.basename(JOB) });
  errs = ctx.RA_LAST || 0;
} else {
  vm.runInContext(fs.readFileSync(path.join(kitDir, "ae", "ra_engine.jsx"), "utf8"), ctx, { filename: "ra_engine.jsx" });
  errs = vm.runInContext("RA.build(" + JSON.stringify(projectDir.replace(/\\/g, "/")) + ", {})", ctx);
}
const log = fs.readFileSync(path.join(projectDir, "ae", "build_log.txt"), "utf8").split("\n").filter(Boolean);
const bad = log.filter(l => /ERROR|WARNING/.test(l));
console.log(`mock build: ${errs} errors, ${log.filter(l => /WARNING/.test(l)).length} warnings, ${STATS.comps} comps, ${STATS.layers} layers, ${STATS.effects} effects, ${STATS.expressions} expressions, ${STATS.keys} keys, ${Date.now() - t0} ms`);
bad.slice(0, 60).forEach(l => console.log("  " + l));

// ---- parse every expression (AE JavaScript engine is modern V8: parse as ES2020 script; no array arithmetic allowed)
let exprBad = 0;
const seen = new Set();
for (const e of EXPR) {
  if (seen.has(e.src)) continue; seen.add(e.src);
  if (acorn) { try { acorn.parse(e.src, { ecmaVersion: 2020, allowReturnOutsideFunction: true }); } catch (er) { exprBad++; console.log("EXPR SYNTAX " + er.message + " in " + e.prop + "\n   " + e.src.slice(0, 300)); } }
  if (/value\s*[+\-]\s*\[|\]\s*[+\-]\s*value(?!\[)|wiggle\([^)]*\)\s*-\s*value(?!\[)/.test(e.src)) { exprBad++; console.log("EXPR ARRAY MATH (not valid in the JavaScript engine): " + e.prop + "\n   " + e.src.slice(0, 200)); }
}
console.log(`expressions: ${seen.size} unique, ${exprBad} problems`);

// ---- run the rig expressions in a sandbox and dump joint positions for a parity check with the Python rig
if (PARITY) {
  /* parity_sliders.json: {s: {slider: value}, t} or {cases: [{comp: "CHAR_<id>", s, t}]} (dev/rig_parity.py writes it).
     Every case evaluates, in that character comp: the limb paths, the head position, the opacity of the four arm
     layers (far arm behind/in front, near arm behind the chest in a three-quarter view) and the torso width and
     clothing transform of the three-quarter turn. */
  function evalExpr(src, sliders, time, value) {
    const C = { effect: n => () => ({ value: sliders[n] === undefined ? 0 : sliders[n] }) };
    const env = { thisComp: { layer: () => C }, time, Math, createPath: (p, i, o, c) => ({ points: p }), seedRandom() {}, random: () => 0.5, value: value || [0, 0] };
    return vm.runInNewContext(src, env);
  }
  const SL = JSON.parse(fs.readFileSync(path.join(projectDir, "parity_sliders.json"), "utf8"));
  const cases = SL.cases || [{ comp: "", s: SL.s, t: SL.t }];
  const res = [];
  for (const cs of cases) {
    const mine = EXPR.filter(e => !cs.comp || e.comp === cs.comp);
    const out = { comp: cs.comp, limbs: {}, head: null, opacity: {}, torsoW: null, clothes: {} };
    const seenL = {};
    for (const e of mine) {
      const nm = e.prop.split(" > ")[0];
      if (/createPath\(\[p0,p1,p2\]/.test(e.src) && !seenL[nm]) { seenL[nm] = 1; out.limbs[nm] = evalExpr(e.src, cs.s, cs.t).points; }
      if (/^ARM_[FN](_FRONT|_BACK)?$/.test(nm) && /Opacity/.test(e.matchName) && out.opacity[nm] === undefined) out.opacity[nm] = evalExpr(e.src, cs.s, cs.t);
      if (nm === "TORSO" && /Stroke Width/.test(e.matchName) && out.torsoW === null) out.torsoW = evalExpr(e.src, cs.s, cs.t);
      if (nm === "CLOTHES" && /Position/.test(e.matchName)) out.clothes.pos = evalExpr(e.src, cs.s, cs.t, [0, 0]);
      if (nm === "CLOTHES" && /Scale/.test(e.matchName)) out.clothes.scale = evalExpr(e.src, cs.s, cs.t, [100, 100]);
    }
    const head = mine.find(e => /head_lift|hu\[0\]\*/.test(e.src) && /neck\[0\]\+hu/.test(e.src));
    if (head) out.head = evalExpr(head.src, cs.s, cs.t);
    /* old single-case readers */
    out.farFront = { ARM_F: out.opacity.ARM_F, ARM_F_FRONT: out.opacity.ARM_F_FRONT };
    res.push(out);
  }
  fs.writeFileSync(path.join(projectDir, "parity_ae.json"), JSON.stringify(SL.cases ? { cases: res } : res[0]));
  console.log("parity dump written (" + res.length + " cases)");
}
// ---- creatures: evaluate every creature expression over time; dev/creature_parity.py checks them against creatures.py
if (args.indexOf("--creatures") >= 0) {
  const P = ctx.app.project; let dur = 0;
  for (let i = 1; i <= P.numItems; i++) { const it = P.item(i); if (it instanceof CompItem && it.name === "MAIN") dur = it.duration; }
  const out = { step: 0.1, layers: {} };
  for (const e of EXPR) {
    const parts = e.prop.split(" > "), ln = parts.find(x => /^CREATURE/.test(x));
    if (!ln) continue;
    const kind = /Position/.test(e.matchName) ? "pos" : (/Scale/.test(e.matchName) ? "scale" : "rot");
    const vals = [];
    for (let k = 0; k * 0.1 <= dur + 1e-9; k++) vals.push(vm.runInNewContext(e.src, { time: k * 0.1, value: [100, 100], Math }));
    (out.layers[ln] = out.layers[ln] || {})[kind] = vals;
  }
  fs.writeFileSync(path.join(projectDir, "parity_creatures.json"), JSON.stringify(out));
  console.log("creature dump: " + Object.keys(out.layers).length + " layers");
}
// ---- dump every character's control values over time; dev/compare_timeline.py checks them against the preview
if (args.indexOf("--timeline") >= 0) {
  const P = ctx.app.project, out = { t0: 0.037, step: 0.1, chars: {} };
  let dur = 0;
  for (let i = 1; i <= P.numItems; i++) { const it = P.item(i); if (it instanceof CompItem && it.name === "MAIN") dur = it.duration; }
  for (let i = 1; i <= P.numItems; i++) {
    const it = P.item(i);
    if (!(it instanceof CompItem) || it.name.indexOf("CHAR_") !== 0) continue;
    const rec = {};
    for (const e of it.layer("CTRL").property("ADBE Effect Parade")._kids) {
      const p = e.property(1), vals = [];
      for (let t = out.t0; t <= dur; t += out.step) vals.push(p.valueAtTime(Math.round(t * 1000) / 1000));
      rec[e.name] = vals;
    }
    out.chars[it.name.slice(5)] = rec;
  }
  fs.mkdirSync(path.join(projectDir, "qc"), { recursive: true });
  fs.writeFileSync(path.join(projectDir, "qc", "mock_timeline.json"), JSON.stringify(out));
  console.log("timeline dump written for " + Object.keys(out.chars).length + " characters -> qc/mock_timeline.json");
}
process.exit(errs || exprBad ? 1 : 0);
