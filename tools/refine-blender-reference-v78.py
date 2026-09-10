from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V78' in s:
    print('Blender heroine generator already carries REFERENCE_V78')
    raise SystemExit(0)
if '# REFERENCE_V77' not in s:
    raise SystemExit('REFERENCE_V77 generator required before v7.8')

s=s.replace(
    '# REFERENCE_V77: pinned-CC0 quad topology hybrid face retargeted to the PARRY DOLL multiview profile.',
    '# REFERENCE_V77: pinned-CC0 quad topology hybrid face retargeted to the PARRY DOLL multiview profile.\n# REFERENCE_V78: narrower mature face, wider almond gaze, fuller sculpted lips and cleaner swept hairline.',
    1,
)

# Preserve the v7.7 topology, but pull the cheek/jaw envelope inward while expanding only the orbital band.
s=s.replace(
    "x=vx*.245*(1.0-.105*jaw_t)",
    "x=vx*.238*(1.0-.135*jaw_t)",
    1,
)
s=s.replace(
    "x+=math.copysign(.0060*orbital*max(0.0,1.0-abs(x)/.122),x) if abs(x)>1e-8 else 0.0",
    "x+=math.copysign(.0076*orbital*max(0.0,1.0-abs(x)/.119),x) if abs(x)>1e-8 else 0.0",
    1,
)

# Adult almond gaze: wider, slightly farther apart, without increasing the surprised vertical opening.
for old,new in [
    ('eye_y=.0308','eye_y=.0330'),
    ('eye_x=.0465','eye_x=.0498'),
    ('eye_rx=.0285','eye_rx=.0318'),
    ('eye_ry=.0124','eye_ry=.0128'),
    ('eye_tilt=.0030','eye_tilt=.0024'),
    ("add_almond_lens(HEAD,f'EyeScleraV76_{side}',ex,eye_y,.1034,.0350,.0127,.00425,SCLERA,8,72,side,eye_tilt*.70)",
     "add_almond_lens(HEAD,f'EyeScleraV78_{side}',ex,eye_y,.1038,.0392,.0129,.00410,SCLERA,8,80,side,eye_tilt*.72)"),
    ("add_sphere(HEAD,f'IrisV76_{side}',(ex,eye_y,.1083),(.0123,.0102,.00140),IRIS_INNER,48,28)",
     "add_sphere(HEAD,f'IrisV78_{side}',(ex,eye_y,.1087),(.0137,.0104,.00142),IRIS_INNER,52,30)"),
    ("add_sphere(HEAD,f'PupilV76_{side}',(ex,eye_y-.0001,.1094),(.00255,.00325,.00096),PUPIL,30,20)",
     "add_sphere(HEAD,f'PupilV78_{side}',(ex,eye_y-.0002,.1098),(.00275,.00335,.00098),PUPIL,32,22)"),
    ("add_ellipse_surface(HEAD,f'EyeLightV60_{side}',ex-side*.0038,eye_y+.0043,.1100,.00120,.00100,SCLERA,18)",
     "add_ellipse_surface(HEAD,f'EyeLightV78_{side}',ex-side*.0044,eye_y+.0041,.1104,.00128,.00102,SCLERA,18)"),
    ("add_strand(HEAD,f'BrowV76_{side}',[(ex-side*.026,.064,.1010),(ex,.0715,.1021),(ex+side*.030,.061,.1012)],.00056,HAIR)",
     "add_strand(HEAD,f'BrowV78_{side}',[(ex-side*.028,.0655,.1014),(ex,.0725,.1024),(ex+side*.032,.0625,.1016)],.00052,HAIR)"),
]:
    if old not in s:
        raise SystemExit(f'v7.8 eye anchor missing: {old[:56]}')
    s=s.replace(old,new,1)

# Fuller but still restrained lips. The central z advance gives the mouth a soft three-dimensional read in 3/4 view.
old_lips="""add_panel(HEAD,'UpperLipV76_L',[(-.0230,-.0850,.1100),(-.0115,-.0802,.1113),(0,-.0834,.1120),(0,-.0871,.1123),(-.0100,-.0862,.1119),(-.0215,-.0884,.1107)],.00050,LIP)
add_panel(HEAD,'UpperLipV76_R',[(0,-.0834,.1120),(.0115,-.0802,.1113),(.0230,-.0850,.1100),(.0215,-.0884,.1107),(.0100,-.0862,.1119),(0,-.0871,.1123)],.00050,LIP)
add_panel(HEAD,'LowerLipV76',[(-.0215,-.0884,.1111),(0,-.0876,.1122),(.0215,-.0884,.1111),(.0185,-.0945,.1108),(0,-.0970,.1110),(-.0185,-.0945,.1108)],.00055,LIP)
add_strand(HEAD,'MouthSeamV76',[(-.0210,-.0868,.1110),(-.0100,-.0864,.1118),(0,-.0872,.1124),(.0100,-.0864,.1118),(.0210,-.0868,.1110)],.000052,FACE_DARK)
"""
new_lips="""add_panel(HEAD,'UpperLipV78_L',[(-.0260,-.0850,.1102),(-.0128,-.0797,.1118),(0,-.0828,.1129),(0,-.0870,.1132),(-.0110,-.0860,.1125),(-.0242,-.0883,.1109)],.00066,LIP)
add_panel(HEAD,'UpperLipV78_R',[(0,-.0828,.1129),(.0128,-.0797,.1118),(.0260,-.0850,.1102),(.0242,-.0883,.1109),(.0110,-.0860,.1125),(0,-.0870,.1132)],.00066,LIP)
add_panel(HEAD,'LowerLipV78',[(-.0242,-.0884,.1112),(0,-.0874,.1129),(.0242,-.0884,.1112),(.0208,-.0954,.1110),(0,-.0990,.1115),(-.0208,-.0954,.1110)],.00072,LIP)
add_strand(HEAD,'MouthSeamV78',[(-.0248,-.0868,.1111),(-.0115,-.0862,.1123),(0,-.0872,.1133),(.0115,-.0862,.1123),(.0248,-.0868,.1111)],.000050,FACE_DARK)
"""
if old_lips not in s:
    raise SystemExit('v7.6 lip block missing')
s=s.replace(old_lips,new_lips,1)

# Replace the visor-like broad veil with a smaller swept root that only seals the scalp/fringe seam.
old_hair="""# v7.7 single continuous front-scalp veil replaces crossed filler ribbons and closes the last forehead opening.
add_flow_ribbon(HEAD,'HairlineVeilV77',[(0,.194,.052),(0,.177,.073),(0,.158,.091),(0,.138,.103),(0,.118,.109)],[.090,.174,.220,.226,.198],.00110,HAIR)
"""
new_hair="""# v7.8 swept root closes the seam without reading as a horizontal visor across the forehead.
add_flow_ribbon(HEAD,'HairlineRootV78',[(-.038,.196,.048),(-.030,.184,.069),(-.014,.169,.087),(.010,.152,.101),(.036,.136,.108)],[.060,.092,.118,.112,.082],.00092,HAIR)
add_flow_ribbon(HEAD,'HairlineRootHiV78',[(-.070,.188,.046),(-.056,.173,.069),(-.034,.156,.088),(-.006,.142,.101)],[.034,.050,.058,.044],.00052,HAIR_HI)
"""
if old_hair not in s:
    raise SystemExit('v7.7 hairline veil block missing')
s=s.replace(old_hair,new_hair,1)

# Bring ears slightly inward to match the narrowed facial envelope.
s=s.replace(
    "for side in(-1,1):add_sphere(HEAD,f'EarV60_{side}',(side*.126,-.018,-.012),(.009,.021,.008),SKIN,20,12)",
    "for side in(-1,1):add_sphere(HEAD,f'EarV78_{side}',(side*.121,-.018,-.012),(.0085,.0205,.0078),SKIN,20,12)",
    1,
)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V78: mature narrow face, wider almond eyes, sculpted lips, swept hairline root')
