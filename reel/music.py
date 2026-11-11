import numpy as np, wave, json, sys
sr=44100; dur=float(sys.argv[1]); sfx=json.loads(open(sys.argv[2]).read())
n=int(sr*dur); t=np.arange(n)/sr; mus=np.zeros(n); fx=np.zeros(n)
rng=np.random.default_rng(1)
def add(buf,sig,start,g=1):
    i=int(start*sr)
    if i<0: sig=sig[-i:]; i=0
    j=min(n,i+len(sig))
    if i<n: buf[i:j]+=sig[:j-i]*g
def T(d): return np.arange(int(d*sr))/sr
def lp(x,k): return np.convolve(x,np.ones(k)/k,'same')
bpm=140; beat=60/bpm
# --- beat trap half-time
def kick(): tt=T(.5); return np.tanh(3*np.sin(2*np.pi*(45+120*np.exp(-tt*35))*tt)*np.exp(-tt*6))
def b808(f,d): tt=T(d); return np.tanh(2.2*np.sin(2*np.pi*f*tt)*np.exp(-tt*1.6))
def snare(): tt=T(.3); return (lp(rng.normal(0,1,len(tt)),3)*.8+np.sin(2*np.pi*200*tt)*.5)*np.exp(-tt*16)
def hat(o=False): tt=T(.2 if o else .05); return np.diff(rng.normal(0,1,len(tt)),prepend=0)*np.exp(-tt*(15 if o else 90))
roots=[55,55,43.65,49]  # A, A, F, G
start=3.8  # beat drops après le hook
# intro: pad only
for b in range(int(dur/beat)):
    s=b*beat; bar=b//8
    if s<start-0.01 or s>dur-1.5: continue
    k=b%8
    if k in (0,3): add(mus,kick(),s,.9)
    if k==4: add(mus,snare(),s,.55)
    if k in (0,): add(mus,b808(roots[bar%4],beat*3),s,.55)
    add(mus,hat(),s,.13); add(mus,hat(),s+beat/2,.09)
    if k==7 and bar%2: [add(mus,hat(),s+beat*q/4,.1) for q in range(4)]
# pad + cloche mélodie (mineur sombre)
ch=[[220,261.6,329.6],[220,261.6,329.6],[174.6,220,261.6],[196,246.9,293.7]]
barD=beat*8
for k in range(int(dur/barD)+1):
    f=ch[k%4]; s=k*barD; tt=T(barD); env=np.minimum(1,tt/.6)*np.minimum(1,(barD-tt)/.6)
    pad=sum(np.sin(2*np.pi*fr*tt+np.sin(2*np.pi*.3*tt))+.4*np.sin(2*np.pi*fr*1.005*tt) for fr in f)*env
    add(mus,pad,s,.035)
    if s>=start-0.1:
        for q,step in enumerate([0,3,6]):
            fr=f[(q+k)%3]*4; pt=T(.8); add(mus,np.sin(2*np.pi*fr*pt)*np.exp(-pt*5)*(1+.5*np.sin(2*np.pi*fr*2*pt)),s+step*beat,.05)
# --- SFX
def boom(): tt=T(1.6); return np.tanh(2*np.sin(2*np.pi*(38+70*np.exp(-tt*8))*tt)*np.exp(-tt*2.2))+lp(rng.normal(0,1,len(tt)),40)*np.exp(-tt*5)*.6
def whoosh(d=.45): tt=T(d); x=lp(rng.normal(0,1,len(tt)),12); return x*np.sin(np.pi*tt/d)**2*2.2
def riser(d): tt=T(d); x=lp(rng.normal(0,1,len(tt)),6)*(tt/d)**2; return x*1.6+np.sin(2*np.pi*(200+800*(tt/d)**2)*tt)*(tt/d)**2*.25
def pop(): tt=T(.12); return np.sin(2*np.pi*(1300-6000*tt)*tt)*np.exp(-tt*35)
def tick(): tt=T(.05); return np.sin(2*np.pi*2400*tt)*np.exp(-tt*80)
def hit(): tt=T(.5); return lp(rng.normal(0,1,len(tt)),25)*np.exp(-tt*9)*2+np.sin(2*np.pi*70*tt)*np.exp(-tt*10)
def clank(): tt=T(.4); return (np.sin(2*np.pi*620*tt)+.7*np.sin(2*np.pi*1453*tt)+.4*np.sin(2*np.pi*2210*tt))*np.exp(-tt*12)*.6
def engine(d=3.6): tt=T(d); return np.tanh(np.sin(2*np.pi*48*tt+3*np.sin(2*np.pi*9*tt))*1.5)*.35*np.minimum(1,tt/.3)*np.minimum(1,(d-tt)/.4)
def projector(d=5.2): tt=T(d); clicks=(np.sin(2*np.pi*24*tt)>0.97).astype(float); return lp(clicks,8)*.6+lp(rng.normal(0,1,len(tt)),3)*.05
def draw(d=2.5): tt=T(d); return lp(rng.normal(0,1,len(tt)),2)*(.5+.5*np.sin(2*np.pi*3*tt))*.12
def typ():
    out=np.zeros(int(1.6*sr))
    for q in range(16): i=int(q*.09*sr); tt=T(.03); out[i:i+len(tt)]+=lp(rng.normal(0,1,len(tt)),2)*np.exp(-tt*150)*.6
    return out
for tm,k in sfx:
    if k=='boom': add(fx,boom(),tm,.8)
    elif k=='whoosh_in': add(fx,whoosh(),tm-.25,.5)
    elif k=='riser': add(fx,riser(2.9),tm,.35)
    elif k=='riser_small': add(fx,riser(.6),tm-.6,.0)
    elif k=='pop': add(fx,pop(),tm,.35)
    elif k=='tick': add(fx,tick(),tm,.3)
    elif k=='hit': add(fx,hit(),tm,.45)
    elif k=='clank': add(fx,clank(),tm,.3)
    elif k=='engine': add(fx,engine(),tm,.5)
    elif k=='projector': add(fx,projector(),tm,.5)
    elif k=='draw': add(fx,draw(),tm,.6)
    elif k=='type': add(fx,typ(),tm,.5)
# ducking musique pendant archives (plus calme)
duck=np.ones(n); 
mix=mus/ (np.max(np.abs(mus))+1e-9)*.55 + fx/(np.max(np.abs(fx))+1e-9)*.6
mix*=np.minimum(1,np.minimum(t/0.05,(dur-t)/1.5))
mix=np.tanh(mix*1.3)/np.tanh(1.3); mix/=np.max(np.abs(mix)); mix*=.9
st=np.stack([mix,mix],1)
with wave.open('music2.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype(np.int16).tobytes())
