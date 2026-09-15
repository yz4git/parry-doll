"""Read-only Blender inspection for a downloaded game character hair donor."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HAIR_WORDS = ("hair", "bang", "fringe", "pony", "tail", "strand", "lock", "braid")


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args(tail_args())


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def tri_count(obj):
    return sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)


def world_bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return {"min": list(lo), "max": list(hi), "center": list((lo + hi) * 0.5), "size": list(hi - lo)}


def import_model(path):
    suffix = path.suffix.lower()
    if suffix in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    else:
        raise RuntimeError(f"unsupported donor model: {path}")


def score(obj, mats):
    text = (obj.name + " " + " ".join(mats)).lower()
    value = sum(8 for w in HAIR_WORDS if w in obj.name.lower())
    value += sum(3 for w in HAIR_WORDS if w in text)
    # Hair in anime exports is often a separate skinned mesh with moderate-to-high triangle count.
    t = tri_count(obj)
    if 300 <= t <= 100000:
        value += 1
    return value


def main():
    a = args()
    path = Path(a.input).resolve()
    clear()
    import_model(path)
    rows = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        mats = [m.name for m in obj.data.materials if m]
        armatures = [m.object.name for m in obj.modifiers if m.type == "ARMATURE" and m.object]
        row = {
            "name": obj.name,
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "triangles": tri_count(obj),
            "materials": mats,
            "parent": obj.parent.name if obj.parent else None,
            "armatures": armatures,
            "bounds": world_bounds(obj),
        }
        row["hair_score"] = score(obj, mats)
        rows.append(row)
    rows.sort(key=lambda r: (-r["hair_score"], -r["triangles"], r["name"].lower()))
    report = {
        "source": str(path),
        "blender_version": bpy.app.version_string,
        "mesh_count": len(rows),
        "total_triangles": sum(r["triangles"] for r in rows),
        "hair_candidates": [r for r in rows if r["hair_score"] > 0],
        "meshes": rows,
    }
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("CHARACTER_HAIR_DONOR_INSPECT", json.dumps({
        "source": str(path),
        "mesh_count": len(rows),
        "total_triangles": report["total_triangles"],
        "hair_candidates": [(r["name"], r["triangles"], r["materials"]) for r in report["hair_candidates"][:12]],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
