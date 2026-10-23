#!/usr/bin/env node
// Assemble src/index.html + data/**/*.json → dist/DebitCredit.html (fichier unique, hors ligne). Usage : node build.js [--lenient]
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const ROOT = __dirname; const lenient = process.argv.includes("--lenient"); const strict = process.argv.includes("--strict");
// Renvoi vers le cours : pour chaque exercice et chaque carte, la partie de la leçon du chapitre dont le vocabulaire est le plus proche
// (TF-IDF calculé sur les parties du chapitre). Nette avance sur la deuxième : une partie ; sinon les deux plus proches ; trop faible : aucune.
const STOP = new Set("dans pour avec sans sous entre plus moins etre avoir fait faire elle elles ils leur leurs cette ces cet celui celle ceux sont sera peut doit tout tous toute toutes quel quelle quels quelles lorsque quand comme mais donc ainsi alors aussi meme autre autres selon apres avant encore tres bien deux trois entreprise societe article code compte comptes vrai faux question reponse exemple".split(" "));
const toks = s => String(s || "").replace(/<[^>]+>/g, " ").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(/[^a-z0-9]+/).filter(w => w.length >= 4 && !STOP.has(w)).map(w => w.replace(/(aux|s|x)$/, ""));
const bag = ws => { const m = new Map(); ws.forEach(w => m.set(w, (m.get(w) || 0) + 1)); return m; };
function lessonLinks(ch) {
  const L = ch.lecon || []; if (L.length < 2) return;
  const secs = L.map(s => bag(toks(`${s.h || ""} ${s.h || ""} ${s.html} ${JSON.stringify(s.entry || "")}`)));
  const df = new Map(); secs.forEach(v => v.forEach((_, w) => df.set(w, (df.get(w) || 0) + 1)));
  const idf = w => Math.log((secs.length + 1) / ((df.get(w) || 0) + 0.5));
  const norm = v => Math.sqrt([...v].reduce((a, [w, c]) => a + (c * idf(w)) ** 2, 0)) || 1;
  const sn = secs.map(norm);
  const link = (o, text) => {
    const v = bag(toks(text)); const vn = norm(v);
    const sc = secs.map((s, i) => { let d = 0; v.forEach((c, w) => { if (s.has(w)) d += c * s.get(w) * idf(w) ** 2; }); return [d / (vn * sn[i]), i]; }).sort((a, b) => b[0] - a[0]);
    if (sc[0][0] < 0.06) return;
    o.sec = sc[0][0] >= 1.3 * sc[1][0] ? [sc[0][1]] : [sc[0][1], sc[1][1]];
  };
  ch.exercices.forEach(e => link(e, [e.q, ...(e.opts || []), e.why, ...(e.items || []).map(x => x[0])].join(" ")));
  (ch.cartes || []).forEach(k => link(k, `${k.q} ${k.r}`));
}
const plan = JSON.parse(fs.readFileSync(path.join(ROOT, "data/plan.json"), "utf8"));
const order = Object.fromEntries(plan.ues.map((u, i) => [u.code, i]));
const chapitres = []; const skipped = []; const rappels = [];
for (const p of plan.chapitres) {
  // Chapitre en brouillon (vérification sur sources officielles pas terminée) : jamais publié.
  if (p.brouillon) { skipped.push(p.id + " (brouillon)"); continue; }
  // UE en « rappels » (UE1) : une page de rappels courts par chapitre, sans exercices ni cartes.
  if (p.rappel) {
    const fr = path.join(ROOT, "data", p.ue.toLowerCase(), p.id + ".rappel.json");
    let rok = fs.existsSync(fr); if (rok) { try { execFileSync("node", [path.join(ROOT, "validate.js"), fr], { stdio: "pipe" }); } catch (e) { rok = false; } }
    if (rok) rappels.push(JSON.parse(fs.readFileSync(fr, "utf8"))); else skipped.push(p.id + " (rappels absents ou invalides)");
    continue;
  }
  const f = path.join(ROOT, "data", p.ue.toLowerCase(), p.id + ".json");
  if (!fs.existsSync(f)) { skipped.push(p.id + " (absent)"); continue; }
  let ok = true; try { execFileSync("node", [path.join(ROOT, "validate.js"), f], { stdio: "pipe" }); } catch (e) { ok = false; }
  if (!ok && !lenient) { skipped.push(p.id + " (invalide)"); continue; }
  const ch = JSON.parse(fs.readFileSync(f, "utf8"));
  // Identifiant stable écrit dans les données (la progression y est attachée) : une suppression ne décale rien.
  ch.exercices.forEach((e, i) => { e.id = e.id || `${ch.id}-${i}`; e.chap = ch.id; });
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
  lessonLinks(ch);
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
rappels.sort((a, b) => a.ordre - b.ordre);
const rapUe = rappels.length ? plan.ues.find(u => u.code === rappels[0].ue) : null;
const data = { ues, chapitres, pcg: pcgU, annales, rappels: rapUe ? { ue: rapUe, pages: rappels } : null, build: { date: new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" }) } };
const tpl = fs.readFileSync(path.join(ROOT, "src/index.html"), "utf8");
const json = JSON.stringify(data).replace(/<\/script/gi, "<\\/script");
const out = tpl.replace("/*__DATA__*/null", json);
fs.mkdirSync(path.join(ROOT, "dist"), { recursive: true });
// Fichier à télécharger : document HTML complet (doctype, encodage, affichage mobile), qui s'ouvre tel quel par double-clic.
// src/index.html est un fragment (en-tête puis contenu) : la partie avant la fin de la feuille de style va dans <head>.
const cut = out.indexOf("</style>") + "</style>".length;
const page = `<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n${out.slice(0, cut)}\n</head>\n<body>\n${out.slice(cut).trim()}\n</body>\n</html>\n`;
fs.writeFileSync(path.join(ROOT, "dist/DebitCredit.html"), page);
// Variante pour une page hébergée qui fournit elle-même l'enveloppe du document : node build.js --fragment <fichier>
const fi = process.argv.indexOf("--fragment"); if (fi > 0 && process.argv[fi + 1]) fs.writeFileSync(process.argv[fi + 1], out);
const nEx = chapitres.reduce((a, c) => a + c.exercices.length, 0);
const nCartes = chapitres.reduce((a, c) => a + (c.cartes || []).length, 0);
const nNotion = chapitres.reduce((a, c) => a + c.exercices.filter(e => e.nature === "notion").length, 0);
const nAnn = annales ? Object.values(annales.epreuves).reduce((a, e) => a + e.sessions.length, 0) : 0;
console.log(`dist/DebitCredit.html : ${chapitres.length} chapitres (${chapitres.filter(c => c.fiche).length} fiches), ${nEx} exercices dont ${nNotion} de notion, ${nCartes} cartes, ${pcgU.length} comptes, ${nAnn} annales, ${rappels.length} pages de rappels, ${(out.length / 1024).toFixed(0)} Ko`);
if (skipped.length) console.log("Ignorés : " + skipped.join(", "));
