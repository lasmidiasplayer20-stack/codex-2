/*  2D Stick Animator - After Effects engine
    Builds a complete, editable "glow stick-figure story short" project from a scene spec (plan/spec.json):
    rigged rubber-hose characters (pose library, walk/run/idle/talk/blink, faces, costumes, accessories, held props),
    AI/stock backgrounds with grades, an eased camera per shot (push-ins, snap pull-outs, punches, pans, shake),
    pop-in props and 3D-emoji icons, thought/speech bubbles, clock badges, money rain, embers, smoke, tints,
    B&W moments, transitions (flash, light leak, red wipe, glitch, whip, zoom blur, B&W fade, fade to black),
    one-word pop captions, vignette, grain and audio layers; then stills and renders.

    Rules for editing this file: ExtendScript is ES3 - no let/const, arrow functions, template strings or ES5
    array helpers; ASCII only. Syntax-check with:  node _kit/dev/check_jsx.js _kit/ae/ra_engine.jsx
    Run through the bridge (ra_bridge.jsx) or File > Scripts > Run Script File on a job file in _ae_jobs/.
*/
var RA = (function () {
    var RA = { VERSION: "2.3.0" };

    /* ================================================================= JSON */
    RA.parseJSON = function (str) {
        var at = 0, ch = " ";
        function err(m) { throw new Error("JSON " + m + " at " + at); }
        function next() { ch = str.charAt(at); at += 1; return ch; }
        function white() { while (ch && ch <= " ") { next(); } }
        function number() {
            var s = "";
            if (ch === "-") { s = "-"; next(); }
            while (ch >= "0" && ch <= "9") { s += ch; next(); }
            if (ch === ".") { s += "."; while (next() && ch >= "0" && ch <= "9") { s += ch; } }
            if (ch === "e" || ch === "E") {
                s += ch; next();
                if (ch === "-" || ch === "+") { s += ch; next(); }
                while (ch >= "0" && ch <= "9") { s += ch; next(); }
            }
            var n = Number(s);
            if (isNaN(n)) { err("bad number"); }
            return n;
        }
        function string() {
            var s = "", hex, i, u;
            if (ch !== "\"") { err("expected string"); }
            while (next()) {
                if (ch === "\"") { next(); return s; }
                if (ch === "\\") {
                    next();
                    if (ch === "u") {
                        u = 0;
                        for (i = 0; i < 4; i += 1) { hex = parseInt(next(), 16); if (!isFinite(hex)) { break; } u = u * 16 + hex; }
                        s += String.fromCharCode(u);
                    } else if (ch === "n") { s += "\n"; } else if (ch === "t") { s += "\t"; } else if (ch === "r") { s += "\r"; }
                    else if (ch === "b") { s += "\b"; } else if (ch === "f") { s += "\f"; } else { s += ch; }
                } else { s += ch; }
            }
            err("unterminated string");
        }
        function word() {
            if (ch === "t") { next(); next(); next(); next(); return true; }
            if (ch === "f") { next(); next(); next(); next(); next(); return false; }
            if (ch === "n") { next(); next(); next(); next(); return null; }
            err("unexpected " + ch);
        }
        var value;
        function array() {
            var a = [];
            next(); white();
            if (ch === "]") { next(); return a; }
            while (ch) {
                a.push(value()); white();
                if (ch === "]") { next(); return a; }
                if (ch !== ",") { err("expected ,"); }
                next(); white();
            }
            err("bad array");
        }
        function object() {
            var o = {}, k;
            next(); white();
            if (ch === "}") { next(); return o; }
            while (ch) {
                k = string(); white();
                if (ch !== ":") { err("expected :"); }
                next(); o[k] = value(); white();
                if (ch === "}") { next(); return o; }
                if (ch !== ",") { err("expected , in object"); }
                next(); white();
            }
            err("bad object");
        }
        value = function () {
            white();
            if (ch === "{") { return object(); }
            if (ch === "[") { return array(); }
            if (ch === "\"") { return string(); }
            if (ch === "-" || (ch >= "0" && ch <= "9")) { return number(); }
            return word();
        };
        var r = value(); white();
        return r;
    };
    RA.stringify = function (v) {
        var t = typeof v, out, i, k;
        if (v === null || v === undefined) { return "null"; }
        if (t === "number") { return isFinite(v) ? String(v) : "null"; }
        if (t === "boolean") { return v ? "true" : "false"; }
        if (t === "string") { return "\"" + v.replace(/\\/g, "\\\\").replace(/"/g, "\\\"").replace(/\n/g, "\\n").replace(/\r/g, "\\r") + "\""; }
        if (v instanceof Array) { out = []; for (i = 0; i < v.length; i += 1) { out.push(RA.stringify(v[i])); } return "[" + out.join(",") + "]"; }
        out = [];
        for (k in v) { if (v.hasOwnProperty(k)) { out.push(RA.stringify(k) + ":" + RA.stringify(v[k])); } }
        return "{" + out.join(",") + "}";
    };

    /* ================================================================= IO + log */
    function readText(path) {
        var f = new File(path);
        if (!f.exists) { throw new Error("File not found: " + path); }
        f.encoding = "UTF-8"; f.open("r"); var s = f.read(); f.close();
        return s;
    }
    function writeText(path, s, append) {
        var f = new File(path);
        if (f.parent && !f.parent.exists) { f.parent.create(); }
        f.encoding = "UTF-8"; f.open(append ? "a" : "w"); f.write(s); f.close();
    }
    RA.readText = readText; RA.writeText = writeText;
    var LOG = { file: null, errors: 0, warnings: 0, lines: [] };
    function log(msg) {
        var line = "[" + (new Date()).toTimeString().substr(0, 8) + "] " + msg;
        LOG.lines.push(line);
        if (LOG.file) { try { writeText(LOG.file, line + "\n", true); } catch (e) {} }
    }
    function warn(msg) { LOG.warnings += 1; log("WARNING " + msg); }
    function fail(what, e) { LOG.errors += 1; log("ERROR in " + what + ": " + e.toString() + (e.line ? " (line " + e.line + ")" : "")); }
    RA.log = log;

    /* ================================================================= utils */
    /* ExtendScript's Array.sort is not stable: ties keep their input order only through this helper */
    function stableSort(arr, cmp) {
        var i, w = [];
        for (i = 0; i < arr.length; i += 1) { w.push({ v: arr[i], i: i }); }
        w.sort(function (a, b) { var c = cmp(a.v, b.v); return c !== 0 ? c : a.i - b.i; });
        for (i = 0; i < w.length; i += 1) { arr[i] = w[i].v; }
        return arr;
    }
    function byT(a, b) { return a.t - b.t; }
    function num(v, d) { return (v === undefined || v === null || (typeof v === "number" && isNaN(v))) ? d : v; }
    function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
    function exists(p) { return p && (new File(p)).exists; }
    function isArr(v) { return v instanceof Array; }
    function hex(h, d) {
        if (h === undefined || h === null) { return d || [1, 1, 1]; }
        if (isArr(h)) { return [h[0], h[1], h[2]]; }
        var s = String(h).replace("#", "");
        if (s.length === 3) { s = s.charAt(0) + s.charAt(0) + s.charAt(1) + s.charAt(1) + s.charAt(2) + s.charAt(2); }
        return [parseInt(s.substr(0, 2), 16) / 255, parseInt(s.substr(2, 2), 16) / 255, parseInt(s.substr(4, 2), 16) / 255];
    }
    function shade(c, k) { return [clamp(c[0] * k, 0, 1), clamp(c[1] * k, 0, 1), clamp(c[2] * k, 0, 1)]; }
    function r4(v) { return Math.round(v * 10000) / 10000; }
    /* a small number from a character id (same as ra_preview.id_hash): each character blinks/talks on its own timing */
    function idHash(id) { var h = 0, i; id = String(id); for (i = 0; i < id.length; i += 1) { h += (i + 1) * id.charCodeAt(i); } return h % 997; }
    /* deterministic 0..1 hash (same formula in ra_preview.py) */
    function hash01(n) { var x = Math.sin(n * 12.9898) * 43758.5453; return x - Math.floor(x); }
    function esc(s) { return String(s).replace(/\\/g, "\\\\").replace(/"/g, "\\\""); }
    function slash(p) { return String(p).replace(/\\/g, "/"); }
    function absPath(base, p) {
        if (!p) { return null; }
        p = slash(p);
        if (/^[A-Za-z]:\//.test(p) || p.charAt(0) === "/" || p.substr(0, 2) === "//") { return p; }
        return slash(base) + "/" + p;
    }
    /* deterministic random so rebuilds look identical */
    var SEED = 12345;
    function rnd() { SEED = (SEED * 1103515245 + 12345) % 2147483648; return SEED / 2147483648; }
    function rr(a, b) { return a + (b - a) * rnd(); }

    /* ================================================================= property handles (AE invalidates refs when siblings are added) */
    function RH(resolve, matchName, name) { this._r = resolve; this.matchName = matchName; this.name = name; }
    RH.prototype.get = function () { return this._r(); };
    RH.prototype.property = function (x) { return this._r().property(x); };
    RH.prototype.addProperty = function (m) { return this._r().addProperty(m); };
    RH.prototype.moveTo = function (i) { return this._r().moveTo(i); };
    RH.prototype.remove = function () { return this._r().remove(); };
    function liveOf(x) { return (x instanceof RH) ? x.get() : x; }
    function effects(layer) { return layer.property("ADBE Effect Parade"); }
    function addFx(layer, matchName, name) {
        var fx = effects(layer).addProperty(matchName);
        if (name) { try { fx.name = name; } catch (e0) {} }
        var nm = fx.name;
        return new RH(function () { return effects(layer).property(nm); }, matchName, nm);
    }
    function fxProp(fx, idx) { try { return fx.property(idx); } catch (e) { warn("effect param " + idx + " on " + fx.name + ": " + e.toString()); return null; } }
    function fxSet(fx, idx, value, label) {
        var p = null;
        try {
            p = fx.property(idx);
            try { p.setValue(value); } catch (e1) {
                if (isArr(value) && value.length === 3) { p.setValue([value[0], value[1], value[2], 1]); } else { throw e1; }
            }
            return p;
        } catch (e) { warn("effect param " + (label || idx) + " on " + fx.name + ": " + e.toString()); return null; }
    }
    function slider(layer, name, v) { var fx = addFx(layer, "ADBE Slider Control", name); fx.property(1).setValue(v); return fx; }
    function tr(layer) { return layer.property("ADBE Transform Group"); }
    function P_pos(l) { return tr(l).property("ADBE Position"); }
    function P_scale(l) { return tr(l).property("ADBE Scale"); }
    function P_rot(l) { return tr(l).property("ADBE Rotate Z"); }
    function P_op(l) { return tr(l).property("ADBE Opacity"); }
    function P_anchor(l) { return tr(l).property("ADBE Anchor Point"); }

    /* ================================================================= keyframes */
    function easeKeys(prop, outInf, inInf) {
        var n = prop.numKeys, i, k, e1, e2, ok;
        for (i = 1; i <= n; i += 1) {
            try {
                if (prop.keyInInterpolationType(i) === KeyframeInterpolationType.HOLD) { continue; }
                prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            } catch (eb) {}
            ok = false;
            for (k = 1; k <= 3 && !ok; k += 1) {
                try {
                    e1 = []; e2 = [];
                    while (e1.length < k) { e1.push(new KeyframeEase(0, clamp(inInf, 0.1, 100))); e2.push(new KeyframeEase(0, clamp(outInf, 0.1, 100))); }
                    prop.setTemporalEaseAtKey(i, e1, e2);
                    ok = true;
                } catch (err) {}
            }
        }
    }
    /* set keys; ease: "inout" | "out" (fast start, slow end) | "in" | "linear" | "hold" | number */
    function setKeys(prop, times, values, ease) {
        if (!times.length) { return; }
        var i, k, e1, e2, ok, a, b, n0 = prop.numKeys;
        prop.setValuesAtTimes(times, values);
        if (ease === "hold") {
            for (i = 0; i < times.length; i += 1) {
                k = prop.nearestKeyIndex(times[i]);
                try { prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD); } catch (eh) {}
            }
            return;
        }
        if (ease === "linear") { return; }
        a = 60; b = 60;
        if (ease === "out") { a = 88; b = 6; }        /* arrive slow (in-influence high), leave fast */
        if (ease === "in") { a = 10; b = 75; }
        if (typeof ease === "number") { a = ease; b = ease; }
        for (i = 0; i < times.length; i += 1) {
            k = prop.nearestKeyIndex(times[i]);
            try { prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); } catch (ex) {}
            ok = false;
            for (var d = 1; d <= 3 && !ok; d += 1) {
                try {
                    e1 = []; e2 = [];
                    while (e1.length < d) { e1.push(new KeyframeEase(0, a)); e2.push(new KeyframeEase(0, b)); }
                    prop.setTemporalEaseAtKey(k, e1, e2);
                    ok = true;
                } catch (er) {}
            }
        }
    }
    function holdKeys(prop, times, values) { setKeys(prop, times, values, "hold"); }
    function popIn(prop, t, base, fps, dims) {
        dims = dims || ((prop.value && prop.value.length === 3) ? 3 : 2);
        var f = 1 / fps, mk = function (s) { return dims === 3 ? [s, s, 100] : [s, s]; };
        setKeys(prop, [t - f, t + 3 * f, t + 6 * f, t + 9 * f], [mk(0), mk(base * 1.16), mk(base * 0.96), mk(base)], 55);
    }
    function popOut(prop, t, base, fps, dims) {
        dims = dims || ((prop.value && prop.value.length === 3) ? 3 : 2);
        var f = 1 / fps, mk = function (s) { return dims === 3 ? [s, s, 100] : [s, s]; };
        setKeys(prop, [t - 6 * f, t - 3 * f, t], [mk(base), mk(base * 1.1), mk(0)], 50);
    }
    function setInOut(layer, tIn, tOut) {
        try { layer.inPoint = Math.max(0, tIn); layer.outPoint = Math.max(tIn + 0.04, tOut); } catch (e) {}
    }
    function parentTo(child, parent) {
        if (child.setParentWithJump) { child.setParentWithJump(parent); } else { child.parent = parent; }
    }

    /* ================================================================= shapes */
    function shapeLayer(comp, name) {
        var l = comp.layers.addShape();
        l.name = name;
        P_anchor(l).setValue([0, 0]);
        P_pos(l).setValue([0, 0]);
        return l;
    }
    function rootContents(l) { return new RH(function () { return l.property("ADBE Root Vectors Group"); }, "ADBE Root Vectors Group"); }
    function groupContents(g) { return new RH(function () { return liveOf(g).property("ADBE Vectors Group"); }, "ADBE Vectors Group"); }
    /* AE draws the first group on top: every new group goes to index 1 so later additions sit on top */
    function addGroup(parentContents, name) {
        var g = liveOf(parentContents).addProperty("ADBE Vector Group");
        g.name = name;
        try { g.moveTo(1); } catch (e) {}
        return new RH(function () { return liveOf(parentContents).property(name); }, "ADBE Vector Group", name);
    }
    function groupTr(g) { return liveOf(g).property("ADBE Vector Transform Group"); }
    function makeShape(pts, closed, smooth) {
        var sh = new Shape(), n = pts.length, i, inT = [], outT = [], p0, p1, p2, tx, ty;
        sh.vertices = pts;
        for (i = 0; i < n; i += 1) {
            if (smooth && n > 2) {
                p1 = pts[i];
                p0 = pts[(i - 1 + n) % n]; p2 = pts[(i + 1) % n];
                if (!closed && i === 0) { p0 = p1; }
                if (!closed && i === n - 1) { p2 = p1; }
                tx = (p2[0] - p0[0]) / 6; ty = (p2[1] - p0[1]) / 6;
                inT.push([-tx, -ty]); outT.push([tx, ty]);
            } else { inT.push([0, 0]); outT.push([0, 0]); }
        }
        sh.inTangents = inT; sh.outTangents = outT; sh.closed = !!closed;
        return sh;
    }
    function ellipseShape(cx, cy, w, h) {
        var k = 0.5523, rx = w / 2, ry = h / 2, sh = new Shape();
        sh.vertices = [[cx, cy - ry], [cx + rx, cy], [cx, cy + ry], [cx - rx, cy]];
        sh.inTangents = [[-rx * k, 0], [0, -ry * k], [rx * k, 0], [0, ry * k]];
        sh.outTangents = [[rx * k, 0], [0, ry * k], [-rx * k, 0], [0, -ry * k]];
        sh.closed = true;
        return sh;
    }
    function addPathTo(gc, shape, name) {
        var p = liveOf(gc).addProperty("ADBE Vector Shape - Group");
        if (name) { p.name = name; }
        p.property("ADBE Vector Shape").setValue(shape);
        var nm = p.name;
        return new RH(function () { return liveOf(gc).property(nm); }, "ADBE Vector Shape - Group", nm);
    }
    function addFill(gc, rgb, opacity) {
        var f = liveOf(gc).addProperty("ADBE Vector Graphic - Fill");
        f.property("ADBE Vector Fill Color").setValue(rgb);
        f.property("ADBE Vector Fill Opacity").setValue(num(opacity, 100));
        return f.name;
    }
    function strokeWidthExpr(gc, sname, expr) {
        try { liveOf(gc).property(sname).property("ADBE Vector Stroke Width").expression = expr; } catch (eW) { fail("stroke width expression", eW); }
    }
    /* three-quarter turn (ra_rig.draw_character_art): torso and clothing narrow by ts and shift towards the facing side */
    function turnTS() { var R = DATA.rig; return "var tnT=thisComp.layer(\"CTRL\").effect(\"turn\")(1).value;var ts=1-" + num(R.torso_turn, 0) + "*(1-tnT);"; }
    function turnShift() { var R = DATA.rig; return num(R.torso_turn_shift, 0) * R.torso_w; }
    function addStroke(gc, rgb, width, opacity) {
        var s = liveOf(gc).addProperty("ADBE Vector Graphic - Stroke");
        s.property("ADBE Vector Stroke Color").setValue(rgb);
        s.property("ADBE Vector Stroke Width").setValue(width);
        try { s.property("ADBE Vector Stroke Opacity").setValue(num(opacity, 100)); } catch (e0) {}
        try { s.property("ADBE Vector Stroke Line Cap").setValue(2); s.property("ADBE Vector Stroke Line Join").setValue(2); } catch (e) {}
        return s.name;
    }
    /* draw one costume/face element (parts.json / faces.json format) into group contents gc, scaled by u */
    function drawEl(gc, el, u, colors) {
        var fill = resolveCol(el.fill, colors), stroke = resolveCol(el.stroke, colors), sw = num(el.sw, 0) * u, sh, i, pts = [];
        if (el.t === "ellipse") { sh = ellipseShape(el.c[0] * u, el.c[1] * u, el.s[0] * u, el.s[1] * u); }
        else if (el.t === "rect") {
            var cx = el.c[0] * u, cy = el.c[1] * u, w = el.s[0] * u, h = el.s[1] * u, r = num(el.r, 0) * u;
            var rc = liveOf(gc).addProperty("ADBE Vector Shape - Rect");
            rc.property("ADBE Vector Rect Size").setValue([w, h]);
            rc.property("ADBE Vector Rect Position").setValue([cx, cy]);
            if (r) { rc.property("ADBE Vector Rect Roundness").setValue(r); }
        } else {
            for (i = 0; i < el.pts.length; i += 1) { pts.push([el.pts[i][0] * u, el.pts[i][1] * u]); }
            if (el.t === "line") { sh = makeShape(pts, false, false); if (!stroke) { stroke = fill || [0, 0, 0]; } fill = null; }
            else { sh = makeShape(pts, !el.open, !!el.smooth); }
        }
        if (sh) { addPathTo(gc, sh); }
        if (stroke && sw > 0) { addStroke(gc, stroke, sw, 100); }
        if (fill && el.t !== "line") {
            var fnm = addFill(gc, fill, 100);
            /* skin-coloured face cuts (eye lids) follow the face colour (poisoned purple, angry red...) */
            if (el.fill === "BODY" && colors.bodyExpr) {
                try { liveOf(gc).property(fnm).property("ADBE Vector Fill Color").expression = colors.bodyExpr; } catch (eBX) { warn("lid colour expression: " + eBX.toString()); }
            }
        }
    }
    function resolveCol(c, colors) {
        if (c === undefined || c === null) { return null; }
        if (c === "BODY") { return colors.body; }
        if (c === "INK") { return colors.ink; }
        if (c === "C1") { return colors.c1; }
        if (c === "C2") { return colors.c2; }
        return hex(c);
    }
    function drawEls(parentContents, name, els, u, colors, onlyLayer) {
        var g = addGroup(parentContents, name), gc = groupContents(g), i, el, sub, n = 0;
        /* each element in its own sub-group so paths and paints do not mix; later elements on top */
        for (i = 0; i < els.length; i += 1) {
            el = els[i];
            if (onlyLayer && num(el.layer, "front") !== onlyLayer) { continue; }
            if (!onlyLayer && el.layer === "back") { continue; }
            sub = addGroup(gc, name + "_" + i);
            drawEl(groupContents(sub), el, u, colors);
            n += 1;
        }
        return g;
    }

    /* ================================================================= footage */
    var FOOT = {};
    function importFile(path, folder) {
        if (!path) { return null; }
        if (FOOT[path]) { return FOOT[path]; }
        if (!exists(path)) { warn("missing file " + path); return null; }
        try {
            var io = new ImportOptions(new File(path));
            var item = app.project.importFile(io);
            if (folder) { item.parentFolder = folder; }
            FOOT[path] = item;
            return item;
        } catch (e) { fail("import " + path, e); return null; }
    }

    /* ================================================================= fonts */
    var FONT_CACHE = {};
    function fontOK(ps) {
        if (FONT_CACHE[ps] !== undefined) { return FONT_CACHE[ps]; }
        var ok = null, list;
        try {
            if (app.fonts && app.fonts.getFontsByPostScriptName) {
                list = app.fonts.getFontsByPostScriptName(ps);
                if (list && list.length) {
                    ok = true;
                    try { if (list[0].isSubstitute) { ok = false; } } catch (e2) {}
                } else { ok = false; }
            }
        } catch (e) { ok = null; }
        FONT_CACHE[ps] = ok;
        return ok;
    }
    function pickFont(list) {
        var i, r;
        for (i = 0; i < list.length; i += 1) { r = fontOK(list[i]); if (r === true) { return list[i]; } }
        for (i = 0; i < list.length; i += 1) { r = fontOK(list[i]); if (r === null) { return list[i]; } }
        return list[list.length - 1];
    }

    /* ================================================================= state */
    var B = null;   /* build state */
    var DATA = {};

    function loadData(kit) {
        DATA.rig = RA.parseJSON(readText(kit + "/data/rig.json"));
        DATA.poses = RA.parseJSON(readText(kit + "/data/poses.json"));
        DATA.parts = RA.parseJSON(readText(kit + "/data/parts.json"));
        DATA.faces = RA.parseJSON(readText(kit + "/data/faces.json"));
        DATA.style = RA.parseJSON(readText(kit + "/data/style.json"));
    }
    function poseVals(name, ov) {
        var P = DATA.poses, base = P.stand, p = P[name] || P.stand, out = {}, k, L = ["aF", "aN", "lF", "lN"], i, src = {};
        if (!P[name] && name) { warn("unknown pose '" + name + "' (using stand)"); }
        for (k in base) { if (base.hasOwnProperty(k)) { src[k] = base[k]; } }
        for (k in p) { if (p.hasOwnProperty(k)) { src[k] = p[k]; } }
        if (ov) { for (k in ov) { if (ov.hasOwnProperty(k) && src.hasOwnProperty(k)) { src[k] = ov[k]; } } }
        out.lean = num(src.lean, 0); out.head = num(src.head, 0); out.hipX = src.hip[0]; out.hipY = src.hip[1];
        out.turn = num(p.turn, 0); if (ov && ov.turn !== undefined) { out.turn = num(ov.turn, 0); }   /* never inherited from stand */
        out.fFront = num(p.fFront, 0); if (ov && ov.fFront !== undefined) { out.fFront = num(ov.fFront, 0); }   /* far arm in front */
        for (i = 0; i < L.length; i += 1) { out[L[i] + "u"] = src[L[i]][0]; out[L[i] + "l"] = src[L[i]][1]; }
        return out;
    }
    var OVER_FACE = { glasses: true };
    var POSE_KEYS = ["lean", "head", "hipX", "hipY", "turn", "fFront", "aFu", "aFl", "aNu", "aNl", "lFu", "lFl", "lNu", "lNl"];

    /* ================================================================= project scaffold */
    function newProject(S) {
        try {
            if (app.project && app.project.numItems > 0) {
                if (app.project.file) { app.project.save(); log("saved the open project before building: " + app.project.file.fsName); }
                else { var bk = new File(B.root + "/ae/_unsaved_project_backup.aep"); if (!bk.parent.exists) { bk.parent.create(); } app.project.save(bk); log("backed up the open untitled project to " + bk.fsName); }
            }
        } catch (eb) { warn("could not save the open project: " + eb.toString()); }
        try { if (app.project) { app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); } } catch (e) {}
        app.newProject();
        try { app.project.expressionEngine = "javascript-1.0"; } catch (e2) { warn("could not set JavaScript expression engine: " + e2.toString()); }
        try { app.project.bitsPerChannel = 8; } catch (e3) {}
        var F = {};
        var names = ["00_MAIN", "01_SHOTS", "02_CHARACTERS", "03_FOOTAGE", "04_AUDIO", "05_SOLIDS"];
        for (var i = 0; i < names.length; i += 1) { F[names[i]] = app.project.items.addFolder(names[i]); }
        F.main = F["00_MAIN"]; F.shots = F["01_SHOTS"]; F.chars = F["02_CHARACTERS"]; F.foot = F["03_FOOTAGE"]; F.audio = F["04_AUDIO"]; F.solids = F["05_SOLIDS"];
        return F;
    }
    function addComp(name, w, h, dur, folder) {
        var c = app.project.items.addComp(name, Math.round(w), Math.round(h), 1, dur, B.S.fps);
        if (folder) { c.parentFolder = folder; }
        try { c.motionBlur = false; } catch (e) {}
        return c;
    }
    function solid(comp, name, rgb, w, h) {
        var l = comp.layers.addSolid(rgb, name, Math.round(w || comp.width), Math.round(h || comp.height), 1, comp.duration);
        try { l.source.parentFolder = B.F.solids; } catch (e) {}
        return l;
    }
    function nullLayer(comp, name) {
        var l = comp.layers.addNull(comp.duration);
        l.name = name;
        P_anchor(l).setValue([0, 0]);
        try { l.source.parentFolder = B.F.solids; } catch (e) {}
        return l;
    }

    /* ================================================================= character rig */
    function rigPrelude(seedIdx) {
        var R = DATA.rig, W = R.procedural.walk, U = R.procedural.run, I = R.procedural.idle;
        return "var C=thisComp.layer(\"CTRL\");function g(n){return C.effect(n)(1).value;}" +
            "var D2R=Math.PI/180;var w=g(\"walk\"),r=g(\"run\"),sp=g(\"wspeed\"),idl=g(\"idle\"),phs=g(\"phase\")*D2R;" +
            "var ph=2*Math.PI*sp*time+phs,s=Math.sin(ph),c=Math.cos(ph);" +
            "var bob=-(w*" + W.bob + "+r*" + U.bob + ")*Math.abs(c)+w*" + (W.bob / 2) + "+r*" + (U.bob / 2) + "+idl*" + I.breath + "*Math.sin(2*Math.PI*0.35*time+phs);" +
            "var idS=idl*Math.sin(2*Math.PI*" + I.freq + "*time+phs);" +
            "var lean=g(\"lean\")+w*" + W.lean + "+r*" + U.lean + ";var la=lean*D2R;" +
            "var hip=[" + R.hip[0] + "+g(\"hipX\")," + R.hip[1] + "+g(\"hipY\")+bob];" +
            "var upv=[Math.sin(la),-Math.cos(la)];var perp=[Math.cos(la),Math.sin(la)];" +
            "var neck=[hip[0]+upv[0]*" + R.torso_len + ",hip[1]+upv[1]*" + R.torso_len + "];var tn=g(\"turn\");" +
            "var shp=[neck[0]-upv[0]*" + r4(num(B.curSD, R.shoulder_down)) + ",neck[1]-upv[1]*" + r4(num(B.curSD, R.shoulder_down)) + "];" +
            "function dv(a){a*=D2R;return [Math.sin(a),Math.cos(a)];}";
    }
    function limbSolve(L) {
        var R = DATA.rig, W = R.procedural.walk, U = R.procedural.run, I = R.procedural.idle;
        var isArm = L.charAt(0) === "a", near = L.charAt(1) === "N", sgnS = near ? "s" : "(-s)", sgnC = near ? "c" : "(-c)";
        var e = "";
        if (isArm) {
            /* armSw 0 = no walking arm swing (hands holding something or someone) */
            e += "var asw=g(\"armSw\");var au=g(\"" + L + "u\")-asw*(w*" + W.arm_amp + "*" + sgnS + "+r*" + U.arm_amp + "*" + sgnS + ")" + (near ? "+" : "-") + I.arm_amp + "*idS;";
            e += "var bl=g(\"" + L + "l\")+asw*(w*" + W.elbow + "*Math.max(0," + sgnS + ")+r*" + (U.elbow * 0.2) + "*Math.max(0," + sgnS + "));";
            /* arms start at the outer shoulder corners (B.curSW = cast.shoulder: the garment's armholes, from
               compile_spec); side views no longer slide them onto the chest (shoulder_side 1.0) */
            var swk = r4(num(B.curSW, num(R.shoulder_spread, 0.36) * R.torso_w)) * (near ? 1 : -1);
            var ks = num(R.shoulder_side, 1);
            e += "var swf=" + ks + "+" + r4(1 - ks) + "*tn;var p0=[shp[0]+perp[0]*" + swk + "*swf,shp[1]+perp[1]*" + swk + "*swf];var LU=" + R.arm_u + ",LL=" + R.arm_l + ";";
        } else {
            e += "var au=g(\"" + L + "u\")+w*" + W.leg_amp + "*" + sgnS + "+r*" + U.leg_amp + "*" + sgnS + ";";
            e += "var bl=g(\"" + L + "l\")-w*(" + W.knee[0] + "+" + W.knee[1] + "*Math.max(0," + sgnC + "))-r*(" + U.knee[0] + "+" + U.knee[1] + "*Math.max(0," + sgnC + "));";
            var sp = num(R.hip_spread, 0.22) * R.torso_w * (near ? 1 : -1);
            e += "var p0=[hip[0]+perp[0]*(" + sp + "),hip[1]+perp[1]*(" + sp + ")];var LU=" + R.leg_u + ",LL=" + R.leg_l + ";";
        }
        e += "var d1=dv(au),p1=[p0[0]+LU*d1[0],p0[1]+LU*d1[1]];var al=au+bl;var d2=dv(al),p2=[p1[0]+LL*d2[0],p1[1]+LL*d2[1]];";
        return e;
    }
    function limbPathExpr(L) {
        var k = DATA.rig.joint_tangent * 0.5;
        return rigPrelude() + limbSolve(L) +
            "var tg=[(p2[0]-p0[0])*" + k + ",(p2[1]-p0[1])*" + k + "];" +
            "createPath([p0,p1,p2],[[0,0],[-tg[0],-tg[1]],[0,0]],[[0,0],tg,[0,0]],false);";
    }
    function torsoPathExpr() { return rigPrelude() + "createPath([hip,neck],[[0,0],[0,0]],[[0,0],[0,0]],false);"; }
    function headPosExpr() {
        var R = DATA.rig;
        return rigPrelude() + "var hu=[Math.sin((lean+g(\"head\")*0.35)*D2R),-Math.cos((lean+g(\"head\")*0.35)*D2R)];[neck[0]+hu[0]*" + R.head_lift + ",neck[1]+hu[1]*" + R.head_lift + "];";
    }
    function headRotExpr() { return rigPrelude() + "lean+g(\"head\");"; }
    function torsoPosExpr() { return rigPrelude() + "hip;"; }
    function torsoRotExpr() { return rigPrelude() + "lean;"; }
    function handPosExpr(L) { return rigPrelude() + limbSolve(L) + "p2;"; }
    function handAngleExpr(L) { return rigPrelude() + limbSolve(L) + "al;"; }

    /* cast.sleeve / cast.pants / cast.shoes: "#hex" or {color, len}: coloured stretches of the limb tube */
    function limbStyle(cast, kind) {
        var v = cast[kind], d = { sleeve: 0.5, pants: 1.0, shoes: 0.13 };
        if (!v) { return null; }
        if (typeof v === "string") { v = { color: v }; }
        return { color: hex(v.color, [0.2, 0.2, 0.2]), len: num(v.len, d[kind]) };
    }
    /* soft clay shading (as in the references): a body part is drawn in its darker edge colour, then a narrower
       body-colour core with a Gaussian blur on top, so the part rolls off softly to its edges - no emboss */
    function softCore(comp, root, name, pathExpr, isEllipse, width, body, sigmaK, chokeK, widthExprFn) {
        var SH = DATA.rig.look.shade;
        if (!SH) { return null; }
        var c = shapeLayer(comp, name);
        var cg = groupContents(addGroup(rootContents(c), "CORE"));
        if (isEllipse) {
            var d = width * (1 - 2 * chokeK);
            addPathTo(cg, ellipseShape(0, 0, d, d));
            addFill(cg, body, 100);
        } else {
            var cp = addPathTo(cg, makeShape([[0, 0], [0, 100], [0, 200]], false, false), "P");
            var csn = addStroke(cg, body, width * (1 - 2 * chokeK), 100);
            if (widthExprFn) { strokeWidthExpr(cg, csn, widthExprFn(width * (1 - 2 * chokeK))); }
            try { liveOf(cp).property("ADBE Vector Shape").expression = pathExpr; } catch (e) { fail("core expression " + name, e); }
        }
        parentTo(c, root); P_pos(c).setValue([0, 0]);
        var gb = addFx(c, "ADBE Gaussian Blur 2", "Soft");
        fxSet(gb, 1, Math.max(0.5, width * sigmaK * 2.5), "blurriness");   /* AE blurriness ~ 2.5 x sigma */
        /* the blurred core is clipped to the part's own shape (alpha track matte), so it fades right out to the edge
           without spilling past it - no visible inner shape */
        var m = shapeLayer(comp, name + "_MATTE");
        var mg = groupContents(addGroup(rootContents(m), "M"));
        if (isEllipse) {
            addPathTo(mg, ellipseShape(0, 0, width, width));
            addFill(mg, [1, 1, 1], 100);
        } else {
            var mp = addPathTo(mg, makeShape([[0, 0], [0, 100], [0, 200]], false, false), "P");
            var msn = addStroke(mg, [1, 1, 1], width, 100);
            if (widthExprFn) { strokeWidthExpr(mg, msn, widthExprFn(width)); }
            try { liveOf(mp).property("ADBE Vector Shape").expression = pathExpr; } catch (e2) { fail("matte expression " + name, e2); }
        }
        parentTo(m, root); P_pos(m).setValue([0, 0]);
        try {
            if (typeof c.setTrackMatte === "function") { c.setTrackMatte(m, TrackMatteType.ALPHA); }
            else { c.trackMatteType = TrackMatteType.ALPHA; }   /* AE before 2023: the layer just above is the matte */
            m.enabled = false;
        } catch (eM) { warn("shading matte " + name + ": " + eM.toString()); }
        return c;
    }
    function addLimbLayer(comp, root, L, body, lw, contourAlpha, cast, tag, opExpr) {
        var SH = DATA.rig.look.shade;
        var l = shapeLayer(comp, (L.charAt(0) === "a" ? "ARM_" : "LEG_") + L.charAt(1) + (tag || ""));
        var gc = groupContents(addGroup(rootContents(l), "LIMB"));
        var pth = addPathTo(gc, makeShape([[0, 0], [0, 100], [0, 200]], false, false), "P");
        addStroke(gc, SH ? shade(body, SH.edge) : body, lw, 100);
        if (contourAlpha > 0) { addStroke(gc, shade(body, 0.62), lw + 7, contourAlpha * 100); }
        parentTo(l, root);
        P_pos(l).setValue([0, 0]);
        try { liveOf(pth).property("ADBE Vector Shape").expression = limbPathExpr(L); } catch (e) { fail("limb expression " + L, e); }
        var core = SH ? softCore(comp, root, l.name + "_CORE", limbPathExpr(L), false, lw, body, SH.sigma, SH.choke) : null;
        /* coloured segments on top (own layer, above the soft core), each a copy of the path trimmed by length */
        var segs = [], q, isArm = L.charAt(0) === "a", st;
        cast = cast || {};
        if (isArm) { st = limbStyle(cast, "sleeve"); if (st) { segs.push({ n: "SLEEVE", c: st.color, a: 0, b: Math.min(1, st.len), w: lw + 1.5 }); } }
        else {
            st = limbStyle(cast, "pants"); if (st) { segs.push({ n: "PANTS", c: st.color, a: 0, b: Math.min(1, st.len), w: lw + 1.5 }); }
            st = limbStyle(cast, "shoes"); if (st) { segs.push({ n: "SHOE", c: st.color, a: Math.max(0, 1 - st.len), b: 1, w: lw * 1.08 }); }
        }
        var cl = l;
        if (segs.length && SH) { cl = shapeLayer(comp, l.name + "_CLOTH"); parentTo(cl, root); P_pos(cl).setValue([0, 0]); }
        for (q = 0; q < segs.length; q += 1) {
            var sgc = groupContents(addGroup(rootContents(cl), segs[q].n));
            var sp = addPathTo(sgc, makeShape([[0, 0], [0, 100], [0, 200]], false, false), "P");
            try { liveOf(sp).property("ADBE Vector Shape").expression = limbPathExpr(L); } catch (e2) { fail("segment expression " + L, e2); }
            try {
                var tr = liveOf(sgc).addProperty("ADBE Vector Filter - Trim");
                tr.property("ADBE Vector Trim Start").setValue(segs[q].a * 100);
                tr.property("ADBE Vector Trim End").setValue(segs[q].b * 100);
            } catch (e3) { warn("trim paths " + L + ": " + e3.toString()); }
            addStroke(sgc, segs[q].c, segs[q].w, 100);
        }
        /* the far arm exists twice (behind and in front of the body); fFront picks which one shows */
        if (opExpr) {
            var opl = [l, core, cl], oi;
            for (oi = 0; oi < opl.length; oi += 1) {
                if (opl[oi] && (oi < 2 || opl[oi] !== l)) {
                    try { P_op(opl[oi]).expression = opExpr; } catch (eO) { fail("far arm opacity " + L, eO); }
                }
            }
        }
        return l;
    }

    function buildCharacter(id, cast, actorTimeline) {
        var R = DATA.rig, S = B.S, Fc = DATA.faces;
        var comp = addComp("CHAR_" + id, R.comp_w, R.comp_h, S.duration, B.F.chars);
        var body = hex(cast.color, [0.35, 0.88, 0.96]);
        var colors = { body: body, ink: hex(Fc.ink), c1: hex(cast.c1, [0.23, 0.16, 0.12]), c2: hex(cast.c2, [0.16, 0.16, 0.16]) };
        var build = num(cast.build, 1), lw = R.limb_w * num(cast.limb, 1), aw = num(R.arm_w, R.limb_w) * num(cast.limb, 1), tw = R.torso_w * build, D = R.head_d * num(cast.head, 1);
        var i, k, L, parts = cast.parts || [], hp = [], tp = [];
        B.curSW = num(cast.shoulder, num(R.shoulder_spread, 0.36) * tw);
        B.curSD = num(cast.shoulder_dn, R.shoulder_down);   /* shoulder height of this character (compile_spec: cast_arms) */
        for (i = 0; i < parts.length; i += 1) {
            if (DATA.parts.head[parts[i]]) { hp.push(parts[i]); } else if (DATA.parts.torso[parts[i]]) { tp.push(parts[i]); } else { warn("cast " + id + ": unknown part " + parts[i]); }
        }

        /* CTRL null with every control the timeline keys */
        var ctrl = nullLayer(comp, "CTRL");
        P_pos(ctrl).setValue(R.origin);
        var ctlNames = POSE_KEYS.concat(["walk", "run", "wspeed", "armSw", "idle", "phase", "eyes", "mouth", "talk", "gaze", "gazeY", "blinkOn"]);
        var st = poseVals("stand");
        for (i = 0; i < ctlNames.length; i += 1) {
            k = ctlNames[i];
            slider(ctrl, k, st.hasOwnProperty(k) ? st[k] : 0);
        }
        effects(ctrl).property("wspeed").property(1).setValue(1.6);
        effects(ctrl).property("armSw").property(1).setValue(1);
        effects(ctrl).property("idle").property(1).setValue(num(cast.idle, 1));
        effects(ctrl).property("phase").property(1).setValue((idHash(id) * 47) % 360);   /* same as ra_preview.py */
        effects(ctrl).property("gaze").property(1).setValue(R.face.gaze);
        effects(ctrl).property("gazeY").property(1).setValue(num(R.face.gaze_y, 0));
        slider(ctrl, "flush", 0);
        var fcc = addFx(ctrl, "ADBE Color Control", "flushCol");
        try { fcc.property(1).setValue([0.55, 0.23, 0.55]); } catch (eFc) {}
        effects(ctrl).property("blinkOn").property(1).setValue(1);

        var root = nullLayer(comp, "ROOT");
        P_pos(root).setValue(R.origin);

        /* null that carries the head transform, and one for the torso frame */
        var headN = nullLayer(comp, "HEADNULL"); parentTo(headN, root);
        P_pos(headN).expression = headPosExpr(); P_rot(headN).expression = headRotExpr();
        var torsoN = nullLayer(comp, "TORSONULL"); parentTo(torsoN, root);
        P_pos(torsoN).expression = torsoPosExpr(); P_rot(torsoN).expression = torsoRotExpr();
        var handN = nullLayer(comp, "HAND_N"); parentTo(handN, root); P_pos(handN).expression = handPosExpr("aN");
        var handF = nullLayer(comp, "HAND_F"); parentTo(handF, root); P_pos(handF).expression = handPosExpr("aF");

        /* draw order bottom -> top: each new layer goes on top, so build from the back */
        var headBack = shapeLayer(comp, "HEAD_BACK"); parentTo(headBack, headN); P_pos(headBack).setValue([0, 0]);
        var nb = 0;
        for (i = 0; i < hp.length; i += 1) {
            var hasBack = false, els = DATA.parts.head[hp[i]].els, j;
            for (j = 0; j < els.length; j += 1) { if (els[j].layer === "back") { hasBack = true; } }
            if (hasBack) { drawEls(rootContents(headBack), "B_" + hp[i], els, D, colors, "back"); nb += 1; }
        }
        accessoryLayers(comp, cast, "behind", headN, torsoN, D, id);
        holdLayers(comp, id, actorTimeline, handF, handN, "back");
        /* far arm in front when the pose asks (fFront) or when it stays on its own side of the body (ra_rig.far_arm_front) */
        var FF = rigPrelude() + limbSolve("aF") + "var d1=dv(au),p1=[p0[0]+LU*d1[0],p0[1]+LU*d1[1]];var al=au+bl;var d2=dv(al),p2=[p1[0]+LL*d2[0],p1[1]+LL*d2[1]];" +
            "var fe=(p1[0]-shp[0])*perp[0]+(p1[1]-shp[1])*perp[1],fh=(p2[0]-shp[0])*perp[0]+(p2[1]-shp[1])*perp[1];" +
            "var ffr=(g(\"turn\")<0.5)||(g(\"fFront\")>=0.5)||(fe<-8&&fh<10);";
        /* three-quarter view (turn < 0.5): the near arm comes from behind the chest, the camera-side far arm is in front */
        var TQ = "thisComp.layer(\"CTRL\").effect(\"turn\")(1).value<0.5";
        addLimbLayer(comp, root, "aN", body, aw, num(R.look.limb_contour, 0.35), cast, "_BACK", TQ + "?100:0;");
        addLimbLayer(comp, root, "aF", body, aw, 0, cast, "", FF + "ffr?0:100;");
        addLimbLayer(comp, root, "lF", body, lw, 0, cast);
        var torso = shapeLayer(comp, "TORSO");
        var tgc = groupContents(addGroup(rootContents(torso), "T"));
        var tpth = addPathTo(tgc, makeShape([[0, -465], [0, -755]], false, false), "P");
        var SHD = R.look.shade;
        var tsn = addStroke(tgc, SHD ? shade(body, SHD.edge) : body, tw, 100);
        var twFn = function (w0) { return turnTS() + r4(w0) + "*ts;"; };
        strokeWidthExpr(tgc, tsn, twFn(tw));
        parentTo(torso, root); P_pos(torso).setValue([0, 0]);
        liveOf(tpth).property("ADBE Vector Shape").expression = torsoPathExpr();
        if (SHD) { softCore(comp, root, "TORSO_CORE", torsoPathExpr(), false, tw, body, SHD.sigma, SHD.choke, twFn); }
        addLimbLayer(comp, root, "lN", body, lw, num(R.look.leg_contour, 0), cast);
        if (tp.length) {
            var clo = shapeLayer(comp, "CLOTHES"); parentTo(clo, torsoN); P_pos(clo).setValue([0, 0]);
            P_pos(clo).expression = turnTS() + "[value[0]+" + r4(turnShift()) + "*(1-tnT),value[1]];";
            P_scale(clo).expression = turnTS() + "[value[0]*ts,value[1]];";
            for (i = 0; i < tp.length; i += 1) { drawEls(rootContents(clo), "T_" + tp[i], DATA.parts.torso[tp[i]].els, 1, colors, null); }
        }
        accessoryLayers(comp, cast, "torso", headN, torsoN, D, id);
        addLimbLayer(comp, root, "aF", body, aw, 0, cast, "_FRONT", FF + "ffr?100:0;");
        holdLayers(comp, id, actorTimeline, handF, handN, "mid");
        addLimbLayer(comp, root, "aN", body, aw, num(R.look.limb_contour, 0.35), cast, "", TQ + "?0:100;");
        armholeCaps(comp, cast, root, torsoN, D, aw, FF, TQ);

        /* HEAD: skull, then hair/hat/beard parts and image accessories, then the FACE layer on top (eyes, brows,
           mouth - like the reference faces drawn over beards), then glasses */
        var head = shapeLayer(comp, "HEAD"); parentTo(head, headN); P_pos(head).setValue([0, 0]);
        var rc = rootContents(head);
        var hg = addGroup(rc, "SKULL"), hgc = groupContents(hg);
        addPathTo(hgc, ellipseShape(0, 0, D, D));
        addFill(hgc, SHD ? shade(body, num(SHD.head_edge, SHD.edge)) : body, 100);
        addStroke(hgc, shade(body, 0.62), 8, num(R.look.head_contour, 0.6) * 100);
        /* list order Path, Fill, Stroke: the fill sits above the stroke so only the outer half of the contour shows */
        if (SHD) {
            softCore(comp, headN, "HEAD_CORE", "", true, D, body, num(SHD.head_sigma, SHD.sigma), num(SHD.head_choke, SHD.choke));
            head = shapeLayer(comp, "HEAD_TOP"); parentTo(head, headN); P_pos(head).setValue([0, 0]);
            rc = rootContents(head);
        }
        var fl = addGroup(rc, "FLUSH"), flc = groupContents(fl);      /* face colour (poisoned, angry, cold) on the skull only */
        addPathTo(flc, ellipseShape(0, 0, D, D));
        addFill(flc, [0.55, 0.23, 0.55], 100);
        try {
            var flp = liveOf(flc).property("ADBE Vector Graphic - Fill");
            flp.property("ADBE Vector Fill Color").expression = "thisComp.layer(\"CTRL\").effect(\"flushCol\")(1).value;";
            groupTr(fl).property("ADBE Vector Group Opacity").expression = "thisComp.layer(\"CTRL\").effect(\"flush\")(1).value*100;";
        } catch (eFl) { warn("face colour expression: " + eFl.toString()); }
        for (i = 0; i < hp.length; i += 1) {
            if (!OVER_FACE[hp[i]]) { drawEls(rc, "H_" + hp[i], DATA.parts.head[hp[i]].els, D, colors, null); }
        }
        accessoryLayers(comp, cast, "head", headN, torsoN, D, id);
        var face = shapeLayer(comp, "FACE"); parentTo(face, headN); P_pos(face).setValue([0, 0]);
        var fcc = rootContents(face);
        var fcolors = {}, ck;
        for (ck in colors) { if (colors.hasOwnProperty(ck)) { fcolors[ck] = colors[ck]; } }
        fcolors.bodyExpr = "var C=thisComp.layer(\"CTRL\");var a=C.effect(\"flush\")(1).value;var f=C.effect(\"flushCol\")(1).value;" +
            "[" + r4(body[0]) + "+(f[0]-" + r4(body[0]) + ")*a," + r4(body[1]) + "+(f[1]-" + r4(body[1]) + ")*a," + r4(body[2]) + "+(f[2]-" + r4(body[2]) + ")*a,1];";
        var eyes = addGroup(fcc, "EYES"), egc = groupContents(eyes);
        var ecodes = Fc.eye_codes, en, blinkable = "(e==0||e==1||e==2||e==3||e==4||e==5||e==8||e==9||e==12)";
        /* blink timing is a deterministic hash shared with ra_preview.py: AE's random() differs per property even with
           the same seed, which made the open and closed eye groups disagree (blank faces for a few frames) */
        var bseed = idHash(id) * 7 + 3, bp0 = R.procedural.blink_period[0], bp1 = R.procedural.blink_period[1];
        var bper = bp0 + hash01(bseed) * (bp1 - bp0), boff = hash01(bseed + 1) * bper;
        var blinkExpr = "var C=thisComp.layer(\"CTRL\");var e=Math.round(C.effect(\"eyes\")(1).value);var bo=C.effect(\"blinkOn\")(1).value;" +
            "var tt=(time+" + r4(boff) + ")%" + r4(bper) + ";var b=(bo>0.5)&&(tt<" + r4(R.procedural.blink_frames / S.fps) + ")&&" + blinkable + ";";
        for (en in ecodes) {
            if (!ecodes.hasOwnProperty(en) || !Fc.eyes[en]) { continue; }
            var eg = drawEls(egc, "E_" + en, Fc.eyes[en], D, fcolors, null);
            var code = ecodes[en];
            var cond = (en === "closed") ? "(e==" + code + "||b)" : "(e==" + code + "&&!b)";
            try { groupTr(eg).property("ADBE Vector Group Opacity").expression = blinkExpr + cond + "?100:0;"; } catch (eE) { fail("eye expression", eE); }
        }
        var gzx = "thisComp.layer(\"CTRL\").effect(\"gaze\")(1).value", gzy = "thisComp.layer(\"CTRL\").effect(\"gazeY\")(1).value";
        try { groupTr(eyes).property("ADBE Vector Position").expression = "[" + gzx + "*" + D + "," + gzy + "*" + D + "];"; } catch (eG) {}
        var mouths = addGroup(fcc, "MOUTH"), mgc = groupContents(mouths), mn, mc = Fc.mouth_codes;
        var talkExpr = "var C=thisComp.layer(\"CTRL\");var m=Math.round(C.effect(\"mouth\")(1).value);var tk=C.effect(\"talk\")(1).value;" +
            "if(tk>0.5){var f=Math.floor(time*" + R.procedural.talk_rate + ");var hx=Math.sin((f*31+" + (idHash(id) * 13) + ")*12.9898)*43758.5453;var q=hx-Math.floor(hx);" +
            "if(m==4||m==7){m=(q<0.5)?7:2;}else if(m==3){m=(q<0.5)?3:2;}else{m=(q<0.35)?1:((q<0.75)?2:0);}}";
        for (mn in mc) {
            if (!mc.hasOwnProperty(mn) || !Fc.mouths[mn] || !Fc.mouths[mn].length) { continue; }
            var mg = drawEls(mgc, "M_" + mn, Fc.mouths[mn], D, fcolors, null);
            try { groupTr(mg).property("ADBE Vector Group Opacity").expression = talkExpr + "(m==" + mc[mn] + ")?100:0;"; } catch (eM) { fail("mouth expression", eM); }
        }
        try { groupTr(mouths).property("ADBE Vector Position").expression = "[" + gzx + "*" + r4(D * num(R.face.mouth_follow, 0.6)) + "," + gzy + "*" + r4(D * num(R.face.mouth_follow_y, 0.3)) + "];"; } catch (eMP) {}
        var ofp = [];
        for (i = 0; i < hp.length; i += 1) { if (OVER_FACE[hp[i]]) { ofp.push(hp[i]); } }
        if (ofp.length) {
            var gl = shapeLayer(comp, "OVER_FACE"); parentTo(gl, headN); P_pos(gl).setValue([0, 0]);
            for (i = 0; i < ofp.length; i += 1) { drawEls(rootContents(gl), "G_" + ofp[i], DATA.parts.head[ofp[i]].els, D, colors, null); }
        }
        accessoryLayers(comp, cast, "over_face", headN, torsoN, D, id);
        holdLayers(comp, id, actorTimeline, handF, handN, "front");
        if (!nb) { try { headBack.remove(); } catch (eR) {} }
        return comp;
    }

    /* image accessories: slot head (rides the head) | torso (rides the torso frame); behind:true draws behind the body */
    function accessoryLayers(comp, cast, which, headN, torsoN, D, id) {
        var acc = cast.accessories || [], i, a, slot, of;
        for (i = 0; i < acc.length; i += 1) {
            a = acc[i];
            slot = a.slot || "head";
            of = !!a.over_face;
            if (which === "behind") { if (!a.behind) { continue; } }
            else if (which === "over_face") { if (a.behind || slot !== "head" || !of) { continue; } }
            else if (a.behind || slot !== which || (which === "head" && of)) { continue; }
            accessoryLayer(comp, a, "ACC_" + i, which, headN, torsoN, D);
        }
    }
    /* one image accessory placed on its slot (shared by the accessories and their armhole caps) */
    function accessoryLayer(comp, a, name, which, headN, torsoN, D) {
        var slot = a.slot || "head", it = importFile(absPath(B.root, a.file), B.F.foot), l, unit, w, sc;
        if (!it) { return null; }
        l = comp.layers.add(it);
        l.name = name;
        unit = slot === "torso" ? DATA.rig.torso_len : D;
        parentTo(l, slot === "torso" ? torsoN : headN);   /* over_face pieces ride the head */
        w = num(a.w, 1.1) * unit;
        P_pos(l).setValue([num(a.dx, 0) * unit, num(a.dy, -0.45) * unit]);
        if (which === "over_face" && a.follow_gaze) {   /* glasses ride the eyes */
            P_pos(l).expression = "var C=thisComp.layer(\"CTRL\");[value[0]+C.effect(\"gaze\")(1).value*" + r4(D) + ",value[1]+C.effect(\"gazeY\")(1).value*" + r4(D) + "];";
        }
        sc = w / it.width * 100;
        P_scale(l).setValue([a.flip ? -sc : sc, sc]);
        if (slot === "torso") {
            P_pos(l).expression = turnTS() + "[" + r4(turnShift()) + "*(1-tnT)+value[0]*ts,value[1]];";
            P_scale(l).expression = turnTS() + "[value[0]*ts,value[1]];";
        }
        if (a.rot) { P_rot(l).setValue(a.rot); }
        if (a.from !== undefined || a.to !== undefined) {
            var t0 = num(a.from, 0), t1 = num(a.to, B.S.duration);
            holdKeys(P_op(l), [0, Math.max(0.001, t0), Math.max(0.002, t1)], [t0 <= 0 ? 100 : 0, 100, t1 >= B.S.duration ? 100 : 0]);
        }
        return l;
    }
    /* armholes (v2.3, same as ra_rig.py): every torso garment is drawn again above the arms, matted to a disc around
       the shoulder of each arm that is in front of the body, so the arms come out from under the clothes at the
       shoulder instead of lying on the fabric */
    function armholeCaps(comp, cast, root, torsoN, D, aw, FF, TQ) {
        var r = num(DATA.rig.look.armhole_cap, 0.55) * aw, acc = cast.accessories || [], i, a, cap, m, mc, k, arms, g;
        if (r <= 0) { return; }
        arms = [["aF", FF + "ffr?100:0;"], ["aN", TQ + "?0:100;"]];
        for (i = 0; i < acc.length; i += 1) {
            a = acc[i];
            if (a.behind || (a.slot || "head") !== "torso") { continue; }
            cap = accessoryLayer(comp, a, "ACC_" + i + "_CAP", "torso", null, torsoN, D);
            if (!cap) { continue; }
            m = shapeLayer(comp, "ACC_" + i + "_ARMHOLES");
            mc = rootContents(m);
            for (k = 0; k < arms.length; k += 1) {
                g = addGroup(mc, "SH_" + arms[k][0]);
                addPathTo(groupContents(g), ellipseShape(0, 0, 2 * r, 2 * r));
                addFill(groupContents(g), [1, 1, 1], 100);
                try {
                    groupTr(g).property("ADBE Vector Position").expression = rigPrelude() + limbSolve(arms[k][0]) + "p0;";
                    groupTr(g).property("ADBE Vector Group Opacity").expression = arms[k][1];
                } catch (eA) { fail("armhole expression " + arms[k][0], eA); }
            }
            parentTo(m, root); P_pos(m).setValue([0, 0]);
            try {
                if (typeof cap.setTrackMatte === "function") { cap.setTrackMatte(m, TrackMatteType.ALPHA); }
                else { cap.trackMatteType = TrackMatteType.ALPHA; }   /* AE before 2023: the layer just above is the matte */
                m.enabled = false;
            } catch (eM) { warn("armhole matte: " + eM.toString()); }
        }
    }
    /* props held in a hand: from the actor timeline (global times). where: back (under far arm) | mid (under near arm) | front */
    function holdLayers(comp, id, tl, handF, handN, where) {
        var hs = tl.holds, i, h, it, l, fr, w, ang;
        for (i = 0; i < hs.length; i += 1) {
            h = hs[i];
            var hand = h.hand === "F" ? "F" : "N";
            var place = h.front === false ? (hand === "F" ? "back" : "mid") : (hand === "F" ? "mid" : "front");
            if (place !== where) { continue; }
            it = importFile(absPath(B.root, h.file), B.F.foot);
            if (!it) { continue; }
            l = comp.layers.add(it);
            l.name = "HOLD_" + i;
            parentTo(l, hand === "F" ? handF : handN);
            fr = h.offset || [0, 0];
            P_pos(l).setValue([fr[0], fr[1]]);
            w = num(h.w, 220);
            P_scale(l).setValue([w / it.width * 100, w / it.width * 100]);
            ang = num(h.rot, 0);
            if (h.grip && h.grip.length === 2) {
                /* held at its grip; a tool continues the forearm (tip points where the arm points), upright stays upright */
                try { P_anchor(l).setValue([h.grip[0] * it.width, h.grip[1] * it.height]); } catch (eA) { warn("hold anchor: " + eA.toString()); }
                if ((h.style || "tool") === "tool") {
                    var tp = (h.tip && h.tip.length === 2) ? h.tip : [h.grip[0], 0];
                    var th = Math.atan2((tp[1] - h.grip[1]) * it.height, (tp[0] - h.grip[0]) * it.width) * 180 / Math.PI;
                    if (h.aim && h.aim.length === 2) {   /* the tip points at a spot (a cheek being brushed) */
                        P_rot(l).expression = handPosExpr("a" + hand) + "var phi=Math.atan2(" + r4(h.aim[1]) + "-p2[1]-(" + fr[1] + ")," + r4(h.aim[0]) + "-p2[0]-(" + fr[0] + "))*180/Math.PI;phi-(" + r4(th) + ")+(" + ang + ");";
                    } else {
                        P_rot(l).expression = handAngleExpr("a" + hand) + "var phi=Math.atan2(Math.cos(al*D2R),Math.sin(al*D2R))*180/Math.PI;phi-(" + r4(th) + ")+(" + ang + ");";
                    }
                } else { P_rot(l).setValue(ang); }
            } else if (h.follow) { P_rot(l).expression = handAngleExpr("a" + hand) + "-al+" + ang + ";"; } else { P_rot(l).setValue(ang); }
            var t0 = num(h.t, 0), t1 = num(h.end, B.S.duration);
            holdKeys(P_op(l), [0, Math.max(0.001, t0), Math.max(0.002, t1)], [t0 <= 0 ? 100 : 0, 100, t1 >= B.S.duration ? 100 : 0]);
        }
    }

    /* ---------------------------------------------------------------- actor timelines (all shots merged per cast id) */
    function emptyTimeline() { return { pose: [], eyes: [], mouth: [], gaze: [], gazeY: [], walk: [], run: [], wspeed: [], armSw: [], talk: [], holds: [], flush: [] }; }
    function collectTimelines(spec) {
        var TL = {}, s, a, i, j, sh, ac, tl, k, prev, v, dur, t, keys;
        var fps = B.S.fps, f = 1 / fps;
        for (s = 0; s < spec.shots.length; s += 1) {
            sh = spec.shots[s];
            for (a = 0; a < (sh.actors || []).length; a += 1) {
                ac = sh.actors[a];
                if (!ac.cast || !spec.cast[ac.cast]) { warn("shot " + sh.id + ": actor without a known cast id"); continue; }
                tl = TL[ac.cast] || (TL[ac.cast] = emptyTimeline());
                keys = (ac.keys && ac.keys.length) ? ac.keys : [{ t: sh.t, pose: "stand" }];
                keys = stableSort(keys.slice(0), byT);
                if (keys[0].t > sh.t + 0.001) { keys.unshift({ t: sh.t, pose: keys[0].pose, eyes: keys[0].eyes, mouth: keys[0].mouth }); }
                for (i = 0; i < keys.length; i += 1) {
                    k = keys[i];
                    t = Math.max(sh.t, k.t);
                    v = poseVals(k.pose || (i ? keys[i - 1].pose : "stand"), k.set);
                    dur = (i === 0) ? f : num(k.dur, 0.22);
                    tl.pose.push({ t: t, d: dur, v: v, snap: i === 0 });
                    if (k.eyes !== undefined) { tl.eyes.push({ t: t, v: k.eyes }); } else if (i === 0) { tl.eyes.push({ t: t, v: "normal" }); }
                    if (k.mouth !== undefined) { tl.mouth.push({ t: t, v: k.mouth }); } else if (i === 0) { tl.mouth.push({ t: t, v: "none" }); }
                    if (k.gaze !== undefined) { tl.gaze.push({ t: t, v: k.gaze }); } else if (i === 0) { tl.gaze.push({ t: t, v: DATA.rig.face.gaze }); }
                    if (k.gaze_y !== undefined) { tl.gazeY.push({ t: t, v: k.gaze_y }); } else if (i === 0) { tl.gazeY.push({ t: t, v: num(DATA.rig.face.gaze_y, 0) }); }
                    if (k.face_color !== undefined && k.face_color !== null) {
                        var fcv = k.face_color, fcn = (fcv === "none" || fcv === "" || fcv === false);
                        var fhex = fcn ? null : ((DATA.rig.face_colors && DATA.rig.face_colors[fcv]) ? DATA.rig.face_colors[fcv] : fcv);
                        tl.flush.push({ t: t, d: num(k.dur, 0.35), v: fcn ? 0 : num(k.face_amount, num(DATA.rig.face_color_amount, 0.82)), c: fhex ? hex(fhex) : null });
                    }
                }
                /* locomotion: [{t, mode: walk|run|none, speed}] */
                var loco = ac.walk || [];
                tl.walk.push({ t: sh.t, v: 0, snap: true }); tl.run.push({ t: sh.t, v: 0, snap: true }); tl.armSw.push({ t: sh.t, v: 1, snap: true });
                for (i = 0; i < loco.length; i += 1) {
                    var m = loco[i].mode || "walk", tt = Math.max(sh.t, num(loco[i].t, sh.t));
                    tl.walk.push({ t: tt, v: m === "walk" ? 1 : 0 });
                    tl.run.push({ t: tt, v: m === "run" ? 1 : 0 });
                    tl.wspeed.push({ t: tt, v: num(loco[i].speed, m === "run" ? 2.4 : 1.6) });
                    tl.armSw.push({ t: tt, v: loco[i].arms === false ? 0 : 1 });
                }
                /* talk ranges */
                tl.talk.push({ t: sh.t, v: 0 });
                for (i = 0; i < (ac.talk || []).length; i += 1) {
                    tl.talk.push({ t: Math.max(sh.t, ac.talk[i][0]), v: 1 });
                    tl.talk.push({ t: Math.min(sh.end, ac.talk[i][1]), v: 0 });
                }
                for (i = 0; i < (ac.hold || []).length; i += 1) {
                    var h = ac.hold[i], hh = {}, q;
                    for (q in h) { if (h.hasOwnProperty(q)) { hh[q] = h[q]; } }
                    hh.t = Math.max(sh.t, num(h.t, sh.t)); hh.end = Math.min(sh.end, num(h.end, sh.end));
                    tl.holds.push(hh);
                }
            }
        }
        return TL;
    }
    function applyTimeline(comp, tl) {
        var ctrl = comp.layer("CTRL"), i, j, k, times, vals, fps = B.S.fps, f = 1 / fps, cur = poseVals("stand"), pts = [], p, last;
        stableSort(tl.pose, byT);
        if (tl.pose.length) { cur = tl.pose[0].v; }   /* start IN the first pose */
        for (i = 0; i < tl.pose.length; i += 1) {
            p = tl.pose[i];
            last = pts.length ? pts[pts.length - 1].t : -1;
            var t0 = Math.max(p.t, last + f * 0.5), t1 = Math.max(t0 + f * 0.5, p.t + p.d);
            pts.push({ t: t0, v: cur });
            pts.push({ t: t1, v: p.v });
            cur = p.v;
        }
        for (k = 0; k < POSE_KEYS.length; k += 1) {
            times = []; vals = [];
            for (i = 0; i < pts.length; i += 1) { times.push(pts[i].t); vals.push(pts[i].v[POSE_KEYS[k]]); }
            if (times.length) {
                var prop = effects(ctrl).property(POSE_KEYS[k]).property(1);
                try { setKeys(prop, times, vals, 62); } catch (e) { fail("pose keys " + POSE_KEYS[k], e); }
            }
        }
        var ec = DATA.faces.eye_codes, mc = DATA.faces.mouth_codes;
        function holdList(name, list, mapper, ease) {
            if (!list.length) { return; }
            stableSort(list, byT);
            var tt = [], vv = [], q;
            for (q = 0; q < list.length; q += 1) {
                if (tt.length && Math.abs(list[q].t - tt[tt.length - 1]) < 0.0005) { vv[vv.length - 1] = mapper(list[q].v); continue; }
                tt.push(list[q].t); vv.push(mapper(list[q].v));
            }
            var pr = effects(ctrl).property(name).property(1);
            try { if (ease) { setKeys(pr, tt, vv, 50); } else { holdKeys(pr, tt, vv); } } catch (e2) { fail(name + " keys", e2); }
        }
        holdList("eyes", tl.eyes, function (v) { return typeof v === "number" ? v : num(ec[v], 0); }, false);
        holdList("mouth", tl.mouth, function (v) { return typeof v === "number" ? v : num(mc[v], 0); }, false);
        holdList("gaze", tl.gaze, function (v) { return v; }, false);
        holdList("gazeY", tl.gazeY, function (v) { return v; }, false);
        if (tl.flush.length) {   /* face colour: amount fades linearly over the key's dur, colour switches at the key */
            stableSort(tl.flush, byT);
            var ft = [], fv = [], ct = [], cv = [], amt = 0, q2;
            for (q2 = 0; q2 < tl.flush.length; q2 += 1) {
                var fe = tl.flush[q2];
                ft.push(fe.t, fe.t + Math.max(1 / fps, fe.d)); fv.push(amt, fe.v); amt = fe.v;
                if (fe.c) { ct.push(fe.t); cv.push(fe.c); }
            }
            try { setKeys(effects(ctrl).property("flush").property(1), ft, fv, "linear"); } catch (eF1) { fail("face colour keys", eF1); }
            if (ct.length) { try { holdKeys(effects(ctrl).property("flushCol").property(1), ct, cv); } catch (eF2) { fail("face colour keys", eF2); } }
        }
        holdList("walk", tl.walk, function (v) { return v; }, false);
        holdList("run", tl.run, function (v) { return v; }, false);
        holdList("wspeed", tl.wspeed, function (v) { return v; }, false);
        holdList("armSw", tl.armSw, function (v) { return v; }, false);
        holdList("talk", tl.talk, function (v) { return v; }, false);
    }

    /* ================================================================= shots */
    function coverScale(item, w, h) { return Math.max(w / item.width, h / item.height) * 100; }
    var GRADES = {
        none: { desat: 0, bright: 0, contrast: 0, tint: null, tintOp: 0 },
        moody: { desat: 18, bright: -8, contrast: 6, tint: null, tintOp: 0 },
        dark: { desat: 25, bright: -22, contrast: 8, tint: "#0E1A2A", tintOp: 18 },
        night: { desat: 30, bright: -30, contrast: 10, tint: "#0A1A3A", tintOp: 30 },
        warm: { desat: 5, bright: -4, contrast: 4, tint: "#FF9A3C", tintOp: 12 },
        cold: { desat: 15, bright: -6, contrast: 6, tint: "#3C8CFF", tintOp: 14 },
        sepia: { desat: 70, bright: -6, contrast: 4, tint: "#A8743A", tintOp: 30 },
        bw: { desat: 100, bright: -6, contrast: 10, tint: null, tintOp: 0 },
        green: { desat: 20, bright: -10, contrast: 4, tint: "#3AA64A", tintOp: 30 },
        red: { desat: 20, bright: -10, contrast: 8, tint: "#C8202A", tintOp: 26 }
    };
    function applyGrade(layer, comp, gname, parentL) {
        var g = GRADES[gname || "moody"] || GRADES.moody;
        if (g.desat > 0) { var t = addFx(layer, "ADBE Tint", "Desat"); fxSet(t, 3, g.desat, "tint amount"); }
        if (g.bright || g.contrast) { var bc = addFx(layer, "ADBE Brightness & Contrast 2", "Grade"); fxSet(bc, 1, g.bright, "brightness"); fxSet(bc, 2, g.contrast, "contrast"); }
        return g;
    }
    function bgLayer(comp, sh, cam) {
        var bg = sh.bg || {}, kind = bg.kind || (bg.file ? (/\.(mp4|mov|webm|avi|m4v)$/i.test(bg.file) ? "video" : "image") : "color"), l, it;
        /* the scene: the frame, or a wider/taller world for this location (bg.world [W, H]) that the camera travels over */
        var hasW = !!(bg.world && bg.world.length === 2 && kind !== "video");
        var WW = hasW ? Math.max(comp.width, num(bg.world[0], comp.width)) : comp.width, WH = hasW ? Math.max(comp.height, num(bg.world[1], comp.height)) : comp.height;
        if (kind === "color") {
            l = solid(comp, "BG", hex(bg.color, [0.13, 0.14, 0.16]), Math.round(WW * 1.6), Math.round(WH * 1.6));
            parentTo(l, cam); P_pos(l).setValue([WW / 2, WH / 2]);
        } else {
            it = importFile(absPath(B.root, bg.file), B.F.foot);
            if (!it) { l = solid(comp, "BG_MISSING", [0.2, 0.2, 0.22], Math.round(WW * 1.6), Math.round(WH * 1.6)); parentTo(l, cam); P_pos(l).setValue([WW / 2, WH / 2]); return l; }
            l = comp.layers.add(it);
            l.name = "BG";
            parentTo(l, cam);
            var c = coverScale(it, WW, WH) * num(bg.scale, hasW ? 1.0 : 1.06);
            var pan = bg.pan || [0, 0];
            P_pos(l).setValue([WW / 2 + num(bg.offset ? bg.offset[0] : 0, 0), WH / 2 + num(bg.offset ? bg.offset[1] : 0, 0)]);
            P_scale(l).setValue([bg.flip ? -c : c, c]);
            if (pan[0] || pan[1]) {
                var p0 = P_pos(l).value;
                setKeys(P_pos(l), [sh.t, sh.end], [[p0[0], p0[1]], [p0[0] + pan[0], p0[1] + pan[1]]], "linear");
            }
            if (kind === "video") {
                l.startTime = sh.t - num(bg.start, 0) / num(bg.speed, 1);
                if (num(bg.speed, 1) !== 1) { try { l.stretch = 100 / bg.speed; } catch (eS) {} }
                try { l.audioEnabled = false; } catch (eA) {}
                if (it.duration && (sh.end - sh.t) > it.duration - num(bg.start, 0)) {
                    try { l.timeRemapEnabled = true; l.property("ADBE Time Remapping").expression = "loopOut(\"cycle\");"; } catch (eL) { warn("video loop: " + eL.toString()); }
                }
            }
        }
        applyGrade(l, comp, bg.grade || (kind === "video" ? "none" : "moody"));
        if (num(bg.blur, 0) > 0) { var gb = addFx(l, "ADBE Gaussian Blur 2", "Depth"); fxSet(gb, 1, bg.blur, "blurriness"); try { fxSet(gb, 3, 1, "repeat edge"); } catch (eB) {} }
        var gr = GRADES[bg.grade || "moody"];
        if (gr && gr.tint && gr.tintOp) {
            var tl = solid(comp, "BG_TINT", hex(gr.tint), Math.round(WW * 1.6), Math.round(WH * 1.6));
            parentTo(tl, cam); P_pos(tl).setValue([WW / 2, WH / 2]);
            P_op(tl).setValue(gr.tintOp);
            try { tl.blendingMode = BlendingMode.SOFT_LIGHT; } catch (eT) {}
            tl.moveBefore(l);
        }
        return l;
    }
    function camLayer(comp, sh) {
        var S = B.S, cam = nullLayer(comp, "CAM"), keys = sh.camera || [], i, k;
        var zfx = slider(cam, "zoom", 1), rfx = slider(cam, "roll", 0), shk = slider(cam, "shake", 0);
        var pfx = addFx(cam, "ADBE Point Control", "focus");
        pfx.property(1).setValue([S.width / 2, S.height / 2]);
        if (!keys.length) { keys = [{ t: sh.t, zoom: 1.0 }, { t: sh.end, zoom: 1.08 }]; }
        var zt = [], zv = [], ft = [], fv = [], rt = [], rv = [], eases = [];
        for (i = 0; i < keys.length; i += 1) {
            k = keys[i];
            zt.push(Math.max(0, k.t)); zv.push(num(k.zoom, 1));
            ft.push(Math.max(0, k.t)); fv.push(k.focus || [S.width / 2, S.height / 2]);
            rt.push(Math.max(0, k.t)); rv.push(num(k.roll, 0));
            eases.push(k.ease || "inout");
        }
        /* per-segment easing: the ease of key i+1 shapes the move into it */
        var zp = effects(cam).property("zoom").property(1), fp = effects(cam).property("focus").property(1), rp = effects(cam).property("roll").property(1);
        zp.setValuesAtTimes(zt, zv); fp.setValuesAtTimes(ft, fv); rp.setValuesAtTimes(rt, rv);
        for (i = 0; i < keys.length; i += 1) {
            var e = eases[i], nxt = (i + 1 < keys.length) ? eases[i + 1] : "inout", inI = 60, outI = 60;
            if (e === "out") { inI = 92; }          /* arrive very slowly at this key */
            if (e === "linear") { inI = 0.1; }
            if (e === "cut" || e === "snap") { inI = 0.1; }
            if (nxt === "out") { outI = 5; }        /* leave this key fast toward an 'out' key */
            if (nxt === "linear") { outI = 0.1; }
            if (nxt === "cut" || nxt === "snap") { outI = 0.1; }
            var props = [zp, fp, rp], q;
            for (q = 0; q < props.length; q += 1) {
                var pr = props[q], ki = pr.nearestKeyIndex(zt[i]);
                if (nxt === "cut" && q < 3) {
                    try { pr.setInterpolationTypeAtKey(ki, pr.keyInInterpolationType(ki), KeyframeInterpolationType.HOLD); } catch (eh) {}
                    continue;
                }
                try {
                    pr.setInterpolationTypeAtKey(ki, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                    var ei = [new KeyframeEase(0, inI)], eo = [new KeyframeEase(0, outI)];
                    try { pr.setTemporalEaseAtKey(ki, ei, eo); } catch (e1) { pr.setTemporalEaseAtKey(ki, [ei[0], ei[0]], [eo[0], eo[0]]); }
                } catch (ee) {}
            }
        }
        /* shake bursts */
        var sk = sh.shake || [];
        if (sk.length) {
            var st = [0], sv = [0];
            for (i = 0; i < sk.length; i += 1) {
                var a = num(sk[i].amp, 16), t0 = sk[i].t, d = num(sk[i].dur, 0.4);
                st.push(t0 - 0.01, t0, t0 + d); sv.push(0, a, 0);
            }
            try { setKeys(effects(cam).property("shake").property(1), st, sv, "linear"); } catch (eK) { warn("shake keys: " + eK.toString()); }
        }
        var C = "[" + S.width / 2 + "," + S.height / 2 + "]";
        P_pos(cam).expression = "var z=effect(\"zoom\")(1).value,f=effect(\"focus\")(1).value,sk=effect(\"shake\")(1).value;" +
            "var C=" + C + ";var wx=0,wy=0;if(sk>0){var wg=wiggle(18,sk);wx=wg[0]-value[0];wy=wg[1]-value[1];}[C[0]-z*f[0]+wx,C[1]-z*f[1]+wy];";
        P_scale(cam).expression = "var z=effect(\"zoom\")(1).value*100;[z,z];";
        P_rot(cam).expression = "effect(\"roll\")(1).value;";
        return cam;
    }

    function actorLayers(comp, sh, ac, idx, cam, charComp) {
        var S = B.S, R = DATA.rig, cast = B.spec.cast[ac.cast] || {};
        var s = num(ac.h, 900) / R.H, face = num(ac.face, 1) < 0 ? -1 : 1;
        var rootN = nullLayer(comp, "A" + idx + "_" + ac.cast);
        parentTo(rootN, cam);
        var mv = ac.move || [], i, mt = [], mvv = [];
        var x0 = num(ac.x, S.width / 2), y0 = num(ac.y, S.height * 0.86);
        P_pos(rootN).setValue([x0, y0]);
        if (mv.length) {
            for (i = 0; i < mv.length; i += 1) { mt.push(Math.max(0, mv[i].t)); mvv.push([num(mv[i].x, x0), num(mv[i].y, y0)]); }
            setKeys(P_pos(rootN), mt, mvv, mv[mv.length - 1].ease || "linear");
        }
        var sc = s * 100;
        P_scale(rootN).setValue([sc * face, sc]);
        if (ac.flip && ac.flip.length) {
            var ft = [sh.t], fv = [[sc * face, sc]];
            for (i = 0; i < ac.flip.length; i += 1) { ft.push(ac.flip[i][0]); fv.push([sc * (ac.flip[i][1] < 0 ? -1 : 1), sc]); }
            holdKeys(P_scale(rootN), ft, fv);
        }
        if (ac.rot) { P_rot(rootN).setValue(ac.rot); }
        if (ac.tilt && ac.tilt.length) {   /* whole-body rotation (topple): 'in' = accelerating fall */
            var tk = stableSort(ac.tilt.slice(0), byT), tt2 = [], tv2 = [], ein = false;
            for (i = 0; i < tk.length; i += 1) { tt2.push(Math.max(0, tk[i].t)); tv2.push(num(ac.rot, 0) + num(tk[i].rot, 0)); if (tk[i].ease === "in") { ein = true; } }
            try { setKeys(P_rot(rootN), tt2, tv2, ein ? "in" : 60); } catch (eT) { warn("tilt keys: " + eT.toString()); }
        }
        /* entrances / exits */
        var en = ac.enter, ex = ac.exit, pz = P_pos(rootN);
        if (en && en.from) {
            var tIn = num(en.t, sh.t), dIn = num(en.dur, 0.35), pv = pz.value;
            if (en.from === "pop") { popIn(P_scale(rootN), tIn, sc, S.fps); if (face < 0) { P_scale(rootN).expression = "[-Math.abs(value[0]),value[1]];"; } }
            else {
                /* lookup, not a chained ternary: ExtendScript mis-evaluates a ? b : c ? d : e */
                var OFFS_IN = { left: [-S.width * 0.45, 0], right: [S.width * 0.45, 0], bottom: [0, S.height * 0.5], top: [0, -S.height * 0.6] };
                var off = OFFS_IN[en.from] || OFFS_IN.top;
                if (!mv.length) { setKeys(pz, [tIn, tIn + dIn], [[pv[0] + off[0], pv[1] + off[1]], [pv[0], pv[1]]], "out"); }
            }
        }
        if (ex && ex.to) {
            var tOut = num(ex.t, sh.end - 0.3), dOut = num(ex.dur, 0.35), pv2 = pz.valueAtTime(tOut, false);
            if (ex.to === "pop") { popOut(P_scale(rootN), tOut + dOut, sc, S.fps); }
            else {
                var OFFS_OUT = { left: [-S.width * 0.6, 0], right: [S.width * 0.6, 0], bottom: [0, S.height * 0.5], top: [0, -S.height * 0.7] };
                var off2 = OFFS_OUT[ex.to] || OFFS_OUT.top;
                setKeys(pz, [tOut, tOut + dOut], [[pv2[0], pv2[1]], [pv2[0] + off2[0], pv2[1] + off2[1]]], "in");
            }
        }
        /* layers: shadow, glow, outline, art (bottom -> top) */
        var look = R.look, layers = [];
        if (ac.shadow !== false) {
            var shd = shapeLayer(comp, "A" + idx + "_SHADOW");
            var sgc = groupContents(addGroup(rootContents(shd), "S"));
            addPathTo(sgc, ellipseShape(0, 0, 560, 70)); addFill(sgc, [0, 0, 0], 100);
            parentTo(shd, rootN); P_pos(shd).setValue([0, -6]);
            P_op(shd).setValue(look.shadow_opacity * 100);
            var bl = addFx(shd, "ADBE Gaussian Blur 2"); fxSet(bl, 1, 22, "blur");
            layers.push(shd);
        }
        var glow = num(cast.glow, look.glow_default), gl = null;
        if (glow > 0) {
            gl = comp.layers.add(charComp); gl.name = "A" + idx + "_GLOW";
            parentTo(gl, rootN); P_anchor(gl).setValue(R.origin); P_pos(gl).setValue([0, 0]);
            var gb = addFx(gl, "ADBE Gaussian Blur 2"); fxSet(gb, 1, look.glow_radius * 1.6, "glow blur");
            try { gl.blendingMode = BlendingMode.SCREEN; } catch (eb) {}
            P_op(gl).setValue(clamp(glow * 100, 0, 100));
            layers.push(gl);
        }
        var ol = comp.layers.add(charComp); ol.name = "A" + idx + "_OUTLINE";
        parentTo(ol, rootN); P_anchor(ol).setValue(R.origin); P_pos(ol).setValue([0, 0]);
        var ck = addFx(ol, "ADBE Simple Choker"); /* outline_px is in rig units (scales with the character); +1/s offsets the anti-aliased edge Simple Choker eats */
        fxSet(ck, 2, -clamp(look.outline_px + 1 / Math.max(0.15, s), 1, 60), "choke");
        var olc = cast.outline ? hex(cast.outline) : shade(hex(cast.color, [0.35, 0.88, 0.96]), num(look.outline_shade, 0.42));
        var fl = addFx(ol, "ADBE Fill"); fxSet(fl, 3, olc, "outline colour");
        layers.push(ol);
        var art = comp.layers.add(charComp); art.name = "A" + idx + "_" + ac.cast;
        parentTo(art, rootN); P_anchor(art).setValue(R.origin); P_pos(art).setValue([0, 0]);
        if (num(look.bevel, 0) > 0) {   /* legacy emboss; the reference look is soft per-part shading inside the character comp */
            var bv = addFx(art, "ADBE Bevel Alpha"); fxSet(bv, 1, look.bevel_thickness, "edge thickness"); fxSet(bv, 2, -45, "light angle"); fxSet(bv, 4, look.bevel, "light intensity");
        }
        layers.push(art);
        /* states over time: gray | silhouette | red | sick | ghost */
        if ((ac.state && ac.state !== "color") || (ac.states && ac.states.length)) { actorStates(art, ol, glow > 0 ? gl : null, ac, sh); }
        for (i = 0; i < layers.length; i += 1) { setInOut(layers[i], sh.t - 0.5, sh.end + 0.5); }
        setInOut(rootN, sh.t - 0.5, sh.end + 0.5);
        return { root: rootN, top: art, bottom: layers[0] };
    }
    /* Effective actor state over the shot: a timed entry of ac.states replaces the base ac.state while it runs
       (later entries win), exactly like ra_preview.py. Returns segments [{t, state, fade}] with no repeats. */
    function stateSegments(ac, sh) {
        var base = (ac.state && ac.state !== "color") ? ac.state : "color";
        var st = ac.states || [], pts = [sh.t, sh.end], i, j, seg = [], u = [];
        for (i = 0; i < st.length; i += 1) { pts.push(num(st[i].t, sh.t), num(st[i].end, sh.end)); }
        pts.sort(function (x, y) { return x - y; });
        for (i = 0; i < pts.length; i += 1) {
            if (pts[i] < sh.t - 0.0001 || pts[i] > sh.end + 0.0001) { continue; }
            if (!u.length || pts[i] - u[u.length - 1] > 0.0005) { u.push(pts[i]); }
        }
        for (i = 0; i < u.length - 1; i += 1) {
            var mid = (u[i] + u[i + 1]) / 2, eff = base, fd = 0.12;
            for (j = 0; j < st.length; j += 1) {
                if (num(st[j].t, sh.t) <= mid && mid < num(st[j].end, sh.end)) { eff = st[j].state || "color"; fd = num(st[j].fade, 0.2); }
            }
            if (!seg.length || seg[seg.length - 1].state !== eff) { seg.push({ t: u[i], state: eff, fade: Math.max(0.01, fd) }); }
        }
        if (!seg.length) { seg.push({ t: sh.t, state: base, fade: 0.01 }); }
        return seg;
    }
    /* keys a property so it is `on` while the effective state is nm and `off` otherwise */
    function stateKeys(prop, seg, nm, on, off, sh) {
        var tt = [sh.t - 0.5], vv = [seg[0].state === nm ? on : off], i, cur = vv[0];
        for (i = 1; i < seg.length; i += 1) {
            var nv = seg[i].state === nm ? on : off;
            if (nv === cur) { continue; }
            tt.push(seg[i].t, seg[i].t + seg[i].fade); vv.push(cur, nv); cur = nv;
        }
        if (tt.length === 1) { prop.setValue(vv[0]); return; }
        setKeys(prop, tt, vv, "linear");
    }
    function actorStates(art, ol, gl, ac, sh) {
        var MAP = { gray: [[0.08, 0.08, 0.08], [0.92, 0.92, 0.92]], red: [[0.35, 0.02, 0.02], [1, 0.45, 0.42]], sick: [[0.05, 0.25, 0.05], [0.7, 1, 0.55]] };
        var seg = stateSegments(ac, sh), used = {}, i, nm;
        for (i = 0; i < seg.length; i += 1) { used[seg[i].state] = true; }
        for (nm in MAP) {
            if (!MAP.hasOwnProperty(nm) || !used[nm]) { continue; }
            var targets = [art];
            if (gl && nm === "gray") { targets.push(gl); }
            for (i = 0; i < targets.length; i += 1) {
                var t = addFx(targets[i], "ADBE Tint", "STATE_" + nm);
                fxSet(t, 1, MAP[nm][0], "map black"); fxSet(t, 2, MAP[nm][1], "map white");
                var amt = fxProp(t, 3);
                if (amt) { try { stateKeys(amt, seg, nm, nm === "sick" ? 65 : 100, 0, sh); } catch (e) { warn("state keys " + nm + ": " + e.toString()); } }
            }
        }
        if (used.silhouette) {
            /* flat ink silhouette (no face, no bevel), glow off. A Tint with both colours equal is flat and its
               Amount blends with the original; a Fill effect cannot be used: Fill at 0% opacity hides the layer. */
            var sf = addFx(art, "ADBE Tint", "STATE_silhouette");
            fxSet(sf, 1, [0.04, 0.04, 0.04], "silhouette black"); fxSet(sf, 2, [0.04, 0.04, 0.04], "silhouette white");
            var sop = fxProp(sf, 3);
            if (sop) { try { stateKeys(sop, seg, "silhouette", 100, 0, sh); } catch (e2) { warn("silhouette keys: " + e2.toString()); } }
            if (gl) { try { stateKeys(P_op(gl), seg, "silhouette", 0, P_op(gl).value, sh); } catch (e3) { warn("silhouette glow: " + e3.toString()); } }
        }
        if (used.ghost) {
            var gls = [art, ol];
            for (i = 0; i < gls.length; i += 1) { try { stateKeys(P_op(gls[i]), seg, "ghost", 45, 100, sh); } catch (eg) {} }
        }
    }

    function propLayer(comp, sh, p, idx, cam) {
        var S = B.S, it = importFile(absPath(B.root, p.file), B.F.foot);
        if (!it) { return null; }
        var l = comp.layers.add(it);
        l.name = "PROP" + idx + "_" + (p.id || "");
        if (p.screen) { /* locked to the frame */ } else { parentTo(l, cam); }
        var w = num(p.w, 300), sc = w / it.width * 100, t0 = num(p.t, sh.t), t1 = num(p.end, sh.end);
        P_pos(l).setValue([num(p.x, S.width / 2), num(p.y, S.height / 2)]);
        P_scale(l).setValue([p.flip ? -sc : sc, sc]);
        if (p.rot) { P_rot(l).setValue(p.rot); }
        var anim = p.anim || "none";
        if (p.pop !== false && t0 > sh.t + 0.02) { popIn(P_scale(l), t0, sc, S.fps); if (p.flip) { P_scale(l).expression = "[-Math.abs(value[0]),value[1]];"; } }
        if (p.pop_out && t1 < sh.end - 0.02) { popOut(P_scale(l), t1, sc, S.fps); }
        if (anim === "float") { P_pos(l).expression = "[value[0],value[1]+Math.sin(time*2.4+" + idx + ")*" + num(p.amp, 10) + "];"; }
        else if (anim === "bob") { P_rot(l).expression = "value+Math.sin(time*3+" + idx + ")*" + num(p.amp, 6) + ";"; }
        else if (anim === "spin") { P_rot(l).expression = "value+(time-" + t0 + ")*" + num(p.speed, 200) + ";"; }
        else if (anim === "shake") { P_pos(l).expression = "wiggle(16," + num(p.amp, 8) + ");"; }
        else if (anim === "fall") { var y0 = num(p.from_y, -200); setKeys(P_pos(l), [t0, t0 + num(p.dur, 0.6)], [[P_pos(l).value[0], y0], P_pos(l).value], "in"); }
        else if (anim === "slide") { var dx = num(p.dx, -400); setKeys(P_pos(l), [t0, t0 + num(p.dur, 0.35)], [[P_pos(l).value[0] + dx, P_pos(l).value[1]], P_pos(l).value], "out"); }
        else if (anim === "grow") { setKeys(P_scale(l), [t0, t1], [[sc * 0.85, sc * 0.85], [sc * 1.08, sc * 1.08]], "linear"); }
        else if (anim === "drift") { setKeys(P_pos(l), [t0, t1], [P_pos(l).value, [P_pos(l).value[0] + num(p.dx, 120), P_pos(l).value[1] + num(p.dy, 0)]], "linear"); }
        if (p.shadow !== false) { var ds = addFx(l, "ADBE Drop Shadow"); fxSet(ds, 2, 140, "opacity"); fxSet(ds, 3, 160, "direction"); fxSet(ds, 4, 10, "distance"); fxSet(ds, 5, 24, "softness"); }
        if (p.outline) { var olf = addFx(l, "ADBE Bevel Alpha"); fxSet(olf, 1, 4, "edge"); fxSet(olf, 4, 0.3, "intensity"); }
        if (p.blend === "screen") { try { l.blendingMode = BlendingMode.SCREEN; } catch (e1) {} }
        if (p.blend === "add") { try { l.blendingMode = BlendingMode.ADD; } catch (e2) {} }
        if (num(p.opacity, 100) < 100) { P_op(l).setValue(p.opacity); }
        setInOut(l, t0 - (p.exact ? 0 : 0.05), t1);   // exact: back-to-back frames (gait cycles) never overlap
        return l;
    }

    /* living creatures (creatures.py): every copy of a flock is a footage layer anchored at its feet; position,
       scale and rotation run the same deterministic behaviour maths as the preview - breathing, looking around,
       walking, pecking, hopping, flying, swimming */
    function crHash(n) { var x = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); }
    function crCopy(c, i) {
        var seed = idHash(c.id || "creature") + 101 * i, sp = c.spread || [0, 0];
        if (i === 0) { return { seed: seed, dx: 0, dy: 0, k: 1 }; }
        return { seed: seed, dx: (crHash(seed + 1) - 0.5) * num(sp[0], 0), dy: (crHash(seed + 2) - 0.5) * num(sp[1], 0), k: 0.88 + 0.24 * crHash(seed + 3) };
    }
    function creatureExpr(c, sh, cp) {
        var t0 = num(c.t, sh.t), H = num(c.h, 200) * cp.k, x0 = num(c.x, 540) + cp.dx, y0 = num(c.y, 1750) + cp.dy;
        var sp = num(c.speed, 1), f0 = num(c.dir, 1) >= 0 ? 1 : -1, art = c.faces === "left" ? -1 : 1;
        var R = num(c.range, Math.min(260, 1.6 * H)), beh = c.behave || "idle";
        var e = "function h(n){var x=Math.sin(n*12.9898+78.233)*43758.5453;return x-Math.floor(x);}" +
            "function sm(v){v=Math.max(0,Math.min(1,v));return v*v*(3-2*v);}" +
            "function st(t){var TAU=2*Math.PI,u=t-" + t0 + ",H=" + H + ",x0=" + x0 + ",y0=" + y0 + ",sp=" + sp + ",f0=" + f0 + ",R=" + R + ",sd=" + cp.seed + ";" +
            "var ph=h(sd+7)*6.2832,x=x0,y=y0,fl=f0,rot=0;" +
            "var br=" + (beh === "sleep" ? "0.05*Math.sin(TAU*0.35*u+ph)" : "0.03*Math.sin(TAU*1.4*u+ph)") + ";var sy=1+br,sx=1-0.5*br;";
        if (beh === "wander" || beh === "peck" || beh === "hop") {
            e += "var T=(2.2+1.4*h(sd+11))/sp,q=(u+h(sd+13)*T)/T,n=Math.floor(q),v=q-n;" +
                "var xa=x0+(h(sd+31+(n-1)*17)-0.5)*2*R,xb=x0+(h(sd+31+n*17)-0.5)*2*R,mf=" + (beh === "hop" ? 0.6 : 0.5) + ";" +
                "var k=v<mf?sm(v/mf):1;x=xa+(xb-xa)*k;fl=xb>=xa?1:-1;var mv=(v<mf&&Math.abs(xb-xa)>6)?1:0;";
            if (beh === "hop") { e += "var w=(v/mf*2)%1;y=y0-mv*0.35*H*4*w*(1-w);rot=-fl*9*(1-2*w)*mv;"; }
            else { e += "var stp=3.6*sp;y=y0-mv*0.045*H*Math.abs(Math.sin(Math.PI*stp*u));rot=mv*5*Math.sin(Math.PI*stp*u);"; }
            if (beh === "peck") {
                e += "if(mv<0.5){var w2=(v-mf)/(1-mf),pk=0;if(w2>=0.12&&w2<0.34){pk=Math.sin(Math.PI*(w2-0.12)/0.22);}" +
                    "else if(w2>=0.58&&w2<0.8){pk=Math.sin(Math.PI*(w2-0.58)/0.22);}rot=fl*30*pk;x+=fl*0.05*H*pk;}";
            }
        } else if (beh === "walk" || beh === "flee") {
            var fast = beh === "flee", cx = num(c.x, 540), cy = num(c.y, 1750);
            var to = c.to || [cx + f0 * (fast ? 1100 : 420), cy];
            var dx = num(to[0], cx) - cx, dy = num(to[1], cy) - cy, spd = num(c.px_s, fast ? 680 : 210) * sp;
            var dur = Math.max(0.3, Math.sqrt(dx * dx + dy * dy) / spd);
            e += "var k=Math.min(1,Math.max(0,u)/" + dur + ");x=x0+(" + dx + ")*k;y=y0+(" + dy + ")*k;fl=" + (dx >= 0 ? 1 : -1) + ";" +
                "var mv=k<1?1:0,stp=" + (fast ? 5.5 : 3.4) + "*sp;y-=mv*" + (fast ? 0.07 : 0.045) + "*H*Math.abs(Math.sin(Math.PI*stp*u));" +
                "rot=mv*(" + (fast ? 8 : 5) + "*Math.sin(Math.PI*stp*u)+fl*" + (fast ? 10 : 0) + ");";
        } else if (beh === "fly") {
            e += "var A=" + num(c.range, 260) + ",a1=TAU*0.21*sp*u+ph,a2=TAU*0.33*sp*u+ph*1.7;x=x0+A*Math.sin(a1);y=y0+0.35*A*Math.sin(a2);" +
                "fl=Math.cos(a1)>=0?1:-1;sy*=1+0.16*Math.sin(TAU*7.5*u);rot=fl*6*Math.cos(a2);";
        } else if (beh === "swim") {
            e += "var A=" + num(c.range, 220) + ",a1=TAU*0.13*sp*u+ph;x=x0+A*Math.sin(a1);y=y0+0.06*H*Math.sin(TAU*0.6*u+ph);" +
                "fl=Math.cos(a1)>=0?1:-1;rot=7*Math.sin(TAU*2.3*u+ph);sx*=1+0.04*Math.sin(TAU*2.3*u+ph+1.2);";
        } else if (beh === "idle") {
            e += "var P=(2.6+2.2*h(sd+5))/sp,n=Math.floor((u+h(sd+6)*P)/P);fl=h(sd+n*7+1)<0.65?f0:-f0;rot=2.5*Math.sin(TAU*0.6*u+ph);";
        }
        e += "return [x,y,sx*fl*(" + art + "),sy,rot];}";
        return e;
    }
    function creatureLayers(comp, sh, c, idx, cam) {
        var it = importFile(absPath(B.root, c.file), B.F.foot);
        if (!it) { return; }
        var n = Math.max(1, Math.round(num(c.count, 1))), order = [], i;
        for (i = 0; i < n; i += 1) { order.push({ i: i, dy: crCopy(c, i).dy }); }
        stableSort(order, function (a, b) { if (a.dy !== b.dy) { return a.dy - b.dy; } return a.i - b.i; });   /* further back first */
        var t0 = num(c.t, sh.t), t1 = num(c.end, sh.end);
        for (i = 0; i < order.length; i += 1) {
            var cp = crCopy(c, order[i].i), l = comp.layers.add(it);
            l.name = "CREATURE " + (sh.id || "") + " " + idx + " " + order[i].i + " " + (c.id || "");
            parentTo(l, cam);
            P_anchor(l).setValue([it.width / 2, it.height]);
            var sc = num(c.h, 200) * cp.k / it.height * 100;
            P_scale(l).setValue([sc, sc]);
            if (c.pop !== false && t0 > sh.t + 0.02) { popIn(P_scale(l), t0, sc, B.S.fps); }
            if (c.pop_out && t1 < sh.end - 0.02) { popOut(P_scale(l), t1, sc, B.S.fps); }
            var fn = creatureExpr(c, sh, cp);
            try {
                P_pos(l).expression = fn + "var s=st(time);[s[0],s[1]];";
                P_scale(l).expression = fn + "var s=st(time);[value[0]*s[2],value[1]*s[3]];";
                P_rot(l).expression = fn + "st(time)[4];";
            } catch (eC) { fail("creature expression " + (c.id || idx), eC); }
            if (c.shadow !== false) { var ds = addFx(l, "ADBE Drop Shadow"); fxSet(ds, 2, 140, "opacity"); fxSet(ds, 3, 160, "direction"); fxSet(ds, 4, 10, "distance"); fxSet(ds, 5, 24, "softness"); }
            setInOut(l, t0 - 0.05, t1);
        }
    }

    /* bubbles, badges, emoji icons */
    function iconLayer(comp, sh, ic, idx, cam) {
        var S = B.S, kind = ic.kind || "emoji", t0 = num(ic.t, sh.t), t1 = num(ic.end, sh.end), size = num(ic.size, 220);
        var x = num(ic.x, S.width / 2), y = num(ic.y, S.height * 0.35), it = ic.file ? importFile(absPath(B.root, ic.file), B.F.foot) : null;
        var hostN = nullLayer(comp, "ICON" + idx + "_" + kind);
        if (!ic.screen) { parentTo(hostN, cam); }
        P_pos(hostN).setValue([x, y]);
        var made = [], l, gc, i;
        if (kind === "thought" || kind === "speech") {
            l = shapeLayer(comp, "ICON" + idx + "_BUBBLE");
            var rc = rootContents(l), w = size * 1.5, h = size * 1.15;
            if (kind === "thought") {
                var blobs = [[0, 0, w, h], [-w * 0.32, -h * 0.18, w * 0.55, h * 0.6], [w * 0.3, -h * 0.2, w * 0.55, h * 0.62], [-w * 0.28, h * 0.22, w * 0.5, h * 0.5], [w * 0.3, h * 0.2, w * 0.5, h * 0.52], [0, -h * 0.34, w * 0.6, h * 0.5]];
                var tail = ic.tail || [-0.5, 0.9];
                gc = groupContents(addGroup(rc, "CLOUD"));
                for (i = 0; i < blobs.length; i += 1) { addPathTo(gc, ellipseShape(blobs[i][0], blobs[i][1], blobs[i][2], blobs[i][3])); }
                try { liveOf(gc).addProperty("ADBE Vector Filter - Merge"); } catch (eMg) {}
                addFill(gc, [1, 1, 1], 100); addStroke(gc, [0.12, 0.12, 0.12], 6, 100);
                var g2 = groupContents(addGroup(rc, "DOTS"));
                addPathTo(g2, ellipseShape(tail[0] * w * 0.62, tail[1] * h * 0.62, size * 0.22, size * 0.18));
                addPathTo(g2, ellipseShape(tail[0] * w * 0.9, tail[1] * h * 0.98, size * 0.13, size * 0.11));
                addFill(g2, [1, 1, 1], 100); addStroke(g2, [0.12, 0.12, 0.12], 5, 100);
            } else {
                var tl2 = ic.tail || [-0.35, 0.6];
                gc = groupContents(addGroup(rc, "BALLOON"));
                addPathTo(gc, ellipseShape(0, 0, w, h * 0.92));
                addPathTo(gc, makeShape([[tl2[0] * w * 0.35 - 30, h * 0.3], [tl2[0] * w * 0.35 + 30, h * 0.3], [tl2[0] * w * 0.9, tl2[1] * h * 1.2]], true, false));
                try { liveOf(gc).addProperty("ADBE Vector Filter - Merge"); } catch (eMg2) {}
                addFill(gc, [1, 1, 1], 100); addStroke(gc, [0.12, 0.12, 0.12], 6, 100);
            }
            parentTo(l, hostN); P_pos(l).setValue([0, 0]);
            var ds = addFx(l, "ADBE Drop Shadow"); fxSet(ds, 2, 110, "opacity"); fxSet(ds, 4, 8, "distance"); fxSet(ds, 5, 18, "softness");
            made.push(l);
        }
        if (kind === "badge") {
            l = shapeLayer(comp, "ICON" + idx + "_BADGE");
            var brc = rootContents(l);
            var ring = groupContents(addGroup(brc, "RING"));
            addPathTo(ring, ellipseShape(0, 0, size * 1.25, size * 1.25)); addFill(ring, hex(ic.ring, [0.24, 0.21, 0.22]), 100); addStroke(ring, [0.08, 0.07, 0.07], 6, 100);
            var faceG = groupContents(addGroup(brc, "FACE"));
            addPathTo(faceG, ellipseShape(0, 0, size * 0.98, size * 0.98)); addFill(faceG, hex(ic.face, [0.42, 0.36, 0.38]), 100);
            var ticks = groupContents(addGroup(brc, "TICKS"));
            for (i = 0; i < 12; i += 1) {
                var a = i / 12 * Math.PI * 2, r1 = size * 0.53, r2 = size * 0.58;
                addPathTo(ticks, makeShape([[Math.sin(a) * r1, -Math.cos(a) * r1], [Math.sin(a) * r2, -Math.cos(a) * r2]], false, false));
            }
            addStroke(ticks, [0.92, 0.88, 0.86], 5, 100);
            parentTo(l, hostN); P_pos(l).setValue([0, 0]);
            var bvl = addFx(l, "ADBE Bevel Alpha"); fxSet(bvl, 1, 8, "edge"); fxSet(bvl, 4, 0.5, "intensity");
            var dsb = addFx(l, "ADBE Drop Shadow"); fxSet(dsb, 2, 140, "opacity"); fxSet(dsb, 4, 8, "distance"); fxSet(dsb, 5, 16, "softness");
            made.push(l);
        }
        if (it) {
            l = comp.layers.add(it); l.name = "ICON" + idx + "_IMG";
            parentTo(l, hostN);
            var isz = (kind === "thought" || kind === "speech") ? size * 0.72 : (kind === "badge" ? size * 0.7 : size);
            var s2 = isz / Math.max(it.width, it.height) * 100;
            P_pos(l).setValue([0, kind === "thought" ? -size * 0.04 : 0]);
            P_scale(l).setValue([s2, s2]);
            if (kind === "emoji") { var dse = addFx(l, "ADBE Drop Shadow"); fxSet(dse, 2, 120, "opacity"); fxSet(dse, 4, 8, "distance"); fxSet(dse, 5, 18, "softness"); }
            made.push(l);
        }
        if (ic.no) {
            l = shapeLayer(comp, "ICON" + idx + "_NO");
            var ngc = groupContents(addGroup(rootContents(l), "NO")), rr2 = size * 0.42;
            addPathTo(ngc, ellipseShape(0, 0, rr2 * 2, rr2 * 2));
            addPathTo(ngc, makeShape([[-rr2 * 0.7, -rr2 * 0.7], [rr2 * 0.7, rr2 * 0.7]], false, false));
            addStroke(ngc, [0.9, 0.12, 0.12], size * 0.09, 100);
            parentTo(l, hostN); P_pos(l).setValue([0, 0]);
            made.push(l);
        }
        if (ic.text) {
            var tlay = comp.layers.addText(String(ic.text));
            tlay.name = "ICON" + idx + "_TEXT";
            var tdp = tlay.property("ADBE Text Properties").property("ADBE Text Document"), td = tdp.value;
            td.fontSize = num(ic.text_size, size * 0.62);
            try { td.font = B.font; } catch (eTF) {}
            td.applyFill = true; td.fillColor = hex(ic.text_color, [0.91, 0.13, 0.16]);
            td.applyStroke = true; td.strokeColor = [0.1, 0.05, 0.05]; td.strokeWidth = Math.max(4, size * 0.04); td.strokeOverFill = false;
            td.justification = ParagraphJustification.CENTER_JUSTIFY;
            tdp.setValue(td);
            P_anchor(tlay).expression = "var r=sourceRectAtTime(time,false);[r.left+r.width/2,r.top+r.height/2];";
            parentTo(tlay, hostN); P_pos(tlay).setValue(ic.text_pos || [0, 0]);
            var dst = addFx(tlay, "ADBE Drop Shadow"); fxSet(dst, 2, 200, "opacity"); fxSet(dst, 4, 5, "distance"); fxSet(dst, 5, 0, "softness");
            made.push(tlay);
        }
        /* pop the whole icon via the host null */
        var hs = num(ic.scale, 100);
        P_scale(hostN).setValue([hs, hs]);
        if (ic.pop !== false) { popIn(P_scale(hostN), t0, hs, S.fps, 3); }
        if (ic.pop_out !== false && t1 < sh.end - 0.05) { popOut(P_scale(hostN), t1, hs, S.fps, 3); }
        if (ic.anim === "float" || (kind !== "badge" && ic.anim !== "none")) { P_pos(hostN).expression = "[value[0],value[1]+Math.sin(time*2.6+" + idx + ")*" + num(ic.amp, 8) + "];"; }
        if (ic.anim === "spin") { P_rot(hostN).expression = "value+Math.sin(time*5)*8;"; }
        for (i = 0; i < made.length; i += 1) { setInOut(made[i], t0 - 0.05, t1 + 0.05); }
        setInOut(hostN, t0 - 0.05, t1 + 0.05);
        return made;
    }

    /* overlays: image_rain (money/leaves/paper), embers, rain, smoke, tint, glitch, flash, video (fire/smoke on black) */
    function fxLayers(comp, sh, fx, idx, cam) {
        var S = B.S, kind = fx.kind, t0 = num(fx.t, sh.t), t1 = num(fx.end, sh.end), i, l, made = [];
        if (kind === "image_rain" || kind === "money_rain") {
            var it = importFile(absPath(B.root, fx.file), B.F.foot);
            if (!it) { return made; }
            var n = num(fx.count, 36), area = fx.area || [-80, S.width + 80];
            for (i = 0; i < n; i += 1) {
                l = comp.layers.add(it); l.name = "FX" + idx + "_RAIN_" + i;
                if (!fx.screen) { parentTo(l, cam); }
                var w = rr(num(fx.min_w, 90), num(fx.max_w, 170)), sc = w / it.width * 100;
                P_scale(l).setValue([sc, sc]);
                var x = rr(area[0], area[1]), sp = rr(num(fx.speed, 520) * 0.7, num(fx.speed, 520) * 1.3), ph = rr(0, 6.28), y0 = rr(-S.height * 0.9, S.height * 0.2);
                if (fx.pile && i < n * 0.35) {
                    P_pos(l).setValue([x, rr(S.height * 0.82, S.height * 0.97)]); P_rot(l).setValue(rr(-40, 40));
                } else {
                    P_pos(l).expression = "var t=time-" + r4(t0) + ";var H=" + S.height + ";var y=" + r4(y0) + "+t*" + r4(sp) + ";var M=H+600;y=(((y+300)%M)+M)%M-300;[" + r4(x) + "+Math.sin(t*1.7+" + r4(ph) + ")*60,y];";
                    P_rot(l).expression = "Math.sin((time-" + r4(t0) + ")*2.3+" + r4(ph) + ")*35;";
                    P_scale(l).expression = "var k=Math.cos((time-" + r4(t0) + ")*3.1+" + r4(ph) + ");[value[0]*(0.35+0.65*Math.abs(k)),value[1]];";
                }
                setInOut(l, t0, t1); made.push(l);
            }
            return made;
        }
        if (kind === "embers" || kind === "dust" || kind === "snow") {
            var n2 = num(fx.count, kind === "snow" ? 60 : 36), col = hex(fx.color, kind === "embers" ? [1, 0.55, 0.15] : [1, 1, 1]);
            for (i = 0; i < n2; i += 1) {
                l = shapeLayer(comp, "FX" + idx + "_" + kind + "_" + i);
                var gc = groupContents(addGroup(rootContents(l), "P")), d = rr(num(fx.min_size, 4), num(fx.max_size, 10));
                addPathTo(gc, ellipseShape(0, 0, d, kind === "embers" ? d * 1.6 : d)); addFill(gc, col, 100);
                var xx = rr(0, S.width), yy = rr(0, S.height), vy = kind === "snow" ? rr(60, 140) : -rr(80, 220), ph2 = rr(0, 6.28);
                P_pos(l).expression = "var t=time;var H=" + S.height + ";var y=" + r4(yy) + "+t*" + r4(vy) + ";y=((y%H)+H)%H;[" + r4(xx) + "+Math.sin(t*1.3+" + r4(ph2) + ")*40,y];";
                P_op(l).expression = "50+50*Math.sin(time*4+" + r4(ph2) + ");";
                if (kind === "embers") { var g = addFx(l, "ADBE Glo2"); fxSet(g, 3, 14, "radius"); fxSet(g, 4, 1.5, "intensity"); }
                setInOut(l, t0, t1); made.push(l);
            }
            return made;
        }
        if (kind === "rain") {
            l = solid(comp, "FX" + idx + "_RAIN", [0, 0, 0]);
            var cr = null;
            try { cr = addFx(l, "CC Rainfall"); } catch (eR) { warn("CC Rainfall unavailable: " + eR.toString()); }
            if (cr) { try { liveOf(cr).property("Drops").setValue(num(fx.count, 3000)); } catch (e1) {} try { liveOf(cr).property("Influence %").setValue(0); } catch (e2) {} try { liveOf(cr).property("Opacity").setValue(num(fx.opacity, 40)); } catch (e3) {} }
            try { l.blendingMode = BlendingMode.SCREEN; } catch (e4) {}
            setInOut(l, t0, t1); made.push(l); return made;
        }
        if (kind === "smoke") {
            l = solid(comp, "FX" + idx + "_SMOKE", [0, 0, 0]);
            var fn = addFx(l, "ADBE Fractal Noise");
            try { liveOf(fn).property("Contrast").setValue(160); liveOf(fn).property("Brightness").setValue(-20); liveOf(fn).property("Scale").setValue(420); } catch (eF) {}
            try { liveOf(fn).property("Evolution").expression = "time*60;"; } catch (eV) {}
            var tint = addFx(l, "ADBE Tint"); fxSet(tint, 2, hex(fx.color, [0.55, 0.55, 0.55]), "smoke colour");
            try { l.blendingMode = fx.dark ? BlendingMode.MULTIPLY : BlendingMode.SCREEN; } catch (eB2) {}
            P_op(l).setValue(num(fx.opacity, 45));
            setKeys(P_op(l), [t0, t0 + 0.3], [0, num(fx.opacity, 45)], "linear");
            setInOut(l, t0, t1); made.push(l); return made;
        }
        if (kind === "tint") {
            l = solid(comp, "FX" + idx + "_TINT", hex(fx.color, [0.2, 0.7, 0.2]));
            try { l.blendingMode = fx.blend === "multiply" ? BlendingMode.MULTIPLY : (fx.blend === "color" ? BlendingMode.COLOR : BlendingMode.OVERLAY); } catch (eT) {}
            var op = num(fx.opacity, 55), fi = num(fx.fade, 0.25);
            setKeys(P_op(l), [t0, t0 + fi, t1 - fi, t1], [0, op, op, 0], "linear");
            setInOut(l, t0, t1); made.push(l); return made;
        }
        if (kind === "glitch") {
            l = comp.layers.addSolid([0, 0, 0], "FX" + idx + "_GLITCH", S.width, S.height, 1, S.duration);
            l.adjustmentLayer = true;
            var mo = addFx(l, "ADBE Mosaic"), hb = fxProp(mo, 1), vb = fxProp(mo, 2);
            var tm = [], hv = [], vv = [];
            for (i = 0; i <= 6; i += 1) { tm.push(t0 + i * 0.04); hv.push(i % 2 ? rr(8, 22) : rr(28, 60)); vv.push(i % 2 ? rr(14, 40) : rr(40, 90)); }
            tm.push(t0 + 0.3); hv.push(1000); vv.push(1000);
            if (hb) { holdKeys(hb, tm, hv); } if (vb) { holdKeys(vb, tm, vv); }
            setInOut(l, t0, t0 + 0.28); made.push(l); return made;
        }
        if (kind === "flash") {
            l = solid(comp, "FX" + idx + "_FLASH", hex(fx.color, [1, 0.95, 0.85]));
            try { l.blendingMode = BlendingMode.ADD; } catch (eA) {}
            setKeys(P_op(l), [t0, t0 + 0.04, t0 + 0.3], [0, num(fx.opacity, 85), 0], "linear");
            setInOut(l, t0, t0 + 0.32); made.push(l); return made;
        }
        if (kind === "video" || kind === "fire" || kind === "overlay") {
            var iv = importFile(absPath(B.root, fx.file), B.F.foot);
            if (!iv) { return made; }
            l = comp.layers.add(iv); l.name = "FX" + idx + "_OVERLAY";
            if (!fx.screen) { parentTo(l, cam); }
            var cs = fx.w ? fx.w / iv.width * 100 : coverScale(iv, S.width, S.height);
            P_scale(l).setValue([cs, cs]); P_pos(l).setValue([num(fx.x, S.width / 2), num(fx.y, S.height / 2)]);
            try { l.blendingMode = fx.blend === "normal" ? BlendingMode.NORMAL : (fx.blend === "add" ? BlendingMode.ADD : BlendingMode.SCREEN); } catch (eO) {}
            if (iv.duration) { l.startTime = t0 - num(fx.start, 0); try { l.audioEnabled = false; } catch (eAu) {} }
            if (num(fx.opacity, 100) < 100) { P_op(l).setValue(fx.opacity); }
            setInOut(l, t0, t1); made.push(l); return made;
        }
        warn("unknown fx kind " + kind);
        return made;
    }

    function stateLayers(comp, sh) {
        var st = sh.state || [], i, l, s;
        for (i = 0; i < st.length; i += 1) {
            s = st[i];
            l = comp.layers.addSolid([0, 0, 0], "STATE_" + i + "_" + s.kind, B.S.width, B.S.height, 1, B.S.duration);
            l.adjustmentLayer = true;
            var t0 = num(s.t, sh.t), t1 = num(s.end, sh.end + 1), fd = num(s.fade, 0.25);
            if (s.kind === "bw" || s.kind === "gray") {
                var t = addFx(l, "ADBE Tint", "BW"); var a = fxProp(t, 3);
                if (a) { setKeys(a, [t0, t0 + fd], [0, 100], "linear"); }
                var bc = addFx(l, "ADBE Brightness & Contrast 2"); fxSet(bc, 1, num(s.bright, -10), "brightness"); fxSet(bc, 2, 12, "contrast");
            } else if (s.kind === "dark") {
                var bc2 = addFx(l, "ADBE Brightness & Contrast 2"); var b2 = fxProp(bc2, 1); if (b2) { setKeys(b2, [t0, t0 + fd], [0, num(s.bright, -45)], "linear"); }
            } else {
                var tn = addFx(l, "ADBE Tint", "TINT"); fxSet(tn, 1, [0, 0, 0], "black"); fxSet(tn, 2, hex(s.color, [1, 0.3, 0.3]), "white");
                var am = fxProp(tn, 3); if (am) { setKeys(am, [t0, t0 + fd], [0, num(s.amount, 60)], "linear"); }
            }
            setInOut(l, t0, Math.min(t1, B.S.duration));
        }
    }

    function buildShot(sh, idx, charComps) {
        var S = B.S;
        var comp = addComp(sh.id || ("S" + (idx + 1)), S.width, S.height, S.duration, B.F.shots);
        var cam = camLayer(comp, sh);
        var bg = bgLayer(comp, sh, cam);
        var props = sh.props || [], i, back = [], front = [];
        for (i = 0; i < props.length; i += 1) { if (props[i].z === "back") { back.push(i); } else { front.push(i); } }
        for (i = 0; i < back.length; i += 1) { try { propLayer(comp, sh, props[back[i]], back[i], cam); } catch (e) { fail("prop " + sh.id + "/" + back[i], e); } }
        var crs = sh.creatures || [];
        for (i = 0; i < crs.length; i += 1) { if ((crs[i].z || "back") === "back") { try { creatureLayers(comp, sh, crs[i], i, cam); } catch (eCr) { fail("creature " + sh.id + "/" + i, eCr); } } }
        var acts = (sh.actors || []).slice(0);
        for (i = 0; i < acts.length; i += 1) { acts[i]._i = i; }
        stableSort(acts, function (a, b) { var za = num(a.z, 0), zb = num(b.z, 0); if (za !== zb) { return za - zb; } return num(a.y, 0) - num(b.y, 0); });
        for (i = 0; i < acts.length; i += 1) {
            try {
                if (!charComps[acts[i].cast]) { warn("no character comp for " + acts[i].cast); continue; }
                actorLayers(comp, sh, acts[i], acts[i]._i, cam, charComps[acts[i].cast]);
            } catch (e2) { fail("actor " + sh.id + "/" + acts[i].cast, e2); }
        }
        for (i = 0; i < crs.length; i += 1) { if ((crs[i].z || "back") !== "back") { try { creatureLayers(comp, sh, crs[i], i, cam); } catch (eCr2) { fail("creature " + sh.id + "/" + i, eCr2); } } }
        for (i = 0; i < front.length; i += 1) { try { propLayer(comp, sh, props[front[i]], front[i], cam); } catch (e3) { fail("prop " + sh.id + "/" + front[i], e3); } }
        var icons = sh.icons || [];
        for (i = 0; i < icons.length; i += 1) { try { iconLayer(comp, sh, icons[i], i, cam); } catch (e4) { fail("icon " + sh.id + "/" + i, e4); } }
        var fx = sh.fx || [];
        for (i = 0; i < fx.length; i += 1) { try { fxLayers(comp, sh, fx[i], i, cam); } catch (e5) { fail("fx " + sh.id + "/" + i, e5); } }
        try { stateLayers(comp, sh); } catch (e6) { fail("states " + sh.id, e6); }
        cam.moveToBeginning();
        return comp;
    }

    /* ================================================================= MAIN: shots, transitions, look, captions, audio */
    function transitions(main, shotLayers, shots) {
        var S = B.S, i, sh, tr, b, l, prev, f = 1 / S.fps;
        for (i = 1; i < shots.length; i += 1) {
            sh = shots[i]; tr = sh.transition || "cut"; b = sh.t; prev = shotLayers[i - 1];
            if (tr === "cut") { continue; }
            try {
                if (tr === "flash") {
                    l = solid(main, "TR_FLASH_" + i, [1, 1, 1]);
                    setKeys(P_op(l), [b - 2 * f, b, b + 5 * f], [0, 100, 0], "linear");
                    setInOut(l, b - 3 * f, b + 6 * f);
                } else if (tr === "light_leak") {
                    l = shapeLayer(main, "TR_LEAK_" + i);
                    var g = groupContents(addGroup(rootContents(l), "L"));
                    addPathTo(g, ellipseShape(0, 0, S.width * 1.4, S.height * 0.9)); addFill(g, [1, 0.62, 0.12], 100);
                    var g2 = groupContents(addGroup(rootContents(l), "L2"));
                    addPathTo(g2, ellipseShape(S.width * 0.25, -S.height * 0.1, S.width * 0.8, S.height * 0.5)); addFill(g2, [1, 0.95, 0.75], 100);
                    var fb = addFx(l, "ADBE Gaussian Blur 2"); fxSet(fb, 1, 180, "blur");
                    try { l.blendingMode = BlendingMode.ADD; } catch (e1) {}
                    setKeys(P_pos(l), [b - 0.18, b + 0.32], [[-S.width * 0.6, S.height * 0.2], [S.width * 1.6, S.height * 0.7]], "linear");
                    setKeys(P_op(l), [b - 0.18, b - 0.02, b + 0.12, b + 0.32], [0, 100, 90, 0], "linear");
                    setInOut(l, b - 0.2, b + 0.34);
                } else if (tr === "red_wipe") {
                    l = shapeLayer(main, "TR_REDWIPE_" + i);
                    var g3 = groupContents(addGroup(rootContents(l), "R"));
                    var rc = liveOf(g3).addProperty("ADBE Vector Shape - Rect"); rc.property("ADBE Vector Rect Size").setValue([S.width * 0.35, S.height * 1.4]);
                    addFill(g3, [0.95, 0.18, 0.16], 100);
                    var fb2 = addFx(l, "ADBE Gaussian Blur 2"); fxSet(fb2, 1, 40, "blur");
                    try { l.blendingMode = BlendingMode.SCREEN; } catch (e2) {}
                    setKeys(P_pos(l), [b - 0.12, b + 0.36], [[S.width * 1.3, S.height / 2], [-S.width * 0.3, S.height / 2]], "linear");
                    P_op(l).setValue(80);
                    setInOut(l, b - 0.14, b + 0.38);
                } else if (tr === "glitch") {
                    prev.outPoint = b + 0.2;
                    var bd = addFx(prev, "ADBE Block Dissolve"), cmp = fxProp(bd, 1);
                    fxSet(bd, 2, 60, "block w"); fxSet(bd, 3, 30, "block h");
                    if (cmp) { setKeys(cmp, [b - 0.02, b + 0.2], [0, 100], "linear"); }
                } else if (tr === "bw_fade") {
                    l = main.layers.addSolid([0, 0, 0], "TR_BW_" + i, S.width, S.height, 1, S.duration);
                    l.adjustmentLayer = true;
                    var tt = addFx(l, "ADBE Tint"), am = fxProp(tt, 3);
                    if (am) { setKeys(am, [b - 0.3, b - 0.02], [0, 100], "linear"); }
                    setInOut(l, b - 0.3, b);
                } else if (tr === "whip") {
                    prev.outPoint = b + 0.12;
                    setKeys(P_pos(prev), [b - 0.12, b + 0.12], [[S.width / 2, S.height / 2], [-S.width * 0.6, S.height / 2]], "in");
                    var db = addFx(prev, "ADBE Motion Blur"); fxSet(db, 1, 90, "direction"); var ln = fxProp(db, 2); if (ln) { setKeys(ln, [b - 0.12, b, b + 0.12], [0, 160, 160], "linear"); }
                    var cur = shotLayers[i];
                    cur.inPoint = b - 0.12;
                    setKeys(P_pos(cur), [b - 0.12, b + 0.14], [[S.width * 1.6, S.height / 2], [S.width / 2, S.height / 2]], "out");
                    var db2 = addFx(cur, "ADBE Motion Blur"); fxSet(db2, 1, 90, "direction"); var ln2 = fxProp(db2, 2); if (ln2) { setKeys(ln2, [b - 0.12, b + 0.02, b + 0.14], [160, 120, 0], "linear"); }
                } else if (tr === "zoom_blur") {
                    l = main.layers.addSolid([0, 0, 0], "TR_ZOOM_" + i, S.width, S.height, 1, S.duration);
                    l.adjustmentLayer = true;
                    var rb = addFx(l, "ADBE Radial Blur"); fxSet(rb, 3, 2, "type zoom");
                    var amt = fxProp(rb, 1); if (amt) { setKeys(amt, [b - 0.12, b, b + 0.14], [0, 55, 0], "linear"); }
                    setInOut(l, b - 0.12, b + 0.15);
                } else { warn("unknown transition " + tr); }
            } catch (e) { fail("transition " + tr + " into " + sh.id, e); }
        }
    }
    function lookLayers(main) {
        var S = B.S, lk = B.spec.look || {}, l;
        var vg = num(lk.vignette, DATA.style.look.vignette);
        if (vg > 0) {
            l = solid(main, "LOOK_VIGNETTE", [0, 0, 0]);
            var m = l.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
            m.property("ADBE Mask Shape").setValue(ellipseShape(S.width / 2, S.height / 2, S.width * 1.15, S.height * 1.05));
            m.inverted = true;
            m.property("ADBE Mask Feather").setValue([S.width * 0.45, S.width * 0.45]);
            P_op(l).setValue(vg * 100);
        }
        var gr = num(lk.grain, DATA.style.look.grain);
        if (gr > 0) {
            l = main.layers.addSolid([0, 0, 0], "LOOK_GRAIN", S.width, S.height, 1, S.duration);
            l.adjustmentLayer = true;
            var nz = addFx(l, "ADBE Noise"); fxSet(nz, 1, gr * 100, "noise amount"); fxSet(nz, 2, 0, "colour noise off");
        }
        if ((lk.end || DATA.style.look.end) === "fade_black") {
            l = solid(main, "END_FADE", [0, 0, 0]);
            setKeys(P_op(l), [S.duration - 0.7, S.duration - 0.05], [0, 100], "linear");
            setInOut(l, S.duration - 0.7, S.duration);
        }
    }
    function captionLayer(main) {
        var S = B.S, cs = DATA.style.captions, caps = B.spec.captions || [], i, c;
        var sty = B.spec.caption_style || {};
        var l = main.layers.addText(" ");
        l.name = "CAPTIONS";
        var tdp = l.property("ADBE Text Properties").property("ADBE Text Document"), base = tdp.value;
        try { base.font = B.font; } catch (eF) { warn("caption font " + B.font + " not accepted: " + eF.toString()); }
        base.fontSize = num(sty.size, cs.size);
        base.applyFill = true; base.fillColor = hex(cs.yellow);
        base.applyStroke = true; base.strokeColor = hex(cs.stroke); base.strokeWidth = num(sty.stroke, cs.stroke_width); base.strokeOverFill = false;
        base.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { base.tracking = num(sty.tracking, cs.tracking); } catch (eT) {}
        tdp.setValue(base);
        var times = [], docs = [];
        function doc(text, colName, scale) {
            var d = tdp.value;
            d.text = text;
            d.fillColor = hex(colName === "red" ? cs.red : (colName === "white" ? "#FFFFFF" : (colName && colName.charAt(0) === "#" ? colName : cs.yellow)));
            d.fontSize = num(sty.size, cs.size) * num(scale, 1);
            return d;
        }
        times.push(0); docs.push(doc(" ", "yellow", 1));
        for (i = 0; i < caps.length; i += 1) {
            c = caps[i];
            var t = Math.max(0, c.t);
            if (times.length && Math.abs(t - times[times.length - 1]) < 0.001) { docs[docs.length - 1] = doc(String(c.text), c.color, c.scale); }
            else { times.push(t); docs.push(doc(String(c.text), c.color, c.scale)); }
            var nextT = (i + 1 < caps.length) ? caps[i + 1].t : null;
            if (nextT === null || nextT - num(c.end, t + 0.4) > num(cs.gap_blank, 0.35)) {
                times.push(num(c.end, t + 0.4) + 0.08); docs.push(doc(" ", "yellow", 1));
            }
        }
        try { tdp.setValuesAtTimes(times, docs); } catch (e) {
            for (i = 0; i < times.length; i += 1) { try { tdp.setValueAtTime(times[i], docs[i]); } catch (e2) { fail("caption key " + i, e2); break; } }
        }
        P_anchor(l).expression = "var r=sourceRectAtTime(time,false);[r.left+r.width/2,r.top+r.height/2];";
        P_pos(l).setValue([S.width / 2, S.height * num(sty.y, cs.y)]);
        P_scale(l).expression = "var st=text.sourceText;var t0=0;if(st.numKeys>0){var k=st.nearestKey(time).index;if(st.key(k).time>time){k=k-1;}if(k>=1){t0=st.key(k).time;}}" +
            "var d=Math.max(0,time-t0);var s=100+" + cs.pop + "*Math.exp(-d*" + cs.pop_decay + ")*Math.cos(d*" + cs.pop_freq + ");[s,s];";
        var ds = addFx(l, "ADBE Drop Shadow", "Extrude");
        fxSet(ds, 1, hex(cs.shadow), "shadow colour"); fxSet(ds, 2, 255, "opacity"); fxSet(ds, 3, 145, "direction"); fxSet(ds, 4, cs.shadow_distance, "distance"); fxSet(ds, 5, 0, "softness");
        var gl = addFx(l, "ADBE Glo2", "Halo");
        fxSet(gl, 2, cs.glow_threshold, "threshold"); fxSet(gl, 3, cs.glow_radius, "radius"); fxSet(gl, 4, cs.glow_intensity, "intensity");
        fxSet(gl, 5, 1, "composite original");   /* 1 keeps the letters' own colour over the halo (the default 2 turns red into pink) */
        return l;
    }
    function audioLayers(main) {
        var A = B.spec.audio || {}, it, l, i;
        if (A.voice) { it = importFile(absPath(B.root, A.voice), B.F.audio); if (it) { l = main.layers.add(it); l.name = "VO"; l.startTime = num(A.voice_offset, 0); } }
        if (A.music) {
            it = importFile(absPath(B.root, A.music), B.F.audio);
            if (it) { l = main.layers.add(it); l.name = "MUSIC"; try { l.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([num(A.music_db, -18), num(A.music_db, -18)]); } catch (e) {} }
        }
        var sfx = A.sfx || [];
        for (i = 0; i < sfx.length; i += 1) {
            it = importFile(absPath(B.root, sfx[i].file), B.F.audio);
            if (!it) { continue; }
            l = main.layers.add(it); l.name = "SFX_" + i; l.startTime = num(sfx[i].t, 0);
            try { l.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([num(sfx[i].gain_db, -6), num(sfx[i].gain_db, -6)]); } catch (e2) {}
        }
    }

    /* ================================================================= entry points */
    function begin(projectDir, logName) {
        B = { root: slash(projectDir), F: null, S: null, spec: null, font: null };
        FOOT = {}; FONT_CACHE = {}; SEED = 12345;
        LOG.file = B.root + "/ae/" + (logName || "build_log.txt"); LOG.errors = 0; LOG.warnings = 0; LOG.lines = [];
        try { writeText(LOG.file, ""); } catch (e) {}
        log("2D Stick Animator engine " + RA.VERSION + " on After Effects " + app.version);
    }
    function kitDir() {
        if (typeof RA_KIT !== "undefined" && RA_KIT) { return slash(RA_KIT); }
        return slash((new File($.fileName)).parent.parent.fsName);
    }
    RA.build = function (projectDir, opts) {
        opts = opts || {};
        begin(projectDir, "build_log.txt");
        var t0 = (new Date()).getTime();
        try {
            loadData(kitDir());
            var specRel = opts.spec || ((new File(B.root + "/plan/spec_compiled.json")).exists ? "plan/spec_compiled.json" : "plan/spec.json");
            log("spec: " + specRel);
            var spec = RA.parseJSON(readText(B.root + "/" + specRel));
            B.spec = spec;
            var M = spec.meta || {};
            B.S = { fps: num(M.fps, 30), width: num(M.width, 1080), height: num(M.height, 1920), duration: num(M.duration, 60) };
            if (!spec.shots || !spec.shots.length) { throw new Error("spec has no shots"); }
            B.F = newProject(B.S);
            var cs = DATA.style.captions;
            B.font = pickFont((spec.caption_style && spec.caption_style.fonts) || cs.fonts);
            log("caption font: " + B.font + (fontOK(B.font) === true ? "" : " (could not confirm it is installed)"));
            app.beginUndoGroup("2D Stick Animator build");
            /* characters */
            var TL = collectTimelines(spec), charComps = {}, id;
            for (id in spec.cast) {
                if (!spec.cast.hasOwnProperty(id)) { continue; }
                try {
                    var tl = TL[id] || emptyTimeline();
                    charComps[id] = buildCharacter(id, spec.cast[id], tl);
                    applyTimeline(charComps[id], tl);
                    log("character " + id + " built (" + tl.pose.length + " pose keys)");
                } catch (eC) { fail("character " + id, eC); }
            }
            /* shots */
            var main = addComp("MAIN", B.S.width, B.S.height, B.S.duration, B.F.main);
            var shotComps = [], i;
            for (i = 0; i < spec.shots.length; i += 1) {
                try { shotComps.push(buildShot(spec.shots[i], i, charComps)); }
                catch (eS) { fail("shot " + spec.shots[i].id, eS); shotComps.push(null); }
            }
            /* MAIN stacking: earlier shots above later ones (so outgoing shots can dissolve over incoming) */
            var shotLayers = [];
            for (i = shotComps.length - 1; i >= 0; i -= 1) {
                if (!shotComps[i]) { shotLayers[i] = null; continue; }
                var sl = main.layers.add(shotComps[i]);
                sl.name = spec.shots[i].id || ("S" + (i + 1));
                setInOut(sl, spec.shots[i].t, spec.shots[i].end);
                shotLayers[i] = sl;
            }
            transitions(main, shotLayers, spec.shots);
            lookLayers(main);
            if (spec.captions && spec.captions.length) { try { captionLayer(main); } catch (eCap) { fail("captions", eCap); } }
            try { audioLayers(main); } catch (eAu) { fail("audio", eAu); }
            app.endUndoGroup();
            main.openInViewer();
            var aep = new File(B.root + "/ae/" + (M.slug || "project") + ".aep");
            if (!aep.parent.exists) { aep.parent.create(); }
            app.project.save(aep);
            log("saved " + aep.fsName);
        } catch (e) { fail("build", e); try { app.endUndoGroup(); } catch (e9) {} }
        var secs = Math.round(((new Date()).getTime() - t0) / 100) / 10;
        log("DONE errors=" + LOG.errors + " warnings=" + LOG.warnings + " seconds=" + secs);
        return LOG.errors;
    };
    function openProject(projectDir, slugGuess) {
        var f = null, fl = new Folder(projectDir + "/ae"), list, i;
        if (app.project && app.project.file && slash(app.project.file.fsName).indexOf(slash(projectDir)) === 0) { return true; }
        list = fl.exists ? fl.getFiles("*.aep") : [];
        for (i = 0; i < list.length; i += 1) { if (!f || list[i].modified > f.modified) { f = list[i]; } }
        if (!f) { warn("no .aep in " + projectDir + "/ae"); return false; }
        app.open(f);
        return true;
    }
    function mainComp() {
        var i;
        for (i = 1; i <= app.project.numItems; i += 1) { if (app.project.item(i) instanceof CompItem && app.project.item(i).name === "MAIN") { return app.project.item(i); } }
        return null;
    }
    RA.stills = function (projectDir, times, opts) {
        opts = opts || {};
        begin(projectDir, "stills_log.txt");
        try {
            openProject(B.root);
            var m = mainComp(), i, made = 0;
            if (!m) { throw new Error("MAIN comp not found"); }
            var dir = new Folder(B.root + "/ae/stills"); if (!dir.exists) { dir.create(); }
            if (!times || !times.length) { times = []; for (i = 0.5; i < m.duration; i += num(opts.every, 2)) { times.push(i); } }
            for (i = 0; i < times.length; i += 1) {
                var f = new File(dir.fsName + "/still_" + ("00000" + Math.round(times[i] * 1000)).slice(-6) + ".png");
                if (f.exists) { try { f.remove(); } catch (eR) {} }   /* so the caller can wait for the fresh file (saveFrameToPng is asynchronous in AE 2024+) */
                try { m.saveFrameToPng(Math.min(times[i], m.duration - 1 / m.frameRate), f); made += 1; } catch (e) { fail("still " + times[i], e); }
            }
            log("stills requested=" + made);
        } catch (e2) { fail("stills", e2); }
        log("DONE errors=" + LOG.errors + " warnings=" + LOG.warnings);
        return LOG.errors;
    };
    RA.render = function (projectDir, opts) {
        opts = opts || {};
        begin(projectDir, "render_log.txt");
        try {
            openProject(B.root);
            var m = mainComp();
            if (!m) { throw new Error("MAIN comp not found"); }
            var rq = app.project.renderQueue, i;
            for (i = rq.numItems; i >= 1; i -= 1) { try { rq.item(i).remove(); } catch (e0) {} }
            var item = rq.items.add(m);
            try { item.applyTemplate("Best Settings"); } catch (e1) {}
            var om = item.outputModule(1), names = om.templates, pick = null, j, ext = ".mov";
            var prefs = opts.templates || ["H.264 - Match Render Settings - 40 Mbps", "H.264 - Match Render Settings - 15 Mbps", "H.264", "Apple ProRes 422 HQ", "High Quality", "Lossless"];
            for (i = 0; i < prefs.length && !pick; i += 1) { for (j = 0; j < names.length; j += 1) { if (names[j].indexOf(prefs[i]) === 0 && names[j].indexOf("_HIDDEN") < 0) { pick = names[j]; break; } } }
            if (pick) { om.applyTemplate(pick); log("output template: " + pick); } else { warn("no preferred output template; using default"); }
            if (pick && pick.indexOf("H.264") === 0) { ext = ".mp4"; } else if (pick && pick.indexOf("Lossless") === 0) { ext = ".avi"; }
            var out = new File(B.root + "/exports/ae_render" + ext);
            if (!out.parent.exists) { out.parent.create(); }
            om.file = out;
            log("rendering to " + out.fsName);
            app.project.save();
            rq.render();
            log("render finished: " + out.fsName);
            writeText(B.root + "/exports/ae_render.done", out.fsName);
        } catch (e) { fail("render", e); }
        log("DONE errors=" + LOG.errors + " warnings=" + LOG.warnings);
        return LOG.errors;
    };
    RA.fonts = function (projectDir, names) {
        begin(projectDir, "fonts_log.txt");
        var i;
        for (i = 0; i < names.length; i += 1) { log("font " + names[i] + ": " + fontOK(names[i])); }
        log("DONE errors=0 warnings=0");
    };
    RA.run = function (job) {
        var root = (typeof RA_ROOT !== "undefined" && RA_ROOT) ? slash(RA_ROOT) : slash((new Folder(kitDir())).parent.fsName);
        var pdir = job.project ? (/^[A-Za-z]:\//.test(slash(job.project)) || slash(job.project).charAt(0) === "/" ? slash(job.project) : root + "/" + job.project) : root;
        if (job.kind !== "fonts" && !(new Folder(pdir)).exists) { throw new Error("project folder not found: " + pdir + " (give it relative to the workspace, e.g. projects/my-video)"); }
        if (job.kind === "build") {
            var rb = RA.build(pdir, job);
            if (LOG.errors) { throw new Error("build finished with " + LOG.errors + " error(s) - see " + LOG.file); }
            return rb;
        }
        if (job.kind === "stills") { return RA.stills(pdir, job.times, job); }
        if (job.kind === "render") { return RA.render(pdir, job); }
        if (job.kind === "fonts") { return RA.fonts(pdir, job.names || []); }
        throw new Error("unknown job kind " + job.kind);
    };
    RA._test = { poseVals: poseVals, limbPathExpr: limbPathExpr, collectTimelines: collectTimelines, DATA: DATA, setB: function (b) { B = b; } };
    return RA;
}());
