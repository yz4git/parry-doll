"""Render neutral hair review views without requiring a GPU/EGL context."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def tail_args():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--angle", type=float, default=22.0)
    return p.parse_args(tail_args())


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def world_bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def add_area(name, loc, energy, size, target):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
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
    hair = bpy.data.objects.get("HairPremiumV181")
    if not head or not hair:
        raise RuntimeError("preview requires HeadShellV140 and HairPremiumV181")

    lo, hi, center, size = world_bounds(head)
    hpts = [hair.matrix_world @ v.co for v in hair.data.vertices]
    hlo = Vector((min(p.x for p in hpts), min(p.y for p in hpts), min(p.z for p in hpts)))
    hhi = Vector((max(p.x for p in hpts), max(p.y for p in hpts), max(p.z for p in hpts)))
    total_lo = Vector((min(lo.x, hlo.x), min(lo.y, hlo.y), min(lo.z, hlo.z)))
    total_hi = Vector((max(hi.x, hhi.x), max(hi.y, hhi.y), max(hi.z, hhi.z)))
    target = (total_lo + total_hi) * 0.5
    extent = max(total_hi.x - total_lo.x, total_hi.z - total_lo.z)

    scene = bpy.context.scene
    # Cycles CPU works on the stock GitHub Actions runner without libEGL, unlike Eevee Next.
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.060, 0.070)

    cam_data = bpy.data.cameras.new("HairPreviewCamera")
    cam = bpy.data.objects.new("HairPreviewCamera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    angle = math.radians(a.angle)
    distance = max(0.75, extent * 3.35)
    cam.location = Vector((math.sin(angle) * distance, -math.cos(angle) * distance, target.z + extent * 0.03))
    cam_data.lens = 68
    cam_data.sensor_width = 36
    look_at(cam, target)

    add_area("Key", Vector((-extent * 2.0, -distance * 0.50, target.z + extent * 1.25)), 850, extent * 3.0, target)
    add_area("Fill", Vector((extent * 2.2, -distance * 0.30, target.z + extent * 0.35)), 430, extent * 2.5, target)
    add_area("Rim", Vector((extent * 0.6, distance * 0.30, target.z + extent * 1.45)), 950, extent * 2.0, target)

    scene.view_settings.look = "AgX - Medium High Contrast"
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("HAIR_PREVIEW_V181", out, out.stat().st_size)


if __name__ == "__main__":
    main()
