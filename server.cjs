const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const root = __dirname;
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp' };
http.createServer((req, res) => {
  let name;
  try { name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); } catch { res.writeHead(400).end(); return; }
  const file = path.resolve(root, '.' + (name === '/' ? '/index.html' : name));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (err, bytes) => {
    if (err) { res.writeHead(404).end('Not found'); return; }
    const ext = path.extname(file);
    const headers = { 'Content-Type': mime[ext] || 'application/octet-stream', 'Cache-Control': 'no-cache', Vary: 'Accept-Encoding' };
    if (/\b(gzip)\b/.test(req.headers['accept-encoding'] || '') && ['.svg', '.css', '.js', '.html'].includes(ext)) {
      bytes = zlib.gzipSync(bytes); headers['Content-Encoding'] = 'gzip';
    }
    headers['Content-Length'] = bytes.length;
    res.writeHead(200, headers);
    res.end(req.method === 'HEAD' ? undefined : bytes);
  });
}).listen(process.env.PORT || 4173, '0.0.0.0', () => console.log('Health prototype listening on 4173'));
