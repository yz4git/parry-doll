"""Render isolated head + textured v18.5 hair review views on CPU."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

FINAL = "HairPremiumV185_Adventurer"


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def args():
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


def solid_material(name, base, roughness=0.5):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.25
    return mat


def face_sign(head_center_y):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    ys = []
    for obj in iris:
        pts = mesh_points(obj)
        if pts:
            ys.append(sum(p.y for p in pts) / len(pts))
    return -1.0 if not ys or sum(ys) / len(ys) < head_center_y else 1.0


def add_area(name, loc, energy, size, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    look_at(obj, target)


def main():
    a = args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))
    head = bpy.data.objects.get("HeadShellV140")
    hair = bpy.data.objects.get(FINAL)
    if head is None or head.type != "MESH" or hair is None or hair.type != "MESH":
        raise RuntimeError("preview requires HeadShellV140 + v18.5 hair")

    review = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        keep = under(obj, "BL_HEAD") or under(obj, "BL_HAIR_ASSET") or obj is hair
        obj.hide_render = not keep
        if keep:
            review.append(obj)

    # Keep the donor's embedded textured hair material. Override only face/head helper materials so
    # geometry is readable and the hair texture can be judged honestly.
    mats = {
        "skin": solid_material("ReviewSkinV185", (0.54, 0.37, 0.31, 1.0), 0.58),
        "sclera": solid_material("ReviewScleraV185", (0.72, 0.72, 0.70, 1.0), 0.45),
        "iris": solid_material("ReviewIrisV185", (0.05, 0.10, 0.16, 1.0), 0.28),
        "dark": solid_material("ReviewDarkV185", (0.012, 0.009, 0.015, 1.0), 0.36),
        "lip": solid_material("ReviewLipV185", (0.42, 0.16, 0.18, 1.0), 0.52),
    }
    for obj in review:
        if obj is hair:
            continue
        n = obj.name.lower()
        mat = mats["skin"]
        if "sclera" in n:
            mat = mats["sclera"]
        elif "iris" in n or "pupil" in n or "eyelight" in n:
            mat = mats["iris"]
        elif "lash" in n or "brow" in n or "canthus" in n:
            mat = mats["dark"]
        elif "lip" in n or "mouth" in n:
            mat = mats["lip"]
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    _, _, hc, hs = bounds(mesh_points(head))
    hlo, hhi, _, hsize = bounds(mesh_points(hair))
    target = Vector((hc.x, hc.y, hc.z + hs.z * 0.005))
    # Do not let long rear strands shrink the face excessively in review framing.
    visible_height = min(hsize.z, hs.z * 2.65)
    visible_width = min(hsize.x, hs.x * 2.15)
    extent = max(hs.x * 1.85, visible_width, visible_height)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 30
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 820
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.018, 0.020, 0.026)

    sign = face_sign(hc.y)
    cam_data = bpy.data.cameras.new("HairPreviewV185Camera")
    cam = bpy.data.objects.new("HairPreviewV185Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    ang = math.radians(a.angle)
    distance = max(0.82, extent * 2.80)
    cam.location = Vector((math.sin(ang) * distance, sign * math.cos(ang) * distance,
                           target.z + extent * 0.01))
    cam_data.lens = 74
    cam_data.sensor_width = 36
    look_at(cam, target)

    add_area("Key", Vector((-extent * 1.5, sign * distance * 0.48, target.z + extent * 0.84)), 105, extent * 1.9, target)
    add_area("Fill", Vector((extent * 1.35, sign * distance * 0.36, target.z + extent * 0.12)), 58, extent * 1.75, target)
    add_area("HairRim", Vector((extent * 0.40, -sign * distance * 0.31, target.z + extent * 0.72)), 110, extent * 1.45, target)
    scene.view_settings.look = "AgX - Medium High Contrast"

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("HAIR_V185_PREVIEW", str(out), out.stat().st_size, "hair_bounds", list(hlo), list(hhi), "face_sign", sign)


if __name__ == "__main__":
    main()
