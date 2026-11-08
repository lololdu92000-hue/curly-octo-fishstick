import cv2, numpy as np
S=2
src=cv2.imread('src.png'); m0=cv2.imread('mask.png',0)
m0=cv2.morphologyEx(m0,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
h0,w0=src.shape[:2]
im=cv2.resize(src,(w0*S,h0*S),interpolation=cv2.INTER_LANCZOS4)
mask=cv2.resize(m0,(w0*S,h0*S),interpolation=cv2.INTER_LINEAR)
H,W=im.shape[:2]
mf=cv2.GaussianBlur(mask,(0,0),1.5).astype(np.float32)/255
mf3=mf[...,None]
f=im.astype(np.float32)/255
HOR=478*S
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)

# ---- background: inpaint characters, depth blur
small=cv2.resize(im,(w0,h0)); msk=cv2.dilate(m0,np.ones((15,15),np.uint8))
bgs=cv2.inpaint(small,msk,9,cv2.INPAINT_TELEA)
bg=cv2.resize(bgs,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
bg=f*(1-cv2.dilate(mask,np.ones((31,31),np.uint8))[...,None]/255.)+bg*(cv2.dilate(mask,np.ones((31,31),np.uint8))[...,None]/255.)
# blur level per pixel
d=np.where(yy<HOR, 1.0, np.clip(1-(yy-HOR)/(380*S),0,1)**1.6)
levels=[0,2,5,9,14]
stack=[bg]+[cv2.GaussianBlur(bg,(0,0),s*S/2) for s in levels[1:]]
li=d*(len(levels)-1); lo=np.floor(li).astype(int); hi=np.minimum(lo+1,len(levels)-1); t=(li-lo)[...,None]
st=np.stack(stack)
bgb=st[lo,yy.astype(int),xx.astype(int)]*(1-t)+st[hi,yy.astype(int),xx.astype(int)]*t

# floor: cast shadow + reflection
floor=(yy>HOR).astype(np.float32)
ys=np.where(mask.max(1)>128)[0]; foot=ys.max()
M=np.float32([[1,-0.9,0.9*foot],[0,-0.32,foot*1.32]])  # flip up, squash, shear right
sh=cv2.warpAffine(mf,M,(W,H))
sh=cv2.GaussianBlur(sh,(0,0),10*S)*np.clip((yy-HOR)/(200*S),0,1)
contact=np.zeros((H,W),np.float32)
for cx in [(300+330)//2,(370)//1,(430),(520)]:
    pass
fx_=np.where(mask[foot-60*S:foot].max(0)>128)[0]
for x0,x1 in [(fx_.min(),fx_.max())]:
    cv2.ellipse(contact,((x0+x1)//2,foot-6*S),((x1-x0)//2+20*S,22*S),0,0,360,1.0,-1)
contact=cv2.GaussianBlur(contact,(0,0),14*S)
dark=np.clip(sh*0.6+contact*0.6,0,0.7)*floor
bgb=bgb*(1-dark[...,None])
Mr=np.float32([[1,0,0],[0,-1,2*foot]])
refl=cv2.warpAffine(f,Mr,(W,H)); rm=cv2.warpAffine(mf,Mr,(W,H))
fade=np.clip(1-(yy-foot)/(-1),0,1)
rw=(rm*0.10*floor*np.clip((yy-foot+300*S)/(300*S),0,1))[...,None]
bgb=bgb*(1-rw)+cv2.GaussianBlur(refl,(0,0),3*S)*rw

# atmospheric haze near horizon
haze=np.exp(-np.abs(yy-HOR)/(70*S))*0.35
hazec=np.array([0.93,0.90,0.86],np.float32)  # BGR: soft warm-white
bgb=bgb*(1-haze[...,None])+hazec*haze[...,None]
# sky: richer gradient + sun glow top-left
sky=(yy<HOR).astype(np.float32)[...,None]
skyg=np.clip(1-yy/HOR,0,1)[...,None]
bgb=bgb*(1-sky*skyg*0.4)+sky*skyg*0.4*np.array([0.62,0.30,0.06],np.float32)
sun=np.exp(-((xx+50*S)**2+(yy+80*S)**2)/(2*(220*S)**2))[...,None]
bgb=bgb+sun*np.array([0.55,0.75,0.95],np.float32)*0.3

# ---- characters: local contrast, sharpen, key + rim light
lab=cv2.cvtColor((f*255).astype(np.uint8),cv2.COLOR_BGR2LAB)
lab[...,0]=cv2.createCLAHE(2.0,(8,8)).apply(lab[...,0])
ch=cv2.cvtColor(lab,cv2.COLOR_LAB2BGR).astype(np.float32)/255
ch=0.6*ch+0.4*f
ch=cv2.addWeighted(ch,1.6,cv2.GaussianBlur(ch,(0,0),2.0),-0.6,0)
key=np.clip(1.15-0.35*(xx/W)-0.15*(yy/H),0.75,1.15)[...,None]
ch=ch*key*np.array([0.97,1.0,1.05],np.float32)
# AO: darken lower legs/ near ground slightly
ch*= (1-0.12*np.clip((yy-foot+120*S)/(120*S),0,1))[...,None]
# rim light (left/top edges toward sun)
er=cv2.erode(mask,np.ones((5,5),np.uint8)).astype(np.float32)/255
inner=np.clip(mf-cv2.GaussianBlur(er,(0,0),4*S),0,1)
dirw=np.clip(cv2.Sobel(mf,cv2.CV_32F,1,0,ksize=5)*-1+cv2.Sobel(mf,cv2.CV_32F,0,1,ksize=5)*-1,0,None)
dirw=cv2.GaussianBlur(np.clip(dirw/ (dirw.max()+1e-6)*6,0,1),(0,0),2*S)
ch=ch+(inner*dirw*mf)[...,None]*np.array([0.55,0.75,1.0],np.float32)*0.5

out=bgb*(1-mf3)+ch*mf3
# light wrap
out=out+cv2.GaussianBlur(bgb,(0,0),8*S)*(np.clip(mf-cv2.GaussianBlur(mf,(0,0),6*S),0,1)[...,None])*0.25

# ---- global grade
out=np.clip(out,0,None)
bright=np.clip(out.max(2,keepdims=True)-0.82,0,None)*out
bloom=sum(cv2.GaussianBlur(bright,(0,0),s*S) for s in (6,18,45))/3
out=out+bloom*0.9
a=2.51;b=0.03;c=2.43;dd=0.59;e=0.14
x=out*0.95; out=np.clip((x*(a*x+b))/(x*(c*x+dd)+e),0,1)   # ACES filmic
lum=out.mean(2,keepdims=True)
out=out+(1-lum)*lum*0+ (np.array([0.06,0.02,-0.03],np.float32)*(1-lum)**2) + (np.array([-0.04,0.0,0.04],np.float32)*lum**2)
out=lum+(out-lum)*1.12
v=1-0.45*(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.75))**2)
out=out*np.clip(v,0.4,1)[...,None]
# chromatic aberration
b_,g_,r_=cv2.split(out); sc=1.0015
Mc=cv2.getRotationMatrix2D((W/2,H/2),0,sc); r_=cv2.warpAffine(r_,Mc,(W,H),borderMode=cv2.BORDER_REFLECT)
Mc=cv2.getRotationMatrix2D((W/2,H/2),0,1/sc); b_=cv2.warpAffine(b_,Mc,(W,H),borderMode=cv2.BORDER_REFLECT)
out=cv2.merge([b_,g_,r_])
out=out+np.random.default_rng(1).normal(0,0.012,(H,W,1)).astype(np.float32)
cv2.imwrite('realiste.png',np.clip(out*255,0,255).astype(np.uint8))
print('ok')
