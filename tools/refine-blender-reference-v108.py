from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V108' in s:
    print('Blender heroine generator already carries REFERENCE_V108')
    raise SystemExit(0)
if '# REFERENCE_V107' not in s:
    raise SystemExit('REFERENCE_V107 generator required before v10.8')

marker='# REFERENCE_V107: the remaining lower patch edge tightens further and settles into the head shell, eliminating the last under-chin sawtooth silhouette.'
if marker not in s:
    raise SystemExit('v10.8 REFERENCE_V107 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V108: only the lower CC0 patch perimeter is feathered into the backing head shell, removing residual chin-edge teeth while preserving the centre profile.',1)

old="""  under_t=max(0.0,min(1.0,(-.078-yy)/.067))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.52*under_t
  # Anime-reference eye spacing: spread the orbital band without widening cheeks/jaw globally.
"""
new="""  under_t=max(0.0,min(1.0,(-.078-yy)/.067))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.52*under_t
  # v10.8 feathers only the lower outer CC0 perimeter. The centre chin keeps the measured profile;
  # outer seam vertices contract a little more so no isolated triangle can protrude past HeadShellV60.
  edge_t=max(0.0,min(1.0,(abs(vx)-.205)/.095))
  edge_t=edge_t*edge_t*(3.0-2.0*edge_t)
  edge_under=edge_t*under_t
  x*=1.0-.14*edge_under
  # Anime-reference eye spacing: spread the orbital band without widening cheeks/jaw globally.
"""
if old not in s:
    raise SystemExit('v10.8 lower-face perimeter anchor missing')
s=s.replace(old,new,1)

old_z="""  # Keep the expressive face patch proud through the cheeks, then settle its lower boundary into the backing shell.
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t)
"""
new_z="""  # Keep the expressive face patch proud through the cheeks, then settle its lower boundary into the backing shell.
  # At the lower outer perimeter suppress generic relief and pull the seam fractionally rearward;
  # centre-line chin/lip depth remains untouched because edge_under is zero there.
  local_relief*=1.0-.62*edge_under
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t-.00085*edge_under)
"""
if old_z not in s:
    raise SystemExit('v10.8 face patch seam-depth anchor missing')
s=s.replace(old_z,new_z,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V108: lower CC0 perimeter feathered into head shell with centre profile frozen')
