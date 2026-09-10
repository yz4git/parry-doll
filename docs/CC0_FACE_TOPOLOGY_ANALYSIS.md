# CC0 Face Topology Analysis

Source: MakeHuman/MPFB hm08 data vendored by `nirholas/three.ws`, pinned at `03264788d967bcd33844be70e35db05b231aa017` and declared CC0-1.0.

## v2 local-face extraction

- hm08 vertices: **19,158**; body range: 0–13,379.
- Head morph envelope: **4,355 vertices**, bbox `{'min': [-0.8793, 5.4729, -0.3916], 'max': [0.8793, 8.4913, 1.6807]}`.
- +Z facial ROI seed: **4,011 vertices** from cheek/chin/brows/eyes/forehead/mouth/nose after geometric clipping.
- After two adjacency rings: **4,154 vertices**.
- Largest connected face skin patch: **4,154 vertices / 4,106 faces**.
- Quads: **4,106 (100.0%)**; triangles: 0; n-gons: 0.
- Open patch boundary edges: **94**. A nonzero boundary is expected and is the seam used to blend into PARRY DOLL's cranium.

## PARRY DOLL use

The generic CC0 geometry is **not the heroine's identity target**. The extracted patch supplies edge flow and local vertex density only. v7.5+ remains the side-profile constraint, while the generated PARRY DOLL face sheet controls eye scale, V-jaw, cheek width, nose and lip shape. The next hybrid head should fit this topology to those targets and bridge its boundary into a simpler rear cranium.

Machine data: `tools/cc0-face-topology-stats.json` and `tools/cc0-face-topology-template-v1.json`.
