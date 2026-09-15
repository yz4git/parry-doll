#!/usr/bin/env python3
"""Final audit for exact v17.0 geometry plus visible eyeball texture."""
from __future__ import annotations
import argparse,hashlib,json,os,runpy
HERE=os.path.dirname(os.path.abspath(__file__))
H=runpy.run_path(os.path.join(HERE,'add-eye-textures-v170.py'),run_name='__v170_r3_audit_helpers__')

def args():
 p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--patched',required=True);return p.parse_args()

def main():
 a=args();od,ob,obytes=H['parse_glb'](a.original);pd,pb,pbytes=H['parse_glb'](a.patched)
 oh,on=H['position_fingerprint'](od,ob);ph,pn=H['position_fingerprint'](pd,pb)
 if (oh,on)!=(ph,pn):raise RuntimeError('POSITION fingerprint differs from exact v17.0')
 if od.get('nodes')!=pd.get('nodes'):raise RuntimeError('node hierarchy/transforms changed')
 if len(od.get('meshes',[]))!=len(pd.get('meshes',[])):raise RuntimeError('mesh count changed')
 if pb[:len(ob)]!=ob:raise RuntimeError('original v17.0 binary prefix changed')

 omats=od.get('materials',[]);pmats=pd.get('materials',[])
 sclera_idx=next((i for i,m in enumerate(omats) if m.get('name')=='Sclera'),None)
 final_idx=next((i for i,m in enumerate(pmats) if m.get('name')=='Eyeball Surface v17.0'),None)
 if sclera_idx is None or final_idx is None:raise RuntimeError('required sclera/final eyeball material missing')
 images={i.get('name') for i in pd.get('images',[])}
 if 'PARRY_DOLL_EyeballSurfaceTexture_v170' not in images:raise RuntimeError('visible eyeball texture image missing')

 # Identify the two original high-density Sclera globes from data, not exporter-generated mesh names.
 allowed=set()
 for mi,m in enumerate(od.get('meshes',[])):
  for pi,p in enumerate(m.get('primitives',[])):
   if p.get('material')!=sclera_idx:continue
   pos_idx=p.get('attributes',{}).get('POSITION')
   if pos_idx is None:continue
   if od['accessors'][pos_idx].get('count',0)>=900:allowed.add((mi,pi))
 if len(allowed)!=2:raise RuntimeError(f'expected two original sclera globes, got {sorted(allowed)}')

 changed=[]
 for mi,(om,pm) in enumerate(zip(od.get('meshes',[]),pd.get('meshes',[]))):
  if om.get('name')!=pm.get('name'):raise RuntimeError(f'mesh name changed at {mi}')
  opa=om.get('primitives',[]);ppa=pm.get('primitives',[])
  if len(opa)!=len(ppa):raise RuntimeError(f'primitive count changed at {mi}')
  for pi,(o,p) in enumerate(zip(opa,ppa)):
   if o.get('indices')!=p.get('indices') or o.get('mode')!=p.get('mode') or o.get('targets')!=p.get('targets'):
    raise RuntimeError(f'topology changed at {mi}/{pi}')
   oa=o.get('attributes',{});pa=p.get('attributes',{})
   for semantic,idx in oa.items():
    if pa.get(semantic)!=idx:raise RuntimeError(f'existing attribute {semantic} changed at {mi}/{pi}')
   for semantic in ('POSITION','NORMAL','TANGENT','JOINTS_0','WEIGHTS_0'):
    if oa.get(semantic)!=pa.get(semantic):raise RuntimeError(f'shape attribute {semantic} changed at {mi}/{pi}')
   if o.get('material')!=p.get('material'):
    if (mi,pi) not in allowed:raise RuntimeError(f'non-eyeball material changed at {mi}/{pi}')
    if p.get('material')!=final_idx:raise RuntimeError(f'eyeball final material mismatch at {mi}/{pi}')
    changed.append((mi,pi,om.get('name',''),od['accessors'][oa['POSITION']]['count']))
 if set((m,p) for m,p,_,_ in changed)!=allowed:raise RuntimeError(f'eyeball material changes incomplete: {changed}')

 extras=pd.get('asset',{}).get('extras',{})
 if extras.get('parryDollModelPolicy')!='exact-v17.0-shape-eyeball-texture-only':raise RuntimeError('final eye-only policy tag missing')
 front=extras.get('eyeballFrontUV')
 if not isinstance(front,list) or len(front)!=2:raise RuntimeError('eyeballFrontUV metadata missing')
 # Correct front of a Y-up glTF sphere should be near the equator, not near a UV pole.
 if not (0.30<=float(front[1])<=0.70):raise RuntimeError(f'front UV is not near sphere equator: {front}')

 result={'geometry_changed':False,'position_fingerprint':oh,'position_accessors':on,'nodes_unchanged':True,'topology_unchanged':True,'original_binary_prefix_unchanged':True,'changed_eyeball_primitives':changed,'front_uv':front,'texture':'PARRY_DOLL_EyeballSurfaceTexture_v170','source_sha256':hashlib.sha256(obytes).hexdigest(),'patched_sha256':hashlib.sha256(pbytes).hexdigest()}
 print('V170_FINAL_EYEBALL_R3_AUDIT',json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
