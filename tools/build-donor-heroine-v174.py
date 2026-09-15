"""Fresh PARRY DOLL heroine v17.4.

v17.4 is a fresh empty-scene Blender build. It never imports the previous shipping GLB. The
repository generator builds body/outfit/hair/weapon/runtime nodes, the pinned David Onizaki CC-BY
head is fitted as the actual head shell, and the visible portrait is built on that donor surface.

The key correction versus v17.3 is that BL_EYELID_L/R are now non-rendering EMPTY runtime
placeholders. The former skin-coloured blink meshes measured ~0.062 x 0.026 m and were the exact
size/location of the pale circular cheek/eye artifacts in the visual audit. Blink geometry is not
rendered in this pass; the node contract is retained while the eye aperture itself is represented
only by pointed almond sclera, iris, lashes, wetline and lid-line geometry.
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
V171 = os.path.join(ROOT, "tools", "build-donor-heroine-v171.py")
V173 = os.path.join(ROOT, "tools", "build-donor-heroine-v173.py")
DEFAULT_OUTPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v174.json")


def tail():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)      # verified legal source asset; intentionally unused
    p.add_argument("--donor-normal", required=True)  # verified legal source asset; intentionally unused
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(tail())


def create_blink_empty(parent_obj, name):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent_obj
    obj["expression"] = "blink"
    obj["blink_render_geometry"] = False
    obj["portrait_revision"] = "v17.4"
    return obj


def build_surface_eyes_v174(gen, v171, v173, head, cfg):
    e = cfg["eyes"]
    HEAD = gen["HEAD"]
    add_ellipse = gen["add_ellipse_surface"]
    add_rays = gen["add_iris_rays_v129"]
    add_strand = gen["add_strand"]
    sample_front_z = v171["sample_front_z"]

    SCLERA = gen["SCLERA"]
    IRIS = gen["IRIS"]
    IRIS_INNER = gen["IRIS_INNER"]
    IRIS_RAY_WARM = gen["IRIS_RAY_WARM"]
    IRIS_RAY_DARK = gen["IRIS_RAY_DARK"]
    PUPIL = gen["PUPIL"]
    HAIR = gen["HAIR"]
    FACE_DARK = gen["FACE_DARK"]
    EYE_WET = gen["EYE_WET"]

    created = []
    samples = {}
    for side in (-1, 1):
        ex = side * e["center_x"]
        surface_z, sample_count = sample_front_z(
            head, ex, e["center_y"], e["surface_sample_rx"], e["surface_sample_ry"], e["surface_percentile"]
        )
        samples[str(side)] = {"surface_z": round(surface_z, 6), "samples": sample_count}
        sclera_z = surface_z + e["sclera_front"]
        iris_z = surface_z + e["iris_front"]
        lid_z = surface_z + e["lid_front_offset"]
        lash_z = surface_z + e["lash_front_offset"]
        ex_iris = ex + side * e["aperture_rx"] * 0.025

        created.append(v173["add_almond_surface"](
            gen, HEAD, f"DonorScleraAlmondV174_{side}", ex, e["center_y"], sclera_z,
            e["aperture_rx"], e["aperture_ry"], e["lower_lid_ratio"], e["tilt"], SCLERA
        ).name)
        created.append(add_ellipse(HEAD, f"DonorIrisOuterV174_{side}", ex_iris, e["center_y"], iris_z,
                                   e["iris_outer_rx"], e["iris_outer_ry"], IRIS, 68).name)
        created.append(add_ellipse(HEAD, f"DonorIrisInnerV174_{side}", ex_iris, e["center_y"] + 0.00015,
                                   iris_z + 0.00013, e["iris_inner_rx"], e["iris_inner_ry"], IRIS_INNER, 62).name)
        created.append(add_rays(HEAD, f"DonorIrisRaysV174_{side}", ex_iris, e["center_y"] + 0.00010,
                                iris_z + 0.00022, e["iris_inner_rx"] * 0.92,
                                e["iris_inner_ry"] * 0.90, 0.30,
                                (IRIS_RAY_WARM, IRIS_RAY_DARK), 32).name)
        created.append(add_ellipse(HEAD, f"DonorPupilV174_{side}", ex_iris, e["center_y"] - 0.00010,
                                   iris_z + 0.00034, e["pupil_rx"], e["pupil_ry"], PUPIL, 46).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV174A_{side}", ex_iris - side * 0.0035,
                                   e["center_y"] + 0.0035, iris_z + 0.00048,
                                   0.00138, 0.00102, SCLERA, 22).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV174B_{side}", ex_iris + side * 0.0024,
                                   e["center_y"] + 0.0010, iris_z + 0.00045,
                                   0.00047, 0.00037, SCLERA, 18).name)

        inner = ex - side * e["aperture_rx"]
        outer = ex + side * e["aperture_rx"]
        created.append(add_strand(HEAD, f"DonorUpperLashV174_{side}", [
            (inner, e["center_y"] - e["tilt"], lash_z),
            (ex - side * 0.0020, e["center_y"] + e["aperture_ry"] * 1.02, lash_z + 0.00048),
            (outer + side * 0.0018, e["center_y"] + e["tilt"], lash_z + 0.00012)
        ], 0.00092, HAIR).name)
        created.append(add_strand(HEAD, f"DonorOuterLashV174_{side}", [
            (outer - side * 0.0025, e["center_y"] + e["tilt"] + 0.0013, lash_z),
            (outer + side * 0.0063, e["center_y"] + e["tilt"] + 0.0050, lash_z + 0.00025),
            (outer + side * 0.0115, e["center_y"] + e["tilt"] + 0.0035, lash_z)
        ], 0.00050, HAIR).name)
        created.append(add_strand(HEAD, f"DonorLowerLidV174_{side}", [
            (inner + side * 0.0035, e["center_y"] - e["tilt"] - 0.0002, lid_z),
            (ex, e["center_y"] - e["aperture_ry"] * e["lower_lid_ratio"], lid_z + 0.00012),
            (outer - side * 0.0025, e["center_y"] + e["tilt"] - 0.00015, lid_z)
        ], 0.00019, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorLidFoldV174_{side}", [
            (inner + side * 0.0050, e["center_y"] - e["tilt"] + 0.0040, lid_z - 0.00025),
            (ex, e["center_y"] + e["aperture_ry"] * 1.38, lid_z),
            (outer - side * 0.0055, e["center_y"] + e["tilt"] + 0.0038, lid_z - 0.00020)
        ], 0.00014, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorWetlineV174_{side}", [
            (inner + side * 0.0045, e["center_y"] - e["tilt"], iris_z + 0.00060),
            (ex, e["center_y"] - e["aperture_ry"] * e["lower_lid_ratio"], iris_z + 0.00064),
            (outer - side * 0.0090, e["center_y"] + e["tilt"], iris_z + 0.00060)
        ], 0.00010, EYE_WET).name)
        created.append(add_ellipse(HEAD, f"DonorCanthusV174_{side}", inner + side * 0.0014,
                                   e["center_y"] - e["tilt"] + 0.0002, iris_z + 0.00064,
                                   0.00120, 0.00052, EYE_WET, 18).name)

        blink_name = "BL_EYELID_L" if side < 0 else "BL_EYELID_R"
        created.append(create_blink_empty(HEAD, blink_name).name)
    return created, samples


def rename_lips_v174(created_names):
    renamed = []
    for name in created_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        old_obj_name = obj.name
        new_name = old_obj_name.replace("V171", "V174")
        obj.name = new_name
        if getattr(obj, "data", None) is not None and obj.data.name:
            obj.data.name = obj.data.name.replace("V171", "V174")
        obj["portrait_revision"] = "v17.4"
        renamed.append(new_name)
    return renamed


def add_beauty_mark_v174(gen, v171, head, cfg):
    b = cfg["beauty_mark"]
    z, count = v171["sample_front_z"](head, b["x"], b["y"], 0.012, 0.012, 0.84)
    obj = gen["add_ellipse_surface"](
        gen["HEAD"], "BeautyMarkV174", b["x"], b["y"], z + b["front_offset"],
        b["radius"], b["radius"] * 0.94, gen["FACE_DARK"], 20
    )
    obj["portrait_revision"] = "v17.4"
    return obj.name, {"surface_z": round(z, 6), "samples": count}


def live_audit(v171, cfg):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = v171["find_generated_head"]()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")

    new_eye = [o for o in bpy.data.objects if "V174" in o.name and any(
        t in o.name for t in ("Eye", "Sclera", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in (
        "V166", "V167", "DonorScleraAlmondV173", "DonorIrisOuterV173", "DonorPupilV173",
        "DonorEyeGlobeV172", "DonorScleraPatchV172"))]
    lips = [o for o in bpy.data.objects if any(t in o.name for t in (
        "DonorUpperLipV174", "DonorLowerLipV174", "DonorMouthSeamV174"))]
    generated_ears = [o for o in bpy.data.objects if o.name.startswith(tuple(cfg["remove_generated_ears"]))]
    blink_l = bpy.data.objects.get("BL_EYELID_L")
    blink_r = bpy.data.objects.get("BL_EYELID_R")

    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"not enough v17.4 eye parts: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old eye parts remain: " + ", ".join(o.name for o in old_eye))
    if len(lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"not enough v17.4 lip parts: {len(lips)}")
    if len(generated_ears) > cfg["audit"]["max_generated_ear_parts"]:
        raise RuntimeError("duplicate generated ears remain: " + ", ".join(o.name for o in generated_ears))
    if cfg["audit"]["blink_nodes_must_be_empty"]:
        if blink_l is None or blink_r is None or blink_l.type != "EMPTY" or blink_r.type != "EMPTY":
            raise RuntimeError(f"blink nodes must be EMPTY, got {getattr(blink_l,'type',None)}/{getattr(blink_r,'type',None)}")
    if not any(m and m.name == "Skin" for m in head.data.materials):
        raise RuntimeError("donor head is not using generator Skin material")

    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "new_lip_parts": len(lips),
        "generated_ear_parts": len(generated_ears),
        "blink_l_type": blink_l.type,
        "blink_r_type": blink_r.type,
        "uses_generator_skin": True,
        "beauty_mark": bpy.data.objects.get("BeautyMarkV174") is not None,
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/parry-doll-fresh-donor-v174.blend")
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.4":
        raise RuntimeError("unexpected v17.4 config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR, V171, V173):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    v171 = runpy.run_path(V171, run_name="__parry_doll_v171_helpers_for_v174__")
    v173 = runpy.run_path(V173, run_name="__parry_doll_v173_helpers_for_v174__")
    gen = runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v174__")

    head = v171["find_generated_head"]()
    generated_bbox = v171["bbox_dict"](head)
    donor = v171["import_donor_obj"](os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV174"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = v171["bbox_dict"](donor)
    moved, max_delta = v171["sculpt_donor"](donor, cfg)
    v171["subdivide"](donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = v171["bbox_dict"](donor)

    fit = v171["replace_fresh_head"](head, donor, cfg, gen["SKIN"])
    head.data.name = "DavidOnizakiFreshAnimeHeadV174Mesh"
    head["portrait_surface_policy"] = cfg["surface"]["policy"]
    head["donor_albedo_used"] = False
    head["donor_normal_used"] = False

    removed_portrait = v171["cleanup_old_portrait"](cfg, head)
    removed_ears = v173["remove_generated_ear_anatomy"](cfg)
    eye_parts, eye_samples = build_surface_eyes_v174(gen, v171, v173, head, cfg)
    lip_names_v171, lip_sample = v171["build_donor_lips"](gen, head, cfg)
    lip_parts = rename_lips_v174(lip_names_v171)
    hair = v173["retarget_hair_and_brows"](cfg)
    neck = v171["retarget_neck"](cfg)
    beauty_name, beauty_sample = add_beauty_mark_v174(gen, v171, head, cfg)
    v171["tag_hierarchy"](cfg)

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["build_pipeline"] = "fresh-empty-scene-david-onizaki-v174-no-visible-blink-mesh"
        root["source_glb_imported"] = False
        root["donor_albedo_used"] = False
        root["donor_normal_used"] = False
    audit = live_audit(v171, cfg)

    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(os.path.abspath(a.output))

    print("FRESH_DONOR_V174_RESULT", json.dumps({
        "revision": cfg["revision"],
        "source_glb_imported": False,
        "donor_albedo_used": False,
        "donor_normal_used": False,
        "donor_author": cfg["donor"]["author"],
        "generated_head_bbox_before_replace": generated_bbox,
        "donor_bbox_before": donor_before,
        "donor_bbox_after": donor_after,
        "donor_vertices_sculpted": moved,
        "donor_max_sculpt_delta": round(max_delta, 7),
        "fit": fit,
        "removed_old_portrait_parts": removed_portrait,
        "removed_generated_ears": removed_ears,
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
