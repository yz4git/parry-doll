"""Replace only the shipping heroine hairstyle with the CC0 OverScore Proxy High Ponytail.

The current face/head/eyes remain imported from the shipping GLB and are never edited.  Hair is
appended from the donor .blend, oriented, fitted to HeadShellV140 and parented under BL_HAIR_ASSET.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "dist/assets/models/heroine-blender.glb"
DEFAULT_OUTPUT = DEFAULT_INPUT
DEFAULT_REPORT = ROOT / "dist/hair-donor-v180-build.json"

FACE_LOCK_TOKENS = (
    "headshell", "eye", "iris", "pupil", "sclera", "lid", "lash", "brow", "canthus",
    "wetline", "lip", "mouth", "beautymark", "ear", "nose", "facequad", "facedetail",
)
STYLE_NAME_TOKENS = (
    "hair", "fringe", "bang", "crown", "temporal", "temple", "ponytail", "pony",
    "wisp", "nape", "lock", "strand", "flow", "scalp", "cap", "rear", "cascade",
)


def argv_tail():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(DEFAULT_INPUT))
    p.add_argument("--output", default=str(DEFAULT_OUTPUT))
    p.add_argument("--donor", required=True)
    p.add_argument("--report", default=str(DEFAULT_REPORT))
    return p.parse_args(argv_tail())


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def mesh_world_points(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def combined_points(objects):
    pts = []
    for obj in objects:
        if obj.type == "MESH":
            pts.extend(mesh_world_points(obj))
    if not pts:
        raise RuntimeError("no mesh points")
    return pts


def bounds(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def object_signature(obj):
    # The signature is captured before any hair edit and rechecked before export.  It deliberately
    # includes local mesh coordinates and transform/parent identity, so accidental face edits fail.
    verts = tuple(round(float(c), 8) for v in obj.data.vertices for c in v.co)
    matrix = tuple(round(float(c), 8) for row in obj.matrix_world for c in row)
    return (
        len(obj.data.vertices),
        len(obj.data.edges),
        len(obj.data.polygons),
        verts,
        matrix,
        obj.parent.name if obj.parent else None,
    )


def is_face_locked(obj):
    if obj.type != "MESH":
        return False
    n = obj.name.lower()
    return any(t in n for t in FACE_LOCK_TOKENS)


def is_old_style_hair(obj):
    if obj.type != "MESH" or is_face_locked(obj):
        return False
    n = obj.name.lower()
    if any(t in n for t in STYLE_NAME_TOKENS):
        return True
    mats = [m.name.lower() for m in obj.data.materials if m]
    return bool(mats) and all("hair" in m for m in mats)


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as exc:
            print("HAIR_V180 modifier skipped", obj.name, mod.name, repr(exc))
    obj.select_set(False)


def donor_candidates_from_collection(donor_path):
    loaded = []
    with bpy.data.libraries.load(str(donor_path), link=False) as (src, dst):
        exact = [n for n in src.collections if "high" in n.lower() and "ponytail" in n.lower()]
        if not exact:
            exact = [n for n in src.collections if "ponytail" in n.lower()]
        dst.collections = exact[:1]
        chosen_names = list(exact[:1])
    for coll in [c for c in dst.collections if c]:
        if coll.name not in bpy.context.scene.collection.children:
            try:
                bpy.context.scene.collection.children.link(coll)
            except RuntimeError:
                pass
        loaded.extend([o for o in coll.all_objects if o.type == "MESH"])
    print("HAIR_V180 donor collection candidates", chosen_names)
    return list(dict.fromkeys(loaded))


def donor_candidates_from_objects(donor_path):
    with bpy.data.libraries.load(str(donor_path), link=False) as (src, dst):
        names = [n for n in src.objects if "high" in n.lower() and "ponytail" in n.lower()]
        if not names:
            names = [n for n in src.objects if "ponytail" in n.lower()]
        if not names:
            names = [n for n in src.objects if "hair" in n.lower()]
        dst.objects = names
        chosen_names = list(names)
    loaded = []
    for obj in [o for o in dst.objects if o and o.type == "MESH"]:
        if not obj.users_collection:
            bpy.context.scene.collection.objects.link(obj)
        elif not any(c in bpy.context.scene.collection.children for c in obj.users_collection):
            try:
                bpy.context.scene.collection.objects.link(obj)
            except RuntimeError:
                pass
        loaded.append(obj)
    print("HAIR_V180 donor object candidates", chosen_names)
    return loaded


def append_high_ponytail(donor_path):
    before = set(bpy.data.objects)
    donor = donor_candidates_from_collection(donor_path)
    if not donor:
        donor = donor_candidates_from_objects(donor_path)
    donor = [o for o in donor if o not in before and o.type == "MESH"]
    if not donor:
        # Some appended collection objects can already be in bpy.data before the collection is linked.
        donor = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not donor:
        raise RuntimeError("High Ponytail mesh not found in donor blend")

    # If the collection includes helpers/reference head geometry, keep only explicitly hair-like meshes
    # when such names are available.
    explicit = [o for o in donor if any(k in o.name.lower() for k in ("hair", "ponytail", "pony"))]
    if explicit:
        for obj in list(donor):
            if obj not in explicit:
                bpy.data.objects.remove(obj, do_unlink=True)
        donor = explicit

    for obj in donor:
        apply_modifiers(obj)
    return donor


def rotate_tail_to_back(donor):
    pts = combined_points(donor)
    zs = sorted(p.z for p in pts)
    if len(zs) < 8:
        return False
    q35 = zs[int((len(zs) - 1) * 0.35)]
    q72 = zs[int((len(zs) - 1) * 0.72)]
    low = [p for p in pts if p.z <= q35]
    high = [p for p in pts if p.z >= q72]
    if not low or not high:
        return False
    tail_y = sum(p.y for p in low) / len(low)
    crown_y = sum(p.y for p in high) / len(high)
    print("HAIR_V180 donor tail direction", {"tail_y": tail_y, "crown_y": crown_y})
    # Parry Doll's face is -Y and the rear/ponytail direction is +Y.
    if tail_y >= crown_y:
        return False
    _, _, center, _ = bounds(pts)
    rot = Matrix.Translation(center) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-center)
    for obj in donor:
        obj.matrix_world = rot @ obj.matrix_world
    bpy.context.view_layer.update()
    return True


def fit_to_shipping_head(donor, head):
    head_lo, head_hi, head_center, head_size = bounds(mesh_world_points(head))
    donor_pts = combined_points(donor)
    donor_lo, donor_hi, _, donor_size = bounds(donor_pts)

    # Use the crown width rather than the whole tail span to set scale.
    crown_cut = donor_hi.z - donor_size.z * 0.44
    crown_pts = [p for p in donor_pts if p.z >= crown_cut]
    crown_width = (max(p.x for p in crown_pts) - min(p.x for p in crown_pts)) if crown_pts else donor_size.x
    if crown_width <= 1e-6:
        raise RuntimeError("invalid donor crown width")
    uniform_scale = (head_size.x * 1.105) / crown_width
    scale_m = Matrix.Scale(uniform_scale, 4)
    for obj in donor:
        obj.matrix_world = scale_m @ obj.matrix_world
    bpy.context.view_layer.update()

    donor_lo, donor_hi, donor_center, donor_size = bounds(combined_points(donor))
    target_top = head_hi.z + head_size.z * 0.045
    target_front = head_lo.y - head_size.y * 0.020
    dx = head_center.x - donor_center.x
    dy = target_front - donor_lo.y
    dz = target_top - donor_hi.z
    trans = Matrix.Translation(Vector((dx, dy, dz)))
    for obj in donor:
        obj.matrix_world = trans @ obj.matrix_world
    bpy.context.view_layer.update()

    final_lo, final_hi, final_center, final_size = bounds(combined_points(donor))
    # Guardrails: the donor must form a plausible hairstyle around this exact head, not a giant prop.
    if not (head_size.x * 0.90 <= final_size.x <= head_size.x * 2.30):
        raise RuntimeError(f"donor width outside guardrail: {final_size.x} vs head {head_size.x}")
    if final_hi.z < head_hi.z:
        raise RuntimeError("donor does not cover crown")
    if final_lo.y > head_center.y:
        raise RuntimeError("donor sits entirely behind head")
    return {
        "scale": float(uniform_scale),
        "head_bounds": {"min": list(head_lo), "max": list(head_hi), "size": list(head_size)},
        "hair_bounds": {"min": list(final_lo), "max": list(final_hi), "size": list(final_size)},
    }


def create_hair_material():
    mat = bpy.data.materials.get("HairDonorV180") or bpy.data.materials.new("HairDonorV180")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        base = bsdf.inputs.get("Base Color")
        rough = bsdf.inputs.get("Roughness")
        metallic = bsdf.inputs.get("Metallic")
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        coat = bsdf.inputs.get("Coat Weight") or bsdf.inputs.get("Clearcoat")
        if base: base.default_value = (0.022, 0.014, 0.020, 1.0)
        if rough: rough.default_value = 0.34
        if metallic: metallic.default_value = 0.0
        if spec: spec.default_value = 0.28
        if coat: coat.default_value = 0.08
    return mat


def polish_and_parent(donor, hair_root):
    mat = create_hair_material()
    tri_total = 0
    for idx, obj in enumerate(donor):
        obj.name = f"HairDonorV180_{idx:02d}"
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for poly in obj.data.polygons:
            poly.use_smooth = True
        # Preserve world-space placement while moving beneath the dedicated hair root.
        world = obj.matrix_world.copy()
        obj.parent = hair_root
        obj.matrix_world = world
        tri_total += sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)

    # One Catmull-Clark pass turns the modular game asset into a cleaner anime/game silhouette while
    # keeping iPhone cost modest.  The donor file itself remains external and untouched.
    if tri_total < 18000:
        for obj in donor:
            bpy.context.view_layer.objects.active = obj
            sub = obj.modifiers.new("HairDonorV180_Soften", "SUBSURF")
            sub.subdivision_type = "CATMULL_CLARK"
            sub.levels = 1
            sub.render_levels = 1
            try:
                bpy.ops.object.modifier_apply(modifier=sub.name)
            except Exception as exc:
                print("HAIR_V180 subdivision skipped", obj.name, repr(exc))
    return tri_total


def export_glb(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
    )


def main():
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    donor_path = Path(args.donor).resolve()
    if not input_path.is_file():
        raise RuntimeError(f"shipping GLB missing: {input_path}")
    if not donor_path.is_file():
        raise RuntimeError(f"donor blend missing: {donor_path}")

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(input_path))
    head = bpy.data.objects.get("HeadShellV140")
    if head is None or head.type != "MESH":
        raise RuntimeError("HeadShellV140 missing from shipping model")
    hair_root = bpy.data.objects.get("BL_HAIR_ASSET")
    if hair_root is None:
        raise RuntimeError("BL_HAIR_ASSET missing from shipping model")

    locked = {o.name: object_signature(o) for o in bpy.data.objects if is_face_locked(o)}
    if "HeadShellV140" not in locked:
        raise RuntimeError("face lock did not capture HeadShellV140")

    old_hair = [o for o in list(bpy.data.objects) if is_old_style_hair(o)]
    if len(old_hair) < 5:
        raise RuntimeError(f"old hairstyle detection unexpectedly low: {len(old_hair)}")
    old_names = sorted(o.name for o in old_hair)
    for obj in old_hair:
        bpy.data.objects.remove(obj, do_unlink=True)

    donor = append_high_ponytail(donor_path)
    rotated = rotate_tail_to_back(donor)
    fit = fit_to_shipping_head(donor, head)
    donor_tris_before = polish_and_parent(donor, hair_root)

    # Hard face lock: no protected face mesh, transform, or parent may change before export.
    for name, sig in locked.items():
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"FACE LOCK: protected object removed: {name}")
        if object_signature(obj) != sig:
            raise RuntimeError(f"FACE LOCK: protected object changed: {name}")

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["hair_revision"] = "v18.0"
        root["hair_source"] = "OverScore Proxy 1.5 / High Ponytail / CC0"
        root["face_locked_for_hair_v180"] = True

    export_glb(output_path)
    report = {
        "revision": "v18.0",
        "source": "OverScore Proxy 1.5 High Ponytail",
        "license": "CC0",
        "source_url": "https://opengameart.org/node/157297",
        "face_lock_count": len(locked),
        "removed_old_hair_count": len(old_names),
        "removed_old_hair": old_names,
        "donor_objects": [o.name for o in donor],
        "donor_tris_before_soften": donor_tris_before,
        "tail_rotated_180": rotated,
        "fit": fit,
        "output_bytes": output_path.stat().st_size,
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_DONOR_V180_BUILD", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
