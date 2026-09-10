# Face Reference Analysis v7.3

## Purpose

Use external CC0 human-head topology as structural reference only. Do not copy an identity or directly transplant a mesh. The goal is to improve the original PARRY DOLL heroine by learning continuous facial depth, landmark spacing, and multiview consistency.

## External reference

Primary structural reference: MakeHuman / MPFB hm08 base mesh, CC0 assets.

- Coordinate convention in the vendored reference: Y-up, face toward +Z.
- Base mesh: 19,158 vertices including body and helper geometry.
- The MPFB license explicitly places bundled base mesh/assets under CC0 1.0 Universal.
- OpenGameArt also provides a female CC0 head basemesh (760 tris), but its binary OBJ endpoint was not directly retrievable in the current tool environment, so it was used only as an additional availability/topology reference.

## What the sampled CC0 mesh teaches us

The sampled frontal head vertices are not organized as a flat face with a nose object added on top. Around the same vertical band, lateral facial points have smaller +Z values while the central face progressively moves forward. The centre-line samples reach roughly z=1.58–1.61 in the sampled region, while more lateral samples in the same broad face band sit roughly around z=1.22–1.45. These are not direct heroine target dimensions; they demonstrate the structural principle that profile depth is distributed across many neighboring vertices.

For PARRY DOLL this means:

1. Eye sockets must recess into the head while the brow/zygoma support them.
2. The nasal bridge must begin near the glabella, not at the nose tip.
3. Dorsum, tip, columella and philtrum need different depths.
4. Upper lip, lower lip, labiomental crease and chin must create a continuous S-profile.
5. The eye opening must remain visibly almond-shaped from front and 3/4, not collapse to a circular exposed centre.
6. Every face revision must pass front, left/right profile, and left/right 3/4 views.

## v7.2 audit diagnosis

- Front: face is clean but eyes collapse to small circular centres.
- Profile: nose/lip/chin depth is too weak and the face reads nearly planar.
- 3/4: nose projection suddenly becomes visible, proving the model is view-dependent rather than consistently sculpted.

## v7.3 target constraints

- Preserve the stable single UV head topology.
- Keep nose/lips/chin integrated into that topology; no detached nose or floating lip volume.
- Increase dorsum/tip projection gradually, while adding a stronger philtrum and labiomental setback.
- Expose more of the almond sclera lens by bringing its perimeter closer to the facial surface.
- Keep iris smaller than the visible sclera but large enough to read clearly at iPhone model-viewer scale.
- Preserve v6.8+ body, outfit, shoulder width and ponytail baseline.

## Multiview acceptance

A revision is accepted only if the same landmarks remain plausible in all five portrait audit views:

- front
- left profile
- right profile
- left 3/4
- right 3/4

The goal is not photorealism. The target is a coherent adult anime-realistic heroine whose facial planes behave like one sculpted surface from every view.
