// Search that understands Dutch and English, synonyms and small typos.
// Same rules as the Prompt app (app/prompt.pyw, "Zoeken"); synonyms come from data/synonyms.json.

const STOPWORDS = new Set(('de het een en of van voor met op in aan om te naar bij uit ik wil mijn je jij me mij hoe wat kan iets ' +
  'die dat dit is the a an and or for with on to my i how can want it this that please graag even laten doen').split(' '));
// Too general: only counts when found in the name or tags.
const WEAK = new Set(('skill skills claude code use gebruik gebruiken user help helpen whenever maken make create nieuw nieuwe ' +
  'new schrijven write bouwen build').split(' '));

let synonymMap = new Map();

export function norm(text) {
  return String(text ?? '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, ' ').trim();
}

export function setSynonyms(data) {
  synonymMap = new Map();
  for (const group of data?.groups ?? []) {
    const words = new Set(group.flatMap((m) => norm(m).split(' ').filter(Boolean)));
    for (const w of words) {
      if (!synonymMap.has(w)) synonymMap.set(w, new Set());
      words.forEach((x) => synonymMap.get(w).add(x));
    }
  }
}

// A pasted wall of text must not freeze the page: same limits as the app.
const MAX_QUERY_CHARS = 200;
const MAX_QUERY_TERMS = 10;

export function queryTerms(query) {
  const words = [...new Set(norm(String(query ?? '').slice(0, MAX_QUERY_CHARS)).split(' ').filter(Boolean))];
  const terms = words.filter((w) => !STOPWORDS.has(w));
  return (terms.length ? terms : words).slice(0, MAX_QUERY_TERMS);
}

function withinOneEdit(a, b) {
  if (Math.abs(a.length - b.length) > 1) return false;
  if (a.length > b.length) [a, b] = [b, a];
  let i = 0, j = 0, edits = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { i++; j++; continue; }
    if (++edits > 1) return false;
    if (a.length === b.length) i++;
    j++;
  }
  return edits + (b.length - j) + (a.length - i) <= 1;
}

function matchQuality(term, words, loose) {
  let best = 0;
  for (const w of words) {
    if (w === term) return 1;
    if (term.length >= 3 && w.startsWith(term)) best = Math.max(best, 0.85);
    else if (!loose) continue;
    else if (w.length >= 4 && term.startsWith(w)) best = Math.max(best, 0.7);
    else if (term.length >= 5 && withinOneEdit(term, w)) best = Math.max(best, 0.7);
    else if (term.length >= 4 && w.includes(term)) best = Math.max(best, 0.5);
  }
  return best;
}

function variants(term) {
  const out = new Map([[term, 1]]);
  let group = synonymMap.get(term);
  if (!group && term.length >= 4) {
    group = new Set();
    for (const [w, g] of synonymMap) if (w.startsWith(term)) g.forEach((x) => group.add(x));
  }
  for (const w of group ?? []) if (!out.has(w)) out.set(w, 0.8);
  return out;
}

/** fields: [[weight, words[], weakOk]] → score (0 = no match) */
export function scoreFields(terms, fields) {
  if (!terms.length) return 1;
  const strong = terms.filter((t) => !WEAK.has(t));
  let total = 0, matched = 0;
  for (const term of terms) {
    const weak = WEAK.has(term);
    let best = 0;
    for (const [weight, words, weakOk] of fields) {
      if (weak && !weakOk) continue;
      for (const [v, factor] of variants(term)) {
        const q = matchQuality(v, words, factor === 1);
        if (q) best = Math.max(best, weight * q * factor * (weak ? 0.6 : 1));
      }
    }
    if (best) {
      total += best;
      if (!weak || !strong.length) matched++;
    }
  }
  const counted = strong.length || terms.length;
  const needed = counted <= 2 ? 1 : Math.ceil(counted * 0.6);
  return matched < needed ? 0 : total * (0.5 + 0.5 * matched / counted);
}

export function skillFields(s, categoryLabel) {
  const words = (t) => norm(t).split(' ').filter(Boolean);
  return [
    [10, words(s.name), true],
    [7, words(s.tags.join(' ')), true],
    [5, words(s.summary_nl), false],
    [4, words(`${categoryLabel} ${s.category}`), true],
    [3, words(s.description), false],
    [2, words(s.author), true],
  ];
}

/** Keep results close to the best match. */
export function rank(scored, terms, keep = 0.25) {
  if (!terms.length || !scored.length) return scored;
  const top = Math.max(...scored.map((r) => r.score));
  return scored.filter((r) => r.score >= top * keep);
}
