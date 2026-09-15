#!/usr/bin/env python3
"""Audit that the eye-textured model keeps the exact v17.0 shape/topology."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
PATCHER = os.path.join(HERE, "add-eye-textures-v170.py")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True)
    p.add_argument("--patched", required=True)
    return p.parse_args()


def main():
    a = parse_args()
    h = runpy.run_path(PATCHER, run_name="__v170_eye_texture_helpers__")
    parse_glb = h["parse_glb"]
    position_fingerprint = h["position_fingerprint"]
    target_materials = h["TARGET_MATERIALS"]

    odoc, obin, obytes = parse_glb(a.original)
    pdoc, pbin, pbytes = parse_glb(a.patched)

    oh, on = position_fingerprint(odoc, obin)
    ph, pn = position_fingerprint(pdoc, pbin)
    if oh != ph or on != pn:
        raise RuntimeError(f"shape fingerprint mismatch: {oh}/{on} != {ph}/{pn}")
    if odoc.get("nodes") != pdoc.get("nodes"):
        raise RuntimeError("node transforms/hierarchy changed")
    if len(odoc.get("meshes", [])) != len(pdoc.get("meshes", [])):
        raise RuntimeError("mesh count changed")

    for mi, (om, pm) in enumerate(zip(odoc.get("meshes", []), pdoc.get("meshes", []))):
        if om.get("name") != pm.get("name"):
            raise RuntimeError(f"mesh name changed at {mi}")
        if len(om.get("primitives", [])) != len(pm.get("primitives", [])):
            raise RuntimeError(f"primitive count changed at mesh {mi}")
        for pi, (op, pp) in enumerate(zip(om.get("primitives", []), pm.get("primitives", []))):
            for key in ("indices", "mode", "material", "targets"):
                if op.get(key) != pp.get(key):
                    raise RuntimeError(f"topology changed at mesh {mi} primitive {pi} key {key}")
            oa = op.get("attributes", {})
            pa = pp.get("attributes", {})
            for semantic, accessor in oa.items():
                if pa.get(semantic) != accessor:
                    raise RuntimeError(f"existing attribute {semantic} changed at {mi}/{pi}")
            if pa.get("POSITION") != oa.get("POSITION"):
                raise RuntimeError(f"POSITION accessor changed at {mi}/{pi}")

    # Every original BIN byte remains byte-identical at the front of the patched BIN.
    if pbin[:len(obin)] != obin:
        raise RuntimeError("original binary buffer changed")

    mats = {m.get("name", ""): m for m in pdoc.get("materials", [])}
    for name in target_materials:
        if name not in mats:
            raise RuntimeError(f"eye material missing after patch: {name}")
        tex = mats[name].get("pbrMetallicRoughness", {}).get("baseColorTexture")
        if not isinstance(tex, dict) or "index" not in tex:
            raise RuntimeError(f"eye texture not bound on material: {name}")

    image_names = {i.get("name") for i in pdoc.get("images", [])}
    required_images = {"PARRY_DOLL_IrisTexture_v170", "PARRY_DOLL_ScleraTexture_v170"}
    if not required_images.issubset(image_names):
        raise RuntimeError("required embedded eye texture images missing")

    extras = pdoc.get("asset", {}).get("extras", {})
    if extras.get("parryDollModelPolicy") != "exact-v17.0-shape-eye-texture-only":
        raise RuntimeError("v17.0 eye-texture-only policy tag missing")
    if extras.get("v170SourceCommit") != h["V170_COMMIT"]:
        raise RuntimeError("v17.0 source commit tag mismatch")

    result = {
        "source_glb_sha256": hashlib.sha256(obytes).hexdigest(),
        "patched_glb_sha256": hashlib.sha256(pbytes).hexdigest(),
        "position_fingerprint": oh,
        "position_accessors": on,
        "node_hierarchy_unchanged": True,
        "mesh_topology_unchanged": True,
        "original_binary_prefix_unchanged": True,
        "eye_materials_textured": sorted(target_materials),
        "embedded_images": sorted(required_images),
        "geometry_changed": False,
    }
    print("V170_EYE_TEXTURE_AUDIT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
