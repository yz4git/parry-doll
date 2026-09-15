"""Diagnostic-only connected-component audit for the current freshly-generated heroine head.

This script may import the current shipping GLB because it never edits or re-exports it.  It reports
connected components inside HeadShellV140 so disconnected donor islands can be distinguished from
the actual David Onizaki head shell before the next fresh Blender rebuild.
"""
from __future__ import annotations

import json
import os
import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GLB = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def world_bounds(obj, vertex_indices):
    pts = [obj.matrix_world @ obj.data.vertices[i].co for i in vertex_indices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) * 0.5
    size = hi - lo
    return {
        "min": [round(float(v), 6) for v in lo],
        "max": [round(float(v), 6) for v in hi],
        "center": [round(float(v), 6) for v in center],
        "size": [round(float(v), 6) for v in size],
    }


def connected_components(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen = set(range(len(mesh.vertices)))
    components = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        comp = {seed}
        while stack:
            cur = stack.pop()
            for nxt in adjacency[cur]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    comp.add(nxt)
                    stack.append(nxt)
        components.append(comp)
    components.sort(key=len, reverse=True)
    return components


def main():
    if not os.path.isfile(GLB):
        raise RuntimeError("GLB missing: " + GLB)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=GLB)
    head = bpy.data.objects.get("HeadShellV140")
    if head is None or head.type != "MESH":
        raise RuntimeError("HeadShellV140 mesh missing")

    comps = connected_components(head.data)
    poly_component = {}
    for idx, comp in enumerate(comps):
        for v in comp:
            poly_component[v] = idx
    face_counts = [0] * len(comps)
    for poly in head.data.polygons:
        ids = {poly_component[v] for v in poly.vertices}
        if len(ids) == 1:
            face_counts[next(iter(ids))] += 1

    print("HEAD_COMPONENT_COUNT", len(comps))
    total_vertices = len(head.data.vertices)
    total_polys = len(head.data.polygons)
    records = []
    for idx, comp in enumerate(comps):
        rec = {
            "index": idx,
            "verts": len(comp),
            "polys": face_counts[idx],
            "vertex_ratio": round(len(comp) / max(1, total_vertices), 6),
            "poly_ratio": round(face_counts[idx] / max(1, total_polys), 6),
            "bounds": world_bounds(head, comp),
        }
        records.append(rec)
        print("HEAD_COMPONENT", json.dumps(rec, sort_keys=True))

    # Flag components that are small enough to be overlay/island candidates but still visually large.
    suspects = []
    for rec in records[1:]:
        sx, sy, sz = rec["bounds"]["size"]
        if rec["verts"] >= 3 and max(sx, sy, sz) >= 0.008:
            suspects.append(rec)
    print("HEAD_COMPONENT_SUSPECT_COUNT", len(suspects))
    for rec in suspects:
        print("HEAD_COMPONENT_SUSPECT", json.dumps(rec, sort_keys=True))

    summary = {
        "component_count": len(comps),
        "largest_vertices": len(comps[0]) if comps else 0,
        "largest_vertex_ratio": round(len(comps[0]) / max(1, total_vertices), 6) if comps else 0,
        "suspect_count": len(suspects),
        "head_vertices": total_vertices,
        "head_polygons": total_polys,
    }
    print("HEAD_COMPONENT_SUMMARY", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
