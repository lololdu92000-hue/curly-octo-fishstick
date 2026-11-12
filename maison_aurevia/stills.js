const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1440,height:1152}});p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(m.type()==='error'||m.type()==='warning')console.log('C',m.text().slice(0,300))});
await p.goto('http://127.0.0.1:8765/film.html');const t0=Date.now();await p.evaluate(()=>window.ready);console.log('init',Date.now()-t0,'ms');
const sub=+process.env.SUB||1;
for(const t of process.argv.slice(2).map(Number)){const s=Date.now();await p.evaluate(([t,s])=>seek(t,s),[t,sub]);
 const d=await p.evaluate(()=>document.getElementById('out').toDataURL('image/png'));fs.writeFileSync(`still_${t}.png`,Buffer.from(d.split(',')[1],'base64'));console.log(t,Date.now()-s,'ms')}
await b.close()})();
