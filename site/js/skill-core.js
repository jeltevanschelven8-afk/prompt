// Shared by the website (browser) and the build script (Node). The Prompt app mirrors the bits it needs in Python.
// No dependencies, no DOM access.

export const CATEGORIES = [
  'code', 'testing', 'design', 'writing', 'data', 'automation',
  'devops', 'security', 'productivity', 'learning', 'workflow', 'other',
];

export const NAME_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
export const MAX_NAME = 64;
export const MAX_DESCRIPTION = 1024;
export const ALLOWED_EXTENSIONS = ['.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.py', '.js', '.mjs', '.ts', '.sh', '.ps1', '.html', '.css', '.svg'];
export const MAX_FILE_BYTES = 200 * 1024;

function unquote(v) {
  if (v.length >= 2 && v[0] === "'" && v.at(-1) === "'") return v.slice(1, -1).replace(/''/g, "'");
  if (v.length >= 2 && v[0] === '"' && v.at(-1) === '"') {
    try { return JSON.parse(v); } catch { return v.slice(1, -1); }
  }
  if (v[0] === '[' && v.at(-1) === ']') {
    return v.slice(1, -1).split(',').map((s) => unquote(s.trim())).filter(Boolean);
  }
  return v;
}

/** Parses the small YAML subset used in SKILL.md frontmatter. */
export function parseFrontmatter(raw) {
  const text = String(raw).replace(/^﻿/, '').replace(/\r\n?/g, '\n');
  const m = /^---\n([\s\S]*?)\n---[ \t]*(?:\n|$)/.exec(text);
  if (!m) return { data: {}, body: text, hasFrontmatter: false };

  const data = {};
  const lines = m[1].split('\n');
  for (let i = 0; i < lines.length; i++) {
    const km = /^([A-Za-z0-9_-]+):[ \t]*(.*)$/.exec(lines[i]);
    if (!km) continue;
    const key = km[1];
    let v = km[2].trim();
    const isContinuation = (l) => l !== undefined && (/^[ \t]+\S/.test(l) || l.trim() === '');

    if (/^[>|][+-]?$/.test(v)) {
      const folded = v[0] === '>';
      const block = [];
      while (isContinuation(lines[i + 1])) block.push(lines[++i].trim());
      while (block.length && block.at(-1) === '') block.pop();
      if (folded) {
        let out = '';
        for (const b of block) out += b === '' ? '\n' : (out && !out.endsWith('\n') ? ' ' : '') + b;
        v = out;
      } else {
        v = block.join('\n');
      }
    } else if (v === '' && /^[ \t]+[A-Za-z0-9_-]+:/.test(lines[i + 1] ?? '')) {
      // Nested map, e.g. metadata:\n  author: x
      const block = [];
      while (isContinuation(lines[i + 1])) block.push(lines[++i]);
      const indent = Math.min(...block.filter((l) => l.trim()).map((l) => l.match(/^[ \t]*/)[0].length));
      v = parseFrontmatter(`---\n${block.map((l) => l.slice(indent)).join('\n')}\n---\n`).data;
    } else if (v === '' && /^[ \t]+-[ \t]/.test(lines[i + 1] ?? '')) {
      // YAML list:  tags:\n  - a\n  - b
      const items = [];
      while (/^[ \t]+-[ \t]/.test(lines[i + 1] ?? '')) items.push(unquote(lines[++i].replace(/^[ \t]+-[ \t]+/, '').trim()));
      v = items;
    } else {
      // Plain or quoted scalar, possibly continued on indented lines.
      while (isContinuation(lines[i + 1]) && lines[i + 1].trim() !== '') v += ' ' + lines[++i].trim();
      v = unquote(v);
    }
    data[key] = v;
  }
  return { data, body: text.slice(m[0].length), hasFrontmatter: true };
}

/**
 * Builds a SKILL.md string. JSON strings are valid YAML double-quoted scalars.
 * Marketplace fields go under `metadata:` (Agent Skills spec), which Claude ignores.
 */
export function buildSkillMd({ name, description, body, license, metadata = {} }) {
  const desc = String(description ?? '').replace(/\s+/g, ' ').trim();
  let fm = `name: ${name}\ndescription: ${JSON.stringify(desc)}\n`;
  if (license) fm += `license: ${JSON.stringify(String(license))}\n`;
  const meta = Object.entries(metadata).filter(([, v]) => v !== undefined && v !== null && String(v).trim() !== '');
  if (meta.length) fm += `metadata:\n${meta.map(([k, v]) => `  ${k}: ${JSON.stringify(Array.isArray(v) ? v.join(', ') : String(v))}`).join('\n')}\n`;
  return `---\n${fm}---\n\n${String(body ?? '').trim()}\n`;
}

/** Merges marketplace metadata from frontmatter `metadata:` / `license:` and an optional skill.json. */
export function skillMeta(data, json = {}) {
  const fm = data.metadata && typeof data.metadata === 'object' ? data.metadata : {};
  const merged = { ...fm, ...(data.license ? { license: data.license } : {}), ...json };
  // Only text counts: numbers, objects or lists in the wrong place are ignored rather than stringified.
  const text = (v, fallback) => (typeof v === 'string' && v.trim() ? v : fallback);
  const tags = Array.isArray(merged.tags) ? merged.tags.filter((t) => typeof t === 'string')
    : typeof merged.tags === 'string' ? merged.tags.split(',') : [];
  return {
    author: text(merged.author, 'anonymous').trim(),
    category: CATEGORIES.includes(merged.category) ? merged.category : 'other',
    rawCategory: merged.category,
    tags: [...new Set(tags.map((t) => String(t).toLowerCase().trim().replace(/^#/, '')).filter(Boolean))].slice(0, 8),
    version: text(merged.version, '1.0.0'),
    license: text(merged.license, 'MIT'),
    homepage: text(merged.homepage, null),
    summaryNl: text(merged.summary_nl, '').trim(),
  };
}

/** Returns { errors: string[], warnings: string[] } as message keys + params. */
export function validateSkill({ data, body, hasFrontmatter }, folderName) {
  const errors = [];
  const warnings = [];
  if (!hasFrontmatter) errors.push({ key: 'v.noFrontmatter' });
  const name = typeof data.name === 'string' ? data.name : '';
  if (!name) errors.push({ key: 'v.nameMissing' });
  else {
    if (!NAME_RE.test(name)) errors.push({ key: 'v.nameFormat' });
    if (name.length > MAX_NAME) errors.push({ key: 'v.nameLong', n: MAX_NAME });
    if (folderName && name !== folderName) errors.push({ key: 'v.nameFolder', folder: folderName });
  }
  const desc = typeof data.description === 'string' ? data.description.trim() : '';
  if (!desc) errors.push({ key: 'v.descMissing' });
  else {
    if (desc.length > MAX_DESCRIPTION) errors.push({ key: 'v.descLong', n: MAX_DESCRIPTION });
    if (desc.length < 40) warnings.push({ key: 'v.descShort' });
    if (!/\b(use|gebruik|when|wanneer|trigger)/i.test(desc)) warnings.push({ key: 'v.descWhen' });
  }
  if (!String(body ?? '').trim()) errors.push({ key: 'v.bodyEmpty' });
  else if (String(body).trim().length < 200) warnings.push({ key: 'v.bodyShort' });
  return { errors, warnings };
}

// Patterns worth a human look before installing. Informational, not a verdict.
const SAFETY_RULES = [
  // Quantifiers are bounded so a hostile file cannot make a pattern take quadratic time.
  { id: 'pipe-shell', re: /\b(curl|wget)\b[^\n|]{0,300}\|\s{0,5}(ba|z)?sh\b/i },
  { id: 'iex', re: /\b(iex|Invoke-Expression)\b/i },
  { id: 'rm-rf', re: /\brm\s{1,5}-[a-z]{0,6}(r[a-z]{0,6}f|f[a-z]{0,6}r)|\brm\s{1,5}-[rf]\s{1,5}-[rf]\b|\bRemove-Item\b[^\n]{0,200}?-Recurse\b[^\n]{0,200}?-Force\b/i },
  { id: 'skip-perms', re: /dangerously|skip[- ]permissions|bypass[- ]?permissions|--no-verify/i },
  { id: 'secrets', re: /\b(api[_ -]?key|access[_ -]?token|password|wachtwoord|private key)\b/i },
  { id: 'override', re: /ignore (all )?(previous|prior|above) instructions|negeer (alle )?(vorige|eerdere) instructies/i },
  { id: 'encoded', re: /\bbase64\b[^\n]{0,200}?(-d\b|--decode|FromBase64String)|FromBase64String/i },
  { id: 'exfil', re: /\b(webhook|ngrok|pastebin|requestbin)\b/i },
];

export function safetyScan(text) {
  const hits = [];
  for (const rule of SAFETY_RULES) {
    const m = rule.re.exec(text);
    if (m) {
      const start = text.lastIndexOf('\n', m.index) + 1;
      const end = text.indexOf('\n', m.index);
      hits.push({ id: rule.id, line: text.slice(0, m.index).split('\n').length, excerpt: text.slice(start, end === -1 ? undefined : end).trim().slice(0, 160) });
    }
  }
  const urls = new Set((text.match(/https?:\/\/[^\s)'"`>\]]+/g) || []).map((u) => { try { return new URL(u).host; } catch { return u; } }));
  return { hits, hosts: [...urls].sort() };
}

export function wordCount(text) {
  return (String(text).match(/\S+/g) || []).length;
}
