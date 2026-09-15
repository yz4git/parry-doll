"""Refine the accepted-face v18.5 hair candidate without touching face/head geometry.

Changes only hair-side assets:
- lift the imported Adventurer hair slightly so the authored bangs reveal more of the eyes;
- create a separate scalp cap by COPYING upper/back polygons from HeadShellV140;
- offset the copied cap outward to avoid z-fighting.
HeadShellV140 and every protected facial/helper mesh remain byte/transform identical in scene data.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

MAIN_HAIR = "HairPremiumV185_Adventurer"
SCALP = "HairPremiumV185_ScalpCap"
HAIR_ROOT = "BL_HAIR_ASSET"
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
    p.add_argument("--lift", type=float, default=0.085, help="hair lift as fraction of head height")
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


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def face_sign(head_center):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    ys = []
    for obj in iris:
        pts = world_points(obj)
        if pts:
            _, _, c, _ = bounds(pts)
            ys.append(c.y)
    if not ys:
        raise RuntimeError("FACE LOCK: cannot derive face side")
    return -1.0 if sum(ys) / len(ys) < head_center.y else 1.0


def create_scalp_cap(head, root, hc, hs, sign):
    mw = head.matrix_world
    vertex_map = {}
    verts = []
    faces = []
    selected_polys = 0

    for poly in head.data.polygons:
        wps = [mw @ head.data.vertices[i].co for i in poly.vertices]
        center = sum(wps, Vector()) / len(wps)
        zrel = (center.z - hc.z) / max(hs.z, 1e-8)
        front = ((center.y - hc.y) * sign) / max(hs.y, 1e-8)  # positive toward face

        # Main cap = upper half around side/back. Very top is allowed to extend farther toward the
        # forehead so no white crown is visible between donor bangs. The lower forehead remains open.
        keep = (zrel > 0.015 and front < 0.10) or (zrel > 0.225 and front < 0.36)
        if not keep:
            continue
        selected_polys += 1
        face = []
        for old_idx, wp in zip(poly.vertices, wps):
            key = int(old_idx)
            if key not in vertex_map:
                d = wp - hc
                # Small anisotropic outward shell. This creates a distinct hair asset and prevents
                # z-fighting while preserving the immutable original head beneath it.
                expanded = Vector((hc.x + d.x * 1.014, hc.y + d.y * 1.014, hc.z + d.z * 1.010))
                vertex_map[key] = len(verts)
                verts.append((float(expanded.x), float(expanded.y), float(expanded.z)))
            face.append(vertex_map[key])
        faces.append(face)

    if selected_polys < 300 or not faces:
        raise RuntimeError(f"scalp cap selection too small: {selected_polys} polygons")
    mesh = bpy.data.meshes.new(SCALP + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    cap = bpy.data.objects.new(SCALP, mesh)
    bpy.context.scene.collection.objects.link(cap)
    cap.parent = root
    for p in cap.data.polygons:
        p.use_smooth = True
    return cap, selected_polys


def scalp_material():
    mat = bpy.data.materials.new("HairPremiumV185ScalpRoot")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.055, 0.075, 0.22, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.43
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.27
    return mat


def main():
    a = parse_args()
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))
    head = bpy.data.objects.get("HeadShellV140")
    hair = bpy.data.objects.get(MAIN_HAIR)
    root = bpy.data.objects.get(HAIR_ROOT)
    if head is None or head.type != "MESH" or hair is None or hair.type != "MESH" or root is None:
        raise RuntimeError("v18.5 r2 requires HeadShellV140, v18.5 hair, and BL_HAIR_ASSET")

    locked = {o.name: signature(o) for o in bpy.data.objects if protected(o)}
    if len(locked) < 50 or "HeadShellV140" not in locked:
        raise RuntimeError(f"FACE LOCK: suspicious protected set {len(locked)}")

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)
    lift = hs.z * a.lift
    hair.matrix_world = Matrix.Translation(Vector((0.0, 0.0, lift))) @ hair.matrix_world
    bpy.context.view_layer.update()

    old_cap = bpy.data.objects.get(SCALP)
    if old_cap is not None:
        bpy.data.objects.remove(old_cap, do_unlink=True)
    cap, selected = create_scalp_cap(head, root, hc, hs, sign)
    cap.data.materials.clear()
    cap.data.materials.append(scalp_material())

    hair_tris = tri_count(hair)
    cap_tris = tri_count(cap)
    total = hair_tris + cap_tris
    if not (1800 <= hair_tris <= 12000):
        raise RuntimeError(f"main hair triangle budget invalid: {hair_tris}")
    if not (500 <= cap_tris <= 18000):
        raise RuntimeError(f"scalp cap triangle budget invalid: {cap_tris}")
    if total > 22000:
        raise RuntimeError(f"combined v18.5 r2 hair too heavy: {total}")

    now = {o.name: signature(o) for o in bpy.data.objects if protected(o)}
    if set(now) != set(locked):
        raise RuntimeError(f"FACE LOCK: protected set changed before={len(locked)} after={len(now)}")
    changed = [name for name in locked if locked[name] != now[name]]
    if changed:
        raise RuntimeError("FACE LOCK: protected object changed: " + ", ".join(changed[:30]))

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r2"
        hero["hair_refinement"] = "lifted-authored-bangs-plus-copied-scalp-cap"
        hero["face_locked_for_hair_v185_r2"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    hlo, hhi, hcenter, hsize = bounds(world_points(hair))
    clo, chi, ccenter, csize = bounds(world_points(cap))
    report = {
        "revision": "v18.5-r2",
        "face_locked": True,
        "protected_face_meshes": len(locked),
        "hair_lift_fraction_head_height": a.lift,
        "hair_lift_world": lift,
        "main_hair_triangles": hair_tris,
        "scalp_cap_triangles": cap_tris,
        "combined_hair_triangles": total,
        "scalp_selected_head_polygons": selected,
        "main_hair_bounds": {"min": list(hlo), "max": list(hhi), "center": list(hcenter), "size": list(hsize)},
        "scalp_cap_bounds": {"min": list(clo), "max": list(chi), "center": list(ccenter), "size": list(csize)},
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_ADVENTURER_V185_R2_REFINE", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
