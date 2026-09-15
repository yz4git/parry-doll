"""Post-export audit for the v18.1 high-detail hair replacement.

The whole non-hair BL_HEAD subtree is immutable.  Hair is excluded solely by its dedicated
BL_HAIR_ASSET hierarchy, avoiding name-based false positives.
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
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def under(obj, ancestor_name):
    cur = obj
    while cur:
        if cur.name == ancestor_name:
            return True
        cur = cur.parent
    return False


def canonical_points(obj, digits=5):
    mw = obj.matrix_world
    return tuple(sorted({
        (
            round(float((mw @ v.co).x), digits),
            round(float((mw @ v.co).y), digits),
            round(float((mw @ v.co).z), digits),
        )
        for v in obj.data.vertices
    }))


def snapshot(path):
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    protected = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not under(obj, "BL_HEAD") or under(obj, "BL_HAIR_ASSET"):
            continue
        protected[obj.name] = {
            "points": canonical_points(obj),
            "parent": obj.parent.name if obj.parent else None,
        }
    hair = bpy.data.objects.get("HairPremiumV181")
    hair_info = None
    if hair and hair.type == "MESH":
        hair_info = {
            "vertices": len(hair.data.vertices),
            "polygons": len(hair.data.polygons),
            "triangles": sum(max(1, len(p.vertices) - 2) for p in hair.data.polygons),
            "parent": hair.parent.name if hair.parent else None,
        }
    old_donor = sorted(o.name for o in bpy.data.objects if o.name.startswith("HairDonorV180"))
    return protected, hair_info, old_donor


def main():
    a = parse_args()
    before, _, _ = snapshot(a.before)
    after, hair, old_donor = snapshot(a.after)

    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")
    missing = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    if missing:
        raise RuntimeError("FACE LOCK: protected objects removed: " + ", ".join(missing[:20]))
    if added:
        raise RuntimeError("FACE LOCK: protected objects added: " + ", ".join(added[:20]))

    changed = []
    hierarchy = []
    for name in sorted(before):
        if before[name]["points"] != after[name]["points"]:
            changed.append(name)
        if before[name]["parent"] != after[name]["parent"]:
            hierarchy.append(name)
    if changed:
        raise RuntimeError("FACE LOCK: protected geometry changed: " + ", ".join(changed[:20]))
    if hierarchy:
        raise RuntimeError("FACE LOCK: protected hierarchy changed: " + ", ".join(hierarchy[:20]))

    if not hair:
        raise RuntimeError("HAIR: HairPremiumV181 missing after export")
    if hair["parent"] != "BL_HAIR_ASSET":
        raise RuntimeError(f"HAIR: unexpected parent {hair['parent']}")
    if hair["triangles"] < 10000:
        raise RuntimeError(f"HAIR: detail gate failed ({hair['triangles']} triangles)")
    if hair["triangles"] > 120000:
        raise RuntimeError(f"HAIR: mobile budget exceeded ({hair['triangles']} triangles)")
    if old_donor:
        raise RuntimeError("HAIR: old v18.0 donor still present: " + ", ".join(old_donor))

    summary = {
        "revision": "v18.1",
        "protected_head_objects_checked": len(before),
        "head_unique_world_points": len(after["HeadShellV140"]["points"]),
        "face_unchanged": True,
        "old_v180_hair_removed": True,
        "hair": hair,
        "audit_space": "canonical world points rounded to 5 decimals",
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_PREMIUM_V181_AUDIT", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
