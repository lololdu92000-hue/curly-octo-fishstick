const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2});const p=await ctx.newPage();
await p.goto('file://'+__dirname+'/site.html');await p.evaluate(async()=>{await document.fonts.ready;});
const H=await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,30))}window.scrollTo(0,0);return document.body.scrollHeight});
console.log('page height',H);
const layers=await p.evaluate(()=>[...document.querySelectorAll('[data-layer]')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.layer,x:r.left,y:r.top+scrollY,w:r.width,h:r.height}}));
fs.writeFileSync('cap/layers.json',JSON.stringify({pageH:H,pad:28,layers},null,1));
await p.addStyleTag({content:'[data-layer]{visibility:hidden !important}'});
await p.screenshot({path:'cap/page.png',fullPage:true});
for(const L of layers){
 await p.evaluate(id=>{let s=document.getElementById('solo');if(!s){s=document.createElement('style');s.id='solo';document.head.appendChild(s)}
  s.textContent=`html,body{background:transparent!important} body *{visibility:hidden!important} [data-layer="${id}"],[data-layer="${id}"] *{visibility:visible!important}`},L.id);
 await p.screenshot({path:`cap/${L.id}.png`,omitBackground:true,fullPage:true,clip:{x:L.x-28,y:L.y-28,width:L.w+56,height:L.h+56}});
}
await b.close();console.log(layers.length,'layers')})();
