#!/usr/bin/env node
// Assemble src/index.html + data/**/*.json → dist/DebitCredit.html (fichier unique, hors ligne). Usage : node build.js [--lenient]
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const ROOT = __dirname; const lenient = process.argv.includes("--lenient");
const plan = JSON.parse(fs.readFileSync(path.join(ROOT, "data/plan.json"), "utf8"));
const order = Object.fromEntries(plan.ues.map((u, i) => [u.code, i]));
const chapitres = []; const skipped = [];
for (const p of plan.chapitres) {
  const f = path.join(ROOT, "data", p.ue.toLowerCase(), p.id + ".json");
  if (!fs.existsSync(f)) { skipped.push(p.id + " (absent)"); continue; }
  let ok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), f], { stdio: "pipe" }); } catch (e) { ok = false; }
  if (!ok && !lenient) { skipped.push(p.id + " (invalide)"); continue; }
  const ch = JSON.parse(fs.readFileSync(f, "utf8"));
  ch.exercices.forEach((e, i) => { e.id = `${ch.id}-${i}`; e.chap = ch.id; });
  chapitres.push(ch);
}
chapitres.sort((a, b) => order[a.ue] - order[b.ue] || a.ordre - b.ordre);
const pcg = [];
for (const f of fs.readdirSync(path.join(ROOT, "data/pcg")).filter(x => x.endsWith(".json")).sort()) {
  const full = path.join(ROOT, "data/pcg", f);
  let ok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), full], { stdio: "pipe" }); } catch (e) { ok = false; }
  if (!ok && !lenient) { skipped.push("pcg/" + f + " (invalide)"); continue; }
  pcg.push(...JSON.parse(fs.readFileSync(full, "utf8")).comptes);
}
pcg.sort((a, b) => a.num.localeCompare(b.num));
const seen = new Set(); const pcgU = pcg.filter(a => !seen.has(a.num) && seen.add(a.num));
const ues = plan.ues.filter(u => chapitres.some(c => c.ue === u.code) || !lenient);
const data = { ues, chapitres, pcg: pcgU, build: { date: new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" }) } };
const tpl = fs.readFileSync(path.join(ROOT, "src/index.html"), "utf8");
const json = JSON.stringify(data).replace(/<\/script/gi, "<\\/script");
const out = tpl.replace("/*__DATA__*/null", json);
fs.mkdirSync(path.join(ROOT, "dist"), { recursive: true });
fs.writeFileSync(path.join(ROOT, "dist/DebitCredit.html"), out);
const nEx = chapitres.reduce((a, c) => a + c.exercices.length, 0);
console.log(`dist/DebitCredit.html : ${chapitres.length} chapitres, ${nEx} exercices, ${pcgU.length} comptes, ${(out.length / 1024).toFixed(0)} Ko`);
if (skipped.length) console.log("Ignorés : " + skipped.join(", "));
