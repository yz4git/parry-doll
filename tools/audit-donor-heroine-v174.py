"""Post-export structural audit for fresh David Onizaki heroine v17.4."""
from __future__ import annotations
import argparse, json, os, sys
import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INPUT = os.path.join(ROOT, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "heroine-donor-fresh-v174.json")


def tail():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    return p.parse_args(tail())


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def under(obj, ancestor):
    p = obj.parent
    while p:
        if p.name == ancestor:
            return True
        p = p.parent
    return False


def find_head():
    exact = bpy.data.objects.get("HeadShellV140")
    if exact and exact.type == "MESH":
        return exact
    candidates = [
        o for o in bpy.data.objects
        if o.type == "MESH" and under(o, "BL_HEAD_ASSET") and "Head" in o.name
    ]
    if not candidates:
        raise RuntimeError("v17.4 donor head not found after GLB re-import")
    return max(candidates, key=lambda o: len(o.data.vertices))


def false_or_missing(root, key):
    if key not in root:
        return True
    value = root.get(key)
    return value is False or value == 0 or (
        isinstance(value, str) and value.strip().lower() in ("false", "0", "no", "off")
    )


def main():
    a = parse_args()
    with open(a.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("revision") != "v17.4":
        raise RuntimeError("unexpected v17.4 audit config")
    if not os.path.isfile(a.input):
        raise RuntimeError("GLB missing: " + a.input)

    clear()
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.input))

    missing = [n for n in cfg["audit"]["required_runtime_nodes"] if bpy.data.objects.get(n) is None]
    if missing:
        raise RuntimeError("missing runtime nodes: " + ", ".join(missing))

    head = find_head()
    verts = len(head.data.vertices)
    polys = len(head.data.polygons)
    if verts < cfg["audit"]["min_head_vertices"] or polys < cfg["audit"]["min_head_polygons"]:
        raise RuntimeError(f"head density below target: {verts}/{polys}")

    new_eye = [o for o in bpy.data.objects if "V174" in o.name and any(
        t in o.name for t in ("Eye", "Sclera", "Iris", "Pupil", "Lash", "Lid", "Canthus", "Wetline"))]
    old_eye = [o for o in bpy.data.objects if any(t in o.name for t in (
        "EyeScleraGlobeV166", "IrisOuterV167", "PupilV167",
        "DonorEyeGlobeV172", "DonorScleraPatchV172", "DonorIrisOuterV172", "DonorPupilV172",
        "DonorScleraAlmondV173", "DonorIrisOuterV173", "DonorPupilV173"))]
    globes = [o for o in bpy.data.objects if "DonorEyeGlobe" in o.name]
    lips = [o for o in bpy.data.objects if any(t in o.name for t in (
        "DonorUpperLipV174", "DonorLowerLipV174", "DonorMouthSeamV174"))]
    generated_ears = [o for o in bpy.data.objects if o.name.startswith(tuple(cfg["remove_generated_ears"]))]

    if len(new_eye) < cfg["audit"]["min_new_eye_parts"]:
        raise RuntimeError(f"v17.4 eye count below target: {len(new_eye)}")
    if len(old_eye) > cfg["audit"]["max_old_eye_parts"]:
        raise RuntimeError("old eyes remain after export: " + ", ".join(o.name for o in old_eye))
    if globes:
        raise RuntimeError("forbidden full eye globes remain: " + ", ".join(o.name for o in globes))
    if len(lips) < cfg["audit"]["min_new_lip_parts"]:
        raise RuntimeError(f"v17.4 lip count below target: {len(lips)}")
    if len(generated_ears) > cfg["audit"]["max_generated_ear_parts"]:
        raise RuntimeError("duplicate generated ear anatomy remains: " + ", ".join(o.name for o in generated_ears))

    blink_l = bpy.data.objects.get("BL_EYELID_L")
    blink_r = bpy.data.objects.get("BL_EYELID_R")
    if blink_l is None or blink_r is None:
        raise RuntimeError("blink runtime nodes missing")
    if cfg["audit"].get("blink_nodes_must_be_empty", False):
        if blink_l.type != "EMPTY" or blink_r.type != "EMPTY":
            raise RuntimeError(f"blink nodes must be EMPTY: {blink_l.type}/{blink_r.type}")

    if bpy.data.objects.get("BeautyMarkV174") is None:
        raise RuntimeError("BeautyMarkV174 missing")

    head_material_names = [m.name for m in head.data.materials if m]
    if not any(name == "Skin" or name.startswith("Skin.") for name in head_material_names):
        raise RuntimeError("head does not use generator Skin material: " + repr(head_material_names))

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root is None:
        raise RuntimeError("BLENDER_HEROINE missing")
    for key in ("source_glb_imported", "donor_albedo_used", "donor_normal_used"):
        if not false_or_missing(root, key):
            raise RuntimeError(f"{key} unexpectedly true: {root.get(key)!r}")

    print("FRESH_DONOR_V174_AUDIT", json.dumps({
        "revision": "v17.4",
        "input_bytes": os.path.getsize(a.input),
        "head_vertices": verts,
        "head_polygons": polys,
        "head_materials": head_material_names,
        "new_eye_parts": len(new_eye),
        "old_eye_parts": len(old_eye),
        "eye_globes": len(globes),
        "new_lip_parts": len(lips),
        "generated_ear_parts": len(generated_ears),
        "blink_l_type": blink_l.type,
        "blink_r_type": blink_r.type,
        "beauty_mark": True,
        "source_glb_imported": False,
        "donor_albedo_used": False,
        "donor_normal_used": False,
        "build_pipeline": root.get("build_pipeline"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
