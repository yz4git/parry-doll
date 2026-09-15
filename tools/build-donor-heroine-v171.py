"""Fresh PARRY DOLL heroine v17.1 portrait pass.

The previous shipping GLB is never imported.  The script starts from the repository's empty-scene
procedural Blender generator, imports only the pinned David Onizaki CC-BY donor OBJ, sculpts/fits
that head, removes the old generator-specific portrait overlays, and rebuilds eyes/lips against the
*actual fitted donor surface* before exporting the game's shipping GLB.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import runpy
import sys
from mathutils import Matrix, Vector

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATOR = os.path.join(ROOT, "tools", "make-blender-heroine.py")
DEFAULT_OUTPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v171.json")


def argv_after_double_dash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)
    p.add_argument("--donor-normal", required=True)
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(argv_after_double_dash())


def mesh_objects():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def under(obj, ancestor_name):
    q = obj.parent
    while q is not None:
        if q.name == ancestor_name:
            return True
        q = q.parent
    return False


def world_bbox(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not pts:
        raise RuntimeError(f"empty mesh: {obj.name}")
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def bbox_dict(obj):
    lo, hi = world_bbox(obj)
    size = hi - lo
    center = (lo + hi) * 0.5
    return {
        "min": [round(float(v), 6) for v in lo],
        "max": [round(float(v), 6) for v in hi],
        "size": [round(float(v), 6) for v in size],
        "center": [round(float(v), 6) for v in center],
    }


def smoothstep(a, b, x):
    if abs(b - a) < 1e-9:
        return 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def gaussian(v, center, radius):
    if radius <= 0:
        return 0.0
    d = (v - center) / radius
    return math.exp(-(d * d))


def logical_from_blender(co):
    # Repository generator bpos((x,y,z)) == (x,-z,y).
    return Vector((float(co.x), float(co.z), float(-co.y)))


def find_generated_head():
    exact = bpy.data.objects.get("HeadShellV140")
    if exact is not None and exact.type == "MESH":
        return exact
    candidates = []
    for obj in mesh_objects():
        if not under(obj, "BL_HEAD_ASSET"):
            continue
        mats = {m.name for m in getattr(obj.data, "materials", []) if m}
        if "Skin" in mats or "Head" in obj.name or "Face" in obj.name:
            candidates.append(obj)
    if not candidates:
        raise RuntimeError("fresh generator did not create a usable head shell")
    return max(candidates, key=lambda o: len(o.data.vertices))


def import_donor_obj(path):
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.obj_import(filepath=path)
    except (AttributeError, RuntimeError):
        bpy.ops.import_scene.obj(filepath=path, axis_forward="-Z", axis_up="Y")
    added = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not added:
        raise RuntimeError("donor OBJ import produced no mesh")
    return max(added, key=lambda o: len(o.data.vertices))


def sculpt_donor(obj, cfg):
    s = cfg["sculpt"]
    lo, hi = world_bbox(obj)
    size = hi - lo
    center = (lo + hi) * 0.5
    inv = obj.matrix_world.inverted()
    moved = 0
    max_delta = 0.0

    for vert in obj.data.vertices:
        p = obj.matrix_world @ vert.co
        old = p.copy()
        h = (p.z - lo.z) / max(size.z, 1e-6)
        xnorm = abs(p.x - center.x) / max(size.x * 0.5, 1e-6)
        frontness = min(1.0, max(0.0, (center.y - p.y) / max(size.y * 0.42, 1e-6)))

        if h < s["jaw_start_from_bottom"]:
            amount = (s["jaw_start_from_bottom"] - h) / max(s["jaw_start_from_bottom"], 1e-6)
            p.x = center.x + (p.x - center.x) * (1.0 - s["jaw_narrow_at_bottom"] * amount)
        if h < s["chin_start_from_bottom"]:
            amount = (s["chin_start_from_bottom"] - h) / max(s["chin_start_from_bottom"], 1e-6)
            p.x = center.x + (p.x - center.x) * (1.0 - s["chin_extra_narrow"] * amount)

        cheek = gaussian(h, 0.43, 0.16)
        p.x = center.x + (p.x - center.x) * (1.0 - s["cheek_soften"] * cheek)

        # v17.0 profile was too flat.  Add restrained adult anime bridge/tip/lip/chin projection
        # rather than pushing the donor nose back toward the face plane.
        centre_mask = max(0.0, 1.0 - xnorm / max(s["nose_center_radius_x"], 1e-6))
        if p.y < center.y and centre_mask > 0.0:
            bridge = gaussian(h, s["bridge_center_h"], s["bridge_radius_h"])
            tip = gaussian(h, s["nose_tip_center_h"], s["nose_tip_radius_h"])
            philtrum = gaussian(h, s["philtrum_center_h"], s["philtrum_radius_h"])
            upper_lip = gaussian(h, s["upper_lip_center_h"], s["upper_lip_radius_h"])
            lower_lip = gaussian(h, s["lower_lip_center_h"], s["lower_lip_radius_h"])
            chin = gaussian(h, s["chin_center_h"], s["chin_radius_h"])
            p.y -= centre_mask * frontness * (
                s["bridge_forward"] * bridge
                + s["nose_tip_forward"] * tip
                + s["upper_lip_forward"] * upper_lip
                + s["lower_lip_forward"] * lower_lip
                + s["chin_forward"] * chin
            )
            p.y += centre_mask * frontness * s["philtrum_recess"] * philtrum

        if h > s["forehead_compress_start"] and p.y < center.y:
            t = smoothstep(s["forehead_compress_start"], 1.0, h)
            p.z -= size.z * s["forehead_compress"] * t * frontness

        delta = (p - old).length
        if delta > 1e-7:
            moved += 1
            max_delta = max(max_delta, delta)
            vert.co = inv @ p

    obj.data.update()
    return moved, max_delta


def subdivide(obj, levels):
    if levels <= 0:
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod = obj.modifiers.new(name="FreshDonorFaceSubdivV171", type="SUBSURF")
    mod.subdivision_type = "CATMULL_CLARK"
    mod.levels = levels
    mod.render_levels = levels
    mod.show_only_control_edges = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.select_set(False)


def set_principled_input(bsdf, names, value):
    for name in names:
        inp = bsdf.inputs.get(name)
        if inp is not None:
            inp.default_value = value
            return True
    return False


def make_skin_material(uv_path, normal_path, cfg):
    s = cfg["surface"]
    mat = bpy.data.materials.new("DavidOnizakiAnimeSkinV171")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = s["roughness"]
    set_principled_input(bsdf, ("Specular IOR Level", "Specular"), s["specular"])
    set_principled_input(bsdf, ("Subsurface Weight", "Subsurface"), s["subsurface"])

    uv_img = bpy.data.images.load(os.path.abspath(uv_path), check_existing=True)
    uv_tex = nodes.new("ShaderNodeTexImage")
    uv_tex.image = uv_img
    uv_tex.interpolation = "Linear"
    tint = nodes.new("ShaderNodeMixRGB")
    tint.blend_type = "MULTIPLY"
    tint.inputs[0].default_value = s["warm_tint_mix"]
    tint.inputs[2].default_value = s["warm_tint"]
    links.new(uv_tex.outputs["Color"], tint.inputs[1])
    links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])

    normal_img = bpy.data.images.load(os.path.abspath(normal_path), check_existing=True)
    try:
        normal_img.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = normal_img
    normal_tex.interpolation = "Linear"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = s["normal_strength"]
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def replace_fresh_head(current_head, donor, cfg, material):
    fit = cfg["fit"]
    target_lo, target_hi = world_bbox(current_head)
    donor_lo, donor_hi = world_bbox(donor)
    target_size = target_hi - target_lo
    donor_size = donor_hi - donor_lo
    target_center = (target_lo + target_hi) * 0.5
    donor_center = (donor_lo + donor_hi) * 0.5

    sx = (target_size.x / max(donor_size.x, 1e-6)) * fit["width_factor"]
    sz = (target_size.z / max(donor_size.z, 1e-6)) * fit["height_factor"]
    sy = ((sx + sz) * 0.5) * fit["depth_factor_from_uniform"]
    target_center += Vector((fit["center_x_offset"], fit["center_y_offset"], fit["center_z_offset"]))
    fit_world = (
        Matrix.Translation(target_center)
        @ Matrix.Diagonal(Vector((sx, sy, sz, 1.0)))
        @ Matrix.Translation(-donor_center)
    )
    donor_to_head_local = current_head.matrix_world.inverted() @ fit_world @ donor.matrix_world

    new_mesh = donor.data.copy()
    new_mesh.name = "DavidOnizakiFreshAnimeHeadV171Mesh"
    new_mesh.transform(donor_to_head_local)
    new_mesh.materials.clear()
    new_mesh.materials.append(material)

    old_mesh = current_head.data
    current_head.data = new_mesh
    current_head["face_rebuild"] = cfg["revision"]
    current_head["fresh_build"] = True
    current_head["source_glb_imported"] = False
    current_head["donor_author"] = cfg["donor"]["author"]
    current_head["donor_license"] = cfg["donor"]["license"]
    current_head["donor_source"] = cfg["donor"]["source"]
    current_head["donor_carrier_commit"] = cfg["donor"]["carrier_commit"]
    bpy.data.objects.remove(donor, do_unlink=True)
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    return {"scale": [round(sx, 6), round(sy, 6), round(sz, 6)], "center": [round(float(v), 6) for v in target_center]}


def cleanup_old_portrait(cfg, head):
    tokens = tuple(cfg["portrait_cleanup_tokens"])
    removed = []
    for obj in list(bpy.data.objects):
        if obj == head:
            continue
        if any(token in obj.name for token in tokens):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def percentile(values, q):
    vals = sorted(values)
    if not vals:
        raise RuntimeError("cannot sample an empty face region")
    idx = int(round(max(0.0, min(1.0, q)) * (len(vals) - 1)))
    return vals[idx]


def sample_front_z(head, x, y, rx, ry, q):
    samples = []
    for v in head.data.vertices:
        p = logical_from_blender(v.co)
        nx = abs(p.x - x) / max(rx, 1e-6)
        ny = abs(p.y - y) / max(ry, 1e-6)
        if nx * nx + ny * ny <= 1.0:
            samples.append(float(p.z))
    if len(samples) < 12:
        # fall back to a wider region; donor eye openings can leave the exact centre empty.
        for v in head.data.vertices:
            p = logical_from_blender(v.co)
            if abs(p.x - x) <= rx * 1.55 and abs(p.y - y) <= ry * 1.55:
                samples.append(float(p.z))
    if len(samples) < 8:
        raise RuntimeError(f"too few donor surface samples near ({x},{y}): {len(samples)}")
    return percentile(samples, q), len(samples)


def add_dynamic_blink_lid(gen, parent_obj, name, ex, cy, rx, ry, front_z, mat):
    bpos = gen["bpos"]
    parent = gen["parent"]
    smooth = gen["smooth"]
    us = (-1.0, -0.55, 0.0, 0.55, 1.0)
    opened = []
    closed = []
    for u in us:
        bow = max(0.0, 1.0 - u * u)
        x = ex + u * rx * 0.985
        z = front_z + 0.00040 * bow
        edge = cy + ry * (0.10 + 0.82 * bow)
        top = edge + 0.0031 + 0.00035 * bow
        opened.append((x, top, z)); closed.append((x, top, z))
    for u in us:
        bow = max(0.0, 1.0 - u * u)
        x = ex + u * rx * 0.985
        z = front_z + 0.00020 * bow
        edge = cy + ry * (0.10 + 0.82 * bow)
        close_y = cy - 0.00015 + ry * 0.055 * bow
        opened.append((x, edge, z)); closed.append((x, close_y, z + 0.00018))
    for u in us:
        bow = max(0.0, 1.0 - u * u)
        x = ex + u * rx * 0.985
        z = front_z + 0.00012 * bow
        edge = cy - ry * (0.08 + 0.58 * bow)
        close_y = cy - 0.00015 + ry * 0.055 * bow + 0.00025
        opened.append((x, edge, z)); closed.append((x, close_y, z + 0.00012))
    for u in us:
        bow = max(0.0, 1.0 - u * u)
        x = ex + u * rx * 0.985
        z = front_z
        edge = cy - ry * (0.08 + 0.58 * bow)
        bottom = edge - 0.0028 - 0.00025 * bow
        opened.append((x, bottom, z)); closed.append((x, bottom, z))
    verts = [bpos(v) for v in opened]
    faces = []
    for i in range(4):
        faces.append((i, i + 1, 6 + i, 5 + i))
        faces.append((10 + i, 11 + i, 16 + i, 15 + i))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    parent(obj, parent_obj)
    obj.shape_key_add(name="Basis")
    blink = obj.shape_key_add(name="Blink")
    for i, v in enumerate(closed):
        blink.data[i].co = bpos(v)
    obj["expression"] = "blink"
    obj["blink_morph"] = "Blink"
    obj["portrait_revision"] = "v17.1"
    smooth(obj)
    return obj


def build_donor_eyes(gen, head, cfg):
    e = cfg["eyes"]
    HEAD = gen["HEAD"]
    add_sphere = gen["add_sphere"]
    add_ellipse = gen["add_ellipse_surface"]
    add_rays = gen["add_iris_rays_v129"]
    add_strand = gen["add_strand"]
    SCLERA = gen["SCLERA"]
    IRIS = gen["IRIS"]
    IRIS_INNER = gen["IRIS_INNER"]
    IRIS_RAY_WARM = gen["IRIS_RAY_WARM"]
    IRIS_RAY_DARK = gen["IRIS_RAY_DARK"]
    PUPIL = gen["PUPIL"]
    HAIR = gen["HAIR"]
    FACE_DARK = gen["FACE_DARK"]
    EYE_WET = gen["EYE_WET"]
    SKIN = gen["SKIN"]

    created = []
    samples = {}
    for side in (-1, 1):
        ex = side * e["center_x"]
        surface_z, sample_count = sample_front_z(
            head, ex, e["center_y"], e["surface_sample_rx"], e["surface_sample_ry"], e["surface_percentile"]
        )
        samples[str(side)] = {"surface_z": round(surface_z, 6), "samples": sample_count}
        globe_z = surface_z - e["globe_backset"]
        iris_z = surface_z + e["iris_forward"]
        lid_z = surface_z + e["lid_front_offset"]
        lash_z = surface_z + e["lash_front_offset"]
        ex_iris = ex + side * e["aperture_rx"] * 0.025

        created.append(add_sphere(
            HEAD, f"DonorEyeScleraV171_{side}",
            (ex, e["center_y"], globe_z),
            (e["globe_radius"], e["globe_radius"], e["globe_radius"]),
            SCLERA, 48, 32
        ).name)
        created.append(add_ellipse(HEAD, f"DonorIrisOuterV171_{side}", ex_iris, e["center_y"], iris_z,
                                   e["iris_outer_rx"], e["iris_outer_ry"], IRIS, 64).name)
        created.append(add_ellipse(HEAD, f"DonorIrisInnerV171_{side}", ex_iris, e["center_y"] + 0.00015, iris_z + 0.00012,
                                   e["iris_inner_rx"], e["iris_inner_ry"], IRIS_INNER, 60).name)
        created.append(add_rays(HEAD, f"DonorIrisRaysV171_{side}", ex_iris, e["center_y"] + 0.00012, iris_z + 0.00020,
                                e["iris_inner_rx"] * 0.92, e["iris_inner_ry"] * 0.90, 0.30,
                                (IRIS_RAY_WARM, IRIS_RAY_DARK), 30).name)
        created.append(add_ellipse(HEAD, f"DonorPupilV171_{side}", ex_iris, e["center_y"] - 0.00010, iris_z + 0.00031,
                                   e["pupil_rx"], e["pupil_ry"], PUPIL, 44).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV171A_{side}", ex_iris - side * 0.0031, e["center_y"] + 0.0030,
                                   iris_z + 0.00043, 0.00120, 0.00090, SCLERA, 22).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV171B_{side}", ex_iris + side * 0.0020, e["center_y"] + 0.0010,
                                   iris_z + 0.00040, 0.00042, 0.00034, SCLERA, 18).name)

        inner = ex - side * e["aperture_rx"]
        outer = ex + side * e["aperture_rx"]
        created.append(add_strand(HEAD, f"DonorUpperLashV171_{side}", [
            (inner, e["center_y"] - e["tilt"], lash_z),
            (ex - side * 0.0020, e["center_y"] + e["aperture_ry"] * 0.96, lash_z + 0.0004),
            (outer + side * 0.0015, e["center_y"] + e["tilt"], lash_z + 0.0001)
        ], 0.00078, HAIR).name)
        created.append(add_strand(HEAD, f"DonorOuterLashV171_{side}", [
            (outer - side * 0.0020, e["center_y"] + e["tilt"] + 0.0012, lash_z),
            (outer + side * 0.0050, e["center_y"] + e["tilt"] + 0.0042, lash_z + 0.0002),
            (outer + side * 0.0090, e["center_y"] + e["tilt"] + 0.0032, lash_z)
        ], 0.00042, HAIR).name)
        created.append(add_strand(HEAD, f"DonorLowerLidV171_{side}", [
            (inner + side * 0.0030, e["center_y"] - e["tilt"] - 0.0002, lid_z),
            (ex, e["center_y"] - e["aperture_ry"] * 0.78, lid_z + 0.00012),
            (outer - side * 0.0020, e["center_y"] + e["tilt"] - 0.00015, lid_z)
        ], 0.00018, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorLidFoldV171_{side}", [
            (inner + side * 0.0045, e["center_y"] - e["tilt"] + 0.0035, lid_z - 0.0003),
            (ex, e["center_y"] + e["aperture_ry"] * 1.32, lid_z),
            (outer - side * 0.0050, e["center_y"] + e["tilt"] + 0.0032, lid_z - 0.0002)
        ], 0.00013, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorWetlineV171_{side}", [
            (inner + side * 0.0040, e["center_y"] - e["tilt"], iris_z + 0.00055),
            (ex, e["center_y"] - e["aperture_ry"] * 0.80, iris_z + 0.00058),
            (outer - side * 0.0080, e["center_y"] + e["tilt"], iris_z + 0.00054)
        ], 0.00010, EYE_WET).name)
        created.append(add_ellipse(HEAD, f"DonorCanthusV171_{side}", inner + side * 0.0012,
                                   e["center_y"] - e["tilt"] + 0.0002, iris_z + 0.00058,
                                   0.0011, 0.00048, EYE_WET, 18).name)
        blink_name = "BL_EYELID_L" if side < 0 else "BL_EYELID_R"
        created.append(add_dynamic_blink_lid(gen, HEAD, blink_name, ex, e["center_y"],
                                             e["aperture_rx"], e["aperture_ry"],
                                             surface_z + e["blink_front_offset"], SKIN).name)
    return created, samples


def build_donor_lips(gen, head, cfg):
    l = cfg["lips"]
    HEAD = gen["HEAD"]
    add_panel = gen["add_panel"]
    add_strand = gen["add_strand"]
    add_ellipse = gen["add_ellipse_surface"]
    LIP = gen["LIP"]
    FACE_DARK = gen["FACE_DARK"]
    surface_z, sample_count = sample_front_z(head, 0.0, l["center_y"], l["surface_sample_rx"],
                                             l["surface_sample_ry"], l["surface_percentile"])
    z = surface_z + l["front_offset"]
    hw = l["half_width"]
    uh = l["upper_height"]
    lh = l["lower_height"]
    cy = l["center_y"]
    created = []
    created.append(add_panel(HEAD, "DonorUpperLipV171_L", [
        (-hw, cy + 0.0002, z - 0.0005), (-hw * 0.46, cy + uh * 0.72, z + 0.0002),
        (0.0, cy + uh * 0.30, z + 0.0006), (0.0, cy - 0.0007, z + 0.0007),
        (-hw * 0.44, cy - 0.0002, z + 0.0001), (-hw * 0.96, cy - 0.0011, z - 0.00045)
    ], 0.00038, LIP).name)
    created.append(add_panel(HEAD, "DonorUpperLipV171_R", [
        (0.0, cy + uh * 0.30, z + 0.0006), (hw * 0.46, cy + uh * 0.72, z + 0.0002),
        (hw, cy + 0.0002, z - 0.0005), (hw * 0.96, cy - 0.0011, z - 0.00045),
        (hw * 0.44, cy - 0.0002, z + 0.0001), (0.0, cy - 0.0007, z + 0.0007)
    ], 0.00038, LIP).name)
    created.append(add_panel(HEAD, "DonorLowerLipV171", [
        (-hw * 0.94, cy - 0.0015, z - 0.00035), (0.0, cy - 0.0010, z + 0.00055),
        (hw * 0.94, cy - 0.0015, z - 0.00035), (hw * 0.78, cy - lh * 0.82, z - 0.00015),
        (0.0, cy - lh, z + 0.00030), (-hw * 0.78, cy - lh * 0.82, z - 0.00015)
    ], 0.00046, LIP).name)
    created.append(add_strand(HEAD, "DonorMouthSeamV171", [
        (-hw, cy - 0.0010, z + 0.00055), (-hw * 0.44, cy - 0.0007, z + 0.00078),
        (0.0, cy - 0.0010, z + 0.00090), (hw * 0.44, cy - 0.0007, z + 0.00078),
        (hw, cy - 0.0010, z + 0.00055)
    ], 0.000085, FACE_DARK).name)

    nose_z, _ = sample_front_z(head, 0.0, -0.060, 0.020, 0.016, 0.88)
    for side in (-1, 1):
        created.append(add_ellipse(HEAD, f"DonorNostrilV171_{side}", side * 0.0062, -0.0605,
                                   nose_z + 0.00075, 0.00175, 0.00062, FACE_DARK, 22).name)
    return created, {"surface_z": round(surface_z, 6), "samples": sample_count}


def retarget_fringe(cfg):
    h = cfg["hair"]
    moved = []
    for obj in bpy.data.objects:
        if any(token in obj.name for token in h["tokens"]):
            obj.location.z -= h["fringe_drop"]
            obj.scale.x *= h["fringe_width_scale"]
            obj["portrait_retarget"] = "v17.1"
            moved.append(obj.name)
    return moved


def retarget_neck(cfg):
    n = cfg["neck"]
    candidates = [o for o in bpy.data.objects if o.name == "Neck" or o.name.startswith("Neck.")]
    if not candidates:
        return []
    changed = []
    for obj in candidates:
        obj.location.z += n["raise"]
        obj.scale.x *= n["width_scale"]
        obj.scale.y *= n["width_scale"]
        obj["portrait_retarget"] = "v17.1"
        changed.append(obj.name)
    return changed


def tag_hierarchy(cfg):
    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["character_revision"] = cfg["revision"]
        root["build_pipeline"] = "fresh-empty-scene-david-onizaki-v171"
        root["source_glb_imported"] = False
        root["donor_author"] = cfg["donor"]["author"]
        root["donor_license"] = cfg["donor"]["license"]
    head_asset = bpy.data.objects.get("BL_HEAD_ASSET")
    if head_asset:
        head_asset["face_rebuild_revision"] = cfg["revision"]
        head_asset["head_geometry_source"] = "David Onizaki CC-BY anime female base"
        head_asset["profile_target"] = "supplied front + exact right profile"
    face_asset = bpy.data.objects.get("BL_FACE_ASSET")
    if face_asset:
        face_asset["fresh_donor_face"] = True
        face_asset["anime_game_face_revision"] = cfg["revision"]


def live_audit(cfg):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = find_generated_head()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")
    new_eye = [o for o in bpy.data.objects if "V171" in o.name and any(t in o.name for t in ("Eye", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in ("IrisOuterV167", "IrisInnerV167", "PupilV167", "EyeScleraGlobeV166", "EyeLightV167"))]
    new_lips = [o for o in bpy.data.objects if any(t in o.name for t in ("DonorUpperLipV171", "DonorLowerLipV171", "DonorMouthSeamV171"))]
    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"not enough v17.1 eye parts: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old v16/v17 eye parts remain: " + ", ".join(o.name for o in old_eye))
    if len(new_lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"not enough v17.1 lip parts: {len(new_lips)}")
    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "head_bbox": bbox_dict(head),
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "new_lip_parts": len(new_lips),
        "mesh_objects": len(mesh_objects()),
        "required_runtime_nodes": len(cfg["audit"]["required_runtime_nodes"]),
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/parry-doll-fresh-donor-v171.blend")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )


def main():
    a = parse_args()
    with open(a.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.1":
        raise RuntimeError("unexpected v17.1 donor config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    output = os.path.abspath(a.output)
    # This is the key invariant: fresh source build only.  No glTF import occurs in this builder.
    gen = runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v171__")

    generated_head = find_generated_head()
    generated_bbox = bbox_dict(generated_head)
    donor = import_donor_obj(os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV171"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = bbox_dict(donor)
    moved, max_delta = sculpt_donor(donor, cfg)
    subdivide(donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = bbox_dict(donor)

    skin = make_skin_material(a.donor_uv, a.donor_normal, cfg)
    fit = replace_fresh_head(generated_head, donor, cfg, skin)
    removed = cleanup_old_portrait(cfg, generated_head)
    eye_parts, eye_samples = build_donor_eyes(gen, generated_head, cfg)
    lip_parts, lip_sample = build_donor_lips(gen, generated_head, cfg)
    fringe = retarget_fringe(cfg)
    neck = retarget_neck(cfg)
    tag_hierarchy(cfg)
    audit = live_audit(cfg)

    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(output)

    print("FRESH_DONOR_V171_RESULT", json.dumps({
        "revision": cfg["revision"],
        "source_glb_imported": False,
        "generator": os.path.basename(GENERATOR),
        "donor_author": cfg["donor"]["author"],
        "donor_carrier_commit": cfg["donor"]["carrier_commit"],
        "generated_head_bbox_before_replace": generated_bbox,
        "donor_bbox_before": donor_before,
        "donor_bbox_after_sculpt_subdiv": donor_after,
        "donor_vertices_sculpted": moved,
        "donor_max_sculpt_delta": round(max_delta, 7),
        "fit": fit,
        "removed_old_portrait_parts": removed,
        "new_eye_parts": eye_parts,
        "eye_surface_samples": eye_samples,
        "new_lip_parts": lip_parts,
        "lip_surface_sample": lip_sample,
        "retargeted_fringe": fringe,
        "retargeted_neck": neck,
        "audit": audit,
        "output": output,
        "output_bytes": os.path.getsize(output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
