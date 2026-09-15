"""Diagnostic-only: inspect exported v17.3 face objects for large overlay artifacts.

This script is allowed to import the NEWLY GENERATED shipping GLB because it never edits/exports it;
it only reports object hierarchy, local/world bounds and materials so visual artifacts can be traced.
"""
from __future__ import annotations
import os, sys, json
import bpy
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
GLB=os.path.join(ROOT,'dist','assets','models','heroine-blender.glb')

def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def under(o,name):
    p=o.parent
    while p:
        if p.name==name:return True
        p=p.parent
    return False

def bounds(o):
    if o.type!='MESH' or not o.data.vertices:return None
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(lo+hi)*.5;s=hi-lo
    return {'center':[round(float(x),6) for x in c],'size':[round(float(x),6) for x in s]}

def path(o):
    names=[o.name];p=o.parent
    while p:
        names.append(p.name);p=p.parent
    return '/'.join(reversed(names))

def main():
    clear();bpy.ops.import_scene.gltf(filepath=GLB)
    records=[]
    for o in bpy.data.objects:
        if o.type!='MESH':continue
        if not (under(o,'BL_HEAD') or under(o,'BL_HEAD_ASSET') or under(o,'BL_FACE_ASSET') or o.name=='HeadShellV140'):
            continue
        b=bounds(o)
        mats=[m.name for m in o.data.materials if m]
        rec={'name':o.name,'data':o.data.name,'path':path(o),'materials':mats,'verts':len(o.data.vertices),'polys':len(o.data.polygons),'bounds':b}
        records.append(rec)
    records.sort(key=lambda r:r['name'])
    print('FACE_OBJECT_COUNT',len(records))
    for r in records:
        print('FACE_OBJECT',json.dumps(r,sort_keys=True))
    # Explicitly rank plausible overlay artifacts: sizeable, shallow/front-facing meshes with pale/skin/sclera material.
    suspects=[]
    for r in records:
        if not r['bounds']:continue
        sx,sy,sz=r['bounds']['size']
        mats=' '.join(r['materials']).lower()
        if max(sx,sy,sz)>=0.018 and any(k in mats for k in ('skin','sclera','white','eye')):
            suspects.append(r)
    suspects.sort(key=lambda r:max(r['bounds']['size']),reverse=True)
    print('FACE_SUSPECT_COUNT',len(suspects))
    for r in suspects[:80]:print('FACE_SUSPECT',json.dumps(r,sort_keys=True))

if __name__=='__main__':main()
