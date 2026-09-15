"""Post-export audit for Parry Doll hybrid anime high-ponytail hair v18.3."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

HAIR_MARKERS = (
    "hairdonor", "hairpremium", "hairrear", "hairtop", "herohair", "heropony", "herocrown",
    "ponymass", "ponyfan", "ponyfoundation", "ponywing", "ponyroot", "ponytail", "hairtie",
    "fringe", "bang", "crown", "temporal", "temple", "nape", "wisp", "strand", "lock",
    "cascade", "profileeyeframe", "profilehairornament", "referencewisp", "eyerevealfringe",
    "earfrontwisp", "bl_pony_dynamic",
)
FACE_MARKERS = (
    "headshell", "davidonizaki", "eyelid", "eyelight", "iris", "pupil", "sclera", "wetline",
    "lash", "canthus", "brow", "skinrim", "beautymark", "nose", "lip", "mouth",
    "earantihelix", "earconcha", "earhelix", "earlobefold", "eartragus", "earring",
)
PREFIX = "HairPremiumV183_"
REQUIRED = {"HairPremiumV183_Main", "HairPremiumV183_Detail", "HairPremiumV183_Tail"}


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


def hair_name(obj):
    n = obj.name.lower()
    return any(token in n for token in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(token in n for token in HAIR_MARKERS):
        return False
    return any(token in n for token in FACE_MARKERS)


def protected(obj):
    if obj.type != "MESH":
        return False
    if face_name(obj):
        return True
    return under(obj, "BL_HEAD") and not hair_name(obj)


def points(obj, digits=5):
    mw = obj.matrix_world
    return tuple(sorted({
        (
            round(float((mw @ v.co).x), digits),
            round(float((mw @ v.co).y), digits),
            round(float((mw @ v.co).z), digits),
        )
        for v in obj.data.vertices
    }))


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def snapshot(path):
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    protected_rows = {}
    for obj in bpy.data.objects:
        if protected(obj):
            protected_rows[obj.name] = {
                "points": points(obj),
                "parent": obj.parent.name if obj.parent else None,
                "vertices": len(obj.data.vertices),
            }
    hair = {}
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name.startswith(PREFIX):
            hair[obj.name] = {
                "triangles": tri_count(obj),
                "vertices": len(obj.data.vertices),
                "parent": obj.parent.name if obj.parent else None,
            }
    old = sorted(
        obj.name for obj in bpy.data.objects
        if obj.type == "MESH" and (
            obj.name.startswith("HairDonorV180")
            or obj.name.startswith("HairPremiumV181")
            or obj.name.startswith("HairPremiumV182")
            or (under(obj, "BL_HAIR_ASSET") and hair_name(obj) and not obj.name.startswith(PREFIX))
        )
    )
    return protected_rows, hair, old


def main():
    a = parse_args()
    before, _, _ = snapshot(a.before)
    after, hair, old = snapshot(a.after)
    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")

    missing = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    if missing:
        raise RuntimeError("FACE LOCK: protected meshes removed: " + ", ".join(missing[:30]))
    if added:
        raise RuntimeError("FACE LOCK: protected meshes added: " + ", ".join(added[:30]))

    changed = []
    moved_parent = []
    for name in sorted(before):
        if before[name]["points"] != after[name]["points"]:
            changed.append(name)
        if before[name]["parent"] != after[name]["parent"]:
            moved_parent.append(name)
    if changed:
        raise RuntimeError("FACE LOCK: protected geometry changed: " + ", ".join(changed[:30]))
    if moved_parent:
        raise RuntimeError("FACE LOCK: protected hierarchy changed: " + ", ".join(moved_parent[:30]))

    if set(hair) != REQUIRED:
        raise RuntimeError(f"HAIR: expected {sorted(REQUIRED)}, got {sorted(hair)}")
    if any(row["parent"] != "BL_HAIR_ASSET" for row in hair.values()):
        raise RuntimeError(f"HAIR: premium objects not under BL_HAIR_ASSET: {hair}")
    total = sum(row["triangles"] for row in hair.values())
    if total < 48000:
        raise RuntimeError(f"HAIR: insufficient authored/evaluated detail: {total} tris")
    if total > 118000:
        raise RuntimeError(f"HAIR: iPhone budget exceeded: {total} tris")
    if hair["HairPremiumV183_Main"]["triangles"] < 9000:
        raise RuntimeError("HAIR: scalp/main layer lost too much donor detail")
    if hair["HairPremiumV183_Detail"]["triangles"] < 25000:
        raise RuntimeError("HAIR: temple/back detail layer too sparse")
    if hair["HairPremiumV183_Tail"]["triangles"] < 700:
        raise RuntimeError("HAIR: ponytail guide did not survive smoothing")
    if old:
        raise RuntimeError("HAIR: previous hairstyle mesh survived replacement: " + ", ".join(old[:30]))

    vulnerable = sorted(name for name in before if "lash" in name.lower() or "canthus" in name.lower())
    if not vulnerable:
        raise RuntimeError("FACE LOCK: expected lash/canthus helpers missing from accepted base")
    if any(name not in after for name in vulnerable):
        raise RuntimeError("FACE LOCK: lash/canthus helper lost")

    summary = {
        "revision": "v18.3",
        "face_unchanged": True,
        "protected_head_face_meshes": len(before),
        "head_unique_world_points": len(after["HeadShellV140"]["points"]),
        "vulnerable_lash_canthus_helpers_checked": vulnerable,
        "previous_hair_removed": True,
        "hair": hair,
        "triangles_total": total,
        "audit_space": "canonical world points rounded to 5 decimals",
    }
    out = Path(a.report).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_HYBRID_V183_AUDIT", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
