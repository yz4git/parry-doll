"""Render isolated head/hair CPU review views for modular anime hair v18.4."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PREFIX = "HairPremiumV184_"


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


def solid_material(name, base, roughness=0.5):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.28
    return mat


def assign_material(obj, mats):
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


def face_side(head_center_y):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    ys = []
    for obj in iris:
        pts = mesh_points(obj)
        if pts:
            ys.append(sum(p.y for p in pts) / len(pts))
    if not ys:
        return -1.0
    return -1.0 if sum(ys) / len(ys) < head_center_y else 1.0


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get("HeadShellV140")
    hairs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PREFIX)]
    if head is None or head.type != "MESH" or len(hairs) != 4:
        raise RuntimeError(f"preview requires HeadShellV140 + 4 v18.4 hair meshes, got {len(hairs)}")

    review = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        keep = under(obj, "BL_HEAD") or under(obj, "BL_HAIR_ASSET") or obj.name.startswith(PREFIX)
        obj.hide_render = not keep
        if keep:
            review.append(obj)

    hp = mesh_points(head)
    _, _, hc, hs = bounds(hp)
    hair_pts = []
    for obj in hairs:
        hair_pts.extend(mesh_points(obj))
    hlo, hhi, _, _ = bounds(hair_pts)

    max_width = hs.x * 3.0
    max_height = hs.z * 3.35
    lo = Vector((max(hlo.x, hc.x - max_width * 0.5), hlo.y, max(hlo.z, hc.z - max_height * 0.64)))
    hi = Vector((min(hhi.x, hc.x + max_width * 0.5), hhi.y, min(hhi.z, hc.z + max_height * 0.62)))
    target = Vector((hc.x, hc.y, hc.z + hs.z * 0.015))
    extent = max(hs.x * 1.9, hi.x - lo.x, hi.z - lo.z)

    mats = {
        "hair": solid_material("ReviewHairV184", (0.034, 0.012, 0.052, 1.0), 0.29),
        "skin": solid_material("ReviewSkinV184", (0.54, 0.37, 0.31, 1.0), 0.58),
        "sclera": solid_material("ReviewScleraV184", (0.72, 0.72, 0.70, 1.0), 0.45),
        "iris": solid_material("ReviewIrisV184", (0.05, 0.10, 0.16, 1.0), 0.28),
        "dark": solid_material("ReviewDarkV184", (0.012, 0.009, 0.015, 1.0), 0.36),
        "lip": solid_material("ReviewLipV184", (0.42, 0.16, 0.18, 1.0), 0.52),
    }
    for obj in review:
        assign_material(obj, mats)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 28
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 820
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.018, 0.020, 0.026)

    sign = face_side(hc.y)
    cam_data = bpy.data.cameras.new("HairPreviewV184Camera")
    cam = bpy.data.objects.new("HairPreviewV184Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    angle = math.radians(a.angle)
    distance = max(0.82, extent * 2.92)
    cam.location = Vector((math.sin(angle) * distance, sign * math.cos(angle) * distance, target.z + extent * 0.012))
    cam_data.lens = 76
    cam_data.sensor_width = 36
    look_at(cam, target)

    add_area("Key", Vector((-extent * 1.55, sign * distance * 0.48, target.z + extent * 0.85)), 115, extent * 2.0, target)
    add_area("Fill", Vector((extent * 1.45, sign * distance * 0.35, target.z + extent * 0.10)), 65, extent * 1.8, target)
    add_area("HairRim", Vector((extent * 0.45, -sign * distance * 0.30, target.z + extent * 0.80)), 150, extent * 1.55, target)

    scene.view_settings.look = "AgX - Medium High Contrast"
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("HAIR_V184_PREVIEW", str(out), out.stat().st_size, [o.name for o in hairs], "face_sign", sign)


if __name__ == "__main__":
    main()
