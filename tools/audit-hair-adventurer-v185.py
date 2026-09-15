"""Post-export immutable-face and mobile hair audit for v18.5."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

FINAL = "HairPremiumV185_Adventurer"
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


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def args():
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
    return any(t in obj.name.lower() for t in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(t in n for t in HAIR_MARKERS):
        return False
    return any(t in n for t in FACE_MARKERS)


def protected(obj):
    if obj.type != "MESH":
        return False
    return face_name(obj) or (under(obj, "BL_HEAD") and not hair_name(obj))


def points(obj, digits=5):
    mw = obj.matrix_world
    return tuple(sorted({(
        round(float((mw @ v.co).x), digits),
        round(float((mw @ v.co).y), digits),
        round(float((mw @ v.co).z), digits),
    ) for v in obj.data.vertices}))


def tris(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def snapshot(path):
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    locked = {}
    for obj in bpy.data.objects:
        if protected(obj):
            locked[obj.name] = {"points": points(obj), "parent": obj.parent.name if obj.parent else None}
    hair = bpy.data.objects.get(FINAL)
    hair_row = None
    if hair is not None and hair.type == "MESH":
        hair_row = {
            "triangles": tris(hair),
            "vertices": len(hair.data.vertices),
            "uv_layers": len(hair.data.uv_layers),
            "materials": [m.name for m in hair.data.materials if m],
            "parent": hair.parent.name if hair.parent else None,
        }
    extras = sorted(o.name for o in bpy.data.objects if o.type == "MESH" and under(o, "BL_HAIR_ASSET")
                    and not protected(o) and o.name != FINAL)
    return locked, hair_row, extras


def main():
    a = args()
    before, _, _ = snapshot(a.before)
    after, hair, extras = snapshot(a.after)
    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")
    if set(before) != set(after):
        raise RuntimeError(f"FACE LOCK: protected mesh set changed: before={len(before)} after={len(after)}")
    changed = [name for name in sorted(before) if before[name] != after[name]]
    if changed:
        raise RuntimeError("FACE LOCK: protected geometry/hierarchy changed: " + ", ".join(changed[:30]))
    if hair is None:
        raise RuntimeError("HAIR: v18.5 mesh missing")
    if hair["parent"] != "BL_HAIR_ASSET":
        raise RuntimeError(f"HAIR: wrong parent {hair['parent']}")
    if not (1800 <= hair["triangles"] <= 12000):
        raise RuntimeError(f"HAIR: triangle budget invalid: {hair['triangles']}")
    if hair["uv_layers"] < 1:
        raise RuntimeError("HAIR: UV map missing")
    if not hair["materials"]:
        raise RuntimeError("HAIR: material missing")
    if extras:
        raise RuntimeError("HAIR: previous hairstyle survived: " + ", ".join(extras[:30]))
    vulnerable = sorted(name for name in before if "lash" in name.lower() or "canthus" in name.lower())
    if not vulnerable or any(name not in after for name in vulnerable):
        raise RuntimeError("FACE LOCK: lash/canthus helper lost")
    summary = {
        "revision": "v18.5",
        "face_unchanged": True,
        "protected_head_face_meshes": len(before),
        "head_unique_world_points": len(after["HeadShellV140"]["points"]),
        "vulnerable_lash_canthus_helpers_checked": vulnerable,
        "previous_hair_removed": True,
        "hair": hair,
        "audit_space": "canonical world points rounded to 5 decimals",
    }
    out = Path(a.report).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_ADVENTURER_V185_AUDIT", json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
