"""v18.5 r14: exact donor material + UV transfer restricted to blue hair texels.

Rejects white/skin/dark atlas regions before building the donor BVH. Geometry stays immutable.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

import importlib.util
R13_PATH = Path(__file__).with_name("match-hair-crown-exact-v185-r13.py")
spec = importlib.util.spec_from_file_location("r13core", R13_PATH)
r13 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(r13)

UV_NAME = "HairCrownBlueR14UV"


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def image_from_material(mat):
    if not mat.use_nodes or not mat.node_tree:
        raise RuntimeError("donor material nodes missing")
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None:
            return node.image
    raise RuntimeError("donor texture image missing")


def sample_image(img, uv):
    w, h = img.size
    u = max(0.0, min(0.999999, float(uv.x)))
    v = max(0.0, min(0.999999, float(uv.y)))
    x = min(w - 1, max(0, int(u * w)))
    y = min(h - 1, max(0, int(v * h)))
    base = (y * w + x) * 4
    px = img.pixels
    return (float(px[base]), float(px[base+1]), float(px[base+2]))


def blue_score(rgb):
    r, g, b = rgb
    lum = (r + g + b) / 3.0
    if lum < 0.075 or lum > 0.78:
        return -1.0
    if b < 0.24:
        return -1.0
    # Require clearly blue/violet donor hair; rejects white and neutral atlas content.
    if b < r * 1.18 or b < g * 1.08:
        return -1.0
    return (b - (r + g) * 0.5) + 0.18 * b


def donor_blue_surface(hair, donor_mat):
    if not hair.data.uv_layers or hair.data.uv_layers.active is None:
        raise RuntimeError("donor active UV missing")
    uv_layer = hair.data.uv_layers.active
    img = image_from_material(donor_mat)
    mw = hair.matrix_world
    verts = [mw @ v.co for v in hair.data.vertices]
    tris = []
    tri_uvs = []
    scores = []
    rejected = 0
    for poly in hair.data.polygons:
        vids = list(poly.vertices)
        loops = list(poly.loop_indices)
        for j in range(1, len(vids) - 1):
            uv0 = uv_layer.data[loops[0]].uv.copy()
            uv1 = uv_layer.data[loops[j]].uv.copy()
            uv2 = uv_layer.data[loops[j+1]].uv.copy()
            center = (uv0 + uv1 + uv2) / 3.0
            sc = blue_score(sample_image(img, center))
            if sc < 0.0:
                rejected += 1
                continue
            tris.append((vids[0], vids[j], vids[j+1]))
            tri_uvs.append((uv0, uv1, uv2))
            scores.append(sc)
    if len(tris) < 100:
        raise RuntimeError(f"too few blue donor triangles: {len(tris)}")
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), verts, tris, tri_uvs, uv_layer.name, img.name, len(tris), rejected, min(scores), max(scores)


def transfer_uv(lock, bvh, hverts, tris, tri_uvs):
    uv = lock.data.uv_layers.get(UV_NAME) or lock.data.uv_layers.new(name=UV_NAME)
    lock.data.uv_layers.active = uv
    mw = lock.matrix_world
    distances = []
    for poly in lock.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = lock.data.loops[loop_idx].vertex_index
            p = mw @ lock.data.vertices[vi].co
            loc, _normal, tri_idx, dist = bvh.find_nearest(p)
            if loc is None or tri_idx is None:
                raise RuntimeError(f"blue donor nearest surface missing for {lock.name}:{vi}")
            ia, ib, ic = tris[tri_idx]
            wa, wb, wc = r13.barycentric(loc, hverts[ia], hverts[ib], hverts[ic])
            ua, ub, uc = tri_uvs[tri_idx]
            q = ua * wa + ub * wb + uc * wc
            uv.data[loop_idx].uv = (float(q.x), float(q.y))
            distances.append(float(dist))
    return max(distances), sum(distances)/len(distances), len(distances)


def main():
    a = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(a.input).resolve()))

    head = bpy.data.objects.get(r13.HEAD)
    hair = bpy.data.objects.get(r13.HAIR)
    cap = bpy.data.objects.get(r13.CAP)
    locks = sorted([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(r13.LOCK_PREFIX)], key=lambda o:o.name)
    if not head or not hair or not cap or len(locks) != 7:
        raise RuntimeError(f"r12 objects missing head={bool(head)} hair={bool(hair)} cap={bool(cap)} locks={len(locks)}")
    if not hair.data.materials or hair.data.materials[0] is None:
        raise RuntimeError("donor hair material missing")
    donor_mat = hair.data.materials[0]

    geom_before = {o.name:r13.geom_signature(o) for o in bpy.data.objects if o.type=="MESH"}
    face_before = {o.name:r13.geom_signature(o) for o in bpy.data.objects if r13.protected_face(o)}
    hair_mat_before = r13.material_signature(hair)
    cap_mat_before = r13.material_signature(cap)

    bvh,hverts,tris,tri_uvs,donor_uv,donor_img,eligible,rejected,score_min,score_max = donor_blue_surface(hair, donor_mat)
    per_lock = {}
    prior_materials = {}
    for obj in locks:
        prior_materials[obj.name] = list(r13.material_signature(obj))
        dmax,dmean,loops = transfer_uv(obj,bvh,hverts,tris,tri_uvs)
        obj.data.materials.clear()
        obj.data.materials.append(donor_mat)
        for poly in obj.data.polygons:
            poly.material_index=0
        per_lock[obj.name] = {"uv_loops":loops,"nearest_blue_donor_max_distance":dmax,"nearest_blue_donor_mean_distance":dmean}

    geom_after = {o.name:r13.geom_signature(o) for o in bpy.data.objects if o.type=="MESH"}
    if geom_after != geom_before:
        changed=[n for n in geom_before if geom_before.get(n)!=geom_after.get(n)]
        raise RuntimeError("GEOMETRY LOCK changed: "+", ".join(changed[:20]))
    if {o.name:r13.geom_signature(o) for o in bpy.data.objects if r13.protected_face(o)} != face_before:
        raise RuntimeError("FACE LOCK changed")
    if r13.material_signature(hair)!=hair_mat_before:
        raise RuntimeError("MAIN HAIR MATERIAL changed")
    if r13.material_signature(cap)!=cap_mat_before:
        raise RuntimeError("SCALP GAP MATERIAL changed")
    if any(r13.material_signature(o)!=(donor_mat.name,) for o in locks):
        raise RuntimeError("LOCK donor material assignment failed")

    hero=bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"]="v18.5-r14"
        hero["hair_refinement"]="crown-lock-blue-atlas-exact-donor"
        hero["geometry_locked_for_hair_v185_r14"]=True
        hero["face_locked_for_hair_v185_r14"]=True

    out=Path(a.output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",export_apply=False,export_materials="EXPORT",export_image_format="AUTO")
    report={
        "revision":"v18.5-r14","scope":"seven-crown-lock-blue-atlas-exact-donor",
        "geometry_unchanged":True,"face_unchanged":True,"main_hair_unchanged":True,
        "bangs_unchanged":True,"side_hair_unchanged":True,"ponytail_unchanged":True,
        "scalp_gap_material_unchanged":True,"crown_lock_count":len(locks),
        "exact_shared_material":donor_mat.name,"donor_texture":donor_img,"donor_uv_layer":donor_uv,
        "transferred_uv_layer":UV_NAME,"eligible_blue_triangles":eligible,"rejected_nonblue_triangles":rejected,
        "blue_score_min":score_min,"blue_score_max":score_max,"prior_lock_materials":prior_materials,
        "per_lock_transfer":per_lock,"output_bytes":out.stat().st_size,
    }
    rp=Path(a.report).resolve(); rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HAIR_CROWN_BLUE_V185_R14",json.dumps(report,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
