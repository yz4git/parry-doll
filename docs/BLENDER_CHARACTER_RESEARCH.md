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
- Blender Manual — Sculpting: https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/index.html
- Blender Manual — Remeshing / Retopology: https://docs.blender.org/manual/en/dev/modeling/meshes/retopology.html
- Blender Manual — Face Sets: https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/editing/face_sets.html
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
14. Automate repeatable generation/export/audit work. The project already uses setup-python + NumPy + Blender in GitHub Actions, which matches Blender Studio's recommendation to automate repetitive production steps.

## Application to BLENDER heroine v2.9+

- Keep measured four-view proportions as the hard outer envelope.
- Replace the existing face-feature assembly with a continuous anatomical head shell, embedded eyeballs, curved eyelids, a connected nose form and smaller embedded lips.
- Strengthen cheekbone/jaw/chin/forehead plane changes while retaining the stylized reference face.
- Replace overly spherical bust shaping with a smoother continuous ribcage/bodice curve.
- Improve clavicle/deltoid and pelvis/thigh transitions so the character reads as one body under the costume.
- Retain v2.8 hair improvements, then judge hair after the improved skull/face changes because hairline quality depends on the head surface beneath it.
- Continue fixed front/left/back/right/face WebGL audits before publishing.
