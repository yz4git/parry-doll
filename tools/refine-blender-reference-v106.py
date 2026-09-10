from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V106' in s:
    print('Blender heroine generator already carries REFERENCE_V106')
    raise SystemExit(0)
if '# REFERENCE_V105' not in s:
    raise SystemExit('REFERENCE_V105 generator required before v10.6')

marker='# REFERENCE_V105: visible rear-hair geometry expands around ear height while the buried v10.4 undercap returns to the compact v10.3 footprint.'
if marker not in s:
    raise SystemExit('v10.6 REFERENCE_V105 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V106: the CC0 face patch lower third tapers into the head shell, removing the collar-like under-chin boundary spikes without changing eyes, nose or cheeks.',1)

old="""  jaw_t=max(0.0,min(1.0,(-.025-yy)/.120))
  x=vx*.238*(1.0-.175*jaw_t)
"""
new="""  jaw_t=max(0.0,min(1.0,(-.025-yy)/.120))
  x=vx*.238*(1.0-.175*jaw_t)
  # The open CC0 patch used to stay too wide below the mouth while HeadShellV60 narrows sharply.
  # Smoothly pull only the lower third inward so its boundary stays inside the jaw/under-chin silhouette.
  under_t=max(0.0,min(1.0,(-.080-yy)/.065))
  under_t=under_t*under_t*(3.0-2.0*under_t)
  x*=1.0-.40*under_t
"""
if old not in s:
    raise SystemExit('v10.6 CC0 jaw mapping anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V106: tapered CC0 lower-face boundary now follows the chin shell instead of protruding as side spikes')
