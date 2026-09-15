#!/usr/bin/env python3
"""Paint visible eye texture into the donor faceUV of exact v17.0 without changing model shape.

v17.0 uses the David Onizaki donor head as a closed facial surface.  Its original procedural eye
meshes are behind that surface, so even after correcting their ~1 mm sclera-depth error they are not
what the camera sees.  The visible circular eye regions come from the donor faceUV itself.

This pass therefore edits only the embedded `faceUV` PNG: warm sclera, grey-brown iris, pupil and
small catchlights are painted inside the two existing donor eye sockets.  No POSITION/NORMAL/index,
mesh, node, transform, hierarchy or topology data is touched.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import runpy
import struct
import zlib

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
PNG_SIG=b'\x89PNG\r\n\x1a\n'


def args():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--manifest');return p.parse_args()

def paeth(a,b,c):
 p=a+b-c;pa=abs(p-a);pb=abs(p-b);pc=abs(p-c)
 return a if pa<=pb and pa<=pc else (b if pb<=pc else c)

def decode_rgba_png(data):
 if not data.startswith(PNG_SIG):raise RuntimeError('faceUV is not PNG')
 pos=8;idat=[];w=h=None
 while pos<len(data):
  ln=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+ln];pos+=12+ln
  if kind==b'IHDR':
   w,h,bit,ctype,comp,flt,interlace=struct.unpack('>IIBBBBB',payload)
   if (bit,ctype,comp,flt,interlace)!=(8,6,0,0,0):raise RuntimeError(f'unsupported faceUV PNG format {(bit,ctype,comp,flt,interlace)}')
  elif kind==b'IDAT':idat.append(payload)
  elif kind==b'IEND':break
 if not w or not h:raise RuntimeError('PNG IHDR missing')
 raw=zlib.decompress(b''.join(idat));bpp=4;stride=w*bpp;rows=[];off=0;prev=bytearray(stride)
 for _y in range(h):
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

def png_chunk(kind,payload):
 body=kind+payload;return struct.pack('>I',len(payload))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)

def encode_rgba_png(w,h,rows):
 raw=bytearray()
 for row in rows:raw.append(0);raw.extend(row)
 return PNG_SIG+png_chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+png_chunk(b'IDAT',zlib.compress(bytes(raw),9))+png_chunk(b'IEND',b'')

def getpx(rows,x,y):
 i=x*4;r=rows[y];return (r[i],r[i+1],r[i+2],r[i+3])

def setpx(rows,x,y,rgba):
 i=x*4;r=rows[y]
 for k,v in enumerate(rgba):r[i+k]=max(0,min(255,int(round(v))))

def color_dist(a,b):return math.sqrt(sum((float(a[i])-float(b[i]))**2 for i in range(3)))

def detect_socket(rows,w,h,expected_x,expected_y):
 # Exact donor faceUV is 1024x1024, but scale the search window for safety.
 sx=w/1024.0;sy=h/1024.0;cx0=expected_x*sx;cy0=expected_y*sy
 target=(231,162,139);pts=[]
 for y in range(max(0,int(cy0-70*sy)),min(h,int(cy0+70*sy)+1)):
  for x in range(max(0,int(cx0-80*sx)),min(w,int(cx0+80*sx)+1)):
   p=getpx(rows,x,y)
   if color_dist(p,target)<22.0:pts.append((x,y))
 if len(pts)<500:raise RuntimeError(f'could not detect donor eye socket near {(expected_x,expected_y)}; pixels={len(pts)}')
 cx=sum(x for x,_ in pts)/len(pts);cy=sum(y for _,y in pts)/len(pts)
 xs=[x for x,_ in pts];ys=[y for _,y in pts]
 return cx,cy,(min(xs),min(ys),max(xs),max(ys)),len(pts)

def paint_eye(rows,w,h,cx,cy,bbox,seed):
 # Socket size comes from detected donor fill rather than hardcoding model geometry.
 bw=max(1,bbox[2]-bbox[0]+1);bh=max(1,bbox[3]-bbox[1]+1)
 socket_rx=bw*.50;socket_ry=bh*.50
 iris_rx=socket_rx*.56;iris_ry=socket_ry*.62
 pupil_rx=iris_rx*.31;pupil_ry=iris_ry*.34
 target=(231,162,139)
 changed=0
 x0=max(0,int(cx-socket_rx-3));x1=min(w-1,int(cx+socket_rx+3));y0=max(0,int(cy-socket_ry-3));y1=min(h-1,int(cy+socket_ry+3))
 for y in range(y0,y1+1):
  for x in range(x0,x1+1):
   orig=getpx(rows,x,y)
   # Preserve eyelid/brow pixels; repaint only the donor socket fill.
   ex=(x-cx)/max(socket_rx,1e-6);ey=(y-cy)/max(socket_ry,1e-6);er=math.sqrt(ex*ex+ey*ey)
   if er>1.04 or color_dist(orig,target)>34.0:continue
   edge=max(0.0,min(1.0,(er-.78)/.24))
   grain=math.sin((x+seed)*.17)*math.sin((y-seed)*.13)
   scl=(241+2*grain-8*edge,237+2*grain-7*edge,233+1.5*grain-6*edge,255)
   out=scl
   dx=(x-cx)/max(iris_rx,1e-6);dy=(y-cy)/max(iris_ry,1e-6);r=math.sqrt(dx*dx+dy*dy)
   if r<=1.0:
    ang=math.atan2(dy,dx)
    fibre=.5+.5*math.sin(ang*39.0+r*28.0+.25*math.sin(ang*7.0))
    fine=.5+.5*math.sin(ang*79.0-r*17.0)
    inner=math.exp(-((r-.36)/.17)**2)
    limbal=max(0.0,min(1.0,(r-.80)/.18))
    b=.50+.18*fibre+.07*fine
    rr=(112*b+25*inner)*(1-.70*limbal);gg=(98*b+19*inner)*(1-.70*limbal);bb=(91*b+16*inner)*(1-.70*limbal)
    pr=math.sqrt(((x-cx)/max(pupil_rx,1e-6))**2+((y-cy)/max(pupil_ry,1e-6))**2)
    if pr<=1.0:
     q=max(0.0,min(1.0,pr));rr=7+rr*.12*q;gg=7+gg*.10*q;bb=9+bb*.10*q
    # Two restrained game-style catchlights, baked into texture only.
    h1=math.exp(-(((dx+.36)/.18)**2+((dy+.34)/.20)**2))
    h2=math.exp(-(((dx-.24)/.10)**2+((dy+.08)/.11)**2))*.45
    hi=max(h1,h2)
    rr=rr*(1-.82*hi)+249*.82*hi;gg=gg*(1-.82*hi)+247*.82*hi;bb=bb*(1-.82*hi)+244*.82*hi
    out=(rr,gg,bb,255)
   setpx(rows,x,y,out);changed+=1
 return {'center':[cx,cy],'socket_bbox':list(bbox),'socket_radius':[socket_rx,socket_ry],'iris_radius':[iris_rx,iris_ry],'pupil_radius':[pupil_rx,pupil_ry],'changed_pixels':changed}

def main():
 a=args();h=runpy.run_path(HELPER,run_name='__v170_faceuv_eye_helpers__');doc,binary0,_=h['parse_glb'](a.input);doc=copy.deepcopy(doc);binary=bytes(binary0)
 pos_before,_=h['position_fingerprint'](doc,binary)
 images=doc.get('images',[]);idx=next((i for i,im in enumerate(images) if im.get('name')=='faceUV'),None)
 if idx is None:raise RuntimeError('embedded donor faceUV image missing')
 im=images[idx]
 if 'bufferView' not in im or im.get('mimeType')!='image/png':raise RuntimeError('faceUV is not embedded PNG')
 bv=doc['bufferViews'][im['bufferView']];off=int(bv.get('byteOffset',0));png=bytes(binary[off:off+int(bv['byteLength'])]);src_hash=hashlib.sha256(png).hexdigest()
 w,hh,rows=decode_rgba_png(png)
 left=detect_socket(rows,w,hh,380,702);right=detect_socket(rows,w,hh,641,702)
 details=[paint_eye(rows,w,hh,*left[:3],17),paint_eye(rows,w,hh,*right[:3],53)]
 new_png=encode_rgba_png(w,hh,rows);new_hash=hashlib.sha256(new_png).hexdigest()
 new_bv,binary=h['append_buffer_view'](doc,binary,new_png)
 images[idx]['bufferView']=new_bv;images[idx]['mimeType']='image/png';images[idx].setdefault('extras',{})['parryDollEyeTextureRevision']='v17.0-visible-faceuv-eyes'
 doc.setdefault('asset',{}).setdefault('extras',{})['parryDollVisibleEyeTexture']='faceUV-only'
 h['write_glb'](a.output,doc,binary)
 final_doc,final_bin,_=h['parse_glb'](a.output);pos_after,_=h['position_fingerprint'](final_doc,final_bin)
 if pos_before!=pos_after:raise RuntimeError('faceUV paint unexpectedly changed POSITION data')
 out={'revision':'v17.0-visible-faceuv-eyes','image':'faceUV','width':w,'height':hh,'source_faceuv_sha256':src_hash,'patched_faceuv_sha256':new_hash,'detected_socket_pixels':[left[3],right[3]],'eyes':details,'geometry_changed':False,'position_fingerprint':pos_after,'output_bytes':os.path.getsize(a.output)}
 print('V170_FACEUV_EYES',json.dumps(out,sort_keys=True))
 if a.manifest:json.dump(out,open(a.manifest,'w',encoding='utf-8'),indent=2,sort_keys=True)

if __name__=='__main__':main()
