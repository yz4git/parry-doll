#!/usr/bin/env python3
"""Move only the existing v17.0 iris/pupil/highlight stack in front of the sclera globe.

The user explicitly allowed this single model correction after restoring v17.0: the original
iris geometry sits about 1 mm *inside* the eyeball sphere, so it is occluded even when textured.
This patcher keeps the exact v17.0 mesh shapes, X/Y coordinates, node transforms, hierarchy,
indices and topology.  It changes only the Z coordinate of the already-existing eye-detail
POSITION accessors so the stack clears the original sclera surface by sub-millimetre offsets.

Blender face-forward -Y is glTF +Z in this exported asset, therefore positive Z is outward.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import runpy
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(HERE, "add-eye-textures-v170.py")

# Clearance from the original sclera front surface in metres / Blender units.
# Keep the layers very close to the sphere so profile silhouette is unchanged.
CLEARANCE = {
    "IrisOuterV167": 0.00018,
    "IrisInnerV167": 0.00030,
    "IrisRaysV167": 0.00040,
    "PupilV167": 0.00052,
    "EyeLightV167A": 0.00064,
    "EyeLightV167B": 0.00062,
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest")
    return p.parse_args()


def node_side(name: str) -> int:
    if name.endswith("_-1"):
        return -1
    if name.endswith("_1"):
        return 1
    raise RuntimeError(f"cannot resolve eye side from node name: {name}")


def target_kind(name: str):
    for prefix in CLEARANCE:
        if name.startswith(prefix + "_"):
            return prefix
    return None


def accessor_layout(doc, accessor_index):
    acc = doc["accessors"][accessor_index]
    if acc.get("componentType") != 5126 or acc.get("type") != "VEC3":
        raise RuntimeError(f"POSITION accessor {accessor_index} is not FLOAT VEC3")
    if "bufferView" not in acc:
        raise RuntimeError(f"POSITION accessor {accessor_index} has no bufferView")
    bv = doc["bufferViews"][acc["bufferView"]]
    stride = int(bv.get("byteStride", 12))
    if stride < 12:
        raise RuntimeError(f"unexpected POSITION stride {stride}")
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    return acc, bv, base, stride


def read_positions(doc, binary, accessor_index):
    acc, _bv, base, stride = accessor_layout(doc, accessor_index)
    return [struct.unpack_from("<fff", binary, base + i * stride) for i in range(acc["count"])]


def write_uniform_z(doc, binary: bytearray, accessor_index: int, desired_z: float):
    acc, _bv, base, stride = accessor_layout(doc, accessor_index)
    before = []
    for i in range(acc["count"]):
        off = base + i * stride
        x, y, z = struct.unpack_from("<fff", binary, off)
        before.append((x, y, z))
        struct.pack_into("<fff", binary, off, x, y, float(desired_z))
    if "min" in acc and len(acc["min"]) == 3:
        acc["min"][2] = float(desired_z)
    if "max" in acc and len(acc["max"]) == 3:
        acc["max"][2] = float(desired_z)
    return before


def main():
    a = parse_args()
    h = runpy.run_path(HELPER, run_name="__v170_iris_lift_helpers__")
    doc, binary_bytes, _original = h["parse_glb"](a.input)
    doc = copy.deepcopy(doc)
    binary = bytearray(binary_bytes)

    # Resolve the actual front surface of both untouched v17.0 sclera globes.
    sclera_front = {}
    for node in doc.get("nodes", []):
        name = node.get("name", "")
        if not name.startswith("EyeScleraGlobeV166_"):
            continue
        side = node_side(name)
        mesh_index = node.get("mesh")
        if mesh_index is None:
            raise RuntimeError(f"sclera node has no mesh: {name}")
        prims = doc["meshes"][mesh_index].get("primitives", [])
        if len(prims) != 1:
            raise RuntimeError(f"unexpected sclera primitive count for {name}: {len(prims)}")
        pos_index = prims[0].get("attributes", {}).get("POSITION")
        if pos_index is None:
            raise RuntimeError(f"sclera POSITION missing: {name}")
        local = read_positions(doc, binary, pos_index)
        translation = node.get("translation", [0.0, 0.0, 0.0])
        scale = node.get("scale", [1.0, 1.0, 1.0])
        if node.get("rotation") not in (None, [0.0, 0.0, 0.0, 1.0]):
            raise RuntimeError(f"unexpected sclera rotation on {name}; refuse unsafe depth patch")
        front = float(translation[2]) + max(float(p[2]) * float(scale[2]) for p in local)
        sclera_front[side] = front
    if set(sclera_front) != {-1, 1}:
        raise RuntimeError(f"expected two sclera globes, got {sclera_front}")

    # POSITION accessors must not be shared with unrelated meshes.  Refuse to patch if they are.
    position_users = {}
    for mi, mesh in enumerate(doc.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is not None:
                position_users.setdefault(ai, []).append((mi, pi, mesh.get("name", "")))

    changed_accessors = {}
    changed_nodes = []
    for node in doc.get("nodes", []):
        name = node.get("name", "")
        kind = target_kind(name)
        if kind is None:
            continue
        side = node_side(name)
        mesh_index = node.get("mesh")
        if mesh_index is None:
            raise RuntimeError(f"target node has no mesh: {name}")
        mesh = doc["meshes"][mesh_index]
        desired_z = sclera_front[side] + CLEARANCE[kind]
        for pi, prim in enumerate(mesh.get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is None:
                raise RuntimeError(f"target primitive POSITION missing: {name} primitive {pi}")
            users = position_users.get(ai, [])
            if any(u[0] != mesh_index for u in users):
                raise RuntimeError(f"target POSITION accessor {ai} is shared outside {name}: {users}")
            if ai in changed_accessors:
                # Iris rays can have multiple material primitives sharing one POSITION accessor.
                prev = changed_accessors[ai]
                if abs(prev["desired_z"] - desired_z) > 1e-9:
                    raise RuntimeError(f"conflicting target Z for shared accessor {ai}")
                continue
            before = write_uniform_z(doc, binary, ai, desired_z)
            old_min = min(p[2] for p in before)
            old_max = max(p[2] for p in before)
            if abs(old_max - old_min) > 1e-6:
                raise RuntimeError(f"eye detail accessor {ai} is not planar in Z; refuse shape-changing patch")
            changed_accessors[ai] = {
                "node": name,
                "kind": kind,
                "side": side,
                "old_z": float((old_min + old_max) * 0.5),
                "desired_z": float(desired_z),
                "delta_z": float(desired_z - (old_min + old_max) * 0.5),
                "vertices": len(before),
            }
        changed_nodes.append(name)

    expected_nodes = 2 * len(CLEARANCE)
    if len(changed_nodes) != expected_nodes:
        raise RuntimeError(f"expected {expected_nodes} eye-detail nodes, changed {len(changed_nodes)}: {changed_nodes}")

    # Record intent in asset metadata only; no node transform/hierarchy changes are made.
    asset = doc.setdefault("asset", {})
    extras = asset.setdefault("extras", {})
    extras["parryDollRevision"] = "v17.0-eye-texture-plus-iris-depth-fix"
    extras["parryDollGeometryPolicy"] = "only-existing-iris-pupil-highlight-POSITION-z-changed"
    extras["parryDollScleraGeometryChanged"] = False

    h["write_glb"](a.output, doc, bytes(binary))

    manifest = {
        "revision": "v17.0-eye-texture-plus-iris-depth-fix",
        "face_forward_gltf_axis": "+Z",
        "sclera_front_z": {str(k): v for k, v in sorted(sclera_front.items())},
        "clearance": CLEARANCE,
        "changed_nodes": sorted(changed_nodes),
        "changed_position_accessors": {str(k): v for k, v in sorted(changed_accessors.items())},
        "changed_geometry_scope": "existing iris/pupil/highlight depth only",
        "topology_changed": False,
        "node_transforms_changed": False,
        "sclera_geometry_changed": False,
        "output_bytes": os.path.getsize(a.output),
    }
    print("V170_IRIS_DEPTH_FIX", json.dumps(manifest, sort_keys=True))
    if a.manifest:
        with open(a.manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
