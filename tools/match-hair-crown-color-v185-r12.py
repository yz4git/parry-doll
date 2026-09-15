"""v18.5 r12: match ONLY the seven added r11 crown-lock materials to the accepted donor hair.

Geometry is immutable. Face, main hair, scalp gap filler, bangs, side hair and ponytail are untouched.
The donor hair texture is sampled robustly to derive its visible blue tone, and the crown locks get a
small packed texture built from that tone while copying the donor Principled roughness/specular.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import bpy

HEAD = "HeadShellV140"
HAIR = "HairPremiumV185_Adventurer"
CAP = "HairPremiumV185_ScalpCap"
LOCK_PREFIX = "HairPremiumV185_CrownLockR11_"
TARGET_MATERIAL = "HairPremiumV185CrownMatchR12"

HAIR_MARKERS = (
    "hairdonor", "hairpremium", "hairrear", "hairtop", "herohair", "heropony", "herocrown",
    "ponymass", "ponyfan", "ponyfoundation", "ponywing", "ponyroot", "ponytail", "hairtie",
    "fringe", "bang", "crown", "temporal", "temple", "nape", "wisp", "strand", "lock",
    "cascade", "profileeyeframe", "profilehairornament", "referencewisp", "eyerevealfringe",
    "earfrontwisp", "bl_pony_dynamic", "scalpcap",
)
FACE_MARKERS = (
    "headshell", "davidonizaki", "eyelid", "eyelight", "iris", "pupil", "sclera", "wetline",
    "lash", "canthus", "brow", "skinrim", "beautymark", "nose", "lip", "mouth",
    "earantihelix", "earconcha", "earhelix", "earlobefold", "eartragus", "earring",
)


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def under(obj, ancestor):
    cur = obj
    while cur:
        if cur.name == ancestor:
            return True
        cur = cur.parent
    return False


def hair_name(obj):
    return any(t in obj.name.lower() for t in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(t in n for t in HAIR_MARKERS):
        return False
    return any(t in n for t in FACE_MARKERS)


def protected_face(obj):
    return obj.type == "MESH" and (face_name(obj) or (under(obj, "BL_HEAD") and not hair_name(obj)))


def geom_signature(obj):
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    return (
        len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), verts, matrix,
        obj.parent.name if obj.parent else None,
    )


def material_signature(obj):
    return tuple(slot.material.name if slot.material else None for slot in obj.material_slots)


def donor_material_and_bsdf(hair):
    if not hair.data.materials or hair.data.materials[0] is None:
        raise RuntimeError("donor hair material missing")
    mat = hair.data.materials[0]
    if not mat.use_nodes or not mat.node_tree:
        raise RuntimeError("donor hair node material missing")
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        raise RuntimeError("donor hair Principled BSDF missing")
    image = next((n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
    if image is None:
        raise RuntimeError("donor hair texture image missing")
    return mat, bsdf, image


def robust_hair_tone(image):
    px = list(image.pixels)
    samples = []
    step = max(1, (image.size[0] * image.size[1]) // 120000)
    for i in range(0, len(px) // 4, step):
        r, g, b, a = (float(px[i * 4 + j]) for j in range(4))
        if a < 0.5:
            continue
        lum = (r + g + b) / 3.0
        # Keep chromatic blue/violet hair pixels, reject black atlas padding and near-white noise.
        if lum < 0.055 or lum > 0.82:
            continue
        if b < max(r, g) * 1.05:
            continue
        samples.append((r, g, b))
    if len(samples) < 200:
        raise RuntimeError(f"too few usable donor hair pixels: {len(samples)}")

    # Median is intentionally used instead of mean so isolated atlas highlights/shadows cannot skew it.
    med = tuple(statistics.median(s[c] for s in samples) for c in range(3))
    # Slight lift toward the donor render's midtone, but keep the same hue ratios.
    peak = max(med)
    scale = 0.54 / peak if peak > 1e-6 else 1.0
    scale = max(0.82, min(1.28, scale))
    tone = tuple(max(0.02, min(0.78, v * scale)) for v in med)
    return tone, len(samples), med


def make_texture(tone, size=256):
    img = bpy.data.images.new("HairCrownMatchR12Texture", width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    for y in range(size):
        ny = (y / (size - 1) - 0.5) * 2.0
        for x in range(size):
            nx = (x / (size - 1) - 0.5) * 2.0
            fine = 0.5 + 0.5 * math.sin((nx * 6.2 + ny * 1.35) * math.pi + 0.25)
            broad = 0.5 + 0.5 * math.sin((nx * 1.65 - ny * 0.55) * math.pi + 0.8)
            value = 0.88 + 0.075 * fine + 0.045 * broad
            r = max(0.015, min(0.92, tone[0] * value))
            g = max(0.020, min(0.92, tone[1] * value))
            b = max(0.040, min(0.96, tone[2] * value))
            k = (y * size + x) * 4
            pixels[k:k+4] = (r, g, b, 1.0)
    img.pixels = pixels
    img.pack()
    return img


def copy_scalar(bsdf, name, fallback):
    socket = bsdf.inputs.get(name)
    return float(socket.default_value) if socket is not None else fallback


def make_mat(image, donor_bsdf):
    mat = bpy.data.materials.new(TARGET_MATERIAL)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = copy_scalar(donor_bsdf, "Roughness", 0.55)
    bsdf.inputs["Metallic"].default_value = copy_scalar(donor_bsdf, "Metallic", 0.0)
    src_spec = donor_bsdf.inputs.get("Specular IOR Level") or donor_bsdf.inputs.get("Specular")
    dst_spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if src_spec is not None and dst_spec is not None:
        dst_spec.default_value = float(src_spec.default_value)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(HEAD)
    hair = bpy.data.objects.get(HAIR)
    cap = bpy.data.objects.get(CAP)
    locks = sorted(
        [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(LOCK_PREFIX)],
        key=lambda o: o.name,
    )
    if not head or not hair or not cap or len(locks) != 7:
        raise RuntimeError(f"accepted r11 objects missing: head={bool(head)} hair={bool(hair)} cap={bool(cap)} locks={len(locks)}")

    face_before = {o.name: geom_signature(o) for o in bpy.data.objects if protected_face(o)}
    all_geom_before = {o.name: geom_signature(o) for o in bpy.data.objects if o.type == "MESH"}
    hair_mat_before = material_signature(hair)
    cap_mat_before = material_signature(cap)
    lock_geom_before = {o.name: geom_signature(o) for o in locks}

    donor_mat, donor_bsdf, donor_img = donor_material_and_bsdf(hair)
    tone, sample_count, median = robust_hair_tone(donor_img)
    matched_mat = make_mat(make_texture(tone), donor_bsdf)

    prior_lock_materials = {}
    for obj in locks:
        prior_lock_materials[obj.name] = list(material_signature(obj))
        obj.data.materials.clear()
        obj.data.materials.append(matched_mat)
        for poly in obj.data.polygons:
            poly.material_index = 0

    # Hard geometry gate: this task is color-only.
    all_geom_after = {o.name: geom_signature(o) for o in bpy.data.objects if o.type == "MESH"}
    if set(all_geom_after) != set(all_geom_before):
        raise RuntimeError("GEOMETRY LOCK: mesh object set changed")
    changed_geom = [n for n in all_geom_before if all_geom_before[n] != all_geom_after[n]]
    if changed_geom:
        raise RuntimeError("GEOMETRY LOCK changed: " + ", ".join(changed_geom[:20]))
    if material_signature(hair) != hair_mat_before:
        raise RuntimeError("MAIN HAIR MATERIAL changed")
    if material_signature(cap) != cap_mat_before:
        raise RuntimeError("SCALP GAP MATERIAL changed")
    face_after = {o.name: geom_signature(o) for o in bpy.data.objects if protected_face(o)}
    if face_after != face_before:
        raise RuntimeError("FACE LOCK changed")
    if any(geom_signature(o) != lock_geom_before[o.name] for o in locks):
        raise RuntimeError("CROWN LOCK GEOMETRY changed")

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.5-r12"
        hero["hair_refinement"] = "crown-lock-color-match-only"
        hero["face_locked_for_hair_v185_r12"] = True
        hero["geometry_locked_for_hair_v185_r12"] = True

    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", export_apply=False,
        export_materials="EXPORT", export_image_format="AUTO",
    )

    report = {
        "revision": "v18.5-r12",
        "scope": "seven-crown-lock-materials-only",
        "geometry_unchanged": True,
        "face_unchanged": True,
        "main_hair_unchanged": True,
        "bangs_unchanged": True,
        "side_hair_unchanged": True,
        "ponytail_unchanged": True,
        "scalp_gap_material_unchanged": True,
        "crown_lock_count": len(locks),
        "crown_lock_names": [o.name for o in locks],
        "prior_lock_materials": prior_lock_materials,
        "matched_material": matched_mat.name,
        "donor_material": donor_mat.name,
        "donor_texture": donor_img.name,
        "donor_sample_count": sample_count,
        "donor_median_rgb": list(median),
        "matched_tone_rgb": list(tone),
        "matched_roughness": copy_scalar(donor_bsdf, "Roughness", 0.55),
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_CROWN_COLOR_V185_R12", json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
