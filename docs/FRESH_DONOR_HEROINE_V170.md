# Fresh donor heroine v17.0

## Build rule

v17.0 is intentionally **not** an edit of the previous `heroine-blender.glb`. The build starts from an empty Blender scene and regenerates the PARRY DOLL body, costume, hair, sword and runtime hierarchy from the repository's Blender source scripts. The previous GLB is deleted from the CI working tree before Blender starts.

After the fresh procedural character exists in the same Blender process, the head shell is replaced with a freshly extracted and modified David Onizaki anime head. No old GLB is imported as a geometry or fitting source. The finished character is exported directly to the game's existing path, `dist/assets/models/heroine-blender.glb`, so the current Three.js runtime uses the new model without a loader-path change.

## Head source and attribution

- Creator: **David Onizaki**
- Asset: **Genshin Style Anime Female Base Mesh For Blender**
- Source: https://sketchfab.com/3d-models/genshin-style-anime-female-base-mesh-for-blender-c2d6727e8c9742feb9a4a3bccac6e0e0
- License: **CC-ATTRIBUTION / CC BY**, as recorded by the pinned carrier repository
- Carrier: https://github.com/TjhaiME/Godot-Active-Rigid-Ragdoll
- Pinned carrier commit: `5328516c87d56c90e409dfd09b1c7694e37696fb`
- Carrier resource: `addons/rigidRagdoll/Characters/GeneralRagdoll_Simple.tscn`, `HeadMesh`, ArrayMesh surface 0

The workflow verifies the attribution line in the carrier repository before extracting the head. The donor's face UV and normal textures are used by the final Blender material.

## Modeling pass

`tools/build-donor-heroine-v170.py` performs the donor-specific Blender work after the fresh body build. It narrows the lower jaw/chin, gently softens cheek width, reduces only excessive central nose projection, compresses the upper-front forehead slightly, subdivides/smooths the donor surface, fits the result to the freshly generated head envelope, and preserves the game's modular runtime roots.

The existing PARRY DOLL eye assembly is retained and retuned, while procedural lid/rim/nostril/lip overlays that conflict with the donor topology are removed. Hair, accessories and costume are fresh outputs of the source generator in the same build rather than geometry copied from the old GLB.

## Game integration

The existing runtime already loads `assets/models/heroine-blender.glb`. v17.0 therefore replaces that shipping asset in-place while preserving the required nodes such as `BL_HEAD`, `BL_TORSO`, limb groups, face asset groups and `BL_SWORD`. `tools/audit-donor-heroine-v170.py` re-imports the **newly exported** GLB only for validation and checks hierarchy, donor-head density and eye assembly before the CI commit is allowed.
