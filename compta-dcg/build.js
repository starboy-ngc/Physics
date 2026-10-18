#!/usr/bin/env node
// Assemble src/index.html + data/**/*.json → dist/DebitCredit.html (fichier unique, hors ligne). Usage : node build.js [--lenient]
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const ROOT = __dirname; const lenient = process.argv.includes("--lenient"); const strict = process.argv.includes("--strict");
const plan = JSON.parse(fs.readFileSync(path.join(ROOT, "data/plan.json"), "utf8"));
const order = Object.fromEntries(plan.ues.map((u, i) => [u.code, i]));
const chapitres = []; const skipped = [];
for (const p of plan.chapitres) {
  // Chapitre en brouillon (vérification sur sources officielles pas terminée) : jamais publié.
  if (p.brouillon) { skipped.push(p.id + " (brouillon)"); continue; }
  const f = path.join(ROOT, "data", p.ue.toLowerCase(), p.id + ".json");
  if (!fs.existsSync(f)) { skipped.push(p.id + " (absent)"); continue; }
  let ok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), f], { stdio: "pipe" }); } catch (e) { ok = false; }
  if (!ok && !lenient) { skipped.push(p.id + " (invalide)"); continue; }
  const ch = JSON.parse(fs.readFileSync(f, "utf8"));
  ch.exercices.forEach((e, i) => { e.id = `${ch.id}-${i}`; e.chap = ch.id; });
  const ff = f.replace(/\.json$/, ".fiche.json");
  if (fs.existsSync(ff)) {
    let fok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), ff], { stdio: "pipe" }); } catch (e) { fok = false; }
    if (fok || lenient) ch.fiche = JSON.parse(fs.readFileSync(ff, "utf8")); else skipped.push(p.id + " (fiche invalide)");
  } else if (strict) skipped.push(p.id + " (fiche absente)");
  const fc = f.replace(/\.json$/, ".cartes.json");
  if (fs.existsSync(fc)) {
    let cok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), fc], { stdio: "pipe" }); } catch (e) { cok = false; }
    if ((cok || lenient) && ch.fiche) ch.cartes = JSON.parse(fs.readFileSync(fc, "utf8")).cartes; else skipped.push(p.id + " (cartes invalides)");
  } else if (strict) skipped.push(p.id + " (cartes absentes)");
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
// Une matière sans chapitre validé n'est pas publiée (UE en cours de rédaction).
const ues = plan.ues.filter(u => chapitres.some(c => c.ue === u.code));
const annF = path.join(ROOT, "data/annales.json");
const annales = fs.existsSync(annF) ? JSON.parse(fs.readFileSync(annF, "utf8")) : null;
if (annales) for (const code of Object.keys(annales.epreuves)) if (!ues.some(u => u.code === code)) delete annales.epreuves[code];
const data = { ues, chapitres, pcg: pcgU, annales, build: { date: new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" }) } };
const tpl = fs.readFileSync(path.join(ROOT, "src/index.html"), "utf8");
const json = JSON.stringify(data).replace(/<\/script/gi, "<\\/script");
const out = tpl.replace("/*__DATA__*/null", json);
fs.mkdirSync(path.join(ROOT, "dist"), { recursive: true });
fs.writeFileSync(path.join(ROOT, "dist/DebitCredit.html"), out);
const nEx = chapitres.reduce((a, c) => a + c.exercices.length, 0);
const nCartes = chapitres.reduce((a, c) => a + (c.cartes || []).length, 0);
const nNotion = chapitres.reduce((a, c) => a + c.exercices.filter(e => e.nature === "notion").length, 0);
const nAnn = annales ? Object.values(annales.epreuves).reduce((a, e) => a + e.sessions.length, 0) : 0;
console.log(`dist/DebitCredit.html : ${chapitres.length} chapitres (${chapitres.filter(c => c.fiche).length} fiches), ${nEx} exercices dont ${nNotion} de notion, ${nCartes} cartes, ${pcgU.length} comptes, ${nAnn} annales, ${(out.length / 1024).toFixed(0)} Ko`);
if (skipped.length) console.log("Ignorés : " + skipped.join(", "));
