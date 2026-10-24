/*  2D Stick Animator - After Effects bridge.
    Run it once per After Effects session:  File > Scripts > Run Script File...  ->  <workspace>/_kit/ae/ra_bridge.jsx
    It watches <workspace>/_ae_jobs/ for *.jsx job files (written by make_job.py) and runs them one at a time,
    writing <job>.result.json next to them and moving the job to _ae_jobs/done/. Nothing needs clicking afterwards.
    A heartbeat (_ae_jobs/bridge_heartbeat.json) is refreshed every ~1.2 s while After Effects is idle.
    Needs: Edit > Preferences > Scripting & Expressions > "Allow Scripts to Write Files and Access Network".
    ES3 + ASCII only.
*/
(function () {
    var me = new File($.fileName);
    var kit = me.parent.parent, root = kit.parent;
    $.global.RA_ROOT = root.fsName.replace(/\\/g, "/");
    $.global.RA_KIT = kit.fsName.replace(/\\/g, "/");
    var jobs = new Folder(RA_ROOT + "/_ae_jobs");
    if (!jobs.exists) { jobs.create(); }
    var done = new Folder(jobs.fsName + "/done");
    if (!done.exists) { done.create(); }

    function q(s) { return "\"" + String(s).replace(/\\/g, "\\\\").replace(/"/g, "\\\"").replace(/\r?\n/g, "\\n") + "\""; }
    function writeFile(path, s) {
        var f = new File(path);
        f.encoding = "UTF-8";
        if (!f.open("w")) { throw new Error("cannot write " + path); }
        f.write(s); f.close();
    }
    try { writeFile(jobs.fsName + "/bridge_heartbeat.json", "{\"starting\":true}"); }
    catch (e) {
        alert("2D Stick Animator bridge: After Effects is not allowed to write files.\n\n" +
              "Turn on Edit > Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network', then run ra_bridge.jsx again.");
        return;
    }
    if ($.global.RA_BRIDGE) { try { $.global.RA_BRIDGE.stopped = true; app.cancelTask($.global.RA_BRIDGE.task); } catch (e2) {} }
    var B = { busy: false, task: null, runs: 0, started: (new Date()).getTime(), version: "1.1.0", stopped: false };
    $.global.RA_BRIDGE = B;
    B.heartbeat = function (state) {
        var proj = "";
        try { proj = app.project && app.project.file ? app.project.file.fsName : ""; } catch (e) {}
        writeFile(jobs.fsName + "/bridge_heartbeat.json",
            "{\"time\":" + (new Date()).getTime() + ",\"state\":" + q(state) + ",\"runs\":" + B.runs + ",\"ae\":" + q(app.version) +
            ",\"project\":" + q(proj.replace(/\\/g, "/")) + ",\"root\":" + q(RA_ROOT) + ",\"bridge\":" + q(B.version) + "}");
    };
    B.poll = function () {
        if (B.busy) { return; }
        B.busy = true;
        try {
            B.heartbeat("idle");
            var list = jobs.getFiles("*.jsx"), i, f = null;
            list.sort(function (a, b) { return a.name < b.name ? -1 : (a.name > b.name ? 1 : 0); });
            for (i = 0; i < list.length; i += 1) { if (list[i] instanceof File) { f = list[i]; break; } }
            if (f) {
                var base = decodeURI(f.name).replace(/\.jsx$/i, "");
                var runPath = jobs.fsName + "/" + base + ".running";
                var old = new File(runPath); if (old.exists) { old.remove(); }
                f.rename(base + ".running");
                B.heartbeat("running " + base);
                var res = "{\"job\":" + q(base) + ",\"started\":" + (new Date()).getTime();
                var ok = true, err = "", line = 0;
                try { app.beginSuppressDialogs(); } catch (e0) {}
                try { $.evalFile(new File(runPath)); }
                catch (e) { ok = false; err = String(e); line = e.line || 0; }
                try { app.endSuppressDialogs(false); } catch (e1) {}
                B.runs += 1;
                res += ",\"finished\":" + (new Date()).getTime() + ",\"ok\":" + (ok ? "true" : "false") + ",\"error\":" + q(err) + ",\"line\":" + line + "}";
                writeFile(jobs.fsName + "/" + base + ".result.json", res);
                var rf = new File(runPath);
                if (rf.exists) { rf.copy(done.fsName + "/" + base + ".jsx"); rf.remove(); }
                B.heartbeat("idle");
            }
        } catch (eAll) {
            try { writeFile(jobs.fsName + "/bridge_error.txt", String(eAll) + " line " + (eAll.line || 0)); } catch (e3) {}
        }
        B.busy = false;
    };
    /* Self-rescheduling one-shot tasks instead of one repeating task: After Effects drops repeating scheduled
       tasks during a render-queue render, which silently stopped the bridge after the first render job. A
       slower repeating watchdog re-arms the chain if it ever breaks. */
    B.last = (new Date()).getTime();
    B.arm = function () {
        try { B.task = app.scheduleTask("if($.global.RA_BRIDGE){RA_BRIDGE.tick();}", 1200, false); } catch (e) {}
    };
    B.tick = function () {
        B.last = (new Date()).getTime();
        try { B.poll(); } catch (e) {}
        if (!B.stopped) { B.arm(); }
    };
    B.watch = function () {
        if (!B.stopped && (new Date()).getTime() - B.last > 6000 && !B.busy) { B.arm(); }
    };
    B.stop = function () {
        B.stopped = true;
        try { app.cancelTask(B.task); } catch (e) {}
        try { app.cancelTask(B.watchTask); } catch (e2) {}
        B.task = null; B.heartbeat("stopped");
    };
    if ($.global.RA_BRIDGE_WATCH) { try { app.cancelTask($.global.RA_BRIDGE_WATCH); } catch (e5) {} }
    B.arm();
    B.watchTask = app.scheduleTask("if($.global.RA_BRIDGE){RA_BRIDGE.watch();}", 5000, true);
    $.global.RA_BRIDGE_WATCH = B.watchTask;
    B.heartbeat("idle");
    try { clearOutput(); writeLn("2D Stick Animator bridge is running."); writeLn("Jobs: " + jobs.fsName); } catch (e4) {}
}());
