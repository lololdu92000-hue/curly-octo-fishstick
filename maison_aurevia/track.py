import numpy as np,wave
sr=48000;D=14.5;n=int(sr*D);t=np.arange(n)/sr;L=np.zeros(n);R=np.zeros(n);rng=np.random.default_rng(7)
def add(sig,at,g=1,pan=0):
    i=int(at*sr);j=min(n,i+len(sig));L[i:j]+=sig[:j-i]*g*(1-max(0,pan));R[i:j]+=sig[:j-i]*g*(1+min(0,pan))
def T(d):return np.arange(int(d*sr))/sr
def lp(x,k):return np.convolve(x,np.ones(k)/k,'same')
# nappe : accords majeurs 7 lumineux (Dmaj7 -> Bm9 -> Gmaj7 -> A6)
ch=[[146.8,220,277.2,329.6],[123.5,185,220,277.2],[98,146.8,185,246.9],[110,164.8,220,277.2]]
for k,c in enumerate(ch):
    st=k*2.45;d=2.9;tt=T(d);env=np.minimum(1,tt/0.9)*np.minimum(1,(d-tt)/1.0)
    for i,f in enumerate(c):
        s=np.sin(2*np.pi*f*tt+0.4*np.sin(2*np.pi*0.2*tt))+0.35*np.sin(2*np.pi*f*2.003*tt)
        add(s*env,st,0.035,pan=(-0.4 if i%2 else 0.4))
# arpège cristallin pendant le vol
notes=[587.3,740,880,1108.7,880,740]
for i in range(int(8.2/0.205)):
    f=notes[i%6]*(1 if (i//6)%2==0 else 0.9439);tt=T(0.9)
    s=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*f*3*tt))*np.exp(-tt*5.5)
    add(s,0.3+i*0.205,0.035,pan=np.sin(i)*0.6)
# pulsation douce
for i in range(int(8.2/0.41)):
    tt=T(0.35);k=np.sin(2*np.pi*(55+40*np.exp(-tt*25))*tt)*np.exp(-tt*9);add(k,0.4+i*0.41,0.22)
# montée (7.75 -> 9.25)
tt=T(1.5);noise=lp(rng.normal(0,1,len(tt)),6)*(tt/1.5)**2;add(noise,7.75,0.12)
# whooshs
def whoosh(d):
    tt=T(d);x=lp(rng.normal(0,1,len(tt)),14);return x*np.sin(np.pi*tt/d)**2
add(whoosh(0.55),8.66-0.3,0.55,pan=-0.3);add(whoosh(0.45),9.80-0.25,0.6,pan=0.3)
# impact à 9.97 : sub + corps + scintillement
tt=T(3.5)
sub=np.sin(2*np.pi*(42+60*np.exp(-tt*10))*tt)*np.exp(-tt*1.6)
body=lp(rng.normal(0,1,len(tt)),30)*np.exp(-tt*9)
bell=sum(np.sin(2*np.pi*f*tt)*a for f,a in [(1174.7,1),(1760,.6),(2349.3,.35),(3520,.2)])*np.exp(-tt*1.4)
add(np.tanh(1.6*sub)*0.9+body*0.5,9.97,0.75);add(bell,9.97,0.10,pan=0.2)
# nappe finale tenue
tt=T(4.5);env=np.minimum(1,tt/0.4)*np.minimum(1,(4.5-tt)/1.6)
for i,f in enumerate([146.8,220,277.2,370,440]):add((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*f*2*tt))*env,10.0,0.04,pan=(i-2)*0.25)
# réverb simple
def rev(x):
    y=x.copy()
    for dl,g in [(0.031,.35),(0.047,.3),(0.071,.25),(0.113,.2),(0.167,.15)]:
        k=int(dl*sr);y[k:]+=x[:-k]*g
    return y
L=rev(L);R=rev(R);m=max(np.abs(L).max(),np.abs(R).max());L/=m;R/=m;L*=0.89;R*=0.89
fade=np.minimum(1,(D-t)/0.6);L*=fade;R*=fade
st=np.stack([L,R],1)
with wave.open('track.wav','wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype(np.int16).tobytes())
print('ok')
