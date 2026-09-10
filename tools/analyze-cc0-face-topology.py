#!/usr/bin/env python3
"""Analyze a pinned CC0 MakeHuman/MPFB hm08 base mesh and extract a reusable face topology template.

The source mesh is not copied wholesale into PARRY DOLL. We keep provenance, topology statistics,
and a compact normalized face patch built only from the facial target regions plus two adjacency rings.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path

BODY_VERTEX_LIMIT = 13380  # documented hm08 body range 0..13379; helpers follow.
CORE_REGIONS = ("cheek", "chin", "eyebrows", "eyes", "forehead", "mouth", "nose")
EXTENDED_REGIONS = CORE_REGIONS + ("head",)
SOURCE_COMMIT = "03264788d967bcd33844be70e35db05b231aa017"
SOURCE_REPO = "https://github.com/nirholas/three.ws"
SOURCE_PATH = "avatar-sources/anny"


def load_obj(path: Path):
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                _, xs, ys, zs, *_ = line.split()
                verts.append((float(xs), float(ys), float(zs)))
            elif line.startswith("f "):
                ids = []
                for token in line.split()[1:]:
                    raw = token.split("/", 1)[0]
                    if not raw:
                        continue
                    idx = int(raw)
                    if idx < 0:
                        idx = len(verts) + idx
                    else:
                        idx -= 1
                    ids.append(idx)
                if len(ids) >= 3:
                    faces.append(tuple(ids))
    return verts, faces


def iter_target_lines(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    mode = "rt"
    with opener(path, mode, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if not parts:
                continue
            try:
                yield int(parts[0])
            except ValueError:
                continue


def target_region_vertices(targets_root: Path, region: str) -> tuple[set[int], int]:
    root = targets_root / region
    ids: set[int] = set()
    files = 0
    if not root.exists():
        return ids, files
    for p in sorted(root.rglob("*.target")) + sorted(root.rglob("*.target.gz")):
        files += 1
        ids.update(i for i in iter_target_lines(p) if 0 <= i < BODY_VERTEX_LIMIT)
    return ids, files


def build_adjacency(faces: list[tuple[int, ...]], limit: int):
    adj: dict[int, set[int]] = defaultdict(set)
    body_faces: list[tuple[int, ...]] = []
    for face in faces:
        if not face or any(i < 0 or i >= limit for i in face):
            continue
        body_faces.append(face)
        for a, b in zip(face, face[1:] + face[:1]):
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
    return adj, body_faces


def expand_vertices(seed: set[int], adj: dict[int, set[int]], rings: int) -> set[int]:
    out = set(seed)
    frontier = set(seed)
    for _ in range(rings):
        nxt = set()
        for v in frontier:
            nxt.update(adj.get(v, ()))
        nxt -= out
        out.update(nxt)
        frontier = nxt
    return out


def connected_components(nodes: set[int], adj: dict[int, set[int]]):
    unseen = set(nodes)
    comps = []
    while unseen:
        start = unseen.pop()
        comp = {start}
        q = [start]
        while q:
            v = q.pop()
            for n in adj.get(v, ()):
                if n in unseen:
                    unseen.remove(n)
                    comp.add(n)
                    q.append(n)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def bbox(verts, ids):
    pts = [verts[i] for i in ids]
    return {
        "min": [min(p[k] for p in pts) for k in range(3)],
        "max": [max(p[k] for p in pts) for k in range(3)],
    }


def centroid(verts, ids):
    pts = [verts[i] for i in ids]
    n = max(len(pts), 1)
    return [sum(p[k] for p in pts) / n for k in range(3)]


def normalized_region_box(verts, ids, face_box):
    if not ids:
        return None
    b = bbox(verts, ids)
    fmin, fmax = face_box["min"], face_box["max"]
    span = [max(fmax[k] - fmin[k], 1e-9) for k in range(3)]
    return {
        "min": [round((b["min"][k] - fmin[k]) / span[k], 6) for k in range(3)],
        "max": [round((b["max"][k] - fmin[k]) / span[k], 6) for k in range(3)],
        "centroid": [round((centroid(verts, ids)[k] - fmin[k]) / span[k], 6) for k in range(3)],
    }


def profile_samples(verts, ids, bins=24):
    box = bbox(verts, ids)
    xmin, ymin, zmin = box["min"]
    xmax, ymax, zmax = box["max"]
    width = max(xmax - xmin, 1e-9)
    height = max(ymax - ymin, 1e-9)
    depth = max(zmax - zmin, 1e-9)
    cx = (xmin + xmax) * 0.5
    band = width * 0.075
    out = []
    for bi in range(bins):
        y0 = ymin + height * bi / bins
        y1 = ymin + height * (bi + 1) / bins
        cand = [verts[i] for i in ids if y0 <= verts[i][1] <= y1 and abs(verts[i][0] - cx) <= band]
        if not cand:
            continue
        p = max(cand, key=lambda q: q[2])
        out.append({
            "y": round((p[1] - ymin) / height, 6),
            "front_z": round((p[2] - zmin) / depth, 6),
            "x_from_center": round((p[0] - cx) / width, 6),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True, type=Path)
    ap.add_argument("--stats", default="tools/cc0-face-topology-stats.json", type=Path)
    ap.add_argument("--template", default="tools/cc0-face-topology-template-v1.json", type=Path)
    ap.add_argument("--report", default="docs/CC0_FACE_TOPOLOGY_ANALYSIS.md", type=Path)
    args = ap.parse_args()

    source = args.source_root
    obj = source / "3dobjs" / "base.obj"
    targets = source / "targets"
    readme = (source / "README.md").read_text(encoding="utf-8", errors="replace")
    license_text = (source / "LICENSE.md").read_text(encoding="utf-8", errors="replace")
    if "CC0" not in readme or "CC0" not in license_text:
        raise SystemExit("CC0 provenance check failed")

    verts, faces = load_obj(obj)
    if len(verts) < BODY_VERTEX_LIMIT:
        raise SystemExit(f"hm08 vertex count too small: {len(verts)}")
    adj, body_faces = build_adjacency(faces, BODY_VERTEX_LIMIT)

    region_ids = {}
    region_files = {}
    for region in EXTENDED_REGIONS:
        ids, count = target_region_vertices(targets, region)
        region_ids[region] = ids
        region_files[region] = count
        if region in CORE_REGIONS and not ids:
            raise SystemExit(f"missing/empty facial target region: {region}")

    core = set().union(*(region_ids[r] for r in CORE_REGIONS))
    expanded = expand_vertices(core, adj, 2)
    comps = connected_components(expanded, adj)
    if not comps:
        raise SystemExit("no connected face patch")
    # Keep all large components: left/right eye islands can be distinct before closure, while tiny helpers are excluded.
    keep_components = [c for c in comps if len(c) >= max(16, len(comps[0]) * 0.01)]
    patch_seed = set().union(*keep_components)
    patch_faces = [f for f in body_faces if all(i in patch_seed for i in f)]
    used = set(i for f in patch_faces for i in f)
    if not used:
        raise SystemExit("face patch has no faces")

    # Re-evaluate connectedness on faces actually retained and keep all meaningful components.
    patch_adj: dict[int, set[int]] = defaultdict(set)
    for f in patch_faces:
        for a, b in zip(f, f[1:] + f[:1]):
            patch_adj[a].add(b); patch_adj[b].add(a)
    face_comps = connected_components(used, patch_adj)

    edge_face_count = Counter()
    valence = Counter()
    tri = quad = ngon = 0
    for f in patch_faces:
        if len(f) == 3: tri += 1
        elif len(f) == 4: quad += 1
        else: ngon += 1
        for a, b in zip(f, f[1:] + f[:1]):
            e = tuple(sorted((a, b)))
            edge_face_count[e] += 1
    for a, b in edge_face_count:
        valence[a] += 1; valence[b] += 1
    boundaries = [e for e, count in edge_face_count.items() if count == 1]

    face_box = bbox(verts, used)
    fmin, fmax = face_box["min"], face_box["max"]
    center = [(fmin[k] + fmax[k]) * 0.5 for k in range(3)]
    span = [max(fmax[k] - fmin[k], 1e-9) for k in range(3)]

    old_to_new = {old: i for i, old in enumerate(sorted(used))}
    normalized_verts = []
    for old in sorted(used):
        x, y, z = verts[old]
        normalized_verts.append([
            round((x - center[0]) / span[0], 6),
            round((y - center[1]) / span[1], 6),
            round((z - center[2]) / span[2], 6),
        ])
    template_faces = [[old_to_new[i] for i in f] for f in patch_faces if all(i in old_to_new for i in f)]

    stats = {
        "source": {
            "repo": SOURCE_REPO,
            "commit": SOURCE_COMMIT,
            "path": SOURCE_PATH,
            "license": "CC0-1.0",
            "base_mesh": "MakeHuman/MPFB hm08",
            "coordinate_system": "Y-up, +Z face-forward, OBJ units as source",
        },
        "mesh": {
            "total_vertices": len(verts),
            "body_vertex_limit": BODY_VERTEX_LIMIT,
            "total_faces": len(faces),
            "body_faces": len(body_faces),
        },
        "facial_regions": {
            r: {
                "target_files": region_files[r],
                "unique_body_vertices": len(region_ids[r]),
                "normalized_box": normalized_region_box(verts, region_ids[r] & used, face_box),
            }
            for r in EXTENDED_REGIONS
        },
        "patch": {
            "core_target_vertices": len(core),
            "expanded_two_ring_vertices": len(expanded),
            "retained_vertices": len(used),
            "retained_faces": len(patch_faces),
            "triangles": tri,
            "quads": quad,
            "ngons": ngon,
            "quad_ratio": round(quad / max(len(patch_faces), 1), 6),
            "boundary_edges": len(boundaries),
            "connected_components": [len(c) for c in face_comps[:10]],
            "valence_histogram": {str(k): v for k, v in sorted(Counter(valence.values()).items())},
            "bbox": face_box,
            "profile_samples_normalized": profile_samples(verts, used),
        },
    }

    template = {
        "version": 1,
        "license": "CC0-1.0",
        "source_repo": SOURCE_REPO,
        "source_commit": SOURCE_COMMIT,
        "source_path": SOURCE_PATH + "/3dobjs/base.obj",
        "description": "Normalized hm08 facial topology extracted from facial morph regions plus a two-edge-ring closure. Coordinates are centered and independently normalized by patch x/y/z span.",
        "normalization": {"source_center": center, "source_span": span},
        "vertices": normalized_verts,
        "faces": template_faces,
    }

    args.stats.parent.mkdir(parents=True, exist_ok=True)
    args.template.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.stats.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    args.template.write_text(json.dumps(template, separators=(",", ":")) + "\n", encoding="utf-8")

    report = f"""# CC0 Face Topology Analysis\n\nSource: MakeHuman/MPFB hm08 data vendored by `nirholas/three.ws`, pinned at `{SOURCE_COMMIT}`. The source directory declares CC0-1.0. This analysis does not import a third-party character identity; it studies and extracts the public-domain generic facial topology.\n\n## Result\n\n- hm08 vertices: **{len(verts):,}** (body vertices 0–{BODY_VERTEX_LIMIT-1:,})\n- Facial target core vertices: **{len(core):,}**\n- Two-ring topology closure: **{len(expanded):,}** candidate vertices\n- Retained face patch: **{len(used):,} vertices / {len(patch_faces):,} faces**\n- Face patch quads: **{quad:,} ({quad/max(len(patch_faces),1):.1%})**; triangles: {tri:,}; n-gons: {ngon:,}\n- Boundary edges: **{len(boundaries):,}**\n- Connected components after face retention: **{', '.join(str(len(c)) for c in face_comps[:8])}**\n\n## Modeling implications for PARRY DOLL\n\n1. Keep the v7.5+ absolute nose–mouth–chin profile as the silhouette target, but stop relying on a uniform UV-sphere grid for the facial front.\n2. Reuse the extracted CC0 topology only as an **edge-flow template**: eye, cheek, mouth, nose, forehead and chin regions get local vertex density where deformation and shading need it.\n3. Preserve a separate smooth cranium/back-head surface, then blend the topology patch into it through an outer boundary ring.\n4. Fit the normalized patch to the heroine reference sheet, not to the generic hm08 proportions; the reference images remain the identity/shape target.\n5. Keep eyes as embedded volumes behind eyelid loops. Mouth color/volume should sit on topology-defined lip loops rather than floating stickers.\n\nMachine-readable statistics: `tools/cc0-face-topology-stats.json`. Compact topology template: `tools/cc0-face-topology-template-v1.json`.\n"""
    args.report.write_text(report, encoding="utf-8")
    print(report)
    print('template bytes', args.template.stat().st_size)


if __name__ == "__main__":
    main()
