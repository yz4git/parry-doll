"""Restore only the accepted donor hair crown toward its original pre-lift position.

v18.5 r2 lifted the entire donor hair by 8.5% of head height to improve eye visibility, then added a
separate scalp cap. This script removes only that cap and lowers only the spatial crown of the donor
hair, with a soft falloff, while keeping the lower fringe/bangs, side locks and ponytail unchanged.
Face/head source geometry is immutable.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HEAD = "HeadShellV140"
HAIR = "HairPremiumV185_Adventurer"
CAP = "HairPremiumV185_ScalpCap"
LIFT_FRACTION = 0.085

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
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def under(obj, ancestor):
    cur = obj
    while cur:
        if cur.name == ancestor:
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


def protected_face(obj):
    return obj.type == "MESH" and (face_name(obj) or (under(obj, "BL_HEAD") and not hair_name(obj)))


def signature(obj):
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    return (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
            obj.parent.name if obj.parent else None)


def world_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def face_sign(head_center):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    ys = []
    for obj in iris:
        pts = world_points(obj)
        if pts:
            ys.append(bounds(pts)[2].y)
    if not ys:
        raise RuntimeError("cannot derive face direction")
    return -1.0 if sum(ys) / len(ys) < head_center.y else 1.0


def smoothstep(a, b, x):
    if b <= a:
        return 1.0 if x >= b else 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def main():
    a = parse_args()
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(HEAD)
    hair = bpy.data.objects.get(HAIR)
    cap = bpy.data.objects.get(CAP)
    if not head or head.type != "MESH" or not hair or hair.type != "MESH" or not cap or cap.type != "MESH":
        raise RuntimeError("accepted v18.5 r2 objects missing")

    locked_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if len(locked_face) < 50 or HEAD not in locked_face:
        raise RuntimeError(f"face lock set suspicious: {len(locked_face)}")

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)
    lift = hs.z * LIFT_FRACTION

    mw = hair.matrix_world.copy()
    inv = mw.inverted()
    before = world_points(hair)
    moved = []
    max_disp = 0.0

    for v, p in zip(hair.data.vertices, before):
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        front = yr * sign

        # Crown only. Lower forehead/fringe is excluded by z and front bounds. The rear ponytail/root
        # is excluded by the rear/front bound. Side locks are excluded by x.
        if zr <= 0.18 or abs(xr) >= 0.48 or front <= -0.16 or front >= 0.15:
            continue

        zfade = smoothstep(0.18, 0.34, zr)
        xfade = 1.0 - smoothstep(0.34, 0.48, abs(xr))
        rearfade = smoothstep(-0.16, -0.06, front)
        frontfade = 1.0 - smoothstep(0.08, 0.15, front)
        weight = zfade * xfade * rearfade * frontfade
        if weight <= 0.001:
            continue

        # Restore most, but not all, of the original global lift at the crown. A tiny asymmetrical
        # side-part term avoids recreating a perfectly spherical top.
        dz = -lift * 0.88 * weight
        dz += hs.z * 0.0040 * math.sin((xr * 4.0 + front * 1.2) * math.pi) * weight
        dx = hs.x * 0.0020 * math.sin(front * math.pi) * weight
        q = p + Vector((dx, 0.0, dz))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved.append(v.index)

    if not (20 <= len(moved) <= 900):
        raise RuntimeError(f"unexpected crown vertex count: {len(moved)}")
    if max_disp > lift * 0.95:
        raise RuntimeError(f"crown displacement too large: {max_disp} > {lift * 0.95}")
    hair.data.update()

    # Remove only the artificial r2 gap-filling cap after the donor crown itself covers the scalp.
    bpy.data.objects.remove(cap, do_unlink=True)

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected set changed")
    changed = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed[:20]))

    # Prove all edits were inside the declared crown scope on the original r2 positions.
    illegal = []
    for idx in moved:
        p = before[idx]
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        front = yr * sign
        if not (zr > 0.18 and abs(xr) < 0.48 and -0.16 < front < 0.15):
            illegal.append(idx)
    if illegal:
        raise RuntimeError("CROWN SCOPE: illegal moved vertices")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r7"
        hero["hair_refinement"] = "restore-donor-crown-only-remove-scalp-cap"
        hero["face_locked_for_hair_v185_r7"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r7",
        "scope": "donor-crown-only-kappa-fix",
        "face_unchanged": True,
        "scalp_cap_removed": True,
        "lower_bangs_outside_crown_untouched": True,
        "side_hair_outside_crown_untouched": True,
        "ponytail_outside_crown_untouched": True,
        "original_r2_lift_world": lift,
        "crown_restore_fraction": 0.88,
        "crown_vertices_moved": len(moved),
        "max_crown_displacement": max_disp,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R7", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
