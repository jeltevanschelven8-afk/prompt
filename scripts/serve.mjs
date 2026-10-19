#!/usr/bin/env node
// Tiny static server for dist/ during development:  node scripts/serve.mjs [port]
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIST = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'dist');
const PORT = Number(process.argv[2] || process.env.PORT || 4321);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.md': 'text/markdown; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8',
};

createServer(async (req, res) => {
  try {
    let rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    let file = path.join(DIST, path.normalize(rel));
    if (!file.startsWith(DIST)) throw Object.assign(new Error('forbidden'), { code: 'EACCES' });
    if ((await stat(file).catch(() => null))?.isDirectory()) file = path.join(file, 'index.html');
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': TYPES[path.extname(file).toLowerCase()] || 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
    res.end(body);
  } catch (e) {
    res.writeHead(e.code === 'EACCES' ? 403 : 404, { 'content-type': 'text/plain' });
    res.end(e.code === 'EACCES' ? 'Forbidden' : 'Not found');
  }
}).listen(PORT, () => console.log(`Prompt dev server: http://localhost:${PORT}`));
