const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:540,height:960}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/reel.html');await p.evaluate(()=>window.ready);
const D=await p.evaluate(()=>DURATION),sfx=await p.evaluate(()=>SFX);fs.writeFileSync('sfx.json',JSON.stringify(sfx));
execFileSync('python3',['music2.py',String(D),'sfx.json']);
const fps=30,N=Math.round(D*fps),SUB=3;
const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-i','music2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','slow','-profile:v','high','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','reel_nanterre_raw.mp4'],{stdio:['pipe','inherit','inherit']});
for(let i=0;i<N;i++){const d=await p.evaluate(([t,s])=>{render(t,s,1/60);return document.getElementById('out').toDataURL('image/jpeg',.94)},[i/fps,SUB]);
 const buf=Buffer.from(d.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%300==0)console.log(i,'/',N);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',N)})();
