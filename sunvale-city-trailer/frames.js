const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const [,, mode, a, b2, wid, extra] = process.argv; // mode: 'frames' start end worker | 'times' "t1,t2" 
const root = __dirname, port = 8800 + (+wid || 0);
const types = { '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.html': 'text/html' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(p, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); }).listen(port);
(async () => {
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (!/Driver|Canvas2D/.test(m.text())) console.log('console:', m.text()); });
  await p.goto(`http://localhost:${port}/trailer.html?pr=1${extra || ''}`);
  await p.waitForFunction(() => window.__ready, null, { timeout: 300000, polling: 500 });
  await p.evaluate(() => document.fonts.ready);
  const FPS = 24;
  let list = [];
  if (mode === 'times') list = a.split(',').map(Number).map(t => [t, `test_${t}.jpg`]);
  else { fs.mkdirSync('frames', { recursive: true }); for (let f = +a; f < +b2; f++) list.push([f / FPS, `frames/f${String(f).padStart(5, '0')}.jpg`]); }
  const t0 = Date.now();
  for (const [t, out] of list) {
    if (mode !== 'times' && fs.existsSync(out)) continue;
    await p.evaluate(t => window.renderAt(t), t);
    await p.screenshot({ path: out, type: 'jpeg', quality: 93 });
  }
  console.log('done', list.length, 'in', (Date.now() - t0) / 1000, 's');
  await br.close(); srv.close();
})();
