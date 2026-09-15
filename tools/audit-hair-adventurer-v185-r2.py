"""Post-export immutable-face audit for v18.5 r2 main hair + copied scalp cap."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy

MAIN = "HairPremiumV185_Adventurer"
SCALP = "HairPremiumV185_ScalpCap"
REQUIRED = {MAIN, SCALP}
HAIR_MARKERS = (
    "hairdonor", "hairpremium", "hairrear", "hairtop", "herohair", "heropony", "herocrown",
    "ponymass", "ponyfan", "ponyfoundation", "ponywing", "ponyroot", "ponytail", "hairtie",
    "fringe", "bang", "crown", "temporal", "temple", "nape", "wisp", "strand", "lock",
    "cascade", "profileeyeframe", "profilehairornament", "referencewisp", "eyerevealfringe",
    "earfrontwisp", "bl_pony_dynamic", "scalpcap",
)
FACE_MARKERS = (
    "headshell", "davidonizaki", "eyelid", "eyelight", "iris", "pupil", "sclera", "wetline",
    "lash", "canthus", "brow", "skinrim", "beautymark", "nose", "lip", "mouth",
    "earantihelix", "earconcha", "earhelix", "earlobefold", "eartragus", "earring",
)


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


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
    hair = {}
    for name in REQUIRED:
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.type == "MESH":
            hair[name] = {
                "triangles": tris(obj),
                "vertices": len(obj.data.vertices),
                "uv_layers": len(obj.data.uv_layers),
                "materials": [m.name for m in obj.data.materials if m],
                "parent": obj.parent.name if obj.parent else None,
            }
    extras = sorted(o.name for o in bpy.data.objects if o.type == "MESH" and under(o, "BL_HAIR_ASSET")
                    and not protected(o) and o.name not in REQUIRED)
    return locked, hair, extras


def main():
    a = parse_args()
    before, _, _ = snapshot(a.before)
    after, hair, extras = snapshot(a.after)
    if "HeadShellV140" not in before or "HeadShellV140" not in after:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")
    if set(before) != set(after):
        raise RuntimeError(f"FACE LOCK: protected set changed before={len(before)} after={len(after)}")
    changed = [name for name in sorted(before) if before[name] != after[name]]
    if changed:
        raise RuntimeError("FACE LOCK: protected geometry/hierarchy changed: " + ", ".join(changed[:30]))
    if set(hair) != REQUIRED:
        raise RuntimeError(f"HAIR: expected {sorted(REQUIRED)}, got {sorted(hair)}")
    if any(row["parent"] != "BL_HAIR_ASSET" for row in hair.values()):
        raise RuntimeError(f"HAIR: wrong parent: {hair}")
    if not (1800 <= hair[MAIN]["triangles"] <= 12000):
        raise RuntimeError(f"HAIR: main donor budget invalid {hair[MAIN]['triangles']}")
    if not (500 <= hair[SCALP]["triangles"] <= 18000):
        raise RuntimeError(f"HAIR: scalp cap budget invalid {hair[SCALP]['triangles']}")
    total = sum(r["triangles"] for r in hair.values())
    if total > 22000:
        raise RuntimeError(f"HAIR: combined budget invalid {total}")
    if hair[MAIN]["uv_layers"] < 1:
        raise RuntimeError("HAIR: donor UV missing")
    if not hair[MAIN]["materials"] or not hair[SCALP]["materials"]:
        raise RuntimeError("HAIR: material missing")
    if extras:
        raise RuntimeError("HAIR: previous style survived: " + ", ".join(extras[:30]))
    vulnerable = sorted(name for name in before if "lash" in name.lower() or "canthus" in name.lower())
    if not vulnerable or any(name not in after for name in vulnerable):
        raise RuntimeError("FACE LOCK: lash/canthus helper lost")
    summary = {
        "revision": "v18.5-r2",
        "face_unchanged": True,
        "protected_head_face_meshes": len(before),
        "head_unique_world_points": len(after["HeadShellV140"]["points"]),
        "vulnerable_lash_canthus_helpers_checked": vulnerable,
        "previous_hair_removed": True,
        "hair": hair,
        "combined_hair_triangles": total,
        "audit_space": "canonical world points rounded to 5 decimals",
    }
    out = Path(a.report).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_ADVENTURER_V185_R2_AUDIT", json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
