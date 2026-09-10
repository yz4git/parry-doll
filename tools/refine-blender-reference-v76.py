from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V76' in s:
    print('Blender heroine generator already carries REFERENCE_V76')
    raise SystemExit(0)
if '# REFERENCE_V75' not in s:
    raise SystemExit('REFERENCE_V75 generator required before v7.6')

s=s.replace(
    '# REFERENCE_V75: CC0-informed facial plane, absolute profile cage, single iris and flush two-volume lips.',
    '# REFERENCE_V75: CC0-informed facial plane, absolute profile cage, single iris and flush two-volume lips.\n# REFERENCE_V76: covered hairline, slimmer V-face, wider almond gaze and sculpted Cupid lips.',
    1,
)

# Keep the v7.5 absolute profile depth unchanged, but make the frontal silhouette less round.
old_width="width=.132*(1.0-.320*lower+.040*cheek)"
new_width="width=.1285*(1.0-.345*lower+.038*cheek)"
if old_width not in s:
    raise SystemExit('v7.5 face width expression not found')
s=s.replace(old_width,new_width,1)

# Slightly wider, softer almond eye aperture. Keep the embedded-eye depth established in v7.5.
s=s.replace('eye_x=.0475\neye_rx=.0260\neye_ry=.0118', 'eye_x=.0465\neye_rx=.0285\neye_ry=.0124', 1)
s=s.replace(
    "add_almond_lens(HEAD,f'EyeScleraV75_{side}',ex,eye_y,.1032,.0320,.0118,.0042,SCLERA,8,64,side,eye_tilt*.66)",
    "add_almond_lens(HEAD,f'EyeScleraV76_{side}',ex,eye_y,.1034,.0350,.0127,.00425,SCLERA,8,72,side,eye_tilt*.70)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'IrisV75_{side}',(ex,eye_y,.1080),(.0110,.0096,.00145),IRIS_INNER,44,26)",
    "add_sphere(HEAD,f'IrisV76_{side}',(ex,eye_y,.1083),(.0123,.0102,.00140),IRIS_INNER,48,28)",
    1,
)
s=s.replace(
    "add_sphere(HEAD,f'PupilV75_{side}',(ex,eye_y-.0001,.1091),(.00245,.00315,.00100),PUPIL,30,20)",
    "add_sphere(HEAD,f'PupilV76_{side}',(ex,eye_y-.0001,.1094),(.00255,.00325,.00096),PUPIL,30,20)",
    1,
)
s=s.replace('ex-side*.0035,eye_y+.0041,.1097,.00115,.00095','ex-side*.0038,eye_y+.0043,.1100,.00120,.00100',1)

old_lids=""" add_strand(HEAD,f'UpperLashV75_{side}',[(inner,eye_y-eye_tilt+.0010,.1070),(ex,eye_y+.0130,.1082),(outer,eye_y+eye_tilt+.0010,.1071)],.00076,HAIR)
 add_strand(HEAD,f'UpperLidFoldV75_{side}',[(inner+side*.004,eye_y-eye_tilt+.0030,.1058),(ex,eye_y+.0150,.1065),(outer-side*.004,eye_y+eye_tilt+.0030,.1058)],.00018,FACE_DARK)
 add_strand(HEAD,f'LowerLidV75_{side}',[(inner+side*.0040,eye_y-eye_tilt-.0002,.1052),(ex,eye_y-.0090,.1057),(outer-side*.0040,eye_y+eye_tilt-.0002,.1052)],.000085,FACE_DARK)
 add_strand(HEAD,f'BrowV75_{side}',[(ex-side*.025,.064,.1010),(ex,.071,.1020),(ex+side*.029,.061,.1012)],.00058,HAIR)
"""
new_lids=""" add_strand(HEAD,f'UpperLashV76_{side}',[(inner,eye_y-eye_tilt+.0010,.1072),(ex,eye_y+.0138,.1085),(outer,eye_y+eye_tilt+.0010,.1073)],.00088,HAIR)
 add_strand(HEAD,f'UpperLidFoldV76_{side}',[(inner+side*.0042,eye_y-eye_tilt+.0032,.1060),(ex,eye_y+.0160,.1068),(outer-side*.0042,eye_y+eye_tilt+.0032,.1060)],.00021,FACE_DARK)
 add_strand(HEAD,f'LowerLidV76_{side}',[(inner+side*.0042,eye_y-eye_tilt-.0002,.1054),(ex,eye_y-.0095,.1059),(outer-side*.0042,eye_y+eye_tilt-.0002,.1054)],.000075,FACE_DARK)
 add_strand(HEAD,f'BrowV76_{side}',[(ex-side*.026,.064,.1010),(ex,.0715,.1021),(ex+side*.030,.061,.1012)],.00056,HAIR)
"""
if old_lids not in s:
    raise SystemExit('v7.5 eyelid block not found')
s=s.replace(old_lids,new_lids,1)

# Replace flat almond lip stickers with shallow sculpted panels. The nose/chin cage itself is unchanged.
old_mouth="""add_almond_surface(HEAD,'UpperLipTintV75',0,-.0800,.1091,.0215,.0042,.00014,LIP,72,1,0.0)
add_almond_surface(HEAD,'LowerLipTintV75',0,-.0900,.1111,.0222,.0046,.00014,LIP,72,1,0.0)
add_strand(HEAD,'MouthSeamV75',[(-.0205,-.0850,.1100),(0,-.0854,.1104),(.0205,-.0850,.1100)],.000060,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV75_{side}',side*.0056,-.0570,.1157,.00155,.00058,FACE_DARK,16)
"""
new_mouth="""add_panel(HEAD,'UpperLipV76_L',[(-.0230,-.0850,.1100),(-.0115,-.0802,.1113),(0,-.0834,.1120),(0,-.0871,.1123),(-.0100,-.0862,.1119),(-.0215,-.0884,.1107)],.00050,LIP)
add_panel(HEAD,'UpperLipV76_R',[(0,-.0834,.1120),(.0115,-.0802,.1113),(.0230,-.0850,.1100),(.0215,-.0884,.1107),(.0100,-.0862,.1119),(0,-.0871,.1123)],.00050,LIP)
add_panel(HEAD,'LowerLipV76',[(-.0215,-.0884,.1111),(0,-.0876,.1122),(.0215,-.0884,.1111),(.0185,-.0945,.1108),(0,-.0970,.1110),(-.0185,-.0945,.1108)],.00055,LIP)
add_strand(HEAD,'MouthSeamV76',[(-.0210,-.0868,.1110),(-.0100,-.0864,.1118),(0,-.0872,.1124),(.0100,-.0864,.1118),(.0210,-.0868,.1110)],.000052,FACE_DARK)
for side in(-1,1):
 add_ellipse_surface(HEAD,f'NostrilTintV76_{side}',side*.0056,-.0570,.1157,.00145,.00052,FACE_DARK,16)
"""
if old_mouth not in s:
    raise SystemExit('v7.5 mouth block not found')
s=s.replace(old_mouth,new_mouth,1)

# v7.5 moved the forehead forward, exposing a triangular scalp gap between old fringe sheets.
# Add a broad, very thin front hairline underlay behind the existing swept fringe. It stops well above the brows.
hair_anchor="""# Two wide dark planes establish a natural side-swept fringe instead of repeated finger-like locks.
"""
hair_insert="""# v7.6 front hairline underlay follows the advanced forehead and prevents skin wedges between fringe ribbons.
add_flow_ribbon(HEAD,'HairlineUnderlayV76',[(0,.188,.034),(0,.166,.060),(0,.143,.082),(0,.120,.099),(0,.101,.106)],[.118,.205,.232,.216,.176],.00125,HAIR)
add_flow_ribbon(HEAD,'HairlineSoftEdgeV76',[(-.020,.177,.050),(-.008,.153,.075),(.010,.130,.095),(.026,.111,.106)],[.150,.168,.150,.096],.00095,HAIR_HI)

# Two wide dark planes establish a natural side-swept fringe instead of repeated finger-like locks.
"""
if hair_anchor not in s:
    raise SystemExit('v5.9 fringe anchor not found')
s=s.replace(hair_anchor,hair_insert,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V76: covered hairline, slimmer V-face, wider almond gaze and sculpted Cupid lips')
