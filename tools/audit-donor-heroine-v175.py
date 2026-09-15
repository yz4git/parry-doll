"""Post-export audit for fresh David Onizaki heroine v17.5."""
from __future__ import annotations
import argparse, json, os, sys
import bpy
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
DEFAULT_INPUT=os.path.join(ROOT,'dist','assets','models','heroine-blender.glb')
DEFAULT_CONFIG=os.path.join(ROOT,'tools','heroine-donor-fresh-v175.json')

def tail():
    a=sys.argv
    return a[a.index('--')+1:] if '--' in a else []

def parse_args():
    p=argparse.ArgumentParser();p.add_argument('--input',default=DEFAULT_INPUT);p.add_argument('--config',default=DEFAULT_CONFIG);return p.parse_args(tail())

def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def under(o,name):
    p=o.parent
    while p:
        if p.name==name:return True
        p=p.parent
    return False

def find_head():
    o=bpy.data.objects.get('HeadShellV140')
    if o and o.type=='MESH':return o
    c=[o for o in bpy.data.objects if o.type=='MESH' and under(o,'BL_HEAD_ASSET') and 'Head' in o.name]
    if not c:raise RuntimeError('v17.5 donor head not found')
    return max(c,key=lambda o:len(o.data.vertices))

def components(mesh):
    adj=[set() for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    unseen=set(range(len(mesh.vertices)));out=[]
    while unseen:
        s=unseen.pop();stack=[s];comp={s}
        while stack:
            cur=stack.pop()
            for n in adj[cur]:
                if n in unseen:
                    unseen.remove(n);comp.add(n);stack.append(n)
        out.append(comp)
    out.sort(key=len,reverse=True);return out

def bounds(obj,comp):
    pts=[obj.matrix_world@obj.data.vertices[i].co for i in comp]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return (lo+hi)*.5,hi-lo

def rng(v,a,b):return a<=v<=b

def main():
    a=parse_args();cfg=json.load(open(a.config,'r',encoding='utf-8'))
    if cfg.get('revision')!='v17.5':raise RuntimeError('unexpected config revision')
    clear();bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.input))
    miss=[n for n in cfg['audit']['required_runtime_nodes'] if bpy.data.objects.get(n) is None]
    if miss:raise RuntimeError('missing runtime nodes: '+', '.join(miss))
    h=find_head();v=len(h.data.vertices);p=len(h.data.polygons);comps=components(h.data)
    if v<cfg['audit']['min_head_vertices'] or p<cfg['audit']['min_head_polygons']:raise RuntimeError(f'head density low: {v}/{p}')
    if len(comps)>cfg['audit']['max_head_components_after_cleanup']:raise RuntimeError(f'too many head components: {len(comps)}')
    c=cfg['head_component_cleanup'];matches=[]
    for i,comp in enumerate(comps):
        center,size=bounds(h,comp)
        if (rng(len(comp),c['min_vertices'],c['max_vertices']) and rng(abs(center.x),c['abs_center_x_min'],c['abs_center_x_max']) and rng(center.y,c['center_y_min'],c['center_y_max']) and rng(center.z,c['center_z_min'],c['center_z_max']) and rng(size.x,c['size_x_min'],c['size_x_max']) and rng(size.y,c['size_y_min'],c['size_y_max']) and rng(size.z,c['size_z_min'],c['size_z_max'])):
            matches.append({'index':i,'verts':len(comp),'center':[round(float(x),6) for x in center],'size':[round(float(x),6) for x in size]})
    if matches:raise RuntimeError('diagnosed pale cheek islands remain after export: '+json.dumps(matches,sort_keys=True))

    new_eye=[o for o in bpy.data.objects if 'V175' in o.name and any(t in o.name for t in ('Eye','Sclera','Iris','Pupil','Lash','Lid','Canthus','Wetline'))]
    old_eye=[o for o in bpy.data.objects if any(t in o.name for t in ('V166','V167','DonorScleraAlmondV173','DonorScleraAlmondV174','DonorIrisOuterV173','DonorIrisOuterV174','DonorPupilV173','DonorPupilV174','DonorEyeGlobeV172','DonorScleraPatchV172'))]
    lips=[o for o in bpy.data.objects if any(t in o.name for t in ('DonorUpperLipV175','DonorLowerLipV175','DonorMouthSeamV175'))]
    ears=[o for o in bpy.data.objects if o.name.startswith(tuple(cfg['remove_generated_ears']))]
    if len(new_eye)<cfg['audit']['min_new_eye_parts']:raise RuntimeError(f'v17.5 eye count low: {len(new_eye)}')
    if old_eye:raise RuntimeError('old portrait eye parts remain: '+', '.join(o.name for o in old_eye))
    if len(lips)<cfg['audit']['min_new_lip_parts']:raise RuntimeError(f'v17.5 lip count low: {len(lips)}')
    if ears:raise RuntimeError('generated ear duplicates remain: '+', '.join(o.name for o in ears))
    bl=bpy.data.objects.get('BL_EYELID_L');br=bpy.data.objects.get('BL_EYELID_R')
    if not bl or not br or bl.type!='EMPTY' or br.type!='EMPTY':raise RuntimeError('blink runtime nodes are not EMPTY')
    if bpy.data.objects.get('BeautyMarkV175') is None:raise RuntimeError('BeautyMarkV175 missing')
    mats=[m.name for m in h.data.materials if m]
    if not any(n=='Skin' or n.startswith('Skin.') for n in mats):raise RuntimeError('head Skin material missing: '+repr(mats))
    root=bpy.data.objects.get('BLENDER_HEROINE')
    if not root:raise RuntimeError('BLENDER_HEROINE missing')
    print('FRESH_DONOR_V175_AUDIT',json.dumps({'revision':'v17.5','input_bytes':os.path.getsize(a.input),'head_vertices':v,'head_polygons':p,'head_components':len(comps),'remaining_cheek_matches':0,'new_eye_parts':len(new_eye),'new_lip_parts':len(lips),'generated_ear_parts':len(ears),'blink_l_type':bl.type,'blink_r_type':br.type,'beauty_mark':True,'head_materials':mats,'build_pipeline':root.get('build_pipeline')},sort_keys=True))

if __name__=='__main__':main()
