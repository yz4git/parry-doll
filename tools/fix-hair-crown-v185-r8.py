"""v18.5 r8: fix only the kappa-looking crown by texture-projecting the accepted donor hair onto the scalp cap.

Face geometry and the accepted Adventurer hair mesh/transform/material remain unchanged. The existing
scalp cap stays as a gap filler, but receives UVs sampled from the nearest donor-hair surface and uses
the exact donor hair material. A tiny crown-only relief breaks the smooth helmet highlight.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HEAD = "HeadShellV140"
HAIR = "HairPremiumV185_Adventurer"
CAP = "HairPremiumV185_ScalpCap"

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


def signature(obj, materials=True):
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    mats = tuple(slot.material.name if slot.material else None for slot in obj.material_slots) if materials else ()
    return (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
            obj.parent.name if obj.parent else None, mats)


def world_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def barycentric(p, a, b, c):
    v0 = b - a
    v1 = c - a
    v2 = p - a
    d00 = v0.dot(v0)
    d01 = v0.dot(v1)
    d11 = v1.dot(v1)
    d20 = v2.dot(v0)
    d21 = v2.dot(v1)
    denom = d00 * d11 - d01 * d01
    if abs(denom) < 1e-12:
        return (1.0, 0.0, 0.0)
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    w = max(0.0, min(1.0, w))
    s = u + v + w
    if s <= 1e-12:
        return (1.0, 0.0, 0.0)
    return (u / s, v / s, w / s)


def build_hair_bvh_and_uv(hair):
    if not hair.data.uv_layers:
        raise RuntimeError("donor hair UV missing")
    uv_layer = hair.data.uv_layers.active
    mw = hair.matrix_world
    verts = [mw @ v.co for v in hair.data.vertices]
    tris = []
    tri_uvs = []
    for poly in hair.data.polygons:
        vids = list(poly.vertices)
        loops = list(poly.loop_indices)
        if len(vids) < 3:
            continue
        for j in range(1, len(vids) - 1):
            tri = (vids[0], vids[j], vids[j + 1])
            luv = (uv_layer.data[loops[0]].uv.copy(), uv_layer.data[loops[j]].uv.copy(), uv_layer.data[loops[j + 1]].uv.copy())
            tris.append(tri)
            tri_uvs.append(luv)
    bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True)
    return bvh, verts, tris, tri_uvs


def transfer_uv(cap, hair):
    bvh, hverts, tris, tri_uvs = build_hair_bvh_and_uv(hair)
    if cap.data.uv_layers:
        uv_layer = cap.data.uv_layers.active
    else:
        uv_layer = cap.data.uv_layers.new(name="CrownDonorTransferUV")

    cmw = cap.matrix_world
    mapped = {}
    distances = []
    for v in cap.data.vertices:
        p = cmw @ v.co
        hit = bvh.find_nearest(p)
        if not hit or hit[0] is None or hit[2] is None:
            raise RuntimeError(f"UV transfer failed at cap vertex {v.index}")
        loc, _normal, tri_index, dist = hit
        a_idx, b_idx, c_idx = tris[tri_index]
        wa, wb, wc = barycentric(loc, hverts[a_idx], hverts[b_idx], hverts[c_idx])
        ua, ub, uc = tri_uvs[tri_index]
        uv = ua * wa + ub * wb + uc * wc
        mapped[v.index] = uv
        distances.append(float(dist))

    for poly in cap.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = cap.data.loops[loop_idx].vertex_index
            uv_layer.data[loop_idx].uv = mapped[vi]
    return max(distances), sum(distances) / len(distances)


def add_crown_relief(cap, hc, hs):
    mw = cap.matrix_world.copy()
    inv = mw.inverted()
    pts = world_points(cap)
    moved = 0
    max_disp = 0.0
    for v, p in zip(cap.data.vertices, pts):
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        if zr < 0.14 or abs(xr) > 0.56 or abs(yr) > 0.60:
            continue
        radial = min(1.0, math.sqrt((xr / 0.56) ** 2 + (yr / 0.60) ** 2))
        fade = max(0.0, 1.0 - radial ** 2.0)
        # Directional, non-radial flow: shallow diagonal sheets rather than a round helmet dome.
        phase = (xr * 5.2 + yr * 2.0) * math.pi
        dz = hs.z * 0.0038 * math.sin(phase) * fade
        dz += hs.z * 0.0030 * math.exp(-(((xr + 0.12) / 0.15) ** 2 + ((yr + 0.02) / 0.30) ** 2))
        q = Vector((hc.x + (p.x - hc.x) * (1.0 + 0.0015 * fade),
                    hc.y + (p.y - hc.y) * (1.0 + 0.0015 * fade),
                    p.z + dz))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved += 1
    cap.data.update()
    if moved < 100:
        raise RuntimeError(f"too few cap vertices relieved: {moved}")
    if max_disp > hs.z * 0.010:
        raise RuntimeError(f"cap relief too large: {max_disp}")
    return moved, max_disp


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
    hair_sig = signature(hair)
    cap_topology = (len(cap.data.vertices), len(cap.data.edges), len(cap.data.polygons))

    _, _, hc, hs = bounds(world_points(head))
    mapped_max, mapped_mean = transfer_uv(cap, hair)
    moved, max_relief = add_crown_relief(cap, hc, hs)

    # Use the exact accepted donor hair material after UV projection. This removes the separate
    # scalp-cap color/lighting identity and makes the cap visually continuous with authored hair.
    source_mat = hair.data.materials[0]
    if source_mat is None:
        raise RuntimeError("accepted donor hair material missing")
    cap.data.materials.clear()
    cap.data.materials.append(source_mat)
    for poly in cap.data.polygons:
        poly.use_smooth = True
        poly.material_index = 0

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected set changed")
    changed_face = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed_face:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed_face[:20]))
    if signature(hair) != hair_sig:
        raise RuntimeError("MAIN HAIR LOCK: donor hair changed")
    if (len(cap.data.vertices), len(cap.data.edges), len(cap.data.polygons)) != cap_topology:
        raise RuntimeError("CAP TOPOLOGY changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r8"
        hero["hair_refinement"] = "crown-cap-donor-uv-transfer"
        hero["face_locked_for_hair_v185_r8"] = True
        hero["main_hair_locked_for_hair_v185_r8"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r8",
        "scope": "scalp-cap-only-donor-texture-transfer",
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "side_hair_unchanged": True,
        "ponytail_unchanged": True,
        "cap_topology_unchanged": True,
        "cap_uses_exact_donor_hair_material": True,
        "cap_vertices_relief": moved,
        "max_cap_relief": max_relief,
        "uv_transfer_max_distance": mapped_max,
        "uv_transfer_mean_distance": mapped_mean,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R8", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
