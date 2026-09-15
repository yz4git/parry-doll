#!/usr/bin/env python3
"""Audit restored v17.0 with the only permitted geometry change: eye-detail Z depth."""
from __future__ import annotations
import argparse, json, os, runpy

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
ALLOWED_PREFIXES=('IrisOuterV167_','IrisInnerV167_','IrisRaysV167_','PupilV167_','EyeLightV167A_','EyeLightV167B_')

def args():
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--patched',required=True);return p.parse_args()

def node_mesh_map(doc):
    return {n.get('name',''):n['mesh'] for n in doc.get('nodes',[]) if 'mesh' in n}

def pos_accessors_for_mesh(doc,mi):
    return {p.get('attributes',{}).get('POSITION') for p in doc['meshes'][mi].get('primitives',[]) if p.get('attributes',{}).get('POSITION') is not None}

def all_position_users(doc):
    users={}
    for mi,m in enumerate(doc.get('meshes',[])):
        for pi,p in enumerate(m.get('primitives',[])):
            ai=p.get('attributes',{}).get('POSITION')
            if ai is not None:users.setdefault(ai,[]).append((mi,pi,m.get('name','')))
    return users

def bv_bytes(doc,binary,bvi):
    bv=doc['bufferViews'][bvi];off=int(bv.get('byteOffset',0));ln=int(bv['byteLength']);return binary[off:off+ln]

def image_bytes(doc,binary,name):
    img=next((i for i in doc.get('images',[]) if i.get('name')==name),None)
    if not img or 'bufferView' not in img:return None
    return bv_bytes(doc,binary,img['bufferView'])

def main():
    a=args();h=runpy.run_path(HELPER,run_name='__audit_v170_iris_depth_helpers__')
    od,ob,_=h['parse_glb'](a.original);pd,pb,_=h['parse_glb'](a.patched)
    if len(od.get('nodes',[]))!=len(pd.get('nodes',[])):raise RuntimeError('node count changed')
    node_keys=('name','mesh','children','translation','rotation','scale','matrix')
    for i,(on,pn) in enumerate(zip(od.get('nodes',[]),pd.get('nodes',[]))):
        for k in node_keys:
            if on.get(k)!=pn.get(k):raise RuntimeError(f'node {i} {k} changed')
    if len(od.get('meshes',[]))!=len(pd.get('meshes',[])):raise RuntimeError('mesh count changed')
    omap=node_mesh_map(od);pmap=node_mesh_map(pd)
    if omap!=pmap:raise RuntimeError('node/mesh mapping changed')
    allowed_meshes={mi for name,mi in omap.items() if name.startswith(ALLOWED_PREFIXES)}
    allowed_accessors=set()
    for mi in allowed_meshes:allowed_accessors|=pos_accessors_for_mesh(od,mi)
    for mi,(om,pm) in enumerate(zip(od['meshes'],pd['meshes'])):
        if len(om.get('primitives',[]))!=len(pm.get('primitives',[])):raise RuntimeError(f'primitive count changed mesh {mi}')
        for pi,(op,pp) in enumerate(zip(om.get('primitives',[]),pm.get('primitives',[]))):
            if op.get('indices')!=pp.get('indices'):raise RuntimeError(f'indices changed mesh {mi} primitive {pi}')
            if op.get('mode',4)!=pp.get('mode',4):raise RuntimeError(f'mode changed mesh {mi} primitive {pi}')
            if op.get('attributes',{}).get('POSITION')!=pp.get('attributes',{}).get('POSITION'):raise RuntimeError(f'POSITION binding changed mesh {mi} primitive {pi}')
    users=all_position_users(od);changed=[];unchanged=0
    for ai in sorted(users):
        ov=h['read_accessor'](od,ob,ai);pv=h['read_accessor'](pd,pb,ai)
        if len(ov)!=len(pv):raise RuntimeError(f'POSITION count changed accessor {ai}')
        dz=[]
        for j,(o,p) in enumerate(zip(ov,pv)):
            if abs(float(o[0])-float(p[0]))>1e-8 or abs(float(o[1])-float(p[1]))>1e-8:raise RuntimeError(f'X/Y changed accessor {ai} vertex {j}')
            dz.append(float(p[2])-float(o[2]))
        maxabs=max(abs(d) for d in dz) if dz else 0.0
        if maxabs<=1e-8:unchanged+=1;continue
        if ai not in allowed_accessors:raise RuntimeError(f'non-eye POSITION changed: {ai} users={users[ai]}')
        if min(dz)<=0.010 or max(dz)>=0.050:raise RuntimeError(f'eye Z correction outside safe range accessor {ai}: {min(dz)}..{max(dz)}')
        changed.append({'accessor':ai,'min_delta_z':min(dz),'max_delta_z':max(dz),'vertices':len(dz),'users':users[ai]})
    if not changed:raise RuntimeError('no iris depth correction detected')
    for name,mi in omap.items():
        if name.startswith('EyeScleraGlobeV166_') or name=='HeadShellV140':
            for ai in pos_accessors_for_mesh(od,mi):
                if h['read_accessor'](od,ob,ai)!=h['read_accessor'](pd,pb,ai):raise RuntimeError(f'forbidden geometry change: {name}')
    if image_bytes(od,ob,'faceUV')!=image_bytes(pd,pb,'faceUV'):raise RuntimeError('donor faceUV changed; eye-only request must preserve face texture')
    image_names=[im.get('name','') for im in pd.get('images',[])]
    for expected in ('PARRY_DOLL_IrisTexture_v170','PARRY_DOLL_ScleraTexture_v170'):
        if expected not in image_names:raise RuntimeError(f'missing eye texture {expected}')
    print('V170_IRIS_LIFT_AUDIT',json.dumps({
        'revision':'v17.0-eye-texture-plus-donor-surface-iris-depth-fix',
        'changed_position_accessors':changed,'changed_accessor_count':len(changed),'unchanged_position_accessor_count':unchanged,
        'x_y_unchanged':True,'non_eye_geometry_unchanged':True,'head_geometry_unchanged':True,'sclera_geometry_unchanged':True,
        'node_hierarchy_and_transforms_unchanged':True,'topology_unchanged':True,'donor_faceuv_unchanged':True,'eye_textures':image_names
    },sort_keys=True))

if __name__=='__main__':main()
