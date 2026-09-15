"""Final crown-only tuning layered on v18.5 r9.

Reuses r9's face/main-hair locks and donor-color extraction, but darkens the crown gap-fill
and increases only the existing cap's directional hair relief. No face, bangs, side hair or
ponytail geometry is edited.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

BASE = Path(__file__).with_name("fix-hair-crown-v185-r9.py")
spec = importlib.util.spec_from_file_location("hair_crown_r9", BASE)
r9 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(r9)


def final_relief(cap, hc, hs):
    inv = cap.matrix_world.inverted()
    moved = 0
    max_disp = 0.0
    for v, p in zip(cap.data.vertices, r9.world_points(cap)):
        xr = (p.x - hc.x) / max(hs.x, 1e-8)
        yr = (p.y - hc.y) / max(hs.y, 1e-8)
        zr = (p.z - hc.z) / max(hs.z, 1e-8)
        if zr < 0.14 or abs(xr) > 0.56 or abs(yr) > 0.60:
            continue
        radial = min(1.0, math.sqrt((xr / 0.56) ** 2 + (yr / 0.60) ** 2))
        fade = max(0.0, 1.0 - radial ** 2.1)

        # Broad diagonal sheets + a shallow off-center part. This breaks the round helmet highlight
        # while keeping the overall head silhouette and all authored donor-hair pieces unchanged.
        phase = (xr * 4.2 + yr * 1.65) * math.pi
        ridge = hs.z * 0.0058 * math.sin(phase) * fade
        side_part = hs.z * 0.0040 * math.exp(-(((xr + 0.13) / 0.15) ** 2 + ((yr + 0.01) / 0.28) ** 2))
        center_groove = -hs.z * 0.0035 * math.exp(-(((xr - 0.01) / 0.12) ** 2 + ((yr + 0.04) / 0.24) ** 2))
        dz = ridge + side_part + center_groove

        q = Vector((hc.x + (p.x - hc.x) * (1.0 + 0.0018 * fade),
                    hc.y + (p.y - hc.y) * (1.0 + 0.0018 * fade),
                    p.z + dz))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved += 1

    cap.data.update()
    if moved < 100 or max_disp > hs.z * 0.014:
        raise RuntimeError(f"invalid final cap relief moved={moved} max={max_disp}")
    return moved, max_disp


def final_material(cap, colors):
    name = "HairCrownR9FinalColor"
    if name in cap.data.color_attributes:
        cap.data.color_attributes.remove(cap.data.color_attributes[name])
    attr = cap.data.color_attributes.new(name=name, type="FLOAT_COLOR", domain="CORNER")

    # Darken the donor-derived crown tone while retaining the same hue and local variation.
    # The previous white/kappa read came from the crown's upward-facing diffuse highlight.
    for poly in cap.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = cap.data.loops[loop_idx].vertex_index
            c = colors[vi]
            tuned = Vector((c.x * 0.52, c.y * 0.56, c.z * 0.66))
            attr.data[loop_idx].color = (tuned.x, tuned.y, tuned.z, 1.0)

    mat = bpy.data.materials.new("HairPremiumV185CrownFinal")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    vcol = nodes.new("ShaderNodeVertexColor")
    vcol.layer_name = name
    links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.74
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.08
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    cap.data.materials.clear()
    cap.data.materials.append(mat)
    for poly in cap.data.polygons:
        poly.material_index = 0
        poly.use_smooth = True
    return mat.name


r9.add_relief = final_relief
r9.apply_color_material = final_material

if __name__ == "__main__":
    r9.main()
