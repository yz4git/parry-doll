#!/usr/bin/env python3
"""Audit the eye-pixel-only v17.0 donor faceUV patch."""
from __future__ import annotations
import argparse,hashlib,json,os,runpy
HERE=os.path.dirname(os.path.abspath(__file__));HELPER=os.path.join(HERE,'add-eye-textures-v170.py')
def args():
 p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--patched',required=True);return p.parse_args()
def image_bytes(doc,binary,name):
 m=[im for im in doc.get('images',[]) if im.get('name')==name]
 if len(m)!=1:raise RuntimeError(f'expected one {name}, got {len(m)}')
 im=m[0]
 if im.get('mimeType')!='image/png' or 'bufferView' not in im:raise RuntimeError(f'{name} not embedded PNG')
 bv=doc['bufferViews'][im['bufferView']];off=int(bv.get('byteOffset',0));ln=int(bv['byteLength']);return bytes(binary[off:off+ln]),im
def main():
 a=args();h=runpy.run_path(HELPER,run_name='__audit_v170_eye_atlas_helpers__');od,ob,_=h['parse_glb'](a.original);pd,pb,_=h['parse_glb'](a.patched)
 of,_=image_bytes(od,ob,'faceUV');pf,pim=image_bytes(pd,pb,'faceUV');oh=hashlib.sha256(of).hexdigest();ph=hashlib.sha256(pf).hexdigest()
 if oh==ph:raise RuntimeError('visible donor eye UV texture was not changed')
 rev=(pim.get('extras') or {}).get('parryDollEyeTextureRevision')
 if rev!='v17.0-visible-donor-eye-uv-islands':raise RuntimeError(f'eye atlas revision missing: {rev!r}')
 # Normal map and model topology are not part of the eye-pixel change.
 on,_=image_bytes(od,ob,'faceNormal');pn,_=image_bytes(pd,pb,'faceNormal')
 if on!=pn:raise RuntimeError('faceNormal changed')
 names=[im.get('name','') for im in pd.get('images',[])]
 for expected in ('faceUV','faceNormal','PARRY_DOLL_IrisTexture_v170','PARRY_DOLL_ScleraTexture_v170'):
  if expected not in names:raise RuntimeError(f'missing expected image {expected}')
 extras=pd.get('asset',{}).get('extras',{})
 if extras.get('parryDollVisibleEyeTexture')!='faceUV-eye-uv-islands-only':raise RuntimeError('eye UV island metadata missing')
 print('V170_FACEUV_EYE_AUDIT',json.dumps({'revision':'v17.0-visible-donor-eye-uv-islands','original_faceuv_sha256':oh,'patched_faceuv_sha256':ph,'faceuv_changed':True,'face_normal_unchanged':True,'visible_eye_texture':'faceUV-eye-uv-islands-only','required_images_present':True},sort_keys=True))
if __name__=='__main__':main()
