#!/usr/bin/env python3
"""Final audit for v17.0 visible eye texture + permitted iris-depth correction.

This complements audit-v170-iris-lift.py. It verifies that the final shipping GLB keeps the expected
visible-eye texture embedded in David Onizaki's donor faceUV image while the model geometry remains
restricted to the separately-audited iris/pupil/highlight Z-only correction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy

HERE=os.path.dirname(os.path.abspath(__file__))
HELPER=os.path.join(HERE,'add-eye-textures-v170.py')


def args():
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--patched',required=True);return p.parse_args()


def image_bytes(doc,binary,name):
    matches=[im for im in doc.get('images',[]) if im.get('name')==name]
    if len(matches)!=1:raise RuntimeError(f'expected exactly one {name} image, got {len(matches)}')
    im=matches[0]
    if im.get('mimeType')!='image/png' or 'bufferView' not in im:raise RuntimeError(f'{name} is not an embedded PNG')
    bv=doc['bufferViews'][im['bufferView']];off=int(bv.get('byteOffset',0));ln=int(bv['byteLength'])
    return bytes(binary[off:off+ln]),im


def main():
    a=args();h=runpy.run_path(HELPER,run_name='__audit_v170_faceuv_helpers__')
    od,ob,_=h['parse_glb'](a.original);pd,pb,_=h['parse_glb'](a.patched)
    original_faceuv,_=image_bytes(od,ob,'faceUV');patched_faceuv,pim=image_bytes(pd,pb,'faceUV')
    oh=hashlib.sha256(original_faceuv).hexdigest();ph=hashlib.sha256(patched_faceuv).hexdigest()
    if oh==ph:raise RuntimeError('faceUV eye texture was not changed')
    rev=(pim.get('extras') or {}).get('parryDollEyeTextureRevision')
    if rev!='v17.0-visible-faceuv-eyes':raise RuntimeError(f'faceUV eye revision missing: {rev!r}')
    names=[im.get('name','') for im in pd.get('images',[])]
    for expected in ('faceUV','PARRY_DOLL_IrisTexture_v170','PARRY_DOLL_ScleraTexture_v170'):
        if expected not in names:raise RuntimeError(f'missing expected eye image {expected}')
    if 'PARRY_DOLL_EyeballSurfaceTexture_v170' in names:raise RuntimeError('obsolete whole-eyeball paint workaround present')
    asset_extras=pd.get('asset',{}).get('extras',{})
    if asset_extras.get('parryDollVisibleEyeTexture')!='faceUV-only':
        raise RuntimeError('faceUV-only visible eye metadata missing')
    print('V170_FACEUV_EYE_AUDIT',json.dumps({
        'revision':'v17.0-visible-faceuv-eyes',
        'original_faceuv_sha256':oh,
        'patched_faceuv_sha256':ph,
        'faceuv_changed':True,
        'visible_eye_texture':'faceUV-only',
        'required_images_present':True,
        'obsolete_eyeball_surface_texture_present':False,
    },sort_keys=True))

if __name__=='__main__':main()
