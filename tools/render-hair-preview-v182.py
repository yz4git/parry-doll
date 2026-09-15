"""Render CPU-only review views for the v18.2 Blender-chan hair candidate."""
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


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get("HeadShellV140")
    hairs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PREFIX)]
    if head is None or head.type != "MESH" or len(hairs) != 3:
        raise RuntimeError(f"preview requires HeadShellV140 + 3 v18.2 hair meshes, got {len(hairs)}")

    # Frame the head and most of the hair, but do not let an accidental distant stray vertex turn the
    # face into a tiny dot.  Clamp the target extent against a reasonable multiple of head size.
    hp = mesh_points(head)
    hlo, hhi, hcenter, hsize = bounds(hp)
    all_hair = []
    for obj in hairs:
        all_hair.extend(mesh_points(obj))
    alo, ahi, acenter, asize = bounds(all_hair)
    max_width = hsize.x * 4.2
    max_height = hsize.z * 4.3
    lo = Vector((max(alo.x, hcenter.x - max_width * 0.5), alo.y, max(alo.z, hcenter.z - max_height * 0.62)))
    hi = Vector((min(ahi.x, hcenter.x + max_width * 0.5), ahi.y, min(ahi.z, hcenter.z + max_height * 0.58)))
    target = Vector((hcenter.x, (hcenter.y + (alo.y + ahi.y) * 0.5) * 0.5, (lo.z + hi.z) * 0.5))
    extent = max(hsize.x * 2.15, hi.x - lo.x, hi.z - lo.z)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 820
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.045, 0.050, 0.060)

    camera_data = bpy.data.cameras.new("HairPreviewV182Camera")
    camera = bpy.data.objects.new("HairPreviewV182Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    angle = math.radians(a.angle)
    distance = max(0.95, extent * 3.15)
    # The character faces -Y. Positive X angle exposes the left side and rear hair volume.
    camera.location = Vector((math.sin(angle) * distance, -math.cos(angle) * distance, target.z + extent * 0.025))
    camera_data.lens = 72
    camera_data.sensor_width = 36
    look_at(camera, target)

    add_area("Key", Vector((-extent * 1.7, -distance * 0.42, target.z + extent * 1.05)), 620, extent * 2.4, target)
    add_area("Fill", Vector((extent * 1.65, -distance * 0.30, target.z + extent * 0.20)), 300, extent * 2.1, target)
    add_area("HairRim", Vector((extent * 0.55, distance * 0.32, target.z + extent * 0.95)), 760, extent * 1.8, target)

    scene.view_settings.look = "AgX - Medium High Contrast"
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("HAIR_V182_PREVIEW", str(out), out.stat().st_size, [o.name for o in hairs])


if __name__ == "__main__":
    main()
