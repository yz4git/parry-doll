"""v18.5 r11: replace the visible smooth crown cap with head-conforming layered locks.

The accepted face and Adventurer hair remain immutable. The existing scalp cap is retained only as
a recessed dark gap filler. Every visible crown polygon is copied into one of seven broad diagonal
hair-lock bands that conform to the cap surface, preventing the single kappa/helmet dome read.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

R9_PATH = Path(__file__).with_name("fix-hair-crown-v185-r9.py")
spec = importlib.util.spec_from_file_location("hair_crown_r9_core", R9_PATH)
r9 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(r9)

HEAD = "HeadShellV140"
HAIR = "HairPremiumV185_Adventurer"
CAP = "HairPremiumV185_ScalpCap"
PREFIX = "HairPremiumV185_CrownLockR11_"


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def make_texture(name, base, size=128):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    for py in range(size):
        v = py / (size - 1)
        ny = (v - 0.5) * 2.0
        for px in range(size):
            u = px / (size - 1)
            nx = (u - 0.5) * 2.0
            # Long diagonal painted streaks, not radial spokes.
            flow = 0.5 + 0.5 * math.sin((nx * 4.0 + ny * 1.45) * math.pi + 0.35)
            broad = 0.5 + 0.5 * math.sin((nx * 1.35 - ny * 0.72) * math.pi + 1.0)
            value = 0.84 + 0.11 * flow + 0.05 * broad
            r = max(0.035, min(0.32, base[0] * value))
            g = max(0.060, min(0.42, base[1] * value))
            b = max(0.20, min(0.88, base[2] * value))
            i = (py * size + px) * 4
            pixels[i:i+4] = (r, g, b, 1.0)
    img.pixels = pixels
    img.pack()
    return img


def make_material(name, image, rough=0.62, specular=0.12):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    sp = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if sp is not None:
        sp.default_value = specular
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def assign_uv(obj, hc, hs):
    uv = obj.data.uv_layers.get("CrownR11UV") or obj.data.uv_layers.new(name="CrownR11UV")
    mw = obj.matrix_world
    for poly in obj.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = obj.data.loops[loop_idx].vertex_index
            p = mw @ obj.data.vertices[vi].co
            u = 0.5 + (p.x - hc.x) / max(hs.x * 1.04, 1e-8)
            v = 0.5 + (p.y - hc.y) / max(hs.y * 1.04, 1e-8)
            uv.data[loop_idx].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))


def recess_gap_fill(cap, hc):
    inv = cap.matrix_world.inverted()
    max_disp = 0.0
    for v, p in zip(cap.data.vertices, r9.world_points(cap)):
        d = p - hc
        q = Vector((hc.x + d.x * 0.994, hc.y + d.y * 0.994, hc.z + d.z * 0.996))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
    cap.data.update()
    return max_disp


def band_for(center, hc, hs):
    xr = (center.x - hc.x) / max(hs.x, 1e-8)
    yr = (center.y - hc.y) / max(hs.y, 1e-8)
    # Slightly curved diagonal parting; asymmetric so it reads as styled hair, not a radial flower.
    s = xr + 0.19 * yr + 0.025 * math.sin(yr * math.pi * 3.0)
    edges = (-0.34, -0.225, -0.105, 0.025, 0.155, 0.285)
    for i, edge in enumerate(edges):
        if s < edge:
            return i
    return 6


def build_lock(source_cap, band, root, hc, hs, material):
    mw = source_cap.matrix_world
    vertex_map = {}
    verts = []
    faces = []
    source_faces = []
    for poly in source_cap.data.polygons:
        wps = [mw @ source_cap.data.vertices[i].co for i in poly.vertices]
        center = sum(wps, Vector()) / len(wps)
        if band_for(center, hc, hs) != band:
            continue
        source_faces.append(poly.index)
        face = []
        for old_idx, p in zip(poly.vertices, wps):
            key = int(old_idx)
            if key not in vertex_map:
                d = p - hc
                # All locks hug the cap. Small per-band lift makes layered plate edges visible without
                # floating above the skull. A longitudinal wave adds strand curvature.
                lift = 1.0065 + (band % 3) * 0.0013
                xr = d.x / max(hs.x, 1e-8)
                yr = d.y / max(hs.y, 1e-8)
                wave = hs.z * 0.0022 * math.sin((xr * 3.1 + yr * 1.25 + band * 0.31) * math.pi)
                q = Vector((hc.x + d.x * lift,
                            hc.y + d.y * lift,
                            hc.z + d.z * lift + wave))
                vertex_map[key] = len(verts)
                verts.append(tuple(q))
            face.append(vertex_map[key])
        faces.append(face)
    if not faces:
        raise RuntimeError(f"empty crown band {band}")
    mesh = bpy.data.meshes.new(f"{PREFIX}{band+1:02d}Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f"{PREFIX}{band+1:02d}", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = True
    assign_uv(obj, hc, hs)
    return obj, len(source_faces)


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(HEAD)
    hair = bpy.data.objects.get(HAIR)
    cap = bpy.data.objects.get(CAP)
    if not head or head.type != "MESH" or not hair or hair.type != "MESH" or not cap or cap.type != "MESH":
        raise RuntimeError("accepted v18.5 r2 objects missing")
    root = cap.parent
    if root is None:
        raise RuntimeError("scalp cap parent missing")

    locked_face = {o.name: r9.signature(o) for o in bpy.data.objects if r9.protected_face(o)}
    hair_sig = r9.signature(hair)
    cap_topology = (len(cap.data.vertices), len(cap.data.edges), len(cap.data.polygons))
    if len(locked_face) < 50 or HEAD not in locked_face:
        raise RuntimeError(f"face lock set suspicious: {len(locked_face)}")

    _, _, hc, hs = r9.bounds(r9.world_points(head))

    dark_img = make_texture("HairCrownR11GapTexture", (0.075, 0.135, 0.44))
    mid_img = make_texture("HairCrownR11MidTexture", (0.120, 0.215, 0.61))
    light_img = make_texture("HairCrownR11LightTexture", (0.155, 0.265, 0.69))
    dark_mat = make_material("HairPremiumV185CrownGapR11", dark_img, 0.72, 0.07)
    mats = [
        make_material("HairPremiumV185CrownLockR11A", mid_img, 0.64, 0.10),
        make_material("HairPremiumV185CrownLockR11B", light_img, 0.61, 0.11),
        make_material("HairPremiumV185CrownLockR11C", mid_img, 0.65, 0.09),
    ]

    # Keep the original cap only beneath the visible locks as a dark no-skin gap filler.
    gap_disp = recess_gap_fill(cap, hc)
    cap.data.materials.clear()
    cap.data.materials.append(dark_mat)
    assign_uv(cap, hc, hs)

    created = []
    face_counts = []
    for band in range(7):
        obj, count = build_lock(cap, band, root, hc, hs, mats[band % len(mats)])
        created.append(obj.name)
        face_counts.append(count)

    # All original cap faces must be represented exactly once across visible crown locks.
    if sum(face_counts) != cap_topology[2]:
        raise RuntimeError(f"crown lock face coverage mismatch {sum(face_counts)} != {cap_topology[2]}")

    now_face = {o.name: r9.signature(o) for o in bpy.data.objects if r9.protected_face(o)}
    if set(now_face) != set(locked_face) or any(now_face[n] != locked_face[n] for n in locked_face):
        raise RuntimeError("FACE LOCK changed")
    if r9.signature(hair) != hair_sig:
        raise RuntimeError("MAIN HAIR LOCK changed")
    if (len(cap.data.vertices), len(cap.data.edges), len(cap.data.polygons)) != cap_topology:
        raise RuntimeError("CAP TOPOLOGY changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r11"
        hero["hair_refinement"] = "layered-head-conforming-crown-locks"
        hero["face_locked_for_hair_v185_r11"] = True
        hero["main_hair_locked_for_hair_v185_r11"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=False,
                              export_materials="EXPORT", export_image_format="AUTO")

    report = {
        "revision": "v18.5-r11",
        "scope": "crown-cap-only-layered-locks",
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "side_hair_unchanged": True,
        "ponytail_unchanged": True,
        "cap_topology_unchanged": True,
        "visible_crown_lock_count": len(created),
        "visible_crown_locks": created,
        "crown_lock_face_counts": face_counts,
        "all_cap_faces_covered_once": True,
        "gap_fill_recess_max": gap_disp,
        "protected_face_meshes": len(locked_face),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_V185_R11", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
