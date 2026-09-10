# AI Face Modeling Playbook — PARRY DOLL

Purpose: turn AI/visual feedback into stable 3D face changes instead of repeatedly moving isolated parts.

## 1. Geometry first, materials second

Evaluate an untextured or low-detail face silhouette before polishing materials. A face that only works because of eye/lip color is not accepted. The head must read from front, both profiles, and 3/4 views.

## 2. Multi-view is a hard constraint

Use the same identity, neutral expression, camera distance, head scale, lighting, and hairstyle in every reference view. Preferred set:

- front
- left/right profile
- 3/4
- back only when hair mass is being changed

Do not optimize the front image while allowing the side profile to become a different face.

## 3. Landmark groups, not vague adjectives

Describe and validate these groups explicitly:

- cranial silhouette: forehead, temple, cheekbone, jaw angle, chin
- orbit: inner/outer canthus, upper/lower lid, iris center, brow
- nose: root, bridge, dorsum, tip, alar width, columella
- mouth: cupid bow, commissures, upper/lower volume, labiomental crease
- profile: forehead -> nasal root -> tip -> philtrum -> lips -> chin must form one continuous S-curve

Words such as “beautiful”, “realistic”, and “anime-like” may describe the goal, but they are never sufficient geometry instructions.

## 4. PARRY DOLL portrait target

Young-adult realistic-anime heroine. Delicate rather than childlike. Soft tapered jaw; small but visible nose; large dark grey-brown eyes with restrained sclera; defined upper lid; natural small lips; smooth cheek plane. No doll-button eyes, no circular iris rings, no pasted-on nose balls, no floating lip ribbons, no muzzle, no helmet hair.

The face must remain readable at iPhone gameplay scale, so primary forms matter more than microdetail.

## 5. AI instruction pattern

Put high-value geometry first:

`Young-adult feminine head, neutral expression, realistic-anime proportions; tapered oval jaw and small chin; large horizontally almond eyes seated inside the orbits, grey-brown iris, restrained sclera; narrow continuous nose bridge and small projected tip; small curved lips integrated into the muzzle plane; high dark ponytail; clean watertight game-ready surface, no floating facial parts.`

For multi-view generation append:

`Same identity, same neutral expression, same hairstyle, same scale and lens in every view. Orthographic-like front, profile and 3/4 views. Preserve silhouette and landmark positions across views.`

Negative/avoid list:

`no goggle eyes, no circular button eyes, no detached nose spheres, no protruding muzzle, no flat sticker lips, no duplicate face surfaces, no z-fighting, no asymmetry drift, no different identity between views.`

## 6. Iteration order

1. skull/jaw silhouette
2. eye sockets + visible eyeball envelope
3. integrated nose profile
4. integrated lip/chin profile
5. three-quarter validation
6. hairline and large hair masses
7. materials and microdetail

Only one or two geometry families should change in a pass. Keep the last stable body/hair version locked during portrait-only passes.

## 7. Project validation gates

A portrait pass is accepted only when all are true:

- front: both eyes separated; sclera does not dominate; iris is not a ring/button
- profile: nose and lips project from the same facial surface; nothing dangles or floats
- left/right: silhouette is consistent
- 3/4: no sudden flattening or doubled surfaces
- runtime: BLENDER variant loads, GLB HTTP 200, no fatal browser errors
- CLASSIC variant remains untouched

## 8. Sources / recent practice

- Meshy, “How to Write Text to 3D Prompts: Step-by-Step Guide (2026)” — subject/material/style/technical constraints; front-load important details: https://www.meshy.ai/tutorials/3d-prompt-guide
- Meshy, “How to Use Multi-View Image to 3D in Meshy (2026 Guide)” — consistent 1–4 views, same distance/lighting, geometry rebuilt from supplied views: https://www.meshy.ai/tutorials/multi-view-image-to-3d
- Tencent Hunyuan3D-2.1 — separate shape generation from PBR texture synthesis; production asset pipeline: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1
- FaceLift, ICCV 2025 / arXiv 2412.17812 — generate consistent side/back views, then reconstruct a 360-degree head: https://arxiv.org/abs/2412.17812

## 9. Immediate implementation consequence

From v7.1 onward, the PARRY DOLL face should prefer deformation of the single stable UV head surface. Separate geometry is permitted for eyeballs/iris and tiny color accents, but not as the primary nose or mouth volume. Nose/lip depth belongs to the head mesh so front and profile cannot diverge.
