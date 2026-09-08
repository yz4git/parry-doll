"""Deterministic authored stone PBR maps; Pillow + NumPy, no runtime download."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np, random
out=Path(__file__).resolve().parents[1]/'dist/assets';out.mkdir(exist_ok=True)
rng=np.random.default_rng(731);rnd=random.Random(731);size=512
noise=Image.fromarray(rng.integers(0,256,(64,64),dtype=np.uint8)).resize((size,size),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(2))
h=np.asarray(noise,dtype=np.float32)/255
fine=rng.normal(0,1,(size,size));height=h*.42+fine*.035+.4
seams=Image.new('L',(size,size),0);draw=ImageDraw.Draw(seams)
for row in range(4):
 y=row*128;draw.line([(0,y),(512,y)],fill=255,width=5)
 for col in range(4):
  x=(col*128+(64 if row%2 else 0))%512;draw.line([(x,y),(x,y+128)],fill=255,width=5)
  for k in range(2):
   px=x+rnd.randrange(14,105);py=y+rnd.randrange(15,100);points=[(px,py)]
   for j in range(rnd.randrange(2,5)):px+=rnd.randrange(-13,15);py+=rnd.randrange(7,19);points.append((px,py))
   draw.line(points,fill=130,width=1)
seam=np.asarray(seams.filter(ImageFilter.GaussianBlur(1)),dtype=np.float32)/255
height=np.clip(height-seam*.28,0,1)
base=np.stack([155+height*62,155+height*59,145+height*54],axis=-1)
base+=fine[:,:,None]*1.8;base*=1-seam[:,:,None]*.35
moss=np.maximum(0,h-.67)*40;base[:,:,1]+=moss;base[:,:,0]-=moss*.3
Image.fromarray(np.uint8(np.clip(base,0,255))).save(out/'stone-color.png',optimize=True)
gy,gx=np.gradient(height);normal=np.dstack([-gx*5,np.ones_like(gx),-gy*5]);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
# OpenGL tangent-space normal map stores x/y slopes then up as blue.
normal=normal[:,:,[0,2,1]]
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(out/'stone-normal.png',optimize=True)
rough=np.uint8(np.clip(185+height*52+seam*15,0,255));Image.fromarray(rough).convert('RGB').save(out/'stone-rough.png',optimize=True)
print('Generated stone-color.png, stone-normal.png, stone-rough.png')
