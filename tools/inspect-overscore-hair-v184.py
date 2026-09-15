"""Inspect OverScore Proxy 1.5 CC0 Blender file for modular bang/ponytail hair parts."""
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


def mesh_stats(obj):
    tris = sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons) if obj.type == "MESH" else None
    mats = [m.name for m in getattr(obj.data, "materials", []) if m] if obj.type == "MESH" else []
    return {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "vertices": len(obj.data.vertices) if obj.type == "MESH" else None,
        "polygons": len(obj.data.polygons) if obj.type == "MESH" else None,
        "triangles": tris,
        "materials": mats,
        "collections": [c.name for c in obj.users_collection],
    }


def main():
    a = parse_args()
    bpy.ops.wm.open_mainfile(filepath=str(Path(a.input).resolve()))
    keywords = ("hair", "bang", "fringe", "ponytail", "pony", "curtain", "peek", "layer")
    objects = [mesh_stats(o) for o in bpy.data.objects if any(k in o.name.lower() for k in keywords)]
    collections = []
    for c in bpy.data.collections:
        if any(k in c.name.lower() for k in keywords):
            collections.append({
                "name": c.name,
                "objects": [o.name for o in c.all_objects],
            })
    report = {
        "source": str(Path(a.input).resolve()),
        "blender_version": bpy.app.version_string,
        "hair_objects": sorted(objects, key=lambda x: x["name"].lower()),
        "hair_collections": sorted(collections, key=lambda x: x["name"].lower()),
    }
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OVERSCORE_HAIR_V184_INSPECT", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
