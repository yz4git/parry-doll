#!/usr/bin/env python3
"""Move only the existing v17.0 iris/pupil/highlight stack to the visible eye surface.

The exact v17.0 donor-head build has two separate depth problems:
1) the original iris planes are about 1 mm inside the sclera sphere, and
2) the David Onizaki donor head is a closed face surface whose eye-region front sits farther
   forward than that hidden eyeball sphere.

The user explicitly allowed only the model correction required for the buried iris.  Therefore
this patch keeps the exact v17.0 head/body/sclera shapes, X/Y coordinates, node transforms,
hierarchy, indices and topology.  It changes only the Z coordinate of the already-existing
IrisOuter/IrisInner/IrisRays/Pupil/EyeLight POSITION accessors.  Their plane is moved as a rigid
surface to just clear the donor eye-region skin; no vertex is resized or reshaped.

Blender face-forward -Y becomes glTF +Z in this asset, therefore positive Z is outward.
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

# Layer spacing above the sampled donor eye-region surface.  These are deliberately sub-millimetre
# so the correction reads as the original v17.0 iris, not a new protruding eye model.
CLEARANCE = {
    "IrisOuterV167": 0.00010,
    "IrisInnerV167": 0.00020,
    "IrisRaysV167": 0.00030,
    "PupilV167": 0.00042,
    "EyeLightV167A": 0.00054,
    "EyeLightV167B": 0.00052,
}
SURFACE_PERCENTILE = 0.95


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


def percentile(values, q):
    vals = sorted(float(v) for v in values)
    if not vals:
        raise RuntimeError("percentile on empty values")
    idx = int(round(max(0.0, min(1.0, q)) * (len(vals) - 1)))
    return vals[idx]


def mesh_positions(doc, binary, mesh_index):
    out = []
    for prim in doc["meshes"][mesh_index].get("primitives", []):
        ai = prim.get("attributes", {}).get("POSITION")
        if ai is not None:
            out.extend(read_positions(doc, binary, ai))
    return out


def main():
    a = parse_args()
    h = runpy.run_path(HELPER, run_name="__v170_iris_lift_helpers__")
    doc, binary_bytes, _original = h["parse_glb"](a.input)
    doc = copy.deepcopy(doc)
    binary = bytearray(binary_bytes)

    nodes = doc.get("nodes", [])
    by_name = {n.get("name", ""): n for n in nodes}

    # Original hidden sclera-front depth, retained only as a safety lower bound / diagnostic.
    sclera_front = {}
    for node in nodes:
        name = node.get("name", "")
        if not name.startswith("EyeScleraGlobeV166_"):
            continue
        side = node_side(name)
        mesh_index = node.get("mesh")
        prims = doc["meshes"][mesh_index].get("primitives", [])
        if len(prims) != 1:
            raise RuntimeError(f"unexpected sclera primitive count for {name}: {len(prims)}")
        local = read_positions(doc, binary, prims[0]["attributes"]["POSITION"])
        translation = node.get("translation", [0.0, 0.0, 0.0])
        scale = node.get("scale", [1.0, 1.0, 1.0])
        if node.get("rotation") not in (None, [0.0, 0.0, 0.0, 1.0]):
            raise RuntimeError(f"unexpected sclera rotation on {name}")
        sclera_front[side] = float(translation[2]) + max(float(p[2]) * float(scale[2]) for p in local)
    if set(sclera_front) != {-1, 1}:
        raise RuntimeError(f"expected two sclera globes, got {sclera_front}")

    # Resolve the v17.0 donor head front surface around each original iris XY footprint.  The donor
    # face is closed in front of the hidden sphere, which is why clearing only sclera depth was still
    # invisible in the high-res audit.  We do not edit this head mesh; it is only sampled.
    head_node = by_name.get("HeadShellV140")
    if not head_node or "mesh" not in head_node:
        raise RuntimeError("HeadShellV140 donor head missing")
    if head_node.get("rotation") not in (None, [0.0, 0.0, 0.0, 1.0]) or head_node.get("scale") not in (None, [1.0, 1.0, 1.0]):
        raise RuntimeError("unexpected HeadShellV140 transform; refuse unsafe depth patch")
    head_translation = head_node.get("translation", [0.0, 0.0, 0.0])
    head_positions = [
        (p[0] + head_translation[0], p[1] + head_translation[1], p[2] + head_translation[2])
        for p in mesh_positions(doc, binary, head_node["mesh"])
    ]

    iris_surface = {}
    iris_footprint = {}
    for side in (-1, 1):
        outer = by_name.get(f"IrisOuterV167_{side}")
        if not outer or "mesh" not in outer:
            raise RuntimeError(f"IrisOuterV167_{side} missing")
        pts = mesh_positions(doc, binary, outer["mesh"])
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        rx = max((max(xs) - min(xs)) * 0.5, 1e-6) * 1.10
        ry = max((max(ys) - min(ys)) * 0.5, 1e-6) * 1.15
        front_samples = []
        for x, y, z in head_positions:
            if z <= 0.0:
                continue  # ignore the closed back-of-head surface
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                front_samples.append(z)
        if len(front_samples) < 8:
            raise RuntimeError(f"too few donor eye-surface samples on side {side}: {len(front_samples)}")
        sampled = percentile(front_samples, SURFACE_PERCENTILE)
        iris_surface[side] = max(sampled, sclera_front[side])
        iris_footprint[side] = {
            "center": [cx, cy], "radius": [rx, ry], "samples": len(front_samples),
            "sampled_head_front_z": sampled,
        }

    # POSITION accessors must not be shared with unrelated meshes.
    position_users = {}
    for mi, mesh in enumerate(doc.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is not None:
                position_users.setdefault(ai, []).append((mi, pi, mesh.get("name", "")))

    changed_accessors = {}
    changed_nodes = []
    for node in nodes:
        name = node.get("name", "")
        kind = target_kind(name)
        if kind is None:
            continue
        side = node_side(name)
        mesh_index = node.get("mesh")
        if mesh_index is None:
            raise RuntimeError(f"target node has no mesh: {name}")
        desired_z = iris_surface[side] + CLEARANCE[kind]
        for pi, prim in enumerate(doc["meshes"][mesh_index].get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is None:
                raise RuntimeError(f"target primitive POSITION missing: {name} primitive {pi}")
            users = position_users.get(ai, [])
            if any(u[0] != mesh_index for u in users):
                raise RuntimeError(f"target POSITION accessor {ai} is shared outside {name}: {users}")
            if ai in changed_accessors:
                prev = changed_accessors[ai]
                if abs(prev["desired_z"] - desired_z) > 1e-9:
                    raise RuntimeError(f"conflicting target Z for shared accessor {ai}")
                continue
            before = write_uniform_z(doc, binary, ai, desired_z)
            old_min = min(p[2] for p in before); old_max = max(p[2] for p in before)
            if abs(old_max - old_min) > 1e-6:
                raise RuntimeError(f"eye detail accessor {ai} is not planar in Z")
            changed_accessors[ai] = {
                "node": name, "kind": kind, "side": side,
                "old_z": float((old_min + old_max) * 0.5),
                "desired_z": float(desired_z),
                "delta_z": float(desired_z - (old_min + old_max) * 0.5),
                "vertices": len(before),
            }
        changed_nodes.append(name)

    expected_nodes = 2 * len(CLEARANCE)
    if len(changed_nodes) != expected_nodes:
        raise RuntimeError(f"expected {expected_nodes} eye-detail nodes, changed {len(changed_nodes)}")

    asset = doc.setdefault("asset", {})
    extras = asset.setdefault("extras", {})
    extras["parryDollRevision"] = "v17.0-eye-texture-plus-visible-iris-depth-fix"
    extras["parryDollGeometryPolicy"] = "only-existing-iris-pupil-highlight-POSITION-z-changed"
    extras["parryDollHeadGeometryChanged"] = False
    extras["parryDollScleraGeometryChanged"] = False

    h["write_glb"](a.output, doc, bytes(binary))
    manifest = {
        "revision": "v17.0-eye-texture-plus-visible-iris-depth-fix",
        "face_forward_gltf_axis": "+Z",
        "sclera_front_z": {str(k): v for k, v in sorted(sclera_front.items())},
        "sampled_donor_eye_surface_z": {str(k): v for k, v in sorted(iris_surface.items())},
        "iris_footprint": {str(k): v for k, v in sorted(iris_footprint.items())},
        "surface_percentile": SURFACE_PERCENTILE,
        "clearance": CLEARANCE,
        "changed_nodes": sorted(changed_nodes),
        "changed_position_accessors": {str(k): v for k, v in sorted(changed_accessors.items())},
        "changed_geometry_scope": "existing iris/pupil/highlight rigid depth only",
        "topology_changed": False,
        "node_transforms_changed": False,
        "head_geometry_changed": False,
        "sclera_geometry_changed": False,
        "output_bytes": os.path.getsize(a.output),
    }
    print("V170_VISIBLE_IRIS_DEPTH_FIX", json.dumps(manifest, sort_keys=True))
    if a.manifest:
        with open(a.manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
