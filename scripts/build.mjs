#!/usr/bin/env node
// Validates every skill in skills/ and builds the static site into dist/.
//   node scripts/build.mjs          build dist/
//   node scripts/build.mjs --check  validate only (used on pull requests)
import { readFile, writeFile, readdir, stat, mkdir, rm, cp } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  parseFrontmatter, validateSkill, safetyScan, wordCount, skillMeta,
  CATEGORIES, ALLOWED_EXTENSIONS, MAX_FILE_BYTES,
} from '../site/js/skill-core.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS = path.join(ROOT, 'skills');
const SITE = path.join(ROOT, 'site');
const DIST = path.join(ROOT, 'dist');
const checkOnly = process.argv.includes('--check');

const MESSAGES = {
  'v.noFrontmatter': 'SKILL.md must start with a --- frontmatter block',
  'v.nameMissing': 'frontmatter is missing "name"',
  'v.nameFormat': '"name" must be lowercase letters, digits and single hyphens',
  'v.nameLong': '"name" is longer than {n} characters',
  'v.nameFolder': '"name" must equal the folder name "{folder}"',
  'v.descMissing': 'frontmatter is missing "description"',
  'v.descLong': '"description" is longer than {n} characters',
  'v.descShort': '"description" is very short; say what it does and when to use it',
  'v.descWhen': '"description" should say when Claude should use the skill',
  'v.bodyEmpty': 'SKILL.md has no instructions after the frontmatter',
  'v.bodyShort': 'instructions are very short',
};
const fmt = (m) => MESSAGES[m.key].replace(/\{(\w+)\}/g, (_, k) => m[k]);

async function walk(dir, base = dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    // A link could point anywhere on the build machine and get published; skills are plain files only.
    if (entry.isSymbolicLink() || (!entry.isDirectory() && !entry.isFile())) {
      throw new Error(`${path.relative(SKILLS, full)}: links and special files are not allowed in a skill`);
    }
    if (entry.isDirectory()) out.push(...await walk(full, base));
    else out.push(path.relative(base, full).split(path.sep).join('/'));
  }
  return out;
}

function lastCommitDate(rel) {
  try {
    return execFileSync('git', ['log', '-1', '--format=%cI', '--', rel], { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() || null;
  } catch { return null; }
}

async function readConfig() {
  const cfg = JSON.parse(await readFile(path.join(ROOT, 'prompt.config.json'), 'utf8'));
  // In GitHub Actions the repository is known, so a fresh fork works without editing the config.
  if (process.env.GITHUB_REPOSITORY && (!cfg.repo || cfg.repo.startsWith('OWNER/'))) cfg.repo = process.env.GITHUB_REPOSITORY;
  return cfg;
}

async function main() {
  const config = await readConfig();
  const folders = (await readdir(SKILLS, { withFileTypes: true })).filter((d) => d.isDirectory()).map((d) => d.name).sort();
  const skills = [];
  let failed = 0;

  for (const folder of folders) {
    const dir = path.join(SKILLS, folder);
    const problems = [];
    const files = (await walk(dir)).sort();
    if (!files.includes('SKILL.md')) {
      console.error(`✗ ${folder}: SKILL.md not found`);
      failed++;
      continue;
    }
    for (const f of files) {
      // File paths end up inside shell install commands, so keep them boring.
      if (!/^[A-Za-z0-9._-]+(?:\/[A-Za-z0-9._-]+)*$/.test(f) || f.split('/').some((p) => p.startsWith('.'))) problems.push(`${f}: use only letters, digits, . _ - in file names (no hidden files)`);
      const ext = path.extname(f).toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) problems.push(`${f}: file type ${ext || '(none)'} is not allowed`);
      if ((await stat(path.join(dir, f))).size > MAX_FILE_BYTES) problems.push(`${f}: larger than ${MAX_FILE_BYTES / 1024} KB`);
    }

    const raw = await readFile(path.join(dir, 'SKILL.md'), 'utf8');
    const parsed = parseFrontmatter(raw);
    const { errors, warnings } = validateSkill(parsed, folder);
    problems.push(...errors.map(fmt));

    let json = {};
    if (files.includes('skill.json')) {
      try { json = JSON.parse(await readFile(path.join(dir, 'skill.json'), 'utf8')); }
      catch (e) { problems.push(`skill.json: ${e.message}`); }
    }
    const meta = skillMeta(parsed.data, json);
    if (meta.rawCategory && meta.category !== meta.rawCategory) problems.push(`unknown category "${meta.rawCategory}" (use one of ${CATEGORIES.join(', ')})`);

    if (problems.length) {
      failed++;
      console.error(`✗ ${folder}\n  - ${problems.join('\n  - ')}`);
      continue;
    }
    warnings.forEach((w) => console.warn(`! ${folder}: ${fmt(w)}`));

    let allText = raw;
    for (const f of files) if (f !== 'SKILL.md' && f !== 'skill.json') allText += '\n' + await readFile(path.join(dir, f), 'utf8');
    const scan = safetyScan(allText);
    const updated = lastCommitDate(`skills/${folder}`) ?? (await stat(path.join(dir, 'SKILL.md'))).mtime.toISOString();

    skills.push({
      name: parsed.data.name,
      description: parsed.data.description.trim(),
      author: meta.author,
      category: meta.category,
      tags: meta.tags,
      version: meta.version,
      license: meta.license,
      homepage: meta.homepage,
      summary_nl: meta.summaryNl,
      updated,
      words: wordCount(parsed.body),
      files: files.filter((f) => f !== 'skill.json'),
      safety: scan,
    });
    console.log(`✓ ${folder}${scan.hits.length ? `  (${scan.hits.length} safety note${scan.hits.length > 1 ? 's' : ''})` : ''}`);
  }

  if (failed) {
    console.error(`\n${failed} skill(s) failed validation.`);
    process.exit(1);
  }
  console.log(`\n${skills.length} skills valid.`);
  if (checkOnly) return;

  // The Prompt app ships this catalogue, so the marketplace works before (or without) a hosted site.
  await writeFile(path.join(ROOT, 'app', 'catalog-index.json'), JSON.stringify({ count: skills.length, skills }, null, 2) + '\n');

  await rm(DIST, { recursive: true, force: true });
  await cp(SITE, DIST, { recursive: true });
  await cp(SKILLS, path.join(DIST, 'skills'), { recursive: true });
  await mkdir(path.join(DIST, 'data'), { recursive: true });
  await writeFile(path.join(DIST, 'data', 'index.json'), JSON.stringify({ generated: new Date().toISOString(), count: skills.length, skills }, null, 2));
  await cp(path.join(ROOT, 'app', 'synonyms.json'), path.join(DIST, 'data', 'synonyms.json'));
  await writeFile(path.join(DIST, 'config.json'), JSON.stringify(config, null, 2));
  await writeFile(path.join(DIST, '.nojekyll'), '');
  console.log(`Built dist/ (${skills.length} skills).`);
}

main().catch((e) => { console.error(e); process.exit(1); });
