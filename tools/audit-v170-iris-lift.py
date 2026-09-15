#!/usr/bin/env python3
"""Audit the only allowed geometry change on restored v17.0: iris stack depth.

The patched GLB may add eye textures/UVs/material metadata, and may move only the already-existing
IrisOuter/IrisInner/IrisRays/Pupil/EyeLight POSITION Z coordinates.  All X/Y coordinates,
all non-eye-detail POSITION accessors, topology, node transforms/hierarchy and sclera geometry must
remain identical to the exact v17.0 source model.
"""
from __future__ import annotations

import argparse
import json
import os
import runpy

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
ALLOWED_PREFIXES=('IrisOuterV167_','IrisInnerV167_','IrisRaysV167_','PupilV167_','EyeLightV167A_','EyeLightV167B_')


def args():
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--patched',required=True);return p.parse_args()


def node_mesh_map(doc):
    out={}
    for n in doc.get('nodes',[]):
        if 'mesh' in n: out[n.get('name','')]=n['mesh']
    return out


def pos_accessors_for_mesh(doc,mesh_index):
    return {p.get('attributes',{}).get('POSITION') for p in doc['meshes'][mesh_index].get('primitives',[]) if p.get('attributes',{}).get('POSITION') is not None}


def all_position_users(doc):
    users={}
    for mi,m in enumerate(doc.get('meshes',[])):
        for pi,p in enumerate(m.get('primitives',[])):
            ai=p.get('attributes',{}).get('POSITION')
            if ai is not None:users.setdefault(ai,[]).append((mi,pi,m.get('name','')))
    return users


def main():
    a=args();h=runpy.run_path(HELPER,run_name='__audit_v170_iris_lift_helpers__')
    od,ob,_=h['parse_glb'](a.original);pd,pb,_=h['parse_glb'](a.patched)
    if len(od.get('nodes',[]))!=len(pd.get('nodes',[])):raise RuntimeError('node count changed')
    # Node transforms/hierarchy/object->mesh bindings must remain exact.
    node_keys=('name','mesh','children','translation','rotation','scale','matrix')
    for i,(on,pn) in enumerate(zip(od.get('nodes',[]),pd.get('nodes',[]))):
        for k in node_keys:
            if on.get(k)!=pn.get(k):raise RuntimeError(f'node {i} {k} changed: {on.get(k)!r} -> {pn.get(k)!r}')
    if len(od.get('meshes',[]))!=len(pd.get('meshes',[])):raise RuntimeError('mesh count changed')

    omap=node_mesh_map(od);pmap=node_mesh_map(pd)
    if omap!=pmap:raise RuntimeError('node/mesh mapping changed')
    allowed_meshes={mi for name,mi in omap.items() if name.startswith(ALLOWED_PREFIXES)}
    if len(allowed_meshes)<10:raise RuntimeError(f'too few allowed eye-detail meshes: {len(allowed_meshes)}')
    allowed_accessors=set()
    for mi in allowed_meshes:allowed_accessors|=pos_accessors_for_mesh(od,mi)

    # Primitive topology/index bindings remain unchanged. TEXCOORD/material bindings may differ because of texturing.
    for mi,(om,pm) in enumerate(zip(od['meshes'],pd['meshes'])):
        if len(om.get('primitives',[]))!=len(pm.get('primitives',[])):raise RuntimeError(f'primitive count changed mesh {mi}')
        for pi,(op,pp) in enumerate(zip(om.get('primitives',[]),pm.get('primitives',[]))):
            if op.get('indices')!=pp.get('indices'):raise RuntimeError(f'indices accessor binding changed mesh {mi} primitive {pi}')
            if op.get('mode',4)!=pp.get('mode',4):raise RuntimeError(f'primitive mode changed mesh {mi} primitive {pi}')
            if op.get('attributes',{}).get('POSITION')!=pp.get('attributes',{}).get('POSITION'):
                raise RuntimeError(f'POSITION accessor binding changed mesh {mi} primitive {pi}')

    # Compare every original POSITION accessor numerically. Only allowed accessors may differ, and there only Z.
    changed=[];unchanged=0
    users=all_position_users(od)
    for ai in sorted(users):
        ov=h['read_accessor'](od,ob,ai);pv=h['read_accessor'](pd,pb,ai)
        if len(ov)!=len(pv):raise RuntimeError(f'POSITION count changed accessor {ai}')
        diffs=[]
        for j,(o,p) in enumerate(zip(ov,pv)):
            if len(o)!=3 or len(p)!=3:raise RuntimeError(f'POSITION {ai} not VEC3')
            if abs(float(o[0])-float(p[0]))>1e-8 or abs(float(o[1])-float(p[1]))>1e-8:
                raise RuntimeError(f'X/Y changed accessor {ai} vertex {j}')
            diffs.append(float(p[2])-float(o[2]))
        maxabs=max(abs(d) for d in diffs) if diffs else 0.0
        if maxabs<=1e-8:
            unchanged+=1;continue
        if ai not in allowed_accessors:raise RuntimeError(f'non-eye-detail POSITION accessor changed: {ai} users={users[ai]}')
        spread=max(diffs)-min(diffs)
        if spread>1e-7:raise RuntimeError(f'non-uniform Z shift would alter shape: accessor {ai} spread={spread}')
        changed.append({'accessor':ai,'delta_z':sum(diffs)/len(diffs),'vertices':len(diffs),'users':users[ai]})

    if not changed:raise RuntimeError('no iris depth correction detected')

    # Verify the sclera globe POSITION accessors are bit/numerically unchanged.
    for name,mi in omap.items():
        if not name.startswith('EyeScleraGlobeV166_'):continue
        for ai in pos_accessors_for_mesh(od,mi):
            if h['read_accessor'](od,ob,ai)!=h['read_accessor'](pd,pb,ai):raise RuntimeError(f'sclera geometry changed: {name}')

    # Ensure expected eye textures exist and the obsolete painted-surface workaround is absent.
    image_names=[im.get('name','') for im in pd.get('images',[])]
    for expected in ('PARRY_DOLL_IrisTexture_v170','PARRY_DOLL_ScleraTexture_v170'):
        if expected not in image_names:raise RuntimeError(f'missing eye texture {expected}')
    if 'PARRY_DOLL_EyeballSurfaceTexture_v170' in image_names:
        raise RuntimeError('obsolete painted eyeball-surface workaround still present')

    print('V170_IRIS_LIFT_AUDIT',json.dumps({
        'revision':'v17.0-eye-texture-plus-iris-depth-fix',
        'changed_position_accessors':changed,
        'changed_accessor_count':len(changed),
        'unchanged_position_accessor_count':unchanged,
        'x_y_unchanged':True,
        'non_eye_geometry_unchanged':True,
        'sclera_geometry_unchanged':True,
        'node_hierarchy_and_transforms_unchanged':True,
        'topology_unchanged':True,
        'eye_textures':image_names,
    },sort_keys=True))

if __name__=='__main__':main()
