s = open('v3.html').read()
def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# ---------- head: styles + overlay DOM ----------
head_old = s[s.index('<style>'):s.index('</style>') + 8]
rep(head_old, r'''<style>
@font-face{font-family:Anton;src:url(./node_modules/@fontsource/anton/files/anton-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:Bebas;src:url(./node_modules/@fontsource/bebas-neue/files/bebas-neue-latin-400-normal.woff2) format('woff2')}
html,body{margin:0;padding:0;overflow:hidden;background:#000;width:1920px;height:1080px}
canvas{display:block}
#stage{position:absolute;inset:0;overflow:hidden}
#wrap{position:absolute;inset:-40px;transform-origin:50% 50%}
#wrap canvas{position:absolute;left:40px;top:40px}
.ov{position:absolute;inset:0;pointer-events:none}
#vig{background:radial-gradient(ellipse at 50% 50%,transparent 50%,rgba(0,0,0,.6) 100%)}
#grade{background:linear-gradient(180deg,rgba(0,40,80,.10),rgba(255,120,40,.07));mix-blend-mode:soft-light}
#grain{opacity:.10;mix-blend-mode:overlay;background-size:384px 384px}
.bar{position:absolute;left:0;right:0;height:112px;background:#000;z-index:8}
#bt{top:0}#bb{bottom:0}
#flash{background:#fff;opacity:0;z-index:6}
#black{background:#000;opacity:0;z-index:4}
#txt{display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:7;text-align:center}
.big{font-family:Anton,sans-serif;font-size:190px;line-height:.95;color:#fff;letter-spacing:4px;text-transform:uppercase;text-shadow:0 8px 40px rgba(0,0,0,.6)}
.mid{font-family:Anton,sans-serif;font-size:96px;line-height:1;color:#fff;letter-spacing:3px;text-transform:uppercase;text-shadow:0 6px 30px rgba(0,0,0,.7)}
.sub{font-family:Bebas,sans-serif;font-size:46px;letter-spacing:16px;color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.9)}
.or{color:#ff8a1f}
.line{width:0;height:5px;background:#ff8a1f;margin:22px auto}
.gl{position:relative}
.gl::before,.gl::after{content:attr(data-t);position:absolute;left:0;top:0;width:100%;height:100%}
.gl::before{color:#ff2a4a;transform:translate(var(--gx,0),0);mix-blend-mode:screen;opacity:var(--go,0)}
.gl::after{color:#18e7ff;transform:translate(calc(var(--gx,0) * -1),0);mix-blend-mode:screen;opacity:var(--go,0)}
#corner{position:absolute;right:70px;bottom:132px;z-index:7;font-family:Bebas,sans-serif;font-size:30px;letter-spacing:8px;color:rgba(255,255,255,.75)}
</style>''')
rep('''<div id="grade"></div><div id="vig"></div>
<div id="logo"><div class="t">SUNVALE <span>LIFE</span></div><div class="s">ROLEPLAY · 93</div></div>''',
'''<div id="stage"><div id="wrap"></div>
<div id="grade" class="ov"></div><div id="vig" class="ov"></div><div id="grain" class="ov"></div>
<div id="black" class="ov"></div><div id="flash" class="ov"></div>
<div id="bt" class="bar"></div><div id="bb" class="bar"></div>
<div id="txt" class="ov"></div><div id="corner"></div></div>''')
rep("if (Q.get('logo') === '0') document.getElementById('logo').style.display = 'none';", "")
rep("document.body.prepend(renderer.domElement);", "document.getElementById('wrap').appendChild(renderer.domElement);")
rep("import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';", "import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';\nconst LANG = 0;")

# ---------- night emissive maps ----------
rep("const lit = rnd() < 0.06; wins.push([wx, wy, ww, wh, shut, lit]);",
    "const lit = rnd() < 0.06; const lit2 = lit || (shut < 0.75 && rnd() < 0.42); wins.push([wx, wy, ww, wh, shut, lit, lit2]);")
rep("""  return new THREE.MeshStandardMaterial({ map, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: 0.55, roughnessMap: rough, roughness: 1, metalness: 0, envMapIntensity: 0.55, userData: { tw: BAY * 4, th: FLR * 4 } });""",
"""  const em2 = tex(S, S, (g) => { g.fillStyle = '#000'; g.fillRect(0, 0, S, S); for (const [x, y, w, h, s, l, l2] of wins) if (l2) { g.fillStyle = pick(['#ffcf8a', '#ffe2b0', '#ffd39b', '#cfe0ff', '#ffb870', '#ffc98a']); g.fillRect(x + 3, y + h * s + 3, w - 6, h * (1 - s) - 6); } });
  return new THREE.MeshStandardMaterial({ map, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: 0.55, roughnessMap: rough, roughness: 1, metalness: 0, envMapIntensity: 0.55, userData: { tw: BAY * 4, th: FLR * 4, emDay: em, emNight: em2, ei: [0.55, 1.9] } });""")
rep("const sh = rnd(); wins.push([wx, wy, ww, wh, rnd() < 0.05]);", "const sh = rnd(); wins.push([wx, wy, ww, wh, rnd() < 0.05, rnd() < 0.45]);")
rep("""  return new THREE.MeshStandardMaterial({ map, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: 0.5, roughness: 0.92, envMapIntensity: 0.5, userData: { tw: 3.2 * 3, th: 3.0 * 3 } });""",
"""  const em2 = tex(S, S, (g) => { g.fillStyle = '#000'; g.fillRect(0, 0, S, S); for (const [x, y, w, h, l, l2] of wins) if (l || l2) { g.fillStyle = pick(['#ffd08f', '#ffc070', '#ffe0b0']); g.fillRect(x + 3, y + 3, w - 6, h - 6); } });
  return new THREE.MeshStandardMaterial({ map, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: 0.5, roughness: 0.92, envMapIntensity: 0.5, userData: { tw: 3.2 * 3, th: 3.0 * 3, emDay: em, emNight: em2, ei: [0.5, 1.8] } });""")
rep("emissive: 0xffffff, emissiveIntensity: 0.9, roughness: 0.6, envMapIntensity: 0.6, userData: { tw: 24, th: 4 } });",
    "emissive: 0xffffff, emissiveIntensity: 0.9, roughness: 0.6, envMapIntensity: 0.6, userData: { tw: 24, th: 4, ei: [0.9, 3.2] } });")

# ---------- cars: moving / parked ----------
rep("function car(x, z, rotY, type) {", "const headOff = new THREE.MeshStandardMaterial({ color: 0xd8d8d8, roughness: 0.2 }); const tailOff = new THREE.MeshStandardMaterial({ color: 0x5a0d0d, roughness: 0.3 });\nfunction car(x, z, rotY, type, moving = false) {")
rep("const h = new THREE.Mesh(lightGeo, headMat);", "const h = new THREE.Mesh(lightGeo, moving ? headMat : headOff);")
rep("const t = new THREE.Mesh(lightGeo, tailMat);", "const t = new THREE.Mesh(lightGeo, moving ? tailMat : tailOff);")
rep("  g.position.set(x, 0.03, z); g.rotation.y = rotY; scene.add(g);\n}", "  g.position.set(x, 0.03, z); g.rotation.y = rotY; scene.add(g); return g;\n}")
rep("for (let z = Z0; z > -1100; z -= rr(9, 26)) car(rnd() < 0.5 ? 2 : 6, z, Math.PI / 2 * -1 + Math.PI, null) ;",
    "for (let z = Z0; z > -1100; z -= rr(9, 26)) mover(car(rnd() < 0.5 ? 2 : 6, z, Math.PI / 2, null, true), 'z', -1);")
rep("for (let z = Z0; z > -1100; z -= rr(9, 26)) car(rnd() < 0.5 ? -2 : -6, z, Math.PI / 2 * -1, null);",
    "for (let z = Z0; z > -1100; z -= rr(9, 26)) mover(car(rnd() < 0.5 ? -2 : -6, z, -Math.PI / 2, null, true), 'z', 1);")
rep("car(x, cz + (rnd() < 0.5 ? 2.5 : -2.5), rnd() < 0.5 ? 0 : Math.PI); }",
    "const dd = rnd() < 0.5 ? 1 : -1; mover(car(x, cz + dd * 2.5, dd > 0 ? 0 : Math.PI, null, true), 'x', dd); }")
rep("// ================= STREET FURNITURE =================", r"""const poolTex = tex(256, 256, g => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.45)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); });
const beamGeo = new THREE.PlaneGeometry(14, 6); beamGeo.rotateX(-Math.PI / 2); 
const beamMat = new THREE.MeshBasicMaterial({ map: poolTex, color: 0xfff0d0, transparent: true, opacity: 0.3, blending: THREE.AdditiveBlending, depthWrite: false });
const movers = [], nightOnly = [];
function mover(g, axis, dir) {
  const b = new THREE.Mesh(beamGeo, beamMat); b.position.set(8, 0.08, 0); b.visible = false; g.add(b); nightOnly.push(b);
  movers.push({ g, axis, dir, base: g.position[axis], speed: rr(9, 15) });
}
// ================= STREET FURNITURE =================""")
rep("  addInst('lamphead', placeLocal(new THREE.Vector3(x + face * 2.3, 8.7, z), 0, 0, 0, 0));",
    "  addInst('lamphead', placeLocal(new THREE.Vector3(x + face * 2.3, 8.7, z), 0, 0, 0, 0));\n  addInst('pool', placeLocal(new THREE.Vector3(x + face * 2.3, 0.25, z), 0, 0, 0, 0));")
rep("  head: [new THREE.SphereGeometry(0.13, 8, 6), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 })],",
    "  head: [new THREE.SphereGeometry(0.13, 8, 6), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 })],\n  pool: [(() => { const g = new THREE.PlaneGeometry(13, 13); g.rotateX(-Math.PI / 2); return g; })(), new THREE.MeshBasicMaterial({ map: poolTex, color: 0xffa64d, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending, depthWrite: false })],")
rep("im.receiveShadow = true; scene.add(im);", "im.receiveShadow = k !== 'pool'; if (k === 'pool') im.castShadow = false; scene.add(im); IM[k] = im;")
rep("for (const k in inst) {", "const IM = {};\nfor (const k in inst) {")

# ---------- engine ----------
tail_old = s[s.index('// ================= RENDER ================='):s.index('</script></body></html>')]
rep(tail_old, open('engine.js').read())
open('trailer.html', 'w').write(s)
print('ok')
