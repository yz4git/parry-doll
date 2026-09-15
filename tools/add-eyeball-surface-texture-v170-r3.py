#!/usr/bin/env python3
"""Corrected visible-eyeball UV pass for the exact v17.0 model.

Blender -Y face-forward becomes glTF +Z after Y-up export.  This wrapper reuses the validated
material-only v17.0 eyeball patcher but replaces only its forward-UV locator; no geometry code is
introduced here.
"""
from __future__ import annotations
import math
import os
import runpy

HERE=os.path.dirname(os.path.abspath(__file__))
BASE=os.path.join(HERE,'add-eyeball-surface-texture-v170.py')
M=runpy.run_path(BASE,run_name='__v170_eyeball_surface_r3__')


def corrected_front_uv(helper,doc,binary,prim):
    pos=helper['read_accessor'](doc,binary,prim['attributes']['POSITION'])
    uv=helper['read_accessor'](doc,binary,prim['attributes']['TEXCOORD_0'])
    if len(pos)!=len(uv):raise RuntimeError('POSITION/UV count mismatch on eyeball globe')
    xs=[p[0] for p in pos];ys=[p[1] for p in pos];zs=[p[2] for p in pos]
    cx=(min(xs)+max(xs))*.5;cy=(min(ys)+max(ys))*.5
    rx=max(xs)-min(xs);ry=max(ys)-min(ys);rz=max(zs)-min(zs)
    # Blender forward is -Y. glTF Y-up basis conversion maps that direction to +Z.
    candidates=[]
    for p,t in zip(pos,uv):
        if p[2]>=max(zs)-rz*.055 and abs(p[0]-cx)<=rx*.20 and abs(p[1]-cy)<=ry*.20:
            candidates.append((float(t[0]),float(t[1])))
    if not candidates:
        idx=max(range(len(pos)),key=lambda i:pos[i][2]);candidates=[(float(uv[idx][0]),float(uv[idx][1]))]
    circular=M['circular_mean']
    return circular([u for u,_ in candidates]),sum(v for _,v in candidates)/len(candidates),len(candidates)


# main() resolves front_uv through its own globals dictionary, so replacing this key preserves the
# already-audited patch implementation while correcting only the view-direction UV calculation.
M['front_uv']=corrected_front_uv
M['main'].__globals__['front_uv']=corrected_front_uv

if __name__=='__main__':
    M['main']()
