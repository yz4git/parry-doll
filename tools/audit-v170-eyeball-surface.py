#!/usr/bin/env python3
"""Audit final v17.0 eye-texture-only GLB against the exact v17.0 source model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
HELPERS = os.path.join(HERE, "add-eye-textures-v170.py")


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True)
    p.add_argument("--patched", required=True)
    return p.parse_args()


def main():
    a = args()
    h = runpy.run_path(HELPERS, run_name="__v170_final_eye_audit_helpers__")
    odoc, obin, obytes = h["parse_glb"](a.original)
    pdoc, pbin, pbytes = h["parse_glb"](a.patched)

    oh, on = h["position_fingerprint"](odoc, obin)
    ph, pn = h["position_fingerprint"](pdoc, pbin)
    if oh != ph or on != pn:
        raise RuntimeError("POSITION fingerprint differs from v17.0")
    if odoc.get("nodes") != pdoc.get("nodes"):
        raise RuntimeError("node transforms/hierarchy differ from v17.0")
    if len(odoc.get("meshes", [])) != len(pdoc.get("meshes", [])):
        raise RuntimeError("mesh count differs from v17.0")
    if pbin[:len(obin)] != obin:
        raise RuntimeError("original v17.0 BIN prefix changed")

    final_mat_idx = next((i for i, m in enumerate(pdoc.get("materials", [])) if m.get("name") == "Eyeball Surface v17.0"), None)
    if final_mat_idx is None:
        raise RuntimeError("final eyeball surface material missing")
    image_names = {i.get("name") for i in pdoc.get("images", [])}
    if "PARRY_DOLL_EyeballSurfaceTexture_v170" not in image_names:
        raise RuntimeError("final eyeball texture image missing")

    eye_material_changes = []
    for mi, (om, pm) in enumerate(zip(odoc.get("meshes", []), pdoc.get("meshes", []))):
        if om.get("name") != pm.get("name"):
            raise RuntimeError(f"mesh name changed at {mi}")
        op = om.get("primitives", []); pp = pm.get("primitives", [])
        if len(op) != len(pp):
            raise RuntimeError(f"primitive count changed at {mi}")
        for pi, (a0, a1) in enumerate(zip(op, pp)):
            # Geometry shape/topology invariants. Added UV coordinates are permitted texture data only.
            if a0.get("indices") != a1.get("indices") or a0.get("mode") != a1.get("mode") or a0.get("targets") != a1.get("targets"):
                raise RuntimeError(f"topology changed at {mi}/{pi}")
            attrs0 = a0.get("attributes", {}); attrs1 = a1.get("attributes", {})
            for semantic, accessor in attrs0.items():
                if attrs1.get(semantic) != accessor:
                    raise RuntimeError(f"existing attribute {semantic} changed at {mi}/{pi}")
            for semantic in ("POSITION", "NORMAL", "TANGENT", "JOINTS_0", "WEIGHTS_0"):
                if attrs0.get(semantic) != attrs1.get(semantic):
                    raise RuntimeError(f"shape attribute {semantic} changed at {mi}/{pi}")
            if a0.get("material") != a1.get("material"):
                name = pm.get("name", "")
                if "EyeSclera" not in name and "ScleraGlobe" not in name:
                    raise RuntimeError(f"non-eyeball material changed at {mi}/{pi}: {name}")
                if a1.get("material") != final_mat_idx:
                    raise RuntimeError(f"eyeball did not receive final texture material at {mi}/{pi}")
                eye_material_changes.append(name)

    if len(eye_material_changes) != 2:
        raise RuntimeError(f"expected exactly 2 eyeball material changes, got {len(eye_material_changes)}: {eye_material_changes}")

    extras = pdoc.get("asset", {}).get("extras", {})
    if extras.get("parryDollModelPolicy") != "exact-v17.0-shape-eyeball-texture-only":
        raise RuntimeError("final model policy tag missing")

    result = {
        "geometry_changed": False,
        "position_fingerprint": oh,
        "position_accessors": on,
        "node_hierarchy_unchanged": True,
        "mesh_count_unchanged": True,
        "topology_unchanged": True,
        "original_binary_prefix_unchanged": True,
        "eyeball_material_changes": eye_material_changes,
        "texture": "PARRY_DOLL_EyeballSurfaceTexture_v170",
        "source_sha256": hashlib.sha256(obytes).hexdigest(),
        "patched_sha256": hashlib.sha256(pbytes).hexdigest(),
        "front_uv": extras.get("eyeballFrontUV"),
    }
    print("V170_FINAL_EYEBALL_AUDIT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
