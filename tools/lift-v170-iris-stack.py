#!/usr/bin/env python3
"""Apply the only allowed geometry correction to exact v17.0: iris-stack depth.

The original v17.0 IrisOuter/IrisInner/IrisRays/Pupil/EyeLight planes sit about 1 mm inside the
existing sclera sphere.  This patch keeps every X/Y coordinate, mesh shape, node transform,
hierarchy, index and non-eye POSITION unchanged, and changes only those existing eye-detail Z
coordinates so they sit just outside the untouched sclera front.  It deliberately does *not* move
the eye stack to the donor forehead/face surface; visible eye colour is supplied separately as a
texture-only patch to the donor faceUV image.
"""
from __future__ import annotations
import argparse, copy, json, os, runpy, struct

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
CLEARANCE={
 'IrisOuterV167':0.00018,
 'IrisInnerV167':0.00030,
 'IrisRaysV167':0.00040,
 'PupilV167':0.00052,
 'EyeLightV167A':0.00064,
 'EyeLightV167B':0.00062,
}

def args():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--manifest');return p.parse_args()

def side_of(name):
 if name.endswith('_-1'):return -1
 if name.endswith('_1'):return 1
 raise RuntimeError('cannot resolve side '+name)

def kind_of(name):
 for k in CLEARANCE:
  if name.startswith(k+'_'):return k
 return None

def layout(doc,ai):
 acc=doc['accessors'][ai]
 if acc.get('componentType')!=5126 or acc.get('type')!='VEC3' or 'bufferView' not in acc:raise RuntimeError(f'bad POSITION accessor {ai}')
 bv=doc['bufferViews'][acc['bufferView']];stride=int(bv.get('byteStride',12));base=int(bv.get('byteOffset',0))+int(acc.get('byteOffset',0))
 return acc,base,stride

def positions(doc,binary,ai):
 acc,base,stride=layout(doc,ai);return [struct.unpack_from('<fff',binary,base+i*stride) for i in range(acc['count'])]

def write_z(doc,binary,ai,znew):
 acc,base,stride=layout(doc,ai);before=[]
 for i in range(acc['count']):
  off=base+i*stride;x,y,z=struct.unpack_from('<fff',binary,off);before.append((x,y,z));struct.pack_into('<fff',binary,off,x,y,float(znew))
 if 'min' in acc and len(acc['min'])==3:acc['min'][2]=float(znew)
 if 'max' in acc and len(acc['max'])==3:acc['max'][2]=float(znew)
 return before

def main():
 a=args();h=runpy.run_path(HELPER,run_name='__v170_depth_helpers__');doc,b0,_=h['parse_glb'](a.input);doc=copy.deepcopy(doc);binary=bytearray(b0)
 sclera={}
 for n in doc.get('nodes',[]):
  name=n.get('name','')
  if not name.startswith('EyeScleraGlobeV166_'):continue
  side=side_of(name);mi=n['mesh'];prims=doc['meshes'][mi]['primitives']
  if len(prims)!=1:raise RuntimeError('unexpected sclera primitive count')
  vals=positions(doc,binary,prims[0]['attributes']['POSITION']);t=n.get('translation',[0,0,0]);s=n.get('scale',[1,1,1])
  if n.get('rotation') not in (None,[0.0,0.0,0.0,1.0]):raise RuntimeError('unexpected sclera rotation')
  sclera[side]=float(t[2])+max(float(p[2])*float(s[2]) for p in vals)
 if set(sclera)!={-1,1}:raise RuntimeError('two sclera globes required')
 users={}
 for mi,m in enumerate(doc.get('meshes',[])):
  for pi,p in enumerate(m.get('primitives',[])):
   ai=p.get('attributes',{}).get('POSITION')
   if ai is not None:users.setdefault(ai,[]).append((mi,pi,m.get('name','')))
 changed={};nodes=[]
 for n in doc.get('nodes',[]):
  name=n.get('name','');kind=kind_of(name)
  if kind is None:continue
  side=side_of(name);mi=n['mesh'];desired=sclera[side]+CLEARANCE[kind]
  for pi,p in enumerate(doc['meshes'][mi].get('primitives',[])):
   ai=p.get('attributes',{}).get('POSITION')
   if ai is None:raise RuntimeError('target POSITION missing')
   if any(u[0]!=mi for u in users.get(ai,[])):raise RuntimeError(f'shared target POSITION {ai}')
   if ai in changed:continue
   before=write_z(doc,binary,ai,desired);zs=[q[2] for q in before]
   if max(zs)-min(zs)>1e-6:raise RuntimeError(f'non-planar eye detail {ai}')
   old=sum(zs)/len(zs);changed[ai]={'node':name,'kind':kind,'side':side,'old_z':old,'desired_z':desired,'delta_z':desired-old,'vertices':len(before)}
  nodes.append(name)
 if len(nodes)!=2*len(CLEARANCE):raise RuntimeError(f'expected {2*len(CLEARANCE)} target nodes, got {len(nodes)}')
 doc.setdefault('asset',{}).setdefault('extras',{}).update({
  'parryDollRevision':'v17.0-eye-texture-plus-iris-depth-fix',
  'parryDollGeometryPolicy':'only-existing-iris-pupil-highlight-POSITION-z-changed',
  'parryDollScleraGeometryChanged':False,
 })
 h['write_glb'](a.output,doc,bytes(binary))
 out={'revision':'v17.0-eye-texture-plus-iris-depth-fix','sclera_front_z':{str(k):v for k,v in sclera.items()},'clearance':CLEARANCE,'changed_nodes':sorted(nodes),'changed_position_accessors':{str(k):v for k,v in sorted(changed.items())},'changed_geometry_scope':'existing iris/pupil/highlight rigid depth only','x_y_changed':False,'topology_changed':False,'node_transforms_changed':False,'sclera_geometry_changed':False,'output_bytes':os.path.getsize(a.output)}
 print('V170_IRIS_DEPTH_FIX',json.dumps(out,sort_keys=True))
 if a.manifest:json.dump(out,open(a.manifest,'w',encoding='utf-8'),indent=2,sort_keys=True)

if __name__=='__main__':main()
