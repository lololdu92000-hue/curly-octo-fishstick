const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1440,height:1152}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://127.0.0.1:8765/film.html');await p.evaluate(()=>window.ready);
const FPS=60,N=Math.round(14.5*FPS),SUB=+process.env.SUB||3;
const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','60','-c:v','mjpeg','-i','-','-i','track.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','16','-preset','slow','-profile:v','high','-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart','maison_aurevia.mp4'],{stdio:['pipe','inherit','inherit']});
const t0=Date.now();
for(let i=0;i<N;i++){const d=await p.evaluate(([t,s])=>{seek(t,s);return document.getElementById('out').toDataURL('image/jpeg',0.96)},[i/FPS,SUB]);
 const buf=Buffer.from(d.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(i%60==0)console.log(i,'/',N,Math.round((Date.now()-t0)/1000)+'s');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done')})();
