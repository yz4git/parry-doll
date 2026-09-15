"""Fit the standalone CC0 Anime Female Adventurer v1.2 hair to Parry Doll without editing the face.

Donor: Dawn to Dusk Games, 3D Anime Female Adventurer v1.2, CC0.
Only the distributed MeshPieces/Hair.fbx plus Hair_Base.png are imported. No donor head/body is used.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

FINAL = "HairPremiumV185_Adventurer"
HAIR_ROOT = "BL_HAIR_ASSET"

HAIR_MARKERS = (
    "hairdonor", "hairpremium", "hairrear", "hairtop", "herohair", "heropony", "herocrown",
    "ponymass", "ponyfan", "ponyfoundation", "ponywing", "ponyroot", "ponytail", "hairtie",
    "fringe", "bang", "crown", "temporal", "temple", "nape", "wisp", "strand", "lock",
    "cascade", "profileeyeframe", "profilehairornament", "referencewisp", "eyerevealfringe",
    "earfrontwisp", "bl_pony_dynamic",
)
FACE_MARKERS = (
    "headshell", "davidonizaki", "eyelid", "eyelight", "iris", "pupil", "sclera", "wetline",
    "lash", "canthus", "brow", "skinrim", "beautymark", "nose", "lip", "mouth",
    "earantihelix", "earconcha", "earhelix", "earlobefold", "eartragus", "earring",
)


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--hair", required=True)
    p.add_argument("--texture", required=True)
    p.add_argument("--output", required=True)
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
    return any(token in obj.name.lower() for token in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(token in n for token in HAIR_MARKERS):
        return False
    return any(token in n for token in FACE_MARKERS)


def protected(obj):
    if obj.type != "MESH":
        return False
    if face_name(obj):
        return True
    return under(obj, "BL_HEAD") and not hair_name(obj)


def world_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def signature(obj):
    # Exact local topology + transform + parent. Captured before any hair edit and rechecked before export.
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    return (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
            obj.parent.name if obj.parent else None)


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def iris_metrics(head_center):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    if not iris:
        raise RuntimeError("FACE LOCK: iris meshes missing")
    centers = []
    for obj in iris:
        pts = world_points(obj)
        if pts:
            _, _, c, _ = bounds(pts)
            centers.append(c)
    if not centers:
        raise RuntimeError("FACE LOCK: iris points missing")
    iris_y = sum(c.y for c in centers) / len(centers)
    face_sign = -1.0 if iris_y < head_center.y else 1.0
    return face_sign, float(iris_y)


def transform(obj, matrix):
    obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()


def remove_old_hair():
    removed, preserved = [], []
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not under(obj, HAIR_ROOT):
            continue
        if protected(obj):
            preserved.append(obj.name)
            continue
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    return sorted(removed), sorted(preserved)


def import_hair(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(Path(path).resolve()), use_anim=False)
    new_meshes = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if len(new_meshes) != 1:
        raise RuntimeError(f"donor Hair.fbx must contain exactly one mesh, got {[o.name for o in new_meshes]}")
    hair = new_meshes[0]
    # Standalone distribution is intentionally unrigged. Remove any accidental non-mesh donor objects.
    for obj in list(bpy.data.objects):
        if obj in before or obj is hair:
            continue
        bpy.data.objects.remove(obj, do_unlink=True)
    return hair


def fit_donor(hair, head, face_sign):
    hlo, hhi, hc, hs = bounds(world_points(head))
    pts = world_points(hair)
    dlo, dhi, dc, ds = bounds(pts)

    # Determine donor back from lower/long-hair mass relative to the crown. The source v1.2 export is
    # authored in character world space, so this detects orientation instead of hardcoding an axis.
    crown_cut = dhi.z - ds.z * 0.30
    lower_cut = dlo.z + ds.z * 0.48
    crown = [p for p in pts if p.z >= crown_cut]
    lower = [p for p in pts if p.z <= lower_cut]
    if not crown or not lower:
        raise RuntimeError("donor hair has insufficient crown/lower samples")
    crown_y = sum(p.y for p in crown) / len(crown)
    lower_y = sum(p.y for p in lower) / len(lower)
    donor_back_sign = 1.0 if lower_y > crown_y else -1.0
    target_back_sign = -face_sign
    rotated = False
    if donor_back_sign != target_back_sign:
        rot = Matrix.Translation(dc) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-dc)
        transform(hair, rot)
        rotated = True
        pts = world_points(hair)
        dlo, dhi, dc, ds = bounds(pts)
        crown = [p for p in pts if p.z >= dhi.z - ds.z * 0.30]

    crown_width = max(p.x for p in crown) - min(p.x for p in crown)
    if crown_width <= 1e-6:
        raise RuntimeError("invalid donor crown width")
    scale = (hs.x * 1.095) / crown_width
    if not (0.65 <= scale <= 2.6):
        raise RuntimeError(f"donor fit scale implausible: {scale}")
    transform(hair, Matrix.Scale(scale, 4))

    pts = world_points(hair)
    dlo, dhi, dc, ds = bounds(pts)
    crown = [p for p in pts if p.z >= dhi.z - ds.z * 0.30]
    crown_center_x = sum(p.x for p in crown) / len(crown)

    target_top = hhi.z + hs.z * 0.030
    head_front = hc.y + face_sign * hs.y * 0.5
    donor_front = dlo.y if face_sign < 0 else dhi.y
    # Keep the authored fringe just outside the immutable forehead surface.
    target_front = head_front + face_sign * hs.y * 0.008
    dy = target_front - donor_front
    trans = Matrix.Translation(Vector((hc.x - crown_center_x, dy, target_top - dhi.z)))
    transform(hair, trans)

    flo, fhi, fc, fs = bounds(world_points(hair))
    if fhi.z < hhi.z:
        raise RuntimeError("fitted donor does not cover crown")
    if fs.x < hs.x * 0.93 or fs.x > hs.x * 1.55:
        raise RuntimeError(f"fitted donor width implausible: hair={fs.x} head={hs.x}")
    return {
        "scale": float(scale),
        "rotated_180": rotated,
        "donor_back_sign_before_fit": donor_back_sign,
        "head": {"min": list(hlo), "max": list(hhi), "center": list(hc), "size": list(hs)},
        "hair": {"min": list(flo), "max": list(fhi), "center": list(fc), "size": list(fs)},
    }


def make_material(texture_path):
    mat = bpy.data.materials.new("HairPremiumV185Texture")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(Path(texture_path).resolve()), check_existing=False)
    tex.interpolation = "Linear"
    # Preserve the author's painted blue-violet gradients. Slight multiply tint brings it toward
    # Parry Doll's existing violet-black palette without flattening strand/value information.
    tint = nodes.new("ShaderNodeMixRGB")
    tint.blend_type = "MULTIPLY"
    tint.inputs[0].default_value = 0.26
    tint.inputs[2].default_value = (0.44, 0.30, 0.72, 1.0)
    links.new(tex.outputs["Color"], tint.inputs[1])
    links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.40
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.30
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def main():
    a = args()
    reset()
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))
    head = bpy.data.objects.get("HeadShellV140")
    root = bpy.data.objects.get(HAIR_ROOT)
    if head is None or head.type != "MESH" or root is None:
        raise RuntimeError("accepted base missing HeadShellV140 or BL_HAIR_ASSET")

    locked = {o.name: signature(o) for o in bpy.data.objects if protected(o)}
    if len(locked) < 50 or "HeadShellV140" not in locked:
        raise RuntimeError(f"FACE LOCK: suspicious protected set size {len(locked)}")
    _, _, hc, _ = bounds(world_points(head))
    face_sign, iris_y = iris_metrics(hc)
    removed, preserved = remove_old_hair()

    hair = import_hair(a.hair)
    source_tris = tri_count(hair)
    if not (1800 <= source_tris <= 5000):
        raise RuntimeError(f"unexpected donor hair triangle count: {source_tris}")
    fit = fit_donor(hair, head, face_sign)

    hair.name = FINAL
    hair.data.name = FINAL + "Mesh"
    hair.data.materials.clear()
    hair.data.materials.append(make_material(a.texture))
    for poly in hair.data.polygons:
        poly.use_smooth = True
    hair.parent = root
    bpy.context.view_layer.update()

    final_tris = tri_count(hair)
    if not (1800 <= final_tris <= 12000):
        raise RuntimeError(f"v18.5 mobile hair outside quality budget: {final_tris}")
    if len(hair.data.uv_layers) < 1:
        raise RuntimeError("v18.5 donor hair lost UVs")

    # Hard face lock immediately before export.
    now = {o.name: signature(o) for o in bpy.data.objects if protected(o)}
    if set(now) != set(locked):
        raise RuntimeError(f"FACE LOCK: protected set changed; before={len(locked)} after={len(now)}")
    changed = [name for name in locked if locked[name] != now[name]]
    if changed:
        raise RuntimeError("FACE LOCK: protected object changed: " + ", ".join(changed[:30]))

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5"
        hero["hair_source"] = "Dawn to Dusk Games Anime Female Adventurer v1.2 Hair.fbx"
        hero["hair_source_license"] = "CC0-1.0"
        hero["hair_source_url"] = "https://dawn-to-dusk-games.itch.io/3d-anime-female-adventurer"
        hero["hair_texture_source"] = "Hair_Base.png"
        hero["face_locked_for_hair_v185"] = True

    output = Path(a.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(output), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5",
        "face_locked": True,
        "protected_face_meshes": len(locked),
        "source": "Dawn to Dusk Games 3D Anime Female Adventurer v1.2",
        "license": "CC0-1.0",
        "source_hair_triangles": source_tris,
        "final_hair_triangles": final_tris,
        "uv_layers": len(hair.data.uv_layers),
        "removed_previous_hair": removed,
        "preserved_face_helpers_under_hair_root": preserved,
        "face_sign_y": face_sign,
        "iris_y": iris_y,
        "fit": fit,
        "output_bytes": output.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_ADVENTURER_V185_BUILD", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
