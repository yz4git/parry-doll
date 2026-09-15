"""Final crown-only fix for accepted v18.5 r2 hair.

Only HairPremiumV185_ScalpCap is edited. Face/head source geometry and the accepted Adventurer
main hair mesh/material/transform remain exact. The cap gets shallow hair-flow ridges, planar UVs,
and a darker low-glare painted blue texture so the crown no longer reads as a white/kappa patch.
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


def signature(obj, include_materials=False):
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    mats = tuple(slot.material.name if slot.material else None for slot in obj.material_slots) if include_materials else ()
    return (
        len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
        obj.parent.name if obj.parent else None, mats,
    )


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


def make_texture(size=192):
    img = bpy.data.images.new("HairCrownR6Texture", width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    for py in range(size):
        v = py / (size - 1)
        ny = (v - 0.5) * 2.0
        for px in range(size):
            u = px / (size - 1)
            nx = (u - 0.5) * 2.0
            radial = min(1.3, math.sqrt(nx * nx + ny * ny))
            angle = math.atan2(nx, -ny + 0.06)

            # Broad hand-painted-looking crown locks: stronger grooves than r5, but no hard spokes.
            wave = 0.5 + 0.5 * math.cos(angle * 7.0 + radial * 2.5 + 0.28)
            groove = 1.0 - 0.48 * (wave ** 2.1)
            center = 0.90 - 0.07 * math.exp(-(radial / 0.30) ** 2)
            front = 0.92 + 0.08 * max(0.0, -ny)
            edge = 0.96 - 0.12 * min(1.0, radial)
            value = max(0.38, min(1.0, groove * center * front * edge))

            # Intentionally darker/saturated in linear space to prevent the top light from blowing
            # the crown toward white. This still sits in the accepted blue-violet hair family.
            r = 0.030 + 0.085 * value
            g = 0.060 + 0.175 * value
            b = 0.250 + 0.430 * value
            i = (py * size + px) * 4
            pixels[i:i + 4] = (r, g, b, 1.0)
    img.pixels = pixels
    img.pack()
    return img


def make_material(image):
    mat = bpy.data.materials.new("HairPremiumV185ScalpRootR6")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.68
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.10
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def assign_planar_uv(cap, hc, hs, sign):
    uv = cap.data.uv_layers.active if cap.data.uv_layers else cap.data.uv_layers.new(name="CrownR6UV")
    mw = cap.matrix_world
    for poly in cap.data.polygons:
        for li in poly.loop_indices:
            vi = cap.data.loops[li].vertex_index
            p = mw @ cap.data.vertices[vi].co
            u = 0.5 + (p.x - hc.x) / max(hs.x * 1.04, 1e-8)
            v = 0.5 + sign * (p.y - hc.y) / max(hs.y * 1.04, 1e-8)
            uv.data[li].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))


def sculpt_cap(cap, hc, hs, sign):
    mw = cap.matrix_world.copy()
    inv = mw.inverted()
    before = world_points(cap)
    moved = 0
    max_disp = 0.0
    for v, p in zip(cap.data.vertices, before):
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        front = yr * sign
        if zr < 0.12 or abs(xr) > 0.56 or abs(yr) > 0.60:
            continue

        radial = min(1.0, math.sqrt((xr / 0.56) ** 2 + (yr / 0.60) ** 2))
        angle = math.atan2(xr, -front + 0.045)
        fade = max(0.0, 1.0 - radial ** 1.65)

        ridge = 0.0060 * hs.z * math.cos(angle * 7.0 + radial * 1.8 + 0.15) * fade
        center_lower = -0.0060 * hs.z * math.exp(-((xr / 0.21) ** 2 + (front / 0.23) ** 2))
        side_part = 0.0065 * hs.z * math.exp(-(((xr + 0.14) / 0.17) ** 2 + ((front + 0.01) / 0.29) ** 2))
        dz = ridge + center_lower + side_part

        scale_xy = 1.0015 + 0.0018 * fade
        q = Vector((
            hc.x + (p.x - hc.x) * scale_xy,
            hc.y + (p.y - hc.y) * scale_xy,
            p.z + dz,
        ))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved += 1
    cap.data.update()
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
    hair_sig = signature(hair, include_materials=True)

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)
    cap_points = len(cap.data.vertices)
    cap_polys = len(cap.data.polygons)

    moved, max_disp = sculpt_cap(cap, hc, hs, sign)
    if moved < 100:
        raise RuntimeError(f"too few scalp-cap vertices sculpted: {moved}")
    if max_disp > hs.z * 0.020:
        raise RuntimeError(f"scalp-cap displacement too large: {max_disp}")

    assign_planar_uv(cap, hc, hs, sign)
    cap.data.materials.clear()
    cap.data.materials.append(make_material(make_texture()))
    for p in cap.data.polygons:
        p.use_smooth = True

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected object set changed")
    changed = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed[:20]))
    if signature(hair, include_materials=True) != hair_sig:
        raise RuntimeError("MAIN HAIR LOCK: accepted hair changed")
    if len(cap.data.vertices) != cap_points or len(cap.data.polygons) != cap_polys:
        raise RuntimeError("CAP TOPOLOGY: vertex/poly count changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r6"
        hero["hair_refinement"] = "scalp-cap-only-dark-low-glare-textured-crown"
        hero["face_locked_for_hair_v185_r6"] = True
        hero["main_hair_locked_for_hair_v185_r6"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", export_apply=False,
        export_materials="EXPORT", export_image_format="AUTO",
    )

    report = {
        "revision": "v18.5-r6",
        "scope": "scalp-cap-only-kappa-fix",
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "ponytail_unchanged": True,
        "cap_topology_unchanged": True,
        "cap_vertices_sculpted": moved,
        "cap_uv_layers": len(cap.data.uv_layers),
        "cap_texture": "HairCrownR6Texture",
        "roughness": 0.68,
        "specular": 0.10,
        "max_cap_displacement": max_disp,
        "max_allowed_displacement": hs.z * 0.020,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R6", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
