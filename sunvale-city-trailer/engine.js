// ================= TRAILER ENGINE =================
const dayEnv = scene.environment;
const dayBg = (() => {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 1024; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 1024);
  gr.addColorStop(0, '#1f4f8f'); gr.addColorStop(0.2, '#3d6fb0'); gr.addColorStop(0.38, '#7da0cc'); gr.addColorStop(0.46, '#c9c6cc'); gr.addColorStop(0.495, '#f0cfa8'); gr.addColorStop(1, '#bfae96');
  g.fillStyle = gr; g.fillRect(0, 0, 2048, 1024);
  g.filter = 'blur(14px)';
  for (let i = 0; i < 120; i++) { const y = rr(150, 490); g.fillStyle = `rgba(255,${ri(235, 248)},${ri(225, 240)},${rr(0.15, 0.45) * (y / 490)})`; g.beginPath(); g.ellipse(rr(0, 2048), y, rr(60, 260) * (0.5 + y / 490), rr(8, 26) * (y / 490 + 0.3), 0, 0, 7); g.fill(); }
  g.filter = 'none';
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.mapping = THREE.EquirectangularReflectionMapping; return t;
})();
const hemi = scene.children.find(o => o.isHemisphereLight);
const nightBg = (() => {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 1024; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 1024);
  gr.addColorStop(0, '#03050c'); gr.addColorStop(0.3, '#070b18'); gr.addColorStop(0.44, '#141a30'); gr.addColorStop(0.49, '#3a2a3a'); gr.addColorStop(0.505, '#5a3a32'); gr.addColorStop(1, '#120e12');
  g.fillStyle = gr; g.fillRect(0, 0, 1920, 1080);
  for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(255,255,255,${rr(0.15, 0.7)})`; const r = rr(0.5, 1.3); g.beginPath(); g.arc(rr(0, 2048), rr(0, 420), r, 0, 7); g.fill(); }
  g.filter = 'blur(30px)';
  for (let i = 0; i < 25; i++) { g.fillStyle = `rgba(90,70,90,${rr(0.08, 0.2)})`; g.beginPath(); g.ellipse(rr(0, 2048), rr(200, 470), rr(150, 400), rr(15, 40), 0, 0, 7); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.mapping = THREE.EquirectangularReflectionMapping; return t;
})();
const nightEnv = window.__nightEnv;
const lampMat = IGEO.lamphead[1];
IGEO.pool[1].opacity = 0.35;
const facadeMats = new Set(), shopLike = new Set();
scene.traverse(o => { if (!o.isMesh) return; for (const m of [].concat(o.material)) { if (m.userData && m.userData.emNight) facadeMats.add(m); else if (m.userData && m.userData.ei) shopLike.add(m); } });

const composer = new EffectComposer(renderer);
composer.setPixelRatio(PR); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
if (Q.get('ao') !== '0') try {
  const ao = new GTAOPass(scene, camera, W, H);
  ao.updateGtaoMaterial({ radius: 3.5, distanceExponent: 1.5, thickness: 2, scale: 1.2, samples: 12 });
  ao.blendIntensity = 0.85; composer.addPass(ao);
} catch (e) { console.log('no ao', e.message); }
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.32, 0.5, 0.93);
composer.addPass(bloom);
composer.addPass(new OutputPass());

let MODE = null;
renderer.shadowMap.autoUpdate = false;
for (const m of movers) m.g.traverse(o => { o.castShadow = false; });
function setMode(m) {
  if (MODE === m) return; MODE = m; const N = m === 'night'; renderer.shadowMap.needsUpdate = true;
  for (const mt of facadeMats) { mt.emissiveMap = N ? mt.userData.emNight : mt.userData.emDay; mt.emissiveIntensity = N ? 0.95 : mt.userData.ei[0]; }
  for (const mt of shopLike) mt.emissiveIntensity = N ? 1.5 : mt.userData.ei[0];
  lampMat.emissiveIntensity = N ? 7 : 1.2;
  headMat.emissiveIntensity = N ? 6 : 1.2; tailMat.emissiveIntensity = N ? 4 : 1.0;
  sun.color.set(N ? 0x9db4ff : 0xffc48a); sun.intensity = N ? 0.55 : 5.2;
  hemi.intensity = N ? 0.10 : 0.42; hemi.color.set(N ? 0x5a6fa8 : 0xa9c2e6);
  scene.background = N ? nightBg : dayBg; scene.environment = N ? nightEnv : dayEnv;
  scene.fog.color.set(N ? 0x0e1220 : 0xdcc7b4); scene.fog.density = N ? 0.0007 : 0.00052;
  renderer.toneMappingExposure = N ? 0.85 : 0.78;
  bloom.strength = N ? 0.55 : 0.3; bloom.threshold = N ? 0.85 : 0.93; bloom.radius = N ? 0.35 : 0.5;
  IM.pool.visible = N; for (const b of nightOnly) b.visible = N;
  for (const k in IM) if (k.startsWith('lit_')) IM[k].material = N ? litMat : glassDayLit;
  glassMat.envMapIntensity = N ? 0.9 : 1.8;
}

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const ease = u => u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
const lin = (a, b, u) => a.clone().lerp(b, u);
const path = (p0, p1, l0, l1, e = ease) => u => { const k = e(u); return { p: lin(p0, p1, k), l: lin(l0, l1, k) }; };
const SH = {
  aerialN: path(V(70, 110, 240), V(38, 92, 165), V(0, 15, -150), V(0, 12, -170)),
  streetN: path(V(17.6, 2.7, 96), V(17.6, 2.9, 62), V(13, 3.2, 20), V(13, 3.3, -10), u => u),
  aveLowN: path(V(0.2, 2.8, 104), V(0.2, 3.1, 84), V(-1, 3.2, -200), V(1, 3.2, -200), u => u),
  barreN: path(V(42, 17, 32), V(104, 22, 32), V(52, 20, -16), V(114, 24, -16), u => u),
  towerD: u => { const a = 1.9 + 0.35 * ease(u); return { p: V(40 + 40 * Math.cos(a), 1.8 + u * 1.2, -215 + 40 * Math.sin(a)), l: V(40, 48, -215) }; },
  stadeD: path(V(-39, 2.6, 71), V(-44, 3.4, 67), V(-62, 1.4, 52), V(-63, 1.2, 50), u => u),
  topN: u => { const a = -0.9 + ease(u) * 0.6; return { p: V(40 + 95 * Math.cos(a), 55 - u * 8, -215 - 95 * Math.sin(a)), l: V(40, 30, -215) }; },
  droneD: path(V(3, 27, 128), V(3, 31, 72), V(-3, 13, -40), V(-3, 13, -110), u => u),
  revealN: path(V(0, 26, 60), V(0, 88, 235), V(0, 18, -120), V(0, 8, -230)),
  dateN: path(V(-150, 150, 40), V(-120, 140, 0), V(0, 0, -220), V(0, 0, -240), u => u),
  q1N: path(V(-14.5, 2.0, 40), V(-14.5, 2.2, 22), V(-11, 2.8, -40), V(-11, 2.8, -60), u => u),
  q2D: path(V(140, 6, 30), V(110, 8, 34), V(80, 30, -16), V(60, 32, -16), u => u),
  q3N: path(V(30, 40, 20), V(20, 46, 0), V(-60, 10, -150), V(-70, 10, -160), u => u),
  q4D: path(V(-6, 2, 30), V(-6, 2.4, 16), V(-30, 6, -10), V(-30, 6, -30), u => u),
  cityN2: path(V(-20, 30, 140), V(-5, 38, 110), V(20, 18, -60), V(10, 18, -90), u => u),
};
const BAR = 60 / 140 * 4;
const b = n => n * BAR;
// shots: [start, end, mode, shotName, fov]
const SHOTS = [
  [0, b(2), 'night', 'aerialN', 46],
  [b(2), b(4), 'night', 'streetN', 58],
  [b(4), b(5), 'night', 'aveLowN', 62],
  [b(5), b(6), 'night', 'barreN', 50],
  [b(6), b(7), 'day', 'towerD', 70],
  [b(7), b(8), 'day', 'stadeD', 54],
  [b(8), b(9), 'night', 'topN', 50],
  [b(9), b(10), 'day', 'droneD', 54],
  [b(10), b(10.5), 'night', 'q1N', 60],
  [b(10.5), b(11), 'day', 'q2D', 55],
  [b(11), b(11.5), 'night', 'q3N', 50],
  [b(11.5), b(12), 'day', 'q4D', 60],
  [b(12), b(14), 'night', 'revealN', 50],
  [b(14), b(15), 'night', 'cityN2', 50],
  [b(15), b(16), 'night', 'aveLowN', 62],
  [b(16), b(20.5), 'night', 'dateN', 42],
];
// hits (flash + shake)
const HITS = [b(4), b(5), b(6), b(7), b(8), b(9), b(10), b(10.5), b(11), b(11.5), b(12), b(14), b(16.25)];
// text cues: [t0, t1, html, style]
const CUES = [
  [0.35, b(1) + 0.1, '<div class="sub">UNE VILLE.</div>', 'fade'],
  [b(1) + 0.15, b(2) - 0.05, '<div class="mid">DES MILLIERS<br>D\'HISTOIRES.</div>', 'fade'],
  [b(2) + 0.3, b(3) + 0.2, '<div class="sub">TA PLACE T\'ATTEND</div>', 'fade'],
  [b(3) + 0.25, b(4) - 0.02, '<div class="mid">PRÉPARE-TOI.</div>', 'flicker'],
  [b(4), b(5), '<div class="big">BUSINESS</div>', 'punch'],
  [b(5), b(6), '<div class="big">GANGS</div>', 'punch'],
  [b(6), b(7), '<div class="big">POLICE</div>', 'punch'],
  [b(7), b(8), '<div class="big">QUARTIERS</div>', 'punch'],
  [b(8), b(9), '<div class="big">LIBERTÉ</div>', 'punch'],
  [b(9), b(10), '<div class="mid">TON BLOC.<br><span class="or">TES RÈGLES.</span></div>', 'punch'],
  [b(10), b(10.5), '<div class="mid">ÉCONOMIE</div>', 'punch'],
  [b(10.5), b(11), '<div class="mid">MÉTIERS</div>', 'punch'],
  [b(11), b(11.5), '<div class="mid">VÉHICULES</div>', 'punch'],
  [b(11.5), b(12), '<div class="mid">STAFF ACTIF</div>', 'punch'],
  [b(12) + 0.1, b(14), '<div class="big gl" data-t="SUNVALE CITY">SUNVALE CITY</div><div class="line" data-w="520"></div><div class="sub">R O L E P L A Y</div>', 'logo'],
  [b(14) + 0.1, b(15), '<div class="sub">UNE NOUVELLE ÈRE</div><div class="mid">VA COMMENCER</div>', 'fade'],
  [b(15) + 0.1, b(16), '<div class="sub">SORTIE LE</div>', 'flicker'],
  [b(16.25), b(19.6), '<div class="sub">SORTIE OFFICIELLE</div><div class="big gl" data-t="10.12.2026" style="font-size:230px">10.12.2026</div><div class="line" data-w="640"></div><div class="mid or" data-late="1" style="font-size:72px">ÇA VA ÊTRE LE FEU.</div>', 'date'],
  [b(19.6), b(20.5), '<div class="mid" style="font-size:80px">SUNVALE CITY RP</div><div class="sub">10 . 12 . 2026 — SOIS PRÊT</div>', 'fade'],
];
const DUR = b(20.5);
window.__dur = DUR;

const $ = id => document.getElementById(id);
const grainCanvas = (() => { const c = document.createElement('canvas'); c.width = c.height = 384; const g = c.getContext('2d'); const id = g.createImageData(384, 384); for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } g.putImageData(id, 0, 0); return c.toDataURL(); })();
$('grain').style.backgroundImage = `url(${grainCanvas})`;
let lastCue = -1;
function overlay(T) {
  // flash / shake
  let fl = 0, sh = 0;
  for (const h of HITS) { const d = T - h; if (d >= 0 && d < 0.5) { fl = Math.max(fl, Math.exp(-d * 14) * 0.9); sh = Math.max(sh, Math.exp(-d * 8)); } }
  $('flash').style.opacity = fl;
  const amp = sh * 16; const zoom = 1 + sh * 0.025;
  $('wrap').style.transform = `translate(${(Math.random() - 0.5) * amp}px,${(Math.random() - 0.5) * amp}px) scale(${zoom})`;
  $('grain').style.backgroundPosition = `${Math.floor(Math.random() * 384)}px ${Math.floor(Math.random() * 384)}px`;
  // black: intro fade-in, break before date, outro
  let bk = 0;
  if (T < 1.0) bk = 1 - T / 1.0;
  if (T > b(15) && T < b(16.25)) bk = Math.min(1, (T - b(15)) / 0.25) * 0.9;
  if (T > DUR - 0.9) bk = Math.min(1, (T - (DUR - 0.9)) / 0.8);
  $('black').style.opacity = bk;
  $('wrap').style.filter = (T > b(16.25) && T < b(19.6)) ? 'blur(5px) brightness(0.55) saturate(1.2)' : (T > b(19.6) ? 'blur(8px) brightness(0.4)' : 'none');
  // text
  const ci = CUES.findIndex(c => T >= c[0] && T < c[1]);
  const box = $('txt');
  if (ci !== lastCue) { box.innerHTML = ci >= 0 ? CUES[ci][2] : ''; lastCue = ci; }
  if (ci < 0) return;
  const [t0, t1, , st] = CUES[ci]; const d = T - t0, r = t1 - T, len = t1 - t0;
  let op = 1, sc = 1, ls = 0, blur = 0;
  if (st === 'fade') { op = Math.min(1, d / 0.35, r / 0.3); sc = 1 + 0.04 * (d / len); blur = Math.max(0, (1 - d / 0.35) * 8); }
  if (st === 'flicker') { op = (d < 0.25 ? (Math.random() < 0.5 ? 0.15 : 1) : 1) * Math.min(1, r / 0.1); sc = 1 + 0.06 * (d / len); }
  if (st === 'punch') { sc = 1 + 0.35 * Math.exp(-d * 18) + 0.05 * (d / len); op = Math.min(1, d / 0.04, r / 0.06); }
  if (st === 'logo' || st === 'date') { sc = 1 + 0.25 * Math.exp(-d * 10) + 0.03 * (d / len); op = Math.min(1, d / 0.06, r / 0.3); }
  box.style.opacity = op; box.style.transform = `scale(${sc})`; box.style.filter = blur ? `blur(${blur}px)` : 'none';
  box.querySelectorAll('.line').forEach(el => { el.style.width = Math.min(1, d / 0.6) * (+el.dataset.w) + 'px'; });
  box.querySelectorAll('[data-late]').forEach(el => { el.style.opacity = Math.min(1, Math.max(0, (d - 1.0) / 0.3)); el.style.transform = `translateY(${Math.max(0, 1 - (d - 1.0) / 0.3) * 20}px)`; });
  box.querySelectorAll('.gl').forEach(el => { const g = d < 0.45 || Math.random() < 0.06; el.style.setProperty('--go', g ? 0.85 : 0); el.style.setProperty('--gx', (g ? (Math.random() - 0.5) * 22 : 0) + 'px'); });
}

function updateMovers(T) {
  for (const m of movers) {
    const lo = m.axis === 'z' ? -1100 : -700, hi = m.axis === 'z' ? Z0 : 700, L = hi - lo;
    let v = m.base + m.dir * m.speed * T; v = ((v - lo) % L + L) % L + lo; m.g.position[m.axis] = v;
  }
}
window.renderAt = (T) => {
  const s = SHOTS.find(x => T >= x[0] && T < x[1]) || SHOTS[SHOTS.length - 1];
  setMode(s[2]);
  const u = Math.min(1, Math.max(0, (T - s[0]) / (s[1] - s[0])));
  const c = SH[s[3]](u);
  camera.fov = s[4]; camera.updateProjectionMatrix();
  camera.position.copy(c.p);
  if (c.top) camera.up.set(Math.sin(c.a), 0, -Math.cos(c.a)); else camera.up.set(0, 1, 0);
  camera.lookAt(c.l);
  updateMovers(T);
  composer.render(); window.__calls = renderer.info.render.calls;
  overlay(T);
};
window.__ready = true;
window.__done = true;
