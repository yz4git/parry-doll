#!/usr/bin/env python3
"""Add eye-only textures to the exact v17.0 PARRY DOLL GLB without changing shape.

This is intentionally a GLB chunk/material patcher, not a Blender modelling pass.
It does not import, regenerate, sculpt, transform, delete or add any mesh geometry.
The workflow first restores the shipping GLB from v17.0 commit
ff135e507f5d44cc4bce6d49915aa4719105dd29, then this script:

- keeps every existing POSITION/NORMAL/index byte untouched,
- appends only texture image bytes and, where required, TEXCOORD_0 accessors,
- changes only eye-material texture bindings / base-colour factors,
- keeps nodes, transforms, mesh positions and topology unchanged.

The added textures are generated deterministically with Python stdlib so no extra binary source
asset is required in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import zlib
from copy import deepcopy

MAGIC = b"glTF"
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
FLOAT = 5126
ARRAY_BUFFER = 34962

V170_COMMIT = "ff135e507f5d44cc4bce6d49915aa4719105dd29"
TARGET_MATERIALS = {
    "Sclera": "sclera",
    "Iris": "iris",
    "Iris Inner": "iris",
    "Iris Ray Warm": "iris",
    "Iris Ray Dark": "iris",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest")
    return p.parse_args()


def parse_glb(path):
    data = open(path, "rb").read()
    if len(data) < 20 or data[:4] != MAGIC:
        raise RuntimeError("not a GLB file")
    magic, version, declared = struct.unpack_from("<4sII", data, 0)
    if version != 2 or declared != len(data):
        raise RuntimeError(f"unexpected GLB header version={version} declared={declared} actual={len(data)}")
    pos = 12
    js = None
    binary = b""
    while pos < len(data):
        length, ctype = struct.unpack_from("<II", data, pos)
        pos += 8
        payload = data[pos:pos + length]
        pos += length
        if ctype == JSON_CHUNK:
            js = json.loads(payload.rstrip(b" \t\r\n\x00").decode("utf-8"))
        elif ctype == BIN_CHUNK:
            binary = payload
    if js is None:
        raise RuntimeError("GLB JSON chunk missing")
    return js, binary, data


def pad4(data: bytes, byte=b"\x00") -> bytes:
    return data + byte * ((4 - (len(data) % 4)) % 4)


def write_glb(path, doc, binary):
    doc["buffers"][0]["byteLength"] = len(binary)
    js = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    js = pad4(js, b" ")
    binary = pad4(binary, b"\x00")
    total = 12 + 8 + len(js) + (8 + len(binary) if binary else 0)
    out = bytearray(struct.pack("<4sII", MAGIC, 2, total))
    out += struct.pack("<II", len(js), JSON_CHUNK) + js
    if binary:
        out += struct.pack("<II", len(binary), BIN_CHUNK) + binary
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, "wb").write(out)


def png_rgba(width, height, pixel_fn):
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0
        for x in range(width):
            raw += bytes(max(0, min(255, int(v))) for v in pixel_fn(x, y))

    def chunk(kind, payload):
        body = kind + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def build_iris_png(size=256):
    c = (size - 1) * 0.5
    inv = 1.0 / c

    def px(x, y):
        dx = (x - c) * inv
        dy = (y - c) * inv
        r = math.sqrt(dx * dx + dy * dy)
        a = math.atan2(dy, dx)
        # Adult realistic-anime grey-brown iris: quiet outer limbal ring, fine radial fibres,
        # subtle warm inner ring. Separate existing pupil geometry remains untouched.
        fibre = 0.5 + 0.5 * math.sin(a * 37.0 + r * 29.0 + 0.22 * math.sin(a * 9.0))
        fine = 0.5 + 0.5 * math.sin(a * 71.0 - r * 18.0)
        ring = 0.5 + 0.5 * math.sin(r * 68.0)
        base = 0.58 + 0.18 * fibre + 0.07 * fine + 0.04 * ring
        inner = math.exp(-((r - 0.34) / 0.18) ** 2)
        edge = max(0.0, min(1.0, (r - 0.77) / 0.20))
        pupil_falloff = max(0.0, min(1.0, r / 0.22))
        rr = (112 * base + 30 * inner) * pupil_falloff
        gg = (96 * base + 22 * inner) * pupil_falloff
        bb = (88 * base + 18 * inner) * pupil_falloff
        dark = 1.0 - 0.68 * edge
        rr *= dark; gg *= dark; bb *= dark
        # Keep the texture defined outside the disc because the mesh itself clips the final shape.
        if r > 1.0:
            rr, gg, bb = 30, 25, 24
        return rr, gg, bb, 255

    return png_rgba(size, size, px)


def build_sclera_png(size=256):
    def px(x, y):
        u = x / max(1, size - 1)
        v = y / max(1, size - 1)
        n = math.sin(u * 31.0 + math.sin(v * 13.0)) * math.sin(v * 27.0 + 0.4 * math.sin(u * 19.0))
        edge = abs(v - 0.5) * 2.0
        # Extremely restrained warm-grey sclera variation. No painted iris/pupil; geometry remains v17.0.
        vein1 = math.exp(-((v - (0.18 + 0.035 * math.sin(u * 20.0))) / 0.010) ** 2) * max(0.0, 0.7 - abs(u - 0.5))
        vein2 = math.exp(-((v - (0.79 + 0.025 * math.sin(u * 27.0 + 1.7))) / 0.009) ** 2) * max(0.0, 0.6 - abs(u - 0.5))
        veins = min(1.0, vein1 + vein2) * 0.16
        base = 238 + 4 * n - 7 * edge
        r = base + 6 - 8 * veins
        g = base + 2 - 28 * veins
        b = base - 2 - 24 * veins
        return r, g, b, 255

    return png_rgba(size, size, px)


def comp_info(component_type):
    if component_type == 5126:
        return "f", 4
    if component_type == 5125:
        return "I", 4
    if component_type == 5123:
        return "H", 2
    if component_type == 5121:
        return "B", 1
    raise RuntimeError(f"unsupported accessor component type {component_type}")


def type_components(type_name):
    return {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}.get(type_name) or (_ for _ in ()).throw(RuntimeError(f"unsupported accessor type {type_name}"))


def read_accessor(doc, binary, accessor_index):
    acc = doc["accessors"][accessor_index]
    if "bufferView" not in acc:
        raise RuntimeError("sparse/no-buffer accessor not supported for eye UV projection")
    bv = doc["bufferViews"][acc["bufferView"]]
    fmt, csize = comp_info(acc["componentType"])
    ncomp = type_components(acc["type"])
    elem_size = csize * ncomp
    stride = bv.get("byteStride", elem_size)
    offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    vals = []
    for i in range(acc["count"]):
        vals.append(struct.unpack_from("<" + fmt * ncomp, binary, offset + i * stride))
    return vals


def append_buffer_view(doc, binary, payload, target=None):
    payload = bytes(payload)
    padding = (4 - (len(binary) % 4)) % 4
    if padding:
        binary += b"\x00" * padding
    offset = len(binary)
    binary += payload
    bv = {"buffer": 0, "byteOffset": offset, "byteLength": len(payload)}
    if target is not None:
        bv["target"] = target
    doc.setdefault("bufferViews", []).append(bv)
    return len(doc["bufferViews"]) - 1, binary


def add_image_texture(doc, binary, name, png_bytes):
    bv_idx, binary = append_buffer_view(doc, binary, png_bytes)
    doc.setdefault("images", []).append({"name": name, "bufferView": bv_idx, "mimeType": "image/png"})
    image_idx = len(doc["images"]) - 1
    samplers = doc.setdefault("samplers", [])
    sampler_idx = None
    # Reuse a linear/clamped sampler when possible.
    for i, s in enumerate(samplers):
        if s.get("magFilter", 9729) == 9729 and s.get("minFilter", 9729) in (9729, 9987) and s.get("wrapS", 33071) == 33071 and s.get("wrapT", 33071) == 33071:
            sampler_idx = i; break
    if sampler_idx is None:
        samplers.append({"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071})
        sampler_idx = len(samplers) - 1
    doc.setdefault("textures", []).append({"name": name, "sampler": sampler_idx, "source": image_idx})
    return len(doc["textures"]) - 1, binary


def create_planar_uv_accessor(doc, binary, position_accessor_index):
    pos = read_accessor(doc, binary, position_accessor_index)
    if not pos or len(pos[0]) != 3:
        raise RuntimeError("eye POSITION accessor is not VEC3")
    mins = [min(p[a] for p in pos) for a in range(3)]
    maxs = [max(p[a] for p in pos) for a in range(3)]
    ranges = [maxs[a] - mins[a] for a in range(3)]
    axes = sorted(range(3), key=lambda a: ranges[a], reverse=True)[:2]
    if ranges[axes[1]] < 1e-8:
        axes = [0, 1]
    uvs = []
    for p in pos:
        uv = []
        for a in axes:
            span = max(ranges[a], 1e-8)
            uv.append(max(0.0, min(1.0, (p[a] - mins[a]) / span)))
        # Keep image orientation consistent with the front-facing portrait.
        uvs.append((uv[0], 1.0 - uv[1]))
    payload = b"".join(struct.pack("<ff", u, v) for u, v in uvs)
    bv_idx, binary = append_buffer_view(doc, binary, payload, ARRAY_BUFFER)
    doc.setdefault("accessors", []).append({
        "bufferView": bv_idx,
        "byteOffset": 0,
        "componentType": FLOAT,
        "count": len(uvs),
        "type": "VEC2",
        "min": [0.0, 0.0],
        "max": [1.0, 1.0],
        "name": f"EyeTextureUV_from_POSITION_{position_accessor_index}",
    })
    return len(doc["accessors"]) - 1, binary


def position_fingerprint(doc, binary):
    h = hashlib.sha256()
    seen = set()
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            idx = prim.get("attributes", {}).get("POSITION")
            if idx is None or idx in seen:
                continue
            seen.add(idx)
            vals = read_accessor(doc, binary, idx)
            h.update(struct.pack("<I", idx))
            for p in vals:
                h.update(struct.pack("<" + "f" * len(p), *[float(x) for x in p]))
    return h.hexdigest(), len(seen)


def main():
    a = parse_args()
    doc, binary, original_bytes = parse_glb(a.input)
    original_doc = deepcopy(doc)
    original_binary = bytes(binary)
    pos_hash_before, position_accessors = position_fingerprint(doc, binary)
    original_accessors = len(doc.get("accessors", []))
    original_buffer_views = len(doc.get("bufferViews", []))

    materials = doc.get("materials", [])
    by_name = {m.get("name", ""): i for i, m in enumerate(materials)}
    missing = [name for name in TARGET_MATERIALS if name not in by_name]
    if missing:
        raise RuntimeError("v17.0 eye materials missing: " + ", ".join(missing))

    iris_tex, binary = add_image_texture(doc, binary, "PARRY_DOLL_IrisTexture_v170", build_iris_png())
    sclera_tex, binary = add_image_texture(doc, binary, "PARRY_DOLL_ScleraTexture_v170", build_sclera_png())
    texture_by_kind = {"iris": iris_tex, "sclera": sclera_tex}

    target_material_indices = set()
    patched_materials = []
    for name, kind in TARGET_MATERIALS.items():
        idx = by_name[name]
        target_material_indices.add(idx)
        mat = materials[idx]
        pbr = mat.setdefault("pbrMetallicRoughness", {})
        pbr["baseColorTexture"] = {"index": texture_by_kind[kind], "texCoord": 0}
        # The texture now owns eye colour. This is a material/texture mapping change only; geometry stays exact v17.0.
        pbr["baseColorFactor"] = [1.0, 1.0, 1.0, 1.0]
        mat.setdefault("extras", {})["parryDollEyeTextureRevision"] = "v17.0-eye-texture-only"
        patched_materials.append(name)

    uv_by_position = {}
    textured_primitives = 0
    added_uv_primitives = 0
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if prim.get("material") not in target_material_indices:
                continue
            textured_primitives += 1
            attrs = prim.setdefault("attributes", {})
            if "TEXCOORD_0" in attrs:
                continue
            pos_idx = attrs.get("POSITION")
            if pos_idx is None:
                raise RuntimeError("eye primitive has no POSITION attribute")
            if pos_idx not in uv_by_position:
                uv_idx, binary = create_planar_uv_accessor(doc, binary, pos_idx)
                uv_by_position[pos_idx] = uv_idx
            attrs["TEXCOORD_0"] = uv_by_position[pos_idx]
            added_uv_primitives += 1

    if textured_primitives < 2:
        raise RuntimeError(f"too few textured eye primitives: {textured_primitives}")

    # Shape invariants: nodes/transforms, POSITION accessors, indices and all original binary bytes are untouched.
    if doc.get("nodes") != original_doc.get("nodes"):
        raise RuntimeError("node/transform data changed unexpectedly")
    if binary[:len(original_binary)] != original_binary:
        raise RuntimeError("original GLB BIN prefix changed; geometry-preservation invariant failed")
    for i in range(original_accessors):
        if doc["accessors"][i] != original_doc["accessors"][i]:
            raise RuntimeError(f"existing accessor {i} changed")
    for i in range(original_buffer_views):
        if doc["bufferViews"][i] != original_doc["bufferViews"][i]:
            raise RuntimeError(f"existing bufferView {i} changed")
    for mi, (before_mesh, after_mesh) in enumerate(zip(original_doc.get("meshes", []), doc.get("meshes", []))):
        if before_mesh.get("name") != after_mesh.get("name") or len(before_mesh.get("primitives", [])) != len(after_mesh.get("primitives", [])):
            raise RuntimeError(f"mesh structure changed at {mi}")
        for pi, (bp, ap) in enumerate(zip(before_mesh.get("primitives", []), after_mesh.get("primitives", []))):
            for key in ("indices", "mode", "material", "targets"):
                if bp.get(key) != ap.get(key):
                    raise RuntimeError(f"mesh primitive topology/material index changed at {mi}/{pi}/{key}")
            for semantic, accessor_idx in bp.get("attributes", {}).items():
                if semantic == "TEXCOORD_0" and ap.get("attributes", {}).get(semantic) != accessor_idx:
                    raise RuntimeError(f"existing UV accessor changed at {mi}/{pi}")
                if semantic != "TEXCOORD_0" and ap.get("attributes", {}).get(semantic) != accessor_idx:
                    raise RuntimeError(f"geometry attribute {semantic} changed at {mi}/{pi}")

    pos_hash_after, _ = position_fingerprint(doc, binary)
    if pos_hash_after != pos_hash_before:
        raise RuntimeError("POSITION fingerprint changed")

    doc.setdefault("asset", {}).setdefault("extras", {})["parryDollModelPolicy"] = "exact-v17.0-shape-eye-texture-only"
    doc["asset"]["extras"]["v170SourceCommit"] = V170_COMMIT
    doc["asset"]["extras"]["positionFingerprint"] = pos_hash_before
    write_glb(a.output, doc, binary)

    manifest = {
        "revision": "v17.0-eye-texture-only",
        "source_commit": V170_COMMIT,
        "geometry_changed": False,
        "position_fingerprint_before": pos_hash_before,
        "position_fingerprint_after": pos_hash_after,
        "position_accessors": position_accessors,
        "original_glb_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "patched_materials": patched_materials,
        "textured_primitives": textured_primitives,
        "added_uv_primitives": added_uv_primitives,
        "existing_accessors_preserved": original_accessors,
        "existing_buffer_views_preserved": original_buffer_views,
        "textures": ["PARRY_DOLL_IrisTexture_v170", "PARRY_DOLL_ScleraTexture_v170"],
        "output_bytes": os.path.getsize(a.output),
    }
    if a.manifest:
        os.makedirs(os.path.dirname(os.path.abspath(a.manifest)), exist_ok=True)
        open(a.manifest, "w", encoding="utf-8").write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("V170_EYE_TEXTURE_RESULT", json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
