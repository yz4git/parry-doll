"""Build Parry Doll v18.4 modular anime hair without changing the accepted face.

Sources (both CC0):
- Blender-chan / Amarillo: evaluated Hair Main only, used as a smooth scalp/crown base.
- OverScore Proxy 1.5: Curtain Bangs + High Ponytail, used as authored front/rear silhouette.

Hair Rigged / radial spike geometry from Blender-chan is intentionally NOT used.  The ponytail receives
longitudinal strand ridges derived from its own fitted surface so the static silhouette reads as layered
anime/game hair instead of one smooth tube.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

FINAL_MAIN = "HairPremiumV184_Crown"
FINAL_BANGS = "HairPremiumV184_CurtainBangs"
FINAL_TAIL = "HairPremiumV184_HighPonytail"
FINAL_RIDGES = "HairPremiumV184_TailStrands"
PREFIX = "HairPremiumV184_"

HAIR_MARKERS = (
    "hairdonor", "hairpremium", "hairrear", "hairtop", "herohair", "heropony", "herocrown",
    "ponymass", "ponyfan", "ponyfoundation", "ponywing", "ponyroot", "ponytail", "hairtie",
    "fringe", "bang", "crown", "temporal", "temple", "nape", "wisp", "strand", "lock",
    "cascade", "profileeyeframe", "profilehairornament", "referencewisp", "eyerevealfringe",
    "earfrontwisp", "bl_pony_dynamic",
)
FACE_MARKERS = (
    "headshell", "davidonizaki", "eyelid", "eyelight", "iris", "pupil", "sclera", "wetline",
    "lash", "canthus", "brow", "skinrim", "beautymark", "nose", "lip", "mouth",
    "earantihelix", "earconcha", "earhelix", "earlobefold", "eartragus", "earring",
)


def tail_args():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--blenderchan", required=True, help="Extracted Blender-chan donor GLB containing BC_HairMain")
    p.add_argument("--overscore", required=True, help="OverScore Proxy 1.5 .blend")
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def under(obj, ancestor_name):
    cur = obj
    while cur:
        if cur.name == ancestor_name:
            return True
        cur = cur.parent
    return False


def hair_name(obj):
    n = obj.name.lower()
    return any(token in n for token in HAIR_MARKERS)


def face_name(obj):
    n = obj.name.lower()
    if any(token in n for token in HAIR_MARKERS):
        return False
    return any(token in n for token in FACE_MARKERS)


def protected(obj):
    if obj.type != "MESH":
        return False
    if face_name(obj):
        return True
    return under(obj, "BL_HEAD") and not hair_name(obj) and not obj.name.startswith("BC_Hair")


def canonical_points(obj, digits=6):
    mw = obj.matrix_world
    return tuple(sorted({
        (
            round(float((mw @ v.co).x), digits),
            round(float((mw @ v.co).y), digits),
            round(float((mw @ v.co).z), digits),
        )
        for v in obj.data.vertices
    }))


def protected_signature():
    rows = {}
    for obj in bpy.data.objects:
        if protected(obj):
            rows[obj.name] = {
                "points": canonical_points(obj),
                "parent": obj.parent.name if obj.parent else None,
                "vertices": len(obj.data.vertices),
            }
    if "HeadShellV140" not in rows:
        raise RuntimeError("FACE LOCK: HeadShellV140 missing")
    return rows


def world_points(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]


def bounds(points):
    if not points:
        raise RuntimeError("empty bounds")
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, hi - lo


def vec(v):
    return [float(v.x), float(v.y), float(v.z)]


def tri_count(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def iris_metrics(head_center):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    if not iris:
        raise RuntimeError("FACE LOCK: iris meshes missing")
    centers = []
    for obj in iris:
        pts = world_points(obj)
        if pts:
            _, _, c, _ = bounds(pts)
            centers.append(c)
    if not centers:
        raise RuntimeError("FACE LOCK: iris meshes have no geometry")
    iris_y = sum(c.y for c in centers) / len(centers)
    iris_z = sum(c.z for c in centers) / len(centers)
    eye_x = sum(abs(c.x - head_center.x) for c in centers) / len(centers)
    face_sign = -1.0 if iris_y < head_center.y else 1.0
    return face_sign, float(iris_y), float(iris_z), float(eye_x)


def transform_objects(objects, matrix):
    for obj in objects:
        obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for m in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as exc:
            print("V184 modifier skipped", obj.name, m.name, repr(exc))
    obj.select_set(False)


def remove_old_hair():
    removed, preserved = [], []
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not under(obj, "BL_HAIR_ASSET"):
            continue
        if face_name(obj):
            preserved.append(obj.name)
            continue
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    return sorted(removed), sorted(preserved)


def import_blenderchan_main(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    new = [o for o in bpy.data.objects if o not in before]
    main = bpy.data.objects.get("BC_HairMain")
    if main is None:
        matches = [o for o in new if o.type == "MESH" and o.name.startswith("BC_HairMain")]
        main = matches[0] if matches else None
    if main is None or main.type != "MESH":
        raise RuntimeError("BC_HairMain missing")
    # Explicitly remove all other donor objects; radial Hair Rigged is prohibited in v18.4.
    for obj in list(new):
        if obj is not main:
            bpy.data.objects.remove(obj, do_unlink=True)
    return main


def append_overscore(path):
    wanted = ["Curtain Bangs", "High Ponytail"]
    with bpy.data.libraries.load(str(Path(path).resolve()), link=False) as (src, dst):
        missing = [name for name in wanted if name not in src.objects]
        if missing:
            raise RuntimeError("OverScore exact hair objects missing: " + ", ".join(missing))
        dst.objects = wanted
    result = {}
    for obj in [o for o in dst.objects if o]:
        if obj.type != "MESH":
            raise RuntimeError(f"OverScore {obj.name} is not a mesh")
        if not obj.users_collection:
            bpy.context.scene.collection.objects.link(obj)
        else:
            try:
                bpy.context.scene.collection.objects.link(obj)
            except RuntimeError:
                pass
        apply_modifiers(obj)
        result[obj.name] = obj
    if set(result) != set(wanted):
        raise RuntimeError(f"OverScore append mismatch: {sorted(result)}")
    return result


def orient_and_fit_blenderchan(main, head, face_sign):
    hlo, hhi, hc, hs = bounds(world_points(head))
    _, _, mc, ms = bounds(world_points(main))
    # Prior inspection established Blender-chan hair is 180 degrees opposite the shipping face after GLB
    # extraction. Derive the desired rotation from the immutable face sign rather than hardcoding world -Y.
    # The extracted source uses its prominent lower-front mass toward +Y; map that to the detected face.
    if face_sign < 0:
        rot = Matrix.Translation(mc) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-mc)
        main.matrix_world = rot @ main.matrix_world
        bpy.context.view_layer.update()
    _, _, mc, ms = bounds(world_points(main))
    scale = (hs.x * 1.065) / ms.x
    main.matrix_world = Matrix.Scale(scale, 4) @ main.matrix_world
    bpy.context.view_layer.update()
    mlo, mhi, mc, _ = bounds(world_points(main))
    translation = Vector((
        hc.x - mc.x,
        hc.y - mc.y,
        (hhi.z + hs.z * 0.018) - mhi.z,
    ))
    main.matrix_world = Matrix.Translation(translation) @ main.matrix_world
    bpy.context.view_layer.update()
    return float(scale)


def crop_crown_front(main, hc, hs, face_sign, eye_z):
    """Remove only lower frontal polygons; unlike v18.3 this never deforms remaining vertices."""
    mw = main.matrix_world
    keep_polys = []
    remove = []
    for poly in main.data.polygons:
        pts = [mw @ main.data.vertices[i].co for i in poly.vertices]
        c = sum(pts, Vector()) / len(pts)
        front = (c.y - hc.y) * face_sign
        # Curtain Bangs will cover this cut edge. Keep crown/back untouched.
        if front > hs.y * 0.035 and c.z < eye_z + hs.z * 0.30:
            remove.append(poly.index)
        else:
            keep_polys.append(poly.index)
    if not remove:
        return main, 0
    new = mesh_from_poly_indices(main, keep_polys, FINAL_MAIN)
    bpy.data.objects.remove(main, do_unlink=True)
    return new, len(remove)


def mesh_from_poly_indices(source, indices, name):
    wanted = set(indices)
    mw = source.matrix_world
    vmap, verts, faces = {}, [], []
    for poly in source.data.polygons:
        if poly.index not in wanted:
            continue
        face = []
        for old in poly.vertices:
            if int(old) not in vmap:
                wp = mw @ source.data.vertices[old].co
                vmap[int(old)] = len(verts)
                verts.append((float(wp.x), float(wp.y), float(wp.z)))
            face.append(vmap[int(old)])
        if len(face) >= 3:
            faces.append(face)
    if not faces:
        raise RuntimeError(f"{name}: crop produced no faces")
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def overscore_tail_direction(objs):
    tail = objs["High Ponytail"]
    pts = world_points(tail)
    zs = sorted(p.z for p in pts)
    q35 = zs[int((len(zs) - 1) * 0.35)]
    q72 = zs[int((len(zs) - 1) * 0.72)]
    low = [p for p in pts if p.z <= q35]
    high = [p for p in pts if p.z >= q72]
    return (sum(p.y for p in low) / len(low)) - (sum(p.y for p in high) / len(high))


def fit_overscore_pair(objs, head, face_sign):
    hlo, hhi, hc, hs = bounds(world_points(head))
    tail = objs["High Ponytail"]
    all_objs = list(objs.values())
    direction = overscore_tail_direction(objs)
    back_sign = -face_sign
    # direction * back_sign should be positive when tail points behind the face.
    rotated = False
    if direction * back_sign < 0:
        _, _, pivot, _ = bounds(world_points(tail))
        rot = Matrix.Translation(pivot) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-pivot)
        transform_objects(all_objs, rot)
        rotated = True

    tpts = world_points(tail)
    tlo, thi, _, ts = bounds(tpts)
    crown_cut = thi.z - ts.z * 0.44
    crown = [p for p in tpts if p.z >= crown_cut]
    crown_width = max(p.x for p in crown) - min(p.x for p in crown)
    if crown_width <= 1e-7:
        raise RuntimeError("OverScore High Ponytail crown width invalid")
    scale = (hs.x * 1.075) / crown_width
    transform_objects(all_objs, Matrix.Scale(scale, 4))

    # Align using High Ponytail crown/front exactly once so Curtain Bangs retains author-matched placement.
    tlo, thi, tc, ts = bounds(world_points(tail))
    target_front = hc.y + face_sign * (hs.y * 0.54)
    donor_front = tlo.y if face_sign < 0 else thi.y
    dy = target_front - donor_front
    dx = hc.x - tc.x
    dz = (hhi.z + hs.z * 0.035) - thi.z
    transform_objects(all_objs, Matrix.Translation(Vector((dx, dy, dz))))
    return float(scale), rotated, float(direction)


def crop_high_ponytail_to_rear(tail, hc, hs, face_sign):
    back_sign = -face_sign
    mw = tail.matrix_world
    keep = []
    for poly in tail.data.polygons:
        pts = [mw @ tail.data.vertices[i].co for i in poly.vertices]
        c = sum(pts, Vector()) / len(pts)
        back = (c.y - hc.y) * back_sign
        root = c.z > hc.z + hs.z * 0.24
        if back > -hs.y * 0.025 or (root and back > -hs.y * 0.12):
            keep.append(poly.index)
    rear = mesh_from_poly_indices(tail, keep, FINAL_TAIL)
    bpy.data.objects.remove(tail, do_unlink=True)
    return rear


def subdivide(obj, levels, name):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    sub = obj.modifiers.new(name, "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = levels
    sub.render_levels = levels
    bpy.ops.object.modifier_apply(modifier=sub.name)
    obj.select_set(False)
    for p in obj.data.polygons:
        p.use_smooth = True


def fit_curtain_to_face(bangs, head, face_sign, iris_y, eye_z, eye_x):
    hlo, hhi, hc, hs = bounds(world_points(head))
    blo, bhi, bc, bs = bounds(world_points(bangs))
    # After paired donor fit, refine only bangs scale around its own center so it frames the immutable eyes.
    target_width = max(hs.x * 0.86, eye_x * 2.65)
    if bs.x <= 1e-7:
        raise RuntimeError("Curtain Bangs width invalid")
    sx = target_width / bs.x
    # Scale uniformly enough to keep authored shape, then place lower tips slightly above lower eye rim.
    pivot = bc
    matrix = Matrix.Translation(pivot) @ Matrix.Scale(sx, 4) @ Matrix.Translation(-pivot)
    bangs.matrix_world = matrix @ bangs.matrix_world
    bpy.context.view_layer.update()
    blo, bhi, bc, bs = bounds(world_points(bangs))
    donor_front = blo.y if face_sign < 0 else bhi.y
    desired_front = iris_y + face_sign * (hs.y * 0.055)
    desired_bottom = eye_z - hs.z * 0.055
    translation = Vector((hc.x - bc.x, desired_front - donor_front, desired_bottom - blo.z))
    bangs.matrix_world = Matrix.Translation(translation) @ bangs.matrix_world
    bpy.context.view_layer.update()
    return float(sx)


def tail_slice_stats(tail, slices=9):
    pts = world_points(tail)
    lo, hi, _, size = bounds(pts)
    rows = []
    for i in range(slices):
        t = i / (slices - 1)
        z = hi.z * (1 - t) + lo.z * t
        half = max(size.z / (slices - 1) * 0.65, size.z * 0.035)
        band = [p for p in pts if abs(p.z - z) <= half]
        if len(band) < 4:
            band = sorted(pts, key=lambda p: abs(p.z - z))[: max(8, min(32, len(pts)))]
        xmin, xmax = min(p.x for p in band), max(p.x for p in band)
        ymin, ymax = min(p.y for p in band), max(p.y for p in band)
        rows.append({
            "z": z,
            "xc": (xmin + xmax) * 0.5,
            "yc": (ymin + ymax) * 0.5,
            "rx": max((xmax - xmin) * 0.5, size.x * 0.08),
            "ry": max((ymax - ymin) * 0.5, size.y * 0.08),
        })
    return rows


def add_tail_ridges(tail, hs):
    rows = tail_slice_stats(tail, slices=10)
    coll = bpy.data.collections.new("HairPremiumV184Strands")
    bpy.context.scene.collection.children.link(coll)
    curves = []
    # 8 surface-following strands; rotate start angle slightly per strand for organic breakup.
    for j in range(8):
        theta = (j / 8.0) * math.tau + 0.17
        curve = bpy.data.curves.new(f"TailStrandCurveV184_{j:02d}", "CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        curve.bevel_depth = hs.x * (0.0046 + 0.00045 * (j % 3))
        curve.bevel_resolution = 2
        spl = curve.splines.new("BEZIER")
        spl.bezier_points.add(len(rows) - 1)
        for i, row in enumerate(rows):
            # Slight taper inward toward the tip and a small phase drift to avoid parallel tubes.
            taper = 0.82 - 0.30 * (i / max(1, len(rows) - 1))
            phase = theta + math.sin(i * 0.65 + j) * 0.07
            p = Vector((
                row["xc"] + row["rx"] * math.cos(phase) * taper,
                row["yc"] + row["ry"] * math.sin(phase) * taper,
                row["z"],
            ))
            bp = spl.bezier_points[i]
            bp.co = p
            bp.handle_left_type = "AUTO"
            bp.handle_right_type = "AUTO"
            bp.radius = max(0.35, 1.0 - 0.055 * i)
        obj = bpy.data.objects.new(f"TailStrandV184_{j:02d}", curve)
        coll.objects.link(obj)
        curves.append(obj)

    # Convert and join to one game mesh.
    bpy.ops.object.select_all(action="DESELECT")
    for o in curves:
        o.select_set(True)
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.convert(target="MESH")
    converted = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if not converted:
        raise RuntimeError("tail strand conversion failed")
    bpy.context.view_layer.objects.active = converted[0]
    for o in converted:
        o.select_set(True)
    if len(converted) > 1:
        bpy.ops.object.join()
    ridges = bpy.context.view_layer.objects.active
    ridges.name = FINAL_RIDGES
    ridges.data.name = FINAL_RIDGES + "Mesh"
    return ridges


def make_material():
    mat = bpy.data.materials.get("HairPremiumV184") or bpy.data.materials.new("HairPremiumV184")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.014, 0.007, 0.020, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.29
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.31
        aniso = bsdf.inputs.get("Anisotropic IOR Level") or bsdf.inputs.get("Anisotropic")
        if aniso is not None:
            aniso.default_value = 0.43
        coat = bsdf.inputs.get("Coat Weight")
        if coat is not None:
            coat.default_value = 0.055
        coat_r = bsdf.inputs.get("Coat Roughness")
        if coat_r is not None:
            coat_r.default_value = 0.19
    return mat


def finalize(obj, name, root, mat):
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    world = obj.matrix_world.copy()
    obj.parent = root
    obj.matrix_world = world


def export_glb(path):
    out = Path(path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_animations=True,
    )


def main():
    a = parse_args()
    inp = Path(a.input).resolve()
    bc_path = Path(a.blenderchan).resolve()
    os_path = Path(a.overscore).resolve()
    out = Path(a.output).resolve()
    for p in (inp, bc_path, os_path):
        if not p.is_file():
            raise RuntimeError(f"missing input: {p}")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(inp))
    head = bpy.data.objects.get("HeadShellV140")
    root = bpy.data.objects.get("BL_HAIR_ASSET")
    if head is None or head.type != "MESH" or root is None:
        raise RuntimeError("accepted heroine head/hair root missing")

    face_before = protected_signature()
    hlo, hhi, hc, hs = bounds(world_points(head))
    face_sign, iris_y, eye_z, eye_x = iris_metrics(hc)
    removed, preserved_helpers = remove_old_hair()
    for name in face_before:
        if bpy.data.objects.get(name) is None:
            raise RuntimeError(f"FACE LOCK: protected object removed with old hair: {name}")

    crown = import_blenderchan_main(bc_path)
    crown_scale = orient_and_fit_blenderchan(crown, head, face_sign)
    crown, crown_removed_polys = crop_crown_front(crown, hc, hs, face_sign, eye_z)

    over = append_overscore(os_path)
    over_scale, over_rotated, over_tail_direction = fit_overscore_pair(over, head, face_sign)
    bangs = over["Curtain Bangs"]
    tail = crop_high_ponytail_to_rear(over["High Ponytail"], hc, hs, face_sign)
    bangs_scale_refine = fit_curtain_to_face(bangs, head, face_sign, iris_y, eye_z, eye_x)

    # High enough subdivision to make imported low-poly donor smooth, but all shape decisions remain donor-authored.
    subdivide(bangs, 4, "CurtainBangsSurfaceV184")
    subdivide(tail, 3, "HighPonytailSurfaceV184")
    ridges = add_tail_ridges(tail, hs)

    # Small mobile guardrail. If imported donor tessellation changes, fail rather than silently balloon iPhone cost.
    counts = {
        FINAL_MAIN: tri_count(crown),
        FINAL_BANGS: tri_count(bangs),
        FINAL_TAIL: tri_count(tail),
        FINAL_RIDGES: tri_count(ridges),
    }
    total = sum(counts.values())
    if total < 22000:
        raise RuntimeError(f"v18.4 hair detail unexpectedly low: {total}")
    if total > 90000:
        raise RuntimeError(f"v18.4 hair exceeds iPhone budget: {total}")

    mat = make_material()
    finalize(crown, FINAL_MAIN, root, mat)
    finalize(bangs, FINAL_BANGS, root, mat)
    finalize(tail, FINAL_TAIL, root, mat)
    finalize(ridges, FINAL_RIDGES, root, mat)

    face_after = protected_signature()
    if face_before != face_after:
        changed = sorted(k for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k))
        raise RuntimeError("FACE LOCK: protected geometry changed: " + ", ".join(changed[:30]))

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.4"
        hero["hair_source"] = "Blender-chan CC0 Hair Main + OverScore Proxy CC0 Curtain Bangs + High Ponytail"
        hero["face_locked_for_hair_v184"] = True
        hero["hair_static_visual_priority"] = True
        hero["hair_radial_spike_donor_used"] = False

    export_glb(out)
    report = {
        "revision": "v18.4",
        "face_locked": True,
        "protected_face_meshes": len(face_before),
        "source_crown": "Blender-chan / Amarillo / CC0 / Hair Main",
        "source_bangs": "OverScore Proxy 1.5 / CC0 / Curtain Bangs",
        "source_tail": "OverScore Proxy 1.5 / CC0 / High Ponytail",
        "blenderchan_hair_rigged_used": False,
        "face_sign_y": face_sign,
        "iris_y": iris_y,
        "eye_z": eye_z,
        "eye_x": eye_x,
        "removed_previous_hair_count": len(removed),
        "removed_previous_hair": removed,
        "preserved_face_helpers_under_hair_root": preserved_helpers,
        "crown_scale": crown_scale,
        "crown_removed_front_polygons": crown_removed_polys,
        "overscore_scale": over_scale,
        "overscore_rotated_180": over_rotated,
        "overscore_tail_direction_before_fit": over_tail_direction,
        "curtain_bangs_refine_scale": bangs_scale_refine,
        "triangles": counts,
        "triangles_total": total,
        "head": {"min": vec(hlo), "max": vec(hhi), "center": vec(hc), "size": vec(hs)},
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_MODULAR_V184_BUILD", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
