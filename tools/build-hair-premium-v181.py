"""Hair-only high-detail donor pass for Parry Doll v18.1.

Source target: OpenGameArt Toon/Low Poly Dread Ponytail by tiko479, CC0, Blender-authored.
The donor is intentionally much denser than the rejected v18.0 proxy hair.  The shipping face is
immutable; only descendants of BL_HAIR_ASSET are removed/replaced.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "dist/assets/models/heroine-blender.glb"
DEFAULT_REPORT = ROOT / "dist/hair-premium-v181-build.json"


def argv_tail():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(DEFAULT_MODEL))
    p.add_argument("--output", default=str(DEFAULT_MODEL))
    p.add_argument("--donor", required=True)
    p.add_argument("--report", default=str(DEFAULT_REPORT))
    return p.parse_args(argv_tail())


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def descendants(root):
    out = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        out.append(obj)
        stack.extend(obj.children)
    return out


def under(obj, ancestor_name):
    cur = obj
    while cur:
        if cur.name == ancestor_name:
            return True
        cur = cur.parent
    return False


def points_world(obj):
    if obj.type != "MESH":
        return []
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(pts):
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def protected_signature():
    sig = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not under(o, "BL_HEAD") or under(o, "BL_HAIR_ASSET"):
            continue
        pts = tuple(
            sorted(
                (
                    round(float((o.matrix_world @ v.co).x), 6),
                    round(float((o.matrix_world @ v.co).y), 6),
                    round(float((o.matrix_world @ v.co).z), 6),
                )
                for v in o.data.vertices
            )
        )
        sig[o.name] = (pts, o.parent.name if o.parent else None)
    if "HeadShellV140" not in sig:
        raise RuntimeError("FACE LOCK: HeadShellV140 not protected")
    return sig


def append_source_objects(path):
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = list(src.objects)
        source_names = list(src.objects)
    loaded = [o for o in dst.objects if o and o not in before]
    for o in loaded:
        if not o.users_collection:
            bpy.context.scene.collection.objects.link(o)
    candidates = [o for o in loaded if o.type in {"MESH", "CURVE"}]
    if not candidates:
        raise RuntimeError("donor blend contains no mesh/curve objects")

    hair_named = [o for o in candidates if any(t in o.name.lower() for t in ("hair", "dread", "pony", "strand", "lock", "style"))]
    if hair_named:
        chosen = hair_named
    else:
        reject = ("camera", "light", "head", "face", "eye", "bust", "body", "mannequin")
        chosen = [o for o in candidates if not any(t in o.name.lower() for t in reject)]
    if not chosen:
        chosen = candidates

    for o in list(loaded):
        if o not in chosen:
            bpy.data.objects.remove(o, do_unlink=True)
    print("HAIR_V181 source objects", source_names)
    print("HAIR_V181 chosen", [(o.name, o.type) for o in chosen])
    return chosen, source_names


def freeze_and_convert(objects):
    meshes = []
    for obj in list(objects):
        if obj.animation_data:
            obj.animation_data_clear()
        for mod in list(obj.modifiers):
            if mod.type in {"SOFT_BODY", "CLOTH", "COLLISION", "DYNAMIC_PAINT"}:
                obj.modifiers.remove(mod)
        if obj.type == "CURVE":
            try:
                obj.data.resolution_u = max(3, min(6, int(obj.data.resolution_u)))
            except Exception:
                pass
            try:
                obj.data.bevel_resolution = max(2, min(4, int(obj.data.bevel_resolution)))
            except Exception:
                pass
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.convert(target="MESH")
            obj = bpy.context.view_layer.objects.active
        if obj.type == "MESH":
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            for mod in list(obj.modifiers):
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except Exception as exc:
                    print("HAIR_V181 modifier skipped", obj.name, mod.name, repr(exc))
            meshes.append(obj)
    if not meshes:
        raise RuntimeError("donor conversion produced no meshes")
    return meshes


def join_meshes(meshes):
    if len(meshes) == 1:
        return meshes[0]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def orient_back(obj):
    pts = points_world(obj)
    lo, hi, center, size = bounds(pts)
    if size.z <= 1e-8:
        return False
    z_low = lo.z + size.z * 0.35
    z_high = hi.z - size.z * 0.30
    low = [p for p in pts if p.z <= z_low]
    high = [p for p in pts if p.z >= z_high]
    if not low or not high:
        return False
    low_y = sum(p.y for p in low) / len(low)
    high_y = sum(p.y for p in high) / len(high)
    if low_y < high_y - size.y * 0.04:
        rot = Matrix.Translation(center) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-center)
        obj.matrix_world = rot @ obj.matrix_world
        bpy.context.view_layer.update()
        return True
    return False


def fit_to_head(obj, head):
    hp = points_world(head)
    hlo, hhi, hcenter, hsize = bounds(hp)
    dp = points_world(obj)
    dlo, dhi, dcenter, dsize = bounds(dp)

    crown_cut = dhi.z - dsize.z * 0.42
    crown = [p for p in dp if p.z >= crown_cut]
    if len(crown) < 20:
        crown = dp
    crown_width = max(1e-7, max(p.x for p in crown) - min(p.x for p in crown))
    target_width = hsize.x * 1.14
    scale = max(0.0001, min(target_width / crown_width, 1000.0))
    obj.matrix_world = Matrix.Scale(scale, 4) @ obj.matrix_world
    bpy.context.view_layer.update()

    dp = points_world(obj)
    dlo, dhi, dcenter, dsize = bounds(dp)
    crown_cut = dhi.z - dsize.z * 0.42
    crown = [p for p in dp if p.z >= crown_cut]
    crown_center_x = (min(p.x for p in crown) + max(p.x for p in crown)) * 0.5
    crown_front = min(p.y for p in crown)
    target_front = hlo.y - hsize.y * 0.022
    target_top = hhi.z + hsize.z * 0.045
    trans = Vector((hcenter.x - crown_center_x, target_front - crown_front, target_top - dhi.z))
    obj.matrix_world = Matrix.Translation(trans) @ obj.matrix_world
    bpy.context.view_layer.update()

    flo, fhi, _, fsize = bounds(points_world(obj))
    if not (hsize.x * 0.90 <= fsize.x <= hsize.x * 2.70):
        raise RuntimeError(f"hair width guardrail failed: {fsize.x} vs head {hsize.x}")
    if fhi.z < hhi.z:
        raise RuntimeError("hair does not cover crown")
    if flo.y > hcenter.y:
        raise RuntimeError("hair is entirely behind the face")
    return {
        "scale": float(scale),
        "head": {"min": list(hlo), "max": list(hhi), "size": list(hsize)},
        "hair": {"min": list(flo), "max": list(fhi), "size": list(fsize)},
    }


def optimize_density(obj):
    before = tri_count(obj)
    target_max = 95000
    if before > target_max:
        ratio = target_max / before
        dec = obj.modifiers.new("HairPremiumV181_GameBudget", "DECIMATE")
        dec.decimate_type = "COLLAPSE"
        dec.ratio = ratio
        dec.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.modifier_apply(modifier=dec.name)
        except Exception as exc:
            print("HAIR_V181 decimate failed", repr(exc))
    after = tri_count(obj)
    # Never inflate a sparse donor to pretend it is high-detail.  This pass is accepted only if the
    # actual donor still contains substantial authored geometry after conversion.
    if after < 30000:
        raise RuntimeError(f"high-detail hair quality gate failed: only {after} tris")
    if after > 120000:
        raise RuntimeError(f"hair exceeds mobile quality budget: {after} tris")
    return before, after


def hair_material():
    mat = bpy.data.materials.get("HairPremiumV181") or bpy.data.materials.new("HairPremiumV181")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": (0.020, 0.012, 0.020, 1.0),
            "Roughness": 0.30,
            "Metallic": 0.0,
            "IOR": 1.45,
            "Anisotropic IOR Level": 0.30,
            "Coat Weight": 0.10,
            "Coat Roughness": 0.20,
        }
        for key, value in values.items():
            inp = bsdf.inputs.get(key)
            if inp is not None:
                inp.default_value = value
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.32
    return mat


def polish(obj, hair_root):
    obj.name = "HairPremiumV181"
    obj.data.name = "HairPremiumV181Mesh"
    obj.data.materials.clear()
    obj.data.materials.append(hair_material())
    for p in obj.data.polygons:
        p.use_smooth = True
    world = obj.matrix_world.copy()
    obj.parent = hair_root
    obj.matrix_world = world


def export(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
    )


def main():
    a = args()
    inp, out, donor = Path(a.input).resolve(), Path(a.output).resolve(), Path(a.donor).resolve()
    if not inp.is_file() or not donor.is_file():
        raise RuntimeError(f"missing input or donor: {inp} / {donor}")

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(inp))
    head = bpy.data.objects.get("HeadShellV140")
    hair_root = bpy.data.objects.get("BL_HAIR_ASSET")
    if not head or head.type != "MESH" or not hair_root:
        raise RuntimeError("shipping head/hair root missing")

    face_before = protected_signature()
    old = descendants(hair_root)
    old_names = sorted(o.name for o in old)
    for o in list(old):
        if o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)

    source, source_names = append_source_objects(donor)
    meshes = freeze_and_convert(source)
    hair = join_meshes(meshes)
    rotated = orient_back(hair)
    fit = fit_to_head(hair, head)
    tris_before, tris_final = optimize_density(hair)
    polish(hair, hair_root)

    face_after = protected_signature()
    if face_before != face_after:
        changed = sorted(k for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k))
        raise RuntimeError("FACE LOCK: protected head changed before export: " + ", ".join(changed[:20]))

    root = bpy.data.objects.get("BLENDER_HEROINE")
    if root:
        root["hair_revision"] = "v18.1"
        root["hair_source"] = "OpenGameArt Toon Low Poly Dread Ponytail / tiko479 / CC0"
        root["face_locked_for_hair_v181"] = True
        root["hair_static_visual_priority"] = True

    export(out)
    report = {
        "revision": "v18.1",
        "source": "Toon/Low Poly Dread Ponytail",
        "source_author": "tiko479",
        "source_url": "https://opengameart.org/content/toonlow-poly-dread-ponytail",
        "license": "CC0",
        "source_objects": source_names,
        "removed_previous_hair": old_names,
        "face_lock_count": len(face_before),
        "tail_or_long_mass_rotated_180": rotated,
        "triangles_before_mobile_budget": tris_before,
        "triangles_final": tris_final,
        "fit": fit,
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_PREMIUM_V181_BUILD", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
