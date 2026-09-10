# PARRY DOLL face rebuild v11.2

## Goal

Rebuild the BLENDER heroine face from a new continuous head mesh instead of extending the old HeadShellV60 + FaceQuadPatchV77 stack.

## Public references reviewed

### MakeHuman / MPFB
- https://github.com/makehumancommunity/makehuman
- https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html
- Core graphical assets, including base mesh and targets, are CC0.
- The public MakeHuman base is designed as a continuous morphable human surface rather than a collection of facial plates.
- PARRY DOLL uses this only as a structural reference: continuous cranium, cheek, jaw and under-chin flow. No MakeHuman vertex data is copied into the generated heroine mesh.

### MB-Lab anime female
- https://mb-lab-docs.readthedocs.io/en/latest/dev_data.html
- MB-Lab documents an MBLab_anime_female base alongside human female/male bases.
- Its database/mesh assets are AGPL-3.0, so no MB-Lab mesh, vertices, morph data or JSON are copied into PARRY DOLL.
- It is used only to validate the high-level production idea that an anime-stylized face should still be driven by one coherent skull / orbital / cheek / jaw surface.

### Existing public stylized-anime studies
- Public downloadable stylized/anime heads were reviewed only for silhouette tendencies: enlarged but adult-scaled eyes, compact lower face, shallow muzzle, small nasal wings, and a cheek-to-jaw curve that remains three-dimensional in profile.
- No third-party downloadable geometry is imported into the repository.

## v11.2 geometry rules

1. One closed head shell owns forehead, temples, eye sockets, cheeks, nose, muzzle, jaw, chin and under-chin.
2. Remove FaceQuadPatchV77 from the rendered model entirely.
3. Preserve compatibility with the existing hair cap, rear hair shell and ears by keeping the cranium envelope close to the measured reference.
4. Keep adult-scale almond eye placement, but sculpt orbital recess and zygomatic support into the head itself.
5. Build the nose continuously from glabella to bridge, dorsum, tip and columella; nostril tint is only a surface accent.
6. Build a shallow muzzle and chin pad into the shell so lip panels remain tint/detail, not structural geometry.
7. Use a compact jaw-to-neck transition with no UV-sphere tail or lower overlay seam.
8. Validate front, both three-quarter views and both profiles before accepting the rebuild.

## License boundary

MakeHuman CC0 information may be used freely, but v11.2 remains independently generated parametric geometry. MB-Lab AGPL data is not copied or embedded. The rebuild is authored from project measurements and general anatomical/stylized modeling observations.
