# CC0 Face Topology Analysis

Source: MakeHuman/MPFB hm08 data vendored by `nirholas/three.ws`, pinned at `03264788d967bcd33844be70e35db05b231aa017`. The source directory declares CC0-1.0. This analysis does not import a third-party character identity; it studies and extracts the public-domain generic facial topology.

## Result

- hm08 vertices: **19,158** (body vertices 0–13,379)
- Facial target core vertices: **12,130**
- Two-ring topology closure: **13,380** candidate vertices
- Retained face patch: **13,380 vertices / 13,378 faces**
- Face patch quads: **13,378 (100.0%)**; triangles: 0; n-gons: 0
- Boundary edges: **0**
- Connected components after face retention: **13380**

## Modeling implications for PARRY DOLL

1. Keep the v7.5+ absolute nose–mouth–chin profile as the silhouette target, but stop relying on a uniform UV-sphere grid for the facial front.
2. Reuse the extracted CC0 topology only as an **edge-flow template**: eye, cheek, mouth, nose, forehead and chin regions get local vertex density where deformation and shading need it.
3. Preserve a separate smooth cranium/back-head surface, then blend the topology patch into it through an outer boundary ring.
4. Fit the normalized patch to the heroine reference sheet, not to the generic hm08 proportions; the reference images remain the identity/shape target.
5. Keep eyes as embedded volumes behind eyelid loops. Mouth color/volume should sit on topology-defined lip loops rather than floating stickers.

Machine-readable statistics: `tools/cc0-face-topology-stats.json`. Compact topology template: `tools/cc0-face-topology-template-v1.json`.
