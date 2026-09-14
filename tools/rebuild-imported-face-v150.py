"""Rebuild the current game face by importing the shipped GLB into Blender and sculpting it in place.

This deliberately preserves the existing runtime hierarchy / animation-facing node names.
It does not vendor or copy geometry from a commercial game model.  The repo's pinned
CC0 hm08 topology analysis remains the topology reference while the supplied key art
defines proportions and silhouette.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import shutil
import sys
import tempfile

import bpy

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MODEL = os.path.join(ROOT_DIR, "dist", "assets", "models", "heroine-blender.glb")
DEFAULT_CONFIG = os.path.join(ROOT_DIR, "tools", "heroine-face-import-v150.json")
CC0_STATS = os.path.join(ROOT_DIR, "tools", "cc0-face-topology-stats.json")


def args_after_double_dash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=DEFAULT_MODEL)
    p.add_argument("--output", default=DEFAULT_MODEL)
    p.add_argument("--config", default=DEFAULT_CONFIG)
    p.add_argument("--audit-only", action="store_true")
    return p.parse_args(args_after_double_dash())


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def smoothstep(edge0, edge1, x):
    if edge0 == edge1:
        return 0.0
    t = clamp((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def gaussian(v, center, radius):
    if radius <= 0:
        return 0.0
    d = (v - center) / radius
    return math.exp(-(d * d))


# Generator authoring -> Blender is bpos((x,y,z)) == (x,-z,y).
def to_logical(co):
    return [float(co.x), float(co.z), float(-co.y)]


def from_logical(co, xyz):
    co.x, co.y, co.z = xyz[0], -xyz[2], xyz[1]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_glb(path):
    if not os.path.isfile(path):
        raise RuntimeError(f"input GLB missing: {path}")
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=path)


def mesh_objects():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def find_named(*names):
    for name in names:
        o = bpy.data.objects.get(name)
        if o is not None:
            return o
    return None


def find_head():
    exact = find_named("HeadShellV140")
    if exact and exact.type == "MESH":
        return exact
    candidates = [
        o for o in mesh_objects()
        if o.name.startswith("HeadShellV140") or o.get("face_rebuild") or "HeadShell" in o.name
    ]
    if not candidates:
        raise RuntimeError("could not find imported HeadShellV140")
    return max(candidates, key=lambda o: len(o.data.vertices))


def deform_head(head, cfg):
    s = cfg["shape"]
    changed = 0
    max_delta = 0.0
    for v in head.data.vertices:
        old = to_logical(v.co)
        x, y, z = old

        # Front-of-face weight. Lower-jaw width is intentionally allowed to affect
        # more of the section so the 3/4 and exact-profile silhouettes agree.
        front = smoothstep(s["front_weight_start_z"], s["front_weight_full_z"], z)

        # Signed logical Y: jaw_start_y is negative and jaw_end_y is more negative.
        if y < s["jaw_start_y"]:
            lower = smoothstep(-s["jaw_start_y"], -s["jaw_end_y"], -y)
            x *= 1.0 - s["jaw_narrow"] * lower
        chin_t = smoothstep(-s["chin_start_y"], -s["chin_end_y"], -y) if y < s["chin_start_y"] else 0.0
        if chin_t > 0.0:
            x *= 1.0 - s["chin_narrow"] * chin_t

        # Delicate lower-midface from the front reference.
        cheek_w = gaussian(y, s["cheek_center_y"], s["cheek_radius_y"]) * front
        x *= 1.0 - s["cheek_narrow"] * cheek_w

        # Small, smooth game/anime nose from the profile reference. Reduce only
        # protrusion above the facial plane, retaining bridge continuity.
        nose_w = (
            gaussian(x, 0.0, s["nose_radius_x"])
            * gaussian(y, s["nose_center_y"], s["nose_radius_y"])
            * front
        )
        if z > s["nose_plane_z"]:
            z -= (z - s["nose_plane_z"]) * s["nose_projection_reduce"] * nose_w

        # Slightly cleaner nasion transition.
        nasion_w = (
            gaussian(x, 0.0, s["nasion_radius_x"])
            * gaussian(y, s["nasion_center_y"], s["nasion_radius_y"])
            * front
        )
        if z > s["nasion_plane_z"]:
            z -= (z - s["nasion_plane_z"]) * s["nasion_projection_reduce"] * nasion_w

        # A small forward chin pad keeps the exact side profile from becoming weak
        # after the lower-face taper.
        chin_w = (
            gaussian(x, 0.0, s["chin_radius_x"])
            * gaussian(y, s["chin_center_y"], s["chin_radius_y"])
            * front
        )
        z += s["chin_forward"] * chin_w

        new = [x, y, z]
        delta = math.sqrt(sum((new[i] - old[i]) ** 2 for i in range(3)))
        if delta > 1e-7:
            changed += 1
            max_delta = max(max_delta, delta)
            from_logical(v.co, new)

    head.data.update()
    head["face_rebuild"] = cfg["revision"]
    head["face_style"] = cfg["style"]
    head["source_pipeline"] = "import-existing-glb-and-sculpt"
    return changed, max_delta


def eye_side_for_object(obj):
    xs = []
    for v in obj.data.vertices:
        xs.append(to_logical(v.co)[0])
    if not xs:
        return 0
    mean_x = sum(xs) / len(xs)
    if abs(mean_x) < 0.008:
        return 0
    return -1 if mean_x < 0 else 1


def reshape_eye_assets(cfg):
    e = cfg["eyes"]
    tokens = tuple(e["mesh_name_tokens"])
    touched = []
    for obj in mesh_objects():
        if not any(t in obj.name for t in tokens):
            continue
        side = eye_side_for_object(obj)
        if side == 0:
            continue
        cx = side * e["center_x"]
        cy = e["center_y"]
        count = 0
        for v in obj.data.vertices:
            x, y, z = to_logical(v.co)
            # Avoid catching distant meshes that only happen to share a token.
            if abs(x - cx) > e["max_radius_x"] or abs(y - cy) > e["max_radius_y"]:
                continue
            x = cx + (x - cx) * e["width_scale"]
            y = cy + (y - cy) * e["height_scale"]
            from_logical(v.co, (x, y, z))
            count += 1
        if count:
            obj.data.update()
            obj["anime_eye_fit"] = cfg["revision"]
            touched.append((obj.name, count))
    return touched


def retarget_nostril_details(cfg):
    n = cfg["nostrils"]
    touched = []
    for obj in mesh_objects():
        if "Nostril" not in obj.name:
            continue
        for v in obj.data.vertices:
            x, y, z = to_logical(v.co)
            z -= n["inset"]
            x *= n["width_scale"]
            from_logical(v.co, (x, y, z))
        obj.data.update()
        touched.append(obj.name)
    return touched


def tag_assets(cfg):
    root = find_named("BLENDER_HEROINE")
    head_asset = find_named("BL_HEAD_ASSET")
    face_asset = find_named("BL_FACE_ASSET")
    if root:
        root["character_revision"] = cfg["revision"]
        root["face_pipeline"] = "imported-blender-sculpt"
    if head_asset:
        head_asset["face_rebuild_revision"] = cfg["revision"]
        head_asset["profile_target"] = "supplied-front-and-right-profile-key-art"
        head_asset["topology_reference"] = cfg["topology_reference"]
    if face_asset:
        face_asset["anime_game_face_revision"] = cfg["revision"]
        face_asset["preserve_runtime_hierarchy"] = True


def audit_scene(cfg):
    head = find_head()
    required = ["BLENDER_HEROINE", "BL_HEAD", "BL_HEAD_ASSET", "BL_FACE_ASSET"]
    missing = [name for name in required if bpy.data.objects.get(name) is None]
    if missing:
        raise RuntimeError("missing required runtime nodes: " + ", ".join(missing))
    if len(head.data.vertices) < cfg["audit"]["min_head_vertices"]:
        raise RuntimeError(f"head vertex count too small: {len(head.data.vertices)}")
    eye_objs = [
        o for o in mesh_objects()
        if any(t in o.name for t in ("EyeSclera", "IrisOuter", "Pupil", "UpperLash"))
    ]
    if len(eye_objs) < cfg["audit"]["min_eye_meshes"]:
        raise RuntimeError(f"eye mesh count too small: {len(eye_objs)}")
    return {
        "head": head.name,
        "head_vertices": len(head.data.vertices),
        "mesh_objects": len(mesh_objects()),
        "eye_meshes": len(eye_objs),
        "revision": head.get("face_rebuild", "imported-unmodified"),
    }


def export_glb(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(path)[0] + "-face-v150.blend")
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
    if cfg.get("version") != 1 or cfg.get("revision") != "v15.0":
        raise RuntimeError("unexpected face-import config")
    if not os.path.isfile(CC0_STATS):
        raise RuntimeError("pinned CC0 topology stats are missing")

    source = os.path.abspath(a.input)
    output = os.path.abspath(a.output)
    tmp_source = None
    if source == output and not a.audit_only:
        fd, tmp_source = tempfile.mkstemp(prefix="heroine-face-v150-", suffix=".glb")
        os.close(fd)
        shutil.copy2(source, tmp_source)
        source = tmp_source

    try:
        import_glb(source)
        before = audit_scene(cfg)
        if a.audit_only:
            print("FACE_V150_AUDIT", json.dumps(before, sort_keys=True))
            return

        head = find_head()
        changed, max_delta = deform_head(head, cfg)
        eyes = reshape_eye_assets(cfg)
        nostrils = retarget_nostril_details(cfg)
        tag_assets(cfg)
        after = audit_scene(cfg)

        if changed < cfg["audit"]["min_changed_head_vertices"]:
            raise RuntimeError(f"too few head vertices changed: {changed}")
        if len(eyes) < cfg["audit"]["min_retargeted_eye_meshes"]:
            raise RuntimeError(f"too few eye assets retargeted: {len(eyes)}")

        export_glb(output)
        print("FACE_V150_RESULT", json.dumps({
            "before": before,
            "after": after,
            "changed_head_vertices": changed,
            "max_head_delta": round(max_delta, 7),
            "retargeted_eye_meshes": len(eyes),
            "retargeted_nostril_meshes": len(nostrils),
            "output_bytes": os.path.getsize(output),
        }, sort_keys=True))
    finally:
        if tmp_source and os.path.exists(tmp_source):
            os.remove(tmp_source)


if __name__ == "__main__":
    main()
