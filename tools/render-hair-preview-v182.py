"""Render head-only CPU review views for the v18.2 Blender-chan hair candidate.

The shipping character carries large costume meshes around the head/shoulders, so a full-scene render is
not a reliable hair review.  This preview hides everything except the head subtree, protected facial
helpers and the candidate hair, then detects the actual face side from the irises instead of assuming an
axis convention after glTF round-tripping.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PREFIX = "HairPremiumV182_"


def tail_args():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--angle", type=float, default=30.0)
    return p.parse_args(tail_args())


def under(obj, ancestor_name):
    cur = obj
    while cur:
        if cur.name == ancestor_name:
            return True
        cur = cur.parent
    return False


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def mesh_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def add_area(name, loc, energy, size, target):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.shape = "DISK"
    ld.size = size
    obj = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    look_at(obj, target)
    return obj


def solid_material(name, base, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.28
    return mat


def assign_preview_material(obj, mats):
    n = obj.name.lower()
    if obj.name.startswith(PREFIX):
        mat = mats["hair"]
    elif "sclera" in n:
        mat = mats["sclera"]
    elif "iris" in n or "pupil" in n or "eyelight" in n:
        mat = mats["iris"]
    elif "lash" in n or "brow" in n or "canthus" in n:
        mat = mats["dark"]
    elif "lip" in n or "mouth" in n:
        mat = mats["lip"]
    else:
        mat = mats["skin"]
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def face_side_from_irises(head_center_y):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    if not iris:
        return -1.0, None
    ys = []
    for obj in iris:
        pts = mesh_points(obj)
        if pts:
            ys.append(sum(p.y for p in pts) / len(pts))
    if not ys:
        return -1.0, None
    iris_y = sum(ys) / len(ys)
    return (-1.0 if iris_y < head_center_y else 1.0), iris_y


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get("HeadShellV140")
    hairs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PREFIX)]
    if head is None or head.type != "MESH" or len(hairs) != 3:
        raise RuntimeError(f"preview requires HeadShellV140 + 3 v18.2 hair meshes, got {len(hairs)}")

    # Remove costume/body visual noise from the review.  Facial helpers incorrectly parented under the
    # hair root are intentionally kept; the face-lock audit protects their geometry separately.
    review_meshes = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        keep = under(obj, "BL_HEAD") or under(obj, "BL_HAIR_ASSET") or obj.name.startswith(PREFIX)
        obj.hide_render = not keep
        if keep:
            review_meshes.append(obj)

    hp = mesh_points(head)
    hlo, hhi, hcenter, hsize = bounds(hp)
    all_hair = []
    for obj in hairs:
        all_hair.extend(mesh_points(obj))
    alo, ahi, _, _ = bounds(all_hair)

    # Fit a head-and-hair portrait rather than the torso. Clamp outlier strands so the face remains large.
    max_width = hsize.x * 2.65
    max_height = hsize.z * 2.75
    lo = Vector((max(alo.x, hcenter.x - max_width * 0.5), alo.y, max(alo.z, hcenter.z - max_height * 0.55)))
    hi = Vector((min(ahi.x, hcenter.x + max_width * 0.5), ahi.y, min(ahi.z, hcenter.z + max_height * 0.60)))
    target = Vector((hcenter.x, hcenter.y, hcenter.z + hsize.z * 0.04))
    extent = max(hsize.x * 1.75, hi.x - lo.x, hi.z - lo.z)

    mats = {
        "hair": solid_material("ReviewHair", (0.045, 0.018, 0.060, 1.0), 0.30),
        "skin": solid_material("ReviewSkin", (0.54, 0.37, 0.31, 1.0), 0.58),
        "sclera": solid_material("ReviewSclera", (0.72, 0.72, 0.70, 1.0), 0.45),
        "iris": solid_material("ReviewIris", (0.05, 0.10, 0.16, 1.0), 0.28),
        "dark": solid_material("ReviewDark", (0.012, 0.009, 0.015, 1.0), 0.36),
        "lip": solid_material("ReviewLip", (0.42, 0.16, 0.18, 1.0), 0.52),
    }
    for obj in review_meshes:
        assign_preview_material(obj, mats)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 820
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.018, 0.020, 0.026)

    face_sign, iris_y = face_side_from_irises(hcenter.y)
    camera_data = bpy.data.cameras.new("HairPreviewV182Camera")
    camera = bpy.data.objects.new("HairPreviewV182Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    angle = math.radians(a.angle)
    distance = max(0.78, extent * 2.85)
    # Rotate around the detected front side.  This survives Blender/glTF axis conversions.
    camera.location = Vector((
        math.sin(angle) * distance,
        face_sign * math.cos(angle) * distance,
        target.z + extent * 0.015,
    ))
    camera_data.lens = 76
    camera_data.sensor_width = 36
    look_at(camera, target)

    add_area("Key", Vector((-extent * 1.55, face_sign * distance * 0.48, target.z + extent * 0.85)), 115, extent * 2.0, target)
    add_area("Fill", Vector((extent * 1.45, face_sign * distance * 0.35, target.z + extent * 0.10)), 65, extent * 1.8, target)
    add_area("HairRim", Vector((extent * 0.45, -face_sign * distance * 0.30, target.z + extent * 0.80)), 150, extent * 1.55, target)

    scene.view_settings.look = "AgX - Medium High Contrast"
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("HAIR_V182_PREVIEW", {
        "output": str(out),
        "bytes": out.stat().st_size,
        "hair": [o.name for o in hairs],
        "review_meshes": len(review_meshes),
        "face_sign_y": face_sign,
        "iris_y": iris_y,
        "head_center_y": float(hcenter.y),
    })


if __name__ == "__main__":
    main()
