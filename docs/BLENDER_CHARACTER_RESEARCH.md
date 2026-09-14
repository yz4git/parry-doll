# Blender character modeling research

Purpose: keep the BLENDER heroine grounded in production character-modeling practice while preserving the CLASSIC model as an untouched fallback.

## Sources reviewed

Primary references:
- Blender Studio — Realistic Character Workflow: https://studio.blender.org/training/realistic-human-research/
- Blender Studio — Use of Base Meshes: https://studio.blender.org/training/realistic-human-research/use-of-base-meshes/
- Blender Studio — Design Sculpting: https://studio.blender.org/training/realistic-human-research/design-sculpting/
- Blender Studio — Generic Retopology: https://studio.blender.org/training/realistic-human-research/retopology/
- Blender Studio — Creating Facial Shapes: https://studio.blender.org/training/realistic-human-research/creating-facial-shapes/
- Blender Studio — Reprojection & Sculpt Layers: https://studio.blender.org/training/realistic-human-research/reprojection-sculpt-layers/
- Blender Studio — Stylized Character Workflow / facial topology notes: https://studio.blender.org/training/stylized-character-workflow/
- Blender Manual — Multiresolution Modifier / bake-from-multires workflow: https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/multiresolution.html
- Blender Manual — Render Baking: https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- Khronos — glTF 2.0 Specification (morph targets, skinning, PBR textures): https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Khronos — Physically Based Rendering in glTF: https://www.khronos.org/gltf/pbr
- Khronos — glTF runtime 3D asset delivery / KTX2 overview: https://www.khronos.org/gltf/
- Epic Games — MetaHuman Identity Asset / template-conform workflow: https://dev.epicgames.com/documentation/metahuman/metahuman-identity-asset
- Polycount — clean topology discussion/tutorial references: https://polycount.com/discussion/229984/learn-how-to-create-clean-topology-for-your-character-models-all-the-time

## Production rules distilled for Parry Doll

1. Lock silhouette and large forms before detail. Head size, shoulder line, ribcage, waist, pelvis and limb lengths must read correctly in front/side/back views before adding micro detail.
2. Build the body as continuous masses, not a collection of visible spheres/cylinders. Ribcage-to-waist and pelvis-to-thigh transitions should be continuous.
3. Treat the skull, jaw, cheekbone and eye socket as primary facial planes. Facial features should sit on or emerge from that continuous surface.
4. Place eyeballs first, then wrap eyelids around them. Avoid flat rectangular eye plates floating in front of the face.
5. The nose should grow out of the brow/face plane through bridge, tip and alar wings; the mouth should stay embedded in the muzzle/lower-face plane rather than appearing as a decal.
6. Hair is a separate layered mass. First establish scalp/crown volume, then major locks, then secondary strands. Specular should not turn dark hair into silver plastic.
7. Clothing should be layered over the body and should not replace anatomical form. Keep a clean underlying torso/pelvis silhouette.
8. A neutral A-pose or relaxed base pose is best for authoring because major surfaces are not already stretched/compressed.
9. Voxel/automatic remesh is useful for blockout and cleanup, but final deformation topology should follow anatomy and articulation; there is no perfect automatic final-character retopology.
10. Keep base topology reasonably even and low enough to support subdivision/multires workflows. Add detail in layers instead of baking every form into the base.
11. Facial topology needs loops and curvature support around eyes, mouth and major creases; proximity loops should support curvature without pinching.
12. Iterate broad proportions first. Changes to base proportions are cheaper and safer before expression shapes, clothing corrections and fine detail.
13. Use references continuously. Correct eye size, head depth, jaw width, shoulder width, pelvis depth and limb taper against orthographic/reference views rather than intuition alone.
14. Automate repeatable generation/export/audit work. The project already uses setup-python + NumPy + Blender in GitHub Actions, which matches production practice for repeatable asset builds.
15. Keep runtime and authoring representations separate: a high-detail sculpt can be baked into normal/roughness/AO while a lighter game mesh carries skinning and morph targets.
16. Treat morph targets as a first-class runtime contract. glTF supports morph deltas and skinning, so blink/expression work should be built on stable base topology rather than repeatedly changing vertex structure after expressions are authored.

## v14.0 root face rebuild decision

The v13 series proved that small local edits can improve one camera angle, but repeated profile/nose/lip patches accumulate competing Gaussian/RBF fields and make the face harder to reason about. v14.0 therefore freezes the body, BL_HEAD hierarchy, neck connection, hair hierarchy and blink runtime contract, while replacing only the visible head base.

Implementation rules for v14.0:
- Use one new continuous closed quad cage (`HeadShellV140`) as the visible skull/face/jaw/under-jaw surface.
- Drive large forms from explicit multiview section rows plus a single centre-profile curve stored in `tools/heroine-face-rebuild-v140.json`.
- Use local depth fields only for anatomical planes: orbit, brow, malar support, cheek hollow, alar base, philtrum, lips, mouth corners and chin. Do not use local fields to define the primary profile silhouette.
- Keep the supplied profile reference intent: recessed eye socket, slim smooth nasal bridge, small rounded tip, embedded lips, soft projected chin and a jaw plane that rises toward the ear.
- Keep front/3Q eye design adult and almond-shaped while retaining an exact-profile side-eye helper only where required for mobile readability.
- Preserve `BL_HEAD`, `BL_EYE_L`, `BL_EYE_R`, `BL_EYELID_L`, `BL_EYELID_R`, `BL_MOUTH`, and `BL_HAIR_ASSET` names so gameplay and blink code do not change.
- After the v14.0 base is accepted, add sculpt/bake detail on top rather than restarting local silhouette edits. The next texture stage should prioritize normal + roughness + AO; KTX2/Basis can be considered if texture memory becomes the limiting factor on iPhone.
- Five-view high-resolution portrait and normal WebGL audits are mandatory before publishing the rebuild.

## Application to BLENDER heroine

- Keep measured four-view body proportions as the hard outer envelope.
- Keep the improved layered hair, visible ear, profile ornament and long-neck work from v13.x.
- Replace the v13 accumulated visible face shell with the v14.0 continuous cage.
- Re-seat the modular eyes and lip colour accents on the new surface, but keep geometry ownership in the continuous head shell.
- Once the new base passes front/3Q/profile review, add a higher-detail sculpt layer and bake fine eyelid/nasal/lip surface change into runtime textures instead of increasing visible helper geometry.
- Continue fixed front/left/back/right/face WebGL audits before publishing.
