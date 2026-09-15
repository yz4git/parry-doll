#!/usr/bin/env python3
"""Rigidly move only the existing v17.0 iris stack to the visible donor eye surface.

The shipping model is restored from exact v17.0 before this runs.  The David Onizaki donor head
sits substantially farther forward than the legacy procedural iris planes, so a ~1 mm lift from
the old sclera sphere is not enough to make the existing iris visible.  This is still kept within
the user's allowed correction: the already-existing iris/pupil/highlight geometry may be corrected
for depth, but its shape must not change.

Policy enforced here:
- Head/body/sclera geometry stays byte/numerically unchanged.
- Existing IrisOuter/IrisInner/IrisRays/Pupil/EyeLight shapes stay planar and unchanged.
- X/Y coordinates stay exact v17.0.
- Every affected POSITION accessor receives one *uniform* Z translation only.
- Target depth is the HeadShellV140 surface at the centre of the corresponding existing iris,
  plus a sub-millimetre layer clearance.
- No mesh, topology, indices, hierarchy, or node transform is added/removed/changed.

This is a rigid donor eye-surface depth correction, not a face-shape edit.
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

CLEARANCE = {
    "IrisOuterV167": 0.00018,
    "IrisInnerV167": 0.00030,
    "IrisRaysV167": 0.00040,
    "PupilV167": 0.00052,
    "EyeLightV167A": 0.00064,
    "EyeLightV167B": 0.00062,
}


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest")
    return p.parse_args()


def side_of(name: str) -> int:
    if name.endswith("_-1"):
        return -1
    if name.endswith("_1"):
        return 1
    raise RuntimeError("cannot resolve side from " + name)


def kind_of(name: str):
    for k in CLEARANCE:
        if name.startswith(k + "_"):
            return k
    return None


def layout(doc, ai):
    acc = doc["accessors"][ai]
    if acc.get("componentType") != 5126 or acc.get("type") != "VEC3" or "bufferView" not in acc:
        raise RuntimeError(f"bad POSITION accessor {ai}")
    bv = doc["bufferViews"][acc["bufferView"]]
    stride = int(bv.get("byteStride", 12))
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    if stride < 12:
        raise RuntimeError(f"unexpected POSITION stride {stride}")
    return acc, base, stride


def positions(doc, binary, ai):
    acc, base, stride = layout(doc, ai)
    return [struct.unpack_from("<fff", binary, base + i * stride) for i in range(acc["count"])]


def read_indices(doc, binary, ai):
    acc = doc["accessors"][ai]
    if acc.get("type") != "SCALAR" or "bufferView" not in acc:
        raise RuntimeError(f"bad index accessor {ai}")
    fs = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}.get(acc.get("componentType"))
    if fs is None:
        raise RuntimeError(f"unsupported index component type {acc.get('componentType')}")
    fmt, size = fs
    bv = doc["bufferViews"][acc["bufferView"]]
    stride = int(bv.get("byteStride", size))
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    return [struct.unpack_from("<" + fmt, binary, base + i * stride)[0] for i in range(acc["count"])]


def write_uniform_z(doc, binary: bytearray, ai: int, desired_z: float):
    acc, base, stride = layout(doc, ai)
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


def build_head_triangles(doc, binary):
    head_node = next((n for n in doc.get("nodes", []) if n.get("name") == "HeadShellV140"), None)
    if head_node is None or "mesh" not in head_node:
        raise RuntimeError("HeadShellV140 mesh missing")
    tris = []
    for prim in doc["meshes"][head_node["mesh"]].get("primitives", []):
        if prim.get("mode", 4) != 4:
            raise RuntimeError("HeadShellV140 must use TRIANGLES")
        pai = prim.get("attributes", {}).get("POSITION")
        iai = prim.get("indices")
        if pai is None or iai is None:
            raise RuntimeError("HeadShellV140 requires POSITION and indices")
        verts = positions(doc, binary, pai)
        inds = read_indices(doc, binary, iai)
        if len(inds) % 3:
            raise RuntimeError("HeadShellV140 indices not divisible by three")
        for k in range(0, len(inds), 3):
            a, b, c = verts[inds[k]], verts[inds[k + 1]], verts[inds[k + 2]]
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            tris.append((
                a, b, c, den,
                min(a[0], b[0], c[0]), max(a[0], b[0], c[0]),
                min(a[1], b[1], c[1]), max(a[1], b[1], c[1]),
            ))
    if len(tris) < 1000:
        raise RuntimeError(f"unexpectedly few donor head triangles: {len(tris)}")
    return tris


def surface_z_at(tris, x: float, y: float) -> float:
    eps = 1e-7
    candidates = []
    for a, b, c, den, minx, maxx, miny, maxy in tris:
        if x < minx - eps or x > maxx + eps or y < miny - eps or y > maxy + eps:
            continue
        w1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / den
        w2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / den
        w3 = 1.0 - w1 - w2
        if w1 >= -eps and w2 >= -eps and w3 >= -eps:
            z = w1 * a[2] + w2 * b[2] + w3 * c[2]
            if z > 0.05:  # +Z is face-forward; reject the closed head's rear surface.
                candidates.append(float(z))
    if not candidates:
        raise RuntimeError(f"no visible HeadShellV140 surface at iris centre ({x:.6f},{y:.6f})")
    return max(candidates)


def main():
    a = args()
    h = runpy.run_path(HELPER, run_name="__v170_rigid_depth_helpers__")
    doc, b0, _ = h["parse_glb"](a.input)
    doc = copy.deepcopy(doc)
    binary = bytearray(b0)

    head_tris = build_head_triangles(doc, binary)

    # Determine one visible donor-face depth per eye from the centre of the *existing* IrisOuter.
    eye_surface = {}
    for n in doc.get("nodes", []):
        name = n.get("name", "")
        if not name.startswith("IrisOuterV167_"):
            continue
        side = side_of(name)
        mi = n.get("mesh")
        if mi is None:
            raise RuntimeError(f"IrisOuter node has no mesh: {name}")
        prims = doc["meshes"][mi].get("primitives", [])
        if len(prims) != 1:
            raise RuntimeError(f"unexpected IrisOuter primitive count: {name}")
        vals = positions(doc, binary, prims[0]["attributes"]["POSITION"])
        cx = sum(p[0] for p in vals) / len(vals)
        cy = sum(p[1] for p in vals) / len(vals)
        eye_surface[side] = {
            "center_x": float(cx),
            "center_y": float(cy),
            "surface_z": float(surface_z_at(head_tris, cx, cy)),
        }
    if set(eye_surface) != {-1, 1}:
        raise RuntimeError(f"expected two iris centres, got {eye_surface}")

    users = {}
    for mi, mesh in enumerate(doc.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is not None:
                users.setdefault(ai, []).append((mi, pi, mesh.get("name", "")))

    changed = {}
    changed_nodes = []
    for n in doc.get("nodes", []):
        name = n.get("name", "")
        kind = kind_of(name)
        if kind is None:
            continue
        side = side_of(name)
        mi = n.get("mesh")
        if mi is None:
            raise RuntimeError(f"target eye-detail node has no mesh: {name}")
        desired = eye_surface[side]["surface_z"] + CLEARANCE[kind]
        for prim in doc["meshes"][mi].get("primitives", []):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is None:
                raise RuntimeError(f"target POSITION missing: {name}")
            if any(u[0] != mi for u in users.get(ai, [])):
                raise RuntimeError(f"target POSITION accessor {ai} is shared outside {name}: {users.get(ai)}")
            if ai in changed:
                continue
            before = write_uniform_z(doc, binary, ai, desired)
            zs = [p[2] for p in before]
            if max(zs) - min(zs) > 1e-6:
                raise RuntimeError(f"existing eye-detail mesh is not planar; refuse shape change: {name} accessor {ai}")
            old = sum(zs) / len(zs)
            delta = desired - old
            if delta <= 0.010 or delta >= 0.050:
                raise RuntimeError(f"unexpected rigid donor-surface depth correction for {name}: {delta}")
            changed[ai] = {
                "node": name,
                "kind": kind,
                "side": side,
                "old_z": float(old),
                "desired_z": float(desired),
                "delta_z": float(delta),
                "vertices": len(before),
            }
        changed_nodes.append(name)

    if len(changed_nodes) != 2 * len(CLEARANCE):
        raise RuntimeError(f"expected {2 * len(CLEARANCE)} target nodes, got {len(changed_nodes)}")

    doc.setdefault("asset", {}).setdefault("extras", {}).update({
        "parryDollRevision": "v17.0-eye-texture-plus-rigid-donor-eye-depth-fix",
        "parryDollGeometryPolicy": "only-existing-iris-pupil-highlight-POSITION-z-rigidly-translated",
        "parryDollScleraGeometryChanged": False,
        "parryDollFaceGeometryChanged": False,
        "parryDollEyeDetailShapeChanged": False,
    })
    h["write_glb"](a.output, doc, bytes(binary))

    out = {
        "revision": "v17.0-eye-texture-plus-rigid-donor-eye-depth-fix",
        "eye_surface": {str(k): v for k, v in sorted(eye_surface.items())},
        "clearance": CLEARANCE,
        "changed_nodes": sorted(changed_nodes),
        "changed_position_accessors": {str(k): v for k, v in sorted(changed.items())},
        "changed_geometry_scope": "existing iris/pupil/highlight rigid Z translation only",
        "x_y_changed": False,
        "eye_detail_shape_changed": False,
        "topology_changed": False,
        "node_transforms_changed": False,
        "sclera_geometry_changed": False,
        "face_geometry_changed": False,
        "output_bytes": os.path.getsize(a.output),
    }
    print("V170_IRIS_DEPTH_FIX", json.dumps(out, sort_keys=True))
    if a.manifest:
        with open(a.manifest, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
