"""Deterministic micro-surface maps for leather, woven silk and hair cards."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
out=Path(__file__).resolve().parents[1]/'dist/assets';rng=np.random.default_rng(94321);N=256
# Stable alpha strand texture: transparent edges, many fine parallel fibers, no painted lighting.
H,W=512,128;yy,xx=np.mgrid[:H,:W];t=yy/(H-1);u=xx/(W-1);width=(1-t*.82);q=(u-.5)/np.maximum(.05,width)+.5
fiber=.63+.28*np.sin(q*240+np.sin(t*8)*.45)**2+.09*np.sin(q*580)**2
edge=np.clip(np.minimum(q,1-q)*18,0,1);tip=np.clip((1-t)*18,0,1);alpha=np.uint8(np.clip(fiber*edge*tip,0,1)*255)
Image.fromarray(alpha).save(out/'hair-fibers.png')
print('Baked hair-fiber alpha')
