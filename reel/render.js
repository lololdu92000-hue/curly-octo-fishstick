const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:540,height:960}});
await p.goto('file://'+__dirname+'/reel.html');await p.evaluate(()=>window.ready);
const D=await p.evaluate(()=>DURATION),sc=await p.evaluate(()=>scenes);
execFileSync('python3',['music.py',String(D),JSON.stringify(sc)]);
const fps=30,N=Math.round(D*fps);
const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-i','music.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','reel_nanterre.mp4'],{stdio:['pipe','inherit','inherit']});
for(let i=0;i<N;i++){const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.93)},i/fps);
 const buf=Buffer.from(d.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('frames',N)})();
