"""Fresh PARRY DOLL heroine v17.2.

Starts from an empty Blender scene, regenerates the game character from repository source, imports
only the pinned David Onizaki CC-BY donor OBJ, then fits/sculpts that donor and builds a clean
portrait assembly on its actual surface.  The previous shipping GLB is never imported.

v17.2 specifically fixes the v17.1 visual audit issue where the donor albedo contained its own
painted eye whites underneath the new runtime eyes.  The donor normal map is retained, but the
head gets an unpainted warm skin PBR material matching the generated neck/body.  Explicit sclera
patches, larger almond irises, revised vertical eye placement, stronger profile projection, lower
fringe and the reference beauty mark are then built in Blender.
"""
from __future__ import annotations

import argparse
import json
import os
import runpy
import sys

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATOR = os.path.join(ROOT, "tools", "make-blender-heroine.py")
HELPERS = os.path.join(ROOT, "tools", "build-donor-heroine-v171.py")
DEFAULT_OUTPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v172.json")


def argv_after_double_dash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)  # verified source asset; v17.2 intentionally does not use it as albedo
    p.add_argument("--donor-normal", required=True)
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(argv_after_double_dash())


def set_principled_input(bsdf, names, value):
    for name in names:
        inp = bsdf.inputs.get(name)
        if inp is not None:
            inp.default_value = value
            return True
    return False


def make_clean_skin_material(normal_path, cfg):
    s = cfg["surface"]
    mat = bpy.data.materials.new("DavidOnizakiCleanSkinV172")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = s["base_color"]
    bsdf.inputs["Roughness"].default_value = s["roughness"]
    set_principled_input(bsdf, ("Specular IOR Level", "Specular"), s["specular"])
    set_principled_input(bsdf, ("Subsurface Weight", "Subsurface"), s["subsurface"])

    normal_img = bpy.data.images.load(os.path.abspath(normal_path), check_existing=True)
    try:
        normal_img.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = normal_img
    tex.interpolation = "Linear"
    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = s["normal_strength"]
    links.new(tex.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    mat["albedo_policy"] = "clean-unpainted-skin-v172"
    mat["donor_albedo_used"] = False
    return mat


def build_donor_eyes_v172(gen, helpers, head, cfg):
    e = cfg["eyes"]
    HEAD = gen["HEAD"]
    add_sphere = gen["add_sphere"]
    add_ellipse = gen["add_ellipse_surface"]
    add_rays = gen["add_iris_rays_v129"]
    add_strand = gen["add_strand"]
    sample_front_z = helpers["sample_front_z"]
    add_blink = helpers["add_dynamic_blink_lid"]

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
        sclera_z = surface_z + e["sclera_patch_front"]
        iris_z = surface_z + e["iris_forward"]
        lid_z = surface_z + e["lid_front_offset"]
        lash_z = surface_z + e["lash_front_offset"]
        ex_iris = ex + side * e["aperture_rx"] * 0.025

        created.append(add_sphere(
            HEAD, f"DonorEyeGlobeV172_{side}",
            (ex, e["center_y"], globe_z),
            (e["globe_radius"], e["globe_radius"], e["globe_radius"]),
            SCLERA, 48, 32
        ).name)
        # Visible surface sclera: unlike v17.1 this is guaranteed to sit in front of the donor skin.
        created.append(add_ellipse(
            HEAD, f"DonorScleraPatchV172_{side}", ex, e["center_y"], sclera_z,
            e["sclera_patch_rx"], e["sclera_patch_ry"], SCLERA, 72
        ).name)
        created.append(add_ellipse(HEAD, f"DonorIrisOuterV172_{side}", ex_iris, e["center_y"], iris_z,
                                   e["iris_outer_rx"], e["iris_outer_ry"], IRIS, 64).name)
        created.append(add_ellipse(HEAD, f"DonorIrisInnerV172_{side}", ex_iris, e["center_y"] + 0.00015, iris_z + 0.00012,
                                   e["iris_inner_rx"], e["iris_inner_ry"], IRIS_INNER, 60).name)
        created.append(add_rays(HEAD, f"DonorIrisRaysV172_{side}", ex_iris, e["center_y"] + 0.00012, iris_z + 0.00020,
                                e["iris_inner_rx"] * 0.92, e["iris_inner_ry"] * 0.90, 0.30,
                                (IRIS_RAY_WARM, IRIS_RAY_DARK), 30).name)
        created.append(add_ellipse(HEAD, f"DonorPupilV172_{side}", ex_iris, e["center_y"] - 0.00010, iris_z + 0.00031,
                                   e["pupil_rx"], e["pupil_ry"], PUPIL, 44).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV172A_{side}", ex_iris - side * 0.0032, e["center_y"] + 0.0031,
                                   iris_z + 0.00043, 0.00126, 0.00094, SCLERA, 22).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV172B_{side}", ex_iris + side * 0.0022, e["center_y"] + 0.0010,
                                   iris_z + 0.00040, 0.00045, 0.00035, SCLERA, 18).name)

        inner = ex - side * e["aperture_rx"]
        outer = ex + side * e["aperture_rx"]
        created.append(add_strand(HEAD, f"DonorUpperLashV172_{side}", [
            (inner, e["center_y"] - e["tilt"], lash_z),
            (ex - side * 0.0020, e["center_y"] + e["aperture_ry"] * 0.98, lash_z + 0.00042),
            (outer + side * 0.0016, e["center_y"] + e["tilt"], lash_z + 0.00010)
        ], 0.00082, HAIR).name)
        created.append(add_strand(HEAD, f"DonorOuterLashV172_{side}", [
            (outer - side * 0.0020, e["center_y"] + e["tilt"] + 0.0012, lash_z),
            (outer + side * 0.0055, e["center_y"] + e["tilt"] + 0.0044, lash_z + 0.00020),
            (outer + side * 0.0100, e["center_y"] + e["tilt"] + 0.0032, lash_z)
        ], 0.00046, HAIR).name)
        created.append(add_strand(HEAD, f"DonorLowerLidV172_{side}", [
            (inner + side * 0.0030, e["center_y"] - e["tilt"] - 0.0002, lid_z),
            (ex, e["center_y"] - e["aperture_ry"] * 0.76, lid_z + 0.00012),
            (outer - side * 0.0020, e["center_y"] + e["tilt"] - 0.00015, lid_z)
        ], 0.00018, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorLidFoldV172_{side}", [
            (inner + side * 0.0045, e["center_y"] - e["tilt"] + 0.0036, lid_z - 0.0003),
            (ex, e["center_y"] + e["aperture_ry"] * 1.30, lid_z),
            (outer - side * 0.0050, e["center_y"] + e["tilt"] + 0.0033, lid_z - 0.0002)
        ], 0.00013, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorWetlineV172_{side}", [
            (inner + side * 0.0040, e["center_y"] - e["tilt"], iris_z + 0.00056),
            (ex, e["center_y"] - e["aperture_ry"] * 0.77, iris_z + 0.00060),
            (outer - side * 0.0080, e["center_y"] + e["tilt"], iris_z + 0.00056)
        ], 0.00010, EYE_WET).name)
        created.append(add_ellipse(HEAD, f"DonorCanthusV172_{side}", inner + side * 0.0012,
                                   e["center_y"] - e["tilt"] + 0.0002, iris_z + 0.00060,
                                   0.00115, 0.00050, EYE_WET, 18).name)
        blink_name = "BL_EYELID_L" if side < 0 else "BL_EYELID_R"
        blink = add_blink(gen, HEAD, blink_name, ex, e["center_y"], e["aperture_rx"], e["aperture_ry"],
                          surface_z + e["blink_front_offset"], SKIN)
        blink["portrait_revision"] = "v17.2"
        created.append(blink.name)
    return created, samples


def rename_v171_lips_to_v172(created_names):
    renamed = []
    for name in created_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        new_name = name.replace("V171", "V172")
        obj.name = new_name
        obj["portrait_revision"] = "v17.2"
        renamed.append(new_name)
    return renamed


def retarget_hair_and_brows(cfg):
    h = cfg["hair"]
    changed = []
    for obj in bpy.data.objects:
        if any(token in obj.name for token in h["tokens"]):
            obj.location.z -= h["fringe_drop"]
            obj.scale.x *= h["fringe_width_scale"]
            obj["portrait_retarget"] = "v17.2"
            changed.append(obj.name)
        elif "BrowV119" in obj.name:
            obj.location.z -= h["brow_drop"]
            obj["portrait_retarget"] = "v17.2"
            changed.append(obj.name)
    return changed


def add_beauty_mark(gen, helpers, head, cfg):
    b = cfg["beauty_mark"]
    z, count = helpers["sample_front_z"](head, b["x"], b["y"], 0.012, 0.012, 0.82)
    obj = gen["add_ellipse_surface"](
        gen["HEAD"], "BeautyMarkV172", b["x"], b["y"], z + b["front_offset"],
        b["radius"], b["radius"] * 0.94, gen["FACE_DARK"], 20
    )
    obj["portrait_revision"] = "v17.2"
    return obj.name, {"surface_z": round(z, 6), "samples": count}


def live_audit_v172(helpers, cfg):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = helpers["find_generated_head"]()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")
    new_eye = [o for o in bpy.data.objects if "V172" in o.name and any(t in o.name for t in ("Eye", "Sclera", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in ("V166", "V167", "DonorEyeScleraV171", "DonorIrisOuterV171", "DonorIrisInnerV171", "DonorPupilV171"))]
    new_lips = [o for o in bpy.data.objects if any(t in o.name for t in ("DonorUpperLipV172", "DonorLowerLipV172", "DonorMouthSeamV172"))]
    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"not enough v17.2 eye parts: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old eye parts remain: " + ", ".join(o.name for o in old_eye))
    if len(new_lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"not enough v17.2 lip parts: {len(new_lips)}")
    skin = bpy.data.materials.get("DavidOnizakiCleanSkinV172")
    if skin is None or skin.get("donor_albedo_used") is not False:
        raise RuntimeError("clean v17.2 skin material policy missing")
    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "new_lip_parts": len(new_lips),
        "beauty_mark": bpy.data.objects.get("BeautyMarkV172") is not None,
        "clean_skin": True,
        "mesh_objects": len([o for o in bpy.data.objects if o.type == "MESH"]),
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/parry-doll-fresh-donor-v172.blend")
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.2":
        raise RuntimeError("unexpected v17.2 config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR, HELPERS):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    helpers = runpy.run_path(HELPERS, run_name="__parry_doll_v171_helpers_for_v172__")
    gen = runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v172__")

    head = helpers["find_generated_head"]()
    generated_bbox = helpers["bbox_dict"](head)
    donor = helpers["import_donor_obj"](os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV172"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = helpers["bbox_dict"](donor)
    moved, max_delta = helpers["sculpt_donor"](donor, cfg)
    helpers["subdivide"](donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = helpers["bbox_dict"](donor)

    skin = make_clean_skin_material(a.donor_normal, cfg)
    fit = helpers["replace_fresh_head"](head, donor, cfg, skin)
    removed = helpers["cleanup_old_portrait"](cfg, head)
    eye_parts, eye_samples = build_donor_eyes_v172(gen, helpers, head, cfg)
    lip_names_v171, lip_sample = helpers["build_donor_lips"](gen, head, cfg)
    lip_parts = rename_v171_lips_to_v172(lip_names_v171)
    hair = retarget_hair_and_brows(cfg)
    neck = helpers["retarget_neck"](cfg)
    beauty_name, beauty_sample = add_beauty_mark(gen, helpers, head, cfg)
    helpers["tag_hierarchy"](cfg)
    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["build_pipeline"] = "fresh-empty-scene-david-onizaki-v172-clean-portrait"
        root["donor_albedo_used"] = False
    audit = live_audit_v172(helpers, cfg)

    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(os.path.abspath(a.output))

    print("FRESH_DONOR_V172_RESULT", json.dumps({
        "revision": cfg["revision"],
        "source_glb_imported": False,
        "donor_albedo_used": False,
        "donor_author": cfg["donor"]["author"],
        "generated_head_bbox_before_replace": generated_bbox,
        "donor_bbox_before": donor_before,
        "donor_bbox_after": donor_after,
        "donor_vertices_sculpted": moved,
        "donor_max_sculpt_delta": round(max_delta, 7),
        "fit": fit,
        "removed_old_portrait_parts": removed,
        "new_eye_parts": eye_parts,
        "eye_surface_samples": eye_samples,
        "new_lip_parts": lip_parts,
        "lip_surface_sample": lip_sample,
        "retargeted_hair_brows": hair,
        "retargeted_neck": neck,
        "beauty_mark": beauty_name,
        "beauty_mark_sample": beauty_sample,
        "audit": audit,
        "output": os.path.abspath(a.output),
        "output_bytes": os.path.getsize(a.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
