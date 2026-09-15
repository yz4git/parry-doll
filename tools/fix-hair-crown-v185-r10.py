"""v18.5 r10 final crown-only fix.

Uses r9's hard face/main-hair locks and cap topology checks, but replaces unsupported exported
vertex-color shading with a packed image texture that survives GLB export. Only the existing scalp
cap geometry/material changes; face, bangs, side hair and ponytail remain unchanged.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

BASE = Path(__file__).with_name("fix-hair-crown-v185-r9.py")
spec = importlib.util.spec_from_file_location("hair_crown_r9_base", BASE)
r9 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(r9)


def r10_relief(cap, hc, hs):
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
        phase = (xr * 4.15 + yr * 1.55) * math.pi
        ridge = hs.z * 0.0054 * math.sin(phase) * fade
        side_part = hs.z * 0.0038 * math.exp(-(((xr + 0.13) / 0.15) ** 2 + ((yr + 0.01) / 0.28) ** 2))
        center_groove = -hs.z * 0.0032 * math.exp(-(((xr - 0.01) / 0.12) ** 2 + ((yr + 0.04) / 0.24) ** 2))
        q = Vector((hc.x + (p.x - hc.x) * (1.0 + 0.0017 * fade),
                    hc.y + (p.y - hc.y) * (1.0 + 0.0017 * fade),
                    p.z + ridge + side_part + center_groove))
        max_disp = max(max_disp, (q - p).length)
        v.co = inv @ q
        moved += 1
    cap.data.update()
    if moved < 100 or max_disp > hs.z * 0.014:
        raise RuntimeError(f"invalid r10 cap relief moved={moved} max={max_disp}")
    return moved, max_disp


def make_texture(size=256):
    img = bpy.data.images.new("HairCrownR10Texture", width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    for py in range(size):
        v = py / (size - 1)
        ny = (v - 0.5) * 2.0
        for px in range(size):
            u = px / (size - 1)
            nx = (u - 0.5) * 2.0
            radial = min(1.0, math.sqrt(nx * nx + ny * ny))

            # Diagonal locks flow toward the ponytail root instead of radiating from the crown.
            flow = 0.5 + 0.5 * math.sin((nx * 4.1 + ny * 1.55) * math.pi + radial * 0.6)
            broad = 0.5 + 0.5 * math.sin((nx * 1.6 - ny * 0.9) * math.pi + 0.7)
            part = math.exp(-(((nx + 0.24) / 0.10) ** 2 + ((ny + 0.05) / 0.70) ** 2))
            edge = 1.0 - 0.10 * radial
            value = (0.86 + 0.09 * flow + 0.05 * broad - 0.10 * part) * edge

            # Medium blue-violet root tone. Deliberately darker than the upward-facing pale bangs
            # so direct key light cannot turn the top into a white scalp/helmet patch.
            r = max(0.060, min(0.19, 0.115 * value + 0.018))
            g = max(0.105, min(0.31, 0.205 * value + 0.028))
            b = max(0.34, min(0.76, 0.590 * value + 0.055))
            i = (py * size + px) * 4
            pixels[i:i+4] = (r, g, b, 1.0)
    img.pixels = pixels
    img.pack()
    return img


def r10_material(cap, _colors):
    pts = r9.world_points(cap)
    lo, hi, _center, size = r9.bounds(pts)
    uv = cap.data.uv_layers.get("CrownR10UV") or cap.data.uv_layers.new(name="CrownR10UV")
    mw = cap.matrix_world
    for poly in cap.data.polygons:
        for loop_idx in poly.loop_indices:
            vi = cap.data.loops[loop_idx].vertex_index
            p = mw @ cap.data.vertices[vi].co
            u = (p.x - lo.x) / max(size.x, 1e-8)
            v = (p.y - lo.y) / max(size.y, 1e-8)
            uv.data[loop_idx].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))

    mat = bpy.data.materials.new("HairPremiumV185CrownR10")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = make_texture()
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.66
    bsdf.inputs["Metallic"].default_value = 0.0
    spec = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if spec is not None:
        spec.default_value = 0.11
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    cap.data.materials.clear()
    cap.data.materials.append(mat)
    for poly in cap.data.polygons:
        poly.material_index = 0
        poly.use_smooth = True
    return mat.name


r9.add_relief = r10_relief
r9.apply_color_material = r10_material

if __name__ == "__main__":
    r9.main()
