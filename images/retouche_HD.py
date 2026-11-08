import cv2, numpy as np
src=cv2.imread('src.png'); S=2
h,w=src.shape[:2]
im=cv2.resize(src,(w*S,h*S),interpolation=cv2.INTER_LANCZOS4)
# lissage qui garde les contours (enlève les pixels/compression)
im=cv2.bilateralFilter(im,9,30,7)
f=im.astype(np.float32)/255
# netteté HD (2 niveaux)
f=cv2.addWeighted(f,1.5,cv2.GaussianBlur(f,(0,0),1.2),-0.5,0)
f=cv2.addWeighted(f,1.25,cv2.GaussianBlur(f,(0,0),6),-0.25,0)
f=np.clip(f,0,1)
# couleurs : vibrance + contraste doux
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
s=hsv[...,1]; hsv[...,1]=np.clip(s+(1-s)*s*0.55,0,1)
f=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
f=np.clip(0.5+(f-0.5)*1.08,0,1)
f=f**0.97
# ciel plus profond en haut
H,W=f.shape[:2]; yy=np.mgrid[0:H,0:W][0].astype(np.float32)
sky=np.clip(1-yy/(470*S),0,1)[...,None]**1.5
f=f*(1-sky*0.18)+sky*0.18*np.array([0.62,0.28,0.05],np.float32)
# léger éclat sur les zones brillantes (peau, épée)
br=np.clip(f.max(2,keepdims=True)-0.8,0,None)*f
f=np.clip(f+cv2.GaussianBlur(br,(0,0),8)*0.6,0,1)
cv2.imwrite('hd.png',(f*255).astype(np.uint8))
