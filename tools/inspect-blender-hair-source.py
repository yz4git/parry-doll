"""Inspect a donor .blend and print hair-related geometry/material/modifier metadata.

Read-only donor inspection. It never saves the source file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def tail_args():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args(tail_args())


def tri_count(mesh):
    return sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)


def evaluated_mesh_info(obj):
    if obj.type not in {"MESH", "CURVE", "CURVES"}:
        return None
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    try:
        mesh = bpy.data.meshes.new_from_object(ev, depsgraph=deps)
    except Exception as exc:
        return {"error": repr(exc)}
    try:
        return {
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "triangles": tri_count(mesh),
        }
    finally:
        bpy.data.meshes.remove(mesh)


def main():
    a = parse_args()
    src = Path(a.input).resolve()
    if not src.is_file():
        raise RuntimeError(f"missing donor: {src}")
    bpy.ops.wm.open_mainfile(filepath=str(src), load_ui=False)

    rows = []
    for obj in bpy.data.objects:
        n = obj.name.lower()
        mats = [m.name for m in getattr(obj.data, "materials", []) if m] if getattr(obj, "data", None) else []
        modifiers = [
            {
                "name": m.name,
                "type": m.type,
                "node_group": getattr(getattr(m, "node_group", None), "name", None),
            }
            for m in getattr(obj, "modifiers", [])
        ]
        hair_hint = (
            "hair" in n
            or "bang" in n
            or "fringe" in n
            or "ponytail" in n
            or "strand" in n
            or any("hair" in m.lower() for m in mats)
            or any("hair" in (m.get("name") or "").lower() for m in modifiers)
            or any("hair" in (m.get("node_group") or "").lower() for m in modifiers)
        )
        if not hair_hint:
            continue
        rows.append({
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "hidden_render": bool(obj.hide_render),
            "materials": mats,
            "modifiers": modifiers,
            "raw": {
                "vertices": len(obj.data.vertices) if obj.type == "MESH" else None,
                "polygons": len(obj.data.polygons) if obj.type == "MESH" else None,
                "triangles": tri_count(obj.data) if obj.type == "MESH" else None,
            },
            "evaluated": evaluated_mesh_info(obj),
        })

    summary = {
        "source": str(src),
        "blender_version": bpy.app.version_string,
        "objects_total": len(bpy.data.objects),
        "hair_candidates": rows,
        "materials_with_hair": sorted(m.name for m in bpy.data.materials if "hair" in m.name.lower()),
        "node_groups_with_hair": sorted(g.name for g in bpy.data.node_groups if "hair" in g.name.lower()),
    }
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DONOR_HAIR_INSPECT", json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
