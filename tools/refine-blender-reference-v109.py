from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V109' in s:
    print('Blender heroine generator already carries REFERENCE_V109')
    raise SystemExit(0)
if '# REFERENCE_V108' not in s:
    raise SystemExit('REFERENCE_V108 generator required before v10.9')

marker='# REFERENCE_V108: only the lower CC0 patch perimeter is feathered into the backing head shell, removing residual chin-edge teeth while preserving the centre profile.'
if marker not in s:
    raise SystemExit('v10.9 REFERENCE_V108 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V109: the CC0 overlay fades behind the backing shell below the mouth; the continuous head shell owns chin and under-chin silhouette with no beard-like patch edge.',1)

old="""  local_relief*=1.0-.62*edge_under
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t-.00085*edge_under)
  bridge_lat=math.exp(-(x/.030)**2)
"""
new="""  local_relief*=1.0-.62*edge_under
  z=pz+local_relief*relief_gain+(.0016-.0012*under_t-.00085*edge_under)
  # The CC0 patch is an expression/topology overlay, not the final under-chin shell. Fade it behind
  # HeadShellV60 after the mouth so the closed UV head owns the chin silhouette continuously.
  chin_hide=max(0.0,min(1.0,(-.094-yy)/.051))
  chin_hide=chin_hide*chin_hide*(3.0-2.0*chin_hide)
  z-=.0190*chin_hide
  bridge_lat=math.exp(-(x/.030)**2)
"""
if old not in s:
    raise SystemExit('v10.9 CC0 chin fade anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V109: CC0 lower overlay fades behind the continuous head shell below the mouth')
