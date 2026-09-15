"""Fix only the crown/kappa appearance of accepted v18.5 r2 hair.

Hard constraints:
- face/head geometry is immutable;
- accepted Adventurer main hair mesh/transform/material is immutable;
- bangs and ponytail are not moved;
- preserve the r2 scalp cap so no scalp is exposed;
- add only short crown strands that conform to the existing crown surface.
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
MAIN_HAIR = "HairPremiumV185_Adventurer"
SCALP_CAP = "HairPremiumV185_ScalpCap"
ROOT = "BL_HAIR_ASSET"
CROWN_PREFIX = "HairPremiumV185_CrownStrandR3_"

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
    mats = tuple(slot.material.name if slot.material else None for slot in obj.material_slots)
    return (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
            obj.parent.name if obj.parent else None, mats)


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


def make_material(name, color, roughness=0.40):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.26
    return mat


def crown_surface_points(hair, cap, hc, hs, sign):
    pts = []
    for source in (hair, cap):
        for p in world_points(source):
            xr = abs((p.x - hc.x) / max(hs.x, 1e-8))
            yr = abs((p.y - hc.y) / max(hs.y, 1e-8))
            zr = (p.z - hc.z) / max(hs.z, 1e-8)
            front = ((p.y - hc.y) * sign) / max(hs.y, 1e-8)
            if xr < 0.60 and yr < 0.60 and zr > 0.16 and front > -0.30:
                pts.append(p.copy())
    if len(pts) < 200:
        raise RuntimeError(f"insufficient crown samples: {len(pts)}")
    return pts


def surface_z(samples, x, y, radius):
    r2 = radius * radius
    nearby = [p.z for p in samples if (p.x - x) ** 2 + (p.y - y) ** 2 <= r2]
    if nearby:
        return max(nearby)
    nearest = min(samples, key=lambda p: (p.x - x) ** 2 + (p.y - y) ** 2)
    return nearest.z


def add_conformal_panel(name, root, samples, hc, hs, sign, x0, x1, y0, y1, width0, width1, mat):
    sections = 10
    verts = []
    faces = []
    sample_radius = hs.x * 0.075
    for i in range(sections):
        t = i / (sections - 1)
        ease = t * t * (3.0 - 2.0 * t)
        cx = hc.x + hs.x * (x0 * (1.0 - ease) + x1 * ease)
        cy = hc.y + sign * hs.y * (y0 * (1.0 - ease) + y1 * ease)
        w = hs.x * (width0 * (1.0 - t) + width1 * t)
        lx, rx = cx - w, cx + w
        lz = surface_z(samples, lx, cy, sample_radius)
        rz = surface_z(samples, rx, cy, sample_radius)
        micro = hs.z * (0.004 + 0.003 * math.sin(math.pi * t))
        verts.append((lx, cy, lz + micro))
        verts.append((rx, cy, rz + micro))

    for i in range(sections - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))

    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True

    sol = obj.modifiers.new("Crown strand thickness", "SOLIDIFY")
    sol.thickness = hs.x * 0.0045
    sol.offset = 0.0
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=sol.name)
    obj.select_set(False)
    return obj


def main():
    a = parse_args()
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(HEAD)
    hair = bpy.data.objects.get(MAIN_HAIR)
    cap = bpy.data.objects.get(SCALP_CAP)
    root = bpy.data.objects.get(ROOT)
    if not head or head.type != "MESH" or not hair or hair.type != "MESH" or not cap or cap.type != "MESH" or not root:
        raise RuntimeError("accepted v18.5 r2 crown objects missing")

    locked_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if len(locked_face) < 50 or HEAD not in locked_face:
        raise RuntimeError(f"face lock set suspicious: {len(locked_face)}")
    main_hair_sig = signature(hair)
    cap_sig = signature(cap)

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)
    samples = crown_surface_points(hair, cap, hc, hs, sign)

    mat_a = make_material("HairPremiumV185CrownStrandR3A", (0.24, 0.37, 0.82), 0.39)
    mat_b = make_material("HairPremiumV185CrownStrandR3B", (0.17, 0.27, 0.66), 0.42)

    # Wider overlapping strips sit directly on the existing cap. Together they hide the smooth
    # single-dome read while keeping the cap underneath as guaranteed scalp coverage.
    specs = [
        (-0.24, -0.36, -0.12, 0.17, 0.082, 0.024, mat_b),
        (-0.16, -0.25, -0.14, 0.20, 0.086, 0.026, mat_a),
        (-0.08, -0.13, -0.15, 0.22, 0.090, 0.026, mat_b),
        ( 0.00,  0.01, -0.16, 0.23, 0.092, 0.027, mat_a),
        ( 0.08,  0.14, -0.15, 0.22, 0.088, 0.026, mat_b),
        ( 0.16,  0.25, -0.13, 0.20, 0.084, 0.024, mat_a),
        ( 0.24,  0.35, -0.11, 0.16, 0.078, 0.022, mat_b),
    ]
    created = []
    for idx, spec in enumerate(specs, 1):
        created.append(add_conformal_panel(f"{CROWN_PREFIX}{idx:02d}", root, samples, hc, hs, sign, *spec))

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected object set changed")
    changed = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed[:20]))
    if signature(hair) != main_hair_sig:
        raise RuntimeError("HAIR LOCK: accepted Adventurer hair changed")
    if signature(cap) != cap_sig:
        raise RuntimeError("CAP LOCK: accepted scalp cap changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r3"
        hero["hair_refinement"] = "crown-only-layered-cap-overlay"
        hero["face_locked_for_hair_v185_r3"] = True
        hero["main_hair_locked_for_hair_v185_r3"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r3",
        "scope": "crown-only-kappa-fix",
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "scalp_cap_unchanged": True,
        "bangs_unchanged": True,
        "ponytail_unchanged": True,
        "old_smooth_scalp_cap_preserved": True,
        "crown_surface_samples": len(samples),
        "crown_strands": [o.name for o in created],
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R3", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
