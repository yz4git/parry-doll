"""Fix only the crown/kappa appearance of accepted v18.5 r2 hair.

Hard constraints:
- do not modify face/head source geometry;
- do not modify the accepted Adventurer main hair mesh/transform/material;
- do not move bangs or ponytail;
- replace only the smooth scalp-cap look with a subtle layered crown/root treatment.
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
OLD_CAP = "HairPremiumV185_ScalpCap"
ROOT = "BL_HAIR_ASSET"
CROWN_BASE = "HairPremiumV185_CrownBaseR3"
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


def make_material(name, color, roughness=0.42):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.28
    return mat


def create_crown_base(head, root, hc, hs, sign):
    """Copy only upper-head polygons; add subtle radial ridges instead of a smooth helmet dome."""
    mw = head.matrix_world
    vertex_map = {}
    verts = []
    faces = []
    selected = 0

    for poly in head.data.polygons:
        wps = [mw @ head.data.vertices[i].co for i in poly.vertices]
        c = sum(wps, Vector()) / len(wps)
        zrel = (c.z - hc.z) / max(hs.z, 1e-8)
        front = ((c.y - hc.y) * sign) / max(hs.y, 1e-8)
        side = abs((c.x - hc.x) / max(hs.x, 1e-8))

        # Crown only: deliberately stop well above ears/temples so accepted side hair is untouched.
        keep = zrel > 0.20 and front < 0.30 and side < 0.50
        if not keep:
            continue
        selected += 1
        face = []
        for old_idx, wp in zip(poly.vertices, wps):
            key = int(old_idx)
            if key not in vertex_map:
                d = wp - hc
                # Small root-shell offset plus alternating crown ridges. The ridge amplitude fades
                # toward the perimeter and breaks the single smooth kappa/helmet highlight.
                angle = math.atan2(d.x / max(hs.x, 1e-8), (-sign * d.y) / max(hs.y, 1e-8))
                radial = min(1.0, math.sqrt((d.x / (hs.x * 0.52)) ** 2 + (d.y / (hs.y * 0.52)) ** 2))
                ridge = (0.010 + 0.010 * (0.5 + 0.5 * math.cos(angle * 7.0 + 0.65))) * (1.0 - 0.55 * radial)
                scale_xy = 1.012 + ridge
                scale_z = 1.010 + ridge * 0.72
                out = Vector((hc.x + d.x * scale_xy, hc.y + d.y * scale_xy, hc.z + d.z * scale_z))
                vertex_map[key] = len(verts)
                verts.append(tuple(out))
            face.append(vertex_map[key])
        faces.append(face)

    if selected < 250:
        raise RuntimeError(f"crown base selection too small: {selected}")
    mesh = bpy.data.meshes.new(CROWN_BASE + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(CROWN_BASE, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    for p in mesh.polygons:
        p.use_smooth = True
    return obj, selected


def add_panel(name, root, hc, hs, sign, x0, x1, y0, y1, z_peak, z_drop, width0, width1, mat):
    """Create one thin tapered crown panel following the head arc; used only above the crown."""
    sections = 7
    verts = []
    faces = []
    for i in range(sections):
        t = i / (sections - 1)
        ease = t * t * (3.0 - 2.0 * t)
        x = hc.x + hs.x * (x0 * (1.0 - ease) + x1 * ease)
        y = hc.y + sign * hs.y * (y0 * (1.0 - ease) + y1 * ease)
        z = hc.z + hs.z * (z_peak - z_drop * (t ** 1.45))
        # Slight arch above the root shell; biggest near middle for layered-hair silhouette.
        z += hs.z * 0.018 * math.sin(math.pi * t)
        w = hs.x * (width0 * (1.0 - t) + width1 * t)
        verts.append((x - w, y, z))
        verts.append((x + w, y, z))
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
    sol.thickness = hs.x * 0.010
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
    root = bpy.data.objects.get(ROOT)
    old = bpy.data.objects.get(OLD_CAP)
    if not head or head.type != "MESH" or not hair or hair.type != "MESH" or not root:
        raise RuntimeError("accepted v18.5 r2 objects missing")

    locked_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if len(locked_face) < 50 or HEAD not in locked_face:
        raise RuntimeError(f"face lock set suspicious: {len(locked_face)}")
    main_hair_sig = signature(hair)

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)

    # Remove only the r2 smooth scalp cap. Accepted donor hair remains untouched.
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    base_mat = make_material("HairPremiumV185CrownRootR3", (0.12, 0.19, 0.48), 0.44)
    strand_mat = make_material("HairPremiumV185CrownStrandR3", (0.22, 0.34, 0.78), 0.40)
    base, selected = create_crown_base(head, root, hc, hs, sign)
    base.data.materials.append(base_mat)

    # Five short overlapping crown panels: enough to break the bald/helmet read, but deliberately
    # stop before the existing bangs. Their asymmetry avoids a radial flower/LEGO pattern.
    specs = [
        (-0.16, -0.29, -0.08, 0.16, 0.525, 0.105, 0.095, 0.030),
        (-0.07, -0.15, -0.10, 0.19, 0.535, 0.112, 0.100, 0.032),
        ( 0.00,  0.04, -0.11, 0.20, 0.542, 0.118, 0.105, 0.030),
        ( 0.09,  0.19, -0.09, 0.18, 0.532, 0.108, 0.096, 0.030),
        ( 0.18,  0.31, -0.07, 0.15, 0.520, 0.100, 0.086, 0.026),
    ]
    created = []
    for idx, spec in enumerate(specs, 1):
        created.append(add_panel(f"{CROWN_PREFIX}{idx:02d}", root, hc, hs, sign, *spec, strand_mat))

    # Hard lock: face + accepted main hair must be exactly unchanged.
    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected object set changed")
    changed = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed[:20]))
    if signature(hair) != main_hair_sig:
        raise RuntimeError("HAIR LOCK: accepted Adventurer hair changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r3"
        hero["hair_refinement"] = "crown-only-kappa-fix"
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
        "old_smooth_scalp_cap_removed": old is not None,
        "crown_base_polygons_selected": selected,
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
