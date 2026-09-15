"""Fit evaluated Blender-chan CC0 anime hair to Parry Doll without changing the face.

Input heroine GLB must be the last accepted face-locked base.  Existing hairstyle meshes are removed,
but facial helpers are protected even when they happen to be parented under BL_HAIR_ASSET.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

DONOR_NAMES = ("BC_HairMain", "BC_HairBun", "BC_HairRigged")
FINAL_NAMES = {
    "BC_HairMain": "HairPremiumV182_Main",
    "BC_HairBun": "HairPremiumV182_Bun",
    "BC_HairRigged": "HairPremiumV182_Strands",
}
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
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--donor", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def under(obj, ancestor_name):
    cur = obj
    while cur:
        if cur.name == ancestor_name:
            return True
        cur = cur.parent
    return False


def hair_name(obj):
    n = obj.name.lower()
    return any(token in n for token in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(token in n for token in HAIR_MARKERS):
        return False
    return any(token in n for token in FACE_MARKERS)


def is_protected_head_mesh(obj):
    if obj.type != "MESH":
        return False
    # Name-based protection wins even if an old facial helper was incorrectly placed under hair root.
    if face_name(obj):
        return True
    return under(obj, "BL_HEAD") and not hair_name(obj) and not obj.name.startswith("BC_Hair")


def canonical_points(obj, digits=6):
    mw = obj.matrix_world
    return tuple(sorted({
        (
            round(float((mw @ v.co).x), digits),
            round(float((mw @ v.co).y), digits),
            round(float((mw @ v.co).z), digits),
        )
        for v in obj.data.vertices
    }))


def protected_signature():
    sig = {}
    for obj in bpy.data.objects:
        if is_protected_head_mesh(obj):
            sig[obj.name] = {
                "points": canonical_points(obj),
                "parent": obj.parent.name if obj.parent else None,
                "verts": len(obj.data.vertices),
            }
    if "HeadShellV140" not in sig:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing from protected signature")
    return sig


def world_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    if not points:
        raise RuntimeError("empty bounds")
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def vec(v):
    return [float(v.x), float(v.y), float(v.z)]


def remove_old_hair():
    removed = []
    preserved_face_helpers = []
    hair_root = bpy.data.objects.get("BL_HAIR_ASSET")
    if hair_root is None:
        raise RuntimeError("BL_HAIR_ASSET missing")
    # Work on meshes only. Empty dynamic helpers can remain harmlessly; removing a parent could move or
    # orphan protected facial helpers.  Every mesh under the hair root that is not a face component is
    # old hairstyle geometry and is replaced.
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not under(obj, "BL_HAIR_ASSET"):
            continue
        if face_name(obj):
            preserved_face_helpers.append(obj.name)
            continue
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    return sorted(removed), sorted(preserved_face_helpers)


def import_donor(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    new_objects = [o for o in bpy.data.objects if o not in before]
    meshes = {}
    for wanted in DONOR_NAMES:
        obj = bpy.data.objects.get(wanted)
        if obj is None:
            # glTF can suffix names if a stale object exists. Search among new objects only.
            matches = [o for o in new_objects if o.type == "MESH" and o.name.startswith(wanted)]
            obj = matches[0] if matches else None
        if obj is None or obj.type != "MESH":
            raise RuntimeError(f"donor component missing after import: {wanted}")
        meshes[wanted] = obj
    return meshes


def transform_objects(objects, matrix):
    for obj in objects:
        obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()


def orient_donor(meshes):
    main = meshes["BC_HairMain"]
    rigged = meshes["BC_HairRigged"]
    _, _, main_center, _ = bounds(world_points(main))
    _, _, rigged_center, _ = bounds(world_points(rigged))
    # Parry Doll faces -Y, so the substantial back/strand mass should sit toward +Y relative to the cap.
    delta_y = rigged_center.y - main_center.y
    rotated = False
    if delta_y < 0:
        pivot = main_center
        matrix = Matrix.Translation(pivot) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-pivot)
        transform_objects(meshes.values(), matrix)
        rotated = True
    return rotated, float(delta_y)


def fit_to_head(meshes, head):
    hlo, hhi, hcenter, hsize = bounds(world_points(head))
    main = meshes["BC_HairMain"]
    mlo, mhi, mcenter, msize = bounds(world_points(main))
    if msize.x <= 1e-8:
        raise RuntimeError("invalid Blender-chan Hair Main width")

    scale = (hsize.x * 1.105) / msize.x
    transform_objects(meshes.values(), Matrix.Scale(scale, 4))

    mlo, mhi, mcenter, msize = bounds(world_points(main))
    target_center = Vector((hcenter.x, hcenter.y + hsize.y * 0.015, hcenter.z))
    # Match cap center horizontally/depth-wise, then put its top a little above the immutable scalp.
    translation = Vector((
        target_center.x - mcenter.x,
        target_center.y - mcenter.y,
        (hhi.z + hsize.z * 0.035) - mhi.z,
    ))
    transform_objects(meshes.values(), Matrix.Translation(translation))

    final = {}
    for name, obj in meshes.items():
        lo, hi, center, size = bounds(world_points(obj))
        final[name] = {"min": vec(lo), "max": vec(hi), "center": vec(center), "size": vec(size)}

    main_size = Vector(final["BC_HairMain"]["size"])
    if not (hsize.x * 0.95 <= main_size.x <= hsize.x * 1.25):
        raise RuntimeError(f"hair cap width guardrail failed: {main_size.x} vs head {hsize.x}")
    # The rigged strand volume may be long/wide, but it must at least overlap the head region.
    rlo = Vector(final["BC_HairRigged"]["min"])
    rhi = Vector(final["BC_HairRigged"]["max"])
    if rhi.z < hlo.z or rlo.z > hhi.z + hsize.z:
        raise RuntimeError("Blender-chan strands do not overlap head vertically")
    return {
        "scale": float(scale),
        "head": {"min": vec(hlo), "max": vec(hhi), "center": vec(hcenter), "size": vec(hsize)},
        "components": final,
    }


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def decimate_to_total(meshes, target_total=108000):
    counts_before = {name: tri_count(obj) for name, obj in meshes.items()}
    fixed = counts_before["BC_HairMain"] + counts_before["BC_HairBun"]
    rigged = meshes["BC_HairRigged"]
    rigged_before = counts_before["BC_HairRigged"]
    target_rigged = max(50000, target_total - fixed)
    if rigged_before > target_rigged:
        mod = rigged.modifiers.new("HairPremiumV182_MobileBudget", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = max(0.1, min(1.0, target_rigged / rigged_before))
        mod.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = rigged
        rigged.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        rigged.select_set(False)
    counts_after = {name: tri_count(obj) for name, obj in meshes.items()}
    total = sum(counts_after.values())
    if total < 70000:
        raise RuntimeError(f"premium hair lost too much authored detail: {total} tris")
    if total > 125000:
        raise RuntimeError(f"premium hair exceeds mobile budget: {total} tris")
    return counts_before, counts_after, total


def make_material():
    mat = bpy.data.materials.get("HairPremiumV182") or bpy.data.materials.new("HairPremiumV182")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": (0.018, 0.010, 0.018, 1.0),
            "Roughness": 0.34,
            "Metallic": 0.0,
            "IOR": 1.46,
            "Anisotropic IOR Level": 0.38,
            "Coat Weight": 0.07,
            "Coat Roughness": 0.22,
        }
        for key, value in values.items():
            inp = bsdf.inputs.get(key)
            if inp is not None:
                inp.default_value = value
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.30
    return mat


def finalize(meshes, hair_root):
    mat = make_material()
    for source_name, obj in meshes.items():
        obj.name = FINAL_NAMES[source_name]
        obj.data.name = FINAL_NAMES[source_name] + "Mesh"
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for poly in obj.data.polygons:
            poly.use_smooth = True
        world = obj.matrix_world.copy()
        obj.parent = hair_root
        obj.matrix_world = world


def export_glb(path):
    out = Path(path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
    )


def main():
    a = parse_args()
    inp, donor, out = Path(a.input).resolve(), Path(a.donor).resolve(), Path(a.output).resolve()
    if not inp.is_file() or not donor.is_file():
        raise RuntimeError(f"missing input/donor: {inp} / {donor}")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(inp))
    head = bpy.data.objects.get("HeadShellV140")
    hair_root = bpy.data.objects.get("BL_HAIR_ASSET")
    if head is None or head.type != "MESH" or hair_root is None:
        raise RuntimeError("accepted heroine head/hair root missing")

    face_before = protected_signature()
    removed, preserved_helpers = remove_old_hair()
    # Deletion is not allowed to affect any protected face helper.
    for name in face_before:
        if bpy.data.objects.get(name) is None:
            raise RuntimeError(f"FACE LOCK: protected object removed while clearing old hair: {name}")

    meshes = import_donor(donor)
    rotated, donor_back_delta = orient_donor(meshes)
    fit = fit_to_head(meshes, head)
    counts_before, counts_after, total = decimate_to_total(meshes)
    finalize(meshes, hair_root)

    face_after = protected_signature()
    if face_before != face_after:
        changed = sorted(k for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k))
        raise RuntimeError("FACE LOCK: protected geometry changed before export: " + ", ".join(changed[:30]))

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["hair_revision"] = "v18.2"
        root["hair_source"] = "Blender-chan / Amarillo / CC0 / evaluated Amarillo Hair Geometry Nodes"
        root["face_locked_for_hair_v182"] = True
        root["hair_static_visual_priority"] = True

    export_glb(out)
    report = {
        "revision": "v18.2",
        "source": "Blender-chan: Free Blender character",
        "source_author": "Amarillo",
        "source_url": "https://amarilloarts.itch.io/blender-chan",
        "license": "CC0",
        "source_components": list(DONOR_NAMES),
        "removed_previous_hair_count": len(removed),
        "removed_previous_hair": removed,
        "preserved_face_helpers_under_hair_root": preserved_helpers,
        "protected_face_meshes": len(face_before),
        "donor_back_delta_before_orientation": donor_back_delta,
        "rotated_180": rotated,
        "triangles_before_budget": counts_before,
        "triangles_after_budget": counts_after,
        "triangles_total": total,
        "fit": fit,
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_BLENDERCHAN_V182_BUILD", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
