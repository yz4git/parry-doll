"""Post-export structural audit for the fresh David Onizaki heroine v17.2 GLB."""
from __future__ import annotations
import argparse, json, os, sys
import bpy

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
DEFAULT_INPUT=os.path.join(ROOT,'dist','assets','models','heroine-blender.glb')
DEFAULT_CONFIG=os.path.join(ROOT,'tools','heroine-donor-fresh-v172.json')

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

def head_obj():
    o=bpy.data.objects.get('HeadShellV140')
    if o and o.type=='MESH':return o
    c=[o for o in bpy.data.objects if o.type=='MESH' and under(o,'BL_HEAD_ASSET') and ('Head' in o.name or any(m and m.name=='DavidOnizakiCleanSkinV172' for m in o.data.materials))]
    if not c:raise RuntimeError('v17.2 head not found')
    return max(c,key=lambda o:len(o.data.vertices))

def main():
    a=parse_args();cfg=json.load(open(a.config,'r',encoding='utf-8'))
    if cfg.get('revision')!='v17.2':raise RuntimeError('unexpected config revision')
    clear();bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.input))
    miss=[n for n in cfg['audit']['required_runtime_nodes'] if bpy.data.objects.get(n) is None]
    if miss:raise RuntimeError('missing runtime nodes: '+', '.join(miss))
    h=head_obj();v=len(h.data.vertices);p=len(h.data.polygons)
    if v<cfg['audit']['min_head_vertices'] or p<cfg['audit']['min_head_polygons']:raise RuntimeError(f'head density low: {v}/{p}')
    new_eye=[o for o in bpy.data.objects if 'V172' in o.name and any(t in o.name for t in ('Eye','Sclera','Iris','Pupil','Lash','Lid','Canthus','Wetline'))]
    old_eye=[o for o in bpy.data.objects if any(t in o.name for t in ('EyeScleraGlobeV166','IrisOuterV167','IrisInnerV167','PupilV167','DonorEyeScleraV171','DonorIrisOuterV171','DonorPupilV171'))]
    lips=[o for o in bpy.data.objects if any(t in o.name for t in ('DonorUpperLipV172','DonorLowerLipV172','DonorMouthSeamV172'))]
    if len(new_eye)<cfg['audit']['min_new_eye_parts']:raise RuntimeError(f'v17.2 eye count low: {len(new_eye)}')
    if len(old_eye)>cfg['audit']['max_old_eye_parts']:raise RuntimeError('old portrait eyes remain')
    if len(lips)<cfg['audit']['min_new_lip_parts']:raise RuntimeError(f'v17.2 lip count low: {len(lips)}')
    for n in ('BL_EYELID_L','BL_EYELID_R','BeautyMarkV172'):
        if bpy.data.objects.get(n) is None:raise RuntimeError(f'missing portrait node: {n}')
    root=bpy.data.objects.get('BLENDER_HEROINE')
    if not root or root.get('source_glb_imported') is not False:raise RuntimeError('fresh-build metadata missing')
    if root.get('donor_albedo_used') is not False:raise RuntimeError('donor albedo policy metadata missing')
    print('FRESH_DONOR_V172_AUDIT',json.dumps({'revision':'v17.2','input_bytes':os.path.getsize(a.input),'head_vertices':v,'head_polygons':p,'new_eye_parts':len(new_eye),'old_eye_parts':len(old_eye),'new_lip_parts':len(lips),'beauty_mark':True,'source_glb_imported':False,'donor_albedo_used':False,'build_pipeline':root.get('build_pipeline')},sort_keys=True))

if __name__=='__main__':main()
