"""Budget-corrected entry point for hybrid hair v18.3.

Loads the v18.3 authoring implementation, then tightens only generated hair mesh budgets. The immutable
face/head path is unchanged.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import bpy

BASE = Path(__file__).with_name("build-hair-hybrid-v183.py")
spec = importlib.util.spec_from_file_location("hair_v183_base", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {BASE}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_original_tail = mod.extract_v180_tail
_original_detail_budget = mod.decimate_detail


def extract_v180_tail_mobile(old_hair, hcenter, hsize, face_sign):
    tail, source_tris, _subdiv_tris = _original_tail(old_hair, hcenter, hsize, face_sign)
    before = mod.tri_count(tail)
    target = 24000
    if before > target:
        dec = tail.modifiers.new("TailMobileBudgetV183R2", "DECIMATE")
        dec.decimate_type = "COLLAPSE"
        dec.ratio = max(0.12, min(1.0, target / before))
        dec.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = tail
        tail.select_set(True)
        bpy.ops.object.modifier_apply(modifier=dec.name)
        tail.select_set(False)
    after = mod.tri_count(tail)
    if after < 9000:
        raise RuntimeError(f"v18.3 ponytail optimization removed too much silhouette detail: {after}")
    return tail, source_tris, after


def decimate_detail_mobile(detail, target=52000):
    return _original_detail_budget(detail, target=target)


mod.extract_v180_tail = extract_v180_tail_mobile
mod.decimate_detail = decimate_detail_mobile

if __name__ == "__main__":
    mod.main()
