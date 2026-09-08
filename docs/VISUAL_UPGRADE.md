# Visual overhaul — rendering only

Baseline: 60e3f3a965ec9d2c4f6ea84436b447f7c991e003.

The latest combat scripts, physics, hit reactions, camera, input and timings are retained byte-for-byte. A separate WebGL canvas draws meshes at the existing ragdoll nodes. The existing Canvas layer draws attack telegraphs and feedback at the same projection. Failure to create a WebGL renderer falls back to the original renderer.

## Pass 1 — Characters

- Vertex-colored beveled armor, segmented limb guards, helmets, masks, horns, layered cloth and forged weapons.
- Separate metal, fabric and emissive materials; directional lighting and soft shadow maps.
- Humanoid, beast, spider and giant designs share the existing skeletons, not replacement animation.
- Draw calls are reduced by merging each node/link's decorative meshes by material.

Detailed validation is deferred until all visual passes are saved.

Build: `cd visual-src && npm ci && npm run build`. Runtime assets are vendored; the game does not load code from a CDN.

## Pass 2 — Courtyard and materials

- Pillow/NumPy generates deterministic stone color, normal and roughness maps. Source: tools/make-materials.py.
- Detailed circular courtyard, bronze inlays, gate, stone lanterns, outer galleries, cliffs, moonlit sky and cloth banners.
- All tall scenery stays beyond the original navigable radius; no collisions or gameplay geometry are added.
- Repeated architecture uses instancing. Only one shadow-casting light and two lantern lights are used.

## Pass 3 — Finish

- Soft environment reflections reveal armor bevels and blade edges.
- The original weapon-tip length is preserved for each pose; the model is fitted to it.
- Metal, cloth, stone and luminous elements use distinct material responses.
- HUD surfaces, health bars and touch controls receive matching restrained colors and highlights, without layout/input changes.
- Gameplay scripts remain unchanged from the baseline. Integration precedes final checks as requested.
