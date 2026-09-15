"""Bake the CC0 Blender-chan hairstyle into standalone static game geometry.

The donor's heavy Geometry Nodes hair is evaluated in-place, then copied as plain mesh geometry.
Only Hair Main, Hair Bun, and Hair Rigged are exported; donor head/body/eyebrows/tail never leave
this extraction step. Static appearance is intentionally prioritized over donor rig/dynamics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SOURCE_NAMES = ("Hair Main", "Hair Bun", "Hair Rigged")
OUTPUT_NAMES = {
    "Hair Main": "BC_HairMain",
    "Hair Bun": "BC_HairBun",
    "Hair Rigged": "BC_HairRigged",
}


def tail_args():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def tri_count(mesh):
    return sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)


def world_bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def vec(v):
    return [float(v.x), float(v.y), float(v.z)]


def main():
    a = parse_args()
    src = Path(a.input).resolve()
    out = Path(a.output).resolve()
    report_path = Path(a.report).resolve()
    if not src.is_file():
        raise RuntimeError(f"missing Blender-chan source: {src}")

    bpy.ops.wm.open_mainfile(filepath=str(src), load_ui=False)
    deps = bpy.context.evaluated_depsgraph_get()
    extracted = []
    rows = []

    for source_name in SOURCE_NAMES:
        obj = bpy.data.objects.get(source_name)
        if obj is None or obj.type != "MESH":
            raise RuntimeError(f"required Blender-chan hair object missing: {source_name}")
        evaluated = obj.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
        if not mesh.vertices or not mesh.polygons:
            raise RuntimeError(f"evaluated donor hair is empty: {source_name}")
        baked = bpy.data.objects.new(OUTPUT_NAMES[source_name], mesh)
        bpy.context.scene.collection.objects.link(baked)
        baked.matrix_world = evaluated.matrix_world.copy()
        extracted.append(baked)
        lo, hi, center, size = world_bounds(baked)
        rows.append({
            "source_name": source_name,
            "output_name": baked.name,
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "triangles": tri_count(mesh),
            "bounds": {"min": vec(lo), "max": vec(hi), "center": vec(center), "size": vec(size)},
        })

    # Delete every donor object except our evaluated static copies. This is a hard content boundary:
    # no donor face, body, eyebrow, armature, tail, animation, or helper can be exported by mistake.
    keep = set(extracted)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in extracted:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = extracted[0]

    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_animations=False,
    )
    summary = {
        "revision": "v18.2-donor-extract",
        "source": "Blender-chan: Free Blender character",
        "author": "Amarillo",
        "license": "CC0",
        "source_url": "https://amarilloarts.itch.io/blender-chan",
        "objects": rows,
        "triangles_total": sum(r["triangles"] for r in rows),
        "output_bytes": out.stat().st_size,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BLENDERCHAN_HAIR_V182_EXTRACT", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
