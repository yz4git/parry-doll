"""Post-export audit for fresh David Onizaki heroine v17.1."""
from __future__ import annotations

import argparse
import json
import os
import sys

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v171.json")


def argv_after_double_dash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(argv_after_double_dash())


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def under(obj, ancestor_name):
    q = obj.parent
    while q is not None:
        if q.name == ancestor_name:
            return True
        q = q.parent
    return False


def find_head():
    exact = bpy.data.objects.get("HeadShellV140")
    if exact is not None and exact.type == "MESH":
        return exact
    candidates = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not under(obj, "BL_HEAD_ASSET"):
            continue
        mats = {m.name for m in getattr(obj.data, "materials", []) if m}
        if "DavidOnizakiAnimeSkinV171" in mats or "Head" in obj.name:
            candidates.append(obj)
    if not candidates:
        raise RuntimeError("could not resolve v17.1 donor head after GLB re-import")
    return max(candidates, key=lambda o: len(o.data.vertices))


def main():
    a = parse_args()
    with open(a.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("revision") != "v17.1":
        raise RuntimeError("unexpected v17.1 audit config")
    if not os.path.isfile(a.input):
        raise RuntimeError(f"GLB missing: {a.input}")

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.input))

    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("post-export GLB missing runtime nodes: " + ", ".join(missing))

    head = find_head()
    verts = len(head.data.vertices)
    polys = len(head.data.polygons)
    if verts < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertices below target after export: {verts}")
    if polys < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head polygons below target after export: {polys}")

    new_eye = [o for o in bpy.data.objects if "V171" in o.name and any(t in o.name for t in ("Eye", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in ("IrisOuterV167", "IrisInnerV167", "PupilV167", "EyeScleraGlobeV166", "EyeLightV167"))]
    new_lips = [o for o in bpy.data.objects if any(t in o.name for t in ("DonorUpperLipV171", "DonorLowerLipV171", "DonorMouthSeamV171"))]
    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"post-export v17.1 eye count below target: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("post-export old eye parts remain: " + ", ".join(o.name for o in old_eye))
    if len(new_lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"post-export v17.1 lip count below target: {len(new_lips)}")

    if bpy.data.objects.get("BL_EYELID_L") is None or bpy.data.objects.get("BL_EYELID_R") is None:
        raise RuntimeError("blink eyelid nodes missing after export")

    root = bpy.data.objects.get("BLENDER_HEROINE")
    result = {
        "revision": cfg["revision"],
        "input_bytes": os.path.getsize(a.input),
        "head": head.name,
        "head_vertices": verts,
        "head_polygons": polys,
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "new_lip_parts": len(new_lips),
        "mesh_objects": sum(1 for o in bpy.data.objects if o.type == "MESH"),
        "required_runtime_nodes": len(cfg["audit"]["required_runtime_nodes"]),
        "source_glb_imported_property": root.get("source_glb_imported") if root else None,
        "build_pipeline": root.get("build_pipeline") if root else None,
        "donor_author": root.get("donor_author") if root else None,
    }
    print("FRESH_DONOR_V171_AUDIT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
