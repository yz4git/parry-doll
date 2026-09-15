"""Crown-only sculpt for accepted v18.5 r2 hair.

No extra crown accessories are created. Only vertices/polygons in the spatial crown region of the
accepted donor hair are changed. Face/head, bangs/lower fringe, side hair and ponytail are left as-is.
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


def crown_region(p, hc, hs, sign):
    xr = (p.x - hc.x) / max(hs.x, 1e-8)
    yr = (p.y - hc.y) / max(hs.y, 1e-8)
    zr = (p.z - hc.z) / max(hs.z, 1e-8)
    front = yr * sign
    allowed = zr > 0.285 and abs(xr) < 0.50 and abs(yr) < 0.50 and front > -0.30 and front < 0.30
    return allowed, xr, yr, zr, front


def make_crown_material(hair):
    if not hair.data.materials or hair.data.materials[0] is None:
        raise RuntimeError("main hair material missing")
    mat = hair.data.materials[0].copy()
    mat.name = "HairPremiumV185Texture_CrownR4"
    if not mat.use_nodes:
        return mat
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return mat
    base = bsdf.inputs.get("Base Color")
    if base is None:
        return mat
    if base.is_linked:
        old_link = base.links[0]
        source = old_link.from_socket
        links.remove(old_link)
        tint = nodes.new("ShaderNodeMixRGB")
        tint.name = "CrownR4TextureTint"
        tint.blend_type = "MULTIPLY"
        tint.inputs[0].default_value = 0.30
        tint.inputs[2].default_value = (0.56, 0.70, 0.98, 1.0)
        links.new(source, tint.inputs[1])
        links.new(tint.outputs["Color"], base)
    else:
        c = base.default_value
        base.default_value = (c[0] * 0.86, c[1] * 0.92, min(1.0, c[2] * 1.02), c[3])
    rough = bsdf.inputs.get("Roughness")
    if rough is not None:
        rough.default_value = max(float(rough.default_value), 0.46)
    return mat


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
    cap_sig = signature(cap)

    _, _, hc, hs = bounds(world_points(head))
    sign = face_sign(hc)
    mw = hair.matrix_world.copy()
    inv = mw.inverted()
    before = world_points(hair)

    moved = []
    max_disp = 0.0
    for v, p in zip(hair.data.vertices, before):
        allowed, xr, yr, zr, front = crown_region(p, hc, hs, sign)
        if not allowed:
            continue
        # Fade to zero at the crown-region boundary so there is no hard geometry seam.
        edge_x = max(0.0, 1.0 - abs(xr) / 0.50)
        edge_y = max(0.0, 1.0 - abs(yr) / 0.50)
        edge_z = min(1.0, max(0.0, (zr - 0.285) / 0.16))
        fade = edge_x * edge_y * edge_z

        # Subtle side-part sculpt: lower the perfectly round center very slightly, raise an
        # off-centre sweep, and add broad low-amplitude strand ridges. No spikes/accessories.
        center_soften = -0.0055 * hs.z * math.exp(-((xr / 0.17) ** 2 + (front / 0.22) ** 2))
        sweep = 0.0105 * hs.z * math.exp(-(((xr + 0.13) / 0.16) ** 2 + ((front + 0.01) / 0.27) ** 2))
        ridges = 0.0045 * hs.z * math.sin((xr * 4.2 + front * 1.35) * math.pi) * fade
        dz = (center_soften + sweep) * fade + ridges
        dx = 0.0035 * hs.x * math.sin(front * math.pi) * fade
        dy = sign * 0.0020 * hs.y * math.sin((xr + 0.15) * math.pi) * fade
        q = p + Vector((dx, dy, dz))
        disp = (q - p).length
        max_disp = max(max_disp, disp)
        v.co = inv @ q
        moved.append(v.index)

    if not (20 <= len(moved) <= 900):
        raise RuntimeError(f"unexpected crown moved vertex count: {len(moved)}")
    if max_disp > hs.z * 0.025:
        raise RuntimeError(f"crown displacement too large: {max_disp}")
    hair.data.update()

    # Reuse the original authored texture for crown polygons, only with a subtle darker tint to
    # remove the bright circular/kappa highlight. Lower fringe/pony polygons keep material 0.
    crown_mat = make_crown_material(hair)
    hair.data.materials.append(crown_mat)
    crown_index = len(hair.data.materials) - 1
    crown_polys = 0
    moved_set = set(moved)
    for poly in hair.data.polygons:
        if not any(i in moved_set for i in poly.vertices):
            continue
        center = mw @ poly.center
        allowed, _, _, _, _ = crown_region(center, hc, hs, sign)
        if allowed:
            poly.material_index = crown_index
            crown_polys += 1
    if crown_polys < 20:
        raise RuntimeError(f"too few crown material polygons: {crown_polys}")

    now_face = {o.name: signature(o) for o in bpy.data.objects if protected_face(o)}
    if set(now_face) != set(locked_face):
        raise RuntimeError("FACE LOCK: protected object set changed")
    changed_face = [n for n in locked_face if locked_face[n] != now_face[n]]
    if changed_face:
        raise RuntimeError("FACE LOCK: changed: " + ", ".join(changed_face[:20]))
    if signature(cap) != cap_sig:
        raise RuntimeError("CAP LOCK: scalp cap changed")

    # Verify every moved vertex belonged to the original spatial crown region.
    illegal = []
    for idx in moved:
        if not crown_region(before[idx], hc, hs, sign)[0]:
            illegal.append(idx)
    if illegal:
        raise RuntimeError("CROWN SCOPE: moved non-crown vertices")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r4"
        hero["hair_refinement"] = "crown-only-local-sculpt-and-texture-tint"
        hero["face_locked_for_hair_v185_r4"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r4",
        "scope": "crown-only-kappa-fix",
        "face_unchanged": True,
        "scalp_cap_unchanged": True,
        "bangs_and_ponytail_outside_crown_untouched": True,
        "crown_vertices_moved": len(moved),
        "crown_polygons_tinted": crown_polys,
        "max_crown_displacement": max_disp,
        "max_allowed_displacement": hs.z * 0.025,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R4", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
