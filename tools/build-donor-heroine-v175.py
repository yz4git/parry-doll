"""Fresh PARRY DOLL heroine v17.5.

This is still a true empty-scene Blender build.  It never imports the previous shipping GLB.
The repository generator rebuilds the body/outfit/hair/weapon/runtime hierarchy, the pinned
David Onizaki CC-BY anime head is imported as donor topology, sculpted and fitted as the actual
head shell, and the portrait is rebuilt on that surface.

v17.5 fixes the remaining v17.4 pale cheek circles using evidence from a connected-component
inspection of the generated GLB.  The donor head contained 39 disconnected components after
subdivision.  Exactly two symmetric 141-vertex / 252-polygon islands were centered at
x +/-0.053951, y -0.093175, z -0.026746 with ~0.062 x 0.026 x 0.053 m bounds, exactly matching
the rendered cheek circles.  Only those two diagnosed islands are deleted.  The main facial shell,
skull, donor ears and all other donor topology are kept.
"""
from __future__ import annotations

import argparse
import json
import os
import runpy
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATOR = os.path.join(ROOT, "tools", "make-blender-heroine.py")
V171 = os.path.join(ROOT, "tools", "build-donor-heroine-v171.py")
V173 = os.path.join(ROOT, "tools", "build-donor-heroine-v173.py")
V174 = os.path.join(ROOT, "tools", "build-donor-heroine-v174.py")
DEFAULT_OUTPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v175.json")


def tail():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-obj", required=True)
    p.add_argument("--donor-uv", required=True)      # license/source verification only; intentionally unused
    p.add_argument("--donor-normal", required=True)  # license/source verification only; intentionally unused
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(tail())


def connected_components(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen = set(range(len(mesh.vertices)))
    components = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        comp = {seed}
        while stack:
            cur = stack.pop()
            for nxt in adjacency[cur]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    comp.add(nxt)
                    stack.append(nxt)
        components.append(comp)
    components.sort(key=len, reverse=True)
    return components


def component_bounds(obj, comp):
    pts = [obj.matrix_world @ obj.data.vertices[i].co for i in comp]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) * 0.5
    size = hi - lo
    return center, size


def in_range(v, lo, hi):
    return lo <= v <= hi


def remove_diagnosed_cheek_islands(head, cfg):
    c = cfg["head_component_cleanup"]
    comps = connected_components(head.data)
    records = []
    victims = []
    for index, comp in enumerate(comps):
        center, size = component_bounds(head, comp)
        match = (
            in_range(len(comp), c["min_vertices"], c["max_vertices"])
            and in_range(abs(center.x), c["abs_center_x_min"], c["abs_center_x_max"])
            and in_range(center.y, c["center_y_min"], c["center_y_max"])
            and in_range(center.z, c["center_z_min"], c["center_z_max"])
            and in_range(size.x, c["size_x_min"], c["size_x_max"])
            and in_range(size.y, c["size_y_min"], c["size_y_max"])
            and in_range(size.z, c["size_z_min"], c["size_z_max"])
        )
        if match:
            victims.append(comp)
            records.append({
                "index": index,
                "vertices": len(comp),
                "center": [round(float(v), 6) for v in center],
                "size": [round(float(v), 6) for v in size],
            })

    expected_components = int(c["expected_removed_components"])
    expected_vertices = int(c["expected_removed_vertices"])
    removed_vertex_indices = sorted({i for comp in victims for i in comp})
    if len(victims) != expected_components:
        raise RuntimeError(
            f"cheek-island selector matched {len(victims)} components, expected {expected_components}: {records}"
        )
    if len(removed_vertex_indices) != expected_vertices:
        raise RuntimeError(
            f"cheek-island selector matched {len(removed_vertex_indices)} vertices, expected {expected_vertices}: {records}"
        )

    before_vertices = len(head.data.vertices)
    before_polygons = len(head.data.polygons)
    before_components = len(comps)

    bm = bmesh.new()
    bm.from_mesh(head.data)
    bm.verts.ensure_lookup_table()
    delete_verts = [bm.verts[i] for i in removed_vertex_indices]
    bmesh.ops.delete(bm, geom=delete_verts, context="VERTS")
    bm.normal_update()
    bm.to_mesh(head.data)
    bm.free()
    head.data.update()

    after_components = len(connected_components(head.data))
    result = {
        "matched": records,
        "removed_components": len(victims),
        "removed_vertices": len(removed_vertex_indices),
        "before_vertices": before_vertices,
        "after_vertices": len(head.data.vertices),
        "before_polygons": before_polygons,
        "after_polygons": len(head.data.polygons),
        "before_components": before_components,
        "after_components": after_components,
    }
    head["donor_cheek_islands_removed"] = len(victims)
    head["donor_cheek_vertices_removed"] = len(removed_vertex_indices)
    head["donor_components_after_cleanup"] = after_components
    print("V175_CHEEK_ISLAND_CLEANUP", json.dumps(result, sort_keys=True))
    return result


def rename_objects_to_v175(names):
    renamed = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        if "V174" in obj.name:
            obj.name = obj.name.replace("V174", "V175")
        if getattr(obj, "data", None) is not None and getattr(obj.data, "name", None) and "V174" in obj.data.name:
            obj.data.name = obj.data.name.replace("V174", "V175")
        obj["portrait_revision"] = "v17.5"
        renamed.append(obj.name)
    return renamed


def rename_lips_to_v175(v174_lip_names):
    renamed = []
    for name in v174_lip_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.name = obj.name.replace("V174", "V175").replace("V171", "V175")
        if getattr(obj, "data", None) is not None and getattr(obj.data, "name", None):
            obj.data.name = obj.data.name.replace("V174", "V175").replace("V171", "V175")
        obj["portrait_revision"] = "v17.5"
        renamed.append(obj.name)
    return renamed


def add_beauty_mark_v175(gen, v171, head, cfg):
    b = cfg["beauty_mark"]
    z, count = v171["sample_front_z"](head, b["x"], b["y"], 0.012, 0.012, 0.84)
    obj = gen["add_ellipse_surface"](
        gen["HEAD"], "BeautyMarkV175", b["x"], b["y"], z + b["front_offset"],
        b["radius"], b["radius"] * 0.94, gen["FACE_DARK"], 20
    )
    obj["portrait_revision"] = "v17.5"
    return obj.name, {"surface_z": round(z, 6), "samples": count}


def live_audit(v171, cfg, cleanup):
    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))
    head = v171["find_generated_head"]()
    components = connected_components(head.data)

    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    if len(head.data.polygons) < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygon count too small: {len(head.data.polygons)}")
    if cleanup["removed_components"] != cfg["audit"]["expected_removed_cheek_components"]:
        raise RuntimeError("unexpected cheek component removal count")
    if cleanup["removed_vertices"] != cfg["audit"]["expected_removed_cheek_vertices"]:
        raise RuntimeError("unexpected cheek vertex removal count")
    if len(components) > cfg["audit"]["max_head_components_after_cleanup"]:
        raise RuntimeError(f"too many donor head components remain: {len(components)}")

    # Re-run the exact geometric selector: zero diagnosed cheek islands are allowed after cleanup.
    c = cfg["head_component_cleanup"]
    remaining_matches = []
    for index, comp in enumerate(components):
        center, size = component_bounds(head, comp)
        if (
            in_range(len(comp), c["min_vertices"], c["max_vertices"])
            and in_range(abs(center.x), c["abs_center_x_min"], c["abs_center_x_max"])
            and in_range(center.y, c["center_y_min"], c["center_y_max"])
            and in_range(center.z, c["center_z_min"], c["center_z_max"])
            and in_range(size.x, c["size_x_min"], c["size_x_max"])
            and in_range(size.y, c["size_y_min"], c["size_y_max"])
            and in_range(size.z, c["size_z_min"], c["size_z_max"])
        ):
            remaining_matches.append(index)
    if remaining_matches:
        raise RuntimeError("diagnosed pale cheek islands still present: " + repr(remaining_matches))

    new_eye = [o for o in bpy.data.objects if "V175" in o.name and any(
        t in o.name for t in ("Eye", "Sclera", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in (
        "V166", "V167", "DonorScleraAlmondV173", "DonorScleraAlmondV174",
        "DonorIrisOuterV173", "DonorIrisOuterV174", "DonorPupilV173", "DonorPupilV174",
        "DonorEyeGlobeV172", "DonorScleraPatchV172"))]
    lips = [o for o in bpy.data.objects if any(t in o.name for t in (
        "DonorUpperLipV175", "DonorLowerLipV175", "DonorMouthSeamV175"))]
    generated_ears = [o for o in bpy.data.objects if o.name.startswith(tuple(cfg["remove_generated_ears"]))]
    blink_l = bpy.data.objects.get("BL_EYELID_L")
    blink_r = bpy.data.objects.get("BL_EYELID_R")

    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"not enough v17.5 eye parts: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old eye parts remain: " + ", ".join(o.name for o in old_eye))
    if len(lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"not enough v17.5 lip parts: {len(lips)}")
    if len(generated_ears) > cfg["audit"]["max_generated_ear_parts"]:
        raise RuntimeError("duplicate generated ears remain: " + ", ".join(o.name for o in generated_ears))
    if cfg["audit"]["blink_nodes_must_be_empty"]:
        if blink_l is None or blink_r is None or blink_l.type != "EMPTY" or blink_r.type != "EMPTY":
            raise RuntimeError("blink nodes must remain EMPTY")
    if bpy.data.objects.get("BeautyMarkV175") is None:
        raise RuntimeError("BeautyMarkV175 missing")
    if not any(m and m.name == "Skin" for m in head.data.materials):
        raise RuntimeError("donor head is not using generator Skin material")

    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "head_polygons": len(head.data.polygons),
        "head_components": len(components),
        "removed_cheek_components": cleanup["removed_components"],
        "removed_cheek_vertices": cleanup["removed_vertices"],
        "remaining_cheek_matches": 0,
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "new_lip_parts": len(lips),
        "generated_ear_parts": len(generated_ears),
        "blink_l_type": blink_l.type,
        "blink_r_type": blink_r.type,
        "uses_generator_skin": True,
        "beauty_mark": True,
    }


def final_export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/parry-doll-fresh-donor-v175.blend")
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v17.5":
        raise RuntimeError("unexpected v17.5 config")
    for required in (a.donor_obj, a.donor_uv, a.donor_normal, GENERATOR, V171, V173, V174):
        if not os.path.isfile(required):
            raise RuntimeError(f"required source missing: {required}")

    v171 = runpy.run_path(V171, run_name="__parry_doll_v171_helpers_for_v175__")
    v173 = runpy.run_path(V173, run_name="__parry_doll_v173_helpers_for_v175__")
    v174 = runpy.run_path(V174, run_name="__parry_doll_v174_helpers_for_v175__")
    gen = runpy.run_path(GENERATOR, run_name="__parry_doll_fresh_generator_v175__")

    head = v171["find_generated_head"]()
    generated_bbox = v171["bbox_dict"](head)
    donor = v171["import_donor_obj"](os.path.abspath(a.donor_obj))
    donor.name = "CCBY_DavidOnizaki_SourceHeadV175"
    donor["author"] = cfg["donor"]["author"]
    donor["license"] = cfg["donor"]["license"]
    donor["source"] = cfg["donor"]["source"]
    donor_before = v171["bbox_dict"](donor)
    moved, max_delta = v171["sculpt_donor"](donor, cfg)
    v171["subdivide"](donor, int(cfg["surface"]["subdivision_levels"]))
    donor_after = v171["bbox_dict"](donor)

    fit = v171["replace_fresh_head"](head, donor, cfg, gen["SKIN"])
    head.data.name = "DavidOnizakiFreshAnimeHeadV175Mesh"
    head["portrait_surface_policy"] = cfg["surface"]["policy"]
    head["donor_albedo_used"] = False
    head["donor_normal_used"] = False
    cleanup = remove_diagnosed_cheek_islands(head, cfg)

    removed_portrait = v171["cleanup_old_portrait"](cfg, head)
    removed_ears = v173["remove_generated_ear_anatomy"](cfg)
    eye_names_v174, eye_samples = v174["build_surface_eyes_v174"](gen, v171, v173, head, cfg)
    eye_parts = rename_objects_to_v175(eye_names_v174)
    lip_names_v171, lip_sample = v171["build_donor_lips"](gen, head, cfg)
    lip_names_v174 = v174["rename_lips_v174"](lip_names_v171)
    lip_parts = rename_lips_to_v175(lip_names_v174)
    hair = v173["retarget_hair_and_brows"](cfg)
    neck = v171["retarget_neck"](cfg)
    beauty_name, beauty_sample = add_beauty_mark_v175(gen, v171, head, cfg)
    v171["tag_hierarchy"](cfg)

    blink_l = bpy.data.objects.get("BL_EYELID_L")
    blink_r = bpy.data.objects.get("BL_EYELID_R")
    for blink in (blink_l, blink_r):
        if blink:
            blink["portrait_revision"] = "v17.5"

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["build_pipeline"] = "fresh-empty-scene-david-onizaki-v175-cheek-islands-removed"
        root["character_revision"] = "v17.5"
        root["source_glb_imported"] = False
        root["donor_albedo_used"] = False
        root["donor_normal_used"] = False
        root["donor_cheek_islands_removed"] = cleanup["removed_components"]
    audit = live_audit(v171, cfg, cleanup)

    intermediate_blend = os.path.splitext(DEFAULT_OUTPUT)[0] + ".blend"
    if os.path.exists(intermediate_blend):
        os.remove(intermediate_blend)
    final_export(os.path.abspath(a.output))

    print("FRESH_DONOR_V175_RESULT", json.dumps({
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
        "cheek_island_cleanup": cleanup,
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
