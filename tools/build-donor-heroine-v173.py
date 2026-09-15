"""Fresh PARRY DOLL heroine v17.3 visual-correction pass.

The previous shipping GLB is never imported.  The repository generator first creates the complete
character from an empty Blender scene.  Only the pinned David Onizaki CC-BY donor head OBJ is then
imported and fitted as the actual head shell.  v17.3 removes the full spherical eye globes that
caused the v17.2 cheek discs, uses the generator's own clean skin material (no donor albedo/normal),
creates pointed almond sclera surfaces directly on the fitted donor face, strengthens the profile,
shortens/widens the face, removes duplicate generated ear anatomy, lowers the fringe and widens the
neck before exporting the game GLB.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import runpy
import sys

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATOR = os.path.join(ROOT, "tools", "make-blender-heroine.py")
HELPERS = os.path.join(ROOT, "tools", "build-donor-heroine-v171.py")
DEFAULT_OUTPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v173.json")


def tail():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)      # source validation only; intentionally unused
    p.add_argument("--donor-normal", required=True)  # source validation only; intentionally unused
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(tail())


def add_almond_surface(gen, parent_obj, name, ex, cy, z, rx, ry, lower_ratio, tilt, mat, segments=18):
    """Create a pointed eye-white aperture instead of a round/spherical eye surface."""
    bpos = gen["bpos"]
    parent = gen["parent"]
    smooth = gen["smooth"]
    verts = []

    # Upper lid from inner to outer. sqrt gives pointed canthi; a slight asymmetric height reads
    # more like an adult Japanese-game eye than a circular doll eye.
    for i in range(segments + 1):
        u = -1.0 + 2.0 * i / segments
        bow = math.sqrt(max(0.0, 1.0 - u * u))
        x = ex + u * rx
        y = cy + ry * bow + tilt * u
        zz = z + 0.00045 * bow
        verts.append(bpos((x, y, zz)))
    for i in range(segments, -1, -1):
        u = -1.0 + 2.0 * i / segments
        bow = math.sqrt(max(0.0, 1.0 - u * u))
        x = ex + u * rx
        y = cy - ry * lower_ratio * bow + tilt * u
        zz = z + 0.00022 * bow
        verts.append(bpos((x, y, zz)))

    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    parent(obj, parent_obj)
    obj["portrait_revision"] = "v17.3"
    smooth(obj)
    return obj


def build_surface_eyes(gen, helpers, head, cfg):
    e = cfg["eyes"]
    HEAD = gen["HEAD"]
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
        sclera_z = surface_z + e["sclera_front"]
        iris_z = surface_z + e["iris_front"]
        lid_z = surface_z + e["lid_front_offset"]
        lash_z = surface_z + e["lash_front_offset"]
        ex_iris = ex + side * e["aperture_rx"] * 0.025

        created.append(add_almond_surface(
            gen, HEAD, f"DonorScleraAlmondV173_{side}", ex, e["center_y"], sclera_z,
            e["aperture_rx"], e["aperture_ry"], e["lower_lid_ratio"], e["tilt"], SCLERA
        ).name)
        created.append(add_ellipse(HEAD, f"DonorIrisOuterV173_{side}", ex_iris, e["center_y"], iris_z,
                                   e["iris_outer_rx"], e["iris_outer_ry"], IRIS, 68).name)
        created.append(add_ellipse(HEAD, f"DonorIrisInnerV173_{side}", ex_iris, e["center_y"] + 0.00015,
                                   iris_z + 0.00013, e["iris_inner_rx"], e["iris_inner_ry"], IRIS_INNER, 62).name)
        created.append(add_rays(HEAD, f"DonorIrisRaysV173_{side}", ex_iris, e["center_y"] + 0.00010,
                                iris_z + 0.00022, e["iris_inner_rx"] * 0.92,
                                e["iris_inner_ry"] * 0.90, 0.30,
                                (IRIS_RAY_WARM, IRIS_RAY_DARK), 32).name)
        created.append(add_ellipse(HEAD, f"DonorPupilV173_{side}", ex_iris, e["center_y"] - 0.00010,
                                   iris_z + 0.00034, e["pupil_rx"], e["pupil_ry"], PUPIL, 46).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV173A_{side}", ex_iris - side * 0.0035,
                                   e["center_y"] + 0.0034, iris_z + 0.00048,
                                   0.00135, 0.00100, SCLERA, 22).name)
        created.append(add_ellipse(HEAD, f"DonorEyeLightV173B_{side}", ex_iris + side * 0.0023,
                                   e["center_y"] + 0.0010, iris_z + 0.00045,
                                   0.00046, 0.00036, SCLERA, 18).name)

        inner = ex - side * e["aperture_rx"]
        outer = ex + side * e["aperture_rx"]
        created.append(add_strand(HEAD, f"DonorUpperLashV173_{side}", [
            (inner, e["center_y"] - e["tilt"], lash_z),
            (ex - side * 0.0020, e["center_y"] + e["aperture_ry"] * 1.02, lash_z + 0.00048),
            (outer + side * 0.0018, e["center_y"] + e["tilt"], lash_z + 0.00012)
        ], 0.00090, HAIR).name)
        created.append(add_strand(HEAD, f"DonorOuterLashV173_{side}", [
            (outer - side * 0.0025, e["center_y"] + e["tilt"] + 0.0013, lash_z),
            (outer + side * 0.0060, e["center_y"] + e["tilt"] + 0.0048, lash_z + 0.00025),
            (outer + side * 0.0110, e["center_y"] + e["tilt"] + 0.0034, lash_z)
        ], 0.00048, HAIR).name)
        created.append(add_strand(HEAD, f"DonorLowerLidV173_{side}", [
            (inner + side * 0.0035, e["center_y"] - e["tilt"] - 0.0002, lid_z),
            (ex, e["center_y"] - e["aperture_ry"] * e["lower_lid_ratio"], lid_z + 0.00012),
            (outer - side * 0.0025, e["center_y"] + e["tilt"] - 0.00015, lid_z)
        ], 0.00019, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorLidFoldV173_{side}", [
            (inner + side * 0.0050, e["center_y"] - e["tilt"] + 0.0040, lid_z - 0.00025),
            (ex, e["center_y"] + e["aperture_ry"] * 1.38, lid_z),
            (outer - side * 0.0055, e["center_y"] + e["tilt"] + 0.0038, lid_z - 0.00020)
        ], 0.00014, FACE_DARK).name)
        created.append(add_strand(HEAD, f"DonorWetlineV173_{side}", [
            (inner + side * 0.0045, e["center_y"] - e["tilt"], iris_z + 0.00060),
            (ex, e["center_y"] - e["aperture_ry"] * e["lower_lid_ratio"], iris_z + 0.00064),
            (outer - side * 0.0090, e["center_y"] + e["tilt"], iris_z + 0.00060)
        ], 0.00010, EYE_WET).name)
        created.append(add_ellipse(HEAD, f"DonorCanthusV173_{side}", inner + side * 0.0014,
                                   e["center_y"] - e["tilt"] + 0.0002, iris_z + 0.00064,
                                   0.00120, 0.00052, EYE_WET, 18).name)

        blink_name = "BL_EYELID_L" if side < 0 else "BL_EYELID_R"
        blink = add_blink(gen, HEAD, blink_name, ex, e["center_y"], e["aperture_rx"],
                          e["aperture_ry"], surface_z + e["blink_front_offset"], SKIN)
        blink["portrait_revision"] = "v17.3"
        created.append(blink.name)
    return created, samples


def rename_v171_lips(created_names):
    renamed = []
    for name in created_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        new_name = name.replace("V171", "V173")
        obj.name = new_name
        obj["portrait_revision"] = "v17.3"
        renamed.append(new_name)
    return renamed


def remove_generated_ear_anatomy(cfg):
    tokens = tuple(cfg["remove_generated_ears"])
    removed = []
    for obj in list(bpy.data.objects):
        if obj.name.startswith(tokens):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def retarget_hair_and_brows(cfg):
    h = cfg["hair"]
    changed = []
    for obj in bpy.data.objects:
        if any(token in obj.name for token in h["fringe_tokens"]):
            obj.location.z -= h["fringe_drop"]
            obj.scale.x *= h["fringe_width_scale"]
            obj["portrait_retarget"] = "v17.3"
            changed.append(obj.name)
        elif "BrowV119" in obj.name:
            obj.location.z -= h["brow_drop"]
            obj["portrait_retarget"] = "v17.3"
            changed.append(obj.name)
    return changed


def add_beauty_mark(gen, helpers, head, cfg):
    b = cfg["beauty_mark"]
    z, count = helpers["sample_front_z"](head, b["x"], b["y"], 0.012, 0.012, 0.84)
    obj = gen["add_ellipse_surface"](
        gen["HEAD"], "BeautyMarkV173", b["x"], b["y"], z + b["front_offset"],
        b["radius"], b["radius"] * 0.94, gen["FACE_DARK"], 20
    )
    obj["portrait_revision"] = "v17.3"
    return obj.name, {"surface_z": round(z, 6), "samples": count}


def live_audit(helpers, cfg):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = helpers["find_generated_head"]()
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")

    new_eye = [o for o in bpy.data.objects if "V173" in o.name and any(
        t in o.name for t in ("Eye", "Sclera", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in (
        "EyeScleraGlobeV166", "IrisOuterV167", "PupilV167", "DonorEyeGlobeV172",
        "DonorScleraPatchV172", "DonorIrisOuterV172", "DonorPupilV172"))]
    globes = [o for o in bpy.data.objects if "DonorEyeGlobe" in o.name]
    lips = [o for o in bpy.data.objects if any(t in o.name for t in (
        "DonorUpperLipV173", "DonorLowerLipV173", "DonorMouthSeamV173"))]
    generated_ears = [o for o in bpy.data.objects if o.name.startswith(tuple(cfg["remove_generated_ears"]))]

    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"not enough v17.3 eye parts: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old eye parts remain: " + ", ".join(o.name for o in old_eye))
    if globes:
        raise RuntimeError("full eye globes are forbidden in v17.3: " + ", ".join(o.name for o in globes))
    if len(lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"not enough v17.3 lip parts: {len(lips)}")
    if len(generated_ears) > cfg["audit"]["max_generated_ear_parts"]:
        raise RuntimeError("duplicate generated ears remain: " + ", ".join(o.name for o in generated_ears))
    if not any(m and m.name == "Skin" for m in head.data.materials):
        raise RuntimeError("donor head is not using the generator Skin material")

    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "eye_globes": len(globes),
        "new_lip_parts": len(lips),
        "generated_ear_parts": len(generated_ears),
        "uses_generator_skin": True,
        "beauty_mark": bpy.data.objects.get("BeautyMarkV173") is not None,
        "mesh_objects": len([o for o in bpy.data.objects if o.type == "MESH"]),
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/parry-doll-fresh-donor-v173.blend")
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.3":
        raise RuntimeError("unexpected v17.3 config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR, HELPERS):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    helpers = runpy.run_path(HELPERS, run_name="__parry_doll_v171_helpers_for_v173__")
    gen = runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v173__")

    head = helpers["find_generated_head"]()
    generated_bbox = helpers["bbox_dict"](head)
    donor = helpers["import_donor_obj"](os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV173"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = helpers["bbox_dict"](donor)
    moved, max_delta = helpers["sculpt_donor"](donor, cfg)
    helpers["subdivide"](donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = helpers["bbox_dict"](donor)

    # Use the exact same skin material as neck/body.  No donor painted albedo and no donor normal
    # map are attached to the face in this pass; geometry owns the profile and facial volume.
    fit = helpers["replace_fresh_head"](head, donor, cfg, gen["SKIN"])
    head.data.name = "DavidOnizakiFreshAnimeHeadV173Mesh"
    head["portrait_surface_policy"] = cfg["surface"]["policy"]
    head["donor_albedo_used"] = False
    head["donor_normal_used"] = False

    removed_portrait = helpers["cleanup_old_portrait"](cfg, head)
    removed_ears = remove_generated_ear_anatomy(cfg)
    eye_parts, eye_samples = build_surface_eyes(gen, helpers, head, cfg)
    lip_names_v171, lip_sample = helpers["build_donor_lips"](gen, head, cfg)
    lip_parts = rename_v171_lips(lip_names_v171)
    hair = retarget_hair_and_brows(cfg)
    neck = helpers["retarget_neck"](cfg)
    beauty_name, beauty_sample = add_beauty_mark(gen, helpers, head, cfg)
    helpers["tag_hierarchy"](cfg)

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["build_pipeline"] = "fresh-empty-scene-david-onizaki-v173-surface-eyes"
        root["source_glb_imported"] = False
        root["donor_albedo_used"] = False
        root["donor_normal_used"] = False
    audit = live_audit(helpers, cfg)

    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(os.path.abspath(a.output))

    print("FRESH_DONOR_V173_RESULT", json.dumps({
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
