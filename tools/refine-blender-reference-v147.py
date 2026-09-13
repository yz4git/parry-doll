from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V147' in s:
    print('Blender heroine generator already carries REFERENCE_V147')
    raise SystemExit(0)
if '# REFERENCE_V146' not in s:
    raise SystemExit('REFERENCE_V146 generator required before v13.17')

marker="# REFERENCE_V146: visible-profile ornament pass moves the previously buried side hair hardware onto the outer hair surface and rebuilds it as a segmented black/silver vertical spine with a crown cap and pony-root bands, matching the supplied reference silhouette."
if marker not in s:
    raise SystemExit('v13.17 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V147: continuous-profile silhouette pass rebuilds the centre-line forehead/nasal-root/nose/lip/chin S-curve from the supplied side portrait while leaving frontal widths, eye spacing, jaw width and the accepted neck/hair systems unchanged.",1)

# The accepted v13.8 profile had a compact nose tip but still changed depth too abruptly, reading as a small
# attached nub at exact profile. This spline begins the nasal projection higher, carries it forward gradually,
# separates upper/lower lip peaks, and lets the chin sit slightly behind the lower lip like the supplied portrait.
old=""" base_profile=[
  (.090,.1005),(.060,.1017),(.035,.1007),(.015,.0988),(-.005,.1020),(-.025,.1105),
  (-.040,.1235),(-.048,.1287),(-.055,.1272),(-.062,.1168),(-.068,.1078),
  (-.077,.1115),(-.086,.1190),(-.094,.1216),(-.103,.1113),(-.111,.1030),
  (-.121,.1168),(-.131,.1150),(-.140,.1040),(-.148,.0870),(-.154,.0710)
 ]
"""
new=""" base_profile=[
  (.090,.1002),(.060,.1010),(.038,.1000),(.020,.0984),(.006,.0995),(-.008,.1042),
  (-.022,.1112),(-.035,.1200),(-.046,.1264),(-.053,.1290),(-.059,.1266),
  (-.065,.1182),(-.071,.1086),(-.078,.1118),(-.086,.1204),(-.093,.1228),
  (-.100,.1188),(-.106,.1112),(-.112,.1040),(-.121,.1162),(-.130,.1142),
  (-.139,.1030),(-.148,.0860),(-.154,.0705)
 ]
"""
if old not in s:
    raise SystemExit('v13.17 profile spline anchor missing')
s=s.replace(old,new,1)

# Keep projection restrained overall, but allow the longer bridge to read as one continuous surface rather
# than compensating with an oversized tip.
old="nose_proj=profile_ctrl['noseProjection']*.73;nose_width=profile_ctrl['noseWidth']"
new="nose_proj=profile_ctrl['noseProjection']*.71;nose_width=profile_ctrl['noseWidth']"
if old not in s:
    raise SystemExit('v13.17 nose projection anchor missing')
s=s.replace(old,new,1)

# Refine lip depth in the actual shell, not only the colour patches: a restrained upper peak, rounder lower
# lip, and a slightly deeper labiomental groove make the side silhouette readable even before material cues.
for old,new in (
    ("z+=fm*.00340*lip_volume*ul","z+=fm*.00362*lip_volume*ul"),
    ("z+=fm*.00398*lip_volume*ll","z+=fm*.00430*lip_volume*ll"),
    ("z-=fm*.00195*lip_volume*mouth_groove","z-=fm*.00225*lip_volume*mouth_groove"),
):
    if old in s:
        s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.16';"
new="ROOT['character_revision']='v13.17';"
if old not in s:
    raise SystemExit('v13.17 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.16'","HEAD_ASSET['reference_profile_silhouette']='v13.17'",1)
s=s.replace("FACE_ASSET['reference_nose_lip_revision']='v13.8'","FACE_ASSET['reference_nose_lip_revision']='v13.17'",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['continuous_profile_revision']='v13.17';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V147: continuous nasal bridge, separated lip peaks and recessed elegant chin profile')
