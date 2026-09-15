"""v18.5 r15: put donor-blue UVs into TEXCOORD_0 for the seven crown locks.

r14 proved that glTF was still using the original first UV set. This revision overwrites the first
UV layer in-place while sharing the exact donor hair material. Mesh geometry remains immutable.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import bpy

R14_PATH = Path(__file__).with_name("match-hair-crown-blue-uv-v185-r14.py")
spec = importlib.util.spec_from_file_location("r14core", R14_PATH)
r14 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(r14)
r13 = r14.r13


def tail_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--report", required=True)
    return p.parse_args(tail_args())


def transfer_uv0(lock, bvh, hverts, tris, tri_uvs):
    if not lock.data.uv_layers:
        uv = lock.data.uv_layers.new(name="CrownR15UV0")
    else:
        uv = lock.data.uv_layers[0]
    uv.name = "CrownR15UV0"
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
    return uv.name, max(distances), sum(distances) / len(distances), len(distances)


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
    before_uv_names = {o.name:[u.name for u in o.data.uv_layers] for o in locks}

    bvh,hverts,tris,tri_uvs,donor_uv,donor_img,eligible,rejected,score_min,score_max = r14.donor_blue_surface(hair, donor_mat)
    per_lock = {}
    prior_materials = {}
    for obj in locks:
        prior_materials[obj.name] = list(r13.material_signature(obj))
        uv_name,dmax,dmean,loops = transfer_uv0(obj,bvh,hverts,tris,tri_uvs)
        obj.data.materials.clear(); obj.data.materials.append(donor_mat)
        for poly in obj.data.polygons: poly.material_index=0
        per_lock[obj.name] = {"uv0":uv_name,"uv_loops":loops,"nearest_blue_donor_max_distance":dmax,"nearest_blue_donor_mean_distance":dmean}

    geom_after = {o.name:r13.geom_signature(o) for o in bpy.data.objects if o.type=="MESH"}
    if geom_after != geom_before:
        changed=[n for n in geom_before if geom_before.get(n)!=geom_after.get(n)]
        raise RuntimeError("GEOMETRY LOCK changed: "+", ".join(changed[:20]))
    if {o.name:r13.geom_signature(o) for o in bpy.data.objects if r13.protected_face(o)} != face_before: raise RuntimeError("FACE LOCK changed")
    if r13.material_signature(hair)!=hair_mat_before: raise RuntimeError("MAIN HAIR MATERIAL changed")
    if r13.material_signature(cap)!=cap_mat_before: raise RuntimeError("SCALP GAP MATERIAL changed")
    if any(r13.material_signature(o)!=(donor_mat.name,) for o in locks): raise RuntimeError("LOCK donor material assignment failed")

    hero=bpy.data.objects.get("BLENDER_HEROINE")
    if hero:
        hero["hair_revision"]="v18.5-r15"
        hero["hair_refinement"]="crown-lock-donor-blue-texcoord0"
        hero["geometry_locked_for_hair_v185_r15"]=True
        hero["face_locked_for_hair_v185_r15"]=True
    out=Path(a.output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",export_apply=False,export_materials="EXPORT",export_image_format="AUTO")
    report={"revision":"v18.5-r15","scope":"seven-crown-lock-donor-blue-texcoord0","geometry_unchanged":True,"face_unchanged":True,"main_hair_unchanged":True,"bangs_unchanged":True,"side_hair_unchanged":True,"ponytail_unchanged":True,"scalp_gap_material_unchanged":True,"crown_lock_count":len(locks),"exact_shared_material":donor_mat.name,"donor_texture":donor_img,"donor_uv_layer":donor_uv,"eligible_blue_triangles":eligible,"rejected_nonblue_triangles":rejected,"before_lock_uv_layers":before_uv_names,"per_lock_transfer":per_lock,"output_bytes":out.stat().st_size}
    rp=Path(a.report).resolve(); rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HAIR_CROWN_UV0_V185_R15",json.dumps(report,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
