from pathlib import Path
p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')
if '# REFERENCE_V149' in s:
 print('already applied'); raise SystemExit(0)
if '# REFERENCE_V148' not in s: raise SystemExit('v148 required')
marker="# REFERENCE_V148: exact-profile eye-readability pass enlarges only the YZ side-facing sclera/iris/pupil aperture and moves the profile lids/lashes slightly outward, matching the supplied portrait without changing frontal eye spacing or width."
if marker not in s: raise SystemExit('marker missing')
s=s.replace(marker,marker+"\n# REFERENCE_V149: lower profile refinement increases the rear-side lift while preserving the accepted front silhouette.",1)
old="render_y+=.0075*under*(1.0-frontness**1.45)"
new="render_y+=.0100*under*(1.0-frontness**1.55)"
if old not in s: raise SystemExit('side lift anchor missing')
s=s.replace(old,new,1)
old="render_y+=.0200*under*(backness**1.18)"
new="render_y+=.0315*under*(backness**1.10)"
if old not in s: raise SystemExit('rear lift anchor missing')
s=s.replace(old,new,1)
old="ROOT['character_revision']='v13.18';"
new="ROOT['character_revision']='v13.19';"
if old not in s: raise SystemExit('revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.18'","HEAD_ASSET['reference_profile_silhouette']='v13.19'",1)
s=s.replace("HEAD_ASSET['underjaw_slope_revision']='v13.7'","HEAD_ASSET['underjaw_slope_revision']='v13.19'",1)
p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V149 lower profile refinement')
