#!/usr/bin/env python3
"""Paint only the actually sampled v17.0 donor eye UV islands; never change model shape.

The David Onizaki donor head maps its visible eye whites to two small UV islands in the white
upper-right area of `faceUV`, not to the obvious painted face preview lower in the atlas.  Earlier
painting targeted that preview and therefore never appeared in-game.  This pass resolves the two
visible eye UV centres from HeadShellV140 POSITION+TEXCOORD_0 plus the existing white texels, then
adds only grey-brown iris/pupil/catchlight pixels around those resolved centres.

No POSITION/NORMAL/index/mesh/node/transform/hierarchy/topology data is touched.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,runpy,struct,zlib

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
PNG_SIG=b'\x89PNG\r\n\x1a\n'

def args():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--manifest');return p.parse_args()
def paeth(a,b,c):
 p=a+b-c;pa=abs(p-a);pb=abs(p-b);pc=abs(p-c);return a if pa<=pb and pa<=pc else (b if pb<=pc else c)
def decode_rgba_png(data):
 if not data.startswith(PNG_SIG):raise RuntimeError('faceUV is not PNG')
 pos=8;idat=[];w=h=None
 while pos<len(data):
  ln=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+ln];pos+=12+ln
  if kind==b'IHDR':
   w,h,bit,ctype,comp,flt,interlace=struct.unpack('>IIBBBBB',payload)
   if (bit,ctype,comp,flt,interlace)!=(8,6,0,0,0):raise RuntimeError('unsupported faceUV PNG format')
  elif kind==b'IDAT':idat.append(payload)
  elif kind==b'IEND':break
 raw=zlib.decompress(b''.join(idat));bpp=4;stride=w*bpp;rows=[];off=0;prev=bytearray(stride)
 for _ in range(h):
  f=raw[off];off+=1;src=bytearray(raw[off:off+stride]);off+=stride;dst=bytearray(stride)
  for i,x in enumerate(src):
   left=dst[i-bpp] if i>=bpp else 0;up=prev[i];ul=prev[i-bpp] if i>=bpp else 0
   if f==0:v=x
   elif f==1:v=(x+left)&255
   elif f==2:v=(x+up)&255
   elif f==3:v=(x+((left+up)//2))&255
   elif f==4:v=(x+paeth(left,up,ul))&255
   else:raise RuntimeError(f'unsupported PNG filter {f}')
   dst[i]=v
  rows.append(dst);prev=dst
 return w,h,rows
def chunk(kind,payload):
 body=kind+payload;return struct.pack('>I',len(payload))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
def encode_rgba_png(w,h,rows):
 raw=bytearray()
 for row in rows:raw.append(0);raw.extend(row)
 return PNG_SIG+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')
def getpx(rows,x,y):
 r=rows[y];i=x*4;return (r[i],r[i+1],r[i+2],r[i+3])
def setpx(rows,x,y,c):
 r=rows[y];i=x*4
 for k,v in enumerate(c):r[i+k]=max(0,min(255,int(round(v))))
def image_bytes(doc,binary,img):
 bv=doc['bufferViews'][img['bufferView']];off=int(bv.get('byteOffset',0));return bytes(binary[off:off+int(bv['byteLength'])])
def resolve_eye_uvs(doc,binary,rows,w,h):
 head=next((n for n in doc.get('nodes',[]) if n.get('name')=='HeadShellV140'),None)
 if not head or 'mesh' not in head:raise RuntimeError('HeadShellV140 missing')
 prims=doc['meshes'][head['mesh']].get('primitives',[])
 if len(prims)!=1:raise RuntimeError(f'unexpected HeadShellV140 primitive count {len(prims)}')
 prim=prims[0];pa=prim.get('attributes',{}).get('POSITION');ua=prim.get('attributes',{}).get('TEXCOORD_0')
 if pa is None or ua is None:raise RuntimeError('HeadShellV140 POSITION/TEXCOORD_0 missing')
 pos=H['read_accessor'](doc,binary,pa);uv=H['read_accessor'](doc,binary,ua)
 if len(pos)!=len(uv):raise RuntimeError('HeadShellV140 POSITION/UV mismatch')
 out=[]
 for side in (-1,1):
  target_x=side*.045;target_y=-.040;pts=[]
  for p,t in zip(pos,uv):
   if not (.085<=p[2]<=.115 and -.075<=p[1]<=-.010):continue
   if side<0 and not (-.080<=p[0]<=-.015):continue
   if side>0 and not (.015<=p[0]<=.080):continue
   tx=max(0,min(w-1,int(round(float(t[0])*(w-1)))));ty=max(0,min(h-1,int(round(float(t[1])*(h-1)))))
   c=getpx(rows,tx,ty)
   if min(c[:3])<250:continue
   wt=math.exp(-((p[0]-target_x)/.022)**2-((p[1]-target_y)/.020)**2-((p[2]-.100)/.020)**2)
   if wt<1e-4:continue
   pts.append((wt,float(t[0]),float(t[1])))
  if len(pts)<40:raise RuntimeError(f'could not resolve visible donor eye UV island side={side}: {len(pts)} candidates')
  sw=sum(q[0] for q in pts);u=sum(q[0]*q[1] for q in pts)/sw;v=sum(q[0]*q[2] for q in pts)/sw
  if not (.74<u<.92 and .005<v<.09):raise RuntimeError(f'resolved eye UV outside expected visible islands: {(u,v)}')
  out.append({'side':side,'u':u,'v':v,'x':u*(w-1),'y':v*(h-1),'candidates':len(pts)})
 return out
def paint_iris(rows,w,h,eye):
 cx,cy=eye['x'],eye['y'];scale=(w/1024.0+h/1024.0)*.5
 rx=11.5*scale;ry=13.0*scale;prx=3.7*scale;pry=4.3*scale;changed=0
 x0=max(0,int(cx-rx-2));x1=min(w-1,int(cx+rx+2));y0=max(0,int(cy-ry-2));y1=min(h-1,int(cy+ry+2))
 for y in range(y0,y1+1):
  for x in range(x0,x1+1):
   orig=getpx(rows,x,y)
   # This UV island is intentionally white in the donor atlas. Refuse to paint skin/hair texels.
   if min(orig[:3])<242:continue
   dx=(x-cx)/max(rx,1e-6);dy=(y-cy)/max(ry,1e-6);r=math.sqrt(dx*dx+dy*dy)
   if r>1.0:continue
   ang=math.atan2(dy,dx);fibre=.5+.5*math.sin(ang*41+r*27+.2*math.sin(ang*9));fine=.5+.5*math.sin(ang*73-r*19)
   inner=math.exp(-((r-.38)/.18)**2);limbal=max(0,min(1,(r-.78)/.20));base=.52+.17*fibre+.07*fine
   rr=(108*base+27*inner)*(1-.73*limbal);gg=(94*base+21*inner)*(1-.73*limbal);bb=(87*base+18*inner)*(1-.73*limbal)
   pupil=math.sqrt(((x-cx)/max(prx,1e-6))**2+((y-cy)/max(pry,1e-6))**2)
   if pupil<=1.0:
    q=max(0,min(1,pupil));rr=7+rr*.10*q;gg=7+gg*.09*q;bb=9+bb*.09*q
   h1=math.exp(-((((x-cx)/rx+.35)/.17)**2+(((y-cy)/ry+.34)/.18)**2));h2=.42*math.exp(-((((x-cx)/rx-.20)/.10)**2+(((y-cy)/ry+.05)/.11)**2));hi=max(h1,h2)
   rr=rr*(1-.84*hi)+250*.84*hi;gg=gg*(1-.84*hi)+248*.84*hi;bb=bb*(1-.84*hi)+245*.84*hi
   setpx(rows,x,y,(rr,gg,bb,255));changed+=1
 return {'side':eye['side'],'uv_center':[eye['u'],eye['v']],'pixel_center':[cx,cy],'iris_radius_px':[rx,ry],'pupil_radius_px':[prx,pry],'candidate_vertices':eye['candidates'],'changed_pixels':changed}
def main():
 global H
 a=args();H=runpy.run_path(HELPER,run_name='__v170_eye_atlas_helpers__');doc,binary0,_=H['parse_glb'](a.input);doc=copy.deepcopy(doc);binary=bytes(binary0)
 pos_before,_=H['position_fingerprint'](doc,binary)
 images=doc.get('images',[]);idx=next((i for i,im in enumerate(images) if im.get('name')=='faceUV'),None)
 if idx is None:raise RuntimeError('embedded donor faceUV image missing')
 img=images[idx]
 if img.get('mimeType')!='image/png' or 'bufferView' not in img:raise RuntimeError('faceUV is not embedded PNG')
 png=image_bytes(doc,binary,img);src_hash=hashlib.sha256(png).hexdigest();w,hh,rows=decode_rgba_png(png)
 eyes=resolve_eye_uvs(doc,binary,rows,w,hh);details=[paint_iris(rows,w,hh,e) for e in eyes]
 if any(d['changed_pixels']<200 for d in details):raise RuntimeError(f'too few visible-eye pixels changed: {details}')
 new_png=encode_rgba_png(w,hh,rows);new_hash=hashlib.sha256(new_png).hexdigest();new_bv,binary=H['append_buffer_view'](doc,binary,new_png)
 images[idx]['bufferView']=new_bv;images[idx]['mimeType']='image/png';images[idx].setdefault('extras',{})['parryDollEyeTextureRevision']='v17.0-visible-donor-eye-uv-islands'
 doc.setdefault('asset',{}).setdefault('extras',{})['parryDollVisibleEyeTexture']='faceUV-eye-uv-islands-only'
 H['write_glb'](a.output,doc,binary);fd,fb,_=H['parse_glb'](a.output);pos_after,_=H['position_fingerprint'](fd,fb)
 if pos_before!=pos_after:raise RuntimeError('eye-atlas paint unexpectedly changed POSITION data')
 out={'revision':'v17.0-visible-donor-eye-uv-islands','image':'faceUV','width':w,'height':hh,'source_faceuv_sha256':src_hash,'patched_faceuv_sha256':new_hash,'eyes':details,'geometry_changed':False,'position_fingerprint':pos_after,'output_bytes':os.path.getsize(a.output)}
 print('V170_FACEUV_EYES',json.dumps(out,sort_keys=True))
 if a.manifest:json.dump(out,open(a.manifest,'w',encoding='utf-8'),indent=2,sort_keys=True)
if __name__=='__main__':main()
