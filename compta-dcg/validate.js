#!/usr/bin/env node
// Validateur des fichiers de chapitre et de plan comptable. Usage : node validate.js <fichier.json> [...]
const fs = require("fs");
const ALLOWED_TAGS = new Set(["p", "ul", "ol", "li", "b", "i", "code", "br", "table", "thead", "tbody", "tr", "th", "td", "div", "span", "strong", "em"]);
const FIAB = /^(stable|millésimé 20\d\d)$/;
let total = 0;
function checkHtml(html, where, errs) {
  const tags = html.match(/<\/?([a-zA-Z0-9]+)([^>]*)>/g) || [];
  for (const t of tags) {
    const m = t.match(/^<\/?([a-zA-Z0-9]+)([^>]*)>$/); const name = m[1].toLowerCase(); const attrs = m[2].trim();
    if (!ALLOWED_TAGS.has(name)) errs.push(`${where}: balise interdite <${name}>`);
    if (attrs && !/^class="(note|mono)"$/.test(attrs) && !/^\/$/.test(attrs)) errs.push(`${where}: attribut interdit dans ${t}`);
  }
  if (/<script|javascript:|on\w+=/i.test(html)) errs.push(`${where}: script interdit`);
}
function isAcct(a) { return typeof a === "string" && /^[1-7]\d{1,5}$/.test(a); }
function checkEntry(entry, where, errs) {
  if (!Array.isArray(entry) || entry.length < 2) { errs.push(`${where}: écriture avec moins de 2 lignes`); return; }
  let d = 0, c = 0;
  for (const l of entry) {
    if (!isAcct(l.a)) errs.push(`${where}: numéro de compte invalide « ${l.a} »`);
    if (typeof l.d !== "number" || typeof l.c !== "number" || l.d < 0 || l.c < 0) errs.push(`${where}: montants d/c non numériques`);
    if ((l.d > 0) === (l.c > 0)) errs.push(`${where}: une ligne doit avoir soit un débit soit un crédit (compte ${l.a})`);
    d += l.d || 0; c += l.c || 0;
  }
  if (Math.abs(d - c) > 0.005) errs.push(`${where}: écriture déséquilibrée (D ${d} / C ${c})`);
}
function checkChapter(ch, errs) {
  for (const k of ["id", "ue", "ordre", "title", "resume", "duree", "niveau", "lecon", "sources", "exercices"]) if (ch[k] === undefined) errs.push(`champ manquant : ${k}`);
  if (!/^ue(2|3|4|6|9|10)-\d\d$/.test(ch.id || "")) errs.push(`id invalide : ${ch.id}`);
  if (!Array.isArray(ch.lecon) || ch.lecon.length < 4) errs.push(`lecon : au moins 4 sections attendues (${(ch.lecon || []).length})`);
  (ch.lecon || []).forEach((s, i) => {
    if (typeof s.html !== "string" || s.html.length < 150) errs.push(`lecon[${i}] : html trop court`);
    else checkHtml(s.html, `lecon[${i}]`, errs);
    if (s.entry) checkEntry(s.entry, `lecon[${i}].entry`, errs);
  });
  if (!Array.isArray(ch.sources) || ch.sources.length < 2) errs.push("sources : au moins 2 références");
  const ex = ch.exercices || [];
  if (ex.length < 18) errs.push(`exercices : ${ex.length} (minimum 18)`);
  const counts = {};
  ex.forEach((e, i) => {
    const w = `exercices[${i}]`; counts[e.type] = (counts[e.type] || 0) + 1;
    if (typeof e.q !== "string" || e.q.length < 15) errs.push(`${w}: énoncé manquant`);
    if (typeof e.why !== "string" || e.why.length < 40) errs.push(`${w}: explication « why » trop courte`);
    if (typeof e.src !== "string" || e.src.length < 3) errs.push(`${w}: source « src » manquante`);
    if (!FIAB.test(e.fiab || "")) errs.push(`${w}: fiab invalide « ${e.fiab} »`);
    if (![1, 2, 3].includes(e.niveau)) errs.push(`${w}: niveau doit être 1, 2 ou 3`);
    switch (e.type) {
      case "qcm":
        if (!Array.isArray(e.opts) || e.opts.length < 3 || e.opts.length > 5) errs.push(`${w}: qcm doit avoir 3 à 5 options`);
        else { if (new Set(e.opts).size !== e.opts.length) errs.push(`${w}: options en double`); if (!Number.isInteger(e.a) || e.a < 0 || e.a >= e.opts.length) errs.push(`${w}: index de réponse invalide`); }
        break;
      case "multi":
        if (!Array.isArray(e.opts) || e.opts.length < 4 || e.opts.length > 6) errs.push(`${w}: multi doit avoir 4 à 6 options`);
        else if (!Array.isArray(e.a) || e.a.length < 2 || e.a.length >= e.opts.length || e.a.some(x => !Number.isInteger(x) || x < 0 || x >= e.opts.length) || new Set(e.a).size !== e.a.length) errs.push(`${w}: multi : « a » doit lister 2 index valides ou plus, sans doublon, sans être toutes les options`);
        break;
      case "calc":
        if (typeof e.a !== "number" || !isFinite(e.a)) errs.push(`${w}: calc : « a » doit être un nombre`);
        if (e.tol !== undefined && (typeof e.tol !== "number" || e.tol < 0)) errs.push(`${w}: tol invalide`);
        if (typeof e.unit !== "string") errs.push(`${w}: calc : « unit » manquant (chaîne, éventuellement vide)`);
        break;
      case "tri":
        if (!Array.isArray(e.cats) || e.cats.length < 2 || e.cats.length > 7) errs.push(`${w}: tri : 2 à 7 catégories`);
        if (!Array.isArray(e.items) || e.items.length < 3) errs.push(`${w}: tri : au moins 3 items`);
        else e.items.forEach((it, k) => { if (!Array.isArray(it) || typeof it[0] !== "string" || !Number.isInteger(it[1]) || it[1] < 0 || it[1] >= (e.cats || []).length) errs.push(`${w}: tri item ${k} invalide`); });
        break;
      case "ecriture":
        if (!Array.isArray(e.palette) || e.palette.length < 3 || e.palette.length > 9 || e.palette.some(a => !isAcct(a))) errs.push(`${w}: palette invalide (3 à 9 comptes)`);
        if (!Array.isArray(e.sol) || !e.sol.length) errs.push(`${w}: sol manquante`);
        else e.sol.forEach((s, k) => { checkEntry(s, `${w}.sol[${k}]`, errs); (s || []).forEach(l => { if (e.palette && !e.palette.includes(l.a)) errs.push(`${w}: compte ${l.a} de la solution absent de la palette`); }); });
        if (/\b(675|775)\b/.test(JSON.stringify(e))) errs.push(`${w}: comptes 675/775 supprimés par le PCG 2025 (utiliser 657/757)`);
        break;
      default: errs.push(`${w}: type inconnu « ${e.type} »`);
    }
  });
  const qcmShare = ((counts.qcm || 0) + (counts.multi || 0)) / Math.max(1, ex.length);
  if (ex.length >= 18 && qcmShare < 0.5) errs.push(`exercices : part de QCM/multi ${Math.round(qcmShare * 100)} % (minimum 50 %)`);
  if (ex.length >= 18 && (counts.calc || 0) < 2) errs.push("exercices : au moins 2 calc attendus");
  if (/\b(675|775)\b/.test(JSON.stringify(ch.lecon)) && !/avant 2025|ancien|supprim|rempla/i.test(JSON.stringify(ch.lecon))) errs.push("lecon : mention de 675/775 sans signaler qu'ils sont supprimés par le PCG 2025");
  return counts;
}
function checkPcg(list, errs) {
  if (!Array.isArray(list) || list.length < 20) { errs.push("plan comptable : liste trop courte"); return; }
  const seen = new Set();
  list.forEach((a, i) => {
    const w = `comptes[${i}]`;
    if (!isAcct(a.num)) errs.push(`${w}: numéro invalide « ${a.num} »`);
    if (seen.has(a.num)) errs.push(`${w}: numéro en double ${a.num}`); seen.add(a.num);
    if (typeof a.label !== "string" || a.label.length < 3) errs.push(`${w}: intitulé manquant`);
    if (!["D", "C", "D/C", "–"].includes(a.sens)) errs.push(`${w}: sens invalide « ${a.sens} » (D, C, D/C ou –)`);
    if (typeof a.explication !== "string" || a.explication.length < 60) errs.push(`${w}: explication trop courte (${a.num})`);
    if (a.exemple && typeof a.exemple !== "string") errs.push(`${w}: exemple doit être une chaîne`);
    if (a.piege && typeof a.piege !== "string") errs.push(`${w}: piege doit être une chaîne`);
    if (a.entry) checkEntry(a.entry, `${w}.entry`, errs);
    if (a.pcg2025 !== null && a.pcg2025 !== undefined && typeof a.pcg2025 !== "string") errs.push(`${w}: pcg2025 doit être null ou une chaîne`);
    if (a.obligatoire !== undefined && typeof a.obligatoire !== "boolean") errs.push(`${w}: obligatoire doit être booléen`);
  });
  if (list.some(a => ["675", "775", "791", "796", "797", "777"].includes(a.num) && !/supprim/i.test(a.pcg2025 || ""))) errs.push("plan comptable : 675/775/777/791/796/797 ne peuvent figurer que comme comptes supprimés (pcg2025 doit le dire)");
}
let failed = 0;
for (const f of process.argv.slice(2)) {
  const errs = [];
  let data;
  try { data = JSON.parse(fs.readFileSync(f, "utf8")); } catch (e) { console.log(`✗ ${f} : JSON invalide — ${e.message}`); failed++; continue; }
  let info = "";
  if (data.comptes) { checkPcg(data.comptes, errs); info = `${data.comptes.length} comptes`; }
  else { const c = checkChapter(data, errs); info = `${(data.exercices || []).length} exercices ${JSON.stringify(c)}`; total += (data.exercices || []).length; }
  if (errs.length) { failed++; console.log(`✗ ${f} (${info})`); errs.forEach(e => console.log("   - " + e)); }
  else console.log(`✓ ${f} (${info})`);
}
if (process.argv.length > 3 && total) console.log(`Total : ${total} exercices`);
process.exit(failed ? 1 : 0);
