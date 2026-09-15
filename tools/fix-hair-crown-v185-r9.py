"""v18.5 r9: crown-cap only fix using smoothed donor-hair colors.

Face and accepted donor hair stay exactly unchanged. The existing scalp cap keeps its topology,
receives a shallow hair-flow relief, and gets donor-derived colors baked to corners with strong
outlier suppression so atlas seams/dark pixels cannot appear as black crown cracks.
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
COLOR_ATTR = "HairCrownR9Color"

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


def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1.0, 0.0, 0.0)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    u = 1.0 - v - w
    u, v, w = max(0.0, u), max(0.0, v), max(0.0, w)
    s = u + v + w
    return (u / s, v / s, w / s) if s > 1e-12 else (1.0, 0.0, 0.0)


def donor_surface(hair):
    if not hair.data.uv_layers:
        raise RuntimeError("donor hair UV missing")
    uv_layer = hair.data.uv_layers.active
    mw = hair.matrix_world
    verts = [mw @ v.co for v in hair.data.vertices]
    tris, tri_uvs = [], []
    for poly in hair.data.polygons:
        vids, loops = list(poly.vertices), list(poly.loop_indices)
        for j in range(1, len(vids) - 1):
            tris.append((vids[0], vids[j], vids[j + 1]))
            tri_uvs.append((uv_layer.data[loops[0]].uv.copy(), uv_layer.data[loops[j]].uv.copy(), uv_layer.data[loops[j + 1]].uv.copy()))
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), verts, tris, tri_uvs


def image_from_material(mat):
    if not mat or not mat.use_nodes or not mat.node_tree:
        raise RuntimeError("donor material nodes missing")
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None:
            return node.image
    raise RuntimeError("donor hair texture image missing")


def sample_image(img, uv):
    w, h = img.size
    u = max(0.0, min(0.999999, float(uv.x)))
    v = max(0.0, min(0.999999, float(uv.y)))
    x = min(w - 1, max(0, int(u * w)))
    y = min(h - 1, max(0, int(v * h)))
    base = (y * w + x) * 4
    px = img.pixels
    return Vector((float(px[base]), float(px[base + 1]), float(px[base + 2])))


def donor_colors_for_cap(cap, hair):
    bvh, hverts, tris, tri_uvs = donor_surface(hair)
    img = image_from_material(hair.data.materials[0])
    cmw = cap.matrix_world
    raw = {}
    distances = []
    for v in cap.data.vertices:
        p = cmw @ v.co
        loc, _normal, tri_idx, dist = bvh.find_nearest(p)
        if loc is None or tri_idx is None:
            raise RuntimeError(f"nearest donor surface missing for cap vertex {v.index}")
        ia, ib, ic = tris[tri_idx]
        wa, wb, wc = barycentric(loc, hverts[ia], hverts[ib], hverts[ic])
        ua, ub, uc = tri_uvs[tri_idx]
        uv = ua * wa + ub * wb + uc * wc
        raw[v.index] = sample_image(img, uv)
        distances.append(float(dist))

    # Robust global hair-crown tone. Reject very dark atlas/seam samples before averaging.
    good = [c for c in raw.values() if max(c) > 0.20 and (c.x + c.y + c.z) / 3.0 > 0.12]
    if len(good) < len(raw) * 0.45:
        good = list(raw.values())
    avg = sum(good, Vector()) / len(good)

    smooth = {}
    for idx, c in raw.items():
        lum = (c.x + c.y + c.z) / 3.0
        if lum < 0.14 or max(c) < 0.22:
            c = avg.copy()
        # 70% shared donor crown tone + 30% local donor variation. This preserves hair identity
        # while suppressing UV-atlas seams and one-pixel dark cracks.
        out = avg * 0.70 + c * 0.30
        out.x = max(avg.x * 0.72, min(avg.x * 1.28, out.x))
        out.y = max(avg.y * 0.72, min(avg.y * 1.28, out.y))
        out.z = max(avg.z * 0.78, min(avg.z * 1.22, out.z))
        smooth[idx] = out
    return smooth, avg, max(distances), sum(distances) / len(distances)


def add_relief(cap, hc, hs):
    mw, inv = cap.matrix_world.copy(), cap.matrix_world.inverted()
    moved, max_disp = 0, 0.0
    for v, p in zip(cap.data.vertices, world_points(cap)):
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        if zr < 0.14 or abs(xr) > 0.56 or abs(yr) > 0.60:
            continue
        radial = min(1.0, math.sqrt((xr / 0.56) ** 2 + (yr / 0.60) ** 2))
        fade = max(0.0, 1.0 - radial ** 2)
        # Broad diagonal locks; deliberately not radial to avoid kappa/helmet symmetry.
        phase = (xr * 4.5 + yr * 1.8) * math.pi
        dz = hs.z * 0.0032 * math.sin(phase) * fade
        dz += hs.z * 0.0026 * math.exp(-(((xr + 0.12) / 0.16) ** 2 + ((yr + 0.01) / 0.30) ** 2))
        q = Vector((hc.x + (p.x - hc.x) * (1.0 + 0.0012 * fade),
                    hc.y + (p.y - hc.y) * (1.0 + 0.0012 * fade),
                    p.z + dz))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved += 1
    cap.data.update()
    if moved < 100 or max_disp > hs.z * 0.009:
        raise RuntimeError(f"invalid cap relief moved={moved} max={max_disp}")
    return moved, max_disp


def apply_color_material(cap, colors):
    if COLOR_ATTR in cap.data.color_attributes:
        cap.data.color_attributes.remove(cap.data.color_attributes[COLOR_ATTR])
    attr = cap.data.color_attributes.new(name=COLOR_ATTR, type="FLOAT_COLOR", domain="CORNER")
    for poly in cap.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = cap.data.loops[loop_idx].vertex_index
            c = colors[vi]
            attr.data[loop_idx].color = (c.x, c.y, c.z, 1.0)

    mat = bpy.data.materials.new("HairPremiumV185CrownR9")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    vcol = nodes.new("ShaderNodeVertexColor")
    vcol.layer_name = COLOR_ATTR
    links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.56
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.18
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    cap.data.materials.clear()
    cap.data.materials.append(mat)
    for poly in cap.data.polygons:
        poly.material_index = 0
        poly.use_smooth = True
    return mat.name


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
    colors, avg, uv_max, uv_mean = donor_colors_for_cap(cap, hair)
    moved, max_relief = add_relief(cap, hc, hs)
    mat_name = apply_color_material(cap, colors)

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face) or any(locked_face[n] != now_face[n] for n in locked_face):
        raise RuntimeError("FACE LOCK changed")
    if signature(hair) != hair_sig:
        raise RuntimeError("MAIN HAIR LOCK changed")
    if (len(cap.data.vertices), len(cap.data.edges), len(cap.data.polygons)) != cap_topology:
        raise RuntimeError("CAP TOPOLOGY changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r9"
        hero["hair_refinement"] = "crown-cap-smoothed-donor-color"
        hero["face_locked_for_hair_v185_r9"] = True
        hero["main_hair_locked_for_hair_v185_r9"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r9",
        "scope": "scalp-cap-only-smoothed-donor-color",
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "side_hair_unchanged": True,
        "ponytail_unchanged": True,
        "cap_topology_unchanged": True,
        "dark_atlas_outliers_suppressed": True,
        "cap_material": mat_name,
        "donor_color_average": [avg.x, avg.y, avg.z],
        "cap_vertices_relief": moved,
        "max_cap_relief": max_relief,
        "nearest_hair_max_distance": uv_max,
        "nearest_hair_mean_distance": uv_mean,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R9", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
