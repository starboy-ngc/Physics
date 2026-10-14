#!/usr/bin/env node
// Contrôle global des fiches documentaires : présence, hésitations dans le texte affiché, doublons d'items, couverture en liens officiels.
const fs = require("fs"), path = require("path");
const plan = JSON.parse(fs.readFileSync("data/plan.json", "utf8"));
const HESIT = /(à vérifier|non vérifi|non confirm|non recoup|sous réserve de vérification|\(\?\)|TODO)/i;
let problems = 0, items = 0, withUrl = 0, withCite = 0;
const strip = s => String(s || "").replace(/<[^>]+>/g, "");
for (const c of plan.chapitres) {
  const f = path.join("data", c.ue.toLowerCase(), c.id + ".fiche.json");
  if (!fs.existsSync(f)) { console.log(`✗ ${c.id} : fiche absente`); problems++; continue; }
  const j = JSON.parse(fs.readFileSync(f, "utf8"));
  const seen = new Set(); const issues = [];
  const texts = [j.programme.ref, ...(j.programme.points || []), ...j.textes.flatMap(t => [t.objet, t.version])];
  texts.forEach(t => { if (HESIT.test(strip(t))) issues.push(`programme/textes : « ${strip(t).slice(0, 80)} »`); });
  for (const s of j.sections) for (const it of s.items) {
    items++; if (it.url) withUrl++; if (it.cite) withCite++;
    const t = strip(it.t);
    if (HESIT.test(t) || HESIT.test(strip(it.src))) issues.push(`${s.h} : hésitation « ${t.slice(0, 90)} »`);
    const k = t.toLowerCase().replace(/\s+/g, " ").slice(0, 120);
    if (seen.has(k)) issues.push(`${s.h} : item en double « ${t.slice(0, 60)} »`); seen.add(k);
  }
  if (issues.length) { problems += issues.length; console.log(`✗ ${c.id}`); issues.forEach(i => console.log("   - " + i)); }
}
console.log(`${items} énoncés, ${withUrl} avec lien officiel direct (${Math.round(withUrl / Math.max(1, items) * 100)} %), ${withCite} avec extrait verbatim.`);
console.log(problems ? `${problems} problème(s).` : "Aucun problème.");
process.exit(problems ? 1 : 0);
