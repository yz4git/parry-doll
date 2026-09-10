from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V107' in s:
    print('Blender heroine generator already carries REFERENCE_V107')
    raise SystemExit(0)
if '# REFERENCE_V106' not in s:
    raise SystemExit('REFERENCE_V106 generator required before v10.7')

marker='# REFERENCE_V106: the CC0 face patch lower third tapers into the head shell, removing the collar-like under-chin boundary spikes without changing eyes, nose or cheeks.'
if marker not in s:
    raise SystemExit('v10.7 REFERENCE_V106 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V107: the remaining lower patch edge tightens further and settles into the head shell, eliminating the last under-chin sawtooth silhouette.',1)

old="""  under_t=max(0.0,min(1.0,(-.080-yy)/.065))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.40*under_t
"""
new="""  under_t=max(0.0,min(1.0,(-.078-yy)/.067))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.52*under_t
"""
if old not in s:
    raise SystemExit('v10.7 lower-face taper anchor missing')
s=s.replace(old,new,1)

old_z="""  z=pz+local_relief*relief_gain+.0016
"""
new_z="""  # Keep the expressive face patch proud through the cheeks, then settle its lower boundary into the backing shell.
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t)
"""
if old_z not in s:
    raise SystemExit('v10.7 face patch lift anchor missing')
s=s.replace(old_z,new_z,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V107: lower CC0 patch edge is narrower and shell-hugging for a clean chin-to-neck silhouette')
