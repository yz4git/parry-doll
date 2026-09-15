#!/usr/bin/env python3
"""Project only the existing v17.0 iris/pupil/highlight stack onto the donor face surface.

The exact v17.0 donor head sits ~20–30 mm in front of the legacy procedural eye-detail planes,
so moving those planes only to the old sclera globe still leaves them hidden behind the donor face.
The user explicitly allowed this one model correction.  This patch therefore:

- keeps the exact v17.0 head/body/sclera geometry unchanged,
- keeps every target eye-detail X/Y coordinate unchanged,
- changes only Z on existing IrisOuter/IrisInner/IrisRays/Pupil/EyeLight vertices,
- projects each existing vertex onto the visible HeadShellV140 surface plus a tiny layer clearance,
- adds no mesh, deletes no mesh, changes no topology, transform, hierarchy, or indices.

This is a depth-only correction for the already-existing iris stack, not a face-shape edit.
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

# Layer separation above the donor face in glTF +Z (face-forward) direction.
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
    fmt_size = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}.get(acc.get("componentType"))
    if fmt_size is None:
        raise RuntimeError(f"unsupported index component type {acc.get('componentType')}")
    fmt, size = fmt_size
    bv = doc["bufferViews"][acc["bufferView"]]
    stride = int(bv.get("byteStride", size))
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    return [struct.unpack_from("<" + fmt, binary, base + i * stride)[0] for i in range(acc["count"])]


def parent_map(doc):
    out = {}
    for pi, n in enumerate(doc.get("nodes", [])):
        for child in n.get("children", []):
            out[child] = pi
    return out


def assert_identity_chain_to_head(doc, node_index, parents):
    cur = node_index
    while cur is not None:
        n = doc["nodes"][cur]
        if n.get("name") == "BL_HEAD":
            return
        if n.get("translation") not in (None, [0.0, 0.0, 0.0]):
            raise RuntimeError(f"unexpected translation in eye/head chain: {n.get('name')}")
        if n.get("rotation") not in (None, [0.0, 0.0, 0.0, 1.0]):
            raise RuntimeError(f"unexpected rotation in eye/head chain: {n.get('name')}")
        if n.get("scale") not in (None, [1.0, 1.0, 1.0]):
            raise RuntimeError(f"unexpected scale in eye/head chain: {n.get('name')}")
        if "matrix" in n:
            raise RuntimeError(f"unexpected matrix in eye/head chain: {n.get('name')}")
        cur = parents.get(cur)
    raise RuntimeError("target is not under BL_HEAD")


def build_head_triangles(doc, binary):
    head_index = next((i for i, n in enumerate(doc.get("nodes", [])) if n.get("name") == "HeadShellV140"), None)
    if head_index is None:
        raise RuntimeError("HeadShellV140 missing")
    mesh_index = doc["nodes"][head_index].get("mesh")
    if mesh_index is None:
        raise RuntimeError("HeadShellV140 has no mesh")
    triangles = []
    head_positions = []
    for prim in doc["meshes"][mesh_index].get("primitives", []):
        if prim.get("mode", 4) != 4:
            raise RuntimeError("HeadShellV140 primitive is not TRIANGLES")
        pai = prim.get("attributes", {}).get("POSITION")
        iai = prim.get("indices")
        if pai is None or iai is None:
            raise RuntimeError("HeadShellV140 requires POSITION + indices")
        verts = positions(doc, binary, pai)
        inds = read_indices(doc, binary, iai)
        head_positions.extend(verts)
        if len(inds) % 3:
            raise RuntimeError("HeadShellV140 triangle index count is not divisible by 3")
        for k in range(0, len(inds), 3):
            a, b, c = verts[inds[k]], verts[inds[k + 1]], verts[inds[k + 2]]
            # Skip triangles whose XY projection is degenerate.
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            triangles.append((a, b, c, den,
                              min(a[0], b[0], c[0]), max(a[0], b[0], c[0]),
                              min(a[1], b[1], c[1]), max(a[1], b[1], c[1])))
    if len(triangles) < 1000:
        raise RuntimeError(f"unexpectedly few donor head triangles: {len(triangles)}")
    return head_index, triangles, head_positions


def surface_z(triangles, head_positions, x, y):
    candidates = []
    eps = 1e-7
    for a, b, c, den, minx, maxx, miny, maxy in triangles:
        if x < minx - eps or x > maxx + eps or y < miny - eps or y > maxy + eps:
            continue
        w1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / den
        w2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / den
        w3 = 1.0 - w1 - w2
        if w1 >= -eps and w2 >= -eps and w3 >= -eps:
            z = w1 * a[2] + w2 * b[2] + w3 * c[2]
            # The head is closed, so front/back surfaces overlap in XY. Face-forward is +Z.
            candidates.append(float(z))
    front = [z for z in candidates if z > 0.05]
    if front:
        return max(front), "triangle"

    # Defensive fallback for a point exactly outside a projected triangle seam.
    near = []
    for p in head_positions:
        if p[2] <= 0.05:
            continue
        dx, dy = p[0] - x, p[1] - y
        d2 = dx * dx + dy * dy
        near.append((d2, p[2]))
    near.sort(key=lambda q: q[0])
    if not near:
        raise RuntimeError(f"no donor face surface near ({x},{y})")
    use = near[:6]
    weights = [1.0 / (d + 1e-10) for d, _ in use]
    z = sum(w * pz for w, (_, pz) in zip(weights, use)) / sum(weights)
    return float(z), "nearest"


def write_projected_z(doc, binary, ai, triangles, head_positions, clearance):
    acc, base, stride = layout(doc, ai)
    before = []
    after_z = []
    methods = {"triangle": 0, "nearest": 0}
    for i in range(acc["count"]):
        off = base + i * stride
        x, y, z = struct.unpack_from("<fff", binary, off)
        before.append((x, y, z))
        face_z, method = surface_z(triangles, head_positions, x, y)
        methods[method] += 1
        new_z = face_z + clearance
        struct.pack_into("<fff", binary, off, x, y, float(new_z))
        after_z.append(float(new_z))
    if "min" in acc and len(acc["min"]) == 3:
        acc["min"][2] = min(after_z)
    if "max" in acc and len(acc["max"]) == 3:
        acc["max"][2] = max(after_z)
    return before, after_z, methods


def main():
    a = args()
    h = runpy.run_path(HELPER, run_name="__v170_depth_helpers__")
    doc, b0, _ = h["parse_glb"](a.input)
    doc = copy.deepcopy(doc)
    binary = bytearray(b0)

    parents = parent_map(doc)
    head_index, triangles, head_positions = build_head_triangles(doc, binary)
    assert_identity_chain_to_head(doc, head_index, parents)

    users = {}
    for mi, mesh in enumerate(doc.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is not None:
                users.setdefault(ai, []).append((mi, pi, mesh.get("name", "")))

    changed = {}
    changed_nodes = []
    for ni, node in enumerate(doc.get("nodes", [])):
        name = node.get("name", "")
        kind = kind_of(name)
        if kind is None:
            continue
        assert_identity_chain_to_head(doc, ni, parents)
        if node.get("translation") not in (None, [0.0, 0.0, 0.0]) or node.get("rotation") not in (None, [0.0, 0.0, 0.0, 1.0]) or node.get("scale") not in (None, [1.0, 1.0, 1.0]):
            raise RuntimeError(f"target eye-detail node transform is not identity: {name}")
        mi = node.get("mesh")
        if mi is None:
            raise RuntimeError(f"target eye-detail node has no mesh: {name}")
        for prim in doc["meshes"][mi].get("primitives", []):
            ai = prim.get("attributes", {}).get("POSITION")
            if ai is None:
                raise RuntimeError(f"target POSITION missing: {name}")
            if any(u[0] != mi for u in users.get(ai, [])):
                raise RuntimeError(f"target POSITION {ai} is shared outside {name}: {users.get(ai)}")
            if ai in changed:
                continue
            before, after_z, methods = write_projected_z(doc, binary, ai, triangles, head_positions, CLEARANCE[kind])
            deltas = [after_z[i] - before[i][2] for i in range(len(before))]
            if min(deltas) <= 0.010 or max(deltas) >= 0.050:
                raise RuntimeError(f"unexpected donor-surface depth correction for {name}: {min(deltas)}..{max(deltas)}")
            changed[ai] = {
                "node": name,
                "kind": kind,
                "vertices": len(before),
                "min_old_z": min(p[2] for p in before),
                "max_old_z": max(p[2] for p in before),
                "min_new_z": min(after_z),
                "max_new_z": max(after_z),
                "min_delta_z": min(deltas),
                "max_delta_z": max(deltas),
                "surface_methods": methods,
            }
        changed_nodes.append(name)

    if len(changed_nodes) != 2 * len(CLEARANCE):
        raise RuntimeError(f"expected {2 * len(CLEARANCE)} target nodes, got {len(changed_nodes)}")

    doc.setdefault("asset", {}).setdefault("extras", {}).update({
        "parryDollRevision": "v17.0-eye-texture-plus-donor-surface-iris-depth-fix",
        "parryDollGeometryPolicy": "only-existing-iris-pupil-highlight-POSITION-z-projected-to-HeadShellV140",
        "parryDollScleraGeometryChanged": False,
        "parryDollFaceGeometryChanged": False,
    })
    h["write_glb"](a.output, doc, bytes(binary))

    out = {
        "revision": "v17.0-eye-texture-plus-donor-surface-iris-depth-fix",
        "head_surface": "HeadShellV140",
        "head_triangles": len(triangles),
        "clearance": CLEARANCE,
        "changed_nodes": sorted(changed_nodes),
        "changed_position_accessors": {str(k): v for k, v in sorted(changed.items())},
        "changed_geometry_scope": "existing iris/pupil/highlight Z-depth only",
        "x_y_changed": False,
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
