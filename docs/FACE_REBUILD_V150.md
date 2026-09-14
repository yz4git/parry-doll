# Face Rebuild v15.0 — imported Blender sculpt

## Goal

Rebuild the heroine face from the **current game-ready `heroine-blender.glb`** instead of replacing the whole character. Blender imports the existing GLB, edits the face/eye geometry in place, validates the runtime hierarchy, then exports the same GLB path.

The supplied front and exact-right-profile key art are the proportion target. The target is an adult realistic-anime / Japanese game heroine: delicate lower face, V-shaped jaw, small smooth nose, large but not chibi almond eyes, soft cheek plane, compact lips, and a clean forehead–nose–chin profile.

## Geometry source policy

No ripped or unverified commercial game/anime mesh is copied into the repository. The existing pinned CC0 hm08 / MakeHuman-MPFB face-topology analysis remains the topology reference. This keeps the face pipeline legally reusable while letting the reference images control the style and proportions.

## v15.0 changes

- Import the existing `dist/assets/models/heroine-blender.glb` into Blender.
- Preserve `BLENDER_HEROINE`, `BL_HEAD`, `BL_HEAD_ASSET`, `BL_FACE_ASSET`, body, hair, and animation-facing node names.
- Narrow the jaw progressively below the cheek line and taper the chin further for the front silhouette.
- Reduce lower-midface width slightly without collapsing the malar plane.
- Reduce only the excess nose projection above the facial plane; keep the bridge continuous for the side view.
- Smooth/reduce the nasion transition and add a very small forward chin pad for profile balance.
- Retarget the existing complete eye assembly together (sclera, iris, pupil, lashes, lids, wetline/canthus) to a slightly wider almond shape so pieces remain aligned.
- Pull nostril detail inward with the smaller nose.
- Re-import the exported GLB and assert required runtime nodes, face density, and eye assets before committing.

## Tuning

All artistic numbers live in `tools/heroine-face-import-v150.json`. The deformation tool is `tools/rebuild-imported-face-v150.py`. This separates the sculpt logic from reference-driven proportion tuning, so subsequent front/profile reviews can adjust a few measurements without accumulating another long chain of destructive generator patches.

The next visual pass should judge, in order: exact right profile, front symmetry/eye spacing, 3/4 cheek-to-jaw transition, eye seating, then close-up skin/eye materials. Hair and costume are intentionally untouched by this rebuild.
