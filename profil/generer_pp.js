const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:540,height:960}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/reel2.html');await p.evaluate(()=>window.ready);
for(const v of ['A','B','C']){
 const d=await p.evaluate((v)=>{
  ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;
  const m=v==='C'?1.85:.85;
  sky(1.5,m,1180,330,v==='C'?null:560);skyline(1180,m);ground(1180,m);
  cluster(0,{m,hor:1180,camY:330,f:1250,camX:-20,mix:v==='C'?[['night',1]]:[['day',.2],['sunset',.8]]});
  if(v!=='C'){ctx.globalCompositeOperation='lighter';for(let i=0;i<7;i++){const a=-.6+i*.2;ctx.fillStyle='rgba(255,180,110,.05)';ctx.beginPath();ctx.moveTo(330,560);ctx.lineTo(330+Math.cos(a)*2400,560+Math.sin(a)*2400);ctx.lineTo(330+Math.cos(a+.07)*2400,560+Math.sin(a+.07)*2400);ctx.fill()}ctx.globalCompositeOperation='source-over'}
  const c=document.createElement('canvas');c.width=c.height=1080;const g=c.getContext('2d');
  g.drawImage(FR,0,420,1080,1080,0,0,1080,1080);
  // vignette ronde
  const vg=g.createRadialGradient(540,540,300,540,540,620);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.55)');g.fillStyle=vg;g.fillRect(0,0,1080,1080);
  if(v!=='A'){// bandeau texte, dans le cercle
   const grd=g.createLinearGradient(0,640,0,1000);grd.addColorStop(0,'rgba(0,0,0,0)');grd.addColorStop(1,'rgba(0,0,0,.65)');g.fillStyle=grd;g.fillRect(0,600,1080,480);
   g.textAlign='center';g.shadowColor='rgba(0,0,0,.6)';g.shadowBlur=24;g.shadowOffsetY=6;
   g.font='150px Anton';g.fillStyle='#fff';g.fillText('HISTOIRE',540,810);
   g.font='118px Anton';const w1=g.measureText('DE ').width,w2=g.measureText('VILLE').width;const x0=540-(w1+w2)/2;g.textAlign='left';
   g.fillStyle='#fff';g.fillText('DE ',x0,930);g.fillStyle='#ff3b30';g.fillText('VILLE',x0+w1,930);
   g.shadowColor='transparent';g.fillStyle='#ff3b30';g.fillRect(x0+w1,948,w2,12);
  }
  // anneau rouge
  g.strokeStyle='#ff3b30';g.lineWidth=26;g.beginPath();g.arc(540,540,527,0,7);g.stroke();
  return c.toDataURL('image/png')},v);
 fs.writeFileSync(`pfp_${v}.png`,Buffer.from(d.split(',')[1],'base64'))}
await b.close()})();
