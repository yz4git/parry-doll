#!/usr/bin/env python3
"""Paint iris/pupil detail onto the visible v17.0 eyeball surface without changing geometry.

This is a second, material-only pass after add-eye-textures-v170.py.  It identifies the two
high-density v17.0 sclera globes, derives the forward-looking UV coordinate from their existing
POSITION/TEXCOORD_0 data, embeds one deterministic grey-brown eyeball texture, clones the Sclera
material, and assigns that material only to the two eyeball globe primitives.

No POSITION/NORMAL/index/accessor byte that existed before this pass is modified.  No node,
transform, mesh vertex, face or object is added/deleted/transformed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATCHER = os.path.join(HERE, "add-eye-textures-v170.py")


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest")
    return p.parse_args()


def circular_mean(values):
    if not values:
        return 0.5
    sx = sum(math.cos(2.0 * math.pi * v) for v in values)
    sy = sum(math.sin(2.0 * math.pi * v) for v in values)
    if abs(sx) + abs(sy) < 1e-9:
        return values[0] % 1.0
    return (math.atan2(sy, sx) / (2.0 * math.pi)) % 1.0


def front_uv(helper, doc, binary, prim):
    pos = helper["read_accessor"](doc, binary, prim["attributes"]["POSITION"])
    uv = helper["read_accessor"](doc, binary, prim["attributes"]["TEXCOORD_0"])
    if len(pos) != len(uv):
        raise RuntimeError("POSITION/UV count mismatch on eyeball globe")
    xs = [p[0] for p in pos]; ys = [p[1] for p in pos]; zs = [p[2] for p in pos]
    cx = (min(xs) + max(xs)) * 0.5
    cz = (min(zs) + max(zs)) * 0.5
    ry = max(ys) - min(ys)
    rx = max(xs) - min(xs)
    rz = max(zs) - min(zs)
    # v17.0 eyes come from an unrotated Blender UV sphere. The character faces Blender -Y.
    # Use a small cap around that local -Y direction and circular-average U to survive the seam.
    candidates = []
    for p, t in zip(pos, uv):
        if p[1] <= min(ys) + ry * 0.055 and abs(p[0] - cx) <= rx * 0.20 and abs(p[2] - cz) <= rz * 0.20:
            candidates.append((float(t[0]), float(t[1])))
    if not candidates:
        idx = min(range(len(pos)), key=lambda i: pos[i][1])
        candidates = [(float(uv[idx][0]), float(uv[idx][1]))]
    return circular_mean([u for u, _ in candidates]), sum(v for _, v in candidates) / len(candidates), len(candidates)


def build_eyeball_png(helper, center_u, center_v, size=512):
    # Equirectangular sphere UV: one physical angular radius occupies ~2x more V than U.
    iris_ru = 0.075
    iris_rv = 0.150

    def pixel(x, y):
        u = x / max(1, size - 1)
        v = y / max(1, size - 1)
        du0 = abs(u - center_u)
        du = min(du0, 1.0 - du0)
        dv = v - center_v
        r = math.sqrt((du / iris_ru) ** 2 + (dv / iris_rv) ** 2)

        # Warm off-white sclera with extremely restrained vein detail.
        n = math.sin(u * 39.0 + math.sin(v * 17.0)) * math.sin(v * 29.0 + math.sin(u * 11.0))
        edge_tint = min(1.0, abs(dv) / 0.45)
        sr = 239 + 3.0 * n - 4.0 * edge_tint
        sg = 235 + 3.0 * n - 5.0 * edge_tint
        sb = 231 + 2.0 * n - 5.0 * edge_tint
        # Fine peripheral vessels, deliberately faint so the face still reads as clean game art.
        vein = 0.0
        for phase, amp, freq in ((0.4, 0.9, 31.0), (2.1, 0.7, 43.0)):
            curve = center_v + (0.22 + 0.025 * math.sin(u * freq + phase)) * (1 if phase < 1 else -1)
            vein += math.exp(-((v - curve) / 0.0045) ** 2) * max(0.0, 0.55 - du)
        sr -= 4.0 * vein; sg -= 22.0 * vein; sb -= 18.0 * vein

        if r <= 1.0:
            angle = math.atan2(dv / iris_rv, du / iris_ru if du > 1e-9 else 1e-9)
            fibre = 0.5 + 0.5 * math.sin(angle * 43.0 + r * 31.0 + 0.25 * math.sin(angle * 9.0))
            fine = 0.5 + 0.5 * math.sin(angle * 83.0 - r * 19.0)
            ring = 0.5 + 0.5 * math.sin(r * 72.0)
            brightness = 0.48 + 0.20 * fibre + 0.07 * fine + 0.04 * ring
            inner = math.exp(-((r - 0.36) / 0.16) ** 2)
            limbal = max(0.0, min(1.0, (r - 0.80) / 0.18))
            rr = (116 * brightness + 25 * inner) * (1.0 - 0.72 * limbal)
            gg = (101 * brightness + 19 * inner) * (1.0 - 0.72 * limbal)
            bb = (94 * brightness + 17 * inner) * (1.0 - 0.72 * limbal)
            if r < 0.27:
                q = max(0.0, min(1.0, r / 0.27))
                rr = 7 + rr * 0.16 * q
                gg = 7 + gg * 0.14 * q
                bb = 8 + bb * 0.14 * q
            # Small soft catchlight embedded in texture; existing geometry highlights remain untouched.
            hu = (du / iris_ru + 0.34)
            hv = (dv / iris_rv + 0.34)
            h = math.exp(-(hu * hu + hv * hv) / 0.035)
            rr = rr * (1 - 0.78 * h) + 246 * 0.78 * h
            gg = gg * (1 - 0.78 * h) + 244 * 0.78 * h
            bb = bb * (1 - 0.78 * h) + 241 * 0.78 * h
            return rr, gg, bb, 255
        return sr, sg, sb, 255

    return helper["png_rgba"](size, size, pixel)


def main():
    a = args()
    h = runpy.run_path(BASE_PATCHER, run_name="__v170_eye_texture_helpers_surface__")
    doc, binary, original_bytes = h["parse_glb"](a.input)
    original_doc = copy.deepcopy(doc)
    original_binary = bytes(binary)
    pos_before, pos_count = h["position_fingerprint"](doc, binary)

    mats = doc.get("materials", [])
    sclera_idx = next((i for i, m in enumerate(mats) if m.get("name") == "Sclera"), None)
    if sclera_idx is None:
        raise RuntimeError("Sclera material missing")

    globes = []
    for mi, mesh in enumerate(doc.get("meshes", [])):
        name = mesh.get("name", "")
        if "EyeSclera" not in name and "ScleraGlobe" not in name:
            continue
        for pi, prim in enumerate(mesh.get("primitives", [])):
            if prim.get("material") != sclera_idx:
                continue
            attrs = prim.get("attributes", {})
            if "POSITION" not in attrs or "TEXCOORD_0" not in attrs:
                continue
            pos = h["read_accessor"](doc, binary, attrs["POSITION"])
            if len(pos) < 300:
                continue
            globes.append((mi, pi, prim, len(pos), name))
    if len(globes) != 2:
        # Fallback: exactly two large Sclera-material primitives, independent of exporter naming.
        globes = []
        for mi, mesh in enumerate(doc.get("meshes", [])):
            for pi, prim in enumerate(mesh.get("primitives", [])):
                if prim.get("material") != sclera_idx:
                    continue
                attrs = prim.get("attributes", {})
                if "POSITION" not in attrs or "TEXCOORD_0" not in attrs:
                    continue
                pos = h["read_accessor"](doc, binary, attrs["POSITION"])
                if len(pos) >= 900:
                    globes.append((mi, pi, prim, len(pos), mesh.get("name", "")))
    if len(globes) != 2:
        raise RuntimeError(f"expected exactly two v17.0 eyeball globes, found {len(globes)}")

    centers = [front_uv(h, doc, binary, prim) for _, _, prim, _, _ in globes]
    cu = circular_mean([x[0] for x in centers])
    cv = sum(x[1] for x in centers) / len(centers)
    png = build_eyeball_png(h, cu, cv)
    tex_idx, binary = h["add_image_texture"](doc, binary, "PARRY_DOLL_EyeballSurfaceTexture_v170", png)

    new_mat = copy.deepcopy(mats[sclera_idx])
    new_mat["name"] = "Eyeball Surface v17.0"
    pbr = new_mat.setdefault("pbrMetallicRoughness", {})
    pbr["baseColorFactor"] = [1.0, 1.0, 1.0, 1.0]
    pbr["baseColorTexture"] = {"index": tex_idx, "texCoord": 0}
    new_mat.setdefault("extras", {})["parryDollEyeTextureRevision"] = "v17.0-eye-texture-only-r2"
    mats.append(new_mat)
    new_mat_idx = len(mats) - 1

    changed_primitives = []
    for mi, pi, prim, count, name in globes:
        prim["material"] = new_mat_idx
        changed_primitives.append({"mesh": name, "mesh_index": mi, "primitive": pi, "vertices": count})

    # Hard shape invariants.
    if doc.get("nodes") != original_doc.get("nodes"):
        raise RuntimeError("node hierarchy/transform changed")
    if binary[:len(original_binary)] != original_binary:
        raise RuntimeError("pre-existing BIN bytes changed")
    pos_after, _ = h["position_fingerprint"](doc, binary)
    if pos_after != pos_before:
        raise RuntimeError("POSITION fingerprint changed")
    if len(doc.get("meshes", [])) != len(original_doc.get("meshes", [])):
        raise RuntimeError("mesh count changed")
    for mi, (before, after) in enumerate(zip(original_doc.get("meshes", []), doc.get("meshes", []))):
        if before.get("name") != after.get("name") or len(before.get("primitives", [])) != len(after.get("primitives", [])):
            raise RuntimeError(f"mesh structure changed at {mi}")
        for pi, (bp, ap) in enumerate(zip(before.get("primitives", []), after.get("primitives", []))):
            if bp.get("indices") != ap.get("indices") or bp.get("attributes") != ap.get("attributes") or bp.get("mode") != ap.get("mode"):
                raise RuntimeError(f"geometry/topology changed at {mi}/{pi}")
            allowed = any(mi == g[0] and pi == g[1] for g in globes)
            if not allowed and bp.get("material") != ap.get("material"):
                raise RuntimeError(f"non-eyeball material changed at {mi}/{pi}")

    doc.setdefault("asset", {}).setdefault("extras", {})["parryDollModelPolicy"] = "exact-v17.0-shape-eyeball-texture-only"
    doc["asset"]["extras"]["positionFingerprint"] = pos_before
    doc["asset"]["extras"]["eyeballFrontUV"] = [round(cu, 7), round(cv, 7)]
    h["write_glb"](a.output, doc, binary)

    result = {
        "revision": "v17.0-eye-texture-only-r2",
        "geometry_changed": False,
        "position_fingerprint_before": pos_before,
        "position_fingerprint_after": pos_after,
        "position_accessors": pos_count,
        "eyeball_front_uv": [cu, cv],
        "per_globe_front_uv": centers,
        "changed_material_primitives": changed_primitives,
        "new_material": "Eyeball Surface v17.0",
        "new_texture": "PARRY_DOLL_EyeballSurfaceTexture_v170",
        "input_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "output_bytes": os.path.getsize(a.output),
    }
    if a.manifest:
        open(a.manifest, "w", encoding="utf-8").write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("V170_EYEBALL_SURFACE_RESULT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
