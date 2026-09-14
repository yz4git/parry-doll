from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V154' in s:
    print('Blender heroine generator already carries REFERENCE_V154')
    raise SystemExit(0)
if '# REFERENCE_V153' not in s:
    raise SystemExit('REFERENCE_V153 generator required before v13.24')

marker="# REFERENCE_V153: nasion/bridge profile pass deepens the orbital-to-nose root break and builds a narrow continuous dorsum into the accepted small nose tip without changing the mouth, jaw or frontal face width."
if marker not in s:
    raise SystemExit('v13.24 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V154: exact-profile eye hero pass enlarges and slightly externalizes only the side-facing sclera/iris/pupil aperture, matching lids and lashes to that silhouette while preserving the accepted frontal/three-quarter almond eye.",1)

# Larger exact-profile ocular aperture; these YZ surfaces are nearly edge-on from the front.
for old,new in (
    ("ex+side*eye_rx*.870,eye_y+.0001,.1025,eye_ry*1.055,.00810,SCLERA,46",
     "ex+side*eye_rx*.892,eye_y+.0001,.1027,eye_ry*1.180,.00900,SCLERA,48"),
    ("ex+side*eye_rx*.880,eye_y+.0002,.10345,eye_ry*.670,.00505,IRIS_INNER,42",
     "ex+side*eye_rx*.900,eye_y+.0002,.10365,eye_ry*.760,.00570,IRIS_INNER,44"),
    ("ex+side*eye_rx*.886,eye_y+.0001,.10390,eye_ry*.312,.00242,PUPIL,32",
     "ex+side*eye_rx*.904,eye_y+.0001,.10405,eye_ry*.340,.00265,PUPIL,34"),
):
    if old not in s:
        raise SystemExit('v13.24 profile-eye anchor missing: '+old[:50])
    s=s.replace(old,new,1)

# Move the side-view lid silhouette outward and open it around the enlarged sclera.
for old,new in (
    ("(ex+side*eye_rx*.894,eye_y+eye_ry*.74,.1019)","(ex+side*eye_rx*.915,eye_y+eye_ry*.82,.1020)"),
    ("(ex+side*eye_rx*.896,eye_y+eye_ry*.33,.10715)","(ex+side*eye_rx*.918,eye_y+eye_ry*.39,.10775)"),
    ("(ex+side*eye_rx*.896,eye_y-.0001,.10865)","(ex+side*eye_rx*.918,eye_y-.0001,.10925)"),
    ("(ex+side*eye_rx*.894,eye_y-eye_ry*.70,.1020)","(ex+side*eye_rx*.915,eye_y-eye_ry*.78,.1021)"),
    ("(ex+side*eye_rx*.896,eye_y-eye_ry*.34,.10655)","(ex+side*eye_rx*.918,eye_y-eye_ry*.40,.10705)"),
    ("(ex+side*eye_rx*.896,eye_y-.0001,.10835)","(ex+side*eye_rx*.918,eye_y-.0001,.10895)"),
    (".00024*eye_contrast,FACE_DARK)",".00029*eye_contrast,FACE_DARK)"),
    (".00015*eye_contrast,EYE_WET)",".00018*eye_contrast,EYE_WET)"),
):
    if old not in s:
        raise SystemExit('v13.24 profile-lid anchor missing: '+old[:52])
    s=s.replace(old,new,1)

# Give the supplied-reference side view a clearer lash fan without changing frontal lash geometry.
for old,new in (
    ("(outer+side*.0035,eye_y+eye_tilt+.0078,.1104)","(outer+side*.0042,eye_y+eye_tilt+.0082,.1123)"),
    (".00027*eye_contrast,HAIR)",".00031*eye_contrast,HAIR)"),
    ("(outer+side*.0040,eye_y+eye_tilt+.0028,.1100)","(outer+side*.0047,eye_y+eye_tilt+.0028,.1118)"),
    (".00023*eye_contrast,HAIR)",".00027*eye_contrast,HAIR)"),
):
    if old not in s:
        raise SystemExit('v13.24 profile-lash anchor missing: '+old[:52])
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.23';"
new="ROOT['character_revision']='v13.24';"
if old not in s:
    raise SystemExit('v13.24 revision anchor missing')
s=s.replace(old,new,1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['exact_profile_eye_revision']='v13.24';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V154: larger side-facing ocular aperture with matched lids and lash fan')
