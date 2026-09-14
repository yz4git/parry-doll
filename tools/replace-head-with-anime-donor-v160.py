"""Replace only the imported PARRY DOLL face/head shell with a legal anime-game donor head.

Pipeline:
1. Import the *current shipped* heroine GLB into Blender.
2. Import a CC-BY David Onizaki anime head extracted from the pinned Godot carrier repo.
3. Fit/sculpt that head to the current heroine's head envelope and supplied key-art direction.
4. Keep the existing BLENDER_HEROINE / BL_HEAD / BL_HEAD_ASSET / BL_FACE_ASSET hierarchy.
5. Reuse the existing eyes/hair/body, while removing old procedural lid overlays that clash with
   the donor's much better eye sockets.
6. Export the same game GLB path.

The donor attribution is preserved in docs/THIRD_PARTY_FACE_V160.md and in GLB custom properties.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from mathutils import Matrix, Vector

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MODEL = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-face-donor-v160.json")


def args_after_double_dash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=DEFAULT_MODEL)
    p.add_argument("--output", default=DEFAULT_MODEL)
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)
    p.add_argument("--donor-normal", required=True)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    p.add_argument("--audit-only", action="store_true")
    return p.parse_args(args_after_double_dash())


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_glb(path):
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=path)


def import_obj(path):
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.obj_import(filepath=path)
    except (AttributeError, RuntimeError):
        bpy.ops.import_scene.obj(filepath=path, axis_forward="-Z", axis_up="Y")
    added = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not added:
        raise RuntimeError("OBJ import produced no mesh object")
    return max(added, key=lambda o: len(o.data.vertices))


def mesh_objects():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def find_head():
    exact = bpy.data.objects.get("HeadShellV140")
    if exact and exact.type == "MESH":
        return exact
    candidates = [o for o in mesh_objects() if "HeadShell" in o.name or o.get("face_rebuild")]
    if not candidates:
        raise RuntimeError("current game head shell was not found")
    return max(candidates, key=lambda o: len(o.data.vertices))


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
        "min": [round(v, 6) for v in lo],
        "max": [round(v, 6) for v in hi],
        "size": [round(v, 6) for v in size],
        "center": [round(v, 6) for v in center],
    }


def smoothstep(a, b, x):
    if a == b:
        return 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def gaussian(x, center, radius):
    if radius <= 0:
        return 0.0
    d = (x - center) / radius
    return math.exp(-(d * d))


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

        if h < s["jaw_start_from_bottom"]:
            amount = (s["jaw_start_from_bottom"] - h) / s["jaw_start_from_bottom"]
            p.x = center.x + (p.x - center.x) * (1.0 - s["jaw_narrow_at_bottom"] * amount)
        if h < s["chin_start_from_bottom"]:
            amount = (s["chin_start_from_bottom"] - h) / s["chin_start_from_bottom"]
            p.x = center.x + (p.x - center.x) * (1.0 - s["chin_extra_narrow"] * amount)

        cheek = gaussian(h, 0.42, 0.16)
        p.x = center.x + (p.x - center.x) * (1.0 - s["cheek_soften"] * cheek)

        # OBJ import maps the donor's -Z-forward convention to Blender -Y-forward.
        # Reduce only a small central protrusion; the donor already has a good anime nose.
        xnorm = abs(p.x - center.x) / max(size.x * 0.5, 1e-6)
        if xnorm < 0.23 and 0.34 < h < 0.63 and p.y < center.y:
            nose_w = (1.0 - xnorm / 0.23) * gaussian(h, 0.49, 0.13)
            p.y += (center.y - p.y) * s["front_nose_reduce"] * nose_w

        d = (p - old).length
        if d > 1e-7:
            moved += 1
            max_delta = max(max_delta, d)
            vert.co = inv @ p
    obj.data.update()
    return moved, max_delta


def add_subdivision(obj, levels):
    if levels <= 0:
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod = obj.modifiers.new(name="AnimeFaceSubdiv", type="SUBSURF")
    mod.subdivision_type = "CATMULL_CLARK"
    mod.levels = levels
    mod.render_levels = levels
    mod.show_only_control_edges = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.select_set(False)


def make_skin_material(uv_path, normal_path, cfg):
    surface = cfg["surface"]
    mat = bpy.data.materials.new("AnimeFaceSkinV160")
    mat.use_nodes = True
    mat.diffuse_color = (1.0, 0.88, 0.86, 1.0)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = surface["roughness"]
    if "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = surface["specular"]
    if "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = surface["subsurface"]

    uv_img = bpy.data.images.load(os.path.abspath(uv_path), check_existing=True)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = uv_img
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    normal_img = bpy.data.images.load(os.path.abspath(normal_path), check_existing=True)
    normal_img.colorspace_settings.name = "Non-Color"
    ntex = nodes.new("ShaderNodeTexImage")
    ntex.image = normal_img
    ntex.interpolation = "Linear"
    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = surface["normal_strength"]
    links.new(ntex.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def fit_and_replace(current_head, donor, cfg, material):
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

    new_data = donor.data.copy()
    new_data.name = "AnimeGameHeadV160Mesh"
    new_data.transform(donor_to_head_local)
    new_data.materials.clear()
    new_data.materials.append(material)

    old_data = current_head.data
    current_head.data = new_data
    current_head["face_rebuild"] = cfg["revision"]
    current_head["face_style"] = "CC-BY anime-game donor + Blender sculpt"
    current_head["donor_author"] = cfg["donor"]["author"]
    current_head["donor_source"] = cfg["donor"]["source"]
    current_head["donor_license"] = cfg["donor"]["license"]
    current_head["donor_carrier_commit"] = cfg["donor"]["carrier_commit"]

    bpy.data.objects.remove(donor, do_unlink=True)
    if old_data.users == 0:
        bpy.data.meshes.remove(old_data)
    return {"scale": [sx, sy, sz], "target_center": list(target_center)}


def has_ancestor(obj, name):
    p = obj.parent
    while p is not None:
        if p.name == name:
            return True
        p = p.parent
    return False


def cleanup_old_face_overlays(cfg, head):
    tokens = tuple(cfg["cleanup"]["delete_face_overlay_tokens"])
    removed = []
    for obj in list(mesh_objects()):
        if obj == head:
            continue
        if not has_ancestor(obj, "BL_FACE_ASSET"):
            continue
        if any(t in obj.name for t in tokens):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def tune_eye_meshes(cfg):
    ecfg = cfg["eyes"]
    results = []
    for obj in mesh_objects():
        name = obj.name
        if not has_ancestor(obj, "BL_FACE_ASSET"):
            continue
        factor = None
        if any(t in name for t in ("IrisOuter", "IrisInner", "IrisRay")):
            factor = ecfg["iris_scale"]
        elif "Pupil" in name:
            factor = ecfg["pupil_scale"]
        if factor is None or not obj.data.vertices:
            continue
        center = sum((v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
        for v in obj.data.vertices:
            v.co = center + (v.co - center) * factor
            v.co.y -= ecfg["iris_forward"]
        obj.data.update()
        results.append(obj.name)
    return results


def tag_hierarchy(cfg):
    for name in ("BLENDER_HEROINE", "BL_HEAD", "BL_HEAD_ASSET", "BL_FACE_ASSET"):
        obj = bpy.data.objects.get(name)
        if obj:
            obj["face_revision"] = cfg["revision"]
    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["face_source_policy"] = "CC-BY donor head, transformed and modified in Blender"


def audit(cfg):
    required = ["BLENDER_HEROINE", "BL_HEAD", "BL_HEAD_ASSET", "BL_FACE_ASSET"]
    missing = [n for n in required if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = find_head()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head too low density: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")
    eye_meshes = [o for o in mesh_objects() if any(t in o.name for t in ("EyeSclera", "IrisOuter", "Pupil", "UpperLash"))]
    if len(eye_meshes) < cfg["audit"]["min_eye_meshes"]:
        raise RuntimeError(f"not enough eye meshes: {len(eye_meshes)}")
    return {
        "revision": head.get("face_rebuild", "unknown"),
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "head_bbox": bbox_dict(head),
        "eye_meshes": len(eye_meshes),
        "mesh_objects": len(mesh_objects()),
    }


def export_glb(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blend_path = os.path.splitext(path)[0] + "-face-v160.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v16.0":
        raise RuntimeError("unexpected v16 donor config")

    import_glb(os.path.abspath(a.input))
    if a.audit_only:
        print("FACE_V160_AUDIT", json.dumps(audit(cfg), sort_keys=True))
        return

    current_head = find_head()
    before = {"head": bbox_dict(current_head), "audit": audit({**cfg, "audit": {**cfg["audit"], "min_head_vertices": 1, "min_head_polygons": 1}})}

    donor = import_obj(os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_AnimeHead_Source"
    donor["license"] = cfg["donor"]["license"]
    donor["author"] = cfg["donor"]["author"]
    donor["source"] = cfg["donor"]["source"]
    donor_bbox_before = bbox_dict(donor)
    moved, max_delta = sculpt_donor(donor, cfg)
    add_subdivision(donor, int(cfg["surface"]["subdivision_levels"]))
    donor_bbox_after = bbox_dict(donor)
    material = make_skin_material(a.donor_uv, a.donor_normal, cfg)
    fit_result = fit_and_replace(current_head, donor, cfg, material)
    removed = cleanup_old_face_overlays(cfg, current_head)
    tuned_eyes = tune_eye_meshes(cfg)
    tag_hierarchy(cfg)
    after = audit(cfg)

    export_glb(os.path.abspath(a.output))
    print("FACE_V160_RESULT", json.dumps({
        "before": before,
        "donor_bbox_before": donor_bbox_before,
        "donor_bbox_after_sculpt_subdiv": donor_bbox_after,
        "donor_vertices_moved": moved,
        "donor_max_sculpt_delta": round(max_delta, 7),
        "fit": fit_result,
        "removed_overlays": removed,
        "tuned_eye_meshes": tuned_eyes,
        "after": after,
        "output_bytes": os.path.getsize(a.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
