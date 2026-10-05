#!/usr/bin/env node
// Croise les comptes utilisés dans les chapitres (écritures de leçon, palettes, solutions) avec le plan comptable commenté.
const fs = require("fs"), path = require("path");
const pcg = {}; for (const f of fs.readdirSync("data/pcg")) if (f.endsWith(".json")) for (const a of JSON.parse(fs.readFileSync(path.join("data/pcg", f), "utf8")).comptes) pcg[a.num] = a;
const problems = [];
for (const dir of fs.readdirSync("data")) {
  if (!fs.statSync(path.join("data", dir)).isDirectory() || dir === "pcg") continue;
  for (const f of fs.readdirSync(path.join("data", dir))) {
    if (!f.endsWith(".json")) continue;
    const ch = JSON.parse(fs.readFileSync(path.join("data", dir, f), "utf8"));
    const used = new Map();
    const add = (a, w) => { if (!used.has(a)) used.set(a, w); };
    ch.lecon.forEach((s, i) => (s.entry || []).forEach(l => add(l.a, `lecon[${i}]`)));
    ch.exercices.forEach((e, i) => { if (e.type === "ecriture") { e.palette.forEach(a => add(a, `exercices[${i}]`)); e.sol.forEach(s => s.forEach(l => add(l.a, `exercices[${i}]`))); } });
    for (const [a, w] of used) {
      if (!pcg[a]) { const parent = Object.keys(pcg).filter(k => a.startsWith(k)).sort((x, y) => y.length - x.length)[0]; problems.push(`${ch.id} ${w}: compte ${a} absent du plan commenté${parent ? ` (parent connu : ${parent} ${pcg[parent].label})` : ""}`); }
      else if (/^supprim/i.test(pcg[a].pcg2025 || "")) problems.push(`${ch.id} ${w}: compte ${a} marqué supprimé par le PCG 2025 (${pcg[a].pcg2025})`);
    }
  }
}
console.log(problems.length ? problems.join("\n") : "Tous les comptes utilisés existent dans le plan commenté.");
console.log(`${Object.keys(pcg).length} comptes dans le plan.`);
