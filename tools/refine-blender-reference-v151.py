from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V151' in s:
    print('Blender heroine generator already carries REFERENCE_V151')
    raise SystemExit(0)
if '# REFERENCE_V150' not in s:
    raise SystemExit('REFERENCE_V150 generator required before v13.21')

marker="# REFERENCE_V150: facial-plane refinement deepens the orbital bowl, strengthens the zygomatic plane and adds restrained alar, mouth-corner and jaw-angle breaks for a more premium three-quarter read without changing frontal proportions."
if marker not in s:
    raise SystemExit('v13.21 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V151: eyelid-integration pass narrows the frontal/three-quarter aperture, reduces iris dominance and increases canthal tilt while preserving the accepted exact-profile eye readability.",1)

# Narrow the frontal/3Q eye opening without changing horizontal eye spacing or width.
for old,new in (
    ("eye_ry=.00995*ASSEMBLY120['head']['eyeSize']","eye_ry=.00932*ASSEMBLY120['head']['eyeSize']"),
    ("eye_tilt=.00285","eye_tilt=.00312"),
    ("iris_scale=ASSEMBLY120['head']['irisScale']*.97","iris_scale=ASSEMBLY120['head']['irisScale']*.915"),
    ("(eye_rx*.82,eye_ry*.88,.0107)","(eye_rx*.82,eye_ry*.84,.0102)"),
    ("(eye_rx*.285,eye_ry*.48,.00495)","(eye_rx*.278,eye_ry*.445,.00470)"),
    ("(eye_rx*.105,eye_ry*.235,.00355)","(eye_rx*.100,eye_ry*.215,.00335)"),
):
    if old not in s:
        raise SystemExit('v13.21 eye anchor missing: '+old[:36])
    s=s.replace(old,new,1)

# Keep exact-profile readability after reducing eye_ry by compensating only the side-facing YZ planes.
for old,new in (
    ("eye_ry*.985,.00810,SCLERA,46","eye_ry*1.055,.00810,SCLERA,46"),
    ("eye_ry*.625,.00505,IRIS_INNER,42","eye_ry*.670,.00505,IRIS_INNER,42"),
    ("eye_ry*.292,.00242,PUPIL,32","eye_ry*.312,.00242,PUPIL,32"),
):
    if old not in s:
        raise SystemExit('v13.21 profile compensation anchor missing: '+old[:40])
    s=s.replace(old,new,1)

# Pull the dark upper lid down and the lower lid up around the eyeball so the eye reads embedded, not pasted on.
for old,new in (
    ("(ex-side*.0030,eye_y+.01165,.10484)","(ex-side*.0030,eye_y+.01055,.10482)"),
    ("(ex,eye_y-.00870,.10403)","(ex,eye_y-.00770,.10403)"),
    ("(ex,eye_y+.0153,.10375)","(ex,eye_y+.0137,.10375)"),
    (".00110*eye_contrast,HAIR)",".00116*eye_contrast,HAIR)"),
):
    if old not in s:
        raise SystemExit('v13.21 lid anchor missing: '+old[:38])
    s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.20';"
new="ROOT['character_revision']='v13.21';"
if old not in s:
    raise SystemExit('v13.21 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("FACE_ASSET['almond_eye_revision']='v13.15'","FACE_ASSET['almond_eye_revision']='v13.21'",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['eyelid_integration_revision']='v13.21';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V151: narrower almond aperture, reduced iris dominance and integrated eyelid coverage')
