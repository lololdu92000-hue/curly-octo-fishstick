s = open('v2.html').read()
def rep(a, b, cnt=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, cnt)

# ---------- imports + HDRI ----------
rep("import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';",
"""import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
import HDR_DAY from './pa/package/hdri/city.exr.js';
import HDR_NIGHT from './pa/package/hdri/night.exr.js';""")
rep("""  envScene.add(sky);
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(envScene).texture;""",
"""  envScene.add(sky);
  const pm = new THREE.PMREMGenerator(renderer);
  const exr = new EXRLoader();
  const dt = await exr.loadAsync(HDR_DAY); dt.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = pm.fromEquirectangular(dt).texture;
  const nt = await exr.loadAsync(HDR_NIGHT); nt.mapping = THREE.EquirectangularReflectionMapping;
  window.__nightEnv = pm.fromEquirectangular(nt).texture;""")

# ---------- wall-only textures with normal maps + 3D window system ----------
rep("// ---------- faubourg facade (3 bays x 3 floors) ----------", r"""// ---------- normal map from height ----------
function normalFromHeight(hc, strength = 2) {
  const w = hc.width, h = hc.height, src = hc.getContext('2d').getImageData(0, 0, w, h).data;
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const out = g.createImageData(w, h);
  const H = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = (H(x + 1, y) - H(x - 1, y)) * strength, dy = (H(x, y + 1) - H(x, y - 1)) * strength;
    const l = Math.hypot(dx, dy, 1), i = (y * w + x) * 4;
    out.data[i] = (-dx / l * 0.5 + 0.5) * 255; out.data[i + 1] = (dy / l * 0.5 + 0.5) * 255; out.data[i + 2] = (1 / l * 0.5 + 0.5) * 255; out.data[i + 3] = 255;
  }
  g.putImageData(out, 0, 0);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = MAXANI; return t;
}
function heightCanvas(S, draw) { const c = document.createElement('canvas'); c.width = c.height = S; const g = c.getContext('2d'); draw(g, S); return c; }
// HLM wall without windows (windows are real 3D)
const WIN_BOT = 0.6, WIN_H = 1.55, DOOR_H = 2.2;
function hlmWall(o) {
  const S = 1024, cw = S / 4, ch = S / 4;
  const map = tex(S, S, (g) => {
    g.fillStyle = o.wall; g.fillRect(0, 0, S, S); grain(g, S, S, 18);
    blotches(g, S, S, 40, 'rgba(60,50,40,0.06)', 40, 160);
    for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
      const x = c * cw, y = r * ch;
      if (o.accent && (o.accentAll || c % 2 === 0)) { g.fillStyle = o.accent; g.fillRect(x + 8, y + ch * 0.80, cw - 16, ch * 0.2 - 2); }
      const ww = cw * (o.wide ? 0.64 : 0.42), wb = (r + 1) * ch - ch * (WIN_BOT / FLR);
      const dg = g.createLinearGradient(0, wb, 0, wb + ch * 0.5); dg.addColorStop(0, 'rgba(40,35,28,0.28)'); dg.addColorStop(1, 'rgba(40,35,28,0)');
      g.fillStyle = dg; g.fillRect(x + (cw - ww) / 2 + 6, wb, ww - 12, ch * 0.5);
    }
    g.fillStyle = 'rgba(0,0,0,0.18)';
    for (let r = 0; r <= 4; r++) g.fillRect(0, r * ch - 2, S, 3);
    for (let c = 0; c <= 4; c++) g.fillRect(c * cw - 1, 0, 2, S);
  });
  const nm = normalFromHeight(heightCanvas(S, (g) => {
    g.fillStyle = '#888'; g.fillRect(0, 0, S, S);
    const id = g.getImageData(0, 0, S, S); for (let i = 0; i < id.data.length; i += 4) { const v = 136 + (rnd() - 0.5) * 36; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; } g.putImageData(id, 0, 0);
    g.filter = 'blur(1px)'; g.drawImage(g.canvas, 0, 0); g.filter = 'none';
    g.fillStyle = '#222'; for (let r = 0; r <= 4; r++) g.fillRect(0, r * ch - 3, S, 6); for (let c = 0; c <= 4; c++) g.fillRect(c * cw - 3, 0, 6, S);
  }), 3);
  return new THREE.MeshStandardMaterial({ map, normalMap: nm, normalScale: new THREE.Vector2(0.8, 0.8), roughness: 0.93, metalness: 0, envMapIntensity: 0.7, userData: { tw: BAY * 4, th: FLR * 4 } });
}
function plasterWall(wall) {
  const S = 768;
  const map = tex(S, S, (g) => { g.fillStyle = wall; g.fillRect(0, 0, S, S); grain(g, S, S, 24); blotches(g, S, S, 35, 'rgba(70,55,40,0.08)', 30, 140); blotches(g, S, S, 20, 'rgba(255,255,255,0.08)', 30, 100);
    for (let i = 0; i < 18; i++) { const x = rr(0, S); const dg = g.createLinearGradient(0, 0, 0, S); dg.addColorStop(0, 'rgba(50,40,30,0.12)'); dg.addColorStop(1, 'rgba(50,40,30,0)'); g.fillStyle = dg; g.fillRect(x, 0, rr(2, 8), rr(80, 300)); } });
  const nm = normalFromHeight(heightCanvas(S, (g) => { const id = g.createImageData(S, S); for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (rnd() - 0.5) * 60; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } g.putImageData(id, 0, 0); g.filter = 'blur(1.5px)'; g.drawImage(g.canvas, 0, 0); }), 4);
  return new THREE.MeshStandardMaterial({ map, normalMap: nm, normalScale: new THREE.Vector2(0.7, 0.7), roughness: 0.95, envMapIntensity: 0.6, userData: { tw: 9.6, th: 9 } });
}
// ---------- 3D window kits (instanced) ----------
const WREG = {};
const glassMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 0.55, roughness: 0.035, envMapIntensity: 1.8, clearcoat: 1, clearcoatRoughness: 0.02 });
const litMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 1.9, 1.35) });
const pvcMat = new THREE.MeshStandardMaterial({ color: 0xf3f2ee, roughness: 0.35, envMapIntensity: 0.9 });
const surMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, envMapIntensity: 0.6 });
const sillMat = new THREE.MeshStandardMaterial({ color: 0xdcd8cf, roughness: 0.7 });
const shutMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, envMapIntensity: 0.6, map: tex(64, 256, g => { g.fillStyle = '#ddd'; g.fillRect(0, 0, 64, 256); g.fillStyle = '#9a9a9a'; for (let y = 0; y < 256; y += 8) g.fillRect(0, y, 64, 2); }) });
const railTex = tex(256, 64, g => { g.fillStyle = '#000'; g.fillRect(0, 0, 256, 64); g.fillStyle = '#fff'; for (let x = 2; x < 256; x += 12) g.fillRect(x, 0, 3, 64); g.fillRect(0, 0, 256, 5); g.fillRect(0, 56, 256, 5); }, false);
const railMat = new THREE.MeshStandardMaterial({ color: 0x2a2c2e, metalness: 0.7, roughness: 0.4, alphaMap: railTex, alphaTest: 0.5, side: THREE.DoubleSide });
function mergeBoxes(list) { const gs = list.map(([w, h, d, x, y, z]) => { const b = new THREE.BoxGeometry(w, h, d); b.translate(x, y, z); return b; }); return mergeGeometries(gs); }
function winKit(name, ww, wh, deep = 0.24) {
  if (WREG['sur_' + name]) return name;
  const b = 0.13;
  WREG['sur_' + name] = [mergeBoxes([[ww + 2 * b, b, deep, 0, wh / 2 + b / 2, deep / 2], [ww + 2 * b, b * 0.6, deep, 0, -wh / 2 - b * 0.3, deep / 2], [b, wh, deep, -ww / 2 - b / 2, 0, deep / 2], [b, wh, deep, ww / 2 + b / 2, 0, deep / 2]]), surMat];
  const f = 0.06;
  WREG['pvc_' + name] = [mergeBoxes([[ww, f, 0.08, 0, wh / 2 - f / 2, 0.06], [ww, f, 0.08, 0, -wh / 2 + f / 2, 0.06], [f, wh, 0.08, -ww / 2 + f / 2, 0, 0.06], [f, wh, 0.08, ww / 2 - f / 2, 0, 0.06], [f * 0.9, wh, 0.07, 0, 0, 0.06]]), pvcMat];
  WREG['sill_' + name] = [mergeBoxes([[ww + 0.36, 0.06, 0.34, 0, -wh / 2 - 0.04, 0.17]]), sillMat];
  const gl = new THREE.PlaneGeometry(ww - 0.04, wh - 0.04); gl.translate(0, 0, 0.04);
  WREG['gl_' + name] = [gl, glassMat];
  WREG['lit_' + name] = [gl, glassDayLit];
  const sh = new THREE.BoxGeometry(ww - 0.02, 1, 0.05); sh.translate(0, -0.5, 0.075);
  WREG['sh_' + name] = [sh, shutMat];
  return name;
}
WREG.bwall = [new THREE.BoxGeometry(0.14, FLR - 0.2, 1.42), new THREE.MeshStandardMaterial({ color: 0xd2cdc3, roughness: 0.9 })];
WREG.rail = [(() => { const g = new THREE.PlaneGeometry(BAY * 0.92, 1.0); return g; })(), railMat];
WREG.hand = [new THREE.BoxGeometry(BAY * 0.94, 0.06, 0.08), new THREE.MeshStandardMaterial({ color: 0x3a3c3e, metalness: 0.7, roughness: 0.35 })];
WREG.pers = [new THREE.BoxGeometry(0.58, 1.95, 0.05), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7, map: shutMat.map })];
WREG.orail = [new THREE.PlaneGeometry(1.25, 0.9), railMat];
WREG.pot = [new THREE.IcosahedronGeometry(0.28, 1), new THREE.MeshStandardMaterial({ color: 0x4a7a3a, roughness: 0.9 })];
const LIT = ['#ffd9a0', '#ffe6c0', '#ffcf8a', '#d8e6ff', '#ffc070', '#fff0d8'];
const TINT = ['#2a3642', '#33404c', '#3e4650', '#4a4038', '#2f3a45', '#55504a', '#24303b'];
// place one window at face base point (wall surface, floor level), local x offset lx, center height cy
function putWindow(kit, base, rotY, lx, cy, wh, opt = {}) {
  addInst('sur_' + kit, placeLocal(base, rotY, lx, cy, 0), opt.sur || '#e8e4dc');
  addInst('pvc_' + kit, placeLocal(base, rotY, lx, cy, 0));
  if (!opt.noSill) addInst('sill_' + kit, placeLocal(base, rotY, lx, cy, 0));
  const lit = rnd() < 0.36;
  addInst((lit ? 'lit_' : 'gl_') + kit, placeLocal(base, rotY, lx, cy, 0), lit ? pick(LIT) : pick(TINT));
  if (opt.shutters !== false && rnd() < 0.45) addInst('sh_' + kit, placeLocal(base, rotY, lx, cy + wh / 2, 0, 1, wh * rr(0.1, 0.95), 1), pick(['#d8d3c8', '#c8c3b8', '#e6e2da', '#b5b0a5']));
}
// ---------- faubourg facade (3 bays x 3 floors) ----------""")

rep("import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';", "import { mergeVertices, mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';")

# near HLM materials
rep("const oldMats = [", "const hlmNear = hlmMats.map((m, i) => ({ mat: hlmWall({ wall: WALLS[i % WALLS.length], accent: ACC[i], accentAll: i % 3 === 0, wide: i % 2 === 0 }), acc: m.acc, wide: i % 2 === 0, sur: pick(['#e9e5dd', '#d9d3c8', '#f2efe8']) }));\nconst oldMats = [")
rep("const oldMats = ['#e9c9a1', '#d9b38c', '#f0e2c8', '#cf9f7a', '#e6d2b5', '#c9a58a', '#efd9b0', '#d7c4a8'].map(oldFacade);",
    "const OLDC = ['#e9c9a1', '#d9b38c', '#f0e2c8', '#cf9f7a', '#e6d2b5', '#c9a58a', '#efd9b0', '#d7c4a8'];\nconst oldMats = OLDC.map(oldFacade);\nconst oldNear = OLDC.map(plasterWall);")

# hlm: near uses wall + 3D windows
rep("  const set = opts.set ?? pick(hlmMats); const h = floors * FLR;", "  const set = opts.set ?? (opts.far ? pick(hlmMats) : pick(hlmNear)); const h = floors * FLR;")
old_balc = s[s.index("  // balconies on long faces\n  if (opts.balcony !== false && opts.far !== true) {"):s.index("function oldBuilding")]
rep(old_balc, r"""  // ---- real 3D facade: windows on every face that is a multiple of BAY, balconies on long faces ----
  if (!opts.far) {
    const alongX = w >= d;
    const pattern = opts.pattern ?? ri(0, 2);
    const railBars = rnd() < 0.45;
    const kitW = winKit(set.wide ? 'hw' : 'hn', set.wide ? 2.2 : 1.5, WIN_H), kitD = winKit('hd', 1.9, DOOR_H, 0.2);
    const faces = [[0, 1, w, d], [Math.PI, -1, w, d], [Math.PI / 2, 1, d, w], [-Math.PI / 2, -1, d, w]];
    faces.forEach(([rotY, side, len, other], fi) => {
      const isX = fi < 2; // faces normal to z
      const nb = Math.round(len / BAY); if (Math.abs(nb * BAY - len) > 0.3) return;
      const long = (isX === alongX);
      for (let bi = 0; bi < nb; bi++) {
        const t = -len / 2 + (bi + 0.5) * BAY;
        const balc = long && !(pattern === 1 && bi % 2) && !(pattern === 2 && bi % 3 === 1);
        for (let f = 0; f < floors; f++) {
          const fy = PL + f * FLR;
          // local x axis of face: (cos rotY, -sin rotY); for each face choose base so that local x spans the face
          const base = isX ? new THREE.Vector3(x, fy, z + side * d / 2) : new THREE.Vector3(x + side * w / 2, fy, z);
          const lx = (rotY === 0 || rotY === Math.PI / 2) ? t : -t;
          if (balc) {
            putWindow(kitD, base, rotY, lx, 0.15 + DOOR_H / 2, DOOR_H, { noSill: true, sur: set.sur });
            addInst('slab', placeLocal(base, rotY, lx, 0.05, 0.7));
            addInst('bwall', placeLocal(base, rotY, lx + BAY / 2 - 0.07, (FLR - 0.2) / 2 + 0.14, 0.71));
            if (railBars) { addInst('rail', placeLocal(base, rotY, lx, 0.65, 1.36)); addInst('hand', placeLocal(base, rotY, lx, 1.17, 1.36)); }
            else addInst('parapet', placeLocal(base, rotY, lx, 0.62, 1.35), rnd() < 0.88 ? set.acc : '#d9d6cf');
            if (rnd() < 0.16) addInst('dish', placeLocal(base, rotY + rr(-0.3, 0.3), lx + rr(-1.0, 1.0), 1.75, 1.2));
            if (rnd() < 0.08) addInst('laundry', placeLocal(base, rotY, lx + rr(-0.8, 0.8), 1.3, 0.95), pick(['#e63946', '#f1faee', '#457b9d', '#ffb703', '#8ecae6', '#2a9d8f']));
            if (rnd() < 0.12) addInst('pot', placeLocal(base, rotY, lx + rr(-1.2, 1.2), 1.25, 1.3, 1, 0.8, 1));
          } else {
            putWindow(kitW, base, rotY, lx, WIN_BOT + WIN_H / 2, WIN_H, { sur: set.sur });
          }
        }
      }
    });
    // entrance canopy
    const ef = alongX ? [x, z + d / 2 + 1.2, 5, 2.4] : [x + w / 2 + 1.2, z, 2.4, 5];
    const can = new THREE.Mesh(new THREE.BoxGeometry(ef[2], 0.25, ef[3]), concreteMat); can.position.set(ef[0], PL - 0.2, ef[1]); can.castShadow = true; scene.add(can);
  }
}
""")

# old buildings: near version with 3D windows (all calls are near except far loop)
rep("function oldBuilding(x, z, w, d, floors, shop = true) {\n  const m = pick(oldMats); const h = floors * 3.0;",
    "function oldBuilding(x, z, w, d, floors, shop = true, far = false) {\n  const mi = Math.floor(rnd() * OLDC.length); const m = far ? oldMats[mi] : oldNear[mi]; const h = floors * 3.0;")
rep("  // awnings toward avenue (face toward x=0)\n  if (shop) {",
r"""  if (!far) {
    const kit = winKit('old', 1.15, 1.95, 0.18); const pc = pick(['#5d7b6f', '#7a8b99', '#c9c2b0', '#8a5a44', '#4f6d8a', null]);
    const stone = pick(['#efe9dc', '#e4dccb', '#f4f0e6']);
    for (const [rotY, side] of [[Math.PI / 2, 1], [-Math.PI / 2, -1]]) {
      const nb = Math.max(1, Math.floor(d / 3.2)), len = nb * 3.2;
      for (let bi = 0; bi < nb; bi++) {
        const t = -len / 2 + (bi + 0.5) * 3.2; const lx = rotY === Math.PI / 2 ? t : -t;
        for (let f = 0; f < floors; f++) {
          const base = new THREE.Vector3(x + side * w / 2, 4 + f * 3.0, z);
          putWindow(kit, base, rotY, lx, 1.5, 1.95, { sur: stone, shutters: pc === null });
          if (pc) { for (const sx of [-1, 1]) addInst('pers', placeLocal(base, rotY, lx + sx * (1.15 / 2 + 0.42), 1.5, 0.07), pc); }
          if (f === 0 || rnd() < 0.5) addInst('orail', placeLocal(base, rotY, lx, 0.95, 0.2));
        }
      }
    }
    for (let f = 1; f < floors; f++) { const band = new THREE.Mesh(new THREE.BoxGeometry(w + 0.25, 0.16, d + 0.25), concreteMat); band.position.set(x, 4 + f * 3.0 - 0.05, z); band.receiveShadow = true; scene.add(band); }
    // dormers
    for (const side of [1, -1]) for (let k = -1; k <= 1; k++) { const dm = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.5, 1.2), zincMat); dm.position.set(x + side * (w / 2 - 1.6), 4 + h + 1.4, z + k * d / 3.2); dm.castShadow = true; scene.add(dm); const dg = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.9), glassMat); dg.position.set(x + side * (w / 2 - 1.6 + 0.61), 4 + h + 1.35, z + k * d / 3.2); dg.rotation.y = side * Math.PI / 2; scene.add(dg); }
  }
  // awnings toward avenue (face toward x=0)
  if (shop) {""")
# far old buildings
rep("else { oldBuilding(jx, jz, rr(14, 22), rr(14, 26), ri(3, 6), false);", "else { oldBuilding(jx, jz, rr(14, 22), rr(14, 26), ri(3, 6), false, true);")
rep("if (Math.abs(gx) < 75) { oldBuilding(Math.sign(gx) * 27, jz, 13, 40, ri(3, 6), true); continue; }", "if (Math.abs(gx) < 75) { oldBuilding(Math.sign(gx) * 27, jz, 13, 40, ri(3, 6), true, jz < -420); continue; }")

# instance build: use registry
rep("  const [geo, mat] = IGEO[k]; const arr = inst[k];", "  const [geo, mat] = IGEO[k] || WREG[k]; const arr = inst[k];")
rep("  im.castShadow = !['person', 'head', 'lamphead'].includes(k);", "  im.castShadow = !['person', 'head', 'lamphead'].includes(k) && !/^(gl_|lit_|pvc_)/.test(k);")

# denser, nicer trees
rep("  const n = ri(5, 8);\n  for (let k = 0; k < n; k++) { const a = rr(0, 6.28), r = rr(0.5, 2.4) * s; const sc = rr(1.6, 2.6) * s;",
    "  const n = ri(9, 13);\n  for (let k = 0; k < n; k++) { const a = rr(0, 6.28), r = rr(0.3, 2.6) * s; const sc = rr(1.2, 2.0) * s;")
rep("(rr(6.2, 8.5)) * s", "(rr(5.6, 9.2)) * s")
rep("camera.lookAt(-3, 13, -40);", "camera.lookAt(-3, 13, -40);\nif (Q.get('cam')) { const c = Q.get('cam').split(',').map(Number), l = Q.get('look').split(',').map(Number); camera.position.set(...c); camera.lookAt(...l); if (Q.get('fov')) { camera.fov = +Q.get('fov'); camera.updateProjectionMatrix(); } }")

rep("const litMat = new THREE.MeshBasicMaterial", "const glassDayLit = glassMat.clone(); glassDayLit.color.set(0x262b31);\nconst litMat = new THREE.MeshBasicMaterial")
rep("for (const s of [-1, 1]) sidewalk(s * (AVW / 2 + 3), (a + b) / 2, 6, a - b);", "for (const s of [-1, 1]) sidewalk(s * (AVW / 2 + 4.8), (a + b) / 2, 9.6, a - b);")
rep("if (rnd() < 0.5) tag(g, rr(40, 800), 230, 90, pick(['93', 'SVL', '93', 'BLOC', 'S.V']));", "if (rnd() < 0.3) tag(g, rr(40, 800), 230, rr(60, 90), pick(['93', 'SVL', 'S.V', 'ZONE', 'B.A']));")

open('v3.html', 'w').write(s)
print('ok')
