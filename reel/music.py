import numpy as np, wave, json, sys
sr=44100; dur=float(sys.argv[1]); scenes=json.loads(sys.argv[2])
n=int(sr*dur); t=np.arange(n)/sr; out=np.zeros(n)
bpm=92; beat=60/bpm
def add(sig,start):
    i=int(start*sr); j=min(n,i+len(sig)); 
    if i<n: out[i:j]+=sig[:j-i]
# kick
kt=np.arange(int(.35*sr))/sr; kick=np.sin(2*np.pi*(50+90*np.exp(-kt*30))*kt)*np.exp(-kt*9)
rng=np.random.default_rng(0)
ht=np.arange(int(.06*sr))/sr; hat=rng.normal(0,1,len(ht))*np.exp(-ht*70); hat=np.diff(hat,prepend=0)
st=np.arange(int(.25*sr))/sr; snare=(rng.normal(0,1,len(st))*.6+np.sin(2*np.pi*190*st))*np.exp(-st*18)
b=0
while b*beat<dur-1:
    s=b*beat
    if b%4 in (0,2) or (b%8==7): add(kick*.9,s)
    if b%4 in (1,3): add(snare*.35,s)
    add(hat*.18,s+beat/2)
    b+=1
# pad chords Am F C G
ch=[[220,261.6,329.6],[174.6,220,261.6],[130.8,164.8,196,261.6],[196,246.9,293.7]]
bar=beat*4
for k in range(int(dur/bar)+1):
    f=ch[k%4]; s=k*bar; L=int(bar*sr); tt=np.arange(L)/sr
    env=np.minimum(1,tt/.4)*np.minimum(1,(bar-tt)/.4)
    sig=sum(np.sin(2*np.pi*fr*tt)+.3*np.sin(2*np.pi*fr*2*tt+1) for fr in f)*env*.07
    add(sig,s)
    # pluck melody
    for q in range(4):
        fr=f[(q*2+k)%len(f)]*2; pt=np.arange(int(.5*sr))/sr
        add(np.sin(2*np.pi*fr*pt)*np.exp(-pt*7)*.08,s+q*beat+beat*.5*(q%2))
# whoosh + pop at scenes
for s in scenes[1:]:
    wl=int(.5*sr); w=rng.normal(0,1,wl); 
    w=np.convolve(w,np.ones(30)/30,'same')*np.sin(np.linspace(0,np.pi,wl))**2
    add(w*.5,s-.35)
for s in scenes:
    pt=np.arange(int(.12*sr))/sr; add(np.sin(2*np.pi*(900-3000*pt)*pt)*np.exp(-pt*40)*.4,s+.2)
fade=np.minimum(1,np.minimum(t/0.5,(dur-t)/1.2)); out*=fade
out=out/np.max(np.abs(out))*.85
with wave.open('music.wav','wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype(np.int16).tobytes())
