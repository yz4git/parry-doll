"""Build Parry Doll hair v18.3 from two CC0/game-ready sources while freezing the face.

Strategy
- Keep the accepted v18.0 high-ponytail silhouette only as a rear-tail guide.
- Use Blender-chan's evaluated Hair Main + Amarillo Hair Geometry Nodes detail for the visible scalp,
  temples and strand language.
- Remove the donor side bun and central face-covering strand mass.
- Open the eyes with a center-part deformation based on the immutable iris position.
- Never modify protected face/head geometry.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

DONOR_MAIN = "BC_HairMain"
DONOR_BUN = "BC_HairBun"
DONOR_DETAIL = "BC_HairRigged"
FINAL_MAIN = "HairPremiumV183_Main"
FINAL_DETAIL = "HairPremiumV183_Detail"
FINAL_TAIL = "HairPremiumV183_Tail"

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
    p.add_argument("--donor", required=True)
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


def transform_objects(objects, matrix):
    for obj in objects:
        obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()


def iris_metrics(head_center):
    iris = [o for o in bpy.data.objects if o.type == "MESH" and "irisouter" in o.name.lower()]
    if not iris:
        iris = [o for o in bpy.data.objects if o.type == "MESH" and "iris" in o.name.lower()]
    if not iris:
        raise RuntimeError("FACE LOCK: iris meshes missing; cannot derive front/eye reveal")
    centers = []
    for obj in iris:
        pts = world_points(obj)
        if pts:
            _, _, c, _ = bounds(pts)
            centers.append(c)
    if not centers:
        raise RuntimeError("FACE LOCK: iris meshes have no points")
    iris_y = sum(c.y for c in centers) / len(centers)
    iris_z = sum(c.z for c in centers) / len(centers)
    eye_x = sum(abs(c.x - head_center.x) for c in centers) / len(centers)
    face_sign = -1.0 if iris_y < head_center.y else 1.0
    return face_sign, float(iris_y), float(iris_z), float(eye_x)


def create_mesh_from_faces(source, keep_face, name):
    mw = source.matrix_world
    vertex_map = {}
    verts = []
    faces = []
    for poly in source.data.polygons:
        world = [mw @ source.data.vertices[i].co for i in poly.vertices]
        center = sum(world, Vector()) / len(world)
        if not keep_face(poly, world, center):
            continue
        face = []
        for old_index, wp in zip(poly.vertices, world):
            key = int(old_index)
            if key not in vertex_map:
                vertex_map[key] = len(verts)
                verts.append((float(wp.x), float(wp.y), float(wp.z)))
            face.append(vertex_map[key])
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


def extract_v180_tail(old_hair, hcenter, hsize, face_sign):
    back_sign = -face_sign

    def primary(_poly, _world, center):
        back = (center.y - hcenter.y) * back_sign
        low = center.z < hcenter.z + hsize.z * 0.13
        return back > hsize.y * 0.23 or (back > hsize.y * 0.07 and low)

    tail = create_mesh_from_faces(old_hair, primary, FINAL_TAIL)
    tris = tri_count(tail)
    if tris < 220:
        bpy.data.objects.remove(tail, do_unlink=True)

        def fallback(_poly, _world, center):
            back = (center.y - hcenter.y) * back_sign
            return back > hsize.y * 0.035

        tail = create_mesh_from_faces(old_hair, fallback, FINAL_TAIL)
        tris = tri_count(tail)
    if tris < 220:
        raise RuntimeError(f"v18.0 ponytail guide crop too small: {tris} tris")

    # Smooth the accepted game-hair silhouette rather than inventing a new tail shape. Two subdivision
    # levels turn the low-poly guide into a clean static mass; premium strand detail is supplied by the
    # Blender-chan detail layer around the root and temples.
    bpy.context.view_layer.objects.active = tail
    tail.select_set(True)
    sub = tail.modifiers.new("TailSurfaceV183", "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=sub.name)
    tail.select_set(False)
    for poly in tail.data.polygons:
        poly.use_smooth = True
    return tail, tris, tri_count(tail)


def remove_old_hair_except_face():
    removed = []
    preserved = []
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not under(obj, "BL_HAIR_ASSET"):
            continue
        if face_name(obj):
            preserved.append(obj.name)
            continue
        if obj.name == FINAL_TAIL:
            continue
        removed.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    return sorted(removed), sorted(preserved)


def import_donor(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
    new = [o for o in bpy.data.objects if o not in before]
    result = {}
    for wanted in (DONOR_MAIN, DONOR_BUN, DONOR_DETAIL):
        obj = bpy.data.objects.get(wanted)
        if obj is None:
            matches = [o for o in new if o.type == "MESH" and o.name.startswith(wanted)]
            obj = matches[0] if matches else None
        if obj is None or obj.type != "MESH":
            raise RuntimeError(f"donor component missing: {wanted}")
        result[wanted] = obj
    return result


def orient_donor(meshes, hcenter, face_sign):
    back_sign = -face_sign
    main = meshes[DONOR_MAIN]
    detail = meshes[DONOR_DETAIL]
    _, _, mc, _ = bounds(world_points(main))
    _, _, dc, _ = bounds(world_points(detail))
    signed_back_delta = (dc.y - mc.y) * back_sign
    rotated = False
    if signed_back_delta < 0:
        pivot = mc
        matrix = Matrix.Translation(pivot) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-pivot)
        transform_objects(meshes.values(), matrix)
        rotated = True
    return rotated, float(signed_back_delta)


def fit_donor(meshes, head):
    hlo, hhi, hcenter, hsize = bounds(world_points(head))
    main = meshes[DONOR_MAIN]
    _, _, mc, ms = bounds(world_points(main))
    scale = (hsize.x * 1.075) / ms.x
    transform_objects(meshes.values(), Matrix.Scale(scale, 4))
    mlo, mhi, mc, _ = bounds(world_points(main))
    translation = Vector((
        hcenter.x - mc.x,
        hcenter.y - mc.y,
        (hhi.z + hsize.z * 0.018) - mhi.z,
    ))
    transform_objects(meshes.values(), Matrix.Translation(translation))
    return hlo, hhi, hcenter, hsize, float(scale)


def set_world_vertex(obj, index, world_point):
    obj.data.vertices[index].co = obj.matrix_world.inverted() @ world_point


def open_center_part(main, hcenter, hsize, face_sign, eye_z, eye_x):
    # Only deform the face-side/lower cap. Back/scalp silhouette remains authored Blender-chan geometry.
    gap = max(hsize.x * 0.115, eye_x * 0.58)
    front_gate = hsize.y * 0.18
    eye_floor = eye_z + hsize.z * 0.035
    changed = 0
    for v in main.data.vertices:
        p = main.matrix_world @ v.co
        front = (p.y - hcenter.y) * face_sign
        if front < front_gate:
            continue
        if p.z > eye_z + hsize.z * 0.28:
            continue
        xrel = p.x - hcenter.x
        ax = abs(xrel)
        # Create a narrow center-part gap instead of the donor's heavy one-eye curtain.
        if ax < gap:
            sign = -1.0 if xrel < 0 else 1.0
            if abs(xrel) < 1e-6:
                sign = 1.0
            blend = 1.0 - ax / gap
            p.x = hcenter.x + sign * (gap + blend * hsize.x * 0.035)
            p.z += blend * hsize.z * 0.055
            changed += 1
        # No central fringe may hang below the iris line.
        if abs(p.x - hcenter.x) < eye_x * 1.22 and p.z < eye_floor:
            p.z = eye_floor
            changed += 1
        set_world_vertex(main, v.index, p)
    main.data.update()
    return changed, float(gap), float(eye_floor)


def crop_detail_to_temples_and_back(detail, hcenter, hsize, face_sign):
    def keep(_poly, _world, center):
        front = (center.y - hcenter.y) * face_sign
        xrel = abs(center.x - hcenter.x)
        # Remove the dense central curtain that hid the face. Keep temple pieces and all rear/root detail.
        if front > hsize.y * 0.015 and xrel < hsize.x * 0.43:
            return False
        return True

    cropped = create_mesh_from_faces(detail, keep, FINAL_DETAIL)
    bpy.data.objects.remove(detail, do_unlink=True)
    return cropped


def compact_detail(detail, hcenter, hsize, face_sign):
    back_sign = -face_sign
    changed = 0
    for v in detail.data.vertices:
        p = detail.matrix_world @ v.co
        xrel = p.x - hcenter.x
        signed = (p.y - hcenter.y) * back_sign
        # Bring radial spikes closer to a commercial-game head silhouette while preserving strand tips.
        p.x = hcenter.x + xrel * 0.73
        if signed >= 0:
            p.y = hcenter.y + back_sign * (hsize.y * 0.025 + signed * 0.78)
            p.z = hcenter.z + (p.z - hcenter.z) * 0.96
        else:
            front = -signed
            p.y = hcenter.y + face_sign * (front * 0.72)
        set_world_vertex(detail, v.index, p)
        changed += 1
    detail.data.update()
    return changed


def decimate_detail(detail, target=56000):
    before = tri_count(detail)
    if before > target:
        mod = detail.modifiers.new("DetailBudgetV183", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = max(0.12, min(1.0, target / before))
        mod.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = detail
        detail.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        detail.select_set(False)
    return before, tri_count(detail)


def make_material():
    mat = bpy.data.materials.get("HairPremiumV183") or bpy.data.materials.new("HairPremiumV183")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.015, 0.007, 0.020, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.30
        bsdf.inputs["Metallic"].default_value = 0.0
        spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if spec is not None:
            spec.default_value = 0.31
        aniso = bsdf.inputs.get("Anisotropic IOR Level") or bsdf.inputs.get("Anisotropic")
        if aniso is not None:
            aniso.default_value = 0.42
        coat = bsdf.inputs.get("Coat Weight")
        if coat is not None:
            coat.default_value = 0.06
        coat_r = bsdf.inputs.get("Coat Roughness")
        if coat_r is not None:
            coat_r.default_value = 0.20
    return mat


def finalize(obj, name, root, mat):
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
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
    donor = Path(a.donor).resolve()
    out = Path(a.output).resolve()
    if not inp.is_file() or not donor.is_file():
        raise RuntimeError(f"missing input/donor: {inp} / {donor}")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(inp))
    head = bpy.data.objects.get("HeadShellV140")
    root = bpy.data.objects.get("BL_HAIR_ASSET")
    old = bpy.data.objects.get("HairDonorV180_00")
    if head is None or head.type != "MESH" or root is None or old is None or old.type != "MESH":
        raise RuntimeError("v18.3 requires accepted v18.0 face/head/hair base")

    face_before = protected_signature()
    hlo, hhi, hcenter, hsize = bounds(world_points(head))
    face_sign, iris_y, eye_z, eye_x = iris_metrics(hcenter)

    tail, tail_source_tris, tail_subdiv_tris = extract_v180_tail(old, hcenter, hsize, face_sign)
    removed, preserved_helpers = remove_old_hair_except_face()

    meshes = import_donor(donor)
    rotated, signed_back_delta = orient_donor(meshes, hcenter, face_sign)
    hlo, hhi, hcenter, hsize, donor_scale = fit_donor(meshes, head)

    # The side bun is the wrong silhouette for Parry Doll; the accepted v18.0 ponytail guide replaces it.
    bpy.data.objects.remove(meshes[DONOR_BUN], do_unlink=True)
    main = meshes[DONOR_MAIN]
    detail = crop_detail_to_temples_and_back(meshes[DONOR_DETAIL], hcenter, hsize, face_sign)
    part_changed, part_gap, eye_floor = open_center_part(main, hcenter, hsize, face_sign, eye_z, eye_x)
    detail_vertices_changed = compact_detail(detail, hcenter, hsize, face_sign)
    detail_before, detail_after = decimate_detail(detail)

    mat = make_material()
    finalize(main, FINAL_MAIN, root, mat)
    finalize(detail, FINAL_DETAIL, root, mat)
    finalize(tail, FINAL_TAIL, root, mat)

    counts = {
        FINAL_MAIN: tri_count(main),
        FINAL_DETAIL: tri_count(detail),
        FINAL_TAIL: tri_count(tail),
    }
    total = sum(counts.values())
    if total < 48000:
        raise RuntimeError(f"v18.3 premium hair detail too low: {total} tris")
    if total > 118000:
        raise RuntimeError(f"v18.3 iPhone hair budget exceeded: {total} tris")

    face_after = protected_signature()
    if face_before != face_after:
        changed = sorted(k for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k))
        raise RuntimeError("FACE LOCK: protected geometry changed: " + ", ".join(changed[:30]))

    hero = bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"] = "v18.3"
        hero["hair_source"] = "Blender-chan CC0 detail + accepted OverScore CC0 high-ponytail silhouette"
        hero["face_locked_for_hair_v183"] = True
        hero["hair_static_visual_priority"] = True

    export_glb(out)
    report = {
        "revision": "v18.3",
        "source_front_detail": "Blender-chan / Amarillo / CC0 / evaluated Amarillo Hair Geometry Nodes",
        "source_tail_guide": "accepted v18.0 OverScore Proxy High Ponytail / CC0",
        "face_locked": True,
        "protected_face_meshes": len(face_before),
        "face_sign_y": face_sign,
        "iris_y": iris_y,
        "eye_z": eye_z,
        "eye_x": eye_x,
        "removed_previous_hair_count": len(removed),
        "removed_previous_hair": removed,
        "preserved_face_helpers_under_hair_root": preserved_helpers,
        "donor_rotated_180": rotated,
        "donor_signed_back_delta": signed_back_delta,
        "donor_scale": donor_scale,
        "center_part_vertices_changed": part_changed,
        "center_part_gap_half_width": part_gap,
        "eye_reveal_floor_z": eye_floor,
        "detail_vertices_compacted": detail_vertices_changed,
        "detail_triangles_before_budget": detail_before,
        "detail_triangles_after_budget": detail_after,
        "tail_source_triangles": tail_source_tris,
        "tail_triangles_after_subdivision": tail_subdiv_tris,
        "triangles": counts,
        "triangles_total": total,
        "head": {"min": vec(hlo), "max": vec(hhi), "center": vec(hcenter), "size": vec(hsize)},
        "output_bytes": out.stat().st_size,
    }
    rp = Path(a.report).resolve()
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("HAIR_HYBRID_V183_BUILD", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
