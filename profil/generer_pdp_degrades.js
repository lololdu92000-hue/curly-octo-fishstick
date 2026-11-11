const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/pp2.html');await p.evaluate(async()=>{await document.fonts.load('100px Anton');await document.fonts.load('800 40px InterX')});
for(const v of 'ABC'){const d=await p.evaluate(v=>draw(v),v);fs.writeFileSync(`pp2_${v}.png`,Buffer.from(d.split(',')[1],'base64'))}await b.close()})();
