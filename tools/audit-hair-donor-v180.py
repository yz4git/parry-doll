"""Targeted post-export audit for the v18.0 donor-hair replacement.

Compares the pre-hair shipping GLB with the exported result and fails if protected face geometry or
transforms changed. This is intentionally narrower than a full visual audit because the task is hair-only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

FACE_LOCK_TOKENS = (
    "headshell", "eye", "iris", "pupil", "sclera", "lid", "lash", "brow", "canthus",
    "wetline", "lip", "mouth", "beautymark", "ear", "nose", "facequad", "facedetail",
)


def argv_tail():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(argv_tail())


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def is_locked(obj):
    return obj.type == "MESH" and any(t in obj.name.lower() for t in FACE_LOCK_TOKENS)


def snap(path):
    reset_scene()
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    result = {}
    for obj in bpy.data.objects:
        if not is_locked(obj):
            continue
        result[obj.name] = {
            "verts": [tuple(float(c) for c in v.co) for v in obj.data.vertices],
            "edges": len(obj.data.edges),
            "polys": len(obj.data.polygons),
            "matrix": [float(c) for row in obj.matrix_world for c in row],
            "parent": obj.parent.name if obj.parent else None,
        }
    donors = sorted(o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("HairDonorV180_"))
    return result, donors


def max_abs_diff(a, b):
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


def flatten(verts):
    return [c for v in verts for c in v]


def main():
    args = parse_args()
    before, _ = snap(args.before)
    after, donors = snap(args.after)

    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("HeadShellV140 missing from before/after audit")
    missing = sorted(set(before) - set(after))
    added_locked = sorted(set(after) - set(before))
    if missing:
        raise RuntimeError("FACE LOCK: protected objects missing after hair export: " + ", ".join(missing))
    if added_locked:
        raise RuntimeError("FACE LOCK: unexpected protected objects added: " + ", ".join(added_locked))

    tolerance = 3e-6
    worst_vertex = 0.0
    worst_matrix = 0.0
    checked = 0
    for name in sorted(before):
        a = before[name]
        b = after[name]
        if len(a["verts"]) != len(b["verts"]) or a["edges"] != b["edges"] or a["polys"] != b["polys"]:
            raise RuntimeError(f"FACE LOCK: topology changed for {name}")
        if a["parent"] != b["parent"]:
            raise RuntimeError(f"FACE LOCK: parent changed for {name}: {a['parent']} -> {b['parent']}")
        vd = max_abs_diff(flatten(a["verts"]), flatten(b["verts"]))
        md = max_abs_diff(a["matrix"], b["matrix"])
        worst_vertex = max(worst_vertex, vd)
        worst_matrix = max(worst_matrix, md)
        if vd > tolerance:
            raise RuntimeError(f"FACE LOCK: vertex coordinates changed for {name}: {vd}")
        if md > tolerance:
            raise RuntimeError(f"FACE LOCK: transform changed for {name}: {md}")
        checked += 1

    if not donors:
        raise RuntimeError("v18.0 donor hair objects missing after export")

    summary = {
        "revision": "v18.0",
        "protected_face_objects_checked": checked,
        "head_vertices": len(after["HeadShellV140"]["verts"]),
        "head_polygons": after["HeadShellV140"]["polys"],
        "max_protected_vertex_delta": worst_vertex,
        "max_protected_matrix_delta": worst_matrix,
        "tolerance": tolerance,
        "donor_objects": donors,
        "face_unchanged": True,
    }
    Path(args.report).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_DONOR_V180_AUDIT", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
