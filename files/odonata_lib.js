// Shared by odonatatree.html and odonatalist.html: reading the World Odonata
// List, matching names against it, and the life-list CSV both pages exchange.
'use strict';

window.OdoLib = (function () {

  // ── CSV parser ──────────────────────────────────────────────
  // RFC 4180-ish, quotes tracked across the whole text (same scanner as
  // birdtree.html). Returns an array of row arrays.
  function parseCSVRows(text) {
    text = text.replace(/^﻿/, '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const rows = [];
    let row = [], cur = '', quoted = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c !== '"') { cur += c; continue; }
        if (text[i + 1] === '"') { cur += '"'; i++; }
        else quoted = false;
      }
      else if (c === '"')  quoted = true;
      else if (c === ',')  { row.push(cur); cur = ''; }
      else if (c === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; }
      else cur += c;
    }
    if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
    return rows;
  }

  // Rows as objects keyed by the (trimmed) header.
  function parseCSV(text) {
    const rows = parseCSVRows(text);
    if (!rows.length) return [];
    const headers = rows[0].map(h => h.trim());
    return rows.slice(1).filter(r => r.some(v => v.trim())).map(r => {
      const obj = {};
      headers.forEach((h, i) => { obj[h] = (r[i] || '').trim(); });
      return obj;
    });
  }

  // ── Names ───────────────────────────────────────────────────
  // "Genus epithet" from anything that starts with a binomial: drops the
  // authority, a "?" of uncertain placement, a subgenus in parentheses and
  // any third (subspecific) word. Returns '' if there is no binomial.
  function binomial(s) {
    if (!s) return '';
    const w = s.replace(/\?/g, '').replace(/\s+\([A-Z][a-z]+\)\s+/, ' ')
               .trim().split(/\s+/);
    if (w.length < 2 || !/^[A-Z][a-z]+$/.test(w[0]) || !/^[a-z][a-z-]*$/.test(w[1])) return '';
    return w[0] + ' ' + w[1];
  }

  // English names for families that have a settled one. Many Odonata
  // families have none, and the scientific name is what is shown either way.
  const FAMILY_EN = {
    Hemiphlebiidae: 'Ancient greenling',
    Lestidae: 'Spreadwings',
    Synlestidae: 'Malachites and sylphs',
    Platystictidae: 'Shadowdamsels',
    Calopterygidae: 'Demoiselles and jewelwings',
    Chlorocyphidae: 'Jewels',
    Euphaeidae: 'Gossamerwings',
    Polythoridae: 'Bannerwings',
    Argiolestidae: 'Flatwings',
    Isostictidae: 'Narrow-wings',
    Platycnemididae: 'Featherlegs and threadtails',
    Coenagrionidae: 'Pond damselflies',
    Aeshnidae: 'Hawkers and darners',
    Austropetaliidae: 'Redspots',
    Petaluridae: 'Petaltails',
    Gomphidae: 'Clubtails',
    Cordulegastridae: 'Spiketails and goldenrings',
    Synthemistidae: 'Tigertails',
    Macromiidae: 'Cruisers',
    Corduliidae: 'Emeralds',
    Libellulidae: 'Skimmers',
  };

  // ── World Odonata List ──────────────────────────────────────
  // The list is hierarchical: each row fills one column and applies to the
  // rows below it. A subfamily heading lasts until the next one or the end of
  // its family. The exception is Coenagrionidae: its one subfamily,
  // Protoneurinae, is listed first and never closed, so every later genus
  // would inherit it. Its other genera have no accepted subfamily (Carter et
  // al. 2026), so the family is kept without subfamilies.
  //
  // Besides each accepted binomial, a species can be found by its listed
  // synonyms ("Syn Genus epithet ..."), by its original combination
  // ("Perissolestes castor (Kennedy, 1937) [Perilestes]" -> Perilestes castor)
  // and by a name given in parentheses. An alias claimed by two species, or
  // equal to an accepted name, is dropped rather than guessed.
  function parseWOL(rows) {
    if (!rows.length) throw new Error('File is empty.');
    const need = ['Suborder', 'Superfamily', 'Family', 'Genus', 'Species'];
    const miss = need.filter(k => !(k in rows[0]));
    if (miss.length) throw new Error('Not a World Odonata List CSV (missing ' + miss.join(', ') + ').');

    const first = s => (s || '').trim().split(/\s+/)[0] || '';
    const species = [], families = [], famSeen = new Map();
    const aliasOwners = new Map();
    const addAlias = (alias, sci) => {
      if (!alias || alias === sci) return;
      if (!aliasOwners.has(alias)) aliasOwners.set(alias, new Set());
      aliasOwners.get(alias).add(sci);
    };
    const OPEN_SUBFAMILIES = new Set(['Coenagrionidae']);
    let sub = '', sup = '', fam = '', subfam = '', last = null;

    for (const r of rows) {
      if (r.Suborder)    { sub = first(r.Suborder); sup = ''; fam = ''; subfam = ''; }
      if (r.Superfamily) { sup = first(r.Superfamily); fam = ''; subfam = ''; }
      if (r.Family) {
        fam = first(r.Family); subfam = '';
        if (fam.toUpperCase() === 'INCERTAE') fam = sup + ' incertae sedis';
        if (!famSeen.has(fam)) {
          const f = { name: fam, superfamily: sup, suborder: sub, en: FAMILY_EN[fam] || '' };
          famSeen.set(fam, f); families.push(f);
        }
      }
      if (r.Subfamily && fam && !OPEN_SUBFAMILIES.has(fam)) subfam = first(r.Subfamily);
      if (r.Species) {
        const full = r.Species.trim();
        const sci = binomial(full);
        if (!sci || !fam) { last = null; continue; }
        // Authority is what follows the binomial, minus the annotations: an
        // [original genus], a parenthesised original name ("(Leptagrion?
        // inornatum Selys, 1876)") and notes such as "(doubtful species)".
        // "(Hagen in Selys, 1862)" and "(Palisot de Beauvois, 1807)" are
        // authorities, not names: "in" and name particles are never epithets.
        const ORIG_NAME = /^([A-Z][a-z]+\??\s+(?!(?:in|de|du|da|del|dos|la|le|van|von|der)\b)[a-z][a-z-]*)\b/;
        const author = full.split(/\s+/).slice(2).join(' ')
          .replace(/\s*\[[^\]]*\]/g, '')
          .replace(/\s*\(([^)]*)\)/g, (m, inner) =>
            /^(doubtful|original|incertae|nec\b)/i.test(inner) || ORIG_NAME.test(inner) ? '' : m)
          .trim();
        last = { sci, author, genus: sci.split(' ')[0], family: fam, subfamily: subfam,
                 superfamily: sup, suborder: sub, synonyms: [],
                 doubtful: /doubtful species/i.test(full) };
        // Older names for this species: listed synonyms, plus the original
        // combination and any original spelling given in the entry itself.
        const older = n => { if (n && n !== sci && !last.synonyms.includes(n)) last.synonyms.push(n); };
        species.push(last);
        const orig = /\[([A-Z][a-z]+)\]/.exec(full);
        if (orig) { const n = orig[1] + ' ' + sci.split(' ')[1]; older(n); addAlias(n, sci); }
        for (const m of full.matchAll(/\(([^)]*)\)/g)) {
          const n = ORIG_NAME.exec(m[1]);
          if (n) { older(binomial(n[1])); addAlias(binomial(n[1]), sci); }
        }
      }
      if (r.Synonym && last) {
        const syn = binomial(r.Synonym.replace(/^Syn\s+/i, ''));
        if (syn) { if (!last.synonyms.includes(syn)) last.synonyms.push(syn); addAlias(syn, last.sci); }
      }
    }
    if (!species.length) throw new Error('No species rows found.');

    const bySci = new Map(species.map(s => [s.sci, s]));
    const alias = new Map();
    for (const [a, owners] of aliasOwners) {
      if (owners.size === 1 && !bySci.has(a)) alias.set(a, [...owners][0]);
    }
    return { species, families, bySci, alias };
  }

  // Accepted name for any binomial the taxonomy knows, else ''.
  function resolve(tax, name) {
    const b = binomial(name);
    if (!b) return '';
    if (tax.bySci.has(b)) return b;
    return tax.alias.get(b) || '';
  }

  function loadBundled() {
    if (typeof window.WOL_CSV_TEXT !== 'string') return null;
    return parseWOL(parseCSV(window.WOL_CSV_TEXT));
  }

  // ── Regional lists: China (Chinese names), North America (English names) ──
  // Each list (files/odonata_china.js, files/odonata_north_america.js, built
  // from the CSVs of the same names) gives the species of a region with a name
  // in another language. A row is placed by its Scientific Name, else by its
  // Name in Source, through resolve(), so a later list version that renames
  // or lumps a species still finds it. Where the list lumps several of the
  // source's species into one, the row printed under the accepted name gives
  // the name and the others become alternatives.
  // Returns Map accepted name -> { name, alt[] }, and the rows not placed.
  function placeRegional(tax, csvText, nameCol) {
    const bySp = new Map(), lost = [];
    for (const r of parseCSV(csvText)) {
      const sci = resolve(tax, r['Scientific Name']) || resolve(tax, r['Name in Source']);
      if (!sci) { lost.push(r); continue; }
      if (!bySp.has(sci)) bySp.set(sci, []);
      bySp.get(sci).push(r);
    }
    const out = new Map();
    for (const [sci, rows] of bySp) {
      const main = rows.find(r => binomial(r['Name in Source']) === sci) || rows[0];
      const name = main[nameCol];
      out.set(sci, { name, alt: [...new Set(rows.map(r => r[nameCol]))].filter(n => n !== name) });
    }
    return { map: out, lost };
  }

  // A regional list: marks its species with s.regions[key] = { name, alt }
  // (the name may be empty for a species with no name in use yet) and keeps
  // the names of higher taxa (suborders, superfamilies, families, genera) from
  // the optional taxa CSV as tax.regionTaxa[key], keyed by scientific name. A
  // taxon the list has since sunk simply labels nothing.
  function attachRegion(tax, key, csvText, nameCol, taxaCsvText) {
    if (typeof csvText !== 'string') return null;
    const { map, lost } = placeRegional(tax, csvText, nameCol);
    for (const [sci, v] of map) {
      const s = tax.bySci.get(sci);
      (s.regions || (s.regions = {}))[key] = { name: v.name, alt: v.alt.filter(Boolean) };
    }
    const taxa = new Map();
    if (typeof taxaCsvText === 'string') {
      for (const r of parseCSV(taxaCsvText)) if (r[nameCol]) taxa.set(r['Scientific Name'], r[nameCol]);
    }
    (tax.regionTaxa || (tax.regionTaxa = {}))[key] = taxa;
    return { count: map.size, lost };
  }

  // ── Life list CSV ───────────────────────────────────────────
  // What odonatalist.html exports and odonatatree.html reads. Any CSV with a
  // scientific-name column also works: an iNaturalist observation export
  // (taxon_species_name / scientific_name), a spreadsheet, etc. Rows above
  // species rank and names the taxonomy does not know are counted, not kept.
  const NAME_COLS = ['scientific name', 'taxon_species_name', 'scientific_name',
                     'sci_name', 'species', 'taxon', 'name'];

  function readLifeList(tax, rows) {
    const keys = rows.length ? Object.keys(rows[0]) : [];
    const cols = NAME_COLS.map(n => keys.find(k => k.toLowerCase().trim() === n)).filter(Boolean);
    if (!cols.length) throw new Error('No scientific-name column found (columns: ' + keys.slice(0, 6).join(', ') + ').');
    const seen = new Set(), unmatched = new Set();
    for (const r of rows) {
      const raw = cols.map(c => r[c]).find(v => v && v.trim()) || '';
      if (!binomial(raw)) continue;                // genus-level or blank
      const sci = resolve(tax, raw);
      if (sci) seen.add(sci); else unmatched.add(binomial(raw));
    }
    return { seen, unmatched: [...unmatched].sort() };
  }

  function csvField(v) {
    v = String(v == null ? '' : v);
    return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }

  function lifeListCSV(tax, seenSet) {
    const out = [['Scientific Name', 'Authority', 'Genus', 'Family', 'Superfamily', 'Suborder']];
    for (const s of tax.species) {
      if (seenSet.has(s.sci)) out.push([s.sci, s.author, s.genus, s.family, s.superfamily, s.suborder]);
    }
    return out.map(r => r.map(csvField).join(',')).join('\n') + '\n';
  }

  function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  // ── The list kept in this browser ───────────────────────────
  // odonatalist.html saves here as you tick; odonatatree.html offers it when
  // no file has been dropped. Storage may be unavailable (private windows,
  // blocked site data), so every access is guarded.
  const STORE_KEY = 'odonata-life-list-v1';

  function loadSaved() {
    try {
      const v = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      return v && Array.isArray(v.species) ? v : null;
    } catch (e) { return null; }
  }

  function save(seenSet) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        species: [...seenSet].sort(), updated: new Date().toISOString() }));
      return true;
    } catch (e) { return false; }
  }

  function readFile(file) {
    return new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onload  = e => resolve(e.target.result);
      r.onerror = () => reject(new Error('Could not read ' + file.name));
      r.readAsText(file, 'UTF-8');
    });
  }

  return { parseCSV, parseWOL, binomial, resolve, loadBundled, attachRegion, readLifeList,
           lifeListCSV, downloadText, loadSaved, save, readFile, FAMILY_EN, STORE_KEY };
})();
