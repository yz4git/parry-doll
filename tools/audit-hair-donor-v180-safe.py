"""Safe post-export geometry audit for Hair Donor v18.0.

Protects the complete non-hair BL_HEAD subtree. It compares canonical world-space point clouds rather
than edge/polygon counts, because a Blender/glTF round-trip may triangulate an unchanged accessory
(such as an earring) differently while preserving its actual shape.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HAIR_NAME_TOKENS = (
    "hair", "fringe", "bang", "crown", "temporal", "temple", "ponytail", "pony",
    "wisp", "nape", "strand", "cascade", "profileeyeframe",
)
HAIR_EXACTISH_TOKENS = (
    "keyartbang", "herocrown", "heropony", "ponymass", "ponyfan", "ponyfoundation",
    "ponywing", "ponyrootband", "hairtiev", "hairtopcap", "hairrearshell", "temporalunder",
    "referencewisp", "profileswisp", "profilewisp", "templesweep", "templeribbon",
    "templefine", "templelayer", "crownlayer", "fringesurface", "fringefine",
    "eyerevealfringe", "earfrontwisp", "profilehairornament",
)
FACE_PREFIXES = (
    "headshell", "bl_eyelid", "eyelight", "iris", "pupil", "sclera", "outerlash",
    "upperlash", "lowerlid", "profilelash", "wrappedcanthuslash", "eyewetline",
    "innercanthus", "upperskinrim", "lowerskinrim", "brow", "beautymark", "upperlip",
    "lowerlip", "mouth", "nose", "earantihelix", "earconcha", "earhelix", "earlobefold",
    "eartragus", "earring", "davidonizaki",
)


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


def under_head(obj):
    cur = obj
    while cur:
        if cur.name == "BL_HEAD":
            return True
        cur = cur.parent
    return False


def material_is_hair(obj):
    mats = [m.name.lower() for m in getattr(obj.data, "materials", []) if m]
    return bool(mats) and all("hair" in name for name in mats)


def is_style(obj):
    if obj.type != "MESH":
        return False
    n = obj.name.lower()
    if n.startswith("hairdonorv180_"):
        return True
    if any(n.startswith(prefix) for prefix in FACE_PREFIXES):
        return False
    if any(token in n for token in HAIR_EXACTISH_TOKENS):
        return True
    if any(token in n for token in HAIR_NAME_TOKENS):
        return True
    return under_head(obj) and material_is_hair(obj)


def canonical_world_points(obj, digits=5):
    pts = set()
    mw = obj.matrix_world
    for v in obj.data.vertices:
        p = mw @ v.co
        pts.add((round(float(p.x), digits), round(float(p.y), digits), round(float(p.z), digits)))
    return tuple(sorted(pts))


def bounds(points):
    if not points:
        return None
    return (
        (min(p[0] for p in points), min(p[1] for p in points), min(p[2] for p in points)),
        (max(p[0] for p in points), max(p[1] for p in points), max(p[2] for p in points)),
    )


def snapshot(path):
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    protected = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not under_head(obj) or is_style(obj):
            continue
        pts = canonical_world_points(obj)
        protected[obj.name] = {
            "points": pts,
            "bounds": bounds(pts),
            "parent": obj.parent.name if obj.parent else None,
        }
    donors = sorted(o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("HairDonorV180_"))
    return protected, donors


def main():
    a = parse_args()
    before, _ = snapshot(a.before)
    after, donors = snapshot(a.after)
    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")

    missing = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    if missing:
        raise RuntimeError("FACE LOCK: protected head objects removed: " + ", ".join(missing))
    if added:
        raise RuntimeError("FACE LOCK: protected head objects unexpectedly added: " + ", ".join(added))

    changed = []
    parent_changed = []
    max_point_count_delta = 0
    for name in sorted(before):
        b = before[name]
        n = after[name]
        max_point_count_delta = max(max_point_count_delta, abs(len(b["points"]) - len(n["points"])))
        if b["points"] != n["points"]:
            changed.append(name)
        if b["parent"] != n["parent"]:
            parent_changed.append(name)

    if changed:
        preview = ", ".join(changed[:12])
        raise RuntimeError(f"FACE LOCK: protected world-space geometry changed: {preview}")
    if parent_changed:
        raise RuntimeError("FACE LOCK: protected hierarchy changed: " + ", ".join(parent_changed[:12]))
    if not donors:
        raise RuntimeError("HAIR: HairDonorV180 mesh missing after export")

    summary = {
        "revision": "v18.0-safe",
        "protected_head_objects_checked": len(before),
        "head_unique_world_points": len(after["HeadShellV140"]["points"]),
        "max_protected_unique_point_count_delta": max_point_count_delta,
        "donor_objects": donors,
        "face_unchanged": True,
        "audit_space": "canonical world points rounded to 5 decimals",
    }
    Path(a.report).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_DONOR_V180_SAFE_AUDIT", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
