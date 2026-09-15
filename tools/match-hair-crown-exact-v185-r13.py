"""v18.5 r13: exact donor-hair look transfer for the seven added crown locks.

Geometry is immutable. The seven r11 crown-lock meshes keep exactly the same vertices/transforms.
Only their UVs and materials are changed: each lock loop receives the UV of the nearest point on
the accepted Adventurer donor hair, then all locks share the donor hair material itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HEAD = "HeadShellV140"
HAIR = "HairPremiumV185_Adventurer"
CAP = "HairPremiumV185_ScalpCap"
LOCK_PREFIX = "HairPremiumV185_CrownLockR11_"
UV_NAME = "HairCrownExactR13UV"

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


def geom_signature(obj):
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    return (
        len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
        obj.parent.name if obj.parent else None,
    )


def material_signature(obj):
    return tuple(slot.material.name if slot.material else None for slot in obj.material_slots)


def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14:
        return (1.0, 0.0, 0.0)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    u = 1.0 - v - w
    u, v, w = max(0.0, u), max(0.0, v), max(0.0, w)
    s = u + v + w
    return (u / s, v / s, w / s) if s > 1e-14 else (1.0, 0.0, 0.0)


def donor_surface(hair):
    if not hair.data.uv_layers or hair.data.uv_layers.active is None:
        raise RuntimeError("donor hair active UV missing")
    uv_layer = hair.data.uv_layers.active
    mw = hair.matrix_world
    verts = [mw @ v.co for v in hair.data.vertices]
    tris, tri_uvs = [], []
    for poly in hair.data.polygons:
        vids = list(poly.vertices)
        loops = list(poly.loop_indices)
        for j in range(1, len(vids) - 1):
            tris.append((vids[0], vids[j], vids[j + 1]))
            tri_uvs.append((
                uv_layer.data[loops[0]].uv.copy(),
                uv_layer.data[loops[j]].uv.copy(),
                uv_layer.data[loops[j + 1]].uv.copy(),
            ))
    if not tris:
        raise RuntimeError("donor hair has no triangles")
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), verts, tris, tri_uvs, uv_layer.name


def transfer_uv(lock, bvh, hverts, tris, tri_uvs):
    uv = lock.data.uv_layers.get(UV_NAME) or lock.data.uv_layers.new(name=UV_NAME)
    lock.data.uv_layers.active = uv
    mw = lock.matrix_world
    distances = []
    for poly in lock.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = lock.data.loops[loop_idx].vertex_index
            p = mw @ lock.data.vertices[vi].co
            loc, _normal, tri_idx, dist = bvh.find_nearest(p)
            if loc is None or tri_idx is None:
                raise RuntimeError(f"nearest donor surface missing for {lock.name}:{vi}")
            ia, ib, ic = tris[tri_idx]
            wa, wb, wc = barycentric(loc, hverts[ia], hverts[ib], hverts[ic])
            ua, ub, uc = tri_uvs[tri_idx]
            q = ua * wa + ub * wb + uc * wc
            uv.data[loop_idx].uv = (float(q.x), float(q.y))
            distances.append(float(dist))
    if not distances:
        raise RuntimeError(f"no UV loops transferred for {lock.name}")
    return max(distances), sum(distances) / len(distances), len(distances)


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(HEAD)
    hair = bpy.data.objects.get(HAIR)
    cap = bpy.data.objects.get(CAP)
    locks = sorted(
        [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(LOCK_PREFIX)],
        key=lambda o: o.name,
    )
    if not head or not hair or not cap or len(locks) != 7:
        raise RuntimeError(f"r12 objects missing: head={bool(head)} hair={bool(hair)} cap={bool(cap)} locks={len(locks)}")
    if not hair.data.materials or hair.data.materials[0] is None:
        raise RuntimeError("donor hair material missing")
    donor_mat = hair.data.materials[0]

    all_geom_before = {o.name: geom_signature(o) for o in bpy.data.objects if o.type == "MESH"}
    face_before = {o.name: geom_signature(o) for o in bpy.data.objects if protected_face(o)}
    hair_mat_before = material_signature(hair)
    cap_mat_before = material_signature(cap)
    lock_geom_before = {o.name: geom_signature(o) for o in locks}

    bvh, hverts, tris, tri_uvs, donor_uv_name = donor_surface(hair)
    per_lock = {}
    prior_materials = {}
    for obj in locks:
        prior_materials[obj.name] = list(material_signature(obj))
        dmax, dmean, loops = transfer_uv(obj, bvh, hverts, tris, tri_uvs)
        obj.data.materials.clear()
        obj.data.materials.append(donor_mat)
        for poly in obj.data.polygons:
            poly.material_index = 0
        per_lock[obj.name] = {
            "uv_loops": loops,
            "nearest_donor_max_distance": dmax,
            "nearest_donor_mean_distance": dmean,
        }

    all_geom_after = {o.name: geom_signature(o) for o in bpy.data.objects if o.type == "MESH"}
    if all_geom_after != all_geom_before:
        changed = [n for n in all_geom_before if all_geom_before.get(n) != all_geom_after.get(n)]
        raise RuntimeError("GEOMETRY LOCK changed: " + ", ".join(changed[:20]))
    if {o.name: geom_signature(o) for o in bpy.data.objects if protected_face(o)} != face_before:
        raise RuntimeError("FACE LOCK changed")
    if material_signature(hair) != hair_mat_before:
        raise RuntimeError("MAIN HAIR MATERIAL changed")
    if material_signature(cap) != cap_mat_before:
        raise RuntimeError("SCALP GAP MATERIAL changed")
    if any(geom_signature(o) != lock_geom_before[o.name] for o in locks):
        raise RuntimeError("CROWN LOCK GEOMETRY changed")
    if any(material_signature(o) != (donor_mat.name,) for o in locks):
        raise RuntimeError("CROWN LOCK exact donor material assignment failed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r13"
        hero["hair_refinement"] = "crown-lock-exact-donor-uv-material"
        hero["face_locked_for_hair_v185_r13"] = True
        hero["geometry_locked_for_hair_v185_r13"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", export_apply=False,
        export_materials="EXPORT", export_image_format="AUTO",
    )

    report = {
        "revision": "v18.5-r13",
        "scope": "seven-crown-lock-exact-donor-uv-material",
        "geometry_unchanged": True,
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "side_hair_unchanged": True,
        "ponytail_unchanged": True,
        "scalp_gap_material_unchanged": True,
        "crown_lock_count": len(locks),
        "prior_lock_materials": prior_materials,
        "exact_shared_material": donor_mat.name,
        "donor_uv_layer": donor_uv_name,
        "transferred_uv_layer": UV_NAME,
        "per_lock_transfer": per_lock,
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_EXACT_V185_R13", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
