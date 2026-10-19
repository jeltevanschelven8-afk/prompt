import { t, getLang, setLang } from './i18n.js';
import { queryTerms, scoreFields, skillFields, rank, setSynonyms } from './search.js';
import {
  CATEGORIES, NAME_RE, MAX_DESCRIPTION, parseFrontmatter, buildSkillMd, validateSkill, safetyScan, skillMeta,
} from './skill-core.js';

// ── Helpers ────────────────────────────────────────────────
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
const main = $('#main');

const store = {
  get(key, fallback) {
    try { const v = localStorage.getItem('prompt.' + key); return v == null ? fallback : JSON.parse(v); } catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem('prompt.' + key, JSON.stringify(value)); } catch { /* storage blocked */ }
  },
};

const state = {
  index: null,
  config: { repo: 'OWNER/prompt', branch: 'main' },
  mine: sanitizeMine(store.get('mine', {})),
  q: '', cat: 'all', sort: 'relevance', safeOnly: false,
  sources: new Map(),
  mode: ['prompt', 'app', 'win', 'unix'].includes(store.get('mode')) ? store.get('mode') : 'prompt',
  docTab: 'doc',
  task: '',
};

function sanitizeMine(m) {
  const out = {};
  if (m && typeof m === 'object') for (const [k, v] of Object.entries(m)) if (NAME_RE.test(k)) out[k] = { active: v?.active !== false, added: v?.added || new Date().toISOString() };
  return out;
}

const BASE = new URL('.', location.href.split('#')[0]).href;
const SAFE_PATH = /^[A-Za-z0-9._-]+(?:\/[A-Za-z0-9._-]+)*$/;
const fileUrl = (name, rel = 'SKILL.md') => `${BASE}skills/${encodeURIComponent(name)}/${rel.split('/').map(encodeURIComponent).join('/')}`;
const safeFiles = (s) => s.files.filter((f) => SAFE_PATH.test(f) && !f.split('/').includes('..'));
const repoUrl = () => `https://github.com/${state.config.repo}`;
const hasRepo = () => /^[\w.-]+\/[\w.-]+$/.test(state.config.repo) && !state.config.repo.startsWith('OWNER/');
const findSkill = (name) => state.index?.skills.find((s) => s.name === name);

function summary(desc) {
  const m = /^(.+?[.!?])(?:\s|$)/.exec(desc);
  const s = m ? m[1] : desc;
  return s.length > 180 ? s.slice(0, 177).trimEnd() + '…' : s;
}

function ago(iso) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (!isFinite(diff)) return '';
  if (diff < 60) return t('time.now');
  if (diff < 3600) return t('time.min', { n: Math.floor(diff / 60) });
  if (diff < 86400) return t('time.h', { n: Math.floor(diff / 3600) });
  const d = Math.floor(diff / 86400);
  if (d === 1) return t('time.d1');
  if (d < 31) return t('time.d', { n: d });
  if (d < 365) return t('time.mo', { n: Math.floor(d / 30) });
  return t('time.y');
}

function renderMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    return window.DOMPurify.sanitize(window.marked.parse(text, { gfm: true }), { FORBID_TAGS: ['style', 'form', 'input'] });
  }
  return `<pre class="source">${esc(text)}</pre>`;
}

function toast(msg) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  $('#toasts').append(el);
  setTimeout(() => el.remove(), 2600);
}

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = Object.assign(document.createElement('textarea'), { value: text });
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.append(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    if (!ok) return toast(t('toast.copyFail'));
  }
  toast(t('toast.copied'));
}

function downloadBlob(blob, filename) {
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: filename });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

async function getSource(name, rel = 'SKILL.md') {
  const key = `${name}/${rel}`;
  if (!state.sources.has(key)) {
    state.sources.set(key, fetch(fileUrl(name, rel)).then((r) => {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).catch((e) => { state.sources.delete(key); throw e; }));
  }
  return state.sources.get(key);
}
// Synchronous read of an already-fetched source, so clipboard writes stay inside the click.
const cachedText = new Map();
async function prefetch(names) {
  await Promise.all(names.map(async (n) => {
    try { cachedText.set(n, await getSource(n)); } catch { /* shown as missing */ }
  }));
}

// ── Prompt & install command builders ──────────────────────
function buildPrompt(items, task = '') {
  const head = items.length === 1 ? t('prompt.one') : t('prompt.many', { n: items.length });
  const blocks = items.map(({ name, text }) => `<skill name="${name}">\n${text.trim()}\n</skill>`).join('\n\n');
  const tail = task.trim() ? `\n\n${t('prompt.task')} ${task.trim()}` : '';
  return `${head}\n\n${blocks}${tail}\n`;
}

function cmdWindows(skills) {
  const lines = [];
  for (const s of skills) {
    lines.push(`$d = "$HOME\\.claude\\skills\\${s.name}"; New-Item -ItemType Directory -Force $d | Out-Null`);
    for (const f of safeFiles(s)) {
      const win = f.replace(/\//g, '\\');
      if (f.includes('/')) lines.push(`New-Item -ItemType Directory -Force (Split-Path "$d\\${win}") | Out-Null`);
      lines.push(`Invoke-WebRequest -UseBasicParsing "${fileUrl(s.name, f)}" -OutFile "$d\\${win}"`);
    }
  }
  return lines.join('\n');
}

function cmdUnix(skills) {
  return skills.flatMap((s) => safeFiles(s).map((f) => `curl -fsSL --create-dirs -o ~/.claude/skills/${s.name}/${f} "${fileUrl(s.name, f)}"`)).join('\n');
}

async function downloadZip(skills) {
  if (!window.JSZip) {
    // No zip library (offline / blocked CDN): fall back to plain SKILL.md files.
    for (const s of skills) downloadBlob(new Blob([await getSource(s.name)], { type: 'text/markdown' }), `${s.name}-SKILL.md`);
    return;
  }
  toast(t('toast.zip'));
  const zip = new window.JSZip();
  for (const s of skills) {
    for (const f of safeFiles(s)) zip.file(`${s.name}/${f}`, await getSource(s.name, f));
  }
  const blob = await zip.generateAsync({ type: 'blob' });
  downloadBlob(blob, skills.length === 1 ? `${skills[0].name}.zip` : 'prompt-skills.zip');
}

// ── My skills store ────────────────────────────────────────
function saveMine() {
  store.set('mine', state.mine);
  const n = Object.keys(state.mine).length;
  const pill = $('#mine-count');
  pill.textContent = n;
  pill.hidden = n === 0;
}
function toggleSaved(name) {
  if (state.mine[name]) {
    delete state.mine[name];
    toast(t('toast.removed', { n: '/' + name }));
  } else {
    state.mine[name] = { active: true, added: new Date().toISOString() };
    toast(t('toast.saved', { n: '/' + name }));
  }
  saveMine();
  $$(`[data-toggle-save="${CSS.escape(name)}"]`).forEach(paintSaveButton);
}
function paintSaveButton(btn) {
  const saved = !!state.mine[btn.dataset.toggleSave];
  btn.classList.toggle('is-on', saved);
  btn.setAttribute('aria-pressed', saved);
  const long = btn.dataset.long === '1';
  btn.textContent = saved ? '✓ ' + t(long ? 'detail.saved' : 'card.added') : '+ ' + t(long ? 'detail.save' : 'card.add');
}

// ── Icons ──────────────────────────────────────────────────
const ICON = {
  search: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  back: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>',
  arrow: '<span aria-hidden="true">↗</span>',
  sun: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
  moon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
};

// ── Discover ───────────────────────────────────────────────
const fieldCache = new Map();
function fieldsFor(s) {
  if (!fieldCache.has(s.name)) fieldCache.set(s.name, skillFields(s, t('cat.' + s.category)));
  return fieldCache.get(s.name);
}

// Dutch one-liner when the site is in Dutch and the skill has one.
const blurb = (s) => (getLang() === 'nl' && s.summary_nl ? s.summary_nl : summary(s.description));

function filtered() {
  const terms = queryTerms(state.q);
  let list = state.index.skills
    .filter((s) => (state.cat === 'all' || s.category === state.cat) && !(state.safeOnly && s.safety.hits.length))
    .map((s) => ({ s, score: scoreFields(terms, fieldsFor(s)) }))
    .filter(({ score }) => score > 0);
  list = rank(list, terms);
  const by = {
    relevance: (a, b) => a.s.name.localeCompare(b.s.name),
    updated: (a, b) => b.s.updated.localeCompare(a.s.updated),
    name: (a, b) => a.s.name.localeCompare(b.s.name),
    saved: (a, b) => (!!state.mine[b.s.name] - !!state.mine[a.s.name]) || a.s.name.localeCompare(b.s.name),
  }[state.sort] || (() => 0);
  list.sort((a, b) => (terms.length && state.sort === 'relevance' ? b.score - a.score : 0) || by(a, b));
  return list.map((x) => x.s);
}

function card(s) {
  const notes = s.safety.hits.length;
  return `<article class="card">
    <div class="card-top">
      <span class="cat">${esc(t('cat.' + s.category))}</span>
      ${notes ? `<span class="badge badge-warn">! ${esc(notes === 1 ? t('card.notes1') : t('card.notes', { n: notes }))}</span>` : ''}
    </div>
    <h3><a href="#/skill/${encodeURIComponent(s.name)}"><span class="slash">/</span>${esc(s.name)}</a></h3>
    <p class="desc">${esc(blurb(s))}</p>
    ${s.tags.length ? `<div class="tags">${s.tags.slice(0, 4).map((x) => `<span class="tag">#${esc(x)}</span>`).join('')}</div>` : ''}
    <div class="card-foot">
      <span class="byline">${esc(t('card.by', { a: s.author }))} · ${esc(t('card.updated', { d: ago(s.updated) }))}</span>
      <button type="button" class="btn btn-sm" data-toggle-save="${esc(s.name)}"></button>
    </div>
  </article>`;
}

function renderGrid() {
  const list = filtered();
  $('#count').textContent = list.length === 1 ? t('browse.count1') : t('browse.count', { n: list.length });
  $$('.chip').forEach((c) => c.setAttribute('aria-pressed', c.dataset.cat === state.cat));
  const grid = $('#grid');
  if (!list.length) {
    grid.outerHTML = `<div id="grid" class="empty">
      <h2>${esc(t('browse.empty', { q: state.q || t('cat.' + state.cat) }))}</h2>
      <p>${esc(t('browse.emptyHint'))}</p>
      <a class="btn btn-primary" href="#/publish">${esc(t('browse.emptyCta'))}</a>
    </div>`;
  } else {
    const html = `<div id="grid" class="grid">${list.map(card).join('')}</div>`;
    grid.outerHTML = html;
    $$('#grid [data-toggle-save]').forEach(paintSaveButton);
  }
  const params = new URLSearchParams();
  if (state.q) params.set('q', state.q);
  if (state.cat !== 'all') params.set('cat', state.cat);
  const hash = '#/' + (params.toString() ? '?' + params : '');
  if (location.hash !== hash && !(hash === '#/' && !location.hash)) history.replaceState(null, '', hash);
}

function viewDiscover(params) {
  state.q = params.get('q') || '';
  state.cat = CATEGORIES.includes(params.get('cat')) ? params.get('cat') : 'all';
  const skills = state.index.skills;
  const authors = new Set(skills.map((s) => s.author)).size;
  const counts = Object.fromEntries(CATEGORIES.map((c) => [c, skills.filter((s) => s.category === c).length]));
  const usedCats = CATEGORIES.filter((c) => counts[c]);
  const demo = skills.find((s) => s.name === 'design-first') || skills[0];

  main.innerHTML = `<div class="wrap">
    <section class="hero">
      <div>
        <p class="eyebrow">${esc(t('hero.eyebrow'))}</p>
        <h1>${t('hero.title')}</h1>
        <p class="lede">${esc(t('hero.lede'))}</p>
        <label class="search">
          ${ICON.search}
          <input id="q" type="search" value="${esc(state.q)}" placeholder="${esc(t('search.placeholder'))}" aria-label="${esc(t('search.label'))}" autocomplete="off" spellcheck="false">
          <kbd>/</kbd>
        </label>
        <dl class="stats">
          <div><dt>${skills.length}</dt><dd>${esc(t('stats.skills'))}</dd></div>
          <div><dt>${authors}</dt><dd>${esc(t('stats.authors'))}</dd></div>
          <div><dt>${usedCats.length}</dt><dd>${esc(t('stats.categories'))}</dd></div>
        </dl>
      </div>
      <a class="appmock" href="#/about" aria-label="${esc(t('about.app.t'))}">
        <div class="appmock-bar"><span class="keycap keycap-sm" aria-hidden="true">/</span> Prompt</div>
        <div class="appmock-tabs"><span>${esc(t('demo.tabLocal'))}</span><span class="on">${esc(t('demo.tabMarket'))}</span></div>
        ${[demo, ...skills.filter((s) => s !== demo)].slice(0, 3).map((s, i) => `<div class="appmock-row">
          <div><b>/${esc(s.name)}</b><small>${esc(t('cat.' + s.category))}${i === 0 ? ` · <em>✓ ${esc(t('demo.ok'))}</em>` : ''}</small></div>
          <span class="appmock-btns"><span class="ghost">${esc(t('detail.copyPrompt'))}</span>${i === 0 ? '' : `<span class="solid">${esc(t('demo.install'))}</span>`}</span>
        </div>`).join('')}
      </a>
    </section>

    <section id="browse" aria-label="${esc(t('nav.discover'))}">
      <div class="toolbar">
        <div class="chips" role="group">
          <button type="button" class="chip" data-cat="all">${esc(t('browse.all'))} <b>${skills.length}</b></button>
          ${usedCats.map((c) => `<button type="button" class="chip" data-cat="${c}">${esc(t('cat.' + c))} <b>${counts[c]}</b></button>`).join('')}
        </div>
        <label class="sort safe-toggle"><input type="checkbox" id="safe" ${state.safeOnly ? 'checked' : ''}> ${esc(t('browse.safe'))}</label>
        <label class="sort">${esc(t('browse.sort'))}
          <select class="select" id="sort">
            ${['relevance', 'updated', 'name', 'saved'].map((k) => `<option value="${k}" ${state.sort === k ? 'selected' : ''}>${esc(t('sort.' + k))}</option>`).join('')}
          </select>
        </label>
      </div>
      <p class="result-count" id="count"></p>
      <div id="grid"></div>
    </section>

    <section class="how">
      <h2 class="section-title">${esc(t('how.title'))}</h2>
      <ol class="steps">
        ${[1, 2, 3].map((i) => `<li><h3>${esc(t(`how.${i}.t`))}</h3><p>${t(`how.${i}.d`)}</p></li>`).join('')}
      </ol>
    </section>
  </div>`;

  renderGrid();
  const input = $('#q');
  input.addEventListener('input', () => { state.q = input.value; renderGrid(); });
  $('#sort').addEventListener('change', (e) => { state.sort = e.target.value; renderGrid(); });
  $('#safe').addEventListener('change', (e) => { state.safeOnly = e.target.checked; renderGrid(); });
  $$('.chip').forEach((c) => c.addEventListener('click', () => { state.cat = c.dataset.cat; renderGrid(); }));
  if (state.q) input.focus();
}

// ── Detail ─────────────────────────────────────────────────
function modeBody(s) {
  const mode = state.mode;
  if (mode === 'prompt') {
    const text = cachedText.get(s.name);
    const preview = text ? buildPrompt([{ name: s.name, text }], state.task) : '…';
    return `<p class="help">${esc(t('detail.prompt.help'))}</p>
      <label class="field" style="margin-bottom:12px"><span>${esc(t('detail.prompt.task'))}</span>
        <input class="input" id="task" value="${esc(state.task)}" placeholder="${esc(t('detail.prompt.taskPh'))}" autocomplete="off">
      </label>
      <div class="codebox"><pre id="prompt-preview">${esc(preview.length > 700 ? preview.slice(0, 700) + '\n…' : preview)}</pre></div>
      <button type="button" class="btn btn-primary btn-block" style="margin-top:12px" data-action="copy-prompt" data-name="${esc(s.name)}">${esc(t('detail.copyPrompt'))}</button>`;
  }
  if (mode === 'app') {
    return `<p class="help">${t('detail.app.help', { n: esc(s.name) })}</p>
      <a class="btn btn-block" href="#/about">${esc(t('detail.app.get'))}</a>`;
  }
  const cmd = mode === 'win' ? cmdWindows([s]) : cmdUnix([s]);
  const shell = { win: 'PowerShell', unix: 'bash / zsh' }[mode];
  return `<p class="help">${esc(t(`detail.${mode}.help`))}</p>
    ${codebox(cmd, shell)}
    <p class="tip">${esc(t('detail.restart'))}</p>`;
}

function codebox(text, label) {
  return `<div class="codebox"><div class="codebox-head"><span>${esc(label)}</span><button type="button" class="btn" data-copy="${esc(text)}">${esc(t('detail.copy'))}</button></div><pre>${esc(text)}</pre></div>`;
}

function renderModeBody(s) {
  $$('.seg button').forEach((b) => b.setAttribute('aria-selected', b.dataset.mode === state.mode));
  $('#mode-body').innerHTML = modeBody(s);
  const task = $('#task');
  if (task) task.addEventListener('input', () => {
    state.task = task.value;
    const text = cachedText.get(s.name);
    if (text) {
      const p = buildPrompt([{ name: s.name, text }], state.task);
      $('#prompt-preview').textContent = p.length > 700 ? p.slice(0, 700) + '\n…' : p;
    }
  });
}

function safetyHtml(s) {
  const { hits, hosts } = s.safety;
  let html = hits.length
    ? `<p class="small-desc">${esc(t('detail.safetyIntro'))}</p><ul class="safety-list">${hits.map((h) => `<li><b>${esc(t('safety.' + h.id))}</b>${esc(t('detail.line', { n: h.line }))}<code>${esc(h.excerpt)}</code></li>`).join('')}</ul>`
    : `<p class="ok-line"><span class="ic ic-ok" style="width:20px;height:20px;border-radius:50%;display:grid;place-items:center">✓</span>${esc(t('detail.safe'))}</p>`;
  if (hosts.length) html += `<dl class="kv" style="margin-top:16px"><dt>${esc(t('detail.hosts'))}</dt><dd>${hosts.map(esc).join(', ')}</dd></dl>`;
  return html;
}

async function viewDetail(name) {
  const s = findSkill(name);
  if (!s) {
    main.innerHTML = `<div class="wrap"><a class="back" href="#/">${ICON.back}${esc(t('detail.back'))}</a>
      <div class="empty"><h2>${esc(t('detail.notFound'))}</h2><a class="btn btn-primary" href="#/">${esc(t('detail.back'))}</a></div></div>`;
    return;
  }
  document.title = `/${s.name} · Prompt`;
  const gh = hasRepo() ? `${repoUrl()}/blob/${state.config.branch}/skills/${s.name}/SKILL.md` : null;
  const edit = hasRepo() ? `${repoUrl()}/edit/${state.config.branch}/skills/${s.name}/SKILL.md` : null;
  const report = hasRepo() ? `${repoUrl()}/issues/new?template=skill-report.yml&title=${encodeURIComponent(`[${s.name}] `)}` : null;
  const modes = [['prompt', 'detail.m.prompt'], ['app', 'detail.m.app'], ['win', 'detail.m.win'], ['unix', 'detail.m.unix']];

  main.innerHTML = `<div class="wrap">
    <a class="back" href="#/">${ICON.back}${esc(t('detail.back'))}</a>
    <header class="detail-head">
      <span class="cat">${esc(t('cat.' + s.category))}</span>
      <h1><span class="slash">/</span>${esc(s.name)}</h1>
      <p class="summary">${esc(blurb(s))}</p>
      <ul class="meta-row">
        <li>${esc(t('card.by', { a: '' }))}<b>${esc(s.author)}</b></li>
        <li>${esc(t('detail.version'))} <b>${esc(s.version)}</b></li>
        <li>${esc(t('card.updated', { d: ago(s.updated) }))}</li>
        <li>${esc(t('detail.words', { n: s.words.toLocaleString(getLang()) }))}</li>
        <li>${esc(t('detail.license'))} <b>${esc(s.license)}</b></li>
      </ul>
    </header>
    <div class="detail-grid">
      <article>
        <div class="tabs" role="tablist">
          <button type="button" class="tab" role="tab" data-doc="doc">${esc(t('detail.tab.doc'))}</button>
          <button type="button" class="tab" role="tab" data-doc="source">${esc(t('detail.tab.source'))}</button>
        </div>
        <div id="doc"><div class="skeleton"></div></div>
      </article>
      <aside class="panel">
        <section class="box">
          <h2>${esc(t('detail.activate'))}</h2>
          <div class="seg" role="tablist">${modes.map(([m, k]) => `<button type="button" role="tab" data-mode="${m}">${esc(t(k))}</button>`).join('')}</div>
          <div id="mode-body"></div>
          <div class="row" style="margin-top:12px">
            <button type="button" class="btn" data-long="1" data-toggle-save="${esc(s.name)}"></button>
            <button type="button" class="btn" data-action="zip" data-name="${esc(s.name)}">${esc(t('detail.downloadZip'))}</button>
          </div>
        </section>
        <section class="box">
          <h2>${esc(t('detail.safety'))}</h2>
          ${safetyHtml(s)}
        </section>
        <section class="box">
          <h2>${esc(t('detail.when'))}</h2>
          <p class="small-desc">${esc(s.description)}</p>
          ${s.tags.length ? `<div class="tags" style="margin-top:16px">${s.tags.map((x) => `<a class="tag" href="#/?q=${encodeURIComponent(x)}">#${esc(x)}</a>`).join('')}</div>` : ''}
          <dl class="kv" style="margin-top:16px"><dt>${esc(t('detail.files'))}</dt><dd class="mono">${s.files.map(esc).join('<br>')}</dd></dl>
        </section>
        ${gh ? `<nav class="box links">
          <a href="${esc(gh)}" target="_blank" rel="noopener">${esc(t('detail.github'))} ${ICON.arrow}</a>
          <a href="${esc(edit)}" target="_blank" rel="noopener">${esc(t('detail.edit'))} ${ICON.arrow}</a>
          <a href="${esc(report)}" target="_blank" rel="noopener">${esc(t('detail.report'))} ${ICON.arrow}</a>
        </nav>` : ''}
      </aside>
    </div>
  </div>`;

  $$('[data-toggle-save]').forEach(paintSaveButton);
  $$('.seg button').forEach((b) => b.addEventListener('click', () => {
    state.mode = b.dataset.mode;
    store.set('mode', state.mode);
    renderModeBody(s);
  }));
  renderModeBody(s);

  const paintDoc = (text) => {
    $$('.tab').forEach((b) => b.setAttribute('aria-selected', b.dataset.doc === state.docTab));
    $('#doc').innerHTML = state.docTab === 'doc'
      ? `<div class="prose">${renderMarkdown(parseFrontmatter(text).body)}</div>`
      : `<pre class="source">${esc(text)}</pre>`;
  };
  try {
    const text = await getSource(s.name);
    cachedText.set(s.name, text);
    if (!main.contains($('#doc'))) return;
    paintDoc(text);
    $$('.tab').forEach((b) => b.addEventListener('click', () => { state.docTab = b.dataset.doc; paintDoc(text); }));
    if (state.mode === 'prompt') renderModeBody(s);
  } catch {
    $('#doc').innerHTML = `<div class="empty"><p>${esc(t('toast.loadFail'))}</p></div>`;
  }
}

// ── My skills ──────────────────────────────────────────────
function viewMine() {
  document.title = `${t('mine.title')} · Prompt`;
  const names = Object.keys(state.mine).sort((a, b) => state.mine[a].added.localeCompare(state.mine[b].added));
  const head = `<header class="page-head"><h1>${esc(t('mine.title'))}</h1><p>${esc(t('mine.lede'))}</p></header>`;
  const importBtn = `<label class="btn btn-ghost btn-sm">${esc(t('mine.import'))}<input type="file" accept=".json,application/json" id="import-list" hidden></label>`;

  if (!names.length) {
    main.innerHTML = `<div class="wrap">${head}<div class="empty"><h2>${esc(t('mine.empty'))}</h2><p></p>
      <div class="row" style="justify-content:center"><a class="btn btn-primary" href="#/" style="flex:none">${esc(t('mine.emptyCta'))}</a>${importBtn}</div></div></div>`;
    bindImport();
    return;
  }

  const active = names.filter((n) => state.mine[n].active && findSkill(n)).map(findSkill);
  main.innerHTML = `<div class="wrap">${head}
    <div class="mine-layout">
      <ul class="mine-list">
        ${names.map((n) => {
          const s = findSkill(n);
          const on = state.mine[n].active;
          return `<li class="mine-item ${on ? '' : 'is-off'}">
            <label class="switch" title="${esc(on ? t('mine.active') : t('mine.inactive'))}">
              <input type="checkbox" data-active="${esc(n)}" ${on ? 'checked' : ''} ${s ? '' : 'disabled'} aria-label="/${esc(n)}"><span></span>
            </label>
            <div class="mine-main">
              <a href="#/skill/${encodeURIComponent(n)}"><span style="color:var(--accent)">/</span>${esc(n)}</a>
              ${s ? `<p>${esc(blurb(s))}</p>` : `<p class="missing">${esc(t('mine.missing'))}</p>`}
            </div>
            <div class="mine-actions">
              ${s ? `<button type="button" class="btn btn-ghost btn-sm" data-action="copy-prompt" data-name="${esc(n)}">${esc(t('detail.copyPrompt'))}</button>` : ''}
              <button type="button" class="btn btn-ghost btn-sm" data-remove="${esc(n)}" aria-label="${esc(t('mine.remove'))} /${esc(n)}">✕</button>
            </div>
          </li>`;
        }).join('')}
      </ul>
      <aside class="panel">
        <section class="box">
          <h2>${esc(t('mine.selected', { n: active.length, t: names.length }))}</h2>
          <label class="field" style="margin-bottom:12px"><span>${esc(t('detail.prompt.task'))}</span>
            <input class="input" id="task" value="${esc(state.task)}" placeholder="${esc(t('detail.prompt.taskPh'))}" autocomplete="off">
          </label>
          <div class="stack">
            <button type="button" class="btn btn-primary" data-action="copy-active" ${active.length ? '' : 'disabled'}>${esc(t('mine.bulk.prompt'))}</button>
            <button type="button" class="btn" data-copy-cmd="win" ${active.length ? '' : 'disabled'}>${esc(t('mine.bulk.win'))}</button>
            <button type="button" class="btn" data-copy-cmd="unix" ${active.length ? '' : 'disabled'}>${esc(t('mine.bulk.unix'))}</button>
            <button type="button" class="btn" data-action="zip-active" ${active.length ? '' : 'disabled'}>${esc(t('mine.bulk.zip'))}</button>
          </div>
          <p class="tip">${esc(t('mine.zipHelp', { p: '~/.claude/skills' }))} ${esc(t('detail.restart'))}</p>
          <div class="row" style="margin-top:16px">
            <button type="button" class="btn btn-ghost btn-sm" data-action="export-list">${esc(t('mine.export'))}</button>
            ${importBtn}
          </div>
        </section>
      </aside>
    </div>
  </div>`;

  prefetch(names.filter(findSkill));
  $('#task').addEventListener('input', (e) => { state.task = e.target.value; });
  $$('[data-active]').forEach((cb) => cb.addEventListener('change', () => {
    state.mine[cb.dataset.active].active = cb.checked;
    saveMine();
    viewMine();
  }));
  $$('[data-remove]').forEach((b) => b.addEventListener('click', () => {
    delete state.mine[b.dataset.remove];
    saveMine();
    toast(t('toast.removed', { n: '/' + b.dataset.remove }));
    viewMine();
  }));
  $$('[data-copy-cmd]').forEach((b) => b.addEventListener('click', () => copy((b.dataset.copyCmd === 'win' ? cmdWindows : cmdUnix)(active))));
  bindImport();
}

function bindImport() {
  const input = $('#import-list');
  if (!input) return;
  input.addEventListener('change', async () => {
    try {
      const data = JSON.parse(await input.files[0].text());
      const list = Array.isArray(data) ? data : data.skills;
      let n = 0;
      for (const name of list) if (NAME_RE.test(name) && !state.mine[name]) { state.mine[name] = { active: true, added: new Date().toISOString() }; n++; }
      saveMine();
      toast(t('toast.imported', { n }));
      viewMine();
    } catch {
      toast(t('pub.importFail'));
    }
  });
}

// ── Publish ────────────────────────────────────────────────
const EMPTY_DRAFT = { name: '', description: '', category: 'code', tags: '', author: '', version: '1.0.0', license: 'MIT', body: '' };
let draft = { ...EMPTY_DRAFT, ...store.get('draft', {}) };
let pubTab = 'preview';

const slugify = (s) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 64);

function draftMd() {
  return buildSkillMd({
    name: draft.name,
    description: draft.description,
    body: draft.body,
    license: draft.license,
    metadata: { author: draft.author, category: draft.category, tags: draft.tags.split(',').map((x) => x.trim()).filter(Boolean).slice(0, 8), version: draft.version },
  });
}

function checksHtml() {
  const md = draftMd();
  const parsed = parseFrontmatter(md);
  const { errors, warnings } = validateSkill(parsed);
  const has = (list, prefix) => list.some((m) => m.key.startsWith(prefix));
  const items = [
    ...errors.map((m) => ['bad', '✕', t(m.key, m)]),
    ...warnings.map((m) => ['warn', '!', t(m.key, m)]),
  ];
  if (!has(errors, 'v.name')) items.push(['ok', '✓', t('v.ok.name')]);
  if (!has(errors, 'v.desc') && !has(warnings, 'v.desc')) items.push(['ok', '✓', t('v.ok.desc')]);
  if (!has(errors, 'v.body') && !has(warnings, 'v.body')) items.push(['ok', '✓', t('v.ok.body')]);
  const scan = safetyScan(md);
  if (scan.hits.length) items.push(['warn', '!', t('pub.safetyNote', { n: scan.hits.length })]);
  return { html: `<ul class="checks">${items.map(([k, ic, msg]) => `<li><span class="ic ic-${k}">${ic}</span><span>${esc(msg)}</span></li>`).join('')}</ul>`, ok: !errors.length, md };
}

function githubNewUrl(md) {
  return `${repoUrl()}/new/${encodeURIComponent(state.config.branch)}?filename=${encodeURIComponent(`skills/${draft.name}/SKILL.md`)}&value=${encodeURIComponent(md)}`;
}

function renderPubSide() {
  const { html, ok, md } = checksHtml();
  $('#checks').innerHTML = html;
  $('#pub-preview').innerHTML = pubTab === 'preview'
    ? `<div class="prose">${draft.body.trim() ? renderMarkdown(draft.body) : `<p style="color:var(--muted)">${esc(t('pub.bodyHelp'))}</p>`}</div>`
    : `<pre class="source" style="max-height:none">${esc(md)}</pre>`;
  $$('[data-pubtab]').forEach((b) => b.setAttribute('aria-selected', b.dataset.pubtab === pubTab));
  $('#name-help').textContent = t('pub.nameHelp', { n: draft.name || '…' });
  const counter = $('#desc-count');
  counter.textContent = `${draft.description.length} / ${MAX_DESCRIPTION}`;
  counter.classList.toggle('is-bad', draft.description.length > MAX_DESCRIPTION);

  const url = githubNewUrl(md);
  const gh = $('#to-github');
  const note = $('#pub-note');
  let blocked = !ok;
  if (!hasRepo()) { note.innerHTML = esc(t('pub.noRepo')); blocked = true; }
  else if (url.length > 7800) { note.innerHTML = esc(t('pub.tooLong')); blocked = true; }
  else note.innerHTML = t('pub.steps');
  gh.href = blocked ? '#/publish' : url;
  gh.setAttribute('aria-disabled', blocked);
  $$('[data-needs-valid]').forEach((b) => { b.disabled = !ok; });
}

let saveTimer;
function onDraftChange() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { store.set('draft', draft); $('#saved-hint')?.removeAttribute('hidden'); }, 300);
  renderPubSide();
}

function importSkillText(text, filename) {
  const parsed = parseFrontmatter(text);
  const meta = skillMeta(parsed.data);
  draft = {
    name: typeof parsed.data.name === 'string' ? parsed.data.name : slugify(filename.replace(/\.md$/i, '')),
    description: typeof parsed.data.description === 'string' ? parsed.data.description : '',
    category: meta.category,
    tags: meta.tags.join(', '),
    author: meta.author === 'anonymous' ? '' : meta.author,
    version: meta.version,
    license: meta.license,
    body: parsed.body.trim(),
  };
  store.set('draft', draft);
  viewPublish();
  toast(t('pub.imported', { f: filename }));
}

function viewPublish() {
  document.title = `${t('pub.title')} · Prompt`;
  const field = (key, label, input, help = '') => `<label class="field"><span>${esc(t(label))}</span>${input}${help ? `<small ${key ? `id="${key}"` : ''}>${help}</small>` : ''}</label>`;
  main.innerHTML = `<div class="wrap">
    <header class="page-head"><h1>${esc(t('pub.title'))}</h1><p>${esc(t('pub.lede'))}</p></header>
    <div class="pub-layout">
      <form class="form" id="pub-form" autocomplete="off" onsubmit="return false">
        <div class="dropzone" id="dropzone">
          <label class="btn btn-sm">${esc(t('pub.import'))}<input type="file" accept=".md,text/markdown,text/plain" id="import-md" hidden></label>
          <small>${esc(t('pub.drop'))}</small>
          <button type="button" class="btn btn-ghost btn-sm" id="reset" style="margin-left:auto">${esc(t('pub.reset'))}</button>
        </div>
        ${field('name-help', 'pub.name', `<input class="input mono" name="name" value="${esc(draft.name)}" maxlength="64" placeholder="mijn-skill" required>`, ' ')}
        <div class="field">
          ${field('', 'pub.desc', `<textarea class="textarea" name="description" rows="4">${esc(draft.description)}</textarea>`, esc(t('pub.descHelp')))}
          <span class="counter" id="desc-count"></span>
        </div>
        <div class="form-row">
          ${field('', 'pub.category', `<select class="select" name="category">${CATEGORIES.map((c) => `<option value="${c}" ${draft.category === c ? 'selected' : ''}>${esc(t('cat.' + c))}</option>`).join('')}</select>`)}
          ${field('', 'pub.tags', `<input class="input" name="tags" value="${esc(draft.tags)}" placeholder="ui, testing">`, esc(t('pub.tagsHelp')))}
        </div>
        <div class="form-row form-row-3">
          ${field('', 'pub.author', `<input class="input" name="author" value="${esc(draft.author)}" placeholder="octocat">`)}
          ${field('', 'pub.version', `<input class="input mono" name="version" value="${esc(draft.version)}">`)}
          ${field('', 'pub.license', `<input class="input" name="license" value="${esc(draft.license)}">`)}
        </div>
        ${field('', 'pub.body', `<textarea class="textarea mono" name="body" rows="18" placeholder="${esc(t('pub.bodyPh'))}">${esc(draft.body)}</textarea>`, esc(t('pub.bodyHelp')))}
        <span class="saved-hint" id="saved-hint" hidden>${esc(t('pub.saved'))}</span>
      </form>

      <aside class="panel">
        <section class="box">
          <h2>${esc(t('pub.checks'))}</h2>
          <div id="checks"></div>
        </section>
        <section class="box">
          <div class="stack">
            <a class="btn btn-primary" id="to-github" target="_blank" rel="noopener">${esc(t('pub.toGithub'))} ${ICON.arrow}</a>
            <p class="note" id="pub-note"></p>
            <div class="row">
              <button type="button" class="btn btn-sm" data-needs-valid data-action="pub-download">${esc(t('pub.download'))}</button>
              <button type="button" class="btn btn-sm" data-needs-valid data-action="pub-copy">${esc(t('pub.copyMd'))}</button>
              <button type="button" class="btn btn-sm" data-needs-valid data-action="pub-prompt">${esc(t('pub.tryPrompt'))}</button>
            </div>
          </div>
        </section>
        <section class="box">
          <div class="tabs" role="tablist" style="margin-bottom:16px">
            <button type="button" class="tab" role="tab" data-pubtab="preview">${esc(t('pub.preview'))}</button>
            <button type="button" class="tab" role="tab" data-pubtab="source">SKILL.md</button>
          </div>
          <div id="pub-preview" class="preview-box"></div>
        </section>
      </aside>
    </div>
  </div>`;

  const form = $('#pub-form');
  form.addEventListener('input', (e) => {
    if (!e.target.name) return;
    draft[e.target.name] = e.target.value;
    onDraftChange();
  });
  const nameInput = form.elements.namedItem('name');
  nameInput.addEventListener('blur', () => {
    const slug = slugify(nameInput.value);
    if (slug !== nameInput.value) { nameInput.value = slug; draft.name = slug; onDraftChange(); }
  });
  $$('[data-pubtab]').forEach((b) => b.addEventListener('click', () => { pubTab = b.dataset.pubtab; renderPubSide(); }));
  $('#reset').addEventListener('click', () => { draft = { ...EMPTY_DRAFT }; store.set('draft', draft); viewPublish(); });

  const readFile = async (file) => {
    if (!file) return;
    try {
      if (file.size > 300 * 1024) throw new Error('too big');
      importSkillText(await file.text(), file.name);
    } catch { toast(t('pub.importFail')); }
  };
  $('#import-md').addEventListener('change', (e) => readFile(e.target.files[0]));
  const dz = $('#dropzone');
  dz.addEventListener('dragover', (e) => { e.preventDefault(); dz.classList.add('is-over'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('is-over'));
  dz.addEventListener('drop', (e) => { e.preventDefault(); dz.classList.remove('is-over'); readFile(e.dataTransfer.files[0]); });

  renderPubSide();
}

// ── About ──────────────────────────────────────────────────
function viewAbout() {
  document.title = `${t('nav.about')} · Prompt`;
  main.innerHTML = `<div class="wrap">
    <header class="page-head"><h1>${esc(t('about.title'))}</h1><p>${esc(t('about.lede'))}</p></header>
    <div class="about">
      <section class="box wide" id="app">
        <h2>${esc(t('about.app.t'))}</h2>
        <p>${t('about.app.d')}</p>
        <ol class="app-steps">${[1, 2, 3].map((i) => `<li>${t(`about.app.${i}`)}</li>`).join('')}</ol>
        ${hasRepo() ? `<a class="btn btn-primary" href="${esc(repoUrl())}/archive/refs/heads/${esc(state.config.branch)}.zip" style="margin-top:16px">${esc(t('about.app.download'))}</a>` : ''}
      </section>
      ${['what', 'activate', 'publish', 'safety'].map((k) => `<section class="box"><h2>${esc(t(`about.${k}.t`))}</h2><p>${t(`about.${k}.d`)}</p></section>`).join('')}
      <section class="box wide">
        <div class="row">
          <a class="btn btn-ink" href="#/publish" style="flex:none">${esc(t('about.newSkill'))}</a>
          ${hasRepo() ? `<a class="btn" href="${esc(repoUrl())}/blob/${esc(state.config.branch)}/CONTRIBUTING.md" target="_blank" rel="noopener" style="flex:none">${esc(t('about.contribute'))} ${ICON.arrow}</a>` : ''}
        </div>
      </section>
    </div>
  </div>`;
}

// ── Global actions (event delegation) ──────────────────────
document.addEventListener('click', async (e) => {
  const saveBtn = e.target.closest('[data-toggle-save]');
  if (saveBtn) return toggleSaved(saveBtn.dataset.toggleSave);

  const copyBtn = e.target.closest('[data-copy]');
  if (copyBtn) return copy(copyBtn.dataset.copy);

  const gh = e.target.closest('#to-github[aria-disabled="true"]');
  if (gh) { e.preventDefault(); return; }

  const actionEl = e.target.closest('[data-action]');
  if (!actionEl) return;
  const { action, name } = actionEl.dataset;
  const activeSkills = () => Object.keys(state.mine).filter((n) => state.mine[n].active && findSkill(n)).map(findSkill);

  switch (action) {
    case 'copy-prompt': {
      const text = cachedText.get(name) ?? await getSource(name);
      return copy(buildPrompt([{ name, text }], state.task));
    }
    case 'copy-active': {
      const skills = activeSkills();
      const items = [];
      for (const s of skills) items.push({ name: s.name, text: cachedText.get(s.name) ?? await getSource(s.name) });
      return copy(buildPrompt(items, state.task));
    }
    case 'zip': return downloadZip([findSkill(name)]);
    case 'zip-active': return downloadZip(activeSkills());
    case 'export-list': {
      const data = JSON.stringify({ skills: Object.keys(state.mine) }, null, 2);
      return downloadBlob(new Blob([data], { type: 'application/json' }), 'mijn-skills.json');
    }
    case 'pub-download': return downloadBlob(new Blob([draftMd()], { type: 'text/markdown' }), 'SKILL.md');
    case 'pub-copy': return copy(draftMd());
    case 'pub-prompt': return copy(buildPrompt([{ name: draft.name, text: draftMd() }], ''));
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
  const tag = document.activeElement?.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || document.activeElement?.isContentEditable) return;
  e.preventDefault();
  if (!$('#q')) { location.hash = '#/'; setTimeout(() => $('#q')?.focus(), 0); } else $('#q').focus();
});

// ── Chrome: nav, language, theme ───────────────────────────
function applyStaticI18n() {
  $$('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $('#lang-btn').textContent = getLang() === 'nl' ? 'EN' : 'NL';
  $('#lang-btn').setAttribute('aria-label', t('top.lang'));
  $('#theme-btn').setAttribute('aria-label', t('top.theme'));
  document.documentElement.lang = getLang();
}

function effectiveTheme() {
  return document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}
function paintThemeIcon() { $('#theme-btn').innerHTML = effectiveTheme() === 'dark' ? ICON.sun : ICON.moon; }

$('#lang-btn').addEventListener('click', () => { setLang(getLang() === 'nl' ? 'en' : 'nl'); applyStaticI18n(); route(); });
$('#theme-btn').addEventListener('click', () => {
  const next = effectiveTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  store.set('theme', next);
  try { localStorage.setItem('prompt.theme', next); } catch { /* storage blocked */ }
  paintThemeIcon();
});

// ── Router ─────────────────────────────────────────────────
let lastView = '';
function route() {
  if (!state.index) return;
  const [path, query = ''] = (location.hash.slice(1) || '/').split('?');
  const parts = path.split('/').filter(Boolean);
  const view = ['skill', 'mine', 'publish', 'about'].includes(parts[0]) ? parts[0] : 'discover';
  $$('[data-nav]').forEach((a) => (a.dataset.nav === view ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  if (view !== 'skill') document.title = 'Prompt';
  if (view !== lastView || view === 'skill') window.scrollTo(0, 0);
  lastView = view;
  switch (view) {
    case 'skill': return viewDetail(decodeURIComponent(parts[1] || ''));
    case 'mine': return viewMine();
    case 'publish': return viewPublish();
    case 'about': return viewAbout();
    default: return viewDiscover(new URLSearchParams(query));
  }
}
window.addEventListener('hashchange', route);

async function boot() {
  applyStaticI18n();
  paintThemeIcon();
  saveMine();
  main.innerHTML = `<div class="wrap" style="padding-top:64px"><div class="grid">${'<div class="skeleton"></div>'.repeat(6)}</div></div>`;
  try {
    const [config, index] = await Promise.all([
      fetch('config.json').then((r) => (r.ok ? r.json() : {})).catch(() => ({})),
      fetch('data/index.json').then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch('data/synonyms.json').then((r) => (r.ok ? r.json() : {})).then(setSynonyms).catch(() => {}),
    ]);
    state.config = { ...state.config, ...config };
    state.index = index;
  } catch {
    main.innerHTML = `<div class="wrap"><div class="empty" style="margin-top:64px"><h2>${esc(t('toast.loadFail'))}</h2><p><code>npm run build</code></p></div></div>`;
    return;
  }
  if (hasRepo()) { $('#gh-link').href = repoUrl(); $('#footer-gh').href = repoUrl(); }
  route();
}

boot();
