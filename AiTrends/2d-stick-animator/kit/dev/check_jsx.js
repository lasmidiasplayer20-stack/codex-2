// Usage: node check_jsx.js file.jsx [...]   (needs: npm i acorn)
// ES3 syntax + ASCII check for ExtendScript files
const fs=require('fs'), path=require('path');
let acorn; try { acorn=require('acorn'); } catch(e) { try { acorn=require(path.join(process.cwd(),'node_modules','acorn')); } catch(e2) { console.log("needs acorn: run 'npm i acorn' in this folder or the workspace"); process.exit(2); } }
let bad=0;
for (const f of process.argv.slice(2)) {
  const src=fs.readFileSync(f,'utf8');
  const nonAscii=[...src].findIndex(c=>c.charCodeAt(0)>127);
  if (nonAscii>=0){console.log(f+': non-ASCII char at offset '+nonAscii); bad++;}
  try { acorn.parse(src,{ecmaVersion:3,allowReserved:false}); console.log(f+': ES3 OK'); }
  catch(e){ console.log(f+': '+e.message); bad++; }
  // ExtendScript mis-evaluates unparenthesised chained ternaries (a ? b : c ? d : e): require parentheses.
  // Scanner: per bracket depth, a '?' that appears after the ':' of an open ternary at the same depth is a chain.
  src.split(/\n/).forEach((line, i) => {
    let code = line.replace(/\/\*.*?\*\//g, '').replace(/\/\/.*$/, '');
    code = code.replace(/"(?:[^"\\]|\\.)*"/g, '""').replace(/'(?:[^'\\]|\\.)*'/g, "''").replace(/\/(?:[^\/\\\n]|\\.)+\/[gimy]*/g, '//');
    let depth = 0, st = [], hit = false;
    for (const ch of code) {
      if ('([{'.includes(ch)) { depth++; continue; }
      if (')]}'.includes(ch)) { depth--; while (st.length && st[st.length - 1].d > depth) st.pop(); continue; }
      if (ch === ',' || ch === ';') { while (st.length && st[st.length - 1].d >= depth) st.pop(); continue; }
      if (ch === '?') {
        const top = st.length ? st[st.length - 1] : null;
        if (top && top.d === depth && top.colon) { hit = true; }
        st.push({ d: depth, colon: false });
      } else if (ch === ':') {
        for (let k = st.length - 1; k >= 0; k--) { if (st[k].d === depth && !st[k].colon) { st[k].colon = true; break; } }
      }
    }
    if (hit) { console.log(f + ':' + (i + 1) + ': chained ternary without parentheses (ExtendScript mis-evaluates it): ' + line.trim().slice(0, 120)); bad++; }
  });
  // forbidden ES5+ array helpers that ExtendScript lacks
  const m=src.match(/\.(indexOf|forEach|map|filter|reduce|some|every)\(/g)||[];
  const arrHits=[];
  src.split('\n').forEach((ln,i)=>{ if(/\b(forEach|\.map\(|\.filter\(|\.reduce\(|\.some\(|\.every\()/.test(ln) && !/^\s*\/\//.test(ln)) arrHits.push(i+1); });
  if(arrHits.length) console.log(f+': ES5 array helpers on lines '+arrHits.join(','));
}
process.exit(bad?1:0);
