# Third-party face asset — v16.0

PARRY DOLL v16.0 uses an anime-style head mesh as a Blender **modeling source**. The mesh is not from a commercial game and is not a ripped asset.

## Attribution

- **Creator:** David Onizaki
- **Asset:** Genshin Style Anime Female Base Mesh For Blender
- **Source:** https://sketchfab.com/3d-models/genshin-style-anime-female-base-mesh-for-blender-c2d6727e8c9742feb9a4a3bccac6e0e0
- **License:** CC-ATTRIBUTION / CC BY, as recorded in the pinned carrier repository below.
- **Carrier repository:** https://github.com/TjhaiME/Godot-Active-Rigid-Ragdoll
- **Pinned carrier commit:** `5328516c87d56c90e409dfd09b1c7694e37696fb`
- **Carrier resource:** `addons/rigidRagdoll/Characters/GeneralRagdoll_Simple.tscn`, `HeadMesh`, ArrayMesh surface 0

The carrier repository's `LicenseInfo.txt` explicitly identifies its head as David Onizaki's CC-ATTRIBUTION asset and links to the Sketchfab source above.

## Modifications in PARRY DOLL

The source head is extracted from the pinned Godot ArrayMesh, imported into Blender, fitted to the existing PARRY DOLL head envelope, sculpted toward the supplied front and exact-right-profile key art, subdivided/smoothed, re-materialed, and substituted only for the existing `HeadShellV140` mesh while keeping the game's runtime hierarchy.

The v16 pipeline also retains the game's own body, hair, accessories and eye assembly. Old procedural lid overlays that conflict with the donor eye sockets are removed; iris and pupil components are retuned for visibility. The donor `faceUV.png` and `faceNormal.png` from the same pinned carrier are embedded into the generated GLB material by Blender.

This file is intentionally kept with the project so attribution remains visible even after Blender embeds the modified geometry and textures into the shipping GLB.
