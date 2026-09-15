"""Mobile-budget entry point for modular hair v18.4.

Keeps the v18.4 donor choices and immutable-face logic, but reduces only the expensive ponytail
surface tessellation and decorative strand tubes. The crown and curtain-bang construction remain
unchanged. This targets iPhone Safari without reverting to a blocky silhouette.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

BASE = Path(__file__).with_name("build-hair-modular-v184.py")
spec = importlib.util.spec_from_file_location("hair_v184_base_r3", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {BASE}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def append_overscore_stable(path):
    canonical = ("Curtain Bangs", "High Ponytail")
    request = list(canonical)
    with bpy.data.libraries.load(str(Path(path).resolve()), link=False) as (src, dst):
        missing = [name for name in canonical if name not in src.objects]
        if missing:
            raise RuntimeError("OverScore exact hair objects missing: " + ", ".join(missing))
        dst.objects = request
    loaded = [o for o in dst.objects if o]
    if len(loaded) != len(canonical):
        raise RuntimeError(f"OverScore append count mismatch: wanted={canonical!r}, loaded={[o.name for o in loaded]!r}")
    result = {}
    for expected, obj in zip(canonical, loaded):
        if obj.type != "MESH":
            raise RuntimeError(f"OverScore {expected} loaded as {obj.type}, not MESH")
        if not obj.users_collection:
            bpy.context.scene.collection.objects.link(obj)
        else:
            try:
                bpy.context.scene.collection.objects.link(obj)
            except RuntimeError:
                pass
        mod.apply_modifiers(obj)
        result[expected] = obj
        print("V184_R3_OVERSCORE_MAP", expected, "->", obj.name)
    return result


def subdivide_mobile(obj, levels, name):
    # Curtain bangs retain level 4 because they dominate the face silhouette. The rear ponytail is
    # viewed mostly as a moving silhouette on iPhone, so level 2 is visually smooth with smooth normals.
    effective = min(levels, 2) if "Ponytail" in name else levels
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    sub = obj.modifiers.new(name + "Mobile", "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = effective
    sub.render_levels = effective
    bpy.ops.object.modifier_apply(modifier=sub.name)
    obj.select_set(False)
    for p in obj.data.polygons:
        p.use_smooth = True
    print("V184_R3_SUBDIV", name, "requested", levels, "effective", effective, "tris", mod.tri_count(obj))


def add_tail_ridges_mobile(tail, hs):
    rows = mod.tail_slice_stats(tail, slices=9)
    coll = bpy.data.collections.new("HairPremiumV184StrandsMobile")
    bpy.context.scene.collection.children.link(coll)
    curves = []
    # Nine cheap guide strands clear the existing >=800-triangle quality gate while staying far below
    # the previous eight high-resolution curves. They add visible breakup rather than hidden density.
    for j in range(9):
        theta = (j / 9.0) * math.tau + 0.19
        curve = bpy.data.curves.new(f"TailStrandCurveV184M_{j:02d}", "CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 1
        curve.bevel_depth = hs.x * (0.0044 + 0.00028 * (j % 3))
        curve.bevel_resolution = 1
        spl = curve.splines.new("BEZIER")
        spl.bezier_points.add(len(rows) - 1)
        for i, row in enumerate(rows):
            taper = 0.80 - 0.31 * (i / max(1, len(rows) - 1))
            phase = theta + math.sin(i * 0.68 + j * 0.91) * 0.065
            p = Vector((
                row["xc"] + row["rx"] * math.cos(phase) * taper,
                row["yc"] + row["ry"] * math.sin(phase) * taper,
                row["z"],
            ))
            bp = spl.bezier_points[i]
            bp.co = p
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
            bp.radius = max(0.32, 1.0 - 0.065 * i)
        obj = bpy.data.objects.new(f"TailStrandV184M_{j:02d}", curve)
        coll.objects.link(obj)
        curves.append(obj)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in curves:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.convert(target="MESH")
    converted = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if not converted:
        raise RuntimeError("mobile tail strand conversion failed")
    bpy.context.view_layer.objects.active = converted[0]
    for obj in converted:
        obj.select_set(True)
    if len(converted) > 1:
        bpy.ops.object.join()
    ridges = bpy.context.view_layer.objects.active
    ridges.name = mod.FINAL_RIDGES
    ridges.data.name = mod.FINAL_RIDGES + "Mesh"
    print("V184_R3_RIDGES tris", mod.tri_count(ridges))
    return ridges


mod.append_overscore = append_overscore_stable
mod.subdivide = subdivide_mobile
mod.add_tail_ridges = add_tail_ridges_mobile

if __name__ == "__main__":
    mod.main()
