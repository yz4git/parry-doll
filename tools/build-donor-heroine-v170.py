"""Build a fresh PARRY DOLL heroine from an empty Blender scene with a David Onizaki CC-BY anime head.

IMPORTANT: this script never imports the existing game GLB. It runs the project's procedural
Blender character generator in the same empty Blender process, then replaces the freshly generated
procedural head shell with the pinned donor head before the final export. Body, costume, hair,
weapon and runtime hierarchy are therefore rebuilt from source each run.
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
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v170.json")


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


def find_generated_head():
    exact = bpy.data.objects.get("HeadShellV140")
    if exact is not None and exact.type == "MESH":
        return exact

    candidates = []
    for obj in mesh_objects():
        if not under(obj, "BL_HEAD_ASSET"):
            continue
        mat_names = {m.name for m in getattr(obj.data, "materials", []) if m}
        if "Skin" in mat_names or "Head" in obj.name or "Face" in obj.name:
            candidates.append(obj)
    if not candidates:
        raise RuntimeError("fresh generator did not create a usable head shell under BL_HEAD_ASSET")
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

        # Elegant V jaw and a compact chin, matching the supplied front reference.
        if h < s["jaw_start_from_bottom"]:
            amount = (s["jaw_start_from_bottom"] - h) / max(s["jaw_start_from_bottom"], 1e-6)
            p.x = center.x + (p.x - center.x) * (1.0 - s["jaw_narrow_at_bottom"] * amount)
        if h < s["chin_start_from_bottom"]:
            amount = (s["chin_start_from_bottom"] - h) / max(s["chin_start_from_bottom"], 1e-6)
            p.x = center.x + (p.x - center.x) * (1.0 - s["chin_extra_narrow"] * amount)

        # Slightly soften the broad donor cheek plane without flattening the zygomatic volume.
        cheek = gaussian(h, 0.43, 0.16)
        p.x = center.x + (p.x - center.x) * (1.0 - s["cheek_soften"] * cheek)

        # OBJ import maps the donor's face toward Blender -Y. Only central forward nose points
        # are moved toward the facial plane, preserving the bridge and profile continuity.
        xnorm = abs(p.x - center.x) / max(size.x * 0.5, 1e-6)
        if xnorm < 0.23 and 0.34 < h < 0.64 and p.y < center.y:
            w = (1.0 - xnorm / 0.23) * gaussian(h, 0.49, 0.13)
            p.y += (center.y - p.y) * s["nose_projection_reduce"] * w

        # Compress only the upper-front forehead, not the skull/back-of-head mass.
        if h > s["forehead_compress_start"] and p.y < center.y:
            frontness = min(1.0, max(0.0, (center.y - p.y) / max(size.y * 0.40, 1e-6)))
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
    mod = obj.modifiers.new(name="FreshDonorFaceSubdiv", type="SUBSURF")
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
    mat = bpy.data.materials.new("DavidOnizakiAnimeSkinV170")
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
    links.new(uv_tex.outputs["Color"], bsdf.inputs["Base Color"])

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
    new_mesh.name = "DavidOnizakiFreshAnimeHeadV170Mesh"
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


def cleanup_procedural_face_overlays(cfg, head):
    tokens = tuple(cfg["cleanup"]["delete_face_overlay_tokens"])
    removed = []
    for obj in list(mesh_objects()):
        if obj == head or not under(obj, "BL_FACE_ASSET"):
            continue
        if any(token in obj.name for token in tokens):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def tune_existing_eyes(cfg):
    e = cfg["eyes"]
    tuned = []
    for obj in mesh_objects():
        if not under(obj, "BL_FACE_ASSET") or not obj.data.vertices:
            continue
        name = obj.name
        scale = None
        if any(t in name for t in ("IrisOuter", "IrisInner", "IrisRay")):
            scale = e["iris_scale"]
        elif "Pupil" in name:
            scale = e["pupil_scale"]
        if scale is None:
            continue
        center = sum((v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
        for vert in obj.data.vertices:
            vert.co = center + (vert.co - center) * scale
            # The generated face assembly also uses Blender -Y as its forward direction.
            vert.co.y -= e["iris_forward"]
        obj.data.update()
        tuned.append(obj.name)
    return tuned


def tag_hierarchy(cfg):
    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["character_revision"] = cfg["revision"]
        root["build_pipeline"] = "fresh-empty-scene-donor-head"
        root["source_glb_imported"] = False
        root["donor_author"] = cfg["donor"]["author"]
        root["donor_license"] = cfg["donor"]["license"]
    head_asset = bpy.data.objects.get("BL_HEAD_ASSET")
    if head_asset:
        head_asset["face_rebuild_revision"] = cfg["revision"]
        head_asset["head_geometry_source"] = "David Onizaki CC-BY anime female base"
        head_asset["profile_target"] = "user supplied front + exact right profile"
    face_asset = bpy.data.objects.get("BL_FACE_ASSET")
    if face_asset:
        face_asset["fresh_donor_face"] = True
        face_asset["anime_game_face_revision"] = cfg["revision"]


def live_audit(cfg):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes after fresh build: " + ", ".join(missing))
    head = find_generated_head()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"fresh donor head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"fresh donor head polygon count too small: {len(head.data.polygons)}")
    eye_meshes = [o for o in mesh_objects() if any(t in o.name for t in ("EyeSclera", "IrisOuter", "Pupil", "UpperLash"))]
    if len(eye_meshes) < cfg["audit"]["min_eye_meshes"]:
        raise RuntimeError(f"fresh build eye mesh count too small: {len(eye_meshes)}")
    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "head_bbox": bbox_dict(head),
        "eye_meshes": len(eye_meshes),
        "mesh_objects": len(mesh_objects()),
        "required_runtime_nodes": len(cfg["audit"]["required_runtime_nodes"]),
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_blend = os.path.join("/tmp", "parry-doll-fresh-donor-v170.blend")
    bpy.ops.wm.save_as_mainfile(filepath=tmp_blend)
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.0":
        raise RuntimeError("unexpected fresh donor config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    output = os.path.abspath(a.output)
    # The generator starts by deleting the Blender scene and builds the body/hair/outfit from source.
    # No bpy glTF import is called anywhere in this wrapper.
    runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v170__")

    generated_head = find_generated_head()
    generated_bbox = bbox_dict(generated_head)
    donor = import_donor_obj(os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV170"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = bbox_dict(donor)
    moved, max_delta = sculpt_donor(donor, cfg)
    subdivide(donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = bbox_dict(donor)

    skin = make_skin_material(a.donor_uv, a.donor_normal, cfg)
    fit = replace_fresh_head(generated_head, donor, cfg, skin)
    removed = cleanup_procedural_face_overlays(cfg, generated_head)
    tuned_eyes = tune_existing_eyes(cfg)
    tag_hierarchy(cfg)
    audit = live_audit(cfg)

    # make-blender-heroine.py writes an intermediate GLB/.blend; overwrite GLB with the final donor
    # geometry and remove the intermediate .blend from the repository working tree.
    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(output)

    result = {
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
        "removed_procedural_face_overlays": removed,
        "tuned_eye_meshes": tuned_eyes,
        "audit": audit,
        "output": output,
        "output_bytes": os.path.getsize(output),
    }
    print("FRESH_DONOR_V170_RESULT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
