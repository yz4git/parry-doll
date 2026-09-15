# Hair Donor v18.0

## Scope

This pass changes **hair only**. The shipping face is frozen: `HeadShellV140`, eyes, irises, pupils, sclera, eyelids, lashes, brows, canthi, wetlines, lips, mouth details, beauty mark, ears, nose/face detail meshes and their transforms are protected by an automated before/after GLB audit.

## Donor

- Asset: **OverScore Proxy 1.5 - Modular Low-Poly Female Character Creation Set**
- Hair style: **High Ponytail**
- Source: https://opengameart.org/node/157297
- Download used by the build: https://opengameart.org/sites/default/files/proxy_1.5.blend
- License: **CC0**
- Author: OverScore Media (`overscore_media` on OpenGameArt)
- Source file was authored in Blender 4.0.2; the repository build uses pinned Blender 4.2.0.

The donor contains 30 hairstyles. High Ponytail was chosen because it matches Parry Doll's established high-ponytail silhouette while giving us a real Blender-authored game hair mesh instead of relying only on procedural strips.

## Blender edit

`tools/build-hair-donor-v180.py` imports the current shipping GLB, snapshots all protected face meshes, removes only the old hairstyle meshes, appends High Ponytail from the external donor `.blend`, orients the ponytail toward the character rear, fits crown width/top/front to `HeadShellV140`, applies the donor's authored modifiers, adds one controlled smoothing subdivision when affordable, assigns a dedicated dark game-hair material, and parents the result to `BL_HAIR_ASSET`.

The donor source itself is not checked into this repository. GitHub Actions downloads the original CC0 `.blend` during the authoring job.

## Face-lock acceptance gate

`tools/audit-hair-donor-v180.py` re-imports the GLB from before the hair pass and the newly exported GLB. The job fails if any protected face object is missing/added, topology differs, parent differs, or any protected vertex/transform changes by more than `3e-6` world/local units.

This means future hair iterations can continue without silently drifting the face.
